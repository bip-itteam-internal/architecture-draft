# order.download_fbs_invoices

- Path: `/api/v2/order/download_fbs_invoices`
- Method: POST
- Auth: shop
- Deskripsi: This API allows you to download FBS invoices. To use this API, the client must first call v2.order.generate_fbs_invoices to create a new shipping document task, followed by calling v2.order.get_fbs_invoices_result to check the task status. The document can only be downloaded once the task status is "READY."
- Sumber: open.shopee.com/documents/v2/order.download_fbs_invoices?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `request_id_list` | object | tidak | list of request id (task identifiers) |

## Response

| field | tipe | keterangan |
|---|---|---|
| `response` | object |  |
| `response.request_id` | int64 |  |
| `response.file_link` | string |  |
| `error` | int32 |  |
| `error_msg` | string |  |
| `request_id` | string |  |
| `timestamp` | timestamp |  |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
