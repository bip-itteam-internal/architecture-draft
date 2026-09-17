## Untuk Manajemen

- **Yang berubah di layar**: sesudah pelatihan selesai, peserta menjawab satu pertanyaan tambahan "seberapa sesuai materi ini dengan pekerjaan Anda" (1 sampai 10), di layar penilaian yang sama dengan penilaian trainer, di web dan MyBharata (MyBharata ditunda per 2026-09-17; untuk sementara lewat web). Di KPI Training Officer, dua metrik bisa diisi sistem: kesesuaian materi (dari jawaban peserta) dan kenaikan kinerja peserta (skor KPI bulan sebelum pelatihan dibanding bulan sesudahnya).
- **Siapa terdampak**: peserta pelatihan (satu pertanyaan tambahan), Training Officer (dua metrik terisi otomatis), HR (memasang sumbernya di Atur Target).
- **Tidak dijanjikan**: jobdesk per jabatan dan kurikulum per jabatan TIDAK dibangun di keputusan ini. Kenaikan skor KPI tidak membuktikan bahwa pelatihanlah penyebabnya. Angka kenaikan baru muncul dua bulan sesudah kelas selesai, dan peserta yang tidak punya skor KPI di salah satu bulan tidak ikut terhitung.
- **Besaran kerja**: kecil sampai sedang, tersebar di dua service backend, satu layar web, satu layar aplikasi, dan satu rilis MyBharata.

## Deskripsi

*Dua metrik KPI Training & Performance Officer yang belum bisa dinilai sistem diisi dari data yang sudah ada: kesesuaian materi dari satu pertanyaan 1-10 kepada peserta yang disimpan TERPISAH dari penilaian trainer, dan dampak pelatihan dari kenaikan skor KPI peserta antara bulan sebelum dan sesudah pelatihan dengan jeda dua bulan. Jobdesk per posisi dipisah jadi keputusan sendiri.*

