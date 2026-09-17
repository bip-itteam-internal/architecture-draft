# Finance - Proses Costing HPP Produk

## Deskripsi

*Proses P11, costing HPP produk, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Penilaian cakupan dan kesesuaiannya ada di dok induk.*

- **Status**: 🟡 **Konsep**. Belum ada alur costing di ERP; baru kartu hasil di dashboard AP dan rencana master HPP.
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, butir bertanda *survei 2026-09*), kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17. Keadaan prod bertanggal di tiap butir; ukur ulang sebelum dipakai memutuskan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

HPP produk dihitung dari formula, harga bahan, dan kapasitas yang sama dengan yang dipakai modul lain, lalu disetujui dan dibagikan tanpa berkas terpisah.

## Hari ini (*survei 2026-09*)

Formula dari APJ, harga bahan baku dan kemas diminta ke Procurement, kapasitas produksi dimintakan, HPP dihitung di templat Excel, disetujui Supervisor FAT, lalu dibagikan ke SPV Marketing. Alatnya Excel dan WhatsApp; yang ditunggu data harga bahan.

## Sudah ada di ERP

BOM/formula dan master bahan di manufacture-service ([[Manufacture - Stock & Material Management]]); HPP dipakai perhitungan insentif ([[Finance - Incentive]]); kartu "Costing HPP valid" di dashboard AP (`erp-frontend/src/features/finance/posisi/data/ap.ts:72-78`); rencana master HPP per SKU ([[Sales - HPP Master (Plan)]], 🟡).

## Alur target

TBD. Kandidatnya: formula dari BOM manufaktur, harga bahan dari data pembelian, kapasitas dari PPIC, hasil costing disetujui di ERP dan menjadi HPP yang dibaca insentif.

## Celah

**C** belum jadi task dan belum diputuskan masuk ERP; perlu `/analisa-kebutuhan` karena melibatkan APJ, Procurement, PPIC, dan Marketing. Apakah hasil costing Excel hari ini yang menjadi HPP di insentif: **TBD**.

## Kontrol wajib

Penghitung costing bukan penyetujunya.

## Ukuran efisiensi

Lama dari permintaan costing sampai hasil dibagikan; jumlah costing yang menunggu data harga bahan.

Sumber data baseline: Catatan permintaan dan persetujuan costing.

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[Manufacture - Stock & Material Management]] · [[Finance - Incentive]] · [[Sales - HPP Master (Plan)]]
