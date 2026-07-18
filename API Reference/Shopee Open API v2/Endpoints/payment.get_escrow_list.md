# payment.get_escrow_list

- Path: `/api/v2/payment/get_escrow_list`
- Method: GET
- Auth: shop
- Deskripsi: Use this API to fetch the accounting list of order.
- Sumber: open.shopee.com/documents/v2/payment.get_escrow_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `release_time_from` | timestamp | ya | Query start time Contoh: `1651680000` |
| `release_time_to` | timestamp | ya | Query end time Contoh: `1651939200` |
| `page_size` | int32 | tidak | Number of pages returned max:100 default:40 Contoh: `40` |
| `page_no` | int32 | tidak | The page number min:1 default:1 Contoh: `1` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | The business content of the response |
| `response.escrow_list` | object[] | The list of escrow order sn. |
| `response.escrow_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `response.escrow_list[].payout_amount` | float | The settlement amount |
| `response.escrow_list[].escrow_release_time` | timestamp | The release time |
| `response.more` | boolean | This is to indicate whether the escrow list is more than one page. If this value is true, you may want to continue to check next page to retrieve escrow orders. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
