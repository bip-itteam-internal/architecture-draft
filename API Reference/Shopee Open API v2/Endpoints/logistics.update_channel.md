# logistics.update_channel

- Path: `/api/v2/logistics/update_channel`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to update shop level logistics channel's configuration.
- Sumber: open.shopee.com/documents/v2/logistics.update_channel?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `logistics_channel_id` | int64 | ya | The identity of logistic channel. Contoh: `14623` |
| `enabled` | boolean | tidak | Whether to enable this logistic channel. Contoh: `true` |
| `cod_enabled` | boolean | tidak | Whether to enable COD for this logistic channel. Only COD supported channels are applicable. Contoh: `true` |
| `auto_call_driver_setting` | object | tidak |  |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier of the API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.shop_id` | int64 | Shopee's unique identifier for a shop. |
| `response.enabled` | boolean | Whether this logistic channel is enabled. |
| `response.cod_enabled` | boolean | Whether COD is enabled for this channel. |
| `response.logistics_channel_id` | int64 | The identity of logistic channel. |
| `response.updated_channels` | object[] | List of channels that are updated in the operation (inclusive of dependent logistics channels) |
| `response.updated_channels[].channel_id` | int64 | Logistics channel ID |
| `response.updated_channels[].channel_display_name` | string | Logistics channel name |
| `response.updated_channels[].unsupport_warehouse` | object[] | List details of unsupported warehouses |
| `response.updated_channels[].unsupport_warehouse[].warehouse_id` | int64 | Unsupported warehouse ID |
| `response.updated_channels[].unsupport_warehouse[].warehouse_name` | string | Unsupported warehouse name |
| `response.is_multi_warehouse` | boolean |  |
| `response.auto_call_driver_setting` | object |  |
| `response.auto_call_driver_setting.auto_call_driver_enabled` | boolean | Indicate whether Auto Call Driver is currently enabled for this channel. |
| `response.auto_call_driver_setting.preparation_time` | int32 | The current valid preparation time for this channel, in minutes. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
