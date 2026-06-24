## Deskripsi

*Kamus data **field-level** per service — turunan dari [[DB - Overview and Notes]]. Field di bawah **grounded** dari struct Go (`bson:` tag) di repo `bip-erp`. Tipe ditulis bila non-string; `?` = `omitempty`. Sebagian koleksi tak punya struct bertipe (disimpan `bson.M` dinamis) → ditandai.*

- **Status**: ⚠️ Field-level grounded untuk service yang struct-nya ada; beberapa koleksi dinamis/not-located (lihat catatan)
- **Pola**: database-per-service ([[ADR - 0002 Database-per-Service]]). Sumber kebenaran tetap struct di kode — verifikasi `services/<svc>/*.go` saat berubah.
- **Umum**: banyak dok memakai `metadata` (`common.Metadata`: created_at/created_by/updated_at/updated_by) & `_id` (ObjectID/string).

## employee — `employee-mongo` (replica set)
Doc: [[Microservices - Employee Service]]

- **personal_data**: employee_id, photo (MinIOFile), full_name, gender, date_of_birth (time), religion, marital_status, blood_type, home_address, postal_code (int), email_address, phone_number, nik_number (int), kk_number (int), metadata
- **work_data**: employee_id, department, position, join_date (time), employment_type, contract_ending (time), npwp_number, bpjs_ks_number, bpjs_kt_number, bank_detail?/bank_details? ([]BankDetail), fingerprint_id (int), is_supervisor (bool), vacation?, metadata
- **work_schedule**: employee_id, full_name, fingerprint_id (int), schedule_type, schedule_id?, group_id?
- **company_work_schedule**: schedule_id, schedule (WeeklySchedule)
- **system_authentication**: employee_id, username, system_roles (common.Roles), password, pin?, is_active (bool), has_registered (bool), device ([]Device), web_browser ([]WebBrowser)
- **kpi_score**: employee_id, period, template (KPITemplate), score (float64), metadata
- **company_holiday**: struct di attendance (lihat bawah)
- **personal_document**, **work_document**: struct tak ditemukan (kemungkinan dinamis/inline) — TBD

## attendance — `attendance-mongo-db`
Doc: [[Microservices - Attendance Service]]

- **attendance_entries**: _id, employee_id, full_name, fingerprint_id (int), schedule_id, schedule_fmt?, group_id?, date (time), realtime (time), work_time (WorkTime), clock_in (*string), clock_out (*string), clock_in_method, clock_out_method, clock_in_location (*GPS), clock_out_location (*GPS), status, emoji, late_hour (int), leave_hour (int), overtime_hour (int), comment, document ([]Document), metadata
- **leave_request**: _id, employee_id, full_name, position, department, from_date (time), to_date (time), leave_type, leave_subtype?, reason, document (MinIOFile), status, spv_status (ReviewData), hr_status (ReviewData), security_verify?, metadata
- **shift_exchange_request**: _id, employee_id, full_name, position, department, work_date (time), exchange_date (time), exchange_work_time? (*WorkTime), reason, status, review_1 (ReviewData), review_2 (ReviewData), metadata
- **attendance_correction_request**: _id, employee_id, full_name, position, department, attendance_id (ObjectID), attendance_date (time), work_time (WorkTime), correction_type, reason, status, review_1, review_2, metadata
- **company_group_rotation**: group_id, schedule_rotation ([]*string), schedule_rotated_in_x_days (int), starting_date (time), starting_schedule (*string)
- **company_wifi**: _id, ssid, mac_address, metadata
- **guestbook**: _id, employee_id?, full_name, phone_number, plate_number?, visit_from?, visit_purpose?, meeting_with?, category?, number_of_people? (int), visiting_office?, standby_security?, notes?, metadata
- **fingerprint_export**: struct tak ditemukan — TBD

## notification — `notification-mongo-db`
Doc: [[Microservices - Notification Service]] (struct di `shared-library/models/notification`)

- **inbox**: _id, employee_id, title, body, category, is_read (bool), action (ExtraResource: external_url/app_route), metadata
- **splash**: _id, start_promotion (time), end_promotion (time), image (MinIOFile), action (ExtraResource), metadata
- **article**: _id, title, body, image (MinIOFile), action (ExtraResource), metadata

## insentive — `insentive-mongo-db`
Doc: [[Microservices - Insentive Service]]

- **employee_performance_mappings** (bson.M dinamis): _id, role, platform, mapping_data (map), is_active (bool), employee_id, fullname, team ([]{employee_id, fullname}), created_at, updated_at
- **audit_logs** (bson.M): _id, target_collection, target_id, action, executor_id, executor_name, before, after, reason, created_at
- **cron_locks** (bson.M): _id (key), expires_at (time, TTL), started_at (time)
- **master_kpis** (`MasterKPI`): _id, role, kpis ([]{kpi, bobot, target, target_atas}), created_at, updated_at
- **incentive_results**: _id, role, period_month (int), period_year (int), calculated_at (time), member_count (int), incentive_team (float64), incentive_personal (float64), member_results ([]), kpi_details ([]), total_final_score (float64), incentive_multiplier (float64), status, metadata

