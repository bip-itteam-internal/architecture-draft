# order.unsplit_order

- Path: `/api/v2/order/unsplit_order`
- Method: POST
- Auth: shop
- Deskripsi: Use this ai to undo split of order. After undo split, the order will have only one package. It can only be used when order status still at READY_TO_SHIP.
- Sumber: open.shopee.com/documents/v2/order.unsplit_order?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn` | string | ya | Shopee's unique identifier for an order. Contoh: `2012312AVA7HVN` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier of the API request for error tracking. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
