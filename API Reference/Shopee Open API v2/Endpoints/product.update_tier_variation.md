# product.update_tier_variation

- Path: `/api/v2/product/update_tier_variation`
- Method: POST
- Auth: shop
- Deskripsi: This api can only be used without changing the tier structure, you can add options, delete options, and update the option image by this api. More detail please check: https://open.shopee.com/developer-guide/219
- Sumber: open.shopee.com/documents/v2/product.update_tier_variation?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id` | int64 | ya | ID of item. Contoh: `1000` |
| `model_list` | object[] | tidak | Item's model list |
| `standardise_tier_variation` | object[] | tidak | item standardise tier variation There is at least one standardise_tier_variation and tier_variation |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
