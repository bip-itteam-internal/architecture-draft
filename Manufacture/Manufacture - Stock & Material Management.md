## Deskripsi

*Desain (to-be) sistem **manajemen stok & material** untuk produksi — pengganti spreadsheet manual (stok bahan baku/kemas vs kebutuhan). Menggabungkan **master material + stok per gudang + perencanaan kebutuhan → kekurangan → pengadaan**. Menjadi backbone yang menaungi [[WH - Management System]], [[WH - Inbound (Receiving)]] / [[WH - Outbound (Sending)]], dan stock opname.*

- **Status**: ⚠️ Sebagian Implemented — service nyata = [[Microservices - Manufacture Service]] (`manufacture-service` + `manufacture_db`). Fase 1 (master bahan/produk + stok + transaksi), BOM/formula, dan **baca stok dari Accurate (satu arah)** sudah jalan; fase lanjut (kekurangan otomatis, opname digital, multi-gudang, tulis balik ke Accurate) masih konsep.
- **Target arsitektur**: microservice **`manufacture-service`** (Go + Fiber v2 + MongoDB) + modul web di [[APP - Web ERP]], **rollout bertahap**. (Dok ini awalnya menamai `warehouse-service`; implementasi final memakai nama tunggal **`manufacture`** di semua layer — service, db, FE.)
- **Catatan**: berbeda dari [[Microservices - Inventory Service]] & [[GA - Inventory Management]] yang menangani **aset GA**, bukan stok bahan/produksi

## Latar Belakang

* Saat ini stok & kebutuhan bahan dicatat di **spreadsheet** yang berantakan (multi-section, merged cell, kolom tercampur: KATEGORI berisi nama supplier/kode batch, KODE belum terstandar, status & angka bercampur).
* Tujuan: master & stok terstruktur, perhitungan kekurangan otomatis untuk pengadaan, dan jejak yang bisa dilacak.

## Cakupan Barang

Bahan Baku · Bahan Kemas · Barang Setengah Jadi (WIP) · Barang Jadi — dihubungkan **BOM/resep** (barang jadi → WIP → bahan baku/kemas).

## Fitur Inti

- **Master Material** — kode terstandar (migrasi + cleanup dari spreadsheet: kode pembantu → kode penyesuaian), nama, kategori, jenis, satuan, dan **status pergerakan** (fast / medium / slow moving, bad stock, tidak aktif, belum launching)
- **Stok per gudang/lokasi** — termasuk **gudang karantina** untuk barang rusak/kadaluarsa (ED)
- **BOM / Resep** (hybrid) — komponen bahan baku/kemas per barang jadi/WIP. **Dua varian resep** (Formula 1 / Formula 2): sebagian produk punya resep alternatif dengan bahan sama tapi qty beda (dari import Excel grup kolom `FURMULA 2`). Menu operasional (**RM Keluar Ke Produksi**, **Material Order**, **Batch Record**) menampilkan pilihan Formula 1/2 **hanya bila produk punya F2** — kalau tidak, langsung Formula 1. Rencana Produksi (kapasitas) tetap default Formula 1.
- **Perencanaan kebutuhan** — rencana produksi/target → kebutuhan dihitung otomatis via BOM, **bisa di-override/tambah manual** (hybrid)
- **Perhitungan kekurangan** — kebutuhan vs stok → daftar kekurangan → diteruskan ke [[GA - Procurement System]] untuk pengadaan
- **Stock opname & penyesuaian** — integrasi flow yang sudah ada: hitung fisik → selisih sistem vs fisik → barang rusak/ED ke karantina (input + foto via [[APP - MyBharata]]) → berita acara → adjustment. Flowchart: [[Manufacture - Stok Pengecekan Fisik (Flow Source)]]

## Model Data

