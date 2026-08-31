## Deskripsi

*Isi lengkap `kpi_template` di **production**: seluruh label metrik, bobot, dan targetnya, dikelompokkan per departemen. Dokumen kerja untuk dev departemen yang akan mengotomatiskan metriknya. Cara mengerjakannya ada di [[RUN - Menambah Metrik KPI Otomatis]]; latar belakang dan analisis kelayakannya di [[HRIS - Otomasi Skor KPI]].*

- **Status**: ⚠️ Salinan setia data production per **2026-08-01**, dengan bab **Tech Development** disegarkan langsung dari `employee_db` prod **2026-08-28** (status arsip template, konfigurasi `auto` yang benar-benar terpasang, dan ketersediaan tiap sumbernya). Bukan rancangan dan bukan usulan; ini yang benar-benar dipakai menilai orang hari ini. **Ralat 2026-08-31**: 18 sel yang menyatakan "TIDAK ADA modul Kaizen" dan 1 sel yang menyatakan "TIDAK ADA modul forecast" **salah** dan sudah diperbaiki — rinciannya di bagian [[#Ralat 2026-08-31 Kaizen dan forecast kas]].
- **Sumber**: koleksi `kpi_template` di `employee_db` ([[Microservices - Employee Service]]).

## Cara membaca

**Label ditulis persis seperti tersimpan**, termasuk typo (`Perfomance Monitoring`), spasi di ujung (`Monitoring Team `), dan penomoran yang tidak deskriptif (`Performa 1`, `Administrasi 3`). Itu bukan kelalaian penyalinan: **label adalah kunci identitas metrik di kode**, sehingga menuliskannya "yang benar" di sini justru membuat dokumen tidak cocok dengan sistem.

Kolom **Target / keterangan** adalah isi `description` apa adanya. Di situlah target sebenarnya tersimpan, karena `kpi_template` **tidak punya field target yang dapat dibaca mesin** (diverifikasi: nol template memilikinya). Konsekuensinya sebagian deskripsi memuat lebih dari satu angka, dan itu harus diselesaikan dengan pemilik metriknya sebelum diotomatiskan.

Kolom **Klasifikasi otomasi** per departemen memakai empat kategori dari [[HRIS - Otomasi Skor KPI]]: sumber ada dan terisi / sumber ada tapi butuh definisi / modul ada tapi datanya kosong / tidak ada sumber sama sekali. Itu penilaian tingkat departemen. **Verdict per metrik tetap tugas dev departemen**, memakai langkah 1 di [[RUN - Menambah Metrik KPI Otomatis]], karena "endpointnya ada" tidak sama dengan "datanya cukup terisi".

## Ringkasan

| Departemen       | Template |  Metrik | Otomatis |   Semi | Terblokir data |  Manual | by    |
| ---------------- | -------: | ------: | -------: | -----: | -------------: | ------: | ----- |
| Beauty Hacks     |       11 |      30 |       14 |      2 |              0 |      14 | kukuh |
| Finance          |       11 |      61 |       13 |     17 |              0 |      31 | ozi   |
| General Affair   |        5 |      24 |        1 |      5 |              1 |      17 | irfan |
| Human Resource   |        5 |      31 |        7 |      5 |             10 |       9 | irfan |
| Kesekretariatan  |        7 |      28 |        0 |      0 |              0 |      28 | ozi   |
| Kyura            |        9 |      27 |       16 |      1 |              0 |      10 | kukuh |
| Manufaktur       |        9 |      52 |        3 |     16 |             16 |      17 | izan  |
| Procurement      |        2 |      10 |        4 |      2 |              0 |       4 | faiz  |
| Quality          |        4 |      18 |        1 |      2 |              8 |       7 | faiz  |
| Tech Development |        7 |      30 |       14 |      9 |              0 |       7 | izan  |
| **Total**        |   **70** | **311** |   **73** | **59** |         **35** | **144** |       |

Dua departemen di `work_data` **tidak muncul di sini karena belum punya template sama sekali**: Percetakan (13 karyawan) dan Marketing Offline Distribution (1 karyawan).

## Ralat 2026-08-31 Kaizen dan forecast kas

> **Status ralat**: ✅ diverifikasi ke kode `bip-erp` `main` (`9734bea0`, 2026-08-28) pada 2026-08-31.
> Yang diralat: **18 sel** berbunyi *"TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol
> hasil di services + shared-library)"* dan **2 sel** berbunyi *"TIDAK ADA modul forecast/demand
> planning"* pada metrik yang sebenarnya mengukur **forecast KAS** (Cost Control #4 dan Finance
> Supervisor `Return on Operation`). Dua sel lain yang memakai kalimat yang sama — `Inventory turn
> over 90 days` di Beauty Hacks dan Kyura — **tidak diralat dan memang tetap benar**: yang mereka
> ukur adalah *demand planning*, dan modul itu memang tidak ada.

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

