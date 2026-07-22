# TikTok Shop Partner API — Endpoint Index

Base: `https://open-api.tiktokglobalshop.com`. Auth & sign: lihat `README.md`.

> **Di-seed dari path yang benar-benar DIPANGGIL kode** `bip-erp/services/integration`
> (verified-by-usage — bukan tebakan). Versi path per-modul beda; **ambil dari kode, jangan
> menebak**. Field request/response: cek `Endpoints/` atau struct di
> `internal/infrastructure/clients/tiktok*.go` (tag `json:"..."`).

## Endpoint (verified-by-usage)

| Modul | Method | Path | Fungsi | Dipakai di |
|---|---|---|---|---|
| order | POST | `/order/202309/orders/search` | cari order (filter status/waktu, paginated by page_token) | `tiktok_client.GetOrderList` |
| fulfillment | GET | `/fulfillment/202309/orders/{order_id}/tracking` | **tracking paket maju** (milestone pengiriman) | `tiktok_client` (forward tracking) |
| fulfillment | POST | `/fulfillment/202309/packages/{package_id}/ship` | tandai paket dikirim | `tiktok_client` |
| fulfillment | GET | `/fulfillment/202309/packages/{package_id}/shipping_documents` | dokumen kirim (label/resi) | `tiktok_client` |
| return_refund | POST | `/return_refund/202602/returns/search` | **cari retur** (milestone, resi retur, status) — lihat `Endpoints/return_refund.returns_search.md` | `tiktok_return_usecase` |
| product | GET | `/product/202309/products/{product_id}` | detail produk | `tiktok_client` |
| finance | GET | `/finance/202309/withdrawals` | riwayat penarikan dana | `tiktok_withdrawal_client` |
| analytics | GET | `/analytics/202509/shop_products/{id}/performance` | performa 1 produk | `tiktok_business_client` |
| analytics | POST | `/analytics/202605/shop_products/performance` | performa produk (batch) | `tiktok_business_client` |
| analytics | POST | `/analytics/202605/shop_videos/performance` | performa video | `tiktok_business_client` |
| affiliate_seller | — | `/affiliate_seller/202410/...` | data afiliasi seller | `affiliate_client` |

## Modul lain (belum dipakai kode — verifikasi via dok/paste sebelum coding)

`authorization` (get_authorized_shops, shop_cipher), `logistics` (warehouses, shipping_providers),
`promotion`, `product` (create/update, search), `return_refund` (refunds/search, approve/reject),
`customer_service`, `seller` (permissions). Path & versinya **belum grounded** — jangan tulis di
kode sebelum diverifikasi.
