# ADR - 0178 Serapan Anggaran per Departemen Jurnal, Seluruh Perusahaan Dihapus, Pagu Gabungan per Departemen

> **Status**: 🟢 Diterima, 2026-10-15, oleh Azzerith. Diusulkan 2026-10-15 lewat `/analisa-kebutuhan` (aturan persetujuan di [[ADR - 0151 Issue Siap Dikerjakan Agent Bila Keputusannya Bisa Ditunjuk, Ditandai Manusia]]). Kode belum ada. Pertanyaan terbuka Finance di §Consequences masih menahan pagu gabungan (T4–T5), tidak menahan T1–T3. **Butir 1–2 direvisi sebagian oleh [[ADR - 0180 Akun Anggaran Seluruh Perusahaan Diatur Finance, Non Ops Dua Akun dengan Baseline Isian]]** (2026-10-15): departemen kosong kembali sah khusus untuk akun di daftar akun seluruh perusahaan yang diatur Finance.

## Untuk Manajemen

**Apa yang berubah di layar.** Tabel "Serapan per pos" di Anggaran & Cost Control dipecah **per departemen sesuai tag di jurnal Accurate**: UMUM, Marketing KY + GB, Marketing Beautyhacks, Marketing Bahan Pangan, berurutan dalam kelompok per divisi. Baris "Seluruh perusahaan" dihapus dari tabel maupun dari angka KPI. Urutan kolom menjadi Terpakai lalu Anggaran. Kolom Sisa diganti **Varians = Terpakai − Anggaran**, sehingga minus berarti anggaran masih tersisa dan plus berarti lewat anggaran, ditambah kolom **% Varians**. Finance bisa membuat **pagu gabungan** per departemen per bulan, misalnya "Beban packing" (dua akun packing) dan "lain-lain marketing" (semua belanja operasional marketing selain iklan, gaji, dan packing). Satu pagu dikurangi realisasi seluruh akun anggotanya.

**Siapa yang terdampak.** Cost Control (mengisi RAPB per departemen dan pagu gabungan, memantau serapan), Supervisor Finance, dan pemegang KPI Cost Control. Divisi marketing kini terlihat masing-masing.

**Apa yang TIDAK dijanjikan.**
- Belanja yang dijurnal **tanpa departemen** atau dengan departemen yang salah tetap salah di laporan ini. Sumbernya tag jurnal Accurate, dan sistem tidak menebak.
- Lewat anggaran tetap hanya **memperingatkan**; tidak memblokir pengajuan.
- Rumus KPI Cost Control tidak berubah: tetap selisih mutlak total ≤ 5%. Yang berubah hanya isinya, yaitu total per departemen tanpa baris se-perusahaan.
- Anggaran per proyek tetap tidak ada.
- RAPB yang sudah diunggah tanpa departemen **tidak dipindahkan otomatis**; Finance mengunggah ulang.

**Perkiraan besaran kerja.** Sekitar 4 PR, BE lebih dulu: (1) tampilan tabel, (2) baris se-perusahaan dibuang dan input tanpa departemen ditolak, (3) pagu gabungan di backend, (4) pagu gabungan di layar dan template.

## Deskripsi

*Serapan anggaran dibaca per departemen yang ditandai di jurnal Accurate. Baris departemen kosong ("Seluruh perusahaan") tidak lagi menjadi pos anggaran, tidak ditampilkan, dan tidak ikut total maupun KPI. Anggaran boleh berupa pagu gabungan beberapa akun pada satu departemen per bulan. Tanda varians di layar Serapan mengikuti Finance: Terpakai − Anggaran. Merevisi sebagian [[ADR - 0159 Serapan Anggaran Dibaca dari Pengajuan sebagai Bagian dari Terpakai, Rute Tulis Anggaran Digerbang Izin Sendiri]] K1/K4 dan [[ADR - 0097 Anggaran Iklan Dashboard Marketing Dibaca dari Master Anggaran Finance]] butir 2.*

