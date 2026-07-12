## ADR 0008 — Profit Engine: Join Laba per Produk via `item_group_id`

- **Status**: ✅ Implemented (2026-07-04, mekanisme data model BERBEDA dari rencana persis — lihat *Catatan Implementasi* di bawah) — diperluas multi-channel (Shopee) + fitur Cash Flow 2026-07-10, lihat [[Microservices - Integration Service]] §Gross Profit per Product
- **Tanggal**: 2026-07-01
- **Konteks dok**: [[Microservices - Integration Service]] · [[Sales - GMV Creative]] · [[DB - Data Dictionary]] · [[ADR - 0001 Akuntansi via Accurate]]

## Context

Dashboard "Marketing & Ads Command Center" (mockup `10_DASH_MARKETING_ADS.html`) butuh **laba after-ads per produk**: `Net Settlement − HPP − retur − iklan`, plus margin & status (SCALE/JAGA/PERBAIKI/HENTIKAN). Semua komponen mengalir di `integration_db`, TAPI tersebar di koleksi berbeda dengan **key produk yang tidak seragam**:

- **Ad spend per produk** — `tt_business_gmv_max_performance_reports` (429k doc). Dimensi: `item_group_id`, `item_id`, `campaign_id`. **Tidak ada SKU.** `item_id` sering `-1`/`0` (placeholder). `tt_business_gmv_max_product_reports` **KOSONG** (0 doc).
- **Order + settlement** — `tt_shop_order_details.line_items`: `product_id`, `sku_id`, `seller_sku`, `product_name`. `transaction_orders.income`: settlement_amount, service_fee, affiliate_comm, ad_cost, discount (semua real).
- **Master produk** — `items` (87 doc): key `sku` (mis. "PJB-002"), `name`, `base_price`, `item_type` (BASE/BUNDLE), `bundle_contents`. **Tanpa** `product_id`, **tanpa** HPP/cost.
- **HPP** — hanya di file xlsx Finance (`COGS-per-products (jan-mei2026).xlsx`), key = nama produk.

Masalah: menyambungkan ad-spend (item_group_id) → order → HPP tidak ada satu key seragam. Naif "item_id == SKU" **salah** (dibuktikan: field beda, item_id placeholder).

## Decision

**Verifikasi data produksi (mongosh read-only, 2026-06-30):**
- **`item_group_id` (ads gmv_max) == `product_id` (tt_shop order line_items)** — TERBUKTI: sampel 200 product_id ∩ 297 item_group_id → **135 overlap**; via CSV affiliate 18/18 (100%). Format ID identik.
- `line_items.seller_sku` = **teks bebas** ("DR FAY CREAM") ≠ `items.sku` (kode "PJB-002").

**Keputusan:**
1. **Join key produk = `item_group_id` (ads) ↔ `product_id` (order/shop).** ID-based, bukan fuzzy `product_name`. Abaikan `item_id` (placeholder). Pakai `gmv_max_PERFORMANCE_reports` (bukan product_reports yang kosong).
2. **Master `items` jadi mapping hub.** Tambah 3 field: `product_id` (= item_group_id), `seller_sku` (teks di order), `cost` (HPP). Isi sekali untuk 87 produk → join runtime 100% ID-based.
3. **HPP masuk lewat `items.cost`** (upload xlsx → fuzzy-match nama → SKU → preview → commit). Bukan koleksi config terpisah.
4. **Fee/settlement pakai nilai real** dari `transaction_orders.income` — **tidak** membuat config tarif. Selaras [[ADR - 0001 Akuntansi via Accurate]] (bip-erp tidak membangun akuntansi; laba = laba kontribusi operasional, bukan GL).
5. **Bundle** (`item_type=BUNDLE`, sku gabung) ditangani via `bundle_contents` (pecah ke komponen, jumlah HPP).
6. **Profit engine = agregator read-time** di atas data existing (join, bukan re-ingest). Endpoint baru `/report/profit/*`.

## Consequences

