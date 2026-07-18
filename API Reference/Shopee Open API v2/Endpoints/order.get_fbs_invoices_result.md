# order.get_fbs_invoices_result

- Path: `/api/v2/order/get_fbs_invoices_result`
- Method: POST
- Auth: shop
- Deskripsi: This API allows you to consult the status of a previously requested batch download for FBS tax documents.
- Sumber: open.shopee.com/documents/v2/order.get_fbs_invoices_result?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `request_id_list` | object | ya | - |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | int32 | Indicate error type if hit error. Empty if no error happened. |
| `error_msg` | string | Indicate error details if hit error. Empty if no error happened. |
| `result_list` | object[] |  |
| `result_list[].request_id` | int64 | Represents the current status of the request |
| `result_list[].file_name` | string | Name of the file to be downloaded |
| `result_list[].status` | string | Represents the current status of the request |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
