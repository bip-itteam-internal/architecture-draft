# product.get_item_promotion

- Path: `/api/v2/product/get_item_promotion`
- Method: GET
- Auth: shop
- Deskripsi: Get item promotion info.
- Sumber: open.shopee.com/documents/v2/product.get_item_promotion?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_id_list` | int64[] | ya | Item ID list, can send 1 to 50 items. Contoh: `13233406680,17924576533` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Waring message. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.success_list` | object[] | Success item promotion info. |
| `response.success_list[].item_id` | int | The identity of product item. |
| `response.success_list[].promotion` | object[] | Item promotion info list |
| `response.success_list[].promotion[].promotion_type` | string | Promotion type, Applicable values: See Data Definition- PromotionType. |
| `response.success_list[].promotion[].promotion_id` | int64 | The identity of item promotion. |
| `response.success_list[].promotion[].model_id` | int64 | The identity of product model. |
| `response.success_list[].promotion[].start_time` | timestamp | Promotion start tiem. |
| `response.success_list[].promotion[].end_time` | timestamp | Promotion end item. |
| `response.success_list[].promotion[].promotion_price_info` | object[] | Promotion price info. |
| `response.success_list[].promotion[].promotion_price_info[].promotion_price` | float | Promotion price. |
| `response.success_list[].promotion[].promotion_staging` | string | Could be ongoing/upcoming |
| `response.success_list[].promotion[].promotion_stock_info_v2` | object | new promotion stock |
| `response.success_list[].promotion[].promotion_stock_info_v2.summary_info` | object | stock summary info |
| `response.success_list[].promotion[].promotion_stock_info_v2.total_reserved_stock` | int32 | Total Stock reserved for promotion |
| `response.failure_list` | object[] | Fail item promotion info. |
| `response.failure_list[].item_id` | int64 | The identity of item. |
| `response.failure_list[].failed_reason` | string | Fail reason. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
