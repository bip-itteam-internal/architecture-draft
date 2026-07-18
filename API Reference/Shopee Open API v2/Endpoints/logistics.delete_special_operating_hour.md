# logistics.delete_special_operating_hour

- Path: `/api/v2/logistics/delete_special_operating_hour`
- Method: POST
- Auth: shop
- Deskripsi: This API is used to delete a specific special operating hour for a seller. This API allows sellers to manage their operating hours by removing any special operating hours that are no longer needed. To use this API, the name of the special operating hour to be deleted should be obtained from the v2.logistics.get_operating_hours API.
- Sumber: open.shopee.com/documents/v2/logistics.delete_special_operating_hour?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `name` | string | ya | Name of the special operating hour which can be retrieved from v2.logistics.get_operating_hours Contoh: `3.3 Campaign` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
