---
tags: [hris, recruitment, roadmap]
---

# HRIS - Recruitment Roadmap (Adopsi ERPGo)

> 🟡 **Konsep / Roadmap** — pemetaan fitur modul Recruitment **ERPGo SaaS (WorkDo)** terhadap implementasi **bip-erp** saat ini + rekomendasi apa yang layak diadopsi, **disesuaikan dengan kondisi & keputusan perusahaan**. Bagian "Status" grounded ke kode (`services/recruitment` + `erp-frontend`); bagian "Rekomendasi" bersifat usulan (belum diputuskan kecuali ditandai).

## Deskripsi

*ERPGo Recruitment punya 12 sub-menu + dashboard, dikelompokkan 4 fase: konfigurasi → sourcing → seleksi → offer & onboarding. Sebagian besar sudah kita adopsi (Fase A–E), beberapa sengaja **tidak** diadopsi (keputusan sadar), dan beberapa jadi kandidat implementasi berikutnya.*

- **Sumber implementasi:** [[Microservices - Recruitment Service]] · [[API - Recruitment Service]] · FE [[APP - Web ERP]] · portal [[APP - Portal Karir Bharata]]
- **Konsep & alur:** [[HRIS - Recruitment]]
- **Legenda status:** ✅ ada · ⚠️ parsial · ❌ belum ada · ⛔ sengaja tak diadopsi
- **Legenda rekomendasi:** 🟢 prioritas · 🟡 pertimbangkan · ⏭️ skip · 🔮 future (selaras kapabilitas AI)

## Kondisi Aktual (As-Is)

*Grounded ke `services/recruitment/routes.go` (semua endpoint) + model + menu FE. **Menu FE nyata:** Recruitment (HR) = Job Requisitions · Job Postings · Candidates · Interviews · Candidate Onboarding · System Setup. Portal SPV = Job Requisitions (ajukan). Link login-gated tanpa sidebar: `/interview-feedback/[id]`, `/onboarding-review/[employeeId]`. Portal publik: [[APP - Portal Karir Bharata]].*

