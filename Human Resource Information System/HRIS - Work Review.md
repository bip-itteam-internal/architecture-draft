## Deskripsi

*Subsistem **Review Cycle** — siklus penilaian kinerja karyawan berkala yang **menyatukan** sisi **kuantitatif (KPI, sudah sebagian jalan)** dan **kualitatif (work review / feedback, konsep)** menjadi **satu** proses, sesuai mandat konsolidasi **Fase D** di [[HRIS - Roadmap]]. Dokumen ini menaikkan "Work Review" dari konsep tipis menjadi **payung Review Cycle** — hasil adaptasi fitur **Performance Management Mekari Talenta** ke kondisi Bharata, diambil selektif.*

- **Status**: 🟡 Konsep konsolidasi — sisi **KPI ✅ sebagian** (template + scoring per-karyawan di [[Microservices - Employee Service]] `/kpi/*`); **siklus bulanan wajib, review kualitatif SPV→HR, & workflow** 🟡 belum di kode
- **Prinsip #1 — jangan duplikasi**: engine **KPI→insentif marketing** ([[Microservices - Insentive Service]], ✅ produksi) **tetap terpisah**; KPI appraisal per-karyawan yang **sudah ada** ([[HRIS - Key Performance Index]]) **di-reuse**, bukan dibangun ulang. Review Cycle = **satu** siklus, bukan modul penilaian baru
- **Referensi bentuk**: Performance Management **Mekari Talenta** (KPI/OKR/feedback · penilaian atasan/peer/360 · IDP · Succession) — diambil selektif (lihat tabel adaptasi)
- **Penempatan usulan**: perluasan modul `/kpi/*` di [[Microservices - Employee Service]]

## Latar Belakang

- Perusahaan ingin evaluasi kinerja **objektif & berkelanjutan** dengan umpan balik konsisten. Saat ini penilaian tersebar: KPI angka (`/kpi/*`) sudah ada tapi **tanpa penegakan siklus & workflow review**; sisi kualitatif (perilaku/kerja) masih manual/konsep.
- **Fase D** roadmap sudah memutuskan: satukan **"KPI appraisal menyeluruh" + Work Review** jadi **satu Review Cycle** — **bukan** dua sistem terpisah. Dokumen ini adalah desain siklus tersebut.
- **Mekari Talenta** dipakai sebagai referensi struktur (seperti [[HRIS - Recruitment]] mengadopsi ERPGo selektif), **bukan** cetak biru wajib — banyak fiturnya (OKR, 360°, Succession) belum cocok dengan kematangan sistem kita.

## Ruang Lingkup — MVP Review Cycle (Direncanakan)

Satu siklus penilaian berkala (default **bulanan**) per karyawan, menggabungkan:

1. **KPI kuantitatif** — skor metrik berbobot per posisi. **Sudah ada** di `/kpi/*` (template per posisi + scoring per periode `YYYY-MM`). Tugas konsolidasi: **tautkan** ke siklus, bukan bikin baru.
2. **Review kualitatif** — catatan perilaku/kerja + feedback naratif oleh **atasan langsung (SPV)**. **Baru** (menutup konsep Work Review lama).
3. **Siklus & jadwal** — periode wajib (bulanan; bila tanggal 1 jatuh Minggu/libur → hari kerja berikutnya, sesuai catatan HRD di [[HRIS - Key Performance Index]]).
4. **Workflow review** — **karyawan/SPV isi → SPV review → diteruskan ke HR** (rekap dashboard). Menutup TBD "workflow SPV→HR" yang selama ini kosong.

Di luar MVP (OKR, peer/360, IDP, Succession) → lihat **Rollout Bertahap** & **TBD**.

## Adaptasi dari Mekari Talenta (Ambil / Sesuaikan / Tunda)

