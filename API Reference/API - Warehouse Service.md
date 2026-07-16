## Deskripsi

*Endpoint **warehouse-service** (WMS Tinggarjaya fulfillment MVP: event ingestion, state machine, reconciler, operasi gudang). Gateway: `/api/warehouse/*`. Grounded ke `services/warehouse/`.*

- **Implementasi**: [[Microservices - Warehouse Service]] · **Status**: ⚠️ Implemented (ada catatan) — event ingestion ✅; operasi WMS lengkap termasuk handover ✅; master produk CRUD ✅; frontend sebagian ✅
- **Indeks**: [[API - Index]] · Auth: gateway key `BIP-Gateway-ID` untuk semua route. Operasional WMS tambahan: role guard via `BIP-System-Roles` header (`system_roles["warehouse"]`).

## Fulfillment — Event Ingestion (✅ Diimplementasikan)

| Method | Path | Fungsi |
|---|---|---|
| POST | `/fulfillment/events` | Terima event order dari integration service. Idempoten upsert by `order_id + channel`; abaikan bila `update_time` ≤ existing. Buat `status_wms: NEW` untuk order TO_SHIP baru. Propagasi CANCELLED ke order WMS yang belum final (HANDED_OVER/CANCELLED). |
| GET | `/health` | Health check |

**Request body** `POST /fulfillment/events`:
```json
{
  "order_id":         "string (wajib)",
  "channel":          "string (wajib) — tiktok / shopee",
  "shop_id":          "string",
  "shop_name":        "string",
  "status":           "string — TO_SHIP / CANCELLED / dll",
  "update_time":      "int64 (unix timestamp)",
  "recipient_name":   "string — nama penerima",
  "recipient_address":"string — alamat lengkap penerima",
  "shipping_provider":"string — nama kurir (JNE, SiCepat, dll)",
  "package_id":       "string — TikTok saja; diambil dari PackageID line-item pertama; boleh kosong untuk Shopee",
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
| GET | `/fulfillment/queue` | admin_gudang, leader, spv, admin_qc | Antrian order: filter status/q/shop_ids/tanggal+jam, sort, pagination |
| GET | `/fulfillment/queue/counts` | admin_gudang, leader, spv, admin_qc | Jumlah order per status_wms + kunci `ALL` (total) |
| GET | `/fulfillment/queue/shops` | admin_gudang, leader, spv, admin_qc | Daftar distinct toko yang ada di antrian, sort nama ASC |
| GET | `/fulfillment/queue/export` | admin_gudang, leader, spv, admin_qc | Unduh xlsx rekon (filter sama dengan queue); tandai `exported_at` |
| POST | `/fulfillment/approve` | admin_gudang, leader, spv | Batch approve → APPROVED |
| POST | `/fulfillment/hold` | admin_gudang, leader, spv | Batch hold → HELD |
| POST | `/fulfillment/pick` | admin_gudang, leader, spv | Batch konfirmasi picking → PICKING |
| POST | `/fulfillment/pack` | admin_gudang, leader, spv | Verifikasi scan SKU+qty per order → PACKED |
| POST | `/fulfillment/rts` | admin_gudang, leader, spv | Batch RTS → proxy integration ship-batch |
| POST | `/fulfillment/labels` | admin_gudang, leader, spv | Proxy integration labels → LABEL_PRINTED |
| POST | `/fulfillment/handover` | admin_gudang, leader, spv | Konfirmasi serah-terima kurir → HANDED_OVER |
| GET | `/fulfillment/dashboard` | admin_gudang, leader, spv, admin_qc | Aggregate count per status_wms |

### Request / Response

**`GET /fulfillment/queue`**
- Query (semua opsional):
  - `status=NEW` — dicocokkan ke `status_wms`
  - `q=` — regex case-insensitive ke `order_id` / `items.sku`
  - `shop_ids=id1,id2` — filter multi-toko
  - `date_from=` / `date_to=` — filter `created_at`, timezone WIB. Dua format: `2006-01-02T15:04` (dengan jam; `date_to` inklusif sampai akhir menit) atau `2006-01-02` (tanpa jam; `date_to` sampai 23:59:59.999). Format tidak valid diabaikan (graceful skip)
  - `sort=` — `created_desc` / `updated_desc`; default created_at ASC
  - `page=` (default 1), `limit=` (default 50, max 200)
- Response `200`: `{"data": [FulfillmentOrder...], "total": n, "page": n, "limit": n}`

**`GET /fulfillment/queue/export`** — unduh xlsx untuk rekap/rekon gudang:
- Query: filter sama dengan `/queue` (status, q, shop_ids, date_from/to, sort — tanpa pagination), plus `only_new=true` = hanya order yang `exported_at`-nya belum ada (rekon per batch — unduhan siang tidak membawa data pagi)
- Satu baris per item produk. Kolom: No, Nomor Pesanan, Tanggal Pesanan Masuk (WIB), No Resi (awb), SKU, Nama Barang, Qty Pesanan, Nama Toko, Expedisi, Kode Packer (`packer_code`, fallback `packed_by`), Keterangan (kosong, diisi manual)
- Efek samping: order yang ikut ter-export dicap `exported_at` + `exported_by` (sekali; unduhan ulang tidak menimpa) — **gerbang wajib sebelum RTS**
- Response `200`: file xlsx (`Content-Disposition: attachment`); `400` bila hasil filter > 20.000 order

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
// Request — packer_code opsional (kode tim harian/freelance T1/T2)
{
  "order_id": "ORDER_A",
  "scanned_items": [{"sku": "SKU-001", "qty": 2}, {"sku": "SKU-002", "qty": 1}],
  "packer_code": "T1"
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
// Response 200 — partial result per order; not_exported = order yang ditolak gerbang rekon
{ "data": [{"order_id": "ORDER_A", "channel": "tiktok", "success": true, "awb": "JNE123"}], "not_exported": [] }
// Response 422 — SEMUA order yang diminta belum ditarik datanya (gerbang rekon)
{ "error": "data pesanan belum ditarik — unduh data pesanan masuk dulu sebelum RTS/cetak resi", "not_exported": ["ORDER_A"] }
```
- **Gerbang rekon**: order dengan `exported_at` kosong ditolak — wajib unduh via `/queue/export` dulu
- Transisi valid: APPROVED → RTS_OK (jalur cepat tanpa scan) atau PACKED → RTS_OK (jalur scan); RTS_FAILED → RTS_OK (retry)
- `502`: integration service tidak bisa dihubungi

