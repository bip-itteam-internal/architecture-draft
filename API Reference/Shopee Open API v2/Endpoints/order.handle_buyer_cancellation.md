# order.handle_buyer_cancellation

- Path: `/api/v2/order/handle_buyer_cancellation`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to handle buyer's cancellation application.
- Sumber: open.shopee.com/documents/v2/order.handle_buyer_cancellation?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn` | string | ya | Shopee's unique identifier for an order. Contoh: `201016F6B94MQK` |
| `operation` | string | ya | The operation you want to handle.Avaiable value: ACCEPT, REJECT Contoh: `ACCEPT` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.update_time` | timestamp | The time when the order is updated. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
