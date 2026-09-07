**Status**: ⚠️ Perbaikan CEPAT (Temuan 2) sudah dikerjakan & terverifikasi live prod (2026-09-02, `common.IsMarketingDepartmentStaff`, bip-erp branch `fix/shop-acl-marketing-only`). **Redesign PENUH (Rekomendasi §1) sudah DIKODEKAN 2026-09-05** — bip-erp branch `feat/acl-shops-department-source`, commit `f4d45777` (+ fix konvensi test `36c6e5eb`) — **tapi BELUM MERGE, BELUM DEPLOY, BELUM diverifikasi live**. Riset awal dilakukan 2026-09-02 sebagai kelanjutan investigasi Fase Contract [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]], setelah rencana "cabut menu Teams sepenuhnya" dibatalkan karena ditemukan fungsi ACL yang masih aktif.

**Keputusan lingkup eksplisit user (2026-09-05), sebelum implementasi**:
1. Redesign ini **hanya** ganti sumber data (§Rekomendasi 1) — gate rute `RequireIntegrationStaff` di `GET /transactions/master/shops` **tidak diubah**. SPV/leader marketing tanpa `system_roles.integration` tetap 403 di gerbang rute, tak pernah sempat kena/lolos filter `AllowedShops` sama sekali. Membuka gate itu (pola sama dengan perbaikan `/shops/status` 2026-09-04) sengaja **di luar lingkup** — dipakai puluhan halaman Integration, perlu pemetaan dampak sendiri.
2. Exemption `!IsIntegrationAdmin` (§Rekomendasi 2, opsi "balik logika") **dipertahankan apa adanya** — staf kyura/beauty_hacks yang JUGA `system_roles.integration` supervisor/admin (mis. Maftuhissaiin/Kyura, Aris Romadhoni/Beauty Hacks) **tetap bypass filter**, lihat semua toko. Tidak ada perubahan perilaku untuk populasi ini.

## Pertanyaan yang dijawab

Bisakah `team_shops`/`marketing_teams`/`team_members` dipensiunkan sekarang bahwa kepemilikan toko sudah pindah ke `department_shops`? **Belum** — ketiganya masih jadi sumber data untuk mekanisme ACL terpisah (`AllowedShops`, "siapa boleh lihat toko apa") yang dipakai puluhan halaman operasional. Dokumen ini menganalisa apakah dan bagaimana ACL itu bisa direplikasi dari `department_shops` + `work_data.department`, supaya Teams akhirnya bisa benar-benar dicabut.

## Mekanisme ACL saat ini

`transaction_handler.go` (integration-service), endpoint `GET /transactions/master/shops` (path benar setelah gateway membuang prefix `/api/integration` — bukan `/transactions/orders/master/shops` seperti draf awal dokumen ini, dikoreksi setelah verifikasi curl langsung 2026-09-02). Gerbang rute `RequireIntegrationStaff`.

**Kondisi SETELAH perbaikan cepat 2026-09-02** (sebelumnya tanpa `common.IsMarketingDepartmentStaff(c) &&`), **dan setelah redesign 2026-09-05 (branch `feat/acl-shops-department-source`, BELUM merge)**:

```go
if h.marketingTeamUseCase != nil && common.IsMarketingDepartmentStaff(c) && !common.IsIntegrationAdmin(c) && c.Query("scope") != "all" {
    department := c.Get(common.Header.Department)
    allowed, err := h.marketingTeamUseCase.AllowedShops(c.Context(), department)
    // ... filter shopList ke channel+shopID yang ada di `allowed`
}
```

`AllowedShops(department)` **(sejak 2026-09-05 — sebelumnya `AllowedShops(employeeID)`, lihat riwayat di bawah)**: baca seluruh `department_shops` (`DepartmentShopUseCase.ListSemua`), saring pakai `Sedepartemen(ds.Department, department)` — pola sama persis `department_shop_handler.go List()` non-IT. Departemen kosong/tak dikenal → `map[string][]string{}` kosong (fail-closed) → **shopList terfilter jadi kosong total**, bukan error; sama seperti semantik lama (employee tanpa keanggotaan tim), jadi bukan regresi.

**Riwayat sebelum redesign** (sampai commit sebelum `feat/acl-shops-department-source`): `AllowedShops(employeeID)` — `ListTeamIDsByEmployee` baca `team_members` (employee→team), lalu `ListShopsByTeamIDs` baca `team_shops` (team→shop). Kedua method repo ini **masih ada** di `MarketingTeamRepository` (dipakai fitur Teams CRUD lain), tapi TIDAK dipakai lagi oleh `AllowedShops`.

