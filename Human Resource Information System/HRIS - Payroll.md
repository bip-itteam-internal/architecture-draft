## Deskripsi

*Dashboard ini menampilkan seluruh attrition dari departemen internal yang mencakup karyawan yang masuk dan yang keluar*

[Contoh dari sistem ini](https://drive.google.com/drive/folders/17RNDBtMwKCU_tuAiLZbwCgFp-xwwmzuz)

- **Status**: ⚠️ **Fase 1 (Salary Setup & Config) sudah di kode** ([[Microservices - Payroll Service]]) — komponen gaji, config BPJS/pajak, assign gaji per karyawan. Komponen *supplement* dari attendance juga **✅ ada**. **Payroll run/kalkulasi + slip gaji = fase berikut.**

## Sudah Diimplementasikan (komponen attendance)

> Grounded: belum ada `payroll-service`/payroll penuh. Yang ada baru penyedia *supplement* berbasis kehadiran.

- `GET /payroll-supplement` ([[Microservices - Attendance Service]]) — agregasi entry kehadiran **periode payroll 26 bln-lalu → 25 bln-ini**: `payout_pct = total_work_hours / expected_work_hours`, plus rincian jam (telat, cuti, lembur, absen) & hitung per status. Entry `Pending` dilewati dari kalkulasi payout.
- `GET /payroll-approx` ([[Microservices - Employee Service]]) — endpoint per-karyawan yang mem-proxy `payroll-supplement` (pakai `employee_id` dari header).
- Konsumen: [[CORE - HRIS Orchestrator]] (sisi perhitungan payroll).

## Sudah Diimplementasikan (payroll-service — Fase 1: Setup & Config)

> Service baru [[Microservices - Payroll Service]] (`services/payroll`, `payroll_db`, port 6980, branch `feat/payroll-service`). Grounded ke **slip gaji nyata** (CV Pure Glow Lux).

- **Config** (singleton, seed default): perusahaan (kop slip), **BPJS** (rate/cap 5 program), **pajak PPh21 metode TER** + PTKP per status.
- **Master komponen gaji** (`/salary-components`): di-seed **15 komponen persis slip** (9 pendapatan + 6 pengurangan); tandai `manual` vs `computed`.
- **Gaji per karyawan** (`/employee-salary/:employeeId`): `basic_salary`, **`upah_bpjs`** (dasar BPJS terpisah), `ptkp_status`, komponen manual. Referensi `employee_id` (NPWP/BPJS/rekening di-join FE).

## Fitur

- Dashboard
	- Ikhtisar segala hal yang sangat baik untuk pelaporan kepada stakeholder
	- Tampilan per-departemen
	- Tampilan per-orang
- Kontrol payroll per-karyawan
	- Ini akan menjadi tulang punggung sistem karena informasi ini akan digunakan untuk membuat segala hal pada dashboard
	- Kontrol harian
		- Attendance
		- Cuti
		- Overtime
	- Pencapaian atau prestasi
	- Insentif
	- Asuransi
- Form quality assurance
	- Dokumen ini akan diteruskan dari Human Resource Department ke Accounting

## Detail yang Tertunda

- [ ] Informasi lebih lanjut tentang apa yang memengaruhi kontrol payroll harian untuk karyawan

* Setting Gaji
* Setting BPJS Kesehatan dan Ketenagakerjaan
* Perhitungan Izin selain sakit dan cuti
## Kebutuhan

- [ ] Master data karyawan (referensi lookup)
	- [ ] Detail bank pembayaran
- [ ] Informasi dan rincian attendance
	- Ini diperlukan untuk mengambil informasi jam kerja normal dan overtime

## Dependensi

- [ ] DB - Attendance Data

## Belum Diimplementasikan (kalkulasi & slip)

Setup gaji, BPJS, dan pajak **sudah ada** ([[Microservices - Payroll Service]] Fase 1). **Belum di kode**: **engine payroll run** (kalkulasi BPJS/PPh21 TER, prorata Tunjangan Kehadiran via `payroll-supplement`, lembur), generate **payslip**, THR, dashboard, serta handoff/export → Accounting. Gaji/akuntansi final didelegasikan ke Accurate ([[ADR - 0001 Akuntansi via Accurate]]) — **batas scope payroll vs Accurate masih perlu diputuskan**.

## Dokumen Terkait

- [[Microservices - Payroll Service]] (implementasi Fase 1) · [[Microservices - Attendance Service]] (`payroll-supplement`) · [[Microservices - Employee Service]] (`payroll-approx`) · [[CORE - HRIS Orchestrator]]
- [[HRIS - Overtime]] · [[HRIS - Compensation & Benefits]] · [[Finance - Big Pictures]] · [[ADR - 0001 Akuntansi via Accurate]]
