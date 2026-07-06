# Profit Engine + HPP Master — Design (Fase 1)

> Spec ini fondasi dashboard "Marketing & Ads Command Center" (mockup `10_DASH_MARKETING_ADS.html`).
> Fase 1 = laba after-ads real per produk/akun + KPI ringkasan + HPP master. Modul Creator/Affiliate/Live + RBAC = fase lanjut.

## Problem

Mockup menampilkan **laba after-ads** (laba kontribusi) per produk/akun/brand: GMV − biaya marketplace − promo = Net Settlement, lalu − HPP − retur − iklan = Laba. Saat ini:
- Fee/settlement/retur **sudah real** di `TransactionIncome` (TikTok + Shopee settlement).
- Ad spend per produk **sudah real** di `TiktokBusinessGMVMaxProductReport.Cost` (dimensi `ItemID`). Shopee ad spend inline di settlement.
- **HPP/COGS belum ada** di master `items` (hanya `BasePrice` = harga jual). HPP hanya di file `COGS-per-products (jan-mei2026).xlsx`.
- FE `product-performance` hanya tampil spend+roas — tak ada kolom laba/net/HPP/retur.

Engine laba (join 3 sumber + HPP) + tab HPP master + tab dashboard belum ada.

## Decisions (locked)

- **Visual**: samakan layout mockup, TAPI **prioritas fungsi & data real**, bukan styling. Pakai komponen/style FE existing (shadcn + Tailwind + pola `features/marketing-insight`). Mock = referensi layout, bukan CSS.
- **Backend**: ikut pola existing service `integration` (handler/usecase/repo, naming route).
- **Upload**: ikut pola `demography-csv-upload` (multipart `file`, modal, `axiosInstance`, summary `{inserted,updated}` + list error). HPP tambahan: **preview → commit** karena mengubah angka laba (sensitif).
- **Naming & i18n**: label Bahasa Indonesia, konsisten modul `marketing-insight`.
- **Join ad-spend**: **per produk via `ItemID`** (data sudah granular per produk — tidak perlu alokasi proporsional).
- **HPP storage**: field baru `Cost` di master `items` (bukan koleksi config terpisah) — SKU+nama sudah ada di sana.
- **Match nama xlsx → SKU**: normalize + fuzzy/contains, hasil `matched/ambiguous/unmatched`, preview sebelum commit.
- **Periode**: HPP xlsx Jan–Mei 2026; pakai **HPP Mei** untuk laba Juni (HPP stabil). Upload bisa update kapan saja.
- **RAPB/target**: config per brand, bulanan. **Default target (dari tim): ROAS ≥ 3.2, CPA < Rp30.000.** ROAS 3.2 konsisten dgn `GMV_MAX_WINNER_ROI_THRESHOLD` existing di FE. Config bisa override per brand/campaign; bila kosong → pakai default ini.

## Formula Laba

Per produk (`ItemID`/SKU), per periode:
```
GMV            ← GMVMaxProductReport.GrossRevenue  (atau transaction TotalBasePrice)
SpendIklan     ← GMVMaxProductReport.Cost          (TikTok, per produk, real)
                 + Shopee: TotalAdvertisingCost     (inline di settlement)
NetSettlement  ← TransactionIncome.TotalSettlementAmount  (real)
Retur          ← ReturnedRevenue                    (real)
HPP            ← items.Cost × qty terjual           (dari xlsx)

Laba = NetSettlement − HPP − Retur − SpendIklan(TikTok bila belum di settlement)
Margin = Laba / GMV
```
Catatan: TikTok settlement `TotalAdvertisingCost = 0` (ad cost di BC report terpisah) → join tambahkan. Shopee ad cost sudah di settlement → jangan double-count.

## Risiko (verifikasi saat implementasi)

- Align `ItemID` (GMV-max) ↔ `product_id`/SKU di `transaction` ↔ SKU master `items`. Bila tak align → butuh mapping; dilaporkan, bukan disembunyikan.
- Nama produk xlsx ("Glossmen") ≠ nama listing ("Glossmen Lip Serum") → fuzzy match + preview manual.

---

## Backend

### 1. Master items + HPP

Field baru di `entity.ItemProduct`:
```go
Cost float64 `json:"cost" bson:"cost,omitempty"` // HPP per pcs
```

Endpoints (group `/items` atau modul master existing):
```
GET  /items/hpp              list { sku, name, brand, base_price, cost, status }  (status: filled/empty)
POST /items/hpp/upload       multipart file=xlsx → parse → fuzzy match → return preview (TIDAK tulis DB)
POST /items/hpp/commit       body = hasil preview yang dikonfirmasi → upsert items.Cost
POST /items/hpp/:sku         edit manual 1 HPP (koreksi)
```

**Upload flow:**
1. `POST /upload` multipart `file` (xlsx). Parse sheet (kol A=Produk, kol B=HPP/Pcs). Skip baris header/kosong.
2. Normalize nama (lowercase, trim, buang simbol) → match ke `items.Name`.
3. Return preview JSON:
   ```
   {
     matched:    [{ xlsx_name, sku, item_name, current_cost, new_cost }],
     ambiguous:  [{ xlsx_name, new_cost, candidates: [{sku, item_name}] }],
     unmatched:  [{ xlsx_name, new_cost }]
   }
   ```
