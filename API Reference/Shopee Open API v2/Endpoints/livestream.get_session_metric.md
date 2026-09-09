# livestream.get_session_metric

- Path: `/api/v2/livestream/get_session_metric`
- Method: GET
- Auth: user
- Deskripsi: Get real-time indicator data of the live stream room, including the number of likes, comments, shares, views, etc.(For TW, ID, TH, PH, MY, SG, VN)
- Sumber: open.shopee.com/documents/v2/livestream.get_session_metric?type=1 (backend doc/api) — 2026-09-09
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
| `response.gmv` | float | Value of placed orders (paid and unpaid) during Livestream, including sales from cancelled orders. |
| `response.atc` | int64 | Number of "Add To Cart" button clicked for all products in the orange bag during livestream. |
| `response.ctr` | float | Number of products clicks divided by Number of Livestream views. |
| `response.co` | float | Amount of product orders from the stream divided by Amount of product clicks from the stream. |
| `response.orders` | int64 | Number of placed orders (paid and unpaid) during Livestream, including cancelled orders. |
| `response.ccu` | int64 | Number of viewers during stream. |
| `response.engage_ccu_1m` | int64 | Number of Concurrent viewers in the stream that have watched for more than 1 minute. |
| `response.peak_ccu` | int64 | Highest number of viewers during stream. |
| `response.likes` | int64 | Number of "Like" clicked during livestream. |
| `response.comments` | int64 | Number of comments acquired during the stream. |
| `response.shares` | int64 | Number of shares created during the stream. |
| `response.views` | int64 | Number of views from the stream. |
| `response.avg_viewing_duration` | int64 | Average of Viewer duration watching in the stream. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