`manufacture-service` punya database sendiri (`manufacture_db`). **Koleksi nyata di kode** (prefix `manufacture_`, lihat [[Microservices - Manufacture Service]]): `manufacture_master_bahan`, `manufacture_master_product`, `manufacture_stok` (snapshot), `manufacture_transaksi` (in/out — sumber kebenaran pergerakan), `manufacture_formula` (BOM), `manufacture_sku_mapping` (listing SKU → komponen; bundle **virtual**, stok hanya di level komponen), `manufacture_sync_log`, `manufacture_production_log`, `manufacture_material_order`, `manufacture_marketing_po`, `manufacture_procurement_po`, `manufacture_proposal`, `manufacture_audit_log`, `manufacture_resi` (master resi retur), `manufacture_saldo_awal_bulanan` (snapshot saldo awal per bulan — **data master barang terpisah dari saldo awal bulanan**; snapshot otomatis idempoten tiap awal bulan).

**Desain to-be (belum semua di kode)** — penamaan konseptual:

- `material` → terealisasi sbg `manufacture_master_bahan` + `manufacture_master_product`
- `stock` → `manufacture_stok` (snapshot; **belum** per-gudang/lokasi — aproksimasi per-gudang via `GET /stok/sektor`: Utama = kode master bahan, Tinggar = kode master barang, Sadewa = net transaksi bergudang-simpan "sadewa")
- `bom` → `manufacture_formula` (header + ingredients)
- `production_plan` / `requirement` — target produksi + kebutuhan terhitung (+ override manual) — **TBD**
- `shortage` — hasil perhitungan kekurangan (untuk pengadaan) — **TBD**
- `stock_opname` — sesi opname + selisih + penyesuaian — **sebagian**: **Saldo Akhir bulanan kini bisa direkonsiliasi ke hasil SO** via import Excel (PPIC/SPV; `qty_akhir` dikunci = hasil SO, lihat [[Microservices - Manufacture Service]]) & saldo awal bisa **direvisi lewat approval PPIC→SPV** (revisi bulan tertutup di-gate izin **Buka Kunci Edit WMS** dari IT, sama seperti koreksi transaksi — lihat [[Microservices - Manufacture Service]]); sesi opname digital penuh (selisih per lokasi, karantina, berita acara) masih TBD
- `inbound` / `outbound` → via `manufacture_transaksi`; **rantai alur FE sudah tersambung & anti-duplikat**: keluar bahan (grup RM-OUT-BOM, stok tak boleh minus, deviasi fisik vs teori BOM **atau tambah/hapus bahan dari formula** → approval PPIC→SPV) → laporan hasil produksi (stok FG tercipta) → kirim produk (SJ IN TRANSIT) → input gudang FG (terima SJ → DELIVERED + gudang simpan) → masuk kembali sisa bahan (checklist per grup); flow [[WH - Inbound (Receiving)]] / [[WH - Outbound (Sending)]] penuh **TBD**
- `warehouse` / `location` — multi-gudang + karantina — **sebagian**: **Mutasi Gudang Fase 1** (29 Juli 2026) menambah master **kode lokasi** (`manufacture_lokasi_gudang`) + dokumen mutasi antar-lokasi (DRAFT→DIKIRIM→DITERIMA) + saldo per-lokasi diturunkan — sebagai **layer pelacakan** (tak menyentuh stok global; lihat [[Microservices - Manufacture Service]]). Ledger per-lokasi sejati (saldo awal absolut), karantina, & AR/konsinyasi (Fase 2) masih TBD

## Arsitektur & Integrasi

- **`manufacture-service`**: Go + Fiber v2 + MongoDB, di belakang [[CORE - API Master Gateway]], auth via header gateway (lihat [[CORE - SSO Flow]]), role Manufacture / PPIC / Warehouse. Detail implementasi: [[Microservices - Manufacture Service]]. **Sync Google Sheets sudah dihapus** — master bahan & angka stok kini dari **Accurate** (read-only), barang jadi & bundle dari **data HPP**, formula dari **import Excel**. Transaksi = sumber kebenaran pergerakan di Mongo (mutasi atomik via replica-set transaction).
- **Integrasi**:
	- [[External - Accurate]] — **sumber master bahan & angka stok, READ-ONLY** (lewat [[Microservices - Integration Service]]) — *sudah jalan*; WMS tak pernah push balik. Dua arah ditunda sampai ada koordinasi manufacture↔finance (risiko dobel-hitung)
	- [[GA - Procurement System]] — kekurangan → pengadaan/PO — *rencana*
	- [[APP - MyBharata]] — input stock opname & foto barang rusak/ED — *rencana*
	- [[Microservices - Notification Service]] — notifikasi (stok rendah, kekurangan, opname) — *rencana*
	- [[Microservices - Employee Service]] — audit (pencatatan oleh siapa) — *sudah: header `BIP-Employee-ID`/`BIP-Username` → `manufacture_audit_log`*
