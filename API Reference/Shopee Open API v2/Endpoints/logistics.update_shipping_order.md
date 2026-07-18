# logistics.update_shipping_order

- Path: `/api/v2/logistics/update_shipping_order`
- Method: POST
- Auth: shop
- Deskripsi: For pickup method only, use this api to update pickup address and pickup time for packages meet: 1) package's fulfillment status is LOGISTICS_PICKUP_RETRY; or 2) package's fulfillment status is 'LOGISTICS_REQUEST_CREATED' and meets the Instant Order Reschedule Pickup conditions.
- Sumber: open.shopee.com/documents/v2/logistics.update_shipping_order?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn` | string | ya | Shopee's unique identifier for an order. Contoh: `201214JASXYXY6` |
| `package_number` | string | tidak | Shopee's unique identifier for the package under an order. You should't fill the field with empty string when there is't a package number. |
| `pickup` | object | ya | Required parameter ONLY if GetParameterForInit returns "pickup" or if GetLogisticsInfo returns "pickup" under "info_needed" for the same order. Developer should still include "pickup" field in the call even if "pickup" has empty value. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
