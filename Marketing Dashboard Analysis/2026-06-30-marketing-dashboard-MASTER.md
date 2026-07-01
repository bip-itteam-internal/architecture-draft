# Marketing & Ads Command Center — MASTER Roadmap

> Acuan tetap untuk membangun dashboard `10_DASH_MARKETING_ADS.html`.
> Berbasis audit terverifikasi 5 sisi: koleksi `integration_db`, client API existing, API resmi TikTok Shop, FE marketing, FE accurate/incentive.
> Prinsip: **reuse existing dulu, baru bangun yang kurang.** Jangan dobel-bangun.

## Ringkasan eksekutif

Mayoritas data sudah mengalir & sebagian UI sudah ada (tersebar di module accurate + incentive). Kerja utama = **merangkai existing + tambah HPP/laba + wire endpoint yang sudah ada**, bukan ingest ulang. Progress ≈ **45–50%**.

---

## A. EXISTING — sudah jalan (reuse)

### Data (`integration_db`, 49 koleksi)
- `transaction_orders` — order lintas-channel + `income{settlement, ad_cost, service_fee, affiliate_comm, discount}` + buyer city/province + items[sku]
- `tt_business_gmv_max_product_reports` — **spend+GMV+ROI per produk (item_id)**
- `tt_business_gmv_max_performance_reports` — per campaign (data Juni)
- `tt_business_integrated_reports` / `_summary_reports` — ads metrics per-ad + summary advertiser
- `shopee_gms_item_performances` / `_campaign_performances` — ads Shopee
- `shopee_escrow_details`, `tt_shop_transaction_by_orders` — settlement real
- `marketing_teams` / `team_members` / `team_shops` — ACL tim→toko (employee_id)
- `items` — master SKU+nama+base_price (**tanpa HPP**)

### API client existing
- TikTok BC: advertiser, GMV-max report (product+performance), integrated, campaigns, stores
- TikTok Shop: order, settlement (`statement_transactions`), **`GetShopVideoPerformance`** (video+creator open_id/username + GMV/units/CTR — BELUM disimpan/dipakai)
- Shopee: order, escrow, GMS ads, item info
- Accurate: push sales/invoice/return/receipt

### FE existing (REAL)
- `marketing-insight/`: gmv-max, product-performance, customer-demography
- `integration/ads-analytics` (scorecard+chart; chart pakai MOCK_CHART_DATA)
- `integration/teams`, `integration/transactions`
- `integration-accurate/income|sales|return` (Shopee+TikTok) — **net settlement/income/return UI sudah ada**
- `finance/incentive/` — **engine akuntabilitas: role, kpi_metrics, team[], videos[], bobot/target/realisasi, profit_target**

### FE MOCK (perlu diganti)
- `integration/ads-management` → `MOCK_ADS_CONTENT`
- `integration/ads-analytics` chart tab → `MOCK_CHART_DATA`

---

## B. GAP — belum ada

| Gap | Catatan |
|---|---|
| HPP per SKU di `items` | hanya di file xlsx |
| Config RAPB + target | belum ada (target ROAS 3.2 / CPA 30k dari tim) |
| Profit engine (join → laba/margin/status) | belum ada |
| Tab dashboard 1–4 (Ringkasan/Produk-laba/Akun/Kampanye) | belum dirangkai |
| Simpan video performance ke DB + map open_id→employee | endpoint ada, belum disimpan |
| Affiliate client (roster/order/komisi/kolaborasi) | **0 method**; API resmi ADA |
| Live analytics | endpoint tak ketemu — gelap |
| RBAC | belum |

---

## B2. ENGINE yang dibutuhkan mockup

Daftar "otak hitung" yang diminta dashboard. Reuse dulu, baru bangun.

