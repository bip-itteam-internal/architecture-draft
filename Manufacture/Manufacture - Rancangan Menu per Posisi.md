## Deskripsi

*Rancangan menu, halaman, dan detail layar Manufaktur di erp-frontend untuk tiap jabatan yang terlibat (Manufaktur, Quality, Procurement, Finance, Marketing, Direksi), beserta alur proses yang menghubungkan halaman-halaman itu. Disusun dari kajian fondasi 2026-10-13 dan divisualkan sebagai prototipe (canvas Design) bergaya UI ERP. Dok ini menyalin **struktur** prototipe itu (menu, kolom, tahapan, keputusan); baris data contohnya sengaja tidak disalin.*

- **Status**: 🟡 Konsep / Draft. Rancangan, belum ada di kode kecuali halaman yang ditandai "Sudah dipakai" atau "Ada di ERP". Disusun 2026-10-13.
- **Dasar**: [[Manufacture - Kajian Fondasi Sistem]] (temuan dan TBD), [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]] (menu per urusan, digerbang izin posisi).
- **Persona dan diagram alur**: [[Manufacture - Fondasi Manufaktur Persona]].
- **Path di repo (yang sudah ada)**: `erp-frontend/src/features/manufacture/`, `bip-erp/services/manufacture/`, `bip-erp/services/employee/quality_*.go`, `bip-erp/services/procurement/`.

## Cara membaca

Status ERP tiap halaman:

| Penanda | Arti |
|---|---|
| ✅ Dipakai | sudah dipakai di prod hari ini |
| Ada | sudah ada di ERP, belum pernah dipakai |
| Ubah | ada di ERP, perlu diubah agar cocok dengan alur |
| Baru | belum ada di kode |
| Fase berikut | sengaja ditunda |

- Menu disusun per **urusan** dan digerbang izin posisi (ADR 0149). Departemen lain hanya melihat potongan miliknya.
- **Persetujuan**, **Pengajuan**, dan **KPI** adalah menu umum yang sama untuk semua jabatan; isinya berbeda per posisi.
- `(baca)` = jabatan itu hanya melihat halaman, tanpa aksi.
- Gudang Utama, Sadewa, Sidareja, dan Tinggarjaya memakai menu yang sama; bedanya cakupan data per gudang.
- Setiap menu baru wajib membawa panduan pemakaian (aturan tim panduan per menu).
- **TBD n** merujuk ke daftar "Belum Diputuskan" di dok kajian.

## Peta menu per departemen

| Departemen | Jabatan | Menu umum | Urusan dan halaman | Catatan lintas departemen |
|---|---|---|---|---|
| Gudang | Admin, Staf, Leader Warehouse | Beranda, KPI | **Bahan & Gudang**: Penerimaan Bahan, Serah Bahan ke WIP, Stok & Kartu Stok, Stock Opname, Gudang Barang Jadi, Mutasi Antar Gudang | QC Assistant memakai layar penerimaan yang sama untuk keputusan QC |
| Produksi | Admin Produksi, Leader Produksi | Beranda, KPI | **Produksi**: Jadwal Produksi, Batch Record, Realisasi Produksi | Operator tidak menginput ERP; Admin Produksi menyalin dari form kertas |
| Quality & PJT | QC Assistant, QC Production, Supervisor Quality, Penanggung Jawab Teknis | Beranda, Persetujuan, KPI | **Mutu**: QC Bahan Masuk, Keputusan Rilis Batch, COA Keluar, CAPA, Komplain Produk. **Produksi**: Batch Record (bagian uji) | Mengisi bagian uji di Batch Record yang sama dengan Produksi |
| PPIC | PPIC | Beranda, Pengajuan, KPI | **Perencanaan**: Rencana Produksi, Kebutuhan Bahan (MRP), Production Order Masuk, Formula, Safety Stock & ROP | Permintaan Pengadaan dikirim lewat menu Pengajuan ke Procurement |
| SPV Manufacture | SPV Manufacture; Direktur melihat ringkasan | Beranda (ringkasan), Persetujuan, KPI | Semua urusan manufaktur: Perencanaan, Produksi, Bahan & Gudang, Laporan | Persetujuan: rencana, keluar bahan, penyesuaian stok, penggantian bahan (bersama APJ) |
| Procurement | Leader Procurement, Staff Inventory | Beranda, KPI | **Pengadaan**: Permintaan dari PPIC, Status PO & Kedatangan, Retur ke Pemasok | PPIC membaca status PO dan ETA; PO hanya dibuat di Procurement |
| Finance | Supervisor FAT, Accounting, Cost Control | Beranda, Persetujuan, KPI | **Laporan**: Mutasi Persediaan Pabrik, Fisik vs Accurate, Biaya per Batch | Persetujuan: validasi penyesuaian stok sebelum dikirim ke Accurate |
| Marketing | SPV Brand | Beranda, Pengajuan, KPI | **Barang Jadi**: Ketersediaan Barang Jadi (produk brand sendiri) | Production Order diajukan lewat menu Pengajuan, tanpa masuk menu Manufaktur |

