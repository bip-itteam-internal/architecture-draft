# product.get_kit_item_info

- Path: `/api/v2/product/get_kit_item_info`
- Method: GET
- Auth: shop
- Deskripsi: Get the kit basic information and kit components.
- Sumber: open.shopee.com/documents/v2/product.get_kit_item_info?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id` | int64 | ya | ID of kit item. Contoh: `28001430` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.product_info` | object |  |
| `response.product_info.item_id` | int64 | ID of this kit item. |
| `response.product_info.item_name` | string | The name of this kit item. |
| `response.product_info.category_id` | int64[] | The category of this kit item, sync from the category of the main component of this kit item. |
| `response.product_info.item_status` | string | Enumerated type that defines the current status of the item. Applicable values: NORMAL, BANNED, UNLIST, SELLER_DELETE, SHOPEE_DELETE, REVIEWING. |
| `response.product_info.item_sku` | string | An item SKU (stock keeping unit) is an identifier defined by a seller, sometimes called parent SKU. Item SKU can be assigned to an item in Shopee Listings. |
| `response.product_info.images` | object | Item images with 1:1 ratio. |
| `response.product_info.images.image_id_list` | string[] | List of image id. |
| `response.product_info.images.image_url_list` | string[] | List of image url. |
| `response.product_info.images.image_ratio` | string | 1:1 |
| `response.product_info.long_images` | object | Item images with 3:4 ratio. |
| `response.product_info.long_images.image_id_list` | string[] | List of image id. |
| `response.product_info.long_images.image_url_list` | string[] | List of image url. |
| `response.product_info.long_images.image_ratio` | string | 3:4 |
| `response.product_info.description_info` | object | Rich text description field. Only whitelist sellers can use it. |
| `response.product_info.description_info.extended_description` | object | If description_type is extended , Description information will be returned through this field. |
| `response.product_info.description_info.extended_description.field_list` | object[] | Field of extended description. |
| `response.product_info.description_info.extended_description.field_list[].field_type` | string | Type of extended description field. See Data Definition- description_field_type (text , image). |
| `response.product_info.description_info.extended_description.field_list[].text` | string | If field_type is text, text information will be returned through this field. |
| `response.product_info.description_info.extended_description.field_list[].image_info` | object | If field_type is image, image will be returned through this field. |
| `response.product_info.description_info.extended_description.field_list[].image_info.image_id` | string | Image id. |
| `response.product_info.description_info.extended_description.field_list[].image_info.image_url` | string | Image url. |
| `response.product_info.description` | string | If description_type is normal, description information will be returned through this field, else description will be empty. |
| `response.product_info.description_type` | string | Type of description : values: See Data Definition- description_type (normal , extended). |
| `response.product_info.video_list` | object | Info of video list. |
| `response.product_info.video_list.video_url` | string | Url of video. |
| `response.product_info.video_list.thumbnail_url` | string | Thumbnail of video. |
| `response.product_info.video_list.duration` | int32 | Duration of video. |
| `response.product_info.attributes` | object[] | The attributes of this kit item, sync from the attributes of the main component of this kit item. |
| `response.product_info.attributes[].attribute_id` | int64 | The Identify of each attribute. |
| `response.product_info.attributes[].original_attribute_name` | string | The name of each attribute. |
| `response.product_info.attributes[].attribute_value_list` | object[] |  |
| `response.product_info.attributes[].attribute_value_list[].value_id` | int64 | Unique identifier for value of this item attribute. |
| `response.product_info.attributes[].attribute_value_list[].original_value_name` | string | Value name of this item attribute. |
| `response.product_info.attributes[].attribute_value_list[].value_unit` | string | Value unit of this item attribute. |
| `response.product_info.weight` | string | The weight of this kit item, the unit is KG. |
| `response.product_info.dimension` | object | The dimension of this kit item. |
| `response.product_info.dimension.package_length` | int32 | The length of package for this item, the unit is CM. |
| `response.product_info.dimension.package_width` | int32 | The width of package for this item, the unit is CM. |
| `response.product_info.dimension.package_height` | int32 | The height of package for this item, the unit is CM. |
| `response.product_info.brand_info` | object | The brand of this kit item, sync from the brand of the main component of this kit item. |
| `response.product_info.brand_info.brand_id` | int64 | Id of brand. |
| `response.product_info.brand_info.original_brand_name` | string | Original name of brand. |
| `response.product_info.model_list` | object[] | Model info list, model number at most 9. |
| `response.product_info.model_list[].model_id` | int64 | ID of this kit model. |
| `response.product_info.model_list[].model_sku` | int64 | Seller SKU of this kit model. |
| `response.product_info.model_list[].original_price` | float | Original price of this kit model. |
| `response.product_info.model_list[].tier_index` | int32[] | Tier index of this kit model. |
| `response.product_info.model_list[].component_list` | object[] |  |
| `response.product_info.model_list[].component_list[].component_item_id` | int64 | ID of the item that composes this kit model. |
| `response.product_info.model_list[].component_list[].component_item_name` | string | Name of the item that composes this kit model. |
| `response.product_info.model_list[].component_list[].component_model_id` | int64 | ID of the model that composes this kit model. |
| `response.product_info.model_list[].component_list[].component_model_name` | string | Name of the model that composes this kit model. |
| `response.product_info.model_list[].component_list[].quantity` | int32 | The amount of the item/model that composes this kit model. |
| `response.product_info.model_list[].component_list[].main_component` | boolean | Whether this item/model is the main component for this kit. |
| `response.product_info.model_list[].component_list[].component_item_or_model_image` | string |  |
| `response.product_info.model_list[].component_list[].component_item_or_model_sku` | string |  |
| `response.product_info.pre_order_info` | object |  |
| `response.product_info.pre_order_info.is_pre_order` | boolean |  |
| `response.product_info.pre_order_info.days_to_ship` | int32 |  |
| `response.product_info.tier_variation_list` | object[] | Variation config of item. |
| `response.product_info.tier_variation_list[].name` | string | Variation name. |
| `response.product_info.tier_variation_list[].option_list` | object[] | Option list. |
| `response.product_info.tier_variation_list[].option_list[].option` | string | Option name. |
| `response.product_info.tier_variation_list[].option_list[].image` | object[] |  |
| `response.product_info.tier_variation_list[].option_list[].image[].image_id` | string | Id of image. |
| `response.product_info.tier_variation_list[].option_list[].image[].image_url` | string | Url of image. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
