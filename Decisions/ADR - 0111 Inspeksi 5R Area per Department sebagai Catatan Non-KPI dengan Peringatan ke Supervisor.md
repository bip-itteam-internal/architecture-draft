> **Status**: ⚠️ **Implemented sebagian, di BRANCH — belum merged, belum deploy.** T1+T2 (tulis+foto) mendarat di `origin/main` 2026-09-21 (`services/employee/area_inspection.go`, commit `6d5f4634`). **T3+T4+T5 dibuat 2026-09-23 dan di-push ke branch, BELUM merged ke `main`, BELUM prod, mobile BELUM diuji perangkat:** T3 baca/rekap di bip-erp `feat/area-inspection-baca-rekap` (`services/employee/area_inspection_read.go`, 9 test Fiber hijau); T5 rekap web SPV di erp-frontend `feat/area-inspection-rekap-web` (tab "Inspeksi Area", build + 27 test hijau); T4 mode isi petugas di my-bharata `feat/faiz` (`lib/src/features/area_inspection/*`, `dart analyze` bersih + `flutter test` 1538 hijau). T6 (KPI & push SPV) tetap **TBD**. Menambah track KETIGA di payung Satgas/Industrial Relation; **tidak** mengubah track per-PIC (ADR 0090) maupun catatan per-orang (ADR 0085). Rincian di `## Deskripsi`.

## Untuk Manajemen

Menambah cara inspeksi **5R per ruangan/area department** di aplikasi. Petugas Culture & Industrial berkeliling, dan untuk **tiap department** (bukan tiap orang) mencatat "ada temuan atau tidak" beserta **hingga 15 foto** bukti. Hasilnya menjadi **catatan** yang bisa dibaca **atasan (supervisor) department** yang bersangkutan, sebagai peringatan untuk membenahi ruangannya.

**Apa yang berubah di layar:** menu Satgas 5R di MyBharata mendapat mode baru "per ruangan/department" (daftar department, isi temuan + foto per department). Di Web ERP, supervisor department bisa membaca rekap temuan ruangannya.

**Siapa yang terdampak:** petugas Culture & Industrial (mengisi), dan supervisor tiap department (membaca temuan ruangannya).

**Apa yang TIDAK dijanjikan:** ini **catatan pembinaan area**, **bukan** KPI, **bukan** Surat Peringatan, **bukan** potongan gaji. Penilaian KPI per orang untuk Office Boy & Security **tetap** lewat jalur yang sudah ada dan **tidak berubah**. Pada tahap pertama **tidak** ada notifikasi push otomatis ke supervisor — rekapnya dibaca saat menu dibuka.

**Perkiraan besaran kerja:** sedang. Bahan sudah banyak yang bisa dipakai ulang (gerbang petugas, unggah foto + kompres di MyBharata, resolusi supervisor per department, pola rekap per-department). Yang baru: satu penyimpanan catatan inspeksi area, satu mode di menu Satgas MyBharata, dan satu rekap area untuk supervisor di Web. Perlu rilis backend lebih dulu, lalu aplikasi.

## Deskripsi

*Inspeksi 5R yang objeknya **ruangan/area sebuah department** (bukan seorang PIC), dicatat oleh petugas Culture & Industrial sebagai **sinyal pembinaan non-KPI** dengan hingga 15 foto per department per periode, dan dibaca supervisor department yang bersangkutan. Ia **meminjam POLA** [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] (gerbang petugas, visibilitas ke supervisor, foto bukti, entitas terpisah, non-KPI), tetapi subjeknya **department**, bukan karyawan. Berdiri di samping — bukan menggantikan — track per-PIC ber-KPI [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]].*