Dikonsumsi FE lewat `useFetchShops()` (`features/integration/transactions/hooks/use-fetch-shops.ts`), **tanpa parameter `scope`** — dipakai di puluhan halaman: Accurate (auto-sync, auto-sync-return, receipts, rekonsiliasi), payouts (Shopee/TikTok/Lazada), gross-profit, dashboard transaksi (`use-dashboard.ts`, `use-page.ts`), piutang TikTok, dan halaman Teams sendiri (assign shop). **Hanya satu** konsumen lain (`marketing-insight/customer-demography`) yang secara sadar mengirim `scope: "all"`, dengan komentar eksplisit menjelaskan kenapa ("insight agregat, bukan data operasional sensitif").

## Temuan 1 — data `team_shops`/`team_members` sudah selaras department_shops

Diukur langsung ke `integration_db` (2026-09-02), BUKAN keadaan 2026-08-11 yang dicatat ADR-0045:

- `team_members`: **24 baris** (bukan 1). Tim `aris` (SPV Beauty Hacks lama) sudah **soft-deleted**. Tim **BH** kini beranggota 23 orang — 22 di antaranya `work_data.department = "Beauty Hacks"` (posisi Account Specialist/Leader), 1 dari Kyura. Tim **GB-KY** — 1 anggota.
- `team_shops`: **54 baris hidup** (bukan 5).
- **Team BH → department_shops "Beauty Hacks": 32 dari 32 toko cocok, nol beda departemen.**
- **Team GB-KY → department_shops "Kyura": 22 dari 22 toko cocok.** Nama tim "GB-KY" (historis "gabungan brand") kini **secara de-facto** = departemen Kyura, satu-ke-satu.
- 6 toko `department_shops` Beauty Hacks **belum** masuk `team_shops` BH (termasuk `BEAUTYHACKS BHARATA`, baru dipetakan 2026-09-02) — lag dari proses assign manual yang terpisah dari `department_shops`.

**Kesimpulan**: seseorang (bukan bagian dari pekerjaan `department_shops`) sudah **memelihara Team BH/GB-KY secara manual** sampai nyaris identik dengan `department_shops`, kemungkinan besar justru untuk menutupi gejala Temuan 2 di bawah. Ini bukti kuat bahwa **migrasi ke `work_data.department` + `department_shops` sebagai sumber ACL aman dari sisi kecocokan data** — hasilnya nyaris sama dengan keadaan sekarang, dan otomatis menutup lag 6 toko itu.

## Temuan 2 — bug independen, staf non-marketing dapat daftar toko kosong (✅ diperbaiki 2026-09-02)

`IsIntegrationAdmin(c)` sebenarnya `checkRole("integration", RoleSupervisor, RoleAdmin)` — mencakup **supervisor**, bukan cuma admin murni (nama fungsinya menyesatkan, koreksi dari draf awal dokumen ini yang sempat menyimpulkan salah bahwa "supervisor juga kena filter"). `system_roles.integration = "admin"` sendiri tetap **0 akun di seluruh sistem** — tapi supervisor sudah cukup untuk exempt.

⚠️ **Angka "20 orang" di draf awal dokumen ini SALAH** — query awal tidak menyaring `is_active` maupun level supervisor/admin. Setelah dikoreksi (filter `is_active:true` DAN level `staff` murni, bukan supervisor/admin yang sudah exempt lewat `IsIntegrationAdmin`): **8 akun staf integration aktif**, bukan 26. Dari 8 itu:

- **2 aman** (anggota `team_members` Beauty Hacks): Ade Jaenul Farhi, Satrio Jatmiko.
- **5 kena bug murni** (bukan staf marketing sama sekali, salah sasaran filter): Rahadian Sigit Pranowo (Finance, AR Staff — **dikonfirmasi live** lewat curl langsung ke integration-service dengan identitas persis miliknya: respons `{"data":{}}` kosong sebelum fix), Nadya Atiqoh Hasan (Finance), Rizki Nurfian (Kesekretariatan), Seno Dwi Prakoso (HRD), Aminudin Teguh Wijayanto (Tech Development).
- **1 kasus berbeda** — Yudi Kurniawan (Beauty Hacks, **Marketplace Advertiser**): dia staf marketing sungguhan tapi TIDAK ikut ter-assign ke `team_members` saat seseorang dulu mengisi ulang keanggotaan Team BH manual (proses itu menyasar posisi Account Specialist, bukan Marketplace Advertiser). **Bukan bug filter** — perbaikan §Rekomendasi di bawah tidak menyentuh kasusnya, karena dia memang sasaran filter ini, cuma datanya belum lengkap. Konteks bisnis: posisi Marketplace Advertiser rencananya akan dipisah jadi kategori/tim tersendiri (belum ada tanggal); kartu "Langsung di bawah SPV" di ICC Management sengaja dipakai sebagai penampung sementara untuk melengkapi mapping toko dipegang siapa sebelum kategori itu resmi ada.
- (Arif Rahman Maliki, Pero Roberto Kristovic — sempat dicurigai, ternyata `is_active: false`, sudah resign, tidak relevan.)

