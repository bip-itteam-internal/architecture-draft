# product.publish_item_to_outlet_shop

- Path: `/api/v2/product/publish_item_to_outlet_shop`
- Method: POST
- Auth: shop
- Deskripsi: This API supports publishing an existing item from the mart shop to an outlet shop.
- Sumber: open.shopee.com/documents/v2/product.publish_item_to_outlet_shop?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `mart_item_id` | int64 | ya | The item ID of the product in the Mart shop to be published to the outlet shop. |
| `outlet_shop_id` | int64 | ya | The shop ID of the outlet shop where the product will be published. |
| `publish_item` | object | ya | Configuration details for publishing the product to the outlet shop, including model mapping, pricing, stock, logistics, and purchase limits. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `message` | string | Indicate error type if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.item_id` | int64 | The outlet item ID. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
