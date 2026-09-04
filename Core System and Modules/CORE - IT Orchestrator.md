## Deskripsi

*IT Orchestrator adalah service Fiber yang mengorkestrasi operasi IT-admin atas beberapa backend service — employee, attendance, dan notification — menjadi satu operasi lintas-service. Berbeda dengan HRIS Orchestrator, RBAC di sini diterapkan secara blanket dan lebih ketat: SEMUA route dilindungi `ValidateGateway` + `RequireITStaff`. Fokusnya adalah manajemen akun, role, reset kredensial, dan allow-list jaringan WiFi.*

- **Stack:** Go + Fiber v2
- **Path:** `orchestrator/it` (port `7001`)
- **Status**: ⚠️ Implemented, ada bug

## Endpoint / Fitur (Sudah Diimplementasikan)

- `/v2/multi` → employee aggregate `/v2/internal/aggregate/employees/it`.
- `/roles/get`, `/roles/set`: baca / replace `system_roles` pada employee.
- `/reset-password`: ambil data system-auth, reset password ke `employee_id`, clear PIN/devices, pertahankan roles, lalu kirim notifikasi WhatsApp (info akun di-reset) via goroutine.
- `/account/activate|deactivate|status|toggle`: pola get-then-set field `is_active` pada employee.
- `/network` `GET`/`POST`/`DELETE`: allow-list WiFi, di-proxy ke attendance service (`/networks`, `/internal/wifi/add|delete`).

> Catatan: orchestrator **tidak** punya aksi "revoke device saja" — `/reset-password` membersihkan device hanya sebagai efek samping. Untuk lepas device **tanpa** reset password (mis. karyawan ganti HP), gunakan Employee Service `/account/forget-device` (lihat [[Microservices - Employee Service]]).

