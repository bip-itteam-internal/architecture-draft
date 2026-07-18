# product.get_model_list

- Path: `/api/v2/product/get_model_list`
- Method: GET
- Auth: shop
- Deskripsi: Get model list of an item.
- Sumber: open.shopee.com/documents/v2/product.get_model_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id` | int64 | ya | The ID of the item Contoh: `178312` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.tier_variation` | object[] | Variation config of item. |
| `response.tier_variation[].option_list` | object[] | Option list. |
| `response.tier_variation[].option_list[].option` | string | Option name. |
| `response.tier_variation[].option_list[].image` | object |  |
| `response.tier_variation[].option_list[].image.image_id` | string | Id of image |
| `response.tier_variation[].option_list[].image.image_url` | string | Url of image. |
| `response.tier_variation[].name` | string | Variation name. |
| `response.model` | object[] | Model list. |
| `response.model[].price_info` | object[] | Price info. For SG/MY/BR/MX/PL/ES/AR seller: Sellers can set the price with two decimal place, other regions can only set the price as an integer. |
| `response.model[].price_info[].currency` | string | Currency for the item price. |
| `response.model[].price_info[].current_price` | float | Current price of item. |
| `response.model[].price_info[].original_price` | float | Original price of item. |
| `response.model[].price_info[].inflated_price_of_original_price` | float | Original price of item after tax. |
| `response.model[].price_info[].inflated_price_of_current_price` | float | Current price of item after tax. |
| `response.model[].price_info[].sip_item_price` | float | SIP item price. If item is from SIP primary shop, this field will be returned. |
| `response.model[].price_info[].sip_item_price_source` | string | SIP item price source, could be manual or auto.If item is from SIP primary shop, this field will be returned. |
| `response.model[].price_info[].sip_item_price_currency` | string | The currency of sip_item_price.If item is from SIP primary shop, this field will be returned. |
| `response.model[].price_info[].local_price` | float | The original price multiplied by the local adjustment rate equals the local price. The local price is denominated in the local currency and is rounded to two decimal places. <path></path> |
| `response.model[].price_info[].local_promotion_price` | float | During the promotion period, the CB price is multiplied by the local adjustment rate. Once the promotion starts, the price remains unchanged. During the promotion, the local_promotion_price= current_price, which is denominated in the local currency and retained to two decimal places. <path></path> |
| `response.model[].model_id` | int64 | Model ID. |
| `response.model[].tier_index` | int32[] | Tier index of this model. |
| `response.model[].promotion_id` | int64 | Current promotion ID of this model. |
| `response.model[].has_promotion` | boolean | Indicates whether the model is currently under any ongoing promotion. |
| `response.model[].model_sku` | string | SKU of this model. the length should be under 100. |
| `response.model[].model_status` | string | The model status. Should be MODEL_NORMAL or MODEL_UNAVAILABLE. MODEL_NORMAL models can be sold on the buyer's side, and MODEL_UNAVAILABLE models cannot be sold on the buyer's side. |
| `response.model[].pre_order` | object | (Only whitelisted users can use) |
| `response.model[].pre_order.is_pre_order` | boolean | Pre-order. |
| `response.model[].pre_order.days_to_ship` | int32 | The days to ship. |
| `response.model[].stock_info_v2` | object | new stock info. Please check this FAQ for more detail: https://open.shopee.com/faq?top=162&sub=166&page=1&faq=230 ("https://open.shopee.com/faq?top=162&sub=166&page=1&faq=230") |
| `response.model[].stock_info_v2.summary_info` | object | stock summary Info |
| `response.model[].stock_info_v2.summary_info.total_reserved_stock` | int32 | Stock reserved for promotion. Note: For SIP P Item, will return the total reserved stock for P Item and all A Items under the P Item. |
| `response.model[].stock_info_v2.summary_info.total_available_stock` | int32 | Stock can be sold currently |
| `response.model[].stock_info_v2.seller_stock` | object[] | Seller-managed stock |
| `response.model[].stock_info_v2.seller_stock[].location_id` | string | location id |
| `response.model[].stock_info_v2.seller_stock[].stock` | int32 | stock in the current warehouse |
| `response.model[].stock_info_v2.seller_stock[].if_saleable` | boolean | To return if the stock of the location id is saleable |
| `response.model[].stock_info_v2.shopee_stock` | object[] | Shopee warehouse stock |
| `response.model[].stock_info_v2.shopee_stock[].location_id` | string | location id |
| `response.model[].stock_info_v2.shopee_stock[].stock` | string | stock |
| `response.model[].stock_info_v2.advance_stock` | object | Only for PH/VN/ID/MY local selected shops. |
| `response.model[].stock_info_v2.advance_stock.sellable_advance_stock` | int32 | Refers to Advance Fulfillment stock that Seller has shipped out and is available to be used to fulfill an order. |
| `response.model[].stock_info_v2.advance_stock.in_transit_advance_stock` | int32 | Refers to Advance Fulfillment stock that seller has shipped out and is still in transit and unavailable to be used to fulfill an order. |
| `response.model[].gtin_code` | string | (Only TW seller and BR local seller available) gtin code. |
| `response.model[].weight` | string | The weight of this model, the unit is KG. If don't set the weight of this model, will use the weight of item by default. |
| `response.model[].dimension` | object | The dimension of this model. If don't set the dimension of this model, will use the dimension of item by default. |
| `response.model[].dimension.package_height` | int32 | The height of package for this model, the unit is CM. |
| `response.model[].dimension.package_length` | int32 | The length of package for this model, the unit is CM. |
| `response.model[].dimension.package_width` | int32 | The width of package for this model, the unit is CM. |
| `response.model[].is_fulfillment_by_shopee` | boolean | whether model is fulfillment by shopee |
| `response.standardise_tier_variation` | object[] | Standardise Variation config of item. |
| `response.standardise_tier_variation[].variation_id` | int64 | Standardise Variation ID |
| `response.standardise_tier_variation[].variation_name` | string | Standardise Variation Name |
| `response.standardise_tier_variation[].variation_group_id` | int64 | Standardise Variation Group ID |
| `response.standardise_tier_variation[].variation_option_list` | object[] | Standardise Variation Option List |
| `response.standardise_tier_variation[].variation_option_list[].variation_option_id` | int64 | Standardise Option ID |
| `response.standardise_tier_variation[].variation_option_list[].variation_option_name` | string | Standardise Option Name |
| `response.standardise_tier_variation[].variation_option_list[].image_id` | string | ID of image |
| `response.standardise_tier_variation[].variation_option_list[].image_url` | string | URL of image |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
