# product.get_comment

- Path: `/api/v2/product/get_comment`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to get comment by shop_id, item_id, or comment_id, get up to 1000 comments.
- Sumber: open.shopee.com/documents/v2/product.get_comment?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id` | int64 | tidak | The identity of product item. Contoh: `16509872` |
| `comment_id` | int64 | tidak | The identity of comment. Contoh: `120590834` |
| `cursor` | string | ya | Specifies the starting entry of data to return in the current call. Default is "". If data is more than one page, the offset can be some entry to start next call. |
| `page_size` | int32 | ya | Each result set is returned as a page of entries. Use the "page_size" filters to control the maximum number of entries to retrieve per page (i.e., per call). This integer value is used to specify the maximum number of entries to return in a single "page" of data. The limit of page_size if between 1 and 100. Contoh: `10` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.more` | boolean | This is to indicate whether the comment list is more than one page. If this value is true, you may want to continue to check next page to retrieve the rest of comments. But only respond 500 comments at most through OpenAPI, if there are more than 500, this field "more" also respond "true". |
| `response.item_comment_list` | object[] | The comment data list of the items. |
| `response.item_comment_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `response.item_comment_list[].comment_id` | string | The identity of comment. |
| `response.item_comment_list[].comment` | string | The content of the comment. |
| `response.item_comment_list[].buyer_username` | string | The username of the buyer who posted the comment. |
| `response.item_comment_list[].item_id` | int64 | The commented item's id |
| `response.item_comment_list[].model_id` | int64 | Shopee's unique identifier for a model of an item. It will only return 0 now. Will be offline on 2024-12-27 , please switch to use model_id_list. |
| `response.item_comment_list[].rating_star` | int32 | Buyer's rating for the item. |
| `response.item_comment_list[].editable` | string | The editable status of the comment. The value may be one of EXPIRED/EDITABLE/HAVE_EDIT_ONCE. |
| `response.item_comment_list[].hidden` | boolean | The comment is hidden or not. |
| `response.item_comment_list[].create_time` | timestamp | The create time of the comment. |
| `response.item_comment_list[].comment_reply` | object | The reply of the comment. |
| `response.item_comment_list[].comment_reply.reply` | string | The content of reply. |
| `response.item_comment_list[].comment_reply.hidden` | boolean | The comment reply is hidden or not. |
| `response.item_comment_list[].comment_reply.create_time` | timestamp | The time the seller replied to the comment. |
| `response.item_comment_list[].model_id_list` | int64[] | List of model id of the buyer's purchase corresponding to the comment. |
| `response.item_comment_list[].media` | object |  |
| `response.item_comment_list[].media.image_url_list` | string[] | List of image url uploaded by the buyer in the comment. |
| `response.item_comment_list[].media.video_url_list` | string[] | List of video url uploaded by the buyer in the comment. |
| `response.next_cursor` | string | If more is true, you should pass the next_cursor in the next request as cursor. The value of next_cursor will be empty string when more is false. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
