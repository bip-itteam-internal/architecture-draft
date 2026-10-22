# ADR - 0197 Badan Usaha Pemilik Toko Diisi Marketing saat Klaim Kepemilikan Toko

> **Status**: 🟡 **Diusulkan**, 2026-10-22, oleh `/analisa-kebutuhan`. Bentuk A disetujui user dalam sesi yang sama; berlaku setelah Pemutus menulis baris Diterima, dan karena menyentuh lingkup [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] (T8), SPV FAT ikut diminta menyetujui. Pemutus: `irfanarfianto`. Blueprint: `Workspace/ANALISA - Badan Usaha Pemilik Toko dari Marketing.md`.

## Untuk Manajemen

**Apa yang berubah.**
- Saat leader/SPV Marketing mengklaim toko ke departemennya (ICC Management, tab Kepemilikan Toko), mereka juga memilih **badan usaha (CV/PT) atas nama siapa toko itu dibuka**. Marketing yang membuka toko, jadi merekalah yang tahu jawabannya.
- Satu CV/PT boleh memiliki banyak toko; satu toko hanya atas nama satu CV/PT.
- Di Sekretariat, sheet detail Badan Usaha tab **Toko** menampilkan seluruh toko milik badan usaha itu dari pilihan Marketing, bukan lagi tebakan dari nomor rekening (yang hari ini tidak pernah cocok).
- Toko yang belum dipilihkan badan usahanya terlihat jumlahnya, baik di layar Marketing maupun di sheet Sekretariat.

**Siapa yang terdampak.** Leader/SPV Marketing (mengisi, sekali per toko, 69 toko hari ini), Sekretariat (membaca), Finance (memakai data ini nanti untuk penjualan per CV).

**Apa yang TIDAK dijanjikan.**
- Tidak ada pemasangan otomatis: dicoba lewat nama, hasilnya 0 dari 69 toko (nama toko adalah nama merek, bukan nama CV).
- Jurnal penjualan per CV, penarikan saldo per CV, dan laporan pajak per CV **tidak** termasuk; itu tetap T8 di ADR 0096.
- Riwayat pindah badan usaha tidak disimpan; yang tercatat badan usaha terkini beserta siapa dan kapan mengubahnya.

**Perkiraan besaran kerja.** Dua PR berurutan: backend (integration + finance) lalu layar web. Tanpa env baru, tanpa kategori notifikasi baru.

## Deskripsi

*Menambahkan badan usaha pemilik toko (`payroll_company_id`) sebagai atribut kepemilikan di `department_shops`, diisi leader Marketing di alur klaim toko yang sudah ada, lalu tab Toko di sheet Badan Usaha membaca atribut itu menggantikan turunan rekening. Memecah bagian "pemetaan toko" dari T8 ADR 0096 menjadi T8a dan memindahkan penulisnya dari Finance ke Marketing.*

- **Status**: 🟡 Diusulkan, kode belum ada
- **Path di repo** (rencana):
  - `bip-erp/services/integration/internal/domain/entity/department_shop.go`, `internal/interface/http/department_shop_handler.go`, `internal/infrastructure/repository/department_shop_repo.go`, `internal/interface/http/toko_ringkas_handler.go`, `main.go`
  - `bip-erp/services/payroll/` (daftar pilihan badan usaha untuk panggilan antar-service, bila endpoint yang ada tak bisa dipakai)
  - `bip-erp/services/finance/akuntansi_cv_toko_badan_usaha.go`
  - `erp-frontend/src/app/(main)/icc/management/page.tsx` (tab Kepemilikan Toko), `src/features/integration/icc/`, `src/features/secretary/badan-usaha/components/tab-toko-badan-usaha.tsx`, `src/i18n/locales/{id,en}.ts`
- **Tanggal**: 2026-10-22

## Context

Diukur 2026-10-22 ke bip-erp dan erp-frontend `origin/main` serta data PROD (baca saja).

