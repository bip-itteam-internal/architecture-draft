# order.generate_fbs_invoices

- Path: `/api/v2/order/generate_fbs_invoices`
- Method: POST
- Auth: shop
- Deskripsi: This API creates a task to download a specific tax document (e.g., sales invoice, remessa invoice) for the seller's account, available only after the document is issued by the system as part of the Fulfilled by Shopee (FBS) process. The workflow is as follows: (1) v2.order.generate_fbs_invoices; (2) v2.order.get_fbs_invoices_result; (3) v2.order.download_fbs_invoices. Please note: The download link for the document will expire 30 minutes after being generated.
- Sumber: open.shopee.com/documents/v2/order.generate_fbs_invoices?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `batch_download` | object | tidak |  |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | int32 | Indicate error type if hit error. Empty if no error happened. |
| `error_msg` | string | Error messages |
| `result_list` | object[] |  |
| `result_list[].request_id` | int64 | Unique task identifier that includes one or more tax documents to be downloaded according to the filters sent in the request. |
| `result_list[].fail_error` | string | Indicate error type if one element hit error. Empty if no error happened. |
| `result_list[].fail_message` | string | Indicate error details if one element hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
