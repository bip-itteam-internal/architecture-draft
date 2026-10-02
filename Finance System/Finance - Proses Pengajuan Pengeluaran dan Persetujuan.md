# Finance - Proses Pengajuan Pengeluaran dan Persetujuan

## Deskripsi

*Proses P1, pengajuan pengeluaran dan persetujuan, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Penilaian cakupan dan kesesuaiannya ada di dok induk.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Pengajuan Barang, pengajuan budget, dan kas kecil ada di kode (disinkronkan 2026-10-02); pengajuan belum membawa pos anggaran, kotak persetujuan dashboard belum memuatnya, dan pemakaian prod terbaru belum diukur ulang (1 pengajuan barang per 2026-09-12; sesi sinkron ini tidak mengukur prod).
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, butir bertanda *survei 2026-09*), kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17. Keadaan prod bertanggal di tiap butir; ukur ulang sebelum dipakai memutuskan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Setiap pengeluaran punya pengajuan lengkap, dicek terhadap anggaran, dan disetujui orang yang berwenang, tanpa berpindah lewat chat.

## Hari ini (*survei 2026-09*)

Permintaan datang lewat WhatsApp, Excel, dan email. Cost Control memeriksa kelengkapan dokumen dan anggaran lalu menyerahkan form ke Finance untuk dibayar. Persetujuan Supervisor FAT, lalu persetujuan di bank, disebut titik antre.

## Sudah ada di ERP

Pengajuan Barang lima tipe (UMUM, RAWMATERIAL, IKLAN, DANA, KONSUMSI), disinkronkan ke kode 2026-10-02. Urutan tahap per tipe, izin, dan mekanismenya hanya ditulis di [[Microservices - Procurement Service]] (jangan disalin ke sini); pengajuan budget dan kas kecil di [[Finance - Kas Kecil dan Pengajuan Budget]]. Prod 2026-09-12: 1 pengajuan barang (belum diukur ulang). Yang dialami tiap peran:

- **Pemohon.** Tipe yang boleh diajukan ditentukan departemennya, bukan izin pribadi. Pengajuan hanya bisa dibuat dan diajukan ulang dalam **jendela jam** yang diatur Finance (di luar jam, layar menolak dan menyebut kapan dibuka lagi). Harga item wajib untuk tipe uang. Bila dikembalikan untuk revisi, pemohon boleh mengubah isi, sumber dana, dan tujuan dana, lalu dokumen kembali langsung ke tahap yang meminta revisi; atasan yang sudah menyetujui tidak ditanya ulang.
- **Atasan divisi, SPV Finance, Direktur.** Tahap persetujuan; pengaju tidak boleh menyetujui pengajuannya sendiri. Direktur hanya di atas ambang (IKLAN tidak pernah lewat Direktur). SPV Finance memegang dua tahap: menyetujui, lalu (tipe uang) mengonfirmasi transfer sesudah AP menandai. Di tab daftar, SPV Finance bisa menyetujui dan mengonfirmasi transfer secara massal.
- **Cost Control.** Tahap sendiri di depan SPV Finance: memeriksa bukti, memilih CV/rekening pembayar, boleh mengisi nominal realisasi (layar meminta konfirmasi bila nominal berubah). Cost Control boleh menyetujui tahap ini atas pengajuannya sendiri, karena hanya satu orang.
- **Staf AP.** Antrean dan notifikasi hanya untuk dokumen bagian PIC-nya; tab Semua tetap memuat seluruh pengajuan. AP boleh menandai transfer pengajuannya sendiri; mata kedua adalah konfirmasi SPV Finance.
- **Accounting.** Menerima dokumen tipe uang di antreannya hanya setelah bukti transfer diunggah AP, memasangkan akun COA (termasuk akun neraca kepala 1 dan 2), project, dan departemen, lalu mencatat ke Accurate.
- **Semua peran.** Daftar hanya memuat pengajuan departemen sendiri, kecuali Finance. Tiap orang dikabari sekali per pengajuan per siklus; selebihnya lewat antrean "Perlu Aksi Saya" dan tab kerja yang hanya maju (Perlu Disetujui, Sudah Disetujui, Perlu Konfirmasi Transfer, Sudah Ditransfer).

## Alur target

Pemohon membuka pengajuan di ERP beserta lampiran dan pos anggaran → sistem menandai bila melampaui pos → atasan divisi → Cost Control memeriksa → Supervisor FAT menyetujui dari satu kotak persetujuan → Direktur bila di atas ambang → masuk antrean P2 dengan notifikasi ke pelaksana bayar. Urutan di kode memang Cost Control sebelum SPV Finance; pos anggaran belum ada (celah B di bawah).

## Celah

- **A** Pemohon di semua divisi memakai Pengajuan Barang; paket izin terpasang.
- **A** Ambang Direktur diatur. Bernilai nol berarti tahap Direktur tidak disisipkan (`bip-erp/services/procurement/pengajuan_barang_jenjang.go:262`).
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
