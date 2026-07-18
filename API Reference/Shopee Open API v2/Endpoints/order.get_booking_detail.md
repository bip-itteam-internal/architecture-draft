# order.get_booking_detail

- Path: `/api/v2/order/get_booking_detail`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to get booking detail.
- Sumber: open.shopee.com/documents/v2/order.get_booking_detail?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `booking_sn_list` | string | ya | The set of booking_sn. If there are multiple booking_sn, you need to use English comma to connect them. limit [1,50] Contoh: `201214JAJXU6G7,201214JASXYXY6` |
| `response_optional_fields` | string | tidak | The response fields you want to get. Please select from the below response parameters. If you input an object field, all the params under it will be included automatically in the response. If there are multiple response fields you want to get, you need to use English comma to connect them. Available values: item_list,cancel_by,cancel_reason,fulfillment_flag,pickup_done_time,shipping_carrier, recipient_address, dropshipper, dropshipper_phone Contoh: `total_amount` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail information you are querying. |
| `response.booking_list` | object[] | The list of bookings. |
| `response.booking_list[].booking_sn` | string | Return by default. Shopee's unique identifier for a booking. |
| `response.booking_list[].order_sn` | string | Shopee's unique identifier for an order. Only return if booking_status is MATCHED. |
| `response.booking_list[].region` | string | Return by default. The two-digit code representing the region where the booking was made. |
| `response.booking_list[].booking_status` | string | Return by default. Enumerated type that defines the current status of the booking. Available value: READY_TO_SHIP/PROCESSED/SHIPPED/CANCELLED/MATCHED |
| `response.booking_list[].match_status` | string | MATCH_PENDING/MATCH_SUCCESSFUL/MATCH_FAILED |
| `response.booking_list[].shipping_carrier` | string | The logistics service provider that will deliver the booking. |
| `response.booking_list[].create_time` | timestamp | Return by default. Timestamp that indicates the date and time that the booking was created. |
| `response.booking_list[].update_time` | timestamp | Return by default. Timestamp that indicates the last time that there was a change in value of booking, such as booking status changed from 'Processed' to 'Shipped'. |
| `response.booking_list[].ship_by_date` | int64 | Return by default. The deadline to ship out the parcel. |
| `response.booking_list[].recipient_address` | object | This object contains detailed breakdown for the recipient address. |
| `response.booking_list[].recipient_address.name` | string | Recipient's name for the address. |
| `response.booking_list[].recipient_address.phone` | string | Recipient's phone number input when booking was placed. |
| `response.booking_list[].recipient_address.town` | string | The town of the recipient's address. Whether there is a town will depend on the region and/or country. |
| `response.booking_list[].recipient_address.district` | string | The district of the recipient's address. Whether there is a district will depend on the region and/or country. |
| `response.booking_list[].recipient_address.city` | string | The city of the recipient's address. Whether there is a city will depend on the region and/or country. |
| `response.booking_list[].recipient_address.state` | string | The state/province of the recipient's address. Whether there is a state/province will depend on the region and/or country. |
| `response.booking_list[].recipient_address.region` | string | The two-digit code representing the region of the Recipient. |
| `response.booking_list[].recipient_address.zipcode` | string | Recipient's postal code. |
| `response.booking_list[].recipient_address.full_address` | string | The full address of the recipient, including country, state, even street, and etc. |
| `response.booking_list[].item_list` | object[] | This object contains the detailed breakdown for the result of this API call. |
| `response.booking_list[].item_list[].item_id` | int64 | Shopee's unique identifier for an item. |
| `response.booking_list[].item_list[].item_name` | string | The name of the item. |
| `response.booking_list[].item_list[].item_sku` | string | A item SKU (stock keeping unit) is an identifier defined by a seller, sometimes called parent SKU. Item SKU can be assigned to an item in Shopee Listings. |
| `response.booking_list[].item_list[].model_id` | int64 | ID of the model that belongs to the same item. |
| `response.booking_list[].item_list[].model_name` | string | Name of the model that belongs to the same item. A seller can offer models of the same item. For example, the seller could create a fixed-priced listing for a t-shirt design and offer the shirt in different colors and sizes. In this case, each color and size combination is a separate model. Each model can have a different quantity and price. |
| `response.booking_list[].item_list[].model_sku` | string | A model SKU (stock keeping unit) is an identifier defined by a seller. It is only intended for the seller's use. Many sellers assign a SKU to an item of a specific type, size, and color, which are models of one item in Shopee Listings. |
| `response.booking_list[].item_list[].model_quantity_purchased` | int64 | The number of identical items from one listing/item in the same booking. |
| `response.booking_list[].item_list[].weight` | float | The weight of the item |
| `response.booking_list[].item_list[].product_location_id` | string | The fulfilment warehouse ID(s) of the items in the booking. (Multi-Warehouse sellers only) |
| `response.booking_list[].item_list[].image_info` | object | Image info of the product. |
| `response.booking_list[].item_list[].image_info.image_url` | string | The image url of the product. Default to be variation image, if the model does not have a variation image, will use an item main image instead. |
| `response.booking_list[].dropshipper` | string | For Indonesia bookings only. The name of the dropshipper. |
| `response.booking_list[].dropshipper_phone` | string | The phone number of dropshipper, could be empty. |
| `response.booking_list[].cancel_by` | string | Could be one of buyer, seller, system or Ops. |
| `response.booking_list[].cancel_reason` | string | Use this field to get reason for buyer, seller, and system cancellation. |
| `response.booking_list[].fulfillment_flag` | string | Use this field to indicate the booking is fulfilled by shopee or seller. Applicable values: fulfilled_by_shopee, fulfilled_by_cb_seller, fulfilled_by_local_seller. |
| `response.booking_list[].pickup_done_time` | timestamp | The timestamp when pickup is done. |
| `warning` | string | Indicate warning message you should take care. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
