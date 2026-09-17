# Finance - Proses Pembayaran Keluar

## Deskripsi

*Proses P2, pembayaran keluar (rekening PT dan kas CV), dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Penilaian cakupan dan kesesuaiannya ada di dok induk.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Tahap transfer rekening PT dan kas CV, unggah dan pemeriksaan bukti, serta dokumen pembayaran ada di kode; belum dipakai di prod (0 dokumen pembayaran dan 1 Pengajuan Barang per 2026-09-17) dan jurnal otomatis buku CV 🟡 direncanakan.
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, butir bertanda *survei 2026-09*), kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17. Keadaan prod bertanggal di tiap butir; ukur ulang sebelum dipakai memutuskan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Uang keluar dengan nominal benar, dari rekening yang benar, berbukti, dan tercatat, dengan satu kali input.

## Hari ini (*survei 2026-09*)

- Kas CV: BKK Excel dicetak → unggah AppSheet → input Kopra → persetujuan → unduh bukti → jurnal → arsip AppSheet dan kertas → bukti dikirim lewat WhatsApp. Satu pembayaran diketik empat sampai lima kali, dan proses yang sama berjalan terpisah di tiap kelompok CV. Persetujuan ada dua lapis: Supervisor FAT memeriksa, lalu "atasan" menyetujui di internet banking.
- Iklan: top up juga diinput ke iLink Kas Iklan. Sebagian iklan dibayar ke kas iklan lebih dulu lalu diganti dari kas CV, karena ada bank yang tidak bisa membayar virtual account langsung; satu biaya iklan menjadi dua transfer dan dua jurnal.
- Rekening PT: tagihan masuk → internet banking → BKK/BKM kertas → persetujuan Supervisor FAT → arsip bantex bulanan → bukti lewat WhatsApp.

## Sudah ada di ERP

- Tahap `pb_finance_setujui_bayar` (Supervisor FAT memilih kas CV pembayar) dan `pb_ap_transfer` yang bercabang: rekening PT oleh pemegang `budget.ap.bayar`, kas CV oleh pemegang `budget.cv.transfer` yang ditugaskan ke CV itu (`bip-erp/services/procurement/pengajuan_barang_gate.go:245-284`); antrean transfer CV di layar CV Saya. Rinciannya di [[Finance - Buku Besar CV]].
- Unggah bukti oleh pelaksana, pemeriksaan bukti oleh Senior Accountant, faktur pembelian dari hasil QC, dokumen pembayaran yang dikirim manual ke Accurate (`bip-erp/services/procurement/pembayaran_kirim.go:12-29`), dan jurnal kas ke Accurate di balik saklar `ACCURATE_KAS_PUSH` yang bawaannya mati (`bip-erp/services/procurement/kas_jurnal_handler.go:28-37`).
- Prod 2026-09-17 (jumlah dokumen per koleksi, baca-saja): 0 dokumen pembayaran; 1 Pengajuan Barang, dibuat 2026-09-02; 0 entitas CV dan 0 penugasan pemegang CV.
- **Hutang pemasok dan jatuh tempo**: pengingat harian untuk faktur pembelian yang mendekati jatuh tempo dikirim dengan kategori "perlu dibayar" ke setiap pemegang `budget.ap.bayar` di perusahaan default (`bip-erp/services/procurement/jatuh_tempo_pengingat.go:43-56`, `:110-113`). Per 2026-09-12 pemegang izin itu di Finance hanya Supervisor FAT dan Senior Accountant, sehingga pengingat tidak sampai ke AP ([[Finance - FAT Persona]] § Skenario Gagal). ⚠️ **Pengingat membaca faktur yang tersimpan di ERP, bukan Accurate** (`bip-erp/services/procurement/jatuh_tempo_pengingat.go:64`), dan faktur dari Accurate hanya masuk lewat impor yang dijalankan admin, `POST /tagihan/import` (`bip-erp/services/procurement/main.go:834`); `git grep` 2026-09-17 tidak menemukan pemanggil `ImportFakturDenganKlien` selain rute itu, jadi tak ada penjadwal. Prod 2026-09-17: 2.055 faktur, sama dengan hitungan 2026-07-31, dokumen terbaru dibuat 2026-07-30. Artinya faktur Accurate sesudah impor terakhir tidak pernah diingatkan, dan sisa utang yang dibaca pengingat hanya sebaru impor terakhir. KPI AP menghitung persentase faktur jatuh tempo bulan itu yang dibayar paling lambat pada tanggal jatuh temponya, dari data faktur pembelian Accurate lewat procurement-service (`bip-erp/services/employee/kpi_sumber_ap.go:16-30`); sumber ini membaca daftar faktur Accurate langsung (`bip-erp/services/procurement/kpi_pembayaran.go`), jadi tidak ikut basi seperti pengingat.

