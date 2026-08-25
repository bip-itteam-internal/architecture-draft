## Deskripsi

*Endpoint **task-management-service** (task & space ala Kanban; kini diposisikan ticketing/helpdesk). Gateway: `/api/task-management/*` (WebSocket via ingress langsung ke service). RBAC `staff`/`supervisor` di-derive dari map `system_roles`. Grounded ke `services/task-management/routes.go` + `main.go` di `origin/main`.*

- **Implementasi**: [[Microservices - Task Management Service]] · **Status**: ⚠️ (di `main`; WS butuh rute ingress; **admin space** merged 2026-08-06 tapi belum diuji lewat gateway)
- **Indeks**: [[API - Index]]
- > Catatan: attachment (via file-service), reports/stats, history/audit, users/departments, WebSocket, dan SLA — yang dulu dicatat sebagai isi branch `feat/task-management-parity` — **sudah ada di `main`** (diperiksa langsung ke `origin/main` 2026-08-05). Branch itu sendiri tak ada lagi.

## Sistem
| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` · `/me` | Health / identitas user |

## Spaces
| Method | Path | Fungsi |
|---|---|---|
| POST/GET | `/spaces` · `/spaces/:id` | Buat/list/detail space (`?division=`). Body/response bawa `types` (tipe permintaan) + `visibility`/`allowed_divisions`/`allowed_employees` + `admins`. **Disaring hak akses**: space `restricted` hilang dari list dan `403` di detail, kecuali supervisor divisinya, admin, admin space, anggota space, atau yang ada di daftar izin |
| PUT | `/spaces/:id` | Update space. `visibility` hanya menerima `public`/`restricted` (nilai lain `400`). Boleh dilakukan supervisor divisi, admin, ATAU **admin space**. `admins` kosong yang dikirim admin space sendiri → `400` |
| DELETE | `/spaces/:id` | Hapus space — tetap **hanya** supervisor divisi & admin |
| GET | `/spaces/my-roles` | `{admin_space_ids:[...]}` space yang dipegang pemanggil sebagai admin. Rute kecil tersendiri supaya sidebar tak memuat seluruh `/spaces`. **Didaftarkan sebelum `/spaces/:id`** |

### `admins` — admin per space ✅

> Status: **MERGED ke `main` 2026-08-06 pukul 10:14 WIB** (PR [#1027](https://github.com/bip-itteam-internal/bip-erp/pull/1027) + FE [#818](https://github.com/bip-itteam-internal/erp-frontend/pull/818)); branch `feat/task-space-admin` sudah tidak ada. ⚠️ **Belum diuji lewat gateway** dev maupun prod, dan prod belum di-deploy. Keputusannya di [[ADR - 0038 Hak Per-Objek Admin Space Task Management]].

Daftar `employee_id` yang ditunjuk memegang space: menerima permintaan masuk, meninjau,
menugaskan, melihat Laporan Tim space itu, dan mengubah pengaturannya — **sebatas space
tersebut**, walau tier-nya `staff` dan walau ia dari departemen lain.

- Absen/kosong = perilaku lama persis (hanya supervisor divisi & admin), jadi **tanpa migrasi**.
- Jangan tertukar dengan `members` (tim penangan, sasaran auto-assign), yang **bukan** pemegang wewenang.
- Perubahannya tercatat sebagai audit ber-`space_id` dengan action `space_admins` di `GET /audits`.
- Berlaku **seketika** karena tersimpan di dokumen space, bukan di klaim JWT.

### `types[].fields` — pertanyaan per tipe permintaan ✅

> Status: **merged & LIVE di dev DAN prod** per 2026-08-05 (PR [#989](https://github.com/bip-itteam-internal/bip-erp/pull/989)). Kontraknya diuji end-to-end lewat gateway dev, dan sudah dipakai sungguhan di prod: 35 tipe pada 9 space Tech Development terisi 154 pertanyaan.

Tiap `SpaceType` boleh membawa `fields`, yaitu pertanyaan yang harus dijawab pemohon
setelah memilih tipe itu. **Jawabannya tidak pernah dikirim sebagai data**: klien
merangkainya jadi markdown dan mengirimnya lewat `description` pada `POST /tasks` seperti
biasa, sehingga kontrak tugas, notifikasi, laporan, dan [[APP - MyBharata]] tak berubah
sama sekali.

```jsonc
"types": [{
  "id": "...", "name": "Perbaikan Bug", "description": "", "color": "#FF0000",
  "fields": [
    { "key": "gejala", "label": "Apa yang terjadi?", "type": "long_text",
      "hint": "", "required": true },
    { "key": "sejak", "label": "Sejak kapan?", "type": "radio",
      "required": false, "options": ["Baru saja", "Beberapa hari"] }
  ]
}]
```

- `type` ∈ `short_text` · `long_text` · `number` · `date` · `dropdown` · `radio` ·
  `checkbox` — kosakata sama dengan [[API - Form Builder Service]] **dikurangi** `scale`,
  `time`, dan `section` yang tak punya arti pada permintaan kerja.
- `key` **diisi server** bila kosong, dan tak pernah ditulis ulang bila sudah ada.
- Validasi `400` menyebut nama tipe yang bermasalah: label kosong atau >200 **karakter**
  (dihitung per rune, bukan byte), tipe pertanyaan asing, tipe pilihan tanpa opsi terisi,
  opsi kembar, opsi menempel di tipe bukan-pilihan, maksimal 20 pertanyaan dan 15 opsi.
- ⚠️ **`fields` yang ABSEN berarti "jangan diubah"; array kosong yang dikirim eksplisit
  berarti "hapus semua".** Pembedaan ini yang menjaga klien lama: setiap bagian Kelola
  Space mengirim ulang seluruh daftar tipe, dan tanpa aturan ini satu build FE yang belum
  mengenal `fields` akan menghapus seluruh pertanyaan tanpa satu pun galat muncul.
- ⚠️ Tipe yang belum pernah punya pertanyaan mengembalikan `"fields": null` (bukan `[]`),
  karena Mongo tak menyimpan kunci itu. Klien wajib membacanya lewat fallback.

## Tasks
| Method | Path | Fungsi |
|---|---|---|
| POST | `/tasks` | Buat task (set `response_due_at`+24h, notif supervisor). Wajib: `requestor_name` (≥2), `requestor_division`, `phone` (≥10), `keluhan`, `description`, `space_id` — tapi **`requestor_name` & `phone` diisi server bila klien tak mengirimnya** (lihat di bawah). `type_id` **opsional** (klien lama tak mengirimnya) tapi bila diisi **wajib milik space** yang dipilih, kalau tidak `400`. Space `restricted` yang tak boleh diakses → `403` |
| GET | `/tasks/filter` · `/tasks/:id` | Filter (flag `assigned_to_me`/`created_by_me`/`pending_my_approval`/`filter_by_admin_division`) / detail (populated + `sla`) |
| GET | `/tasks/stats` · `/tasks/admin-stats` | Statistik status FLAT (rentang tanggal) |
| GET | `/tasks/counts` | Jumlah tiket **AKTIF** per scope (`created`/`assigned`/`team`) untuk badge tab |
| GET | `/tasks/pending-csat` | Tiket pemanggil yang **sudah selesai tapi belum dinilai** (`{data, total}`, terbaru dulu, maks 20) |
| POST | `/tasks/:id/csat` | Pemohon memberi rating 1..5 (komentar wajib bila ≤2); idempotent overwrite |
| PUT | `/tasks/:id` | Edit generik (partial) |
| PUT | `/tasks/:id/status` · `/archive` · `/unarchive` · `/due-date` · `/priority` · `/space` | Ubah status/arsip/jadwal/prioritas/pindah. `/space` ikut mengosongkan `type_id` (daftar tipe milik space lama) |
| PUT | `/tasks/:id/type` | Supervisor membetulkan tipe (gated izin triase). `type_id` wajib milik space tugas tsb; body kosong = kosongkan tipe |
| PUT/POST | `/tasks/:id/assign` · `/approve` · `/reject` | Assign/approve (body `start_date/due_date/priority_id/assign_to`)/reject. Boleh supervisor divisi space, admin, ATAU **admin space**. Supervisor divisi LAIN kini `403` — sebelumnya lolos karena ketiga rute ini tak pernah mengecek space sama sekali |
| GET | `/tasks/:id/history` | Riwayat perubahan (array) |
| DELETE | `/tasks/:id` | Hapus task (supervisor) |

### Identitas pemohon pada `POST /tasks` ✅

> Status: **merged 2026-08-22** (branch `feat/task-management-identitas-pemohon` + [[APP - MyBharata]] `feat/task-create-identitas-pemohon`). ⚠️ **Belum diuji lewat gateway** dan belum di-deploy ke dev maupun prod.

`requestor_name` dan `phone` tetap **wajib**, tetapi server mengisinya lebih dulu bila klien
mengirimnya kosong, **sebelum** validasi berjalan:

- `requestor_name` ← header `BIP-Fullname` (klaim JWT, selalu dipasang gateway lewat `routes.Reroute`).
- `phone` ← `personal_data.phone_number` milik pemanggil, lewat koneksi read-only ke `employee_db`.

**Nilai kiriman klien tak pernah ditimpa.** Server hanya mengisi kekosongan, karena web
memungkinkan seseorang melaporkan atas nama orang lain; menimpanya akan mengubah data yang
sengaja diisi tanpa satu pun pesan. Jejak pembuat sebenarnya tetap di `created_by`, yang
memang selalu dari header.

**Kenapa ini ada.** Kedua field itu tak punya kolom sama sekali di form MyBharata; nilainya
dirakit dari profil yang belum tentu termuat. Ketika kosong, pemohon ditolak `400` **tanpa
ada apa pun di layar yang bisa ia perbaiki**. Terekam di prod 2026-08-21 lewat `/log/fiber`
di dalam container: empat `POST /tasks` dibalas `400` berturut-turut lalu `201` delapan menit
kemudian. Pengisian di server inilah yang menutup MyBharata versi lama yang sudah beredar,
karena aplikasi mobile tak bisa dipaksa update.

⚠️ **Balasan `400` memuat `errors` per-kolom** (`{"success":false,"error":"Validation
failed","errors":{"phone":"phone min 10 chars"}}`), dan selama ini **tak satu pun klien
membacanya**. Bentuk ini hanya dipakai `POST /tasks`, jadi klien yang mau menampilkannya
harus membacanya sendiri di datasource-nya; jangan berharap lapisan HTTP bersama yang
melakukannya.

> **`/tasks/pending-csat` sengaja terpisah dari `/tasks/counts`.** Tiga hitungan di `counts` menyaring tiket AKTIF (`status $nin [Done, Ditolak]`), sedangkan tiket yang menunggu penilaian justru sudah selesai — jadi ia tak pernah masuk hitungan mana pun sebelum rute ini ada. Aturan "menunggu penilaian" diturunkan dari `canSubmitCSAT`, bukan ditulis ulang: kalau keduanya berbeda, klien akan menawarkan tiket yang justru ditolak server saat rating dikirim.

## Attachments (via file-service)
| Method | Path | Fungsi |
|---|---|---|
| POST | `/tasks/:id/attachments` · `/tasks/:id/links` | Upload file (field `file`, resp `{attachment}`) / tambah link (resp `{link}`) |
| GET | `/tasks/:id/attachments/:fileId/preview` | Presigned URL preview (`{url}`) |
| DELETE | `/tasks/:id/attachments/:attachmentId` | Hapus lampiran |

## Reports & Users
| Method | Path | Fungsi |
|---|---|---|
| GET | `/report/summary-by-department` · `/report/timeline` · `/report/manpower-performance` · `/report/sla` | Ringkasan per space × status / timeline harian / performa per anggota / on-time rate response & resolution |
| GET | `/report/sla-breaches` | **Daftar** tiket yang lewat SLA (bukan agregat), satu baris per dimensi `breached`; tiket `on_hold` tak dihitung. Field `{ticket_id,keluhan,space_name,assignee_name,priority,breach_type,overdue_hours,status}` |
| GET | `/report/csat` | Agregat CSAT flat `{average, top2box_pct, count, distribution[1..5]}`, skala **1–5 bintang**. Rentangnya atas `csat.rated_at`, bukan `createdAt` |
| GET | `/users` · `/users/byDivision` · `/departments` | Dropdown assignee & divisi (dari ERP) |
| GET | `/audits` | Audit trail lintas-task (`{items,total}`). Scope: admin→semua, supervisor→divisinya, **admin space**→space yang ia pegang. Memuat juga audit yang menempel pada SPACE (`space_admins`) yang tak punya `task_id` |

> **Seluruh rute `/report/*` (dan `/tasks/admin-stats`) digerbang `reportGate = gateOrSpaceAdmin(ticket.report.team, "supervisor", "admin")`, dan cakupannya satu aturan bersama**: admin→semua divisi; supervisor→space divisinya ditambah space yang ia pegang; admin space bertier staf→space yang ia pegang ditambah tugasnya sendiri; sisanya→tugasnya sendiri. Parameternya **hanya** `start_date`/`end_date` (default 30 hari terakhir); **tidak ada penyaring `space_id`**, sehingga angka SLA dan CSAT selalu gabungan seluruh space dalam cakupan pemanggil.

## KPI (panggilan mesin)

| Method | Path | Fungsi |
|---|---|---|
| GET | `/kpi/ticket` ✅ | Agregat tiket **satu orang** satu periode untuk penilaian KPI. Query wajib `employee_id`·`periode=YYYY-MM`·`key`. Balasan `{ditugaskan, selesai, sla_terukur, selisih_jam[], csat_rating[]}`. Live di prod sejak 6 Agustus 2026 ([#1055](https://github.com/bip-itteam-internal/bip-erp/pull/1055)); penanda "belum merge" di versi lama dok ini sudah usang |
| GET | `/kpi/space-group` ⚠️ | Agregat tiket **satu kelompok space** satu periode, untuk metrik KPI Leader. Query wajib `division`·`group`·`periode=YYYY-MM`·`key`. Balasan sama dengan `/kpi/ticket` ditambah `{division, group, spaces}`. Merged [#1427](https://github.com/bip-itteam-internal/bip-erp/pull/1427)+[#1428](https://github.com/bip-itteam-internal/bip-erp/pull/1428) 2026-08-25, **belum terverifikasi lewat gateway** |

> **Kenapa tidak memakai `/report/*` yang angkanya bertetangga.** Rute laporan digerbang izin PEMANGGIL dan cakupannya mengikuti siapa yang memanggil; ia menjawab *"apa yang boleh dilihat orang ini"*. Yang dibutuhkan employee-service pertanyaan lain, *"berapa angka si A pada Juli"*, tanpa membawa identitas pemakai sama sekali. Memaksakan satu rute untuk dua pertanyaan berarti salah satunya harus melonggarkan gerbangnya.

> ⛔ **`/kpi/space-group` TIDAK dapat diturunkan dari `/kpi/ticket`.** Menjumlahkan angka per anggota membuang tiket yang **belum ditugaskan kepada siapa pun** dan tiket yang dipegang **akun non-aktif**, padahal keduanya justru yang paling perlu terlihat oleh Leader. Diukur di produksi Juli 2026 untuk space pengembangan: **14 tiket tanpa assignee** dan **24 tiket dipegang akun non-aktif**. Dengan cakupan `team`, penyebutnya menyusut dan angka Leader **membaik persis ketika timnya menelantarkan tiket** — tanpa galat dan tanpa gejala. Karena itu ruang lingkupnya daftar **space**, bukan daftar orang.
>
> Ruang lingkup itu diturunkan dari DATA: `space.division` menyebut departemen pemiliknya dan **`space.kpi_group`** (`support` / `development` / kosong) memisahkan pekerjaan dukungan dari pengembangan di dalam satu divisi. Space baru cukup ditandai lewat layar, tanpa deploy dan tanpa daftar id di kode. Kosakatanya **tetap**, supaya katalog metrik KPI bisa statis dan salah ketik ketahuan saat memilih.
>
> **Divisi yang belum satu pun space-nya bergrup dijawab `409`, bukan `200` berisi nol.** Nol tiket terbaca sebagai "timnya tidak mengerjakan apa pun" dan nilainya tampak sah, sehingga kesalahan pengisian berubah jadi skor buruk seseorang tanpa satu pun gejala. Pesannya menyebut berapa space yang belum diisi **dan di layar mana mengisinya** (Manajemen Tugas › Kelola Space › Ubah › Kelompok KPI), karena yang membacanya berdiri di layar KPI sedangkan sebabnya ada di modul lain. Konsumennya, sumber `kinerja_tiket_divisi` di [[Microservices - Employee Service]], meneruskan badan galat itu apa adanya ke `auto_basis`.

Gerbangnya **kunci layanan sendiri** (`TASK_MANAGEMENT_SERVICE_KEY` lewat query `key`), bukan `INTERNAL_GATEWAY_KEY` yang dipasang gateway untuk setiap permintaan ber-JWT ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). **Kunci yang belum dikonfigurasi MENUTUP rute**, supaya env yang lupa dipasang tidak berubah jadi pintu terbuka. Polanya menyalin `/kpi/uptime` [[Microservices - Monitoring Service]] dan `/kpi/kinerja-toko` [[Microservices - Marketing Analytics Service]].

Aturan isi muatannya, semuanya supaya sumber tidak diam-diam menilai:

- **Tanpa angka target.** Rute ini melapor apa yang terukur dan berapa yang seharusnya terukur; target, bobot, ambang, dan arah diisi HR lewat `POST /kpi/templates`.
- **`selisih_jam` dikirim per tiket**, bukan sudah dirata-rata, karena reduksi `rasio_ambang` di employee-service yang berhak mencacahnya. **Positif berarti tepat waktu.**
- **`sla_terukur` dipisah dari `selesai`.** Tiket tanpa tenggat tak dapat dinilai ketepatan waktunya, dan itu bukan kesalahan penangannya; bedanya menjadi cakupan.
- **Muatan sempit**: tanpa judul tiket, nama space, maupun nama orang. Keluhan pemakai memuat isi pekerjaan; penilaian hanya butuh cacahan.
- ⚠️ **Selesai BUKAN berarti `status == "Done"`.** Stage terakhir dinamai per-space, dan `isTerminalStatus` mengenali `Done`, `Selesai`, serta `Archive`. Tiga space Tech Development memakai `Archive`; menghitung `Done` saja membuang 18 tiket ber-assignee di produksi, 5 di antaranya membawa rating CSAT alias 29% dari seluruh rating yang pernah masuk.
- Tiket **`Ditolak` tidak masuk penyebut** sama sekali: permintaan yang batal dikerjakan, bukan pekerjaan yang gagal diselesaikan.
- Tiket **arsip TETAP dihitung**, beda dari `reportBaseFilter`. Tiket yang selesai lalu diarsipkan auto-close tetap pekerjaan orang itu.

Seluruh aturan di atas berlaku **sama persis** untuk kedua rute, dan itu dijaga kode: `ringkasTiketKPI` (per orang) dan `ringkasTiketGrup` (per kelompok) memanggil satu fungsi `ringkasTiket(tugas, ikut)` yang membedakan keduanya **hanya** lewat predikat siapa yang ikut dihitung. Menyalin badan fungsinya akan melahirkan dua definisi "selesai" yang pasti menyimpang, dan penyimpangannya tak pernah muncul sebagai galat — hanya sebagai dua angka yang berbeda untuk pertanyaan yang sama.

## WebSocket
| Path | Fungsi |
|---|---|
| `GET /ws?token=<JWT>` | Realtime (bypass gateway, via ingress). Event: `notification`/`task_update`/`space_update` |

## Comments · Checklist · Notifications
| Method | Path | Fungsi |
|---|---|---|
| POST/PUT/DELETE | `/tasks/:id/comments` · `/tasks/:taskId/comments/:commentId` | Komentar |
| POST/PUT/DELETE | `/tasks/:id/checklist` · `/tasks/:taskId/checklist/:itemId[/toggle]` | Checklist |
| GET/PUT/DELETE | `/notifications` · `/notifications/unread-count` · `/read-all` · `/:id/read` · `/:id` | Notifikasi |

## Dokumen Terkait
- [[Microservices - Task Management Service]] · [[APP - Dynamic Task Tracker]] · [[API - Index]] · [[ADR - 0038 Hak Per-Objek Admin Space Task Management]]
