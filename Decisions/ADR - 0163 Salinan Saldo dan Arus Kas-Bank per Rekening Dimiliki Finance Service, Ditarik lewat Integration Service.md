# ADR - 0163 Salinan Saldo dan Arus Kas-Bank per Rekening Dimiliki Finance Service, Ditarik lewat Integration Service

> **Status**: 🟢 Diterima, 2026-10-09, oleh wirkancil sebagai Pemutus bip-erp#2880 (aturan persetujuan ADR di [[ADR - 0151 Issue Siap Dikerjakan Agent Bila Keputusannya Bisa Ditunjuk, Ditandai Manusia]]). Bentuknya dipilih di sesi brainstorming 2026-10-09, sesudah pengukuran ke Accurate prod (baca saja) dan `origin/main` hari itu. ⚠️ **Sebagian berjalan**: backend-nya (bip-erp#2896) merged dan berjalan di prod sejak 2026-10-09 sore, dengan jadwal lama tiap 2 jam; perubahan jadwal ke jam tetap pagi dan sore (K4, bip-erp#2903) dan layarnya (erp-frontend#2235) masih dikerjakan per 2026-10-09. Ukur ulang sebelum mengandalkan kalimat ini.

## Untuk Manajemen

**Apa yang berubah di layar.** Halaman Tim Accounting mendapat tab **Kas dan Bank**: sisa saldo, uang masuk, dan uang keluar tiap CV dan PT untuk satu bulan, dengan jam data terakhir dan tombol **Segarkan**. Di bawah totalnya ada satu baris "Kas dan bank lain di Accurate" (deposito, sekuritas, saldo toko marketplace, kas tunai, dan lainnya), supaya total di layar bisa dicocokkan dengan Accurate.

Aturan yang dijaga sistem:

- Angkanya **salinan dari Accurate**, tidak pernah diketik orang. Bulan berjalan disegarkan dua kali sehari pada jam tetap, 07.00 dan 16.00 WIB; tiga bulan sebelumnya sekali tiap dini hari.
- Salinan yang belum ada atau gagal diambil tampil sebagai **keterangan**, tidak pernah sebagai Rp 0.
- CV atau PT yang rekeningnya tidak ditemukan di Accurate **disebut**, tidak diam-diam dilewati.

**Siapa yang terdampak.** Tim Accounting dan pembaca lain halaman Tim Accounting (pemegang izin `finance.accounting.view`).

**Apa yang TIDAK dijanjikan.**

- **Bukan angka detik ini.** Di antara dua jam tetap itu angkanya hanya berubah bila ada yang menekan Segarkan, jadi umurnya bisa sampai sembilan jam di siang hari dan sampai pagi berikutnya sesudah sore. Tombol Segarkan mengambil ulang saat itu juga.
- **Bukan mutasi bank.** Ini buku Accurate. Selisihnya dengan rekening koran tetap urusan layar Rekonsiliasi Bank.
- Tidak ada rincian transaksi per rekening di tab ini.
- Uang masuk dan keluar **tidak** dihitung untuk "kas dan bank lain"; yang tampil hanya saldonya.
- Saat pertama terpasang, bulan yang tersedia hanya bulan berjalan dan tiga bulan sebelumnya.

**Perkiraan besaran kerja.** Sedang: satu pekerjaan backend dan satu pekerjaan layar; backend naik lebih dulu.

## Deskripsi

*Saldo dan arus uang kas-bank per CV dan PT hanya bisa dilihat dengan membuka Accurate akun demi akun. Keputusan ini menetapkan salinannya dimiliki finance-service, disimpan per rekening per bulan, ditarik lewat integration-service secara berkala, dan dikelompokkan ke entitas saat dibaca.*

- **Path di repo** (yang **akan** disentuh): `bip-erp/services/finance/` (koleksi salinan, penjadwal, rute baca, rute Segarkan; baru). Yang **dipakai ulang tanpa diubah**: `services/finance/rekon_bank_sumber.go` (`SumberRekon`), `services/finance/akuntansi_cv_*.go` (master entitas dan `kandidatPemilikRekeningPT`), integration `GET /accounting/riwayat-akun` dan `GET /accounting/account-balance`.
- **Tanggal**: 2026-10-09
- **Terkait**: [[REF - Kepemilikan Data]] · [[Finance - Buku Besar CV]] · [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] · [[ADR - 0130 Dashboard FAT Diringkas, Isi Posisi Pindah ke Modul Kerjanya]] · [[ADR - 0001 Akuntansi via Accurate]]

## Context

Dibaca dari `bip-erp` `origin/main` dan diukur ke Accurate prod (baca saja) pada 2026-10-09:

- **Saldo** semua akun neraca tersedia dalam satu panggilan Accurate lewat integration `GET /accounting/account-balance`. Rute itu tidak mengenal entitas.
- **Arus** hanya tersedia per akun (`glaccount/history.do`, lewat integration `GET /accounting/riwayat-akun`). Satu rekening satu panggilan, tanpa paginasi. Menarik seluruh rekening saat layar dibuka melewati batas 30 detik gateway.
- **Pemilik rekening hanya diketahui finance-service, dan jenisnya tiga**: CV lewat `akun_accurate_no` di master entitas; PT Bharata lewat pohon rekening Rekonsiliasi Bank (`rekeningDiBawahKasDiBank` di `rekon_bank_sumber.go`: akun daun yang menjadi anak langsung akun 1200, tanpa 1224); dan PT lain (PT01 sampai PT21) lewat `kandidatPemilikRekeningPT`, yang memasangkan rekening anak 1298 ke entitas lewat nama. Aturan terakhir sudah dipakai kop BKK dan transfer AP; komentarnya sendiri melarang aturan kedua.
- **Terukur**: 87 rekening milik 62 entitas (26 PT Bharata, 21 PT lain, 40 CV); 21 dari 21 PT lain cocok tepat satu rekening. Satu penyegaran bulan berjalan berarti 87 panggilan riwayat ditambah panggilan saldo.
- **Batas laju Accurate berlaku per token.** Token utama dipakai lebih dari satu service dengan pembatas yang tidak saling tahu; integration-service menggilir lima token untuk semua pekerjaannya. Riwayat pekerjaan Accurate tujuh hari terakhir tidak mencatat penolakan batas laju (pekerjaan yang menelan galatnya sendiri tidak terlihat di catatan itu).
- **Finance-service sudah menarik buku Accurate per rekening** untuk Rekonsiliasi Bank lewat antarmuka `SumberRekon`, dan sudah punya penjadwal berbasis ticker (`rekon_bank_jadwal.go`).
- Salinan Accurate yang lain (aset tetap, stok, realisasi anggaran) tinggal di integration-service, yang punya mesin jadwal dan pola Segarkan. Integration-service tidak mengenal entitas.

## Decision

- **K1. Pemilik salinan: finance-service.** Fakta disimpan per rekening per bulan: saldo awal, uang masuk, uang keluar, saldo akhir, waktu disalin. Uang masuk adalah jumlah debit dan uang keluar jumlah kredit pada buku akun itu. Seluruh rekening satu bulan ditulis sebagai **satu dokumen** dalam satu operasi, supaya pembaca hanya pernah melihat salinan lama yang utuh atau salinan baru yang utuh.
- **K2. Pengelompokan ke entitas dihitung saat dibaca**, tidak disimpan. Master entitas tetap satu-satunya tempat fakta "rekening ini milik siapa"; perubahannya langsung terlihat tanpa menarik ulang. Rute baca **tidak memanggil integration-service maupun Accurate**: struktur bagan akun yang dibutuhkan untuk menentukan pemilik ikut disimpan bersama salinan saat penyegaran.
- **K3. Penarikan wajib lewat integration-service**, memakai rute yang sudah ada. Finance-service tidak membuat sambungan Accurate sendiri.
- **K4. Jadwal.** Bulan berjalan dua kali sehari pada jam tetap, 07.00 dan 16.00 WIB, setiap hari. Tiga bulan sebelumnya sekali tiap dini hari, untuk menangkap jurnal susulan. Bulan di luar jendela itu membeku pada salinan terakhirnya. *Diubah Pemutus 2026-10-09 malam, sesudah melihat jadwal semula (tiap 2 jam sejak salinan terakhir, antara 07.00 dan 19.00) berjalan di prod: jamnya bergeser mengikuti kapan service naik dan Accurate dipanggil sampai tujuh kali sehari, padahal tokennya dipakai bersama pihak lain. Jam 07.00 dan 16.00 adalah usulan pelaksana atas keputusan "pagi dan sore".*
- **K5. Tombol Segarkan** tersedia bagi semua pembaca dan menyalin ulang **satu bulan** (yang sedang dilihat; bawaannya bulan berjalan). Rutenya menjawab seketika dan menolak bila penyegaran sedang berjalan.
- **K6. Pelan dan mengalah.** Sekitar 2 panggilan per detik. Bila Accurate menolak karena batas laju, penyegaran berhenti, salinan terakhir tetap dipakai beserta jamnya, dan dicoba lagi di jadwal berikutnya.
- **K7. Izin baca dan Segarkan: `finance.accounting.view`**, sama dengan menu Tim Accounting. Pemegangnya sudah bisa membaca saldo seluruh akun lewat laporan yang ada, jadi izin baru tidak menambah perlindungan.
- **K8. Semua entitas di master ikut**, termasuk PT01 sampai PT21, lewat `kandidatPemilikRekeningPT` yang sudah ada. Rekening PT Bharata mengikuti lingkup Rekonsiliasi Bank (seluruh rekening bank PT, bukan rekening pembayar BKK saja), supaya aturan rekening PT Bharata tetap satu. Master tidak diisi ulang dan tidak ada aturan pasangan kedua. Entitas yang rekeningnya tidak ditemukan, atau rekening yang diklaim lebih dari satu entitas, tampil berketerangan.
- **K9. Akun kas-bank di luar master tidak digabung ke angka per entitas.** Rute mengirim saldonya per kelompok induk akun Accurate (nama kelompok, jumlah akun, saldo), tanpa nama rekening dan tanpa arus, dari panggilan saldo yang sama. Total entitas ditambah total kelompok ini sama dengan total kas-bank Accurate.