- **Positif**: join stabil ID-based & auditable; tak ada fuzzy-nama saat runtime; reuse settlement real (tak duplikasi definisi biaya); master items jadi satu sumber kebenaran mapping.
- **Beban**: perlu isi 3 field mapping untuk 87 produk (sekali, sebagian auto dari order via seller_sku); HPP butuh input Finance (xlsx) + approval periode (HPP Mei dipakai untuk laba Juni = asumsi bisnis).
- **Risiko akurasi**: data `transaction_orders` belum tentu 100% lengkap — ada **ETL drift** (order raw hilang dari summary, rate-limiter skip Upsert; underreport). Laba engine harus sadar ini; angka laba per produk dipakai keputusan SCALE/HENTIKAN → verifikasi kelengkapan data dulu.
- **TikTok settlement `ad_cost=0`** (ad spend dari BC report terpisah); Shopee ad_cost inline di settlement → engine **channel-aware** agar tak double-count.
- ~~Belum diimplementasi~~ — sudah diimplementasikan, lihat *Catatan Implementasi* di bawah. Spec awal: `docs/superpowers/specs/2026-06-30-profit-engine-design.md` (di repo bip-erp, di luar vault).

## Catatan Implementasi (2026-07, grounded ke kode `bip-erp/services/integration`)

- **Join key `item_group_id`↔`product_id` (keputusan inti #1) — DIPERTAHANKAN persis**: tervalidasi masih dipakai di `usecase/profit_usecase.go` (`SumGMVMaxCostByItemID` match `dimensions.item_group_id` vs daftar item_id dari mapping); komentar kode eksplisit mengonfirmasi `item_group_id` = ID produk, `item_id` = level kreatif — sama seperti temuan ADR ini.
- **Mekanisme data model (keputusan #2–3) — BERBEDA dari rencana**: ADR ini semula memutuskan menambah 3 field (`product_id`, `seller_sku`, `cost`) ke koleksi master `items`, menjadikannya "mapping hub" tunggal, dengan HPP masuk lewat `items.cost`. Implementasi aktual TIDAK melakukan ini — `entity.ItemProduct` tetap seperti semula (tanpa field itu). Sebagai gantinya dibuat **2 koleksi baru terpisah**: `product_costs` (HPP per produk per `effective_from`, dari upload xlsx) + `product_sku_mappings` (SKU↔item_id↔produk, identitas `master_sku`, 1 SKU boleh multi-baris utk multi-toko/bundle). Detail lengkap mekanisme aktual: [[Microservices - Integration Service]] §Gross Profit per Product.
- **Anti-double-count channel-aware (keputusan #4/Consequences) — DIPERTAHANKAN & diperluas**: "Shopee ad_cost inline di settlement → engine channel-aware" (poin Consequences di atas) terpakai persis — agregasi settlement Shopee sengaja mengabaikan `TotalAdvertisingCost` per-item karena sudah inline di `income.total_settlement_amount`.
- **Diperluas multi-channel (Shopee, 2026-07)**: ADR ini & desain awal murni TikTok. Engine kini menghitung Shopee **terpisah** (bukan gabung ke TikTok) dengan aturan settlement sendiri (tak ada koleksi settlement per-SKU terpisah spt TikTok; income Shopee level-order, diprorata). Detail: [[Microservices - Integration Service]] §Gross Profit per Product.
- **Diperluas fitur Cash Flow (Sudah Cair/Uang Gantung/Rincian per toko, 2026-07-10)**: fitur baru di atas fondasi ADR ini, juga channel-aware TikTok/Shopee. Tidak diputuskan/disebut di ADR ini (dibuat belakangan). Detail: [[Microservices - Integration Service]] §Gross Profit per Product, endpoint: [[API - Integration Service]].

## Dokumen Terkait

Analisis lengkap dashboard Marketing & Ads (folder `Marketing Dashboard Analysis/`):
- [[2026-07-01-marketing-dashboard-ANALISIS-REKAP]] — **index** (baca dulu)
- [[2026-06-30-marketing-dashboard-MASTER]] — roadmap 8 scope + 9 engine + join + affiliate
- [[2026-06-30-profit-engine-design]] — spec profit engine + HPP
- [[2026-06-30-hpp-master-plan]] — plan HPP master (field cost + upload xlsx)
- [[ADR - 0009 Affiliate via Search Seller Affiliate Orders API]]
