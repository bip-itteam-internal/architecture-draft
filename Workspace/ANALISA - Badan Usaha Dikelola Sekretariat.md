# ANALISA - Badan Usaha Dikelola Sekretariat

> **Status**: ⛔ **Menunggu [[ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca]] Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

Blueprint hasil `/analisa-kebutuhan` 2026-10-15 atas permintaan "master badan usaha satu pintu kelola di Sekretariat, bukan di HR". Papan kerja, berubah tiap issue selesai; keputusannya di ADR.

- **Keputusan**: [[ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca]] (merevisi sebagian [[ADR - 0182 Badan Usaha Satu Daftar untuk HR dan Finance, Entitas CV Menempel Tanpa Nama Sendiri]])
- **Dok domain**: [[Unlisted - Kesekretariatan (Big Pictures)]] · [[Microservices - Payroll Service]] · [[REF - Kepemilikan Data]]
- **Pemutus**: `wirkancil`
- **Ukuran**: **Besar** (sejak kop masuk, 2026-10-15): dua repo, masing-masing dua PR berurutan (bagian 1/2 izin + isian, bagian 2/2 kop). Awalnya Sedang: `bip-erp` (izin di `shared-library/common/catalog_secretary.go` + gerbang `/companies*` di `services/payroll/routes.go`) dan `erp-frontend` (halaman dan menu baru; FE tidak merender izin atau menu baru secara generik: menu Sekretariat dirakit eksplisit di `src/components/layout/sidebar-menus.tsx` dan tab Pengaturan Gaji di `src/app/(main)/pengaturan/lib/sections.ts:204-207`). `my-bharata` **tidak** berubah: slip membaca snapshot run (`lib/src/features/payroll/data/models/my_payslip_model.dart:32-39`).
- **Urutan**: [BE] lalu [FE]; deploy BE sebelum FE.

## Status 2026-10-16

Kelima issue di bawah **merged (2026-10-15) dan di PROD (2026-10-16)** walau ADR masih Diusulkan, atas perintah user: bip-erp#3185 → PR #3207, bip-erp#3202 → PR #3210 (pengganti #3209 yang tertutup otomatis), bip-erp#3203 → PR #3208, erp-frontend#2498 → PR #2526, erp-frontend#2520 → PR #2527. Status board: Menunggu Adopsi.

⚠️ Blok issue di bawah adalah salinan 2026-10-15 dan **tertinggal dari badan issue di GitHub** pada tiga hal yang diputuskan sesudahnya: form tambah/ubah berupa **halaman** (bukan dialog), **nama unik** (409), dan master wilayah. Badan issue di GitHub yang final; ADR 0183 butir 11-14 memuat keputusannya.

Lanjutan (Backlog): **bip-erp#3212** "Provinsi dan kota badan usaha dipilih dari master wilayah" dengan sub [BE] bip-erp#3213 dan [FE] erp-frontend#2530 (ADR 0183 butir 14).

Langkah manusia yang masih terbuka: pasang paket "Sekretariat: Badan Usaha" ke Corporate Secretary, umumkan ke HR, rapikan 4 data, Finance menekan Semai, catat rilis.

## Kebutuhan dan temuan

- **Kebutuhan sebenarnya**: identitas badan usaha dikelola pemegang legalitasnya (Corporate Secretary); HR dan Finance memakai. Pemicunya prinsip kepemilikan, bukan insiden.
- **Yang sudah ada**: satu daftar (`payroll_company`) dan Entitas CV Finance yang menempel tanpa nama sendiri, merged 2026-10-15 lewat ADR 0182. Yang kurang hanya pintunya.
- **Asumsi eksplisit**: tanpa alur verifikasi akta; tanpa isian legal tambahan; kabar perubahan badan usaha ke HR/Finance hari ini manual.

## Langkah manusia sesudah deploy

1. Pasang paket `secretary.badanusaha.kelola` ke jabatan atau akun Corporate Secretary (tulis prod, manusia).
2. Corporate Secretary merapikan empat data: ejaan "PT. ZAVIRA KIARANA MANDIRI", nama lengkap PT Bharata, NPWP PT Bharata (kosong), NPWP sama `1000000010424024` di PT Citrana Abadi Perkasa dan PT Citravana Mandiri Sejahtera.
3. Finance menekan Semai di Entitas CV supaya PT yang namanya sudah dibetulkan tersambung (ADR 0182 butir 7).
4. Sesudah bagian 2/2 naik, Corporate Secretary mengelola kop di Sekretariat › Badan Usaha; Finance tak lagi mengubah kop.

