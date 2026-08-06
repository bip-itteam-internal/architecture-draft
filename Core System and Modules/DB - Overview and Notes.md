## Deskripsi

bip-erp menerapkan pola **database-per-service**: setiap microservice memiliki MongoDB-nya sendiri (container Mongo terpisah) dan menjadi pemilik (ownership) penuh atas datanya. Tidak ada akses langsung lintas-database antar service; komunikasi dilakukan via HTTP internal melalui gateway (lihat [[CORE - API Master Gateway]]). Khusus employee-service berjalan sebagai **replica set** (primary + secondary) agar datanya dapat diekspos read-only untuk konsumen lain. Seluruh server menyimpan waktu dalam **UTC**. Selain MongoDB per service, terdapat dua infrastruktur data bersama: **Redis** (cache & queue) dan **MinIO** (object storage).

- **Status**: ✅ Aktif — pemetaan DB-per-service yang berjalan (grounded ke docker-compose & service).

## Database per Service

Tiap baris berikut menyebutkan nama service, container Mongo, collection utama, dan dokumen service terkait.

### employee — `employee-mongo-primary` / `employee-mongo-secondary` (replica set)
Doc: [[Microservices - Employee Service]]
- personal_data
- personal_document
- work_data
- work_document
- work_schedule
- company_work_schedule
- system_authentication
- kpi_score (beserta KPI templates)
- company_holiday
- master_department (departments + positions + roles per dept; seed otomatis) — kini **`company_id` per-perusahaan** (PR #652, migrasi backfill BIP; supervisi/RBAC tetap global — [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]])
- master_system_role (feature-based role systems: insentive, integration; seed otomatis)
- master_company (perusahaan/tenant multi-perusahaan: `key`/`name`/`code`; seed BIP; `code` = prefix employee_id). Di dev sudah berisi **2 tenant**: `BIP` + `ELT` (CV Elit).
- company_group_rotation (definisi rotasi shift bergilir, di-sync dari attendance agar resolusi tipe jadwal jadi data-driven; PR #661)
- Index tenant idempoten saat boot (`ensureTenantIndexes`): `work_data {company_id, employee_id}` (covered query untuk himpunan karyawan per perusahaan) + `master_department {company_id}`.

> **Multi-perusahaan (tenant):** `work_data` dan ke-10 koleksi presensi (`attendance_entries`, `leave_request`, `attendance_correction_request`, `business_trip_request`, `schedule_exchange_request`, `guestbook`, `company_work_schedule`, `company_holiday`, `company_wifi`, mood) membawa `company_id` (row-level, default `"BIP"`). Filter di lapisan `common.CompanyID`/`EffectiveCompanyID`. Cakupan & gap: [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]].

### attendance — `attendance-mongo-db`
Doc: [[Microservices - Attendance Service]]
- attendance_entries
- work_schedule
- company_work_schedule
- company_group_rotation
- company_wifi
- company_holiday
- fingerprint_export
- guestbook
- leave_request
- schedule_exchange_request
- attendance_correction_request

### notification — `notification-mongo-db`
Doc: [[Microservices - Notification Service]]
- inbox
- splash
- article — kini ber-`company_id` + `group_wide` (broadcast lintas-perusahaan, hanya admin pusat; migrasi backfill BIP, PR #662 → [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]])

### insentive — `insentive-mongo-db`
Doc: [[Microservices - Insentive Service]]
- employee_performance_mappings
- audit_logs
- cron_locks
- master_kpis
- incentive_results

### integration — `integration-mongo-db`
Doc: [[Microservices - Integration Service]]
- transaction_orders (model terpadu)
- webhook logs
- summary reports
- items / master catalog
- credentials
- holidays
- marketing_teams (grouping tim + shop ACL)
- accurate_products
- accurate_bank_accounts
- accurate_kv_configs
- shopee_escrow_details

### inventory — `inventory-mongo-db`
Doc: [[Microservices - Inventory Service]]
- inventory
- data_master
- repair_history

### tiktok-shop — `tiktok-shop-mongo-db`
Doc: [[Microservices - TikTok Shop Service]]
- tiktok_shop_callbacks
- tiktok_shop_webhooks (payload mentah)

### task-management — `task-management-mongo-db`
Doc: [[Microservices - Task Management Service]]
- task
- space
- notifications
- audits

> Catatan: task-management juga membaca `employee_db` (ERP) secara **read-only** untuk memperoleh nama/divisi.

### recruitment — `recruitment-mongo-db`
Doc: [[Microservices - Recruitment Service]] (⚠️ Fase 1-3)
- job_requisition
- job_posting
- candidate
- screening_result
- interview
- technical_test_result
- psychotest
- background_check
- offer
- audit_logs

### payroll — `payroll-mongo-db`
Doc: [[Microservices - Payroll Service]] (⚠️ Fase 1 — Salary Setup & Config)
- salary_component
- employee_salary
- payroll_config

### learning — `learning-mongo-db` ✅
Doc: [[Microservices - Learning Service]] (live dev + prod 2026-08-06)
- training_type (master jenis pelatihan)
- trainer (master pengajar, internal via `employee_id` atau eksternal)
- training (event pelatihan; `department_key` opsional, diverifikasi ke employee-service lewat HTTP internal)
- training_participant (peserta + kehadiran boolean; unique index `{training_id, employee_id}`)

> Keempatnya **pindahan dari `employee_db`** pada LMS Fase 0, nama koleksi sengaja dipertahankan supaya data terbaca tanpa penyesuaian. Salinan lama di `employee_db` **belum dihapus** (jalan pulang). ⚠️ Belum ada `company_id` di koleksi ini — Fase 1 wajib memasangnya, lihat [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]].

### form-builder — `form-builder-mongo-db` ⚠️
Doc: [[Microservices - Form Builder Service]] (⚠️ merged 2026-08-01, belum live di dev)
- forms (definisi form + sasaran + pengaturan gerbang presensi)
- form_responses (jawaban; `fingerprint` = sidik isi untuk guard idempotensi)
- Keduanya ber-`company_id` **sejak awal** ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]), bukan ditambal belakangan.
- Index idempoten saat boot: `forms {company_id, status}`, `forms {company_id, owner_module}`, `forms {company_id, attendance_gate.enabled, status}` (jalur panas gerbang presensi), `form_responses {form_id, employee_id}`, `form_responses {company_id, employee_id}`.

