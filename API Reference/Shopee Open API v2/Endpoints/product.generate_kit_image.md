# product.generate_kit_image

- Path: `/api/v2/product/generate_kit_image`
- Method: POST
- Auth: shop
- Deskripsi: This API generates a single consolidated image by combining the cover images of all selected items. It is typically used to create a unified product display image for kits or bundles.
- Sumber: open.shopee.com/documents/v2/product.generate_kit_image?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `component_list` | object[] | ya | Please send up until 9 components. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking.<path></path><path></path> |
| `response` | object |  |
| `response.kit_image` | string | generated kit image |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
