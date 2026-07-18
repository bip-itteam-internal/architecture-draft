# payment.get_billing_transaction_info

- Path: `/api/v2/payment/get_billing_transaction_info`
- Method: POST
- Auth: shop
- Deskripsi: This API is applicable for Cross Border (CB) sellers only to get the detailed payout transaction data, both released and to-be released transaction can be found in here
- Sumber: open.shopee.com/documents/v2/payment.get_billing_transaction_info?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `billing_transaction_info_type` | int | ya | Billing transaction types: 1: TO_RELEASE, 2: RELEASED Contoh: `1` |
| `encrypted_payout_ids` | string[] | tidak | encrypted_payout_id get from API: v2.get_payout_info when encrypted_payout_id provided and billing_transaction_info_type=2, we will return the "released" billing items under this payout. when encrypted_payout_id not provided, we will return the "to release" billing items under hasn't form payout yet Max length: 100 Contoh: `["10376329180766","637926329180767"]` |
| `cursor` | string | ya | Specifies the starting entry of data to return in the current call. Default is "". If data is more than one page, the offset can be some entry to start next call. Contoh: `""` |
| `page_size` | int | ya | Number of pages returned max:100 Contoh: `100` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Error code |
| `message` | string | Error message |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.transactions` | object |  |
| `response.transactions.amount` | float | each transaction's amount |
| `response.transactions.currency` | string | transaction currency |
| `response.transactions.order_sn` | string | transaction currency |
| `response.transactions.cost_header` | string | transaction belongs to which type |
| `response.transactions.scenario` | string | transaction detailed scenarios |
| `response.transactions.remark` | string | detailed description for this transactions |
| `response.transactions.level` | string | To define this transaction happen at order level or shop level. e.g. shop level adjustment |
| `response.transactions.billing_transaction_type` | string | could be Escrow (Order Income) or Adjustment (for this order) |
| `response.transactions.billing_transaction_status` | string | Will be either "To Release" or "Released". |
| `response.more` | boolean |  |
| `response.next_cursor` | string |  |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
