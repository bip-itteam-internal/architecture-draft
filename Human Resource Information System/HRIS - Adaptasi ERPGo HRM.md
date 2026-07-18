# HRIS - Adaptasi ERPGo HRM

## Deskripsi

*Peta **gap-analysis** modul **HRM ERPGo SaaS** terhadap bip-erp — **grounded ke bedah kode service HR yang benar-benar berjalan** (bukan hanya status marker vault). Memetakan checklist ERPGo ke status nyata (**sudah jalan / ada sebagian / dok konsep / kandidat baru / buang**) agar Product Owner punya **satu rujukan** untuk memutuskan apa yang layak diimplementasikan. Dokumen ini **tidak menyalin** dok lain; ia **mengindeks** & menautkan (anti-duplikasi). Melanjutkan pola adaptasi-ERPGo-selektif di [[HRIS - Recruitment]] & [[HRIS - Training Program]].*

- **Status**: 🟡 Analisis / Peta adaptasi (dokumen keputusan; **status nyata per-item ada di tabel**). Grounded ke **bedah route/handler/model** lima service HR (`employee`, `attendance`, `payroll`, `hrd-document`, `notification`) per 2026-07-18.
- **Metode grounding**: baca registrasi route + handler + model tiap service, tandai stub/501/TODO, lalu padankan ke checklist ERPGo. Temuan yang mengoreksi dok vault dicatat di §Diskrepansi.

## Latar Belakang & Metode

ERPGo HRM dipakai sebagai **referensi kelengkapan** (checklist), **bukan** cetak biru wajib. bip-erp **sudah punya 26 dok HRIS lain** dan sebagian besar area ERPGo sudah tercakup — nilai dokumen ini adalah **menyaring** (mana yang sudah jalan di kode, mana yang benar-benar baru & layak) sambil menghindari over-engineering. Metode "Ambil / Sesuaikan / Buang" sama seperti [[HRIS - Training Program]] & [[HRIS - Work Review]], **tapi kali ini verdict di-back oleh bedah kode**, bukan status marker dok.

**Legenda status per-item:**

| Kode | Arti |
|---|---|
| ✅ | **Sudah jalan di kode** (route/model nyata; jangan bangun ulang) |
| ⚠️ | **Ada sebagian / fondasi ada** (jalan, ada gap konkret) |
| 🟡 | **Baru dok konsep**, belum di kode (tinggal eksekusi) |
| 🆕 | **Kandidat baru** — belum ada kode, layak dipertimbangkan |
| ❌ | **Buang / tidak relevan** dengan kondisi bip-erp |

## Bedah Sistem HR yang Sudah Berjalan (grounded ke kode `bip-erp`)

Ringkasan hasil bedah route/handler/model. Semua service Go + Fiber v2 + MongoDB, di belakang [[CORE - API Master Gateway]] + gateway-key global; RBAC per-role hanya di sebagian route (via `system_roles`, [[Microservices - Employee Service]] `common/roles.go`).

### [[Microservices - Employee Service]] — master org, karyawan, KPI, cuti-kuota
- **Master org**: `master_department` (key/name/**positions[]**/roles[]) CRUD (`/master/departments`, RBAC `RequireHRISOrITSupervisor`) + `master_system_role` CRUD. Seed 10 dept + 2 role saat kosong.
- **Karyawan**: `personal_data`, `work_data` (embed **Vacation**, `is_supervisor`, `bpjs_ks/kt_number`, `bank_detail`), `work_schedule`, `system_authentication` (`system_roles` map). Create/update 6-langkah via `/internal/transaction/create-employee` (`RequireHRISStaff`, Mongo txn). Banyak CRUD mentah **schemaless** (tanpa RBAC per-role).
- **Agregasi**: `/v2/internal/aggregate/employees` (+`/summary`, +`/it`), `/internal/aggregate/employee/:id`, `/internal/export/all`.
- **Cuti/kuota**: `/vacation`, `/vacation/quota`, `/vacation/decrement` — **embedded di `work_data`** (bukan collection). Cron reset cuti tahunan 1 Jan.
- **KPI**: `/kpi` (matriks), `/kpi/dashboard`, `/kpi/templates` CRUD, `POST /kpi` (skor snapshot template, bobot Σ=1.0). RBAC department-scoped (HRIS bypass total).
- **Kontrak/BPJS**: `/contract` GET+PATCH (status ongoing/ending≤2bln/expired); `/bpjs` **read-only 2 field string** (tanpa perhitungan iuran).
- **Self-service `/me/*`**: profil, kpi-score, vacation, **`payroll-approx` (proxy ke attendance)**, photo.
- **Belum jalan**: modul **Training** (model+collection `training_type/trainer/training/training_participant` **ada tapi NOL route** — belum di-wire). **Org chart** tak ada (supervisor = boolean `is_supervisor` + fallback regex posisi + remap GA→HR). Tanpa 501/stub.

