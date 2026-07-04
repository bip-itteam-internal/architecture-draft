## Deskripsi

*Recruitment Service adalah service (direncanakan) yang mengelola **siklus depan karyawan**: permintaan posisi → lowongan → pelamar → screening → interview → background check → psikotes → offer → onboarding handoff. Ini sisi **implementasi** dari konsep/bisnis di [[HRIS - Recruitment]]. **Belum ada di kode** — dokumen ini menetapkan rancangan service-nya.*

- **Stack**: Go + Fiber v2 + MongoDB (`recruitment_db`) — selaras pola service bip-erp lain
- **Path**: `services/recruitment` *(direncanakan)*
- **Status**: ⚠️ **Implemented (Fase 1-3, BE)** di `services/recruitment` (branch `feat/recruitment-service`) — pipeline inti jalan; Fase 4-5 + FE menyusul. Di belakang [[CORE - API Master Gateway]], auth **SSO** ([[CORE - SSO Flow]]), role `system_roles["hris"]`. Port `6979`, mongo `recruitment-mongo-db`.

## Endpoint / Fitur (Direncanakan)

> 🟡 Belum ada di kode — kontrak/path final ditetapkan saat implementasi. Berikut cakupan yang direncanakan per pipeline.

### Job Requisition
- Ajukan permintaan posisi (Form Permintaan Karyawan) + usulan kualifikasi
- Alur approval: **HR (HRGA Supervisor) review kualifikasi → Direktur menyetujui** → `Approved` (tanpa cek kuota)

### Job Posting & Sourcing
- Buka/tutup lowongan; catat sumber pelamar (utama: **Glints/TapLoker**, referral, walk-in, bootcamp)

### Candidate Management
- CRUD pelamar + pelacakan `progress` (tahap) & `status` (keadaan) — enum mengikuti rekaman HRD
- Field `email` kandidat (opsional internal; **wajib saat apply publik**) untuk notifikasi email
- **Dua jalur input:** HR (`POST /candidates`, JWT + role isHR) **atau** kandidat sendiri (apply publik, tanpa JWT — lihat increment di bawah)
- Upload CV/berkas/portofolio → [[Microservices - File Service]] (MinIO)

### Screening · Interview · Technical Test · Background Check · Psikotes
- Screening **manual** (HR putuskan lanjut/reject); AI CV screening = fase lanjut
- Interview multi-tahap (HR / User / Final) + Technical Test (tes skill)
- Background Check; Psikotes (**manual oleh staf HR** — input skor + report PDF; online = fase lanjut)

### Offer & Onboarding
- Terbitkan offer (`POST /candidates/:id/offer`) → unggah surat penawaran PDF (`POST /candidates/:id/offer/letter` → MinIO) → email penawaran + lampiran PDF ke kandidat → accept/decline
- `Hired` → **handoff** ke [[Microservices - Employee Service]] `POST /onboarding/register` (employee_id + temporary password)

### Notifikasi
- Internal (approval/jadwal/offer, inbox/FCM) + **kandidat via Email (Resend) ✅** — "lamaran diterima" saat input pelamar & "penawaran kerja" + PDF saat unggah offer letter; WhatsApp kandidat menyusul — lewat [[Microservices - Notification Service]] (`POST /email/send`)

## Model Data (`recruitment_db`)

> Detail field per collection ada di [[HRIS - Recruitment]] (hindari duplikasi).

- **Backbone internal:** `job_requisition` · `job_posting` · `candidate` (+`progress`/`status`) · `screening_result` · `interview` · `technical_test_result` · `psychotest` · `psychotest_result` · `background_check` · `offer`
- **Adopsi ERPGo (✅ Fase A–E):** `job_type` · `candidate_source` · `interview_type` · `job_location` · `custom_question` (master); `job_posting` & `candidate` diperkaya (lihat increment di bawah).

## Belum Diimplementasikan / Catatan

