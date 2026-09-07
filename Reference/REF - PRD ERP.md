## Deskripsi

*Peta **PRD (Product Requirements Document) ERP Bharata** dalam kerangka delapan bagian PRD enterprise yang lazim: Business Process, User Roles, Workflow Roles, Functional Modules, Security Requirements, Integration Requirements, Infrastructure Architecture, UAT & Maintenance. Vault sengaja **tidak** menyimpan PRD sebagai satu dokumen: isinya ditulis grounded-in-code per domain, service, ADR, API, dan runbook. Dokumen ini adalah **pintu**: tiap bagian menaut ke dok sumbernya dan menyebut gap yang tersisa. Ia **tidak menyalin** isi apa pun supaya tidak lahir sumber kebenaran kedua.*

- **Status**: ⚠️ Peta terisi dari dok yang ada (dinilai 2026-09-07). Tiga bagian punya lubang nyata: UAT formal, kebijakan keamanan terpusat, dan audit trail lintas modul. Status per dok dibaca di dok itu sendiri, bukan di sini.
- **Kenapa referensi ini ada**: pertanyaan "apakah vault sudah menghasilkan PRD ERP" (2026-09-07) dijawab lewat pencarian: nol dok berjudul PRD dan nol entri `VAULT-INDEX.json` yang menyebut Product Requirements Document. Satu-satunya PRD yang dirujuk vault adalah PRD Website Bharata Internasional v1.2 di repo `website-bharata` (lihat [[APP - Website Bharata Internasional]]), yaitu situs publik, bukan ERP. Padahal isi kedelapan bagian itu sebagian besar sudah ada, hanya tersebar. Peta ini menjawab "bagian X dari PRD ada di mana" tanpa harus membaca ratusan dok.
- **Cara pakai**: mulai dari tabel ringkas, lompat ke dok sumber. Untuk pembaca non-teknis (manajemen, auditor, vendor) tabel ringkas dan §Fokus lintas-bagian biasanya sudah cukup.
- **Aturan pemeliharaan**: dok ini hanya memuat tautan, satu kalimat konteks per tautan, dan daftar gap. **Jangan** menulis angka, ambang, rumus, daftar izin, atau urutan menang di sini; itu milik dok sumber. Dok baru yang mengisi salah satu bagian cukup ditambahkan sebagai satu baris tautan.

## Ringkasan per bagian

| # | Bagian PRD | Dok pintu utama | Kelengkapan (dinilai 2026-09-07) |
|---|---|---|---|
| 01 | Business Process | Big Pictures per domain (lihat §01) | ✅ ada per domain, kedalaman bervariasi; Manufacture belum punya dok Big Pictures |
| 02 | User Roles | [[CORE - RBAC dan Permission Set]] | ⚠️ paket hak per posisi live, sebagian modul masih bertumpu pada tier lama |
| 03 | Workflow Roles (approval flow) | [[REF - Alur Persetujuan]] | ✅ inventaris seluruh alur persetujuan, terverifikasi kode |
| 04 | Functional Modules | [[HOMEPAGE]] · [[API - Index]] | ✅ peta modul, service, dan endpoint |
| 05 | Security Requirements | [[IT - Security]] | ⚠️ kontrol teknis berjalan, program/kebijakan keamanan masih 🟡 |
| 06 | Integration Requirements | [[Microservices - Integration Service]] | ✅ akuntansi, marketplace, dan vendor terdokumentasi |
| 07 | Infrastructure Architecture | [[IT - Server, VMs and Databases]] · [[IT - Environment Inventory]] | ✅ dengan catatan pada CI-CD dan pemetaan port |
| 08 | UAT & Maintenance | [[SCRUM SPECS]] · [[IT - Runbooks]] | 🟡 belum ada prosedur UAT formal; QA Dev terpisah masih target |

## 01 Business Process

Proses bisnis ditulis per domain. Pintu tiap domain adalah dok Big Pictures, dan tiap dok domain memuat bagian **Persona / Pengguna** (siapa memakai, tujuan, pain point, aksi utama).

