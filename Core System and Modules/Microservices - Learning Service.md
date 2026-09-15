## Deskripsi

*Rumah modul **pelatihan karyawan**, sekaligus fondasi **LMS People Development** yang akan dibangun di atasnya. Service ini lahir dari **LMS Fase 0**: memindahkan modul Training dari [[Microservices - Employee Service]] apa adanya, tanpa perubahan yang terlihat pengguna. Dari fitur LMS-nya, yang sudah ada baru **course tipis dan post-test berskor** (merged 2026-08-20); materi, pre-test, kurikulum jabatan, dan Talent Pool **belum ada**. Lihat Belum Diimplementasikan.*

- **Stack:** Go + Fiber v2 + MongoDB (`learning_db`), discaffold dari `services/.template`
- **Path:** `services/learning`
- **Port internal:** 6987 · **Modul gateway:** `learning` (`/api/learning/*`)
- **Status**: ⚠️ **Implemented (ada catatan)** — service **live di dev + produksi 2026-08-06** (bip-erp PR [#1020](https://github.com/bip-itteam-internal/bip-erp/pull/1020), frontend [erp-frontend#814](https://github.com/bip-itteam-internal/erp-frontend/pull/814)), data 4 koleksi dipindah di kedua lingkungan dengan jumlah terverifikasi cocok, dan pengajuan + evaluasi + `/me` **terverifikasi lewat gateway hidup 2026-08-19**. Post-test berskor (PR [#1321](https://github.com/bip-itteam-internal/bip-erp/pull/1321), merged 2026-08-20) **ada di biner produksi** (diperiksa 2026-09-15). **Catatannya bukan di service melainkan di pemakaiannya**: per 2026-09-15 `training_request`, `trainer_evaluation`, dan `quiz_attempt` di produksi masih **0**, post-test belum punya layar di web maupun MyBharata, dan belum ada sumber KPI yang membaca `learning_db`. Materi, pre-test, kurikulum, dan Talent Pool **belum ada**. Konsep & rencana lanjutan: [[HRIS - Training Program]]

## Kenapa service sendiri

Modul Training dulu menumpang Employee Service. Dipindah karena LMS menuntut **kelas tatap muka dan belajar mandiri berbagi satu angka progres**; bila keduanya tinggal di service berbeda, tiap perhitungan progres jadi panggilan lintas-service. Sesuai [[ADR - 0002 Database-per-Service]], modul baru = service + database sendiri.

Service ini **tidak menyimpan** master karyawan, jabatan, maupun departemen. Semuanya tetap milik [[Microservices - Employee Service]] dan dibaca lewat panggilan internal.

## Endpoint / Fitur (Sudah Diimplementasikan)

Daftar lengkap: [[API - Learning Service]] (per 2026-09-15 rute course dan post-test belum tercantum di sana; daftarnya ada di bagian Post-test di bawah). Ringkasnya delapan kelompok; empat pertama pindahan utuh dari Employee Service, sisanya dibangun di service ini:

- **Master jenis pelatihan** — CRUD `/training/types`
- **Master trainer** — CRUD `/training/trainers`, internal (tautan `employee_id`) atau eksternal
- **Event pelatihan** — CRUD `/training` dengan filter `?department_key=&status=`, guard transisi status (Scheduled → Ongoing → Completed, atau → Cancelled), hapus cascade ke peserta
- **Peserta & kehadiran** — `/training/:id/participants` (unique index `{training_id, employee_id}` anti-duplikat, **cap kapasitas ditegakkan sejak 2026-08-10**; 0 = tanpa batas), kehadiran boolean, `/training/history/:employeeId`
- **Pengajuan pelatihan** — `/training/requests` (rantai SPV → HR), lihat bagian tersendiri di bawah
- **Evaluasi trainer** — `POST /me/trainings/:id/evaluation` (peserta mengisi) + `GET /training/:id/evaluation` & `/training/trainers/:id/evaluation` (agregat), lihat bagian tersendiri di bawah
- **Course & bank soal post-test**: `/courses`, `/courses/:id/quiz`, rekap dan ekspor CSV percobaan, lihat bagian Post-test di bawah
- **Mengerjakan post-test**: `POST /me/post-test/:trainingId/start`, `POST /me/post-test/attempt/:id`, pembatalan `PATCH /attempts/:id/void`

RBAC: baca digerbang `PermTrainingView`; tulis digerbang `PermTrainingWork` (event, peserta) atau `PermTrainingManage` (master, course, soal), ditambah `RequireHRISStaff`. Rute `/me/*` dan pembuatan pengajuan tidak digerbang izin modul; yang menggerbang identitas pemanggil dan relasinya (lihat bagian masing-masing). Fungsi validasi murni (`ValidateTraining`, `CanEnroll`, `IsValidStatusTransition`, `validateTrainer`) beserta ujinya ada di `services/learning/models_training.go` dan `models_training_test.go`.

### Verifikasi departemen lewat panggilan internal

Satu-satunya perilaku yang **berubah** saat pemindahan. Sebelumnya `verifyTrainingRefs` mengueri koleksi `master_department` langsung dengan `mongodb.FindOne`. Koleksi itu milik Employee Service, jadi setelah pindah kueri tersebut mengarah ke `learning_db` dan **selalu gagal** — setiap pelatihan yang mengisi departemen akan ditolak "department not found".

Diganti panggilan `GET {EMPLOYEE_MODULE_URL}/master/departments/{key}` lewat `routes.InternalRequest`. Tiga hal yang menyertainya:

- ⚠️ **`EMPLOYEE_MODULE_URL` dibaca langsung `os.Getenv`, TIDAK masuk map `InternalURL`.** `validation.ValidateInternalURL` panic pada entri kosong, sehingga menaruhnya di sana berarti seluruh service mati saat env belum terisi. Pola dan alasannya sama dengan [[Microservices - Form Builder Service]].
- Kunci departemen di-escape dengan `url.PathEscape`. Tanpa itu `department_key = "IT?bogus=1"` lolos verifikasi karena `?bogus=1` terlepas jadi query, dan nilai palsu itu tersimpan sebagai departemen yang tak pernah ada.
- Pemetaan hasil dipisah tegas dan diuji sebagai fungsi murni: 2xx lolos, **404 → 400** (departemen memang tidak ada), **status lain / galat transport / env kosong → 502**. Menyebut departemen tidak ada padahal service-nya tak terjangkau akan menyesatkan pembacanya, dan mencatat gangguan server sebagai kesalahan klien membuat pemantauan 5xx tak menyala.

## Pengajuan pelatihan — ✅ merged 2026-08-10 (PR [#1148](https://github.com/bip-itteam-internal/bip-erp/pull/1148))

Sampai sebelum ini **semua penjadwalan berangkat dari HR**; karyawan dan atasan tak punya jalan masuk sama sekali. Koleksi `training_request`, rantai **SPV → HR**.

⚠️ **DUA tahap, bukan tiga seperti rencana lama di dokumen ini.** Alasannya ada di rumah sendiri: [[HRIS - Recruitment]] pernah memakai bentuk persis SPV → SPV HRD → Direktur lalu **membuang tahap Direktur**, menyisakan status `HR Reviewed` yang sengaja dipertahankan supaya requisition lama tak nyangkut permanen. Meminta pelatihan lebih ringan daripada meminta tambahan karyawan; membuatnya lebih berat akan terbalik. `estimated_cost` tetap disimpan sehingga ambang biaya (Direktur hanya untuk pengeluaran besar) bisa ditambahkan **tanpa migrasi**.

- **`employee_id` (untuk siapa) dipisah dari `requested_by` (siapa menekan tombol)** supaya SPV bisa mengusulkan untuk anggota timnya tanpa pengajuan itu terbaca seolah si anggota yang meminta.
- **Supervisor dicari SEKALI saat pengajuan dibuat lalu dipaku ke slot.** Menghitung ulang tiap pembacaan membuat pengajuan berpindah antrean diam-diam saat supervisor berganti, dan orang yang sudah menyetujui kehilangan jejaknya.
- **Departemen tanpa supervisor ditolak** beserta sebabnya, bukan disimpan diam-diam jadi pengajuan yang menggantung selamanya.
- **Pengaju yang ternyata supervisor departemen itu sendiri melewati tahap SPV** — antrean yang menunggu tanda tangan diri sendiri tak pernah selesai.
- **Penolakan di tahap mana pun FINAL.** Kalau penolakan SPV diteruskan, HR menerima hal yang atasannya sudah tolak, dan persetujuan di atasnya membatalkan keputusan atasan tanpa ada yang menyadarinya.
- **Tahap ditentukan STATUS, bukan dikirim klien**; kalau klien memilih tahap, siapa pun yang tahu bentuk permintaannya bisa mengaku menindak tahap HR. Dan tak seorang pun memutus pengajuannya sendiri.
- **Membuat pengajuan tak digerbang izin modul**: meminta pelatihan bukan hak mengelola pelatihan. Yang menggerbang identitas.
- **Notifikasi memakai kategori `request-*` yang SUDAH ADA**, bukan kategori baru — jadi **tanpa deploy dua container** dan tanpa perubahan MyBharata. `request-waiting-review` sengaja dihindari walau terdaftar: MyBharata memetakan `request-review`, bukan nama itu, sehingga ia jatuh ke `system`.
- ⚠️ **`app_route` notifikasinya sempat berisi rute WEB** (`/hris/training/requests`) sejak fitur ini lahir. Field itu dibaca MyBharata untuk menentukan layar yang dibuka, dan aplikasi tak punya satu pun rute berawalan `/hris/`, jadi deep link-nya tak pernah bisa mendarat. Diperbaiki jadi `/pengajuan-pelatihan` di PR [#1198](https://github.com/bip-itteam-internal/bip-erp/pull/1198) bersama pindahnya sisi pengajuan ke aplikasi. **Nilainya harus sama persis dengan `RouteNames.trainingRequests`** di my-bharata; tak ada apa pun yang memaksa keduanya sejalan, jadi masing-masing repo mengunci nilainya lewat test, dan yang di sini menolak awalan `/hris/` secara eksplisit alih-alih sekadar mencocokkan satu nilai. Berkas `request_notify.go` sebelumnya tak punya satu pun test.
- ⚠️ **Deep link itu belum benar-benar hidup.** `/inbox/send` di notification-service HANYA menyimpan dokumen inbox, tanpa push FCM, dan daftar notifikasi di MyBharata belum menavigasi ke mana pun. Perbaikan di atas menjadikan datanya benar, bukan menjadikan tautannya berfungsi. Detail: [[APP - MyBharata]].

## Evaluasi pasca-pelatihan — ✅ merged 2026-08-10 (PR [#1149](https://github.com/bip-itteam-internal/bip-erp/pull/1149))

Koleksi `trainer_evaluation`. **Peserta menilai trainer**, empat aspek tetap (penguasaan materi, cara menyampaikan, penguasaan kelas, manfaat) masing-masing 1..5 plus komentar. Bentuknya khusus, **bukan** form builder — melanjutkan keputusan sama di Recruitment, sebab pertanyaan bebas menghasilkan jawaban yang tak bisa dibandingkan antar pelatihan.

**Privasi adalah inti desainnya**, bukan pelengkap:

- `employee_id` disimpan (mencegah penilaian ganda, tahu siapa belum mengisi) tapi ber-tag `json:"-"` sehingga **tak pernah keluar di respons**. Trainer internal bisa jadi atasan pesertanya sendiri; kalau penilai bisa dilacak, nilainya akan bagus semua dan datanya tak berguna.
- **Agregat baru tampil setelah minimal TIGA responden.** Dengan satu atau dua penilai, identitasnya bisa ditebak dari jumlahnya saja.
- Di bawah ambang, **angkanya dikirim NOL**, bukan cuma penandanya dimatikan — klien yang lupa membaca penanda tak boleh punya angka untuk ditampilkan. Jumlah responden tetap dikirim, sebab "belum ada yang mengisi" dan "sudah dua orang" dua keadaan berbeda bagi HR yang menunggu.

Penjaga lain: hanya **peserta** yang boleh menilai, hanya pelatihan **`Completed`**, satu peserta satu penilaian lewat **index unik** (pemeriksaan handler saja lolos pada pengiriman berbarengan), dan rata-rata dihitung dari nilai **mentah** bukan dari rata-rata yang sudah dibulatkan.

## Layar karyawan (`/me/trainings`) — ✅ merged 2026-08-11 (PR [#1150](https://github.com/bip-itteam-internal/bip-erp/pull/1150))

`MeTraining` kini membawa `trainer_id`, `trainer_name`, `sudah_dinilai`, dan `boleh_menilai`.

Sebelum ini layar penilaian tak bisa dibuat benar: tanpa penanda sudah-dinilai, satu-satunya cara mengetahuinya adalah **mengirim penilaian lalu ditolak 409**, sehingga tombol muncul di setiap pelatihan selesai termasuk yang sudah dinilai.

- **`boleh_menilai` dihitung SERVER**, mengikuti alasan yang sama dengan `can_attend`: aturannya sudah hidup di `BolehMenilaiPelatihan`, dan menyalinnya ke klien melahirkan salinan ketiga setelah Go dan TypeScript — di aplikasi, salinan yang menyimpang baru bisa diperbaiki lewat rilis baru ke store.
- **Kedua penanda TANPA `omitempty`.** Dengan `omitempty`, nilai `false` hilang dari respons dan klien tak bisa membedakan "tidak boleh" dari "server lama yang belum punya field ini".
- **Dua kueri pengaya gagal-TERBUKA**: galat baca dicatat lalu dilewati, tak menggagalkan layar dan tak menutup tombol. Index unik tetap penjaga sebenarnya.

## ✅ Bug: pencarian supervisor memakai KEY, bukan NAMA — diperbaiki PR [#1153](https://github.com/bip-itteam-internal/bip-erp/pull/1153), **merged 2026-08-11**

Kelas bug yang sudah berulang di repo ini: **dua satuan berbeda untuk hal yang terdengar sama**.

`department_key` adalah **key** (`master_department.key`, mis. `it`), sedangkan `work_data.department` menyimpan **nama** (`Tech Development`). `supervisorDepartemen` mengirim key ke `/list?type=supervisor&department=`, padahal di sana `SupervisorLookupOrder` mencocokkan `d.Name`. Hasilnya nol supervisor, lalu pengajuan dibalas **409 "departemen belum punya supervisor"** — galat yang menuduh data master padahal yang salah satuan nilainya.

Diperiksa pada data dev: **6 dari 10 departemen punya key ≠ name** (`hris`/Human Resource, `ga`/General Affair, `it`/Tech Development, `secretary`/Kesekretariatan, `beauty_hacks`/Beauty Hacks, `manufacture`/Manufaktur). Untuk keenamnya pengajuan pelatihan **mustahil dibuat**. Empat sisanya (Finance, Kyura, Quality, Procurement) jalan hanya karena kebetulan key-nya sama dengan namanya — itulah yang membuatnya tampak "kadang jalan".

Sekalian di PR yang sama: **`department_key` jadi OPSIONAL**, kosong berarti "departemen saya" dari header `BIP-Department`. Tanpa itu MyBharata tak bisa mengajukan sama sekali — aplikasi tak punya endpoint master departemen dan profilnya hanya menyimpan nama, jadi memaksanya mengirim key membuat tiap klien menyalin pemetaan nama↔key, persis duplikasi yang melahirkan bug ini.

⚠️ **Key yang SALAH sengaja tidak jatuh ke pencocokan nama.** Menebaknya akan menyembunyikan klien yang mengirim satuan keliru.

## Post-test pelatihan: ✅ merged 2026-08-20 (PR [#1321](https://github.com/bip-itteam-internal/bip-erp/pull/1321))

Irisan LMS pertama yang benar-benar ada: **bukti kompetensi sesudah kelas**. Tiga koleksi baru: `course`, `quiz`, `quiz_attempt`.

- **`course` sengaja tipis**: judul, deskripsi, `passing_score` (0..100), `is_active`. Ia ada supaya post-test punya tempat menggantung yang bisa dirujuk kelas tatap muka maupun belajar mandiri nanti; menempelkan soal langsung ke `training` akan membuat soal yang sama hidup dua kali begitu jalur mandiri dibangun. Materi PDF dan video belum ada. `passing_score` 0 berarti **tanpa ambang**, bukan mustahil lulus.
- **Kelas menautkan course lewat `training.course_id`**, dan kosong itu sah: kelas tanpa post-test.
- **Bank soal tinggal di koleksi TERPISAH dari course**, supaya membaca course tak pernah berpotensi mengirim kunci jawaban. `Question.MarshalJSON` membuang `correct_index` dari setiap serialisasi JSON; hanya `GET /courses/:id/quiz` (izin kelola) yang merakit bentuk khusus berisi kunci (`quizUntukPengelola`).
- ⚠️ **`correct_index` sempat mustahil disetel lewat API.** Versi awal memakai tag `json:"-"`, yang di Go berlaku **dua arah**: `BodyParser` ikut membuang nilai kiriman HR sehingga setiap soal tersimpan berkunci opsi pertama, dan `ValidateQuiz` meloloskannya karena 0 indeks yang sah. Tak satu pun dari 144 test menangkapnya karena semuanya merakit struct literal tanpa decode JSON; ketahuan lewat satu siklus sungguhan di gateway dev. Diperbaiki commit `1e664ef5` dengan memindahkan penjaganya ke marshaller, yang hanya menyentuh arah keluar.
- **Syarat memulai** (`BolehMengerjakanPostTest`, `skoring.go`): terdaftar sebagai peserta, kelasnya punya `course_id`, status kelas **`Completed`**, dan belum pernah lulus. Saklar `attendance_open` sengaja tidak dipakai bersama: kehadiran dibuka saat sesi, post-test sesudahnya.
- **Soal dan identitas DIBEKUKAN saat percobaan dimulai** (`questions_snapshot`, dan `identity_snapshot` dari header yang distempel gateway). Penilaian memakai snapshot, jadi nilai lama tetap bisa dipertanggungjawabkan sesudah HR memperbaiki soal, dan berkas audit tak ikut berubah saat orangnya pindah jabatan. `training_id` dicatat, bukan diturunkan dari tanggal.
- **Skor dalam poin** (`score` terhadap `max_score`), lulus bila `score × 100 ≥ passing_score × max_score`. Soal yang tak dijawab dihitung salah; untuk jawaban ganda pada satu soal, yang pertama menang.
- **Percobaan terkunci sesudah dikirim** (409 bila dikirim ulang). Batas waktu ditegakkan server dari `started_at`; lewat batas berarti **hangus** (`voided_by: system`) dan boleh diulang, bukan dinilai dari jawaban separuh jalan. Koreksi ditempuh lewat **pembatalan bertanda alasan** (`PATCH /attempts/:id/void`), baris aslinya tetap ada.
- **Rekap dan ekspor CSV** untuk auditor. Nilai berawalan `=`, `+`, `-`, `@` dinetralkan supaya tak terbaca sebagai formula di spreadsheet. Course yang sudah punya percobaan **tak bisa dihapus** (409; nonaktifkan lewat `is_active`).

| Method | Path | Gerbang izin |
|---|---|---|
| GET · POST | `/courses` | view · manage |
| GET · PUT · DELETE | `/courses/:id` | view · manage · manage |
| GET · PUT | `/courses/:id/quiz` | manage (GET pun, karena memuat kunci) |
| GET | `/courses/:id/attempts` · `/courses/:id/attempts/export` | work |
| POST | `/me/post-test/:trainingId/start` · `/me/post-test/attempt/:id` | identitas peserta |
| PATCH | `/attempts/:id/void` | manage |

Rute kelola dan rekap juga menuntut `RequireHRISStaff`. Grup `/courses` sengaja **tidak** diletakkan di bawah `/training`: segmen statik sesudah `/training/:id` akan ter-match sebagai event ber-id `courses`.

⚠️ **Terpasang di produksi, belum punya layar, belum dipakai.** Biner `Learning-Service` prod (image 2026-09-14) memuat `/me/post-test`, `quiz_attempt`, dan `attempts/export`, dengan kontrol negatif string karangan → 0 (diperiksa 2026-09-15). Tetapi `erp-frontend` `main` dan `my-bharata` `dev` sama-sama **nol** pemanggil `/courses` maupun `/me/post-test` (komentar `home_quick_access.dart` di aplikasi menyebut isinya "BELUM LMS penuh (course, materi, post-test)"), dan per 2026-09-15 koleksi `course` **belum pernah terbentuk**, `quiz` 0, `quiz_attempt` 0. Konsekuensinya, metrik KPI yang menunggu skor training (mis. `Skor Penilaian Training All Karyawan > 70` di [[HRIS - Matriks KPI per Departemen]]) menunggu **frontend** dan **sumber KPI**, bukan backend service ini.

## Belum Diimplementasikan / Catatan

- **Sebagian besar fitur LMS belum ada.** Yang sudah: course tipis, bank soal post-test, skoring, dan rekaman percobaan (lihat Post-test di atas), serta penilaian trainer. Yang belum: materi PDF & video, **pre-test** (jenis `pre` sudah ada di `QuizKinds`, tetapi seluruh rute hanya melayani `post`), kurikulum per jabatan, tenggat, Talent Pool, dan **layar** course/post-test di web maupun MyBharata. Desainnya di [[HRIS - Training Program]].
- ⚠️ **Belum ada jalur ke mesin KPI.** Service ini tak punya rute `/internal/`, dan employee-service tak punya satu pun sumber KPI yang membaca `learning_db` (`git grep` `training|pelatihan|learning` di `services/employee/kpi_*.go` = 0 hasil, kontrol positif `tiket` = 10 berkas; diperiksa 2026-09-15). Kehadiran, skor post-test, dan evaluasi trainer karena itu belum bisa mengisi KPI siapa pun, termasuk posisi yang dinilai dari pelatihan (Training & Perfomance Officer, Culture & Industrial, HRD Supervisor). Mengisi datanya saja tidak cukup: sumber KPI-nya tetap harus ditulis dev. Lihat [[HRIS - Matriks KPI per Departemen]].
- ✅ ~~Keempat koleksi belum punya `company_id`~~ — **sudah terpasang**: baca memakai `EffectiveCompanyID`, tulis memakai `CompanyID`, dan `ReplaceOne` sengaja mempertahankannya. Aturan operasional lama "jangan beri role `hris` ke akun non-BIP" **tak lagi jadi satu-satunya penjagaan**.
- ✅ ~~Rute baca Training tidak punya gerbang role~~ — **sudah digerbang** `gate(PermTrainingView, nil)`, bersama RBAC permission-set penuh (`PermTrainingView`/`Work`/`Manage`) berikut kill-switch `TRAINING_PERMISSION_ENFORCEMENT` dan sakelar fase dua `TRAINING_TIER_FALLBACK`.
- ⚠️ **`max_participants` sempat DIKUMPULKAN tanpa pernah ditegakkan** — diperbaiki 2026-08-10 (PR [#1147](https://github.com/bip-itteam-internal/bip-erp/pull/1147)). Kolom itu disebut "cap keras" di **tiga tempat** (komentar field, komentar rute, dokumen vault) sementara `CanEnroll` tak pernah menerima kapasitasnya: HR mengisi kuota 20, orang ke-21 masuk tanpa keluhan apa pun. Pola yang sudah berulang di repo ini — dirakit benar, tak dibaca siapa pun, nol test merah. Nol/negatif = tanpa batas, dan duplikat diperiksa lebih dulu daripada kuota supaya pesannya tidak menyesatkan.
- ✅ ~~Belum ada uji level handler~~ — **21+ rute kini dikunci** lewat `app.Test` (PR #1147): ditolak tanpa identitas, izin baca tak membuka rute tulis, izin tulis tak membuka rute kelola master, penjaga prefix gateway berikut kontrol negatifnya, urutan rute statik vs `/:id`, ObjectID cacat dibalas 400, fallback tier, dan pengunci jumlah rute.
- ⚠️ **Urutan registrasi rute itu kritis dan dikunci uji.** `/training/requests` dan `/training/:id/evaluation` didaftarkan **sebelum** `registerTrainingEventRoutes`; menaruhnya sesudah `/training/:id` membuat permintaannya ter-match sebagai event ber-id "requests" lalu dibalas 400 *"id is not a valid ObjectID"* — galat yang menuduh permintaan yang benar dan paling sulit dicurigai karena pesannya terdengar masuk akal.
- `ensureTrainingIndexes` dan kedua index baru dijaga `mongodb.DB == nil`: paniknya terjadi saat **registrasi rute**, jadi tanpa itu service gagal naik sama sekali.
- Bawaan dari kode lama, belum diperbaiki: `PUT` bersifat full-replace sehingga frontend wajib mengirim objek lengkap, pendaftaran peserta belum memeriksa karyawan benar-benar ada di `work_data`, dan daftar belum berpaginasi.
- ✅ ~~Belum ada frontend untuk pengajuan maupun evaluasi~~ — **sudah ada di web** (erp-frontend [#967](https://github.com/bip-itteam-internal/erp-frontend/pull/967) & [#968](https://github.com/bip-itteam-internal/erp-frontend/pull/968), merged): `/hris/training/requests`, `/hris/pelatihan-saya`, dan agregat penilaian di halaman Pelatihan. Detail di [[APP - Web ERP]].
- ⚠️ **Sisi MENGAJUKAN pindah ke MyBharata 2026-08-13** (erp-frontend [#1022](https://github.com/bip-itteam-internal/erp-frontend/pull/1022) + my-bharata [#115](https://github.com/bip-itteam-internal/my-bharata/pull/115)). Yang tinggal di web adalah **antrean persetujuan** (`as=reviewer`/`reviewed`), menunya berganti nama jadi "Persetujuan Pelatihan" dan mulai digerbang. `/hris/pelatihan-saya` masih hidup sebagai rute dormant tanpa menu. Konsekuensi bagi service ini: **klien pengajuan kini dua**, dan aplikasi tak bisa dipaksa update — perubahan bentuk `POST /training/requests` maupun `GET /training/requests?as=self` wajib aman bagi versi app yang sudah beredar.
- ✅ ~~Seluruh fitur pengajuan & evaluasi belum pernah diverifikasi lewat gateway hidup~~ — **terverifikasi 2026-08-19**. Image `Learning-Service` dibuild ulang di **dev** (13:20) dan **produksi** (13:21); lewat gateway dev `GET /api/learning/training/requests?as=self|reviewer` dan `/api/learning/me/trainings` membalas **200**, sementara kontrol negatif `/api/learning/training/requests-karangan` tetap **400** `id is not a valid ObjectID` — prefiks sama, hasil beda, jadi yang dibuktikan memang routing-nya dan bukan balasan 200 untuk apa saja. Biner prod memuat `boleh_menilai`, `sudah_dinilai`, `pengajuan-pelatihan`, `trainer_evaluation`, `training_request`, dengan kontrol negatif string karangan → 0. Sebelum ini dev memakai image lama sejak #1148 merge sehingga `/training/requests` tertelan `/training/:id`; itulah sebab bug departemen di atas tak terlihat berminggu-minggu. Prosedur: [[RUN - Deploy Microservices bip-erp]].
- ⚠️ **Terpasang penuh tapi BELUM DIPAKAI sama sekali.** Hitungan `learning_db` produksi **2026-09-15**: `training_request` **0**, `trainer_evaluation` **0**, `quiz_attempt` **0**, `quiz` 0, koleksi `course` belum pernah terbentuk, `training` 2, `training_participant` 1 (belum hadir), `trainer` 2, `training_type` 2 (hitungan 2026-08-19: `training_request` 0, `trainer_evaluation` 0, `training` 1, `training_participant` 1, `trainer` 2, `training_type` 1). Pengajuan dan evaluasi live sejak 2026-08-11 dan post-test sejak 2026-08-20, jadi nol di ketiga koleksi itu **pertanyaan, bukan kabar baik**. Sebabnya bukan servicenya: pengajuan terhambat alur karyawan yang terputus di bawah, dan post-test belum punya layar sama sekali. Angka nol yang mencurigakan diperlakukan sebagai pertanyaan; lihat pola yang sama di [[Microservices - Form Builder Service]].
- ⛔ **Alur karyawan biasa TERPUTUS sejak 2026-08-13.** Menu self-service di web sudah dicabut sebelum penggantinya di aplikasi sampai ke orang. Per 2026-09-15: my-bharata [#115](https://github.com/bip-itteam-internal/my-bharata/pull/115) (Pengajuan Pelatihan) sudah **merged ke `dev` 2026-08-22** (belum ada di `main`, yang masih `1.14.5+135`), dan [#112](https://github.com/bip-itteam-internal/my-bharata/pull/112) (Pelatihan Saya) merged ke `dev` 2026-08-11. Apakah build yang terpasang di HP pemakai sudah memuat keduanya **belum diverifikasi**; yang terukur hanya `training_request` produksi yang masih **0**. Selama build itu belum sampai ke orang, karyawan tanpa bawahan dan tanpa izin `training.work` **tak punya satu pun jalan bermenu** untuk mengajukan pelatihan atau melihat pelatihannya sendiri; `/hris/training/requests` masih menyimpan tab `self` berikut formulirnya, tapi menunya digerbang penyetuju. Konsekuensi bagi service ini: `POST /training/requests` sudah live berminggu-minggu **tanpa satu pun pemanggil**. Lihat [[APP - Web ERP]] dan [[APP - MyBharata]].
- **Rute lama `/api/employee/training/*` masih hidup di produksi.** `employee-service` sengaja tidak di-rebuild saat cut-over agar tidak ikut mendorong perubahan orang lain ke produksi. Tidak ada pemanggil yang tersisa. Koleksi Training lama juga masih ada di `employee_db` sebagai jalan pulang.

## Dependensi & Integrasi

- **MongoDB `learning_db`** — koleksi `training_type`, `trainer`, `training`, `training_participant`, `training_request`, `trainer_evaluation`, `course`, `quiz`, `quiz_attempt`. Lihat [[DB - Overview and Notes]].
- [[Microservices - Notification Service]] — inbox pengajuan, memakai kategori `request-*` yang sudah ada.
- [[Microservices - Employee Service]] — sumber master departemen (verifikasi `department_key`) dan master karyawan untuk pemilih peserta serta trainer internal.
- [[CORE - API Master Gateway]] — modul `learning`, env `LEARNING_MODULE_URL`.
- [[APP - Web ERP]] — layar `/hris/training` dan `/hris/training/masters` di grup menu People Development.

## Dokumen Terkait

- [[HRIS - Training Program]] — konsep, desain LMS lengkap, dan rencana bertahap
- [[API - Learning Service]] · [[API - Index]]
- [[Microservices - Employee Service]] — rumah lama modul ini
- [[HRIS - Matriks KPI per Departemen]]: metrik KPI yang menunggu data modul ini (Training & Perfomance Officer, Culture & Industrial, HRD Supervisor)
- [[ADR - 0002 Database-per-Service]] · [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]
