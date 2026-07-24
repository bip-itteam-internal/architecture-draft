## Deskripsi

*Employee Service adalah master data karyawan sekaligus **sumber kebenaran (source of truth) untuk autentikasi & onboarding** di seluruh ekosistem bip-erp. Service ini menangani login (username/employee_id, PIN, biometric), registration, password hashing, serta mengelola data KPI, contract, BPJS, dan vacation quota. Selain itu ia berperan sebagai feed data lintas-service yang dikonsumsi oleh service lain. Ini adalah service terbesar dan paling lengkap (~85 route).*

- **Stack:** Go + Fiber v2 + MongoDB (replica set)
- **Path:** `services/employee`
- **Status**: ✅ Implemented penuh — service terbesar & paling lengkap, tanpa stub berarti · ⚠️ **multi-perusahaan (tenant) parsial** — fondasi ada, banyak read belum ter-scope; lihat catatan & [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]

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

**Cakupan supervisi antar-departemen**
- `master_department` punya `supervised_by` (key departemen induk) + `supervision_label` (nama pendek kelompok, mis. `HRGA`). Di-seed & di-migrasi idempoten saat startup (hanya mengisi bila field belum pernah ada, jadi nilai yang diatur admin tak tertimpa).
- Service ini **sumber kebenaran** relasi tersebut: mengisi klaim JWT `supervised_departments` saat login, dan melayani `/list?type=supervisor` dengan urutan telusur departemen sendiri → induk.
- Konsep, aturan, dan konsekuensinya: [[HRIS - Organization Structure]]

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
- **Multi-perusahaan (tenant)** ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]): **fondasi ADA** — `WorkData.CompanyID` (di-default BIP saat create via `defaultWorkCompany`), master `Company` (`master_company`) + CRUD `/master/companies` (gate IT supervisor), `resolveCompanyID` + join `master_company` di `/me` (objek `company{key,name,code}`) dan di respons login `new_user` (sapaan onboarding mobile). `/list?type=fcm-token` menyaring `?company_id=`. **BELUM ter-scope (leak lintas-perusahaan, di luar fase-1 presensi):** direktori/aggregate karyawan (`/internal/export/all`, `/view`, `/v2/internal/aggregate/employees*`, `/list?type=employee|supervisor`, `/analysis`, `/data-type/headcount`), KPI (`kpi_group` merge department-only), contract, BPJS, vacation, `/birthdays` — `EffectiveCompanyID` belum dipakai di read ini. `executeEmployeeUpdateTransaction` & create schedule bisa menulis `company_id=""` (perlu guard). **Departemen per-perusahaan (`master_department.company_id` + scope `/data-type/department`,`/position`,`/master/departments`): PR #649 TER-ORPHAN** (merged ke branch stacked yang sudah mati, tak sampai `main`) → re-apply **PR #652**; sampai merge departemen/posisi masih GLOBAL. Supervisi/RBAC (`allMasterDepartments`, `system-list`) sengaja global (config BIP-central).

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
