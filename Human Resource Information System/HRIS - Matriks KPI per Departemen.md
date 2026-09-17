## Deskripsi

*Isi lengkap `kpi_template` di **production**: seluruh label metrik, bobot, dan targetnya, dikelompokkan per departemen. Dokumen kerja untuk dev departemen yang akan mengotomatiskan metriknya. Cara mengerjakannya ada di [[RUN - Menambah Metrik KPI Otomatis]]; latar belakang dan analisis kelayakannya di [[HRIS - Otomasi Skor KPI]].*

- **Status**: ⚠️ Salinan setia data production per **2026-08-01**, dengan bab **Tech Development** disegarkan langsung dari `employee_db` prod **2026-08-28** (status arsip template, konfigurasi `auto` yang benar-benar terpasang, dan ketersediaan tiap sumbernya). Bukan rancangan dan bukan usulan; ini yang benar-benar dipakai menilai orang hari ini. **Ralat 2026-08-31**: 18 sel yang menyatakan "TIDAK ADA modul Kaizen" dan 1 sel yang menyatakan "TIDAK ADA modul forecast" **salah** dan sudah diperbaiki — rinciannya di bagian [[#Ralat 2026-08-31 Kaizen dan forecast kas]]. **Segar 2026-09-02**: bab **Recruitment & Onboarding** ditulis ulang dari `employee_db` + `recruitment_db` prod (template aktifnya sudah berganti jadi `Recruitment` dan dua metriknya berbeda dari yang tercatat sebelumnya), sel `PPIC / Inventory Turnover Ratio` diralat karena berisi verdict rekrutmen yang salah tempel, dan baris rekrutmen di `KPI Supervisor HRGA` disegarkan angkanya. **Segar 2026-09-12**: bab **Finance** ditulis ulang dari `employee_db` prod (template, konfigurasi `auto`, penetapan, dan skor 2026; rinciannya di bab itu). **Segar 2026-09-15**: bab **Training & Perfomance Officer** ditulis ulang dari `employee_db` + `learning_db` prod (template aktifnya sudah berganti jadi `People and Development` dengan 6 metrik, dan modul Training ternyata sudah punya post-test berskor yang belum dipakai; rinciannya di bab itu). **Segar 2026-09-15 sore**: sumber KPI `pelatihan` (tiga sub-metrik) live di produksi; baris metrik pelatihan di bab Training & Perfomance Officer dan Culture & Industrial disegarkan, dan **klasifikasinya tidak bergeser** karena konektor kini ada tetapi datanya masih kosong. **Dicatat 2026-09-16**: baris `Terlaksananya kegiatan training & performance officer sesuai dengan rencana` (bab Training & Perfomance Officer) disegarkan — sumber KPI baru `rencana_pelatihan` (Tahap 2 Training & Performance Officer) SUDAH DITULIS di employee-service, dan PR bip-erp #1903 serta #1904 sudah **merged** (diukur `gh pr view` 2026-09-17: bip-erp PR #1903 dan #1904 merged 2026-09-16 00:53Z; ter-deploy di prod, gerbang biner 2026-09-17); klasifikasi baris itu **tidak bergeser** dari *modul ada tapi datanya kosong*. **Ditambah 2026-09-16**: bab **Live Support** (Kyura) ditulis dari `employee_db` prod — template `Host Live Support Kyura` seluruhnya manual, satu karyawan, satu-satunya skor ada di 2026-07, dan Agustus belum dinilai; hitungan template departemen Kyura juga dicatat sudah tertinggal dari salinan 2026-08-01 (17 template, 12 aktif). **Dicatat 2026-09-17**: baris `Skor Penilaian Training All Karyawan > 70 ` (bab Training & Perfomance Officer) disegarkan untuk Tahap 3b (pre-test, kelulusan dari kenaikan skor, dan pilihan sumber kedua `peningkatan_post_test_persen` di samping `skor_post_test_persen`); kodenya di bip-erp PR #1913 + #1934, erp-frontend PR #1603 + #1619, my-bharata PR #151 + #153, semuanya merged; backend dan web ter-deploy di prod per 2026-09-17, MyBharata baru di `dev`. Klasifikasi **tidak bergeser**, dan angka prod 2026-09-15 di bab itu ditandai perlu diukur ulang.
- **Sumber**: koleksi `kpi_template` di `employee_db` ([[Microservices - Employee Service]]).

## Cara membaca

**Label ditulis persis seperti tersimpan**, termasuk typo (`Perfomance Monitoring`), spasi di ujung (`Monitoring Team `), dan penomoran yang tidak deskriptif (`Performa 1`, `Administrasi 3`). Itu bukan kelalaian penyalinan: **label adalah kunci identitas metrik di kode**, sehingga menuliskannya "yang benar" di sini justru membuat dokumen tidak cocok dengan sistem.

Kolom **Target / keterangan** adalah isi `description` apa adanya. Di situlah target sebenarnya tersimpan, karena `kpi_template` **tidak punya field target yang dapat dibaca mesin** (diverifikasi: nol template memilikinya). Konsekuensinya sebagian deskripsi memuat lebih dari satu angka, dan itu harus diselesaikan dengan pemilik metriknya sebelum diotomatiskan.

Kolom **Klasifikasi otomasi** per departemen memakai empat kategori dari [[HRIS - Otomasi Skor KPI]]: sumber ada dan terisi / sumber ada tapi butuh definisi / modul ada tapi datanya kosong / tidak ada sumber sama sekali. Itu penilaian tingkat departemen. **Verdict per metrik tetap tugas dev departemen**, memakai langkah 1 di [[RUN - Menambah Metrik KPI Otomatis]], karena "endpointnya ada" tidak sama dengan "datanya cukup terisi".

## Ringkasan

| Departemen       | Template |  Metrik | Otomatis |   Semi | Terblokir data |  Manual | by    |
| ---------------- | -------: | ------: | -------: | -----: | -------------: | ------: | ----- |
| Beauty Hacks     |       11 |      30 |       14 |      2 |              0 |      14 | kukuh |
| Finance          |       12 |      62 |       16 |    TBD¹ |             TBD¹ |     TBD¹ | ozi   |
| General Affair   |        5 |      24 |        1 |      5 |              1 |      17 | irfan |
| Human Resource   |        5 |      32 |        6 |      7 |              9 |      10 | irfan |
| Kesekretariatan  |        7 |      28 |        0 |      0 |              0 |      28 | ozi   |
| Kyura            |        9 |      27 |       16 |      1 |              0 |      10 | kukuh |
| Manufaktur       |        9 |      52 |        3 |     16 |             16 |      17 | izan  |
| Procurement      |        2 |      10 |        4 |      2 |              0 |       4 | faiz  |
| Quality          |        4 |      18 |        1 |      2 |              8 |       7 | faiz  |
| Tech Development |        7 |      30 |       14 |      9 |              0 |       7 | izan  |
| **Total**        |   **70** | **312** |   **72** | **61** |         **34** | **145** |       |

Dua departemen di `work_data` **tidak muncul di sini karena belum punya template sama sekali**: Percetakan (13 karyawan) dan Marketing Offline Distribution (1 karyawan).

> ⚠️ **Ralat 2026-09-14 (sensus produksi baca-saja):** kalimat di atas benar untuk salinan 2026-08-01, tetapi tak lagi utuh. `kpi_template` kini memuat **4 template aktif berdepartemen `Printing`**, sementara departemen yang sama di `master_department` (key `printing`) dan di `work_data` (14 karyawan) bernama **`Percetakan`**. Pratinjau KPI Saya mencari template dengan nama departemen persis (`services/employee/kpi_me_pratinjau.go`), jadi keempat template itu tidak cocok dengan satu karyawan pun di jalur tersebut. Bab untuk keempat template itu belum ditulis di dokumen ini. Rinciannya di [[REF - Peta Departemen]]. Marketing Offline Distribution tetap tanpa template.

## Ralat 2026-08-31 Kaizen dan forecast kas

> **Status ralat**: ✅ diverifikasi ke kode `bip-erp` `main` (`9734bea0`, 2026-08-28) pada 2026-08-31.
> Yang diralat: **14 sel** berbunyi *"TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol
> hasil di services + shared-library)"* dan **2 sel** berbunyi *"TIDAK ADA modul forecast/demand
> planning"* pada metrik yang sebenarnya mengukur **forecast KAS** (Cost Control #4 dan Finance
> Supervisor `Return on Operation`). Empat sel Kaizen sisanya diralat **berbeda** karena bukan
> hitungan ide (lihat "Batas ralat ini"). Dua sel lain yang memakai kalimat forecast yang sama —
> `Inventory turn over 90 days` di Beauty Hacks dan Kyura — **tidak diralat dan memang tetap
> benar**: yang mereka ukur adalah *demand planning*, dan modul itu memang tidak ada.

### Dua hal yang wajib dipisahkan

Bagian ini mencatat **dua fakta yang berbeda dan tidak boleh saling menggantikan**:

| | Pernyataan | Sifatnya |
|---|---|---|
| **A** | Modul Kaizen **ADA** di sistem, dua sumber KPI-nya **terdaftar** | fakta kode, terverifikasi |
| **B** | Kaizen **DIPUTUSKAN TIDAK DIPAKAI** dalam perencanaan otomasi KPI | keputusan SPV, 2026-08-31 |

Vault sebelumnya salah ke arah **"tidak ada"**. Ralat ini memperbaikinya, dan sekaligus **tidak
boleh** dibaca sebagai belok ke arah "kalau begitu dipakai": metrik ber-redaksi "ide inovasi/Kaizen"
di seluruh template **tetap dinilai MANUAL**. Keputusannya dicatat di
[[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]].

### A — Yang BENAR-BENAR ada (terverifikasi di kode)

| Fakta | Bukti di repo `bip-erp` |
|---|---|
| Dua sumber KPI Kaizen terdaftar | `services/employee/kpi_sumber_kaizen.go:29-30` (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`), didaftarkan ke katalog di baris `169` & `178` lewat `DaftarkanGrupSumber(..., GrupSumberUmum)` + `DaftarkanSumber` |
| Endpoint pemasoknya ada | `services/form-builder/kaizen_metrics.go:32` — `GET /internal/kaizen/metrics?period=YYYY-MM&company_id=` membalas `{data, period_key, has_program}` |
| Tipe form Kaizen ada | `FormTypeKaizen` di form-builder, dipakai di `kaizen_metrics.go:53` dan diuji (`kaizen_me_test.go`, `type_rules_test.go`, `laporan_handlers_test.go`) |
| Sumber `forecast_kas` ada | `services/employee/kpi_sumber_forecast_kas.go:29` (`SumberForecastKas = "forecast_kas"`), metrik `akurasi_forecast_kas` (baris 67), menarik `GET /accounting/anggaran/mingguan/kpi` dari integration-service (`services/integration/main.go:1446`). Ditambahkan commit `58119297`, **14 Agustus 2026** |
| Nama sumber Cost Control | `services/employee/kpi_sumber_cost_control.go:26` — `kinerja_cost_control`, **bukan** `cost_control` |

Modul dan alurnya didokumentasikan di [[HRIS - Kaizen (Ide Perbaikan)]].

### B — Kenapa "terdaftar" tetap bukan "berangka"

Bahkan seandainya keputusan SPV berbalik, `kaizen_ide_*` **tidak otomatis berangka**.
`kaizenMetricsHandler` mencari satu form ber-`company_id`, `deleted_at: nil`, `form_type:
FormTypeKaizen`; bila tak ada, ia membalas `has_program:false` — **200, bukan galat**
(`kaizen_metrics.go:56-66`), karena itu keadaan sah. Di sisi employee-service, `cuplikanKaizen`
memperlakukan `has_program:false` sebagai **galat** (`kpi_sumber_kaizen.go:156-158`): menilai orang
atas kewajiban yang belum dinyalakan bukan nol, melainkan pertanyaan yang salah. Akibatnya metrik
Kaizen **gagal hitung**, bukan bernilai nol.

Ada dua syarat lain yang juga tak terjawab oleh keberadaan sumber: **periode** (sumber menghitung
per bulan `YYYY-MM`, sedangkan target di tabel banyak berbunyi "N ide per kuartal" — terjemahannya
keputusan pemilik metrik, bukan pekerjaan kode) dan **env** `FORM_BUILDER_MODULE_URL` di
employee-service prod, yang bila kosong membuat sumber menggalat *"FORM_BUILDER_MODULE_URL belum
diatur"* (`kpi_sumber_kaizen.go:115-118`).

Ketiganya dicatat di sini sebagai **prasyarat yang harus ditinjau ulang bila keputusan B dicabut**,
bukan sebagai pekerjaan yang tertunda. Selama ADR 0061 berlaku, tak ada yang perlu diverifikasi ke
produksi soal ini.

### Batas ralat ini

Yang diubah **hanya kolom Sumber dan Rekomendasi** pada sel-sel yang keliru. **Bobot, label, dan
deskripsi tidak disentuh** — itu salinan `kpi_template` produksi. Angka pada tabel Ringkasan
(kolom Otomatis / Semi / Terblokir / Manual) **tidak berubah**: metrik Kaizen tetap terhitung
**manual**, sekarang karena keputusan, bukan karena ketiadaan modul.

Empat sel berlabel Kaizen **tidak** dilayani sumber ini dan karena itu diralat berbeda:
`Inovation & Improvement` (Manufaktur Supervisor), `Kaizen 1` (jumlah CAPA produksi), `Kaizen 2`
(kualitas produk 98% sesuai SOP QC), dan `Kaizen dan Growth` (review SOP & WI). Labelnya menyebut
Kaizen, tapi yang diukur bukan hitungan ide — jadi `kaizen_ide_*` tak akan menjawabnya walau
keputusan B dicabut. Masing-masing ditandai di tempatnya dengan sumber yang sebenarnya dituju.

## Cacat yang sudah diketahui

> Aturan penamaan yang seharusnya berlaku (label menyebut yang diukur bukan targetnya,
> nomor tanpa makna dilarang, keterangan wajib) ada di
> [[REF - Penamaan Metrik & Sumber KPI]]. Baris-baris di bawah adalah contoh
> pelanggarannya yang benar-benar terpasang di produksi hari ini.

Beberapa baris di bawah memang cacat di datanya, dan sengaja disalin apa adanya supaya terlihat:

- **Template uji ikut produksi.** `Beauty Hacks / Buzzer / Buzzer` berisi satu metrik berlabel `contoh` berbobot 1.0, sehingga posisi Buzzer punya dua template.
- **Metrik duplikat.** `Manufaktur / Warehouse Leader` memuat `Mencegah over-dispensing ...` dan `... 2` dengan deskripsi identik, total bobot 0,30 untuk hal yang sama.
- **Label memakai target korporat, bukan metrik personal.** `Revenue 240M`, `Net Income 20%`, `Penurunan HPP 5%` muncul sebagai label di posisi Staff Inventory, Tax Staff, dan QA RND. Metrik sebenarnya ada di deskripsinya.
- **Template menilai produk departemen lain.** `Kyura / Kyura Supervisor` memuat `Customer Satisfactions untuk Produk Beautyhacks 4,5 dari 5`.
- **Satu deskripsi memuat tiga angka.** `Kyura Supervisor / Revenue 240M` berbobot 0,6: label menyebut 240M, deskripsinya menyebut profit 546 juta dan omzet 4.090.000.000.
- **Target pindah dari `description` ke `label`.** Template `Recruitment` (22 Agu 2026) mengisi kelima `description`-nya dengan `Target 100%` yang seragam dan memindahkan kalimat metriknya ke `label`. Aturan baca di [[#Cara membaca]] ("target sebenarnya tersimpan di `description`") karena itu **tidak berlaku universal**. Diperiksa 2026-09-15: `People and Development` (juga 22 Agu 2026) mengikuti pola yang sama (`Target 100%`, `Target 100% > 70`, `Target Skala 10`); template generasi baru lainnya belum diperiksa.
- **`key` dipakai ulang untuk metrik yang berbeda.** `People and Development` mempertahankan `key` `kpi` dari template arsipnya, padahal metriknya berganti dari SLA pengumpulan KPI jadi Employee Productivity. Rinciannya di [[#Training & Perfomance Officer]].

Cacat pada **dokumen ini sendiri**, bukan pada datanya:

- **Verdict salah tempel antar-departemen.** Sel `PPIC / Inventory Turnover Ratio` berisi verdict rekrutmen sampai diralat 2026-09-02. Kegagalannya senyap karena selnya terbaca wajar bila hanya kolom Rekomendasi yang dibaca, dan dev yang mengikutinya akan menyelidiki modul yang salah. **Saat menyegarkan satu bab, cocokkan isi kolom Sumber dengan label metriknya, jangan hanya menyalin baris.**
- ⚠️ **Belum diperiksa: kalimat `TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM` muncul 12 kali** di bab yang saling berjauhan (Finance 4, Quality 4, Kesekretariatan 2, Manufaktur 2 termasuk PPIC 1). Dihitung ulang 2026-09-15: semula 13, satu hilang saat bab Host Live Beauty Hacks disegarkan (sel `ROI` template arsip `HOST LIVE`), dan daftar bab versi sebelumnya keliru menyebut Kyura dan Beauty Hacks. Sebagiannya jelas cocok, tetapi `PPIC / Factory Utilization` menerima kalimat itu untuk utilisasi mesin yang tak ada hubungannya dengan pajak maupun BPOM. Belum diukur ulang, jadi **jangan dipercaya sebelum diverifikasi**; kemungkinan besar ia kalimat cadangan yang tersebar terlalu luas, sekelas dengan salah tempel di atas.

## Cara memperbarui dokumen ini

Angka di sini akan bergeser begitu template disunting. Untuk menyegarkan, baca ulang `kpi_template` di `employee_db` (urutkan `department`, `position`, `name`), lalu tulis ulang bab per departemen di bawah. Jangan menyunting sebagian, karena bobot antar-metrik saling terkait dan wajib berjumlah 1.0 per template.

## Dua kolom terakhir

**Sumber di sistem erp** menunjuk ke fakta teknis: nama koleksi atau endpoint beserta volumenya di produksi, atau pernyataan bahwa modulnya ada tapi datanya kosong, atau bahwa memang tidak ada di sistem. Ditujukan untuk dev.

**Rekomendasi** menjawab pertanyaan "jadi apa yang harus dikerjakan", ditulis tanpa istilah teknis supaya bisa dibaca pemilik metrik dan atasan, bukan hanya dev. Isinya jatuh ke lima pola:

| Bunyi rekomendasi | Artinya |
|---|---|
| "Bisa otomatis sekarang" | Datanya lengkap, tinggal disambungkan. Pekerjaan dev. |
| "Bisa otomatis, tapi sepakati dulu ..." | Datanya ada, definisinya yang belum jelas. Perlu keputusan pemilik metrik. |
| "Bisa sebagian" | Sebagian terhitung, sebagian belum, dan alasannya disebut. |
| "Belum bisa sekarang, tapi tidak perlu bikin fitur baru" | Menunya sudah ada tapi belum ada yang mengisi. Ini soal kebiasaan kerja, bukan soal kode. |
| "Belum bisa otomatis" | Memang belum ada di sistem. Perlu diputuskan apakah layak dibuatkan. |

**51 dari 311 metrik** berbunyi "perlu diperiksa dulu" alih-alih ditebak. Penunjuk yang keliru lebih merugikan daripada kolom kosong, karena dev akan mengikutinya.

Kolom ini **bukan pengganti langkah 1** di [[RUN - Menambah Metrik KPI Otomatis]]. Volume yang tertulis adalah jumlah dokumen di koleksinya, bukan jumlah yang relevan untuk satu orang pada satu periode. Contoh nyata bedanya: laporan SLA tiket punya endpoint dan rumus, tetapi **0 dari 293 tiket** memenuhi syarat hitung karena tenggatnya tidak pernah diisi.

> [!important] "Datanya ada" BUKAN "mesin KPI bisa menariknya" — dan tabel ini menjawab yang pertama
> Ditemukan 2026-08-22 saat menyiapkan konfigurasi metrik HRGA. Kolom **Sumber di sistem
> erp** menyebut endpoint atau koleksi tempat datanya hidup. Itu menjawab **ketersediaan
> data**. Yang TIDAK dijawabnya: apakah mesin otomasi KPI punya **konektor** untuk sumber
> itu.
>
> Keduanya berbeda, dan bedanya menentukan siapa yang mengerjakan. Metrik dengan konektor
> tinggal **diisi konfigurasinya** oleh HR di `/hris/kpi/otomasi`. Metrik tanpa konektor
> menuntut **dev menulis sumber baru** lebih dulu (prosedurnya di
> [[RUN - Menambah Metrik KPI Otomatis]]). Membaca "Bisa otomatis sekarang" sebagai yang
> pertama padahal yang kedua berarti menunggu sesuatu yang tak akan pernah datang.
>
> **Sumber yang benar-benar terdaftar di mesin** (`services/employee/kpi_sumber*.go`).
> ✅ **Angka KODE dan angka PRODUKSI kini bertemu.** Sensus 2026-08-25 mencatat 21 di
> `origin/main` versus 20 di produksi; **diukur ulang 2026-08-28 ke biner prod, 26 nama sumber
> yang diperiksa SELURUHNYA ada** (`docker exec Employee-Service grep -ac <nama> /service`,
> dengan kontrol negatif string karangan → 0). Employee-service prod dibuat ulang hari itu
> pukul 08:40 WIB.
>
> `skor_tim` · `varians_anggaran` · `akurasi_aset_ga` · `kinerja_tiket` · `uptime_sistem` ·
> `kinerja_ar` · `kinerja_ap` · `kinerja_sales_admin` · `kinerja_cost_control` ·
> `kinerja_toko` · `kinerja_po_marketing` · `admin_non_ops` · `forecast_kas` ·
> `kaizen_ide_diajukan` · `kaizen_ide_diterapkan` · `kedisiplinan_absensi` ·
> `turnover_karyawan` · `kontrak_karyawan` · `kinerja_affiliate` · `kinerja_affiliate_tim` ·
> ✅ **`kinerja_tiket_divisi`** · `insentif_profit` · `kinerja_live` · `kinerja_engagement` ·
> `indeks_layanan_tim` · `nilai_layanan_pribadi` · ✅ **`pelatihan`**
>
> ✅ **`pelatihan` ditambahkan [#1895](https://github.com/bip-itteam-internal/bip-erp/pull/1895) dan live di produksi 2026-09-15** (biner `Employee-Service` diperiksa dengan kontrol negatif). Daftar ini tetap bukan sensus: nama lain yang lahir sesudah 2026-08-28, mis. `nilai_inspeksi_satgas`, belum diukur ulang di sini.
>
> ⚠️ Lima nama terakhir **tidak pernah tercatat di daftar ini sampai 2026-08-28**, jadi jangan
> memperlakukan daftar mana pun di vault sebagai sensus terakhir tanpa mengukur ulang: `main`
> menerima sumber baru lebih cepat daripada dokumen ini disegarkan.
>
> `kedisiplinan_absensi`, `turnover_karyawan`, dan `kontrak_karyawan` ditambahkan
> [#1379](https://github.com/bip-itteam-internal/bip-erp/pull/1379) (naik di prod dan dev
> 2026-08-22). `kinerja_affiliate` dan `kinerja_affiliate_tim` sudah ada di biner prod
> (diverifikasi `grep -ac` pada `/service`, dengan kontrol negatif string karangan → 0).
>
> ✅ **`kinerja_tiket_divisi` LIVE di produksi 2026-08-28** (merged
> [#1427](https://github.com/bip-itteam-internal/bip-erp/pull/1427) +
> [#1428](https://github.com/bip-itteam-internal/bip-erp/pull/1428) 2026-08-25, naik ke prod
> tiga hari kemudian bersama `Task-Management-Service` dan `frontend-hris-dashboard`). Ia
> melayani metrik KPI **tingkat tim** dan menuntut `space.kpi_group` diisi lebih dulu —
> rinciannya di [[API - Task Management Service]] dan [[Microservices - Employee Service]].
>
> ⛔ **Kode yang hidup BUKAN berarti metriknya bisa dihitung, dan hari itu terbukti dua kali.**
> Pagi 2026-08-28 `GET /kpi/space-group` untuk divisi Tech Development masih membalas **409**
> berbunyi *"belum ada space divisi Tech Development yang dikelompokkan sebagai support (9 space
> divisi ini belum diisi kelompok KPI-nya); isi lewat Manajemen Tugas > Kelola Space > Ubah >
> Kelompok KPI"* — kodenya sudah hidup, data pendukungnya belum ada. Sore harinya kesembilan
> space diisi (**2 support**: Infrastructure dan IT Support; **7 development**: MyBharata/HRIS,
> System Finance, System Marketing, System Manufacture dan Warehouse, Official Website Bharata,
> procurement, Quality) dan rute yang sama menjawab angka: support Agustus 11 tiket masuk, 10
> selesai, 10 terukur SLA, 6 rating; development 16 masuk, 7 selesai, 7 terukur, 1 rating.
> **Pesan 409 itu sendiri yang menuntun ke layarnya**, dan itulah gunanya digalatkan alih-alih
> dijawab 200 berisi nol.
>
> Sub-metrik empat sumber HRGA:
>
> | Sumber | Sub-metrik | Melayani |
> |---|---|---|
> | `kedisiplinan_absensi` | `ketepatan_waktu` · `kelengkapan_catatan` | Personalia `Administrasi 1` & `Kedisiplinan`, Organizational Development `SOP` |
> | `turnover_karyawan` | `turnover_persen` | KPI Supervisor HRGA `Turn Over Rate Target 5% per Tahun` |
> | `kontrak_karyawan` | `perpanjangan_tepat_waktu` · `sisa_hari_kontrak` | Personalia `Administrasi 3` |
> | `pelatihan` (2026-09-15) | `kehadiran_peserta_persen` · `skor_post_test_persen` · `kepuasan_trainer_skala10` | People and Development `Training Attendance Rate`, `Skor Penilaian Training All Karyawan > 70 `, `Training Satisfaction Score ( 1 - 10 )`; Organizational Development `Culture 3` dan `KPI` |
>
> ⚠️ **Masih tidak ada sumber `recruitment` maupun `stok`.** Metrik yang kolom sumbernya
> menyebut koleksi `manufacture_*` atau data rekrutmen tetap **belum bisa dinyalakan**
> betapapun lengkap datanya.
>
> ⚠️ **Punya konektor ≠ skornya otomatis penuh.** `seluruhMetrikOtomatis()` menuntut SEMUA
> metrik dalam satu template ber-`auto` sebelum skornya dibekukan sistem
> ([[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]). `Personalia Team` punya lima
> metrik dan baru tiga yang terlayani, jadi penilaiannya tetap manual dan angka otomatis
> hanya mengisi awal modal. Tidak ada satu pun template HRGA yang dapat mencapai otomasi
> penuh selama `Succession Planing` belum punya modul.
>
> Baris yang sudah diperiksa terhadap daftar ini ditandai di tempatnya. Departemen selain
> HRGA **belum** ditelusuri satu per satu, jadi anggap kolom Rekomendasi di sana masih
> mencampur kedua hal ini sampai ada yang memeriksanya.
## Beauty Hacks

11 template, 30 metrik. Klasifikasi otomasi: **14 / 2 / 0 / 14**.

> ✅ **Posisi ICC sudah maju melewati snapshot ini.** Per sensus 2026-08-20, ICC Beauty Hacks (19 orang) memegang template dengan otomasi PENUH (bobot 1,00) dan skornya kini **dibekukan otomatis** oleh sistem tiap tanggal 1 — lihat [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]. Tabel ICC di bawah tetap salinan struktur metrik per 1 Agustus; rumus sumber yang benar-benar berjalan sekarang ada di `kpi_sumber_kinerja_toko.go` ([[Microservices - Employee Service]]).

### Affiliate

Template `AFFILIATE`, 2 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Jumlah Affiliate Aktif` | Jumlah Affiliator Baru yang bergabung dalam sebulan berdasarkan ketentuan perusahaan | affiliate_orders (194.761) + shopee_affiliate_performance (8.092). Definisi "affiliator baru bergabung" perlu ditetapkan lebih dulu. | Bisa otomatis, tapi sepakati dulu apa artinya "affiliator baru bergabung". Datanya sendiri sudah ada. |
| 0.7 | `Conversion` | Jumlah Konversi Iklan dalam Sebulan | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |

### BeautyHacks Supervisor

Template `BEAUTYHACKS SUPERVISOR`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.6 | `Revenue 240M` | Achievement 100% / Bulan | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.05 | `Inventory turn over 90 days` | Akurasi forecast minimal 85–90%. | TIDAK ADA modul forecast/demand planning. | Belum bisa otomatis. Sistem belum bisa memperkirakan permintaan, jadi tidak ada pembanding untuk menilai akurasinya. |
| 0.05 | `Customer Satisfactions untuk Produk Beautyhacks 4,5 dari 5` | Rating Toko > 4.5 | GET /task-management/report/csat. Pembacaan ulang prod 2026-08-06: **17 tiket ter-rating** seumur hidup, 13 di antaranya Juli. Masih tipis, dan seluruh rating Juli bernilai 5/5 sehingga belum membedakan siapa pun. | Belum layak dipakai. Yang menilai baru 17 orang seumur hidup dan semuanya memberi nilai penuh, jadi angkanya belum bisa membedakan pelayanan yang baik dari yang biasa saja. |
| 0.3 | `Performance Monitoring Team` | TARGET SKOR >70 | Sumber skor_tim + reduksi rata_rata, scope department. Sudah didukung mesin; tinggal isi konfigurasi. | Bisa otomatis sekarang. Sistem tinggal merata-ratakan skor anggota departemen, dan mesinnya sudah siap. |

### Buzzer

Template `BUZZER BHS`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Peforma 1` | Early Engagement Speed : Kecepatan boosting (like, comment, share, save) dalam waktu yang ditentukan setelah video tayang. | Akun buzzer memakai akun personal, TIDAK ada integrasi API. | Belum bisa otomatis. Akun buzzer milik pribadi, jadi sistem tidak punya cara membacanya. |
| 0.45 | `Performa 2` | Engagement Quantity : Jumlah like, comment, share, save sesuai target atau request tim ICC. | Akun buzzer memakai akun personal, TIDAK ada integrasi API. | Belum bisa otomatis. Akun buzzer milik pribadi, jadi sistem tidak punya cara membacanya. |
| 0.2 | `Performa 3` | Reporting & Account Readiness : Kelengkapan laporan harian dan kesiapan akun buzzer (akun aktif & organik). | Akun buzzer memakai akun personal, TIDAK ada integrasi API. | Belum bisa otomatis. Akun buzzer milik pribadi, jadi sistem tidak punya cara membacanya. |
| 0.05 | `Performa 4` | Kaizen : Jumlah inisiatif perbaikan yang diterapkan. | Akun buzzer memakai akun personal, TIDAK ada integrasi API. | Belum bisa otomatis. Akun buzzer milik pribadi, jadi sistem tidak punya cara membacanya. |

### Buzzer

Template `Buzzer`, 1 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 1 | `contoh` | contoh | Akun buzzer memakai akun personal, TIDAK ada integrasi API. | Belum bisa otomatis. Akun buzzer milik pribadi, jadi sistem tidak punya cara membacanya. |

### Customer Support

Template `CUSTOMER SERVICE`, 3 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Perfomance 1` | Closing Rate | TIDAK ADA data percakapan CS / chat marketplace. | Belum bisa otomatis. Percakapan dengan pembeli belum masuk ke sistem. |
| 0.6 | `Perfomance 2` | Konversi | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.1 | `Kaizen` | Jumlah inisiatif perbaikan yang diterapkan. | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |

### Host Live

> ✅ **Segar 2026-09-15**, diukur langsung dari `employee_db` prod (baca-saja), menggantikan salinan 2026-08-01. Template lama `HOST LIVE` (`Conversion` 0,6 · `ROI` 0,3 · `Perfomance Monitoring` 0,1, seluruhnya manual) kini berstatus **`arsip`** (terakhir diubah 2026-08-22). Yang menilai host sekarang `Host Live Beautyhacks` (dibuat 2026-08-06, terakhir diubah 2026-08-27), isi metriknya identik dengan `Host Live Kyura` di bab Kyura (hanya `key` metrik kedua yang berbeda). Klasifikasi departemen di atas (**14 / 2 / 0 / 14**) masih salinan 2026-08-01 dan **belum** memasukkan perubahan ini. Temuan yang berlaku untuk kedua departemen (kenapa skor Agustus identik, skor beku yang keliru, target 7 vs keputusan pemilik metrik) ditulis sekali di bab Kyura › Host Live.

Template `Host Live Beautyhacks`, 3 metrik, **seluruhnya otomatis**. 4 karyawan aktif ber-`position` Host Live (diukur 2026-09-15).

| Bobot | Label (`key`) | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.7 | `Conversion Rate` (`conversion`) | Target Minimal 7% | ✅ `auto`: sumber `kinerja_live` metrik `conversion_rate` (pesanan dibayar ÷ klik produk × 100), formula `rata_rata`, target **7**, arah naik, scope `individu`. Rumus dan penjaganya di [[Microservices - Employee Service]] § `kinerja_live`. | Sudah otomatis. Angkanya dihitung dari siaran yang dicatat host sendiri di MyBharata, jadi host yang tak mencatat shift tak punya skor otomatis. |
| 0.1 | `Add to Chart` (`perfomance-monitoring`) | Target Minimal 7% | ✅ `auto`: `kinerja_live` metrik `add_to_cart_rate` (masuk keranjang ÷ klik produk dari sesi yang data keranjangnya terukur × 100), `rata_rata`, target **7**, naik, `individu`. `key` mewarisi metrik lama karena `key` diturunkan sekali lalu dipertahankan (`KPIMetric.Key`). | Sudah otomatis. Deskripsinya sama persis dengan Conversion Rate; pastikan ke pemilik metrik bahwa target 7% memang dimaksud (lihat bab Kyura). |
| 0.2 | `Average view duration` (`average-view-duration`) | Target Minimal 60 detik | ✅ `auto`: `kinerja_live` metrik `avg_viewing_duration` (rata-rata detik tonton, ditimbang tayangan), `rata_rata`, target **60**, naik, `individu`. | Sudah otomatis. |

Ketiga blok `auto` memuat `target_per_karyawan` untuk satu karyawan dengan angka yang sama dengan target umum, jadi tak mengubah hasil siapa pun.

**Keadaan skor Host Live Beauty Hacks** (diukur `kpi_score` prod 2026-09-15; ID karyawan sengaja tidak disalin):

| Periode | Template di snapshot | Penilai | Skor |
|---|---|---|---|
| 2026-07 | `HOST LIVE BH` (`Conversion` 0,7 · `Perfomance Monitoring` 0,3) | manual, 3 host | 19,6 untuk ketiganya |
| 2026-07 | `Host Live Beautyhacks` | `OTOMASI`, 1 host | 90, dengan `Add to Chart` bernilai **0**; host ini baru masuk 26 Agustus 2026 (lihat bab Kyura › Host Live) |
| 2026-08 | `Host Live Beautyhacks` | `OTOMASI`, 3 host | **90,29 identik** untuk ketiganya |

Template `HOST LIVE BH` yang dipakai skor manual Juli **tak lagi ada** di `kpi_template`: kueri nama dan posisi `host live` hanya menemukan empat template, yaitu dua di atas, `Host Live Kyura`, dan `Host Live Support Kyura`.

⚠️ **September 2026: tak satu pun dari 4 host Beauty Hacks akan dibekukan otomatis bila keadaannya bertahan** (diukur lewat `GET /kpi/kinerja-live` prod per 15 September, bulan masih berjalan). Pembekuan menuntut ketiga metrik punya angka (`layakDifinalisasi`), dan tiap host gagal pada paling sedikit satu:

| Keadaan | Host | Sebab |
|---|---:|---|
| Belum mencatat shift sama sekali | 1 | ketiga metrik "belum ada shift live tercatat" |
| Klik porsi di bawah ambang 100 | 2 | 34 dan 30 klik, jadi `conversion_rate` dan `add_to_cart_rate` "belum dapat dihitung"; durasi tonton tetap terhitung (31 dan 35 detik) |
| Shift tercatat, belum satu pun terjodoh | 1 | host baru (masuk 14 September), 2 shift tak cocok dengan siaran mana pun |

Volume departemennya memang kecil: jalur departemen menghitung **262 klik** dari 16 siaran host sepanjang 1 sampai 15 September, sementara ambang 100 klik per orang dikalibrasi dari akun brand bervolume tinggi (sekitar 123 klik per jam siaran). Dua host yang shift-nya terjodoh juga membawa **8 dan 6 shift tak terjodoh**. Keputusan untuk pemilik metrik (**TBD**): ambang per departemen, atau menerima bahwa Host Live Beauty Hacks dinilai manual. Mengubah scope ke `department` **bukan** jalan keluar: skornya tetap per orang, hanya penjaga ambangnya yang lepas sehingga rasio dari 30-an klik ikut dinilai (koreksi di temuan 6 bab Kyura › Host Live).

### ICC

Template `INTERNAL CONTENT CREATOR`, 3 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.4 | `Jumlah Video` | 125 video/bulan | tt_shop_video_performances (85.149 baris, ada published_at & gmv per video). Atribusi lewat icc_account_mappings employee_id -> tiktok_shop_id. Kyura pakai ambang GMV; Beauty Hacks pakai mart_video_performance.sumber (vsa/gmv_max). | Bisa otomatis sekarang. Data tiap video sudah tersimpan lengkap dengan tanggal tayang dan omzetnya. Syaratnya tiap orang sudah terdaftar memegang toko mana. Kyura sudah 10 dari 12 orang, Beauty Hacks belum sama sekali. |
| 0.2 | `Video Memenuhi Standar Struktur Indikator VSA` | ≥ 70% atau min. 87 video | tt_shop_video_performances (85.149 baris, ada published_at & gmv per video). Atribusi lewat icc_account_mappings employee_id -> tiktok_shop_id. Kyura pakai ambang GMV; Beauty Hacks pakai mart_video_performance.sumber (vsa/gmv_max). | Bisa otomatis sekarang. Data tiap video sudah tersimpan lengkap dengan tanggal tayang dan omzetnya. Syaratnya tiap orang sudah terdaftar memegang toko mana. Kyura sudah 10 dari 12 orang, Beauty Hacks belum sama sekali. |
| 0.4 | `Video Memenuhi Standar Struktur Indikator GMV MAX` | ≥ 30% atau min. 37 video | tt_shop_video_performances (85.149 baris, ada published_at & gmv per video). Atribusi lewat icc_account_mappings employee_id -> tiktok_shop_id. Kyura pakai ambang GMV; Beauty Hacks pakai mart_video_performance.sumber (vsa/gmv_max). | Bisa otomatis sekarang. Data tiap video sudah tersimpan lengkap dengan tanggal tayang dan omzetnya. Syaratnya tiap orang sudah terdaftar memegang toko mana. Kyura sudah 10 dari 12 orang, Beauty Hacks belum sama sekali. |

### Leader

Template `LEADER`, 3 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Perfomance Monitoring` | Persentase Team ICC Mencapai target KPI | Sumber skor_tim + reduksi rasio_ambang (ambang = skor minimal, target = 100%). Cakupan team butuh work_data.supervisor_id terisi (2026-08-01: 54 dari 204). | Bisa otomatis, syaratnya data siapa atasan siapa sudah diisi. Per 1 Agustus baru 54 dari 204 karyawan yang terisi. |
| 0.4 | `Conversion` | 120,000 | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.4 | `ROI` | > 3.2 | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |

### Marketplace Advertiser

Template `ADV MARKETPLACE`, 2 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.7 | `Conversion` | Jumlah konversi iklan dalam sebulan | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.3 | `CPA` | Rata-rata biaya iklan yang dikeluarkan per konversi | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |

### Meta Advertiser

Template `ADV META`, 2 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.5 | `Conversion` | Jumlah konversi iklan dalam sebulan | Meta/Facebook Ads TIDAK terintegrasi. Hanya TikTok Business/Shop, Shopee, Lazada, Accurate. | Belum bisa otomatis. Iklan Meta dan Facebook belum tersambung ke sistem; yang tersambung baru TikTok, Shopee, Lazada, dan Accurate. |
| 0.5 | `CPA` | Rata-rata biaya iklan yang dikeluarkan per konversi | Meta/Facebook Ads TIDAK terintegrasi. Hanya TikTok Business/Shop, Shopee, Lazada, Accurate. | Belum bisa otomatis. Iklan Meta dan Facebook belum tersambung ke sistem; yang tersambung baru TikTok, Shopee, Lazada, dan Accurate. |

### Video Editor

Template `VIDEO EDITOR`, 3 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.35 | `Lead Time` | Persentase pengambilan dan edit Video Content berdasarkan transisi, editing, dan hasil akhir selesai tepat waktu untuk pemenuhan tim marketing. | TIDAK ADA tracker garapan desain/video (pengajuan, persetujuan, tenggat). Metriknya menilai mutu dan ketepatan garapan, bukan performa video di marketplace. | Tetap manual. Yang dinilai mutu dan ketepatan garapan, dan itu penilaian orang. Yang bisa dibantu sistem hanya ketepatan waktunya, kalau ada pencatatan pengajuan dan tenggat. |
| 0.25 | `Pengelolaan Alat dan Kelengkapan` | Persentase alat yang berfungsi baik, jumlah alat yang rusak, dan kerapihan penyimpanan & Kondisi kebersihan alat. | TIDAK ADA tracker garapan desain/video (pengajuan, persetujuan, tenggat). Metriknya menilai mutu dan ketepatan garapan, bukan performa video di marketplace. | Tetap manual. Yang dinilai mutu dan ketepatan garapan, dan itu penilaian orang. Yang bisa dibantu sistem hanya ketepatan waktunya, kalau ada pencatatan pengajuan dan tenggat. |
| 0.4 | `Kualitas Konten` | Persentase pengambilan & edit video content disetujui kualitasnya. | TIDAK ADA tracker garapan desain/video (pengajuan, persetujuan, tenggat). Metriknya menilai mutu dan ketepatan garapan, bukan performa video di marketplace. | Tetap manual. Yang dinilai mutu dan ketepatan garapan, dan itu penilaian orang. Yang bisa dibantu sistem hanya ketepatan waktunya, kalau ada pencatatan pengajuan dan tenggat. |

## Finance

*Persona, akses nyata (RBAC efektif per posisi), dan alur kerja antar-posisi Finance (AR, AP, Cost Control, Senior Accountant, Tax, Supervisor Finance) ada di [[Finance - FAT Persona]]; dokumen ini hanya memuat matriks metrik KPI.*

> ✅ **Segar 2026-09-12**, ditulis ulang langsung dari `employee_db` prod, menggantikan salinan 2026-08-01. Yang berubah: dua template baru (**AR Staff 2026**, **KPI SENIOR ACCOUNTING UPDATE**), dua template diarsipkan 2026-08-25 (**KPI AR Leader**, **AR STAFF PIUTANG**), label dan deskripsi sejumlah metrik berubah dibanding snapshot lama (dicatat per sel), kelima metrik **KPI Supervisor Finance** kini ber-`auto` dengan arah F4 yang sudah dibetulkan, dan **Senior Accountant** kini memegang dua template aktif sekaligus.

14 template (12 aktif, 2 arsip), 62 metrik aktif. Klasifikasi otomasi: **16 / TBD¹ / TBD¹ / TBD¹**. Angka Otomatis (16) dihitung ulang 2026-09-12 dari jumlah metrik ber-`auto` terpasang di `kpi_template`; Semi/Terblokir/Manual **belum dihitung ulang** sejak 2026-08-01, jadi ditandai TBD di sini (juga di baris Finance tabel Ringkasan di atas) alih-alih menyalin angka lama (17/0/31) yang sudah tidak menjumlah pas ke 62 metrik aktif. Posisi Finance aktif tanpa template aktif: **tidak ada** (diukur `employee_db` prod 2026-09-12).

> ¹ Klasifikasi Semi/Terblokir/Manual Finance terakhir dihitung 2026-08-01 (angka lama: 17/0/31, dari total 61 metrik saat itu). Sejak itu jumlah metrik aktif berubah (61 → 62) dan Otomatis bertambah dari 13 ke 16, tetapi ketiga kategori lain belum ditelusuri ulang satu per satu; menyalin angka lama akan menjumlah ke 33, bukan 46 (62 − 16), sehingga sengaja ditandai TBD alih-alih dipertahankan.

### AR Leader

⚠️ **Template `KPI AR Leader` (5 metrik) diarsipkan 2026-08-25.** Tidak ada pemegang posisi "AR Leader" aktif di `work_data` per 2026-09-12 (1 tercatat, 0 aktif). Satu akun ber-`work_data.position` **AR Staff** tetapi ber-`position_key` **`ar_leader`** dinilai memakai template ini pada periode Juni dan Juli 2026 (skor 40,4 dan 52,0). Posisi tercatat dan template penilai tidak sama persis, dan tak ada karyawan aktif hari ini yang cocok dengan kombinasi itu. Tabel di bawah dipertahankan sebagai arsip; bobot, label, dan sumber tidak berubah sejak 2026-08-01, dan jangan dipakai sebagai acuan penetapan template baru.

Template `KPI AR Leader`, 5 metrik. **Arsip 2026-08-25.**

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Mengurangi piutang aging > 60 hari sampai < 5% dari total AR` | Rekonsiliasi AR Harian | Accurate live proxy: GET /accounting/receivables + GET /orders/piutang/summary. | Bisa otomatis sekarang. Data piutang diambil langsung dari Accurate. |
| 0.3 | `Pengawasan 100% AR aging ≤ 14 hari` | Follow-up pembayaran & rekonsiliasi kas - 90% pembayaran diterima sesuai aging ≤ 14 hari | Accurate live proxy: GET /accounting/receivables + GET /orders/piutang/summary. | Bisa otomatis sekarang. Data piutang diambil langsung dari Accurate. |
| 0.2 | `Monitoring Team` | Checker inputan team/Rekonsiliasi dengan selesai pengimputan data max tgl 3 bulan berikutnya | BUKAN murni skor tim: deskripsinya menggabungkan checker inputan dengan ketepatan tanggal. Pisahkan dulu dengan pemilik metrik. | Perlu dipecah dulu. Satu baris ini mencampur dua penilaian berbeda: memeriksa input tim, dan ketepatan tanggal pengumpulan. |
| 0.1 | `Minimal 6 ide inovasi baru dari 5 TOTAL tim pada tiap kuartal` | Mengidentifikasi peluang inovasi di proses AR Finance | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV / Leader | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

### AR Staff

AR Staff memegang beberapa template aktif sekaligus, bukan satu posisi satu template: **AR Staff 2026** (baru), **KPI AR Piutang**, **KPI AR Retur**, dan **KPI Sales Admin**. Penetapan aktif per 2026-09-12 (fakta §7): AR Staff 2026 1, AR Piutang 4, AR Retur 3, Sales Admin 3.

#### AR Staff 2026 (baru, 2026-08-31)

Template `AR Staff 2026`, 3 metrik, seluruhnya ber-`auto`, scope **individu**.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.30 | `Piutang belum tertagih > 60 hari (porsi dari total AR)` | Rekonsiliasi AR Harian | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: kinerja_ar, metrik: piutang_lewat_60_persen, formula: rata_rata, target: 5, arah: turun, scope: individu}` (`services/employee/kpi_sumber_ar.go:35,188-190`). | Sudah berangka, tidak perlu pekerjaan dev. |
| 0.20 | `Piutang belum tertagih > 14 hari (porsi dari total AR)` | Follow-up pembayaran & rekonsiliasi kas. Yang dinilai porsi piutang yang MASIH tertunggak di atas 14 hari — makin kecil makin baik. | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: kinerja_ar, metrik: piutang_lewat_14_persen, formula: rata_rata, target: 5, arah: turun, scope: individu, target_per_karyawan: 1 orang}` (`kpi_sumber_ar.go:184-186`). | Sudah berangka, tidak perlu pekerjaan dev. |
| 0.50 | `Piutang belum tertagih > 90 hari (porsi dari total AR)` | Piutang paling macet. Yang dinilai porsi yang MASIH tertunggak di atas 90 hari — makin kecil makin baik. | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: kinerja_ar, metrik: piutang_lewat_90_persen, formula: rata_rata, target: 5, arah: turun, scope: individu, target_per_karyawan: 1 orang}` (`kpi_sumber_ar.go:219-232`). Bergantung field `lebih90`, yang menurut komentar berkasnya baru terkirim `/piutang/tren` sejak endpoint itu diperbarui; cache Redis 10 menit di sisi integration-service. | Sudah berangka, tidak perlu pekerjaan dev. |

> ⚠️ **`>60 hari` dan `>90 hari` adalah himpunan BERSARANG, bukan dua populasi sejajar** (`kpi_sumber_ar.go:50-71`: bucket `Lebih90` adalah bagian dari `Lebih60`, ditulis eksplisit di komentar `barisTrenPiutang`). Menilai keduanya sebagai metrik terpisah berbobot 0,30 dan 0,50 berarti piutang yang paling tua ikut menyumbang ke kedua penilaian sekaligus. Sumbernya sendiri mendokumentasikan pola ini sebagai pasangan yang mestinya dibaca bersama (komentar `piutang_61_90_persen`, metrik itu sendiri tidak dipakai template ini). **TBD pemilik metrik**: apakah bobot 0,30/0,50 sudah mempertimbangkan efek itu.

#### KPI AR Piutang

Template `KPI AR Piutang`, 4 metrik.

> ⚠️ **Label dan deskripsi baris 1 dan 3 TERTUKAR dibanding snapshot 2026-08-01** (key metriknya tetap sama). Yang dulu berisi angka target sebagai label kini berisi frasa proses, dan sebaliknya, pola yang sama dengan perubahan di `KPI Supervisor Finance` dan `KPI Cost Control` di bawah.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Proses AR & Cash Collection Harian` | Penagihan > 60 hari sampai < 5%  dari total AR | Accurate live proxy: GET /accounting/receivables + GET /orders/piutang/summary. Sumber `kinerja_ar`/`piutang_lewat_60_persen` sudah ber-`auto` di template sebelah (**AR Staff 2026**), tapi template ini sendiri masih `auto=0`. | Bisa otomatis sekarang, persis seperti AR Staff 2026. Belum disatukan; dua template menilai fakta yang sama untuk populasi AR Staff yang tumpang tindih. TBD pemilik. |
| 0.4 | `Pencatatan Piutang ` | Input data piutang (Uang masuk) max laporan inputan piutang bulanan selesai tanggal 3 bulan berikutnya | Accurate live proxy: GET /accounting/receivables + GET /orders/piutang/summary. | Bisa otomatis sekarang. Data piutang diambil langsung dari Accurate. |
| 0.25 | `Proses AR & Cash Collection Harian dengan Max 5% piutang belum tertagih lebih dari  14 hari` | Penagihan piutang > 14 hari  sampai < 5% dari total AR | Accurate live proxy: GET /accounting/receivables + GET /orders/piutang/summary. Sumber `kinerja_ar`/`piutang_lewat_14_persen` sudah ber-`auto` di template sebelah (**AR Staff 2026**). | Bisa otomatis sekarang, persis seperti AR Staff 2026. Belum disatukan. TBD pemilik. |
| 0.1 | `Minimal 5 ide inovasi baru dari  tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses  AR dengan minimal 2 ide terdaftar perbulan | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |

#### KPI AR Retur

Template `KPI AR Retur`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Penanganan retur di platform  atau Expedisi` | Proses foll up retur lebih dari 14 hari dengan maksimal 5% retur | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: kinerja_ar, metrik: retur_lewat_14_persen, formula: rata_rata, target: 5, arah: turun, scope: department}` (`services/employee/kpi_sumber_ar.go:435`, fungsi `cuplikanReturLewat14`). Data dari `GET /accurate/daily-returns/kpi/penanganan`. | ✅ Sudah berangka, tidak perlu pekerjaan dev. ⚠️ `scope: department` di sini **KOSMETIK juga**: `DaftarkanScopeSumber` dikunci PER SUMBER, bukan per metrik (`kpi_sumber.go:211-231`, kunci peta `scopeTerdaftar[nama]`), dan `init()` sumber `kinerja_ar` (`kpi_sumber_ar.go:307-315`) tak pernah memanggilnya sama sekali. Baku jatuh ke `individu` untuk SELURUH metrik sumber ini, termasuk retur, persis alasan yang sama dengan F1/F3/F4 Supervisor Finance di bawah. |
| 0.5 | `Pencatatan retur penjualan` | Input data retur dengan max laporan inputan retur bulanan  selesai tanggal 3 bulan berikutnya | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: kinerja_ar, metrik: retur_tuntas_cutoff_persen, formula: rata_rata, target: 90, arah: naik, scope: department}` (`kpi_sumber_ar.go:445`, fungsi `cuplikanReturTuntasCutoffPadaWaktu`). Cakupan metrik ini DITURUNKAN otomatis selagi tenggat tutup buku bulan itu belum lewat (`kpi_sumber_ar.go:603-626`, `cakupanTuntasCutoffBerjalan`), sehingga bulan berjalan wajar tampil `semi`. | ✅ Sudah berangka, tidak perlu pekerjaan dev. |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses AR minimal 2 ide terdaftar perbulan | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV / Leader | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

