# logistics.download_to_label

- Path: `/api/v2/logistics/download_to_label`
- Method: POST
- Auth: shop
- Deskripsi: Use the API to download the TO label that should be attached to the carton before drop-off at the warehouse (Only for TW channel_id:30029).
- Sumber: open.shopee.com/documents/v2/logistics.download_to_label?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `sorting_group` | int32 | ya | Sorting Group of the TO. Available value: 1:North 2:South Contoh: `1` |
| `quantity` | int32 | tidak | Specifies the TO quantity, up to a maximum of 20 per request. If not specified, the default value is 1 Contoh: `1` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `waybill` | file | The waybill file. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
