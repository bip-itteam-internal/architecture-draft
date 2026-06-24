> **Status:** 🟡 Benchmark / Konsep — research dari ERPGo SaaS, **belum** keputusan Bharata. Sumber: User Manual ERPGo (demo login-gated). Hub: [[ERPGo - Overview & Gap Matrix]].

## Apa yang ERPGo lakukan

Modul **POS** (penjualan ritel di tempat):
- **Add POS / POS Orders** — transaksi kasir (pilih item, qty, diskon, bayar).
- **Manage Product Barcode** — cetak/scan barcode produk.
- **Reports** — penjualan POS, stok terjual.
- Terhubung ke Product/Inventory (potong stok) & Accounting (catat penjualan).

## Yang sudah ada di Bharata ERP

- 🔴 Tidak ada POS. Penjualan = **marketplace** ([[Sales - Marketplace Integration]], [[Microservices - Integration Service]], [[Microservices - TikTok Shop Service]]), bukan kasir tatap muka.
- Stok dikelola [[Microservices - Inventory Service]] + [[WH - Management System]].

## Gap / Peluang

- Gap **secara teknis ada**, tapi **tidak selaras model bisnis**: Bharata = seller online + manufaktur, bukan ritel toko fisik.
- Akan bernilai **hanya bila** ada rencana kanal **offline/outlet/factory-outlet**. Saat ini tidak terlihat di vault.

## Rekomendasi

- **DEFER / tidak diadopsi sekarang.** Tidak ada pemakai jelas; membangun POS = effort besar tanpa kebutuhan.
- **Pemicu re-evaluasi**: bila perusahaan membuka outlet ritel / penjualan langsung di pabrik. Saat itu, POS harus reuse master item & stok dari [[Microservices - Inventory Service]] (jangan master baru).

## Risiko & catatan jaga sistem berjalan

- Jangan bangun jalur stok kedua yang bisa bentrok dengan pemotongan stok marketplace yang sudah jalan.

## Belum Diputuskan (TBD)

- Adakah rencana kanal penjualan offline/outlet? (penentu apakah POS pernah relevan)

## Dokumen Terkait

- [[ERPGo - Overview & Gap Matrix]]
- [[Sales - Marketplace Integration]] · [[Microservices - Integration Service]] · [[Microservices - Inventory Service]] · [[WH - Management System]]
