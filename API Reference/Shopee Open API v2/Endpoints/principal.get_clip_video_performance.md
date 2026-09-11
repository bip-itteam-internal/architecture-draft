# principal.get_clip_video_performance

- Path: `/api/v2/principal/get_clip_video_performance`
- Method: POST
- Auth: principal
- Deskripsi: Queries video clip performance data for the specified videos within the selected time range. Supports request granularity by day, week, month, quarter, year, or customize, and returns both overall summary metrics and video-level detailed metrics.
- Sumber: open.shopee.com/documents/v2/principal.get_clip_video_performance?type=1 (backend doc/api) — 2026-09-11
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `start_date` | string | ya | Start date of the requested period in YYYY-MM-DD format. Limitations: - Must use the YYYY-MM-DD format. - Must be a valid calendar date. - Must not be later than end_date. - Validation is based on the requested timezone. - The earliest selectable date is calculated as: current day in timezone - 1 day - 2 years. - The exact boundary rules depend on granularity: -- For customize, start_date must not be earlier than the earliest selectable date. -- For day, start_date must equal end_date. -- For week, start_date must be a Sunday. -- For month, start_date must be the first day of the month. -- For quarter, start_date must be the first day of the quarter. -- For year, start_date must be the first day of the year. Contoh: `2026-01-01` |
| `end_date` | string | ya | End date of the requested period in YYYY-MM-DD format. Limitations: - Must use the YYYY-MM-DD format. - Must be a valid calendar date. - Must not be earlier than start_date. - Validation is based on the requested timezone. - For customize, end_date must not be later than the day before the current day in the requested timezone. The inclusive date range from start_date to end_date must not exceed 366 days. - For day, end_date must equal start_date. - For week, end_date must be within the selected week range: from start_date (Sunday) to the end of that Sunday-to-Saturday week, or to the latest selectable day if the week extends beyond today. Formally: startDate ≤ endDate ≤ min(startDate + 6 days, today - 1 day). - For month, end_date must be within the selected month: from the 1st day of the month to the last calendar day of that month, or to the latest selectable day for the current month. Formally: startDate ≤ endDate ≤ min(month end, today - 1 day). - For quarter, end_date must be within the selected quarter: from the 1st day of the quarter to the last calendar day of that quarter, or to the latest selectable day for the current quarter. Formally: startDate ≤ endDate ≤ min(quarter end, today - 1 day). - For year, end_date must be within the selected year: from January 1st to December 31st of that year, or to the latest selectable day for the current year. Formally: startDate ≤ endDate ≤ min(Dec 31, today - 1 day). Contoh: `2026-01-31` |
| `timezone` | string | ya | Timezone used for date boundary calculation, selectable date validation, and timestamp conversion. Limitations: - Enum values: [\"GMT+7\", \"GMT+8\", \"GMT-3\"] - The API internally normalizes the open API timezone value for video metric queries. - All date validation rules are evaluated in the requested timezone. Contoh: `GMT+8` |
| `granularity` | string | ya | Aggregation granularity that determines the validation rules for the requested date range and the reporting period. Limitations: - Supported values are customize, day, week, month, quarter, and year. - customize is validated as a free date range. - day represents a single calendar day. - week requires a Sunday-based calendar week. - month requires a calendar month range. - quarter requires a calendar quarter range. - year requires a calendar year range. - Any other value is rejected as invalid_parameter. Contoh: `month` |
| `video_list` | object[] | tidak | List of video clip query targets. Limitations: - Must contain at least one object. - Must contain at most 100 objects. - Every shop_id must belong to the specified principal_id. - Duplicate shop_id values are rejected. - Each object must provide a non-empty video_ids list. - Null video_id values are rejected. - Duplicate video_id values across the whole request are rejected. - The total number of unique video_ids across the whole request must not exceed 100. |
| `page_size` | int64 | tidak | Number of detail records to return in the current response page. Limitations: - Only supported when video_list is omitted or an empty array. - Default value is 100. - Must be between 1 and 200, inclusive. Contoh: `100` |
| `cursor` | int64 | tidak | Zero-based offset of the first detail record to return. Limitations: - Only supported when video_list is omitted or an empty array. - Default value is 0. - Must be greater than or equal to 0. Contoh: `100` |

## Request (nested)

_Ditambahkan manual: `fetch_endpoints.py` tidak merender children request._

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `video_list[].shop_id` | int64 | ya | Shop identifier that owns the specified videos. Limitations: - Required for every object in video_list. - Must belong to the specified principal_id. |
| `video_list[].video_ids` | int64[] | ya | List of video identifiers to be queried under the specified shop. Limitations: - Required for every object in video_list. - Must contain at least one video_id. - Must contain at most 100 video_ids per object. - Null video_id values are rejected. - Duplicate video_id values across the whole request are rejected. - Across the whole request, the total number of unique video_ids must not exceed 100. |
| `video_list[].currency` | string | tidak | Currency used for amount-based metrics for the specified videos. Limitations: - Optional for every object in video_list. - Supported values are LOCAL and USD. - Invalid currency values are rejected as invalid_parameter. - Defaults to USD when omitted. |

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
| `response.summary` | object[] | Aggregated summary metrics for the requested date range, representing the overall performance of the selected videos. Note: - unique_viewers and total_unique_buyers are unavailable for customize, month, quarter, year, and non-full-week weekly ranges. |
| `response.summary[].currency` | string | Currency code used for all amount-based metrics in the summary. |
| `response.summary[].total_views` | int64 | Total views from the selected videos. |
| `response.summary[].unique_viewers` | int64 | Number of video viewers in the selected period. Note: This data is unavailable when you select by month, by quarter, by year, customize date, or a non-full weekly range. |
| `response.summary[].video_duration` | float | Video duration in minutes. |
| `response.summary[].average_views_duration` | float | Average viewing duration per video in minutes. |
| `response.summary[].likes` | int64 | Number of Like clicks from the selected videos. |
| `response.summary[].comments` | int64 | Number of comments generated from the selected videos. |
| `response.summary[].share` | int64 | Number of shares created from the selected videos. |
| `response.summary[].total_unique_buyers` | int64 | Number of unique buyers who placed order from the selected videos. Note: This data is unavailable when you select by month, by quarter, by year, customize date, or a non-full weekly range. |
| `response.summary[].atc_units` | int64 | Number of Add To Cart button clicks for all products in the orange bag during the selected videos. |
| `response.summary[].units_sold` | int64 | Number of items sold from placed orders during the selected videos. |
| `response.summary[].orders` | int64 | Number of placed orders (paid and unpaid) during the selected videos, including cancelled orders. |
| `response.summary[].sales` | float | Value of placed orders (paid and unpaid) from the selected videos in the period, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value includes sales from cancelled and return/refund orders. |
| `response.summary[].conversion_rate` | float | Video orders / total video views. |
| `response.details` | object[] | List of video-level detail records that returns performance metrics for each selected video within the requested date range. Details are sorted by shop_id and then video_id in ascending order. - unique_viewers and total_unique_buyers are unavailable for customize, month, quarter, year, and non-full-week weekly ranges. |
| `response.details[].region` | string | Region code of the shop that owns this video. |
| `response.details[].currency` | string | Currency code used for all amount-based metrics of this video item. |
| `response.details[].shop_id` | int64 | Shop identifier that owns this video. |
| `response.details[].shop_name` | string | Shop name that owns this video. |
| `response.details[].video_id` | int64 | Video identifier. |
| `response.details[].video_name` | string | Video name. |
| `response.details[].total_views` | int64 | Total views from this video. |
| `response.details[].unique_viewers` | int64 | Number of video viewers in the selected period. Note: This data is unavailable when you select by month, by quarter, by year, customize date, or a non-full weekly range. |
| `response.details[].video_duration` | float | Video duration in minutes. |
| `response.details[].average_views_duration` | float | Average viewing duration per video in minutes. |
| `response.details[].likes` | int64 | Number of Like clicks from this video. |
| `response.details[].comments` | int64 | Number of comments generated from this video. |
| `response.details[].share` | int64 | Number of shares created from this video. |
| `response.details[].total_unique_buyers` | int64 | Number of unique buyers who placed order from this video. Note: This data is unavailable when you select by month, by quarter, by year, customize date, or a non-full weekly range. |
| `response.details[].atc_units` | int64 | Number of Add To Cart button clicks for all products in the orange bag during this video. |
| `response.details[].units_sold` | int64 | Number of items sold from placed orders during this video. |
| `response.details[].orders` | int64 | Number of placed orders (paid and unpaid) during this video, including cancelled orders. |
| `response.details[].sales` | float | Value of placed orders (paid and unpaid) from this video in the period, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value includes sales from cancelled and return/refund orders. |
| `response.details[].conversion_rate` | float | Video orders / total video views. |
| `response.next_cursor` | int64 | Offset to be used in the next request for fetching the next page of detail records. Notes: - Returned only when video_list is omitted or an empty array. - Calculated as cursor + returned_detail_count. - If returned_detail_count is less than page_size, it indicates there may be no more records. - If the request is already beyond the end of the result set, the API returns 0 detail records and next_cursor remains equal to the input cursor. |

## Catatan

- Common params **principal** (`partner_id`, `timestamp`, `access_token`, `principal_id`, `sign`) wajib — BUKAN `shop_id`/`merchant_id`; sign = HMAC(`partner_id + path + timestamp + access_token + principal_id`). Hanya app tipe **Brand Portal Service**. Panduan: developer guide 733.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
