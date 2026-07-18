# payment.get_income_overview

- Path: `/api/v2/payment/get_income_overview`
- Method: GET
- Auth: shop
- Deskripsi: Retrieves a consolidated snapshot of the seller’s income amounts categorized by income status for a specified shop. This API provides a holistic overview similar to Seller Center’s “Income Overview” section, allowing external systems to reflect the same current payout view. Data is dynamically determined based on the shop type (Local or Cross Border) and the income status requested. Historical income results are not retrievable, providing consistent information as Seller Centre.
- Sumber: open.shopee.com/documents/v2/payment.get_income_overview?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `income_status` | int32 | tidak | Status of Seller Income payout (Enum - Desc) Local Shop 1 -Released 2 - Pending CB Shop 0 - To Release 1 - Released 2 - Pending Note: By default, if Income Status was not provided in the request params (non mandatory), API response will return all values for all Income status based on either Local/CB Contoh: `1` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.latest_payout_date` | string | The latest payout date for the released income. Format: YYYY-MM-DD. Only for CN shops. |
| `response.total_income` | object | Object containing total income components. |
| `response.total_income.pending_amount` | float | Total amount pending release (Local: orders before ESCROW_PAID; CB: orders before ESCROW_PAYOUT). <path></path> |
| `response.total_income.to_release_amount` | float | Amount queued for release in the next payout cycle (CB only). Not applicable for Local shops. <path></path> |
| `response.total_income.released_amount` | float | Total amount successfully released to the seller. <path></path> |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
