# order.cancel_order

- Path: `/api/v2/order/cancel_order`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to cancel an order. This action can only be performed before the order has been shipped.
- Sumber: open.shopee.com/documents/v2/order.cancel_order?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn` | string | ya | Shopee's unique identifier for an order. Contoh: `201020SQQ5K2EP` |
| `cancel_reason` | string | ya | The reason seller want to cancel this order. Applicable values: OUT_OF_STOCK CUSTOMER_REQUEST UNDELIVERABLE_AREA (Note: Only apply for TW and MY) COD_NOT_SUPPORTED Contoh: `OUT_OF_STOCK` |
| `item_list` | object[] | tidak | Required when cancel_reason is OUT_OF_STOCK. |
| `partial_cancel_item_list` | object[] | tidak | The list of item models and quantities that the seller wants to partially cancel. This field should be provided when the seller intends to cancel only part of the order due to unavailable items while continuing to fulfill the remaining items. |

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
