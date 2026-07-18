# logistics.get_mass_tracking_number

- Path: `/api/v2/logistics/get_mass_tracking_number`
- Method: POST
- Auth: shop
- Deskripsi: After arranging shipment (v2.logistics.mass_ship_order) for the integrated channel, use this api to get the tracking_number, which is a required parameter for creating shipping labels. The api response can return tracking_number empty, since this info is dependent from the 3PL, due to this it is allowed to keep calling the api within 5 minutes interval, until the tracking_number is returned.
- Sumber: open.shopee.com/documents/v2/logistics.get_mass_tracking_number?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `package_list` | object[] | ya | The list of packages you want to get tracking number. limit [1, 50]. |
| `response_optional_fields` | string | tidak | Indicate response fields you want to get. Please select from the below response parameters. If you input an object field, all the params under it will be included automatically in the response. If there are multiple response fields you want to get, you need to use English comma to connect them. Available values: plp_number, first_mile_tracking_number,last_mile_tracking_number. Contoh: `first_mile_tracking_number` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.success_list` | object[] | Success package list. |
| `response.success_list[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `response.success_list[].tracking_number` | string | The tracking number of this order. |
| `response.success_list[].plp_number` | string | The unique identifier for package of BR correios. |
| `response.success_list[].first_mile_tracking_number` | string | The first mile tracking number of the order. Only for Cross Border Seller |
| `response.success_list[].last_mile_tracking_number` | string | The last mile tracking number of the order. Only for Cross Border BR seller. |
| `response.success_list[].hint` | string | Indicate hint information if cannot get some fields under special scenarios. For example, cannot get tracking_number when cvs store is closed. |
| `response.success_list[].pickup_code` | string | For drivers to quickly identify parcel to be picked up. Only returned for instant+sameday orders. |
| `response.fail_list` | object[] | Fail package list. |
| `response.fail_list[].package_number` | string | Shopee's unique identifier for the package under an order. |
| `response.fail_list[].fail_reason` | string | Reason for failure. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
