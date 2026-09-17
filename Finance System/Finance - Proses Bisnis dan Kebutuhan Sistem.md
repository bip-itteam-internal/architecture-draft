# Finance - Proses Bisnis dan Kebutuhan Sistem

## Deskripsi

*Pintu masuk panduan membangun sistem yang membantu proses bisnis Finance bekerja lebih efisien. Dok ini memuat peta sebelas proses bisnis Finance, penilaian seberapa jauh ERP sudah mencakup dan sesuai dengan kebutuhan tiap proses, prinsip rancangan, urutan pengerjaan, dan keputusan yang dibutuhkan. Rincian tiap proses ada di dok prosesnya masing-masing; kalender tenggat dan sambungan lintas departemen punya dok sendiri.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Sebagian besar proses sudah punya modul di kode tetapi belum dipakai di prod atau belum sesuai kebutuhan; sebagian lain 🟡 direncanakan (buku besar CV, penjualan per CV, mutasi bank, payroll ke bank) atau belum diputuskan. Keadaan kode diperiksa ke `origin/main` 2026-09-17; keadaan prod bertanggal, ukur ulang sebelum dipakai memutuskan.
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, pola prosesnya di [[Finance - FAT Persona]]), kode `bip-erp` dan `erp-frontend`, dan dok domain yang ditautkan. Durasi isian survei tidak andal dan tidak dipakai.
- **Bukan**: daftar orang, jumlah pemegang jabatan, atau usulan susunan organisasi. Panduan ini tentang proses dan sistemnya.

## Cara memakai panduan ini

1. Pilih proses di § Peta proses, lalu buka dok prosesnya.
2. Kerjakan dulu celah kelompok **A** proses itu, lalu **B**, baru **C** (§ Kelompok kebutuhan).
3. Sebelum `/start-task`, jawab § Pertanyaan wajib sebelum membangun dan catat baseline dari bagian Ukuran efisiensi di dok proses.
4. Tenggat yang menyangkut proses itu ada di [[Finance - Kalender dan Rantai Tenggat]]; departemen lain yang harus ikut ada di [[Finance - Sambungan dan Permintaan Data Lintas Departemen]].
5. Nomor task T1 sampai T10 mengikuti urutan pekerjaan buku besar CV di [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]].

## Peta proses

| Kode | Dok proses | Peran Finance | Departemen lain | Hari ini |
|---|---|---|---|---|
| P1 | [[Finance - Proses Pengajuan Pengeluaran dan Persetujuan]] | Cost Control, Supervisor FAT | Semua divisi pemohon, Direktur | Chat, Excel, berkas |
| P2 | [[Finance - Proses Pembayaran Keluar]] | AP, Junior Accountant, Supervisor FAT, Senior Accountant | Pemohon, Procurement, bank | BKK, AppSheet, internet banking, arsip kertas |
| P3 | [[Finance - Proses Penjualan Marketplace dan Uang Masuk]] | AR, Junior Accountant, Tax | IT, marketplace | Rekap Excel, alat web terpisah |
| P4 | [[Finance - Proses Retur dan Piutang Marketplace]] | AR | Gudang, IT, ekspedisi | Basis data kerja sendiri, unggah manual |
| P5 | [[Finance - Proses Rekonsiliasi Kas Toko dan Bank]] | AR, Senior Accountant, Junior Accountant, AP | IT, bank | Excel, diulang sampai cocok |
| P6 | [[Finance - Proses Pencatatan dan Buku Besar]] | Junior Accountant, Senior Accountant | Admin gudang dan produksi | Accurate (PT), FINCON (CV), jurnal manual |
| P7 | [[Finance - Proses Gaji dan Iuran BPJS]] | Cost Control, Senior Accountant, Junior Accountant | HR | Rekap dari HR diketik ulang |
| P8 | [[Finance - Proses Pajak]] | Tax, Junior Accountant | Procurement, DJP | Excel, Coretax, hampir semua diketik ulang |
| P9 | [[Finance - Proses Anggaran, Kas Kecil, dan Dana Kegiatan]] | Cost Control | Semua divisi, GA | Accurate, Excel, kertas |
| P10 | [[Finance - Proses Tutup Buku, Stock Opname, dan Laporan]] | Senior Accountant, Cost Control | Gudang, Direktur | Excel, Accurate |
| P11 | [[Finance - Proses Costing HPP Produk]] | AP | APJ, Procurement, PPIC, SPV Marketing | Templat Excel, WhatsApp |

## Cakupan dan kesesuaian (2026-09-17)

Dua pertanyaan dijawab terpisah: apakah prosesnya **tercover** modul ERP, dan apakah modul itu **sesuai** dengan yang dibutuhkan pemakainya. Alasan rincinya di bagian Celah tiap dok proses.

