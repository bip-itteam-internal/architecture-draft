# livestream.get_like_item_list

- Path: `/api/v2/livestream/get_like_item_list`
- Method: GET
- Auth: user
- Deskripsi: Get the item list of My Likes tab.(For TW, ID, TH, PH, MY, SG, VN)
- Sumber: open.shopee.com/documents/v2/livestream.get_like_item_list?type=1 (backend doc/api) — 2026-09-10
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `offset` | int32 | ya | Specifies the starting entry of data to return in the current call. Default is 0, if data is more than one page, the offset can be some entry to start next call. Contoh: `0` |
| `page_size` | int32 | ya | Each result set is returned as a page of entries. Use the "page_size" filters to control the maximum number of entries to retrieve per page (i.e., per call). This integer value is used to specify the maximum number of entries to return in a single "page" of data. The limit of page_size if between 1 and 100. Contoh: `10` |
| `keyword` | string | tidak | Search items with name matching this keyword. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.more` | boolean | This is to indicate whether the list is more than one page. If this value is true, you may want to continue to check next page to retrieve the rest of data. |
| `response.next_offset` | int32 | If more is true, this value need set to next request offset. |
| `response.list` | object[] |  |
| `response.list[].item_id` | int64 | Shopee's unique identifier for an item. |
| `response.list[].shop_id` | int64 | The shop id of this item. |
| `response.list[].name` | string | Name of the item in local language. |
| `response.list[].image_url` | string | The image url of this item. |
| `response.list[].price_info` | object |  |
| `response.list[].price_info.currency` | string | The three-digit code representing the currency unit used for the item. |
| `response.list[].price_info.current_price` | float | The current price of the item in the listing currency. If product under an ongoing promotion, current_price will be the promotion price. |
| `response.list[].price_info.original_price` | float | The original price of the item in the listing currency. |
| `response.list[].affiliate_info` | object |  |
| `response.list[].affiliate_info.commission_rate` | float | The commission rate that the streamer can get, for example, 0.1 means 10%. |
| `response.list[].affiliate_info.is_campaign` | boolean | Whether participate in a campaign project (generally, the commission will be higher). |
| `response.list[].affiliate_info.campaign_mcn_name` | string | MCN agency that initiated this campaign. |
| `response.list[].affiliate_info.campaign_start_time` | int64 | Campaign start time, it's unix timestamp in seconds. |
| `response.list[].affiliate_info.campaign_end_time` | int64 | Campaign end time, it's unix timestamp in seconds. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
