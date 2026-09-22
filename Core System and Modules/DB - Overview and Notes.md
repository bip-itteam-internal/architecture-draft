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
- kpi_template_assignment (🟡 bip-erp PR [#1298](https://github.com/bip-itteam-internal/bip-erp/pull/1298), belum merge) — penetapan template KPI per karyawan: `employee_id`·`template_id`·`company_id`·**`berlaku_mulai`** (`YYYY-MM`)·`metadata`. Ada karena satu jabatan tidak selalu satu template (AR Staff Finance memegang tiga) sedangkan `work_data` tak menyimpan pembedanya. **Berperiode**: mengganti template = MENAMBAH baris, bukan menimpa, supaya penilaian bulan lampau tetap memakai penetapan yang berlaku saat itu. Koleksi tersendiri (bukan field `work_data`) mengikuti alasan `employee_resign`. Index unik `{employee_id, berlaku_mulai}`; disemai sekali saat boot dari riwayat `kpi_score`
- account_status_log (🔜 branch bip-erp `feat/employee-status-akun-bertanggal`, belum merge) — jejak tiap perubahan `system_authentication.is_active`: `employee_id`·`company_id`·`sebelum`·`sesudah`·`alasan`·`sumber` (`it`/`resign`/`akun_luar`)·`resign_id`·`pelaku`·`created_at`. Ada karena `system_authentication` tak punya satu pun stempel waktu, sehingga penonaktifan yang tak lewat menu Resign tak bisa ditanggalkan (diukur PROD 2026-09-21: 24 dari 35 akun non-aktif). Koleksi sendiri, bukan menumpang `employee_resign`: perubahan status akun tak selalu kepergian (skorsing, akun luar) dan menumpangkannya akan mencemari demografi attrition. Index `{employee_id, created_at:-1}`. Keputusan: [[ADR - 0113 Actual vs Planning MPP Dihitung Sistem per Bulan, Berpijak pada Jejak Keluar Bertanggal]] + perluasan [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]]
- company_holiday
- master_department (departments + positions + roles per dept; seed otomatis) — kini **`company_id` per-perusahaan** (PR #652, migrasi backfill BIP; supervisi/RBAC tetap global — [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]])
- master_divisi (🔜 branch bip-erp `feat/employee-master-divisi`, belum merge) — pengelompokan departemen untuk PELAPORAN: `key`·`name`·`urutan`·`company_id`·`metadata`, indeks **unik** `{company_id, key}`. Ter-scope per perusahaan seperti `master_department`; departemen menunjuknya lewat `divisi_key` (kosong = belum dipetakan HRD). Seed empat divisi (Commercial·Operational·Supporting·Management) **hanya untuk perusahaan yang belum punya satu pun divisi**, supaya penghapusan oleh HRD tak hidup lagi tiap boot. ⛔ Jangan dikira sama dengan `supervision_label` di `master_department` (kelompok SUPERVISI, mis. `HRGA`), dengan `common.ReachDivision` pada paket izin, atau dengan `space.division` di task-management — ketiganya berisi/berarti DEPARTEMEN. Keputusan: [[ADR - 0113 Actual vs Planning MPP Dihitung Sistem per Bulan, Berpijak pada Jejak Keluar Bertanggal]]
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
- ⛔ marketing_teams/team_shops/team_members — RETIRED 2026-09-15 (Fase Contract, [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]]); dead data, digantikan `department_shops`
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

> Catatan: task-management juga membaca `employee_db` (ERP) secara **read-only** untuk memperoleh nama/divisi (`erpdb.go`, env `MONGO_URI_ERP`), dan sejak modul Engagement juga membaca `attendance_db` secara read-only untuk memeriksa siapa sedang cuti penuh (`attendancedb.go`, env `MONGO_URI_ATTENDANCE`; terverifikasi `origin/main` 2026-09-07). Keduanya pengecualian atas [[ADR - 0002 Database-per-Service]] dan dicatat sebagai utang di [[REF - Kepemilikan Data]] §Pengecualian.

### recruitment — `recruitment-mongo-db`
Doc: [[Microservices - Recruitment Service]] (⚠️ Fase 1-3)
Daftar di bawah = seluruh `mongodb.GetCollection(...)` di `services/recruitment` (diperiksa 2026-09-10).
- job_requisition
- job_posting
- candidate
- interview
- interview_round · interview_feedback
- candidate_test_result *(hasil babak bertipe tes: Psikotest & Technical Test)*
- psikotes_session *(sesi psikotes online Kraepelin; 3 index, dua di antaranya UNIK: `(candidate_id, round_id)` dan `token`)*
- background_check
- offer
- manpower_plan
- mpp_vacancy_decision *(keputusan HR atas posisi kosong akibat resign: `diganti`/`tidak_diganti`; tanpa index. bip-erp #1961 (merged 2026-09-17) menambah `resign_id` ber-omitempty; dokumen lama tanpa field itu tetap berlaku lewat aturan waktu, lihat [[Microservices - Recruitment Service]])*
- job_type · candidate_source · interview_type · job_location · assessment_type *(master)*
- onboarding_template · onboarding_instance · onboarding_review · onboarding_review_response
- email_template
- candidate_assessment *(legacy — hanya dibaca `migrate_test_result.go`, tak ditulis lagi)*
- audit_logs

> ⚠️ `screening_result`, `technical_test_result`, `psychotest`, dan `psychotest_result` **tidak ada** dan tak pernah lagi ditulis service ini; dokumen lama yang menyebutnya sudah dikoreksi di [[Microservices - Recruitment Service]] dan [[HRIS - Recruitment]].

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

> 🟡 **Tahap 2 — Training & Performance Officer** (bip-erp PR [#1903](https://github.com/bip-itteam-internal/bip-erp/pull/1903) rencana pelatihan, [#1904](https://github.com/bip-itteam-internal/bip-erp/pull/1904) sertifikat; **TERBUKA, belum merge, belum deploy dev maupun prod** — diperiksa 2026-09-16). Empat koleksi baru di bawah ini ada di kode branch, belum di `main`.

- training_plan_item (✅ PR #1903 merged, live prod per 2026-09-17) — satu butir rencana pelatihan tahunan: `company_id`·`tahun`·`bulan`·`judul`·`status` (`aktif`/`dibatalkan`)·`training_type_id?`·`department_keys?` (daftar departemen sasaran, informasional; field lama `department_key` tunggal hanya dibaca dari dokumen lama, bip-erp PR [#1939](https://github.com/bip-itteam-internal/bip-erp/pull/1939) merged 2026-09-17, belum ter-deploy di prod saat diukur 2026-09-17 sesudah merge) (`models_rencana.go:71-96`, `services/learning`). Status pelaksanaan (`direncanakan`/`terlaksana`/`terlaksana_terlambat`/`belum_terlaksana`/`dibatalkan`) **DIHITUNG dari kelas tertaut** lewat `Training.PlanItemID`, tidak disimpan (`models_rencana.go:17-24`, `models_training.go:107-113`) — sumber KPI `rencana_pelatihan` (`services/employee/kpi_sumber_rencana_pelatihan.go:28`) membacanya lewat `GET /kpi/rencana-pelatihan` di learning-service. Index non-unik `{company_id, tahun, bulan}` dibuat saat registrasi rute, `ensureRencanaIndexes` (`rencana.go:51-60`); koleksi `training` yang sudah ada dapat index tambahan `{company_id, plan_item_id}` di fungsi yang sama (`rencana.go:62-65`).
- training_certificate (🟡 PR #1904) — sertifikat pelatihan, **terbit otomatis** (tak diajukan/disetujui siapa pun), isi dibekukan saat terbit (`SnapshotSertifikat`), nomor **tak pernah dipakai ulang** (`models_sertifikat.go:14-32`, `79-97`). Dua index unik dengan **arti berbeda saat duplicate key** (`sertifikat.go:59-73`): `satu_aktif_per_peserta_kelas` — PARSIAL `{company_id, training_id, employee_id}` filter `aktif:true` — bertabrakan berarti permintaan lain sudah menerbitkan lebih dulu, nomor yang baru diambil hangus (celah urutan diterima); `nomor_unik_per_perusahaan` — `{company_id, nomor}` — bertabrakan berarti COUNTER rusak/ter-restore, dan itu GALAT (melanjutkan diam-diam membakar satu nomor tiap klik) (`sertifikat.go:262-277`). Plus index non-unik `{company_id, employee_id}` (`sertifikat.go:72`).
- training_certificate_counter (🟡 PR #1904) — counter atomik nomor sertifikat lewat `$inc` upsert; kunci `_id` = `"<company_id>|<tahun_terbit_WIB>"` (`kunciCounterSertifikat`, `models_sertifikat.go:172-174`; `ambilUrutSertifikatMongo`, `sertifikat.go:207-219`). Tak ada index tambahan selain `_id` bawaan — tak ditemukan pemanggilan `Indexes().Create*` untuk koleksi ini di `sertifikat.go`.
- training_certificate_setting (🟡 PR #1904) — penanda tangan sertifikat, **SATU dokumen per perusahaan** (`PengaturanSertifikat`, `models_sertifikat.go:99-109`). Index unik `{company_id}` (`sertifikat.go:77`).

> ⚠️ PR #1904 (sertifikat) tidak menyentuh `services/employee` maupun kategori inbox `notification` — diverifikasi Grep atas `services/employee` (worktree branch) dan `request_notify.go` (branch yang sama memakai kategori `request-*` yang sudah ada, untuk pengajuan pelatihan, bukan sertifikat). PR #1903 (rencana) **memang** menambah pembaca di `employee-service`; lihat [[RUN - Deploy Microservices bip-erp]] §3d untuk konsekuensi deploy pasangan ini.

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
