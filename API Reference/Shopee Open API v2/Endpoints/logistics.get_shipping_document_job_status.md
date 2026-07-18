# logistics.get_shipping_document_job_status

- Path: `/api/v2/logistics/get_shipping_document_job_status`
- Method: POST
- Auth: shop
- Deskripsi: This API retrieves the status of a shipping document job using the job ID provided.
- Sumber: open.shopee.com/documents/v2/logistics.get_shipping_document_job_status?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `job_id` | string | ya | Generated Job ID for status tracking and download the Shipping Document Contoh: `SDK0001_a86148a97a6e04ce2ed468968de344b7` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier of the API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.job_id` | string | Generated Job ID for status tracking and download the Shipping Document |
| `response.job_name` | string | Generated Shipping Document file name. |
| `response.job_status` | string | Requested Shipping Document current status. Available values: PROCESSING, READY, EXPIRED, FAILED |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
