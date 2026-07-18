> **Status**: ⚠️ Implemented (tool + planner sudah di kode & tervalidasi dry-run 2026-07-17: 7.339 order target/8 toko; **eksekusi write ke prod belum dijalankan** — butuh kredensial Shopee prod + service hidup). Grounded ke [[Microservices - Integration Service]] (§*Observability & Ketahanan Shopee* → butir `shipped_at` = `pickup_done_time`).

## Tujuan

Mengembalikan order Shopee yang **`shipped_at`-nya null** ke rekap **faktur auto-sync Accurate**. Order SHIPPED/COMPLETED ber-`shipped_at` null **tak masuk snapshot faktur** (snapshot memfilter `shipped_at`) → penjualannya hilang diam-diam. Penyebab: record di-sync **sebelum** `pickup_done_time` diminta di `get_order_detail`. Solusi: re-fetch detail (kini membawa `pickup_done_time`) → isi `shipped_at` → bentuk ulang faktur. Grounded ke [[External - Accurate]] (Sales Invoice).

## Kapan dipakai

- Ada laporan "order Shopee tak terekap ke Accurate" untuk periode yang `shipped_at`-nya null.
- Setelah verifikasi (via `b3_verify.js`) bahwa `TOTAL null` > 0 di jendela yang diminta.

## Prasyarat

- Deploy build terbaru: fix `SaveOrderDetail` mem-persist `pickup_done_time` **wajib** ada (kalau tidak, quality-gate selalu lapor "proxy"). Lihat [[Microservices - Integration Service]].
- Env `cmd/ordersync`: `MONGO_URI`, `SHOPEE_PARTNER_*`, **`SHOPEE_ERP_SYSTEM_PARTNER_ID`/`_KEY`** (order route ke app ERP_SYSTEM — tanpa ini semua toko di-skip).
- `SERVICE_URL` = host Integration service (untuk rebuild faktur).
- Skrip pendamping (mongosh) di **`bip-erp/scripts/`**: `b2_plan_faktur_rebuild.js` (planner rebuild), `b3_verify.js` (verifier). Runbook operasional ringkas juga di `bip-erp/scripts/README-shippedat-backfill.md`.

---

## 1. Baseline

```
mongosh "$MONGO_URI" b3_verify.js
```
Catat **TOTAL null** + daftar faktur **FAILED** (baseline diketahui: 2 faktur FAILED = konflik retur, di luar scope).

## 2. Repopulate `shipped_at` (re-fetch `pickup_done_time`)

DRY RUN dulu (tanpa call Shopee / tulis):
```
MODE=shippedatbackfill go run ./cmd/ordersync/        # jumlah target per toko
```
Eksekusi (per toko; skip-if-fixed → re-run murah):
```
MODE=shippedatbackfill MANUAL_SYNC_CONFIRM=yes SHOP_IDS=<shop> go run ./cmd/ordersync/
```
- Default `UPDATED_SINCE=2026-07-01` mem-bound ke era Juli; override bila perlu.
- Baca output `fixed=N (authoritative_pickup=A, proxy_uncertain=P) still_null=S`:
  - **authoritative_pickup** = dapat `pickup_done_time` → tanggal faktur akurat, aman di-faktur.
  - **proxy_uncertain** = Shopee tak kirim pickup → `shipped_at` = `update_time` (bisa meleset ~1 hari). **JANGAN auto-faktur**; tinjau manual.
  - `RATE LIMITED` → berhenti sendiri; ulang setelah 00:00 UTC+8 (lihat [[LOG - Shopee API Rate Limit Request]]).

## 3. Rebuild faktur terdampak (retur-safe)

```
# set SERVICE_URL di dalam b2_plan_faktur_rebuild.js
mongosh "$MONGO_URI" b2_plan_faktur_rebuild.js > b2_calls.sh
less b2_calls.sh        # REVIEW: retry (auto-era) + backfill (pra-cutover SENT)
bash b2_calls.sh
```
Planner **otomatis mengecualikan**: faktur `IMPORTED` (manual finance), `FAILED`, dan **hari-kirim order ber-Retur Penjualan SENT** (rebuild bisa ditolak Accurate "tidak dapat menghapus rincian faktur … dipakai retur" → flip FAILED). Retry/backfill idempoten + skip-unchanged. Latar keputusan retur: [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]].

## 4. Verifikasi

```
mongosh "$MONGO_URI" b3_verify.js
```
Harapan: **TOTAL null turun drastis**; faktur **FAILED tetap** (tak ada FAILED baru — planner sudah exclude hari at-risk); nilai faktur SENT bertambah.

## Tindak lanjut manual (di luar auto)

- Order **proxy_uncertain** → daftar dari log langkah 2; finance tinjau tanggal kirim.
- Hari **at-risk retur** & **2 FAILED** → penanganan retur terpisah ([[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]]).
- Hari **IMPORTED (pra-cutover 10 Jul)** = faktur manual finance; tak disentuh auto.

## Rollback

- Langkah 2 hanya mengisi `shipped_at` (upsert idempoten, tanpa delete) → tak perlu rollback.
- Langkah 3 push replace-by-id ke Accurate; bila salah, re-run dengan data benar (idempoten).

## Dokumen Terkait

- [[Microservices - Integration Service]] — pipeline `shipped_at`/`pickup_done_time` + tool `cmd/ordersync`
- [[External - Accurate]] — target Sales Invoice
- [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] — kenapa hari ber-retur dikecualikan
- [[LOG - Shopee API Rate Limit Request]] — konteks kuota Shopee
