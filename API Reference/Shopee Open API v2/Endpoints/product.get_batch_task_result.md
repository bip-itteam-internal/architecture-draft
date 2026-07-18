# product.get_batch_task_result

- Path: `/api/v2/product/get_batch_task_result`
- Method: GET
- Auth: shop
- Deskripsi: Query batch task result
- Sumber: open.shopee.com/documents/v2/product.get_batch_task_result?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `task_type` | int32 | ya | The task type. 1: price; 2: stock; 3: publish outlet; 4: add item. |
| `task_id` | int64 | ya | The task ID to query. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.publish_status` | int32 | The publish status. 1: ongoing; 2: finished. |
| `response.success_list` | object[] | The batch task success records. |
| `response.success_list[].shop_id` | int64 | The shop ID |
| `response.success_list[].item_id` | int64 | The item ID of the item in the shop. |
| `response.success_list[].model_id` | int64 | The model ID of the model in the shop. |
| `response.failed_list` | object[] | The batch task failed records. |
| `response.failed_list[].shop_id` | int64 | The shop ID |
| `response.failed_list[].item_id` | int64 | The item ID of the item in the shop. |
| `response.failed_list[].model_id` | int64 | The model ID of the model in the shop. |
| `response.failed_list[].failed_reason` | string | The failed reason. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
