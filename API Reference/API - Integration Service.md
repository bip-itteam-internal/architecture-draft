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
| GET | `/transactions/orders/summary/comparison` | Perbandingan performa 2 periode kustom: 4 metrik (TO_SHIP revenue, COMPLETED revenue, COMPLETED qty produk, COMPLETED order count) + granularity hourly/daily. Param: `start_date`, `end_date`, `comparison_start`, `comparison_end` (YYYY-MM-DD; default today vs yesterday), `channel` (opsional), `shop_id`, `timezone` |
| GET | `/transactions/orders/dashboard/summary` | Jumlah order aktif saat ini (tanpa filter tanggal) per kategori kartu dashboard: `pesanan_baru` (TO_PROCESS), `siap_dikirim` (TO_SHIP), `belum_di_proses` (TO_PROCESS+TO_SHIP), `pesanan_selesai` (COMPLETED). Param: `channel` (opsional), `shop_id` (opsional) |
| GET | `/transactions/master/shops` · `/channels` · `/status` | Master shop/channel/status |
| GET/POST | `/transactions/summary/reports` (+ `/:id`, `/:id/items`, `/:id/invoices`, `/group-by-status`) | Laporan ringkasan (generate/list/detail) |
| POST | `/transactions/summary/reports/:id/retry` · `/send/:service` · DELETE `/:id` | Retry/kirim/hapus laporan |
| GET | `/transactions/insight/demography` | Insight demografi |

## TikTok Shop
| Method | Path | Fungsi |
|---|---|---|
| GET | `/tiktok/shop/auth` · `/auth/callback` · `/authorized-shops` | OAuth + shop terotorisasi |
| GET | `/tiktok/shop/orders/list[/direct]` · `/orders/detail[/direct]` · `/orders/sync` | Order (cache/direct/sync). `/orders/detail` juga kembalikan `transaction_orders` = settlement per-order (Finance API `statement_transactions`, breakdown fee/ongkir/afiliasi/settlement per-SKU) |
| GET | `/tiktok/shop/insight/gmv-winning-content` | Insight GMV |
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
| GET | `/shopee/orders/list` · `/orders/detail` · `/orders/sync` · `/v2/shopee/orders/list` | Order (v1/v2/sync) |
| GET | `/shopee/gms/item-performance[/sync|/summary]` · `/campaign-performance[/sync|/summary]` | Performa GMS |
| GET/POST/DELETE | `/shopee/accounts/list` · `/accounts/:id` | Akun Shopee |

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

## Profit (Gross Profit per Product)

> ⚠️ Working branch `feat/gross-profit` (sudah di-push ke origin), belum merge/deploy.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/profit/products?start&end&shop_id&account_id&product_name&sku&mode` | Laba Sejati per produk (roll-up SKU + `bundles` + `breakdown` GMV/promo/fee/net-settlement/retur + `estimated_share`) + flags `unmapped_skus`/`missing_hpp`; `account_id` = credential TikTok Shop; `mode=settled` = MODE CAIR (hanya settlement actual: revenue/qty dari settlement, bucket belum cair dibuang, `estimated_share`=0, iklan diprorata porsi cair) — default semua order |
| POST | `/profit/costs/upload` | Upload xlsx HPP finance (multipart `file` + `effective_from`; **supervisor|admin modul integration/finance**) |
| GET | `/profit/costs?product_name=` | List HPP (riwayat per `effective_from`) |
| POST/PUT/DELETE | `/profit/costs` · `/profit/costs/:id` | CRUD HPP satuan manual dari UI (tambah/edit/hapus 1 baris; **supervisor|admin modul integration/finance**) |
| GET/POST/PUT | `/profit/mappings` | List/simpan mapping SKU↔item_id↔produk (mutasi **supervisor|admin modul integration/finance**) |
| POST | `/profit/mappings/seed` | Generate mapping 2 fase: master `items` (bundle+qty) + match SKU liar ke nama HPP finance (auto/saran); laporan created/skipped/auto_named/suggestions (**supervisor|admin modul integration/finance**) |
| DELETE | `/profit/mappings/:id` | Hapus mapping (**supervisor|admin modul integration/finance**) |
| POST/GET | `/profit/channel-map/upload` · `/profit/channel-map` | Upload kamus channel variation (export Master Product; sku_id→master SKU) · ringkas count (**upload: supervisor|admin integration/finance**) |
| GET | `/profit/order-listings` | Daftar Product Listing dari riwayat order (sample_name, item_id_count, mapped) — sumber dropdown form mapping |
| GET | `/profit/cash-flow?start&end&shop_id&account_id` | Arus dana: `summary` (Sudah Cair actual + Uang Gantung estimasi shrinkage per toko, `estimate_ok`) + `accuracy_30d` (track-record rumus, on-the-fly) + `rows` per toko×bulan (sort gantung desc) |
| GET | `/profit/cash-flow/orders?start&end&shop_id&account_id` | Daftar order uang gantung (COMPLETED belum settle) untuk panel rincian: order_id, toko, akun (credential), tgl order, GMV, umur (hari sejak selesai); sort GMV desc, cap 500 |

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