## Menu per jabatan

| Jabatan | Departemen | Menu | Persetujuan yang masuk ke dia |
|---|---|---|---|
| SPV Manufacture | Manufaktur | Umum: Persetujuan, KPI · Perencanaan: Rencana Produksi, MRP (baca), Production Order Masuk (baca), Formula (baca) · Produksi: Jadwal, Batch Record (baca), Realisasi, Ceklis GMP & K3, Kondisi Mesin (baca) · Bahan & Gudang: Stok (baca), Stock Opname, Gudang Barang Jadi (baca) · Laporan: Fisik vs Accurate, Mutasi Persediaan, Biaya per Batch (semua baca) | penggantian bahan, rencana produksi, penyesuaian stok, pengadaan |
| PPIC | Manufaktur | Umum: Persetujuan, Permintaan Pengadaan, KPI · Perencanaan: Rencana Produksi, MRP, Production Order Masuk, Formula, Safety Stock & ROP · Produksi: Jadwal, Realisasi (baca) · Bahan & Gudang: Stok (baca) | permintaan bahan dari Admin Produksi |
| Admin Produksi | Manufaktur | Umum: Permintaan Bahan, KPI · Produksi: Batch Record, Jadwal (baca), Realisasi | - |
| Leader Produksi | Manufaktur | Umum: KPI · Produksi: Jadwal, Batch Record, Realisasi (baca), Ceklis GMP & K3, Kondisi Mesin | - (paraf verifikasi di Batch Record) |
| Operator Produksi | Manufaktur | Umum: Lapor Kerusakan Mesin (fase berikut), KPI | - |
| Leader Warehouse | Manufaktur | Umum: Persetujuan, KPI · Bahan & Gudang: Penerimaan, Serah ke WIP, Stok, Opname, Barang Jadi, Mutasi Antar Gudang | hasil opname |
| Admin Warehouse | Manufaktur | Umum: KPI · Bahan & Gudang: sama dengan Leader Warehouse | - |
| Staf Warehouse | Manufaktur | Umum: KPI · Bahan & Gudang: Penerimaan, Serah ke WIP, Opname, Stok (baca), Barang Jadi (baca) | - |
| Admin Return | Manufaktur | Umum: KPI · Barang Jadi: Scan Retur Marketplace | - |
| QC Assistant | Quality | Umum: KPI · Mutu: QC Bahan Masuk, Komplain (baca) | - |
| QC Production | Quality | Umum: KPI · Mutu: COA Keluar, CAPA · Produksi: Batch Record | - |
| Supervisor Quality | Quality | Umum: Persetujuan, KPI · Mutu: QC Bahan Masuk (baca), Keputusan Rilis (baca), COA, CAPA, Komplain · Produksi: Batch Record (baca) | bahan ditolak, tutup CAPA |
| Penanggung Jawab Teknis (APJ) | Quality | Umum: Persetujuan, KPI · Mutu: Keputusan Rilis, COA (baca) · Perencanaan: Formula (baca) · Produksi: Batch Record (baca) | rilis batch, penggantian bahan |
| Leader Procurement | Procurement | Umum: Persetujuan, KPI · Pengadaan: Permintaan dari PPIC, Status PO, Retur ke Pemasok | pengadaan |
| Staff Inventory | Procurement | Umum: KPI · Pengadaan: Permintaan dari PPIC, Status PO, Retur (baca) · Perencanaan: Safety Stock (baca) | - |
| Finance Supervisor | Finance | Umum: Persetujuan, KPI · Laporan: Mutasi Persediaan, Fisik vs Accurate, Biaya per Batch | validasi penyesuaian stok |
| Senior Accounting | Finance | Umum: KPI · Laporan: Mutasi Persediaan, Fisik vs Accurate, Biaya per Batch (baca) | - |
| Cost Control | Finance | Umum: KPI · Laporan: Biaya per Batch, Mutasi Persediaan (baca) | - |
| SPV Brand | Marketing | Umum: Production Order, KPI · Barang Jadi: Ketersediaan Barang Jadi | - |
| Direktur | Direksi | Umum: Persetujuan, KPI · Laporan: Realisasi, Fisik vs Accurate, Mutasi, Biaya per Batch (semua baca) | penghentian produk, pengadaan bernilai di atas ambang (TBD) |

