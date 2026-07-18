# logistics.upload_serviceable_polygon

- Path: `/api/v2/logistics/upload_serviceable_polygon`
- Method: POST
- Auth: shop
- Deskripsi: Only available for Brazil sellers. Use this API to upload KML file for shop level serviceability setting for BR Entrega Turbo channel (Channel ID: 90026). Please note that multiple Outlet Shops under the same Mart Shop cannot have overlapping service areas.
- Sumber: open.shopee.com/documents/v2/logistics.upload_serviceable_polygon?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `file` | file | ya | The .kml file to be uploaded to denote the serviceability area of the shops. Note: Please refer to “KML file format for v2.logistics.upload_serviceable_polygon” ("https://open.shopee.com/faq/715") to understand the structure specifications and upload requirements for KML files. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.task_id` | string | Use the task_id to call v2.logistics.check_polygon_update_status to check if the upload job has been completed. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
