# logistics.get_operating_hours

- Path: `/api/v2/logistics/get_operating_hours`
- Method: GET
- Auth: shop
- Deskripsi: This API is utilized to retrieve the existing operating hours of sellers including Pickup Operating Hours, Special Hours, Instant Operating Hours, and Shop Collection Operating Hours.
- Sumber: open.shopee.com/documents/v2/logistics.get_operating_hours?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

_Tidak ada parameter request selain common params._

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `repsonse` | object |  |
| `repsonse.regular_operating_hour` | object | The details of Pickup Operating Hours/Preferred Pickup Hours |
| `repsonse.regular_operating_hour.monday` | object | The Operating hours for Monday |
| `repsonse.regular_operating_hour.monday.start_time` | string | Start time for Monday |
| `repsonse.regular_operating_hour.monday.end_time` | string | End time for Monday |
| `repsonse.regular_operating_hour.tuesday` | object | The Operating hours for Tuesday |
| `repsonse.regular_operating_hour.tuesday.start_time` | string | Start time for Tuesday |
| `repsonse.regular_operating_hour.tuesday.end_time` | string | End time for Tuesday |
| `repsonse.regular_operating_hour.wednesday` | object | The Operating hours for Wednesday |
| `repsonse.regular_operating_hour.wednesday.start_time` | string | Start time for Wednesday |
| `repsonse.regular_operating_hour.wednesday.end_time` | string | End time for Wednesday |
| `repsonse.regular_operating_hour.thursday` | object | The Operating hours for Thursday |
| `repsonse.regular_operating_hour.thursday.start_time` | string | Start time for Thursday |
| `repsonse.regular_operating_hour.thursday.end_time` | string | End time for Thursday |
| `repsonse.regular_operating_hour.friday` | object | The Operating hours for Friday |
| `repsonse.regular_operating_hour.friday.start_time` | string | Start time for Friday |
| `repsonse.regular_operating_hour.friday.end_time` | string | End time for Friday |
| `repsonse.regular_operating_hour.saturday` | object | The Operating hours for Saturday |
| `repsonse.regular_operating_hour.saturday.start_time` | string | Start time for Saturday |
| `repsonse.regular_operating_hour.saturday.end_time` | string | End time for Saturday |
| `repsonse.regular_operating_hour.sunday` | object | The Operating hours for Sunday |
| `repsonse.regular_operating_hour.sunday.start_time` | string | Start time for Sunday |
| `repsonse.regular_operating_hour.sunday.end_time` | string | End time for Sunday |
| `repsonse.regular_operating_hour.public_holiday` | object | The Operating hours for Public Holiday |
| `repsonse.regular_operating_hour.public_holiday.start_time` | string | Start time for Public Holiday |
| `repsonse.regular_operating_hour.public_holiday.end_time` | string | End time for Public Holiday |
| `repsonse.instant_operating_hour` | object | The details of Instant Operating Hours |
| `repsonse.instant_operating_hour.monday` | object | The Operating hours for Monday |
| `repsonse.instant_operating_hour.monday.start_time` | string | Start time for Monday |
| `repsonse.instant_operating_hour.monday.end_time` | string | End time for Monday |
| `repsonse.instant_operating_hour.tuesday` | object | The Operating hours for Tuesday |
| `repsonse.instant_operating_hour.tuesday.start_time` | string | Start time for Tuesday |
| `repsonse.instant_operating_hour.tuesday.end_time` | string | End time for Tuesday |
| `repsonse.instant_operating_hour.wednesday` | object | The Operating hours for Wednesday |
| `repsonse.instant_operating_hour.wednesday.start_time` | string | Start time for Wednesday |
| `repsonse.instant_operating_hour.wednesday.end_time` | string | End time for Wednesday |
| `repsonse.instant_operating_hour.thursday` | object | The Operating hours for Thursday |
| `repsonse.instant_operating_hour.thursday.start_time` | string | Start time for Thursday |
| `repsonse.instant_operating_hour.thursday.end_time` | string | End time for Thursday |
| `repsonse.instant_operating_hour.friday` | object | The Operating hours for Friday |
| `repsonse.instant_operating_hour.friday.start_time` | string | Start time for Friday |
| `repsonse.instant_operating_hour.friday.end_time` | string | End time for Friday |
| `repsonse.instant_operating_hour.saturday` | object | The Operating hours for Saturday |
| `repsonse.instant_operating_hour.saturday.start_time` | string | Start time for Saturday |
| `repsonse.instant_operating_hour.saturday.end_time` | string | End time for Saturday |
| `repsonse.instant_operating_hour.sunday` | object | The Operating hours for Sunday |
| `repsonse.instant_operating_hour.sunday.start_time` | string | Start time for Sunday |
| `repsonse.instant_operating_hour.sunday.end_time` | string | End time for Sunday |
| `repsonse.instant_operating_hour.public_holiday` | object | The Operating hours for Public Holiday |
| `repsonse.instant_operating_hour.public_holiday.start_time` | string | Start time for Public Holiday |
| `repsonse.instant_operating_hour.public_holiday.end_time` | string | End time for Public Holiday |
| `repsonse.special_operating_hour` | object | The details of Special Operating Hours <path></path> |
| `repsonse.special_operating_hour.name` | string | The name of Special Operating Hours |
| `repsonse.special_operating_hour.start_date` | string | The start date of special operating hours |
| `repsonse.special_operating_hour.end_date` | string | The end date of special operating hours |
| `repsonse.special_operating_hour.operating_hours` | object[] |  |
| `repsonse.special_operating_hour.operating_hours[].date` | string | Date: it should include all date from start_date until end_date |
| `repsonse.special_operating_hour.operating_hours[].start_time` | string | Start time for that date <path></path> |
| `repsonse.special_operating_hour.operating_hours[].end_time` | string | End time for that date |
| `repsonse.special_operating_hour.operating_hours[].enable` | boolean | True: If it is open on that date. False: If it is closed on that date. |
| `repsonse.shop_collection_operating_hour` | object | The details of Shop Collection Operating Hours |
| `repsonse.shop_collection_operating_hour.monday` | object | The Operating hours for Monday |
| `repsonse.shop_collection_operating_hour.monday.start_time` | string | Start time for Monday |
| `repsonse.shop_collection_operating_hour.monday.end_time` | string | End time for Monday |
| `repsonse.shop_collection_operating_hour.tuesday` | object | The Operating hours for Tuesday |
| `repsonse.shop_collection_operating_hour.tuesday.start_time` | string | Start time for Tuesday |
| `repsonse.shop_collection_operating_hour.tuesday.end_time` | string | End time for Tuesday |
| `repsonse.shop_collection_operating_hour.wednesday` | object | The Operating hours for Wednesday |
| `repsonse.shop_collection_operating_hour.wednesday.start_time` | string | Start time for Wednesday |
| `repsonse.shop_collection_operating_hour.wednesday.end_time` | string | End time for Wednesday |
| `repsonse.shop_collection_operating_hour.thursday` | object | The Operating hours for Thursday |
| `repsonse.shop_collection_operating_hour.thursday.start_time` | string | Start time for Thursday |
| `repsonse.shop_collection_operating_hour.thursday.end_time` | string | End time for Thursday |
| `repsonse.shop_collection_operating_hour.friday` | object | The Operating hours for Friday |
| `repsonse.shop_collection_operating_hour.friday.start_time` | string | Start time for Friday |
| `repsonse.shop_collection_operating_hour.friday.end_time` | string | End time for Friday |
| `repsonse.shop_collection_operating_hour.saturday` | object | The Operating hours for Saturday |
| `repsonse.shop_collection_operating_hour.saturday.start_time` | string | Start time for Saturday |
| `repsonse.shop_collection_operating_hour.saturday.end_time` | string | End time for Saturday |
| `repsonse.shop_collection_operating_hour.sunday` | object | The Operating hours for Sunday |
| `repsonse.shop_collection_operating_hour.sunday.start_time` | string | Start time for Sunday |
| `repsonse.shop_collection_operating_hour.sunday.end_time` | string | End time for Sunday |
| `repsonse.shop_collection_operating_hour.public_holiday` | object | The Operating hours for Public Holiday |
| `repsonse.shop_collection_operating_hour.public_holiday.start_time` | string | Start time for Public Holiday |
| `repsonse.shop_collection_operating_hour.public_holiday.end_time` | string | End time for Public Holiday |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
