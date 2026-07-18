# logistics.get_shipping_document_data_info

- Path: `/api/v2/logistics/get_shipping_document_data_info`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to fetch the logistics information of an order, these info can be used for self-design AWB printing. Besides, this api supports returning personal info as images.
- Sumber: open.shopee.com/documents/v2/logistics.get_shipping_document_data_info?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn` | string | ya | Shopee's unique identifier for an order. Contoh: `201224EM1FMFG1` |
| `package_number` | string | tidak | Shopee's unique identifier for the package under an order. You shouldn't fill the field with empty string when there isn't a package number. Contoh: `9087129345` |
| `recipient_address_info` | object[] | tidak | recipient address to query as image |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. Note: For parcels that support pre-shipment printing, calling this API before shipment will only return the following fields: response recipient_address_info key image shipping_document_info cod cod_amount order_weight logistics_channel_id shipping_carrier pickup_code |
| `response.recipient_address_info` | object |  |
| `response.recipient_address_info.key` | string | queried field in recipient address |
| `response.recipient_address_info.image` | string | base64 encoded png data string |
| `response.shipping_document_info` | object |  |
| `response.shipping_document_info.cod` | boolean | This value indicates whether the order was a COD (cash on delivery) order. |
| `response.shipping_document_info.cod_amount` | string | Use this field to indicate cod amount. |
| `response.shipping_document_info.order_weight` | int32 | Use this field to indicate order weight when calculate the shipping fee. The unit of weigh is gram. |
| `response.shipping_document_info.logistics_channel_id` | int32 | The identity of logistic channel. |
| `response.shipping_document_info.shipping_carrier` | string | The logistics service provider that the buyer selected for the order to deliver items. |
| `response.shipping_document_info.service_code` | string | Only work for cross-border order. This code is required at some sorting hub. Please ensure the service_code is INCLUDED on your shipping label, otherwise the parcel cannot be processed by the warehouse. If you didn't retrieve service_code after you first called this API, please try few more times within 30 minutes. |
| `response.shipping_document_info.first_mile_name` | string | Only work for cross-border order.The name of the carrier ships cross country or region. |
| `response.shipping_document_info.last_mile_name` | string | Only work for cross-border order.The name of the carrier delivers the parcels in local country or region. |
| `response.shipping_document_info.goods_to_declare` | boolean | Only work for cross-border order.This value indicates whether the order contains goods that are required to declare at customs. "T" means true and it will mark as "T" on the shipping label; "F" means false and it will mark as "P" on the shipping label. This value is accurate ONLY AFTER the order trackingNo is generated, please capture this value AFTER your retrieve the trackingNo. |
| `response.shipping_document_info.lane_code` | string | Only work for cross-border order. The string use for waybill printing. The format is "S - region_code and lane_number". For example, S-TH01, S-TH02 |
| `response.shipping_document_info.warehouse_address` | string | Only work for cross-border order in some special shop. The address info of the warehouse. |
| `response.shipping_document_info.warehouse_id` | string | Only work for cross-border order in some special shop. The ID of the warehouse. |
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
| `response.shipping_document_info.third_party_logistic_info` | object | Only used for TW sellers. |
| `response.shipping_document_info.third_party_logistic_info.service_description` | string | Use this field to indicate the order category. |
| `response.shipping_document_info.third_party_logistic_info.barcode` | string | The manufacturer barcode. |
| `response.shipping_document_info.third_party_logistic_info.purchase_time` | string | The purchase_time of the store. |
| `response.shipping_document_info.third_party_logistic_info.return_time` | string | The return_time of the store. |
| `response.shipping_document_info.third_party_logistic_info.manufacturers_name` | string | The name of manufacturers. |
| `response.shipping_document_info.third_party_logistic_info.manufacturers_website` | string | The website of manufacturers. |
| `response.shipping_document_info.third_party_logistic_info.recipient_area` | string | The identification of recipient area. |
| `response.shipping_document_info.third_party_logistic_info.route_step` | string | The route code of the waybill. |
| `response.shipping_document_info.third_party_logistic_info.suda5_code` | string | The tally code of the waybill. |
| `response.shipping_document_info.third_party_logistic_info.large_logistics_id` | string | The code of large logistics. |
| `response.shipping_document_info.third_party_logistic_info.parent_id` | string | The parent code of the waybill. |
| `response.shipping_document_info.third_party_logistic_info.return_cycle` | string | Use this field to indicate the return cycle. |
| `response.shipping_document_info.third_party_logistic_info.return_mode` | string | Use this field to indicate the return mode. |
| `response.shipping_document_info.third_party_logistic_info.prompt` | string | The reminder of stork work. |
| `response.shipping_document_info.third_party_logistic_info.order_sn` | string | Shopee's unique identifier for an order. |
| `response.shipping_document_info.third_party_logistic_info.qrcode` | string | The QR code of the waybill. |
| `response.shipping_document_info.third_party_logistic_info.ec_supplier_name` | string | The supplier name of channel. |
| `response.shipping_document_info.third_party_logistic_info.ec_bar_code16` | string | Use this field to indicate the first barcode. |
| `response.shipping_document_info.third_party_logistic_info.equipment_id` | string | The device code. |
| `response.shipping_document_info.third_party_logistic_info.eshop_id` | string | The child code for B2C Family-mart. |
| `response.shipping_document_info.third_party_logistic_info.ec_bar_code9` | string | Use this field to indicate the pick barcode. |
| `response.shipping_document_info.third_party_logistic_info.pelican_tracking_no` | string | The tracking number of Shopee Delivery. |
| `response.shipping_document_info.third_party_logistic_info.print_date` | string | The date of printing the wayBill. |
| `response.shipping_document_info.third_party_logistic_info.pzip` | string | The sort code of the order. |
| `response.shipping_document_info.third_party_logistic_info.pzip_c` | string | The barcode of the sort code. |
| `response.shipping_document_info.third_party_logistic_info.deliver_area_txt` | string | The code of the delivery area. |
| `response.shipping_document_info.third_party_logistic_info.deliver_date_ymd` | string | Expected delivery date of the order. |
| `response.shipping_document_info.third_party_logistic_info.sd_driver_code` | string | Lorry driver code of the order. |
| `response.shipping_document_info.third_party_logistic_info.md_driver_code` | string | Motorcycle driver code of the order. |
| `response.shipping_document_info.third_party_logistic_info.putorder_stackzone_code` | string | Stacking area of the order. |
| `response.shipping_document_info.third_party_logistic_info.customer_code` | string | The customer code of Shopee. |
| `response.shipping_document_info.third_party_logistic_info.deliver_router` | string | Use this field to indicate the delivery router. |
| `response.shipping_document_info.third_party_logistic_info.store_type` | string | Use this field to indicate the store type. |
| `response.shipping_document_info.third_party_logistic_info.pick_router` | string | Use this field to indicate the pick router. |
| `response.shipping_document_info.third_party_logistic_info.barcode_dc` | string | The main logistic barcode of the waybill. |
| `response.shipping_document_info.third_party_logistic_info.ec_order_number` | string | Use this field to indicate the logistics order number. |
| `response.shipping_document_info.third_party_logistic_info.barcode_pr` | string | The sorting barcode of the waybill. |
| `response.shipping_document_info.third_party_logistic_info.first_pick_barcode` | string | The first pick barcode of the waybill. |
| `response.shipping_document_info.third_party_logistic_info.second_pick_barcode` | string | The second pick barcode of the waybill. |
| `response.shipping_document_info.third_party_logistic_info.is_cod_bool` | string | Use this field to indicate the service type. |
| `response.shipping_document_info.third_party_logistic_info.receiver_name` | string | Use this field to indicate the receiver name. |
| `response.shipping_document_info.third_party_logistic_info.rcv_store_name` | string | Use this field to indicate the receiver store name. |
| `response.shipping_document_info.third_party_logistic_info.branch_code` | string | Use this field indicates destination service point code. |
| `response.shipping_document_info.third_party_logistic_info.branch_name` | string | Use this field indicates destination service point name. |
| `response.shipping_document_info.third_party_logistic_info.last_third_digits_recipient_phone` | string | Use this field indicates buyer phone number (last 3 digits). |
| `response.shipping_document_info.third_party_logistic_info.last_third_digits_sender_phone` | string | Use this field indicates seller phone number (last 3 digits). |
| `response.shipping_document_info.third_party_logistic_info.barcode_no1` | string | First barcode no. sacnned when seller drop off |
| `response.shipping_document_info.third_party_logistic_info.barcode_no2` | string | Second barcode no. sacnned when seller drop off |
| `response.shipping_document_info.third_party_logistic_info.print_datetime` | string | AWB Print date and time |
| `response.shipping_document_info.third_party_logistic_info.ok_mid_type` | string | Middle type used in OK Mart SOC |
| `response.shipping_document_info.third_party_logistic_info.ok_aisle_no` | string | Aisle no. used in OK Mart SOC |
| `response.shipping_document_info.third_party_logistic_info.ok_grid_no` | string | Grid no used in OK Mart SOC |
| `response.shipping_document_info.third_party_logistic_info.ok_tracking_number` | string | The tracking number of OK Mart. |
| `response.shipping_document_info.third_party_logistic_info.barcode_no3` | string | OK SOC received no. |
| `response.shipping_document_info.third_party_logistic_info.ship_type` | string | Ship type used by OK Mart |
| `response.shipping_document_info.third_party_logistic_info.area` | string | The area of the collect OK branch used for OK sorting |
| `response.shipping_document_info.third_party_logistic_info.barcode_no4` | string | First barcode no. sacnned when buyer collect |
| `response.shipping_document_info.third_party_logistic_info.barcode_no5` | string | Second barcode no. sacnned when buyer collect |
| `response.shipping_document_info.third_party_logistic_info.tw_last_three_digits_buyer_phone` | string | [Only for local TW orders] Last 3 digits of buyer's phone number, apply for channel_id: 30005, 30006, 30007,30014,30015 |
| `response.shipping_document_info.third_party_logistic_info.tw_store_name` | string | [Only for TW channel_id:30005 ] Store name for 7-ELEVEN orders. |
| `response.shipping_document_info.third_party_logistic_info.tw_store_number` | string | [Only for TW channel_id:30005 ]Store number for 7-ELEVEN orders. |
| `response.shipping_document_info.third_party_logistic_info.buyer_prefer_delivery_time` | object | [Only for TW channel:30017] The time buyer prefers to receive the packages. |
| `response.shipping_document_info.third_party_logistic_info.buyer_prefer_delivery_time.slot_id` | string | The slot which buyer choose |
| `response.shipping_document_info.third_party_logistic_info.buyer_prefer_delivery_time.start_time` | string | The start time of a day buyer prefer to receive the packages |
| `response.shipping_document_info.third_party_logistic_info.buyer_prefer_delivery_time.end_time` | string | The end time of a day buyer prefer to receive the packages. |
| `response.shipping_document_info.third_party_logistic_info.buyer_prefer_delivery_time.description` | string | The detailed instructions of the package delivering. |
| `response.shipping_document_info.tracking_number` | string | The tracking number assigned by the shipping carrier for item shipment. |
| `response.shipping_document_info.shopee_tracking_number` | string | First mile tracking NO. for CrossBoard BR seller can be used to self-design CB Brazil AWB. |
| `response.shipping_document_info.last_mile_tracking_number` | string | The last-mile tracking number. Only for Cross Board BR seller. |
| `response.shipping_document_info.pickup_hub` | string | The name of pickup hub. |
| `response.shipping_document_info.delivery_hub` | string | The name of delivery hub. |
| `response.shipping_document_info.deliver_area` | string | Zone name. |
| `response.shipping_document_info.ec_order_no` | string | The name of ec order. |
| `response.shipping_document_info.create_date_ymd_sl` | string | The date of create shipment order. |
| `response.shipping_document_info.manufacturers_name` | string | The name of manufacturer. |
| `response.shipping_document_info.manufacturers_website` | string | The website of manufacturer. |
| `response.shipping_document_info.is_lm_dg_bool` | int32 | Use this field to indicate order contains dangerous goods or not. 0: Non-dangerous good 1: Dangerous good 2: Prohibited |
| `response.shipping_document_info.preferred_delivery_option` | int32 | Use this field to indicate delivery address is residential or office address. 0: not configured 1: office address 2: residential address |
| `response.shipping_document_info.spx_sub_district` | string | The sub-district of recipient's address. |
| `response.shipping_document_info.spx_receive_station` | object | The spx receive station. |
| `response.shipping_document_info.spx_receive_station.spx_first_receive_station` | string | The first pickup station. |
| `response.shipping_document_info.zone` | string | The zone of this order. |
| `response.shipping_document_info.zone_code` | string | Delivery Sub Zone. |
| `response.shipping_document_info.destination_base_code` | string | Distribution Center Code. |
| `response.shipping_document_info.last_third_digits_buyer_phone` | string | Use this field indicates buyer phone number (last 3 digits). For non-TW local sellers |
| `response.shipping_document_info.parcel_size` | string | corresponding locker sizing for self-collection locker channels [only available for specific logistic channels: 148003 and 140006] |
| `response.shipping_document_info.sod` | boolean | this value indicates whether the buyer select "scan on delivery" payment channel at checkout. |
| `response.shipping_document_info.buyer_cpf_id` | string | Buyer's CPF number for taxation and invoice purposes. Only for Brazil order. |
| `response.shipping_document_info.mutual_check` | int32 | only apply for ID/VN shops. mutual_check indicates whether the parcel is eligible for Return-on-the-Spot (RoS) co-check. If mutual_check=1, then the parcel is RoS eligible, where drivers and buyers can co-check the parcel. Buyer can then choose to accept or reject the parcel on the spot. If mutual_check=0, then the parcel is ineligible for RoS. |
| `response.shipping_document_info.dely_fri_label` | string | Probability of Successful Friday Delivery. The value of L(low), M(medium), H(high) represent the chances of successful delivery attempts on Friday. |
| `response.shipping_document_info.dely_sat_label` | string | Probability of Successful Saturday Delivery The value of L(low), M(medium), H(high) represent the chances of successful delivery attempts on Saturday. |
| `response.shipping_document_info.dely_sun_label` | string | Probability of Successful Sunday Delivery. The value of L(low), M(medium), H(high) represent the chances of successful delivery attempts on Sunday. |
| `response.shipping_document_info.pickup_code` | string | For drivers to quickly identify parcel to be picked up. Only returned for ID and TH local orders which use instant+sameday for delivery. |
| `response.shipping_document_info.sorting_group` | string | [Only for TW 30029 channel] This field indicate the sorting group value of the package. Available values: - North - South |
| `response.shipping_document_info.unpackaged_sku_id` | string | [Only for TW 30029 channel] Please refer to this number instead of tracking number for this this channel. This field will be empty for other channels. |
| `response.shipping_document_info.unpackaged_sku_id_qrcode` | string | [Only for TW 30029 channel] Please refer to this field to generate the QR code for the shipping document for this channel. This field will be empty for other channels. |
| `response.shipping_document_info.high_value` | boolean | This value indicates whether the order is considered a “high value” item and requires special handling by the logistics provider. The threshold to be considered "high value" item differs by region, and is only applicable to SPX channels. For regions other than Malaysia and Thailand, this field will always return empty. |
| `response.shipping_document_info.dg_specific_type` | int32 | Currently only applicable for Brazil, Indonesia, Vietnam, Philippines. For orders with Dangerous Goods, this value indicates the severity of the danger and requires special handling by the logistics provider. 0 = Not classified / no DG sub-type 1 = DG_A 2 = DG_B 3 = DG_C 4 = DG_D |
| `response.shipping_document_info.hotspot_id` | string | This ID is used by 3PL to determine parcel routing. For regions other than Malaysia and Thailand, this field will always return empty. |
| `response.shipping_document_info.weekend1_delivery_success_label` | string | This value indicates whether an order has a high / medium / low delivery success rate on each weekend (e.g. sat and sun respectively). For regions other than Malaysia, this field will always return empty. High = H Medium = M Low = L |
| `response.shipping_document_info.weekend2_delivery_success_label` | string | This value indicates whether an order has a high / medium / low delivery success rate on each weekend (e.g. sat and sun respectively). For regions other than Malaysia, this field will always return empty. High = H Medium = M Low = L |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
