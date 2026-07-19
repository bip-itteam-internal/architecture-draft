## Deskripsi

*Endpoint **integration-service** (marketplace ⇄ Accurate: TikTok Shop/Business, Shopee, transaksi, items, ulasan marketplace, ICC account mapping, marketing teams, worker/jobs). Gateway: `/api/integration/*`; webhook publik via `/ext/webhook/:service`. **≈219 rute** (dihitung dari registrasi `main.go`; +5 `/reviews/*` 2026-07-19). Grounded ke `services/integration/internal/interface/http/*` + `main.go`.*

- **Implementasi**: [[Microservices - Integration Service]] · **Status**: ✅
- **Indeks**: [[API - Index]] · Semua butuh gateway key kecuali webhook publik (`/ext/webhook/*`). ⚠️ `/health` **juga** butuh gateway key (route terdaftar setelah middleware `ValidateGateway`; gateway memanggilnya dengan key — bukan endpoint terbuka).

## Webhooks
| Method | Path | Fungsi |
|---|---|---|
| POST | `/webhooks/services/shopee` · `/tiktok` · `/accurate` | Terima webhook (PUBLIK, tanpa gateway) |
| GET | `/webhooks/logs` · `/webhooks/logs/:id` · `/webhooks/tasks` | Log & task webhook |
| POST | `/webhooks/logs/:id/retry` | Retry pengiriman webhook |

## Transactions / Orders
| Method | Path | Fungsi |
|---|---|---|
| GET | `/transactions/orders/list` · `/orders/:id` · `/orders/summary[/shops|/products]` | Order terpadu + ringkasan |
| GET | `/transactions/orders/export` | Export daftar order (Order Management) ke **.xlsx**, 1 baris per item. Filter identik `/orders/list`: `channel`, `status`, `canceled_by`, `time_from`, `time_to`, `shop_id`, `order_id`. Tanpa paginasi (cap 10.000 order, `order_date` desc). Nama file (`Content-Disposition`) mencerminkan filter aktif (channel/shop/rentang tanggal `DD-MM-YYYY_sd_DD-MM-YYYY`) |
| GET | `/transactions/orders/summary/comparison` | Perbandingan performa 2 periode kustom: 4 metrik (TO_SHIP revenue, COMPLETED revenue, COMPLETED qty produk, COMPLETED order count) + granularity hourly/daily. Param: `start_date`, `end_date`, `comparison_start`, `comparison_end` (YYYY-MM-DD; default today vs yesterday), `channel` (opsional), `shop_id`, `timezone` |
| GET | `/transactions/orders/dashboard/summary` | Jumlah order aktif saat ini (tanpa filter tanggal) per kategori kartu dashboard: `pesanan_baru` (TO_PROCESS), `siap_dikirim` (TO_SHIP), `belum_di_proses` (TO_PROCESS+TO_SHIP), `pesanan_selesai` (COMPLETED). Param: `channel` (opsional), `shop_id` (opsional) |
| GET | `/transactions/returns` | **Feed retur lintas-channel** (Shopee **+** TikTok) untuk WMS gudang — satu baris per **event retur** (`return_sn`), bukan per order. Sumber: sub-dokumen `return` di `transaction_orders` (terisi untuk kedua channel). Param: `channel`, `shop_id`, `order_id`, `page`, `limit` (default 50, maks 500). Balasan tiap baris: `dedupe_key` (kunci join ke record gudang: `return_sn`, fallback `order_id`), `goods_returning` (terjemahan `solution`: false = refund-only, barang tak balik), `partial`, `status` retur vs `order_status`, `items[]` + `items_available`. Konsumen: [[API - Manufacture Service]] `GET /returns` |
| GET/POST | `/transactions/summary/reports` (+ `/:id`, `/:id/items`, `/:id/invoices`, `/group-by-status`) | Laporan ringkasan (generate/list/detail) |
| POST | `/transactions/summary/reports/:id/retry` · `/send/:service` · DELETE `/:id` | Retry/kirim/hapus laporan |
| GET | `/transactions/insight/demography` | Insight demografi |

