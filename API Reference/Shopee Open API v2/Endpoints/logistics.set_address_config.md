# logistics.set_address_config

- Path: `/api/v2/logistics/set_address_config`
- Method: POST
- Auth: shop
- Deskripsi: Use this API to set address config of your shop.
- Sumber: open.shopee.com/documents/v2/logistics.set_address_config?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `show_pickup_address` | boolean | tidak | Definite show pickup address or not. Contoh: `true` |
| `address_type_config` | object | tidak | The config of your shop addres. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
