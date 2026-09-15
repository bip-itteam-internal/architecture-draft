## Untuk Manajemen

SPV dan Leader Beauty Hacks serta Kyura kini langsung melihat Ringkasan Marketing saat membuka dashboard, lengkap dengan belanja iklan, ROAS terhadap target, ROI laba, dan **anggaran iklan terpakai per brand untuk bulan berjalan**. Angka anggarannya diambil dari Master Anggaran OPEX yang sudah diisi Finance (akun Beban Iklan per departemen), bukan diketik ulang tim marketing. **Yang berubah di layar**: blok Efisiensi menampilkan per brand persen anggaran terpakai, belanja, anggaran, dan sisa; kartu ROAS vs target naik ke baris utama dengan rumusnya tertulis, dan ROI laba turun ke baris kedua. **Yang TIDAK dijanjikan**: anggaran per channel (Master Anggaran tidak berdimensi channel), proyeksi tanggal anggaran habis, dan penghapusan layar pagu lama milik marketing, yang tetap keputusan terpisah.

**Terdampak**: SPV dan Leader Beauty Hacks & Kyura (dashboard bawaan berganti; kartu Kehadiran dan Pengumuman di `/dashboard` tak lagi tampil untuk mereka), Cost Control Finance (anggaran yang mereka isi kini dibaca marketing), Direktur dan pembaca Ringkasan Marketing lain. **Besaran kerja**: kecil, frontend saja, tanpa perubahan backend.

## Deskripsi

*Anggaran iklan yang ditampilkan Ringkasan Marketing Analytics dibaca dari Master Anggaran OPEX Finance (integration-service, koleksi `anggaran_opex`, akun "Beban Iklan" per departemen Accurate) lewat HTTP, per brand dan per bulan berjalan WIB. `mart_pagu` milik marketing-analytics (pagu per channel+toko+bulan) tak lagi dibaca beranda tetapi belum dihapus; duplikasi fakta "anggaran belanja iklan" dicatat di [[REF - Kepemilikan Data]] sebagai belum diputuskan.*

- **Status**: ⚠️ **Diterima, terimplementasi di branch, belum merge** (dicatat 2026-09-15, ukur ulang sebelum dipakai): erp-frontend `feat/marketing-iklan-dashboard`. Tanpa perubahan backend, env, maupun kontrak.
- **Path di repo**:
  - `erp-frontend/src/features/marketing-analytics/components/anggaran-iklan.ts` (`susunAnggaranIklan`, `KeadaanBlokAnggaran`, `labelBulanBahasa`)
  - `erp-frontend/src/features/marketing-analytics/hooks/use-anggaran-iklan.ts`
  - `erp-frontend/src/features/finance/opex-manual/hooks/use-budget-kategori.ts` (`useBudgetPerDepartemen`) · `erp-frontend/src/features/finance/opex-manual/types.ts` (`DEPARTEMEN_ACCURATE_PER_DIVISI`)
  - `erp-frontend/src/features/marketing-analytics/components/{blok-efisiensi.tsx,deret-kpi.tsx,halaman-beranda.tsx}`
  - `erp-frontend/src/features/marketing-analytics/constants/kepemilikan.ts` (`isPemimpinBrand`) · `erp-frontend/src/features/erp/portal/lib/dashboard-posisi.ts`
- **Tanggal**: 2026-09-15

## Context

