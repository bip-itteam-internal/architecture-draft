# ANALISA - Badan Usaha Dikelola Sekretariat

> **Status**: ⛔ **Menunggu [[ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca]] Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

Blueprint hasil `/analisa-kebutuhan` 2026-10-15 atas permintaan "master badan usaha satu pintu kelola di Sekretariat, bukan di HR". Papan kerja, berubah tiap issue selesai; keputusannya di ADR.

- **Keputusan**: [[ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca]] (merevisi sebagian [[ADR - 0182 Badan Usaha Satu Daftar untuk HR dan Finance, Entitas CV Menempel Tanpa Nama Sendiri]])
- **Dok domain**: [[Unlisted - Kesekretariatan (Big Pictures)]] · [[Microservices - Payroll Service]] · [[REF - Kepemilikan Data]]
- **Pemutus**: `wirkancil`
- **Ukuran**: **Sedang**. Dua repo, masing-masing satu PR: `bip-erp` (izin di `shared-library/common/catalog_secretary.go` + gerbang `/companies*` di `services/payroll/routes.go`) dan `erp-frontend` (halaman dan menu baru; FE tidak merender izin atau menu baru secara generik: menu Sekretariat dirakit eksplisit di `src/components/layout/sidebar-menus.tsx` dan tab Pengaturan Gaji di `src/app/(main)/pengaturan/lib/sections.ts:204-207`). `my-bharata` **tidak** berubah: slip membaca snapshot run (`lib/src/features/payroll/data/models/my_payslip_model.dart:32-39`).
- **Urutan**: [BE] lalu [FE]; deploy BE sebelum FE.

## Kebutuhan dan temuan

- **Kebutuhan sebenarnya**: identitas badan usaha dikelola pemegang legalitasnya (Corporate Secretary); HR dan Finance memakai. Pemicunya prinsip kepemilikan, bukan insiden.
- **Yang sudah ada**: satu daftar (`payroll_company`) dan Entitas CV Finance yang menempel tanpa nama sendiri, merged 2026-10-15 lewat ADR 0182. Yang kurang hanya pintunya.
- **Asumsi eksplisit**: tanpa alur verifikasi akta; tanpa isian legal tambahan; kabar perubahan badan usaha ke HR/Finance hari ini manual.

## Langkah manusia sesudah deploy

1. Pasang paket `secretary.badanusaha.kelola` ke jabatan atau akun Corporate Secretary (tulis prod, manusia).
2. Corporate Secretary merapikan empat data: ejaan "PT. ZAVIRA KIARANA MANDIRI", nama lengkap PT Bharata, NPWP PT Bharata (kosong), NPWP sama `1000000010424024` di PT Citrana Abadi Perkasa dan PT Citravana Mandiri Sejahtera.
3. Finance menekan Semai di Entitas CV supaya PT yang namanya sudah dibetulkan tersambung (ADR 0182 butir 7).

## Issue 1: Induk, `bip-erp`: Badan usaha dikelola Sekretariat, HR dan Finance membaca