> **Kenapa `/transactions/returns` ada, padahal sudah ada endpoint retur lain** — tiga hal yang mudah salah dipakai:
> - **Seleksinya keberadaan sub-dok `return`, BUKAN `status=RETURNED`.** [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] membuktikan 39% retur penuh tetap `COMPLETED` dan flip ke `RETURNED` tak deterministik → memfilter pakai status menyembunyikan mayoritas retur parsial.
> - **Bukan `/shopee/returns/list`** (Shopee-only): TikTok tak punya koleksi retur tersendiri — datanya masuk ke `transaction_orders.return` via `FetchAndSetTikTokReturn`, sedangkan `webhook_logs` TikTok (type 12) hanya membawa `order_id`+`return_status`, tanpa SKU/qty. Memakai endpoint Shopee untuk daftar lintas-channel = retur TikTok hilang diam-diam.
> - **Bukan `/accurate/daily-returns`**: barisnya hanya terbentuk untuk kebutuhan booking Accurate, jadi bukan cerminan semua retur.
>
> `items_available=false` berarti marketplace **tidak memberi rincian** item retur — **bukan** berarti tak ada barang. Item sengaja **tidak** disalin dari item order: itu akan mengklaim seluruh isi order kembali padahal tak diketahui, dan angkanya dipakai admin gudang menggerakkan stok.

## TikTok Shop
| Method | Path | Fungsi |
|---|---|---|
| GET | `/tiktok/shop/auth` · `/auth/callback` · `/authorized-shops` | OAuth + shop terotorisasi |
| GET | `/tiktok/shop/orders/list[/direct]` · `/orders/detail[/direct]` · `/orders/sync` | Order (cache/direct/sync). `/orders/detail` juga kembalikan `transaction_orders` = settlement per-order (Finance API `statement_transactions`, breakdown fee/ongkir/afiliasi/settlement per-SKU) |
| GET | `/tiktok/shop/orders/resi-feed` | Feed resi/AWB order TikTok (`no_resi`, ekspedisi, no pesanan, `status`, `rts_time`→shift, items) untuk **WMS Master Resi**. Param `updated_since`/`limit` (watermark). Di-pull manufacture `POST /resi/sync-tiktok` & di-push scheduler `sync-resi-wms`. Lihat [[API - Manufacture Service]] |
| GET | `/tiktok/shop/insight/gmv-winning-content` | Insight GMV |
| GET | `/tiktok/shop/settlement/sync-status` | Status sync income-reconciler: run terakhir + agregat harian dari `reconciler_run_stats` — konsumen: baris info FE settlement |
| GET | `/tiktok/shop/statements?shop_id&start&end&page&page_size` | 🟡 *branch `feat/statement-time-enrich`, belum deploy* — list batch pencairan (koleksi `tt_shop_statements`: tanggal cair, payable_amount, status, order_count) buat halaman FE Pencairan |
| GET | `/tiktok/shop/statements/:id/orders` | 🟡 *idem* — daftar order dalam satu statement (max 500) |
| GET/DELETE | `/tiktok/shop/accounts/list` · `/accounts/:id` | Akun TikTok Shop |

## TikTok Business
| Method | Path | Fungsi |
|---|---|---|
| GET | `/tiktok/business/auth[/callback]` · `/advertisers[/info][/direct]` · `/stores[/products]` | Auth, advertiser, store |
| GET | `/tiktok/business/report/integrated[/daily/ad][/sync][/list][/summary/list]` | Laporan integrated |
| GET | `/tiktok/business/report/gmv_max/...` (performance, product, campaigns, items, summary, daily/sync) | Laporan GMV-Max |
| GET | `/tiktok/business/sync/master-data` · `/accounts/list` · `/accounts/:id` (GET/POST/DELETE) | Sync & akun |

