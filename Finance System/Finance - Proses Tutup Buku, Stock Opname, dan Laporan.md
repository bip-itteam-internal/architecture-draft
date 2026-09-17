# Finance - Proses Tutup Buku, Stock Opname, dan Laporan

## Deskripsi

*Proses P10, tutup buku, stock opname, dan laporan, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Penilaian cakupan dan kesesuaiannya ada di dok induk.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Laporan dibaca dari Accurate; daftar periksa tutup buku 🟡 direncanakan (T10) dan opname digital masih konsep.
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, butir bertanda *survei 2026-09*), kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17. Keadaan prod bertanggal di tiap butir; ukur ulang sebelum dipakai memutuskan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Tutup buku bulanan tepat waktu dengan input yang lengkap, stok buku cocok dengan fisik, dan laporan yang tidak perlu dikoreksi.

## Hari ini (*survei 2026-09*)

Pekerjaan menumpuk di minggu pertama (gaji, kode billing, rekonsiliasi awal bulan, laporan) dan akhir bulan (stock opname sekitar tanggal 25 sampai 28, cek gaji, cut-off, retur tertahan untuk jurnal penyesuaian). Data yang baru tersedia sesudah akhir bulan (rekap iklan, sampel afiliasi, tagihan utilitas, laporan PPN dan PPh final) ditagih manual. Selisih stock opname ditelusuri item per item dari mutasi stok terhadap kartu stok.

## Sudah ada di ERP

Laporan keuangan dan jurnal dibaca dari Accurate (`/finance/accounting`, `/finance/gl`, [[Finance - Dashboard per Posisi (FAT)]]); ceklis laporan untuk audit internal ([[Finance - Audit Internal]]); manufacture-service membaca stok dari Accurate satu arah dan mengunci saldo akhir yang berasal dari impor stock opname ([[Microservices - Manufacture Service]]); opname digital masih konsep ([[Manufacture - Stock & Material Management]]).

## Alur target

Daftar periksa tutup buku per entitas memperlihatkan input yang belum masuk dan siapa pemiliknya → data akhir bulan dari modul lain ditarik, bukan ditagih → hasil stock opname masuk sebagai data dengan selisih per item → periode dikunci sesudah diperiksa.

## Celah

- **C** Daftar periksa tutup buku dan peran pengunci periode (T10).
- **C** Opname digital dengan selisih per item, milik domain manufaktur dan gudang.
- **TBD** Data akhir bulan mana yang sudah ada di modul lain (iklan dan afiliasi di modul marketing) dan bisa ditarik.

## Kontrol wajib

Periode yang sudah dikunci tidak bisa diubah tanpa jejak.

## Ukuran efisiensi

Tanggal laporan keuangan selesai; jumlah input yang masih ditagih manual; jumlah item selisih stok per opname.

Sumber data baseline: Arsip laporan (tanggal selesai); daftar tagihan data akhir bulan; berita acara opname (item selisih).

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[Finance - Dashboard per Posisi (FAT)]] · [[Finance - Audit Internal]] · [[Microservices - Manufacture Service]] · [[Manufacture - Stock & Material Management]]