1. **Belum ada pemetaan toko ke badan usaha yang tersimpan di mana pun.** `AccurateShop` tak punya field CV/PT/badan usaha (`services/integration/internal/domain/entity/accurate.go:193-215`), `EntitasCV` tak punya field toko (`services/finance/akuntansi_cv_entitas.go:39-42`). `git grep` `origin/main` atas `payroll_company|kode_cv|badan_usaha|pemilik_toko|legal_entity` di integration, marketing-analytics, insentive, dan warehouse: nol.
2. **Tab Toko di sheet Badan Usaha hari ini turunan rekening**: toko `accurate_shops.bank_account_no` sama dengan entitas `akun_accurate_no` (`services/finance/akuntansi_cv_toko_badan_usaha.go:84-124`, butir 15 [[ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca]]). Di PROD 69 dari 69 toko berekening 1310/1320/1340, bukan rekening PT/CV, jadi tak satu pun cocok.
3. **Pemasangan otomatis lewat nama tidak menghasilkan apa pun.** PROD 2026-10-22: 69 `accurate_shops` (47 MARKETING - BEAUTYHACKS, 22 MARKETING - KY + GB) dibandingkan 72 entitas finance (40 CV, 32 PT) sesudah normalisasi (huruf kecil, buang `CV`/`PT` dan tanda baca, cocok bila salah satu memuat yang lain): **0 cocok tepat satu, 0 ganda, 69 tanpa kandidat**. Nama toko adalah merek (Beautyhacks.id, Kyura Beauty Official, Glowbooster7.id - DIKA). Aturan "nama yang cocok tepat satu kandidat dipasangkan otomatis" di ADR 0096 karena itu tak punya bahan.
4. **Marketing sudah memegang kepemilikan toko.** `department_shops` (`entity/department_shop.go:24-38`, unik `(channel, shop_id)`) ditulis lewat `POST /department-shops` bergerbang `RequireMarketingLeader`, dengan pembatasan per departemen di handler (`services/integration/main.go:1656-1660`, `department_shop_handler.go:50`). Layarnya ICC Management, tab Kepemilikan Toko (erp-frontend `app/(main)/icc/management/page.tsx`). Langkah ini sudah tercatat sebagai langkah 2 di [[RUN - Onboarding Toko Marketplace Baru]]. PROD: 76 baris `department_shops`.
5. **Marketing yang membuka toko** (keputusan user 2026-10-22), jadi pemilik fakta "toko ini atas nama badan usaha mana" adalah Marketing. `accurate_shops` sebaliknya diisi tim integration/finance di Config Accurate, dan rute tulisnya tanpa gerbang peran (`main.go:2288-2292`).
6. **Daftar badan usaha tidak terbaca Marketing.** `GET /companies` payroll digerbang `gateBacaBadanUsaha` = `payroll.view` atau `secretary.badan_usaha.kelola` (`services/payroll/badan_usaha_gate.go:40-52`, `routes.go:36`). Leader Marketing tak memegang keduanya.
7. **Kunci badan usaha**: sheet Badan Usaha per `payroll_company_id` ([[ADR - 0182 Badan Usaha Satu Daftar untuk HR dan Finance, Entitas CV Menempel Tanpa Nama Sendiri]]); entitas CV dan PT di finance menempel ke kunci yang sama (`payroll_company_id`), sehingga kode CV untuk T8 tetap bisa diturunkan.
8. ⚠️ **Berdiri di atas ADR berstatus 🟡.** ADR 0096, ADR 0182, dan ADR 0183 masih Diusulkan walau sebagian kodenya sudah berjalan.

## Decision

