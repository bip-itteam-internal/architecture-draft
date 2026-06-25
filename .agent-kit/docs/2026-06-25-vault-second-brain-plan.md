# Vault Team Second Brain — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tambah dua area non-domain ke vault `architecture-draft/` — `Runbooks/` (operasional non-kode, di-publish) dan `Workspace/` (capture privat: Inbox + Meetings, di-exclude dari wiki) — beserta rules, templates, SOP, dan index.

**Architecture:** Reuse pola "non-domain area" yang sudah ada (seperti `Logs`/`Reference`). `Runbooks/` ikut aturan vault penuh (grounded, status marker, wikilink 0-broken) dan di-publish. `Workspace/` dikecualikan dari aturan itu dan dari export wiki; capture mentah "naik kelas" jadi dok permanen (domain / `RUN -` / `ADR -`). Stream bisnis/keputusan TANPA folder baru — reuse `Decisions/`.

**Tech Stack:** Markdown (Obsidian vault), git. Verifikasi via PowerShell + Glob (Bash hang di path vault ini — pakai PowerShell + `git -C`). Ini perubahan **dokumentasi**, bukan kode: tiap task = edit → **verifikasi konkret** (folder/prefix/wikilink-resolve) → commit. Tidak ada unit test runner.

Sumber kebenaran desain: `.agent-kit/docs/2026-06-25-vault-second-brain-design.md`.

## Global Constraints

Aturan vault (`architecture-draft/CLAUDE.md`) berlaku untuk **setiap** task:

- **Penamaan**: `Prefix - Nama.md`, flat, tanpa `/` di nama.
- **Grounded-in-code (§1)**: published areas hanya yang nyata; belum ada = TBD. `Workspace/` **dikecualikan**.
- **Wikilink 0-broken (§4)**: semua `[[...]]` di dok **published** harus resolve sebelum commit. `Workspace/` **dikecualikan**. Dok published **tidak boleh** nge-link ke `Workspace/`.
- **Status marker (§5)**: ✅/⚠️/🟡/🔴 untuk dok arsitektur/Runbook. `Workspace/` dikecualikan.
- **Bahasa**: Indonesia; istilah teknis English (endpoint, service, JWT, dll).
- **Git (§9)**: `$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"`. Stage **per-file** (`git -C $repo add -- "<path>"`). **JANGAN `git add -A`.** **JANGAN commit `.obsidian/*`.** **JANGAN sentuh** file in-progress orang lain yang sudah ada saat plan ini ditulis: `Finance System/Finance - Bridging App New Golang.md` dan `.obsidian/graph.json`. Commit format `docs: ...` + footer `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`. Push terpisah (jangan auto-push tanpa diminta).

**Verification helper — cek wikilink resolve (dipakai di beberapa task).** Jalankan di PowerShell, ganti `$file`:

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
$file = "$repo\<path file yang dicek>"
$links = Select-String -Path $file -Pattern '\[\[([^\]\|#]+)' -AllMatches |
  ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value.Trim() } | Sort-Object -Unique
foreach ($l in $links) {
  $hit = Get-ChildItem -Path $repo -Recurse -Filter "$l.md" -File -ErrorAction SilentlyContinue
  if ($hit) { "OK   $l" } else { "MISS $l" }
}
```
Expected: semua baris `OK ...`, tidak ada `MISS`.

---

### Task 1: Daftarkan area Runbooks + Workspace di rulebook (`CLAUDE.md`)

**Files:**
- Modify: `architecture-draft/CLAUDE.md` (§2 area non-domain; §3 prefix)

**Interfaces:**
- Produces: konvensi `Runbooks/` (`RUN -`, published, grounded) & `Workspace/` (`Inbox/` + `Meetings/` `MTG -`, privat, exempt). Task 2–7 mengikuti definisi ini.

- [ ] **Step 1: Tambah dua paragraf area non-domain di §2.** Di `architecture-draft/CLAUDE.md`, sisipkan **setelah** baris yang dimulai `**Area non-domain:** \`API Reference\`` dan **sebelum** baris `> **Dok meta root**`:

```markdown
**Area non-domain:** `Runbooks` (prefix `RUN -`) — **pengetahuan operasional non-kode**: runbook, how-to, onboarding, troubleshooting. **TETAP grounded** (ikut §1/§4/§5: prosedur harus benar-benar jalan, status marker, wikilink 0-broken) dan **tetap di-publish** ke wiki. Flat, tanpa sub-pohon domain.

**Area non-domain:** `Workspace` — **corong capture privat**, **dikecualikan dari publish wiki**. Dua sub-area: `Workspace/Inbox` (daily notes `YYYY-MM-DD.md` + idea capture, nama bebas) & `Workspace/Meetings` (notulen, prefix `MTG -`, mis. `MTG - 2026-06-25 Standup`). **Dikecualikan** dari grounded-in-code (§1), status marker (§5), template (§6), dan gate wikilink 0-broken (§4) — capture boleh nge-link ke catatan yang belum ada. Catatan matang **"naik kelas"** jadi dok domain / `RUN -` / `ADR -`, lalu yang mentah diarsip/dihapus. **Larangan:** dok published TIDAK boleh nge-link ke `Workspace/` (akan broken di wiki). Exclusion publish via ignore-glob `Workspace/**` dan/atau frontmatter `publish: false`.
```

- [ ] **Step 2: Tambah prefix `RUN -` & `MTG -` di §3.** Di daftar prefix §3, sisipkan **setelah** baris `- \`API -\` → **API Reference** ...` dan **sebelum** baris `- Karakter \`/\` tidak boleh ...`:

```markdown
- `RUN -` → **Runbooks** (operasional non-kode; mis. `RUN - Onboarding Developer Baru`)
- `MTG -` → **Workspace/Meetings** (notulen rapat; mis. `MTG - 2026-06-25 Standup`)
```

- [ ] **Step 3: Verifikasi.** Jalankan:

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
Select-String -Path "$repo\CLAUDE.md" -Pattern 'Runbooks|Workspace|RUN -|MTG -' | Select-Object LineNumber, Line
```
Expected: muncul ≥4 baris memuat `Runbooks`, `Workspace`, `RUN -`, `MTG -`.

- [ ] **Step 4: Commit.**

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git -C $repo add -- "CLAUDE.md"
git -C $repo commit -m @'
docs: daftarkan area Runbooks + Workspace di rulebook (second brain)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
'@
```

---

### Task 2: Tiga template baru (Runbook, Meeting Note, Daily Note)

**Files:**
- Create: `architecture-draft/Templates/Template - Runbook.md`
- Create: `architecture-draft/Templates/Template - Meeting Note.md`
- Create: `architecture-draft/Templates/Template - Daily Note.md`

**Interfaces:**
- Consumes: konvensi dari Task 1.
- Produces: skeleton yang dirujuk Task 3 (seed) & Task 4 (SOP). Frontmatter `publish: false` pada template privat = baris pertama file (syarat YAML frontmatter Obsidian).

- [ ] **Step 1: Buat `Templates/Template - Runbook.md`.**

```markdown
%% ============================================================
TEMPLATE — Runbook (operasional non-kode)
Pakai untuk prefix: RUN -   (folder: Runbooks/)
Untuk: prosedur how-to, onboarding, troubleshooting yang BENAR-BENAR jalan.
TETAP grounded (§1) + status marker (§5) + wikilink 0-broken (§4). Di-publish ke wiki.
Cara pakai: copy isi, ganti placeholder, HAPUS blok komentar %% %% ini.
Lihat: IT - SOP Dokumentasi Vault · CLAUDE.md §2 (area non-domain Runbooks)
============================================================ %%

> **Status:** 🟡 Draft  %% jadi ✅ Implemented bila prosedur sudah terverifikasi jalan %%

## Tujuan

%% 1 kalimat: prosedur ini menyelesaikan apa. %%

## Kapan dipakai

%% Trigger/situasi yang menuntut runbook ini dijalankan. %%

## Prasyarat

- %% akses/role/tool/env yang dibutuhkan %%

## Langkah

1. %% langkah konkret; tulis perintah persis bila ada %%

## Verifikasi

%% cara memastikan berhasil (output yang diharapkan). %%

## Bila gagal / Rollback

%% apa yang dilakukan bila langkah gagal; cara mundur dengan aman. %%

## Dokumen Terkait

- %% wikilink ke service/konsep terkait, tanpa backtick %%
```

- [ ] **Step 2: Buat `Templates/Template - Meeting Note.md`** (frontmatter di baris pertama):

```markdown
---
publish: false
---
%% ============================================================
TEMPLATE — Meeting Note (notulen rapat)
Prefix: MTG -   (folder: Workspace/Meetings/)  nama: MTG - YYYY-MM-DD <Topik>
Area PRIVAT — TIDAK di-publish. Dikecualikan dari grounded (§1), status marker (§5),
template arsitektur (§6), gate wikilink 0-broken (§4).
Keputusan/aksi matang "naik kelas" → ADR - / dok domain / RUN -.
Cara pakai: copy, ganti placeholder, HAPUS blok %% %% ini (frontmatter publish:false TETAP).
============================================================ %%

> **Rapat:** {{title}} · **Tanggal:** {{date}} · **Hadir:** %% nama %%

## Agenda

- %% poin %%

## Catatan

%% diskusi, point-in-time %%

## Keputusan

- %% keputusan → kandidat naik kelas ke ADR - %%

## Aksi (Action Items)

- [ ] %% siapa — apa — kapan %%

## Naik kelas?

%% Apa yang dipindah ke dok permanen (ADR-/domain/RUN-) dan ke mana. %%
```

- [ ] **Step 3: Buat `Templates/Template - Daily Note.md`** (frontmatter di baris pertama):

```markdown
---
publish: false
---
%% ============================================================
TEMPLATE — Daily Note / Idea Capture
Folder: Workspace/Inbox/   nama daily note: YYYY-MM-DD.md  (idea: nama bebas)
Area PRIVAT — TIDAK di-publish. Bebas-bentuk, gesekan minimum.
Dikecualikan dari grounded (§1), status marker (§5), template (§6), gate wikilink (§4).
Item matang "naik kelas" → dok domain / RUN - / ADR -.
Cara pakai: copy, ganti placeholder, HAPUS blok %% %% ini (frontmatter publish:false TETAP).
============================================================ %%

# {{date}}

## Tangkap cepat

- %% ide / catatan / link, bebas %%

## Untuk dinaik-kelaskan

- [ ] %% item yang layak jadi dok permanen + tujuan (domain/RUN-/ADR-) %%
```

- [ ] **Step 4: Verifikasi.** Jalankan:

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
Get-ChildItem "$repo\Templates" -Filter "Template - *.md" | Select-Object Name
"--- publish:false harus muncul 2x (Meeting + Daily) ---"
Select-String -Path "$repo\Templates\Template - Meeting Note.md","$repo\Templates\Template - Daily Note.md" -Pattern 'publish: false'
```
Expected: ketiga file baru ada; `publish: false` muncul di Meeting Note & Daily Note (bukan di Runbook).

- [ ] **Step 5: Commit.**

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git -C $repo add -- "Templates/Template - Runbook.md" "Templates/Template - Meeting Note.md" "Templates/Template - Daily Note.md"
git -C $repo commit -m @'
docs: tambah template Runbook + Meeting Note + Daily Note

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
'@
```

---

### Task 3: Buat folder + seed file (Runbooks/, Workspace/Inbox/, Workspace/Meetings/)

**Files:**
- Create: `architecture-draft/Runbooks/RUN - Onboarding Developer Baru.md`
- Create: `architecture-draft/Workspace/Inbox/2026-06-25.md`
- Create: `architecture-draft/Workspace/Meetings/MTG - 2026-06-25 Contoh Notulen.md`

**Interfaces:**
- Consumes: konvensi (Task 1) + template (Task 2).
- Produces: `RUN - Onboarding Developer Baru` (dirujuk Task 5 HOMEPAGE & Task 6 ADR). Folder non-kosong → persist di git tanpa `.gitkeep`.

- [ ] **Step 1: Buat seed Runbook `Runbooks/RUN - Onboarding Developer Baru.md`** (grounded, wikilink ke dok yang sudah ada):

```markdown
> **Status:** 🟡 Draft (seed — perluas dari pengalaman onboarding nyata)

## Tujuan

Membawa developer baru dari nol sampai bisa menjalankan & berkontribusi ke bip-erp.

## Kapan dipakai

Hari pertama developer baru, atau saat setup ulang environment dari awal.

## Prasyarat

- Akses repo (vault + bip-erp + FE). Git, Go, pnpm, Docker terpasang.

## Langkah

1. Clone vault + repo kode sebagai folder bersebelahan (sibling) — lihat [[CLAUDE]] §0 & [[DEVELOPER GUIDE]].
2. Pahami alur request: baca [[HOMEPAGE]] → [[CORE - API Master Gateway]] → [[CORE - SSO Flow]].
3. Jalankan stack lokal sesuai [[DEVELOPER GUIDE]].
4. Untuk bikin service baru: ikuti langkah di [[HOMEPAGE]] (bagian "Dari mana saya mulai").

## Verifikasi

Login lokal berhasil & bisa hit `/health` salah satu service (lihat [[DEVELOPER GUIDE]]).

## Bila gagal / Rollback

Cek [[IT - Helpdesk]] / [[IT - Monitoring System]]; tanya di channel tim.

## Dokumen Terkait

- [[DEVELOPER GUIDE]] · [[HOMEPAGE]] · [[CLAUDE]] · [[CORE - API Master Gateway]] · [[CORE - SSO Flow]]
```

- [ ] **Step 2: Buat seed daily note `Workspace/Inbox/2026-06-25.md`:**

```markdown
---
publish: false
---

# 2026-06-25

## Tangkap cepat

- (contoh) Ini Inbox — tangkap ide/catatan cepat di sini. Daily note pakai nama `YYYY-MM-DD.md`.

## Untuk dinaik-kelaskan

- [ ] (contoh) Item matang → pindah ke dok domain / RUN - / ADR -.
```

- [ ] **Step 3: Buat seed notulen `Workspace/Meetings/MTG - 2026-06-25 Contoh Notulen.md`:**

```markdown
---
publish: false
---

> **Rapat:** Contoh Notulen (seed) · **Tanggal:** 2026-06-25 · **Hadir:** —

## Agenda

- Contoh struktur notulen di `Workspace/Meetings`.

## Catatan

File contoh untuk menunjukkan pola `MTG - YYYY-MM-DD <Topik>`. Ganti/hapus saat pakai nyata.

## Keputusan

- (contoh) Keputusan yang matang dipindah ke `ADR -`.

## Aksi (Action Items)

- [ ] (contoh) Pindahkan keputusan final ke `Decisions/`.

## Naik kelas?

Keputusan → `ADR -`; konteks bisnis → "Latar Belakang" dok domain.
```

- [ ] **Step 4: Verifikasi folder + publish-flag.** Jalankan:

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
Get-ChildItem "$repo\Runbooks","$repo\Workspace\Inbox","$repo\Workspace\Meetings" -File | Select-Object FullName
"--- Workspace seeds harus publish:false ---"
Select-String -Path "$repo\Workspace\Inbox\2026-06-25.md","$repo\Workspace\Meetings\MTG - 2026-06-25 Contoh Notulen.md" -Pattern 'publish: false'
```
Expected: 3 file ada; kedua seed Workspace memuat `publish: false`.

- [ ] **Step 5: Verifikasi wikilink seed Runbook resolve (0 broken).** Jalankan **verification helper** (Global Constraints) dengan:

```powershell
$file = "$repo\Runbooks\RUN - Onboarding Developer Baru.md"
```
Expected: semua `OK` (DEVELOPER GUIDE, HOMEPAGE, CLAUDE, CORE - API Master Gateway, CORE - SSO Flow, IT - Helpdesk, IT - Monitoring System). Bila ada `MISS`, perbaiki nama wikilink agar match basename file nyata sebelum commit.

- [ ] **Step 6: Commit.**

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git -C $repo add -- "Runbooks/RUN - Onboarding Developer Baru.md" "Workspace/Inbox/2026-06-25.md" "Workspace/Meetings/MTG - 2026-06-25 Contoh Notulen.md"
git -C $repo commit -m @'
docs: seed folder Runbooks + Workspace (second brain)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
'@
```

---

### Task 4: Perluas SOP — decision-tree + bentuk dok + alur "naik kelas"

**Files:**
- Modify: `architecture-draft/Tech Development/IT - SOP Dokumentasi Vault.md`

**Interfaces:**
- Consumes: template (Task 2), konvensi (Task 1).
- Produces: rujukan operasional "ini taruh di mana" + prosedur naik kelas.

- [ ] **Step 1: Tambah template baru ke daftar skeleton.** Di baris yang dimulai `- **Skeleton siap-pakai** (folder \`Templates/\`):`, tambahkan di ujung: ` · [[Template - Runbook]] · [[Template - Meeting Note]] · [[Template - Daily Note]]`.

- [ ] **Step 2: Tambah baris di tabel decision-tree §1.** Sisipkan **setelah** baris `| Daftar endpoint per service | API Reference | \`API -\` |` dan **sebelum** baris `| Belum jelas domainnya | ...`:

```markdown
| Runbook / how-to / onboarding / troubleshoot | Runbooks | `RUN -` |
| Notulen rapat | Workspace/Meetings | `MTG -` |
| Daily note / idea capture | Workspace/Inbox | (bebas, `YYYY-MM-DD`) |
```

- [ ] **Step 3: Tambah bentuk dok di tabel §2.** Sisipkan **setelah** baris tabel `| **Log Operasional** | ... |`:

```markdown
| **Runbook** | prosedur operasional non-kode (grounded, di-publish) | [[Template - Runbook]] | Tujuan → Kapan dipakai → Prasyarat → Langkah → Verifikasi → Bila gagal/Rollback → Dokumen Terkait |
| **Capture (privat)** | daily note / notulen — TIDAK di-publish, exempt | [[Template - Daily Note]] · [[Template - Meeting Note]] | bebas / Agenda → Catatan → Keputusan → Aksi → Naik kelas |
```

- [ ] **Step 4: Perluas pengecualian di §3.** Ganti baris yang dimulai `- **Pengecualian**: dok di \`Logs/\` & file di \`Templates/\`` menjadi:

```markdown
- **Pengecualian**: dok di `Logs/` & file di `Templates/` **dikecualikan** dari grounded/status/template (point-in-time record & scaffold). Dok di `Workspace/` (Inbox + Meetings) **dikecualikan** dari grounded/status/template **dan** dari gate wikilink 0-broken (§4) — privat, tidak di-publish. `Runbooks/` **tidak** dikecualikan (grounded penuh + di-publish).
```

- [ ] **Step 5: Tambah section "Naik kelas".** Sisipkan **sebelum** section `## 4. Cara pakai template`:

```markdown
## Naik kelas (capture → dok permanen)

Capture mentah di `Workspace/` sifatnya sementara. Saat matang, **pindahkan isinya** ke rumah permanen lalu arsip/hapus yang mentah:

| Dari (Workspace) | Isi matang | Ke (permanen) |
|---|---|---|
| Inbox / Meetings | keputusan | `Decisions/ADR - ...` |
| Inbox / Meetings | konteks/aturan bisnis | "Latar Belakang" dok domain |
| Inbox / Meetings | prosedur operasional | `Runbooks/RUN - ...` |
| Inbox | fakta arsitektur/kode | dok domain/service terkait |

`Workspace/` harus tetap **ramping**; kalau menggembung → ada yang belum naik kelas. Dok published **tidak boleh** nge-link ke `Workspace/`.
```

- [ ] **Step 6: Verifikasi.** Jalankan:

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
$f = "$repo\Tech Development\IT - SOP Dokumentasi Vault.md"
Select-String -Path $f -Pattern 'RUN -|MTG -|Naik kelas|Workspace' | Select-Object LineNumber
"--- wikilink resolve ---"
```
Lalu jalankan **verification helper** dengan `$file = $f`. Expected: section/baris baru muncul; semua wikilink (termasuk `Template - Runbook/Meeting Note/Daily Note` dari Task 2) `OK`.

- [ ] **Step 7: Commit.**

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git -C $repo add -- "Tech Development/IT - SOP Dokumentasi Vault.md"
git -C $repo commit -m @'
docs: SOP — runbook/capture + alur naik kelas (second brain)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
'@
```

---

### Task 5: Tambah index Runbooks ke HOMEPAGE

**Files:**
- Modify: `architecture-draft/HOMEPAGE.md`

**Interfaces:**
- Consumes: `RUN - Onboarding Developer Baru` (Task 3) — wikilink wajib resolve.
- Produces: jalur navigasi ke Runbooks. `Workspace/` sengaja TIDAK ditaut (privat).

- [ ] **Step 1: Tambah baris index Runbooks.** Di `HOMEPAGE.md`, sisipkan **setelah** baris `**Tata Kelola** → [[IT - SOP Dokumentasi Vault]] ...`:

```markdown
**Runbooks** → [[RUN - Onboarding Developer Baru]] (operasional non-kode: onboarding · how-to · troubleshooting — di-publish)
```

- [ ] **Step 2: Verifikasi.** Jalankan:

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
Select-String -Path "$repo\HOMEPAGE.md" -Pattern 'Runbooks|RUN - Onboarding'
"--- pastikan TIDAK ada link ke Workspace ---"
Select-String -Path "$repo\HOMEPAGE.md" -Pattern '\[\[Workspace|Workspace/'
```
Lalu jalankan **verification helper** dengan `$file = "$repo\HOMEPAGE.md"`. Expected: baris Runbooks ada; **tidak ada** match Workspace; semua wikilink `OK` (termasuk `RUN - Onboarding Developer Baru`).

- [ ] **Step 3: Commit.**

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git -C $repo add -- "HOMEPAGE.md"
git -C $repo commit -m @'
docs: HOMEPAGE — tambah index Runbooks

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
'@
```

---

### Task 6: ADR-0004 — catat keputusan (dogfooding) + link dari HOMEPAGE

**Files:**
- Create: `architecture-draft/Decisions/ADR - 0004 Vault sebagai Team Knowledge Base.md`
- Modify: `architecture-draft/HOMEPAGE.md` (baris "Roadmap & Keputusan")

**Interfaces:**
- Consumes: `RUN - Onboarding Developer Baru` (Task 3), `IT - SOP Dokumentasi Vault` (ada).

- [ ] **Step 1: Buat `Decisions/ADR - 0004 Vault sebagai Team Knowledge Base.md`** (format mengikuti ADR-0003):

```markdown
## ADR 0004 — Vault sebagai Team Second Brain (Runbooks + Workspace)

- **Status**: ✅ Accepted
- **Tanggal**: 2026-06-25
- **Konteks dok**: [[CLAUDE]] · [[IT - SOP Dokumentasi Vault]] · [[HOMEPAGE]]

## Context

Vault `architecture-draft/` sudah matang sebagai KB arsitektur grounded-in-code, tapi belum punya rumah untuk pengetahuan operasional non-kode (runbook/onboarding/troubleshoot) maupun corong capture (daily note/notulen). Detail: design `.agent-kit/docs/2026-06-25-vault-second-brain-design.md`.

## Decision

Tambah dua area non-domain:
- **`Runbooks/`** (`RUN -`) — operasional non-kode, **tetap grounded + di-publish** ke wiki.
- **`Workspace/`** (`Inbox/` + `Meetings/` `MTG -`) — corong capture **privat, di-exclude dari publish**, dikecualikan dari grounded/status/template/gate-wikilink. Capture "naik kelas" → dok domain / `RUN -` / `ADR -`.

Stream bisnis/keputusan **tanpa folder baru** — reuse `Decisions/` (ADR) + "Latar Belakang" dok domain. Repo privat → `Workspace/` tetap di git, hanya di-exclude dari export wiki.

## Consequences

- ➕ Pengetahuan operasional & capture punya rumah; alur "naik kelas" jelas.
- ➕ Satu graph/search; pemisahan publik/privat lewat satu garis (`Workspace/**`).
- ➖ Butuh disiplin agar `Workspace/` tetap ramping (bukan tempat sampah).
- ⚠️ Mekanisme exclusion publish persis tergantung tool export (TBD-1 — lihat design doc).
- 🔗 Aturan dikodifikasi di [[CLAUDE]] §2/§3 + [[IT - SOP Dokumentasi Vault]].

## Dokumen Terkait

- [[CLAUDE]] · [[IT - SOP Dokumentasi Vault]] · [[HOMEPAGE]] · [[RUN - Onboarding Developer Baru]]
```

- [ ] **Step 2: Tautkan ADR-0004 dari HOMEPAGE.** Di `HOMEPAGE.md`, pada baris `**Roadmap & Keputusan** → ... [[ADR - 0003 SSO-only Gateway]]`, tambahkan di ujung: ` · [[ADR - 0004 Vault sebagai Team Knowledge Base]]`.

- [ ] **Step 3: Verifikasi.** Jalankan **verification helper** dua kali, dengan:

```powershell
$file = "$repo\Decisions\ADR - 0004 Vault sebagai Team Knowledge Base.md"
# lalu:
$file = "$repo\HOMEPAGE.md"
```
Expected: keduanya semua `OK`. Khusus HOMEPAGE, pastikan `ADR - 0004 ...` kini resolve.

- [ ] **Step 4: Commit.**

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git -C $repo add -- "Decisions/ADR - 0004 Vault sebagai Team Knowledge Base.md" "HOMEPAGE.md"
git -C $repo commit -m @'
docs: ADR-0004 vault sebagai team second brain

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
'@
```

---

### Task 7: Verifikasi akhir (gate 0-broken published) + handoff exclusion publish

**Files:** (tidak ada perubahan file; gate + handoff)

- [ ] **Step 1: Cek tidak ada dok published yang nge-link ke `Workspace/`.** Jalankan:

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
Get-ChildItem $repo -Recurse -Filter *.md -File |
  Where-Object { $_.FullName -notmatch '\\Workspace\\' -and $_.FullName -notmatch '\\\.' } |
  Select-String -Pattern '\[\[Workspace' |
  Select-Object Path, LineNumber, Line
```
Expected: **tidak ada output** (tak ada dok published yang nge-link ke Workspace).

- [ ] **Step 2: Cek wikilink 0-broken pada semua dok yang disentuh.** Jalankan **verification helper** untuk: `CLAUDE.md`, `HOMEPAGE.md`, `Tech Development\IT - SOP Dokumentasi Vault.md`, `Runbooks\RUN - Onboarding Developer Baru.md`, `Decisions\ADR - 0004 Vault sebagai Team Knowledge Base.md`. Expected: semua `OK`, 0 `MISS`.

- [ ] **Step 3: Konfirmasi git bersih & tak menyentuh file orang lain.** Jalankan:

```powershell
$repo = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git -C $repo status --porcelain
git -C $repo log --oneline -7
```
Expected: `Finance System/Finance - Bridging App New Golang.md` & `.obsidian/graph.json` **masih** sebagai perubahan belum-di-commit (tidak tersapu); 6 commit `docs:` baru dari Task 1–6.

- [ ] **Step 4: Handoff TBD-1 (manual, di luar kuasa plan ini).** Mekanisme exclusion publish bergantung tool export wiki (plugin export tidak aktif di `.obsidian/community-plugins.json`). **Sampaikan ke pemilik proses publish**: saat export berikutnya, exclude path `Workspace/**` (ignore-glob) — frontmatter `publish: false` sudah dipasang di seed Workspace sebagai sabuk kedua. Catat hasilnya di design doc (resolve TBD-1). **Tidak ada commit untuk step ini.**

---

## Manual follow-up (di luar plan)

- **TBD-1**: Konfigurasi exclude `Workspace/**` di tool export wiki saat publish berikutnya (lihat Task 7 Step 4). Sampai selesai, capture privat aman secara git (repo privat) tapi belum ada jaminan otomatis di pipeline export.
- **Push**: plan ini hanya commit lokal (§9: pull sebelum push). Push dilakukan terpisah sesuai mekanisme tim.

## Self-Review (penulis plan)

- **Spec coverage**: Runbooks (T1/T3/T5) · Workspace Inbox+Meetings (T1/T3) · exemptions (T1/T4) · templates (T2) · promotion flow (T4) · HOMEPAGE index (T5) · bisnis=reuse Decisions (T6 ADR + T4 promotion) · exclusion publish (T1 note + T2/T3 publish:false + T7 handoff TBD-1). Semua item design §"Daftar perubahan" tertutup.
- **Placeholder scan**: tidak ada TODO/TBD tersisa di langkah implementasi; satu-satunya TBD (TBD-1) sengaja = dependensi eksternal (tool export), ditangani sebagai handoff Task 7, bukan placeholder.
- **Type/nama consistency**: prefix `RUN -`/`MTG -`, folder `Runbooks/`/`Workspace/Inbox/`/`Workspace/Meetings/`, dan basename `RUN - Onboarding Developer Baru` konsisten di T1→T7. Wikilink seed hanya menunjuk file yang sudah ada (diverifikasi T3 Step 5).