- **Seluruh service belum ada di kode** (🟡) — scaffolding mengikuti pola `services/.template`.
- `recruitment_db` (container Mongo) **akan didaftarkan** di [[DB - Overview and Notes]] saat implementasi; rute `/api/recruitment/*` ditambahkan ke [[CORE - API Master Gateway]] (`InternalURL`) saat itu juga.
- **AI CV screening** (LLM OpenRouter + OCR) & **psikotes online** (test-engine + bank soal) = **fase lanjut**.
- **Email kandidat** ✅ sudah di kode (best-effort via [[Microservices - Notification Service]] `POST /email/send`, Resend). **WhatsApp kandidat** masih menyusul.
- Relasi dengan **Glints** (impor/sinkron vs menggantikan) = TBD strategis.

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — master posisi/departemen (`PositionTitle*`), cek duplikasi, **handoff `/onboarding/register`** saat hire
- [[Microservices - File Service]] — CV/berkas pelamar, report PDF psikotes, surat penawaran (MinIO)
- [[Microservices - Notification Service]] — notifikasi internal (inbox/FCM) + **kandidat via Email/Resend** (`/email/send`, sudah dipakai) + WhatsApp (menyusul)
- [[CORE - OCR Document Service]] — OCR CV hasil scan (untuk AI screening fase lanjut)
- **LLM (OpenRouter)** — AI CV screening (fase lanjut); reuse infra Ideamills ([[Sales - Veo (Gemini) Implementation]])
- **Glints (TapLoker)** — ATS/job-portal eksternal, sumber pelamar utama
- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]] — routing + auth
- [[DB - Overview and Notes]] — pola database-per-service

## Implementasi (Fase 1-3 — ✅ SELESAI)

> Diimplementasi 2026-06-24 di branch `feat/recruitment-service` (7 slice, `go build`/`test`/`vet` hijau, di-push ke origin). **Live:** Job Requisition + approval (SPV→HR→Direktur/Secretary), Job Posting, Candidate + CV (MinIO), stage records (screening/interview/technical-test/background-check/psikotes), Offer + hire → `/onboarding/register`, audit log + notif inbox internal. **Belum (Fase 4-5):** AI CV screening, psikotes online, portal publik, WhatsApp, Glints sync, FE. Detail di bawah = yang dibangun.

**Git workflow:** di repo `bip-erp`, **branch dari `main`** (checkout `main` + `git pull` dulu — HEAD saat ini di `feat/sso-task-management`), buat branch baru **`feat/recruitment-service`** (konvensi repo `feat/<nama>`).

**Scope terkunci:** BE service **Fase 1-3** (Job Requisition+approval, Posting, Candidate+CV, Screening manual, Interview multi-tahap + Technical Test + Background Check, Psikotes manual, Offer, Onboarding handoff). **Email kandidat DITUNDA** (notif internal FCM/inbox saja). Approval pakai role yang ada: SPV ajukan → `hris` supervisor review → `hris` admin/Secretary (wakil direktur). **Fase 4-5 + FE = menyusul.**

**File baru** (`services/recruitment/`, pola `.template` + `task-management`): `main`/`go.mod`/`Dockerfile` · `identity`/`rbac` (role `hris`) · `db` · `models_{requisition,posting,candidate,stages,offer}` · `pipeline` (enum `progress`/`status` + `validTransition()` — inti TDD) · `{requisition,posting,candidate,stage,offer}_handlers` · `minio` · `onboarding` · `notify` · `audit` · `routes` · tests `{pipeline,rbac,requisition,offer}_test`.

**Wiring:** `shared-library/common/env.go` (+`RecruitmentModuleURL` / `"RECRUITMENT_MODULE_URL"`) · `api-gateway/main.go` (`InternalURL["recruitment"]`) · `docker-compose.yml` (service `recruitment-service` + `recruitment-mongo-db` + volume + env gateway) · `.env`/`.env.example` (`RECRUITMENT_SERVICE_PORT=6978`, `MONGO_RECRUITMENT_DB=recruitment_db`).

