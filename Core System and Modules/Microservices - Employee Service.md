## Deskripsi

*Employee Service adalah master data karyawan sekaligus **sumber kebenaran (source of truth) untuk autentikasi & onboarding** di seluruh ekosistem bip-erp. Service ini menangani login (username/employee_id, PIN, biometric), registration, password hashing, serta mengelola data KPI, contract, BPJS, dan vacation quota. Selain itu ia berperan sebagai feed data lintas-service yang dikonsumsi oleh service lain. Ini adalah service terbesar dan paling lengkap (~85 route).*

- **Stack:** Go + Fiber v2 + MongoDB (replica set)
- **Path:** `services/employee`
- **Status:** ✅ Implemented penuh — service terbesar & paling lengkap, tanpa stub berarti

## Endpoint / Fitur (Sudah Diimplementasikan)

**Auth & Registration (sumber SSO)**
- `POST /auth/login` — login via username atau employee_id, dengan device-hardening + akun bypass, mengembalikan PayloadJWT ke gateway
- `POST /auth/login-pin`, `POST /auth/login-biometrics` — login alternatif via PIN / biometric
- `GET /auth/refresh` — refresh token
- `POST /auth/verify-pin` — verifikasi PIN
- `POST /onboarding/register` — registrasi karyawan baru (temporary password → set username/password/PIN)
- Internal: `GET /internal/auth/user/:username`, `GET /internal/auth/employee/:employee_id`, `POST /internal/auth/change-password`, `GET /internal/auth/roles`, `POST /internal/auth/disable`
- Password & PIN di-hash via `auth.EncryptPassword`

**CRUD Master Data**
- CRUD personal data, personal-documents, work data, work-documents, schedule, dan system-auth
- Transaksi create/update employee (multi-collection, `RequireHRISStaff`) lengkap dengan existence/completeness checks

**Aggregation / HRIS**
- `GET /v2/internal/aggregate/employees` — join multi-collection + paginated
- `GET /v2/internal/aggregate/employees/summary`, `/it`
- `GET /internal/aggregate/employee/:id`
- `GET /internal/export/all`

**KPI**
- `GET /kpi`, `GET /kpi/dashboard`, `POST /kpi`
- Templates CRUD
- `GET /me/kpi-score` — mode grafik 12 bulan

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
- `GET /sync/work-schedules` — dipakai cron attendance
- `GET /qr/:employee_id`, `GET /check-unique/:field/:value`, `GET /data-type/:dt`
- MinIO uploads: `POST /upload`, `POST /upload/multiple`
- Cron aktif

## Belum Diimplementasikan / Catatan

- Tidak ada stub berarti — ini service paling lengkap dalam ekosistem bip-erp.
- Hanya beberapa entry registry yang masih di-comment, yaitu department CRM dan role warehouse.

## Dependencies & Integrasi

- **MongoDB** — penyimpanan utama; collections: `personal_data`, `personal_document`, `work_data`, `work_document`, `work_schedule`, `company_work_schedule`, `system_authentication`, `kpi_score`, `company_holiday`. Lihat [[DB - Overview and Notes]].
- **MinIO** — client langsung untuk upload foto & dokumen.
- [[Microservices - Attendance Service]] — memanggil `POST /vacation/decrement`, mengonsumsi feed `/list` dan cron `/sync/work-schedules`.
- [[Microservices - Notification Service]] — mengonsumsi feed `/list` (fcm-token, supervisor, dll).
- [[Microservices - File Service]] — terkait penyimpanan dokumen/file.
- [[CORE - API Master Gateway]] — menerima PayloadJWT dari endpoint auth (SSO).
- [[CORE - HRIS Orchestrator]] — mengonsumsi aggregate, KPI, contract, BPJS, dan vacation.
- [[CORE - IT Orchestrator]] — mengonsumsi aggregate `/it` dan system-auth roles.

## Dokumen Terkait

- [[APP - Mobile Application]]
- [[HRIS - Key Performance Index]]
- [[HRIS - Payroll]]
