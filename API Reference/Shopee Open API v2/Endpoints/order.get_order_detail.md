# order.get_order_detail

- Path: `/api/v2/order/get_order_detail`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to get order detail.
- Sumber: open.shopee.com/documents/v2/order.get_order_detail?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn_list` | string | ya | The set of order_sn. If there are multiple order_sn, you need to use English comma to connect them. limit [1,50] Contoh: `201214JAJXU6G7,201214JASXYXY6` |
| `request_order_status_pending` | boolean | tidak | Compatible parameter during migration period, send True will let API support PENDING status and return pending_terms, send False or don’t send will fallback to old logic Contoh: `true` |
| `response_optional_fields` | string | tidak | a response fields you want to get. Please select from the below response parameters. If you input an object field, all the params under it will be included automatically in the response. If there are multiple response fields you want to get, you need to use English comma to connect them. Available values: buyer_user_id,buyer_username,estimated_shipping_fee,recipient_address,actual_shipping_fee ,goods_to_declare,note,note_update_time,item_list,pay_time,dropshipper, dropshipper_phone,split_up,buyer_cancel_reason,cancel_by,cancel_reason,actual_shipping_fee_confirmed,buyer_cpf_id,fulfillment_flag,pickup_done_time,package_list,shipping_carrier,payment_method,total_amount,buyer_username,invoice_data,order_chargeable_weight_gram,return_request_due_date,edt,payment_info,international_label Contoh: `total_amount` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.order_list` | object[] | The list of orders. |
| `response.order_list[].order_sn` | string | Return by default. Shopee's unique identifier for an order. |
| `response.order_list[].region` | string | Return by default. The two-digit code representing the region where the order was made. |
| `response.order_list[].currency` | string | Return by default. The three-digit code representing the currency unit for which the order was paid. |
| `response.order_list[].cod` | boolean | Return by default. This value indicates whether the order was a COD (cash on delivery) order. |
| `response.order_list[].total_amount` | float | The total amount paid by the buyer for the order. This amount includes the total sale price of items, shipping cost beared by buyer; and offset by Shopee promotions if applicable. This value will only return after the buyer has completed payment for the order. |
| `response.order_list[].pending_terms` | string[] | The list of pending terms. Applicable values: - SYSTEM_PENDING: Under Shopee internal processing. - KYC_PENDING: Under KYC checking (TW CB order only). - ARRANGE_SHIPMENT_PENDING: Temporarily held due to 3PL capacity constraints. |
| `response.order_list[].pending_description` | string[] | The value of this field is the description of pending reason corresponding with pending terms. Applicable values: - For SYSTEM_PENDING: Order is being processed by Shopee. - For KYC_PENDING: Order is pending buyer TW KYC pre-authorization. - For ARRANGE_SHIPMENT_PENDING: Allocating delivery resources due to high order volume. Label print will be available within 4 days after buyer paid. |
| `response.order_list[].order_status` | string | Return by default. Enumerated type that defines the current status of the order. |
| `response.order_list[].shipping_carrier` | string | The logistics service provider that the buyer selected for the order to deliver items. Note: If logistics_channel_id is 90021, 90025 or 90026, service_code will be appended, e.g., Entrega Turbo - M1020. |
| `response.order_list[].payment_method` | string | The payment method that the buyer selected to pay for the order. Applicable values: See Data Definition- Payment Methods. |
| `response.order_list[].estimated_shipping_fee` | float | The estimated shipping fee is an estimation calculated by Shopee based on specific logistics courier's standard. |
| `response.order_list[].message_to_seller` | string | Return by default. Message to seller. |
| `response.order_list[].create_time` | timestamp | Return by default. Timestamp that indicates the date and time that the order was created. |
| `response.order_list[].update_time` | timestamp | Return by default. Timestamp that indicates the last time that there was a change in value of order, such as order status changed from 'Paid' to 'Completed'. |
| `response.order_list[].days_to_ship` | int32 | Return by default. Shipping preparation time set by the seller when listing item on Shopee. |
| `response.order_list[].ship_by_date` | timestamp | Return by default. The deadline to ship out the parcel. |
| `response.order_list[].buyer_user_id` | int64 | The user id of buyer of this order, will be empty if it is a non-integrated order in TW region. |
| `response.order_list[].buyer_username` | string | The name of buyer, will be masked as "****" if it is a non-integrated order in TW region. |
| `response.order_list[].recipient_address` | object | This object contains detailed breakdown for the recipient address. Different parameters might be masked according to each market and kind of seller. For TW region integrated channel orders will be all masked as "****". More details may refer the announcement. |
| `response.order_list[].recipient_address.name` | string | Recipient's name for the address. |
| `response.order_list[].recipient_address.phone` | string | Recipient's phone number input when order was placed. [Only for TW non-integrated channel] Will return "****" when the "virtual_contact_number" is available |
| `response.order_list[].recipient_address.town` | string | The town of the recipient's address. Whether there is a town will depend on the region and/or country. |
| `response.order_list[].recipient_address.district` | string | The district of the recipient's address. Whether there is a district will depend on the region and/or country. |
| `response.order_list[].recipient_address.city` | string | The city of the recipient's address. Whether there is a city will depend on the region and/or country. |
| `response.order_list[].recipient_address.state` | string | The state/province of the recipient's address. Whether there is a state/province will depend on the region and/or country. |
| `response.order_list[].recipient_address.region` | string | The two-digit code representing the region of the Recipient. |
| `response.order_list[].recipient_address.zipcode` | string | Recipient's postal code. |
| `response.order_list[].recipient_address.full_address` | string | The full address of the recipient, including country, state, even street, and etc. |
| `response.order_list[].recipient_address.geolocation` | object | Geolocation info. Only available for logistics_channel_id 90026. |
| `response.order_list[].recipient_address.geolocation.latitude` | float | Latitude. |
| `response.order_list[].recipient_address.geolocation.longitude` | float | Longitude. |
| `response.order_list[].actual_shipping_fee` | float | The actual shipping fee of the order if available from external logistics partners. |
| `response.order_list[].goods_to_declare` | boolean | Only work for cross-border order.This value indicates whether the order contains goods that are required to declare at customs. "T" means true and it will mark as "T" on the shipping label; "F" means false and it will mark as "P" on the shipping label. This value is accurate ONLY AFTER the order trackingNo is generated, please capture this value AFTER your retrieve the trackingNo. |
| `response.order_list[].note` | string | The note seller made for own reference. |
| `response.order_list[].note_update_time` | timestamp | Update time for the note. |
| `response.order_list[].item_list` | object[] | This object contains the detailed breakdown for the result of this API call. |
| `response.order_list[].item_list[].item_id` | int64 | Shopee's unique identifier for an item. |
| `response.order_list[].item_list[].item_name` | string | The name of the item. |
| `response.order_list[].item_list[].item_sku` | string | A item SKU (stock keeping unit) is an identifier defined by a seller, sometimes called parent SKU. Item SKU can be assigned to an item in Shopee Listings. |
| `response.order_list[].item_list[].model_id` | int64 | ID of the model that belongs to the same item. |
| `response.order_list[].item_list[].model_name` | string | Name of the model that belongs to the same item. A seller can offer models of the same item. For example, the seller could create a fixed-priced listing for a t-shirt design and offer the shirt in different colors and sizes. In this case, each color and size combination is a separate model. Each model can have a different quantity and price. |
| `response.order_list[].item_list[].model_sku` | string | A model SKU (stock keeping unit) is an identifier defined by a seller. It is only intended for the seller's use. Many sellers assign a SKU to an item of a specific type, size, and color, which are models of one item in Shopee Listings. |
| `response.order_list[].item_list[].model_quantity_purchased` | int32 | The number of identical items purchased at the same time by the same buyer from one listing/item. |
| `response.order_list[].item_list[].model_original_price` | float | The original price of the item in the listing currency. |
| `response.order_list[].item_list[].model_discounted_price` | float | The after-discount price of the item in the listing currency. If there is no discount, this value will be same as that of model_original_price. In case of bundle deal item, this value will return 0 as by design bundle deal discount will not be breakdown to item/model level. Due to technical restriction, the value will return the price before bundle deal if we don't configure it to 0. Please call GetEscrowDetails if you want to calculate item-level discounted price for bundle deal item. |
| `response.order_list[].item_list[].wholesale` | boolean | This value indicates whether buyer buy the order item in wholesale price. |
| `response.order_list[].item_list[].weight` | float | The weight of the item |
| `response.order_list[].item_list[].add_on_deal` | boolean | To indicate if this item belongs to an addon deal. |
| `response.order_list[].item_list[].main_item` | boolean | To indicate if this item is main item or sub item. True means main item, false means sub item. |
| `response.order_list[].item_list[].add_on_deal_id` | int64 | A unique ID to distinguish groups of items in Cart, and Order. (e.g. AddOnDeal) |
| `response.order_list[].item_list[].promotion_type` | string | Available type：product_promotion, flash_sale, bundle_deal, add_on_deal_main, add_on_deal_sub. For items which attend multiple promotions will only show one promotion, the order of priority is: bundle_deal > add_on_deal_main > add_on_deal_sub > product_promotion >flash_sale |
| `response.order_list[].item_list[].promotion_id` | int64 | The ID of the promotion. |
| `response.order_list[].item_list[].order_item_id` | int64 | The identify of order item. |
| `response.order_list[].item_list[].line_item_id` | int64 | The identity of order item. In case the order item is a bundle deal, this value will be unique to distinguish the order item |
| `response.order_list[].item_list[].promotion_group_id` | int32 | The identify of product promotion. |
| `response.order_list[].item_list[].image_info` | object | Image info of the product. |
| `response.order_list[].item_list[].image_info.image_url` | string | The image url of the product. Default to be variation image, if the model does not have a variation image, will use an item main image instead. |
| `response.order_list[].item_list[].product_location_id` | string | The fulfilment warehouse ID(s) of the items in the order. (Multi-Warehouse sellers only) |
| `response.order_list[].item_list[].is_prescription_item` | boolean | To indicate if this item is prescription item. Only for PH, TH, ID local shop. |
| `response.order_list[].item_list[].error_in_fetching_is_prescription_item` | boolean | To indicate if there was an error when validating whether this item is prescription. Default false. If is_prescription_item=false and this field is true, the item's prescription status is uncertain (label service call failed). Only for TH, PH, ID local shop. |
| `response.order_list[].item_list[].consultation_id` | string | An identifier of teleconsultation session which buyer did to order this item. Empty if item is not ordered through teleconsultation session |
| `response.order_list[].item_list[].is_b2c_owned_item` | boolean | determine if item is B2C_shop_item It should be ` is_b2c_shop_item ` but it was a bug from dev. Then now it's is_b2c_owned_item |
| `response.order_list[].item_list[].promotion_list` | object[] |  |
| `response.order_list[].item_list[].promotion_list[].promotion_type` | string | Indicates the type of item or package level promotion applied to a product. Each item can be associated with at most one item promotion and one package promotion at a time. Item Promotions: low_price_promotion deep_discount platform_sale seller_discount flash_sale wholesale welcome_package_free_gift brand_flash_sale in_shop_flash_sale synced_promo platform_streaming_price seller_streaming_price exclusive_streamer_price price_bidding_with_rebate price_bidding_without_rebate seller_advisor_price selling_price settlement_price campaign_settlement_price local_sip_settlement_price platform_exclusive_price seller_exclusive_price seller_member_exclusive_sku item_price order_sync_price Package Promotions: bundle_deal add_on_deal_main add_on_deal_sub |
| `response.order_list[].item_list[].promotion_list[].promotion_id` | int64 | Represents the unique identifier of a specific promotion applied to an item. Each promotion_id corresponds to a distinct promotion rule or campaign, defined under a particular promotion_type. The value is expressed in a numeric string format. |
| `response.order_list[].item_list[].hot_listing_item` | boolean | [Only for PH,TH,VN,MY,BR,TW] True if the item is hot listing. |
| `response.order_list[].item_list[].active_qty` | int32 | The quantity of the item model that remains active in the order and is still expected to be fulfilled. |
| `response.order_list[].item_list[].cancel_requested_qty` | int32 | The quantity of the item model that is currently under a cancellation request but has not yet reached the final cancelled status. |
| `response.order_list[].item_list[].cancelled_qty` | int32 | The quantity of the item model that has already been successfully cancelled. |
| `response.order_list[].item_list[].return_requested_qty` | int32 | The quantity of the item model that is currently under a return/refund request. |
| `response.order_list[].item_list[].returned_qty` | int32 | The quantity of the item model that has already been successfully returned through the return/refund process. |
| `response.order_list[].pay_time` | timestamp | The time when the order status is updated from UNPAID to PAID. This value is NULL when order is not paid yet. |
| `response.order_list[].dropshipper` | string | For Indonesia orders only. The name of the dropshipper. |
| `response.order_list[].dropshipper_phone` | string | The phone number of dropshipper, could be empty. |
| `response.order_list[].split_up` | boolean | To indicate whether this order is split to fullfil order(forder) level. Call GetForderInfo if it's "true". |
| `response.order_list[].buyer_cancel_reason` | string | Cancel reason from buyer, could be empty. |
| `response.order_list[].cancel_by` | string | Could be one of buyer, seller, system or Ops. |
| `response.order_list[].cancel_reason` | string | Use this field to get reason for buyer, seller, and system cancellation. |
| `response.order_list[].actual_shipping_fee_confirmed` | boolean | Use this filed to judge whether the actual_shipping_fee is confirmed. |
| `response.order_list[].buyer_cpf_id` | string | Buyer's CPF number for taxation and invoice purposes. Only for Brazil order. |
| `response.order_list[].fulfillment_flag` | string | Use this field to indicate the order is fulfilled by shopee or seller. Applicable values: fulfilled_by_shopee, fulfilled_by_cb_seller, fulfilled_by_local_seller. |
| `response.order_list[].pickup_done_time` | timestamp | The timestamp when pickup is done. |
| `response.order_list[].package_list` | object[] | The list of package under an order |
| `response.order_list[].package_list[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `response.order_list[].package_list[].logistics_status` | string | The Shopee logistics status for the order. Applicable values: See Data Definition-LogisticsStatus. |
| `response.order_list[].package_list[].logistics_channel_id` | int64 | The identity of logistic channel. |
| `response.order_list[].package_list[].shipping_carrier` | string | The logistics service provider that the buyer selected for the order to deliver items. Note: If logistics_channel_id is 90021, 90025 or 90026, service_code will be appended, e.g., Entrega Turbo - M1020. |
| `response.order_list[].package_list[].allow_self_design_awb` | boolean | To indicate whether the package allows for self-designed AWB, if allow_self_design_awb returns false, it means that the package does not allow for self-designed AWB and only the system-AWB can be used. |
| `response.order_list[].package_list[].item_list` | object[] | The lis of items. |
| `response.order_list[].package_list[].item_list[].item_id` | int64 | Shopee's unique identifier for an item. |
| `response.order_list[].package_list[].item_list[].model_id` | int64 | Shopee's unique identifier for a model. |
| `response.order_list[].package_list[].item_list[].model_quantity` | int32 | The number of identical items/variations purchased at the same time by the same buyer from one listing/item. |
| `response.order_list[].package_list[].item_list[].order_item_id` | int64 | The identify of order item. For items in one same bundle deal promotion, the order_item_id should share the same id, such as 1,2. For items not in bundle deal promotion, the order_item_id should be the same as item_id. |
| `response.order_list[].package_list[].item_list[].promotion_group_id` | int32 | The identify of product promotion. |
| `response.order_list[].package_list[].item_list[].product_location_id` | string | The warehouse ID of the item. |
| `response.order_list[].package_list[].parcel_chargeable_weight` | int | display weight used to calculate ASF for this parcel |
| `response.order_list[].package_list[].group_shipment_id` | int64 | The common identifier for multiple orders combined in the same parcel. |
| `response.order_list[].package_list[].virtual_contact_number` | string | [Only for TW non-integrated channel] The virtual phone number to contact the recipient. |
| `response.order_list[].package_list[].package_query_number` | string | [Only for TW non-integrated channel] The query number used in virtual phone number calls to contact the recipient of this package. |
| `response.order_list[].package_list[].sorting_group` | string | [Only for TW 30029 channel] This field indicate the sorting group value of the package. This field is only available for logistics_channel_id = 30029 and after the package has been arranged for shipment. |
| `response.order_list[].invoice_data` | object | The invoice data of the order. |
| `response.order_list[].invoice_data.number` | string | The number of the invoice. |
| `response.order_list[].invoice_data.series_number` | string | The series number of the invoice. |
| `response.order_list[].invoice_data.access_key` | string | The access key of the invoice. |
| `response.order_list[].invoice_data.issue_date` | timestamp | The issue date of the invoice. |
| `response.order_list[].invoice_data.total_value` | float | The total value of the invoice. |
| `response.order_list[].invoice_data.products_total_value` | float | The products total value of the invoice. |
| `response.order_list[].invoice_data.tax_code` | string | The tax code for the invoice. |
| `response.order_list[].checkout_shipping_carrier` | string | For non masking order, the logistics service provider that the buyer selected for the order to deliver items. For masking order, the logistics service type that the buyer selected for the order to deliver items. |
| `response.order_list[].reverse_shipping_fee` | float | Shopee charges the reverse shipping fee for the returned order.The value of this field will be non-negative. |
| `response.order_list[].order_chargeable_weight_gram` | int | display weight used to calculate ASF for this order |
| `response.order_list[].prescription_check_status` | int | Prescription check status. For ID, PH whitelisted sellers, the applicable values: 0: NONE 1: PASSED 2: FAILED For TH whitelisted sellers, the applicable values: 0: NONE 1: PASSED |
| `response.order_list[].pharmacist_name` | string | Name of the Pharmacist for Prescription Order. |
| `response.order_list[].prescription_images` | string[] | Return prescription images of this order, only for ID and PH whitelist sellers. Please add the prefix to review: for ID: https://cf.shopee.co.id/file/+prescription_image ("https://cf.shopee.co.id/file/+prescription_image") for PH:https://cf.shopee.ph/file/+prescription_image ("https://cf.shopee.co.id/file/+prescription_image") |
| `response.order_list[].prescription_approval_time` | timestamp | Time of when the prescription is approved. |
| `response.order_list[].prescription_rejection_time` | timestamp | Time of when the prescription is rejected. |
| `response.order_list[].prescription_reject_reason` | string | Return the reason why a prescription is rejected. If there is no rejection reason, return empty.Only for ID and PH whitelist sellers |
| `response.order_list[].is_buyer_shop_collection` | boolean | To indicate if this order is buyer self collection at store order |
| `response.order_list[].buyer_proof_of_collection` | string[] | The image url of the buyer self collection at the store. |
| `response.order_list[].edt_from` | timestamp | Earliest estimated delivery date of orders (only available for BR region) |
| `response.order_list[].edt_to` | timestamp | Latest estimated delivery time of orders (only available for BR region) |
| `response.order_list[].booking_sn` | string | Return by default. Shopee's unique identifier for a booking. Only returned for advance fulfilment matched order only. |
| `response.order_list[].advance_package` | boolean | Indicate whether order will be fulfilled using advance fulfilment stock or not. If value is true, order will be matched with a booking and seller should not arrange shipment. |
| `response.order_list[].return_request_due_date` | timestamp | This field represents the deadline for buyers to initiate returns and refunds after order is completed. The “return_request_due_date” response parameter will be returned if the requested order meets ALL the conditions below: - The status of the order is COMPLETED - The return refund eligibility of the order is true If you have any questions related to the function of "returns and refunds after order is completed," please refer to the following link: https://seller.shopee.tw/edu/article/18474 |
| `response.order_list[].payment_info` | object[] | [Only for BR] List of payment information, to follow NT 2025.001 ("https://drive.google.com/file/d/1VfqlbmXr3XR6BkpKOPUbLCgjiqvsBbLd/view?usp=sharing") (BR government invoice rules). |
| `response.order_list[].payment_info[].payment_method` | string | [Only for BR] Payment method used in the order, such as Credit Card, Debit Card, Pix, etc. |
| `response.order_list[].payment_info[].payment_processor_register` | string | [Only for BR] CNPJ of the payment processor handling the transaction. |
| `response.order_list[].payment_info[].card_brand` | string | [Only for BR] Card brand for credit or debit transactions, such as VISA, MASTER, etc. Empty string for Pix payments. |
| `response.order_list[].payment_info[].transaction_id` | string | [Only for BR] Payment authorization code generated by the bank or payment processor to validate the transaction. |
| `response.order_list[].payment_info[].payment_amount` | float | [Only for BR] Amount paid by the corresponding payment method. |
| `response.order_list[].hot_listing_order` | boolean | [Only for PH,TH,VN,MY,BR,TW] True if the order includes hot listing item. |
| `response.order_list[].is_international` | boolean | [Only for BR] Indicate if the order is SIP order. This field will only be returned if international_label is included in response_optional_field in the request. |
| `response.order_list[].can_full_cancel_order` | boolean | Indicates whether the order can be full cancelled: - If this value is true, seller can cancel the entire order - If the value is false, full order cancellation is not available for the order |
| `response.order_list[].can_partial_cancel_order` | boolean | Indicates whether the order is eligible for partial cancellation. This value is determined by both the system eligibility check and the buyer’s out-of-stock handling preference. - If this value is true, seller can cancel selected out-of-stock item quantities while continuing to fulfill the remaining items. - If this value is false, partial cancellation is not allowed. |
| `response.order_list[].buyer_preference_for_partial_cancellation` | int64 | Indicates the buyer’s preference for handling out-of-stock items in the order. Applicable values: 0 = Ship Available Items Only (The buyer allows the seller to cancel unavailable items and continue shipping the remaining available items) 1 = Cancel The Entire Order (The buyer does not allow partial cancellation. If any item is unavailable, the seller should cancel the entire order instead) |
| `response.order_list[].affiliate_sample_type` | int32 | Indicates that this order is a refundable sample order. Applicable values: 0 = Order is not a refundable sample order 1 = Order is a refundable sample order |
| `warning` | string[] | Indicate warning message you should take care. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