**Slices (commit per slice, TDD):** 1) scaffold + wiring + pipeline enums → 2) requisition + approval → 3) posting → 4) candidate + CV + advance → 5) stage records → 6) offer + hire→`/onboarding/register` → 7) notif internal + audit.

**Deviasi tercatat:** CV ke **MinIO langsung** (prefix `recruitment/`, pola task-management) bukan via File Service; **"Direktur" = `hris` admin/Secretary**; onboarding handoff hanya **mengaktifkan akun** (pembuatan data master karyawan = di luar MVP).

**Saat `/sync-docs` nanti:** status dok ini + [[HRIS - Recruitment]] → ⚠️/✅; daftarkan `recruitment_db` di [[DB - Overview and Notes]]; port di [[IT - Environment Inventory]]; tak ada cron/job (N/A di [[IT - Background Jobs & Schedulers]]).

## Increment: Notifikasi Email Kandidat (✅)

> Ditambah setelah Fase 1-3 (branch `feat/recruitment-service`, `go build`/`test`/`vet` hijau). Channel Email [[Microservices - Notification Service]] (Resend) kini dipakai recruitment, **best-effort** (gagal kirim ≠ gagalkan aksi inti).

- `candidate` + field **`email`** (opsional, divalidasi format); helper `notifyCandidateEmail` → `POST /email/send` (service-key + gateway key).
- **Lamaran diterima**: email otomatis saat `POST /candidates` (bila `email` terisi).
- **Penawaran kerja**: `POST /candidates/:id/offer/letter` — HR unggah offer letter PDF → MinIO (`recruitment/offer/<id>/`) → email penawaran + **lampiran PDF** ke kandidat; `offer.letter_object` menyimpan referensi.
- `idempotency_key` per event; `from` default `RESEND_FROM_EMAIL` (env Resend di-wire ke `docker-compose.yml` notification-service).

## Increment: Apply Publik Kandidat (✅)

> Ditambah setelah Fase 1-3 (branch `feat/recruitment-service`). Kandidat bisa **melamar sendiri** tanpa login, **selain** input oleh HR. Versi MVP dari "portal publik" (UI/form publik & captcha = fase lanjut).

- **Service:** `POST /apply` (tanpa JWT/RBAC; tetap di belakang gateway key). `email` **wajib**; `posting_id` opsional (bila diisi → lowongan harus **ada & Open**). Service yang mengontrol field internal (`status=Applied`, `progress=CV Screening`, dll) — kiriman klien untuk itu diabaikan. Sukses → email "lamaran diterima" + respons minimal (`candidate_id`).
- **Gateway:** `POST /public/recruitment/apply` (grup `/public`, **rate-limited**) → forward ke recruitment `/apply` — lihat [[CORE - API Master Gateway]].
- HR tetap pakai `POST /candidates` (JWT + role isHR). Keduanya menghasilkan record kandidat yang sama.

## Increment: Adopsi Struktur ERPGo (Data — Fase A–E ✅)

> Ditambah 2026-07-03 di branch `feat/recruitment-service` (6 commit, `go build`/`vet`/`test` hijau, auto-push). Mengadopsi struktur data modul Recruitment **ERPGo SaaS (WorkDo)** secara **hybrid**: backbone internal kita (requisition+approval, pipeline `Progress`/`Status`, stage records, offer, onboarding handoff) **dipertahankan**; entity front-of-funnel & form-builder ERPGo **ditambahkan**. Referensi antar-service = **string ID** (bukan objectId), tanpa tenant-scope (`created_by`=`employee_id` audit), uang `float64`.

**Master baru (role `isHR`):**
- `job_type` · `candidate_source` · `interview_type` — lookup identik (`Lookup`: name, description, is_active). Endpoint `/masters/{job-types,candidate-sources,interview-types}`.
- `job_location` — lokasi kerja (name, remote_work, address, city/state/country/postal_code [**string**, jaga leading zero], status). Endpoint `/locations`.
- `custom_question` — form builder aplikasi: question, `type` (Text/Textarea/Select/Radio/Checkbox/Date/Number), `options` (wajib utk tipe pilihan), is_required, is_active, sort_order. Endpoint `/questions`.