Empat sel berlabel Kaizen yang **tidak** dilayani sumber ini — `Inovation & Improvement` (Manufaktur
Supervisor), `Kaizen 1` (CAPA produksi), `Kaizen 2` (kualitas produk 98%), dan `Kaizen dan Growth`
(review SOP & WI) — ditandai terpisah di tempatnya masing-masing: labelnya menyebut Kaizen, tapi
yang diukur bukan hitungan ide, sehingga `kaizen_ide_*` tak akan menjawabnya walau keputusan
berbalik.

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
> `indeks_layanan_tim` · `nilai_layanan_pribadi`
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
> Sub-metrik tiga sumber HRGA:
>
> | Sumber | Sub-metrik | Melayani |
> |---|---|---|
> | `kedisiplinan_absensi` | `ketepatan_waktu` · `kelengkapan_catatan` | Personalia `Administrasi 1` & `Kedisiplinan`, Organizational Development `SOP` |
> | `turnover_karyawan` | `turnover_persen` | KPI Supervisor HRGA `Turn Over Rate Target 5% per Tahun` |
> | `kontrak_karyawan` | `perpanjangan_tepat_waktu` · `sisa_hari_kontrak` | Personalia `Administrasi 3` |
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

Template `HOST LIVE`, 3 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.6 | `Conversion` | Jumlah konversi live dalam sebulan | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.3 | `ROI` | Skor final KPI tercapai sesuai target | TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM. | Belum bisa otomatis. Temuan audit, pelaporan pajak, dan izin BPOM belum dicatat di sistem. |
| 0.1 | `Perfomance Monitoring` | Skor final KPI tercapai sesuai target | SIRKULAR: merujuk skor pemegangnya sendiri, sehingga metrik ikut menentukan dirinya. Tetap manual sampai maknanya diputuskan ulang. | Tetap manual dulu. Metrik ini menilai skor orang itu sendiri, jadi nilainya ikut menentukan dirinya sendiri. Maksudnya perlu diperjelas lebih dulu. |

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

11 template, 61 metrik. Klasifikasi otomasi: **13 / 17 / 0 / 31**.

### AR Leader