| Kode | Tercover di ERP | Sesuai kebutuhan | Inti alasannya |
|---|---|---|---|
| P1 | Ada | Sebagian | Rantai persetujuan sesuai; pengajuan belum membawa pos anggaran, kotak persetujuan Supervisor FAT belum memuatnya, jalur pajak, BPJS, dan hutang CV belum ada; hampir tak dipakai |
| P2 | Ada (rekening PT dan kas CV) | Sebagian | Arah menghapus BKK dan AppSheet tepat; notifikasi pembayaran PENDING, saklar jurnal kas, dan jalur iklan lewat kas iklan belum; belum dipakai |
| P3 | Sebagian | Sebagian | Sinkron marketplace ke Accurate menolong; penjualan dan penarikan per CV, kebutuhan utamanya, belum ada |
| P4 | Sebagian | Kurang | Validasi di empat sumber masih manual, ada retur yang lolos sinkron, fitur pelacakan cancel dan retur disebut belum membantu |
| P5 | Sebagian | Tidak sesuai | Layar rekonsiliasi kas toko tidak cocok dengan format kerja; impor mutasi bank belum ada |
| P6 | PT lewat Accurate; CV belum | CV belum | Buku 40 CV masih di luar ERP dengan jurnal manual; T3 sampai T6 menunggu ADR 0096 |
| P7 | Sebagian | Belum menjawab kebutuhan Finance | Perhitungan payroll ada; daftar transfer bank, rekap iuran BPJS, dan jurnal gaji belum; payroll baru dua kali dijalankan di prod |
| P8 | Ada (Tax Control) | Kurang | Hambatan utama (data acuan dan cut-off) tidak dijawab modul; master pajak di prod kosong |
| P9 | Sebagian | Sebagian | Kas kecil dipakai; varians tidak bisa ditelusuri ke transaksi; pertanggungjawaban dana kegiatan belum ada |
| P10 | Sebagian | Kurang | Laporan dibaca dari Accurate; daftar periksa tutup buku dan opname digital belum ada |
| P11 | Belum | Belum | Seluruhnya di Excel dan WhatsApp |

**Ringkasan**: 3 proses sudah ada di kode (P1, P2, P8), 6 tercover sebagian (P3, P4, P5, P7, P9, P10), dan 2 belum (buku CV di P6, dan P11). Tidak ada proses yang sudah sesuai penuh sekaligus dipakai.

**Penilaian pengguna** (*survei 2026-09*, digabung per sisi pekerjaan): peran di sisi data marketplace menilai ERP terbantu; peran di sisi pembayaran, buku CV, pajak, dan kendali anggaran menilai sedikit terbantu atau belum memakai ERP untuk pekerjaan Finance.

**Kesimpulan**:

1. **ERP kuat di sisi yang otomatis, lemah di kerja manual harian.** Sinkron marketplace ke Accurate menolong; pembayaran, buku CV, rekonsiliasi, dan pajak, tempat beban harian terbesar, belum tertolong.
2. **Sebagian modul dirancang untuk proses yang berbeda dari praktik.** Pembayaran semula dirancang terpusat padahal praktiknya per CV (disesuaikan lewat T2); Tax Control mengandaikan data pajak sudah siap padahal masalahnya menyiapkan data itu; layar rekonsiliasi tidak mengikuti format kerja pemakainya.
3. **Kebutuhan terbesar belum dijawab**: data per CV, rekonsiliasi yang bisa dipercaya, dan payroll ke bank.
4. **Belum bisa dinilai**: sisi persetujuan (belum terwakili di survei), format rekonsiliasi yang dibutuhkan, dan alasan fitur pelacakan retur tidak membantu. Ketiganya ditanyakan langsung sebelum dibangun, supaya tidak mengulang pola "ada tapi tidak sesuai".

## Prinsip rancangan

