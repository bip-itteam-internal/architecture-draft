# logistics.update_operating_hours

- Path: `/api/v2/logistics/update_operating_hours`
- Method: POST
- Auth: shop
- Deskripsi: This API is designed to allow sellers to update their operating hours. It is essential that the values provided in this API align with the restrictions retrieved from the v2.logistics.get_operating_hour_restrictions API to ensure compliance with platform requirements. This API uses overwriting updates, when updating pickup operating hours, still need to include all parts even those not needing changes.
- Sumber: open.shopee.com/documents/v2/logistics.update_operating_hours?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `regular_operating_hour` | object | tidak | Details of Pickup Operating Hours / Preferred Pickup Hours: You can skip this parameter if you are not updating the Pickup Operating Hours / Preferred Pickup Hours |
| `special_operating_hour` | object | tidak | Details of Special Operating Hours : You can skip this parameter if you are not creating Special Operating Hours or if you do not have access to create Special Operating Hours |
| `instant_operating_hour` | object | tidak | Details of Instant Operating Hours : You can skip this parameter if you are not creating/updating Instant Operating Hours or if you do not have access to create/update Instant Operating Hours |
| `shop_collection_operating_hour` | object | tidak | Details of Shop Collection Operating Hours : You can skip this parameter if you are not creating/updating Shop Collection Operating Hours or if you do not have access to create/update Shop Collection Operating Hours |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.result_list` | object |  |
| `response.result_list.regular_operating_hour` | object | The result of create/update regular_operating_hour. |
| `response.result_list.regular_operating_hour.status` | string | The system will return "Failed" if there are any validation errors. Otherwise, it will return a blank response. |
| `response.result_list.regular_operating_hour.fail_message` | string | Fail reason |
| `response.result_list.special_operating_hour` | object | The result of create/update speicial_operating_hour. |
| `response.result_list.special_operating_hour.status` | string | The system will return "Failed" if there are any validation errors. Otherwise, it will return a blank response. |
| `response.result_list.special_operating_hour.fail_message` | string | Fail reason |
| `response.result_list.instant_operating_hour` | object | The result of create/update instant_operating_hour. |
| `response.result_list.instant_operating_hour.status` | string | The system will return "Failed" if there are any validation errors. Otherwise, it will return a blank response. |
| `response.result_list.instant_operating_hour.fail_message` | string | Fail reason |
| `response.result_list.shop_collection_operating_hour` | object | The result of create/update shop_collection_operating_hour. |
| `response.result_list.shop_collection_operating_hour.status` | string | The system will return "Failed" if there are any validation errors. Otherwise, it will return a blank response. |
| `response.result_list.shop_collection_operating_hour.fail_message` | string | Fail reason |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