Template `KPI AR Leader`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Mengurangi piutang aging > 60 hari sampai < 5% dari total AR` | Rekonsiliasi AR Harian | Accurate live proxy: GET /accounting/receivables + GET /orders/piutang/summary. | Bisa otomatis sekarang. Data piutang diambil langsung dari Accurate. |
| 0.3 | `Pengawasan 100% AR aging ≤ 14 hari` | Follow-up pembayaran & rekonsiliasi kas - 90% pembayaran diterima sesuai aging ≤ 14 hari | Accurate live proxy: GET /accounting/receivables + GET /orders/piutang/summary. | Bisa otomatis sekarang. Data piutang diambil langsung dari Accurate. |
| 0.2 | `Monitoring Team` | Checker inputan team/Rekonsiliasi dengan selesai pengimputan data max tgl 3 bulan berikutnya | BUKAN murni skor tim: deskripsinya menggabungkan checker inputan dengan ketepatan tanggal. Pisahkan dulu dengan pemilik metrik. | Perlu dipecah dulu. Satu baris ini mencampur dua penilaian berbeda: memeriksa input tim, dan ketepatan tanggal pengumpulan. |
| 0.1 | `Minimal 6 ide inovasi baru dari 5 TOTAL tim pada tiap kuartal` | Mengidentifikasi peluang inovasi di proses AR Finance | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV / Leader | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

### AR Staff

Template `KPI AR Piutang`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Penagihan > 60 hari sampai < 5% dari total AR` | Proses AR & Cash Collection Harian | Accurate live proxy: GET /accounting/receivables + GET /orders/piutang/summary. | Bisa otomatis sekarang. Data piutang diambil langsung dari Accurate. |
| 0.4 | `Pencatatan Piutang` | Input data piutang (Uang masuk) max laporan inputan piutang bulanan selesai tanggal 3 bulan berikutnya | Accurate live proxy: GET /accounting/receivables + GET /orders/piutang/summary. | Bisa otomatis sekarang. Data piutang diambil langsung dari Accurate. |
| 0.25 | `Penagihan piutang > 14 hari sampai < 5% dari total AR` | Proses AR & Cash Collection Harian dengan Max 5% piutang belum tertagih lebih dari 14 hari | Accurate live proxy: GET /accounting/receivables + GET /orders/piutang/summary. | Bisa otomatis sekarang. Data piutang diambil langsung dari Accurate. |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses AR dengan minimal 2 ide terdaftar perbulan | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |

### AR Staff

