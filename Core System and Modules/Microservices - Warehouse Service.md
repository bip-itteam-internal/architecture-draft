## Deskripsi

*Microservice **warehouse-service** — WMS Tinggarjaya fulfillment MVP: event ingestion, state machine fulfillment, reconciler periodik, dan operasi gudang approve/pick/pack/RTS/label/dashboard. Implementasi nyata dari konsep [[WH - Fulfillment Flow & WMS Tinggarjaya]].*

- **Stack**: Go + Fiber v2 + MongoDB (driver resmi) + Redis (via redsync distributed lock) + shared-library; di belakang [[CORE - API Master Gateway]] (`/api/warehouse/*`), route internal dilindungi `BIP-Gateway-ID`.
- **Path di repo**: `bip-erp/services/warehouse/` · flat package `main` · `models.go` (state machine) · `fulfillment_event.go` (event ingestion) · `reconciler.go` (sync 60s) · `fulfillment_ops.go` (operasi WMS + role guard).
- **Port**: `6980` (default). **Database**: `warehouse_db` (MongoDB per-service). **Env kunci**: `MONGO_URI`, `MONGO_DB`, `REDIS_URL`, `INTERNAL_GATEWAY_KEY`, `INTEGRATION_MODULE_URL`.
- **Status**: ⚠️ Implemented (ada catatan) — event ingestion + reconciler (Task 4) ✅; operasi WMS approve/pick/pack/rts/labels/dashboard (Task 7) ✅; master produk CRUD + frontend belum.
- **API**: [[API - Warehouse Service]].

## Endpoint / Fitur (Sudah Diimplementasikan)

Daftar rute lengkap di [[API - Warehouse Service]]. Ringkas:

### Event Ingestion & Reconciler

- **`POST /fulfillment/events`** — terima event order dari integration service. Idempoten upsert by `order_id + channel`; abaikan bila `update_time` lebih lama (watermark). Buat order baru `StatusWMS: NEW` bila `status_mp = TO_SHIP`. Propagasi CANCELLED ke order WMS yang belum final. Dilindungi gateway key middleware.
- **Reconciler 60s** — goroutine poll `GET {INTEGRATION_MODULE_URL}/transactions/orders/list?status=TO_SHIP` setiap 60 detik. Redis distributed lock (`lock:warehouse-reconciler`, TTL 50s) cegah concurrent run antar-pod. Cursor watermark tersimpan di `sync_cursors` (ID: `warehouse-reconciler`), overlap 5 menit untuk catch-up event yang hilang.
- **`GET /health`** — health check.

### Operasi WMS (Task 7 — `fulfillment_ops.go`)

Role guard via `system_roles["warehouse"]` (header `BIP-System-Roles` dari gateway): `admin_gudang`, `leader`, `spv` (operasional penuh); `admin_qc` (read-only: queue + dashboard).

- **`GET /fulfillment/queue?status=`** — antrian order, filter opsional by `status_wms`, diurutkan `created_at ASC`. Role: admin_gudang, leader, spv, admin_qc.
- **`POST /fulfillment/approve`** — batch approve `order_ids[]`; NEW/HELD → APPROVED. Catat `approved_by/at`. Non-all-or-nothing: kembalikan `{transitioned, skipped, failed}`.
- **`POST /fulfillment/hold`** — batch hold `order_ids[]`; NEW/APPROVED → HELD. Opsional `note` di history.
- **`POST /fulfillment/pick`** — batch konfirmasi picking `order_ids[]`; APPROVED → PICKING. Catat `picked_by/at`.
- **`POST /fulfillment/pack`** — verifikasi scan barcode `scanned_items[]` vs `order.Items` (SKU+qty harus cocok persis); PICKING → PACKED. Catat `packed_by/at`. Mismatch → HTTP 422 + detail.
- **`POST /fulfillment/rts`** — batch RTS; proxy ke integration `POST /fulfillment/ship-batch`. Partial result per order: sukses → RTS_OK + AWB; gagal → RTS_FAILED + `rts_error`. Role: admin_gudang, leader, spv.
- **`POST /fulfillment/labels`** — proxy ke integration `POST /fulfillment/labels`; jika integration 200 OK, update order yang bisa → LABEL_PRINTED + `label_printed_at`. Shopee bersifat async (PROCESSING → FE retry).
- **`GET /fulfillment/dashboard`** — MongoDB `$group by status_wms + $sum 1`; kembalikan `{data:[{status,count}], counts:{STATUS:N}}`. Role: admin_gudang, leader, spv, admin_qc.