| Fitur Mekari | Kondisi perusahaan (grounded) | Keputusan |
|---|---|---|
| **KPI** | ✅ sudah jalan sebagian — `/kpi/*` (template per posisi + scoring per periode + dashboard) di [[Microservices - Employee Service]] | ✅ **Ambil (reuse)** — tautkan ke siklus; lengkapi penegakan bulanan |
| **Feedback berkala** | 🟡 konsep (Work Review lama) | ✅ **Ambil** — jadi sisi kualitatif siklus |
| **Penilaian atasan langsung** | ✅ model default (SPV mengisi/review) | ✅ **Ambil** — jalur utama MVP |
| **OKR** | ❌ tak ada — model kita KPI template per posisi (top-down berbobot), bukan objective-setting | 🟡 **Tunda/TBD** — beda paradigma; adopsi = perubahan metodologi besar |
| **Peer review** | 🟡 pola **multi-penilai lintas-divisi sudah jalan** (Performance Review Onboarding, [[Microservices - Recruitment Service]]) | 🔧 **Fase lanjut** — perluas siklus jadi multi-rater (benih sudah ada) |
| **360°** | ❌ tak ada (self+atasan+peer+bawahan) | 🟡 **Tunda** — investasi besar; benihnya multi-rater |
| **Individual Development Plan (IDP)** | 🟡 singgung [[HRIS - Career & Promotion]] + [[HRIS - Training Program]] | 🔧 **Fase lanjut ringan** — tautkan hasil review → tindak lanjut (enroll training / usul promosi) |
| **Succession Planning** | ❌ prasyarat belum ada — org chart, jenjang/golongan, competency matrix semua TBD ([[HRIS - Organization Structure]], [[HRIS - Career & Promotion]]) | 🟡 **Tunda (roadmap jauh)** — bangun prasyarat dulu |

## Komponen & Model Data (Usulan — di Employee Service)

Reuse `/kpi/*` yang ada; tambah koleksi untuk sisi kualitatif & siklus. **Semua TBD** sampai disetujui.

- **KPI (sudah ada)** — `kpi_score` (snapshot template + `values` + skor final Σ(weight×value), per `employee_id`+`YYYY-MM`), template per posisi. **Tidak diubah**; hanya ditautkan ke record siklus.
- **`review_cycle`** (baru) — `{ period (YYYY-MM), department_key, status, opened_at, due_at }`. Menegakkan periode wajib + jadwal.
- **`work_review`** (baru) — `{ cycle_period, employee_id, reviewer_id (SPV), ratings?{aspek→skala}, notes (naratif), status (Draft/Submitted/ReviewedBySPV/ForwardedToHR), kpi_score_ref }`. Menyatukan kualitatif + tautan ke skor KPI periode itu.
- *(fase lanjut)* `review_rater` (multi-rater peer/360), `development_plan` (IDP), `succession_slate`.

> **Reuse, jangan duplikat:** posisi/departemen/atasan dari `work_data` & `master_department`; skor dari `kpi_score` yang sudah ada. Jangan bikin master karyawan/skor tandingan (pola sama seperti [[HRIS - Organization Structure]] & [[HRIS - Training Program]]).

## Alur Siklus (MVP)

1. **Buka periode** — sistem membuka `review_cycle` awal bulan (aturan tanggal 1/Minggu/libur → hari kerja berikutnya).
2. **Isi** — **SPV** mengisi review karyawan timnya (skor KPI via `/kpi/*` + catatan kualitatif). Opsi: karyawan mengisi draft sendiri lalu minta review SPV (sesuai catatan HRD di [[HRIS - Key Performance Index]]).
3. **Review SPV** — SPV memvalidasi/menyetujui → status `ReviewedBySPV`.
4. **Teruskan ke HR** — hasil masuk rekap HR (`ForwardedToHR`).
5. **Rekap & dashboard HR** — ikhtisar untuk stakeholder + tampilan **per-departemen** & **per-orang** (reuse dashboard KPI: need-training <60, top-performer ≥80).
6. **Tindak lanjut** — hasil jadi masukan [[HRIS - Career & Promotion]] (promosi), [[HRIS - Training Program]] (pengembangan), atau [[HRIS - Disciplinary (Surat Peringatan)]] (bila bermasalah berulang).

## Aktor & Persona

> Grounded ke RBAC nyata: supervisor per divisi = `work_data.is_supervisor`; hak modul via `system_roles`. Lihat [[HRIS - Organization Structure]].

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| **SPV / Atasan langsung** — penilai utama | Divisi masing-masing | isi & review KPI + kualitatif untuk timnya (`RequireKPIDepartmentRBAC`) | Web ERP / [[APP - MyBharata]] |
| **HR** — pemilik proses & rekap | HRIS | kelola template, tegakkan siklus, lihat rekap lintas-departemen, tindak lanjut | Web ERP |
| **Karyawan** — subjek (opsional pengisi draft) | Semua divisi | lihat skornya + tren; opsi isi draft self-review | Web ERP / [[APP - MyBharata]] |
| **Peer / rater tambahan** (fase lanjut) | Lintas divisi | beri penilaian saat multi-rater/360 aktif (pola onboarding review) | Web ERP |

## Penempatan Arsitektur

**Usulan: perluas modul `/kpi/*` di [[Microservices - Employee Service]]** (bukan service/modul penilaian baru). Grounded:

- KPI per-karyawan **sudah** hidup di sana (`kpi_score`, template, `RequireKPIDepartmentRBAC`, dashboard). Konsolidasi = **menambah** siklus + review kualitatif + workflow di modul yang sama → nol duplikasi data.
- Reuse master karyawan/departemen/atasan (`work_data`, `master_department`) & feed lintas-service yang sudah ada.
- **Tetap terpisah**: engine **KPI→insentif marketing** ([[Microservices - Insentive Service]]) — beda tujuan (insentif 9 role marketing), sesuai [[ADR - 0002 Database-per-Service]]. Review Cycle **tidak** menyentuhnya.
- Stack konsisten: Go + Fiber v2 + MongoDB di [[Microservices - Employee Service]].

## Keputusan (dikonfirmasi sesi ini)

- **Konsolidasi, bukan duplikasi** — satu Review Cycle menyatukan KPI (kuantitatif, sudah ada) + Work Review (kualitatif, baru); engine insentif marketing tetap terpisah. (Sesuai Fase D.)
- **Target dokumen** = perkaya **Work Review** jadi payung Review Cycle (dok ini); KPI tetap punya dok sendiri sebagai sisi engine/scoring.
- **Cakupan** = **MVP konsolidasi** (KPI + review kualitatif SPV→HR + siklus bulanan + workflow) + roadmap fase lanjut.
- **Penempatan** = perluas `/kpi/*` di Employee Service.
- **Penilai MVP** = **atasan langsung (SPV)**; peer/360 = fase lanjut.
- **OKR & Succession** = ditunda (belum cocok / prasyarat belum ada).

## Rollout Bertahap (Usulan)

- [ ] **MVP-1 — Siklus & workflow** — `review_cycle` (periode wajib bulanan) + status `Draft→Submitted→ReviewedBySPV→ForwardedToHR`; tautkan ke `/kpi/*` yang ada.
- [ ] **MVP-2 — Review kualitatif** — `work_review` (catatan naratif + rating aspek opsional) oleh SPV, digabung dengan skor KPI periode itu.
- [ ] **MVP-3 — Rekap HR** — dashboard konsolidasi (per-departemen & per-orang; reuse ambang need-training/top-performer) + ekspor stakeholder.
- [ ] **Fase lanjut A — Peer / multi-rater** — perluas jadi banyak penilai (pola Performance Review Onboarding, [[Microservices - Recruitment Service]]).
- [ ] **Fase lanjut B — IDP** — Individual Development Plan yang menautkan hasil review → [[HRIS - Training Program]] & [[HRIS - Career & Promotion]].
- [ ] **Fase lanjut C — 360° & OKR** — bila metodologi diputuskan (butuh keputusan HR).
- [ ] **Fase lanjut D — Succession Planning** — setelah org chart + jenjang/golongan + competency matrix ([[HRIS - Organization Structure]], [[HRIS - Career & Promotion]]) siap.

## Belum Diputuskan (TBD)

- **Skala & aspek** review kualitatif (mis. 1–5 per aspek perilaku) — purpose-built, bukan form builder (konsisten keputusan sadar di [[HRIS - Recruitment]]).
- **Periode**: bulanan untuk semua, atau berbeda per departemen?
- **Self-review**: wajib, opsional, atau tidak dipakai.
- **Dampak ke payroll** — apakah hasil siklus mempengaruhi komponen gaji (detail tertunda di [[HRIS - Key Performance Index]]).
- **OKR**: diadopsi atau tidak; bila ya, hidup berdampingan atau menggantikan KPI template.
- **360°/peer**: siapa boleh jadi rater, bobot suara peer vs atasan, anonimitas.
- **Succession**: kriteria talent pool & readiness — tergantung prasyarat org chart/kompetensi.

## Dependensi / Dokumen Terkait

- [[HRIS - Roadmap]] (Fase D — mandat konsolidasi) · [[HRIS - Big Pictures]] · [[HRIS - Analysis]] (asal subsistem Work Review)
- [[HRIS - Key Performance Index]] — sisi kuantitatif/engine scoring (di-reuse) · [[Microservices - Insentive Service]] — engine insentif marketing (tetap terpisah)
- [[Microservices - Employee Service]] — host `/kpi/*` + master karyawan · [[DB - Overview and Notes]]
- [[HRIS - Career & Promotion]] · [[HRIS - Training Program]] · [[HRIS - Disciplinary (Surat Peringatan)]] — tindak lanjut hasil review
- [[HRIS - Retention]] · [[HRIS - Attrition]] · [[HRIS - Organization Structure]] · [[HRIS - Interrelationship Matrices]]
- [[Microservices - Recruitment Service]] — pola multi-penilai (Performance Review Onboarding) untuk peer/360
- [[ADR - 0002 Database-per-Service]] · [[APP - Web ERP]] · [[APP - MyBharata]]
