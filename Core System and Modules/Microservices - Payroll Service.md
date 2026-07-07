## Deskripsi

*Payroll Service mengelola **penggajian**: setup komponen gaji, konfigurasi BPJS & pajak (PPh21 TER), dan penetapan gaji per karyawan. Ini sisi **implementasi** dari konsep [[HRIS - Payroll]] & [[HRIS - Compensation & Benefits]]. **Fase 1 (Salary Setup & Config)** sudah di kode; kalkulasi payroll run + slip gaji = fase berikut.*

- **Stack**: Go + Fiber v2 + MongoDB (`payroll_db`) — selaras pola service bip-erp lain
- **Path**: `services/payroll` (branch `feat/payroll-service`)
- **Status**: ⚠️ **Implemented (Fase 1 — Setup & Config)**. Di belakang [[CORE - API Master Gateway]] (`InternalURL["payroll"]`), auth **SSO** ([[CORE - SSO Flow]]), role `system_roles["hris"]`. Port `6980`, mongo `payroll-mongo-db` (host `32792`).

## Endpoint / Fitur (Sudah Diimplementasikan — Fase 1)

### Config global (single-company)
- `GET/PUT /config/company` — identitas perusahaan (nama, kota, penanda tangan HRD) untuk kop slip
- `GET/PUT /config/bpjs` — rate & cap 5 program: Kesehatan, JHT, JP, JKK, JKM
- `GET/PUT /config/tax` — PPh21 metode **TER** + nominal PTKP per status + tabel TER
- GET = role HR; PUT = HR admin. Dokumen **singleton**, di-seed default saat boot (idempoten).

### Master Komponen Gaji
- CRUD `/salary-components` — komponen `type` (earning/deduction), `input_type` (manual/computed), `taxable`, `bpjs_base`, `sort_order`, `is_active`
- **Di-seed 15 komponen** default **persis slip nyata** (9 pendapatan + 6 pengurangan). Yang `computed` (Tunjangan Kehadiran, Lembur, BPJS, PPh21) dihitung engine Fase 2. GET = HR; tulis = HR admin.

### Gaji per Karyawan
- `GET /employee-salary` (list) · `GET/PUT /employee-salary/:employeeId` (upsert; path = sumber kebenaran)
- Field: `basic_salary`, **`upah_bpjs`** (dasar BPJS terpisah dari gaji pokok — temuan dari slip), `ptkp_status` (TK/0…K/3), `component_values[]`, `bpjs_enrollment`, `effective_date`
- Referensi `employee_id` ke [[Microservices - Employee Service]] — NPWP/no.BPJS/rekening **di-join di FE**, tidak disalin.

## Model Data (`payroll_db`)

- `salary_component` · `employee_salary` · `payroll_config` (singleton)

## Belum Diimplementasikan / Catatan

- **Engine payroll run** (kalkulasi gross → BPJS → PPh21 TER → net), **prorata Tunjangan Kehadiran** via attendance `payroll-supplement` (`payout_pct`), dan **Lembur** = **Fase 2**.
- **Slip gaji** (PDF) = Fase 3. **THR & rekonsiliasi PPh21 tahunan** = Fase 4. **Dashboard + export Accurate** = Fase 5 ([[ADR - 0001 Akuntansi via Accurate]]).
- **FE** "Pengaturan Gaji" (pola Recruitment System Setup) = menyusul.
- **Multi-company ditunda** (Fase 1 single-company) — kenyataan grup punya >1 entitas (mis. CV Pure Glow Lux, PT Bharata Internasional).
- Validasi referensial (`component_id` / eksistensi `employee_id`) dilakukan di FE; assign gaji memakai role `isHR`.

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — master karyawan (NPWP/BPJS/bank) via `employee_id`; juga penyedia `payroll-approx`
- [[Microservices - Attendance Service]] — `payroll-supplement` (agregasi kehadiran periode 26→25) = input kalkulasi Fase 2
- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]] — routing + auth
- [[DB - Overview and Notes]] — pola database-per-service ([[ADR - 0002 Database-per-Service]])

## Dokumen Terkait

- [[HRIS - Payroll]] · [[HRIS - Compensation & Benefits]] — konsep/bisnis (pasangan dok ini)
- [[Microservices - Employee Service]] · [[Microservices - Attendance Service]]
