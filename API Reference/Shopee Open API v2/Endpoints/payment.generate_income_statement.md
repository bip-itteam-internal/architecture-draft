# payment.generate_income_statement

- Path: `/api/v2/payment/generate_income_statement`
- Method: GET
- Auth: shop
- Deskripsi: Trigger income statement generation.
- Sumber: open.shopee.com/documents/v2/payment.generate_income_statement?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `release_time_from` | int64 | ya | The release_time_from must be - Monday (local time) for a weekly report - The 1st day (local time) of a Month for a monthly report Contoh: `1751302800` |
| `release_time_to` | int64 | ya | The release_time_to must be - Sunday (local time) for a weekly report - The last day (local time) of a Month for a monthly report Contoh: `1753981199` |
| `statement_type` | int32 | ya | STATEMENT_TYPE_WEEKLY = 1; STATEMENT_TYPE_MONTHLY = 2; Local seller Income statement requires this value to be set. CB seller income statement does not require this. Contoh: `1` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `response` | object |  |
| `response.id` | int64 | Identifier of income statement file. |
| `error` | string | error code |
| `message` | string | error message |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
