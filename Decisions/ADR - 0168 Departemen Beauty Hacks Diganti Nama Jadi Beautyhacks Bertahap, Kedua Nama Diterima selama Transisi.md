## Untuk Manajemen

**Yang berubah di layar.** Di semua layar ERP web dan MyBharata, nama departemen akan tertulis **Beautyhacks**, sama dengan nama brand di dokumen SOP perusahaan, menggantikan "Beauty Hacks". Ini berlaku untuk filter, kartu KPI, daftar karyawan, plafon kas, mapping toko, dan laporan.

**Siapa yang terdampak.** Seluruh staf dan supervisor Beautyhacks (sekitar 50 orang aktif), juga HR, Finance, dan Procurement yang menyaring atau menghitung per departemen. Selama pergantian, tidak boleh ada saat di mana staf kehilangan menu, KPI terbaca nol, atau insentif tidak terhitung. Karena itu pergantian dibuat bertahap: sistem dulu disiapkan untuk mengenali kedua nama, baru data diganti, lalu nama lama dibuang.

**Yang tidak dijanjikan.**
- Nama departemen di Accurate (`MARKETING - BEAUTYHACKS`) tidak diubah. Itu milik Accurate.
- Kode teknis modul (`beauty_hacks`) dan alamat halaman (`/icc/kpi/beauty-hacks`) tidak diubah. Keduanya tidak terlihat sebagai nama.
- Nama toko marketplace tidak disentuh.
- Rename departemen lain di masa depan tetap butuh pekerjaan sebesar ini. Perbaikan mendasarnya ("kunci stabil" di ADR 0045) di luar keputusan ini.

**Besaran kerja.** Besar: tiga aplikasi (backend, web, mobile), lima pekerjaan, satu migrasi data produksi yang dijalankan manusia, dan satu rilis MyBharata. Perkiraan 1 sampai 2 minggu kalender, termasuk jeda supaya sesi login lama habis sebelum nama lama dibuang.

## Deskripsi

*Departemen `beauty_hacks` diganti nama dari "Beauty Hacks" menjadi "Beautyhacks" lewat tiga fase expand → migrate → contract. Selama transisi, backend menerima kedua nama untuk departemen yang sama. Key modul, rute, dan nama departemen di Accurate tetap.*

- **Status**: 🟡 **Diusulkan**, 2026-10-10, kode belum ada. Blueprint: [[ANALISA - Ganti Nama Departemen Beauty Hacks Jadi Beautyhacks]]
- **Path di repo**: `bip-erp/shared-library/models/employee/master_data.go` · `bip-erp/shared-library/common/roles.go` · `bip-erp/shared-library/common/departemen_marketing.go` · `bip-erp/shared-library/models/manufacture/models.go` · `bip-erp/services/attendance/schedule_list.go` · `bip-erp/services/integration/internal/usecase/beban_marketing.go` · `bip-erp/services/integration/internal/usecase/beban_marketing_footage.go` · `bip-erp/services/form-builder/culture_club_seed.json` · `bip-erp/scripts/ganti-nama-beautyhacks/` (baru) · `erp-frontend/src/features/hris/kpi/lib/departemen-marketing.ts` · `erp-frontend/src/features/finance/opex-manual/types.ts` · `erp-frontend/src/features/marketing-analytics/hooks/use-anggaran-iklan.ts` · `erp-frontend/src/components/layout/sidebar-kategori.ts` · `erp-frontend/src/i18n/locales/{id,en}.ts` · `mybharata-app/lib/src/core/utils/department_color_utils.dart`
- **Tanggal**: 2026-10-10

## Context

Sistem menyimpan nama departemen ini sebagai "Beauty Hacks" (`shared-library/models/employee/master_data.go:20`, `DeptBeautyHacks`). Sementara itu dokumen SOP perusahaan memakai ejaan "Beautyhacks" (11 dok `Marketing - SOP Posisi * Beautyhacks`, disalin apa adanya dari "SOP BHARATA 2026"). Ejaan "Beautyhacks" dikonfirmasi pengguna (2026-10-10). Pemicunya ketepatan nama brand. Tidak ada gangguan operasional yang mendesak, jadi itu dicatat sebagai asumsi.

Mengganti nama ini tidak bisa dilakukan lewat layar Master Data, dan penolakannya disengaja:

