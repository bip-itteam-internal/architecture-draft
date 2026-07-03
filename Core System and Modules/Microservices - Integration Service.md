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
- `POST /webhooks/services/shopee` — ingest **Shopee Push Mechanism** (publik via gateway `/ext/webhook/shopee`). Auth **HMAC-SHA256** atas string `URL|body` lewat header `Authorization`; key dipilih per query `app_type` (`ads`/`order`/`marketing`/`one`/`affiliate` → `SHOPEE_ADS_WEBHOOK_KEY` / `SHOPEE_ORDER_WEBHOOK_KEY` / `SHOPEE_MARKETING_WEBHOOK_KEY` / `SHOPEE_ONE_WEBHOOK_KEY` / `SHOPEE_AFFILIATE_WEBHOOK_KEY`). ⚠️ Verifikasi signature **sementara di-bypass** — mismatch hanya di-log lalu tetap 200 (workaround bug Shopee console saat simpan key baru; `webhook_usecase.go`). Payload disimpan ke `webhook_logs` lalu diproses async oleh `ShopeePushProcessor` (create-on-missing — lihat *Observability & Ketahanan Shopee* di bawah).
- `POST /webhooks/services/tiktok` — ingest webhook **TikTok direct/push** (`TiktokDirectProcessor` — selalu tarik order detail dari TikTok, bisa buat order baru)

### Credentials & Holidays
- `POST /credentials` — simpan/registrasi kredensial integrasi
- `POST /holidays`, `GET /holidays`, `DELETE /holidays/:id` — manajemen hari libur untuk automasi auto-ship/auto-approve yang sadar-holiday

### TikTok Business / Ads
- OAuth: `/tiktok/business/auth` (+ callback)
- Advertisers: list advertiser
- Integrated Reports: `/report/integrated`, report daily/ad (+ sync), list, summary
- GMV Max: performance & product (direct + sync), summary, campaigns/items
- **GMV Max Monitoring**: `GET /tiktok/business/report/gmv_max/monitoring` — ranking performa per-campaign (GMV/ROI/orders/cost) lintas account & shop untuk dashboard marketing-insight, dengan flag **GMV winner** = ROI ≥ 3.2 & order ≥ 15 (aturan khusus ICC 2026 di [[Finance - Incentive]]; ambang `roi_threshold`/`min_orders` bisa di-override). Agregasi **menjumlahkan semua baris report** per campaign — termasuk bucket atribusi `item_id="-1"` yang **terpisah** (bukan rollup dari baris per-creative), sehingga total ROI realistis (~4) bukan menyesatkan (~42 bila pakai `-1` saja). Grounded: `tiktok_business_handler.go` (`ListGMVMaxMonitoring`), `usecase/gmv_max_monitoring.go`, `entity.GMVMaxCampaignMonitoringItem.ComputeDerived`. ⚠️ Baru — sudah di kode (unit test + tervalidasi data prod), **belum deploy**.
- **ICC Video Metrics**: `GET /tiktok/business/insight/icc-video-metrics` — metrik per-video untuk insentif **ICC** (`ctr`, `watch25`, `roas`, `orders`, `post_date`, `creator`): agregasi GMV Max ad-creative + join `tt_business_campaign_items` (video↔creator) + join `tt_shop_video_performances` (post_date). Dikonsumsi service insentif via HTTP untuk `EvaluateICCVideoIncentive`/`IsICCVideoEligible` (lihat [[Finance - Incentive]]). Grounded: `tiktok_business_handler.go` (`ListICCVideoMetrics`), `entity.ICCVideoMetric.ComputeDerived`. ⚠️ Baru — di kode + tervalidasi prod (1.138 video), **belum deploy**; per-video ROAS diketahui kurang andal (atribusi biaya ke bucket campaign).
- Stores & Products
- `/sync/master-data` — sinkronisasi master data
- Accounts: CRUD (`/accounts/list`, `/accounts/:id`) — kredensial TikTok Business punya field **`brand`** (mis. KYURA/BEAUTYHACKS): di-set saat update akun (`POST /accounts/:id`) & dikembalikan di `/accounts/list`. Dipakai form integrasi insentif untuk mengelompokkan akun (Brand → Account → Advertiser). Grounded: `tiktok_business_handler.go` (UpdateCredential/GetAllCredential), `entity.TiktokBusinessCredential.Brand`. ⚠️ Sudah di kode, **belum deploy** ke prod; backfill `brand` akun lama belum dilakukan.

