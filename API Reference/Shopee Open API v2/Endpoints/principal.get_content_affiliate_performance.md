# principal.get_content_affiliate_performance

- Path: `/api/v2/principal/get_content_affiliate_performance`
- Method: POST
- Auth: principal
- Deskripsi: Queries affiliate performance data for the specified content items within the selected time range. Supports request granularity by day, week, month, quarter, year, or customize, and returns both overall summary metrics and content-level detailed metrics with placed-order and confirmed-order views.
- Sumber: open.shopee.com/documents/v2/principal.get_content_affiliate_performance?type=1 (backend doc/api) — 2026-09-11
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `start_date` | string | ya | Start date of the requested period in YYYY-MM-DD format. Limitations: - Must use the YYYY-MM-DD format. - Must be a valid calendar date. - Must not be later than end_date. - Validation is based on the requested timezone. - The earliest selectable date is calculated as: current day in timezone - 1 day - 2 years. - The exact boundary rules depend on granularity: -- For customize, start_date must not be earlier than the earliest selectable date. -- For day, start_date must equal end_date. -- For week, start_date must be a Sunday. -- For month, start_date must be the first day of the month. -- For quarter, start_date must be the first day of the quarter. -- For year, start_date must be the first day of the year. Contoh: `2026-01-01` |
| `end_date` | string | ya | End date of the requested period in YYYY-MM-DD format. Limitations: - Must use the YYYY-MM-DD format. - Must be a valid calendar date. - Must not be earlier than start_date. - Validation is based on the requested timezone. - For customize, end_date must not be later than the day before the current day in the requested timezone. The inclusive date range from start_date to end_date must not exceed 366 days. - For day, end_date must equal start_date. - For week, end_date must be within the selected week range: from start_date (Sunday) to the end of that Sunday-to-Saturday week, or to the latest selectable day if the week extends beyond today. Formally: startDate ≤ endDate ≤ min(startDate + 6 days, today - 1 day). - For month, end_date must be within the selected month: from the 1st day of the month to the last calendar day of that month, or to the latest selectable day for the current month. Formally: startDate ≤ endDate ≤ min(month end, today - 1 day). - For quarter, end_date must be within the selected quarter: from the 1st day of the quarter to the last calendar day of that quarter, or to the latest selectable day for the current quarter. Formally: startDate ≤ endDate ≤ min(quarter end, today - 1 day). - For year, end_date must be within the selected year: from January 1st to December 31st of that year, or to the latest selectable day for the current year. Formally: startDate ≤ endDate ≤ min(Dec 31, today - 1 day). Contoh: `2026-01-01` |
| `timezone` | string | ya | Timezone used for date boundary calculation, selectable date validation, and timestamp conversion. Limitations: - Enum values: [\"GMT+7\", \"GMT+8\", \"GMT-3\"] - All date validation rules are evaluated in the requested timezone. Contoh: `GMT+8` |
| `granularity` | string | ya | Aggregation granularity that determines the validation rules for the requested date range and the reporting period. Limitations: - Supported values are customize, day, week, month, quarter, and year. - customize is validated as a free date range and is internally queried as daily data. - day represents a single calendar day. - week requires a Sunday-based calendar week. - month requires a calendar month range. - quarter requires a calendar quarter range. - year requires a calendar year range. - Any other value is rejected as invalid_parameter. Contoh: `day` |
| `content_list` | object[] | tidak | List of shops and content IDs to be queried. Limitations: - If omitted or set to [], the API returns all eligible content under the specified principal_id. - If provided, must contain 1 to 100 shop entries. - Duplicate shop_id values are not allowed. - page_size and cursor are only supported when content_list is omitted or empty. |
| `page_size` | int64 | tidak | Number of detail records to return in the current response page. Limitations: - Only supported when content_list is omitted or an empty array. - Default value is 100. - Must be between 1 and 200, inclusive. Contoh: `100` |
| `cursor` | int64 | tidak | Zero-based offset of the first detail record to return. Limitations: - Only supported when content_list is omitted or an empty array. - Default value is 0. - Must be greater than or equal to 0. Contoh: `0` |

## Request (nested)

_Ditambahkan manual: `fetch_endpoints.py` tidak merender children request._

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `content_list[].shop_id` | int64 | ya | Shop identifier of the target shop to be queried. Limitations: - Required for every shop object in content_list. - Must belong to the specified principal_id. |
| `content_list[].content_ids` | int64[] | ya | List of content IDs under the specified shop_id to be queried. Limitations: - Required for every shop object in content_list. - Must contain 1 to 100 values. - Duplicate content_id values are not allowed within the request. |
| `content_list[].currency` | string | tidak | Currency used for amount-based metrics for the specified content items. Limitations: - Optional for every object in content_list. - Supported values are LOCAL and USD. - Invalid currency values are rejected as invalid_parameter. - Defaults to USD when omitted. |

## Catatan principal

- api_type backend: `Principal`; api_permission: `['Brand Portal Service']` (hanya app tipe Brand Portal Service).
- Common params principal: `partner_id`, `timestamp`, `access_token`, `principal_id`, `sign` (bukan `shop_id`). Panduan: developer guide 733 *Brand Portal Service API Integration Guide*.
- Bila list (region/shop/content/session/video) dikosongkan, API memakai seluruh objek yang bisa diakses principal.

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request, used for troubleshooting and log tracing. |
| `error` | string | Indicate error type if any error happened. Empty string if no error. |
| `message` | string | Indicate error details if any error happened. Empty string if no error. |
| `response` | object | Business response payload. See Business Response Parameters below. |
| `response.summary` | object[] | Aggregated summary metrics for the requested date range, representing the overall affiliate performance of the selected content items. The summary currency is USD when multiple currencies are requested; otherwise it follows the single requested currency, or USD by default. |
| `response.summary[].currency` | string | Currency code used for all amount-based metrics in the summary. |
| `response.summary[].views` | int64 | Total content views generated during the selected period. |
| `response.summary[].likes` | int64 | Total content likes generated during the selected period. |
| `response.summary[].comments` | int64 | Total content comments generated during the selected period. |
| `response.summary[].sales_placed` | float | Total value of placed orders generated through affiliate marketing during the selected period. Placed orders are orders (COD and non-COD) that buyers have successfully placed, including paid and unpaid orders. |
| `response.summary[].sales_confirmed` | float | Total value of confirmed orders generated through affiliate marketing during the selected period. Confirmed orders are either non-Cash On Delivery (non-COD) orders that have been paid for or COD orders that have been confirmed for shipping (usually 30 mins after placing the order). |
| `response.summary[].units_sold_placed` | int64 | Total number of items sold in placed orders generated through affiliate marketing during the selected period. |
| `response.summary[].units_sold_confirmed` | int64 | Total number of items sold in confirmed orders generated through affiliate marketing during the selected period. |
| `response.summary[].orders_placed` | int64 | Total number of placed orders generated through affiliate marketing during the selected period. Placed orders are orders (COD and non-COD) that buyers have successfully placed, including paid and unpaid orders. |
| `response.summary[].orders_confirmed` | int64 | Total number of confirmed orders generated through affiliate marketing during the selected period. Confirmed orders are either non-Cash On Delivery (non-COD) orders that have been paid for or COD orders that have been confirmed for shipping (usually 30 mins after placing the order). |
| `response.details` | object[] | List of content-level detail records that returns affiliate performance metrics for each selected content item within the requested date range. Details are sorted by shop_id and then content_id in ascending order. |
| `response.details[].region` | string | Region code of the shop that owns this content item. |
| `response.details[].currency` | string | Currency code used for all amount-based metrics of this content item. |
| `response.details[].shop_id` | int64 | Shop identifier that owns this content item. |
| `response.details[].shop_name` | string | Shop name that owns this content item. |
| `response.details[].content_id` | int64 | Affiliate content identifier. |
| `response.details[].content_name` | string | Affiliate content name. |
| `response.details[].views` | int64 | Total content views generated during the selected period for this content item. |
| `response.details[].likes` | int64 | Total content likes generated during the selected period for this content item. |
| `response.details[].comments` | int64 | Total content comments generated during the selected period for this content item. |
| `response.details[].sales_placed` | float | Total value of placed orders generated through affiliate marketing during the selected period for this content item. Placed orders are orders (COD and non-COD) that buyers have successfully placed, including paid and unpaid orders. |
| `response.details[].sales_confirmed` | float | Total value of confirmed orders generated through affiliate marketing during the selected period for this content item. Confirmed orders are either non-Cash On Delivery (non-COD) orders that have been paid for or COD orders that have been confirmed for shipping (usually 30 mins after placing the order). |
| `response.details[].units_sold_placed` | int64 | Total number of items sold in placed orders generated through affiliate marketing during the selected period for this content item. |
| `response.details[].units_sold_confirmed` | int64 | Total number of items sold in confirmed orders generated through affiliate marketing during the selected period for this content item. |
| `response.details[].orders_placed` | int64 | Total number of placed orders generated through affiliate marketing during the selected period for this content item. Placed orders are orders (COD and non-COD) that buyers have successfully placed, including paid and unpaid orders. |
| `response.details[].orders_confirmed` | int64 | Total number of confirmed orders generated through affiliate marketing during the selected period for this content item. Confirmed orders are either non-Cash On Delivery (non-COD) orders that have been paid for or COD orders that have been confirmed for shipping (usually 30 mins after placing the order). |
| `response.next_cursor` | int64 | Offset to be used in the next request for fetching the next page of detail records. Notes: - Returned only when content_list is omitted or an empty array. - Calculated as cursor + returned_detail_count. - If returned_detail_count is less than page_size, it indicates there may be no more records. - If the request is already beyond the end of the result set, the API returns 0 detail records and next_cursor remains equal to the input cursor. |

## Catatan

- Common params **principal** (`partner_id`, `timestamp`, `access_token`, `principal_id`, `sign`) wajib — BUKAN `shop_id`/`merchant_id`; sign = HMAC(`partner_id + path + timestamp + access_token + principal_id`). Hanya app tipe **Brand Portal Service**. Panduan: developer guide 733.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
