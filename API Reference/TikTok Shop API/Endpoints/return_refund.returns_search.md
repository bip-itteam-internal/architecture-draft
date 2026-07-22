# return_refund.returns_search

- Path: `/return_refund/202602/returns/search`
- Method: POST
- Auth: shop (`app_key` + `timestamp` + `shop_cipher` + `sign` di query; `x-tts-access-token` header)
- Deskripsi: Cari retur/refund seller. Sumber utama data retur TikTok di ERP — mengisi
  `transaction_orders.return` (via `FetchAndSetTikTokReturn`). Termasuk resi retur & status.
- Sumber: `bip-erp/services/integration/internal/usecase/tiktok_return_usecase.go` +
  `internal/infrastructure/clients/tiktok_client.go` (verified-by-usage) — field JSON dari tag struct.
- Confidence: **verified-by-usage** (field yang DIPAKAI kode; daftar penuh param request TikTok
  bisa lebih luas — verifikasi ke dok resmi bila butuh field di luar ini).

## Request (yang dipakai kode)

Body JSON berisi filter waktu + status; paginasi via `page_size` + `page_token`. Ambil bentuk
persisnya dari `TiktokReturnSearchPayload` di `tiktok_client.go` sebelum menambah field.

## Response — field yang menjawab kebutuhan retur (grounded, dari tag `json`)

`return_orders[]` — tiap elemen:

| field | keterangan |
|---|---|
| `return_id` | ID retur (kunci) |
| `order_id` | order asal |
| `return_status` | status mesin retur |
| `display_status` | status tampil |
| `return_type` | jenis (REFUND / RETURN_AND_REFUND, dll) |
| `seller_proposed_return_type` | usulan tipe dari seller |
| `return_tracking_number` | **resi paket balik** (retur fisik) |
| `return_provider_name` | kurir retur |
| `refund_amount` / `refund_total` | nilai refund |
| `cancel_reason` / `seller_note` | alasan / catatan |
| `return_line_items[]` | baris retur → `return_line_item_id`, `seller_sku`, `return_sub_line_items[]` |
| `package_status` | status paket |
| `exchange_source_order_id` / `replaced_order_id` | untuk tukar barang |

> `return_tracking_number` = resi retur yang dicari saat verifikasi paket balik di gudang.
> Untuk **tracking maju** (paket keluar), pakai `fulfillment.orders.{id}.tracking` (`202309`).
