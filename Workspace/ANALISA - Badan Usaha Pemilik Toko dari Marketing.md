# ANALISA - Badan Usaha Pemilik Toko dari Marketing

**Status**: ⛔ Menunggu ADR [[ADR - 0197 Badan Usaha Pemilik Toko Diisi Marketing saat Klaim Kepemilikan Toko]] Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.

- **Keputusan**: [[ADR - 0197 Badan Usaha Pemilik Toko Diisi Marketing saat Klaim Kepemilikan Toko]] (memecah T8 [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]])
- **Dok domain**: [[Microservices - Integration Service]] § Kepemilikan toko per departemen · [[RUN - Onboarding Toko Marketplace Baru]] langkah 2 · [[REF - Kepemilikan Data]]
- **Ukuran**: **Sedang**, dua repo, masing-masing satu PR. BE (bip-erp: integration + finance, dan payroll bila daftar badan usaha butuh endpoint antar-service baru) satu PR; FE (erp-frontend) satu PR. FE memang harus berubah: tab Kepemilikan Toko belum punya kolom badan usaha (`app/(main)/icc/management/page.tsx`), dan tab Toko sheet Badan Usaha masih merender keadaan rekening (`features/secretary/badan-usaha/components/tab-toko-badan-usaha.tsx:45,56,90-92`).
- **Pemutus**: `irfanarfianto` (SPV FAT diminta ikut menyetujui karena menyentuh T8 ADR 0096)
- **Tanggal**: 2026-10-22

## Kebutuhan yang dijawab

Setiap toko tercatat dibuka atas nama badan usaha mana, oleh orang yang membukanya (Marketing), supaya Sekretariat melihat toko per badan usaha dan T8 punya kunci. Dasar data PROD 2026-10-22: 69 toko `accurate_shops`, 76 baris `department_shops`, 72 entitas (40 CV, 32 PT); pemasangan otomatis lewat nama 0 dari 69, turunan rekening 0 dari 69.

## Issue

### Induk: Badan usaha pemilik toko diisi Marketing (T8a)
- **Repo**: bip-erp · **Issue**: [bip-erp#3434](https://github.com/bip-itteam-internal/bip-erp/issues/3434)
- Tanpa PR sendiri. Sub-issue: [BE] lalu [FE]. Ditutup manual saat keduanya merged.

### [BE] Badan usaha pemilik toko di department_shops, tab Toko membacanya
- **Repo**: bip-erp · **Urutan**: 1 · **Issue**: [bip-erp#3435](https://github.com/bip-itteam-internal/bip-erp/issues/3435)

**Pemutus:** irfanarfianto
**PIC:** (diisi saat In Progress)

## Masalah
Tak ada tempat menyimpan "toko X dibuka atas nama badan usaha Y". Tab Toko di sheet Badan Usaha menebaknya dari rekening Accurate, dan di PROD tebakan itu tak pernah cocok (0 dari 69 toko).

## Keputusan
[[ADR - 0197 Badan Usaha Pemilik Toko Diisi Marketing saat Klaim Kepemilikan Toko]]. Layak `Siap Agent` sesudah ADR berstatus Diterima.
- Field `payroll_company_id` + pengubah + waktu ubah di `department_shops`; ditulis lewat `POST /department-shops` yang ada (`RequireMarketingLeader`, batas per departemen).
- Satu toko satu badan usaha; satu badan usaha banyak toko. Kosong = belum diisi, bukan default.
- Pilihan = badan usaha beroperasi, disediakan integration dari payroll lewat panggilan antar-service (id + nama).

## Yang harus benar
- `POST /department-shops` menerima `payroll_company_id` opsional; id yang bukan badan usaha beroperasi ditolak 400 dengan pesan yang menyebut badan usahanya tak dikenal; mengosongkannya kembali (string kosong) diterima dan tersimpan kosong (bukan diabaikan, perhatikan `$set` + `omitempty`).
- Upsert yang tak menyebut `payroll_company_id` tidak mengosongkan nilai yang sudah ada (klaim ulang departemen tak menghapus badan usaha).
- Endpoint daftar pilihan badan usaha untuk pemegang gerbang Marketing mengembalikan hanya id + nama badan usaha yang beroperasi; akun tanpa gerbang itu 403.
- `GET /department-shops` dan endpoint ringkas toko memuat `payroll_company_id`.
- Finance `GET /akuntansi-cv/badan-usaha/:payrollCompanyId/toko` mengembalikan seluruh toko ber-`payroll_company_id` itu (lebih dari satu toko per badan usaha teruji) dan jumlah toko global yang belum berbadan usaha; tidak lagi membaca `bank_account_no`.
- Test handler lewat Fiber untuk jalur 400/403, dan test kontrak finance yang mengurai respons integration apa adanya.

## Di luar cakupan
Jurnal penjualan per CV, penarikan saldo per CV, riwayat perpindahan badan usaha, pemasangan otomatis (semuanya T8 atau tidak diputuskan).

## Data / bukti pendukung
PROD 2026-10-22 (baca saja): `accurate_shops` 69 (47 MARKETING - BEAUTYHACKS, 22 MARKETING - KY + GB); `department_shops` 76; `akuntansi_cv_entitas` 72 (40 CV, 32 PT); kecocokan nama toko ke entitas 0/69; rekening toko 1310/1320/1340, 0/69 cocok rekening entitas. `GET /companies` payroll tertutup bagi Marketing (`badan_usaha_gate.go:40-52`).

## Prasyarat
ADR 0197 Diterima.

### [FE] Pilih badan usaha di Kepemilikan Toko, tab Toko membacanya
- **Repo**: erp-frontend · **Urutan**: 2 · **Issue**: [erp-frontend#2725](https://github.com/bip-itteam-internal/erp-frontend/issues/2725)

**Pemutus:** irfanarfianto
**PIC:** (diisi saat In Progress)

## Masalah
Leader Marketing tak punya tempat memilih badan usaha toko, dan tab Toko di sheet Badan Usaha menampilkan keadaan rekening yang tak pernah cocok.

## Keputusan
[[ADR - 0197 Badan Usaha Pemilik Toko Diisi Marketing saat Klaim Kepemilikan Toko]]. Layak `Siap Agent` sesudah ADR berstatus Diterima.

## Yang harus benar
- ICC Management › Kepemilikan Toko: kolom Badan Usaha per toko + pemilih (Combobox) berisi badan usaha beroperasi dari endpoint pilihan integration; menyimpan lewat upsert yang sama; toko tanpa badan usaha diberi penanda dan jumlahnya tampil di atas tabel.
- Sheet Badan Usaha › tab Toko menampilkan seluruh toko milik badan usaha itu (nama, channel, departemen) dan jumlah toko global yang belum dipilihkan badan usaha; keadaan rekening (`tanpa_rekening`, `rekening_ganda`, `belum_dipetakan`) dihapus.
- Seluruh teks baru lewat i18n `id` + `en`; kosong/galat/403 terbaca.

## Di luar cakupan
Halaman baru; perubahan Config Accurate.

## Data / bukti pendukung
Lihat [BE].

## Prasyarat
[BE] merged; deploy BE (integration, finance, dan payroll bila tersentuh) sebelum FE.
