## Deskripsi

*Kamus data per service — turunan **field-level** dari [[DB - Overview and Notes]]. Daftar koleksi di sini **grounded** (sesuai DB Overview); **skema field per koleksi = (TBD)**, sumber kebenarannya struct `models_*.go`/handler di tiap service. Doc ini = kerangka + penunjuk; diisi bertahap saat mendokumentasikan tiap service.*

- **Status**: 🟡 Kerangka — koleksi grounded; field-level TBD per service
- **Pola**: database-per-service ([[ADR - 0002 Database-per-Service]]). Tiap service punya Mongo sendiri; tak ada query lintas-DB.

## Cara mengisi field-level

Untuk tiap service, baca struct model di repo (`bip-erp/services/<svc>/models_*.go`) → daftar field + tipe + index. **Jangan mengarang** field (§1).

## Koleksi per service (grounded dari DB Overview)

### employee — `employee-mongo` (replica set)
Doc: [[Microservices - Employee Service]] · field-level: TBD
`personal_data` · `personal_document` · `work_data` · `work_document` · `work_schedule` · `company_work_schedule` · `system_authentication` · `kpi_score` · `company_holiday`

### attendance — `attendance-mongo-db`
Doc: [[Microservices - Attendance Service]] · field-level: TBD
`attendance_entries` · `work_schedule` · `company_work_schedule` · `company_group_rotation` · `company_wifi` · `company_holiday` · `fingerprint_export` · `guestbook` · `leave_request` · `shift_exchange_request` · `attendance_correction_request`

### notification — `notification-mongo-db`
Doc: [[Microservices - Notification Service]] · field-level: TBD
`inbox` · `splash` · `article`

### insentive — `insentive-mongo-db`
Doc: [[Microservices - Insentive Service]] · field-level: TBD
`employee_performance_mappings` · `audit_logs` · `cron_locks` · `master_kpis` · `incentive_results`

### integration — `integration-mongo-db`
Doc: [[Microservices - Integration Service]] · field-level: TBD
`transaction_orders` · webhook logs · summary reports · `items` · `credentials` · `holidays` · `marketing_teams` · `accurate_products` · `accurate_bank_accounts` · `accurate_kv_configs` · `shopee_escrow_details`

### inventory — `inventory-mongo-db`
Doc: [[Microservices - Inventory Service]] · field-level: TBD
`inventory` · `data_master` · `repair_history`

### tiktok-shop — `tiktok-shop-mongo-db`
Doc: [[Microservices - TikTok Shop Service]] · field-level: TBD
`tiktok_shop_callbacks` · `tiktok_shop_webhooks`

### task-management — `task-management-mongo-db`
Doc: [[Microservices - Task Management Service]] · field-level: **sebagian terbaca** di `services/task-management/models_task.go`, `models_space.go`, `models_notification.go` (TBD diuraikan)
`task` · `space` · `notifications` · `audits`
> Catatan: membaca `employee_db` read-only untuk nama/divisi.

## Infrastruktur data bersama

- **Redis** — cache gateway + queue antar service (prefix per domain, mis. `srv:integration`).
- **MinIO** — object storage, prefix path per domain: `employee/` · `attendance/` · `task/` · `notification/`.

## Dokumen Terkait

- [[DB - Overview and Notes]] · [[ADR - 0002 Database-per-Service]] · [[CORE - API Master Gateway]]
