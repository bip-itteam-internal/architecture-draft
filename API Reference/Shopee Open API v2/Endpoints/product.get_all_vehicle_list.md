# product.get_all_vehicle_list

- Path: `/api/v2/product/get_all_vehicle_list`
- Method: GET
- Auth: shop
- Deskripsi: Use this Open API to get all vehicle list.
- Sumber: open.shopee.com/documents/v2/product.get_all_vehicle_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `page_size` | int64 | ya | The size of one page. Max=100 Contoh: `10` |
| `offset` | int64 | tidak | Specifies the starting entry of data to return in the current call. Default is 0, if data is more than one page, the offset can be some entry to start next call. Contoh: `0` |
| `language` | string | tidak | If language is not uploaded, the default language=en, the following are the languages supported by different markets SG: en ; MY: en / ms-my / zh-hans ; TH: en / th ; VN: en / vi ; PH: en ; TW: en / zh-hant ; ID: en / id ; BR: en / pt-br ; MX: en / es-mx ; CO: en/es-CO ; CL: en/es-CL. Note: For markets that have already launched global tree, Crossboard shop only support returning en and zh-hans language data Contoh: `pt-br` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking |
| `response` | object |  |
| `response.vehicle_list` | object[] |  |
| `response.vehicle_list[].brand_id` | int64 | ID of the brand. |
| `response.vehicle_list[].brand_name` | string | Name of the brand. |
| `response.vehicle_list[].model_id` | int64 | ID of the model. |
| `response.vehicle_list[].model_name` | string | Name of the model. |
| `response.vehicle_list[].year_id` | int64 | ID of the year. |
| `response.vehicle_list[].year_name` | string | Name of the year. |
| `response.vehicle_list[].version_id` | int64 | ID of the version. |
| `response.vehicle_list[].version_name` | string | Name of the version. |
| `response.has_next_page` | boolean | This is to indicate whether the item list is more than one page. If this value is true, you may want to continue to check next page to retrieve the rest of items. |
| `response.next_offset` | int64 | If has_next_page is true, this value need set to next request offset |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