- **Status**: 🟡 **Diusulkan** 2026-09-17, disetujui pemilik proses (opsi A1 + K1). ⚠️ **Backend sudah MERGED, belum di prod** (per 2026-09-17, ukur ulang sebelum dipakai): T1-T2 (jawaban `kesesuaian_materi` 1-10 opsional di evaluasi pasca-pelatihan, agregat per kelas, kontrak `GET /kpi/pelatihan` bertambah `kesesuaian` serta `bulan_mulai`/`bulan_selesai`) lewat bip-erp [#1945](https://github.com/bip-itteam-internal/bip-erp/pull/1945), merged 2026-09-17 07:51 UTC; T3-T4 (metrik `kesesuaian_materi_skala10` dan `kenaikan_kpi_peserta_persen`) lewat [#1951](https://github.com/bip-itteam-internal/bip-erp/pull/1951), merged 2026-09-17 08:49 UTC. T5-T6 (layar web) merged lewat erp-frontend [#1631](https://github.com/bip-itteam-internal/erp-frontend/pull/1631) 2026-09-17 09:19 UTC; ⚠️ halaman web Pelatihan Saya tak punya menu sidebar sejak 2026-08-13, jadi peserta hanya menjangkaunya lewat tautan langsung. T7 (MyBharata) **ditunda**: rilis terakhir masih `v1.14.5`, peserta praktis menilai lewat web. **DEV terverifikasi sebagian** (penyimpanan, validasi, agregat per kelas, dan katalog 6 metrik lewat gateway; perhitungan kedua metrik lewat template belum). **PROD belum deploy** (T8, dijalankan manusia) dan HR belum memasang sumbernya di Atur Target (T9). Rujukan baris kode di Context dibaca dari `origin/main` sebelum #1945.
- **Path di repo**: `bip-erp/services/learning/models_evaluation.go` · `evaluation.go` · `kpi_pelatihan.go` · `bip-erp/services/employee/kpi_sumber_pelatihan.go` (metrik baru) · `erp-frontend/src/features/hris/training/evaluation/components/evaluation-form-dialog.tsx` · `erp-frontend/src/features/hris/kpi/lib/label-otomatis.ts` · `my-bharata/lib/src/features/training/presentation/widgets/trainer_evaluation_sheet.dart`
- **Tanggal**: 2026-09-17
- **Terkait**: [[HRIS - Training Program]] · [[HRIS - Matriks KPI per Departemen]] · [[Microservices - Learning Service]] · [[Microservices - Employee Service]]

## Context

Template `People and Development` (satu pemegang aktif) punya dua metrik yang dibahas di sini. Keduanya belum punya blok `auto`, dan skor Agustus 2026 diketik tangan oleh pemegang posisi sendiri ([[HRIS - Matriks KPI per Departemen]]).

1. **`Kesesuaian materi LMS dengan jobdesk`** (bobot 0,15, target skala 10) tak punya sumber. Usulan awalnya (opsi B) membangun tempat jobdesk per posisi, kurikulum per jabatan, lalu penilaian 1-10 oleh penilai yang ditunjuk. Wawancara 2026-09-17 menggeser dasarnya:
   - Yang menilai adalah **peserta pelatihan**. Peserta tahu pekerjaannya sendiri, jadi penilaian ini **tidak membutuhkan jobdesk tersimpan**.
   - Jobdesk per posisi **belum ada sama sekali**, tertulis maupun tidak. Diukur prod 2026-09-17: 122 `position_items` (BIP 108, ELT 14) dan struct-nya hanya `key`, `name`, `permission_sets`, `level_key` (`shared-library/models/employee/master_data.go:88-114`). Membangun wadahnya tidak menghasilkan satu angka pun sebelum HR menulis 122 jobdesk.
   - Skor KPI dipakai untuk **pemantauan**, tidak memengaruhi uang.
2. **`Skor Penilaian Training All Karyawan > 70`** (bobot 0,35) selama ini dipetakan ke skor post-test (`skor_post_test_persen`, atau `peningkatan_post_test_persen` sejak Tahap 3b). Pemilik proses menyatakan 2026-09-17 bahwa arti metrik ini adalah **apakah skor KPI peserta naik** dari bulan sebelum pelatihan ke bulan sesudahnya, **tanpa ambang 70**.

Yang sudah ada dan dipakai sebagai dasar (bukan dok konsep):

- **Evaluasi pasca-pelatihan oleh peserta** ✅ live: satu per peserta per kelas, hanya kelas `Completed`, identitas penilai tak keluar, minimal 3 responden ([[Microservices - Learning Service]]). Keempat aspeknya menilai TRAINER. Aspek `manfaat` sudah dijumlah ke nilai kepuasan (`services/learning/kpi_pelatihan.go:294-295`) dan server menolak aspek bernilai nol (`services/learning/models_evaluation.go:74-86`). Prod: 0 evaluasi.
- **Sumber KPI `pelatihan`** ✅ live: membawa pendaftaran per kelas (`training_id`, `employee_id`, `hadir`, skor ujian) dari `GET /kpi/pelatihan` (`services/employee/kpi_sumber_pelatihan.go:63-75`). Cakupannya sudah mengeluarkan orang yang dinilai dari populasinya sendiri (`kpi_sumber_pelatihan.go:211-214`).
- **`kpi_score` per karyawan per bulan** ✅, milik employee-service ([[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]). Diukur prod 2026-09-17: 107 sampai 165 karyawan berskor per bulan (Juli 165, Agustus 108). Dari 4 peserta di 2 kelas yang sudah selesai, baru 2 yang punya skor bulan sebelum pelatihan.
- **Tanggal beku**: hanya posisi yang seluruh metriknya otomatis yang dibekukan sistem tanggal 1 bulan berikutnya; posisi manual menunggu diketik; skor Agustus 2026 Training Officer sendiri baru disimpan 10 September ([[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]], [[HRIS - Matriks KPI per Departemen]]).

Yang ditolak saat analisa:

- **Aspek `manfaat` sebagai kesesuaian**: sudah masuk `kepuasan_trainer_skala10`, jadi angka yang sama terhitung dua kali di template yang sama.
- **Aspek kelima di dalam penilaian trainer**: pembagi `*4` ada di tiga tempat, agregat per trainer berubah arti (yang dinilai materi, bukan trainer), dan aspek wajib baru membuat MyBharata lama ditolak 400.
- **Sumber `ceklis_kpi`**: hanya sudah/belum, skala 10 hilang.
- **Form Builder per kelas**: form dibuat manual tiap kelas, tanpa tautan ke peserta kelas dan tanpa ambang responden.
- **Dokumen HRD berjenis jobdesk**: sasaran jabatan dicocokkan lewat NAMA (`services/hrd-document/target.go:21-23`) dan tanpa `company_id`. Relevan untuk keputusan jobdesk nanti, bukan untuk metrik ini.

## Decision

### 1. Kesesuaian materi adalah pertanyaan TERPISAH kepada peserta, bukan aspek penilaian trainer

Satu pertanyaan skala **1-10**, *"Seberapa sesuai materi pelatihan ini dengan pekerjaan Anda?"*, ditanyakan pada kiriman evaluasi yang sama (satu layar, satu tombol kirim) tetapi disimpan sebagai **angka sendiri** di luar keempat aspek trainer.

- **Tidak ikut dijumlah** ke nilai kepuasan trainer. Kolom ini **sejajar**, bukan komponen `kepuasan_trainer_skala10`, dan tak boleh dijumlah atau dirata-rata dengannya.
- **Opsional di server**: kiriman tanpa jawaban kesesuaian tetap diterima (MyBharata lama yang beredar). Tidak dijawab dibedakan dari nilai apa pun, dan keluar dari penyebut.
- **Semua kelas `Completed`** ikut dinilai, bukan hanya yang bertaut materi LMS. Per 2026-09-17 baru 1 kelas yang bertaut materi, dan yang ditanyakan adalah kesesuaian isi pelatihan.

### 2. Metrik `kesesuaian_materi_skala10` di sumber `pelatihan`

Rata-rata jawaban 1-10 **langsung**, tanpa konversi, atas kelas yang selesai di periode itu dalam cakupan. Di bawah **3 responden** gabungan: *belum dapat dihitung*, mengikuti ambang evaluasi yang sudah ada. Responden kesesuaian **dihitung sendiri**, tidak memakai jumlah responden kepuasan, karena kiriman lama tidak punya jawaban kesesuaian.

- **Bahan kesesuaian yang tidak tersedia adalah galat biasa**, bukan *belum dapat dihitung*: bila learning tidak membawa kunci `kesesuaian` (versi lama, atau satu batch saja tak membawanya), metrik ini gagal dengan pesan yang menyuruh menaikkan learning-service. Menyamarkannya sebagai "belum ada jawaban" membuat HR menagih peserta untuk masalah deploy. Metrik lain dari muatan yang sama tetap dihitung. Sebagaimana dikodekan (#1951): `cuplikanKesesuaianMateri` dan `ambilPelatihanBerbatch`, `services/employee/kpi_sumber_pelatihan.go:237-269`, `:532-568`.

### 3. Metrik `kenaikan_kpi_peserta_persen` di sumber `pelatihan`, jeda dua bulan

Periode **P** menilai kelas `Completed` yang **selesai di bulan P-2**.

- **Satuannya per PENDAFTARAN kelas, dan hanya peserta HADIR** (keputusan pemilik proses 2026-09-17, mempertegas "per peserta" di butir-butir di bawah). Orang yang ikut dua kelas dinilai dua kali, masing-masing dengan bulan mulai dan selesai kelasnya sendiri. Pendaftar yang tidak hadir tidak masuk populasi: kenaikan skor orang yang tidak mengikuti pelatihan bukan dampaknya, dan kehadiran sudah diukur metriknya sendiri. Populasi = pendaftaran hadir. Bila tak satu pun peserta hadir membawa bulan kelas, itu **galat biasa** (tanda learning versi lama), bukan *belum dapat dihitung*. Sebagaimana dikodekan (#1951): `cuplikanKenaikanKPIPeserta`, `services/employee/kpi_sumber_pelatihan.go:633-724`.
- **Pembanding per peserta**: skor akhir `kpi_score.score` bulan kalender **sebelum bulan mulai kelas**, dibanding bulan kalender **sesudah bulan selesai kelas**. Untuk kelas satu hari, itu P-3 lawan P-1.
- **Nilai per peserta**: **100** bila skor sesudah lebih tinggi daripada skor sebelum, **0** bila sama atau turun. **Tanpa ambang** (keputusan pemilik proses 2026-09-17).
- **Skor tak ada** di salah satu bulan: peserta keluar dari nilai, tetap di populasi, dan rinciannya menyebut berapa. Polanya sama dengan `peningkatan_post_test_persen`.
- **Orang yang dinilai** tidak masuk populasinya sendiri; perilaku cakupan yang sudah ada dipertahankan.
- **Kepemilikan**: `kpi_score` dibaca employee-service di databasenya sendiri; learning hanya menambah tanggal mulai dan selesai kelas pada pendaftaran di `GET /kpi/pelatihan`. Tidak ada service lain yang membaca `kpi_score`.
- **Jeda dua bulan** dipilih supaya skor "sesudah" hampir selalu sudah ada saat dinilai. Rinciannya wajib menyebut bulan kelas dan dua bulan yang dibandingkan, supaya angka November tidak dibaca sebagai hasil pelatihan November.

### 4. Metrik 0,35 memakai kenaikan KPI; sumber post-test tetap ada

Metrik `Skor Penilaian Training All Karyawan > 70` dipasang ke `kenaikan_kpi_peserta_persen`. `skor_post_test_persen` dan `peningkatan_post_test_persen` **tidak dihapus**: kelulusan, sertifikat, dan rekaman ujian bergantung padanya, dan artinya tidak diubah.

### 5. Jobdesk per posisi dan kurikulum per jabatan TIDAK diputuskan di sini

Keduanya dipisah ke analisa sendiri bersama metrik Recruitment & Onboarding `Ketersediaan Dokumen Jobdesk diseluruh posisi` (bobot 0,25), yang terkunci karena alasan yang sama. Pertanyaan pokoknya siapa yang menulis 122 jobdesk dan kapan, lalu baru wadahnya.

## Consequences

### Yang membaik

- Dua metrik berbobot total **0,5** bisa diisi sistem tanpa menunggu data yang belum pernah ada.
- Tidak ada hitung ganda: kesesuaian dan kepuasan trainer berdiri sebagai dua angka terpisah.
- Aplikasi lama tetap bisa mengirim penilaian trainer.

### Yang memburuk atau tetap terbuka

- ⚠️ **Jeda dua bulan**: kelas September baru tercermin di KPI November. Metrik Training Officer untuk bulan berjalan selalu menilai pelatihan dua bulan lalu.
- ⚠️ **Skor KPI antar bulan tidak selalu sebanding**: template seseorang bisa berganti di antara dua bulan itu, dan banyak skor diketik manual. Karena skor ini untuk pemantauan, keduanya diterima dan wajib disebut di rincian metrik, bukan disembunyikan.
- ⚠️ **Cakupan skor belum semua karyawan** (107 sampai 165 per bulan). Peserta tanpa skor tidak ikut terhitung, jadi populasi kecil bisa membuat angkanya melompat.
- ⚠️ **Kenaikan bukan bukti sebab-akibat.** Metrik ini mengukur apakah kinerja peserta bergerak naik sesudah pelatihan, bukan bahwa pelatihan penyebabnya.
- **Kelas panjang** (mis. pendampingan tiga bulan) membandingkan bulan sebelum mulai dengan bulan sesudah selesai, jadi jaraknya lebih dari dua bulan.
- **Evaluasi yang terkirim sebelum fitur ini** tak bisa dilengkapi jawaban kesesuaian (satu kiriman per peserta per kelas). Prod 2026-09-17: 0 evaluasi, jadi tak ada yang hilang.

### Konsekuensi deploy

- `learning-service` dan `employee-service` **naik bersamaan** begitu metrik `kesesuaian_materi_skala10` dan `kenaikan_kpi_peserta_persen` (T3/T4) ikut, karena kontrak `GET /kpi/pelatihan` bertambah (dijaga uji kontrak yang sudah ada). Backend lebih dulu, lalu erp-frontend, lalu **rilis MyBharata** dengan version name dan code dinaikkan.
	- **Penyempitan sadar untuk T1-T2 saja** (diputuskan saat `/plan` 2026-09-17): selama belum ada metrik yang membaca tambahan kontrak, urutan kedua service **bebas**. Learning lama dengan employee baru membuat `kesesuaian` terbaca *tidak tersedia* tanpa memadamkan metrik lain; learning baru dengan employee lama hanya membuat kunci barunya diabaikan. Rincian di [[Microservices - Employee Service]]. Penyempitan ini **tidak berlaku lagi** sejak T3-T4 merged 2026-09-17 (#1951): kedua service naik bersama.
- ⛔ **erp-frontend naik SESUDAH learning-service**, bukan sekadar "sesudah backend" secara umum. Learning sebelum #1945 mengurai kiriman penilaian hanya sebagai `ratings` dan `comment`, jadi `kesesuaian_materi` dari layar baru diabaikan diam-diam: kiriman tetap 201 dan jawaban peserta hilang tanpa satu pun galat. Karena satu peserta hanya bisa menilai sekali per kelas (indeks unik `training_id` + `employee_id`, `services/learning/evaluation.go:28-36`), jawaban yang hilang tak bisa dikirim ulang.
- ⚠️ **Pipeline DEV melewatkan learning-service pada merge ini.** 2026-09-17 sekitar 15.50-16.05 WIB pipeline dev menaikkan Employee-Service tetapi tidak Learning-Service, jadi learning dibangun ulang manual; gerbang biner kedua service lalu memuat kode baru (kontrol positif ada, string karangan 0). Merged bukan bukti ter-deploy: saat deploy PROD, gerbang biner wajib diperiksa di **kedua** service, bukan salah satunya.
- **MyBharata ditunda** (T7, 2026-09-17): rilis terakhir masih `v1.14.5`, jadi urutan "lalu rilis MyBharata" di atas belum berjalan dan untuk sementara peserta menjawab kesesuaian lewat web. MyBharata yang beredar tetap bisa menilai trainer karena jawabannya opsional (§1).
- Tanpa env baru, tanpa kategori inbox baru, tanpa migrasi data.
- HR memasang dua sumber baru di Atur Target sesudah deploy. Template tidak berubah sendiri.

### Yang sengaja tidak dilakukan

- **Ambang 70** pada kenaikan KPI.
- **Menurunkan kesesuaian dari aspek `manfaat`** (hitung ganda).
- **Aspek kelima wajib di penilaian trainer** (memecah pembagi, arti agregat trainer, dan klien lama).
- **Jobdesk per posisi, kurikulum per jabatan, materi PDF/video**: keputusan terpisah.

## Dokumen Terkait

- [[HRIS - Training Program]] · [[HRIS - Matriks KPI per Departemen]] · [[HRIS - Dashboard per Posisi]]
- [[Microservices - Learning Service]] · [[Microservices - Employee Service]] · [[API - Learning Service]]
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] · [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]
- [[HRIS - Career & Promotion]] (kurikulum jabatan dan matriks kompetensi yang tetap TBD) · [[HRIS - HRD Documents]]
- [[RUN - Menambah Metrik KPI Otomatis]]
