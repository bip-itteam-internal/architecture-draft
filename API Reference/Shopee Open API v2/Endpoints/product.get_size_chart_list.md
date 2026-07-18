# product.get_size_chart_list

- Path: `/api/v2/product/get_size_chart_list`
- Method: GET
- Auth: shop
- Deskripsi: Get new size chart list. Now only support local shop to use new size chart.
- Sumber: open.shopee.com/documents/v2/product.get_size_chart_list?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `category_id` | string | ya | category id under this shop Contoh: `100087` |
| `page_size` | string | ya | the size of one page. Max=50. Contoh: `10` |
| `cursor` | string | tidak | Specifies the starting entry of data to return in the current call. Default is "". If data is more than one page, the cursor can be some entry to start next call. Contoh: `1683255510` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.size_chart_list` | object[] |  |
| `response.size_chart_list[].size_chart_id` | string | ID of new size chart |
| `response.total_count` | string | total number of new size chart under requested category_id |
| `response.next_cursor` | string | if next_cursor has value, this value need set to next request.cursor |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
