# payment.get_shop_installment_status

- Path: `/api/v2/payment/get_shop_installment_status`
- Method: GET
- Auth: shop
- Deskripsi: Get the installment state of shop.
- Sumber: open.shopee.com/documents/v2/payment.get_shop_installment_status?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

_Tidak ada parameter request selain common params._

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Error code |
| `message` | string | Error message |
| `request_id` | string | Request Id |
| `response` | object | The business content of the response. |
| `response.installment_status` | int | The installment status for the shop |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