### TikTok Shop
- OAuth: `/auth` (+ callback), `/authorized-shops`
- Orders: list/detail, direct, sync
- GMV Winning Content: `GET /tiktok/shop/insight/gmv-winning-content` — daftar konten pemenang GMV (handle `ErrShopNotFound` → HTTP 400)
- **Shop Video Performance (persist)**: worker harian `sync-tt-shop-video-performance` (02:30) mem-persist performa video shop ke koleksi **`tt_shop_video_performances`** (video_id, creator, **post_date** dari `PublishTime`, views) — sumber **tanggal upload** (eligibility ICC 7–30 hari) & **hitung produksi video/creator/bulan**. Endpoint `GET /tiktok/shop/insight/creator-video-count?month=YYYY-MM`. Grounded: `usecase/icc_shop_video.go` (`SyncShopVideoPerformance`/`GetCreatorVideoCount`), `worker/tasks/tt_shop_video_performance_task.go`. ⚠️ Baru, **belum deploy** (koleksi terisi setelah worker jalan live; alignment `video_id` shop↔business dikonfirmasi pada sync pertama).
- Accounts: CRUD

### Shopee
- OAuth: `/auth` (+ callback) — per `account_type` (**ADS_SERVICE** / **ERP_SYSTEM** / **AMS**), lihat *Dual/Tri-app* di bawah
- **Affiliate (AMS)**: `GET /shopee/affiliate/performance` (per-affiliate) + `/shopee/affiliate/recommended` — via app AMS, lihat *AMS affiliate* di *Observability & Ketahanan Shopee*
- Orders: list, v2 list, detail, **sync (chunked ≤15 hari, mendukung histori ~3 bulan)**, **escrow backfill** (`/orders/escrow/backfill`) — lihat *Manual order sync histori panjang* di *Observability & Ketahanan Shopee*
- Shops
- Products / Items
- GMS Analytics: item & campaign performance (+ sync + summary)
- Accounts: CRUD

### Transactions (model terpadu)
- `/transactions/orders/list`, summary (+ shops / + products), `/transactions/orders/:id`
- Master: `/master/shops`, `/master/channels`, `/master/status`
- Summary Reports: list, `POST` trigger, group-by-status, get, items, **invoices** (`/summary/reports/:id/invoices`), retry, delete
- `POST /summary/reports/:id/send/:service` — kirim ringkasan ke Accurate
- **Income reporting**: agregasi income invoice + field income pada transaction order (laporan pemasukan)
- **Demography Insight**: `GET /transactions/insight/demography` — insight demografi dari transaksi
- **Status history**: pelacakan riwayat status (status history) transaction order
- **Revenue Comparison**: `GET /transactions/orders/summary/comparison` — perbandingan omset hari ini vs kemarin: total `total_revenue` (status `TO_SHIP`) per channel, + breakdown 24 slot per-jam untuk line chart. Aggregasi berdasarkan `order_update_date` (bukan `order_date`) karena TO_SHIP di-set saat order diupdate. Query param: `channel` (SHOPEE|TIKTOK, wajib), `shop_id` (opsional), `timezone` (IANA, default `Asia/Jakarta`).

### Accurate
- Shop Settings: CRUD (`/accurate/settings/shops`)
- **Product Management**: CRUD `/accurate/products` + validasi item (mapping produk Accurate)
- **Bank Account**: CRUD `/accurate/bank-accounts`
- **KV Config** (key-value): CRUD `/accurate/settings/kv-configs`

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
- Sync TikTok Shop orders — 1 AM
- TikTok Business master-data
- GMV-Max report — 1 AM
- Integration report — 2 AM
- Webhook-consumer — tiap 5 detik
- Desty-credential refresh — tengah malam
- Sync Shopee performance — 2 AM
- Redis queue digunakan untuk task summary-report
- Optimasi concurrency: global semaphore + sequential processing untuk mitigasi rate limit API marketplace

### Observability & Ketahanan Shopee ✅

> ✅ **Implemented** — sudah merge & **live di prod**.

