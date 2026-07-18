# logistics.get_booking_shipping_parameter

- Path: `/api/v2/logistics/get_booking_shipping_parameter`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to get the parameter "info_needed" from the response to check if the booking has pickup or dropoff. This api will also return the addresses and pickup time id options for the pickup method. For dropoff, it can return branch id, sender real name etc, depending on the 3PL requirements.
- Sumber: open.shopee.com/documents/v2/logistics.get_booking_shipping_parameter?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `booking_sn` | string | ya | Shopee's unique identifier for a booking. Contoh: `201214JASXYXY6` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string |  |
| `response` | object | Detail information you are querying. |
| `response.info_needed` | object | The parameters required based on each specific booking to Init. Must use the fields included under info_needed to call Init. |
| `response.info_needed.dropoff` | string[] | Could contain 'branch_id', 'sender_real_name' or 'tracking_no'. If it contains 'branch_id', choose one to Init. If it contains 'sender_real_name' or 'tracking_no', should manually input these values in Init API. If it has empty value, developer should still include "dropoff" field in Init API. |
| `response.info_needed.pickup` | string[] | Could contain 'address_id' and 'pickup_time_id'. Choose one address_id and its corresponding pickup_time_id to Init. If it has empty value, developer should still include "pickup" field in Init API.It could contains "tracking_number" returned from "info_need"for some channels, please also add it when init. |
| `response.pickup` | object | Logistics information for pickup mode booking. |
| `response.pickup.address_list` | object[] | List of available pickup address info. |
| `response.pickup.address_list[].address_id` | int64 | The identity of address. |
| `response.pickup.address_list[].region` | string | The region of specify address. |
| `response.pickup.address_list[].state` | string | The state of specify address. |
| `response.pickup.address_list[].city` | string | The city of specify address. |
| `response.pickup.address_list[].district` | string | The district of specify address. |
| `response.pickup.address_list[].town` | string | The town of specify address. |
| `response.pickup.address_list[].address` | string | The address description of specify address. |
| `response.pickup.address_list[].zipcode` | string | The zipcode of specify address. |
| `response.pickup.address_list[].address_flag` | string[] | The flag of shop address, applicable values: default_address, pickup_address, return_address, current_address(only for multi-warehouse sellers) |
| `response.pickup.address_list[].time_slot_list` | object[] | List of pickup_time information corresponding to the address_id. Some logistics channels may not return any date or time for pickup time slots. In such cases, sellers can arrange shipment without selecting any time slot, and Shopee will arrange a suitable timing for these situations. |
| `response.pickup.address_list[].time_slot_list[].date` | timestamp | The date of pickup time. In timestamp. |
| `response.pickup.address_list[].time_slot_list[].time_text` | string | The text description of pickup time. Only applicable for certain channels. |
| `response.pickup.address_list[].time_slot_list[].pickup_time_id` | string | The identity of pickuptime. |
| `response.pickup.address_list[].time_slot_list[].flags` | string[] | This field will have the value “recommended” for the time slot that Shopee suggests sellers choose. While it is advisable for sellers to choose the recommended time slot, they can also choose other time slots that do not have the recommended flag. |
| `response.pickup.address_list[].time_slot_list[].error` | string | return if error getting pickup time, otherwise omitted |
| `response.pickup.address_list[].time_slot_list[].msg` | string | return if error getting pickup time, otherwise omitted |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
