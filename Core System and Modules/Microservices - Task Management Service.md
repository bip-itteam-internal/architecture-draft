# Microservices - Task Management Service

## Deskripsi

*Task Management Service adalah backend **IT Helpdesk / ticketing** internal ERP yang dipadukan dengan board Kanban. Desk dimiliki dan ditangani oleh **divisi IT**, sementara **karyawan dari semua divisi dapat membuat (submit) tiket** untuk meminta bantuan/penyelesaian. Tiket ditriase oleh tim IT melalui workflow Kanban (`Request → Todo → On Going → Testing → Done`, ditambah jalur `Ditolak`). Service ini menyediakan gate approval, engine SLA dua dimensi (response + resolution) dengan scheduler eskalasi per jam, update realtime via WebSocket, push notification FCM serta inbox melalui notification-service, attachment (MinIO), comment, checklist, audit trail, dan reporting/dashboard.*

> Catatan positioning: kode saat ini masih mendukung multi-divisi (Space per divisi, supervisor per divisi; role hanya `supervisor`/`staff`). Sesuai positioning IT Helpdesk, penanganan difokuskan ke divisi IT dengan semua divisi sebagai requestor — pembatasan scope ke IT perlu dipertimbangkan di implementasi.

- **Stack:** Go + Fiber v2 + MongoDB + WebSocket + file-service (MinIO via [[Microservices - File Service]])
- **Path:** `services/task-management`
- **Status**: ⚠️ Implemented, **sudah di `main`** (diperiksa langsung ke `origin/main` 2026-08-05; catatan lama "branch `feat/task-management-parity` belum merge" sudah tidak berlaku dan branch-nya tak ada lagi). Catatan: **WebSocket butuh rute ingress** (gateway tak proxy WS), **push FCM/inbox ke notification-service ditunda** (WS-only), **role hanya `supervisor`/`staff`** (admin lintas-divisi tidak diaktifkan). Pertanyaan per tipe (`SpaceType.Fields`) ✅ **LIVE di dev & prod** dan sudah terisi untuk seluruh tipe Tech Development — lihat bagiannya di bawah.

## Endpoint / Fitur (Sudah Diimplementasikan)

### Bootstrap & Identity
- `GET /health` — health check.
- `GET /me` — identitas SSO dari header gateway (`IdentityFromHeaders`). Nomor telepon/foto diambil FE terpisah via `/api/employee/me`.

#### Cakupan divisi supervisor (`Identity.Divisions`)

Supervisor yang membawahi **lebih dari satu departemen** melihat dan menindak tiket seluruh divisi dalam cakupannya. Saat ini: **SPV Human Resource mencakup divisi General Affair** (relasi dari `master_department.supervised_by`, lihat [[HRIS - Organization Structure]]).

- Cakupan datang dari header `BIP-Supervised-Departments` (klaim JWT), **bukan** dari pengelompokan organisasi yang dipakai KPI. Bedanya menentukan: di KPI penggabungan cuma tampilan sehingga berlaku bagi semua yang sudah berhak; **di sini ia menambah WEWENANG**, jadi dibatasi pemegang `is_supervisor`.
- `scopedDivisions()` adalah satu-satunya pintu baca. Ia memberi cakupan lintas departemen **hanya** bila `isPrivileged` (admin/supervisor); selain itu, dan bila cakupan kosong (token lama), jatuh ke `BIP-Department` sehingga perilakunya sama seperti sebelum fitur ini ada.
	- Konsekuensinya: orang ber-`is_supervisor` di HRIS tapi berperan **staf** di modul tiket **tidak** mendapat divisi tambahan.
- Berlaku konsisten di **daftar tiket, laporan tim, CSAT, dan audit log**.
- **Notifikasi**: `findDivisionSupervisors` menengok departemen **induk** bila sebuah divisi tak punya atasan sendiri. Tanpa itu tiket di General Affair tak memberi tahu siapa pun, karena GA memang sengaja tanpa supervisor sendiri.
- `GET /ws` — koneksi WebSocket (auth lewat query `?token=` JWT, divalidasi sendiri). **Masuk via ingress LANGSUNG ke service (bypass gateway)** — didaftarkan sebelum `ValidateGateway`; butuh rute ingress `/ws/task-management → service:/ws` (lihat `WEBSOCKET.md`). Event: `notification` (per user), `task_update`/`space_update` (broadcast).