1. **Kebutuhan manajemen** (sheet requirement 2026-09-15, prioritas Tinggi): "Informasi iklan di dashboard utama (ROI, budget terpakai, ROAS)", status di sheet "Sebagian".
2. **Angka iklannya sudah ada, pembacanya tak mendarat di sana.** Ringkasan Marketing Analytics sudah memuat belanja iklan, ROAS, dan ROI, tetapi `dashboardUntukPosisi` (erp-frontend [#1252](https://github.com/bip-itteam-internal/erp-frontend/pull/1252)) hanya mengenal Direktur, HRGA, FAT, dan supervisor IT, jadi SPV/Leader brand mendarat di beranda portal.
3. **"Budget terpakai" hanya muncul saat satu channel dipilih, dan sumbernya kosong.** Beranda membaca `mart_pagu` (per `channel`+`shop_id`+`bulan`, `services/marketing-analytics/pagu.go:20`); keadaan bawaan halaman tanpa channel terpilih selalu berbunyi "pagu belum diisi". PROD 2026-09-15: `mart_pagu` 0 baris, dan halaman `/marketing-analytics/pagu` tak ada di sidebar.
4. **Anggaran iklan per brand per bulan sudah dikelola Finance.** Master Anggaran OPEX (`anggaran_opex`, `services/integration/internal/infrastructure/repository/anggaran_repo.go:19`; cara pengisiannya di [[Finance - Rancangan Finance Service]] §Cara Master Data Terisi) menyimpan akun "Beban Iklan" per departemen Accurate. PROD September 2026: `MARKETING - BEAUTYHACKS` Rp2.278.839.202 dan `MARKETING - KY + GB` Rp1.860.010.318, dibuat 13-14 September; Oktober sampai Desember baru punya baris seluruh perusahaan (`departemen` kosong).
5. **Pasangan brand ke departemen Accurate sudah dipakai Finance**, tetapi hanya tersirat dari urutan dua larik terpisah (`DEPARTEMEN_MARKETING`, `DEPARTEMEN_MARKETING_ACCURATE`). `MARKETING - KY + GB` dihitung 100% Kyura (keputusan produk 2026-08-25).
6. **Id `GET /divisi` adalah nama departemen** sejak [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] (`services/marketing-analytics/divisi.go`, `ID == Nama == Department`). PROD `department_shops` 2026-09-15: "Beauty Hacks" 41 toko, "Kyura" 22, tanpa ejaan lain.
7. **"ROI" berarti lebih dari satu hal**: KPI Leader menyebut ROAS terhadap target sebagai ROI (target 3,2, [[Sales - Dashboard per Posisi (Beauty Hacks & Kyura)]]), ambang `roas_min` modul ini (PROD `mart_ambang` 4,5 berlaku 2026-08-01), dan ROI laba di kartu (`hitungRoi` = laba ÷ belanja iklan × 100).

## Decision

### 1. Anggaran iklan dibaca dari Master Anggaran Finance, tak diketik ulang marketing

Blok Efisiensi Ringkasan Marketing membaca `GET /api/integration/accounting/anggaran` (`services/integration/main.go:1558`) untuk akun "Beban Iklan" bulan berjalan WIB. Nomor akunnya di-resolve dari `GET /api/integration/accounting/anggaran/katalog` lewat nama PERSIS, pemakai ketiga resolver yang sama dengan panel opex-manual Finance. marketing-analytics tidak menyimpan salinannya.

### 2. Per brand, tak pernah dijumlah

Satu baris per brand lewat satu peta, `DEPARTEMEN_ACCURATE_PER_DIVISI` ("Beauty Hacks" → `MARKETING - BEAUTYHACKS`, "Kyura" → `MARKETING - KY + GB`); kedua larik lama kini diturunkan darinya. Anggaran dua brand tidak dijumlahkan: tak seorang pun menetapkan anggaran gabungan, dan departemen lain (mis. `MARKETING - BAHAN PANGAN`) ikut beriklan tanpa divisi HRIS padanannya. Baris seluruh perusahaan tidak dibagi ke brand mana pun.

### 3. Pembandingnya belanja iklan divisi pada bulan yang sama

Belanja per brand = jumlah `ads_cost` dari `GET /api/marketing-analytics/profit/shops?bulan=YYYY-MM&divisi=<brand>` seluruh channel, bukan belanja rentang halaman: anggaran berdimensi bulan, sedangkan rentang bawaan halaman 30 hari melintasi dua bulan. Bulannya tertulis di judul blok dan mengikuti bahasa aktif. Brand di luar saringan divisi tak diminta belanjanya.

### 4. Tak satu keadaan pun jatuh ke 0%

Memuat (kerangka), terkunci (403: "hanya dapat dibaca tim Finance"), gagal (akun tak ditemukan di katalog dibedakan dari anggaran gagal dimuat), dan siap per brand: ada, anggaran nol ("tidak dianggarkan bulan ini"), belum ada (menyebut departemen Accurate yang dicari dan "diisi Cost Control"), divisi tanpa peta, serta saringan `belum_dipetakan` (satu kalimat, tanpa kartu brand). Belanja yang gagal dibaca, atau belum punya satu baris toko pun bulan itu, tampil "belum terbaca", bukan 0% terpakai.

### 5. `mart_pagu` tak dipakai beranda, belum dihapus

Lencana, keterangan, dan tautan pagu dicabut dari kartu Belanja iklan dan blok Efisiensi; baris tindakan pagu di daftar "Perlu tindakan" tak lagi terpicu. `GET/POST /pagu` dan halaman `/marketing-analytics/pagu` dibiarkan. Menghapus atau menggabungkannya ke Master Anggaran adalah keputusan lintas modul yang belum diambil.

### 6. ROAS vs target di baris utama, ROI laba di baris kedua, rumus tertulis

Kartu ROAS vs target naik ke lapis satu dengan rumus "omzet ÷ biaya iklan" dan lencana status terhadap target (tanpa lencana bila ROAS tak terhitung); kartu ROI laba turun ke lapis dua dengan rumus "laba ÷ biaya iklan", tanpa lencana ROAS. Nama "ROI" saja tak membedakan definisi di Context butir 7.

### 7. SPV/Leader brand mendarat di Ringkasan Marketing

`dashboardUntukPosisi` mendapat langkah kelima sesudah supervisor IT: `isPemimpinBrand` (SPV/admin `kyura` atau `beauty_hacks`, atau `insentive: adv_leader`) → Ringkasan Marketing. Sengaja bukan `isMarketingLeader` utuh, karena `integration: supervisor` ikut dipegang orang Finance, Kesekretariatan, Tech Development, dan akun sistem: PROD 2026-09-15, sembilan dari 17 pemegang `isMarketingLeader` lolos hanya lewat peran itu. Ini kontrol tampilan; aksesnya tetap `bolehAnalitik`.

## Consequences

### Yang membaik

- "Budget terpakai" terlihat tanpa memilih channel, dari angka yang benar-benar ditetapkan Finance.
- Anggaran iklan diketik di satu tempat oleh pemiliknya, Cost Control.
- SPV/Leader brand melihat angka iklan tanpa membuka menu, dan ketiga definisi "ROI" terbaca terpisah lewat rumusnya.

### Yang memburuk atau tetap terbuka

- ⚠️ **Dua tempat untuk "anggaran belanja iklan"** masih hidup, `anggaran_opex` dan `mart_pagu`; dicatat di [[REF - Kepemilikan Data]] §Duplikasi.
- ⚠️ **Dua sumber "belanja iklan aktual"**: panel opex-manual Finance dan `ads_cost` mart marketing bisa berbeda. Belum dicek silang dengan data sungguhan.
- **Departemen Accurate yang diganti nama** membuat brand terbaca "belum ada" tanpa galat; kalimatnya menyebut departemen yang dicari supaya sebabnya bisa dilacak.
- **Target ROAS di layar (4,5) tidak sama dengan "ROI" KPI Leader (3,2).** Menyamakannya keputusan pemilik KPI.
- **Endpoint Master Anggaran tanpa gerbang peran, baca maupun tulis**: grup `/accounting` dan rute `/anggaran*` didaftarkan tanpa middleware peran (`services/integration/main.go:1492`, `:1558-1564`). Pembaca marketing menerima baris Beban Iklan seluruh departemen bulan itu, dan blok menyaringnya di klien. Keadaan terkunci di blok bersifat defensif untuk bila kelak digerbang; celah tulisnya milik Finance dan tidak disentuh keputusan ini.
- **SPV/Leader BH & Kyura kehilangan kartu Kehadiran dan Pengumuman di `/dashboard`**, konsekuensi yang sama dengan posisi HRGA/FAT. Satu Leader BH di PROD belum memegang peran marketing apa pun, jadi tetap mendarat di beranda portal sampai perannya dibetulkan.
- **Hingga empat permintaan tambahan** tiap Ringkasan dibuka (katalog ber-cache, daftar anggaran, dua belanja divisi).
- Angka rupiah dan persen di blok tetap berformat id-ID di mode en (`format.ts`, dipakai belasan berkas).

### Yang sengaja tidak dilakukan

- **Anggaran per channel**: Master Anggaran tidak berdimensi channel.
- **Proyeksi tanggal anggaran habis**: butuh belanja per hari bulan berjalan, bukan jumlah bulanan.
- **Baris tindakan anggaran per brand** di "Perlu tindakan", **menyamakan target ROAS dengan KPI**, dan **memetakan `MARKETING - BAHAN PANGAN`**.
- **Lembar per posisi Leader dan Supervisor** menurut [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]: yang dipakai tetap Ringkasan per topik.

## Dokumen Terkait

- [[Microservices - Marketing Analytics Service]] · [[API - Marketing Analytics Service]] · [[Sales - Marketing Analytics (Audit Ketersediaan Data)]]
- [[Finance - Rancangan Finance Service]] (Master Anggaran OPEX) · [[REF - Kepemilikan Data]]
- [[APP - Web ERP]] (dashboard per posisi, Ringkasan Marketing) · [[Sales - Dashboard per Posisi (Beauty Hacks & Kyura)]]
- [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] · [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] · [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
