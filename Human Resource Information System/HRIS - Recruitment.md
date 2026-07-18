## Deskripsi

*Desain (to-be) subsistem **Recruitment** — mengelola **siklus depan karyawan**: dari kebutuhan posisi sampai jadi karyawan aktif. Memisahkan subsistem **Talent acquisition → Interview → On-boarding** yang sekarang menumpuk di [[HRIS - Analysis]] ke ruangnya sendiri.*

- **Status**: ⚠️ **BE sebagian diimplementasi** — Fase 1-3 + adopsi struktur ERPGo (Fase A–F) live di [[Microservices - Recruitment Service]]; **portal karir publik sudah ada** ([[APP - Portal Karir Bharata]] — pelamar melamar sendiri + kirim berkas + cek status). Menyusul: AI CV screening, psikotes online, WhatsApp kandidat, integrasi job board
- **Target arsitektur**: microservice `recruitment-service` baru ([[Microservices - Recruitment Service]]) + modul web, dengan **rollout bertahap**
- Titik singgung yang sudah ada di kode: `POST /onboarding/register` (aktivasi akun karyawan baru) di [[Microservices - Employee Service]] — menjadi handoff akhir recruitment

## Latar Belakang

* Saat ini langkah recruitment (talent acquisition, interview, onboarding) tercampur di [[HRIS - Analysis]] dan sebagian masih manual/spreadsheet.
* Tujuannya: alur formal & terlacak dari **permintaan posisi → lowongan → pelamar → screening → interview → psikotes → offer → onboarding**, terintegrasi dengan master data karyawan.

## Pipeline (End-to-End)

![[Recruitment Pipeline.excalidraw]]

