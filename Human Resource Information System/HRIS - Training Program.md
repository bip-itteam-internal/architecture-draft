## Deskripsi

*Manajemen program **pelatihan & pengembangan karyawan** (training & development). Dokumen ini menaikkan status dari konsep-mentah menjadi **usulan desain MVP** — hasil adaptasi modul **Training ERPGo** ke kondisi Bharata. **Backend & Frontend MVP sudah diimplementasi & merged ke main**, grounded ke pola service & master data yang ada. **Cakupan sengaja dibatasi ke MVP inti**; fitur lanjut ditandai fase-lanjut/TBD.*

- **Status**: ⚠️ **MVP implemented & merged ke main** (BE bip-erp #545/#550 + FE erp-frontend #390/#391; refine FE #396) — endpoint di [[Microservices - Employee Service]] · [[API - Employee Service]], UI `/hris/training`. **Deploy dev + smoke test masih pending**. Desain di bawah = acuan.
- **Referensi bentuk**: modul **Training ERPGo** (3 sub-menu: Training Types · Trainers · Training List) — diambil selektif, **bukan** disalin utuh
- **Penempatan usulan**: perluasan [[Microservices - Employee Service]] (bukan microservice baru) — lihat **Penempatan Arsitektur**
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

## Model Data (Usulan — di Employee Service)

Collection baru di database Employee Service (MongoDB), sejajar dengan `master_department`. **Semua TBD** sampai disetujui & dibangun.

- **`training_type`** — `{ name, description?, department_key?, is_active }`. Lookup; `department_key` opsional (merujuk `master_department.key`, bukan Branch).
- **`trainer`** — `{ name, is_internal, employee_id?, contact?, email?, experience?, expertise?, qualification?, department_key?, is_active }`. Bila `is_internal=true`, `employee_id` menautkan ke karyawan (reuse master); bila eksternal, isi manual.
- **`training`** — `{ title, training_type_id, trainer_id, status, department_key, start_date, end_date, start_time, end_time, max_participants?, location?, cost?, description? }`. `status ∈ {Scheduled, Ongoing, Completed, Cancelled}`. `department_key` → `master_department` (pengganti Branch+Department ERPGo). `max_participants` = **cap keras** (penugasan peserta ditolak bila kuota penuh).
- **`training_participant`** (MVP) — `{ training_id, employee_id, attended (boolean), enrolled_at }`. Relasi karyawan↔training; `attended` = **hadir/tidak** (boolean, cukup untuk MVP); dasar kehadiran & riwayat.
- *(fase lanjut)* `training_evaluation` (rating purpose-built), `training_certificate` (ref file MinIO), `training_request` (pengajuan+approval).

> **Prinsip reuse:** dropdown Department memakai master `master_department` yang sudah ada; picker peserta/trainer-internal memakai feed karyawan (`GET /list?type=employee` / aggregate) di [[Microservices - Employee Service]] — **jangan** bikin master karyawan/departemen tandingan (lihat pola pada [[HRIS - Organization Structure]]).

## Alur Proses Bisnis (MVP)

1. **Persiapan master** — HR/HRD mendaftarkan **Training Types** (katalog) & **Trainers** (internal/eksternal) sekali di awal, lalu dipelihara.
2. **Penjadwalan** — HR membuat entri **Training** (pilih Type + Trainer, tentukan jadwal tanggal/jam, lokasi, kapasitas, biaya, departemen penyelenggara). Status awal **Scheduled**.
3. **Penugasan peserta** — HR menautkan karyawan sebagai **peserta** (dari master karyawan; bisa per-individu / per-departemen).
4. **Eksekusi & monitoring** — status mengikuti siklus **Scheduled → Ongoing → Completed** (atau **Cancelled**). Saat/'sesudah acara, HR menandai **kehadiran** peserta.
5. **Riwayat** — dari `training_participant`, muncul **riwayat pelatihan per-karyawan** (fondasi untuk umpan KPI & pengembangan karir di fase lanjut).

**Karakteristik:** seluruh entitas tersegmentasi per **Department** (bukan Branch). Field **Cost** = **informasional** (perencanaan anggaran; tanpa integrasi akunting). **Max Participants** = **cap keras** — penugasan peserta ditolak saat kuota penuh.

## Aktor & Role / Persona

> Grounded ke RBAC nyata: `system_roles` = hak akses **modul** (key = kode modul, mis. `hris`), supervisor per divisi ada di `work_data.is_supervisor` — bukan di `system_roles`. Lihat [[HRIS - Organization Structure]].

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| **HR Training Officer** — pemilik proses | HRIS | kelola master (Types/Trainers) + CRUD Training + peserta/kehadiran; **keputusan final** pengajuan pelatihan (`RequireHRISStaff`) | Web ERP |
| **SPV / Kepala Departemen** — pengusul & approver-1 (fase lanjut) | Divisi masing-masing | usulkan pelatihan untuk timnya + **setujui pengajuan** anggota tim; lihat training departemennya | Web ERP / mobile |
| **Direktur** — approver akhir (fase lanjut) | Pimpinan | **persetujuan akhir** pengajuan pelatihan (tahap ke-3) | Web ERP / mobile |
| **Karyawan** — peserta | Semua divisi | lihat jadwal pelatihannya + riwayat; *(fase lanjut)* ajukan pelatihan, isi evaluasi | Web ERP / [[APP - MyBharata]] |

- **Tujuan HR Training Officer**: satu tempat mengelola katalog, jadwal, & peserta yang terlacak per departemen.
- **Pain saat ini**: data tersebar di spreadsheet; tak ada riwayat/kehadiran terpusat.
- **Aksi utama**: definisikan Type/Trainer → buat Training → tugaskan peserta → update status & kehadiran.

## Penempatan Arsitektur

**Usulan: perluas [[Microservices - Employee Service]]** (bukan microservice baru). Grounded:

- Employee Service **sudah** memegang master org (`master_department`), master karyawan (`work_data`), dan **MinIO upload** — semua yang dibutuhkan Training tinggal reuse, tanpa duplikasi data lintas-service.
- Sudah ada helper RBAC (`RequireHRISStaff`, `RequireHRISOrITSupervisor`) & feed karyawan (`GET /list`) → picker peserta/trainer-internal langsung tersedia.
- Konsisten dengan stack: Go + Fiber v2 + MongoDB, di belakang [[CORE - API Master Gateway]] + SSO ([[CORE - SSO Flow]]).
- **Trade-off** (disadari): menambah beban ke service terbesar; alternatif microservice terpisah (pola [[Microservices - Recruitment Service]], sesuai [[ADR - 0002 Database-per-Service]]) tetap opsi bila modul Training tumbuh besar (evaluasi/sertifikat/request kompleks). Untuk **MVP**, extend Employee Service dipilih demi kecepatan & reuse master.

## Keputusan (dikonfirmasi sesi ini)

- **Cakupan** = **MVP inti** (Types + Trainers + Training + peserta/kehadiran) + roadmap bertahap; fitur lanjut ditunda.
- **Penempatan** = **perluas Employee Service** (bukan service baru) untuk MVP.
- **Branch dibuang** (adaptasi ERPGo). **Department = OPSIONAL** (peran *Penyelenggara*) — **tidak** membatasi peserta; peserta lintas semua departemen, di-assign HRD. *(Revisi: semula wajib satu dept.)*
- **Cost** informasional (tanpa integrasi akunting; Accurate = [[ADR - 0001 Akuntansi via Accurate]]).
- **Evaluasi** (bila dibangun) = **purpose-built**, bukan form builder.
- **Pemilik proses** = **HR Training Officer** (kelola master + transaksi + keputusan final pengajuan).
- **Kehadiran** = **boolean hadir/tidak** (cukup untuk MVP; tanpa status izin/jam).
- **Kapasitas** = **otomatis mengikuti jumlah peserta yang di-assign** (cap keras `max_participants` **dibuang**); assign via **multi-select** karyawan. *(Revisi keputusan lama.)*
- **Approval pengajuan pelatihan** (fase lanjut) = **SPV → HR Training Officer → Direktur**, bersifat **administratif** (Cost informasional, **tanpa** approval anggaran / integrasi keuangan).

## Implementasi (BE+FE — ✅ merged ke main; deploy dev pending)

*Dibangun sebagai perluasan [[Microservices - Employee Service]] (`services/employee/training.go` + model/validasi di `shared-library/models/employee/training.go`) + UI [[APP - Web ERP]] (`src/features/hris/training/*`). Endpoint lengkap: [[API - Employee Service]] §Training Program.*

- **Master** ✅ — CRUD `/training/types` & `/training/trainers` (internal/eksternal).
- **Transaksi** ✅ — CRUD `/training` (filter Department+Status), cek FK, guard transisi status, delete cascade.
- **Peserta & kehadiran** ✅ — **assign multi-select** (lintas dept), unique index anti-duplikat, **tanpa cap keras** (kapasitas = jumlah peserta), kehadiran boolean, riwayat per-karyawan.
- **Validasi murni + unit test** ✅ — `ValidateTraining`, `CanEnroll`, `IsValidStatusTransition`, `validateTrainer`.
- **Frontend** ✅ — `/hris/training` (list + form) & `/hris/training/masters` + dialog peserta (multi-select, reuse `MultiEmployeeSelect`) + menu nav (grup People Development). **Belum**: deploy manual ke dev + smoke test live.
- **Backlog/hardening** (dari /review): PUT = full-replace (FE wajib kirim objek lengkap); enroll belum cek employee ada di `work_data`; list tanpa pagination; `department_key` beda konvensi (vs nama di KPI/`work_data`); resolusi route `/training/:id` bergantung urutan registrasi Fiber (statik didaftarkan lebih dulu).

## Rollout Bertahap (Usulan)

- [x] **MVP-1 — Master** (✅ BE+FE) — `training_type` + `trainer` (internal/eksternal) CRUD.
- [x] **MVP-2 — Transaksi** (✅ BE+FE) — `training` CRUD + list (filter Department+Status) + status lifecycle.
- [x] **MVP-3 — Peserta & Kehadiran** (✅ BE+FE) — assign multi-select + tandai hadir + **riwayat per-karyawan**.
- [ ] **Fase lanjut A** — **Evaluasi pasca-pelatihan** (rating purpose-built) → umpan [[HRIS - Key Performance Index]].
- [ ] **Fase lanjut B** — **Sertifikat PDF** (MinIO via [[Microservices - File Service]]).
- [ ] **Fase lanjut C** — **Request/approval pelatihan** (rantai **SPV → HR Training Officer → Direktur**, administratif; pola [[HRIS - Employee Request & Approval]]) + **notifikasi** ([[Microservices - Notification Service]]).
- [ ] **Fase lanjut D (opsional)** — AI assist deskripsi · grid view · integrasi ke [[HRIS - Career & Promotion]] / [[HRIS - Work Review]].

## Belum Diputuskan (TBD)

> *Sebagian TBD sebelumnya sudah diputuskan — lihat **Keputusan** (pemilik proses, kehadiran, kapasitas, rantai approval).*

- **Evaluasi**: aspek yang dinilai & bobot; siapa menilai (peserta menilai trainer, atau trainer/HR menilai peserta, atau keduanya?); apakah hasil masuk KPI.
- **Sertifikasi/kompetensi**: apakah dilacak sebagai kompetensi karyawan (link ke [[HRIS - Career & Promotion]]).
- **Trigger onboarding**: apakah karyawan baru ([[HRIS - Recruitment]]) otomatis di-enroll pelatihan awal.
- **Penuh-kuota**: perilaku saat `max_participants` tercapai — tolak keras + waitlist, atau tolak saja? (default MVP: tolak tanpa waitlist).

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]] · [[HRIS - Roadmap]] (Fase E) · [[HRIS - Analysis]]
- [[HRIS - Organization Structure]] (master Department — pengganti Branch) · [[HRIS - Key Performance Index]] (umpan evaluasi) · [[HRIS - Career & Promotion]] · [[HRIS - Work Review]] · [[HRIS - Employee Request & Approval]] (pola approval)
- [[Microservices - Employee Service]] (host usulan + master karyawan/departemen) · [[Microservices - Notification Service]] · [[Microservices - File Service]] (sertifikat)
- [[Microservices - Recruitment Service]] — contoh adopsi struktur ERPGo secara selektif
- [[ADR - 0001 Akuntansi via Accurate]] (batas scope biaya) · [[ADR - 0002 Database-per-Service]] (opsi service terpisah)
- [[APP - Web ERP]] · [[APP - MyBharata]]
