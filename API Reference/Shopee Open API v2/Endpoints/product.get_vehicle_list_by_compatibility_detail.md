# product.get_vehicle_list_by_compatibility_detail

- Path: `/api/v2/product/get_vehicle_list_by_compatibility_detail`
- Method: GET
- Auth: shop
- Deskripsi: Use this Open API to get vehicle list by brand, model, year, and version.
- Sumber: open.shopee.com/documents/v2/product.get_vehicle_list_by_compatibility_detail?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `compatibility_details` | string | ya | To inform compatibility list, can be equal to Brand, Model, Year, or Version. Pass the compatibility_details="Brand" to get all brand list; Pass the compatibility_details="Model" and brand_id=1234 to get all model list under brand_id=1234; Pass the compatibility_details="Year" and brand_id=1234 and model_id=2345 to get all year list under brand_id=1234 and model_id=2345; Pass the compatibility_details="Version" and brand_id=1234 and model_id=2345 and year_id=3456 to get all version list under brand_id=1234 and model_id=2345 and year_id=3456. Contoh: `Brand` |
| `brand_id` | int64 | tidak | ID of the brand. Contoh: `1234` |
| `model_id` | int64 | tidak | ID of the model. Contoh: `2345` |
| `year_id` | int64 | tidak | ID of the year. Contoh: `3456` |
| `language` | string | tidak | If language is not uploaded, the default language=en, the following are the languages supported by different markets SG: en ; MY: en / ms-my / zh-hans ; TH: en / th ; VN: en / vi ; PH: en ; TW: en / zh-hant ; ID: en / id ; BR: en / pt-br ; MX: en / es-mx ; CO: en/es-CO ; CL: en/es-CL. Note: For markets that have already launched global tree, Crossboard shop only support returning en and zh-hans language data. Contoh: `pt-br` |

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

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
