# principal.get_session_livestream_performance

- Path: `/api/v2/principal/get_session_livestream_performance`
- Method: POST
- Auth: principal
- Deskripsi: Queries livestream session performance data for the specified sessions within the selected time range. Supports request granularity by day, week, month, quarter, year, or customize, and returns both overall summary metrics and session-level detailed metrics.
- Sumber: open.shopee.com/documents/v2/principal.get_session_livestream_performance?type=1 (backend doc/api) — 2026-09-09
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `start_date` | string | ya | Start date of the requested period in YYYY-MM-DD format. Limitations: - Must use the YYYY-MM-DD format. - Must be a valid calendar date. - Must not be later than end_date. - Validation is based on the requested timezone. - The earliest selectable date is calculated as: current day in timezone - 1 day - 2 years. - The exact boundary rules depend on granularity: -- For customize, start_date must not be earlier than the earliest selectable date. -- For day, start_date must equal end_date. -- For week, start_date must be a Sunday. -- For month, start_date must be the first day of the month. -- For quarter, start_date must be the first day of the quarter. -- For year, start_date must be the first day of the year. Contoh: `2026-01-01` |
| `end_date` | string | ya | End date of the requested period in YYYY-MM-DD format. Limitations: - Must use the YYYY-MM-DD format. - Must be a valid calendar date. - Must not be earlier than start_date. - Validation is based on the requested timezone. - For customize, end_date must not be later than the day before the current day in the requested timezone. The inclusive date range from start_date to end_date must not exceed 366 days. - For day, end_date must equal start_date. - For week, end_date must be within the selected week range: from start_date (Sunday) to the end of that Sunday-to-Saturday week, or to the latest selectable day if the week extends beyond today. Formally: startDate ≤ endDate ≤ min(startDate + 6 days, today - 1 day). - For month, end_date must be within the selected month: from the 1st day of the month to the last calendar day of that month, or to the latest selectable day for the current month. Formally: startDate ≤ endDate ≤ min(month end, today - 1 day). - For quarter, end_date must be within the selected quarter: from the 1st day of the quarter to the last calendar day of that quarter, or to the latest selectable day for the current quarter. Formally: startDate ≤ endDate ≤ min(quarter end, today - 1 day). - For year, end_date must be within the selected year: from January 1st to December 31st of that year, or to the latest selectable day for the current year. Formally: startDate ≤ endDate ≤ min(Dec 31, today - 1 day). Contoh: `2026-01-31` |
| `timezone` | string | ya | Timezone used for date boundary calculation, selectable date validation, and timestamp conversion. Limitations: - Enum values: [\"GMT+7\", \"GMT+8\", \"GMT-3\"] - The API internally normalizes the open API timezone value for livestream metric queries. - All date validation rules are evaluated in the requested timezone. Contoh: `GMT+8` |
| `granularity` | string | ya | Aggregation granularity that determines the validation rules for the requested date range and the reporting period. Limitations: - Supported values are customize, day, week, month, quarter, and year. - customize is validated as a free date range and is internally queried with the affiliate-compatible livestream granularity. - day represents a single calendar day. - week requires a Sunday-based calendar week. - month requires a calendar month range. - quarter requires a calendar quarter range. - year requires a calendar year range. - Any other value is rejected as invalid_parameter. Contoh: `month` |
| `session_list` | object[] | tidak | List of livestream session query targets. Limitations: - Must contain at least one object. - Must contain at most 100 objects. - Every shop_id must belong to the specified principal_id. - Duplicate shop_id values are rejected. - Each object must provide a non-empty session_ids list. - Null session_id values are rejected. - Duplicate session_id values across the whole request are rejected. - The total number of unique session_ids across the whole request must not exceed 100. |
| `page_size` | int64 | tidak | Number of detail records to return in the current response page. Limitations: - Only supported when session_list is omitted or an empty array. - Default value is 100. - Must be between 1 and 200, inclusive. Contoh: `100` |
| `cursor` | int64 | tidak | Zero-based offset of the first detail record to return. Limitations: - Only supported when session_list is omitted or an empty array. - Default value is 0. - Must be greater than or equal to 0. Contoh: `0` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request, used for troubleshooting and log tracing. |
| `error` | string | Indicate error type if any error happened. Empty string if no error. |
| `message` | string | Indicate error details if any error happened. Empty string if no error. |
| `response` | object | Business response payload. See Business Response Parameters below. |
| `response.summary` | object[] | Aggregated summary metrics for the requested date range, representing the overall livestream session performance of the selected sessions. Summary values are returned in USD when data exists. |
| `response.summary[].currency` | string | Currency code used for all amount-based metrics in the summary. Summary values are returned in USD. |
| `response.summary[].likes` | int64 | Total number of likes in the selected livestream sessions. |
| `response.summary[].comments` | int64 | Total number of comments acquired during the selected livestream sessions. |
| `response.summary[].buyers` | int64 | Number of unique buyers who placed orders from the selected livestream sessions. |
| `response.summary[].orders` | int64 | Number of placed orders (paid and unpaid) during the selected livestream sessions, including cancelled orders. |
| `response.summary[].total_views` | int64 | Total views from the selected livestream sessions. |
| `response.summary[].unique_viewers` | int64 | Total unique viewers from the selected livestream sessions. |
| `response.summary[].total_live_duration` | int64 | Total duration of the selected livestream sessions. |
| `response.summary[].average_views_duration` | float | Average time viewers watch the selected livestream sessions. |
| `response.summary[].new_followers` | int64 | Total followers gained from the selected livestream sessions. |
| `response.summary[].atc_units` | int64 | Number of Add To Cart button clicks for all products in the orange bag during the selected livestream sessions. |
| `response.summary[].units_sold` | int64 | Number of items sold from placed orders during the selected livestream sessions. |
| `response.summary[].sales_gross` | float | Value of placed orders (paid and unpaid) during the selected livestream sessions, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value includes sales from cancelled orders. |
| `response.summary[].sales_net` | float | Value of placed orders (paid and unpaid) during the selected livestream sessions, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value excludes the refund amount for all non-cancelled and invalid items. |
| `response.summary[].conversion_rate` | float | Livestream orders / Livestream views. |
| `response.details` | object[] | List of livestream session-level detail records that returns performance metrics for each selected session within the requested date range. |
| `response.details[].region` | string | Region code of the shop that owns this livestream session. |
| `response.details[].currency` | string | Currency code used for all amount-based metrics of this livestream session item. |
| `response.details[].likes` | int64 | Total number of likes in this livestream session. |
| `response.details[].comments` | int64 | Total number of comments acquired during this livestream session. |
| `response.details[].buyers` | int64 | Number of unique buyers who placed orders from this livestream session. |
| `response.details[].orders` | int64 | Number of placed orders (paid and unpaid) during this livestream session, including cancelled orders. |
| `response.details[].shop_id` | int64 | Shop identifier that owns this livestream session. |
| `response.details[].shop_name` | string | Shop name that owns this livestream session. |
| `response.details[].session_id` | int64 | Livestream session identifier. |
| `response.details[].session_name` | string | Livestream session name. |
| `response.details[].total_views` | int64 | Total views from this livestream session. |
| `response.details[].unique_viewers` | int64 | Total unique viewers from this livestream session. |
| `response.details[].total_live_duration` | int64 | Total duration of this livestream session. |
| `response.details[].average_views_duration` | float | Average time viewers watch this livestream session. |
| `response.details[].new_followers` | int64 | Total followers gained from this livestream session. |
| `response.details[].atc_units` | int64 | Number of Add To Cart button clicks for all products in the orange bag during this livestream session. |
| `response.details[].units_sold` | int64 | Number of items sold from placed orders during this livestream session. |
| `response.details[].sales_gross` | float | Value of placed orders (paid and unpaid) during this livestream session, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value includes sales from cancelled orders. |
| `response.details[].sales_net` | float | Value of placed orders (paid and unpaid) during this livestream session, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value excludes the refund amount for all non-cancelled and invalid items. |
| `response.details[].conversion_rate` | float | Livestream orders / Livestream views. |
| `response.next_cursor` | int64 | Offset to be used in the next request for fetching the next page of detail records. Notes: - Returned only when session_list is omitted or an empty array. - Calculated as cursor + returned_detail_count. - If returned_detail_count is less than page_size, it indicates there may be no more records. - If the request is already beyond the end of the result set, the API returns 0 detail records and next_cursor remains equal to the input cursor. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
