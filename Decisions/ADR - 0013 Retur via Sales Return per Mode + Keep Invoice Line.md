# ADR - 0013 Retur via Sales Return per Mode + Keep Invoice Line

Status: 🟡 **Superseded (2026-07-17)** oleh [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]] — menggantikan [[ADR - 0012 Retur Refund-only Push-all]]

> ⚠️ **Bagian yang SUDAH TIDAK BERLAKU** — jangan dijadikan acuan:
> - **Mekanisme *drop snapshot*/line-drop SUDAH DICABUT TOTAL.** Faktur kini **permanen**: `OnOrderCancelledOrReturned` = no-op & `listSnapshotOrders` **tanpa filter status** (semua order ber-`shipped_at` masuk). Konsekuensinya, keep-line **bukan lagi pengecualian** — ia berlaku untuk semua.
> - **Guard "jangan buku bila order sudah `RETURNED`" (HIGH-C) SUDAH DICABUT** (beserta kembarannya di `RetryDailyReturn`). Premisnya mati; membiarkannya membuat retur pada faktur auto-sync **tak pernah terbukukan** (terukur: 6 retur TikTok menggantung).
> - **`CANCELLED` → "selalu drop"** tidak berlaku lagi; pembatalan pasca-kirim kini butuh Retur Penjualan tersendiri (belum diimplementasikan — lihat ADR-0018).
>
> Yang **masih berlaku**: mode per-`solution`/`partial` (RETURNED/NOT_RETURNED/PARTIALLY_RETURNED), prinsip "faktur tetap utuh, tidak pernah dihapus" ([[ADR - 0001 Akuntansi via Accurate]]), dan larangan mengirim enum mode kosong.

## Context

Auto-sync retur ke Accurate ([[Microservices - Integration Service]]) membalik penjualan saat ada retur. Sistem punya **dua mekanisme pembalik** yang hidup berdampingan:

1. **Koreksi faktur / drop snapshot** — faktur harian di-snapshot ulang dari order berstatus `{SHIPPED, COMPLETED}`; begitu `order.status` jadi `RETURNED`/`CANCELLED`, order keluar dari snapshot → baris jualnya **hilang** saat re-snapshot (membalik penjualan **dan** stok).
2. **Retur Penjualan** (`sales-return/save.do`) — dokumen terpisah terhadap faktur asli.

Bila **keduanya** kena order yang sama → **pengurangan penjualan GANDA**.

Pendekatan awal (dan [[ADR - 0012 Retur Refund-only Push-all]]) berasumsi retur **penuh** selalu membuat order keluar dari snapshot, sehingga cukup di-skip (`FULL_VIA_INVOICE`) dan diandalkan ke mekanisme (1). **Verifikasi data prod** (`integration_db`, 2026-07-13) membantah asumsi itu:

- Dari **28** order "retur penuh + barang balik" (`return.solution=0, partial=false`): **61%** berakhir `RETURNED`/`CANCELLED` (baris di-drop), tapi **39% tetap `COMPLETED`** (baris **masih ada** → **butuh** Retur Penjualan). 7 di antaranya sudah `ACCEPTED`.
- `order.status` flip ke `RETURNED` **tidak deterministik** terhadap `return.status` (ada `RETURNED` saat return masih `REQUESTED`/`PROCESSING`). Jadi status order **tak bisa** dipakai sebagai penanda tunggal "sudah dibalik".

Enum Accurate diverifikasi dari OpenAPI resmi: `returnDetailStatusType ∈ {RETURNED, NOT_RETURNED}`, `returnStatusType ∈ {RETURNED, PARTIALLY_RETURNED, NOT_RETURNED}`.

## Decision

1. **Buku Retur Penjualan saat baris jual MASIH ADA** (order `SHIPPED`/`COMPLETED`) **dan** retur **disetujui** marketplace (`ACCEPTED` — konfirmasi Finance: tak perlu tunggu barang fisik sampai gudang). Mode dari `solution`+`partial` (`resolveReturnMode`/`deriveReturnMode`):
   - refund-only (`solution=1`, barang tak balik) → detail + header **`NOT_RETURNED`** (dana balik, **stok tidak** bertambah).
   - barang balik (`solution=0`) → detail **`RETURNED`** (restock); header **`PARTIALLY_RETURNED`** bila parsial, else **`RETURNED`**.
2. **Jangan buku bila order sudah `RETURNED`** saat sync (`order.Status==RETURNED` guard) — pembalikan sudah lewat drop snapshot; menambah Retur Penjualan = ganda. Mode kosong/tak tentu → baris `FAILED` tanpa kirim (jangan pernah kirim enum kosong).
3. **Rekonsiliasi = pertahankan baris faktur** (BUKAN void dokumen): bila order yang **sudah** punya Retur Penjualan `SENT` kemudian flip `RETURNED`, snapshot faktur **tidak men-drop** barisnya (`listSnapshotOrders` + `includeReturnedWithSentReturn`, dipakai seragam oleh 5 titik build snapshot + cek-hash) → Retur Penjualan jadi **satu-satunya** pembalik. Selaras prinsip "faktur tetap utuh, tidak pernah dihapus" ([[ADR - 0001 Akuntansi via Accurate]]).
4. **Menggantikan** [[ADR - 0012 Retur Refund-only Push-all]]: status `HELD_REFUND_ONLY` / `FULL_VIA_INVOICE` / sakelar `autoPushRefundOnly` **dihapus**; status baris `accurate_daily_returns` = **PENDING/SENT/FAILED** (mode tersimpan di `detail_status`/`return_status`, dipakai saat re-push).

## Consequences

- ✅ Setiap kasus terbalik **tepat sekali**: parsial & refund-only (order tetap `COMPLETED`) via Retur Penjualan; retur penuh via drop-snapshot bila keluar, atau via Retur Penjualan + keep-line bila tetap `COMPLETED`.
- ✅ Refund-only pakai mode `NOT_RETURNED` → **tak over-restock** — menutup trade-off stok ADR-0012 tanpa balik ke review manual.
- ⚠️ **Rem `RTS_RETURN_ENABLED` (default `false`)** — fitur gated OFF sampai rollout diverifikasi (fail-safe).
- ⚠️ Sisa **jendela ganda transien (self-healing):** bila order flip `RETURNED` tepat di antara retur-`ACCEPTED` dan retur-`SENT`, satu putaran sweep bisa drop baris sebelum retur `SENT` → ganda sesaat; sweep berikutnya rebuild via `listSnapshotOrders` → hash beda → re-sync → baris balik. **Backstop monitoring** (deteksi order `RETURNED` yang punya baris `accurate_daily_returns` `SENT`) = **TBD**.
- Idempotensi & kontrak Accurate tetap sesuai [[ADR - 0001 Akuntansi via Accurate]]; exactly-once retur masih **TBD** (lihat *Belum (retur)* di [[Microservices - Integration Service]]).

## Dokumen Terkait

- [[Microservices - Integration Service]]
- [[ADR - 0012 Retur Refund-only Push-all]] (superseded)
- [[ADR - 0001 Akuntansi via Accurate]]