- [[HRIS - Big Pictures]] · [[Sales - Big Pictures]] · [[GA - Big Pictures]] · [[Finance - Big Pictures]] · [[WH - Management System]] · [[IT - Big Pictures]] · [[QA - Big Pictures]]
- **Manufacture** belum punya dok Big Pictures; pintunya [[Manufacture - Stock & Material Management]] dan [[Manufacture - Order Production Workflow (Flow Source)]].
- Alur banyak-aktor yang dipisah jadi dok persona sendiri: [[HRIS - Payroll Persona]].
- Rantai bisnis yang di kode terpecah jadi beberapa pengajuan terpisah: [[REF - Rantai Pengajuan Lintas Modul]].
- Aturan bisnis yang menentukan uang dan sanksi (cuti, telat, mangkir, SP) **tidak** hidup di vault; petanya di [[HRIS - Kepatuhan Peraturan Perusahaan]] dan kewajibannya di [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]].
- Istilah dan singkatan lintas domain: [[REF - Glossary]].

## 02 User Roles

- **Mekanisme hak akses** (tiga sumbu: modul, tingkat aksi, cakupan data; paket hak menempel pada posisi): [[CORE - RBAC dan Permission Set]] dan keputusannya [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].
- **Akun dan `system_roles`** (peta modul ke role, aktif/nonaktif, reset): [[IT - Employee System]].
- **Hierarki organisasi dan atasan langsung** (bukan bagian RBAC, tinggal di data kerja karyawan): [[HRIS - Organization Structure]].
- Pengecualian yang sengaja di luar tiga sumbu: hak per-objek admin space di [[ADR - 0038 Hak Per-Objek Admin Space Task Management]]; izin yang menempel di departemen [[ADR - 0041 Izin Tipe Form Menempel di Departemen]]; kewenangan yang ditugaskan [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]].
- **Peran tim pengembang dan pemilik dok**: [[REF - Ownership & RACI]]. Gap: owner per-orang masih TBD di sana.

## 03 Workflow Roles (approval flow)

- **Inventaris seluruh alur persetujuan dan siapa yang berwenang**, disusun dari rute dan handler seluruh service: [[REF - Alur Persetujuan]]. Dok itu juga menjelaskan tiga cara gerbang persetujuan ditulis, dan kenapa menyapu daftar rute saja menghasilkan kesimpulan yang salah.
- **Rantai pengajuan yang putus antar modul** (pengajuan disetujui lalu data diketik ulang di layar lain): [[REF - Rantai Pengajuan Lintas Modul]]. Status: peta masalah, arah perbaikan sengaja belum diputuskan.
- Alur per modul: [[HRIS - Employee Request & Approval]] (pengajuan karyawan) · [[GA - SOP Procurement]] dan [[GA - Procurement System]] (pembelian) · [[IT - Helpdesk]] (Kanban tiket IT) · [[Manufacture - Order Production Workflow (Flow Source)]] (order produksi) · [[HRIS - Alur KPI Otomatis]] (penilaian).
- Keputusan yang membentuk alur: [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]] · [[ADR - 0062 Jenjang Jabatan Menggerbangi Pengajuan Requisition Lintas-Departemen]].
- Jadwal dan tenggat yang harus terlihat orang masuk lewat satu kalender: [[Microservices - Calendar Service]]. Undangan kalender memberi tahu, bukan meminta izin; itu keputusan sadar yang tercatat di sana.

## 04 Functional Modules

- **Peta sistem dan indeks dokumentasi**: [[HOMEPAGE]]. Struktur repo, gateway, orchestrator, dan daftar service ada di situ.
- **Aplikasi yang dipakai orang**: [[APP - Web ERP]] · [[APP - MyBharata]] · [[APP - Dynamic Task Tracker]] · [[APP - Audit Internal]] · [[APP - Portal Karir Bharata]] · [[BASE - Enterance Point]].
- **Service backend**: seluruh dok berprefix `Microservices -` di folder Core System and Modules, satu dok per service. Daftar endpoint per service: [[API - Index]].
- **Data**: [[DB - Overview and Notes]] (database per service) dan [[DB - Data Dictionary]].
- **Yang belum ada atau masih konsep**: [[ROADMAP]] dan [[HRIS - Roadmap]].
- Kemampuan AI yang sudah dan belum ada di ERP: [[CORE - Kapabilitas AI dan Machine Learning]].

## 05 Security Requirements

- **Pandangan keamanan terpusat, sekaligus peta gap-nya**: [[IT - Security]]. Kontrol yang sudah berjalan di sana: autentikasi dan SSO, otorisasi, jaringan, secret deploy, backup terenkripsi. Yang masih konsep: kebijakan proteksi PII dan kredensial, incident response, patch dan vulnerability management, keamanan endpoint, audit keamanan IT.
- Autentikasi dan gateway: [[CORE - SSO Flow]] · [[CORE - API Master Gateway]] · [[ADR - 0003 SSO-only Gateway]].
- Batas keamanan yang sering disalahpahami: prefix `/internal/` **bukan** privat, lihat [[ADR - 0031 Prefix internal Bukan Batas Keamanan]].
- Otorisasi: [[CORE - RBAC dan Permission Set]]. Audit otorisasi point-in-time: [[LOG - 2026-07-30 Audit Otorisasi Employee Service]].
- Jaringan, backup, dan secret deploy: [[IT - Network Management]] · [[IT - Backup & DR]] · [[IT - CI-CD]].

