---
tags: [api-reference, lazada, endpoint, retur]
confidence: verified-live
verified: 2026-07-28
---

# `/reverse/getreverseordersforseller` — Daftar retur seller

Sumber retur Lazada untuk ERP. Dipakai `SyncReverseByID`, `BackfillReturns`, dan
`ResolveReturnByOrderID` di `internal/usecase/lazada_return.go`.

| | |
|---|---|
| **Path** | `/reverse/getreverseordersforseller` |
| **Method** | GET |
| **Auth** | `access_token` toko + `sign` (lihat [[README]]) |
| **Fungsi Go** | `LazadaClient.GetReverseOrdersForSeller(ctx, accessToken, tradeOrderID)` |

## Request

| Param | Wajib | Catatan |
|---|---|---|
| `trade_order_id` | tidak | **TIDAK BERFUNGSI** sebagai filter — lihat gotcha |
| *(param auth standar)* | ya | `app_key`, `timestamp` (ms), `sign_method`, `access_token`, `sign` |

## ⚠ Gotcha: filter `trade_order_id` tidak bekerja

Terverifikasi live: apa pun nilai `trade_order_id`, API **selalu mengembalikan daftar global**
seluruh reverse-order toko. Konsekuensinya, SEMUA pencarian retur Lazada harus:

1. tarik daftar,
2. cocokkan sendiri di sisi kita (`reverse_order_id` atau `trade_order_id`).

Ini yang membuat `fetchReverseItems` diekstrak jadi helper bersama di `lazada_return.go`.

Implikasi biaya: resolve-by-order (fallback gudang) menarik daftar penuh tiap panggilan.
Untuk toko dengan banyak retur ini berat — pertimbangkan cache pendek bila volume naik.

## Response

```
result.total                                   int     bisa > len(items) → paging (TBD)
result.items[]
  .reverse_order_id                            int64   → TransactionReturn.ReturnSN
  .request_type                                string  → Type + solution
  .trade_order_id                              int64   → order_id ERP
  .shipping_type                                string  belum dipakai
  .reverse_order_lines[]                                1 baris = 1 unit fisik
    .reverse_status                            string
    .ofc_status                                string
    .refund_amount                             int64   ⚠ SEN — bagi 100
    .item_unit_price                           int64   ⚠ SEN — bagi 100
    .reason_text                               string  → TransactionReturn.Reason
    .reason_code                               int64
    .is_need_refund                            bool
    .seller_sku_id                             string  → item SKU
    .tracking_number                           string  → resi BALIK (scan gudang)
    .return_order_line_gmt_create              int64   unix DETIK → RequestedAt
    .product.product_sku                       string
```

### Pemetaan `reverse_status` → enum internal

| Lazada | Internal (`tracking.Return*`) | `return_request_status` (mentah, lintas-MP) |
|---|---|---|
| `REFUND_SUCCESS` | `REFUNDED` (final) | `RETURN_OR_REFUND_REQUEST_COMPLETE` |
| `REQUEST_CANCEL` | `CANCELLED` (final) | `RETURN_OR_REFUND_REQUEST_CANCEL` |
| lainnya | `UNKNOWN` (belum final) | `""` (jangan tulis nilai ngawur) |

### Pemetaan `request_type` → `solution`

| `request_type` | `solution` | Arti |
|---|---|---|
| `REFUND` (case-insensitive) | 1 | refund-only — barang tak balik, **tak** menunggu gudang |
| lainnya / kosong | 0 | barang balik — **ditahan** sampai gudang scan ([[ADR - 0025]]) |

⚠ **TBD**: enum `request_type` yang terverifikasi live baru `"RETURN"`. Pemetaan `"REFUND"`
disusun dari penamaannya, belum terbukti dari data prod. Nilai tak dikenal sengaja jatuh ke 0
(sisi aman: tertahan menunggu manusia, bukan terbukukan dengan asumsi keliru).

## Cara membuktikan

```
GET /lazada/debug/reverse?store_id=<seller_id>&trade_order_id=<id>&reverse_order_id=<id>
```
Admin-only, mengembalikan JSON mentah. Menyentuh data produksi — minta izin dulu.

## TBD terbuka

- Paging: `result.total > len(items)` baru di-log warning, belum ditangani.
- Apakah `tracking_number` konsisten terisi (kalau kosong, scan resi-balik gudang gagal).
- Apakah satu `reverse_order_line` bisa qty > 1 (kode kini mengasumsikan tepat 1).
