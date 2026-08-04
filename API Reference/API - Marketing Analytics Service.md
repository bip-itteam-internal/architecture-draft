## Deskripsi

*Daftar endpoint **Marketing Analytics Service** — grounded ke kode (`routes.go`, `handler_mart.go`, `price_floor_handler.go`, `jobs.go`, `penjadwal_status.go`; audit 2026-08-02, 21 route). Arsitektur & semantik data: [[Microservices - Marketing Analytics Service]].*

- **Status**: ✅ Grounded ke kode (2026-08-02)
- **Prefix gateway**: `/api/marketing-analytics/*` → path internal tanpa prefix. Routing & auth: [[API - Index]].

## Konvensi respons

- Amplop `{rows, unavailable_channels, ...}`; `unavailable_channels` menandai channel yang datanya memang tak disediakan platform (mis. Lazada tanpa analytics konten) beserta alasannya.
- **`kolom_tidak_berlaku`** (bila ada): kolom yang di level itu tak punya sumber sama sekali — FE wajib menghilangkan kolomnya, bukan merender "—" per baris.
- Parameter enum yang tak dikenal → **400 + daftar nilai sah** (tidak jatuh diam-diam ke bawaan). Batas tanggal **hari WIB**, batas atas eksklusif.
- Endpoint drill berpaginasi: `limit` bawaan 50 maks 500, `offset`; `total: -1` = cacah gagal (bukan 0).

## Laba (`mart_profit_attribution`)

| Method | Path | Catatan |
|---|---|---|
| GET | `/summary` | Ringkasan lintas sumber |
| GET | `/profit/shops` | `granularitas=bulanan\|harian` (bawaan bulanan) · `bulan=YYYY-MM` · `sort_by`/`sort_dir` |
| GET | `/profit/products` | + `lingkup=lintas_toko\|per_toko` (bawaan lintas_toko; baris gabungan membawa `jumlah_toko`, `shop_id` kosong) |
| GET | `/profit/campaigns` | idem shops |
| GET | `/profit/ads` | + `campaign_id` (filter drill); baris membawa `metrik_iklan` (15 metrik API, `spend` per mata uang) |
| GET | `/profit/orders` | Drill product → order. `entity_id` **wajib**; `bulan` XOR `dari`/`sampai`; `termasuk_batal=true\|false` (bawaan false — CANCELLED dikecualikan, konsisten agregasi); respons + `sku_tercakup` |

## Video & live

| Method | Path | Catatan |
|---|---|---|
| GET | `/videos` | `VideoRow` (tab VSA/GMV Max/organik); + `gross_profit` (nil = tak pernah dihitung), `product_title`/`product_image_url`/`product_item_group_id`, `ad_id`, `channel`, `synced_at`. **Menolak `granularitas` (400)** — snapshot kumulatif |
| GET | `/videos/orders` | Drill video → order **affiliate saja** (`affiliate_orders`, `content_type="VIDEO"`). `video_id` **wajib**; field `cakupan` selalu terisi |
| GET | `/lives` | `mart_live_sessions` (koleksi masih kosong) |

## Retur & analitik

| Method | Path | Catatan |
|---|---|---|
| GET | `/returns/breakdown` | Agregat per channel+initiator+alasan mentah+kurir; `refund_value` ≠ `order_value` |
| GET | `/returns/detail` | Drill → daftar order (order_id, toko, ICC, items, alasan mentah). `reason=` kosong bermakna "tanpa alasan tercatat"; `initiator=BUYER\|SYSTEM\|SELLER` |
| GET | `/affiliate` | + `collaboration_type=internal\|eksternal\|tanpa_kolaborasi`; `sort_by`: orders/gmv/actual_commission/est_commission/returns |
| GET | `/cohort` | Kohort pembeli |
| GET | `/audience` | `sort_by`: orders/returns/return_rate_pct/return_value/revenue |
| GET | `/matrix/sku-shop` | 🔴 **Stub** — envelope kosong |

## Price floor

| Method | Path | Catatan |
|---|---|---|
| GET | `/price-floor` | Daftar harga minimal per SKU (effective-dated) |
| POST | `/price-floor` | Tambah baris |
| POST | `/price-floor/upload` | Upload xlsx; laporan per-baris, unggahan yang tak menyimpan apa pun dibalas galat |

## Job, penjadwal & health

| Method | Path | Catatan |
|---|---|---|
| POST | `/jobs/:name/trigger` | `:name` = `sync-ad-creative-link` · `sync-video-performance` · `sync-profit-attribution`. `?hari` bawaan 7 maks 120 (hanya profit-attribution yang memakainya); job berjalan → **409**; `hari` cacat → **400, job tidak jalan** |
| GET | `/jobs/status` | `penjadwal_hidup`, `dinonaktifkan`, alasan, interval, ambang mati 72 jam, `sync_state` tiap job |
| GET | `/health` | `ok` / `degraded` (503) bila index unik gagal dibuat |

## Dokumen Terkait

- [[Microservices - Marketing Analytics Service]] · [[API - Index]] · [[CORE - API Master Gateway]]
