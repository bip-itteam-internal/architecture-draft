# Microservices - Inventory Service

## Deskripsi

_Inventory Service adalah microservice untuk manajemen **aset/inventaris General Affairs (GA)** — mengelola item peralatan beserta spesifikasi, pemegang (heldBy), dokumen pembelian/kedatangan, serta riwayat perbaikan/maintenance. Fokusnya adalah pelacakan **aset** (asset tracking), bukan stok-kuantitas gudang._

- **Stack:** Go + Fiber v2 + MongoDB + MinIO
- **Path:** `services/inventory`
- **Status**: ✅ Implemented penuh

## Endpoint / Fitur (Sudah Diimplementasikan)

- **Health check:** `GET /health`
- **Data-type / enum master:** `GET /master-items`, `GET /data-type/category`, `GET /data-type/electronics`, `GET /data-type/item-status`, `GET /data-type/repair`, `GET /data-type/service`, `GET /data-type/repair-status`, `GET /data-type/component-action`
- **Kategori (registry `category`):** `GET /categories` (daftar untuk saran), `POST /categories` (daftar kategori baru — gate `RequireGeneralAffair`). Kategori bersifat **bebas-ketik**; disimpan apa adanya, dedup case-insensitive (`name_key`). Di-seed saat startup (`seedCategories`, unique index `name_key`). Lihat Catatan.
- **Group `/item`** (di-gate dengan `RequireGeneralAffair`):
  - `GET /item/master/:master_id/spec-template` — ambil template spesifikasi per master
  - `POST /item/` — create item; auto-create/reuse `DataMaster`, generate ID dengan pola **`INV-BIP-DDMMYY-NAMA-n`** (DDMMYY dari `purchase_date` dibaca **WIB**, fallback waktu sekarang; `NAMA` = `item_name` di-UPPERCASE tanpa spasi, maks 20 char; `n` = increment per prefix), validasi spec & `heldBy`, dan verifikasi dokumen ada di MinIO sebelum simpan
  - `POST /item/upload/presigned-url` + `GET /item/upload/presigned-get` — MinIO presigned URL (upload/get); nama objek dibersihkan (`sanitizeObjectName`)
  - `GET /item/:id` — detail item
  - `PATCH /item/:id` — partial update
  - `DELETE /item/:id` — hapus item
- **List item:** `GET /items` — list dengan `$lookup` ke master + filter `?status`
- **Repair history** (`/item/repair`):
  - `POST /item/repair/:item_id` — tambah riwayat perbaikan; sinkron status ke item induk
  - `GET /item/repair/:item_id/all` — semua riwayat perbaikan untuk satu item
  - `GET /item/repair/:repair_id` — detail satu record perbaikan
  - `PATCH /item/repair/:repair_id` — edit satu record perbaikan (`UpdateRepairHistory`)
- **Summary / reporting:** `GET /summary` — agregasi `$facet` per category/status/department + new-arrivals 30 hari terakhir + **agregasi biaya** (`total_purchase_cost` dari `purchase_price`, `total_repair_cost` dari `repair_history`)

## Belum Diimplementasikan / Catatan

- Tidak ada stub — CRUD lengkap, workflow repair, dan reporting sudah komplet.
- `InternalURL` kosong; service ini **tidak memanggil service lain**.
- **Kategori & nama barang bebas-ketik**: frontend kini memakai input teks manual (dropdown/saran dihapus). Backend tetap mendaftarkan kategori ke koleksi `category` via `resolveCategory` saat create, sehingga koleksi & endpoint `/categories` kini **vestigial** untuk UI (masih terisi, tidak lagi dibaca dropdown). Nama & kategori disimpan **apa adanya** (trim + rapikan spasi), dedup master **case-insensitive**; hanya **ID** yang di-UPPERCASE.
- **Integritas dokumen (anti `NoSuchKey`)**: `CreateInventory`/`UpdateInventory` memanggil `ValidateDocumentsExists` (MinIO `StatObject`) → tolak `400` bila objek tidak ada, mencegah referensi menggantung. `GeneratePresignedURL` membersihkan nama objek (`sanitizeObjectName`). Catatan operasional: presigned di-sign untuk `MINIO_PUBLIC_BASE_URL`; jika app HTTPS sementara nilai ini HTTP → upload diblokir *mixed-content* (perbaiki di infra, bukan kode).
- **ID pakai WIB**: komponen tanggal ID dibaca `time.FixedZone("WIB", +7)` agar tidak mundur 1 hari dari tanggal yang tampil (frontend kirim ISO UTC).

## Dependencies & Integrasi

- **MongoDB** — collection: `inventory`, `data_master`, `repair_history`, `category`.
- **MinIO** — diakses langsung untuk presigned URL serta upload image/PDF (limit 4MB); objek diverifikasi ada sebelum referensinya disimpan. Lihat [[Microservices - File Service]].
- Diekspos via gateway — lihat [[CORE - API Master Gateway]].
- Skema database — lihat [[DB - Overview and Notes]].

## Dokumen Terkait

- [[GA - Inventory Management]]
