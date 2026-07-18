# product.update_kit_item

- Path: `/api/v2/product/update_kit_item`
- Method: POST
- Auth: shop
- Deskripsi: Update the kit basic information and kit components, only support adding kit variations and updating existing kit variation’s image, price, and model_sku, don’t support deleting existing kit variations and updating the items, main component and quantity per kit of existing kit variations.
- Sumber: open.shopee.com/documents/v2/product.update_kit_item?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id` | int64 | ya | ID of kit item. Contoh: `28001430` |
| `item_setting` | object | tidak |  |
| `sync_setting` | object | tidak |  |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string |  |
| `message` | string |  |
| `warning` | string |  |
| `request_id` | string |  |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
