# principal.get_principal_sales_performance_detail

- Path: `/api/v2/principal/get_principal_sales_performance_detail`
- Method: POST
- Auth: principal
- Deskripsi: Queries the business performance data aggregated at principal level for the specified regions within the selected time range. Supports request granularity by day, week, month, quarter, year, or customize, and returns both overall summary metrics and region-level detailed metrics.
- Sumber: open.shopee.com/documents/v2/principal.get_principal_sales_performance_detail?type=1 (backend doc/api) — 2026-09-11
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `start_date` | string | ya | Start date of the requested period in YYYY-MM-DD format. Limitations: - Must use the YYYY-MM-DD format. - Must be a valid calendar date. - Must not be later than end_date. - Validation is based on the requested timezone. - The earliest selectable date is calculated as: current day in timezone - 1 day - 2 years. - The exact boundary rules depend on granularity: -- For customize, start_date must not be earlier than the earliest selectable date. -- For day, start_date must equal end_date. -- For week, start_date must be a Sunday. -- For month, start_date must be the first day of the month. -- For quarter, start_date must be the first day of the quarter. -- For year, start_date must be the first day of the year. Contoh: `2026-01-01` |
| `end_date` | string | ya | End date of the requested period in YYYY-MM-DD format. Limitations: - Must use the YYYY-MM-DD format. - Must be a valid calendar date. - Must not be earlier than start_date. - Validation is based on the requested timezone. - For customize, end_date must not be later than the day before the current day in the requested timezone. The inclusive date range from start_date to end_date must not exceed 366 days. - For day, end_date must equal start_date. - For week, end_date must be within the selected week range: from start_date (Sunday) to the end of that Sunday-to-Saturday week, or to the latest selectable day if the week extends beyond today. Formally: startDate ≤ endDate ≤ min(startDate + 6 days, today - 1 day). - For month, end_date must be within the selected month: from the 1st day of the month to the last calendar day of that month, or to the latest selectable day for the current month. Formally: startDate ≤ endDate ≤ min(month end, today - 1 day). - For quarter, end_date must be within the selected quarter: from the 1st day of the quarter to the last calendar day of that quarter, or to the latest selectable day for the current quarter. Formally: startDate ≤ endDate ≤ min(quarter end, today - 1 day). - For year, end_date must be within the selected year: from January 1st to December 31st of that year, or to the latest selectable day for the current year. Formally: startDate ≤ endDate ≤ min(Dec 31, today - 1 day). Contoh: `2026-01-01` |
| `timezone` | string | ya | Timezone used for date boundary calculation, selectable date validation, and timestamp conversion. Limitations: - Enum values: [\"GMT+7\", \"GMT+8\", \"GMT-3\"] - All date validation rules are evaluated in the requested timezone. Contoh: `GMT+8` |
| `granularity` | string | ya | Aggregation granularity that determines the validation rules for the requested date range and the reporting period. Limitations: - Supported values are customize, day, week, month, quarter, and year. - customize is validated as a free date range and is internally queried as daily data. - day represents a single calendar day. - week requires a Sunday-based calendar week. - month requires a calendar month range. - quarter requires a calendar quarter range. - year requires a calendar year range. - Any other value is rejected as invalid_parameter. Contoh: `day` |
| `region_list` | object[] | tidak | List of principal regions to be queried. Limitations: - Optional. If omitted or empty, the API queries all regions that belong to the specified principal. - Duplicate region entries are deduplicated internally. - The same region must not appear multiple times with different currency values. |

## Request (nested)

_Ditambahkan manual: `fetch_endpoints.py` tidak merender children request._

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `region_list[].region` | string | ya | Target region code of the principal to be queried. Limitations: - Required for every region object in region_list. - Must be a valid region code or region name recognized by the API, such as SG or ID. |
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
| `response.summary` | object[] | Aggregated summary metrics for the requested date range and selected granularity, representing the overall performance of the requested principal across the selected regions. |
| `response.summary[].currency` | string | Currency code used for all monetary metrics in the summary. When multiple regions are requested, the summary currency is always USD. When exactly one region is requested, the summary currency follows that region's requested currency. |
| `response.summary[].sales` | float | Total order value (paid and unpaid) within the selected time period, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value includes sales from cancelled and return/refund orders. |
| `response.summary[].orders` | int64 | The number of placed orders, including unpaid orders. |
| `response.summary[].units_sold` | int64 | The number of units associated with the orders placed, including unpaid orders. |
| `response.summary[].average_basket_size` | float | Average Basket Size = Sales ÷ Orders. It measures average sales per order. |
| `response.summary[].items_per_order` | float | Items Per Order = Units Sold ÷ Orders. It measures the average number of items sold per transaction. |
| `response.summary[].average_selling_price` | float | Average selling price = Sales ÷ Units Sold. It measures average sales per unit. |
| `response.summary[].product_clicks` | int64 | Total number of times your item cards were clicked over the selected time period, on both App and PC. This metric is only available after 31/12/2023. |
| `response.summary[].product_views` | int64 | The number of visits to the product page. |
| `response.summary[].unique_visitors` | int64 | Total number of unique visitors who viewed your shop or product pages over the selected time period. Multiple views by the same visitor are counted as 1 unique visitor. This metric is only available after 31/12/2023. |
| `response.summary[].item_conversion_rate` | float | Item conversion rate = Units Sold ÷ Product Views. |
| `response.summary[].order_conversion_rate` | float | Number of orders divided by total number of product clicks over the selected time period. This metric is only available after 31/12/2023. |
| `response.details` | object[] | List of region-level detail records that returns performance metrics for each selected region within the requested date range. |
| `response.details[].region` | string | Region code. |
| `response.details[].currency` | string | Currency code used for all monetary metrics of this region item. |
| `response.details[].sales` | float | Total order value (paid and unpaid) within the selected time period, reflecting the sales amount received by sellers after deducting seller rebates. Note: This value includes sales from cancelled and return/refund orders. |
| `response.details[].orders` | int64 | The number of placed orders, including unpaid orders. |
| `response.details[].units_sold` | int64 | The number of units associated with the orders placed, including unpaid orders. |
| `response.details[].average_basket_size` | float | Average Basket Size = Sales ÷ Orders. It measures average sales per order. |
| `response.details[].items_per_order` | float | Items Per Order = Units Sold ÷ Orders. It measures the average number of items sold per transaction. |
| `response.details[].average_selling_price` | float | Average selling price = Sales ÷ Units Sold. It measures average sales per unit. |
| `response.details[].product_clicks` | int64 | Total number of times your item cards were clicked over the selected time period, on both App and PC. This metric is only available after 31/12/2023. |
| `response.details[].product_views` | int64 | The number of visits to the product page. |
| `response.details[].unique_visitors` | int64 | Total number of unique visitors who viewed your shop or product pages over the selected time period. Multiple views by the same visitor are counted as 1 unique visitor. This metric is only available after 31/12/2023. |
| `response.details[].item_conversion_rate` | float | Item conversion rate = Units Sold ÷ Product Views. |
| `response.details[].order_conversion_rate` | float | Number of orders divided by total number of product clicks over the selected time period. This metric is only available after 31/12/2023. |

## Catatan

- Common params **principal** (`partner_id`, `timestamp`, `access_token`, `principal_id`, `sign`) wajib — BUKAN `shop_id`/`merchant_id`; sign = HMAC(`partner_id + path + timestamp + access_token + principal_id`). Hanya app tipe **Brand Portal Service**. Panduan: developer guide 733.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
