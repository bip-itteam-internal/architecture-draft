# product.get_variations

- Path: `/api/v2/product/get_variation_tree`
- Method: GET
- Auth: shop
- Deskripsi: Get the standardized tier variation defined by Shopee, which is currently a three-layer tree structure. The top layer is variations, the second layer is groups, groups are used to divide options, and the third layer is options.
- Sumber: open.shopee.com/documents/v2/product.get_variations?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `category_id` | int | ya | Leaf category id |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `data` | object | standardized tier variation data |
| `data.standardise_variation_list` | object[] | standardized tier variation tree |
| `data.standardise_variation_list[].variation_id` | int |  |
| `data.standardise_variation_list[].variation_name` | string |  |
| `data.standardise_variation_list[].variation_group_list` | object[] |  |
| `data.standardise_variation_list[].variation_group_list[].variation_group_id` | int |  |
| `data.standardise_variation_list[].variation_group_list[].variation_group_name` | string |  |
| `data.standardise_variation_list[].variation_group_list[].variation_option_list` | object[] |  |
| `data.standardise_variation_list[].variation_group_list[].variation_option_list[].variation_option_id` | int |  |
| `data.standardise_variation_list[].variation_group_list[].variation_option_list[].variation_option_name` | string |  |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
