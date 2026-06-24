> **Status:** 🟡 Benchmark / Konsep — research dari ERPGo SaaS, **belum** keputusan Bharata. Sumber: User Manual ERPGo (demo login-gated). Hub: [[ERPGo - Overview & Gap Matrix]].

## Apa yang ERPGo lakukan

Modul **Form Builder** = pembuat form dinamis tanpa coding:
- **Create Form** — rancang form (judul, deskripsi).
- **Add Form Fields** — tambah field (text, select, checkbox, date, file, dll) secara drag/konfigurasi.
- **Manage & Share Forms** — bagikan via link publik/internal.
- **View Form Responses** — kumpulkan & lihat jawaban.
- **Convert Form into Module** — jadikan submission sebagai record modul (mis. leads/kandidat).

## Yang sudah ada di Bharata ERP

- 🔴 Tidak ada form-builder generik. Form yang ada **hardcoded** per kasus: [[HRIS - Employee Request & Approval]], [[HRIS - Leave Request]], [[HRIS - Overtime]], [[HRIS - Attendance Correction]], Form Permintaan Karyawan ([[HRIS - Recruitment]]), guestbook ([[GA - Guestbook System (Complete)]]).
- [[GA - Checklist Management]] mendekati (checklist konfigurabel) tapi bukan form umum.

## Gap / Peluang

- **Fit sangat tinggi.** Bharata banyak memakai "form request" yang masing-masing dibangun manual. Form Builder bisa jadi **fondasi reusable**: form baru tanpa rilis kode.
- Cocok untuk survei internal, pendaftaran event ([[HRIS - Career & Promotion]]/announcement), intake kandidat, intake leads ([[Sales - CRM management tool]]).

## Rekomendasi

- **Adopsi — prioritas tinggi sebagai enabler**, namun lingkup awal **kecil & jelas** (jangan menggantikan form approval bisnis yang sudah matang).
- **Penempatan usulan** (bila jadi): dok konsep `IT - Form Builder` di domain Tech Development (sifatnya tooling platform), bukan domain bisnis.
- **MVP minimal**: definisi form (skema field JSON) + render + simpan response + export. "Convert-to-module" = fase lanjut.

## Risiko & catatan jaga sistem berjalan

- **Jangan** memaksa migrasi form approval yang sudah jalan (leave/overtime/correction) ke form-builder generik — itu punya logika workflow/SSO khusus. Form Builder untuk **kasus baru/ad-hoc** dulu.
- Submission file → [[Microservices - File Service]]; auth tetap via [[CORE - SSO Flow]].

## Rencana Implementasi (disetujui — eksekusi DITUNDA)

> Hasil `/plan` 2026-06-24. Keputusan dikunci; eksekusi `/implement` ditunda ("nanti saja"). Saat dilanjutkan, langsung TDD per langkah di bawah.

**Keputusan terkunci:**
- **Topologi:** microservice baru `form-builder` + Mongo terpisah (`form_builder_db`) — pola `services/.template` + `task-management`; selaras database-per-service ([[DB - Overview and Notes]]). Nol dampak ke service berjalan.
- **RBAC MVP:** kelola/bangun form = `system_roles["it"]` (supervisor/admin); isi & submit = semua karyawan terautentikasi. Form-fill publik = fase lanjut (tanpa ubah employee-service).
- **MVP scope:** field text/textarea/number/select/checkbox/radio/date → render → simpan response → export CSV. **File field & FE (builder UI/renderer di erp-frontend) = fase lanjut.**

**Perubahan file (path eksak):**
- `shared-library/common/env.go` — tambah `FormBuilderModuleURL` + map `"FORM_BUILDER_MODULE_URL"`.
- `api-gateway/main.go` — tambah `"form-builder"` ke `InternalURL` (proxy `/api/form-builder/*` otomatis).
- `services/form-builder/` (baru): `main.go`, `go.mod`, `Dockerfile`, `identity.go`, `rbac.go` (baca key `it`), `db.go` (`forms`, `form_responses`), `models_form.go`, `models_response.go`, `validate.go`, `form_handlers.go`, `response_handlers.go`, `export.go`, `routes.go`.
- `docker-compose.yml` — service `form-builder-service` + `form-builder-mongo-db` + volume + env gateway.
- `.env` / `.env.example` — `FORM_BUILDER_SERVICE_PORT`, `MONGO_FORM_BUILDER_DB`.

**Urutan TDD:**
1. `validate_test.go` → `validate.go` (key unik, required, nilai ∈ options, tipe cocok).
2. `export_test.go` → `export.go` (CSV: header=field keys, escaping).
3. `rbac_test.go` (copy, gate `it`).
4. Rangkai handlers + routes + db.
5. Wiring gateway + compose → smoke end-to-end.

**Saat `/sync-docs`:** buat dok `Microservices - Form Builder Service` (§7) + naikkan status dok ini ke ⚠️/✅.

## Dokumen Terkait

- [[ERPGo - Overview & Gap Matrix]]
- [[HRIS - Employee Request & Approval]] · [[GA - Checklist Management]] · [[GA - Guestbook System (Complete)]]
- [[Microservices - File Service]] · [[CORE - SSO Flow]] · [[DB - Overview and Notes]] · [[CORE - API Master Gateway]]
