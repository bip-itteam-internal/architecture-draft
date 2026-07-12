## Deskripsi

*Endpoint **warehouse-service** (WMS Tinggarjaya fulfillment MVP: event ingestion, state machine, reconciler). Gateway: `/api/warehouse/*`. Grounded ke `services/warehouse/`.*

- **Implementasi**: [[Microservices - Warehouse Service]] · **Status**: ⚠️ Partial (Task 4 done; Task 5–9 belum)
- **Indeks**: [[API - Index]] · Auth: gateway key `BIP-Gateway-ID` untuk semua route `/fulfillment/*`.

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

## Fulfillment — Operasi WMS (🟡 Belum Diimplementasikan — Task 5–9)

| Method | Path | Fungsi |
|---|---|---|
| GET | `/fulfillment/queue` | Antrian order per `status_wms` |
| POST | `/fulfillment/approve` | Batch approve NEW → APPROVED |
| POST | `/fulfillment/hold` | Tahan order → HELD |
| POST | `/fulfillment/pick` | Konfirmasi picking per order → PICKING |
| POST | `/fulfillment/pack` | Verifikasi scan barcode SKU + qty → PACKED |
| POST | `/fulfillment/rts` | RTS batch → proxy integration `/fulfillment/ship-batch` |
| GET | `/fulfillment/labels` | Cetak label → proxy integration `/fulfillment/labels` |
| GET | `/fulfillment/dashboard` | Kartu antrian, resi keluar, cancel, RTS gagal |

## Master Produk (🟡 Belum Diimplementasikan — Task 5–9)

| Method | Path | Fungsi |
|---|---|---|
| GET/POST/PUT/DELETE | `/products` · `/products/:id` | CRUD master SKU + lokasi rak |
| POST | `/products/import` | Import xlsx master produk |

## Dokumen Terkait

- [[Microservices - Warehouse Service]] · [[WH - Fulfillment Flow & WMS Tinggarjaya]] · [[API - Integration Service]] · [[API - Index]]
