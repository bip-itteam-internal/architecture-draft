# livestream.get_latest_comment_list

- Path: `/api/v2/livestream/get_latest_comment_list`
- Method: GET
- Auth: user
- Deskripsi: Get live stream room comments in the last 10 seconds, including user id, user name, comment id, comment content, and comment time. (For TW, ID, TH, PH, MY, SG, VN)
- Sumber: open.shopee.com/documents/v2/livestream.get_latest_comment_list?type=1 (backend doc/api) — 2026-09-10
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `session_id` | int64 | ya | The identifier of livestream session. Contoh: `6236215` |
| `offset` | int32 | tidak | Specifies the starting entry of data to return in the current call. Default is 0, if data is more than one page, the offset can be some entry to start next call. Contoh: `0` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.next_offset` | int32 | The offset for next page request. |
| `response.list` | object[] |  |
| `response.list[].comment_id` | int64 | The identifier of comment. |
| `response.list[].content` | string | The content of comment. |
| `response.list[].timestamp` | timestamp | Timestamp for posting comment. It's unix timestamp in seconds. |
| `response.list[].user_id` | int64 | The user id of the one who posted the comment. |
| `response.list[].username` | string | The username of the one who posted comment. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
