# product.add_model

- Path: `/api/v2/product/add_model`
- Method: POST
- Auth: shop
- Deskripsi: Add model. More detail please check: https://open.shopee.com/developer-guide/219
- Sumber: open.shopee.com/documents/v2/product.add_model?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id` | int64 | ya | ID of item Contoh: `1000` |
| `model_list` | object[] | ya | Model list |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string |  |
| `response` | object |  |
| `response.model` | object[] |  |
| `response.model[].tier_index` | int32[] | model tier index |
| `response.model[].model_id` | int64 | ID of model |
| `response.model[].model_sku` | string | Seller SKU of this model, model_sku length information needs to be no more than 100 characters. |
| `response.model[].price_info` | object[] |  |
| `response.model[].price_info[].original_price` | float | Original Price. For CO local VAT responsible seller： Please remember the price you set in here must be VAT inclusive. If you have any doubts on how to calculate VAT for your product please refer to the Seller Education Hub（https://seller.shopee.com.co/edu/article/13565） |
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
