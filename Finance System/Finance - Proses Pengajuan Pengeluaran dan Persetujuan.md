# Finance - Proses Pengajuan Pengeluaran dan Persetujuan

## Deskripsi

*Proses P1, pengajuan pengeluaran dan persetujuan, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Penilaian cakupan dan kesesuaiannya ada di dok induk.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Pengajuan Barang, pengajuan budget, dan kas kecil ada di kode; pengajuan belum membawa pos anggaran, kotak persetujuan belum memuatnya, dan di prod hampir tak dipakai (1 pengajuan barang per 2026-09-12).
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, butir bertanda *survei 2026-09*), kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17. Keadaan prod bertanggal di tiap butir; ukur ulang sebelum dipakai memutuskan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Setiap pengeluaran punya pengajuan lengkap, dicek terhadap anggaran, dan disetujui orang yang berwenang, tanpa berpindah lewat chat.

## Hari ini (*survei 2026-09*)

Permintaan datang lewat WhatsApp, Excel, dan email. Cost Control memeriksa kelengkapan dokumen dan anggaran lalu menyerahkan form ke Finance untuk dibayar. Persetujuan Supervisor FAT, lalu persetujuan di bank, disebut titik antre.

## Sudah ada di ERP

Pengajuan Barang lima tipe (UMUM, RAWMATERIAL, IKLAN, DANA, KONSUMSI) dengan tahap per izin, termasuk Supervisor FAT dan Direktur di atas ambang ([[Microservices - Procurement Service]]); pengajuan budget dan kas kecil ([[Finance - Kas Kecil dan Pengajuan Budget]]). Prod 2026-09-12: 1 pengajuan barang.

## Alur target

Pemohon membuka pengajuan di ERP beserta lampiran dan pos anggaran → sistem menandai bila melampaui pos → Cost Control memeriksa → Supervisor FAT menyetujui dari satu kotak persetujuan → Direktur bila di atas ambang → masuk antrean P2 dengan notifikasi ke pelaksana bayar.

## Celah

- **A** Pemohon di semua divisi memakai Pengajuan Barang; paket izin terpasang.
- **A** Ambang Direktur diatur. Bernilai nol berarti tahap Direktur tidak disisipkan (`bip-erp/services/procurement/pengajuan_barang_jenjang.go:154-157`).
- **B** Pengajuan membawa pos anggaran yang dibebaninya. Dashboard AP sendiri mencatat metrik "Expense di luar anggaran" berstatus belum karena pengajuan beserta pos anggarannya belum tercatat di sistem (`erp-frontend/src/features/finance/posisi/data/ap.ts:64-71`).
- **B** Pengajuan barang yang menunggu Supervisor FAT tampil di kotak persetujuan dashboard, yang hari ini hanya memuat proposal dan aksi Sadewa serta insentif DRAFT (`bip-erp/services/integration/internal/interface/http/persetujuan_handler.go:16-19`).
- **TBD** Pembayaran pajak, iuran BPJS, dan hutang supplier CV belum punya tipe pengajuan khusus; apakah lewat tipe DANA, P7, P8, atau jalur sendiri belum diputuskan.
- Pengajuan budget berhenti di status DISETUJUI; pencairannya di luar modul (`bip-erp/services/procurement/main.go:754-758`).

## Kontrol wajib

Pemohon, pemeriksa anggaran, dan penyetuju adalah peran berbeda.

## Ukuran efisiensi

Lama dari pengajuan sampai disetujui; porsi permintaan yang masih datang lewat chat.

Sumber data baseline: Tanggal di berkas hari ini; tanggal tahap di ERP sesudahnya.

## Proses terkait

- P2: [[Finance - Proses Pembayaran Keluar]]
- P7: [[Finance - Proses Gaji dan Iuran BPJS]]
- P8: [[Finance - Proses Pajak]]

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[Microservices - Procurement Service]] · [[Finance - Kas Kecil dan Pengajuan Budget]]
