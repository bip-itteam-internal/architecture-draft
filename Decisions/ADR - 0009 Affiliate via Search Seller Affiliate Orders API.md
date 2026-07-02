## ADR 0009 — Data Affiliate via Search Seller Affiliate Orders API (bukan CSV)

- **Status**: ✅ Implemented (terverifikasi live 2026-07-01: re-auth toko OK, 95 order tertarik ke `affiliate_orders`)
- **Tanggal**: 2026-07-01 (impl 2026-07-02)
- **Konteks dok**: [[Microservices - Integration Service]] · [[Microservices - TikTok Shop Service]] · [[Sales - GMV Creative]] · [[ADR - 0008 Profit Engine Join via item_group_id]]

## Context

Toko sudah menjalankan program affiliate TikTok (creator promosi → order + komisi), tapi datanya **tidak ter-capture** di pipeline existing:
- `transaction_orders.income.total_affiliate_commission_fee` = **0** di seluruh order (settlement TikTok mem-*blend* komisi affiliate ke `fee_and_tax_amount`).
- `tt_shop_transaction_by_orders.sku_transactions.fee_tax_breakdown.affiliate_*` = **0** (skema field ada, nilai kosong; 60% statement `sku_transactions` kosong).
- File `affiliate_orders_*.csv` (export manual TikTok Affiliate Center, 802 order Juni) = **bukti** program jalan + **referensi field**, bukan sumber produksi.

Dashboard tab Affiliate #7 butuh: roster creator, komisi per order, GMV affiliate, top creator, ICC-vs-eksternal — semua tak tersedia dari data existing.

## Decision

**Sumber data affiliate = TikTok Shop Affiliate Seller API, bukan import CSV.**

- Endpoint: **`Search Seller Affiliate Orders`** (`POST /affiliate_seller/202410/orders/search`). ⚠️ **Versi = 202410** (terverifikasi live, bukan 202405 seperti draft awal — versi 202405 mengembalikan error `36009004 "Invalid API version"`; endpoint affiliate lain seperti `open_collaborations` tetap 202405, jadi versi beda per-endpoint). Versi HANYA di path, **tanpa** query param `version` (param version juga memicu 36009004). Host `open-api.tiktokglobalshop.com` + signing (`x-tts-access-token`, app_key, shop_cipher, sign, timestamp) **sama** dengan client TikTok Shop existing ([[Microservices - Integration Service]]) → reuse `generateSign`/`buildQueryString`. Batas TikTok: rentang query max **3 bulan**.
- Response 2-level: order (`id`, `create_time`, `delivery_time`) berisi `skus[]`; detail affiliate per-SKU (creator_username, content_id/type, commission_model/rate, price, est/actual commission = object `{amount,currency}`, settlement_status). **Tak ada** product_name/creator_id.
- **Auto-sync** (cron per 8 jam `"0 0 0,8,16,23 * * *"`, seragam dengan ads GMV-max) → koleksi baru `affiliate_orders` (upsert idempotent by order_id+sku_id). Rate limiter (30 req/s) + guard sku_id kosong + error isolated per-shop.
- **Join** ke laba/dashboard via `product_id` == `item_group_id` (terbukti — lihat [[ADR - 0008 Profit Engine Join via item_group_id]]). `creator_username` → roster. `content_id` → video performance.

**Onboarding/scope (dok resmi TikTok):**
- Kategori partner: **App Developer > Creator Collaboration** (TikTok menyamakan Affiliate = Creator Collaboration). Sudah **approved**.
- Scope: **733764 Read Seller Affiliate Collaborations** → Search Seller Affiliate Orders (utama). 434372 Affiliate Information → Get Creator Profile + Get Live Room Info (bonus: kandidat sumber data Live).
- Affiliate API **inactive by default** — perlu apply + approval Account/Partner Manager (dok baris 23).

## Consequences

- **Positif**: data affiliate otomatis (sejalan pola sync ads/order lain), tak manual import; join ke laba per produk via key yang sudah terbukti; membuka roster creator + attribution.
- **Prereq eksternal — RESOLVED**:
  1. **Re-authorize toko — SELESAI**. Token lama di-issue sebelum scope → 401. Setelah re-auth, call `Search Seller Affiliate Orders` balik **200 OK** (verifikasi: toko Glowbooster.Store, backfill 89 hari → 95 order). ⚠️ Catatan: field `scopes` di `tt_shop_credentials` di-hardcode `[]` (tiktok_usecase.go), jadi **tak bisa** dipakai cek grant — hanya API call yang membuktikan.
  2. **App ID** = sama dengan `TIKTOK_SHOP_APP_ID` (1 app, 1 token untuk transaction + affiliate) — terkonfirmasi via test call sukses pakai token store existing.
- **Isolasi**: `affiliate_orders` = koleksi terpisah dari `transaction_orders` (terverifikasi: 113rb transaction utuh). 1 order affiliate juga ada di transaction_orders → **link via order_id**, bukan campur.
- **Catatan data**: status settlement mayoritas belum final → dashboard bedakan **Est vs Actual commission**.
- **Ads (BC)** = app terpisah (`TIKTOK_BUSINESS_APP_ID`), tak terpengaruh scope affiliate.
- **Implementasi** (repo bip-erp, service integration): client `affiliate_client.go`, entity `affiliate.go`, repo `affiliate_repo.go` (upsert + aggregate totals/creator/product), usecase `affiliate_usecase.go`, cron task `affiliate_orders_sync.go` + weekly refresh `affiliate_orders_refresh.go` (Minggu 02:00, window 89h — update settlement_status/actual_commission order lama; API hanya filter create_time, order settle ~90h; spec: `docs/superpowers/specs/2026-07-02-affiliate-status-refresh-design.md`) + validasi komisi harian `affiliate_commission_validate.go` (cross-check finance statement lokal, spec: `docs/superpowers/specs/2026-07-03-affiliate-commission-validation-design.md`; bukti: 939/943 sample match <Rp1, 0 mismatch), handler `affiliate_handler.go` (`GET /affiliate/orders`, `/summary/{totals,creators,products}`). FE: modul `marketing-insight/affiliate` ([[APP - Web ERP]]). Spec: `docs/superpowers/specs/2026-06-30-affiliate-seller-sync-design.md`.

## Dokumen Terkait

Folder `Marketing Dashboard Analysis/`:
- [[2026-06-30-affiliate-seller-sync-design]] — spec auto-sync (client, cron, koleksi affiliate_orders, handler)
- [[2026-07-01-affiliate-seller-sync-plan]] — **plan implementasi** (bite-sized, 7 task; token via GetOrRefreshToken karena token DB stale)
- [[2026-07-01-marketing-dashboard-ANALISIS-REKAP]] — index analisis
- [[2026-06-30-marketing-dashboard-MASTER]] — §B4 affiliate lengkap (scope, endpoint, blocker)
- Dok resmi TikTok: [[Affiliate integration]] · [[TikTok Shop Affiliate(Creator Collaboration)Developer onboarding & termination Rules]]
- [[ADR - 0008 Profit Engine Join via item_group_id]] (join via product_id==item_group_id)