## integration — `integration-mongo-db`
Doc: [[Microservices - Integration Service]]

- **transaction_orders** (`TransactionOrder`): _id, order_id, shop_id, shop_name, order_date (time), order_update_date (time), buyer (obj), items ([]TransactionItem), total_payment (float64), payment, status, channel, cancelled_at?, returned_at?, completed_at?, shipped_at?, sales_invoice_report_id?, sales_return_report_id?, income_report_id?, income?, created_at, updated_at
- **items** (`ItemProduct`): _id, parent_id?, name?, item_type?, sku?, base_price? (float64), has_children? (bool), variations? ([]ItemProduct), items? ([]BundleItemDetail), bundle_contents? ([]BundleItem), created_at, updated_at, deleted_at?
- **credentials**: `Credential`{_id, platform, store_id, key, value} · `ShopeeCredential`{_id, name, access_token, refresh_token, expire_in (int64), shop_id_list ([]int64), user_id_list, supplier_id_list, merchant_id_list, account_type, metric_types ([]string), expired_at, created_at, updated_at, deleted_at?}
- **holidays** (`Holiday`): _id, date (YYYY-MM-DD), description
- **marketing_teams** (`MarketingTeam`): _id, name, description, created_at, updated_at, deleted_at?
- **accurate_products** (`AccurateProduct`): _id, item_id, item_name?, item_sku?, item_base_price? (float64), item_type?, product_code, created_at, updated_at
- **accurate_bank_accounts** (`AccurateBankAccount`): _id, bank_name, bank_code, branch_name, branch_code, account_name, account_number, account_currency, accurate_id, created_at, updated_at
- **accurate_kv_configs** (`AccurateKVConfig`): _id, key, value, description, type, created_at, updated_at
- **shopee_escrow_details** (`ShopeeEscrowDetail`): _id, order_sn, store_id, buyer_user_name, return_order_sn_list ([]string), order_income (obj), buyer_payment_info (obj), created_at, updated_at

## inventory — `inventory-mongo-db`
Doc: [[Microservices - Inventory Service]]

- **inventory** (`InventoryItem`): _id?, master_id (ObjectID), specs? ([]SpecField), item_status, purchase_price? (*int64), purchase_date (*time), arrived_date?, purchase_document (DocumentSimplify), arrived_document (DocumentSimplify), held_by (obj), notes?, metadata
- **data_master** (`DataMaster`): _id?, item_name, item_category, spec_template? ([]string), tags? ([]string), metadata
- **repair_history** (`RepairHistory`): _id?, inventory_item_id, reported_date?, repair_date?, next_maintenance_date?, repair_type, problem_description, components? ([]RepairComponent), service_type, service_by, repair_status, notes?, documents? ([]MinIOFile), reported_by, metadata

## tiktok-shop — `tiktok-shop-mongo-db`
Doc: [[Microservices - TikTok Shop Service]] — **disimpan `bson.M` dinamis** (tanpa struct bertipe)

- **tiktok_shop_callbacks**: code, state, created_at (observasi)
- **tiktok_shop_webhooks**: payload (bson.M mentah), received_at

## task-management — `task-management-mongo-db`
Doc: [[Microservices - Task Management Service]]

- **task** (`Task`): _id, created_by (*string), requestor_name, requestor_division, phone, keluhan, description, space_id (*ObjectID), priority_id (*ObjectID), assign_to ([]string), start_date?, due_date?, status, is_archived (bool), todo_approval?, done_approval?, spv_req?, attachments ([]FileAttachment), comments ([]TaskComment), checklist ([]ChecklistItem), completed_at?, response_due_at?, responded_at?, sla_resp_warned/breached (bool), sla_reso_warned/breached (bool), createdAt, updatedAt
- **space** (`Space`): _id, name, division, owner_id (*ObjectID), description, status ([]Stage: id/title/order/color), priority ([]Priority: id/name/description/color/resolution_hours), createdAt, updatedAt
- **notifications** (`Notification`): _id, user_id, actor_id (*string), task_id (*ObjectID), space_id (*ObjectID), type, title, message, meta (map), is_read (bool), createdAt
- **audits** (`Audit`): _id, task_id (ObjectID), actor_id, action, detail, created_at

## file — MinIO only
Doc: [[Microservices - File Service]] — **tanpa koleksi Mongo**; proxy ke MinIO (prefix `employee/`, `attendance/`, `task/`, `notification/`), akses via API key/JWT.

## Infrastruktur data bersama

- **Redis** — cache gateway + queue antar service (prefix per domain, mis. `srv:integration`).
- **MinIO** — object storage; prefix path per domain.

## Dokumen Terkait

- [[DB - Overview and Notes]] · [[ADR - 0002 Database-per-Service]] · [[CORE - API Master Gateway]]
- [[Microservices - Employee Service]] · [[Microservices - Attendance Service]] · [[Microservices - Integration Service]] · [[Microservices - Inventory Service]] · [[Microservices - Insentive Service]] · [[Microservices - Notification Service]] · [[Microservices - Task Management Service]] · [[Microservices - TikTok Shop Service]] · [[Microservices - File Service]]
