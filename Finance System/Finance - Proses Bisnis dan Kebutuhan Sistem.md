# Finance - Proses Bisnis dan Kebutuhan Sistem

## Deskripsi

*Panduan untuk membangun sistem yang membantu proses bisnis Finance bekerja lebih efisien. Dok ini memetakan sebelas proses bisnis Finance: untuk tiap proses, apa tujuannya, siapa perannya, bagaimana dikerjakan hari ini, apa yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Rincian teknis tetap di dok yang ditautkan; dok ini pintu per proses, bukan salinannya.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Sebagian besar proses sudah punya modul di kode tetapi belum dipakai di prod; sebagian lain 🟡 direncanakan (buku besar CV, penjualan per CV, mutasi bank, payroll ke bank) atau belum diputuskan. Keadaan kode diperiksa ke `origin/main` 2026-09-17; keadaan prod bertanggal di tiap butir, ukur ulang sebelum dipakai memutuskan.
- **Sumber**: survei alur kerja Finance (isian mandiri 14 sampai 16 September 2026, butir bertanda *survei 2026-09*, pola prosesnya di [[Finance - FAT Persona]]), kode `bip-erp` dan `erp-frontend`, dan dok domain yang ditautkan. Durasi isian survei tidak andal dan tidak dipakai.
- **Bukan**: daftar orang, jumlah pemegang jabatan, atau usulan susunan organisasi. Dok ini tentang proses dan sistemnya.

## Cara memakai dok ini

1. Pilih proses (P1 sampai P11) yang mau dibantu sistem.
2. Kerjakan dulu kelompok **A** proses itu (sudah ada, tinggal dipakai), lalu **B** (perbaiki yang ada), baru **C** (bangun yang belum ada). Definisinya di § Kelompok kebutuhan.
3. Sebelum `/start-task`, jawab enam pertanyaan di § Pertanyaan wajib sebelum membangun, lalu ukur baseline di § Ukuran efisiensi supaya hasilnya bisa dibuktikan.
4. Nomor task T1 sampai T10 mengikuti urutan pekerjaan buku besar CV di [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]].

## Prinsip rancangan

1. **Pakai yang sudah ada sebelum membangun.** Rantai pengajuan, pembayaran, bukti transfer, kas kecil, payroll, dan Tax Control sudah ada di kode. Membangun tambahan di atas modul yang belum dipakai menghasilkan nol efisiensi.
2. **Data diinput sekali, oleh pemiliknya, di sumbernya.** Pemohon mengajukan sendiri, HR menjalankan payroll, gudang men-scan retur. Finance memeriksa dan memakai, bukan mengetik ulang. Pemilik tiap fakta ada di [[REF - Kepemilikan Data]].
3. **Satu data acuan untuk semua pemakai.** Penjualan per entitas, omzet pajak, dan jurnal diambil dari data yang sama, bukan direkap ulang tiap posisi. Basis data kerja paralel di Excel adalah gejala data sistem belum dipercaya; yang diperbaiki datanya, bukan dibuatkan basis data baru.
4. **Pemisahan tugas dijaga, pengetikan ulang dihapus.** Pembuat, pemeriksa, penyetuju, dan pelaku rekonsiliasi tetap peran berbeda. Otomasi menghapus langkah ketik ulang dan arsip ganda, tidak menghapus pemeriksanya.
5. **Keadaan menunggu harus terlihat dan memberi tahu.** Setiap langkah yang menunggu orang lain punya antrean di layar pelakunya dan notifikasi; menunggu tanpa pemberitahuan adalah alur putus.
6. **Angka yang belum lengkap harus mengaku.** Layar yang menjumlah data sebagian menyebut apa yang tidak ikut dihitung (contoh yang sudah ada: kartu Varians OPEX, `erp-frontend/src/features/finance/anggaran/components/kartu-varians-opex.tsx:107-140`).
7. **Batas sistem jelas.** ERP tidak memindahkan uang (transfer tetap di bank) dan tidak menggantikan Coretax. Buku PT tetap di Accurate ([[ADR - 0001 Akuntansi via Accurate]]); buku CV diarahkan ke ERP ([[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]]).
8. **Efisiensi dibuktikan dengan ukuran sebelum dan sesudah**, bukan dengan fitur yang sudah rilis.

## Peta proses

