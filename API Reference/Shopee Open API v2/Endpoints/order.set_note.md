# order.set_note

- Path: `/api/v2/order/set_note`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to set note for an order.
- Sumber: open.shopee.com/documents/v2/order.set_note?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn` | string | ya | Shopee's unique identifier for an order. Contoh: `201224EM1FMFG1` |
| `note` | string | ya | The note seller add for reference. Contoh: `Thank you` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
