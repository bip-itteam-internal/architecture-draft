# product.category_recommend

- Path: `/api/v2/product/category_recommend`
- Method: GET
- Auth: shop
- Deskripsi: Recommend category by item name.
- Sumber: open.shopee.com/documents/v2/product.category_recommend?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `item_name` | string | ya | name of item Contoh: `海飞丝洗发水` |
| `product_cover_image` | string | tidak | Please use the image id returned by v2.media_space.upload_image api, we will ignore if this field is empty string Contoh: `16bdad2c365f1fccea7664e69b696571` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `warning` | string | Indicate waring details if hit waring. Empty if no waring happened. |
| `request_id` | string | The identifier for an API request for error tracking. |
| `response` | object |  |
| `response.category_id` | int[] | Shopee's unique identifier for a category. |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
