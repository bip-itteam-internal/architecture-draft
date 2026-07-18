✅ **Implemented** (kode + deploy 2026-07-17; 19 dokumen prod dikoreksi)

# ADR - 0017 Tanggal Retur TikTok via `order_update_date`

Mengubah sumber tanggal Retur Penjualan **khusus TikTok**. Menggantikan sebagian keputusan-1 [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] (yang tetap berlaku untuk Shopee).

## Context

- [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] menetapkan tanggal retur = `accepted` (`update_time` record retur marketplace), seragam lintas channel. Asumsinya: `update_time` = saat retur **disetujui**.
- **Untuk TikTok asumsi itu salah.** `update_time` adalah sentuhan **TERAKHIR** record retur — termasuk **settle refund** yang terjadi berhari-hari setelah returnya. Terukur prod 2026-07-17: **24 dari 49** retur TikTok terbukukan **mundur 7–10 hari** dari kejadian sebenarnya (mis. order `584588723385435246` dibukukan 09/07 padahal returnya 02/07).
- Diperparah pola ingestion: **82% (50/61)** retur TikTok punya `returned_at` NULL → ketahuan lewat **backfill/order-sync**, bukan webhook. Saat returnya di-fetch, `update_time` sudah terlanjur maju.
- Sumber tanggal yang tersedia dari API retur TikTok **hanya dua**: `create_time` (`return.requested_at`) & `update_time` (`return.updated_at`). Retur TikTok **tak punya** data barang-tiba/reverse-tracking (puluhan `*_time` lain milik **order**, bukan retur).
- **Status History** (`transaction_order_histories`, tampil di halaman detail order [[APP - Web ERP]]) **mengkonfirmasi** tanggal yang benar, tapi **bukan** sumber yang dipakai: `created_at`-nya = kapan **sistem kita** mencatat transisi → ikut telat 2–4 hari saat order-sync/backfill telat (19 dari 58). Sumber tanggal harus timestamp **marketplace**, bukan waktu proses kita.
- `order_update_date` = timestamp **TikTok** saat order jadi RETURNED. Cakupan **100%** & terbukti stabil (tak pernah melewati catatan status-history kita: 39 sama, 19 lebih awal).

## Decision

**1. TikTok**: `resolveReturnTransDate` memakai `order.OrderUpdateDate` (source baru **`order_updated`**), fallback berjenjang `accepted` → `requested` → `shipped`. **Shopee tidak berubah** — semantiknya beda (tak kena settle-drift) dan status-history-nya hanya 9% (19/203), jadi kebijakan `accepted` di sana tetap berlaku.

**2. `returnEraDateWIB` DIDELEGASIKAN** ke `resolveReturnTransDate` (tak lagi menyalin urutannya). Gate cutover **wajib** menilai tanggal yang **persis sama** dengan tanggal dokumen; dua salinan logika = begitu satu berubah, yang lain diam-diam tertinggal dan mesin menilai era dengan tanggal berbeda dari yang ia bukukan.

**3. Tanggal ke Accurate & nomor RTR dinormalkan ke hari WIB** (`util.WIBDayStart(transDateAt)`):
- **Jebakan zona**: driver Mongo mengembalikan `time.Time` dalam **UTC**; `Format("02/01/2006")` langsung memakai UTC → untuk retur **≥17:00 UTC (= dini hari WIB)** tanggalnya **mundur sehari** dari WIB, padahal kunci grup memakai WIB (`util.WIBDateKey`) → dokumen mendarat di hari berbeda dari kunci grupnya sendiri. Terukur: **14 dokumen** SENT terdampak, **1 di antaranya lompat bulan** (`RTR/2026/06/23/007-BH`: Accurate 30/06, seharusnya 01/07 → periode akuntansi salah).
- **Nomor RTR** dulu memakai **hari-kirim** (menyalin tanggal faktur) — 74/74 dokumen, mis. `RTR/2026/07/06/001` padahal dokumennya bertanggal 12/07. Nomor memuat tanggal dan finance membacanya saat rekonsiliasi → menyesatkan. Sistem lama finance pun menomori pakai **tanggal retur** (`RTR/26/07/14/…` untuk retur 14 Juli).

## Consequences

- **Koreksi data prod (selesai 2026-07-17)**: 20 dokumen TikTok di-redate → 19 dokumen (1 melebur, [[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]]); 14 dokumen lintas-zona dikoreksi. `cmd/returnredate` (`--wib` untuk mode zona) — **tidak idempoten** (`trans_date` tetap jam-UTC≥17 setelah koreksi) → **jangan dijalankan ulang**.
- **4 retur pra-cutover TIDAK dikoreksi** (tanggal benarnya 27–29 Jun < cutover `20260701`). Mengoreksinya = hapus dok lalu `SyncOrderReturn` **skip** (era manual) → pembalikan **lenyap**. Dokumennya dibiarkan bertanggal salah (nilainya benar & tetap terbalik). Perlu keputusan finance.
- **Aturan umum**: **jangan pernah** `.Format()` langsung atas `time.Time` dari Mongo untuk tanggal WIB. Tes wajib membangun waktu dalam `time.UTC` — memakai zona WIB membuat tes **lolos palsu**.
- Nomor RTR baru mengikuti tanggal retur; **74 nomor lama tetap gaya lama** kecuali dibukukan ulang.
- Anomali `order_update_date` (1 dari 24): bisa lebih **belakang** dari `update_time` bila TikTok menyentuh order setelah returnya.

## Dokumen Terkait
- [[Microservices - Integration Service]] — Auto-Sync Retur (tanggal & penomoran)
- [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] — tetap berlaku untuk Shopee
- [[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]]
- [[APP - Web ERP]] — Status History (konfirmasi, bukan sumber)