Setiap jabatan juga punya **Beranda** berisi ringkasan angka posisinya dan daftar tugas yang menunggu.

## Katalog halaman

### Umum

| Halaman | Status | Rute saat ini | Isi | Kolom | Catatan |
|---|---|---|---|---|---|
| Persetujuan | Baru | menu umum ADR 0149 | hanya hal yang menunggu keputusan pembaca, dari departemen mana pun | Jenis, Dari, Rincian, Diajukan, Status | satu menu untuk semua jenis persetujuan |
| KPI | ✅ Dipakai | `/kpi` | KPI posisi yang dihitung otomatis; bila data belum ada, statusnya ditulis apa adanya, bukan nol | KPI, Bobot, Target, Realisasi, Sumber data, Status | |
| Permintaan Pengadaan (PPIC) | Ubah | `/pengajuan-barang` | permintaan bahan ke Procurement hasil MRP | No., Tgl, Keperluan, Bahan, Qty, Estimasi datang, Status | rantai pengajuan barang perlu tahap PPIC |
| Permintaan Bahan (Admin Produksi) | Ubah | `/manufacture/orders-po` (Material Order) | permintaan bahan ke gudang untuk batch terjadwal, dihitung dari formula, disetujui PPIC | No. permintaan, Batch, Jumlah bahan, Diajukan, Status | menggantikan Form Permintaan Produksi kertas |
| Production Order (SPV Brand) | Ubah | `/manufacture/mo-barang-jadi` | PO brand ke PPIC, boleh diubah satu kali sebelum dikunci | No. PO, Produk, Qty, Diajukan, Jadwal produksi, Status | MOQ masih usulan |
| Lapor Kerusakan Mesin | Fase berikut | - | laporan gangguan mesin ke Leader Produksi | Tgl, Mesin, Deskripsi, Tindakan sementara, Status | |

### Bahan & Gudang

