✅ **Implemented** (kode 2026-07-16/17; ⚠️ belum deploy per 2026-07-17)

# ADR - 0023 Retur: Tanggal Accepted-Seragam + Cutover Terpisah Retur/Faktur

Dua keputusan terkait semantik pembukuan **Retur Penjualan** auto-sync ke Accurate. Melengkapi [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] & [[ADR - 0012 Retur Refund-only Push-all]].

## Context

- Auto-sync retur (`SyncOrderReturn`, [[Microservices - Integration Service]]) membukukan Retur Penjualan terhadap faktur harian sumbernya. Dua isu tanggal & era muncul di prod Juli 2026.
- **Tanggal**: implementasi awal memakai urutan `arrival` (barang fisik tiba via Shopee reverse-tracking + ePOD) → `accepted` (disetujui marketplace) → `requested` → `shipped`. Terukur di prod: `arrival` **hampir tak pernah tersedia** — 1 dari 23 retur SENT (Shopee butuh ePOD; **TikTok tak punya reverse-tracking sama sekali**). Hasilnya faktur retur **tak seragam** (mayoritas accepted, minoritas arrival) tanpa manfaat akurasi nyata.
- **Cutover**: satu konstanta `autoSyncCutoverDateWIB = "20260710"` menjaga BAIK jalur faktur (buat/edit) MAUPUN jalur retur (bukukan), keduanya berbasis **hari kirim**. Tapi finance berhenti input manual retur sejak **awal Juli**, sementara faktur manual finance 1–9 Jul **tetap ada & tak boleh disentuh**. Retur telat matang 5–10 hari → retur yang matang sekarang berasal dari order kirim akhir Juni–awal Juli, yang gate hari-kirih-10-Jul memblokirnya → ~Rp2,7 jt retur yatim tak terkerjakan.

## Decision

**1. Tanggal Retur = tanggal DISETUJUI marketplace (`accepted`), SERAGAM.** Buang `arrival` dari prioritas & cabut seluruh infrastrukturnya (`arrivalResolver`, `SetReturnArrivalResolver`, injeksi `main.go`, `GetReturnArrival`/`ArrivalTime` ditinggalkan dorman). Urutan baru `resolveReturnTransDate`: `accepted` (`update_time`) → `requested` (`create_time`, fallback) → `shipped` (hari kirim — **ANOMALI**, tak boleh normal terjadi utk retur ACCEPTED). Retur mencermin **status marketplace**; kapan barang fisik tiba di gudang diurus **service lain**.

**2. Cutover DIPECAH dua konstanta berbeda basis:**
- **Faktur** `autoSyncCutoverDateWIB = "20260710"` (basis **hari kirim**) — jalur yang membuat/mengedit faktur: `OnOrderToShip`, `SweepDailyInvoice`, `RetryDailyInvoice`, `BackfillPreCutoverInvoice`, `OnOrderCancelledOrReturned`.
- **Retur** `autoSyncReturnCutoverDateWIB = "20260701"` (basis **tanggal retur**) — jalur yang membukukan retur: `SyncOrderReturn`, `RetryDailyReturn`, `RecordReturnFetchFailure`. Aman lebih awal karena membukukan retur hanya **MERUJUK** faktur (tak mengedit), jadi faktur manual finance 1–9 Jul tetap utuh.

## Consequences

- **Positif**: faktur retur seragam (1 basis tanggal → mudah direkonsiliasi ke tanggal persetujuan marketplace); badge "perkiraan" hilang untuk retur normal, dipersempit ke anomali `shipped` (badge "cek tanggal", [[APP - Web ERP]]); retur yatim 1–9 Jul (TikTok berfaktur IMPORTED) kini bisa dibukukan tanpa menyentuh faktur finance.
- **Trade-off tanggal**: retur yang barangnya tiba di bulan berbeda dari tanggal disetujui tercatat di bulan disetujui — dapat diterima karena stok fisik diurus service lain.
- **Prasyarat cutover-split aman**: `OnOrderCancelledOrReturned` WAJIB tetap ber-guard cutover **faktur** (10 Jul) — guard ini sempat HILANG di jalur koreksi & ditambahkan 2026-07-16; tanpa itu, re-snapshot menimpa faktur IMPORTED finance (vektor insiden [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] / 14 Jul).
- **Anomali `shipped` = data problem**: kalau retur ACCEPTED tetap jatuh ke `shipped`, timestamp marketplace hilang → ditandai (dokumen Accurate + UI) untuk cek manual.

## Dokumen Terkait
- [[Microservices - Integration Service]] — bagian Auto-Sync Retur (HIGH-F tanggal, Cutover terpisah)
- [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]]
- [[APP - Web ERP]] — halaman Auto-Sync Retur (badge)
