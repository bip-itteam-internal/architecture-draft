# Microservices - Inventory Service

## Deskripsi

_Inventory Service adalah microservice untuk manajemen **aset/inventaris General Affairs (GA)** — mengelola item peralatan beserta spesifikasi, pemegang (heldBy), dokumen pembelian/kedatangan, serta riwayat perbaikan/maintenance. Fokusnya adalah pelacakan **aset** (asset tracking), bukan stok-kuantitas gudang._

- **Stack:** Go + Fiber v2 + MongoDB + MinIO
- **Path:** `services/inventory`
- **Status:** ✅ Implemented penuh

## Endpoint / Fitur (Sudah Diimplementasikan)

- **Health check:** `GET /health`
- **Data-type / enum master:** `GET /master-items`, `GET /data-type/category`, `GET /data-type/electronics`, `GET /data-type/item-status`, `GET /data-type/repair`, `GET /data-type/service`, `GET /data-type/repair-status`, `GET /data-type/component-action`
- **Group `/item`** (di-gate dengan `RequireGeneralAffair`):
  - `GET /item/master/:master_id/spec-template` — ambil template spesifikasi per master
  - `POST /item/` — create item; auto-create/reuse `DataMaster`, generate ID dengan pola `INV-MMYY-NAMA-n`, melakukan validasi spec dan `heldBy`
  - `POST /item/upload/presigned-url` + `GET /item/upload/presigned-get` — MinIO presigned URL (upload/get)
  - `GET /item/:id` — detail item
  - `PATCH /item/:id` — partial update
  - `DELETE /item/:id` — hapus item
- **List item:** `GET /items` — list dengan `$lookup` ke master + filter `?status`
- **Repair history** (`/item/repair`):
  - `POST /item/repair/:item_id` — tambah riwayat perbaikan; sinkron status ke item induk
  - `GET /item/repair/:item_id/all` — semua riwayat perbaikan untuk satu item
  - `GET /item/repair/:repair_id` — detail satu record perbaikan
- **Summary / reporting:** `GET /summary` — agregasi `$facet` per category/status/department + new-arrivals 30 hari terakhir

## Belum Diimplementasikan / Catatan

- Tidak ada stub — CRUD lengkap, workflow repair, dan reporting sudah komplet.
- `InternalURL` kosong; service ini **tidak memanggil service lain**.
- Minor: terdapat 2 baris `fmt.Println("DEBUG...")` di `validation.go`.
- Beberapa struct/helper validasi tertentu tampak sebagian tidak terpakai (dead code minor).

## Dependencies & Integrasi

- **MongoDB** — collection: `inventory`, `data_master`, `repair_history`.
- **MinIO** — diakses langsung untuk presigned URL serta upload image/PDF (limit 4MB). Lihat [[Microservices - File Service]].
- Diekspos via gateway — lihat [[CORE - API Master Gateway]].
- Skema database — lihat [[DB - Overview and Notes]].

## Dokumen Terkait

- [[GA - Inventory Management]]
