# Affiliate Seller Sync — Design

> Auto-sync data affiliate dari TikTok Shop **Affiliate Seller API** (bukan CSV import). Pola = sync existing (`SyncTTBusinessGMVMaxReport`).
> Bagian dari MASTER roadmap Scope 6. Spec sumber: `2026-06-30-marketing-dashboard-MASTER.md` §B4.

## Problem

Toko sudah jalankan affiliate program (creator promosi → order+komisi), tapi data affiliate (komisi per order, creator, content) **tidak ter-capture** di pipeline existing:
- `transaction_orders.income.total_affiliate_commission_fee` = 0 (settlement TikTok blend di fee_and_tax)
- `sku_transactions.fee_tax_breakdown.affiliate_*` = 0
- CSV `affiliate_orders_*.csv` = export manual (bukti data ada) — **hanya pembanding, BUKAN sumber produksi**

Butuh: tarik data affiliate **otomatis via API**, simpan, join ke dashboard (profit + ads analytics + per-creator).

## Decisions (locked)

- **Sumber = API, BUKAN CSV.** `Search Seller Affiliate Orders` (TikTok Shop Affiliate Seller API). CSV cuma verifikasi hasil.
- **Pola = sync task existing** (`internal/worker/tasks/tt_business_gmv_max_report.go`): `Run` + `Schedule` cron harian.
- **Reuse signing** existing: `generateSign`, `buildQueryString`, `tiktokAPIBaseURL` di `tiktok_client.go`. Host + auth (x-tts-access-token + app_key + shop_cipher + sign + timestamp) sama.
- **Token per-store** via `GetOrRefreshToken(storeID)` existing (auto-refresh).
- **Join** ke dashboard via `product_id` (= ads `item_group_id`, terbukti 100% match 18/18).
- **Idempotent upsert** by `order_id`+`sku_id` (re-sync aman).

## PREREQUISITE (blocker eksternal — di luar kode)

1. **Scope 733764** (Read Seller Affiliate Collaborations) granted di app TikTok. ✅ (sudah dicentang)
2. **Re-authorize tiap toko** dgn scope affiliate included → token baru. Token lama (di-issue sebelum scope) ditolak (401 saat test). **WAJIB sebelum sync jalan.**
3. Approval kategori "Creator Collaboration" — sudah approved.

Tanpa #2, sync 401. Re-auth pakai flow existing `/tp/auth` → `/tp/auth/callback`.

## API: Search Seller Affiliate Orders

```
POST {host}/affiliate_seller/202405/orders/search
Query: app_key, timestamp, shop_cipher, sign, version=202405, page_size, page_token
Header: x-tts-access-token: <seller token, scope 733764>
Body: { } (filter opsional: create_time range, order_status)
```
Response (per dok `Affiliate integration.md` + CSV field): order_id, product_id, sku_id, product_name, payment_amount, quantity, order_status, **creator_username/creator_id**, content_type, content_id (video), commission_rate, est/actual_commission, shop_ads_commission, timestamps.

> Verifikasi field response aktual saat implement (dok tak kasih schema response lengkap; CSV = referensi field). Catat field yang tak match.

## Data Model

Koleksi baru `affiliate_orders` (integration_db):
```
{
  _id:              "<order_id>_<sku_id>",      // idempotent key
  order_id:         string,
  store_id:         string,
  product_id:       string,                      // = ads item_group_id (join hub)
  sku_id:           string,
  product_name:     string,
  payment_amount:   float64,
  quantity:         int,
  order_status:     string,                      // Unpaid/Pending/Settled/...
  creator_id:       string,
  creator_username: string,
  content_type:     string,                      // VIDEO / LIVE
  content_id:       string,                      // video id → join video perf nanti
  commission_rate:  float64,
  est_commission:   float64,
  actual_commission: float64,
  shop_ads_commission: float64,
  order_create_time: time,
  synced_at:        time,
}
```
Index: unique `_id`; `store_id`+`order_create_time`; `product_id`; `creator_id`.

## Backend Components

```
internal/infrastructure/clients/affiliate_client.go (atau extend tiktok_client.go)
  func (c *TikTokClient) SearchSellerAffiliateOrders(ctx, shopCipher, token, appKey, appSecret, pageToken string, createTimeGe/Le int64) (resp, nextToken, error)
    — reuse generateSign + buildQueryString; path /affiliate_seller/202405/orders/search; version=202405

internal/domain/entity/affiliate.go
  AffiliateOrder struct (model di atas)

internal/infrastructure/repository/affiliate_repo.go
  UpsertOrders(ctx, []AffiliateOrder) error      // bulk upsert by _id
  ListOrders(ctx, filter) ([]AffiliateOrder, int64, error)
  AggregateByCreator / ByProduct (untuk dashboard)

internal/usecase/affiliate_usecase.go
  SyncOrders(ctx, storeID, dateRange) (count int, error)   // loop pagination → upsert
  (getStore token via existing GetOrRefreshToken)

internal/worker/tasks/affiliate_orders_sync.go
  Run + Schedule (cron harian, mis. "0 3 * * *" — setelah GMV-max jam 1, integration jam 2)
  loop semua authorized shop → SyncOrders

internal/interface/http/affiliate_handler.go
  GET  /affiliate/orders              list (filter store/date/creator/product)
  GET  /affiliate/orders/sync         manual trigger sync (admin)
  GET  /affiliate/summary/creators    agregat per creator (GMV, komisi, order)
  GET  /affiliate/summary/products    agregat per produk

main.go: wire client+repo+usecase+handler + register task + routes (pola existing)
```

## Dashboard join (Scope 3/4 nanti)

- `affiliate_orders.product_id` == `gmv_max.item_group_id` → laba per produk include komisi affiliate real
- `affiliate_orders.creator_username` → roster + ICC vs eksternal (map ke marketing_team employee)
- `affiliate_orders.content_id` → join video performance (setelah GetShopVideoPerformance di-ingest)
- est vs actual commission → dashboard bedakan (banyak order Unpaid/Pending)

## Verifikasi (saat implement)

1. Re-authorize 1 toko → token fresh scope 733764. Test `SearchSellerAffiliateOrders` return data (bukan 401).
2. Bandingkan hasil API vs CSV `affiliate_orders_*.csv` (802 order) — field + jumlah cocok?
3. `product_id` API == `item_group_id` ads (sudah terbukti 18/18 di CSV).

## Di luar scope

- Creator API (Get Creator Profile, scope 1021508) — butuh creator token terpisah. Roster cukup dari order's creator_username dulu.
- Collaboration management (write: create/edit collab) — scope 890884, fase lain.
- Get Live Room Info (scope 434372) → modul Live, spec terpisah.
- Webhook affiliate real-time — fase lanjut (cron harian dulu).