| # | Engine | Untuk tab | Status |
|---|---|---|---|
| 1 | **Profit/Laba** — settlement − HPP − retur − iklan, margin | Produk, Akun, Ringkasan | 🔴 baru (Scope 2) |
| 2 | **KPI/Incentive** — score, tier, conversions per role | Marketing/Creator | ✅ **REUSE** service `insentive` (jangan bangun ulang) |
| 3 | **Status/Rekomendasi** — SCALE/JAGA/PERBAIKI/HENTIKAN, BOOST/FATIGUE/MATIKAN, coaching | Produk, Kampanye, Creative, Marketing | 🔴 baru, rule di atas profit+metrics (Scope 2) |
| 4 | **Funnel/agregasi** — impr→klik→ATC→order→selesai | Ringkasan | 🟡 data ada, agregasi belum (Scope 3) |
| 5 | **KPI turunan** — BE-ROAS, return-rate, iklan%GMV, AOV, freq, watch-rate | Ringkasan, Creative | 🟡 ads metrics ada, turunan belum (Scope 3) |
| 6 | **Pacing** — spend vs RAPB, gauge target ROAS | Ringkasan | 🔴 baru + RAPB (Scope 1/3) |
| 7 | **Attribution** — GMV per creator/video/affiliate | Creator, Creative, Affiliate | 🟡 video-API ada, attribution belum (Scope 4) |
| 8 | **Budget pacing per campaign** — budget/hari, % terpakai | Kampanye | 🟡 spend ada, budget/hari belum (Scope 3) |
| 9 | **Affiliate churn/retensi** — aktif/baru/churn | Affiliate | 🔴 baru + data affiliate (Scope 6) |

**Engine baru yang harus dibangun (urut):** Profit (1) → Status (3) → KPI-turunan/funnel/pacing (4,5,6,8) → Attribution (7) → Affiliate-churn (9).
**Reuse (jangan bangun ulang):** KPI/Incentive (2) = service `insentive` (role: ADV TikTok/Meta/Marketplace, SPV+profit-tier, ICC, Host Live, Affiliate, CRM; endpoint `/calculate`, `/stats`, `/master-kpi`; sudah konsumsi `/integration/shopee/item-performance`).
**Tidak perlu:** ads metrics dasar (spend/roas/ctr/cvr/cpc/cpm) — sudah dihitung TikTok/Shopee API.

⚠️ **Sebelum bangun Profit engine (1):** cek dulu definisi profit di `insentive` SPVProfitTier — supaya konsisten, bukan bikin formula laba tandingan.

## B4. AFFILIATE — sumber = CSV upload (TERVALIDASI 2026-06-30)

Affiliate commission di settlement/order = **0 semua** (skema `sku_transactions.fee_tax_breakdown.affiliate_*` ada tapi nilai 0; 60% statement sku_transactions kosong). **Data affiliate REAL ada di CSV export TikTok Affiliate** (dari tim marketing): `affiliate_orders_*.csv`, 802 order Juni.

**Field CSV:** Order ID, **Product ID**, Product Name, SKU ID, Payment Amount, Quantity, Order Status, **Creator Username**, Content Type, **Content ID** (video), commission model, Standard commission rate, Est/Actual Commission Payment, Shop Ads commission, co-funded bonus, timestamps, Platform (TTS/TT_LITE).

**Join TERBUKTI:** CSV `Product ID` == ads `item_group_id` = **18/18 (100%)**. Maka CSV nyambung ke profit-engine via hub yang sama (B3). `Creator Username` = roster (apexlvg_, luminaaa_care.id, bharaskin, dst). `Content ID` = video ID → join ke video performance (tapi koleksi video BELUM di-ingest).

**Unlock:** buka tab Affiliate #7 (roster/komisi/GMV/top-creator/ICC-vs-eksternal) + masuk profit-engine + creator attribution. Tab Creative #6 butuh wire `GetShopVideoPerformance` dulu (koleksi video belum ada).

**SUMBER PRODUKSI = API, BUKAN CSV.** CSV = bukti + referensi field (export manual dari API yang sama). Endpoint+scope RESMI (dari docv2/page/affiliate-integration, dibaca via Playwright):

