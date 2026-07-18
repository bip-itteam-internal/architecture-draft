# product.register_brand

- Path: `/api/v2/product/register_brand`
- Method: POST
- Auth: shop
- Deskripsi: Use this call to register a brand.
- Sumber: open.shopee.com/documents/v2/product.register_brand?type=1 (backend doc/api) — 2026-07-18
- Confidence: verified-docs

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `original_brand_name` | string | ya | Brand name, length<=254. Contoh: `Nike` |
| `category_list` | int[] | ya | Category_id list for this brand, please input category in L1 or L2. Max input num of category_id is 50. Contoh: `[16521,16522]` |
| `product_image` | object | ya |  |
| `app_logo_image_id` | string | tidak | Image_id of logo for app client,please input hashcode of this picture. Contoh: `6373157f9408b42c8aacda1d63d3a209` |
| `brand_website` | string | tidak | Official website of brand, length<=254. Contoh: `www.nike.com` |
| `brand_description` | string | tidak | The description of this brand, can input the information, length<=254. Contoh: `Our mission is what drives us to do everything possible to expand human potential. We do that by creating groundbreaking sport innovations, by making our products more sustainably, by building a creative and diverse global team and by making a positive impact in communities where we live and work` |
| `additional_information` | string | tidak | Additional notes or comment can seller can add, length<=254. Contoh: `additional notes or comment can seller can add` |
| `pc_logo_image_id` | string | tidak | Image_id of logo for pc client,please input hashcode of this picture. Contoh: `6373157f9408b42c8aacda1d63d3a209` |
| `brand_region` | string | ya | origin region of brand. Contoh: `US` |
| `licenses` | object[] | tidak | For appeal blacklisted brand data |
| `brand_registration_website` | string | tidak | The link to brand registration website, It is mandatory when brand name hit blacklist.len<254 Contoh: `https://www.jumbomark.com/indonesia/trademark-registration/mischief-DID2019017755` |

## Response

| field | tipe | keterangan |
|---|---|---|
| `request_id` | string | The identifier for an API request for error tracking. |
| `error` | string | Indicate error type if hit error. Empty if no error happened. |
| `message` | string | Indicate error details if hit error. Empty if no error happened. |
| `response` | object |  |
| `response.brand_id` | int | The identity of brand. |
| `response.original_brand_name` | string | Brand name |

## Catatan

- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.
- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).
