# Microservices - Task Management Service

## Deskripsi

*Task Management Service adalah backend **IT Helpdesk / ticketing** internal ERP yang dipadukan dengan board Kanban. Desk dimiliki dan ditangani oleh **divisi IT**, sementara **karyawan dari semua divisi dapat membuat (submit) tiket** untuk meminta bantuan/penyelesaian. Tiket ditriase oleh tim IT melalui workflow Kanban (`Request → Todo → On Going → Testing → Done`, ditambah jalur `Ditolak`). Service ini menyediakan gate approval, engine SLA dua dimensi (response + resolution) dengan scheduler eskalasi per jam, update realtime via WebSocket, push notification FCM serta inbox melalui notification-service, attachment (MinIO), comment, checklist, audit trail, dan reporting/dashboard.*

> Catatan positioning: kode saat ini masih mendukung multi-divisi (Space per divisi, supervisor per divisi, admin/sekretaris lintas-divisi). Sesuai positioning IT Helpdesk, penanganan difokuskan ke divisi IT dengan semua divisi sebagai requestor — pembatasan scope ke IT perlu dipertimbangkan di implementasi.

- **Stack:** Go + Fiber v2 + MongoDB + MinIO + WebSocket
- **Path:** `services/task-management`
- **Status:** ✅ Implemented penuh (aktif dikembangkan, branch `feat/sso-task-management`)

## Endpoint / Fitur (Sudah Diimplementasikan)

### Bootstrap & Identity
- `GET /health` — health check.
- `GET /me` — identitas SSO (diambil dari header gateway) dilengkapi nomor telepon dari ERP.
- `GET /ws` — koneksi WebSocket (auth lewat query `?token=` JWT) untuk broadcast event realtime.

### Spaces (board Kanban per divisi)
- `POST /spaces` — create Space; validasi divisi harus ada di ERP, seed otomatis 5 stage + 3 priority default.
- `GET /spaces` & `GET /spaces/:id` — list dan detail Space.
- `PUT /spaces/:id` & `DELETE /spaces/:id` — update/delete; gated untuk admin atau supervisor divisi terkait. Stage wajib (`Request`/`Todo`/`Done`) dilindungi dari penghapusan.

### Tasks
- `POST /tasks` — create task (status awal `Request`, set `response_due_at = now + 24h`).
- `GET /tasks/:id` — detail task (populated).
- `GET /tasks/filter` — list dengan RBAC + filter (`space_id`, `status`, `assigned_to_me`, `created_by_me`, `pending_my_approval`, dll), search, dan pagination.
- `PUT /tasks/:id/status` — ubah status (set `completed_at` saat mencapai `Done`).
- `PUT /tasks/:id/assign`, `/archive`, `/unarchive`, `/due-date`, `/priority`, `/space` — mutasi atribut task.
- `GET /tasks/:id/history` — riwayat perubahan task.
- `DELETE /tasks/:id` — hapus task.

### Approval
- `POST /tasks/:id/approve` — approve task. Untuk transisi `Request → Todo` WAJIB body `start_date`, `due_date`, `priority_id`; stamp `responded_at` (menghentikan SLA response clock). Untuk `Testing → Done` stamp `completed_at`.
- `POST /tasks/:id/reject` — tolak task (status `Ditolak`).

### SLA Engine (dua dimensi)
- **Response:** `response_due_at` vs `responded_at`. **Resolution:** `due_date` vs `completed_at`.
- State: `none` / `on_track` / `warning` / `breached` / `met`; `warning` aktif di 80% window.
- Default: response 24 jam, resolution 72 jam (dapat di-override per-priority).
- Scheduler eskalasi: goroutine background berjalan per jam, mengirim notifikasi `warning`/`breach` bertingkat sekali masing-masing (response breach → supervisor + admin; resolution breach → assignee + supervisor).

### Reports / Dashboard
- `GET /tasks/stats` & `GET /tasks/admin-stats` — statistik task.
- `GET /report/summary-by-department` — ringkasan per divisi.
- `GET /report/timeline` — timeline.
- `GET /report/manpower-performance` — performa manpower.
- `GET /report/sla` — rate on-time response & resolution (overall + per divisi, dengan rentang tanggal).

### Lain-lain
- **Attachments** — upload ke MinIO, allowlist MIME, cap 25MB, presigned URL untuk preview.
- **Comments** & **Checklist** — kolaborasi pada task.
- **Notifications** — `GET /notifications`, `/unread-count`, `PUT /read-all`, `/:id/read`, `DELETE /:id`. Fan-out ke Mongo + WebSocket live + FCM/inbox via notification-service.
- **Users/departments** — data dari ERP untuk dropdown.
- **Audit** — `GET /audits` (admin) untuk audit trail.

## Belum Diimplementasikan / Catatan

- Tidak ada stub/TODO yang tersisa di kode.
- `responded_at` hanya di-set melalui alur approve.
- `GET /report/sla` menghitung `warning`/`on_track` sebagai "met" — artinya "belum breach", bukan strictly tepat waktu.
- `getAdminTaskStats` saat ini merupakan alias dari `getTaskStats`.
- Field `Space.OwnerID` ada tetapi belum dipakai.
- Tipe notifikasi lama `due-soon`/`overdue` kini tidak terpakai (dilebur ke eskalasi SLA).

## Dependencies & Integrasi

- **Auth = SSO via API gateway** (tanpa login lokal). Lihat [[CORE - API Master Gateway]]. Role diambil dari `system_roles["task-management"]`: **admin** (sekretaris lintas-divisi) > **supervisor** (divisi sendiri) > **staff**.
- **MongoDB** sendiri untuk koleksi task, space, notifications, audits. Lihat [[DB - Overview and Notes]].
- **ERP employee_db (read-only)** untuk data karyawan/divisi. Lihat [[Microservices - Employee Service]].
- **notification-service** untuk push FCM (`/fcm/send-personal`) + inbox (`/inbox/send`). Lihat [[Microservices - Notification Service]].
- **MinIO** untuk penyimpanan attachment. Lihat [[Microservices - File Service]].
- **shared-library** untuk utilitas bersama antar service.

## Dokumen Terkait

- [[APP - Dynamic Task Tracker]] — sisi FE/aplikasi task tracker.
