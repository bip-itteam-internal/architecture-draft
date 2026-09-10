# livestream.upload_image

- Path: `/api/v2/livestream/upload_image`
- Method: POST
- Auth: user
- Deskripsi: Upload an image as the live stream cover.(For TW, ID, TH, PH, MY, SG, VN)
- Sumber: open.shopee.com/documents/v2/livestream.upload_image?type=1 (backend doc/api) — 2026-09-10
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `image` | file | ya | The image file to upload. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.image_url` | string | The image URL |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
