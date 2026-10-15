# ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca

> **Status**: 🟡 Diusulkan, 2026-10-15. Arahnya (satu pintu tambah/ubah badan usaha di Sekretariat, bukan HR) disetujui user dalam sesi `/analisa-kebutuhan` 2026-10-15. Merevisi sebagian [[ADR - 0182 Badan Usaha Satu Daftar untuk HR dan Finance, Entitas CV Menempel Tanpa Nama Sendiri]] (butir 4 dan 6: pintu tambah dan perapian nama). Pemutus: `wirkancil`. Blueprint: [[ANALISA - Badan Usaha Dikelola Sekretariat]].

## Untuk Manajemen

**Apa yang berubah.**
- **Badan usaha (PT Bharata, seluruh CV, seluruh PT lain) ditambah dan diubah oleh Kesekretariatan**, di menu baru Sekretariat › Badan Usaha. Isinya sama dengan yang hari ini diisi HR: nama resmi, NPWP, kota, bank, rekening, dan badan usaha default.
- **HR tidak lagi menambah atau mengubah badan usaha.** HR tetap melihat daftarnya dan tetap memilih badan usaha penggaji per karyawan di struktur gaji.
- **Finance tidak berubah.** Badan usaha baru dari Sekretariat muncul di Entitas CV sebagai "Badan usaha tanpa entitas", lalu Finance menekan Daftarkan untuk memberinya kode, singkatan BKK, rekening, pemegang, penandatangan, dan kop.
- **Data tetap satu daftar**, yang sama dengan yang dibaca slip gaji, payroll, dan Finance hari ini. Tidak ada pemindahan data.

**Siapa yang terdampak.** Corporate Secretary (pintu baru), HR (kehilangan hak tambah/ubah, tetap bisa melihat), Finance pengelola Entitas CV (tidak berubah).

**Apa yang TIDAK dijanjikan.**
- Tidak ada isian legal baru (akta, NIB, alamat lengkap, logo). Kop surat tetap diunggah Finance di Entitas CV.
- Tidak ada alur verifikasi atau persetujuan: yang disimpan Sekretariat langsung berlaku.
- Slip gaji yang sudah terbit tidak berubah.

**Perkiraan besaran kerja.** Dua PR berurutan: backend (izin baru dan gerbang tulis) lalu layar. Sesudah deploy, satu langkah manusia: memasang paket izin ke Corporate Secretary dan merapikan empat data yang sudah diketahui salah.

## Deskripsi

*Memindahkan pintu tulis daftar Badan Usaha (`payroll_company`) dari HR ke Kesekretariatan lewat izin baru `secretary.badanusaha.kelola`, tanpa memindahkan data: payroll-service tetap menyimpan dan menyajikannya, HR dan Finance membaca.*

- **Status**: 🟡 Diusulkan 2026-10-15
- **Path di repo** (rencana):
  - `bip-erp/shared-library/common/catalog_secretary.go` (izin dan paket baru)
  - `bip-erp/services/payroll/routes.go` (gerbang POST/PUT/DELETE `/companies` dan POST `/companies/impor`)
  - `bip-erp/services/finance/akuntansi_cv_daftar.go` (komentar "Daftar Badan Usaha milik HR")
  - `erp-frontend/src/app/(main)/secretary/badan-usaha/page.tsx` (baru)
  - `erp-frontend/src/features/hris/payroll/components/companies-page.tsx`, `src/components/layout/sidebar-menus.tsx`, `src/features/panduan/isi/` (baru untuk Sekretariat)
- **Tanggal**: 2026-10-15

## Context

Diukur 2026-10-15 ke bip-erp dan erp-frontend `origin/main` serta data PROD (baca saja).

