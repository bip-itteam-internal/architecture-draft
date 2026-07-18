# logistics.get_address_list

- Path: `/api/v2/logistics/get_address_list`
- Method: GET
- Auth: shop
- Deskripsi: For integrated logistics channel, use this call to get pickup address for pickup mode order.
- Sumber: open.shopee.com/documents/v2/logistics.get_address_list?type=1 (backend doc/api) — 2026-07-18
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
| `response.show_pickup_address` | boolean | Show pickup address or not. |
| `response.address_list` | object[] | The address list of you shop |
| `response.address_list[].address_id` | int64 | The identity of address. |
| `response.address_list[].region` | string | The region of specify address. |
| `response.address_list[].state` | string | The state of specify address. |
| `response.address_list[].city` | string | The city of specify address. |
| `response.address_list[].address` | string | The address description of specify address. |
| `response.address_list[].zipcode` | string | The zipcode of specify address. |
| `response.address_list[].district` | string | The district of specify address. |
| `response.address_list[].town` | string | The town of specify address. |
| `response.address_list[].address_type` | string[] | The flag of shop address.Available values: DEFAULT_ADDRESS, PICK_UP_ADDRESS, RETURN_ADDRESS, INBOUND_PICKUP_ADDRESS. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