1. **Job Requisition** — **approval 3-tingkat**: SPV ajukan (`Submitted`) → HR review (`HR Reviewed`/`Revision Requested`) → **Direktur** (`Approved`) → `Posted`; + reject + resubmit. Kualifikasi (usia/gender/pendidikan/pengalaman/tugas/tanggal mulai). Capability flags per-aksi.
2. **Job Posting** — dibuka dari requisition Approved; `Open/Closed`, **slug** URL publik; field kaya (job_type/location/branch/positions/priority/experience/salary/deadline/featured/show_*/skills/description/requirements/benefits/terms HTML).
3. **Candidate** — pipeline **`progress` (10 tahap) + `status` (9 keadaan)** + `tracking_token`; field lengkap + salary expected/current, notice, portfolio/linkedin, source; berkas **CV + profile image + cover letter** (MinIO); aksi create/update/**advance**/reject/withdraw/**link-employee**; **apply publik + tracking**. Flags can_issue_offer/upload_letter/respond/hire.
4. **Stage records (timeline seleksi, 5 jenis)** — `GET /stages` + PUT/DELETE per record: **Screening** (lanjut/reject) · **Interview** (dari menu Interviews: HR/User/Final, panel, rounds per-lowongan, feedback rating+rekomendasi + link email) · **Technical Test** (skill/score/notes — **manual**) · **Background Check** (clear/issue) · **Psikotes** (jenis/mode/scores/interpretasi + **report PDF**; `online` placeholder).
5. **Offer & Hire** — issue (HR supervisor) → upload **letter PDF** → accept/decline → **hire** (Direktur/approver). Status `Issued/Accepted/Declined`. → link-employee jadi karyawan.
6. **"Onboarding" = masa evaluasi** — **Performance Review Onboarding** (multi-penilai 7 rating + 3 uraian → Lulus/Diperpanjang/Tidak Lulus, penilai isi via link). **Bukan** checklist tugas.
7. **Master & Settings (System Setup)** — master `job_type`/`candidate_source`/`interview_type`/`job_location`; **Kelola Template Email** per-event (preview/test-send/reset); **audit log** (HR admin).

**Sudah dihapus (jangan dihitung ada):** Custom Questions (#486), Onboarding Checklist template + per-kandidat (2026-07-18), toggle `ask_gender`/`ask_date_of_birth`/`ask_country`.

## Pemetaan Fitur

### Dashboard (Talent Acquisition Hub)
| Fitur ERPGo | Status bip-erp | Rekomendasi |
|---|---|---|
| KPI cards (Total Candidates, Active Jobs, Interviews, Onboarded) | ✅ **dibangun** — Total Kandidat · Lowongan Open · Interviews (total) · Onboarded (kandidat tahap Onboarding) | ✅ FE `feat/recruitment-dashboard` |
| Hiring Funnel (Applications→…→Hired) | ✅ **dibangun** — kumulatif "mencapai ≥ tahap" + **persentase** (agregasi `progress`) | ✅ |
| Status Overview — donut Candidate Status | ✅ **dibangun** (donut per `status`) | ✅ |
| Status Overview — donut Onboarding Progress | ✅ **dibangun** (dari Performance Review masa-evaluasi: Scheduled + outcome Lulus/Diperpanjang/Tidak Lulus) | ✅ |
| Interview Calendar | ✅ **dibangun** (grid bulan + navigasi, dari `scheduled_at`) | ✅ |
| Copy Career Portal + QR | ❌ belum (portal ada [[APP - Portal Karir Bharata]]) | 🟡 tombol salin link + QR (opsional) |

### Fase 1 — Konfigurasi / Master Data
| Fitur ERPGo | Status bip-erp | Rekomendasi |
|---|---|---|
| Job Locations | ✅ `job_location` (`/locations`) | — |
| Custom Questions (form builder lamaran) | ⛔ **dihapus** (BE #486/FE #342) — portal pakai field native `candidate` | ⏭️ jangan re-add (keputusan sadar) |
| System Setup → Job Types / Candidate Sources / Interview Types | ✅ master lookups | — |
| System Setup → Onboarding Checklists | ⛔ **dihapus 2026-07-18** (dead code, tak dipakai FE) | ⏭️ lihat "Onboarding" di bawah |
| System Setup → Brand Settings + konten portal (About, Application Tips, What Happens Next, Need Help, Tracking FAQ) | ❌ konten portal karir sebagian hardcoded | 🟡 config konten portal via System Setup (HR ubah tanpa deploy) |
| System Setup → Offer Letter Template | ❌ offer letter = **upload PDF manual** (`letter_object` MinIO), bukan template | 🟡 template + generate PDF (lihat Offers) |
| *(di luar ERPGo)* **Kelola Template Email** per-event | ✅ bip-erp punya (settings: list/get/put/preview/test-send/reset) | — kelebihan bip-erp |

### Fase 2 — Sourcing
| Fitur ERPGo | Status bip-erp | Rekomendasi |
|---|---|---|
| Job Postings (kaya: type/location/branch/positions/priority/experience/salary/deadline/featured/show_*/skills/requirements/benefits/terms HTML) | ✅ lengkap (`job_posting` diperkaya) | — |
| Job Posting → **AI assist** konten (title/requirements/benefits) | ❌ | 🔮 selaras kapabilitas AI internal (sejajar "AI CV screening" di roadmap) |
| Job Posting → Application Questions | ⛔ ikut Custom Questions dihapus | ⏭️ skip |
| Candidates (Tracking ID, source, field lengkap, CV/cover/profile MinIO, apply publik) | ✅ (`candidate` + `tracking_token`) | — |
| Candidates → ubah **Status inline** dari daftar | ⚠️ ubah tahap via detail kandidat / `advance` | 🟢 quick-win: ubah status/tahap inline dari list |

