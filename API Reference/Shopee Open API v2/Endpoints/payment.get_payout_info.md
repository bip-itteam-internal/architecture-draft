# payment.get_payout_info

- Path: `/api/v2/payment/get_payout_info`
- Method: GET
- Auth: shop
- Deskripsi: This is a new API which applicable for Cross Border (CB) sellers only to get the shop's payout data, will be used for the original API v2.get_payout_details replacement, we provide data such as the payout amount, currency, FX rate, the payout's associated order income and adjustment records etc.
- Sumber: open.shopee.com/documents/v2/payment.get_payout_info?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `payout_time_from` | timestamp | ya | Start time. Maximum time range is 15 days Contoh: `1643365068` |
| `payout_time_to` | timestamp | ya | Payout End time Contoh: `1659003469` |
| `page_size` | int | ya | Number of pages returned max:100 Contoh: `10` |
| `cursor` | string | ya | Specifies the starting entry of data to return in the current call. Default is "". If data is more than one page, the offset can be some entry to start next call. Contoh: `""` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.payout_list` | object |  |
| `response.payout_list.from_currency` | string | The settlement currency of orders. |
| `response.payout_list.payout_currency` | string | The actual currency of payout. |
| `response.payout_list.from_amount` | float | The settlement amount. |
| `response.payout_list.payout_amount` | float | The actual amount of payout. |
| `response.payout_list.exchange_rate` | string | The exchange rate. |
| `response.payout_list.payout_time` | timestamp | The time of payout. |
| `response.payout_list.pay_service` | string | The service provider of seller. Available value: payoneer, pingpong, lianlian. |
| `response.payout_list.payee_id` | string | Seller's account to receive the payout. |
| `response.payout_list.encrypted_payout_id` | string | payout id used to query API "v2.get_billing_item_info" as request parameters. User can get detailed billing items under current payout |
| `response.more` | boolean | True or False |
| `response.next_cursor` | string | used for next batch data query. will return empty when all data been returned |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