1. **Satu daftar sudah ada; pintunya HR.** [[ADR - 0182 Badan Usaha Satu Daftar untuk HR dan Finance, Entitas CV Menempel Tanpa Nama Sendiri]] menjadikan `payroll_db.payroll_company` satu-satunya daftar badan usaha, dan kodenya merged hari ini (bip-erp#3178, erp-frontend#2493). Tulisnya digerbang `gate(common.PermPayrollManage, isHRAdmin)` di `services/payroll/routes.go` (POST `/companies/impor`, POST `/companies`, PUT dan DELETE `/companies/:id`); bacanya `gate(common.PermPayrollView, isHR)`. Layarnya tab Badan Usaha di Pengaturan Gaji (`/pengaturan/payroll?tab=companies`, `companies-page.tsx`), dan layar itu tak punya gerbang tulis sendiri (hanya `payroll.view`; `payroll.manage` ditegakkan backend saja).
2. **Pemegang legalitas badan usaha adalah Corporate Secretary** (jawaban user 2026-10-15). Di PROD satu orang (`BIP-0069-08-24`, Kesekretariatan); jabatan Legal satu orang (`BIP-0184-08-25`).
3. **Kesekretariatan belum punya izin untuk ini.** Katalog `secretary` (`shared-library/common/catalog_secretary.go:81-93`) hanya `secretary.legal.*` dan `secretary.rnd.*`, dipakai register perizinan, kontrak, dispute, dan R&D. `system_roles.secretary` sengaja tak dipetakan ke izin apa pun ([[CORE - RBAC dan Permission Set]]), dan Corporate Secretary menerima peran `secretary: supervisor` dari jabatannya, bukan `legal`.
4. **Rute layar.** Proxy FE menggerbang `/legal/*` dengan cookie peran `legal` (`src/proxy.ts:182-194`), yang tak dipegang Corporate Secretary; `/secretary/*` hanya digerbang untuk `/secretary/kpi`. Register Legal tak punya field badan usaha (`LegalLicense`, `LegalContract`), jadi tak ada register yang bisa dipakai ulang sebagai daftar badan usaha.
5. **Data hari ini** (PROD): `payroll_company` 62 baris (PT Bharata, 21 PT lain, 40 CV); `akuntansi_cv_entitas` 62 baris. Empat data yang diketahui salah: ejaan "PT. ZAVIRA KIARANA MANDIRI" (Finance: "Kirana"), NPWP sama `1000000010424024` di PT Citrana Abadi Perkasa dan PT Citravana Mandiri Sejahtera, NPWP PT Bharata kosong, nama PT Bharata tak lengkap. 21 baris tanpa data bank.
6. **PT dipakai untuk gaji** (menjawab TBD ADR 0182): dari 186 `employee_salary`, PT Bharata 32, PT Gentara Distribusi Indonesia 3, CV 89, tanpa `company_id` 62 (jatuh ke default).
7. **Slip aman terhadap perubahan master.** Identitas badan usaha disematkan ke tiap slip lewat `CompanySnapshot` saat run; slip web dan MyBharata (`PayslipCompanyModel`) membaca snapshot itu.

## Decision

1. **Pintu tambah dan ubah badan usaha = Kesekretariatan.** Izin baru `secretary.badanusaha.kelola` di katalog `secretary`, dengan paket sendiri (bukan bagian paket Legal atau R&D), dipasang ke jabatan Corporate Secretary. Area baru di samping `legal` dan `rnd`, mengikuti preseden tangga per area di modul ini.
2. **Gerbang tulis payroll-service berganti.** POST `/companies`, PUT dan DELETE `/companies/:id`, serta POST `/companies/impor` hanya untuk `secretary.badanusaha.kelola`. `payroll.manage` dan admin HR **tidak lagi** cukup. Gerbang baca `/companies` tetap (`payroll.view`) dan ditambah pemegang izin baru, supaya layar Sekretariat bisa memuat daftarnya.
3. **Data tidak pindah.** `payroll_company` tetap di payroll-service, termasuk `GET /internal/badan-usaha` yang dibaca Finance. Aturan yang sudah ada tetap: satu default, default tak bisa dihapus.
4. **Layar pindah ke menu Sekretariat**, rute `/secretary/badan-usaha` (bukan `/legal/*`, lihat Context 4), digerbang izin di halaman. Tab Badan Usaha di Pengaturan Gaji menjadi **baca saja** dengan keterangan bahwa perubahan dilakukan Kesekretariatan. Menu baru membawa panduannya.
5. **Finance tidak berubah.** Daftarkan dan Sambungkan di Entitas CV tetap seperti ADR 0182; nama entitas tetap mengikuti daftar ini.
6. **Perapian data pindah ke Kesekretariatan** (menggantikan ADR 0182 butir 6 yang menugaskannya ke HR): ejaan PT05, nama lengkap PT Bharata, NPWP PT Bharata, dan NPWP ganda Citrana/Citravana, dilakukan lewat layar baru sesudah deploy.

## Consequences

- Satu pintu: identitas badan usaha diubah oleh pemegang legalitasnya; HR dan Finance hanya membaca.
- HR tak bisa lagi membetulkan salah ketik badan usaha sendiri; perbaikan lewat Kesekretariatan. Ini disengaja.
- Corporate Secretary hanya satu orang di PROD. Tanpa pemasangan paket, tak seorang pun bisa menambah badan usaha sesudah deploy (gagal tertutup, bukan terbuka). Pemasangan paket adalah langkah manusia, tulis data PROD.
- Izin baru ada di `shared-library`, jadi service yang memakainya perlu di-rebuild; cache izin di gateway 3 menit. Urutan deploy: bip-erp (payroll-service dan service yang membaca katalog), lalu frontend.
- Selama BE sudah naik dan FE belum, tab Pengaturan Gaji masih menampilkan tombol simpan yang akan ditolak 403 bagi HR. Jedanya diterima karena singkat dan gagal tertutup.
- [[REF - Kepemilikan Data]], [[API - Payroll Service]], [[Microservices - Payroll Service]], [[Finance - Buku Besar CV]], [[CORE - RBAC dan Permission Set]], dan [[Unlisted - Kesekretariatan (Big Pictures)]] menyatakan pintu ini; disunting bersama ADR ini.

## Belum Diputuskan (TBD)

- **Isian legal tambahan** (akta, NIB, alamat lengkap). Ditambah bila ada dokumen yang mencetaknya; kop tetap di Entitas CV Finance.
- **Field bank di daftar ini**: identitas badan usaha atau rekening pembayar gaji (milik Finance/Accurate). Sampai diputuskan, tetap diisi di layar ini.

## Dokumen Terkait

- [[ADR - 0182 Badan Usaha Satu Daftar untuk HR dan Finance, Entitas CV Menempel Tanpa Nama Sendiri]] (direvisi sebagian)
- [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] · [[ADR - 0131 Tanda Tangan Direktur-Sekutu pada BKK Otomatis Tanpa Approval]]
- [[ANALISA - Badan Usaha Dikelola Sekretariat]] · [[Unlisted - Kesekretariatan (Big Pictures)]] · [[REF - Kepemilikan Data]] · [[Microservices - Payroll Service]] · [[CORE - RBAC dan Permission Set]]
