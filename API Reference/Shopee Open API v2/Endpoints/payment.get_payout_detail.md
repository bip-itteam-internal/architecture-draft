# payment.get_payout_detail

- Path: `/api/v2/payment/get_payout_detail`
- Method: GET
- Auth: shop
- Deskripsi: This API is applicable for Cross Border (CB) sellers only to get the shop's payout data, such as the payout amount, currency, FX rate, the payout's associated order income and adjustment records etc.
- Sumber: open.shopee.com/documents/v2/payment.get_payout_detail?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `page_size` | int | ya | Number of pages returned max:100 Contoh: `10` |
| `page_no` | int | ya | The page number min:1 default:1 Contoh: `1` |
| `payout_time_from` | timestamp | ya | Strat time. Maximum time range is 15 days Contoh: `1643365068` |
| `payout_time_to` | timestamp | ya | End time Contoh: `1659003469` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Error code |
| `message` | string | Error message |
| `request_id` | string | The unique id for request. |
| `response` | object | The business content of the response |
| `response.more` | boolean |  |
| `response.payout_list` | object[] |  |
| `response.payout_list[].payout_info` | object | The information of payout. |
| `response.payout_list[].payout_info.from_currency` | string | The settlement currency of orders. |
| `response.payout_list[].payout_info.payout_currency` | string | The actual currency of payout. |
| `response.payout_list[].payout_info.from_amount` | float | The settlement amount. |
| `response.payout_list[].payout_info.payout_amount` | float | The actual amount of payout. |
| `response.payout_list[].payout_info.exchange_rate` | string | The exchange rate. |
| `response.payout_list[].payout_info.payout_time` | timestamp | The time of payout. |
| `response.payout_list[].payout_info.pay_service` | string | The service provider of seller. Available value: payoneer, pingpong, lianlian. |
| `response.payout_list[].payout_info.payee_id` | string | Seller's account to receive the payout. |
| `response.payout_list[].escrow_list` | object[] |  |
| `response.payout_list[].escrow_list[].escrow_amount` | float | The total amount that the seller is expected to receive for the order. |
| `response.payout_list[].escrow_list[].currency` | string | The currency used for calculating escrow amount. |
| `response.payout_list[].escrow_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `response.payout_list[].offline_adjustment_list` | object[] | The list of offline adjustments. |
| `response.payout_list[].offline_adjustment_list[].adjustment_amount` | float | The amount of offline adjustments. |
| `response.payout_list[].offline_adjustment_list[].module` | string | The reason for offline adjustment. |
| `response.payout_list[].offline_adjustment_list[].remark` | string | The remark for the reason. |
| `response.payout_list[].offline_adjustment_list[].scenario` | string | The scenario of adjustment. |
| `response.payout_list[].offline_adjustment_list[].adjustment_level` | string | Dimension of offline adjustment. Available value: shop, order. |
| `response.payout_list[].offline_adjustment_list[].order_sn` | string | Shopee's unique identifier for an order. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