| Halaman | Status | Rute saat ini | Isi | Kolom | Catatan |
|---|---|---|---|---|---|
| Penerimaan Bahan | Ubah | `/manufacture/raw-materials` | bahan datang dari pemasok; tiap lot masuk Karantina sampai QC memutuskan | Tgl, No. SJ, Pemasok, Bahan, Qty SJ, No. lot, ED, Status | TBD 4; satu lot satu bahan; bahan kemas tak ber-ED; menyatukan antrean RM, cek RM, dan incoming QC |
| Serah Bahan ke WIP | Ubah | `/manufacture/orders-po` (Material Order) | permintaan produksi yang disetujui PPIC; lot dipilih FEFO | No. permintaan, Batch tujuan, Jumlah bahan, Diajukan, Disetujui, Status | TBD 2: stok berkurang saat serah ke WIP, pemakaian final saat batch selesai |
| Stok & Kartu Stok | Ubah | `/manufacture/stock` | saldo per bahan per gudang, dipisah Lulus dan Karantina; kartu stok dicetak untuk BPOM | Kode, Bahan, Kategori, Gudang, Lulus, Karantina, ED terdekat, ROP | TBD 1, TBD 5 (dua kartu: kosmetik, OT) |
| Stock Opname | Ubah | `/manufacture/cycle-count` | opname mingguan; selisih menjadi satu jalur penyesuaian | Opname, Gudang, Tanggal, Bahan dihitung, Akurasi, Status | menyatukan cycle count dan selisih RM |
| Gudang Barang Jadi | Ubah | `/manufacture/finished-goods` | FG masuk sebagai karantina, baru bisa dikirim setelah rilis; Surat Jalan dicetak bersama COA | No. batch, Produk, Qty, Masuk, Status, COA | status FG karantina baru; TBD 9 |
| Mutasi Antar Gudang | Ada | `/manufacture/mutasi-gudang` | pemindahan antar gudang dengan kirim dan terima | No. mutasi, Dari, Ke, Barang, Qty kirim, Qty terima, Status | perlu dikaitkan ke status FG (hanya FG rilis) |
| Scan Retur Marketplace | ✅ Dipakai | `/manufacture/finished-goods` (scan retur) | retur Shopee dan TikTok discan per resi dan kembali ke stok | Waktu, Resi, Channel, Produk, Qty, Kondisi, Status | satu-satunya fitur manufaktur yang aktif; tidak diubah |

### Produksi

| Halaman | Status | Rute saat ini | Isi | Kolom | Catatan |
|---|---|---|---|---|---|
| Jadwal Produksi | Baru | - | jadwal per shift dari rencana PPIC; batch hanya bisa dimulai bila bahan formula lengkap dan lulus QC | Tgl, Shift, Produk, Target, Tim, Kesiapan bahan, Status | TBD 10 |
| Batch Record | Ubah | `/manufacture/dokumen-produksi-batch` | satu catatan per batch mengikuti form kertas; penyimpangan dihitung sistem | No. batch, Produk, Ukuran, Tahap, Penyimpangan, Uji QC, Rilis | tambahan: spesifikasi produk dan penyimpangan otomatis; menggantikan Laporan Hasil Produksi dan `POST /production` |
| Realisasi Produksi | Ada | `/manufacture/production` | target vs realisasi per shift dan tim; sementara dari spreadsheet PPIC (jembatan) | Tgl, Shift, Produk, Target, Realisasi, %, Tim | |
| Ceklis GMP & K3 | Ada | `/manufacture/k3-gmp` | ceklis GMP bulanan, APD harian, laporan kecelakaan | Tgl, Jenis, Area, Skor, Temuan, Status | belum dipakai |
| Kondisi Mesin | Fase berikut | - | log harian mesin, inspeksi, perawatan, laporan kerusakan | Mesin, Area, Kondisi, Inspeksi terakhir, Laporan terbuka, Status | departemen teknisi TBD 8 |

### Mutu

| Halaman | Status | Rute saat ini | Isi | Kolom | Catatan |
|---|---|---|---|---|---|
| QC Bahan Masuk | Ubah | `/quality/pengecekan-rm` | antrean lot di karantina; keputusan QC langsung mengubah status stok | Diterima, Bahan, Pemasok, Lot, Qty, COA pemasok, Umur, Keputusan | satu gerbang menggantikan `quality_incoming`, `quality_rm_check`, dan karantina procurement; KPI ≤ 3 hari kerja |
| Keputusan Rilis Batch | Ubah | `/quality/batch-release` | batch yang menunggu keputusan PJT | Batch, Produk, Selesai, Menunggu, Uji QC, Penyimpangan, Keputusan | satu keputusan di Batch Record; TBD 3 |
| COA Keluar | Baru | - | Certificate of Analysis per batch dari spesifikasi, uji QC, dan rilis; dilampirkan ke Surat Jalan | Batch, Produk, Lini, Parameter uji, Kelengkapan, Penanda tangan | TBD 9; tiga lini: Pangan, OT, Kosmetik |
| CAPA | Ada | `/quality/capa` | tindakan perbaikan dan pencegahan dari penyimpangan, audit, komplain | No., Sumber, Masalah, PIC, Tenggat, Status | bisa dibuat otomatis dari penyimpangan Batch Record |
| Komplain Produk | Ada | `/quality/komplain` | komplain dari Marketing dan pelanggan, ditelusuri ke batch | Tgl, Produk, Batch, Kategori, Sumber, Status | |