## Affiliate (TikTok Seller)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/affiliate/orders` | List order affiliate (filter: `store_id`, `creator_username`, `product_id`, `order_status`, `validation_status`, `from`/`to` unix; paginated `page`/`per_page`) |
| GET | `/affiliate/summary/totals` | KPI: GMV, komisi est/actual, jml order, jml creator |
| GET | `/affiliate/summary/creators` | Agregat per creator (GMV desc): order, konten, GMV, komisi |
| GET | `/affiliate/summary/products` | Agregat per produk: order, qty, GMV, komisi |
| GET | `/affiliate/summary/validation` | Breakdown validasi komisi vs finance statement (per status: VALIDATED/DISCREPANCY/NO_STATEMENT/PENDING) |
| GET | `/affiliate/summary/sync-history` | Aktivitas pipeline: sync/validasi terakhir, total order, 10 batch tarikan terakhir (per jam WIB) |

> Sumber = koleksi `affiliate_orders` (di-sync cron 8-jam via Search Seller Affiliate Orders API). Lihat [[ADR - 0009 Affiliate via Search Seller Affiliate Orders API]].

## Shopee
| Method | Path | Fungsi |
|---|---|---|
| GET | `/shopee/auth[/callback]` · `/shops/list` · `/products/items` | OAuth, shop, produk |
| GET | `/shopee/orders/list` · `/orders/detail` · `/orders/sync` · `/orders/escrow/backfill` · `/v2/shopee/orders/list` | Order (v1/v2/sync **chunked ≤15 hari** + backfill escrow income) |
| GET | `/shopee/orders/resi-feed` | Feed resi/AWB order Shopee untuk **WMS Master Resi** (AWB via `get_tracking_number`, diisi worker `sync-shopee-tracking`; shift dari `update_time`; `shop_id` disimpan di `shopee_order_details`). Konsumen: manufacture `POST /resi/sync-shopee` + scheduler `sync-resi-wms`. Lihat [[API - Manufacture Service]] |
| GET | `/shopee/returns/sync` · `/returns/list` | **Return/Refund ingestion** (chunked ≤15 hari, app ERP_SYSTEM) — tarik return via `get_return_list` → koleksi `shopee_returns` + sub-doc `order.return` (item **parsial** + tanggal proses + refund); `Partial` dari **kuantitas** (bukan uang). ⚠️ baru, tervalidasi live (15 return), belum deploy. Detail: [[Microservices - Integration Service]] |
| GET | `/shopee/gms/item-performance[/sync|/summary]` · `/campaign-performance[/sync|/summary]` | Performa GMS |
| GET/POST | `/shopee/affiliate/performance` · POST `/affiliate/sync` · `/affiliate/recommended` | Affiliate/AMS — per-affiliate performa (baca DB `shopee_affiliate_performance`, sales/order/komisi/ROI) + `sync` (backfill manual dari AMS) + rekomendasi (proxy, via app AMS) |
| GET/POST | `/shopee/affiliate/conversions[/sync]` · `/affiliate/validations[/sync]` | **Affiliate v2 (AMS order-level)** ✅ live — ledger order+item (baca DB `shopee_affiliate_conversion`, `get_conversion_report`; `price`/komisi = **string desimal rupiah**) + tagihan komisi bulanan & rekonsiliasi (`shopee_affiliate_validation_bill`, `get_validation_list`/`get_validation_report` window placement **[M−2..M−1]**); `sync` = backfill background via notifier |
| GET/POST | `/shopee/affiliate/products[/sync]` · `/affiliate/contents[/sync]` | **Affiliate v3 (AMS analytics)** ✅ live — per-produk (`get_product_performance`, baca DB `shopee_affiliate_product_performance`, ≈ klon v1 per-item) + per-konten Video/Live (`get_content_performance`, `shopee_affiliate_content_performance`; `views`/`likes` **kumulatif→MAX**, `sales` per-hari→SUM). Beda dari GMS item-performance. Sync harian via worker 03:00 + background manual |
| GET/POST/DELETE | `/shopee/accounts/list` · `/accounts/:id` | Akun Shopee |
| GET | `/shopee/payouts?shop_id&start&end&page&page_size` | 🟡 *branch `feat/statement-time-enrich`, belum deploy* — rekap pencairan escrow HARIAN per toko (dari `income.paid_at`+`payout_amount`; Shopee cair per-order, baris = pseudo-batch harian) buat tab Shopee halaman Pencairan |
| GET | `/shopee/payouts/orders?shop_id&date=YYYY-MM-DD` | 🟡 *idem* — order yang cair pada tanggal itu (max 500; dua param wajib; + order_date, completed_at) |

