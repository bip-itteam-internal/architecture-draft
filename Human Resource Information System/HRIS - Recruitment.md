## Deskripsi

*Desain (to-be) subsistem **Recruitment** — mengelola **siklus depan karyawan**: dari kebutuhan posisi sampai jadi karyawan aktif. Memisahkan subsistem **Talent acquisition → Interview → On-boarding** yang sekarang menumpuk di [[HRIS - Analysis]] ke ruangnya sendiri.*

- **Status**: ⚠️ **BE sebagian diimplementasi** — Fase 1-3 + adopsi struktur ERPGo (Fase A–F) live di [[Microservices - Recruitment Service]]; **portal karir publik sudah ada** ([[APP - Portal Karir Bharata]] — pelamar melamar sendiri + kirim berkas; **cek status lamaran DIHAPUS** 2026-07-24). **psikotes online (Kraepelin) sudah dibangun** — [[HRIS - Psikotes Kraepelin]]. Menyusul: AI CV screening, WhatsApp kandidat, integrasi job board. 🟡 **Rekrutmen lintas perusahaan: kode lengkap di branch, BELUM merge maupun deploy** (diukur 2026-09-11, lihat bagian "Rekrutmen Lintas Perusahaan" di bawah dan [[ADR - 0092 Rekrutmen Lintas Perusahaan lewat Paket Izin]]) · 🟡 **Alur kerja HR (titik putus dibuka, kotak Langkah berikutnya, tombol Setujui offer dari `can_approve`): kode lengkap di branch, BELUM merge maupun deploy** (2026-09-12, lihat bagian "Alur Kerja HR" di bawah)
- **Target arsitektur**: microservice `recruitment-service` baru ([[Microservices - Recruitment Service]]) + modul web, dengan **rollout bertahap**
- Titik singgung yang sudah ada di kode: `POST /onboarding/register` (aktivasi akun karyawan baru) di [[Microservices - Employee Service]]. ⚠️ **Bukan handoff hire yang bekerja**: aktivasinya mewajibkan username, password, dan PIN baru yang diisi karyawan sendiri, jadi hire tak pernah berhasil memanggilnya (lihat langkah 8 pipeline di bawah)

## Latar Belakang

* Saat ini langkah recruitment (talent acquisition, interview, onboarding) tercampur di [[HRIS - Analysis]] dan sebagian masih manual/spreadsheet.
* Tujuannya: alur formal & terlacak dari **permintaan posisi → lowongan → pelamar → screening → interview → psikotes → offer → onboarding**, terintegrasi dengan master data karyawan.

## Pipeline (End-to-End)

![[Recruitment Pipeline.excalidraw]]