- **Repo**: `bip-erp` · **Urutan**: induk, tanpa PR sendiri · **Issue**: [bip-erp#3184](https://github.com/bip-itteam-internal/bip-erp/issues/3184)

**Pemutus:** @wirkancil
**PIC:** @

### Masalah

Daftar Badan Usaha (`payroll_company`, 62 baris: PT Bharata, 21 PT lain, 40 CV) sudah jadi satu-satunya daftar badan usaha (ADR 0182), tetapi pintu tambah/ubahnya HR (`gate(common.PermPayrollManage, isHRAdmin)` di `services/payroll/routes.go`). Pemegang akta dan legalitas badan usaha adalah Corporate Secretary, yang hari ini tak punya izin maupun layar untuk itu.

### Keputusan

ADR "ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca" (vault `architecture-draft/Decisions/`), merevisi sebagian ADR 0182. Layak `Siap Agent` sesudah ADR berstatus Diterima (sekarang 🟡 Diusulkan).

Bentuk: izin baru `secretary.badanusaha.kelola` (paket sendiri, untuk Corporate Secretary) menggerbang tulis `/companies*`; layar pindah ke `/secretary/badan-usaha`; HR dan Finance membaca; data tidak pindah.

Issue induk tanpa PR sendiri. Dikerjakan lewat sub-issue [BE] (bip-erp) lalu [FE] (erp-frontend).

### Yang harus benar

- [ ] Sub-issue [BE] merged dan ter-deploy sebelum [FE] ter-deploy.
- [ ] Sesudah keduanya di prod, Corporate Secretary bisa menambah dan mengubah badan usaha di Sekretariat › Badan Usaha, dan HR tidak bisa (403 di backend, tombol tak tampil di layar).
- [ ] Badan usaha baru dari Sekretariat muncul di Entitas CV Finance sebagai "Badan usaha tanpa entitas".

### Di luar cakupan

- Isian legal baru (akta, NIB, alamat, logo); kop tetap di Entitas CV Finance.
- Memindahkan data ke service lain.
- Alur persetujuan atas perubahan badan usaha.

### Data / bukti pendukung

Diukur PROD 2026-10-15 (baca saja): `payroll_company` 62, `akuntansi_cv_entitas` 62. `employee_salary` 186: PT Bharata 32, PT Gentara 3, CV 89, tanpa `company_id` 62. Corporate Secretary satu orang (`BIP-0069-08-24`, Kesekretariatan). Blueprint: vault `Workspace/ANALISA - Badan Usaha Dikelola Sekretariat.md`.

### Prasyarat

ADR 0183 Diterima. ADR 0182 (bip-erp#3178, erp-frontend#2493) sudah merged.

## Issue 2: [BE] `bip-erp`: Izin Sekretariat untuk tulis daftar Badan Usaha

- **Repo**: `bip-erp` · **Urutan**: 1 · **Issue**: [bip-erp#3185](https://github.com/bip-itteam-internal/bip-erp/issues/3185)

**Pemutus:** @wirkancil
**PIC:** @

### Masalah

Tulis daftar Badan Usaha di payroll-service digerbang izin HR: `app.Post("/companies/impor")`, `app.Post("/companies")`, `app.Put("/companies/:id")`, `app.Delete("/companies/:id")` semuanya `gate(common.PermPayrollManage, isHRAdmin)` (`services/payroll/routes.go`). Katalog `secretary` (`shared-library/common/catalog_secretary.go:81-93`) belum punya izin untuk badan usaha. Komentar `services/finance/akuntansi_cv_daftar.go:17-28` menyebut "Daftar Badan Usaha milik HR".

### Keputusan

ADR "ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca", Decision 1-3. Layak `Siap Agent` sesudah ADR berstatus Diterima.

- Izin baru `secretary.badanusaha.kelola` di katalog `secretary`, paket sendiri (bukan paket Legal/R&D), dipasang ke jabatan Corporate Secretary lewat mekanisme paket default per jabatan yang dipakai katalog ini.
- POST/PUT/DELETE `/companies*` dan POST `/companies/impor`: hanya `secretary.badanusaha.kelola`. `payroll.manage`/admin HR tidak lagi cukup.
- GET `/companies`: tetap `payroll.view`/isHR, DITAMBAH pemegang `secretary.badanusaha.kelola`.

### Yang harus benar

- [ ] Akun dengan `payroll.manage` + admin HR tanpa izin baru: POST, PUT, DELETE `/companies` dan POST `/companies/impor` dibalas 403. Uji lewat `app.Test(httptest.NewRequest(...))`.
- [ ] Akun dengan `secretary.badanusaha.kelola` saja (tanpa peran/izin HR): keempat rute tulis berhasil, dan GET `/companies` dibalas 200 berisi daftar.
- [ ] Akun `payroll.view`/isHR tanpa izin baru: GET `/companies` tetap 200 (HR tetap bisa memilih badan usaha penggaji).
- [ ] Aturan lama tetap: satu default, default tak bisa dihapus (uji yang ada hijau).
- [ ] Paket baru muncul di katalog izin (layar Hak per Posisi) dan bukan bagian paket `secretary_legal_*`/`secretary_rnd_*` maupun "Lihat Semua". Uji katalog menguncinya.
- [ ] `system_roles.secretary` tetap tidak memberi izin apa pun (`TestPeranSecretaryTidakMemberiLegalAtauRnd` dan sejenisnya hijau).
- [ ] Komentar `akuntansi_cv_daftar.go:17-28` diperbarui: daftar dikelola Kesekretariatan, merujuk ADR 0183.
- [ ] `GET /internal/badan-usaha` tidak berubah (Finance tetap membaca).

### Di luar cakupan

- Layar (sub-issue [FE]).
- Memasang paket ke akun Corporate Secretary di prod (langkah manusia sesudah deploy).
- Field baru di `Company`.

### Data / bukti pendukung

PROD 2026-10-15: Corporate Secretary satu orang (`BIP-0069-08-24`), peran turunan jabatannya `secretary: supervisor`, bukan `legal`. Izin di `shared-library` berarti service yang memakai katalog perlu di-rebuild; cache izin gateway 3 menit.

### Prasyarat

ADR 0183 Diterima. Deploy: bip-erp (payroll-service + service pembaca katalog) SEBELUM sub-issue [FE].

## Issue 3: [FE] `erp-frontend`: Layar Badan Usaha di menu Sekretariat, Pengaturan Gaji baca saja

- **Repo**: `erp-frontend` · **Urutan**: 2, deploy sesudah [BE] · **Issue**: [erp-frontend#2498](https://github.com/bip-itteam-internal/erp-frontend/issues/2498)

**Pemutus:** @wirkancil
**PIC:** @

### Masalah

Layar Badan Usaha ada di Pengaturan Gaji (`/pengaturan/payroll?tab=companies`, `src/features/hris/payroll/components/companies-page.tsx`), digerbang `payroll.view` saja tanpa gerbang tulis di layar (`pengaturan/lib/sections.ts:204-207`). Menu Sekretariat (`sidebar-menus.tsx`, kunci `secretary`) belum punya menu Badan Usaha, dan `src/features/panduan/isi/` belum punya berkas untuk Kesekretariatan.

### Keputusan

ADR "ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca", Decision 4. Layak `Siap Agent` sesudah ADR berstatus Diterima.

- Halaman baru `/secretary/badan-usaha` (BUKAN `/legal/*`: proxy `/legal` memeriksa cookie peran `legal` yang tak dipegang Corporate Secretary), menu di Sekretariat ber-`perm: "secretary.badanusaha.kelola"`, isi = tabel + dialog tambah/ubah + impor yang sudah ada di `companies-page.tsx`, dipakai ulang, bukan disalin.
- Tab Badan Usaha di Pengaturan Gaji: baca saja (tanpa tombol tambah/ubah/hapus/impor) + satu kalimat bahwa perubahan dilakukan Kesekretariatan di Sekretariat › Badan Usaha.

### Yang harus benar

- [ ] Pemegang `secretary.badanusaha.kelola` melihat menu Sekretariat › Badan Usaha, dan di halamannya bisa tambah, ubah, hapus (kecuali default), set default, dan impor.
- [ ] Tanpa izin itu, menu tidak tampil dan membuka `/secretary/badan-usaha` langsung menampilkan keadaan tak berizin, bukan form.
- [ ] Tab Badan Usaha di Pengaturan Gaji menampilkan daftar yang sama tanpa satu pun tombol tulis, dengan kalimat penunjuk ke Sekretariat.
- [ ] Pilih badan usaha penggaji di struktur gaji dan buat karyawan tetap jalan (`use-isian-struktur-gaji.ts`, `pilih-badan-usaha.tsx`).
- [ ] Teks baru lewat i18n di `id.ts` dan `en.ts`.
- [ ] Panduan menu baru ditulis di `src/features/panduan/isi/` untuk Kesekretariatan (berkas baru mengikuti pola `isi/marketing.ts`), atau URL-nya dicatat di daftar `BELUM_DITULIS_*` departemen itu; uji penjaga panduan hijau. Panduan `/pengaturan/payroll` di `hrga.ts` diperbarui bila menyebut menambah badan usaha.
- [ ] `pnpm tsc --noEmit`, `pnpm lint`, `pnpm build` hijau; `pnpm test` tanpa kegagalan baru dibanding baseline `origin/main`.

### Di luar cakupan

- Entitas CV Finance (`/finance/entitas-cv`) tidak berubah.
- Isian baru di form badan usaha.
- Menghapus berkas mati `company-config-form.tsx` (boleh, tapi bukan syarat).

### Data / bukti pendukung

Tidak perlu data prod. Corporate Secretary di prod satu orang; paket dipasang manusia sesudah deploy BE.

### Prasyarat

Sub-issue [BE] merged. Deploy SESUDAH [BE] ter-deploy di prod (kalau FE duluan, layar Sekretariat menerima 403).
