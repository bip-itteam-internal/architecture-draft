# finance.get_statements

- Path: `/finance/202309/statements`
- Method: GET
- Auth: shop (`app_key` + `timestamp` + `shop_cipher` + `sign` di query; `x-tts-access-token` header)
- Deskripsi: **DAFTAR statement** (batch pencairan) satu toko dalam rentang waktu. Satu-satunya cara
  ERP *menanyakan* "statement apa saja yang ada" — endpoint `202501`
  (`statement_transactions`) menuntut kita **sudah tahu** nomor statement-nya.
- Sumber: `bip-erp/services/integration/internal/infrastructure/clients/tiktok_client_statements.go`
  (`TikTokClient.GetStatements`, verified-by-usage) — dipakai `cmd/statementdiscover`.
- Confidence: **verified-by-usage untuk path, parameter, dan `data.statements[].id` /
  `data.next_page_token`** (dipanggil ke prod 2026-09-07, mengembalikan 19 statement Agustus untuk
  satu toko). Field respons lain di bawah **dideklarasikan di struct kita tapi BELUM terbukti
  terisi** — ditandai eksplisit; verifikasi ke dok resmi sebelum mengandalkannya.

## Kenapa endpoint ini ada di ERP

Sebelum 2026-09-07 nomor statement hanya didapat **titipan** dari baris pesanan
(`tt_shop_transaction_by_orders.sku_transactions.statement_id`). Statement yang pesanannya tak
tercatat — atau yang isinya **cuma penyesuaian tanpa pesanan sama sekali** — tak pernah masuk
`tt_shop_statements`, sehingga seluruh alat hilir tak bisa menjangkaunya dan uang di dalamnya hilang
senyap. Terukur prod: satu toko punya 19 statement Agustus di TikTok tapi hanya 13 terdaftar.

## Request

| param | wajib | keterangan |
|---|---|---|
| `shop_cipher` | ya | standar semua endpoint shop |
| `page_size` | — | dikirim `100` oleh klien kita |
| `sort_field` | — | dikirim `statement_time` oleh klien kita |
| `statement_time_ge` | tidak | epoch detik, batas bawah **inklusif** |
| `statement_time_lt` | tidak | epoch detik, batas atas **EKSKLUSIF** — ikuti penamaan `_lt`, jangan diterjemahkan jadi inklusif |
| `page_token` | tidak | kosong = halaman pertama; ambil dari `data.next_page_token` |

## Response

`data` — dua field yang **dipakai & terbukti**:

| field | keterangan |
|---|---|
| `statements[]` | daftar statement |
| `next_page_token` | kosong = halaman terakhir |

`data.statements[]` — `id` **terbukti** (dipakai sebagai nomor statement). Sisanya dideklarasikan di
struct `StatementSummary` tapi **belum diverifikasi terisi**: `statement_time`, `currency`,
`settlement_amount`, `revenue_amount`, `fee_amount`, `adjustment_amount`, `shipping_cost_amount`,
`net_sales_amount`, `payment_status`, `payment_id`.

## ⚠️ Jangan campur penamaan dua endpoint statement

Endpoint ini (`202309`) dan `statement_transactions` (`202501`) memakai **nama field berbeda untuk
hal yang sama**:

| konsep | `202309` (daftar) | `202501` (isi statement) |
|---|---|---|
| waktu statement | `statement_time` | `create_time` |
| nilai statement | `settlement_amount` | `payable_amount` |

Karena itu `cmd/statementdiscover` memakai endpoint daftar **hanya untuk menemukan nomor**;
metadata yang disimpan ke `tt_shop_statements` tetap diambil dari `202501` lewat
`FetchStatementTransactions`, supaya semantiknya identik dengan yang ditulis
`tt-statement-reconciler`. Mencampurnya akan merusak perbandingan yang sudah ada.
