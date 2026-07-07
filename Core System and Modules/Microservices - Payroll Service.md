## Deskripsi

*Payroll Service mengelola **penggajian**: setup komponen gaji, konfigurasi BPJS & pajak, penetapan gaji per karyawan, dan **kalkulasi gaji (payroll run)**. Ini sisi **implementasi** dari konsep [[HRIS - Payroll]] & [[HRIS - Compensation & Benefits]]. **Fase 1 (Setup & Config)** + **Fase 2 (Engine Payroll Run)** sudah di kode; slip PDF + PPh21 TER = fase berikut.*

- **Stack**: Go + Fiber v2 + MongoDB (`payroll_db`) — selaras pola service bip-erp lain
- **Path**: `services/payroll` (Fase 1 merged #262; Fase 2 PR #265, branch `feat/payroll-service`)
- **Status**: ⚠️ **Implemented (Fase 1 Setup + Fase 2 Engine Run)**. Di belakang [[CORE - API Master Gateway]] (`InternalURL["payroll"]`), auth **SSO** ([[CORE - SSO Flow]]), role `system_roles["hris"]`. Port `6980`, mongo `payroll-mongo-db` (host `32792`).

## Endpoint / Fitur (Sudah Diimplementasikan — Fase 1)

### Config global (single-company)
- `GET/PUT /config/company` — identitas perusahaan (nama, kota, penanda tangan HRD) untuk kop slip
- `GET/PUT /config/bpjs` — rate & cap 5 program: Kesehatan, JHT, JP, JKK, JKM
- `GET/PUT /config/tax` — PPh21 metode **TER** + nominal PTKP per status + tabel TER
- GET = role HR; PUT = HR admin. Dokumen **singleton**, di-seed default saat boot (idempoten).

### Master Komponen Gaji
- CRUD `/salary-components` — komponen `type` (earning/deduction), `input_type` (manual/computed), `taxable`, `bpjs_base`, `sort_order`, `is_active`
- **Di-seed 15 komponen** default **persis slip nyata** (9 pendapatan + 6 pengurangan). Yang `computed` (Lembur, BPJS, PPh21, **potongan** Tunjangan Kehadiran) dihitung engine; **earning Tunjangan Kehadiran = manual** (base per karyawan). GET = HR; tulis = HR admin.

### Gaji per Karyawan
- `GET /employee-salary` (list) · `GET/PUT /employee-salary/:employeeId` (upsert; path = sumber kebenaran)
- Field: `basic_salary`, **`upah_bpjs`** (dasar BPJS terpisah dari gaji pokok — temuan dari slip), `ptkp_status` (TK/0…K/3), `component_values[]`, `bpjs_enrollment`, `effective_date`
- Referensi `employee_id` ke [[Microservices - Employee Service]] — NPWP/no.BPJS/rekening **di-join di FE**, tidak disalin.

## Endpoint / Fitur (Sudah Diimplementasikan — Fase 2: Payroll Run)

- **Kalkulasi** (`buildPayslip`): Gaji Pokok = `basic_salary` (bukan komponen → hindari double-count) + komponen manual + Tunjangan Kehadiran penuh + lembur − BPJS (dari `upah_bpjs` + config) − potongan Tunjangan Kehadiran (`base × (1 − payout)`) − **PPh21 = 0** (engine TER = Fase 2b). Hanya komponen `manual` diambil dari `component_values`; yang `computed` dihitung engine.
- **Batch run**: `POST /payroll-runs` (hitung semua karyawan, simpan snapshot per orang; supplement gagal per-orang ditandai, tak gagalkan run) · `GET /payroll-runs` · `GET /payroll-runs/:id` (+ lines) · `POST /:id/recalculate` (draft) · `POST /:id/approve` (approver) · `GET /:id/lines/:employeeId`. Status **draft → approved**.
- **Service-to-service**: panggil [[Microservices - Attendance Service]] `GET /payroll-supplement` (`payout_pct` **persentase 0–100** → prorata Tunjangan Kehadiran + lembur) via `InternalRequest`.
- Grounded: **golden test reproduksi slip nyata** (gross 4.328.500 & BPJS 32.200/96.600 cocok persis; net 4.094.423 ~slip, selisih ~4 rp krn payout dibulatkan 1 desimal) + smoke E2E lolos.

## Model Data (`payroll_db`)

- `salary_component` · `employee_salary` · `payroll_config` (singleton) · `payroll_run` · `payroll_run_line`

## Belum Diimplementasikan / Catatan

- **PPh21 TER** (engine pajak; tabel TER kategori A/B/C per PTKP) = **Fase 2b** — saat ini **PPh21 = 0**. **Formula lembur** default `jam × (gaji_pokok/173)` (DJTK 1.5×/2× = TBD konfirmasi HRD). **Insentif** = komponen manual (belum integrasi [[Finance - Incentive]]).
- **Slip gaji** (PDF) = Fase 3. **THR & rekonsiliasi PPh21 tahunan** = Fase 4. **Dashboard + export Accurate** = Fase 5 ([[ADR - 0001 Akuntansi via Accurate]]).
- **FE** "Pengaturan Gaji" (5 tab: Komponen Gaji, Gaji Karyawan, BPJS, Pajak/PTKP, Perusahaan) — **✅ Fase 1 ada** ([[APP - Web ERP]]; branch `feat/payroll-fe`, belum merge). Butuh service ini ter-deploy di gateway untuk E2E.
- **Multi-company ditunda** (Fase 1 single-company) — kenyataan grup punya >1 entitas (mis. CV Pure Glow Lux, PT Bharata Internasional).
- Validasi referensial (`component_id` / eksistensi `employee_id`) dilakukan di FE; assign gaji memakai role `isHR`.

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — master karyawan (NPWP/BPJS/bank) via `employee_id`; juga penyedia `payroll-approx`
- [[Microservices - Attendance Service]] — `payroll-supplement` (agregasi kehadiran periode 26→25) = input kalkulasi (Fase 2, **sudah dipakai**)
- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]] — routing + auth
- [[DB - Overview and Notes]] — pola database-per-service ([[ADR - 0002 Database-per-Service]])

## Dokumen Terkait

- [[HRIS - Payroll]] · [[HRIS - Compensation & Benefits]] — konsep/bisnis (pasangan dok ini)
- [[Microservices - Employee Service]] · [[Microservices - Attendance Service]]
