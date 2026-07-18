# order.split_order

- Path: `/api/v2/order/split_order`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to split an order into multiple packages. Orders that include installation services cannot be split by quantity.
- Sumber: open.shopee.com/documents/v2/order.split_order?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn` | string | ya | Shopee's unique identifier for an order. Contoh: `2012300NQJVTYN` |
| `package_list` | object[] | ya | The list of packages that you want to split. Note: - Orders that include installation services cannot be split by quantity. - When splitting the order, must contain all items in the order in one request. - You can split the order into 30 parcels at most in TW and 5 parcels at most in other regions. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.order_sn` | string | Shopee's unique identifier for an order. |
| `response.package_list` | object[] | The list of package under this order you have split. |
| `response.package_list[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `response.package_list[].item_list` | object[] | The list of items under this package. |
| `response.package_list[].item_list[].item_id` | int64 | Shopee's unique identifier for an item. |
| `response.package_list[].item_list[].model_id` | int64 | Shopee's unique identifier for a model. |
| `response.package_list[].item_list[].order_item_id` | int | The identify of order item. For items in one same bundle deal promotion, the order_item_id should share the same id, such as 1,2. For items not in bundle deal promotion, the order_item_id should be the same as item_id. |
| `response.package_list[].item_list[].promotion_group_id` | int | The identify of product promotion. For items in one same add on deal promotion, the promotion_group_id should share the same id. For items not in add on deal promotion, the promotion_group_id should be 0. And the data is from group_id of shopee.orders.GetOrderDetails. |
| `response.package_list[].item_list[].model_quantity` | int | The number of identical items put in the package. |
| `request_id` | string | The identifier of the API request for error tracking. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
