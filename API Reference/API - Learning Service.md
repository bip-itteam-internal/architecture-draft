## Deskripsi

*Endpoint service `learning` (modul gateway **`/api/learning/*`**, port internal 6987). Isinya modul pelatihan karyawan yang dipindah utuh dari [[Microservices - Employee Service]] pada LMS Fase 0, ditambah pengajuan, evaluasi trainer, layar karyawan, dan post-test yang dibangun di service ini. Implementasi & catatan: [[Microservices - Learning Service]] · konsep: [[HRIS - Training Program]].*

- **Status**: ✅ Grounded ke kode `bip-erp` `origin/main` (diperiksa 2026-09-15); live di dev + produksi 2026-08-06; pengajuan, evaluasi, dan `/me` **terverifikasi lewat gateway hidup 2026-08-19**; rute post-test ada di biner produksi (diperiksa 2026-09-15); `GET /kpi/pelatihan` dan `GET /internal/calendar-feed` (PR [#1895](https://github.com/bip-itteam-internal/bip-erp/pull/1895)) **live di produksi 2026-09-15** dan diverifikasi dari dalam container, bersama penyaringan `as=reviewed` (PR [#1892](https://github.com/bip-itteam-internal/bip-erp/pull/1892)); DEV belum dideploy
- **RBAC**: izin modul `training` (`training.view` · `training.work` · `training.manage`), rincian di [[#Gerbang izin]]
- **Catatan pemindahan**: path internalnya **tidak berubah** dari versi lama, hanya prefix modulnya. `/api/employee/training/...` menjadi `/api/learning/training/...`

## Gerbang izin

Rute kelola digerbang `gate(izin, fallback)` (`services/learning/permission_gate.go`). Kolom **Izin** di tabel-tabel bawah memakai singkatan `view` / `work` / `manage`.

| Izin | Membuka |
|---|---|
| `training.view` | baca master, jadwal, peserta, riwayat, course, agregat evaluasi |
| `training.work` | tulis event & peserta, saklar kehadiran mandiri, rekap & ekspor percobaan post-test, antrean dan keputusan tahap HR pengajuan |
| `training.manage` | tulis master jenis & trainer, course, bank soal, pembatalan percobaan |

- Izin dibaca dari klaim JWT (header `BIP-Permissions`) **bila klaim itu memuat izin modul `training`**. Bila tidak, dan sakelar `TRAINING_TIER_FALLBACK` menyala (bawaan), tier `system_roles["hris"]` admin, supervisor, maupun staff mendapat **ketiga** izin sekaligus (`TrainingTierDefault`, `shared-library/common/catalog_training.go`).
- Kill-switch `TRAINING_PERMISSION_ENFORCEMENT=off` mengembalikan gerbang lama: rute tulis jatuh ke `RequireHRISStaff`, rute baca terbuka. Selama kill-switch menyala, `RequireHRISStaff` **tidak** dijalankan. Kedua sakelar dibaca sekali saat service start.
- **Tidak digerbang izin modul**: pengajuan pelatihan, seluruh `/me/*`, dan mengerjakan post-test. Yang menggerbang identitas pemanggil dan relasinya.

## Master — Jenis Pelatihan & Trainer

| Method | Path | Izin | Fungsi |
|---|---|---|---|
| GET | `/training/types` · `/training/types/:id` | view | List / detail jenis pelatihan |
| POST · PUT · DELETE | `/training/types` · `/training/types/:id` | manage | Buat (`name` wajib) / ubah (full-replace) / hapus |
| GET | `/training/trainers` · `/training/trainers/:id` | view | List / detail trainer |
| POST · PUT · DELETE | `/training/trainers` · `/training/trainers/:id` | manage | Buat / ubah / hapus. Trainer internal (`is_internal`) wajib `employee_id` |

> ⚠️ Rute statik (`/types`, `/trainers`) **wajib** didaftarkan sebelum rute param `/training/:id`. Fiber mencocokkan per urutan registrasi; terbalik berarti `/training/trainers` ter-match sebagai `:id` bernilai `"trainers"`.

⚠️ **Hapus jenis maupun trainer tidak memeriksa apakah masih dirujuk event.** Event yang merujuk master terhapus tak bisa disunting lagi, sebab `PUT /training/:id` memverifikasi ulang rujukannya dan membalas 400 `training_type ... not found` / `trainer ... not found`.

## Transaksi — Event Pelatihan

| Method | Path | Izin | Fungsi |
|---|---|---|---|
| GET | `/training` (`?department_key=&status=`) | view | List event pelatihan |
| GET | `/training/:id` | view | Detail |
| POST | `/training` | work | Buat; `status` kosong berarti `Scheduled` |
| PUT | `/training/:id` | work | Ubah (full-replace, guard transisi status) |
| PATCH | `/training/:id/attendance-open` | work | `{attendance_open: bool}` wajib ada (absen → 400). Membuka/menutup kehadiran mandiri |
| DELETE | `/training/:id` | work | Hapus, peserta dihapus lebih dulu |

- **Field**: `title`, `training_type_id`, `trainer_id`, `start_date`, `end_date` wajib (`end_date` tak boleh sebelum `start_date`); `start_time`/`end_time` `"HH:MM"`; `max_participants` 0 = tanpa batas; `location`, `cost` (informasional), `description`; `course_id` opsional menautkan post-test (lihat [[#Course & Bank Soal]]).
- **Department opsional** (peran penyelenggara, tidak membatasi peserta). Bila diisi, diverifikasi ke employee-service — lihat di bawah.
- Transisi status sah: `Scheduled → Ongoing → Completed`, dan `Scheduled|Ongoing → Cancelled`. `Completed` serta `Cancelled` terminal.
- ⚠️ `PUT` bersifat **full-replace**. Yang dipertahankan dari dokumen lama hanya `company_id`, `attendance_open`, dan metadata; field lain yang tak dikirim ikut terhapus, **termasuk `course_id` dan `max_participants`**. Klien penyunting wajib mengirim ulang keduanya.
- Saklar `attendance_open` sengaja punya endpoint sendiri supaya penyuntingan form tak diam-diam mematikannya.

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

| Method | Path | Izin | Fungsi |
|---|---|---|---|
| GET | `/training/:id/participants` | view | List peserta; tiap baris membawa `attended`, `attended_by`, `attended_at` |
| POST | `/training/:id/participants` | work | `{employee_id}`. Sudah terdaftar → 409; **kuota `max_participants` penuh → 409** (0 = tanpa batas, ditegakkan sejak 2026-08-11). Unique index `{training_id, employee_id}` menutup pendaftaran ganda yang berbarengan |
| PATCH | `/training/:id/participants/:employeeId` | work | `{attended: bool}` wajib ada. Ikut menulis `attended_by` = pemanggil dan `attended_at`, jadi koreksi HR menimpa tanda hadir mandiri |
| DELETE | `/training/:id/participants/:employeeId` | work | Batalkan peserta |
| GET | `/training/history/:employeeId` | view | Riwayat pelatihan per karyawan |

- **Pencatat kehadiran diturunkan, tidak disimpan terpisah** (`SumberKehadiran`): `attended_by` sama dengan `employee_id` berarti mandiri, selain itu HR, termasuk data lama yang tak punya `attended_by`.
- Pendaftaran belum memeriksa bahwa `employee_id` benar-benar ada di `work_data`.

## Pengajuan Pelatihan

| Method | Path | Gerbang | Fungsi |
|---|---|---|---|
| POST | `/training/requests` | identitas | Buat pengajuan. Body `{employee_id?, department_key?, training_type_id atau topic, reason, estimated_cost?}`; `employee_id` kosong = untuk diri sendiri, `department_key` kosong = departemen pemanggil. Balas 201 `{_id, status}` |
| GET | `/training/requests?as=self\|reviewer\|reviewed` | identitas | `self` = untuk ATAU oleh pemanggil; `reviewer` = tahap SPV yang menunjuk pemanggil, ditambah seluruh `Menunggu HR` bila memegang `training.work`, tanpa pengajuan milik sendiri; `reviewed` = pengajuan `Disetujui`/`Ditolak`: pemegang `training.view` atau `training.work` melihat seluruh riwayat keputusan perusahaannya, selain itu hanya yang tahap SPV-nya menunjuk pemanggil (`spv_review.employee_id`) |
| PATCH | `/training/requests/:id/review` | SPV yang ditunjuk · `training.work` untuk tahap HR | `{approve, note}`. Tahap ditentukan STATUS, bukan dikirim klien; tak seorang pun memutus pengajuannya sendiri |
| POST | `/training/requests/:id/cancel` | pembuat | Hanya `requested_by`, hanya selama belum diputuskan |

Status: `Menunggu SPV` → `Menunggu HR` → `Disetujui`, atau `Ditolak` di tahap mana pun, atau `Dibatalkan` oleh pembuatnya. Pengaju yang ternyata supervisor departemen itu sendiri langsung mulai di `Menunggu HR`; departemen tanpa supervisor ditolak 409.

✅ ~~**`as=reviewed` TIDAK disaring ke pemanggil.**~~ **Diperbaiki PR [#1892](https://github.com/bip-itteam-internal/bip-erp/pull/1892)** (merged 2026-09-15; image `Learning-Service` produksi hari itu dibangun dari commit yang memuatnya). Sebelumnya filternya hanya `company_id` dan status, jadi siapa pun yang punya identitas di perusahaan itu menerima **seluruh** pengajuan yang sudah diputuskan. Kini cabang `reviewed` di `request.go` membaca `izinTrainingEfektif`: tanpa `training.view` maupun `training.work`, filter ditambah `spv_review.employee_id` = pemanggil. Riwayat keputusan dibuka untuk `training.view` karena izin itu sudah membuka baca riwayat pelatihan siapa pun. Dikunci `TestPengajuanAsReviewedDisaringPerPemanggil` (`request_handler_test.go`).

⚠️ **`/training/requests` didaftarkan SEBELUM rute event.** Ia segmen statik; ditaruh sesudah `/training/:id` membuat seluruh permintaannya ter-match sebagai event ber-id `"requests"` lalu dibalas 400 *"id is not a valid ObjectID"*.

## Layar Karyawan (`/me`)

| Method | Path | Fungsi |
|---|---|---|
| GET | `/me/trainings` · `/me/trainings/history` | Pelatihan milik pemanggil: `Scheduled`/`Ongoing` · `Completed`/`Cancelled` |
| GET | `/me/trainings/:id` | Detail satu pelatihan milik pemanggil (bukan miliknya → 404) |
| POST | `/me/trainings/:id/attendance` | Tandai hadir mandiri. Syarat: tidak `Cancelled`, `attendance_open` menyala, dan sekarang berada di rentang tanggal + jam pelaksanaan (WIB). Bukan peserta → 403; sudah hadir → 200 `kehadiran sudah tercatat` beserta `sumber` |
| POST | `/me/trainings/:id/evaluation` | `{ratings: {penguasaan_materi, cara_menyampaikan, penguasaan_kelas, manfaat}, comment}`, tiap aspek 1..5 (0 ditolak). Hanya peserta (403), hanya `Completed` (409), sekali (duplikat → 409) |

Identitas **selalu** dari header yang diisi gateway dari klaim JWT, tak pernah dari path maupun query.

Baris `/me/trainings*` berbentuk rata: `training_id`, `title`, `status`, `department_key`, `location`, `start_date`/`end_date` (`YYYY-MM-DD`, WIB), `start_time`/`end_time`, `attendance_open`, `attended`, `trainer_id`, `trainer_name`, dan keputusan yang dihitung **server**: `can_attend` + `attend_block_reason`, serta `boleh_menilai` + `sudah_dinilai`. Kedua penanda penilaian dikirim **tanpa `omitempty`** supaya klien bisa membedakan "tidak boleh" dari "server lama yang belum punya field ini". `attend_block_reason` kosong bila boleh hadir, dan kosong pula bila sudah hadir.

## Agregat Penilaian Trainer

| Method | Path | Izin | Fungsi |
|---|---|---|---|
| GET | `/training/:id/evaluation` | view | Agregat satu kelas |
| GET | `/training/trainers/:id/evaluation` | view | Agregat satu trainer lintas kelasnya |

Balasan `data`: `responden`, `ditampilkan`, `penguasaan_materi`, `cara_menyampaikan`, `penguasaan_kelas`, `manfaat`, `rata_rata` (dibulatkan satu desimal; `rata_rata` dihitung dari nilai mentah, bukan dari rata-rata per aspek). Identitas penilai tak pernah ikut dalam respons.

Di bawah **tiga responden**, `ditampilkan: false` **dan seluruh angkanya nol** — klien yang lupa membaca penanda tak boleh punya angka untuk ditampilkan. Jumlah responden tetap dikirim.

## Course & Bank Soal

Grup `/courses` sengaja **tidak** diletakkan di bawah `/training`: segmen statik sesudah `/training/:id` akan ter-match sebagai event ber-id `courses`.

| Method | Path | Izin | Fungsi |
|---|---|---|---|
| GET | `/courses` · `/courses/:id` | view | List (`{data, count}`) / detail course |
| POST | `/courses` | manage | `{title, description?, passing_score}` (`passing_score` 0..100, 0 = tanpa ambang); `is_active` diset `true` |
| PUT | `/courses/:id` | manage | Ubah (full-replace) |
| DELETE | `/courses/:id` | manage | Hapus beserta quiz-nya. **409 bila course sudah punya percobaan**; nonaktifkan lewat `is_active` |
| GET | `/courses/:id/quiz` | manage | Bank soal post-test **berikut kunci** (`correct_index`); karena memuat kunci, GET pun digerbang `manage` |
| PUT | `/courses/:id/quiz` | manage | Upsert `{questions: [{id, text, options, correct_index, points}], shuffle, time_limit_minutes}`. `course_id` diambil dari path dan `kind` selalu `post` |
| GET | `/courses/:id/attempts` | work | Seluruh percobaan course (`{data, count}`), tanpa snapshot soal |
| GET | `/courses/:id/attempts/export` | work | CSV `rekaman-post-test.csv`: `employee_id, nama, jabatan, departemen, percobaan_ke, skor, skor_maks, lulus, training_id, dimulai, dikirim, dibatalkan, alasan_batal` |

- **Validasi soal**: `id` wajib dan unik dalam satu quiz (jawaban dicocokkan lewat id, bukan urutan), minimal 2 opsi, `correct_index` dalam rentang, `points` > 0, `time_limit_minutes` ≥ 0 (0 = tanpa batas). Satu quiz per course per jenis, dikunci unique index `{course_id, kind}`.
- Kunci jawaban tak pernah keluar lewat rute lain: `Question.MarshalJSON` membuang `correct_index`, dan hanya `GET /courses/:id/quiz` yang merakit bentuk berkunci.
- ⚠️ `PUT /courses/:id` full-replace termasuk `is_active`: permintaan tanpa field itu **menonaktifkan** course.

## Post-test (peserta)

| Method | Path | Gerbang | Fungsi |
|---|---|---|---|
| POST | `/me/post-test/:trainingId/start` | identitas | Mulai percobaan. Syarat: peserta terdaftar, event punya `course_id`, status `Completed`, belum pernah lulus (gagal syarat → 403; quiz belum disiapkan → 404). Balas 201 `{attempt_id, time_limit_minutes, questions: [{id, text, options, points}]}`, tanpa kunci, diacak bila `shuffle` |
| POST | `/me/post-test/attempt/:id` | identitas (pemilik) | `{answers: [{question_id, selected_index}]}`. Balas `{score, max_score, passed, passing_score}`. Sudah dikirim atau dibatalkan → 409; lewat batas waktu → 409 dan percobaan **hangus** (boleh mengulang); percobaan orang lain → 404 |
| PATCH | `/attempts/:id/void` | manage | `{reason}` wajib. Menandai batal **tanpa menghapus** barisnya |

- Tanpa header identitas, ketiga rute membalas **401** sebelum handler jalan.
- Penilaian memakai **snapshot** soal yang dibekukan saat percobaan dimulai; lulus bila `score × 100 ≥ passing_score × max_score`.
- `/me/post-test/attempt/:id` didaftarkan sebelum `/me/post-test/:trainingId/start` supaya `attempt` tak ter-match sebagai `trainingId`.

## Bahan KPI (panggilan mesin)

| Method | Path | Gerbang | Fungsi |
|---|---|---|---|
| GET | `/kpi/pelatihan?periode=YYYY-MM&company_id=&employee_id=A,B&key=` | kunci layanan `LEARNING_SERVICE_KEY` (query `key`) + `BIP-Gateway-ID` | Bahan sumber KPI `pelatihan` di [[Microservices - Employee Service]] |

- **Gerbang**: `key` kosong atau salah, maupun kunci server yang belum diatur, dibalas **401**. Rute ini tak digerbang izin modul maupun identitas; pemanggilnya mesin.
- **Validasi**: `periode` wajib `YYYY-MM` (bulan kalender WIB), `company_id` wajib, `employee_id` wajib dan maksimal **200** per panggilan; pelanggaran dibalas **400** (untuk batas id disertai `maks`). Database belum tersambung **503**.
- **Jawaban** `{"data": {...}}`:

| Field | Isi |
|---|---|
| `periode`, `dari`, `sampai` | Periode dan batasnya dalam WIB (`dari` inklusif, `sampai` eksklusif) |
| `pendaftaran[]` | Satu baris per pendaftaran pada kelas `Completed` yang `end_date`-nya di periode itu, disaring ke `company_id` dan `employee_id` yang diminta, diurutkan `training_id` lalu `employee_id`: `training_id`, `employee_id`, `hadir`, `wajib_post_test` (kelas punya `course_id`), `skor_terbaik_persen` (skor tertinggi dari percobaan post-test yang dikirim dan tidak dibatalkan; `null` bila belum ada atau kelasnya tanpa post-test) |
| `evaluasi` | `{responden, jumlah_nilai}` untuk kelas dan karyawan yang sama; `jumlah_nilai` = total empat aspek seluruh responden, jadi rata-rata per aspek = `jumlah_nilai / (responden × 4)`. **Tanpa** identitas penilai dan **tanpa** ambang responden: ambangnya diterapkan pemanggil atas gabungan batch |

`pendaftaran` tak pernah `null`. Contoh muatan yang dikunci test: `contohMuatanKPIPelatihan` di `services/learning/kpi_pelatihan_test.go`.

## Feed Kalender

| Method | Path | Gerbang | Fungsi |
|---|---|---|---|
| GET | `/internal/calendar-feed?from=<RFC3339>&to=<RFC3339>` | identitas (`BIP-Employee-ID`) | Kelas yang diikuti pemanggil sebagai peserta, dalam bentuk item [[Microservices - Calendar Service]] |

- Tanpa identitas **403**; `from`/`to` kosong, bukan RFC3339, `to` mendahului `from`, atau lebih dari 400 hari **400**; database belum tersambung **503**; galat lain **500**.
- Jawaban `{"items": [...]}`, tak pernah `null`. Item: `id` `learning:training:<id>`, `source` `learning`, `kind` `training`, `title`, `start_at`/`end_at`/`all_day`, `scope` `personal`, `owner` (pemanggil), `company_id` (perusahaan pembaca), `status` (`cancelled` bila kelas `Cancelled`, selain itu `confirmed`), `deep_link` `/hris/pelatihan-saya`, `meta.lokasi`. Aturan berjam vs seharian ada di dok kalender.
- `/internal/` **bukan** privat ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]); karena itu penyaringan ke peserta dikerjakan di rute ini.

✅ **Kedua rute terverifikasi di produksi 2026-09-15** dari dalam container, beserta kontrol negatifnya (rincian di [[Microservices - Learning Service]]). **Belum pernah dipanggil lewat gateway**: `/kpi/pelatihan` dipanggil langsung oleh employee-service, dan feed dipanggil calendar-service.

## Lain-lain

| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` | Health check, di belakang kunci gateway `BIP-Gateway-ID` |

## Belum Ada

Endpoint LMS lanjutan **belum ada**: materi PDF & video pada course, **pre-test** (model mengenal jenis `pre`, tetapi seluruh rute hanya melayani `post`), kurikulum jabatan, tenggat, Talent Pool. Desainnya di [[HRIS - Training Program]]. Bahan KPI (`/kpi/pelatihan`) dan feed kalender (`/internal/calendar-feed`) sudah ada sejak 2026-09-15, lihat bagian masing-masing di atas.

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

⚠️ **Rute course dan post-test belum pernah diverifikasi lewat gateway produksi.** Yang terbukti 2026-09-15 hanya keberadaan string rutenya di biner `Learning-Service` prod (`/me/post-test`, `quiz_attempt`, `attempts/export`, kontrol negatif string karangan → 0).

⚠️ **Terpasang bukan berarti terpakai.** Di produksi 2026-09-15 koleksi `training_request`, `trainer_evaluation`, `quiz`, dan `quiz_attempt` sama-sama **0 dokumen**, dan `course` belum pernah terbentuk, walau endpointnya live sejak 2026-08-11 (pengajuan, evaluasi) dan 2026-08-20 (post-test). Sebabnya ada di alur pemakai dan ketiadaan layar, lihat [[Microservices - Learning Service]].

## Dokumen Terkait

- [[Microservices - Learning Service]] · [[HRIS - Training Program]]
- [[API - Employee Service]] — rumah lama endpoint ini · [[API - Index]]
- [[CORE - API Master Gateway]]
