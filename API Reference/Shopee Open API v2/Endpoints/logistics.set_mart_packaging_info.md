# logistics.set_mart_packaging_info

- Path: `/api/v2/logistics/set_mart_packaging_info`
- Method: POST
- Auth: shop
- Deskripsi: [Only for ID mart seller] This API allows sellers to set up their packaging fee info. Through this API, sellers can enable or disable packaging fees, and if enabled, specify the dimensions of the packaging and the associated fee. This ensures that sellers can configure their shipping costs accurately based on their packaging requirements.
- Sumber: open.shopee.com/documents/v2/logistics.set_mart_packaging_info?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `enable` | boolean | ya | Indicates whether the seller has enabled or disabled the packaging fee configuration. True: The seller charges a packaging fee. False: The seller does not charge a packaging fee. Contoh: `true` |
| `dimension` | object | tidak | Required if enabled is set to True. |
| `packaging_fee` | object | tidak | Required if enabled is set to True. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.enable` | boolean | Indicates whether the seller has enabled or disabled the packaging fee configuration. True: The seller charges a packaging fee. False: The seller does not charge a packaging fee. |
| `response.dimension` | object | Returned only if enabled is set to True. |
| `response.dimension.length` | int32 | The length of the packaging in centimetres (cm). |
| `response.dimension.width` | int32 | The width of the packaging in centimetres (cm). |
| `response.dimension.height` | int32 | The height of the packaging in centimetres (cm). |
| `response.packaging_fee` | object | Returned only if enabled is set to True. |
| `response.packaging_fee.value` | float | The packaging fee price in the seller's local currency. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
