**Status**: ✅ Diputuskan 2026-09-17, **merged, belum PROD**: bip-erp [#1963](https://github.com/bip-itteam-internal/bip-erp/pull/1963) (katalog, paket, registrasi) dan [#1964](https://github.com/bip-itteam-internal/bip-erp/pull/1964) (jalur izin di gerbang baca komplain gudang), erp-frontend [#1640](https://github.com/bip-itteam-internal/erp-frontend/pull/1640) (induk menu dan gerbang). DEV terukur lewat gateway 2026-09-17: modul `akuntoko` ada di `/master/permission-modules`, paket ter-seed dengan dua izinnya, dan akun uji tanpa peran gudang/marketing mendapat `GET /api/warehouse/wms/komplain` 403 tanpa paket, 200 `{"data":[]}` sesudah paket tingkat akun dipasang dan login ulang, lalu 403 lagi sesudah dicabut.

## Context

Pemegang akun toko marketplace di divisi Beauty Hacks dan Kyura (posisi **Account Specialist**, dulu ICC, dan **Marketplace Advertiser**) bekerja di dalam toko: memantau performa, membaca ulasan, melaporkan masalah packing ke gudang, dan mengajukan boosting. Menu untuk pekerjaan itu sudah ada, tetapi tiga lapis gerbangnya tidak sejalan dengan siapa orangnya:

| Menu | Account Specialist (`insentive: icc`) | Marketplace Advertiser (`insentive: adv_marketplace`) |
|---|---|---|
| Performa Saya | terbuka | menu dan halaman tertutup (`bolehAkunSaya` tak mengenal `adv_marketplace`), padahal `GET /icc/mappings/me` sudah menyaring per karyawan |
| Ulasan | menu tak tampil (`bolehKomplain` tak memuat `insentive: icc`), padahal halaman dan `/reviews` tanpa gerbang peran | terbuka |
| Komplain ke Gudang | menu tak tampil, halaman terkunci cermin `bolehBacaKomplain`, padahal backend menerima pemegang toko | menu tampil, halaman terkunci, backend menerima bila memegang toko |
| Komplain ke QC | menu tak tampil, backend `RequireMarketingStaff` menolak | terbuka |

*Baris terakhir sudah tidak berlaku sejak 2026-09-18; lihat keputusan 5.*

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
5. ~~**Komplain ke QC sengaja TIDAK ikut.**~~ **TERPENUHI 2026-09-18.** Register QC di employee-service belum menerima pemegang toko saat ADR ini ditulis, jadi menunya ditahan di `marketing.komplain.work` supaya tidak berakhir 403. Gerbang itu mendarat lewat keputusan 11 [[ADR - 0103 Satu Pintu Komplain Produk, Unit Tujuan Diturunkan dari Kategori]], jadi menunya pindah ke `akuntoko.komplain.work` bersama Ulasan dan Komplain ke Gudang.
   - **Membuka BACA saja.** Mengajukan komplain QC tetap diturunkan dari kepemilikan toko, bukan dari izin ini; asimetri itu disengaja dan alasannya ada di ADR 0103 keputusan 11c.
   - ⛔ **Cakupan barisnya BEDA dari dua menu lain**, dan ini yang perlu diketahui saat memasang paketnya: Ulasan dan Komplain ke Gudang menyempitkan baris ke toko yang dipegang, sehingga pemegang tanpa toko melihat nol baris, sedangkan Komplain ke QC hanya menyaring perusahaan. Rinciannya di [[CORE - RBAC dan Permission Set]].
   - Perpindahan ini tidak mencabut akses siapa pun yang tak memegang klaim `akuntoko.*`, sebab fallback kedua izin itu fungsi yang sama. Diukur PROD 2026-09-18: nol paket izin memuat `marketing.komplain.work`, dan nol paket `akuntoko` yang parsial.
6. **Cakupan data tetap kepemilikan toko**, bukan izin: Performa Saya dan Komplain ke Gudang hanya toko milik pembaca. Ulasan tetap menampilkan semua toko (konten publik marketplace) dengan tombol komplain hanya pada toko miliknya; penyaringan per brand di luar keputusan ini.
7. **Induk menurut HUBUNGAN, bukan modul asal.** Kategori Marketing: "Pekerjaan Saya" (Performa Saya, Ulasan, Komplain ke Gudang, Komplain ke QC, Engagement) dan "Kelola Tim" (ICC Management, Team Performance, Analisis Account Specialist) menggantikan induk "ICC". Rute tidak berubah.
8. **Pintu kategori.** Pemegang paket tanpa peran marketing wajib tetap mendapat kategori Marketing: `sidebar.tsx` mengoper hasil `bolehMenu` kedua izin ke `bolehLihatModulMarketing`, pola yang sama dengan `jadwal` dan `engagement`.
9. **Backend baca komplain gudang menerima izin itu** (bip-erp #1964, `gerbangBacaKomplain`), supaya pemegang paket yang belum memegang toko mendapat daftar kosong, bukan 403. **HR tidak memasang paket di PROD sebelum itu naik** (keputusan review 2026-09-17).

## Consequences

**Yang membaik.** Account Specialist akhirnya melihat Ulasan dan Komplain ke Gudang atas toko yang ia pegang, dan Marketplace Advertiser melihat Performa Saya, tanpa satu pun daftar peran baru. Posisi berikutnya yang memegang toko cukup dipasangi paket, tanpa perubahan kode.

**Yang diterima sadar.**
- Aksesnya bergantung langkah manusia: HR memasang paket ke posisi, lalu karyawan login ulang (klaim dibentuk saat token terbit). Tanpa itu tak ada yang berubah bagi siapa pun.
- Mencabut paket tidak langsung menutup rute baca yang sudah pernah dibuka: cache respons gateway (kunci `employee_id` + URL, tanpa melihat izin, TTL 3 menit, [[CORE - API Master Gateway]]) tetap menyajikan 200 lama untuk URL yang sama sampai kedaluwarsa. Terlihat saat verifikasi DEV; URL yang belum ter-cache langsung 403.
- ~~Komplain ke QC masih tertutup bagi Account Specialist sampai T11.~~ **Dibuka 2026-09-18** (keputusan 5 di atas); paket ini kini menggerbangi empat menu, bukan tiga.
- Nama induk "Pekerjaan Saya" bentrok dengan tab Engagement `engagement.tabMine`; penggantian nama tab jadi task terpisah.
- Cermin frontend tetap tak mengenal kepemilikan toko: Account Specialist yang memegang toko tapi belum dipasangi paket masih melihat layar terkunci walau backend mau membalas. Paketlah yang menutup celah itu. Sejak 2026-09-18 halaman Komplain ke QC ikut punya cermin (`bolehBacaKomplainQC`), jadi keterbatasan ini kini berlaku untuk dua halaman, bukan satu.
- ⛔ **Larangan memecah paketnya kini punya bukti perilaku, bukan sekadar konvensi.** `klaimMemuatModul` di `bolehMenu` membisukan fallback tier SELURUH modul begitu klaim memuat satu izin `akuntoko.*`, jadi permission set berisi `akuntoko.performa.view` saja akan MENCABUT Komplain ke QC dari orang yang sebelumnya melihatnya lewat peran. Layar Hak per Posisi mengizinkan IT mencentang izin satu per satu, jadi keadaan itu bisa dibuat. Diukur PROD 2026-09-18: nol paket parsial, jadi nol orang terdampak; dikunci test di `menu-permission-marketing.test.ts`.

**Konsekuensi deploy.** Tanpa env baru dan tanpa kategori inbox baru. Urutan: employee-service (katalog + seed lewat `migrateMissingDefaultPermissionSets`), frontend, warehouse-service; baru kemudian HR memasang paket. Gateway tak perlu naik: klaim `permissions` diteruskan tanpa penyaring modul.

**Penjaga.** `catalog_akuntoko_test.go` (nilai izin literal, prefiks, paket tepat dua izin), `permission_catalogs_test.go` (registrasi dan seed), `sidebar-pekerjaan-saya.test.ts` (potret akses per persona dari `origin/main` sebagai test regresi, pintu kategori lewat pemindai sumber), `menu-permission-marketing.test.ts`, `akses-komplain-akuntoko.test.ts`.

## Terkait

[[CORE - RBAC dan Permission Set]] · [[APP - Web ERP]] · [[Sales - ICC Account Manager Mapping]] · [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]] · [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]] · [[ADR - 0103 Satu Pintu Komplain Produk, Unit Tujuan Diturunkan dari Kategori]] · [[HRIS - Otomasi Skor KPI]]