| Kode | Proses | Peran Finance | Departemen lain | Hari ini | Sistem sekarang |
|---|---|---|---|---|---|
| P1 | Pengajuan pengeluaran dan persetujuan | Cost Control, Supervisor FAT | Semua divisi pemohon, Direktur | Chat, Excel, berkas | Ada di ERP, hampir tak dipakai |
| P2 | Pembayaran keluar (rekening PT dan kas CV) | AP, Junior Accountant, Supervisor FAT, Senior Accountant | Pemohon, Procurement, bank | BKK, AppSheet, internet banking, arsip kertas | Ada di ERP, belum dipakai |
| P3 | Penjualan marketplace dan uang masuk | AR, Junior Accountant, Tax | IT, marketplace | Rekap Excel, alat web terpisah | Sinkron ke Accurate jalan; per CV belum ada |
| P4 | Retur dan piutang marketplace | AR | Gudang, IT, ekspedisi | Basis data kerja sendiri, unggah manual | Sinkron retur bergerbang scan gudang |
| P5 | Rekonsiliasi kas toko dan bank | AR, Senior Accountant, Junior Accountant, AP | IT, bank | Excel, diulang sampai cocok | Layar ada, format belum cocok; mutasi bank belum ada |
| P6 | Pencatatan dan buku besar | Junior Accountant, Senior Accountant | Admin gudang dan produksi | Accurate (PT), FINCON (CV), jurnal manual | PT otomatis sebagian; CV direncanakan |
| P7 | Gaji dan iuran BPJS | Cost Control, Senior Accountant, Junior Accountant | HR | Rekap dari HR diketik ulang | Payroll ada; ke bank dan jurnal belum ada |
| P8 | Pajak | Tax, Junior Accountant | Procurement, DJP | Excel, Coretax, hampir semua diketik ulang | Tax Control ada, data kosong |
| P9 | Anggaran, kas kecil, dana kegiatan | Cost Control | Semua divisi, GA | Accurate, Excel, kertas | Anggaran dan kas kecil ada; dana kegiatan belum ada |
| P10 | Tutup buku, stock opname, laporan | Senior Accountant, Cost Control | Gudang, Direktur | Excel, Accurate | Laporan dibaca dari Accurate; checklist belum ada |
| P11 | Costing HPP produk | AP | APJ, Procurement, PPIC, SPV Marketing | Templat Excel, WhatsApp | Belum ada; hanya kartu hasil |

## Proses

### P1. Pengajuan pengeluaran dan persetujuan

- **Tujuan**: setiap pengeluaran punya pengajuan lengkap, dicek terhadap anggaran, dan disetujui orang yang berwenang, tanpa berpindah lewat chat.
- **Hari ini** (*survei 2026-09*): permintaan datang lewat WhatsApp, Excel, dan email. Cost Control memeriksa kelengkapan dokumen dan anggaran lalu menyerahkan form ke Finance untuk dibayar. Persetujuan Supervisor FAT, lalu persetujuan di bank, disebut titik antre.
- **Sudah ada di ERP**: Pengajuan Barang lima tipe (UMUM, RAWMATERIAL, IKLAN, DANA, KONSUMSI) dengan tahap per izin, termasuk Supervisor FAT dan Direktur di atas ambang ([[Microservices - Procurement Service]]); pengajuan budget dan kas kecil ([[Finance - Kas Kecil dan Pengajuan Budget]]). Prod 2026-09-12: 1 pengajuan barang.
- **Alur target**: pemohon membuka pengajuan di ERP beserta lampiran dan pos anggaran → sistem menandai bila melampaui pos → Cost Control memeriksa → Supervisor FAT menyetujui dari satu kotak persetujuan → Direktur bila di atas ambang → masuk antrean P2 dengan notifikasi ke pelaksana bayar.
- **Celah**:
  - **A** Pemohon di semua divisi memakai Pengajuan Barang; paket izin terpasang.
  - **A** Ambang Direktur diatur. Bernilai nol berarti tahap Direktur tidak disisipkan (`bip-erp/services/procurement/pengajuan_barang_jenjang.go:154-157`).
  - **B** Pengajuan membawa pos anggaran yang dibebaninya. Dashboard AP sendiri mencatat metrik "Expense di luar anggaran" berstatus belum karena pengajuan beserta pos anggarannya belum tercatat di sistem (`erp-frontend/src/features/finance/posisi/data/ap.ts:64-71`).
  - **B** Pengajuan barang yang menunggu Supervisor FAT tampil di kotak persetujuan dashboard, yang hari ini hanya memuat proposal dan aksi Sadewa serta insentif DRAFT (`bip-erp/services/integration/internal/interface/http/persetujuan_handler.go:16-19`).
  - **TBD** Pembayaran pajak, iuran BPJS, dan hutang supplier CV belum punya tipe pengajuan khusus; apakah lewat tipe DANA, P7, P8, atau jalur sendiri belum diputuskan.
  - Pengajuan budget berhenti di status DISETUJUI; pencairannya di luar modul (`bip-erp/services/procurement/main.go:754-758`).
- **Kontrol wajib**: pemohon, pemeriksa anggaran, dan penyetuju adalah peran berbeda.
- **Ukuran**: lama dari pengajuan sampai disetujui; porsi permintaan yang masih datang lewat chat.

### P2. Pembayaran keluar (rekening PT dan kas CV)

