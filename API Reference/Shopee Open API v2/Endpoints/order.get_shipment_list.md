# order.get_shipment_list

- Path: `/api/v2/order/get_shipment_list`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to get order list which order_status is READY_TO_SHIP or RETRY_SHIP to start process the whole shipping progress.
- Sumber: open.shopee.com/documents/v2/order.get_shipment_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `cursor` | string | tidak | Specifies the starting entry of data to return in the current call. Default is "". If data is more than one page, the offset can be some entry to start next call. Contoh: `""` |
| `page_size` | int32 | ya | Each result set is returned as a page of entries. Use the "page_size" filters to control the maximum number of entries to retrieve per page (i.e., per call). This integer value is used to specify the maximum number of entries to return in a single "page" of data.The limit of page_size if between 1 and 100. Contoh: `20` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.order_list` | object[] | The list of shipment orders |
| `response.order_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `response.order_list[].package_number` | string | Shopee's unique identifier for the package under an order |
| `response.more` | boolean | This is to indicate whether the order list is more than one page. If this value is true, you may want to continue to check next page to retrieve orders. |
| `response.next_cursor` | string | If more is true, you should pass the next_cursor in the next request as cursor. The value of next_cursor will be empty string when more is false. |
| `request_id` | string | The identifier for an API request for error tracking. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
