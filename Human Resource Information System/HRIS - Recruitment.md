## Deskripsi

*Desain (to-be) subsistem **Recruitment** — mengelola **siklus depan karyawan**: dari kebutuhan posisi sampai jadi karyawan aktif. Memisahkan subsistem **Talent acquisition → Interview → On-boarding** yang sekarang menumpuk di [[HRIS - Analysis]] ke ruangnya sendiri.*

- **Status**: 🟡 Desain / Direncanakan (**belum** diimplementasi di kode)
- **Target arsitektur**: microservice `recruitment-service` baru + modul web, dengan **rollout bertahap**
- Titik singgung yang sudah ada di kode: `POST /onboarding/register` (aktivasi akun karyawan baru) di [[Microservices - Employee Service]] — menjadi handoff akhir recruitment

## Latar Belakang

* Saat ini langkah recruitment (talent acquisition, interview, onboarding) tercampur di [[HRIS - Analysis]] dan sebagian masih manual/spreadsheet.
* Tujuannya: alur formal & terlacak dari **permintaan posisi → lowongan → pelamar → screening → psikotes → interview → offer → onboarding**, terintegrasi dengan master data karyawan.

## Pipeline (End-to-End)

1. **Job Requisition** — departemen/SPV mengajukan posisi + headcount + **usulan kualifikasi** + justifikasi → **cek sisa kuota headcount departemen** (tak boleh melebihi) → approval **SPV/kepala departemen → HR** (2 tingkat, konsisten dgn pola [[HRIS - Leave Request]]; **HR finalkan kualifikasi**) → status `Approved` → lowongan boleh dibuka
2. **Sourcing & Job Posting** — HR membuka lowongan (internal/eksternal) + mencatat **sumber pelamar** (job portal, referral, walk-in, bootcamp)
3. **Candidate Management** — data pelamar (CV, kontak, posisi dilamar, sumber) + status pipeline: `Applied → Screening → Psikotes → Interview → Offer → Hired/Rejected`. Tahap **Screening** dibantu **AI CV screening** (lihat bagian khusus di bawah)
4. **Psikotes / Assessment** — kandidat yang **lolos screening** mengikuti psikotes sebelum interview. Dua mode: **(a) online self-service** (kandidat mengerjakan tes di portal — butuh test-engine/bank soal, **TBD**) atau **(b) manual/vendor** (psikolog internal atau vendor melaksanakan; HR input skor + lampirkan **report PDF**). **Rekomendasi rollout: mulai mode manual/vendor (paling ringan & grounded), online engine menyusul.** Hasil (skor per-aspek + rekomendasi/interpretasi) disimpan & jadi bahan pertimbangan lanjut/tidak ke interview (ambang/bobot final di HR — lihat **Pertanyaan untuk HRD** poin 5)
5. **Interview** — penjadwalan, **multi-tahap** (HR + hiring manager/SPV dept), scoring + catatan per tahap
6. **Offer & Decision** — keputusan + surat penawaran → kandidat accept/decline
7. **Onboarding Handoff** — saat kandidat `Hired` → buat akun karyawan via [[Microservices - Employee Service]] `POST /onboarding/register` (employee_id + temporary password) → masuk siklus karyawan aktif

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
5. **HR review** skor + alasan → **HR putuskan** lanjut ke **Psikotes** / Reject (final di HR, bukan AI)

**Pengaman**: human-in-the-loop (tanpa auto-reject), alasan disimpan untuk audit/fairness, data pelamar (PII) disimpan aman.

## Aktor & Role

| Aktor                         | Peran                                                                                                                                          |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Pengaju (SPV / staf dept)** | Mengajukan Job Requisition (dalam sisa kuota) +**usul kualifikasi** kandidat *(siapa boleh mengajukan: lihat poin 1)*                          |
| **SPV / Kepala departemen**   | Approval requisition**tingkat 1**; juga hiring manager (ikut interview & penilaian)                                                            |
| **HR Recruiter**              | Mengelola pipeline: validasi requisition, lowongan, pelamar, jadwal (termasuk **jadwal psikotes**), **input hasil psikotes**, offer            |
| **HR**                        | Approval requisition**tingkat 2**; **finalkan kualifikasi**; penerbitan offer                                                                  |
| **Psikolog / Asesor**         | Melaksanakan & **menginterpretasi psikotes** (skor + rekomendasi); **internal** atau **vendor** pihak ketiga *(internal vs vendor: lihat TBD)* |
| **Direktur**                  | Approval bila **melebihi kuota** / headcount-posisi tertentu *(opsional — lihat TBD)*                                                          |
| **Kandidat**                  | Eksternal —**tanpa akun ERP** (data dikelola HR)                                                                                               |