**`POST /fulfillment/labels`**:
```json
// Request — packer_code (T1/T2) dicap ke semua order batch yang transisi ke LABEL_PRINTED
{ "orders": [{"order_id": "ORDER_A", "package_id": "PKG_123"}], "packer_code": "T1" }
// Response — proxy langsung dari integration
{ "status": "success", "data": [{"order_id": "ORDER_A", "channel": "tiktok", "status": "READY", "url": "https://..."}] }
```
- Label status: `READY` | `PROCESSING` (Shopee async, FE harus retry) | `FAILED`
- Jika response integration 200 OK → order yang bisa transisi diupdate ke `LABEL_PRINTED`
- `packer_code` tidak menimpa kode yang sudah ada dari scan packing

**`GET /fulfillment/queue/counts`**:
```json
// Response 200 — map status_wms → jumlah order; "ALL" = total semua status
{"NEW": 5, "APPROVED": 3, "PICKING": 1, "PACKED": 2, "ALL": 11}
```

**`GET /fulfillment/queue/shops`**:
```json
// Response 200 — array distinct toko, sorted shop_name ASC
[{"shop_id": "123", "shop_name": "BH Official", "channel": "tiktok"}]
```

**`POST /fulfillment/handover`** (pola sama dengan approve/hold/pick):
```json
// Request
{ "order_ids": ["ORDER_A", "ORDER_B"], "note": "opsional" }
// Response 200
{ "transitioned": ["ORDER_A"], "skipped": ["ORDER_B"], "failed": [] }
```
- Transisi yang diizinkan: LABEL_PRINTED → HANDED_OVER.
- Catat `handed_over_at` timestamp pada order yang berhasil transisi.

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
| 422 | SKU/qty mismatch (pack) · semua order belum ditarik datanya (rts) |
| 502 | Integration service tidak bisa dihubungi (rts, labels) |

## Master Produk (✅ Diimplementasikan)

Auth: gateway key + role guard `system_roles["warehouse"]`. Path group `/wms/`.

| Method | Path | Role yang Diizinkan | Fungsi |
|---|---|---|---|
| GET | `/wms/products` | admin_gudang, leader, spv, admin_qc | List master SKU, filter `?q=` |
| POST | `/wms/products` | admin_gudang, leader, spv | Buat SKU baru |
| PUT | `/wms/products/:sku` | admin_gudang, leader, spv | Update data SKU |
| DELETE | `/wms/products/:sku` | admin_gudang, leader, spv | Hapus SKU |
| POST | `/wms/products/import` | admin_gudang, leader, spv | Import xlsx master produk |

## Dokumen Terkait

- [[Microservices - Warehouse Service]] · [[WH - Fulfillment Flow & WMS Tinggarjaya]] · [[API - Integration Service]] · [[API - Index]]
