**Status**: 🟡 Diputuskan 2026-09-17, **belum merge**: bip-erp branch `feat/employee-izin-akuntoko` (katalog, paket, registrasi) dan erp-frontend branch `feat/marketing-pekerjaan-saya` (induk menu dan gerbang). Jalur izin di gerbang baca komplain gudang menyusul di bip-erp branch `feat/warehouse-komplain-izin-akuntoko`.

## Context

Pemegang akun toko marketplace di divisi Beauty Hacks dan Kyura (posisi **Account Specialist**, dulu ICC, dan **Marketplace Advertiser**) bekerja di dalam toko: memantau performa, membaca ulasan, melaporkan masalah packing ke gudang, dan mengajukan boosting. Menu untuk pekerjaan itu sudah ada, tetapi tiga lapis gerbangnya tidak sejalan dengan siapa orangnya:

| Menu | Account Specialist (`insentive: icc`) | Marketplace Advertiser (`insentive: adv_marketplace`) |
|---|---|---|
| Performa Saya | terbuka | menu dan halaman tertutup (`bolehAkunSaya` tak mengenal `adv_marketplace`), padahal `GET /icc/mappings/me` sudah menyaring per karyawan |
| Ulasan | menu tak tampil (`bolehKomplain` tak memuat `insentive: icc`), padahal halaman dan `/reviews` tanpa gerbang peran | terbuka |
| Komplain ke Gudang | menu tak tampil, halaman terkunci cermin `bolehBacaKomplain`, padahal backend menerima pemegang toko | menu tampil, halaman terkunci, backend menerima bila memegang toko |
| Komplain ke QC | menu tak tampil, backend `RequireMarketingStaff` menolak | terbuka |

Sumber: `erp-frontend` `src/features/marketing-analytics/constants/izin.ts`, `src/features/warehouse/komplain/lib/akses-komplain.ts`; `bip-erp` `services/warehouse/komplain_akses.go`, `shared-library/common/roles.go`, `services/integration/main.go` (rute `/reviews`). Diukur di `origin/main` 2026-09-17, dan dibuktikan dengan menjalankan rantai sidebar per persona: Account Specialist tanpa peran lain hanya melihat `/icc/my-accounts` di kategori Marketing.

Fakta populasi yang menentukan (dikutip dari pengukuran bertanggal, ukur ulang sebelum dipakai): keempat puluh Account Specialist hanya berperan `insentive: icc` dan nol yang punya peran brand `kyura`/`beauty_hacks` (2026-09-16, komentar `komplain_akses.go`); tiga Marketplace Advertiser, dua di antaranya memegang toko Shopee ([[HRIS - Otomasi Skor KPI]], 2026-09-02).

Tiga cara membuka akses ditimbang:

| | A. Tambah peran ke daftar peran | B. Syarat "memegang toko" di semua gerbang | C. Izin yang ditugaskan per posisi (**dipilih**) |
|---|---|---|---|
| Inti | `insentive: icc` / `adv_marketplace` ditambahkan ke `bolehKomplain`, `bolehAkunSaya`, `marketingStaffChecks` | Menu dan gerbang menilai `icc_account_mappings` | HR memasang paket ke posisi lewat Hak per Posisi; gerbang lama tetap berlaku berdampingan |
| Kelemahan | `marketingStaffChecks` meloloskan pengajuan komplain gudang untuk toko MANA PUN, padahal pemegang toko sengaja dibatasi ke tokonya; salinan daftar peran di FE dan BE bertambah | sidebar butuh panggilan data tambahan tiap dimuat; Customer Support tak memegang toko per orang | butuh katalog backend, deploy, dan langkah manusia (HR memasang paket, karyawan login ulang) |

## Decision

**Alat kerja pemegang akun toko dibuka lewat izin modul `akuntoko` yang dipasang HR ke posisi, bukan lewat daftar peran, dan dikelompokkan di induk menu "Pekerjaan Saya".**