1. **Job Requisition** — SPV/atasan mengajukan posisi via **Form Permintaan Karyawan** (field: departemen, jumlah karyawan sekarang, jumlah dibutuhkan, posisi, **jenis permintaan: penambahan/penggantian**, alasan, **persyaratan/kualifikasi**: usia, jenis kelamin, pendidikan, pengalaman, kualifikasi, tugas & tanggung jawab, tanggal mulai). Alur: **SPV mengisi kualifikasi** → **HR (HRGA Supervisor) review kualifikasi** (sesuai/standar atau minta revisi) → **Direktur menyetujui** → status `Approved` → lowongan boleh dibuka. **Tanpa batasan kuota** (jumlah dibutuhkan bersifat informasional, bukan cap)
2. **Sourcing & Job Posting** — HR membuka lowongan + mencatat **sumber pelamar**. Kanal eksternal utama saat ini: **Glints (TapLoker)** — ATS/job-portal yang dipakai aktif (PT Bharata terverifikasi: pasang lowongan, Pertanyaan Skrining, akses CV, chat WA); plus referral, walk-in, bootcamp
3. **Candidate Management** — data pelamar (CV, kontak, posisi dilamar, sumber) + pelacakan pipeline via field **`progress`** (tahap) & **`status`** (keadaan), enum mengikuti **rekaman HRD** (lihat Model Data)
4. **Screening (manual)** — HR menyaring CV/data pelamar **manual** terhadap kriteria posisi (lihat bagian khusus di bawah); **AI CV screening** direncanakan sebagai enhancement fase lanjut
5. **Interview** — penjadwalan, **multi-tahap**: HR Interview → User Interview → **Technical Test (tes skill — terpisah dari psikotes)** → Final Interview (jumlah tahap tergantung posisi, mis. SPV) — HR + hiring manager/SPV dept; scoring + catatan per tahap. Lolos → **Background Check**. **Orkestrasi (✅ #498/#356):** sesi bisa ditautkan ke **babak** (`round_id`). **Feedback via link email (✅ #536/#381, 2026-07-18):** untuk stage **User & Final**, tiap pewawancara di panel (snapshot nama+email dikirim FE saat menjadwalkan, terpisah dari `Lokasi`) menerima **email undangan branded** (jadwal, lokasi/link meeting, tombol **"Buka Form Feedback"**) menuju halaman **login-gated tanpa sidebar** (`/interview-feedback/<id>`) tempat ia mengisi feedback sendiri (3 rating + rekomendasi, editable/upsert) — **menggantikan** menu **"Interview Saya"** (dihapus dari navigasi Portal Saya; komponen & endpoint `/interviews/assigned` tetap ada tapi dormant). Stage **HR**: tanpa email — HR isi feedback dari menu **Interviews** (dialog Lihat). **Kandidat** juga menerima email undangan jadwal (**semua stage**, tanpa link form). **Pengelolaan interview terpusat di menu Interviews (✅ FE):** jadwalkan (pilih kandidat aktif) + edit + hapus + salin link + lihat/isi feedback (terisi/total), semua dari sini; **detail kandidat menampilkan interview read-only** (jenis tahap lain — screening/tes/background check — tetap dicatat dari detail kandidat). Belum: kalender/reminder ICS, auto-advance tahap dari hasil.
6. **Psikotes / Assessment** — setelah lolos interview & **Background Check**, kandidat mengikuti psikotes **sebelum offer**. Dua mode: **(a) online self-service** (kandidat mengerjakan tes di portal — butuh test-engine/bank soal, **TBD**) atau **(b) manual** — **dilaksanakan staf HR langsung** (HR input skor + lampirkan **report PDF**). **Rekomendasi: mulai mode manual (HR)**, online menyusul. Hasil (skor per-aspek + rekomendasi/interpretasi) jadi bahan keputusan akhir sebelum offer (ambang/bobot final di HR — lihat **Pertanyaan untuk HRD**)
7. **Offer & Decision** — keputusan + surat penawaran → kandidat accept/decline
8. **Hire → Karyawan** — saat kandidat `Hired`, HR membuat **data karyawan** di HRIS "Tambah Karyawan" (mode *dari kandidat* — data kandidat diprefill, HR isi sisanya) via [[Microservices - Employee Service]]; kandidat lalu **ditautkan** ke `employee_id` (`PUT /candidates/:id/link-employee`, progress→Onboarding). Aktivasi akun tetap via `POST /onboarding/register`.
9. **Masa Evaluasi & Performance Review Onboarding** — karyawan baru jalani masa evaluasi, berpuncak pada sesi **Performance Review** (presentasi → penilai lintas divisi menilai → keputusan status) — lihat bagian khusus di bawah. *(Onboarding checklist per-kandidat #492 dihapus 2026-07-18 — dead code.)*

## Screening (Manual; AI menyusul)

*Penyaringan awal pelamar: HR menilai kecocokan CV/data pelamar terhadap **kriteria posisi** (dari kualifikasi yang difinalkan di requisition). **Saat ini manual** — keputusan lanjut/tidak tetap di HR. Untuk pelamar via **Glints**, **Pertanyaan Skrining** Glints menjadi filter awal sebelum HR review. **AI CV screening** direncanakan sebagai enhancement (fase lanjut).*

**Alur (manual — fase awal):**
1. Pelamar masuk (via portal lowongan publik / input HR) → buat record `candidate` (status `Applied`); CV disimpan ke [[Microservices - File Service]] (MinIO)
2. **HR review** CV vs kriteria (pendidikan, pengalaman, skill; must-have/nice-to-have) → **putuskan lanjut ke Interview / Reject**
3. Alasan keputusan disimpan untuk audit/fairness

**Enhancement (fase lanjut) — AI CV Screening:**
- Ekstrak teks CV (PDF; fallback OCR via [[CORE - OCR Document Service]] bila CV hasil scan) → kirim ke **LLM (OpenRouter)** → **skor kecocokan + rekomendasi** (bersifat **asisten**, tanpa auto-reject; HR tetap memutuskan). Reuse infra LLM Ideamills ([[Sales - Veo (Gemini) Implementation]]).

**Pengaman**: human-in-the-loop (tanpa auto-reject), alasan disimpan untuk audit/fairness, data pelamar (PII) disimpan aman.

## Aktor & Role

| Aktor | Peran |
| --- | --- |
| **Pengaju (SPV / kepala dept)** | Mengajukan Job Requisition via Form Permintaan Karyawan + **mengisi usulan kualifikasi** kandidat |
| **HR / HRGA Supervisor** | **Review kualifikasi** requisition (sesuai/minta revisi) + finalkan kriteria; kelola pipeline (lowongan, pelamar, jadwal incl. psikotes, input hasil); penerbitan offer |
| **Direktur** | **Menyetujui Job Requisition** (menggantikan pola lama berbasis kuota) |
| **Pewawancara** (hiring manager / SPV dept) | Ikut interview & penilaian (multi-tahap s/d 3×) |
| **Kandidat** | Eksternal — **tanpa akun ERP** (data dikelola HR) |

*(Psikotes **dilaksanakan & dicatat staf HR langsung** — tanpa psikolog/asesor internal/vendor.)*

## User Persona

> Persona pengguna sistem Recruitment — grounded ke aktor & proses HRD saat ini (manual/spreadsheet + Glints).

**1. HR / HRGA Supervisor — "pemilik proses"**
- **Tujuan**: kelola seluruh pipeline efisien & terlacak; review kualifikasi, jadwalkan tahap, **laksanakan & catat psikotes**, putuskan lolos/tolak, terbitkan offer.
- **Butuh dari sistem**: satu tampilan semua pelamar + `progress`/`status`, skrining cepat, akses CV/berkas, jadwal & notifikasi.
- **Pain saat ini**: data tersebar di spreadsheet + Glints; manual; sulit melacak status & kandidat "nyangkut".

**2. SPV / Kepala Departemen — "pengaju & pewawancara teknis"**
- **Tujuan**: dapat kandidat sesuai kebutuhan teknis posisinya, cepat.
- **Butuh**: ajukan requisition + isi kualifikasi; lihat pelamar untuk posisinya; beri nilai User Interview & Technical Test.
- **Pain**: approval lama; tak tahu progress lamaran.

**3. Direktur — "pemberi persetujuan"**
- **Tujuan**: kontrol penambahan karyawan.
- **Butuh**: approve requisition ringkas (justifikasi + kualifikasi), idealnya dari mobile.
- **Pain**: tanda tangan manual di form kertas.

**4. Kandidat / Pelamar (eksternal, tanpa akun ERP) — "pencari kerja"**
- **Tujuan**: melamar mudah & tahu kabar tiap tahap.
- **Butuh**: lamar via Glints/portal, upload CV/berkas, notifikasi tiap tahap (Email → WA) termasuk hasil akhir.
- **Pain**: tak dapat kabar / lama menunggu tanpa kepastian.

## Model Data

`recruitment-service` memiliki database sendiri (`recruitment_db`), collection utama:

- `job_requisition` — permintaan posisi (**Form Permintaan Karyawan**): departemen, jumlah karyawan sekarang, jumlah dibutuhkan, posisi, **jenis permintaan (penambahan/penggantian)**, alasan, **kualifikasi/persyaratan** (usia, jenis kelamin, pendidikan, pengalaman, kualifikasi, tugas & tanggung jawab, tanggal mulai), status approval (**HR review kualifikasi → Direktur setuju**)
- `job_posting` — lowongan (posisi, deskripsi, sumber/channel, status buka/tutup)
- `candidate` — pelamar (field = **rekaman HRD saat ini**): tanggal melamar, posisi dilamar, **sumber informasi lowongan**, nama lengkap, jenis kelamin, **alamat domisili & alamat KTP**, tempat & tanggal lahir, **no. HP/WA**, pendidikan terakhir + jurusan + nama institusi (PT/sekolah) + **IPK / rata-rata UN**, **motivasi melamar**, **berkas lamaran & portofolio** (upload → [[Microservices - File Service]]/MinIO), pengalaman kerja terakhir (posisi/jabatan + nama perusahaan + durasi), serta **catatan**. Pelacakan pipeline via field `progress` & `status` (enum di bawah). Sejalan dgn kolom Glints & Form Permintaan Karyawan
  - `progress` (tahap — **rekaman HRD**; **Psikotes** = tahap baru/to-be): `CV Screening → HR Interview → User Interview → Technical Test (skill) → Final Interview → Background Check → Psikotes → Offering → Hired → Onboarding`
  - `status` (keadaan di tahap): `In Progress · Scheduled · Pending · Hold · Hired · Rejected · Withdrawn · Buffer`
- `screening_result` — hasil screening **manual** HR (lanjut/reject + alasan, waktu); field skor/rekomendasi **AI = TBD (fase lanjut)**
- `interview` — sesi interview (kandidat, tahap: HR / User / Final, pewawancara, skor, catatan)
- `technical_test_result` — hasil **Technical Test (tes skill)** per kandidat (skor/penilaian, penilai, waktu)
- `psychotest` — penugasan tes ke kandidat (jenis tes, mode online/manual, jadwal, status pelaksanaan)
- `psychotest_result` — hasil psikotes (skor per-aspek, rekomendasi/interpretasi, **report PDF di MinIO**, penilai = **staf HR**, waktu); bank soal untuk mode online **TBD**
- `background_check` — hasil **Background Check** (status, temuan/catatan, waktu)
- `offer` — penawaran (kandidat, detail, status accept/decline)

**Master & form builder (adopsi ERPGo — ✅ Fase A–E; detail di [[Microservices - Recruitment Service]]):**
- `job_type` / `candidate_source` / `interview_type` — lookup (name, is_active) untuk klasifikasi lowongan, sumber pelamar, jenis interview
- `job_location` — master lokasi kerja (name, remote_work, alamat, city/state/country/postal_code, status); dipakai dropdown Location di `job_posting`
- ~~`onboarding_checklist` + `checklist_item` + `onboarding_progress`~~ — **dihapus 2026-07-18** (template checklist onboarding + instance per-kandidat; dead code — komponen FE tak pernah dirender)
- `onboarding_review` + `onboarding_review_response` (⚠️ #493) — sesi **Performance Review Onboarding** (masa evaluasi): peserta (**karyawan masa evaluasi**, `employment_type` "PKWT (Evaluasi)"), jadwal, penilai, 7 rating + 3 uraian per penilai, keputusan status
- `job_posting` **diperkaya**: job_type/location/branch, number_of_positions, priority, min/max experience & salary, application_deadline, is_featured, toggle show_* (profile/resume/cover), required_skills, description/requirements/benefits/terms_condition (HTML). *(Toggle `ask_gender`/`ask_date_of_birth` dibuang #503/#358 — jenis_kelamin & tanggal_lahir kini SELALU wajib pelamar.)*
- `candidate` **diperkaya**: source_id, country, profile_image/cover_letter (MinIO), expected/current_salary, notice_period, portfolio_url, linkedin_url, education, **`employee_id`** (terisi saat kandidat Hired dikonversi jadi karyawan)

> **Custom Questions (form builder) dihapus** #486/#342 (2026-07-16): `custom_question` + `application_questions`/`custom_answers` tak ada lagi — portal karir memakai field native `candidate`.

## Masa Evaluasi & Performance Review Onboarding

*Setelah `Hired` → jadi karyawan, karyawan baru menjalani **masa evaluasi** (semacam masa percobaan). Di perusahaan, istilah "**onboarding**" merujuk ke fase ini, yang berpuncak pada sesi **Performance Review Onboarding**: peserta mempresentasikan hasil kerja, lalu **beberapa penilai** (karyawan lintas divisi, diundang HRGA) memberi penilaian; hasilnya jadi bahan HR memutuskan status.*

> ~~**Onboarding checklist per-kandidat (#492/#346)**~~ **dihapus 2026-07-18** — alat centang tugas onboarding (kontrak/dokumen/IT setup) ini **tak pernah terpakai di FE** (komponen yatim) sejak dibangun, jadi dibuang sebagai dead code (BE+FE). Masa evaluasi kini didukung **hanya** oleh Performance Review Onboarding di bawah.

**Performance Review Onboarding (⚠️ #493/#349)** — digitalisasi **Form Review Performance Masa Evaluasi** (dulu Google Form):
- **HR** menjadwalkan sesi (peserta, waktu, tempat) + menugaskan **penilai**; sistem mengirim **undangan** (inbox + email) — menggantikan undangan manual HRGA.
- **Penilai** (karyawan mana pun, identitas SSO) mengisi **7 aspek skala 1–5** (pemahaman pekerjaan, jelaskan hasil, jelaskan kendala & solusi, jawab pertanyaan, presentasi & komunikasi, kerapihan materi, profesionalisme) + **3 uraian** (kelebihan/kontribusi, yang perlu ditingkatkan, saran pengembangan).
- **HR** melihat **rekap** (rata-rata per aspek + semua uraian) lalu mencatat **keputusan status**: **Lulus / Diperpanjang / Tidak Lulus**.
- Kriteria bersifat **tetap (purpose-built)**, bukan form builder — keputusan sadar (form-builder `custom_question` sebelumnya sudah dihapus karena tak terpakai). Implementasi: [[Microservices - Recruitment Service]] & [[API - Recruitment Service]].

> **Persona penilai:** karyawan mana pun bisa diundang menilai (lintas divisi); aksesnya via menu **"Review Onboarding Saya"** (Portal Saya). Keputusan status tetap di HR.

## Arsitektur & Integrasi

- **`recruitment-service`**: Go + Fiber v2 + MongoDB, di belakang [[CORE - API Master Gateway]], auth **SSO** (lihat [[CORE - SSO Flow]]), role HR/recruitment dari `system_roles`
- **Integrasi**:
  - [[Microservices - Employee Service]] — master data posisi/departemen (`PositionTitle*`), cek duplikasi, **handoff `/onboarding/register`** saat hire
  - [[Microservices - Notification Service]] — notifikasi **internal** (approval requisition / jadwal / offer / undangan interview) via FCM + inbox; **pewawancara stage User/Final** tambahan dapat **email** (link form feedback) — lihat pipeline Interview di atas
  - **Notifikasi kandidat (eksternal)** — **Email** kanal utama: ✅ **sudah jalan** (channel Resend di [[Microservices - Notification Service]], **terverifikasi live** 2026-07-16) — email "lamaran diterima" otomatis saat melamar + email penawaran + lampiran PDF saat offer letter diunggah. Nama pengirim di inbox kandidat diatur per-service via env `RECRUITMENT_EMAIL_FROM` ("Bharata Recruitment"). **WhatsApp menyusul** (WA otomatis saat ini memakai satu nomor IT — lihat catatan teknis)
  - [[Microservices - File Service]] — penyimpanan CV/dokumen pelamar + **report PDF psikotes** (MinIO)
  - [[CORE - OCR Document Service]] — OCR CV hasil scan (untuk AI screening fase lanjut)
  - **LLM (OpenRouter)** — **AI CV screening (fase lanjut)**; reuse infra LLM yang dipakai Ideamills ([[Sales - Veo (Gemini) Implementation]])
  - **Psikotes** — modul di `recruitment-service`; mode **manual (dilaksanakan staf HR)** cukup catat hasil + lampiran via [[Microservices - File Service]], mode **online** butuh **test-engine + bank soal (TBD / fase lanjut)**; undangan jadwal via [[Microservices - Notification Service]]
  - **Glints (TapLoker)** — ATS/job-portal eksternal yang dipakai aktif (sumber pelamar utama). Pemetaan stage Glints → pipeline kita: *Chat Dimulai/Terhubung* → Screening · *Skill & Psikotes* → Technical Test (skill) + Psikotes (kita pisahkan) · *Wawancara* → Interview · *Negosiasi* → Offer · *Direkrut* → Hired · *Belum Sesuai* → Rejected. ⚠️ **Beda urutan**: Glints menaruh **Skill & Psikotes sebelum Wawancara**, sedangkan proses internal kita **psikotes setelah interview** (keputusan HRD) — perlu disadari saat memetakan dari Glints. Komunikasi kandidat saat ini lewat **chat/WA Glints**. Relasi `recruitment-service` ↔ Glints (impor/sinkron vs menggantikan) = **TBD strategis**
- **UI**: modul **Recruitment** di [[APP - Web ERP]] (HR & SPV) + **portal karir publik** untuk pelamar ✅ [[APP - Portal Karir Bharata]] — lihat lowongan, **melamar sendiri** (field native `candidate` + **satu berkas PDF gabungan maks 10 MB**), dan **cek status** via `tracking_token`. Menggantikan alur **Google Form** lama (lamaran langsung masuk pipeline, HR tak lagi memindahkan data manual)

## Keputusan (sudah disepakati HRD)

- **Kuota headcount**: **tanpa batasan** — requisition tak dicek/dibatasi kuota; "jumlah dibutuhkan" bersifat informasional.
- **Approval requisition**: SPV/atasan mengajukan + isi persyaratan → **HR (HRGA Supervisor) review kualifikasi** (sesuai / minta revisi) → **Direktur menyetujui**. (Sesuai blok tanda tangan **Form Permintaan Karyawan**.)
- **Persyaratan kandidat**: diusulkan **SPV** di requisition, **direview & difinalkan HR** jadi kriteria resmi (dipakai saat screening).
- **Melamar**: satu orang **boleh** melamar beberapa posisi; **boleh** melamar lagi setelah ditolak (tanpa jeda).
- **Screening**: **manual** dulu (HR yang memutuskan); AI hanya **asisten skor & rekomendasi** (tanpa auto-reject) bila nanti diaktifkan.
- **Interview**: multi-tahap **s/d 3×** tergantung posisi (mis. SPV).
- **Psikotes**: dilaksanakan & dicatat **staf HR langsung** (tanpa psikolog/asesor internal/vendor).
- **Urutan tahap (high-level)**: Screening → Interview → Psikotes → Offer.
- **Tahap detail (rekaman HRD)**: CV Screening → HR/User Interview → **Technical Test (tes skill)** → Final Interview → **Background Check** → **Psikotes** → Offering → Hired → Onboarding. *(Technical Test = tes skill, **terpisah dari Psikotes**; Psikotes = tahap baru setelah Background Check, sebelum Offering.)*
- **Notifikasi kandidat**: **Email dulu**, **WhatsApp menyusul** (email perlu dibangun — lihat Arsitektur & Integrasi).
- **Sumber pelamar**: kanal eksternal utama **Glints (TapLoker)** — ATS yang dipakai aktif (pemetaan stage di Arsitektur & Integrasi).
- **Data pelamar**: field mengikuti **rekaman HRD saat ini** (lihat collection `candidate`) — termasuk progress/status/catatan untuk pelacakan.

## Pertanyaan untuk HRD (masih terbuka)

> 🟡 Yang belum diputuskan, dikelompokkan per topik.

**Data pelamar** — *informasi yang dikumpulkan dari pelamar.*
- Field data pelamar **sudah ditetapkan** mengikuti **rekaman HRD saat ini** (lihat collection `candidate`). *(Catatan: ekspektasi gaji belum termasuk — perlu ditambah?)*
- Pelamar perlu **consent** pemrosesan data & dihubungi?
- Data kandidat (terutama yang ditolak) disimpan sampai kapan?
- Siapa boleh melihat data pelamar (HR semua; SPV hanya pelamar posisinya)?

**Psikotes** — *kini setelah interview, sebelum offer.*
- Mode: online (portal/tool) atau manual oleh staf HR?
- Jenis tes: kemampuan (kognitif/numerik/verbal/logika), kepribadian (DISC/Papikostick/MBTI), atau keduanya?
- Penentu lulus/tidak (ambang skor) atau bahan pertimbangan? Seberapa besar bobotnya?

**Offer & keputusan akhir**
- Siapa berhak menyetujui offer (HR / SPV / Direktur)?
- Isi surat penawaran (gaji, tunjangan, tanggal mulai, masa percobaan)? Template baku?
- Masa berlaku offer & penanganan nego?

**Notifikasi ke kandidat** — *kanal email→WA sudah diputuskan.*
- Di tahap mana saja kandidat dikabari? Yang **ditolak** dikabari (bahasa halus) atau tidak?
- Tampil **atas nama siapa** (HRD/perusahaan)? Dikirim **otomatis sistem** atau manual petugas?

> **Catatan teknis:** fitur **email sudah tersedia & terpakai** (Resend via [[Microservices - Notification Service]], terverifikasi live 2026-07-16). Pengiriman WhatsApp otomatis saat ini masih memakai **satu nomor milik IT** (bukan nomor resmi HRD).

## Rollout Bertahap

- [x] **Fase 1** — Job Requisition (approval **SPV → HR review → Direktur**) + Candidate management (data pelamar + status pipeline) — ✅ BE
- [x] **Fase 2** — Sourcing & Job Posting + **Screening manual** + **Interview** (multi-tahap) + **Psikotes (manual oleh HR)** — ✅ BE
- [x] **Fase 3** — Offer & Decision + **Onboarding handoff** (`/onboarding/register`) + **Notifikasi kandidat via Email** (Resend) — ✅ BE
- [x] **Fase A–E (adopsi ERPGo)** — master (job_type/candidate_source/interview_type/job_location) + enrich job_posting & candidate — ✅ BE (2026-07-03). *(form builder `custom_question` sempat ada lalu **dihapus** #486/#342.)*
- [x] **Portal karir publik** — [[APP - Portal Karir Bharata]]: browse lowongan (URL `slug`) → detail → **self-apply** (field native `candidate` + **berkas PDF gabungan maks 10 MB** → MinIO) → **cek status** via `tracking_token`; + email otomatis "lamaran diterima". ✅ BE (2026-07-16) & FE jalan terhadap dev — ⚠️ **belum go-live** (belum ada domain/deploy; sebagian menunggu deploy manual BE)
- [x] **Hire → Karyawan** — konversi kandidat Hired jadi data karyawan di HRIS (mode *dari kandidat*, prefill + isi sisa) + `link-employee` — ✅ BE #490 / FE #344 (2026-07-16, merged; ⚠️ deploy manual)
- [x] **Interview — feedback via link email** — pewawancara stage User/Final isi feedback lewat **email + link login-gated** (`/interview-feedback/<id>`), menggantikan menu "Interview Saya" (dihapus dari navigasi); HR pantau semua sesi via menu baru **Interviews** — ✅ BE #536 / FE #381 (2026-07-18, merged & ter-deploy dev)
- [x] **Interview — pengelolaan terpusat di menu Interviews** — buat/jadwalkan (picker kandidat aktif) + edit + hapus interview dipindah dari **detail kandidat** ke menu **Interviews**; detail kandidat jadi **read-only** untuk interview. FE-only (BE tak berubah — endpoint sudah pakai `id`) — ✅ FE `feat/interview-manage-on-menu` (2026-07-18)
- [x] ~~**Onboarding checklist per-kandidat**~~ — **DIHAPUS 2026-07-18** (dead code, komponen FE tak pernah dirender) — bekas BE #492 / FE #346
- [x] **Performance Review Onboarding (masa evaluasi)** — sesi review multi-penilai (7 rating + 3 uraian) → keputusan status — ⚠️ BE #493 / FE #349 (PR, belum merged/deploy)
- [ ] **Fase 4 (enhancement)** — **AI CV screening** (skor & rekomendasi, HR putuskan) + **WhatsApp** notifikasi kandidat
- [ ] **Fase 5 (opsional, sisa)** — **psikotes online** (test-engine + bank soal) + integrasi job board (mis. JobStreet)
- [ ] **Fase F–I (adopsi ERPGo lanjut)** — [x] interview rounds+feedback (✅ BE); ~~onboarding checklist per-kandidat #492~~ (dihapus 2026-07-18); [ ] offer letter template, career/recruitment settings

## Belum Diputuskan (TBD)

- **Strategi Glints** — `recruitment-service` mengimpor/sinkron dari Glints vs menggantikannya (Glints kini ATS eksternal utama); kini bertambah pertanyaan: posisi Glints vs **portal karir sendiri** ([[APP - Portal Karir Bharata]]) sebagai kanal utama.
- ~~**Mapping hire → data karyawan**~~ ✅ **selesai** (2026-07-16, #490/#344): HRIS "Tambah Karyawan" punya mode *dari kandidat* (prefill data kandidat, HR isi sisa) + `link-employee` menautkan kandidat ke `employee_id`. Detail: [[Microservices - Recruitment Service]].
- ~~**Onboarding checklist & Performance Review**~~ → **Performance Review Onboarding** dibangun (#493/#349); **onboarding checklist per-kandidat dihapus 2026-07-18** (dead code, komponen FE tak pernah dirender). Lihat bagian **Masa Evaluasi & Performance Review Onboarding**.
- **Sumber lowongan ganda** — situs korporat ([[APP - Website Bharata Internasional]]) punya halaman karir dengan BE sendiri; perlu diputuskan apakah diarahkan ke portal karir agar tak ada dua sumber lowongan.
- **Psikotes**: mode (online vs manual oleh HR), jenis tes & tools (kemampuan/kepribadian), ambang skor & bobot terhadap keputusan.
- **AI CV screening (fase lanjut)**: model LLM yang dipakai & penanganan CV hasil scan (OCR).
- **Offer letter**: template & approver.

## Dependensi / Dokumen Terkait

- [[HRIS - Analysis]] — sumber subsistem talent acquisition/interview/onboarding yang dipisah ke sini
- [[HRIS - Personalia]] · [[HRIS - Big Pictures]]
- [[Microservices - Recruitment Service]] — sisi implementasi service · [[API - Recruitment Service]] — endpoint
- [[APP - Portal Karir Bharata]] — portal karir publik untuk pelamar
- [[Microservices - Employee Service]] — onboarding/register & master data
- [[Microservices - Notification Service]] · [[Microservices - File Service]]
- [[APP - Web ERP]]
