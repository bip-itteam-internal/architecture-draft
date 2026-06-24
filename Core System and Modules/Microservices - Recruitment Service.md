## Deskripsi

*Recruitment Service adalah service (direncanakan) yang mengelola **siklus depan karyawan**: permintaan posisi → lowongan → pelamar → screening → interview → background check → psikotes → offer → onboarding handoff. Ini sisi **implementasi** dari konsep/bisnis di [[HRIS - Recruitment]]. **Belum ada di kode** — dokumen ini menetapkan rancangan service-nya.*

- **Stack**: Go + Fiber v2 + MongoDB (`recruitment_db`) — selaras pola service bip-erp lain
- **Path**: `services/recruitment` *(direncanakan)*
- **Status**: 🟡 Konsep / Direncanakan — **belum ada di kode**; di belakang [[CORE - API Master Gateway]], auth **SSO** ([[CORE - SSO Flow]]), role HR/recruitment dari `system_roles`

## Endpoint / Fitur (Direncanakan)

> 🟡 Belum ada di kode — kontrak/path final ditetapkan saat implementasi. Berikut cakupan yang direncanakan per pipeline.

### Job Requisition
- Ajukan permintaan posisi (Form Permintaan Karyawan) + usulan kualifikasi
- Alur approval: **HR (HRGA Supervisor) review kualifikasi → Direktur menyetujui** → `Approved` (tanpa cek kuota)

### Job Posting & Sourcing
- Buka/tutup lowongan; catat sumber pelamar (utama: **Glints/TapLoker**, referral, walk-in, bootcamp)

### Candidate Management
- CRUD pelamar + pelacakan `progress` (tahap) & `status` (keadaan) — enum mengikuti rekaman HRD
- Upload CV/berkas/portofolio → [[Microservices - File Service]] (MinIO)

### Screening · Interview · Technical Test · Background Check · Psikotes
- Screening **manual** (HR putuskan lanjut/reject); AI CV screening = fase lanjut
- Interview multi-tahap (HR / User / Final) + Technical Test (tes skill)
- Background Check; Psikotes (**manual oleh staf HR** — input skor + report PDF; online = fase lanjut)

### Offer & Onboarding
- Terbitkan offer (+ surat penawaran PDF) → accept/decline
- `Hired` → **handoff** ke [[Microservices - Employee Service]] `POST /onboarding/register` (employee_id + temporary password)

### Notifikasi
- Internal (approval/jadwal/offer) + **kandidat eksternal via Email (Resend, direncanakan) → WhatsApp menyusul** — lewat [[Microservices - Notification Service]]

## Model Data (`recruitment_db`)

> Detail field per collection ada di [[HRIS - Recruitment]] (hindari duplikasi).

- `job_requisition` · `job_posting` · `candidate` (+`progress`/`status`) · `screening_result` · `interview` · `technical_test_result` · `psychotest` · `psychotest_result` · `background_check` · `offer`

## Belum Diimplementasikan / Catatan

- **Seluruh service belum ada di kode** (🟡) — scaffolding mengikuti pola `services/.template`.
- `recruitment_db` (container Mongo) **akan didaftarkan** di [[DB - Overview and Notes]] saat implementasi; rute `/api/recruitment/*` ditambahkan ke [[CORE - API Master Gateway]] (`InternalURL`) saat itu juga.
- **AI CV screening** (LLM OpenRouter + OCR) & **psikotes online** (test-engine + bank soal) = **fase lanjut**.
- **Email channel** (kandidat) menunggu kemampuan email di [[Microservices - Notification Service]] (belum ada — lihat catatan di sana).
- Relasi dengan **Glints** (impor/sinkron vs menggantikan) = TBD strategis.

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — master posisi/departemen (`PositionTitle*`), cek duplikasi, **handoff `/onboarding/register`** saat hire
- [[Microservices - File Service]] — CV/berkas pelamar, report PDF psikotes, surat penawaran (MinIO)
- [[Microservices - Notification Service]] — notifikasi internal + kandidat (Email/Resend direncanakan + WhatsApp + inbox)
- [[CORE - OCR Document Service]] — OCR CV hasil scan (untuk AI screening fase lanjut)
- **LLM (OpenRouter)** — AI CV screening (fase lanjut); reuse infra Ideamills ([[Sales - Veo (Gemini) Implementation]])
- **Glints (TapLoker)** — ATS/job-portal eksternal, sumber pelamar utama
- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]] — routing + auth
- [[DB - Overview and Notes]] — pola database-per-service

## Dokumen Terkait

- [[HRIS - Recruitment]] — konsep/bisnis & keputusan HRD (pasangan dok ini)
- [[Microservices - Employee Service]] · [[Microservices - Notification Service]] · [[Microservices - File Service]]
- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]]
