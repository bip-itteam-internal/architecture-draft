# push.get_app_push_config

- Path: `/api/v2/push/get_app_push_config`
- Method: GET
- Auth: public
- Deskripsi: you can get your app current push config setting through this api
- Sumber: open.shopee.com/documents/v2/push.get_app_push_config?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

_Tidak ada parameter request selain common params._

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.callback_url` | string | The callback url of push mechanism. It is the address where the Shopee will send the push message to. If you don't set any callback_url before, this parameters is required. |
| `response.live_push_status` | string | live push status:Normal,Warning,Suspended |
| `response.suspended_time` | timestamp | The live push suspended time caused by low successful rate of push mechanism.Only when live push status is suspended, this parameters will response. |
| `response.blocked_shop_id` | int[] | Use this filed to indicate that Shopee won't send any push message created by this shop. |
| `response.push_config_on_list` | int[] | Use this field to indicate which push config turn on, and you can receive the push message. 1=Shop authorization for partners 2=Shop deauthorization for partners 3=Order status update push 4=TrackingNo push 5=Shopee Updates 6=Banned item push 7=item promotion push 8=reserved stock change push 9=promotionn update push 10=webchat push 11=video upload push 12=openapi authorization expiry push 13=brand register result |
| `response.push_config_off_list` | int[] | Use this field to indicate which push config turn on, and you can receive the push message. 1=Shop authorization for partners 2=Shop deauthorization for partners 3=Order status update push 4=TrackingNo push 5=Shopee Updates 6=Banned item push 7=item promotion push 8=reserved stock change push 9=promotionn update push 10=webchat push 11=video upload push 12=openapi authorization expiry push 13=brand register result |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
