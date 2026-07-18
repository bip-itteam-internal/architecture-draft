# product.get_item_list

- Path: `/api/v2/product/get_item_list`
- Method: GET
- Auth: shop
- Deskripsi: Use this call to get a list of items.
- Sumber: open.shopee.com/documents/v2/product.get_item_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `offset` | int64 | ya | Specifies the starting entry of data to return in the current call. Default is 0. if data is more than one page, the offset can be some entry to start next call. Contoh: `0` |
| `page_size` | int64 | ya | the size of one page.Max=100 Contoh: `10` |
| `update_time_from` | timestamp | tidak | The update_time_from and update_time_to fields specify a date range for retrieving orders (based on the item update time). The update_time_from field is the starting date range. Contoh: `1611311600` |
| `update_time_to` | timestamp | tidak | The update_time_from and update_time_to fields specify a date range for retrieving orders (based on the item update time). The update_time_to field is the ending date range Contoh: `1611311631` |
| `item_status` | string[] | ya | NORMAL/BANNED/UNLIST/ REVIEWING/SELLER_DELETE/SHOPEE_DELETE If you want to search multiple status, please upload the url like this: item_status=NORMAL&item_status=BANNED Contoh: `["NORMAL"]` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking |
| `response` | object |  |
| `response.item` | object[] | list of item info with item_id/ item_status/ update_time |
| `response.item[].item_id` | int64 | Shopee's unique identifier for an item. |
| `response.item[].item_status` | string | Enumerated type that defines the current status of the item. Applicable values: NORMAL, BANNED, UNLIST, REVIEWING, SELLER_DELETE, SHOPEE_DELETE . |
| `response.item[].update_time` | timestamp | The update time of item. |
| `response.item[].tag` | object |  |
| `response.item[].tag.kit` | boolean | Indicate if the item is kit item. |
| `response.total_count` | int64 | total count of all items |
| `response.has_next_page` | boolean | This is to indicate whether the item list is more than one page. If this value is true, you may want to continue to check next page to retrieve the rest of items. |
| `response.next_offset` | int64 | if has_next_page is true, this value need set to next request.offset |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