**`job_posting` diperkaya:** title, job_type_id, location_id, branch, job_application, career_portal_url, number_of_positions, priority (Low/Medium/High), min/max_experience, min/max_salary, application_deadline, is_featured, toggle `ask_gender`/`ask_date_of_birth`/`ask_country` & `show_profile_image`/`show_resume`/`show_cover_letter`, required_skills[], description/requirements/benefits/terms_condition (HTML), show_terms_on_form, `application_questions[]` (m2m ke `custom_question`). Keberadaan job_type/location/questions dicek saat create/update. Kontrak `PUT /postings/:id` = **full-replace** (kirim form lengkap).

**`candidate` diperkaya:** source_id, country, `custom_answers[]` (jawaban `application_questions`), profile_image_object & cover_letter_object (MinIO), + opsional expected/current_salary, notice_period, portfolio_url, linkedin_url, education. Validasi baru: pertanyaan **wajib** per-lowongan harus terjawab + field kondisional (`ask_*`) — diwire ke `POST /candidates` (HR) & `POST /apply` (publik).

**Deviasi tercatat vs skema ERPGo:** tanpa `created_by` tenant-scope; FK antar-service = string; funnel tetap enum `Progress`/`Status` (bukan `job_stages` master); `candidate_assessments` **di-skip** (sudah ada `technical_test_result`+`psychotest`).

**Increment lanjut (✅ gap A):** endpoint **upload/preview** `profile-image` & `cover-letter` kandidat (MinIO, pola CV) — menutup field yang tadinya yatim; **portal karir publik** `GET /public/postings` (daftar Open) & `GET /public/postings/:id` (detail + `application_questions` di-expand ke `custom_question` aktif) — dipublish gateway `/public/recruitment/postings*`, melengkapi `/apply` agar form publik bisa render pertanyaan. Detail endpoint: [[API - Recruitment Service]].

**Increment (✅ Fase F — interview rounds+feedback):** `interview_round` (per lowongan: name, sequence, status active/inactive — CRUD `/postings/:id/rounds` & `/rounds/:id`); `interview_feedback` (per sesi: rating 1-5 technical/communication/cultural_fit, `recommendation` Strong Hire..Strong No Hire, strengths/weaknesses/comments — `POST`/`GET /interviews/:id/feedback`); `interview` diperkaya (interview_type_id, interviewers[] employee_id, meeting_link, duration_minutes, scheduled_time). + backlog: `GET /:id` get-single master/location/question; `validateAgainstPosting` juga di `PUT /candidates/:id`.

**Increment (✅ tracking status lamaran):** `candidate.tracking_token` (crypto/rand 32-hex — **bukan `_id`** agar tak bisa dienumerasi) di-set saat create/apply; endpoint publik `GET /public/track/:token` (gateway `/public/recruitment/track/:token`) → tampilan **curated** (nama/posisi/tanggal + progress & status label ramah + stepper), tanpa skor/catatan internal. Email "lamaran diterima" +tombol **Lihat Status Lamaran** (base env `CAREER_PORTAL_URL`); respons `/apply` kembalikan `tracking_token` + `track_url`. Label penolakan dilembutkan ("Belum Sesuai") — apakah status ditampilkan ke kandidat = keputusan HRD terbuka ([[HRIS - Recruitment]]).

**Belum (menyusul, Fase G–I):** onboarding checklist; offer letter template; recruitment/career settings.

## Dokumen Terkait

- [[HRIS - Recruitment]] — konsep/bisnis & keputusan HRD (pasangan dok ini)
- [[Microservices - Employee Service]] · [[Microservices - Notification Service]] · [[Microservices - File Service]]
- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]]
