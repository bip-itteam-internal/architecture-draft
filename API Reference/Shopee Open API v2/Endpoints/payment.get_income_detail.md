# payment.get_income_detail

- Path: `/api/v2/payment/get_income_detail`
- Method: GET
- Auth: shop
- Deskripsi: Retrieves detailed order-level income information across various income statuses for a specified time period. This API enables partners to display granular transaction-level income data consistent with Seller Center’s “Income Details” view, segmented by income status and payout stage. The API dynamically adapts data fields based on the seller’s shop type (Local or Cross Border) and the selected income status (e.g., Pending, To Release, Released).
- Sumber: open.shopee.com/documents/v2/payment.get_income_detail?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `date_from` | string | ya | Start date (YYYY-MM-DD) of the income reference period. This field is only used for Income Status = Released, the other statuses will display all records currently in that status. For income Status = Released, For Released → Payout released date: 1. date_to must be later than date_from 2. date range cannot exceed 14 days 3. Input must follow valid date format. Contoh: `2025-09-25` |
| `date_to` | string | ya | End date (YYYY-MM-DD) of the income reference period. Must be later than date_from. This field is only used for Income Status = Released, the other statuses will display all records currently in that status. For income Status = Released, For Released → Payout released date: 1. date_to must be later than date_from 2. date range cannot exceed 14 days 3. Input must follow valid date format. Contoh: `2025-09-30` |
| `income_status` | int32 | ya | Status of Seller Income payout (Enum - Desc) Local 1 -Released 2 - Pending CB 0 - To Release 1 - Released 2 - Pending Contoh: `1` |
| `cursor` | string | tidak | Pagination token for the next set of results. Use an empty string "" for the first request. Contoh: `176714986216530` |
| `page_size` | int64 | ya | Number of income detail records to retrieve per page Contoh: `30` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. <path></path><path></path> |
| `income_detail_list` | object | List of income detail records returned for the specified time range and status. |
| `income_detail_list.next_page` | object | Contains pagination metadata for fetching the next page. |
| `income_detail_list.next_page.cursor` | string | Token to retrieve the next page of results. Returns empty if there is no more data. |
| `income_detail_list.next_page.page_size` | int32 | Number of records returned per page. |
| `income_detail_list.income_detail_list_item` | object | List of income detail objects |
| `income_detail_list.income_detail_list_item.payment_method` | string | Payment channel or method used for the order |
| `income_detail_list.income_detail_list_item.order_sn` | string | Unique order serial number associated with the income record. |
| `income_detail_list.income_detail_list_item.description` | string | Type of income or billing item — e.g., Order Income, Adjustment etc |
| `income_detail_list.income_detail_list_item.status` | string | Status description of the order income or payout. |
| `income_detail_list.income_detail_list_item.currency` | string | Currency in which the income was transacted. |
| `income_detail_list.income_detail_list_item.estimated_escrow_amount` | float | Estimated escrow amount pending release for the order. |
| `income_detail_list.income_detail_list_item.estimated_payout_time` | int64 | Estimated payout time (Unix timestamp). Applicable for Pending/To Release status. |
| `income_detail_list.income_detail_list_item.to_release_amount` | float | Amount that is queued for release to seller (Cross Border only). |
| `income_detail_list.income_detail_list_item.creation_date` | int64 | Order creation timestamp (Unix format). |
| `income_detail_list.income_detail_list_item.released_amount` | float | Amount successfully released to the seller. |
| `income_detail_list.income_detail_list_item.actual_payout_time` | int64 | Actual payout time (Unix timestamp) when funds were transferred. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