Template `KPI AR Retur`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Penanganan retur di platform atau Expedisi` | Proses foll up retur lebih dari 14 hari dengan maksimal 5% retur | accurate_daily_returns (3.351) + shopee_returns (271) + GET /daily-returns/stats. | Bisa otomatis sekarang. Data retur sudah ditarik rutin dari marketplace dan Accurate. |
| 0.5 | `Pencatatan retur penjualan` | Input data retur dengan max laporan inputan retur bulanan selesai tanggal 3 bulan berikutnya | accurate_daily_returns (3.351) + shopee_returns (271) + GET /daily-returns/stats. | Bisa otomatis sekarang. Data retur sudah ditarik rutin dari marketplace dan Accurate. |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses AR minimal 2 ide terdaftar perbulan | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV / Leader | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

### AR Staff

Template `KPI Sales Admin`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.5 | `Pencatatan Penjualan` | Input data penjualan dengan max laporan inputan penjualan bulanan selesai tanggal 3 bulan berikutnya | `accurate_daily_invoices` via `GET /accurate/daily-invoices/kpi/pencatatan`, sumber `kinerja_sales_admin` metrik `penjualan_tuntas_cutoff_persen` (bip-erp PR #1254, belum merge). | Bisa otomatis, mesinnya sudah siap — sama seperti retur. Tinggal menunggu PR #1254 merge lalu dikonfigurasi ke template. |
| 0.3 | `Rekonsiliasi stok penjualan` | Rekonsiliasi data stok terjual dengan data pengiriman gudang dengan Max laporan rekonsiliasi stok selesai tanggal 3 bulan berikutnya | Accurate live proxy + GET /transactions/reconciliation dan /reconciliation/missing. accurate_bank_accounts (44). | Bisa sebagian. Alat pencocokan data sudah ada, tapi perlu disepakati dulu apa yang dihitung sebagai selisih dan kapan batas waktunya. |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses AR Minimal 2 ide inovasi terdaftar perbulan | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV / Leader | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

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

### Cost Control

Template `KPI Cost Control`, 7 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Varians antara budget vs realisasi OPEX ≤ ±5%` | Review Cash Outflow Mingguan - Realisasi OPEX dalam batas ±5% dari budget | Budget TIDAK tersimpan di ERP mana pun. Realisasi ada di Accurate; perlu master anggaran lebih dulu. | Belum bisa otomatis. Pengeluarannya sudah tercatat, tapi anggarannya belum pernah dimasukkan ke sistem, jadi tidak ada yang bisa dibandingkan. |
| 0.1 | `Penurunan biaya admin/non operasional minimal 2% YoY` | Analisis biaya berulang dan rekomendasi perbaikan | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.2 | `Penurunan OPEX 3–5% dalam 6 bulan` | Melakukan Analisis Varians OPEX dengan minimal 3 rekomendasi efisiensi cost driver setiap bulan | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.15 | `Forecast cashflow mingguan dengan akurasi ≥ 95%.` | Analisis Deviasi Forecast vs Aktual | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul forecast" SALAH.** Sumber `forecast_kas` ada di `main` sejak **14 Agustus 2026** (`kpi_sumber_forecast_kas.go:29`, commit `58119297`), metrik **`akurasi_forecast_kas`**, menarik `GET /accounting/anggaran/mingguan/kpi` dari [[Microservices - Integration Service]] (`services/integration/main.go:1446`). Sumber ini memang **dibuat khusus untuk metrik ini** (disebut eksplisit di komentar berkasnya). Yang lama benar hanya untuk *demand planning* — dan itu bukan yang diukur baris ini. | ⚠️ **Konektornya sudah ada; belum dinyalakan.** Isi konfigurasi `{sumber: forecast_kas, metrik: akurasi_forecast_kas, target: 95, arah: naik}` di `/hris/kpi/otomasi`. **TBD**: perlu dipastikan dulu anggaran mingguan benar-benar terisi di produksi — bila `akurasi_terdefinisi` bernilai false, sumber sengaja **menggalat, bukan memberi nol** (`kpi_sumber_forecast_kas.go:68`), jadi angkanya tak muncul. Verifikasi: panggil `GET /accounting/anggaran/mingguan/kpi?tahun=2026&bulan=8` dan periksa `akurasi_terdefinisi` bernilai `true`. |
| 0.2 | `Pengelolaan Kas Iklan` | Akurasi Distribusi kas iklan dan pencatatan | Accurate live proxy + GET /transactions/reconciliation dan /reconciliation/missing. accurate_bank_accounts (44). | Bisa sebagian. Alat pencocokan data sudah ada, tapi perlu disepakati dulu apa yang dihitung sebagai selisih dan kapan batas waktunya. |
| 0.1 | `Minimal 5 ide inovasi baru dari tim` | Mengidentifikasi peluang inovasi di proses cost control | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
| 0.05 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

### Finance Supervisor