- **UI**: modul **manufacture** di [[APP - Web ERP]] (`erp-frontend/src/features/manufacture`)

## Rollout Bertahap

- [x] **Fase 1** — Master material (bahan + produk) terstandar + stok (snapshot) + transaksi in/out ✅ *(sumber master sudah pindah dari Google Sheets ke Accurate/HPP; per-gudang & kekurangan otomatis masih TBD)*
- [~] **Fase 2** — BOM/resep ✅ (import Excel header-driven, layout NEW FORMULA FIX; mendukung dua varian Formula 1/2); kebutuhan otomatis dari rencana produksi (hybrid + override manual) — *belum*
- [~] **Fase 3** — Integrasi Accurate: **baca stok bahan & barang jadi sudah jalan (satu arah)** ✅; tulis balik ke Accurate + stock opname digital (selisih, karantina, berita acara) — *belum*
- [ ] **Fase 4** — Inbound/outbound digital + multi-gudang/dispatch; `manufacture-service` jadi **source of truth** stok

## Catatan Migrasi & Belum Diputuskan (TBD)

- **Migrasi data spreadsheet** butuh cleanup: kode belum terstandar, KATEGORI tercampur (supplier/batch/produk), satuan tidak konsisten, dan **anomali nilai** (mis. MENTHOL CRYSTAL ±18,8 juta gram ≈ 76% total stok — perlu diverifikasi)
- ~~Konversi & konsistensi **satuan** (gram/kg vs pcs)~~ → **terjawab saat integrasi Accurate**: Accurate menyimpan bahan curah dalam **KG**, WMS memakai **GRAM** → sync mengalikan 1000 untuk satuan GRAM (PCS/LITER/ROL/KG apa adanya). Kasus yang tak bisa disimpulkan dari satuan dipakaikan `faktor_stok_accurate` per-item (mis. cangkang kapsul: Accurate ribuan butir, WMS PCS → 1000). Detail: [[Microservices - Manufacture Service]]. Sisa: satuan master yang salah entri dilaporkan tiap sync lewat `satuan_perlu_dicek`
- **Multi-gudang** vs gudang tunggal — sementara: identitas gudang di level spreadsheet master (Utama = sheet bahan "GUDANG MANUFACTURE", Tinggar = sheet barang "GUDANG TINGGAR JAYA"; Elit = pemasok saja; Sadewa = titipan, dihitung dari transaksi); stok per-gudang sejati (ledger per lokasi) masih TBD
- ~~Ownership sistem: PPIC vs Warehouse vs Manufacture~~ → **dok diletakkan di domain Manufacture** (ownership condong Manufacture; peran Warehouse/PPIC tetap terlibat di operasional)
- Apakah stok **barang jadi** dikelola di sini atau di sisi Sales/distribusi

## Dependensi / Dokumen Terkait

- [[Microservices - Manufacture Service]] (implementasi) · [[API - Manufacture Service]] (endpoint)
- [[Manufacture - Issue Material Miss Count]] · [[Manufacture - Issue ED Material after Stock Opname]] — issue produksi yang dijawab sistem ini
- **Flow source (Mermaid)**: [[Manufacture - Order Production Workflow (Flow Source)]] · [[Manufacture - Stok Pengecekan Fisik (Flow Source)]]
- [[WH - Management System]] · [[WH - Inbound (Receiving)]] · [[WH - Outbound (Sending)]]
- [[GA - Procurement System]]
- [[External - Accurate]] · [[APP - MyBharata]] · [[APP - Web ERP]]
