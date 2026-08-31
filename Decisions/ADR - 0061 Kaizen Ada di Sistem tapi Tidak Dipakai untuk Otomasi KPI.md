## Deskripsi

*Modul Kaizen dan kedua sumber KPI-nya **ada dan terdaftar di kode**, tetapi **tidak dipakai** dalam perencanaan otomasi skor KPI. Metrik ber-redaksi "ide inovasi / Kaizen" di seluruh template `kpi_template` **tetap dinilai manual**. Keputusan ini murni soal PEMAKAIAN, bukan soal ketersediaan: tak ada kode yang dihapus, tak ada rencana pembangunan yang dibatalkan.*

- **Status**: ✅ **Berlaku** sejak 2026-08-31. Keputusan pemilik proses (SPV), bukan temuan teknis. Tidak menyentuh kode: modul Kaizen tetap hidup di produksi seperti sebelumnya.
- **Path di repo (yang TIDAK diubah)**: `bip-erp/services/employee/kpi_sumber_kaizen.go` · `bip-erp/services/form-builder/kaizen_metrics.go`
- **Tanggal**: 2026-08-31

## Context

Dokumen [[HRIS - Matriks KPI per Departemen]] menyatakan di **18 sel** bahwa *"TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru."* Pernyataan itu **salah**, dan diverifikasi salah pada 2026-08-31 terhadap `bip-erp` `main` (`9734bea0`):

| Yang ada | Bukti |
|---|---|
| Dua sumber KPI terdaftar | `services/employee/kpi_sumber_kaizen.go:29-30` — `kaizen_ide_diajukan` & `kaizen_ide_diterapkan`, didaftarkan ke katalog di baris `169` dan `178` |
| Endpoint pemasok | `services/form-builder/kaizen_metrics.go:32` — `GET /internal/kaizen/metrics?period=YYYY-MM&company_id=` |
| Tipe form | `FormTypeKaizen`, dipakai di `kaizen_metrics.go:53`, diuji di `kaizen_me_test.go` · `type_rules_test.go` · `laporan_handlers_test.go` |
| Modul lengkap | [[HRIS - Kaizen (Ide Perbaikan)]] — seluruh tahap live di dev dan prod sejak 2026-08-06 |

Metrik ber-redaksi "ide inovasi" muncul di **sembilan dari sebelas template Finance** dan tersebar sampai Manufaktur, Kyura, HRGA, dan Tech Development. Selama vault menyatakan modulnya tidak ada, siapa pun yang merencanakan otomasi akan menyimpulkan template-template itu mustahil disentuh — kesimpulan yang berdasar pada dokumen yang keliru.

Namun memperbaiki dokumen saja menciptakan risiko yang berlawanan: pembaca berikutnya bisa membaca "modulnya ada dan sumbernya terdaftar" sebagai "kalau begitu ayo otomatiskan sembilan template Finance". Itu juga **tidak benar**.

Dua fakta yang harus hidup berdampingan di vault:

- **A (fakta kode)** — modul Kaizen ada, sumbernya terdaftar, endpointnya jalan.
- **B (keputusan)** — Kaizen tidak dipakai dalam perencanaan otomasi KPI.

Tanpa ADR ini, B tidak punya tempat tinggal. Keputusan "ada tapi sengaja tidak dipakai" adalah jenis yang paling cepat hilang dari ingatan tim, lalu tiga bulan kemudian ada yang menemukan `kaizen_ide_diajukan` di katalog sumber dan bertanya kenapa tak dipakai — atau lebih buruk, memakainya.

## Decision

**Kaizen TIDAK dipakai sebagai sumber otomasi skor KPI. Metrik "ide inovasi / Kaizen" di seluruh template tetap dinilai manual oleh atasan.**

Turunannya:

1. **Tak ada konfigurasi `auto` bersumber `kaizen_ide_diajukan` atau `kaizen_ide_diterapkan` yang boleh dipasang** di `kpi_template` lewat `/hris/kpi/otomasi`, sampai keputusan ini dicabut.
2. **Kode tidak disentuh.** Kedua sumber tetap terdaftar di katalog, endpoint form-builder tetap melayani, dan modul Kaizen tetap berjalan sebagai program pengumpulan ide. Yang berhenti hanyalah rencana memakainya untuk **menilai orang**.
3. **Vault wajib menyatakan keduanya.** Setiap sel matriks KPI yang menyangkut Kaizen menyebut modulnya ada **dan** keputusan ini, dengan pranala ke ADR ini. Menyebut salah satu saja mengulang kesalahan yang justru sedang diperbaiki.
4. **Pertanyaan "apakah ada program Kaizen hidup di produksi" ditutup** sebagai prasyarat otomasi KPI. Ia tetap pertanyaan sah bagi modul Kaizen itu sendiri ([[HRIS - Kaizen (Ide Perbaikan)]]), tetapi bukan lagi penghambat yang perlu diselesaikan demi KPI.

### Yang harus ditinjau ulang bila keputusan ini dicabut

Bukan daftar pekerjaan hari ini — daftar yang harus dibaca lebih dulu oleh siapa pun yang membalikkan keputusan ini:

| # | Prasyarat | Kenapa |
|---|---|---|
| 1 | Ada satu form `form_type: kaizen`, `deleted_at: null` per `company_id` | Tanpanya `kaizenMetricsHandler` membalas `has_program:false` (`kaizen_metrics.go:56-66`), dan `cuplikanKaizen` memperlakukan itu sebagai **galat**, bukan nol (`kpi_sumber_kaizen.go:156-158`). Metrik **gagal hitung**, bukan bernilai nol |
| 2 | Terjemahan kuartal → bulan disepakati | Sumber menghitung per `period_key` bulanan; banyak target berbunyi "N ide per kuartal". Ini keputusan pemilik metrik, bukan pekerjaan kode |
| 3 | `FORM_BUILDER_MODULE_URL` terisi di employee-service | Bila kosong, sumber menggalat *"FORM_BUILDER_MODULE_URL belum diatur"* (`kpi_sumber_kaizen.go:115-118`) |

## Consequences

**Yang membaik.** Vault berhenti menyatakan sesuatu yang salah, dan sekaligus berhenti mengundang kesimpulan yang salah ke arah sebaliknya. Perencana otomasi KPI berikutnya tahu persis kenapa Kaizen tidak ada di daftar pekerjaannya — dan itu bukan karena sistemnya kurang.

**Yang memburuk.** Sembilan template Finance tetap tak bisa mencapai **otomasi penuh**: `seluruhMetrikOtomatis()` menuntut SEMUA metrik dalam satu template ber-`auto` sebelum skornya dibekukan sistem ([[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]). Satu metrik Kaizen manual di dalam template cukup untuk menahan seluruh template tetap manual. Konsekuensi itu **diterima**, dan perlu disebut supaya tak dicari-cari sebabnya di tempat lain.

**Yang tetap.** Modul Kaizen berjalan sebagaimana adanya sebagai program pengumpulan ide; keputusan ini tidak menyentuh papan ide, komite, maupun kepatuhan kuota.

## Dokumen Terkait

- [[HRIS - Matriks KPI per Departemen]] — sel-sel yang diralat, bagian "Ralat 2026-08-31 Kaizen dan forecast kas"
- [[HRIS - Kaizen (Ide Perbaikan)]] — modul yang keberadaannya dikonfirmasi ADR ini
- [[HRIS - Otomasi Skor KPI]] — kerangka otomasi yang Kaizen dikeluarkan darinya
- [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]] — sebab satu metrik manual menahan seluruh template
- [[Microservices - Employee Service]] — pemilik katalog sumber KPI
- [[Microservices - Form Builder Service]] — rumah kode modul Kaizen
- [[RUN - Menambah Metrik KPI Otomatis]] — prosedur yang TIDAK dijalankan untuk Kaizen selama ADR ini berlaku
