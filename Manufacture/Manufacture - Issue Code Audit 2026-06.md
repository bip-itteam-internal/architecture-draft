## Deskripsi

*Hasil audit kode service [[Microservices - Manufacture Service]] (backend Go + frontend Next.js) per 2026-06-26. Mendaftar temuan korektnes, keamanan, dan integritas data beserta lokasi `file:line` dan rencana perbaikan. Point-in-time record — status per temuan diperbarui saat fix masuk.*

- **Status**: 🟡 Issue / Teridentifikasi — plan perbaikan disetujui, sebagian **belum** masuk kode.
- **Cakupan**: `bip-erp/services/manufacture/*` + `erp-frontend/src/features/manufacture/*`.

## Temuan Backend (Go)

| # | Lokasi | Severity | Masalah | Rencana fix | Status |
|---|---|---|---|---|---|
| B1 | `proposal.go:60-64` | 🔴 Critical | **Authz bypass**: `ApproveProposal` ambil `role` dari body request, bukan header gateway. Siapa pun kirim `{"role":"SUPERVISOR"}` → apply koreksi stok tanpa hak. | Ambil role dari `c.Get(BIP-System-Roles)` (key `manufacture`): staff→PPIC, supervisor→SPV, admin→keduanya. Abaikan body. | 🟡 Belum |
| B2 | `transaksi.go:52-60` | 🔴 Critical | **Race stok**: cek stok OUTBOUND di luar `RunTransaction` (TOCTOU) → dua OUTBOUND paralel lolos → stok minus. | Buang cek pra-tx; conditional `$inc` dalam tx (`{"_id":kode,"stok_sekarang":{"$gte":qty}}`, cek `MatchedCount==0`). | 🟡 Belum |
| B3 | `production.go:67-75` | 🔴 Critical | Sama B2 untuk konsumsi bahan saat produksi → stok bahan minus. | Conditional `$inc` per bahan dalam tx. | 🟡 Belum |
| B4 | `master.go:93-119` | 🟠 Major | **Seed OPENING non-atomik**: insert transaksi + update snapshot terpisah; `CountDocuments` cek-lalu-insert (race) → seed ganda saat sync 2x. | Bungkus per-kode `RunTransaction` + idempotensi via key unik `{kode_bahan, ref:OPENING}`. | 🟡 Belum |
| B5 | `proposal.go:88-104` | 🟠 Major | Apply proposal tak cek status terkini di dalam tx → dua approve SPV bersamaan → koreksi stok ganda. | Update proposal dgn filter status (`PENDING_SPV`); `ModifiedCount==0` → batalkan. | 🟡 Belum |
| B6 | handler sync/reconcile | 🟠 Major | Pakai `context.Background()` bukan request ctx → request sync besar tak bisa dibatalkan. | Pakai `c.Context()`/`c.UserContext()`. | 🟡 Belum |
| B7 | `master.go` · `master_product.go` | 🟠 Major | Partial-failure sync: error di tengah loop `return 500` → state setengah jadi tanpa rollback/laporan. | Kumpulkan error per-baris, lanjut, balas `{synced, failed[]}`. | 🟡 Belum |
| B8 | `helper.go:56-64` | 🟡 Minor | `parseNum` buang semua titik (ribuan) → desimal ber-titik salah; non-angka → 0 senyap. | Dokumentasikan locale id-ID; log warning saat parse gagal. | 🟡 Belum |

## Temuan Frontend (Next.js)

| # | Lokasi | Severity | Masalah | Rencana fix | Status |
|---|---|---|---|---|---|
| F1 | `manufacture-app.tsx` (materialOrders/marketingPOs/procurementPOs/proposals/productionLogs) | 🔴 Critical | Set `as any` dari Go (snake_case) tanpa mapper → komponen baca camelCase → `undefined` → crash cetak/`toLocaleString()` + tabel kosong. Pola sama bug formula. | Tambah mapper `mapMaterialOrder/mapMarketingPO/mapProcurementPO/mapProductionLog/mapProposal` (snake→camel). | 🟡 Belum |
| F2 | `manufacture-app.tsx` `mapTransaksiToLegacy` | 🟠 Major | Map hanya 6 field; `date/customerOrSupplier/picQc/driver` kosong → ledger & Dashboard tak akurat. | Perluas mapper transaksi sesuai field Go. | 🟡 Belum |
| F3 | `ApprovalsAccountsView.tsx` + `handleCreateProposal` | 🔴 Critical | Approve/Reject/Create proposal hanya state lokal — tidak POST ke Go → hilang saat refresh; koreksi stok tak persisten. | Panggil endpoint Go yang sudah ada (`POST /proposal`, `/proposal/:id/approve`, `/reject`) + refetch. | 🟡 Belum |
| F4 | view stok (GudangBahanBaku/BarangJadi/Production) | 🟠 Major | `onUpdateStock` lokal setelah POST+refetch → **double-count** stok sesaat. | Hapus mutasi lokal pasca-POST; andalkan refetch server. | 🟡 Belum |
| F5 | `manufacture-app.tsx` `loadData` | 🟠 Major | master/stok/transaksi tanpa `.catch` per-request → satu gagal → layar kosong total; tak ada loading/error state. | `.catch` per-request / `Promise.allSettled` + state loading/error. | 🟡 Belum |
| F6 | `manufacture-app.tsx:189` | 🟡 Minor | Ternary status FG `... ? "ACTIVE" : "ACTIVE"` → produk DISCONTINUED tetap ACTIVE. | Perbaiki cabang false → `"DISCONTINUED"`. | 🟡 Belum |

## Catatan

- Formula mapper (`mapFormulaToLegacy`) **sudah** diperbaiki (commit FE 2026-06-26); F1 adalah pola yang sama untuk 5 entitas sisanya.
- Endpoint approve/reject/create proposal **sudah ada** di backend; F3 murni soal FE memanggilnya.
- Urutan perbaikan disarankan: B1 (security) → F1 (crash) → B2/B3 (race) → B4 → F3 → sisanya.

## Dokumen Terkait

- [[Microservices - Manufacture Service]] · [[API - Manufacture Service]] · [[Manufacture - Stock & Material Management]]