## 06 Integration Requirements

- **Akuntansi (Accurate)**: [[External - Accurate]] · [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0014 Accurate Token DB-backed via OAuth]] · [[ADR - 0015 Push Pergerakan WMS ke Accurate]] · runbook [[RUN - Accurate API Access Token (OAuth)]].
- **Marketplace dan iklan**: [[Sales - Marketplace Integration]] · [[Microservices - Integration Service]] · [[Microservices - TikTok Shop Service]] · [[Sales - Affiliate Integration (TikTok Docs)]] · [[RUN - Onboarding Meta Ads]]. Cache dokumentasi Shopee Open API v2 di-generate skrip di folder `API Reference/Shopee Open API v2/` dan dibaca lewat path, bukan wikilink.
- **Orkestrasi order pihak ketiga**: [[External - Desty]] (soft-disabled, kodenya masih ada) · [[Vendor - CRM]].
- **Logistik**: [[RUN - Onboarding KiriminAja]].
- **Perangkat**: [[APP (Extension) - Fingerprint Listener (Complete)]].
- **Email transaksional**: [[ADR - 0026 Email Transaksional via Resend (bukan Mail Server Sendiri)]].
- **Integrasi internal antar service**: notifikasi lewat [[Microservices - Notification Service]] (kategori inbox adalah daftar-izin bersama), agenda lewat [[Microservices - Calendar Service]] (feed dari tiap service, kalender tak punya aturan visibilitas sendiri).
- Kinerja jalur integrasi: [[ADR - 0011 Integration Read Cache + Singleflight (Fase 1 Perf)]].

## 07 Infrastructure Architecture

- **Server, VM, database**: [[IT - Server, VMs and Databases]] · **inventaris environment dan endpoint**: [[IT - Environment Inventory]].
- **Prinsip arsitektur**: [[ADR - 0002 Database-per-Service]] · [[DB - Overview and Notes]].
- **CI/CD dan deploy**: [[IT - CI-CD]] · [[RUN - Deploy Microservices bip-erp]] · [[RUN - Deploy Frontend ERP ke Produksi]] · [[RUN - Deploy Task Management Service]]. Prod dijalankan manusia, bukan agent.
- **Monitoring**: [[IT - Monitoring System]] dan pembaca statusnya [[Microservices - Monitoring Service]].
- **Backup dan DR**: [[IT - Backup & DR]]. Gap: prosedur restore dan DR sebagian masih TBD, tercatat di [[IT - Runbooks]].
- **Job terjadwal**: [[IT - Background Jobs & Schedulers]] · **jaringan**: [[IT - Network Management]] · **tooling dev**: [[IT - Development Apps and Tools]].

## 08 UAT & Maintenance

- **Proses pengembangan dan Definition of Done**: [[SCRUM SPECS]]. QA saat ini dijalankan sementara oleh Scrum Master atau Product Owner; QA Dev terpisah masih target.
- **Cara kerja developer dan AI agent**: [[DEVELOPER GUIDE]] · [[RUN - Onboarding Developer Baru]] · gerbang kualitas lokal dan papan sesi di [[IT - Gerbang Repo dan Papan Sesi Agent]] · otonomi merge agent di [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]].
- **Operasional rutin**: [[IT - Runbooks]] dan seluruh dok `RUN -` di folder Runbooks.
- **Dukungan pengguna pascarilis**: [[IT - Helpdesk]] (tiket, SLA dua dimensi, eskalasi).
- **Rekam insiden dan pembersihan data**: folder Logs, mis. [[LOG - Clock-in Gagal Karyawan Shift (schedule not found)]] dan [[LOG - 2026-08-11 Pembersihan Faktur Menggelembung Agustus]].
- **Arah dan prioritas**: [[ROADMAP]].
- **Gap UAT**: kata UAT hanya muncul sebagai satu baris jadwal di [[Finance - Kas Kecil dan Pengajuan Budget]] dan sebagai langkah sandbox di [[RUN - Onboarding KiriminAja]]. Tidak ada prosedur penerimaan pengguna, kriteria lolos, maupun siapa yang menandatangani. Definition of Done di [[SCRUM SPECS]] menyebut QA, tidak menyebut penerimaan oleh pengguna.