Pilihan yang ditolak:

- **Salinan di integration-service.** Sejalan dengan salinan Accurate lain dan mesin jadwalnya sudah ada, tetapi ia tidak mengenal entitas, sehingga dua service harus berubah dan aturan pemilik rekening terancam tersalin.
- **Tarik langsung saat layar dibuka.** Melewati batas waktu gateway dan membebani token tiap kali halaman dibuka.
- **Sekali sehari saja.** Lebih ringan, tetapi angka siang hari selalu angka kemarin.
- **Tiap 2 jam pada jam kerja** (keputusan semula, sempat berjalan di prod): diganti jam tetap pagi dan sore, lihat K4.
- **Izin khusus.** Baru berarti bila laporan saldo yang sudah ada ikut ditutup.
- **Mengisi `akun_accurate_no` PT01 sampai PT21.** Melahirkan tempat kedua untuk fakta yang sudah diturunkan `kandidatPemilikRekeningPT`.

## Consequences

- **Menyimpang sadar dari pola "salinan Accurate tinggal di integration-service".** Alasannya K2 dan K8: yang menentukan isi layar adalah pemilik rekening, dan itu milik finance-service. Salinannya tetap memenuhi syarat salinan yang sah di [[REF - Kepemilikan Data]]: satu arah (Accurate ke finance), tidak pernah ditulis tangan, dan berpenjaga (jadwal, jam salinan yang tampil di layar, tombol Segarkan). Baris barunya di §Salinan dok itu ditambahkan saat kodenya merged.
- **Finance-service tidak punya mesin job seperti integration-service.** Penjadwalnya ticker seperti Rekonsiliasi Bank, dan riwayat penyegarannya tidak masuk `workers.worker_history`. Keadaan penyegaran (sedang berjalan, galat terakhir) harus ikut di respons rute baca supaya terlihat tanpa membuka log.
- **Pasangan PT lain bergantung pada kesamaan nama** antara master dan akun Accurate. Mengganti nama di salah satu sisi membuat PT itu tampil "rekening tidak ditemukan". Kerapuhan ini diwarisi dari aturan yang ada, bukan diperkenalkan di sini.
- **Bulan di luar jendela membeku.** Jurnal susulan yang dibukukan lebih dari tiga bulan ke belakang tidak mengubah angka bulan itu di layar.
- **Beban ke Accurate** sekitar 87 panggilan tiap penyegaran bulan berjalan, dua kali sehari, ditambah tiga bulan sebelumnya tiap dini hari. Terukur di prod 2026-10-09: satu penyegaran selesai dalam sekitar 45 detik tanpa penolakan batas laju. Karena lewat integration-service, bebannya terbagi ke kelima token.
- **Segarkan dua kali dalam 10 menit memberi data yang sama.** Integration-service menyimpan jawaban Accurate selama 10 menit, dan salinan ini tidak melewatinya. Karena saldo dan mutasi di-cache terpisah, saldo akhir rekening yang punya mutasi diambil dari baris mutasi terakhir, bukan dari saldo neraca.
- **Ada jalur kedua untuk angka total kas-bank**: procurement-service membaca total saldo kas dan bank langsung dari Accurate untuk dasbor lain. Kedua angka bisa berselisih sampai dua jam; penyatuannya di luar keputusan ini.
- **Angka per entitas tidak sama dengan total kas-bank Accurate.** Selisihnya dijelaskan baris "kas dan bank lain" (K9); tanpa baris itu pembaca yang membandingkan dengan neraca akan menduga ada yang hilang.

## Belum diputuskan

- Uang masuk dan keluar untuk akun di luar master (deposito, saldo toko marketplace), bila kelak diminta.
- Penyatuan pembatas laju antar-service yang memakai token utama Accurate. Risikonya sudah ada sebelum keputusan ini dan tidak disentuh di sini.

## Dokumen Terkait

- [[REF - Kepemilikan Data]] (syarat salinan yang sah; master entitas CV)
- [[Finance - Buku Besar CV]] · [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]]
- [[ADR - 0130 Dashboard FAT Diringkas, Isi Posisi Pindah ke Modul Kerjanya]]
- [[ADR - 0001 Akuntansi via Accurate]]
- [[ADR - 0151 Issue Siap Dikerjakan Agent Bila Keputusannya Bisa Ditunjuk, Ditandai Manusia]]
