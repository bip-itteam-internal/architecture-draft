# product.add_kit_item

- Path: `/api/v2/product/add_kit_item`
- Method: POST
- Auth: shop
- Deskripsi: Create the kit item by selecting multiple items and setting main component and quantity per kit.
- Sumber: open.shopee.com/documents/v2/product.add_kit_item?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_setting` | object | ya |  |
| `sync_setting` | object | tidak |  |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string |  |
| `message` | string |  |
| `warning` | string |  |
| `request_id` | string |  |
| `response` | object |  |
| `response.item_id` | int64 |  |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
