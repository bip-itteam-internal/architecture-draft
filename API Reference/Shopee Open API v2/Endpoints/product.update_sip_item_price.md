# product.update_sip_item_price

- Path: `/api/v2/product/update_sip_item_price`
- Method: POST
- Auth: shop
- Deskripsi: Update sip item price.
- Sumber: open.shopee.com/documents/v2/product.update_sip_item_price?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id` | int | ya | ID of item. Contoh: `1000` |
| `sip_item_price` | object[] | tidak |  |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
