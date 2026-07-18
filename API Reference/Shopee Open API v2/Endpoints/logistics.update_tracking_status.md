# logistics.update_tracking_status

- Path: `/api/v2/logistics/update_tracking_status`
- Method: POST
- Auth: shop
- Deskripsi: Only available for Brazil sellers. This API is only available for orders/parcels which are fulfilled by BR Seller Logistics channel (logistics_channel_id: 90021), Samsung (logistics_channel_id: 90025) and BR Instant Delivery channel (logistics_channel_id: 90026). The logistics_status will become LOGISTICS_REQUEST_CREATED after arrange shipment, and can call this API to update to: LOGISTICS_PICKUP_DONE, LOGISTICS_DELIVERY_DONE, LOGISTICS_DELIVERY_FAILED.
- Sumber: open.shopee.com/documents/v2/logistics.update_tracking_status?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn` | string | ya | Shopee's unique identifier for an order. Contoh: `201212DCXHJUIKJ` |
| `tracking_number` | string | tidak | Order tracking number, might help seller to identify his order on the tracking_URL. Can only be sent when updating logistics_status to "logistic_pickup_done". Contoh: `1234567890` |
| `tracking_url` | string | tidak | Website's URL for order tracking with maximum length of 2048 characters. Can only be sent when updating logistics_status to "logistic_pickup_done". Contoh: `https://tracking_url_order_201212DCXHJUIKJ` |
| `logistics_status` | string | ya | Order status update support: - logistics_pickup_done - logistics_delivery_done - logistics_delivery_failed Contoh: `logistics_pickup_done` |
| `failed_reason` | string | tidak | Only required when updating logistics_status to "logistics_delivery_failed". Only required for BR Instant Delivery channel (logistics_channel_id: 90026). Only accept the following values. - buyer_unreachable - buyer_unresponsive - no_delivery_location_consensus Contoh: `buyer_unreachable` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | API request identifier |
| `error` | string | Error code |
| `message` | string | Error message |
| `warning` | string |  |
| `response` | object | Response body |
| `response.update_result` | string | Update results: - succeed - failed |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
