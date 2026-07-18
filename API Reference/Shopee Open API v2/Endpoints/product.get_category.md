# product.get_category

- Path: `/api/v2/product/get_category`
- Method: GET
- Auth: shop
- Deskripsi: Get category tree data. More detail please check https://open.shopee.com/developer-guide/209
- Sumber: open.shopee.com/documents/v2/product.get_category?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `language` | string | tidak | If language is not uploaded, the default language=en, the following are the languages supported by different markets SG: en ; MY: en / ms-my / zh-hans ; TH: en / th ; VN: en / vi ; PH: en ; TW: en / zh-hant ; ID: en / id ; BR: en / pt-br ; MX: en / es-mx ; CO: en/es-CO ; CL: en/es-CL .Note: For markets that have already launched global tree, Crossboard shop only support returning en and zh-hans language data Contoh: `zh-hans` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.category_list` | object[] |  |
| `response.category_list[].category_id` | int64 | ID for category. |
| `response.category_list[].parent_category_id` | int64 | ID for parent category. |
| `response.category_list[].original_category_name` | string | Default name for category. |
| `response.category_list[].display_category_name` | string | Display name dependent on display name. |
| `response.category_list[].has_children` | boolean | Whether this category has active children category. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
