# Marketing Analytics — Audit Ketersediaan Data Prototipe Direktur

## Deskripsi

*Pemeriksaan satu per satu: dari seluruh metrik di prototipe "Bharata Command Center" yang diberikan Direktur, mana yang datanya sudah ada di `marketing-analytics`, mana yang ada tapi nyaris kosong, dan mana yang memang tidak ada. Tujuannya supaya keputusan "kejar sumber datanya" atau "coret" diambil dari fakta, bukan dari dugaan.*

- **Stack**: Go + Fiber v2 (service `marketing-analytics`), MongoDB (koleksi `mart_*`)
- **Path di repo**: `bip-erp/services/marketing-analytics/`
- **Status**: ⚠️ Implemented (ada catatan) — **13 dari 13 halaman prototipe sudah punya endpoint**, tetapi cakupan per-metrik timpang: lapisan laba Bharata lengkap, lapisan metrik platform (Ads Manager & Seller Center) tipis sampai kosong.
- **Tanggal audit**: 2026-08-09
- **Sumber prototipe**: `Marketing_Analytics_Lengkap_Bharata.html` (dari Direktur, 13 halaman + 10 penambahan)

## Cara membaca label

Empat label, bukan tiga. Label keempat ditambahkan karena "ada" saja menyembunyikan beda yang menentukan biaya: antara data yang tinggal ditampilkan dan data yang masih harus dihitung.

| Label | Arti | Yang dibutuhkan |
|---|---|---|
| **ADA** | Field tersimpan dan terisi | Tinggal ditampilkan |
| **RAKIT** | Bahannya ada, angkanya belum dihitung | Pekerjaan kode, bukan pekerjaan data |
| **TIPIS** | Field ada, cakupan datanya rendah | Perbaikan ingest/API, bukan fitur |
| **TIDAK ADA** | Tak ada field maupun sumbernya | Sumber data baru, atau dicoret |

## Temuan utama

**Terbalik dari dugaan biasa.** Yang membuat prototipe itu berharga justru bagian yang paling lengkap di service: settlement, retur, HPP, laba, fee marketplace, harga floor, repeat rate, wilayah, kurir, penanggung jawab (ICC). Itu persis kolom yang di prototipe ditandai "tidak ada di dashboard platform mana pun". Yang tipis justru bagian yang **disalin dari dashboard platform**.

**Lapisan metrik iklan cakupannya rendah, dan itu tertulis di kodenya sendiri** (`metrik_iklan.go:141-172`):

| Kelompok field | Cakupan |
|---|---|
| `impressions`, `spend`, `clicks` | **18 sampai 77%** |
| `conversion`, `conversion_rate`, `cost_per_conversion`, `onsite_shopping_roas` | **0,3 sampai 1%** |

Konsekuensinya bukan "belum dibangun", melainkan "kalau dibangun pun kolomnya kosong". Kolom **CVR, CPA, GMV platform, dan ROAS platform** di halaman Kampanye dan Iklan berdiri di lapisan 0,3 sampai 1% itu. **Funnel di Ringkasan SPV** (Impresi → View 2s → Klik → Order → GMV) berdiri di lapisan 18 sampai 77%, sehingga tiap tahapnya mencacah populasi yang berbeda: corongnya akan terlihat rapi dan menyesatkan.

**Baris mart profit tidak memuat cacah order maupun qty** (`entity.go:324-357` hanya berisi kolom uang). Satu ketiadaan ini sekaligus mematikan **AOV**, **klik→order**, **CPA**, dan **cancel per toko**. Ia juga menjelaskan kenapa `cpa_maks` di `/ambang` tersimpan tapi tak pernah dibaca siapa pun: tak ada penyebut untuk menghitungnya.

## Peta halaman

Ketiga belas halaman prototipe seluruhnya sudah punya endpoint.

| Halaman prototipe | Endpoint |
|---|---|
| Ringkasan SPV | `GET /beranda` + `GET /summary` |
| Profit per Toko | `GET /profit/shops` |
| Profit per Kampanye | `GET /profit/campaigns` |
| Profit per Iklan | `GET /profit/ads` |
| Profit per Video | `GET /videos` |
| Live Shopping | `GET /lives` |
| Affiliate | `GET /affiliate` |
| Bedah Retur | `GET /returns/breakdown` + `GET /returns/detail` |
| Harga & Diskon | `GET /price-floor` |
| Matriks SKU × Toko | `GET /matrix/sku-shop` |
| Pelanggan & CRM | `GET /cohort` |
| Audiens & Wilayah | `GET /audience` |
| Kamus Metrik | frontend, tanpa endpoint |

