# product.batch_publish_item_to_outlet_shop

- Path: `/api/v2/product/batch_publish_item_to_outlet_shop`
- Method: POST
- Auth: shop
- Deskripsi: Create asynchronous task to batch publish outlet item
- Sumber: open.shopee.com/documents/v2/product.batch_publish_item_to_outlet_shop?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_list` | object[] | ya | The item list to batch publish to Outlet shop. The list size must be between 1 and 100. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.task_id` | int64 | The task ID of the batch publish outlet item task. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
