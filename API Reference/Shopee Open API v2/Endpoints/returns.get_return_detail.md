# returns.get_return_detail

- Path: `/api/v2/returns/get_return_detail`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to get detail information of a return by return sn.
- Sumber: open.shopee.com/documents/v2/returns.get_return_detail?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `return_sn` | string | ya | The serial number of return. Contoh: `2206150VT13E3MQ` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking |
| `error` | string | error code |
| `message` | string | error description |
| `response` | object | Amount of the refund. |
| `response.image` | string[] | Image URLs of return. |
| `response.buyer_videos` | object[] |  |
| `response.buyer_videos[].thumbnail_url` | string | The thumbnail url of video |
| `response.buyer_videos[].video_url` | string | The url of video |
| `response.reason` | string | Indicates the original return reason submitted by the buyer when initiating the return request. Applicable values: See Data Definition- ReturnReason and Reassessed Request Reason. Note: There may be cases where Shopee Agent updates the return request with a "Reassessed Return Reason" after reviewing more details about the buyer's return request and potentially after requesting evidence from the seller. If the platform updates the return reason during this process, the reassessed outcome will be provided separately in the reassessed_request_reason field. |
| `response.text_reason` | string | Reason that buyer provide. |
| `response.reassessed_request_reason` | string | Indicates the return reason reassessed by the platform as more suitable. There may be cases where Shopee Agent updates the return request with a "Reassessed Return Reason" after reviewing more details about the buyer's return request and potentially after requesting evidence from the seller. Applicable values: See Data Definition- ReturnReason and Reassessed Request Reason. If no reassessment has been made, the value will be NONE. |
| `response.return_sn` | string | The serial number of return. |
| `response.refund_amount` | float | Amount of the refund. |
| `response.currency` | string | Currency of the return. |
| `response.create_time` | timestamp | The time of return create. |
| `response.update_time` | timestamp | The time of modify return. |
| `response.status` | string | Enumerated type that defines the current status of the return. Applicable values: See Data Definition- ReturnStatus. |
| `response.due_date` | timestamp | The last time seller deal with this return. |
| `response.tracking_number` | string | The tracking number assigned by the shipping carrier for item shipment. |
| `response.dispute_reason` | string[] | The reason of seller dispute return. While the return has been disputed, this field is useful. Applicable values: See Data Definition- ReturnDisputeReason. |
| `response.dispute_text_reason` | string[] | The reason that seller provide. While the return has been disputed, this field is useful. |
| `response.needs_logistics` | boolean | Items to be sent back to seller. Can be either integrated/non-integrated. |
| `response.amount_before_discount` | float | Order price before discount. |
| `response.user` | object |  |
| `response.user.username` | string | Buyer's nickname, will be masked as "****" if it is a non-integrated return in TW region. |
| `response.user.email` | string | Buyer's email, will be empty if it is a non-integrated return in TW region. |
| `response.user.portrait` | string | Buyer's portrait, will be empty if it is a non-integrated return in TW region. |
| `response.item` | object[] |  |
| `response.item[].model_id` | int64 | Shopee's unique identifier for a variation of an item. |
| `response.item[].name` | string | Name of item in local language. |
| `response.item[].images` | string[] | Image URLs of item. |
| `response.item[].amount` | int32 | Amount of this item. |
| `response.item[].item_price` | float | The price of item. |
| `response.item[].is_add_on_deal` | boolean | To indicate if this item belongs to an addon deal. |
| `response.item[].is_main_item` | boolean | To indicate if this item is main item or sub item. True means main item, false means sub item. |
| `response.item[].add_on_deal_id` | int64 | The unique identity of an addon deal. |
| `response.item[].item_id` | int64 | The id of item. |
| `response.item[].item_sku` | string | The sku of item. |
| `response.item[].variation_sku` | string | the variation sku of item |
| `response.item[].refund_amount` | float | item's refund amount. only for shops whitelisted for Partial Qty RR. If not available, refer to item_price |
| `response.order_sn` | string | Shopee's unique identifier for an order. |
| `response.return_ship_due_date` | timestamp | The due date for buyer to ship order. |
| `response.return_seller_due_date` | timestamp | The due date for seller to deal with this return when buyer have shipped order. |
| `response.activity` | object[] |  |
| `response.activity[].activity_id` | int64 | The id of activity. |
| `response.activity[].activity_type` | string | The type of activity. |
| `response.activity[].original_price` | string | activity's origin price |
| `response.activity[].discounted_price` | string | activity's discount price |
| `response.activity[].items` | object[] |  |
| `response.activity[].items[].item_id` | int64 | The id of item. |
| `response.activity[].items[].variation_id` | int64 | Shopee's unique identifier for a variation of an item. |
| `response.activity[].items[].quantity_purchased` | int64 | item's quantity purchase |
| `response.activity[].items[].original_price` | string | item's origin price |
| `response.activity[].refund_amount` | string | item's refund amount for bundle deal cases, only for shops whitelisted for Partial Qty RR. |
| `response.seller_proof` | object |  |
| `response.seller_proof.seller_proof_status` | string | To indicate whether the seller needs to provide evidence when the return status is RETURN_JUDING, RETURN_SELLER_DISPUTE and RETURN_ACCEPTED. Applicable values: See Data Definition- SellerProofStatus. |
| `response.seller_proof.seller_evidence_deadline` | timestamp | To indicate the deadline for submitting the evidence. |
| `response.seller_compensation` | object |  |
| `response.seller_compensation.seller_compensation_status` | string | To indicate whether the seller is eligible for raising a compensation request. See "Data Definition - SellerCompensationStatus" |
| `response.seller_compensation.seller_compensation_due_date` | timestamp | To indicate the deadline for requesting the compensation |
| `response.seller_compensation.compensation_amount` | float | To indicate the compensation amount that the agent decided |
| `response.seller_compensation.compensation_amount_list` | object |  |
| `response.seller_compensation.compensation_amount_list.compensation_type` | string | To indicate the type of return-related compensation Applicable values: See Data Definition - Compensation Type |
| `response.seller_compensation.compensation_amount_list.compensation_amount` | float |  |
| `response.negotiation` | object |  |
| `response.negotiation.negotiation_status` | string | To indicate whether the seller can negotiate with the buyer. See "Data Definition - NegotiationStatus" |
| `response.negotiation.latest_solution` | string | To indicate what is the offer solution. See "Data Definition - ReturnSolution" |
| `response.negotiation.latest_offer_amount` | float | To indicate the refund amount in the latest offer solution |
| `response.negotiation.latest_offer_creator` | string | To indicate which party made the latest offer |
| `response.negotiation.counter_limit` | int32 | To indicate the remaining counter limit |
| `response.negotiation.offer_due_date` | timestamp | To indicate offer_due_date |
| `response.logistics_status` | string | To indicate the reverse logistics status. See "Data Definition - LogisticsStatus". Note: - This is a legacy field that only reflects the reverse logistics status of Normal RR. To determine whether the RR is a Normal RR, check if return_refund_request_type = 0. - If you need the reverse logistics status for Normal RR, In-transit RR, or Return-on-the-Spot, please use the newly released field reverse_logistic_status instead. |
| `response.reverse_logistics_status` | string | To indicate the latest reverse logistic status of a return, referring to the current status of the buyer shipping the return parcel back to the validation point (seller or warehouse), including Normal RR, In-transit RR, and Return-on-the-Spot. See "Data Definition - ReverseLogisticsStatus" as status displayed for Normal RR and In-transit RR or Return-on-the-Spot are different. |
| `response.return_pickup_address` | object | To indicate the buyer's pickup address |
| `response.return_pickup_address.address` | string | To indicate receiver's address |
| `response.return_pickup_address.name` | string | To indicate receiver's name |
| `response.return_pickup_address.phone` | string | To indicate receiver's phone [Only for TW non-integrated channel] Will return "****" when the "virtual_contact_number" is available |
| `response.return_pickup_address.town` | string | To indicate receiver's town |
| `response.return_pickup_address.district` | string | To indicate receiver's district |
| `response.return_pickup_address.city` | string | To indicate receiver's city |
| `response.return_pickup_address.state` | string | To indicate receiver's state |
| `response.return_pickup_address.region` | string | To indicate receiver's region |
| `response.return_pickup_address.zipcode` | string | To indicate receiver's zip code |
| `response.virtual_contact_number` | string | [Only for TW non-integrated channel] The virtual phone number to contact the recipient. |
| `response.package_query_number` | string | [Only for TW non-integrated channel] The query number used in virtual phone number calls to contact the recipient of this return. |
| `response.return_address` | object |  |
| `response.return_address.whs_id` | string | To indicate the warehouse id where item will be returned to. Please call v2.shop.get_warehouse_detail to check the detailed warehouse information the item returned to with the field "location_id" of the v2.shop.get_warehouse_detail match to the field"whs_id"of the v2.return.get_return_detail. For fulfillment by Shopee (FBS) & multi warehouse sellers, R/R orders will be returned back to the nearest warehouse of buyer address instead of going back to only 1 default return address like a normal seller.If it's a normal seller, then the field will be response empty. |
| `response.return_refund_type` | string | To indicate whether the return is RRBOC (Return/Refund request raised before Order Complete) or RRAOC (Return/Refund request raised after Order Complete). |
| `response.return_solution` | int32 | To indicate the most updated solution of the Return/Refund request (NOTE: this is not the solution during negotiation). Applicable value: - 0: Return and Refund - 1: Refund Only |
| `response.is_seller_arrange` | boolean | To indicate whether the return_sn is using the “Seller Arrange” return method. This would only be True for TW and BR. |
| `response.is_shipping_proof_mandatory` | boolean | To indicate whether uploading shipping proof is mandatory for seller to confirm "Arrange Pickup" when is_seller_arrange = true. |
| `response.has_uploaded_shipping_proof` | boolean | To indicate whether seller has already uploaded shipping proof for this return. |
| `response.is_reverse_logistics_channel_integrated` | boolean | To indicate whether the reverse logistic channel type selected is integrated or non-integrated. |
| `response.reverse_logistics_channel_name` | string | To indicate reverse logistic carrier name. |
| `response.return_refund_request_type` | int32 | To indicate the type of return refund request, whether it is a Normal RR request, an In-transit RR request, and a Return on the Spot: 0: Normal RR (RR is raised by the buyer after delivery done / estimated delivery date) 1: In-transit RR (RR is raised by the buyer while item is still in-transit to buyer) 2: Return-on-the-Spot (RR is raised by the driver after buyer rejected parcel at delivery) For more details, see Data Definition- Return Refund Request Type. |
| `response.validation_type` | string | To indicate whether seller or warehouse will expect to receive the return parcel from buyer and validate the condition of the parcel: - seller_validation - warehouse_validation For more details, see Data Definition- ValidationType. |
| `response.is_arrived_at_warehouse` | int32 | [Only for validation_type = warehouse_validation] Indicates the parcel’s check-in status at the warehouse. This field helps sellers quickly determine whether the parcel has arrived at the warehouse or has been rejected. Applicable values: 1: Pending Inbound 2: Rejected 3: Inbound 4: Cancelled |
| `response.follow_up_action_list` | object[] | [Only for validation_type = warehouse_validation] Warehouse handling actions for each item in the parcel. |
| `response.follow_up_action_list[].item_id` | int64 | Unique identifier of the item. |
| `response.follow_up_action_list[].model_id` | int64 | Unique identifier of the model under the item. |
| `response.follow_up_action_list[].qty` | int32 | Quantity of items or models under the same current status. |
| `response.follow_up_action_list[].current_status` | int32 | Current status for the item/model within the warehouse. Applicable values: 1：Dispose 2：Return to Seller 7：Received and Putaway 8：Return to Buyer 9：Shortage Note: Since Resell is currently applicable only to Failed Delivery parcels, the following values will not be returned for now, and will be returned once Resell becomes applicable to Return Refund parcels in the future: 3：Putaway for Resell 4：Resell Outbound 5：Resell Failed 6：Resell Exit |
| `response.follow_up_action_list[].related_order_sn_list` | string[] | List of order_sn generated from the Resell process. Returned only when current_status = 4 (Resell Outbound). Note: Since Resell is currently applicable only to Failed Delivery parcels, this field will remain empty for now, and valid values will be returned once Resell becomes applicable to Return Refund parcels in the future. |
| `response.follow_up_action_list[].resell_failed_next_step` | string | Next step after a Resell failure. Returned only when current_status = 5 (Resell Failed). Note: Since Resell is currently applicable only to Failed Delivery parcels, this field will remain empty for now, and valid values will be returned once Resell becomes applicable to Return Refund parcels in the future. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
