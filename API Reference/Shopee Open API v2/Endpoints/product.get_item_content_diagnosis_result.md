# product.get_item_content_diagnosis_result

- Path: `/api/v2/product/get_item_content_diagnosis_result`
- Method: POST
- Auth: shop
- Deskripsi: Get the content quality details (including content quality level, content issues, and system suggestions) for specific product list.
- Sumber: open.shopee.com/documents/v2/product.get_item_content_diagnosis_result?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id_list` | int64[] | ya | item_id list; limit [1,48] Contoh: `[10760653,10943921]` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.success_item_list` | object[] |  |
| `response.success_item_list[].item_id` | int64 | Shopee's unique identifier for an item. |
| `response.success_item_list[].quality_level` | int32 | Item's latest content quality level. Applicable values: 0: NONE (No quality level for item in SELLER_DELETE / SHOPEE_DELETE / BANNED status) 1: TO_BE_IMPROVED 2: QUALIFIED 3: EXCELLENT |
| `response.success_item_list[].unfinished_task` | object[] |  |
| `response.success_item_list[].unfinished_task[].issue_type` | int32 | Item's content issue. Applicable values: 1: TOO_FEW_IMAGES 2: WRONG_CATEGORY 3: TOO_FEW_ATTRIBUTES_FOR_QUALIFIED 4: LACK_OF_SIZE_CHART 5: LACK_OF_STANDARD_VARIATION 6: LACK_BRAND 7: TOO_SHORT_DESCRIPTION 8: TOO_SHORT_OR_TOO_LONG_NAME 9: WRONG_WEIGHT 10: LACK_OF_VIDEO 11: TOO_FEW_ATTRIBUTES_FOR_EXCELLENT |
| `response.success_item_list[].unfinished_task[].suggestion` | string | System suggestion for item's content issue. Applicable values: Add at least 3 images Adopt suggested category Add at least 1 attributes Add size chart Adopt the color or size variation Add brand info Add at least 100 characters or 1 image for desc Add characters for name to 25~100 Adopt suggested weight Add video Add at least 3 attributes |
| `response.failure_item_list` | object[] |  |
| `response.failure_item_list[].item_id` | int64 | Shopee's unique identifier for an item. |
| `response.failure_item_list[].failed_reason` | string | Item's failure reason. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
