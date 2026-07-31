## Deskripsi

*Struktur organisasi perusahaan — departemen, posisi/jabatan, dan hierarki (atasan/SPV). **Departemen dan posisi** kini dikelola sebagai master data di MongoDB (`master_department`) dengan CRUD endpoint dan halaman admin di frontend. Data karyawan tetap di `work_data`. Visualisasi org chart formal belum ada.*

- **Status**: ⚠️ Implemented (ada catatan) — master departemen/posisi sudah di-DB; org chart belum

## Ruang Lingkup

- **Departemen** — dikelola di collection `master_department` (`key`, `name`, `positions[]`, `position_items[]`, `roles[]`, `company_id`, `supervised_by`, `supervision_label`); CRUD via `GET/POST/PUT/DELETE /master/departments` di [[Microservices - Employee Service]]
- **Posisi/jabatan** per departemen — tersimpan sebagai array `positions` di setiap dokumen `master_department`; sebelumnya hardcoded (`PositionTitle*` di shared-library), sekarang dapat ditambah/ubah via API atau frontend `/hris/master-data`
	- **`position_items[]` — jabatan sebagai entitas ber-identitas** ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]). Tiap item `{key, name, permission_sets[]}`: `key` slug stabil yang **tidak berubah walau namanya diganti**, sehingga paket hak yang menempel tak lepas saat jabatan di-rename; `permission_sets` = paket hak yang diwarisi setiap karyawan berjabatan itu, digabung dengan paket milik akun saat login (union, reach tertinggi). Sengaja **hidup berdampingan** dengan `positions[]` (array nama) yang tetap jadi sumber jawaban `/data-type/position`; `positions[]` dibuang nanti setelah semua pembaca pindah. `SyncPositionItems` menjaga keduanya selaras sambil mempertahankan key dan paket hak yang sudah ada.
	- Sisi karyawan: `work_data.position` (nama, untuk tampilan/laporan/template KPI) + `work_data.position_key` (kunci pencocokan paket hak). Kosong pada data lama sebelum migrasi → pemanggil jatuh ke pencocokan by nama.
- **Departemen ter-scope per perusahaan** — `master_department.company_id` ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]). **`key` unik PER perusahaan, bukan global**; kosong pada data lama berarti BIP. Perusahaan baru mulai dengan daftar departemen kosong. Endpoint `/data-type/department`, `/data-type/position`, dan `/master/departments` menyaring memakai `EffectiveCompanyID`. ⚠️ Supervisi/RBAC (`allMasterDepartments`, `system-list`) sengaja **tetap global**, jadi jangan disamakan dengan penyaringan tampilan.
- **System roles** — role per department (staff, supervisor, admin, security) dan feature-based roles (insentive, integration) dikelola di `master_department.roles` dan `master_system_role`
- **Hierarki/atasan** — relasi supervisor per divisi (dipakai di banyak approval, mis. `getSupervisorData`)
	- **Atasan LANGSUNG per orang** (`work_data.supervisor_id`) — dihidupkan 2026-07-31 (branch `feat/atasan-langsung-kpi-leader`, **belum merge**). Sebelumnya field itu ada di dokumen dan di form tapi **tak pernah masuk struct `WorkData`, terisi 0 dari 179 karyawan, dan tak dipakai apa pun**. Menjawab pertanyaan yang tak bisa dijawab hierarki departemen: siapa bawahan seorang **Leader**. Departemen hanya mengenal satu supervisor, sehingga 11 Leader di 7 departemen tak punya cakupan apa pun.
	- ⚠️ **Dipakai untuk CAKUPAN TAMPILAN, BUKAN cakupan wewenang.** Alur persetujuan pengajuan **tidak berubah** dan tetap lewat `getSupervisorData` + `supervised_by`. Pemisahan ini disengaja dan diputuskan pemilik keputusan; menggabungkannya berarti menambah satu tahap persetujuan untuk 178 orang. Lihat tabel dua konsep di bawah.
	- Diisi lewat **HRIS → Personalia → Atasan Langsung** (alat isi-massal per departemen, `GET/PUT /supervisor-assignment`), atau per orang di form Edit Data Pekerjaan. Keduanya divalidasi sama: menolak atasan = diri sendiri, tak ditemukan, beda perusahaan, atau akunnya tak aktif.
	- **Tidak rekursif**, hanya satu tingkat ke bawah. Selama hierarki masih Supervisor → Leader → Staff, rekursi tak menambah apa pun.
- **Org chart** — visualisasi struktur (**belum ada**; diverifikasi ulang 2026-07-31, tak ada komponen bagan organisasi di `erp-frontend`). Datanya sudah cukup untuk membangunnya, **kecuali jenjang/golongan** yang memang belum ada di data mana pun (lihat TBD)

## Cakupan supervisi antar-departemen (`supervised_by`)

⚠️ **Baca sebelum mengubah data departemen atau supervisor.** Relasi ini menentukan ke siapa pengajuan cuti mengalir.

Sebagian departemen sengaja **tidak punya supervisor sendiri** dan dibawahi supervisor departemen lain. Saat ini: **General Affair dibawahi supervisor Human Resource** (`work_data.is_supervisor` = `true` nol orang di GA). Kedua departemen **tetap terpisah sebagai data** — 15 orang GA (mayoritas Security & Office Boy) tetap ber-`work_data.department` = `General Affair`.

Relasinya disimpan sebagai **master data**, bukan di kode: `master_department.supervised_by` berisi **key** departemen induk (GA → `hris`). Pasangannya `master_department.supervision_label` memberi nama pendek untuk kelompok gabungan (HR → `HRGA`).