Service kita punya lebih dari prototipe: `/profit/products`, `/profit/items`, drill `/profit/orders` dan `/videos/orders`, `/ambang`, `/kpi/kinerja-toko`.

## 1 · Ringkasan SPV

| Metrik prototipe | Label | Keterangan |
|---|---|---|
| Spend MTD | ADA | `ads_cost` |
| Pagu / anggaran | TIDAK ADA | Tak ada konsep anggaran di service ini |
| GMV platform | TIPIS | `total_onsite_on_web_cart_value`, ikut cakupan 18–77% |
| GMV settlement | RAKIT | `net_settlement` ada per baris, belum dijumlah ke kartu vonis |
| ⭐ Laba after-ads | ADA | `gross_profit`, sudah jadi angka utama halaman depan |
| ROAS settlement | RAKIT | `net_settlement` ÷ `ads_cost` |
| ROAS platform | TIPIS | `onsite_shopping_roas`, cakupan 0,3–1% |
| Video menang (7d) | RAKIT | `/videos` punya views/completion/GMV; ambang "menang" belum didefinisikan |
| Funnel 7 tahap | TIPIS | Tiga tahap teratas dari lapisan 18–77%; tahap Order tak ada di mart profit |
| Rantai keputusan (navigasi) | ADA | Seluruh route level sudah ada, tinggal ditampilkan di halaman depan |

## 2 · Profit per Toko

| Metrik prototipe | Label | Keterangan |
|---|---|---|
| Pengunjung (visitors) | TIDAK ADA | Nol kemunculan di seluruh service |
| Impresi produk · Klik produk · CTR | TIDAK ADA | Ada di `/videos` & `/lives`, tidak di level toko |
| Order · Klik→Order | TIDAK ADA | Baris mart profit tak memuat cacah order |
| Buyer baru % | TIPIS | `/summary` punya Pembeli & Pembeli berulang, **hanya Shopee**; `user_id` TikTok belum disalin ke `transaction_orders` |
| AOV | TIDAK ADA | Butuh cacah order di mart |
| GMV | ADA | `revenue`, dengan catatan penting di bawah |
| Cancel % | TIPIS | `/summary` mencacah order dibatalkan secara global, belum per toko |
| Retur % | ADA | `retur` + `/returns/breakdown` |
| Fee platform % | ADA | `fee_marketplace` |
| Iklan alokasi | ADA | `ads_cost` |
| ⭐ Laba after-ads | ADA | `gross_profit` |
| ROAS settlement | RAKIT | |

> **Catatan `revenue`**: isinya `income.total_original_price`, yaitu **harga list sebelum diskon kita sendiri** (`sumber_agregasi.go:746`). Terverifikasi 100,0% atas 20.000 order produksi di dua channel. Karena itu ROAS dan "iklan % revenue" yang berdiri di atasnya optimistis. `gross_profit` tidak terpengaruh, karena ia turun dari settlement. Rincian di [[Microservices - Marketing Analytics Service]] dan [[DB - Data Dictionary]].

## 3 · Profit per Kampanye

| Metrik prototipe | Label | Keterangan |
|---|---|---|
| Spend | ADA | |
| Impresi · Klik · CTR · CPC | TIPIS | Cakupan 18–77%; CTR sudah dalam persen 0–100 |
| CPM | RAKIT | Turunan spend ÷ impresi, ikut tipis |
| Frequency | TIDAK ADA | Butuh `reach`, tidak ada |
| Konversi · CVR · CPA | TIPIS | Cakupan **0,3–1%** |
| GMV platform · ROAS platform | TIPIS | Cakupan **0,3–1%** |
| GMV settlement | ADA | |
| Retur % | ADA | |
| ROAS settlement | RAKIT | |
| Laba | ADA | |
| vs ROAS-minimal | ADA | `/ambang` (roas_min) + `/price-floor` (`target_npm_pct`) |
| Penanda kampanye tanpa kode SKU | ADA | `belum_termapping` |

> Batas platform yang sudah dinyatakan service: **Lazada tidak melayani level kampanye**; **Shopee punya barisnya tapi tanpa nama kampanye**, sehingga tampil ber-id (`handler_mart.go:1004`).

## 4 · Profit per Iklan

