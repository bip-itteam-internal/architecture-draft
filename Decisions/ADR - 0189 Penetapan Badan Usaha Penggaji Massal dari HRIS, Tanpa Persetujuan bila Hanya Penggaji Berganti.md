# ADR - 0189 Penetapan Badan Usaha Penggaji Massal dari HRIS, Tanpa Persetujuan bila Hanya Penggaji Berganti

> **Status**: 🟢 Diterima, 2026-10-21, oleh irfanarfianto (Pemutus). Diusulkan 2026-10-20. Data PROD 2026-10-21 (bip-erp#3324): 62 `employee_salary` tanpa `company_id`, 5 versi menunggu persetujuan, 0 rencana; penerima notifikasi `payroll.approve.hrd` = 1 orang lewat paket JABATAN `HRD Supervisor` (bukan akun), jadi penerima di-resolve lewat paket jabatan. Bentuknya disetujui user dalam sesi `/analisa-kebutuhan` 2026-10-20 (desain layar di Figma, opsi endpoint massal di payroll-service). Merevisi sebagian [[ADR - 0148 Struktur Gaji Berversi per Event Personalia dan Diprorata per Hari]] (butir persetujuan). Pemutus: `irfanarfianto`. Blueprint: `Workspace/ANALISA - Penetapan Badan Usaha Massal dari HRIS.md`.

## Untuk Manajemen

**Apa yang berubah.**
- **Menu baru HRIS › Penetapan Badan Usaha.** HR melihat seluruh karyawan aktif beserta badan usaha (PT/CV) yang menggajinya, menyaring yang belum ditetapkan, memilih banyak karyawan sekaligus, lalu menekan **Tetapkan**. Tidak perlu lagi membuka struktur gaji satu per satu di menu Payroll.
- **Langsung berlaku pada tanggal yang dipilih HR** (bawaan awal bulan depan). Mengganti badan usaha penggaji **tidak lagi menunggu persetujuan** selama gaji, BPJS, dan PTKP-nya tidak ikut berubah.
- **SPV HRD menerima satu notifikasi per penetapan** (berapa karyawan, ke badan usaha mana, mulai kapan). Riwayat setiap perubahan tetap tercatat di riwayat struktur gaji karyawan.
- Karyawan yang belum punya struktur gaji tetap bisa ditetapkan; badan usahanya dipakai saat struktur gajinya dibuat.

**Siapa yang terdampak.** Staf HR pemegang izin tulis struktur gaji (pemakai halaman), SPV HRD (penerima notifikasi), dan karyawan yang slipnya berganti kop mulai periode yang dipilih.

**Apa yang TIDAK dijanjikan.**
- Perubahan gaji, BPJS, atau PTKP tetap lewat Struktur Gaji dan tetap menunggu persetujuan SPV HRD.
- Payroll run yang sudah berjalan dan slip yang sudah terbit tidak berubah.
- Kontrak kerja tidak disentuh dan tidak dibuat ulang: kontrak atas nama perusahaan (tenant), bukan atas nama badan usaha penggaji.
- Karyawan yang sedang punya perubahan gaji menunggu persetujuan tidak bisa ditetapkan dulu sampai perubahan itu diputus.

**Perkiraan besaran kerja.** Dua PR berurutan: backend payroll (daftar, penetapan massal, notifikasi) lalu layar web. Satu kategori notifikasi baru, sehingga dua service naik bersama saat deploy.

## Deskripsi

*Menambah pintu penetapan badan usaha penggaji (`company_id`) secara massal dari menu HRIS: satu endpoint di payroll-service yang, per karyawan, menerbitkan versi gaji salinan versi berlaku dengan `company_id` baru dan langsung `terjadwal`, atau menulis rencana badan usaha bila karyawan belum bergaji; ditambah daftar lintas badan usaha dan notifikasi per batch ke SPV HRD.*

- **Status**: 🟢 Diterima 2026-10-21, kode belum ada
- **Path di repo** (rencana):
  - `bip-erp/services/payroll/penetapan_badan_usaha.go` (baru): daftar lintas badan usaha + penetapan massal
  - `bip-erp/services/payroll/salary_version_service.go`, `models_salary_version.go`, `badan_usaha_rencana.go`, `notifikasi.go`, `routes.go`
  - `bip-erp/shared-library/...` daftar-izin `InboxCategories` (kategori baru)
  - `erp-frontend/src/app/(main)/hris/penetapan-badan-usaha/page.tsx` (baru), `src/features/hris/penetapan-badan-usaha/` (baru), `src/components/layout/sidebar-menus.tsx`, `src/utils/menu-permission.ts`, `src/features/panduan/isi/hrga.ts`, `src/i18n/locales/{id,en}.ts`
- **Tanggal**: 2026-10-20

## Context

Diukur 2026-10-20 ke bip-erp, erp-frontend, dan vault `origin/main`. Data PROD belum diukur di sesi ini (lihat Belum Diputuskan).

1. **`company_id` adalah satu field di dalam versi gaji.** `MasukanVersi` dan `versiDariMasukan` (`services/payroll/salary_version_service.go:131-146`) menyalin semua field apa adanya, sehingga versi yang hanya membawa `company_id` lahir dengan gaji pokok, komponen, dan dasar upah BPJS nol. Tidak ada helper "salin versi berlaku"; pola terdekat `rencanakanBarisImpor` (`salary_version_impor.go:275-313`) dan `masukanDariEmployeeSalary` (`models_salary_version.go:566-577`).
2. **Setiap versi baru menunggu persetujuan**: `baru.Status = StatusVersiMenunggu` (`salary_version_service.go:342`), disetujui lewat `POST /salary-versions/:id/setujui` bergerbang `payroll.approve.hrd` (`salary_version_handlers.go:165`), antreannya `GET /salary-versions/menunggu` (`:161`) yang dirender `AntreanVersiGaji` di halaman Payroll › Gaji Karyawan (erp-frontend `components/antrean-versi-gaji.tsx:38`). Preseden lewati persetujuan sudah ada: jalur Legacy menerbitkan versi `terjadwal` dengan `PersetujuanDilewati=true` saat kill-switch `PAYROLL_VERSI_GAJI_WAJIB_SETUJU` mati (`salary_version_service.go:343-349`).
3. **Rencana badan usaha** (`employee_badan_usaha_rencana`, `badan_usaha_rencana.go`) menampung penggaji karyawan yang belum bergaji; PUT per karyawan (`payroll.salary.write`), ditolak 409 bila karyawan sudah punya versi (`:182-184`), dipakai sekali oleh `buatVersiGaji` lalu dihapus (`salary_version_service.go:236-250`).
4. **Belum ada pintu massal maupun daftar lintas badan usaha.** Yang ada: `GET /companies/:id/karyawan` per satu badan usaha (`karyawan_badan_usaha.go`, menggabungkan gaji berlaku, rencana, dan `belum_diplot` untuk default), `POST /employee-salary/bulk-bpjs-base` (pola hasil per baris `{diperbarui, tanpa_ubah, gagal[]}`, batas 1000, `bulk_bpjs_base.go:27,43-60`), dan impor versi berbasis berkas tanpa kolom `company_id` (`salary_version_impor.go:56-63`). Hulu `keputusan_massal` sudah sah di model tetapi belum dipakai siapa pun (`models_salary_version.go:53`).
5. **Penetapan hari ini per orang, di menu Payroll**: `EmployeeSalaryForm` di Sheet halaman Gaji Karyawan (erp-frontend `salary-register-page.tsx:438`), plus pemilih rencana di Buat Karyawan (`create-employee/pilih-badan-usaha.tsx`). Menurut ADR 0183 Context 6, 62 dari 186 `employee_salary` tidak ber-`company_id` dan jatuh ke badan usaha default.
6. **Tidak ada notifikasi versi gaji.** Kategori inbox payroll hanya untuk run (`notifikasi.go:39-51`).
7. **Aturan bisnis.** `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` tidak mengatur badan usaha penggaji. Kontrak kerja memakai `company_id` tenant ([[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]]); kontrak baru hanya dituntut untuk mutasi antar-tenant ([[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]).
8. ⚠️ **Berdiri di atas ADR berstatus 🟡.** [[ADR - 0148 Struktur Gaji Berversi per Event Personalia dan Diprorata per Hari]], [[ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca]], dan [[ADR - 0129 Persetujuan Payroll Run Bertingkat dan Dibayar per Badan Usaha sebelum Terbit]] masih Diusulkan walau kode versi gaji dan pintu Sekretariat sudah berjalan. [[ADR - 0181 Portal Persetujuan Memuat Keputusan dan Tindakan Operasional]] Diterima.

## Decision

1. **Halaman baru HRIS › Penetapan Badan Usaha**, di luar menu Payroll, hanya untuk pemegang `payroll.salary.write` (izin yang sama dengan menulis struktur gaji dan rencana hari ini). Daftar karyawan **aktif** dengan kolom badan usaha penggaji, status (Ditetapkan, Rencana, Belum ditetapkan), dan ada-tidaknya struktur gaji; bawaan tersaring "Belum ditetapkan"; pilih-banyak lewat pilihan baris `MainTable`.
2. **Satu endpoint penetapan massal di payroll-service**, mode `cek` dan `terapkan`, menerima `{company_id, effective_date, employee_ids[]}`. Per karyawan:
   - **punya versi berlaku**: menerbitkan versi baru yang isinya **salinan versi berlaku** dengan `company_id` diganti, lewat `buatVersiGaji` (validasi yang sama, termasuk penolakan badan usaha tidak beroperasi);
   - **belum punya versi**: menulis rencana badan usaha.
   Satu batch memakai hulu `keputusan_massal` dengan pengenal batch, sehingga seluruh versinya bisa ditelusuri ke satu penetapan. Hasilnya per baris (diterapkan, tanpa ubah, gagal + alasan), mengikuti pola bulk BPJS; batas jumlah per panggilan sama dengan bulk BPJS.
3. **Tanpa persetujuan bila hanya penggaji berganti** (keputusan user 2026-10-20, merevisi ADR 0148 butir persetujuan untuk kasus ini saja). Versi dari endpoint ini lahir `terjadwal` dengan `PersetujuanDilewati=true` lalu menjadi `berlaku` lewat rekonsiliasi yang sudah ada. Pengecualian ini **hanya** untuk versi yang berbeda dari versi berlakunya di `company_id` saja; endpoint tidak menerima field gaji lain. Versi lain tetap menunggu persetujuan SPV HRD.
4. **Pengaman**: jejak di riwayat versi tiap karyawan (hulu `keputusan_massal`, pengisi, waktu) dan **satu notifikasi inbox per batch ke pemegang `payroll.approve.hrd`** berisi jumlah karyawan, badan usaha tujuan, dan tanggal berlaku. Kategori inbox baru di daftar-izin `InboxCategories`.
5. **Tanggal berlaku diisi HR**, bawaan tanggal 1 bulan berikutnya. Versi yang sudah dipakai payroll run di atas draft tidak berubah (ADR 0148 butir versi lewat); slip terbit tidak berubah (`CompanySnapshot`).
6. **Penolakan per baris yang wajib terbaca**:
   - karyawan yang punya versi **menunggu persetujuan** ditolak (menyalin dari versi yang belum disetujui akan ikut mengesahkan isinya);
   - badan usaha sama dengan yang sudah berlaku pada tanggal itu dihitung **tanpa ubah**, bukan versi baru (`kontenGajiSama` sudah membandingkan `CompanyID`, `models_salary_version.go:583`);
   - badan usaha tidak beroperasi ditolak di tingkat batch sebelum baris mana pun diproses.
7. **Daftar lintas badan usaha** di payroll-service memakai sumber yang sama dengan `GET /companies/:id/karyawan` (gaji berlaku, rencana, identitas, resign), tidak menyalin aturan gabungnya ke tempat kedua; badan usaha default ditampilkan sebagai "Default: <nama>" untuk karyawan yang belum ditetapkan.
8. **Kontrak tidak disentuh** (keputusan user 2026-10-20): mengganti badan usaha penggaji di dalam satu tenant tidak menuntut kontrak baru.
9. **Penetapan per karyawan di Struktur Gaji tetap ada** dan tetap lewat persetujuan, karena di sana field gaji lain ikut bisa diubah. Halaman baru menjadi pintu utama penetapan badan usaha; form struktur gaji tidak dihapus.

## Consequences

- HR bisa membereskan karyawan yang belum ditetapkan dalam satu langkah, dan karyawan baru ditetapkan tanpa menunggu struktur gajinya disetujui.
- Satu orang dengan `payroll.salary.write` bisa mengganti penggaji banyak karyawan tanpa mata kedua sebelum berlaku. Ini disengaja; pengamannya notifikasi ke SPV HRD dan riwayat versi. Salah tetap bisa dibetulkan dengan penetapan berikutnya selama run periode itu belum di atas draft.
- Prinsip "pengisi bukan penyetuju" di ADR 0148 punya pengecualian bernama. Penanda `PersetujuanDilewati` kini dipakai dua jalur (Legacy dan penetapan massal), jadi pembacanya tak boleh menganggapnya selalu berarti Legacy.
- Kategori inbox baru: payroll-service dan notification-service naik **bersama**, lalu satu notifikasi sungguhan dipicu sebagai bukti ([[RUN - Deploy Microservices bip-erp]] §3a). Kontrak baru: deploy BE sebelum FE.
- Menu HRIS baru wajib membawa panduannya, atau tercatat di `BELUM_DITULIS_HRGA`.
- [[ADR - 0148 Struktur Gaji Berversi per Event Personalia dan Diprorata per Hari]], [[Microservices - Payroll Service]], [[HRIS - Payroll]], dan [[REF - Kepemilikan Data]] menyatakan pengecualian dan pintu ini; disunting bersama ADR ini.

## Belum Diputuskan (TBD)

- **Data PROD belum diukur di sesi ini**: jumlah karyawan aktif tanpa `company_id` dan tanpa rencana hari ini, jumlah versi `menunggu_persetujuan` (yang akan ditolak per baris), dan jumlah pemegang `payroll.approve.hrd` (penerima notifikasi). Kuerinya di blueprint.
- **Alasan pemindahan dari menu Payroll** belum dinyatakan pemilik kebutuhan; asumsi yang dipakai: penetapan massal tanpa membuka struktur gaji per orang.

## Dokumen Terkait

- [[ADR - 0148 Struktur Gaji Berversi per Event Personalia dan Diprorata per Hari]] (direvisi sebagian: butir persetujuan)
- [[ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca]] · [[ADR - 0182 Badan Usaha Satu Daftar untuk HR dan Finance, Entitas CV Menempel Tanpa Nama Sendiri]] · [[ADR - 0129 Persetujuan Payroll Run Bertingkat dan Dibayar per Badan Usaha sebelum Terbit]] · [[ADR - 0181 Portal Persetujuan Memuat Keputusan dan Tindakan Operasional]] · [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]
- [[HRIS - Payroll]] · [[Microservices - Payroll Service]] · [[REF - Kepemilikan Data]] · [[RUN - Deploy Microservices bip-erp]]
