## Deskripsi

*Inventaris **proses yang berjalan diam-diam** di bip-erp — cron/scheduler/worker latar belakang: apa yang jalan, kapan, di service mana, untuk apa, dan lock-nya. Grounded dari kode (`bson`/cron string disalin verbatim). Tujuannya: tak ada "sistem tersembunyi" yang tak diketahui saat debugging, perencanaan kapasitas, atau mengubah service.*

- **Status**: ✅ Implemented — 26 job terjadwal + 1 dispatcher webhook (per audit kode; +4 job integration ditambahkan 2026-07-11: affiliate Shopee AMS performance/conversion & WMS resi bridge `sync-resi-wms`/`sync-shopee-tracking`; +1 guardian order Shopee `sync-shopee-orders` 2026-07-14, **belum deploy**; +1 guardian retur Shopee `sync-shopee-returns` 2026-07-15 & +1 guardian retur TikTok `recover-tiktok-returns` 2026-07-16 — memicu booking Retur Penjualan yang selama ini tak pernah menyala, **belum deploy**; +1 sync ulasan marketplace `sync-reviews` 2026-07-19 harian 06:45, **LIVE**; +3 job Packet Tracking `sync-tracking`/`detect-stuck`/`sync-return-tracking` 2026-07-17..18 — checkpoint pengiriman forward+retur & deteksi mandek, **LIVE**). *3 job reminder attendance (koreksi/leave/tukar jadwal) + auto-ignore koreksi & tukar jadwal + pre-alokasi sadar-swap dari **PR #165** — belum rilis ke prod.*
- **Zona waktu**: semua **Asia/Jakarta (WIB)** kecuali override env `INTEGRATION_WORKER_TZ`
- **Sintaks cron**: integration pakai `robfig/cron` **6-field** (`detik menit jam tgl bln dow`); attendance/employee/notification pakai **5-field** klasik

## Job Terjadwal (time-scheduled)

