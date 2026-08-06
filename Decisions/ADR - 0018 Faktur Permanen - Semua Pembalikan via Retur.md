**Status**: ✅ **Implemented** (faktur permanen: PR #511; cabut guard HIGH-C: 2026-07-17; cancel pasca-kirim → retur: 2026-07-18; guardian wired + fix titik-baca dead-sub-doc: 2026-07-22)

# ADR - 0018 Faktur Permanen — Semua Pembalikan via Retur Penjualan

Faktur Penjualan tak pernah diubah setelah terbit; **setiap** pembalikan (retur maupun batal) lewat dokumen **Retur Penjualan**. Menggantikan mekanisme *line-drop* di [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] & [[ADR - 0012 Retur Refund-only Push-all]].

## Context

- Model lama: penjualan bisa dibalik **dua cara** — (a) **line-drop**: faktur di-snapshot ulang tanpa order itu → barisnya lenyap; (b) **Retur Penjualan**. [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] menetapkan campuran: `RETURNED` + ada retur SENT → baris dipertahankan; `RETURNED` tanpa retur → drop; **`CANCELLED` → selalu drop**.
- Campuran itu punya dua masalah. **Konseptual**: line-drop **menulis ulang sejarah** — penjualan bruto hari itu mengecil sendiri dan returnya tak pernah muncul di laporan retur. **Operasional**: dua mekanisme harus selalu sepakat, dan ketidaksepakatannya = pembalikan ganda atau nol.
- Kerangka bisnis (keputusan user 2026-07-17): **`penjualan = income (faktur) + retur`** — tiap transaksi marketplace adalah salah satu: *income* (barang keluar → INV) atau *retur* (barang balik → RTR). Faktur mencatat apa yang terjual; retur mencatat apa yang balik; angka bersih = selisihnya. **Sistem lama finance bekerja persis begini** (bukti prod: `INV/2026/07/06/015-BH` barisnya tetap, dibalik oleh `RTR/26/07/14/014-BH`).

## Decision

**1. Faktur PERMANEN.** Sekali order pernah `shipped`, barisnya **tetap di faktur selamanya**, apa pun statusnya kemudian:
- `OnOrderCancelledOrReturned` = **no-op** (PR #511).
- `listSnapshotOrders` = **tanpa filter `Statuses`** — "semua order ber-`shipped_at` masuk, apapun status kini". Helper `includeReturnedWithSentReturn` jadi tak terpakai.
- Order batal **sebelum** shipped (`shipped_at` NULL) tak pernah masuk faktur → tak ada yang perlu dikoreksi.

**2. Guard "HIGH-C" DICABUT** (2026-07-17) di `SyncOrderReturn` **dan** kembarannya di `RetryDailyReturn`. Guard itu men-skip retur pada faktur auto-sync dengan alasan *"sudah dibalik lewat baris faktur yang hilang"* — premis yang **mati** begitu faktur jadi permanen. Status faktur (`SENT` vs `IMPORTED`) **tak lagi relevan** untuk keputusan membukukan retur.

## Consequences

- **Kebocoran yang ditemukan & ditambal**: dengan faktur permanen tapi HIGH-C masih hidup, retur pada faktur auto-sync **di-skip diam-diam** → penjualannya **tak pernah terbalik**. Terukur prod 2026-07-17: **6 retur TikTok** menggantung → sudah di-backfill (`cmd/returnrebook`). Sisa 4 retur era-auto (~Rp400rb) macet karena **gagal-tautan-faktur** (2 TikTok tanpa baris faktur hari-kirim Juni; 2 Shopee `shipped_at` NULL) — masalah terpisah.
- **Rumus berlaku konsisten**: `penjualan = faktur + retur` kini benar di semua faktur (dulu tak berlaku pada faktur auto-sync yang barisnya di-drop).
- **✅ Pembatalan pasca-kirim → Retur Penjualan (2026-07-18, go-forward deployed).** COD gagal / batal setelah barang dikirim = barang balik; faktur permanen → retur ini satu-satunya pembalik. `synthesizeCancelReturn` membentuk retur dari `order.Items` (seluruh qty balik, `Solution=0` restock, `Partial=false`, `ReturnSN=""`); `effectiveReturn` dipakai **tanpa syarat** di empat titik — pemicu `SyncOrderReturn`, rebuild grup, detail FE (`loadMemberOrders`), & pre-check `RetryDailyReturn` — supaya member cancel dapat barisnya di semua jalur. Sub-doc retur HIDUP dipakai apa adanya; sub-doc **MATI** (`returnSubDocDead`: status `CANCELLED`, permintaan retur diurungkan) pada order batal-pasca-kirim **tetap disintesis** — kalau tidak order-nya tershadow sub-doc mati & tak pernah terbukukan (prod 2026-07: `260702J8PNRG1F`). Dua titik-baca sempat tertinggal guard `== nil` lama (detail FE kosong / Retry gagal-palsu "source order/return not found") → diperbaiki 2026-07-22, selaras jalur pembukuan. Tanggal = `cancelled_at` (`resolveReturnTransDate` cabang `cancelled`, **diutamakan** atas TikTok/accepted). Pemicu: `OnOrderCancelledOrReturned` (dulu no-op) saat CANCELLED **dan** `shipped_at` ada; cutover `cancelled_at ≥ 20260701` (via `returnEraDateWIB`). **Grouping nol perubahan** — cancel melebur ke grup faktur+tanggal yang sama, termasuk grup retur biasa ([[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]]). Sistem lama finance BERHENTI bukukan RETUR COD sejak 1 Jul (konfirmasi user → 0 dobel).
  - **Backfill backlog** (`cmd/cancelreturnbackfill`, DRY-RUN default, rem+verify, `--shop` bertahap): ~4.756 order sejak 1 Jul (~Rp523 jt) → ~1.988 dokumen setelah grouping. Kandidat mencakup order **tanpa** sub-doc retur **maupun** yang sub-doc-nya **MATI** (status `CANCELLED`). Untuk cancel **LAMA pra-gerbang**, `--skip-warehouse-gate` (`WithSkipWarehouseGate`, context key) melewati gerbang gudang — barang sudah balik berminggu lalu, hindari PENDING abadi; jalur webhook/guardian **TETAP** kena gerbang ([[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]).
  - **✅ Guardian aktif (go-forward)**: `NewSyncShopeeOrdersTask` (safety net Shopee, jendela trailing env-tunable, toggle `POST /jobs/sync-shopee-orders/{disable,enable}`) memanggil `SyncOrders` lewat `shopeeUseCase` yang **di-wire `accurateRTSUseCase`** → order ke-flip `CANCELLED`/`RETURNED` di dalam jendela memicu `OnOrderCancelledOrReturned` (booking cancel-return) otomatis. **CLI** `cmd/ordersync` sengaja rtsUseCase=nil (mis. `MODE=refetchdetail` = repopulasi `pickup_done_time`→`shipped_at` **tanpa** memicu faktur/retur) — bukan jalur guardian. Order yang batal jauh **di luar** jendela guardian tetap perlu `cmd/cancelreturnbackfill`.
- **Perkakas hapus-lalu-bukukan-ulang WAJIB**: (a) menolak jalan bila `RTS_RETURN_ENABLED != true`, (b) **memverifikasi** barisnya ada & SENT setelah `SyncOrderReturn`. Sebabnya insiden 2026-07-17: `cmd/returnredate --apply` dijalankan dengan rem mati → dokumen **dihapus**, `SyncOrderReturn` **skip diam-diam**, skrip melapor "berhasil" → **20 Retur Penjualan lenyap** (dipulihkan via `cmd/returnrebook`). `SyncOrderReturn` sengaja **tak mengembalikan error** (dipanggil sbg goroutine) → pemanggil **tak boleh** menganggapnya sukses.

## Pelajaran (kenapa bug ini bisa hidup diam-diam)

- **Tes bisa MELINDUNGI bug.** Tiga tes (`OrderReturned_SkipsToAvoidDoubleReduction`, `ReturnedOrderWithOurInvoice_StillSkips`, `RetryDailyReturn_OrderReturned_Rejected`) mengunci HIGH-C lengkap dengan alasan panjang & meyakinkan. Saat line-drop dicabut, tes-tes itu **tak ikut dibalik** → suite **hijau terus** sementara retur diam-diam tak terbukukan. **Saat premis arsitektur berubah, tes penegak premis lama WAJIB ikut dibalik.**
- **Komentar usang lebih menyesatkan daripada tanpa komentar.** Komentar interface `OnOrderCancelledOrReturned` masih menyebut "re-snapshot/auto-drop" padahal implementasinya sudah no-op — cukup untuk membuat pembaca (termasuk AI agent) salah membaca arsitektur dan nyaris melestarikan bug.

## Dokumen Terkait
- [[Microservices - Integration Service]] — Auto-Sync Faktur & Retur
- [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] — digantikan
- [[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]]
- [[ADR - 0017 Tanggal Retur TikTok via order_update_date]]
