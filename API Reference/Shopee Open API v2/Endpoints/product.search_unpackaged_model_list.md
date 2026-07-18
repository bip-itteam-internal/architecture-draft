# product.search_unpackaged_model_list

- Path: `/api/v2/product/search_unpackaged_model_list`
- Method: POST
- Auth: shop
- Deskripsi: Use this API to retrieve Unpackaged SKU ID information for items that toggle on logistics channel 30029.
- Sumber: open.shopee.com/documents/v2/product.search_unpackaged_model_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `page_size` | int32 | ya | Each result set is returned as a page of entries. Use the "page_size" filters to control the maximum number of entries to retrieve per page (i.e., per call). This integer value is used to specify the maximum number of entries to return in a single "page" of data. The limit of page_size if between 1 and 48. Contoh: `2` |
| `cursor` | string | tidak | Specifies the starting entry of data to return in the current call. Default is "". If data is more than one page, the cursor can be some entry to start next call. |
| `item_id` | int64 | tidak | Shopee's unique identifier for an item. |
| `item_name` | string | tidak | Name of the item. Contoh: `JIT` |
| `model_id` | int64 | tidak | Shopee's unique identifier for a model under item. |
| `unpackaged_sku_id` | string | tidak | Unpackaged SKU ID of the model. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.total_count` | int32 | Total number of models that match the condition. |
| `response.next_cursor` | string | Pass the next_cursor in the next request as cursor to get the next page data. |
| `response.model_list` | object[] | List of models that match the condition. |
| `response.model_list[].item_id` | int64 | Shopee's unique identifier for an item. |
| `response.model_list[].item_name` | string | Name of the item. |
| `response.model_list[].model_id` | int64 | Shopee's unique identifier for a model under item. 0 for no model item. |
| `response.model_list[].unpackaged_sku_id` | string | Unpackaged SKU ID of the model. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
