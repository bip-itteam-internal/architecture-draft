# product.get_mart_item_mapping_by_id

- Path: `/api/v2/product/get_mart_item_mapping_by_id`
- Method: POST
- Auth: shop
- Deskripsi: Get the mapping information between a Mart item and its corresponding outlet item by item ID.
- Sumber: open.shopee.com/documents/v2/product.get_mart_item_mapping_by_id?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `mart_item_id` | int64 | ya | The item ID of the item in the Mart shop. |
| `outlet_shop_id_list` | int64[] | ya | A list of outlet shop IDs used to filter the mapping results. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.item_mapping_list` | object[] | A list of item mapping records between the Mart item and its corresponding outlet items. |
| `response.item_mapping_list[].mart_item_id` | int64 | The item ID of the item in the Mart shop. |
| `response.item_mapping_list[].outlet_item_id` | int64 | The item ID of the corresponding item in the outlet shop. |
| `response.item_mapping_list[].model_mapping` | object[] | The mapping relationship between Mart models and outlet models under the mapped items. |
| `response.item_mapping_list[].model_mapping[].mart_model_id` | int64 | The model ID of the product in the Mart shop. |
| `response.item_mapping_list[].model_mapping[].outlet_model_id` | int64 | The model ID of the corresponding product in the outlet shop. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
