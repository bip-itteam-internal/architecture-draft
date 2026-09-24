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
- ⛔ **Mengejar tunggakan MEMINDAHKAN keterlambatannya ke bulan berjalan, tidak menghapusnya** (temuan 2026-09-23). Saat gudang men-scan, tanggal dokumen retur ditulis ulang menjadi tanggal scan sehingga returnya berpindah periode; jam mulai keterlambatan tetap tanggal retur marketplace, jadi ia tetap terhitung telat — sekarang di bulan baru. Terukur prod: **2.993 dari 3.306** dokumen berperiode September masuk lewat jalur ini. Akibatnya bagi AR: metrik **"Penanganan retur di platform atau Expedisi"** (bobot 0,3) sedikit memburuk justru saat tunggakan dibereskan, sementara metrik **"Pencatatan retur penjualan"** (bobot 0,5) membaik. Keduanya bergerak berlawanan untuk tindakan yang sama, dan tak satu pun layar mengatakannya. Yang benar-benar memperbaiki metrik pertama hanya retur yang **selesai dalam ≤14 hari** sejak returnya terjadi. Rinciannya di [[Microservices - Employee Service]] §`retur_lewat_14_persen`.
- ✅ **Angka telat kini bisa ditelusuri jadi daftar ordernya** (bip-erp PR #2018 + erp-frontend PR #1702, PROD 2026-09-23): baris "Telat >14 hari" di rincian KPI dapat diklik, tiap baris membawa tanggal retur asli **dan** tanggal dokumen sekaligus beserta penanda masih-menggantung vs sudah-beres-tapi-telat, plus tautan ke Auto Sync Retur. ⚠️ Daftar itu langsung memperlihatkan dua hal yang sebelumnya tersembunyi di balik satu angka: **order hantu** dari dokumen yang `order_id`-nya bukan anggota `members` (sekitar dua pertiga dari angka telat September; [[Microservices - Integration Service]], akar TBD), dan **retur yang muncul di dua dokumen sekaligus** (708 order, 2026-09-23).
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
