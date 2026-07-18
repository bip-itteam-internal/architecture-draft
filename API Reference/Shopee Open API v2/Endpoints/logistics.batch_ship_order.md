# logistics.batch_ship_order

- Path: `/api/v2/logistics/batch_ship_order`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to batch initiate logistics including arrange pickup, dropoff or shipment for non-integrated logistic channels. Should call v2.logistics.get_shipping_parameter to fetch all required param first. It's recommended to initiate logistics one hour after the orders were placed since there is one-hour window buyer can cancel any order without request to seller.Only channel 90003 - Padrão in Brazil has the permission of this API.
- Sumber: open.shopee.com/documents/v2/logistics.batch_ship_order?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_list` | object[] | ya | The list of order. |
| `pickup` | object | tidak | Required parameter ONLY if GetParameterForInit returns "pickup" or if GetLogisticsInfo returns "pickup" under "info_needed" for the same order. Developer should still include "pickup" field in the call even if "pickup" has empty value. |
| `dropoff` | object | tidak | Required parameter ONLY if GetParameterForInit returns "dropoff" or if GetLogisticsInfo returns "dropoff" under "info_needed" for the same order. Developer should still include "dropoff" field in the call even if "dropoff" has empty value. For logistic_id 80003 and 80004, both Regular and JOB shipping methods are supported. If you choose Regular shipping method, please use "tracking_no" to call Init API. If you choose JOB shipping method, please use "sender_real_name" to call Init API. Note that only one of "tracking_no" and "sender_real_name" can be selected. |
| `non_integrated` | object | tidak | Optional parameter when GetParameterForInit returns "non-integrated" or GetLogisticsInfo returns "non-integrated" under "info_needed". |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | object[] | Indicate warning message you should take care. |
| `warning[].order_sn` | string | Shopee's unique identifier for an order. |
| `warning[].package_number` | string | Shopee's unique identifier for the package under an order. You should't fill the field with empty string when there is't a package number. |
| `response` | object |  |
| `response.result_list` | object[] |  |
| `response.result_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `response.result_list[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `response.result_list[].fail_error` | string | Indicate error type if one element hit error. |
| `response.result_list[].fail_message` | string | Indicate error details if one element hit error. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
