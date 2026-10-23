**Status**: ✅ Kode kedua task **merged ke `main`** (T1 PR #3405 2026-10-21; T2 PR #3413, masuk `main` lewat PR #3427 2026-10-22), disinkronkan ke dok domain 2026-10-22. Sisa **bukan kode**: deploy prod, dua isian kv, dan verifikasi di Accurate (lihat § Sisa sesudah merge). Keputusannya [[ADR - 0195 Retur Sebagian Shopee Dibalik Retur Penjualan dan Komisi AMS Dompet Dibukukan ke Biaya Affiliate]] **🟢 Diterima 2026-10-21 oleh bagusizzanm**. Cara kerja dan akunnya di [[Finance - Pemetaan Komponen Marketplace ke Akun Accurate]] dan [[Microservices - Integration Service]]. Dok ini papan kerja, bukan arsitektur: coret item begitu PR-nya merge dan pindahkan keadaannya ke dok domain lewat `/sync-docs`.

**Pemutus:** @bagusizzanm · **Ukuran: Kecil** (satu repo `bip-erp`; dua issue sejajar, masing-masing satu PR, tanpa induk).

## Kebutuhan yang dijawab

Finance AR merekonsiliasi penerimaan Shopee dengan mutasi dompet dan menemukan dua selisih (sheet "CEK REKON" tab CEK, 2026-10-21): retur sebagian tercatat 2 pcs Rp184.000 padahal 1 pcs diretur (seharusnya 1 pcs Rp92.000), dan potongan komisi AMS yang hanya ada di mutasi dompet belum masuk ERP (−Rp1.136.138, 99 mutasi).

Permintaan itu diterima sebagai kebutuhan "pembukuan penerimaan Shopee cocok dengan mutasi dan akun klasifikasinya benar", bukan sebagai "tambah kolom". Pemeriksaan menunjukkan retur sebagian sudah dijawab keputusan pemilik 2026-08-05 yang belum pernah masuk kode, dan AMS hanya kekurangan satu case di klasifikasi mutasi dompet.

**Ukuran Kecil karena**: `erp-frontend` tidak memuat teks "Retur Sebagian" maupun pemetaan tipe dompet (git grep `origin/main`, 2026-10-21); rekap dirakit backend dan layar Config Accurate membaca katalog kv dari backend secara generik. Mobile tidak menyentuh penerimaan marketplace.

## Urutan deploy yang mengikat

- Backend saja. Tidak ada env baru, jadi `--force-recreate` tidak diperlukan; tidak ada kategori inbox baru.
- Dua kv tanggal baru diisi lewat layar Config Accurate sesudah deploy (isi = keputusan; tidak boleh mundur sebelum 2026-10-01).
- `integration-service` hanya di-recreate saat `worker_locks` kosong (jangan memotong putaran sinkron penerimaan).
- Prod dijalankan manusia (skill `deploy-bip-erp` §0). Setelah kv diisi, penerimaan Oktober yang sudah SENT ditulis ulang otomatis; beri tahu finance.

## Task

### ~~T1. Komisi AMS dompet Shopee dibukukan ke Biaya Affiliate (6113)~~ ✅ merged (PR #3405, issue #3397 tertutup)
- **Repo**: bip-erp · **Ukuran**: Kecil, 1 PR · **Urutan**: 1 (lebih kecil dan selisihnya terus bertambah)
- **Issue**: https://github.com/bip-itteam-internal/bip-erp/issues/3397
- **Isi**: kategori baru untuk `AMS_COMMISSION_FEE_DEDUCT`, satu baris per toko-hari ke kv `affiliate-commision`, rincian per pesanan di ekspor, kv tanggal `shopee-ams-wallet-cutover-date` (≥ 2026-10-01).
- **Verifikasi**: penerimaan 12 dan 13 Okt memuat 99 potongan (−Rp1.136.138); Beautyhack's Original Shop −Rp908.333 cocok sheet.

### ~~T2. Retur sebagian Shopee dibalik Retur Penjualan dan penerimaan melunasi qty sisa~~ ✅ merged (PR #3413 via #3427; ⚠️ issue #3398 masih terbuka karena #3413 masuk ke branch bukan `main`, tutup manual)
- **Repo**: bip-erp · **Ukuran**: Kecil (1 repo), 1 PR karena dua sisi wajib berubah serentak (ADR 0195 butir 4) · **Urutan**: 2
- **Issue**: https://github.com/bip-itteam-internal/bip-erp/issues/3398
- **Isi**: gerbang retur dilonggarkan untuk retur sebagian Shopee, base penerimaan dikurangi qty retur, refund identitas dari `seller_return_refund`, klasifikasi dibetulkan, kv `shopee-retur-sebagian-cutover-date` (≥ 2026-10-01).
- **Verifikasi**: `INC/2026/10/17/008-BH` memuat Bayar faktur Rp92.000 dan Biaya Admin sekitar Rp16.035, dengan Retur Penjualan Rp92.000 NOT_RETURNED.
- **Dependensi**: tidak bergantung pada T1.

### T3. Retur sebagian BERNILAI (refund bukan kelipatan harga), ADR 0195 butir 10
- **Repo**: bip-erp · **Ukuran**: M, 1 PR · ditemukan 2026-10-22 saat memeriksa order contoh: 5 dari 6 order Oktober berbentuk ini dan tidak terjangkau T2.
- **Issue**: https://github.com/bip-itteam-internal/bip-erp/issues/3450 · **PR**: #3451 (lolos judge dan gerbang, **belum merged**).
- **Isi**: penanda `ReturNilai`, refund identitas = `seller_return_refund`, klasifikasi "Retur Sebagian", tanpa Retur Penjualan, payout > 0 di kedua jalur, sapuan 31 hari.
- **Verifikasi**: lima order (`261012ED5EQT1Q`, `261001FKDBAKND`, `261002J0ETWP8S`, `261001F6MEWPCH`, `2609288HFWXW90`): Biaya Admin tanpa tumpukan residual (total lama Rp452.717), Potongan Penjualan 4003 membawa refund, faktur terlunasi, tidak ada Retur Penjualan baru.

## Sisa sesudah merge (manusia, belum terukur selesai)

1. Deploy `integration-service` saat `worker_locks` kosong (prod dijalankan manusia).
2. Isi kv `shopee-ams-wallet-cutover-date` dan `shopee-retur-sebagian-cutover-date` = `2026-10-01` di layar Config Accurate. **Retur sebagian sebelum 31 Okt**: sapuan hanya menjangkau release 14 hari terakhir dan order contoh `261010944296TR` cair 17 Okt.
3. Beri tahu finance: penerimaan Oktober SENT ditulis ulang otomatis; kas tidak bergeser.
4. Verifikasi di Accurate, bukan `docker ps`: `INC/2026/10/17/008-BH` (Bayar faktur 92.000, Biaya Admin ±16.035, Retur Penjualan 92.000 NOT_RETURNED) dan mutasi AMS 12–13 Okt di Biaya Affiliate (Beautyhack's Original Shop −908.333).
5. Celah yang diketahui (pengawas retur sekali-tembak, order escrow ≤ 0, hari AMS-saja tanpa order) dicatat di § Implementasi ADR 0195; belum ada issue.

## Yang masih terbuka dari analisa yang sama (bukan bagian ADR ini)

Tidak dibuatkan issue di sini; masing-masing perlu keputusan atau ukur lebih dulu dan tercatat di [[Microservices - Integration Service]]: enam faktur Shopee `INVOICE_PAID` dari kaskade FO 13 Okt (perbaikan manual finance, lalu Retry); `INC/2026/10/15/013-KY+GB` (selisih −125.409, penyebab per order belum ditelusuri); kapasitas putaran sinkron penerimaan (11 dari ±45 putaran terpotong); gerbang tutup buku faktur dan batas unggah FO ([[ADR - 0152 FO yang Dilaporkan Sesudah Uang Cair Mengecilkan atau Menghapus INC, FO Tidak Masuk Penjualan]]); pola refund residual untuk TikTok belum diukur.
