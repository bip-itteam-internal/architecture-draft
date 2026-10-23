> **Status**: 🟢 **Diterima**, 2026-10-23, oleh **Finance** (jawaban Senior Accounting, ditegaskan IT sebagai jawaban Pemutus pada 2026-10-23). Diusulkan 2026-10-19 sebagai keputusan K-1 di [[ANALISA - Fondasi Manufaktur]]. Akun pemakaian produksi ditunda bersama K-2/K-6; tanggal peralihan belum ditetapkan.

## Untuk Manajemen

**Apa yang perlu diputuskan.** Angka stok bahan baku dan barang jadi pabrik **mana yang dipegang**: angka di ERP (dicatat gudang dan produksi, lalu dikirim ke Accurate), atau angka di Accurate (ERP hanya menyalin). Juga urutan validasi stock opname sebelum selisihnya dibukukan.

**Usulan singkat.**
1. **Stok operasional pabrik = stok di ERP**: bertambah saat bahan diterima atau barang jadi selesai, berkurang saat bahan keluar ke produksi atau barang dikirim. Ini sama dengan keputusan untuk stok GA ([[ADR - 0175 Stok GA di ERP Jadi Stok Operasional, Barang Keluar dan Penyesuaian Dikirim ke Accurate]]).
2. **Accurate tetap acuan akuntansi** dan menerima pergerakan ERP sebagai **Penyesuaian Persediaan** otomatis.
3. **Tarik stok dari Accurate yang menimpa angka ERP tiap 6 jam dihentikan**, diganti laporan selisih ERP vs Accurate yang hanya membaca.
4. **Selisih opname baru dibukukan sesudah divalidasi Finance**, sesuai syarat Finance yang sudah tercatat di kajian.

**Siapa yang terdampak.** Gudang RM dan FG, produksi, PPIC (angka stok untuk rencana), Finance (Penyesuaian Persediaan di Accurate, validasi opname).

**Kenapa perlu ditulis sekarang.** Hari ini sistem punya **dua pemilik sekaligus**: transaksi gudang menambah dan mengurangi angka ERP, tetapi setiap 6 jam angka bahan baku **ditimpa** dengan angka Accurate. Begitu gudang mulai mencatat di ERP (sasaran Fase 1), pengeluaran yang belum sampai ke Accurate akan "kembali" ke stok setiap putaran. PPIC lalu melihat angka yang tidak pernah ada di rak, tanpa satu pun pesan galat. Butir M-12 (satu jalur penyesuaian stok) dan M-25 (laporan mutasi vs Accurate) menunggu keputusan ini.

**Apa yang tidak dijanjikan.** Akun beban dan gudang Accurate untuk tiap jenis penyesuaian (lihat pertanyaan 4). HPP per batch (keputusan K-6). Pemilik master barang (K-7, [[ADR - 0136 Pemilik Master Barang dan Master Gudang]]).

**Perkiraan besaran kerja.** Sedang (estimasi): mematikan penimpaan berkala, laporan selisih baca-saja, satu jalur penyesuaian opname dengan validasi Finance, dan perbaikan pengiriman ke Accurate (lihat Context, temuan push).

## Pertanyaan untuk Pemutus

Rekomendasi disertakan; Pemutus boleh memilih lain.