Template `KPI Supervisor Finance`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Monitoring AR & Collection ... < 5% dari total AR.` | Mengurangi piutang aging > 60 hari sampai < 5% dari total AR. | **Koreksi 2026-08-26**: sumber `kinerja_ar` metrik `piutang_lewat_60_persen`, sudah terdaftar dan **sudah ter-deploy di prod** (`kpi_sumber_ar.go`). Konfigurasi identik sudah hidup di template `AR STAFF PIUTANG`. | ✅ **Bisa dinyalakan sekarang, tanpa deploy** — cukup konfigurasi `{sumber: kinerja_ar, metrik: piutang_lewat_60_persen, formula: rata_rata, target: 5, arah: turun, scope: department}`. ⚠️ Angkanya akan **sama persis dengan AR Staff**: `kinerja_ar` menarik piutang se-perusahaan tanpa parameter departemen. |
| 0.25 | `Rasio EBITDA 45%` | Kontrol OPEX dengan Budget Compliance 95% (Varians antara budget vs realisasi OPEX ≤ ±5%) | Budget TIDAK tersimpan di ERP mana pun. Realisasi ada di Accurate; perlu master anggaran lebih dulu. | Belum bisa otomatis. Pengeluarannya sudah tercatat, tapi anggarannya belum pernah dimasukkan ke sistem, jadi tidak ada yang bisa dibandingkan. |
| 0.2 | `Net income 20%` | Kontrol Beban Non-Operasional ≤ 2% | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.1 | `Return on Operation = 2,75` | Cashflow Forecasting mingguan dengan akurasi ≥ 95%. | ⚠️ **Ralat 2026-08-31 — sama dengan Cost Control #4.** Deskripsinya adalah *cashflow* forecasting, bukan demand planning, dan sumber `forecast_kas` metrik `akurasi_forecast_kas` sudah ada di `main` sejak 14 Agustus 2026 (`kpi_sumber_forecast_kas.go:29`). ⚠️ **Namun label dan deskripsinya berbeda hal**: label mengukur `Return on Operation = 2,75`, deskripsinya mengukur akurasi forecast. Satu baris, dua penilaian. | Perlu dipecah dulu dengan pemilik metrik. Untuk bagian akurasi forecast-nya konektornya sudah ada (lihat Cost Control #4); untuk `Return on Operation` belum jelas angka mana di sistem yang dimaksud. |
| 0.2 | `Performance Monitoring Team` | KPI Tim minimal skor 70 | Sumber skor_tim + reduksi rata_rata, scope department. Sudah didukung mesin; tinggal isi konfigurasi. | Bisa otomatis sekarang. Sistem tinggal merata-ratakan skor anggota departemen, dan mesinnya sudah siap. |

> ⛔ **Metrik 0,25 di atas SEMPAT tercatat di sini sebagai `Revenue 240M` dengan sumber GMV TikTok + `mart_profit_attribution`, dan itu SALAH.** Labelnya salah isi dari HR; deskripsinya sejak awal berbunyi piutang, bukan omzet, dan produksi sudah membetulkan labelnya. Kunci metriknya tetap `revenue-240m` karena `key` memang identitas stabil yang tak boleh diganti, jadi siapa pun yang membedah Mongo akan menemukan token yang menyebut revenue untuk metrik yang mengukur piutang. **Jangan mengembalikan baris ini ke sumber omzet.**
>
> Kelas kesalahannya persis yang diperingatkan Langkah 1 di [[RUN - Menambah Metrik KPI Otomatis]]: label dan deskripsi yang menyebut dua hal berbeda, lalu yang membaca dokumen memilih yang salah satu. Yang menentukan bukan labelnya melainkan **apa yang benar-benar terpasang di `kpi_template` produksi**.

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
| 0.15 | `Kebersihan 3` | Pelaksanaan 5R di Area Pantry dan Area Tanggung Jawab Kebersihan | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |

### Security

Template `Security Team`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Pelayanan Security` | Rating Pelayanan dan Keamanan (1-10) | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.3 | `Kualitas Keamanan` | Kepatuhan Melakukan Patroli Setiap 3 Jam ( Aspek Keamanan, Kerapian & Kondisi Area ) | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |
| 0.2 | `Dokumentasi` | Kepatuhan SOP Security | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.2 | `Kerapihan dan kebersihan Pos` | Persentase kerapihan dan kebersihan pos jaga ( Konsep 5R ) | TIDAK ADA modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance). Konsepnya di GA - Checklist Management. | Belum bisa otomatis. Perlu daftar periksa berjadwal beserta bukti fotonya, dan itu belum ada. |

## Human Resource

5 template, 31 metrik. Klasifikasi otomasi: **7 / 5 / 10 / 9**.

### Culture & Industrial

