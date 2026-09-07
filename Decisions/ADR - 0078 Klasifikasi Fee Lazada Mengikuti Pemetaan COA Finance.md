# ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance

## Untuk Manajemen

- **Yang berubah di layar**: rincian potongan pada halaman Laba Kotor untuk kanal Lazada. Sebelumnya enam baris bernama istilah Lazada (Komisi, Biaya Pembayaran, Komisi Affiliate, Biaya Pengiriman, Voucher & Diskon Penjual, Pendapatan Lain); kini lima baris yang **namanya sama dengan akun pembukuan** — Biaya Admin, Potongan Afiliasi, Beban Ongkir, Potongan & Promosi, Pendapatan Lain. Angka totalnya tidak berubah; yang berubah adalah pengelompokannya.
- **Siapa terdampak**: finance (yang membukukan) dan siapa pun yang membaca laba kotor Lazada. Tidak ada perubahan pada order, pengiriman, atau data pelanggan.
- **Tidak dijanjikan**: angka **historis tidak berubah dengan sendirinya**. Order Lazada yang sudah tersimpan memakai pengelompokan lama sampai proses penarikan ulang menyentuhnya. Bila laporan bulan lalu harus ikut berubah, itu pekerjaan terpisah yang belum dikerjakan.
- **Besaran kerja**: satu hari, tiga berkas kode inti plus penyesuaian tampilan.

## Deskripsi

*Aturan pengelompokan biaya Lazada sebelumnya hidup sebagai tiga salinan kode yang sudah menyimpang satu sama lain, dan tak satu pun bersandar pada pemetaan akun yang dipakai finance. Keputusan ini menyatukannya jadi satu fungsi dan menjadikan sheet pemetaan COA dari finance sebagai sumber aturannya.*

- **Status**: ⚠️ **Implemented (ada catatan)** — bip-erp PR #1755, erp-frontend PR #1470, keduanya **belum deploy**. Catatan: data lama belum di-backfill; dua nama fee di sheet belum pernah muncul di prod.
- **Path di repo**: `bip-erp/services/integration/internal/domain/entity/lazada_fee_kategori.go` (sumber aturan) · `lazada_income.go` · `internal/interface/http/lazada_settlement.go` · `erp-frontend/src/features/integration/gross-profit/lib/breakdown-config.ts`
- **Tanggal**: 2026-09-07

## Context

Klasifikasi fee Lazada hidup sebagai **tiga salinan** `switch strings.Contains` — di `TransformToOrderIncome`, `AggregateLazadaFinanceToSKUSettlement`, dan `buildLazadaSettlement`. Ketiganya membawa komentar yang menyatakan mereka identik, padahal **sudah menyimpang**: cabang `item price` dijaga `amt > 0` di dua tempat, tidak di tempat ketiga. Satu fakta di tiga tempat, salah satunya sudah bergeser diam-diam — kelas kerusakan yang dicatat berulang di ingatan tim.

Yang lebih menentukan: ketiganya mengelompokkan fee ke ember generik lintas-marketplace (`FeeCommission`, `FeeProcess`, `FeeShipping`, `Promo`) yang **tidak sama** dengan akun COA yang benar-benar dipakai finance membukukannya. Tidak ada satu pun titik di kode yang menyatakan fee Lazada mana masuk akun mana; pengetahuan itu hanya ada di kepala orang finance dan di sebuah spreadsheet.

Pengukuran ke prod 2026-09-07 (`integration_db.lazada_finance_lines`, 3.667 baris / 466 order) menemukan **19 nama fee berbeda** — jauh lebih banyak dari tiga nama yang selama ini muncul di test, dan beberapa di antaranya tak pernah terbayang saat aturan lama ditulis (empat jenis fee koreksi, dua pasang fee yang saling meniadakan).

## Decision

Satu fungsi `KlasifikasiFeeLazada(feeName, transactionType, amt)` menjadi **sumber kebenaran tunggal**; ketiga pemanggil mendelegasikan kepadanya. Aturannya mengikuti sheet pemetaan COA dari finance:

| COA | Isi |
|---|---|
| **6112** Beban Admin E-Commerce | komisi, biaya transaksi, order processing, SPA, Lazada Funded Commission, penyesuaian komisi **debit maupun kredit** |
| **6113** Potongan Afiliasi E-Commerce | biaya afiliasi bersponsor |
| **6114** Beban Ongkir E-Commerce | Free Shipping Max |
| **4003** Potongan Penjualan | diskon, LazCoins, price cut, co-fund (kedua sisi), dan seluruh **biaya promosi** (voucher, Flexi-Combo, promosi LazKoin) |
| pendapatan lain | klaim barang hilang ("seperti uang masuk biasa") |

Fee yang belum dikenal **sengaja jatuh ke 6112**, bukan diabaikan, supaya identitas settlement tidak bocor diam-diam saat Lazada menambah jenis fee tanpa pemberitahuan.

### Urutan pemeriksaan adalah bagian dari keputusan

Tiga hal hanya benar karena urutannya, dan membaliknya menghasilkan angka yang salah tanpa satu pun galat:

1. **Kata "promotion" diperiksa sebelum "discount".** `LazCoins Discount Promotion Fee` (−Rp1.368.578, fee promosi terbesar) memuat LazCoins, Discount, **dan** Promotion sekaligus.
2. **Penyesuaian (`correction`) diperiksa sebelum aturan tanda.** `Commission fee refund - correction for overcharge` bertanda **positif** (+Rp13.518) tapi tetap 6112 — ia mengurangi beban komisi, bukan pendapatan baru.
3. **Affiliate diperiksa sebelum commission.** `Affiliate Commission Fee` memuat kata "commission" dan akan salah jatuh ke 6112.

## Consequences

**Angka per akun (data prod 2026-09-07):** 6112 −Rp5.128.270 · 6113 −Rp292.015 · 6114 −Rp2.235.549 · 4003 −Rp1.961.016 · pendapatan lain +Rp253.775 · GMV +Rp41.633.780.

**Yang membaik.** Co-fund kini berada di akun yang **sama** dengan potongannya, sehingga pasangan `Price Cut Discount` (−401.500) / `Co-fund Price Cut` (+401.500) dan `Promotional Charges Vouchers` (−147.000) / `Co-fund Voucher` (+147.000) saling meniadakan di tempat yang benar. Sebelumnya kedua sisi bisa mendarat di akun berbeda dan menggelembungkan keduanya — beban yang tak pernah ditanggung, diimbangi pendapatan yang tak pernah diterima.

**Yang menjadi utang.**

- **Data lama tidak ikut berubah.** Order Lazada yang sudah tersimpan memakai pemetaan lama sampai `lazada-income-reconciler` menyentuhnya ulang. Backfill belum dikerjakan.
- **Dua fee di sheet belum pernah muncul di prod** — `Lazada Voucher Max Fees` dan `Payment fee atas barang hilang/rusak`. Sudah ditangani di kode, belum teruji data nyata.
- **Menyimpang dari pola lintas-marketplace.** Shopee dan TikTok tetap memakai pembagian ember generik. Lazada kini satu-satunya kanal yang klasifikasinya bersandar langsung pada COA. Itu disengaja — sheet finance hanya ada untuk Lazada — tapi berarti kanal lain **tidak** boleh dianggap mengikuti aturan ini.
- **Sheet finance kini jadi sumber yang tidak versioned.** Aturannya sudah disalin ke doc-comment `KlasifikasiFeeLazada` beserta alasan tiap urutan, jadi kode tetap bisa dibaca sendiri; tapi bila sheet berubah, tak ada yang otomatis memberi tahu.

**Yang menahan.** Test memakai **19 nama fee sesungguhnya dari prod**, bukan karangan — termasuk nama berspasi di ujung (`Seller Virtual Credit - Co-fund Voucher `) yang akan lolos dari perbandingan persis. Identitas balance per-order dan per-SKU dipertahankan dan tetap diuji. Kontrol negatif dijalankan: membalik urutan promosi/diskon membuat test merah pada assertion yang diklaimnya.

## Dokumen Terkait

- [[Microservices - Integration Service]] — implementasi Lazada
- [[APP - Web ERP]] — halaman Laba Kotor
- [[ADR - 0065 Payout yang Sudah Dibukukan Dokumen Lain Ditutup, Bukan Dibuat Ulang]] — keputusan Lazada lain di jalur pembukuan