2 dari 5 (Rahadian, dan secara desain seluruh staf non-marketing lain) mengalami ini karena mereka **memang sengaja** diberi `system_roles.integration` untuk pekerjaan mereka sendiri (Rahadian: memastikan angka sales benar — butuh lihat SEMUA toko lintas brand, bukan satu departemen), bukan salah pemberian role.

**Perbaikan** (bip-erp `fix/shop-acl-marketing-only`, `shared-library/common/roles.go`): tambah `common.IsMarketingDepartmentStaff(c)` — true hanya untuk pemegang role apa pun di `kyura`/`beauty_hacks` — sebagai syarat TAMBAHAN sebelum filter diterapkan. Staf non-marketing (Rahadian dkk) sekarang **tidak difilter sama sekali** (lihat semua toko), staf Beauty Hacks/Kyura (Ade, Satrio) **tidak berubah** perilakunya. Test unit `TestIsMarketingDepartmentStaff` (`roles_gate_test.go`) mengunci kontrol negatif: staf finance/hris/tech-development dengan `system_roles.integration` tetap `false`.

Ini **bukan efek dari pekerjaan `department_shops`** — gejala yang sudah ada sejak filter ACL ini dipasang (2026-06-29), independen dari ADR-0045. Ditemukan tak sengaja saat menelusuri kelayakan pencabutan Teams.

## Rekomendasi

### 1. Ganti sumber data, PERTAHANKAN semantik departemen — ✅ DIKODEKAN 2026-09-05

`AllowedShops(department)` baru: baca `BIP-Department` (header, dari `work_data.department`) alih-alih `team_members`, lalu cari `department_shops` yang departemennya cocok (kanonik — reuse `usecase.Sedepartemen`, fungsi murni yang sama dipakai penyempitan tulis `/icc/mappings` dan `/department-shops`). Tidak perlu koleksi `team_members`/`team_shops` sama sekali.

Diimplementasikan **persis seperti ini** di branch `feat/acl-shops-department-source` (commit `f4d45777`) — `services/integration/internal/usecase/marketing_team_usecase.go`. Sumber datanya `DepartmentShopUseCase.ListSemua` disuntik lewat tipe fungsi baru `DepartmentShopLister` (pola sama `ShopLister` di file yang sama), bukan meng-inject struct use-case penuh. `team_members`/`team_shops`/`ListTeamIDsByEmployee`/`ListShopsByTeamIDs` **tidak dihapus** — masih dipakai fitur Teams CRUD lain, cuma tak dipanggil lagi dari `AllowedShops`.

### 2. Perbaiki SIAPA yang kena filter — SUDAH TERTUTUP oleh perbaikan cepat 2026-09-02

Filter ACL ini secara desain dimaksudkan untuk **"marketing users only see their team's shops"** (komentar asli di kode) — bukan untuk semua pemegang `system_roles.integration`. Bagian "siapa yang kena filter" ternyata **sudah selesai** lewat perbaikan cepat Temuan 2 (`common.IsMarketingDepartmentStaff`) — pola akhirnya PERSIS alternatif "balik logika" yang disebut draf awal rekomendasi ini: hanya staf `kyura`/`beauty_hacks` yang kena, semua yang lain (termasuk staf integration murni seperti Rahadian) lihat semua. Redesign 2026-09-05 tidak perlu menyentuh bagian ini lagi.

⚠️ **Satu bagian TIDAK diadopsi, keputusan eksplisit user (2026-09-05)**: exemption `!common.IsIntegrationAdmin(c)` **dipertahankan**, bukan dihapus. Staf `kyura`/`beauty_hacks` yang JUGA `system_roles.integration` supervisor/admin (Maftuhissaiin/Kyura, Aris Romadhoni/Beauty Hacks — ditemukan lewat verifikasi live sesi ini) **tetap bypass filter**, lihat semua toko lintas departemen. Ini beda dari bunyi literal alternatif "balik logika" (yang tak menyebut exemption ini sama sekali) — dicatat di sini supaya tidak ada yang mengira ini terlewat.

### 3. Reuse, jangan duplikasi — reuse terjadi, TIDAK diangkat jadi helper baru

