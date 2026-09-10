## Catatan

*[Accurate](https://accurate.id/) (Accurate Online) adalah software akuntansi third-party — **sumber kebenaran pembukuan** Bharata (lihat [[ADR - 0001 Akuntansi via Accurate]]). ERP tidak membangun general ledger sendiri; data penjualan dijembatani ke Accurate.*

- **Status**: ✅ Implemented — dipakai [[Microservices - Integration Service]] (auto-sync RTS + manual send) dan sistem Finance lama ([[Finance - Bridging App]])
- **Endpoint prod**: langsung `zeus.accurate.id` (mode **API Token**: `Authorization: Bearer` + HMAC-SHA256 `X-Api-Timestamp`/`X-Api-Signature` dari secret key; tanpa sesi open-db). Env service integration: `ACCURATE_ACCOUNT_URL`, `ACCURATE_SECRET_KEY`, `ACCURATE_BEARER_TOKEN`.
- **Schema resmi**: OpenAPI `account.accurate.id/open-api/json.do` (diverifikasi 2026-07-10 untuk desain auto-sync). **Salinan utuh di repo** (sumber kebenaran yang dipakai sehari-hari): `bip-erp/docs/accurate-api/accurate-api-resmi.json` + pembaca `lihat.py` — lihat README-nya soal kenapa SwaggerHub `cpssoft/accurate-online_public_api` **dilarang** dipakai (terbukti usang & menyesatkan).
- **Webhook**: permukaan terpisah (tipe event, masa aktif 7 hari, model per-aplikasi) → **[[External - Accurate Webhook]]**.

## Fakta API yang dipakai integrasi (verified dari schema resmi)

- `POST /api/sales-invoice/save.do` — body JSON; required `customerNo` + `detailItem[]`; per baris required `itemNo` + `unitPrice`. **`itemNo` boleh duplikat antar baris** (dasar split baris per harga).
- **Edit dokumen** = header `id` (int internal Accurate) + per-baris `id`/`_status: delete`. Kirim ulang `number` sama **tidak terdokumentasi** sebagai upsert — jangan diandalkan.
- `GET /api/sales-invoice/detail.do` — menerima `id` **atau** `number`; sumber `id` internal + daftar `detailItem[].id` untuk protokol edit.
- `POST /api/sales-invoice/delete.do` — ada di client tapi **tidak dipakai** (kebijakan: faktur tak pernah dihapus; koreksi via edit/retur).
- `POST /api/sales-return/save.do` — retur; `InvoiceNumber` menunjuk faktur, `Number` dikosongkan (auto-nomor Accurate).
- **Bundle/paket**: tidak ada field bundle di invoice — bundle harus terdaftar sebagai **item paket di master Accurate**; ERP mem-mapping SKU marketplace → kode item via koleksi `accurate_products`.

## ⛔ `ACCURATE_DB_ID` di env prod SENGAJA kosong

**Jangan "melengkapi" env ini.** Token berformat `aat.…` (API Token) **sudah membawa sesi database**: memanggil `open-db.do` dengannya ditolak dengan pesan *"API Token ini sudah termasuk Sesi Database. Anda tidak perlu melakukan open-db.do lagi."* (dikunci tes `accurate_client_apitoken_session_test.go`).

Mengisi `ACCURATE_DB_ID` **bersama** token `aat.…` adalah kombinasi yang **mematikan seluruh sinkronisasi** — terjadi sebagai insiden **4 Agustus 2026**. Bentuk kegagalannya: client menyimpulkan mode OAuth (butuh sesi), lalu tiap call data membawa sesi yang tak pernah sah.

Kode punya **dua penjaga** yang memperingatkannya saat boot (grounded: `usecase/accurate_auth_usecase.go`):

| Penjaga | Memperingatkan bila |
|---|---|
| `WarnOnFallbackMismatch` | jenis token & `ACCURATE_DB_ID` tak berpasangan |
| `WarnOnDuplicateSlotTokens` | satu nilai token dipasang di lebih dari satu variabel — batas laju Accurate berlaku **PER TOKEN**, jadi slot bertoken sama tetap berbagi jatah dan multi-token tak memberi manfaat apa pun |

⚠️ Keduanya **peringatan log, bukan penolakan** — jadi env yang salah tetap boot dan tetap tampak hidup. **Baca log boot** setelah mengubah env Accurate. Aturan mode token selengkapnya: [[RUN - Accurate API Access Token (OAuth)]] §Mode token.

## Ongkos API terukur (prod, 2026-09-10)

Angka ini menentukan apakah sebuah fitur menarik sekali lalu menyaring, atau menarik per-entitas:

- **`glaccount/get-bs-account-amount.do?asOfDate=`** — **1,48 detik**, 56 KB, mengembalikan **347 akun neraca sekaligus dalam satu call**. ⚠️ Membacanya **per-akun** mengalikan biaya tanpa menambah informasi apa pun.
- **Volume jurnal ≈ 6.462/bulan** (terbukti Juli 2026) ≈ **208/hari** → menarik detail satu hari ≈ **211 call**.
- **Limiter Accurate 6 req/detik dibagi SELURUH service** — bukan per-job, bukan per-endpoint. Job yang menumpuk di jam yang sama saling merebut jatah laju, termasuk dari jalur yang menghadap pengguna. Ini alasan jadwal job Accurate sengaja disebar per menit ganjil (lihat [[IT - Background Jobs & Schedulers]]).

⛔ **Jurnal umum tak punya event webhook** (tak ada `JOURNAL_VOUCHER` di 24 tipe resmi), jadi jurnal manual finance **hanya** bisa didapat dengan menarik — dan angka di atas adalah ongkos yang harus dianggarkan untuk itu. Detail: [[External - Accurate Webhook]].

## Konsumen di ERP

- [[Microservices - Integration Service]] — **auto-sync RTS** (Sales Invoice otomatis saat order pickup kurir, 1 faktur/toko/hari WIB) + manual send summary report (Sales Invoice/Return/Income) + master mapping shop/product/bank/kv.
- [[APP - Web ERP]] — menu `integration-accurate` (tab Auto-Sync monitoring + Panduan finance + summary report manual).

## Dokumen Terkait

- [[External - Accurate Webhook]] — tipe event, `webhook-renew`/`webhook-history`, dua aplikasi bernama mirip
- [[Microservices - Integration Service]] — bridging Sales Invoice/Return ke Accurate
- [[API - Integration Service]] — daftar endpoint (termasuk `/accurate/daily-invoices`)
- [[ADR - 0001 Akuntansi via Accurate]]
- [[Finance - Bridging App]] · [[Finance - Big Pictures]] — konsumen akuntansi (sistem lama)
- [[Microservices - Insentive Service]] · [[Sales - Marketplace Integration]]