| Service | Jadwal (WIB) | Untuk apa | Lock | File:line |
|---|---|---|---|---|
| employee | harian 04:00 (`0 4 * * *`) | sync company work schedule | — | `services/employee/cron.go:29` |
| employee | tgl 1 / bulan 08:45 (`45 8 1 * *`) | broadcast reminder KPI (FCM + inbox) | — | `services/employee/cron.go:34` |
| employee | 1 Jan 00:05 (`5 0 1 1 *`) | reset kuota cuti tahunan (used→0) | — | `services/employee/cron.go:37` |
| attendance | tiap 30 mnt (`*/30 * * * *`) | pre-alokasi entry absensi ~2j sebelum shift; pending→alpha saat shift mulai; perhitungkan **cuti & tukar jadwal** disetujui (swap kedua sisi via `WorkTimeFor`) | — | `services/attendance/cron.go:28` |
| attendance | tiap jam (`0 * * * *`) | auto-ignore **leave + koreksi presensi + tukar jadwal** basi (>24j) + FCM — termasuk tahap consent rekan | — | `services/attendance/cron.go:38` |
| attendance | tiap jam (`0 * * * *`) | **reminder reviewer koreksi** basi (T+18j, ~6j sblm auto-ignore) → SPV/HR FCM | — | `services/attendance/cron.go:41` |
| attendance | tiap jam (`0 * * * *`) | **reminder reviewer leave** basi (T+18j) → SPV/HR FCM | — | `services/attendance/cron.go:42` |
| attendance | tiap jam (`0 * * * *`) | **reminder tukar jadwal** basi (T+18j) → rekan/atasan/HRD FCM | — | `services/attendance/cron.go:43` |
| insentive | harian 00:00 (akhir bulan: 15:00 Sn–Jm / 12:00 Sb) | hitung insentif otomatis; tarik metrik TikTok/Shopee; carry-over tgl 1–7 | Mongo `cron_locks` TTL 2j | `services/insentive/cron_worker.go:63` |
| task-management | tiap jam (delay awal 1 mnt) | eskalasi SLA task (warning ke SPV / breach ke admin) | — | `services/task-management/reminder.go:12` |
| notification | harian 03:00 (`0 3 * * *`) | hapus `inbox` > 2 bulan | — | `services/notification/cron.go:20` |
| integration | ~~harian 01:00~~ **dead code** | ~~refresh token Desty + retry order PENDING~~ — `CronManager` tidak pernah dipanggil dari `main.go` (verifikasi 2026-07-12) | Redis | `services/integration/internal/cmd/cron.go:34` |
| integration | **4× sehari** 00:00/08:00/16:00/23:00 (`0 0 0,8,16,23 * * *`) | sync order TikTok Shop (semua shop authorized, window **48 jam** overlap by `create_time`) | Redis `lock:sync-tt-shop-orders` (15m) | `.../worker/tasks/tt_shop_sync_orders.go:35` |
| integration | harian 00:00 (`0 0 0 * * *`) | sync master data TikTok Business | Redis `lock:sync-tt-business-master-data` (15m) | `.../worker/tasks/tt_business_master_data.go:45` |
| integration | harian 01:00 (`0 0 1 * * *`) | sync report GMV-Max | Redis `lock:sync-tt-business-gmv-max-report` (15m, conc. 5) | `.../worker/tasks/tt_business_gmv_max_report.go:33` |
| integration | harian 02:00 (`0 0 2 * * *`) | sync integration report | Redis `lock:sync-tt-business-integration-report` (15m) | `.../worker/tasks/tt_business_integration_report.go:35` |
| integration | harian 00:00 (`0 0 0 * * *`) | sync master data TikTok Shop (produk/kategori) | Redis `lock:sync-tt-shop-master-data` (15m) | `.../worker/tasks/tt_shop_master_data.go:34` |
| integration | **tiap 5 detik** (`*/5 * * * * *`) | konsumsi antrian webhook `webhook_tasks` & dispatch | Redis `lock:webhook-consumer` (5m) | `.../worker/tasks/webhook_consumer_task.go:36` |
| integration | ~~harian 00:00~~ **dicabut 2026-07-12** | ~~refresh kredensial Desty~~ — registrasi task dihapus dari `main.go` ([[External - Desty]] soft-disabled) | Redis `lock:desty-credential-task` (5m) | `.../worker/tasks/desty_credential_task.go:40` |
| integration | harian 02:00 (`0 0 2 * * *`) | sync performa Shopee GMS (item & campaign) | Redis `lock:sync-shopee-performance` (30m) | `.../worker/tasks/shopee_sync_task.go:30` |
| integration | **tiap 4 jam** 00/04/08/12/16/20 (`0 0 */4 * * *`) | **guardian order Shopee**: tarik-ulang order (window trailing-overlap 8j, env `SHOPEE_ORDER_GUARDIAN_LOOKBACK_HOURS`) sbg fallback bila push/webhook tak tersimpan; app ERP_SYSTEM, honest-partial. ⚠️ belum deploy | Redis `lock:sync-shopee-orders` (60m) | `.../worker/tasks/shopee_orders_sync_task.go` |
| integration | **tiap 2 jam** (`0 0 */2 * * *`) | **guardian retur Shopee**: `SyncReturns` per toko lewat usecase **wired `rtsUseCase`** → memicu booking **Retur Penjualan** yang eligible (gated `RTS_RETURN_ENABLED`, idempoten). Menutup bug: transisi retur→ACCEPTED di-ingest jalur nil-wired → trigger booking tak pernah menyala (0 retur terbukukan). Window trailing **60 hari** by `create_time` (env `SHOPEE_RETURN_GUARDIAN_LOOKBACK_DAYS`, clamp 120) krn retur telat matang; honest-partial. ⚠️ belum deploy | Redis `lock:sync-shopee-returns` (30m) | `.../worker/tasks/shopee_returns_sync_task.go` |
| integration | **tiap 2 jam** (`0 30 */2 * * *`) | **guardian retur TikTok** `recover-tiktok-returns` (2026-07-16): recovery-based (TikTok tak punya pencarian retur by-waktu) — pindai order TikTok RETURNED (window env `TIKTOK_RETURN_RECOVER_LOOKBACK_DAYS`, default 30, clamp 90), isi data retur via `FetchAndSetTikTokReturn`, drive `SyncOrderReturn` (semua pengaman). Menutup celah: retur TikTok dulu hanya webhook, sekali meleset hilang. ⚠️ belum deploy | Redis `lock:recover-tiktok-returns` (30m) | `.../worker/tasks/tiktok_returns_recover_task.go` |
| integration | harian 05:05 (`0 5 5 * * *`) | proaktif refresh token semua Shopee shop (buffer sebelum expiry 06:00) | Redis `lock:shopee-credential-task` (30m) | `.../worker/tasks/shopee_credential_task.go:30` |
| integration | tiap jam :00 (`0 0 * * * *`) | rekonsiliasi income/escrow Shopee | Redis `lock:shopee-escrow-reconciler` | `.../worker/tasks/shopee_escrow_reconciler.go` |
| integration | tiap jam :30 (`0 30 * * * *`) | rekonsiliasi income TikTok per order (refetch settlement) | Redis `lock:income-reconciler` | `.../worker/tasks/tt_income_reconciler.go` |
| integration | **4× sehari** 00:00/08:00/16:00/23:00 (`0 0 0,8,16,23 * * *`) | sync affiliate orders TikTok Seller | Redis `lock:sync-affiliate-orders` (15m) | `.../worker/tasks/affiliate_orders_sync.go` |
| integration | mingguan Minggu 02:00 (`0 0 2 * * 0`) | refresh status affiliate orders 89 hari terakhir | Redis `lock:refresh-affiliate-orders` | `.../worker/tasks/affiliate_orders_refresh.go` |
| integration | harian 04:00 (`0 0 4 * * *`) | validasi komisi affiliate vs finance statement lokal | Redis `lock:validate-affiliate-commission` | `.../worker/tasks/affiliate_commission_validate.go` |
| integration | harian 02:30 (`0 30 2 * * *`) | sync video performance TikTok Shop | Redis `lock:sync-tt-shop-video-performance` | `.../worker/tasks/tt_shop_video_performance_task.go` |
| integration | harian **06:45** (`0 45 6 * * *`) | **sync ulasan marketplace** (`sync-reviews`): komentar Shopee incremental (cap 500/query, snapshot harian di-recompute dari DB) + distribusi bintang kumulatif TikTok per produk (1 call/produk, throttle 500ms) + enrichment nama produk (order + fallback API produk). Jadwal sengaja pagi — hindari bentrok quota dgn rumpun sync 00:00–02:00. LIVE 2026-07-19 (26 toko) | Redis `lock:sync-reviews` (60m) | `.../worker/tasks/sync_reviews.go` |
| integration | **4× sehari** 00:00/08:00/16:00/23:00 (`0 0 0,8,16,23 * * *`) | sync report GMV-Max **hari ini** (intraday update) | Redis `lock:sync-tt-business-gmv-max-report-today` (15m) | `.../worker/tasks/tt_business_gmv_max_report_today.go:34` |
| integration | harian 03:00 (`0 0 3 * * *`) | sync performa affiliate Shopee AMS (v1 snapshot per-affiliate + v3 product/content) | Redis `lock:sync-shopee-affiliate-performance` (30m) | `.../worker/tasks/shopee_affiliate_sync_task.go:31` |
| integration | **tiap 30 mnt** (`0 */30 * * * *`) | **`sync-tracking`** (Packet Tracking forward): tarik checkpoint API resmi MP (Shopee `get_tracking_info` / TikTok `/fulfillment/202309/orders/{id}/tracking`) utk order non-terminal belum DELIVERED + final-sync 1× saat COMPLETED + enrich resi/provider. Isi sub-dok `tracking` | Redis `lock:sync-tracking` | `.../worker/tasks/sync_tracking.go` |
| integration | tiap jam :15 (`0 15 * * * *`) | **`detect-stuck`** (deteksi order mandek): scan **hanya SHIPPED/IN_TRANSIT** (window `order_date ≥ now-14hr`) vs threshold per-stage (config KV `stuck_thresholds`), set/clear sub-dok `stuck` + `ClearStuckOlderThan` | Redis `lock:detect-stuck` | `.../worker/tasks/detect_stuck.go` |
| integration | tiap jam :20 (`0 20 * * * *`) | **`sync-return-tracking`** (retur): Shopee `get_reverse_tracking_info` (checkpoint hub) / TikTok `Search Returns` (resi+kurir+milestone, tanpa checkpoint) → sub-dok `return_tracking`; SELALU tulis `last_sync_at` (backoff, cegah re-sync storm refund-only) | Redis `lock:sync-return-tracking` | `.../worker/tasks/sync_return_tracking.go` |
| integration | harian 05:00 (`0 0 5 * * *`) | sync konversi order-level + validasi komisi affiliate Shopee AMS (v2) | Redis `lock:sync-shopee-affiliate-conversion` (30m) | `.../worker/tasks/shopee_affiliate_conversion_sync_task.go:32` |
| integration | **tiap :05 & :35** (`0 5,35 * * * *`) | **WMS resi**: fetch AWB Shopee (`get_tracking_number`) untuk order shippable tanpa resi — dijalankan sebelum `sync-resi-wms` | Redis `lock:sync-shopee-tracking` (12m) | `.../worker/tasks/sync_shopee_tracking.go:28` |
| integration | **tiap 10 menit** (`0 */10 * * * *`) | **WMS resi bridge**: pull resi-feed TikTok+Shopee (watermark per-channel di `sync_cursors`) → push batch ke manufacture `POST /resi/sync-batch` | Redis `lock:sync-resi-wms` (8m) | `.../worker/tasks/sync_resi_wms.go:55` |
| integration | **tiap 15 menit** (`0 */15 * * * *`) | **`auto-arrange`** (pengganti auto-ship Desty, Gap 2): per channel cek gerbang window sadar-holiday (dievaluasi "sekarang": libur/≥15:00 TikTok/besok-libur Shopee → tunda), cari order **siap-diatur-kirim** (`raw_status ∈ {AWAITING_SHIPMENT, READY_TO_SHIP, RETRY_SHIP}`, termasuk COD; umur ≤7 hari; belum `arranged`/`needs_review`) → `ShipBatch` (TO_PROCESS→TO_SHIP) → tandai `arranged` / retry 3× → `needs_review`+Telegram. **⚠️ DORMANT**: hanya didaftarkan bila env **`AUTO_ARRANGE_ENABLED=true`** (default off) — aman di-deploy siapa pun; nyalakan hanya saat **cutover Desty→WMS**. MongoDB lock (LockKey) `lock:auto-arrange` (10m) | `.../worker/tasks/auto_arrange.go` |