| # | Pertanyaan | Pilihan | Rekomendasi |
|---|---|---|---|
| 1 | Angka stok pabrik yang dipegang | (a) ERP, Accurate menerima penyesuaian; (b) Accurate, ERP hanya menyalin dan gudang tetap mencatat di Accurate; (c) seperti sekarang (dua-duanya menulis) | **(a)**, sama dengan stok GA. (b) berarti gudang mengetik di Accurate dan ERP tak bisa dipakai untuk rencana harian; (c) membuat angka bergerak sendiri |
| 2 | ~~Bahan dari pemasok sampai ke Accurate lewat apa~~ | - | **Sudah terjawab, tidak ditanyakan lagi**: [[ADR - 0015 Push Pergerakan WMS ke Accurate]] menetapkan barang masuk dari pemasok tercakup Faktur Pembelian Finance, bukan dikirim ERP. Konsekuensinya ada jeda (ERP naik saat diterima gudang, Accurate saat faktur dibukukan) yang ditandai laporan selisih |
| 3 | Batas selisih stock opname yang boleh langsung dibukukan | angka batas / tidak ada batas (semua diverifikasi) | **Sebagian sudah ada di SOP**: SOP Stock Opname ([[WH - SOP Posisi Admin Warehouse]]) menyebut FAT memverifikasi hasil opname dan penyesuaian disetujui SPV Manufaktur. Yang ditanyakan tinggal batas selisihnya |
| 4 | Akun dan gudang Accurate untuk Penyesuaian Persediaan pabrik (pemakaian produksi, rusak/kedaluwarsa, selisih opname) | ditetapkan Finance | Perlu daftar dari Finance. **Mendesak**: pengiriman hari ini tidak menyebut akun, jadi Accurate memakai bawaannya, **Ekuitas Saldo Awal** (bukan akun beban), dan Accurate belum punya gudang bahan baku (lihat Context) |
| 5 | Angka awal saat beralih | opname fisik penuh di hari H / angka Accurate hari H | **Opname fisik penuh**, karena kajian mencatat stok fisik dan Accurate sudah berbeda (tab Mutasi + SO di spreadsheet PPIC) |

*Dicocokkan ke vault, kode, dan data prod 2026-10-19 sebelum dikirim, supaya Pemutus tak ditanya hal yang sudah tertulis. Pertanyaan disampaikan lewat Senior Accountant Finance; Pemutus di baris status tetap Finance Supervisor sampai ditegaskan lain.*

### Jawaban Finance (Senior Accountant, 2026-10-19, lewat WA)

| # | Jawaban | Arti untuk keputusan |
|---|---|---|
| 1 | "ERP sync ke Accurate" | Pilihan (a): stok operasional di ERP, Accurate menerima penyesuaian. Sesuai usulan Decision 1 |
| 3 | "Wajib cek FAT" | Tidak ada batas selisih: **semua** selisih opname diverifikasi FAT sebelum menjadi penyesuaian (Decision 4) |
| 4 | "Perlu diskusi langsung karena pencatatan pemakaian produksi cukup kompleks" | **Masih terbuka.** Akun dan gudang Accurate menunggu rapat dengan Finance; paket pengiriman (Decision 3) tidak dikerjakan sebelum itu |
| 5 | "Seharusnya disesuaikan dengan fisik (to be confirmed)" | Condong ke opname fisik penuh di hari peralihan; **belum final** |

Status tetap Diusulkan: butir 4 dan 5 belum final, dan belum ditegaskan apakah jawaban ini sudah atas nama Finance Supervisor.

### Lembar penyelesaian (disiapkan 2026-10-23)

Tiga hal tersisa sebelum status bisa menjadi Diterima. Daftar akun dan gudang di bawah dibaca dari Accurate prod 2026-10-23 (baca saja), supaya Finance cukup memilih.

**A. Penegasan.** Apakah jawaban 1 ("ERP sync ke Accurate") dan 3 ("wajib cek FAT") dari Senior Accountant sudah atas nama Finance Supervisor? Bila ya, kedua butir itu final.

**B. Akun lawan per jenis penyesuaian (pertanyaan 4).** Akun persediaan mengikuti jenis barang yang tersedia di Accurate: 1601 Persediaan Bahan Baku, 1602 Persediaan Bahan Kemas, 1603 Persediaan Bahan Penolong, 1605 Persediaan Produk Jadi.

| Jenis penyesuaian | Usulan akun lawan | Catatan |
|---|---|---|
| Pemakaian bahan untuk produksi | 1604 Persediaan Barang dalam Proses - Manufaktur, atau 5100 Harga Pokok Produksi | Pilihan ini bergantung pada zona WIP (K-2) dan pemilik HPP per batch (K-6); boleh dijawab "tunda" |
| Barang rusak atau kedaluwarsa | 5308 Biaya Barang Rusak | |
| Selisih stock opname (kurang atau lebih) | 5313 Laba/Rugi Selisih Persediaan | Sesudah validasi FAT (jawaban 3) |
| Sampel QC | 5309 Biaya Sample QC | |
| Selisih RM susut/hilang | 5313 Laba/Rugi Selisih Persediaan, atau 5104 Biaya Varian Produksi | Lihat [[ADR - 0201 Selisih RM Dicatat Dua Sisi lalu Masuk Satu Jalur Penyesuaian Stok]] |

