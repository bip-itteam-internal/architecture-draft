## Deskripsi

*Endpoint **integration-service** (marketplace ⇄ Accurate: TikTok Shop/Business, Shopee, Desty, transaksi, items, marketing teams, worker/jobs). Gateway: `/api/integration/*`; webhook publik via `/ext/webhook/:service`. ~175 rute. Grounded ke `services/integration/internal/interface/http/*`.*

- **Implementasi**: [[Microservices - Integration Service]] · **Status**: ✅
- **Indeks**: [[API - Index]] · Semua butuh gateway key kecuali webhook publik & `/health`.

## Webhooks
| Method | Path | Fungsi |
|---|---|---|
| POST | `/webhooks/services/desty` · `/shopee` · `/tiktok` | Terima webhook (PUBLIK, tanpa gateway) |
| GET | `/webhooks/logs` · `/webhooks/logs/:id` · `/webhooks/tasks` · `/webhooks/accounts/desty` | Log & task webhook |
| POST | `/webhooks/logs/:id/retry` | Retry pengiriman webhook |

## Transactions / Orders
| Method | Path | Fungsi |
|---|---|---|
| GET | `/transactions/orders/list` · `/orders/:id` · `/orders/summary[/shops|/products]` | Order terpadu + ringkasan |
| GET | `/transactions/orders/summary/comparison` | Perbandingan omset hari ini vs kemarin per channel (total + 24 slot hourly, status TO_SHIP, aggregasi by `order_update_date`) |
| GET | `/transactions/master/shops` · `/channels` · `/status` | Master shop/channel/status |
| GET/POST | `/transactions/summary/reports` (+ `/:id`, `/:id/items`, `/:id/invoices`, `/group-by-status`) | Laporan ringkasan (generate/list/detail) |
| POST | `/transactions/summary/reports/:id/retry` · `/send/:service` · DELETE `/:id` | Retry/kirim/hapus laporan |
| GET | `/transactions/insight/demography` | Insight demografi |

## TikTok Shop
| Method | Path | Fungsi |
|---|---|---|
| GET | `/tiktok/shop/auth` · `/auth/callback` · `/authorized-shops` | OAuth + shop terotorisasi |
| GET | `/tiktok/shop/orders/list[/direct]` · `/orders/detail[/direct]` · `/orders/sync` | Order (cache/direct/sync) |
| GET | `/tiktok/shop/insight/gmv-winning-content` | Insight GMV |
| GET | `/tiktok/shop/insight/creator-video-count` | Jumlah video per-creator per bulan (dari `tt_shop_video_performances`; sumber produksi ICC 125/bln). ⚠️ Baru, belum deploy |
| GET/DELETE | `/tiktok/shop/accounts/list` · `/accounts/:id` | Akun TikTok Shop |

## TikTok Business
| Method | Path | Fungsi |
|---|---|---|
| GET | `/tiktok/business/auth[/callback]` · `/advertisers[/info][/direct]` · `/stores[/products]` | Auth, advertiser, store |
| GET | `/tiktok/business/report/integrated[/daily/ad][/sync][/list][/summary/list]` | Laporan integrated |
| GET | `/tiktok/business/report/gmv_max/...` (performance, product, campaigns, items, summary, monitoring, daily/sync) | Laporan GMV-Max |
| GET | `/tiktok/business/report/gmv_max/monitoring` | Ranking campaign GMV Max (GMV/ROI/orders/cost) lintas account/shop + flag **GMV winner** (ROI≥3.2 & order≥15, ICC 2026) untuk dashboard marketing-insight. ⚠️ Baru, belum deploy. Grounded: `tiktok_business_handler.go` (`ListGMVMaxMonitoring`) |
| GET | `/tiktok/business/insight/icc-video-metrics` | Metrik per-video ICC (ctr/watch25/roas/orders/post_date/creator) untuk insentif ICC; agregasi GMV Max + join `campaign_items` + `tt_shop_video_performances`. ⚠️ Baru, belum deploy. Grounded: `ListICCVideoMetrics` |
| GET | `/tiktok/business/sync/master-data` · `/accounts/list` · `/accounts/:id` (GET/POST/DELETE) | Sync & akun |

> ⚠️ Akun TikTok Business punya field **`brand`** (mis. KYURA/BEAUTYHACKS): di-set via `POST /accounts/:id`, dikembalikan oleh `/accounts/list`; dipakai form integrasi insentif untuk pengelompokan akun (Brand → Account → Advertiser). Grounded: `tiktok_business_handler.go`. Sudah di kode, **belum deploy**.

