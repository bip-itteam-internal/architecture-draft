# video.get_video_list

- Path: `/api/v2/video/get_video_list`
- Method: GET
- Auth: user
- Deskripsi: Get the list of video in draft status or video already post to Shopee Video.
- Sumber: open.shopee.com/documents/v2/video.get_video_list?type=1 (backend doc/api) — 2026-09-10
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `page_no` | int32 | ya | The start index of request. Starting from 1. Contoh: `1` |
| `page_size` | int32 | ya | The number of affiliate returned by this request, Max is 20. Contoh: `10` |
| `list_type` | int32 | ya | Search tpye for video in draft status or video already post to Shopee Video. 1: draft 2: post Contoh: `1` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object | Detail informations you are querying. |
| `response.total_count` | int64 | The total count of video that match the condition. |
| `response.has_more` | boolean | This is to indicate whether the video list is more than one page. If this value is true, you may want to continue to check next page to retrieve the rest of data. |
| `response.list` | object | The list of video that match the condition. |
| `response.list.video_upload_id` | string | ID of uploaded video. |
| `response.list.post_id` | string | The unique identifier for post Shopee Video. Only have value when the video status is 300 (POSTED). |
| `response.list.post_time` | timestamp | The time when the video post to Shopee Video. Only have value when the video status is 300 (POSTED). |
| `response.list.video_url` | string | Video play url. |
| `response.list.status` | int32 | Video current status. Applicable values: 200: DRAFT 300: POSTED 400: DELETED 500: SCHEDULED 600: SCHEDULED_FAILED |
| `response.list.cover_image_url` | string | Cover image url of the Shopee Video. |
| `response.list.caption` | string | Description of the Shopee Video. |
| `response.list.duration` | int64 | Video duration time in millisecond. |
| `response.list.views` | int64 | View count of post Shopee Video. Only have value when the video status is 300 (POSTED). |
| `response.list.likes` | int64 | Like count the post Shopee Video. Only have value when the video status is 300 (POSTED). |
| `response.list.comments` | int64 | Comment count the post Shopee Video. Only have value when the video status is 300 (POSTED). |
| `response.list.has_performance` | boolean | Whether there is video metric data. |
| `response.list.item_list` | object | List of products linked with the Shopee Video. |
| `response.list.item_list.shop_id` | int64 | Shopee's unique identifier for a shop of the item. |
| `response.list.item_list.item_id` | int64 | Shopee's unique identifier for an item. |
| `response.list.item_list.item_name` | string | Name of the item. |
| `response.list.item_list.custom_item_name` | string | Name of the item displayed on Shopee Video (max 255 characters). |
| `response.list.item_list.item_cover_image_url` | string | Cover image url of the item. |
| `response.list.item_list.min_price` | float | Min price of the item. |
| `response.list.item_list.max_price` | float | Max price of the item. |
| `response.list.item_list.stock` | int64 | Stock of the item. |
| `response.list.allow_info` | object | Whether allow stitch and duet. |
| `response.list.allow_info.allow_stitch` | boolean | Whether allow stitch. |
| `response.list.allow_info.allow_duet` | boolean | Whether allow duet. |
| `response.list.scheduled_info` | object | When scheduled_post is true, scheduled_post_time must not empty. When scheduled_post is false, scheduled_post_time must empty. |
| `response.list.scheduled_info.scheduled_post` | boolean | Whether post it to Shopee Video at scheduled time. |
| `response.list.scheduled_info.scheduled_post_time` | timestamp | Scheduled post time, millisecond timestamp. |
| `response.list.update_time` | timestamp | The lasted update time the video. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
