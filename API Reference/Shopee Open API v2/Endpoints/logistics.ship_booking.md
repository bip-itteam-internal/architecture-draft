# logistics.ship_booking

- Path: `/api/v2/logistics/ship_booking`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to initiate logistics including arrange pickup, dropoff. Should call v2.logistics.get_booking_shipping_parameter to fetch all required param first.
- Sumber: open.shopee.com/documents/v2/logistics.ship_booking?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `booking_sn` | string | ya | Shopee's unique identifier for a booking. Contoh: `201214JASXYXY6` |
| `pickup` | object | tidak | Required parameter ONLY if get_shipping_parameter returns "pickup" under "info_needed". Developer should still include "pickup" field in the call even if "pickup" has empty value. |
| `dropoff` | object | tidak | Required parameter ONLY if get_shipping_parameter returns "dropoff" under "info_needed". Developer should still include "dropoff" field in the call even if "dropoff" has empty value. If you choose Regular shipping method, please use "tracking_no" to call Init API. If you choose JOB shipping method, please use "sender_real_name" to call Init API. Note that only one of "tracking_no" and "sender_real_name" can be selected. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
