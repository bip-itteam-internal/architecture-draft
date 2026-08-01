# ams.get_performance_data_update_time

- Path: `/api/v2/ams/get_performance_data_update_time`
- Method: GET
- Auth: shop
- Deskripsi: Retrieve the latest date of AMS dashboard data metrics update.
- Sumber: open.shopee.com/documents/v2/ams.get_performance_data_update_time?type=1 (backend doc/api) — 2026-08-01
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `marker_type` | string | ya | Marker type. Applicable values: - AmsMarker: Used to query the data update date for ams metrics. Contoh: `AmsMarker` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. <path></path><path></path> |
| `response` | object |  |
| `response.last_report_date` | string | The latest date of AMS dashboard data metrics update. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
