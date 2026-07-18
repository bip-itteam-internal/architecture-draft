# logistics.batch_update_tpf_warehouse_tracking_status

- Path: `/api/v2/logistics/batch_update_tpf_warehouse_tracking_status`
- Method: POST
- Auth: shop
- Deskripsi: For CB orders that fulfilled by 3PF, support 3PF Warehouse Vendors to update the tpf_tracking_status when 3PF warehouse receive the order and complete the outbound of the package. CB orders that fulfilled by 3PF： v2.shop.get_shop_info - shop_fulfillment_flag in {Pure - 3PF Shop,PFF - 3PF Shop,LFF Hybrid Shop} And v2.order.get_order_detail - fulfillment_flag = fulfilled_by_local_seller
- Sumber: open.shopee.com/documents/v2/logistics.batch_update_tpf_warehouse_tracking_status?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `tpf_name` | string | ya | The name of 3PF Warehouse Vendor. Prohibit pure numbers and excessive abbreviations. Standardize naming for easy business recognition. Input priority: warehouse English name > full pinyin of warehouse brand name > warehouse Chinese name > other officially recognized and prominent names. Contoh: `Shopee 3PF` |
| `tpf_tracking_status` | string | ya | The 3PF tracking status for the timestamp. All statuses are in lower case. List of status: - 3pf_warehouse_order_created - 3pf_warehouse_outbound_done Contoh: `3pf_warehouse_outbound_done` |
| `package_list` | object[] | ya |  |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.success_list` | object[] | Update success order list. |
| `response.success_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `response.success_list[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `response.fail_list` | object[] | Update fail order list. |
| `response.fail_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `response.fail_list[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `response.fail_list[].fail_error` | string | Reason for failure. |
| `response.fail_list[].fail_message` | string | Reason for failure. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
