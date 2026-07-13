## Deskripsi

*HRD Document Service mengelola **dokumen HRD** (SOP, Syarat & Ketentuan, Kebijakan, dll.) dengan model reusable: `title + body` (rich-text) + **penyasaran (`targets`) polimorfik** (semua/posisi/departemen/jenis-pengajuan/karyawan), **versioning immutable**, dan **acknowledgment** per-versi. Sisi implementasi dari [[HRIS - HRD Documents]] & [[ADR - 0013 HRD Documents]].*

- **Stack**: Go + Fiber v2 + MongoDB (`hrd_document_db`) — selaras pola service bip-erp lain.
- **Path**: `services/hrd-document` (port `6990`).
- **Status**: ⚠️ **Implemented (Fase 1 BE)**. Di belakang [[CORE - API Master Gateway]] (map `/api/hrd-document/*`), auth **SSO**, RBAC `system_roles["hris"]` (**author=`isHR`** staf HR; registry-type tulis=`isHRAdmin`). Konten body = **Markdown** (`body_md`, selaras editor FE). **FE author = di kode** ([[APP - Web ERP]] PR #276); **employee-facing FE, soft-validate target ke sumber, enforcement ack di BE = belum** (lihat Catatan).

## Endpoint / Fitur (Sudah Diimplementasikan — Fase 1 BE)

### Registry jenis dokumen
- `GET /document-types` (isHR) — daftar jenis. `POST` / `PUT /:id` (isHRAdmin). Di-seed default **sop / terms / policy / guideline** (idempoten); HR bisa tambah tanpa deploy.

### Dokumen (kelola HR)
- `POST /documents` (isHR) — buat **draft** (`type`, `title`, `body_md`, `targets[]`, `ack_required`).
- `GET /documents` (isHR, filter `?status=`/`?type=`) · `GET /documents/:id` (isHR).
- `PUT /documents/:id` (isHR) — edit konten kerja/config · `DELETE /documents/:id` (isHR, **hanya draft**).
- `POST /documents/:id/publish` (isHR) — snapshot konten kerja ke **versi baru IMMUTABLE** + `current_version++` + status `published` (isi wajib non-kosong).
- `GET /documents/:id/versions` + `GET /documents/:id/versions/:v` (isHR) — riwayat versi.

### Karyawan (self-service)
- `GET /my/documents` (auth) — dokumen **published** yang berlaku untuk karyawan (resolve `targets` vs posisi/dept/employee_id + `all`); **konten dari versi terbit**; sertakan status `acked`. Filter `?request_type=Cuti` → **S&K saat pengajuan** (dokumen yang menyasar jenis pengajuan itu).
- `POST /documents/:id/ack` (auth) — karyawan **setuju versi aktif** (idempoten per dokumen+versi+karyawan).

## Model Data (`hrd_document_db`)

- `hrd_document` — identitas + config + konten kerja: `type`, `title`, `body_md` (Markdown kanonik) + `body_text` (turunan teks polos via `toPlainText`, untuk search/preview), `targets[]{type,value,label}`, `ack_required`, `status` (draft/published/archived), `current_version`.
- `hrd_document_version` — **snapshot konten immutable** per publish (`document_id`, `version`, `title`, `body_md/text`, `published_by/at`). Ack terikat ke versi.
- `hrd_document_ack` — persetujuan (`document_id`, `version`, `employee_id`, `agreed_at`).
- `hrd_document_type` — registry jenis (`key`, `label`, `is_active`).

**Penyasaran**: `targets[]` semantik **OR** (berlaku bila cocok salah satu); `scope_type` ENUM 5 dimensi `all|position|department|request_type|employee`. `request_type` kontekstual (S&K saat pengajuan), tak dicocokkan di daftar umum.

## Belum Diimplementasikan / Catatan

- **Soft-validate nilai target ke sumber** (posisi/dept → employee, `request_type` → attendance `/data-type/hr-request`) **belum** — Fase 1 hanya validasi struktural + `label = value`. `fetchEmployeeWork` (employee `/internal/aggregate/employee/:id`) dipakai **fallback** resolusi "Dokumen Saya" (utama: header gateway) — **bentuk respons belum diverifikasi live** (parser toleran).
- **Enforcement ack di BE saat submit request** (attendance `/request/create` cek ack) = **Fase 2** (kini gate di FE).
- **Endpoint arsip** (status `archived`) belum ada; publish/ack **non-atomik** (belum ada unique index) — robustness Fase lanjut.
- **FE author** (form author + targets builder polimorfik + versi/riwayat, body Markdown via `RichTextField`) **diimplementasi** — [[APP - Web ERP]] `erp-frontend` **PR #276** (`/hris/documents`, menu "Dokumen HRD"). **Employee-facing** ("Dokumen Saya", ack, S&K saat pengajuan) = **belum**.
- **Deploy**: env wajib — service butuh `EMPLOYEE_MODULE_URL`+`ATTENDANCE_MODULE_URL`, gateway `HRD_DOCUMENT_MODULE_URL` (`ValidateInternalURL` panic bila kosong). docker-compose: `hrd-document-service` + `hrd-document-mongo-db` (host `32796`).

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — resolusi posisi/departemen karyawan (`/internal/aggregate/employee/:id`) untuk "Dokumen Saya".
- [[Microservices - Attendance Service]] — registry `request_type` (`/data-type/hr-request`) untuk nilai target S&K (soft-validate = Fase lanjut).
- [[CORE - API Master Gateway]] — routing `/api/hrd-document/*`. [[ADR - 0002 Database-per-Service]] — DB terpisah.

## Dokumen Terkait

- [[HRIS - HRD Documents]] (konsep + persona) · [[ADR - 0013 HRD Documents]] (keputusan desain) · [[Microservices - Employee Service]] · [[Microservices - Attendance Service]]
