# order.get_order_list

- Path: `/api/v2/order/get_order_list`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to search orders. You may also filter them by status, if needed.
- Sumber: open.shopee.com/documents/v2/order.get_order_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `time_range_field` | string | ya | The kind of time_from and time_to. Available value: create_time, update_time. Contoh: `create_time` |
| `time_from` | timestamp | ya | The time_from and time_to fields specify a date range for retrieving orders (based on the time_range_field). The time_from field is the starting date range. The maximum date range that may be specified with the time_from and time_to fields is 15 days. Contoh: `1607235072` |
| `time_to` | timestamp | ya | The time_from and time_to fields specify a date range for retrieving orders (based on the time_range_field). The time_from field is the starting date range. The maximum date range that may be specified with the time_from and time_to fields is 15 days. Contoh: `1608271872` |
| `page_size` | int32 | ya | Each result set is returned as a page of entries. Use the "page_size" filters to control the maximum number of entries to retrieve per page (i.e., per call). This integer value is used to specify the maximum number of entries to return in a single "page" of data.The limit of page_size if between 1 and 100. Contoh: `20` |
| `cursor` | string | tidak | Specifies the starting entry of data to return in the current call. The default is empty. If the data is more than one page, the offset can be some entry to start the next call. |
| `order_status` | string | tidak | The order_status filter for retriveing orders and each one only every request. Available value: UNPAID/READY_TO_SHIP/PROCESSED/SHIPPED/COMPLETED/IN_CANCEL/CANCELLED/INVOICE_PENDING Contoh: `READY_TO_SHIP` |
| `response_optional_fields` | string | tidak | Optional fields in response. Available value: order_status. Contoh: `order_status` |
| `request_order_status_pending` | boolean | tidak | Compatible parameter during migration period, send True will let API support PENDING status, send False or don’t send will fallback to old logic. Contoh: `true` |
| `logistics_channel_id` | int32 | tidak | The identity of logistic channel. Valid only for BR. Contoh: `91007` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.more` | boolean | This is to indicate whether the order list is more than one page. If this value is true, you may want to continue to check next page to retrieve orders. |
| `response.order_list` | object[] |  |
| `response.order_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `response.order_list[].order_status` | string | The order_status filter for retriveing orders and each one only every request. Available value: UNPAID/READY_TO_SHIP/PROCESSED/SHIPPED/COMPLETED/IN_CANCEL/CANCELLED |
| `response.order_list[].booking_sn` | string | Return by default. Shopee's unique identifier for a booking. Only returned for advance fulfilment matched order only. |
| `response.next_cursor` | string | If more is true, you should pass the next_cursor in the next request as cursor. The value of next_cursor will be empty string when more is false. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
