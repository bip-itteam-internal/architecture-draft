# Microservices - Task Management Service

## Deskripsi

*Task Management Service adalah backend **IT Helpdesk / ticketing** internal ERP yang dipadukan dengan board Kanban. Desk dimiliki dan ditangani oleh **divisi IT**, sementara **karyawan dari semua divisi dapat membuat (submit) tiket** untuk meminta bantuan/penyelesaian. Tiket ditriase oleh tim IT melalui workflow Kanban (`Request → Todo → On Going → Testing → Done`, ditambah jalur `Ditolak`). Service ini menyediakan gate approval, engine SLA dua dimensi (response + resolution) dengan scheduler eskalasi per jam, update realtime via WebSocket, push notification FCM serta inbox melalui notification-service, attachment (MinIO), comment, checklist, audit trail, dan reporting/dashboard.*

> Catatan positioning: kode saat ini masih mendukung multi-divisi (Space per divisi, supervisor per divisi; role hanya `supervisor`/`staff`). Sesuai positioning IT Helpdesk, penanganan difokuskan ke divisi IT dengan semua divisi sebagai requestor — pembatasan scope ke IT perlu dipertimbangkan di implementasi.

- **Stack:** Go + Fiber v2 + MongoDB + WebSocket + file-service (MinIO via [[Microservices - File Service]])
- **Path:** `services/task-management`
- **Status:** ⚠️ Implemented (branch `feat/task-management-parity`, dari `main`; belum merge). Paritas penuh dengan FE gateway-cutover. Catatan: **WebSocket butuh rute ingress** (gateway tak proxy WS), **push FCM/inbox ke notification-service ditunda** (WS-only), **role hanya `supervisor`/`staff`** (admin lintas-divisi tidak diaktifkan).

## Endpoint / Fitur (Sudah Diimplementasikan)

### Bootstrap & Identity
- `GET /health` — health check.
- `GET /me` — identitas SSO dari header gateway (`IdentityFromHeaders`). Nomor telepon/foto diambil FE terpisah via `/api/employee/me`.
- `GET /ws` — koneksi WebSocket (auth lewat query `?token=` JWT, divalidasi sendiri). **Masuk via ingress LANGSUNG ke service (bypass gateway)** — didaftarkan sebelum `ValidateGateway`; butuh rute ingress `/ws/task-management → service:/ws` (lihat `WEBSOCKET.md`). Event: `notification` (per user), `task_update`/`space_update` (broadcast).

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
- **Response:** `response_due_at` vs `responded_at` (field diset saat create/approve). **Resolution:** `due_date` vs `completed_at`.
- State (dihitung di `sla.go`, disertakan pada task populated `sla.response/resolution.{due_at,state}`): `none` / `on_track` / `warning` / `breached` / `met`; `warning` aktif di 80% window.
- Default: response **24 jam** (diset saat create), resolution **72 jam** (referensi resolution: `start_date`/`responded_at`/`created_at` → `due_date`). Override per-priority: **TBD**.
- Scheduler eskalasi (`sla_scheduler.go`): goroutine per jam, mengirim notifikasi **breach sekali** per task (ditandai array `sla_notified`): response breach → **supervisor divisi**; resolution breach → **assignee + supervisor**. (Warning hanya untuk badge, belum dieskalasi via notifikasi.)

### Reports / Dashboard
- `GET /tasks/stats` & `GET /tasks/admin-stats` — statistik task.
- `GET /report/summary-by-department` — ringkasan per divisi.
- `GET /report/timeline` — timeline.
- `GET /report/manpower-performance` — performa manpower.
- `GET /report/sla` — rate on-time response & resolution (overall + per divisi, dengan rentang tanggal).

### Lain-lain
- **Attachments** — lewat **[[Microservices - File Service]]** (bukan MinIO langsung; prefix object `task/`, key `MINIO_TASK_KEY`), bukan temp-upload (FE create-task-lalu-upload). Endpoint (`attachment_handlers.go`, `fileclient.go`):
	- `POST /tasks/:id/attachments` — multipart field `file` (satu file/request) → upload ke file-service → simpan `FileAttachment{type:"file"}` di task; respons `{attachment}`. **Batas 4 MB/file** (dari file-service; BE lama dulu 25 MB) → map ke `413`.
	- `POST /tasks/:id/links` — body `{name,url}` → `FileAttachment{type:"link"}`; respons `{link}`.
	- `DELETE /tasks/:id/attachments/:attachmentId` — hapus object di file-service (bila file) + `$pull`; lampiran milik requestor tak bisa dihapus assignee.
	- `GET /tasks/:id/attachments/:fileId/preview` — respons `{url}` = presigned GET (public base MinIO, ~300s); untuk link kembalikan URL apa adanya.
