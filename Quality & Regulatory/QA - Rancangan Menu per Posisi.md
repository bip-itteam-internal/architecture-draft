## Deskripsi

*Rancangan sidebar erp-frontend untuk tiap posisi di departemen Quality, ditambah PJT (Penanggung Jawab Teknis) dan pembaca dari luar Quality. Nama menu sama untuk semua orang; yang berbeda adalah menu mana yang tampil, cakupan data, dan aksi yang boleh dilakukan. Disusun 2026-10-13 sebagai prototipe interaktif (Artifact privat) mengikuti format rancangan menu departemen lain; dok ini menyalin **struktur**-nya (menu, cakupan, aksi, keputusan). Jumlah orang dan akses diukur dari data prod 2026-10-13.*

- **Status**: 🟡 Konsep / Draft. Menunggu persetujuan rancangan dan keputusan Q1 sampai Q7. Rancangan ini hanya **menata menu yang sudah ada**; halaman baru (COA Keluar, satu gerbang QC bahan masuk, satu keputusan rilis) menunggu K-3, K-4, dan K-8 di [[Manufacture - Kajian Fondasi Sistem]].
- **Dasar**: [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]] (menu per urusan, digerbang izin posisi), [[ADR - 0105 Beranda Portal Menumpuk Zona Personal di Atas Ruang Kerja Posisi]] (Beranda), [[ADR - 0114 Antrean Persetujuan Terpusat di Web, Satu Tabel Seragam dari Agregator Employee-Service]] (Persetujuan).
- **Pasangan**: [[Manufacture - Rancangan Menu per Posisi]] (menu Manufaktur; Dokumen Produksi Batch dan Rekonsiliasi MO milik urusan Produksi di sana).
- **Path di repo (yang sudah ada)**: `erp-frontend/src/app/(main)/quality/*`, `bip-erp/services/employee/quality_*.go`, `bip-erp/services/employee/peran_dari_jabatan.go`.

## Cara membaca

| Penanda | Arti |
|---|---|
| **S** | data milik sendiri |
| **T** | tim yang dipimpin |
| **D** | seluruh departemen. Catatan mutu tidak dibagi per orang: lot, batch, komplain, dan CAPA milik departemen |
| **D\*** | sementara D, menunggu keputusan (Q5) |
| **✓** | tampil tanpa cakupan data |
| **antrean** | hanya yang menunggu tahap Anda (batch menunggu rilis, CAPA menunggu persetujuan, permintaan belum diambil) |
| **baru** | halaman atau cakupan yang belum ada untuk posisi itu |

- Induk menamai urusan, daun tanpa kata "Saya" (`ui-checklist` §2b). Induk yang bagi seseorang hanya berisi satu daun tampil sebagai menu tunggal tanpa induk.
- **Beranda** (zona personal ADR 0105) tampil untuk semua posisi dan tidak dihitung sebagai menu Quality.
- Penyaringan cakupan dilakukan di server, bukan di browser.
- Setiap menu baru wajib membawa panduan pemakaian (aturan tim panduan per menu).

## Struktur menu

Urusan umum (dulu Portal Saya) di atas, tanpa pembatas dengan urusan departemen.

| Urusan | Daun | Rute | Catatan |
|---|---|---|---|
| (tunggal) | Kalender | `/calendar` | Kalender terpusat: data diri sendiri, pekerjaan sendiri, agenda perusahaan |
| (tunggal) | KPI | `/portal/kpi` | Satu menu: staf melihat KPI sendiri, atasan juga rekap tim di tab terpisah. Menu KPI Quality (`/quality/kpi`) dilebur ke sini sebagai tab |
| Pengajuan & Persetujuan (umum) | Pengajuan · Persetujuan | `/portal/pengajuan` · `/portal/persetujuan` | Pengajuan milik sendiri tak pernah muncul di antrean sendiri |
| Tugas (umum) | Daftar Tugas · Permintaan Masuk · Laporan Tugas · Laporan Tim | `/task-management/*` | Laporan Tim hanya bagi atasan |
| **Pengendalian Mutu** | Pemeriksaan Bahan Masuk | `/quality/pengecekan-rm` | Antrean lot dari rantai pengajuan barang; keputusan Lulus / Reject / Ditolak |
| | Inspeksi Bahan Masuk | `/quality/incoming` | Register inspeksi manual. Tumpang tindih dengan daun di atas; tetap dua daun sampai K-4 |
| | Rilis Batch | `/quality/batch-release` | Keputusan rilis kedua di luar Batch Record; satu tempat keputusan menunggu K-3 |
| | Komplain Produk | `/quality/komplain` | Dulu "Komplain dari Marketing"; nama mengikuti urusan, bukan pengirim |
| | CAPA | `/quality/capa` | Satu pintu Quality dan Manufaktur (Q1). Penyetuju CAPA dari produksi atau gudang |
| Produksi (milik Manufaktur) | Dokumen Produksi Batch · Rekonsiliasi MO | `/manufacture/dokumen-produksi-batch` · `/manufacture/rekonsiliasi-mo` | Tidak disalin ke urusan Quality. Tampil bagi Quality lewat peran `manufacture: qc`, bagi PJT lewat `manufacture: rnd` |
| Registrasi & Pengembangan Produk (Kesekretariatan) | Registrasi NIE / BPOM / Halal · Pengembangan Produk | `/rnd/*` | Ditampilkan supaya sidebar PJT lengkap; tidak diubah rancangan ini |