### Fase 3 — Seleksi
| Fitur ERPGo | Status bip-erp | Rekomendasi |
|---|---|---|
| Interview Rounds (per lowongan, sequence, status) | ✅ `interview_round` (#498) | — |
| Interviews (jadwal, tipe, durasi, lokasi) | ✅ dikelola dari **menu Interviews** (#385) | — |
| Interviews → **Status lifecycle** (Scheduled/Completed/Cancelled/No-show) | ⛔ sengaja tanpa status di v1 | 🟡 revisit: Completed/Cancelled/No-show berguna untuk dashboard & funnel |
| Interview Feedback (rating + rekomendasi, panel) | ✅ + link email pewawancara (#536) | — |
| Candidate Assessments (Score% + Pass/Fail/Pending) | ⚠️ **terpisah**: Technical Test (skill/score/notes) + Psikotes (mode/scores/interpretasi/report PDF), **tanpa status hasil terpadu**; keduanya **catat manual** (tes di luar sistem) | 🟡 tambah **status hasil (Lulus/Tidak/Pending)**; opsi tes online (bank soal/upload jawaban) — lihat catatan Tes |

### Fase 4 — Offer & Onboarding
| Fitur ERPGo | Status bip-erp | Rekomendasi |
|---|---|---|
| Offers (Candidate/Position/Salary/Start/Status) | ✅ `offer` (Issued→Accepted/Declined) + letter PDF upload/preview | — |
| Offer → status kaya (Draft/Sent/Negotiating/Expired) + **Expiration Date** | ❌ hanya Issued/Accepted/Declined, tanpa kedaluwarsa | 🟢 tambah **tanggal kedaluwarsa** + state "Dikirim" (kecil, berguna) |
| Offer → **Approval Status** (Pending/Approved) sebelum kirim | ⚠️ tak ada field status approval di offer, TAPI ada **role-gating**: issue oleh **HR supervisor** → **hire oleh Direktur/approver**. Approval "berat" ada di **requisition (3-tingkat)** di hulu | 🟡 opsional: field approval eksplisit di offer bila butuh gate tambahan sebelum kirim ke kandidat |
| Offer → salary increment | ❌ | ⏭️ low value |
| Offer Letter **Template** generator | ❌ upload PDF manual | 🟡 template + generate (butuh konten di System Setup) |
| Checklist Items + Candidate Onboarding + **Buddy** | ⛔ checklist **dihapus**; buddy ❌ tak ada | ⏭️ skip — model perusahaan beda: "onboarding" = **masa evaluasi** → **Performance Review Onboarding** (#493), bukan checklist tugas |

## Sengaja TIDAK diadopsi (keputusan perusahaan)

- **Custom Questions / form-builder lamaran** — dihapus (#486); portal karir memakai field `candidate` native. Menambah lagi = mundur.
- **Onboarding Checklist + Buddy system** — checklist dibuang sebagai dead code (2026-07-18). Di perusahaan, **"onboarding" = masa evaluasi** karyawan baru yang berpuncak pada **Performance Review Onboarding** (multi-penilai → keputusan Lulus/Diperpanjang/Tidak Lulus), bukan daftar tugas + mentor. Kalau kelak butuh alat operasional checklist HRD, itu inisiatif terpisah.

## Kandidat Implementasi (prioritas, disesuaikan perusahaan)

**🟢 Prioritas — data sudah ada, nilai tinggi:**
1. ~~**Dashboard Rekrutmen**~~ ✅ **SELESAI 2026-07-18** (FE `feat/recruitment-dashboard`) — KPI (Total Kandidat/Lowongan Open/Interviews/Onboarded) + hiring funnel (kumulatif + %) + donut status kandidat + donut onboarding progress + **kalender interview**. Reuse recharts+StatSummary, agregasi FE (BE tak diubah). Sisa opsional: Copy Portal + QR.
2. **Quick wins:** ubah status/tahap kandidat **inline** dari daftar; **tanggal kedaluwarsa** + state "Dikirim" pada Offer.

**🟡 Pertimbangkan — nilai jelas, effort sedang:**
3. **Offer Letter template** (+ konten di System Setup); field status approval eksplisit di offer = **opsional** (role-gating issue→hire sudah ada; approval berat ada di requisition).
4. **Status hasil asesmen** (Lulus/Tidak/Pending) untuk Technical Test & Psikotes; opsi **tes online** (bank soal / kirim tugas + upload jawaban) — menjawab pertanyaan pengembangan Tes.
5. **Interview status lifecycle** (Completed/Cancelled/No-show) — mendukung dashboard/funnel.
6. **Config konten Career Portal** (About/Tips/What-Happens-Next/FAQ) via System Setup.

**🔮 Future — selaras kapabilitas AI internal:**
7. **AI assist** konten lowongan + **AI CV screening** (sudah tercatat di roadmap [[HRIS - Recruitment]]).

## Dependensi & Dokumen Terkait
- [[HRIS - Recruitment]] — konsep, alur, model data, backlog
- [[Microservices - Recruitment Service]] — implementasi BE (adopsi ERPGo Fase A–E, increment)
- [[API - Recruitment Service]] — endpoint
- [[APP - Portal Karir Bharata]] — portal karir publik
- [[APP - Web ERP]] — FE recruitment (menu, panduan in-app)
- [[HRIS - Key Performance Index]] — pola KPI/dashboard yang bisa di-reuse