> Inisialisasi index (bukan job): `services/insentive/cron_worker.go:1550` — `ensureCronIndexes()` (TTL index `cron_locks.expires_at`) dipanggil sekali saat startup.

## Event-driven (webhook dispatcher)

- **integration** — `internal/webhook/dispatcher.go`: antrian in-memory, **5 worker goroutine** default. Entry: `POST /webhooks/services/shopee` · `/tiktok` · `/accurate` (publik, tanpa validasi gateway). Callback TikTok Shop/Shopee → di-log → di-antri per-platform → di-konsumsi job `webhook_consumer_task` (tiap 5 detik). Rate limit 20 req/dtk per platform; retry on failure; status disimpan ke Mongo. Entry `/webhooks/services/desty` **dicabut 2026-07-12** ([[External - Desty]] soft-disabled). Lihat [[Microservices - Integration Service]].

## In-process poller (goroutine, bukan cron)

- **warehouse** — dua goroutine poll di `main.go` (bukan cron manager), Redis lock via redsync:
  - **Reconciler 60s** (`reconciler.go`, `lock:warehouse-reconciler` TTL 50s) — tarik order dari integration `GET /transactions/orders/list` **by-watermark** (`order_update_date`, cursor per-status di `sync_cursors`), 4 stream `TO_SHIP`/`SHIPPED`/`COMPLETED`/`RETURNED`, batch 500. Antrian kerja WMS + auto-close order yang diproses di luar WMS.
  - **Open-order sweep 5m** (`open_order_sweep.go`, `lock:warehouse-open-sweep` TTL 4m) — jaring pengaman **self-healing**: kumpulkan order **terbuka** (`status_wms NOT IN [HANDED_OVER, CANCELLED]`, tertua-dulu, cap 5000/tick) → tanya status terkini `?order_ids=…` → `doUpsert`. **Tanpa cursor** → menutup celah reconciler yang melewatkan update telat (order nyangkut). Idempoten; run pertama membersihkan backlog. Lihat [[Microservices - Warehouse Service]].

