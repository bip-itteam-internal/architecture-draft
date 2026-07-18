# order.get_booking_list

- Path: `/api/v2/order/get_booking_list`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to search bookings. You may also filter them by status, if needed.
- Sumber: open.shopee.com/documents/v2/order.get_booking_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `time_range_field` | string | ya | The kind of time_from and time_to. Available value: create_time, update_time. Contoh: `create_time` |
| `time_from` | int64 | ya | The time_from and time_to fields specify a date range for retrieving bookings (based on the time_range_field). The time_from field is the starting date range. The maximum date range that may be specified with the time_from and time_to fields is 15 days. Contoh: `1607235072` |
| `time_to` | int64 | ya | The time_from and time_to fields specify a date range for retrieving bookings (based on the time_range_field). The time_from field is the starting date range. The maximum date range that may be specified with the time_from and time_to fields is 15 days. Contoh: `1608271872` |
| `page_size` | int32 | ya | Each result set is returned as a page of entries. Use the "page_size" filters to control the maximum number of entries to retrieve per page (i.e., per call). This integer value is used to specify the maximum number of entries to return in a single "page" of data.The limit of page_size if between 1 and 100. Contoh: `20` |
| `cursor` | string | tidak | Specifies the starting entry of data to return in the current call. Default is "". If data is more than one page, the offset can be some entry to start next call. Contoh: `""` |
| `booking_status` | string | tidak | The booking_status filter for retrieving bookings and each one only every request. Available value: READY_TO_SHIP/PROCESSED/SHIPPED/CANCELLED/MATCHED Contoh: `READY_TO_SHIP` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail information you are querying. |
| `response.more` | boolean | This is to indicate whether the booking list is more than one page. If this value is true, you may want to continue to check next page to retrieve bookings. |
| `response.booking_list` | object[] |  |
| `response.booking_list[].booking_sn` | string | Shopee's unique identifier for a booking. |
| `response.booking_list[].order_sn` | string | Shopee's unique identifier for an order. Only return if booking_status is MATCHED. |
| `response.booking_list[].booking_status` | string | The booking_status filter for retrieving booking and each one only every request. Available value: READY_TO_SHIP/PROCESSED/SHIPPED/CANCELLED/MATCHED |
| `response.booking_list[].next_cursor` | string | If more is true, you should pass the next_cursor in the next request as cursor. The value of next_cursor will be empty string when more is false. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