> [!warning] Lima rute di bawah ini KEHILANGAN pemakai terakhirnya
> `/reset-password` dan `/account/activate|deactivate` digantikan grup `/account` milik [[Microservices - Employee Service]], yang menandai dirinya sendiri sebagai pengganti (`// region Employee account operations to replaces orchestrator/it/*`). [[APP - MyBharata]] sudah lama memakai pengganti itu; [[APP - Web ERP]] menyusul lewat PR [erp-frontend#875](https://github.com/bip-itteam-internal/erp-frontend/pull/875), **merged & live di dev 2026-08-09** (prod belum). `/account/status` dan `/account/toggle` bahkan sudah tak dipanggil klien mana pun sebelum itu.
>
> **Jangan langsung dihapus.** Penghapusan rute menuntut pemeriksaan pemakai lain lebih dulu — skrip, integrasi, atau klien yang tak terlihat dari repo frontend mana pun. Pelajaran dari penghapusan `form_type: "request"` masih relevan: yang tampak tak terpakai tetap layak diverifikasi sebelum dibuang, dan pemeriksaannya murah dibanding memulihkan jalur yang mati diam-diam.
>
> Yang **tetap tinggal** di orchestrator dan belum punya pengganti: `/roles/get`, `/roles/set`, `/network*`, dan `/v2/multi` — daftar karyawan versi ini punya filter departemen yang `GET /employee/view?system=it` belum punya.

## Belum Diimplementasikan / Catatan

> ⚠️ Bagian ini berisi bug penting.

- **Response payload dibuang:** `getRolesByEmployeeID`, `getAccountStatus`, `activateAccount`, `deactivateAccount`, dan `toggleAccountStatus` membangun objek response lengkap (roles / is_active / action) tetapi hanya mengembalikan `{"message","status"}` generik — data yang diharapkan tidak pernah terkirim ke caller.
- **Role per-departemen nonaktif:** fungsi `setDepartmentRole`, `removeDepartmentRole`, dan `getRolesByDepartment` sudah ditulis penuh TAPI route-nya (`/roles/get-department`, `/set-department`, `/remove-department`) masih di-comment — sehingga manajemen role per-departemen efektif belum diekspos.
- **Log startup menyesatkan:** mencetak "routes registered" untuk route yang sebenarnya masih di-comment.
- ⛔ **`ReadBufferSize` masih 4 KB**, sama dengan [[CORE - HRIS Orchestrator]]: `orchestrator/it/main.go` tidak menyetelnya, jadi SELURUH `/api/it/*` membalas 431 untuk akun berizin banyak. Terukur di dev 2026-09-04 (`/api/it/v2/multi` → 431 dengan header probe 6 KB, sementara rute service ber-32 KB → 200). Aturan dan sebabnya di [[CORE - API Master Gateway]]; perbaikannya di PR [bip-erp#1708](https://github.com/bip-itteam-internal/bip-erp/pull/1708), **belum merge per 2026-09-04**. Yang membuat ini lebih menggigit di sini daripada kelihatannya: `/roles/*`, `/network*`, dan `/v2/multi` belum punya pengganti di service mana pun (lihat peringatan di atas), jadi tak ada jalur cadangan saat rutenya mati.

### `/roles/set` membalas 502 selama sepuluh hari di dev (2026-07-30 → 2026-08-09)

Mengubah role akun lewat Web ERP gagal dengan `502 Service unavailable`, dan sebabnya **bukan** kode yang salah melainkan container yang tak pernah dibangun ulang.

Tiga commit pada 30 Juli, berurutan dan saling melengkapi:

| Jam | Commit | Isi |
|---|---|---|
| 11:22 | `541ff172` | rute `/internal/*` employee-service digerbang (perbaikan keamanan, benar) |
| 15:21 | `1b17dd2f` | orchestrator meneruskan `ctx` pada lompatan **tulis** system-auth |
| 15:27 | `40dcc7c7` | idem untuk lompatan **baca** (`getCurrentRoles`) |

Dua yang terakhir justru antisipasi atas yang pertama. Tapi image IT-Orchestrator masih **12 Juli**, yang memanggil `getCurrentRoles(employeeID)` tanpa `ctx` — sehingga header `BIP-System-Roles` milik pemanggil tak ikut terkirim, employee-service membalas **403**, dan `setAllRoles` menerjemahkan status ≥400 apa pun (selain 404) jadi **502**. Perbaikannya sudah ada di repo sepuluh hari, hanya tak pernah sampai ke dev.

Dua hal yang memperlambat pelacakan, keduanya sudah ditambal:

- **Galat aslinya tak pernah dicatat.** Yang sampai ke pemakai hanya "Service unavailable", dan tiga sebab yang sangat berbeda — tak terjangkau, ditolak, atau balasan tak terbaca — tampak persis sama. Kini status dan galatnya di-log (`[ERROR] getCurrentRoles ... status=%d err=%v`).
- **Cache Redis di gateway sempat menyesatkan reproduksi.** Kuncinya `employee_id` + path tanpa melihat izin, sehingga dua token berbeda memberi hasil identik sampai cache dikosongkan. Ini juga berarti perubahan hak seseorang bisa tertutup respons GET yang sudah ter-cache untuk sesaat.

> **Pola yang sama menggigit dua kali dalam satu hari.** Sebelumnya `api-gateway` — image 12 Juli yang belum mengenal klaim `permissions` — membuat SELURUH permission-set tak pernah aktif di dev (lihat [[CORE - RBAC dan Permission Set]]). Tujuh service lain masih memakai image 12 Juli. Membaca kode di repo tidak cukup untuk menyimpulkan perilaku lingkungan.

## Dependencies & Integrasi

- [[Microservices - Employee Service]] — sumber/target data employee, roles, system-auth, dan status akun.
- [[Microservices - Attendance Service]] — target proxy untuk allow-list jaringan WiFi.
- [[Microservices - Notification Service]] — pengiriman notifikasi WhatsApp (akun di-reset) via goroutine.
- [[DB - Overview and Notes]] — referensi collection `system_roles`, `system-auth`, dan field akun.
- Di-route lewat [[CORE - API Master Gateway]] pada prefix `/api/it/*` (menggunakan internal gateway key).

## Dokumen Terkait

- [[CORE - HRIS Orchestrator]]
- [[IT - Employee System]]
