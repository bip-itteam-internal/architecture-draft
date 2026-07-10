## ADR 0011 — Integration Read Cache + Singleflight (Fase 1 Optimasi Performa)

- **Status**: ✅ Accepted (disetujui 2026-07-06)
- **Tanggal**: 2026-07-06
- **Konteks dok**: [[Microservices - Integration Service]] · spec: `docs/superpowers/specs/2026-07-06-integration-read-cache-design.md` (repo workspace)

## Context

Endpoint analitik integration service (transaksi order, iklan TikTok, profit, GMS Shopee) menghitung ulang dari data mentah setiap request (compute-on-read). Terukur di prod 2026-07-06:

- `/profit/products` range 6 bulan = **11.2s idle** (5 query berantai; agregasi unwind 297K `transaction_orders` + decode 143K dokumen settlement utuh).
- `/transactions/orders/summary/shops` = 2.6s single → **9.5-10s saat 4-8 request paralel**.
- Lewat timeout wrapper Mongo shared **10s** → HTTP 500; handler berantai lewat timeout gateway **30s** → HTTP 502.
- Index sudah benar (IXSCAN) — bottleneck volume komputasi. Pola gagal dominan: **query identik berjalan paralel** (multi-user), bukan satu query lambat.
- Gateway sengaja meng-exclude modul integration dari cache Redis-nya (`noCacheModules`).

Keputusan produk: toleransi data basi **5-15 menit**; scope semua menu analitik; quick-win dulu, struktural menyusul.

## Decision

**Fase 1:** middleware response-cache **in-service** (`rescache`) di route GET analitik + **singleflight** per cache-key + spot-fix profit (paralelisasi `errgroup` 5 query `GetProductProfit`, projection dokumen settlement).

- Key = `path + query ternormalisasi` (sort param, buang kosong); **tanpa** segmen identitas — hasil audit: satu-satunya GET yang memfilter per-employee adalah `/transactions/master/shops`, dan route itu di-exclude dari cache. Endpoint baru yang membaca header identitas WAJIB keyed-by-employee atau exclude (checklist review PR).
- TTL: 10 menit analitik; 2 menit `orders/list` + `orders/dashboard/summary`. Exclude: non-GET, `*/sync`, `*/direct`, `*/export`, `master/*`, by-id detail, accounts/auth/webhook.
- Invalidasi: TTL murni + endpoint admin `DELETE /cache?prefix=` (flush manual pasca-backfill).
- Degradasi: Redis down → bypass total; hanya 200+JSON ≤1MB yang di-cache; `X-Cache: HIT|MISS` + log hit-rate per 5 menit.

**Fase 2 (keputusan arah, spec terpisah belum ditulis):** pre-agregasi — worker incremental (hari ini + H-1, karena settlement/status order telat datang) materialize summary harian per SKU/shop (sales, settlement; ads sudah granular di `tt_business_gmv_max_performance_reports`); endpoint assembly dari koleksi kecil (milidetik walau range 2 tahun); data mentah tetap sumber kebenaran (summary rebuildable kapan pun). Contoh skema:

```
profit_daily_summary:
{ date: "2026-07-05", sku: "PJG-001", shop_id: "749...",
  quantity: 320, revenue: 24800000, fee: 812000, ads_cost: 95000 }
```

Estimasi: Fase 1 = 1-3 hari; Fase 2 = 1-2 minggu (skema, worker, backfill, rekonsiliasi). Dipisah agar desain rekonsiliasi finansial yang butuh kehati-hatian tidak menyandera perbaikan cepat. Prioritas Fase 2 ditentukan data hit-rate cache Fase 1: hit-rate tinggi (~90%) = urgensi turun; pola filter unik terus (cache jarang kena) = naik.

## Consequences

- ➕ 500/502 praktis hilang untuk trafik nyata: warm <50ms; cold dilindungi singleflight (1 komputasi per kombinasi filter per TTL, bukan N paralel × 10s).
- ➕ Beban Mongo turun drastis → memory pressure host (swap 3.3GB) ikut turun.
- ➕ Satu titik perubahan (middleware), usecase tak disentuh; rollback = cabut middleware; Redis down = degradasi ke perilaku sekarang, bukan insiden baru.
- ➖ Cold hit tetap lambat (profit ~6-7s pertama per kombinasi filter per TTL) — diselesaikan Fase 2, bukan Fase 1.
- ➖ Data basi ≤10 menit di dashboard/laporan (disetujui); `X-Cache` untuk debug keluhan "belum update".
- ➖ Hit rate bergantung pola filter — range unik per user = cold terus; mitigasi nyata di Fase 2.
- ⚠️ **Risiko keamanan #1**: endpoint ber-ACL salah klasifikasi = bocor data antar role → audit eksplisit sudah dilakukan (2026-07-06), guard checklist wajib untuk endpoint baru.
- ⚠️ Memori Redis (kombinasi filter × TTL) → guard skip cache body >1MB (body terbesar terukur 315KB).
- ⚠️ **Risiko utama Fase 2** (dicatat sejak sekarang): angka summary vs data mentah tidak match karena order/settlement telat update — angka finansial wajib cocok 100%; desain wajib menyertakan rekonsiliasi + kemampuan rebuild summary dari mentah.

## Dokumen Terkait

- Spec Fase 1: `docs/superpowers/specs/2026-07-06-integration-read-cache-design.md`
- [[Microservices - Integration Service]] · [[ADR - 0008 Profit Engine Join via item_group_id]]
