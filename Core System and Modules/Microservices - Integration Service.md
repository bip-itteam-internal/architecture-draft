# Microservices - Integration Service

## Deskripsi

*Integration Service adalah service integrasi marketplace e-commerce sekaligus bridge akuntansi. Service ini menghubungkan ERP ke marketplace Indonesia (TikTok Shop, TikTok Business/Ads, Shopee) dan middleware orkestrasi order (Desty), lalu menormalkan order dan laporan iklan menjadi model "transaction" terpadu. Tujuan akhirnya adalah bridging finansial ke Accurate Online: membuat invoice, menyusun ringkasan transaksi harian per-shop/channel, serta melakukan push Sales Invoice dan Sales Return ke Accurate. Selain itu service ini menangani webhook marketplace (via Desty), automasi auto-ship/auto-approve yang sadar-holiday, manajemen kredensial OAuth per marketplace, dan job sync terjadwal.*

- **Stack**: Go + Fiber v2 + MongoDB + Redis
- **Path**: `services/integration` (service terbesar)
- **Status**: ✅ Implemented (mostly) — masih ada bagian legacy yang di-disable dan target bridging non-Accurate belum tersedia
- **Referensi API**: dok endpoint lengkap (129 endpoint, 7 modul: Auth, TikTok, Shopee, Transactions, Webhooks, Workers, Accurate) → [docs-api-greget.vercel.app](https://docs-api-greget.vercel.app/) (Nextra). Dibangun vendor **Greget**, telah diserahterimakan ke BIP (maintenance kini internal).

## Endpoint / Fitur (Sudah Diimplementasikan)

### Webhooks
- `GET /webhooks/logs`, `GET /webhooks/logs/:id` — list & detail log webhook
- `POST /webhooks/logs/:id/retry` — retry pemrosesan webhook
- `GET /webhooks/tasks` — list task hasil webhook
- `GET /webhooks/accounts/desty` — daftar account Desty
- `POST /webhooks/services/desty` — ingest webhook Desty (auth `key` + `accessToken`, lalu enqueue ke queue)

### Credentials & Holidays
- `POST /credentials` — simpan/registrasi kredensial integrasi
- `POST /holidays`, `GET /holidays`, `DELETE /holidays/:id` — manajemen hari libur untuk automasi auto-ship/auto-approve yang sadar-holiday

### TikTok Business / Ads
- OAuth: `/tiktok/business/auth` (+ callback)
- Advertisers: list advertiser
- Integrated Reports: `/report/integrated`, report daily/ad (+ sync), list, summary
- GMV Max: performance & product (direct + sync), summary, campaigns/items
- **GMV Max Overview** (`GetGMVMaxOverview` → `/report/gmv_max/overview`, 2026-07) — agregasi Mongo `tt_business_gmv_max_performance_reports` group by `dimensions.item_group_id` (buang `item_id="0"`), join nama produk (`tt_business_store_products.title`) + nama toko (`tt_business_stores.store_name`). Metrik per produk: spend (Σcost), revenue (Σgross_revenue), orders (Σorders), cost/order, ROAS (rev/spend), **ROI = (rev−spend)/spend×100** (ad-level, exclude HPP). FE = dashboard **Product Performance** ([[APP - Web ERP]] modul marketing-insight). Rentang bebas (agregat, bukan raw report). **Fix 2026-07**: ROI awalnya `$avg(metrics.roi)` (rata-rata rasio per-row → nilai ngaco ~558%), diganti agregat dari total.
- **GMV Max Monitoring** (`ListGMVMaxCampaignMonitoring` → `/report/gmv_max/monitoring`) — agregasi per campaign untuk dashboard winner (ICC Finance: ROI≥3.2 & orders≥15). `item_id="-1"` = attribution bucket "no-creative" **terpisah** dari row per-item (bukan rollup — verified: rasio item/-1 acak lintas campaign), jadi Σ semua row = performa campaign sebenarnya. `item_group_id`=ID produk, `item_id`=level kreatif.
- Stores & Products
- **Cron master data** (`SyncMasterData`, setiap 00:00): sync campaigns + stores per advertiser. Sebelumnya kena rate limit TikTok (`40000: Request too frequent`) akibat burst concurrency (advertiser goroutine limit 5, campaign page limit 10). **Fix 2026-07-09**: tambah `getCampaignsWithRetry` (4 attempts, exponential backoff 5s→10s→20s + jitter ≤3s), turunkan concurrency advertiser 5→2 dan page 10→3. Campaigns wajib ada agar cron GMV Max 01:00 bisa berjalan (filter `store_id` dari campaigns).
- **`ListGMVMaxPerformanceReport`** — filter `advertiser_id` sebelumnya salah pakai field path `metrics.advertiser_id` (nested di sub-dokumen); **fix 2026-07-09** ke `advertiser_id` (field top-level di koleksi `tt_business_gmv_max_performance_reports`). Bug ini menyebabkan semua query performance per advertiser return 0 hasil di FE.
- `/sync/master-data` — sinkronisasi master data
- Accounts: CRUD

### Meta Ads

> 🟡 **Bagian ini KONSEP/RENCANA — belum ada kode.** Ditulis untuk grounding rencana implementasi client Meta Marketing API (pola ads/reporting seperti TikTok Business/Ads di atas, **bukan** pola order-sync Shopee/TikTok Shop). Update marker ke ✅ per sub-bagian begitu client Meta Ads nyata di-merge. Detail teknis di bawah bersumber dari dokumentasi publik Meta for Developers (`developers.facebook.com`) per Juli 2026 — **bukan dari kode BIP** — jadi wajib diverifikasi ulang sebelum implementasi (API vendor bisa berubah).

- **Kondisi saat ini**: `TIDAK ada client Meta Ads` di backend `services/integration`. Konsepnya sudah eksis di sisi lain: FE Finance/Incentive (`erp-frontend`) punya role `adv_meta`, `PLATFORMS = ["tiktok", "shopee", "meta"]`, setting "Meta Ads PPN (%)", dan Master Integration (mapping employee↔platform/campaign) — tapi semua **manual entry**, bukan API sync. [[Finance - Incentive]] §Arsitektur & Sumber Data eksplisit hanya menyebut `[[Sales - GMV Creative]]`/Dashboard TikTok sebagai sumber "Jumlah konversi" — Meta **tidak** disebut sebagai sumber otomatis sama sekali, konsisten dengan skema "ADV META DAN MARKETPLACE SHOPEE" di dokumen yang sama yang juga tidak punya jalur data otomatis.
- **Rencana App/Auth**: buat app tipe **Business** di Meta for Developers → hubungkan ke **Business Manager** Bharata → buat **System User** di Business Manager → assign ad account + permission (`ads_read` minimal, `ads_management` bila perlu tulis, `business_management` untuk kelola aset) → generate token System User (**tidak expired**, beda dari token user biasa yang cuma 60 hari). **App Review hanya perlu bila akses ad account di luar Business Manager Bharata sendiri** — untuk kebutuhan internal saat ini kemungkinan tidak perlu App Review sama sekali (lebih sederhana dari OAuth per-shop Shopee/TikTok). Detail langkah operasional: [[RUN - Onboarding Meta Ads]].
- **Kredensial**: rencana reuse entity generik `PlatformToken`/`Credential` yang sudah ada — komentar kode entity saat ini baru sebut "tiktokshop, shopee, lazada, ..." (belum sebut "meta" eksplisit, perlu ditambah saat implementasi) — **bukan** entity baru dari nol.
- **Data pull**: `GET /act_{ad_account_id}/insights` (fields `campaign_name`, `impressions`, `clicks`, `spend`, `actions`, `cost_per_action_type`) — pola mirip `/report/integrated` TikTok Business/Ads (laporan/reporting), **BUKAN** order sync. Tidak ada order/transaksi dari Meta, jadi **tidak** menyentuh `TransactionChannel`/`transaction_orders` sama sekali (beda dari Shopee/TikTok Shop/rencana Lazada sebelumnya).
- **Konsumen data**: `Microservices - Insentive Service` (skor KPI/konversi/CPA untuk skema insentif ADV Meta, lihat [[Finance - Incentive]]) — bukan model transaksi terpadu. Rekomendasi pola alur: Integration Service tarik data Insights dulu (satu pintu, konsisten pola TikTok GMV-Max) → baru dikonsumsi Insentif Service, alih-alih Insentif Service manggil Meta API langsung.
- **Rate limit**: mekanisme Meta berbasis tier akses (header `X-FB-Ads-Insights-Throttle`, `app_id_util_pct`/`acc_id_util_pct`), beda dari window-reset Shopee/Lazada. Tetap rekomendasikan pacing/circuit-breaker serupa pola ketahanan Shopee (lihat §Observability & Ketahanan Shopee di bawah) begitu jumlah ad account bertambah.
- **Open question (belum diputuskan)**: apakah data Insights Meta Ads perlu disimpan sebagai koleksi tersendiri di Integration Service (mirror `affiliate_orders`) sebelum dikonsumsi Insentif Service, atau cukup pass-through tanpa persist? Perlu keputusan eksplisit sebelum implementasi, bukan asumsi dokumen ini.

### TikTok Shop
- OAuth: `/auth` (+ callback), `/authorized-shops`
- **Model multi-account & multi-toko** — hierarki `1 open platform app → N credential → N authorized shop`:
  - **App tunggal**: `TIKTOK_SHOP_APP_KEY`/`TIKTOK_SHOP_APP_SECRET` dibaca dari env (`tiktok_usecase.go` ctor) — satu app TikTok Shop Open Platform dipakai semua akun. Konsekuensi: rate limit API dihitung per-app, makin banyak akun/toko makin cepat kena limit (analog kasus kuota Shopee di §Observability & Ketahanan Shopee).
  - **Credential per akun seller**: tiap otorisasi OAuth (`/auth/callback` → `ExchangeAccessToken`) membuat 1 dokumen `TiktokShopCredential` (`_id` UUID, name, access/refresh token + expiry, open_id) — 1 credential = 1 akun TikTok seller yang meng-authorize app.
  - **Shop per credential**: `GetAuthorizedShops` (API `/authorization/202309/shops`) mengembalikan array shops per credential; disimpan sebagai `TiktokShopAuthorizedShop` (id, name, region, cipher, `credential_id` sebagai link ke credential). Tiap call API per-toko memakai `shop_cipher` toko tsb.
  - **Cron multi-account otomatis**: task sync (orders, master data, affiliate) loop `ListCredentials` → per credential loop authorized shops — akun/toko baru cukup di-authorize via OAuth, tanpa perubahan kode/env.
- Orders: list/detail, direct, sync
- **Settlement per-order** (detail penyelesaian pembayaran): client `GetTransactionsByOrder` panggil TikTok **Finance API** `GET /finance/202501/orders/{order_id}/statement_transactions`. Ditarik saat sync order (`GetTransactionByOrderID` → fallback `GetTransactionsByOrder` bila belum ada), disimpan via `UpsertTransactionByOrder` ke entity `TiktokShopTransactionByOrder`, lalu ikut dikembalikan di response `/orders/detail` (field `transaction_orders`). Breakdown **per-SKU** mencakup semua komponen layar TikTok Shop: subtotal (`revenue_breakdown.subtotal_before_discount_amount` − `seller_discount_amount`), komisi platform (`fee.platform_commission_amount`/`referral_fee_amount`), ongkir (`shipping_cost_breakdown.*`), komisi afiliasi (`fee.affiliate_commission_amount` + partner/ads), komisi dinamis (co-funded/flash-sale/voucher-xtra fee), cashback bonus (`fee.bonus_cashback_service_fee_amount`), biaya pemrosesan (`fee.transaction_fee_amount`/`sfp_service_fee_amount`), dan `settlement_amount`. Transform `TransformToOrderIncome()` agregat ke `TransactionIncome` (revenue, service fee, shipping, discount, affiliate commission, settlement). **Catatan versi**: `202501` di-hardcode di client — verifikasi versi masih aktif sebelum diandalkan.
- GMV Winning Content: `GET /tiktok/shop/insight/gmv-winning-content` — daftar konten pemenang GMV (handle `ErrShopNotFound` → HTTP 400)
- Accounts: CRUD

### Affiliate (TikTok Seller)
- **Affiliate orders** — client `SearchSellerAffiliateOrders` panggil TikTok Affiliate Seller API `POST /affiliate_seller/202410/orders/search` (reuse `generateSign`/`buildQueryString`; versi **202410** terverifikasi live). Cron 8-jam tarik → koleksi `affiliate_orders` (grain order_id+sku_id, upsert idempotent), terpisah dari `transaction_orders` (link via order_id). Data per-SKU: creator_username, content_id/type, commission_model/rate, price, est/actual commission, settlement_status.
- **Dashboard API**: `GET /affiliate/orders` (list+filter+paginate, incl. `validation_status`) · `/affiliate/summary/{totals,creators,products,validation}` (agregasi Mongo untuk KPI + top creator/produk). FE: [[APP - Web ERP]] modul marketing-insight/affiliate. Detail keputusan: [[ADR - 0009 Affiliate via Search Seller Affiliate Orders API]].

### Shopee
- OAuth: `/auth` (+ callback)
- Orders: list, v2 list, detail, sync
- Shops
- Products / Items
- GMS Analytics: item & campaign performance (+ sync + summary)
- Accounts: CRUD

### KiriminAja

> 🟡 **Bagian ini KONSEP/RENCANA — belum ada kode.** Ditulis untuk grounding rencana integrasi. **Beda kategori** dari section platform lain di atas: KiriminAja **bukan** channel order (seperti Shopee/TikTok Shop) atau ads (seperti TikTok Business/Meta Ads) — ini API agregator **shipping/logistics** (rate check, booking AWB, tracking, cetak label, webhook, pickup, COD), dipakai dari sisi Bharata untuk operasional pengiriman, bukan sumber data penjualan. Detail teknis di bawah bersumber dari dokumentasi publik KiriminAja Mitra API (`developer.kiriminaja.com`) per Juli 2026 — **bukan dari kode BIP** — jadi wajib diverifikasi ulang sebelum implementasi (API vendor bisa berubah). Cakupan fitur dikonfirmasi tim marketing (2026-07-05).

- **Kondisi saat ini**: `TIDAK ada client KiriminAja` di kode — 0 referensi di seluruh `bip-erp`. Satu-satunya jejak historis ada di sistem Finance **lama** (Java, di luar lingkup dokumen ini) yang mencatat KiriminAja sebagai channel "Non-Marketplace" via Excel upload manual (kolom `Ekspedisi, Service, AWB, COD, Biaya COD, Pencairan COD, Ongkir` — bukan format order/produk seperti Shopee/TikTok/Lazada).
- **Rencana Auth**: Bearer token API key. Registrasi via email `tech@kiriminaja.com` → proses partnership/approval → sandbox key (`https://tdev.kiriminaja.com`) via Sandbox Dashboard → UAT → transisi ke API key produksi (`https://client.kiriminaja.com`). Header: `Authorization: Bearer {api_key}`. Detail langkah operasional: [[RUN - Onboarding KiriminAja]].
- **Catatan implementasi khusus**: KiriminAja punya **Go SDK resmi** (`github.com/kiriminaja/go`) — beda dari Shopee/TikTok/Meta Ads yang semua pakai client custom tulisan BIP sendiri. Rekomendasi: evaluasi pakai SDK resmi ini langsung di `services/integration`, bukan tulis ulang HTTP client dari nol seperti pola platform lain.
- **Cakupan fitur** (dikonfirmasi tim marketing, semua jadi fitur utama — bukan sekunder):
  - **Create Shipment** — booking pengiriman, generate AWB (nomor resi)
  - **Cek Ongkir** — rate check lintas 15+ kurir (JNE, J&T, SiCepat, TIKI, Pos Indonesia, dll)
  - **Tracking** — pelacakan status pengiriman real-time
  - **Cetak Label** — cetak label pengiriman (bila tersedia di API)
  - **Webhook** — pembaruan status pengiriman otomatis (bila tersedia; alternatif: polling)
  - **Pickup Scheduling** — jadwal penjemputan kurir
  - **Payment / COD Management** — proses pembayaran COD & non-COD, rekonsiliasi pencairan dana COD di level API KiriminAja (data mentah); pencatatan **akuntansi** COD ke Accurate tetap ranah Finance — di luar lingkup dokumen ini
- **Sumber order — open question (belum diputuskan)**: fitur "Create Shipment" butuh detail order (alamat, berat, nilai barang, status COD/non-COD) sebagai input. Order marketplace di `transaction_orders` (Shopee/TikTok) **biasanya sudah** punya logistik built-in dari platform masing-masing. KiriminAja historisnya untuk channel **"Order Online"** (non-marketplace) — tapi **channel ini tidak punya entitas order sama sekali di `bip-erp`** (0 hasil pencarian "Order Online"/"order_online"). Perlu keputusan eksplisit: (a) bikin entitas order baru untuk "Order Online" dulu, atau (b) scope KiriminAja generik dulu sebagai utility (cek ongkir/booking/tracking dipanggil dari mana saja tanpa order-source built-in) — **bukan diasumsikan oleh dokumen ini**.
- **Webhook**: rencana endpoint native baru `POST /webhooks/services/kiriminaja` (pola sama seperti `/webhooks/services/shopee`/`/tiktok`), processor baru di registry `(platform, source)` — pola identik `shopee_push.go`/`tiktok_direct.go`.
- **Model data**: berbeda dari platform lain — KiriminAja **bukan sumber** `TransactionChannel` baru (tidak menambah entry ke `transaction_orders` sebagai channel order), melainkan **konsumen** yang membaca detail order yang sudah ada (dari channel manapun yang diputuskan di atas) untuk keperluan booking pengiriman + menulis balik status tracking.

### Transactions (model terpadu)
- `/transactions/orders/list`, summary (+ shops / + products), `/transactions/orders/:id`
- Master: `/master/shops`, `/master/channels`, `/master/status`
- Summary Reports: list, `POST` trigger, group-by-status, get, items, **invoices** (`/summary/reports/:id/invoices`), retry, delete
- `POST /summary/reports/:id/send/:service` — kirim ringkasan ke Accurate
- **Income reporting**: agregasi income invoice + field income pada transaction order (laporan pemasukan)
- **Demography Insight**: `GET /transactions/insight/demography` — insight demografi dari transaksi
- **Status history**: pelacakan riwayat status (status history) transaction order
- **Revenue Comparison**: `GET /transactions/orders/summary/comparison` — perbandingan performa dua periode kustom. Query param: `start_date`/`end_date` (periode aktif, YYYY-MM-DD, default hari ini), `comparison_start`/`comparison_end` (periode pembanding, default kemarin), `channel` (SHOPEE|TIKTOK, **opsional** — omit untuk semua channel), `shop_id`, `timezone` (IANA, default `Asia/Jakarta`). Granularity otomatis: `hourly` (rentang 1 hari → 24 slot label `HH:00`) atau `daily` (multi-hari → 1 slot per hari label `DD/MM`). Respons: `current`, `previous` (masing-masing `total_revenue`, `total_orders` TO_SHIP; `total_completed_revenue`, `total_completed_orders`, `total_products` COMPLETED; + array `slots`), `comparison` (% perubahan ke-5 metrik), `granularity`. Dua query MongoDB dijalankan **concurrent** via `errgroup` (TO_SHIP + COMPLETED).
- **Dashboard Status Summary**: `GET /transactions/orders/dashboard/summary` — jumlah order aktif saat ini **tanpa filter tanggal** (semua order di DB), dikelompokkan per kategori kartu dashboard. Param: `channel`, `shop_id` (opsional). Respons: `pesanan_baru` (TO_PROCESS), `siap_dikirim` (TO_SHIP), `belum_di_proses` (TO_PROCESS + TO_SHIP), `pesanan_selesai` (COMPLETED).

### Accurate
- Shop Settings: CRUD (`/accurate/settings/shops`)
- **Product Management**: CRUD `/accurate/products` + validasi item (mapping produk Accurate)
- **Bank Account**: CRUD `/accurate/bank-accounts`
- **KV Config** (key-value): CRUD `/accurate/settings/kv-configs`

### ICC Account Mapping (marketing leader)

> Auth: `RequireMarketingLeader` = kyura/beauty_hacks SPV · insentive `adv_leader` · integration SPV/admin. Grounded ke `internal/interface/http/icc_mapping_handler.go`. Lihat [[Sales - ICC Account Manager Mapping]].

- `GET /icc/mappings` — daftar mapping aktif (filter: `employee_id`, `tiktok_shop_id`, `tiktok_advertiser_id`, `is_active`; default `true`)
- `POST /icc/mappings` — buat mapping; enrich shop/advertiser name dari `tt_shop_authorized_shops` & `tt_business_advertisers`; unique constraint active per shop & advertiser (409 jika duplikat)
- `PATCH /icc/mappings/:id` — update `is_active` / `notes`
- `DELETE /icc/mappings/:id` — hapus (hanya jika `is_active=false`; else 409)
- `GET /icc/mappings/available-shops` — toko belum di-assign (untuk dropdown form)
- `GET /icc/mappings/available-advertisers` — advertiser belum di-assign (untuk dropdown form); pipeline `$unwind → $group by advertiser_id` untuk deduplikasi (advertiser yang muncul di beberapa dokumen `tt_business_advertisers` dideduplikasi di sini)

Koleksi `icc_account_mappings`. Index: partial unique `(tiktok_shop_id, is_active=true)` + `(tiktok_advertiser_id, is_active=true)` + compound `(employee_id, is_active)`.

> ⚠️ **Gap**: semua route `/icc/mappings` dilindungi `RequireMarketingLeader` — staff ICC (position=icc) tidak bisa mengakses data mapping milik sendiri. Perlu route `/icc/mappings/me` dengan middleware terpisah di Phase 3. Lihat [[Sales - ICC Account Manager Mapping]].

### Marketing Team & Shop ACL (admin only)
- `/marketing/teams` — CRUD tim marketing (gated `RequireIntegrationAdmin` = supervisor/admin module integration)
- Anggota tim: assign/unassign member (`/marketing/teams/:id/members`)
- **Shop ACL**: assign/unassign toko ke tim (`/marketing/teams/:id/shops`) — kontrol akses toko per tim marketing

### Items / Master Catalog
- CRUD lengkap: `/items/list`, `/items/sku/:sku`, history, create, bulk, bundle, variations, patch, delete

### Workers / Jobs
- `/jobs/status`, `POST /jobs/:name/trigger`, status/history/config/enable/disable
- `GET /health`

### Background Workers (cron)
- **Sync TikTok Shop orders** — **4× sehari** 00:00/08:00/16:00/23:00 WIB (`0 0 0,8,16,23 * * *`); window 9 jam overlap. *Re-enabled 2026-07-09 dengan jadwal diperbarui — sebelumnya 1× di 01:00 dan sempat disabled sejak Jun 2026.*
- TikTok Business master-data — harian 00:00
- GMV-Max report (historis) — harian 01:00
- **GMV-Max report today** (intraday) — **4× sehari** 00:00/08:00/16:00/23:00
- Integration report — harian 02:00
- Video performance TikTok Shop — 02:30
- **Affiliate orders sync** — 4× sehari (`0,8,16,23`), loop credential→authorized-shop, error isolated per-shop
- **Affiliate status refresh** — mingguan (Minggu 02:00): re-pull window 89 hari agar `settlement_status` + `actual_commission` lama ter-update
- **Affiliate commission validation** — harian 04:00: cross-check komisi SETTLED vs finance statement lokal (`tt_shop_transaction_by_orders`), stempel `validation_status`. Nol call TikTok API
- **Income reconciler TikTok** — tiap jam **:30** (digeser dari :00 — hindari pileup quota TikTok dengan gmv-max/affiliate-sync/escrow). Batch 600 order/run, limiter 5 req/s + circuit breaker 36009002 (5 fail beruntun → abort run). Klasifikasi hasil refetch: `fetched` (settlement masuk) / `not_available` (belum cair, re-scan tanpa bakar attempt; min-age 3 hari) / `pending` (error teknis, attempt++ cap 10). Ringkasan tiap run disimpan ke koleksi `reconciler_run_stats` → dipakai endpoint `settlement/sync-status` untuk baris info FE settlement
- **Shopee escrow reconciler** — tiap jam :00
- Webhook-consumer — tiap 5 detik
- **Desty credential refresh** — 00:00 (cek expiry buffer 5 hari, singleflight)
- **Shopee credential refresh** — 05:05 (proaktif sebelum expiry 06:00)
- Sync Shopee performance — 02:00
- Redis queue digunakan untuk task summary-report
- Optimasi concurrency: global semaphore + sequential processing untuk mitigasi rate limit API marketplace
- **Notifikasi kegagalan**: semua worker kirim Telegram otomatis via `WithOnJobError` hook manager level (setelah semua retry habis) — 18 job ter-cover tanpa konfigurasi per-task
- ⚠️ **Jadwal task = DB source of truth**: schedule di-SEED sekali ke Mongo `workers.worker_configs` saat registrasi pertama; setelahnya **nilai DB yang berlaku** — mengubah `Schedule()` di kode TIDAK berpengaruh sampai dokumen `worker_configs` di-update manual (`db.worker_configs.updateOne({_id:"<job>"},{$set:{schedule:"..."}})`; efektif live tanpa restart). Boot log WARN bila schedule DB ≠ kode. Pause task sementara: tanam lock di `workers.worker_locks` (`_id: lock:<job>`, `expires_at` = auto-lepas). Insiden 4 Jul 2026: jadwal income-reconciler diubah di kode tapi prod tetap pakai config lama. Detail: `services/integration/internal/worker/README.md`
- **One-off CLI recovery** (`cmd/backfill`, `cmd/settledfeed`; dry-run default, idempotent, `--apply` untuk tulis ke DB): `backfill` = migrasi field `income_status` doc lama + re-insert order raw-only (order_date dari `create_time` asli — summary group by order_date); `settledfeed` = feed order affiliate SETTLED → by-order finance fetch (interleave per-shop, adaptive backoff 36009002 cool-down 5/10/15s, newest-first). Dipakai recovery Jul 2026: coverage finance affiliate-SETTLED 15,7% → 100% (~78rb order, ~26 jam)

### Gross Profit per Product (modul profit)

> ⚠️ Bagian ini ada di **working branch `feat/gross-profit` (sudah di-push ke origin) yang BELUM di-merge/deploy**. Ubah marker ke ✅ setelah merge. Deploy note: drop index unik lama `sku_1_tiktok_item_id_1_product_name_1` di `product_sku_mappings` (index baru menambah `master_sku`). Spec: `bip-erp` sibling `docs/superpowers/specs/2026-07-03-gross-profit-submodule-design.md`.

Rumus per produk/SKU (TikTok) — **"Laba Sejati"** (blueprint dashboard marketing):
`GMV − biaya marketplace (breakdown) − promo = NET SETTLEMENT`, lalu `NET SETTLEMENT − HPP − iklan = LABA KONTRIBUSI` (retur = kolom informasi).

- **Sumber komponen**: settlement per-SKU dari `tt_shop_transaction_by_orders` (GMV `subtotal_before_discount`, promo `seller_discount`, fee breakdown komisi/affiliate/proses/ongkir, retur refund, `settlement_amount`; identitas kolom eksak, residual di `other`) — join `sku_id→seller_sku` via `tt_shop_orders.line_items` (per-order → kamus global → fallback); qty & bucket bulanan dari `transaction_orders`; iklan = GMV Max `metrics.cost` per `dimensions.item_group_id` (= ID produk; `item_id` = level kreatif — verified) dengan split prorata revenue untuk listing multi-claim; HPP = `product_costs` per BULAN order (`effective_from` bulanan, bucket `%Y-%m` WIB).
- **Estimasi order belum settle**: rate komponen/GMV agregat per bulan dari data settled → komponen order pending diestimasi; `estimated_share` dilaporkan per baris & agregat (transparansi, terganti otomatis saat settlement masuk).
- **Mode cair** (`?mode=settled`, default FE): bucket sales diganti angka settlement actual (`SettledOnlySales` — revenue=GMV settled, qty=qty settled, bucket belum cair dibuang) → seluruh breakdown murni actual tanpa estimasi; iklan diprorata porsi cair per SKU (`applySettledAdsScale`) karena spend harian tak mengenal status settle. Mode default (tanpa param) = semua order.
- **Dibayar Pembeli** (`buyer_paid`): `total_payment` order (uang dibayar buyer = setelah diskon + ongkir, SEBELUM potongan komisi TikTok) diprorata ke SKU dengan share `items.total` — konsisten cara fee di-split. = kolom "Order Amount" export Semua Pesanan TikTok (verified match). Bucket settlement-only (order yatim) tanpa total_payment → buyer_paid 0.
- **Klasifikasi Komisi**: `fee_commission` = platform + referral + **dynamic commission + flash-sale + voucher-xtra** (dynamic terverifikasi prod > platform commission, Jun 2026: 313jt vs 226jt — sebelumnya nyangkut di residual Proses); `fee_affiliate` = organik + partner + **affiliate ADS commission**; `fee_process` = residual: cashback program + biaya infrastruktur tetap (`vn_fix_infrastructure_fee`) + mall service fee + pajak/lainnya (porsi fluktuatif antar periode). **Pecahan informasi** dibawa breakdown & tampil di kartu KPI, kolom tabel (grup − BIAYA MARKETPLACE), dan sub-baris waterfall panel: `fee_comm_dynamic` (komisi dinamis; dasar = commission − dynamic) + `fee_proc_cashback/infra/mall` (lainnya = process − 3) — semua subset, ikut Add/Scale/estimasi/projection.
- **Arus dana** (`GET /profit/cash-flow`): kartu **Sudah Cair** (Σ `income.total_settlement_amount` order `income_status=fetched` — actual) vs **Uang Gantung** (COMPLETED belum settle — estimasi `GMV × rate_toko`, shrinkage `(net+global×K)/(gmv+K)` K=100jt, window belajar order settled 21/45 hari terdekat; backtest Apr+Mei total ±3,0%, per-toko 4–6%) + rincian toko×bulan + `accuracy_30d` (track-record rumus dihitung on-the-fly). Granularitas repo per (toko, hari WIB) — `AggregateCashFlowDaily`. Kartu Sudah Cair juga menghitung **order yatim** (settlement tercatat tapi order tak pernah masuk pipeline — 9.625 order drift order-list historis; `AggregateOrphanSettledDaily` anti-join) supaya konsisten dengan tabel; tooling pemulihan: `cmd/orphanbackfill` (tarik detail by-ID batch 50, dry-run default).
- **Bundle**: SKU multi-komponen dialokasikan ke produk komponen dengan rasio nilai HPP (revenue/fee/net di-share; HPP exact per komponen; qty = qty_bundle × qty_per_unit); daftar `bundles` terpisah di response sebagai view informasi (overlap dengan products, jangan dijumlah).
- **Koleksi baru (integration_db)**: `product_costs` (HPP per produk, riwayat per `effective_from`, `source: upload|accurate` — siap sync Accurate fase berikut) + `product_sku_mappings` (kunci unik `(sku, tiktok_item_id, product_name)`; 1 SKU boleh multi-baris: multi-toko per item_id & bundle per komponen dengan `qty_per_unit`; HPP dihitung sekali per komponen distinct).
- **Arsitektur hitung**: aggregate on-read (pipeline Mongo + fungsi murni `AssembleProductProfit` di usecase, unit-tested) — tanpa ETL/snapshot baru.
- **Identitas produk = SKU master** (mis. `PJB-002`): HPP, roll-up produk, dan dedup komponen di-join per `master_sku`; NAMA hanya alias/tampilan (case-insensitive, boleh berubah antar upload — yang tampil nama dari HPP terbaru). Baris mapping per product listing: `master_sku` sama = alias (HPP sekali), beda = komponen bundle. Terminologi: **Product Listing** = teks SKU penjual di order; **SKU** = SKU master.
- **Input HPP**: upload xlsx finance — format baru `SKU | Produk | HPP/Pcs` (header by-nama, posisi bebas) ATAU format lama 2 kolom (SKU di-resolve dari nama sekali saat upload; sisanya legacy by-nama). Baris berawalan CONTOH dilewati. Plus **CRUD satuan manual** dari UI (`POST/PUT/DELETE /profit/costs[/:id]`, `source: manual`). Authz upload/mapping/CRUD: `supervisor|admin` modul `integration` ATAU `finance`; lainnya view-only.
- **Seed mapping 2 fase**: fase 1 dari master `items` (komponen bundle + qty); fase 2 match SKU liar (tak terdaftar master) ke nama HPP finance via normalisasi/token (auto kalau kandidat tunggal, `suggestions` kalau ganda — indikasi bundle).
- **Transparansi data bolong**: response bawa `pending_income_items` (order COMPLETED belum settle), `unmapped_skus`, flag `missing_hpp` — tidak ada angka diam-diam.
- **Filter**: all / per account (credential TikTok Shop → resolve authorized shops) / per toko (`shop_id`) / per produk / per SKU (iklan level SKU = prorata share revenue, granularitas asli GMV Max per item_id).
- Konsumen: [[APP - Web ERP]] halaman `/integration/gross-profit`. Rute lengkap: [[API - Integration Service]].

### Observability & Ketahanan Shopee

> ⚠️ Bagian ini ada di **working branch yang BELUM di-merge/deploy** (prod masih menjalankan kode lama). Didokumentasikan agar tidak hilang; ubah marker ke ✅ setelah merge.

- **Notifikasi success-rate API Shopee per-run** — setiap cron `Sync Shopee performance` (02:00) **dan** endpoint sync manual (`/shopee/orders/sync`, `/shopee/gms/*/sync`) mengirim ringkasan **success-rate per-endpoint + overall** via Telegram di akhir tiap run. Penghitung **in-memory per-run** (dibawa di `context`) — tanpa DB, tanpa payload/PII. Tujuan: visibilitas success-rate tanpa bergantung dashboard Shopee yang delay.
- **Ketahanan refresh & sync Shopee** (akar masalah restriction rate-limit Shopee, lihat [[LOG - Shopee API Rate Limit Request]]): distributed lock refresh-token per-shop (Redis) cegah race antar-instance + **circuit breaker** yang menghentikan run begitu Shopee balas `error_limit` (cegah death-spiral kuota) + retry simpan credential + timeout independen per-shop + observability (kegagalan GMS tidak lagi senyap).
- **Webhook order ingest — TikTok vs Shopee** (jalur "direct"/push, registry `(platform, source) → processor`): keduanya kini menarik order detail dari API platform, tapi beda strategi. **TikTok direct** (`TiktokDirectProcessor`) **selalu** tarik order detail dari API TikTok tiap webhook (bisa buat order baru). **Shopee push** (`ShopeePushProcessor`, code 3) kini **create-on-missing**: order yang sudah ada → update status saja (0 call API); order baru → tarik order detail dari Shopee (buat order). Sebelumnya Shopee-push hanya update-status & **error** bila order belum ada. Langkah menuju "lepas dari [[External - Desty]]" untuk Shopee.
- **Rate-limit gate Shopee** (proses-wide, in-memory): begitu ada call Shopee balas `error_limit`, gate menyala sampai **00:00 UTC+8** (reset kuota Shopee). Webhook order-fetch cek gate **sebelum** call — bila menyala, **skip + defer** (retry setelah reset) agar tidak menambah call gagal saat kuota habis. Push code ≠ 3 / tanpa `order_sn` → di-acknowledge tanpa error.

## Belum Diimplementasikan / Catatan

- **Target kirim selain Accurate** mengembalikan `501` ("service integration not implemented yet"); enum service yang tersedia baru `ACCURATE`.
- Route direct-push Accurate (`/transactions/summary/create|send|status`) handler-nya sudah **LENGKAP**, tetapi route-nya **DI-COMMENT** — digantikan alur summary-report `/send/:service`.
- Route webhook Desty langsung (`/webhook/desty`, `/webhooks/desty`) **di-comment** — digantikan `/webhooks/services/desty`.
- CronManager lama **fully disabled** — fungsinya dipindah ke worker framework.
- **Lazada** hanya disebut di kode cron yang sudah disabled — **TIDAK ada client Lazada** (placeholder/partial).
- **Meta Ads** — **TIDAK ada client Meta Ads** di backend; konsepnya baru eksis sebagai role/setting manual di FE Finance/Incentive. Rencana integrasi: lihat §Meta Ads di atas.
- **KiriminAja** — **TIDAK ada client KiriminAja** sama sekali; 0 referensi di kode. Rencana integrasi (shipping/logistics API): lihat §KiriminAja di atas.
- TODO kecil: indexing `time.Time`.

## Dependencies & Integrasi

- [[CORE - API Master Gateway]] — entry point / routing ke service
- [[External - Accurate]] — bridging finansial (Accurate Online, HMAC-signed): Sales Invoice / Sales Return
- [[Microservices - Insentive Service]] — konsumen data iklan (laporan TikTok/Shopee, + Meta Ads rencana)
- [[Microservices - TikTok Shop Service]] — webhook landing
- [[DB - Overview and Notes]] — MongoDB & Redis (queue prefix `srv:integration`)

External lain: TikTok Shop, TikTok Business/Ads, Shopee, [[External - Desty]] (middleware order), Telegram (notifier error/job).

## Dokumen Terkait

- [[External - Desty]] — vendor middleware orkestrasi order (webhook + auto-approve)
- [[RUN - Onboarding Meta Ads]] — langkah operasional pembuatan akun/app Meta Ads (rencana)
- [[RUN - Onboarding KiriminAja]] — langkah operasional partnership & API key KiriminAja (rencana)
- [[Finance - Incentive]] — konsumen data konversi/CPA Meta Ads untuk skema insentif ADV Meta
- [[Sales - Marketplace Integration]] (konsep sisi marketing)
- [[Finance - Bridging App]]
- [[Sales - GMV Creative]]
- [[Vendor - CRM]]
- [Referensi API — docs-api-greget](https://docs-api-greget.vercel.app/) — REST API lengkap (129 endpoint, Nextra)
- [[IT - Background Jobs & Schedulers]] — 9 cron + webhook dispatcher service ini (sync TikTok/Shopee/Desty; konsumsi webhook tiap 5 dtk)
