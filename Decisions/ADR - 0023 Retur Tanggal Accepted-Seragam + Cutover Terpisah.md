⚠️ **Implemented (sebagian digantikan)** — keputusan **#1 (tanggal accepted-seragam)** **digantikan** [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] (2026-07-18). Keputusan **#2**: struktur **split** (2 konstanta) tetap, TAPI **basis cutover retur diubah tanggal-retur → hari-kirim** (2026-07-19, ADR-0024).

# ADR - 0023 Retur: Tanggal Accepted-Seragam + Cutover Terpisah Retur/Faktur

> **Sebagian digantikan (2026-07-18):** keputusan **#1** (tanggal = `accepted` seragam) memakai premis "Shopee `accepted` bersih" yang **terbantah** — `updated_at` Shopee juga melar mundur saat settle refund (median 3 hari). Kini tanggal **per-solution** (refund-only→`requested_at`; barang-balik→arrival via `return_tracking`), lihat [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]]. Keputusan **#2** (cutover faktur `20260710` vs retur `20260701`) **TIDAK berubah**.

Dua keputusan terkait semantik pembukuan **Retur Penjualan** auto-sync ke Accurate. Melengkapi [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] & [[ADR - 0012 Retur Refund-only Push-all]].

## Context

- Auto-sync retur (`SyncOrderReturn`, [[Microservices - Integration Service]]) membukukan Retur Penjualan terhadap faktur harian sumbernya. Dua isu tanggal & era muncul di prod Juli 2026.
- **Tanggal**: implementasi awal memakai urutan `arrival` (barang fisik tiba via Shopee reverse-tracking + ePOD) → `accepted` (disetujui marketplace) → `requested` → `shipped`. Terukur di prod: `arrival` **hampir tak pernah tersedia** — 1 dari 23 retur SENT (Shopee butuh ePOD; **TikTok tak punya reverse-tracking sama sekali**). Hasilnya faktur retur **tak seragam** (mayoritas accepted, minoritas arrival) tanpa manfaat akurasi nyata.
- **Cutover**: satu konstanta `autoSyncCutoverDateWIB = "20260710"` menjaga BAIK jalur faktur (buat/edit) MAUPUN jalur retur (bukukan), keduanya berbasis **hari kirim**. Tapi finance berhenti input manual retur sejak **awal Juli**, sementara faktur manual finance 1–9 Jul **tetap ada & tak boleh disentuh**. Retur telat matang 5–10 hari → retur yang matang sekarang berasal dari order kirim akhir Juni–awal Juli, yang gate hari-kirih-10-Jul memblokirnya → ~Rp2,7 jt retur yatim tak terkerjakan.

## Decision

**1. Tanggal Retur = tanggal DISETUJUI marketplace (`accepted`), SERAGAM.** Buang `arrival` dari prioritas & cabut seluruh infrastrukturnya (`arrivalResolver`, `SetReturnArrivalResolver`, injeksi `main.go`, `GetReturnArrival`/`ArrivalTime` ditinggalkan dorman). Urutan baru `resolveReturnTransDate`: `accepted` (`update_time`) → `requested` (`create_time`, fallback) → `shipped` (hari kirim — **ANOMALI**, tak boleh normal terjadi utk retur ACCEPTED). Retur mencermin **status marketplace**; kapan barang fisik tiba di gudang diurus **service lain**.

**2. Cutover DIPECAH dua konstanta berbeda basis:**
- **Faktur** `autoSyncCutoverDateWIB = "20260710"` (basis **hari kirim**) — jalur yang membuat/mengedit faktur: `OnOrderToShip`, `SweepDailyInvoice`, `RetryDailyInvoice`, `BackfillPreCutoverInvoice`, `OnOrderCancelledOrReturned`.
- **Retur** `autoSyncReturnCutoverDateWIB = "20260701"` — ⚠️ **basis DIUBAH 2026-07-19: tanggal-retur → HARI KIRIM** ([[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]]). Dulu basis **tanggal-retur** menarik retur order-lama (kirim Mei/Juni) ke auto padahal faktur & income-nya **manual finance** → retur auto membalik pembukuan manual (tak konsisten + potensi dobel). Kini basis **hari kirim** = retur ikut era faktur sumbernya: order kirim < 1 Jul = manual finance (faktur, income, DAN retur); ≥ 1 Jul = auto. Jalur: `SyncOrderReturn`, `RetryDailyReturn`, `RecordReturnFetchFailure` (semua kini menilai `dateWIB` hari-kirim, bukan tanggal-retur). Retur < 1 Jul yang terlanjur di-book **di-descope** (`cmd/returndescope`: hapus dok Accurate + tandai SKIPPED; 1565 baris, 1007 dok Accurate dihapus 2026-07-19).

## Consequences

- **Positif**: faktur retur seragam (1 basis tanggal → mudah direkonsiliasi ke tanggal persetujuan marketplace); badge "perkiraan" hilang untuk retur normal, dipersempit ke anomali `shipped` (badge "cek tanggal", [[APP - Web ERP]]); retur yatim 1–9 Jul (TikTok berfaktur IMPORTED) kini bisa dibukukan tanpa menyentuh faktur finance.
- **Trade-off tanggal**: retur yang barangnya tiba di bulan berbeda dari tanggal disetujui tercatat di bulan disetujui — dapat diterima karena stok fisik diurus service lain.
- **Prasyarat cutover-split aman**: `OnOrderCancelledOrReturned` WAJIB tetap ber-guard cutover **faktur** (10 Jul) — guard ini sempat HILANG di jalur koreksi & ditambahkan 2026-07-16; tanpa itu, re-snapshot menimpa faktur IMPORTED finance (vektor insiden [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] / 14 Jul).
- **Anomali `shipped` = data problem**: kalau retur ACCEPTED tetap jatuh ke `shipped`, timestamp marketplace hilang → ditandai (dokumen Accurate + UI) untuk cek manual.

## Dokumen Terkait
- [[Microservices - Integration Service]] — bagian Auto-Sync Retur (HIGH-F tanggal, Cutover terpisah)
- [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]]
- [[APP - Web ERP]] — halaman Auto-Sync Retur (badge)
