# product.boost_item

- Path: `/api/v2/product/boost_item`
- Method: POST
- Auth: shop
- Deskripsi: Boost item.
- Sumber: open.shopee.com/documents/v2/product.boost_item?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id_list` | int64[] | ya | Shopee's unique identifier for an item, limit:[1,5] |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.failure_list` | object[] |  |
| `response.failure_list[].item_id` | int64 | Failed item ID. |
| `response.failure_list[].failed_reason` | string | Reason for failure. |
| `response.success_list` | object |  |
| `response.success_list.item_id_list` | int64[] | Success item ID. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
