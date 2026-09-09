# public.get_access_token

- Path: `/api/v2/auth/token/get`
- Method: POST
- Auth: public
- Deskripsi: Use the code from the authorization step to call this API to obtain the authorized shop_id, merchant_id, supplier_id, or user_id, and its corresponding access_token and refresh_token.
- Sumber: open.shopee.com/documents/v2/public.get_access_token?type=1 (backend doc/api) — 2026-09-09
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `code` | string | ya | The code in redirect url after the authorization. Valid for one-time use, expires in 10 minutes Contoh: `5a5477794a55537954697169514f4653` |
| `partner_id` | int64 | ya | Partner ID is assigned upon registration is successful. Required for all requests. Contoh: `1001141` |
| `shop_id` | int64 | tidak | Shopee's unique identifier for a shop. |
| `main_account_id` | int64 | tidak | The main_account_id of the seller that authorized the developer. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Error codes for API requests; always returned.When the API call is successful, the error code returned is empty. |
| `message` | string | Always returned. Provides detailed error information. |
| `request_id` | string | ID of API requests; always returned. Used to diagnose problems. |
| `shop_id_list` | int64[] | Returned all shop_ids authorized this time. |
| `merchant_id_list` | int64[] | Returned all merchant_ids authorized this time. |
| `supplier_id_list` | int64[] | Returned all supplier_ids authorized this time. |
| `user_id_list` | int64[] | Returned all user_ids authorized this time. |
| `principal_id_list` | int64[] | If the authorized role is principal administrator, return all principal_id under this authorization. |
| `access_token` | string | Returned when the API call is successful. A dynamic token that can be used multiple times and expires after 4 hours. |
| `refresh_token` | string | Returned when the API call is successful. Use refresh_token to get a new access_token. Valid for each shop_id, merchant_id, supplier_id, or user_id respectively, for 30 days. |
| `expire_in` | timestamp | Returned when the API call is successful. The validity period of the access_token, in seconds. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