Pengiriman hari ini tidak menyebut akun sama sekali, sehingga Accurate memakai bawaannya, Ekuitas Saldo Awal (lihat Context). Mengisi tabel ini menghentikan itu.

**C. Gudang tujuan.** Menurut IT (2026-10-23), stok pabrik di Accurate dicatat di **Gudang Utama**; Accurate memang tidak punya gudang bernama bahan baku (8 gudang: Utama, Sadewa, Shopee, Gentara, Iis, Sidareja, Rework, GA). Pengaturan gudang tujuan kiriman ERP (`ACCURATE_WMS_WAREHOUSE`) hari ini **kosong**. Yang ditanyakan: apakah semua penyesuaian pabrik, bahan maupun barang jadi, masuk Gudang Utama? Bila barang jadi punya gudang lain, sebutkan.

**D. Angka awal (pertanyaan 5).** Konfirmasi opname fisik penuh di hari peralihan, beserta tanggal peralihannya dan siapa dari FAT yang memvalidasi hasilnya.

### Jawaban lembar penyelesaian (2026-10-23, disampaikan lewat IT)

| Butir | Jawaban | Arti untuk keputusan |
|---|---|---|
| A | "Yang melakukan SO Senior Accounting" | Stock opname pabrik dilakukan dan divalidasi **Senior Accounting** (FAT). Apakah jawaban 19 Oktober atas nama Finance Supervisor tidak dijawab langsung |
| B | "Gunakan yang ada saat ini di Accurate" | Akun mengikuti praktik Finance di Accurate hari ini (tabel di bawah) |
| C | "Ya, stok masuk Gudang Utama" | Semua penyesuaian pabrik dikirim ke **Gudang Utama** |
| D | "Tanggal tidak menentu" | Angka awal tetap opname fisik penuh; **tanggal peralihan belum ditetapkan** |

**Akun yang dipakai Finance hari ini**, dibaca dari 45 dokumen Penyesuaian Persediaan manual terbaru di Accurate prod (2026-10-23, baca saja; total 2.338 dokumen):

| Jenis penyesuaian | Akun | Gudang |
|---|---|---|
| Sampel QC | 5309 Biaya Sample QC | Gudang Utama |
| Barang rusak / reject | 5308 Biaya Barang Rusak | Gudang Utama; reject dari gudang online ke Gudang Rework |
| Rework produk | 6120 Beban Rework Produk | Gudang Utama |
| Selisih stok (opname, pemindahan pengakuan stok) | 5313 Laba/Rugi Selisih Persediaan | Gudang Utama |
| Bahan penolong (bulanan) | 5307 Biaya Bahan Penolong | Gudang Utama |
| Perlengkapan pabrik (bulanan) | 5306 Biaya Perlengkapan Pabrik | Gudang Utama |
| **Pemakaian bahan untuk produksi** | **tidak ada contohnya** di dokumen yang dibaca | ditunda bersama K-2 (zona WIP) dan K-6 (HPP per batch) |