## Model Data

`recruitment-service` memiliki database sendiri (`recruitment_db`), collection utama:

- `headcount_quota` — jatah headcount per departemen/periode (mis. tahunan); requisition divalidasi vs **sisa kuota**
- `job_requisition` — permintaan posisi (dept, headcount, **kualifikasi usulan**, justifikasi, status approval SPV→HR; tervalidasi vs kuota)
- `job_posting` — lowongan (posisi, deskripsi, sumber/channel, status buka/tutup)
- `candidate` — pelamar (data diri, CV di MinIO, posisi dilamar, sumber, status pipeline)
- `screening_result` — hasil AI CV screening (skor, per-kriteria, rekomendasi, alasan, model, waktu)
- `psychotest` — penugasan tes ke kandidat (jenis tes, mode online/manual, jadwal, status pelaksanaan)
- `psychotest_result` — hasil psikotes (skor per-aspek, rekomendasi/interpretasi, **report PDF di MinIO**, penilai/asesor, waktu); bank soal untuk mode online **TBD**
- `interview` — sesi interview (kandidat, tahap, pewawancara, skor, catatan)
- `offer` — penawaran (kandidat, detail, status accept/decline)

## Arsitektur & Integrasi

- **`recruitment-service`**: Go + Fiber v2 + MongoDB, di belakang [[CORE - API Master Gateway]], auth **SSO** (lihat [[CORE - SSO Flow]]), role HR/recruitment dari `system_roles`
- **Integrasi**:
  - [[Microservices - Employee Service]] — master data posisi/departemen (`PositionTitle*`), cek duplikasi, **handoff `/onboarding/register`** saat hire
  - [[Microservices - Notification Service]] — notifikasi **internal** approval requisition/jadwal/offer (FCM + inbox). Notifikasi ke **kandidat eksternal** dibahas di **Pertanyaan untuk HRD** (poin 8)
  - [[Microservices - File Service]] — penyimpanan CV/dokumen pelamar + **report PDF psikotes** (MinIO)
  - **LLM (OpenRouter)** — AI CV screening (analisis CV vs kriteria); reuse infra LLM yang dipakai Ideamills ([[Sales - Veo (Gemini) Implementation]])
  - **Psikotes** — modul di `recruitment-service`; mode **manual/vendor** cukup catat hasil + lampiran via [[Microservices - File Service]], mode **online** butuh **test-engine + bank soal (TBD / fase lanjut)**; undangan jadwal via [[Microservices - Notification Service]] (internal HR; ke kandidat eksternal lihat **Pertanyaan untuk HRD** poin 8)
- **UI**: modul **Recruitment** di [[APP - Web ERP]] (HR & SPV) + **portal lowongan publik** untuk pelamar (self-apply + upload CV)

## Pertanyaan untuk HRD (bahan diskusi)

> 🟡 **Bahan diskusi — preferensi HRD belum diketahui.** Sebelum sistemnya dirancang, kita perlu tahu **maunya HRD** soal proses, data, dan cara mengabari kandidat — dari pelamar masuk sampai diterima/ditolak. Pertanyaannya dikelompokkan per tahap.

**1. Permintaan posisi (dari SPV/atasan)** — *sebelum ada lowongan, kebutuhan datang dari atasan. Tiap departemen punya **kuota** (jatah jumlah orang); selama kuota masih ada, SPV/kepala departemen boleh mengajukan permintaan posisi (job requisition) sesuai kebutuhan **asal tidak melebihi kuota**. Permintaan disetujui dulu, baru lowongan dibuka.*