- **Notifikasi success-rate API Shopee per-run** — setiap cron `Sync Shopee performance` (02:00) **dan** endpoint sync manual (`/shopee/orders/sync`, `/shopee/gms/*/sync`) mengirim ringkasan **success-rate per-endpoint + overall** via Telegram di akhir tiap run. Penghitung **in-memory per-run** (dibawa di `context`) — tanpa DB, tanpa payload/PII. Tujuan: visibilitas success-rate tanpa bergantung dashboard Shopee yang delay.
- **Ketahanan refresh & sync Shopee** (akar masalah restriction rate-limit Shopee, lihat [[LOG - Shopee API Rate Limit Request]]): distributed lock refresh-token per-shop (Redis) cegah race antar-instance + **circuit breaker** yang menghentikan run begitu Shopee balas rate-limit (`error_limit`, `error_too_many_request`, atau `ads_rate_limit_shop_api` — throttle per-shop pada endpoint ads/GMS) (cegah death-spiral kuota) + retry simpan credential + timeout independen per-shop + observability (kegagalan GMS di level *usecase* di-log & di-return). ⚠️ **Gap (diperbaiki oleh hardening di bawah)**: status **worker** `sync-shopee-performance` tetap `success` walau semua GMS gagal (task `return nil` per-toko), sehingga `worker_history` tak mencerminkan kegagalan — ini yang membuat "cron jalan tapi data GMS tak masuk" tak terlihat sejak ~24 Jun 2026.
- **Webhook order ingest — TikTok vs Shopee** (jalur "direct"/push, registry `(platform, source) → processor`): keduanya kini menarik order detail dari API platform, tapi beda strategi. **TikTok direct** (`TiktokDirectProcessor`) **selalu** tarik order detail dari API TikTok tiap webhook (bisa buat order baru). **Shopee push** (`ShopeePushProcessor`, code 3) kini **create-on-missing**: order yang sudah ada → update status saja (0 call API); order baru → tarik order detail dari Shopee (buat order). Sebelumnya Shopee-push hanya update-status & **error** bila order belum ada. Langkah menuju "lepas dari [[External - Desty]]" untuk Shopee.
- **Rate-limit gate Shopee** (proses-wide, in-memory): begitu ada call Shopee balas `error_limit`, gate menyala sampai **00:00 UTC+8** (reset kuota Shopee). Webhook order-fetch cek gate **sebelum** call — bila menyala, **skip + defer** (retry setelah reset) agar tidak menambah call gagal saat kuota habis. Push code ≠ 3 / tanpa `order_sn` → di-acknowledge tanpa error.
- **Dual-app credential per toko (routing per `account_type`)** ✅ live — tiap toko Shopee kini bisa punya DUA kredensial: **ADS_SERVICE** (app "Ads Bharata", partner `2032638`) untuk **GMS** (`get_gms_*`), dan **ERP_SYSTEM** (app "One Bharata", partner `2032314`) untuk **order/escrow/push** (`get_order_*`, `get_escrow_detail`). Sebab: kategori app Shopee memisahkan **Ads vs ERP secara desain** — tak ada satu app yang punya izin GMS + Payment/escrow sekaligus. Resolusi kredensial sadar-API-group (`getAndRefreshCredentialByType`): GMS→ADS_SERVICE, order/escrow→ERP_SYSTEM; **degrade gracefully** bila salah satu cred belum ada (skip tanpa fail). Index unik compound `(shop_id_list, account_type)` mengizinkan kedua cred hidup berdampingan; `/shopee/accounts/list` mengembalikan `account_type` + `shop_id_list` (frontend menggabung 2 cred jadi 1 kartu per toko). Grounded: `usecase/shopee_new_usecase.go`, `repository/shopee_repo.go`.
- **AMS affiliate — `account_type` KETIGA (tri-app)** ✅ live (spike terverifikasi prod 2026-07-03) — menyusul dual-app, ditambah **`AMS`** (app "Affiliate Bharata", partner `2038141`, kategori Shopee **"Affiliate Marketing Solution Management"**). AMS OpenAPI (`/api/v2/ams/*`, modul 127) **HANYA** bisa dipanggil app kategori ini — ADS (`2032638`)/ERP (`2032314`) **tak bisa** (sama seperti Ads-vs-ERP: kategori app fixed). Endpoint: `GET /shopee/affiliate/performance?shop_id=` (per-affiliate: `sales`/`orders`/`items_sold`/`est_commission`/`roi`/`total_buyers`/`clicks` dari `get_affiliate_performance`; default Last30d/AllChannel/ConfirmedOrder, page_size ≤20) + `GET /shopee/affiliate/recommended?shop_id=&limit=` (`get_recommended_affiliate_list`). Route sadar-account-type (`getAndRefreshCredentialByType(shopID, AMS)`); money field = **string desimal**, `roi` bisa `"--"`. Live 908963392 → **507 affiliate** (top "Shopee Media Network" Rp16,1jt/162 order/ROI 19). **v1 = proxy on-demand** (belum sync-ke-DB; tren historis + koleksi **`shopee_affiliate_performance`** = v1.1/v2). Frontend: **Marketing Insight → Affiliate**, toggle **Shopee/TikTok** (default Shopee), view Shopee = pemilih toko (akun ber-cred AMS) + KPI + tabel per-affiliate + kartu Rekomendasi. Catatan: app AMS "No access to Sensitive Data" **tak** menghalangi data performa affiliate. Grounded: `clients/shopee_ams_client.go`, `usecase/shopee_new_usecase.go` (`GetAffiliatePerformance`/`GetRecommendedAffiliates`), `interface/http/shopee_affiliate_handler.go`, FE `features/marketing-insight/affiliate/`.
- **Anti-burst GMS + status jujur (hardening 2026-07-01)** ⚠️ **sudah di kode, belum deploy** — perbaikan akar penyebab data GMS berhenti masuk sejak ~24 Jun 2026. **Akar masalah** (terverifikasi via `worker_history` prod + Shopee console access-log partner `2032638`): call `/ads` (`get_gms_item_performance` / `get_gms_campaign_performance`) yang di-**burst** per toko (fan-out goroutine per-hari/campaign) memicu `ads_rate_limit_shop_api`; **run-wide breaker** lalu meng-abort seluruh run pada throttle pertama; dan kegagalan **ditelan** worker (status `success` palsu). **Perbaikan** (tanpa retry/backoff): **(1) anti-burst** — call `/ads` per toko kini **diserialkan + di-pace** (`adsCallPacing` 1500 ms via `paceAdsCall`), menggantikan fan-out goroutine; konkurensi worker **3 → 2**. **(2) Status jujur** — worker mengagregasi hasil per-toko (`summarizeShopResults`) → `worker_history.status=failed` + ringkasan `ok / rate-limited / failed` saat partial/rate-limited (sentinel `ErrShopeeRateLimited`), menutup gap di atas. **(3) Hemat kuota** — `get_shop_info` **tak lagi** dipanggil saat refresh token (shop info sudah terisi saat auth `ExchangeAccessToken`), membebaskan kuota harian app Ads untuk call GMS. Order **tidak** terdampak karena app terpisah (partner `2032314`). Grounded: `worker/tasks/shopee_sync_task.go`, `usecase/shopee_new_usecase.go` (`SyncGMSItemPerformances` / `SyncGMSCampaignPerformances`, `paceAdsCall`, `ErrShopeeRateLimited`).
- **Escrow income (`get_escrow_detail`) via One** ✅ live — untuk order **COMPLETED**, `SyncOrderDetail` menarik escrow (net settlement setelah fee) dan mengisi field `income` transaction order. **Fix bug decode (2026-07-01)**: Shopee mengirim `order_income.tenure_info_list` sebagai **array**, tapi dimodelkan struct tunggal → decode gagal 100% (income tak pernah terisi); diperbaiki jadi `[]ShopeeTenureInfo` (`clients/shopee_client_new.go`, `entity/shopee.go`) → escrow tervalidasi terisi di prod. **Backfill histori** ✅ (live, dijalankan 2026-07-01): `GET /shopee/orders/escrow/backfill?shop_id=&limit=` (`BackfillEscrow`) memilih order completed lokal ber-`income` null (filter `TransactionOrderFilter.IncomeEmpty`) → escrow-only tanpa re-list, batch 50, breaker bersama, **resumable**. Toko 908963392 ter-backfill penuh: **1.308/1.308** order completed kini ber-`income` (looped `limit=40`, ~29 putaran, tanpa rate-limit). **Escrow-capture on completion (2026-07-02):** `ShopeePushProcessor` dulu pada push code 3 untuk order **existing** cuma update status (escrow tak pernah ditarik saat completion → income null menumpuk); kini pada transisi → **COMPLETED** ia memanggil `SyncOrderDetail` (tarik escrow → isi `income`), re-read agar income tak ke-timpa update status, `CompletedAt` terjaga, defer (`ErrDelayed`) saat rate-limit/auth, non-fatal saat escrow belum siap; status non-COMPLETED tetap 0 API-call (`shopee_push.go`). **shopee_income di order-detail:** `GET /transactions/orders/:id` untuk order Shopee **COMPLETED** kini mengekspos objek **`shopee_income`** (2 seksi ala Seller Center: **Rincian Penghasilan** seller + **Pembayaran Pembeli**) dari escrow tersimpan (rekonsiliasi persis: seksi seller = `escrow_amount`, seksi buyer = `buyer_total_amount`); nil bila non-completed → FE fallback ke PaymentSummary. Grounded: `interface/http/shopee_income.go`, `transaction_handler.go` (`renderShopeeTransactionDetail`).
- **Manual order sync histori panjang (chunking ≤15 hari)** ⚠️ **sudah di kode, belum deploy** — `GET /shopee/orders/sync` kini bisa menarik histori panjang (mis. ~3 bulan) dalam satu panggilan. `get_order_list` Shopee membatasi jendela `time_from`/`time_to` ke **≤15 hari**, jadi rentang dipecah otomatis ke sub-window ≤15 hari (`splitOrderWindows`, span 14 hari, urut **terbaru→terlama**, kontigu & disjoint) dan tiap window disync via `syncOrdersWindow`, berbagi **satu circuit breaker per-run** + pacing antar-window (`paceOrderCall` 400 ms; terpisah dari `paceAdsCall`/GMS). **Sengaja TIDAK memakai gate proses-wide `IsShopeeRateLimited()`**: gate itu juga di-trip oleh app **Ads** (GMS, partner `2032638`), sedangkan order memakai app **ERP_SYSTEM** (partner `2032314`) berkuota independen — mengikat order ke gate akan membuat throttle GMS **salah-memblokir** order sync yang masih punya kuota (breaker per-run mencerminkan respons app ERP yang benar). **Honest-partial**: bila breaker trip di tengah run → `SyncOrders` return `ErrShopeeRateLimited`, handler balas **HTTP 200 "partial"** (bukan 500) + ringkasan **success-rate per-endpoint** (`APIStatsSummary`) di body agar sync manual bisa dipantau; idempoten & resumable (upsert). Shop tanpa kredensial ERP → skip **satu kali** (sentinel di-propagasi, bukan re-cek tiap window). Param query: `shop_id` (wajib), `time_from`/`time_to` (unix) **atau** `days` (mis. `days=90`); guard rentang **maks 400 hari**. **Validasi backfill Juni 2026** (dijalankan 2026-07-03 via harness one-off `cmd/ordersync`, chunk ~7 hari; endpoint HTTP sendiri **belum deploy**): **8 toko**, **~14.700 call** order+escrow **~100%**, **tanpa sekali pun rate-limit** — 2 order escrow sempat gagal (blip jaringan) lalu di-fix via re-run chunk (repo-first → hanya 2 escrow kurang yang di-call ulang). Mengonfirmasi kuota harian app **ERP_SYSTEM** (`2032314`) lega untuk order+escrow (kontras app Ads `2032638` yang kronis ter-throttle sejak ~24 Jun). Grounded: `usecase/shopee_new_usecase.go` (`SyncOrders` / `syncOrdersWindow` / `splitOrderWindows` / `paceOrderCall` / `orderListWindow`), `interface/http/shopee_handler.go` (`SyncOrders`).

