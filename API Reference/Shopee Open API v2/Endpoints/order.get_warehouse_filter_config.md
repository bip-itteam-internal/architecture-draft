# order.get_warehouse_filter_config

- Path: `/api/v2/order/get_warehouse_filter_config`
- Method: GET
- Auth: shop
- Deskripsi: For multi-warehouse shops, return all warehouses with packages that have not been SHIPPED including product_location_id and address_id. Compared to v2.shop.get_warehouse_detail, it covers some edge cases like warehouse that have been unlinked but still retain packages that have not been SHIPPED, and does not cover some cases like single warehouse with default product_location_id and FBS shop.
- Sumber: open.shopee.com/documents/v2/order.get_warehouse_filter_config?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

_Tidak ada parameter request selain common params._

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string |  |
| `message` | string |  |
| `request_id` | string |  |
| `response` | object |  |
| `response.warehouse_filters` | object[] |  |
| `response.warehouse_filters[].warehouse_name` | string | The warehouse name filled in when creating the warehouse address. |
| `response.warehouse_filters[].warehouse_type` | int32 | Type of warehouse. Applicable values: - 1: Local Warehouse - 2: CB Warehouse |
| `response.warehouse_filters[].product_location_id` | string | Location identifier for stocks. Different location_ids represent that your addresses are in different item stocks. |
| `response.warehouse_filters[].address_id` | int64 | Identity of address. |
| `response.warehouse_filters[].address` | string | Detail address of your warehouse. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
