# logistics.get_tracking_info

- Path: `/api/v2/logistics/get_tracking_info`
- Method: GET
- Auth: shop
- Deskripsi: Use this api to get the logistics tracking information of an order.
- Sumber: open.shopee.com/documents/v2/logistics.get_tracking_info?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `order_sn` | string | ya | Shopee's unique identifier for an order. Contoh: `2409177JCSRTEU` |
| `package_number` | string | tidak | Shopee's unique identifier for the package under an order. You shouldn't fill the field with empty string when there is a package number. |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object | Detail informations you are querying. |
| `response.order_sn` | string | Shopee's unique identifier for an order. |
| `response.package_number` | string | Shopee's unique identifier for the package under an order. |
| `response.logistics_status` | string | The logistics status for the order. Applicable values: See Data Definition- LogisticsStatus. |
| `response.tracking_info` | object[] | The tracking info of the order. |
| `response.tracking_info[].update_time` | timestamp | The time when the logistics tracking info is updated. |
| `response.tracking_info[].description` | string | The description of the logistics tracking info. |
| `response.tracking_info[].logistics_status` | string | The logistics status for the order. Applicable values: See Data Definition- LogisticsStatus. |
| `response.tracking_info[].return_code` | string | The OTP generated after the parcel enters the RTS (Return to Seller) process. Sellers need to provide this OTP to the driver to complete the return confirmation. Note: - This field only applies to orders under the SPX Instant & Sameday channel in ID region. - This field is only returned when the driver has initiated the return process to the seller. If the driver has not initiated the return process for the parcel, this field will be empty. |
| `response.collection_pin_code` | string | [TW Only] The unique 6-digit PIN code for sellers to collect RTS (Return to Seller) parcels at service points. This field is returned when the channel is C2C and the logistics_status is FULFILMENT_DELIVERY_FAILED. |
| `response.reversed_tracking_number` | string | The tracking number of the reversed logistics. Note: Only apply to the cross-border segment of failed delivery parcels returned from the local return warehouse to the seller. |
| `response.reversed_courier_name` | string | The courier name of the reversed logistics. Note: Only apply to the cross-border segment of failed delivery parcels returned from the local return warehouse to the seller. |
| `response.reversed_tracking_info` | object[] | The tracking information of the reversed logistics. Note: Only apply to the cross-border segment of failed delivery parcels returned from the local return warehouse to the seller. |
| `response.reversed_tracking_info[].update_time` | int64 | The time when the reversed logistics tracking info is updated. |
| `response.reversed_tracking_info[].description` | string | The description of the reversed logistics tracking info. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
