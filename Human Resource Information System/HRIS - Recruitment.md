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
3. **Candidate Management** — data pelamar (CV, kontak, posisi dilamar, sumber) + status pipeline: `Applied → Screening → Interview → Offer → Hired/Rejected`
4. **Interview** — penjadwalan, **multi-tahap** (HR + hiring manager/SPV dept), scoring + catatan per tahap
5. **Offer & Decision** — keputusan + surat penawaran → kandidat accept/decline
6. **Onboarding Handoff** — saat kandidat `Hired` → buat akun karyawan via [[Microservices - Employee Service]] `POST /onboarding/register` (employee_id + temporary password) → masuk siklus karyawan aktif

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
- `candidate` — pelamar (data diri, CV, posisi dilamar, sumber, status pipeline)
- `interview` — sesi interview (kandidat, tahap, pewawancara, skor, catatan)
- `offer` — penawaran (kandidat, detail, status accept/decline)

## Arsitektur & Integrasi

- **`recruitment-service`**: Go + Fiber v2 + MongoDB, di belakang [[CORE - API Master Gateway]], auth **SSO** (lihat [[CORE - SSO Flow]]), role HR/recruitment dari `system_roles`
- **Integrasi**:
	- [[Microservices - Employee Service]] — master data posisi/departemen (`PositionTitle*`), cek duplikasi, **handoff `/onboarding/register`** saat hire
	- [[Microservices - Notification Service]] — notifikasi approval requisition, jadwal interview, offer (FCM + inbox)
	- [[Microservices - File Service]] — penyimpanan CV/dokumen pelamar (opsional)
- **UI**: modul **Recruitment** di [[APP - Web Application]] (HR & SPV); kandidat eksternal tidak butuh aplikasi

## Rollout Bertahap

- [ ] **Fase 1** — Job Requisition (approval SPV→HR) + Candidate management (data pelamar + status pipeline)
- [ ] **Fase 2** — Sourcing & Job Posting + Interview (penjadwalan + scoring multi-tahap)
- [ ] **Fase 3** — Offer & Decision + **Onboarding handoff** (integrasi `/onboarding/register`)
- [ ] **Fase 4 (opsional)** — portal pelamar eksternal / integrasi job board (mis. JobStreet)

## Belum Diputuskan (TBD)

- Approval **Direktur** untuk headcount/posisi tertentu (saat ini requisition cukup SPV→HR)
- Portal pelamar eksternal (self-apply) vs input manual oleh HR
- Integrasi job board pihak ketiga
- Format & template surat penawaran (offer letter)

## Dependensi / Dokumen Terkait

- [[HRIS - Analysis]] — sumber subsistem talent acquisition/interview/onboarding yang dipisah ke sini
- [[HRIS - Personalia]] · [[HRIS - Big Pictures]]
- [[Microservices - Employee Service]] — onboarding/register & master data
- [[Microservices - Notification Service]]
- [[APP - Web Application]]
