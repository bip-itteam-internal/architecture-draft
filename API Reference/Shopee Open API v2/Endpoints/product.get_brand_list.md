# product.get_brand_list

- Path: `/api/v2/product/get_brand_list`
- Method: GET
- Auth: shop
- Deskripsi: Get the brand data of a leaf category. More detail please check: https://open.shopee.com/developer-guide/209
- Sumber: open.shopee.com/documents/v2/product.get_brand_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `offset` | int64 | ya | Specifies the starting entry of data to return in the current call. Default is 0. If data is more than one page,this field needs to be replaced with "next_offset" to request,and the offset can be some entry to start next call. Contoh: `0` |
| `page_size` | int64 | ya | the size of one page.Max=100 Contoh: `10` |
| `category_id` | int64 | ya | ID of category. Contoh: `12345` |
| `status` | int64 | ya | Brand status , 1: normal brand, 2: pending brand Contoh: `1` |
| `language` | string | tidak | If language is not uploaded, the default language=en, the following are the languages supported by different markets SG: en ; MY: en / ms-my / zh-hans ; TH: en / th ; VN: en / vi ; PH: en ; TW: en / zh-hant ; ID: en / id ; BR: en / pt-br ; MX: en / es-mx ; CO: en/es-CO ; CL: en/es-CL. Note: For markets that have already launched global tree, Crossboard shop only support returning en and zh-hans language data Contoh: `zh-hans` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking |
| `response` | object |  |
| `response.brand_list` | object[] |  |
| `response.brand_list[].original_brand_name` | string | Original name of brand |
| `response.brand_list[].brand_id` | int64 |  |
| `response.brand_list[].display_brand_name` | string | Display name of brand |
| `response.has_next_page` | boolean | This is to indicate whether the item list is more than one page. If this value is true, you may want to continue to check next page to retrieve the rest of items. |
| `response.next_offset` | int64 | If has_next_page is true, this value need set to next request.offset |
| `response.is_mandatory` | boolean | Whether is mandatory. |
| `response.input_type` | string | Input type: DROP_DOWN |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