> **Tri-app per toko** (✅ live): tiap shop bisa punya sampai 3 kredensial via `account_type` — **ADS_SERVICE** (GMS, partner 2032638), **ERP_SYSTEM** (order/escrow/push, 2032314), **AMS** (affiliate, 2038141, kategori app "Affiliate Marketing Solution Management" — hanya app ini yang bisa panggil AMS API); `/accounts/list` mengembalikan `account_type` + `shop_id_list`. **`/orders/escrow/backfill?shop_id=&limit=`** (✅ live): isi `income` order COMPLETED yang belum ter-escrow (escrow-only, resumable) — backfill 908963392 (1.308/1.308). **`/affiliate/performance`** (✅ live, **baca DB** `shopee_affiliate_performance`, roll-up per-affiliate, param `start_date`/`end_date` yyyymmdd, default 30 hari) + **`POST /affiliate/sync`** (backfill manual dari AMS, snapshot harian) + **`/affiliate/recommended`** (proxy live). Snapshot harian juga diisi worker `sync-shopee-affiliate-performance` (03:00, lihat [[IT - Background Jobs & Schedulers]]). ⚠️ `total_buyers`/`new_buyers` = akumulasi harian (buyer-hari, bukan pembeli unik). Detail: [[Microservices - Integration Service]].

> **`/orders/sync`** (⚠️ baru, belum deploy): tarik order per toko, mendukung **histori panjang (~3 bulan)** via chunking otomatis ke window **≤15 hari** (batas `get_order_list`), satu circuit breaker per-run, **tanpa** gate proses-wide (app order ERP_SYSTEM `2032314` terpisah dari GMS `2032638`). Param: `shop_id` (wajib), `time_from`/`time_to` (unix) **atau** `days` (mis. `days=90`; maks **400 hari**). Rate-limit di tengah → **HTTP 200 partial** + ringkasan success-rate di body. Grounded: `shopee_handler.go` (`SyncOrders`). Detail: [[Microservices - Integration Service]].

> **Catatan Filter Toko (All Shop)**: Semua endpoint Shopee GMS (`/shopee/gms/*`) dan Shopee Affiliate (`/shopee/affiliate/*`) **mewajibkan parameter `shop_id` tunggal** (`shop_id > 0`). Untuk fitur filter **"All Shop"** di aplikasi ERP Web, frontend melakukan **Client-Side Aggregation** (`Promise.all` ke semua toko terotorisasi lalu menggabungkan responsnya secara live di browser) karena backend tidak mendukung query multi-toko/agregasi tanpa `shop_id` secara native.

