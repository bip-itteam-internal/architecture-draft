---
tags: [api-reference, lazada, integration]
---

# Lazada Open Platform API — Referensi

Folder ini menampung spesifikasi endpoint **Lazada Open Platform** yang dipakai ERP.
Dipanggil lewat `/lazada` (lihat `.claude/commands/lazada.md`).

Pola & aturannya sama dengan [[Shopee Open API v2]] dan [[TikTok Shop API]], dengan satu
perbedaan penting: **Lazada tak punya backend doc JSON publik**, tapi **punya endpoint debug
live** di service integration — jadi field bisa DIBUKTIKAN, bukan ditebak.

## Sumber kebenaran, berurut

1. **Kode kita** — `bip-erp/services/integration/internal/infrastructure/clients/lazada_client.go`
   dan struct di `internal/usecase/lazada_*.go`. Path & field di sini `verified-by-usage`:
   ia benar-benar jalan di produksi.
2. **Endpoint debug live** (`/lazada/debug/*`) — mengembalikan JSON MENTAH dari Lazada.
   Ini yang menaikkan confidence jadi `verified-live`.
3. **Portal resmi** `open.lazada.com/apps/doc/api` — butuh login, jadi tak bisa di-fetch agent.

## Auth & sign

Host per negara (`lazadaDataHostByCountry`); Indonesia = `https://api.lazada.co.id/rest`.

Query param wajib pada tiap panggilan terproteksi:

| Param | Nilai |
|---|---|
| `app_key` | dari env `LAZADA_APP_KEY` |
| `timestamp` | unix **milidetik** (bukan detik) |
| `sign_method` | `sha256` |
| `access_token` | token toko (per store) |
| `sign` | lihat di bawah |

```
sign = UPPER(hex(HMAC_SHA256(
         key  = app_secret,
         data = apiName + concat(sortedKeys[i] + values[i])   // "sign" dikecualikan
       )))
```

`apiName` = path endpoint (mis. `/orders/get`). Beda dari TikTok yang menaruh `app_secret` di
kedua ujung data. Implementasi: `LazadaClient.sign()`.

## Gotcha yang sudah terbukti

- **Satuan SEN.** `refund_amount` & `item_unit_price` pada reverse-order dalam SEN → bagi 100
  untuk rupiah. Terverifikasi live (GATE 1). Jangan asumsikan rupiah.
- **Filter `trade_order_id` pada `/reverse/getreverseordersforseller` TIDAK BERFUNGSI** —
  selalu mengembalikan daftar global. Semua pencarian retur (by reverse_order_id maupun by
  trade_order_id) terpaksa menarik daftar lalu mencocokkan di sisi kita.
- **Paging reverse-order belum lengkap.** `result.total` bisa > `len(result.items)`; kode saat
  ini memproses halaman pertama saja dan menulis warning. TBD.
- **`store_id` = `seller_id` numerik**, bukan email. Ada migrasi khusus untuk ini
  (`/lazada/migrate-store-key`). `accurate_shops` channel LAZADA wajib di-key dengan nilai yang
  sama, kalau tidak faktur gagal dengan `ErrAccurateShopNotFound`.
- **Retur Lazada hanya masuk lewat webhook reverse-order.** Tak ada worker penyapu berkala
  (Shopee & TikTok punya). Kalau webhook meleset, retur tak masuk dengan sendirinya — pemicu
  manual yang tersedia: `POST /lazada/backfill-returns` dan fallback gudang "input nomor order".

## Confidence

Setiap file di `Endpoints/` menyebut salah satu:

- `verified-live` — pernah dilihat langsung dari respons Lazada (debug endpoint / log prod)
- `verified-by-usage` — dipakai kode produksi dan jalan, tapi field lengkapnya belum diaudit
- `TBD` — belum terbukti; jangan dijadikan dasar keputusan pembukuan