- **Tujuan**: uang keluar dengan nominal benar, dari rekening yang benar, berbukti, dan tercatat, dengan satu kali input.
- **Hari ini** (*survei 2026-09*):
  - Kas CV: BKK Excel dicetak → unggah AppSheet → input Kopra → persetujuan → unduh bukti → jurnal → arsip AppSheet dan kertas → bukti dikirim lewat WhatsApp. Satu pembayaran diketik empat sampai lima kali, dan proses yang sama berjalan terpisah di tiap kelompok CV.
  - Rekening PT: tagihan masuk → internet banking → BKK/BKM kertas → persetujuan Supervisor FAT → arsip bantex bulanan → bukti lewat WhatsApp.
- **Sudah ada di ERP**:
  - Tahap `pb_finance_setujui_bayar` (Supervisor FAT memilih kas CV pembayar) dan `pb_ap_transfer` yang bercabang: rekening PT oleh pemegang `budget.ap.bayar`, kas CV oleh pemegang `budget.cv.transfer` yang ditugaskan ke CV itu (`bip-erp/services/procurement/pengajuan_barang_gate.go:245-284`); antrean transfer CV di layar CV Saya. Rinciannya di [[Finance - Buku Besar CV]].
  - Unggah bukti oleh pelaksana, pemeriksaan bukti oleh Senior Accountant, faktur pembelian dari hasil QC, dokumen pembayaran yang dikirim manual ke Accurate (`bip-erp/services/procurement/pembayaran_kirim.go:12-29`), dan jurnal kas ke Accurate di balik saklar `ACCURATE_KAS_PUSH` yang bawaannya mati (`bip-erp/services/procurement/kas_jurnal_handler.go:28-37`).
  - Prod: 0 dokumen pembayaran (2026-09-12); data penugasan pemegang CV 0 (2026-09-17).
- **Alur target**: pengajuan disetujui (P1) → antrean bayar di layar pelaksana dengan notifikasi → transfer di bank → unggah bukti → pemeriksaan bukti Senior Accountant → pemohon dikabari otomatis → jurnal otomatis (PT ke Accurate, CV ke buku besar CV). Dokumen pengajuan beserta bukti menjadi arsip; BKK kertas dan AppSheet tidak dibuat lagi.
- **Celah**:
  - **A** Paket izin pelaksana bayar terpasang; data 40 CV dan pemegangnya diisi; keputusan bahwa dokumen pengajuan menggantikan BKK dan AppSheet.
  - **B** Dokumen pembayaran berstatus PENDING belum punya notifikasi, jadi pengiriman manual ke Accurate bisa terlupa ([[Finance - FAT Persona]] § Skenario Gagal).
  - **B** Pembayaran tanpa faktur (tipe DANA, IKLAN, KONSUMSI) dibukukan lewat jurnal umum yang tidak terbit selama saklar kas mati; kapan saklar dinyalakan perlu diputuskan sesudah diuji.
  - **C** Jurnal otomatis buku CV dari pembayaran berbukti (T6).
  - **TBD** Berkas transfer massal ke bank belum dianalisa.
- **Kontrol wajib**: pelaksana transfer, penyetuju, pemeriksa bukti, dan pelaku rekonsiliasi bank adalah peran berbeda.
- **Ukuran**: jumlah BKK per bulan per CV (ekspor AppSheet), transaksi Kopra per rekening per bulan, lama dari disetujui sampai ditransfer, jumlah pengetikan ulang per pembayaran (target satu).

### P3. Penjualan marketplace dan uang masuk

- **Tujuan**: penjualan, potongan platform, dan penarikan saldo tercatat benar per toko dan per entitas tanpa rekap manual, lalu dipakai bersama pencatatan, pajak, dan pemeriksaan.
- **Hari ini** (*survei 2026-09*): penjualan diekspor dari ERP ke basis data kerja setiap hari; tiap awal bulan dashboard, ERP, dan Accurate dicocokkan; penarikan per CV direkap lewat alat web terpisah di luar ERP; data penarikan diolah ulang per CV (pecah bundling, kuantitas, HPP) untuk invoice CV dan omzet pajak. Data penarikan sering telat sampai ke pengolahnya.
- **Sudah ada di ERP**: sinkron order marketplace dan pengiriman faktur harian, retur, serta penerimaan ke Accurate ([[Microservices - Integration Service]]); rute rekonsiliasi income dan rekap kuantitas (`bip-erp/services/integration/main.go:1780-1783`); dompet marketplace dengan saldo, penarikan, dan rekonsiliasi settlement (`main.go:1905-1907`).
- **Alur target**: toko dipetakan ke entitas CV di master CV → sistem menghasilkan penjualan, potongan, dan penarikan per CV → Junior Accountant memakainya untuk jurnal CV, Tax untuk omzet, Senior Accountant memeriksa. Tidak ada rekap ulang.
- **Celah**:
  - **C** Pemetaan toko ke CV dan penjualan per CV (T8). Hari ini `accurate_shops` tidak punya field CV ([[REF - Kepemilikan Data]] § Duplikasi).
  - **C** Aturan kolom yang tidak boleh dijumlahkan ikut tertulis di rancangan ([[Finance - Buku Besar CV]] § Gerbang kolom).
  - **TBD** Isi, aturan, dan pemilik alat web rekap penarikan CV ditelusuri sebelum T8 dirancang, supaya tidak membangun tandingannya dari nol.
  - **TBD** Income yang belum masuk sinkron dan masih diinput manual: kanal dan penyebabnya belum diukur.