### AR Staff

Template `KPI Sales Admin`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.5 | `Pencatatan Penjualan` | Input data penjualan dengan max laporan inputan penjualan bulanan  selesai tanggal 3 bulan berikutnya | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: kinerja_sales_admin, metrik: penjualan_tuntas_cutoff_persen, formula: rata_rata, target: 100, arah: naik, scope: department}` (`services/employee/kpi_sumber_sales_admin.go:23,34`). Menarik `GET /accurate/daily-invoices/kpi/pencatatan`, sepasang dengan `MetrikReturTuntasCutoff` (rumus dan arah identik, satuannya faktur harian bukan retur). ⚠️ **Catatan lama "PR #1254 belum merge" SUDAH USANG** dan PR itu sudah merge; jangan menunggu PR ini lagi. `scope: department` di sini juga tak berpengaruh (sumber tak mendaftar `DaftarkanScopeSumber`, lihat catatan `kinerja_ar` di baris di atas untuk mekanismenya). | ✅ Sudah berangka, tidak perlu pekerjaan dev. |
| 0.3 | `Rekonsiliasi stok penjualan` | Rekonsiliasi data stok terjual dengan data pengiriman gudang dengan Max laporan rekonsiliasi stok selesai tanggal 3 bulan berikutnya | Accurate live proxy + GET /transactions/reconciliation dan /reconciliation/missing. accurate_bank_accounts (44). | Bisa sebagian. Alat pencocokan data sudah ada, tapi perlu disepakati dulu apa yang dihitung sebagai selisih dan kapan batas waktunya. |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses AR Minimal 2 ide inovasi terdaftar perbulan | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV / Leader | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

#### AR STAFF PIUTANG (arsip 2026-08-25)

Template `AR STAFF PIUTANG`, 5 metrik, diarsipkan 2026-08-25. Isinya sudah pernah tercatat sebagai salinan 2026-08-01 di versi lama dokumen ini (2 metrik ber-`auto`: `piutang_lewat_60_persen` dan `piutang_lewat_14_persen`, keduanya sudah digantikan cakupannya oleh **AR Staff 2026** dan **KPI AR Piutang** di atas). Tidak ditulis ulang tabelnya di sini karena tidak ada penetapan aktif yang memakainya per 2026-09-12 (fakta §7).

### Account Payable

Template `KPI Finance Staff Account Payable`, 6 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Cashflow terpantau 100% setiap minggu, operating cashflow ≥ 100%` | Mengecek expense dari cost control sesuai anggaran | Budget TIDAK tersimpan di ERP mana pun. Realisasi ada di Accurate; perlu master anggaran lebih dulu. | Belum bisa otomatis. Pengeluarannya sudah tercatat, tapi anggarannya belum pernah dimasukkan ke sistem, jadi tidak ada yang bisa dibandingkan. |
| 0.2 | `100% pembayaran dan pengeluaran sesuai rencana cashflow` | Memvalidasi dan mencatat pengeluaran operasional sebelum dibayarkan | ~~Accurate live proxy P&L~~ **Koreksi 2026-08-12**: redefinisi jadi "% faktur dibayar tepat waktu vs `dueDate`", sumbernya `purchase-invoice/list.do` (field `lastPaymentDate`, terbukti lewat probe live — 94,1% faktur Lunas punya tanggalnya, 5,9% lunas via alokasi DP dikecualikan). | 🟡 **Sedang dibangun** — sumber `kinerja_ap` di [[Microservices - Procurement Service]] + [[Microservices - Employee Service]], PR [#1178](https://github.com/bip-itteam-internal/bip-erp/pull/1178) belum merge, belum dikonfigurasi ke `kpi_template`. |
| 0.2 | `Perhitungan harga pokok produksi (HPP)` | Costing HPP 95% valid dengan realisasi costing max 1 hari setelah permintaan | **Koreksi 2026-08-12**: `/profit/costing-ratio` menjawab (486/486 SKU produksi punya HPP) tapi **selalu 100% dan tak ber-periode** — nilainya identik tiap bulan, dan separuh definisinya ("realisasi costing max 1 hari setelah permintaan") tak punya sumber sama sekali. | ⚠️ **Tetap perlu definisi ulang**, bukan "bisa otomatis sekarang" — metrik berbobot besar yang tak pernah bergerak tidak mengukur apa pun (pola sama `uptime` sebelum dibalik jadi `downtime`). |
| 0.15 | `Minimal ide inovasi baru dari tim pada setiap quartal` | Mengidentifikasi peluang inovasi di proses finance minimal 1 ide inovasi terdaftar per bulan | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
| 0.1 | `Laporan credit team dibuat 100% tepat waktu dan terdokumentasi` | Menyusun laporan credit term berdasarkan data valid selesai tepat waktu setiap bulan | **Koreksi 2026-08-12**: `term_name`/`due_date` memang lengkap 2.055/2.055 di `procurement_db.faktur_pembelian`, tapi KPI-nya mengukur **penyerahan laporan**, bukan datanya — tak ada jejak kapan laporan diserahkan. | ⚠️ **Tetap perlu definisi ulang**. Data yang disebut kolom sebelumnya memang ada, tapi bukan data yang dibutuhkan metrik ini. |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

> ⚠️ **Dua sumber KPI untuk Account Payable SUDAH ADA di kode tapi BELUM dipasang ke template ini.** Keduanya terdaftar dan lolos katalog (`DaftarkanGrupSumber(..., GrupSumberFinance)`), tetapi tidak ada satu pun metrik di `KPI Finance Staff Account Payable` yang mengarah ke sana per 2026-09-12.
>
> - **`realisasi_ap`** (`services/employee/kpi_sumber_realisasi_ap.go:16-37`): tiga metrik, `pembayaran_30menit_persen` (menjawab baris sheet berbobot 40), `ketepatan_nominal_persen` (50), `bukti_terunggah_persen` (10, "membuat bukti transaksi untuk requester dan arsip"; pembilangnya bukti TERUNGGAH bukan bukti DISETUJUI, `kpi_sumber_realisasi_ap.go:34-37`). Ambang "30 menit" adalah `ambangMenitBawaan = 30` di `services/procurement/kpi_realisasi_ap.go:114-120`, dan komentarnya eksplisit: angka itu dari sheet KPI, bukan hasil pengukuran sistem.
> - **`kinerja_ap`** (`services/employee/kpi_sumber_ap.go:31,36`): satu metrik, `pembayaran_tepat_waktu_persen`, mengukur ketepatan waktu pembayaran FAKTUR VENDOR terhadap `dueDate` (BEDA populasi dari `realisasi_ap`, yang mengukur pengajuan internal; komentarnya eksplisit memperingatkan agar keduanya tak dipakai saling gantikan, `kpi_sumber_realisasi_ap.go:19-23`).
>
> Bobot sheet 40/50/10 milik `realisasi_ap` **tidak cocok** dengan struktur 6 metrik template aktif prod (25/20/20/15/10/10): ini terbaca sebagai matriks KPI generasi baru yang belum dimuat ke `kpi_template`, bukan tambahan ke matriks lama. **TBD pemilik/HR**: apakah `KPI Finance Staff Account Payable` akan diganti total oleh matriks baru ini (pola yang sama dengan AR Staff, dari 4 template lama ke `AR Staff 2026`), atau kedua sumber ini dipasang sebagian ke metrik existing. Data sumbernya sendiri kosong di prod per 2026-09-12 (`procurement_db.pembayaran` 0 dokumen, fakta §9), jadi konektor ini belum bisa diverifikasi ujung-ke-ujung sekalipun dipasang.

### Cost Control

Template `KPI Cost Control`, 7 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
> ⚠️ **Label dan deskripsi baris 2, 3, 4, dan 5 berubah dibanding snapshot 2026-08-01** (template diperbarui 2026-08-29). Pola serupa `KPI AR Piutang` di atas: baris 2 dan 4 TERTUKAR (label lama jadi deskripsi baru dan sebaliknya), baris 3 dan 5 ditulis ulang dengan target yang lebih konkret di deskripsi. Baris 1, 6, 7 label tak berubah, hanya deskripsi baris 6 dan 7 yang diperjelas.

| 0.2 | `Varians antara budget vs realisasi OPEX ≤ ±5%` | Review Cash Outflow Mingguan - Realisasi OPEX dalam batas ±5% dari budget | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: varians_anggaran, metrik: varians_absolut_persen, formula: rata_rata, target: 5, arah: turun, scope: department}`. ⛔ **`scope: department` di sini adalah nilai LAMA yang tak lagi didukung**, dan tetap TIDAK berpengaruh terhadap angkanya. `init()` sumber ini mendaftarkan cakupannya HANYA `perusahaan` (`kpi_sumber_varians_anggaran.go:372-379`, `DaftarkanScopeSumber(SumberVariansAnggaran, Perusahaan, Perusahaan)`, satu-satunya nilai yang didukung), tetapi pendaftaran itu cuma metadata untuk dropdown UI, bukan penjaga config tersimpan; `cuplikanVarians` (`kpi_sumber_varians_anggaran.go:335-367`) sendiri tidak pernah membaca `k.Cfg.Scope` sama sekali dan tidak pernah menyisipkan parameter departemen ke `GET /accounting/anggaran/varians`, terlepas dari nilai `scope` di konfigurasi manapun; dikunci test `TestCuplikanVarians_TanpaParameterDepartemenDiURL`. Jadi baris ini dan F2 Supervisor Finance (yang ber-`scope: perusahaan`, nilai yang kini didukung) membaca angka OPEX SELURUH PERUSAHAAN yang sama persis pada periode yang sama. | ✅ Sudah berangka, tidak perlu pekerjaan dev. Realisasinya akan SELALU sama dengan F2 Supervisor Finance pada periode yang sama; jangan menganggap keduanya independen saat membaca dua skor berdampingan. TBD HR: nilai `scope: department` yang tertulis di template ini sendiri layak diperbarui jadi `perusahaan` supaya tak menyesatkan pembaca layar Atur Target. |
| 0.1 | `Analisis biaya berulang dan rekomendasi perbaikan` | Penurunan biaya admin/non operasional minimal 2% YoY | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.2 | `Melakukan Analisis Varians OPEX dengan minimal 3 rekomendasi efisiensi cost driver setiap bulan` | Minimal 3 rekomendasi efisiensi cost driver setiap bulan | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.15 | `Analisis Deviasi Forecast vs Aktual` | Akurasi cashflow forecast ≥ 95%. | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: forecast_kas, metrik: akurasi_forecast_kas, formula: jumlah_nilai, target: 95, arah: naik, scope: individu}` (`services/employee/kpi_sumber_forecast_kas.go:29,66-97`), menarik `GET /accounting/anggaran/mingguan/kpi` dari [[Microservices - Integration Service]]. ⚠️ **`formula: jumlah_nilai` di sini, `rata_rata` di F4 Supervisor Finance untuk sumber yang sama** (lihat catatan F4 di bawah): keduanya menghitung Cuplikan berisi SATU nilai (`Populasi: 1`, `kpi_sumber_forecast_kas.go:134-142`), dan `employee.Reduksi` (`shared-library/models/employee/kpi_reduksi.go:132-186`) menjumlah/merata-ratakan array satu-elemen menjadi angka yang SAMA persis untuk kedua rumus itu; hanya kalimat basisnya ("jumlah X dari 1 unit" vs "rata-rata X") yang berbeda. **Bukan bug, tapi TBD gaya**: kenapa dua template ditulis dengan formula berbeda untuk hasil yang identik. | ✅ Sudah berangka, tidak perlu pekerjaan dev. `akurasi_terdefinisi=false` digalatkan, bukan nol (`kpi_sumber_forecast_kas.go:68-96`); verifikasi lewat `GET /accounting/anggaran/mingguan/kpi?tahun=2026&bulan=<N>`. |
| 0.2 | `Akurasi Distribusi kas iklan dan pencatatan` | 100% distribusi kas iklan tepat jumlah dan tepat waktu | Accurate live proxy + GET /transactions/reconciliation dan /reconciliation/missing. accurate_bank_accounts (44). | Bisa sebagian. Alat pencocokan data sudah ada, tapi perlu disepakati dulu apa yang dihitung sebagai selisih dan kapan batas waktunya. |
| 0.1 | `Minimal 5 ide inovasi baru dari tim` | Minimal 1 ide inovasi terdaftar perbulan di Q1 | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
| 0.05 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | 100% staf mengikuti minimal 1 sesi per bulan | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

### Finance Supervisor