Pola kanonikalisasi departemen (`usecase.Sedepartemen`) dan penyempitan berbasis `BIP-Department` sudah ada dua kali di codebase ini (`/icc/mappings`, `/department-shops`) — implementasi 2026-09-05 jadi **pemakaian ketiga** (`AllowedShops` baca `ListSemua` + saring `Sedepartemen`, persis pola `department_shop_handler.go List()`). **Tidak diangkat jadi helper bersama baru** — bentuknya cuma dua baris (satu panggilan + satu filter), belum cukup kompleks untuk sepadan dengan abstraksi baru; menunggu pemakai keempat kalau pola ini terbukti perlu disatukan.

## Risiko & yang perlu diverifikasi sebelum implementasi

- ✅ **Selesai (2026-09-02)**: staf Finance terbukti mengalami dropdown kosong — dua cara sekaligus: (1) Rahadian login ulang (logout+login penuh, supaya JWT membawa klaim role terbaru) dan melihat sendiri `data: {}` di Network tab; (2) curl langsung ke integration-service (skip gateway publik, pakai `INTERNAL_GATEWAY_KEY` dari env container + header `BIP-Employee-ID`/`BIP-System-Roles` identik datanya) menghasilkan respons mentah yang sama. Teknik #2 dicatat di sini karena dipakai lagi: request GET biasa (baca-saja) tapi mengarang identitas orang lain untuk lewat autentikasi — dipakai HANYA setelah konfirmasi eksplisit, bukan cara baku.
- **Cek ulang cakupan department_shops** sebelum migrasi: departemen di luar Kyura/Beauty Hacks (kalau ada toko yang di-assign ke departemen lain di masa depan) harus tercakup aturan yang sama tanpa perlu kode tambahan — sudah otomatis benar kalau basisnya `department_shops` generik, bukan hardcode dua nama tim.
- **Urutan migrasi** — status per 2026-09-05: langkah **migrate** (alihkan `AllowedShops` sepenuhnya ke `department_shops`) sudah DIKODEKAN dan lolos unit test (`marketing_team_usecase_test.go`: staf marketing dapat toko departemennya, cross-departemen tak bocor, kanonikalisasi kapitalisasi/spasi, departemen tak dikenal fail-closed, galat lister diteruskan). Belum dikerjakan: **expand paralel** (dilewati — Temuan 1 sudah cukup membuktikan kecocokan data tanpa perlu jalur paralel runtime), **verifikasi live pasca-deploy** (staf Finance/IT/Kesekretariatan tetap lihat semua toko, staf Beauty Hacks/Kyura dapat toko departemennya — belum bisa dijalankan sebelum merge+deploy), dan **contract** (belum boleh dimulai sampai verifikasi live di atas selesai).
- **Test**: ✅ selesai — lihat di atas. **Tidak ada test Fiber penuh** untuk glue `transaction_handler.go` (satu baris ganti `employeeID`→`department`) — `TikTokShopUseCase` interface-nya besar (belasan method), fixture-nya tak sepadan untuk membuktikan satu baris. Risiko wiring ini ditutup verifikasi manual gateway pasca-deploy, bukan test otomatis.

## Di luar lingkup

**Sudah dikerjakan** (2026-09-05, lihat §Rekomendasi 1 & 2 di atas): ganti sumber `AllowedShops` ke `department_shops`; "siapa kena filter" sudah tertutup lewat perbaikan cepat 2026-09-02.

**Masih di luar lingkup**:
- **Membuka gate `RequireIntegrationStaff`** di `GET /transactions/master/shops` untuk SPV marketing tanpa role `integration` — keputusan eksplisit user 2026-09-05: blast radius puluhan halaman Integration, perlu pemetaan dampak sendiri sebelum diputuskan.
- **Menghapus exemption `!IsIntegrationAdmin`** — keputusan eksplisit user 2026-09-05: perilaku Maftuhissaiin/Aris Romadhoni sengaja tidak diubah.
- **Fase Contract**: mencabut `team_members`/`team_shops`/koleksi/menu `/integration/teams`/`ListTeamIDsByEmployee`/`ListShopsByTeamIDs` — baru aman setelah redesign di atas di-deploy DAN diverifikasi live beberapa waktu. Lihat [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] §Migrasi langkah 4.
- Kasus Yudi Kurniawan / posisi Marketplace Advertiser — di luar lingkup redesign ACL ini, menunggu keputusan bisnis pemisahan kategori tersendiri.

## Dokumen Terkait

- [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] — §Migrasi langkah 4 mencatat koreksi bahwa Teams tak bisa dicabut karena temuan ini
- [[Microservices - Integration Service]] — pemilik `department_shops`, `team_shops`, `marketing_teams`
- [[API - Integration Service]] — kontrak `/department-shops`, `/marketing/teams`