| Scope ID | Scope Name | API yang dipakai |
|---|---|---|
| **733764** | **Read Seller Affiliate Collaborations** | **Search Seller Affiliate Orders** ← sumber utama (order+komisi+creator+product), Seller Search Affiliate Open Collaboration Product |
| 434372 | Affiliate Information | Get Creator Profile (roster), **Get Live Room Info** (← petunjuk data LIVE), Get Shop Products |
| 890884 | Manage Seller Affiliate Collaboration | Create Open/Target Collab, Generate Promotion Link (write — opsional) |
| 1021508 | Read Creator Affiliate Collaborations | Search Creator Affiliate Orders (butuh Creator token terpisah) |

**Untuk dashboard #7 cukup: scope 733764 → `Search Seller Affiliate Orders`** (Seller Center token). Field = persis CSV (Product ID, Creator, Content ID, commission, status). Opsional 434372 untuk Get Creator Profile + Get Live Room Info.

**Catatan auth:** Seller API pakai Seller Center token (sudah ada pola). Creator API butuh token terpisah + kirim 14-char key ke partner manager TikTok (creator authorization) — TIDAK perlu untuk Seller Affiliate Orders.

**Endpoint resmi (dok `docs/superpowers/Affiliate integration.md`):**
- Host `open-api.tiktokglobalshop.com`, base `affiliate_seller/202405/` (& `affiliate_creator/202405/`) — **sama host + sama signing (x-tts-access-token + app_key + shop_cipher + sign + timestamp) dgn tiktok_client.go existing.**
- `Search Seller Affiliate Orders` = sumber utama (order affiliate juga muncul di Seller Center order biasa, 1 jam hold).
- Seller token (pola ADA) cukup utk dashboard. Creator token (Search Creator Affiliate Orders, Get Creator Profile) = opsional, butuh creator authorize + 14-char app_key ke partner manager.

**Client kosong (0 method affiliate)** → bangun `SearchSellerAffiliateOrders` + cron + koleksi `affiliate_orders` + repo. Implementasi cepat krn signing/host sama existing.

**BLOCKER NYATA (eksplisit di dok baris 23):** "Affiliate API is **inactive by default**, partner/ISV **harus APPLY for access + APPROVAL Account/Partner Manager**." Plus: daftar kategori partner **App developer > Customer Engagement > Affiliate**, bikin app **Affiliate (public)** + compliance review. **Bukan sekadar centang scope — butuh apply+approval TikTok.** Ini PR eksternal, bisa makan waktu.

