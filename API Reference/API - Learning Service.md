## Deskripsi

*Endpoint service `learning` (modul gateway **`/api/learning/*`**, port internal 6987). Isinya modul pelatihan karyawan yang dipindah utuh dari [[Microservices - Employee Service]] pada LMS Fase 0. Implementasi & catatan: [[Microservices - Learning Service]] · konsep: [[HRIS - Training Program]].*

- **Status**: ✅ Grounded ke kode, live di dev + produksi 2026-08-06; pengajuan, evaluasi, dan `/me` **terverifikasi lewat gateway hidup 2026-08-19**
- **RBAC**: tulis = `RequireHRISStaff`; GET terbuka di belakang gateway
- **Catatan pemindahan**: path internalnya **tidak berubah** dari versi lama, hanya prefix modulnya. `/api/employee/training/...` menjadi `/api/learning/training/...`

## Master — Jenis Pelatihan & Trainer

| Method | Path | Fungsi |
|---|---|---|
| GET · POST | `/training/types` | List / buat jenis pelatihan |
| GET · PUT · DELETE | `/training/types/:id` | Detail / ubah / hapus (by ObjectID) |
| GET · POST | `/training/trainers` | List / buat trainer, internal (`employee_id`) atau eksternal |
| GET · PUT · DELETE | `/training/trainers/:id` | Detail / ubah / hapus (by ObjectID) |

> ⚠️ Rute statik (`/types`, `/trainers`) **wajib** didaftarkan sebelum rute param `/training/:id`. Fiber mencocokkan per urutan registrasi; terbalik berarti `/training/trainers` ter-match sebagai `:id` bernilai `"trainers"`.

## Transaksi — Event Pelatihan

| Method | Path | Fungsi |
|---|---|---|
| GET · POST | `/training` (`?department_key=&status=`) | List / buat event pelatihan |
| GET · PUT · DELETE | `/training/:id` | Detail / ubah (guard transisi status) / hapus (cascade peserta) |

- **Department opsional** (peran penyelenggara, tidak membatasi peserta). Bila diisi, diverifikasi ke employee-service — lihat di bawah.
- Transisi status sah: `Scheduled → Ongoing → Completed`, dan `Scheduled|Ongoing → Cancelled`. `Completed` serta `Cancelled` terminal.
- `PUT` bersifat **full-replace**, jadi pemanggil wajib mengirim objek lengkap.

### Kode status verifikasi `department_key`

Verifikasi memanggil `GET {EMPLOYEE_MODULE_URL}/master/departments/{key}` di [[Microservices - Employee Service]]. Pemetaannya dipisah tegas supaya gangguan server tidak terbaca sebagai kesalahan input:

| Kondisi | Balasan |
|---|---|
| Departemen ditemukan (2xx) | Lolos |
| Departemen tidak ada (404) | **400** `department "<key>" not found` |
| employee-service membalas 5xx / status lain | **502**, pesan menyebut status, bukan "not found" |
| Tak terjangkau, atau `EMPLOYEE_MODULE_URL` kosong | **502**, pesan menyebut tak terjangkau / belum dikonfigurasi |

`department_key` kosong melewati pemeriksaan sepenuhnya.