## Shopee
| Method | Path | Fungsi |
|---|---|---|
| GET | `/shopee/auth[/callback]` · `/shops/list` · `/products/items` | OAuth, shop, produk |
| GET | `/shopee/orders/list` · `/orders/detail` · `/orders/sync` · `/orders/escrow/backfill` · `/v2/shopee/orders/list` | Order (v1/v2/sync **chunked ≤15 hari** + backfill escrow income) |
| GET | `/shopee/gms/item-performance[/sync|/summary]` · `/campaign-performance[/sync|/summary]` | Performa GMS |
| GET/POST | `/shopee/affiliate/performance` · POST `/affiliate/sync` · `/affiliate/recommended` | Affiliate/AMS — per-affiliate performa (baca DB `shopee_affiliate_performance`, sales/order/komisi/ROI) + `sync` (backfill manual dari AMS) + rekomendasi (proxy, via app AMS) |
| GET/POST | `/shopee/affiliate/conversions[/sync]` · `/affiliate/validations[/sync]` | **Affiliate v2 (AMS order-level)** ✅ live — ledger order+item (baca DB `shopee_affiliate_conversion`, `get_conversion_report`; `price`/komisi = **string desimal rupiah**) + tagihan komisi bulanan & rekonsiliasi (`shopee_affiliate_validation_bill`, `get_validation_list`/`get_validation_report` window placement **[M−2..M−1]**); `sync` = backfill background via notifier |
| GET/POST/DELETE | `/shopee/accounts/list` · `/accounts/:id` | Akun Shopee |

> **Tri-app per toko** (✅ live): tiap shop bisa punya sampai 3 kredensial via `account_type` — **ADS_SERVICE** (GMS, partner 2032638), **ERP_SYSTEM** (order/escrow/push, 2032314), **AMS** (affiliate, 2038141, kategori app "Affiliate Marketing Solution Management" — hanya app ini yang bisa panggil AMS API); `/accounts/list` mengembalikan `account_type` + `shop_id_list`. **`/orders/escrow/backfill?shop_id=&limit=`** (✅ live): isi `income` order COMPLETED yang belum ter-escrow (escrow-only, resumable) — backfill 908963392 (1.308/1.308). **`/affiliate/performance`** (✅ live, **baca DB** `shopee_affiliate_performance`, roll-up per-affiliate, param `start_date`/`end_date` yyyymmdd, default 30 hari) + **`POST /affiliate/sync`** (backfill manual dari AMS, snapshot harian) + **`/affiliate/recommended`** (proxy live). Snapshot harian juga diisi worker `sync-shopee-affiliate-performance` (03:00, lihat [[IT - Background Jobs & Schedulers]]). ⚠️ `total_buyers`/`new_buyers` = akumulasi harian (buyer-hari, bukan pembeli unik). Detail: [[Microservices - Integration Service]].

> **`/orders/sync`** (⚠️ baru, belum deploy): tarik order per toko, mendukung **histori panjang (~3 bulan)** via chunking otomatis ke window **≤15 hari** (batas `get_order_list`), satu circuit breaker per-run, **tanpa** gate proses-wide (app order ERP_SYSTEM `2032314` terpisah dari GMS `2032638`). Param: `shop_id` (wajib), `time_from`/`time_to` (unix) **atau** `days` (mis. `days=90`; maks **400 hari**). Rate-limit di tengah → **HTTP 200 partial** + ringkasan success-rate di body. Grounded: `shopee_handler.go` (`SyncOrders`). Detail: [[Microservices - Integration Service]].

## Accurate (akuntansi)
| Method | Path | Fungsi |
|---|---|---|
| GET/POST/PUT/DELETE | `/accurate/settings/shops[/:id]` | Shop di Accurate |
| GET/POST/PUT/DELETE | `/accurate/products[/list|/:id]` | Produk Accurate |
| GET/POST/PUT/DELETE | `/accurate/bank-accounts[/list|/:id]` | Rekening bank Accurate |
| GET/POST/PUT/DELETE | `/accurate/settings/kv-configs[/list|/:id]` | KV config Accurate |

## Items · Credentials · Holidays
| Method | Path | Fungsi |
|---|---|---|
| GET | `/items/list` · `/items/sku/:sku` · `/items/:id[/history]` | Master item/SKU |
| POST | `/items/` · `/items/bulk` · `/items/bundle` · `/items/variations` | Buat item/bundle/variasi |
| PATCH/DELETE | `/items/:id` | Update/hapus item |
| POST | `/credentials` | Kredensial platform |
| GET/POST/DELETE | `/holidays[/:id]` | Hari libur kalkulasi |

## Marketing Teams (admin) · Worker/Jobs
| Method | Path | Fungsi |
|---|---|---|
| GET/POST/PATCH/DELETE | `/marketing/teams[/:id]` (+ `/members[/:employeeId]`, `/shops[/:shopAssignmentId]`) | Tim marketing + ACL shop (admin) |
| GET | `/jobs/status` · `/jobs/histories` · `/jobs/configs` · `/jobs/:name/status|history|config` | Status/histori/config job |
| POST/PUT | `/jobs/:name/trigger` · `/config` · `/disable` · `/enable` | Kelola scheduler |
| GET | `/health` | Health (tanpa gateway) |

> Banyak job terjadwal (sync TikTok/Shopee/Desty + webhook consumer 5 detik) — lihat [[IT - Background Jobs & Schedulers]].

## Dokumen Terkait
- [[Microservices - Integration Service]] · [[Sales - Marketplace Integration]] · [[External - Accurate]] · [[External - Desty]] · [[IT - Background Jobs & Schedulers]] · [[API - Index]]
