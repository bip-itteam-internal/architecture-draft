# payment.set_shop_installment_status

- Path: `/api/v2/payment/set_shop_installment_status`
- Method: POST
- Auth: shop
- Deskripsi: Sets the staging capability of shop level.
- Sumber: open.shopee.com/documents/v2/payment.set_shop_installment_status?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `installment_status` | int | ya | The status of installment contains 1 and 0. Contoh: `0` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string |  |
| `error` | string |  |
| `message` | string |  |
| `response` | object |  |
| `response.installment_status` | int |  |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
