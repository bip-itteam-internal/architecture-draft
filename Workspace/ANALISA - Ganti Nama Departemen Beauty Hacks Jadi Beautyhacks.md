## Deskripsi

*Blueprint (draf issue Siap Agent) untuk [[ADR - 0168 Departemen Beauty Hacks Diganti Nama Jadi Beautyhacks Bertahap, Kedua Nama Diterima selama Transisi]]. Cara kerjanya di [[REF - Peta Departemen]] § "Rename Beauty Hacks menjadi Beautyhacks (direncanakan)". Ini bukan rencana per berkas, karena itu tugas `/plan`.*

> ⛔ **Menunggu ADR "Departemen Beauty Hacks Diganti Nama Jadi Beautyhacks Bertahap, Kedua Nama Diterima selama Transisi" Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

- **Status**: 🟡 Belum dikerjakan (2026-10-10).
- **Tanggal**: 2026-10-10
- **Pemutus**: `irfanarfianto`
- **Ukuran**: **Besar**. Tiga repo harus berubah, dan `bip-erp` butuh tiga PR yang terpisah waktu (Expand, skrip Migrate, Contract). Alasannya: FE tidak merender nama ini secara generik di semua tempat. Ada kesamaan persis di `erp-frontend/src/features/hris/kpi/lib/departemen-marketing.ts:23`, `opex-manual/types.ts:71-74`, `marketing-analytics/hooks/use-anggaran-iklan.ts:26,64`, dan `components/layout/sidebar-kategori.ts:223`. Mobile juga mencocokkan persis di `mybharata-app/lib/src/core/utils/department_color_utils.dart:25,69`.
- **Pemicu**: ejaan brand resmi "Beautyhacks" (SOP perusahaan), dikonfirmasi pengguna 2026-10-10.

## Urutan

```
Induk (bip-erp)
├─ 1. [BE] bagian 1/3 Expand ─────────────┐ deploy dulu
├─ 3. [FE] (sesudah 1 ter-deploy)         │
├─ 4. [Mobile] (sesudah 1 ter-deploy)     │
├─ 2. [BE] bagian 2/3 skrip Migrate ──────┘ apply prod oleh manusia sesudah 1 ter-deploy
└─ 5. [BE] bagian 3/3 Contract (sesudah 2 apply + dry-run nol + token lama kedaluwarsa)
```

## Kueri ukur prod (baca saja, dijalankan manusia)

Dibutuhkan oleh issue 2 dan 5. Dijalankan dengan `mongosh --file` atas URI admin prod ([[IT - Server, VMs and Databases]] § MongoDB ERP Production). Skrip ini hanya membaca.

```js
// ukur-beauty-hacks.js — hitung dokumen bernilai "Beauty Hacks" per db/koleksi/field
const re = /^\s*beauty hacks\s*$/i;
const fields = ["department","departemen","team","divisi","name","entity_name",
  "requester_department","department_toko","department_name","departments",
  "departemen_tambahan","departemen_requester","work_data.department"];
const lewati = ["transaction_orders"]; // koleksi raksasa tanpa field departemen
db.adminCommand({listDatabases:1}).databases.map(d=>d.name)
  .filter(n=>!["admin","local","config"].includes(n)).forEach(dbn=>{
  const d = db.getSiblingDB(dbn);
  d.getCollectionNames().filter(c=>!lewati.includes(c)).forEach(c=>{
    fields.forEach(f=>{
      const n = d.getCollection(c).countDocuments({[f]: re});
      if (n>0) print(`${dbn}\t${c}\t${f}\t${n}`);
    });
  });
});
```

## Issue

### Induk: Ganti nama departemen Beauty Hacks jadi Beautyhacks