1. **Nama departemen disimpan sebagai teks, tanpa cascade.** `PUT` master department menolak (409) perubahan nama yang mengubah kanon selama masih ada karyawan aktif dengan nama lama (`services/employee/master_departemen_rute.go:280-292`, `renameMemutus`). `KanonPosisi("Beauty Hacks")` = `beauty_hacks` sedangkan `KanonPosisi("Beautyhacks")` = `beautyhacks`, jadi perubahan ini termasuk yang ditolak.
2. **Pembanding nama tidak melumatkan spasi tengah.** Sebagian besar memakai `ToLower(TrimSpace)` atau `EqualFold`: `common.DepartemenMarketing` (`shared-library/common/departemen_marketing.go:22-23`), `deptKeyToNames` (`shared-library/common/roles.go:662`), `indeksDepartemen` (`services/employee/position_assign.go`). Yang memakai kesamaan persis: `scheduleListForDepartment` (`services/attendance/schedule_list.go:46`), `KodeDivisiMarketingPO` (`shared-library/models/manufacture/models.go:651`), dan peta proyek Accurate ke departemen (`services/integration/internal/usecase/beban_marketing.go:153`, `beban_marketing_footage.go:53`). Hanya segelintir yang kebal karena mencocokkan substring "beauty" (`services/employee/kpi_posisi_dikecualikan.go:44`; FE `isDepartemenMarketing`).
3. **Nama tersalin di sekitar 40 koleksi lintas service.** Antara lain `work_data.department`, `kpi_template.department`, `department_shops.department`, `icc_account_mappings.team`, `icc_leaders.team`, `icc_affiliate_accounts.team`, plafon dan unit kas (`divisi`, `departemen`), dokumen procurement, MPP (`department`), insentif (`departemen`, `entity_name`), jadwal siaran, engagement (`requester_department`), form-builder, calendar, payroll run, dan snapshot pengajuan attendance. Daftar lengkap beserta struct ada di blueprint.
4. **Klaim JWT membawa nama departemen** (`shared-library/common/struct.go`, field `department`, diteruskan sebagai header `BIP-Department`). Token yang terbit sebelum migrasi tetap membawa nama lama sampai kedaluwarsa atau diperbarui.
5. **Konsumen di FE dan mobile mencocokkan persis.** FE: `DEPARTEMEN_BEAUTY_HACKS` (`erp-frontend/src/features/hris/kpi/lib/departemen-marketing.ts:23`) dikirim sebagai `?department=` ke `/kpi`, `DEPARTEMEN_ACCURATE_PER_DIVISI` (`opex-manual/types.ts:71-74`), `BEAUTY_HACKS` (`marketing-analytics/hooks/use-anggaran-iklan.ts:26`), dan `sidebar-kategori.ts:223`. Mobile: `department_color_utils.dart:25,69` (`contains('beauty hacks')`). Kalau tidak cocok, warnanya jatuh ke abu-abu.

**Preseden dan yang sudah diputuskan.** [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] memutuskan `department_key` sebagai identitas dan nama hanya untuk tampilan. Tapi butir "Kunci stabil" di sana tercatat **belum dimulai**, dan konsekuensinya sudah ditulis di sana: "Mengganti nama departemen di HRIS harus diikuti pemeriksaan kesehatan". [[REF - Peta Departemen]] § "Selisih nama Printing dan Percetakan" mencatat rename yang setengah jalan: master dan `work_data` berganti, tapi `kpi_template`, konstanta kode, dan `deptKeyToNames` tidak. Hasilnya error 400 di pemilih jadwal dan template KPI yang tidak pernah terpakai. Keputusan ini dirancang supaya kelas kegagalan itu tidak terulang.

**Yang sudah ada dan dipakai ulang.** `deptKeyToNames` sudah berbentuk key → daftar nama, jadi bisa memuat dua nama. Ada pola skrip dump → dry-run → apply di `scripts/hrga-perbaikan-peran/`, dan mesin penggantian nilai lintas koleksi `shared-library/database/mongodb/idreplace/` (dibangun untuk ganti employee ID, desain scan-dan-update-nya bisa dipakai untuk nilai persis). Seeder `seedMasterDepartments` hanya mengisi koleksi yang kosong (`services/employee/master_data.go:232-238`), jadi dokumen yang sudah diganti nama tidak akan dibuat ulang sebagai "Beauty Hacks".

**Data produksi belum diukur.** Jumlah dokumen per koleksi yang berisi "Beauty Hacks" belum diukur. Kuerinya ada di blueprint, dan blueprint menahan issue migrasi sampai hasilnya ditempel.

## Decision

