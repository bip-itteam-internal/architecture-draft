# livestream.get_item_set_list

- Path: `/api/v2/livestream/get_item_set_list`
- Method: GET
- Auth: user
- Deskripsi: Get the product set of the live stream, including the product set name, id, and item number. (For TW, ID, TH, PH, MY, SG, VN)
- Sumber: open.shopee.com/documents/v2/livestream.get_item_set_list?type=1 (backend doc/api) — 2026-09-10
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `offset` | int32 | ya | Specifies the starting entry of data to return in the current call. Default is 0, if data is more than one page, the offset can be some entry to start next call. Contoh: `0` |
| `page_size` | int32 | ya | Each result set is returned as a page of entries. Use the "page_size" filters to control the maximum number of entries to retrieve per page (i.e., per call). This integer value is used to specify the maximum number of entries to return in a single "page" of data. The limit of page_size if between 1 and 100. Contoh: `10` |
| `keyword` | string | tidak | Search the item set with it's name matching the keyword. Contoh: `set` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.more` | boolean | This is to indicate whether the list is more than one page. If this value is true, you may want to continue to check next page to retrieve the rest of data. |
| `response.next_offset` | int64 | If more is true, this value need set to next request offset. |
| `response.list` | object[] |  |
| `response.list[].item_set_id` | int64 | The identifier of the item set. |
| `response.list[].item_set_name` | string | The name of the item set. |
| `response.list[].item_count` | int64 | The number of items in this item set. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