## Fokus lintas-bagian

Empat fokus yang lazim diminta PRD enterprise, dipetakan ke dok yang ada.

### Workflow bisnis

§01 dan §03 di atas. Pintu tercepat: [[REF - Alur Persetujuan]] untuk "siapa boleh memutuskan apa", [[REF - Rantai Pengajuan Lintas Modul]] untuk "di mana rantainya putus".

### Approval flow

[[REF - Alur Persetujuan]] adalah satu-satunya inventaris lengkap. Alur baru wajib ditambahkan ke sana, bukan ke dok ini.

### Audit trail

Tidak ada kebijakan audit trail tingkat ERP. Tiap service memutuskan sendiri apa yang dijejak dan bagaimana bentuknya, sehingga bentuknya berbeda-beda. Yang sudah ada:

| Modul | Bentuk yang ada | Dok |
|---|---|---|
| Tiket IT (task-management) | audit ditulis di semua mutasi task, komentar, checklist, lampiran; riwayat per task dan daftar audit berlingkup peran | [[Microservices - Task Management Service]] · [[API - Task Management Service]] |
| Tiket engagement | koleksi log sendiri, sekaligus riwayat penugasan | [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] |
| Manufaktur (WMS) | audit log per aksi dan rekap per user per bulan yang dipakai KPI otomatis; target audit hanya kode, bukan id dokumen | [[Microservices - Manufacture Service]] · [[API - Manufacture Service]] · [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] |
| Dokumen produksi batch | audit pada transisi status | [[Manufacture - Dokumen Produksi Batch]] |
| Insentif | koleksi audit dengan before/after dan pelaksana | [[DB - Data Dictionary]] · [[API - Insentive Service]] |
| Rekrutmen | audit log keputusan untuk HR admin | [[Microservices - Recruitment Service]] · [[API - Recruitment Service]] |
| Hak per-objek admin space | satu-satunya jejaknya ada di audit trail | [[ADR - 0038 Hak Per-Objek Admin Space Task Management]] |
| Percobaan pengajuan lintas modul | dijejaki middleware, dibaca modul IT | [[ADR - 0046 Percobaan Pengajuan Dijejaki Middleware, Bukan Panggilan per Cabang]] · [[ADR - 0047 Jejak Pengajuan Dibaca Modul IT, Digerbang Departemen Bukan Peran]] |

Yang belum ada: daftar apa yang **wajib** dijejak, bentuk baku (aksi saja atau before/after), retensi, siapa boleh membaca, dan apakah shared-library menyediakan satu helper supaya service berikutnya tidak merancang ulang.

### Security & compliance

- Keamanan sistem: §05 dan [[IT - Security]].
- Kepatuhan peraturan perusahaan (uang, sanksi, jatah): [[HRIS - Kepatuhan Peraturan Perusahaan]] · [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]].
- Kepatuhan regulasi farmasi (CPOB, BPOM, batch, CAPA, ED, recall): [[QA - Big Pictures]] dan turunannya.
- Audit internal sebagai fungsi: [[Finance - Audit Internal]] · [[APP - Audit Internal]] · [[GA - Audit Internal System]] · [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]] · [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]].

## Belum Diputuskan (TBD)

Tiga lubang di bawah butuh keputusan manajemen, bukan sekadar sinkron dok. Jalur resminya `/analisa-kebutuhan`, yang menghasilkan ADR dan dok domain; peta ini tinggal menaut hasilnya.

1. **UAT formal**: siapa yang menandatangani penerimaan, kriteria lolos, posisinya di siklus Scrum ([[SCRUM SPECS]]), dan apakah rekamannya lewat form builder atau tiket.
2. **Kebijakan keamanan terpusat**: daftar TBD di [[IT - Security]] (pemilik proses, klasifikasi data, incident response, patch, endpoint, adopsi standar).
3. **Audit trail lintas modul**: lihat §Fokus lintas-bagian di atas.

## Dokumen Terkait

- [[HOMEPAGE]] · [[README]] · [[DEVELOPER GUIDE]] · [[ROADMAP]] · [[SCRUM SPECS]]
- [[REF - Alur Persetujuan]] · [[REF - Rantai Pengajuan Lintas Modul]] · [[REF - Ownership & RACI]] · [[REF - Glossary]]
- [[IT - SOP Dokumentasi Vault]] (kenapa vault berbentuk dok grounded per domain, bukan PRD tunggal)