> ⚠️ **Aturan di atas berlaku untuk EVENT pelatihan, bukan PENGAJUAN.** Sejak PR [#1153](https://github.com/bip-itteam-internal/bip-erp/pull/1153) `POST /training/requests` memakai resolusi tersendiri (`departemen.go`): kosong berarti "departemen saya" dari header `BIP-Department`, dan key yang dikirim **diterjemahkan jadi NAMA** sebelum dipakai mencari supervisor. Lihat catatan satuan di bawah.

### ⚠️ Satuan `department_key` vs `work_data.department`

`department_key` adalah **key** (`master_department.key`, mis. `it`); `work_data.department` menyimpan **nama** (`Tech Development`). Pencarian supervisor di [[Microservices - Employee Service]] (`/list?type=supervisor&department=`) menyaring **nama**, bukan key.

Mengirim key ke sana menghasilkan nol supervisor lalu **409 "departemen belum punya supervisor"** — galat yang menuduh data master padahal yang salah satuan nilainya. Terjadi nyata di `POST /training/requests` sejak PR #1148; **6 dari 10 departemen** punya key ≠ name sehingga pengajuan mustahil dibuat untuk keenamnya, sementara empat sisanya jalan karena kebetulan key-nya sama dengan namanya. Diperbaiki PR #1153.

## Peserta & Kehadiran

| Method | Path | Fungsi |
|---|---|---|
| GET · POST | `/training/:id/participants` | List / enroll peserta. Unique index `{training_id, employee_id}` menutup pendaftaran ganda secara atomik; **tanpa cap kapasitas** (kapasitas = jumlah peserta yang di-assign) |
| PATCH · DELETE | `/training/:id/participants/:employeeId` | Tandai kehadiran (boolean) / batalkan peserta |
| GET | `/training/history/:employeeId` | Riwayat pelatihan per karyawan |

## Pengajuan Pelatihan

| Method | Path | Fungsi |
|---|---|---|
| POST | `/training/requests` | Buat pengajuan. `department_key` **opsional** (kosong = departemen pemanggil) |
| GET | `/training/requests?as=self\|reviewer\|reviewed` | Daftar per sudut pandang; ketiganya relasional, bukan berbasis izin |
| PATCH | `/training/requests/:id/review` | `{approve, note}`. Tahap ditentukan STATUS, bukan dikirim klien |
| POST | `/training/requests/:id/cancel` | Hanya pembuatnya, hanya selama belum diputuskan |

⚠️ **`/training/requests` didaftarkan SEBELUM rute event.** Ia segmen statik; ditaruh sesudah `/training/:id` membuat seluruh permintaannya ter-match sebagai event ber-id `"requests"` lalu dibalas 400 *"id is not a valid ObjectID"*.

## Layar Karyawan (`/me`)

| Method | Path | Fungsi |
|---|---|---|
| GET | `/me/trainings` · `/me/trainings/history` | Pelatihan milik pemanggil (berjalan / selesai-batal) |
| GET | `/me/trainings/:id` | Detail satu pelatihan milik pemanggil |
| POST | `/me/trainings/:id/attendance` | Tandai hadir mandiri |
| POST | `/me/trainings/:id/evaluation` | `{ratings, comment}`, empat aspek 1..5 |

Identitas **selalu** dari header yang diisi gateway dari klaim JWT, tak pernah dari path maupun query.

Keputusan dihitung **server**, klien cukup menampilkan: `can_attend` + `attend_block_reason`, dan (PR #1150) `boleh_menilai` + `sudah_dinilai` + `trainer_name`. Kedua penanda penilaian dikirim **tanpa `omitempty`** supaya klien bisa membedakan "tidak boleh" dari "server lama yang belum punya field ini".

## Agregat Penilaian Trainer

| Method | Path | Fungsi |
|---|---|---|
| GET | `/training/:id/evaluation` | Agregat satu kelas |
| GET | `/training/trainers/:id/evaluation` | Agregat satu trainer lintas kelasnya |

Di bawah **tiga responden**, `ditampilkan: false` **dan seluruh angkanya nol** — klien yang lupa membaca penanda tak boleh punya angka untuk ditampilkan. Jumlah responden tetap dikirim.

## Lain-lain

| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` | Health check, di belakang kunci gateway `BIP-Gateway-ID` |

## Belum Ada

Seluruh endpoint LMS (course, materi, bank soal, pre/post test, skoring, kurikulum jabatan, Talent Pool) **belum ada** — Fase 1 ke atas. Desainnya di [[HRIS - Training Program]]. **Penilaian trainer sudah ada** (lihat di atas).

✅ ~~Seluruh endpoint pengajuan, evaluasi, dan penanda `/me` belum pernah diverifikasi lewat gateway hidup~~ — **terverifikasi 2026-08-19** lewat gateway dev, sesudah image `learning-service` dibuild ulang di dev dan produksi:

| Panggilan lewat gateway dev | Balasan |
|---|---|
| `GET /api/learning/training` | 200 |
| `GET /api/learning/training/types` | 200 (1 dokumen) |
| `GET /api/learning/training/requests?as=self` | 200 |
| `GET /api/learning/training/requests?as=reviewer` | 200 |
| `GET /api/learning/me/trainings` | 200 |
| `GET /api/learning/training/requests-karangan` (**kontrol negatif**) | **400** `id is not a valid ObjectID` |

Kontrol negatif itu bagian dari buktinya, bukan pelengkap: ia berprefiks **sama** dengan rute nyata sehingga hasil yang beda membuktikan routing-nya benar-benar membedakan. Tanpa itu, deretan 200 di atas tak bisa dipisahkan dari gateway yang meloloskan apa saja. Sebelum rebuild, `/training/requests` tertelan `/training/:id` dan membalas 400.

⚠️ **Terpasang bukan berarti terpakai.** Di produksi 2026-08-19 koleksi `training_request` dan `trainer_evaluation` sama-sama **0 dokumen** walau endpointnya live sejak 2026-08-11 — sebabnya alur karyawan yang terputus, lihat [[Microservices - Learning Service]].

## Dokumen Terkait

- [[Microservices - Learning Service]] · [[HRIS - Training Program]]
- [[API - Employee Service]] — rumah lama endpoint ini · [[API - Index]]
- [[CORE - API Master Gateway]]
