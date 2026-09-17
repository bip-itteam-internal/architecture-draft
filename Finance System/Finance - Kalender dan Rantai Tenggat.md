# Finance - Kalender dan Rantai Tenggat

## Deskripsi

*Tanggal kerja bulanan Finance dan ketergantungan antarlangkahnya, sebagai dasar merancang tenggat, pengingat, dan daftar periksa tutup buku di sistem. Bagian dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]].*

- **Status**: ⚠️ **Implemented (ada catatan)**. Tenggat pajak sudah dikirim ke kalender terpusat (`bip-erp/services/finance/pajak_calendar_feed.go:156`, rute `bip-erp/services/finance/routes.go:137`, provider `bip-erp/services/calendar/providers.go:38`); tenggat lain di tabel ini belum punya feed maupun pengingat.
- **Sumber**: isian survei alur kerja Finance 14 sampai 16 September 2026. Tanggal ini **bukan aturan perusahaan**; konfirmasi ke Supervisor FAT sebelum dijadikan tenggat sistem.

## Kalender bulanan

Yang penting bagi rancangan adalah **rantainya**: langkah di kolom kegiatan tidak bisa dikerjakan sebelum yang di kolom "Bergantung pada" selesai, jadi keterlambatan di awal rantai menumpuk di minggu pertama.

| Tanggal | Kegiatan | Proses | Bergantung pada |
|---|---|---|---|
| 1 | Pembayaran gaji | P7, P2 | Rekap gaji dari HR tiba dan diperiksa sebelum tanggal 1 |
| 1 | Unduh rekening koran, rekonsiliasi awal bulan | P5 | Rekening koran baru tersedia tanggal 1 |
| 1 | Pencocokan penjualan dashboard, ERP, dan Accurate | P3 | Sinkron marketplace bulan lalu lengkap |
| 1 sampai 3 | Kode billing PPh final, PPh 21, PPh 25 | P8 | Omzet per CV dari pengolahan penjualan (P3); gaji (P7) |
| 1 sampai 3 | Kas kecil GA dan marketing | P9 | Lampiran pengeluaran dari unit |
| 1 sampai 5 | Tutup buku kas umum, laporan keuangan bulanan | P10 | Seluruh input akhir bulan lengkap |
| 2 | Rekonsiliasi penjualan dengan gudang | P3, P4 | Balasan gudang |
| 5 (sebagian 6 sampai 10) | Pembayaran hutang supplier dan PPh final | P2, P8 | Kode billing; data penarikan kas toko |
| 10 | Pembayaran iuran BPJS TK | P7, P2 | Tagihan dan lampiran per badan usaha dari HR |
| 20 | Kode billing PPh 23 dan PPN | P8 | Data pembelian dan pembayaran |
| Beberapa tanggal tetap per brand | Pembayaran iklan dan FO | P1, P2 | Permintaan dari marketing; frekuensinya tidak konsisten antar isian (TBD volume) |
| Sekitar 25 sampai 28 | Stock opname gudang dan rekonsiliasi stok | P10 | Hitung fisik tim gudang |
| Mulai 26, lalu sekitar 29 sampai 30 | Pengecekan rekap gaji (kehadiran dan potongan, lalu rekening dan PPh) | P7 | Rekap dari HR |
| 30 atau 31 | Penarikan afiliasi, cut-off | P9, P10 | Data afiliasi |

Kode proses: P1 [[Finance - Proses Pengajuan Pengeluaran dan Persetujuan]] · P2 [[Finance - Proses Pembayaran Keluar]] · P3 [[Finance - Proses Penjualan Marketplace dan Uang Masuk]] · P4 [[Finance - Proses Retur dan Piutang Marketplace]] · P5 [[Finance - Proses Rekonsiliasi Kas Toko dan Bank]] · P7 [[Finance - Proses Gaji dan Iuran BPJS]] · P8 [[Finance - Proses Pajak]] · P9 [[Finance - Proses Anggaran, Kas Kecil, dan Dana Kegiatan]] · P10 [[Finance - Proses Tutup Buku, Stock Opname, dan Laporan]].

## Kebutuhan sistem dari rantai ini

- Tiap tenggat punya pemilik, dan pengingatnya dikirim ke **pemilik langkah sebelumnya**, bukan hanya ke pemilik tenggat.
- Tenggat didaftarkan sebagai feed ke [[Microservices - Calendar Service]], mengikuti pola feed pajak yang sudah ada; bukan halaman kalender sendiri.
- Daftar periksa tutup buku (P10, T10) memperlihatkan langkah mana yang masih menahan rantai dan siapa pemiliknya.

## Belum Diputuskan (TBD)

- Tanggal mana yang menjadi tenggat resmi, dan untuk entitas mana saja.
- Volume dan jadwal pasti pembayaran iklan dan FO per brand.

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[Microservices - Calendar Service]] · [[API - Finance Service]]