**Bonus:** `Get Live Room Info` (scope 434372) = kandidat sumber LIVE (tab #7) — perlu cek detail endpoint, tapi tak gelap total.

**Catatan:** status order CSV mayoritas Unpaid(431)/Pending(269) → komisi sebagian belum final; dashboard bedakan Est vs Actual.

## C. API resmi TikTok (referensi sumber gap)

- **Affiliate Seller API ADA**: Open/Target Collaboration, Affiliate Orders, search creator, Get Payments, affiliate webhook (beta). Butuh **scope app** + client baru. (Catatan: "Creator Search Affiliate Trace Orders" pensiun 2026-08-15 — pakai endpoint baru.)
- Webhook `(17) Shoppable Content Posting` sudah dimiliki (creator_open_id + content_id video/live).
- **Live analytics**: tak terkonfirmasi di partner docs — perlu riset.

Sumber: partner.tiktokshop.com/docv2 (affiliate-seller-api-overview, new-apis-and-webhook-for-affiliates-beta, access-scope).

---

## B3. STRATEGI JOIN — TERVALIDASI DATA NYATA (cek 2026-06-30, baca DB prod read-only)

**Hop 1 ads↔order: TERBUKTI ID-based.** `gmv_max_performance_reports.dimensions.item_group_id` == `tt_shop_order_details.line_items.product_id`. Sampel: 200 product_id ∩ 297 item_group_id → **135 overlap**, format ID identik. Join ads-spend ke order VALID via product_id (bukan fuzzy nama).

**Fakta dari data prod (87 items, integration_db):**
- `gmv_max_PRODUCT_reports` = **KOSONG (0 doc)**. Yang terisi = `gmv_max_PERFORMANCE_reports` (429k). **Pakai performance_reports** (item_group_id + metrics.cost/gross_revenue), bukan product report.
- `item_id` ads sering `-1`/`0` (placeholder). **Pakai `item_group_id`, abaikan item_id.**
- `line_items.seller_sku` = **teks bebas** ("DR FAY CREAM","EWA"), BUKAN kode. `items.sku` = kode ("PJB-002"). **seller_sku ≠ items.sku** → map via nama/manual.
- Bundle: `items` punya item_type BUNDLE, sku gabung ("PJB-001 + PJB-002"). Handle terpisah (pecah ke komponen via bundle_contents, jumlah HPP).
- store_products.title = nama listing panjang ("FLO Hair Growth Shampoo...BPOM") ≠ items.name ("Glossmen") → fuzzy nama RAPUH.

**Rantai join final:**
```
ad-spend (performance, item_group_id)
   ↓ item_group_id == items.product_id        ✅ ID-based (terbukti)
master items {product_id, sku, seller_sku, cost}
   ↑ seller_sku == line_items.seller_sku       (teks, di-map sekali)
order/settlement (tt_shop_order_details)
   → cost/HPP dari items
```

**SOLUSI: master `items` jadi mapping hub. Tambah 3 field:** `product_id` (=TikTok Shop product_id=ads item_group_id), `seller_sku` (teks yg dipakai order), `cost` (HPP). Map sekali untuk 87 produk → join 100% ID-based sesudahnya. Bundle ditangani via bundle_contents.

**#3 Periode — OK.** performance_reports punya stat_time_day → iris Juni bisa. HPP Mei→Juni = asumsi, approval Finance. Settlement-lag = risiko terbuka.

## D. Scope (hulu → hilir)

| Scope | Sifat | Reuse | Blocker |
|---|---|---|---|
| **1. HPP + RAPB/target** | baru tipis | `items`, settlement | RAPB nunggu Finance (HPP✅ xlsx, target✅ 3.2/30k) |
| **2. Profit Engine** | join (no ingest baru) | gmv-max product report, transaction income, settlement | — |
| **3. Dashboard tab 1–4** | FE + endpoint | ads-analytics, product-performance, integration-accurate | — |
| **4. Creative + Creator** | wire `GetShopVideoPerformance` → simpan → FE; ganti MOCK_ADS_CONTENT | video API existing, incentive videos[] | map open_id→employee |
| **5. Marketing/Creator akuntabilitas** | reuse incentive engine + ACL | **finance/incentive**, marketing_teams | perluas role/mapping |
| **6. Affiliate** | client baru (API resmi ada) | komisi total existing (sbg biaya) | **konfirmasi scope app** |
| **7. Live** | riset dulu | — | sumber gelap |
| **8. RBAC** | tata kelola | — | terakhir (belum urgent) |

Urutan: **1 → 2 → 3** (jalur utama, no blocker selain RAPB) → 4/5 paralel → 6 (saat scope dikonfirmasi) → 7 riset → 8 akhir.

---

## E. Aksi konfirmasi (tim/kamu)

1. **Finance**: RAPB Juni 2026 per brand (plafon ads). [Scope 1]
2. **TikTok App owner**: app punya scope **Affiliate Seller API**? [Scope 6]
3. **Riset**: sumber Live analytics — ada API/export? [Scope 7]

## F. Input tim yang SUDAH masuk
- ✅ HPP per SKU (xlsx Jan–Mei 2026) → pakai HPP Mei untuk laba Juni
- ✅ Target: ROAS ≥ 3.2, CPA < Rp30.000 (default global)

---

## G. Jangan dobel-bangun (pengingat)
- Net settlement/income/return: **sudah ada UI** di integration-accurate — reuse, jangan rebuild.
- Akuntabilitas per orang/tim + KPI + video + profit: **incentive engine sudah ada** — sambungkan ke dashboard marketing, jangan bikin engine kedua.
- Video+creator metrics: endpoint `GetShopVideoPerformance` sudah ada — wire, jangan cari API lain.

## H. Progress
≈ **45–50%** dari visi mockup. Naik dari estimasi awal (35%) karena video/creator+affiliate ada jalur resmi & akuntabilitas/settlement sudah ada di module lain.
