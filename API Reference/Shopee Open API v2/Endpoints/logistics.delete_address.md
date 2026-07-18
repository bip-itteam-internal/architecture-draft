# logistics.delete_address

- Path: `/api/v2/logistics/delete_address`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to delete address.
- Sumber: open.shopee.com/documents/v2/logistics.delete_address?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `address_id` | int | ya | The identity of address you want to delete. Contoh: `14278` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