1. **Pakai yang sudah ada sebelum membangun.** Rantai pengajuan, pembayaran, bukti transfer, kas kecil, payroll, dan Tax Control sudah ada di kode. Membangun tambahan di atas modul yang belum dipakai menghasilkan nol efisiensi.
2. **Data diinput sekali, oleh pemiliknya, di sumbernya.** Pemohon mengajukan sendiri, HR menjalankan payroll, gudang men-scan retur. Finance memeriksa dan memakai, bukan mengetik ulang. Pemilik tiap fakta ada di [[REF - Kepemilikan Data]].
3. **Satu data acuan untuk semua pemakai.** Penjualan per entitas, omzet pajak, dan jurnal diambil dari data yang sama, bukan direkap ulang tiap posisi. Basis data kerja paralel di Excel adalah gejala data sistem belum dipercaya; yang diperbaiki datanya, bukan dibuatkan basis data baru.
4. **Pemisahan tugas dijaga, pengetikan ulang dihapus.** Pembuat, pemeriksa, penyetuju, dan pelaku rekonsiliasi tetap peran berbeda. Otomasi menghapus langkah ketik ulang dan arsip ganda, tidak menghapus pemeriksanya.
5. **Keadaan menunggu harus terlihat dan memberi tahu.** Setiap langkah yang menunggu orang lain punya antrean di layar pelakunya dan notifikasi; menunggu tanpa pemberitahuan adalah alur putus.
6. **Angka yang belum lengkap harus mengaku.** Layar yang menjumlah data sebagian menyebut apa yang tidak ikut dihitung (contoh yang sudah ada: kartu Varians OPEX, `erp-frontend/src/features/finance/anggaran/components/kartu-varians-opex.tsx:107-140`).
7. **Batas sistem jelas.** ERP tidak memindahkan uang (transfer tetap di bank) dan tidak menggantikan Coretax. Buku PT tetap di Accurate ([[ADR - 0001 Akuntansi via Accurate]]); buku CV diarahkan ke ERP ([[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]]).
8. **Efisiensi dibuktikan dengan ukuran sebelum dan sesudah**, bukan dengan fitur yang sudah rilis.
9. **Tenggat tampil di kalender terpusat, bukan kalender sendiri.** Fitur bertanggal mendaftarkan feed ke [[Microservices - Calendar Service]]; rinciannya di [[Finance - Kalender dan Rantai Tenggat]].
10. **Yang meminta data melihatnya sendiri.** Data yang rutin diminta dari Finance disediakan di layar peminta sesuai hak aksesnya, bukan dikirim ulang lewat chat; daftarnya di [[Finance - Sambungan dan Permintaan Data Lintas Departemen]].

## Kelompok kebutuhan

| Kelompok | Arti | Isi |
|---|---|---|
| **A. Sudah ada, tinggal dipakai** | Tanpa kode baru; butuh keputusan, paket izin, data master, dan keterlibatan departemen lain | Pengajuan Barang dan pembayaran (P1, P2); Tax Control (P8); payroll oleh HR (P7); disiplin scan retur gudang (P4) |
| **B. Sudah ada, perlu diperbaiki** | Perubahan kecil sampai menengah pada modul yang ada | Pengajuan tersambung pos anggaran (P1, P9); kotak persetujuan memuat pengajuan barang (P1); notifikasi pembayaran PENDING (P2); format rekonsiliasi kas toko dan celah retur (P4, P5); varians yang bisa ditelusuri (P9) |
| **C. Belum ada, perlu dibangun** | Modul atau alur baru | Payroll ke bank, BPJS, dan jurnal gaji (T7); impor mutasi bank dan rekonsiliasi (T9); penjualan per CV (T8); buku besar CV, laporan, migrasi, jurnal otomatis (T3 sampai T6); daftar periksa tutup buku (T10); pertanggungjawaban dana kegiatan; costing HPP |
| **D. Sengaja tidak dibangun** | Di luar batas sistem | Lihat § Yang sengaja tidak dibangun |

## Urutan pengerjaan dan ketergantungan

1. **Kelompok A.** Paling murah dan paling besar dampaknya pada pengetikan ulang. Tidak menunggu ADR 0096, tetapi menunggu keputusan di § Keputusan yang dibutuhkan.
2. **Kelompok B.** Perbaikan kecil yang langsung terasa pada rekonsiliasi dan kendali anggaran.
3. **T7 dan T9**, karena tidak bergantung pada buku besar CV untuk daftar transfer, rekap iuran, dan impor mutasi.
4. **T8, lalu T3 sampai T6 dan T10**, sesudah ADR 0096 disetujui.
5. **Pertanggungjawaban dana kegiatan dan costing HPP** lewat `/analisa-kebutuhan` masing-masing.

Urutan orang dan sistem: sistem dipakai lebih dulu, baru cara kerja manual yang digantikannya dihentikan. Menghentikan cara manual sebelum sistemnya berjalan memindahkan beban, tidak menghapusnya. Masa jalan paralel (mis. buku CV bersama FINCON satu siklus, T5) sementara menambah kerja dan perlu dijadwalkan di luar minggu tutup buku.

**Mulai bertahap dan terukur.** Kelompok A dijalankan dulu pada lingkup kecil, misalnya satu atau dua CV membayar lewat Pengajuan Barang selama satu bulan, dengan baseline dari dok proses diambil sebelumnya. Hasilnya dibandingkan sebelum cakupan diperluas ke seluruh CV dan rekening PT.

