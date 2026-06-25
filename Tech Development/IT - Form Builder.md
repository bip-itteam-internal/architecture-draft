## Deskripsi

*Konsep **Form Builder** — pembuat form dinamis tanpa coding untuk kasus internal baru/ad-hoc. Bharata banyak memakai "form request" yang kini di-hardcode per kasus; Form Builder jadi fondasi reusable (buat form baru tanpa rilis kode). Rencana `/plan` sudah disusun & disetujui; **eksekusi ditunda**.*

- **Status**: 🟡 Konsep / Direncanakan (rencana terkunci, belum di kode)
- **Penempatan**: tooling platform (Tech Development)

## Latar Belakang

- Form yang ada hardcoded per kasus: [[HRIS - Employee Request & Approval]], [[HRIS - Leave Request]], [[HRIS - Overtime]], [[HRIS - Attendance Correction]], Form Permintaan Karyawan ([[HRIS - Recruitment]]), guestbook ([[GA - Guestbook System (Complete)]]). [[GA - Checklist Management]] mendekati tapi bukan form umum.
- Cocok untuk survei internal, intake kandidat, intake leads, pendaftaran event — **tanpa** mengganggu form approval bisnis yang sudah matang.

## Rencana Implementasi (disetujui — eksekusi DITUNDA)

> Keputusan terkunci. Saat dilanjutkan: TDD per langkah. **Git**: di `bip-erp`, branch dari `main` → `feat/form-builder` (konvensi `feat/<nama>`).

**Keputusan terkunci:**
- **Topologi**: microservice baru `form-builder` + Mongo terpisah (`form_builder_db`) — pola `services/.template` + `task-management`; selaras database-per-service ([[DB - Overview and Notes]]). Nol dampak ke service berjalan.
- **RBAC MVP**: kelola/bangun form = `system_roles["it"]` (supervisor/admin); isi & submit = semua karyawan terautentikasi. Form-fill publik = fase lanjut (tanpa ubah employee-service).
- **MVP scope**: field text/textarea/number/select/checkbox/radio/date → render → simpan response → export CSV. **File field & FE (builder UI/renderer di erp-frontend) = fase lanjut.**

**Perubahan file (path eksak):**
- `shared-library/common/env.go` — tambah `FormBuilderModuleURL` + map `"FORM_BUILDER_MODULE_URL"`.
- `api-gateway/main.go` — tambah `"form-builder"` ke `InternalURL`.
- `services/form-builder/` (baru): `main.go`, `go.mod`, `Dockerfile`, `.air.toml`, `identity.go`, `rbac.go` (baca key `it`), `db.go` (`forms`, `form_responses`), `models_form.go`, `models_response.go`, `validate.go` (key unik, required, nilai ∈ options, tipe cocok), `form_handlers.go`, `response_handlers.go`, `export.go`, `routes.go`.
- `docker-compose.yml` — service `form-builder-service` + `form-builder-mongo-db` + volume + env gateway.
- `.env` / `.env.example` — `FORM_BUILDER_SERVICE_PORT`, `MONGO_FORM_BUILDER_DB`.

**Urutan TDD:** 1) `validate_test.go` → `validate.go` · 2) `export_test.go` → `export.go` (CSV) · 3) `rbac_test.go` (gate `it`) · 4) handlers + routes + db · 5) wiring gateway + compose → smoke end-to-end.

**Catatan:** jangan migrasikan form approval yang sudah jalan (leave/overtime/correction) ke form-builder generik — itu punya workflow/SSO khusus. Form Builder untuk **kasus baru/ad-hoc** dulu. Submission file → [[Microservices - File Service]]; auth via [[CORE - SSO Flow]].

## Dokumen Terkait

- [[HRIS - Employee Request & Approval]] · [[GA - Checklist Management]] · [[GA - Guestbook System (Complete)]]
- [[Microservices - File Service]] · [[CORE - SSO Flow]] · [[CORE - API Master Gateway]] · [[DB - Overview and Notes]] · [[ROADMAP]]
