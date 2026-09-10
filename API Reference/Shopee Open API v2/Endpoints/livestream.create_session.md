# livestream.create_session

- Path: `/api/v2/livestream/create_session`
- Method: POST
- Auth: user
- Deskripsi: Create a new live stream, include basic information, like cover, title, description, type (test live or normal live). (For TW, ID, TH, PH, MY, SG, VN)
- Sumber: open.shopee.com/documents/v2/livestream.create_session?type=1 (backend doc/api) — 2026-09-10
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `title` | string | ya | The title of livestream session, cannot exceed 200 characters. Contoh: `test livestream` |
| `description` | string | tidak | The description of livestream session, cannot exceed 200 characters. Contoh: `test` |
| `cover_image_url` | string | ya | The cover image URL of livestream session. Please call the v2.livestream.upload_image to upload the cover image file and get the cover_image_url. Contoh: `https://cf.shopee.sg/file/id-11134104-7r98o-m9pq7jw2cdhx5e` |
| `is_test` | boolean | tidak | Indicate whether the livestream session is for testing purpose only. Contoh: `false` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.session_id` | int64 | The identifier of livestream session. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
