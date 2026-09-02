**Status**: 🟡 Analisa — belum ada kode. Riset dilakukan 2026-09-02 sebagai kelanjutan investigasi Fase Contract [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]], setelah rencana "cabut menu Teams sepenuhnya" dibatalkan karena ditemukan fungsi ACL yang masih aktif.

## Pertanyaan yang dijawab

Bisakah `team_shops`/`marketing_teams`/`team_members` dipensiunkan sekarang bahwa kepemilikan toko sudah pindah ke `department_shops`? **Belum** — ketiganya masih jadi sumber data untuk mekanisme ACL terpisah (`AllowedShops`, "siapa boleh lihat toko apa") yang dipakai puluhan halaman operasional. Dokumen ini menganalisa apakah dan bagaimana ACL itu bisa direplikasi dari `department_shops` + `work_data.department`, supaya Teams akhirnya bisa benar-benar dicabut.

## Mekanisme ACL saat ini

`transaction_handler.go` (integration-service), endpoint `GET /transactions/orders/master/shops` (gerbang rute `RequireIntegrationStaff`):

```go
if h.marketingTeamUseCase != nil && !common.IsIntegrationAdmin(c) && c.Query("scope") != "all" {
    employeeID := c.Get(common.Header.EmployeeID)
    allowed, err := h.marketingTeamUseCase.AllowedShops(c.Context(), employeeID)
    // ... filter shopList ke channel+shopID yang ada di `allowed`
}
```

`AllowedShops(employeeID)`: `ListTeamIDsByEmployee` baca `team_members` (employee→team), lalu `ListShopsByTeamIDs` baca `team_shops` (team→shop). Employee tanpa keanggotaan tim → `map[string][]string{}` kosong → **shopList terfilter jadi kosong total**, bukan error.

Dikonsumsi FE lewat `useFetchShops()` (`features/integration/transactions/hooks/use-fetch-shops.ts`), **tanpa parameter `scope`** — dipakai di puluhan halaman: Accurate (auto-sync, auto-sync-return, receipts, rekonsiliasi), payouts (Shopee/TikTok/Lazada), gross-profit, dashboard transaksi (`use-dashboard.ts`, `use-page.ts`), piutang TikTok, dan halaman Teams sendiri (assign shop). **Hanya satu** konsumen lain (`marketing-insight/customer-demography`) yang secara sadar mengirim `scope: "all"`, dengan komentar eksplisit menjelaskan kenapa ("insight agregat, bukan data operasional sensitif").

## Temuan 1 — data `team_shops`/`team_members` sudah selaras department_shops

Diukur langsung ke `integration_db` (2026-09-02), BUKAN keadaan 2026-08-11 yang dicatat ADR-0045:

- `team_members`: **24 baris** (bukan 1). Tim `aris` (SPV Beauty Hacks lama) sudah **soft-deleted**. Tim **BH** kini beranggota 23 orang — 22 di antaranya `work_data.department = "Beauty Hacks"` (posisi Account Specialist/Leader), 1 dari Kyura. Tim **GB-KY** — 1 anggota.
- `team_shops`: **54 baris hidup** (bukan 5).
- **Team BH → department_shops "Beauty Hacks": 32 dari 32 toko cocok, nol beda departemen.**
- **Team GB-KY → department_shops "Kyura": 22 dari 22 toko cocok.** Nama tim "GB-KY" (historis "gabungan brand") kini **secara de-facto** = departemen Kyura, satu-ke-satu.
- 6 toko `department_shops` Beauty Hacks **belum** masuk `team_shops` BH (termasuk `BEAUTYHACKS BHARATA`, baru dipetakan 2026-09-02) — lag dari proses assign manual yang terpisah dari `department_shops`.

**Kesimpulan**: seseorang (bukan bagian dari pekerjaan `department_shops`) sudah **memelihara Team BH/GB-KY secara manual** sampai nyaris identik dengan `department_shops`, kemungkinan besar justru untuk menutupi gejala Temuan 2 di bawah. Ini bukti kuat bahwa **migrasi ke `work_data.department` + `department_shops` sebagai sumber ACL aman dari sisi kecocokan data** — hasilnya nyaris sama dengan keadaan sekarang, dan otomatis menutup lag 6 toko itu.

## Temuan 2 — bug independen, staf non-marketing kemungkinan besar dapat daftar toko kosong

`system_roles.integration = "admin"` — **0 akun di seluruh sistem**. `IsIntegrationAdmin(c)` karena itu **selalu false**, untuk siapa pun. Filter ACL di atas SELALU aktif untuk setiap pemegang `system_roles.integration` (staff/supervisor), kecuali mereka kebetulan memanggil endpoint dengan `scope=all` — yang hanya dilakukan satu hook FE.

Diukur: 26 akun memegang `system_roles.integration` (staff/supervisor). Hanya **~6** benar-benar staf/leader/SPV marketing (Beauty Hacks/Kyura) yang tercakup keanggotaan tim di atas. **20 sisanya** tersebar di departemen yang tak ada hubungannya dengan tim manapun di `team_members`: Finance (7 — AR Staff, Senior Accountant, Finance Supervisor), Tech Development (8 — developer, IT Support), Kesekretariatan (3 — Corporate Secretary, Internal Audit, Direktur), HRD (1).

