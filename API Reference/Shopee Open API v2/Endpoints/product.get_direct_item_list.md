# product.get_direct_item_list

- Path: `/api/v2/product/get_direct_item_list`
- Method: GET
- Auth: shop
- Deskripsi: get direct item by main item.
- Sumber: open.shopee.com/documents/v2/product.get_direct_item_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `main_item_id` | int64[] | ya | Item id of main shop. Contoh: `801931707` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.list` | object[] |  |
| `response.list[].main_item_id` | int64 | Item id of main shop. |
| `response.list[].direct_item_list` | object[] |  |
| `response.list[].direct_item_list[].direct_shop_id` | int64 | Id of direct shop. |
| `response.list[].direct_item_list[].direct_item_id` | int64 | Item id of direct shop. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
