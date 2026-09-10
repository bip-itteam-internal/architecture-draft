# livestream.get_show_item

- Path: `/api/v2/livestream/get_show_item`
- Method: GET
- Auth: user
- Deskripsi: Get the showing item. (For TW, ID, TH, PH, MY, SG, VN)
- Sumber: open.shopee.com/documents/v2/livestream.get_show_item?type=1 (backend doc/api) — 2026-09-10
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `session_id` | int64 | ya | The identifier of livestream session. Contoh: `6236215` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.has_show_item` | boolean | Whether has the showing item. |
| `response.item` | object |  |
| `response.item.item_no` | int64 | The order of this item in the shopping bag of current session, start from 1. Only return item_no when showing item is in the shopping bag of current session. |
| `response.item.item_id` | int64 | Shopee's unique identifier for an item. |
| `response.item.shop_id` | int64 | The shop id of this item. |
| `response.item.name` | string | Name of the item in local language. |
| `response.item.image_url` | string | The image url of this item. |
| `response.item.price_info` | object |  |
| `response.item.price_info.currency` | string | The three-digit code representing the currency unit used for the item. |
| `response.item.price_info.current_price` | float | The current price of the item in the listing currency. If product under an ongoing promotion, current_price will be the promotion price. |
| `response.item.price_info.original_price` | float | The original price of the item in the listing currency. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
