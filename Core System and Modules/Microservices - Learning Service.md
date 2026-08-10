## Deskripsi

*Rumah modul **pelatihan karyawan**, sekaligus fondasi **LMS People Development** yang akan dibangun di atasnya. Service ini lahir dari **LMS Fase 0**: memindahkan modul Training dari [[Microservices - Employee Service]] apa adanya, tanpa perubahan yang terlihat pengguna. Fitur LMS-nya sendiri (materi, kuis, skoring, kurikulum jabatan) **belum ada** — lihat Belum Diimplementasikan.*

- **Stack:** Go + Fiber v2 + MongoDB (`learning_db`), discaffold dari `services/.template`
- **Path:** `services/learning`
- **Port internal:** 6987 · **Modul gateway:** `learning` (`/api/learning/*`)
- **Status**: ✅ **Implemented & live di dev + produksi 2026-08-06** (bip-erp PR [#1020](https://github.com/bip-itteam-internal/bip-erp/pull/1020), frontend [erp-frontend#814](https://github.com/bip-itteam-internal/erp-frontend/pull/814)). Data 4 koleksi sudah dipindah di kedua lingkungan, jumlah terverifikasi cocok. Konsep & rencana lanjutan: [[HRIS - Training Program]]

## Kenapa service sendiri

Modul Training dulu menumpang Employee Service. Dipindah karena LMS menuntut **kelas tatap muka dan belajar mandiri berbagi satu angka progres**; bila keduanya tinggal di service berbeda, tiap perhitungan progres jadi panggilan lintas-service. Sesuai [[ADR - 0002 Database-per-Service]], modul baru = service + database sendiri.

Service ini **tidak menyimpan** master karyawan, jabatan, maupun departemen. Semuanya tetap milik [[Microservices - Employee Service]] dan dibaca lewat panggilan internal.

## Endpoint / Fitur (Sudah Diimplementasikan)

Daftar lengkap: [[API - Learning Service]]. Ringkasnya empat kelompok, semuanya pindahan utuh dari Employee Service:

- **Master jenis pelatihan** — CRUD `/training/types`
- **Master trainer** — CRUD `/training/trainers`, internal (tautan `employee_id`) atau eksternal
- **Event pelatihan** — CRUD `/training` dengan filter `?department_key=&status=`, guard transisi status (Scheduled → Ongoing → Completed, atau → Cancelled), hapus cascade ke peserta
- **Peserta & kehadiran** — `/training/:id/participants` (unique index `{training_id, employee_id}` anti-duplikat, **cap kapasitas ditegakkan sejak 2026-08-10**; 0 = tanpa batas), kehadiran boolean, `/training/history/:employeeId`
- **Pengajuan pelatihan** — `/training/requests` (rantai SPV → HR), lihat bagian tersendiri di bawah
- **Evaluasi trainer** — `POST /me/trainings/:id/evaluation` (peserta mengisi) + `GET /training/:id/evaluation` & `/training/trainers/:id/evaluation` (agregat), lihat bagian tersendiri di bawah

RBAC tulis = `RequireHRISStaff`; GET terbuka di belakang gateway. Fungsi validasi murni (`ValidateTraining`, `CanEnroll`, `IsValidStatusTransition`, `validateTrainer`) beserta ujinya ada di `services/learning/models_training.go` dan `models_training_test.go`.

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

## Evaluasi pasca-pelatihan — ✅ merged 2026-08-10 (PR [#1149](https://github.com/bip-itteam-internal/bip-erp/pull/1149))

Koleksi `trainer_evaluation`. **Peserta menilai trainer**, empat aspek tetap (penguasaan materi, cara menyampaikan, penguasaan kelas, manfaat) masing-masing 1..5 plus komentar. Bentuknya khusus, **bukan** form builder — melanjutkan keputusan sama di Recruitment, sebab pertanyaan bebas menghasilkan jawaban yang tak bisa dibandingkan antar pelatihan.

**Privasi adalah inti desainnya**, bukan pelengkap:

- `employee_id` disimpan (mencegah penilaian ganda, tahu siapa belum mengisi) tapi ber-tag `json:"-"` sehingga **tak pernah keluar di respons**. Trainer internal bisa jadi atasan pesertanya sendiri; kalau penilai bisa dilacak, nilainya akan bagus semua dan datanya tak berguna.
- **Agregat baru tampil setelah minimal TIGA responden.** Dengan satu atau dua penilai, identitasnya bisa ditebak dari jumlahnya saja.
- Di bawah ambang, **angkanya dikirim NOL**, bukan cuma penandanya dimatikan — klien yang lupa membaca penanda tak boleh punya angka untuk ditampilkan. Jumlah responden tetap dikirim, sebab "belum ada yang mengisi" dan "sudah dua orang" dua keadaan berbeda bagi HR yang menunggu.

Penjaga lain: hanya **peserta** yang boleh menilai, hanya pelatihan **`Completed`**, satu peserta satu penilaian lewat **index unik** (pemeriksaan handler saja lolos pada pengiriman berbarengan), dan rata-rata dihitung dari nilai **mentah** bukan dari rata-rata yang sudah dibulatkan.

## Belum Diimplementasikan / Catatan

- **Seluruh fitur LMS belum ada.** Course, materi PDF & video, bank soal, pre/post test, skoring otomatis, kurikulum per jabatan, tenggat, Talent Pool — semuanya Fase 1 ke atas. Desainnya lengkap, lihat [[HRIS - Training Program]]. **Penilaian trainer sudah ada** (lihat di atas).
- ✅ ~~Keempat koleksi belum punya `company_id`~~ — **sudah terpasang**: baca memakai `EffectiveCompanyID`, tulis memakai `CompanyID`, dan `ReplaceOne` sengaja mempertahankannya. Aturan operasional lama "jangan beri role `hris` ke akun non-BIP" **tak lagi jadi satu-satunya penjagaan**.
- ✅ ~~Rute baca Training tidak punya gerbang role~~ — **sudah digerbang** `gate(PermTrainingView, nil)`, bersama RBAC permission-set penuh (`PermTrainingView`/`Work`/`Manage`) berikut kill-switch `TRAINING_PERMISSION_ENFORCEMENT` dan sakelar fase dua `TRAINING_TIER_FALLBACK`.
- ⚠️ **`max_participants` sempat DIKUMPULKAN tanpa pernah ditegakkan** — diperbaiki 2026-08-10 (PR [#1147](https://github.com/bip-itteam-internal/bip-erp/pull/1147)). Kolom itu disebut "cap keras" di **tiga tempat** (komentar field, komentar rute, dokumen vault) sementara `CanEnroll` tak pernah menerima kapasitasnya: HR mengisi kuota 20, orang ke-21 masuk tanpa keluhan apa pun. Pola yang sudah berulang di repo ini — dirakit benar, tak dibaca siapa pun, nol test merah. Nol/negatif = tanpa batas, dan duplikat diperiksa lebih dulu daripada kuota supaya pesannya tidak menyesatkan.
- ✅ ~~Belum ada uji level handler~~ — **21+ rute kini dikunci** lewat `app.Test` (PR #1147): ditolak tanpa identitas, izin baca tak membuka rute tulis, izin tulis tak membuka rute kelola master, penjaga prefix gateway berikut kontrol negatifnya, urutan rute statik vs `/:id`, ObjectID cacat dibalas 400, fallback tier, dan pengunci jumlah rute.
- ⚠️ **Urutan registrasi rute itu kritis dan dikunci uji.** `/training/requests` dan `/training/:id/evaluation` didaftarkan **sebelum** `registerTrainingEventRoutes`; menaruhnya sesudah `/training/:id` membuat permintaannya ter-match sebagai event ber-id "requests" lalu dibalas 400 *"id is not a valid ObjectID"* — galat yang menuduh permintaan yang benar dan paling sulit dicurigai karena pesannya terdengar masuk akal.
- `ensureTrainingIndexes` dan kedua index baru dijaga `mongodb.DB == nil`: paniknya terjadi saat **registrasi rute**, jadi tanpa itu service gagal naik sama sekali.
- Bawaan dari kode lama, belum diperbaiki: `PUT` bersifat full-replace sehingga frontend wajib mengirim objek lengkap, pendaftaran peserta belum memeriksa karyawan benar-benar ada di `work_data`, dan daftar belum berpaginasi.
- **Belum ada frontend** untuk pengajuan maupun evaluasi, dan keduanya **belum diverifikasi lewat gateway hidup**.
- **Rute lama `/api/employee/training/*` masih hidup di produksi.** `employee-service` sengaja tidak di-rebuild saat cut-over agar tidak ikut mendorong perubahan orang lain ke produksi. Tidak ada pemanggil yang tersisa. Koleksi Training lama juga masih ada di `employee_db` sebagai jalan pulang.

## Dependensi & Integrasi

- **MongoDB `learning_db`** — koleksi `training_type`, `trainer`, `training`, `training_participant`, `training_request`, `trainer_evaluation`. Lihat [[DB - Overview and Notes]].
- [[Microservices - Notification Service]] — inbox pengajuan, memakai kategori `request-*` yang sudah ada.
- [[Microservices - Employee Service]] — sumber master departemen (verifikasi `department_key`) dan master karyawan untuk pemilih peserta serta trainer internal.
- [[CORE - API Master Gateway]] — modul `learning`, env `LEARNING_MODULE_URL`.
- [[APP - Web ERP]] — layar `/hris/training` dan `/hris/training/masters` di grup menu People Development.

## Dokumen Terkait

- [[HRIS - Training Program]] — konsep, desain LMS lengkap, dan rencana bertahap
- [[API - Learning Service]] · [[API - Index]]
- [[Microservices - Employee Service]] — rumah lama modul ini
- [[ADR - 0002 Database-per-Service]] · [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]
