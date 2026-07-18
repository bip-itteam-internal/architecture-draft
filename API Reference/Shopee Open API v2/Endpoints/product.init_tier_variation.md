# product.init_tier_variation

- Path: `/api/v2/product/init_tier_variation`
- Method: POST
- Auth: shop
- Deskripsi: This API allows you to update the tier structure of a product. Defining only color creates one tier, while color + size creates two tiers (maximum supported). Supported changes include: no tier ↔ one/two tiers, one tier ↔ two/no tier, and two tiers ↔ one/no tier. For details, see Developer Guide. Please wait at least 5 seconds after creating an item before creating variants, as processing may be delayed.
- Sumber: open.shopee.com/documents/v2/product.init_tier_variation?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id` | int64 | ya | ID of item Contoh: `1000` |
| `model` | object[] | ya | Model info list, model number at most 50 |
| `standardise_tier_variation` | object[] | tidak | There is at least one standardise_tier_variation and tier_variation. If you want to update one tier/two tier to no tier, can just pass the tier_variation and standardise_tier_variation as [], and pass the model >> tier_index as [], meanwhile pass the original_price, seller_stock, etc., to set the price and stock for the modified product with no tier structure. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking |
| `response` | object |  |
| `response.item_id` | int64 | ID of item |
| `response.tier_variation` | object[] | Variations of item |
| `response.tier_variation[].name` | string | Variation name |
| `response.tier_variation[].option_list` | object[] | Options of this variation |
| `response.tier_variation[].option_list[].image` | object | Image of this option |
| `response.tier_variation[].option_list[].image.image_url` | string | URL of image |
| `response.tier_variation[].option_list[].option` | string | Option name |
| `response.model` | object[] |  |
| `response.model[].tier_index` | object[] | Tier index of model. Index starts from 0. |
| `response.model[].model_id` | int64 | ID of model |
| `response.model[].model_sku` | string | Seller SKU of this model |
| `response.model[].price_info` | object[] |  |
| `response.model[].price_info[].original_price` | float | Original price |
| `response.model[].seller_stock` | object[] | new stock info |
| `response.model[].seller_stock[].location_id` | string | location id |
| `response.model[].seller_stock[].stock` | int32 | stock |
| `response.model[].weight` | float | The weight of this model, the unit is KG. If don't set the weight of this model, will use the weight of item by default. If set the dimension of this model, them must set the weight of this model. |
| `response.model[].dimension` | object | The dimension of this model. If don't set the dimension of this model, will use the dimension of item by default. |
| `response.model[].dimension.package_height` | int32 | The height of package for this model, the unit is CM. |
| `response.model[].dimension.package_length` | int32 | The length of package for this model, the unit is CM. |
| `response.model[].dimension.package_width` | int32 | The width of package for this model, the unit is CM. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