## Belum Diimplementasikan / Catatan

- **Target kirim selain Accurate** mengembalikan `501` ("service integration not implemented yet"); enum service yang tersedia baru `ACCURATE`.
- Route direct-push Accurate (`/transactions/summary/create|send|status`) handler-nya sudah **LENGKAP**, tetapi route-nya **DI-COMMENT** — digantikan alur summary-report `/send/:service`.
- Route webhook Desty langsung (`/webhook/desty`, `/webhooks/desty`) **di-comment** — digantikan `/webhooks/services/desty`.
- CronManager lama **fully disabled** — fungsinya dipindah ke worker framework.
- **Lazada** hanya disebut di kode cron yang sudah disabled — **TIDAK ada client Lazada** (placeholder/partial).
- TODO kecil: indexing `time.Time`.

## Dependencies & Integrasi

- [[CORE - API Master Gateway]] — entry point / routing ke service
- [[External - Accurate]] — bridging finansial (Accurate Online, HMAC-signed): Sales Invoice / Sales Return
- [[Microservices - Insentive Service]] — konsumen data iklan (laporan TikTok/Shopee)
- [[Microservices - TikTok Shop Service]] — webhook landing
- [[DB - Overview and Notes]] — MongoDB & Redis (queue prefix `srv:integration`)

External lain: TikTok Shop, TikTok Business/Ads, Shopee, [[External - Desty]] (middleware order), Telegram (notifier error/job).

## Dokumen Terkait

- [[External - Desty]] — vendor middleware orkestrasi order (webhook + auto-approve)
- [[Sales - Marketplace Integration]] (konsep sisi marketing)
- [[Finance - Bridging App]]
- [[Sales - GMV Creative]]
- [[Vendor - CRM]]
- [Referensi API — docs-api-greget](https://docs-api-greget.vercel.app/) — REST API lengkap (129 endpoint, Nextra)
- [[IT - Background Jobs & Schedulers]] — 9 cron + webhook dispatcher service ini (sync TikTok/Shopee/Desty; konsumsi webhook tiap 5 dtk)
