## Deskripsi

*Endpoint **task-management-service** (task & space ala Kanban; kini diposisikan ticketing/helpdesk). Gateway: `/api/task-management/*` (WebSocket via ingress langsung ke service). RBAC `staff`/`supervisor` di-derive dari map `system_roles`. Grounded ke `services/task-management/routes.go` + `main.go` di `origin/main`.*

- **Implementasi**: [[Microservices - Task Management Service]] · **Status**: ⚠️ (di `main`; WS butuh rute ingress)
- **Indeks**: [[API - Index]]
- > Catatan: attachment (via file-service), reports/stats, history/audit, users/departments, WebSocket, dan SLA — yang dulu dicatat sebagai isi branch `feat/task-management-parity` — **sudah ada di `main`** (diperiksa langsung ke `origin/main` 2026-08-05). Branch itu sendiri tak ada lagi.

## Sistem
| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` · `/me` | Health / identitas user |

## Spaces
| Method | Path | Fungsi |
|---|---|---|
| POST/GET | `/spaces` · `/spaces/:id` | Buat/list/detail space (`?division=`). Body/response bawa `types` (tipe permintaan) + `visibility`/`allowed_divisions`/`allowed_employees` + `admins` (🟡). **Disaring hak akses**: space `restricted` hilang dari list dan `403` di detail, kecuali supervisor divisinya, admin, admin space, anggota space, atau yang ada di daftar izin |
| PUT | `/spaces/:id` | Update space. `visibility` hanya menerima `public`/`restricted` (nilai lain `400`). Boleh dilakukan supervisor divisi, admin, ATAU **admin space** (🟡). `admins` kosong yang dikirim admin space sendiri → `400` |
| DELETE | `/spaces/:id` | Hapus space — tetap **hanya** supervisor divisi & admin |
| GET | `/spaces/my-roles` 🟡 | `{admin_space_ids:[...]}` space yang dipegang pemanggil sebagai admin. Rute kecil tersendiri supaya sidebar tak memuat seluruh `/spaces`. **Didaftarkan sebelum `/spaces/:id`** |

### `admins` — admin per space 🟡

> Status: **branch `feat/task-space-admin`, belum merge & belum deploy** (2026-08-06). Keputusannya di [[ADR - 0038 Hak Per-Objek Admin Space Task Management]].

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
| POST | `/tasks` | Buat task (set `response_due_at`+24h, notif supervisor). `type_id` **opsional** (klien lama tak mengirimnya) tapi bila diisi **wajib milik space** yang dipilih, kalau tidak `400`. Space `restricted` yang tak boleh diakses → `403` |
| GET | `/tasks/filter` · `/tasks/:id` | Filter (flag `assigned_to_me`/`created_by_me`/`pending_my_approval`/`filter_by_admin_division`) / detail (populated + `sla`) |
| GET | `/tasks/stats` · `/tasks/admin-stats` | Statistik status FLAT (rentang tanggal) |
| GET | `/tasks/counts` | Jumlah tiket **AKTIF** per scope (`created`/`assigned`/`team`) untuk badge tab |
| GET | `/tasks/pending-csat` | Tiket pemanggil yang **sudah selesai tapi belum dinilai** (`{data, total}`, terbaru dulu, maks 20) |
| POST | `/tasks/:id/csat` | Pemohon memberi rating 1..5 (komentar wajib bila ≤2); idempotent overwrite |
| PUT | `/tasks/:id` | Edit generik (partial) |
| PUT | `/tasks/:id/status` · `/archive` · `/unarchive` · `/due-date` · `/priority` · `/space` | Ubah status/arsip/jadwal/prioritas/pindah. `/space` ikut mengosongkan `type_id` (daftar tipe milik space lama) |
| PUT | `/tasks/:id/type` | Supervisor membetulkan tipe (gated izin triase). `type_id` wajib milik space tugas tsb; body kosong = kosongkan tipe |
| PUT/POST | `/tasks/:id/assign` · `/approve` · `/reject` | Assign/approve (body `start_date/due_date/priority_id/assign_to`)/reject. Boleh supervisor divisi space, admin, ATAU **admin space** (🟡). Supervisor divisi LAIN kini `403` — sebelumnya lolos karena ketiga rute ini tak pernah mengecek space sama sekali |
| GET | `/tasks/:id/history` | Riwayat perubahan (array) |
| DELETE | `/tasks/:id` | Hapus task (supervisor) |

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
| GET | `/report/summary-by-department` · `/report/timeline` · `/report/manpower-performance` · `/report/sla` | Laporan (scope supervisor→divisi + space yang ia pegang, **admin space**→space yang ia pegang + tugasnya sendiri, staff→sendiri) |
| GET | `/users` · `/users/byDivision` · `/departments` | Dropdown assignee & divisi (dari ERP) |
| GET | `/audits` | Audit trail lintas-task (`{items,total}`). Scope: admin→semua, supervisor→divisinya, **admin space**→space yang ia pegang (🟡). Memuat juga audit yang menempel pada SPACE (`space_admins`) yang tak punya `task_id` |

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