1. **Modul `akuntoko`, dua izin, satu paket.** `akuntoko.performa.view` (Performa Saya) dan `akuntoko.komplain.work` (Ulasan, Komplain ke Gudang), paket "Marketing: Pemegang Akun Toko" (key `marketing_akuntoko_pemegang`, `ReachAll`). Sumber: `shared-library/common/catalog_akuntoko.go`.
2. **Prefiks BUKAN `marketing`.** Klaim yang memuat satu izin `marketing.*` membuat frontend berhenti menilai fallback seluruh modul marketing (insiden paket Engagement 2026-09-09, lihat [[CORE - RBAC dan Permission Set]]). Nama modul juga tak boleh sama dengan kunci kategori sidebar.
3. **Pengganti, bukan tambahan.** Nilai izin menu cermin frontend diganti (`marketing.akun.view` → `akuntoko.performa.view`; Ulasan dan Komplain ke Gudang pindah ke `akuntoko.komplain.work`), dengan fallback yang sama persis (`bolehAkunSaya`, `bolehKomplain`). **Yang tak memegang paket tak berubah aksesnya.** Aman karena modul `marketing` tak pernah berkatalog di backend, jadi tak ada penugasan tersimpan yang memakai nama lama.
4. **Paket tidak dipecah.** Begitu klaim memuat satu izin `akuntoko.*`, fallback tier modul itu tak dinilai lagi; paket berisi satu izin akan mencabut izin akuntoko lainnya secara diam-diam.
5. **Komplain ke QC sengaja TIDAK ikut.** Register QC di employee-service belum menerima pemegang toko; gerbangnya milik T11 [[ADR - 0103 Satu Pintu Komplain Produk, Unit Tujuan Diturunkan dari Kategori]] dan diputuskan lewat kepemilikan toko. Menunya tetap `marketing.komplain.work` sampai itu mendarat.
6. **Cakupan data tetap kepemilikan toko**, bukan izin: Performa Saya dan Komplain ke Gudang hanya toko milik pembaca. Ulasan tetap menampilkan semua toko (konten publik marketplace) dengan tombol komplain hanya pada toko miliknya; penyaringan per brand di luar keputusan ini.
7. **Induk menurut HUBUNGAN, bukan modul asal.** Kategori Marketing: "Pekerjaan Saya" (Performa Saya, Ulasan, Komplain ke Gudang, Komplain ke QC, Engagement) dan "Kelola Tim" (ICC Management, Team Performance, Analisis Account Specialist) menggantikan induk "ICC". Rute tidak berubah.
8. **Pintu kategori.** Pemegang paket tanpa peran marketing wajib tetap mendapat kategori Marketing: `sidebar.tsx` mengoper hasil `bolehMenu` kedua izin ke `bolehLihatModulMarketing`, pola yang sama dengan `jadwal` dan `engagement`.
9. **Backend baca komplain gudang menerima izin itu** (menyusul, branch `feat/warehouse-komplain-izin-akuntoko`), supaya pemegang paket yang belum memegang toko mendapat daftar kosong, bukan 403. **HR tidak memasang paket di PROD sebelum itu naik** (keputusan review 2026-09-17).

## Consequences

**Yang membaik.** Account Specialist akhirnya melihat Ulasan dan Komplain ke Gudang atas toko yang ia pegang, dan Marketplace Advertiser melihat Performa Saya, tanpa satu pun daftar peran baru. Posisi berikutnya yang memegang toko cukup dipasangi paket, tanpa perubahan kode.

**Yang diterima sadar.**
- Aksesnya bergantung langkah manusia: HR memasang paket ke posisi, lalu karyawan login ulang (klaim dibentuk saat token terbit). Tanpa itu tak ada yang berubah bagi siapa pun.
- Komplain ke QC masih tertutup bagi Account Specialist sampai T11.
- Nama induk "Pekerjaan Saya" bentrok dengan tab Engagement `engagement.tabMine`; penggantian nama tab jadi task terpisah.
- Cermin frontend `bolehBacaKomplain` tetap tak mengenal kepemilikan toko: Account Specialist yang memegang toko tapi belum dipasangi paket masih melihat layar terkunci walau backend mau membalas. Paketlah yang menutup celah itu.

**Konsekuensi deploy.** Tanpa env baru dan tanpa kategori inbox baru. Urutan: employee-service (katalog + seed lewat `migrateMissingDefaultPermissionSets`), frontend, warehouse-service; baru kemudian HR memasang paket. Gateway tak perlu naik: klaim `permissions` diteruskan tanpa penyaring modul.

**Penjaga.** `catalog_akuntoko_test.go` (nilai izin literal, prefiks, paket tepat dua izin), `permission_catalogs_test.go` (registrasi dan seed), `sidebar-pekerjaan-saya.test.ts` (potret akses per persona dari `origin/main` sebagai test regresi, pintu kategori lewat pemindai sumber), `menu-permission-marketing.test.ts`, `akses-komplain-akuntoko.test.ts`.

## Terkait

[[CORE - RBAC dan Permission Set]] · [[APP - Web ERP]] · [[Sales - ICC Account Manager Mapping]] · [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]] · [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]] · [[ADR - 0103 Satu Pintu Komplain Produk, Unit Tujuan Diturunkan dari Kategori]] · [[HRIS - Otomasi Skor KPI]]
