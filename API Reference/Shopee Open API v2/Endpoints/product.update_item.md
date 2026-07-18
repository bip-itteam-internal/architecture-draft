# product.update_item

- Path: `/api/v2/product/update_item`
- Method: POST
- Auth: shop
- Deskripsi: Update item.
- Sumber: open.shopee.com/documents/v2/product.update_item?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `description` | string | tidak | Description of item. Contoh: `Hello product product WlQPdMV4SlVoG7QD1v0fEecNoCVEBNx6` |
| `weight` | float | tidak | The weight of this item, the unit is KG. Updating the weight of this item will overwrite the weight of all models under this item. Contoh: `0.9` |
| `pre_order` | object | tidak | Pre Order setting. |
| `item_name` | string | tidak | Item name. Contoh: `Hello Pgkk50jdNgEnlWvX` |
| `attribute_list` | object[] | tidak | Item attributes. |
| `image` | object | tidak | Images of item. |
| `item_sku` | string | tidak | SKU tag for item. Contoh: `abc` |
| `item_status` | string | tidak | Item status, could be UNLIST or NORMAL. Contoh: `UNLIST` |
| `wholesale` | object[] | tidak | Wholesale setting. If you want to delete it, please pass it with blank. |
| `item_id` | int64 | ya | ID of item. Contoh: `28001430` |
| `category_id` | int32 | tidak | ID of category. Contoh: `34106` |
| `dimension` | object | tidak | The dimension of this item. Updating the dimension of this item will overwrite the dimension of all models under this item. |
| `condition` | string | tidak | Condition of item, could be NEW or USED. Contoh: `USED` |
| `video_upload_id` | string[] | tidak | Video upload ID returned from video uploading API. If you want to delete it, please pass it with blank. Contoh: `["sg_f4bde9bc-ff3c-485e-a6dd-3161dab4b942_000000"]` |
| `brand` | object | tidak |  |
| `item_dangerous` | int32 | tidak | This field is only applicable for local sellers in Indonesia and Malaysia. Use this field to identify whether a product is a dangerous product. 0 for non-dangerous product and 1 for dangerous product. For more information, please visit the market's respective Seller Education Hub. Contoh: `0` |
| `tax_info` | object | tidak | Tax information |
| `complaint_policy` | object | tidak | Complaint Policy for item. Only required for local PL sellers, ignored otherwise. |
| `description_info` | object | tidak | New description field. Only whitelist sellers can use it. If you use the field, please upload the description_type=extended otherwise api will return error. If you don't use this field, you don't need to upload the description_type or upload description_type=normal |
| `description_type` | string | tidak | Values: See Data Definition- description_type (normal , extended). If you want to use extended_description or change description type ,this field must be inputed |
| `gtin_code` | string | tidak | - GTIN is an identifier for trade items, developed by the international organization GS1. - They have 8 to 14 digits. The most common are UPC, EAN, JAN and ISBN. - GTIN will help boost positioning in online marketing channels like Google and Facebook. - That incorporation with GTIN will also aid in Search and Recommendation in Shopee itself allowing buyers to have higher likelihood of finding one's listing. Note: If you want to set “Item without GTIN”, please pass the gtin_code as "00". The validation rule is based on the value return in gtin_validation_rule" field in v2.product.get_item_limit API - Mandatory: This field is required and must contain a correctly formatted GTiN number. - Flexible: This field is required and must contain either a correctly formatted GTlN number or "00" to declare that the item/model has no valid GTlN. - Optional: This field is optional and can contain a correctly formatted GTiN number, "00" or be omitted entirely. |
| `ds_cat_rcmd_id` | string | tidak | category recommendation service id |
| `promotion_images` | object | tidak | Promotion Image Currently only allow one promoton image You could set promotion image only if the product images' ratio is 3:4 |
| `compatibility_info` | object | tidak |  |
| `scheduled_publish_time` | timestamp | tidak | Scheduled publish time of this item: 1) Can only set scheduled_publish_time for item with UNLIST status 2) Can only set the time from current time +1hour to current time +90days, and the time is only allowed to be accurate to the minute Contoh: `1733590920` |
| `authorised_brand_id` | int64 | tidak | ID of authorised reseller brand. |
| `size_chart_info` | object | tidak |  |
| `certification_info` | object | tidak | For PH product certification input Required for some category and attribute option |
| `purchase_limit_info` | object | tidak | purchase limit info |
| `medicine_id` | int64 | tidak | [Only for ID local sellers] as a unique identifier for each standardized medicine, the medicine id can only be obtained offline |

