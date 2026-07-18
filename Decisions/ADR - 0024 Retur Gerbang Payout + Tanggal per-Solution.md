✅ **Implemented** (kode 2026-07-18: gerbang payout + tanggal per-solution + pemicu settlement; ⚠️ belum deploy; cleanup data existing PENDING)

# ADR - 0024 Retur: Gerbang Payout≈0 (Income vs Retur) + Tanggal per-Solution

Dua keputusan dari satu investigasi (2026-07-18, "Opsi B") yang membenahi **Retur Penjualan** auto-sync ke Accurate. Menggantikan sebagian [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] (keputusan tanggal) & premis refund-only-as-retur di [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] / [[ADR - 0012 Retur Refund-only Push-all]].

## Context

Investigasi berangkat dari keluhan: tanggal & jumlah retur di ERP ≠ Shopee (contoh `260622R69SUCKP`). Dua temuan grounded:

**1. Refund Shopee = penyesuaian INCOME (escrow), bukan dokumen retur.** `get_escrow_detail`: `order_income.escrow_amount` **sudah net-of-refund** (rumus resmi memuat `+seller_return_refund`; kurir-salah → `seller_lost_compensation` menutup, seller tak rugi). ERP punya **dua sisi** di Accurate: Faktur+Retur (revenue) & **Auto Sync Income / Bukti Terima Kas** (kas). `buildReceiptPayload` (`accurate_receipt_usecase.go`) **sudah** menyerap refund untuk order **payout>0** (baris Potongan Penjualan `discount = basePorsi − payment − feeLain`, `payment`=payout net-of-refund; akun discount 4003) & **melunasi piutang penuh**; order **payout≈0** (refund penuh) **di-skip receipt** (Accurate tolak baris 0-payment) → kode itu sendiri mengarahkan koreksi **lewat retur**. Tapi pipeline retur membukukan **SEMUA** retur tanpa melihat payout → untuk order payout>0 terjadi **DOBEL** (revenue balik dua kali + piutang ter-kredit minus). Terukur prod: **7 RTR SENT dobel**, 92 baris FAILED payout>0 = ranjau (jadi dobel bila di-retry).

**2. Tanggal `accepted` Shopee TIDAK bersih.** [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] memakai `accepted` (`update_time`) seragam dengan premis "Shopee tak kena settle-drift". **Terbantah 2026-07-18**: `updated_at` Shopee **melar mundur** saat settle refund — median **3 hari**, 46 dari 49 lebih lambat dari kedatangan fisik (penyakit sama `update_time` TikTok). `return_tracking` (reverse-tracking RECEIVED / `last_event_at`) menyediakan tanggal **fisik** barang-sampai untuk 49 retur barang-balik Shopee — lebih benar.

**3. Shopee tak punya push retur.** `push_config_on_list` resmi (13 tipe: order-status, tracking-no, dst.) **tak memuat return/refund** → retur tak real-time; koreksi harus lewat **field anti-drift + polling**, bukan webhook. (Push order-status hanya bantu deteksi **cancel**.)

## Decision

**1. Retur Penjualan ⟺ order `payout ≈ 0`.** `returnPayoutGate(order)` (`accurate_rts_usecase.go`, reuse `payoutOf()` **identik** dgn receipt):
- order **CANCELLED** → **book** langsung (tak punya escrow, tak menunggu).
- income belum settle (`Income.PaidAt == nil`) → **DEFER** (payout belum diketahui).
- settled & **payout > 0** → **SKIP** (baris ditandai `SKIPPED`; Auto Sync Income yang menangani).
- settled & **payout ≈ 0** → **book**.

Dipasang di `SyncOrderReturn` (auto) & `RetryDailyReturn` (manual tolak payout>0/belum-settle). **Pemicu**: retur DEFER di-book saat escrow cair — `triggerReturnAfterSettlement` di `syncEscrowReleaseWindow` (refetch branch, `shopee_new_usecase.go`) memanggil `SyncOrderReturn` bila payout≈0; urutan sebaliknya (settle dulu, retur menyusul) ditangani ingestion `SyncReturns` yang gate-nya melihat income settled. Idempoten (guard by-member) & fire-and-forget.

**2. Tanggal retur per-solution (Shopee).** `resolveReturnTransDate`: CANCELLED→`cancelled_at`; **TikTok**→`order_update_date` (tetap, [[ADR - 0017 Tanggal Retur TikTok via order_update_date]]); **Shopee refund-only** (`solution=1`)→`requested_at` (`create_time`, anti-drift); **Shopee barang-balik** (`solution=0`) + `return_tracking.status==RECEIVED` + `last_event_at`→**arrival**; fallback `updated_at`→`requested_at`→`shipped`. Memakai sub-doc `return_tracking` yang **sudah** diisi cron reverse-tracking — **bukan** menghidupkan `arrivalResolver` lama yang dicabut ADR-0023.

## Consequences

- **Dobel mustahil by-design**: payout>0 & payout≈0 saling eksklusif — Receipt ATAU Retur, tak pernah keduanya.
- **Income/Auto Sync Income sync TIDAK diubah** — ia sudah benar (menyerap refund payout>0, defer payout≈0 ke retur). Perbaikan 100% di sisi retur.
- **Tanggal benar go-forward**: refund-only pakai tanggal ajukan (stabil), barang-balik pakai tanggal fisik sampai gudang.
- **Menggantikan**: ADR-0023 **keputusan #1** (accepted-seragam) — premisnya salah; ADR-0023 **keputusan #2** (cutover split faktur/retur) **tetap berlaku**. Juga menutup premis "refund-only selalu jadi retur" di [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] / [[ADR - 0012 Retur Refund-only Push-all]].
- **Cleanup data existing (PENDING)**: **void ~7 RTR payout>0 dobel**; **re-date/rebuild** retur sah (payout≈0) yang tanggalnya terlanjur `updated_at` melar.
- **Edge butuh finance**: barang-balik `solution=0` **payout>0** (~48, ~1–2 SENT) — receipt urus revenue, tapi **stok tak balik** (Accurate under-stock). Konservatif (stok-opname backstop), idealnya retur-stok-saja — **ditahan untuk finance**.

## Dokumen Terkait
- [[Microservices - Integration Service]] — Auto-Sync Retur (gerbang payout, tanggal per-solution) & Auto Sync Income (receipt)
- [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] — keputusan #1 digantikan; #2 tetap
- [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]]
- [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]]
- [[ADR - 0017 Tanggal Retur TikTok via order_update_date]]
