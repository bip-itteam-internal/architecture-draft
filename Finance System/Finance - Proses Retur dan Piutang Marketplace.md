# Finance - Proses Retur dan Piutang Marketplace

## Deskripsi

*Proses P4, retur dan piutang marketplace, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Penilaian cakupan dan kesesuaiannya ada di dok induk.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Sinkron retur bergerbang payout dan scan gudang berjalan; retur yang lolos sinkron dan daftar pengecualian terpadu belum ditangani.
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, butir bertanda *survei 2026-09*), kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17. Keadaan prod bertanggal di tiap butir; ukur ulang sebelum dipakai memutuskan.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Retur dibukukan sekali, sesuai barang yang benar-benar kembali, dan piutang terbuka akurat tanpa basis data kerja paralel.

## Hari ini (*survei 2026-09*)

Retur divalidasi di empat sumber (ERP, marketplace, Accurate, gudang); retur yang belum discan dikejar ke gudang dan ekspedisi (tindak lanjut tiga sampai lima hari); piutang minus ditelusuri karena income yang berubah jadi retur; retur yang ternyata belum terbukukan diunggah manual, dan untuk faktur sejak Juli 2026 dicatat lalu dilaporkan ke IT. Fitur pelacakan cancel dan retur di ERP disebut belum membantu.

## Sudah ada di ERP

Sinkron retur ke Accurate dengan gerbang payout ([[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]]) dan gerbang gudang: retur barang kembali ditahan PENDING sampai gudang men-scan barangnya ([[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]). Per 2026-08-06: 908 baris PENDING, 900 menunggu scan ([[Microservices - Integration Service]]). Order yang dikirim sebelum 1 Juli 2026 memang dibukukan manual oleh Finance.

## Alur target

Gudang men-scan retur tepat waktu → retur terbukukan otomatis → AR menangani pengecualian dari satu daftar di ERP (belum discan, lolos sinkron, piutang minus) → piutang terbuka diperbarui.

## Celah

- **A** Disiplin scan retur di gudang, karena antrean pembukuan retur Finance adalah antrean scan gudang.
- **B** Ukur besar celah retur yang lolos sinkron (rekap unggah manual yang dikirim ke IT adalah sumber volumenya), lalu tutup penyebabnya.
- **B** Satu daftar pengecualian retur dan piutang di ERP untuk menggantikan basis data kerja. 🟡 Sisi retur diusulkan jadi tab **Selisih Retur** di Auto Sync Retur ([[ADR - 0104 Selisih Retur Dihitung Terjadwal per Periode dan Bisa Ditandai Beres]], 2026-09-17): menunggu scan >30 hari, dibukukan tanpa scan, komponen paket belum discan, scan tak sampai pembukuan, dan (Tahap 2) catatan ERP berbeda dari isi Accurate. **Piutang minus dan retur yang lolos sinkron belum tercakup** di sana.
- **TBD** Pemilik pelacakan paket yang tertahan di ekspedisi.
- **TBD** Kenapa fitur pelacakan cancel dan retur yang sudah ada di ERP belum membantu; tanyakan saat wawancara sebelum membangun fitur pelacakan baru.
- **B** Kompensasi TikTok atas pesanan yang uangnya **sudah pernah cair** menambah nilai bayar faktur yang sudah lunas, dan dokumen returnya justru ter-skip. Terukur prod 2026-09-22: **14 pesanan, Rp1.610.697** (lawan 360 pesanan Rp34.872.894 yang sudah benar dan tak boleh disentuh). Sumber piutang minus yang selama ini ditelusuri AR. 🟡 [[ADR - 0119 Kompensasi TikTok Dipisah Menurut Sudah atau Belum Ada Uang Masuk]] (diusulkan, belum di kode) — dua sisi (penerimaan dan gerbang retur) wajib berubah bersamaan.

## Kontrol wajib

Retur yang sudah diserap penerimaan tidak dibukukan lagi (gerbang payout).

## Ukuran efisiensi

Jumlah retur yang diunggah manual per bulan; umur retur PENDING yang menunggu scan.

Sumber data baseline: Rekap unggah manual yang dikirim ke IT; daftar retur PENDING di integration-service.

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] · [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] · [[ADR - 0104 Selisih Retur Dihitung Terjadwal per Periode dan Bisa Ditandai Beres]] · [[Microservices - Integration Service]]
