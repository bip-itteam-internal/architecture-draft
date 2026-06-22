# Microservices - Insentive Service

## Deskripsi

_Insentive Service adalah engine perhitungan insentif untuk tim sales/marketing. Service ini menghitung insentif bagi 9 role marketing (Supervisor, ADV Leader TikTok, ADV Marketplace, ADV Meta, Host Live, Affiliate, CRM, CS, ICC) menggunakan scoring KPI bertingkat, dilengkapi workflow approval, audit log, dan cron harian yang menarik performa iklan dari integration-service._

- **Stack:** Go + Fiber v2 + MongoDB
- **Path:** `services/insentive`
- **Status:** ✅ Implemented penuh (production-grade, dilengkapi unit test)

## Endpoint / Fitur (Sudah Diimplementasikan)

### Core & Engine
- `GET /health` — health check.
- `POST /calculate` — engine perhitungan universal, dengan validasi per-role (individual vs shared vs SPV vs ICC).
- `POST /calculate/auto` — trigger manual cron, dijalankan di goroutine background.
- `GET /stats` — dashboard total + tren bulanan.

### Master KPI (CRUD)
- `GET /master-kpi`, `POST /master-kpi`, `PUT /master-kpi/:id`, `DELETE /master-kpi/:id` — pengelolaan master KPI; bobot harus berjumlah total 100.

### Accurate Proxies
- `GET /accurate/summary`
- `GET /accurate/income`
- `GET /accurate/invoices`

### Mappings Performa Employee & Audit
- `GET /mappings`, `POST /mappings` — daftar dan pembuatan mapping performa employee.
- `PATCH /mappings/:id` — update (reason wajib ≥10 karakter).
- `DELETE /mappings/:id` — hapus mapping.
- Semua operasi tulis pada mappings menulis audit log.
- `GET /audit-logs` — pembacaan audit log.

### Incentive Results & Workflow
- `GET /results`, `GET /results/summary` (paginated) — daftar hasil insentif.
- `GET /results/export` — export Excel (single + multi-sheet pivot via excelize).
- `GET /results/me`, `GET /results/team` — hasil untuk user sendiri / tim.
- `GET /results/:id` — detail hasil.
- `POST /results/bulk-approve`, `POST /results/bulk-unapprove` — approve/unapprove massal.
- `PATCH /results/:id/override`, `PATCH /daily-override` — override hasil.
- `POST /results/:id/approve`, `POST /results/:id/unapprove` — approve/unapprove per-hasil.
- `DELETE /results/:id` — hapus hasil (ditolak jika sudah `APPROVED`).

### Business Rules
- Tabel multiplier tier per-role.
- Tier profit-achievement untuk SPV.
- Ambang diskualifikasi: `MinKPIScore` 70; SPV team-avg 70 + retur ≤5%; CS closing ≥50%.
- Strategi scoring CPA/ROI.
- Aturan ICC pay-per-video: tier Rp10k / Rp150k, video eligible 7–30 hari.

### Cron (Worker Harian)
- Berjalan harian pukul 00:00 WIB, dengan cutoff khusus pada akhir bulan.
- Distributed lock via MongoDB TTL (`cron_locks`).
- Mengelompokkan mapping aktif per store/employee.
- Menarik metrik TikTok GMV-Max + Shopee GMS harian dari integration-service.
- Menghitung dan melakukan upsert hasil sebagai `DRAFT` (tidak menimpa hasil yang sudah `APPROVED`).
- Rekonsiliasi carry-over pada akhir bulan.

## Belum Diimplementasikan / Catatan

- Tidak ada stub — service ini production-grade.
- Minor: beberapa `fmt.Println` debug masih tersisa di kode.
- Minor: route `GET /results/:id` terdaftar dua kali; registrasi kedua bersifat dead/shadowed.

## Dependencies & Integrasi

- **MongoDB** — koleksi `employee_performance_mappings`, `audit_logs`, `cron_locks`, `master_kpis`, `incentive_results`. Lihat [[DB - Overview and Notes]].
- **[[Microservices - Integration Service]]** — sumber laporan iklan TikTok & Shopee (GMV-Max / GMS harian).
- **[[External - Accurate]]** — Accurate API untuk summary, income, dan invoices.
- **[[Microservices - Employee Service]]** — data employee untuk mapping performa.
- **[[CORE - API Master Gateway]]** — gateway untuk routing request ke service.
- `excelize` — library untuk export hasil ke Excel.

## Dokumen Terkait

- [[Finance - Incentive]]
- [[Sales - Incentive]]
- [[HRIS - Key Performance Index]]
