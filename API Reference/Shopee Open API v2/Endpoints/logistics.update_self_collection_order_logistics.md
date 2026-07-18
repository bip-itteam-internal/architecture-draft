# logistics.update_self_collection_order_logistics

- Path: `/api/v2/logistics/update_self_collection_order_logistics`
- Method: POST
- Auth: shop
- Deskripsi: Use this api to update the order status for buyer to collect the orders directly from your pharmacy. This includes indicating that order is ready for collection, and that the order has been picked up by the buyer. You should call v2.logistics.get_order_detail or v2.logistics.get_package_detail first to get the package_number of such orders.
- Sumber: open.shopee.com/documents/v2/logistics.update_self_collection_order_logistics?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `package_number` | string | ya | Shopee's unique identifier for the package under an order. Contoh: `OFG211171863281841` |
| `self_collection_logistics_action` | string | ya | Order logistics action. available values: - ready_for_collection - order_collected Contoh: `order_collected` |
| `epoc_image_list` | string[] | tidak | List of image_id for the proof that buyer already collected the order at the store. Required when self_collection_logistics_action is order_collected. Max: 3. You can call the v2.media.upload_image to upload image and get the image_id, for this scenario, please pass the business = 1 and scene = 1. Contoh: `["id-11134284-7r98o-mef6xcoiw1nt15"]` |
| `pin` | string | tidak | PIN code required for prescription orders when buyer collects at your shop. Contoh: `123456` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `request_id` | string | The identifier for an API request for error tracking. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
