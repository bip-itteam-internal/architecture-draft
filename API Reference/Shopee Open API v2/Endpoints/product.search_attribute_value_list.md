# product.search_attribute_value_list

- Path: `/api/v2/product/search_attribute_value_list`
- Method: POST
- Auth: shop
- Deskripsi: this api is for searching attribute value list for attribute with support_search_value flag
- Sumber: open.shopee.com/documents/v2/product.search_attribute_value_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `attribute_id` | int32 | ya |  |
| `value_name` | string | tidak | search the keywords of the attributes value |
| `cursor` | int64 | ya |  |
| `limit` | int64 | ya | The range is 1 to 100 Contoh: `100` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string |  |
| `msg` | string |  |
| `warning` | string |  |
| `request_id` | string |  |
| `debug_message` | string |  |
| `response` | object |  |
| `response.value_list` | object[] |  |
| `response.value_list[].value_id` | int64 | The ID of the predefined attributes value. |
| `response.value_list[].value_name` | string | The name of the predefined attributes value. |
| `response.page_info` | object |  |
| `response.page_info.cursor` | int64 |  |
| `response.page_info.has_next` | boolean |  |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
