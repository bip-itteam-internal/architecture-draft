# principal.get_principal_video_performance

- Path: `/api/v2/principal/get_principal_video_performance`
- Method: POST
- Auth: principal
- Deskripsi: Queries video performance data for the specified principal within the selected time range. Supports request granularity by day, week, month, quarter, year, or customize, and returns both overall summary metrics and region-level detailed metrics.
- Sumber: open.shopee.com/documents/v2/principal.get_principal_video_performance?type=1 (backend doc/api) — 2026-09-11
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `start_date` | string | ya | Start date of the requested period in YYYY-MM-DD format. Limitations: - Must use the YYYY-MM-DD format. - Must be a valid calendar date. - Must not be later than end_date. - Validation is based on the requested timezone. - The earliest selectable date is calculated as: current day in timezone - 1 day - 2 years. - The exact boundary rules depend on granularity: -- For customize, start_date must not be earlier than the earliest selectable date. -- For day, start_date must equal end_date. -- For week, start_date must be a Sunday. -- For month, start_date must be the first day of the month. -- For quarter, start_date must be the first day of the quarter. -- For year, start_date must be the first day of the year. Contoh: `2026-01-01` |
| `end_date` | string | ya | End date of the requested period in YYYY-MM-DD format. Limitations: - Must use the YYYY-MM-DD format. - Must be a valid calendar date. - Must not be earlier than start_date. - Validation is based on the requested timezone. - For customize, end_date must not be later than the day before the current day in the requested timezone. The inclusive date range from start_date to end_date must not exceed 366 days. - For day, end_date must equal start_date. - For week, end_date must be within the selected week range: from start_date (Sunday) to the end of that Sunday-to-Saturday week, or to the latest selectable day if the week extends beyond today. Formally: startDate ≤ endDate ≤ min(startDate + 6 days, today - 1 day). - For month, end_date must be within the selected month: from the 1st day of the month to the last calendar day of that month, or to the latest selectable day for the current month. Formally: startDate ≤ endDate ≤ min(month end, today - 1 day). - For quarter, end_date must be within the selected quarter: from the 1st day of the quarter to the last calendar day of that quarter, or to the latest selectable day for the current quarter. Formally: startDate ≤ endDate ≤ min(quarter end, today - 1 day). - For year, end_date must be within the selected year: from January 1st to December 31st of that year, or to the latest selectable day for the current year. Formally: startDate ≤ endDate ≤ min(Dec 31, today - 1 day). Contoh: `2026-01-31` |
| `timezone` | string | ya | Timezone used for date boundary calculation, selectable date validation, and timestamp conversion. Limitations: - Enum values: [\"GMT+7\", \"GMT+8\", \"GMT-3\"] - The API internally normalizes the open API timezone value for video metric queries. - All date validation rules are evaluated in the requested timezone. Contoh: `GMT+8` |
| `granularity` | string | ya | Aggregation granularity that determines the validation rules for the requested date range and the reporting period. Limitations: - Supported values are customize, day, week, month, quarter, and year. - customize is validated as a free date range. - day represents a single calendar day. - week requires a Sunday-based calendar week. - month requires a calendar month range. - quarter requires a calendar quarter range. - year requires a calendar year range. - Any other value is rejected as invalid_parameter. Contoh: `month` |
| `region_list` | object[] | tidak | Optional list of principal regions to be queried. Limitations: - When omitted or empty, the API queries all regions belonging to the specified principal_id except the aggregate regional bucket. - Must contain at most 100 region objects. - Every region must belong to the specified principal_id. - Duplicate region values are merged when they use the same currency. - The same region cannot appear with different currencies. - Currency defaults to USD when omitted. |

## Request (nested)

_Ditambahkan manual: `fetch_endpoints.py` tidak merender children request._

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `region_list[].region` | string | ya | Region code to be queried. Limitations: - Required for every region object in region_list. - Must be a valid region code supported by the API. - Must belong to the specified principal_id. |
| `region_list[].currency` | string | tidak | Currency used for amount-based metrics for the region. Limitations: - Optional for every region object in region_list. - Supported values are LOCAL and USD. - Invalid currency values are rejected as invalid_parameter. - Defaults to USD when omitted. |

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
| `response.summary` | object[] | Aggregated summary metrics for the requested date range, representing the overall video performance of the selected principal. Summary values are returned in USD when data exists. Note: - total_video_duration is returned only in summary. - unique_viewers and total_unique_buyers are unavailable for customize, month, quarter, year, and non-full-week weekly ranges. |
| `response.summary[].currency` | string | Currency code used for all amount-based metrics in the summary. Summary values are returned in USD. |
| `response.summary[].orders` | int64 | Number of placed orders (paid and unpaid) during your Video, including cancelled orders. |
| `response.summary[].likes` | int64 | Number of Like clicks from all videos. |
| `response.summary[].comments` | int64 | Number of comments generated from all videos. |
| `response.summary[].share` | int64 | Number of shares created from all videos. |
| `response.summary[].sales` | float | Value of placed orders (paid and unpaid) from all videos in the period, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value includes sales from cancelled and return/refund orders. |
| `response.summary[].units_sold` | int64 | Number of items sold from placed orders during your Video. |
| `response.summary[].effective_views` | int64 | Number of views from the video that lasted for more than 3 seconds. |
| `response.summary[].unique_viewers` | int64 | Number of video viewers in the selected period. Note: This data is unavailable when you select by month, by quarter, by year, customize date, or a non-full weekly range. |
| `response.summary[].total_video_duration` | float | Total duration of your videos in minutes. This field is returned only in summary. |
| `response.summary[].atc_units` | int64 | Number of Add To Cart button clicks for all products in the orange bag during your Video. |
| `response.summary[].average_video_duration` | float | Average duration of your videos in minutes. |
| `response.summary[].average_views_duration` | float | Average viewing duration per video in minutes. |
| `response.summary[].total_unique_buyers` | int64 | Number of unique buyers who placed order from your Video. Note: This data is unavailable when you select by month, by quarter, by year, customize date, or a non-full weekly range. |
| `response.summary[].conversion_rate` | float | Video orders / effective video views. |
| `response.details` | object[] | List of region-level detail records that returns video performance metrics for each selected region within the requested date range. Note: - details do not include total_video_duration. - unique_viewers and total_unique_buyers are unavailable for customize, month, quarter, year, and non-full-week weekly ranges. |
| `response.details[].region` | string | Region code of this detail item. |
| `response.details[].currency` | string | Currency code used for all amount-based metrics of this region item. |
| `response.details[].orders` | int64 | Number of placed orders (paid and unpaid) during your Video, including cancelled orders. |
| `response.details[].likes` | int64 | Number of Like clicks from all videos. |
| `response.details[].comments` | int64 | Number of comments generated from all videos. |
| `response.details[].share` | int64 | Number of shares created from all videos. |
| `response.details[].sales` | float | Value of placed orders (paid and unpaid) from all videos in the period, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value includes sales from cancelled and return/refund orders. |
| `response.details[].units_sold` | int64 | Number of items sold from placed orders during your Video. |
| `response.details[].effective_views` | int64 | Number of views from the video that lasted for more than 3 seconds. |
| `response.details[].unique_viewers` | int64 | Number of video viewers in the selected period. Note: This data is unavailable when you select by month, by quarter, by year, customize date, or a non-full weekly range. |
| `response.details[].atc_units` | int64 | Number of Add To Cart button clicks for all products in the orange bag during your Video. |
| `response.details[].average_video_duration` | float | Average duration of your videos in minutes. |
| `response.details[].average_views_duration` | float | Average viewing duration per video in minutes. |
| `response.details[].total_unique_buyers` | int64 | Number of unique buyers who placed order from your Video. Note: This data is unavailable when you select by month, by quarter, by year, customize date, or a non-full weekly range. |
| `response.details[].conversion_rate` | float | Video orders / effective video views. |

## Catatan

- Common params **principal** (`partner_id`, `timestamp`, `access_token`, `principal_id`, `sign`) wajib — BUKAN `shop_id`/`merchant_id`; sign = HMAC(`partner_id + path + timestamp + access_token + principal_id`). Hanya app tipe **Brand Portal Service**. Panduan: developer guide 733.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
