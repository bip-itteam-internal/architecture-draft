# logistics.get_booking_tracking_info

- Path: `/api/v2/logistics/get_booking_tracking_info`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to get the logistics tracking information of a booking.
- Sumber: open.shopee.com/documents/v2/logistics.get_booking_tracking_info?type=1 (backend doc/api) — 2026-07-18
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
| `response` | object | Detail informations you are querying. |
| `response.booking_sn` | string | Shopee's unique identifier for a booking. |
| `response.logistics_status` | string | The Shopee logistics status for the booking. Applicable values. LOGISTICS_REQUEST_CREATED:booking arranged shipment LOGISTICS_PICKUP_DONE:booking handed over to 3PL LOGISTICS_PICKUP_FAILED:booking cancelled by 3PL due to failed pickup or picked up but not able to proceed with delivery LOGISTICS_DELIVERY_DONE:successfully delivered LOGISTICS_REQUEST_CANCELED:cancelled when booking at LOGISTICS_REQUEST_CREATED LOGISTICS_READY:booking ready for fulfilment LOGISTICS_INVALID:cancelled when booking at LOGISTICS_READY LOGISTICS_LOST:booking cancelled due to 3PL lost the parcel |
| `response.tracking_info` | object[] | The tracking info of the booking. |
| `response.tracking_info[].update_time` | timestamp | The time when logistics info has been updated. |
| `response.tracking_info[].description` | string | The description of booking logistics tracking info.logistics_status |
| `response.tracking_info[].logistics_status` | string | The Shopee logistics status for the booking. TrackingLogisticsStatus: INITIAL ORDER_INIT ORDER_SUBMITTED ORDER_CREATED PICKUP_REQUESTED PICKUP_PENDING PICKED_UP DELIVERY_PENDING DELIVERED LOST UPDATE UPDATE_SUBMITTED UPDATE_CREATED RETURN_STARTED RETURN_PENDING CANCEL CANCEL_CREATED CANCELED FAILED_ORDER_SUBMITTED FAILED_ORDER_CREATED FAILED_PICKUP_REQUESTED FAILED_PICKED_UP FAILED_DELIVERED FAILED_UPDATE_SUBMITTED FAILED_UPDATE_CREATED FAILED_RETURNED FAILED_CANCEL_CREATED FAILED_CANCELED RETURNED RETURN_INTIATED |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
