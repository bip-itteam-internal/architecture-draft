# public.refresh_access_token

- Path: `/api/v2/auth/access_token/get`
- Method: POST
- Auth: public
- Deskripsi: Use this API to refresh the access_token after it expires. Refresh_token can be used once only, this API will also return a new refresh_token. Please use the new refresh_token for the next RefreshAccessToken call
- Sumber: open.shopee.com/documents/v2/public.refresh_access_token?type=1 (backend doc/api) — 2026-09-09
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `refresh_token` | string | ya | Use refresh_token to get a new access_token. Each refresh_token is valid for 30 days, and can only be used once by either a shop_id or merchant_id or supplier_id or user_id. Contoh: `4c7259534969484e71734d695a6e6d55` |
| `partner_id` | int64 | ya | The partner_id obtained from the App. This partner_id is inserted into the body. Contoh: `2001887` |
| `shop_id` | int64 | tidak | The shop_id that granted authorization to your App. Only the shop_id or merchant_id or supplier_id or user_id can be selected as the input parameter, and they must be refreshed separately. Contoh: `322300222` |
| `merchant_id` | int64 | tidak | The merchant_id that granted authorization to your App. Only the shop_id or merchant_id or supplier_id or user_id can be selected as the input parameter, and they must be refreshed separately. |
| `supplier_id` | int64 | tidak | The supplier_id that granted authorization to your App. Only the shop_id or merchant_id or supplier_id or user_id can be selected as the input parameter, and they must be refreshed separately. |
| `user_id` | int64 | tidak | The user_id that granted authorization to your App. Only the shop_id or merchant_id or supplier_id or user_id can be selected as the input parameter, and they must be refreshed separately. |
| `principal_id` | int64 | tidak | Shopee's unique identifier for a principal. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `partner_id` | int64 | Returned when the API call is successful. The partner_id you used for this refresh. |
| `principal_id` | int64 | Returned when the API call is successful.The principal_id for this refresh. |
| `shop_id` | int64 | Returned when the API call is successful. The shop_id for this refresh. |
| `merchant_id` | int64 | Returned when the API call is successful. The merchant_id for this refresh. |
| `supplier_id` | int64 | Returned when the API call is successful. The supplier_id for this refresh. |
| `user_id` | int64 | Returned when the API call is successful. The user_id for this refresh. |
| `access_token` | string | Returned when the API call is successful. Each new access_token is a dynamic token that can be used multiple times. It expires after 4 hours. |
| `refresh_token` | string | New refresh_tokenReturned when the API call is successful. Use a refresh_token to get a new access_token. Each refresh_token is valid for 30 days, and can only be used once by either a shop_id or merchant_id or supplier_id or user_id. |
| `expire_in` | timestamp | Returned when the API call is successful. The validity period of the access_token, in seconds. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