- **Status**: 🟢 Diterima 2026-10-15 (Azzerith), kode belum ada
- **Path di repo**:
  - `bip-erp/services/integration/internal/domain/entity/anggaran.go`
  - `bip-erp/services/integration/internal/usecase/anggaran_varians.go`
  - `bip-erp/services/integration/internal/usecase/anggaran_xlsx.go`
  - `bip-erp/services/integration/internal/interface/http/anggaran_handler.go`
  - `bip-erp/services/integration/internal/domain/entity/pagu_gabungan.go` (baru)
  - `bip-erp/services/integration/internal/usecase/pagu_gabungan.go` (baru)
  - `erp-frontend/src/features/finance/anggaran/components/tabel-serapan.tsx`
  - `erp-frontend/src/features/finance/anggaran/components/tab-serapan.tsx`
  - `erp-frontend/src/features/finance/anggaran/lib/serapan.ts`
  - `erp-frontend/src/features/finance/anggaran/components/tab-anggaran-bulanan.tsx`
- **Tanggal**: 2026-10-15

## Context

Permintaan Cost Control (2026-10-15, lewat chat) atas tabel Serapan per pos memuat tujuh butir:
1. pengelompokan per divisi;
2. Terpakai di kiri, Anggaran di kanan;
3. Sisa diganti Varians;
4. % Varians;
5. pagu gabungan;
6. KPI = total seluruhnya;
7. arti "Seluruh perusahaan".

Klarifikasi dengan Finance di chat yang sama:
- "Seluruh perusahaan" yang tampil adalah **inputan awal dari sistem**, bukan maksud Finance. Laporan realisasi seharusnya **mengikuti tag departemen di jurnal**, bukan perlakuan data anggaran ("tidak perlu ada seluruh perusahaan, dirinci saja umum, marketing").
- RAPB diinput Finance **per divisi per bulan**.
- Pagu "lain-lain marketing" **per divisi per bulan** (contoh 45 jt).
- Tanda varians: **Terpakai − Anggaran**, sehingga minus berarti anggaran masih tersedia (dikonfirmasi user 2026-10-15).

Keadaan kode (`bip-erp` origin/main b957f1252, `erp-frontend` origin/main 2b533e90f):
- **Kunci anggaran** = akun × departemen × tahun × bulan; departemen `""` = seluruh perusahaan (`entity/anggaran.go:18-47`).
- **Realisasi per departemen** diturunkan dari `departmentId` di riwayat transaksi akun (history.do). Baris `""` realisasi adalah **jumlah semua baris akun itu** (`usecase/agregasi_riwayat_akun.go:144-152`). Populasi akun OPEX sengaja ditambahkan **hanya** di departemen `""` supaya belanja tak beranggaran tidak hilang (`worker/tasks/realisasi_opex_refresh.go`, komentar `jalankanRefreshRealisasi`).
- **`HitungVarians`**: `Varians = Anggaran − Realisasi`, `PersenTerpakai` nil bila anggaran 0 (`entity/anggaran.go:296-304`). Field `varians` dipakai 6+ konsumen FE dengan tanda ini, antara lain kartu Varians OPEX, kotak sisa pos pengajuan, kartu Anggaran pengajuan, peringatan lewat anggaran, dan panel OPEX Marketing.
- **`RingkasVarians`** menjumlah semua baris terdefinisi **tanpa membedakan** baris `""` dari baris per departemen (`entity/anggaran.go:338-360`). Bila satu akun punya anggaran di `""` dan di departemen, realisasinya terhitung dua kali.
- **KPI.** Sumber KPI `varians_anggaran` (`services/employee/kpi_sumber_varians_anggaran.go`) membaca total itu tanpa filter departemen, dengan metrik `varians_absolut_persen` = |TotalVarians| / TotalAnggaran (mutlak). Ada juga metrik `varians_persen` yang bertanda ("positif berarti hemat", `:128-132`). Dipakai KPI Cost Control #1 (0,2), SPV FAT F2 (0,25), dan baris Tax ([[HRIS - Matriks KPI per Departemen]]). Tidak ada bukti skor KPI ini dipakai untuk uang (skema insentif KPI-multiplier dihapus 2026-07-30, `services/insentive/business_rules.go:36-41`).
- **Data prod Oktober 2026** (dibaca 2026-10-15, `GET /accounting/anggaran/varians?tahun=2026&bulan=10`, baca saja):
  - **38 dari 38 baris beranggaran** ada di departemen `""`; **nol** baris anggaran per departemen.
  - 18 baris `""` lainnya hanya punya realisasi.
  - Realisasi per departemen: MARKETING - KY + GB Rp 317,8 jt, MARKETING - BEAUTYHACKS Rp 227,5 jt, UMUM Rp 92,9 jt, MARKETING - BAHAN PANGAN Rp 2,6 jt.

  Jadi hitung dobel belum terjadi, tetapi akan terjadi begitu Finance mengunggah RAPB per departemen tanpa menghapus baris `""`.