### Dua konsep terpisah yang jangan dicampur

| | Cakupan TAMPILAN | Cakupan WEWENANG |
|---|---|---|
| Sumber | Struktur organisasi (`DepartmentGroups`) | Cakupan orang, di klaim JWT |
| Berlaku bagi | Siapa pun yang sudah berhak melihat | Hanya `is_supervisor` |
| Dipakai | KPI, daftar karyawan, laporan absensi | Support Ticket |
| Sifat | Mengelompokkan ulang baris yang sudah lolos RBAC; **tak pernah menambah baris** | Menambah akses |

Mencampur keduanya berbahaya dua arah: menyempitkan tampilan bikin staf HR melihat HR dan GA terpisah padahal timnya satu; melebarkan wewenang bikin staf HR ikut mendapat akses tiket GA yang bukan haknya.

### Urutan pencarian atasan

`/list?type=supervisor&department=X` menelusuri berurutan sampai ketemu:

1. `is_supervisor` di departemen X sendiri
2. `is_supervisor` di departemen induk X
3. Judul jabatan cocok `Supervisor|^Leader$` di X
4. Judul jabatan cocok di induk X

**Data eksplisit selalu menang atas tebakan judul jabatan**, di kedalaman mana pun. Kalau tidak, seseorang berjudul `GA Supervisor` (jabatan itu ada di seed default GA) tanpa flag `is_supervisor` akan membajak seluruh pengajuan GA dari supervisor HR yang sah.

**Departemen yang punya atasan sendiri selalu menang atas induknya.** Jadi memisahkan kembali cukup mengangkat supervisor di departemen itu; relasinya tak perlu dikosongkan lebih dulu, dan tak perlu ubah kode maupun deploy.

### Konsekuensi yang perlu dijaga

- **Jangan hapus `supervised_by` GA tanpa mengangkat supervisor GA lebih dulu.** Tak satu pun posisi di GA (`Security`, `Office Boy`, `GA Staff`, `Legal Staff`, `Admin`) cocok pola judul `Supervisor|^Leader$`, jadi hasilnya **nol approver** untuk 15 orang — dan gejalanya bukan error, melainkan pengajuan yang mentok diam-diam.
- **Relasi satu arah dan satu tingkat.** Induk membawa yang dibawahinya, bukan sebaliknya; cucu tidak ikut naik ke kakek.
- **Perubahan cakupan baru terasa setelah pemakai login ulang**, karena cakupannya ikut di token (berlaku 72 jam). Label kelompok dibaca per-permintaan, jadi perubahannya langsung terlihat.
- **Tahap review HR bersifat dept-level**: slot `hr_status` diisi pseudo-user tanpa `employee_id`, sehingga **semua** orang berdepartemen `Human Resource` dapat melihat & menindak antrian tahap HR, termasuk pengajuan milik orang GA. Tahap SPV tidak begitu (diisi `employee_id` spesifik). Ini alasan kuat untuk **tidak** menggabungkan kedua departemen di level data: bila GA dipindah ke HR, Security & Office Boy ikut bisa melihat antrian pengajuan seluruh perusahaan.
- **Dikelola dari `/hris/master-data`**, blok "Supervisi Antar-Departemen" pada form Departemen. `supervised_by` diisi **key** departemen induk (mis. `hris`), bukan nama tampilannya; `supervision_label` diisi di departemen **induk**, bukan anaknya.
	- Form **selalu mengirim** kedua field (boleh kosong), dan itu satu-satunya cara melepas relasi dari UI. `PUT /master/departments/:key` memakai `ReplaceOne` tapi **mempertahankan** kedua field bila tak disebut di body, sehingga pemanggil lain yang hanya mengirim sebagian field tak diam-diam memutus relasi.
	- Form memuat peringatan bahwa mengosongkan relasi tanpa mengangkat supervisor lebih dulu membuat anggotanya kehilangan penyetuju **tanpa pesan error**.

Tampilan KPI menyatukan keduanya sebagai satu entri tanpa menyentuh data — lihat [[HRIS - Key Performance Index]].

## Keterkaitan

- Sumber data master: `master_department` dan `master_system_role` di [[Microservices - Employee Service]] (seed otomatis saat kosong)
- Sumber data karyawan: `work_data` (departemen/posisi/supervisor) & `system_authentication` (role/supervisor) di [[Microservices - Employee Service]]
- Dipakai oleh hampir semua subsistem HRIS untuk routing approval & RBAC (lihat [[HRIS - Interrelationship Matrices]])
- Perubahan struktur ditangani via [[HRIS - Career & Promotion]] (mutasi/promosi)
- Frontend admin: `/hris/master-data` — tabs Departments + System Roles dengan full CRUD

## Belum Diputuskan (TBD)

- Format org chart (visual) + jenjang/golongan
- Penanganan posisi rangkap / matriks
- **Relasi supervisi berjenjang** — saat ini sengaja dibatasi SATU tingkat. Organisasi bertingkat (divisi → departemen → sub-departemen) perlu keputusan tersendiri
- **Satukan `deptKeyToNames`** (`shared-library/common/roles.go`) ke master data — pemetaan role key → nama departemen masih hardcode, dan `finance` → `Finance` + `Procurement` sebenarnya konsep yang sama dengan `supervised_by`. Departemen yang benar-benar baru masih butuh ubah kode di situ **dan** di switch jadwal absensi

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]]
- [[Microservices - Employee Service]] · [[HRIS - Personalia]] · [[HRIS - Career & Promotion]] · [[HRIS - Interrelationship Matrices]]
