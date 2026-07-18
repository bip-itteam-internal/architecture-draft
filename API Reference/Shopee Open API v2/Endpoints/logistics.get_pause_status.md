# logistics.get_pause_status

- Path: `/api/v2/logistics/get_pause_status`
- Method: GET
- Auth: shop
- Deskripsi: This API returns the pause status of logistics channels under the shop. Pausing allows the shop to temporarily prevent buyers from placing orders through specific logistics channels. The response includes whether a pause is currently active, the pause end time (if active), and the remaining daily pause quota in seconds (if inactive). Sellers need to refer to the support_pause field in v2.logistics.get_channel_list response to determine which channels are actually paused.
- Sumber: open.shopee.com/documents/v2/logistics.get_pause_status?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

_Tidak ada parameter request selain common params._

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.is_paused` | boolean | Indicate the current pause status of logistics channels under the shop. Applicable values: - true: All relevant channels are currently paused and will not have any new incoming orders - false: No channels are paused and may have new incoming orders Note: Please first call v2.logistics.get_pause_status to query the current suspension status of instant orders for the store. If is_paused = true, then call v2.logistics.get_channel_list and identify the range of channels affected by the pause function through support_pause = true. |
| `response.pause_end_time` | timestamp | Time at which the relevant paused channels will automatically resume, returned only when is_paused = true, indicating the estimated time when the system will automatically resume order acceptance after the daily remaining quota is exhausted. Note: During the pause period, the seller may call the v2.logistics.set_pause_status at any time with is_paused = false to manually resume order acceptance. After resumption, the consumption of the daily remaining quota will stop and it will be retained until reset the next day. |
| `response.remaining_pause_quota` | int64 | The remaining pause quota of the shop on the current day, in seconds, returned only when is_paused = false. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
