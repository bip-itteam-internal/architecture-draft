# Recruitment Pipeline Redesign — Implementation Plan

- **Status**: 🟡 Direncanakan (Plan) — rencana implementasi task-by-task; belum ada kode. Spec: [[HRIS - Recruitment Pipeline Redesign]].

> **For agentic workers:** REQUIRED SUB-SKILL: gunakan superpowers:subagent-driven-development (rekomendasi) atau superpowers:executing-plans untuk eksekusi task-by-task. Step pakai checkbox `- [ ]`.
> **Spec:** [[HRIS - Recruitment Pipeline Redesign]]. **Sisi implementasi:** [[Microservices - Recruitment Service]] (BE) + [[APP - Web ERP]] (FE).

**Goal:** Sederhanakan pipeline kandidat jadi satu field `status` 6-nilai, buang tahap Technical Test/Background Check/Psikotes/Screening-record, dan jadikan jenis interview sebagai Interview Rounds (katalog global + override per-lowongan).

**Architecture:** BE Go/Fiber/Mongo (`services/recruitment`, package `main`, flat-file). Fungsi pipeline MURNI di `pipeline.go` (TDD). FE Next.js (erp-frontend, i18n id+en). Perubahan bertahap per-slice; **deploy BE sebelum FE** (manual, CI dev disabled).

**Tech Stack:** Go 1.x + Fiber v2 + MongoDB driver; Next.js + react-hook-form + zod + react-i18next + vitest.

## Global Constraints

- Go: build/test/vet dari `services/recruitment` (go.mod per-service). Test pakai `go test ./...`.
- FE: **pnpm** (bukan npm/yarn). Finalize pakai **full `pnpm lint`** + `pnpm exec tsc --noEmit`. Test: `pnpm exec vitest run`.
- i18n: SEMUA teks user-facing baru lewat `t("...")` + key di **dua** file `src/i18n/locales/{id,en}.ts`. Default Indonesia; istilah teknis English biarkan English.
- Git: branch per-service dari `main`; **tanpa** trailer `Co-Authored-By`. bip-erp **commit = auto-push (published)**; erp-frontend push manual.
- Loading FE pakai **ShimmerBox/Skeleton**, bukan spinner. Reuse komponen shared (mis. `InlineSelectBadge`, `StarRating`), jangan bikin tiruan.
- **Deploy BE sebelum FE** untuk perubahan kontrak.

---

## Decomposition (6 slice = 6 plan/PR)

| Slice | Repo | Deliverable | Branch |
|---|---|---|---|
| 1 | bip-erp | Status 6-nilai + migrasi + transisi manual | `feat/recruitment-status-simplify` |
| 2 | bip-erp | Hapus technical-test/background-check/psikotes/screening_result | `feat/recruitment-drop-stages` |
| 3 | bip-erp | Interview Rounds global+override + `round_id` + flag feedback-link | `feat/recruitment-interview-rounds` |
| 4 | erp-frontend | Status field + inline badge + funnel + public tracking | `feat/recruitment-status-fe` |
| 5 | erp-frontend | Hapus stage-record detail + timeline (sisakan interview) | `feat/recruitment-drop-stages-fe` |
| 6 | erp-frontend | Menu Manage Interview Rounds (System Setup) + form jadwal pakai round | `feat/recruitment-rounds-fe` |

Urutan wajib: **1→2→3 (BE) lalu deploy, baru 4→5→6 (FE)**. Slice 3 harus selesai sebelum 6 (FE rounds butuh kontrak BE).

Dokumen ini merinci **Slice 1** lengkap (TDD, kode nyata terverifikasi). Slice 2–6 dirinci per-file di bawah; kode edit detailnya dibuat saat eksekusi dengan **membaca tiap file** (banyak file hanya me-*rename* konstanta → dipandu `go build`/`tsc`, bukan ditebak di sini).

---

## SLICE 1 — BE: Status 6-nilai + migrasi + transisi (`feat/recruitment-status-simplify`)

**Sumber terverifikasi:** [pipeline.go](../../bip-erp/services/recruitment/pipeline.go), [pipeline_test.go](../../bip-erp/services/recruitment/pipeline_test.go), [models_candidate.go](../../bip-erp/services/recruitment/models_candidate.go). Referensi enum lama tersebar di **21 file** (grep `Prog[A-Z]`/`St[A-Z]`).

### Task 1.1 — Enum status baru + fungsi murni (pipeline.go)

**Files:**
- Modify: `bip-erp/services/recruitment/pipeline.go`
- Test: `bip-erp/services/recruitment/pipeline_test.go`

