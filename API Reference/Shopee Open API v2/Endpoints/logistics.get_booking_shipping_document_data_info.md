# logistics.get_booking_shipping_document_data_info

- Path: `/api/v2/logistics/get_booking_shipping_document_data_info`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to fetch the logistics information of a booking these info can be used for airwaybill printing. Dedicated for crossborder SLS order airwaybill. May not be applicable for local channel airwaybill. Besides, this api supports returning personal info as images.
- Sumber: open.shopee.com/documents/v2/logistics.get_booking_shipping_document_data_info?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `booking_sn` | string | ya | Shopee's unique identifier for a booking. Contoh: `201201E81SYYKE` |
| `recipient_address_info` | object[] | tidak | recipient address to query as image |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.recipient_address_info` | object |  |
| `response.recipient_address_info.key` | string | queried field in recipient address |
| `response.recipient_address_info.image` | string | base64 encoded png data string |
| `response.shipping_document_info` | object |  |
| `response.shipping_document_info.booking_weight` | int64 | Use this field to indicate booking weight when calculate the shipping fee. The unit of weigh is gram. |
| `response.shipping_document_info.logistics_channel_id` | int64 | The identity of logistic channel. |
| `response.shipping_document_info.shipping_carrier` | string | The logistics service provider for the booking. |
| `response.shipping_document_info.recipient_sort_code` | object | The sort_code of recipient. |
| `response.shipping_document_info.recipient_sort_code.first_recipient_sort_code` | string | The first-level sort_code of recipient. |
| `response.shipping_document_info.recipient_sort_code.second_recipient_sort_code` | string | The second-level sort_code of recipient. |
| `response.shipping_document_info.recipient_sort_code.third_recipient_sort_code` | string | The third-level sort_code of recipient. |
| `response.shipping_document_info.sender_sort_code` | object | The sort_code of sender. |
| `response.shipping_document_info.sender_sort_code.first_sender_sort_code` | string | The first-level sort_code of sender. |
| `response.shipping_document_info.sender_sort_code.second_sender_sort_code` | string | The second-level sort_code of sender. |
| `response.shipping_document_info.sender_sort_code.third_sender_sort_code` | string | The third-level sort_code of sender. |
| `response.shipping_document_info.return_sort_code` | object | The sort code for 3PL doing RTS. |
| `response.shipping_document_info.return_sort_code.return_first_sort_code` | string | The first-level sort code for 3PL doing RTS. |
| `response.shipping_document_info.tracking_number` | string | The tracking number assigned by the shipping carrier for item shipment. |
| `response.shipping_document_info.pickup_hub` | string | The name of pickup hub. |
| `response.shipping_document_info.delivery_hub` | string | The name of delivery hub. |
| `response.shipping_document_info.deliver_area` | string | Zone name. |
| `response.shipping_document_info.ec_booking_no` | string | The name of ec booing. |
| `response.shipping_document_info.create_date_ymd_sl` | string | The date of create shipment booking. |
| `response.shipping_document_info.manufacturers_name` | string | The name of manufacturer. |
| `response.shipping_document_info.manufacturers_website` | string | The website of manufacturer. |
| `response.shipping_document_info.is_lm_dg_bool` | int64 | Use this field to indicate order contains dangerous goods or not. 0: Non-dangerous good 1: Dangerous good 2: Prohibited |
| `response.shipping_document_info.spx_sub_district` | string | The sub-district of recipient's address. |
| `response.shipping_document_info.spx_receive_station` | object | The spx receive station. |
| `response.shipping_document_info.spx_receive_station.spx_first_receive_station` | string | The first pickup station. |
| `response.shipping_document_info.zone` | string | The zone of this booking. |
| `response.shipping_document_info.zone_code` | string | Delivery Sub Zone. |
| `response.shipping_document_info.destination_base_code` | string | Distribution Center Code. |
| `response.shipping_document_info.dg_specific_type` | int32 | Currently only applicable for Brazil, Indonesia, Vietnam, Philippines. For orders with Dangerous Goods, this value indicates the severity of the danger and requires special handling by the logistics provider. 0 = Not classified / no DG sub-type 1 = DG_A 2 = DG_B 3 = DG_C 4 = DG_D |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
