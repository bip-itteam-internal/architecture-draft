# logistics.create_shipping_document_job

- Path: `/api/v2/logistics/create_shipping_document_job`
- Method: POST
- Auth: shop
- Deskripsi: This API creates a shipping document job for selected documents. The system receives requests and returns a job ID along with success and failure details.
- Sumber: open.shopee.com/documents/v2/logistics.create_shipping_document_job?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `shipping_document_type` | string | ya | The type of shipping document. Available values: THERMAL_UNPACKAGED_LABEL Contoh: `THERMAL_UNPACKAGED_LABEL` |
| `unpackaged_sku_requests` | object[] | tidak | List of Unpackaged SKUs to generate labels for. Note: The unpackaged_sku_requests and package_list cannot be populated at the same time, please select one. |
| `package_list` | string[] | tidak | List of Package Numbers to generate labels for. (maximum 600 total) Note: The unpackaged_sku_requests and package_list cannot be populated at the same time, please select one. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier of the API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.job_id` | string | Generated Job ID which will be used for status tracking and download the Shipping Document |
| `response.success_id_list` | string[] | List of Package Number or Unpackaged SKU ID that succeeds in generating Shipping Document |
| `response.fail_list` | object[] | List of Package Numbers or Unpackaged SKUs that failed in generating Shipping Document |
| `response.fail_list[].id` | string | Package Number or Unpackaged SKU ID that failed in generating Shipping Document |
| `response.fail_list[].fail_error` | string | Indicate error type if one element hit error. |
| `response.fail_list[].fail_message` | string | Indicate error details if one element hit error. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