- **Rencana alurnya**: SPV mengajukan posisi + jumlah orang + alasan → sistem cek **sisa kuota** departemen → disetujui bertingkat (atasan, lalu HR) → setelah disetujui, lowongan baru boleh dibuka. Apakah HRD setuju alur ini?
- **Kuota**: siapa yang menetapkan jatah tiap departemen & untuk periode apa (mis. tahunan / terkait anggaran)?
- Selama **dalam kuota**, apakah approval tetap bertingkat atau cukup lebih ringan? Kalau **melebihi kuota** ditolak, atau boleh tapi perlu persetujuan lebih tinggi (mis. **direktur**)?
- Siapa yang boleh mengajukan hanya SPV/kepala departemen, atau staf juga (lalu disetujui atasannya)?
- Apa saja yang wajib diisi (posisi, jumlah, alasan, target mulai, kisaran gaji, **usulan kualifikasi/kriteria kandidat**)? Kalau ditolak, direvisi & diajukan ulang?
- **Kualifikasi kandidat disepakati kolaborasi**: diusulkan **SPV** di requisition (paham kebutuhan teknis job), lalu **difinalkan & distandarkan HRD** jadi kriteria resmi (dipakai saat screening, poin 4).

**2. Cara melamar & sumber pelamar** — *dari mana kandidat datang dan bagaimana mereka mendaftar.*

- Lowongan disebar ke mana saja selain portal kita sendiri? (mis. job board seperti JobStreet, referral karyawan, media sosial, atau pelamar datang langsung/walk-in)
- Kalau ada pelamar lewat jalur lain (kirim CV ke email, walk-in), apakah HRD mau memasukkannya manual ke sistem?
- Satu orang boleh melamar beberapa posisi sekaligus? Kalau pernah ditolak, boleh melamar lagi setelah berapa lama?

**3. Data kandidat** — *informasi apa yang dikumpulkan dari pelamar dan aturan mainnya.*

- Saat melamar, data apa yang **wajib** diisi? (usulan dasar: nama, nomor WhatsApp/telepon, email, posisi yang dilamar, dan CV) — perlu tambahan seperti pendidikan, pengalaman, ekspektasi gaji, atau domisili?
- Pelamar perlu menyetujui dulu bahwa datanya boleh diproses & dihubungi (consent)?
- Data kandidat — terutama yang ditolak — disimpan sampai kapan, lalu diapakan?
- Siapa saja yang boleh melihat data pelamar? (mis. HR lihat semua; SPV/hiring manager hanya pelamar untuk posisinya)

**4. Screening (penyaringan awal)** — *menyaring pelamar sebelum interview; rencananya dibantu AI untuk menilai kecocokan CV, tapi keputusan tetap di HR.*

- **Kriteria/kualifikasi sudah disepakati** (poin 1): diusulkan SPV, difinalkan HRD — dipakai sebagai syarat wajib vs nilai plus saat screening.
- HRD setuju AI hanya memberi **skor & rekomendasi** (tidak menolak otomatis), dan HR yang memutuskan?
- Pakai batas skor tertentu untuk lanjut ke tahap berikutnya, atau murni penilaian HR?

**5. Psikotes (assessment)** — *tes psikologi/kemampuan untuk kandidat yang lolos screening, sebelum interview.*

- Mau psikotes dilakukan **online** (kandidat mengerjakan sendiri di portal) atau **manual/luring** (psikolog/vendor melaksanakan, lalu hasilnya dicatat ke sistem)?
- Jenis tesnya apa — tes **kemampuan** (kognitif/numerik/verbal/logika), tes **kepribadian** (mis. DISC/Papikostick/MBTI), atau keduanya?
- Siapa yang menilai & menafsirkan — **psikolog internal** atau **vendor pihak ketiga**? Kalau vendor, hasilnya berupa report PDF yang dilampirkan ke sistem?
- Semua kandidat ikut psikotes, atau hanya yang lolos screening? (rencana saat ini: setelah screening, sebelum interview)
- Hasil psikotes jadi **penentu lulus/tidak** (pakai ambang skor) atau hanya **bahan pertimbangan** bersama interview? Seberapa besar bobotnya?
- Hasil psikotes (terutama kandidat yang ditolak) disimpan sampai kapan?

**6. Interview** — *proses wawancara kandidat yang lolos screening & psikotes.*

