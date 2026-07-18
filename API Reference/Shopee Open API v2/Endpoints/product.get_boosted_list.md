# product.get_boosted_list

- Path: `/api/v2/product/get_boosted_list`
- Method: GET
- Auth: shop
- Deskripsi: Get boosted item list.
- Sumber: open.shopee.com/documents/v2/product.get_boosted_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

_Tidak ada parameter request selain common params._

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.item_list` | object[] |  |
| `response.item_list[].item_id` | int | Shopee's unique identifier for an item |
| `response.item_list[].cool_down_second` | int | Remain cool down time |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
