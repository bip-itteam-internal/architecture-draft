# Finance - Proses Pajak

## Deskripsi

*Proses P8, pajak, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Penilaian cakupan dan kesesuaiannya ada di dok induk.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Tax Control ada di kode; master jenis pajak dan kewajiban di prod masih kosong (2026-09-12), dan data acuan satu sumber belum ada.
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, butir bertanda *survei 2026-09*), kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17. Keadaan prod bertanggal di tiap butir; ukur ulang sebelum dipakai memutuskan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Kewajiban pajak dihitung dari data acuan yang sama dengan pembukuan, dilaporkan dan dibayar tepat waktu, dengan titik cut-off yang disepakati.

## Hari ini (*survei 2026-09*)

Data transaksi dicek dan dikonfirmasi, catatan perusahaan diekualisasi dengan Coretax, data diinput ke Coretax, kode billing dibuat tanggal 1 sampai 3 (PPh final, PPh 21, PPh 25) dan tanggal 20 (PPh 23, PPN), lalu pajak dibayar Junior Accountant. Hampir semua data diketik ulang; hambatan utamanya menentukan data acuan dan cut-off; pos persediaan hanya tersedia sebagai angka tanpa rincian.

## Sudah ada di ERP

Tax Control berisi kewajiban per masa, pengingat jatuh tempo H-7 dan H-3, pencatatan pelaporan, dan unggah BPE serta bukti bayar ([[API - Finance Service]], [[Finance - Rancangan Finance Service]]). Prod 2026-09-12: master jenis pajak dan kewajiban masih 0.

## Alur target

Kewajiban per masa terbit di Tax Control → data penjualan per entitas (P3), pembelian dan pembayaran (P2), dan gaji (P7) ditarik dari satu sumber → ekualisasi dan input Coretax (tetap di DJP) → kode billing dibayar lewat P2 → BPE diunggah ke Tax Control.

## Celah

- **A** Master jenis pajak diisi, paket `finance_pajak` dipasang.
- **C** Omzet per entitas dari T8 dan data pembelian/pembayaran dari P2 yang benar-benar dipakai.
- **TBD** Rincian pos persediaan dan titik cut-off yang disepakati bersama P10.

## Kontrol wajib

Yang menghitung kewajiban bukan satu-satunya yang memeriksa angka laporan.

## Ukuran efisiensi

Jumlah data yang diketik ulang untuk satu masa pajak; kewajiban yang dilaporkan lewat tenggat.

Sumber data baseline: Catatan Tax per masa (data diketik ulang, pelaporan lewat tenggat).

## Proses terkait

- P2: [[Finance - Proses Pembayaran Keluar]]
- P3: [[Finance - Proses Penjualan Marketplace dan Uang Masuk]]
- P7: [[Finance - Proses Gaji dan Iuran BPJS]]
- P10: [[Finance - Proses Tutup Buku, Stock Opname, dan Laporan]]

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[API - Finance Service]] · [[Finance - Rancangan Finance Service]]