1. **Badan usaha pemilik toko disimpan di `department_shops`** sebagai `payroll_company_id`, bersama penanda siapa dan kapan terakhir mengubahnya. Satu toko milik tepat satu badan usaha; **satu badan usaha boleh memiliki banyak toko**, lintas channel dan lintas departemen, tanpa batas jumlah (keputusan user 2026-10-22). Kosong berarti belum diisi, bukan "milik badan usaha default".
2. **Penulisnya leader/SPV Marketing**, lewat `POST /department-shops` yang sudah ada dengan gerbang dan pembatasan per departemen yang sama. Tidak ada pintu tulis kedua, termasuk dari Finance atau Config Accurate.
3. **Pilihan dibatasi badan usaha yang masih beroperasi.** Daftar pilihannya disediakan integration-service untuk pemegang gerbang Marketing, diambil dari payroll lewat panggilan antar-service (id + nama saja, tanpa data gaji). Integration memvalidasi `payroll_company_id` terhadap daftar yang sama saat menyimpan; id yang tak dikenal ditolak 400.
4. **Tanpa pemasangan otomatis** (Context 3). Seluruh toko diisi manusia; layar Kepemilikan Toko menampilkan jumlah toko yang belum berbadan usaha.
5. **Tab Toko di sheet Badan Usaha membaca `department_shops.payroll_company_id`** menggantikan turunan rekening. Keadaan `tanpa_rekening`, `rekening_ganda`, dan `belum_dipetakan` diganti satu penanda: jumlah toko yang belum dipilihkan badan usaha (global). Gerbang baca sheet tidak berubah (`gateKopSekretariatCV`).
6. **Memecah T8 ADR 0096**: bagian pemetaan toko menjadi T8a (ADR ini) dengan penulis Marketing dan kunci `payroll_company_id`, menggantikan rumusan "toko dipetakan ke kode CV di master Finance, nama cocok dipasangkan otomatis". Jurnal penjualan per CV, penarikan saldo, dan pertanyaan buku dasar laporan CV tetap T8.

## Consequences

- Fakta kepemilikan toko punya satu pemilik dan satu tempat (Marketing, `department_shops`); Finance dan Sekretariat membaca. Sesuai [[REF - Kepemilikan Data]].
- Toko yang ada di `accurate_shops` tetapi belum diklaim departemen (atau sebaliknya) tak punya badan usaha sampai diklaim; laporan kesehatan `department_shops` yang sudah ada tetap jadi tempat menemukannya.
- Mengganti badan usaha toko langsung berlaku tanpa persetujuan dan tanpa riwayat. Bila T8 kelak menjurnal per CV, perpindahan di tengah periode perlu tanggal berlaku; itu diputuskan di T8, bukan di sini.
- Kontrak lintas service baru: integration memanggil payroll untuk daftar badan usaha, dan finance membaca field baru dari integration. Deploy: payroll (bila endpointnya baru) dan integration sebelum finance, BE sebelum FE.
- [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]], [[ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca]], [[REF - Kepemilikan Data]], [[RUN - Onboarding Toko Marketplace Baru]], [[Finance - Proses Penjualan Marketplace dan Uang Masuk]], dan [[Microservices - Integration Service]] disunting bersama ADR ini.

## Belum Diputuskan (TBD)

- **Pemakai keputusan** di luar tab Toko belum dinyatakan; asumsi: Sekretariat (legalitas per badan usaha) lalu Finance (T8).
- **Toko atas nama PT Bharata Internasional** dipilih seperti badan usaha lain; apakah toko tanpa badan usaha boleh dianggap milik PT diputuskan Finance di T8.

## Dokumen Terkait

- [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] (T8 dipecah) · [[ADR - 0183 Badan Usaha Dikelola Sekretariat, HR dan Finance Membaca]] (butir 15 diganti) · [[ADR - 0182 Badan Usaha Satu Daftar untuk HR dan Finance, Entitas CV Menempel Tanpa Nama Sendiri]] · [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]]
- [[Microservices - Integration Service]] · [[RUN - Onboarding Toko Marketplace Baru]] · [[Finance - Proses Penjualan Marketplace dan Uang Masuk]] · [[REF - Kepemilikan Data]]
