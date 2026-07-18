# product.add_item

- Path: `/api/v2/product/add_item`
- Method: POST
- Auth: shop
- Deskripsi: Add a new item.
- Sumber: open.shopee.com/documents/v2/product.add_item?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `original_price` | float | ya | Item price Contoh: `123.3` |
| `description` | string | ya | if description_type is normal , Description information should be set by this field. Contoh: `item description test` |
| `weight` | float | ya | The weight of this item, the unit is KG. Contoh: `1.1` |
| `item_name` | string | ya | Item name Contoh: `Item Name Example` |
| `item_status` | string | tidak | Item status, could be UNLIST or NORMAL Contoh: `UNLIST` |
| `dimension` | object | tidak | The dimension of this item. |
| `logistic_info` | object[] | ya | Logistic channel setting |
| `attribute_list` | object[] | tidak | This field is optional(expect Indonesia) depending on the specific attribute under different categories. Should call shopee.item.GetAttributes to get attribute first. Must contain all all mandatory attribute. |
| `category_id` | int32 | ya | ID of category Contoh: `14695` |
| `image` | object | ya | Item images |
| `pre_order` | object | tidak | Pre order setting |
| `item_sku` | string | tidak | SKU tag of item |
| `condition` | string | tidak | Condition of item, could be USED or NEW Contoh: `NEW` |
| `wholesale` | object[] | tidak | Wholesale setting |
| `video_upload_id` | string[] | tidak | Video upload ID returned from video uploading API. Only accept one video_upload_id. Contoh: `["sg_f4bde9bc-ff3c-485e-a6dd-3161dab4b942_000000"]` |
| `brand` | object | tidak |  |
| `item_dangerous` | int32 | tidak | This field is only applicable for local sellers in Indonesia and Malaysia. Use this field to identify whether a product is a dangerous product. 0 for non-dangerous product and 1 for dangerous product. For more information, please visit the market's respective Seller Education Hub. Contoh: `0` |
| `tax_info` | object | tidak | Tax information |
| `complaint_policy` | object | tidak | Complaint Policy for item. Only required for local PL sellers, ignored otherwise. |
| `description_info` | object | tidak | New description field. Only whitelist sellers can use it. If you use the field, please upload the description_type=extended otherwise api will return error. If you don't use this field, you don't need to upload the description_type or upload description_type=normal |
| `description_type` | string | tidak | Values: See Data Definition- description_type (normal , extended). If you want to use extended_description, this field must be inputed |
| `seller_stock` | object[] | tidak | seller stock（Please notice that stock(including Seller Stock and Shopee Stock) should be larger than or equal to real-time reserved stock） |
| `gtin_code` | string | tidak | - GTIN is an identifier for trade items, developed by the international organization GS1. - They have 8 to 14 digits. The most common are UPC, EAN, JAN and ISBN. - GTIN will help boost positioning in online marketing channels like Google and Facebook. - That incorporation with GTIN will also aid in Search and Recommendation in Shopee itself allowing buyers to have higher likelihood of finding one's listing. Note: If you want to set “Item without GTIN”, please pass the gtin_code as "00". The validation rule is based on the value return in gtin_validation_rule" field in v2.product.get_item_limit API - Mandatory : This field is required and must contain a correctly formatted GTiN number. - Flexible : This field is required and must contain either a correctly formatted GTlN number or "00" to declare that the item/model has no valid GTlN. - Optional: This field is optional and can contain a correctly formatted GTiN number, "00" or be omitted entirely. |
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
| `request_id` | string | The identifier for an API request for error tracking |
| `response` | object |  |
| `response.description` | string | Description of item |
| `response.weight` | float | The weight of this item, the unit is KG. |
| `response.pre_order` | object | Pre order setting |
| `response.pre_order.days_to_ship` | int32 | The guaranteed days to ship orders. |
| `response.pre_order.is_pre_order` | boolean | Whether this item is pre order |
| `response.item_name` | string | Item name |
| `response.images` | object | Item images |
| `response.images.image_id_list` | string[] | ID of image |
| `response.images.image_url_list` | string[] | Display URL of image |
| `response.item_status` | string | Item status |
| `response.price_info` | object | Item price info |
| `response.price_info.current_price` | float | Current price of item |
| `response.price_info.original_price` | float | Original price of item |
| `response.logistic_info` | object[] | Logistic setting |
| `response.logistic_info[].size_id` | int32 | Size ID |
| `response.logistic_info[].shipping_fee` | float | Shipping fee |
| `response.logistic_info[].enabled` | boolean | Whether this channel is enabled for this item |
| `response.logistic_info[].logistic_id` | int32 | Logistic channel ID |
| `response.logistic_info[].is_free` | boolean | Whether cover shipping fee for buyer |
| `response.item_id` | int64 | Item ID |
| `response.attribute` | object[] | Item attributes |
| `response.attribute[].attribute_id` | int32 | Attribute ID |
| `response.attribute[].attribute_value_list` | object[] |  |
| `response.attribute[].attribute_value_list[].original_value_name` | string | Value name |
| `response.attribute[].attribute_value_list[].value_id` | int32 | Value ID |
| `response.attribute[].attribute_value_list[].value_unit` | string | Unit of attribute value |
| `response.category_id` | int32 | Category ID |
| `response.dimension` | object | The dimension of this item. |
| `response.dimension.package_width` | int32 | The width of package for this item, the unit is CM. |
| `response.dimension.package_length` | int32 | The length of package for this item, the unit is CM. |
| `response.dimension.package_height` | int32 | The height of package for this item, the unit is CM. |
| `response.condition` | string | Item condition, could be NEW or USED |
| `response.video_info` | object[] | Item video |
| `response.video_info[].video_url` | string | Video playback url |
| `response.video_info[].thumbnail_url` | string | Video preview image url |
| `response.video_info[].duration` | int32 | Video duration |
| `response.wholesale` | object[] | Wholesale setting |
| `response.wholesale[].min_count` | int32 | Minimum count of this tier |
| `response.wholesale[].max_count` | int32 | Maximum count of this tier |
| `response.wholesale[].unit_price` | float | Unit price of this tier |
| `response.brand` | object |  |
| `response.brand.brand_id` | int32 | Id of brand. |
| `response.brand.original_brand_name` | string | Original name of brand. |
| `response.item_dangerous` | int32 | This field is only applicable for local sellers in Indonesia and Malaysia. Use this field to identify whether a product is a dangerous product. 0 for non-dangerous product and 1 for dangerous product. For more information, please visit the market's respective Seller Education Hub. |
| `response.description_info` | object | New description field. Only whitelist sellers can use it. If item with extended_description this field will return, otherwise do not return. |
| `response.description_info.extended_description` | object | If description_type is extended , description information should be set by this field. |
| `response.description_info.extended_description.field_list` | object[] | Field of extended description. |
| `response.description_info.extended_description.field_list[].field_type` | string | Type of extended description field ：values: See Data Definition- description_field_type (text , image). |
| `response.description_info.extended_description.field_list[].text` | string | If field_type is text, text information will be set by this field. |
| `response.description_info.extended_description.field_list[].image_info` | object | If field_type is image, image url will be set by this field. |
| `response.description_info.extended_description.field_list[].image_info.image_id` | string | Image id. |
| `response.description_type` | string | Values: See Data Definition- description_type (normal , extended). |
| `response.complaint_policy` | object | Complaint Policy for item. Only returned for local PL sellers. |
| `response.complaint_policy.warranty_time` | string | Time for a warranty claim. Could be ONE_YEAR, TWO_YEARS, OVER_TWO_YEARS. |
| `response.complaint_policy.exclude_entrepreneur_warranty` | boolean | If True means "I exclude warranty complaints for entrepreneur" |
| `response.complaint_policy.complaint_address_id` | int64 | The identity of complaint address. |
| `response.complaint_policy.additional_information` | string | Additional information for complaint policy. |
| `response.seller_stock` | object[] | seller stock |
| `response.seller_stock[].location_id` | string | location id |
| `response.seller_stock[].stock` | int32 | stock |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
