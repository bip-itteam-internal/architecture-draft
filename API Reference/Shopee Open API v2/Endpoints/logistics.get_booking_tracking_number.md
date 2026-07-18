# logistics.get_booking_tracking_number

- Path: `/api/v2/logistics/get_booking_tracking_number`
- Method: GET
- Auth: shop
- Deskripsi: After arranging shipment (v2.logistics.ship_booking) for the integrated channel, use this api to get the tracking_number, which is a required parameter for creating shipping labels. The api response can return tracking_number empty, since this info is dependent from the 3PL, due to this it is allowed to keep calling the api within 5 minutes interval, until the tracking_number is returned.
- Sumber: open.shopee.com/documents/v2/logistics.get_booking_tracking_number?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `booking_sn` | string | ya | Shopee's unique identifier for a booking. Contoh: `201201E81SYYKE` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `tracking_number` | string | The tracking number of this booking. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