- **Status**: ⚠️ **Implemented sebagian, di branch** (lihat status baris pertama). T1–T5 ada di kode; T6 TBD. Artefak kerja: `Workspace/ANALISA - Inspeksi 5R Area per Department.md`
- **Path di repo**:
  - bip-erp (**T1+T2 merged `main`**): `shared-library/models/employee/area_inspection.go` · `services/employee/area_inspection.go` (tulis + foto) · registrasi di `main.go`
  - bip-erp (**T3, branch `feat/area-inspection-baca-rekap`**): `services/employee/area_inspection_read.go` (roster petugas, rekap petugas/supervisor, preview foto) · `area_inspection_read_test.go` · `registerAreaInspectionReadRoutes` di `area_inspection.go`
  - erp-frontend (**T5, branch `feat/area-inspection-rekap-web`**): `src/app/(main)/hris/industrial-relation/page.tsx` (tab "Inspeksi Area") · `src/features/hris/industrial-relation/components/area-inspection-rekap.tsx` · `.../hooks/use-area-inspection.ts` · `.../types/area-inspection.ts` · `src/features/erp/auth/hooks/use-auth.ts` (`isAnySupervisor`) · `src/i18n/locales/{id,en}.ts`
  - my-bharata (**T4, branch `feat/faiz`**): `lib/src/features/area_inspection/*` (data/domain/presentation) · registrasi di `lib/src/core/config/di/*` · entri di `lib/src/features/satgas/presentation/pages/satgas_page.dart` (AppBar) · `lib/l10n/app_{id,en}.arb`. Endpoint didefinisikan **lokal di datasource**, bukan `Api/url.dart` (§Consequences).
- **Tanggal**: 2026-09-21 (T3–T5 diimplementasikan 2026-09-23)

## Context

Tiga track kini hidup di payung Satgas/Industrial Relation, dan ketiganya dipegang petugas yang **sama** (jabatan **Culture & Industrial**, `position_key: culture_industrial`; gerbang `kepatuhan.satgas.input`):

| Track | Objek yang dinilai | KPI? | Sumber |
|---|---|---|---|
| Satgas per-PIC | Office Boy/Security (orang) | **Ya** — KPI individual | [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] |
| Catatan Kepatuhan | Karyawan (atribut kerja) | Tidak | [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] |
| **5R Area (keputusan ini)** | **Ruangan/area department** | **Tidak** — catatan + peringatan SPV | ADR ini |

Kebutuhan datang dari pemakainya: 5R secara praktik adalah inspeksi **AREA** (ruangan department), bukan penilaian per orang. Track per-PIC (ADR 0090) benar untuk KPI Office Boy/Security, tetapi **bukan** tempat mencatat "ruangan Manufaktur berantakan" — di sana tak ada orang tunggal yang tepat dinilai, dan menautkannya ke KPI seseorang justru salah alamat. Kebutuhannya: **catatan area + peringatan ke atasan department**, tegas **bukan** KPI.

Grounding ke kode (bip-erp `origin/main`, erp-frontend, my-bharata `feat/faiz`, 2026-09-21):

