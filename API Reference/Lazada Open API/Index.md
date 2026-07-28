---
tags: [api-reference, lazada, index]
---

# Lazada Open API — Index Endpoint

Endpoint yang **benar-benar dipanggil** ERP, diambil dari
`bip-erp/services/integration/internal/infrastructure/clients/lazada_client.go`.
Bukan daftar lengkap API Lazada — hanya yang terpakai (`verified-by-usage` minimal).

Aturan, auth/sign, & gotcha: [[README]].

| Path | Method | Fungsi Go | Dipakai untuk | Confidence |
|---|---|---|---|---|
| `/orders/get` | GET | `GetOrders`, `GetOrdersRange` | Tarik order per rentang `created_after`/`created_before` (paging offset+limit) | verified-by-usage |
| `/order/get` | GET | `GetOrder` | Detail 1 order | verified-by-usage |
| `/order/items/get` | GET | `GetOrderItems` | Item + `tracking_code` (resi forward) 1 order | verified-by-usage |
| `/logistic/order/trace` | GET | `GetOrderTrace` | Checkpoint logistik forward | verified-by-usage |
| `/reverse/getreverseordersforseller` | GET | `GetReverseOrdersForSeller` | **Daftar retur (reverse-order) seller** | verified-live |
| `/order/reverse/return/detail/list` | GET | `GetReverseOrderDetail` | Detail 1 reverse-order | TBD — belum dipakai jalur produksi |
| `/finance/transaction/details/get` | GET | `GetTransactionDetails` | Rincian fee/biaya per order | verified-by-usage |
| `/finance/transaction/accountTransactions/query` | POST | `GetAccountTransactions` | Mutasi wallet / withdrawal | verified-by-usage |
| `/finance/payout/status/get` | GET | `GetPayoutStatus` | Statement payout + `closing_balance` | verified-by-usage |
| `/seller/get` | GET | `GetSeller` | `seller_id` numerik (kunci `store_id`) | verified-live |

## Catatan retur

`/reverse/getreverseordersforseller` adalah **satu-satunya** sumber retur yang dipakai produksi.
Bentuk responsnya (`lazadaReverseResponse` di `internal/usecase/lazada_return.go`):

```
result.total                                   int
result.items[].reverse_order_id                int64   → return_sn
result.items[].request_type                    string  → "RETURN" (…"REFUND"? TBD)
result.items[].trade_order_id                  int64   → order_id ERP
result.items[].shipping_type                   string  (belum dipakai)
result.items[].reverse_order_lines[]                   1 baris = 1 unit fisik
  .reverse_status                              string  REFUND_SUCCESS | REQUEST_CANCEL | …
  .ofc_status                                  string
  .refund_amount                               int64   SEN (÷100)
  .item_unit_price                             int64   SEN (÷100)
  .reason_text / .reason_code
  .is_need_refund                              bool
  .seller_sku_id                               string  → SKU
  .tracking_number                             string  → resi BALIK (scan gudang)
  .return_order_line_gmt_create                int64   unix DETIK
  .product.product_sku                         string
```

**TBD yang masih terbuka** (butuh probe `/lazada/debug/reverse`):
- Enum lengkap `request_type` — baru "RETURN" yang terlihat. Apakah ada nilai refund-only?
  Ini menentukan `solution` (0 barang-balik vs 1 refund-only) → menentukan gerbang gudang.
- Enum lengkap `reverse_status` di luar `REFUND_SUCCESS`/`REQUEST_CANCEL`.
- Apakah `tracking_number` benar-benar terisi. Kalau kosong, scan resi-balik gudang gagal
  dan fallback "input nomor order" jadi satu-satunya jalan.
- Apakah satu `reverse_order_line` bisa mewakili qty > 1.
