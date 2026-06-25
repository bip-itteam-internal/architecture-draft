## Deskripsi

*Endpoint **recruitment-service** (ATS Fase 1-3). Gateway: `/api/recruitment/*`. RBAC `system_roles["hris"]`. Grounded ke `services/recruitment/routes.go` (branch `feat/recruitment-service`).*

- **Implementasi**: [[Microservices - Recruitment Service]] · **Status**: ⚠️ BE Fase 1-3 (branch, belum merge)
- **Indeks**: [[API - Index]] · Role: `isSupervisor` (ajukan), `isHR`/`isHRSupervisor` (kelola/review), `isApprover` (Direktur/Secretary).

## Sistem
| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` · `/me` | Health / identitas (+`is_hr`) |

## Job Requisition
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST | `/requisitions` | Ajukan permintaan posisi | supervisor |
| GET | `/requisitions` · `/requisitions/:id` | List (HR semua / pengaju sendiri) / detail | auth |
| PUT | `/requisitions/:id` | Edit (saat Submitted/Revision) | pengaju |
| POST | `/requisitions/:id/resubmit` | Kirim ulang setelah revisi | pengaju |
| POST | `/requisitions/:id/hr-review` | Review kualifikasi (approve/revision) | HR supervisor |
| POST | `/requisitions/:id/director-approve` | Persetujuan final | approver |
| POST | `/requisitions/:id/reject` | Tolak | HR sup / approver |

## Job Posting
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST | `/postings` | Buka lowongan dari requisition Approved | HR |
| GET | `/postings` · `/postings/:id` | List (`?status=&requisition_id=`) / detail | auth |
| PUT/POST | `/postings/:id` · `/postings/:id/close` | Edit / tutup lowongan | HR |

## Candidate
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST/GET | `/candidates` · `/candidates/:id` | Input/list (`?posting_id=&progress=&status=`)/detail | HR |
| PUT | `/candidates/:id` · `/advance` · `/reject` · `/withdraw` | Edit / gerak tahap (maju) / tolak / undur | HR |
| POST/GET | `/candidates/:id/cv` · `/cv/preview` | Upload/preview CV (MinIO) | HR |

## Stages & Offer
| Method | Path | Fungsi | Role |
|---|---|---|---|
| POST | `/candidates/:id/screening` · `/interviews` · `/technical-test` · `/background-check` · `/psychotest` | Catat tiap tahap | HR |
| GET | `/candidates/:id/stages` | Timeline tahap kandidat | HR |
| POST | `/candidates/:id/offer` | Terbitkan offer (→ Offering) | HR supervisor |
| POST | `/candidates/:id/offer/accept` · `/offer/decline` | Respon offer | HR |
| POST | `/candidates/:id/hire` | Hire → onboarding handoff ke employee `/onboarding/register` | approver |
| GET | `/audits` | Audit log keputusan | HR admin |

## Dokumen Terkait
- [[Microservices - Recruitment Service]] · [[HRIS - Recruitment]] · [[Microservices - Employee Service]] · [[API - Index]]