## Response

| field | tipe | keterangan |
|---|---|---|
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.description` | string | Item description. |
| `response.weight` | float | The weight of this item, the unit is KG. |
| `response.pre_order` | object |  |
| `response.pre_order.days_to_ship` | int32 | The time it takes to ship the item. |
| `response.pre_order.is_pre_order` | boolean | Whether item is pre order. |
| `response.item_name` | string | Item name. |
| `response.item_status` | string | Item status. |
| `response.images` | object | Item images. |
| `response.images.image_id_list` | string[] | ID list of item image. |
| `response.images.image_url_list` | string[] | URL list of item image |
| `response.logistic_info` | object[] |  |
| `response.logistic_info[].estimated_shipping_fee` | float | Estimated shipping fee. |
| `response.logistic_info[].logistic_name` | string | Name of logistics channel. |
| `response.logistic_info[].enabled` | boolean | Whether this channel is enabled. |
| `response.logistic_info[].logistic_id` | int32 | ID of this channel. |
| `response.logistic_info[].is_free` | boolean | Whether cover shipping fee for buyer. |
| `response.item_id` | int64 | ID of item. |
| `response.category_id` | int32 | ID of item category. |
| `response.dimension` | object | The dimension of this item. |
| `response.dimension.package_width` | int32 | The width of package for this item, the unit is CM. |
| `response.dimension.package_length` | int32 | The length of package for this item, the unit is CM. |
| `response.dimension.package_height` | int32 | The height of package for this item, the unit is CM. |
| `response.condition` | string | Item condition, could be USED or NEW. |
| `response.brand` | object |  |
| `response.brand.brand_id` | int32 | Id of brand. |
| `response.brand.original_brand_name` | string | Original name of brand. |
| `response.item_dangerous` | int32 | This field is only applicable for local sellers in Indonesia and Malaysia. Use this field to identify whether a product is a dangerous product. 0 for non-dangerous product and 1 for dangerous product. For more information, please visit the market's respective Seller Education Hub. |
| `response.complaint_policy` | object | Complaint policy |
| `response.complaint_policy.warranty_time` | string | Value should be in one of ONE_YEAR TWO_YEARS OVER_TWO_YEARS. |
| `response.complaint_policy.exclude_entrepreneur_warranty` | boolean | If True means "I exclude warranty complaints for entrepreneur" |
| `response.complaint_policy.additional_information` | string | Additional information for complaint policy |
| `response.description_info` | object | New description field. Only whitelist sellers can use it. If you use the field, please upload the description_type=extended otherwise api will return error. If you don't use this field, you don't need to upload the description_type or upload description_type=normal |
| `response.description_info.extended_description` | object | If description_type is extended , description information should be set by this field. |
| `response.description_info.extended_description.field_list` | object[] | Field of extended description. |
| `response.description_info.extended_description.field_list[].field_type` | string | Type of extended description field ：values: See Data Definition- description_field_type (text , image). |
| `response.description_info.extended_description.field_list[].text` | string | If field_type is text， text information will be set by this field. |
| `response.description_info.extended_description.field_list[].image_info` | object | If field_type is image，image url will be set by this field. |
| `response.description_info.extended_description.field_list[].image_info.image_id` | string | Image id. |
| `response.description_type` | string | Values: See Data Definition- description_type (normal , extended). |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
