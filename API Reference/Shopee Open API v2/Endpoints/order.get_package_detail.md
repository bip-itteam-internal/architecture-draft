# order.get_package_detail

- Path: `/api/v2/order/get_package_detail`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to get package detail.
- Sumber: open.shopee.com/documents/v2/order.get_package_detail?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `package_number_list` | string | ya | The set of package_number. If there are multiple package_number, you need to use English comma to connect them. limit [1,50] Contoh: `OFG1156498731071468,OFG199593509207187` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.package_list` | object[] | The list of packages. |
| `response.package_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `response.package_list[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `response.package_list[].fulfillment_status` | string | The Shopee fulfillment status for the package. Applicable values: See V2.0 Data Definition - PackageFulfillmentStatus. |
| `response.package_list[].update_time` | int64 | Timestamp that indicates the last time that there was a change in value of package. |
| `response.package_list[].logistics_channel_id` | int64 | The identity of logistic channel. |
| `response.package_list[].shipping_carrier` | string | The logistics service provider that the buyer selected for the package to deliver items. Note: If logistics_channel_id is 90021, 90025 or 90026, service_code will be appended, e.g., Entrega Turbo - M1020. |
| `response.package_list[].allow_self_design_awb` | boolean | To indicate whether the package allows for self-designed AWB, if allow_self_design_awb returns false, it means that the package does not allow for self-designed AWB and only the system-AWB can be used. |
| `response.package_list[].days_to_ship` | int64 | Shipping preparation time set by the seller when listing item on Shopee. |
| `response.package_list[].ship_by_date` | int64 | The deadline to ship out the package. |
| `response.package_list[].pending_terms` | string[] | The list of pending terms. Applicable values: - SYSTEM_PENDING: Under Shopee internal processing. - KYC_PENDING: Under KYC checking (TW CB order only). - ARRANGE_SHIPMENT_PENDING: Temporarily held due to 3PL capacity constraints. |
| `response.package_list[].pending_description` | string[] | The value of this field is the description of pending reason corresponding with pending terms. Applicable values: - For SYSTEM_PENDING: Order is being processed by Shopee. - For KYC_PENDING: Order is pending buyer TW KYC pre-authorization. - For ARRANGE_SHIPMENT_PENDING: Allocating delivery resources due to high order volume. Label print will be available within 4 days after buyer paid. |
| `response.package_list[].tracking_number` | string | The tracking number of this package. |
| `response.package_list[].tracking_number_expiration_date` | int64 | [TW only] Tracking number expiration date |
| `response.package_list[].pickup_done_time` | int64 | The timestamp when pickup is done. |
| `response.package_list[].is_split_up` | boolean | To indicate whether this parcel is split. |
| `response.package_list[].item_list` | object[] | The lis of items in the package. |
| `response.package_list[].item_list[].item_id` | int64 | Shopee's unique identifier for an item. |
| `response.package_list[].item_list[].model_id` | int64 | Shopee's unique identifier for a model. |
| `response.package_list[].item_list[].item_sku` | string | A item SKU (stock keeping unit) is an identifier defined by a seller, sometimes called parent SKU. Item SKU can be assigned to an item in Shopee Listings. |
| `response.package_list[].item_list[].model_sku` | string | ID of the model that belongs to the same item. |
| `response.package_list[].item_list[].model_quantity` | int64 | The number of identical items/variations purchased at the same time by the same buyer from one listing/item. |
| `response.package_list[].item_list[].order_item_id` | int64 | The identify of order item. For items in one same bundle deal promotion, the order_item_id should share the same id, such as 1,2. For items not in bundle deal promotion, the order_item_id should be the same as item_id. |
| `response.package_list[].item_list[].promotion_group_id` | int64 | The identify of product promotion. |
| `response.package_list[].item_list[].product_location_id` | string | The warehouse ID of the item. |
| `response.package_list[].item_list[].consultation_id` | string | An identifier of teleconsultation session which buyer did to order this item. Empty if item is not ordered through teleconsultation session |
| `response.package_list[].item_list[].is_prescription_item` | boolean | To indicate if this item is a prescription item. Default false. Only for PH, TH, ID whitelist shops. |
| `response.package_list[].item_list[].error_in_fetching_is_prescription_item` | boolean | To indicate if there was an error when validating whether this item is prescription. Default false. If is_prescription_item=false and this field is true, the item's prescription status is uncertain (label service call failed). Only for PH, TH, ID whitelist shops. |
| `response.package_list[].item_list[].prescription_check_status` | int32 | Prescription check status. For ID, PH whitelisted sellers, the applicable values: 0: NONE 1: PASSED 2: FAILED For TH whitelisted sellers, the applicable values: 0: NONE 1: PASSED |
| `response.package_list[].item_list[].prescription_reject_reason` | string | Return the reason why a prescription is rejected. If no rejection reason, return empty. Only for ID and PH whitelist sellers. |
| `response.package_list[].recipient_address` | object | This object contains detailed breakdown for the recipient address. Different parameters might be masked according to each market and kind of seller. For TW region integrated channel orders will be all masked as "****". More details may refer the announcement. |
| `response.package_list[].recipient_address.name` | string | Recipient's name for the address. |
| `response.package_list[].recipient_address.phone` | string | Recipient's phone number input when order was placed. [Only for TW non-integrated channel] Will return "****" when the "virtual_contact_number" is available |
| `response.package_list[].recipient_address.town` | string | The town of the recipient's address. Whether there is a town will depend on the region and/or country. |
| `response.package_list[].recipient_address.district` | string | The district of the recipient's address. Whether there is a district will depend on the region and/or country. |
| `response.package_list[].recipient_address.city` | string | The city of the recipient's address. Whether there is a city will depend on the region and/or country. |
| `response.package_list[].recipient_address.state` | string | The state/province of the recipient's address. Whether there is a state/province will depend on the region and/or country. |
| `response.package_list[].recipient_address.region` | string | The two-digit code representing the region of the Recipient. |
| `response.package_list[].recipient_address.zipcode` | string | Recipient's postal code. |
| `response.package_list[].recipient_address.full_address` | string | The full address of the recipient, including country, state, even street, and etc. |
| `response.package_list[].recipient_address.geolocation` | object | Geolocation info. Only available for logistics_channel_id 90026. |
| `response.package_list[].recipient_address.geolocation.latitude` | float | Latitude. |
| `response.package_list[].recipient_address.geolocation.longitude` | float | Longitude. |
| `response.package_list[].parcel_chargeable_weight_gram` | int64 | display weight used to calculate ASF for this parcel |
| `response.package_list[].group_shipment_id` | int64 | The common identifier for multiple orders combined in the same parcel. |
| `response.package_list[].virtual_contact_number` | string | [Only for TW non-integrated channel] The virtual phone number to contact the recipient. |
| `response.package_list[].package_query_number` | string | [Only for TW non-integrated channel] The query number used in virtual phone number calls to contact the recipient of this package. |
| `response.package_list[].sorting_group` | string | [Only for TW 30029 channel] This field indicate the sorting group value of the package. This field is only available for logistics_channel_id = 30029 and after the package has been arranged for shipment. |
| `response.package_list[].is_shipment_arranged` | boolean | Only effective when the package's logistics_status/fulfillment_status is LOGISTICS_READY. This parameter further distinguishes between two scenarios: - true: Package shipment has been arranged (Seller has processed shipment, system is generating tracking number, not yet updated to LOGISTICS_REQUEST_CREATED, no duplicate action needed) - false: Package awaiting shipment arrangement (Seller hasn't processed shipment yet, shipping arrangement required) |
| `response.package_list[].status_info_tag` | object | Package shipping urgency tag information. |
| `response.package_list[].status_info_tag.tag_id` | int32 | Shipping urgency tag type, applicable values below: 0: No tag 1: Will be cancelled within 1 day 2: Must ship before the specified timestamp 3: Shipment delayed 4: Must ship within the current hour 5: Will be cancelled at the specified timestamp |
| `response.package_list[].status_info_tag.timestamp` | timestamp | When tag_id is 2 or 5, returns specific timestamp (e.g., cancel time, shipment deadline); otherwise returns 0. |
| `response.package_list[].can_split_order` | boolean | This field indicates whether this order can be split into multiple packages for separate shipment. - true: Support splitting, can call v2.order.split_order to execute - false: Does not support splitting |
| `response.package_list[].can_unsplit_order` | boolean | This field indicates whether this order can be unsplit. - true: Support unsplitting, can call v2.order.unsplit_order to execute - false: Does not support unsplitting |
| `response.package_list[].is_pre_order` | boolean | This field indicates whether this order is a pre-order. - true: Pre-order - false: Non pre-order |
| `response.package_list[].pharmacist_name` | string | Name of the Pharmacist for Prescription Order. |
| `response.package_list[].prescription_images` | string[] | Return prescription images of this order, only for ID and PH whitelist sellers. Please add the prefix to review: for ID: https://cf.shopee.co.id/file/+prescription_image for PH: https://cf.shopee.ph/file/+prescription_image |
| `response.package_list[].prescription_approval_time` | timestamp | Time of when the prescription is approved. |
| `response.package_list[].prescription_rejection_time` | timestamp | Time of when the prescription is rejected. |
| `response.package_list[].is_buyer_shop_collection` | boolean | To indicate if this order is buyer self collection at store order. |
| `response.package_list[].buyer_proof_of_collection` | string[] | The image url of the proof for buyer self collection at the store. |
| `response.package_list[].preparation_end_time` | timestamp | The system-calculated deadline for package preparation. When the package fulfillment_status/logistics_status changes to "LOGISTICS_READY", the system calculates this time based on the "Preparation Time" configured for the logistics channel of this package. Notes: 1) Only effective for logistics channels that have Auto Call Driver enabled and Preparation Time configured. 2) Seller needs to complete packing and waybill printing before this time to ensure the package is ready when the driver arrives. 3) When this time is reached, the system will automatically arrange shipment and trigger driver dispatch: - If driver calling is successful, the package fulfillment_status/logistics_status will change from “LOGISTICS_READY” to “LOGISTICS_REQUEST_CREATED”. - If driver calling fails, the package fulfillment_status/logistics_status will remain unchanged, and the seller must arrange shipment manually. |
| `response.package_list[].driver_info` | object | After the driver is successfully called, the driver's information will be returned. Note: Data availability depends on the specific 3PL provider; certain fields may be omitted due to provider policies, PII restrictions, or data unavailability. |
| `response.package_list[].driver_info.driver_name` | string | Driver Name |
| `response.package_list[].driver_info.driver_phone` | string | Driver phone number |
| `response.package_list[].driver_info.vehicle_type` | string | Delivery vehicle type |
| `response.package_list[].driver_info.license_plate` | string | License plate number |
| `response.package_list[].driver_info.courier_photo` | string | URL of the driver's photo |
| `response.package_list[].driver_info.eta_start_time` | int64 | Earliest estimated arrival time at pickup address |
| `response.package_list[].driver_info.eta_end_time` | int64 | Latest estimated arrival time at pickup address |
| `response.package_list[].driver_info.driver_status` | string | Driver status. Applicable values: - Allocating Driver - Driver assigned - Driver is on the way - Driver is arrived - Driver should arrive by {starting_time} - {end_time} |
| `response.package_list[].can_full_cancel_order` | boolean | Indicates whether the order can be full cancelled: - If this value is true, seller can cancel the entire order - If the value is false, full order cancellation is not available for the order |
| `response.package_list[].can_partial_cancel_order` | boolean | Indicates whether the order is eligible for partial cancellation. This value is determined by both the system eligibility check and the buyer’s out-of-stock handling preference. - If this value is true, seller can cancel selected out-of-stock item quantities while continuing to fulfill the remaining items. - If this value is false, partial cancellation is not allowed. |
| `response.package_list[].buyer_preference_for_partial_cancellation` | int64 | Indicates the buyer’s preference for handling out-of-stock items in the order. Applicable values: 0 = Ship Available Items Only (The buyer allows the seller to cancel unavailable items and continue shipping the remaining available items) 1 = Cancel The Entire Order (The buyer does not allow partial cancellation. If any item is unavailable, the seller should cancel the entire order instead) |
| `warning` | string | Indicate warning message you should take care. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
