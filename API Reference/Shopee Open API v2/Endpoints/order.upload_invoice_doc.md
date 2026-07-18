# order.upload_invoice_doc

- Path: `/api/v2/order/upload_invoice_doc`
- Method: POST
- Auth: shop
- Deskripsi: This endpoint is for PH and BR local seller. Upload the invoice document
- Sumber: open.shopee.com/documents/v2/order.upload_invoice_doc?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn` | string | ya | Shopee's unique identifier for an order. Contoh: `201218V2Y6E59M` |
| `file_type` | int | ya | the type of invoice file. 1:pdf 2.jpeg 3.png. 4.xml Contoh: `1` |
| `file` | file | ya | invoice file. File size limit to 1MB. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