### Perencanaan

| Halaman | Status | Rute saat ini | Isi | Kolom | Catatan |
|---|---|---|---|---|---|
| Rencana Produksi | Ubah | `/manufacture/rencana-produksi` (simulasi) | dari Production Order dan stok FG, disetujui SPV Manufacture; hari ini hanya simulasi | Minggu, Produk, Sisa PO, Stok FG, Target, Kesiapan bahan, Status | meniru tab Rencana dan Prioritas spreadsheet PPIC |
| Kebutuhan Bahan (MRP) | Ubah | `/manufacture/rencana-produksi` | rencana × formula, dikurangi stok lulus dan bahan sedang dipesan | Bahan, Kebutuhan, Stok lulus, Sedang dipesan, Kekurangan, ROP, Status | bahan sedang dipesan dibaca dari PO Procurement |
| Production Order Masuk | Ubah | `/manufacture/orders-po` (MO Marketing) | PO dari Marketing, dicek MOQ, boleh diubah satu kali | No. PO, Brand, Produk, Qty, MOQ, Perubahan, Status | tiga rute MO lama disatukan |
| Formula Produk | Ada | `/manufacture/raw-materials?form=formula` | komposisi per fase, versi terdaftar, susut, lead time | Kode, Produk, Lini, Versi, Jumlah bahan, Status registrasi, Diubah | formula spreadsheet perlu dibersihkan sebelum jadi sumber |
| Safety Stock & ROP | Baru | - | rata-rata dan maksimum pemakaian per hari, safety stock, titik pesan ulang | Bahan, Rata-rata/hari, Maks/hari, Lead time, Safety stock, ROP, Stok lulus, Status | meniru tab safety stock spreadsheet PPIC |

### Pengadaan

| Halaman | Status | Rute saat ini | Isi | Kolom | Catatan |
|---|---|---|---|---|---|
| Permintaan dari PPIC | Ubah | `/pengajuan-barang` | permintaan bahan baku dan kemas untuk produksi | No., Keperluan, Bahan, Qty, Dibutuhkan, Status | |
| Status PO & Kedatangan | Ada | `/po` (procurement) | PO bahan dengan ETA, qty diterima, qty lulus QC; dibaca PPIC sebagai bahan sedang dipesan | PO, Pemasok, Bahan, Qty, ETA, Diterima, Lulus QC, Status | PO di modul manufaktur dihapus |
| Retur ke Pemasok | Baru | - | bahan ditolak QC dikembalikan atau dipotong dari tagihan | No. retur, Pemasok, Bahan, Lot, Qty, Alasan, Penyelesaian, Status | hari ini manual |

### Laporan (Finance)

| Halaman | Status | Rute saat ini | Isi | Kolom | Catatan |
|---|---|---|---|---|---|
| Mutasi Persediaan Pabrik | Baru | - | saldo awal, masuk, keluar, saldo akhir per kategori dan gudang | Kategori, Saldo awal, Masuk, Keluar, Saldo akhir, Nilai | 7 kategori (PJ/BB/BK × OT/Kosmetik + Pangan), 4 gudang |
| Fisik vs Accurate | Baru | - | hasil opname dibanding saldo Accurate per kategori | Kategori, Barang, Sama persis, Selisih ≤ 2%, Selisih > 2% | dasar keputusan TBD 1 |
| Biaya per Batch (HPP) | Baru | - | biaya bahan per batch dari penimbangan nyata dibanding standar formula | Batch, Produk, Qty, Biaya standar, Biaya nyata, Selisih, Per unit | TBD 6 |

### Barang Jadi (Marketing)

