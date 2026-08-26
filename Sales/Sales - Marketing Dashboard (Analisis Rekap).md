# Marketing & Ads Dashboard — Rekap Analisis (Index)

- **Status**: 🟡 **Arsip analisis (30 Juni 2026) — temuan datanya masih sahih, peta service-nya tidak.** Keadaan sekarang: [[Microservices - Marketing Analytics Service]] · [[API - Marketing Analytics Service]]. Latar: [[Sales - Marketing Dashboard (Index)]].

> ⛔ **"~45-50%" di §1 adalah potret 30 Juni 2026.** Lapisan marketing & ads sudah live di PROD sejak Agustus 2026 sebagai service tersendiri `marketing-analytics` (40 route), sementara profit engine + HPP mendarat di `integration` sebagai `/integration/gross-profit`. Jangan mengutip persentase ini sebagai status proyek.
>
> Temuan **data** di bawah (koleksi mana berisi apa, mana yang real vs kosong) tervalidasi ke produksi saat itu dan tak digantikan dokumen mana pun — itulah nilai berkas ini. Untuk cakupan per-metrik yang **terbaru**, pakai [[Sales - Marketing Analytics (Audit Ketersediaan Data)]] (audit 2026-08-09) yang memakai label ADA/RAKIT/TIPIS/TIDAK ADA.

> Rekap lengkap analisis untuk membangun dashboard `10_DASH_MARKETING_ADS.html`.
> Semua temuan tervalidasi **data produksi nyata** (mongosh read-only, integration_db) / **dok resmi TikTok**.
> Dokumen ini = index. Detail per topik di file terkait (link bawah).

## Dokumen terkait

Tautan di bawah semula berupa path berkas dari repo asalnya (`2026-06-30-*.md` di `docs/superpowers/`) yang tak menunjuk apa pun dari dalam vault; sudah diganti wikilink ke salinan vault-nya:

- Roadmap master + engine + join + affiliate: [[Sales - Marketing Dashboard (Master Roadmap)]]
- Profit engine + HPP: [[Sales - Profit Engine (Design)]]
- Affiliate auto-sync: [[Sales - Affiliate Seller Sync (Design)]] · [[Sales - Affiliate Seller Sync (Plan)]]
- Plan HPP master: [[Sales - HPP Master (Plan)]]
- Dok TikTok affiliate: [[Sales - Affiliate Integration (TikTok Docs)]] · [[Sales - TikTok Affiliate Rules (Docs)]]

---

## 1. Progress vs mockup: ~45-50% *(per 30 Juni 2026)*

Banyak komponen SUDAH ADA tapi **tersebar** — reuse, jangan dobel-bangun:
- Settlement/income/return UI → `integration-accurate` (Shopee+TikTok, real)
- KPI/akuntabilitas per orang+tim+video+profit-tier → service `insentive` (`/api/insentive/calculate`)
- Video+creator metrics → `GetShopVideoPerformance` (endpoint ada, belum ingest ke DB)
- Ads (spend/GMV/ROAS) → `tt_business_gmv_max_*` + `shopee_gms_*` (real, sync jalan)
- Transaction/order/settlement → `transaction_orders` 103k (real)

**Gap inti:** HPP + profit-engine + config RAPB.

## 2. Engine dibutuhkan (9)
Baru: Profit → Status(SCALE/JAGA/PERBAIKI/HENTIKAN) → KPI-turunan/funnel/pacing → Attribution → Affiliate-churn.
Reuse: **KPI/Incentive = service `insentive`** (jangan bangun ulang). ⚠️ cek definisi profit di SPVProfitTier insentif sebelum bikin profit-engine (hindari 2 definisi laba tabrakan).
Tak perlu: ads metrics dasar (API sudah hitung).