> Catatan: **tak ada index unik** pada `(form_id, employee_id)` — satu-jawaban-per-orang hanya berlaku bila `settings.single_response` menyala, dan itu per-form; index unik akan salah untuk form yang memang boleh diisi berulang. Penegakannya di handler.

## Infrastruktur Data Bersama (Redis, MinIO)

- **Redis** — cache response gateway sekaligus queue antar service. Key di-namespace per domain, mis. prefix `srv:integration`.
- **MinIO** — object storage bersama. Objek dipisah per domain melalui prefix path: `employee/`, `attendance/`, `task/`, `notification/`.

## Catatan

- Setiap service mengelola datanya sendiri (ownership). Database satu service tidak diakses langsung oleh service lain.
- Komunikasi antar service dilakukan via HTTP internal melalui gateway, lihat [[CORE - API Master Gateway]] — bukan query/lookup lintas-database.
- Hanya employee-service yang berjalan sebagai replica set (primary + secondary); secondary dipakai untuk akses read-only, termasuk oleh task-management terhadap `employee_db`.
- Cluster primary tidak boleh diubah sembarangan karena belum ada dynamic cluster picker.
- Seluruh waktu disimpan dalam UTC.

## Dokumen Terkait

- [[CORE - API Master Gateway]]
- [[Microservices - Employee Service]]
- [[Microservices - Attendance Service]]
- [[Microservices - Notification Service]]
- [[Microservices - File Service]]
- [[Microservices - Insentive Service]]
- [[Microservices - Integration Service]]
- [[Microservices - Inventory Service]]
- [[Microservices - Task Management Service]]
- [[Microservices - TikTok Shop Service]]
- [[Microservices - Payroll Service]]