| Metrik prototipe | Label | Keterangan |
|---|---|---|
| Spend · Impresi · Klik · CTR | TIPIS | |
| View 2s · View 6s | ADA | `video_watched_2s`, `video_watched_6s` |
| Completion 25–100% | TIDAK ADA | `completion_rate` ada di `/videos`, tidak di level iklan |
| Avg watch time | ADA, terbatas | `average_video_play` **nil di level agregat, sengaja**: penyebutnya tidak dikirim API sehingga tak bisa dirata-rata (`metrik_iklan.go:160-166`) |
| Konversi · CPA · GMV platform | TIPIS | |
| GMV settlement · Laba | ADA | |
| Tren 7 hari | RAKIT | Mart berdimensi hari, tinggal dirangkai |

> **Lazada tidak melayani level iklan** sama sekali.

## 5 · Profit per Video

| Metrik prototipe | Label | Keterangan |
|---|---|---|
| Views · Completion | ADA | |
| Avg watch | ADA | `avg_watch_sec`, satuan **detik** bukan persen seperti prototipe |
| Like · Komentar · Share · Simpan | TIDAK ADA | Like/komentar/share ada di `/lives`, tidak di `/videos`; "simpan" tak ada di mana pun |
| Impresi produk · Klik produk | ADA | |
| CTR produk · GMV/1000 views | RAKIT | |
| Order · GMV | ADA | |
| Kreator | ADA | `creator_username` |
| Sumber (organik/boost/ads) | ADA | `sumber` + `ada_sumber_lain` |
| Spend per video | ADA | `spend_vsa` + `spend_gmv_max` |
| ⭐ Laba per video | TIDAK ADA | `/videos` membawa GMV dan spend, **tidak** `net_settlement`/`hpp`. Drill `/videos/orders` cakupannya **affiliate-saja** |
| Hook (Before-After, POV, Testimoni) | TIDAK ADA | Tak ada field klasifikasi kreatif |
| Keputusan (menang/boost/fatigue/stop) | TIDAK ADA | Butuh definisi ambang lebih dulu |

## 6 · Live Shopping

| Metrik prototipe | Label | Keterangan |
|---|---|---|
| Viewers · Avg watch · Klik produk · Order · GMV | ADA | |
| Durasi · GMV/jam · Rev/1000 viewers | RAKIT | `start_time`/`end_time` ada |
| **Peak concurrent** | TIDAK ADA | **Sengaja**: endpoint list `shop_lives` tidak menyediakannya (`entity.go:34`) |
| Host | ADA | `username` |
| Studio | TIDAK ADA | Data operasional, bukan data platform |
| Laba per sesi | TIDAK ADA | Sebab sama dengan video |
| Heatmap jam × hari | RAKIT | `start_time` + GMV sudah ada |

Bonus di service yang tak ada di prototipe: `items_sold`, `customers`, `new_followers`.

## 7 · Affiliate

| Metrik prototipe | Label | Keterangan |
|---|---|---|
| Kreator · Order · GMV · Komisi · Retur | ADA | Komisi tersedia aktual maupun estimasi |
| Komisi % | RAKIT | |
| Sample dikirim · Konten tayang · Views kreator | TIDAK ADA | Data operasional program affiliate |
| GMV / sample | TIDAK ADA | Ikut ketiadaan sample |
| Laba bersih | TIDAK ADA | Sebab sama dengan video |
| Kepemilikan kreator (ICC) | ADA | Melebihi prototipe |

## 8 · Bedah Retur

| Metrik prototipe | Label | Keterangan |
|---|---|---|
| Rasio retur · Nilai retur | ADA | |
| Alasan retur | ADA | Superset `cancel_reason` → `buyer_cancel_reason` → `return.reason` |
| Kurir | ADA | |
| Wilayah | ADA, tapi di `/audience` | |
| **Kurir × wilayah** | TIDAK ADA | Dua dimensi hidup di dua pipeline berbeda; `returns_detail.go` tak membawa province |
| **Kategori QC A–E** | **DITOLAK SENGAJA** | `returns_breakdown.go:23` menolaknya eksplisit demi menghindari kategori karangan |
| Akar teridentifikasi (lot, batch, segel) | TIDAK ADA | |
| Biaya sejati per retur | TIDAK ADA | Ongkir balik, handling, barang tak layak jual: tak satu pun ada |
| Program penurunan retur (PIC, due, status) | TIDAK ADA | Ranah task management, bukan analytics |
| Drill ke order + nama toko + ICC | ADA | Melebihi prototipe |

## 9 · Harga & Diskon

