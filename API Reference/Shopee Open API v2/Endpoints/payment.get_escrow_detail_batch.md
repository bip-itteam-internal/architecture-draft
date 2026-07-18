# payment.get_escrow_detail_batch

- Path: `/api/v2/payment/get_escrow_detail_batch`
- Method: GET
- Auth: shop
- Deskripsi: Use this API to fetch the details of order income by batch.
- Sumber: open.shopee.com/documents/v2/payment.get_escrow_detail_batch?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn_list` | string[] | ya | Shopee's unique identifier for an order. limit [1,50] The number of recommended requests ranges from 1 to 20 orders. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `response` | object[] |  |
| `response[].escrow_detail` | object | The escrow detail for one order |
| `response[].escrow_detail.order_sn` | string | Shopee's unique identifier for an order. <path></path> |
| `response[].escrow_detail.buyer_user_name` | string | The username of buyer. <path></path> |
| `response[].escrow_detail.return_order_sn_list` | string[] | The list of the serial number of return. <path></path> |
| `response[].escrow_detail.order_income` | object |  |
| `response[].escrow_detail.order_income.escrow_amount` | float | The total amount that the seller is expected to receive for the order and will change before order is completed. For non cb sip affiliate shop (new formula): escrow_amount= original_cost_of_goods_sold-original_shopee_discount+seller_return_refund+ shopee_discounts- voucher_from_seller- seller_coin_cash_back+ buyer_paid_shipping_fee- actual_shipping_fee+ shopee_shipping_rebate+ shipping_fee_discount_from_3pl- reverse_shipping_fee+ rsf_seller_protection_fee_claim_amount+ fsf_seller_protection_fee_claim_amount- final_return_to_seller_shipping_fee- seller_transaction_fee- service_fee- commission_fee- campaign_fee- shipping_seller_protection_fee_premium_amount- delivery_seller_protection_fee_premium_amount-final_escrow_product_gst- order_ams_commission fee- escrow_tax-sales_tax_on_lvg-reverse_shipping_fee_sst-shipping_fee_sst-withholding_tax-overseas_return_service_fee-vat_on_imported_goods - withholding_vat_tax - withholding_pit_tax - withholding_cit_tax - seller_order_processing_fee + buyer_paid_packaging_fee - trade_in_bonus_seller - fbs_fee - ads_escrow_top_up_fee_or_technical_support_fee - th_import_duty For cb sip affiliate shop: escrow_amount=escrow_amount_pri * exchange_rate note: Return refund amount = if adjustable RR, will equal to drc_adjustable_refund |
| `response[].escrow_detail.order_income.order_original_price` | float | The original price of the item before ANY promotion/discount in the listing currency. It returns the subtotal of that specific item if quantity exceeds 1. |
| `response[].escrow_detail.order_income.original_price` | float | The original price of the item before ANY promotion/discount in the listing currency. It returns the subtotal of that specific item if quantity exceeds 1. |
| `response[].escrow_detail.order_income.order_selling_price` | float | This field value = sum of item unit price.selling price comes from the sum up of each item's unit price. For non-bundle deal case, this value will be same like order_original_price; For bundle deal case, this value will be price of sum of item price before bundle deal promo but after item promo.It returns the subtotal of that specific item if quantity exceeds 1. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.bcrs_deposit` | float | The deposit fee paid by buyer of $0.10 per container as part of the SG Beverage Container Return Scheme mandated by the National Environment Agency (NEA). This value might be updated after RR/cancellation. |
| `response[].escrow_detail.order_income.order_seller_discount` | float | The total discount seller provided for this order. It returns the subtotal of that specific item if quantity exceeds 1. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.seller_discount` | float | Final sum of each item seller discount of a specific order. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.order_discounted_price` | float | The total discounted price for this order. It returns the subtotal of that specific item if quantity exceeds 1. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.shopee_discount` | float | Final sum of each item Shopee discount of a specific order. This amount will return remaining rebate value (i.e. remaining Shopee Item Rebate + remaining Shopee PIX Rebate) to seller. (Only display for non cb sip affiliate order. ) |
| `response[].escrow_detail.order_income.voucher_from_seller` | float | Final value of voucher provided by Seller for the order. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.voucher_from_shopee` | float | Final value of voucher provided by Shopee for the order. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.coins` | float | This value indicates the total amount offset when the buyer consumed Shopee Coins upon checkout. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.cross_border_tax` | float | Amount incurred by Buyer for purchasing items outside of home country. Amount may change after Return Refund. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.payment_promotion` | float | The amount offset via payment promotion. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.commission_fee` | float | The commission fee charged by Shopee platform if applicable. For CB SIP affiliate shop: commission_fee=commission_fee_pri * exchange_rate |
| `response[].escrow_detail.order_income.service_fee` | float | Amount charged by Shopee to seller for additional services. For CB SIP affiliate shop: service_fee=service_fee_pri * exchange_rate |
| `response[].escrow_detail.order_income.seller_transaction_fee` | float | Tansaction fee paid by seller for the order. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.seller_lost_compensation` | float | Compensation to seller in case of lost parcel. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.seller_coin_cash_back` | float | Value of coins provided by Seller for purchasing with his or her store for the order. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.escrow_tax` | float | Cross-border tax imposed by the Indonesian government on sellers. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.final_shipping_fee` | float | Final adjusted amount that seller has to bear as part of escrow. This amount could be negative or positive. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.actual_shipping_fee` | float | The final shipping cost of order and it is positive. For Non-integrated logistics channel is 0. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.shopee_shipping_rebate` | float | The platform shipping subsidy to the seller. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.shipping_fee_sst` | float | The Service Tax charged on Seller Paid Shipping Fee for forward shipping, based on Malaysia SST regulations for shipping fees on all orders. Definition of Seller Paid Shipping Fee is Actual Shipping Fee subtracted by sum of Shipping Fee Paid by Buyer and Shipping Rebate From Shopee. (Only applicable for non cb sip affiliate shop) |
| `response[].escrow_detail.order_income.shipping_fee_discount_from_pl` | float | The discount of shipping fee from 3PL. Currently only applicable to ID. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.seller_shipping_discount` | float | The shipping discount defined by seller. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.estimated_shipping_fee` | float | The estimated shipping fee is an estimation calculated by Shopee based on specific logistics courier's standard. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.seller_voucher_code` | float | The list of voucher code provided by seller. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.drc_adjustable_refund` | float | The adjustable refund amount from Shopee Dispute Resolution Center. |
| `response[].escrow_detail.order_income.refund_amount_to_buyer` | float | Amount returned to Seller in the event of Partial Return. |
| `response[].escrow_detail.order_income.cost_of_goods_sold` | float | Final amount paid by the buyer for the items in a specific order. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.original_cost_of_goods_sold` | float | Amount paid by the buyer for the items in a specific order. (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.original_shopee_discount` | float | Sum of each item Shopee discount of a specific order. This amount will return initial rebate value (i.e. remaining Shopee Item Rebate + remaining Shopee PIX Rebate) to seller. (Only display for non cb sip affiliate order. ) |
| `response[].escrow_detail.order_income.items` | object[] | This object contains the detailed breakdown for all the items in this order, including regular items(non-activity) and activity items. |
| `response[].escrow_detail.order_income.items[].item_id` | int64 | ID of item |
| `response[].escrow_detail.order_income.items[].item_name` | string | Name of item |
| `response[].escrow_detail.order_income.items[].item_sku` | string | A item SKU (stock keeping unit) is an identifier defined by a seller, sometimes called parent SKU. Item SKU can be assigned to an item in Shopee Listings. |
| `response[].escrow_detail.order_income.items[].model_id` | int64 | ID of the model that belongs to the same item. |
| `response[].escrow_detail.order_income.items[].model_name` | string | Name of the model that belongs to the same item. A seller can offer variations of the same item. For example, the seller could create a fixed-priced listing for a t-shirt design and offer the shirt in different colors and sizes. In this case, each color and size combination is a separate variation. Each variation can have a different quantity and price. |
| `response[].escrow_detail.order_income.items[].model_sku` | string | A model SKU (stock keeping unit) is an identifier defined by a seller. It is only intended for the seller's use. Many sellers assign a SKU to an item of a specific type, size, and color, which are variations of one item in Shopee Listings. |
| `response[].escrow_detail.order_income.items[].line_item_id` | int64 | The identity of order item. In case the order item is a bundle deal, this value will be unique to distinguish the order item. |
| `response[].escrow_detail.order_income.items[].original_price` | float | The original price of the item before ANY promotion/discount in the listing currency. It returns the subtotal of that specific item if quantity exceeds 1. |
| `response[].escrow_detail.order_income.items[].original_price_pri` | float | The agreed settlement price of items used as settlement basis, amount is in the primary currency. (Only display for CB SIP affiliate shop.) |
| `response[].escrow_detail.order_income.items[].selling_price` | float | For non-bundle deal case, this value will be same like item original_price; For bundle deal case, this value will be price of sum of item price before bundle deal promo but after item promo. It returns the subtotal of that specific item if quantity exceeds 1 (Only display for non cb sip affiliate shop.) |
| `response[].escrow_detail.order_income.items[].discounted_price` | float | The after-discount price of the item in the listing currency. It returns the subtotal of that specific item if quantity exceeds 1. If there is no discount, this value will be the same as that of original_price. |
| `response[].escrow_detail.order_income.items[].bcrs_deposit` | float | The deposit fee paid by buyer of $0.10 per container as part of the SG Beverage Container Return Scheme mandated by the National Environment Agency (NEA). This will be an initial value and will not update after RR/cancellation. |
| `response[].escrow_detail.order_income.items[].seller_discount` | float | The discount provided by seller for this item |
| `response[].escrow_detail.order_income.items[].shopee_discount` | float | The discount provided by Shopee for this item |
| `response[].escrow_detail.order_income.items[].discount_from_coin` | float | The offset of this item when the buyer consumed Shopee Coins upon checkout. In case of bundle deal item, this value will return 0. Due to technical restriction, this field will return incorrect value under bundle deal case if we don’t configure it to 0. |
| `response[].escrow_detail.order_income.items[].discount_from_voucher_shopee` | float | The offset of this item when the buyer use Shopee voucher. |
| `response[].escrow_detail.order_income.items[].discount_from_voucher_seller` | float | The offset of this item when the buyer use seller-specific voucher. |
| `response[].escrow_detail.order_income.items[].activity_type` | string | The type of the item, default is "". If the item is a bundle item the value is "bundle_deal", and if a add on deal item, the value is "add_on_deal" |
| `response[].escrow_detail.order_income.items[].activity_id` | int64 | If bundle_deal the is id of bundle deal, if add_on_deal this is id of add on deal. Unsigned 64-bit integer (uint64). Clients should treat this field as an identifier, not as a numeric type. |
| `response[].escrow_detail.order_income.items[].is_main_item` | boolean | Meaning a main or sub item for add_on_deal. |
| `response[].escrow_detail.order_income.items[].quantity_purchased` | int32 | This value indicates the number of identical items purchased at the same time by the same buyer from one listing/item. |
| `response[].escrow_detail.order_income.items[].is_b2c_shop_item` | boolean | Indicates whether this is a B2C owned item. |
| `response[].escrow_detail.order_income.items[].ams_commission_fee` | float | The amount of affiliate commission fee. Applicable for items sold via the Affiliate Program. |
| `response[].escrow_detail.order_income.items[].is_kit` | boolean | Indicates if this item is a kit. (Only for BR Local Sellers) |
| `response[].escrow_detail.order_income.items[].kit_items` | object | Only applicable to BR local sellers |
| `response[].escrow_detail.order_income.items[].kit_items.original_product_id` | float | The merchant item identifier of the product within the kit (Only for BR Local Sellers) |
| `response[].escrow_detail.order_income.items[].kit_items.original_model_id` | float | The merchant product model of the item within the kit (Only for BR Local Sellers) |
| `response[].escrow_detail.order_income.items[].kit_items.total_qty` | float | The quantity of this specific component within the kit. (Only for BR Local Sellers) |
| `response[].escrow_detail.order_income.items[].kit_items.original_price` | float | The price of the item when it is listed as a standalone item. |
| `response[].escrow_detail.order_income.items[].kit_items.proportional_price` | float | The price of the item when it is listed within the kit (i.e. proportionally distributed) (Only for BR Local Sellers) |
| `response[].escrow_detail.order_income.items[].promotion_list` | object[] |  |
| `response[].escrow_detail.order_income.items[].promotion_list[].promotion_type` | string | Indicates the type of item- or package-level promotion applied to a product. Each item can be associated with at most one item promotion and one package promotion at a time. Item Promotions: low_price_promotion deep_discount platform_sale seller_discount flash_sale wholesale welcome_package_free_gift brand_flash_sale in_shop_flash_sale synced_promo platform_streaming_price seller_streaming_price exclusive_streamer_price price_bidding_with_rebate price_bidding_without_rebate seller_advisor_price selling_price settlement_price campaign_settlement_price local_sip_settlement_price platform_exclusive_price seller_exclusive_price seller_member_exclusive_sku item_price order_sync_price Package Promotions: bundle_deal add_on_deal_main add_on_deal_sub |
| `response[].escrow_detail.order_income.items[].promotion_list[].promotion_id` | int64 | Represents the unique identifier of a specific promotion applied to an item. Each promotion_id corresponds to a distinct promotion rule or campaign, defined under a particular promotion_type. Unsigned 64-bit integer (uint64). Clients should treat this field as an identifier, not as a numeric type. |
| `response[].escrow_detail.order_income.escrow_amount_pri` | float | The total amount in the prim currency that the seller is expected to receive for the order and will change before order completed . escrow_amount_pri=original_price_pri-seller_return_refund_pri-commission_fee_pri-service_fee_pri-drc_adjustable_refund_pri.(Only display for cb sip affiliate order. ) |
| `response[].escrow_detail.order_income.buyer_total_amount_pri` | float | The total amount that paid by buyer in the primary currency. (Only display for cb sip affiliate order. ) |
| `response[].escrow_detail.order_income.original_price_pri` | float | The original price of the item before ANY promotion/discount in the primary currency. It returns the subtotal of that specific item if quantity exceeds 1.(Only display for cb sip affiliate order. ) <path></path> |
| `response[].escrow_detail.order_income.seller_return_refund_pri` | float | Amount returned to Seller in the event of Partial Return in the primary currency. (Only display for cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.commission_fee_pri` | float | The commission fee charged by Shopee platform if applicable in the primary currency. (Only display for cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.service_fee_pri` | float | Amount charged by Shopee to seller for additional services in the primary currency. (Only display for cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.drc_adjustable_refund_pri` | float | The adjustable refund amount from Shopee Dispute Resolution Center in the primary currency after proration. (Only applicable for cb sip affiliate shop.) |
| `response[].escrow_detail.order_income.pri_currency` | string | The currency of the country or region where the shop that real seller operates. (Only display for cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.aff_currency` | string | The currency of the country or region where shop opened in. (Only display for cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.exchange_rate` | float | Exchange rate from primary shop currency to affiliate shop currency. |
| `response[].escrow_detail.order_income.reverse_shipping_fee` | float | Shopee charges the reverse shipping fee for the returned order.The value of this field will be non-negative. |
| `response[].escrow_detail.order_income.reverse_shipping_fee_sst` | float | The Service Tax charged on Reverse Shipping Fee for reverse shipping, based on Malaysia SST regulations for shipping fees on all orders. (Only applicable for non cb sip affiliate shop) |
| `response[].escrow_detail.order_income.final_product_protection` | float | The total amount of product protection purchased during placing an order. |
| `response[].escrow_detail.order_income.credit_card_promotion` | float | This value indicate the offset via credit card promotion. |
| `response[].escrow_detail.order_income.credit_card_transaction_fee` | float | This value indicate the total transaction fee. credit_card_transaction_fee=buyer_transaction_fee+seller_transaction_fee |
| `response[].escrow_detail.order_income.final_product_vat_tax` | float | Value-added Tax is required for online purchases based on EU Value-added Tax regulations . (Only display for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.final_shipping_vat_tax` | float | Value-added Tax for product price is required for online purchases based on EU Value-added Tax regulations. (Only applicable for non cb sip affiliate shop. ) |
| `response[].escrow_detail.order_income.campaign_fee` | float | The campaign fee charged by Shopee platform. Only available for some local Indonesian shops. |
| `response[].escrow_detail.order_income.sip_subsidy` | float | The SIP subsidy amount is the difference between the item settlement price set by seller and item price actually paid by buyer. (Only available for CB SIP A Shops) |
| `response[].escrow_detail.order_income.sip_subsidy_pri` | float | The SIP subsidy amount is the difference between the item settlement price set by seller and item price actually paid by buyer. This value is in the primary currency. (Only available for CB SIP A Shops) |
| `response[].escrow_detail.order_income.rsf_seller_protection_fee_claim_amount` | float | The insurance claim amount if seller opt in to insurance program. this covers Reverse shipping Fee in the case of RR. As per Jun 2024: - For ID & MY Local: After Extension on coverage to FSF due to RR. this claim amount will consist of FSF + RSF claim. - For PH local: This will only cover RSF claim will be updated if there's any RR/cancellation |
| `response[].escrow_detail.order_income.rsf_seller_protection_fee_premium_amount` | float | Amount charged by Shopee to seller for additional services. Only apply for PH local orders. |
| `response[].escrow_detail.order_income.final_escrow_product_gst` | float | Goods and Service Tax for product price is required for imported goods (overseas orders) based on Singapore GST regulations. (Only applicable for non cb sip affiliate shop selling in Singapore) |
| `response[].escrow_detail.order_income.final_escrow_shipping_gst` | float | Goods and Service Tax for shipping fee is required for imported goods (overseas orders) based on Singapore GST regulations. (Only applicable for non cb sip affiliate shop selling in Singapore.) |
| `response[].escrow_detail.order_income.delivery_seller_protection_fee_premium_amount` | float | [Currently apply to ID & local orders only] An insurance premium charged to seller at the time parcel is picked up by 3PL for insurance in case of parcel lost/damaged by 3PL. |
| `response[].escrow_detail.order_income.order_ams_commission_fee` | float | The amount of affiliate commission fee for this order. Applicable for orders sold via the Affiliate Program. |
| `response[].escrow_detail.order_income.buyer_payment_method` | float | The payment method buyer used when do the order checkout. |
| `response[].escrow_detail.order_income.instalment_plan` | float | The instalment plan buyer chosen when do the order checkout. Only applicable when payment method support instalment. |
| `response[].escrow_detail.order_income.sales_tax_on_lvg` | float | Sales Tax on Low Value Goods (LVG) is required for imported goods (overseas orders) based on Malaysia SST regulations for selective orders (e.g. CB LVG orders in MY) |
| `response[].escrow_detail.order_income.withholding_tax` | float | Only for PH and ID local shops. PH: According to regulations issued by Bureau of Internal Revenue in PH, the Withholding Tax is applied to the gross remittances sent by Shopee to online suppliers of goods and services. ID: According to regulations issued by Directorate General of Taxation in ID, the Withholding Tax is applied to the income stated in the invoice generated via Shopee related to Seller and/or Merchants' sales in Shopee's platform. |
| `response[].escrow_detail.order_income.overseas_return_service_fee` | float | This is overseas return service fee charged to sellers who register ORS program.(Only applicable for non cb sip affiliate shop) |
| `response[].escrow_detail.order_income.prorated_coins_value_offset_return_items` | float | This is the prorated value from cash equivalent of coin offset due to adjustable RR.This field will only be updated when there is an adjustable RR. If it's a full RR or normal order will response 0. |
| `response[].escrow_detail.order_income.prorated_shopee_voucher_offset_return_items` | float | This is the prorated refund value from shopee voucher discount due to adjustable RR.This field will only be updated when there is an adjustable RR. If it's a full RR or normal order will response 0. |
| `response[].escrow_detail.order_income.prorated_seller_voucher_offset_return_items` | float | This is the prorated refund value from seller voucher discount due to adjustable RR.This field will only be updated when there is an adjustable RR. If it's a full RR or normal order will response 0. |
| `response[].escrow_detail.order_income.prorated_payment_channel_promo_bank_offset_return_items` | float | This is the prorated value from bank payment channel promo due to adjustable RR.This field will only be updated when there is an adjustable RR.If it's a full RR or normal order will response 0. |
| `response[].escrow_detail.order_income.prorated_payment_channel_promo_shopee_offset_return_items` | float | This is the prorated value from shopee payment channel promo due to adjustable RR.This field will only be updated when there is an adjustable RR.If it's a full RR or normal order will response 0. |
| `response[].escrow_detail.order_income.fsf_seller_protection_fee_claim_amount` | float | The claim amount given to seller if seller opt in to shipping fee service program. this covers Forward Shipping Fee cost in the case of cancelled due to Failed delivery. only apply to PH Local as per Jun 2024. |
| `response[].escrow_detail.order_income.shipping_seller_protection_fee_amount` | float | Service fee charged to seller in MY,ID,PH,BR Local (as per Jun 2024) due to additional program purchased |
| `response[].escrow_detail.order_income.final_return_to_seller_shipping_fee` | float | The amount of fee charged to seller (if any) for the failed delivery order |
| `response[].escrow_detail.order_income.vat_on_imported_goods` | float | 7% VAT is charged for imported goods entering Thailand |
| `response[].escrow_detail.order_income.withholding_vat_tax` | float | By VN law, E-commerce platforms need to Withhold VAT tax applicable to all VN business household and VN individual sellers |
| `response[].escrow_detail.order_income.withholding_pit_tax` | float | By VN law, E-commerce platforms need to Withhold Personal Income Tax applicable to all VN business household and VN individual sellers |
| `response[].escrow_detail.order_income.withholding_cit_tax` | float | By VN law, E-commerce platforms need to Withhold Personal Income Tax applicable to corporate sellers selling in VN region |
| `response[].escrow_detail.order_income.tax_registration_code` | string | For VN Withholding Tax. This is the Tax Registration Number (TRN) from Seller Info (Business information) of the seller at the point of order creation |
| `response[].escrow_detail.order_income.seller_order_processing_fee` | float | Order Processing Fee is the amount charged to sellers for every order created. |
| `response[].escrow_detail.order_income.buyer_paid_packaging_fee` | float | The fee charged to the buyer for packaging materials. |
| `response[].escrow_detail.order_income.trade_in_bonus_seller` | float | The discount provided by Seller/Retailers for buyers who opt for trade-in. |
| `response[].escrow_detail.order_income.fbs_fee` | float | Fulfilled by Shopee (FBS) Fee applied to this order, covering costs such as handling and storage and packaging. Only for PH Local Orders. |
| `response[].escrow_detail.order_income.net_commission_fee` | float | The respective fee amounts after the proportional rebate deduction.The total net commission fee applied to the order, calculated as the sum of all net commission fee items. -only for BR local sellers. |
| `response[].escrow_detail.order_income.net_service_fee` | float | The respective fee amounts after the proportional rebate deduction.The total net service fee applied to the order, calculated as the sum of all net service fee items. -only for BR local sellers. |
| `response[].escrow_detail.order_income.net_commission_fee_info_list` | object | Returns a breakdown of the net commission fees. -only for BR local sellers. |
| `response[].escrow_detail.order_income.net_commission_fee_info_list.rule_id` | float | The unique identifier of the commission rule applied to calculate the net commission fee. |
| `response[].escrow_detail.order_income.net_commission_fee_info_list.fee_amount` | float | The net commission fee amount calculated based on the corresponding commission rule. |
| `response[].escrow_detail.order_income.net_commission_fee_info_list.rule_display_name` | string | The display name of the commission rule for reference and readability. |
| `response[].escrow_detail.order_income.net_service_fee_info_list` | object | Returns a breakdown of the net service fees. -only for BR local sellers. |
| `response[].escrow_detail.order_income.net_service_fee_info_list.rule_id` | float | The unique identifier of the service fee rule applied to calculate the net service fee. |
| `response[].escrow_detail.order_income.net_service_fee_info_list.fee_amount` | float | The net service fee amount calculated based on the corresponding service fee rule. |
| `response[].escrow_detail.order_income.net_service_fee_info_list.rule_display_name` | string | The display name of the service fee rule for reference and readability. |
| `response[].escrow_detail.order_income.net_service_fee_info_list.category` | string | The category of the service fee, indicating the type of service the fee is charged for. |
| `response[].escrow_detail.order_income.seller_product_rebate` | object | The shopee rebate borne by seller. -only for BR local sellers. |
| `response[].escrow_detail.order_income.seller_product_rebate.amount` | float | This is the portion of Shopee rebate borne by seller. |
| `response[].escrow_detail.order_income.seller_product_rebate.commission_fee_offset` | float | This is the offset to gross commission fee, reducing it to the net value. |
| `response[].escrow_detail.order_income.seller_product_rebate.service_fee_offset` | float | This is the offset to gross service fee, reducing it to the net value. |
| `response[].escrow_detail.order_income.pix_discount` | float | [BR only]Final sum of pix discount of a specific order. (Only display for non cb sip affiliate shop.) |
| `response[].escrow_detail.order_income.prorated_pix_discount_offset_return_items` | float | [BR only]This is the prorated value from pix discount due to adjustable RR. This field will only be updated when there is an adjustable RR. If it's a full RR or normal order, will response 0. |
| `response[].escrow_detail.order_income.ads_escrow_top_up_fee_or_technical_support_fee` | float | Includes both ads escrow top up fee (auto escrow top up to your ads balance) and technical support fee (charged by Shopee) The actual fee type included in this field varies depending on the seller type and selling region, and may represent one of the following in Shopee Seller Center: Ads Escrow Top-Up Fee For local MY TH SG VN PH ID sellers and CNCB / JPCB / KRCB sellers selling in PH and ID For JPCB sellers selling in SG, MY, TH, and VN Technical Support Fee For CNCB sellers selling in SG, MY, TH, and VN Traffic Growth Fee For KRCB sellers selling in SG, MY, TH, and VN |
| `response[].escrow_detail.order_income.th_import_duty` | float | [TH only] Import Duty collected for imported goods entering Thailand |
| `response[].escrow_detail.buyer_payment_info` | object | The buyer payment info at order checkout moment. (snapshot value) |
| `response[].escrow_detail.buyer_payment_info.buyer_payment_method` | string | The payment method used by buyer. |
| `response[].escrow_detail.buyer_payment_info.buyer_service_fee` | string | An additional service fee charged by shopee to Buyer at checkout. currently only applicable to ID region. it is an initial value (will not be updated after RR/cancellation) |
| `response[].escrow_detail.buyer_payment_info.buyer_tax_amount` | float | The tax amount paid by buyer. currently this is a custom tax charged to CB orders in TW,CL,MX |
| `response[].escrow_detail.buyer_payment_info.buyer_total_amount` | float | The total amount paid by buyer at checkout moment. |
| `response[].escrow_detail.buyer_payment_info.shopeevip_subtotal` | float | The subscription fee paid by buyer for ShopeeVIP. |
| `response[].escrow_detail.buyer_payment_info.bcrs_discount` | float | The deposit fee paid by buyer of $0.10 per container as part of the SG Beverage Container Return Scheme mandated by the National Environment Agency (NEA). This will be an initial value and will not update after RR/cancellation. |
| `response[].escrow_detail.buyer_payment_info.credit_card_promotion` | float | The promotion provided by credit card. it is an initial value (will not be updated after RR/cancellation) |
| `response[].escrow_detail.buyer_payment_info.icms_tax_amount` | float | The icms tax paid by buyer. this is only applicable to BR region. it is an initial value (will not be updated after RR/cancellation) |
| `response[].escrow_detail.buyer_payment_info.import_tax_amount` | float | The import tax paid by buyer. it is an initial value (will not be updated after RR/cancellation) |
| `response[].escrow_detail.buyer_payment_info.initial_buyer_txn_fee` | float | Transaction fee paid by buyer for the order. (Only display for non cb sip affiliate shop. ). Most regions would have this fee charged to buyer at checkout depending on the fee rules applied in each region. it is an initial value (will not be updated after RR/cancellation) |
| `response[].escrow_detail.buyer_payment_info.insurance_premium` | float | The insurance premium paid by buyer. Currently only applicable to some regions like ID & BR it is an initial value (will not be updated after RR/cancellation) |
| `response[].escrow_detail.buyer_payment_info.iof_tax_amount` | float | The iof tax paid by buyer. this is only applicable for BR region. it is an initial value (will not be updated after RR/cancellation) |
| `response[].escrow_detail.buyer_payment_info.is_paid_by_credit_card` | boolean | Whether this order is paid by credit card. it's related to payment channel used at checkout |
| `response[].escrow_detail.buyer_payment_info.merchant_subtotal` | float | The total item price paid by buyer at checkout. it is an initial value and will not be updated after RR/cancellation |
| `response[].escrow_detail.buyer_payment_info.seller_voucher` | float | The voucher provided by seller to offset some value needs to be paid by buyer. it is an initial value (will not be updated after RR/cancellation) |
| `response[].escrow_detail.buyer_payment_info.shipping_fee` | float | The shipping fee paid by buyer. (Only display for non cb sip affiliate shop. it is an initial value (will not be updated after RR/cancellation) |
| `response[].escrow_detail.buyer_payment_info.shipping_fee_sst_amount` | float | The shipping fee sst paid by buyer. Currently apply to MY region only it is an initial value (will not be updated after RR/cancellation) |
| `response[].escrow_detail.buyer_payment_info.shopee_voucher` | float | The voucher provided by Shopee to offset the amount need to be paid by buyer. it is an initial value (will not be updated after RR/cancellation) |
| `response[].escrow_detail.buyer_payment_info.shopee_coins_redeemed` | float | This is an amount of coin used by buyer at checkout to offset some amount to be paid. it is an initial value (will not be updated after RR/cancellation) |
| `response[].escrow_detail.buyer_payment_info.buyer_paid_packaging_fee` | float | The fee charged to the buyer for packaging materials. |
| `response[].escrow_detail.buyer_payment_info.trade_in_bonus` | float | The total amount of all trade-in bonuses applied to a transaction. This value is the summation of the bonuses contributed by all four parties: Shopee, Seller, Bank and Trade-in Partner. |
| `response[].escrow_detail.buyer_payment_info.bulky_handling_fee` | float | A fee charged to the buyer for the special handling and transportation required for items that exceed a specified weight or dimension threshold.Only for local ID sellers. |
| `response[].escrow_detail.buyer_payment_info.discount_pix` | float | The discount provided by PIX (Only applicable for BR region) |
| `response[].escrow_detail.buyer_payment_info.bcrs_deposit` | float | The deposit fee paid by buyer of $0.10 per container as part of the SG Beverage Container Return Scheme mandated by the National Environment Agency (NEA). This will be an initial value and will not update after RR/cancellation. |
| `response[].escrow_detail.buyer_payment_info.ads_voucher_discount` | float | The voucher provided by Ads team to offset the amount need to be paid by buyer. it is an initial value (will not be updated after RR/cancellation) |
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Error code |
| `message` | string | Error message |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