1. **Ejaan baru `Beautyhacks`** (satu kata, h kecil). Key modul `beauty_hacks`, rute FE `/icc/kpi/beauty-hacks`, nama departemen Accurate `MARKETING - BEAUTYHACKS`, nama jabatan (`BeautyHacks Supervisor` dan seterusnya), dan nama toko tidak diubah.
2. **Tiga fase, berurutan, masing-masing ter-deploy dan terverifikasi sebelum fase berikutnya:**
	- **Expand (BE).** `DeptBeautyHacks` menjadi "Beautyhacks". Nama lama dipertahankan sebagai konstanta transisi yang diberi nama jelas (bukan literal tersebar). `deptKeyToNames["beauty_hacks"]` = `{"Beautyhacks", "Beauty Hacks"}`, dengan nama baru di urutan pertama karena `DepartmentNameFromKey` mengembalikan `names[0]`. Setiap pembanding yang mencocokkan persis (daftar di Context §2) menerima kedua nama. Seed `master_data.go` dan `culture_club_seed.json` memakai nama baru. Sesudah fase ini, sistem berperilaku sama untuk data bernama lama maupun baru.
	- **Migrate (data, dijalankan manusia).** Satu skrip mengganti nilai persis "Beauty Hacks" (perbandingan sesudah trim, tanpa beda huruf besar/kecil) menjadi "Beautyhacks" di seluruh koleksi dan field yang tercantum di blueprint, termasuk `master_department.name`. Skrip wajib punya `mongodump` koleksi tersentuh lebih dulu, mode dry-run yang mencetak jumlah per koleksi, mode apply, dan rollback dari dump. Field yang berisi nama Accurate atau nama toko tidak disentuh.
	- **Contract (BE).** Nama lama dibuang dari `deptKeyToNames` dan pembanding, paling cepat **sesudah** dry-run ulang di prod menunjukkan nol dokumen bernama lama **dan** masa berlaku token terlama sudah lewat sejak migrasi (supaya header `BIP-Department` bernama lama tidak lagi beredar).
3. **FE dan mobile** mengganti konstanta dan pembanding ke nama baru sekaligus menerima nama lama, lalu ikut membuang nama lama setelah Contract. Teks i18n yang menyebut departemen (14 string di `id.ts` dan `en.ts`) diganti ke "Beautyhacks". FE dan mobile dideploy **sesudah** Expand. Urutan relatif terhadap Migrate bebas, karena keduanya menerima kedua nama.
4. **Dok vault yang menyebut nama departemen diperbarui sesudah Migrate selesai di prod**, lewat `/sync-docs`. Sebelum itu, nama yang hidup di prod tetap "Beauty Hacks", dan dok yang mendahului data berbohong ke arah sebaliknya.

## Consequences

- **Tidak ada jeda rusak.** Setiap fase aman dideploy sendiri. Rollback Migrate = pulihkan dump. Selama Expand masih aktif, data bernama lama tetap terbaca.
- **Satu fakta sempat hidup dua kali, dengan sengaja dan berbatas waktu.** Selama transisi, dua nama untuk satu departemen dipegang di satu tempat (`deptKeyToNames` dan konstanta transisi), bukan tersebar. Contract wajib dikerjakan: issue-nya dibuat sekarang supaya tidak terlupakan.
- **Kelemahan dasarnya tetap.** Pencocokan departemen lewat nama (ADR 0045 "Kunci stabil", belum dimulai) tidak diselesaikan di sini, jadi rename departemen berikutnya butuh pekerjaan sebesar ini lagi. Ini diterima sadar demi nama brand yang benar tanpa menunggu proyek kunci stabil.
- **Ada snapshot historis yang ikut berganti nama** (pengajuan lama, payroll run, catatan kepatuhan). Diterima: departemennya sama, hanya ejaannya yang dibetulkan. Kalau Finance atau HR butuh snapshot apa adanya untuk audit, field itu dikeluarkan dari daftar migrasi sebelum apply.
- **Rilis MyBharata** membawa perubahan warna departemen. Sebelum rilis, staf Beautyhacks melihat warna abu-abu bawaan di beberapa kartu. Tidak ada error.
- **Risiko utama: koleksi atau field yang terlewat.** Gejalanya senyap (200 dengan nol baris). Penjaganya ada dua: dry-run yang menyapu **seluruh** database lalu mencari nilai "Beauty Hacks" di field apa pun (bukan hanya daftar yang diketahui), dan dry-run ulang bernilai nol sebagai syarat Contract.

## Dokumen Terkait

- [[ANALISA - Ganti Nama Departemen Beauty Hacks Jadi Beautyhacks]]
- [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]]
- [[REF - Peta Departemen]]
- [[REF - Kepemilikan Data]]
- [[Microservices - Employee Service]]