1. **Subjek penilaian yang ada MODELNYA per-orang.** `FormSubject.Resolved` adalah `[]employeeRef` dan `matchesSubject` mengembalikan karyawan (`services/form-builder/subject.go:95-113`, `models_form.go:404-438`). Tak ada konsep "department sebagai objek yang dinilai". Submit pun `subject_employee_id` (`services/form-builder/response_handlers.go:395-404`). Jadi track baru **tak bisa** memakai ulang mesin subject form-builder apa adanya.
2. **Catatan Kepatuhan (ADR 0085) juga per-orang.** `compliance_note` berkunci `employee_id` (`ADR 0085 §Decision 1`). Objeknya karyawan+atribut, bukan ruangan department. Jadi track baru **tak bisa** numpang `compliance_note`, tapi **pola**-nya cocok (§Decision di bawah).
3. **Foto = single-file per pertanyaan.** `FieldFile` menyimpan satu `upload_id` per jawaban (`services/form-builder/models_form.go:74-79`); ADR 0090 §7 menunda `max_files`. Kebutuhan ≤15 foto per department adalah kapabilitas baru.
4. **Petugas & gerbang sudah ada.** Jabatan `Culture & Industrial` nyata di `work_data` (diukur dev 2026-09-21; akun uji `TEST-HR-STAFF` berjabatan itu), dan izin `kepatuhan.satgas.input` (modul `kepatuhan`, paket `kepatuhan_petugas_satgas`) sudah menempel ke jabatan itu (ADR 0090 §4, merged bip-erp [#1849](https://github.com/bip-itteam-internal/bip-erp/pull/1849)).
5. **Resolusi supervisor per-department sudah ada di employee-service.** `SupervisedDepartmentsStrict` (dipakai gerbang baca SP dan direncanakan ADR 0085) memetakan atasan → department yang diawasinya, tanpa fallback `BIP-Department`. Filter department wajib lewat `ResolveDepartmentFilter` + `ExpandToDepartmentGroup` (gotcha HRGA: label grup tak pernah cocok `work_data.department` siapa pun — [[CORE - RBAC dan Permission Set]]).
6. **`BUSINESS_LOGIC_IMPLEMENTATION.md` tak memuat pasal 5R/K3/area** (git grep kosong, kontrol positif "mangkir"; sama dengan ADR 0090 §Context 10 dan ADR 0085). Jadi catatan area ini murni pembinaan, tak bertabrakan tabel sanksi mana pun.

⚠️ **Status dok tetangga:** [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] berstatus 🟡 (kode `compliance_note` sedang dirintis di `feat/faiz`, belum matang). Keputusan ini **meminjam polanya**, jadi ia berdiri sebagian di atas rencana — dinyatakan terang di sini, dan task-nya menuntut verifikasi pola itu saat pembangunan, bukan mengasumsikannya sudah jadi.

## Decision

### 1. Entitas terpisah untuk inspeksi area, bukan tumpangan

Inspeksi 5R area hidup di **koleksi/entitas baru** (mis. `area_inspection`) di **employee-service** — service yang sama dengan `compliance_note` (ADR 0085) dan yang **memiliki** resolusi department/supervisor. Bukan di form-builder (mesinnya per-PIC + KPI, §Context 1), bukan menumpang `compliance_note` (per-orang, §Context 2), bukan `kpi_score`, bukan `employee_warning`. Pemisahan koleksi membuat batas "area ≠ orang ≠ KPI ≠ sanksi" **struktural**, bukan janji — persis alasan ADR 0085 §1.

Subjeknya **department** (nilai `work_data.department` / master department), bukan `employee_id`. Satu dokumen inspeksi = (department, periode, petugas, ada_temuan, foto[], catatan).

### 2. Non-KPI, tegas — track per-PIC tak disentuh

Modul ini **tidak** menulis `kpi_score`, **tidak** membuat `employee_warning`, **tidak** dibaca payroll. **KPI Office Boy & Security tetap** lewat track per-PIC ADR 0090 dan **tidak berubah**; kerja `feat/satgas-input-web` yang sudah merge **tetap sah**. Bila kelak manajemen ingin skor area ikut memengaruhi KPI seseorang (mis. penanggung jawab ruangan), itu **keputusan baru** yang menuntut ADR tersendiri — **tidak** otomatis di sini.

### 3. Pencatat = petugas Culture & Industrial, gerbang server, reuse izin `kepatuhan`

Yang boleh mencatat hanya petugas ber-izin **`kepatuhan.satgas.input`** — sama dengan petugas Satgas per-PIC, karena orangnya memang sama. `POST` diperiksa **di server**; pemunculan mode/menu di MyBharata **bukan** gerbang (pola ADR 0085 §4 dan ADR 0090 §4). **Tidak** membuat izin kedua untuk petugas yang sama, kecuali `/plan` menemukan alasan pemisahan (mis. petugas area ≠ petugas PIC) — bila muncul, izin baru di modul `kepatuhan` yang sama, bukan modul kedua.

### 4. Visibilitas dua-arah: petugas + supervisor department

Baca: **petugas Culture & Industrial** se-perusahaan, dan **supervisor** atas **department yang diawasinya** (`SupervisedDepartmentsStrict`, tanpa fallback). Berbeda dari ADR 0085 yang tiga-arah: di sini **tak ada "diri sendiri"** karena objeknya ruangan, bukan orang. Filter department wajib `ResolveDepartmentFilter` + `ExpandToDepartmentGroup` (gotcha HRGA). Mengikuti preseden SP & ADR 0085: **tidak** didaftarkan ke [[Microservices - Calendar Service]] maupun feed lintas modul.

### 5. Peringatan ke supervisor = rekap saat dibuka (irisan-1), push ditunda

"Memperingatkan department lewat SPV-nya" pada irisan pertama berarti **supervisor melihat rekap temuan ruangannya saat membuka menu** (pola rekap ADR 0085 §6 / `kpi_ringkasan_departemen.go`, tanpa cron). **Notifikasi push/inbox ditunda**: kategori inbox baru menuntut notification-service + service pengirim naik **bersama** (kelas gotcha "kategori inbox = deploy dua container", [[RUN - Deploy Microservices bip-erp]]) dan ADR/revisi tersendiri. Ditambahkan bila rekap-saat-dibuka terbukti kurang.

### 6. Objek = daftar department yang berdiri, ≤15 foto per department per periode

Petugas melihat **daftar department** (master department BIP, diukur dev 2026-09-21: 12 department) dan mengisi kapan saja dalam periode berjalan — **tidak** perlu membuat form per inspeksi (inilah yang menjawab friksi "buat form tiap inspeksi ribet"). Periode **bulanan** (sejajar Satgas per-PIC). **≤15 foto per department per periode**, disimpan di file-service (MinIO) seperti bukti `compliance_note`; batas 4 MB/file file-service tidak dinaikkan. Angka 15 dan apakah per-temuan vs per-department dikunci saat `/plan`.

### 7. MyBharata: mode dalam menu Satgas yang sama, bukan menu terpisah

Objeknya sama-sama "Satgas 5R" dan petugasnya sama, jadi mode area sebaiknya **satu permukaan dengan menu Satgas** (mis. dua mode: "Per PIC" existing + "Per Ruangan/Area" baru), memakai ulang alur isi yang sudah ada (`SurveyFillView`/boolean/`survey_file_input`/kompres foto). Diputuskan final saat `/plan`; yang mengikat di sini: **jangan** menduplikasi komponen isi/unggah yang sudah ada (aturan tim "reuse dulu"; jebakan komponen tiruan).

## Consequences

### Yang membaik

- 5R punya tempat yang benar untuk **inspeksi area** — tanpa memaksa "ruangan" jadi "orang" di jalur KPI.
- Supervisor department melihat temuan ruangannya sebagai bahan pembinaan, tanpa menyentuh SP/gaji/KPI.
- Batas "area ≠ orang ≠ KPI" struktural (koleksi terpisah), sekelas jaminan ADR 0085.
- Track per-PIC ber-KPI (ADR 0090) dan input web yang baru merge **tetap utuh**.

### Yang memburuk atau tetap terbuka

- ⚠️ **Berdiri sebagian di atas ADR 0085 yang masih 🟡.** Pola yang dipinjam (gerbang petugas, `SupervisedDepartmentsStrict`, rekap per-dept) wajib **diverifikasi ada & jalan** saat membangun, bukan diasumsikan matang.
- ⚠️ **KPI sengaja TIDAK dipetakan.** Skor/temuan area tak memengaruhi KPI siapa pun. Bila kelak dituntut, butuh ADR baru + peta department→penanggung jawab yang belum ada.
- **Peringatan hanya rekap-saat-dibuka** di irisan-1; supervisor yang tak membuka menu tak diperingatkan. Push adalah irisan berikutnya (2 container + ADR).
- **Tiga permukaan (BE/Web/Mobile) + tiga sesi Satgas paralel** (`feat/satgas-input-web`, `feat/satgas-rekap`, mobile `feat/faiz`) harus dijaga selaras. Perubahan kontrak → **BE dulu**. Koordinasi wajib agar tak lahir dua model area.
- **Multi-foto (≤15)** adalah kapabilitas unggah baru untuk track ini; pastikan pola unggah-dulu-kirim-id tetp dipakai, bukan mengirim berkas di dalam JSON.

### Yang sengaja tidak dilakukan

- Tidak mengubah track per-PIC (ADR 0090) maupun catatan per-orang (ADR 0085).
- Tidak menulis `kpi_score`, tidak membuat SP, tidak menyentuh payroll.
- Tidak ada notifikasi push/inbox pada irisan pertama (kategori inbox baru = deploy dua container + ADR).
- Tidak ada master "area/ruangan" tersendiri di luar daftar department, sampai ada pemakai nyata yang menuntutnya (aturan "tunggu pemakai ketiga").

### Diputuskan saat implementasi (2026-09-23)

- **Visibilitas SPV di web TANPA klaim JWT baru.** §4/§5 menuntut supervisor department bisa membaca; diimplementasikan sebagai **gerbang backend** (`common.SupervisedDepartmentsStrict` + `employee.ExpandToDepartmentGroup`, deny-by-default 403 di `GET /area-inspections/rekap`) ditambah **tab web yang sekadar TAMPIL** bila pemanggil punya peran supervisor modul mana pun (`isAnySupervisor(system_roles)` di `use-auth.ts`). Usul menambah klaim `is_supervisor` ke JWT **ditolak/ditunda**: minting token tersebar di ~7 jalur login `api-gateway/main.go` (blast-radius auth tinggi), dan cakupan sebenarnya sudah ditegakkan server, jadi klaim FE hanya untuk menyembunyikan menu — cukup peran modul. Konsekuensi diterima: SPV yang tak berperan supervisor modul mana pun tak melihat tab walau backend mungkin mengizinkannya; bila kelak menggigit, klaim JWT adalah perbaikan durabelnya (ADR/task tersendiri).
- **Mobile HANYA untuk petugas pencatat.** §7 diwujudkan sebagai fitur `area_inspection` tersendiri yang dijangkau dari **AppBar menu Satgas** (ikon gedung, muncul saat `overview.allowed`), bukan mode-toggle di dalam `SatgasView` (yang diuji ketat). SPV **tidak** mendapat menu mobile — ia membaca di web; notifikasi push ke SPV tetap ditunda (irisan berikutnya, §5).
- **Endpoint mobile didefinisikan LOKAL di datasource**, bukan `Api`/`core/api/url.dart`, karena url.dart sedang disunting paralel di `feat/faiz`; commit mobile jadi swasembada (kompilasi tanpa perubahan sesi lain). Bila url.dart bebas, pindahkan mengikuti konvensi repo (task kecil tersendiri).
- **Satu inspeksi per (department, periode)** dipastikan lewat **upsert** (index unik T2), tanpa alur cek-ulang temuan→perbaikan terpisah seperti track per-PIC. Submit ulang memperbarui `ada_temuan`/`catatan`; foto ditambah, tak menghapus yang lama.

## Dokumen Terkait

- [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] — track per-PIC ber-KPI yang keputusan ini **tidak** ubah
- [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] — pola non-KPI yang dipinjam (gerbang petugas, visibilitas, foto, entitas terpisah)
- [[HRIS - Industrial Relation]] — dok domain (cara kerja modulnya); daftar task `Workspace/ANALISA - Inspeksi 5R Area per Department.md`
- [[HRIS - Disciplinary (Surat Peringatan)]] — sumber pola visibilitas & `SupervisedDepartmentsStrict`
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] — kenapa track ini tak menulis `kpi_score`
- [[CORE - RBAC dan Permission Set]] — modul izin `kepatuhan`, gotcha HRGA
- [[Microservices - Employee Service]] — rumah entitas & resolusi supervisor · [[Microservices - File Service]] — foto bukti · [[Microservices - Calendar Service]] — prinsip tiga-lapis (kenapa tak masuk feed)
- [[APP - MyBharata]] · [[APP - Web ERP]]
