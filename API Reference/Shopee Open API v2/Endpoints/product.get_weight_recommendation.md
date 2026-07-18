# product.get_weight_recommendation

- Path: `/api/v2/product/get_weight_recommendation`
- Method: POST
- Auth: shop
- Deskripsi: Get recommended weight. Now only BR shop support to use this api to get recommended weight.
- Sumber: open.shopee.com/documents/v2/product.get_weight_recommendation?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_name` | string | ya | Name of the item in local language. Contoh: `paper` |
| `cover_image_id` | string | ya | Image id of first product image. Contoh: `e9a76cf159c3e7f12510a7017e120467` |
| `category_id` | int | ya | Shopee's unique identifier for a category. Contoh: `100061` |
| `attribute_list` | object[] | ya |  |
| `brand_id` | int | ya | Id of brand. Contoh: `100021` |
| `description_type` | string | ya | Type of description, values: See Data Definition- description_type (normal , extended). Contoh: `extended` |
| `description` | string | tidak | If description_type is normal , Description information should be set by this field. |
| `description_info` | object | tidak | New description field. Only whitelist sellers can use it. If you use the field, please upload the description_type=extended. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking |
| `response` | object |  |
| `response.normal_weight_range` | float[] | Recommended weight range, in kg. If there are no recommended results, return empty. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
