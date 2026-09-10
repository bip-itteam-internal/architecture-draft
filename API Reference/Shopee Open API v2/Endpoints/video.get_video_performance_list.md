# video.get_video_performance_list

- Path: `/api/v2/video/get_video_performance_list`
- Method: GET
- Auth: user
- Deskripsi: Get specific performance data for individual post Shopee Video. There is at least a one-day delay.
- Sumber: open.shopee.com/documents/v2/video.get_video_performance_list?type=1 (backend doc/api) — 2026-09-10
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `page_no` | int32 | ya | The start index of request. Starting from 1. Contoh: `1` |
| `page_size` | int32 | ya | The number of video returned by this request. Max is 20. Contoh: `10` |
| `period_type` | string | ya | Period Type. Applicable values: Day Week Month Last7d Last15d Last30d Note: The end date must align with the Period Type. Contoh: `Last7d` |
| `end_date` | string | ya | The end_date format should be "YYYY-MM-DD". - For Day, Last7d, Last15d, and Last30d, the end_date must before current day. - For Week, the end_date must be Sunday and must be less than or equal to the current week. - For Month, the end_date must be the end of the month and must be less than or equal to the current month. Contoh: `2025-10-30` |
| `caption` | string | tidak | Description of the Shopee Video. |
| `order_by` | string | ya | Use this field to specify which field to use to sort the returned list. Available values: Views Likes Comments AvgViewsDuration Contoh: `Likes` |
| `sort` | string | ya | Use this field to specify whether the returned list is sorted in ascending or descending order_by. Available values: asc desc Contoh: `desc` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.total_count` | int32 | The total count of video that match the condition. |
| `response.has_more` | boolean | This is to indicate whether the video list is more than one page. If this value is true, you may want to continue to check next page to retrieve the rest of data. |
| `response.list` | object[] | The list of video that match the condition. |
| `response.list[].video_upload_id` | string | ID of uploaded video. |
| `response.list[].post_id` | string | The unique identifier for post Shopee Video. Only have value when the video status is 300 (POSTED). |
| `response.list[].post_time` | timestamp | The time when the video post to Shopee Video. Only have value when the video status is 300 (POSTED). |
| `response.list[].video_url` | string | Video play url. |
| `response.list[].status` | int64 | Video current status. Applicable values: 300: POSTED 400: DELETED |
| `response.list[].cover_image_url` | string | Cover image url of the Shopee Video. |
| `response.list[].caption` | string | Description of the Shopee Video. |
| `response.list[].duration` | string | Video duration time in millisecond. |
| `response.list[].views` | int64 | View count of post Shopee Video. Only have value when the video status is 300 (POSTED). |
| `response.list[].likes` | int64 | Like count the post Shopee Video. Only have value when the video status is 300 (POSTED). |
| `response.list[].comments` | int64 | Comment count the post Shopee Video. Only have value when the video status is 300 (POSTED). |
| `response.list[].shares` | int64 | Share count the post Shopee Video. Only have value when the video status is 300 (POSTED). |
| `response.list[].avg_views_duration` | int64 | Total watch duration per video. |
| `response.list[].completion_rate` | float | Video completion rate. |
| `response.list[].placed_orders` | int64 | The number of placed orders for the video. |
| `response.list[].confirmed_orders` | int64 | The number of confirmed orders for the video. |
| `response.list[].placed_sales` | float | The placed value of orders for the video. |
| `response.list[].confirmed_sales` | float | The confirmed value of orders for the video. |
| `response.list[].placed_item_sold` | int64 | Number of item sold from placed orders in the video. |
| `response.list[].confirmed_item_sold` | int64 | Number of item sold from confirmed orders in the video. |
| `response.list[].fetched_date_range` | string | Data Date Range. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