**Kapasitas IT ikut dihitung.** Survei mencatat perbaikan data atau sistem ditunggu 1 sampai 5 hari per kasus. Tiap modul baru menambah hal yang bisa salah dan harus diperbaiki; tanpa kapasitas perbaikan, efisiensi di Finance berpindah menjadi antrean di IT. Sebelum modul dirilis, tetapkan siapa menangani laporan selisih dan berapa lama targetnya.

## Pertanyaan wajib sebelum membangun

Setiap fitur untuk proses Finance menjawab enam pertanyaan ini di rencana `/plan`:

1. **Pengetikan ulang mana yang hilang?** Sebut langkah manual hari ini yang tidak dikerjakan lagi. Fitur yang tidak menghapus langkah manual apa pun perlu alasan lain untuk dibangun.
2. **Siapa menginput, di mana sumbernya?** Pemilik datanya menurut [[REF - Kepemilikan Data]]; Finance tidak menjadi juru ketik data departemen lain.
3. **Kontrol mana yang dijaga?** Sebut pembuat, pemeriksa, dan penyetuju, dan pastikan tidak menyatu di satu peran.
4. **Keadaan menunggu terlihat di mana?** Antrean di layar pelaku berikutnya dan notifikasinya.
5. **Apa yang terjadi bila datanya belum lengkap atau salah?** Layar mengaku, bukan menampilkan angka yang tampak utuh.
6. **Ukuran sebelum dan sesudahnya apa?** Ambil dari bagian Ukuran efisiensi di dok proses dan catat baseline-nya sebelum rilis. Isian durasi survei tidak andal, jadi ukurannya dari data objektif.

## Keputusan yang dibutuhkan

Diputuskan Supervisor FAT atau manajemen sebelum kelompok A berjalan:

- Persetujuan [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]].
- Dokumen pengajuan menggantikan BKK dan arsip AppSheet atau tidak.
- Pemisahan pembuat, pemeriksa, penyetuju, dan pelaku rekonsiliasi pada P2 dan P5.
- Ambang persetujuan Direktur dan kemungkinan delegasi persetujuan.
- Makna hutang supplier CV (hutang ke PT atau bukan) dan jalur pembayarannya ([[Finance - Buku Besar CV]] § Belum Diputuskan).
- Pemeriksaan rekap gaji dari dua sudut tetap dua langkah atau tidak (P7).
- Kapan saklar jurnal kas `ACCURATE_KAS_PUSH` dinyalakan (P2).
- Tanggal di [[Finance - Kalender dan Rantai Tenggat]] dijadikan tenggat resmi atau tidak.

## Yang sengaja tidak dibangun

- **Buku PT di luar Accurate.** ERP mengirim ke Accurate, bukan menggantikannya ([[ADR - 0001 Akuntansi via Accurate]]).
- **Aplikasi pajak pengganti Coretax.** Yang dibutuhkan data acuan, bukan pelaporan tandingan.
- **Transfer uang dari ERP.** Transfer tetap dikerjakan di bank; ERP mencatat, menyetujui, dan menyimpan bukti.
- **Versi ERP dari BKK kertas dan AppSheet.** Dokumen pengajuan menggantikannya.
- **Basis data kerja baru untuk AR.** Yang dibutuhkan data marketplace yang bisa dipercaya dan daftar pengecualian.
- **Buku CV paralel di luar ERP.** FINCON dijadikan spesifikasi lalu dipensiunkan (T10), bukan dirawat bersama.

## Belum Diputuskan (TBD)

- Hal yang belum diputuskan per proses tercatat di bagian Celah dok prosesnya, bertanda **TBD**.
- Sisi persetujuan belum terwakili di survei, sehingga P1 dan antrean persetujuan belum dikonfirmasi dari sisi penyetuju.

## Dokumen Terkait

- Dok proses: [[Finance - Proses Pengajuan Pengeluaran dan Persetujuan]] · [[Finance - Proses Pembayaran Keluar]] · [[Finance - Proses Penjualan Marketplace dan Uang Masuk]] · [[Finance - Proses Retur dan Piutang Marketplace]] · [[Finance - Proses Rekonsiliasi Kas Toko dan Bank]] · [[Finance - Proses Pencatatan dan Buku Besar]] · [[Finance - Proses Gaji dan Iuran BPJS]] · [[Finance - Proses Pajak]] · [[Finance - Proses Anggaran, Kas Kecil, dan Dana Kegiatan]] · [[Finance - Proses Tutup Buku, Stock Opname, dan Laporan]] · [[Finance - Proses Costing HPP Produk]]
- Lintas proses: [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]]
- [[Finance - FAT Persona]] (peran dan praktik nyata per posisi) · [[Finance - Big Pictures]] · [[Finance - Dashboard per Posisi (FAT)]]
- [[Finance - Buku Besar CV]] · [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] · [[ADR - 0001 Akuntansi via Accurate]] · [[REF - Kepemilikan Data]]
