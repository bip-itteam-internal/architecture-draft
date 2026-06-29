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
- `POST /webhooks/services/shopee` — ingest **Shopee Push Mechanism** (publik via gateway `/ext/webhook/shopee`). Auth **HMAC-SHA256** atas string `URL|body` lewat header `Authorization`; key dipilih per query `app_type` (`ads`/`order`/`marketing`/`one` → `SHOPEE_ADS_WEBHOOK_KEY` / `SHOPEE_ORDER_WEBHOOK_KEY` / `SHOPEE_MARKETING_WEBHOOK_KEY` / `SHOPEE_ONE_WEBHOOK_KEY`). ⚠️ Verifikasi signature **sementara di-bypass** — mismatch hanya di-log lalu tetap 200 (workaround bug Shopee console saat simpan key baru; `webhook_usecase.go`). Payload disimpan ke `webhook_logs` lalu diproses async oleh `ShopeePushProcessor` (create-on-missing — lihat *Observability & Ketahanan Shopee* di bawah).
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
- OAuth: `/auth` (+ callback)
- Orders: list, v2 list, detail, sync
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
- **Ketahanan refresh & sync Shopee** (akar masalah restriction rate-limit Shopee, lihat [[LOG - Shopee API Rate Limit Request]]): distributed lock refresh-token per-shop (Redis) cegah race antar-instance + **circuit breaker** yang menghentikan run begitu Shopee balas `error_limit` (cegah death-spiral kuota) + retry simpan credential + timeout independen per-shop + observability (kegagalan GMS tidak lagi senyap).
- **Webhook order ingest — TikTok vs Shopee** (jalur "direct"/push, registry `(platform, source) → processor`): keduanya kini menarik order detail dari API platform, tapi beda strategi. **TikTok direct** (`TiktokDirectProcessor`) **selalu** tarik order detail dari API TikTok tiap webhook (bisa buat order baru). **Shopee push** (`ShopeePushProcessor`, code 3) kini **create-on-missing**: order yang sudah ada → update status saja (0 call API); order baru → tarik order detail dari Shopee (buat order). Sebelumnya Shopee-push hanya update-status & **error** bila order belum ada. Langkah menuju "lepas dari [[External - Desty]]" untuk Shopee.
- **Rate-limit gate Shopee** (proses-wide, in-memory): begitu ada call Shopee balas `error_limit`, gate menyala sampai **00:00 UTC+8** (reset kuota Shopee). Webhook order-fetch cek gate **sebelum** call — bila menyala, **skip + defer** (retry setelah reset) agar tidak menambah call gagal saat kuota habis. Push code ≠ 3 / tanpa `order_sn` → di-acknowledge tanpa error.

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
