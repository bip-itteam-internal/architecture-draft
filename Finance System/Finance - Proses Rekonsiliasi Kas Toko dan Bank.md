# Finance - Proses Rekonsiliasi Kas Toko dan Bank

## Deskripsi

*Proses P5, rekonsiliasi kas toko dan bank, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Penilaian cakupan dan kesesuaiannya ada di dok induk.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Layar rekonsiliasi kas toko ada tetapi formatnya belum cocok dengan kerja rekonsiliasi; impor mutasi rekening 🟡 direncanakan (T9).
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, butir bertanda *survei 2026-09*), kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17. Keadaan prod bertanggal di tiap butir; ukur ulang sebelum dipakai memutuskan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Saldo buku sama dengan saldo nyata di seller center dan rekening bank, dan setiap selisih punya sebab tertulis.

## Hari ini (*survei 2026-09*)

Saldo kas toko direkonsiliasi mingguan terhadap Accurate beserta analisis selisih harga, biaya, dan nilai settle; saldo kas toko disajikan manual dari Accurate lalu diperbarui berulang sampai sama dengan seller center, sambil menunggu perbaikan dari IT; rekening koran baru tersedia tanggal 1. Ini beban terbesar yang disebut lintas peran.

## Sudah ada di ERP

Layar Rekonsiliasi kas toko empat tab: rekap, rincian, akumulasi, dan **Neraca** (`erp-frontend/src/app/(main)/integration-accurate/rekonsiliasi/page.tsx:69-80`). Neraca menyandingkan saldo Seller Center, ERP, dan Accurate per akun kas toko pada satu tanggal, beserta jam sync MP terakhir karena sisi MP diperbarui tiap 30 menit, bukan real-time. Saldo MP = saldo pembukaan per toko + mutasi sejak tanggal cutover toko itu; mekanisme dan angkanya di [[Microservices - Integration Service]], butir Buku Besar Rekonsiliasi Kas. Keadaan prod 2026-09-23: pembukaan diisi dari saldo Seller Center 31 Agustus 2026 dan cutover 1 September. Juli sampai Agustus sudah disesuaikan manual di Accurate dan **tidak** diulang atau dikirim ulang. Posisi 17 September: 36 dari 56 akun bernol selisih, nol akun ber-saldo MP negatif, dan sisa terbesarnya 11 penarikan September yang belum dijurnal di Accurate (Rp1.065.093.727). Ukur ulang sebelum dipakai. rute rekonsiliasi dompet dan income (P3). Impor mutasi rekening bank **belum ada**: `git grep` 2026-09-17 atas `services/finance`, `services/integration`, dan `services/procurement` hanya menemukan rekening koran sebagai lampiran bukti audit internal.

## Alur target

Satu pelaku rekonsiliasi per jenis saldo memakai satu format di ERP → selisih muncul sebagai daftar bersebab (bukan saldo yang diperbarui berulang) → mutasi bank diimpor dan dicocokkan dengan jurnal kas → Senior Accountant memeriksa hasil akhir.

## Celah

- **B** Format layar rekonsiliasi kas toko disesuaikan dengan kerja rekonsiliasi. Format yang dibutuhkan belum dirinci (**TBD**, minta contoh format kerja yang dipakai sekarang).
- **B** Saldo tersedia TikTok tak bisa diambil langsung dari marketplace: Partner API SEA tak menyediakan saldo (`Get Payments` tak tersedia), jadi sisi MP selalu hasil hitung dan hanya sama dengan Seller Center bila saldo pembukaan terisi dan mutasinya lengkap. Lazada juga dihitung, karena `closing_balance` payout adalah saldo akhir satu statement, bukan saldo akun.
- **C** Impor mutasi rekening dan rekonsiliasi bank (T9). Lingkup T9 kini rekening CV; rekening PT dan kas toko masuk atau jadi task sendiri belum diputuskan.

## Kontrol wajib

Pelaku rekonsiliasi bukan pelaksana transfer.

## Ukuran efisiensi

Putaran rekonsiliasi kas toko per bulan dan jam per putaran; jumlah selisih yang belum bersebab di akhir bulan.

Sumber data baseline: Catatan pelaku rekonsiliasi (putaran dan jam); laporan Kopra dan internet banking (transaksi per rekening).

## Proses terkait

- P3: [[Finance - Proses Penjualan Marketplace dan Uang Masuk]]

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
