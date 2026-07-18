# payment.get_payment_method_list

- Path: `/api/v2/payment/get_payment_method_list`
- Method: GET
- Auth: public
- Deskripsi: Obtain payment method (no authentication required)
- Sumber: open.shopee.com/documents/v2/payment.get_payment_method_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

_Tidak ada parameter request selain common params._

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | error code |
| `message` | string | error message |
| `request_id` | string | Unique id for request |
| `response` | object[] |  |
| `response[].payment_method` | string[] |  |
| `response[].region` | string |  |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
