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

Layar Rekonsiliasi kas toko tiga tab, rekap, rincian, dan akumulasi (`erp-frontend/src/app/(main)/integration-accurate/rekonsiliasi/page.tsx:39`); rute rekonsiliasi dompet dan income (P3). Impor mutasi rekening bank **belum ada**: `git grep` 2026-09-17 atas `services/finance`, `services/integration`, dan `services/procurement` hanya menemukan rekening koran sebagai lampiran bukti audit internal.

## Alur target

Satu pelaku rekonsiliasi per jenis saldo memakai satu format di ERP → selisih muncul sebagai daftar bersebab (bukan saldo yang diperbarui berulang) → mutasi bank diimpor dan dicocokkan dengan jurnal kas → Senior Accountant memeriksa hasil akhir.

## Celah

- **B** Format layar rekonsiliasi kas toko disesuaikan dengan kerja rekonsiliasi. Format yang dibutuhkan belum dirinci (**TBD**, minta contoh format kerja yang dipakai sekarang).
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
