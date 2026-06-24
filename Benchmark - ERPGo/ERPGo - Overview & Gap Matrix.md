## Deskripsi

*Hub benchmark hasil penelusuran fitur **ERPGo SaaS** (Workdo) — demo `demo.workdo.io/erpgo-saas` — dipetakan terhadap **bip-erp** (ERP internal Bharata). Tujuannya: menemukan fitur yang **belum ada / parsial** di sistem kita dan menilai mana yang layak diadopsi, **tanpa mengganggu sistem yang sudah berjalan**. Tiap baris matriks menaut ke dok arsitektur existing dan/atau dok keputusan per-fitur di folder ini.*

- **Sumber data fitur ERPGo**: User Manual resmi Workdo (katalog modul/submenu = persis yang diekspos demo). Demo login-gated, jadi enumerasi memakai dokumentasi resmi, bukan klik-per-tombol.
- **Status area ini**: 🟡 **Benchmark / Konsep** — *point-in-time research*, **bukan** keputusan/komitmen Bharata dan **bukan** dok grounded-in-code. Analog dengan area non-domain `Logs`/`Templates` (lihat [[IT - SOP Dokumentasi Vault]]): dikecualikan dari grounded-in-code untuk **sisi ERPGo**; **sisi Bharata** tetap grounded & ditaut via wikilink.
- **Prefix file**: `ERPGo -` (khusus area benchmark ini).

## Legenda status (sisi Bharata)

- ✅ **Tercakup** — sudah ada padanannya (kode atau dok arsitektur matang)
- 🟡 **Parsial / Direncanakan** — ada sebagian atau masih konsep; bisa diperkaya pola ERPGo
- 🔴 **Gap** — belum ada padanan → kandidat dok keputusan
- ⚠️ **Didelegasikan / Eksternal** — ada tapi ditangani sistem lain (mis. Accurate, vendor CRM)

## Matriks gap — 25 modul ERPGo vs bip-erp

| # | Modul ERPGo | Submenu kunci ERPGo | Status Bharata | Dok terkait | Verdict |
|---|---|---|---|---|---|
| 1 | User & Role Mgmt | Roles, Users, Login History | ✅ | [[CORE - SSO Flow]], [[CORE - API Master Gateway]] | Tercakup |
| 2 | Proposal | Sales proposal + template | 🔴 | — | → [[ERPGo - Quotation & Proposal]] |
| 3 | Sales Invoice | Invoice (product/service), Returns | ⚠️ | [[External - Accurate]], [[Microservices - Integration Service]] | Out-of-scope (Accurate) |
| 4 | Purchase | Purchase Invoice, Returns, Warehouses, Transfers | 🟡 | [[GA - Procurement System]], [[WH - Management System]], [[Microservices - Inventory Service]] | Parsial — enrich |
| 5 | Product & Service | Items, SKU, setup | ✅ | [[Microservices - Inventory Service]], [[Microservices - Integration Service]] | Tercakup |
| 6 | Quotations | Quotation, actions | 🔴 | — | → [[ERPGo - Quotation & Proposal]] |
| 7 | Project Mgmt | Projects, Milestones, Reports | 🟡 | [[Microservices - Task Management Service]], [[APP - Dynamic Task Tracker]] | Parsial — enrich (+[[ERPGo - Timesheet]]) |
| 8 | Accounting | CoA, Banking, Payments, Expense/Revenue, Debit/Credit Notes | ⚠️ | [[Finance]], [[External - Accurate]], [[Finance - Bridging App]] | Out-of-scope (Accurate) |
| 9 | Goal Mgmt (OKR) | Goals, Milestones, Contributions, Tracking | 🔴 | [[HRIS - Key Performance Index]] | → [[ERPGo - Goal (OKR) Management]] |
| 10 | Budget Planner | Periods, Budget, Allocations, Monitoring | 🔴 | [[Finance]] | → [[ERPGo - Budget Planner]] |
| 11 | Double Entry | Ledger, Trial Balance, Balance Sheet, P&L | ⚠️ | [[External - Accurate]] | Out-of-scope (Accurate) |
| 12 | HRM (inti) | Employees, Payslip, Attendance, Leave, Holidays | ✅ | [[Microservices - Employee Service]], [[Microservices - Attendance Service]], [[HRIS - Payroll]] | Tercakup |
| 12b | HRM (lifecycle) | Awards, Promotions, Resignations, Terminations, Warnings, Complaints, Transfers, Acknowledgment, Announcement, Events | 🟡 | [[HRIS - Career & Promotion]], [[HRIS - Disciplinary (Surat Peringatan)]], [[HRIS - Conflict Management]], [[HRIS - Attrition]] | Parsial — enrich |
| 13 | Performance Mgmt | Indicators, Review Cycles, Reviews | 🟡 | [[HRIS - Key Performance Index]], [[HRIS - Work Review]] | → [[ERPGo - Performance Review Cycles]] |
| 14 | Training Mgmt | Types, Trainers, Training List | 🟡 | [[HRIS - Training Program]] | Parsial — enrich |
| 15 | Recruitment (ATS) | Job posting → candidate → interview → offer → onboarding | 🟡 | [[HRIS - Recruitment]], [[Microservices - Recruitment Service]] | Enrich pola ATS |
| 16 | POS | Orders, Barcode, Reports | 🔴 | — | → [[ERPGo - POS (Point of Sale)]] (defer) |
| 17 | CRM (Leads/Deals) | Pipeline, Kanban, 360° deal | ⚠️ | [[Sales - CRM management tool]], [[Vendor - CRM]] | → [[ERPGo - Internal CRM (Leads & Deals)]] |
| 18 | Form Builder | Dynamic form, responses, convert-to-module | 🔴 | [[HRIS - Employee Request & Approval]] | → [[ERPGo - Form Builder]] |
| 19 | Support Ticket | Tickets, Knowledge Base, FAQ, Contact | ✅ | [[IT - Helpdesk]] | Tercakup — enrich KB/FAQ |
| 20 | Contract Mgmt | Contracts, Contract Types | 🔴 | [[GA - Procurement System]] | → [[ERPGo - Contract Management]] |
| 21 | Calendar | Activity calendar | 🟡 | — | Minor (lihat Goal/CRM) |
| 22 | Zoom Meeting | Schedule meeting | 🔴 | — | Minor add-on |
| 23 | Timesheet | Timesheet per project/task | 🟡 | [[Microservices - Attendance Service]], [[Microservices - Task Management Service]] | → [[ERPGo - Timesheet]] |
| 24 | Messenger | Internal chat | 🔴 | [[Microservices - Notification Service]] | → [[ERPGo - Messenger (Internal Chat)]] |
| 25 | SaaS layer | Subscription, Coupon, CMS Landing, Plans | ⛔ | [[Sales - Landing page]] | Out-of-scope (single-tenant) |

