# logistics.download_booking_shipping_document

- Path: `/api/v2/logistics/download_booking_shipping_document`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to download shipping_document. You have to call v2.logistics.create_booking_shipping_document to create a new shipping document task first and call v2.logistics.get_booking_shipping_document_result to get the task status second. If the task is READY, you can download this shipping document.
- Sumber: open.shopee.com/documents/v2/logistics.download_booking_shipping_document?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `shipping_document_type` | string | tidak | The type of shipping document. Available values: NORMAL_AIR_WAYBILL,THERMAL_AIR_WAYBILL Contoh: `NORMAL_AIR_WAYBILL` |
| `booking_list` | object[] | ya | The list of bookings you want to get. limit [1,50] |

## Response

| field | tipe | keterangan |
|---|---|---|
| `waybill` | file | The waybill file. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