- **Repo**: `bip-erp` (tanpa PR sendiri, ditutup manual sesudah semua sub-issue merged)
- **Issue**: [bip-erp#2944](https://github.com/bip-itteam-internal/bip-erp/issues/2944)

**Pemutus:** @irfanarfianto
**PIC:** @

#### Masalah
Sistem menamai departemen `beauty_hacks` dengan "Beauty Hacks", sedangkan nama brand resmi di SOP perusahaan adalah "Beautyhacks". Rename lewat layar Master Data ditolak 409 (`services/employee/master_departemen_rute.go:280-292`), karena nama itu tersalin sebagai teks di sekitar 40 koleksi dan dicocokkan persis di BE, FE, dan mobile.

#### Keputusan
Ikuti ADR "Departemen Beauty Hacks Diganti Nama Jadi Beautyhacks Bertahap, Kedua Nama Diterima selama Transisi". Layak `Siap Agent` sesudah ADR itu berstatus Diterima.
Bentuknya: Expand (BE menerima dua nama) → Migrate (skrip data, dijalankan manusia) → Contract (buang nama lama). Key `beauty_hacks`, rute, nama Accurate, dan nama jabatan tetap.

#### Yang harus benar
- [ ] Kelima sub-issue merged dan ter-deploy prod sesuai urutan di ANALISA.
- [ ] Dry-run skrip Migrate di prod sesudah apply mencetak nol dokumen bernama "Beauty Hacks".
- [ ] Layar Master Data, filter departemen HRIS, KPI `/icc/kpi/beauty-hacks`, dan MyBharata menampilkan "Beautyhacks".

#### Di luar cakupan
Kunci stabil `department_key` (ADR 0045), nama departemen Accurate, nama toko, nama jabatan.

#### Data / bukti pendukung
Lihat sub-issue 2.

#### Prasyarat
ADR 0168 Diterima.

---

### 1. [BE] Ganti nama Beautyhacks bagian 1/3: backend menerima kedua nama (Expand)

- **Repo**: `bip-erp` · **Urutan**: pertama
- **Issue**: [bip-erp#2945](https://github.com/bip-itteam-internal/bip-erp/issues/2945)

**Pemutus:** @irfanarfianto
**PIC:** @

#### Masalah
Pembanding departemen di BE mencocokkan "Beauty Hacks" persis, atau dengan `ToLower(TrimSpace)` yang tetap membedakan spasi tengah. Kalau data diganti ke "Beautyhacks" tanpa persiapan, menu marketing, jadwal hostlive, kode PO, peta beban Accurate, dan akses supervisor patah tanpa error.

#### Keputusan
ADR "Departemen Beauty Hacks Diganti Nama Jadi Beautyhacks Bertahap, Kedua Nama Diterima selama Transisi" § Decision 2 (Expand). Layak `Siap Agent` sesudah ADR Diterima.
`DeptBeautyHacks` = "Beautyhacks", nama lama sebagai SATU konstanta transisi bernama. `deptKeyToNames["beauty_hacks"]` = `{"Beautyhacks","Beauty Hacks"}` (baru di urutan pertama).

#### Yang harus benar
- [ ] `shared-library/models/employee/master_data.go:20` `DeptBeautyHacks` = "Beautyhacks". Nama lama ada di satu konstanta transisi, tidak sebagai literal tersebar.
- [ ] `shared-library/common/roles.go:662`: `deptKeyToNames["beauty_hacks"]` memuat kedua nama, "Beautyhacks" di indeks 0. Test: `DepartmentNameFromKey("beauty_hacks")` = "Beautyhacks", dan `hasDepartmentAccess` lolos untuk kedua nama.
- [ ] `shared-library/common/departemen_marketing.go:23` `DepartemenMarketing` bernilai true untuk "Beautyhacks" dan "Beauty Hacks".
- [ ] `services/attendance/schedule_list.go:46`: kedua nama mendapat jadwal regular + hostlive.
- [ ] `shared-library/models/manufacture/models.go:651` `KodeDivisiMarketingPO`: kedua nama → "BHS".
- [ ] `services/integration/internal/usecase/beban_marketing.go:153` dan `beban_marketing_footage.go:53` memetakan proyek Accurate ke "Beautyhacks". Pembaca yang membandingkan hasilnya dengan `work_data.department` menerima kedua nama.
- [ ] `services/form-builder/culture_club_seed.json` memakai "Beautyhacks".
- [ ] Penjaga kontrak: test di shared-library gagal bila literal "Beauty Hacks" muncul di berkas Go non-test selain konstanta transisi dan komentar (pemindai sumber, dengan kontrol negatif).
- [ ] `go build ./...` dan test service tersentuh hijau. Test yang memakai literal lama diperbarui ke konstanta.

#### Di luar cakupan
Migrasi data (issue 2), FE, mobile, dan membuang nama lama (issue 5). Komentar kode boleh tetap menyebut nama lama.

#### Data / bukti pendukung
Daftar titik logika dan koleksi: ADR 0168 § Context. Belum butuh data prod.

#### Prasyarat
ADR 0168 Diterima. Deploy: semua service yang memakai `shared-library` dan disentuh (employee, attendance, integration, manufacture, form-builder, task-management, marketing-analytics, procurement), lewat skill `deploy-bip-erp`.

---

### 2. [BE] Ganti nama Beautyhacks bagian 2/3: skrip migrasi data

- **Repo**: `bip-erp` · **Urutan**: kedua (skrip boleh merged kapan saja, **apply prod sesudah issue 1 ter-deploy**)
- **Issue**: [bip-erp#2946](https://github.com/bip-itteam-internal/bip-erp/issues/2946)

**Pemutus:** @irfanarfianto
**PIC:** @

#### Masalah
Nama "Beauty Hacks" tersimpan sebagai teks di sekitar 40 koleksi lintas database, tanpa cascade. Rename Printing → Percetakan pernah setengah jalan karena koleksi terlewat ([[REF - Peta Departemen]]).

#### Keputusan
ADR "Departemen Beauty Hacks Diganti Nama Jadi Beautyhacks Bertahap, Kedua Nama Diterima selama Transisi" § Decision 2 (Migrate). Layak `Siap Agent` sesudah ADR Diterima **dan** hasil ukur prod ditempel di bawah.
Pola `scripts/hrga-perbaikan-peran/` (`jalankan.ps1` + `.js`): dump → dry-run → apply → rollback. Ganti nilai persis (trim, case-insensitive) "Beauty Hacks" → "Beautyhacks".

#### Yang harus benar
- [ ] Skrip di `scripts/ganti-nama-beautyhacks/` dengan mode `cek` (dry-run, cetak jumlah per db/koleksi/field), `terapkan`, dan `pulihkan`.
- [ ] `terapkan` menolak jalan tanpa `mongodump` koleksi tersentuh yang berhasil, dan menolak jalan bila `cek` belum dijalankan pada hari yang sama (gerbang berkas hasil cek).
- [ ] Mencakup seluruh pasangan koleksi/field yang ditemukan kueri ukur di ANALISA, termasuk `master_department.name`, `work_data.department`, `kpi_template.department`, `department_shops.department`, `icc_*.team`, field array (`departments[]`, `departemen_tambahan[]`).
- [ ] Mode `cek` menyapu SELURUH database dengan daftar field kandidat, dan mencetak juga pasangan yang tidak ada di daftar migrasi (supaya koleksi baru tidak terlewat senyap).
- [ ] Tidak menyentuh nilai yang hanya mengandung "Beauty Hacks" sebagai bagian teks lain (mis. nama toko, `MARKETING - BEAUTYHACKS`).
- [ ] Diuji di DEV: `cek` → `terapkan` → `cek` bernilai nol → `pulihkan` mengembalikan jumlah awal.
- [ ] README berisi perintah prod siap-tempel untuk manusia (skill `deploy-bip-erp` §0).

#### Di luar cakupan
Menjalankannya di prod (manusia). Perubahan kode aplikasi.

#### Data / bukti pendukung
**Perlu ukur prod:** jumlah dokumen per db/koleksi/field yang bernilai "Beauty Hacks". Kuerinya `ukur-beauty-hacks.js` di ANALISA § Kueri ukur prod. Tempel keluarannya di sini.

#### Prasyarat
ADR 0168 Diterima. Apply prod sesudah issue 1 ter-deploy di prod.

---

### 3. [FE] Ganti nama departemen Beautyhacks di erp-frontend

- **Repo**: `erp-frontend` · **Urutan**: sesudah issue 1 ter-deploy
- **Issue**: [erp-frontend#2290](https://github.com/bip-itteam-internal/erp-frontend/issues/2290)

**Pemutus:** @irfanarfianto
**PIC:** @

#### Masalah
FE mencocokkan "Beauty Hacks" persis di beberapa tempat. Kalau data berganti, halaman KPI Beautyhacks kosong, blok anggaran iklan tidak menemukan belanja, OPEX manual melempar staf ke "di luar kelompok", dan label WORKSPACE sidebar hilang. Semuanya tanpa error.

#### Keputusan
ADR "Departemen Beauty Hacks Diganti Nama Jadi Beautyhacks Bertahap, Kedua Nama Diterima selama Transisi" § Decision 3. Layak `Siap Agent` sesudah ADR Diterima.
Konstanta = "Beautyhacks". Pembanding menerima kedua nama sampai issue 5. Teks i18n menjadi "Beautyhacks".

#### Yang harus benar
- [ ] `src/features/hris/kpi/lib/departemen-marketing.ts:23` `DEPARTEMEN_BEAUTY_HACKS` = "Beautyhacks". `/icc/kpi/beauty-hacks` mengirim `?department=Beautyhacks`.
- [ ] `src/features/finance/opex-manual/types.ts:71-74`: key peta = "Beautyhacks" (nilai Accurate `MARKETING - BEAUTYHACKS` tetap). Filter PIC, pemegang laptop, dan breakdown per departemen menerima karyawan dengan `department` lama maupun baru.
- [ ] `src/features/marketing-analytics/hooks/use-anggaran-iklan.ts:26` memakai konstanta bersama (bukan literal lokal), dan perbandingan `divisi` di :64 menerima kedua nama.
- [ ] `src/components/layout/sidebar-kategori.ts:223`: "beautyhacks" dan "beauty hacks" sama-sama → `marketing`.
- [ ] 14 string i18n yang menyebut departemen (7 di `id.ts`, 7 di `en.ts`) menjadi "Beautyhacks".
- [ ] Test yang mematok konstanta diperbarui. Satu test per pembanding untuk kedua nama.
- [ ] `pnpm tsc --noEmit`, `pnpm lint`, `pnpm build` hijau. `pnpm test` tidak menambah kegagalan dibanding baseline `origin/main`.

#### Di luar cakupan
Rute `/icc/kpi/beauty-hacks`, nama jabatan, nama toko, membuang nama lama (issue 5).

#### Data / bukti pendukung
Titik-titik di atas dari `git grep origin/main` 2026-10-10.

#### Prasyarat
Deploy sesudah `bip-erp` issue 1 ter-deploy (BE harus menerima `?department=Beautyhacks` lebih dulu).

---

### 4. [Mobile] Warna departemen MyBharata mengenali Beautyhacks

- **Repo**: `my-bharata` (folder lokal `mybharata-app`, PR ke `dev`) · **Urutan**: sesudah issue 1 ter-deploy
- **Issue**: [my-bharata#202](https://github.com/bip-itteam-internal/my-bharata/issues/202)

**Pemutus:** @irfanarfianto
**PIC:** @

#### Masalah
`lib/src/core/utils/department_color_utils.dart:25,69` mengecek `contains('beauty hacks')`. Untuk "Beautyhacks", warna dan gradien jatuh ke abu-abu bawaan di halaman kehadiran tim, kartu informasi, dan konstanta task.

#### Keputusan
ADR "Departemen Beauty Hacks Diganti Nama Jadi Beautyhacks Bertahap, Kedua Nama Diterima selama Transisi" § Decision 3. Layak `Siap Agent` sesudah ADR Diterima.
Kedua nama mendapat warna dan gradien Beautyhacks yang sama.

#### Yang harus benar
- [ ] `getDepartmentColor` dan `getDepartmentGradient` mengembalikan warna Beautyhacks untuk "Beautyhacks", "beautyhacks", dan "Beauty Hacks".
- [ ] Unit test untuk ketiga ejaan, plus kontrol bahwa departemen tak dikenal tetap jatuh ke fallback.
- [ ] `flutter analyze` (berkas tersentuh) dan test tersentuh hijau.
- [ ] Ikut rilis store berikutnya dengan version name naik (bukan hanya versionCode).

#### Di luar cakupan
Teks UI lain (tidak ada yang menyebut nama departemen ini secara hardcode).

#### Data / bukti pendukung
Pemanggil: `team_attendance_page.dart`, `tenggo_promo_bottom_sheet.dart`, `information_card_header.dart`, `task_constants.dart`.

#### Prasyarat
Sesudah `bip-erp` issue 1 ter-deploy. Sesudah PR merged ke `dev`, issue ditutup manual (Closes tidak menutup di repo ini).

---

### 5. [BE] Ganti nama Beautyhacks bagian 3/3: buang nama lama (Contract)

- **Repo**: `bip-erp` · **Urutan**: terakhir
- **Issue**: [bip-erp#2947](https://github.com/bip-itteam-internal/bip-erp/issues/2947)

**Pemutus:** @irfanarfianto
**PIC:** @

#### Masalah
Sesudah Migrate, dua nama untuk satu departemen yang dipegang di Expand menjadi fakta ganda yang tidak lagi diperlukan.

#### Keputusan
ADR "Departemen Beauty Hacks Diganti Nama Jadi Beautyhacks Bertahap, Kedua Nama Diterima selama Transisi" § Decision 2 (Contract). Layak `Siap Agent` sesudah ADR Diterima **dan** syarat data di bawah terisi.
Hapus konstanta transisi dan nama lama dari `deptKeyToNames` dan pembanding. FE dan mobile ikut membuang penerimaan nama lama di PR masing-masing yang terpisah, bila tim memutuskan perlu.

#### Yang harus benar
- [ ] Konstanta transisi dan "Beauty Hacks" hilang dari `deptKeyToNames` dan seluruh pembanding yang ditambah di issue 1.
- [ ] Penjaga pemindai sumber dari issue 1 diperketat: nol literal "Beauty Hacks" di Go non-test selain komentar.
- [ ] `go build ./...` dan test tersentuh hijau.

#### Di luar cakupan
Dok vault, yang diperbarui lewat `/sync-docs` sesudah Migrate.

#### Data / bukti pendukung
**Perlu ukur prod:** keluaran mode `cek` skrip issue 2 di prod sesudah apply harus nol untuk semua pasangan. Tanggal apply juga perlu dicatat supaya bisa dibuktikan masa berlaku token terlama sudah lewat.

#### Prasyarat
`bip-erp` issue 2 sudah di-apply di prod. FE (issue 3) dan mobile (issue 4) sudah rilis.
