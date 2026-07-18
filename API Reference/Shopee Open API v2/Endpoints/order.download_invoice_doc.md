# order.download_invoice_doc

- Path: `/api/v2/order/download_invoice_doc`
- Method: GET
- Auth: shop
- Deskripsi: This endpoint only for PH and BR local seller. Seller can download the invoice uploaded before through this endpoint.
- Sumber: open.shopee.com/documents/v2/order.download_invoice_doc?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn` | string | ya | Shopee's unique identifier for an order. Contoh: `201218V2Y6E59M` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `invoice_doc` | file |  |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
