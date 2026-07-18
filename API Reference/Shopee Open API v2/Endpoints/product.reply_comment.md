# product.reply_comment

- Path: `/api/v2/product/reply_comment`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to reply comments from buyers in batch.
- Sumber: open.shopee.com/documents/v2/product.reply_comment?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `comment_list` | object[] | ya | The list of comment. The limit is between 1 and 100. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.result_list` | object[] | The result list of the request comment list. |
| `response.result_list[].comment_id` | int | The identity of comment. |
| `response.result_list[].fail_error` | string | Indicate error details if one element hit error. |
| `response.result_list[].fail_message` | string | Indicate error type if one element hit error. |
| `warning` | string[] | Indicate warning message you should take care. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
