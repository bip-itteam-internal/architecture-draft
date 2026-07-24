## Deskripsi

*[Desty](https://desty.app/) adalah middleware/SaaS **orkestrasi order** pihak ketiga (Indonesia) — satu pintu yang menyatukan banyak marketplace (a.l. TikTok Shop, Shopee, Lazada, Blibli, Zalora). Di bip-erp, Desty bukan service sendiri melainkan **integrasi eksternal** yang ditangani [[Microservices - Integration Service]]: menerima webhook order, melakukan auto-ship/approve sadar-holiday, dan menjadi salah satu sumber order untuk bridging akuntansi ke [[External - Accurate]].*

> **Cakupan di bip-erp:** client marketplace **khusus** baru **TikTok Shop & Shopee** (ada `ShipOrder` masing-masing). Platform Desty lain (mis. Lazada/Blibli/Zalora) di-auto-approve **generik** lewat Desty `POST /api/order/accept` — **tanpa** client khusus (konsisten dgn catatan "tidak ada client Lazada" di [[Microservices - Integration Service]]).

- **Status**: ⚠️ Implemented (ada catatan) — **soft-disabled per 2026-07-12**; kode masih ada, tapi seluruh registrasi runtime (route, processor, credential task) dicabut dari `main.go`
- **Sisi vendor**: produk SaaS eksternal (akun + kredensial dikelola via ENV)
- **Detail implementasi**: ada di [[Microservices - Integration Service]] (dok ini hanya level vendor/konsep + pointer)

> **SOFT-DISABLED (2026-07-12).** Traffic Desty di prod terbukti mati (total 18 webhook sepanjang masa, terakhir 2026-06-24, nol task diproses) — seluruh order TikTok & Shopee kini masuk via webhook **direct** masing-masing platform (`TiktokDirectProcessor` / `ShopeePushProcessor`). Yang dicabut dari `services/integration/main.go` (branch `chore/disable-desty-webhook`): route `POST /webhooks/services/desty` + `GET /webhooks/accounts/desty`, registrasi `DestyTiktokProcessor` + `DestyShopeeProcessor`, dan `DestyCredentialTask`. File `desty_*` dan konstruksi `destyRepo`/`destyClient` tetap ada (dependency `NewWebhookUseCase`) — rollback = revert 1 commit. Deskripsi peran di bawah = **historis**.

## Peran di bip-erp

- **Webhook order masuk** — Desty mengirim event order lintas-platform → di-*ingest* lewat `POST /webhooks/services/desty` (auth `key` + `accessToken`), lalu di-enqueue ke queue untuk diproses.
- **Auto-ship / auto-approve sadar-holiday** — saat order baru: ship hanya pada **00:01–14:59 WIB**; ditunda (`PENDING`) bila **>15:00 WIB** atau **hari libur** (varian Shopee juga menunda bila **besok** libur). Eksekusi per platform: Shopee/TikTok via ship-order masing-masing, selain itu via Desty `POST /api/order/accept`.
  - **Pengganti in-house UTAMA (2026-07-23): menu WMS "Perlu Diproses"** — meniru tab *Siap Dikirim → Perlu diproses* Desty. Admin gudang melihat order belum-berresi, memilih batch, klik **"Proses Pengiriman"** → resi terbit (`POST /fulfillment/arrange` → `ship-batch`). Dipilih **manual, bukan otomatis**, karena praktik lapangan menunjukkan admin butuh mengatur *ritme* (proses saat gudang siap kemas) dan *menyaring* (menahan order bermasalah). Lihat [[Microservices - Warehouse Service]] & [[WH - Fulfillment Flow & WMS Tinggarjaya]].
    - 🔴 **BLOCKER CUTOVER (simulasi pertama 2026-07-24):** order yang di-arrange lewat menu ini **tidak sampai ke WMS** — marketplace tampaknya tidak mengirim webhook untuk perubahan yang kita sendiri sebabkan, dan `ShipBatch` tak memanggil `NotifyWarehouse` langsung (2/2 sampel TikTok gagal masuk antrian). Jaring pengaman reconciler kebetulan juga sedang macet hari itu. **Desty tetap jadi jalur operasional** sampai celah ini ditutup. Catatan tambahan: daftar Shopee menggelembung ~198 order karena `raw_status` tak disegarkan di jalur push webhook, jadi **jangan pakai selisih angka Shopee vs Desty untuk menilai akurasi** sebelum diperbaiki. Detail: [[Microservices - Integration Service]].
  - **Pengganti otomatis (Gap 2, DORMANT):** logika sadar-holiday ini juga direplikasi sebagai worker **`auto-arrange`** di integration (lihat [[IT - Background Jobs & Schedulers]] & [[Microservices - Integration Service]]) — mengambil order `raw_status` siap-kirim (termasuk COD) → `ShipBatch`. **Landing DORMANT** di balik env `AUTO_ARRANGE_ENABLED` (default off); dinyalakan **hanya saat cutover Desty→WMS** (WMS gudang mulai dipakai & arrange manual Desty dihentikan). Sampai flag on, arrange masih via Desty App operasional.
- **Token rotation** — token Bearer Desty disimpan sebagai **current + previous** (jendela aman saat rotasi) dan di-refresh cron **tengah malam** (`0 0 0 * * *`, buffer kedaluwarsa 5 hari).

## Konfigurasi & Kredensial

- **ENV**: `DESTY_BASE_URL`, `DESTY_APPLY_ID`, `DESTY_USERNAME`, `DESTY_MOBILE`
- **Endpoint Desty yang dipakai**: `POST /api/auth/token` (ambil Bearer token), `POST /api/order/accept` (auto-approve order)
- **Sisi bip-erp**: webhook landing `POST /webhooks/services/desty`; daftar account via `GET /webhooks/accounts/desty`

## Catatan

- **2026-07-12**: seluruh jalur Desty **soft-disabled** (lihat blok status di atas). `POST /webhooks/services/desty` kini 404.
- Cron 01:00 `refreshDestyToken` + `ProcessPendingAutoShip` di `internal/cmd/cron.go` (`CronManager`) ternyata **dead code** — tidak pernah dipanggil dari `main.go`; refresh kredensial yang sempat aktif adalah `DestyCredentialTask` (worker, 00:00), kini juga dicabut.
- Historis: route webhook Desty langsung (`/webhook/desty`, `/webhooks/desty`) **di-comment** — digantikan `/webhooks/services/desty` (lihat [[Microservices - Integration Service]]).

## Dokumen Terkait

- [[Microservices - Integration Service]] — implementasi (webhook ingest, auto-approve, token rotation)
- [[External - Accurate]] — bridging akuntansi hilir (sesama integrasi eksternal)
- [[Finance - Bridging App]] · [[Sales - Marketplace Integration]] — konsumen/konsep sisi finance & marketing
- [[DB - Overview and Notes]] — MongoDB & Redis (queue `srv:integration`)
