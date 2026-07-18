# payment.get_income_statement

- Path: `/api/v2/payment/get_income_statement`
- Method: GET
- Auth: shop
- Deskripsi: To query income statement status and provide file link if the income statement is ready to be downloaded.
- Sumber: open.shopee.com/documents/v2/payment.get_income_statement?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `income_statement_id` | int64 | ya | The identifier for income statement file request. return from the API v2.payment.generate_income_statement Contoh: `123456` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `response` | object |  |
| `response.id` | int64 | The identifier for income statement file request. |
| `response.file_name` | string | Income statement file name. |
| `response.status` | int32 | STATUS_INVALID = 0; STATUS_PROCESSING = 1; STATUS_DOWNLOADABLE = 2; STATUS_DOWNLOADED = 3; STATUS_FAILED = 4; |
| `response.generated_time` | int64 | File generation time. |
| `response.file_link` | string | Link to download income statement file. |
| `error` | string | Error Code |
| `message` | string | Error Message |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
