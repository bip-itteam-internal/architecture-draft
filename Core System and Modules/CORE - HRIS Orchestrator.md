## Deskripsi

*HRIS Orchestrator adalah service Fiber yang mengorkestrasi operasi HR yang membentang lintas beberapa backend service sekaligus — employee, attendance, notification, dan MinIO — menjadi satu operasi/transaksi tunggal. Selain file-service, ini adalah satu-satunya komponen yang memegang client MinIO secara langsung, dipakai untuk upload dokumen employee/attendance serta stream preview dokumen. Setiap operasi multi-step (misalnya create employee) dijalankan sebagai transaksi dengan rollback bila salah satu langkah gagal.*

- **Stack:** Go + Fiber v2 (+ client MinIO langsung)
- **Path:** `orchestrator/hris` (port `7000`)
- **Status:** ✅ Implemented, aktif dipakai

## Endpoint / Fitur (Sudah Diimplementasikan)

### `/employees/*`
- `PATCH` `personal-data`, `work-data`, `personal-documents`, `work-documents`, `work-schedule` → diteruskan ke employee service.
- `GET` `/employees/it`, `GET` `/employees/export`.
- RBAC: `RequireHRISStaff` / `RequireITStaff`.

### `/employees/multi*` — workflow inti
Create/update employee dijalankan sebagai **TRANSAKSI**:
1. Validasi keunikan (email/username) dan keberadaan data lintas 4 collection.
2. Upload dokumen ke MinIO (rollback bila gagal).
3. Panggil employee service `/internal/transaction/create-employee` atau `/update-employee`.
4. Kirim notifikasi WhatsApp (info akun dibuat) ke notification-service via goroutine.

Plus aggregate read: `/v2/multi`, `/v2/multi/summary`, `/:id/multi`.

### `/attendances/*`
- `summary`.
- `PATCH` `/:id/update` (mendukung JSON maupun multipart + upload dokumen ke MinIO dengan rollback).
- CRUD `company-holiday`.

### Lainnya
- `bank-detail` routes.
- `/public/documents/*`: preview dokumen (KTP/KK/work/attendance) **tanpa JWT**.

## Belum Diimplementasikan / Catatan

- Secara fungsional sudah Implemented.
- Terdapat **dead code**: blok `PATCH /:id/update` versi lama yang masih di-comment pada route attendance.

## Dependencies & Integrasi

- [[Microservices - Employee Service]] — sumber data employee, target transaksi create/update.
- [[Microservices - Attendance Service]] — data attendance, summary, dan company-holiday.
- [[Microservices - Notification Service]] — pengiriman notifikasi WhatsApp (akun dibuat) via goroutine.
- [[Microservices - File Service]] — domain pengelolaan file; HRIS Orchestrator memegang client MinIO langsung untuk upload/preview dokumen.
- [[DB - Overview and Notes]] — referensi struktur collection yang divalidasi dan diakses.
- Di-route lewat [[CORE - API Master Gateway]] pada prefix `/api/hris/*` (menggunakan internal gateway key).

## Dokumen Terkait

- [[CORE - IT Orchestrator]]
- [[APP - Mobile Application]]
