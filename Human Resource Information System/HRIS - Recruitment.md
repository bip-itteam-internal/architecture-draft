## Catatan

*Desain (to-be) subsistem **Recruitment** — mengelola **siklus depan karyawan**: dari kebutuhan posisi sampai jadi karyawan aktif. Memisahkan subsistem **Talent acquisition → Interview → On-boarding** yang sekarang menumpuk di [[HRIS - Analysis]] ke ruangnya sendiri.*

- **Status**: 🟡 Desain / Direncanakan (**belum** diimplementasi di kode)
- **Target arsitektur**: microservice `recruitment-service` baru + modul web, dengan **rollout bertahap**
- Titik singgung yang sudah ada di kode: `POST /onboarding/register` (aktivasi akun karyawan baru) di [[Microservices - Employee Service]] — menjadi handoff akhir recruitment

## Latar Belakang

* Saat ini langkah recruitment (talent acquisition, interview, onboarding) tercampur di [[HRIS - Analysis]] dan sebagian masih manual/spreadsheet.
* Tujuannya: alur formal & terlacak dari **permintaan posisi → lowongan → pelamar → interview → offer → onboarding**, terintegrasi dengan master data karyawan.

## Pipeline (End-to-End)

1. **Job Requisition** — departemen/SPV mengajukan posisi + headcount + justifikasi → approval **SPV/kepala departemen → HR** (2 tingkat, konsisten dgn pola [[HRIS - Leave Request]]) → status `Approved` → lowongan boleh dibuka
2. **Sourcing & Job Posting** — HR membuka lowongan (internal/eksternal) + mencatat **sumber pelamar** (job portal, referral, walk-in, bootcamp)
3. **Candidate Management** — data pelamar (CV, kontak, posisi dilamar, sumber) + status pipeline: `Applied → Screening → Interview → Offer → Hired/Rejected`. Tahap **Screening** dibantu **AI CV screening** (lihat bagian khusus di bawah)
4. **Interview** — penjadwalan, **multi-tahap** (HR + hiring manager/SPV dept), scoring + catatan per tahap
5. **Offer & Decision** — keputusan + surat penawaran → kandidat accept/decline
6. **Onboarding Handoff** — saat kandidat `Hired` → buat akun karyawan via [[Microservices - Employee Service]] `POST /onboarding/register` (employee_id + temporary password) → masuk siklus karyawan aktif

## Screening Awal (AI CV Screening)

*Otomasi penyaringan awal pelamar — pelamar upload CV, AI menilai kecocokan dengan kriteria posisi. **AI bersifat asisten** (skor + rekomendasi); keputusan final tetap di HR (human-in-the-loop).*

**Alur:**
1. Pelamar buka **halaman lowongan publik** → isi data + **upload CV (PDF)** → submit
2. Sistem simpan CV ke [[Microservices - File Service]] (MinIO) + buat record `candidate` (status `Applied`)
3. **AI screening otomatis**:
	- Ekstrak teks CV (PDF; fallback OCR via [[CORE - OCR Document Service]] bila CV hasil scan)
	- Ambil **kriteria dari Job Posting/Requisition** (pendidikan, pengalaman, skill; must-have/nice-to-have)
	- Kirim ke **LLM (OpenRouter)** → **skor kecocokan (%)** + breakdown per kriteria (terpenuhi/tidak + bukti dari CV) + **rekomendasi lolos/tidak** + ringkasan
4. Hasil disimpan di `candidate` (status `Screening`) beserta skor & rekomendasi AI
5. **HR review** skor + alasan → **HR putuskan** lanjut ke Interview / Reject (final di HR, bukan AI)

**Pengaman**: human-in-the-loop (tanpa auto-reject), alasan disimpan untuk audit/fairness, data pelamar (PII) disimpan aman.

## Aktor & Role

| Aktor | Peran |
|---|---|
| Pengaju / SPV departemen | Mengajukan & menyetujui Job Requisition (tingkat 1) |
| HR Recruiter | Mengelola pipeline: validasi requisition, lowongan, pelamar, jadwal, offer |
| Hiring Manager / SPV dept | Ikut interview + memberi penilaian/keputusan |
| HR | Approval requisition (tingkat 2), penerbitan offer |
| Direktur | Approval headcount tertentu *(opsional — lihat TBD)* |
| Kandidat | Eksternal — **tanpa akun ERP** (data dikelola HR) |

## Model Data

`recruitment-service` memiliki database sendiri (`recruitment_db`), collection utama:

- `job_requisition` — permintaan posisi (dept, headcount, justifikasi, status approval SPV→HR)
- `job_posting` — lowongan (posisi, deskripsi, sumber/channel, status buka/tutup)
- `candidate` — pelamar (data diri, CV di MinIO, posisi dilamar, sumber, status pipeline)
- `screening_result` — hasil AI CV screening (skor, per-kriteria, rekomendasi, alasan, model, waktu)
- `interview` — sesi interview (kandidat, tahap, pewawancara, skor, catatan)
- `offer` — penawaran (kandidat, detail, status accept/decline)

## Arsitektur & Integrasi

- **`recruitment-service`**: Go + Fiber v2 + MongoDB, di belakang [[CORE - API Master Gateway]], auth **SSO** (lihat [[CORE - SSO Flow]]), role HR/recruitment dari `system_roles`
- **Integrasi**:
	- [[Microservices - Employee Service]] — master data posisi/departemen (`PositionTitle*`), cek duplikasi, **handoff `/onboarding/register`** saat hire
	- [[Microservices - Notification Service]] — notifikasi approval requisition, jadwal interview, offer (FCM + inbox)
	- [[Microservices - File Service]] — penyimpanan CV/dokumen pelamar (MinIO)
	- **LLM (OpenRouter)** — AI CV screening (analisis CV vs kriteria); reuse infra LLM yang dipakai Ideamills ([[Sales - Veo (Gemini) Implementation]])
- **UI**: modul **Recruitment** di [[APP - Web Application]] (HR & SPV) + **portal lowongan publik** untuk pelamar (self-apply + upload CV)

## Rollout Bertahap

- [ ] **Fase 1** — Job Requisition (approval SPV→HR) + Candidate management (data pelamar + status pipeline)
- [ ] **Fase 2** — Sourcing & Job Posting + Interview (penjadwalan + scoring multi-tahap)
- [ ] **Fase 3** — Offer & Decision + **Onboarding handoff** (integrasi `/onboarding/register`)
- [ ] **Fase 4** — **portal lamaran publik (self-apply) + AI CV screening** (skor & rekomendasi, HR putuskan)
- [ ] **Fase 5 (opsional)** — integrasi job board pihak ketiga (mis. JobStreet)

## Belum Diputuskan (TBD)

- Approval **Direktur** untuk headcount/posisi tertentu (saat ini requisition cukup SPV→HR)
- ~~Portal pelamar eksternal vs input manual HR~~ → **diputuskan: portal self-apply (pelamar upload CV) + AI screening**
- **AI screening**: ambang skor, model LLM yang dipakai, penanganan CV hasil scan (OCR)
- Integrasi job board pihak ketiga
- Format & template surat penawaran (offer letter)

## Dependensi / Dokumen Terkait

- [[HRIS - Analysis]] — sumber subsistem talent acquisition/interview/onboarding yang dipisah ke sini
- [[HRIS - Personalia]] · [[HRIS - Big Pictures]]
- [[Microservices - Employee Service]] — onboarding/register & master data
- [[Microservices - Notification Service]]
- [[APP - Web Application]]
