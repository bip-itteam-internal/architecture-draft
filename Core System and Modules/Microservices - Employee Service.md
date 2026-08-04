## Deskripsi

*Employee Service adalah master data karyawan sekaligus **sumber kebenaran (source of truth) untuk autentikasi & onboarding** di seluruh ekosistem bip-erp. Service ini menangani login (username/employee_id, PIN, biometric), registration, password hashing, serta mengelola data KPI, contract, BPJS, dan vacation quota. Selain itu ia berperan sebagai feed data lintas-service yang dikonsumsi oleh service lain. Ini adalah service terbesar dan paling lengkap (~85 route).*

- **Stack:** Go + Fiber v2 + MongoDB (replica set)
- **Path:** `services/employee`
- **Status**: ✅ Implemented penuh — service terbesar & paling lengkap, tanpa stub berarti · ✅ **multi-perusahaan (tenant)**: fondasi + direktori/agregat karyawan sudah ter-scope (F2-A, PR #659); sisa catatan kecil di bawah & [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]

## Endpoint / Fitur (Sudah Diimplementasikan)

**Auth & Registration (sumber SSO)**
- `POST /auth/login` — login via username atau employee_id, dengan device-hardening + akun bypass, mengembalikan PayloadJWT ke gateway
- `POST /auth/login-pin`, `POST /auth/login-biometrics` — login alternatif via PIN / biometric
- `GET /auth/refresh` — refresh token
- `POST /auth/verify-pin` — verifikasi PIN
- `POST /onboarding/register` — registrasi karyawan baru (temporary password → set username/password/PIN)
- Internal: `GET /internal/auth/user/:username`, `GET /internal/auth/employee/:employee_id`, `POST /internal/auth/change-password`, `GET /internal/auth/roles`, `POST /internal/auth/disable`
- Password & PIN di-hash via `auth.EncryptPassword`

**Account Admin (IT-staff, `RequireITStaff`)** — grup `/account/*` (operasi admin akun langsung di Employee Service)
- `PATCH /account/active-status` — set status aktif/nonaktif akun
- `PATCH /account/forget-device` — **revoke semua registered device & web browser** (set `inactive`) **tanpa** mengubah password/PIN; untuk kasus ganti perangkat / lepas tautan device lama. Respon: "All devices and browsers revoked"
- `PATCH /account/reset` — **hard reset** akun: kosongkan username/PIN, password sementara = `employee_id`, `has_registered=false`, revoke device/browser, role dipertahankan → karyawan onboarding ulang
- `GET /account/roles`, `PATCH /account/roles` — baca / set `system_roles`
> Catatan: sebagian operasi akun juga diorkestrasi via [[CORE - IT Orchestrator]] (mis. reset-password, roles); `/account/forget-device` & `/account/reset` adalah endpoint **langsung** Employee Service (gated IT-staff).

**Master Data — Departments & System Roles**
- `GET /master/departments`, `GET /master/departments/:key` — list / detail department (key, name, positions, roles)
- `POST /master/departments`, `PUT /master/departments/:key`, `DELETE /master/departments/:key` — CRUD department (`RequireHRISOrITSupervisor`: supervisor/admin HRIS **atau** IT — halaman Master Data di-link dari menu IT, sebelumnya HRIS-only sehingga akun IT 403; fix 17 Juli 2026)
- `GET /master/system-roles` — list system roles (feature-based: insentive, integration, dll)
- `POST /master/system-roles`, `PUT /master/system-roles/:key`, `DELETE /master/system-roles/:key` — CRUD system role (`RequireITSupervisor`: supervisor/admin IT saja — kelola role sistem di bawah IT sejak 9 Juli 2026, commit `b9f85de5`). FE menyembunyikan tombol kelola bila role tak berhak (lihat-saja).
- Seed otomatis: `seedMasterData()` meng-insert default departments (~10) dan system roles (~2) saat collection kosong
- Data-type endpoint (`GET /data-type/:dt`) sekarang membaca dari collection `master_department` / `master_system_role` (sebelumnya hardcoded di source code)
- Model: `MasterDepartment` (key, name, positions[], roles[]) dan `MasterSystemRole` (key, name, roles[]) di `shared-library/models/employee/master_data.go`
- Frontend: halaman CRUD di `/hris/master-data` (tabs Departments + System Roles)

**Training Program (HRIS) — ✅ merged ke main (deploy dev pending)**
- Modul pelatihan karyawan (perluasan service ini, `services/employee/training.go`) + UI `/hris/training`. **Department opsional** (penyelenggara — tak membatasi peserta), **tanpa Branch**; peserta lintas dept di-assign HRD.
- **Master**: CRUD `/training/types` (jenis) & `/training/trainers` (internal via `employee_id` / eksternal), by ObjectID.
- **Transaksi**: CRUD `/training` + filter `?department_key=&status=`; cek FK type/trainer (department **opsional**); **guard transisi status** (Scheduled→Ongoing→Completed / →Cancelled); delete cascade ke peserta.
- **Peserta & kehadiran**: `/training/:id/participants` (enroll — **unique index** `{training_id, employee_id}` anti-duplikat, **tanpa cap keras**; kapasitas = jumlah peserta; FE assign **multi-select** lintas dept), PATCH kehadiran boolean, `GET /training/history/:employeeId`.
- RBAC tulis = `RequireHRISStaff`; GET open (di belakang gateway). Model + validasi murni + unit test di `shared-library/models/employee/training.go`.
- **Backlog/hardening**: PUT = full-replace (FE wajib kirim objek lengkap); enroll belum cek employee ada di `work_data`; list tanpa pagination. Detail konsep: [[HRIS - Training Program]].

**CRUD Employee Data**
- CRUD personal data, personal-documents, work data, work-documents, schedule, dan system-auth
- Transaksi create/update employee (multi-collection, `RequireHRISStaff`) lengkap dengan existence/completeness checks
- `GET /birthdays?month=1-12` — karyawan **aktif** (`$lookup` `system_authentication` + `is_active=true`) yang ulang tahun per bulan (default bulan berjalan); `$lookup` `work_data` untuk posisi/departemen + umur saat ini, urut per tanggal; hanya field aman (tanpa NIK/KK/alamat). Filter bulan & umur dihitung di Go (`date_of_birth` bisa string ISO, bukan BSON Date) + konversi ke WIB (data disimpan midnight WIB sebagai UTC)

**Aggregation / HRIS**
- `GET /v2/internal/aggregate/employees` — join multi-collection + paginated
- `GET /v2/internal/aggregate/employees/summary`, `/it`
- `GET /internal/aggregate/employee/:id`
- `GET /internal/export/all`

**KPI**
- `GET /kpi`, `GET /kpi/dashboard`, `POST /kpi`
- Templates CRUD
- `GET /me/kpi-score` — mode grafik 12 bulan
- Departemen yang satu tim tampil sebagai satu kelompok, dari master data. Detail: [[HRIS - Key Performance Index]]

**Nilai otomatis metrik KPI** — ⚠️ branch `feat/kpi-auto-value`, **belum merge & belum deploy** ([[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]], analisis: [[HRIS - Otomasi Skor KPI]])
- `KPIMetric` bertambah `key` (identitas stabil), `auto` (konfigurasi), serta `auto_value`/`auto_basis`/`auto_cakupan`/`auto_at` (hasil hitung). Semuanya `omitempty`, jadi 70 template & 406 skor lama terbaca apa adanya.
- **Kosakata sumber disamakan dengan frontend** (`otomatis`/`semi`/`manual` di `erp-frontend/src/features/finance/posisi/lib/status-sumber.ts`), bukan padanan baru. `SumberMetrik` **memaksa `manual` selama belum ada `auto_value`**, dan `semi` bila cakupan tim belum 100% — meniru `tampilanSumberKpi()` di FE supaya sumber angka tak bisa berbohong dari sisi mana pun.
- `GET /kpi/auto-values?employee_id=&period=&template_id=` — pratinjau usulan sistem, **read-only**, gerbang sama dengan `POST /kpi`. `POST /kpi` menstempel `auto_*` ke snapshot saat submit (dihitung di situ, karena `ReplaceOne` menimpa seluruh dokumen).
- Dua rumus: `rata_skor_tim` dan `persen_capai_target`, keduanya dibatasi 100 mengikuti pola `(realisasi/target)` di [[Microservices - Insentive Service]]. Cakupan `department` memakai `SupervisedDepartments` dari master data (HRGA menyatu karena master datanya bilang begitu); cakupan `team` memakai `work_data.supervisor_id`.
- **Hitungan yang gagal tidak diisi angka**: `auto_value` dibiarkan kosong dan alasannya ditulis ke `auto_basis`, sehingga sumbernya jatuh ke `manual`. Nilai 0 akan menekan skor penilai tanpa dasar dan tak terbedakan dari tim yang memang berskor 0. Karyawan yang dinilai juga dikeluarkan dari daftar timnya sendiri.
- Migrasi `migrateKPIMetricKeys()` mengisi `metrics[].key` idempoten saat boot (pola `migrateDepartmentPositionItems`); `label` tidak disentuh dan `kpi_score.template` **tidak** dimigrasi karena snapshot beku adalah inti desain penilaian.
- Index baru `kpi_score{employee_id, period}` di `ensureTenantIndexes` (koleksi itu di produksi sebelumnya hanya punya `_id_`).
- **Belum menghasilkan apa pun** sampai HR mengisi konfigurasi `auto` pada metrik lewat `POST /kpi/templates`; tidak ada nama posisi yang di-hardcode. Frontend belum ada.

**Cakupan supervisi antar-departemen**
- `master_department` punya `supervised_by` (key departemen induk) + `supervision_label` (nama pendek kelompok, mis. `HRGA`). Di-seed & di-migrasi idempoten saat startup (hanya mengisi bila field belum pernah ada, jadi nilai yang diatur admin tak tertimpa).
- Service ini **sumber kebenaran** relasi tersebut: mengisi klaim JWT `supervised_departments` saat login, dan melayani `/list?type=supervisor` dengan urutan telusur departemen sendiri → induk.
- Konsep, aturan, dan konsekuensinya: [[HRIS - Organization Structure]]

**Jenjang jabatan — ✅ live di produksi 2026-08-03** (PR [#952](https://github.com/bip-itteam-internal/bip-erp/pull/952), `60e77d53`)
- Koleksi baru `master_job_level` (`key`, `name`, `rank`) + `position_items[].level_key` di `master_department`. Lima tingkat bawaan: Pelaksana(10) · Senior/Officer(20) · Leader(30) · Supervisor(40) · Direktur(50). Model & helper di `shared-library/models/employee/master_data.go` (`JobLevel`, `DefaultJobLevels`, `RankOf`, `MinJarakRank`), handler di `services/employee/job_level.go`.
- ⚠️ **Penanda ORGANISASI, BUKAN sumbu hak akses** ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]). `permission_resolve.go` & `permission_exceptions.go` **tidak boleh menyebutnya sama sekali**, dan itu dikunci `TestJenjangBukanSumbuHakAkses` yang membaca kedua berkas itu — pola sama dengan `internal_routes_guard_test.go`. Dijaga dari sumbernya karena pelanggarannya tak akan membuat satu pun test fungsional gagal.
- **Rank renggang** supaya tingkat baru (mis. Manager ber-rank 45) cukup satu entri di `DefaultJobLevels()` + deploy, tanpa menyentuh dokumen jabatan/karyawan mana pun. Jarak minimalnya dikunci uji.
- `seedJobLevels()` menyisipkan **per key**, bukan skip-if-nonempty seperti `seedMasterDepartments`/`seedMasterSystemRoles`/`seedPermissionSets` — pola itu menuntut fungsi `migrate*` sendiri tiap ada key baru, karena dev & prod tak pernah kosong. Nama yang sudah diubah HR tak ditimpa.
- **GLOBAL**, tanpa `company_id`, beda dari `master_department`. Index unik `key` di `ensureTenantIndexes`.
- `GET /master/job-levels` · `PUT /master/departments/:key/positions/:positionKey/level` (`RequireHRISOrITSupervisor`, sama dengan `menu-hidden`). Frontend: tab **Jenjang Jabatan** di `/hris/master-data`.
- **Belum menghasilkan apa pun sampai HR mengisi**: verifikasi prod 2026-08-03 menunjukkan 5 jenjang ter-seed dan **0 dari 79 jabatan** berjenjang. Aturan & konsekuensinya: [[HRIS - Organization Structure]] · [[HRIS - Career & Promotion]]

**Self-Service (`/me`)**
- Profile, kpi-score, vacation, payroll-approx
- Photo get/upload

**Vacation**
- `GET /vacation`, `POST /vacation/quota`
- `POST /vacation/decrement` — dipanggil oleh attendance

**Contract / BPJS / Analysis**
- Endpoint contract, BPJS, dan analysis (`RequireHRISStaff`)
- Device/browser management + FCM token

**Feed Lintas-Service**
- `GET /list?type=fcm-token|department|supervisor|employee|vacation` — dipakai attendance & notification
- `GET /sync/work-schedules` — dipakai cron attendance; kini **enrich `department`** (dari `work_data`) untuk guard swap same-department ([[ADR - 0006 Swap Jadwal Same-Department]])
- `GET /qr/:employee_id`, `GET /check-unique/:field/:value`, `GET /data-type/:dt`
- MinIO uploads: `POST /upload`, `POST /upload/multiple`
- Cron aktif

## Belum Diimplementasikan / Catatan

- Tidak ada stub berarti — ini service paling lengkap dalam ekosistem bip-erp.
- Department CRM sudah dihapus (di-merge ke BeautyHacks/Kyura); role warehouse belum aktif.
- **Departments, positions, dan system roles** sudah dimigrasikan dari hardcoded source ke **MongoDB master data** (`master_department`, `master_system_role`). Dapat dikelola via CRUD endpoint atau frontend `/hris/master-data`.
- `common.Roles` (tipe system_roles di JWT/MongoDB) diubah dari Go struct dengan fixed field menjadi `map[string]Role` — mendukung penambahan department/role tanpa ubah kode. Format serialisasi JSON/BSON tidak berubah (backward compatible).
- Backward compat string constants (`DeptHR`, `DeptGA`, dll) tersedia di `shared-library/models/employee/master_data.go` untuk consumer yang compare department name.
- **Multi-perusahaan (tenant)** ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]): **fondasi** `WorkData.CompanyID` (di-default BIP saat create via `defaultWorkCompany`), master `Company` (`master_company`) + CRUD `/master/companies` (gate IT supervisor), `resolveCompanyID` + join `master_company` di `/me` (objek `company{key,name,code}`) dan di respons login `new_user` (sapaan onboarding mobile). `/list?type=fcm-token` dan `/list?type=supervisor` menyaring `?company_id=`.
	- **Direktori & agregat karyawan: ✅ ter-scope (F2-A, PR #659).** Helper `companyEmployeeIDs(c)` (`services/employee/company.go:19`) membatasi jalur yang berangkat dari `personal_data`/`system_authentication` (dua koleksi itu tak punya `company_id`, jadi sumber kanonis = `work_data.company_id`). Cakupan: `/v2/internal/aggregate/employees`, `/summary`, `/it`, `/list?type=employee`, `/internal/export/all`, `/view`, plus sub-list sensitif headcount, KPI, `kpi/dashboard`, contract, BPJS, analysis, `/birthdays`, vacation. Index `{company_id, employee_id}` + `master_department.company_id` dipasang idempoten saat boot (`ensureTenantIndexes`) sehingga lookup jadi covered query.
	- **Departemen per-perusahaan** (`master_department.company_id` + scope `/data-type/department`, `/position`, `/master/departments` via `EffectiveCompanyID`): **live di main via PR #652**, memperbaiki PR #649 yang sempat ter-orphan (merged ke branch stacked yang sudah mati). Departemen & posisi kini per-perusahaan (migrasi backfill BIP); perusahaan baru mulai kosong. Supervisi/RBAC (`allMasterDepartments`, `system-list`) sengaja **tetap global** (config BIP-central).
	- **Katalog jadwal data-driven (PR #661)**: `resolveScheduleType` membaca `company_work_schedule` / `company_group_rotation` yang di-sync ke `employee_db` (fallback katalog hardcoded), dipakai di create-employee + `PATCH /employees/work-schedule`. Tanpa ini, `schedule_id` milik perusahaan lain (mis. `ELT-REGULAR`) ditolak "invalid schedule type".
	- **Jalur update parsial diperbaiki (2026-07-30, branch `fix/employee-partial-update` — belum merge)**: `PUT /update/:employee_id/work` dan `/personal` menerima body sebagai map lalu men-`$set` isinya, jadi pemanggil wajib mengirim HANYA field yang diubah. [[CORE - HRIS Orchestrator]] dulu melanggarnya (round-trip struct) sehingga tiap simpan form menimpa `company_id`, `vacation`, dan `photo` dengan nilai nol. Kini orchestrator meneruskan map, dan audit distempel di sini lewat dot-notation `metadata.updated_at`/`updated_by` (`services/employee/partial_update.go`) supaya `metadata.created_*` tak tertimpa. Detail: [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] §Perbaikan jalur edit karyawan.
	- **Sisa catatan**: `executeEmployeeUpdateTransaction` memakai `$set: update.WorkData` **tanpa** `defaultWorkCompany` (`services/employee/func.go:205`) sedangkan `WorkData.CompanyID` ber-tag `bson:"company_id"` tanpa `omitempty`, jadi payload update yang tak menyertakan `company_id` menimpanya jadi `""` (jalur create sudah aman). **Jalur ini terpisah dari rute update parsial di atas dan BELUM diperbaiki.** Pengelompokan KPI (`kpi_group`) & supervisor-lookup masih berbasis **nama departemen**, jadi dua perusahaan dengan nama departemen sama bisa ter-merge.
	- **Korupsi tipe BSON (belum diperbaiki)**: karena rute update parsial men-`$set` nilai mentah dari JSON, tanggal tertulis sebagai **string** dan angka sebagai **double**, padahal model memakai `time.Time`/`int`. Terverifikasi DB dev 2026-07-30: **31 dari 179** `work_data` (`join_date`, `contract_ending`, `fingerprint_id`, `metadata.created_at`) dan **6** `personal_data` (`date_of_birth`). Dokumen itu gagal didekode ke struct; belum ada normalisasi maupun migrasi.

## Dependencies & Integrasi

- **MongoDB** — penyimpanan utama; collections: `personal_data`, `personal_document`, `work_data`, `work_document`, `work_schedule`, `company_work_schedule`, `system_authentication`, `kpi_score`, `company_holiday`, `master_department`, `master_system_role`, `training_type`, `trainer`, `training`, `training_participant`. Lihat [[DB - Overview and Notes]].
- **MinIO** — client langsung untuk upload foto & dokumen.
- [[Microservices - Attendance Service]] — memanggil `POST /vacation/decrement`, mengonsumsi feed `/list` dan cron `/sync/work-schedules`.
- [[Microservices - Notification Service]] — mengonsumsi feed `/list` (fcm-token, supervisor, dll).
- [[Microservices - File Service]] — terkait penyimpanan dokumen/file.
- [[CORE - API Master Gateway]] — menerima PayloadJWT dari endpoint auth (SSO).
- [[CORE - HRIS Orchestrator]] — mengonsumsi aggregate, KPI, contract, BPJS, dan vacation.
- [[CORE - IT Orchestrator]] — mengonsumsi aggregate `/it` dan system-auth roles.

## Dokumen Terkait

- [[APP - MyBharata]]
- [[HRIS - Key Performance Index]]
- [[HRIS - Payroll]]
- [[IT - Background Jobs & Schedulers]] — cron service ini (sync schedule harian 04:00, reminder KPI tgl 1, reset cuti 1 Jan)
