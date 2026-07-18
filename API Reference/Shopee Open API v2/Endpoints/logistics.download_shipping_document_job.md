# logistics.download_shipping_document_job

- Path: `/api/v2/logistics/download_shipping_document_job`
- Method: POST
- Auth: shop
- Deskripsi: This API allows users to download the shipping document associated with a specific job ID. It checks the job status before proceeding with the download.
- Sumber: open.shopee.com/documents/v2/logistics.download_shipping_document_job?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `job_id` | string | ya | Generated Job ID for status tracking and download the Shipping Document Contoh: `SDK0001_a86148a97a6e04ce2ed468968de344b7` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `file` | file |  |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
