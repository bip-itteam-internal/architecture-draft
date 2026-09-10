# livestream.update_session

- Path: `/api/v2/livestream/update_session`
- Method: POST
- Auth: user
- Deskripsi: Update live stream information, including cover, title, description, and type (test live or normal live). (For TW, ID, TH, PH, MY, SG, VN)
- Sumber: open.shopee.com/documents/v2/livestream.update_session?type=1 (backend doc/api) — 2026-09-10
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `session_id` | int64 | ya | The identifier of livestream session. Contoh: `6236215` |
| `title` | string | ya | The title of the livestream session, cannot exceed 200 characters. Contoh: `test title` |
| `description` | string | tidak | The description of the livestream session, cannot exceed 200 characters. Contoh: `test desc` |
| `cover_image_url` | string | ya | The cover image url of the livestream session. Please call the v2.livestream.upload_image to upload the cover image file and get the cover_image_url. Contoh: `https://cf.shopee.sg/file/id-11134104-7r98o-m9pqmldbyce282` |
| `is_test` | boolean | ya | Indicate whether this livestream session if for testing purpose only. Contoh: `false` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
