## Deskripsi

*Struktur organisasi perusahaan — departemen, posisi/jabatan, jenjang, dan hierarki (atasan/SPV). **Departemen dan posisi** dikelola sebagai master data di MongoDB (`master_department`) dengan CRUD endpoint dan halaman admin di frontend. Data karyawan tetap di `work_data`. **Bagan organisasi sudah ada** (`/hris/org-chart`); **jenjang jabatan sudah ada** (2026-08-03) tapi belum diisi HR.*

- **Status**: ⚠️ Implemented (ada catatan) — master departemen/posisi sudah di-DB; org chart **sudah ada** (2026-08-01); **jenjang jabatan sudah ada & live di produksi** (2026-08-03) tapi **nol dari 79 jabatan** terisi

## Ruang Lingkup

- **Departemen** — dikelola di collection `master_department` (`key`, `name`, `positions[]`, `position_items[]`, `roles[]`, `company_id`, `supervised_by`, `supervision_label`); CRUD via `GET/POST/PUT/DELETE /master/departments` di [[Microservices - Employee Service]]
- **Posisi/jabatan** per departemen — tersimpan sebagai array `positions` di setiap dokumen `master_department`; sebelumnya hardcoded (`PositionTitle*` di shared-library), sekarang dapat ditambah/ubah via API atau frontend `/hris/master-data`
	- **`position_items[]` — jabatan sebagai entitas ber-identitas** ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]). Tiap item `{key, name, permission_sets[]}`: `key` slug stabil yang **tidak berubah walau namanya diganti**, sehingga paket hak yang menempel tak lepas saat jabatan di-rename; `permission_sets` = paket hak yang diwarisi setiap karyawan berjabatan itu, digabung dengan paket milik akun saat login (union, reach tertinggi). Sengaja **hidup berdampingan** dengan `positions[]` (array nama) yang tetap jadi sumber jawaban `/data-type/position`; `positions[]` dibuang nanti setelah semua pembaca pindah. `SyncPositionItems` menjaga keduanya selaras sambil mempertahankan key dan paket hak yang sudah ada.
	- Sisi karyawan: `work_data.position` (nama, untuk tampilan/laporan/template KPI) + `work_data.position_key` (kunci pencocokan paket hak). Kosong pada data lama sebelum migrasi → pemanggil jatuh ke pencocokan by nama.
- **Jenjang jabatan** — ✅ **live di produksi 2026-08-03** (BE [#952](https://github.com/bip-itteam-internal/bip-erp/pull/952) `60e77d53`, FE [#767](https://github.com/bip-itteam-internal/erp-frontend/pull/767) `aed8edbf`). Lima tingkat: **Pelaksana · Senior/Officer · Leader · Supervisor · Direktur**. Dikelola di tab **Jenjang Jabatan** pada `/hris/master-data`.
	- ⚠️ **Penanda ORGANISASI, BUKAN sumbu hak akses.** Hak tetap datang dari `permission_sets` ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]). Kalau jenjang ikut menentukan akses, ada dua sumber hak yang bisa menyimpang, dan menaikkan jenjang seseorang diam-diam memberinya wewenang yang tak pernah diputuskan siapa pun. Aturan ini **dikunci uji dari sumbernya**: `TestJenjangBukanSumbuHakAkses` membaca `permission_resolve.go` dan `permission_exceptions.go` dan menolak kemunculan `LevelKey`/`level_key`/`RankOf`/`JobLevel`. Dijaga begitu karena pelanggarannya akan tampak wajar saat ditulis (satu baris `if RankOf(...) >= ...` di resolver terasa praktis) dan **tak ada satu pun test fungsional yang akan gagal karenanya**. Pola sama dengan `internal_routes_guard_test.go`.
	- **Nama dan URUTAN sengaja dipisah.** Jabatan menyimpan `position_items[].level_key`; angka `rank` tinggal di koleksi baru `master_job_level` (`key`, `name`, `rank`, index unik `key`). Menyimpan angka langsung di jabatan akan memaksa penomoran ulang tiap ada tingkat baru di tengah, dan yang lebih berbahaya, membuat kode yang terlanjur menulis `rank >= 40` **berubah arti tanpa satu pun galat muncul**.
	- **Rank RENGGANG** (10, 20, 30, 40, 50). Menambah tingkat baru (mis. **Manager** di antara Supervisor dan Direktur) cukup satu entri ber-rank 45 di `DefaultJobLevels()` lalu deploy; **tak ada dokumen jabatan maupun karyawan yang perlu disentuh**. Jarak minimalnya dikunci uji lewat `MinJarakRank`, karena begitu menyempit jadi 1, janji itu batal. Baca urutannya lewat `RankOf(levels, key)`, **jangan pernah** membandingkan dengan angka yang diketik di kode; key kosong dan key tak dikenal sama-sama jatuh ke 0 sehingga jabatan tanpa jenjang tak pernah dinilai lebih tinggi dari tingkat mana pun.
	- **`seedJobLevels` menilai PER KEY**, bukan melewati koleksi yang tak kosong seperti `seedMasterDepartments`/`seedMasterSystemRoles`/`seedPermissionSets`. Pola skip-if-nonempty membuat tiap key baru menuntut fungsi `migrate*` tersendiri, karena dev dan prod koleksinya sudah terisi sejak hari pertama. Nama yang sudah diubah HR **tidak ditimpa** — kelas bug yang membuat `migratePermissionSetAssignment` dicabut. Bukti di log boot prod: tiga seeder lama menulis *"already has N entries, skipping"*, sementara jenjang menulis *"5 jenjang disisipkan"*.
	- **GLOBAL, tidak ter-scope `company_id`** seperti `master_department`. Tangga ini kebijakan grup; memisahkannya per perusahaan membuat gaji dan KPI antar perusahaan tak bisa dibandingkan. Bila suatu perusahaan benar-benar butuh tangga sendiri, itu keputusan tersendiri.
	- `SyncPositionItems` mempertahankan `level_key` saat form Master Data menyimpan ulang (dikunci uji sendiri). Tanpa itu, menambah satu jabatan mengosongkan jenjang **seluruh** departemen tanpa pesan apa pun — kelas bug yang pernah memutus jalur pengajuan cuti 15 orang General Affair.
	- ⚠️ **Belum menghasilkan apa pun sampai HR mengisi.** Verifikasi prod 2026-08-03: 5 jenjang ter-seed, **0 dari 79 jabatan** berjenjang. Posisi yang sama dengan `supervisor_id` sewaktu dihidupkan. Berkas Excel berisi usulan pemetaan 79 jabatan sedang menunggu koreksi HR.
	- **Belum ada CRUD jenjang lewat layar.** Menambah/mengubah tingkat = ubah `DefaultJobLevels()` + deploy. Cukup untuk sekarang karena tangganya lima baris dan jarang berubah; CRUD-nya TBD.
	- **Riwayat promosi tidak termasuk** — lihat [[HRIS - Career & Promotion]].
