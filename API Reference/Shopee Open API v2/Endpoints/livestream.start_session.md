# livestream.start_session

- Path: `/api/v2/livestream/start_session`
- Method: POST
- Auth: user
- Deskripsi: Start Live. (For TW, ID, TH, PH, MY, SG, VN)
- Sumber: open.shopee.com/documents/v2/livestream.start_session?type=1 (backend doc/api) — 2026-09-10
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `session_id` | int64 | ya | The identifier of livestream session. Contoh: `6236215` |
| `domain_id` | int64 | ya | The identifier of the stream domain. Contoh: `1` |
| `ai_stream` | boolean | tidak | Only available in PH region. To support transparent experiences on Shopee Live, please select this option if AI-generated streamer is used for live-streaming. Failure of doing so may lead to warning or termination. Learn more about the policy: PH: https://seller.shopee.ph/edu/article/25213 ("https://seller.shopee.ph/edu/article/25213") Contoh: `true` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. <path></path><path></path> |
| `response` | object | Detail informations you are querying. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
