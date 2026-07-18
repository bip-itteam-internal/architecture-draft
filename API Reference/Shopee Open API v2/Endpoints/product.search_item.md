# product.search_item

- Path: `/api/v2/product/search_item`
- Method: GET
- Auth: shop
- Deskripsi: Use this call to search item.
- Sumber: open.shopee.com/documents/v2/product.search_item?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `offset` | string | tidak | Specifies the starting entry of data to return in the current call. Default is empty. if data is more than one page, the offset can be some entry to start next call. Contoh: `0` |
| `page_size` | int | ya | the size of one page. Contoh: `10` |
| `item_name` | string | tidak | name of item. Contoh: `apple` |
| `attribute_status` | int | tidak | 1:get item lack of requires attribute. 2:get item lack of optional attribute. Contoh: `2` |
| `item_sku` | string | tidak | sku. If you search for item_sku and item_name at the same time, only the results that match item_sku will be returned. If you search for item_sku and attribute_status at the same time, the results that match both item_sku and attribute_status will be returned. Contoh: `sku` |
| `item_status` | string[] | tidak | NORMAL/BANNED/UNLIST/ REVIEWING/SELLER_DELETE/SHOPEE_DELETE If you want to search multiple status, please upload the url like this: item_status=NORMAL&item_status=BANNED Contoh: `["NORMAL"]` |
| `deboost_only` | boolean | tidak | If deboost_only is true, then API will return items whose deboost is true, if deboost_only is empty or false, then API will return items whose deboost is true and false simultaneously Contoh: `true` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking |
| `response` | object |  |
| `response.item_id_list` | int[] | List of item ID. |
| `response.total_count` | int | Total num of items match condation. |
| `response.next_offset` | string | If has_next_page is true, this value need set to next request.offset |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