Penegasan diterima 2026-10-23: IT menegaskan jawaban ini sebagai jawaban Pemutus, dan status menjadi Diterima. Tanggal peralihan tidak menghalangi pekerjaan kode; ia diumumkan sebelum opname fisik dilakukan. Syarat Decision 6 tetap: pengiriman ke Accurate diperbaiki lebih dulu (bip-itteam-internal/bip-erp#3278).

## Deskripsi

*Stok pabrik (manufacture `stok_sekarang`) menjadi stok operasional yang hanya diubah lewat transaksi ERP dan penyesuaian tervalidasi; Accurate menerima Penyesuaian Persediaan otomatis dan tidak lagi menimpa angka ERP; selisih ERP vs Accurate dilaporkan, tidak ditimpakan.*

- **Status**: lihat blockquote di baris pertama dokumen ini
- **Keputusan papan**: K-1; membuka M-12 dan M-25 di [[ANALISA - Fondasi Manufaktur]]
- **Preseden**: [[ADR - 0175 Stok GA di ERP Jadi Stok Operasional, Barang Keluar dan Penyesuaian Dikirim ke Accurate]], [[ADR - 0015 Push Pergerakan WMS ke Accurate]]
- **Tanggal**: 2026-10-19

## Context

Diukur di kode `bip-erp` `origin/main` (a13cd40a, 2026-10-19). Rujukan baris bisa bergeser sesudah tanggal itu.

**Empat jalur menulis angka stok pabrik, dua di antaranya menimpa:**

| Jalur | Cara menulis | Kapan |
|---|---|---|
| Tarik dari Accurate (`jalankanSyncStokAccurate`, `services/manufacture/sync_hpp.go`) | **menimpa** dengan qty Accurate | otomatis tiap 6 jam untuk bahan (env `ACCURATE_STOK_AUTOSYNC`, bawaan menyala); tombol manual menimpa bahan dan barang jadi |
| Transaksi ERP (masuk, keluar, produksi, barang jadi, penerimaan pengajuan, koreksi) | menambah/mengurangi, atomik dengan ledger | setiap transaksi |
| Rekonsiliasi (`POST /stok/reconcile`) | **menimpa** dengan Σ ledger | manual |
| Penggabungan kode bahan/produk | menimpa saat kode digabung | manual |

Tidak ada penguncian atau versi: penulis "menimpa" yang terakhir menang, dan transaksi menumpuk di atas angka itu.

**Pengiriman ke Accurate** (`services/manufacture/accurate_push.go`): pergerakan ledger dikumpulkan per hari dan per arah menjadi dokumen Penyesuaian Persediaan, tiap 10 menit, hanya bila `ACCURATE_WMS_PUSH=true` (bawaan kode mati, `docker-compose.yml` mengisi `true`). Penjualan dan retur marketplace, penerimaan pemasok, kiriman produk, dan saldo pembuka **tidak** dikirim. Yang dikirim selisih pergerakan, bukan saldo.

**Akibat dua pemilik:** pengeluaran di ERP yang belum terkirim ke Accurate dikembalikan oleh tarikan berikutnya; penerimaan pemasok terhapus dari angka ERP sampai Finance membukukan fakturnya. Selama gudang belum mencatat di ERP (prod hari ini), efek ini tak terlihat; ia muncul begitu adopsi Fase 1 berjalan.

**Opname hari ini tidak pernah menjadi penyesuaian:** cycle count dan Bukti Selisih RM hanya menyimpan catatan dan persetujuan SPV; impor hasil SO menimpa saldo akhir bulanan tanpa langkah persetujuan; ketiganya tidak menyentuh stok maupun Accurate. Hanya koreksi lewat proposal yang mengubah ledger dan stok dengan persetujuan.

**Temuan saat mengukur (bukan bagian keputusan, perlu ditangani terpisah):**
- **Push kedua di hari dan arah yang sama menghapus baris yang sudah terkirim.** Push hanya mengelompokkan baris berstatus PENDING (`accurate_push.go`, `kelompokkanPush`), baris terkirim ditandai SENT, lalu integration-service menghapus **semua** baris lama dokumen hari itu dan menggantinya dengan baris baru (`services/integration/internal/usecase/accurate_wms_adjustment.go`). Akibatnya dokumen Penyesuaian Persediaan di Accurate hanya memuat kiriman terakhir hari itu. Besarnya dampak di prod belum diukur.
- Tanggal dokumen memakai tanggal pemindaian, bukan tanggal transaksi.
- Koreksi lewat proposal mengubah qty transaksi di tempat, sementara outbox hanya diisi sekali per transaksi; koreksi kemungkinan tidak ikut terkirim (dugaan, belum dibuktikan).
- Ketiga temuan di atas dilacak di bip-itteam-internal/bip-erp#3278.
- **Akun penyesuaian tidak dikirim.** Permintaan Penyesuaian Persediaan sengaja tidak memuat akun, sehingga Accurate memakai akun bawaannya: Ekuitas Saldo Awal, bukan akun beban (komentar di klien Accurate integration-service, terbukti pada satu dokumen Penyesuaian Persediaan prod Juli 2026). Gudang tujuan diambil dari env `ACCURATE_WMS_WAREHOUSE` yang bawaannya kosong, dan compose mencatat Accurate belum punya gudang bahan baku (pemetaan RM menunggu Finance). Per IT 2026-10-23, stok pabrik di Accurate dicatat di Gudang Utama (lihat Lembar penyelesaian C).
- **Status pengiriman tidak seragam di dokumentasi.** [[ADR - 0015 Push Pergerakan WMS ke Accurate]] masih menulis pengiriman MATI di prod, sementara compose menyalakannya sejak 18 Juli, dan komentar kode per 2026-08-09 mencatat pengiriman harian gagal karena format tanggal (kini ada normalisasi tanggal). Berapa dokumen yang benar-benar sampai ke Accurate diukur bersama #3278.

**Syarat Finance yang sudah tercatat** ([[Manufacture - Kajian Fondasi Sistem]] TBD 1): ERP mengikuti aturan pencatatan masuk/keluar (penjualan, retur, pembelian, pemakaian produksi); penyesuaian opname dibukukan setelah validasi Finance.

## Decision

*Diterima 2026-10-23. Butir 3 dan 4 diperjelas oleh jawaban lembar penyelesaian.*

1. **`stok_sekarang` pabrik = stok operasional.** Hanya berubah lewat transaksi ERP dan satu jalur penyesuaian bervalidasi (M-12). Tarik dari Accurate tidak lagi menimpa (otomatis dimatikan, tombol manual dicabut atau diubah menjadi laporan).
2. **Laporan selisih ERP vs Accurate** (baca saja) menggantikan penimpaan, dengan penanda jeda yang wajar (penerimaan yang fakturnya belum dibukukan).
3. **Penyesuaian Persediaan otomatis ke Accurate** untuk pergerakan yang tidak sampai lewat dokumen lain (pemakaian produksi, barang rusak/kedaluwarsa, selisih opname tervalidasi), dengan akun mengikuti praktik Finance di Accurate hari ini (tabel di Jawaban lembar penyelesaian) dan gudang **Gudang Utama**. Akun pemakaian produksi ditunda sampai K-2 dan K-6 diputuskan.
4. **Opname** dilakukan dan divalidasi **Senior Accounting**; tidak ada batas selisih, semua selisih divalidasi sebelum menjadi penyesuaian (jawaban pertanyaan 3).
5. **Rekonsiliasi Σ ledger** tetap ada sebagai alat periksa, bukan penimpa harian.
6. Pengiriman ke Accurate **diperbaiki lebih dulu** (temuan push kedua di hari sama) sebelum aturan ini berlaku, supaya Accurate tidak kehilangan baris.

## Consequences

**Yang didapat.** Angka stok yang dilihat PPIC dan gudang hanya bergerak karena kejadian nyata di gudang; selisih dengan Accurate terlihat sebagai daftar yang bisa ditelusuri, bukan menghilang diam-diam; satu pola dengan stok GA.

**Yang harus diterima.**
- Bila gudang lupa mencatat di ERP, angka ERP salah sampai opname berikutnya. Tidak ada lagi "pembetulan otomatis" dari Accurate, dan itu disengaja: pembetulan itu justru membatalkan catatan yang benar.
- Butuh opname fisik penuh di hari peralihan.
- Finance menerima dokumen Penyesuaian Persediaan dari ERP dan perlu menyediakan akun serta gudangnya.

## Alternatif yang ditolak

- **Accurate pemilik, ERP hanya menyalin.** Gudang harus mencatat di Accurate yang tidak dirancang untuk karantina, lot, dan rencana produksi; ERP lalu tak berguna untuk PPIC harian.
- **Biarkan dua pemilik, perpendek interval tarik.** Mempersempit jendela tumpang tindih tetapi tidak menghilangkannya; angka tetap bisa bergerak tanpa kejadian nyata.
- **Rekonsiliasi Σ ledger sebagai penimpa berkala.** Menimpa angka dengan hitungan dari ledger yang belum lengkap (penerimaan dan retur tak semuanya tercatat) sama berbahayanya dengan menimpa dari Accurate.
