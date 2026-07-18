# product.get_recommend_attribute

- Path: `/api/v2/product/get_recommend_attribute`
- Method: GET
- Auth: shop
- Deskripsi: Get recommend attributes.
- Sumber: open.shopee.com/documents/v2/product.get_recommend_attribute?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_name` | string | ya | name of item Contoh: `Ipone11` |
| `cover_image_id` | int | tidak | Cover image id of item |
| `category_id` | int | ya | ID of category Contoh: `14695` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking |
| `response` | object |  |
| `response.attribute_list` | object[] | Attribute info list. |
| `response.attribute_list[].attribute_id` | int | ID of attribute. |
| `response.attribute_list[].attribute_value_list` | object[] | Value list of this attribute. |
| `response.attribute_list[].attribute_value_list[].value_id` | int | ID of attribute value. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
