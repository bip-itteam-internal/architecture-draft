# logistics.get_shipping_document_parameter

- Path: `/api/v2/logistics/get_shipping_document_parameter`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to get the selectable shipping_document_type and suggested shipping_document_type.
- Sumber: open.shopee.com/documents/v2/logistics.get_shipping_document_parameter?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_list` | object[] | ya | The list of orders you want to get. limit [1,50] |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | object[] | Indicate warning message you should take care. |
| `warning[].order_sn` | string | Shopee's unique identifier for an order. |
| `warning[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `response` | object | Detail informations you are querying. |
| `response.result_list` | object[] | The list of the result data. |
| `response.result_list[].order_sn` | string | Shopee's unique identifier for an order. |
| `response.result_list[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `response.result_list[].suggest_shipping_document_type` | string | The shipping document type Shopee suggests. If you don't select any shipping document type, Shopee will use this as default shipping document type. |
| `response.result_list[].selectable_shipping_document_type` | string[] | The shipping document type you can select of this order. |
| `response.result_list[].fail_error` | string | Indicate error type if one element hit error. |
| `response.result_list[].fail_message` | string | Indicate error details if one element hit error. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