**Interfaces (Produces):**
- `type Status string` dgn const: `StNew="New"`, `StScreening="Screening"`, `StInterview="Interview"`, `StOffer="Offer"`, `StHired="Hired"`, `StRejected="Rejected"`.
- `func IsValidStatus(s Status) bool`
- `func IsTerminalStatus(s Status) bool` → true untuk `StHired`, `StRejected`.
- `func NormalizeStatus(s string) (Status, bool)` (case-insensitive, trim).
- `func MigrateStatus(oldProgress, oldStatus string) Status` — peta data lama → status baru.
- **Hapus:** `type Progress`, semua `Prog*`, `progressOrder`, `progressIndex`, `IsValidProgress`, `CanAdvance`, `NormalizeProgress`, dan `Status` lama (`StApplied`..`StBuffer`).

- [ ] **Step 1: Tulis test gagal** — ganti isi `pipeline_test.go`:

```go
package main

import "testing"

func TestIsValidStatus(t *testing.T) {
	for _, s := range []Status{StNew, StScreening, StInterview, StOffer, StHired, StRejected} {
		if !IsValidStatus(s) {
			t.Errorf("%q harus valid", s)
		}
	}
	if IsValidStatus(Status("Galau")) {
		t.Fatal("status tak dikenal harus invalid")
	}
}

func TestIsTerminalStatus(t *testing.T) {
	for _, s := range []Status{StHired, StRejected} {
		if !IsTerminalStatus(s) {
			t.Errorf("%q harus terminal", s)
		}
	}
	for _, s := range []Status{StNew, StScreening, StInterview, StOffer} {
		if IsTerminalStatus(s) {
			t.Errorf("%q tidak boleh terminal", s)
		}
	}
}

func TestNormalizeStatus(t *testing.T) {
	if s, ok := NormalizeStatus("  interview "); !ok || s != StInterview {
		t.Errorf("normalize gagal: %q %v", s, ok)
	}
	if _, ok := NormalizeStatus("unknown"); ok {
		t.Error("string tak dikenal harus gagal")
	}
}

func TestMigrateStatus(t *testing.T) {
	cases := []struct{ prog, stat string; want Status }{
		{"CV Screening", "Applied", StScreening},
		{"", "Applied", StNew},
		{"HR Interview", "In Progress", StInterview},
		{"Technical Test", "Scheduled", StInterview},
		{"Background Check", "In Progress", StInterview},
		{"Psikotes", "In Progress", StInterview},
		{"Offering", "In Progress", StOffer},
		{"Hired", "Hired", StHired},
		{"Onboarding", "Hired", StHired},
		{"CV Screening", "Rejected", StRejected},
		{"HR Interview", "Withdrawn", StRejected},
	}
	for _, c := range cases {
		if got := MigrateStatus(c.prog, c.stat); got != c.want {
			t.Errorf("MigrateStatus(%q,%q)=%q want %q", c.prog, c.stat, got, c.want)
		}
	}
}
```

- [ ] **Step 2: Jalankan, pastikan gagal**
Run: `go -C services/recruitment test ./... -run 'Status' -v`
Expected: FAIL (undefined: StNew, IsValidStatus signature lama, MigrateStatus undefined).

- [ ] **Step 3: Tulis implementasi** — ganti isi `pipeline.go`:

```go
package main

import "strings"

// Status = keadaan kandidat dalam pipeline (satu field, gantikan Progress+Status lama).
type Status string

const (
	StNew       Status = "New"
	StScreening Status = "Screening"
	StInterview Status = "Interview"
	StOffer     Status = "Offer"
	StHired     Status = "Hired"
	StRejected  Status = "Rejected"
)

var allStatuses = []Status{StNew, StScreening, StInterview, StOffer, StHired, StRejected}

func IsValidStatus(s Status) bool {
	for _, v := range allStatuses {
		if v == s {
			return true
		}
	}
	return false
}

// IsTerminalStatus: kandidat keluar dari pipeline aktif.
func IsTerminalStatus(s Status) bool { return s == StHired || s == StRejected }

func NormalizeStatus(s string) (Status, bool) {
	t := strings.TrimSpace(s)
	for _, v := range allStatuses {
		if strings.EqualFold(string(v), t) {
			return v, true
		}
	}
	return "", false
}

// MigrateStatus memetakan data lama (progress+status) ke status baru (dipakai sekali saat migrasi).
func MigrateStatus(oldProgress, oldStatus string) Status {
	switch strings.TrimSpace(oldStatus) {
	case "Rejected", "Withdrawn":
		return StRejected
	case "Hired":
		return StHired
	}
	switch strings.TrimSpace(oldProgress) {
	case "", "Applied":
		return StNew
	case "CV Screening":
		return StScreening
	case "Offering":
		return StOffer
	case "Hired", "Onboarding":
		return StHired
	default: // HR/User/Final Interview, Technical Test, Background Check, Psikotes
		return StInterview
	}
}
```