## Menu per posisi

| Posisi | Orang (prod 2026-10-13) | Menu dan cakupan | Ruang kerja di Beranda |
|---|---|---|---|
| Quality Supervisor | 1 | Umum (Persetujuan antrean, Laporan Tim D, KPI S+D) · Pengendalian Mutu: kelima daun D · Produksi: kedua daun D | Lot dan batch yang menunggu, CAPA lewat tenggat, komplain belum divalidasi |
| QA Leader | 1 | Umum (KPI S+T) · Pengendalian Mutu: kelima daun D · Produksi: kedua daun D | Batch menunggu rilis, CAPA yang perlu ditindaklanjuti |
| QC Production | 3 | Umum · Pengendalian Mutu: Rilis Batch, Komplain, CAPA (D) · Produksi: kedua daun D | Batch berjalan yang menunggu isian uji, batch yang sudah diajukan rilis |
| QC Assistant | 1 | Umum · Pengendalian Mutu: Pemeriksaan Bahan Masuk, Inspeksi Bahan Masuk, Komplain (D) | Lot di karantina menunggu pemeriksaan, dari yang paling lama (KPI laporan maksimal 3 hari kerja) |
| QC Leader | 0 | Seperti QC Production ditambah Pemeriksaan dan Inspeksi Bahan Masuk; KPI S+T | Seperti QC Production ditambah antrean bahan masuk |
| PJT (jabatan QA RND) | 1 | Umum (Persetujuan antrean) · Rilis Batch (antrean, **baru**) · Dokumen Produksi Batch D · Registrasi & Pengembangan Produk | Batch menunggu keputusan rilis, lama menunggu dibanding target 24 jam |
| Marketing (CS, Shop Quality, SPV brand) | luar Quality | Komplain Produk (D\*) | Ruang kerja Marketing |
| Penyetuju CAPA (produksi & gudang) | luar Quality | CAPA (antrean) | Ruang kerja Manufaktur; CAPA menunggu muncul di Persetujuan |
| Direktur & Corporate Secretary | luar Quality | Umum (Persetujuan antrean, KPI D) · Pengendalian Mutu: kelima daun D · Dokumen Produksi Batch D | Ruang Direktur yang sudah ada |

Catatan per posisi:

- **Akses Quality hari ini datang dari penurunan peran jabatan** (`ROLE_FROM_POSITION` aktif), bukan dari paket atau peran tersimpan: dari enam orang Quality dan PJT, tak satu pun punya `system_roles` atau paket tersimpan. Posisi Quality menurunkan `quality: staff`/`supervisor` + `manufacture: qc`.
- **QA Leader**: data jabatan keliru, `position_key` tercatat `qc_assistant` (D2). Akses hari ini tak terpengaruh karena tabel peran mencocokkan nama jabatan. Pemeriksaan dan Inspeksi Bahan Masuk hanya baca.
- **QC Production**: mengisi bagian uji (IPC) di Dokumen Produksi Batch yang sama dengan Produksi, lalu **mengajukan** rilis, tidak memutus. Menu Hasil Produksi dan Formula dikeluarkan: tab WMS-nya tidak terbuka untuk peran `qc`, jadi menu itu tampil lalu ditolak (D5, Q6).
- **QC Leader**: jabatan ada di master data tanpa pemegang (D3); turunan perannya sudah disiapkan.
- **PJT**: tercatat di departemen Kesekretariatan. Sejak M-03 (bip-erp#3084, merged 2026-10-13) jabatan QA RND menurunkan `rnd: staff` + `manufacture: rnd`, sehingga bisa membuka dan memutus Dokumen Produksi Batch serta menulis spesifikasi produk ([[Manufacture - Dokumen Produksi Batch]]). **Rilis Batch masih belum terbuka** karena PJT tidak berperan `quality` (D1). Pemutus tunggal rilis batch dan penyetuju bahan pengganti bersama SPV Manufacture.
- **Marketing**: mengajukan dan memantau komplain. Di rancangan Marketing menu ini ada di urusan Permintaan ke Unit Lain, mengarah ke halaman yang sama.
- **Direktur**: membaca seluruh data mutu tanpa aksi mengubah catatan mutu; memegang peran seluruh modul termasuk `quality: supervisor` (keputusan 2026-08-11).

## Matriks aksi

Aksi yang mengubah data. Posisi yang tidak disebut hanya melihat.

| Menu | Aksi per posisi |
|---|---|
| Pemeriksaan Bahan Masuk | QC Assistant, QC Leader: catat hasil, putuskan Lulus / Reject / Ditolak · Quality Supervisor: sama + konfirmasi Ditolak |
| Inspeksi Bahan Masuk | QC Assistant, QC Leader: catat inspeksi, ubah · Quality Supervisor: sama + hapus |
| Rilis Batch | QC Production, QC Leader, QA Leader: ajukan rilis · PJT: putuskan lulus / ditolak · Quality Supervisor: hapus |
| Komplain Produk | Marketing: ajukan, ubah, pantau · QA Leader: validasi · Quality Supervisor: validasi, hapus |
| CAPA | staf Quality: buat, ajukan, finalisasi · Quality Supervisor: sama + hapus · Penyetuju CAPA: setujui |
| Dokumen Produksi Batch | QC Production, QC Leader, QA Leader: isi bagian uji |
| Persetujuan | Quality Supervisor: izin bawahan, pengajuan barang · PJT: putuskan rilis batch, setujui bahan pengganti · Direktur: setujui / tolak |
| Pengajuan, Tugas | semua: ajukan barang & dana, kas kecil, ruang, tugas ke tim lain; kerjakan dan ambil tugas |

## Pemisahan tugas dan jejak

Yang membuat catatan mutu tidak memutus catatan itu sendiri ([[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]], masih diusulkan; praktik CPOB: keputusan rilis oleh Penanggung Jawab Teknis).

| Data / tindakan | Yang menetapkan | Yang tidak boleh | Keadaan hari ini |
|---|---|---|---|
| Keputusan rilis batch | PJT | QC Production yang mengajukan; staf Quality lain | Belum ditegakkan sistem; rincian di issue privat repo kode (ADR 0149 §6) |
| Keputusan lot bahan masuk | QC Assistant; Ditolak dikonfirmasi Quality Supervisor | Gudang yang menerima bahan | Gudang dan QC terpisah; konfirmasi Ditolak belum ada di sistem |
| Bahan pengganti dalam batch | SPV Manufacture bersama PJT | Produksi yang menimbang | Belum ada di sistem (K-9, Fondasi M-20) |
| Persetujuan CAPA | Penyetuju produksi atau gudang | Quality yang membuat CAPA | Sudah terpisah |
| Validasi komplain | Quality | Marketing yang mengajukan | Sudah terpisah |
| Hapus catatan mutu | Quality Supervisor | Staf Quality | Sesuai; usul hapus lunak dengan jejak |

- **Wajib tercatat jejaknya**: keputusan rilis (lulus/ditolak, alasan, nasib barang, penanda tangan, waktu); keputusan lot bahan masuk (hasil per parameter, pemeriksa, dokumen QC, konfirmasi Ditolak); status CAPA; penghapusan catatan mutu dan pemasangan paket izin per posisi. Catatan mutu dibaca saat audit BPOM, jadi penghapusan permanen tanpa jejak tidak dapat diterima.
- **Kesegaran data**: seluruh data Quality langsung. Modul belum dipakai di prod (2026-10-13): koleksi `quality_*` yang terbentuk baru `quality_complaint`, berisi 0 dokumen. Ruang kerja wajib menampilkan keadaan kosong yang jujur ("belum ada lot yang diperiksa"), bukan angka nol yang terbaca sebagai kinerja.
- **Pemberitahuan**: sudah ada untuk pengajuan masuk tahap penyetuju; perlu dicek untuk CAPA diajukan dan komplain masuk/divalidasi; baru untuk lot menunggu pemeriksaan, batch diajukan rilis, dan batch diputuskan. Kategori inbox baru berarti container pengirim dan `notification-service` naik bersama.

## Perbaikan data

Disiapkan agent sebagai perubahan kode atau skrip dry-run beserta daftar sebelum/sesudah; data prod dijalankan manusia. Pemegang jabatan login ulang sesudahnya.

| Kode | Masalah | Usul | Jenis |
|---|---|---|---|
| D1 | PJT (QA RND) tidak berperan `quality`, tidak bisa membuka Rilis Batch. Sebagian sudah tertangani: `manufacture: rnd` sejak M-03 membuka Dokumen Produksi Batch | Beri akses Quality lewat tabel peran turunan (`kesekretariatan` / `qa_rnd`) atau paket posisi setelah katalog Quality ada (Q7) | kode + keputusan |
| D2 | QA Leader ber-`position_key` `qc_assistant` | Ubah ke `qa_leader`; paket per posisi kelak menempel ke key | data prod |
| D3 | Jabatan QC Leader tanpa pemegang | Pertahankan bila akan diisi; bila tidak, cabut dari master | keputusan |
| D4 | Quality belum punya katalog izin; menu digerbang kategori saja | Kunci menu `quality.view` / `quality.work` / `quality.manage` dengan entri fallback ke tier `quality`, supaya perilaku pemegang peran tak berubah; katalog backend menyusul | kode (Q-SG) |
| D5 | Hasil Produksi dan Formula tampil untuk QC tetapi tab WMS-nya tertutup bagi peran `qc` | Keluarkan dari menu Quality setelah dikonfirmasi uji pakai akun QC (Q6) | kode |

## Belum Diputuskan (TBD)

| Kode | Keputusan | Usul |
|---|---|---|
| Q1 | Letak CAPA. Rancangan Manufaktur menaruhnya di urusan K3 & Mutu | CAPA satu daun di Pengendalian Mutu; urusan Manufaktur menjadi K3 & GMP. Penyetuju CAPA produksi tetap melihatnya lewat izin |
| Q2 | Nama urusan | Pengendalian Mutu |
| Q3 | Dua jalur bahan masuk | Disatukan setelah K-4; sampai itu dua daun |
| Q4 | Satu tempat keputusan rilis | Mengikuti K-3 |
| Q5 | Cakupan komplain untuk Marketing | Per brand (hari ini seluruh peran Marketing membaca semua komplain lintas brand) |
| Q6 | Hasil Produksi dan Formula untuk QC | Dikeluarkan, kecuali dibutuhkan untuk spesifikasi produk dan COA |
| Q7 | Jalur akses PJT | Tabel peran turunan dulu, paket posisi setelah katalog Quality ada |

## Uji pakai

Rancangan diuji pada 3 sampai 5 orang dari posisi berbeda, satu sesi sekitar 15 menit: peserta memegang tetikus di prototipe, fasilitator membacakan tugas tanpa menunjukkan menunya, lalu mencatat hasil (lancar / ragu / tidak ketemu, salah klik, istilah yang dipakai). Peserta ditulis dengan kode, bukan nama.

| Posisi | Tugas | Jalur yang diharapkan |
|---|---|---|
| QC Assistant | Cari lot bahan yang paling lama menunggu pemeriksaan, lalu putuskan | Pengendalian Mutu › Pemeriksaan Bahan Masuk |
| QC Assistant | Catat hasil inspeksi satu lot bahan kemas | Pengendalian Mutu › Inspeksi Bahan Masuk |
| QC Production | Isi hasil uji pengolahan untuk batch yang sedang berjalan | Produksi › Dokumen Produksi Batch |
| QC Production | Ajukan rilis untuk batch yang ujinya sudah lengkap | Pengendalian Mutu › Rilis Batch |
| QC Production | Buat CAPA dari penyimpangan rekonsiliasi filling | Pengendalian Mutu › CAPA |
| PJT | Putuskan rilis batch yang sudah menunggu paling lama | Persetujuan atau Pengendalian Mutu › Rilis Batch |
| PJT | Tolak satu batch, lengkap dengan alasan dan nasib barang | Pengendalian Mutu › Rilis Batch |
| QA Leader | Buat CAPA dari penyimpangan batch dan ajukan ke penyetuju | Pengendalian Mutu › CAPA |
| QA Leader | Validasi komplain produk yang baru masuk | Pengendalian Mutu › Komplain Produk |
| Quality Supervisor | Cari CAPA yang lewat tenggat | Beranda › Perlu Tindakan atau Pengendalian Mutu › CAPA |
| Quality Supervisor | Konfirmasi bahan yang ditolak QC | Pengendalian Mutu › Pemeriksaan Bahan Masuk |
| Quality Supervisor | Lihat rekap KPI tim Quality bulan ini | KPI › tab tim |
| Marketing | Ajukan komplain mutu untuk satu batch produk | Komplain Produk |

Pertanyaan penutup: kalau menu ini Anda namai sendiri, Anda menyebutnya apa; apa yang dicari tetapi tak ketemu; menu mana yang tak pernah diperlukan; dari 1 sampai 5, seberapa mudah menemukan pekerjaan Anda.

## Dokumen Terkait

- [[Manufacture - Rancangan Menu per Posisi]] — rancangan menu Manufaktur (pasangan dok ini).
- [[Manufacture - Kajian Fondasi Sistem]] — temuan dan keputusan K-3, K-4, K-8, K-9 yang ditunggu.
- [[Manufacture - Dokumen Produksi Batch]] — Batch Record, termasuk spesifikasi produk (M-03).
- [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] — implementasi halaman Quality yang ditata rancangan ini.
- [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]] · [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]]
