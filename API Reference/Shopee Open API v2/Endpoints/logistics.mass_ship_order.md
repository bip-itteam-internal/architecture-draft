# logistics.mass_ship_order

- Path: `/api/v2/logistics/mass_ship_order`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to initiate logistics including arrange pickup, dropoff or shipment for non-integrated logistic channels. Should call v2.logistics.get_mass_shipping_parameter to fetch all required params first. It's recommended to initiate logistics one hour after the orders were placed since there is one-hour window buyer can cancel any order without request to seller. The API can only batch arrange shipment for multiple packages under the same product_location_id and same logistics_channel_id.
- Sumber: open.shopee.com/documents/v2/logistics.mass_ship_order?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `logistics_channel_id` | int64 | tidak | The API can only batch arrange shipment for multiple packages under the same product_location_id and same logistics_channel_id. Use this field to specify the logistics_channel_id for the request. If not specified, will use the logistics_channel_id corresponds to the first package_number by default. Contoh: `50021` |
| `product_location_id` | string | tidak | The API can only batch arrange shipment for multiple packages under the same product_location_id and same logistics_channel_id. Use this field to specify the product_location_id for the request. If not specified, will use the product_location_id corresponds to the first package_number by default. |
| `package_list` | object[] | ya | The list of packages you want to arrange shipment. limit [1, 50]. |
| `pickup` | object | tidak | Required parameter ONLY if GetParameterForInit returns "pickup" or if GetLogisticsInfo returns "pickup" under "info_needed" for the same order. Developer should still include "pickup" field in the call even if "pickup" has empty value. |
| `dropoff` | object | tidak | Required parameter ONLY if GetParameterForInit returns "dropoff" or if GetLogisticsInfo returns "dropoff" under "info_needed" for the same order. Developer should still include "dropoff" field in the call even if "dropoff" has empty value. For logistic_id 80003 and 80004, both Regular and JOB shipping methods are supported. If you choose Regular shipping method, please use "tracking_no" to call Init API. If you choose JOB shipping method, please use "sender_real_name" to call Init API. Note that only one of "tracking_no" and "sender_real_name" can be selected. |
| `non_integrated` | object | tidak | Optional parameter when get_mass_shipping_parameter returns "non-integrated" under "info_needed". |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `success_list` | object[] | Success package list. |
| `success_list[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `fail_list` | object[] | Fail package list. |
| `fail_list[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `fail_list[].fail_reason` | string | Reason for failure. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