| Halaman | Status | Rute saat ini | Isi | Kolom | Catatan |
|---|---|---|---|---|---|
| Ketersediaan Barang Jadi | Baru | - | stok FG yang sudah dirilis untuk produk brand pembaca | Produk, Siap kirim, Menunggu rilis, PO berjalan, Status | hanya potongan milik brand pembaca |

## Detail (Sheet)

Baris di halaman daftar membuka detail berbentuk Sheet. Tahapan ditulis berurutan.

| Detail | Dibuka dari | Tahapan | Bagian | Aksi |
|---|---|---|---|---|
| Batch Record | Batch Record | kesiapan ruang → penimbangan → pengolahan → pengemasan → uji QC → keputusan rilis | spesifikasi produk (baru, dasar COA), kesiapan ruang (PR/04/PD/011/03), penimbangan (R = ditimbang/teoritis, batas ≤ 2%, kolom bahan formula vs bahan dipakai), pengolahan per fase dengan Hasil QC, rekonsiliasi (batas 98-102%), pengemasan (PR/SOP/007/01/F/01), penyimpangan (dihitung sistem), paraf digital per peran | Cetak format BPOM, Ajukan ke PJT |
| Keputusan rilis | Keputusan Rilis Batch | - | ringkasan uji QC, penyimpangan (wajib dibaca), keputusan: Lulus / Ditolak, alasan (wajib bila ditolak), nasib barang: karantina / musnah / rework / lainnya (TBD 3), tanda tangan PJT | Simpan keputusan |
| Penerimaan & QC lot | Penerimaan Bahan, QC Bahan Masuk | diterima gudang → label karantina → pemeriksaan QC → simpan atau pisah | pemeriksaan QC (identitas, kemasan, pemerian), sampling bahan kemas (√n + 1 dus), keputusan: Lulus / Reject / Ditolak, qty lulus, tindak lanjut (retur dibuat otomatis) | Cetak label, Simpan keputusan |
| COA | COA Keluar | - | hasil analisa (parameter, spesifikasi, hasil, metode), pengesahan dan penanda tangan (TBD 9) | Unduh PDF, Terbitkan |
| Surat Jalan + COA | Gudang Barang Jadi | disiapkan → dicek Leader → dikirim → diterima tujuan | barang per batch dengan COA terlampir; hanya batch berstatus Rilis | Cetak Surat Jalan + COA |
| Production Order | Production Order, PO Masuk | diajukan → diterima PPIC → dijadwalkan → diproduksi → dirilis QC → siap kirim | jadwal produksi terkait, riwayat perubahan (1x sebelum dikunci; sesudahnya jadi upgrade produk atau NPD) | Ubah (sisa 1x), Terima |
| Kesiapan bahan | Jadwal Produksi, Rencana Produksi | - | bahan formula vs stok (butuh, stok lulus, karantina, dipesan), aturan penggantian bahan (TBD 10) | Ajukan penggantian bahan, Ajukan pengadaan |
| Permintaan bahan | Serah Bahan ke WIP, Permintaan Bahan | diajukan → disetujui PPIC → diserahkan → sisa kembali | bahan dengan lot FEFO otomatis, sisa kembali: layak pakai / rusak / reject | Catat sisa kembali, Serahkan ke WIP |
| Opname & penyesuaian | Stock Opname | hitung fisik → diperiksa Leader → disetujui SPV → validasi Finance → kirim ke Accurate | selisih per bahan dengan alasan, BA opname | Unduh BA, Setujui/validasi |
| Kartu stok | Stok & Kartu Stok | - | mutasi per periode (keterangan, referensi, lot, masuk, keluar, saldo) | Cetak kartu stok |
| Formula produk | Formula Produk | - | komposisi per fase dengan daftar **bahan pengganti sah** (INCI sama), riwayat versi disetujui PJT | Buat versi baru, Simpan |
| Mutasi antar gudang | Mutasi Antar Gudang | dibuat → dikirim → diterima | barang, qty kirim, qty terima, selisih | Konfirmasi terima |
| Mesin & laporan kerusakan | Kondisi Mesin, Lapor Kerusakan | dilaporkan → diterima Leader → diperbaiki teknisi → diverifikasi Leader | log harian cek pra-operasi | Catat perbaikan, Verifikasi siap pakai |
| CAPA | CAPA | dibuat → investigasi → tindakan → verifikasi → ditutup | uraian: permasalahan, akar masalah, perbaikan, batas waktu (format PR/02/QA/012/04) | Tambah tindakan, Ajukan selesai |
| Permintaan pengadaan | Permintaan Pengadaan, Permintaan dari PPIC, Status PO | diajukan PPIC → disetujui SPV → PO terbit → datang → lulus QC | status kedatangan | Proses ke PO |
| Retur ke pemasok | Retur ke Pemasok | ditolak QC → retur dibuat → dijemput → dikreditkan | penyelesaian: retur barang, potong tagihan, atau dipakai dengan persetujuan khusus SPV Manufacture | Tandai selesai |
| Biaya per batch | Biaya per Batch | - | rincian bahan: standar, nyata, harga rata-rata, selisih | Unduh |

