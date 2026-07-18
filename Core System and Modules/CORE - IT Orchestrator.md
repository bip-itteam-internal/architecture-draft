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

## Belum Diimplementasikan / Catatan

> ⚠️ Bagian ini berisi bug penting.

- **Response payload dibuang:** `getRolesByEmployeeID`, `getAccountStatus`, `activateAccount`, `deactivateAccount`, dan `toggleAccountStatus` membangun objek response lengkap (roles / is_active / action) tetapi hanya mengembalikan `{"message","status"}` generik — data yang diharapkan tidak pernah terkirim ke caller.
- **Role per-departemen nonaktif:** fungsi `setDepartmentRole`, `removeDepartmentRole`, dan `getRolesByDepartment` sudah ditulis penuh TAPI route-nya (`/roles/get-department`, `/set-department`, `/remove-department`) masih di-comment — sehingga manajemen role per-departemen efektif belum diekspos.
- **Log startup menyesatkan:** mencetak "routes registered" untuk route yang sebenarnya masih di-comment.

## Dependencies & Integrasi

- [[Microservices - Employee Service]] — sumber/target data employee, roles, system-auth, dan status akun.
- [[Microservices - Attendance Service]] — target proxy untuk allow-list jaringan WiFi.
- [[Microservices - Notification Service]] — pengiriman notifikasi WhatsApp (akun di-reset) via goroutine.
- [[DB - Overview and Notes]] — referensi collection `system_roles`, `system-auth`, dan field akun.
- Di-route lewat [[CORE - API Master Gateway]] pada prefix `/api/it/*` (menggunakan internal gateway key).

## Dokumen Terkait

- [[CORE - HRIS Orchestrator]]
- [[IT - Employee System]]
