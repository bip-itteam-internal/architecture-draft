# Finance - Proses Anggaran, Kas Kecil, dan Dana Kegiatan

## Deskripsi

*Proses P9, anggaran, kas kecil, dan dana kegiatan, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Penilaian cakupan dan kesesuaiannya ada di dok induk.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Master anggaran, varians, dan kas kecil ada (kas kecil dipakai); varians belum bisa ditelusuri ke transaksi dan pertanggungjawaban dana kegiatan belum ada.
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, butir bertanda *survei 2026-09*), kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17. Keadaan prod bertanggal di tiap butir; ukur ulang sebelum dipakai memutuskan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Pengeluaran dikendalikan terhadap anggaran, kas kecil tertib per unit, dan dana kegiatan dipertanggungjawabkan sampai sisa dikembalikan atau kekurangan diganti.

## Hari ini (*survei 2026-09*)

Realisasi anggaran dicek di Accurate setiap pagi; pengajuan dari divisi diperiksa kelengkapan dokumen dan anggarannya; dana kegiatan dicairkan lalu laporan pemakaian dan buktinya dicocokkan, dengan penyelesaian berupa input, pengembalian dana, atau reimburse; laporan realisasi RAPB disusun sesudah cut-off akhir bulan. Angka varians di ERP sulit dijelaskan karena transaksi pembentuknya tidak terlihat. Forecast kas tercantum sebagai salah satu pekerjaan di sisi ini; langkah kerjanya tidak dirinci (TBD).

## Sudah ada di ERP

Master anggaran OPEX, kartu Varians OPEX, breakdown mingguan anggaran terhadap realisasi, dan laporan Admin & Non-Ops (`erp-frontend/src/features/finance/anggaran/`, data di integration-service `anggaran_opex`, [[REF - Kepemilikan Data]]); kas kecil dengan verifikasi Finance dan jurnal ke Accurate ([[Finance - Kas Kecil dan Pengajuan Budget]]); rekomendasi efisiensi (0 dokumen di prod 2026-09-12). Forecast kas mingguan: panel proyeksi terhadap realisasi per minggu beserta akurasinya di layar anggaran (`erp-frontend/src/features/finance/anggaran/components/panel-forecast-kas.tsx`); barisnya per akun anggaran (`erp-frontend/src/features/finance/anggaran/types-mingguan.ts:36`), dan akurasinya tidak terdefinisi bila anggaran periode itu belum diunggah (`:27`). KPI `forecast_kas` membaca `GET /accounting/anggaran/mingguan/kpi` untuk metrik "forecast cashflow mingguan" (`bip-erp/services/employee/kpi_sumber_forecast_kas.go:15`, `:31`).

## Alur target

Pengajuan membawa pos anggaran (P1) → realisasi per pos bisa ditelusuri sampai transaksinya → dana kegiatan tercatat dari pencairan sampai pertanggungjawaban → laporan realisasi tersusun dari data yang sama.

## Celah

- **B** Varians bisa ditelusuri ke transaksi. Kartu Varians OPEX hanya menyajikan total dan cacah pos lewat anggaran (`kartu-varians-opex.tsx:65-94`), dan komponen anggaran tidak menaut ke transaksi Accurate mana pun.
- **B** Pengajuan tersambung ke pos anggaran (sama dengan P1).
- **TBD** Cakupan forecast kas. Proyeksinya disusun per akun anggaran, jadi yang terlihat adalah pengeluaran beranggaran; apakah uang masuk (penarikan marketplace, pelunasan piutang) dan pembayaran terjadwal (gaji, pajak, hutang pemasok jatuh tempo) ikut diperhitungkan belum diperiksa di integration-service. Periksa sebelum menjadikannya forecast kas perusahaan.
- **C** Pertanggungjawaban dana kegiatan. `git grep` 2026-09-17 atas `bip-erp/services` tidak menemukan alur uang muka sampai pertanggungjawaban; perlu `/analisa-kebutuhan` lebih dulu (apakah memperluas tipe DANA atau modul sendiri).

## Kontrol wajib

Pengaju bukan pemeriksa anggaran; penerima dana kegiatan bukan yang menyetujui pertanggungjawabannya.

## Ukuran efisiensi

Jumlah pertanyaan varians yang harus ditelusuri manual; umur dana kegiatan yang belum dipertanggungjawabkan; akurasi forecast kas mingguan (sudah dihitung KPI `forecast_kas`).

Sumber data baseline: Catatan Cost Control (pertanyaan varians, umur dana kegiatan).

## Proses terkait

- P1: [[Finance - Proses Pengajuan Pengeluaran dan Persetujuan]]

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[REF - Kepemilikan Data]] · [[Finance - Kas Kecil dan Pengajuan Budget]]