## 3. Strategi join laba — TERBUKTI data prod (2026-06-30)
- **`item_group_id` (ads gmv_max) == `product_id` (tt_shop order)** — 18/18 CSV & 135/200 sampel match. Join ID-based, bukan fuzzy nama.
- `gmv_max_PRODUCT_reports` KOSONG → pakai `gmv_max_PERFORMANCE_reports` (429k). `item_id` sering -1/0 placeholder → pakai `item_group_id`.
- `line_items.seller_sku` = teks bebas ("DR FAY CREAM") ≠ `items.sku` ("PJB-002") → map via nama.
- Bundle: `items` item_type=BUNDLE sku gabung → handle via bundle_contents.
- **Solusi:** master `items` (87 produk) = mapping hub, +3 field: `product_id`, `seller_sku`, `cost`. Map sekali → join 100% ID-based.

## 4. HPP
Sumber = xlsx Finance (`COGS-per-products (jan-mei2026).xlsx`, 2 sheet Beautyhacks + KY+GB+CRM, kol Produk + HPP/Pcs, Jan-Mei 2026). Pakai HPP Mei utk laba Juni (approval Finance). Bukan di master (cuma base_price).

## 5. Fee/settlement — semua REAL
`transaction_orders.income`: settlement_amount, service_fee, affiliate_comm, ad_cost, discount. Tak perlu config tarif — pakai settlement real. TikTok settlement ad_cost=0 (ad spend dari BC report terpisah; jangan double-count Shopee).

## 6. Target (dari tim)
ROAS ≥ 3.2 (konsisten `GMV_MAX_WINNER_ROI_THRESHOLD` existing), CPA < Rp30.000.

## 7. Affiliate — sumber API (BUKAN CSV)
- Endpoint: `Search Seller Affiliate Orders` (`affiliate_seller/202405/orders/search`, host+signing SAMA `tiktok_client.go`). Butuh `version=202405`.
- Kategori "App Developer > Creator Collaboration" **APPROVED**, scope dicentang.
- Join `product_id` == `item_group_id` (terbukti). Creator username → roster. content_id → video.
- **CSV `affiliate_orders_*.csv` = pembanding/referensi field, BUKAN import.**
- **TEST API GAGAL:** token `tt_shop_credentials` 401 "invalid" (di-issue SEBELUM scope; belum punya affiliate access). `platform_tokens` coll KOSONG. app_key/secret per-store dari coll `credentials` (kosong→env fallback).
- **PREREQUISITE WAJIB: re-authorize tiap toko** via `/tp/auth`→`/tp/auth/callback` → token baru include scope 733764. Tanpa itu semua call 401.

## 8. OAuth affiliate — rekomendasi tak-ribet
Scope nempel ke APP (`service_id`), bukan URL auth (`GetAuthorizeURL` cuma `service_id=app_id`). Idealnya **1 app** (scope affiliate + transaction di app Shop existing) → 1 re-auth → 1 token cover semua. Ads (BC) = app terpisah (`TIKTOK_BUSINESS_APP_ID`), tak terpengaruh. **OPEN: app affiliate (Creator Collaboration) = App ID sama/beda dgn `TIKTOK_SHOP_APP_ID` (75485...)?** Sama→1-app simpel; beda→2-app (extend token per-app).

## 9. Risiko akurasi (dari sesi lain, relevan ke laba)
- **ETL drift:** 364 order hilang dari summary (Rp32.6jt underreport) — rate-limiter skip Upsert. Profit-engine harus sadar data transaction belum 100% lengkap. (Temuan sesi lain *etl-transaction-orders-drift* — belum ada nota terpisah di vault.)
- **Timezone:** revenue beda vs seller center (fixed, date-fns-tz Asia/Jakarta). (Temuan sesi lain *wib-timezone-date-filter* — sudah fixed.)

---

## Scope eksekusi (hulu→hilir)
1. HPP + RAPB/target (RAPB nunggu Finance; HPP/target ada)
2. Profit Engine (join terbukti, no ingest baru)
3. Dashboard tab 1-4 (reuse ads-analytics/accurate)
4. Creative + Creator (wire GetShopVideoPerformance)
5. Marketing/Creator akuntabilitas (reuse insentif)
6. Affiliate (re-auth toko → client+sync)
7. Live (Get Live Room Info — cek detail)
8. RBAC (terakhir)

## Blocker eksternal tersisa
1. Re-authorize toko + konfirmasi App ID affiliate (1 vs 2 app)
2. RAPB Juni per brand — Finance
3. Detail Get Live Room Info (Live)
