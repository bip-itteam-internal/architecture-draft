# logistics.check_polygon_update_status

- Path: `/api/v2/logistics/check_polygon_update_status`
- Method: POST
- Auth: shop
- Deskripsi: Only available for Brazil sellers. Use this API to check the status of polygon file uploaded for BR Entrega Turbo channel (Channel ID: 90026) by querying the task_id returned via the v2.logistics.upload_serviceable_polygon.
- Sumber: open.shopee.com/documents/v2/logistics.check_polygon_update_status?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `task_id` | string | ya | ID that needs to be checked. Please pass the task_id returned via the v2.logistics.upload_serviceable_polygon. Contoh: `test_task_id` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.status` | int32 | Serviceable polygon file upload status. Applicable values: 0: Task completed 1: Task in progress 2: KML file related errors |
| `response.message` | string | Details of the upload status, e.g "task in progress". |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
