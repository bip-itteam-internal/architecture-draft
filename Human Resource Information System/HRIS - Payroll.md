## Deskripsi

*Dashboard ini menampilkan seluruh attrition dari departemen internal yang mencakup karyawan yang masuk dan yang keluar*

[Contoh dari sistem ini](https://drive.google.com/drive/folders/17RNDBtMwKCU_tuAiLZbwCgFp-xwwmzuz)

- **Status**: 🟡 Konsep (payroll penuh belum dibangun) — **kecuali** komponen *supplement* dari attendance yang **✅ sudah ada** di kode.

## Sudah Diimplementasikan (komponen attendance)

> Grounded: belum ada `payroll-service`/payroll penuh. Yang ada baru penyedia *supplement* berbasis kehadiran.

- `GET /payroll-supplement` ([[Microservices - Attendance Service]]) — agregasi entry kehadiran **periode payroll 26 bln-lalu → 25 bln-ini**: `payout_pct = total_work_hours / expected_work_hours`, plus rincian jam (telat, cuti, lembur, absen) & hitung per status. Entry `Pending` dilewati dari kalkulasi payout.
- `GET /payroll-approx` ([[Microservices - Employee Service]]) — endpoint per-karyawan yang mem-proxy `payroll-supplement` (pakai `employee_id` dari header).
- Konsumen: [[CORE - HRIS Orchestrator]] (sisi perhitungan payroll).

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

## Belum Diimplementasikan (payroll penuh)

🟡 Belum di kode: setting gaji nominal, BPJS Kesehatan & Ketenagakerjaan, perhitungan & potongan, generate **payslip**, serta handoff Form QA → Accounting. Gaji/akuntansi final didelegasikan ke Accurate ([[ADR - 0001 Akuntansi via Accurate]]) — **batas scope payroll vs Accurate masih perlu diputuskan**.

## Dokumen Terkait

- [[Microservices - Attendance Service]] (`payroll-supplement`) · [[Microservices - Employee Service]] (`payroll-approx`) · [[CORE - HRIS Orchestrator]]
- [[HRIS - Overtime]] · [[HRIS - Compensation & Benefits]] · [[Finance - Big Pictures]] · [[ADR - 0001 Akuntansi via Accurate]]
