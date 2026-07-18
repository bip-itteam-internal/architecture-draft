# product.get_size_chart_detail

- Path: `/api/v2/product/get_size_chart_detail`
- Method: GET
- Auth: shop
- Deskripsi: Get new size chart detail. Now only local shop support to use this api to get new size chart detail.
- Sumber: open.shopee.com/documents/v2/product.get_size_chart_detail?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `size_chart_id` | int | ya | ID of new size chart Contoh: `700024639` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Warning message. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.size_chart_id` | int | ID of new size chart |
| `response.size_chart_name` | string | name of new size chart |
| `response.size_chart_table` | object | new size chart is a table format which include multiple columns. each column has column header (measurement) and multiple values (measurement value) of this column. |
| `response.size_chart_table.column_list` | object[] | column list of new size chart table. it include one column (measurement) and multiple values (measurement value) |
| `response.size_chart_table.column_list[].measurement` | object | this is the column header which means a kind of measurement |
| `response.size_chart_table.column_list[].measurement.input_type` | string | there are 3 kinds of measurement type: Single Dropdown, Input Single Number, Input Range Number. |
| `response.size_chart_table.column_list[].measurement.display_name` | string | name of column header (measurement) |
| `response.size_chart_table.column_list[].measurement.unit` | string | the unit of this size measurement. |
| `response.size_chart_table.column_list[].measurement_value_list` | object[] | the list of measurement value |
| `response.size_chart_table.column_list[].measurement_value_list[].value` | float | if the input_type of measurement is single input number, measurement will have one value which is returned by this field. |
| `response.size_chart_table.column_list[].measurement_value_list[].min_value` | float | if the input_type of measurement is input range number, measurement will be a range which is returned by 2 fields: min_value and max_value. |
| `response.size_chart_table.column_list[].measurement_value_list[].max_value` | float | if the input_type of measurement is input range number, measurement will be a range which is returned by 2 fields: min_value and max_value. |
| `response.size_chart_table.column_list[].measurement_value_list[].option` | string | if the input_type of measurement is single dropdown, measurement will have one value which is returned by this field. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
