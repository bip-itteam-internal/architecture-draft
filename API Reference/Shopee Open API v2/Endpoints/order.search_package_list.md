# order.search_package_list

- Path: `/api/v2/order/search_package_list`
- Method: POST
- Auth: shop
- Deskripsi: Use this API to search the list of packages that have not been SHIPPED to proceed arranging shipment, and it supports various filters and sort fields.
- Sumber: open.shopee.com/documents/v2/order.search_package_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `filter` | object | tidak |  |
| `pagination` | object | ya |  |
| `sort` | object | tidak |  |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `mesage` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object |  |
| `response.packages_list` | object[] |  |
| `response.packages_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `response.packages_list[].package_number` | string | Shopee's unique identifier for the package under an order |
| `response.packages_list[].logistics_channel_id` | int32 | The identity of logistic channel. |
| `response.packages_list[].product_location_id` | string | Just use this field to pass the next step of Mass ArrangeShipment |
| `response.packages_list[].sorting_group` | string | [Only for TW 30029 channel] This field indicate the sorting group value of the package. This field is only available for logistics_channel_id = 30029 and after the package has been arranged for shipment. |
| `response.packages_list[].is_shipment_arranged` | boolean | Only effective when the package's logistics_status/fulfillment_status is LOGISTICS_READY. This parameter further distinguishes between two scenarios: - true: Package shipment has been arranged (Seller has processed shipment, system is generating tracking number, not yet updated to LOGISTICS_REQUEST_CREATED, no duplicate action needed) - false: Package awaiting shipment arrangement (Seller hasn't processed shipment yet, shipping arrangement required) |
| `response.pagination` | object |  |
| `response.pagination.total_count` | int64 | Total orders can be returned with your query |
| `response.pagination.next_cursor` | string | if packages is not empty or length of packages <= page_size. You should pass the next_cursor in the next request as page_sentinel. |
| `response.pagination.more` | boolean | To indicate, it's a the last page or not |
| `response.sort` | object | As same as request param |
| `response.sort.sort_type` | int32 | As same as request param |
| `response.sort.is_asc` | boolean | As same as request param |
| `request_id` | string | The identifier for an API request for error tracking. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
