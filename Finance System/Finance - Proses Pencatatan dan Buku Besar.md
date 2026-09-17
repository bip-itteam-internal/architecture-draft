# Finance - Proses Pencatatan dan Buku Besar

## Deskripsi

*Proses P6, pencatatan dan buku besar, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Penilaian cakupan dan kesesuaiannya ada di dok induk.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Buku PT lewat Accurate dengan pengiriman otomatis sebagian; buku CV di ERP 🟡 direncanakan (T3 sampai T6, T10), menunggu persetujuan ADR 0096.
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, butir bertanda *survei 2026-09*), kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17. Keadaan prod bertanggal di tiap butir; ukur ulang sebelum dipakai memutuskan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Setiap transaksi dicatat sekali di buku entitasnya, dan diperiksa sebelum masuk laporan.

## Hari ini (*survei 2026-09*)

Buku PT di Accurate, buku 40 CV di aplikasi luar ERP ([[APP - Buku Besar Konsolidasi CV FINCON]]); jurnal diketik manual per CV; hasil sinkron marketplace dan input jurnal harian (termasuk admin gudang dan produksi) diperiksa Senior Accountant setiap hari.

## Sudah ada di ERP

Pengiriman otomatis faktur, retur, dan penerimaan marketplace ke Accurate (P3, P4); jurnal kas kecil ke Accurate lewat outbox ([[Finance - Kas Kecil dan Pengajuan Budget]]); master entitas CV, penugasan pemegang, dan cakupan per CV (T1, merge 2026-09-16).

## Alur target

Buku PT tetap Accurate; buku CV di ERP (T3 sampai T5) dengan jurnal otomatis dari pembayaran dan kas kecil (T6), penjualan per CV (T8), dan gaji (T7); jurnal manual tinggal untuk yang benar-benar tidak punya sumber sistem, dan diperiksa sebelum diposting.

## Celah

**C** T3 sampai T6 dan T10, menunggu persetujuan ADR 0096. Aturannya (dokumen atomik, nominal sen bilangan bulat, kunci periode, jurnal balik, jejak sumber) di [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] dan [[Finance - Buku Besar CV]].

## Kontrol wajib

Pencatat bukan pemeriksa; periode terkunci tidak bisa ditulisi.

## Ukuran efisiensi

Porsi jurnal CV yang terbit otomatis; jumlah jurnal yang dikoreksi saat pemeriksaan.

Sumber data baseline: Buku besar CV sesudah T6 (porsi jurnal otomatis); catatan pemeriksaan (jurnal dikoreksi).

## Proses terkait

- P3: [[Finance - Proses Penjualan Marketplace dan Uang Masuk]]
- P4: [[Finance - Proses Retur dan Piutang Marketplace]]

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[APP - Buku Besar Konsolidasi CV FINCON]] · [[Finance - Kas Kecil dan Pengajuan Budget]] · [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] · [[Finance - Buku Besar CV]]