- Berapa tahap interview dan siapa saja pewawancaranya? (mis. HR dulu, lalu hiring manager/SPV; perlu direktur untuk posisi tertentu?)
- Soal jadwal: HRD yang menawarkan slot waktu, atau kandidat yang memilih sendiri?
- Penilaian interview pakai form/skor yang seragam, atau catatan bebas tiap pewawancara?

**7. Offer & keputusan akhir** — *menawari kandidat terpilih dan memutuskan penerimaan.*

- Siapa yang berhak menyetujui offer dan jumlah orang yang direkrut (headcount)? (HR saja, atau perlu SPV/direktur untuk posisi tertentu?)
- Isi surat penawaran apa saja — gaji, tunjangan, tanggal mulai, masa percobaan? Pakai template baku?
- Offer berlaku sampai kapan (batas waktu jawaban kandidat)? Kalau kandidat menawar (nego), siapa yang memutuskan?
- Begitu kandidat diterima, data apa yang dipindahkan menjadi data karyawan baru?

**8. Pemberitahuan ke kandidat** — *bagaimana kandidat tahu hasil tiap tahap. Catatan: kandidat ini orang luar, tidak punya akun di sistem.*

- Di tahap mana saja kandidat dikabari? Yang **ditolak** dikabari, atau dibiarkan? Kalau dikabari, dengan bahasa sehalus apa?
- Lewat apa kabarnya — WhatsApp, email, atau kandidat cek sendiri di portal? Dan tampil **atas nama siapa** — HRD/perusahaan, atau nomor sistem?
- Pesannya **dikirim petugas HRD sendiri**, atau **otomatis oleh sistem**?
- Saat ditawari (offer), kandidat menerima/menolak lewat apa — balas WhatsApp, telepon, atau klik tautan?

> **Catatan teknis singkat (belum mengikat):** fitur **email belum tersedia** di sistem (kalau dipilih, perlu dibangun dulu). Pengiriman WhatsApp otomatis lewat sistem saat ini memakai **satu nomor milik IT** (bukan nomor resmi HRD) — kalau mau atas nama HRD atau otomatis yang aman, perlu disiapkan nomor/akun tersendiri. Detailnya dibahas setelah HRD menentukan arah.

## Rollout Bertahap

- [ ] **Fase 1** — Job Requisition (approval SPV→HR) + Candidate management (data pelamar + status pipeline)
- [ ] **Fase 2** — Sourcing & Job Posting + **Psikotes (manual/vendor: input skor + lampiran report)** + Interview (penjadwalan + scoring multi-tahap)
- [ ] **Fase 3** — Offer & Decision + **Onboarding handoff** (integrasi `/onboarding/register`)
- [ ] **Fase 4** — **portal lamaran publik (self-apply) + AI CV screening** (skor & rekomendasi, HR putuskan)
- [ ] **Fase 5 (opsional)** — integrasi job board pihak ketiga (mis. JobStreet) · **psikotes online (test-engine + bank soal)**

## Belum Diputuskan (TBD)

- ~~Portal pelamar eksternal vs input manual HR~~ → **diputuskan: portal self-apply (pelamar upload CV) + AI screening**
- **Preferensi HRD** (alur approval & kuota/direktur, kriteria & ambang skor, **psikotes**, template offer letter, job board, notifikasi ke kandidat) — belum diketahui; dirinci di **Pertanyaan untuk HRD**
- **Teknis AI screening**: model LLM yang dipakai & penanganan CV hasil scan (OCR)
- **Psikotes**: mode (online test-engine vs manual/vendor), jenis tes & tools (kemampuan/kepribadian), penilai (psikolog internal vs vendor), ambang skor & bobot terhadap keputusan (lihat Pertanyaan poin 5)
- **Kuota headcount**: sumber/penetapan jatah per departemen & periodenya (lihat Pertanyaan poin 1)

## Dependensi / Dokumen Terkait

- [[HRIS - Analysis]] — sumber subsistem talent acquisition/interview/onboarding yang dipisah ke sini
- [[HRIS - Personalia]] · [[HRIS - Big Pictures]]
- [[Microservices - Employee Service]] — onboarding/register & master data
- [[Microservices - Notification Service]]
- [[APP - Web ERP]]
