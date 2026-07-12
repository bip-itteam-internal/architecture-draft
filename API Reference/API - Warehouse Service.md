## Deskripsi

*Endpoint **warehouse-service** (WMS Tinggarjaya fulfillment MVP: event ingestion, state machine, reconciler, operasi gudang). Gateway: `/api/warehouse/*`. Grounded ke `services/warehouse/`.*

- **Implementasi**: [[Microservices - Warehouse Service]] · **Status**: ⚠️ Partial (event ingestion ✅ Task 4; operasional WMS ✅ Task 7; produk CRUD 🟡 belum)
- **Indeks**: [[API - Index]] · Auth: gateway key `BIP-Gateway-ID` untuk semua route. Operasional WMS tambahan: role guard via `BIP-System-Roles` header (`system_roles["warehouse"]`).

## Fulfillment — Event Ingestion (✅ Diimplementasikan)

| Method | Path | Fungsi |
|---|---|---|
| POST | `/fulfillment/events` | Terima event order dari integration service. Idempoten upsert by `order_id + channel`; abaikan bila `update_time` ≤ existing. Buat `status_wms: NEW` untuk order TO_SHIP baru. Propagasi CANCELLED ke order WMS yang belum final (HANDED_OVER/CANCELLED). |
| GET | `/health` | Health check |

**Request body** `POST /fulfillment/events`:
```json
{
  "order_id":    "string (wajib)",
  "channel":     "string (wajib) — tiktok / shopee",
  "shop_id":     "string",
  "shop_name":   "string",
  "status":      "string — TO_SHIP / CANCELLED / dll",
  "update_time": "int64 (unix timestamp)",
  "items": [{ "sku": "string", "qty": "int" }]
}
```

**Response**:
- `201 Created` + `{"action": "created"}` — order baru berhasil dibuat
- `200 OK` + `{"action": "updated"}` — status_mp diperbarui
- `200 OK` + `{"action": "cancelled"}` — cancel propagasi berhasil
- `200 OK` + `{"action": "skipped", "reason": "stale_event"}` — update_time lebih lama
- `200 OK` + `{"action": "skipped", "reason": "already_final"}` — cancel tapi sudah HANDED_OVER/CANCELLED
- `200 OK` + `{"action": "ignored", "reason": "not_to_ship"}` — order baru tapi bukan TO_SHIP
- `400 Bad Request` — body tidak valid atau `order_id`/`channel` kosong
- `401 Unauthorized` — gateway key tidak cocok

## Fulfillment — Operasi WMS (✅ Diimplementasikan — Task 7)

Auth tambahan: `BIP-System-Roles` header (JSON map), key `"warehouse"`, value = role string.

| Method | Path | Role yang Diizinkan | Fungsi |
|---|---|---|---|
| GET | `/fulfillment/queue` | admin_gudang, leader, spv, admin_qc | Antrian order, filter `?status=`, sort created_at ASC |
| POST | `/fulfillment/approve` | admin_gudang, leader, spv | Batch approve → APPROVED |
| POST | `/fulfillment/hold` | admin_gudang, leader, spv | Batch hold → HELD |
| POST | `/fulfillment/pick` | admin_gudang, leader, spv | Batch konfirmasi picking → PICKING |
| POST | `/fulfillment/pack` | admin_gudang, leader, spv | Verifikasi scan SKU+qty per order → PACKED |
| POST | `/fulfillment/rts` | admin_gudang, leader, spv | Batch RTS → proxy integration ship-batch |
| POST | `/fulfillment/labels` | admin_gudang, leader, spv | Proxy integration labels → LABEL_PRINTED |
| GET | `/fulfillment/dashboard` | admin_gudang, leader, spv, admin_qc | Aggregate count per status_wms |

### Request / Response

**`GET /fulfillment/queue`**
- Query: `?status=NEW` (opsional, nilai bebas — dicocokkan ke `status_wms`)
- Response `200`: `{"data": [FulfillmentOrder...]}`

**`POST /fulfillment/approve` / `/hold` / `/pick`** (pola sama):
```json
// Request
{ "order_ids": ["ORDER_A", "ORDER_B"], "note": "opsional" }
// Response 200
{ "transitioned": ["ORDER_A"], "skipped": ["ORDER_B"], "failed": [] }
```
- `skipped`: order yang tidak bisa transisi per state machine (`CanTransition` false)
- `failed`: order tidak ditemukan di DB atau error update

**`POST /fulfillment/pack`**:
```json
// Request
{
  "order_id": "ORDER_A",
  "scanned_items": [{"sku": "SKU-001", "qty": 2}, {"sku": "SKU-002", "qty": 1}]
}
// Response 200
{ "action": "packed", "order_id": "ORDER_A" }
// Response 422 (SKU/qty mismatch)
{ "error": "verifikasi SKU/qty gagal", "mismatches": [{"sku": "SKU-001", "expected": 2, "got": 1}] }
```
- `409`: order tidak bisa transisi ke PACKED (status saat ini bukan PICKING)

**`POST /fulfillment/rts`**:
```json
// Request — package_id diperlukan untuk TikTok; Shopee boleh kosong
{ "orders": [{"order_id": "ORDER_A", "package_id": "PKG_123"}] }
// Response 200 — partial result per order
{ "data": [{"order_id": "ORDER_A", "channel": "tiktok", "success": true, "awb": "JNE123"}] }
```
- `502`: integration service tidak bisa dihubungi

**`POST /fulfillment/labels`**:
```json
// Request
{ "orders": [{"order_id": "ORDER_A", "package_id": "PKG_123"}] }
// Response — proxy langsung dari integration
{ "status": "success", "data": [{"order_id": "ORDER_A", "channel": "tiktok", "status": "READY", "url": "https://..."}] }
```
- Label status: `READY` | `PROCESSING` (Shopee async, FE harus retry) | `FAILED`
- Jika response integration 200 OK → order yang bisa transisi diupdate ke `LABEL_PRINTED`

**`GET /fulfillment/dashboard`**:
```json
// Response 200
{
  "data": [{"status": "APPROVED", "count": 5}, {"status": "NEW", "count": 12}],
  "counts": {"APPROVED": 5, "NEW": 12, "PACKED": 3}
}
```

### Error Umum (semua endpoint operasional)

| Code | Keterangan |
|---|---|
| 400 | Body tidak valid atau `order_ids`/`orders` kosong |
| 401 | `BIP-Employee-ID` header kosong |
| 403 | `system_roles["warehouse"]` tidak ada dalam daftar role yang diizinkan |
| 404 | Order tidak ditemukan (pack only) |
| 409 | Transisi tidak valid per state machine (pack only) |
| 422 | SKU/qty mismatch (pack only) |
| 502 | Integration service tidak bisa dihubungi (rts, labels) |

## Master Produk (🟡 Belum Diimplementasikan)

| Method | Path | Fungsi |
|---|---|---|
| GET/POST/PUT/DELETE | `/products` · `/products/:id` | CRUD master SKU + lokasi rak |
| POST | `/products/import` | Import xlsx master produk |

## Dokumen Terkait

- [[Microservices - Warehouse Service]] · [[WH - Fulfillment Flow & WMS Tinggarjaya]] · [[API - Integration Service]] · [[API - Index]]