Template `KPI Supervisor Finance`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Monitoring AR & Collection: piutang belum tertagih > 60 hari (porsi dari total AR)` | Mengurangi piutang aging > 60 hari sampai < 5% dari total AR. | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: kinerja_ar, metrik: piutang_lewat_60_persen, formula: rata_rata, target: 5, arah: turun, scope: individu}` (`services/employee/kpi_sumber_ar.go:35,188-190`). Konfigurasi identik dengan **AR Staff 2026**. ⚠️ Label lama (arsip) menyebut "< 5% dari total AR." sebagai label; label saat ini di prod sudah ditulis ulang seperti kolom ini. | ✅ Sudah berangka, tidak perlu pekerjaan dev. ⚠️ Angkanya akan **sama persis dengan AR Staff**: `kinerja_ar` menarik piutang se-perusahaan tanpa parameter departemen. ⚠️ **`scope` di sini KOSMETIK**, lihat catatan cakupan di bawah tabel. |
| 0.25 | `Kontrol OPEX dengan Budget Compliance 95% (Varians antara budget vs realisasi OPEX ≤ ±5%)` | Varians antara budget vs realisasi OPEX ≤ ±5%. | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: varians_anggaran, metrik: varians_absolut_persen, formula: rata_rata, target: 5, arah: turun, scope: perusahaan}`. ⛔ **Ralat 2026-09-12 atas catatan 2026-08-31 di bawah.** Label lama "Rasio EBITDA 45%" sudah diganti label di atas. | ✅ Sudah berangka (mengukur OPEX SELURUH PERUSAHAAN, bukan Finance saja; `scope: perusahaan` cocok dengan perilaku kodenya, beda dari F1/F3/F4 yang menulis `individu`/`department` padahal sama-sama diabaikan kodenya). Realisasinya akan **SAMA PERSIS** dengan Cost Control baris 1 (`varians_absolut_persen`, tabel Cost Control di atas) pada periode yang sama, sumber dan periodenya identik. |
| 0.2 | `Kontrol Beban Non-Operasional` | Kontrol Beban Non-Operasional ≤ 2% | ⚠️ **Ralat 2026-08-31.** Klaim lama *"bisa otomatis sekarang"* menyesatkan: proxy Accurate memang ada, tapi **tak ada satu pun metrik KPI yang menghitung rasio itu** sampai 31 Agustus 2026. Pembilangnya sudah lama ada (3 akun `DaftarAkunAdminNonOps`, tersalin harian); **penyebutnya tidak pernah ditentukan** — "≤ 2% dari APA" adalah pertanyaan yang baru dijawab sekarang. Metrik `admin_non_ops/penurunan_yoy_persen` yang sudah ada **bukan** jawabannya (ia mengukur penurunan terhadap baseline tahun lalu, bukan rasio terhadap pendapatan). PR [bip-erp#1548](https://github.com/bip-itteam-internal/bip-erp/pull/1548) (`fea804a7`) + [erp-frontend#1332](https://github.com/bip-itteam-internal/erp-frontend/pull/1332) (`de1f24ea`) **SUDAH merge** ke `origin/main` masing-masing repo, 31 Agustus 2026. | ⚠️ **Sudah dinyalakan** (terpasang `{sumber: admin_non_ops, metrik: rasio_beban_non_ops_persen, formula: rata_rata, target: 2, arah: turun, scope: individu}`, arah turun BENAR untuk "≤ 2%"). Status galat `INTEGRATION_SERVICE_KEY belum diatur` **belum diverifikasi ulang 2026-09-12** (terakhir diukur 2026-08-31); TBD ukur ulang sebelum dipakai. Keputusan SPV: penyebut = pendapatan periode itu sendiri, dari baris top-total `GET /accounting/profit-loss`. ⚠️ `scope` di sini **KOSMETIK**. |
| 0.1 | `Cashflow Forecasting` | Cashflow Forecasting mingguan dengan akurasi ≥ 95%. | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: forecast_kas, metrik: akurasi_forecast_kas, formula: rata_rata, target: 95, arah: naik, scope: individu}`. ✅ **Arahnya SUDAH DIBETULKAN** (label lama "Return on Operation = 2,75" yang membingungkan dua penilaian juga sudah diganti label di atas, sehingga baris ini kini murni mengukur satu hal: akurasi forecast kas). Kronologi bug arah terbalik (100/100 untuk akurasi 38,03%) ada di [[HRIS - Otomasi Skor KPI]] §"Kesalahan arah F4"; pelajaran umum di [[RUN - Menambah Metrik KPI Otomatis]] §"Arah mengikuti BUNYI KPI-nya". | ✅ Sudah berangka dan arahnya benar. ⚠️ Angkanya akan **identik dengan Cost Control baris 4** (`akurasi_forecast_kas`, tabel Cost Control di atas): sumber sama, formula BEDA (`rata_rata` di sini vs `jumlah_nilai` di Cost Control) tapi hasilnya SAMA PERSIS karena Cuplikan sumber ini selalu berisi satu nilai (lihat catatan formula di baris Cost Control). ⚠️ `scope` **KOSMETIK**. |
| 0.2 | `Performance Monitoring Team` | KPI Tim minimal skor 70 (HIT/MISS) | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: skor_tim, formula: rata_rata, target: 80, arah: naik, hit_miss: true, scope: department}`. ⛔ **Target berubah dari 70 (masih tertulis di deskripsi) jadi 80 di konfigurasi, dan `hit_miss: true` baru ditambahkan.** **TBD pemilik metrik**: mana yang benar. ⚠️ **Konsekuensi `hit_miss: true` bukan kosmetik**: `NilaiBiner` (`kpi_team.go:149-153`, `shared-library/models/employee/kpi_reduksi.go:281-292`) melewati gradien sama sekali: realisasi 79 dengan target 80 arah naik bernilai **0**, bukan 98,75 seperti bila memakai `NilaiDenganArah` biasa. Sebelumnya (sampai 2026-08-31) F5 belum pernah berangka sama sekali; per Agustus 2026 fakta menunjukkan F5 SUDAH menghasilkan `auto_value` (lihat subbagian Penilaian 2026 di akhir bab Finance), jadi gerbang biner ini sudah aktif menilai. | ✅ Sudah berangka. F5 tetap hidup dari BAWAH, lihat catatan cakupan & urutan penilaian di bawah tabel; menyentuh konfigurasi F5 sendiri tidak mengubah kapan ia terisi. |

> ⛔ **Metrik 0,25 di atas SEMPAT tercatat di sini sebagai `Revenue 240M` dengan sumber GMV TikTok + `mart_profit_attribution`, dan itu SALAH.** Labelnya salah isi dari HR; deskripsinya sejak awal berbunyi piutang, bukan omzet, dan produksi sudah membetulkan labelnya. Kunci metriknya tetap `revenue-240m` karena `key` memang identitas stabil yang tak boleh diganti, jadi siapa pun yang membedah Mongo akan menemukan token yang menyebut revenue untuk metrik yang mengukur piutang. **Jangan mengembalikan baris ini ke sumber omzet.**
>
> Kelas kesalahannya persis yang diperingatkan Langkah 1 di [[RUN - Menambah Metrik KPI Otomatis]]: label dan deskripsi yang menyebut dua hal berbeda, lalu yang membaca dokumen memilih yang salah satu. Yang menentukan bukan labelnya melainkan **apa yang benar-benar terpasang di `kpi_template` produksi**.

#### ⚠️ `scope` pada F1–F4 tidak mengubah angka apa pun (dan F2 sudah kembali ke keadaan itu; F5 BEDA, lihat subbab berikutnya)

Ketiga sumber di balik F1, F3, F4 — `kinerja_ar`, `admin_non_ops`, `forecast_kas` — **tidak memanggil `DaftarkanScopeSumber` dan tidak menyentuh `k.Karyawan` sama sekali** (dicacah 2026-08-31 ke `main`: nol kemunculan di ketiganya; bandingkan `kpi_sumber_cost_control.go` yang punya satu). `kpi_sumber.go:176` menyatakan sumber yang tak mendaftarkan cakupan **dianggap mengabaikan cakupan**, dengan baku jatuh ke `individu`.

Artinya `scope` yang tertulis di konfigurasi **tersimpan sah tetapi tidak menyaring apa pun** untuk ketiganya: angkanya se-perusahaan, sama untuk siapa pun yang dinilai. Buta-departemen ini **DISENGAJA**, komentar kepala tiap berkas menyebut alasannya (AR: seluruh toko dikelola bersama tim AR Sales dan endpoint sumbernya tak punya dimensi karyawan; `forecast_kas` & `admin_non_ops`: keduanya lahir untuk memasok metrik KPI **Cost Control**). Jadi ini **bukan cacat yang perlu diperbaiki**. Yang dicatat di sini agar orang berikutnya tidak mengira datanya sudah disaring per departemen padahal tidak.

⚠️ **Konsekuensi yang perlu disadari**: karena F3 dan F4 memakai sumber yang komentar kepalanya menyatakan diri memasok metrik **Cost Control**, SPV Finance dinilai atas **angka yang identik dengan Cost Control** untuk dua metrik. Hal yang sama berlaku antara F1 dan AR Staff / AR Staff 2026. Sah secara mesin; keputusan apakah itu yang dikehendaki ada di pemilik metrik (**TBD**).

> ⛔ **Ralat 2026-09-12 atas seluruh subbab ini.** Catatan 2026-08-31 di bawah menyatakan F2 (`varians_anggaran`) **satu-satunya dari lima yang benar-benar per-departemen**, sejak PR#1546 (`d5d50ff3`) menambahkan parameter `&departemen=`. **Itu TIDAK LAGI BENAR pada kode yang dibaca 2026-09-12.** `cuplikanVarians` (`services/employee/kpi_sumber_varians_anggaran.go:335-367`) TIDAK mengirim parameter departemen sama sekali, dikunci test `TestCuplikanVarians_TanpaParameterDepartemenDiURL` (`kpi_sumber_varians_anggaran_test.go:225-251`), dan komentar berkasnya (baris 348-360) menjelaskan alasannya secara eksplisit: nilai departemen yang benar-benar ada di baris anggaran hanyalah `""` (56 baris), `UMUM`, dan varian `MARKETING - *`, `"FINANCE"` tak pernah muncul, sehingga menyempitkan berdasar departemen karyawan membuat filter SELALU jatuh ke nol baris (persis galat "total anggaran periode ini nol" yang tercatat di ralat lama). Konfigurasi templatenya sendiri sudah mengikuti perubahan ini: fakta prod 2026-09-12 mencatat F2 ber-`scope: perusahaan`, bukan `department`. **Belum diketahui KAPAN reversion ini terjadi** (antara 31 Agustus dan 12 September 2026); tidak ada commit hash yang bisa dikutip dari snapshot kode yang dibaca sesi ini. Sekarang **F1–F4 sama-sama tidak tersaring per departemen** oleh kode, walau `scope` yang tertulis di konfigurasi berbeda-beda (`individu`/`department`/`perusahaan`). **F5 (`skor_tim`) BEDA**: sumbernya memanggil `DaftarkanScopeSumber` dan `DaftarkanScopePengaruh` (`kpi_auto.go:405-406`), jadi `scope: department` pada F5 **sungguhan menentukan** anggota mana yang skornya dirata-rata, bukan kosmetik seperti F1-F4.

Catatan historis (2026-08-31, tidak lagi berlaku untuk F2, dipertahankan sebagai jejak): F2 sempat dianggap "buta-departemen, lalu diperbaiki PR#1546 (`d5d50ff3`, 31 Agustus 2026)", dengan penanda "Individu" pada layar Atur Target yang juga tak berpengaruh karena penyempitannya "dipaksakan tanpa syarat di kode terlepas dari `cfg.Scope`". Rantai penjelasan itu sudah usang seluruhnya sejak F2 kembali company-wide; jangan mengutipnya sebagai keadaan kode saat ini.

⚠️ **Konsekuensi yang berlaku untuk keempatnya (F1-F4)**: layar Atur Target menawarkan pilihan scope yang **tidak mengubah apa pun** pada baris-baris itu. Itu jebakan tampilan, bukan cacat perhitungan. **Jangan mengubah nilai scope untuk "memperbaikinya"**, mengubah nilai yang tak berpengaruh menambah risiko tulisan tanpa manfaat, dan `individu` adalah nilai yang sah menurut `ValidateKPIAutoConfig` (`kpi_source.go:183-188`).

#### ⚠️ F5: dua arah yang berbeda, dan kenapa angkanya masih kosong

> **Pembaruan 2026-09-12**: skor Agustus 2026 Supervisor Finance di prod sudah memuat `auto_value` untuk **kelima** metrik, termasuk F5 (lihat subbagian Penilaian 2026 di akhir bab Finance). Penjelasan di bawah tetap berlaku sebagai mekanisme kapan F5 bisa kosong, tetapi judul "masih kosong" menggambarkan keadaan 2026-08-31.

Ada **dua aliran** pada KPI, untuk hal yang berbeda, dan keduanya sama-sama berlaku:

| Yang mengalir | Arah | Mekanismenya |
|---|---|---|
| **Target** | SPV → staf (breakdown) | `KPIAutoConfig.TargetPerKaryawan` (`kpi_source.go:100-114`) — tiga lapis: `Target` umum, `TargetPerPeriode` per bulan, `TargetPerKaryawan` per orang; dipilih `employee.TargetBerlaku(cfg, periode, employeeID)` |
| **Skor** | staf → SPV (rata-rata) | sumber `skor_tim` (`kpi_auto.go:243-304`) merata-ratakan skor anggota departemen |

F5 memakai aliran kedua. Kenapa ia masih kosong padahal konfigurasinya sudah menyala:

1. **Bulan berjalan punya fallback.** `kpi_auto.go:281-298` mengisi anggota yang skornya belum tersimpan dengan **usulan penuh-otomatisnya**, supaya KPI Team tak kosong sepanjang bulan. Jadi pada bulan berjalan F5 **tidak** harus menunggu penilaian manual.
2. **Tapi fallback itu bergerbang penuh.** Ia memanggil `kumpulkanOtomatisPenuh` → `kumpulkanOtomatis(izinkanParsial=false)` → `seluruhMetrikOtomatis(tpl)` (`kpi_finalisasi.go:205,451`). Satu saja metrik template staf yang `Auto == nil` membuat orang itu **dilewati sebelum satu pun sumber dipanggil**. Gerbangnya **biner**: menyalakan tiga dari empat metrik AR Staff menyumbang **nol** ke F5, persis sama dengan menyalakan nol.
3. **Karena itu F5 hidup dari BAWAH.** Yang bernilai bukan "sebanyak mungkin metrik dinyalakan", melainkan **paling sedikit satu posisi staf Finance yang templatenya 100% ber-`auto`**. Satu posisi tuntas mengalahkan lima posisi setengah jalan.
4. ⛔ **Untuk BULAN LAMPAU fallback tidak jalan sama sekali** — skor tim hanya dari skor final anggota. Dan snapshot `kpi_score` **dibekukan begitu `POST /kpi` tersimpan**, jadi menilai SPV terlalu cepat menghasilkan angka yang tak bisa diperbaiki tanpa menilai ulang periode itu. **Urutannya mengikat: anggota → Leader → Supervisor.** Yang harus mengisi adalah **atasan langsung anggota Finance**, bukan "sistem menunggu data".

Analisis lengkap posisi-per-posisi staf Finance ada di `scripts/kpi-staf-finance/LAPORAN-otomasi-staf-finance.md` (bip-erp, branch `bip-erp/t_15263a7a-…`, commit `5b12a6a4`).

#### Langit-langit skor SPV Finance, dengan hitungannya

Skor total **TIDAK dinormalisasi** (`kpi_auto_scores.go:130-146`, dan alasannya ditulis panjang di komentar: menormalisasi ke metrik yang menyala membuat KPI yang baru mulai tampak sudah tercapai penuh). Jadi langit-langitnya = **Σ bobot metrik yang menyala × 100**.

| Keadaan | Metrik menyala | Σ bobot | Langit-langit |
|---|---|---:|---:|
| **Hari ini (2026-08-31)** — F2 & F3 menyala tapi bergalat, F5 menyala tapi belum berangka | F1 + F4 | 0,25 + 0,10 = **0,35** | **35** |
| + F5 berangka (staf Finance berotomasi penuh) | F1 + F4 + F5 | 0,55 | 55 |
| + anggaran Finance diunggah (F2) & `INTEGRATION_SERVICE_KEY` terpasang (F3) | F1 + F2 + F3 + F4 + F5 | 1,00 | 100 |

⛔ **Langit-langit itu mengukur CAKUPAN, bukan kebenaran.** Angka 35 hari ini sudah termasuk F4 yang **nilainya salah** (100, seharusnya 40) — sepuluh poin penuh untuk metrik yang seharusnya menyumbang empat. Memperbaiki arahnya **menurunkan** skor SPV 6 poin tanpa mengubah langit-langitnya sedikit pun.

Bobot produksi terkonfirmasi cocok dengan tabel di atas (layar Atur Target 2026-08-31: F2 25%, F3 20%, F4 10%, F5 20%, sisanya F1 25% → Σ = 1,00), sehingga `ValidateKPIMetrics` (toleransi 1e-9) aman.

> **Pembaruan 2026-09-12**: tabel langit-langit di atas adalah keadaan 2026-08-31. Diukur prod 2026-09-12, kelima metrik terpasang dan skor Agustus 2026 memuat `auto_value` untuk kelimanya (5 dari 5), dengan total **36,8** (Juli 2026, dinilai manual: 79,7). Karena seluruh bobot kini menyala, langit-langit teoretisnya 100; angka 36,8 berasal dari nilai per metrik, dan rincian per metriknya belum ditelusuri sesi ini (**TBD**). Arah F4 sudah `naik`, jadi catatan "nilainya salah (100, seharusnya 40)" di atas tidak lagi berlaku untuk konfigurasi terkini.

### Junior Accountant

Template `KPI Accounting CV`, 6 metrik.

| Bobot | Label                                                                 | Target / keterangan                                                                                                                                                                 | Sumber di sistem erp                                                                                                                                  | Rekomendasi                                                                                                                           |
| ----: | --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
|   0.3 | `Laporan keuangan`                                                    | Menyusun laporan keuangan dengan persentase laporan keuangan secara akurat dan tepat waktu max tgl 4 bulan berikutnya                                                               | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini.                                                 |
|  0.25 | `Pengelolaan kas`                                                     | Melakukan rekonsiliasi bank dan pencatatan kas laporan keuangan dengan Presentase selisih antara laporan keuangan perusahaan dengan rekening koran setiap bulan (Target 0% selisih) | Accurate live proxy + GET /transactions/reconciliation dan /reconciliation/missing. accurate_bank_accounts (44).                                      | Bisa sebagian. Alat pencocokan data sudah ada, tapi perlu disepakati dulu apa yang dihitung sebagai selisih dan kapan batas waktunya. |
|  0.15 | `Pengelolaan asset/perlengkapan`                                      | Pengecekan dan depresiasi asset dengan Presentase aset dan perlengkapan tercatat secara akurat dan tepat waktu max tgl 4 bulan berikutnya                                           | manufacture_resi (328.272) + warehouse_db.fulfillment_orders (38.949, event pick/pack/handover).                                                      | Bisa otomatis sekarang. Data resi dan proses gudang sudah tercatat lengkap.                                                           |
|   0.1 | `Pajak`                                                               | Pajak terbayar tepat waktu dengan persentase pajak perusahaan dan karyawan terbayar tepat waktu (max 1 hari sebelum jatuh tempo)                                                    | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets.                                                       | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate.                                                |
|   0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal`             | Mengidentifikasi peluang inovasi di proses accounting dengan Minimal 2 ide inovasi terdaftar perbulan di tiap kuartal                                                               | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
|   0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV                                                                                                                    | TIDAK ADA log 1-on-1. Perlu fitur baru.                                                                                                               | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah.                                                     |

### Junior Accountant

Template `KPI Accounting PT`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.35 | `Transaksi Keuangan` | Akurasi & ketepatan waktu pencatatan transaksi keuangan | Accurate live proxy + GET /transactions/reconciliation dan /reconciliation/missing. accurate_bank_accounts (44). | Bisa sebagian. Alat pencocokan data sudah ada, tapi perlu disepakati dulu apa yang dihitung sebagai selisih dan kapan batas waktunya. |
| 0.35 | `Transaksi Non-keuangan` | Akurasi & ketepatan waktu pencatatan transaksi non-keuangan | Accurate live proxy + GET /transactions/reconciliation dan /reconciliation/missing. accurate_bank_accounts (44). | Bisa sebagian. Alat pencocokan data sudah ada, tapi perlu disepakati dulu apa yang dihitung sebagai selisih dan kapan batas waktunya. |
| 0.15 | `Minimal 5 ide inovasi baru dari tim pada Q1` | Mengidentifikasi peluang inovasi di proses accounting | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
| 0.15 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

### Senior Accountant

Senior Accountant memegang **dua template aktif sekaligus**, masing-masing dengan satu penetapan (diukur prod 2026-09-12): **KPI SENIOR ACCOUNTING UPDATE** (baru, 3 metrik ceklis, seluruhnya ber-`auto`) dan **KPI Senior Accounting Bharata** (lama, 8 metrik manual). Skor terakhir yang tersimpan (Juli 2026, 65,0) masih memakai template lama. **TBD pemilik/HR**: arsipkan salah satu, supaya tidak ada dua sumber penilaian untuk satu orang.

#### KPI SENIOR ACCOUNTING UPDATE (baru, 2026-09-02)

Template `KPI SENIOR ACCOUNTING UPDATE`, 3 metrik, seluruhnya ber-`auto` dari sumber `ceklis_kpi`.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.60 | `Menyusun laporan keuangan secara akurat` | 100 % Laporan keuangan akurat | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: ceklis_kpi, metrik: <UID butir form-builder>, formula: rata_rata, target: 100, arah: naik, hit_miss: true, scope: individu}`. Sumber `ceklis_kpi` (`services/employee/kpi_sumber_ceklis.go:16-39`) menilai lewat ceklis sudah/belum di form-builder, diisi tanggal 1 sampai 5 oleh Internal Audit (laporan) dan SPV FAT (arsip); `metrik` berisi UID butir, bukan judul atau urutan pertanyaan. | Sudah otomatis dari ceklis; pekerjaannya ada di penilai yang mengisi ceklis tiap awal bulan. ⚠️ **TBD**: baris ini dan baris berikutnya menunjuk **UID butir yang sama** (`6a98359398ef90bb78e9a366`), sehingga satu centang mengisi dua metrik sekaligus. Pastikan ke pemilik metrik apakah disengaja. |
| 0.30 | `Menyusun laporan keuangan tepat waktu` | laporan keuangan tepat waktu maks. tgl 5 bulan berikutnya | ✅ **Terpasang di prod** (diukur 2026-09-12): sumber dan UID butir sama dengan baris di atas. | Lihat TBD UID ganda di baris atas. |
| 0.10 | `Menyimpan bukti transaksi dan arsip yang dibuat AP` | 100 % Semua Transaksi memiliki Arsip | ✅ **Terpasang di prod** (diukur 2026-09-12): `{sumber: ceklis_kpi, metrik: <UID butir 6a98359398ef90bb78e9a365>, formula: rata_rata, target: 100, arah: naik, hit_miss: true, scope: individu}`. Menurut komentar sumbernya, butir arsip dinilai SPV FAT. | Sudah otomatis dari ceklis. |

#### KPI Senior Accounting Bharata (lama, masih aktif)

Template `KPI Senior Accounting Bharata`, 8 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Laporan Keuangan 1` | Menyusun laporan keuangan secara akurat dengan persentase laporan keuangan secara akurat dan tepat waktu maks. tgl 7 bulan berikutnya | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.15 | `Laporan Keuangan` | Melakukan analisa laporan keuangan min. 2 rekomendasi perbaikan kinerja perusahaan di setiap bulan | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.15 | `Pengelolaan Aset Tetap` | Pengecekan dan depresiasi aset - Persentase aset dan perlengkapan tercatat secara akurat dan tepat waktu maks. tgl 7 | manufacture_resi (328.272) + warehouse_db.fulfillment_orders (38.949, event pick/pack/handover). | Bisa otomatis sekarang. Data resi dan proses gudang sudah tercatat lengkap. |
| 0.15 | `Rekonsiliasi bank, penjualan, dan persediaan` | Melakukan rekonsiliasi bank, penjualan, dan persediaan - Persentase laporan rekonsiliasi bank, penjualan, persediaan secara akurat dan tepat waktu | Accurate live proxy + GET /transactions/reconciliation dan /reconciliation/missing. accurate_bank_accounts (44). | Bisa sebagian. Alat pencocokan data sudah ada, tapi perlu disepakati dulu apa yang dihitung sebagai selisih dan kapan batas waktunya. |
| 0.05 | `Audit Internal` | Menyusun data dan dokumentasi pendukung untuk audit internal 100% tersedia tepat waktu. | TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM. | Belum bisa otomatis. Temuan audit, pelaporan pajak, dan izin BPOM belum dicatat di sistem. |
| 0.1 | `Monitoring Team` | Checker pencatatan/inputan team dengan minimal target KPI Staff 80 dan maks. pengumpulan tgl 3 | BUKAN murni skor tim: deskripsinya menggabungkan checker inputan dengan ketepatan tanggal. Pisahkan dulu dengan pemilik metrik. | Perlu dipecah dulu. Satu baris ini mencampur dua penilaian berbeda: memeriksa input tim, dan ketepatan tanggal pengumpulan. |
| 0.1 | `Minimal ide inovasi baru dari tim pada tiap kuartal` | Mengidentifikasi peluang inovasi di proses accounting minimal 2 ide inovasi terdaftar per bulan di kuartal 1 | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
| 0.1 | `Pertemuan 1-on-1 min. 1 per bulan per staf, 100% terdokumentasi` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

### Tax Staff

Template `KPI Tax Officer`, 8 metrik.

> ⚠️ **Tiga vonis di tabel bawah sudah dikoreksi 2026-08-31** lewat pengukuran langsung ke produksi ([[ANALISA - KPI Tax Officer]]). Tabelnya sengaja dibiarkan apa adanya sebagai salinan setia audit 2026-08-01; koreksinya di sini.
>
> 1. ⛔ **"Budget TIDAK tersimpan di ERP mana pun" (baris 0,15) KEDALUWARSA.** Master `anggaran_opex` kini terisi 233 baris (2026-07 s/d 2026-12, 40 akun), dan metriknya **sudah bisa dinyalakan tanpa satu baris kode** lewat sumber `varians_anggaran`/`varians_persen`. Pratinjau produksi Tax Staff periode 2026-07: realisasi varians **39,06%**, nilai **12,8**, status `semi` dengan cakupan **28,06%** ("39 dari 139 pos terhitung"). Cakupannya rendah karena anggaran baru terisi untuk 3 departemen; menaikkannya pekerjaan pengisian master data, bukan dev.
> 2. ⛔ **Dua baris bervonis "Bisa otomatis sekarang" KELIRU, bobot gabungan 0,30.** `Kepatuhan pajak … 1` (rekonsiliasi bulanan) dan `… 3` (temuan ditindaklanjuti ≤ 10 hari kerja) menyebut `/accounting/profit-loss` dan `/balance-sheet` sebagai sumber. Laba rugi Accurate tidak menyimpan temuan maupun tanggal tindak lanjutnya. Ini kelas yang sudah dinamai [[Finance - Rancangan Finance Service]]: **sumber datanya ada, tetapi bukan sumber untuk hal yang diukur** — sama dengan kekeliruan `Pencatatan Piutang`/`Pencatatan Retur` di rumpun AR.
> 3. ⚠️ **Baris 0,15 mengukur dua hal berbeda.** Labelnya `Varians antara budget vs realisasi OPEX ≤ ±5%` (bisa otomatis), deskripsinya bicara **deductible vs non-deductible** (mustahil: tak ada satu pun penanda deductible di data mana pun, diperiksa pada lima koleksi produksi). Harus diselesaikan pemilik metrik sebelum otomasi, sebab yang mengikat adalah hal yang benar-benar dihitung sumbernya.
> 4. ⛔ **(2026-09-12) Sel "TIDAK ADA tracker pajak" pada baris SPT Masa (0,10) dan filing (0,15) usang untuk sisi pajaknya.** Modul Tax Control kini ada di finance-service ([[API - Finance Service]]), beserta sumber KPI `kinerja_tax` (`services/employee/kpi_sumber_tax.go:12-31`, metrik `pelaporan_tepat_waktu` dan `dokumen_terarsip`, bobot matriks 65/35 yang tidak cocok dengan 8 metrik template aktif). Sumber itu **belum dipasang** ke template ini, dan data kewajiban pajak di prod masih **0** (seed master jenis pajak belum dijalankan), jadi metriknya belum bisa berangka walau dipasang. Diukur prod 2026-09-12.
>
> ⚠️ Tiga metrik berlabel `Kepatuhan pajak 100% setiap bulan 1/2/3` melanggar [[REF - Penamaan Metrik & Sumber KPI]] (label bernomor tanpa makna). Sebabnya: yang masuk kolom `label` adalah **area kinerja**, KPI-nya turun ke `description` — terbalik dari template lain.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.15 | `Varians antara budget vs realisasi OPEX ≤ ±5%` | Memastikan perlakuan PPh dan PPN tepat (deductible vs non deductible) - Potensi untuk menekan biaya non-deuctible 10% | Budget TIDAK tersimpan di ERP mana pun. Realisasi ada di Accurate; perlu master anggaran lebih dulu. | Belum bisa otomatis. Pengeluarannya sudah tercatat, tapi anggarannya belum pernah dimasukkan ke sistem, jadi tidak ada yang bisa dibandingkan. |
| 0.15 | `Kepatuhan pajak 100% setiap bulan 1` | Rekonsiliasi pajak bulanan dengan Selisih (discrepancy) rekonsiliasi = 0% setiap bulan | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.1 | `Kepatuhan pajak 100% setiap bulan 2` | Menyusun dan melakukan penyampaian SPT Masa tepat waktu minimal H-1 dari batas waktu | TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM. | Belum bisa otomatis. Temuan audit, pelaporan pajak, dan izin BPOM belum dicatat di sistem. |
| 0.15 | `Kepatuhan pajak 100% setiap bulan 3` | Melakukan monitoring kepatuhan dan melaporkan temuan pajak dengan 100% temuan ditindaklanjuti dalam ≤ 10 hari kerja | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.15 | `100% laporan pajak & regulatory filing diperiksa sebelum dikirim` | Menyiapkan laporan tepat waktu, valid, dan sesuai regulasi | TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM. | Belum bisa otomatis. Temuan audit, pelaporan pajak, dan izin BPOM belum dicatat di sistem. |
| 0.1 | `Minimal 2 audit internal per tahun, rate non-compliance ≤ 5%` | Menyediakan data pajak dan laporan government filing untuk audit internal | TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM. | Belum bisa otomatis. Temuan audit, pelaporan pajak, dan izin BPOM belum dicatat di sistem. |
| 0.1 | `Laporan keuangan` | Menyusun laporan keuangan dengan persentasi laporan keuangan secara akurat dan tepat waktu maks. tgl 5 | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses tax dengan minimal 2 ide inovasi terdaftar per bulan | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |

### Penilaian 2026 (diukur prod 2026-09-12)

Jumlah karyawan Finance yang punya `kpi_score` per periode, dari 16 karyawan aktif: Maret 1, April 15, Mei 15, Juni 14, Juli 15, **Agustus 2** (per 12 September 2026).

| Periode | Posisi | Template | Skor | Metrik ber-`auto_value` |
|---|---|---|---:|---|
| 2026-08 | Finance Supervisor | KPI Supervisor Finance | 36,8 | 5 dari 5 |
| 2026-08 | AR Staff | AR Staff 2026 | 22,7 | 3 dari 3 |
| 2026-07 | Finance Supervisor | KPI Supervisor Finance | 79,7 | 0 dari 5 |
| 2026-07 | Cost Control | KPI Cost Control | 92,0 | 0 dari 7 |
| 2026-07 | Account Payable | KPI Finance Staff Account Payable | 100 | 0 dari 6 |
| 2026-07 | Senior Accountant | KPI Senior Accounting Bharata | 65,0 | 0 dari 8 |
| 2026-07 | Tax Staff | KPI Tax Officer | 90,0 | 0 dari 8 |
| 2026-07 | Junior Accountant (6 orang) | KPI Accounting CV | 100 untuk keenamnya | 0 dari 36 |
| 2026-07 | Junior Accountant | KPI Accounting PT | 97,2 | 0 dari 4 |
| 2026-07 | AR Staff (3 orang, template berbeda) | AR STAFF PIUTANG · KPI AR Piutang · KPI AR Leader | 89,4 · 91,0 · 52,0 | 0 |

- **Skor yang ber-`auto_value` penuh jauh di bawah skor manual bulan sebelumnya.** Skor total tidak dinormalisasi (lihat Langit-langit skor SPV di atas), jadi angka rendah berasal dari nilai per metrik; rincian per metrik belum ditelusuri (**TBD**).
- **KPI Accounting CV**: 6 sampai 7 orang bernilai 100 (atau 98,2 sampai 100) setiap bulan April sampai Juli 2026, seluruhnya manual. Metriknya belum membedakan kinerja, dan nilainya diinput akun HR tanpa catatan maupun bukti (lihat subbagian berikut).
- **Agustus baru 2 orang dinilai.** Untuk bulan lampau, F5 hanya membaca skor final anggota, jadi urutan penilaian anggota, leader, lalu supervisor tetap mengikat.

#### Siapa menilai, buktinya, dan jejak kerja di ERP (diukur prod 2026-09-12)

Pertanyaan yang dijawab subbagian ini: **apakah matriks dan skor KPI Finance memberi tahu apa yang benar-benar dikerjakan tiap orang?** Per 12 September 2026 jawabannya **tidak**. Matriks memuat apa yang *diharapkan* dari tiap posisi; skornya tidak membawa jejak pekerjaan. Nama dan ID karyawan sengaja tidak disalin ke dok ini.

**Penginput skor.** Dari 61 `kpi_score` karyawan Finance periode April sampai Agustus 2026:

| Penginput (posisi akun) | Skor | Periode |
|---|---:|---|
| Human Resource / `Training & Perfomance Officer` (akun pertama) | 19 | April sampai Mei |
| Human Resource / HRD Supervisor | 25 | Mei sampai Juni |
| Human Resource / `Training & Perfomance Officer` (akun kedua) | 15 | Juli |
| Akun yang tidak cocok dengan data karyawan mana pun | 2 | Agustus (dua skor ber-`auto_value` di tabel atas) |

Supervisor Finance tidak menginput satu pun skor timnya. Ini **berselisih** dengan [[Finance - FAT Persona]], yang menempatkan Supervisor FAT sebagai penilai terakhir KPI tim. Apakah Supervisor menilai di luar sistem lalu HR yang mengetik nilainya: **TBD**, perlu dikonfirmasi ke HR.

**Catatan dan bukti.**
- Dokumen skor (`KPIScore`, `shared-library/models/employee/models.go:729-736`) hanya menyimpan salinan template plus nilai per metrik. Di prod, metriknya berisi `label`, `description`, `weight`, `value`, dan `key`; field `auto_*` hanya ada di 8 metrik otomatis. **Tidak ada field catatan penilai.**
- Lampiran bukti per metrik punya koleksi sendiri, `kpi_evidence` (`KPIEvidence`, `models.go:64` dan `:738-758`, lengkap dengan `note` dan `uploaded_by`). Isinya **0 dokumen untuk seluruh perusahaan**, bukan hanya Finance. Fiturnya ada, pemakainya belum.

**Metrik bernilai 100 per template** (jumlah metrik bernilai 100 dari metrik di snapshot skor):

| Template | April | Mei | Juni | Juli |
|---|---|---|---|---|
| KPI Accounting CV (6 sampai 7 orang) | 36/36 | 38/42 | 36/36 | 36/36 |
| KPI Finance Staff Account Payable | 4/5 | 5/5 | 5/6 | 6/6 |
| KPI Tax Officer | belum dinilai | belum dinilai | belum dinilai | 7/8 |
| KPI Cost Control | 3/7 | 3/7 | 5/7 | 6/7 |
| KPI Senior Accounting Bharata | 4/7 | 6/7 | 4/8 | 6/8 |
| KPI Supervisor Finance | 0/5 | 3/5 | 3/5 | 3/5 |

Account Payable dan Tax Staff bernilai hampir penuh, padahal akun keduanya tanpa izin finance apa pun, koleksi `pembayaran` di procurement berisi 0, dan modul pajak kosong (lihat [[Finance - FAT Persona]]). Itu **bukan bukti mereka tidak bekerja**; pekerjaannya kemungkinan terjadi di Accurate atau di luar sistem, sehingga tidak terlihat dari ERP.

**Jejak kerja per posisi di ERP.** Pencatat dokumen yang bisa dipetakan ke posisi Finance:

