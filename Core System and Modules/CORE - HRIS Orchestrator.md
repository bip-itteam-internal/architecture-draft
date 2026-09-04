## Deskripsi

*HRIS Orchestrator adalah service Fiber yang mengorkestrasi operasi HR yang membentang lintas beberapa backend service sekaligus — employee, attendance, notification, dan MinIO — menjadi satu operasi/transaksi tunggal. Selain file-service, ini adalah satu-satunya komponen yang memegang client MinIO secara langsung, dipakai untuk upload dokumen employee/attendance serta stream preview dokumen. Setiap operasi multi-step (misalnya create employee) dijalankan sebagai transaksi dengan rollback bila salah satu langkah gagal.*

- **Stack:** Go + Fiber v2 (+ client MinIO langsung)
- **Path:** `orchestrator/hris` (port `7000`)
- **Status**: ⚠️ Implemented (ada catatan) — aktif dipakai, tapi `ReadBufferSize` masih default 4 KB di `main` sehingga seluruh rute membalas 431 untuk akun berizin banyak (lihat Catatan)

## Endpoint / Fitur (Sudah Diimplementasikan)

### `/employees/*`
- `PATCH` `personal-data`, `work-data`, `personal-documents`, `work-documents`, `work-schedule` → diteruskan ke employee service.
	- **Pembaruan PARSIAL**: `personal-data` & `work-data` meneruskan body sebagai **map**, bukan struct. Rute tujuan di [[Microservices - Employee Service]] men-`$set` isi body apa adanya, jadi field yang tak dikirim TIDAK boleh ikut terpancar. Round-trip struct yang dipakai sebelumnya melanggar itu dan menimpa `company_id`, `vacation`, serta `photo` dengan nilai nol setiap kali form disimpan (`orchestrator/hris/partial_update.go`, branch `fix/employee-partial-update` — belum merge). Audit **bukan** lagi tanggung jawab orchestrator; `UpsertMetadata` dicabut dari kedua handler dan distempel service pemilik koleksi.
- `GET` `/employees/it`, `GET` `/employees/export`.
- RBAC: `RequireHRISStaff` / `RequireITStaff`.

### `/employees/multi*` — workflow inti
Create/update employee dijalankan sebagai **TRANSAKSI**:
1. Validasi keunikan (email/username) dan keberadaan data lintas 4 collection.
2. Upload dokumen ke MinIO (rollback bila gagal).
3. Panggil employee service `/internal/transaction/create-employee` atau `/update-employee`.
4. Kirim notifikasi WhatsApp (info akun dibuat) ke notification-service via goroutine.

Plus aggregate read: `/v2/multi`, `/v2/multi/summary`, `/:id/multi`.

> **Multi-perusahaan**: rute yang meneruskan ke employee-service **wajib ikut meneruskan query string**, sebab override admin pusat dikirim lewat `?company=`. `/v2/multi/summary` dan `/employees/export` sempat membuangnya sehingga direktori sudah benar (0 karyawan ELT) tapi summary & ekspor tetap memakai angka perusahaan pemakai; diperbaiki di PR #660. Detail: [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]].

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

### ⛔ `ReadBufferSize` masih 4 KB: SELURUH `/api/hris/*` membalas 431 untuk akun berizin banyak

`fiber.New(fiber.Config{BodyLimit: 50 * 1024 * 1024})` di `orchestrator/hris/main.go` tidak menyetel `ReadBufferSize`, jadi berlaku default fasthttp 4 KB. Aturannya dan sebabnya ada di [[CORE - API Master Gateway]]; ringkasnya, gateway menambahkan `BIP-Permissions` dkk ke permintaan sebelum meneruskannya, sehingga yang tiba di sini selalu lebih besar daripada yang dikirim browser.

Diukur di **dev 2026-09-04** lewat gateway, dengan satu header probe 6 KB untuk membuat ukurannya deterministik tanpa bergantung pada izin akun penguji:

| Endpoint | tanpa probe | dengan probe 6 KB |
|---|---|---|
| `/api/hris/employees/v2/multi/summary` | 200 | **431** |
| `/api/it/v2/multi` | 200 | **431** |
| `/api/employee/master/permission-modules` | 200 | 200 |
| `/api/notification/inbox` | 200 | 200 |

Dua baris terakhir adalah kontrolnya: header 6 KB yang sama lolos gateway dan diterima service ber-32 KB, jadi yang menolak memang orchestrator-nya.

⚠️ **Reproduksi TIDAK bisa memakai akun dev biasa.** Sensus di [[CORE - RBAC dan Permission Set]] menemukan hanya segelintir posisi dan akun yang berpaket di dev, jadi `BIP-Permissions` di sana masih di bawah 4 KB dan endpointnya membalas 200 baik sebelum maupun sesudah perbaikan. Verifikasi yang bersandar pada itu membuktikan nol.

Perbaikannya (`ReadBufferSize: 32 * 1024` + penjaga perilaku di `konfig_fiber_test.go`) ada di PR [bip-erp#1708](https://github.com/bip-itteam-internal/bip-erp/pull/1708), **belum merge per 2026-09-04** — ukur ulang sebelum memakai kalimat ini.

## Dependencies & Integrasi

- [[Microservices - Employee Service]] — sumber data employee, target transaksi create/update.
- [[Microservices - Attendance Service]] — data attendance, summary, dan company-holiday.
- [[Microservices - Notification Service]] — pengiriman notifikasi WhatsApp (akun dibuat) via goroutine.
- [[Microservices - File Service]] — domain pengelolaan file; HRIS Orchestrator memegang client MinIO langsung untuk upload/preview dokumen.
- [[DB - Overview and Notes]] — referensi struktur collection yang divalidasi dan diakses.
- Di-route lewat [[CORE - API Master Gateway]] pada prefix `/api/hris/*` (menggunakan internal gateway key).

## Dokumen Terkait

- [[CORE - IT Orchestrator]]
- [[APP - MyBharata]]
