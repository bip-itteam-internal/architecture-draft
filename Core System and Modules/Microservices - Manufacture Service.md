## Deskripsi

*Microservice **manufacture-service** — WMS manufaktur (warehouse/produksi): master bahan baku & produk, stok, transaksi in/out, formula/BOM, produksi, material order, PO marketing/procurement, proposal koreksi, dan audit log. Master di-sync dari **Google Sheets** (via service account); data operasional (transaksi, stok) **sumber kebenaran di MongoDB**. Implementasi nyata dari konsep [[Manufacture - Stock & Material Management]].*

- **Stack**: Go + Fiber v2 + MongoDB (driver resmi) + shared-library; di belakang [[CORE - API Master Gateway]] (`/api/manufacture/*`), auth via header gateway (lihat [[CORE - SSO Flow]]).
- **Path di repo**: `bip-erp/services/manufacture/` · models: `bip-erp/shared-library/models/manufacture/models.go` · FE modul: `erp-frontend/src/features/manufacture/`.
- **Port**: `6978` (`MANUFACTURE_SERVICE_PORT`). **Database**: `manufacture_db` (Mongo per-service, **replica set 1-node** `rs-manufacture` + keyfile auth).
- **Status**: ✅ Implemented (Fase 1 master/stok/transaksi/formula sync jalan; entitas produksi/PO/proposal ada di kode).
- **API**: [[API - Manufacture Service]].

## Endpoint / Fitur (Sudah Diimplementasikan)

Daftar rute lengkap di [[API - Manufacture Service]]. Ringkas:

- **Master bahan & produk** — list/detail + `POST /sync` (tarik dari Google Sheet) + `PATCH status` (active/discontinued, dengan audit).
- **Stok** — snapshot per kode + `POST /stok/reconcile` (rekonsiliasi snapshot vs transaksi).
- **Transaksi** — INBOUND/OUTBOUND; mengubah stok **atomik** (Mongo transaction).
- **Formula/BOM** — CRUD + `POST /formula/sync` (tarik resep dari Sheet via service account).
- **Produksi** — order produksi (konsumsi stok) + production-log (catatan tanpa konsumsi).
- **PO & Proposal** — marketing-po, procurement-po (status workflow + audit), proposal approve/reject.
- **Audit log** — `GET /audit-log` (siapa mengubah apa, per aksi/target).

## Model Data (`manufacture_db`)

12 collection (prefix `manufacture_`), grounded ke `models.go`:

- `manufacture_master_bahan` — master bahan baku (`_id`=kode, nama, kategori, satuan, min_stok, stok_awal dari Sheet, status app-managed).
- `manufacture_master_product` — master produk/bahan kemas (kode, jenis_barang, kategori_produk, status).
- `manufacture_stok` — snapshot stok per kode.
- `manufacture_transaksi` — transaksi in/out (sumber kebenaran pergerakan stok).
- `manufacture_formula` — resep/BOM (product_name + ingredients[kode_bahan, nama, qty_needed]).
- `manufacture_sync_log` — riwayat sync Sheet (tipe: master/product/formula).
- `manufacture_production_log` · `manufacture_material_order` · `manufacture_marketing_po` · `manufacture_procurement_po` · `manufacture_proposal`.
- `manufacture_audit_log` — jejak perubahan oleh user (dari header `BIP-Employee-ID`/`BIP-Username`).

## Keputusan Teknis (grounded)

- **Stok = opening-balance-as-transaction + reconcile**: stok awal dari Sheet (STOK GUDANG) di-seed sebagai transaksi OPENING, bukan snapshot langsung → rekonsiliasi konsisten (snapshot = jumlah semua transaksi). Mutasi stok pakai **Mongo multi-document transaction** (butuh replica set; itu sebab `manufacture_db` dijadikan RS 1-node + keyfile).
- **Master dari Google Sheets (3 file terpisah)** via **service account** (`SHEETS_SA_KEY` base64, scope readonly): bahan baku, produk, formula. Tiap sync upsert ke koleksi + catat sync-log + audit. Service account lebih aman dari gviz publik (sheet tak perlu "anyone with link"). Sheet wajib di-share ke email SA (Viewer).
- **Tagged logging** `[Manufacture <Event>]` untuk identifikasi di monitoring Docker.
- **Audit log** merekam user login terakhir yang mengubah data di tab mana pun (header gateway).
- **FE**: modul `manufacture` di [[APP - Web ERP]] (Next.js, `erp-frontend/src/features/manufacture`), 10 view (gudang bahan baku/jadi, stok, produksi, PO, KPI, dll). Field Go snake_case di-map ke legacy camelCase di mapper container.

## Belum Diimplementasikan / Catatan (TBD)

- Perhitungan kebutuhan→kekurangan otomatis dari rencana produksi (Fase 2 di [[Manufacture - Stock & Material Management]]) — sebagian (formula ada, planning belum penuh).
- Multi-gudang/lokasi + karantina ED, stock opname digital, integrasi [[External - Accurate]] — masih konsep.
- Master `stok_awal` tersimpan 0 saat upsert master (kosmetik; snapshot stok benar ter-seed dari STOK GUDANG).
- **Temuan audit kode** (authz, race stok, mapper FE, seed atomik) terdaftar di [[Manufacture - Issue Code Audit 2026-06]] — perbaikan terjadwal.

## Dependensi & Integrasi

- [[CORE - API Master Gateway]] (routing + inject header identitas) · [[CORE - SSO Flow]] (auth).
- [[Microservices - Employee Service]] — sumber identitas/role (audit).
- [[GA - Procurement System]] — kekurangan → pengadaan (rencana).
- [[External - Accurate]] — tarik stok awal (rencana, hybrid bertahap).
- Google Sheets (master bahan/produk/formula) — sumber master via service account.

## Dokumen Terkait

- [[Manufacture - Stock & Material Management]] (konsep/desain) · [[API - Manufacture Service]] (endpoint)
- [[DB - Overview and Notes]] · [[APP - Web ERP]]
