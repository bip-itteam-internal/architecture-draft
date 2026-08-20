## Deskripsi

*Dashboard ini menampilkan seluruh attrition dari departemen internal yang mencakup karyawan yang masuk dan yang keluar*

[Contoh dari sistem ini](https://drive.google.com/drive/folders/17RNDBtMwKCU_tuAiLZbwCgFp-xwwmzuz)

- **Status**: ⚠️ **Fase 1 (Setup) + Fase 2 (Payroll Run + publish + slip self-service) + Fase 2b (PPh21 TER) + Fase 4 (THR) sudah di kode** ([[Microservices - Payroll Service]]) — komponen gaji, config BPJS/pajak, assign gaji per karyawan, + **payroll run** (kalkulasi gross → BPJS → potongan kehadiran → **PPh21 TER** → net; lifecycle **draft → approved → published**; karyawan lihat **slip sendiri** via self-service). Penggajian **bulanan** (tak ada mingguan). *Supplement* attendance dipakai untuk prorata Tunjangan Kehadiran (⚠️ **diganti potongan eksplisit 4 baris**, lihat §Potongan Kehadiran Eksplisit — belum merged). Scope: **sampai terbitkan slip, tanpa pembayaran**. **Slip PDF/cetak = fase berikut.**

## Sudah Diimplementasikan (komponen attendance)

> Grounded: bagian ini = penyedia *supplement* berbasis kehadiran di [[Microservices - Attendance Service]] (input untuk payroll-service). Engine payroll penuh ada di [[Microservices - Payroll Service]] — lihat bagian Fase 1 & 2b di bawah.

- `GET /payroll-supplement` ([[Microservices - Attendance Service]]) — agregasi entry kehadiran **periode payroll 26 bln-lalu → 25 bln-ini**: `payout_pct = total_work_hours / expected_work_hours`, plus rincian jam (telat, cuti, lembur, absen) & hitung per status. Entry `Pending` dilewati dari kalkulasi payout. **Status mana dibayar vs dipotong kini _configurable_** (master `payroll_status_treatment`; FE tab **"Perlakuan Kehadiran"** di Pengaturan Gaji, sejak 2026-08-09 disunting pemegang **`payroll.manage`** dan dibaca pemegang `payroll.view`, bukan lagi siapa pun berdepartemen HR). Default: Cuti/Sakit/Dinas/Libur = dibayar; Izin/Tanpa Keterangan = dipotong. Master juga punya **override per-subtipe** (`payroll_subtype_treatment`, diturunkan dari `LeaveSubtypes`; PR #271/#169), dan **kini memengaruhi payout** (Fase 2, PR #273): subtipe dipersist ke `attendance_entries`, `computePayoutBreakdown` menerapkan override per-(status,subtipe) di atas per-status. Berlaku untuk **entry baru** (tanpa backfill); efektif bila HR meng-custom subtipe (default subtipe = default status).

- `GET /payroll-approx` ([[Microservices - Employee Service]]) — endpoint per-karyawan yang mem-proxy `payroll-supplement` (pakai `employee_id` dari header).
- Konsumen: [[CORE - HRIS Orchestrator]] (sisi perhitungan payroll).

## Potongan Kehadiran Eksplisit (⚠️ belum merged — [#1317](https://github.com/bip-itteam-internal/bip-erp/pull/1317) · [#1318](https://github.com/bip-itteam-internal/bip-erp/pull/1318) · [erp-frontend #1109](https://github.com/bip-itteam-internal/erp-frontend/pull/1109))

**`payout_pct` berhenti menentukan rupiah.** Ia tetap dihitung dan tetap ditampilkan, tapi
potongan kini dihitung eksplisit jadi **empat baris slip** bertarif tetap:

| Baris | Tarif | Dasar |
|---|---|---|
| Potongan Telat | `tunjangan_kehadiran / 173` per jam | pembagi upah sejam, sama dengan lembur |
| Potongan Izin | `tunjangan_kehadiran / 26` per hari (sebagian diprorata) | hari kerja sebulan |
| Potongan Mangkir | 1,5x tarif harian sehari · **2x per hari** bila ≥ 2 hari | **Peraturan Perusahaan Pasal 20** |
| Potongan Uang Makan | Rp 10.000 per hari bila tak hadir > 4 jam | kebijakan perusahaan |

**Kenapa ini ada**: HRD menghitungnya tangan di Excel, dan satu baris gabungan mustahil
dicocokkan baris per baris. Keempat angka + dua pengali mangkir jadi **config**
(`payroll_config.attendance_deduction`), disunting HR lewat tab **"Potongan Kehadiran"** di
Pengaturan > Payroll. Rincian mekanisme & jebakannya: [[Microservices - Payroll Service]].

⚠️ **Sumber kebenaran aturan potongan TIDAK ada di vault ini.** Ia tinggal di
`mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` (turunan teknis
*Peraturan Perusahaan PT Bharata Internasional Pharmaceutical 2026-2028*). Akibat nyata:
rancangan awal fitur ini memotong mangkir 1x, **setengah** dari yang diatur Pasal 20, dan
baru tertangkap saat review. **Tiap perubahan aturan potongan wajib membuka berkas itu
lebih dulu.**

🔜 **Penyimpangan sadar yang belum ber-ADR**: dokumen itu menyatakan "Izin Jam Kerja
memotong Tunjangan Kehadiran & Uang Makan" **tanpa ambang**, sementara implementasi memakai
ambang 4 jam (keputusan pemilik produk 2026-08-20). Layak diangkat jadi ADR supaya tak
ditemukan lagi sebagai kejutan.

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

## Belum Diimplementasikan (slip & pajak)

Setup gaji + **engine payroll run** (kalkulasi gross → BPJS → potongan kehadiran → **PPh21 TER** → net; prorata Tunjangan Kehadiran via `payroll-supplement`; lembur) **sudah ada** ([[Microservices - Payroll Service]] Fase 1 + 2 + 2b). **PPh21 TER** (metode TER bulanan PMK 168/2023) kini dihitung — ⚠️ angka tabel TER **perlu sign-off HRD/Finance** (editable via config). **THR** ✅ **sudah di kode (Fase 4)** — run THR terpisah, basis **gaji pokok × proporsi masa kerja** (Permenaker), PPh21 TER standalone (aktor & alur: [[HRIS - Payroll Persona]]). **Belum di kode**: generate **payslip** (PDF), **rekonsiliasi PPh21 tahunan Desember** (true-up Ps.17), dashboard, serta handoff/export → Accounting. Gaji/akuntansi final didelegasikan ke Accurate ([[ADR - 0001 Akuntansi via Accurate]]) — **batas scope payroll vs Accurate masih perlu diputuskan**.

## Dokumen Terkait

- [[Microservices - Payroll Service]] (implementasi Fase 1) · [[Microservices - Attendance Service]] (`payroll-supplement`) · [[Microservices - Employee Service]] (`payroll-approx`) · [[CORE - HRIS Orchestrator]]
- [[HRIS - Overtime]] · [[HRIS - Compensation & Benefits]] · [[Finance - Big Pictures]] · [[ADR - 0001 Akuntansi via Accurate]]
