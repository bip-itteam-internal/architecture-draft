# product.get_item_list_by_content_diagnosis

- Path: `/api/v2/product/get_item_list_by_content_diagnosis`
- Method: POST
- Auth: shop
- Deskripsi: Query the list of products and their content quality details by content quality level or content issues.
- Sumber: open.shopee.com/documents/v2/product.get_item_list_by_content_diagnosis?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `page_size` | int32 | ya | the size of one page. Max=48 Contoh: `5` |
| `offset` | string | tidak | Specifies the starting entry of data to return in the current call. Default is empty. if data is more than one page, the offset can be some entry to start next call. Contoh: `""` |
| `quality_level` | int32[] | tidak | Item's latest content quality level. Applicable values: 1: TO_BE_IMPROVED 2: QUALIFIED 3: EXCELLENT Contoh: `[1,2]` |
| `issue_type` | int32[] | tidak | Item's content issue. Applicable values: 1: TOO_FEW_IMAGES 2: WRONG_CATEGORY 3: TOO_FEW_ATTRIBUTES_FOR_QUALIFIED 4: LACK_OF_SIZE_CHART 5: LACK_OF_STANDARD_VARIATION 6: LACK_BRAND 7: TOO_SHORT_DESCRIPTION 8: TOO_SHORT_OR_TOO_LONG_NAME 9: WRONG_WEIGHT 10: LACK_OF_VIDEO 11: TOO_FEW_ATTRIBUTES_FOR_EXCELLENT If you need to pass both quality_level and issue_type, the logic are as follows: - When quality_level is 1, issue_type can only be 1, 2, 3, 4, 5 - When quality_level is 2, issue_type can only be 6, 7, 8, 9, 10, 11 - When quality_level is 3, issue_type can only be empty Contoh: `[1,2,3,4,5,6,7,8,9,10,11]` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking |
| `response` | object |  |
| `response.item_list` | object[] |  |
| `response.item_list[].item_id` | int64 | Shopee's unique identifier for an item. |
| `response.item_list[].quality_level` | int32 | Item's latest content quality level. Applicable values: 0: NONE (No quality level for item in SELLER_DELETE / SHOPEE_DELETE / BANNED status) 1: TO_BE_IMPROVED 2: QUALIFIED 3: EXCELLENT |
| `response.item_list[].unfinished_task` | object[] |  |
| `response.item_list[].unfinished_task[].issue_type` | int32 | Item's content issue. Applicable values: 1: TOO_FEW_IMAGES 2: WRONG_CATEGORY 3: TOO_FEW_ATTRIBUTES_FOR_QUALIFIED 4: LACK_OF_SIZE_CHART 5: LACK_OF_STANDARD_VARIATION 6: LACK_BRAND 7: TOO_SHORT_DESCRIPTION 8: TOO_SHORT_OR_TOO_LONG_NAME 9: WRONG_WEIGHT 10: LACK_OF_VIDEO 11: TOO_FEW_ATTRIBUTES_FOR_EXCELLENT |
| `response.item_list[].unfinished_task[].suggestion` | string | System suggestion for item's content issue. Applicable values: Add at least 3 images Adopt suggested category Add at least 1 attributes Add size chart Adopt the color or size variation Add brand info Add at least 100 characters or 1 image for desc Add characters for name to 25~100 Adopt suggested weight Add video Add at least 3 attributes |
| `response.total_count` | int64 | Total num of items match condition. |
| `response.has_next_page` | boolean | This is to indicate whether the item list is more than one page. If this value is true, you may want to continue to check next page to retrieve the rest of items. |
| `response.next_offset` | string | If has_next_page is true, this value need set to next request.offset |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
