## Deskripsi

*Struktur organisasi perusahaan — departemen, posisi/jabatan, jenjang, dan hierarki (atasan/SPV). **Departemen dan posisi** dikelola sebagai master data di MongoDB (`master_department`) dengan CRUD endpoint dan halaman admin di frontend. Data karyawan tetap di `work_data`. **Bagan organisasi sudah ada** (`/hris/org-chart`); **jenjang jabatan sudah ada** (2026-08-03) tapi belum diisi HR.*

- **Status**: ⚠️ Implemented (ada catatan): master departemen/posisi sudah di-DB; **org chart live di produksi** (2026-08-01) berikut peleburan simpul se-kelompok supervisi (`HRGA`); **jenjang jabatan live di produksi** (2026-08-03), **56 dari 81 jabatan** terisi per 2026-08-12 dan **ditampilkan** di daftar karyawan serta bagan organisasi (FE PR [#1000](https://github.com/bip-itteam-internal/erp-frontend/pull/1000)); **penyetuju pengajuan per departemen live di produksi** (PR [#1184](https://github.com/bip-itteam-internal/bip-erp/pull/1184) & [#999](https://github.com/bip-itteam-internal/erp-frontend/pull/999)); resolusi atasan **disatukan jadi satu rantai** (PR [#1201](https://github.com/bip-itteam-internal/bip-erp/pull/1201)). Ketiganya **diverifikasi langsung di PRODUKSI 2026-08-26**, lihat §Bukti verifikasi produksi

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
	- **Pengisiannya sudah jauh berjalan, dan sejak 2026-08-12 hasilnya TERLIHAT.** Verifikasi prod 2026-08-12: **56 dari 81 jabatan** berjenjang, 5 di antaranya `leader`. Angka lama (0 dari 79 pada 2026-08-03) sudah usang — jangan dipakai menyimpulkan fitur ini belum dipakai, persis peringatan yang sama berlaku untuk `supervisor_id`.
	- **Ditampilkan sebagai kolom di daftar karyawan dan label di kartu bagan organisasi** (erp-frontend PR [#1000](https://github.com/bip-itteam-internal/erp-frontend/pull/1000)). Sebelum itu `level_key` tidak dibaca oleh apa pun di luar layar penyuntingnya sendiri, sehingga 56 isian tak menghasilkan akibat apa pun dan pengisinya menunggu sesuatu yang tak akan datang.
		- **Murni tampilan; ADR 0030 dan `TestJenjangBukanSumbuHakAkses` tidak tersentuh.** Yang berubah cuma jenjang jadi terlihat, bukan jadi berkuasa.
		- **Tanpa perubahan backend.** Pemetaan `(departemen, nama jabatan) → level_key → nama tingkat` dikerjakan frontend dari bahan yang sudah tersedia; daftar karyawan memang sudah mengirim departemen dan jabatan. Pencocokan memakai NAMA, bukan `position_key`, karena `position_key` tak ikut dikirim — konsekuensinya jabatan yang di-rename di master tanpa memperbarui data karyawan akan tampil tanpa jenjang, dan itu senyap.
		- Kegagalan memuat master departemen **tidak menjatuhkan halaman**: kolomnya kosong dan daftar karyawan tetap hidup. Daftar karyawan adalah layar kerja harian.
	- **Belum ada CRUD jenjang lewat layar.** Menambah/mengubah tingkat = ubah `DefaultJobLevels()` + deploy. Cukup untuk sekarang karena tangganya lima baris dan jarang berubah; CRUD-nya TBD.
	- **Riwayat promosi** kini punya modulnya sendiri (koleksi `employee_movement`), ⚠️ merged ke `main` 2026-08-10 (PR [#1142](https://github.com/bip-itteam-internal/bip-erp/pull/1142)) tapi belum diverifikasi lewat gateway dan belum punya frontend — lihat [[HRIS - Career & Promotion]] & [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]. Jenjang tetap **tidak** dipakai menyimpulkan promosi; jenisnya dipilih HR. Alasannya kini bukan lagi "belum ada datanya" (56 dari 81 jabatan sudah berjenjang per 2026-08-12) melainkan keputusan sadar: menyimpulkan promosi dari jenjang berarti menjadikan jenjang penentu, dan itu pintu belakang menuju hal yang [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] tutup.
- **Departemen ter-scope per perusahaan** — `master_department.company_id` ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]). **`key` unik PER perusahaan, bukan global**; kosong pada data lama berarti BIP. Perusahaan baru mulai dengan daftar departemen kosong. Endpoint `/data-type/department`, `/data-type/position`, dan `/master/departments` menyaring memakai `EffectiveCompanyID`. ⚠️ Supervisi/RBAC (`allMasterDepartments`, `system-list`) sengaja **tetap global**, jadi jangan disamakan dengan penyaringan tampilan.
	- **Isi nyata produksi 2026-08-19** — **13 dokumen**: 12 milik BIP (`hris`, `ga`, `it`, `secretary`, `finance`, `beauty_hacks`, `kyura`, `manufacture`, `quality`, `procurement`, `marketing`, `printing`) dan **1 milik ELT** (`pct` "Percetakan", 14 jabatan, kini **nol karyawan** setelah perpindahan). ⚠️ `marketing` ("Marketing Offline Distribution") **tidak ada di `DefaultDepartments()` maupun di `deptKeyToNames`** — bukti bahwa departemen bisa lahir murni sebagai master data, dan bahwa pemetaan role key memang tidak wajib.
	- **`printing` ("Printing") ditambahkan ke BIP 2026-08-19** sebagai tujuan perpindahan karyawan CV Elit ([[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]] aturan #7: departemen & jabatan tujuan wajib ada lebih dulu di perusahaan TUJUAN). 13 jabatan disalin dari `pct` milik ELT. ✅ **Live di DEV dan PRODUKSI, terverifikasi lewat gateway.** Perpindahan 14 karyawannya **sudah dijalankan** 2026-08-19 11:40 WIB; rincian dan urutannya di [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]].
		- Nama jabatan ditulis ulang **Title Case** (sumbernya di ELT ALL CAPS), dan itu aman justru karena `common.KanonPosisi` melumatkan kapitalisasi: `"Operator Mesin Laminasi"` dan `"OPERATOR MESIN LAMINASI"` sama-sama menghasilkan `operator_mesin_laminasi`, sehingga `work_data.position_key` karyawan tetap cocok setelah pindah tenant dan paket hak yang menempel di jabatan tidak lepas. Dikunci uji `TestPosisiPrintingBerkeySamaDenganELT`, yang membandingkan ke key **yang dibaca dari produksi**, bukan menghitung ulang dari namanya.
		- Duplikat ELT `"OPERATOR MESIN "` (berspasi di ujung, **nol pemakai**) sengaja **tidak** ikut. Di ELT ia melahirkan item kedua ber-key `operator_mesin_2` bernama tampilan sama persis — tak terbedakan di dropdown, dan satu-satunya item `pct` yang `level_key`-nya kosong.
		- ⚠️ **Printing tak punya jaring pengaman penyetuju sama sekali, dan itu TETAP berlaku walau penyetujunya kini sudah ditetapkan.** Dua dari tiga lapisan §Urutan pencarian atasan permanen kosong di sini: `supervised_by` kosong (Printing berdiri sendiri, sejajar Manufaktur), dan tebakan judul `Supervisor|^Leader$` tak cocok dengan jabatan mana pun di Printing — bukan dengan `"SPV Operasional"`, bukan pula dengan `"Admin"` yang kini memegangnya. Jadi **flag `is_supervisor` eksplisit adalah satu-satunya yang menahan jalur pengajuan 14 orang**; mencabutnya gagal senyap, tanpa lapisan cadangan yang menutupinya seperti di departemen lain.
			- Penyetuju terpasang **2026-08-19 11:41 WIB**: `ELT-0002-07-26` (Linda Sulastri, jabatan **Admin**), ditetapkan sengaja lewat layar Penyetuju Pengajuan, menggantikan `ELT-2015-07-26` (SPV Operasional) yang sempat terbawa dari ELT. `department_approver_log` mencatat pertukarannya berikut pelakunya — dan justru catatan itu yang membedakan "keputusan" dari "kelalaian" saat perubahannya terlihat mencurigakan dari luar.
			- Me-rename jabatannya jadi "Printing Supervisor" memang akan menyalakan tebakan judul itu, tapi **mematahkan** kecocokan `position_key` di atas. Jangan.
		- Printing **tidak menurunkan `system_roles` apa pun**: `peranJabatanTabel` (`services/employee/peran_dari_jabatan.go`) di-key per departemen dan tak punya entri `printing`. Itu keadaan yang benar, bukan kelalaian — "Operator Production" di Manufaktur pun sengaja absen dari tabel itu, bukti bahwa staf biasa tak butuh peran modul untuk presensi dan pengajuan. Konsekuensi yang perlu disadari: jabatan `Security` di Printing **tidak** mewarisi `ga: security` (buku tamu) seperti Security di General Affair, karena tabelnya ter-scope departemen.
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
	- **Departemen se-kelompok supervisi dilebur jadi SATU simpul** (mis. Human Resource + General Affair → `HRGA`) — ✅ **merged 2026-08-02** (BE [#890](https://github.com/bip-itteam-internal/bip-erp/pull/890), FE [#710](https://github.com/bip-itteam-internal/erp-frontend/pull/710)) dan ✅ **live di PRODUKSI**, diverifikasi 2026-08-26 (§Bukti verifikasi produksi). Catatan lama "prod belum deploy" sudah tidak berlaku. Urutan deploy-nya tetap **BE dulu**, karena FE yang menerima respons tanpa `groups` kembali menggambar per departemen. Sejalan dengan KPI dan menu Atasan Langsung yang lebih dulu tak bisa memilih keduanya terpisah. Departemen asal tetap disebut sebagai keterangan di samping label, karena "HRGA" sendirian tak memberi tahu isinya apa. **Yang berubah cuma tampilan**: `work_data.department` orang GA tetap `General Affair`, sesuai alasan di §Cakupan supervisi antar-departemen.
		- Konsekuensi yang dituju: karena anggota kelompok masuk ember yang sama, **rantai atasan ikut tersambung lintas departemen**. Sebelumnya atasan hanya dicari di dalam satu departemen, jadi orang GA yang atasannya supervisor HR tetap menempel ke akar GA walau relasinya sudah diisi.
		- Aturan kelompok datang **jadi dari backend** (`groups` di respons `/org-chart`, dari `DepartmentGroups`), bukan dihitung ulang di frontend. Frontend tak pernah menyentuh `supervised_by`; ia hanya menerima label beserta anggotanya. Menyalin aturannya ke TypeScript berarti dua sumber kebenaran yang bisa menyimpang diam-diam, hal yang sudah ditandai sebagai langkah mundur di `features/hris/kpi/constants.ts`.
		- `groups` kosong (organisasi tanpa relasi supervisi, atau backend yang belum di-deploy) menghasilkan bagan persis seperti sebelumnya; itu dikunci uji, jadi FE aman naik lebih dulu meski urutan deploy tetap BE dulu.
	- Orang tanpa atasan **menempel ke departemennya** dan jumlahnya disebut di kepala halaman, jadi bagan sekaligus menunjukkan pekerjaan pengisian yang belum selesai. Karyawan **tanpa departemen** dikumpulkan ke kelompok berlabel, bukan dibuang — dikunci uji "jumlah seluruh simpul selalu sama dengan jumlah orang".
	- ⚠️ **Penjaga siklus WAJIB di sini walau tak ada di KPI.** KPI hanya melihat satu tingkat sehingga siklus tak berbahaya; bagan **menelusuri rantai**, jadi satu siklus akan berputar tanpa henti dan membekukan browser. Orang yang atasannya membentuk siklus tetap digambar, menempel ke departemen. Logikanya di `features/hris/org-chart/lib/bangun-pohon.ts`, terpisah dari render supaya bisa diuji tanpa React.
	- **Tanpa pustaka bagan.** HTML bersarang biasa; `recharts` yang sudah ada tak punya tata letak pohon. Departemen terbuka, isinya terlipat secara bawaan — 204 kartu sekaligus membuat bagan lebih sulit dibaca daripada daftar.
	- ⚠️ **Direktur muncul di dalam Kesekretariatan, bukan di puncak**, karena begitulah datanya (`work_data.department` = `Kesekretariatan`). Penentuan akar **tidak** ditebak dari nama jabatan. Menjadikan Direktur puncak organisasi adalah **keputusan data**, sekelas dengan jenjang jabatan; bagan ini justru membuat kejanggalan itu terlihat.
	- ⚠️ Direktur di dalam Kesekretariatan **tetap begitu walau jenjang sudah ada**: akar bagan ditentukan `work_data.department`, bukan `level_key`. Menjadikan jenjang penentu akar akan membuat bagan bercabang dari lima Supervisor sekaligus dan berbeda dari struktur pelaporan yang sebenarnya.

## Penyetuju pengajuan per departemen (`work_data.is_supervisor`)

- ✅ **Merged 2026-08-12** (BE PR [#1184](https://github.com/bip-itteam-internal/bip-erp/pull/1184), FE PR [#999](https://github.com/bip-itteam-internal/erp-frontend/pull/999)) dan ✅ **live di PRODUKSI**, diverifikasi 2026-08-26 (§Bukti verifikasi produksi). Catatan lama "belum diverifikasi lewat gateway dan belum deploy" sudah tidak berlaku.
- Layar: **Pengaturan → Organisasi → Penyetuju Pengajuan** (`/pengaturan/organisasi?tab=penyetuju`). Endpoint: `GET /master/departments/approvers` & `PUT /master/departments/:key/approver` ([[API - Employee Service]]).

### Kenapa ada

`work_data.is_supervisor` menentukan ke siapa cuti, izin, koreksi absensi, dan dinas satu departemen mengalir, tetapi sampai 2026-08-12 **tak ada layar mana pun yang menentukannya**. Frontend menurunkannya dari NAMA JABATAN (`position.includes("Supervisor") || position === "Leader"`) setiap kali Data Pekerjaan disimpan.

Akibatnya: **menyunting data siapa pun berjabatan persis `"Leader"` mengalihkan seluruh persetujuan departemennya**, tanpa centang dan tanpa pesan. Terjadi di **Beauty Hacks 2026-08-12**: pengajuan 48 orang berpindah dari Aris Romadhoni (`BIP-0224-01-26`, "BeautyHacks Supervisor") ke Ade Jaenul Farhi (`BIP-0055-02-24`, "Leader") yang `system_roles`-nya kosong. Dua koreksi absensi menggantung sampai keluhan masuk lewat MyBharata, bukan lewat satu pun test.

Ini juga menjelaskan kalimat "data eksplisit selalu menang atas tebakan judul jabatan" di bawah: data eksplisit itu **sendiri** diisi dari tebakan judul jabatan.

### Aturan yang berlaku sekarang

- **Satu departemen satu penyetuju.** Pemanggil memakai `supervisors[0]`, jadi penyetuju kedua tak menambah siapa pun yang bisa menyetujui — ia hanya membuat pilihannya ambigu dan membuat salah satunya melihat antrian review kosong tanpa tahu sebabnya. Penetapan adalah **pertukaran** dalam satu transaksi, bukan penambahan.
- **`is_supervisor` tak lagi bisa ditulis lewat form data pekerjaan.** Dibuang di **ketiga** pintu tulis `work_data` lewat `fieldPenyetuju` (`services/employee/partial_update.go`), bersama `fieldKontrak`: `buildUpdateSet`, `POST /create/:id/work`, dan `workDataSetTanpaFieldTerkunci` (jalur `PUT /api/hris/employees/multi/:id` yang menerima struct). Pintu ketiga paling berbahaya karena `IsSupervisor` bertag bson **tanpa `omitempty`**, sehingga pemanggil yang tak menyentuhnya tetap menulis `false` lewat zero value Go. Dibuang **senyap, bukan 400**, mengikuti alasan `fieldKontrak`: backend naik lebih dulu daripada frontend.
- **Penyetuju wajib anggota departemen yang disetujuinya.** Lookup menyaring `{is_supervisor, department}` sekaligus, jadi orang dari departemen lain tak akan pernah ditemukan dan departemennya berakhir tanpa penyetuju secara senyap.
- ⚠️ **`:key` adalah satu key departemen, BUKAN label grup.** Endpoint ini sengaja **tidak** memakai `ResolveDepartmentFilter`/`ExpandToDepartmentGroup` seperti `/supervisor-assignment` dan `/kpi`: memekarkan `HRGA` akan mematikan penyetuju Human Resource sekaligus, sementara General Affair justru harus tetap kosong agar alirannya ke HR tak putus. Dikunci uji pembaca berkas.
- **Departemen tanpa penyetuju sendiri bukan kekurangan.** Layar membedakan "mengikuti *induk*" dari "belum ditetapkan", dan yang pertama **tidak** dihitung sebagai perlu perhatian — menyamakannya akan mengundang orang mengangkat supervisor GA dan memutus jalur pengajuan 21 orang.
- **Perpindahan hanya berlaku untuk pengajuan BARU.** Penyetuju disnapshot saat pengajuan dibuat, jadi yang sedang berjalan tetap di orang lama; itulah yang membuat dua koreksi Hanif Fauzan menggantung saat insiden. Dialog konfirmasi menyebutkannya.
- **Jejak audit** di koleksi `department_approver_log` (`company_id`, `department_key`, `department_name`, `from_employee_id`, `to_employee_id`, `actor`, `at`), ditulis **di dalam transaksi** yang sama. Insiden 2026-08-12 hanya bisa dilacak karena `metadata.updated_at` kebetulan belum tertimpa.

### Beda dari Atasan Langsung

| | **Atasan Langsung** (`supervisor_id`) | **Penyetuju Pengajuan** (`is_supervisor`) |
|---|---|---|
| Mengatur | Cakupan TAMPILAN (siapa melihat KPI siapa) | WEWENANG menyetujui pengajuan |
| Layar | HRIS → Personalia → Atasan Langsung | Pengaturan → Organisasi → Penyetuju Pengajuan |
| Cakupan | Per orang, banyak bawahan | Per departemen, satu penyetuju |
| Label grup | Dimekarkan (HRGA jadi satu tim) | **Tidak** dimekarkan |

Halaman Atasan Langsung berkali-kali disangka juga menetapkan penyetuju, jadi kini ia memuat keterangan **read-only** yang menunjuk ke tab penyetuju. Sengaja hanya memberi tahu, tidak menulis: menyatukan kedua kendali di satu layar akan melebur dua konsep yang tabel di §Cakupan supervisi sengaja pisahkan.

### Menemukan layar yang benar (erp-frontend PR [#1000](https://github.com/bip-itteam-internal/erp-frontend/pull/1000))

Keterangan satu arah di atas ternyata belum cukup: ia menolong orang yang sudah terlanjur membuka halaman yang salah, bukan yang sedang mencari. Karena itu:

- **Tautannya kini dua arah** — tab Penyetuju Pengajuan menunjuk balik ke Atasan Langsung.
- **Halaman Pengaturan → Organisasi & Jabatan memuat "peta niat"** di atas tab bar, memetakan "saya mau apa" ke tempatnya. Peta itu **sengaja menyebut tujuan yang BUKAN di halaman itu** (Atasan Langsung, Bagan Organisasi), karena justru itu yang dicari orang lalu tak ditemukan. Baris tabnya **diturunkan dari `SUB_MENU_PENGATURAN`**, bukan diketik ulang, supaya tab baru otomatis muncul dan petanya tak bisa jadi basi.

⚠️ **Tidak ada rute yang dipindah, dan itu keputusan sadar.** Dua usulan yang lebih besar ditimbang lalu dibatalkan, dicatat di sini supaya tidak diusulkan lagi:

- **Memindahkan Atasan Langsung ke Pengaturan** melanggar pemisahan `HRIS → Personalia` (data per-orang) versus `Pengaturan` (setelan master), dan memutus pasangannya dengan Bagan Organisasi yang sengaja bertetangga karena keduanya membaca data yang sama — yang satu mengisinya, yang satu menampilkannya.
- **Menyatukan kedua layar** mengabaikan bahwa gerbangnya berbeda: `/supervisor-assignment` digerbang `RequireHRISOrITStaff`, sedangkan `/master/departments/:key/approver` digerbang `RequireHRISOrITSupervisor`. Menyatukannya membuat staf HRIS melihat kendali yang tak boleh mereka pakai.

Efek sampingnya menguntungkan: `PETA_URL_MENU_LAMA` dan setelan `menu_hidden` yang menyimpan URL tak perlu disentuh sama sekali.

## Cakupan supervisi antar-departemen (`supervised_by`)

⚠️ **Baca sebelum mengubah data departemen atau supervisor.** Relasi ini menentukan ke siapa pengajuan cuti mengalir.

Sebagian departemen sengaja **tidak punya supervisor sendiri** dan dibawahi supervisor departemen lain. Saat ini: **General Affair dibawahi supervisor Human Resource** (`work_data.is_supervisor` = `true` nol orang di GA). Kedua departemen **tetap terpisah sebagai data** — 15 orang GA (mayoritas Security & Office Boy) tetap ber-`work_data.department` = `General Affair`.

> **Peleburan HR + GA jadi HRGA sudah jadi keputusan organisasi (2026-08-09), tapi yang dilebur baru lapisan tampilan dan wewenang, BUKAN data.** Keputusan itu sejauh ini hanya tercatat sebagai komentar di `services/employee/peran_dari_jabatan.go` ("General Affair — kini bergabung dengan HR menjadi HRGA"), dan konsekuensi konkretnya di sana: puncak GA kini **Leader**, bukan "GA Supervisor", sebab setelah penggabungan tak ada lagi supervisor di sisi GA.
>
> Yang sudah menyatu tanpa satu pun nilai `department` diubah: kelompok supervisi (`supervised_by` + `supervision_label`), cakupan supervisor di klaim JWT, tampilan KPI, org chart, layar Tampilan Menu (`MODUL_HRGA`), dan **satu blok sidebar** (branch `feat/sidebar-blok-hrga`, ⚠️ belum merge — `gabungBlokHrga` menyatukan blok `hris` dan `ga` SETELAH penyaringan izin, bukan dengan memindahkan menu GA ke kategori `hris`, sebab pemegang role `ga` saja tak pernah melihat kategori `hris`).
>
> Yang belum, dan syaratnya ada di bawah: mengganti nilai `work_data.department` jadi `HRGA`.

Relasinya disimpan sebagai **master data**, bukan di kode: `master_department.supervised_by` berisi **key** departemen induk (GA → `hris`). Pasangannya `master_department.supervision_label` memberi nama pendek untuk kelompok gabungan (HR → `HRGA`).

### Dua konsep terpisah yang jangan dicampur

| | Cakupan TAMPILAN | Cakupan WEWENANG |
|---|---|---|
| Sumber | Struktur organisasi (`DepartmentGroups`) | Cakupan orang, di klaim JWT |
| Berlaku bagi | Siapa pun yang sudah berhak melihat | Hanya `is_supervisor` |
| Dipakai | KPI, daftar karyawan, laporan absensi | Support Ticket |
| Sifat | Mengelompokkan ulang baris yang sudah lolos RBAC; **tak pernah menambah baris** | Menambah akses |

Mencampur keduanya berbahaya dua arah: menyempitkan tampilan bikin staf HR melihat HR dan GA terpisah padahal timnya satu; melebarkan wewenang bikin staf HR ikut mendapat akses tiket GA yang bukan haknya.

### Kontrak penerjemah filter departemen

⚠️ **Tiga fungsi bernama mirip di `shared-library/models/employee/department_scope.go` menjawab pertanyaan BERBEDA, dan memakai yang keliru tak pernah melempar galat.** Ia mengembalikan slice yang sah berisi nama yang tak dimiliki siapa pun, sehingga endpoint membalas **200 tanpa satu pun baris** dan layar berbunyi "belum ada datanya" alih-alih "filternya tak menemukan siapa-siapa".

| Fungsi | Menerima | Menjawab |
|---|---|---|
| `ResolveDepartmentFilter` | nilai dari LAYAR: nama, label grup, CSV, atau campurannya | "nilai yang dipilih orang ini maksudnya departemen apa saja" |
| `ExpandToDepartmentGroup` | nama departemen saja | "menyebut satu anggota berarti menyebut siapa saja" |
| `SupervisedDepartments` | nama departemen saja | "apa cakupan supervisi ORANG ini" |

**Nilai yang datang dari layar wajib memakai komposisi `ExpandToDepartmentGroup(ResolveDepartmentFilter(master, q))`**, persis seperti `GET /kpi`. Di employee-service komposisi itu tinggal di satu tempat, `cakupanDepartemenKPI` (`services/employee/kpi_departemen_query.go`), dengan penjaga pemindai sumber berdaftar-izin: pemanggil baru yang menembak `SupervisedDepartments` atas nilai query membuat testnya merah. Pemanggilan yang memakai `work_data.department` milik seseorang tetap aman dan sengaja diizinkan, sebab label grup tak pernah tersimpan di sana.

`ResolveDepartmentFilter` menerima **empat** bentuk, dan bentuk keempat yang paling lama tak terlihat:

1. nama departemen biasa → satu nama, apa adanya
2. label grup (`HRGA`) → seluruh anggotanya
3. beberapa nama dipisah koma → nama-nama itu
4. **campuran nama dan label dalam satu CSV** → tiap potongan diterjemahkan sendiri-sendiri

⛔ **Bentuk keempat sempat patah, dan kerusakannya menyebar lebih luas dari yang terlihat.** Selama perbandingan labelnya dilakukan terhadap **seluruh** nilai, label hanya dikenali bila berdiri sendiri; label yang sama di antara nama lain diteruskan mentah. Yang membuatnya bergejala: `DepartmentFilterOptions` sengaja **mengganti** anggota grup dengan satu entri berlabel, jadi dropdown bergrup yang seluruh opsinya digabung koma mengirim satu label untuk **setiap** grup. Tab "Per Karyawan" halaman KPI melakukan persis itu, dan yang hilang bukan satu departemen melainkan seluruh departemen yang punya grup. Pemekarannya kini dikerjakan **per potongan**, dengan dedup case-insensitive supaya label yang datang bersama anggotanya tak menggandakan isi `$in`.

Dua hal yang menyertainya:

- **`ResolveDepartmentFilter` sengaja TIDAK memekarkan anggota→grup.** Menyebut `Human Resource` tetap menghasilkan satu nama; itu tugas `ExpandToDepartmentGroup`. Pemisahannya dipakai: `filterDepartemenTemplateKPI` memanggilnya **sendirian** justru supaya filter satu departemen tak diam-diam membawa template departemen saudaranya, sebab frontend memanggil endpoint itu per departemen lalu menggabungkan sendiri.
- ⚠️ **Koma adalah pemisah, jadi `name` maupun `supervision_label` tak boleh mengandung koma.** Hari ini tak ada yang begitu (label tanpa `supervision_label` berbentuk `A + B`), dan bila suatu saat ada, potongannya pecah salah dan departemen itu hilang tanpa pesan.
- **RBAC menilai string query MENTAH**, lewat `ParseDepartmentList` yang cuma memecah koma tanpa pemekaran grup. Jadi memekarkan label di lapisan filter tidak melebarkan hak akses siapa pun: `hasDepartmentAccess` mencocokkan `deptKeyToNames`, dan `HRGA` tak pernah cocok dengan key mana pun.

Riwayat kelas ini: [#1444](https://github.com/bip-itteam-internal/bip-erp/pull/1444) (`/kpi/auto-scores`, kolom "Terhitung otomatis" berbunyi 0/20), [#1454](https://github.com/bip-itteam-internal/bip-erp/pull/1454) (`/kpi/template-assignment` tampil kosong), lalu bentuk CSV di atas. Perbaikan pertama tak ikut menyentuh yang kedua — bukti langsung bahwa aturannya tak boleh punya dua salinan.

### Urutan pencarian atasan

Rantainya menelusuri berurutan sampai ketemu:

1. `is_supervisor` di departemen X sendiri
2. `is_supervisor` di departemen induk X (`master_department.supervised_by`)
3. Judul jabatan cocok `Supervisor|^Leader$` di X
4. Judul jabatan cocok di induk X

**Data eksplisit selalu menang atas tebakan judul jabatan**, di kedalaman mana pun. Kalau tidak, seseorang berjudul `GA Supervisor` (jabatan itu ada di seed default GA) tanpa flag `is_supervisor` akan membajak seluruh pengajuan GA dari supervisor HR yang sah.

#### Satu rantai, dipakai bersama semua pemanggil (PR [#1201](https://github.com/bip-itteam-internal/bip-erp/pull/1201))

⚠️ **`atasanDepartemen` (`services/employee/supervisor_lookup.go`) adalah SATU-SATUNYA resolusi "siapa atasan departemen ini".** Jangan menyalin sebagiannya ke pemanggil baru, dan jangan menghitung ulang dari `is_supervisor` di service lain.

Alasannya sudah terbukti: sampai 2026-08-13 langkah pertama berdiri sendiri di pemanggil sementara langkah 2 sampai 4 tinggal di `supervisorFallbackSteps`. Pemanggil baru (lookup penyetuju **laporan** milik form-builder) menyalin langkah pertama saja lalu mengira sudah menjawab pertanyaan yang sama. Untuk setiap departemen yang kosongnya **disengaja** supaya mengalir ke induk, terutama **General Affair (15 orang)**, salinan itu membalas string kosong. Akibatnya keputusan dan antrean laporan dibalas **403 untuk SEMUA orang, termasuk penyetuju yang sah**, dan notifikasinya diam. Tak satu pun pesan menyebut sebabnya. Kini langkah pertama ikut disusun `langkahAtasan`, jadi rantainya mustahil disalin setengah.

Dua pemanggilnya sekarang:

| Pemanggil | Rute | Untuk |
|---|---|---|
| attendance-service | `GET /list?type=supervisor&department=X` | penyetuju cuti, izin, koreksi absensi, perjalanan dinas |
| form-builder | `GET /internal/department-approver?department=&company_id=` | penyetuju **laporan** ([[Microservices - Form Builder Service]]) |

Keduanya memakai orang **PERTAMA** (`supervisors[0]` dan `kandidat[0]`), dan pipeline sudah menyortir `employee_id` menaik. **Jangan menyaring atau menyortir ulang di pemanggil**: begitu dua pemanggil memilih orang berbeda dari daftar yang sama, cuti seseorang mengalir ke A sementara laporannya menunggu B.

⚠️ **`penyetujuSekarang` (`department_approver.go`) sengaja TIDAK ikut memakai rantai penuh.** Ia menjawab pertanyaan yang berbeda, yaitu "siapa yang tercatat **eksplisit** sebagai penyetuju departemen ini", untuk layar admin dan jejak audit pertukarannya. Rantai penuh justru salah di sana: ia akan melaporkan supervisor HR sebagai "penyetuju General Affair" lalu mematikannya saat pertukaran, memutus jalur pengajuan yang sedang berjalan.

#### Satu percobaan yang menggalat menghentikan SELURUH rantai

Galat pada satu lapisan dikembalikan apa adanya, **bukan** di-log lalu dilanjutkan ke lapisan berikutnya. **Jangan mengubahnya jadi "log lalu lanjut", sebab percobaan yang gagal bukan bukti percobaan itu kosong.**

Kerusakannya konkret dan senyap: departemen yang **punya** `is_supervisor` sendiri mengalami galat sesaat di lapisan 1 (cursor timeout, blip failover), lalu lapisan 3 (tebakan judul di departemen yang sama) berhasil dan mengembalikan orang yang `is_supervisor`-nya justru `false`. Pengajuannya dibalas 200, dan `spv_review.employee_id` dipaku ke orang itu **selamanya** di dokumen pengajuan. Itu bentuk persis insiden pembajakan penyetuju 2026-08-12.

Yang **tidak** berubah: hasil **kosong tanpa galat** tetap jatuh ke lapisan berikutnya. Itu jawaban yang sah dan pasti ("departemen ini tak punya siapa-siapa yang cocok"), berbeda dari galat yang berarti "tak tahu".

Konsekuensi bagi pemanggil: lookup penyetuju laporan **gagal-tertutup** (500, bukan `200 {"employee_id":""}`), sementara attendance-service memetakan setiap balasan non-200 ke slice kosong sehingga tak ada layar yang berubah.

**Departemen yang punya atasan sendiri selalu menang atas induknya.** Jadi memisahkan kembali cukup mengangkat supervisor di departemen itu; relasinya tak perlu dikosongkan lebih dulu, dan tak perlu ubah kode maupun deploy.

⚠️ **Pemanggil memakai `supervisors[0]` — SATU orang, yang pertama.** Sejak PR [#1184](https://github.com/bip-itteam-internal/bip-erp/pull/1184) kedua pipeline (jalur utama dan jalur cadangan) memakai `$sort {employee_id: 1}` eksplisit, dan hasil lebih dari satu dicatat ke log beserta siapa yang menang. Sebelumnya urutannya adalah urutan index yang kebetulan tersedia: produksi hanya punya `{company_id, employee_id}`, sehingga employee_id terkecil menang tanpa pernah diputuskan siapa pun. Hasil akhirnya sama, bedanya kini itu keputusan yang tertulis. Jalur **cadangan** yang paling mungkin mengembalikan beberapa orang, karena ia menebak dari judul jabatan yang tak mengenal siapa yang sah.

### Konsekuensi yang perlu dijaga

- **Jangan hapus `supervised_by` GA tanpa mengangkat supervisor GA lebih dulu.** Tak satu pun posisi di GA (`Security`, `Office Boy`, `GA Staff`, `Legal Staff`, `Admin`) cocok pola judul `Supervisor|^Leader$`, jadi hasilnya **nol approver** untuk 15 orang — dan gejalanya bukan error, melainkan pengajuan yang mentok diam-diam.
- **Relasi satu arah dan satu tingkat.** Induk membawa yang dibawahinya, bukan sebaliknya; cucu tidak ikut naik ke kakek.
- **Perubahan cakupan baru terasa setelah pemakai login ulang**, karena cakupannya ikut di token (berlaku 72 jam). Label kelompok dibaca per-permintaan, jadi perubahannya langsung terlihat.
- **Tahap review HR bersifat dept-level**: slot `hr_status` diisi pseudo-user tanpa `employee_id`, sehingga **semua** orang berdepartemen `Human Resource` dapat melihat & menindak antrian tahap HR, termasuk pengajuan milik orang GA. Tahap SPV tidak begitu (diisi `employee_id` spesifik). Ini alasan kuat untuk **tidak** menggabungkan kedua departemen di level data: bila GA dipindah ke HR, Security & Office Boy ikut bisa melihat antrian pengajuan seluruh perusahaan.

	> **Keberatan itu bukan tembok permanen, melainkan URUTAN KERJA.** Izin `hris.pengajuan.view` dan `hris.pengajuan.approve` beserta paketnya ("HRIS: Pemantau Pengajuan" / "HRIS: Penyetuju Pengajuan") **sudah merged** dan justru dibuat berlingkup pengajuan supaya himpunan pemakainya lebih sempit daripada pemegang role hris. Begitu keduanya berlaku eksklusif, yang menentukan siapa melihat antrean adalah **paket yang menempel di jabatan**, bukan nama departemen — dan Security yang tak dipasangi paket tak melihat apa pun meski departemennya sudah bernama HRGA.
	>
	> Hari ini belum eksklusif: gerbangnya masih **union** (`bolehPengajuan` di `services/attendance/hris_gate.go`), jadi `gerbangLamaBacaPengajuan = isHRDept || isCostControl` tetap meloloskan siapa pun berdepartemen HR. Tiga prasyarat sebelum sakelarnya boleh disentuh:
	>
	> 1. **Pasang paketnya lebih dulu** — pengukuran ke data dev 2026-08-09 menemukan NOL posisi memegang paket `hris_*` mana pun, jadi fase dua hari ini menolak semua orang alih-alih menyaring.
	> 2. **Sakelarnya belum bisa dipakai untuk pengajuan saja** — union diikat ke `HRIS_TIER_FALLBACK` yang berlaku untuk SELURUH modul hris, jadi mematikannya ikut mencabut Kontrak, Resign, Kuota Cuti, dan Laporan Kehadiran. Pilihannya: siapkan seluruh modul hris sekaligus, atau pecah sakelarnya.
	> 3. **Tahap HRD tak selalu duduk di `hr_status`** — koreksi milik staf HR dan tukar jadwal milik atasan menaruh peninjau HR di slot `spv_status`.
	>
	> Rinciannya di [[CORE - RBAC dan Permission Set]] §Irisan ketiga. Urutan yang benar: pasang paket → siapkan sakelar → nyalakan fase dua → verifikasi antrean menyusut ke yang berhak → **baru** lebur departemennya.
- **Dikelola dari `/hris/master-data`**, blok "Supervisi Antar-Departemen" pada form Departemen. `supervised_by` diisi **key** departemen induk (mis. `hris`), bukan nama tampilannya; `supervision_label` diisi di departemen **induk**, bukan anaknya.
	- Form **selalu mengirim** kedua field (boleh kosong), dan itu satu-satunya cara melepas relasi dari UI. `PUT /master/departments/:key` memakai `ReplaceOne` tapi **mempertahankan** kedua field bila tak disebut di body, sehingga pemanggil lain yang hanya mengirim sebagian field tak diam-diam memutus relasi.
	- Form memuat peringatan bahwa mengosongkan relasi tanpa mengangkat supervisor lebih dulu membuat anggotanya kehilangan penyetuju **tanpa pesan error**.

Tampilan KPI menyatukan keduanya sebagai satu entri tanpa menyentuh data — lihat [[HRIS - Key Performance Index]].

## Bukti verifikasi produksi (2026-08-26)

Tiga catatan "prod belum" di dokumen ini sudah tidak berlaku. Yang membuktikannya bukan `docker ps` maupun `git log` di server, melainkan **artefak yang benar-benar berjalan**: repo di server bisa sudah benar sementara containernya belum di-rebuild.

**Backend** (`Employee-Service`, image dibangun 2026-08-26 11:11 WIB). Grep biner `/service`:

| String | Hit | Membuktikan |
|---|---|---|
| `department_approver_log` | 1 | jejak audit pertukaran penyetuju (PR #1184) |
| `/departments/:key/approver` | 2 | rute penetapan penyetuju |
| `/internal/department-approver` | 1 | lookup penyetuju laporan (PR #1201) |
| `atasanDepartemen` · `penyetujuUntukLookup` | 3 · 1 | rantai atasan yang disatukan |
| `DepartmentGroups` · `SupervisorLookupOrder` | 1 · 1 | peleburan simpul `HRGA` di org chart (PR #890) |
| `master_job_level` | 5 | jenjang jabatan |
| *(kontrol negatif, string karangan)* | **0** | grep-nya memang membedakan |

**Frontend** (`frontend-hris-dashboard`, image dibangun 2026-08-26 14:47 WIB). Rute `(main)/pengaturan/organisasi`, `(main)/hris/org-chart`, dan `(main)/hris/employee/atasan-langsung` ketiganya ada di `/app/.next/server/app`; string locale `"Assign one approver per department"`, `"Decide who approves a department"`, dan `"Position Levels"` ada di bundel JS (masing-masing 2 berkas), kontrol negatif **0**.

⚠️ **Umur IMAGE yang dibaca, bukan umur container.** Container bisa muda karena restart biasa; hanya image baru yang membuktikan rebuild. Resep lengkapnya di [[RUN - Deploy Microservices bip-erp]].

⚠️ Probe ini membuktikan **kodenya terpasang**, bukan bahwa alurnya sudah dijalani orang. Untuk penyetuju pengajuan, bukti pemakaian yang sesungguhnya adalah isi `department_approver_log`. Belum dihitung.

## Keterkaitan

- Sumber data master: `master_department` dan `master_system_role` di [[Microservices - Employee Service]] (seed otomatis saat kosong)
- Sumber data karyawan: `work_data` (departemen/posisi/supervisor) & `system_authentication` (role/supervisor) di [[Microservices - Employee Service]]
- **Siapa yang memakainya: §Peta konsumen di bawah.** Kalimat lama "dipakai hampir semua subsistem HRIS" sudah dicabut, karena keliru di **dua arah sekaligus**: konsumen terbesar ketiga adalah **procurement**, yang bukan HRIS, sementara lima service justru tak memakainya sama sekali. [[HRIS - Interrelationship Matrices]] juga bukan jawabannya; ia memetakan aliran data antar-subsistem HRIS, bukan konsumen struktur organisasi, dan statusnya masih 🟡 Draft.
- Perubahan struktur ditangani via [[HRIS - Career & Promotion]] (mutasi/promosi)
- Frontend admin: `/hris/master-data` — tabs Departments + System Roles dengan full CRUD

### Peta konsumen

> Diukur langsung ke `origin/main`: bip-erp `84faee96` dan erp-frontend `17cb901f`, keduanya 2026-08-26.

Ada **dua cara** memakainya, dan membedakannya penting karena skalanya jauh berbeda.

**Cara pertama, lewat header gateway.** `shared-library/routes/gateway_request.go` menyuntikkan `BIP-Department`, `BIP-Position`, `BIP-Supervised-Departments`, dan `BIP-System-Roles` ke **setiap** permintaan yang diteruskan. Jadi service tak perlu query `master_department` untuk tahu departemen pemanggilnya, dan pemakaian semacam ini tak terlihat sebagai dependensi di mana pun.

**Cara kedua, membaca datanya.** 16 dari 21 service:

| Service | Yang dirujuk | Untuk |
|---|---|---|
| [[Microservices - Attendance Service]] | `Header.Department` 24 · `Header.Position` 17 · `SupervisedDepartments` 6 | **konsumen terbesar**: routing approval, picker jadwal, laporan |
| [[Microservices - Employee Service]] | `is_supervisor` 36 · `supervisor_id` 32 · `position_key` 21 · `supervised_by` 16 | pemilik datanya |
| procurement | `Header.Department` 8 · `is_supervisor` 5 · `SupervisedDepartments` 4+2 | approval pengadaan & budget |
| [[Microservices - Form Builder Service]] | `SupervisedDepartments` 8 · `Header.Department` 7 · `supervised_by` 2 | kepemilikan form per dept, penyetuju laporan |
| [[Microservices - Insentive Service]] | `position_key` 6 · `supervisor_id` 2 · `is_supervisor` 1 | menyusun hierarki tim marketing (`hierarki_hris.go`) |
| [[Microservices - Task Management Service]] | `is_supervisor` 4 · `supervised_by` 2 | peran supervisor/staff di space tiket |
| [[Microservices - Recruitment Service]] | `SupervisedDepartments` 4 · `is_supervisor` 1 | requisition & MPP per departemen |
| manufacture | `Header.Position` 6 | gerbang per jabatan |
| [[Microservices - Calendar Service]] | Department · Position · **SupervisedDepartments** | penyaringan feed agenda |
| [[Microservices - Learning Service]] · notification · payroll · [[Microservices - HRD Document Service]] · integration | Department dan/atau Position (1 sampai 2) | gerbang & pelabelan |
| inventory · marketing-analytics | `SupervisedDepartments` 1 · `supervisor_id` 1 | cakupan data |

**Lima service TIDAK memakainya sama sekali**: `file`, `finance`, `monitoring`, `tiktok-shop-service`, `warehouse`. Dua terakhir (`monitoring/identity.go`, `warehouse/fulfillment_ops.go`) hanya menyentuh `BIP-System-Roles` untuk gerbang RBAC, tak pernah departemen maupun jabatan. **Baris ini yang paling berguna dari seluruh tabel**: tanpanya orang menganggap semua modul bergantung pada departemen, lalu berhati-hati pada hal yang tak perlu.

⛔ **Jangan mengukur peta ini dari worktree lokal.** Diukur 2026-08-26 dari checkout yang tertinggal **62 commit**, jawabannya menyebut `insentive` sebagai contoh service yang tak memakai struktur organisasi. Yang benar sebaliknya: `services/insentive/hierarki_hris.go` adalah **satu berkas utuh** yang menyusun hierarki insentif dari `position_key` dan `supervisor_id` HRIS. Kesalahannya tak berbunyi apa pun, karena hasil grep yang KURANG terbaca persis seperti "memang tak ada". Ukur ke ref-nya: `git grep <pola> origin/main -- services/`.

### Sisi frontend

**Yang mengelola** (menulis): `/hris/master-data` (departemen, jabatan, jenjang, system role) dan tab **Hak per Posisi** + **Penyetuju Pengajuan** di `/pengaturan/organisasi`, keduanya `RequireHRISOrITSupervisor`; **Atasan Langsung** di `/hris/employee/atasan-langsung`, `RequireHRISOrITStaff`. Gerbangnya sengaja berbeda, lihat §Menemukan layar yang benar.

**Yang membaca**: `/hris/org-chart`, plus **23 pemanggil** `useDataTypes({ endpoint: "department" })` yang tersebar jauh melampaui HRIS (termasuk `/it/employee` dan dua layar **procurement**: `TabUnitKas`, `PersetujuanBudget`). Delapan berkas lagi memakai `endpoint: "position"`.

⚠️ Dari 23 pemanggil itu **hanya 4 yang memakai `grouped`**. Sisanya menerima departemen mentah, dan untuk sebagian layar itu memang yang benar: `template-editor.tsx` sengaja mentah karena **menulis** nama departemen asli ke `kpi_template.department`, dan label grup `HRGA` tak akan pernah cocok dengan `work_data.department` seorang pun (§Cakupan supervisi antar-departemen). Templat yang tersimpan sebagai `HRGA` jadi tanpa galat, lalu tak pernah terpakai menilai siapa-siapa. Putuskan per halaman, jangan sapu massal.

## Belum Diputuskan (TBD)

- ~~Format org chart (visual)~~ — **selesai 2026-08-01**, lihat §Ruang Lingkup
- ~~Jenjang/golongan~~ — **kodenya selesai 2026-08-03** dan live di produksi, lihat §Ruang Lingkup. Yang tersisa memang bagian yang sejak awal disebut bukan urusan kode: **siapa di tingkat mana untuk 79 jabatan**. Nol jabatan terisi; berkas usulan pemetaan menunggu koreksi HR
	- **Yang masih terbuka setelahnya**: apakah jenjang perlu bisa ditambah/diubah lewat layar (sekarang lewat `DefaultJobLevels()` + deploy), dan apakah ELT (Percetakan, 14 orang) memakai tangga yang sama atau tangganya sendiri. ELT sengaja **ditunda**
		- ⚠️ **Angka lama "`position_key` 11 karyawan ELT menunjuk key milik BIP" SUDAH TIDAK BENAR.** Pengukuran ulang ke `employee_db` **produksi** 2026-08-19: **13 dari 14** karyawan ELT ber-`position_key` yang cocok dengan `position_items` departemen `pct` miliknya sendiri (`admin`, `operator_mesin`, `spv_operasional`, dst). Yang menyimpang tinggal **satu**, `ELT-2010-07-26`, ber-`department` = `Manufaktur` dan `position_key` = `operator_production` — keduanya milik BIP, sementara ELT **tidak punya** departemen `Manufaktur` sama sekali di `master_department`. Jadi sisa masalahnya bukan ketidakcocokan massal, melainkan satu karyawan yang menunjuk departemen yang tak ada di perusahaannya
- Penanganan posisi rangkap / matriks
- **Relasi supervisi berjenjang** — saat ini sengaja dibatasi SATU tingkat. Organisasi bertingkat (divisi → departemen → sub-departemen) perlu keputusan tersendiri
- **Satukan `deptKeyToNames`** (`shared-library/common/roles.go`) ke master data — pemetaan role key → nama departemen masih hardcode, dan `finance` → `Finance` + `Procurement` sebenarnya konsep yang sama dengan `supervised_by`. Departemen yang benar-benar baru masih butuh ubah kode di situ **dan** di picker jadwal absensi
	- **Contoh konkretnya kini ada**: departemen **Printing** (2026-08-19, PR [#1276](https://github.com/bip-itteam-internal/bip-erp/pull/1276)) menuntut `DeptPrinting` + entri `deptKeyToNames` + satu `case` di picker jadwal, padahal dokumen departemennya sendiri murni master data. Yang paling menggigit **bukan** `deptKeyToNames` (entrinya inert sampai ada pemegang `system_roles.printing`, dan departemen `marketing` hidup di produksi tanpa pemetaan itu) melainkan **picker jadwal**: departemen BIP yang tak ada di `case` mana pun jatuh ke `default` dan dibalas **400**, sehingga menyimpan Data Pekerjaan karyawannya gagal dengan pesan yang tak menyebut jadwal sama sekali. Lihat [[Microservices - Attendance Service]]

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]]
- [[Microservices - Employee Service]] · [[HRIS - Personalia]] · [[HRIS - Career & Promotion]] · [[HRIS - Interrelationship Matrices]]
