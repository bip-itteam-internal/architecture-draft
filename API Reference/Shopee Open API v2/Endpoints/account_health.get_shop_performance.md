# account_health.get_shop_performance

- Path: `/api/v2/account_health/get_shop_performance`
- Method: GET
- Auth: shop
- Sumber: https://open.shopee.com/opservice/api/v1/doc/api/?version=2&api_name=v2.account_health.get_shop_performance — 2026-09-11
- Confidence: verified-docs

## Response — metric_type

| nilai | arti |
|---|---|
| 1 | Fulfillment Performance |
| 2 | Listing Performance |
| 3 | Customer Service Performance |

## Response — metric_id (daftar RESMI lengkap)

`metric_id < 0` = bukan metrik nyata, melainkan GRUP metrik.

| id | nama | CS? |
|---|---|---|
| -1 | Non-Responded Chats | ✅ |
| 1 | Late Shipment Rate (All Channels) |  |
| 3 | Non-Fulfilment Rate (All Channels) |  |
| 4 | Preparation Time |  |
| 11 | Chat Response Rate | ✅ |
| 12 | Pre-order Listing % |  |
| 15 | Days of Pre-order Listing Violation |  |
| 21 | Response Time | ✅ |
| 22 | Shop Rating | ✅ |
| 23 | No. of Non-Responded Chats | ✅ |
| 25 | Fast Handover Rate |  |
| 27 | On-time Pickup Failure Rate |  |
| 28 | On-time Pickup Failure Rate Violation Value |  |
| 29 | Average Response Time | ✅ |
| 42 | Cancellation Rate (All Channels) |  |
| 43 | Return-refund Rate (All Channels) |  |
| 52 | Severe Listing Violations |  |
| 53 | Other Listing Violations |  |
| 54 | Prohibited Listings |  |
| 55 | Counterfeit/IP infringement |  |
| 56 | Spam Listings |  |
| 85 | Late Shipment Rate (NDD) |  |
| 88 | Non-fulfilment Rate (NDD) |  |
| 91 | Cancellation Rate (NDD) |  |
| 92 | Return-refund Rate (NDD) |  |
| 95 | Customer Satisfaction | ✅ |
| 96 | % SDD Listings |  |
| 97 | % NDD Listings |  |
| 2001 | Fast Handover Rate - SLS |  |
| 2002 | Fast Handover Rate - FBS |  |
| 2003 | Fast Handover Rate - 3PF |  |
| 2011 | Poor Quality Products |  |
| 2030 | % HD Listings |  |
| 2031 | % HD Free Shipping Enabled |  |
| 2032 | Saturday Shipment |  |
| 2033 | Preparation Time PS |  |
| 2036 | OTDR Logistic Rate |  |
| 2037 | OTDR DD Rate |  |

## Catatan — DIUKUR DI PRODUKSI

⛔ **Tidak ada satu pun metrik konversi chat.** Seluruh daftar di atas sudah
diperiksa: tak ada chat-to-order, closing rate, maupun GMV yang diatribusikan
ke chat — tidak di tipe 3 maupun tipe 1/2. Indikator KPI semacam "Closing Rate"
untuk toko Shopee TIDAK dapat diotomatiskan dari endpoint ini, dan tidak dapat
dirumuskan sendiri: responsnya mengirim angka jadi (`current_period`) tanpa
pembilang/penyebut, dan `transaction_orders` tak punya penanda asal-usul chat.
Padanannya hanya ada di TikTok (`conversion_rate`, `cs_guided_gmv`).

⚠️ **21 (Response Time), 29 (Average Response Time), dan 23 (No. of
Non-Responded Chats) TIDAK dikirim untuk toko Indonesia** meski terdaftar di
dokumentasi ini. Terukur 2026-09-08 atas 9 toko produksi, HTTP 200 seluruhnya.
Menambahkannya ke kode tidak memunculkan data — hanya memberi kesan metriknya
tersedia. Konsumen: `services/marketing-analytics/cs_sla_client_shopee.go`.

⚠️ **`target` dibaca dari respons, JANGAN ditanam sebagai konstanta.** Terukur
produksi: satu toko bertarget `>=60` sementara delapan lainnya `>=70`.

Yang dipakai sistem: **11** (Chat Response Rate), **22** (Shop Rating),
**95** (Customer Satisfaction).
