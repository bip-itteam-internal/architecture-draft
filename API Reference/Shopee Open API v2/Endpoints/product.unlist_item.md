# product.unlist_item

- Path: `/api/v2/product/unlist_item`
- Method: POST
- Auth: shop
- Deskripsi: Unlist item.
- Sumber: open.shopee.com/documents/v2/product.unlist_item?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_list` | object[] | ya | Length should be between 1 to 50. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier of the API request for error tracking. |
| `response` | object |  |
| `response.failure_list` | object[] |  |
| `response.failure_list[].item_id` | int64 | Failed item id |
| `response.failure_list[].failed_reason` | string | Failed reason |
| `response.success_list` | object[] |  |
| `response.success_list[].item_id` | int64 | Success item id |
| `response.success_list[].unlist` | boolean | Whether the item is unlisted |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
