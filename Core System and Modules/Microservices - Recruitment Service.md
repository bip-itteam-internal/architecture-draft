## Deskripsi

*Recruitment Service mengelola **siklus depan karyawan**: permintaan posisi → lowongan → pelamar → screening → interview → background check → psikotes → offer → onboarding handoff. Ini sisi **implementasi** dari konsep/bisnis di [[HRIS - Recruitment]].*

- **Stack**: Go + Fiber v2 + MongoDB (`recruitment_db`) — selaras pola service bip-erp lain
- **Path**: `services/recruitment` (go.mod per-service; build/vet dari folder itu)
- **Status**: ⚠️ **Implemented (BE)** — Fase 1-3 + adopsi ERPGo (A–F) + portal publik (browse/apply/track), **sudah di `main`** & jalan di dev. Belum: AI CV screening, psikotes online, WhatsApp kandidat, Glints sync, FE internal (erp-frontend Candidate Pipeline berjalan terpisah). Di belakang [[CORE - API Master Gateway]], auth **SSO** ([[CORE - SSO Flow]]), role `system_roles["hris"]`. Port `6979`, mongo `recruitment-mongo-db`.
- **⚠️ Deploy MANUAL**: workflow "BIP ERP — Deploy to Dev" **disabled** → **merge ≠ deploy**. Deploy: SSH `erp@10.10.10.121:/home/erp/apps/bip-erp` → `git reset --hard origin/main` + `docker compose build/up -d recruitment-service`. Selalu **deploy BE sebelum FE/portal** untuk perubahan kontrak.
- **Konsumen publik**: [[APP - Portal Karir Bharata]] · **Endpoint lengkap**: [[API - Recruitment Service]]

## Endpoint / Fitur (Sudah Diimplementasikan)

> Daftar path/role lengkap ada di [[API - Recruitment Service]] (hindari duplikasi). Di bawah = cakupan per pipeline.

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
- `Hired` → **handoff** ke [[Microservices - Employee Service]] `POST /onboarding/register` (aktivasi akun; employee_id + temporary password)
- **Pembuatan data karyawan** dari kandidat Hired dilakukan di HRIS "Tambah Karyawan" (mode *dari kandidat*), lalu `PUT /candidates/:id/link-employee` menautkan kandidat ke `employee_id` (cegah konversi ganda) — lihat increment di bawah

### Notifikasi
- Internal (approval/jadwal/offer, inbox/FCM) + **kandidat via Email (Resend) ✅** — "lamaran diterima" saat input pelamar & "penawaran kerja" + PDF saat unggah offer letter; WhatsApp kandidat menyusul — lewat [[Microservices - Notification Service]] (`POST /email/send`)

## Model Data (`recruitment_db`)

> Detail field per collection ada di [[HRIS - Recruitment]] (hindari duplikasi).

