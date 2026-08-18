## Deskripsi

*Isi lengkap `kpi_template` di **production**: seluruh label metrik, bobot, dan targetnya, dikelompokkan per departemen. Dokumen kerja untuk dev departemen yang akan mengotomatiskan metriknya. Cara mengerjakannya ada di [[RUN - Menambah Metrik KPI Otomatis]]; latar belakang dan analisis kelayakannya di [[HRIS - Otomasi Skor KPI]].*

- **Status**: ✅ Salinan setia data production per **2026-08-01**. Bukan rancangan dan bukan usulan; ini yang benar-benar dipakai menilai orang hari ini.
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

## Cacat yang sudah diketahui

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
| 0.1 | `Kaizen` | Jumlah inisiatif perbaikan yang diterapkan. | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |

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
| 0.1 | `Minimal 6 ide inovasi baru dari 5 TOTAL tim pada tiap kuartal` | Mengidentifikasi peluang inovasi di proses AR Finance | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV / Leader | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

### AR Staff

Template `KPI AR Piutang`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Penagihan > 60 hari sampai < 5% dari total AR` | Proses AR & Cash Collection Harian | Accurate live proxy: GET /accounting/receivables + GET /orders/piutang/summary. | Bisa otomatis sekarang. Data piutang diambil langsung dari Accurate. |
| 0.4 | `Pencatatan Piutang` | Input data piutang (Uang masuk) max laporan inputan piutang bulanan selesai tanggal 3 bulan berikutnya | Accurate live proxy: GET /accounting/receivables + GET /orders/piutang/summary. | Bisa otomatis sekarang. Data piutang diambil langsung dari Accurate. |
| 0.25 | `Penagihan piutang > 14 hari sampai < 5% dari total AR` | Proses AR & Cash Collection Harian dengan Max 5% piutang belum tertagih lebih dari 14 hari | Accurate live proxy: GET /accounting/receivables + GET /orders/piutang/summary. | Bisa otomatis sekarang. Data piutang diambil langsung dari Accurate. |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses AR dengan minimal 2 ide terdaftar perbulan | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |

### AR Staff

Template `KPI AR Retur`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.3 | `Penanganan retur di platform atau Expedisi` | Proses foll up retur lebih dari 14 hari dengan maksimal 5% retur | accurate_daily_returns (3.351) + shopee_returns (271) + GET /daily-returns/stats. | Bisa otomatis sekarang. Data retur sudah ditarik rutin dari marketplace dan Accurate. |
| 0.5 | `Pencatatan retur penjualan` | Input data retur dengan max laporan inputan retur bulanan selesai tanggal 3 bulan berikutnya | accurate_daily_returns (3.351) + shopee_returns (271) + GET /daily-returns/stats. | Bisa otomatis sekarang. Data retur sudah ditarik rutin dari marketplace dan Accurate. |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses AR minimal 2 ide terdaftar perbulan | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV / Leader | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

### AR Staff

Template `KPI Sales Admin`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.5 | `Pencatatan Penjualan` | Input data penjualan dengan max laporan inputan penjualan bulanan selesai tanggal 3 bulan berikutnya | `accurate_daily_invoices` via `GET /accurate/daily-invoices/kpi/pencatatan`, sumber `kinerja_sales_admin` metrik `penjualan_tuntas_cutoff_persen` (bip-erp PR #1254, belum merge). | Bisa otomatis, mesinnya sudah siap — sama seperti retur. Tinggal menunggu PR #1254 merge lalu dikonfigurasi ke template. |
| 0.3 | `Rekonsiliasi stok penjualan` | Rekonsiliasi data stok terjual dengan data pengiriman gudang dengan Max laporan rekonsiliasi stok selesai tanggal 3 bulan berikutnya | Accurate live proxy + GET /transactions/reconciliation dan /reconciliation/missing. accurate_bank_accounts (44). | Bisa sebagian. Alat pencocokan data sudah ada, tapi perlu disepakati dulu apa yang dihitung sebagai selisih dan kapan batas waktunya. |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses AR Minimal 2 ide inovasi terdaftar perbulan | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV / Leader | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

### Account Payable

Template `KPI Finance Staff Account Payable`, 6 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Cashflow terpantau 100% setiap minggu, operating cashflow ≥ 100%` | Mengecek expense dari cost control sesuai anggaran | Budget TIDAK tersimpan di ERP mana pun. Realisasi ada di Accurate; perlu master anggaran lebih dulu. | Belum bisa otomatis. Pengeluarannya sudah tercatat, tapi anggarannya belum pernah dimasukkan ke sistem, jadi tidak ada yang bisa dibandingkan. |
| 0.2 | `100% pembayaran dan pengeluaran sesuai rencana cashflow` | Memvalidasi dan mencatat pengeluaran operasional sebelum dibayarkan | ~~Accurate live proxy P&L~~ **Koreksi 2026-08-12**: redefinisi jadi "% faktur dibayar tepat waktu vs `dueDate`", sumbernya `purchase-invoice/list.do` (field `lastPaymentDate`, terbukti lewat probe live — 94,1% faktur Lunas punya tanggalnya, 5,9% lunas via alokasi DP dikecualikan). | 🟡 **Sedang dibangun** — sumber `kinerja_ap` di [[Microservices - Procurement Service]] + [[Microservices - Employee Service]], PR [#1178](https://github.com/bip-itteam-internal/bip-erp/pull/1178) belum merge, belum dikonfigurasi ke `kpi_template`. |
| 0.2 | `Perhitungan harga pokok produksi (HPP)` | Costing HPP 95% valid dengan realisasi costing max 1 hari setelah permintaan | **Koreksi 2026-08-12**: `/profit/costing-ratio` menjawab (486/486 SKU produksi punya HPP) tapi **selalu 100% dan tak ber-periode** — nilainya identik tiap bulan, dan separuh definisinya ("realisasi costing max 1 hari setelah permintaan") tak punya sumber sama sekali. | ⚠️ **Tetap perlu definisi ulang**, bukan "bisa otomatis sekarang" — metrik berbobot besar yang tak pernah bergerak tidak mengukur apa pun (pola sama `uptime` sebelum dibalik jadi `downtime`). |
| 0.15 | `Minimal ide inovasi baru dari tim pada setiap quartal` | Mengidentifikasi peluang inovasi di proses finance minimal 1 ide inovasi terdaftar per bulan | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |
| 0.1 | `Laporan credit team dibuat 100% tepat waktu dan terdokumentasi` | Menyusun laporan credit term berdasarkan data valid selesai tepat waktu setiap bulan | **Koreksi 2026-08-12**: `term_name`/`due_date` memang lengkap 2.055/2.055 di `procurement_db.faktur_pembelian`, tapi KPI-nya mengukur **penyerahan laporan**, bukan datanya — tak ada jejak kapan laporan diserahkan. | ⚠️ **Tetap perlu definisi ulang**. Data yang disebut kolom sebelumnya memang ada, tapi bukan data yang dibutuhkan metrik ini. |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

### Cost Control

Template `KPI Cost Control`, 7 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Varians antara budget vs realisasi OPEX ≤ ±5%` | Review Cash Outflow Mingguan - Realisasi OPEX dalam batas ±5% dari budget | Budget TIDAK tersimpan di ERP mana pun. Realisasi ada di Accurate; perlu master anggaran lebih dulu. | Belum bisa otomatis. Pengeluarannya sudah tercatat, tapi anggarannya belum pernah dimasukkan ke sistem, jadi tidak ada yang bisa dibandingkan. |
| 0.1 | `Penurunan biaya admin/non operasional minimal 2% YoY` | Analisis biaya berulang dan rekomendasi perbaikan | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.2 | `Penurunan OPEX 3–5% dalam 6 bulan` | Melakukan Analisis Varians OPEX dengan minimal 3 rekomendasi efisiensi cost driver setiap bulan | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.15 | `Forecast cashflow mingguan dengan akurasi ≥ 95%.` | Analisis Deviasi Forecast vs Aktual | TIDAK ADA modul forecast/demand planning. | Belum bisa otomatis. Sistem belum bisa memperkirakan permintaan, jadi tidak ada pembanding untuk menilai akurasinya. |
| 0.2 | `Pengelolaan Kas Iklan` | Akurasi Distribusi kas iklan dan pencatatan | Accurate live proxy + GET /transactions/reconciliation dan /reconciliation/missing. accurate_bank_accounts (44). | Bisa sebagian. Alat pencocokan data sudah ada, tapi perlu disepakati dulu apa yang dihitung sebagai selisih dan kapan batas waktunya. |
| 0.1 | `Minimal 5 ide inovasi baru dari tim` | Mengidentifikasi peluang inovasi di proses cost control | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |
| 0.05 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV | TIDAK ADA log 1-on-1. Perlu fitur baru. | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah. |

### Finance Supervisor

Template `KPI Supervisor Finance`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Revenue 240M` | Monitoring AR & Collection untuk Menjaga Cashflow Penjualan dengan mengurangi piutang aging > 60 hari sampai < 5% dari total AR. | tt_business_gmv_max_performance_reports (712.855) + marketing_analytics mart_profit_attribution (405.543, level ad/campaign/video/shop/product). Untuk level departemen perlu pemetaan toko ke departemen lebih dulu. | Bisa otomatis, tapi tentukan dulu toko mana milik departemen mana. Tanpa itu ada toko yang omzetnya tidak terhitung, dan itu sudah pernah terjadi senilai Rp 715 juta dalam sebulan. |
| 0.25 | `Rasio EBITDA 45%` | Kontrol OPEX dengan Budget Compliance 95% (Varians antara budget vs realisasi OPEX ≤ ±5%) | Budget TIDAK tersimpan di ERP mana pun. Realisasi ada di Accurate; perlu master anggaran lebih dulu. | Belum bisa otomatis. Pengeluarannya sudah tercatat, tapi anggarannya belum pernah dimasukkan ke sistem, jadi tidak ada yang bisa dibandingkan. |
| 0.2 | `Net income 20%` | Kontrol Beban Non-Operasional ≤ 2% | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.1 | `Return on Operation = 2,75` | Cashflow Forecasting mingguan dengan akurasi ≥ 95%. | TIDAK ADA modul forecast/demand planning. | Belum bisa otomatis. Sistem belum bisa memperkirakan permintaan, jadi tidak ada pembanding untuk menilai akurasinya. |
| 0.2 | `Performance Monitoring Team` | KPI Tim minimal skor 70 | Sumber skor_tim + reduksi rata_rata, scope department. Sudah didukung mesin; tinggal isi konfigurasi. | Bisa otomatis sekarang. Sistem tinggal merata-ratakan skor anggota departemen, dan mesinnya sudah siap. |

### Junior Accountant

Template `KPI Accounting CV`, 6 metrik.

| Bobot | Label                                                                 | Target / keterangan                                                                                                                                                                 | Sumber di sistem erp                                                                                                                                  | Rekomendasi                                                                                                                           |
| ----: | --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
|   0.3 | `Laporan keuangan`                                                    | Menyusun laporan keuangan dengan persentase laporan keuangan secara akurat dan tepat waktu max tgl 4 bulan berikutnya                                                               | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini.                                                 |
|  0.25 | `Pengelolaan kas`                                                     | Melakukan rekonsiliasi bank dan pencatatan kas laporan keuangan dengan Presentase selisih antara laporan keuangan perusahaan dengan rekening koran setiap bulan (Target 0% selisih) | Accurate live proxy + GET /transactions/reconciliation dan /reconciliation/missing. accurate_bank_accounts (44).                                      | Bisa sebagian. Alat pencocokan data sudah ada, tapi perlu disepakati dulu apa yang dihitung sebagai selisih dan kapan batas waktunya. |
|  0.15 | `Pengelolaan asset/perlengkapan`                                      | Pengecekan dan depresiasi asset dengan Presentase aset dan perlengkapan tercatat secara akurat dan tepat waktu max tgl 4 bulan berikutnya                                           | manufacture_resi (328.272) + warehouse_db.fulfillment_orders (38.949, event pick/pack/handover).                                                      | Bisa otomatis sekarang. Data resi dan proses gudang sudah tercatat lengkap.                                                           |
|   0.1 | `Pajak`                                                               | Pajak terbayar tepat waktu dengan persentase pajak perusahaan dan karyawan terbayar tepat waktu (max 1 hari sebelum jatuh tempo)                                                    | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets.                                                       | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate.                                                |
|   0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal`             | Mengidentifikasi peluang inovasi di proses accounting dengan Minimal 2 ide inovasi terdaftar perbulan di tiap kuartal                                                               | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru.                                    | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu.                                     |
|   0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV                                                                                                                    | TIDAK ADA log 1-on-1. Perlu fitur baru.                                                                                                               | Belum bisa otomatis. Belum ada tempat mencatat pertemuan atasan dengan anak buah.                                                     |

### Junior Accountant

Template `KPI Accounting PT`, 4 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.35 | `Transaksi Keuangan` | Akurasi & ketepatan waktu pencatatan transaksi keuangan | Accurate live proxy + GET /transactions/reconciliation dan /reconciliation/missing. accurate_bank_accounts (44). | Bisa sebagian. Alat pencocokan data sudah ada, tapi perlu disepakati dulu apa yang dihitung sebagai selisih dan kapan batas waktunya. |
| 0.35 | `Transaksi Non-keuangan` | Akurasi & ketepatan waktu pencatatan transaksi non-keuangan | Accurate live proxy + GET /transactions/reconciliation dan /reconciliation/missing. accurate_bank_accounts (44). | Bisa sebagian. Alat pencocokan data sudah ada, tapi perlu disepakati dulu apa yang dihitung sebagai selisih dan kapan batas waktunya. |
| 0.15 | `Minimal 5 ide inovasi baru dari tim pada Q1` | Mengidentifikasi peluang inovasi di proses accounting | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |
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
| 0.1 | `Minimal ide inovasi baru dari tim pada tiap kuartal` | Mengidentifikasi peluang inovasi di proses accounting minimal 2 ide inovasi terdaftar per bulan di kuartal 1 | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |
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
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses tax dengan minimal 2 ide inovasi terdaftar per bulan | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |

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
| 0.1 | `SOP` | Tingkat Kedisipilnan Karyawan ( Attandance & Intergritas ) | GET /attendance/report?date=YYYY-MM (status Hadir/Terlambat/Alpha + late_hour). 24.163 entri, periode 26 ke 26 sesuai payroll. | Bisa otomatis sekarang. Data absensi lengkap dan periodenya sudah mengikuti siklus gajian. |
| 0.1 | `Kaizen` | Jumlah Inovasi All Divisi ( 7 / Bulan ) | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |

### HRD Supervisor

Template `KPI Supervisor HRGA`, 10 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.15 | `Revenue 240 Miliar` | Menjamin ketersediaan tenaga kerja dengan rata-rata time recruitment <30 hari untuk posisi kritikal | Modul Recruitment ADA tapi koleksi candidate KOSONG (job_requisition 2, job_posting 1). | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. |
| 0.05 | `Net Income 20%` | Efisiensi biaya operasional GA min. 5% dari bulanan | Accurate live proxy: /accounting/profit-loss, /balance-sheet, /profit/cash-flow, /fixed-assets. | Bisa otomatis sekarang. Laporan laba rugi dan arus kas diambil langsung dari Accurate. |
| 0.05 | `Return On Operation Asset` | Monitoring aset 100% terdata secara realtime | accurate_daily_returns (3.351) + shopee_returns (271) + GET /daily-returns/stats. | Bisa otomatis sekarang. Data retur sudah ditarik rutin dari marketplace dan Accurate. |
| 0.2 | `Performance Monitoring 100% Terimplementasi di Q4` | Memastikan seluruh tim/karyawan di setiap departemen memiliki skor KPI Min. 70 | Sumber skor_tim + reduksi rata_rata, scope department. Sudah didukung mesin; tinggal isi konfigurasi. | Bisa otomatis sekarang. Sistem tinggal merata-ratakan skor anggota departemen, dan mesinnya sudah siap. |
| 0.1 | `Turn Over Rate Target 5% per Tahun` | Peningkatan Kualitas Rekruitment | Modul Recruitment ADA tapi koleksi candidate KOSONG (job_requisition 2, job_posting 1). | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. |
| 0.1 | `Implementasi Training` | Memenuhi kebutuhan pelatihan untuk talent dan seluruh karyawan 100% terpenuhi tiap bulan dan terjadi peningkatan performa. | Modul Training ADA di kode tapi koleksi training & training_participant KOSONG di prod. Skor & survei kepuasan training juga belum ada fieldnya. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu pelatihan sudah ada, hanya belum ada yang mengisinya. Nilai dan survei kepuasan pelatihan memang belum ada tempatnya. |
| 0.2 | `Performance Monitoring Team HRGA` | Rata-rata KPI Team HRGA min. 70 | Sumber skor_tim + reduksi rata_rata, scope department. Sudah didukung mesin; tinggal isi konfigurasi. | Bisa otomatis sekarang. Sistem tinggal merata-ratakan skor anggota departemen, dan mesinnya sudah siap. |
| 0.05 | `Employee Productivity sebesar 120 Juta per Employee ( DIv. Marketing )` | Memberikan Training, Coaching, atau Tools untuk meningkatkan Produktivitas. | Modul Training ADA di kode tapi koleksi training & training_participant KOSONG di prod. Skor & survei kepuasan training juga belum ada fieldnya. | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu pelatihan sudah ada, hanya belum ada yang mengisinya. Nilai dan survei kepuasan pelatihan memang belum ada tempatnya. |
| 0.05 | `Succession Planing Terimplementasi` | Menyusun Kaderisasi & Talent Pool - 100% Calon Successor memiliki Development Plan dan Siap apabila diperlukan | TIDAK ADA modul succession/talent pool. | Belum bisa otomatis. Belum ada pencatatan calon penerus jabatan. |
| 0.05 | `Employee Satisfaction` | Tingkat kepuasan pelayanan Team General Service minimal 90% memberikan penilaian 5 dari all karyawan | GET /task-management/report/csat. Pembacaan ulang prod 2026-08-06: **17 tiket ter-rating** seumur hidup, 13 di antaranya Juli. Masih tipis, dan seluruh rating Juli bernilai 5/5 sehingga belum membedakan siapa pun. | Belum layak dipakai. Yang menilai baru 17 orang seumur hidup dan semuanya memberi nilai penuh, jadi angkanya belum bisa membedakan pelayanan yang baik dari yang biasa saja. |

### Personalia

Template `Personalia Team`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Administrasi 1` | Terselesaikannya administrasi payroll dan absensi karyawan sesuai dengan ketentuan perusahaan secara akurat | GET /attendance/report?date=YYYY-MM (status Hadir/Terlambat/Alpha + late_hour). 24.163 entri, periode 26 ke 26 sesuai payroll. | Bisa otomatis sekarang. Data absensi lengkap dan periodenya sudah mengikuti siklus gajian. |
| 0.2 | `Administrasi 2` | Terselesaikannya administrasi BPJS rekening dan surat-surat karyawan sesuai dengan ketentuan perusahaan | payroll_db baru 1 payroll_run; GET /employee/bpjs tersedia. | Bisa sebagian. Data BPJS sudah ada, tapi payroll baru berjalan sekali sehingga belum cukup jadi dasar penilaian. |
| 0.2 | `Administrasi 3` | Terselesaikannya administrasi kontrak karyawan baru dan perpanjang kontrak dengan tepat | work_data.contract_ending + join_date di employee_db. | Bisa otomatis sekarang. Tanggal masuk dan tanggal berakhir kontrak sudah tersimpan. |
| 0.25 | `Administrasi 4` | Pengkinian Data Karyawan terupdate secara akurat di drive utama | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.1 | `Kedisiplinan` | Kehadiran dan Ketepatan Waktu | GET /attendance/report?date=YYYY-MM (status Hadir/Terlambat/Alpha + late_hour). 24.163 entri, periode 26 ke 26 sesuai payroll. | Bisa otomatis sekarang. Data absensi lengkap dan periodenya sudah mengikuti siklus gajian. |

### Recruitment & Onboarding

Template `Recruitment Team`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.25 | `Rekrutmen Seleksi dan penempatan` | Time to Fulfilment Rate ( < 30 Hari ) All Vacant | Modul Recruitment ADA tapi koleksi candidate KOSONG (job_requisition 2, job_posting 1). | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. |
| 0.2 | `Rekrutmen Seleksi dan penempatan` | Membuat rencana jadwal dan pelaksanaan onboarding karyawan Masa Percobaan. | Modul Recruitment ADA tapi koleksi candidate KOSONG (job_requisition 2, job_posting 1). | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. |
| 0.2 | `Rekrutmen Seleksi dan Penempatan` | Presentase Data Base Buffer Kebutuan MPP | Modul Recruitment ADA tapi koleksi candidate KOSONG (job_requisition 2, job_posting 1). | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. |
| 0.25 | `Job Description` | Skor Kompetensi New Hire Fase On Boarding >80 | Modul Recruitment ADA tapi koleksi candidate KOSONG (job_requisition 2, job_posting 1). | Belum bisa sekarang, tapi tidak perlu bikin fitur baru. Menu rekrutmen sudah ada, hanya data pelamarnya belum diisi. |
| 0.1 | `Kaizen` | Jumlah inisiatif perbaikan yang diterapkan | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |

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
| 0.25 | `Inovation & Improvement` | Meningkatkan Inovasi & Efisiensi Produk | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |
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
| 0.2 | `Kaizen` | Jumlah inisiatif perbaikan yang diterapkan. | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |

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
| 0.1 | `Kaizen 1` | Mengurangi Jumlah CAPA produksi yang ditemukan. | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |
| 0.15 | `Kaizen 2` | Menjaga Kualitas Produk Target 98% ( Sesuai SOP QC ) | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |
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
| 0.2 | `Kaizen dan Growth` | Melakukan Review Kesesuaian SOP & WI di Area Produksi dengan target 5 produk/bulan | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |

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

> **Departemen pertama yang dikerjakan.** Kodenya **sudah merge (PR #866) dan deploy ke produksi 1 Agustus 2026**, terverifikasi terhadap data sungguhan. Lihat [[Microservices - Monitoring Service]].
>
> ✅ **TIGA metrik menyala otomatis sejak 2026-08-06.** Catatan lama di sini ("belum satu pun metrik benar-benar otomatis", sensus 1 Agustus: 0 dari 70 template) sudah tidak berlaku. Yang dinyalakan: `Performance Monitoring Team` pada **Leader** (`skor_tim`, scope `team`, target 70) dan **Supervisor** (scope `department`), serta `Network ` pada **IT Support** (`uptime_sistem`, target 90).
>
> Diverifikasi hari itu juga untuk orang sungguhan: Leader periode 2026-07 menghasilkan **100** dengan cakupan penuh (`otomatis`, basis "rata-rata 86.00 dari 5 pengukuran"), IT Support **100** dengan cakupan 74,19% sehingga dilaporkan **`semi`** (heartbeat baru 23 dari 31 hari), dan periode 2026-08 yang belum dinilai menjawab "belum dapat dihitung" alih-alih nol. Rinciannya di [[HRIS - Otomasi Skor KPI]].
>
> **`kpi_score` tidak tersentuh** (tetap 0 dokumen ber-`auto_value`): snapshot penilaian yang sudah ada beku, jadi angka otomatis baru terpakai pada penilaian **Agustus** di awal September. Kebetulan angkanya sama persis dengan yang sudah diisi manual, jadi tak ada selisih yang perlu dijelaskan ke siapa pun.
>
> **Tujuh metrik punya sumber terdaftar, tetapi hanya lima menyentuh orang.** Posisi `IT Infrastructure` **tidak punya karyawan sama sekali (0 orang)**, sehingga `System` 0,1 dan `Server` 0,1 menempel di template yang tak dipegang siapa pun. Yang nyata:
>
> | Posisi | Orang | Metrik siap | Sumber | Bobot |
> |---|---:|---|---|---:|
> | `IT Support` | 2 | `Network ` | `uptime_sistem` | 0,4 |
> | `Tech Development Leader ` | 1 | `Revenue 240M` · `Performance Monitoring Team` | `uptime_sistem` · `skor_tim` | 0,6 |
> | `Tech Development Supervisor` | 1 | `Revenue 240M` · `Performance Monitoring Team` | `uptime_sistem` · `skor_tim` | 0,5 |
>
> **Tujuh developer tidak tersentuh sama sekali.** 2 Backend, 1 Frontend, dan 4 Fullstack — mayoritas departemen — tidak punya satu pun metrik dengan sumber data di sistem. Metrik mereka (`Delivery`, `Quality`, `Support`, `Improvement`, `System Development`, `Kaizen`) semuanya belum terpetakan.
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
| 0.5 | `System Development` | Penyelesaian Project Development Software & Uprgade Fitur Penunjang Operational | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.2 | `Implementasi` | Monitoring Implementasi Sinkronisasi/Review dengan Requester | Stok & penjualan tersedia, tapi tanpa modul demand planning sebagian metrik ini tidak terdefinisi. | Bisa sebagian. Data stok dan penjualan ada, tapi rumusnya perlu disepakati dulu karena belum ada perencanaan permintaan. |
| 0.2 | `Customer Satifaction` | Survey Penilaian Software yang sudah diimplementasikan | GET /task-management/report/csat. Pembacaan ulang prod 2026-08-06: **17 tiket ter-rating** seumur hidup, 13 di antaranya Juli. Masih tipis, dan seluruh rating Juli bernilai 5/5 sehingga belum membedakan siapa pun. | Belum layak dipakai. Yang menilai baru 17 orang seumur hidup dan semuanya memberi nilai penuh, jadi angkanya belum bisa membedakan pelayanan yang baik dari yang biasa saja. |
| 0.1 | `Kaizen` | Ide Improvement | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |

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
| 0.4 | `Network` | Optimalisasi Uptime Server & Sistem | Sumber `uptime_sistem` (GET /monitoring/kpi/uptime?periode=YYYY-MM) + reduksi `rata_rata`, arah `naik`. 34 monitor aktif. SUDAH DEPLOY & terverifikasi di prod 2026-08-01 (Juli 99,81% atas 23 dari 31 hari; Juni null). | Bisa otomatis sekarang, tapi angkanya baru penuh mulai Agustus 2026. Sistem sudah memantau 34 server dan aplikasi, dan tiap bulan dilaporkan berapa hari yang benar-benar ada datanya. |
| 0.15 | `Customer Satisfaction` | Kepuasan Pelayanan IT Support | GET /task-management/report/csat. Pembacaan ulang prod 2026-08-06: **17 tiket ter-rating** seumur hidup, 13 di antaranya Juli. Masih tipis, dan seluruh rating Juli bernilai 5/5 sehingga belum membedakan siapa pun. | Belum layak dipakai. Yang menilai baru 17 orang seumur hidup dan semuanya memberi nilai penuh, jadi angkanya belum bisa membedakan pelayanan yang baik dari yang biasa saja. |
| 0.3 | `Problem Solving` | Penyelesaian E - Ticket sesuai dengan SLA ( Service Level Agreement ) | GET /task-management/report/sla. Pembacaan ulang prod 2026-08-06: resolusi **214 sampel** terukur seumur hidup (56 di Juli), response 63. Angka "0 sampel" di versi sebelumnya SALAH, sebabnya sensus memakai nama field `completedAt` padahal BSON-nya `completed_at`. | Bisa otomatis sekarang. Kecepatan menanggapi dan menyelesaikan tiket dua-duanya sudah terhitung. Yang perlu diperhatikan justru hasilnya: on-time rate Juli rendah, jadi sepakati dulu targetnya sebelum dipakai menilai orang. |
| 0.15 | `Kaizen` | Improvement | TIDAK ADA modul Kaizen/ide inovasi di sistem (pencarian nol hasil di services + shared-library). Perlu fitur baru. | Belum bisa otomatis. Sistem belum punya tempat mencatat ide perbaikan, jadi harus dibuatkan dulu. |

### Tech Development Leader

Template `Leader`, 5 metrik.

| Bobot | Label | Target / keterangan | Sumber di sistem erp | Rekomendasi |
|---:|---|---|---|---|
| 0.2 | `Revenue 240M` | Menjamin operasional IT tanpa gangguan | Sumber `uptime_sistem` (GET /monitoring/kpi/uptime?periode=YYYY-MM) + reduksi `rata_rata`, arah `naik`. 34 monitor aktif. SUDAH DEPLOY & terverifikasi di prod 2026-08-01 (Juli 99,81% atas 23 dari 31 hari; Juni null). | Bisa otomatis sekarang, tapi angkanya baru penuh mulai Agustus 2026. Sistem sudah memantau 34 server dan aplikasi, dan tiap bulan dilaporkan berapa hari yang benar-benar ada datanya. |
| 0.1 | `Net income 20%` | Pengendalian anggaran IT | Budget TIDAK tersimpan di ERP mana pun. Realisasi ada di Accurate; perlu master anggaran lebih dulu. | Belum bisa otomatis. Pengeluarannya sudah tercatat, tapi anggarannya belum pernah dimasukkan ke sistem, jadi tidak ada yang bisa dibandingkan. |
| 0.2 | `Integration System Development di Q4` | On-time project delivery rate (%) – proyek IT/development selesai sesuai timeline | Belum dipetakan. Tentukan dengan langkah 1 di RUN - Menambah Metrik KPI Otomatis (cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya). | Perlu diperiksa dulu. Belum jelas data mana di sistem yang dipakai untuk menilai ini. |
| 0.1 | `Customer Satifaction` | Average Tingkat Kepuasan User Terhadap Pelayanan Team IT ( Fullstack & Support ) | GET /task-management/report/csat. Pembacaan ulang prod 2026-08-06: **17 tiket ter-rating** seumur hidup, 13 di antaranya Juli. Masih tipis, dan seluruh rating Juli bernilai 5/5 sehingga belum membedakan siapa pun. | Belum layak dipakai. Yang menilai baru 17 orang seumur hidup dan semuanya memberi nilai penuh, jadi angkanya belum bisa membedakan pelayanan yang baik dari yang biasa saja. |
| 0.4 | `Performance Monitoring Team` | KPI Team | Sumber skor_tim + reduksi rata_rata, scope department. Sudah didukung mesin; tinggal isi konfigurasi. | Bisa otomatis sekarang. Sistem tinggal merata-ratakan skor anggota departemen, dan mesinnya sudah siap. |

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
