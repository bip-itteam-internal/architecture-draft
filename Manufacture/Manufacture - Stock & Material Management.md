## Deskripsi

*Desain (to-be) sistem **manajemen stok & material** untuk produksi — pengganti spreadsheet manual (stok bahan baku/kemas vs kebutuhan). Menggabungkan **master material + stok per gudang + perencanaan kebutuhan → kekurangan → pengadaan**. Menjadi backbone yang menaungi [[WH - Management System]], [[WH - Inbound (Receiving)]] / [[WH - Outbound (Sending)]], dan stock opname.*

- **Status**: 🟡 Desain / Direncanakan (**belum** diimplementasi di kode)
- **Target arsitektur**: microservice `warehouse-service` baru + modul web, **rollout bertahap**
- **Catatan**: berbeda dari [[Microservices - Inventory Service]] & [[GA - Inventory Management]] yang menangani **aset GA**, bukan stok bahan/produksi

## Latar Belakang

* Saat ini stok & kebutuhan bahan dicatat di **spreadsheet** yang berantakan (multi-section, merged cell, kolom tercampur: KATEGORI berisi nama supplier/kode batch, KODE belum terstandar, status & angka bercampur).
* Tujuan: master & stok terstruktur, perhitungan kekurangan otomatis untuk pengadaan, dan jejak yang bisa dilacak.

## Cakupan Barang

Bahan Baku · Bahan Kemas · Barang Setengah Jadi (WIP) · Barang Jadi — dihubungkan **BOM/resep** (barang jadi → WIP → bahan baku/kemas).

## Fitur Inti

- **Master Material** — kode terstandar (migrasi + cleanup dari spreadsheet: kode pembantu → kode penyesuaian), nama, kategori, jenis, satuan, dan **status pergerakan** (fast / medium / slow moving, bad stock, tidak aktif, belum launching)
- **Stok per gudang/lokasi** — termasuk **gudang karantina** untuk barang rusak/kadaluarsa (ED)
- **BOM / Resep** (hybrid) — komponen bahan baku/kemas per barang jadi/WIP
- **Perencanaan kebutuhan** — rencana produksi/target → kebutuhan dihitung otomatis via BOM, **bisa di-override/tambah manual** (hybrid)
- **Perhitungan kekurangan** — kebutuhan vs stok → daftar kekurangan → diteruskan ke [[GA - Procurement System]] untuk pengadaan
- **Stock opname & penyesuaian** — integrasi flow yang sudah ada: hitung fisik → selisih sistem vs fisik → barang rusak/ED ke karantina (input + foto via [[APP - Mobile Application]]) → berita acara → adjustment

## Model Data

`warehouse-service` memiliki database sendiri (`warehouse_db`), collection utama:

- `material` — master bahan (kode, nama, kategori, jenis: baku/kemas/WIP/jadi, satuan, status pergerakan)
- `stock` — stok per material per gudang/lokasi
- `bom` — resep (header + komponen)
- `production_plan` / `requirement` — target produksi + kebutuhan terhitung (+ override manual)
- `shortage` — hasil perhitungan kekurangan (untuk pengadaan)
- `stock_opname` — sesi opname + selisih + penyesuaian
- `inbound` / `outbound` — pergerakan stok (selaras [[WH - Inbound (Receiving)]] / [[WH - Outbound (Sending)]])
- `warehouse` / `location` — multi-gudang + karantina

## Arsitektur & Integrasi

- **`warehouse-service`**: Go + Fiber v2 + MongoDB, di belakang [[CORE - API Master Gateway]], auth **SSO** (lihat [[CORE - SSO Flow]]), role Warehouse / PPIC / Manufacture
- **Integrasi**:
	- [[External - Accurate]] — **tarik stok awal** → bertahap menjadi source of truth (hybrid bertahap)
	- [[GA - Procurement System]] — kekurangan → pengadaan/PO
	- [[APP - Mobile Application]] — input stock opname & foto barang rusak/ED
	- [[Microservices - Notification Service]] — notifikasi (stok rendah, kekurangan, opname)
	- [[Microservices - Employee Service]] — audit (pencatatan oleh siapa)
- **UI**: modul **Warehouse** di [[APP - Web Application]]

## Rollout Bertahap

- [ ] **Fase 1** — Master material terstandar (migrasi + cleanup spreadsheet) + stok per gudang (tarik dari Accurate) + perhitungan kekurangan → daftar pengadaan
- [ ] **Fase 2** — BOM/resep + kebutuhan otomatis dari rencana produksi (hybrid + override manual)
- [ ] **Fase 3** — Integrasi Accurate lebih dalam + stock opname digital (selisih, karantina, berita acara)
- [ ] **Fase 4** — Inbound/outbound digital + multi-gudang/dispatch; `warehouse-service` jadi **source of truth** stok

## Catatan Migrasi & Belum Diputuskan (TBD)

- **Migrasi data spreadsheet** butuh cleanup: kode belum terstandar, KATEGORI tercampur (supplier/batch/produk), satuan tidak konsisten, dan **anomali nilai** (mis. MENTHOL CRYSTAL ±18,8 juta gram ≈ 76% total stok — perlu diverifikasi)
- Konversi & konsistensi **satuan** (gram/kg vs pcs)
- **Multi-gudang** vs gudang tunggal
- ~~Ownership sistem: PPIC vs Warehouse vs Manufacture~~ → **dok diletakkan di domain Manufacture** (ownership condong Manufacture; peran Warehouse/PPIC tetap terlibat di operasional)
- Apakah stok **barang jadi** dikelola di sini atau di sisi Sales/distribusi

## Dependensi / Dokumen Terkait

- [[Manufacture - Issue Material Miss Count]] · [[Manufacture - Issue ED Material after Stock Opname]] — issue produksi yang dijawab sistem ini
- [[WH - Management System]] · [[WH - Inbound (Receiving)]] · [[WH - Outbound (Sending)]]
- [[GA - Procurement System]]
- [[External - Accurate]] · [[APP - Mobile Application]] · [[APP - Web Application]]
