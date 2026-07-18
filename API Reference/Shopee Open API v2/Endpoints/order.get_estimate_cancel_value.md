# order.get_estimate_cancel_value

- Path: `/api/v2/order/get_estimate_cancel_value`
- Method: POST
- Auth: shop
- Deskripsi: Returns the estimated refund value for a partial order cancellation given the specified items to cancel.
- Sumber: open.shopee.com/documents/v2/order.get_estimate_cancel_value?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn` | string | ya | Shopee's unique identifier for an order. Contoh: `2012300NQJVTYN` |
| `partial_cancel_item_list` | object[] | ya | The list of item models and quantities for which the seller wants to estimate the cancellation value before submitting the actual partial cancellation request. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `cancel_value_price` | string | The estimated cancellation value for the selected item quantities. This value is calculated before the actual cancellation is submitted and can be used by sellers to preview the expected cancellation amount and support partial cancellation confirmation. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
