## Deskripsi

*Roadmap pengembangan domain **HRIS** — disusun grounded dari status kode & dok per area (lihat tiap wikilink). **Urutan fase = usulan**; prioritas final ditetapkan Product Owner ([[REF - Ownership & RACI]], [[SCRUM SPECS]]). Turunan HRIS dari [[ROADMAP]] umum.*

- **Status item**: ✅ jalan · ⚠️ perlu perbaikan · 🟡 konsep/belum di kode · 💤 ditunda · ❓ butuh keputusan

## ✅ Fondasi (sudah jalan — jangan diutak-atik)

- Data karyawan, jadwal, hari libur, auth — [[Microservices - Employee Service]]
- Kehadiran + **Leave/Shift/Correction** request+approval — [[Microservices - Attendance Service]] (pola bersama: [[HRIS - Employee Request & Approval]])
- **KPI→insentif marketing** (9 role) — [[Microservices - Insentive Service]] · komponen **payroll-supplement** ([[HRIS - Payroll]])
- [[CORE - HRIS Orchestrator]]

## Fase A — Perbaiki yang sudah ada (⚠️ dampak langsung)

| Item | Temuan | Catatan prioritas |
|---|---|---|
| **File-service RBAC** | `services/file/main.go:124-137` — akses dokumen tanpa cek role (TODO/501). Dokumen HR sensitif. | Naik (keamanan) — [[Microservices - File Service]] |
| **Clock-in Website (stub)** | `services/attendance/main.go:858-877` selalu `501` | Tergantung kebutuhan web-tap |
| **Overtime → pola request/approval** | belum ikut pola Leave/Shift/Correction | 💤 **Ditunda** (PO: belum urgen) — [[HRIS - Overtime]] |
| ~~Cleanup dok Payroll & KPI~~ | ✅ selesai (deskripsi diluruskan, implemented vs konsep dipisah) | — |

## Fase B — Enabler

- **Kapabilitas Email** di [[Microservices - Notification Service]] (kini hanya inbox/WA/FCM). **Prasyarat** notifikasi kandidat di [[HRIS - Recruitment]].

## Fase C — Net-new prioritas (desain sudah matang)

- **Recruitment / ATS** — [[HRIS - Recruitment]] + [[Microservices - Recruitment Service]] (🟡, service belum ada). Bergantung **Email (Fase B)** untuk notifikasi kandidat.

## Fase D — Konsolidasi Performance (hindari duplikasi)

- Satukan **"KPI appraisal menyeluruh" (konsep)** + [[HRIS - Work Review]] jadi **satu Review Cycle** ([[ERPGo - Performance Review Cycles]]) — **bukan** dua sistem terpisah. Engine insentif marketing ([[Microservices - Insentive Service]]) tetap terpisah. Lihat catatan overlap di [[HRIS - Key Performance Index]].

## Fase E — HR lifecycle (🟡 konsep)

- [[HRIS - Disciplinary (Surat Peringatan)]] · [[HRIS - Career & Promotion]] · [[HRIS - Training Program]] · [[HRIS - Conflict Management]] · [[HRIS - Retention]]

## Fase F — Struktur & Payroll (perlu keputusan scope dulu)

- [[HRIS - Organization Structure]] (org chart) · [[HRIS - Personalia]] · [[HRIS - Interrelationship Matrices]]
- ❓ **Payroll penuh + [[HRIS - Compensation & Benefits]]** → butuh **keputusan batas scope vs Accurate** ([[ADR - 0001 Akuntansi via Accurate]]) sebelum dibangun.

## Dependensi kunci

- `Email (B)` → `Recruitment (C)`
- `Keputusan scope Payroll-vs-Accurate` → `Fase F`
- `Konsolidasi Review Cycle (D)` sebelum bangun appraisal/Work Review terpisah

## Dokumen Terkait

- [[ROADMAP]] (umum) · [[HRIS - Big Pictures]] · [[REF - Ownership & RACI]]
- [[ERPGo - Performance Review Cycles]] · [[ADR - 0001 Akuntansi via Accurate]]
