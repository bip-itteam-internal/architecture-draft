# order.get_order_detail

- Path: `/order/202309/orders`
- Method: GET
- Auth: shop (`app_key` + `timestamp` + `shop_cipher` + `sign` di query; `x-tts-access-token` header)
- Deskripsi: Detail order by `ids` (batch). Dipakai buat verifikasi ground-truth LIVE ke TikTok
  langsung (bukan data ter-sync kita) — mis. cek apakah order genuinely `CANCELLED`/`RETURNED` di
  sisi TikTok saat data lokal tampak janggal.
- Sumber: `bip-erp/services/integration/internal/infrastructure/clients/tiktok_client.go`
  (`TikTokClient.GetOrderDetail`, verified-by-usage) — field JSON dari tag struct
  `TiktokShopOrderDetailResponseOrder`.
- Confidence: **verified-by-usage** (field yang DIPAKAI kode; daftar penuh field TikTok bisa lebih
  luas — verifikasi ke dok resmi bila butuh field di luar ini).

## Request

Query param `ids` = daftar order ID dipisah koma (`strings.Join(orderIDs, ",")`). Tak ada body.

## Response — field yang menjawab "apa status order ini SEBENARNYA di TikTok"

`data.orders[]` — tiap elemen (subset relevan, daftar penuh field lain ada juga di struct):

| field | keterangan |
|---|---|
| `id` | order ID |
| `status` | status order TikTok (mis. `IN_TRANSIT`, `CANCELLED`, dll — **BUKAN** selalu sinkron dgn `tracking.status` kita; lihat catatan gap di bawah) |
| `cancellation_initiator` / `cancel_reason` | siapa & kenapa batal (kosong kalau tak pernah batal) |
| `update_time` | sentuhan TERAKHIR record order (generik — **jangan** disamakan "kapan jadi retur", lihat [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] amandemen 2026-08-20) |
| `tracking_number` | resi forward |
| `line_items[]` | isi order |
| `is_cod` | COD atau bukan |
| `rts_time` / `paid_time` / `delivery_time` | checkpoint waktu |

## Gotcha ditemukan prod (2026-08-20)

Order bisa punya paket **forward** yang sudah `tracking.status=RETURNED` (kurir, mis. J&T,
menandai paket balik ke seller) padahal `order.status` di respons endpoint ini **TETAP**
`IN_TRANSIT` selamanya — TikTok tidak selalu mem-flip status order jadi `CANCELLED`/`RETURNED`
untuk skenario ini, beda dari Shopee yang platformnya konsisten. Dikonfirmasi live pada order
`584959989047461290`: endpoint ini balik `IN_TRANSIT`, dan
[[return_refund.returns_search]] balik KOSONG (TikTok tak pernah tahu
ini retur). Satu-satunya sinyal genuinely retur = tracking kurir forward, bukan endpoint ini.
Detail fix: [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]].
