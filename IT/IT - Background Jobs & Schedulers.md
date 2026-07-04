## Deskripsi

*Inventaris **proses yang berjalan diam-diam** di bip-erp — cron/scheduler/worker latar belakang: apa yang jalan, kapan, di service mana, untuk apa, dan lock-nya. Grounded dari kode (`bson`/cron string disalin verbatim). Tujuannya: tak ada "sistem tersembunyi" yang tak diketahui saat debugging, perencanaan kapasitas, atau mengubah service.*

- **Status**: ✅ Implemented — 20 job terjadwal + 1 dispatcher webhook (per audit kode). *3 job reminder attendance (koreksi/leave/tukar jadwal) + auto-ignore koreksi & tukar jadwal + pre-alokasi sadar-swap dari **PR #165** — belum rilis ke prod.*
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
| integration | harian 01:00 (`0 1 * * *`) | refresh token Desty + retry order PENDING | Redis | `services/integration/internal/cmd/cron.go:34` |
| integration | harian 01:00 (`0 0 1 * * *`) | sync order TikTok Shop (semua shop authorized) | Redis `lock:sync-tt-shop-orders` (15m) | `.../worker/tasks/tt_shop_sync_orders.go:35` |
| integration | harian 00:00 (`0 0 0 * * *`) | sync master data TikTok Business | Redis `lock:sync-tt-business-master-data` (15m) | `.../worker/tasks/tt_business_master_data.go:45` |
| integration | harian 01:00 (`0 0 1 * * *`) | sync report GMV-Max | Redis `lock:sync-tt-business-gmv-max-report` (15m, conc. 5) | `.../worker/tasks/tt_business_gmv_max_report.go:33` |
| integration | harian 02:00 (`0 0 2 * * *`) | sync integration report | Redis `lock:sync-tt-business-integration-report` (15m) | `.../worker/tasks/tt_business_integration_report.go:35` |
| integration | harian 00:00 (`0 0 0 * * *`) | sync master data TikTok Shop (produk/kategori) | Redis `lock:sync-tt-shop-master-data` (15m) | `.../worker/tasks/tt_shop_master_data.go:34` |
| integration | **tiap 5 detik** (`*/5 * * * * *`) | konsumsi antrian webhook `webhook_tasks` & dispatch | Redis `lock:webhook-consumer` (5m) | `.../worker/tasks/webhook_consumer_task.go:36` |
| integration | harian 00:00 (`0 0 0 * * *`) | refresh kredensial Desty (cek expiry buffer 5 hari) | Redis `lock:desty-credential-task` (5m) | `.../worker/tasks/desty_credential_task.go:40` |
| integration | harian 02:00 (`0 0 2 * * *`) | sync performa Shopee GMS (item & campaign) | Redis `lock:sync-shopee-performance` (30m) | `.../worker/tasks/shopee_sync_task.go:30` |
| integration | harian 03:00 (`0 0 3 * * *`) | snapshot performa affiliate Shopee AMS per toko → `shopee_affiliate_performance` (window **mundur 3 hari** untuk self-heal order yang baru ter-confirm; upsert idempotent; toko tanpa cred AMS di-skip) | Redis `lock:sync-shopee-affiliate-performance` (30m) | `.../worker/tasks/shopee_affiliate_sync_task.go:26` |
| integration | harian 05:00 (`0 0 5 * * *`) ✅ live | Affiliate v2: ledger order-level (`get_conversion_report`, iris per-hari) → `shopee_affiliate_conversion` + tagihan komisi bulanan (`get_validation_list`/`report` window placement **[M−2..M−1]**) → `shopee_affiliate_validation_bill` + stamp/rekonsiliasi; window konversi di-gate ke `get_performance_data_update_time` (fallback trailing-3-hari); plafon `page*size≤10000`; per-shop isolation, skip tanpa cred AMS | Redis `lock:sync-shopee-affiliate-conversion` (30m) | `.../worker/tasks/shopee_affiliate_conversion_sync_task.go:26` |

> Inisialisasi index (bukan job): `services/insentive/cron_worker.go:1550` — `ensureCronIndexes()` (TTL index `cron_locks.expires_at`) dipanggil sekali saat startup.

## Event-driven (webhook dispatcher)

- **integration** — `internal/webhook/dispatcher.go`: antrian in-memory, **5 worker goroutine** default. Entry: `POST /webhooks/services/desty` (publik, tanpa validasi gateway). Callback Desty/TikTok Shop/Shopee → di-log → di-antri per-platform → di-konsumsi job `webhook_consumer_task` (tiap 5 detik). Rate limit 20 req/dtk per platform; retry on failure; status disimpan ke Mongo. Lihat [[Microservices - Integration Service]].

## Service tanpa job background

`file` · `inventory` · `tiktok-shop-service` · `api-gateway` · orchestrator `hris` · orchestrator `it`.

## Catatan & risiko operasional

- **Penumpukan jam 00:00–02:00**: banyak sync integration (master data, order, report, kredensial) menumpuk di tengah malam WIB — perhatikan saat menilai beban/quota API TikTok/Shopee.
- **Job tersibuk**: `webhook_consumer` jalan **tiap 5 detik** — paling sering; pastikan lock Redis sehat agar tak dobel.
- **Locking**: integration = Redis (prefix `srv:integration:lock:*`); insentive = Mongo `cron_locks` (TTL 2j). Service lain (employee/attendance/notification/task-management) **tanpa distributed lock** — aman selama **single instance**; bila di-scale horizontal, job bisa dobel.
- Backup DB mingguan ada di luar tabel ini (lihat [[IT - Backup & DR]] / [[IT - Runbooks]]).

## Dokumen Terkait

- [[IT - Monitoring System]] · [[IT - Runbooks]] · [[IT - Environment Inventory]] · [[IT - Backup & DR]]
- [[DB - Overview and Notes]] (`cron_locks`, `webhook_tasks`) · [[Microservices - Integration Service]] · [[Microservices - Insentive Service]] · [[Microservices - Employee Service]] · [[Microservices - Attendance Service]] · [[Microservices - Notification Service]] · [[Microservices - Task Management Service]]
- [[External - Desty]] · [[Sales - Marketplace Integration]]
