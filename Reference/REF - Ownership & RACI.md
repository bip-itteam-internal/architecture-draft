## Deskripsi

*Peta **kepemilikan** (siapa owner service/dok, siapa ditanya, eskalasi) untuk Bharata. Doc **Reference**. Peran tim grounded dari [[SCRUM SPECS]]; **owner per-orang = (TBD)**, diisi manajemen agar agent/manusia tahu "ke siapa bertanya".*

- **Status**: 🟡 Seed — kerangka + peran tim; owner per-orang TBD

## Peran tim (dari [[SCRUM SPECS]])

| Peran | Pengisi | Tugas |
|---|---|---|
| Product Owner | Lead Departments (SPV) | Tentukan & prioritaskan fitur |
| Scrum Master | Fani Triastowo | Fasilitasi proses + (sementara) QA |
| Development Team | BE / FE / DevOps | Kerjakan sprint backlog |
| QA | sementara SM/PO | Verifikasi sebelum rilis (target: QA Dev terpisah) |

## Ownership service (bip-erp)

> Domain dari [[CLAUDE]] §7 + [[DB - Overview and Notes]]. Owner per-orang = (TBD).

| Service | Domain dok | Owner (TBD) |
|---|---|---|
| api-gateway, orchestrator, SSO | Core / IT | TBD |
| employee, attendance, insentive | HRIS | TBD |
| integration, tiktok-shop, inventory | Marketing / Warehouse | TBD |
| notification, file | Core/IT | TBD |
| task-management | IT (helpdesk/ticketing) | TBD |

## Ownership dokumentasi (vault)

> Tiap domain idealnya punya **maintainer dok** (biasanya lead departemen terkait). (TBD)

| Area vault | Maintainer (TBD) |
|---|---|
| HRIS, Marketing, GA, Warehouse, Manufacture, Finance | Lead departemen masing-masing |
| Core / Application / Tech Development | Tim BE/DevOps |
| Quality & Regulatory | Tim QA/RA |
| Decisions / Reference / Benchmark / Roadmap | (lintas — TBD) |

## Eskalasi

- Teknis/infra → Tech Development (lihat [[IT - Big Pictures]])
- Proses/prioritas → Scrum Master / Product Owner
- (Detail kontak & jalur eskalasi = TBD)

## Belum Diputuskan (TBD)

- Owner per-orang tiap service & area dok.
- Jalur & SLA eskalasi insiden (kait ke [[IT - Monitoring System]] / [[IT - Backup & DR]]).

## Dokumen Terkait

- [[SCRUM SPECS]] · [[CLAUDE]] · [[DB - Overview and Notes]] · [[ROADMAP]] · [[REF - Glossary]]