| Posisi | Jejak pencatat di ERP |
|---|---|
| AR Staff | `invoice_correction_logs` (jejak audit koreksi faktur manual oleh finance, `services/integration/internal/domain/entity/invoice_correction_log.go:45-48`): **233 dari 268**, 26 Agustus sampai 4 September 2026. `fake_order_import_batches`: 5 dari 6. `transaction_summary_reports`: 129, 2 sampai 15 Juli 2026. `item_histories` 10 dan `item_price_history` 5 (Juli sampai Agustus). |
| Cost Control | `kas_plafon` 6 dari 6, `kas_parameter` 2 dari 6, `kas_jurnal_outbox` 1 dari 1, `anggaran_opex` 8 dari 233. |
| Finance Supervisor | 1 entri persetujuan di `pengajuan_pembelian.riwayat`. |
| Senior Accountant, Junior Accountant, Account Payable, Tax Staff | **Tidak ada jejak pekerjaan keuangan.** Nama mereka hanya muncul sebagai pengaju tiket ke Tech Development dan di pengajuan pribadi HR (lihat butir "Di luar Procurement, Finance, dan Integration" di bawah). |

- Koreksi faktur dan batch impor tercatat sebagai nama, bukan ID. Nama itu cocok sebagian dengan dua kandidat yang **sama-sama** AR Staff, jadi posisinya pasti tapi orangnya belum.
- 5.138 `transaction_summary_reports` lainnya ditulis aktor `Auto-Sync` milik worker (`services/integration/internal/worker/tasks/auto_summary_report.go:103`), bukan orang.
- `product_costs` (HPP per produk): 45 dari 47 diunggah Tech Development Leader, 1 oleh Direktur, 1 oleh Fullstack Developer. Metrik HPP milik Account Payable tidak punya jejak di sini.
- `kas_transaksi`: 68 dari 69 dibuat pada 26 Agustus 2026 oleh satu ID yang tidak ada di data karyawan. Asal ID itu (impor atau akun non-karyawan) **TBD**.
- `audit_jejak` dan `audit_setelan_sampel` di `finance_db` hanya berisi pencatat Tech Development.
- **Di luar Procurement, Finance, dan Integration**, nama orang Finance muncul di dua tempat, dan keduanya **bukan** pekerjaan keuangan:
  - `task_management_db.tasks`: 24 tiket yang diajukan orang Finance **ke** Tech Development (Junior Accountant 12, AR Staff 7, Senior Accountant 3, Finance Supervisor 2), Juli sampai September 2026. Ruangnya IT Support 13, System Finance 10, MyBharata/HRIS 1. Tidak satu pun tiket ditugaskan (`assign_to`) ke orang Finance.
  - `attendance_db` dan `employee_db`: cuti, koreksi absen, perjalanan dinas, dan data diri milik mereka sendiri.
- Container Manufacture, Insentive, Inventory, Warehouse, Form Builder, Payroll, Marketing Analytics, Calendar, Notification, Recruitment, HRD Document, Learning, TikTok Shop, dan Vault MCP: **0** baris dengan pencatat berposisi Finance. Artinya proposal Sadewa manufaktur yang masuk kotak persetujuan Supervisor FAT dan target profit insentif level supervisor (keduanya dicatat di [[Finance - FAT Persona]]) belum meninggalkan jejak atas nama orang Finance, setidaknya lewat field pencatat yang dipindai. Untuk Form Builder (ceklis KPI Senior Accountant), jawaban ceklis mungkin disimpan di field yang tak bernama pencatat, jadi nol di sini **belum** membuktikan ceklis tak pernah diisi (**TBD**). `log-direktur-mongo-1` tidak terbaca karena env kredensialnya kosong.

**Accurate tidak menyimpan pembuat dokumen di ERP.** Dari 20 koleksi `accurate_*` di `integration_db`, **0** punya field pembuat atau pengubah (pemindaian kunci sampai kedalaman 6 atas 20 dokumen terbaru tiap koleksi), dan entity maupun klien Accurate di integration-service tidak memetakan field pengguna. Jadi siapa yang membuat faktur, jurnal, atau pembayaran di Accurate, yaitu sebagian besar pekerjaan Accounting, AP, dan Tax, **tidak bisa diketahui dari ERP**. Apakah API Accurate menyediakan data pembuat dokumen: **TBD**.

**Cara ukur dan batasnya.** Field bernada pencatat (`created_by`, `createdBy`, `dibuat_oleh`, `uploaded_by`, `action_by`, `riwayat[].oleh`, dan sejenisnya) dicari di 50 dokumen terbaru tiap koleksi pada **21 container MongoDB prod milik semua departemen** (satu tak terbaca, lihat di atas) sampai kedalaman 3, lalu dihitung atas 2000 dokumen terbaru. Field subjek seperti `employee_id` sengaja tidak dihitung, karena menunjuk orang yang datanya dicatat, bukan orang yang mencatat. Nilainya dipetakan ke posisi lewat `employee_id`, `_id` akun, `username`, atau `full_name`; untuk objek aktor (`services/integration/internal/domain/entity/actor.go:9-16`) dipakai `employee_id`-nya. Koleksi tanpa field pencatat, misalnya faktur pembelian hasil sinkron Accurate, tidak bisa diatribusikan.

**Keputusan yang tersisa (TBD HR dan pemilik metrik):** wajibkan unggah bukti per metrik lewat `kpi_evidence` yang sudah ada, atau tetapkan sumber jejak kerja lain untuk posisi yang pekerjaannya di Accurate.

## General Affair

5 template, 24 metrik. Klasifikasi otomasi: **1 / 5 / 1 / 17**.

### Admin

Template `Admin General Service`, 7 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Pengelolaan Keuangan GA 1` | Persentase realisasi anggaran belanja sesuai rencana tanpa over budget. Terpakai di 30% dari Total Anggaran / Bulan | Budget TIDAK tersimpan di ERP mana pun. Realisasi ada di Accurate; perlu master anggaran lebih dulu. | Belum bisa otomatis. Pengeluarannya sudah tercatat, tapi anggarannya belum pernah dimasukkan ke sistem, jadi tidak ada yang bisa dibandingkan. |
| 0.2 | `Pengelolaan Keuangan GA 2` | Akurasi pencatatan data kas kecil secara tepat waktu. | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.1 | `Administrasi & Pengadaan 1` | Persentase ketepatan rekap pengajuan dana kebutuhan GA | GET /procurement/po/lead-time + penerimaan (1.835) + /harga/banding + pemasok (139) + faktur_pembelian (2.055). | Bisa otomatis sekarang. Data pesanan pembelian, penerimaan barang, dan riwayat harga sudah lengkap. |
| 0.15 | `Administrasi & Pengadaan 2` | Administrasi Dokumen GA ( Kelengkapan & kerapihan dokumen secara Real Time ) | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |
| 0.15 | `Administrasi & Pengadaan 3` | Ketepatan Pengadaan Barang ATK & GA ( Tepat Waktu ) | GET /procurement/po/lead-time + penerimaan (1.835) + /harga/banding + pemasok (139) + faktur_pembelian (2.055). | Bisa otomatis sekarang. Data pesanan pembelian, penerimaan barang, dan riwayat harga sudah lengkap. |
| 0.1 | `Pengelolaan Vendor` | Skor Pelayanan & Harga(tidak Over Budget) vendor | Budget TIDAK tersimpan di ERP mana pun. Realisasi ada di Accurate; perlu master anggaran lebih dulu. | Belum bisa otomatis. Pengeluarannya sudah tercatat, tapi anggarannya belum pernah dimasukkan ke sistem, jadi tidak ada yang bisa dibandingkan. |
| 0.1 | `Aset Support Operational` | Akurasi Pengelolaan ATK & Inventory | inventory_db.inventory (134 item) + handover per karyawan. Repair history KOSONG, stock opname aset belum ada. | Bisa sebagian. Daftar aset dan serah terimanya sudah ada, tapi riwayat perbaikan belum pernah diisi dan opname aset belum ada menunya. |

### GA Staff

Template `Building & Maintenance`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Pengelolaan Aset Building dan Fasilitas 1` | Realisasi Preventif Maintenance Building & Fasilitas | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |
| 0.3 | `Pengelolaan Aset Building dan Fasilitas 2` | Menyelesaikan kerusakan secara cepat dan tepat (Jumlah Perbaikan Berhasil : Total Perbaikan) | inventory_db.inventory (134 item) + handover per karyawan. Repair history KOSONG, stock opname aset belum ada. | Bisa sebagian. Daftar aset dan serah terimanya sudah ada, tapi riwayat perbaikan belum pernah diisi dan opname aset belum ada menunya. |
| 0.25 | `Efisiensi Biaya Maintenance / Project` | Mengontrol biaya tanpa menurunkan kualitas (Realisasi/Budget) x 100% All Project Perbaikan | Budget TIDAK tersimpan di ERP mana pun. Realisasi ada di Accurate; perlu master anggaran lebih dulu. | Belum bisa otomatis. Pengeluarannya sudah tercatat, tapi anggarannya belum pernah dimasukkan ke sistem, jadi tidak ada yang bisa dibandingkan. |
| 0.15 | `Daily Report` | Checklist Harian & Bulanan | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |

### GA Staff

