# payment.get_item_installment_status

- Path: `/api/v2/payment/get_item_installment_status`
- Method: POST
- Auth: shop
- Deskripsi: Get item installment tenures.Only for TH、TW.
- Sumber: open.shopee.com/documents/v2/payment.get_item_installment_status?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id_list` | int[] | ya | Item id array, Max :100 |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Error Code |
| `message` | string | Error message |
| `request_id` | string | Request id |
| `response` | object | The business content of the response |
| `response.item_installment_list` | object[] |  |
| `response.item_installment_list[].item_id` | int | Item unique id |
| `response.item_installment_list[].tenure_list` | int[] | The tenures of item support installment. [] represents with no installment |
| `response.item_plan_ahora_list` | object[] | Only applicable for local AR sellers. |
| `response.item_plan_ahora_list[].item_id` | int | Only applicable for local AR sellers. |
| `response.item_plan_ahora_list[].participate_plan_ahora` | boolean | Only applicable for local AR sellers. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