### [[Microservices - Attendance Service]] — presensi, leave, shift, koreksi, dinas, libur
- **Presensi**: `/tap` (clock-in/out; **`?method=Website` = STUB 501** di `main.go:869/871`; **Fingerprint & Mobile jalan**), `/report` (grid kehadiran bulanan, `RequireHRISStaff`), `/entries`, `/history`, `/today`, `/mood`, `PATCH /:id/update` (HR set status/leave_hour/**overtime_hour** manual).
- **Leave (pola request→approval)**: `/request/create|view|review|cancel` + `/request/security-lookup|security-verify` (rantai **SPV→HR**; izin per-jam → verifikasi QR satpam). Katalog **Sakit/Izin/Cuti/Dinas** + subtipe lengkap. Kuota Cuti tahunan cek+decrement ke employee-service.
- **Turunan pola yang sama**: **Business-trip** (Perjadin), **Correction** (anti-fraud guestbook, SPV→HR), **Schedule-exchange** (**Tukar Shift 3-langkah** consent→SPV→HRD, **Tukar Hari 2-langkah**). HR admin lintas-jenis `/hr/requests`.
- **Payroll-supplement**: `/payroll-supplement` (agregat 26→25, `payout_pct`; **tanpa RBAC guard**) + `/payroll-status-treatment` GET/PUT (**perlakuan bayar per-status/subtipe configurable**).
- **Hari libur**: `/holiday` GET/POST/DELETE (mutasi `RequireHRISStaff`), collection `company_holiday` — **CRUD nyata sudah ada**.
- **Cron**: prealloc entri (Pending→Alpha di jam mulai), auto-ignore stale 24 jam, reminder reviewer.
- **Catatan**: `company_work_schedule` **di-drop & re-seed tiap start** (statik, **belum bisa diatur HR** dari HRIS). Field `paid_leave_hour` **tidak ada** (mekanisme = `leave_hour` + master treatment).

### [[Microservices - Payroll Service]] — setup gaji, run, PPh21 TER, THR, slip
- **Config**: `/config/company`, `/config/bpjs` (5 program rate/cap), `/config/tax` (**PPh21 TER + PTKP**); master multi-badan-usaha `/companies`.
- **Komponen**: `salary-components` CRUD (earning/deduction, taxable, bpjs_base, **manual vs computed**) — di-seed 15. **Gaji per karyawan**: `employee-salary` GET/PUT (basic_salary, upah_bpjs, ptkp_status, component_values, bpjs_enrollment).
- **Run**: `POST /payroll-runs` (draft + hitung semua) → `recalculate` → `approve` → `publish`; **THR** `POST /thr-runs` (reuse lifecycle run). **Slip self-service** `/payroll-runs/my[/:id]` (**hanya run published**, field HR di-redaksi).
- **Engine nyata** (grounded ke fungsi): **PPh21 TER** (`terRate×gross`, tabel penuh PMK 168/2023) ✓ · **BPJS** (**sisi karyawan saja**; `company_rate` tersimpan tapi **tak dipakai** — tak ada baris beban perusahaan) ⚠️ · **prorata Tunjangan Kehadiran** (`base×payout` dari supplement) ✓ · **THR** (`basic×proporsi masa kerja`, Permenaker) ✓ · **Lembur** simplistik (`basic/173`, **tanpa multiplier 1,5×/2×** — TBD) ⚠️.
- **Belum ada** (dikonfirmasi absen di kode): **generate PDF slip**, **rekonsiliasi PPh21 tahunan** (true-up Desember), **export Accurate**, **dashboard/laporan**, delete/void run. Tanpa 501/stub.

### [[Microservices - HRD Document Service]] — dokumen HRD + targeting + ack + versioning
- **Route**: `document-types` CRUD (registry SOP/S&K/Kebijakan/Panduan), `/my/documents` (published, resolve target), `documents` CRUD + `publish` (versi immutable) + `versions`, `/ack`.
- **Targeting `targets[]`**: 5 dimensi (**all/position/department/request_type/employee**) semantik OR; `request_type` **hanya** via `?request_type=` (konteks S&K submit), tak muncul di daftar umum.
- **Ack**: model + pencatatan idempoten **ada**; **enforcement pemblokiran BE = TIDAK ADA** (gate di FE/attendance) → **Fase 2**.
- **Gap**: soft-validate nilai target, enforcement ack BE, status `archived` tanpa endpoint, publish/ack non-atomik tanpa unique index, URL attendance di-wire tapi belum dipakai.

### [[Microservices - Notification Service]] — inbox, FCM, WhatsApp, Email — **relevan untuk Announcements**
- **Channel semua nyata**: **Inbox** (Mongo), **FCM** (Firebase Admin, multicast 500), **WhatsApp** (`notifapi.com`, 3 grup hardcoded), **Email/Resend** (`resend-go/v3`, **sudah jadi + ada unit test** — bukan TODO).
- **Konten broadcast eksisting**: `Article` (**papan pengumuman global, dibaca semua user** via `/article`) + `SplashPromotion` (pop-up). Push fan-out: **`/fcm/send-broadcast`** (semua per platform) + **`/fcm/send-department`** (per segmen).
- **Batasan**: **Inbox = per-individu** (tak ada bulk/fan-out); Email multi-recipient tapi **tanpa resolusi audiens**; enum `InboxCategories` **belum ada** kategori "announcement".

### Ringkasan kapabilitas riil
> **Absensi & Cuti + Payroll + Master org (dept/posisi) + Dokumen HRD + semua channel notifikasi (termasuk Email)** = **sudah jalan di kode**, sebagian **melebihi** ERPGo. Yang **benar-benar kosong di kode**: Awards, Events, Kasbon/Loan, org chart, PDF slip. Yang **punya fondasi tapi belum jadi fitur**: Announcements (fondasi Article + broadcast + Email **ada**), Training (model ada, route belum).

## Prinsip Adaptasi Lintas-Cutting

1. **Single-site → buang "Branch".** Org unit tunggal = **Department** (`master_department`). Adaptasi terpenting (sudah ditegaskan [[HRIS - Training Program]] & [[HRIS - Organization Structure]]).
2. **Batas scope Payroll vs Accurate.** Yang menyentuh jurnal → Accurate ([[ADR - 0001 Akuntansi via Accurate]]). Sisi finansial fitur HR = informasional/pencatatan.
3. **Anti over-engineering.** Buang form-builder, tunda AI-assist, sederhanakan "Approved By" tak perlu (konsisten keputusan sadar tim).
4. **Reuse master & pola, jangan bikin tandingan.** `master_department`, targeting `targets[]` HRD, pola request→approval ([[HRIS - Employee Request & Approval]]), upload MinIO ([[Microservices - File Service]]), broadcast FCM/Article/Email ([[Microservices - Notification Service]]) **sudah ada** — item baru menumpang, bukan menduplikasi.

## Peta ERPGo HRM → bip-erp

### Dashboard HRM
| Item | Status | Grounded |
|---|---|---|
| Dashboard KPI HR (Total/Present/Absent/On-Leave, dsb.) | ✅ | **Dashboard HRM gaya ERPGo dibuat** (`/hris/dashboard`, PR erp-frontend #394): 8 KPI cards + widget monitoring (grounded ke `/entries` hari-ini, summary, requests, article, holiday/birthdays); demografi pindah ke `/hris/analysis`. Sebelumnya terpencar (`/kpi/dashboard`, `/report`, [[BASE - Enterance Point]]). Payroll masih **tanpa dashboard**. |

### 1. System Setup (17 master)
| Master ERPGo | Status | Grounded |
|---|---|---|
| Branches | ❌ | Buang — single-site. |
| Departments · Designations | ✅ | `master_department` CRUD (+positions[]) — [[Microservices - Employee Service]] · [[HRIS - Organization Structure]]. |
| Allowance · Deduction Types | ✅ | `salary-components` earning/deduction (manual/computed) — [[Microservices - Payroll Service]]. |
| Working Days / Shift | ⚠️ | `company_work_schedule` jalan **tapi statik seed** (drop+re-seed tiap start; belum bisa diatur HR). — [[HRIS - Attendance System]]. |
| Holiday (+ Types) | ⚠️→✅ | **CRUD `/holiday` nyata** di attendance (`company_holiday`); *typing* kategori belum. Lihat kandidat **Kalender** di bawah. |
| Document Types / Categories | ⚠️ | Registry `type` (SOP/S&K/Kebijakan/Panduan) + `personal_document` — [[HRIS - HRD Documents]]. |
| Termination · Warning · Complaint Types | 🟡 | Bagian dok konsep [[HRIS - Attrition]]/[[HRIS - Personalia]] · [[HRIS - Disciplinary (Surat Peringatan)]] · [[HRIS - Conflict Management]]. |
| Award Types | 🆕 | Kandidat **Awards** di bawah. |
| Announcement Categories · Event Types | 🆕/⚠️ | Announcement: fondasi ada (lihat kandidat). Event: baru. |
| Loan Types | 🆕 | Kandidat **Kasbon** di bawah. |
| IP Restricts | ❌ | Tidak relevan — absen via fingerprint/mobile (Website `/tap` = 501), bukan web-tap ber-IP. |

### 2. Employees (wizard 6 tahap)
| Item | Status | Grounded |
|---|---|---|
| Data karyawan (Personal/Employment/Contact/Banking/Hours&Rates/Documents) | ✅ | `personal_data`+`work_data`+`system_authentication`+dokumen (Employee) + bank/basic_salary/ptkp (Payroll `employee-salary`). Create 6-langkah via `/internal/transaction/create-employee`. |
| Wizard UI 6-tahap | ⚠️ | Data & transaksi sudah ada; **wizard = kemasan UI**. Onboarding baru lewat hire Recruitment → create-employee ([[Microservices - Recruitment Service]]). Bukan fitur baru. |

### 3. Payroll & Kompensasi
| Item | Status | Grounded |
|---|---|---|
| Set Salary | ✅ | `employee-salary` GET/PUT — [[Microservices - Payroll Service]]. |
| Payrolls (batch run) | ✅ | Run draft→approved→published + **PPh21 TER** + **THR**; prorata kehadiran dari supplement. — [[HRIS - Payroll]]. |
| Payslip | ⚠️ | Slip **self-service (JSON) jalan**; **PDF/cetak TIDAK ADA** (dikonfirmasi). |

> **Lebih maju dari ERPGo** (PPh21 TER, THR, prorata kehadiran). **Gap riil**: PDF slip · rekonsiliasi PPh21 tahunan · beban BPJS perusahaan (config ada, engine tak pakai) · multiplier lembur · export Accurate.

### 4. Absensi & Cuti
| Item | Status | Grounded |
|---|---|---|
| Shifts · Attendance grid · Leave Types · Leave Applications · Leave Balance | ✅ | Semua nyata: `/report` grid, katalog Sakit/Izin/Cuti/Dinas + subtipe, `/request/*` (SPV→HR), kuota `/vacation`. — [[HRIS - Leave Request]] · [[HRIS - Attendance System]]. |

> **Area paling matang** — bip-erp **melebihi** ERPGo (subtipe payroll-aware, verifikasi satpam, Tukar Shift/Hari, Perjadin, Koreksi, auto-ignore). Tak ada yang perlu diambil dari ERPGo.

### 5. Employee Lifecycle
| Item | Status | Grounded |
|---|---|---|
| Promotions · Transfers | 🟡 | Konsep [[HRIS - Career & Promotion]]; eksekusi = ubah `work_data` + workflow. |
| Resignations · Terminations | 🟡 | [[HRIS - Personalia]] (off-boarding) + [[HRIS - Attrition]]. |
| **Awards** | 🆕 | Belum ada di kode — kandidat di bawah. |

### 6. Disiplin, Dokumen & Komunikasi
| Item | Status | Grounded |
|---|---|---|
| Warnings (SP) | 🟡 | Konsep [[HRIS - Disciplinary (Surat Peringatan)]]. |
| Complaints | 🟡 | Konsep [[HRIS - Conflict Management]]. |
| Documents · Acknowledgments | ⚠️ | BE nyata ([[Microservices - HRD Document Service]]): CRUD+publish+versi+ack; **enforcement ack BE & FE karyawan = Fase 2**. |
| **Announcements** | ⚠️ | **Fondasi ADA** (Article global + FCM broadcast/dept + Email) — bukan nol. Lihat kandidat. |
| **Events** | 🆕 | Belum ada. |
| Holidays | ✅ | CRUD `/holiday` di attendance (lihat System Setup). |

## Kandidat Baru / Perluasan — "Ambil / Sesuaikan / Buang"

### A. Announcements / Pengumuman — ⚠️ **PERLUAS fondasi (bukan net-new)**
Temuan bedah kode membalik asumsi awal: infrastruktur inti **sudah ada**.

| Aspek | Keputusan | Grounded |
|---|---|---|
| Papan pengumuman | ✅ Sudah ada | `Article` (dibaca semua user) + `SplashPromotion` — [[Microservices - Notification Service]]. |
| Notifikasi push | ✅ Sudah ada | `/fcm/send-broadcast` (semua) + `/fcm/send-department` (segmen). |
| Email | ✅ Sudah ada | Resend jalan + teruji (Roadmap Fase B "belum" = **stale**, lihat §Diskrepansi). |
| **Penyasaran per posisi/dept** | 🔧 Tambah | `Article` kini **global-only** → reuse pola `targets[]` HRD ([[HRIS - HRD Documents]]), jangan bikin tandingan. |
| **Inbox fan-out** | 🔧 Tambah | Inbox **per-individu**; perlu bulk-insert bila pengumuman harus masuk inbox tiap orang. |
| **Kategori** | 🔧 Tambah | Tambah nilai `announcement` di `InboxCategories`. |
| Approval "Approved By" | 🔧 Buang | HR/Direktur publish langsung (prinsip #3). |

**Verdict**: **quick-win termurah** — tinggal tambah targeting + kategori + (opsional) fan-out inbox di atas `Article`/broadcast yang sudah jalan.

### B. Awards / Employee Recognition — 🆕
| Aspek | Keputusan | Grounded |
|---|---|---|
| Master `award_type` + transaksi `award` (Employee, Type, Date, Sertifikat) | ✅ Ambil core | Pola master→transaksi = `training_type`→`training` (model sudah ada di Employee, tinggal wire). |
| Branch | 🔧 Buang | Prinsip #1. |
| Sertifikat | 🔧 Sesuaikan | MinIO via [[Microservices - File Service]]. |
| Approval | 🔧 Sederhanakan | HR-issued langsung. |
| **Penempatan** | Perluas [[Microservices - Employee Service]] | Ringan; reuse master karyawan/dept. |

**Verdict**: biaya rendah; umpan ke [[HRIS - Retention]]/[[HRIS - Work Review]].

### C. Events / Kalender Perusahaan (gabung Holidays) — 🆕 di atas ✅ Holidays
| Aspek | Keputusan | Grounded |
|---|---|---|
| `event` (Title, Type, Start/End Date+Time, Status) | ✅ Ambil core | Sederhana. |
| Gabung dengan Holidays | 🔧 Sesuaikan | **`/holiday` CRUD sudah ada** — tambah Events → satu "Kalender Perusahaan", bukan modul terpisah. |
| Approval kompleks | 🔧 Buang | Prinsip #3. |

**Verdict**: *nice-to-have*; naik bila Announcements dibangun (satu modul "Komunikasi & Kalender HR").

### D. Kasbon / Loan — 🆕 (butuh keputusan)
| Aspek | Keputusan | Grounded |
|---|---|---|
| Master `loan_type` + transaksi (amount, tenor, cicilan) | ✅ Ambil | Kebutuhan kasbon nyata. |
| Potongan otomatis | 🔧 Sesuaikan | Sebagai deduction di [[Microservices - Payroll Service]] (mekanisme `salary-components` computed sudah ada). |
| Bunga | 🔧 Buang | Kasbon umumnya tanpa bunga. |
| **Batas vs Accurate** | ⚠️ Putuskan dulu | Pencatatan pinjaman (HR) vs jurnal (Accurate, [[ADR - 0001 Akuntansi via Accurate]]) — perlu ADR. |

**Verdict**: berguna tapi menyentuh keuangan → keputusan scope dulu.

## Rekomendasi Prioritas (grounded)

- **Tier 1 — Quick-win (fondasi sudah ada di kode):**
  - **Announcements** — perluas `Article`+broadcast+Email (tambah targeting `targets[]` + kategori). 🆕→⚠️
  - **Payslip PDF** — melengkapi Payroll yang sudah matang. ⚠️→✅
- **Tier 2 — Ringan, nilai jelas:**
  - **Awards** (wire model yang sudah ada di Employee Service). 🆕
  - **Events → Kalender Perusahaan** (numpang `/holiday` CRUD). 🆕
- **Tier 3 — Butuh keputusan / eksekusi konsep:**
  - **Kasbon/Loan** — keputusan batas vs Accurate dulu. 🆕
  - **Lifecycle** (Promotions/Transfers/Resignations/Terminations) — dok konsep siap. 🟡
  - **Warnings & Complaints** — dok konsep siap. 🟡
- **Perbaikan Payroll (bukan ERPGo, tapi muncul dari bedah):** rekonsiliasi PPh21 tahunan · beban BPJS perusahaan · multiplier lembur.
- **Buang:** Branches, IP Restricts, wizard 6-tahap sebagai fitur baru, form-builder apa pun.

> **Intinya**: dari 6 kelompok ERPGo, **Absensi&Cuti + Payroll + Master org + Dokumen + Notifikasi** sudah jalan (sebagian melebihi ERPGo); **Lifecycle + Disiplin** sudah punya dok konsep. *Net-new & layak* hanya **Awards, Events, Kasbon** — dan **Announcements yang tinggal diperluas** (bukan dibangun dari nol).

## Diskrepansi Dok Vault vs Kode (untuk `/sync-docs`)

Temuan bedah kode yang **tidak cocok** dengan dok vault — perlu koreksi saat sync:

1. ✅ **dikoreksi di disk** (belum commit — git hang) — **Email/Resend sudah jadi** (kode + unit test); [[HRIS - Roadmap]] Fase B diperbaiki. Catatan: [[Microservices - Notification Service]] **sudah benar** (Email/Article terdokumentasi) — tak perlu diubah.
2. ✅ **dikoreksi di disk** (belum commit) — **Field `paid_leave_hour` tidak ada di kode** (grep 0 match); **hanya** [[HRIS - Leave Request]] yang mengklaimnya (bukan [[Microservices - Attendance Service]]) — diperbaiki ke mekanisme riil (`leave_subtype` + master `payroll_subtype_treatment`/`payroll_status_treatment`).
3. **Modul Training**: model+collection ada di Employee Service **tanpa route** (belum di-wire) — [[HRIS - Training Program]] bilang "belum ada kode"; sebenarnya **scaffolding model sudah ada**. Nuansa kecil.
4. **`Article` (papan pengumuman)** di Notification Service belum tercermin sebagai fondasi Announcements di dok HRIS.
5. **`company_work_schedule` statik** (drop+re-seed tiap start, belum HR-editable) — perjelas di [[HRIS - Attendance System]].

## Belum Diputuskan (TBD)

- **Kasbon vs Accurate** — batas pencatatan HR vs jurnal (perlu ADR bila diambil).
- **Penempatan Announcements** — perluas Notification (`Article`) atau HRD Document Service (yang punya `targets[]`).
- **Awards** — approval berjenjang atau HR-issued langsung.
- **Kalender Perusahaan** — Events & Holidays digabung atau terpisah.
- **Dashboard HRM** — konsolidasi atau cukup tersebar.

## Dokumen Terkait

- [[HRIS - Roadmap]] · [[HRIS - Big Pictures]] · [[HRIS - Analysis]] · [[HRIS - Interrelationship Matrices]] · [[REF - Ownership & RACI]]
- Pola adaptasi ERPGo/Mekari selektif: [[HRIS - Recruitment]] · [[HRIS - Training Program]] · [[HRIS - Work Review]]
- Service yang dibedah: [[Microservices - Employee Service]] · [[Microservices - Attendance Service]] · [[Microservices - Payroll Service]] · [[Microservices - HRD Document Service]] · [[Microservices - Notification Service]] · [[CORE - HRIS Orchestrator]] · [[Microservices - File Service]] · [[Microservices - Recruitment Service]]
- Area sudah ada: [[HRIS - Payroll]] · [[HRIS - Leave Request]] · [[HRIS - Attendance System]] · [[HRIS - Organization Structure]] · [[HRIS - HRD Documents]] · [[HRIS - Compensation & Benefits]]
- Area konsep: [[HRIS - Career & Promotion]] · [[HRIS - Personalia]] · [[HRIS - Attrition]] · [[HRIS - Retention]] · [[HRIS - Disciplinary (Surat Peringatan)]] · [[HRIS - Conflict Management]]
- Keputusan: [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0002 Database-per-Service]] · [[ADR - 0013 HRD Documents]]