4. User koreksi ambiguous/unmatched di FE (pilih SKU / abaikan).
5. `POST /commit` dengan list final `[{sku, cost}]` → upsert `items.Cost`. Return `{updated}`.

### 2. Config RAPB + target

Koleksi baru `marketing_budget`:
```
{ _id, period: "YYYY-MM", brand, plafon_ads_rp, target_roas, target_cpa, created_at, updated_at }
// default bila record kosong: target_roas = 3.2, target_cpa = 30000
```
```
GET  /config/budget?period=YYYY-MM
POST /config/budget    upsert per (period, brand)
```

### 3. Profit engine (agregator read-time, tidak simpan koleksi hasil)

```
GET /report/profit/summary?period=&brand=&platform=
    → { spend, gmv, roas, net_revenue, laba, margin, be_roas, return_rate, ads_pct_gmv,
        order, unit, impr, reach, ctr, cvr, cpc, cpm, cpa, aov,
        funnel:{impr,click,atc,order,completed},
        pacing:{spend, plafon}, target_roas, mix_platform:[{platform,pct}] }

GET /report/profit/products?period=&brand=&platform=&sort=
    → rows: [{ sku, name, brand, platform, gmv,
               komisi, layanan, admin, ongkir, voucher, affiliate,   // biaya marketplace+promo (dari settlement)
               net_settlement, hpp, retur, iklan, laba, margin, status }]
      status: SCALE | JAGA | PERBAIKI | HENTIKAN

GET /report/profit/product/:sku?period=
    → waterfall 1 produk (GMV → semua potongan → net → hpp/retur/iklan → laba)

GET /report/profit/accounts?period=&platform=
    → rows per akun/toko: { account, platform, brand, spend, gmv, roas, order, aov,
                            return_rate, net_revenue, laba, status }
```

**Status rule** (threshold di config budget; default ROAS≥3.2, CPA<Rp30.000):
```
SCALE    : margin ≥ 30% & ROAS ≥ target_roas (3.2)
JAGA     : margin 15–30%  (atau ROAS < target tapi laba masih positif)
PERBAIKI : margin > 0 & (return_rate > 15% atau CPA ≥ target_cpa Rp30.000)
HENTIKAN : laba < 0
```
Target dipakai juga di: Ringkasan (gauge ROAS vs 3.2, badge CPA), Kampanye (target vs aktual), Marketing (status per orang vs target).

Reuse agregasi existing (`ListSummaryGroupByProduct`, GMV-max report repo) sebisa mungkin; profit = layer hitung di atasnya.

---

## Frontend

Lokasi: tab di `/marketing-insight` (ikut struktur feature-folder existing: `types/constants/utils/hooks`). Komponen pakai shadcn + reuse `ads-analytics` (date filter, advertiser/shop select, column toggle) bila cocok.

Tab Fase 1:
1. **Ringkasan** — scorecard penuh (spend, GMV, ROAS, net-rev, laba after-ads, BE-ROAS, retur%, iklan%GMV, order, unit, impr, reach, CTR, CVR, CPC, CPM, CPA, AOV), funnel akuisisi, pacing budget vs RAPB, gauge target ROAS, mix spend platform.
2. **Per Produk · laba after-ads** — tabel grup-biaya (komisi/layanan/admin/ongkir/voucher/affiliate/net/HPP/retur/iklan/laba/margin/status) + waterfall per produk (klik baris).
3. **Per Akun & Channel** — tabel laba per toko.
4. **Per Kampanye** — pacing + target + status. Tombol pause/edit budget = disabled (placeholder, butuh write-API TikTok).
5. **HPP Master** (tab baru) — tabel SKU+nama+brand+HPP+status, tombol **Upload xlsx** (modal), preview matched/ambiguous/unmatched, konfirmasi commit, edit inline per baris.

Data via `axiosInstance` ke endpoint backend. Loading/error/empty state ikut pola existing.

---

## Di luar Fase 1 (YAGNI / fase lanjut)

- Tab Per Marketing/Creator, Creative real, Affiliate & Live — butuh scope TikTok (Creator Collab / Affiliate / Live API) + mapping creator → employee. Konfirmasi scope dulu.
- RBAC (hak akses per peran) — paling akhir.
- Tombol pause/edit budget aktif — butuh TikTok/Shopee write-API.
- Breakdown komisi-platform vs layanan terpisah bila settlement detail mendukung (kalau tidak, tampil layanan gabungan).

## Input dari tim lain (sudah/akan)

- ✅ HPP per SKU — file xlsx (Jan–Mei 2026), via upload.
- ⏳ RAPB Juni 2026 per brand — Finance.
- ✅ Target (dari tim): **ROAS ≥ 3.2, CPA < Rp30.000** (default global; per-brand override opsional nanti).
