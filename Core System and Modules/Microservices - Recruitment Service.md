## Deskripsi

*Recruitment Service mengelola **siklus depan karyawan**: permintaan posisi → lowongan → pelamar → screening → interview → background check → psikotes → offer → onboarding handoff. Ini sisi **implementasi** dari konsep/bisnis di [[HRIS - Recruitment]].*

- **Stack**: Go + Fiber v2 + MongoDB (`recruitment_db`) — selaras pola service bip-erp lain
- **Path**: `services/recruitment` (go.mod per-service; build/vet dari folder itu)
- **Status**: ⚠️ **Implemented (BE)** — Fase 1-3 + adopsi ERPGo (A–F) + portal publik (browse/apply/track), **sudah di `main`** & jalan di dev. Belum: AI CV screening, psikotes online, WhatsApp kandidat, Glints sync, FE internal (erp-frontend Candidate Pipeline berjalan terpisah). Di belakang [[CORE - API Master Gateway]], auth **SSO** ([[CORE - SSO Flow]]), role `system_roles["hris"]`. Port `6979`, mongo `recruitment-mongo-db`. · ✅ **Multi-perusahaan: ter-scope** (bip-erp [#1853](https://github.com/bip-itteam-internal/bip-erp/pull/1853), merged dan live prod 2026-09-12): enam koleksi proses diberi `company_id` (backfill prod mengisi BIP ke 30 dokumen lama), ditambah `GET /companies` dan `?company=`. Portal karir publik (`/public/postings`, `/apply`) tetap satu untuk semua tenant; perusahaan kandidat diturunkan dari lowongan. Paket izin belum dipasang di prod (per 2026-09-12). Lihat bagian **Increment: Rekrutmen Lintas Perusahaan** di bawah dan [[ADR - 0092 Rekrutmen Lintas Perusahaan lewat Paket Izin]]. Fase lanjut yang lebih tua: [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]].
- **⚠️ Deploy MANUAL**: workflow "BIP ERP — Deploy to Dev" **disabled** → **merge ≠ deploy**. Deploy: SSH `erp@10.10.10.121:/home/erp/apps/bip-erp` → `git reset --hard origin/main` + `docker compose build/up -d recruitment-service`. Selalu **deploy BE sebelum FE/portal** untuk perubahan kontrak.
- **Konsumen publik**: [[APP - Portal Karir Bharata]] · **Endpoint lengkap**: [[API - Recruitment Service]]

## Endpoint / Fitur (Sudah Diimplementasikan)

> Daftar path/role lengkap ada di [[API - Recruitment Service]] (hindari duplikasi). Di bawah = cakupan per pipeline.

### Job Requisition
- Ajukan permintaan posisi (Form Permintaan Karyawan) + usulan kualifikasi
- Alur approval: **SPV HRD review kualifikasi lalu menyetujui** → `Approved` (tanpa cek kuota). Satu tahap, `isHRSupervisor` (role supervisor/admin modul `hris`) adalah pemberi persetujuan **final** — lihat perubahan 2026-07-22 di bawah
- **Tahap Direktur dihapus** (PR #609/#466, 2026-07-22). Status `HR Reviewed` masih ada di enum tapi **tidak diproduksi lagi**; dipertahankan supaya requisition lama yang terlanjur menggantung di status itu tetap bisa diselesaikan SPV HRD lewat endpoint yang sama. Field `director_approver`/`director_approver_name`/`director_note` disimpan sebagai **riwayat** persetujuan lama, tak diisi lagi, tanpa migrasi MongoDB
- Alasan penolakan kini ditulis ke `hr_reviewer`/`hr_note` (dulu `director_note`), karena SPV HRD yang menolak

### Job Posting & Sourcing
- Buka/tutup lowongan; catat sumber pelamar (utama: **Glints/TapLoker**, referral, walk-in, bootcamp)
- **Tanpa rentang gaji.** Field `min_salary`/`max_salary` dihapus dari model, DTO publik, dan UI (PR #608/#465/career-bharata #2, 2026-07-22) — lowongan tidak menampilkan kisaran gaji ke pelamar. Data lama di dokumen `job_postings` dibiarkan jadi field yatim (tanpa migrasi). Tidak menyentuh `expected_salary`/`current_salary` kandidat maupun `gaji_pokok` offer

### Candidate Management
- CRUD pelamar + pelacakan `progress` (tahap) & `status` (keadaan) — enum mengikuti rekaman HRD
- Field `email` kandidat (opsional internal; **wajib saat apply publik**) untuk notifikasi email
- **Dua jalur input:** HR (`POST /candidates`, JWT + role isHR) **atau** kandidat sendiri (apply publik, tanpa JWT — lihat increment di bawah)
- Upload CV/berkas/portofolio → [[Microservices - File Service]] (MinIO)

### Babak Seleksi: Interview · Tes (Psikotest/Technical Test) · Background Check

> ⚠️ Diverifikasi ulang ke kode 2026-09-10. Bentuk lama (`screening_result`, `technical_test_result`, `psychotest`, `psychotest_result` sebagai koleksi + endpoint per-tahap) **sudah tidak ada**; jangan pakai daftar itu sebagai acuan.

- Screening **manual** (HR putuskan lanjut/reject); AI CV screening = fase lanjut
- **Babak = katalog GLOBAL** `interview_round`, CRUD `/masters/interview-rounds` (bukan lagi config per-lowongan). Di-seed 7 babak baku saat startup, **idempoten lewat `$setOnInsert`** sehingga perubahan HR (nama/urutan/status) tak pernah ketimpa: CV Screening → HR Interview → **Psikotest** → User Interview → **Technical Test** → Final Interview → Background Check (`seed.go`). Lowongan memilih babak mana yang dipakai lewat `round_ids[]`
- **`form_type` menentukan bentuk form penilaian** yang dirender FE. Lima nilai: `generic` · `hrd_interview` · `user_interview` · `background_check` · `test` (kosong = `generic`, fallback aman untuk babak lama; `models_interview_ext.go`). Ini yang memisahkan babak yang **dijadwalkan** (interview) dari babak yang **hanya dicatat hasilnya** (tes, BGC) — FE menyaring by `form_type`, bukan by nama babak, jadi babak tes baru yang dibuat HR langsung ikut terbawa
- **Hasil tes** babak ber-`form_type: "test"` (baku: **Psikotest** & **Technical Test**) direkam per kandidat: `POST /candidates/:id/test-result`, **upsert per (`candidate_id`, `round_id`)**, isi `score` (opsional) + `result` (**Pass/Fail/Pending**) + `notes`. `round_id` yang bukan babak tes ditolak `400`. **Tanpa lampiran** — tak ada tempat menyimpan report PDF. ⚠️ `score` yang tidak dikirim ditulis `null`, menimpa skor otomatis psikotes (task T0b; lihat [[HRIS - Psikotes Kraepelin]])
- **Hasil menggerakkan pipeline (SP-Wiring).** Menyimpan hasil memindahkan `progress` kandidat ke babak itu (`setProgressToBabak`, `progress_move.go`) lalu menderivasi status: **Pass → `Pending`**, **Fail & Pending → `Hold`** (`wiring.go`). Terminal `Rejected` tetap aksi HR. Guard: tak menggerakkan kandidat yang sudah terminal atau sudah di `Offering`/`Onboarding`. Best-effort — gagal menggerakkan status **tidak** menggagalkan penyimpanan hasil
- **Background Check** punya form terstruktur sendiri (`verifications[]`, `reference`, `slik`, `decision`, `hr_note`) via `POST /candidates/:id/background-check`, pola wiring sama
- ✅ **Psikotes ONLINE sudah dibangun** (Kraepelin): HR menerbitkan sesi, kandidat mengerjakan sendiri lewat magic link tanpa login, server menilai, hasilnya **di-upsert ke `candidate_test_result`** babak Psikotest dengan `result: Pending` — HR tetap yang memutuskan Pass/Fail. 12 berkas Go (`models_psikotes.go`, `psikotes_public_handlers.go`, `psikotes_hr_handlers.go`, `psikotes_selesai.go`, `psikotes_token.go`, `psikotes_index.go`, `psikotes_notify.go` + `kraepelin_*`). Rincian lengkap: **[[HRIS - Psikotes Kraepelin]]**
	- ⚠️ Upsert itu **tidak** lewat handler `/test-result`, jadi SP-Wiring dan perpindahan `progress` **tidak** ikut jalan untuk hasil psikotes online. 🟡 **(bip-erp `feat/recruitment-alur-kerja-hr`, belum merge)** yang berubah hanya saat MENERBITKAN: `terbitkanPsikotes` dan `terbitkanUlangPsikotes` (`psikotes_hr_handlers.go`) kini memanggil `setProgressToBabak` sesudah sesi tersimpan, sehingga kandidat yang dikirimi tes berada di babak Psikotest walau HR mengirimnya dari tab Hasil Tes; status tidak disentuh dan guard terminal/`Offering`/`Onboarding` tetap berlaku. Hasil skor otomatis tetap tanpa SP-Wiring
	- ✅ **(T0a, bip-erp #1832, merged 2026-09-11 `4ef28e21`; dev terverifikasi hari itu, naik di prod 2026-09-11)** `GET /candidates/psikotes/status`, `/candidates/:id/psikotes/report`, dan `/candidates/:id/test-results` dikeluarkan dari cache gateway 3 menit karena datanya ditulis di luar gateway. Path ketiganya disalin ke `noCacheRoutes` api-gateway dan dijaga `rute_gateway_nocache_test.go`: rename di sini tanpa menyunting `api-gateway/redis.go` membuat test itu merah. Lihat [[CORE - API Master Gateway]]

### Offer & Onboarding
- Terbitkan offer (`POST /candidates/:id/offer`) → unggah surat penawaran PDF (`POST /candidates/:id/offer/letter` → MinIO) → email penawaran + lampiran PDF ke kandidat → accept/decline
- `Hired` → handoff ke [[Microservices - Employee Service]] `POST /onboarding/register` **hanya bila body hire membawa `employee_id`** (`offer_handlers.go` `hireCandidate`; tanpa itu balasan `onboarding.performed: false`). ⚠️ **Jalur itu tak pernah bisa berhasil** (diukur 2026-09-12): hire hanya meneruskan `employee_id` + `temporary_password`, sedangkan `/onboarding/register` mewajibkan juga `NewUsername`, `NewPassword`, dan `NewPIN` (`services/employee/main.go:3133`), jadi selalu `400` dan hire ikut gagal. Akun sesungguhnya diaktifkan karyawan sendiri di [[APP - MyBharata]]. 🟡 **(erp-frontend `feat/rekrutmen-buka-alur`, belum merge)** dialog Hire mengirim body kosong, jadi handoff tak lagi dipanggil; BE tidak diubah
- **Pembuatan data karyawan** dari kandidat Hired dilakukan di HRIS "Tambah Karyawan" (mode *dari kandidat*), lalu `PUT /candidates/:id/link-employee` menautkan kandidat ke `employee_id` (cegah konversi ganda) — lihat increment di bawah
- **Menu Offers** (`offer_menu_handlers.go`): Draft → approve → send → Sent → negotiate/accept/decline. `POST /offers/:id/send` memindah progress kandidat ke `Offering` dan mengirim email penawaran (best-effort). 🟡 **(bip-erp `feat/recruitment-alur-kerja-hr`, belum merge)** `GET /offers` mengirim **`can_approve`** per offer, dihitung dari gerbang yang SAMA dengan rute `POST /offers/:id/approve`: pasangan `izinSetujuiOffer` + `fallbackSetujuiOffer` (`offer_setujui.go`) dipakai `routes.go` dan `bolehSetujuiOffer`, dan `lolosGerbang` (`permission_gate.go`) adalah keputusan `gate` sebagai nilai. Nilainya milik pemanggil (sama untuk seluruh daftar) dan sengaja tanpa `omitempty` supaya FE membedakan `false` dari backend lama. Dikunci `offer_setujui_test.go`, yang membandingkan flag dengan hasil gerbang rute sungguhan lewat Fiber

### Notifikasi
- Internal (approval/jadwal/offer, inbox/FCM) + **kandidat via Email (Resend) ✅** — "lamaran diterima" saat input pelamar & "penawaran kerja" + PDF saat unggah offer letter; WhatsApp kandidat menyusul — lewat [[Microservices - Notification Service]] (`POST /email/send`)
- **Interview (✅ #536/#381):** saat `recordInterview`, **kandidat** dapat email jadwal (semua stage, tanpa link) & **pewawancara** stage **User/Final** dapat email undangan + **link form feedback** (login-gated) — lihat increment di bawah

## Model Data (`recruitment_db`)

> Detail field per collection ada di [[HRIS - Recruitment]] (hindari duplikasi).

- **Backbone internal:** `job_requisition` · `job_posting` · `candidate` (+`progress`/`status`) · `interview` · `interview_round` (katalog babak **global**) · `interview_feedback` · `candidate_test_result` · **`psikotes_session`** · `background_check` · `offer` · katalog psikotes `psikotes_tipe`, `psikotes_item`, `psikotes_paket`, `psikotes_seed` (2026-09-11, bip-erp #1837; [[HRIS - Bank Soal dan Paket Psikotes]])
	- ⚠️ **Koleksi yang pernah didokumentasikan tapi TIDAK ada di kode:** `screening_result`, `technical_test_result`, `psychotest`, `psychotest_result` — dibuang saat redesign pipeline 2026-07-18 ([[HRIS - Recruitment Pipeline Redesign]]). `background_check` kemudian lahir kembali sebagai model tersendiri (`models_background_check.go`), bukan struct stage lama. `models_stages.go` kini hanya menyisakan `Interview` + `InterviewPanelist`
- **Adopsi ERPGo (✅ Fase A–E):** `job_type` · `candidate_source` · `interview_type` · `job_location` (master); `job_posting` & `candidate` diperkaya (lihat increment di bawah). *(`custom_question` form-builder **dihapus** #486; `onboarding_checklist`/`checklist_item` per-kandidat lama **dihapus** 2026-07-18.)*
- **Onboarding Checklist (✅ dibangun ulang 2026-07-26):** `onboarding_template` (master) + `onboarding_instance` (per karyawan baru, `tasks[]` snapshot) — model BARU dengan penugasan PIC lintas-tim + notif, menggantikan versi lama yang dibuang. Lihat increment di bawah.
- **Hasil Tes per-babak (✅ menggantikan Candidate Assessment):** `candidate_test_result` — satu hasil per (`candidate_id`, `round_id`): `score` opsional, `result` Pass/Fail/Pending, `notes`, `assessed_by`, timestamps. **Menggerakkan progress + status** kandidat, berbeda dari `candidate_assessment` lama yang sengaja tidak.
	- Koleksi lama **`candidate_assessment` dipertahankan HANYA untuk migrasi** (`migrate_test_result.go`, idempoten saat startup): tipe assessment lama dipetakan ke nama babak lewat heuristik nama — mengandung "psiko" → **Psikotest**, selain itu → **Technical Test**. Handler CRUD-nya sudah dihapus; struct-nya masih ada semata sebagai bentuk baca data lama.
	- ⚠️ **Utang yang belum dibereskan:** master `assessment_type` (`/masters/assessment-types`) masih hidup dan form Lowongan di erp-frontend masih **mewajibkan minimal satu** `assessment_type_ids`, padahal pilihan itu tak lagi menentukan apa pun pada pencatatan hasil (yang menentukan `form_type` babak). Master ini tak punya seed, jadi isinya murni apa yang pernah diketik HR. 🟡 **(erp-frontend `feat/rekrutmen-buka-alur`, belum merge) sisi form dibereskan**: isian itu dan tab Tipe Asesmen di Pengaturan > Rekrutmen dibuang, dan `assessment_type_ids` lama di-round-trip saat edit lowongan (PUT full-replace) supaya tak terhapus. Endpoint master dan field di `job_posting` sengaja dibiarkan di backend (keputusan 2026-09-11), jadi yang tersisa tinggal data lama dan endpoint tanpa pemakai.

## Belum Diimplementasikan / Catatan

- `recruitment_db` (container Mongo) & rute `/api/recruitment/*` + `/public/recruitment/*` — lihat [[DB - Overview and Notes]] dan [[CORE - API Master Gateway]] (`InternalURL["recruitment"]`).
- **AI CV screening** (LLM OpenRouter + OCR) = **fase lanjut**. *(**Psikotes online BUKAN lagi fase lanjut** — sudah dibangun, lihat [[HRIS - Psikotes Kraepelin]]. CFIT dan DISC dikodekan 2026-09-11 lewat katalog dan paket (merged #1837, belum prod): [[HRIS - Bank Soal dan Paket Psikotes]].)*
- **Report PDF psikotes belum ada tempatnya.** Laporan psikotes tampil di layar HR, tapi tak ada lampiran tersimpan: `candidate_test_result` tak punya field lampiran dan `background_check` juga tidak. Desain lama "report PDF di MinIO" ([[HRIS - Recruitment]]) belum terealisasi. ⚠️ Kunci i18n untuk layar unggah report (`stageReportTitle`/`stageReportUpload` "Report Psikotes", `stagePsychotest`, `stageTestType`, `stageMode`, `stageScores`, `stageInterpretation`) **masih ada di `id.ts`/`en.ts` erp-frontend tapi tak dipakai satu berkas pun** — diverifikasi ke `origin/main` 2026-09-10. Membaca locale saja bisa membuat orang menyimpulkan fiturnya sudah jalan. ⚠️ Kunci i18n untuk layarnya (`stageReportTitle`/`stageReportUpload` "Report Psikotes", `stagePsychotest`, `stageTestType`, `stageMode`, `stageScores`, `stageInterpretation`) **masih ada di `id.ts`/`en.ts` erp-frontend tapi tak dipakai satu berkas pun** — membaca locale saja bisa membuat orang menyimpulkan fiturnya sudah jalan.
- **Email kandidat** ✅ sudah di kode (best-effort via [[Microservices - Notification Service]] `POST /email/send`, Resend). **WhatsApp kandidat** masih menyusul.
- Relasi dengan **Glints** (impor/sinkron vs menggantikan) = TBD strategis.

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — master posisi/departemen (`PositionTitle*`), cek duplikasi, **handoff `/onboarding/register`** saat hire. **(2026-09-11, live prod 2026-09-12)** + master `company` (`GET /master/companies`, dicache) untuk nama & validasi perusahaan tujuan, dan `/internal/mpp-vacancies` kini membawa `company_id`; lihat Increment **Rekrutmen Lintas Perusahaan** di bawah
- [[Microservices - File Service]] — CV/berkas pelamar, report PDF psikotes, surat penawaran (MinIO)
- [[Microservices - Notification Service]] — notifikasi internal (inbox/FCM) + **kandidat & pewawancara (interview User/Final) via Email/Resend** (`/email/send`, sudah dipakai) + WhatsApp (menyusul)
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

**Deviasi tercatat:** CV ke **MinIO langsung** (prefix `recruitment/`, pola task-management) bukan via File Service; **"Direktur" = `hris` admin/Secretary** (*tahap ini dihapus 2026-07-22 — lihat Job Requisition di atas*); onboarding handoff hanya **mengaktifkan akun** (pembuatan data master karyawan = di luar MVP).

**Saat `/sync-docs` nanti:** status dok ini + [[HRIS - Recruitment]] → ⚠️/✅; daftarkan `recruitment_db` di [[DB - Overview and Notes]]; port di [[IT - Environment Inventory]]; tak ada cron/job (N/A di [[IT - Background Jobs & Schedulers]]).

## Increment: Notifikasi Email Kandidat (✅)

> Ditambah setelah Fase 1-3 (branch `feat/recruitment-service`, `go build`/`test`/`vet` hijau). Channel Email [[Microservices - Notification Service]] (Resend) kini dipakai recruitment, **best-effort** (gagal kirim ≠ gagalkan aksi inti).

- `candidate` + field **`email`** (opsional, divalidasi format); helper `notifyCandidateEmail` → `POST /email/send` (service-key + gateway key).
- **Lamaran diterima**: email otomatis saat `POST /candidates` (bila `email` terisi).
- **Penawaran kerja**: `POST /candidates/:id/offer/letter` — HR unggah offer letter PDF → MinIO (`recruitment/offer/<id>/`) → email penawaran + **lampiran PDF** ke kandidat; `offer.letter_object` menyimpan referensi.
- `idempotency_key` per event; `from` default `RESEND_FROM_EMAIL` (env Resend di-wire ke `docker-compose.yml` notification-service).

## Increment: Apply Publik Kandidat (✅)

> Ditambah setelah Fase 1-3 (branch `feat/recruitment-service`). Kandidat bisa **melamar sendiri** tanpa login, **selain** input oleh HR. Versi MVP dari "portal publik" (UI/form publik & captcha = fase lanjut).

- **Service:** `POST /apply` (tanpa JWT/RBAC; tetap di belakang gateway key). `email` **wajib**; `posting_id` **awalnya opsional** (bila diisi → lowongan harus **ada & Open**). ⚠️ **(live prod 2026-09-12, bip-erp #1853)** `posting_id` **kini WAJIB** (dulu opsional): kandidat publik perlu diturunkan perusahaannya dari lowongan, jadi tanpa lowongan tak ada perusahaan tujuan yang jelas. Detail kode error lengkap: [[API - Recruitment Service]] bagian Publik. Service yang mengontrol field internal (`status=Applied`, `progress=CV Screening`, dll), kiriman klien untuk itu diabaikan. Sukses → email "lamaran diterima" + respons minimal (`candidate_id`).
- **Gateway:** `POST /public/recruitment/apply` (grup `/public`, **rate-limited**) → forward ke recruitment `/apply` — lihat [[CORE - API Master Gateway]].
- HR tetap pakai `POST /candidates` (JWT + role isHR). Keduanya menghasilkan record kandidat yang sama.

## Increment: Adopsi Struktur ERPGo (Data — Fase A–E ✅)

> Ditambah 2026-07-03 di branch `feat/recruitment-service` (6 commit, `go build`/`vet`/`test` hijau, auto-push). Mengadopsi struktur data modul Recruitment **ERPGo SaaS (WorkDo)** secara **hybrid**: backbone internal kita (requisition+approval, pipeline `Progress`/`Status`, stage records, offer, onboarding handoff) **dipertahankan**; entity front-of-funnel & form-builder ERPGo **ditambahkan**. Referensi antar-service = **string ID** (bukan objectId), tanpa tenant-scope (`created_by`=`employee_id` audit), uang `float64`.

**Master baru (role `isHR`):**
- `job_type` · `candidate_source` · `interview_type` — lookup identik (`Lookup`: name, description, is_active). Endpoint `/masters/{job-types,candidate-sources,interview-types}`.
- `job_location` — lokasi kerja (name, remote_work, address, city/state/country/postal_code [**string**, jaga leading zero], status). Endpoint `/locations`.
> **Custom Questions (form builder) dihapus** — BE #486 / FE #342 (2026-07-16). `custom_question` master (endpoint `/questions`) + field `application_questions` (`job_posting`) & `custom_answers` (`candidate`) **tak ada lagi** di kode; portal karir memakai field native `candidate`. BSON lama diabaikan saat decode (tanpa migrasi).

> **Onboarding checklist dihapus** — BE `chore/remove-onboarding-checklist` / FE erp-frontend (2026-07-18). Master `onboarding_checklist`/`checklist_item` (endpoint `/checklists*`) **dan** instansiasi per-kandidat `onboarding_progress` (`/candidates/:id/onboarding*`) **tak ada lagi** di kode: komponen FE-nya (`ChecklistsPage`, kartu `OnboardingSection`) **yatim/tak pernah dirender** sejak dibangun (#492/#346) — dead code. Data Mongo lama dibiarkan (tak dipakai). **Dipertahankan:** stage pipeline `Onboarding`, hire handoff `/onboarding/register`, `link-employee`, dan Performance Review Onboarding.

**`job_posting` diperkaya:** title, job_type_id, location_id, branch, job_application, career_portal_url, number_of_positions, priority (Low/Medium/High), min/max_experience, min/max_salary, application_deadline, is_featured, `show_profile_image`/`show_resume`/`show_cover_letter`, required_skills[], description/requirements/benefits/terms_condition (HTML), show_terms_on_form. Keberadaan job_type/location dicek saat create/update. Kontrak `PUT /postings/:id` = **full-replace** (kirim form lengkap). ⚠️ **Gotcha full-replace:** field yang tak dikirim tertulis kosong/false → FE (form Lowongan tak punya field `show_*`/`terms`) **wajib round-trip** nilainya saat edit, kalau tidak konfigurasi portal terhapus senyap (diperbaiki di erp-frontend `buildPostingPayload`).

**`candidate` diperkaya:** source_id, country, profile_image_object & cover_letter_object (MinIO), + opsional expected/current_salary, notice_period, portfolio_url, linkedin_url, education. **`jenis_kelamin` & `tanggal_lahir` SELALU wajib** untuk pelamar (`validateCandidate`, berlaku HR-input & apply publik) — lihat catatan penghapusan `ask_*` di bawah.

> **Toggle `ask_gender`/`ask_date_of_birth` DIBUANG** — BE #503 / FE #358 (2026-07-17). Jenis kelamin & tanggal lahir bukan lagi opsional per-lowongan; keduanya **selalu wajib** untuk pelamar. `validateAgainstPosting` + field `AskGender`/`AskDateOfBirth` (`job_posting`) dihapus; portal karir memang sudah selalu memintanya. BSON lama ber-`ask_*` diabaikan saat decode (`ask_country` sudah dibuang lebih dulu, #462).

**Deviasi tercatat vs skema ERPGo:** tanpa `created_by` tenant-scope; FK antar-service = string; funnel tetap enum `Progress`/`Status` (bukan `job_stages` master). *(Catatan `candidate_assessments`: sempat dibangun sebagai koleksi `candidate_assessment` + menu FE "Candidate Assessment", lalu **dibongkar lagi** — dikonsolidasi ke `candidate_test_result` per babak. Menu/rute FE `hris/recruitment/assessments` sudah tidak ada; lihat Model Data di atas.)*

**Increment lanjut (✅ gap A):** endpoint **upload/preview** `profile-image` & `cover-letter` kandidat (MinIO, pola CV) — menutup field yang tadinya yatim; **portal karir publik** `GET /public/postings` (daftar Open) & `GET /public/postings/:id` (detail) — dipublish gateway `/public/recruitment/postings*`, melengkapi `/apply`. Detail endpoint: [[API - Recruitment Service]].

**Increment (✅ Fase F — interview rounds+feedback):** `interview_round` (saat itu **per lowongan**: name, sequence, status active/inactive — CRUD `/postings/:id/rounds` & `/rounds/:id`; ⚠️ **sudah digantikan katalog GLOBAL** `/masters/interview-rounds` + `form_type`, lihat bagian Babak Seleksi di atas); `interview_feedback` (per sesi: rating 1-5 technical/communication/cultural_fit, `recommendation` Strong Hire..Strong No Hire, strengths/weaknesses/comments — `POST`/`GET /interviews/:id/feedback`); `interview` diperkaya (interview_type_id, interviewers[] employee_id, meeting_link, duration_minutes, scheduled_time). + backlog: `GET /:id` get-single master/location.

**Increment (⛔ tracking status lamaran — DIBANGUN LALU DIHAPUS):** dicabut di `a298ba70` *"feat(recruitment): hapus fitur tracking (lacak lamaran) kandidat"* (2026-07-24, sudah di `origin/main`). Per 2026-09-10 `tracking_token`, `track_url`, dan handler `/public/track/:token` **nol hit** di seluruh `services/recruitment/*.go`; test template email menguncinya (`"applied: tombol tracking harus sudah dihapus"`). Rute gateway `/public/recruitment/track/:token` yang tertinggal dibuang di bip-erp #1824 (merged 2026-09-10): dev dan prod sudah bersih (prod sejak 2026-09-11) ([[CORE - API Master Gateway]]). Deskripsi di bawah dipertahankan sebagai riwayat, **bukan keadaan sekarang** — kandidat kini tak punya cara memeriksa lamarannya sendiri. **Riwayat bentuk lamanya:** `candidate.tracking_token` (crypto/rand 32-hex — **bukan `_id`** agar tak bisa dienumerasi) di-set saat create/apply; endpoint publik `GET /public/track/:token` (gateway `/public/recruitment/track/:token`) → tampilan **curated** (nama/posisi/tanggal + progress & status label ramah + stepper), tanpa skor/catatan internal. Email "lamaran diterima" +tombol **Lihat Status Lamaran** (base env `CAREER_PORTAL_URL`); respons `/apply` kembalikan `tracking_token` + `track_url`. Label penolakan dilembutkan ("Belum Sesuai") — apakah status ditampilkan ke kandidat = keputusan HRD terbuka ([[HRIS - Recruitment]]).

**Belum (menyusul, Fase G–I):** offer letter template; recruitment/career settings. *(~~onboarding checklist per-kandidat #492~~ **dibuang lagi 2026-07-18** — dead code, lihat catatan di atas.)*

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

**FE terkait (erp-frontend, semua merged):** badge **Tahap kandidat bisa diubah dari tabel** (reuse `InlineSelectBadge` diekstrak dari Support Ticket); menu **Job Requisitions** di "Portal Saya" (SPV-only) + halaman `/portal/requisitions` (`scope=department`, tombol Buat Pengajuan pindah ke sini, departemen **terkunci** ke pengaju); filter Departemen/Jenis + search + pagination di tabel requisition (+ perbaikan `FilterTable` crash `SelectItem value=""` yang berdampak **semua** halaman ber-filter); **buka detail dengan klik baris** (buang kolom Aksi ikon-mata) di semua tabel Recruitment; **fix data-loss edit lowongan** (`PUT /postings/:id` full-replace → FE round-trip `terms`/`show_*` agar tak terhapus senyap); **fix key i18n mentah** (lookup System Setup + detail requisition).

## Increment: Direktur ajukan requisition lintas-departemen (2026-08-29)

> Pelonggaran **ditargetkan** di atas penguncian PR #478 (departemen = identitas pengaju). `go build`/`vet`/`test` hijau (recruitment + employee). ⚠️ **Belum ter-deploy** (deploy manual — BE recruitment + employee DULU, baru FE). Branch `feature/workspace-position`.
>
> **Kebutuhan:** di `/portal/requisitions/create`, jabatan Direktur hanya bisa memilih posisi departemennya sendiri (Sekretariatan) karena form berjalan mode grup se-departemen. Direktur perlu mengajukan kebutuhan karyawan untuk posisi di **seluruh** departemen.

- **Gerbang = NAMA JABATAN, bukan `system_roles`.** Dipakai `common.SetaraDirektur` (Direktur + Corporate Secretary, [[Microservices - Recruitment Service]] sudah memakainya untuk approval hire) — `id.Position` dari header gateway. SPV biasa tetap terkunci ke departemennya (PR #478 utuh). ⛔ **Sumbu ini SUDAH DIGANTI** beberapa jam kemudian — lihat increment "Sumbunya jenjang" di bawah.
- **BE recruitment (`departmentForNewRequisition`):** untuk `SetaraDirektur` departemen diambil dari **body** (posisi lintas-departemen); selain itu tetap dari identitas pengaju. Recruitment-service tak memiliki koleksi `master_department`, jadi nilai body **tak** divalidasi lintas-master di sini — picker FE hanya menawarkan departemen master valid & Direktur peran tepercaya.
- **BE recruitment (`listRequisitions?scope=department`):** filter kini `$or[{department∈cakupan},{requested_by=pengaju}]`. Tanpa cabang `requested_by`, requisition lintas-departemen yang diajukan Direktur **lenyap dari daftar portalnya** (cakupan portal = departemen sendiri) — alur pengguna terputus. Konstruksi `$or` diekstrak ke helper `requisitionDeptScopeOr` + unit test.
- **BE employee (`GET /data-type/position?all=true`):** mode baru mengembalikan posisi **seluruh** master department company sebagai `[{position,department}]` (helper `allPositionOptions` + test), untuk memberi makan dropdown Posisi sisi Direktur. Company-scoped (`EffectiveCompanyID`).
- **FE (erp-frontend):** hook `useAllPositions` (→ `all=true`); `RequisitionForm` prop `allDepartments` **reuse mekanisme mode grup SPV** (field Departemen disembunyikan, `department` requisition mengikuti posisi terpilih yang berlabel departemen); `/portal/requisitions/create` mendeteksi Direktur via `setaraDirektur(position)`. Key i18n `reqDeptScopeAll` (id+en).
- **Alur pengguna:** Direktur pilih posisi (lintas-departemen, berlabel) → departemen ikut → Simpan → requisition masuk antrean review SPV HRD (tak berubah) → **tampil kembali** di `/portal/requisitions` lewat cabang `requested_by`.
- **Konsumen:** [[API - Recruitment Service]] (`POST /requisitions`, `GET /requisitions?scope=department`) · [[API - Employee Service]] (`/data-type/position?all=true`). Detail endpoint di sana.

## Increment: Sumbunya jenjang jabatan, bukan nama jabatan (2026-08-29, ⚠️ belum merged)

> Mengganti sumbu increment tepat di atas, beberapa jam setelah ia mendarat di `main`. Keputusan & alasan lengkap: [[ADR - 0062 Jenjang Jabatan Menggerbangi Pengajuan Requisition Lintas-Departemen]]. `go build`/`vet`/`test` hijau (recruitment); `pnpm tsc`/`lint`/`build` bersih (erp-frontend). ⚠️ **Belum merged, belum ter-deploy.** Branch `feat/recruitment-requisition-jenjang-direktur` (bip-erp) + `feat/requisition-jenjang-direktur` (erp-frontend).
>
> **Kenapa diganti:** `common.SetaraDirektur` menyatakan wewenang **MEMUTUS** dan mencakup **Corporate Secretary**, sementara pemilik produk membatasi kewenangan ini pada **Direktur saja** (2026-08-29). Pencocokan namanya juga PERSIS, sehingga `"Direktur Utama"` tak akan pernah cocok dan fiturnya mati diam-diam bagi pemegangnya.

- **Gerbang = JENJANG jabatan** (`master_department.position_items[].level_key` terhadap `master_job_level`), dibandingkan dengan **kesamaan** ke `employee.LevelDirektur`, bukan `RankOf(...) >=`. Pertanyaannya keanggotaan satu jenjang, bukan urutan; `>=` akan membuat jenjang baru di atasnya (mis. Komisaris) **diam-diam mewarisi** wewenang ini. Imbalannya `master_job_level` tak perlu dimuat sama sekali.
- **Penyimpangan sadar:** `models/employee/master_data.go` dan `services/employee/job_level.go` menyatakan jenjang **bukan** sumbu hak akses dan tak boleh jadi gerbang endpoint. Batas yang disepakati: jenjang memberi wewenang **MENGAJUKAN**, tidak pernah menyetujui (approval tetap `gate(common.PermRecruitmentApprove, isHRSupervisor)`), dan tak boleh dibaca `permission_resolve.go`. Lihat ADR 0062 dan [[CORE - RBAC dan Permission Set]].
- **BE recruitment (`jenjang.go`, baru):** `bolehAjukanLintasDepartemen` menanyakan jenjang pengaju ke [[Microservices - Employee Service]] `GET /master/departments`, **hanya bila** departemen yang diminta berbeda dari departemen pengaju (`EqualFold`). Pengajuan biasa karena itu tak menyentuh jaringan sama sekali. `departmentForNewRequisition` kini menerima `bolehLintas` sebagai parameter supaya resolusi departemen tetap bisa diuji tanpa jaringan.
- ⛔ **Gagal memastikan jenjang → `503` berpesan, BUKAN diturunkan jadi "tidak berhak".** Menyamakannya akan menyimpan requisition ke departemen pengaju dengan status **201** tanpa satu pun gejala, dan salahnya baru ketahuan berhari-hari kemudian. Lima jalur gagal (URL kosong, host mati, 500, 403, badan bukan JSON) dikunci uji lewat `httptest`.
- **Jabatan tanpa `level_key` berperilaku seperti pengaju biasa** (fail-closed). Diukur ke prod 2026-08-29: **100 dari 118** jabatan sudah berjenjang, dan tepat **satu** berjenjang `direktur` (`Kesekretariatan / Direktur`). ⚠️ **Dev punya NOL** jabatan berjenjang direktur, jadi verifikasi di dev menuntut `level_key` diisi lebih dulu — tanpa itu fiturnya tampak rusak padahal datanya yang belum ada.
- **FE (erp-frontend):** hook `useJenjangSaya` + fungsi murni `jenjangJabatan`/`berjenjangDirektur` (`src/hooks/use-jenjang-jabatan.ts`), cerminan `jenjang.go` dan dikunci uji di kedua sisi. `/portal/requisitions/create` tak lagi memakai `setaraDirektur(position)`; formnya **ditahan kerangka** sampai jenjang diketahui, sebab `useAuth` sengaja mengembalikan undefined pada render pertama (menghindari hydration mismatch) sehingga Direktur akan melihat form versi terkunci-departemen sekejap lebih dulu.
- **Dropdown Posisi & Departemen jadi `Combobox` ber-search**, opsi **dikelompokkan per departemen** saat daftarnya lintas-departemen. Daftar sisi Direktur memuat seluruh posisi perusahaan (118 jabatan di prod) dan tanpa pencarian praktis tak bisa dipakai. Placeholder yang sebelumnya hardcode Bahasa Indonesia dipindah ke `t()` (id+en, diuji instance i18next asli + kontrol negatif `en` bukan salinan `id`).
- **Alur pengguna:** ditutup satu titik putus tambahan — di mode lintas-departemen field Departemen tak dirender dan `department` bergeser mengikuti posisi, jadi ditambahkan keterangan **"Tercatat di departemen X"**. Tanpa itu pengaju menekan Simpan tanpa tahu requisition-nya masuk ke mana, lalu mencarinya di tempat yang salah.

## Increment: Konversi Kandidat → Karyawan (hire→employee, 2026-07-16)

> BE **PR #490** (bip-erp) + FE **PR #344** (erp-frontend), keduanya **merged** ke `main`. `go build`/`vet`/`test` hijau. ⚠️ **Belum ter-deploy** (deploy manual — BE dulu baru FE).

Menutup TBD lama "mapping hire → data karyawan". Pembuatan **data master karyawan** tetap di HRIS (bukan di recruitment) — recruitment hanya menyediakan **data kandidat** + **tautan** agar tak ada konversi ganda.

- **BE (#490):** `candidate` + field **`employee_id`** (omitempty). Endpoint baru `PUT /candidates/:id/link-employee` (isHR): wajib kandidat **Hired** & **belum tertaut** → set `employee_id`, `progress`→**Onboarding**, tulis audit. `updateCandidate` mempertahankan `employee_id`. Tak ada auto-generate employee_id (dibuat HRIS).
- **FE (#344, erp-frontend):** HRIS "Tambah Karyawan" kini bermula dari **modal 2 opsi** — *isi manual* (perilaku lama) atau *dari kandidat rekrutmen*. Mode dari-kandidat: picker kandidat **Hired belum tertaut** (`GET /candidates?status=Hired`, filter `!employee_id`) → wizard memprefill data kandidat (nama, jenis_kelamin, tanggal_lahir, email, no_hp, alamat), **menyembunyikannya** (kartu ringkasan read-only) & hanya menampilkan **sisa** field yang HR isi. Field wajib yang **kosong** di kandidat tetap tampil (email/alamat/tgl lahir opsional). Karyawan dibuat via `POST /api/hris/employees/multi` ([[Microservices - Employee Service]]), lalu `link-employee` dipanggil (best-effort) agar kandidat drop dari picker.
- **Alur:** kandidat harus lebih dulu `Hired` (offer → accept → hire) baru muncul di picker.

## Increment: Onboarding Checklist per-kandidat — ❌ DIHAPUS (2026-07-18) → dibangun ulang 2026-07-26

> **Versi lama** ini dibuang; **dibangun ulang** 2026-07-26 dengan model & alur berbeda — lihat increment "Onboarding Checklist (rebuild)" di bawah.
>
> ~~Instansiasi per-kandidat dari template `onboarding_checklist`.~~ **Dibuang** (BE `chore/remove-onboarding-checklist` + FE erp-frontend, 2026-07-18). Baik master template (`/checklists*`, Fase 2) maupun instance per-kandidat `onboarding_progress` (`/candidates/:id/onboarding*`) beserta komponen FE (`ChecklistsPage`, kartu `OnboardingSection` + hooks) **tak ada lagi di kode** — komponen FE **yatim/tak pernah dirender** sejak dibangun (#492/#346), jadi dead code. Data Mongo lama dibiarkan (tak dipakai). **Dipertahankan:** stage pipeline `Onboarding`, hire handoff `/onboarding/register`, `link-employee`, dan **Performance Review Onboarding** (di bawah).

## Increment: Onboarding Checklist (rebuild — 2026-07-26, ✅ BE live dev)

> Membangun ulang fitur checklist onboarding karyawan baru (dibuang 2026-07-18 karena dead code) sebagai **fitur dedicated** meniru pola Performance Review Onboarding — kali ini **dengan penugasan PIC lintas-tim + notifikasi + pelacakan progres**. Mendigitalisasi proses manual HR (orientasi, setup IT, dokumen, tunjangan, kenalan tim). BE **PR #692** + FE **PR #524** (erp-frontend), keduanya **merged**; BE **terverifikasi live** di dev (smoke test create+delete template via gateway). `go build`/`vet`/`test` hijau. **≠ Performance Review Onboarding**: ini checklist tugas operasional (siapa mengerjakan apa, kapan); Performance Review = penilaian masa evaluasi. Keduanya berdampingan.

- **Koleksi baru** (`db.go`): `onboarding_template` & `onboarding_instance`.
  - `onboarding_template` (master, HR): key/name/description/target/status(`active`/`inactive`) + `items[]` {task, category, `assigned_role` (label panduan), is_required, due_day (hari sejak mulai)}.
  - `onboarding_instance` (per karyawan baru): employee snapshot + template_key/name + start_date + buddy (opsional) + status (`In Progress`→`Completed`) + `tasks[]` snapshot {id lokal, task, category, is_required, due_date, `assignee` (PIC), status (`Pending`/`In Progress`/`Done`), done_by/at, note}. **Snapshot**: edit template tak mengganggu instance berjalan.
- **Template CRUD** (`require(isHR)`): `/onboarding-templates` (+`/:id`).
- **Instance** (`require(isHR)`): `POST /onboarding-instances` (bangun tasks dari item + PIC pilihan HR, hitung `due_date` = start + due_day, notif inbox tiap PIC), `GET` (filter `?status=&employee_id=`), `GET /:id`, `PUT /:id/complete` (override manual).
- **PIC** (`requireAuth` + guard assignee/HR): `GET /onboarding-tasks/assigned` (tugas saya lintas instance), `PUT /onboarding-instances/:id/tasks/:taskId` (tandai status + catatan; **auto-complete** instance saat semua item `is_required` = Done).
- **RBAC**: kelola = isHR; PIC ditetapkan HR **manual** (tak ada auto-resolve role→orang, karena system_roles=hak modul, bukan jabatan org). **Notif** = inbox best-effort; **email PIC DITAHAN** (menyusul, event template `onboarding_task_assigned`). 🟡 **(bip-erp `feat/recruitment-alur-kerja-hr`, belum merge)** satu notifikasi per PIC unik lewat `notifyInboxRute`, kategori `task-assigned`, `app_route` `/tugas-onboarding` (rute layar tugas onboarding MyBharata), pesan netral yang menyebut jumlah tugas dan menyuruh membuka aplikasi MyBharata (`onboarding_notify.go`: `kategoriTugasOnboarding`, `ruteTugasOnboardingDiAplikasi`, `pesanTugasOnboarding`, `picTugasOnboarding`, `payloadInbox` memakai `notification.SendInboxRequest`). Sebelumnya kategori `request-waiting-review` dan pesannya menyuruh membuka menu web "Tugas Onboarding Saya" yang sudah dicabut. `app_route` belum membawa ke mana pun di ponsel: payload push sengaja kosong dan pemeta rute notifikasi MyBharata tak mengenal `task-assigned` (jatuh ke halaman Notifikasi). `task-assigned` sudah ada di `InboxCategories`, jadi notification-service tak perlu ikut naik. Dikunci `onboarding_notify_test.go`
- **FE** ([[APP - Web ERP]]): menu **Onboarding Checklist** (Recruitment, 2 tab: Template + Onboarding Berjalan) + **Tugas Onboarding Saya** (Portal Saya; ⚠️ menunya dicabut 2026-08-13, tugas PIC dikerjakan di [[APP - MyBharata]]). Menu lama **"Candidate Onboarding" di-rename → "Review Onboarding"** (= Performance Review) agar tak rancu. Reuse Combobox 2-baris + `useListEmployees`. i18n id+en.
- **File** (`services/recruitment`): `models_onboarding.go`, `onboarding_template_handlers.go`, `onboarding_instance_handlers.go`, `onboarding_task_handlers.go`, `onboarding_test.go` (+ `db.go`/`routes.go`). Nol perubahan shared-library → service lain nol risiko.
- **Belum**: uji E2E penuh via UI; email PIC; konfirmasi deploy FE (manual).

## Increment: Performance Review Onboarding (⚠️ PR #493/#349 — belum merged/deploy)

> Digitalisasi **Form Review Performance Masa Evaluasi** (dulu Google Form). Di perusahaan, "onboarding" = **masa evaluasi** karyawan baru yang berpuncak pada sesi **Performance Review Onboarding** (peserta presentasi → beberapa penilai lintas divisi menilai → HR putuskan status). `go build`/`vet`/`test` hijau (+ `TestValidateReviewResponse`, `TestReviewOutcomeValid`). Detail konsep di [[HRIS - Recruitment]].

- **Data:** `onboarding_review` (sesi per peserta = **karyawan masa evaluasi** (`employment_type` "PKWT (Evaluasi)"): `employee_id` + snapshot nama/jabatan/departemen, `scheduled_at`, `location`, status `Scheduled`→`Decided`, `reviewers[]` snapshot, `decision` {outcome `Lulus`/`Diperpanjang`/`Tidak Lulus`, note, decided_by/at}) + `onboarding_review_response` (per penilai: `ratings` 7×1-5 + 3 uraian strengths/improvements/recommendations).
- **Kriteria 7 + uraian 3 = konstanta** (`reviewCriteriaKeys`) — **purpose-built, bukan form builder** (Custom Questions form-builder sengaja sudah dihapus; nilai fitur ada di alur undang→isi→rekap→putuskan, bukan di field).
- **HR (isHR):** `POST /onboarding-reviews` (body `{employee_id, peserta_name, peserta_position, peserta_department, scheduled_at, location, reviewers[]}` — peserta = snapshot karyawan dari FE, **BE tak lagi lookup koleksi kandidat / cek StHired**; peserta di-skip bila ikut di `reviewers[]` → **cegah self-review**; buat + undang penilai via `notifyInbox` inbox internal + email Resend best-effort), `GET` (list, filter `?status=&employee_id=`), `GET /:id` (rekap semua jawaban), `PUT /:id/decide`.
- **Penilai (requireAuth, karyawan mana pun):** `GET /onboarding-reviews/assigned` (tugas saya + jawaban saya; jawaban penilai lain disembunyikan), `POST /:id/response` (edit sampai `Decided`).
- **FE (erp-frontend):** halaman khusus HR (menu Recruitment → **Performance Review**: list + buat + detail rekap + keputusan) + menu **Review Onboarding Saya** (Portal Saya, **semua karyawan**: form 7 rating + 3 uraian).

## Increment: Interview Orchestration (2026-07-17, #498/#356 — merged)

> Menutup 3 gap fitur interview (audit 2026-07-17): sebelumnya kaya di pencatatan & feedback tapi kurang orkestrasi. `go build`/`vet`/`test` hijau (+ `TestIsAssignedInterviewer`). ⚠️ **Belum tentu ter-deploy** (deploy manual, BE dulu baru FE).

- **Babak ↔ sesi (Gap A):** `Interview` + field **`round_id`** — sesi interview kini bisa ditautkan ke `interview_round` (babak per-lowongan). Sebelumnya rounds hanya config yatim di lowongan, tak direferensikan saat catat interview. FE: picker Babak di form + tampil di timeline.
- **Undangan pewawancara + "Interview Saya" (Gap B):** `recordInterview` memanggil `notifyInbox` (best-effort) ke tiap pewawancara (`interviewers[]` + `interviewer`, dedup). Endpoint baru **`GET /interviews/assigned`** (requireAuth) mengembalikan sesi yang menugaskan pemanggil sebagai pewawancara, diperkaya nama/posisi kandidat + jawaban sendiri (jawaban penilai lain disembunyikan). FE: menu **"Interview Saya"** (Portal Saya, semua karyawan) → isi feedback sendiri.
- **Feedback editable + agregasi (Gap C):** `POST /interviews/:id/feedback` diturunkan dari `isHR` → **`requireAuth`** + guard (pewawancara sesi **atau** HR) + **upsert** per `(interview_id, interviewer_id)` → satu feedback per pewawancara, bisa diedit, tak dobel. FE dialog feedback menampilkan **rekap panel** (rata-rata per dimensi + overall + tally rekomendasi), bukan lagi daftar mentah.
- **Belum (menyusul):** integrasi kalender/ICS + reminder; auto-advance tahap dari hasil. *(Notifikasi email ke pewawancara/kandidat — ditutup increment berikut.)*

## Increment: Link Form Feedback Interview (email pewawancara, 2026-07-18 — merged)

> BE **PR #536** (bip-erp) + FE **PR #381** (erp-frontend), keduanya **merged** ke `main`. `go build`/`vet`/`test` hijau. **BE dilaporkan sudah ter-deploy di dev**; env `ERP_FRONTEND_URL` (pola sama dengan `reviewFormURL` di [[HRIS - Recruitment]] Performance Review Onboarding) sudah di-set di VM dev — **⚠️ tak terdaftar** di `docker-compose.yml`/`.env.example` repo (masuk lewat `.env` VM di luar repo; tak bisa diverifikasi dari kode saja).

Menutup gap **"notifikasi email ke pewawancara"** dari increment Interview Orchestration di atas: pewawancara stage **User/Final** kini mengisi feedback lewat **link 1-sesi via email** (login-gated), bukan lagi menu "Interview Saya".

- **Model (`models_stages.go`):** `Interview` + field **`Panel []InterviewPanelist`** (`employee_id`/`name`/`email` — snapshot pewawancara dikirim FE saat menjadwalkan, untuk alamat email undangan; `Interviewers []string` tetap sumber identitas/authz) + **`Location string`** (teks bebas, terpisah dari `MeetingLink`/Zoom) + virtual **`FeedbackSubmitted`/`FeedbackTotal`** (diisi `listInterviews`, tak disimpan).
- **`interview_notify.go`:** `interviewUsesLink(stage)` → `true` hanya untuk **User/Final** (stage HR = tanpa link/email, diisi HR dari detail kandidat). `interviewFeedbackURL(interviewID)` membangun `<ERP_FRONTEND_URL>/interview-feedback/<id>` (env kosong → link kosong, email tetap terkirim tanpa tombol). Builder branded: **`interviewInviteEmail`** (ke pewawancara — jadwal+lokasi+tombol "Gabung Meeting" bila ada+tombol "Buka Form Feedback" bila link ada) & **`interviewCandidateEmail`** (ke kandidat — jadwal+durasi+lokasi+meeting link, **tanpa** link form).
- **`email_render.go`:** shell HTML branded (header putih + logo, dari increment sebelumnya) diekstrak jadi **`emailShellHTML`/`emailAccentButton`** — dipakai bersama oleh `renderTemplate` (4 template kandidat existing, tak berubah perilaku) **dan** dua builder email interview di atas — satu sumber tampilan.
- **`stage_handlers.go` (`recordInterview`):** kini kirim **dua email best-effort** setelah simpan sesi: (1) **kandidat** — jadwal+zoom, **semua stage**, `idempotency_key` `intv-cand-<interview_id>`; (2) **panel pewawancara** (`notifyInterviewPanel`, ditulis ulang) — inbox untuk **semua** target (`Interviewers[]` + `Interviewer` tunggal, dedup), **plus email** hanya untuk stage **User/Final** & hanya bila pewawancara punya alamat di `Panel[]`, key `intv-invite-<interview_id>-<employee_id>` (satu email/pewawancara).
- **`interview_ext_handlers.go`:** `submitInterviewFeedback` **diperketat** — hanya **HR** boleh menetapkan `interviewer_id` dari body (rekap/koreksi atas nama pewawancara lain); **non-HR** (jalur link) **selalu** pakai identitas JWT, tak bisa submit atas nama orang lain (authz `isHR || isAssignedInterviewer` tetap). Endpoint baru **`listInterviews`** = `GET /interviews` (HR, list **semua** sesi terbaru dulu, diperkaya nama/posisi kandidat + `feedback_submitted`/`feedback_total`).
- **`routes.go`:** `GET /interviews` (`require(isHR)`) — path eksak, terdaftar **sebelum** `/interviews/:id/*` agar tak ketangkap sebagai `:id`.

**FE (erp-frontend, semua merged):**
- Komponen `InterviewFeedbackForm` diekstrak jadi **reusable** (dipakai baik di dialog HR maupun di halaman link pewawancara).
- Halaman baru **`/interview-feedback/[interviewId]`** (`src/app/interview-feedback/[interviewId]/page.tsx`) — **di luar** grup `(main)` (tanpa sidebar/chrome), pakai `useAssignedInterviews()` (tetap manggil `GET /interviews/assigned`) lalu filter sesi sesuai `interviewId` di URL. **Login tetap wajib**: belum login → interceptor axios (`lib/axios.ts`) auto-redirect ke `/login` saat request 401; identitas dari JWT (server tak percaya `interviewId` di URL untuk authorisasi selain "assigned ke saya").
- Menu HR baru **Interviews** (`/hris/recruitment/interviews`, grup sidebar **Recruitment** — bukan Portal Saya) — tabel semua sesi (filter tahap, search kandidat) + kolom status feedback (`feedback_submitted`/`feedback_total`) + aksi **salin link feedback** (ikon, hanya stage User/Final via `interviewHasFeedbackLink`) & **Lihat** (buka `InterviewFeedbackDialog` rekap panel).
- Form jadwal interview: input **Lokasi** + kirim **snapshot Panel** (nama+email pewawancara) saat menjadwalkan.
- Menu **"Interview Saya"** (dulu `/portal/interviews`, Portal Saya) **dihapus dari navigasi** — digantikan link 1-sesi per email. Komponen `MyInterviewsPage` + route `/portal/interviews` **dibiarkan dormant** (reversible, tak dihapus dari kode).

## Increment: Rekrutmen Lintas Perusahaan (2026-09-11, merged dan live prod 2026-09-12)

> Recruiter yang bekerja di satu perusahaan grup menangani rekrutmen **semua** perusahaan grup lewat izin `recruitment.cross_company` yang dipasang sadar ke posisi (bukan daftar perusahaan tertentu). Pengguna lain tetap terkunci ke perusahaannya sendiri. Merged 2026-09-12 lewat bip-erp #1853, erp-frontend #1543, dan career-bharata #12; backend, Web ERP, dan portal karir live prod (per 2026-09-12). Keputusan & konsekuensi lengkap: [[ADR - 0092 Rekrutmen Lintas Perusahaan lewat Paket Izin]]. Endpoint lengkap: [[API - Recruitment Service]] bagian **Perusahaan**.

### Perusahaan diturunkan satu arah, anak kandidat tanpa salinan

Enam koleksi proses rekrutmen diberi `company_id`: `job_requisition`, `job_posting`, `candidate`, `manpower_plan`, `onboarding_review`, `onboarding_instance` (`services/recruitment/perusahaan.go`, `migrate_company.go`). Rantainya satu arah, tak pernah diketik ulang bila induknya ada:

```
requisition.company_id  (SPV: perusahaan sendiri | pemegang izin lintas: dipilih, divalidasi aktif)
    -> posting.company_id    (selalu dari requisition)
        -> candidate.company_id  (dari posting; tanpa posting: perusahaanTujuan)
            -> interview / offer / hasil tes / background check / psikotes: TIDAK disimpan, dibaca lewat kandidat
```

`manpower_plan`, `onboarding_review`, `onboarding_instance` distempel `perusahaanTujuan` langsung (perusahaan sendiri untuk non-lintas; tervalidasi ke master untuk lintas). Dokumen anak kandidat (interview, offer, hasil tes, background check, psikotes) sengaja TIDAK diberi `company_id` sendiri: perusahaannya selalu dibaca dari kandidatnya (`kandidatTerjangkau`, `idKandidatDalamCakupan`), supaya tak bisa menyimpang bila kandidatnya kelak dipindah lowongan.

`klausaPerusahaan` untuk BIP sengaja ikut menangkap dokumen tanpa field `company_id` (null/absen) dan string kosong: backfill yang gagal sebagian tak boleh membuat data lama BIP lenyap dari layar tanpa satu pun galat. Perusahaan lain tak punya data lama, jadi cukup kesamaan persis.

### Backfill `migrate_company.go`

Dipanggil sekali saat startup, sebelum rute didaftarkan: mengisi `company_id = BIP` pada dokumen ber-`company_id` `$in: [nil, ""]` di keenam koleksi di atas. Idempoten (run kedua mengubah nol dokumen), best-effort per koleksi (kegagalan satu koleksi di-log, tak menghentikan service; data yang tertinggal tetap terlihat BIP karena `klausaPerusahaan` BIP menangkap dokumen tanpa field). BIP dipilih karena sebelum fitur ini recruitment hanya pernah dipakai BIP (komentar `normalPerusahaan`, `perusahaan.go`).

### Izin aditif, bukan pengganti tier

`recruitment.cross_company` dan paket `recruitment_lintas_perusahaan` ("Rekrutmen: Lintas Perusahaan", `shared-library/common/catalog_recruitment.go`) berisi TEPAT satu izin. Sengaja TIDAK masuk `RecruitmentTierDefault` maupun paket admin (penjaga `TestRecruitmentTierDefaultTanpaIzinLintasPerusahaan`, `TestPaketAdminTanpaIzinLintasPerusahaan`): fallback tier akan memberikannya ke setiap pemegang `hris` tanpa paket. Izin ini aditif, melebarkan cakupan perusahaan izin pipeline yang sudah dipegang, bukan memberi izin pipeline itu sendiri. Satu-satunya hak yang ia buka sendiri: `POST /requisitions` (`requireAtasanAtauLintasPerusahaan`), karena perusahaan tujuan bisa belum punya atasan yang memakai ERP.

`izinRecruitmentEfektif` (`permission_gate.go`) TIDAK menghitung izin aditif (`requisition_cross_dept`, `cross_company`, diturunkan dari katalog dikurangi izin pipeline lewat `izinAditifRecruitment`) saat menilai "klaim memuat izin modul recruitment", dan selalu menyertakannya ke hasil. Ini menutup jebakan yang dicatat [[ADR - 0080 Permission Set Menggerbangi Pengajuan Requisition Lintas-Departemen]]: tanpa penjagaan ini, memasang satu paket aditif ke posisi yang belum punya paket recruitment lain membuat cabang "klaim memuat izin modul" menang lalu MENCABUT seluruh izin tier-nya. Menurut komentar kode, itu terjadi di produksi 2026-09-08 pada posisi Direktur.

### Cache master perusahaan: 5 menit segar, jeda gagal 30 detik, salinan basi tetap dipakai

recruitment-service tak menyimpan salinan perusahaan; ia membaca `GET /master/companies` milik employee-service lewat cache in-memory (`cachePerusahaan`, `perusahaan.go`), bukan tiap kali langsung ke jaringan:

- **Segar**: salinan berumur kurang dari 5 menit (`umurCachePerusahaan`) dipakai apa adanya, tanpa panggilan jaringan.
- **Gagal dimuat ulang**: kegagalan diingat 30 detik (`jedaGagalPerusahaan`). Selama jeda itu TIDAK ADA panggilan jaringan baru sama sekali, termasuk permintaan paksa-segar (`perusahaanTujuan` memuat ulang sekali saat perusahaan yang diminta belum ada di cache). Tanpa jeda ini, tiap baris daftar lowongan publik dan tiap email kandidat menunggu timeout `InternalRequest` (10 detik) sendiri-sendiri, dan gateway sudah memutus portal karir sebelum baris kedua selesai.
- **Salinan basi**: bila gagal dimuat ulang tapi masih ada salinan lama, salinan itu tetap dipakai dan ditandai `basi`. Pemanggil yang MENOLAK sesuatu berdasarkan isi daftar (`perusahaanTujuan`, validasi `POST /requisitions`) wajib membaca tanda ini: salinan basi bisa tak mengenal perusahaan yang baru dibuat, dan penolakannya jadi `503` (bukan `400` "tak dikenal") supaya orangnya tahu untuk mencoba lagi, bukan membetulkan pilihan yang sebenarnya sudah benar. Pemanggil yang hanya MENAMPILKAN (nama perusahaan di email, `GET /companies`) memakai salinan basi apa adanya: tampilan yang sedikit usang lebih berguna daripada `503`.
- **Tanpa salinan sama sekali**: galat diteruskan apa adanya (`503` di `GET /companies`, nama jadi key mentah di email).

Dipakai untuk: `{{perusahaan}}` di email kandidat dan undangan panel/penilai, `company_name` di portal karir (`GET /public/postings`, `GET /public/postings/:id`), notifikasi requisition baru ke SPV HRD, validasi perusahaan tujuan (`perusahaanTujuan`), dan pemilih `GET /companies` (dibaca dari cache yang SAMA supaya pemilih tak pernah menawarkan status aktif yang berbeda dari penilaian validatornya).

### Dependensi baru: endpoint publik portal karir kini bergantung employee-service

Sebelum fitur ini, `GET /public/postings*` dan `POST /apply` tak menyentuh employee-service sama sekali (`/apply` hanya memanggil notification-service untuk email). Sekarang keduanya memanggil `namaPerusahaan`: daftar dan detail lowongan untuk `company_name`, `/apply` untuk nama perusahaan di email "lamaran diterima". Dampaknya dikurangi cache dan jeda gagal di atas, tapi tetap panggilan jaringan saat cache meleset. Employee-service yang lambat atau padam kini ikut memperlambat endpoint publik portal karir, bukan cuma layar HR internal.

### Pemindai sumber `penjaga_perusahaan_test.go`

Lima test AST memindai `services/recruitment/*.go` (bukan file `_test.go`), bukan memanggil handler dengan database sungguhan (service ini tak punya database di test):

- `TestSetiapFindOneKoleksiBerperusahaanTerjaga`: tiap fungsi yang memanggil `FindOne` pada koleksi berperusahaan (`requisitionsCol`, `postingsCol`, `candidatesCol`, `offersCol`, `interviewsCol`, `manpowerPlansCol`, `onboardingReviewsCol`, `onboardingInstancesCol`) wajib terdaftar di peta `findOneTerjaga` dengan penjaga yang benar-benar dipanggil di badan fungsinya (atau alasan tertulis kenapa sengaja tanpa penjaga).
- `TestSetiapDaftarKoleksiBerperusahaanDisaring`: tiap fungsi yang membaca/mengubah banyak dokumen (`Find`/`CountDocuments`/`Aggregate`/`Distinct`/`DeleteMany`/`UpdateMany`) wajib terdaftar di `daftarTersaring`.
- `TestSetiapRutePerIDMencapaiPenjaga`: tiap rute per-ID di `routes.go` (`/candidates/:id`, `/offers/:id`, `/postings/:id`, `/requisitions/:id`, `/manpower-plans/:id`, `/onboarding-reviews/:id`, `/onboarding-instances/:id`, `/stages/:kind/:id`, `/interviews/:id`, `/mpp/vacancies/:employeeID`) wajib mencapai penjaganya, langsung atau lewat satu tingkat helper.
- `TestHelperTanpaPenjagaHanyaDariPemanggilBerpenjaga`: helper yang memuat dokumen berperusahaan TANPA penjaga sendiri (mis. `muatReview`, `enrichOffers`) hanya boleh dipanggil dari daftar pemanggil yang terdaftar; pemanggil baru yang tak terdaftar membuat test merah.
- `TestSetiapInsertKoleksiBerperusahaanMenstempelPerusahaan`: tiap fungsi yang `InsertOne`/`InsertMany`/`ReplaceOne` ke koleksi berperusahaan wajib punya penimpaan `CompanyID` di badannya.

**Batasnya, tertulis di kode**: pemindai tak membaca ARGUMEN (mengoper perusahaan yang salah ke penjaga yang benar tetap lolos) dan tak mengikuti koleksi yang dioper lewat variabel. Versi pertama pemindai ini hanya membandingkan himpunan nama fungsi, dan menghapus blok `boleh` di `fetchCandidate` tak membuat test mana pun merah; diperbaiki supaya yang diperiksa adalah kehadiran pemanggilan penjaganya di AST, bukan sekadar namanya ada di daftar.

### Catatan deploy (belum dijalankan)

- **employee-service tak boleh tertinggal dari recruitment-service.** Tanpa `company_id` di `/internal/mpp-vacancies` (employee-service), posisi kosong perusahaan lain terbaca BIP di `GET /mpp/vacancies`, dan keputusan "Buat rencana" tercatat BIP dengan `201` tanpa satu pun galat. Perubahan katalog izin juga menuntut kedua service naik bersama (pola [[ADR - 0080 Permission Set Menggerbangi Pengajuan Requisition Lintas-Departemen]]). BE sebelum FE, seperti biasa. career-bharata aman kapan pun (`company_name` field opsional di tipe).
- **Paket `recruitment_lintas_perusahaan` dipasang ke posisi recruiter yang SUDAH punya paket recruitment lain**, DAN ke posisi SPV HRD penyetuju (keputusan user saat `/review` 2026-09-11). Tanpa yang kedua, SPV HRD tetap menerima notifikasi requisition perusahaan lain (kini menyebut nama perusahaannya) tapi mendapat `404` saat membukanya.
- **Berlaku sesudah login ulang**: izin dipanggang ke klaim JWT saat login, sama seperti ADR 0080. Cache respons gateway yang berkunci `employee_id` juga bisa menahan respons lama sampai TTL habis.
- Gerbang verifikasi sebelum paket dipasang, lewat gateway: `GET /api/recruitment/companies` membalas `200`/`403` (bukan `404` rute hilang); baris `GET /api/recruitment/mpp/vacancies` membawa `company_id`.

## Dokumen Terkait

- [[HRIS - Recruitment]] — konsep/bisnis & keputusan HRD (pasangan dok ini)
- [[API - Recruitment Service]] — daftar endpoint lengkap
- [[APP - Portal Karir Bharata]] — portal karir publik (konsumen `/public/recruitment/*`)
- [[Microservices - Employee Service]] · [[Microservices - Notification Service]] · [[Microservices - File Service]]
- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]]
- [[ADR - 0092 Rekrutmen Lintas Perusahaan lewat Paket Izin]] (rekrutmen lintas perusahaan, live prod 2026-09-12) · [[ADR - 0080 Permission Set Menggerbangi Pengajuan Requisition Lintas-Departemen]] · [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]