## Kandidat dok keputusan (gap → adopsi?)

Dok per-fitur di folder ini (kedalaman **keputusan/benchmark**, bukan spec teknis):

1. [[ERPGo - Contract Management]] — 🔴 gap bersih, fit tinggi (kontrak vendor/customer/karyawan)
2. [[ERPGo - Budget Planner]] — 🔴 gap, melengkapi [[Finance]]
3. [[ERPGo - Goal (OKR) Management]] — 🔴 gap, beda lapis dari KPI
4. [[ERPGo - Form Builder]] — 🔴 gap, fit sangat tinggi (banyak form request internal)
5. [[ERPGo - Quotation & Proposal]] — 🔴 gap (relevan bila ada jalur B2B)
6. [[ERPGo - Internal CRM (Leads & Deals)]] — ⚠️ kini eksternal; peluang internalisasi
7. [[ERPGo - Timesheet]] — 🟡 parsial, melengkapi task/attendance
8. [[ERPGo - Messenger (Internal Chat)]] — 🔴 minor
9. [[ERPGo - Performance Review Cycles]] — 🟡 melengkapi KPI/Work Review
10. [[ERPGo - POS (Point of Sale)]] — 🔴 tapi **defer** (model marketplace, bukan retail)

## Rekomendasi enrichment untuk dok existing (perbaiki vault yang ada)

Pola ERPGo yang bisa **digraft ke dok yang sudah ada** (bukan dok baru):

- [[HRIS - Recruitment]] / [[Microservices - Recruitment Service]] — adopsi struktur ATS ERPGo: **Job Locations**, **Custom Questions** (bank pertanyaan skrining), **Interview Rounds** terdefinisi, **Interview Feedback** terstruktur, **Candidate Assessment** (skor), **Offer** + **Onboarding Checklist Items**. Sebagian sudah selaras dengan rekaman HRD; ERPGo memberi taksonomi yang rapi.
- [[HRIS - Training Program]] — adopsi pemisahan **Training Types**, **Trainers**, **Training List** (peserta + status) sebagai master data minimal.
- [[HRIS - Work Review]] + [[HRIS - Key Performance Index]] — adopsi konsep **Review Cycles** periodik (lihat [[ERPGo - Performance Review Cycles]]).
- [[GA - Procurement System]] / [[WH - Management System]] — adopsi **Purchase Returns** dan **Stock Transfer antar-warehouse** sebagai entitas eksplisit.
- [[GA - Asset Loan & Room Booking]] — sandingkan dengan **HRM › Assets** ERPGo (aset yang ditugaskan ke karyawan) untuk melengkapi siklus aset.
- [[IT - Helpdesk]] — adopsi **Knowledge Base** + **FAQ** publik dari modul Support Ticket ERPGo.
- [[HRIS - Career & Promotion]] / [[HRIS - Attrition]] / [[HRIS - Conflict Management]] — petakan event lifecycle ERPGo (Awards, Transfers, Announcements, Events, Acknowledgment) ke dok-dok ini agar tidak ada lifecycle yang tercecer.

## Out-of-scope (sengaja TIDAK diadopsi)

- **Accounting penuh & Double Entry** (CoA, ledger, balance sheet, P&L) → sudah didelegasikan ke **Accurate** secara sengaja; lihat [[Finance]] (ekosistem finance terenkapsulasi). Menariknya ke internal = duplikasi + risiko ke sistem berjalan.
- **POS retail** → model bisnis = seller marketplace + manufaktur, bukan toko fisik; lihat [[ERPGo - POS (Point of Sale)]].
- **SaaS layer** (subscription, coupon, plan, multi-tenant, CMS landing builder) → bip-erp **single-tenant internal**; hanya landing marketing yang relevan ([[Sales - Landing page]]).

## Catatan jaga sistem berjalan

Semua dok di folder ini berstatus 🟡 dan **tidak mengubah kode**. Tiap rekomendasi adopsi, bila disetujui, harus melewati flow `/start-task → /plan → /implement → /review` tersendiri dan menghormati pola **database-per-service** ([[DB - Overview and Notes]]) serta gerbang **SSO** ([[CORE - SSO Flow]], [[CORE - API Master Gateway]]).

## Dokumen Terkait

- [[DB - Overview and Notes]] · [[CORE - API Master Gateway]] · [[CORE - SSO Flow]]
- [[IT - SOP Dokumentasi Vault]] (aturan area non-domain)
- Semua dok `ERPGo - *` di folder ini.