## Accurate (akuntansi)
| Method | Path | Fungsi |
|---|---|---|
| GET/POST/PUT/DELETE | `/accurate/settings/shops[/:id]` | Shop di Accurate |
| GET/POST/PUT/DELETE | `/accurate/products[/list|/:id]` | Produk Accurate |
| GET/POST/PUT/DELETE | `/accurate/bank-accounts[/list|/:id]` | Rekening bank Accurate |
| GET/POST/PUT/DELETE | `/accurate/settings/kv-configs[/list|/:id]` | KV config Accurate |
| GET | `/accurate/daily-invoices` | List faktur harian auto-sync RTS (filter `shop_id`, `channel`, `date`/`date_from`/`date_to` (WIB `YYYYMMDD`), `status` SENT/FAILED/PENDING; paginated) |
| POST | `/accurate/daily-invoices/:id/retry` | Retry sinkron faktur auto-sync (re-snapshot order `TO_SHIP` shop-hari → kirim ulang, balas status akhir) |
| GET | `/accurate/daily-returns` (+ `/:id`, `/export`) | List/detail/export retur auto-sync (Retur Penjualan; filter `shop_id`/`channel`/`date`/`date_from`/`date_to`/`status` = `PENDING`/`SENT`/`FAILED`/`SKIPPED` (SKIPPED = sengaja dilewati & benar, hanya retur era manual pra-cutover — bukan kegagalan) + **`search`** (alias `order_id`) = cari by nomor pesanan **atau** nomor retur, partial & case-insensitive; `/export` memakai filter yang sama; paginated). *Status `FULL_VIA_INVOICE`/`HELD_REFUND_ONLY` **dihapus** oleh [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]].* |
| POST | `/accurate/daily-returns/:id/retry` | Retry sinkron retur auto-sync (baris `FAILED`). Menolak retur bertanggal **pra-cutover retur** (`20260701`, era manual finance) → set **`SKIPPED`** (bukan FAILED). Guard "order sudah RETURNED" **DICABUT 2026-07-17** (faktur permanen → retur = satu-satunya pembalikan). Over-retur tetap `FAILED` (anomali, harus terlihat) |
| GET | `/accurate/stocks?sku=` | Stok live per SKU listing (pecah komponen bundle via `product_sku_mappings`, get-stock.do) |
| POST | `/accurate/wms-adjustment` | **Internal (manufacture)**: pergerakan stok WMS → dokumen Penyesuaian Persediaan (create/edit protokol resmi; qty float dalam satuan Accurate). Lihat [[ADR - 0015 Push Pergerakan WMS ke Accurate]] |
| GET | `/accurate/stocks/list` | Semua stok dari salinan lokal `accurate_stocks` (search `q`, paginated; `only_products` default true = hanya item ter-mapping produk jualan) ✅ |
| GET | `/accurate/stocks/listing` | Stok per SKU listing dari salinan lokal: komponen bundle (+flag `mapped`) + stok efektif; sku numeric-id legacy tersaring ✅ |
| POST | `/webhooks/services/accurate` | Webhook Accurate (ITEM_QUANTITY/STOCK_MUTATION) → update `accurate_stocks` (PUBLIK via `/ext/webhook/accurate`) ✅ (pendaftaran di portal Accurate masih pending) |

> **Guard anti-dobel:** `POST /transactions/summary/reports/:id/send/accurate` (SALES_INVOICE) balas **409** + daftar overlap bila rentang report beririsan faktur auto-sync `SENT`; bypass `?force=true`.

## Items · Credentials · Holidays
| Method | Path | Fungsi |
|---|---|---|
| GET | `/items/list` · `/items/sku/:sku` · `/items/:id[/history]` | Master item/SKU |
| POST | `/items/` · `/items/bulk` · `/items/bundle` · `/items/variations` | Buat item/bundle/variasi |
| PATCH/DELETE | `/items/:id` | Update/hapus item |
| POST | `/credentials` | Kredensial platform |
| GET/POST/DELETE | `/holidays[/:id]` | Hari libur kalkulasi |

## Profit (Gross Profit per Product)