Template `Organizational Development`, 6 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Culture 1` | Penyusunan program culture | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.2 | `Culture 2` | Persentase terlaksananya program culture yang sesuai jadwal | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.2 | `Culture 3` | Prosentase Keaktifan Peserta Training >= 100% dari jumlah Peserta | Modul Training ADA di kode tapi koleksi training & training_participant KOSONG di prod. Skor & survei kepuasan training juga belum ada fieldnya. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu pelatihan sudah ada, hanya belum ada yang mengisinya. Nilai dan survei kepuasan pelatihan memang belum ada tempatnya. |
| 0.2 | `KPI` | Skor Penilaian Training All Karyawan > 70 | Modul Training ADA di kode tapi koleksi training & training_participant KOSONG di prod. Skor & survei kepuasan training juga belum ada fieldnya. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu pelatihan sudah ada, hanya belum ada yang mengisinya. Nilai dan survei kepuasan pelatihan memang belum ada tempatnya. |
| 0.1 | `SOP` | Tingkat Kedisipilnan Karyawan ( Attandance & Intergritas ) | `kedisiplinan_absensi` / `ketepatan_waktu`, menarik `GET /kpi/attendance` dari attendance-service. | ✅ **KONEKTOR SIAP** (2026-08-22, [#1379](https://github.com/bip-itteam-internal/bip-erp/pull/1379), live di prod). Tinggal diisi HR di `/hris/kpi/otomasi`: sumber `kedisiplinan_absensi`, metrik `ketepatan_waktu`, cakupan **`perusahaan`** (bunyinya "seluruh karyawan", bukan tim OD), reduksi `rasio_ambang`. |
| 0.1 | `Kaizen` | Jumlah Inovasi All Divisi ( 7 / Bulan ) | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |

### HRD Supervisor

Template `KPI Supervisor HRGA`, 10 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.15 | `Revenue 240 Miliar` | Menjamin ketersediaan tenaga kerja dengan rata-rata time recruitment <30 hari untuk posisi kritikal | Modul Recruitment ADA tapi koleksi candidate KOSONG (job_requisition 2, job_posting 1). | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. |
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

Template `Recruitment Team`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Rekrutmen Seleksi dan penempatan` | Time to Fulfilment Rate ( < 30 Hari ) All Vacant | Modul Recruitment ADA tapi koleksi candidate KOSONG (job_requisition 2, job_posting 1). | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. |
| 0.2 | `Rekrutmen Seleksi dan penempatan` | Membuat rencana jadwal dan pelaksanaan onboarding karyawan Masa Percobaan. | Modul Recruitment ADA tapi koleksi candidate KOSONG (job_requisition 2, job_posting 1). | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. |
| 0.2 | `Rekrutmen Seleksi dan Penempatan` | Presentase Data Base Buffer Kebutuan MPP | Modul Recruitment ADA tapi koleksi candidate KOSONG (job_requisition 2, job_posting 1). | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. |
| 0.25 | `Job Description` | Skor Kompetensi New Hire Fase On Boarding >80 | Modul Recruitment ADA tapi koleksi candidate KOSONG (job_requisition 2, job_posting 1). | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. |
| 0.1 | `Kaizen` | Jumlah inisiatif perbaikan yang diterapkan | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |

### Training & Perfomance Officer

