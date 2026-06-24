## Catatan

*Peta **arah & prioritas** pengembangan ERP Bharata — dok proses/PM (seperti [[SCRUM SPECS]]), bukan arsitektur. Diisi grounded dari dok yang ada; **prioritas & target tanggal = (TBD)**, ditetapkan Product Owner/manajemen. Backlog operasional harian tetap di [[APP - Dynamic Task Tracker]].*

- **Status item**: ✅ selesai · 🔵 sedang jalan · 🟡 direncanakan/konsep · 💤 ditunda · ❓ butuh keputusan

## Selesai (baru-baru ini)

- ✅ Task Manager cut-over ke **SSO-only** (jadi service bip-erp) — lihat [[ADR - 0003 SSO-only Gateway]]
- ✅ Benchmark fitur **ERPGo** vs bip-erp — [[ERPGo - Overview & Gap Matrix]]
- ✅ Second-brain Fase 1: domain [[QA - Big Pictures|Quality & Regulatory]] + glosarium [[REF - Glossary]]

## Direncanakan / Konsep

| Item | Status | Sumber | Catatan |
|---|---|---|---|
| Recruitment service (ATS) | 🟡 | [[HRIS - Recruitment]] · [[Microservices - Recruitment Service]] | desain ada, belum di kode |
| Form Builder service | 💤 | [[ERPGo - Form Builder]] | rencana `/plan` terkunci, eksekusi ditunda |
| Contract Management | 🟡 | [[ERPGo - Contract Management]] | gap fit tinggi |
| Budget Planner | 🟡 | [[ERPGo - Budget Planner]] | planning+monitoring saja (bukan akuntansi) |
| Goal/OKR Management | 🟡 | [[ERPGo - Goal (OKR) Management]] | melengkapi KPI |
| Internal CRM pipeline | 🟡 | [[ERPGo - Internal CRM (Leads & Deals)]] | bersyarat (ada jalur B2B?) |
| Isi konten QA/RA farmasi | ❓ | [[QA - Big Pictures]] | butuh input tim QA (saat ini scaffold/TBD) |

## Infra / Teknis (dari [[HOMEPAGE]] TODO)

- 🟡 shared-library sebagai repo standalone (mudah di-include tiap service)
- 🟡 Pisahkan `docker-compose` & `.env` per service secara benar
- ✅ FE/app sudah dipisah dari mono-repo backend

## Butuh keputusan (❓)

- Prioritas & urutan eksekusi kandidat di atas (Product Owner).
- Apakah ada kanal penjualan **B2B/wholesale** (penentu CRM internal + Quotation) — [[ERPGo - Quotation & Proposal]].
- Apakah Bharata memegang fungsi **distribusi (CDOB/PBF)** — [[QA - Big Pictures]].

## Fase second-brain berikutnya

- **Fase 3 (sedang)**: [[DB - Data Dictionary]] · [[IT - Runbooks]] · [[IT - Environment Inventory]]
- Lengkapi [[REF - Ownership & RACI]] dengan pemilik nyata per service/dok.

## Roadmap per-domain

- [[HRIS - Roadmap]] — fase perbaikan + fitur HRIS (grounded per area)

## Dokumen Terkait

- [[SCRUM SPECS]] · [[HOMEPAGE]] · [[ERPGo - Overview & Gap Matrix]] · [[REF - Ownership & RACI]]