Template `General Asset Staff`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Aset dan Insidental 1` | Persentase Realisasi Rencana Kerja VS Realisasi | inventory_db.inventory (134 item) + handover per karyawan. Repair history KOSONG, stock opname aset belum ada. | Bisa sebagian. Daftar aset dan serah terimanya sudah ada, tapi riwayat perbaikan belum pernah diisi dan opname aset belum ada menunya. |
| 0.25 | `Aset dan Insidental 2` | Persentase SLA Preventife Maintenance Alat Operational Tepat Waktu | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |
| 0.2 | `Aset dan Insidental 3` | Persentase Pemeliharaan Aset Dengan Tepat | inventory_db.inventory (134 item) + handover per karyawan. Repair history KOSONG, stock opname aset belum ada. | Bisa sebagian. Daftar aset dan serah terimanya sudah ada, tapi riwayat perbaikan belum pernah diisi dan opname aset belum ada menunya. |
| 0.15 | `Aset dan Insidental 4` | Akurasi Ketepatan Stok Opname Aset | inventory_db.inventory (134 item) + handover per karyawan. Repair history KOSONG, stock opname aset belum ada. | Bisa sebagian. Daftar aset dan serah terimanya sudah ada, tapi riwayat perbaikan belum pernah diisi dan opname aset belum ada menunya. |
| 0.1 | `Penglolaan Aset` | Labeling & Tagging Asset | inventory_db.inventory (134 item) + handover per karyawan. Repair history KOSONG, stock opname aset belum ada. | Bisa sebagian. Daftar aset dan serah terimanya sudah ada, tapi riwayat perbaikan belum pernah diisi dan opname aset belum ada menunya. |

### Office Boy

Template `Office Boy Team`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Pelayanan Kebersihan` | Rating Pelayanan dan Kebersihan (1-10) | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |
| 0.3 | `Kebersihan 1` | Kondisi kebersihan area yang ditugaskan (halaman, loby, ruang QA/QC, produksi, direktur, dll). | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |
| 0.25 | `Kebersihan 2` | Kondisi perawatan barang/perabotan, tanaman asli/hias di area yang ditugaskan. | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |
| 0.15 | `Kebersihan 3` | Pelaksanaan 5R di Area Pantry dan Area Tanggung Jawab Kebersihan | ⚠️ **Sumber `nilai_inspeksi_satgas` merged 2026-09-14, live di DEV, belum deploy PROD** (bip-erp PR [#1866](https://github.com/bip-itteam-internal/bip-erp/pull/1866) `feat/satgas-nilai-kpi`; cek ulang lintas bulan [#1867](https://github.com/bip-itteam-internal/bip-erp/pull/1867) `feat/satgas-cek-ulang`). Diuji E2E di dev 2026-09-14 lewat `GET /api/employee/kpi/auto-values` dengan template KPI uji Office Boy: temuan yang masih bisa dicek ulang dan orang tanpa kiriman berbunyi "belum dapat dihitung", sesudah cek ulang skor 5 `auto_value` 100, semuanya `auto_gagal_sumber: false`. Menarik `GET /internal/satgas/metrics` dari form-builder, yaitu jawaban form bertanda `metric_key: inspeksi_satgas` yang diisi petugas Satgas lewat MyBharata. Nilai per orang per bulan = kiriman **terakhir** (cek ulang menggantikan temuan), skala 1..5 jadi (v-1)/4 (skor 3 = 50), dirata-rata antar form bila orangnya dinilai lebih dari satu form. Temuan yang masih bisa dicek ulang belum final sampai tanggal 5 bulan berikutnya 23:59:59 WIB; form yang sudah ditutup langsung final (`services/form-builder/satgas_nilai.go`, `services/employee/kpi_sumber_inspeksi_satgas.go`). Sampai deploy prod dan HR memasangnya, masih diisi manual dari lembar HRD dengan skala campur (1-5 dan 0-100); template `Office Boy Team` asli di dev pun belum dipasangi sumber ini (2026-09-14). Keputusan: [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]]. | Sesudah deploy prod, HR memasangnya di "Atur Target": sumber `nilai_inspeksi_satgas` (label "Nilai inspeksi Satgas 5R", erp-frontend PR [#1555](https://github.com/bip-itteam-internal/erp-frontend/pull/1555), merged 2026-09-14), formula `rata_rata` dan scope `individu` (satu-satunya pilihan sumber ini), target TBD HR. Belum diinspeksi, menunggu cek ulang, kiriman tanpa skor, dan bulan tanpa form Satgas berjalan berbunyi "belum dapat dihitung": metrik ini jatuh manual, skor otomatis lain tetap tampil. Orang yang bukan sasaran form Satgas dan form tanpa pertanyaan skala digalatkan, dan galat itu menahan seluruh skor otomatis orangnya sampai dibetulkan. Syarat deploy: env `FORM_BUILDER_SERVICE_KEY` bernilai sama di form-builder **dan** employee-service (`.env` dev diisi 2026-09-14 lalu kedua container dibuat ulang; `.env` prod belum diukur). **Jangan** memakai `nilai_layanan_pribadi`: sumber itu melebur seluruh form penilaian bertanda di departemen, jadi skor 5R akan tercampur rating pelayanan. |

### Security

Template `Security Team`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Pelayanan Security` | Rating Pelayanan dan Keamanan (1-10) | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.3 | `Kualitas Keamanan` | Kepatuhan Melakukan Patroli Setiap 3 Jam ( Aspek Keamanan, Kerapian & Kondisi Area ) | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |
| 0.2 | `Dokumentasi` | Kepatuhan SOP Security | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.2 | `Kerapihan dan kebersihan Pos` | Persentase kerapihan dan kebersihan pos jaga ( Konsep 5R ) | ⚠️ **Sumber `nilai_inspeksi_satgas` merged 2026-09-14, live di DEV, belum deploy PROD**, sumber yang sama dengan `Kebersihan 3` Office Boy di atas; cara tarik, aturan nilai, PR, dan bukti uji dev-nya ditulis di baris itu. Template `Security Team` asli di dev belum dipasangi sumber ini (2026-09-14). Keputusan: [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]]. | Sesudah deploy prod, pasang di "Atur Target" seperti baris Office Boy di atas (sumber `nilai_inspeksi_satgas`, `rata_rata`, `individu`, target TBD HR). **Jangan** memakai `nilai_layanan_pribadi` (sumber metrik `Pelayanan Security` di kode): skor 5R akan tercampur rating pelayanan, di KPI Security maupun di indeks tim atasannya. |

## Human Resource

5 template, 32 metrik. Klasifikasi otomasi: **6 / 7 / 9 / 10**. Riwayat: sebelum 2026-09-02
tertulis 7 / 5 / 10 / 9 (satu metrik Recruitment & Onboarding berpindah dari *terblokir data*
ke *butuh definisi*), lalu 7 / 6 / 9 / 9 dengan 31 metrik sampai 2026-09-15 (template Training &
Perfomance Officer berganti). Penjelasan keduanya ada di bab posisi masing-masing.

### Culture & Industrial

Template `Organizational Development`, 6 metrik.

> 🟡 **Template aktif kini `HR Organizational Development`** (branch `feature/workspace-position`, belum merge/prod). Template lama `Organizational Development` di tabel ini **diarsipkan**; label/bobot metriknya dibawa apa adanya. Wiring sumber `program_culture` (di bawah) menempel pada template aktif yang baru, bukan yang arsip.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Culture 1` | Penyusunan program culture | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.2 | `Culture 2` (metrik `culture` di template aktif) | Skor program culture (partisipasi, antusiasme, implementasi) | 🟡 **TERPETAKAN — sumber `program_culture`** (branch `feature/workspace-position`, belum merge/prod). Menarik `GET /internal/culture/metrics` dari form-builder: modul Kelola Program Culture (`culture_programs` + feedback peserta) dihitung per periode jadi **skor komposit** 30/30/40 (implementasi otomatis = part×ant÷100), dirata-rata per officer. Detail: [[Microservices - Form Builder Service]], [[ADR - 0066 Modul Kelola Program Culture]]. | Tinggal diisi HR di "Atur Target": sumber `program_culture` (tanpa sub-metrik, tanpa scope), formula `rata_rata`, target 100, arah naik. Data kosong digalatkan (jatuh manual), bukan 0. |
| 0.2 | `Culture 3` | Prosentase Keaktifan Peserta Training >= 100% dari jumlah Peserta | **Disegarkan 2026-09-17.** Modul Training ada dan ter-deploy ([[Microservices - Learning Service]]); prod `training` 2 (keduanya `Ongoing`), `training_participant` 3 (2 hadir). ✅ Konektor ada: sumber `pelatihan` / `kehadiran_peserta_persen`, live di produksi 2026-09-15. Evaluasi dan post-test juga sudah punya tempat (`trainer_evaluation`, `quiz_attempt`), jadi keterangan lama "belum ada fieldnya" sudah tidak berlaku. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu pelatihan sudah ada, hanya belum diisi, dan kelas baru terhitung sesudah statusnya **Completed**. Begitu terisi, isi Atur Target: sumber `pelatihan`, metrik `kehadiran_peserta_persen`, cakupan `perusahaan`. |
| 0.2 | `KPI` | Skor Penilaian Training All Karyawan > 70 | **Disegarkan 2026-09-17.** Pre-test dan post-test berskor beserta layar web-nya live di prod sejak 2026-09-17 (`quiz_attempt` prod 0; rincian di baris kembarnya). ✅ Konektor ada: sumber `pelatihan` / `skor_post_test_persen` atau `peningkatan_post_test_persen`, live di produksi. | Belum bisa sekarang. Mesin ujian, layar, dan konektornya sudah ada, tetapi belum ada satu pun percobaan ujian. Bunyi "All Karyawan > 70" menunjuk `rasio_ambang` ambang 70, sama dengan baris kembarnya di [[#Training & Perfomance Officer]]. |
| 0.1 | `SOP` | Tingkat Kedisipilnan Karyawan ( Attandance & Intergritas ) | `kedisiplinan_absensi` / `ketepatan_waktu`, menarik `GET /kpi/attendance` dari attendance-service. | ✅ **KONEKTOR SIAP** (2026-08-22, [#1379](https://github.com/bip-itteam-internal/bip-erp/pull/1379), live di prod). Tinggal diisi HR di `/hris/kpi/otomasi`: sumber `kedisiplinan_absensi`, metrik `ketepatan_waktu`, cakupan **`perusahaan`** (bunyinya "seluruh karyawan", bukan tim OD), reduksi `rasio_ambang`. |
| 0.1 | `Kaizen` | Jumlah Inovasi All Divisi ( 7 / Bulan ) | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |

### HRD Supervisor

Template `KPI Supervisor HRGA`, 10 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.15 | `Revenue 240 Miliar` | Menjamin ketersediaan tenaga kerja dengan rata-rata time recruitment <30 hari untuk posisi kritikal | **Disegarkan 2026-09-02.** Modul Recruitment ada tapi koleksi `candidate` **belum pernah terbentuk**; `job_requisition` kini **6** dan `job_posting` **1** (angka lama di dokumen ini, 2 dan 1, sudah basi). Kabar baiknya "posisi kritikal" sudah punya penandanya di sistem: `manpower_plan.is_kritikal` (3 baris tahun 2026, 1 di antaranya kritikal). Batasnya sama persis dengan metrik `Time to Fulfilment Rate` di [[#Recruitment & Onboarding]]: ujung "terpenuhi" belum tercatat di mana pun. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. Metrik ini dan `Time to Fulfilment Rate` milik staf mengukur hal yang sama dengan cakupan berbeda, jadi definisinya wajib disepakati **sekali** untuk keduanya. |
| 0.05 | `Net Income 20%` | Efisiensi biaya operasional GA min. 5% dari bulanan | ⚠️ **DIKOREKSI 2026-08-21.** Sumber lama tertulis `/accounting/profit-loss` + `/balance-sheet` + `/profit/cash-flow` — laba rugi PERUSAHAAN, yang tak menjawab efisiensi satu departemen. Yang menjawab: `GET /accounting/anggaran/varians?tahun&bulan&departemen`, memakai `ringkas.total_realisasi` departemen GA. | Bisa otomatis sekarang, **dengan syarat**: realisasi periode itu sudah disinkron (`belum_pernah_sinkron` false) dan departemen GA ada di katalog Accurate. Sudah terpasang di dashboard, lihat catatan di bawah tabel. |
| 0.05 | `Return On Operation Asset` | Monitoring aset 100% terdata secara realtime | ⚠️ **PERLU DIPERIKSA ULANG 2026-08-21.** Sumber tertulis `accurate_daily_returns` + `shopee_returns` = data RETUR, sementara deskripsinya monitoring ASET. Aset ada di `inventory_db.inventory` (134 item) + rekonsiliasi Accurate ([[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]]), bukan di retur. | **Vonis lama `bisa otomatis sekarang` tidak dapat ditindaklanjuti apa adanya** — sumber yang disebut menjawab metrik yang berbeda. Tetapkan dulu dengan pemilik metrik apakah yang dinilai kelengkapan data aset (maka sumbernya `inventory`) atau benar-benar retur (maka deskripsinya yang salah). |
| 0.2 | `Performance Monitoring 100% Terimplementasi di Q4` | Memastikan seluruh tim/karyawan di setiap departemen memiliki skor KPI Min. 70 | ⚠️ **DIKOREKSI 2026-08-21.** Sumber `skor_tim` benar, tetapi reduksinya **`rasio_ambang`** (ambang 70, target 100), BUKAN `rata_rata` seperti tertulis sebelumnya. Kata kuncinya **"SELURUH"**: rata-rata 78 lolos target walau sepuluh orang berskor 40. `rasio_ambang` menjawab "berapa persen anggota melewati 70" dan sudah ada di mesin (`kpi_reduksi.go`). | Bisa otomatis sekarang, **dengan reduksi `rasio_ambang`**. Memakai `rata_rata` di sini menerbitkan angka yang menjawab pertanyaan lain, dan angka itu akan terlihat wajar. |
| 0.1 | `Turn Over Rate Target 5% per Tahun` | Peningkatan Kualitas Rekruitment | `turnover_karyawan` / `turnover_persen`, memakai ulang `riwayatTurnover` yang menggambar kartu Turnover di halaman Resign. | ⚠️ **KONEKTOR SIAP, tetapi SATUANNYA harus diputuskan dulu** (2026-08-22, [#1379](https://github.com/bip-itteam-internal/bip-erp/pull/1379)). Cakupan wajib **`perusahaan`** (ditolak kode bila lain), arah **`turun`**. Dua hal yang menuntut keputusan pemilik metrik sebelum dinyalakan, lihat catatan di bawah tabel. |
| 0.1 | `Implementasi Training` | Memenuhi kebutuhan pelatihan untuk talent dan seluruh karyawan 100% terpenuhi tiap bulan dan terjadi peningkatan performa. | Modul Training ADA di kode tapi koleksi training & training_participant KOSONG di prod. Skor & survei kepuasan training juga belum ada fieldnya. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu pelatihan sudah ada, hanya belum ada yang mengisinya. Nilai dan survei kepuasan pelatihan memang belum ada tempatnya. |
| 0.2 | `Performance Monitoring Team HRGA` | Rata-rata KPI Team HRGA min. 70 | Sumber skor_tim + reduksi rata_rata, scope department. Sudah didukung mesin; tinggal isi konfigurasi. | Bisa otomatis sekarang. Sistem tinggal merata-ratakan skor anggota departemen, dan mesinnya sudah siap. |
| 0.05 | `Employee Productivity sebesar 120 Juta per Employee ( DIv. Marketing )` | Memberikan Training, Coaching, atau Tools untuk meningkatkan Produktivitas. | Modul Training ADA di kode tapi koleksi training & training_participant KOSONG di prod. Skor & survei kepuasan training juga belum ada fieldnya. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu pelatihan sudah ada, hanya belum ada yang mengisinya. Nilai dan survei kepuasan pelatihan memang belum ada tempatnya. |
| 0.05 | `Succession Planing Terimplementasi` | Menyusun Kaderisasi & Talent Pool - 100% Calon Successor memiliki Development Plan dan Siap apabila diperlukan | TIDAK ADA modul succession/talent pool. | Belum bisa otomatis. Belum ada pencatatan calon penerus jabatan. |
| 0.05 | `Employee Satisfaction` | Tingkat kepuasan pelayanan Team General Service minimal 90% memberikan penilaian 5 dari all karyawan | GET /task-management/report/csat. Pembacaan ulang prod 2026-08-06: **17 tiket ter-rating** seumur hidup, 13 di antaranya Juli. Masih tipis, dan seluruh rating Juli bernilai 5/5 sehingga belum membedakan siapa pun. | Belum layak dipakai. Yang menilai baru 17 orang seumur hidup dan semuanya memberi nilai penuh, jadi angkanya belum bisa membedakan pelayanan yang baik dari yang biasa saja. |

> [!warning] `Turn Over Rate`: dua hal yang harus diputuskan sebelum dinyalakan
> **1. Satuannya bulanan, targetnya tertulis per tahun.** Konektor `turnover_karyawan`
> mengembalikan turnover **satu periode KPI**, yaitu satu bulan, karena itulah yang
> dihitung `riwayatTurnover`. Label metriknya berbunyi "Target 5% per Tahun". Memasang
> target `5` apa adanya berarti ambangnya kira-kira **dua belas kali lebih longgar**
> daripada yang dimaksud, dan angkanya akan lolos tiap bulan tanpa ada yang curiga. 5% per
> tahun setara ±0,42% per bulan. Kode sendiri tidak menjawab ini: konstanta
> `TargetTurnoverBulananPersen = 5.0` di `services/employee/turnover.go` dipakai mewarnai
> kartu di halaman Resign, dan tidak ada catatan apakah angka itu turunan sadar dari target
> tahunan atau salinan yang satuannya ikut terbawa. **Putuskan eksplisit** sebelum mengisi
> `Target`.
>
> **2. Label dan deskripsinya menunjuk dua hal.** Labelnya ukuran (`Turn Over Rate`),
> deskripsinya tujuan ("Peningkatan Kualitas Rekruitment"). Keduanya koheren bila yang
> dimaksud adalah **mengukur kualitas rekrutmen lewat turnover**, dan pemetaan ke
> `turnover_karyawan` berdiri di atas bacaan itu. Bacaan lain, yaitu menilai mutu pelamar
> langsung, menuntut data kandidat yang koleksinya masih kosong. Catatan lama di baris ini
> memilih bacaan kedua; yang sekarang memilih yang pertama, dan itu **perubahan tafsir**,
> bukan sekadar pembaruan status.

> [!warning] "Rata-rata min 70" dan "SELURUH anggota min 70" adalah dua metrik berbeda
> Mesin punya empat reduksi (`kpi_reduksi.go`): `rata_rata`, `jumlah_unit`, `jumlah_nilai`,
> dan **`rasio_ambang`**. Yang terakhir menghitung berapa persen anggota melewati ambang,
> dan itulah yang menjawab kalimat berkata **"seluruh"** atau **"100%"**.
>
> Rata-rata 78 lolos target 70 walau sepuluh orang berskor 40. Untuk metrik yang menuntut
> SELURUH anggota lolos, `rata_rata` bukan sekadar kurang tepat, ia menjawab pertanyaan
> yang berbeda dan menyembunyikan persis kasus yang metriknya ingin cegah.
>
> Di tabel ini yang terkena **hanya `Performance Monitoring 100% Terimplementasi di Q4`**
> (HRD Supervisor), sebab deskripsinya menyebut "seluruh". Metrik `Performance Monitoring
> Team` di departemen lain berbunyi "KPI Tim minimal skor 70" tanpa kata itu, jadi
> `rata_rata` di sana tetap berlaku. **Baca kalimatnya, jangan menyeragamkan reduksinya.**
>
> `Reduksi()` menolak nama yang tak dikenal alih-alih jatuh ke bawaan, dengan alasan yang
> ditulis di kodenya: "memilih rumus diam-diam berarti menyajikan angka yang tak pernah
> diminta siapa pun."

> [!warning] Dua sumber di tabel ini sempat dipetakan dari LABEL, bukan dari deskripsi
> Ditemukan 2026-08-21 saat menyambungkan metriknya ke dashboard. `Net Income 20%`
> dipetakan ke laporan laba rugi dan `Return On Operation Asset` ke data retur — keduanya
> mengikuti bunyi labelnya, padahal deskripsi keduanya bicara soal hal lain (biaya GA dan
> pendataan aset).
>
> **Ini kelas kekeliruan yang khas template ini**, bukan kelalaian sekali: bab "Cacat yang
> sudah diketahui" di atas sudah mencatat bahwa sejumlah label berisi target korporat
> alih-alih nama metrik. Selama labelnya yang dibaca, pemetaan sumbernya akan terus
> meleset ke arah yang sama. **Untuk template ini, baca kolom Target/keterangan lebih dulu,
> baru cari sumbernya.**
>
> Vonis `bisa otomatis sekarang` yang bersandar pada sumber keliru **lebih merugikan
> daripada vonis "belum bisa"**: ia mengundang dev menyambungkan angka yang menjawab
> pertanyaan lain, dan angka itu tetap terlihat wajar di layar.

**Terpasang di dashboard** (erp-frontend [#1128](https://github.com/bip-itteam-internal/erp-frontend/pull/1128) + [#1130](https://github.com/bip-itteam-internal/erp-frontend/pull/1130), merged 2026-08-21): seluruh sepuluh metrik di atas kini tampil sebagai **matriks KPI** di tab HRD Supervisor halaman Ringkasan Divisi HRGA, lengkap dengan bobot, status otomasi, dan kelayakannya. Bobot dan status ditarik hidup dari `GET /kpi/auto-overview`, tidak disalin. Rincian di [[APP - Web ERP]].

**Empat dari sepuluh metrik sudah menampilkan ANGKANYA**, bukan hanya vonis kelayakannya (dua terakhir menyusul di erp-frontend [#1180](https://github.com/bip-itteam-internal/erp-frontend/pull/1180), **belum merge**):

| Metrik | Bobot | Angka yang tampil | Reduksi |
|---|---:|---|---|
| `Net Income 20%` | 0,05 | penurunan realisasi biaya GA terhadap bulan sebelumnya | — |
| `Turn Over Rate Target 5% per Tahun` | 0,10 | turnover bulan berjalan terhadap targetnya | — |
| `Performance Monitoring 100% Terimplementasi di Q4` | 0,20 | **berapa orang** di bawah ambang 70 | `rasio_ambang` |
| `Performance Monitoring Team HRGA` | 0,20 | **rata-rata** skor grup HRGA | `rata_rata` |

> [!warning] Kedua metrik Performance Monitoring menunjuk kartu yang SAMA dan tak boleh dijawab angka yang sama
> Keduanya berbobot 0,20 dan keduanya diarahkan ke kartu Skor KPI karyawan, jadi jalan
> termudah adalah memasangkan keduanya ke satu penyedia angka. Itu keliru, dan kelirunya
> tak akan terlihat: dua baris, dua angka, keduanya masuk akal.
>
> Yang membedakan cuma kalimat metriknya, dan callout **"Rata-rata min 70 dan SELURUH
> anggota min 70 adalah dua metrik berbeda"** di atas sudah mengatur jawabannya. Rata-rata
> 78 lolos target 70 walau sepuluh orang berskor 40.
>
> Sebelum perbaikan ini, `Performance Monitoring Team HRGA` tak punya angka sama sekali
> sementara penunjuknya menyuruh pembaca melihat kartu yang hanya memuat angka **lintas
> departemen**. Diukur di dev 2026-08-21: HRGA 20 orang, lintas departemen 169 orang.

> [!caution] Bobot lembar KPI ini pernah disalin ke frontend dan menyimpang
> `erp-frontend/src/features/hris/dashboard/lib/kpi-spv.ts` (sudah **dihapus**) menyalin
> tabel ini dengan `Return On Operation Asset` berbobot **25** (asli 0,05) dan
> `Performance Monitoring Team HRGA` berbobot **0** (asli 0,20). Keduanya saling menutupi
> sehingga totalnya tetap 100 dan test-nya tetap hijau — test itu menguji konsistensi
> internal, bukan kecocokan dengan tabel ini.
>
> Akibatnya bukan kosmetik: daftar "KPI belum bersumber" diurutkan menurut bobot justru
> untuk memutuskan pekerjaan berikutnya, sehingga ia menunjuk arah terbalik selama
> berbulan-bulan. `Performance Monitoring Team HRGA` — metrik **terberat bersama** dan
> menurut tabel ini **bisa otomatis sekarang** — diabaikan karena dikira berbobot nol.
>
> **Jangan menyalin bobot dari tabel ini ke kode.** Ia sudah tersedia hidup di
> `GET /kpi/auto-overview`.

### Personalia

Template `Personalia Team`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Administrasi 1` | Terselesaikannya administrasi payroll dan absensi karyawan sesuai dengan ketentuan perusahaan secara akurat | `kedisiplinan_absensi` / `kelengkapan_catatan`, menarik `GET /kpi/attendance` dari attendance-service. | ✅ **KONEKTOR SIAP** (2026-08-22, [#1379](https://github.com/bip-itteam-internal/bip-erp/pull/1379), live di prod). Sub-metrik `kelengkapan_catatan`, BUKAN `ketepatan_waktu`: yang dinilai ketuntasan pencatatan personalia (sisa hari `Pending`), bukan perilaku karyawannya. Cakupan **`perusahaan`**, reduksi `rasio_ambang`. |
| 0.2 | `Administrasi 2` | Terselesaikannya administrasi BPJS rekening dan surat-surat karyawan sesuai dengan ketentuan perusahaan | payroll_db baru 1 payroll_run; GET /employee/bpjs tersedia. | Bisa sebagian. Data BPJS sudah ada, tapi payroll baru berjalan sekali sehingga belum cukup jadi dasar penilaian. |
| 0.2 | `Administrasi 3` | Terselesaikannya administrasi kontrak karyawan baru dan perpanjang kontrak dengan tepat | `kontrak_karyawan`, membaca koleksi `employee_contract` (BUKAN salinan `work_data.contract_ending`, yang tak punya jejak perpanjangan). | ⚠️ **KONEKTOR SIAP, tetapi menjawab SEBAGIAN** (2026-08-22, [#1379](https://github.com/bip-itteam-internal/bip-erp/pull/1379)). Yang terukur cuma **perpanjangan**; kontrak karyawan BARU tak punya tenggat tercatat sehingga "dengan tepat" di sisi itu tak dapat dinilai tanpa mengarang tenggatnya. Pilihan sub-metrik: `perpanjangan_tepat_waktu` (proses, tetapi kosong pada bulan tanpa kontrak jatuh tempo) atau `sisa_hari_kontrak` (keadaan tunggakan, selalu bersampel). Keduanya `rasio_ambang` ambang 0, cakupan **`perusahaan`**. Menyalakannya = keputusan pemilik metrik menerima cakupan sebagian. |
| 0.25 | `Administrasi 4` | Pengkinian Data Karyawan terupdate secara akurat di drive utama | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.1 | `Kedisiplinan` | Kehadiran dan Ketepatan Waktu | `kedisiplinan_absensi` / `ketepatan_waktu`, menarik `GET /kpi/attendance` dari attendance-service. | ✅ **KONEKTOR SIAP** (2026-08-22, [#1379](https://github.com/bip-itteam-internal/bip-erp/pull/1379), live di prod). Menjawab pertanyaan yang sama dengan `SOP` milik OD dan sengaja membaca sumber yang sama persis, supaya dua metrik yang menanyakan hal yang sama tak dijawab dua angka berbeda. Cakupan: **`individu`** bila yang dinilai kedisiplinan si staf sendiri, **`perusahaan`** bila yang dinilai hasil kerjanya menjaga disiplin orang lain — putuskan eksplisit, keduanya sah menurut bunyinya. |

### Recruitment & Onboarding

Template `Recruitment`, 5 metrik. Dipegang **1 orang** (`BIP-0123-11-24`, aktif).

> ✅ **Disegarkan langsung dari prod 2026-09-02.** Template yang dipakai menilai kini bernama
> **`Recruitment`** (`6a891211a8f110c4ae85b6ba`, dibuat 22 Agu 2026). Template
> `Recruitment Team` yang tercatat di versi lama dokumen ini (`6a0bdc21af417b963150bdda`,
> Mei 2026) sudah berstatus **`arsip`** sejak 25 Agu 2026. Dua metriknya BERGANTI, bukan
> sekadar berganti kata: metrik ke-4 dari `Skor Kompetensi New Hire Fase On Boarding >80`
> jadi ketersediaan dokumen jobdesk, dan metrik ke-5 dari `Kaizen` jadi turnover masa
> probation (`key` ikut berubah `kaizen` → `turnover`). Verdict lamanya karena itu tidak
> boleh dibawa: yang lama sudah punya keputusan ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]),
> yang baru belum pernah dinilai sama sekali.

> [!warning] Di template ini `description` BUKAN tempat targetnya, berbeda dari bab lain
> Bab [[#Cara membaca]] menyatakan target sebenarnya tersimpan di `description`. Untuk
> template `Recruitment` itu **tidak berlaku**: kelima `description`-nya berbunyi seragam
> `Target 100%`, dan kalimat yang dulu jadi deskripsi kini pindah ke `label`. Kolom
> **Label** di bawah karena itu ditulis apa adanya dari `label` (panjang, dan memang begitu
> tersimpannya), sementara `key` disebut terpisah karena `key`-lah yang stabil lintas
> generasi template.

**Nol dari 5 metrik punya blok `auto`** (diukur ke `kpi_template` prod 2026-09-02), jadi
kelimanya masih diketik tangan. Skor terakhir orangnya `2026-07` = 87,5, seluruhnya manual
dan masih memakai snapshot template yang kini arsip; periode `2026-08` belum dinilai.

| Bobot | Label (`key`) | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Time to Fulfilment Rate ( < 30 Hari ) All Vacant` (`rekrutmen-seleksi-dan-penempatan`) | `Target 100%` | **Sisi buka ADA, sisi terpenuhi TIDAK.** `job_requisition` 6 + `job_posting` 1 di prod (2026-09-02) memberi tanggal mulainya. Ujung pengukurannya hilang di dua tempat sekaligus: koleksi `candidate` **belum pernah terbentuk**, dan `ReqStatus` berhenti di `Posted` tanpa status "terpenuhi" (`services/recruitment/models_requisition.go:20-32`). Begitu kandidat diisi, tanggal penutupnya ada di `candidate.status_changed_at` saat status `Hired` (`models_candidate.go:76`, `pipeline.go:7`) yang dipasangkan ke requisition lewat `posting_id`. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. Satu hal yang tetap perlu disepakati: dihitung sampai kandidat diterima, atau sampai orangnya masuk kerja. |
| 0.2 | `Membuat rencana jadwal dan pelaksanaan onboarding karyawan Masa Percobaan.` (`rekrutmen-seleksi-dan-penempatan-2`) | `Target 100%` | **Fiturnya lengkap dan sudah ter-deploy, datanya nol.** Checklist onboarding (template baku + instance per karyawan baru, `services/recruitment/models_onboarding.go:50-61`) terbukti ada di biner prod `Recruitment-Service` (`grep -ac onboarding_template` → 3, `onboarding_instance` → 4, kontrol negatif string karangan → 0). Koleksi `onboarding_template`, `onboarding_instance`, `onboarding_review` **belum pernah terbentuk** di `recruitment_db`. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu checklist onboarding sudah ada di sistem dan belum pernah dipakai sekali pun. |
| 0.2 | `Presentase Data Base Buffer Kebutuan MPP` (`rekrutmen-seleksi-dan-penempatan-3`) | `Target 100%` | **Paling dekat siap dari kelimanya, penyebutnya sudah terisi.** Rumus lembar KPI HRD (`Jumlah Database / Actual MPP * 100`) sudah diimplementasikan persis sebagai `GET /manpower-plans/coverage?tahun=YYYY` (`services/recruitment/mpp_coverage.go:64-67`, rute `routes.go:104`). Penyebutnya `manpower_plan` **3 baris tahun 2026** di prod. Pembilangnya nol karena ia mencacah kandidat berstatus `Buffer` (`mpp_coverage.go:136-162`) dan koleksi `candidate` kosong, jadi endpointnya hari ini selalu menjawab 0%. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Rencana MPP-nya sudah diisi; yang belum ada cuma daftar kandidat cadangannya. |
| 0.25 | `Ketersediaan Dokumen Jobdesk diseluruh posisi dan memastikan seluruh tim baru memahami jobdesk masing-masing` (`job-description`) | `Target 100%` | **TIDAK ADA tempat menyimpan jobdesk per posisi di sistem mana pun.** `hrd_document_db` berisi 1 dokumen (`hrd_document_type` 4, `hrd_document_version` 6), dan `employee_db` tidak punya koleksi master posisi. Yang paling mendekati hanyalah `job_requisition.kualifikasi.tugas_tanggung_jawab`, teks bebas per permintaan karyawan, bukan per posisi. Paruh kedua metriknya ("seluruh tim baru memahami") tak punya sumber sama sekali. | Belum bisa otomatis. Perlu diputuskan dulu apakah jobdesk per posisi layak disimpan di sistem, dan bagaimana pemahaman tim baru mau dibuktikan. |
| 0.1 | `Tingkat turnover Masa Probation 0%` (`turnover`) | `Target 100%` | ⚠️ **Bahannya ADA di `employee_db`, tapi sumber `turnover_karyawan` yang sudah terdaftar MENJAWAB PERTANYAAN LAIN.** Sumber itu menghitung resign **sukarela seluruh perusahaan** dan menolak cakupan selain `perusahaan` secara eksplisit (`kpi_sumber_turnover.go:25-34`, `:145-149`), jadi ia bukan turnover masa probation. Bahan mentahnya: `employee_resign` 6, `employee_contract` 403 (`PKWT` 347, `PKWT (Evaluasi)` 46, `Magang` 9, `PKWTT` 1), `work_data.join_date` 209. | Bisa otomatis, tapi sepakati dulu siapa yang dihitung "masa probation". Tipe kontrak saja tidak cukup: dua orang terakhir yang resign justru ber-kontrak `PKWT` biasa (`BIP-0248-08-26` masuk 3 Agu keluar 15 Agu; `BIP-0262-07-26` masuk 31 Jul keluar 19 Agu), bukan `PKWT (Evaluasi)`. Sesudah definisinya jelas, tetap butuh sumber KPI baru; `turnover_karyawan` tidak boleh dipakai apa adanya. |

**Akar masalahnya satu, bukan lima.** Modul recruitment ter-deploy penuh tetapi belum
dipakai: `recruitment_db` prod hanya berisi master data (`interview_round` 7,
`email_template` 7, `assessment_type` 4, `job_type` 1, `job_location` 1) ditambah
`job_requisition` 6, `job_posting` 1, `manpower_plan` 3, `audit_logs` 24. Koleksi
`candidate`, `interview`, `offer`, `candidate_test_result`, `background_check`, dan seluruh
`onboarding_*` **belum pernah terbentuk**, artinya nol dokumen sejak awal. Tiga dari lima
metrik di atas menunggu satu hal yang sama, yaitu data kandidat mulai diisi.

⚠️ **Ketiganya tetap butuh dev sesudah datanya terisi.** Tidak ada satu pun sumber KPI yang
menyentuh `recruitment_db` (lihat peringatan "Masih tidak ada sumber `recruitment`" di
[[#Dua kolom terakhir]]), grup sumber `sdm` baru berisi empat nama (`program_culture`,
`kontrak_karyawan`, `kedisiplinan_absensi`, `turnover_karyawan`, `kpi_sumber.go:82-87`), dan
recruitment-service belum punya rute `/internal/` untuk dikonsumsi employee-service. Jadi
"datanya sudah diisi" belum berarti angkanya muncul sendiri di KPI.

**Pergeseran klasifikasi akibat pembaruan ini**, supaya angka bab dan ringkasan bisa
ditelusuri: metrik 1, 2, 3 tetap *modul ada tapi datanya kosong*; metrik 4 pindah dari
kelompok itu ke *tidak ada sumber sama sekali*; metrik 5 masuk *sumber ada tapi butuh
definisi* menggantikan `Kaizen` yang manual karena keputusan. Bersih: terblokir 4 → 3,
semi 0 → 1, manual tetap 1.

### Training & Perfomance Officer

Template `People and Development`, 6 metrik. Dipegang **1 orang aktif**; dua pemegang lain di `work_data` sudah nonaktif.

> ✅ **Disegarkan langsung dari prod 2026-09-15, diukur ulang 2026-09-17** (`employee_db` + `learning_db`, baca-saja; lihat **Keadaan prod 2026-09-17** di bawah).
> Template yang dipakai menilai kini bernama **`People and Development`**
> (`6a891157a8f110c4ae85b6b9`, dibuat 22 Agu 2026). Template `People Development` yang
> tercatat di versi lama dokumen ini (`6a100f8bb55c29fbe5a1f196`, Mei 2026) berstatus
> **`arsip`** sejak 25 Agu 2026. Yang berubah lebih dari sekadar kata:
>
> - **Metrik bertambah satu**: `Kesesuaian materi LMS dengan jobdesk ` (`peningkatan-performance-2`, 0,15).
> - **Bobot bergeser**: skor penilaian training 0,2 → 0,35, terlaksana sesuai rencana 0,35 → 0,2, attendance rate 0,25 → 0,1.
> - ⚠️ **`key` `kpi` dipakai ulang untuk metrik yang BERBEDA.** Di template arsip ia berarti
>   *SLA pengumpulan KPI*, di template aktif *Employee Productivity 120 juta per karyawan*.
>   `key` adalah identitas metrik untuk otomasi yang sengaja dipertahankan walau labelnya
>   berubah (`KPIMetric.Key`, `shared-library/models/employee/models.go`), jadi pembacaan apa
>   pun yang menjajarkan metrik lintas generasi template lewat `key` akan menyamakan dua metrik
>   yang tak berhubungan. Bandingkan dengan [[#Recruitment & Onboarding]]: di sana `key` ikut
>   berganti (`kaizen` → `turnover`).
> - `description` mengikuti pola generasi 22 Agustus: kalimat metrik pindah ke `label`,
>   `description` berisi target. Lihat [[#Cacat yang sudah diketahui]].

**Nol dari 6 metrik punya blok `auto`** (diukur ulang 2026-09-17: masih nol, template terakhir diubah 25 Agu 2026), jadi keenamnya diketik tangan. Penetapan eksplisit
orangnya masih menunjuk template **arsip** (berlaku `2026-07`), dan untuk resolusi otomatis itu
tidak berdampak: kandidat resolusi hanya memuat template aktif (`templateKandidatPerPosisi`
dengan `hanyaAktif`, `services/employee/kpi_assignment.go:80-95`), dan posisi berkandidat
tunggal langsung memakainya (`pilihTemplateEfektif`, `kpi_auto_scores.go:97-102`). Skor yang
tersimpan juga memakai template yang benar: `2026-07` = 97,14 (template lama) dan `2026-08` =
80,95 (template aktif), keduanya tanpa `auto_value`. `metadata.created_by` kedua skor itu adalah
akun pemegang posisi sendiri, begitu pula pembuat template aktifnya; di data tidak ada jejak
penilai kedua. Apakah itu memang alurnya atau HRD Supervisor menilai di luar sistem: **TBD**,
perlu dikonfirmasi ke HR.

**Keadaan prod 2026-09-17** (ukur baca-saja; ⚠️ angka bergerak, ukur ulang sebelum dipakai):

- **Kode**: seluruh Tahap 1 sampai 3b sudah merged dan ter-deploy di prod. Repo server memuat merge
  bip-erp #1895, #1903, #1913, #1934 dan erp-frontend #1594, #1603, #1619; image `Learning-Service`,
  `Employee-Service`, dan `frontend-hris-dashboard` dibangun 2026-09-17 08:49 sampai 08:55 WIB, sesudah
  merge. Gerbang biner: `pre_test_terlewat`, `training_plan_item` (learning) dan
  `peningkatan_post_test_persen`, `rencana_pelatihan`, `kepuasan_trainer_skala10` (employee) ada,
  kontrol positif `gofiber` ada, string karangan 0; bundel FE memuat `pre_test_terlewat`, karangan 0.
- **MyBharata**: my-bharata #150, #151, #153 merged ke `dev`, tetapi rilis GitHub terakhir masih
  `v1.14.5+135` (2026-08-03). Peserta baru bisa mengerjakan ujian lewat **web**.
- **Data `learning_db`** (diukur ulang siang hari): `training` 7 (**6 `Completed`**, 1 `Ongoing`, satu
  bertaut materi), `training_participant` 3 (2 hadir), `course` 1, `quiz` 1 (**hanya jenis `post`**),
  `quiz_attempt` 0, `trainer_evaluation` 0, `training_plan_item` 0, `training_certificate` 0,
  `training_request` 0. Pagi hari masih `training` 2, keduanya `Ongoing`.
- ⛔ **Buntu yang dikhawatirkan sudah terjadi.** Kelas bertaut materi ("time management", 3 peserta)
  kini berstatus `Completed` (terakhir diubah 2026-09-17 09:47 WIB), sementara materinya belum punya
  bank soal PRE. Dengan
  aturan Tahap 3b ketiga pesertanya tak pernah bisa pre-test, sehingga post-test kelas itu terkunci
  permanen, dan status `Completed` tak bisa dikembalikan lewat aplikasi. Penanganannya belum
  diputuskan.

Ringkasnya (diperbarui 2026-09-17 sore): 3 metrik (bobot 0,4: rencana, kehadiran, kepuasan) punya
sumber otomatis live di prod yang sesuai definisinya; 2 metrik (bobot 0,5: skor penilaian training
dan kesesuaian materi) sumbernya **diputuskan ulang** lewat [[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]]
dan **kini punya sumber di kode**: `kenaikan_kpi_peserta_persen` dan `kesesuaian_materi_skala10`,
bip-erp [#1945](https://github.com/bip-itteam-internal/bip-erp/pull/1945) dan
[#1951](https://github.com/bip-itteam-internal/bip-erp/pull/1951) merged 2026-09-17 (koreksi: versi
pagi paragraf ini menulis "belum ada kodenya"). Keduanya terverifikasi sebagian di DEV, belum
di-deploy di prod, layar webnya belum merged, dan HR belum memasangnya. 1 metrik (bobot 0,1,
Employee Productivity) **definisinya diputuskan** pemilik proses 2026-09-17, yaitu laba bersih per
bulan seluruh grup (PT + 40 CV) dibagi seluruh karyawan, tetapi **tetap manual**: laba konsolidasi
PT + 40 CV belum ada di sistem mana pun, jadi metrik ini menunggu buku besar CV
([[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]]) menyediakan laba
CV, dan target 120 juta per karyawan per bulan belum dicocokkan kewajarannya ke Finance. Nol yang
sudah dikonfigurasi di template (per 2026-09-17).

⚠️ **Nilai `2026-08` tidak mungkin berasal dari modul Training.** Dibandingkan dengan isi
`learning_db` prod 2026-09-15 (perbandingan historis; keadaan terkini di atas):

| Metrik | Nilai diketik | Isi modul Training di prod |
|---|---:|---|
| Training attendance rate | 92 | `training_participant` **1** baris seumur hidup, `attended: false` |
| Skor penilaian training > 70 | 83 | `quiz_attempt` **0**, `quiz` **0**, koleksi `course` belum pernah terbentuk (⚠️ angka 2026-09-15, ukur ulang sebelum dipakai: layar ujian Tahap 3a/3b sedang menunggu merge) |
| Training satisfaction score | 77 | `trainer_evaluation` **0** |
| Terlaksana sesuai rencana | 100 | `training` **2**: *time management* (14 Agu) masih `Scheduled` dengan 0 hadir; *Pendampingan Alur Distribusi Offline* (mulai 10 Agu) baru diinput 10 Sep, 13 menit **sesudah** skor Agustus disimpan |

Nilainya dicatat di luar sistem, dan modul yang semestinya menjadi sumbernya baru mulai diisi
10 Sep 2026.

| Bobot | Label (`key`) | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Terlaksananya kegiatan training & performance officer sesuai dengan rencana.` (`training-development`) | `Target 100%` | ✅ **Entitas rencana dan sumber KPI-nya sudah MERGED** (Tahap 2 Training & Performance Officer, bip-erp PR [#1903](https://github.com/bip-itteam-internal/bip-erp/pull/1903) dan [#1904](https://github.com/bip-itteam-internal/bip-erp/pull/1904); diukur ke `origin/main` 2026-09-16 berikut kontrol negatif). ✅ **Ter-deploy di prod** (gerbang biner 2026-09-17: `training_plan_item` di learning, `rencana_pelatihan` di employee). Prod 2026-09-17: `training_plan_item` **0**. Rencana tahunan tersimpan sebagai butir `training_plan_item`, satu dokumen = satu "pelatihan X direncanakan bulan M tahun T", terpisah dari kelas `Training` yang dijadwalkan (`services/learning/models_rencana.go:69-87`). Sumber baru `rencana_pelatihan` di employee-service (`services/employee/kpi_sumber_rencana_pelatihan.go:28`) menghitung: **penyebut** = butir rencana **aktif** (bukan `dibatalkan`) bulan target itu; **pembilang** = butir yang kelas tertautnya `Completed` selesai **DI DALAM** bulan target itu (`awalBulanWIB <= end_date < batasBulanWIB`, fungsi `statusButirRencana`, `services/learning/models_rencana.go:138-172`, dipakai bersama layar Rencana **dan** rute KPI supaya keduanya tak berselisih). Kelas yang selesai **sebelum** bulan target sama sekali tidak dihitung; yang selesai **sesudah** bulan target (`terlaksana_terlambat`) tetap masuk penyebut tapi bernilai 0, tidak menambah pembilang (`services/employee/kpi_sumber_rencana_pelatihan.go:107-146`). Butir `dibatalkan` dikeluarkan dari penyebut sepenuhnya. Sumber ini SELALU cakupan **perusahaan**; team/department sengaja tak didaftarkan karena kodenya tak pernah membaca setelan cakupan (`kpi_sumber_rencana_pelatihan.go:166-171`). Sumber ini TERPISAH dari `pelatihan`, bukan sub-metrik keempatnya: penyebutnya butir rencana perusahaan, bukan karyawan (`kpi_sumber_rencana_pelatihan.go:22-25`). | Belum bisa dipakai sekarang: kodenya sudah live di prod, tetapi belum ada satu pun butir rencana dan template belum dikonfigurasi. Training Officer menyusun butir lewat menu Rencana Pelatihan, lalu HR isi Atur Target: sumber `rencana_pelatihan`, formula `rata_rata`, cakupan `perusahaan`, target 100, arah naik — tapi penyebutnya baru terisi kalau Training Officer sudah menyusun butir rencana lewat menu Rencana Pelatihan untuk bulan itu; kalau belum ada butir, sumbernya membalas "belum dapat dihitung" (`kpi_sumber_rencana_pelatihan.go:136-137`). |
| 0.1 | `Training Attendance Rate` (`training-development-2`) | `Target 100%` | `training_participant.attended` (boolean, ditandai HR atau lewat hadir mandiri berjendela waktu). Prod 2026-09-17 (diukur ulang siang hari): **7** kelas, **6** sudah `Completed`; satu-satunya kelas selesai yang berpeserta ("time management", selesai 12 September) punya **3** peserta dan **2** hadir, jadi September sudah bisa dihitung **66,7%** begitu sumbernya dipasang. ✅ **Konektor ada sejak 2026-09-15** (live di produksi): sumber `pelatihan` / `kehadiran_peserta_persen` ([[Microservices - Employee Service]]), satu nilai 0 atau 100 per pendaftaran di kelas `Completed` yang selesai di bulan itu. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu peserta dan kehadiran sudah ada, hanya belum diisi, dan kelas baru terhitung sesudah statusnya **Completed**. Begitu terisi, HR tinggal mengisi Atur Target: sumber `pelatihan`, metrik `kehadiran_peserta_persen`, cakupan `perusahaan`, formula `rata_rata`, target 100, arah naik. |
| 0.35 | `Skor Penilaian Training All Karyawan > 70 ` (`peningkatan-performance`) | `Target 100% > 70` | ✅ **Sumber yang diputuskan [[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]] kini ada di kode** (koreksi 2026-09-17: sebelum dua merge berikut, sel ini hanya memuat sumber post-test di bawah): `pelatihan` / **`kenaikan_kpi_peserta_persen`**. bip-erp [#1945](https://github.com/bip-itteam-internal/bip-erp/pull/1945) (merged 2026-09-17 07:51 UTC) menambah `bulan_mulai` dan `bulan_selesai` (bulan kalender WIB) pada tiap pendaftaran di `GET /kpi/pelatihan` (`services/learning/kpi_pelatihan.go:83-88`, `:297-298`); [#1951](https://github.com/bip-itteam-internal/bip-erp/pull/1951) (merged 2026-09-17 08:49 UTC) menambah metriknya. Periode P menilai kelas `Completed` yang selesai di P-2 (`jedaBahanPelatihan`, `services/employee/kpi_sumber_pelatihan.go:65-69`). Satuannya **per PENDAFTARAN kelas, hanya peserta HADIR** (keputusan pemilik proses 2026-09-17): orang yang ikut dua kelas dinilai dua kali, masing-masing dengan bulan kelasnya sendiri. Skor KPI tersimpan bulan sebelum bulan mulai kelas dibanding bulan sesudah bulan selesai (`bulanPembandingKenaikan`, `kpi_sumber_pelatihan.go:584-594`); naik bernilai 100, sama atau turun 0, tanpa ambang. Skor salah satu bulan tak ada: keluar dari nilai, tetap di populasi (populasi = pendaftaran hadir). Tanpa peserta hadir: *belum dapat dihitung*; seluruh peserta hadir tanpa bulan kelas: galat biasa, tanda learning versi lama (`cuplikanKenaikanKPIPeserta`, `kpi_sumber_pelatihan.go:633-724`). Catatan metriknya menyebut bulan kelas, dan dua bulan yang dibandingkan bila hanya ada satu pasangan. ⚠️ **DEV 2026-09-17 (sekitar 15.50-16.05 WIB) terverifikasi sebagian**: pipeline dev menaikkan Employee-Service tetapi melewatkan Learning-Service, jadi learning dibangun ulang manual; gerbang biner kedua service lalu memuat kode baru (kontrol positif ada, string karangan 0), dan katalog sumber `pelatihan` lewat gateway DEV membawa 6 metrik. **Belum terbukti**: perhitungan metrik ini lewat template di DEV (tak ada template ber-blok `auto`, dan `POST /kpi/auto-values/pratinjau` sudah dicabut [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] §6). **PROD belum di-deploy.** Data prod 2026-09-17 (baca-saja, ⚠️ ukur ulang sebelum dipakai): `kpi_score` 165 karyawan untuk `2026-07` dan 108 untuk `2026-08`; kelas `Completed` berpeserta 2, dan kelas yang selesai Juli punya 1 peserta berskor di kedua bulan pembanding, jadi metrik periode `2026-09` bisa berangka dari **satu orang** begitu prod di-deploy dan template dipasang (hitungan kelas berpeserta ini tidak sama dengan hitungan siang di baris `Training Attendance Rate`). **Riwayat sumber post-test** (tetap ada untuk kelulusan dan sertifikat, bukan lagi kandidat metrik ini; rujukan baris `kpi_sumber_pelatihan.go` dan `kpi_pelatihan.go` di bawah diperbarui ke `origin/main` sesudah #1951): **Post-test berskor sudah ADA dan ter-deploy** (bip-erp [#1321](https://github.com/bip-itteam-internal/bip-erp/pull/1321), merged 2026-08-20; biner prod memuat `quiz_attempt`, kontrol negatif 0): `course` + `quiz` + `quiz_attempt`, skor dinilai terhadap snapshot soal. Prod 2026-09-17: `course` **1**, `quiz` **1** (hanya bank soal `post`), `quiz_attempt` **0** (⚠️ ukur ulang sebelum dipakai). ✅ **Konektor ada sejak 2026-09-15** (live di produksi): sumber `pelatihan` / `skor_post_test_persen`, skor terbaik tiap peserta kelas bertautan post-test; yang belum mengerjakan tetap di populasi. ✅ **Layarnya sudah live di prod web** (diukur 2026-09-17): Tahap 3a (bip-erp [#1913](https://github.com/bip-itteam-internal/bip-erp/pull/1913), erp-frontend [#1603](https://github.com/bip-itteam-internal/erp-frontend/pull/1603), my-bharata [#151](https://github.com/bip-itteam-internal/my-bharata/pull/151)) merged 2026-09-16 dan Tahap 3b (bip-erp [#1934](https://github.com/bip-itteam-internal/bip-erp/pull/1934), erp-frontend [#1619](https://github.com/bip-itteam-internal/erp-frontend/pull/1619), my-bharata [#153](https://github.com/bip-itteam-internal/my-bharata/pull/153)) merged 2026-09-17, keduanya ter-deploy di prod; sisi MyBharata baru di `dev`, belum dirilis. Tahap 3a menambahkan **batas mengulang** (`max_attempt`, `retry_cooldown_hours`), yang ada justru karena metrik ini memakai **skor terbaik**: tanpa kuota, ia mengukur ketekunan mengulang alih-alih kemampuan. **Tahap 3b** mengubah dua hal yang menyentuh metrik ini. (1) Kelulusan post-test kini berarti skor **naik dari pre-test**, bukan ambang angka ("Nilai Lulus" dihapus), dan post-test terkunci sampai pre-test dikerjakan (`services/learning/skoring.go:38-103`). (2) Sumber `pelatihan` mendapat pilihan otomatis kedua, jadi metrik ini punya **dua** kandidat sumber: **`skor_post_test_persen`** = **penguasaan akhir**, rata-rata skor post-test terbaik (persen) peserta yang sudah mengerjakan, sedangkan peserta wajib yang belum mengerjakan dikeluarkan dari nilai tetapi tetap di populasi (`services/employee/kpi_sumber_pelatihan.go:396-436`; `services/learning/kpi_pelatihan.go:169-197`). **`peningkatan_post_test_persen`** = **efektivitas pelatihan**, persen peserta yang skor post-testnya naik dari pre-test (nilai 100 atau 0 per peserta; yang pre atau post-nya belum lengkap dikeluarkan dari nilai tetapi tetap di populasi) (`kpi_sumber_pelatihan.go:438-499`; `kpi_pelatihan.go:199-250`). Keduanya **bisa bergerak berlawanan**: kelas berisi peserta yang sudah mahir menghasilkan skor tinggi dengan peningkatan rendah (`kpi_sumber_pelatihan.go:43-50`). ⛔ **Jangan dijumlahkan** atau dirata-ratakan jadi satu angka: keduanya membaca peserta yang sama dari sudut berbeda, dan satu metrik template memakai **salah satu**. Arti `skor_post_test_persen` sengaja tidak diubah supaya template yang sudah memakainya tak berganti makna diam-diam (`kpi_sumber_pelatihan.go:48-50`). ⚠️ Karena post-test terkunci tanpa pre-test, peserta yang melewatkan pre-test sampai kelasnya ditutup tak akan pernah punya skor post, jadi cakupan **kedua** metrik tak bisa penuh untuk kelas itu. Alur bisnisnya di [[HRIS - Training Program]] (Alur Ujian E-Learning). | ⚠️ **Definisi diputuskan ulang 2026-09-17 dan sumbernya merged hari yang sama, tetapi belum bisa dipakai** (koreksi 2026-09-17: versi sebelumnya sel ini berbunyi "kode belum ada", benar sampai bip-erp #1951 merged): arti metrik ini adalah **apakah skor KPI peserta naik** dari bulan sebelum pelatihan ke bulan sesudahnya, **tanpa ambang 70** (keputusan pemilik proses), dihitung per pendaftaran kelas atas peserta hadir lewat `pelatihan` / `kenaikan_kpi_peserta_persen`. Langkah tersisa, berurutan: (1) ✅ label dan satuan metrik baru di Atur Target merged lewat erp-frontend [#1631](https://github.com/bip-itteam-internal/erp-frontend/pull/1631) 2026-09-17 09:19 UTC; (2) deploy PROD oleh **manusia**: `learning-service` dan `employee-service` naik bersama, erp-frontend **sesudah** learning, lalu buktikan biner **kedua** service karena pipeline DEV sempat melewatkan learning pada merge ini; (3) HR mengisi Atur Target: sumber `pelatihan`, metrik `kenaikan_kpi_peserta_persen`, formula `rata_rata`, cakupan `perusahaan`, target dalam persen, arah naik. Sampai langkah 3 selesai metrik ini tetap diketik manual, dan angka periode `2026-09` yang pertama kemungkinan berasal dari satu orang. Keputusan dan batasannya (jeda dua bulan, template bisa berganti antar bulan, cakupan skor 107-165 karyawan per bulan, kenaikan bukan bukti sebab-akibat) di [[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]]. Sumber post-test (`skor_post_test_persen`, `peningkatan_post_test_persen`) tetap ada untuk kelulusan dan sertifikat, tetapi **bukan lagi kandidat metrik ini**. ⚠️ Koreksi atas catatan sebelumnya: rumus seluruh metrik `pelatihan` (kini enam) dipaku server ke `rata_rata` (`kpi_sumber_pelatihan.go:300-307` per `origin/main` sesudah #1951) dan layar Atur Target tidak menawarkan `rasio_ambang` untuknya; saran "`rasio_ambang` ambang 70" di versi lama baris ini keliru terhadap kode. |
| 0.15 | `Kesesuaian materi LMS dengan jobdesk ` (`peningkatan-performance-2`) | `Target Skala 10` | ✅ **Sumber ada di kode sejak 2026-09-17** (koreksi 2026-09-17: sel ini sebelumnya dibuka "**TIDAK ADA sumber.**", benar sampai dua merge berikut; yang tetap tidak ada, jobdesk dan materi LMS, dicatat di akhir sel). Penilainya peserta, sesuai [[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]]. bip-erp [#1945](https://github.com/bip-itteam-internal/bip-erp/pull/1945) (merged 2026-09-17 07:51 UTC): kiriman penilaian pasca-pelatihan `POST /me/trainings/:id/evaluation` menerima `kesesuaian_materi` 1-10 **opsional** (tak dikirim tetap sah; 0 dan di atas 10 ditolak 400) (`ValidateKesesuaianMateri`, `services/learning/models_evaluation.go:95-107`; `services/learning/evaluation.go:99-115`), disimpan sebagai field sendiri di `trainer_evaluation`, di luar empat aspek `ratings` (`models_evaluation.go:50-60`). Agregatnya **hanya per kelas**, tidak per trainer (`evaluation.go:51-85`; `models_evaluation.go:78-81`), dengan ambang 3 responden yang menjawab (`models_evaluation.go:84-93`, `:121-139`), dan satu saringan jawaban dipakai bersama bahan KPI (`jawabanKesesuaianSah`, `models_evaluation.go:109-119`; `services/learning/kpi_pelatihan.go:329-334`). `GET /kpi/pelatihan` selalu membawa kunci `kesesuaian`, juga saat nol responden (`kpi_pelatihan.go:91-100`, `:123-125`). [#1951](https://github.com/bip-itteam-internal/bip-erp/pull/1951) (merged 2026-09-17 08:49 UTC): sumber `pelatihan` / **`kesesuaian_materi_skala10`** = rata-rata jawaban 1-10 apa adanya atas kelas `Completed` yang selesai di periode itu, minimal 3 jawaban gabungan seluruh batch (di bawahnya *belum dapat dihitung*); `kesesuaian` yang tak dibawa learning (versi lama, atau satu batch saja tak membawanya) adalah **galat biasa**, bukan *belum dapat dihitung*, supaya HR tak menagih peserta untuk masalah deploy (`services/employee/kpi_sumber_pelatihan.go:237-269`, `:532-568`). ⛔ Sejajar dengan `kepuasan_trainer_skala10`, tak boleh dijumlah atau dirata-rata bersamanya (`kpi_sumber_pelatihan.go:35-38`). ⚠️ **DEV 2026-09-17 (sekitar 15.50-16.05 WIB) terverifikasi sebagian** lewat gateway, sesudah learning dibangun ulang manual karena pipeline dev melewatkannya: agregat per kelas membawa `kesesuaian` dan agregat per trainer tidak; `kesesuaian_materi` 0 dan 11 ditolak 400; kiriman tanpa kesesuaian 201; kiriman bernilai 8 tersimpan terpisah dari `ratings` dan agregat per kelas mencatat responden 1 (di bawah ambang, angkanya tersembunyi). **Belum terbukti**: perhitungan metrik lewat template di DEV. **PROD belum di-deploy**; `trainer_evaluation` prod 2026-09-17: **0**. **Yang tetap tidak ada, dan tak lagi dibutuhkan metrik ini:** `course` hanya berisi judul, deskripsi, dan ambang lulus; materi PDF dan video belum ada (`services/learning/models_course.go`). Sejak Tahap 3a/3b (merged dan ter-deploy per 2026-09-17) ambang lulus dibuang dan `course` berisi judul, deskripsi, batas percobaan, dan jeda mengulang; materi PDF dan video tetap belum ada (`models_course.go:12-44`; `git grep` 2026-09-17 atas `origin/main`: `material_url`, `talent_pool`, dan `TalentPool` nol berkas; `video_url`, `curriculum`, dan `kurikulum` hanya muncul di integration, marketing-analytics, recruitment, dan modul mutasi, tidak di service learning). Jobdesk per posisi juga belum punya tempat di sistem mana pun (lihat metrik jobdesk di [[#Recruitment & Onboarding]]). | ⚠️ **Penilai diputuskan 2026-09-17 dan sumbernya merged hari yang sama, tetapi belum bisa dipakai** (koreksi 2026-09-17: versi sebelumnya sel ini berbunyi "kode belum ada", benar sampai bip-erp #1945 dan #1951 merged): yang menilai adalah **peserta pelatihan**, satu pertanyaan 1-10 "seberapa sesuai materi pelatihan ini dengan pekerjaan Anda" pada kiriman penilaian pasca-pelatihan yang sama, disimpan TERPISAH dari empat aspek trainer, lewat `pelatihan` / `kesesuaian_materi_skala10` (rata-rata langsung, minimal 3 jawaban, semua kelas `Completed`). Karena peserta tahu pekerjaannya sendiri, metrik ini **tidak menunggu** jobdesk per posisi maupun materi PDF/video. Langkah tersisa, berurutan: (1) ✅ merged lewat erp-frontend [#1631](https://github.com/bip-itteam-internal/erp-frontend/pull/1631) 2026-09-17 09:19 UTC (⚠️ halaman web Pelatihan Saya tak punya menu sidebar sejak 2026-08-13, jadi peserta hanya menjangkaunya lewat tautan langsung): dialog penilaian di Pelatihan Saya menanyakan kesesuaian 1-10 **opsional** yang tak menahan tombol Kirim dan kini berjudul "Penilaian Pelatihan", ringkasan penilaian HR per kelas menampilkan blok kesesuaian dengan ambangnya sendiri, dan Atur Target mendapat label serta satuan metrik baru; (2) deploy PROD oleh **manusia**: `learning-service` dan `employee-service` naik bersama, erp-frontend **sesudah** learning, karena learning lama mengabaikan `kesesuaian_materi` sehingga kiriman tetap 201 dan jawabannya hilang tanpa galat, padahal tiap peserta hanya bisa menilai sekali per kelas; (3) HR mengisi Atur Target: sumber `pelatihan`, metrik `kesesuaian_materi_skala10`, formula `rata_rata`, cakupan `perusahaan`, target dalam **skala 1-10** (bukan 0-100), arah naik. MyBharata **ditunda** (rilis terakhir masih `v1.14.5`), jadi untuk sementara peserta menilai lewat **web**. Angkanya baru muncul sesudah ada minimal 3 jawaban gabungan dari kelas yang selesai pada periode itu; prod 2026-09-17 masih 0 evaluasi. ⛔ **Jangan** diturunkan dari aspek `manfaat` evaluasi trainer: aspek itu sudah dijumlah ke `kepuasan_trainer_skala10`, jadi angka yang sama akan terhitung dua kali di template yang sama. Keputusan lengkap di [[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]]; jobdesk per posisi dipisah jadi keputusan sendiri bersama metrik jobdesk di [[#Recruitment & Onboarding]]. |
| 0.1 | `Memastikan Employee Productivity sebesar 120 juta per Employee ` (`kpi`) | `Target 100%` | Bahan mentahnya ADA di dua service: pendapatan dari laporan laba rugi Accurate lewat `GET /accounting/profit-loss` (integration-service meneruskannya ke `profit-loss.do` Accurate, `accurate_client_report.go:94`) dan jumlah karyawan dari `work_data`. **Tidak ada sumber KPI** yang menggabungkan keduanya. Metrik serupa di [[#HRD Supervisor]] (`Employee Productivity sebesar 120 Juta per Employee ( DIv. Marketing )`) dipetakan ke modul Training, jadi kedua baris belum sepakat soal apa yang diukur. | Bisa otomatis, tapi sepakati dulu: pendapatan seluruh perusahaan atau hanya Divisi Marketing (label di HRD Supervisor menyebut Div. Marketing), per bulan atau per tahun, dan karyawan mana yang jadi penyebut. Sesudah itu tetap butuh dev menulis sumber baru. Metrik ini dan milik HRD Supervisor wajib didefinisikan **sekali** untuk keduanya. **Koreksi 2026-09-17:** pemilik proses memutuskan definisinya, yaitu laba bersih per bulan **seluruh grup (PT + 40 CV)** dibagi **seluruh karyawan**. Pertanyaan di atas terjawab untuk metrik ini, tetapi "bisa otomatis" tidak berlaku lagi: bahan di kolom Sumber hanya menutup PT (laporan laba rugi Accurate), sedangkan laba konsolidasi PT + 40 CV belum ada di sistem mana pun. Metrik ini **tetap manual** sampai buku besar CV ([[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]]) menyediakan laba 40 CV; konsolidasi tahap pertamanya pun hanya 40 CV tanpa PT. Target 120 juta per karyawan per bulan belum dicocokkan kewajarannya ke Finance. Apakah definisi ini juga berlaku untuk metrik serupa di [[#HRD Supervisor]] (labelnya menyebut Div. Marketing) belum dikonfirmasi. |
| 0.1 | `Training Satisfaction Score ( 1 - 10 )` (`pelayanan`) | `Target Skala 10` | Evaluasi pasca-pelatihan ADA (`trainer_evaluation`: peserta menilai trainer pada empat aspek **1..5**, agregat baru tampil setelah 3 responden, `services/learning/models_evaluation.go`). Prod 2026-09-17: **0** evaluasi. ✅ **Skala dan konektor beres 2026-09-15**: keputusan hari itu formulir tetap 1-5, dan sumber `pelatihan` / `kepuasan_trainer_skala10` mengonversinya (rata-rata empat aspek × 2), live di produksi; di bawah 3 responden gabungan berbunyi *belum dapat dihitung*. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Datanya belum ada (0 evaluasi). Begitu terisi, isi Atur Target dengan sumber `pelatihan`, metrik `kepuasan_trainer_skala10`, formula `rata_rata`, target dalam skala 1-10 (bukan 0-100), arah naik. |

**Akar masalahnya satu untuk empat metrik (bobot 0,75): modul Training ter-deploy tetapi belum
dipakai.** Per 2026-09-17 siang `learning_db` prod berisi `training` 7 (6 `Completed`),
`training_participant` 3, `trainer` 4, `training_type` 25, `course` 1, `quiz` 1, sedangkan
`training_plan_item`, `training_request`, `trainer_evaluation`, `quiz_attempt`, dan
`training_certificate` nol (⚠️ angka 2026-09-17, ukur ulang sebelum dipakai).

✅ **Konektornya ada sejak 2026-09-15** (bip-erp [#1895](https://github.com/bip-itteam-internal/bip-erp/pull/1895), live di produksi): sumber `pelatihan` di [[Microservices - Employee Service]] dengan `kehadiran_peserta_persen`, `skor_post_test_persen`, dan `kepuasan_trainer_skala10`, menarik `GET /kpi/pelatihan` dari service `learning`. Catatan pagi hari yang sama ("tidak ada satu pun sumber KPI yang membaca `learning_db`") benar sebelum merge. Sejak 2026-09-17 entitas rencana tahunan (Tahap 2) dan layar pre/post-test (Tahap 3a/3b, termasuk metrik keempat `peningkatan_post_test_persen`) juga live di prod web. Untuk metrik yang sumbernya sudah sesuai definisi, yang tersisa bukan kode: data (kelas baru terhitung sesudah `Completed`; hanya satu kelas selesai yang berpeserta; rencana, percobaan, dan evaluasi masih nol), konfigurasi `auto` di template oleh HR (nol per 2026-09-17), dan rilis MyBharata. `Skor Penilaian Training` dan `Kesesuaian materi LMS dengan jobdesk` sumbernya sesuai [[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]] sudah merged 2026-09-17 (bip-erp #1945 dan #1951) dan kini menunggu merge layar web, deploy prod, dan konfigurasi HR (catatan sebelumnya "menunggu kode" benar sampai merge itu). `Employee Productivity` definisinya diputuskan 2026-09-17, tetapi bahannya (laba PT + 40 CV) belum ada di sistem mana pun, jadi tetap manual.

**Klasifikasi tidak bergeser** karena pembaruan 2026-09-15 sore: konektor yang kini ada tidak mengubah kategori *modul ada tapi datanya kosong*, dan ketiga metrik bersumber `pelatihan` tetap di sana sampai datanya terisi.

**Pergeseran klasifikasi akibat pembaruan ini**, supaya angka bab dan ringkasan bisa
ditelusuri. Basis lamanya dibaca dari teks bab versi sebelumnya: empat metrik *modul ada tapi
datanya kosong* dan satu (`KPI`, SLA pengumpulan) *sumber ada dan terisi*, karena
Rekomendasinya berbunyi "Bisa otomatis sekarang". Template aktif: empat *modul ada tapi datanya
kosong* (rencana, attendance, skor, kepuasan), satu *sumber ada tapi butuh definisi*
(productivity), dan satu *tidak ada sumber sama sekali* (LMS vs jobdesk). Bersih: otomatis 1 → 0,
semi 0 → 1, terblokir tetap 4, manual 0 → 1, metrik 31 → 32.

⚠️ **Satu *otomatis* yang hilang bukan kemampuan yang hilang.** Sumber yang ditunjuk baris lama,
`GET /task-management/report/sla`, mengukur tenggat **tiket** Task Management (konektor KPI-nya
di `services/employee/kpi_sumber_tiket.go`), bukan ketepatan **pengumpulan KPI**. Vonis "bisa
otomatis sekarang" di baris itu sudah salah petak sejak awal.

## Kesekretariatan

7 template, 28 metrik. Klasifikasi otomasi: **0 / 0 / 0 / 28**.

### Company Branding

Template `COMPANY BRANDING`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Perfomance & Engagement 1` | Persentase kenaikan engagement rate (ER) instagram dalam sebulan (min. Rata-rata 3%) | Instagram dan TikTok organik akun company TIDAK terintegrasi. Yang ada hanya TikTok Business/Shop, Shopee, Lazada, Accurate. | Belum bisa otomatis. Akun media sosial perusahaan belum tersambung ke sistem. |
| 0.25 | `Perfomance & Engagement 2` | Persentase kenaikan engagement rate (ER) TikTok dalam sebulan (min. Rata-rata 5%). | Instagram dan TikTok organik akun company TIDAK terintegrasi. Yang ada hanya TikTok Business/Shop, Shopee, Lazada, Accurate. | Belum bisa otomatis. Akun media sosial perusahaan belum tersambung ke sistem. |
| 0.3 | `Perfomance & Engagement 3` | Jumlah konten yang disetujui unggah sosial media (Tiktok dan Instagram) dalam sehari. | Instagram dan TikTok organik akun company TIDAK terintegrasi. Yang ada hanya TikTok Business/Shop, Shopee, Lazada, Accurate. | Belum bisa otomatis. Akun media sosial perusahaan belum tersambung ke sistem. |
| 0.15 | `Manajemen Waktu` | Membuat konten planner dan melaksanakan sesuai jadwal. | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |

### Corporate Secretary

Template `CORPORATE SECRETARY`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Manajemen Jadwal Direktur` | Persentase agenda berjalan tanpa bentrok dan sesuai jadwal. | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.25 | `Kualitas & Ketepatan Dokumen Direktur` | Tingkat kesalahan dalam surat, laporan, dan bahan presentasi sesuai standar. | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.3 | `Supporting Agenda Direktur` | Penyelesaian Instruksi Direktur | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.25 | `Penyediaan Laporan dan Data Direktur` | Akurasi Laporan ke Direktur | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |

### Graphic Design

Template `GRAPHIC DESIGNER`, 3 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.35 | `Graphic Content untuk produk kemasan` | Persentase design yang disetujui oleh pengaju dan diserahkan 1 hari setelah form pengajuan ditandatangani. | TIDAK ADA tracker garapan desain/video (pengajuan, persetujuan, tenggat). Metriknya menilai mutu dan ketepatan garapan, bukan performa video di marketplace. | Tetap manual. Yang dinilai mutu dan ketepatan garapan, dan itu penilaian orang. Yang bisa dibantu sistem hanya ketepatan waktunya, kalau ada pencatatan pengajuan dan tenggat. |
| 0.35 | `Product Design untuk kebutuhan perusahaan` | Persentase design disetujui perusahaan dan diserahkan 1 hari setelah form pengajuan ditandatangani. | TIDAK ADA tracker garapan desain/video (pengajuan, persetujuan, tenggat). Metriknya menilai mutu dan ketepatan garapan, bukan performa video di marketplace. | Tetap manual. Yang dinilai mutu dan ketepatan garapan, dan itu penilaian orang. Yang bisa dibantu sistem hanya ketepatan waktunya, kalau ada pencatatan pengajuan dan tenggat. |
| 0.3 | `Graphic Content untuk marketing` | Persentase design yang disetujui oleh marketing officer dan diserahkan 1 hari setelah form pengajuan ditandatangani. | TIDAK ADA tracker garapan desain/video (pengajuan, persetujuan, tenggat). Metriknya menilai mutu dan ketepatan garapan, bukan performa video di marketplace. | Tetap manual. Yang dinilai mutu dan ketepatan garapan, dan itu penilaian orang. Yang bisa dibantu sistem hanya ketepatan waktunya, kalau ada pencatatan pengajuan dan tenggat. |

### Internal Audit

Template `INTERNAL AUDIT`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.15 | `Kepatuhan Implementasi Kebijakan` | Persentase kebijakan dan arahan Direktur yang dijalankan sesuai standar. | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.2 | `Akurasi dan Validitas Data Laporan` | Tingkat kesalahan data dalam laporan lintas divisi Error ≤ 2% | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.25 | `Ketepatan Monitoring dan Follow Up` | Persentase Penyelesaian Temuan (Closing Finding Rate) | Stok & penjualan tersedia, tapi tanpa modul demand planning sebagian metrik ini tidak terdefinisi. | Bisa sebagian. Data stok dan penjualan ada, tapi rumusnya perlu disepakati dulu karena belum ada perencanaan permintaan. |
| 0.15 | `Efektivitas Kontrol dan Deteksi Issue` | Jumlah issue/kendala yang teridentifikasi sebelum berdampak besar. | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.25 | `Kedisiplinan Sistem & Koordinasi Divisi` | Kelengkapan laporan, & Kejelasan rekomendasi ( Target 100 % ) Sesuai | GET /attendance/report?date=YYYY-MM (status Hadir/Terlambat/Alpha + late_hour). 24.163 entri, periode 26 ke 26 sesuai payroll. | Bisa otomatis sekarang. Data absensi lengkap dan periodenya sudah mengikuti siklus gajian. |

### Personal Assistant

Template `PERSONAL ASSISTANT`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Ketepatan Manajemen Jadwal Direktur` | Persentase agenda berjalan tanpa bentrok/terlewat | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.25 | `Ketepatan & Kecepatan Penyelesaian Tugas` | Persentase tugas Direktur selesai tepat waktu & sesuai instruksi | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.3 | `Kelancaran Perjalanan & Agenda Khusus` | Tingkat kesiapan & kelancaran perjalanan dinas tanpa kendala | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.15 | `Responsivitas & Kerahasiaan` | Kecepatan respon & keamanan informasi Direktur | TIDAK ADA data percakapan CS / chat marketplace. | Belum bisa otomatis. Percakapan dengan pembeli belum masuk ke sistem. |

### QA RND

Template `R&D REGULATORY`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.1 | `Zero major finding saat external audit dengan BPOM` | memastikan seluruh aktivitas sesuai regulasi (BPOM, GMP, HACCP, dll) | TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM. | Belum bisa otomatis. Temuan audit, pelaporan pajak, dan izin BPOM belum dicatat di sistem. |
| 0.4 | `Net income 20%` | Product Development Support | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.25 | `Inovation & Improvement` | Meningkatkan Inovasi & Efisiensi Produk | ⚠️ **Bukan dilayani sumber Kaizen.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) tetapi ia menghitung **jumlah ide**, sedangkan metrik ini mengukur "inovasi & efisiensi produk" yang tak punya definisi terukur di sistem mana pun — jadi `kaizen_ide_*` tak akan menjawabnya walau [[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]] dicabut. | Perlu didefinisikan ulang dulu. Modul pencatat ide sudah ada, tapi metrik ini tidak menyebut angka yang bisa dihitung dari sana — sepakati dulu dengan pemilik metrik apa sebenarnya yang dinilai. |
| 0.25 | `New Product Readiness (Permit & Licence from BPOM) di Q1` | Penyelesaian izin BPOM & Halal sebelum deadline launching | TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM. | Belum bisa otomatis. Temuan audit, pelaporan pajak, dan izin BPOM belum dicatat di sistem. |

### Video Editor

Template `VIDEOGRAPHER & EDITOR COMPANY`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.35 | `Lead Time` | Persentase pengambilan dan edit Video Content berdasarkan transisi, editing, dan hasil akhir selesai tepat waktu untuk pemenuhan perusahaan. | TIDAK ADA tracker garapan desain/video (pengajuan, persetujuan, tenggat). Metriknya menilai mutu dan ketepatan garapan, bukan performa video di marketplace. | Tetap manual. Yang dinilai mutu dan ketepatan garapan, dan itu penilaian orang. Yang bisa dibantu sistem hanya ketepatan waktunya, kalau ada pencatatan pengajuan dan tenggat. |
| 0.15 | `Pengelolaan & Kelengkapan Alat` | Persentase alat yang berfungsi baik, jumlah alat yang rusak, dan kerapihan penyimpanan. | TIDAK ADA tracker garapan desain/video (pengajuan, persetujuan, tenggat). Metriknya menilai mutu dan ketepatan garapan, bukan performa video di marketplace. | Tetap manual. Yang dinilai mutu dan ketepatan garapan, dan itu penilaian orang. Yang bisa dibantu sistem hanya ketepatan waktunya, kalau ada pencatatan pengajuan dan tenggat. |
| 0.1 | `Kebersihan Alat` | Kondisi kebersihan alat. | TIDAK ADA tracker garapan desain/video (pengajuan, persetujuan, tenggat). Metriknya menilai mutu dan ketepatan garapan, bukan performa video di marketplace. | Tetap manual. Yang dinilai mutu dan ketepatan garapan, dan itu penilaian orang. Yang bisa dibantu sistem hanya ketepatan waktunya, kalau ada pencatatan pengajuan dan tenggat. |
| 0.4 | `Kualitas Konten` | Persentase pengambilan & edit video content disetujui kualitasnya. | TIDAK ADA tracker garapan desain/video (pengajuan, persetujuan, tenggat). Metriknya menilai mutu dan ketepatan garapan, bukan performa video di marketplace. | Tetap manual. Yang dinilai mutu dan ketepatan garapan, dan itu penilaian orang. Yang bisa dibantu sistem hanya ketepatan waktunya, kalau ada pencatatan pengajuan dan tenggat. |

## Kyura

9 template, 27 metrik. Klasifikasi otomasi: **16 / 1 / 0 / 10**.

> ⚠️ **Hitungan di atas salinan 2026-08-01 dan sudah tertinggal** (sensus prod baca-saja 2026-09-16). `kpi_template` kini memuat **17** template berdepartemen `Kyura`: **12 aktif** dan **5** ber-`status: arsip` (`KPI Kyura Supervisor`, `INTERNAL CONTENT CREATOR `, `LEADER TIKTOK KYURA`, `Customer service`, `MARKETPLACE ADVERTISER`). Keduabelas yang aktif memuat **33** metrik, **20** di antaranya ber-blok `auto`. Bab-bab di bawah masih menyalin keadaan 1 Agustus kecuali **Host Live** dan **Live Support** yang bertanggal sendiri, dan klasifikasi empat kategori **belum** dihitung ulang. Posisi yang punya template aktif tanpa bab di sini: `Engagement Team`, `Account Specialist`, `Bootcamp Content Creator`, `Shop Quality`, dan `Admin Marketplace Kyura` (template kedua untuk `Customer Support`).

> ✅ **Posisi ICC sudah maju melewati snapshot ini.** Per sensus 2026-08-20, ICC Kyura (11 orang) memegang template dengan otomasi PENUH (bobot 1,00) dan skornya kini **dibekukan otomatis** oleh sistem tiap tanggal 1 — lihat [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]. Tabel ICC di bawah tetap salinan struktur metrik per 1 Agustus; rumus sumber yang benar-benar berjalan sekarang ada di `kpi_sumber_kinerja_toko.go` ([[Microservices - Employee Service]]).

### Affiliate

Template `AFFILIATE ACQUSITION`, 3 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.4 | `Jumlah Affiliate Aktif` | Jumlah Affiliator Baru yang bergabung dalam sebulan berdasarkan ketentuan perusahaan | affiliate_orders (194.761) + shopee_affiliate_performance (8.092). Definisi "affiliator baru bergabung" perlu ditetapkan lebih dulu. | Bisa otomatis, tapi sepakati dulu apa artinya "affiliator baru bergabung". Datanya sendiri sudah ada. |
| 0.4 | `Conversion` | Jumlah Konversi Iklan dalam Sebulan | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.2 | `Perfomance Monitoring` | Skor final KPI tercapai sesuai target | SIRKULAR: merujuk skor pemegangnya sendiri, sehingga metrik ikut menentukan dirinya. Tetap manual sampai maknanya diputuskan ulang. | Tetap manual dulu. Metrik ini menilai skor orang itu sendiri, jadi nilainya ikut menentukan dirinya sendiri. Maksudnya perlu diperjelas lebih dulu. |

### Buzzer

Template `BUZZER`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Early Engagement Speed` | Kecepatan boosting (like, comment, share, save) dalam waktu yang ditentukan setelah video tayang.≥ 95% video diboost ≤ 5 menit | Akun buzzer memakai akun personal, TIDAK ada integrasi API. | Belum bisa otomatis. Akun buzzer milik pribadi, jadi sistem tidak punya cara membacanya. |
| 0.25 | `Engagement Quantity` | Jumlah like, comment, share, save sesuai target atau request tim ICC. | Akun buzzer memakai akun personal, TIDAK ada integrasi API. | Belum bisa otomatis. Akun buzzer milik pribadi, jadi sistem tidak punya cara membacanya. |
| 0.2 | `Engagement Quality` | Kualitas komentar (natural, variatif, relevan, tidak template & aman) sehingga meningkatkan engagement.≥ 90% komentar lolos review | Akun buzzer memakai akun personal, TIDAK ada integrasi API. | Belum bisa otomatis. Akun buzzer milik pribadi, jadi sistem tidak punya cara membacanya. |
| 0.2 | `Reporting & Account Readiness` | Kelengkapan laporan harian dan kesiapan akun buzzer (akun aktif & organik). | Akun buzzer memakai akun personal, TIDAK ada integrasi API. | Belum bisa otomatis. Akun buzzer milik pribadi, jadi sistem tidak punya cara membacanya. |
| 0.05 | `Kaizen` | Jumlah inisiatif perbaikan yang diterapkan. | Akun buzzer memakai akun personal, TIDAK ada integrasi API. | Belum bisa otomatis. Akun buzzer milik pribadi, jadi sistem tidak punya cara membacanya. |

### Customer Support

Template `Customer service`, 3 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.4 | `Perfoma` | Rating toko | GET /integration/reviews/summary (ringkasan rating per toko). marketplace_reviews 6.314, product_rating_snapshots 10.933. | Bisa otomatis sekarang. Rating dan ulasan toko sudah ditarik rutin dari marketplace. |
| 0.4 | `Kinerja` | Rate kecepatan respon chat toko | TIDAK ADA data percakapan CS / chat marketplace. | Belum bisa otomatis. Percakapan dengan pembeli belum masuk ke sistem. |
| 0.2 | `Kaizen` | Jumlah inisiatif perbaikan yang diterapkan. | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |

### Host Live

> ✅ **Segar 2026-09-15**, diukur langsung dari `employee_db` prod (baca-saja), menggantikan salinan 2026-08-01 (`HOST LIVE KYURA`: `Conversion` 0,7 · `ROI` 0,3, manual). Yang menilai host sekarang `Host Live Kyura` (dokumen dibuat 2026-05-23, terakhir diubah 2026-08-27), seluruh metriknya otomatis. Klasifikasi departemen di atas (**16 / 1 / 0 / 10**) masih salinan 2026-08-01 dan **belum** memasukkan perubahan ini. Posisi `Live Support` punya template sendiri, `Host Live Support Kyura` (4 metrik manual, dibuat 2026-08-05); babnya ditulis 2026-09-16 dan ada di bawah.

Template `Host Live Kyura`, 3 metrik, **seluruhnya otomatis**. 7 karyawan aktif ber-`position` Host Live (diukur 2026-09-15). Isinya identik dengan `Host Live Beautyhacks` di bab Beauty Hacks.

| Bobot | Label (`key`) | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.7 | `Conversion Rate` (`conversion`) | Target Minimal 7% | ✅ `auto`: sumber `kinerja_live` metrik `conversion_rate`, formula `rata_rata`, target **7**, arah naik, scope `individu`. | Sudah otomatis. |
| 0.1 | `Add to Chart` (`roi`) | Target Minimal 7% | ✅ `auto`: `kinerja_live` metrik `add_to_cart_rate`, `rata_rata`, target **7**, naik, `individu`. `key` mewarisi metrik `ROI` lama. | Sudah otomatis. Pastikan target 7% memang dimaksud (temuan 4 di bawah). |
| 0.2 | `Average view duration` (`average-view-duration`) | Target Minimal 60 detik | ✅ `auto`: `kinerja_live` metrik `avg_viewing_duration`, `rata_rata`, target **60**, naik, `individu`. | Sudah otomatis. |

**Keadaan skor Host Live Kyura** (diukur `kpi_score` prod 2026-09-15; ID karyawan sengaja tidak disalin):

| Periode | Template di snapshot | Penilai | Skor |
|---|---|---|---|
| 2026-07 | `HOST LIVE KYURA` (`Conversion` · `ROI`) | manual, 7 host (satu kini nonaktif) | 100 (3 host), 91,32 (1 host), 83,97 (3 host) |
| 2026-07 | `Host Live Kyura` | `OTOMASI`, 1 host | 90, dengan `Add to Chart` bernilai **0** |
| 2026-08 | `Host Live Kyura` | `OTOMASI`, 7 host | **94,18 identik** untuk ketujuhnya |

#### Temuan Host Live yang berlaku untuk kedua departemen (diukur prod 2026-09-15)

1. **Skor Agustus 2026 adalah angka TIM yang ditempel ke tiap host, walau scope-nya `individu`.** Kesepuluh dokumen `kpi_score` Agustus dibekukan `OTOMASI` pada 1 September 02:00 WIB dengan nilai identik per departemen: Kyura 7 host **94,18**, Beauty Hacks 3 host **90,29**. Saat itu sumber `kinerja_live` belum menghormati scope `individu`; jalur per orang baru berjalan 2026-09-09 ([[Microservices - Employee Service]] § `kinerja_live`). Realisasi yang tersimpan cocok dengan jalur departemen yang dihitung ulang hari ini, misalnya durasi tonton Kyura 67,45 beku vs 67,25 dan Beauty Hacks 30,86 vs 30,77 (selisih kecil karena data siaran bergeser). Skor beku tidak dihitung ulang ([[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]).
2. **Skor Agustus Kyura sekitar 4 poin terlalu rendah.** Pembekuan terjadi sebelum rasio berpasangan (bip-erp #1840, PROD 2026-09-11). Rumus lama membagi masuk keranjang dengan **seluruh** klik, sehingga `Add to Chart` beku 2,93%. Rumus sekarang hanya memakai klik dari sesi yang data keranjangnya terukur; dihitung ulang atas data Agustus hasilnya 1.746 ÷ 30.284 = **5,77%** (seluruh klik Agustus 58.251). Nilai metrik itu naik 41,81 → 82,36 dan skor tiap host **94,18 → 98,24**. Beauty Hacks praktis tak berubah (90,26 dihitung ulang vs 90,29 beku), karena conversion rate dan add to cart-nya di atas target sehingga terpotong di 100 pada kedua rumus. Koreksi snapshot beku menuntut keputusan dan skrip yang dijalankan manusia (**TBD**).
3. **Dua skor Juli beku dengan `Add to Chart` bernilai 0** (satu host per departemen, masing-masing skor 90). Keduanya dibekukan `OTOMASI` 28 Agustus 02:00 WIB, beberapa jam sesudah perubahan terakhir kedua template (27 Agustus 17:53 dan 17:55 WIB), ketika data keranjang belum diambil (per 27 Agustus nol dari 2.365 sesi Agustus memilikinya, [[Microservices - Marketing Analytics Service]] § KPI Host Live), sehingga rumus lama menghasilkan 0%. Nol itu berarti "belum terukur", bukan hasil kerja, jadi masing-masing kehilangan hingga 10 poin. Sejak #1840 keadaan ini tak terulang: tanpa klik berkeranjang metriknya digalatkan. ⚠️ Host Beauty Hacks yang menerima skor Juli itu **baru masuk 26 Agustus 2026** (`work_data.join_date`), jadi skor Juli dan skor Agustus sebulan penuhnya dibuat untuk masa sebelum ia bekerja. Sebabnya di mesin finalisasi, bukan di sumber ini: [[HRIS - Otomasi Skor KPI]] § Belum Diimplementasikan / Catatan.
4. **Target di prod tidak sama dengan keputusan yang tercatat di kode.** Komentar `kpi_sumber_live.go` dan `kpi_live.go` menulis keputusan pemilik metrik 2026-08-27: `conversion_rate` target **2%**, `add_to_cart_rate` **5%**, durasi tonton 60 detik. Prod memakai **7 dan 7**. Kode sendiri menyatakan target milik HR, jadi prod yang berlaku, tetapi selisihnya besar: pada proyeksi September di bawah, host dengan conversion rate 4,35% mendapat 70,7 dengan target 7 dan 7, dan 97,2 dengan target 2 dan 5. Deskripsi `Add to Chart` juga tertulis "Target Minimal 7%" persis seperti Conversion Rate. **TBD**: konfirmasi pemilik metrik.
5. **Conversion rate dan add to cart per host cenderung terbaca lebih rendah** karena pembulatan ke bawah per sesi di marketing-analytics. Mekanismenya di [[Microservices - Employee Service]] § `kinerja_live`; besarnya untuk host Kyura belum diukur.
6. **September 2026 dihitung per shift, padahal pencatatan shift baru dipakai sejak 9 September.** Diukur `marketing_analytics_db.live_shifts` prod 2026-09-15: 136 shift seumur hidup, yang paling awal 2 September (1 shift) dan 7 September (2 shift), lalu pemakaian sungguhan mulai **9 September** (21 shift, 9 host, 5 toko) dan 25 sampai 29 shift per hari penuh sesudahnya. **Agustus tak punya satu shift pun**, jadi angka tim di temuan 1 memang satu-satunya angka otomatis yang mungkin untuk Agustus; menghitung ulang Agustus per orang hanya menghasilkan "belum ada shift live tercatat" untuk semua host. September lain soal: template masih ber-scope `individu`, sementara siaran host sudah berjalan sejak awal bulan (5 sampai 9 sesi berblok interaksi per hari di `mart_live_sessions` seluruh toko pada 1 sampai 8 September) tanpa shift tercatat, sehingga siaran minggu pertama itu tak masuk hitungan siapa pun. `cakupanIndividu` hanya membandingkan shift terjodoh dengan shift tercatat, jadi skornya tetap bisa berstatus `otomatis` walau siaran 1 sampai 8 September (8 dari 30 hari kalender) tak ikut. Besarnya per 14 September, di 7 toko yang pernah dipakai shift (sesi berblok interaksi di `mart_live_sessions`): sebelum 9 September **811 pesanan, 11.462 klik, GMV Rp72,6 jt**; sejak 9 September 779 pesanan, 12.650 klik, GMV Rp69,7 jt. Jadi sampai tanggal itu sekitar **separuh** siaran September (51% pesanan, 47,5% klik, 51% GMV) tak masuk hitungan siapa pun, dan porsinya mengecil seiring bulan berjalan. **Shift tak bisa dicatat mundur**: `permintaanMulai` (`live_shift_handler.go`) hanya menerima toko, akun, dan host, `mulai` diisi jam server saat tombol ditekan, dan tak ada rute maupun layar untuk mengubah `mulai`/`selesai` ([[Microservices - Marketing Analytics Service]] § Pencatatan sesi live). Melengkapinya menuntut tulis DB prod, padahal data yang ada tak bisa memastikan siapa memegang akun mana (ketidakmampuan itu justru alasan `live_shifts` ada), sehingga GMV dan insentif bisa terjodoh ke orang yang salah. Scope juga tak bisa dipisah per tanggal: satu metrik memakai satu scope sepanjang periode. Pilihan yang tersisa (**TBD** HR atau pemilik metrik, sebelum pembekuan 1 Oktober 02:00 WIB): (a) tetap `individu` dengan cakupan sebagian bulan; (b) dinilai manual; (c) menghitung September sebagai angka tim per departemen, yang **menuntut perubahan kode dan deploy**, bukan sekadar mengubah template. Cron finalisasi memakai template aktif dan biner yang berlaku saat ia berjalan (`templateKandidatPerPosisi` lalu `terapkanOtomatis`, `kpi_finalisasi.go`), jadi perubahan apa pun wajib sudah naik sebelum 1 Oktober 02:00 WIB. ⛔ **Koreksi 2026-09-15: mengubah scope ketiga metrik ke `department` TIDAK menghasilkan angka tim.** Versi sebelumnya temuan ini menyarankannya beserta proyeksi Kyura 91,6 dan Beauty Hacks 89,0 untuk semua host. Proyeksi itu diukur dengan memanggil `/kpi/kinerja-live` tanpa `employee_id`, padahal sumber KPI selalu mengirimnya, sehingga scope `department` tetap memberi angka per orang dengan penjaga ambang dan cakupan yang terlepas; mekanismenya di [[Microservices - Employee Service]] § `kinerja_live`. Skor yang dihitung sistem per 15 September lewat `GET /kpi/auto-scores` membenarkan jalur per orang: ketujuh host Kyura berskor berbeda (70,70 sampai 93,44) dan keempat host Beauty Hacks tanpa skor otomatis. Skor Agustus yang identik bukan hasil scope, melainkan karena dibekukan 2026-09-01, sebelum berkas jalur per orang di marketing-analytics (`kpi_live_individu.go`) lahir 2026-09-02.

**Proyeksi September 2026 Kyura** (lewat `GET /kpi/kinerja-live` prod per 15 September, bulan masih berjalan, target 7 · 7 · 60). Ketujuh host lolos seluruh penjaga, jadi akan dibekukan otomatis bila keadaannya bertahan:

| Klik porsi | Conversion rate | Add to cart | Durasi tonton | Proyeksi skor | Cakupan shift |
|---:|---:|---:|---:|---:|---|
| 2.624 | 6,63% | 4,99% | 68,2 dtk | 93,4 | 100% |
| 2.314 | 6,57% | 5,01% | 67,3 dtk | 92,8 | 100% |
| 2.128 | 6,34% | 4,84% | 65,4 dtk | 90,4 | 87% (`semi`) |
| 480 | 5,00% | 8,33% | 53,9 dtk | 78,0 | 100% |
| 1.328 | 5,27% | 4,97% | 52,1 dtk | 77,2 | 77% (`semi`) |
| 429 | 4,90% | 8,86% | 52,2 dtk | 76,4 | 90% (`semi`) |
| 552 | 4,35% | 9,24% | 51,7 dtk | 70,7 | 93% (`semi`) |

`semi` berarti sebagian shift orang itu tak terjodoh dengan siaran mana pun (7 shift di Kyura). Status itu tidak menahan pembekuan: `layakDifinalisasi` hanya memeriksa ada tidaknya angka, dan `kpi_finalisasi.go` tidak membaca cakupan sama sekali.

### ICC

Template `INTERNAL CONTENT CREATOR`, 3 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.4 | `Kuantitas Video Konten` | 125 video/bulan | tt_shop_video_performances (85.149 baris, ada published_at & gmv per video). Atribusi lewat icc_account_mappings employee_id -> tiktok_shop_id. Kyura pakai ambang GMV; Beauty Hacks pakai mart_video_performance.sumber (vsa/gmv_max). | Bisa otomatis sekarang. Data tiap video sudah tersimpan lengkap dengan tanggal tayang dan omzetnya. Syaratnya tiap orang sudah terdaftar memegang toko mana. Kyura sudah 10 dari 12 orang, Beauty Hacks belum sama sekali. |
| 0.2 | `Video Memenuhi Standar Struktur Indikator 10.000/video` | ≥ 70% atau min. 87 video | tt_shop_video_performances (85.149 baris, ada published_at & gmv per video). Atribusi lewat icc_account_mappings employee_id -> tiktok_shop_id. Kyura pakai ambang GMV; Beauty Hacks pakai mart_video_performance.sumber (vsa/gmv_max). | Bisa otomatis sekarang. Data tiap video sudah tersimpan lengkap dengan tanggal tayang dan omzetnya. Syaratnya tiap orang sudah terdaftar memegang toko mana. Kyura sudah 10 dari 12 orang, Beauty Hacks belum sama sekali. |
| 0.4 | `Video Memenuhi Standar Struktur Indikator 150.000/video` | ≥ 30% atau min. 37 video | tt_shop_video_performances (85.149 baris, ada published_at & gmv per video). Atribusi lewat icc_account_mappings employee_id -> tiktok_shop_id. Kyura pakai ambang GMV; Beauty Hacks pakai mart_video_performance.sumber (vsa/gmv_max). | Bisa otomatis sekarang. Data tiap video sudah tersimpan lengkap dengan tanggal tayang dan omzetnya. Syaratnya tiap orang sudah terdaftar memegang toko mana. Kyura sudah 10 dari 12 orang, Beauty Hacks belum sama sekali. |

### Kyura Supervisor

Template `KPI Kyura Supervisor`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.6 | `Revenue 240M` | Target Profit 546 jt yang ditentukan Oleh Finance/ Omset 4.090.000.000 | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.05 | `Inventory turn over 90 days` | Demand forecasting lebih akurat dengan target minimal 85–90%. | TIDAK ADA modul forecast/demand planning. | Belum bisa otomatis. Sistem belum bisa memperkirakan permintaan, jadi tidak ada pembanding untuk menilai akurasinya. |
| 0.05 | `Customer Satisfactions untuk Produk Beautyhacks 4,5 dari 5` | Target Kepuasan Customer dengan target Rating Toko > 4.5 | GET /task-management/report/csat. Pembacaan ulang prod 2026-08-06: **17 tiket ter-rating** seumur hidup, 13 di antaranya Juli. Masih tipis, dan seluruh rating Juli bernilai 5/5 sehingga belum membedakan siapa pun. | Belum layak dipakai. Yang menilai baru 17 orang seumur hidup dan semuanya memberi nilai penuh, jadi angkanya belum bisa membedakan pelayanan yang baik dari yang biasa saja. |
| 0.3 | `Performance Monitoring Team` | KPI Team Kyura denan target skor minimal 70 | Sumber skor_tim + reduksi rata_rata, scope department. Sudah didukung mesin; tinggal isi konfigurasi. | Bisa otomatis sekarang. Sistem tinggal merata-ratakan skor anggota departemen, dan mesinnya sudah siap. |

### Leader

Template `LEADER TIKTOK KYURA`, 3 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.4 | `ROI` | Rata-rata biaya iklan yang dikeluarkan per konversi 3.2 | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.4 | `Conversion / OMZET` | Jumlah konversi yang tertera pada dashboard akun pengiklan 54000 | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.2 | `Perfomance Monitoring` | Skor final KPI tercapai sesuai target | SIRKULAR: merujuk skor pemegangnya sendiri, sehingga metrik ikut menentukan dirinya. Tetap manual sampai maknanya diputuskan ulang. | Tetap manual dulu. Metrik ini menilai skor orang itu sendiri, jadi nilainya ikut menentukan dirinya sendiri. Maksudnya perlu diperjelas lebih dulu. |

### Live Support

> ✅ **Ditulis 2026-09-16**, diukur langsung dari `employee_db` prod (baca-saja). Bab ini tidak ada pada salinan 2026-08-01 karena templatenya baru dibuat 2026-08-05. Klasifikasi departemen Kyura di atas (**16 / 1 / 0 / 10**) belum memasukkannya.
>
> 🟡 **Diperbarui 2026-09-17: 2 dari 4 metrik kini PUNYA sumber, tetapi belum otomatis.** Sumber `kesiapan_live` (`device_lengkap_persen`, `display_sesuai_persen`) live di PROD sejak 2026-09-17 berdasarkan [[ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support]]: host mengisi ceklis dua butir dan memilih Live Support yang bertugas sebelum Mulai di MyBharata. Tiga hal masih menahan: aplikasi MyBharata dengan ceklis itu **belum dirilis**, blok `auto` di template **belum dipasang** (sengaja, sampai ada sesi berceklis), dan skor tetap diisi manual karena tema dan teaser (bobot 0,70) tak punya sistem pencatat. Diukur prod 2026-09-17 untuk Kyura periode September: `toko_diminta` 17, `sesi_departemen_tanpa_pendukung` 130, `sesi_total` 0.
>
> 🟡 **Diperbarui lagi 2026-09-17: tema dan teaser (bobot 0,70) kini punya rancangan sumber yang sudah dikodekan, BELUM merged.** Live Support menyetor tiap tema dan teaser di web ERP, penyetuju departemennya memutus, dan sumber `karya_live_support` menghitung yang disetujui ([[ADR - 0106 Tema dan Teaser Live Support Disetor dan Diputus Penyetuju Departemen sebagai Dasar KPI]]). Sesudah merged, deploy, dan ada setoran nyata, keempat metrik bisa dipasangi blok `auto`, dan skor posisi ini baru bisa dibekukan otomatis.

Template `Host Live Support Kyura`, 4 metrik, **tak satu pun otomatis per 2026-09-16** (tidak ada blok `auto` sama sekali). Dibuat 2026-08-05, terakhir diubah 2026-08-29, aktif (tanpa `status: arsip`). **1 karyawan aktif** ber-`position` Live Support per 2026-09-16, dan ia satu-satunya yang pernah dinilai dengan template ini.

Posisi ini bukan Host Live. Yang dinilai kerja penunjang siaran (kelengkapan alat, tema, cuplikan konten, display etalase), bukan performa siarannya, sehingga sumber `kinerja_live` yang sudah otomatis penuh untuk bab Host Live tidak menjawab satu metrik pun di sini.

| Bobot | Label (`key`) | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Memastikan kelengkapan device penunjang host live` (`pengelolaan-kelengkapan-alat`) | Target 100% | ✅ Sumber `kesiapan_live` → `device_lengkap_persen` (PROD 2026-09-17): persentase sesi berceklis yang dijawab alat lengkap, dihitung dari `live_shifts.kesiapan` pada sesi yang mencatat orang ini di `pendukung[]`. Scope `individu`, reduksi `rata_rata`. | Pasang blok `auto` sesudah MyBharata berceklis dirilis dan sesi pertama tercatat. Memasangnya lebih awal membuat metrik gagal hitung untuk periode berjalan. |
| 0.35 | `Membuat tema hostlive perbulan` (`kualitas-tema`) | Minimal 10 tema | 🟡 Sumber `karya_live_support` → **`tema_disetujui`** (dikodekan 2026-09-17, belum merged): jumlah tema yang disetor Live Support di web ERP dan **disetujui** penyetuju departemennya, berperiode bulan setor pertama. Scope `individu`, reduksi `jumlah_nilai`. `live_shifts` dan `mart_live_sessions` bukan kandidat karena mencatat sesi yang berjalan, bukan tema yang disiapkan. | Pasang blok `auto` (target 10) sesudah deploy dan setoran nyata pertama diputus. ⚠️ Pasangkan ke metrik ini lewat LABEL: key-nya `kualitas-tema`, walau namanya terdengar seperti mutu. |
| 0.35 | `Membuat cuplikan konten (Teaser)` (`kuantitas-tema`) | Minimal 10 cuplikan konten | 🟡 Sumber `karya_live_support` → **`teaser_disetujui`** (dikodekan 2026-09-17, belum merged): teaser yang disetor dengan tautan video dan disetujui; satu tautan terhitung sekali per orang. **`tt_shop_video_performances` terbukti bukan kandidat** (diukur 2026-09-17): 4 dari 123.144 judul memuat teaser/cuplikan, tak satu pun teaser live, dan videonya tertaut ke akun kreator, bukan karyawan. | Pasang blok `auto` (target 10) sesudah deploy dan setoran nyata pertama diputus. Setoran yang masih menunggu tinjauan saat skor dibekukan tak terhitung, dan tersebut di `Catatan`. |
| 0.1 | `Memastikan display product dietalase hostlive sesuai standart ` (`pengelolaan-product-display`) | Target 100% display produk sesuai standar | ✅ Sumber `kesiapan_live` → `display_sesuai_persen` (PROD 2026-09-17), bentuk sama dengan baris alat. Penilaian visualnya tetap dilakukan orang, yaitu host sebelum Mulai, dan yang mengisi bukan yang dinilai. | Sama dengan baris alat: pasang `auto` sesudah ada sesi berceklis. Sisa risikonya host dan Live Support berkolusi; yang tersisa hanya jejak `diisi_oleh`. |

⚠️ **`label` dan `key` bercerita beda, akibat perubahan 2026-08-29.** Nilai `label` sekarang berisi kalimat yang dulu ada di `description`, sementara `description` berisi targetnya. Snapshot `kpi_score` Juli menyimpan bentuk lama, dan `key` masih mengikuti bentuk lama itu:

| `key` | `label` sekarang | `label` di snapshot Juli |
|---|---|---|
| `pengelolaan-kelengkapan-alat` | Memastikan kelengkapan device penunjang host live | Pengelolaan & Kelengkapan Alat |
| `kualitas-tema` | Membuat tema hostlive perbulan | Kualitas Tema |
| `kuantitas-tema` | Membuat cuplikan konten (Teaser) | Kuantitas Tema |
| `pengelolaan-product-display` | Memastikan display product dietalase hostlive sesuai standart␣ | Pengelolaan Product Display |

Akibatnya di layar nama metrik tampil sebagai kalimat panjang, bukan nama metrik, dengan targetnya sebagai keterangan di bawahnya. Label terakhir juga berspasi di ujung (ditandai `␣` di tabel), kelas yang sudah tercatat memutus pencocokan nama tanpa normalisasi trim.

**Keadaan skor** (diukur `kpi_score` prod 2026-09-16; ID karyawan sengaja tidak disalin):

| Periode | Template di snapshot | Penilai | Skor |
|---|---|---|---|
| 2026-06 | — | **belum dinilai** | — |
| 2026-07 | `HOST LIVE SUPPORT`, **5** metrik | manual, 1 orang | 80 |
| 2026-08 | — | **belum dinilai** | — |

Juli satu-satunya skor yang pernah ada untuk posisi ini. Karyawannya masuk 2026-05-26, jadi Juni memang bulan penuh pertamanya dan tetap kosong.

#### Temuan Live Support (diukur prod 2026-09-16)

1. **Agustus 2026 belum dinilai, dan tidak akan terisi sendiri.** Departemen Kyura punya 22 dokumen `kpi_score` periode 2026-08 dan Live Support bukan salah satunya. Karena tak satu pun metriknya otomatis, template ini berada di luar jangkauan pembekuan otomatis ([[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]): harus ada penilai yang mengisi, cron tidak akan menambalnya. Posisi Kyura lain yang punya skor Juli tetapi tidak punya skor Agustus: `Buzzer`, `ICC`, `Meta Advertiser`. (`ICC` 11 orang di Juli dan `Account Specialist` 11 orang di Agustus polanya cocok dengan penggantian nama posisi, tetapi itu **belum diverifikasi**.)

2. **Skor Juli dibekukan atas komposisi yang berbeda dari template sekarang, jadi tren bulan-ke-bulan posisi ini tidak sebanding.** `kpi_score` menyimpan salinan template apa adanya saat penilaian, sehingga snapshot Juli tak ikut berubah ketika templatenya disunting. Snapshot itu bernama `HOST LIVE SUPPORT` dan memuat **5** metrik: keempat metrik sekarang plus `Core Values` (`core-values`, deskripsi `Kaizen`) berbobot 0,05, dengan `kuantitas-tema` masih 0,3 bukan 0,35. Skor 80 itu = 0,2×50 + 0,35×100 + 0,3×100 + 0,1×50 + 0,05×0. Template sekarang membuang `Core Values` dan memindahkan bobotnya ke `kuantitas-tema`. Yang perlu disadari bukan bugnya melainkan bahwa Juli dan Agustus dinilai atas dasar yang berbeda; pembuangan `Core Values` sendiri selaras dengan [[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]].

3. **Penetapan templatenya hasil migrasi, bukan penetapan yang pernah dilakukan orang.** Satu-satunya dokumen `kpi_template_assignment` untuk posisi ini dibuat `migrasi:semai-dari-kpi_score` dengan `berlaku_mulai` `2026-07` dan `company_id` **kosong**. Itu tidak menghalangi apa pun hari ini karena pencocokan template berjalan lewat `department` + `position` (`kpi_me_pratinjau.go`, `kpi_finalisasi.go`), bukan lewat penetapan, tetapi jangan dibaca sebagai bukti bahwa posisi ini pernah ditetapkan secara sadar.

4. **`work_data.position_key` pemegang posisi ini masih `videographer`** sementara `position`-nya sudah `Live Support`, dan ia satu-satunya pemegang `position_key` itu di seluruh prod. **Tidak berpengaruh ke KPI**, karena pencocokan template memakai nama `position`. Yang terdampak paket izin yang menempel pada `position_key`, dan `system_roles` orang itu kosong. Dicatat di sini supaya pembaca bab ini tidak salah menduga KPI-nya ikut terdampak.

### Marketplace Advertiser

Template `ADV MARKETPLACE`, 2 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.5 | `Conversion` | Jumlah konversi iklan dalam sebulan | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.5 | `ROI` | Rata-rata biaya iklan yang dikeluarkan per konversi | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |

### Meta Advertiser

Template `ADV META`, 2 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.5 | `Conversion` | Jumlah konversi iklan dalam sebulan | Meta/Facebook Ads TIDAK terintegrasi. Hanya TikTok Business/Shop, Shopee, Lazada, Accurate. | Belum bisa otomatis. Iklan Meta dan Facebook belum tersambung ke sistem; yang tersambung baru TikTok, Shopee, Lazada, dan Accurate. |
| 0.5 | `ROI` | Rata-rata biaya iklan yang dikeluarkan per konversi | Meta/Facebook Ads TIDAK terintegrasi. Hanya TikTok Business/Shop, Shopee, Lazada, Accurate. | Belum bisa otomatis. Iklan Meta dan Facebook belum tersambung ke sistem; yang tersambung baru TikTok, Shopee, Lazada, dan Accurate. |

## Manufaktur

9 template, 52 metrik. Klasifikasi otomasi: **3 / 16 / 16 / 17**.

### Admin Production

Template `ADMIN PRODUKSI`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Dokumen Produksi` | Persentase kelengkapan dan keabsahan dokumen produksi yang diajukan maksimal 1 hari setelah produksi selesai 100% | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.3 | `Perlengkapan Produksi` | Persentase stok perlengkapan produksi yang tidak ada keluhan berupa kekurangan atau kelebihan | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.2 | `Sumber data terverifikasi dan tervalidasi di setiap bulan` | Melakukan input data produksi (output, downtime, defect) ke template dashboard | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.2 | `Dokumen pendukung produksi diserahkan ke QA/R&D paling lambat Minggu ke-2 Januari` | Menyusun dokumen teknis produksi untuk BPOM (flow proses, parameter kritis, kapasitas mesin, draft batch record) | TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM. | Belum bisa otomatis. Temuan audit, pelaporan pajak, dan izin BPOM belum dicatat di sistem. |

### Admin Warehouse

Template `ADMIN WAREHOUSE 2`, 6 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Arus Stok Bahan` | Persentase input data gudang tepat waktu. | manufacture_stok (530) + saldo_awal_bulanan (530) + POST /stok/reconcile + GET /selisih. Siklus opname terjadwal belum tercatat. | Bisa sebagian. Data stok dan selisihnya sudah ada, tapi jadwal opname belum tercatat sehingga sistem tidak tahu kapan seharusnya dihitung. |
| 0.2 | `100% sumber data terverifikasi dan tervalidasi di akhir bulan` | Rekonsiliasi stok fisik vs sistem untuk validasi data dashboard | manufacture_stok (530) + saldo_awal_bulanan (530) + POST /stok/reconcile + GET /selisih. Siklus opname terjadwal belum tercatat. | Bisa sebagian. Data stok dan selisihnya sudah ada, tapi jadwal opname belum tercatat sehingga sistem tidak tahu kapan seharusnya dihitung. |
| 0.2 | `100% material high-risk & finished goods mengikuti FIFO/FEFO setiap batch` | Melaksanakan proses penerimaan & penyimpanan barang sesuai urutan FIFO/FEFO | manufacture_stok (530) + saldo_awal_bulanan (530) + POST /stok/reconcile + GET /selisih. Siklus opname terjadwal belum tercatat. | Bisa sebagian. Data stok dan selisihnya sudah ada, tapi jadwal opname belum tercatat sehingga sistem tidak tahu kapan seharusnya dihitung. |
| 0.15 | `Akurasi stok fisik vs sistem ≥ 100% setiap stock opname bulanan` | Update kartu stok & dashboard FIFO/FEFO | manufacture_stok (530) + saldo_awal_bulanan (530) + POST /stok/reconcile + GET /selisih. Siklus opname terjadwal belum tercatat. | Bisa sebagian. Data stok dan selisihnya sudah ada, tapi jadwal opname belum tercatat sehingga sistem tidak tahu kapan seharusnya dihitung. |
| 0.1 | `Barang Reject/Retur` | Persentasi penanganan tindak lanjut barang reject/retur | accurate_daily_returns (3.351) + shopee_returns (271) + GET /daily-returns/stats. | Bisa otomatis sekarang. Data retur sudah ditarik rutin dari marketplace dan Accurate. |
| 0.1 | `100% monitoring mingguan dengan temuan dikoreksi dalam ≤3 hari` | Pencatatan kuantitas limbah | Stok & penjualan tersedia, tapi tanpa modul demand planning sebagian metrik ini tidak terdefinisi. | Bisa sebagian. Data stok dan penjualan ada, tapi rumusnya perlu disepakati dulu karena belum ada perencanaan permintaan. |

### Admin Warehouse

Template `ADMIN WAREHOUSE TINGGARJAYA`, 6 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Proses Inbound dan Outbound` | Akurasi controlling stok gudang (fisik) | manufacture_resi (328.272) + warehouse_db.fulfillment_orders (38.949, event pick/pack/handover). | Bisa otomatis sekarang. Data resi dan proses gudang sudah tercatat lengkap. |
| 0.2 | `Stock Opname` | Selisih hasil stock opname fisik dengan data sistem. | manufacture_stok (530) + saldo_awal_bulanan (530) + POST /stok/reconcile + GET /selisih. Siklus opname terjadwal belum tercatat. | Bisa sebagian. Data stok dan selisihnya sudah ada, tapi jadwal opname belum tercatat sehingga sistem tidak tahu kapan seharusnya dihitung. |
| 0.15 | `Administrasi Gudang 1` | Kelengkapan dan kerapian dokumen gudang (surat jalan, retur) | accurate_daily_returns (3.351) + shopee_returns (271) + GET /daily-returns/stats. | Bisa otomatis sekarang. Data retur sudah ditarik rutin dari marketplace dan Accurate. |
| 0.15 | `Administrasi Gudang 2` | Pembagian dan pemetaan produk sebelum dikirim ke ekspedisi (100% resi yang diserahkan ke packing - ekspedisi). | manufacture_resi (328.272) + warehouse_db.fulfillment_orders (38.949, event pick/pack/handover). | Bisa otomatis sekarang. Data resi dan proses gudang sudah tercatat lengkap. |
| 0.2 | `Akurasi Pengiriman Produk` | Jumlah komplain customer yang masuk (salah produk & produk reject) | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.1 | `Kas Gudang` | Report update kas kecil secara realtime | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |

### Leader Production

Template `LEADER PRODUKSI`, 7 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.15 | `Proses Produksi 1` | Produksi 95% tanpa hambatan teknis, 5% Untuk Perbaikan 95% | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.15 | `Proses Produksi 2` | Menurunkan waste pengolahan dan pengemasan. 1,5% | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.15 | `Proses Produksi 3` | Menjaga pemenuhan target kuantiti produk yang diluluskan ≥ 98% | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.15 | `Perfomance Monitoring` | Persentase operator produksi mencapai target KPI (Min. 70). | Sumber skor_tim + reduksi rasio_ambang (ambang = skor minimal, target = 100%). Cakupan team butuh work_data.supervisor_id terisi (2026-08-01: 54 dari 204). | Bisa otomatis, syaratnya data siapa atasan siapa sudah diisi. Per 1 Agustus baru 54 dari 204 karyawan yang terisi. |
| 0.1 | `Kaizen 1` | Mengurangi Jumlah CAPA produksi yang ditemukan. | ⚠️ **Bukan dilayani sumber Kaizen** meski labelnya menyebutnya. Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) tetapi menghitung jumlah ide; yang diukur baris ini adalah **jumlah CAPA produksi**, dan tracker CAPA memang TIDAK ADA di sistem. `kaizen_ide_*` tak akan menjawabnya walau [[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]] dicabut. | Belum bisa otomatis. Temuan dan tindak lanjut CAPA belum dicatat di sistem — itu yang perlu dibuatkan, bukan modul ide perbaikan. |
| 0.15 | `Kaizen 2` | Menjaga Kualitas Produk Target 98% ( Sesuai SOP QC ) | ⚠️ **Bukan dilayani sumber Kaizen** meski labelnya menyebutnya. Yang diukur adalah **persentase kualitas produk sesuai SOP QC**, bukan jumlah ide. Sumbernya batch record & production log, yang ADA di kode tapi KOSONG di prod (0 dokumen). | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. |
| 0.15 | `Realisasi Produksi` | Meningkatkan pelaksanaan rencana produksi sesuai dengan realisasi produksi ≥ 98% | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |

### Manufacturing Supervisor

Template `SPV MANUFAKTUR`, 7 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Jumlah Produksi` | Target Produksi 322.000 pcs / Bulan, 12.800 / Hari | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.1 | `Mengurangi rework & scrap` | Reject & scrap turun ≥ 20%. | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.1 | `Kontrol ketat biaya produksi variabel` | variable dimaintain sama dengan tahun 2025 | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.1 | `Menurunkan material loss` | Material loss mixing turun ≤ 1,5%. | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.1 | `Penguatan implementasi GMP di area produksi & warehouse` | 100% area produksi & gudang memenuhi checklist GMP internal setiap bulan | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |
| 0.1 | `Penguatan SOP K3 dan Standard Safety Equipment di area produksi & warehouse` | 100% pekerja menggunakan APD sesuai SOP setiap hari, Zero accident | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |
| 0.3 | `Performance Monitoring Team` | TARGET SKOR >70 | Sumber skor_tim + reduksi rata_rata, scope department. Sudah didukung mesin; tinggal isi konfigurasi. | Bisa otomatis sekarang. Sistem tinggal merata-ratakan skor anggota departemen, dan mesinnya sudah siap. |

### Operator Production

Template `OPERATOR PRODUKSI`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Keluhan` | 0% | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.25 | `Pengolahan` | ≥ 98% | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.25 | `Waste (pembelian material tambahan akibat kesalahan internal selama 1 bulan produksi)` | MAXIMAL 1,5 % | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.15 | `Kesesuaian stock opname` | 100% | manufacture_stok (530) + saldo_awal_bulanan (530) + POST /stok/reconcile + GET /selisih. Siklus opname terjadwal belum tercatat. | Bisa sebagian. Data stok dan selisihnya sudah ada, tapi jadwal opname belum tercatat sehingga sistem tidak tahu kapan seharusnya dihitung. |
| 0.15 | `Penurunan biaya utilitas (listrik, air, gas) minimal 5% dalam 3 bulan` | 0% | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |

### PPIC

Template `STAFF PPIC`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `REVENUE 240M: OTIF (On Time In Full) / Fill Rate` | Finished good yang dikirim ke WH FG tepat waktu dan dalam jumlah lengkap sesuai yang planning produksi | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.2 | `Inventory Turnover Ratio (ITO) / Perputaran Persediaan` | ITO tinggi menandakan perputaran barang cepat dan manajemen stok efisien. ITO rendah bisa berarti overstock atau barang lambat laku. | ⚠️ **Ralat 2026-09-02: isi sel ini SALAH TEMPEL.** Sampai tanggal itu sel Sumber dan Rekomendasi berbunyi *"Modul Recruitment ADA tapi koleksi candidate KOSONG (job_requisition 2, job_posting 1)"*, verdict milik bab [[#Recruitment & Onboarding]] yang tak ada hubungannya dengan perputaran persediaan. Sumber ITO yang sebenarnya **belum diukur**. Tentukan dengan langkah 1 di [[RUN - Menambah Metrik KPI Otomatis]] (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya); ITO menuntut nilai persediaan **dan** HPP periode, jadi keduanya perlu dipastikan ada sebelum dijanjikan. | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.25 | `Stock Accuracy (Akurasi Stok)` | Memastikan integritas data. PPIC sangat bergantung pada data stok; jika data salah, perencanaan produksi dan pembelian akan kacau. Target umum adalah 98-100%. | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.2 | `Stockout Rate (Tingkat Kekurangan Stok)` | Menghindari terhentinya lini produksi atau hilangnya penjualan karena barang tidak ada. | Stok & penjualan tersedia, tapi tanpa modul demand planning sebagian metrik ini tidak terdefinisi. | Bisa sebagian. Data stok dan penjualan ada, tapi rumusnya perlu disepakati dulu karena belum ada perencanaan permintaan. |
| 0.15 | `Factory Utilization (Utilisasi Pabrik)` | Aset pabrik (mesin dan manusia) digunakan secara optimal. Terlalu rendah berarti idle capacity (boros), terlalu tinggi (di atas 90%) bisa berisiko jika ada lonjakan permintaan darurat. | TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM. | Belum bisa otomatis. Temuan audit, pelaporan pajak, dan izin BPOM belum dicatat di sistem. |

### Warehouse Leader

Template `LEADER WAREHOUSE`, 8 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Melakukan cycle count secara rutin dan terjadwal ( Secara Mingguan )` | Cycle count Bulanan selesai sesuai jadwal dengan akurasi 100% | manufacture_stok (530) + saldo_awal_bulanan (530) + POST /stok/reconcile + GET /selisih. Siklus opname terjadwal belum tercatat. | Bisa sebagian. Data stok dan selisihnya sudah ada, tapi jadwal opname belum tercatat sehingga sistem tidak tahu kapan seharusnya dihitung. |
| 0.15 | `Menjalankan sistem FIFO/FEFO secara konsisten` | Kepatuhan FIFO/FEFO ≥ 98%. | manufacture_stok (530) + saldo_awal_bulanan (530) + POST /stok/reconcile + GET /selisih. Siklus opname terjadwal belum tercatat. | Bisa sebagian. Data stok dan selisihnya sudah ada, tapi jadwal opname belum tercatat sehingga sistem tidak tahu kapan seharusnya dihitung. |
| 0.15 | `Mencegah over-dispensing (bahan diberi lebih banyak dari yang dibutuhkan)` | Selisih antara bahan di-issue dan bahan dipakai ≤ 0,5%.( Khusus Serbuk & Cair) | manufacture_stok (530) + saldo_awal_bulanan (530) + POST /stok/reconcile + GET /selisih. Siklus opname terjadwal belum tercatat. | Bisa sebagian. Data stok dan selisihnya sudah ada, tapi jadwal opname belum tercatat sehingga sistem tidak tahu kapan seharusnya dihitung. |
| 0.15 | `Mengurangi kerusakan material selama penyimpanan` | Kerusakan bahan baku turun dari baseline ≥5% | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.1 | `Penerapan GMP di warehouse (kebersihan, pest control, zoning area, suhu & humidity)` | 100% warehouse comply dengan checklist GMP bulanan | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |
| 0.05 | `Memastikan Update kartu stok & dashboard FIFO/FEFO` | Memastikan 100% kartu stok ter-update ≤ H+1 setelah stock check | manufacture_stok (530) + saldo_awal_bulanan (530) + POST /stok/reconcile + GET /selisih. Siklus opname terjadwal belum tercatat. | Bisa sebagian. Data stok dan selisihnya sudah ada, tapi jadwal opname belum tercatat sehingga sistem tidak tahu kapan seharusnya dihitung. |
| 0.05 | `Memberikan update progres pekerjaan & aspirasi saat 1-on-1 (menjaga stabilitas mood, memberikan solusi, mengajukan bahan diskusi ke atasan)` | 100% mengikuti 1-on-1 bulanan | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |
| 0.15 | `Mencegah over-dispensing (bahan diberi lebih banyak dari yang dibutuhkan) 2` | Selisih antara bahan di-issue dan bahan dipakai ≤ 0,5%.( Khusus Serbuk & Cair) | manufacture_stok (530) + saldo_awal_bulanan (530) + POST /stok/reconcile + GET /selisih. Siklus opname terjadwal belum tercatat. | Bisa sebagian. Data stok dan selisihnya sudah ada, tapi jadwal opname belum tercatat sehingga sistem tidak tahu kapan seharusnya dihitung. |

### Warehouse Staff

Template `STAFF WAREHOUSE`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Zero miss-pick stock 1` | Melakukan stock check berkala untuk mencegah kesalahan picking yang menyebabkan complain | manufacture_resi (328.272) + warehouse_db.fulfillment_orders (38.949, event pick/pack/handover). | Bisa otomatis sekarang. Data resi dan proses gudang sudah tercatat lengkap. |
| 0.3 | `Zero miss-pick stock 2` | Ketepatan Picking (Kesesuaian item, batch, dan quantity) | manufacture_resi (328.272) + warehouse_db.fulfillment_orders (38.949, event pick/pack/handover). | Bisa otomatis sekarang. Data resi dan proses gudang sudah tercatat lengkap. |
| 0.2 | `Kerapihan dan Kebersihan Area` | Penerapan GMP di warehouse (kebersihan, pest control, zoning area, suhu & humidity) | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |
| 0.2 | `Ketepatan Loading dan Unloading` | Barang tidak rusak dan sesuai dokumen | manufacture_resi (328.272) + warehouse_db.fulfillment_orders (38.949, event pick/pack/handover). | Bisa otomatis sekarang. Data resi dan proses gudang sudah tercatat lengkap. |

## Procurement

2 template, 10 metrik. Klasifikasi otomasi: **4 / 2 / 0 / 4**.

### Leader

Template `KPI Leader Procurement`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.4 | `Revenue 240M` | Menjamin Produksi Berjalan Tanpa Shortage dengan target zero production stop karena kekurangan material dan pembuatan SLA untuk semua pembelian R/P materials 100% | GET /task-management/report/sla. Pembacaan ulang prod 2026-08-06: resolusi **214 sampel** terukur seumur hidup (56 di Juli), response 63. Angka "0 sampel" di versi sebelumnya SALAH, sebabnya sensus memakai nama field `completedAt` padahal BSON-nya `completed_at`. | Bisa otomatis sekarang. Kecepatan menanggapi dan menyelesaikan tiket dua-duanya sudah terhitung. Yang perlu diperhatikan justru hasilnya: on-time rate Juli rendah, jadi sepakati dulu targetnya sebelum dipakai menilai orang. |
| 0.2 | `Net Income 20%` | Optimasi Inventory & Cashflow dengan target perencanaan kebutuhan (MRP) akurasi ≥ 95% | TIDAK ADA modul MRP. | Belum bisa otomatis. Belum ada perencanaan kebutuhan bahan di sistem. |
| 0.1 | `Penurunan HPP 5%` | Mengembangkan Skema Kontrak Jangka Panjang (volume-based, price lock, rebate) dengan Mendapatkan rebate/bonus minimal 3-5% dari nilai pembelian tahunan. | work_data.contract_ending + join_date di employee_db. | Bisa otomatis sekarang. Tanggal masuk dan tanggal berakhir kontrak sudah tersimpan. |
| 0.2 | `Credit Terms dari Vendor Rata-Rata N+60 hari` | Negosiasi Ulang Dengan Vendor Untuk Memperpanjang Credit Term Menjadi Rata-Rata 60 hari dengan target Minimal 80% dari total vendor strategis memiliki credit term N+60 hari pada akhir Q2 | GET /procurement/po/lead-time + penerimaan (1.835) + /harga/banding + pemasok (139) + faktur_pembelian (2.055). | Bisa otomatis sekarang. Data pesanan pembelian, penerimaan barang, dan riwayat harga sudah lengkap. |
| 0.1 | `Perfoirmance TIM` | Perfomance TIM dengan target KPI minimal 70 | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |

### Staff Inventory

Template `KPI Staff Inventory`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.4 | `Revenue 240M` | Availability material produksi dengan target ketersediaan stock bahan baku 100 % sesuai planning PPIC dan tidak ada stop produksi karena kekurangan material | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.2 | `Revenue 240 M` | Material yang dipesan datang sesuai dengan waktu yang sudah dijanjikan (ETA) dengan target On Time Delivery Supplier (≥ 95%) | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.2 | `Penurunan HPP 5%` | Efisiensi Harga Pembelian dengan target Selisih harga vs last price / standard cost ( saving ≥5% ) YOY | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.1 | `Penurunan HPP 5% - 2` | Evaluasi Vendor dengan target melakukan evaluasi pelayanan vendor ( Maks 70 % dari jumlah Vendor ) | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.1 | `Penurunan HPP 5% - 3` | Compliance GMP & QA material dengan target material sesuai standar QC ( Target 100 % sesuai ) | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |

## Quality

4 template, 18 metrik. Klasifikasi otomasi: **1 / 2 / 8 / 7**.

### QA Leader

Template `KPI QA Staff`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.4 | `Average QA relelase time sejak batch production selesai` | Melakukan percepatan pre-check batch record dengan target <20 jam batch record setelah dokumen diterima | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.15 | `Testing cost per batch turun 15% dengan optimalisasi alat dan metode` | Testing alat ukur bulanan terselesaikan sesuai jadwal | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.25 | `Zero major finding saat external audit (BPOM)` | Melakukan audit area QC, porduksi, penyimpanan, serta dokumen setiap 2x dalam sebulan | TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM. | Belum bisa otomatis. Temuan audit, pelaporan pajak, dan izin BPOM belum dicatat di sistem. |
| 0.2 | `Kaizen dan Growth` | Melakukan Review Kesesuaian SOP & WI di Area Produksi dengan target 5 produk/bulan | ⚠️ **Bukan dilayani sumber Kaizen** meski labelnya menyebutnya. Yang diukur adalah **jumlah review SOP & WI per bulan**, bukan jumlah ide perbaikan. Tak ada tracker review SOP/WI di sistem. | Belum bisa otomatis. Yang perlu dibuatkan adalah tempat mencatat review SOP & WI, bukan modul ide perbaikan (yang sudah ada). |

### QC Assistant

Template `KPI QC Assistant`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Complain/Rejection` | Persentase bahan kemas yang diluluskan oleh QC Oleh Tim Produksi | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.3 | `Raw Material Checking` | Persentase pengecekan bahan kemas selesai sebelum tenggat waktu retur yang diberikan supplier dengan maksimal 3 hari | accurate_daily_returns (3.351) + shopee_returns (271) + GET /daily-returns/stats. | Bisa otomatis sekarang. Data retur sudah ditarik rutin dari marketplace dan Accurate. |
| 0.3 | `Zero major finding saat external audit (BPOM)` | Pelaksanaan pengendalian ruang penyimpanan bahan dan penyimpanan produk jadi | TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM. | Belum bisa otomatis. Temuan audit, pelaporan pajak, dan izin BPOM belum dicatat di sistem. |
| 0.1 | `Growth` | Kemampuan Multi-Tasking di Area Quality | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |

### QC Production

Template `KPI Quality Staff - Production`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Revenue 240M` | Mempercepat penyelesaian dokumen catatan pengujian pengolahan dan pengemasan batch dengan target maksimal 12 Jam setelah penerimaan CPPB | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.25 | `Complain/Rejection Maks.5%` | Melakukan In-Process Control Tiap Tahap Produksi dengan target 100% produksi berhasil | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.15 | `Complain/Rejection Maksimal 5%` | Tidak ada complain kualitas produk dari Marketing dengan target jumlah komplain maksimal 12 produk tiap bulan | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.15 | `Raw Material checking` | Meningkatkan incoming inspection untuk raw material dan packaging dengan target laporan maks. 3 hari kerja | inventory_db.inventory (134 item) + handover per karyawan. Repair history KOSONG, stock opname aset belum ada. | Bisa sebagian. Daftar aset dan serah terimanya sudah ada, tapi riwayat perbaikan belum pernah diisi dan opname aset belum ada menunya. |
| 0.2 | `Zero major finding saat external audit (BPOM)` | Pelaksanaan pengendalian ruang produksi dan penyimpanan bahan baku dengan 100% area produksi, penyimpanan diaudit setiap minggu | TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM. | Belum bisa otomatis. Temuan audit, pelaporan pajak, dan izin BPOM belum dicatat di sistem. |

### Quality Supervisor

Template `KPI Quality Supervisor`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.15 | `Revenue 240M` | Mempercepat release produk agar tidak menunda shipment dengan Average QA Release Time ≤24 jam sejak batch production selesai | batch_record punya TglSelesaiOlah/DiajukanAt/DisetujuiAt, tapi koleksinya KOSONG di prod. | Belum bisa sekarang. Sistem sudah menyimpan waktu selesai olah dan waktu disetujui, tapi batch record belum pernah diisi. |
| 0.25 | `Complain/Rejection Maks.5%` | Zero complain per bulan dengan persentase jumlah complain 15/bulan | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.15 | `Defect rate maksimal 2% per satu bulan produksi` | Meningkatkan incoming inspection untuk raw material dan packaging dengan incoming inspection raw material dengan laporan maks. 3 hari kerja | Production Log & Batch Record ADA di kode tapi KOSONG di prod (0 dokumen). Begitu dipakai, QA release time & waste langsung terhitung. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Catatan produksi dan batch record sudah ada menunya tapi belum dipakai. Begitu mulai diisi, angkanya terhitung sendiri. |
| 0.15 | `Zero major finding saat external audit (BPOM)` | Melaksanaan internal audit kualitas secara bulanan dengan target tidak ada temukan hal yang melanggar (unsur CAPA) | TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM. | Belum bisa otomatis. Temuan audit, pelaporan pajak, dan izin BPOM belum dicatat di sistem. |
| 0.3 | `Performance Monitoring Team` | KPI Team minimal target skor 70 | Sumber skor_tim + reduksi rata_rata, scope department. Sudah didukung mesin; tinggal isi konfigurasi. | Bisa otomatis sekarang. Sistem tinggal merata-ratakan skor anggota departemen, dan mesinnya sudah siap. |

## Tech Development

7 template, 30 metrik. Klasifikasi otomasi: **14 / 9 / 0 / 7**.

> [!important] Keadaan produksi 2026-08-28 (diukur langsung, bukan disalin dari rencana)
> **Empat dari tujuh template kini berstatus `arsip`** (Tech Development Supervisor, IT
> Infrastructure, Backend Developer, Frontend Developer), jadi yang benar-benar menilai orang
> tinggal **tiga template berisi 13 metrik**: `Leader` (1 orang), `Fullstack` (4 orang),
> `IT Support` (1 orang). Tabel per-metrik di bawah masih memuat ketujuhnya sebagai salinan
> data; bacalah empat yang arsip sebagai riwayat, bukan pekerjaan.
>
> **Sore 2026-08-28 tujuh metrik dinyalakan sekaligus**, jadi metrik ber-`auto` departemen ini
> naik **3 → 10** dan seluruh perusahaan **58 → 65**. `kpi_score` ber-`auto_value` tidak
> bergerak (tetap 2), sehingga penilaian yang sudah tersimpan tak tersentuh. Keadaan 13 metrik
> itu sekarang, diverifikasi lewat `GET /kpi/auto-values` untuk orang sungguhan periode
> 2026-08:
>
> | Keadaan | Metrik | Angka pertama yang keluar |
> |---|---|---|
> | ✅ `otomatis` | IT Support `Problem Solving` (0,3) | 8 dari 10 tepat waktu (80%) atas target 60 → **100** |
> | ✅ `otomatis` | Fullstack `System Development` (0,5) | ketuntasan 80% atas target 85 → **94** |
> | ✅ `otomatis` | Leader `Revenue 240M` (0,2) | tiket support tuntas 90,9% atas target 95 → **96** |
> | ✅ `otomatis` | Leader `Integration System Development di Q4` (0,2) | 1 dari 7 tepat waktu (14,3%) atas target bertahap 30 → **48** |
> | ⚠️ `semi` | IT Support `Network` (0,4) | uptime 99,96%, cakupan 90,3% → 100 |
> | ⚠️ `semi` | IT Support `Customer Satisfaction` (0,15) | rata-rata 5,00 dari 6 rating atas 10 tiket selesai (cakupan 60%) → 100 |
> | ⚠️ `semi` | Fullstack `Customer Satifaction` (0,2) | 1 rating atas 4 tiket selesai (cakupan 25%) → 100 |
> | ⚠️ `semi` | Leader `Customer Satifaction` (0,1) | 1 rating atas 7 tiket selesai (cakupan 14,3%) → 100 |
> | ⏳ `manual` sementara | Leader `KPI Team` (0,4) | `skor_tim` membaca `kpi_score` periode yang SAMA, dan Agustus belum dinilai siapa pun |
> | 🔴 `manual` | IT Support `Kaizen` (0,15) · Fullstack `Kaizen` (0,1) | tak ada program Kaizen hidup di prod |
> | 🔴 `manual` | Fullstack `Monitoring Kegiatan Sinkronisasi/Review` (0,2) | modul kewajiban [[Microservices - Calendar Service]]: 0 template, 0 periode, 0 pemenuhan |
> | ⛔ sengaja manual | Leader `Pengendalian anggaran IT` (0,1) | master anggaran hanya Marketing |
>
> ⚠️ **Empat dari delapan metrik yang menyala berstatus `semi` karena RATING, bukan karena
> kode.** Cakupan CSAT 14% sampai 60% berarti angkanya berdiri di atas satu atau enam penilai;
> nilainya 100 semua karena setiap rating yang pernah masuk bernilai 5. Yang menaikkannya bukan
> pekerjaan dev melainkan kebiasaan meminta pemohon menilai tiketnya.
>
> ⏳ **Metrik terbesar Leader (0,4) belum menghasilkan angka**, dan itu perilaku yang dirancang:
> anggota tim harus dinilai lebih dulu, baru Leader. Urutan itu tidak bisa dibalik tanpa
> kehilangan angka otomatisnya untuk bulan tersebut — sebabnya di [[HRIS - Otomasi Skor KPI]].
>
> ✅ **Tidak ada template yang jadi otomatis PENUH**, jadi [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]
> tetap tidak membekukan siapa pun di sini: Leader 4 dari 5, IT Support 3 dari 4, Fullstack 2
> dari 4.

> **Departemen pertama yang dikerjakan.** Kodenya **sudah merge (PR #866) dan deploy ke produksi 1 Agustus 2026**, terverifikasi terhadap data sungguhan. Lihat [[Microservices - Monitoring Service]].
>
> ✅ **TIGA metrik menyala otomatis sejak 2026-08-06.** Catatan lama di sini ("belum satu pun metrik benar-benar otomatis", sensus 1 Agustus: 0 dari 70 template) sudah tidak berlaku. Yang dinyalakan: `Performance Monitoring Team` pada **Leader** (`skor_tim`, scope `team`, target 70) dan **Supervisor** (scope `department`), serta `Network ` pada **IT Support** (`uptime_sistem`, target 90).
>
> Diverifikasi hari itu juga untuk orang sungguhan: Leader periode 2026-07 menghasilkan **100** dengan cakupan penuh (`otomatis`, basis "rata-rata 86.00 dari 5 pengukuran"), IT Support **100** dengan cakupan 74,19% sehingga dilaporkan **`semi`** (heartbeat baru 23 dari 31 hari), dan periode 2026-08 yang belum dinilai menjawab "belum dapat dihitung" alih-alih nol. Rinciannya di [[HRIS - Otomasi Skor KPI]].
>
> **`kpi_score` tidak tersentuh** (tetap 0 dokumen ber-`auto_value`): snapshot penilaian yang sudah ada beku, jadi angka otomatis baru terpakai pada penilaian **Agustus** di awal September. Kebetulan angkanya sama persis dengan yang sudah diisi manual, jadi tak ada selisih yang perlu dijelaskan ke siapa pun.
>
> ⚠️ **Sensus ulang 2026-08-25: yang menentukan lingkup BUKAN 30 metrik, melainkan siapa yang benar-benar dinilai.** Dari 11 baris `work_data` departemen ini, hanya **6 akun aktif** memegang **3 posisi**. Empat template lain **tak dipegang siapa pun**, sehingga mengotomatiskannya tidak mengubah skor seorang pun.
>
> | Posisi | Akun aktif | Template | Metrik ber-`auto` |
> |---|---:|---|---|
> | `Tech Development Leader` | 1 | `Leader` (dibuat ulang 30 Juli 2026, label sudah menyebut E-TICKET) | 1 dari 5 |
> | `Fullstack Developer` | 4 | `Fullstack` | 0 dari 4 |
> | `IT Support` | 1 | `IT Support` | 1 dari 4 |
> | `Tech Development Supervisor` · `IT Infrastructure` · `Backend Developer` · `Frontend Developer` | **0** | 4 template | 1 dari 17 |
>
> Catatan lama "tujuh developer tidak tersentuh (2 Backend, 1 Frontend, 4 Fullstack)" **sudah tidak berlaku**: kedua Backend dan satu-satunya Frontend kini non-aktif, begitu pula Supervisor. Angka mentah `work_data` tak boleh dibaca sebagai jumlah orang tanpa menyaring `system_authentication.is_active` lebih dulu — kekeliruan yang sama pernah tercatat di [[HRIS - Otomasi Skor KPI]].
>
> **Otomasi 2026-08-25 menyasar tiga template berpenghuni itu saja** (keputusan pemilik produk). Empat metrik dinyalakan lewat konfigurasi tanpa kode (`kinerja_tiket` untuk ketuntasan, SLA, dan CSAT), sementara tiga metrik Leader menuntut sumber baru `kinerja_tiket_divisi` karena menilai tiket **tim**, bukan tiket Leader sendiri. Rencana, target yang disepakati, dan gerbang verifikasinya ada di `.task-plans/2026-08-25-kpi-tech-development-otomatis.md` di repo kerja.
>
> ⛔ **Dua metrik SENGAJA tetap manual, jadi departemen ini tidak akan mencapai otomasi penuh** dan [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]] belum membekukan siapa pun di sini:
> - **`Pengendalian anggaran IT`** (Leader, 0,1) — master anggaran produksi hanya memuat departemen MARKETING, dan sumber `varians_anggaran` memanggil `/accounting/anggaran/varians` **tanpa parameter departemen** sehingga mengukur seluruh perusahaan. Memakainya apa adanya akan menilai Leader IT atas varians anggaran Marketing: angka yang tampak wajar dan menjawab pertanyaan lain.
> - **`Monitoring Kegiatan Sinkronisasi/Review`** (Fullstack, 0,2) — tak ada log pertemuan di sistem mana pun. Diarahkan ke modul kewajiban [[Microservices - Calendar Service]], yang di produksi masih 0 template, 0 periode, dan 0 pemenuhan. ⚠️ **Bukan berarti modulnya belum dibangun**: diukur 2026-08-31, mesinnya **sudah ter-deploy dan berjalan di produksi** (rute `/obligations/templates` membalas 200, kontrol negatif 404). Yang belum ada adalah rute pemakainya. Nol itu berarti belum ada yang membuat template, bukan modulnya tak ada. Lihat § Keadaan terukur di dok itu sebelum merencanakan apa pun untuk metrik ini.
>
> ⚠️ **Metrik Kaizen (IT Support 0,15 · Fullstack 0,1) tetap mustahil otomatis, tetapi SEBABNYA sudah berganti.** Catatan lama benar untuk 25 Agustus: `FORM_BUILDER_MODULE_URL` kosong di employee-service prod. Per **2026-08-28 env itu sudah terisi** (`http://form-builder-service:6986`) dan endpointnya terjangkau, namun `GET /internal/kaizen/metrics?period=2026-08&company_id=BIP` membalas **`has_program:false`**: kedua form ber-`form_type: kaizen` di produksi sudah **dihapus** (`deleted_at` 12 Agustus dan 25 Agustus 11:42), dan filternya memang hanya mencari form yang belum terhapus. Jadi yang kurang sekarang **program Kaizen yang hidup**, bukan konfigurasi container. Ini menyentuh **semua departemen** yang memakai Kaizen, bukan hanya Tech Development. Lihat [[HRIS - Kaizen (Ide Perbaikan)]].
>
> ⚠️ **Koreksi 2026-08-06: dua "penghambat" yang tertulis di sini sebelumnya sebagian besar tidak nyata.** Versi lama menyatakan SLA resolusi tak punya satu pun sampel dan CSAT baru 8 tiket. Pembacaan ulang langsung ke `task_management_db` prod hari ini: dari **307 tiket**, **271 punya `due_date`** dan **214 terukur SLA resolusinya** (56 di antaranya Juli), sedangkan CSAT **17** (13 di Juli). Sebab angka lama nol: sensusnya memakai nama field **`completedAt`** padahal BSON yang sebenarnya **`completed_at`**; diverifikasi, `completedAt` ada di **0 dokumen** dan `completed_at` di 220. Ini persis pola yang sudah diperingatkan di ingatan tim, bahwa angka nol yang mencurigakan diperlakukan sebagai pertanyaan, bukan sebagai temuan.
>
> Yang **tersisa** sebagai penghambat nyata: CSAT masih tipis dan seluruh rating Juli bernilai 5/5 sehingga belum membedakan siapa pun, dan skalanya 1-5 sedangkan KPI menargetkan 1-10. Sedangkan SLA resolusi kini bukan soal "belum terukur" melainkan soal **hasilnya**: on-time rate Juli per space adalah System Finance 8,7% (2 dari 23), IT Support 30% (3 dari 10), MyBharata/HRIS 56,3% (9 dari 16), System Marketing 0% (0 dari 4). Menyalakan metrik ini tanpa menyepakati targetnya lebih dulu akan menjatuhkan skor banyak orang sekaligus.
>
> **Awas spasi di ujung.** Nama posisi `"Tech Development Leader "` dan label `"IT Support / Network "` menyimpan spasi di belakang. `work_data` kebetulan menyimpan spasi yang sama sehingga pencocokan posisi jalan, tetapi jangan mengetik ulang nama itu dari layar — salin apa adanya.

### Backend Developer

Template `Backend Developer`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Delivery` | Kesesuaian dengan requirements dan timeline /Project | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.35 | `Quality` | Kualitas dan performa sistem | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.2 | `Support` | Support dan Troubleshooting | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.15 | `Improvement` | Improvement dan otomasi | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |

### Frontend Developer

Template `Frontend Developer`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Delivery` | Kesesuaian dengan requirements dan timeline /Project | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.35 | `Quality` | Kualitas dan performa sistem | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.2 | `Support` | Support dan Troubleshooting | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.15 | `Improvement` | Improvement dan otomasi | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |

### Fullstack Developer

Template `Fullstack`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.5 | `System Development` | Penyelesaian Project Development Software & Uprgade Fitur Penunjang Operational | ✅ **MENYALA 2026-08-28**: `kinerja_tiket` metrik `selesai_persen`, reduksi `rata_rata`, target **85**, arah naik. Angka pertama (Agustus, `BIP-0205-08-25`): ketuntasan 80% → nilai **94**, status `otomatis`. | Sudah otomatis. Target 85, bukan 100 seperti bunyi deskripsinya: realisasi historis 40% sampai 100%, dan target yang tak pernah tercapai tidak membedakan bulan baik dari bulan buruk. |
| 0.2 | `Implementasi` | Monitoring Implementasi Sinkronisasi/Review dengan Requester | ❌ Tidak ada log pertemuan di sistem mana pun. Diarahkan ke modul kewajiban [[Microservices - Calendar Service]], yang di produksi 2026-08-28 masih **0 template, 0 periode, 0 pemenuhan**. ⚠️ Angka nol itu bukan "modulnya belum ada": mesinnya merged ke `main` 2026-08-07, yang belum ada rute pemakainya. Catatan lama "stok & penjualan tersedia" adalah salah tempel dari departemen lain. | Belum bisa otomatis, tapi jaraknya lebih pendek dari yang terbaca. Yang kurang bukan modul kewajiban dari nol, melainkan cara orang memakainya (menjadwalkan, menandai selesai) plus sumber KPI di employee-service. Dua hal harus diputuskan lebih dulu, bukan dikodekan: siapa yang menandai sesi selesai, dan aturan siapa yang sah jadi lawan sesi. |
| 0.2 | `Customer Satifaction` | Survey Penilaian Software yang sudah diimplementasikan | ✅ **MENYALA 2026-08-28**: `kinerja_tiket` metrik `csat`, `rata_rata`, target **5** (skalanya 1..5, bukan 1-10 seperti bunyi deskripsi). Angka pertama (Agustus): 1 rating atas 4 tiket selesai, cakupan 25% → nilai 100, status **`semi`**. | Sudah otomatis, tapi angkanya belum tajam: yang menilai baru satu orang dan semua rating yang pernah masuk bernilai penuh. Menaikkan kualitas metrik ini soal meminta pemohon menilai tiketnya, bukan soal kode. |
| 0.1 | `Kaizen` | Ide Improvement | ⚠️ Modul Kaizen SUDAH ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan sumber `kaizen_ide_diajukan` sudah di biner prod; `FORM_BUILDER_MODULE_URL` terisi sejak 2026-08-28. Yang kurang: **tak ada program Kaizen hidup** (`has_program:false`, kedua form kaizen prod sudah dihapus). Catatan lama "TIDAK ADA modul Kaizen" sudah tidak berlaku. **Susulan 2026-08-31: Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]), jadi ketiadaan program itu bukan lagi penghambat yang perlu diselesaikan. | **Tetap dinilai manual — karena keputusan.** Bukan karena sistemnya kurang. |

### IT Infrastructure

Template `Infrastruktur`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.1 | `Infrastruktur` | Otomasi & Deployment | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.1 | `Network` | Arsitektur jaringan sesuai requirements | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.1 | `System` | System uptime 99% | Sumber `uptime_sistem` (GET /monitoring/kpi/uptime?periode=YYYY-MM) + reduksi `rata_rata`, arah `naik`. 34 monitor aktif. SUDAH DEPLOY & terverifikasi di prod 2026-08-01 (Juli 99,81% atas 23 dari 31 hari; Juni null). | Bisa otomatis sekarang, tapi angkanya baru penuh mulai Agustus 2026. Sistem sudah memantau 34 server dan aplikasi, dan tiap bulan dilaporkan berapa hari yang benar-benar ada datanya. |
| 0.1 | `Server` | Server uptime 99% | Sumber `uptime_sistem` (GET /monitoring/kpi/uptime?periode=YYYY-MM) + reduksi `rata_rata`, arah `naik`. 34 monitor aktif. SUDAH DEPLOY & terverifikasi di prod 2026-08-01 (Juli 99,81% atas 23 dari 31 hari; Juni null). | Bisa otomatis sekarang, tapi angkanya baru penuh mulai Agustus 2026. Sistem sudah memantau 34 server dan aplikasi, dan tiap bulan dilaporkan berapa hari yang benar-benar ada datanya. |
| 0.6 | `Support` | Support System | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |

> **`System` dan `Server` membaca angka yang sama.** Seluruh monitor di Uptime Kuma bertipe `docker` (33) dan `http` (1) per 1 Agustus 2026, sehingga uptime container dan uptime host belum dapat dibedakan. Memisahkannya butuh monitor tingkat host di Kuma — pekerjaan tim IT, bukan kode. Selama belum dipisah, dua metrik berbobot 0,1 ini efektif menilai hal yang sama.

### IT Support

Template `IT Support`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.4 | `Network` | Optimalisasi Uptime Server & Sistem | ✅ **Satu-satunya metrik departemen ini yang benar-benar ber-`auto`.** Sumber `uptime_sistem` (`GET /kpi/uptime?periode=YYYY-MM`), 2026-08-28: Agustus 99,96% atas 28 dari 31 hari. ⚠️ Konfigurasinya **berubah lagi 2026-08-26** oleh `BIP-0205-08-25` (jejaknya di `kpi_template_audits`): `metrik: downtime` dibuang dan arahnya dibalik ke `naik` dengan `target_per_karyawan` 90, sehingga bentuknya kembali seperti sebelum 7 Agustus. | Bisa otomatis dan memang sudah jalan, **tetapi bentuknya perlu ditinjau ulang**: uptime terhadap target 90 memberi nilai penuh setiap bulan, dan metrik berbobot 0,4 yang selalu 100 tidak mengukur apa pun. Itu persis alasan metriknya dulu dipindah ke `downtime`. |
| 0.15 | `Customer Satisfaction` | Kepuasan Pelayanan IT Support | ✅ **MENYALA 2026-08-28**: `kinerja_tiket` metrik `csat`, `rata_rata`, target **5** (skala 1..5). Angka pertama (Agustus): rata-rata 5,00 dari 6 rating atas 10 tiket selesai, cakupan 60% → nilai 100, status **`semi`**. | Sudah otomatis. Angkanya penuh karena setiap rating yang pernah masuk bernilai 5; yang membuatnya membedakan orang adalah lebih banyak pemohon yang menilai, bukan perubahan rumus. |
| 0.3 | `Problem Solving` | Penyelesaian E - Ticket sesuai dengan SLA ( Service Level Agreement ) | ✅ **MENYALA 2026-08-28**: `kinerja_tiket` metrik `ontime`, reduksi `rasio_ambang` ambang 0, target **80** dengan `target_per_periode` 60 untuk Agustus dan September. Angka pertama (Agustus): 8 dari 10 tepat waktu (80%) → nilai **100**, status `otomatis`. | Sudah otomatis. Targetnya sengaja bertahap: ketepatan waktu bergerak 0% → 7% → 25% → 80% dalam lima bulan, dan target tetap 80 sejak awal akan menilai perbaikan nyata sebagai kegagalan. |
| 0.15 | `Kaizen` | Improvement | ⚠️ Sama dengan Kaizen di template Fullstack: modulnya ada, sumbernya di biner prod, `FORM_BUILDER_MODULE_URL` sudah terisi 2026-08-28, tetapi **tak ada program Kaizen hidup** (`has_program:false`). Catatan lama "TIDAK ADA modul Kaizen" sudah tidak berlaku. **Susulan 2026-08-31: Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan.** Bukan karena sistemnya kurang. |

### Tech Development Leader

Template `Leader`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Revenue 240M` | **Label produksi kini**: "Menjamin operasional IT tanpa gangguan ( E TICKET INFRA & IT SUPPORT )" | ✅ **MENYALA 2026-08-28**: `kinerja_tiket_divisi` metrik `support_selesai_persen`, `rata_rata`, target **95**, arah naik. Angka pertama (Agustus): 10 dari 11 tiket support tuntas (90,9%) → nilai **96**, status `otomatis`, cakupan 100%. | Sudah otomatis. Target 95 diambil dari realisasi Juni 100%, Juli 100%, Agustus 90,9%: tiket dukungan hampir selalu ditutup, jadi target yang lebih rendah tak akan pernah bergerak. |
| 0.1 | `Net income 20%` | Pengendalian anggaran IT | ⛔ **Sengaja tetap manual.** Master anggaran produksi hanya memuat departemen Marketing, dan sumber `varians_anggaran` memanggil `/accounting/anggaran/varians` **tanpa parameter departemen** sehingga mengukur seluruh perusahaan. Memakainya apa adanya menilai Leader IT atas varians anggaran Marketing: angka yang tampak wajar dan menjawab pertanyaan lain. | Belum bisa otomatis, dan itu keputusan sadar. Konsekuensinya template Leader tidak akan pernah otomatis penuh, jadi [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]] tidak membekukan siapa pun di sini. |
| 0.2 | `Integration System Development di Q4` | **Label produksi kini**: "On-time project delivery rate (%) – proyek IT/development selesai sesuai timeline ( E TICKET SOFTWARE DEV )" | ✅ **MENYALA 2026-08-28**: `kinerja_tiket_divisi` metrik `development_ontime`, `rasio_ambang` ambang 0, target **60** dengan `target_per_periode` 30 untuk Agustus dan September. Angka pertama (Agustus): 1 dari 7 tepat waktu (14,3%) → nilai **48**, status `otomatis`. | Sudah otomatis, dan angkanya rendah karena kenyataannya memang rendah: ketepatan waktu tim pengembangan 15,2% (Juni), 28,3% (Juli), 14,3% (Agustus). Target dibuat bertahap supaya perbaikan nyata terbaca, bukan supaya angkanya bagus. |
| 0.1 | `Customer Satifaction` | Average Tingkat Kepuasan User Terhadap Pelayanan Team IT ( Fullstack & Support ) | ✅ **MENYALA 2026-08-28**: `kinerja_tiket_divisi` metrik `development_csat`, `rata_rata`, target **5** (skala 1..5). Angka pertama (Agustus): 1 rating atas 7 tiket selesai, cakupan 14,3% → nilai 100, status **`semi`**. ⚠️ Labelnya berbunyi "Fullstack & Support" tetapi sumbernya hanya punya `support_csat` **atau** `development_csat`; yang terpasang kelompok development saja, jadi rating IT Support tidak ikut terhitung. | Sudah otomatis dengan satu ketidakcocokan yang disengaja: labelnya menjanjikan dua kelompok sekaligus, dan menyatukannya butuh sub-metrik baru di kode, bukan konfigurasi. Putuskan mana yang benar sebelum angkanya dipakai menilai. |
| 0.4 | `Performance Monitoring Team` | KPI Team | ✅ Ber-`auto` sejak 2026-08-06: `skor_tim`, `rata_rata`, scope **`team`**, target 70. ⏳ Untuk periode 2026-08 masih dilaporkan `manual` karena `skor_tim` membaca `kpi_score` periode yang SAMA dan belum seorang pun dinilai untuk Agustus. | Sudah otomatis, tetapi angkanya baru muncul setelah anggota tim dinilai lebih dulu. Menilai Leader duluan membekukan snapshot tanpa angka otomatis, dan itu tidak bisa dibatalkan tanpa menimpa penilaian. |

### Tech Development Supervisor

Template `Supervisor KPI`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Revenue 240M` | Menjamin operasional IT tanpa gangguan | Sumber `uptime_sistem` (GET /monitoring/kpi/uptime?periode=YYYY-MM) + reduksi `rata_rata`, arah `naik`. 34 monitor aktif. SUDAH DEPLOY & terverifikasi di prod 2026-08-01 (Juli 99,81% atas 23 dari 31 hari; Juni null). | Bisa otomatis sekarang, tapi angkanya baru penuh mulai Agustus 2026. Sistem sudah memantau 34 server dan aplikasi, dan tiap bulan dilaporkan berapa hari yang benar-benar ada datanya. |
| 0.1 | `Net income 20%` | Pengendalian anggaran IT | Budget TIDAK tersimpan di ERP mana pun. Realisasi ada di Accurate; perlu master anggaran lebih dulu. | Belum bisa otomatis. Pengeluarannya sudah tercatat, tapi anggarannya belum pernah dimasukkan ke sistem, jadi tidak ada yang bisa dibandingkan. |
| 0.4 | `Integration System Development di Q4` | Menyelesaikan Fitur Baru Sesuai Request SPV All Dept / Bulan | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.3 | `Performance Monitoring Team` | KPI Team | Sumber skor_tim + reduksi rata_rata, scope department. Sudah didukung mesin; tinggal isi konfigurasi. | Bisa otomatis sekarang. Sistem tinggal merata-ratakan skor anggota departemen, dan mesinnya sudah siap. |

## Dokumen Terkait

- [[HRIS - Alur KPI Otomatis.excalidraw]] (diagram Excalidraw untuk pembaca non-teknis: kenapa matrik yang lengkap saja belum cukup)
- [[RUN - Menambah Metrik KPI Otomatis]] (cara mengerjakan otomasinya)
- [[HRIS - Otomasi Skor KPI]] (analisis kelayakan, peta sumber data, rencana bertahap)
- [[HRIS - Key Performance Index]] (mekanisme scoring, RBAC, cakupan tim Leader)
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] (batas service)
- [[Microservices - Employee Service]] (pemilik koleksi kpi_template dan kpi_score)