> ⚠️ Working branch `feat/gross-profit` (sudah di-push ke origin), belum merge/deploy.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/profit/products?start&end&shop_id&account_id&product_name&sku&mode` | Laba Sejati per produk (roll-up SKU + `bundles` + `breakdown` GMV/promo/fee/net-settlement/retur + `estimated_share` + `periods[]` bila HPP produk berubah di rentang — pecah per periode HPP presisi tanggal, SEMUA kolom qty→margin, tidak dirata-rata) + flags `unmapped_skus`/`missing_hpp`; `account_id` = credential TikTok Shop; `mode=settled` = MODE CAIR (hanya settlement actual: revenue/qty dari settlement, bucket belum cair dibuang, `estimated_share`=0, iklan diprorata porsi cair — periods iklan/laba juga diprorata ulang) — default semua order |
| POST | `/profit/costs/upload` | Upload xlsx HPP finance (multipart `file` + `effective_from`; **supervisor|admin modul integration/finance**) |
| GET | `/profit/costs?product_name=` | List HPP (riwayat per `effective_from`) |
| POST/PUT/DELETE | `/profit/costs` · `/profit/costs/:id` | CRUD HPP satuan manual dari UI (tambah/edit/hapus 1 baris; **supervisor|admin modul integration/finance**) |
| GET/POST/PUT | `/profit/mappings` | List/simpan mapping SKU↔item_id↔produk (mutasi **supervisor|admin modul integration/finance**) |
| POST | `/profit/mappings/seed` | Generate mapping 2 fase: master `items` (bundle+qty) + match SKU liar ke nama HPP finance (auto/saran); laporan created/skipped/auto_named/suggestions (**supervisor|admin modul integration/finance**) |
| DELETE | `/profit/mappings/:id` | Hapus mapping (**supervisor|admin modul integration/finance**) |
| POST/GET | `/profit/channel-map/upload` · `/profit/channel-map` | Upload kamus channel variation (export Master Product; sku_id→master SKU) · ringkas count (**upload: supervisor|admin integration/finance**) |
| GET | `/profit/order-listings` | Daftar Product Listing dari riwayat order (sample_name, item_id_count, mapped) — sumber dropdown form mapping |

## ICC Account Mapping

> Auth: `RequireMarketingLeader` (kyura/beauty_hacks SPV · insentive `adv_leader` · integration SPV/admin) — kecuali `/me`. Lihat [[Sales - ICC Account Manager Mapping]].

| Method | Path | Fungsi |
|---|---|---|
| GET | `/icc/mappings/me` | Mapping milik staff ICC yang login — **tanpa** `RequireMarketingLeader`; filter otomatis dari `BIP-Employee-ID` |
| GET | `/icc/mappings` | Daftar mapping ICC (filter: `employee_id`, `tiktok_shop_id`, `tiktok_advertiser_id`, `team`, `is_active`; default `true`) |
| POST | `/icc/mappings` | Buat mapping — `team` auto-fill dari `BIP-Department`; shop/advertiser opsional (minimal satu); enrich nama; validasi keunikan aktif; 409 jika duplikat |
| PATCH | `/icc/mappings/:id` | Update `is_active` / `notes` |
| DELETE | `/icc/mappings/:id` | Hapus mapping (hanya jika `is_active=false`; else 409) |
| GET | `/icc/mappings/available-shops` | TikTok Shop belum di-assign aktif (pool global) |
| GET | `/icc/mappings/available-advertisers` | Advertiser belum di-assign aktif (pool global; deduplikasi via `$group`) |

## Fulfillment (WMS Bridge — internal)

> Auth: gateway key global (semua rute `POST /fulfillment/*` di-cover `ValidateGateway`). Grounded: `usecase/warehouse_bridge_usecase.go`, `interface/http/warehouse_bridge_handler.go`.

| Method | Path | Fungsi |
|---|---|---|
| POST | `/fulfillment/ship-batch` | Batch ship order lintas platform (TikTok + Shopee). Body: `[{order_id, channel, shop_id, package_id}]`. Non-all-or-nothing: satu gagal tak membatalkan yang lain. Response: `[{order_id, channel, success, awb?, error?}]` |
| POST | `/fulfillment/labels` | Ambil shipping label per order. Body: `[{order_id, channel, shop_id, package_id}]` (POST — bukan GET — karena TikTok butuh `package_id` yang tidak derivable dari `order_id` saja). TikTok: synchronous, status READY + `url`. Shopee: async — status PROCESSING bila belum siap (WMS retry); READY + `pdf_data` (base64) bila sudah jadi |

## Kas Toko / Wallet (🟡 branch `feat/kas-toko`, PR #380 — belum merge)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/wallet/balances` | Saldo kas toko semua toko (Shopee aktual dari `current_balance`; TikTok estimasi anchor+Σ, flag `estimated`/`anchor_missing`/`sync_stale`) |
| GET | `/wallet/withdrawals` | Riwayat penarikan (filter shop/channel/type/status/tanggal WIB). Meta paginasi HANYA sisi TikTok; Shopee = list grup penuh + `completed_total` |
| GET | `/wallet/mutations` | Mutasi wallet Shopee ("Saldo Saya") + saldo berjalan, paginasi normal |
| GET | `/wallet/reconciliation` | Laporan uang masuk per toko basis `income.paid_at` (`paid_from/paid_to` wajib; `order_from/order_to` opsional — cross-periode) |
| GET | `/wallet/reconciliation/export` | Export Excel laporan |
| PUT | `/wallet/opening-balance/:shopId` | Set anchor saldo awal TikTok (`{amount, as_of}`) |
| GET | `/wallet/sync-status` | State sync per toko (last_run, status, error) |

## Reviews (Ulasan Marketplace)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/reviews/summary` | Ringkasan rating per toko (`start`/`end` YYYY-MM-DD WIB, `channel`, `shop_id`; SHOPEE=SUM harian, TIKTOK=snapshot kumulatif terbaru) |
| GET | `/reviews/products` | Agregat per produk, sort avg terendah dulu (`rating_avg` 1-5 bucket floor(avg) · `with_star` · `min_reviews` · +`shop_name`/`product_name`) |
| GET | `/reviews/products/:productId/trend` | Deret snapshot harian per produk (tren; TikTok = kumulatif, delta dihitung FE) |
| GET | `/reviews/comments` | Komentar Shopee (teks, baca-saja); `shop_id` **opsional** = feed global lintas toko (PR #568) · filter `item_id`/`rating`/`channel`/`has_text`/`has_media`/`unreplied` · paginated + join `product_name`/`shop_name` |
| GET | `/reviews/sync-status` | State sync per toko (`last_synced_at`, `last_error`, `backfill_truncated` cap-500 Shopee) |

> Worker `sync-reviews` harian 06:45 WIB. TikTok TIDAK punya API teks ulasan (hanya distribusi bintang kumulatif) — detail keterbatasan & desain: [[Microservices - Integration Service]] §Ulasan Marketplace.

## Marketing Teams (admin) · Worker/Jobs
| Method | Path | Fungsi |
|---|---|---|
| GET/POST/PATCH/DELETE | `/marketing/teams[/:id]` (+ `/members[/:employeeId]`, `/shops[/:shopAssignmentId]`) | Tim marketing + ACL shop (admin) |
| GET | `/jobs/status` · `/jobs/histories` · `/jobs/configs` · `/jobs/:name/status|history|config` | Status/histori/config job |
| POST/PUT | `/jobs/:name/trigger` · `/config` · `/disable` · `/enable` | Kelola scheduler |
| GET | `/health` | Health (tanpa gateway) |

> Banyak job terjadwal (sync TikTok/Shopee + webhook consumer 5 detik) — lihat [[IT - Background Jobs & Schedulers]]. Jalur [[External - Desty]] soft-disabled per 2026-07-12 (route `/webhooks/services/desty` + `/webhooks/accounts/desty` dicabut → 404).

## Dokumen Terkait
- [[Microservices - Integration Service]] · [[Sales - Marketplace Integration]] · [[External - Accurate]] · [[External - Desty]] · [[IT - Background Jobs & Schedulers]] · [[API - Index]]
