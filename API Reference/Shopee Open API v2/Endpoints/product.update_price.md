# product.update_price

- Path: `/api/v2/product/update_price`
- Method: POST
- Auth: shop
- Deskripsi: Update price.
- Sumber: open.shopee.com/documents/v2/product.update_price?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id` | int64 | ya | ID of item. Contoh: `1000` |
| `price_list` | object[] | ya | Length should be between 1 to 50. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.failure_list` | object[] | Fail model list. |
| `response.failure_list[].model_id` | int64 | ID of model. |
| `response.failure_list[].failed_reason` | string | Reason for failure. |
| `response.success_list` | object[] | Success model list. |
| `response.success_list[].model_id` | int64 | ID of model. |
| `response.success_list[].original_price` | float | Original price for model. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
