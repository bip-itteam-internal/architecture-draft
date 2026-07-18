# product.get_product_certification_rule

- Path: `/api/v2/product/get_product_certification_rule`
- Method: POST
- Auth: shop
- Deskripsi: Get product certification rule
- Sumber: open.shopee.com/documents/v2/product.get_product_certification_rule?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `attribute_list` | object[] | tidak | Item attributes. |
| `category_id` | int64 | tidak | ID of category. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.certification_rule_list` | object[] | New description field. Only whitelist sellers can use it. If you use the field, please upload the description_type=extended otherwise api will return error. If you don't use this field, you don't need to upload the description_type or upload description_type=normal |
| `response.certification_rule_list[].certification_type` | int64 | type of certification; always=1 |
| `response.certification_rule_list[].is_mandatory` | boolean | if this type of certification is mandatory for product |
| `response.certification_rule_list[].permit_id` | int32 |  |
| `response.certification_rule_list[].name` | string | Permit Type Name |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
