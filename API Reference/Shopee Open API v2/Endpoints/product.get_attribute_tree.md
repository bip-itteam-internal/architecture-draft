# product.get_attribute_tree

- Path: `/api/v2/product/get_attribute_tree`
- Method: GET
- Auth: shop
- Deskripsi: Get the attribute tree for categories
- Sumber: open.shopee.com/documents/v2/product.get_attribute_tree?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `category_id_list` | int[] | ya | max count is 20 |
| `language` | string | tidak | Language Support Lanuage: "SG": [ "en", "zh-Hans", "ms" ], "MY": [ "en", "zh-Hans", "ms" ], "PH": [ "en", "zh-Hans" ], "VN": [ "vn", "en" ], "ID": [ "id", "en" ], "TH": [ "th", "en" ], "BR": [ "pt-BR", "en" ], "MX": [ "es-MX", "en" ], "CO": [ "es-CO", "en" ], "CL": [ "es-CL", "en" ], "TW": [ "zh-Hant", "zh-Hans", "en" ], "IN": [ "en", "hi" ] Contoh: `"en"` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Error |
| `message` | string | Message |
| `warning` | string | Warning |
| `request_id` | string | Request ID |
| `response` | object | Resopnse |
| `response.list` | object[] | Each result corresponds to one category in category_ids |
| `response.list[].attribute_tree` | object[] | One category's attribute trees |
| `response.list[].attribute_tree[].attribute_id` | int | Attribute ID |
| `response.list[].attribute_tree[].mandatory` | boolean | Is mandatory or not |
| `response.list[].attribute_tree[].name` | string | Attribute Name |
| `response.list[].attribute_tree[].attribute_value_list` | object[] | All available values for this attribute |
| `response.list[].attribute_tree[].attribute_value_list[].value_id` | int | Value ID |
| `response.list[].attribute_tree[].attribute_value_list[].name` | string | Value name |
| `response.list[].attribute_tree[].attribute_value_list[].value_unit` | string | Value unit |
| `response.list[].attribute_tree[].attribute_value_list[].child_attribute_list` | object[] | Child attributes for the value of parent attribute The structure content is the same as attribute_tree |
| `response.list[].attribute_tree[].attribute_value_list[].multi_lang` | object[] | Translate results for display |
| `response.list[].attribute_tree[].attribute_value_list[].multi_lang[].language` | string | Language |
| `response.list[].attribute_tree[].attribute_value_list[].multi_lang[].value` | string | Translate result |
| `response.list[].attribute_tree[].attribute_info` | object | Attribute extra info |
| `response.list[].attribute_tree[].attribute_info.input_type` | int | SINGLE_DROP_DOWN = 1 SINGLE_COMBO_BOX = 2 FREE_TEXT_FILED = 3 MULTI_DROP_DOWN = 4 MULTI_COMBO_BOX = 5 |
| `response.list[].attribute_tree[].attribute_info.input_validation_type` | int | VALIDATOR_NO_VALIDATE_TYPE = 0 VALIDATOR_INT_TYPE = 1 VALIDATOR_STRING_TYPE = 2 VALIDATOR_FLOAT_TYPE = 3 VALIDATOR_DATE_TYPE = 4 |
| `response.list[].attribute_tree[].attribute_info.format_type` | int | FORMAT_NORMAL = 1 FORMAT_QUANTITATIVE_WITH_UNIT = 2 |
| `response.list[].attribute_tree[].attribute_info.date_format_type` | int | YEAR_MONTH_DATE = 0 (DD/MM/YYYY) YEAR_MONTH = 1 (MM/YYYY) |
| `response.list[].attribute_tree[].attribute_info.attribute_unit_list` | string[] | Attribute's available units list |
| `response.list[].attribute_tree[].attribute_info.max_value_count` | int | Max selected value count |
| `response.list[].attribute_tree[].attribute_info.introduction` | string | Introduction for special Attribute |
| `response.list[].attribute_tree[].attribute_info.is_oem` | boolean |  |
| `response.list[].attribute_tree[].attribute_info.support_search_value` | boolean | Indicates whether this attribute has searchable values. If yes, please call v2.product.search_attribute_value_list to get the default values |
| `response.list[].attribute_tree[].multi_lang` | object[] | Attribute translate info |
| `response.list[].attribute_tree[].multi_lang[].language` | string | Language |
| `response.list[].attribute_tree[].multi_lang[].value` | string | Translate result |
| `response.list[].category_id` | int | Category ID |
| `response.list[].warning` | string | Warning msg |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
