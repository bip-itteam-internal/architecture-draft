# product.get_item_limit

- Path: `/api/v2/product/get_item_limit`
- Method: GET
- Auth: shop
- Deskripsi: Get item upload control.
- Sumber: open.shopee.com/documents/v2/product.get_item_limit?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `category_id` | int64 | tidak | Shopee's unique identifier for a category. Contoh: `400055` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.price_limit` | object |  |
| `response.price_limit.min_limit` | float | Item price max limit. |
| `response.price_limit.max_limit` | float | Item price min limit. |
| `response.wholesale_price_threshold_percentage` | object |  |
| `response.wholesale_price_threshold_percentage.min_limit` | int64 | Item wholesale price percentage of original price min limit. |
| `response.wholesale_price_threshold_percentage.max_limit` | int64 | Item wholesale price percentage of original price min limit. |
| `response.stock_limit` | object |  |
| `response.stock_limit.min_limit` | int64 | Item stock min limit. |
| `response.stock_limit.max_limit` | int64 | Item stock max limit. |
| `response.item_name_length_limit` | object |  |
| `response.item_name_length_limit.min_limit` | int64 | Item name length min limit. |
| `response.item_name_length_limit.max_limit` | int64 | Item name length max limit. |
| `response.item_image_count_limit` | object |  |
| `response.item_image_count_limit.min_limit` | int64 | Item image count min limit. |
| `response.item_image_count_limit.max_limit` | int64 | Item image count max limit. |
| `response.item_description_length_limit` | object |  |
| `response.item_description_length_limit.min_limit` | int64 | Item description length min limit. |
| `response.item_description_length_limit.max_limit` | int64 | Item description length max limit. |
| `response.tier_variation_name_length_limit` | object |  |
| `response.tier_variation_name_length_limit.min_limit` | int64 | Item tier variation name length min limit. |
| `response.tier_variation_name_length_limit.max_limit` | int64 | Item tier variation name length max limit. |
| `response.tier_variation_option_length_limit` | object |  |
| `response.tier_variation_option_length_limit.min_limit` | int64 | Item tier variation option length min limit. |
| `response.tier_variation_option_length_limit.max_limit` | int64 | Item tier variation option length max limit. |
| `response.item_count_limit` | object |  |
| `response.item_count_limit.max_limit` | int64 | Item count max limit. |
| `response.extended_description_limit` | object |  |
| `response.extended_description_limit.description_text_length_min` | int | length min limit for item extended description text part |
| `response.extended_description_limit.description_text_length_max` | int | length max limit for item extended description text part |
| `response.extended_description_limit.description_image_num_min` | int | length min limit for item extended description image num |
| `response.extended_description_limit.description_image_num_max` | int | length max limit for item extended description image num |
| `response.extended_description_limit.description_image_width_min` | int | length min limit for item extended description image width |
| `response.extended_description_limit.description_image_height_min` | int | length min limit for item extended description image hight |
| `response.extended_description_limit.description_image_aspect_ratio_min` | float | length min limit for item extended description image aspect (image width / image hight ) |
| `response.extended_description_limit.description_image_aspect_ratio_max` | float | length max limit for item extended description image aspect (image width / image hight ) |
| `response.dts_limit` | object |  |
| `response.dts_limit.days_to_ship_limit` | object | Pre order limits for the category |
| `response.dts_limit.days_to_ship_limit.min_limit` | int |  |
| `response.dts_limit.days_to_ship_limit.max_limit` | int |  |
| `response.dts_limit.non_pre_order_days_to_ship` | int |  |
| `response.weight_limit` | object |  |
| `response.weight_limit.weight_mandatory` | boolean | weight is mandatory or not |
| `response.dimension_limit` | object |  |
| `response.dimension_limit.dimension_mandatory` | boolean | dimension is mandatory or not for the category |
| `response.size_chart_limit` | object |  |
| `response.size_chart_limit.size_chart_mandatory` | boolean |  |
| `response.size_chart_limit.support_image_size_chart` | boolean |  |
| `response.size_chart_limit.support_template_size_chart` | boolean |  |
| `gtin_limit` | object |  |
| `gtin_limit.gtin_validation_rule` | string | Indicate gtin_code validation logic in v2.product.add_item v2.product.update_item v2.product.init_tier_variation v2.product.add_model v2.product.update_model - Mandatory : This field is required and must contain a correctly formatted GTiN number. - Flexible : This field is required and must contain either a correctly formatted GTlN number or "00" todeclare that the item/model has no valid GTlN. - Optional : This field is optional and can contain a correctly formatted GTiN number, "00" or be omittedentirely. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