## Alur proses lintas departemen

Setiap langkah menyebut siapa yang mengerjakan, di menu apa, dan apa hasilnya.

### 1. Permintaan sampai rencana produksi (Baru)

| # | Pelaku | Aksi | Hasil | Menu |
|---|---|---|---|---|
| 1 | SPV Brand | Ajukan Production Order | qty per produk, dicek MOQ, boleh diubah 1x sebelum dikunci | Pengajuan · Production Order |
| 2 | PPIC | Terima PO, susun rencana mingguan | rencana per minggu dari sisa PO dan stok FG | Rencana Produksi |
| 3 | SPV Manufacture | Setujui rencana | rencana dikunci; perubahan berikutnya tercatat | Persetujuan |
| 4 | PPIC | Hitung kebutuhan bahan | rencana × formula − stok lulus − bahan sedang dipesan | Kebutuhan Bahan |
| 5 | PPIC | Ajukan pengadaan bahan kurang | permintaan ke Procurement | Pengajuan · Permintaan Pengadaan |

Jika di bawah MOQ: PPIC mengembalikan untuk revisi → SPV Brand mengubah qty (sisa 1x).

### 2. Pengadaan dan bahan masuk (Ada di ERP, perlu diubah)

| # | Pelaku | Aksi | Hasil | Menu |
|---|---|---|---|---|
| 1 | SPV Manufacture | Setujui permintaan pengadaan | rantai pengajuan barang ditambah tahap PPIC | Persetujuan |
| 2 | Procurement | Terbitkan PO, pantau ETA | PPIC membaca status ini sebagai bahan sedang dipesan | Status PO & Kedatangan |
| 3 | Staf Warehouse | Terima barang | cek SJ dan COA pemasok, timbang/hitung, label identitas + karantina (kuning); TBD 4 | Penerimaan Bahan |
| 4 | QC Assistant | Periksa lot | sampling sesuai jenis bahan; Lulus / Reject / Ditolak; TBD 4 | QC Bahan Masuk |
| 5 | Gudang | Simpan bahan lulus | stok Lulus bertambah per lot; kartu stok terisi otomatis | Stok & Kartu Stok |

Jika ditolak: Supervisor Quality mengonfirmasi dan memberi label merah → Procurement meretur ke pemasok → Finance memotong tagihan bila perlu.

### 3. Produksi satu batch (Ada di ERP, perlu diubah)

| # | Pelaku | Aksi | Hasil | Menu |
|---|---|---|---|---|
| 1 | PPIC | Tetapkan jadwal per shift | batch per tanggal, shift, dan tim | Jadwal Produksi |
| 2 | Sistem | Gerbang kesiapan bahan | batch hanya bisa dimulai bila semua bahan formula ada dan lulus QC; TBD 10 | Jadwal Produksi |
| 3 | Admin Produksi | Ajukan permintaan bahan | dihitung dari formula, disetujui PPIC | Pengajuan · Permintaan Bahan |
| 4 | Gudang | Serah bahan ke WIP | lot dipilih FEFO, stok gudang berkurang; TBD 2 | Serah Bahan ke WIP |
| 5 | Produksi | Olah dan kemas | Batch Record disalin Admin dari kertas, QC Production mengisi uji, penyimpangan dihitung sistem | Batch Record |
| 6 | Gudang | Terima sisa dan FG | sisa dipilah layak/rusak/reject; FG masuk sebagai karantina | Gudang Barang Jadi |

