# product.get_direct_shop_recommended_price

- Path: `/api/v2/product/get_direct_shop_recommended_price`
- Method: GET
- Auth: shop
- Deskripsi: get recommend price for direct shop.
- Sumber: open.shopee.com/documents/v2/product.get_direct_shop_recommended_price?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `main_item_id` | int64 | ya | Contoh: `843997552` |
| `direct_shop_regions` | string[] | ya | Direct shop regions. Contoh: `["SG"]` |
| `category_id` | int64 | tidak | Main_item's category. Contoh: `1234` |
| `model_list` | object[] | tidak | Main model model info. |
| `enabled_channel_id_list` | int64[] | tidak | direct shop enabled channel Contoh: `28016` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking |
| `response` | object |  |
| `response.direct_item_price` | object[] |  |
| `response.direct_item_price[].shop_id` | int64 | Id of direct shop. |
| `response.direct_item_price[].region` | string | Region of direct shop. |
| `response.direct_item_price[].hidden_price` | float |  |
| `response.direct_item_price[].item_model_price_list` | object[] |  |
| `response.direct_item_price[].item_model_price_list[].model_id` | int64 | Id of main model. |
| `response.direct_item_price[].item_model_price_list[].tier_index` | int64[] | Tier index of main model. Index starts from 0. |
| `response.direct_item_price[].item_model_price_list[].price` | float |  |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