- **Kontrol wajib**: satu kolom dihitung sekali; kolom yang merupakan bagian dari kolom lain tidak dijumlahkan.
- **Ukuran**: jam rekap penjualan per hari; jumlah selisih dashboard, ERP, dan Accurate pada pencocokan awal bulan; tanggal data penarikan tersedia bagi pengolah.

### P4. Retur dan piutang marketplace

- **Tujuan**: retur dibukukan sekali, sesuai barang yang benar-benar kembali, dan piutang terbuka akurat tanpa basis data kerja paralel.
- **Hari ini** (*survei 2026-09*): retur divalidasi di empat sumber (ERP, marketplace, Accurate, gudang); retur yang belum discan dikejar ke gudang dan ekspedisi (tindak lanjut tiga sampai lima hari); piutang minus ditelusuri karena income yang berubah jadi retur; retur yang ternyata belum terbukukan diunggah manual, dan untuk faktur sejak Juli 2026 dicatat lalu dilaporkan ke IT.
- **Sudah ada di ERP**: sinkron retur ke Accurate dengan gerbang payout ([[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]]) dan gerbang gudang: retur barang kembali ditahan PENDING sampai gudang men-scan barangnya ([[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]). Per 2026-08-06: 908 baris PENDING, 900 menunggu scan ([[Microservices - Integration Service]]). Order yang dikirim sebelum 1 Juli 2026 memang dibukukan manual oleh Finance.
- **Alur target**: gudang men-scan retur tepat waktu → retur terbukukan otomatis → AR menangani pengecualian dari satu daftar di ERP (belum discan, lolos sinkron, piutang minus) → piutang terbuka diperbarui.
- **Celah**:
  - **A** Disiplin scan retur di gudang, karena antrean pembukuan retur Finance adalah antrean scan gudang.
  - **B** Ukur besar celah retur yang lolos sinkron (rekap unggah manual yang dikirim ke IT adalah sumber volumenya), lalu tutup penyebabnya.
  - **B** Satu daftar pengecualian retur dan piutang di ERP untuk menggantikan basis data kerja.
  - **TBD** Pemilik pelacakan paket yang tertahan di ekspedisi.
- **Kontrol wajib**: retur yang sudah diserap penerimaan tidak dibukukan lagi (gerbang payout).
- **Ukuran**: jumlah retur yang diunggah manual per bulan; umur retur PENDING yang menunggu scan.

### P5. Rekonsiliasi kas toko dan bank

- **Tujuan**: saldo buku sama dengan saldo nyata di seller center dan rekening bank, dan setiap selisih punya sebab tertulis.
- **Hari ini** (*survei 2026-09*): saldo kas toko direkonsiliasi mingguan terhadap Accurate beserta analisis selisih harga, biaya, dan nilai settle; saldo kas toko disajikan manual dari Accurate lalu diperbarui berulang sampai sama dengan seller center, sambil menunggu perbaikan dari IT; rekening koran baru tersedia tanggal 1. Ini beban terbesar yang disebut lintas peran.
- **Sudah ada di ERP**: layar Rekonsiliasi kas toko tiga tab, rekap, rincian, dan akumulasi (`erp-frontend/src/app/(main)/integration-accurate/rekonsiliasi/page.tsx:39`); rute rekonsiliasi dompet dan income (P3). Impor mutasi rekening bank **belum ada**: `git grep` 2026-09-17 atas `services/finance`, `services/integration`, dan `services/procurement` hanya menemukan rekening koran sebagai lampiran bukti audit internal.
- **Alur target**: satu pelaku rekonsiliasi per jenis saldo memakai satu format di ERP → selisih muncul sebagai daftar bersebab (bukan saldo yang diperbarui berulang) → mutasi bank diimpor dan dicocokkan dengan jurnal kas → Senior Accountant memeriksa hasil akhir.
- **Celah**:
  - **B** Format layar rekonsiliasi kas toko disesuaikan dengan kerja rekonsiliasi. Format yang dibutuhkan belum dirinci (**TBD**, minta contoh format kerja yang dipakai sekarang).
  - **C** Impor mutasi rekening dan rekonsiliasi bank (T9). Lingkup T9 kini rekening CV; rekening PT dan kas toko masuk atau jadi task sendiri belum diputuskan.
- **Kontrol wajib**: pelaku rekonsiliasi bukan pelaksana transfer.
- **Ukuran**: putaran rekonsiliasi kas toko per bulan dan jam per putaran; jumlah selisih yang belum bersebab di akhir bulan.

### P6. Pencatatan dan buku besar

- **Tujuan**: setiap transaksi dicatat sekali di buku entitasnya, dan diperiksa sebelum masuk laporan.
- **Hari ini** (*survei 2026-09*): buku PT di Accurate, buku 40 CV di aplikasi luar ERP ([[APP - Buku Besar Konsolidasi CV FINCON]]); jurnal diketik manual per CV; hasil sinkron marketplace dan input jurnal harian (termasuk admin gudang dan produksi) diperiksa Senior Accountant setiap hari.
- **Sudah ada di ERP**: pengiriman otomatis faktur, retur, dan penerimaan marketplace ke Accurate (P3, P4); jurnal kas kecil ke Accurate lewat outbox ([[Finance - Kas Kecil dan Pengajuan Budget]]); master entitas CV, penugasan pemegang, dan cakupan per CV (T1, merge 2026-09-16).
- **Alur target**: buku PT tetap Accurate; buku CV di ERP (T3 sampai T5) dengan jurnal otomatis dari pembayaran dan kas kecil (T6), penjualan per CV (T8), dan gaji (T7); jurnal manual tinggal untuk yang benar-benar tidak punya sumber sistem, dan diperiksa sebelum diposting.
- **Celah**: **C** T3 sampai T6 dan T10, menunggu persetujuan ADR 0096. Aturannya (dokumen atomik, nominal sen bilangan bulat, kunci periode, jurnal balik, jejak sumber) di [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] dan [[Finance - Buku Besar CV]].
- **Kontrol wajib**: pencatat bukan pemeriksa; periode terkunci tidak bisa ditulisi.
- **Ukuran**: porsi jurnal CV yang terbit otomatis; jumlah jurnal yang dikoreksi saat pemeriksaan.

### P7. Gaji dan iuran BPJS

- **Tujuan**: gaji dan iuran dihitung sekali dari data kehadiran, dibayar per badan usaha tanpa diketik ulang, dan dijurnal otomatis.
- **Hari ini** (*survei 2026-09*): rekap gaji dan data BPJS datang dari HR lewat WhatsApp, Excel, dan email per CV (satu sampai tiga hari, lampiran kadang tidak ada, nominal bisa beda); rekap diperiksa per orang terhadap lampiran izin, SKS, dan jam absen, lalu diperiksa lagi dari sisi rekening dan PPh; pembayaran diketik ulang ke bank.
- **Sudah ada di ERP**: payroll per badan usaha (41 entitas), dua dasar upah BPJS, potongan kehadiran dari attendance-service, dan beban perusahaan per karyawan ([[Microservices - Payroll Service]]). Per akhir Agustus 2026 baru dua run di prod. Aturan potongan dan sanksi mengikuti [[HRIS - Kepatuhan Peraturan Perusahaan]].
- **Alur target**: HR menjalankan payroll di ERP → pengecekan Finance memakai data kehadiran dan izin yang sudah di sistem → sistem menghasilkan daftar transfer per badan usaha dan rekap iuran BPJS → pembayaran lewat P2 → jurnal gaji otomatis ke buku entitasnya.
- **Celah**:
  - **A** HR memakai payroll ERP sebagai sumber gaji.
  - **C** Daftar transfer bank, rekap iuran BPJS per badan usaha, dan jurnal gaji (T7). `git grep` 2026-09-17 atas `services/payroll` tidak menemukan ekspor transfer bank, rekap BPJS, maupun pemanggilan Accurate atau jurnal (kontrol positif: kata `bpjs` ada di 33 berkas).
  - **TBD** Apakah pemeriksaan rekap gaji dari dua sudut (kehadiran dan potongan; rekening dan PPh) tetap dua langkah sesudah payroll ERP dipakai.
- **Kontrol wajib**: yang menghitung gaji bukan yang menyetujui dan membayarnya.
- **Ukuran**: lama dari rekap gaji tersedia sampai dibayar; jumlah selisih nominal BPJS antara tagihan dan data peserta.

### P8. Pajak

- **Tujuan**: kewajiban pajak dihitung dari data acuan yang sama dengan pembukuan, dilaporkan dan dibayar tepat waktu, dengan titik cut-off yang disepakati.
- **Hari ini** (*survei 2026-09*): data transaksi dicek dan dikonfirmasi, catatan perusahaan diekualisasi dengan Coretax, data diinput ke Coretax, kode billing dibuat tanggal 1 sampai 3 (PPh final, PPh 21, PPh 25) dan tanggal 20 (PPh 23, PPN), lalu pajak dibayar Junior Accountant. Hampir semua data diketik ulang; hambatan utamanya menentukan data acuan dan cut-off; pos persediaan hanya tersedia sebagai angka tanpa rincian.
- **Sudah ada di ERP**: Tax Control berisi kewajiban per masa, pengingat jatuh tempo H-7 dan H-3, pencatatan pelaporan, dan unggah BPE serta bukti bayar ([[API - Finance Service]], [[Finance - Rancangan Finance Service]]). Prod 2026-09-12: master jenis pajak dan kewajiban masih 0.
- **Alur target**: kewajiban per masa terbit di Tax Control → data penjualan per entitas (P3), pembelian dan pembayaran (P2), dan gaji (P7) ditarik dari satu sumber → ekualisasi dan input Coretax (tetap di DJP) → kode billing dibayar lewat P2 → BPE diunggah ke Tax Control.
- **Celah**:
  - **A** Master jenis pajak diisi, paket `finance_pajak` dipasang.
  - **C** Omzet per entitas dari T8 dan data pembelian/pembayaran dari P2 yang benar-benar dipakai.
  - **TBD** Rincian pos persediaan dan titik cut-off yang disepakati bersama P10.
- **Kontrol wajib**: yang menghitung kewajiban bukan satu-satunya yang memeriksa angka laporan.
- **Ukuran**: jumlah data yang diketik ulang untuk satu masa pajak; kewajiban yang dilaporkan lewat tenggat.

### P9. Anggaran, kas kecil, dan dana kegiatan

- **Tujuan**: pengeluaran dikendalikan terhadap anggaran, kas kecil tertib per unit, dan dana kegiatan dipertanggungjawabkan sampai sisa dikembalikan atau kekurangan diganti.
- **Hari ini** (*survei 2026-09*): realisasi anggaran dicek di Accurate setiap pagi; pengajuan dari divisi diperiksa kelengkapan dokumen dan anggarannya; dana kegiatan dicairkan lalu laporan pemakaian dan buktinya dicocokkan, dengan penyelesaian berupa input, pengembalian dana, atau reimburse; laporan realisasi RAPB disusun sesudah cut-off akhir bulan. Angka varians di ERP sulit dijelaskan karena transaksi pembentuknya tidak terlihat.
- **Sudah ada di ERP**: master anggaran OPEX, kartu Varians OPEX, breakdown mingguan anggaran terhadap realisasi, dan laporan Admin & Non-Ops (`erp-frontend/src/features/finance/anggaran/`, data di integration-service `anggaran_opex`, [[REF - Kepemilikan Data]]); kas kecil dengan verifikasi Finance dan jurnal ke Accurate ([[Finance - Kas Kecil dan Pengajuan Budget]]); rekomendasi efisiensi (0 dokumen di prod 2026-09-12).
- **Alur target**: pengajuan membawa pos anggaran (P1) → realisasi per pos bisa ditelusuri sampai transaksinya → dana kegiatan tercatat dari pencairan sampai pertanggungjawaban → laporan realisasi tersusun dari data yang sama.
- **Celah**:
  - **B** Varians bisa ditelusuri ke transaksi. Kartu Varians OPEX hanya menyajikan total dan cacah pos lewat anggaran (`kartu-varians-opex.tsx:65-94`), dan komponen anggaran tidak menaut ke transaksi Accurate mana pun.
  - **B** Pengajuan tersambung ke pos anggaran (sama dengan P1).
  - **C** Pertanggungjawaban dana kegiatan. `git grep` 2026-09-17 atas `bip-erp/services` tidak menemukan alur uang muka sampai pertanggungjawaban; perlu `/analisa-kebutuhan` lebih dulu (apakah memperluas tipe DANA atau modul sendiri).
- **Kontrol wajib**: pengaju bukan pemeriksa anggaran; penerima dana kegiatan bukan yang menyetujui pertanggungjawabannya.
- **Ukuran**: jumlah pertanyaan varians yang harus ditelusuri manual; umur dana kegiatan yang belum dipertanggungjawabkan.

### P10. Tutup buku, stock opname, dan laporan

- **Tujuan**: tutup buku bulanan tepat waktu dengan input yang lengkap, stok buku cocok dengan fisik, dan laporan yang tidak perlu dikoreksi.
- **Hari ini** (*survei 2026-09*): pekerjaan menumpuk di minggu pertama (gaji, kode billing, rekonsiliasi awal bulan, laporan) dan akhir bulan (stock opname sekitar tanggal 25 sampai 28, cek gaji, cut-off, retur tertahan untuk jurnal penyesuaian). Data yang baru tersedia sesudah akhir bulan (rekap iklan, sampel afiliasi, tagihan utilitas, laporan PPN dan PPh final) ditagih manual. Selisih stock opname ditelusuri item per item dari mutasi stok terhadap kartu stok.
- **Sudah ada di ERP**: laporan keuangan dan jurnal dibaca dari Accurate (`/finance/accounting`, `/finance/gl`, [[Finance - Dashboard per Posisi (FAT)]]); ceklis laporan untuk audit internal ([[Finance - Audit Internal]]); manufacture-service membaca stok dari Accurate satu arah dan mengunci saldo akhir yang berasal dari impor stock opname ([[Microservices - Manufacture Service]]); opname digital masih konsep ([[Manufacture - Stock & Material Management]]).
- **Alur target**: daftar periksa tutup buku per entitas memperlihatkan input yang belum masuk dan siapa pemiliknya → data akhir bulan dari modul lain ditarik, bukan ditagih → hasil stock opname masuk sebagai data dengan selisih per item → periode dikunci sesudah diperiksa.
- **Celah**:
  - **C** Daftar periksa tutup buku dan peran pengunci periode (T10).
  - **C** Opname digital dengan selisih per item, milik domain manufaktur dan gudang.
  - **TBD** Data akhir bulan mana yang sudah ada di modul lain (iklan dan afiliasi di modul marketing) dan bisa ditarik.
- **Kontrol wajib**: periode yang sudah dikunci tidak bisa diubah tanpa jejak.
- **Ukuran**: tanggal laporan keuangan selesai; jumlah input yang masih ditagih manual; jumlah item selisih stok per opname.

### P11. Costing HPP produk

- **Tujuan**: HPP produk dihitung dari formula, harga bahan, dan kapasitas yang sama dengan yang dipakai modul lain, lalu disetujui dan dibagikan tanpa berkas terpisah.
- **Hari ini** (*survei 2026-09*): formula dari APJ, harga bahan baku dan kemas diminta ke Procurement, kapasitas produksi dimintakan, HPP dihitung di templat Excel, disetujui Supervisor FAT, lalu dibagikan ke SPV Marketing. Alatnya Excel dan WhatsApp; yang ditunggu data harga bahan.
- **Sudah ada di ERP**: BOM/formula dan master bahan di manufacture-service ([[Manufacture - Stock & Material Management]]); HPP dipakai perhitungan insentif ([[Finance - Incentive]]); kartu "Costing HPP valid" di dashboard AP (`erp-frontend/src/features/finance/posisi/data/ap.ts:72-78`); rencana master HPP per SKU ([[Sales - HPP Master (Plan)]], 🟡).
- **Alur target**: TBD. Kandidatnya: formula dari BOM manufaktur, harga bahan dari data pembelian, kapasitas dari PPIC, hasil costing disetujui di ERP dan menjadi HPP yang dibaca insentif.
- **Celah**: **C** belum jadi task dan belum diputuskan masuk ERP; perlu `/analisa-kebutuhan` karena melibatkan APJ, Procurement, PPIC, dan Marketing. Apakah hasil costing Excel hari ini yang menjadi HPP di insentif: **TBD**.
- **Kontrol wajib**: penghitung costing bukan penyetujunya.
- **Ukuran**: lama dari permintaan costing sampai hasil dibagikan; jumlah costing yang menunggu data harga bahan.

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

## Sambungan dengan departemen lain

Sebagian perbaikan proses Finance dikerjakan di modul milik departemen lain.

| Departemen | Yang dibutuhkan Finance | Modul pemilik | Keadaan sambungan |
|---|---|---|---|
| Semua divisi pemohon | Pengajuan diinput sendiri beserta lampiran dan pos anggaran | Procurement (Pengajuan Barang) | Tersambung di kode, belum dipakai |
| HR | Gaji dan iuran dihitung di payroll dari data kehadiran | Payroll, attendance | Payroll membaca kehadiran; ke bank dan jurnal belum ada |
| Gudang dan manufaktur | Retur discan tepat waktu; hasil stock opname sebagai data | Manufacture, integration | Scan retur membuka pembukuan retur; opname digital belum ada |
| Procurement | Tagihan pemasok dan harga bahan di sistem | Procurement | Faktur pembelian ada; harga bahan untuk costing belum tersambung |
| Marketing | Permintaan iklan lewat pengajuan; rekap iklan dan afiliasi untuk tutup buku | Procurement, marketing | Tipe IKLAN ada; penarikan rekap untuk tutup buku belum diperiksa |
| IT | Sinkron marketplace ke Accurate yang lengkap; perbaikan selisih | Integration | Jalan; celah retur dan income manual belum diukur |
| Pihak luar | Transfer, rekening koran, Coretax, seller center | Di luar ERP | Tetap manual; mutasi bank direncanakan diimpor (T9) |

## Pertanyaan wajib sebelum membangun

Setiap fitur untuk proses Finance menjawab enam pertanyaan ini di rencana `/plan`:

1. **Pengetikan ulang mana yang hilang?** Sebut langkah manual hari ini yang tidak dikerjakan lagi. Fitur yang tidak menghapus langkah manual apa pun perlu alasan lain untuk dibangun.
2. **Siapa menginput, di mana sumbernya?** Pemilik datanya menurut [[REF - Kepemilikan Data]]; Finance tidak menjadi juru ketik data departemen lain.
3. **Kontrol mana yang dijaga?** Sebut pembuat, pemeriksa, dan penyetuju, dan pastikan tidak menyatu di satu peran.
4. **Keadaan menunggu terlihat di mana?** Antrean di layar pelaku berikutnya dan notifikasinya.
5. **Apa yang terjadi bila datanya belum lengkap atau salah?** Layar mengaku, bukan menampilkan angka yang tampak utuh.
6. **Ukuran sebelum dan sesudahnya apa?** Ambil dari § Ukuran efisiensi dan catat baseline-nya sebelum rilis.

## Ukuran efisiensi

Isian durasi survei tidak andal, jadi efisiensi diukur dari data objektif sebelum dan sesudah sistem dipakai.

| Ukuran | Proses | Sumber data baseline |
|---|---|---|
| BKK per bulan per CV | P2 | Ekspor AppSheet tiga bulan |
| Transaksi bank per rekening per bulan | P2, P5 | Laporan Kopra dan internet banking |
| Lama pengajuan sampai disetujui, dan disetujui sampai ditransfer | P1, P2 | Tanggal di berkas hari ini; tanggal tahap di ERP sesudahnya |
| Jumlah pengetikan ulang per pembayaran | P2 | Wawancara alur; target satu |
| Retur yang diunggah manual per bulan | P4 | Rekap yang dikirim ke IT |
| Putaran rekonsiliasi kas toko per bulan dan jam per putaran | P5 | Catatan pelaku rekonsiliasi |
| Porsi jurnal CV yang terbit otomatis | P6 | Buku besar CV sesudah T6 |
| Lama dari rekap gaji tersedia sampai dibayar | P7 | Tanggal kirim rekap dan tanggal transfer |
| Tanggal laporan keuangan bulanan selesai | P10 | Arsip laporan |
| Umur dana kegiatan yang belum dipertanggungjawabkan | P9 | Catatan Cost Control |

## Keputusan yang dibutuhkan

Diputuskan Supervisor FAT atau manajemen sebelum kelompok A berjalan:

- Persetujuan [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]].
- Dokumen pengajuan menggantikan BKK dan arsip AppSheet atau tidak.
- Pemisahan pembuat, pemeriksa, penyetuju, dan pelaku rekonsiliasi pada P2 dan P5.
- Ambang persetujuan Direktur dan kemungkinan delegasi persetujuan.
- Makna hutang supplier CV (hutang ke PT atau bukan) dan jalur pembayarannya ([[Finance - Buku Besar CV]] § Belum Diputuskan).
- Pemeriksaan rekap gaji dari dua sudut tetap dua langkah atau tidak (P7).
- Kapan saklar jurnal kas `ACCURATE_KAS_PUSH` dinyalakan (P2).

