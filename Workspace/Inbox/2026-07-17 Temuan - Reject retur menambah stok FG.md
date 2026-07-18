# Temuan (17 Juli 2026) — Qty Reject pada retur ikut menambah stok FG

**Status**: belum diperbaiki (sengaja) — ditemukan saat mengerjakan feed retur gudang;
user memutuskan dicatat terpisah agar tidak mencampur lingkup task.

## Gejala

Form **Input Return Ekspedisi** (Gudang Barang Jadi → tab Return Dari Ekspedisi) memecah
qty retur jadi **Reuse / Rework / Reject**. Komentar di kode menyatakan niatnya:
*"reuse+rework kembali ke stok; reject ke scrap"*. Kenyataannya **stok FG bertambah
sebesar total ketiganya** — barang reject ikut dihitung sebagai stok layak jual.

## Rantai sebabnya (terverifikasi)

1. `frontend/src/features/manufacture/components/GudangBarangJadiView.tsx` — submit form:
   `const total = l.r + l.w + l.j;` lalu dikirim `qty: total` (termasuk reject).
2. Baris berikutnya `onUpdateStock(l.sku, l.r + l.w)` **hanya** mengubah state React lokal
   (`handleUpdateItemStock` = `setItems`, tanpa panggilan API) — dan langsung tertimpa
   `loadData()` di dalam `addTransaction`. Jadi pengurangan reject tak pernah sampai server.
3. `bip-erp/services/manufacture/transaksi.go` `CreateTransaksi` → `deltaStok(tx.Tipe, tx.Qty)`.
4. `bip-erp/services/manufacture/helper.go` `deltaStok`: `INBOUND` → `return qty` (positif penuh).
5. Hasilnya `$inc stok_sekarang` sebesar **total**, bukan reuse+rework.

## Kenapa ini penting

Ini menyentuh langsung keluhan yang memicu fitur feed retur: **akurasi stok yang dipakai
Finance**. Selama form ini dipakai, tiap barang reject menggelembungkan stok FG layak jual —
dan stok itulah acuan Finance menyesuaikan Accurate.

Perlu diperiksa juga apakah `GudangBahanBakuView` (tab BALIK_RM) punya pola yang sama.

## Yang perlu diputuskan sebelum memperbaiki

- Reject harus **tidak menambah stok** sama sekali, atau masuk **lokasi/akun scrap terpisah**?
  Form sudah menulis `destinationOrStorage: 'Gudang Return & Scrap'`, tapi ledger stok tak
  punya konsep lokasi — `manufacture_stok` hanya `_id` (kode) + `stok_sekarang`.
- Data historis yang sudah terlanjur menggelembung: dikoreksi lewat stok opname, atau
  penyesuaian bertarget?
- Interaksi dengan [[ADR - 0015 Push Pergerakan WMS ke Accurate]]: retur F3 (penanda
  `namaMarket`) **tidak** didorong sebagai Penyesuaian Persediaan karena dianggap tercakup
  Sales Return. Perbaikan qty di sisi WMS perlu dicek agar tak menimbulkan selisih baru
  antara stok WMS dan Accurate.

## Terkait

- [[Microservices - Manufacture Service]] · [[ADR - 0015 Push Pergerakan WMS ke Accurate]]
- [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] (refund-only `NOT_RETURNED`
  sengaja tak me-restock — semangat yang sama: barang yang tak layak/tak kembali jangan
  menambah stok)
