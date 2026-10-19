> **Status**: 🟡 **Diusulkan**, 2026-10-19. Menunggu keputusan **Finance Supervisor** (keputusan K-1 di [[ANALISA - Fondasi Manufaktur]]). **Belum ada kode baru**; yang ditulis di sini usulan beserta pertanyaan yang harus dijawab Pemutus.

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
| 2 | Bahan dari pemasok sampai ke Accurate lewat apa | Faktur Pembelian (seperti sekarang) / Penyesuaian dari ERP saat diterima | **Faktur Pembelian** tetap, agar tak tercatat dua kali. Konsekuensinya ada jeda: ERP naik saat diterima gudang, Accurate naik saat faktur dibukukan. Laporan selisih menandai jeda itu, bukan menganggapnya salah |
| 3 | Urutan validasi stock opname | (a) gudang hitung, SPV Manufacture setuju, Finance validasi, baru dibukukan; (b) tanpa SPV; (c) lainnya | **(a)**. Batas selisih yang boleh dibukukan tanpa validasi Finance: perlu angka dari Pemutus (atau tidak ada batas) |
| 4 | Akun dan gudang Accurate untuk Penyesuaian Persediaan pabrik (pemakaian produksi, rusak/kedaluwarsa, selisih opname) | ditetapkan Finance | Perlu daftar dari Finance. Paket pengiriman tidak dikerjakan sebelum ini tertulis, sama seperti GA |
| 5 | Angka awal saat beralih | opname fisik penuh di hari H / angka Accurate hari H | **Opname fisik penuh**, karena kajian mencatat stok fisik dan Accurate sudah berbeda (tab Mutasi + SO di spreadsheet PPIC) |

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

**Syarat Finance yang sudah tercatat** ([[Manufacture - Kajian Fondasi Sistem]] TBD 1): ERP mengikuti aturan pencatatan masuk/keluar (penjualan, retur, pembelian, pemakaian produksi); penyesuaian opname dibukukan setelah validasi Finance.

## Decision

*Usulan; berlaku sesudah status di baris pertama menjadi Diterima.*

1. **`stok_sekarang` pabrik = stok operasional.** Hanya berubah lewat transaksi ERP dan satu jalur penyesuaian bervalidasi (M-12). Tarik dari Accurate tidak lagi menimpa (otomatis dimatikan, tombol manual dicabut atau diubah menjadi laporan).
2. **Laporan selisih ERP vs Accurate** (baca saja) menggantikan penimpaan, dengan penanda jeda yang wajar (penerimaan yang fakturnya belum dibukukan).
3. **Penyesuaian Persediaan otomatis ke Accurate** untuk pergerakan yang tidak sampai lewat dokumen lain (pemakaian produksi, barang rusak/kedaluwarsa, selisih opname tervalidasi), dengan akun dan gudang dari Finance (pertanyaan 4).
4. **Opname** mengikuti urutan validasi yang dijawab Pemutus (pertanyaan 3) dan baru menjadi penyesuaian sesudah divalidasi Finance.
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
