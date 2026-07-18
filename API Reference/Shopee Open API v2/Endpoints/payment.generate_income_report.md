# payment.generate_income_report

- Path: `/api/v2/payment/generate_income_report`
- Method: GET
- Auth: shop
- Deskripsi: Trigger income report generation.
- Sumber: open.shopee.com/documents/v2/payment.generate_income_report?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `release_time_from` | int64 | ya | Start time in epoch Contoh: `1234567890` |
| `release_time_to` | int64 | ya | End time in epoch Contoh: `1234567890` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `response` | object |  |
| `response.id` | int64 | Identifier of income report file. |
| `error` | string | error code |
| `msg` | string | error message |
| `request_id` | string | request id |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
