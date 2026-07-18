# logistics.get_mass_shipping_parameter

- Path: `/api/v2/logistics/get_mass_shipping_parameter`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to check if package support pickup, dropoff, non-integrated. For pickup, return address and pickup time id options. For dropoff, return branch id, sender real name, etc. Can batch request for packages under same product_location_id and logistics_channel_id. [Please call it when packages meet: 1) fulfillment status is LOGISTICS_READY; or 2) fulfillment status is LOGISTICS_PICKUP_RETRY; or 3) fulfillment status is LOGISTICS_REQUEST_CREATED and meet Instant Order Reschedule conditions]
- Sumber: open.shopee.com/documents/v2/logistics.get_mass_shipping_parameter?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `logistics_channel_id` | int64 | tidak | The API can only batch request the shipping parameter for multiple packages under the same product_location_id and same logistics_channel_id. Use this field to specify the logistics_channel_id for the request. If not specified, will use the logistics_channel_id corresponds to the first package_number by default. Contoh: `50021` |
| `product_location_id` | string | tidak | The API can only batch request the shipping parameter for multiple packages under the same product_location_id and same logistics_channel_id. Use this field to specify the product_location_id for the request. If not specified, will use the product_location_id corresponds to the first package_number by default. Contoh: `"VN0002BIZ"` |
| `package_list` | object[] | ya | The list of packages you want to get shipping parameters. limit [1, 50]. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened.<path></path><path></path> |
| `response` | object |  |
| `response.info_needed` | object | The parameters required based on each specific order to Init. Must use the fields included under info_needed to call Init. For logistic_id 80003 and 80004, both Regular and JOB shipping methods are supported. If you choose Regular shipping method, please use "tracking_no" to call Init API. If you choose JOB shipping method, please use "sender_real_name" to call Init API. Note that only one of "tracking_no" and "sender_real_name" can be selected. |
| `response.info_needed.dropoff` | string[] | Could contain 'branch_id', 'sender_real_name', or 'tracking_no'. If it contains 'branch_id', choose one to Init. If it contains 'sender_real_name' or 'tracking_no', should manually input these values in Init API. If it has empty value, developer should still include "dropoff" field in Init API. |
| `response.info_needed.pickup` | string[] | Could contain 'address_id' and 'pickup_time_id'. Choose one address_id and its corresponding pickup_time_id to Init. If it has empty value, developer should still include "pickup" field in Init API. It could contains "tracking_number" returned from "info_need"for some channels, please also add it when init. |
| `response.info_needed.non_integrated` | string[] | Could contain 'tracking_no'. If it contains 'tracking_no', should manually input these values in Init API. If it has empty value, developer should still include "non-integrated" field in Init API. |
| `response.dropoff` | object | Logistics information for dropoff mode package. |
| `response.dropoff.branch_list` | object[] | List of available dropoff branches info. |
| `response.dropoff.branch_list[].branch_id` | int64 | The identity of logistics branch. |
| `response.dropoff.branch_list[].region` | string | The region of specify address. |
| `response.dropoff.branch_list[].state` | string | The state of specify address. |
| `response.dropoff.branch_list[].city` | string | The city of specify address. |
| `response.dropoff.branch_list[].address` | string | The address description of specify address. |
| `response.dropoff.branch_list[].zipcode` | string | The zipcode of specify address. |
| `response.dropoff.branch_list[].district` | string | The district of specify address. |
| `response.dropoff.branch_list[].town` | string | The town of specify address. |
| `response.pickup` | object | Logistics information for pickup mode package. |
| `response.pickup.address_list` | object[] | List of available pickup address info. For Multi-Warehouse sellers, note that changing pickup address from Current may incur higher shipping fees. |
| `response.pickup.address_list[].address_id` | int64 | The identity of address. |
| `response.pickup.address_list[].region` | string | The region of specify address. |
| `response.pickup.address_list[].state` | string | The state of specify address. |
| `response.pickup.address_list[].city` | string | The city of specify address. |
| `response.pickup.address_list[].district` | string | The district of specify address. |
| `response.pickup.address_list[].town` | string | The town of specify address. |
| `response.pickup.address_list[].address` | string | The address description of specify address. |
| `response.pickup.address_list[].zipcode` | string | The zipcode of specify address. |
| `response.pickup.address_list[].address_flag` | string[] | The flag of shop address, applicable values: default_address, pickup_address, return_address, current_address (Multi-Warehouse sellers only) |
| `response.pickup.address_list[].time_slot_list` | object[] | List of pickup_time information corresponding to the address_id. Some logistics channels may not return any date or time for pickup time slots. In such cases, sellers can arrange shipment without selecting any time slot, and Shopee will arrange a suitable timing for these situations. |
| `response.pickup.address_list[].time_slot_list[].date` | timestamp | The date of pickup time. In timestamp. |
| `response.pickup.address_list[].time_slot_list[].time_text` | string | The text description of pickup time. Only applicable for certain channels. |
| `response.pickup.address_list[].time_slot_list[].pickup_time_id` | string | The identity of pickuptime. |
| `response.pickup.address_list[].time_slot_list[].flags` | string[] | This field will have the value “recommended” for the time slot that Shopee suggests sellers choose. While it is advisable for sellers to choose the recommended time slot, they can also choose other time slots that do not have the recommended flag. |
| `response.success_list` | object[] | Success package list. |
| `response.success_list[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `response.fail_list` | object[] | Fail package list. |
| `response.fail_list[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `response.fail_list[].fail_reason` | string | Reason for failure. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