- [ ] **Step 4: Jalankan test, pastikan lulus**
Run: `go -C services/recruitment test ./... -run 'Status' -v`
Expected: PASS (4 test).

- [ ] **Step 5: Commit**
```bash
git -c core.fsmonitor=false add services/recruitment/pipeline.go services/recruitment/pipeline_test.go
git -c core.fsmonitor=false commit -m "refactor(recruitment): status 6-nilai + MigrateStatus (buang Progress)"
```

### Task 1.2 — Model candidate satu-field + perbaiki semua referensi (kompilasi hijau)

**Files:**
- Modify: `bip-erp/services/recruitment/models_candidate.go` (buang field `Progress`; `Status` pakai tipe baru; default create).
- Modify (referensi enum lama → hapus/ganti): `candidate_handlers.go`, `offer_handlers.go`, `stage_handlers.go`, `tracking.go`, `public_handlers.go`, `interview_ext_handlers.go`, `onboarding.go`, `requisition_handlers.go`, `audit.go`, dan file lain yang muncul di grep `Prog[A-Z]`/`St[A-Z]` (21 file). Test lama yang menyebut enum lama (`candidate_test.go`, `tracking_test.go`, `offer_test.go`, dst) ikut disesuaikan.

**Interfaces (Consumes):** `Status`, `StNew`, `IsValidStatus`, `IsTerminalStatus` dari Task 1.1.

- [ ] **Step 1** — `models_candidate.go`: hapus baris `Progress Progress ...`; ubah `Status Status ...` tetap (tipe baru otomatis). Tempat create kandidat set `Status: StNew` (cari di `candidate_handlers.go` `createCandidate`/`applyPublic` yang set `ProgCVScreening`/`StApplied` → jadi `StNew`).
- [ ] **Step 2** — Update semua referensi: buka tiap file dari grep, ganti pemakaian `Prog*`/`CanAdvance`/`NormalizeProgress` dan `St*` lama. Pola umum: aksi yang dulu set progress (`offer` → `ProgOffering`, hire → `ProgHired`) kini set **Status** (`StOffer`, `StHired`); endpoint `advance`/`reject` (lihat Task 1.3) jadi set-status manual. Endpoint filter `?status=` & `?progress=` → satu param `status`.
- [ ] **Step 3** — `go -C services/recruitment build ./...` → perbaiki sampai **hijau** (compiler memandu; jangan tebak, baca tiap error).
- [ ] **Step 4** — `go -C services/recruitment vet ./...` bersih; `go -C services/recruitment test ./...` → sesuaikan test lama yang gagal (buang assertion tahap detail).
- [ ] **Step 5: Commit** `refactor(recruitment): candidate satu-field status; perbaiki referensi enum`.

### Task 1.3 — Endpoint ubah status (manual, bebas) + migrasi startup

**Files:**
- Modify: `candidate_handlers.go` (ganti `advanceCandidate`/`rejectCandidate` → satu `setCandidateStatus` manual; validasi `IsValidStatus`; audit).
- Modify: `routes.go` (route `PUT /candidates/:id/status`; buang route `advance`/`reject` bila ada; cek [routes.go](../../bip-erp/services/recruitment/routes.go)).
- Modify: `main.go` atau `db.go` — panggil migrasi one-off idempotent saat startup (loop candidate: bila field `progress` masih ada / status lama → set `status = MigrateStatus(...)`, unset `progress`).
- Modify: FE hook nanti (Slice 4) — kontrak `PUT /candidates/:id/status {status}`.

- [ ] **Step 1: Test handler** (`candidate_test.go`): set status valid → 200 & tersimpan; status invalid → 400; body kosong → 400. (Ikuti pola test handler existing di file itu.)
- [ ] **Step 2:** jalankan → gagal.
- [ ] **Step 3:** implement `setCandidateStatus` (baca body `{status}`, `NormalizeStatus`, `IsValidStatus`, update `status`+`updated_at`, audit) + daftarkan route + fungsi migrasi startup (idempotent: skip bila semua sudah 6-nilai).
- [ ] **Step 4:** `go test ./...` PASS; `go build`/`vet` hijau.
- [ ] **Step 5: Commit** `feat(recruitment): PUT /candidates/:id/status manual + migrasi status startup`.

**Verifikasi Slice 1:** `go -C services/recruitment build/vet/test ./...` hijau; migrasi jalan idempotent (jalankan 2×, hasil sama). Deploy manual recruitment-service, cek data dev termigrasi.

---

## SLICE 2 — BE: Hapus tahap detail (`feat/recruitment-drop-stages`)

