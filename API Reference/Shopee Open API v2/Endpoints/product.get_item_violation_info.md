# product.get_item_violation_info

- Path: `/api/v2/product/get_item_violation_info`
- Method: GET
- Auth: shop
- Deskripsi: get item violation info
- Sumber: open.shopee.com/documents/v2/product.get_item_violation_info?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id_list` | int[] | ya | item_id list; limit [0,50] Contoh: `[34001,34002]` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.item_list` | object[] |  |
| `response.item_list[].item_id` | int | Shopee's unique identifier for an item. |
| `response.item_list[].item_name` | string | Name of the item. |
| `response.item_list[].item_status` | string | Enumerated type that defines the current status of the item. Applicable values: NORMAL, BANNED, UNLIST, SELLER_DELETE, SHOPEE_DELETE, REVIEWING. |
| `response.item_list[].deboost` | boolean | If deboost is true, means that the item's search ranking is lowered. |
| `response.item_list[].item_status_details` | object[] |  |
| `response.item_list[].item_status_details[].violation_type` | string | Violation types defined by Shopee. Applicable values: Prohibited Listing Counterfeit and IP Infringement Spam Inappropriate Image Insufficient Information Mall Listing Improvement Other Listing Improvement |
| `response.item_list[].item_status_details[].violation_reason` | string | The reason for violation. |
| `response.item_list[].item_status_details[].suggestion` | string | Shopee provides you with suggestions for modifying items. |
| `response.item_list[].item_status_details[].fix_deadline_time` | timestamp | Action required deadline. Empty if no deadline. |
| `response.item_list[].item_status_details[].update_time` | timestamp | Latest update time. |
| `response.item_list[].deboost_details` | object[] |  |
| `response.item_list[].deboost_details[].violation_type` | string | Violation types defined by Shopee. Applicable values: Prohibited Listing Counterfeit and IP Infringement Spam Inappropriate Image Insufficient Information Mall Listing Improvement Other Listing Improvement |
| `response.item_list[].deboost_details[].violation_reason` | string | The reason for violation. |
| `response.item_list[].deboost_details[].suggestion` | string | Shopee provides you with suggestions for modifying items. |
| `response.item_list[].deboost_details[].suggested_category` | object[] |  |
| `response.item_list[].deboost_details[].suggested_category[].category_id` | int | ID for Shopee suggested category. |
| `response.item_list[].deboost_details[].suggested_category[].category_name` | string | Default name for Shopee suggested category. |
| `response.item_list[].deboost_details[].fix_deadline_time` | timestamp | Action required deadline. Empty if no deadline. |
| `response.item_list[].deboost_details[].update_time` | timestamp | Latest update time. |
| `response.item_list[].fail_error` | string | Indicate error type if one element hit error. |
| `response.item_list[].fail_message` | string | Indicate error details if one element hit error. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
