# logistics.get_booking_shipping_document_result

- Path: `/api/v2/logistics/get_booking_shipping_document_result`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to retrieve the status of the shipping document task. Document will be available for download only after the status change to 'READY'.
- Sumber: open.shopee.com/documents/v2/logistics.get_booking_shipping_document_result?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `booking_list` | object[] | ya | The list of bookings you want to get. limit [1,50] |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | object[] | Indicate warning message you should take care. |
| `warning[].booking_sn` | string | Shopee's unique identifier for a booking. |
| `response` | object | Detail informations you are querying. |
| `response.result_list` | object[] | The list of the result data. |
| `response.result_list[].booking_sn` | string | Shopee's unique identifier for a booking. |
| `response.result_list[].status` | string | The status of the shipping document task you querying with booking_sn. Available values: READY/FAILED/PROCESSING |
| `response.result_list[].fail_error` | string | Indicate error type if one element hit error. |
| `response.result_list[].fail_message` | string | Indicate error details if one element hit error. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