- **Comments** & **Checklist** — kolaborasi pada task.
- **Notifications** — `GET /notifications` (paginate), `/unread-count`, `PUT /read-all`, `/:id/read`, `DELETE /:id`. Fan-out ke **Mongo + WebSocket live** (`notify.go` → `hub.sendToUser`). **FCM/inbox via notification-service: ditunda (TBD)**.
- **Users/departments** — dari ERP employee_db (`users_handlers.go`): `GET /users`, `GET /users/byDivision?division=`, `GET /departments` (array string). Join `system_authentication`+`personal_data`+`work_data`.
- **Audit** — `GET /tasks/:id/history` (array, per task) & `GET /audits` (`{items,total}`, scope divisi supervisor). Audit ditulis di semua mutasi task/comment/checklist/attachment (`audit.go`, `writeAudit`).

## Belum Diimplementasikan / Catatan

- **WebSocket butuh rute ingress** `/ws/task-management → service:/ws` (gateway tak proxy WS); tanpa itu realtime mati tapi app tetap jalan via polling REST. Lihat `WEBSOCKET.md`.
- **Push FCM/inbox via notification-service: TBD** (saat ini WS-only atas keputusan; BE lama punya jalur WA+FCM).
- **Role admin lintas-divisi tidak diaktifkan** — hanya `supervisor`/`staff` (di-derive dari `system_roles`).
- **Override SLA per-priority: TBD** (default response 24 jam / resolution 72 jam).
- `GET /report/sla`: `met` = selesai **tepat waktu** atas item terukur (yang sudah `responded_at`/`completed_at`); `total` = jumlah item terukur. On-time rate = met/total.
- `getAdminTaskStats` = hitungan status divisi supervisor (bentuk **FLAT** `{total,request,todo,ongoing,testing,done,ditolak}`), bukan alias `getTaskStats`.
- `filterTasks` menghormati flag `assigned_to_me`/`created_by_me`/`pending_my_approval`/`filter_by_admin_division` (search/pagination dilakukan client-side).
- Field `Space.OwnerID` ada tetapi belum dipakai.
- Branch `feat/task-management-parity` berbasis `main` lokal (tertinggal dari `origin/main`); rebase sebelum PR.

## Dependencies & Integrasi

- **Auth = SSO via API gateway** (tanpa login lokal), identitas dari header `BIP-*`. Lihat [[CORE - API Master Gateway]]. Role di-derive dari map `system_roles` (`identity.go`): **supervisor** bila supervisor/admin di divisi mana pun, selain itu **staff**. (WebSocket bypass gateway → validasi ERP JWT sendiri.)
- **MongoDB** sendiri (`task_management_db`) untuk koleksi `tasks`, `space`, `notifications`, `audits`. Lihat [[DB - Overview and Notes]].
- **ERP employee_db (read-only)** untuk nama/divisi/supervisor (`MONGO_URI_ERP`/`DB_NAME_ERP`). Lihat [[Microservices - Employee Service]].
- **file-service** untuk attachment (upload/delete/presigned via `FILE_MODULE_URL` + `MINIO_TASK_KEY`, prefix `task/`). Lihat [[Microservices - File Service]].
- **notification-service** (push FCM/inbox): **belum diintegrasikan (TBD)** — notifikasi saat ini Mongo + WebSocket. Lihat [[Microservices - Notification Service]].
- **shared-library** untuk utilitas bersama (`routes.InternalRequest*`, `common.Env/Header`, `auth`, `mongodb`).

## Dokumen Terkait

- [[APP - Dynamic Task Tracker]] — sisi FE/aplikasi task tracker.
- [[IT - Background Jobs & Schedulers]] — scheduler service ini (eskalasi SLA tiap jam)
