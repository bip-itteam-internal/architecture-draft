# logistics.update_address

- Path: `/api/v2/logistics/update_address`
- Method: POST
- Auth: shop
- Deskripsi: Use this API to update the address of a shop.
- Sumber: open.shopee.com/documents/v2/logistics.update_address?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `address_id` | int64 | ya | Unique identifier for the address. You can get the address_id via v2.logistics.get_address_list. Contoh: `123456` |
| `region` | string | tidak | The region of the address. Note: Do not allow to update the region of the address. Contoh: `Brazil` |
| `state` | string | tidak | The state of the address. Contoh: `SP` |
| `city` | string | tidak | The city of the address. Contoh: `São Paulo` |
| `district` | string | tidak | The district of the address. Contoh: `Pinheiros` |
| `town` | string | tidak | The town of the address. Contoh: `Rua dos Pinheiros` |
| `address` | string | tidak | The detailed address description of the address. Contoh: `123 Rua dos Pinheiros Apt 45` |
| `zipcode` | string | tidak | The zipcode of the address. Contoh: `05422-001` |
| `name` | string | tidak | Recipient’s name at this address. Contoh: `Carlos Silva` |
| `phone` | string | tidak | Contact phone number for the recipient. Contoh: `+55-11-91234-5678` |
| `geo_info` | string | tidak | Geolocation information for the address. Type: JSON string Note: 1) To clear existing geo info, pass "" or {} . 2) To keep existing geo info, do not include this field . 3) The JSON may include optional fields: - formattedAddress (string): full formatted address. - region (object) – contains latitude and longitude as floats. - user_verified (boolean) – whether the geolocation is verified by the user. - user_adjusted (boolean) – whether the geolocation was adjusted by the user. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