- **Pagu gabungan belum ada di mana pun.** `git grep` di integration dan erp-frontend tidak menemukannya. Pola terdekat: `AkunPackingMarketing` (6109 Beban Packing Pihak Ketiga, 6116 Beban Packing Gd Sidareja, `usecase/beban_marketing_packing.go:20-23`), `DaftarAkunIklan`, dan agregat `ringkas_tanpa_iklan`. **"Packing Sadewa" bukan nama akun Accurate**; tidak ada di kode maupun vault.
- **Template unggah RAPB sudah punya kolom Departemen** (`usecase/anggaran_template.go`, `kolomTetapKanonik`), dan departemen `MARKETING - BAHAN PANGAN` sudah ada di Accurate.

Keputusan sebelumnya yang bertabrakan:
- [[ADR - 0159 Serapan Anggaran Dibaca dari Pengajuan sebagai Bagian dari Terpakai, Rute Tulis Anggaran Digerbang Izin Sendiri]] K1 (dimensi akun × departemen, tanpa dimensi lain) dan K4 (Sisa = Anggaran − Terpakai). ADR itu sendiri masih 🟡 Diusulkan.
- [[ADR - 0097 Anggaran Iklan Dashboard Marketing Dibaca dari Master Anggaran Finance]] butir 2 ("tak seorang pun menetapkan anggaran gabungan"), yang ditulis untuk anggaran **iklan** dua brand.
- Aturan ⛔ di [[Finance - Serapan Anggaran dan Cost Control]]: anggaran 0 tampil "tidak punya anggaran", bukan 0.

## Decision

1. **Departemen jurnal adalah dimensi wajib untuk pos anggaran.**
   - Upload RAPB dan form anggaran **menolak** baris tanpa departemen. Pesannya menyebut baris dan meminta departemen Accurate, dengan nama yang persis.
   - Baris `""` lama tidak dihapus otomatis. Ia tetap tersimpan sampai Finance mengunggah ulang, tetapi tidak dipakai lagi (butir 2).
   - Merevisi ADR 0159 K1: dimensinya tetap akun × departemen, hanya departemen kosong yang tidak lagi sah.
2. **Baris "Seluruh perusahaan" tidak menjadi pos.**
   - `/accounting/anggaran/varians` tidak mengeluarkan baris departemen `""`, baik anggaran maupun realisasi.
   - `RingkasVarians` hanya menjumlah baris per departemen. Hitung dobel hilang karena baris `""` tidak pernah ikut.
   - Belanja OPEX yang tak beranggaran tetap terlihat, karena baris per departemen realisasi tetap lahir dari transaksinya, berstatus "anggaran belum diisi".
   - Belanja yang dijurnal **tanpa departemen** tetap ditampilkan sebagai baris ber-departemen "Tanpa departemen" (realisasi saja), supaya tidak hilang diam-diam.
   - Populasi refresh realisasi tetap menarik akun OPEX di `""`; yang berubah hanya keluaran varians.
3. **Pagu gabungan (entitas baru, integration-service).**
   - Isinya: nama, departemen (wajib), tahun, bulan, nominal, dan daftar akun anggota.
   - Terpakai pagu = Σ realisasi akun anggota **di departemen itu** pada periode itu.
   - Satu akun pada satu departemen dan bulan hanya boleh menjadi anggota **satu** pagu, dan **tidak boleh** sekaligus punya anggaran per akun. Upload yang melanggar ditolak, supaya realisasinya tidak terhitung dua kali.
   - Varians, % Varians, dan `melebihi` pagu dihitung dengan aturan yang sama dengan pos per akun.
   - Pagu ikut `RingkasVarians` sebagai satu pos, sehingga total KPI tetap satu angka.
   - Merevisi ADR 0097 butir 2 untuk OPEX umum. Untuk anggaran **iklan** dua brand, butir itu tetap berlaku.
