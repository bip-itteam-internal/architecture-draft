## Deskripsi

*Microservice **warehouse-service** — WMS Tinggarjaya fulfillment MVP: penerima event order marketplace, state machine fulfillment, reconciler periodik, dan (fase berikut) approve/pick/pack/RTS/label. Implementasi nyata dari konsep [[WH - Fulfillment Flow & WMS Tinggarjaya]].*

- **Stack**: Go + Fiber v2 + MongoDB (driver resmi) + Redis (via redsync distributed lock) + shared-library; di belakang [[CORE - API Master Gateway]] (`/api/warehouse/*`), route internal dilindungi `BIP-Gateway-ID`.
- **Path di repo**: `bip-erp/services/warehouse/` · flat package `main` · models: `models.go` · handler event: `fulfillment_event.go` · reconciler: `reconciler.go`.
- **Port**: `6980` (default). **Database**: `warehouse_db` (MongoDB per-service). **Env kunci**: `MONGO_URI`, `MONGO_DB`, `REDIS_URL`, `INTERNAL_GATEWAY_KEY`, `INTEGRATION_MODULE_URL`.
- **Status**: ⚠️ Implemented (ada catatan) — event ingestion + reconciler jalan (Task 4); approve/pick/pack/RTS/label/produk belum diimplementasikan (Task 5–9).
- **API**: [[API - Warehouse Service]].

## Endpoint / Fitur (Sudah Diimplementasikan)

Daftar rute di [[API - Warehouse Service]]. Ringkas:

- **`POST /fulfillment/events`** — terima event order dari integration service. Idempoten upsert by `order_id + channel`; abaikan bila `update_time` lebih lama (watermark). Buat order baru `StatusWMS: NEW` bila `status_mp = TO_SHIP`. Propagasi CANCELLED ke order WMS yang belum final. Dilindungi gateway key middleware.
- **Reconciler 60s** — goroutine poll `GET {INTEGRATION_MODULE_URL}/transactions/orders/list?status=TO_SHIP` setiap 60 detik. Redis distributed lock (`lock:warehouse-reconciler`, TTL 50s) cegah concurrent run antar-pod. Cursor watermark tersimpan di `sync_cursors` (ID: `warehouse-reconciler`), overlap 5 menit untuk catch-up event yang hilang.
- **`GET /health`** — health check.

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

Tasks 5–9 belum ada di kode:

- `POST /fulfillment/approve` — batch approve NEW → APPROVED
- `POST /fulfillment/hold` — tahan order → HELD
- `GET /fulfillment/queue` — antrian per status WMS
- `POST /fulfillment/pick` / `/pack` — konfirmasi picking & scan barcode packing
- `POST /fulfillment/rts` — RTS batch → proxy integration `/fulfillment/ship-batch`
- `GET /fulfillment/labels` — cetak label → proxy integration `/fulfillment/labels`
- `GET /fulfillment/dashboard` — kartu antrian, resi keluar, cancel, RTS gagal
- `CRUD /products` + `/products/import` — master SKU + lokasi rak + import xlsx
- Integration service endpoints: `POST /fulfillment/ship-batch`, `GET /fulfillment/labels` — belum ada
- Frontend modul `warehouse` di erp-frontend — belum ada
- Container `Warehouse-MongoDB` + gateway route `/api/warehouse/*` + docker-compose entry — belum dikonfigurasi
- Hook `OnOrderUpsert` di integration service (event push realtime ke warehouse) — belum ada

## Dependensi & Integrasi

- [[CORE - API Master Gateway]] (routing + gateway key middleware)
- [[Microservices - Integration Service]] — sumber order TO_SHIP (pull via reconciler + push via hook); endpoint internal ship-batch + labels (dibangun Task 5+)
- [[External - Accurate]] — hilir settlement (tidak langsung dari warehouse)
- [[WH - Fulfillment Flow & WMS Tinggarjaya]] — arsitektur lengkap + gap analysis
- [[DB - Overview and Notes]] · [[APP - Web ERP]] (frontend modul warehouse — TBD)

## Dokumen Terkait

- [[WH - Fulfillment Flow & WMS Tinggarjaya]] · [[API - Warehouse Service]]
- [[Microservices - Integration Service]] · [[IT - Background Jobs & Schedulers]]
