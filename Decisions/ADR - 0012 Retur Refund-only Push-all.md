# ADR - 0012 Retur Refund-only: Push-all (default) dengan Sakelar

Status: ✅ Implemented (2026-07-13)

## Context

Auto-sync retur ke Accurate ([[Microservices - Integration Service]]) membukukan **Retur Penjualan** untuk retur marketplace. Ada dua situasi ekonomi berbeda pada data retur (`order.return.solution`):

- **Return & refund** (`solution=0`): barang **kembali** ke gudang → Retur Penjualan benar (membalik penjualan **dan** menambah stok).
- **Refund-only** (`solution=1`): pembeli menerima uang kembali tapi **barang tidak kembali** (disimpan pembeli / rusak). Retur Penjualan normal tetap **menambah stok** untuk barang yang tak pernah balik → stok Accurate **over-count**.

Batasan Accurate: `sales-return/save.do` selalu me-restock; tak ada tipe retur "tanpa gerakan stok" yang terverifikasi, dan tak ada API get/list retur untuk rekonsiliasi. Trade-off inti: **akurasi stok** vs **otomasi penuh** (menahan refund-only untuk review manual = akurat tapi butuh intervensi Finance per kasus).

## Decision

Default **push-all** (`autoPushRefundOnly = true` di `usecase/accurate_rts_usecase.go`): refund-only ikut di-push otomatis sebagai Retur Penjualan (perilaku sama seperti jalur summary manual). Over-stock untuk kasus barang-tak-balik **diterima** dan dikoreksi saat **stok-opname** berkala.

Kebijakan dijadikan **satu sakelar** (`autoPushRefundOnly`) dengan fungsi keputusan tunggal `returnHeldReason(solution, autoPush)`:

- `true` (Opsi B, **aktif**) → full-auto, tanpa review manual.
- `false` (Opsi A) → refund-only ditahan status `HELD_REFUND_ONLY` + di-push manual via tombol dashboard "Push ke Accurate".

## Consequences

- ✅ Retur benar-benar otomatis (tak ada bottleneck review manual per kasus).
- ⚠️ Stok Accurate bisa sedikit **lebih** untuk refund-only barang-tak-balik → andalkan stok-opname; bila Finance butuh presisi, cukup balik sakelar ke `false` (kembali ke mode tahan-review, tanpa ubah logika lain).
- 🔭 Upgrade akurasi tanpa balik ke manual = butuh dukungan Accurate (retur tanpa-restock atau auto stock-adjustment) — **belum diverifikasi** (lihat *Belum (retur)* di [[Microservices - Integration Service]]).
- Menjaga kontrak & idempotensi ke Accurate sesuai [[ADR - 0001 Akuntansi via Accurate]].

## Dokumen Terkait

- [[Microservices - Integration Service]]
- [[ADR - 0001 Akuntansi via Accurate]]
