# product.get_item_extra_info

- Path: `/api/v2/product/get_item_extra_info`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to get extra info of item by item_id list.
- Sumber: open.shopee.com/documents/v2/product.get_item_extra_info?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id_list` | int64[] | ya | item_id list, limit [0,50] Contoh: `[34001,34002]` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit error. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.item_list` | object[] | extra info of item list. |
| `response.item_list[].item_id` | int64 | Shopee's unique identifier for an item. |
| `response.item_list[].sale` | int32 | The sales volume of item. |
| `response.item_list[].views` | int32 | The page view of item. |
| `response.item_list[].likes` | int32 | The collection number of item. |
| `response.item_list[].rating_star` | float | The rating star scores of this item. |
| `response.item_list[].comment_count` | int32 | Count of comments for the item. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