- **Backbone internal:** `job_requisition` · `job_posting` · `candidate` (+`progress`/`status`) · `screening_result` · `interview` · `technical_test_result` · `psychotest` · `psychotest_result` · `background_check` · `offer`
- **Adopsi ERPGo (✅ Fase A–E):** `job_type` · `candidate_source` · `interview_type` · `job_location` (master) + `onboarding_checklist`/`checklist_item` (template); `job_posting` & `candidate` diperkaya (lihat increment di bawah). *(`custom_question` form-builder **dihapus** #486 — lihat catatan.)*

## Belum Diimplementasikan / Catatan

- `recruitment_db` (container Mongo) & rute `/api/recruitment/*` + `/public/recruitment/*` — lihat [[DB - Overview and Notes]] dan [[CORE - API Master Gateway]] (`InternalURL["recruitment"]`).
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
- `onboarding_checklist` + `checklist_item` — template checklist onboarding (task_name, category, assigned_to_role, due_day, is_required). Endpoint `/checklists` + `/checklists/:checklistId/items`. **Template saja** — instansiasi per-kandidat saat hire belum ada (TBD, lihat [[HRIS - Recruitment]]).

> **Custom Questions (form builder) dihapus** — BE #486 / FE #342 (2026-07-16). `custom_question` master (endpoint `/questions`) + field `application_questions` (`job_posting`) & `custom_answers` (`candidate`) **tak ada lagi** di kode; portal karir memakai field native `candidate`. BSON lama diabaikan saat decode (tanpa migrasi).

**`job_posting` diperkaya:** title, job_type_id, location_id, branch, job_application, career_portal_url, number_of_positions, priority (Low/Medium/High), min/max_experience, min/max_salary, application_deadline, is_featured, toggle `ask_gender`/`ask_date_of_birth` (~~`ask_country`~~ **dibuang PR #462**) & `show_profile_image`/`show_resume`/`show_cover_letter`, required_skills[], description/requirements/benefits/terms_condition (HTML), show_terms_on_form. Keberadaan job_type/location dicek saat create/update. Kontrak `PUT /postings/:id` = **full-replace** (kirim form lengkap). ⚠️ **Gotcha full-replace:** field yang tak dikirim tertulis kosong/false → FE (form Lowongan tak punya field `ask_*`/`show_*`/`terms`) **wajib round-trip** nilainya saat edit, kalau tidak konfigurasi portal terhapus senyap (diperbaiki di erp-frontend `buildPostingPayload`).

**`candidate` diperkaya:** source_id, country, profile_image_object & cover_letter_object (MinIO), + opsional expected/current_salary, notice_period, portfolio_url, linkedin_url, education. Validasi field kondisional (`ask_*`) diwire ke `POST /candidates` (HR) & `POST /apply` (publik).

**Deviasi tercatat vs skema ERPGo:** tanpa `created_by` tenant-scope; FK antar-service = string; funnel tetap enum `Progress`/`Status` (bukan `job_stages` master); `candidate_assessments` **di-skip** (sudah ada `technical_test_result`+`psychotest`).

**Increment lanjut (✅ gap A):** endpoint **upload/preview** `profile-image` & `cover-letter` kandidat (MinIO, pola CV) — menutup field yang tadinya yatim; **portal karir publik** `GET /public/postings` (daftar Open) & `GET /public/postings/:id` (detail) — dipublish gateway `/public/recruitment/postings*`, melengkapi `/apply`. Detail endpoint: [[API - Recruitment Service]].

**Increment (✅ Fase F — interview rounds+feedback):** `interview_round` (per lowongan: name, sequence, status active/inactive — CRUD `/postings/:id/rounds` & `/rounds/:id`); `interview_feedback` (per sesi: rating 1-5 technical/communication/cultural_fit, `recommendation` Strong Hire..Strong No Hire, strengths/weaknesses/comments — `POST`/`GET /interviews/:id/feedback`); `interview` diperkaya (interview_type_id, interviewers[] employee_id, meeting_link, duration_minutes, scheduled_time). + backlog: `GET /:id` get-single master/location/question; `validateAgainstPosting` juga di `PUT /candidates/:id`.

**Increment (✅ tracking status lamaran):** `candidate.tracking_token` (crypto/rand 32-hex — **bukan `_id`** agar tak bisa dienumerasi) di-set saat create/apply; endpoint publik `GET /public/track/:token` (gateway `/public/recruitment/track/:token`) → tampilan **curated** (nama/posisi/tanggal + progress & status label ramah + stepper), tanpa skor/catatan internal. Email "lamaran diterima" +tombol **Lihat Status Lamaran** (base env `CAREER_PORTAL_URL`); respons `/apply` kembalikan `tracking_token` + `track_url`. Label penolakan dilembutkan ("Belum Sesuai") — apakah status ditampilkan ke kandidat = keputusan HRD terbuka ([[HRIS - Recruitment]]).

**Belum (menyusul, Fase G–I):** onboarding checklist; offer letter template; recruitment/career settings.

## Increment: Penopang Portal Karir Publik (2026-07-16)

> 4 PR ke `main` sebagai BE untuk [[APP - Portal Karir Bharata]] (portal karir publik yang kini benar-benar ada UI-nya). `go build`/`vet`/`test` hijau. **✅ SEMUA sudah ter-deploy & terverifikasi live di dev (2026-07-16).**

- **Slug URL lowongan (PR #448 — ✅ live di dev):** `job_posting` + field `slug`, digenerate saat `POST /postings`: `slugify(title|posisi)` (lowercase, non-alfanumerik → `-`, trim) + `uniquePostingSlug` (bentrok → sufiks `-2`, `-3`, …; fallback `lowongan`). Diekspos di list & detail publik; `GET /public/postings/:id` **menerima slug ATAU ObjectID** (coba parse ObjectID dulu; gagal → lookup by `slug`) → URL portal `/lowongan/frontend-developer`, bukan ObjectID. Test: `TestSlugify`. **Posting lama (pra-#448) tak punya slug** → hanya bisa diakses via ObjectID.
- **Jenis pekerjaan dari master (PR #451 — ✅ deployed & live):** `toPublicPostingView` **resolve `job_type_id` → nama** dari master `job_types` (`Lookup.Name`) lalu mengisi `job_type` di respons publik. **Catatan proses:** PR #449 sempat menambah field plain `JobType` di `job_posting` — **menduplikasi master yang sudah ada** (System Setup → Jenis Pekerjaan) → **dikoreksi/dibatalkan** di #451. Aturan turunan: **cek master/struktur eksisting dulu sebelum menambah field baru**.
- **Upload berkas lamaran di apply publik (PR #452 — ✅ merged & ter-deploy):** `POST /apply` menerima **`multipart/form-data`** selain JSON — field `data` = JSON kandidat + file **`berkas`** = **PDF maks 10 MB** → MinIO `recruitment/cv/<candidate_id>/berkas.pdf` → set `cv_object`, sehingga HR memakai **endpoint lama** `GET /candidates/:id/cv/preview` (tanpa endpoint baru). Upload **best-effort setelah insert** (gagal upload ≠ gagal lamaran); body JSON tanpa file tetap diterima (**backward-compatible**); non-PDF / >10 MB → 400. Satu berkas gabungan (CV+ijazah+sertifikat) mengikuti kebiasaan Google Form HRD sebelumnya.
- **🟢 Gap gateway (ditemukan & DIPERBAIKI 2026-07-16):** multipart mula-mula **tidak bisa lewat gateway** — `routes.InternalRequest` (shared-library) **memaksa** `Content-Type: application/json` (`internal_request.go:29`), sehingga body multipart diteruskan tapi **kehilangan label + `boundary`** → recruitment jatuh ke `BodyParser` → `400 "body tidak valid"`. Diperbaiki **di gateway** (bukan shared-library yang dipakai semua service): route `/public/recruitment/apply` pakai `InternalRequestCustomHeader` + teruskan `Content-Type` asli (**PR #458**). Menyusul **PR #460** menambah origin portal (`career.bharatainternasional.com` + `:3011`) ke CORS allowlist gateway — tanpa itu lamaran dari browser 201 tapi respons diblokir CORS (halaman sukses tak muncul). **Butuh deploy `api-gateway`**, bukan cuma recruitment-service. **✅ Kedua PR deployed & terverifikasi (2026-07-16):** `data` rusak → `"data tidak valid"`; E2E multipart+berkas → `201` → `cv_object` → HR `cv/preview` mengembalikan **PDF valid**. Pelajaran: E2E apply dulu hanya diuji jalur **JSON**; jalur multipart tak pernah diuji **menembus gateway**.
- **Identitas pengirim email (PR #453 — ✅ merged):** `notifyCandidateEmail` mengisi `From` dari env **`RECRUITMENT_EMAIL_FROM`** (format RFC `Nama <email>`, mis. `Bharata Recruitment <noreply@bharatainternasional.com>`) agar inbox kandidat menampilkan nama pengirim, bukan sekadar "noreply". Env kosong → `From` kosong → notification-service fallback ke `RESEND_FROM_EMAIL` (perilaku lama, backward-compatible). **Jangan** ubah `RESEND_FROM_EMAIL` global jadi nama recruitment — itu default **semua** service (email payroll nanti ikut salah nama); pola per-service dijelaskan di [[Microservices - Notification Service]]. Deploy **wajib set env `RECRUITMENT_EMAIL_FROM`** (alamat harus domain terverifikasi Resend).

**Field lamaran publik = model `candidate` yang sudah ada** (nama_lengkap, email, no_hp, jenis_kelamin, tanggal_lahir, alamat, pendidikan, ipk, pengalaman, expected_salary, dll). `tanggal_lahir` memakai **RFC3339 selaras model employee** dan nilai `jenis_kelamin` ("Laki-laki"/"Perempuan") **sudah identik** employee → dipakai untuk prefill saat konversi ke karyawan (lihat increment hire→karyawan di bawah).

**Email kandidat ✅ terverifikasi live** di dev (2026-07-16): "Lamaran Anda Telah Kami Terima" sampai ke inbox pelamar — menutup TODO smoke test di [[Microservices - Notification Service]].

## Increment: Requisition se-departemen + pengetatan (2026-07-16, ✅ deployed)

> 3 PR ke `main` seiring menu **Job Requisitions** di [[APP - Web ERP]] grup "Portal Saya" (sisi atasan/SPV). `go build`/`vet`/`test` hijau, ter-deploy & **terverifikasi live**.

- **Requisition se-departemen (PR #470):** `GET /requisitions?scope=department` → SPV melihat requisition **milik departemennya**, bukan hanya pengajuannya sendiri. Departemen diambil dari **identitas gateway**, bukan query (tak bisa dipakai mengintip departemen lain); butuh `isSupervisor`/`isHR`; departemen kosong → 400. Tanpa `scope` = perilaku lama (HR semua / pengaju sendiri). `GET /requisitions/:id` juga membolehkan SPV se-departemen (`isDepartmentSupervisorOf`) — **wajib berpasangan**, kalau tidak daftar bisa dilihat tapi tiap baris 403 saat diklik. Terverifikasi: Seno (Human Resource) kini hanya lihat 1 departemen (dulu 8).
- **Departemen ditentukan server, bukan body (PR #478):** `createRequisition` mengambil `department` dari **identitas pengaju** (bukan body) via `departmentForNewRequisition`; `updateRequisition` mempertahankan departemen (edit tak memindahkan requisition). Melengkapi #470 agar visibilitas se-departemen tak bisa disiasati. Terverifikasi: body `department:"Finance"` tersimpan sebagai "Human Resource" (departemen pengaju). **Catatan penting:** `isSupervisor` bersumber `system_roles` = hak akses **modul**, bukan hierarki organisasi — cukup untuk visibilitas daftar, **bukan** gerbang approval (approval tetap `isHRSupervisor`/`isApprover`).
- **Buang `AskCountry` (PR #462):** flag `ask_country` di `job_posting` + validasinya dihapus — jadi jebakan setelah field Negara dihapus dari form kandidat (pasar dalam negeri; BE menolak "country wajib" padahal UI tak punya field-nya). `Candidate.Country` dipertahankan (data lama). Respons publik tak lagi memuat `ask_country`. Terverifikasi hilang dari respons.

**FE terkait (erp-frontend, semua merged):** badge **Tahap kandidat bisa diubah dari tabel** (reuse `InlineSelectBadge` diekstrak dari Support Ticket); menu **Job Requisitions** di "Portal Saya" (SPV-only) + halaman `/portal/requisitions` (`scope=department`, tombol Buat Pengajuan pindah ke sini, departemen **terkunci** ke pengaju); filter Departemen/Jenis + search + pagination di tabel requisition (+ perbaikan `FilterTable` crash `SelectItem value=""` yang berdampak **semua** halaman ber-filter); **buka detail dengan klik baris** (buang kolom Aksi ikon-mata) di semua tabel Recruitment; **fix data-loss edit lowongan** (`PUT /postings/:id` full-replace → FE round-trip `terms`/`ask_*`/`show_*` agar tak terhapus senyap); **fix key i18n mentah** (lookup System Setup + detail requisition).

## Increment: Konversi Kandidat → Karyawan (hire→employee, 2026-07-16)

> BE **PR #490** (bip-erp) + FE **PR #344** (erp-frontend), keduanya **merged** ke `main`. `go build`/`vet`/`test` hijau. ⚠️ **Belum ter-deploy** (deploy manual — BE dulu baru FE).

Menutup TBD lama "mapping hire → data karyawan". Pembuatan **data master karyawan** tetap di HRIS (bukan di recruitment) — recruitment hanya menyediakan **data kandidat** + **tautan** agar tak ada konversi ganda.

- **BE (#490):** `candidate` + field **`employee_id`** (omitempty). Endpoint baru `PUT /candidates/:id/link-employee` (isHR): wajib kandidat **Hired** & **belum tertaut** → set `employee_id`, `progress`→**Onboarding**, tulis audit. `updateCandidate` mempertahankan `employee_id`. Tak ada auto-generate employee_id (dibuat HRIS).
- **FE (#344, erp-frontend):** HRIS "Tambah Karyawan" kini bermula dari **modal 2 opsi** — *isi manual* (perilaku lama) atau *dari kandidat rekrutmen*. Mode dari-kandidat: picker kandidat **Hired belum tertaut** (`GET /candidates?status=Hired`, filter `!employee_id`) → wizard memprefill data kandidat (nama, jenis_kelamin, tanggal_lahir, email, no_hp, alamat), **menyembunyikannya** (kartu ringkasan read-only) & hanya menampilkan **sisa** field yang HR isi. Field wajib yang **kosong** di kandidat tetap tampil (email/alamat/tgl lahir opsional). Karyawan dibuat via `POST /api/hris/employees/multi` ([[Microservices - Employee Service]]), lalu `link-employee` dipanggil (best-effort) agar kandidat drop dari picker.
- **Alur:** kandidat harus lebih dulu `Hired` (offer → accept → hire) baru muncul di picker. Onboarding checklist per-kandidat = **masih TBD** (lihat Fase G–I).

## Dokumen Terkait

- [[HRIS - Recruitment]] — konsep/bisnis & keputusan HRD (pasangan dok ini)
- [[API - Recruitment Service]] — daftar endpoint lengkap
- [[APP - Portal Karir Bharata]] — portal karir publik (konsumen `/public/recruitment/*`)
- [[Microservices - Employee Service]] · [[Microservices - Notification Service]] · [[Microservices - File Service]]
- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]]
