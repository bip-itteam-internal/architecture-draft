## Deskripsi

*Manajemen program **pelatihan & pengembangan karyawan** (training & development). Dokumen ini menaikkan status dari konsep-mentah menjadi **usulan desain MVP** — hasil adaptasi modul **Training ERPGo** ke kondisi Bharata. **Backend & Frontend MVP sudah diimplementasi & merged ke main**, grounded ke pola service & master data yang ada. **Cakupan sengaja dibatasi ke MVP inti**; fitur lanjut ditandai fase-lanjut/TBD.*

- **Status**: ⚠️ **MVP Implemented (ada catatan)** — live di dev + produksi 2026-08-06 dan terverifikasi lewat gateway 2026-08-19, kini dilayani **[[Microservices - Learning Service]]** (`/api/learning/*`), UI `/hris/training`. Sebelumnya menumpang Employee Service; dipindah lewat **LMS Fase 0** (bip-erp [#1020](https://github.com/bip-itteam-internal/bip-erp/pull/1020), erp-frontend [#814](https://github.com/bip-itteam-internal/erp-frontend/pull/814)). MVP awal: BE #545/#550 + FE #390/#391, refine FE #396. **Dua catatan yang menentukan jawaban "sudah ready?"** (diperiksa ulang 2026-09-15): (1) layar karyawan (**Pelatihan Saya** dan **Pengajuan Pelatihan**) sudah merged ke `dev` MyBharata tetapi **belum ada di rilis GitHub terbaru** `v1.14.5+135`, dan `training_request` di produksi masih **0**, jadi yang terbukti dipakai baru sisi HR; (2) dari LMS, baru **post-test berskor** (course, bank soal, rekaman percobaan) yang ada di kode dan produksi (PR [#1321](https://github.com/bip-itteam-internal/bip-erp/pull/1321), 2026-08-20), **tanpa layar**; materi, pre-test, kurikulum jabatan, dan Talent Pool **belum ada kode**.
- **Pengajuan & evaluasi (2026-08-11)**: BE [#1148](https://github.com/bip-itteam-internal/bip-erp/pull/1148)/[#1149](https://github.com/bip-itteam-internal/bip-erp/pull/1149)/[#1150](https://github.com/bip-itteam-internal/bip-erp/pull/1150) + FE [#967](https://github.com/bip-itteam-internal/erp-frontend/pull/967)/[#968](https://github.com/bip-itteam-internal/erp-frontend/pull/968) **merged**. Rantai persetujuan **SPV → HR** (dua tahap, bukan tiga — lihat alasannya di [[Microservices - Learning Service]]) dan penilaian trainer empat aspek dengan **ambang tiga responden**. Layar karyawan **Pelatihan Saya** menyusul di MyBharata [#112](https://github.com/bip-itteam-internal/my-bharata/pull/112), **merged ke `dev` 2026-08-11** (catatan lama "belum merge" sudah tidak berlaku), tetapi belum ada di rilis GitHub terbaru `v1.14.5+135` (diperiksa 2026-09-15), lihat butir alur di bawah.
- ✅ ~~Belum satu pun dari fitur 2026-08-11 itu diverifikasi lewat gateway hidup~~ — **terverifikasi 2026-08-19** sesudah image `learning-service` dibuild ulang di dev dan produksi; rincian panggilan + kontrol negatifnya di [[API - Learning Service]]. Selama jeda itu bug satuan `department_key` (key dikirim ke pencarian yang menyaring **nama**) hidup tak terlihat dan membuat pengajuan **mustahil dibuat untuk 6 dari 10 departemen**; ditemukan lewat pembacaan kode, bukan dari layar. Perbaikannya PR [#1153](https://github.com/bip-itteam-internal/bip-erp/pull/1153), **merged 2026-08-11** (catatan lama "belum merge" sudah tidak berlaku).
- ⚠️ **Alur karyawan biasa: terputus sejak 2026-08-13, penggantinya sudah di `dev` tetapi belum terbukti sampai ke orang.** Menu self-service pelatihan dicabut dari web 2026-08-13 ([erp-frontend#1022](https://github.com/bip-itteam-internal/erp-frontend/pull/1022)) mendahului rilis penggantinya. Per 2026-09-15: my-bharata [#112](https://github.com/bip-itteam-internal/my-bharata/pull/112) (Pelatihan Saya) dan [#115](https://github.com/bip-itteam-internal/my-bharata/pull/115) (Pengajuan Pelatihan, **merged ke `dev` 2026-08-22**) ada di `dev` (`1.18.1+163`), tetapi merge #115 bukan leluhur tag rilis GitHub terbaru `v1.14.5+135` (2026-08-03). Datanya konsisten dengan itu: `training_request` produksi masih **0 dokumen**, `trainer_evaluation` **0**, dan satu-satunya peserta belum hadir. **Yang terbukti dipakai baru sisi HR**: kedua kelas yang ada dibuat akun HR.
- **Referensi bentuk**: modul **Training ERPGo** (3 sub-menu: Training Types · Trainers · Training List) — diambil selektif, **bukan** disalin utuh
- **Penempatan**: ✅ **service `learning` sendiri** — lihat **Penempatan Arsitektur** (usulan lama "perluasan Employee Service" sudah ditinggalkan)
- **Kelanjutan**: modul ini jadi fondasi **LMS People Development** (materi PDF & video, pre/post test, skoring otomatis, kurikulum per jabatan, Talent Pool). Desain lengkapnya ada di `erp/docs/superpowers/specs/2026-08-05-lms-people-development-design.md`; ringkasannya di **Rollout Bertahap** di bawah
	- **Kaderisasi / Talent Pool dicatat di [[HRIS - Career & Promotion]]**, bukan di sini. Pelatihan cuma alat ukurnya; yang dikelola adalah perpindahan jenjang
- **Prioritas**: Fase E di [[HRIS - Roadmap]] (HR lifecycle, setelah Recruitment) — belum urgen; dokumen ini menyiapkan desain agar cepat dieksekusi saat gilirannya

## Latar Belakang

- Pelatihan karyawan saat ini dikelola **manual/spreadsheet**; tidak ada katalog jenis pelatihan, daftar trainer, jadwal terlacak, atau riwayat per-karyawan.
- Tujuan MVP: **katalog + penjadwalan + pencatatan peserta/kehadiran** yang terlacak per departemen, sebagai fondasi sebelum fitur lanjut (evaluasi→KPI, sertifikat, request/approval).
- **ERPGo** dipakai sebagai referensi struktur (seperti pada [[HRIS - Recruitment]] yang mengadopsi struktur ERPGo secara selektif), **bukan** cetak biru wajib — beberapa konsepnya tidak cocok dengan kondisi kita (lihat adaptasi di bawah).

## Ruang Lingkup — MVP (Direncanakan)

Tiga entitas inti + peserta, mengikuti pola master→transaksi:

1. **Training Types** (master) — katalog jenis/kategori pelatihan (mis. "Teknis Produksi", "Leadership", "K3"). Lookup sederhana.
2. **Trainers** (master) — pengajar/instruktur, **internal** (tautan ke karyawan) atau **eksternal** (free-form).
3. **Training** (transaksi) — event pelatihan: judul, jenis, trainer, jadwal, lokasi, kapasitas, status lifecycle, departemen penyelenggara.
4. **Peserta & Kehadiran** — penugasan karyawan ke sebuah training + tandai hadir/tidak (dasar untuk riwayat per-karyawan).

Di luar MVP (fase lanjut) → lihat **Rollout Bertahap** & **TBD**.

## Adaptasi dari ERPGo (Ambil / Sesuaikan / Buang)

| Fitur ERPGo | Keputusan | Alasan (grounded) |
|---|---|---|
| **Training Types** (master) | ✅ **Ambil** | Pola sama dengan lookup `job_type`/`interview_type` di [[Microservices - Recruitment Service]] |
| **Trainers** (master) | ✅ **Ambil + sesuaikan** | Bedakan **internal** (`employee_id` → reuse master karyawan) vs **eksternal** (nama/kontak bebas). Kontak: **nomor lokal**, buang wajib `+[kode negara]` |
| **Training List** (transaksi) | ✅ **Ambil core** | Field inti: Title · Type · Trainer · Status · Start/End Date · Start/End Time · Max Participants · Location · Cost · Description |
| **Branch → Department** (dependent filter) | 🔧 **Buang Branch, sisakan Department** | Perusahaan **single-site**; org unit = `master_department` di [[Microservices - Employee Service]]. Tidak ada entitas Branch. Ini adaptasi terpenting |
| Field **Cost** | 🔧 **Ambil sebagai informasional** | Tidak diintegrasikan ke akunting — pembukuan via Accurate ([[ADR - 0001 Akuntansi via Accurate]]). Berguna untuk perencanaan anggaran, bukan jurnal |
| **Status** lifecycle (Scheduled/Ongoing/Completed/Cancelled) | ✅ **Ambil** | Indikator pelacakan utama; cocok apa adanya |
| **AI assist** generate Description | 🟡 **Tunda (opsional/TBD)** | Infra LLM ada (reuse Ideamills), tapi bukan prioritas MVP; tim cenderung hindari fitur over-engineered yang jarang terpakai |
| **Grid/List view toggle** | 🟡 **Tunda (kosmetik)** | Detail UI, bukan prioritas MVP |
| Search / filter / pagination | ✅ **Ambil** | Standar list; murah |

**Tambahan di luar list ERPGo** (tidak tampak di daftar ERPGo tapi cocok & sudah ada polanya di ekosistem) — **peserta & kehadiran** masuk MVP; sisanya fase lanjut:

- **Peserta & kehadiran** (MVP) — penugasan karyawan + tandai hadir; dasar riwayat per-karyawan.
- **Evaluasi pasca-pelatihan** (fase lanjut) — rating **purpose-built** (bukan form builder — sejalan keputusan sadar di [[HRIS - Recruitment]] yang membuang `custom_question`), umpan ke [[HRIS - Key Performance Index]].
- **Sertifikat PDF** (fase lanjut) — simpan ke MinIO via [[Microservices - File Service]] (pola sama report psikotes di Recruitment).
- **Request/approval pelatihan** (fase lanjut) — karyawan/SPV mengajukan → approval, ikut pola [[HRIS - Employee Request & Approval]].
- **Notifikasi undangan/reminder** (fase lanjut) — via [[Microservices - Notification Service]] (inbox/FCM/email).

## Model Data (desain MVP; kini dibangun di `learning_db`)

Semula diusulkan sebagai collection baru di database Employee Service. Keempat koleksi MVP di bawah **sudah dibangun** dan kini tinggal di `learning_db` milik [[Microservices - Learning Service]], yang juga memuat koleksi lanjutan (`training_request`, `trainer_evaluation`, `course`, `quiz`, `quiz_attempt`).

- **`training_type`** — `{ name, description?, department_key?, is_active }`. Lookup; `department_key` opsional (merujuk `master_department.key`, bukan Branch).
- **`trainer`** — `{ name, is_internal, employee_id?, contact?, email?, experience?, expertise?, qualification?, department_key?, is_active }`. Bila `is_internal=true`, `employee_id` menautkan ke karyawan (reuse master); bila eksternal, isi manual.
- **`training`** — `{ title, training_type_id, trainer_id, status, department_key, start_date, end_date, start_time, end_time, max_participants?, location?, cost?, description? }`. `status ∈ {Scheduled, Ongoing, Completed, Cancelled}`. `department_key` → `master_department` (pengganti Branch+Department ERPGo). `max_participants` = **cap keras** (penugasan peserta ditolak bila kuota penuh).
- **`training_participant`** (MVP) — `{ training_id, employee_id, attended (boolean), enrolled_at }`. Relasi karyawan↔training; `attended` = **hadir/tidak** (boolean, cukup untuk MVP); dasar kehadiran & riwayat.
- *(fase lanjut)* ~~`training_evaluation`~~ dibangun sebagai `trainer_evaluation` (peserta menilai trainer) · `training_request` (pengajuan + approval, dibangun) · `training_certificate` (ref file MinIO, **belum ada**).

> **Prinsip reuse:** dropdown Department memakai master `master_department` yang sudah ada; picker peserta/trainer-internal memakai feed karyawan (`GET /list?type=employee` / aggregate) di [[Microservices - Employee Service]] — **jangan** bikin master karyawan/departemen tandingan (lihat pola pada [[HRIS - Organization Structure]]).

## Alur Proses Bisnis (MVP)

1. **Persiapan master** — HR/HRD mendaftarkan **Training Types** (katalog) & **Trainers** (internal/eksternal) sekali di awal, lalu dipelihara.
2. **Penjadwalan** — HR membuat entri **Training** (pilih Type + Trainer, tentukan jadwal tanggal/jam, lokasi, kapasitas, biaya, departemen penyelenggara). Status awal **Scheduled**.
3. **Penugasan peserta** — HR menautkan karyawan sebagai **peserta** (dari master karyawan; bisa per-individu / per-departemen).
4. **Eksekusi & monitoring** — status mengikuti siklus **Scheduled → Ongoing → Completed** (atau **Cancelled**). Saat/'sesudah acara, HR menandai **kehadiran** peserta.
5. **Riwayat** — dari `training_participant`, muncul **riwayat pelatihan per-karyawan** (fondasi untuk umpan KPI & pengembangan karir di fase lanjut).

**Karakteristik:** seluruh entitas tersegmentasi per **Department** (bukan Branch). Field **Cost** = **informasional** (perencanaan anggaran; tanpa integrasi akunting). **Max Participants** = **cap keras** — penugasan peserta ditolak saat kuota penuh; `0` berarti tanpa batas.

> ⚠️ Kalimat "cap keras" di atas **tidak benar sampai 2026-08-10**. Kolomnya dikumpulkan, disimpan, dan disebut cap keras di tiga tempat sekaligus (komentar field, komentar rute, dan dokumen ini) sementara `CanEnroll` tak pernah menerima kapasitasnya — HR mengisi kuota 20, orang ke-21 masuk tanpa keluhan apa pun. Ditegakkan di PR [#1147](https://github.com/bip-itteam-internal/bip-erp/pull/1147). Dicatat, bukan dihapus: dokumentasi yang menyatakan aturan yang tak ditegakkan kode adalah kelas kesalahan tersendiri, dan menghapus jejaknya menghapus juga pelajarannya.

## Aktor & Role / Persona

> Grounded ke RBAC nyata: `system_roles` = hak akses **modul** (key = kode modul, mis. `hris`), supervisor per divisi ada di `work_data.is_supervisor` — bukan di `system_roles`. Lihat [[HRIS - Organization Structure]].

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| **HR Training Officer** — pemilik proses | HRIS | kelola master (Types/Trainers) + CRUD Training + peserta/kehadiran; **keputusan final** pengajuan pelatihan. Izin modul `training.view` / `training.work` / `training.manage`, dengan tier `hris` sebagai cadangan selama `TRAINING_TIER_FALLBACK` menyala; menu **Pelatihan**, **Pengaturan Pelatihan**, dan **Persetujuan Pelatihan** | Web ERP |
| **SPV / Kepala Departemen** — pengusul & approver-1 (✅ dibangun 2026-08-10) | Divisi masing-masing | usulkan pelatihan untuk timnya + **setujui pengajuan** anggota tim; lihat training departemennya | Web ERP / mobile |
| ~~**Direktur** — approver akhir~~ | Pimpinan | ⛔ **tidak dibangun**: rantai dibangun dua tahap SPV → HR (lihat Fase lanjut C) | n/a |
| **Karyawan** — peserta | Semua divisi | lihat pelatihannya + riwayat, hadir mandiri, nilai trainer, ajukan pelatihan (sisi aplikasi merged ke `dev`, belum di rilis GitHub terbaru) | [[APP - MyBharata]] |

- **Tujuan HR Training Officer**: satu tempat mengelola katalog, jadwal, & peserta yang terlacak per departemen.
- **Pain saat ini**: data tersebar di spreadsheet; tak ada riwayat/kehadiran terpusat.
- **Aksi utama**: definisikan Type/Trainer → buat Training → tugaskan peserta → update status & kehadiran.

> **Posisi di master data**: `Training & Perfomance Officer` (departemen Human Resource; ejaan typo tersimpan apa adanya). Kategori menu web yang sama, **People Development** (`erp-frontend` `src/components/layout/sidebar-menus.tsx:1168-1231`), juga memuat **KPI Scoring** dan **KPI Templates**, dan akun posisi ini tercatat menginput skor KPI departemen lain ([[HRIS - Matriks KPI per Departemen]]). Sisi *performance* jabatannya karena itu dilayani [[HRIS - Key Performance Index]], bukan modul ini.

## Penempatan Arsitektur

✅ **Keputusan akhir (2026-08-06): service `learning` sendiri** — [[Microservices - Learning Service]], MongoDB `learning_db`, modul gateway `learning`.

Pemicunya bukan ukuran modul Training, melainkan arah LMS: kelas tatap muka dan belajar mandiri harus **berbagi satu angka progres**. Bila keduanya tinggal di service berbeda, tiap perhitungan progres jadi panggilan lintas-service. Sesuai [[ADR - 0002 Database-per-Service]], modul baru = service + database sendiri.

⚠️ **Pelajaran dari pemindahannya**: "pindahkan apa adanya" ternyata tidak cukup. `verifyTrainingRefs` diam-diam mengueri koleksi `master_department` yang **dimiliki Employee Service**, sehingga setelah pindah kueri itu mengarah ke database yang tidak memilikinya dan setiap pelatihan berdepartemen ditolak "department not found". Diganti panggilan HTTP internal. Tiap handler yang dipindah antar-service wajib diaudit kueri Mongo-nya satu per satu.

<details><summary>Usulan lama (2026, sebelum LMS diputuskan): perluas Employee Service</summary>

Alasan yang dipakai saat itu, disimpan sebagai jejak keputusan:

- Employee Service **sudah** memegang master org (`master_department`), master karyawan (`work_data`), dan **MinIO upload** — semua yang dibutuhkan Training tinggal reuse, tanpa duplikasi data lintas-service.
- Sudah ada helper RBAC (`RequireHRISStaff`, `RequireHRISOrITSupervisor`) & feed karyawan (`GET /list`) → picker peserta/trainer-internal langsung tersedia.
- Konsisten dengan stack: Go + Fiber v2 + MongoDB, di belakang [[CORE - API Master Gateway]] + SSO ([[CORE - SSO Flow]]).
- **Trade-off** (disadari): menambah beban ke service terbesar; alternatif microservice terpisah (pola [[Microservices - Recruitment Service]], sesuai [[ADR - 0002 Database-per-Service]]) tetap opsi bila modul Training tumbuh besar (evaluasi/sertifikat/request kompleks). Untuk **MVP**, extend Employee Service dipilih demi kecepatan & reuse master.

*Trade-off terakhir itulah yang akhirnya terjadi: modul memang tumbuh, dan pemisahannya dieksekusi di LMS Fase 0.*

</details>

## Keputusan (dikonfirmasi sesi ini)

- **Cakupan** = **MVP inti** (Types + Trainers + Training + peserta/kehadiran) + roadmap bertahap; fitur lanjut ditunda.
- **Penempatan** = ~~perluas Employee Service~~ → **service `learning` sendiri** sejak 2026-08-06 ([[Microservices - Learning Service]]).
- **Branch dibuang** (adaptasi ERPGo). **Department = OPSIONAL** (peran *Penyelenggara*) — **tidak** membatasi peserta; peserta lintas semua departemen, di-assign HRD. *(Revisi: semula wajib satu dept.)*
- **Cost** informasional (tanpa integrasi akunting; Accurate = [[ADR - 0001 Akuntansi via Accurate]]).
- **Evaluasi** (bila dibangun) = **purpose-built**, bukan form builder.
- **Pemilik proses** = **HR Training Officer** (kelola master + transaksi + keputusan final pengajuan).
- **Kehadiran** = **boolean hadir/tidak** (cukup untuk MVP; tanpa status izin/jam).
- ~~**Kapasitas** = **otomatis mengikuti jumlah peserta yang di-assign** (cap keras `max_participants` **dibuang**)~~ → **dibalik kode**: kuota `max_participants` ditegakkan sejak PR [#1147](https://github.com/bip-itteam-internal/bip-erp/pull/1147) (2026-08-10), `0` = tanpa batas (`CanEnroll`, `services/learning/models_training.go`). Assign tetap via **multi-select** karyawan.
- ~~**Approval pengajuan pelatihan** = **SPV → HR Training Officer → Direktur**~~ → **dibangun dua tahap SPV → HR** (lihat Fase lanjut C), tetap **administratif** (Cost informasional, **tanpa** approval anggaran / integrasi keuangan).

## Implementasi (BE+FE — ✅ live di dev + produksi 2026-08-06)

*Kini di [[Microservices - Learning Service]] (`services/learning/training.go` + model/validasi di `services/learning/models_training.go`) + UI [[APP - Web ERP]] (`src/features/hris/training/*`, memanggil `/api/learning/training/*`). Endpoint lengkap: [[API - Learning Service]].*

> Berkas lamanya (`services/employee/training.go`, `shared-library/models/employee/training.go`) sudah **dihapus**. Data 4 koleksi dipindah ke `learning_db` di dev dan produksi, jumlah terverifikasi cocok, salinan lama di `employee_db` sengaja dibiarkan sebagai jalan pulang.

- **Master** ✅ — CRUD `/training/types` & `/training/trainers` (internal/eksternal).
- **Transaksi** ✅ — CRUD `/training` (filter Department+Status), cek FK, guard transisi status, delete cascade.
- **Peserta & kehadiran** ✅ — **assign multi-select** (lintas dept), unique index anti-duplikat, kuota `max_participants` ditegakkan sejak 2026-08-10 (`0` = tanpa batas), kehadiran boolean oleh HR atau hadir mandiri berjendela waktu, riwayat per-karyawan.
- **Validasi murni + unit test** ✅ — `ValidateTraining`, `CanEnroll`, `IsValidStatusTransition`, `validateTrainer`.
- **Frontend** ✅ — `/hris/training` (list + form) + dialog peserta (multi-select, reuse `MultiEmployeeSelect`) di menu **Pelatihan** kategori People Development. Master jenis & trainer pindah ke **Pengaturan > Pengaturan Pelatihan** (`/pengaturan/people-development`); rute lama `/hris/training/masters` meneruskan ke sana (`src/features/hris/pengaturan/lib/rute-lama.ts:16`). Antrean pengajuan di **Portal Saya > Persetujuan Pelatihan** (`/hris/training/requests`, `src/components/layout/portal-menu.ts:66`). Live dan terverifikasi lewat gateway sejak 2026-08-19.
- **Backlog/hardening** (dari /review): PUT = full-replace (FE wajib kirim objek lengkap); enroll belum cek employee ada di `work_data`; list tanpa pagination; `department_key` beda konvensi (vs nama di KPI/`work_data`); resolusi route `/training/:id` bergantung urutan registrasi Fiber (statik didaftarkan lebih dulu).

## Rollout Bertahap (Usulan)

- [x] **MVP-1 — Master** (✅ BE+FE) — `training_type` + `trainer` (internal/eksternal) CRUD.
- [x] **MVP-2 — Transaksi** (✅ BE+FE) — `training` CRUD + list (filter Department+Status) + status lifecycle.
- [x] **MVP-3 — Peserta & Kehadiran** (✅ BE+FE) — assign multi-select + tandai hadir + **riwayat per-karyawan**.
- [x] **Fase lanjut A — Evaluasi pasca-pelatihan** (✅ BE, 2026-08-10, PR [#1149](https://github.com/bip-itteam-internal/bip-erp/pull/1149)) — **peserta menilai trainer**, empat aspek tetap 1..5. Agregat baru tampil setelah **minimal 3 responden** dan identitas penilai tak pernah keluar, sebab trainer internal bisa jadi atasan pesertanya sendiri. Umpan ke [[HRIS - Key Performance Index]] **belum** disambung (per 2026-09-15 nol sumber KPI yang membaca `learning_db`). FE **sudah ada** ([erp-frontend#968](https://github.com/bip-itteam-internal/erp-frontend/pull/968), agregat di halaman Pelatihan) — catatan lama "FE belum ada" sudah tidak berlaku. Terpakai: **0 penilaian** di produksi 2026-08-19, dan masih **0** per 2026-09-15.
- [ ] **Fase lanjut B** — **Sertifikat PDF** (MinIO via [[Microservices - File Service]]). Per 2026-09-15 belum ada kode sertifikat di service `learning` (satu-satunya kemunculan kata *certificate* adalah paket `ca-certificates` di Dockerfile).
- [x] **Fase lanjut C — Request/approval pelatihan** (✅ BE, 2026-08-10, PR [#1148](https://github.com/bip-itteam-internal/bip-erp/pull/1148)) — rantainya **SPV → HR**, ⚠️ **bukan** SPV → HR → Direktur seperti tertulis semula. [[HRIS - Recruitment]] pernah memakai bentuk tiga tahap itu lalu membuang tahap Direktur; meminta pelatihan lebih ringan daripada meminta tambahan karyawan, jadi membuatnya lebih berat akan terbalik. `estimated_cost` disimpan supaya ambang biaya bisa ditambahkan tanpa migrasi. Notifikasi memakai kategori `request-*` yang sudah ada ([[Microservices - Notification Service]]), jadi tanpa deploy dua container. FE **sudah ada** ([erp-frontend#967](https://github.com/bip-itteam-internal/erp-frontend/pull/967)) — catatan lama "FE belum ada" sudah tidak berlaku, tapi sejak 2026-08-13 yang tersisa di web adalah **antrean persetujuan**; sisi mengajukan pindah ke my-bharata [#115](https://github.com/bip-itteam-internal/my-bharata/pull/115) (merged ke `dev` 2026-08-22, belum di rilis GitHub terbaru). Terpakai: **0 pengajuan** di produksi 2026-08-19, dan masih **0** per 2026-09-15.
- [ ] **Fase lanjut D (opsional)** — AI assist deskripsi · grid view · integrasi ke [[HRIS - Career & Promotion]] / [[HRIS - Work Review]].
- [ ] **Feed kalender** — pelatihan belum muncul di [[Microservices - Calendar Service]]. Service `learning` tak punya `GET /internal/calendar-feed` (nol kemunculan, sementara attendance, employee, dan finance punya; diperiksa 2026-09-15), padahal fitur bertanggal wajib mendaftarkan feed ke kalender terpusat, bukan membuat kalender sendiri.
- [ ] **Sumber KPI dari data pelatihan** — nol sumber KPI yang membaca `learning_db` (`services/employee/kpi_*.go`, kontrol positif `tiket` = 10 berkas; diperiksa 2026-09-15), dan service `learning` tak punya rute `/internal/`. Metrik yang menunggunya dirinci di [[HRIS - Matriks KPI per Departemen]] (bab Training & Perfomance Officer).
- [ ] **Rencana pelatihan** — tak ada entitas rencana (tahunan maupun bulanan) di `learning_db`; koleksinya per 2026-09-15 hanya `training_type`, `trainer`, `training`, `training_participant`, `training_request`, `trainer_evaluation`, `quiz`, `quiz_attempt`. Metrik "terlaksana sesuai rencana" karena itu tak punya pembanding.
- [ ] ⚠️ **LMS Fase 1 dan seterusnya — SEBAGIAN.** **Sudah ada**: post-test berskor (course tipis, bank soal terpisah dari course, snapshot soal dan identitas, batas waktu ditegakkan server, pembatalan bertanda alasan, ekspor CSV), PR [#1321](https://github.com/bip-itteam-internal/bip-erp/pull/1321) merged 2026-08-20 dan ada di biner produksi; koleksi `quiz` dan `quiz_attempt` terbentuk tetapi **0 dokumen**, `course` belum terbentuk (2026-09-15); **tanpa layar** di web maupun MyBharata. **Belum ada**: `curriculum`, `course_progress`, `learning_setting`, `talent_candidate`, `position_tenure` (nol berkas di `services` dan `shared-library`, kontrol positif `quiz_attempt` = 2 berkas), pre-test (jenis `pre` ada di model tetapi seluruh rute hanya melayani `post`), unggah materi ke MinIO, cron `position_tenure`, dan subdomain e-learning. Catatan lama "belum ada kode sama sekali" (diperiksa 2026-08-19) benar pada hari itu; PR #1321 merged sehari kemudian. **Nama service `learning` tetap mudah disalahbaca sebagai "LMS sudah jalan"**: yang live adalah modul Pelatihan plus mesin post-test. Rincian: [[Microservices - Learning Service]].

## Belum Diputuskan (TBD)

> *Sebagian TBD sebelumnya sudah diputuskan — lihat **Keputusan** (pemilik proses, kehadiran, kapasitas, rantai approval).*

- ~~**Evaluasi**: aspek yang dinilai; siapa menilai~~ — **diputuskan & dibangun 2026-08-10**: peserta menilai trainer, empat aspek tetap tanpa bobot. Arahnya sengaja satu — menilai peserta sudah jadi urusan post-test nanti, dan menambahkan penilaian trainer atas peserta melahirkan dua angka yang mengukur hal sama dengan cara tak sebanding. **Yang masih terbuka**: apakah hasilnya masuk KPI, dan bagaimana agregat di bawah 3 responden ditampilkan di layar (server sudah menyembunyikan angkanya).
- **Sertifikasi/kompetensi**: apakah dilacak sebagai kompetensi karyawan (link ke [[HRIS - Career & Promotion]]).
- **Trigger onboarding**: apakah karyawan baru ([[HRIS - Recruitment]]) otomatis di-enroll pelatihan awal.
- **Penuh-kuota**: perilaku saat `max_participants` tercapai — tolak keras + waitlist, atau tolak saja? (default MVP: tolak tanpa waitlist).

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]] · [[HRIS - Roadmap]] (Fase E) · [[HRIS - Analysis]]
- [[HRIS - Organization Structure]] (master Department — pengganti Branch) · [[HRIS - Key Performance Index]] (umpan evaluasi) · [[HRIS - Career & Promotion]] · [[HRIS - Work Review]] · [[HRIS - Employee Request & Approval]] (pola approval)
- [[Microservices - Learning Service]] (host modul) · [[Microservices - Employee Service]] (master karyawan/departemen) · [[Microservices - Notification Service]] · [[Microservices - File Service]] (sertifikat) · [[Microservices - Calendar Service]] (feed yang belum didaftarkan)
- [[HRIS - Matriks KPI per Departemen]] (metrik KPI yang menunggu data pelatihan)
- [[Microservices - Recruitment Service]] — contoh adopsi struktur ERPGo secara selektif
- [[ADR - 0001 Akuntansi via Accurate]] (batas scope biaya) · [[ADR - 0002 Database-per-Service]] (opsi service terpisah)
- [[APP - Web ERP]] · [[APP - MyBharata]]
