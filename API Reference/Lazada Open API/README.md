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
- **Angka JSON di payload webhook tersimpan sebagai BSON `double`.** `CreateWebhookLazada`
  mem-parse body ke `any`, jadi tiap angka JSON jadi `float64` lalu `double` di
  `webhook_logs.payload`. Processor dulu mendeklarasikan `reverse_order_id` sebagai
  `string` → `bson.Unmarshal` gagal & SELURUH webhook mati. **Diperbaiki 2026-08-06**
  lewat tipe `lazadaID` (terima string/double/int32/int64/null, normalkan ke string
  desimal) — **belum deploy prod**. Lihat §Push Mechanism di bawah.
- **Jangan format float64 payload dengan `%v`/`fmt.Sprint`.** `fmt.Sprintf("%v", 1.234567890123e+12)`
  menghasilkan notasi ilmiah, bukan digit. `SyncReverseByID` mencocokkan dengan
  `strconv.FormatInt(item.ReverseOrderID, 10)` — string bernotasi ilmiah tak akan pernah cocok,
  dan `SyncReverseByID` mengembalikan `nil` (dianggap "belum muncul di list") saat tak cocok.
  Hasilnya webhook **sukses tapi retur tak masuk** — gagal lebih senyap daripada bug sekarang.
  Konversi yang benar: `strconv.FormatInt(int64(f), 10)`.

## Push Mechanism (LPM) — payload webhook masuk

Selain endpoint yang KITA panggil (tabel di [[Index]]), Lazada mendorong notifikasi ke
`POST /webhooks/services/lazada` (handler `CreateWebhookLazada` di
`internal/interface/http/webhook_handler.go`). Payload disimpan mentah ke `webhook_logs`,
di-ack cepat, lalu diproses async oleh `LazadaPushProcessor`
(`internal/webhook/processor/lazada_push.go`).

Bentuk payload yang dikirim Lazada:

```
seller_id                     string|angka  → store_id (= seller_id numerik)
message_type                  int           0 = trade order actions
data.order_status             string
data.status_update_time       int64
data.trade_order_id           string        (di push trade-order; lihat Confidence)
data.trade_order_line_id      ?             belum terverifikasi
data.reverse_order_id         ANGKA         verified-live
timestamp                     int64
site                          string
```

**Yang benar-benar di-decode kode** hanya tiga: `seller_id`, `data.trade_order_id`,
`data.reverse_order_id` — semuanya bertipe `lazadaID` (menerima string maupun angka,
selalu dinormalkan ke string desimal). Struct sengaja dipersempit: tiap field yang
dideklarasikan ikut menentukan hidup-matinya webhook, karena `bson.Unmarshal` berjalan
sebelum percabangan dan satu field salah tipe menggagalkan SEMUANYA. Field sisanya
didokumentasikan di sini saja, tidak di struct. Kalau nanti perlu ditambahkan, pakai
`lazadaID` untuk identitas dan pastikan tipe aslinya sudah terbukti — jangan diasumsikan.

Percabangan processor: `reverse_order_id` terisi → `SyncReverseByID` (jalur retur); selain itu
`trade_order_id` → `FetchAndTransformOrder` → upsert order.

**Confidence**: jalur order `verified-by-usage` (jalan di prod sejak 23 Juli 2026).
`reverse_order_id` bertipe **angka** = `verified-live` — dibuktikan error decode produksi
2026-08-06 (`cannot decode double into a string type`).

`trade_order_id` & `seller_id` pada push **trade-order** = `verified-by-usage` **secara
tak langsung**: sebelum perbaikan keduanya dideklarasikan `string`, dan karena decoder BSON
menggagalkan seluruh dokumen begitu satu key salah tipe, jalur order yang jalan normal sejak
23 Juli membuktikan keduanya memang datang sebagai string. Yang **masih TBD** adalah tipenya
pada push **reverse** — error prod berhenti di key gagal pertama (`reverse_order_id`), jadi
tak membuktikan apa pun soal field lain di pesan itu. Karena itu `lazadaID` tetap dipasang
pada ketiganya, bukan hanya `reverse_order_id`.

## Confidence

Setiap file di `Endpoints/` menyebut salah satu:

- `verified-live` — pernah dilihat langsung dari respons Lazada (debug endpoint / log prod)
- `verified-by-usage` — dipakai kode produksi dan jalan, tapi field lengkapnya belum diaudit
- `TBD` — belum terbukti; jangan dijadikan dasar keputusan pembukuan
