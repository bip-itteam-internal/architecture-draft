# payment.get_income_report

- Path: `/api/v2/payment/get_income_report`
- Method: GET
- Auth: shop
- Deskripsi: To query income report status and provide file link if the income report is ready to be downloaded.
- Sumber: open.shopee.com/documents/v2/payment.get_income_report?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `income_report_id` | int64 | ya | The identifier for income report file request. Contoh: `123456` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `response` | object |  |
| `response.id` | int64 | The identifier for income statement file request. |
| `response.file_name` | string | Income report file name. |
| `response.status` | int32 | STATUS_INVALID = 0; STATUS_PROCESSING = 1; STATUS_DOWNLOADABLE = 2; STATUS_DOWNLOADED = 3; STATUS_FAILED = 4; |
| `response.generated_time` | int64 | File generation time. |
| `response.file_link` | string | Link to download income report file. |
| `error` | string | Error Code |
| `msg` | string | Error Message |
| `request_id` | string | Request ID |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
