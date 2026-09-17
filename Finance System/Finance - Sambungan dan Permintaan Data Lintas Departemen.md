# Finance - Sambungan dan Permintaan Data Lintas Departemen

## Deskripsi

*Apa yang dibutuhkan proses Finance dari departemen lain, di modul siapa kebutuhan itu tinggal, dan data apa yang rutin diminta departemen lain dari Finance. Sebagian perbaikan proses Finance dikerjakan di modul milik departemen lain, jadi dok ini dibaca bersama dok proses sebelum merencanakan pekerjaan. Bagian dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]].*

- **Status**: ⚠️ **Implemented (ada catatan)**. Sebagian sambungan sudah ada di kode (pengajuan, scan retur, payroll membaca kehadiran, faktur pembelian) tetapi belum dipakai atau belum lengkap; sebagian lain belum ada.
- **Sumber**: survei alur kerja Finance 14 sampai 16 September 2026 dan kode `origin/main` 2026-09-17. Pemilik tiap fakta mengikuti [[REF - Kepemilikan Data]].

## Yang dibutuhkan Finance dari departemen lain

| Departemen | Yang dibutuhkan Finance | Modul pemilik | Keadaan sambungan | Proses |
|---|---|---|---|---|
| Semua divisi pemohon | Pengajuan diinput sendiri beserta lampiran dan pos anggaran | Procurement (Pengajuan Barang) | Tersambung di kode, belum dipakai | P1, P2 |
| HR | Gaji dan iuran dihitung di payroll dari data kehadiran | Payroll, attendance | Payroll membaca kehadiran; ke bank dan jurnal belum ada | P7 |
| Gudang dan manufaktur | Retur discan tepat waktu; hasil stock opname sebagai data | Manufacture, integration | Scan retur membuka pembukuan retur; opname digital belum ada | P4, P10 |
| Procurement | Tagihan pemasok dan harga bahan di sistem | Procurement | Faktur pembelian ada; harga bahan untuk costing belum tersambung | P2, P11 |
| Marketing | Permintaan iklan lewat pengajuan; rekap iklan dan afiliasi untuk tutup buku | Procurement, marketing | Tipe IKLAN ada; penarikan rekap untuk tutup buku belum diperiksa | P1, P10 |
| IT | Sinkron marketplace ke Accurate yang lengkap; perbaikan selisih | Integration | Jalan; celah retur dan income manual belum diukur | P3, P4, P5 |
| Pihak luar | Transfer, rekening koran, Coretax, seller center | Di luar ERP | Tetap manual; mutasi bank direncanakan diimpor (T9) | P2, P5, P8 |

## Data yang diminta dari Finance

Permintaan yang hari ini dilayani lewat chat atau berkas. Arah sistemnya: peminta melihat sendiri di ERP sesuai hak aksesnya.

| Data | Diminta oleh | Dilayani hari ini oleh | Proses | Arah di sistem |
|---|---|---|---|---|
| Bukti transfer | Pemohon, HR, Marketing, pemasok | Junior Accountant, AP, Cost Control | P2 | Bukti menempel di pengajuan; pemohon dikabari saat bukti disetujui |
| Totalan penjualan | Departemen lain | AR | P3 | Laporan penjualan per toko dan per entitas |
| Retur yang masih tertahan | Gudang | AR | P4 | Daftar retur PENDING yang sama untuk gudang dan AR |
| Kode billing pajak | Junior Accountant | Tax | P8 | Kewajiban dan kode billing di Tax Control, masuk antrean bayar |
| Realisasi anggaran | Departemen lain; laporan realisasi RAPB ke Direktur | Cost Control | P9 | Varians per pos yang bisa ditelusuri, dibaca sesuai hak akses |
| Pencapaian target profit, penilaian realisasi iklan | Departemen lain (peminta tidak disebut di survei) | Cost Control | P9 | Dashboard insentif yang sudah ada ([[Finance - Incentive]]); apakah cakupannya sama dengan yang diminta: TBD |
| Hasil costing HPP | SPV Marketing | AP lewat Supervisor FAT | P11 | TBD bersama P11 |
| Laporan keuangan | Direktur, departemen lain | Senior Accountant | P10 | Laporan dari buku entitas; hak baca per peran (TBD) |

Kode proses: P1 [[Finance - Proses Pengajuan Pengeluaran dan Persetujuan]] · P2 [[Finance - Proses Pembayaran Keluar]] · P3 [[Finance - Proses Penjualan Marketplace dan Uang Masuk]] · P4 [[Finance - Proses Retur dan Piutang Marketplace]] · P5 [[Finance - Proses Rekonsiliasi Kas Toko dan Bank]] · P7 [[Finance - Proses Gaji dan Iuran BPJS]] · P8 [[Finance - Proses Pajak]] · P9 [[Finance - Proses Anggaran, Kas Kecil, dan Dana Kegiatan]] · P10 [[Finance - Proses Tutup Buku, Stock Opname, dan Laporan]] · P11 [[Finance - Proses Costing HPP Produk]].

## Belum Diputuskan (TBD)

- Hak baca laporan keuangan dan realisasi anggaran per peran di luar Finance.
- Cakupan dashboard insentif dibandingkan permintaan pencapaian target profit dan realisasi iklan.

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - FAT Persona]]
- [[REF - Kepemilikan Data]] · [[Microservices - Procurement Service]] · [[Microservices - Payroll Service]] · [[Microservices - Manufacture Service]] · [[Microservices - Integration Service]] · [[Finance - Incentive]]