| Metrik prototipe | Label | Keterangan |
|---|---|---|
| Harga minimal target NPM | ADA | `floor_price` + `target_npm_pct`, append-only & effective-dated |
| Harga rata-rata aktual | TIDAK ADA | Butuh cacah qty di mart |
| Gap aktual vs floor | TIDAK ADA | Ikut di atas |
| **Diskon per kampanye** | TIDAK ADA | Lihat catatan di bawah |

> **Ini tuas terbesar yang belum punya kolom di mana pun.** Pengukuran atas data produksi menunjukkan jarak antara revenue dan settlement **didominasi diskon penjual kita sendiri (32%)**, bukan fee marketplace (12,7%). Diskon TikTok 31,0% berbanding Shopee 7,2%. Mart belum menyimpan `total_original_price` dan `total_discount` terpisah, sehingga besaran yang paling menentukan laba marketing tidak dapat ditampilkan maupun dipantau.

## 10 · Matriks SKU × Toko

**Halaman paling utuh.** Baris produk, kolom toko, sel per metrik yang bisa dipilih, total per baris dan per kolom, ICC per toko, penanda `belum_termapping`, dan sel absen sebagai gap listing. Seluruhnya ADA.

## 11 · Pelanggan & CRM

| Metrik prototipe | Label | Keterangan |
|---|---|---|
| Pembeli · Repeat 60/90 hari | ADA | `window_days` dapat diatur |
| AOV pembelian ulang | TIDAK ADA | |
| Verdict CRM | TIDAK ADA | Keputusan, bukan data |

> Identitas pembeli **hanya Shopee**. `user_id` TikTok ada di koleksi mentah `tt_shop_orders` tapi belum disalin ke `transaction_orders`, dan Lazada tak mendokumentasikan buyer id yang stabil lintas order. Cohort TikTok karena itu belum dapat dihitung.

## 12 · Audiens & Wilayah

| Metrik prototipe | Label | Keterangan |
|---|---|---|
| GMV per wilayah | ADA | Dikelompokkan dari `buyer.province` |
| Retur per wilayah | ADA | |
| Umur · Gender · Placement | TIDAK ADA | Breakdown Ads API belum ditarik |

## 13 · Sepuluh penambahan di prototipe

| Penambahan | Label | Keterangan |
|---|---|---|
| Tren 7 hari (sparkline) | RAKIT | Mart berdimensi hari |
| Step response ROAS inkremental | TIDAK ADA | Butuh riwayat perubahan budget, tak ada |
| Stok & cover hari | TIDAK ADA | Di luar modul, lihat [[Microservices - Inventory Service]] |
| Traffic source per toko | TIDAK ADA | |
| Aging settlement per toko | RAKIT sebagian | `net_settlement` + flag kematangan ada; umur hari belum dihitung |
| Heatmap jam × hari live | RAKIT | |

## Keputusan yang diminta

Diurut dari yang paling murah dan paling luas dampaknya.

1. **Tambahkan cacah order (dan qty) ke mart profit.** Satu field membuka **AOV, klik→order, CPA, dan cancel per toko** sekaligus, dan menghidupkan `cpa_maks` yang sekarang tersimpan tapi tak terbaca. Paling murah, dampak terluas.

2. **Pisahkan `total_original_price` dan `total_discount` di mart.** Ini menyelesaikan dua hal sekaligus: kata "Revenue" berhenti bermakna ganda, dan diskon sebagai tuas laba terbesar akhirnya punya kolom.

3. **Nasib lapisan metrik iklan.** Perbaiki ingest supaya cakupan naik, atau terima halaman Kampanye dan Iklan tanpa kolom platform dan funnel tanpa tiga tahap teratas. Ini menentukan nasib dua halaman penuh, jadi perlu diputuskan sadar, bukan didiamkan.

4. **Kategori QC A–E**: tetap ditolak, atau dibuatkan pemetaan resmi dari alasan mentah platform ke lima kategori itu.

5. **Metrik yang sumbernya di luar modul ini**: stok (Inventory), sample & konten affiliate (operasional), pagu belanja (RAPB), studio live (operasional). Perlu keputusan dikejar atau dicoret, bukan dibiarkan menggantung.

## Dokumen Terkait

[[Microservices - Marketing Analytics Service]] · [[API - Marketing Analytics Service]] · [[APP - Web ERP]] · [[DB - Data Dictionary]] · [[Sales - Marketing Dashboard (Index)]] · [[ADR - 0008 Profit Engine Join via item_group_id]] · [[Microservices - Inventory Service]]
