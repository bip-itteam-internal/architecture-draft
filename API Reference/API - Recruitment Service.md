## Deskripsi

*Endpoint **recruitment-service** (ATS Fase 1-3 + adopsi struktur ERPGo Fase A–E + portal karir publik). Gateway: `/api/recruitment/*` (auth) & `/public/recruitment/*` (publik, tanpa JWT). RBAC `system_roles["hris"]`. Grounded ke `services/recruitment/routes.go` (branch `main`).*

- **Implementasi**: [[Microservices - Recruitment Service]] · **Status**: ⚠️ BE Fase 1-3 + master ERPGo (A–F) + portal publik (browse/apply/track) + requisition se-departemen — increment 2026-07-16 deployed & terverifikasi live di dev. **Custom Questions dihapus** (#486/#342). **hire→karyawan** (endpoint `link-employee`, PR #490) **merged, belum deploy**.
- **Konsumen publik**: [[APP - Portal Karir Bharata]]
- **Indeks**: [[API - Index]] · Role: `isSupervisor` (ajukan), `isHR`/`isHRSupervisor` (kelola/review), `isApprover` (Direktur/Secretary).

## Sistem
| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` · `/me` | Health / identitas (+`is_hr`) |

## Job Requisition
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST | `/requisitions` | Ajukan permintaan posisi. **`department` diambil dari identitas pengaju, bukan body** (anti-spoof, PR #478) | supervisor |
| GET | `/requisitions` · `/requisitions/:id` | List (HR semua / pengaju sendiri) / detail. **`?scope=department`** → SPV lihat requisition **se-departemen** (departemen dari identitas gateway; detail juga izinkan SPV se-departemen) — PR #470 | auth |
| PUT | `/requisitions/:id` | Edit (saat Submitted/Revision). Departemen **dipertahankan** (edit tak memindahkan requisition) | pengaju |
| POST | `/requisitions/:id/resubmit` | Kirim ulang setelah revisi | pengaju |
| POST | `/requisitions/:id/hr-review` | Review kualifikasi (approve/revision) | HR supervisor |
| POST | `/requisitions/:id/director-approve` | Persetujuan final | approver |
| POST | `/requisitions/:id/reject` | Tolak | HR sup / approver |

## Job Posting
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST | `/postings` | Buka lowongan dari requisition Approved (+ generate `slug` unik dari title/posisi, untuk URL portal publik) | HR |
| GET | `/postings` · `/postings/:id` | List (`?status=&requisition_id=`) / detail | auth |
| PUT/POST | `/postings/:id` · `/postings/:id/close` | Edit / tutup lowongan | HR |

## Candidate
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST/GET | `/candidates` · `/candidates/:id` | Input/list (`?posting_id=&progress=&status=`)/detail | HR |
| PUT | `/candidates/:id` · `/advance` · `/reject` · `/withdraw` | Edit / gerak tahap (maju) / tolak / undur | HR |
| PUT | `/candidates/:id/link-employee` | Tautkan kandidat **Hired** ke karyawan yang dibuat di HRIS (wajib Hired & belum tertaut → set `employee_id`, `progress`→Onboarding, audit; cegah konversi ganda) — PR #490 | HR |
| POST/GET | `/candidates/:id/cv` · `/cv/preview` | Upload/preview CV (MinIO) | HR |
| POST/GET | `/candidates/:id/profile-image[/preview]` · `/cover-letter[/preview]` | Upload/preview foto profil & cover letter (MinIO) | HR |

## Stages & Offer
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST | `/candidates/:id/screening` · `/interviews` · `/technical-test` · `/background-check` · `/psychotest` | Catat tiap tahap | HR |
| GET | `/candidates/:id/stages` | Timeline tahap kandidat | HR |
| POST | `/candidates/:id/offer` | Terbitkan offer (→ Offering) | HR supervisor |
| POST | `/candidates/:id/offer/letter` | Unggah surat penawaran PDF (MinIO) + email kandidat | HR supervisor |
| POST | `/candidates/:id/offer/accept` · `/offer/decline` | Respon offer | HR |
| POST | `/candidates/:id/hire` | Hire (butuh offer Accepted) → set `Hired` + onboarding handoff `/onboarding/register` (aktivasi akun). Pembuatan **data karyawan** dilakukan terpisah di HRIS "Tambah Karyawan" (dari kandidat) → `link-employee` | approver |
| GET | `/audits` | Audit log keputusan | HR admin |

## Interview Rounds & Feedback (Fase F — adopsi ERPGo)
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST/GET | `/postings/:id/rounds` | Definisi/daftar babak interview per lowongan | HR |
| PUT/DELETE | `/rounds/:id` | Ubah / hapus babak | HR |
| POST/GET | `/interviews/:id/feedback` | Kirim/lihat penilaian terstruktur (rating 1-5 + recommendation) | HR |

## Master & Form Builder (adopsi ERPGo)
| Method | Path | Fungsi | Role |
|---|---|---|---|
| CRUD | `/masters/job-types` · `/masters/candidate-sources` · `/masters/interview-types` | Lookup (list/get/create/update/delete) | HR |
| CRUD | `/locations` | Master lokasi kerja (list/get/create/update/delete) | HR |
| CRUD | `/checklists` · `/checklists/:id/items` | Template onboarding checklist + item (list/get/create/update/delete) | HR |

> **Custom Questions dihapus** (BE #486 / FE #342, 2026-07-16): endpoint `/questions` (form builder) + field `application_questions`/`custom_answers` **tak ada lagi** — portal karir memakai field native `candidate`. BSON lama diabaikan saat decode (tanpa migrasi).

## Onboarding Checklist per-kandidat (⚠️ PR #492/#346 — belum merged/deploy)
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST | `/candidates/:id/onboarding` | Mulai onboarding kandidat **Hired**: body `{checklist_id}` → salin item **aktif** template jadi `onboarding_progress` (snapshot). Cegah dobel | HR |
| GET | `/candidates/:id/onboarding` | Progress onboarding kandidat (body `null` bila belum mulai) | HR |
| PUT | `/candidates/:id/onboarding/items/:itemId` | Tandai item selesai/belum `{done}`; `completed_at` saat semua item **wajib** selesai | HR |

## Performance Review Onboarding (⚠️ PR #493/#349 — belum merged/deploy)
> Digitalisasi Form Review Performance Masa Evaluasi (dulu Google Form). Peserta = **karyawan masa evaluasi** (`employment_type` "PKWT (Evaluasi)"); penilai = karyawan mana pun (identitas SSO). Peserta tak boleh menilai dirinya sendiri. Kriteria 7+3 **konstanta** (purpose-built, bukan form builder).

| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST | `/onboarding-reviews` | HR buat sesi `{employee_id, peserta_name, peserta_position, peserta_department, scheduled_at, location, reviewers[]}` (peserta = karyawan masa evaluasi; peserta di-skip bila ikut `reviewers[]`) → undang penilai (inbox + email best-effort) | HR |
| GET | `/onboarding-reviews` | Daftar sesi (`?status=&employee_id=`) | HR |
| GET | `/onboarding-reviews/:id` | Detail + **rekap** (semua jawaban penilai) | HR |
| PUT | `/onboarding-reviews/:id/decide` | Keputusan `{outcome, note}` — outcome `Lulus`/`Diperpanjang`/`Tidak Lulus` → status `Decided` | HR |
| GET | `/onboarding-reviews/assigned` | Sesi yang ditugaskan ke saya (+ jawaban saya) | auth (penilai) |
| POST | `/onboarding-reviews/:id/response` | Submit/ubah jawaban `{ratings(7×1-5), strengths, improvements, recommendations}` — boleh edit sampai sesi `Decided` | auth (penilai) |

## Publik (tanpa JWT — via gateway `/public/recruitment/*`)
| Method | Path (gateway) | Fungsi |
|---|---|---|
| GET | `/public/recruitment/postings` | Daftar lowongan Open (featured dulu) — tiap item memuat **`slug`** |
| GET | `/public/recruitment/postings/:id` | Detail lowongan. **`:id` menerima `slug` ATAU ObjectID** (dicoba ObjectID dulu; gagal parse → lookup by `slug`). Respons + `slug` & **`job_type`** (nama, hasil resolve `job_type_id` → master `job_types`) |
| POST | `/public/recruitment/apply` | Pelamar mendaftar sendiri (email + `posisi_dilamar` wajib) → respons `tracking_token` + `track_url`. **Dua bentuk body**: (a) JSON, atau (b) **`multipart/form-data`**: field `data` = JSON kandidat + file **`berkas`** = PDF **maks 10 MB** → MinIO `recruitment/cv/<candidate_id>/berkas.pdf` → set `cv_object` (HR buka via `GET /candidates/:id/cv/preview`) |
| GET | `/public/recruitment/track/:token` | Cek status lamaran via **tracking_token** (bukan `_id`) — curated: progress/status label + stepper |

> **Catatan kontrak `/apply`:** `posisi_dilamar` **wajib** dan **tidak** diisi server dari posting — divalidasi lebih dulu, jadi klien harus mengirimnya walau sudah kirim `posting_id`. `tanggal_lahir` = **RFC3339** (samakan dengan model employee agar mapping saat hire tidak perlu isi ulang — lihat [[HRIS - Recruitment]]). Upload berkas **backward-compatible**: body JSON tanpa file tetap diterima; berkas non-PDF / >10 MB → 400.

> **Catatan deploy (per 2026-07-16):** `slug`, `job_type` (resolve master), dan upload `berkas` **semua sudah live & terverifikasi** di dev (E2E multipart+berkas → `cv_object` → HR preview PDF valid). Deploy bip-erp **manual** (lihat [[Microservices - Recruitment Service]]).

## Dokumen Terkait
- [[Microservices - Recruitment Service]] · [[HRIS - Recruitment]] · [[Microservices - Employee Service]] · [[CORE - API Master Gateway]] · [[API - Index]]
