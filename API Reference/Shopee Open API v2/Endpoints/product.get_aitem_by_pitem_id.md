# product.get_aitem_by_pitem_id

- Path: `/api/v2/product/get_aitem_by_pitem_id`
- Method: GET
- Auth: shop
- Deskripsi: Get the list of A Items under SIP Affiliate Shop corresponding to P Items under SIP Primary Shop.
- Sumber: open.shopee.com/documents/v2/product.get_aitem_by_pitem_id?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `pitem_id` | int64 | ya | ID of item under SIP Primary Shop. Contoh: `843997615` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.aitem_list` | object[] |  |
| `response.aitem_list[].ashop_id` | int64 | ID of SIP Affiliate Shop. |
| `response.aitem_list[].ashop_region` | string | Region of SIP Affiliate Shop. |
| `response.aitem_list[].aitem_id` | int64 | ID of item under SIP Affiliate Shop corresponding to the P Item. |
| `response.aitem_list[].model_mapping_list` | object[] | If the P Item does not have model, then the model_mapping_list will not be returned. |
| `response.aitem_list[].model_mapping_list[].pmodel_id` | int64 | ID of model for the P Item. |
| `response.aitem_list[].model_mapping_list[].amodel_id` | int64 | ID of model for the A Item. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
