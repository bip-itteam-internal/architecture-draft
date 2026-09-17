# Finance - Proses Aset Tetap

## Deskripsi

*Proses P13, aset tetap, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Aktiva tetap dibaca dari Accurate dan aset GA dipadankan ke Accurate; langkah kerja aset tetap di Finance belum dirinci, dan register aset serta penyusutan buku CV 🟡 direncanakan.
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026), kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17, dan dok GA serta buku besar CV yang ditautkan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Setiap aset tetap tercatat sekali di buku entitasnya dengan nilai perolehan dan penyusutan yang benar, cocok dengan keberadaan fisiknya, dan pembelian aset baru selalu diketahui pencatat register.

## Hari ini (*survei 2026-09*)

Aset tetap dicantumkan sebagai pekerjaan oleh Junior Accountant, Senior Accountant, dan Cost Control; di sisi Junior Accountant disebut juga pengecekan aset, dan daftar perlengkapan atau aset tetap termasuk data yang rutin diminta departemen lain dari Finance. Langkah kerjanya tidak dirinci di isian survei (TBD, dikonfirmasi lewat wawancara). Pencatatan aset ke Accurate adalah hak Finance; staf GA tidak menyentuh Accurate ([[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]]).

## Sudah ada di ERP

- Salinan aktiva tetap dari Accurate dibaca lewat `GET /accounting/fixed-assets` dan `GET /accounting/fixed-assets/summary` di integration-service (`bip-erp/services/integration/main.go:1521-1522`), dipakai kartu dashboard posisi Senior Accountant dan Accounting CV (`erp-frontend/src/features/finance/posisi/components/isi-senior-acc.tsx`, `isi-acc-cv.tsx`).
- Aset dan perlengkapan GA di inventory-service dengan padanan ke nomor aset dan nomor barang Accurate; nilai buku di ERP hanya estimasi, angka resminya milik Accurate ([[REF - Kepemilikan Data]]). Padanan dibuat per item berbasis nama ([[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]]) dan dipindah otomatis saat Accurate mengganti nomor barang ([[ADR - 0088 Auto-Migrasi Padanan Perlengkapan Lewat ID Internal Accurate, Bukan Konfirmasi Manusia]]).
- Pembelian aset di atas ambang lewat jalur aset dengan GA sebagai penyetuju, supaya aset tidak masuk tanpa sepengetahuan pencatat register ([[Finance - Kas Kecil dan Pengajuan Budget]]).
- Rancangan buku besar CV memuat akun akumulasi penyusutan dan penyusutan garis lurus bulanan ([[Finance - Buku Besar CV]]).
- Audit internal punya uji cek fisik aset dan uji kapitalisasi terhadap beban ([[Finance - Audit Internal]]).

## Alur target

Pembelian aset lewat pengajuan jalur aset ([[Finance - Proses Pengajuan Pengeluaran dan Persetujuan]]) → barang diterima dan diberi label GA → Finance mencatat perolehan di buku entitasnya (Accurate untuk PT, buku besar CV untuk CV) → padanan aset GA terbentuk → penyusutan bulanan berjalan otomatis → hasil opname fisik dicocokkan dengan register dan selisihnya bersebab.

## Celah

- **B** Kaitan dari pengajuan jalur aset ke pencatatan aset di buku: apakah sudah memberi tahu Finance secara otomatis belum diperiksa (**TBD**, periksa kode procurement dan inventory sebelum merancang).
- **C** Register aset dan penyusutan untuk buku CV (bagian buku besar CV, T3).
- **TBD** Langkah kerja aset tetap di Finance hari ini, kebijakan kapitalisasi terhadap beban, dan siapa yang boleh mengubah nilai aset.

## Kontrol wajib

Pencatat aset di buku (Finance) bukan pemegang fisik aset (GA); aset yang dibeli lewat pengajuan selalu diketahui pencatat register; perubahan nilai dan penghapusan aset beralasan dan tercatat.

## Ukuran efisiensi

Jumlah aset tanpa padanan GA; selisih register terhadap hasil opname fisik; jumlah aset yang dibeli tanpa lewat jalur aset.

Sumber data baseline: laporan padanan aset GA di inventory-service; salinan aktiva tetap Accurate; hasil opname fisik.

## Proses terkait

- P1: [[Finance - Proses Pengajuan Pengeluaran dan Persetujuan]]
- P6: [[Finance - Proses Pencatatan dan Buku Besar]]
- P10: [[Finance - Proses Tutup Buku, Stock Opname, dan Laporan]]

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[GA - Inventory Management]] · [[Microservices - Inventory Service]] · [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] · [[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]] · [[ADR - 0088 Auto-Migrasi Padanan Perlengkapan Lewat ID Internal Accurate, Bukan Konfirmasi Manusia]] · [[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]]
- [[Finance - Buku Besar CV]] · [[Finance - Audit Internal]] · [[Finance - Kas Kecil dan Pengajuan Budget]] · [[REF - Kepemilikan Data]]