## Yang sengaja tidak dibangun

- **Buku PT di luar Accurate.** ERP mengirim ke Accurate, bukan menggantikannya ([[ADR - 0001 Akuntansi via Accurate]]).
- **Aplikasi pajak pengganti Coretax.** Yang dibutuhkan data acuan, bukan pelaporan tandingan.
- **Transfer uang dari ERP.** Transfer tetap dikerjakan di bank; ERP mencatat, menyetujui, dan menyimpan bukti.
- **Versi ERP dari BKK kertas dan AppSheet.** Dokumen pengajuan menggantikannya.
- **Basis data kerja baru untuk AR.** Yang dibutuhkan data marketplace yang bisa dipercaya dan daftar pengecualian.
- **Buku CV paralel di luar ERP.** FINCON dijadikan spesifikasi lalu dipensiunkan (T10), bukan dirawat bersama.

## Belum Diputuskan (TBD)

- Tipe atau jalur pengajuan untuk pajak, iuran BPJS, dan hutang supplier CV (P1).
- Berkas transfer massal ke bank (P2).
- Isi dan pemilik alat web rekap penarikan CV; kanal income yang masih diinput manual (P3).
- Pemilik pelacakan paket tertahan di ekspedisi (P4).
- Format rekonsiliasi kas toko yang dibutuhkan; lingkup rekening PT dan kas toko di T9 (P5).
- Rincian pos persediaan dan titik cut-off pajak (P8, P10).
- Bentuk pertanggungjawaban dana kegiatan (P9).
- Alur costing HPP di ERP dan hubungannya dengan HPP insentif (P11).
- Sisi persetujuan belum terwakili di survei, sehingga P1 dan antrean persetujuan belum dikonfirmasi dari sisi penyetuju.

## Dokumen Terkait

- [[Finance - FAT Persona]] (peran dan praktik nyata per posisi) · [[Finance - Big Pictures]] · [[Finance - Dashboard per Posisi (FAT)]]
- [[Finance - Buku Besar CV]] · [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] · [[APP - Buku Besar Konsolidasi CV FINCON]] · [[ADR - 0001 Akuntansi via Accurate]]
- [[Microservices - Procurement Service]] · [[Finance - Kas Kecil dan Pengajuan Budget]] · [[Microservices - Integration Service]] · [[Microservices - Payroll Service]] · [[Microservices - Manufacture Service]]
- [[API - Finance Service]] · [[Finance - Rancangan Finance Service]] · [[Finance - Audit Internal]] · [[Finance - Incentive]] · [[Sales - HPP Master (Plan)]]
- [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] · [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] · [[Manufacture - Stock & Material Management]]
- [[REF - Kepemilikan Data]] · [[HRIS - Kepatuhan Peraturan Perusahaan]]