## Model Data (`warehouse_db`)

3 collection, grounded ke `models.go`:

- `fulfillment_orders` — state machine per order marketplace. Field: `order_id`, `channel`, `shop_id`, `shop_name`, `order_status_mp`, `status_wms`, `items[]{sku, barcode, nama, qty, rak}`, `update_time` (watermark), `approved_by/at`, `picked_by/at`, `packed_by/at`, `awb`, `rts_at`, `rts_error`, `label_printed_at`, `handed_over_at`, `history[]{actor, at, from, to, note}`, `created_at`, `updated_at`. **Index**: `{order_id, channel}` unique compound, `{status_wms}`, `{update_time}`.
- `warehouse_products` — master SKU + lokasi rak. Field: `sku`, `barcode`, `nama`, `lokasi_rak`. CRUD manual (Task 5–9).
- `sync_cursors` — watermark reconciler (koleksi bersama dengan pola integration service).

## State Machine `status_wms`

```
NEW → APPROVED → PICKING → PACKED → RTS_OK → LABEL_PRINTED → HANDED_OVER
                                   ↘ RTS_FAILED → RTS_OK (retry)
NEW / APPROVED → HELD → APPROVED / CANCELLED
semua status pra-HANDED_OVER → CANCELLED
```

Implementasi: `CanTransition(to string) bool` di `models.go` — dipanggil setiap transisi status.

## Keputusan Teknis (grounded)

- **Flat package `main`**: semua file di `services/warehouse/` root, tidak ada sub-package. Konsisten dengan pola service lain di bip-erp.
- **`doUpsert` shared function**: logika upsert MongoDB (cek watermark, insert baru, cancel propagation, update status_mp) diekstrak ke `doUpsert(ctx, payload, actor)` — dipanggil handler HTTP dan reconciler tanpa network hop ke diri sendiri.
- **Redis guard graceful**: `startReconciler()` log warning dan return (tanpa crash) bila `REDIS_URL` kosong — memudahkan run dev lokal tanpa Redis.
- **`InternalURL` diisi saat init**: `map[string]string{common.Env.IntegrationModuleURL: os.Getenv(...)}` — `validation.ValidateInternalURL` panic bila kosong (proteksi boot-time).

## Belum Diimplementasikan / Catatan (TBD)

- `CRUD /products` + `/products/import` — master SKU + lokasi rak + import xlsx (Task 8/9)
- Frontend modul `warehouse` di erp-frontend — belum ada
- Container `Warehouse-MongoDB` + gateway route `/api/warehouse/*` + docker-compose entry — belum dikonfigurasi
- `package_id` tidak disimpan di `fulfillment_orders` — FE harus kirim `package_id` untuk TikTok saat RTS dan labels; Shopee tidak butuh.
- Label Shopee bersifat async 3-langkah (create → poll → download) — FE harus retry order yang masih PROCESSING.
- `POST /fulfillment/labels` menggunakan POST (bukan GET) sesuai implementasi integration; brief awal menetapkan GET tetapi diubah karena TikTok memerlukan `package_id` per order.

## Dependensi & Integrasi

- [[CORE - API Master Gateway]] (routing + gateway key middleware)
- [[Microservices - Integration Service]] — sumber order TO_SHIP (pull via reconciler + push via hook); endpoint internal ship-batch + labels (dibangun Task 5+)
- [[External - Accurate]] — hilir settlement (tidak langsung dari warehouse)
- [[WH - Fulfillment Flow & WMS Tinggarjaya]] — arsitektur lengkap + gap analysis
- [[DB - Overview and Notes]] · [[APP - Web ERP]] (frontend modul warehouse — TBD)

## Dokumen Terkait

- [[WH - Fulfillment Flow & WMS Tinggarjaya]] · [[API - Warehouse Service]]
- [[Microservices - Integration Service]] · [[IT - Background Jobs & Schedulers]]