## Issue 1: Induk, `bip-erp`: Badan usaha dikelola Sekretariat, HR dan Finance membaca

- **Urutan**: induk, tanpa PR sendiri · **Issue**: [bip-erp#3184](https://github.com/bip-itteam-internal/bip-erp/issues/3184)

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


## Issue 2: [BE] `bip-erp`: Izin Sekretariat dan isian baru badan usaha (bagian 1/2)

- **Urutan**: 1 · **Issue**: [bip-erp#3185](https://github.com/bip-itteam-internal/bip-erp/issues/3185)



**Pemutus:** @wirkancil
**PIC:** @

### Masalah

Tulis daftar Badan Usaha di payroll-service digerbang izin HR: `app.Post("/companies/impor")`, `app.Post("/companies")`, `app.Put("/companies/:id")`, `app.Delete("/companies/:id")` semuanya `gate(common.PermPayrollManage, isHRAdmin)` (`services/payroll/routes.go`). Katalog `secretary` (`shared-library/common/catalog_secretary.go:81-93`) belum punya izin untuk badan usaha. Komentar `services/finance/akuntansi_cv_daftar.go:17-28` menyebut "Daftar Badan Usaha milik HR".

### Keputusan

ADR "ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca", Decision 1-3. Layak `Siap Agent` sesudah ADR berstatus Diterima.

- Izin baru `secretary.badanusaha.kelola` di katalog `secretary`, paket sendiri (bukan paket Legal/R&D), dipasang ke jabatan Corporate Secretary lewat mekanisme paket default per jabatan yang dipakai katalog ini.
- POST/PUT/DELETE `/companies*` dan POST `/companies/impor`: hanya `secretary.badanusaha.kelola`. `payroll.manage`/admin HR tidak lagi cukup.
- GET `/companies`: tetap `payroll.view`/isHR, DITAMBAH pemegang `secretary.badanusaha.kelola`.
- Field baru di `Company` (ADR 0183 butir 6-8), semua opsional: alamat sesuai NPWP, NIB, nomor + tanggal akta pendirian, nomor + tanggal akta perubahan terakhir, nomor SK Kemenkumham, dan penanda `inactive` (tidak beroperasi, bawaan false). Badan usaha tidak beroperasi tidak bisa jadi default dan tidak bisa ditetapkan baru sebagai penggaji.

### Yang harus benar

- [ ] Akun dengan `payroll.manage` + admin HR tanpa izin baru: POST, PUT, DELETE `/companies` dan POST `/companies/impor` dibalas 403. Uji lewat `app.Test(httptest.NewRequest(...))`.
- [ ] Akun dengan `secretary.badanusaha.kelola` saja (tanpa peran/izin HR): keempat rute tulis berhasil, dan GET `/companies` dibalas 200 berisi daftar.
- [ ] Akun `payroll.view`/isHR tanpa izin baru: GET `/companies` tetap 200 (HR tetap bisa memilih badan usaha penggaji).
- [ ] Aturan lama tetap: satu default, default tak bisa dihapus (uji yang ada hijau).
- [ ] Paket baru muncul di katalog izin (layar Hak per Posisi) dan bukan bagian paket `secretary_legal_*`/`secretary_rnd_*` maupun "Lihat Semua". Uji katalog menguncinya.
- [ ] `system_roles.secretary` tetap tidak memberi izin apa pun (`TestPeranSecretaryTidakMemberiLegalAtauRnd` dan sejenisnya hijau).
- [ ] Komentar `akuntansi_cv_daftar.go:17-28` diperbarui: daftar dikelola Kesekretariatan, merujuk ADR 0183.
- [ ] `GET /internal/badan-usaha` tidak berubah (Finance tetap membaca).
- [ ] `Company` punya field opsional `address`, `nib`, `deed_number`, `deed_date`, `deed_amendment_number`, `deed_amendment_date`, `sk_kemenkumham` (string) dan `inactive` (bool, `omitempty`). POST dan PUT `/companies` menyimpannya, GET mengembalikannya. Tanggal wajib `yyyy-MM-dd` bila diisi, selain itu 400. Dokumen lama tanpa field ini terbaca beroperasi (uji decode dokumen tanpa field).
- [ ] `inactive: true` bersama `is_default: true` ditolak 400, termasuk menandai default yang sudah ada sebagai tidak beroperasi.
- [ ] Penetapan BARU badan usaha tidak beroperasi sebagai penggaji ditolak 422 di setiap rute yang menulis `company_id` (struktur gaji, versi gaji, rencana badan usaha); menyimpan ulang nilai yang sudah tersimpan (tidak berubah) tetap diterima.

### Di luar cakupan

- Layar (sub-issue [FE]).
- Memasang paket ke akun Corporate Secretary di prod (langkah manusia sesudah deploy).
- Mencetak data legal di slip atau dokumen apa pun.
- Memindah karyawan yang sudah tercatat di badan usaha tidak beroperasi.

### Data / bukti pendukung

PROD 2026-10-15: Corporate Secretary satu orang (`BIP-0069-08-24`), peran turunan jabatannya `secretary: supervisor`, bukan `legal`. Izin di `shared-library` berarti service yang memakai katalog perlu di-rebuild; cache izin gateway 3 menit.

### Arah pengerjaan (dibaca dari `origin/main` 2026-10-15; ukur ulang bila basi)

1. **Izin dan paket**, `shared-library/common/catalog_secretary.go`:
   - Konstanta `PermSecretaryBadanUsahaKelola = "secretary.badanusaha.kelola"` dengan komentar gaya konstanta lain di berkas itu (apa yang dibukanya, rujuk ADR 0183).
   - Masukkan ke `SecretaryPermissionCatalog()`. Akibatnya supervisor/admin IT ikut mendapatkannya lewat `superAksesITSecretary`; itu sama dengan izin Sekretariat lain dan diterima.
   - **JANGAN** masukkan ke `SecretaryTierDefault` (tak ada tier lama untuk badan usaha) maupun paket "Sekretariat: Lihat Semua".
   - Key paket `SetKeySecretaryBadanUsaha = "secretary_badan_usaha"` + satu entri baru di `DefaultSecretarySets()`: Name "Sekretariat: Badan Usaha", Module `ModuleSecretary`, Permissions `[PermSecretaryBadanUsahaKelola]`, Reach `ReachAll`, Description bahasa manusia ("Menambah dan mengubah daftar badan usaha (PT, CV) yang dipakai slip gaji dan Finance.").
   - Paket ini di-seed employee-service lewat `shared-library/models/employee/permission_set.go` (pemanggil `DefaultSecretarySets()`); tak perlu kode seed baru.
2. **Gerbang payroll**, `services/payroll/rbac.go`:
   - ⛔ **JANGAN pakai `gate(common.PermSecretaryBadanUsahaKelola, ...)`.** `gate()` memeriksa `izinPayrollEfektif`, yang hanya memuat izin modul payroll, jadi izin `secretary.*` selalu 403.
   - Tambah `gateTulisBadanUsaha()`: kill-switch `permissionEnforcementEnabled` mati → `require(isHRAdmin)` (perilaku pra-fitur, sesuai kontrak `gate`). Menyala → identitas kosong 401; lolos hanya bila `common.IzinSecretaryEfektif(c)[common.PermSecretaryBadanUsahaKelola]`; selain itu 403.
   - Tambah `gateBacaBadanUsaha()`: kill-switch mati → `require(isHR)`. Menyala → lolos bila `izinPayrollEfektif(c, id)[common.PermPayrollView]` **ATAU** izin Sekretariat di atas.
3. **Rute**, `services/payroll/routes.go`: `GET /companies` → `gateBacaBadanUsaha()`; `POST /companies/impor`, `POST /companies`, `PUT /companies/:id`, `DELETE /companies/:id` → `gateTulisBadanUsaha()`. `GET /companies/:id/karyawan` dan rute `badan_usaha_rencana.go` **tidak** diubah. Urutan pendaftaran rute literal sebelum `:id` dipertahankan.
4. **Finance**, `services/finance/akuntansi_cv_daftar.go`: perbarui komentar paket (baris 17-28: "Daftar Badan Usaha milik HR") jadi dikelola Kesekretariatan (ADR 0183), dan pesan di `tolakUbahEntitasTersimpan` (baris ~173) dari "ubah di Pengaturan Gaji › Badan Usaha" jadi "ubah di Sekretariat › Badan Usaha". Sesuaikan test yang mengunci teks pesan itu bila ada (`git grep "Pengaturan Gaji › Badan Usaha" -- services/finance`).
5. **Test**:
   - Uji katalog di `shared-library/common` (pola test katalog secretary yang ada): izin ada di katalog, ada di paket baru, TIDAK ada di `SecretaryTierDefault(...)` untuk tier mana pun, TIDAK ada di paket Lihat Semua.
   - Uji rute di `services/payroll` lewat `app.Test(httptest.NewRequest(...))` dengan header identitas + `BIP-Permissions` (tiru test gerbang payroll yang ada): matriks "Yang harus benar" + satu kasus kill-switch mati (admin HR lolos tulis).
   - Kontrol negatif: ganti sebentar gerbang tulis ke `gate(PermSecretaryBadanUsahaKelola, isHRAdmin)` dan pastikan uji pemegang izin Sekretariat merah, lalu kembalikan.
5b. **Field baru**, `services/payroll/models_company.go` (struct `Company`) + `CompanyPayload`/handler di `company_handlers.go` (map `` ~baris 99 menyimpan field satu per satu, jadi field baru wajib ditambahkan di sana juga; tanpa itu field diterima lalu dibuang diam-diam). Json/bson snake_case seperti field lama; `inactive` ber-`omitempty`. `CompanySnapshot` dan impor massal (`company_impor.go`) TIDAK wajib membawa field legal. Cari semua tempat yang memeriksa keberadaan `company_id` sebelum menyimpan penetapan penggaji: `git grep -n "payroll_company" -- services/payroll` (titik awal: `badan_usaha_rencana.go:98,156`, handler `employee_salary`, versi gaji), lalu tambahkan penolakan bila badan usaha `inactive` DAN nilainya berubah dari yang tersimpan.
6. **Verifikasi lokal**: `go build ./...` di modul yang tersentuh, `go test ./shared-library/common/... ./services/payroll/... ./services/finance/...` lewat antrean.
7. **Catatan PR untuk deploy (bukan dikerjakan agent)**: naik payroll-service, finance-service, dan employee-service (seed paket); lalu pengelola memasang paket "Sekretariat: Badan Usaha" ke jabatan Corporate Secretary di layar Hak per Posisi.
### Prasyarat

ADR 0183 Diterima. Deploy: bip-erp (payroll-service + service pembaca katalog) SEBELUM sub-issue [FE].


## Issue 3: [FE] `erp-frontend`: Layar Badan Usaha di Sekretariat, Pengaturan Gaji baca saja (bagian 1/2)

- **Urutan**: 2, deploy sesudah #3185 · **Issue**: [erp-frontend#2498](https://github.com/bip-itteam-internal/erp-frontend/issues/2498)



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
- [ ] Form badan usaha memuat isian baru ADR 0183 butir 6-7, dikelompokkan di bagian "Data legal": alamat sesuai NPWP (textarea), NIB, nomor + tanggal akta pendirian, nomor + tanggal akta perubahan terakhir, nomor SK Kemenkumham; ditambah saklar "Tidak beroperasi" yang terkunci bila badan usaha itu default. Tanggal memakai `DateStringPicker` (`@/components/ui/date-picker`), BUKAN `<input type="date">` (ui-checklist §2d).
- [ ] Tabel menandai badan usaha tidak beroperasi dengan label teks (bukan warna saja), dan pilihan badan usaha penggaji (`company-options.ts`, dipakai struktur gaji dan buat karyawan) menyembunyikan yang tidak beroperasi, kecuali nilai yang sedang tersimpan di karyawan itu (tetap tampil, berlabel).
- [ ] Teks baru lewat i18n di `id.ts` dan `en.ts`.
- [ ] Panduan menu baru ditulis di `src/features/panduan/isi/` untuk Kesekretariatan (berkas baru mengikuti pola `isi/marketing.ts`), atau URL-nya dicatat di daftar `BELUM_DITULIS_*` departemen itu; uji penjaga panduan hijau. Panduan `/pengaturan/payroll` di `hrga.ts` diperbarui bila menyebut menambah badan usaha.
- [ ] `pnpm tsc --noEmit`, `pnpm lint`, `pnpm build` hijau; `pnpm test` tanpa kegagalan baru dibanding baseline `origin/main`.

### Di luar cakupan

- Entitas CV Finance (`/finance/entitas-cv`) tidak berubah.
- Mencetak data legal di slip atau dokumen apa pun.
- Menghapus berkas mati `company-config-form.tsx` (boleh, tapi bukan syarat).

### Data / bukti pendukung

Tidak perlu data prod. Corporate Secretary di prod satu orang; paket dipasang manusia sesudah deploy BE.

### Arah pengerjaan (dibaca dari `origin/main` 2026-10-15; ukur ulang bila basi)

1. **Izin menu**, `src/utils/menu-permission.ts`:
   - Tambah ke tabel `FALLBACK` (dekat entri `secretary.legal.*` ~baris 483): `"secretary.badanusaha.kelola": () => false`.
   - ⛔ **Wajib.** `bolehMenu` mengembalikan `true` untuk izin tanpa entri `FALLBACK` bagi akun yang tak memegang izin modul `secretary`, jadi tanpa entri ini menu tampil ke hampir semua orang. Uji di `menu-permission` (pola test yang ada): pemegang izin → true; akun HR tanpa paket Sekretariat → false.
2. **Menu**, `src/components/layout/sidebar-menus.tsx` blok `secretary` (~baris 2394): tambah `{ title: "Badan Usaha", url: "/secretary/badan-usaha", icon: Building2, perm: "secretary.badanusaha.kelola" }`. Judul ikut mekanisme i18n judul sidebar yang dipakai item lain di blok itu (cek `sidebar.tsx`/kunci sidebar di `id.ts`/`en.ts`).
3. **Komponen**, `src/features/hris/payroll/components/companies-page.tsx`:
   - Beri prop `bolehUbah: boolean` (komponen milik fitur, bukan shared).
   - `false` → sembunyikan tombol Tambah, Ubah, Hapus, dan dialog; tabel tetap.
   - Saat `false`, tampilkan satu kalimat i18n di bawah deskripsi: perubahan badan usaha dilakukan Kesekretariatan di Sekretariat › Badan Usaha.
   - Perluas `companies-page.test.tsx` untuk dua keadaan itu.
4. **Halaman baru** `src/app/(main)/secretary/badan-usaha/page.tsx`:
   - Render `<CompaniesPage bolehUbah />`, tanpa pembungkus padding (§ `p-6` di team-memory).
   - Proxy tak menggerbang `/secretary/*` selain `/secretary/kpi`, jadi halaman memeriksa izin sendiri dengan `bolehMenu("secretary.badanusaha.kelola", permissions, systemRoles)` dari konteks auth yang sama dengan yang dipakai sidebar (tiru cara `src/features/finance/entitas-cv/components/halaman-entitas-cv.tsx` membaca izinnya).
   - Tak berizin → keadaan "tidak punya akses" (komponen kosong/empty state yang sudah ada), bukan form.
   - ⛔ JANGAN taruh di `/legal/*`: proxy memeriksa cookie peran `legal`, yang tak dipegang Corporate Secretary.
5. **Pengaturan Gaji**, `src/app/(main)/pengaturan/payroll/page.tsx:30`: `companies: <CompaniesPage bolehUbah={false} />`.
5b. **Field baru**: tambah ke tipe `Company`/`CompanyPayload` (`src/features/hris/payroll/types.ts`) dengan nama json persis dari PR BE (bip-erp#3185); baca PR-nya, jangan menebak nama field. Uji `company-options.test.ts` untuk penyaringan tidak beroperasi + pengecualian nilai tersimpan.
6. **i18n**: kunci baru (kalimat penunjuk, judul menu, keadaan tak berizin) di `src/i18n/locales/id.ts` **dan** `en.ts`.
7. **Panduan**:
   - Buat `src/features/panduan/isi/secretary.ts` (pola `isi/marketing.ts`): `SUMBER_SECRETARY` berisi satu catatan untuk `/secretary/badan-usaha`, ditulis dari teks layar, dua bahasa. Isinya: menambah/mengubah PT dan CV, satu default yang tak bisa dihapus, dan bahwa HR dan Finance memakai daftar ini. Plus `BELUM_DITULIS_SECRETARY: readonly string[] = []`.
   - Daftarkan satu baris `{ departemen: "secretary", ... }` di `ISI_PER_DEPARTEMEN` (`isi/index.ts`); `"secretary"` sudah kategori utama (`sidebar-kategori.ts`).
   - Periksa catatan `/pengaturan/payroll` di `isi/hrga.ts`; bila menyuruh HR menambah badan usaha, ubah jadi menunjuk Sekretariat.
8. **Verifikasi lokal**: `pnpm tsc --noEmit`, `pnpm lint`, `pnpm build`, `pnpm test` lewat antrean; bandingkan kegagalan dengan baseline yang terpasang, bukan dengan nol.
### Prasyarat

Sub-issue [BE] merged. Deploy SESUDAH [BE] ter-deploy di prod (kalau FE duluan, layar Sekretariat menerima 403).


## Issue 4: [BE] `bip-erp`: Kop surat diunggah Sekretariat, simpanan tetap di Finance (bagian 2/2)

- **Urutan**: 3, sesudah #3185 merged · **Issue**: [bip-erp#3202](https://github.com/bip-itteam-internal/bip-erp/issues/3202)

**Pemutus:** @wirkancil
**PIC:** @

Bagian 2/2 di sisi BE, sesudah bip-erp#3185 (bagian 1/2: izin `secretary.badanusaha.kelola`).

### Masalah

Kop surat badan usaha (`kop_url` di `akuntansi_cv_entitas`, 61 dari 62 terisi di prod 2026-10-15) hari ini diunggah Finance lewat `PATCH /akuntansi-cv/entitas/:kode` (izin `akuntansicv.kelola`, `services/finance/akuntansi_cv_handler.go`). Yang mendesain kop adalah orang Kesekretariatan, dan layar mereka bekerja per badan usaha (id `payroll_company`), bukan per kode entitas.

### Keputusan

ADR "ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca", butir 9. Layak `Siap Agent` sesudah ADR berstatus Diterima.

- Simpanan kop TETAP `akuntansi_cv_entitas.kop_url`; seluruh pembaca (`/internal/cv/kop`, `akuntansi_cv_pt_bharata.go`, `akuntansi_cv_pt_pemilik_rekening.go`, procurement) tidak berubah.
- Penulisnya pindah: rute finance baru dialamatkan dengan id badan usaha, dikunci `secretary.badanusaha.kelola`. Pemegang `akuntansicv.kelola` tidak lagi bisa mengubah `kop_url`.

### Yang harus benar

- [ ] `GET /akuntansi-cv/badan-usaha/:payrollCompanyId/kop` (izin `secretary.badanusaha.kelola`) membalas `{kode, kop_url}` entitas yang `payroll_company_id`-nya = id itu; badan usaha tanpa entitas tersambung membalas 404 dengan pesan "badan usaha belum tersambung ke entitas Finance".
- [ ] `PUT /akuntansi-cv/badan-usaha/:payrollCompanyId/kop` body `{kop_url}` (string kosong = hapus kop) menyimpan ke entitas tersambung, tercatat di jejak `akuntansi_cv_jejak` seperti perubahan kop lewat PATCH hari ini; tanpa entitas tersambung → 409 pesan yang sama.
- [ ] Kedua rute: tanpa izin → 403; pemegang `akuntansicv.kelola` saja → 403. Uji `app.Test(httptest.NewRequest(...))` dengan header `BIP-Permissions`.
- [ ] `PATCH /akuntansi-cv/entitas/:kode` dengan `kop_url` → 403 (atau 400) dengan pesan yang menunjuk Sekretariat › Badan Usaha; field PATCH lain tetap jalan. Uji membuktikan field lain masih tersimpan.
- [ ] `/internal/cv/kop` dan respons procurement yang memuat `kop_url` tidak berubah bentuk (uji yang ada tetap hijau).

### Di luar cakupan

- Memindah simpanan kop ke payroll.
- Menyambungkan 22 PT ke entitas (alur Sambungkan/Semai yang sudah ada, ADR 0182).
- Penandatangan (tetap Finance).

### Arah pengerjaan (dibaca dari `origin/main` 2026-10-15; ukur ulang bila basi)

1. Gerbang di finance: baca izin Sekretariat dengan `common.IzinSecretaryEfektif(c)` (pola `services/employee/secretary_gate.go:44`), bukan gerbang izin finance yang ada, yang hanya memuat izin modul finance.
2. Daftarkan rute di blok rute akuntansi CV (`akuntansi_cv_handler.go` ~baris 90-132); rute literal sebelum saudara ber-`:param`.
3. Cari entitas lewat `payroll_company_id` + `company_id` pemanggil (index unik parsial `uniq_company_payroll_cv`, `akuntansi_cv_handler.go:1092`).
4. Pakai ulang perekaman jejak yang dipakai PATCH untuk `kop_url` (`akuntansi_cv_handler.go:849`), jangan menulis jejak versi kedua.
5. Di `PATCH`, tolak `req.KopURL != nil` sebelum menulis apa pun.
6. Verifikasi: `go build ./...` dan `go test ./...` di `services/finance` lewat antrean.

### Data / bukti pendukung

PROD 2026-10-15: `akuntansi_cv_entitas` 62 baris, kop terisi 61; 40 CV tersambung ke `payroll_company`, 22 PT (PT00-PT21) belum.

### Prasyarat

bip-erp#3185 merged (izin `secretary.badanusaha.kelola` ada di katalog). ADR 0183 Diterima.

## Issue 5: [FE] `erp-frontend`: Unggah kop di Sekretariat, Entitas CV baca saja (bagian 2/2)

- **Urutan**: 4, deploy sesudah #3202 · **Issue**: [erp-frontend#2520](https://github.com/bip-itteam-internal/erp-frontend/issues/2520)

**Pemutus:** @wirkancil
**PIC:** @

Bagian 2/2 di sisi FE, sesudah erp-frontend#2498 (bagian 1/2: layar Sekretariat › Badan Usaha).

### Masalah

Unggah kop hari ini ada di dialog Ubah Entitas CV milik Finance (`src/features/finance/entitas-cv/components/dialog-ubah-entitas.tsx:99-131`, PDF dikonversi ke PNG di browser, lalu `PATCH kop_url` lewat `use-entitas-cv.ts:266-272`). Yang mendesain kop adalah orang Kesekretariatan.

### Keputusan

ADR "ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca", butir 9. Layak `Siap Agent` sesudah ADR berstatus Diterima.

- Unggah, ganti, dan hapus kop pindah ke form badan usaha di Sekretariat › Badan Usaha, memakai rute BE bagian 2/2.
- Dialog Ubah Entitas CV menampilkan kop baca saja dengan penunjuk ke Sekretariat.

### Yang harus benar

- [ ] Form badan usaha (layar Sekretariat) punya bagian "Kop surat": pratinjau kop sekarang, tombol unggah PDF (konversi PNG di browser, dipakai ulang dari Entitas CV, bukan disalin), dan hapus dengan konfirmasi `AlertDialog` yang menyebut nama badan usaha.
- [ ] Badan usaha yang belum tersambung ke entitas Finance menampilkan kalimat "Kop bisa diunggah setelah Finance menyambungkan badan usaha ini ke entitasnya", tanpa tombol unggah.
- [ ] Dialog Ubah Entitas CV tidak lagi punya tombol unggah/hapus kop; pratinjaunya tetap, dengan kalimat penunjuk ke Sekretariat › Badan Usaha.
- [ ] Teks baru lewat i18n `id.ts` dan `en.ts`; panduan `/secretary/badan-usaha` di `isi/secretary.ts` menyebut kop.
- [ ] `pnpm tsc --noEmit`, `pnpm lint`, `pnpm build` hijau; `pnpm test` tanpa kegagalan baru dibanding baseline yang terpasang.

### Di luar cakupan

- Penandatangan di Entitas CV.
- Mengubah cara kop dicetak di BKK.

### Arah pengerjaan (dibaca dari `origin/main` 2026-10-15; ukur ulang bila basi)

1. Angkat logika konversi PDF→PNG + unggah dari `dialog-ubah-entitas.tsx` ke fungsi/hook bersama di dalam folder fitur yang dipakai KEDUA layar (Entitas CV membaca saja, Sekretariat menulis), jangan menyalinnya.
2. Hook baru memanggil `GET/PUT /api/finance/akuntansi-cv/badan-usaha/:payrollCompanyId/kop` (nama rute persis dari PR BE bagian 2/2; baca PR-nya).
3. 404 dari GET = "belum tersambung", bukan galat merah.

### Data / bukti pendukung

Tidak perlu data prod.

### Prasyarat

Bagian 2/2 BE merged dan erp-frontend#2498 merged. Deploy sesudah BE bagian 2/2 ter-deploy.