## Alur target

Pengajuan disetujui (P1) → antrean bayar di layar pelaksana dengan notifikasi → transfer di bank → unggah bukti → pemeriksaan bukti Senior Accountant → pemohon dikabari otomatis → jurnal otomatis (PT ke Accurate, CV ke buku besar CV). Dokumen pengajuan beserta bukti menjadi arsip; BKK kertas dan AppSheet tidak dibuat lagi.

## Celah

- **A** Paket izin pelaksana bayar terpasang; data 40 CV dan pemegangnya diisi; keputusan bahwa dokumen pengajuan menggantikan BKK dan AppSheet.
- **B** Dokumen pembayaran berstatus PENDING belum punya notifikasi, jadi pengiriman manual ke Accurate bisa terlupa ([[Finance - FAT Persona]] § Skenario Gagal).
- **B** Pembayaran tanpa faktur (tipe DANA, IKLAN, KONSUMSI) dibukukan lewat jurnal umum yang tidak terbit selama saklar kas mati; kapan saklar dinyalakan perlu diputuskan sesudah diuji.
- **C** Jurnal otomatis buku CV dari pembayaran berbukti (T6).
- **A** Pelaksana bayar rekening PT memegang `budget.ap.bayar`, supaya pengingat jatuh tempo hutang pemasok sampai ke orang yang membayar.
- **B** Faktur pemasok di ERP selalu mutakhir terhadap Accurate (impor terjadwal, atau pengingat membaca Accurate langsung seperti KPI AP). Selama belum, pengingat jatuh tempo dan antrean hutang di bawah hanya memuat faktur sampai impor manual terakhir.
- **B** Daftar hutang pemasok yang mendekati atau lewat jatuh tempo tampil sebagai antrean di layar pelaksana bayar; hari ini antrean "perlu dibayar" belum tampil di dashboard AP ([[Finance - FAT Persona]]).
- **TBD** Berkas transfer massal ke bank belum dianalisa.
- **TBD** Siapa "atasan" yang menyetujui di internet banking, dan apakah persetujuan di bank itu tetap ada sesudah persetujuan pindah ke ERP.
- **TBD** Jalur iklan lewat kas iklan lalu diganti kas CV dipertahankan, atau bank pembayar virtual account diganti supaya satu biaya iklan cukup satu transfer.

## Kontrol wajib

Pelaksana transfer, penyetuju, pemeriksa bukti, dan pelaku rekonsiliasi bank adalah peran berbeda.

## Ukuran efisiensi

Jumlah BKK per bulan per CV (ekspor AppSheet), transaksi Kopra per rekening per bulan, lama dari disetujui sampai ditransfer, jumlah pengetikan ulang per pembayaran (target satu), persentase faktur pemasok yang dibayar paling lambat pada tanggal jatuh temponya (sudah dihitung KPI AP).

Sumber data baseline: Ekspor AppSheet tiga bulan (BKK); laporan Kopra dan internet banking (transaksi per rekening); tanggal di berkas dan tahap ERP (lama proses); wawancara alur (pengetikan ulang).

## Proses terkait

- P1: [[Finance - Proses Pengajuan Pengeluaran dan Persetujuan]]

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[Finance - Buku Besar CV]]