**Files (hapus):** `models_stages.go` (bagian `TechnicalTestResult`, `BackgroundCheck`, `Psychotest`, `ScreeningResult`; **sisakan** `Interview`, `InterviewPanelist`), `stage_handlers.go` (handler screening/technical-test/background-check/psikotes; sisakan `recordInterview` & interview), koleksi & route terkait di `routes.go`, `models_stages.go` psychotest_result.
**Sisakan:** semua interview + feedback (`interview_ext_handlers.go`, `models_interview_ext.go`).
**Tasks:** (a) hapus route+handler stage detail → `go build` hijau; (b) hapus model+koleksi; (c) sesuaikan `stage_test.go` (buang case stage detail); (d) commit. Data Mongo lama dibiarkan (tak dipakai).

## SLICE 3 — BE: Interview Rounds global + override + round_id (`feat/recruitment-interview-rounds`)

**Files (baru/ubah):** `models_master.go`/`models_interview_ext.go` (entity `InterviewRound` global: `name, sequence, is_active, sends_feedback_link`), handler CRUD `interview_round_handlers.go` (`/masters/interview-rounds`), per-lowongan override di `models_posting.go`+`posting_handlers.go` (daftar round dipilih + urutan), `models_stages.go` `Interview` + `RoundID` (ganti `Stage` HR/User/Final), `interview_notify.go` `interviewUsesLink` → baca flag round `sends_feedback_link` (bukan hardcoded User/Final).
**Tasks TDD:** (a) model+validasi round (pure test); (b) CRUD master; (c) posting override; (d) `Interview.RoundID` + migrasi sesi lama (stage→round bila ada, else null); (e) `interviewUsesLink(round)` test; (f) commit.
**Catatan:** simpan kompatibilitas — sesi lama tanpa round_id tetap terbaca.

## SLICE 4 — FE: Status field + badge + funnel + tracking (`feat/recruitment-status-fe`)

**Files:** `src/features/hris/recruitment/candidates/types.ts` (`CandidateStatus` = 6; buang `CandidateProgress` + `status` lama), `hooks/use-candidates.ts` (mutation `setStatus` → `PUT /candidates/:id/status`; filter `?status=`), inline badge (`InlineSelectBadge` reuse) 6-nilai, `dashboard/components/hiring-funnel.tsx` → 6 tahap, public tracking stepper (`app/.../track` atau portal) → 6 label curated, i18n id+en (label 6 status + funnel).
**Tasks:** update types → `tsc` hijau; badge 6-nilai + warna; funnel 6; tracking; test badge/funnel yang terdampak; full `pnpm lint`.

## SLICE 5 — FE: Hapus stage-record detail + timeline (`feat/recruitment-drop-stages-fe`)

**Files:** `stages/components/stage-record-dialog.tsx` (buang technical_test/psychotest/background_check/screening), `stages-timeline.tsx` + `lib.ts` (STAGE_KINDS → sisakan interview), `types.ts` (buang TechnicalTestResult/BackgroundCheck/Psychotest/ScreeningResult + DTO), hapus test terkait; candidate-detail timeline = interview saja.
**Tasks:** hapus komponen/kind → `tsc` hijau; sesuaikan `lib.test.ts`/`stages-timeline.test.tsx`; full lint.

## SLICE 6 — FE: Menu Manage Interview Rounds + form jadwal pakai round (`feat/recruitment-rounds-fe`)

**Files:** menu di `Recruitment → System Setup` (tab/section baru "Interview Rounds") — reuse pola master lain (job-types/sources/interview-types), hook `use-interview-rounds.ts` (CRUD `/masters/interview-rounds`), per-lowongan override di form Posting, `interview-form.tsx` ganti `Sub-tahap` (HR/User/Final) → picker **Round** (dari master/override lowongan), i18n id+en.
**Tasks:** master CRUD UI; posting override; interview-form pakai round; sesuaikan test dialog; full lint.

---

## Self-Review (plan vs spec)

- ✅ Status 6-nilai + migrasi → Slice 1. ✅ Transisi manual → Task 1.3. ✅ Hapus tahap detail → Slice 2/5. ✅ Interview Rounds global+override+round_id+flag → Slice 3/6. ✅ Screening=status → Slice 1/2 (buang screening_result). ✅ Onboarding terpisah → tak disentuh. ✅ Dampak funnel/badge/tracking/timeline → Slice 4/5. ✅ Menu System Setup → Slice 6.
- Catatan konsistensi tipe: nama `Status`/`St*`, `MigrateStatus`, `IsValidStatus`, `IsTerminalStatus` konsisten Slice 1↔; FE `CandidateStatus` 6-nilai konsisten Slice 4↔6; `RoundID`/`sends_feedback_link` konsisten Slice 3↔6.
- Slice 1 detail penuh & grounded; Slice 2–6 task per-file (kode edit dibuat saat eksekusi dgn membaca file — mayoritas rename dipandu compiler/tsc, bukan tebakan).
