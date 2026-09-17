## Deskripsi

*Endpoint service `learning` (modul gateway **`/api/learning/*`**, port internal 6987). Isinya modul pelatihan karyawan yang dipindah utuh dari [[Microservices - Employee Service]] pada LMS Fase 0, ditambah pengajuan, evaluasi trainer, layar karyawan, dan post-test yang dibangun di service ini. Implementasi & catatan: [[Microservices - Learning Service]] · konsep: [[HRIS - Training Program]].*

- **Status**: ✅ Grounded ke kode `bip-erp` `origin/main` (diperiksa 2026-09-15); live di dev + produksi 2026-08-06; pengajuan, evaluasi, dan `/me` **terverifikasi lewat gateway hidup 2026-08-19**; rute post-test ada di biner produksi (diperiksa 2026-09-15); `GET /kpi/pelatihan` dan `GET /internal/calendar-feed` (PR [#1895](https://github.com/bip-itteam-internal/bip-erp/pull/1895)) **live di produksi 2026-09-15** dan diverifikasi dari dalam container, bersama penyaringan `as=reviewed` (PR [#1892](https://github.com/bip-itteam-internal/bip-erp/pull/1892)); DEV belum dideploy. § Rencana Pelatihan Tahunan, § Bahan KPI Rencana, dan § Sertifikat Pelatihan: PR bip-erp #1903 dan #1904 **merged 2026-09-16** (diukur `gh pr view` 2026-09-17); status deploy-nya belum diukur ulang. ✅ **Tahap 3a/3b merged** (pre-test, kelulusan = naik dari pre-test, `passing_score` dibuang, kunci per kelas): PR [#1913](https://github.com/bip-itteam-internal/bip-erp/pull/1913) merged 2026-09-16 (Tahap 3a awal) dan PR [#1934](https://github.com/bip-itteam-internal/bip-erp/pull/1934) **merged 2026-09-17 01:15 UTC** (perbaikan review Tahap 3a dan seluruh Tahap 3b), diukur `gh pr view` 2026-09-17 dan dibuktikan `git grep` ke `origin/main` (rute `/me/pre-test`, `NaikDariPreTest`; `passing_score` tinggal di komentar). Pengukuran deploy prod-nya dicatat di [[HRIS - Matriks KPI per Departemen]]. 🔜 **`kesesuaian_materi` dan tambahan kontrak `/kpi/pelatihan`** (T1-T2 [[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]]) dibaca dari branch `feat/learning-kesesuaian-materi`, **belum PR, belum merged, belum deploy** per 2026-09-17; tiap bagian yang berubah diberi catatan bertanggal. Ukur ulang sebelum mengutipnya sebagai perilaku yang berjalan.
- **RBAC**: izin modul `training` (`training.view` · `training.work` · `training.manage`), rincian di [[#Gerbang izin]]
- **Catatan pemindahan**: path internalnya **tidak berubah** dari versi lama, hanya prefix modulnya. `/api/employee/training/...` menjadi `/api/learning/training/...`

## Gerbang izin

Rute kelola digerbang `gate(izin, fallback)` (`services/learning/permission_gate.go`). Kolom **Izin** di tabel-tabel bawah memakai singkatan `view` / `work` / `manage`.

| Izin | Membuka |
|---|---|
| `training.view` | baca master, jadwal, peserta, riwayat, course, agregat evaluasi |
| `training.work` | tulis event & peserta, saklar kehadiran mandiri, rekap & ekspor percobaan pre-test dan post-test, antrean dan keputusan tahap HR pengajuan |
| `training.manage` | tulis master jenis & trainer, course, bank soal, pembatalan percobaan |

- Izin dibaca dari klaim JWT (header `BIP-Permissions`) **bila klaim itu memuat izin modul `training`**. Bila tidak, dan sakelar `TRAINING_TIER_FALLBACK` menyala (bawaan), tier `system_roles["hris"]` admin, supervisor, maupun staff mendapat **ketiga** izin sekaligus (`TrainingTierDefault`, `shared-library/common/catalog_training.go`).
- Kill-switch `TRAINING_PERMISSION_ENFORCEMENT=off` mengembalikan gerbang lama: rute tulis jatuh ke `RequireHRISStaff`, rute baca terbuka. Selama kill-switch menyala, `RequireHRISStaff` **tidak** dijalankan. Kedua sakelar dibaca sekali saat service start.
- **Tidak digerbang izin modul**: pengajuan pelatihan, seluruh `/me/*`, dan mengerjakan pre-test maupun post-test. Yang menggerbang identitas pemanggil dan relasinya.
- ⚠️ **Rute baca sertifikat pelatihan** (`/training/certificate-settings`, `/training/certificates/:certId/pdf`, `/training/:id/certificates` — merged 2026-09-16 lewat bip-erp PR #1904, lihat § Sertifikat Pelatihan) **memakai fallback `RequireHRISStaff`, BUKAN `nil`**, beda dari pola baca lain di file ini. Rute-rute ini baru; bila fallback-nya `nil`, kill-switch mati akan membuka baca status dan unduh PDF sertifikat rekan kerja ke karyawan mana pun. Keputusan 2026-09-15 membatasinya ke peserta sendiri dan HR (`sertifikat.go:460-465`).

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

- **Field**: `title`, `training_type_id`, `trainer_id`, `start_date`, `end_date` wajib (`end_date` tak boleh sebelum `start_date`); `start_time`/`end_time` `"HH:MM"`; `max_participants` 0 = tanpa batas; `location`, `cost` (informasional), `description`; `course_id` opsional menautkan pre-test dan post-test (lihat [[#Course & Bank Soal]]).
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

## Rencana Pelatihan Tahunan (`/training/plan-items`)

✅ Sudah di `origin/main` (diukur 2026-09-16: `git grep plan-items origin/main -- services/learning` menemukan `rencana.go`, `training.go`, dan tiga berkas uji; kontrol negatif string karangan nol hit). Sumber: `services/learning/rencana.go`, `models_rencana.go`.

| Method | Path | Izin | Fungsi |
|---|---|---|---|
| GET | `/training/plan-items?tahun=YYYY` | view | Daftar butir rencana tahun itu (bawaan tahun berjalan WIB) beserta status pelaksanaan dan kelas tertaut |
| POST | `/training/plan-items` | work | Tambah butir `{tahun, bulan, judul, training_type_id?, department_keys?, catatan?}`. `department_keys` = daftar departemen sasaran (boleh lebih dari satu, maks 50, spasi/duplikat dibuang, tiap kunci diperiksa ke master employee-service; kunci tak ada → 400, employee-service tak terjangkau → 502). `department_key` tunggal lama masih diterima dan digabung ke daftar. Bulan target sudah lewat → 409 |
| PUT | `/training/plan-items/:id` | work | Ubah isi/bulan butir aktif, badan sama dengan POST; `department_keys` ditulis utuh dan field lama `department_key` dibuang (`$unset`). Bulan tujuan sudah lewat, butir dibatalkan/terkunci, atau memindah butir yang bulannya sudah berjalan → 409 |
| POST | `/training/plan-items/:id/cancel` | work | Batalkan, `{alasan}` wajib (maks 500 karakter). Sudah dibatalkan, terkunci, atau sudah terlaksana → 409 |
| DELETE | `/training/plan-items/:id` | work | Hapus. Terkunci, bulan sudah berjalan, atau masih tertaut kelas → 409 |

- Gerbang sama seperti Event Pelatihan: `gate(PermTrainingView, nil)` untuk baca, `gate(PermTrainingWork, RequireHRISStaff)` untuk seluruh rute tulis (`rencana.go:114,149,181,247,310`).
- Rute statik, wajib didaftarkan sebelum `/training/:id` (`rencana.go:19-20`).
- Tiap baris respons membawa tambahan yang DIHITUNG server: `status_pelaksanaan` (`direncanakan`/`terlaksana`/`terlaksana_terlambat`/`belum_terlaksana`/`dibatalkan`), **`terkunci`** (bulan target sudah lewat), **`sudah_mulai`** (bulan target sudah dimulai — mengunci aksi Hapus dan Pindah Bulan), dan `kelas` (ringkasan kelas tertaut) (`models_rencana.go:250-259`).
- `department_key`/`training_type_id` opsional, diverifikasi ke master yang sama dengan Event Pelatihan bila diisi (`rencana.go:85-103`).
- Aturan lengkap tiap gerbang 409 (kapan terkunci, kapan `sudah_mulai` berlaku, kenapa membatalkan butir yang sudah terlaksana ditolak): [[Microservices - Learning Service]].

## Bahan KPI Rencana (panggilan mesin)

✅ Sudah di `origin/main` (`services/learning/kpi_rencana_pelatihan.go`), diukur bersama § Rencana Pelatihan Tahunan di atas.

| Method | Path | Gerbang | Fungsi |
|---|---|---|---|
| GET | `/kpi/rencana-pelatihan?periode=YYYY-MM&company_id=&key=` | kunci layanan `LEARNING_SERVICE_KEY` (sama dengan `/kpi/pelatihan`) | Bahan sumber KPI baru `rencana_pelatihan` |

- `periode` (`YYYY-MM`) dan `company_id` wajib; cacat → 400; database belum tersambung → 503 (`kpi_rencana_pelatihan.go:130-141`).
- Jawaban `{"data": {periode, dari, sampai, butir: [{id, judul, status_pelaksanaan}]}}`; `butir` tak pernah `null` (`kpi_rencana_pelatihan.go:30-43,70-92`).
- Melaporkan **status per butir**, bukan persentase — dihitung fungsi murni yang sama dengan layar Rencana, sehingga layar dan KPI tak mungkin berselisih (`kpi_rencana_pelatihan.go:57-92`). Sisi pemanggil (sumber KPI `rencana_pelatihan` di employee-service) **belum dibaca/diverifikasi** untuk dok ini. Rincian: [[Microservices - Learning Service]].

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
| POST | `/me/trainings/:id/evaluation` | `{ratings: {penguasaan_materi, cara_menyampaikan, penguasaan_kelas, manfaat}, kesesuaian_materi, comment}`, tiap aspek 1..5 (0 ditolak). `kesesuaian_materi` 🔜 (branch `feat/learning-kesesuaian-materi`, belum merged per 2026-09-17): bilangan bulat 1..10, **opsional** (`null` atau kunci absen = tidak dijawab), 0 atau di luar rentang → 400 sebelum database. Hanya peserta (403), hanya `Completed` (409), sekali (duplikat → 409) |

Identitas **selalu** dari header yang diisi gateway dari klaim JWT, tak pernah dari path maupun query.

Baris `/me/trainings*` berbentuk rata: `training_id`, `title`, `status`, `department_key`, `location`, `start_date`/`end_date` (`YYYY-MM-DD`, WIB), `start_time`/`end_time`, `attendance_open`, `attended`, `trainer_id`, `trainer_name`, `sertifikat_tersedia` + `nomor_sertifikat`, dan keputusan yang dihitung **server**: `can_attend` + `attend_block_reason`, `boleh_menilai` + `sudah_dinilai`, `pre_test_tersedia` + `pre_test_selesai` + `pre_test_terlewat` (Tahap 3b, merged 2026-09-17 lewat bip-erp PR #1934), serta `post_test_tersedia` + `post_test_lulus`. Penanda-penanda itu dikirim **tanpa `omitempty`** supaya klien bisa membedakan "tidak boleh" dari "server lama yang belum punya field ini". `attend_block_reason` kosong bila boleh hadir, dan kosong pula bila sudah hadir.

- `post_test_tersedia` mengirim **KEPUTUSAN**, bukan fakta mentah: ia memanggil `BolehMengerjakanPostTest`, aturan yang sama dengan penjaga rute `start`, jadi kelas yang belum `Completed`, yang sudah dilulusi, maupun (Tahap 3b) yang **pre-test-nya belum terkirim** tak menyalakannya; ia juga hanya menyala bila bank soal **post** ada (`me.go:338-377`). Itu disengaja. `/me/trainings` justru hanya memuat `Scheduled` dan `Ongoing`, sehingga penanda berbasis "ada bank soalnya" saja akan menyala persis di daftar yang tak satu pun barisnya boleh dikerjakan. Konsekuensi yang diterima sadar: tombol Kerjakan post-test hanya bisa muncul di `/me/trainings/history`.
- **Penanda pre-test (Tahap 3b, merged 2026-09-17 lewat bip-erp PR #1934)**: `pre_test_tersedia` memanggil `BolehMengerjakanPreTest` (kelas belum `Completed`, bukan `Cancelled`, belum ada pre terkirim untuk kelas itu) dan hanya menyala bila bank soal **pre** ada, jadi kebalikan dari post-test ia muncul di `/me/trainings`. `pre_test_selesai` = ada percobaan pre yang terkirim dan tidak dibatalkan untuk kelas itu. Bank soal pre dan post dibaca terpisah, masing-masing untuk penandanya sendiri. Keduanya `false` berarti pre-test belum dikerjakan dan tak bisa dikerjakan sekarang (kelas sudah `Completed` atau `Cancelled`, atau bank soal pre belum ada), atau kelasnya memang tak bermateri; **klien tak bisa membedakan keduanya** karena `course_id` tak dikirim (`me.go:83-96`, `me.go:260-284`, `me.go:338-377`).
- **`pre_test_terlewat`** (Tahap 3b, sama dengan di atas) = KEPUTUSAN server bahwa peserta buntu permanen di kelas itu: kelas `Completed`, materinya punya bank soal **pre**, pre-test tak pernah terkirim untuk kelas itu, **dan** bacaan bank soal maupun percobaan berhasil (`me.go:360-369`). Klien menampilkan "Terkunci: pre-test terlewat, hubungi HR" **hanya** dari penanda ini. ⛔ Jangan dirakit di klien dari `status` + dua penanda pre: versi pertama layar web melakukannya dan menuduh setiap kelas selesai tanpa materi. Penanda ini **gagal-TERTUTUP**, kebalikan dari penanda tersedia, karena kalimatnya menuduh; server lama yang tak mengirimnya dibaca `false`.
- Galat membaca bank soal sengaja **gagal-TERBUKA** untuk kedua penanda **tersedia** (penanda tetap menyala lalu server menjawab "bank soal ... belum disusun"), pola yang sama dengan `boleh_menilai`. Menutupnya diam-diam berarti peserta kehilangan ujiannya tanpa penjelasan. ⚠️ Galat membaca **percobaan** berbeda: di-log, lalu penanda tersedia dihitung seolah tak ada percobaan sama sekali (`me.go:286-295`), sehingga `post_test_tersedia` padam (pre dianggap belum terkirim) sementara `pre_test_tersedia` bisa menyala bagi orang yang sebenarnya sudah mengerjakannya. Untuk jalur ini post gagal-tertutup, pre gagal-terbuka. Kedua galat baca itu **mematikan** `pre_test_terlewat`.
- `post_test_lulus`, `pre_test_selesai`, dan `pre_test_terlewat` berskala **KELAS** (`training_id`), bukan course (Tahap 3b, merged 2026-09-17 lewat bip-erp PR #1934; sebelumnya `post_test_lulus` berskala course), sejalan dengan penjaga `start` yang kini menyaring riwayat percobaan per `training_id` (`me.go:296-315`, `me_posttest.go:123-131`).

## Agregat Penilaian Trainer

| Method | Path | Izin | Fungsi |
|---|---|---|---|
| GET | `/training/:id/evaluation` | view | Agregat satu kelas |
| GET | `/training/trainers/:id/evaluation` | view | Agregat satu trainer lintas kelasnya |

Balasan `data`: `responden`, `ditampilkan`, `penguasaan_materi`, `cara_menyampaikan`, `penguasaan_kelas`, `manfaat`, `rata_rata` (dibulatkan satu desimal; `rata_rata` dihitung dari nilai mentah, bukan dari rata-rata per aspek). Identitas penilai tak pernah ikut dalam respons.

Di bawah **tiga responden**, `ditampilkan: false` **dan seluruh angkanya nol** — klien yang lupa membaca penanda tak boleh punya angka untuk ditampilkan. Jumlah responden tetap dikirim.

🔜 **Kesesuaian materi** (branch `feat/learning-kesesuaian-materi`, belum merged per 2026-09-17; [[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]]):

- **Hanya agregat per kelas** (`/training/:id/evaluation`) menambah objek `kesesuaian`: `{responden, ditampilkan, rata_rata}`. Agregat per trainer tidak membawanya, karena materi kelas bukan milik trainer.
- `responden` = kiriman yang **menjawab** dengan nilai 1..10 saja, jadi bisa lebih kecil dari `responden` agregat trainer. Ambang tiga responden berlaku **sendiri** atas angka ini; di bawahnya `ditampilkan: false` dan `rata_rata` 0. `rata_rata` satu desimal, skala 1..10.
- ⛔ **Sejajar, bukan komponen.** `kesesuaian.rata_rata` menilai materi dan tidak ikut dalam `rata_rata` trainer maupun empat aspeknya. Jangan menjumlahkan atau merata-ratakan keduanya jadi satu angka, dan jangan memakainya bersama metrik kepuasan trainer seolah bagian dari nilai itu.

## Course & Bank Soal

Grup `/courses` sengaja **tidak** diletakkan di bawah `/training`: segmen statik sesudah `/training/:id` akan ter-match sebagai event ber-id `courses`.

| Method | Path | Izin | Fungsi |
|---|---|---|---|
| GET | `/courses` · `/courses/:id` | view | List (`{data, count}`) / detail course |
| POST | `/courses` | manage | `{title, description?, max_attempt?, retry_cooldown_hours?}` (`max_attempt` ≥ 0, 0 = tanpa batas; `retry_cooldown_hours` 0..8760, 0 = tanpa jeda); `is_active` diset `true`. `passing_score` **dibuang** dari model (Tahap 3b, merged 2026-09-17 lewat bip-erp PR #1934): kunci itu bila masih dikirim tak dibaca apa pun, kelulusan kini dihitung dari kenaikan terhadap pre-test (`models_course.go:23-29`, `ValidateCourse` `models_course.go:56-67`) |
| PUT | `/courses/:id` | manage | Ubah (full-replace, **kecuali `is_active`** yang dipulihkan dari dokumen lama bila kuncinya tak dikirim) |
| DELETE | `/courses/:id` | manage | Hapus beserta quiz-nya. **409 bila course sudah punya percobaan**; nonaktifkan lewat `is_active` |
| GET | `/courses/:id/quiz?kind=pre\|post` | manage | Bank soal jenis itu **berikut kunci** (`correct_index`) dan `kind`-nya; karena memuat kunci, GET pun digerbang `manage` |
| PUT | `/courses/:id/quiz?kind=pre\|post` | manage | Upsert `{questions: [{id, text, options, correct_index, points}], shuffle, time_limit_minutes}`. `course_id` diambil dari path dan `kind` dari **query**, bukan dari body |
| GET | `/courses/:id/attempts` | work | Seluruh percobaan course, **pre maupun post** (`{data, count}`, tiap baris membawa `kind`), tanpa snapshot soal |
| GET | `/courses/:id/attempts/export` | work | CSV `rekaman-ujian.csv`: `employee_id, nama, jabatan, departemen, jenis, percobaan_ke, skor, skor_maks, lulus, training_id, dimulai, dikirim, dibatalkan, alasan_batal` |

- **`?kind=` (Tahap 3b, merged 2026-09-17 lewat bip-erp PR #1934)**: kosong = `post` (pemanggil lama tetap mendarat di bank soal post), nilai selain `pre`/`post` **400**, bukan dijatuhkan ke bawaan (`jenisKuisDariQuery`, `course.go:271-281`; dipakai GET dan PUT, `course.go:289-292`, `course.go:312-319`).
- **Ekspor dua jenis (Tahap 3b, merged 2026-09-17 lewat bip-erp PR #1934)**: kolom `jenis` (`pre`/`post`) berdiri sebelum `percobaan_ke`, dan berkasnya berganti nama dari `rekaman-post-test.csv` (`course.go:167-188`). Baris pre selalu `lulus=false` karena pre tak punya kelulusan, dan `percobaan_ke` dihitung per orang, kelas, dan jenis (`me_posttest.go:123-127`, `me_posttest.go:228`), jadi tanpa kolom `jenis` baris pre tak bisa dibedakan dari post-test yang gagal. `/courses/:id/attempts` hanya menyaring `course_id`, sehingga memuat kedua jenis (`course.go:211-213`).
- **Validasi soal**: `id` wajib dan unik dalam satu quiz (jawaban dicocokkan lewat id, bukan urutan), minimal 2 opsi, `correct_index` dalam rentang, `points` > 0, `time_limit_minutes` ≥ 0 (0 = tanpa batas). Satu quiz per course per jenis, dikunci unique index `{course_id, kind}`.
- Kunci jawaban tak pernah keluar lewat rute lain: `Question.MarshalJSON` membuang `correct_index`, dan hanya `GET /courses/:id/quiz` yang merakit bentuk berkunci.
- **Batas mengulang** hidup di course, bukan di quiz: `max_attempt` (kuota) dan `retry_cooldown_hours` (jeda antar-percobaan, dihitung dari `started_at` percobaan terakhir). Keduanya 0 pada course lama, jadi perilaku sebelum fitur ini tidak berubah tanpa tindakan HR. Nilainya disimpan di course, tetapi (Tahap 3b, merged 2026-09-17 lewat bip-erp PR #1934) **hanya berlaku untuk post-test** dan percobaannya dihitung per **KELAS** (`training_id`); pre-test tanpa kuota maupun jeda (`me_posttest.go:123-131`, `me_posttest.go:191-206`). Nilai course memakai percobaan **TERBAIK**, jadi tanpa kuota metrik KPI-nya mengukur ketekunan mengulang, bukan kemampuan.
- ⚠️ `PUT /courses/:id` full-replace, tetapi `is_active` **dikecualikan**: bila kunci itu tak ada di badan permintaan, nilainya diambil dari dokumen lama. Sebelum 2026-09-16 tidak demikian, dan akibatnya satu permintaan Ubah yang cuma membetulkan judul menonaktifkan course-nya diam-diam. Mengirim `is_active: false` secara sengaja tetap berlaku — yang diperiksa kehadiran kuncinya, bukan nilainya.

## Pre-test & Post-test (peserta)

| Method | Path | Gerbang | Fungsi |
|---|---|---|---|
| POST | `/me/pre-test/:trainingId/start` | identitas | **Tahap 3b, merged 2026-09-17 lewat bip-erp PR #1934.** Mulai percobaan pre-test. Syarat: peserta terdaftar, event punya `course_id`, status **belum** `Completed` dan bukan `Cancelled`, belum ada pre-test **terkirim** untuk kelas itu (gagal syarat → 403; bank soal pre belum disusun → 404). Pre yang **hangus** karena waktu habis boleh diulang; tanpa kuota maupun jeda. Balas 201 dengan bentuk yang SAMA dengan `start` post-test. Tak punya rute attempt sendiri: melanjutkan dan mengirim jawaban pre memakai `/me/post-test/attempt/:id` |
| POST | `/me/post-test/:trainingId/start` | identitas | Mulai percobaan BARU (memakan satu kuota). Syarat: peserta terdaftar, event punya `course_id`, status `Completed`, **sudah ada pre-test terkirim untuk kelas itu** (Tahap 3b), belum pernah lulus **di kelas itu** (gagal syarat → 403; bank soal post belum disusun → 404); kuota habis atau masih dalam jeda → 403 dengan pesan yang menyebut **kapan** boleh mengulang (WIB). Balas 201 `{attempt_id, attempt_no, started_at, time_limit_minutes, sisa_detik, questions: [{id, text, options, points}]}`, tanpa kunci, diacak bila `shuffle` |
| GET | `/me/post-test/attempt/:id` | identitas (pemilik) | **Melanjutkan** percobaan yang sedang berjalan (pre maupun post), tanpa memakan kuota. Balas bentuk yang SAMA dengan `start`; soal disajikan pada urutan snapshot, tidak diacak ulang. Sudah dikirim atau dibatalkan → 409; lewat batas waktu → 409, tetapi rute ini **read-only** dan tidak menghanguskan apa pun (penghangusan dikerjakan rute kirim jawaban, `me_posttest.go:419-422`); percobaan orang lain → 404 (ditolak lewat **filter kueri**, bukan diperiksa sesudah dibaca) |
| POST | `/me/post-test/attempt/:id` | identitas (pemilik) | `{answers: [{question_id, selected_index}]}`, untuk percobaan pre maupun post. Balas `{kind, score, max_score, passed}`, ditambah `pre_score` + `pre_max_score` **hanya untuk post** (Tahap 3b; `passing_score` tak lagi dikirim). Sudah dikirim atau dibatalkan → 409; lewat batas waktu → 409 dan percobaan **hangus** (boleh mengulang); percobaan orang lain → 404; (Tahap 3b) **pre kedua** untuk kelas yang sama padahal sudah ada pre terkirim → 409; **post** yang pre pembandingnya tak ditemukan (mis. dibatalkan sesudah post dimulai) atau ber-`max_score` 0 → 409 |
| PATCH | `/attempts/:id/void` | manage | `{reason}` wajib. Menandai batal **tanpa menghapus** barisnya. Membatalkan **pre** ikut membatalkan post terkirim yang bersandar padanya (Tahap 3b), lihat catatan di bawah |

- Tanpa header identitas, kelima rute (termasuk `/me/pre-test/:trainingId/start`) membalas **401** sebelum handler jalan (`me_posttest.go:40-59`).
- Penilaian memakai **snapshot** soal yang dibekukan saat percobaan dimulai.
- **Kelulusan (Tahap 3b, merged 2026-09-17 lewat bip-erp PR #1934)**: `passing_score` dibuang. Post lulus bila persentasenya **lebih tinggi** daripada pre pembanding, dihitung lewat perkalian silang `skorPost × maksPre > skorPre × maksPost` tanpa pembagian (`NaikDariPreTest`, `skoring.go:60-65`). Sama persis **tidak** naik; `max_score` nol di sisi mana pun tidak naik. Pre-test tak punya kelulusan, `passed` selalu `false` untuk pre (`me_posttest.go:571-574`). Pembandingnya percobaan pre yang terkirim dan tidak dibatalkan milik orang + kelas + materi yang sama; bila lebih dari satu, yang paling awal dikirim (`ambilPreTerkirim`, `me_posttest.go:337-357`; baseline dicek di `me_posttest.go:597-619`, penolakan pre kedua di `me_posttest.go:576-596`). Nama field `passed` sengaja dipertahankan karena sertifikat menyaring lewat field itu (`me_posttest.go:665-679`).
- **Kunci per KELAS (Tahap 3b)**: gerbang pre-test, baseline, kuota, jeda, dan "sudah lulus" seluruhnya disaring `training_id`, bukan hanya `course_id` (`me_posttest.go:123-131`, `me_posttest.go:337-346`). Orang yang mengikuti materi yang sama di dua kelas mengerjakan pre dan post sendiri-sendiri di tiap kelas.
- ⚠️ **Peserta yang melewatkan pre-test sampai kelas `Completed` buntu permanen** untuk post-test kelas itu: post menuntut pre terkirim, pre menolak kelas `Completed`, dan `Completed` terminal. Diterima sadar pemilik proses 2026-09-16; penangkalnya di depan (pre-test terlihat sejak kelas dijadwalkan, HR menagih sebelum kelas ditutup) (`skoring.go:77-85`, `skoring.go:96-98`, `skoring.go:125-127`, `models_training.go:219-227`).
- **Pembatalan pre merambat (Tahap 3b, merged 2026-09-17 lewat bip-erp PR #1934)**: `PATCH /attempts/:id/void` atas percobaan pre ber-`training_id` ikut membatalkan seluruh percobaan post yang **terkirim** dan belum dibatalkan milik orang + kelas + materi yang sama. `voided_by` diisi **pembatal pre-nya** (bukan `system`, jadi kuota post kembali) dan `void_reason` menyebut alasan pembatalan pre; sesudahnya sertifikat peserta diperiksa ulang. Best-effort: galat perambatan tak membatalkan pembatalan pre (`rambatkanPembatalanKePost`, `me_posttest.go:703-718`; dipanggil di `me_posttest.go:752-768`). ⚠️ Kuota yang kembali itu praktis tak terpakai: post terkirim hanya ada pada kelas `Completed`, dan pre-test tak bisa diulang di kelas `Completed`, jadi sesudah pre dibatalkan post-test kelas itu tertutup bagi orangnya (buntu yang sama dengan butir di atas).
- `/me/post-test/attempt/:id` (POST maupun GET) didaftarkan sebelum `/me/post-test/:trainingId/start` supaya `attempt` tak ter-match sebagai `trainingId`.
- `sisa_detik` **-1 = tanpa batas waktu**, bukan "habis". Rute lanjutkan mengubah nol jadi 409, jadi klien tak pernah benar-benar menerima nol. Kedua rute merakitnya lewat fungsi yang sama supaya artinya tak bisa menyimpang; sebelum 2026-09-16 rute `start` tak mengirimkannya sama sekali, dan penunjuk mundur di klien karena itu membaca "tanpa batas" sepanjang percobaan pertama.
- ⛔ **Percobaan yang dihanguskan SISTEM karena lewat batas waktu TETAP memakan kuota** dan tetap menahan jeda; yang **dibatalkan HR** tidak, sebab mengembalikan kesempatan justru satu-satunya guna pembatalan. Pembedanya `voided_by == "system"` (konstanta `PembatalSistem`), bukan ada-tidaknya `voided_at`. Tanpa pembedaan itu `max_attempt` tak mengikat sama sekali untuk kuis berbatas waktu: mulai, biarkan waktunya habis, tekan Kirim, mulai lagi — berulang tanpa batas.
- ⚠️ **Utang yang diketahui**: penjagaan kuota masih baca-periksa-tulis (`FindMany` → aturan → `InsertOne`) tanpa unique index di `quiz_attempt`, jadi dua permintaan Mulai yang tiba berbarengan sama-sama lolos dan menghasilkan dua baris ber-`attempt_no` sama. Indeks `quiz` di service yang sama sengaja unik dengan alasan yang persis ini.

## Sertifikat Pelatihan

✅ Sudah di `origin/main` (diukur 2026-09-16: `git grep certificate-settings origin/main -- services/learning` menemukan `sertifikat.go`, `training.go`, dan tiga berkas uji; kontrol negatif string karangan nol hit). Sumber: `services/learning/sertifikat.go`, `models_sertifikat.go`, `sertifikat_pdf.go`.

| Method | Path | Izin | Fungsi |
|---|---|---|---|
| GET | `/training/certificate-settings` | view, fallback `RequireHRISStaff` | Penanda tangan sertifikat perusahaan pemanggil |
| PUT | `/training/certificate-settings` | manage, fallback `RequireHRISStaff` | Simpan `{penanda_tangan_nama, penanda_tangan_jabatan}`; memicu penerbitan tertunda utk maksimal 50 kelas `Completed` terbaru |
| GET | `/training/certificates/:certId/pdf` | view, fallback `RequireHRISStaff` | Unduh PDF (HR). Sertifikat dicabut → 410 |
| GET | `/training/:id/certificates` | view, fallback `RequireHRISStaff` | Status sertifikat tiap peserta kelas, dihitung LIVE |
| POST | `/training/:id/certificates/sync` | work, fallback `RequireHRISStaff` | Terbitkan yang berhak/tertunda dan cabut yang gugur, manual |
| GET | `/me/trainings/:id/certificate` | identitas peserta | Unduh PDF sertifikat aktif milik pemanggil sendiri. Belum terbit → 404 |

Fallback `RequireHRISStaff` (bukan `nil`) pada kelima rute HR: lihat catatan di § Gerbang izin.

- Sertifikat **terbit otomatis**: kelas `Completed` dan (tanpa `course_id` → hadir; ber-`course_id` → lulus post-test **di kelas itu** atas course yang tertaut sekarang) (`syaratSertifikat`, `models_sertifikat.go:129-157`). Sejak Tahap 3b (merged 2026-09-17, bip-erp PR #1934) "lulus" berarti field `passed` yang kini diisi aturan naik-dari-pre-test, lihat § Pre-test & Post-test.
- Status per peserta (`status`): `terbit`, `tertunda`, `tidak_berhak`, `dicabut` (`models_sertifikat.go:41-45`).
- Kode alasan (`alasan_kode`): `kelas_belum_selesai`, `tidak_hadir`, `belum_lulus_post_test`, `penanda_tangan_belum_diatur`, `nama_peserta_tak_terbaca`, `belum_diterbitkan`, `peserta_dihapus`, dan dua yang khusus status LIVE — **`syarat_gugur`** (sertifikat masih aktif tapi syaratnya sudah gugur, mis. kehadiran dikoreksi; hanya tampil di `GET /training/:id/certificates`, tak pernah disimpan) dan **`kelas_dihapus`** (jaring pengaman sesudah kelas dihapus) (`models_sertifikat.go:47-61`).
- `DELETE /training/:id` dibalas **409** bila kelasnya sudah menerbitkan sertifikat aktif (`training.go:485-499`).
- Nomor `NNN/SERT/<company_id>/<romawi bulan>/<tahun terbit WIB>`, tak pernah dipakai ulang; format **belum dikonfirmasi HR** (`formatNomorSertifikat`, `models_sertifikat.go:161-168`).
- Rincian lengkap (state machine terbit/cabut, privasi snapshot, index unik, pemicu sinkron otomatis): [[Microservices - Learning Service]].

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
| `pendaftaran[]` | Satu baris per pendaftaran pada kelas `Completed` yang `end_date`-nya di periode itu, disaring ke `company_id` dan `employee_id` yang diminta, diurutkan `training_id` lalu `employee_id`: `training_id`, `employee_id`, `hadir`, `wajib_post_test` (kelas punya `course_id`), `skor_terbaik_persen` (skor tertinggi dari percobaan post-test yang dikirim dan tidak dibatalkan; `null` bila belum ada atau kelasnya tanpa post-test), `skor_pre_persen`, `naik_dari_pre` (keduanya Tahap 3b, rincian di bawah tabel) |
| `evaluasi` | `{responden, jumlah_nilai}` untuk kelas dan karyawan yang sama; `jumlah_nilai` = total empat aspek seluruh responden, jadi rata-rata per aspek = `jumlah_nilai / (responden × 4)`. **Tanpa** identitas penilai dan **tanpa** ambang responden: ambangnya diterapkan pemanggil atas gabungan batch |

**Tahap 3b (merged 2026-09-17, bip-erp PR #1934)**, tambahan pada tiap baris `pendaftaran`:

- `skor_pre_persen` (`*float64`): persen pre-test pembanding, yaitu percobaan pre sah (terkirim, tidak dibatalkan, `max_score` > 0) yang **paling awal** dikirim; waktu kirim yang sama diputus `_id` terkecil supaya pilihannya deterministik (`skorPrePersen`, `kpi_pelatihan.go:176-204`). `null` = belum mengerjakan pre-test.
- `naik_dari_pre` (`*bool`) **tiga keadaan**: `true` (skor post terbaik > pre, dibandingkan dalam persen), `false` (tidak naik), `null` (pre atau post belum ada, jadi belum bisa dinilai, bukan gagal) (`naikDariPrePersen`, `kpi_pelatihan.go:215-221`). Perbandingannya atas persen `float64`, bukan perkalian silang bilangan bulat seperti `passed` di rute kirim jawaban.
- Kedua field hanya diisi bila `wajib_post_test`; kelas tanpa `course_id` mengirim keduanya `null` (`kpi_pelatihan.go:268-272`).
- Pemilihan percobaan untuk `skor_terbaik_persen` maupun `skor_pre_persen` menyaring `course_id` = course kelas sekarang, supaya kelas yang ditautkan ulang ke materi lain tak membandingkan bank soal lama dengan yang baru (`kpi_pelatihan.go:145-157`, `kpi_pelatihan.go:183-185`). Kueri percobaannya menarik kedua jenis; penyaringan jenis dikerjakan fungsi murni (`kpi_pelatihan.go:314-326`).

🔜 **Tambahan T2 ADR 0102** (branch `feat/learning-kesesuaian-materi`, belum PR, belum merged per 2026-09-17; rujukan baris dari branch itu):

| Field | Isi |
|---|---|
| `pendaftaran[].bulan_mulai`, `pendaftaran[].bulan_selesai` | Bulan kalender **WIB** `YYYY-MM` dari `start_date` dan `end_date` kelas (`bulanWIB`, `kpi_pelatihan.go:162`). Tanggal kosong = `""`. Bahan metrik kenaikan skor KPI peserta: bulan sebelum mulai dibanding bulan sesudah selesai |
| `kesesuaian` | `{responden, jumlah_nilai}` dari jawaban `kesesuaian_materi` yang sah (1..10) untuk kelas dan karyawan yang sama, dengan dedupe yang sama dengan `evaluasi`. **Selalu** dikirim, juga saat nol responden: kunci yang absen berarti learning versi lama. **Tanpa** ambang responden |

- ⛔ `kesesuaian` **sejajar** dengan `evaluasi`, bukan bagiannya: jangan menjumlahkan `jumlah_nilai`-nya ke `evaluasi.jumlah_nilai` dan jangan membaginya dengan `× 4`. Skala keduanya pun berbeda (satu pertanyaan 1..10 lawan empat aspek 1..5).
- Rata-rata kesesuaian = `jumlah_nilai / responden`, dihitung pemanggil sesudah seluruh batch digabung.

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

Endpoint LMS lanjutan **belum ada**: materi PDF & video pada course, kurikulum jabatan, tenggat, Talent Pool. **Pre-test sudah ada di `main`** (Tahap 3b, merged 2026-09-17 lewat bip-erp PR #1934), lihat § Pre-test & Post-test (peserta) dan § Course & Bank Soal. Desainnya di [[HRIS - Training Program]]. Bahan KPI (`/kpi/pelatihan`) dan feed kalender (`/internal/calendar-feed`) sudah ada sejak 2026-09-15, lihat bagian masing-masing di atas.

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

✅ **Layarnya sudah merged** (diukur `gh pr view` 2026-09-17). Tahap 3a: bip-erp **#1913** (rute lanjutkan percobaan, batas mengulang, penanda `post_test_*`), erp-frontend **#1603** (menu Materi E-Learning, bank soal, rekaman percobaan, layar peserta), my-bharata **#151** (layar peserta di ponsel), merged 2026-09-16. Tahap 3b (pre-test, kelulusan naik dari pre-test, kunci per kelas): bip-erp **#1934**, erp-frontend **#1619**, my-bharata **#153**, merged 2026-09-17. Kedua PR my-bharata merged ke **`dev`**, jadi layar ponsel belum sampai ke orang sebelum rilis store. Angka 0 dokumen di atas adalah hitungan sebelum merge; pengukuran deploy prod dan isi koleksi terbaru ada di [[HRIS - Matriks KPI per Departemen]]. Rute course/post-test belum tercatat pernah dipanggil lewat gateway di dok ini.

## Dokumen Terkait

- [[Microservices - Learning Service]] · [[HRIS - Training Program]]
- [[API - Employee Service]] — rumah lama endpoint ini · [[API - Index]]
- [[CORE - API Master Gateway]]
