# livestream.get_session_detail

- Path: `/api/v2/livestream/get_session_detail`
- Method: GET
- Auth: user
- Deskripsi: Get basic information about the live streaming room, including cover, title, description, type (test live or normal live), create time, update time, stream url, etc. (For TW, ID, TH, PH, MY, SG, VN)
- Sumber: open.shopee.com/documents/v2/livestream.get_session_detail?type=1 (backend doc/api) — 2026-09-09
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `session_id` | int64 | ya | The identifier of livestream session. Contoh: `6236215` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.session_id` | int64 | The identifier of livestream session. |
| `response.title` | string | The title of the livestream session. |
| `response.description` | string | The description of the livestream session. |
| `response.cover_image_url` | string | The cover image URL of the livestream session. |
| `response.status` | int32 | The status of the livestream session, the enumeration values are as follows: 0 - Initial 1 - Ongoing 2 - Ended |
| `response.share_url` | string | The share link of the livestream session. |
| `response.is_test` | boolean | Indicate whether this livestream session if for testing purpose only. |
| `response.create_time` | int64 | The creation time of the livestream session. It's unix timestamp in seconds. |
| `response.update_time` | int64 | The update time of the livestream session. It's unix timestamp in seconds. |
| `response.start_time` | int64 | The start time of the livestream session, 0 if session is not started yet. It's unix timestamp in seconds. |
| `response.end_time` | int64 | The end time of livestream session, 0 if session is not ended yet. It's unix timestamp in seconds. |
| `response.stream_url_list` | object |  |
| `response.stream_url_list.push_url` | string | The push stream url for the livestream session. |
| `response.stream_url_list.push_key` | string | The push stream key for the livestream session. |
| `response.stream_url_list.play_url` | string | The pull stream url of the livestream session. |
| `response.stream_url_list.domain_id` | int64 | The identifier of the stream domain, need to be passed in request for v2.livestream.start_session. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
