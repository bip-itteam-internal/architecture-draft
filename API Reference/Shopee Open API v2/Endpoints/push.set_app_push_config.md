# push.set_app_push_config

- Path: `/api/v2/push/set_app_push_config`
- Method: POST
- Auth: public
- Deskripsi: you can turn on or turn off your app push config setting through this open api
- Sumber: open.shopee.com/documents/v2/push.set_app_push_config?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `callback_url` | string | tidak | The callback url of push mechanism. It is the address where the Shopee will send the push message to. If you don't set any callback_url before, this parameters is required. Contoh: `https://open.shopee.com/` |
| `set_push_config_on` | int[] | tidak | Turn on push config, Shopee will send the push message into the callback url. 1=Shop authorization for partners 2=Shop deauthorization for partners 3=Order status update push 4=TrackingNo push 5=Shopee Updates 6=Banned item push 7=item promotion push 8=reserved stock change push 9=promotionn update push 10=webchat push 11=video upload push 12=openapi authorization expiry push 13=brand register result Contoh: `[1,2,3,4,5,8,9,10]` |
| `set_push_config_off` | int[] | tidak | Turn off Push config, Shopee won't send the push message into the callback url. 1=Shop authorization for partners 2=Shop deauthorization for partners 3=Order status update push 4=TrackingNo push 5=Shopee Updates 6=Banned item push 7=item promotion push 8=reserved stock change push 9=promotionn update push 10=webchat push 11=video upload push 12=openapi authorization expiry push 13=brand register result Contoh: `[6,7,11,12,13]` |
| `blocked_shop_id_list` | int[] | tidak | Use this filed to set shops that need to be blocked.Please input no more than 500 shop id. Contoh: `[10010,20020,30030]` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.result` | string | Use this field to indicate whether the configuration is set successfully. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
