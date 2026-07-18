# product.get_kit_item_limit

- Path: `/api/v2/product/get_kit_item_limit`
- Method: GET
- Auth: shop
- Deskripsi: Get the limit of Kit item.
- Sumber: open.shopee.com/documents/v2/product.get_kit_item_limit?type=1 (backend doc/api) — 2026-07-18
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
| `response.item_name_length_limit` | object |  |
| `response.item_name_length_limit.min_limit` | int64 | Item name length min limit. |
| `response.item_name_length_limit.max_limit` | int64 | Item name length max limit. |
| `response.item_image_count_limit` | object |  |
| `response.item_image_count_limit.min_limit` | int64 | Item image count min limit. |
| `response.item_image_count_limit.max_limit` | int64 | Item image count max limit. |
| `response.description_limit` | object |  |
| `response.description_limit.description_length_min` | int64 | Item description length min limit. |
| `response.description_limit.description_length_max` | int64 | length max limit for item extended description text part. |
| `response.description_limit.description_text_length_min` | int64 | length min limit for item extended description text part, when one of the minimum limits for image and text is reached, the item can be added or updated successfully. |
| `response.description_limit.description_text_length_max` | int64 | length max limit for item extended description text part |
| `response.description_limit.description_image_num_min` | int64 | length min limit for item extended description image num, when one of the minimum limits for image and text is reached, the item can be added or updated successfully. |
| `response.description_limit.description_image_num_max` | int64 | length max limit for item extended description image num. |
| `response.description_limit.description_image_width_min` | int64 | length min limit for item extended description image width. |
| `response.description_limit.description_image_height_min` | int64 | length min limit for item extended description image hight. |
| `response.description_limit.description_image_aspect_ratio_min` | float | length min limit for item extended description image aspect ( aspect_ratio= image width / image hight ). |
| `response.description_limit.description_image_aspect_ratio_max` | float | length max limit for item extended description image aspect ( aspect_ratio= image width / image hight ). |
| `response.tier_variation_name_length_limit` | object |  |
| `response.tier_variation_name_length_limit.min_limit` | int32 | Item tier variation name length min limit. |
| `response.tier_variation_name_length_limit.max_limit` | int32 | Item tier variation name length max limit. |
| `response.tier_variation_option_length_limit` | object |  |
| `response.tier_variation_option_length_limit.min_limit` | int32 | Item tier variation option length min limit. |
| `response.tier_variation_option_length_limit.max_limit` | int32 | Item tier variation option length max limit. |
| `response.weight_limit` | object |  |
| `response.weight_limit.weight_mandatory` | boolean | Whether weight is mandatory or not for the category. |
| `response.dimension_limit` | object |  |
| `response.dimension_limit.dimension_mandatory` | boolean | Whether dimension is mandatory or not for the category. |
| `response.dts_limit` | object |  |
| `response.dts_limit.non_pre_order_days_to_ship` | int32 | Days to ship for non pre-order products. |
| `response.dts_limit.support_pre_order` | boolean | Whether support pre_order for the category. |
| `response.dts_limit.days_to_ship_limit` | object | Days to ship for pre-order products. |
| `response.dts_limit.days_to_ship_limit.min_limit` | int32 | Min limit of days to ship for pre-order products. |
| `response.dts_limit.days_to_ship_limit.max_limit` | int32 | Max limit of days to ship for pre-order products. |
| `response.component_count_limit_of_single_model` | object |  |
| `response.component_count_limit_of_single_model.min_limit` | int32 | Item count min limit that each kit variations support. |
| `response.component_count_limit_of_single_model.max_limit` | int32 | Item count max limit that each kit variations support. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
