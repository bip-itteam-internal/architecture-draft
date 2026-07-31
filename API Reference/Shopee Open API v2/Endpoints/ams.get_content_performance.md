# ams.get_content_performance

- Path: `/api/v2/ams/get_content_performance`
- Method: GET
- Auth: shop
- Deskripsi: Retrieve content performance of the shop
- Sumber: open.shopee.com/documents/v2/ams.get_content_performance?type=1 (backend doc/api) — 2026-07-31
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `period_type` | string | ya | Period Type. Applicable values: Day Week Month Last7d Last30d Note: The start date and end date must align with the Period Type. Contoh: `Last30d` |
| `start_date` | string | ya | The start_date must be: - Any day in the past three calendar months for "Day" period type - Sunday for "Week" period type - The 1st day of a Month for "Month" period type - The date that is 6 days prior to the latest data date for "Last7d" period type - The date that is 29 days prior to the latest data date for "Last30d" period type Note: The latest data date can be obtained by using "AmsMarker" in the v2.ams.get_performance_data_update_time API. Contoh: `20250801` |
| `end_date` | string | ya | The end_date must be: - Equal to start_date for "Day" period type - Saturday for "Week" period type - The last day of a Month for "Month" period type. If the selected month is the current month, the end_date should be the latest data date - The latest data date for "Last7d" period type - The latest data date for "Last30d" period type Note: - The end_date must be later than the start_date and earlier than the latest data date - The latest data date can be obtained by using "AmsMarker" in the v2.ams.get_performance_data_update_time API. Contoh: `20250831` |
| `page_no` | int32 | ya | Specifies the page number of data to return in the current call. Starting from 1. if data is more than one page, the page_no can be some entry to start next call. Contoh: `1` |
| `page_size` | int32 | ya | Each result set is returned as a page of entries. Use the "page_size" filters to control the maximum number of entries to retrieve per page (i.e., per call). This integer value is used to specify the maximum number of entries to return in a single "page" of data. The limit of page_size if between 1 and 20. Contoh: `20` |
| `order_type` | string | ya | Order Type. Applicable values: PlacedOrder ConfirmedOrder: Note: - Placed orders are orders (COD and non-COD) that buyers have successfully placed, including paid and unpaid orders. - Confirmed orders are either non-COD orders that have been paid for or COD orders that have been confirmed for shipping (usually 30 mins after placing the order). Contoh: `ConfirmedOrder` |
| `channel` | string | ya | Channel. Applicable values: - ShopeeVideo - LiveStreaming Contoh: `ShopeeVideo` |
| `affiliate_id` | int64 | tidak | Search for the contents published by affiliates with the affiliate id entered. Contoh: `11146330000` |
| `item_id` | int64 | tidak | Search for the contents with the searched product included (precise search). Contoh: `14016184405` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.list` | object[] |  |
| `response.list[].content_id` | string | Unique identifier of the content where the product is placed. |
| `response.list[].content_title` | string | Title or name of the content (e.g., video, livestream) associated with the product. |
| `response.list[].post_time` | int64 | Livestream: The livestream start time. Video: The video post time. |
| `response.list[].affiliate_name` | string | Display name of the affiliate who posted the content, typically the Shopee name. |
| `response.list[].affiliate_username` | string | Login or Shopee account username associated with the affiliate. |
| `response.list[].products` | int64 | Number of products associated with the content. |
| `response.list[].views` | int32 | The total viewed pv of the content of this shop within the selected time range |
| `response.list[].likes` | int32 | The total number of likes for the content of this shop within the selected time range |
| `response.list[].comments` | int32 | The total number of comments for the content of this shop within the selected time range |
| `response.list[].sales` | string | The total sales of the content associated with the shop orders within the selected time range |
| `response.list[].orders` | int64 | The total number of orders associated with the shop for the content in the selected time range |
| `response.list[].items_sold` | int64 | The total number of items sold associated with the shop for the content in the selected time range |
| `response.list[].channel` | string | Channel. Applicable values: - ShopeeVideo - LiveStreaming |
| `response.total_count` | int64 | This is to indicate the whole number of items. |
| `response.has_more` | boolean | This is to indicate whether the list is more than one page. If this value is true, you may want to continue to check next page to retrieve the rest of datas. |
| `response.fetched_date_range` | string | Effective query date range. Invalid input ranges will be automatically shifted. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