4. **Tanda varians di layar Serapan = Terpakai − Anggaran.**
   - Dihitung di FE untuk tabel Serapan dan rincian pos saja. Field `varians` backend **tidak** dibalik, karena konsumennya 6+ layar lain dan metrik KPI `varians_persen`.
   - % Varians = Varians ÷ Anggaran × 100.
   - Bila anggaran 0, sel menampilkan "—" dengan keterangan "tanpa anggaran", bukan 0%. Ini menyimpang dari permintaan "anggaran 0 → 0" karena 0% akan terbaca "sesuai anggaran"; perlu konfirmasi Finance, lihat Consequences.
5. **Tampilan tabel.**
   - Kelompok per divisi dengan subtotal: Marketing KY + GB (`MARKETING - KY + GB`), Marketing Beautyhacks (`MARKETING - BEAUTYHACKS`), Marketing Bahan Pangan (`MARKETING - BAHAN PANGAN`), lalu departemen lain (UMUM dst.) urut nama.
   - Kolom: Departemen, Akun/Pagu, Terpakai, Anggaran, Varians, % Varians.
   - Di dalam kelompok, urutan tetap % terpakai tertinggi dulu.
6. **KPI Cost Control tidak diubah rumusnya.**
   - Total yang dibaca kini total per departemen, termasuk pagu gabungan, tanpa baris se-perusahaan.
   - Cakupan KPI dihitung dari baris per departemen saja. Baris "anggaran belum diisi" tetap menurunkan cakupan seperti sekarang.
   - Ini memenuhi butir 6 permintaan ("total seluruhnya") tanpa hitung dobel.

## Consequences

- **Finance wajib mengunggah ulang RAPB per departemen.** Sampai itu terjadi, sesudah butir 2 di-deploy, tabel Serapan dan KPI **kosong anggaran** (semua pos "anggaran belum diisi"), karena seluruh anggaran Oktober ada di `""`. Urutan deploy karena itu: **Finance mengunggah ulang dulu, baru butir 2 naik.** Atau butir 2 diberi masa transisi; diputuskan di task-nya.
- **Pertanyaan terbuka untuk Finance** (tidak menahan butir 1, 2, 4, 5):
  - (a) Apakah "Packing Sadewa" = 6109 Beban Packing Pihak Ketiga?
  - (b) Daftar akun persis untuk pagu "lain-lain marketing". Usulan: semua akun marketing di daftar OPEX kecuali 6101 Gaji Sales & Marketing, 6107 Iklan, 6108 Pajak Iklan, 6109, dan 6116. Status 6102 Bonus & Insentif masih perlu diputuskan.
  - (c) % Varians saat anggaran 0: "—" atau 0%.
  - (d) Nama pagu jangan bentrok dengan akun Accurate 6111 "Beban Lain-lain Marketing". Usulan nama: "Ops Marketing".
- **Field `varians` backend tetap bertanda lama.** Satu konsep kini punya dua tanda di dua tempat: backend Anggaran − Terpakai, layar Serapan Terpakai − Anggaran. Penjaganya: tanda baru dihitung di **satu** fungsi FE, dan dok [[Finance - Serapan Anggaran dan Cost Control]] menyebut keduanya.
- **Kontrak `/accounting/anggaran/varians` berubah** (baris `""` hilang, field pagu bertambah), jadi **deploy integration-service sebelum FE**. Konsumen lain yang memakai baris `""` ikut terdampak, misalnya `cariPos` di sisa pos pengajuan yang jatuh ke baris (akun, `""`), dan panel OPEX Marketing yang menjumlah departemen marketing. Keduanya wajib diperiksa di task BE.
- **Baris tanpa departemen di jurnal** jadi terlihat sebagai "Tanpa departemen". Finance perlu disiplin men-tag jurnal; itu sesuai keinginan mereka ("mengikuti inputan").
- **Data prod Oktober belum diukur ulang sesudah unggah ulang Finance.** Sebelum butir 2 naik, ukur kembali bahwa baris per departemen sudah beranggaran.

## Dokumen Terkait

- [[Finance - Serapan Anggaran dan Cost Control]]
- [[ADR - 0159 Serapan Anggaran Dibaca dari Pengajuan sebagai Bagian dari Terpakai, Rute Tulis Anggaran Digerbang Izin Sendiri]]
- [[ADR - 0097 Anggaran Iklan Dashboard Marketing Dibaca dari Master Anggaran Finance]]
- [[HRIS - Matriks KPI per Departemen]]
- [[API - Integration Service]]
- [[Finance - Rancangan Finance Service]]