- **Departemen ter-scope per perusahaan** — `master_department.company_id` ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]). **`key` unik PER perusahaan, bukan global**; kosong pada data lama berarti BIP. Perusahaan baru mulai dengan daftar departemen kosong. Endpoint `/data-type/department`, `/data-type/position`, dan `/master/departments` menyaring memakai `EffectiveCompanyID`. ⚠️ Supervisi/RBAC (`allMasterDepartments`, `system-list`) sengaja **tetap global**, jadi jangan disamakan dengan penyaringan tampilan.
- **System roles** — role per department (staff, supervisor, admin, security) dan feature-based roles (insentive, integration) dikelola di `master_department.roles` dan `master_system_role`
- **Hierarki/atasan** — relasi supervisor per divisi (dipakai di banyak approval, mis. `getSupervisorData`)
	- **Atasan LANGSUNG per orang** (`work_data.supervisor_id`) — dihidupkan 2026-07-31, kini **✅ merged dan berjalan di produksi** (backend `GET/PUT /supervisor-assignment` di `services/employee/main.go:892` & `:950`; frontend `src/app/(main)/hris/employee/atasan-langsung/page.tsx`; prod `erp-frontend` di `c18adfec`, merge PR #664). Sebelumnya field itu ada di dokumen dan di form tapi **tak pernah masuk struct `WorkData`, terisi 0 dari 179 karyawan, dan tak dipakai apa pun**.
		- **Pengisiannya sudah berjalan.** Sensus produksi **2026-08-01**: `supervisor_id` terisi **54 dari 204** karyawan (Beauty Hacks 45, Tech Development 5, Human Resource 4). Sehari sebelumnya masih nol, jadi angka ini bergerak cepat begitu alatnya ada — jangan pakai angka lama untuk menyimpulkan fitur ini belum dipakai. Sisanya masih menunggu, dan setiap fitur yang bersandar padanya (cakupan KPI Leader, agregasi skor tim ber-scope `team`) baru menghasilkan sesuatu untuk departemen yang sudah diisi. Menjawab pertanyaan yang tak bisa dijawab hierarki departemen: siapa bawahan seorang **Leader**. Departemen hanya mengenal satu supervisor, sehingga 11 Leader di 7 departemen tak punya cakupan apa pun.
	- ⚠️ **Dipakai untuk CAKUPAN TAMPILAN, BUKAN cakupan wewenang.** Alur persetujuan pengajuan **tidak berubah** dan tetap lewat `getSupervisorData` + `supervised_by`. Pemisahan ini disengaja dan diputuskan pemilik keputusan; menggabungkannya berarti menambah satu tahap persetujuan untuk 178 orang. Lihat tabel dua konsep di bawah.
	- Diisi lewat **HRIS → Personalia → Atasan Langsung** (`GET/PUT /supervisor-assignment`), atau per orang di form Edit Data Pekerjaan. Keduanya divalidasi sama: menolak atasan = diri sendiri, tak ditemukan, beda perusahaan, atau akunnya tak aktif.
	- **Alurnya: pilih departemen → pilih atasan → centang bawahannya** (dibalik 2026-07-31 lewat PR #664, **sudah merged dan live di produksi**). Bentuk awalnya meminta atasan satu per satu untuk tiap karyawan, sehingga satu departemen berarti membuka dropdown belasan kali. Yang dibalik bukan cuma jumlah klik: pertanyaan yang ada di kepala orang adalah "anak buah Aris siapa saja", bukan "atasan si A siapa" diulang dua puluh kali.
	- ⚠️ **Satu karyawan hanya boleh punya SATU atasan**, jadi mencentang orang yang sudah jadi bawahan Leader lain **mencabutnya** dari Leader itu. Aksi sah, tapi tiap baris wajib menyebut akibatnya sebelum disimpan (`akan ditambahkan` · `akan dipindah dari X` · `akan dilepas`), dan berpindah atasan dengan perubahan menggantung meminta konfirmasi.
	- **Karyawan non-aktif disembunyikan**, jumlahnya disebut lewat satu baris keterangan. Semula mereka ditampilkan dengan penanda, dengan alasan jumlah baris harus cocok dengan daftar karyawan; alasan itu gugur begitu dipakai — di Tech Development produksi **5 dari 11 baris** adalah orang yang sudah resign, jadi hampir separuh layar terisi orang yang mustahil diberi atasan. Departemen yang **seluruh** isinya sudah resign diberi pesan berbeda dari departemen yang memang kosong, karena "belum ada karyawan" untuk departemen berisi lima orang yang semuanya sudah pergi adalah pesan yang menyesatkan.
	- **Label grup departemen dikenali.** `GET /supervisor-assignment` menerima `HRGA` maupun nama departemen satuan, memakai `ResolveDepartmentFilter` + `ExpandToDepartmentGroup` seperti `/kpi`. Tanpa itu Leader HRGA tak bisa menetapkan bawahan lintas Human Resource dan General Affair dalam satu layar, padahal keduanya satu tim (30 orang). Konsekuensi yang disengaja: **kedua departemen tak lagi bisa dipilih terpisah** di layar ini, dan karena `ExpandToDepartmentGroup` memekarkan anggota mana pun jadi satu tim penuh, meminta "Human Resource" saja pun kini mengembalikan seluruh HRGA. Sama seperti KPI, penggabungan adalah sifat organisasi, bukan sifat penontonnya.
	- **Tidak ada penjaga siklus.** A bisa jadi atasan B sekaligus bawahannya. Karena relasinya tidak rekursif hal itu tak merusak apa pun, keduanya sekadar saling melihat KPI; backend hanya menolak penetapan diri-sendiri.
	- **Tidak rekursif**, hanya satu tingkat ke bawah. Selama hierarki masih Supervisor → Leader → Staff, rekursi tak menambah apa pun.
- **Org chart** — ✅ dibangun 2026-08-01, **merged** (FE PR [#673](https://github.com/bip-itteam-internal/erp-frontend/pull/673); BE `services/employee/org_chart.go`). `GET /org-chart` mengirim seluruh karyawan **aktif** satu perusahaan beserta daftar departemennya dalam satu panggilan; halaman `/hris/org-chart` (menu **HRIS → Personalia → Bagan Organisasi**) menggambarnya.
	- **Kerangkanya DEPARTEMEN, bukan rantai atasan.** Sebagian besar karyawan belum punya `supervisor_id`, jadi bagan yang murni mengikuti rantai hanya akan menampilkan beberapa cabang berisi dan menyembunyikan sisanya. Dengan departemen sebagai kerangka, bagan utuh sejak hari pertama dan makin dalam seiring data diisi.
	- **Departemen se-kelompok supervisi dilebur jadi SATU simpul** (mis. Human Resource + General Affair → `HRGA`) — ✅ **merged 2026-08-02** (BE [#890](https://github.com/bip-itteam-internal/bip-erp/pull/890), FE [#710](https://github.com/bip-itteam-internal/erp-frontend/pull/710)); **prod belum deploy**, dan BE wajib naik lebih dulu karena FE tanpa `groups` kembali menggambar per departemen. Sejalan dengan KPI dan menu Atasan Langsung yang lebih dulu tak bisa memilih keduanya terpisah. Departemen asal tetap disebut sebagai keterangan di samping label, karena "HRGA" sendirian tak memberi tahu isinya apa. **Yang berubah cuma tampilan**: `work_data.department` orang GA tetap `General Affair`, sesuai alasan di §Cakupan supervisi antar-departemen.
		- Konsekuensi yang dituju: karena anggota kelompok masuk ember yang sama, **rantai atasan ikut tersambung lintas departemen**. Sebelumnya atasan hanya dicari di dalam satu departemen, jadi orang GA yang atasannya supervisor HR tetap menempel ke akar GA walau relasinya sudah diisi.
		- Aturan kelompok datang **jadi dari backend** (`groups` di respons `/org-chart`, dari `DepartmentGroups`), bukan dihitung ulang di frontend. Frontend tak pernah menyentuh `supervised_by`; ia hanya menerima label beserta anggotanya. Menyalin aturannya ke TypeScript berarti dua sumber kebenaran yang bisa menyimpang diam-diam, hal yang sudah ditandai sebagai langkah mundur di `features/hris/kpi/constants.ts`.
		- `groups` kosong (organisasi tanpa relasi supervisi, atau backend yang belum di-deploy) menghasilkan bagan persis seperti sebelumnya; itu dikunci uji, jadi FE aman naik lebih dulu meski urutan deploy tetap BE dulu.
	- Orang tanpa atasan **menempel ke departemennya** dan jumlahnya disebut di kepala halaman, jadi bagan sekaligus menunjukkan pekerjaan pengisian yang belum selesai. Karyawan **tanpa departemen** dikumpulkan ke kelompok berlabel, bukan dibuang — dikunci uji "jumlah seluruh simpul selalu sama dengan jumlah orang".
	- ⚠️ **Penjaga siklus WAJIB di sini walau tak ada di KPI.** KPI hanya melihat satu tingkat sehingga siklus tak berbahaya; bagan **menelusuri rantai**, jadi satu siklus akan berputar tanpa henti dan membekukan browser. Orang yang atasannya membentuk siklus tetap digambar, menempel ke departemen. Logikanya di `features/hris/org-chart/lib/bangun-pohon.ts`, terpisah dari render supaya bisa diuji tanpa React.
	- **Tanpa pustaka bagan.** HTML bersarang biasa; `recharts` yang sudah ada tak punya tata letak pohon. Departemen terbuka, isinya terlipat secara bawaan — 204 kartu sekaligus membuat bagan lebih sulit dibaca daripada daftar.
	- ⚠️ **Direktur muncul di dalam Kesekretariatan, bukan di puncak**, karena begitulah datanya (`work_data.department` = `Kesekretariatan`). Penentuan akar **tidak** ditebak dari nama jabatan. Menjadikan Direktur puncak organisasi adalah **keputusan data**, sekelas dengan jenjang jabatan; bagan ini justru membuat kejanggalan itu terlihat.
	- ⚠️ Direktur di dalam Kesekretariatan **tetap begitu walau jenjang sudah ada**: akar bagan ditentukan `work_data.department`, bukan `level_key`. Menjadikan jenjang penentu akar akan membuat bagan bercabang dari lima Supervisor sekaligus dan berbeda dari struktur pelaporan yang sebenarnya.

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

- ~~Format org chart (visual)~~ — **selesai 2026-08-01**, lihat §Ruang Lingkup
- ~~Jenjang/golongan~~ — **kodenya selesai 2026-08-03** dan live di produksi, lihat §Ruang Lingkup. Yang tersisa memang bagian yang sejak awal disebut bukan urusan kode: **siapa di tingkat mana untuk 79 jabatan**. Nol jabatan terisi; berkas usulan pemetaan menunggu koreksi HR
	- **Yang masih terbuka setelahnya**: apakah jenjang perlu bisa ditambah/diubah lewat layar (sekarang lewat `DefaultJobLevels()` + deploy), dan apakah ELT (Percetakan, 14 orang) memakai tangga yang sama atau tangganya sendiri. ELT sengaja **ditunda**; `position_key` 11 karyawannya menunjuk key milik BIP sehingga tak cocok dengan `position_items` departemennya sendiri
- Penanganan posisi rangkap / matriks
- **Relasi supervisi berjenjang** — saat ini sengaja dibatasi SATU tingkat. Organisasi bertingkat (divisi → departemen → sub-departemen) perlu keputusan tersendiri
- **Satukan `deptKeyToNames`** (`shared-library/common/roles.go`) ke master data — pemetaan role key → nama departemen masih hardcode, dan `finance` → `Finance` + `Procurement` sebenarnya konsep yang sama dengan `supervised_by`. Departemen yang benar-benar baru masih butuh ubah kode di situ **dan** di switch jadwal absensi

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]]
- [[Microservices - Employee Service]] · [[HRIS - Personalia]] · [[HRIS - Career & Promotion]] · [[HRIS - Interrelationship Matrices]]
