## ADR 0009 — Data Affiliate via Search Seller Affiliate Orders API (bukan CSV)

- **Status**: 🟡 Proposed (dok TikTok terverifikasi; terblokir re-authorize toko + konfirmasi app)
- **Tanggal**: 2026-07-01
- **Konteks dok**: [[Microservices - Integration Service]] · [[Microservices - TikTok Shop Service]] · [[Sales - GMV Creative]] · [[ADR - 0008 Profit Engine Join via item_group_id]]

## Context

Toko sudah menjalankan program affiliate TikTok (creator promosi → order + komisi), tapi datanya **tidak ter-capture** di pipeline existing:
- `transaction_orders.income.total_affiliate_commission_fee` = **0** di seluruh order (settlement TikTok mem-*blend* komisi affiliate ke `fee_and_tax_amount`).
- `tt_shop_transaction_by_orders.sku_transactions.fee_tax_breakdown.affiliate_*` = **0** (skema field ada, nilai kosong; 60% statement `sku_transactions` kosong).
- File `affiliate_orders_*.csv` (export manual TikTok Affiliate Center, 802 order Juni) = **bukti** program jalan + **referensi field**, bukan sumber produksi.

Dashboard tab Affiliate #7 butuh: roster creator, komisi per order, GMV affiliate, top creator, ICC-vs-eksternal — semua tak tersedia dari data existing.

## Decision

**Sumber data affiliate = TikTok Shop Affiliate Seller API, bukan import CSV.**

- Endpoint: **`Search Seller Affiliate Orders`** (`POST /affiliate_seller/202405/orders/search`, `version=202405`). Host `open-api.tiktokglobalshop.com` + signing (`x-tts-access-token`, app_key, shop_cipher, sign, timestamp) **sama** dengan client TikTok Shop existing ([[Microservices - Integration Service]]) → reuse `generateSign`/`buildQueryString`.
- Field API = field CSV: order_id, product_id, sku_id, creator_username, content_id (video), commission (est/actual), shop_ads_commission, order_status.
- **Auto-sync** (cron harian, pola `SyncTTBusinessGMVMaxReport`) → koleksi baru `affiliate_orders` (upsert idempotent by order_id+sku_id).
- **Join** ke laba/dashboard via `product_id` == `item_group_id` (terbukti — lihat [[ADR - 0008 Profit Engine Join via item_group_id]]). `creator_username` → roster. `content_id` → video performance.

**Onboarding/scope (dok resmi TikTok):**
- Kategori partner: **App Developer > Creator Collaboration** (TikTok menyamakan Affiliate = Creator Collaboration). Sudah **approved**.
- Scope: **733764 Read Seller Affiliate Collaborations** → Search Seller Affiliate Orders (utama). 434372 Affiliate Information → Get Creator Profile + Get Live Room Info (bonus: kandidat sumber data Live).
- Affiliate API **inactive by default** — perlu apply + approval Account/Partner Manager (dok baris 23).

## Consequences

- **Positif**: data affiliate otomatis (sejalan pola sync ads/order lain), tak manual import; join ke laba per produk via key yang sudah terbukti; membuka roster creator + attribution.
- **Terblokir (prereq eksternal)**:
  1. **Re-authorize tiap toko** — token existing di-issue SEBELUM scope affiliate → uji call `Search Seller Affiliate Orders` mengembalikan **401 "access token invalid"**. Wajib re-auth via flow `/tp/auth`→`/tp/auth/callback` agar token baru meng-include scope 733764.
  2. **Konfirmasi App ID**: app "Creator Collaboration" yang diapprove = App ID sama/beda dengan `TIKTOK_SHOP_APP_ID`? Bila sama → 1 app, 1 re-auth, 1 token (transaction + affiliate). Bila beda → 2 app, token per-app (extend penyimpanan token).
- **Catatan data**: status order CSV mayoritas Unpaid/Pending → komisi sebagian belum final; dashboard bedakan **Est vs Actual commission**.
- **Ads (BC)** = app terpisah (`TIKTOK_BUSINESS_APP_ID`), tak terpengaruh scope affiliate.
- Belum diimplementasi — spec detail: `docs/superpowers/specs/2026-06-30-affiliate-seller-sync-design.md` (di repo bip-erp).

## Dokumen Terkait

Folder `Marketing Dashboard Analysis/`:
- [[2026-06-30-affiliate-seller-sync-design]] — spec auto-sync (client, cron, koleksi affiliate_orders, handler)
- [[2026-07-01-marketing-dashboard-ANALISIS-REKAP]] — index analisis
- [[2026-06-30-marketing-dashboard-MASTER]] — §B4 affiliate lengkap (scope, endpoint, blocker)
- Dok resmi TikTok: [[Affiliate integration]] · [[TikTok Shop Affiliate(Creator Collaboration)Developer onboarding & termination Rules]]
- [[ADR - 0008 Profit Engine Join via item_group_id]] (join via product_id==item_group_id)
