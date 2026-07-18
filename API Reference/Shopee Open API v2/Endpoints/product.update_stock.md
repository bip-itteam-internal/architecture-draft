# product.update_stock

- Path: `/api/v2/product/update_stock`
- Method: POST
- Auth: shop
- Deskripsi: Use this API to update one item_id for each call, but still can support updating multiple model_ids stock of the same item_id (If you need batch modification, please call multiple times)This API will update only "seller_stock".Whenever there is a promotion ongoing or upcoming, the total stock must be larger than or equal to real-time “reserved_stock” promotion stock (Please check v2.get_item_promotion API for more details). Items that are deleted will not be allowed to modify stock.
- Sumber: open.shopee.com/documents/v2/product.update_stock?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id` | int64 | ya | ID of item. Contoh: `1000` |
| `stock_list` | object[] | ya | Length should be between 1 to 50. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.failure_list` | object[] | Fail model list. |
| `response.failure_list[].model_id` | int64 | ID of model. |
| `response.failure_list[].failed_reason` | string | Reason for failure. |
| `response.success_list` | object[] | Success model list. |
| `response.success_list[].model_id` | int64 | ID of model. |
| `response.success_list[].location_id` | string | location id; This field and the stock field are returned in pairs |
| `response.success_list[].stock` | int64 | stock;This field is returned if seller stock is used in the request, and normal stock fields are not returned. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
