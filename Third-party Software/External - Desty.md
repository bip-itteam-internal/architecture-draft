## Deskripsi

*[Desty](https://desty.app/) adalah middleware/SaaS **orkestrasi order** pihak ketiga (Indonesia) — satu pintu yang menyatukan banyak marketplace (a.l. TikTok Shop, Shopee, Lazada, Blibli, Zalora). Di bip-erp, Desty bukan service sendiri melainkan **integrasi eksternal** yang ditangani [[Microservices - Integration Service]]: menerima webhook order, melakukan auto-ship/approve sadar-holiday, dan menjadi salah satu sumber order untuk bridging akuntansi ke [[External - Accurate]].*

> **Cakupan di bip-erp:** client marketplace **khusus** baru **TikTok Shop & Shopee** (ada `ShipOrder` masing-masing). Platform Desty lain (mis. Lazada/Blibli/Zalora) di-auto-approve **generik** lewat Desty `POST /api/order/accept` — **tanpa** client khusus (konsisten dgn catatan "tidak ada client Lazada" di [[Microservices - Integration Service]]).

- **Status**: ✅ Implemented — integrasi aktif lewat [[Microservices - Integration Service]]
- **Sisi vendor**: produk SaaS eksternal (akun + kredensial dikelola via ENV)
- **Detail implementasi**: ada di [[Microservices - Integration Service]] (dok ini hanya level vendor/konsep + pointer)

## Peran di bip-erp

- **Webhook order masuk** — Desty mengirim event order lintas-platform → di-*ingest* lewat `POST /webhooks/services/desty` (auth `key` + `accessToken`), lalu di-enqueue ke queue untuk diproses.
- **Auto-ship / auto-approve sadar-holiday** — saat order baru: ship hanya pada **00:01–14:59 WIB**; ditunda (`PENDING`) bila **>15:00 WIB** atau **hari libur** (varian Shopee juga menunda bila **besok** libur). Eksekusi per platform: Shopee/TikTok via ship-order masing-masing, selain itu via Desty `POST /api/order/accept`.
- **Token rotation** — token Bearer Desty disimpan sebagai **current + previous** (jendela aman saat rotasi) dan di-refresh cron **tengah malam** (`0 0 0 * * *`, buffer kedaluwarsa 5 hari).

## Konfigurasi & Kredensial

- **ENV**: `DESTY_BASE_URL`, `DESTY_APPLY_ID`, `DESTY_USERNAME`, `DESTY_MOBILE`
- **Endpoint Desty yang dipakai**: `POST /api/auth/token` (ambil Bearer token), `POST /api/order/accept` (auto-approve order)
- **Sisi bip-erp**: webhook landing `POST /webhooks/services/desty`; daftar account via `GET /webhooks/accounts/desty`

## Catatan

- Route webhook Desty langsung (`/webhook/desty`, `/webhooks/desty`) **di-comment** — digantikan `/webhooks/services/desty` (lihat [[Microservices - Integration Service]]).

## Dokumen Terkait

- [[Microservices - Integration Service]] — implementasi (webhook ingest, auto-approve, token rotation)
- [[External - Accurate]] — bridging akuntansi hilir (sesama integrasi eksternal)
- [[Finance - Bridging App]] · [[Sales - Marketplace Integration]] — konsumen/konsep sisi finance & marketing
- [[DB - Overview and Notes]] — MongoDB & Redis (queue `srv:integration`)