## Service tanpa job background

`file` · `inventory` · `tiktok-shop-service` · `api-gateway` · orchestrator `hris` · orchestrator `it`.

## Catatan & risiko operasional

- **Penumpukan jam 00:00–02:00**: banyak sync integration (master data, order, report, kredensial) menumpuk di tengah malam WIB — perhatikan saat menilai beban/quota API TikTok/Shopee. Tambahan: `sync-tt-shop-orders` kini 4× sehari (bukan 1× di 01:00) — jam 00:00/08:00/16:00/23:00 WIB.
- **Notifikasi worker**: semua worker integration kirim Telegram otomatis via hook di manager level — tidak perlu konfigurasi per-task. `WithOnJobError` → `SendError` saat gagal (setelah semua retry habis); `WithOnJobEnd` → `Send` saat sukses. Dikecualikan dari notif sukses: `webhook-consumer` & `sync-resi-wms` (frekuensi tinggi, akan spam). PR #322.
- **Job tersibuk**: `webhook_consumer` jalan **tiap 5 detik** — paling sering; pastikan lock Redis sehat agar tak dobel.
- **Locking**: integration = Redis (prefix `srv:integration:lock:*`); insentive = Mongo `cron_locks` (TTL 2j). Service lain (employee/attendance/notification/task-management) **tanpa distributed lock** — aman selama **single instance**; bila di-scale horizontal, job bisa dobel.
- Backup DB mingguan ada di luar tabel ini (lihat [[IT - Backup & DR]] / [[IT - Runbooks]]).

## Dokumen Terkait

- [[IT - Monitoring System]] · [[IT - Runbooks]] · [[IT - Environment Inventory]] · [[IT - Backup & DR]]
- [[DB - Overview and Notes]] (`cron_locks`, `webhook_tasks`) · [[Microservices - Integration Service]] · [[Microservices - Insentive Service]] · [[Microservices - Employee Service]] · [[Microservices - Attendance Service]] · [[Microservices - Notification Service]] · [[Microservices - Task Management Service]]
- [[External - Desty]] · [[Sales - Marketplace Integration]]