Template `People Development`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.35 | `Training & Development` | Terlaksananya kegiatan training & performance officer sesuai dengan rencana. | Modul Training ADA di kode tapi koleksi training & training_participant KOSONG di prod. Skor & survei kepuasan training juga belum ada fieldnya. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu pelatihan sudah ada, hanya belum ada yang mengisinya. Nilai dan survei kepuasan pelatihan memang belum ada tempatnya. |
| 0.25 | `Training & Development 2` | Training Attendance Rate | Modul Training ADA di kode tapi koleksi training & training_participant KOSONG di prod. Skor & survei kepuasan training juga belum ada fieldnya. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu pelatihan sudah ada, hanya belum ada yang mengisinya. Nilai dan survei kepuasan pelatihan memang belum ada tempatnya. |
| 0.2 | `Peningkatan Performance` | Skor Penilaian Training All Karyawan > 70 | Modul Training ADA di kode tapi koleksi training & training_participant KOSONG di prod. Skor & survei kepuasan training juga belum ada fieldnya. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu pelatihan sudah ada, hanya belum ada yang mengisinya. Nilai dan survei kepuasan pelatihan memang belum ada tempatnya. |
| 0.1 | `KPI` | SLA Pengumpulan KPI tepat waktu dan ter-update | GET /task-management/report/sla. Pembacaan ulang prod 2026-08-06: resolusi **214 sampel** terukur seumur hidup (56 di Juli), response 63. Angka "0 sampel" di versi sebelumnya SALAH, sebabnya sensus memakai nama field `completedAt` padahal BSON-nya `completed_at`. | Bisa otomatis sekarang. Kecepatan menanggapi dan menyelesaikan tiket dua-duanya sudah terhitung. Yang perlu diperhatikan justru hasilnya: on-time rate Juli rendah, jadi sepakati dulu targetnya sebelum dipakai menilai orang. |
| 0.1 | `Pelayanan` | Training Satisfaction Score | Modul Training ADA di kode tapi koleksi training & training_participant KOSONG di prod. Skor & survei kepuasan training juga belum ada fieldnya. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu pelatihan sudah ada, hanya belum ada yang mengisinya. Nilai dan survei kepuasan pelatihan memang belum ada tempatnya. |

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
| 0.25 | `Inovation & Improvement` | Meningkatkan Inovasi & Efisiensi Produk | ⚠️ **Bukan dilayani sumber Kaizen.** Modul Kaizen ADA (`kaizen_ide_diajukan`/`kaizen_ide_diterapkan`, lihat [[#Ralat 2026-08-31 Kaizen dan forecast kas]]), tetapi ia menghitung **jumlah ide**, sedangkan metrik ini mengukur "inovasi & efisiensi produk" yang tak punya definisi terukur di sistem mana pun. | Perlu didefinisikan ulang dulu. Modul pencatat ide sudah ada, tapi metrik ini tidak menyebut angka yang bisa dihitung dari sana — sepakati dulu dengan pemilik metrik apakah yang dinilai jumlah ide, atau hal lain. |
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

Template `HOST LIVE KYURA`, 2 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.7 | `Conversion` | Jumlah konversi live dalam sebulan 2500 | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.3 | `ROI` | Jumlah Roi 4 | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |

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
| 0.1 | `Kaizen 1` | Mengurangi Jumlah CAPA produksi yang ditemukan. | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
| 0.15 | `Kaizen 2` | Menjaga Kualitas Produk Target 98% ( Sesuai SOP QC ) | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |
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
| 0.2 | `Inventory Turnover Ratio (ITO) / Perputaran Persediaan` | ITO tinggi menandakan perputaran barang cepat dan manajemen stok efisien. ITO rendah bisa berarti overstock atau barang lambat laku. | Modul Recruitment ADA tapi koleksi candidate KOSONG (job_requisition 2, job_posting 1). | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. |
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
| 0.2 | `Kaizen dan Growth` | Melakukan Review Kesesuaian SOP & WI di Area Produksi dengan target 5 produk/bulan | ⚠️ **Ralat 2026-08-31 — klaim lama "TIDAK ADA modul Kaizen" SALAH.** Modul Kaizen ADA ([[HRIS - Kaizen (Ide Perbaikan)]]) dan dua sumber KPI-nya terdaftar (`kaizen_ide_diajukan`, `kaizen_ide_diterapkan`, `kpi_sumber_kaizen.go:29-30`) memasok dari `GET /internal/kaizen/metrics`. **Namun Kaizen diputuskan TIDAK dipakai untuk otomasi KPI** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]). | **Tetap dinilai manual — karena keputusan, bukan karena sistemnya belum ada.** Menunya sudah ada di sistem, tetapi tidak dipakai untuk penilaian KPI sampai keputusan itu dicabut. |

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
> - **`Monitoring Kegiatan Sinkronisasi/Review`** (Fullstack, 0,2) — tak ada log pertemuan di sistem mana pun. Diarahkan ke modul kewajiban [[Microservices - Calendar Service]], yang di produksi masih 0 template, 0 periode, dan 0 pemenuhan. ⚠️ **Bukan berarti modulnya belum dibangun**: mesinnya sudah di `main` sejak 7 Agustus 2026, yang belum ada adalah rute pemakainya. Lihat § Mesin kewajiban di dok itu sebelum merencanakan apa pun untuk metrik ini.
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
