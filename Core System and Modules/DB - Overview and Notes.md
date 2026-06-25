## Deskripsi

bip-erp menerapkan pola **database-per-service**: setiap microservice memiliki MongoDB-nya sendiri (container Mongo terpisah) dan menjadi pemilik (ownership) penuh atas datanya. Tidak ada akses langsung lintas-database antar service; komunikasi dilakukan via HTTP internal melalui gateway (lihat [[CORE - API Master Gateway]]). Khusus employee-service berjalan sebagai **replica set** (primary + secondary) agar datanya dapat diekspos read-only untuk konsumen lain. Seluruh server menyimpan waktu dalam **UTC**. Selain MongoDB per service, terdapat dua infrastruktur data bersama: **Redis** (cache & queue) dan **MinIO** (object storage).

## Database per Service

Tiap baris berikut menyebutkan nama service, container Mongo, collection utama, dan dokumen service terkait.

### employee — `employee-mongo-primary` / `employee-mongo-secondary` (replica set)
Doc: [[Microservices - Employee Service]]
- personal_data
- personal_document
- work_data
- work_document
- work_schedule
- company_work_schedule
- system_authentication
- kpi_score (beserta KPI templates)
- company_holiday
- master_department (departments + positions + roles per dept; seed otomatis)
- master_system_role (feature-based role systems: insentive, integration; seed otomatis)

### attendance — `attendance-mongo-db`
Doc: [[Microservices - Attendance Service]]
- attendance_entries
- work_schedule
- company_work_schedule
- company_group_rotation
- company_wifi
- company_holiday
- fingerprint_export
- guestbook
- leave_request
- shift_exchange_request
- attendance_correction_request

### notification — `notification-mongo-db`
Doc: [[Microservices - Notification Service]]
- inbox
- splash
- article

### insentive — `insentive-mongo-db`
Doc: [[Microservices - Insentive Service]]
- employee_performance_mappings
- audit_logs
- cron_locks
- master_kpis
- incentive_results

### integration — `integration-mongo-db`
Doc: [[Microservices - Integration Service]]
- transaction_orders (model terpadu)
- webhook logs
- summary reports
- items / master catalog
- credentials
- holidays
- marketing_teams (grouping tim + shop ACL)
- accurate_products
- accurate_bank_accounts
- accurate_kv_configs
- shopee_escrow_details

### inventory — `inventory-mongo-db`
Doc: [[Microservices - Inventory Service]]
- inventory
- data_master
- repair_history

### tiktok-shop — `tiktok-shop-mongo-db`
Doc: [[Microservices - TikTok Shop Service]]
- tiktok_shop_callbacks
- tiktok_shop_webhooks (payload mentah)

### task-management — `task-management-mongo-db`
Doc: [[Microservices - Task Management Service]]
- task
- space
- notifications
- audits

> Catatan: task-management juga membaca `employee_db` (ERP) secara **read-only** untuk memperoleh nama/divisi.

### recruitment — `recruitment-mongo-db`
Doc: [[Microservices - Recruitment Service]] (⚠️ Fase 1-3)
- job_requisition
- job_posting
- candidate
- screening_result
- interview
- technical_test_result
- psychotest
- background_check
- offer
- audit_logs

## Infrastruktur Data Bersama (Redis, MinIO)

- **Redis** — cache response gateway sekaligus queue antar service. Key di-namespace per domain, mis. prefix `srv:integration`.
- **MinIO** — object storage bersama. Objek dipisah per domain melalui prefix path: `employee/`, `attendance/`, `task/`, `notification/`.

## Catatan

- Setiap service mengelola datanya sendiri (ownership). Database satu service tidak diakses langsung oleh service lain.
- Komunikasi antar service dilakukan via HTTP internal melalui gateway, lihat [[CORE - API Master Gateway]] — bukan query/lookup lintas-database.
- Hanya employee-service yang berjalan sebagai replica set (primary + secondary); secondary dipakai untuk akses read-only, termasuk oleh task-management terhadap `employee_db`.
- Cluster primary tidak boleh diubah sembarangan karena belum ada dynamic cluster picker.
- Seluruh waktu disimpan dalam UTC.

## Dokumen Terkait

- [[CORE - API Master Gateway]]
- [[Microservices - Employee Service]]
- [[Microservices - Attendance Service]]
- [[Microservices - Notification Service]]
- [[Microservices - File Service]]
- [[Microservices - Insentive Service]]
- [[Microservices - Integration Service]]
- [[Microservices - Inventory Service]]
- [[Microservices - Task Management Service]]
- [[Microservices - TikTok Shop Service]]