1. **Job Requisition** — SPV/atasan mengajukan posisi via **Form Permintaan Karyawan** (field: departemen, jumlah karyawan sekarang, jumlah dibutuhkan, posisi, **jenis permintaan: penambahan/penggantian**, alasan, **persyaratan/kualifikasi**: usia, jenis kelamin, pendidikan, pengalaman, kualifikasi, tugas & tanggung jawab, tanggal mulai). Alur: **SPV mengisi kualifikasi** → **SPV HRD review kualifikasi lalu menyetujui** (atau minta revisi) → status `Approved` → lowongan boleh dibuka. **Satu tahap persetujuan** sejak 2026-07-22: tahap Direktur dihapus, SPV HRD adalah pemberi persetujuan final. **Tanpa batasan kuota** (jumlah dibutuhkan bersifat informasional, bukan cap). 🟡 **(erp-frontend `feat/rekrutmen-buka-alur`, belum merge)** di detail requisition, SPV HRD memutus lewat tiga tombol langsung: **Setujui** (konfirmasi menyebut posisi + departemen, catatan opsional), **Minta Revisi** (catatan wajib, hanya status `Submitted`), dan **Tolak**; dulu satu tombol HR Review membuka dialog berisi pilihan. Filter status halaman HR dan Portal Saya kini satu sumber, dan requisition lama di `HR Reviewed` berlabel "Menunggu Keputusan (alur lama)", bukan "Disetujui HR"
2. **Sourcing & Job Posting** — HR membuka lowongan + mencatat **sumber pelamar**. Kanal eksternal utama saat ini: **Glints (TapLoker)** — ATS/job-portal yang dipakai aktif (PT Bharata terverifikasi: pasang lowongan, Pertanyaan Skrining, akses CV, chat WA); plus referral, walk-in, bootcamp
3. **Candidate Management** — data pelamar (CV, kontak, posisi dilamar, sumber) + pelacakan pipeline via field **`progress`** (tahap) & **`status`** (keadaan), enum mengikuti **rekaman HRD** (lihat Model Data)
4. **Screening (manual)** — HR menyaring CV/data pelamar **manual** terhadap kriteria posisi (lihat bagian khusus di bawah); **AI CV screening** direncanakan sebagai enhancement fase lanjut
5. **Interview** — penjadwalan, **multi-tahap**: HR Interview → User Interview → **Technical Test (tes skill — terpisah dari psikotes)** → Final Interview (jumlah tahap tergantung posisi, mis. SPV) — HR + hiring manager/SPV dept; scoring + catatan per tahap. Lolos → **Background Check**. **Orkestrasi (✅ #498/#356):** sesi bisa ditautkan ke **babak** (`round_id`). **Feedback via link email (✅ #536/#381, 2026-07-18):** untuk stage **User & Final**, tiap pewawancara di panel (snapshot nama+email dikirim FE saat menjadwalkan, terpisah dari `Lokasi`) menerima **email undangan branded** (jadwal, lokasi/link meeting, tombol **"Buka Form Feedback"**) menuju halaman **login-gated tanpa sidebar** (`/interview-feedback/<id>`) tempat ia mengisi feedback sendiri (3 rating + rekomendasi, editable/upsert) — **menggantikan** menu **"Interview Saya"** (dihapus dari navigasi Portal Saya; komponen & endpoint `/interviews/assigned` tetap ada tapi dormant). Stage **HR**: tanpa email — HR isi feedback dari menu **Interviews** (dialog Lihat). **Kandidat** juga menerima email undangan jadwal (**semua stage**, tanpa link form). **Pengelolaan interview terpusat di menu Interviews (✅ FE):** jadwalkan (pilih kandidat aktif) + edit + hapus + salin link + lihat/isi feedback (terisi/total), semua dari sini; **detail kandidat menampilkan interview read-only** (jenis tahap lain — screening/tes/background check — tetap dicatat dari detail kandidat). Belum: kalender/reminder ICS, auto-advance tahap dari hasil.
6. **Psikotes / Tes keahlian** — ✅ **terimplementasi sebagai babak bertipe tes**, bukan modul tersendiri. Psikotest dan Technical Test adalah dua babak ber-`form_type: "test"` di katalog babak; keduanya **tidak dijadwalkan** lewat Proses Seleksi, melainkan direkam sebagai **form hasil per kandidat** di tab "Hasil Tes" pada detail kandidat: `result` (Pass/Fail/Pending) + `score` opsional + catatan. Menyimpan hasil lewat form itu **memindahkan tahap kandidat ke babak itu** dan menderivasi status (Pass → `Pending`, Fail/Pending → `Hold`). 🟡 **(bip-erp `feat/recruitment-alur-kerja-hr` + erp-frontend `feat/rekrutmen-buka-alur`, belum merge)** menerbitkan psikotes (terbit maupun terbit ulang) juga memindah progress ke babak Psikotest tanpa menyentuh status, dan tab Hasil Tes kini menawarkan **Kirim Psikotes** untuk kandidat yang belum punya sesi (dulu tombol pertamanya hanya ada di sel Progress, dan hanya saat progress sudah Psikotest)
	- ✅ **Psikotes-nya sendiri kini dikerjakan DI DALAM sistem**, mode **online self-service** yang dulu ditandai TBD: HR menerbitkan sesi, kandidat mengerjakan **Kraepelin** lewat magic link tanpa login, server menilai empat kategori (kecepatan/ketelitian/keajegan/ketahanan), hasilnya masuk sebagai `result: Pending` di babak Psikotest, dengan `score` **hanya untuk sesi yang dituntaskan** sejak tahap nol (T0, bip-erp #1828, merged 2026-09-10; terbukti lewat gateway dev hari itu, live di prod 2026-09-11): sesi yang ditinggalkan atau kedaluwarsa menulis baris tanpa skor, karena skornya Rendah secara mekanis. Rincian: **[[HRIS - Psikotes Kraepelin]]**. **Technical Test** tetap dikerjakan di luar aplikasi dan hanya hasilnya yang diketik HR
	- 🟡 **Perluasan ke multi-jenis sudah diputuskan 2026-09-10**: katalog tipe tes, bank soal, dan paket tes menjadi master data yang dikelola HRD, dijalankan tiga mesin penilaian yang tetap berupa kode. Lihat [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]] dan [[HRIS - Bank Soal dan Paket Psikotes]]. Ini menjawab TBD lama "jenis tes dan tools" di bagian Pertanyaan untuk HRD
	- ⚠️ **Sisa gap vs desain di dokumen ini:** **report PDF psikotes** masih belum ada tempatnya (laporan hanya tampil di layar HR, tak ada lampiran tersimpan), dan **bank soal untuk jenis tes selain Kraepelin** (DISC/CFIT) belum ada. Ambang lulus/tidak tetap keputusan HR, tak dikodekan — sistem sengaja berhenti di `Pending`
	- ⚠️ **Gap urutan:** dokumen ini (dan keputusan HRD di bawah) menempatkan Psikotes **setelah** Background Check, sebelum Offering. Kode menaruh **Psikotest di urutan 3**, sebelum User Interview (`seed.go`). Urutannya bisa diubah HR dari katalog babak, jadi ini soal **data seed**, bukan kode — tapi keadaan awalnya memang tidak sesuai keputusan
7. **Offer & Decision** — keputusan + surat penawaran → kandidat accept/decline
8. **Hire → Karyawan** — saat kandidat `Hired`, HR membuat **data karyawan** di HRIS "Tambah Karyawan" (mode *dari kandidat* — data kandidat diprefill, HR isi sisanya) via [[Microservices - Employee Service]]; kandidat lalu **ditautkan** ke `employee_id` (`PUT /candidates/:id/link-employee`, progress→Onboarding).
	- ⚠️ **Koreksi (diukur 2026-09-12): hire TIDAK mengaktifkan akun.** `POST /candidates/:id/hire` hanya meneruskan ke `POST /onboarding/register` bila body membawa `employee_id` (`services/recruitment/offer_handlers.go` `hireCandidate`), dan endpoint itu mewajibkan username, password, **dan PIN baru** (`services/employee/main.go:3133`) yang tak pernah dikirim hire, jadi jalur itu selalu ditolak 400 dan hire ikut gagal. Akun diaktifkan **karyawan sendiri** lewat [[APP - MyBharata]].
	- 🟡 **(erp-frontend `feat/rekrutmen-buka-alur`, belum merge)** dialog Hire tak lagi meminta Employee ID dan password sementara (body kosong, BE tak diubah), dan tab Offer di detail kandidat menampilkan tombol **Buat data karyawan** untuk kandidat Hired yang belum tertaut: tombol itu membuka HRIS > Karyawan dengan modal Tambah Karyawan langsung di mode dari kandidat (`/hris/employee?dari_kandidat=<id>`). Kandidat yang belum Hired, sudah tertaut, atau tak ditemukan jatuh ke layar awal modal dengan pesan. Perusahaan modal diturunkan dari `company_id` kandidat (kosong = BIP), bukan dipatok BIP; perusahaan kandidat yang tak ada di daftar perusahaan juga jatuh ke layar awal dengan pesan (diselaraskan dengan rekrutmen lintas perusahaan saat `main` digabung ke branch itu, 2026-09-12).
9. **Masa Evaluasi & Performance Review Onboarding** — karyawan baru jalani masa evaluasi, berpuncak pada sesi **Performance Review** (presentasi → penilai lintas divisi menilai → keputusan status) — lihat bagian khusus di bawah. *(Onboarding checklist per-kandidat #492 dihapus 2026-07-18 — dead code.)* ⚠️ **Catatan itu tak lagi lengkap:** checklist onboarding **dibangun ulang 2026-07-26** sebagai template + instance per karyawan baru dengan penugasan PIC lintas tim (rincian di [[Microservices - Recruitment Service]]). PIC mengerjakan tugasnya di [[APP - MyBharata]]; 🟡 notifikasinya dirapikan di bip-erp `feat/recruitment-alur-kerja-hr` (belum merge), lihat §Alur Kerja HR.

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
| **HR / HRGA Supervisor (SPV HRD)** | **Review kualifikasi + menyetujui/menolak** requisition — pemberi persetujuan **final** sejak 2026-07-22; finalkan kriteria; kelola pipeline (lowongan, pelamar, jadwal incl. psikotes, input hasil); penerbitan offer |
| **Pewawancara** (hiring manager / SPV dept) | Ikut interview & penilaian (multi-tahap s/d 3×) |
| **Kandidat** | Eksternal — **tanpa akun ERP** (data dikelola HR) |

*(Psikotes **dilaksanakan & dicatat staf HR langsung** — tanpa psikolog/asesor internal/vendor.)*

> ⚠️ **Keputusan di atas tidak lagi mencerminkan sistem (2026-09-10).** Psikotes Kraepelin yang terbangun dikerjakan kandidat **sendiri** lewat tautan tanpa login, tanpa pendamping HR dan tanpa jejak tempat pengerjaan. Keputusan penggantinya belum diambil; pertanyaannya tercatat di [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]] §Belum Diputuskan.

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

> **Persona Direktur dihapus 2026-07-22.** Tahap persetujuan Direktur dibuang dari alur requisition (PR #609/#466); kontrol penambahan karyawan kini sepenuhnya di SPV HRD (persona 1). Requisition lama yang terlanjur disetujui Direktur tetap menyimpan riwayatnya di field `director_approver`.

**3. Kandidat / Pelamar (eksternal, tanpa akun ERP) — "pencari kerja"**
- **Tujuan**: melamar mudah & tahu kabar tiap tahap.
- **Butuh**: lamar via Glints/portal, upload CV/berkas, notifikasi tiap tahap (Email → WA) termasuk hasil akhir.
- **Pain**: tak dapat kabar / lama menunggu tanpa kepastian.

## Model Data

`recruitment-service` memiliki database sendiri (`recruitment_db`), collection utama:

- `job_requisition` — permintaan posisi (**Form Permintaan Karyawan**): departemen, jumlah karyawan sekarang, jumlah dibutuhkan, posisi, **jenis permintaan (penambahan/penggantian)**, alasan, **kualifikasi/persyaratan** (usia, jenis kelamin, pendidikan, pengalaman, kualifikasi, tugas & tanggung jawab, tanggal mulai), status approval (**HR review kualifikasi → Direktur setuju**)
- `job_posting` — lowongan (posisi, deskripsi, sumber/channel, status buka/tutup)
- `candidate` — pelamar (field = **rekaman HRD saat ini**): tanggal melamar, posisi dilamar, **sumber informasi lowongan**, nama lengkap, jenis kelamin, **alamat domisili & alamat KTP**, tempat & tanggal lahir, **no. HP/WA**, pendidikan terakhir + jurusan + nama institusi (PT/sekolah) + **IPK / rata-rata UN**, **motivasi melamar**, **berkas lamaran & portofolio** (upload → [[Microservices - File Service]]/MinIO), pengalaman kerja terakhir (posisi/jabatan + nama perusahaan + durasi), serta **catatan**. Pelacakan pipeline via field `progress` & `status` (enum di bawah). Sejalan dgn kolom Glints & Form Permintaan Karyawan
  - `progress` (tahap) — **bukan enum tetap**: isinya **nama babak** dari katalog `interview_round`, ditambah dua fase non-babak yang dipaku di kode (`Offering`, `Onboarding`). Urutan baku hasil seed: `CV Screening → HR Interview → Psikotest → User Interview → Technical Test → Final Interview → Background Check → Offering → Hired/Onboarding`. Karena HR boleh menambah/menonaktifkan/mengurutkan ulang babak, daftar ini **keadaan awal, bukan kontrak**
  - `status` (keadaan di tahap): `In Progress · Scheduled · Pending · Hold · Buffer · Hired · Rejected · Withdrawn`
- `interview` — sesi interview (kandidat, babak `round_id`, panel pewawancara, jadwal, lokasi/meeting link); penilaian per pewawancara di `interview_feedback`
- `interview_round` — **katalog babak GLOBAL** (`name`, `sequence_number`, `status`, `sends_feedback_link`, **`form_type`**). `form_type` inilah yang menentukan sebuah babak **dijadwalkan** (interview) atau **hanya dicatat hasilnya** (tes / background check). Lowongan memilih babak lewat `round_ids[]`
- `candidate_test_result` — **hasil babak bertipe tes**; Psikotest & Technical Test memakai **satu jalur yang sama**: `round_id`, `score` (opsional), `result` (Pass/Fail/Pending), `notes`, `assessed_by`. Satu hasil per (kandidat, babak), upsert
- `background_check` — hasil **Background Check** (verifikasi per item, referensi, SLIK, keputusan, catatan HR)
- `psikotes_session` — **sesi psikotes online** (satu kandidat satu kali per babak): `jenis` (`kraepelin`), `token` magic link, `status` (pending/in_progress/finished), `config`+`soal`+`hasil` bertipe bebas, `selesai_karena` (tuntas/ditinggalkan/kedaluwarsa). Rincian: **[[HRIS - Psikotes Kraepelin]]**
- ⚠️ **Nama koleksi lama yang TIDAK ada di kode** (diperiksa `origin/main` 2026-09-10): `screening_result` (screening jadi keputusan manual tanpa koleksi sendiri), `technical_test_result` (melebur ke `candidate_test_result`), `psychotest` & `psychotest_result` — **fungsinya ada**, tapi berwujud `psikotes_session` + `candidate_test_result`, bukan dua koleksi terpisah dengan nama itu. Skor per-aspek + interpretasi **sudah ada** untuk Kraepelin (empat kategori + kesimpulan, tampil di laporan individual HR). Yang benar-benar belum terealisasi dari desain lama tinggal **report PDF di MinIO**. Rincian implementasi: [[Microservices - Recruitment Service]]
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

> ~~**Onboarding checklist per-kandidat (#492/#346)**~~ **dihapus 2026-07-18** — alat centang tugas onboarding (kontrak/dokumen/IT setup) ini **tak pernah terpakai di FE** (komponen yatim) sejak dibangun, jadi dibuang sebagai dead code (BE+FE). Masa evaluasi kini didukung **hanya** oleh Performance Review Onboarding di bawah. ⚠️ Kalimat itu basi sejak **2026-07-26**: checklist onboarding dibangun ulang dengan model baru (template + instance per karyawan baru + penugasan PIC lintas tim, lihat increment "Onboarding Checklist (rebuild)" di [[Microservices - Recruitment Service]]), dan PIC mengerjakan tugasnya di [[APP - MyBharata]].

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
- **UI**: modul **Recruitment** di [[APP - Web ERP]] (HR & SPV) + **portal karir publik** untuk pelamar ✅ [[APP - Portal Karir Bharata]] — lihat lowongan, **melamar sendiri** (field native `candidate` + **satu berkas PDF gabungan maks 10 MB**). ⛔ **Cek status lamaran via `tracking_token` sudah DIHAPUS** (2026-07-24) — pelamar kini hanya menerima email konfirmasi, tanpa cara memeriksa kemajuan lamarannya sendiri. Menggantikan alur **Google Form** lama (lamaran langsung masuk pipeline, HR tak lagi memindahkan data manual)

## Alur Kerja HR (branch, belum merge)

> 🟡 **Kode lengkap di branch, BELUM merge maupun deploy** (2026-09-12): bip-erp
> `feat/recruitment-alur-kerja-hr`, erp-frontend `feat/rekrutmen-buka-alur` (PR-A) dan
> `feat/rekrutmen-langkah-berikutnya` (PR-B, di atas PR-A). Rincian layar: [[APP - Web ERP]]
> (modul Recruitment). Sisi service: [[Microservices - Recruitment Service]] ·
> [[API - Recruitment Service]].

*QA dari sudut pandang HR rekrutmen (telusur kode 2026-09-11) menemukan pekerjaan satu kandidat
tersebar di delapan tempat, dan tiga tombol langkah berikutnya menolak kandidat sampai HR mengubah
Progress manual: Jadwalkan Sesi hanya menerima kelompok Interview padahal pelamar baru selalu CV
Screening, Buat Offer hanya menerima progress Offering padahal progress baru pindah ke Offering saat
offer dikirim, dan Kirim Tes pertama hanya muncul saat progress sudah Psikotest. Perubahan ini
membuka titik putus itu, meringkas yang rumit, dan menambah kotak "Langkah berikutnya".*

**Keputusan user:**
1. (2026-09-11) Tugas onboarding PIC hanya lewat MyBharata: pesan notifikasi dibuat netral, kategori
   `task-assigned`, `app_route` `/tugas-onboarding`; menu web tidak dikembalikan. Ketukan notifikasi
   di ponsel tetap membuka halaman Notifikasi, karena `task-assigned` tak dipetakan ke rute di pemeta
   rute notifikasi MyBharata (jatuh ke `default`).
2. (2026-09-11) Kotak Langkah berikutnya dikerjakan sebagai PR kedua.
3. (2026-09-11) Isian Tipe Assessment dan tab Tipe Asesmen dibuang; data backend dibiarkan.
4. (2026-09-11) Nilai status kandidat tidak diubah (paritas spreadsheet HRD). Dua arti `Pending`
   (sesi tanpa jadwal, atau penilaian Lolos) diatasi kotak Langkah berikutnya yang membaca keputusan
   penilaian, bukan status.
5. (2026-09-11) Seluruh self-service rekrutmen (penilaian interview, review masa evaluasi, tugas PIC,
   pengajuan kebutuhan karyawan) pindah ke satu halaman Rekrutmen di [[APP - MyBharata]] sebagai
   task berikutnya.
6. (2026-09-12) Tombol Setujui offer mengikuti flag `can_approve` dari backend, bukan aturan peran
   yang disalin ke frontend.

**Alur pengguna: HR membawa pelamar baru sampai jadi karyawan**
1. Detail kandidat (progress CV Screening) → kotak Langkah berikutnya **Jadwalkan HR Interview**
   (PR-B), atau Proses Seleksi > Jadwalkan Sesi yang kini menerima kandidat CV Screening tanpa
   mengubah Progress.
2. Sesi dibuat → kotak menyebut "menunggu penilaian" dan menautkan ke detail sesi Proses Seleksi.
3. Penilaian Lolos → tahap Psikotest: **Kirim Psikotes** (dari kotak atau tab Hasil Tes) → progress
   pindah ke Psikotest otomatis.
4. Hasil tes dan Background Check diputus di tab masing-masing.
5. **Buat Offer** (dari kotak, atau menu Offers tanpa mengubah Progress) → **Setujui** (SPV HRD) →
   **Kirim** (konfirmasi menyebut nama kandidat) → **Catat Jawaban**.
6. **Hire** di tab Offer (tanpa isian akun) → **Buat data karyawan** → HRIS > Karyawan, modal
   langsung di mode dari kandidat → kandidat tertaut ke karyawan.

**SPV HRD memutus requisition:** detail requisition → **Setujui** (konfirmasi menyebut posisi +
departemen) / **Minta Revisi** (catatan wajib) / **Tolak** → Buka Lowongan.

**Titik putus yang diterima:** mengetuk notifikasi tugas onboarding membuka halaman Notifikasi,
bukan layar tugas; yang mengantar PIC adalah teks pesannya.

**Di luar lingkup:** halaman Rekrutmen self-service di MyBharata (task berikutnya); tombol Kembali
detail requisition untuk atasan (pengajuan kebutuhan karyawan ikut pindah ke MyBharata); pencegahan
offer ganda di backend (aturan "offer aktif" kini dihitung frontend); gambar panduan (PNG
Excalidraw).

## Rekrutmen Lintas Perusahaan

> 🟡 **Kode lengkap di branch, BELUM merge maupun deploy** (diukur 2026-09-11): bip-erp
> `feat/recruitment-lintas-perusahaan`, erp-frontend `feat/recruitment-lintas-perusahaan`.
> Keputusan arsitektur: [[ADR - 0092 Rekrutmen Lintas Perusahaan lewat Paket Izin]]. Landasan:
> [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] (`company_id` = batas data),
> [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] +
> [[ADR - 0080 Permission Set Menggerbangi Pengajuan Requisition Lintas-Departemen]] (wewenang
> khusus lewat paket izin yang dipasang sadar ke posisi).

*Sebelum fitur ini, `recruitment-service` sama sekali tak mengenal perusahaan (28 koleksi tanpa
`company_id`) dan satu-satunya jalan lintas perusahaan adalah admin pusat. Kebutuhannya: satu
recruiter (karyawan BIP) menangani rekrutmen SEMUA perusahaan grup, sementara pengguna lain (SPV
departemen, HR biasa) tetap hanya melihat perusahaannya sendiri.*

**Keputusan user (2026-09-11):**
1. Recruiter lintas perusahaan menangani SEMUA perusahaan grup lewat SATU paket izin baru
   (`recruitment.cross_company`, paket `recruitment_lintas_perusahaan`, berisi tepat satu izin;
   `shared-library/common/catalog_recruitment.go:216-223`); pengguna lain tetap terkunci ke
   perusahaannya sendiri.
2. Requisition untuk perusahaan B boleh diajukan **SPV B** (perusahaan sendiri, perilaku lama)
   **DAN** recruiter lintas atas nama B.
3. Satu portal karir untuk seluruh perusahaan grup; tiap lowongan menyebut nama perusahaan
   perekrut; halaman legal per perusahaan **TBD**, lihat [[APP - Portal Karir Bharata]].
4. Email kandidat menyebut nama perusahaan dari `master_company` (dibaca lewat cache, bukan
   disalin, lihat [[REF - Kepemilikan Data]]); logo tetap SATU untuk semua perusahaan, bukan per
   perusahaan.
5. Saat `/review`: paket juga dipasang ke posisi SPV HRD penyetuju (lihat "Penyetuju" di bawah);
   notifikasi requisition menyebut nama perusahaan; daftar karyawan perusahaan lain yang dibuka
   lewat izin ini disempitkan (`username`/`phone_number`/`photo` dikosongkan), detail di
   [[Microservices - Employee Service]] dan [[CORE - RBAC dan Permission Set]].

### Persona

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| **Recruiter Lintas Perusahaan** | Staf/SPV di departemen Human Resource BIP, sudah memegang paket recruitment biasa (mis. pelaksana/penyetuju) DITAMBAH paket baru `recruitment_lintas_perusahaan` | Melihat & mengelola requisition, lowongan, kandidat, MPP, onboarding SEMUA perusahaan grup; membaca referensi perusahaan lain di employee-service (departemen, posisi, daftar karyawan, proyeksi disempitkan); satu-satunya hak yang izin ini buka SENDIRI adalah mengajukan requisition atas nama perusahaan lain | Web ERP (desktop, HR) |
| **SPV Perusahaan Lain** (mis. CV Elit) | Atasan/kepala departemen perusahaan B, TANPA paket lintas | Mengajukan requisition untuk departemennya sendiri di perusahaan B (perilaku lama, `company_id` otomatis dari identitasnya); tak melihat perusahaan lain | Web ERP / Portal Saya |
| **SPV HRD Penyetuju (BIP)** | Posisi penyetuju requisition/offer (wewenangnya dari tier `hris` supervisor/admin atau paket penyetuju recruitment) | Wajib DITAMBAHI paket `recruitment_lintas_perusahaan` supaya bisa membuka & menyetujui requisition perusahaan lain (tanpanya notifikasi tetap tiba tapi membuka/menyetujuinya dibalas 404, lihat "Penyetuju" di bawah) | Web ERP |

⚠️ **Izin `recruitment.cross_company` bersifat ADITIF, bukan pengganti.** Ia melebarkan cakupan
PERUSAHAAN dari izin pipeline (`recruitment.view`/`work`/`approve`/`manage`) yang sudah dipegang
posisi itu; pemegangnya tanpa izin pipeline tetap tak bisa membuka daftar apa pun
(`shared-library/common/catalog_recruitment.go:69-84`). Satu-satunya hak yang ia buka SENDIRI
adalah `POST /requisitions` atas nama perusahaan lain, karena perusahaan tujuan bisa belum punya
atasan yang memakai ERP (`services/recruitment/rbac.go:89-97` `requireAtasanAtauLintasPerusahaan`).
Paket ini SENGAJA tidak masuk `RecruitmentTierDefault` maupun paket admin bawaan
(`catalog_recruitment.go:61-84`). Kalau ikut, setiap pemegang tier `hris:supervisor`/`admin`
otomatis mendapat wewenang lintas perusahaan tanpa pernah diputuskan siapa pun, jebakan yang sama
dengan yang dicatat [[ADR - 0080 Permission Set Menggerbangi Pengajuan Requisition Lintas-Departemen]].

### Alur Pengguna

**Alur A (SPV perusahaan B butuh orang, recruiter di BIP yang memproses, jalur biasa)**
1. SPV B di Portal Saya > Job Requisitions > Buat → tercatat perusahaan B otomatis (identitas SPV
   B sendiri, bukan pilihan) → berikutnya: review di Recruitment > Requisitions (notif inbox ke
   SPV HRD, perilaku lama).
2. Recruiter/SPV HRD lintas di Requisitions: kolom + filter Perusahaan → setujui → SPV B
   menerima notifikasi disetujui (perilaku lama, tak berubah).
3. Recruiter di Postings > Buat → pilih requisition B → perusahaan ikut requisition (read-only)
   → tampil di portal karir dengan nama perusahaan B.
4. Pelamar di `career.bharatainternasional.com` → lamar → email "lamaran diterima" atas nama B.
5. Recruiter di Candidates (filter B) → seleksi → Interviews: pemilih pewawancara menampilkan
   karyawan B + karyawan sendiri, berlabel perusahaan.
6. Offer → hire → HRIS > Tambah Karyawan → pilih perusahaan B → "Dari kandidat" (hanya
   menampilkan kandidat B) → karyawan dibuat di B, kandidat tertaut.
7. Onboarding checklist (pilih perusahaan B) dan review onboarding (peserta dipilih dari karyawan
   B; perusahaan sesi mengikuti peserta) → karyawan B.

Selesai ketika: karyawan baru tercatat di perusahaan B dan onboarding-nya berjalan.

**Alur B (recruiter mengajukan requisition atas nama B, B belum punya SPV di ERP)**
1. Recruiter di Portal Saya > Job Requisitions > Buat → pilih Perusahaan B → departemen/posisi
   milik B → Simpan → "Tercatat di perusahaan B, departemen X". Dari sini alurnya menyatu dengan
   langkah 2 Alur A.

**Titik putus yang tersisa (dicatat, tidak ditutup fitur ini):**
- Langkah 6 (dari detail kandidat ke Tambah Karyawan di HRIS) pindah modul tanpa tautan dari
  detail kandidat. Celah **LAMA**, bukan akibat fitur ini. 🟡 Ditutup di erp-frontend
  `feat/rekrutmen-buka-alur` (belum merge): tombol **Buat data karyawan** di tab Offer, lihat
  §Alur Kerja HR. Risiko penggabungannya sudah ditutup 2026-09-12 saat `main` (yang memuat fitur
  ini) digabung ke branch itu: tautan `?dari_kandidat=` kini memakai perusahaan dari `company_id`
  kandidat (kosong = BIP), bukan BIP yang dipatok, sehingga kandidat perusahaan B dimulai di B
  (`create-employee/index.tsx`, dijaga test yang merah bila perusahaannya dipatok lagi).
- Recruiter yang paketnya belum dipasang, atau sudah dipasang tapi belum login ulang, hanya
  melihat perusahaannya sendiri TANPA petunjuk bahwa ia seharusnya melihat lebih. Lihat
  [[Microservices - Recruitment Service]] (catatan deploy) untuk urutan pemasangan paket dan
  gerbang verifikasinya.

### Penyetuju requisition tetap satu tim di BIP

Notifikasi requisition baru dikirim ke SEMUA pemegang `role_system=hris`
(`role_value=supervisor|admin`), tanpa parameter perusahaan
(`services/recruitment/notify.go:56-76` `notifyHRSupervisors`), jadi penerimanya tetap tim SPV
HRD BIP walau requisition-nya untuk perusahaan lain. Pesannya
(`services/recruitment/requisition_notify.go:11-26`) menyebut nama perusahaan tujuan supaya
requisition "CV Elit" tidak terbaca sebagai kebutuhan departemen bernama sama di BIP.

Konsekuensinya: paket `recruitment_lintas_perusahaan` **wajib** juga dipasang ke posisi SPV HRD
penyetuju, bukan hanya ke recruiter (tanpanya notifikasi tiba tapi membuka/menyetujui requisition
perusahaan lain dibalas 404, karena penjaga per-ID
(`bolehBukaRequisition`/`requisitionTerjangkau`, `services/recruitment/perusahaan.go:208-232`)
menolaknya). Deploy fitur ini karena itu wajib mengukur dulu siapa penyetujunya sebelum memasang
paket, lihat [[Microservices - Recruitment Service]].

### Belum Diputuskan / Di Luar Lingkup (fitur ini)

- **Halaman legal / pengendali data pelamar per perusahaan**: TBD. Satu portal, tiap lowongan
  menyebut perusahaan perekrutnya, tapi syarat & ketentuan serta kebijakan privasi masih SATU
  untuk seluruh grup, lihat [[APP - Portal Karir Bharata]].
- **Logo per perusahaan**: tidak dibangun (keputusan user "nama saja"); `master_company` belum
  punya field logo.
- **Filter perusahaan di portal karir publik**: belum diminta, label nama perekrut di tiap
  lowongan dianggap cukup.
- **Perusahaan tertentu per recruiter** (mis. recruiter hanya menangani sebagian perusahaan
  grup): tidak ada; keputusan user: semua perusahaan grup.
- **Master/katalog rekrutmen** (babak interview, psikotes, lookup, template email, lokasi) tetap
  GLOBAL, tak ikut perusahaan. Belum ada pemakai yang butuh versi berbeda.

## Keputusan (sudah disepakati HRD)

- **Kuota headcount**: **tanpa batasan** — requisition tak dicek/dibatasi kuota; "jumlah dibutuhkan" bersifat informasional.
- **Approval requisition**: SPV/atasan mengajukan + isi persyaratan → **SPV HRD review kualifikasi lalu menyetujui** (atau minta revisi). Satu tahap, sejak 2026-07-22.
  > ⚠️ **Gap dengan form fisik:** alur lama dua tahap dibuat mengikuti blok tanda tangan **Form Permintaan Karyawan** yang memuat kolom Direktur. Setelah tahap Direktur dihapus di sistem, form kertasnya **belum diselaraskan**. Perlu diputuskan HRD: revisi form fisik, atau kolom Direktur dibiarkan kosong/dihapus.
- **Persyaratan kandidat**: diusulkan **SPV** di requisition, **direview & difinalkan HR** jadi kriteria resmi (dipakai saat screening).
- **Melamar**: satu orang **boleh** melamar beberapa posisi; **boleh** melamar lagi setelah ditolak (tanpa jeda).
- **Screening**: **manual** dulu (HR yang memutuskan); AI hanya **asisten skor & rekomendasi** (tanpa auto-reject) bila nanti diaktifkan.
- **Interview**: multi-tahap **s/d 3×** tergantung posisi (mis. SPV).
- **Psikotes**: dilaksanakan & dicatat **staf HR langsung** (tanpa psikolog/asesor internal/vendor).
  > ⚠️ **Gap dengan sistem (2026-09-10):** psikotes yang terbangun dikerjakan kandidat **sendiri** lewat tautan tanpa login, tanpa pendamping HR dan tanpa jejak tempat pengerjaan. Keputusan ini belum dicabut maupun ditegaskan ulang; pertanyaannya tercatat di [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]] §Belum Diputuskan.
- **Urutan tahap (high-level)**: Screening → Interview → Psikotes → Offer.
- **Tahap detail (rekaman HRD)**: CV Screening → HR/User Interview → **Technical Test (tes skill)** → Final Interview → **Background Check** → **Psikotes** → Offering → Hired → Onboarding. *(Technical Test = tes skill, **terpisah dari Psikotes**; Psikotes = tahap baru setelah Background Check, sebelum Offering.)*
  > ⚠️ **Gap dengan sistem (2026-09-10):** seed babak menaruh **Psikotest di urutan 3** (sebelum User Interview), bukan setelah Background Check. Technical Test dan Psikotest memang tetap dua babak terpisah, sesuai keputusan. Karena urutan babak adalah **data yang bisa disunting HR** di katalog babak, penyelarasannya tidak menuntut perubahan kode — cukup atur ulang `sequence_number`, dan itu belum dilakukan.
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

- [x] **Fase 1** — Job Requisition (approval **SPV → SPV HRD**; alur awal memakai tahap Direktur, dihapus 2026-07-22) + Candidate management (data pelamar + status pipeline) — ✅ BE
- [x] **Fase 2** — Sourcing & Job Posting + **Screening manual** + **Interview** (multi-tahap) + **Psikotes (manual oleh HR)** — ✅ BE
- [x] **Fase 3** — Offer & Decision + **Onboarding handoff** (`/onboarding/register`) + **Notifikasi kandidat via Email** (Resend) — ✅ BE
- [x] **Fase A–E (adopsi ERPGo)** — master (job_type/candidate_source/interview_type/job_location) + enrich job_posting & candidate — ✅ BE (2026-07-03). *(form builder `custom_question` sempat ada lalu **dihapus** #486/#342.)*
- [x] **Portal karir publik** — [[APP - Portal Karir Bharata]]: browse lowongan (URL `slug`) → detail → **self-apply** (field native `candidate` + **berkas PDF gabungan maks 10 MB** → MinIO) → halaman sukses; + email otomatis "lamaran diterima". *(Cek status via `tracking_token` sempat ada lalu dihapus 2026-07-24.)* ✅ BE (2026-07-16) & FE jalan; **live di prod** (`career.bharatainternasional.com`, container `career-bharata`; terukur 2026-09-11 lewat halaman psikotes)
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
- [[HRIS - Recruitment Roadmap (Adopsi ERPGo)]] — pemetaan fitur ERPGo vs implementasi + kandidat pengembangan
- [[APP - Portal Karir Bharata]] — portal karir publik untuk pelamar
- [[Microservices - Employee Service]] — onboarding/register & master data
- [[Microservices - Notification Service]] · [[Microservices - File Service]]
- [[APP - Web ERP]]
- [[ADR - 0092 Rekrutmen Lintas Perusahaan lewat Paket Izin]] (rekrutmen lintas perusahaan, 🟡 branch, belum merge) · [[REF - Kepemilikan Data]] · [[CORE - RBAC dan Permission Set]]