Jika bahan kurang: PPIC mengajukan pengadaan → atau SPV Manufacture menyetujui bahan pengganti → PJT ikut setuju bila komposisi berubah.

### 4. Rilis, COA, dan pengiriman (Baru)

| # | Pelaku | Aksi | Hasil | Menu |
|---|---|---|---|---|
| 1 | QC Production | Lengkapi uji dan ajukan rilis | spesifikasi produk terisi, termasuk pH | Batch Record |
| 2 | PJT | Putuskan rilis | target ≤ 24 jam sejak produksi selesai; TBD 3 | Persetujuan · Keputusan Rilis |
| 3 | QC Production | Terbitkan COA | dari spesifikasi, hasil uji, dan keputusan rilis; TBD 9 | COA Keluar |
| 4 | Gudang | Buat Surat Jalan + COA | hanya batch berstatus Rilis; status Dikirim lalu Diterima | Gudang Barang Jadi |
| 5 | SPV Brand | Lihat ketersediaan | stok FG rilis per produk brand | Ketersediaan Barang Jadi |

Jika ditolak: PJT wajib menulis alasan dan nasib barang → Gudang menjalankan karantina/musnah/rework → sistem membuat CAPA dari penyimpangan.

### 5. Opname dan pembukuan persediaan (Ada di ERP, perlu diubah)

| # | Pelaku | Aksi | Hasil | Menu |
|---|---|---|---|---|
| 1 | Staf Warehouse | Hitung fisik | opname mingguan per gudang | Stock Opname |
| 2 | Leader Warehouse | Periksa dan buat BA | selisih diberi alasan | Persetujuan |
| 3 | SPV Manufacture | Setujui penyesuaian | satu jalur penyesuaian stok | Persetujuan |
| 4 | Finance | Validasi | sebelum dibukukan; TBD 1 | Persetujuan · Validasi |
| 5 | Accurate | Penyesuaian terkirim | push otomatis dari ERP; TBD 1 | Otomatis |

### 6. Retur marketplace (✅ sudah dipakai)

| # | Pelaku | Aksi | Hasil | Menu |
|---|---|---|---|---|
| 1 | Admin Return | Scan resi retur | Shopee dan TikTok | Scan Retur Marketplace |
| 2 | Gudang | Barang masuk stok FG atau dipisah | kondisi baik masuk stok, rusak dipisah | Gudang Barang Jadi |
| 3 | Accurate | Gerakan terkirim | push sudah menyala di prod | Otomatis |

## Belum Diputuskan (TBD)

Seluruh TBD yang dirujuk di sini tercatat di [[Manufacture - Kajian Fondasi Sistem]]. Tambahan yang hanya muncul di rancangan ini:

- **MOQ Production Order**: angka 10.000 pcs di prototipe hanya usulan, belum disepakati bersama Marketing.
- **Ambang nilai pengadaan** yang membutuhkan persetujuan Direktur.
- **Penanda tangan COA** per lini.

## Dokumen Terkait

- [[Manufacture - Kajian Fondasi Sistem]] · [[Manufacture - Fondasi Manufaktur Persona]] · [[Manufacture - Dashboard per Posisi]] · [[Manufacture - Dokumen Produksi Batch]]
- [[Microservices - Manufacture Service]] · [[API - Manufacture Service]] · [[Microservices - Procurement Service]]
- [[QA - Rancangan Menu per Posisi]] (rancangan menu Quality per posisi; letak CAPA = keputusan Q1 di sana) · [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] · [[ADR - 0149 Sidebar Satu Daftar Urusan, Menu Digerbang Izin Posisi, Beranda Ruang Kerja Posisi]]
