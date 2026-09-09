# principal.get_shop_livestream_performance

- Path: `/api/v2/principal/get_shop_livestream_performance`
- Method: POST
- Auth: principal
- Deskripsi: Queries livestream performance data for the specified shops within the selected time range. Supports request granularity by day, week, month, quarter, year, or customize, and returns both overall summary metrics and shop-level detailed metrics.
- Sumber: open.shopee.com/documents/v2/principal.get_shop_livestream_performance?type=1 (backend doc/api) — 2026-09-09
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `start_date` | string | ya | Start date of the requested period in YYYY-MM-DD format. Limitations: - Must use the YYYY-MM-DD format. - Must be a valid calendar date. - Must not be later than end_date. - Validation is based on the requested timezone. - The earliest selectable date is calculated as: current day in timezone - 1 day - 2 years. - The exact boundary rules depend on granularity: -- For customize, start_date must not be earlier than the earliest selectable date. -- For day, start_date must equal end_date. -- For week, start_date must be a Sunday. -- For month, start_date must be the first day of the month. -- For quarter, start_date must be the first day of the quarter. -- For year, start_date must be the first day of the year. Contoh: `2026-01-01` |
| `end_date` | string | ya | End date of the requested period in YYYY-MM-DD format. Limitations: - Must use the YYYY-MM-DD format. - Must be a valid calendar date. - Must not be earlier than start_date. - Validation is based on the requested timezone. - For customize, end_date must not be later than the day before the current day in the requested timezone. The inclusive date range from start_date to end_date must not exceed 366 days. - For day, end_date must equal start_date. - For week, end_date must be within the selected week range: from start_date (Sunday) to the end of that Sunday-to-Saturday week, or to the latest selectable day if the week extends beyond today. Formally: startDate ≤ endDate ≤ min(startDate + 6 days, today - 1 day). - For month, end_date must be within the selected month: from the 1st day of the month to the last calendar day of that month, or to the latest selectable day for the current month. Formally: startDate ≤ endDate ≤ min(month end, today - 1 day). - For quarter, end_date must be within the selected quarter: from the 1st day of the quarter to the last calendar day of that quarter, or to the latest selectable day for the current quarter. Formally: startDate ≤ endDate ≤ min(quarter end, today - 1 day). - For year, end_date must be within the selected year: from January 1st to December 31st of that year, or to the latest selectable day for the current year. Formally: startDate ≤ endDate ≤ min(Dec 31, today - 1 day). Contoh: `2026-01-01` |
| `timezone` | string | ya | Timezone used for date boundary calculation, selectable date validation, and timestamp conversion. Limitations: - Enum values: [\"GMT+7\", \"GMT+8\", \"GMT-3\"] - The API internally normalizes the open API timezone value for livestream metric queries. - All date validation rules are evaluated in the requested timezone. Contoh: `GMT+8` |
| `granularity` | string | ya | Aggregation granularity that determines the validation rules for the requested date range and the reporting period. Limitations: - Supported values are customize, day, week, month, quarter, and year. - customize is validated as a free date range and is internally queried with the affiliate-compatible livestream granularity. - day represents a single calendar day. - week requires a Sunday-based calendar week. - month requires a calendar month range. - quarter requires a calendar quarter range. - year requires a calendar year range. - Any other value is rejected as invalid_parameter. Contoh: `day` |
| `shop_list` | object[] | tidak | List of shops to be queried. This field is optional. If omitted or passed as an empty array, the API will return data for all shops under the specified principal_id. Limitations: - If provided, must contain at most 50 shops. - If omitted or passed as [], all shops under the specified principal_id will be queried. - If provided as a non-empty array, all shops must belong to the specified principal_id. Duplicate shops are not allowed. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request, used for troubleshooting and log tracing. |
| `error` | string | Indicate error type if any error happened. Empty string if no error. |
| `message` | string | Indicate error details if any error happened. Empty string if no error. |
| `response` | object | Business response payload. See Business Response Parameters below. |
| `response.summary` | object[] | Aggregated summary metrics for the requested date range, representing the overall livestream performance of the requested shop set. Summary values are returned in USD when data exists. |
| `response.summary[].currency` | string | Currency code used for all amount-based metrics in the summary. Summary values are returned in USD. |
| `response.summary[].orders` | int64 | Number of placed orders (paid and unpaid) during your Livestream, including cancelled orders. |
| `response.summary[].buyers` | int64 | Number of unique buyers who placed order from your Livestream. |
| `response.summary[].likes` | int64 | Total number of likes in your Livestream. |
| `response.summary[].comments` | int64 | Total number of comments acquired during your Livestream. |
| `response.summary[].sales_gross` | float | Value of placed orders (paid and unpaid) during your Livestream, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value includes sales from cancelled orders. |
| `response.summary[].units_sold` | int64 | Number of items sold from placed orders during your Livestream. |
| `response.summary[].total_views` | int64 | Total views from your Livestream. |
| `response.summary[].total_live_duration` | int64 | Total duration of your Livestream. |
| `response.summary[].unique_viewers` | int64 | Total unique viewers from your Livestream. |
| `response.summary[].atc_units` | int64 | Number of Add To Cart button clicks for all products in the orange bag during your Livestream. |
| `response.summary[].total_livestreams` | int64 | Total count of Livestream sessions in the selected period. |
| `response.summary[].average_live_duration` | float | Average duration of your Livestream. |
| `response.summary[].average_views_duration` | float | Average time viewers watch your Livestreams. |
| `response.summary[].new_followers` | int64 | Total followers gained from your Livestream. |
| `response.summary[].new_buyers` | int64 | Number of buyers who have not had placed orders (including paid and unpaid) via your Livestream in the past 365 days. |
| `response.summary[].existing_buyers` | int64 | Number of buyers who have already had placed orders (including paid and unpaid) via your Livestream in the past 365 days. |
| `response.summary[].sales_net` | float | Value of placed orders (paid and unpaid) during your Livestream, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value excludes the refund amount for all non-cancelled and invalid items. |
| `response.summary[].conversion_rate` | float | Livestream orders / Livestream views. |
| `response.details` | object[] | List of shop-level detail records that returns livestream performance metrics for each selected shop within the requested date range. |
| `response.details[].region` | string | Region code of the shop. |
| `response.details[].currency` | string | Currency code used for all amount-based metrics of this shop item. |
| `response.details[].orders` | int64 | Number of placed orders (paid and unpaid) during your Livestream, including cancelled orders. |
| `response.details[].buyers` | int64 | Number of unique buyers who placed order from your Livestream. |
| `response.details[].likes` | int64 | Total number of likes in your Livestream. |
| `response.details[].comments` | int64 | Total number of comments acquired during your Livestream. |
| `response.details[].shop_id` | int64 | Shop identifier. |
| `response.details[].shop_name` | string | Shop name. |
| `response.details[].sales_gross` | float | Value of placed orders (paid and unpaid) during your Livestream, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value includes sales from cancelled orders. |
| `response.details[].units_sold` | int64 | Number of items sold from placed orders during your Livestream. |
| `response.details[].total_views` | int64 | Total views from your Livestream. |
| `response.details[].total_live_duration` | int64 | Total duration of your Livestream. |
| `response.details[].unique_viewers` | int64 | Total unique viewers from your Livestream. |
| `response.details[].atc_units` | int64 | Number of Add To Cart button clicks for all products in the orange bag during your Livestream. |
| `response.details[].total_livestreams` | int64 | Total count of Livestream sessions in the selected period. |
| `response.details[].average_live_duration` | float | Average duration of your Livestream. |
| `response.details[].average_views_duration` | float | Average time viewers watch your Livestreams. |
| `response.details[].new_followers` | int64 | Total followers gained from your Livestream. |
| `response.details[].new_buyers` | int64 | Number of buyers who have not had placed orders (including paid and unpaid) via your Livestream in the past 365 days. |
| `response.details[].existing_buyers` | int64 | Number of buyers who have already had placed orders (including paid and unpaid) via your Livestream in the past 365 days. |
| `response.details[].sales_net` | float | Value of placed orders (paid and unpaid) during your Livestream, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value excludes the refund amount for all non-cancelled and invalid items. |
| `response.details[].conversion_rate` | float | Livestream orders / Livestream views. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