### Spaces (board Kanban per divisi)
- `POST /spaces` — create Space; validasi divisi harus ada di ERP, seed otomatis 5 stage + 3 priority default.
- `GET /spaces` & `GET /spaces/:id` — list dan detail Space. **Disaring hak akses** (lihat **### Kontrol akses space**).
- `PUT /spaces/:id` & `DELETE /spaces/:id` — update/delete; gated untuk admin atau supervisor divisi terkait. Stage wajib (`Request`/`Todo`/`Done`) dilindungi dari penghapusan.
- Config **automation** per-space (diterima `createSpace`/`updateSpace`): `auto_assign` (bool), `auto_close_days` (int, `0`=nonaktif) — lihat **### Automation**.
- **Tipe permintaan per-space ✅** `Space.Types []SpaceType` (`{id,name,description,color}`), diterima `createSpace`/`updateSpace` lewat field `types`. Lihat **### Tipe permintaan**.
- **Visibility ✅** `Space.Visibility` (`public` bawaan / `restricted`) + `AllowedDivisions` + `AllowedEmployees`. Lihat **### Kontrol akses space**.
- **Admin space 🟡** `Space.Admins []string` (employee_id) — orang yang ditunjuk memegang space itu. Lihat **### Admin space**.
- `GET /spaces/my-roles` 🟡 — `{admin_space_ids:[...]}` untuk pemanggil; dipakai klien memutuskan menu/tab. Didaftarkan **sebelum** `/spaces/:id`.

### Admin space 🟡

> Status: **kode selesai di branch `feat/task-space-admin`, BELUM merge dan BELUM deploy** (2026-08-06). Diverifikasi lewat HTTP di lingkungan lokal (service + Mongo lokal, header identitas dipasang seperti gateway): 20 pemeriksaan lolos, termasuk approve oleh admin space bertier staf, penolakan supervisor divisi lain, dan pencabutan yang berlaku seketika. **Belum** dijalankan lewat gateway dev/prod. Keputusannya di [[ADR - 0038 Hak Per-Objek Admin Space Task Management]].

Menjawab kalimat yang tak bisa dinyatakan model divisi: *"orang ini yang menerima permintaan di space ini"*. Wewenangnya **menempel pada objek**, bukan pada posisi seperti [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].

- Cakupannya **sebatas space itu**: triase (approve/reject), tinjauan `Testing → Done`, assign, betulkan tipe, Laporan Tim space tersebut, dan ubah pengaturan space. Di luar itu ia staf biasa.
- **Kandidatnya karyawan mana pun**, termasuk dari departemen lain. `canAccessSpace` meloloskan admin space supaya ia tak terkunci dari space `restricted` yang justru ia kelola.
- **Membuat & menghapus space tetap milik supervisor divisi/admin** — space baru belum punya admin yang bisa menunjuk dirinya, dan menghapus space menyeret seluruh riwayat tiket.
- **Disimpan di dokumen space, bukan klaim JWT** → perubahan berlaku **seketika**, tak menunggu login ulang seperti `permission_sets`/`supervised_departments` yang ikut token 72 jam.
- **Satu pintu** `canActOnSpace` (`space_admin.go`): admin space menang lebih dulu tanpa izin katalog; selain itu izin **dan** cakupan divisi harus terpenuhi bersama.
- **Gerbang rute cuma membuka pintu.** `gateOrSpaceAdmin` meloloskan pemegang izin ATAU admin di space mana pun (satu `CountDocuments` per request, hanya bagi yang tak lolos lewat izin); space tertentu diputuskan handler. Tanpa pembagian itu admin space bertier staf ditolak 403 sebelum handler melihat space tujuannya.
- ⚠️ **Menutup lubang lama**: `approveTask`/`rejectTask` **tak pernah** mengecek divisi maupun space — gerbangnya hanya izin `ticket.triage` di rute, sehingga supervisor departemen mana pun bisa menyetujui tiket departemen lain lewat API. Kini 403.
- **Daftar admin tak boleh dikosongkan oleh admin space sendiri** (400); supervisor divisi boleh. Perubahannya ditulis sebagai audit ber-`space_id` (action `space_admins`), bukan audit tugas.
- Notifikasi **aditif**: permintaan baru & eskalasi SLA response menyapa admin space **di samping** supervisor divisi.
- `Space.OwnerID` **tetap tak dipakai**: tunggal & bertipe ObjectID, sedangkan yang dibutuhkan daftar employee_id.

### Tipe permintaan
Penanda jenis permintaan yang **dipilih pemohon** saat membuat tiket (mis. Perbaikan Bug, Penambahan Fitur). Bentuknya meniru `Priority`, tapi perannya berbeda: prioritas ditetapkan **supervisor saat triase** dan menentukan target SLA resolusi, sedangkan tipe **murni penanda** untuk filter dan laporan — tidak memengaruhi SLA maupun penugasan.

- Daftarnya **per-space**; `types` kosong berarti tim itu belum memakai tipe, dan FE menyembunyikan pilihannya sama sekali. Karena itu **tidak perlu migrasi** dan rollout bisa per tim.
- Space baru **tidak** di-seed tipe default (beda dari stage & priority) — jenis pekerjaan terlalu spesifik per tim.
- `POST /tasks` menerima `type_id` dan memverifikasi tipe itu **milik space yang dipilih** (`spaceHasType`). Tanpa cek ini tugas tetap tersimpan tapi `buildPopulated` tak menemukan tipenya, sehingga tiket tampil tanpa tipe dan laporan salah hitung.
- ⚠️ `type_id` **OPSIONAL di API** sekalipun space punya daftar tipe; yang mewajibkan memilih adalah FE. Alasannya rilis: MyBharata versi lama tidak mengirim field ini, dan mewajibkannya akan membuat pemakai app lama gagal membuat tiket sampai memperbarui aplikasi.
- `PUT /tasks/:id/type` — supervisor membetulkan salah pilih (gated `PermTicketTriage` + supervisor/admin). Body kosong = mengosongkan tipe, bukan galat.
- `mergeTypes` **mempertahankan id** saat nama tipe diubah; id yang berganti akan membuat tugas lama kehilangan tipenya tanpa galat.
- Pindah space (`PUT /tasks/:id/space`) ikut mengosongkan `type_id` karena daftarnya milik space lama. **Gap:** `priority_id` punya persoalan menggantung yang sama dan sengaja belum disentuh (prioritas menentukan target SLA).

#### Pertanyaan per tipe (`SpaceType.Fields`) ✅

> Status: **merged & LIVE di dev DAN prod** per 2026-08-05 (BE PR [#989](https://github.com/bip-itteam-internal/bip-erp/pull/989), FE PR [#800](https://github.com/bip-itteam-internal/erp-frontend/pull/800)). Dev naik otomatis lewat Harness; prod di-deploy manual (`docker compose up -d --build task-management-service --no-deps`). Keduanya diverifikasi dengan **probe biner** (`grep` string khas kode baru di `/service`), bukan sekadar uptime container.
>
> **Sudah dipakai sungguhan**: seluruh **35 tipe di 9 space Tech Development** terisi **154 pertanyaan** (diverifikasi langsung ke `task_management_db` prod). Perilaku kontraknya diuji end-to-end lewat gateway dev: `fields` tersimpan, `key` diisi server, aturan absen-vs-kosong benar, dan validasi menolak `400` sambil menyebut nama tipe berikut nama pertanyaannya.
>
> ⚠️ Yang **belum** diuji formal: pengiriman tiket dari peramban sampai tampil di detail tiket. Bentuk markdown-nya dikunci test komponen, tapi tak ada catatan uji manual end-to-end.

Menjawab keluhan bahwa permintaan yang masuk ke Tech Development tak jelas isinya. Tiap tipe boleh membawa daftar pertanyaan (`Fields []TypeField`) yang harus dijawab pemohon setelah memilih tipe itu.

- **Jawabannya tidak disimpan sebagai data.** Klien merangkainya jadi markdown lalu mengirimnya sebagai `description` tugas seperti biasa. Itu keputusan sadar: kontrak `POST /tasks` tak berubah, [[APP - MyBharata]] yang tak mengenal `type_id` sama sekali tetap jalan, dan laporan tak perlu tahu fitur ini ada. Harganya, jawaban **tidak bisa difilter atau dilaporkan per pertanyaan**.
- Tipe pertanyaan: `short_text` · `long_text` · `number` · `date` · `dropdown` · `radio` · `checkbox`. Kosakatanya **meniru [[Microservices - Form Builder Service]]** alih-alih mengarang dialek kedua, dikurangi `scale`, `time`, dan `section` yang tak punya arti pada permintaan kerja.
- **Kenapa bukan memakai Form Builder Service.** Service itu punya siklus hidup sendiri (draft → published → closed), sasaran `audience`, dan menyimpan jawaban di database sendiri. Menempelkannya membuat pembuatan satu tiket bergantung pada service kedua dan jawabannya hidup di dua tempat, padahal yang diminta justru satu markdown di tiket. Yang diambil ulang hanya bentuk field dan pola validator murninya.
- Validasi dan normalisasi = **fungsi murni** (`space_type_fields.go`), teruji tanpa Mongo. Batas label dihitung **per rune**, bukan byte, supaya cocok dengan hitungan karakter di FE.
- ⚠️ **`fields` absen ≠ `fields` kosong.** Absen berarti "jangan diubah", array kosong berarti "hapus semua". Tanpa pembedaan ini satu build FE lama yang mengirim ulang daftar tipe tanpa `fields` akan menghapus seluruh pertanyaan tanpa galat apa pun. Diuji di kedua sisi.
- ⚠️ Penegakan "wajib dijawab" **hanya di FE web**. `type_id` sendiri sudah opsional di API demi klien mobile lama, jadi API dan MyBharata tetap bisa mengirim deskripsi bebas.
- ⚠️ `PUT /tasks/:id/type` (supervisor membetulkan tipe) **tidak menulis ulang** deskripsi yang terlanjur tersusun dari tipe lama.

### Kontrol akses space
Space bisa disetel terbuka untuk semua karyawan (`public`, bawaan) atau dibatasi ke departemen/orang tertentu (`restricted`).

- `canAccessSpace(id, sp)` digerbang di **tiga tempat**: `GET /spaces` (menyaring daftar), `GET /spaces/:id` (403), dan `POST /tasks` (403). Menyaring daftar saja tidak cukup — gateway meneruskan permintaan apa adanya, jadi siapa pun bisa mengirim `space_id` langsung ke endpoint create (lihat [[CORE - API Master Gateway]]).
- **Tim pemilik tak pernah terkunci**: supervisor divisi space, admin, **admin space** (🟡, lihat bagiannya), dan anggota space (`members`) selalu lolos lebih dulu. Tanpa itu salah isi daftar izin membuat space jadi yatim dan tak bisa diperbaiki siapa pun.
- Nilai `visibility` asing **ditolak saat menulis** (`normalizeVisibility`). Bila boleh tersimpan, pembacaan akan menganggapnya publik dan space yang dikira terbatas diam-diam terbuka.
- ⚠️ Space lama tak punya field ini di Mongo, sehingga API mengirim `"visibility": ""` (string kosong, **bukan** null). Klien wajib memperlakukan kosong sebagai `public`; `?? "public"` di TypeScript **tidak cukup** karena hanya menangkap null/undefined.
- Gerbang ini mengatur **siapa boleh mengajukan**, bukan visibilitas tiket yang sudah dibuat.

### Tasks
- `POST /tasks` — create task (status awal `Request`, set `response_due_at = now + 24h`).
- `GET /tasks/:id` — detail task (populated).
- `GET /tasks/filter` — list dengan RBAC + filter (`space_id`, `status`, `assigned_to_me`, `created_by_me`, `pending_my_approval`, dll), search, dan pagination.
- `GET /tasks/counts` — jumlah tiket **aktif** per-scope (`created`/`assigned`/`team`) untuk badge tab. Scope divisi mengecualikan status `Request`/`Ditolak`; `team` hanya dihitung untuk supervisor/admin (0 selain itu).
- `PUT /tasks/:id/status` — ubah status (set `completed_at` saat mencapai `Done`).
- `PUT /tasks/:id/assign`, `/archive`, `/unarchive`, `/due-date`, `/priority`, `/space`, `/type` — mutasi atribut task. `/type` digerbang izin triase (bukan `staffOrSup` seperti `/priority`) dan memverifikasi tipe milik space tugas tersebut.
- `GET /tasks/:id/history` — riwayat perubahan task.
- `DELETE /tasks/:id` — hapus task.

### Approval
- `POST /tasks/:id/approve` — approve task. Untuk transisi `Request → Todo` **wajib `priority_id`** (`400` bila kosong/invalid); `due_date` **opsional** — bila kosong diisi otomatis `now + target resolusi prioritas` (`resolution_hours`, fallback 72 jam); `start_date` opsional. Stamp `responded_at` (menghentikan SLA response clock). Untuk `Testing → Done` stamp `completed_at`.
- `POST /tasks/:id/reject` — tolak task (status `Ditolak`).

### Lifecycle: Hold / Reopen
- `POST /tasks/:id/hold` — **tahan** tiket (guard `staffOrSup` + `canHold`: hanya tiket non-terminal & belum di-hold). Set `on_hold=true`, `held_at`, `hold_reason` (opsional dari body). Selama hold, SLA masuk state **`held`** (jam SLA dijeda).
- `POST /tasks/:id/unhold` — **lepas** hold (guard `staffOrSup` + `canUnhold`). Hitung durasi hold `now − held_at`, akumulasi ke `hold_accum_ms`; **geser** `response_due_at`/`due_date` sebesar durasi tsb (hanya bila belum `responded_at`/`completed_at`), lalu clear `on_hold`/`held_at`.
- `POST /tasks/:id/reopen` — **buka kembali** tiket dari status terminal (`Done`/`Selesai` atau ter-`is_archived`) ke **langkah kerja pertama** space (guard `staffOrSup`; **pemohon juga boleh** — dicek di handler via `isCreator`). Reset SLA resolusi: `due_date = now + target resolusi prioritas` (`resolutionHoursOf`, fallback 72 jam), `is_archived=false`, unset `completed_at` & `csat`, `reopen_count++`, stamp `reopened_at`.

### CSAT (Kepuasan Requester)
- `POST /tasks/:id/csat` — requester memberi rating **1–5 bintang** + komentar (guard `staffOrSup`; **requester-only** dicek di handler via `canSubmitCSAT`). Validasi (`csat.go`): rating 1–5, **komentar wajib bila rating ≤ 2** (`400`); hanya untuk tiket **berstatus `Done`, `completed_at != nil`, non-arsip** (`403` bukan pemohon / `409` belum selesai). Idempotent overwrite; disimpan embedded `csat{rating,comment,rated_at,rated_by}` pada task; audit + broadcast `task_update`.
- **Notif** `task_resolved_rate_me` ke requester saat tiket → `Done` (di 3 situs transisi `updateTaskStatus`/`updateTask`/`approveTask`; guard `status != "Done"` cegah dobel; reopen→Done kirim lagi).
- **Reopen** membersihkan `csat` (`$unset`) → siklus resolusi baru, requester menilai ulang. (PR #343 BE, #233 Web.)
- `GET /tasks/pending-csat` — tiket pemanggil yang **sudah selesai tapi belum dinilai** (`{data, total}`, terbaru dulu, maks 20). Dipakai pengingat di beranda [[APP - MyBharata]]. **Sengaja rute tersendiri, bukan ditambahkan ke `/tasks/counts`**: tiga hitungan di sana menyaring tiket AKTIF (`status $nin [Done, Ditolak]`), jadi tiket yang menunggu penilaian tak pernah masuk hitungan mana pun sebelum rute ini ada — dan menaruh keduanya bersebelahan membuat pembaca wajar mengira keempat angka itu sejenis. Aturannya **diturunkan dari `canSubmitCSAT`**, bukan ditulis ulang; kalau keduanya berbeda, klien akan menawarkan tiket yang justru ditolak server saat rating dikirim. Filter Mongo dan penilai in-memory dipakai berdampingan, yang kedua sebagai jaring pengaman untuk dokumen lama yang bentuknya tak tertangkap filter. (PR [#872](https://github.com/bip-itteam-internal/bip-erp/pull/872); **sudah jalan di prod sejak 2026-08-01**, health `200` lewat gateway.)

### Automation (auto-assign & auto-close)
Konfigurasi **per-space** (`Space.auto_assign` bool, `auto_close_days` int `0`=nonaktif, `auto_assign_cursor` internal `json:"-"`).
- **Auto-assign round-robin** (`approveTask`, transisi `Request→Todo`): bila body `assign_to` kosong **dan** `space.auto_assign` **dan** `len(members)>0` → pilih anggota bergiliran via `nextRoundRobin(members, cursor)` (cursor ter-bound `[0,n)`, disimpan di space). Assignee **manual selalu menang**; assignee hasil auto ikut dinotifikasi. Members kosong → tak meng-assign (perilaku approve lama).
- **Auto-close** (`sla_scheduler.go` `runAutoClose()`, per-jam bersama eskalasi SLA): untuk space `auto_close_days>0`, arsip tiket `status=="Done"` non-arsip yang `completed_at` sudah lewat ambang (`shouldAutoClose`) → `is_archived=true` + audit + **notif requester** `task_auto_closed`. Idempoten (ter-arsip → keluar dari query). Tiket ter-auto-close tetap bisa **reopen**. (PR #352 BE, #236 Web.)

### SLA Engine (dua dimensi)
- **Response:** `response_due_at` vs `responded_at` (field diset saat create/approve). **Resolution:** `due_date` vs `completed_at`.
- State (dihitung di `sla.go`, disertakan pada task populated `sla.response/resolution.{due_at,state}`): `none` / `on_track` / `warning` / `breached` / `met` / **`held`** (saat tiket di-hold); `warning` aktif di 80% window.
- Default: response **24 jam** (diset saat create), resolution **72 jam** (referensi resolution: `start_date`/`responded_at`/`created_at` → `due_date`). **Override resolution per-priority ✅**: tiap `Priority` punya `resolution_hours` (per-space, satuan jam) → dipakai `resolutionHoursOf(space, priority_id)` saat approve (default `due_date`) & reopen; fallback 72 jam bila `resolution_hours ≤ 0` / prioritas tak ada. (Response tetap 24 jam, bukan per-priority.)
- Scheduler eskalasi (`sla_scheduler.go`): goroutine per jam, mengirim notifikasi **breach sekali** per task (ditandai array `sla_notified`): response breach → **supervisor divisi**; resolution breach → **assignee + supervisor**. (Warning hanya untuk badge, belum dieskalasi via notifikasi.)

### Reports / Dashboard
Semua reuse `reportBaseFilter` (scope: supervisor→space divisinya, admin→semua, staff→task sendiri) + `parseReportRange` (default 30 hari; `start_date`/`end_date`). Dikonsumsi halaman **Laporan Tim** supervisor di [[APP - Web ERP]].
- `GET /tasks/stats` — statistik status task (scope role). `GET /tasks/admin-stats` — status divisi supervisor **FLAT**, kini + `reopened` & `reopen_rate` (persen 0–100, `reopened/total`).
- `GET /report/summary-by-department` — ringkasan per space × status.
- `GET /report/timeline` — timeline harian (total + per status).
- `GET /report/manpower-performance` — performa per anggota: `total`, `done`, kini + `avg_response_hours`, `avg_resolution_hours` (rata-rata jam atas task yang punya `responded_at`/`completed_at`), `reopened` (jumlah task `reopen_count>0`). Agregasi in-memory via `accumulateManpower` (pure, tertes).
- `GET /report/sla` — rate on-time response & resolution (overall + per divisi, dengan rentang tanggal).
- `GET /report/sla-breaches` — **daftar tiket yang lewat SLA** (bukan agregat): reuse `computeSLA` → satu baris per dimensi `breached` (response/resolution), tiket `on_hold` (state `held`) tak dihitung; field `{ticket_id,keluhan,space_name,assignee_name,priority,breach_type,overdue_hours,status}`. Untuk ditindaklanjuti supervisor.
- `GET /report/csat` — agregat CSAT **flat** `{average, top2box_pct (bintang 4–5), count, distribution[1..5]}`; rentang tanggal (`csat.rated_at`) + scope role meniru `/report/sla`.

### Lain-lain
- **Attachments** — lewat **[[Microservices - File Service]]** (bukan MinIO langsung; prefix object `task/`, key `MINIO_TASK_KEY`), bukan temp-upload (FE create-task-lalu-upload). Endpoint (`attachment_handlers.go`, `fileclient.go`):
	- `POST /tasks/:id/attachments` — multipart field `file` (satu file/request) → upload ke file-service → simpan `FileAttachment{type:"file"}` di task; respons `{attachment}`. **Batas 4 MB/file** (dari file-service; BE lama dulu 25 MB) → map ke `413`.
	- `POST /tasks/:id/links` — body `{name,url}` → `FileAttachment{type:"link"}`; respons `{link}`.
	- `DELETE /tasks/:id/attachments/:attachmentId` — hapus object di file-service (bila file) + `$pull`; lampiran milik requestor tak bisa dihapus assignee.
	- `GET /tasks/:id/attachments/:fileId/preview` — respons `{url}` = presigned GET (public base MinIO, ~300s); untuk link kembalikan URL apa adanya.
- **Comments** & **Checklist** — kolaborasi pada task. **Izin ubah checklist** (tambah/centang/hapus item) di-gate `canHandleTask` = **privileged (admin/supervisor) ATAU assignee**; **pembuat/pemohon TIDAK boleh** (read-only) — beda dari `canEditTask` yang masih memasukkan creator. Checklist **dibuat lewat web** ([[APP - Web ERP]]); mobile ([[APP - MyBharata]]) hanya bisa mencentang.
- **Notifications** — `GET /notifications` (paginate), `/unread-count`, `PUT /read-all`, `/:id/read`, `DELETE /:id`. Fan-out ke **Mongo + WebSocket live** (`notify.go` → `hub.sendToUser`). **FCM/inbox via notification-service: ditunda (TBD)**.
- **Users/departments** — dari ERP employee_db (`users_handlers.go`): `GET /users`, `GET /users/byDivision?division=`, `GET /departments` (array string). Join `system_authentication`+`personal_data`+`work_data`.
- **Audit** — `GET /tasks/:id/history` (array, per task) & `GET /audits` (`{items,total}`, scope divisi supervisor). Audit ditulis di semua mutasi task/comment/checklist/attachment (`audit.go`, `writeAudit`).

## Belum Diimplementasikan / Catatan

- **WebSocket butuh rute ingress** `/ws/task-management → service:/ws` (gateway tak proxy WS); tanpa itu realtime mati tapi app tetap jalan via polling REST. Lihat `WEBSOCKET.md`.
- **Push FCM/inbox via notification-service: TBD** (saat ini WS-only atas keputusan; BE lama punya jalur WA+FCM).
- **Role admin lintas-divisi tidak diaktifkan** — hanya `supervisor`/`staff` (di-derive dari `system_roles`). Wewenang per-space kini ditempuh lewat **admin space** (🟡, belum merge), bukan dengan menaikkan tier.
- **Admin space belum dijalankan lewat gateway** (dev maupun prod): verifikasinya baru di lingkungan lokal. Selama itu belum terjadi, fitur ini tidak boleh dianggap hidup.
- **Belum ada layar "siapa memegang space mana"** lintas space, dan belum ada batas jumlah admin per space (sepuluh admin berarti sepuluh penerima tiap notifikasi permintaan baru).
- **Deteksi supervisor divisi utk notifikasi** (`findDivisionSupervisors`) memakai `work_data` ERP (flag `is_supervisor`, fallback jabatan regex `Supervisor|^Leader$`), **bukan** `system_roles` (key `system_roles` = kode modul spt "it"/"finance", tak pernah cocok dgn nama departemen). Hanya akun aktif.
- Notif **"Permintaan baru"** (`NotifTaskRequest`, ke supervisor divisi + admin saat tiket dibuat) menyertakan arahan **buka website ERP** — sebab **approve/reject hanya tersedia di web**; mobile ([[APP - MyBharata]]) belum punya alur approval.
- **Override SLA resolution per-priority ✅ implemented** (`Priority.resolution_hours` per-space, fallback 72 jam; approve auto-`due_date` + reopen; PR #337). Override **response** per-priority tetap TBD (response fix 24 jam).
- `GET /report/sla`: `met` = selesai **tepat waktu** atas item terukur (yang sudah `responded_at`/`completed_at`); `total` = jumlah item terukur. On-time rate = met/total.
- `getAdminTaskStats` = hitungan status divisi supervisor (bentuk **FLAT** `{total,request,todo,ongoing,testing,done,ditolak}` + `reopened`,`reopen_rate`), bukan alias `getTaskStats`.
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
- [[ADR - 0038 Hak Per-Objek Admin Space Task Management]] — keputusan admin per space (menyimpang dari [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]])
