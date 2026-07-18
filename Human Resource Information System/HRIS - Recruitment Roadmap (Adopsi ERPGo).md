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

## Pemetaan Fitur

### Dashboard (Talent Acquisition Hub)
| Fitur ERPGo | Status bip-erp | Rekomendasi |
|---|---|---|
| KPI cards (Total Candidates, Active Jobs, Interviews, Onboarded) | ❌ tak ada dashboard rekrutmen khusus (data-nya ada: candidate/posting/interview) | 🟢 **Dashboard Rekrutmen** — reuse pola KPI HRIS ([[HRIS - Key Performance Index]]) |
| Hiring Funnel (Applications→Shortlisted→Interviewed→Hired) | ❌ | 🟢 funnel dari agregasi `progress` (10 tahap pipeline) |
| Status Overview (donut Candidate Status) | ❌ | 🟢 breakdown per `status` |
| Interview Calendar | ⚠️ ada list menu **Interviews** (bukan kalender) | 🟡 tampilan kalender (nice-to-have) |
| Copy Career Portal + QR | ⚠️ portal ada ([[APP - Portal Karir Bharata]]); tombol share/QR di app ❌ | 🟡 tombol salin link + QR |

### Fase 1 — Konfigurasi / Master Data
| Fitur ERPGo | Status bip-erp | Rekomendasi |
|---|---|---|
| Job Locations | ✅ `job_location` (`/locations`) | — |
| Custom Questions (form builder lamaran) | ⛔ **dihapus** (BE #486/FE #342) — portal pakai field native `candidate` | ⏭️ jangan re-add (keputusan sadar) |
| System Setup → Job Types / Candidate Sources / Interview Types | ✅ master lookups | — |
| System Setup → Onboarding Checklists | ⛔ **dihapus 2026-07-18** (dead code, tak dipakai FE) | ⏭️ lihat "Onboarding" di bawah |
| System Setup → Brand Settings + konten portal (About, Application Tips, What Happens Next, Need Help, Tracking FAQ) | ❌ konten portal karir sebagian hardcoded | 🟡 config konten portal via System Setup (HR ubah tanpa deploy) |
| System Setup → Offer Letter Template | ❌ offer letter = **upload PDF manual** (`letter_object` MinIO), bukan template | 🟡 template + generate PDF (lihat Offers) |

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
| Offer → **Approval Status** (Pending/Approved) sebelum kirim | ❌ approval ada di **requisition**, bukan offer | 🟡 offer approval pakai approver existing (SPV→hris supervisor→Secretary) |
| Offer → salary increment | ❌ | ⏭️ low value |
| Offer Letter **Template** generator | ❌ upload PDF manual | 🟡 template + generate (butuh konten di System Setup) |
| Checklist Items + Candidate Onboarding + **Buddy** | ⛔ checklist **dihapus**; buddy ❌ tak ada | ⏭️ skip — model perusahaan beda: "onboarding" = **masa evaluasi** → **Performance Review Onboarding** (#493), bukan checklist tugas |

## Sengaja TIDAK diadopsi (keputusan perusahaan)

- **Custom Questions / form-builder lamaran** — dihapus (#486); portal karir memakai field `candidate` native. Menambah lagi = mundur.
- **Onboarding Checklist + Buddy system** — checklist dibuang sebagai dead code (2026-07-18). Di perusahaan, **"onboarding" = masa evaluasi** karyawan baru yang berpuncak pada **Performance Review Onboarding** (multi-penilai → keputusan Lulus/Diperpanjang/Tidak Lulus), bukan daftar tugas + mentor. Kalau kelak butuh alat operasional checklist HRD, itu inisiatif terpisah.

## Kandidat Implementasi (prioritas, disesuaikan perusahaan)

**🟢 Prioritas — data sudah ada, nilai tinggi:**
1. **Dashboard Rekrutmen** — KPI (total kandidat, lowongan Open, interview terjadwal, hired periode) + **hiring funnel** (agregasi `progress`) + breakdown `status`. Fondasi visibilitas HR; reuse pola KPI/dashboard HRIS.
2. **Quick wins:** ubah status/tahap kandidat **inline** dari daftar; **tanggal kedaluwarsa** + state "Dikirim" pada Offer.

**🟡 Pertimbangkan — nilai jelas, effort sedang:**
3. **Offer approval flow** (pakai approver existing) + **Offer Letter template** (+ konten di System Setup).
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