Staf Finance ini **memakai** halaman Accurate/piutang/payouts untuk rekonsiliasi keuangan lintas semua toko/brand — pekerjaan yang secara alami butuh melihat SEMUA toko, bukan satu departemen. Karena mereka tak terdaftar di `team_members`, dan hook `useFetchShops()` yang dipakai halaman-halaman itu tak pernah mengirim `scope=all`, **secara logika kode mereka mendapat dropdown/daftar toko KOSONG** di endpoint `master/shops` — bukan galat, senyap. Belum diverifikasi lewat sesi login sungguhan (butuh token staf Finance asli), tapi deduksinya langsung dari kode yang sudah dibaca lengkap.

Ini **bukan efek dari pekerjaan `department_shops`** — ini gejala yang sudah ada sejak filter ACL ini dipasang, independen dari ADR-0045.

## Rekomendasi

### 1. Ganti sumber data, PERTAHANKAN semantik departemen

`AllowedShops(employeeID)` baru: baca `BIP-Department` (header, dari `work_data.department`) alih-alih `team_members`, lalu cari `department_shops` yang departemennya cocok (kanonik — reuse `usecase.Sedepartemen`, fungsi murni yang sama dipakai penyempitan tulis `/icc/mappings` dan `/department-shops`). Tidak perlu koleksi `team_members`/`team_shops` sama sekali.

### 2. Perbaiki SIAPA yang kena filter — bukan sekadar ganti sumber datanya

Filter ACL ini secara desain dimaksudkan untuk **"marketing users only see their team's shops"** (komentar asli di kode) — bukan untuk semua pemegang `system_roles.integration`. Redesign yang benar sekaligus menutup Temuan 2:

- **Kena filter** (lihat toko departemennya sendiri saja): staf `kyura`/`beauty_hacks` tingkat manapun yang mengakses endpoint ini.
- **Dikecualikan** (lihat semua toko, seperti admin): `IsITMember`, staf/supervisor `finance`, `secretary`, `hris` — pola exemption yang sama sudah lazim di codebase ini (lihat `IsITMember` di `roles.go`, dipakai persis untuk kasus serupa: "yang merapikan data lintas tim").
- Alternatif yang lebih sederhana dan konsisten dengan prinsip *default aman*: **balik logikanya** — bukan "semua kena kecuali admin", tapi "hanya `kyura`/`beauty_hacks` yang kena, semua yang lain (termasuk staf integration murni) lihat semua". Ini juga otomatis menutup kelas kegagalan "role modul baru muncul, lupa dikecualikan".

### 3. Reuse, jangan duplikasi

Pola kanonikalisasi departemen (`usecase.Sedepartemen`) dan penyempitan berbasis `BIP-Department` sudah ada dua kali di codebase ini (`/icc/mappings`, `/department-shops`) — ini akan jadi pemakaian ketiga. Pertimbangkan mengangkatnya jadi helper bersama di titik ini (baru pemakai ketiga, sesuai ambang "jangan generalisasi sebelum ada tiga pemakai nyata" — lihat gotcha abstraksi prematur di catatan tim).

## Risiko & yang perlu diverifikasi sebelum implementasi

- **Verifikasi langsung** (bukan cuma deduksi kode) bahwa staf Finance benar-benar mengalami dropdown kosong hari ini — butuh sesi login staf Finance asli atau replikasi header identitas mereka lewat test `app.Test`.
- **Cek ulang cakupan department_shops** sebelum migrasi: departemen di luar Kyura/Beauty Hacks (kalau ada toko yang di-assign ke departemen lain di masa depan) harus tercakup aturan yang sama tanpa perlu kode tambahan — sudah otomatis benar kalau basisnya `department_shops` generik, bukan hardcode dua nama tim.
- **Urutan migrasi**: expand (tambah pembacaan `department_shops` sebagai jalur paralel, verifikasi hasilnya sama dengan `team_shops` untuk populasi Beauty Hacks/Kyura yang sudah dikonfirmasi cocok) → migrate (alihkan `AllowedShops` sepenuhnya) → verifikasi staf Finance/IT/Kesekretariatan benar-benar melihat semua toko pasca-perubahan → contract (baru di titik ini `team_shops`/`marketing_teams`/`team_members`/menu `/integration/teams`/`marketing_team_repo`+`handler`+route benar-benar aman dicabut).
- **Test**: `AllowedShops` versi baru perlu test unit (fungsi murni, tanpa Mongo) untuk kasus staf marketing (dapat toko departemennya), staf dikecualikan (dapat semua), dan departemen kosong/tak dikenal (fail-closed, bukan fail-open — konsisten dengan pola `Sedepartemen`/`DepartmentInScope` yang sudah ada).

## Di luar lingkup analisa ini

- Implementasi kode — ini murni riset per permintaan eksplisit, belum ada satu baris kode diubah.
- Perbaikan bug staf Finance secara terpisah dari redesign ini (bisa jadi quick-fix independen kalau urgent: exempt `finance` dari filter, tanpa menunggu migrasi department_shops penuh) — layak dipertimbangkan sebagai langkah cepat terpisah, disebut di sini supaya tidak hilang.

## Dokumen Terkait

- [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] — §Migrasi langkah 4 mencatat koreksi bahwa Teams tak bisa dicabut karena temuan ini
- [[Microservices - Integration Service]] — pemilik `department_shops`, `team_shops`, `marketing_teams`
- [[API - Integration Service]] — kontrak `/department-shops`, `/marketing/teams`
