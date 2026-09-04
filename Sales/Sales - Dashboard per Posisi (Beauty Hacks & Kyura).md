## Deskripsi

*Rancangan isi dashboard per posisi untuk dua divisi brand, **Beauty Hacks** (10 posisi) dan **Kyura** (9 posisi). Diturunkan mengikuti [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]. Keduanya digabung dalam satu dokumen karena **berbagi delapan posisi dengan nama dan struktur metrik yang sama persis**; yang berbeda hanya angka targetnya.*

- **Status**: 🟡 **Rancangan**. Tak satu pun posisi di sini punya lembar per posisi. Yang ada [[Sales - Marketing Dashboard (Index)|Marketing Analytics]], 16 halaman per TOPIK, bukan per orang.
- **Angka KPI diukur 2026-08-28** (sumber: [[HRIS - Matriks KPI per Departemen]]). **Ukur ulang sebelum dipakai mengambil keputusan.**
- **Path di repo**: `erp-frontend/src/features/marketing-analytics/` · `erp-frontend/src/features/marketing-insight/`

## Kenapa dua brand satu dokumen

Delapan posisi ini ada di **kedua** divisi dengan struktur metrik yang sama: Affiliate, Buzzer, Customer Support, Host Live, ICC, Leader, Marketplace Advertiser, Meta Advertiser. Yang berbeda cuma nama supervisornya, angka targetnya, dan Video Editor yang hanya ada di Beauty Hacks.

Menulis dua dokumen berarti dua tempat yang harus dijaga sama, dan yang ketinggalan tidak akan berbunyi. Perbedaan antar-brand ditulis di tempatnya masing-masing di bawah.

## Yang membedakan divisi ini dari seluruh divisi lain

Di HR, GA, dan Manufaktur, penghambatnya **ketiadaan data**. Di sini datanya justru paling tebal di seluruh perusahaan:

| Sumber | Baris |
|---|---:|
| `tt_business_gmv_max_performance_reports` | 712.855 |
| `mart_profit_attribution` (level ad/campaign/video/shop/product) | 405.543 |
| `affiliate_orders` | 194.761 |
| `tt_shop_video_performances` (ada `published_at` & GMV per video) | 85.149 |
| `shopee_affiliate_performance` | 8.092 |
| `marketplace_reviews` | 6.314 |

Layarnya pun sudah ada, 16 halaman Marketing Analytics lengkap dengan saringan, kartu vonis, dan blok keputusan.

⚠️ **RALAT 2026-09-04.** Dokumen ini semula menyatakan atribusi ke orang adalah gerbang tunggal divisi ini, dan bahwa jembatannya `icc_account_mappings`. **Keduanya tidak akurat**, dan koreksinya mengubah rekomendasi di bawah. Diukur langsung ke `integration_db` produksi hari itu:

**a. `icc_account_mappings` TERISI dan sehat.** 61 dokumen, 55 aktif, dan **seluruh 55 baris aktif punya `employee_id`** (100%), mencakup **32 orang unik** di tim Beauty Hacks dan Kyura. Dari 44 baris ber-`tiktok_shop_id`, **tak satu toko pun dibagi dua orang** (maksimum satu orang per toko), jadi atribusi lewat toko memang membedakan orang. Yang tipis justru kanal lain: hanya 2 baris punya `tiktok_advertiser_id` dan 8 punya `shopee_shop_id`.

**b. Atribusi VIDEO tidak lewat pemetaan itu sama sekali.** `ICCVideoMetric` (`services/integration/internal/domain/entity/icc_video_metric.go`) beratribut **`creator_username`**, dijoin lewat `tt_business_campaign_items` dan tanggal tayangnya dari snapshot `tt_shop_video_performances`. Jadi metrik per-video ICC punya jalur atribusinya sendiri, dan `icc_account_mappings` bukan prasyaratnya.

**c. Metrik per-video ICC SUDAH dihitung backend**, dan sudah dikonsumsi `services/insentive` lewat `EvaluateICCVideoIncentive` serta `IsICCVideoEligible`.

⛔ **Peringatan yang wajib dibaca sebelum merancang layar apa pun di atasnya**, tertulis di komentar entity-nya: **ROAS per-video TIDAK DAPAT DIANDALKAN**, karena alokasi biayanya bocor ke bucket campaign `-1`. Itu keputusan produk yang diterima sadar, bukan cacat yang belum ketahuan. Menggambar ROAS per video sebagai angka penilaian akan memberi kekeliruan itu tampilan resmi.

**Konsekuensi rancangan yang berubah**: karena metriknya sudah ada dan sudah dipakai modul insentif, langkah berikutnya untuk divisi ini bukan membangun dashboard.

✅ **Pemeriksaan itu sudah dilakukan 2026-09-04**, dan hasilnya lebih baik daripada dashboard mana pun: endpoint `GET /api/integration/insight/icc-video-metrics` **sudah hidup**, tetapi formulir insentif di frontend masih **mengetik CTR, Watch 25%, ROAS, dan Orders dengan tangan** per video. Nol berkas frontend memanggil endpoint itu. Pekerjaan berikutnya karena itu menyambungkan keduanya, bukan membangun layar baru. Rincian, bukti, dan peringatan ROAS-nya di [[Finance - Incentive]] § Metrik ICC sudah dihitung sistem.

Pola "yang mau dibangun ternyata sudah ada di modul lain" kini sudah berulang **empat kali** dalam analisis keluarga dokumen ini.

## Posisi yang bisa dirancang sekarang

### ICC (Internal Content Creator)

Ada di kedua brand, 3 metrik, struktur sama.

| Bobot | Metrik | Target BH | Target Kyura |
|---:|---|---|---|
| 0,4 | Jumlah video | 125/bulan | 125/bulan |
| 0,4 | Video memenuhi standar tinggi | GMV MAX, ≥ 30% atau min. 37 | 150.000/video, ≥ 30% atau min. 37 |
| 0,2 | Video memenuhi standar dasar | VSA, ≥ 70% atau min. 87 | 10.000/video, ≥ 70% atau min. 87 |

Sumber ketiganya sama: `tt_shop_video_performances`, yang punya `published_at` dan GMV per video.

**Bisa ditampilkan sekarang.** Posisi paling siap di kedua divisi.

- **Visual utama**: cacah video per bulan terhadap target 125, dengan tiga pita standar (belum memenuhi, standar dasar, standar tinggi) ditumpuk. Satu bagan menjawab ketiga metriknya sekaligus, dan ketiganya memang membaca deret yang sama.
- Daftar video bulan berjalan beserta GMV masing-masing, diurutkan menurun.

⚠️ **Atribusinya lewat `creator_username`, bukan `icc_account_mappings`** (lihat ralat di atas). Jalur itu sudah ada dan sudah dipakai modul insentif, jadi posisi ini tidak terhalang pemetaan. Yang perlu diperiksa lebih dulu justru apakah layarnya sudah ada di `finance/incentive`.

### Leader

Ada di kedua brand, 3 metrik. Beauty Hacks: Performance Monitoring (0,2), Conversion (0,4), ROI (0,4). Kyura: ROI (0,4), Conversion (0,4), Performance Monitoring (0,2).

**Bisa ditampilkan sekarang.** Conversion dan ROI keduanya bersumber data GMV yang tebal.

- **Visual utama**: tren ROI bulanan terhadap ambang (BH > 3,2; Kyura 3,2). Ia berbobot 0,4 dan satu-satunya yang bergerak tajam.
- Kartu konversi terhadap target (BH 120.000; Kyura 54.000).
- Sebaran skor KPI anggota tim terhadap ambang.

⚠️ Metrik Performance Monitoring Beauty Hacks memakai `skor_tim` dengan reduksi `rasio_ambang`, dan **cakupan tim menuntut `work_data.supervisor_id` terisi**. Bila belum, angkanya bukan salah melainkan tak keluar sama sekali.

### Marketplace Advertiser

Dua metrik di kedua brand, keduanya bersumber data GMV. BH: Conversion (0,7) + CPA (0,3). Kyura: Conversion (0,5) + ROI (0,5).

**Bisa ditampilkan sekarang.** Tren CPA atau ROI per kampanye, plus kartu konversi terhadap target. Halaman [[Sales - Marketing Dashboard (Index)|GMV Max Monitoring]] sudah menggambar hampir persis ini, tinggal disaring per pengiklan.

### Affiliate

BH 2 metrik, Kyura 3. Sumber `affiliate_orders` (194.761) dan `shopee_affiliate_performance` (8.092).

⚠️ **Satu keputusan harus diambil lebih dulu**: definisi "affiliator baru bergabung dalam sebulan" belum ditetapkan. Tanpa itu metrik berbobot 0,3 (BH) atau 0,4 (Kyura) tak bisa diangkakan, dan itu **keputusan pemilik KPI, bukan pekerjaan kode**.

⚠️ Untuk atribusi order afiliasi, tanggalnya **wajib** memakai `place_order_date`; `place_order_time` dan `conversion_completed_time` bernilai kosong seluruhnya di produksi. Menyaring rentang lewat dua field itu mengembalikan nol baris tanpa satu pun galat.

### Host Live

BH 3 metrik (Conversion 0,6, ROI 0,3, Performance Monitoring 0,1); Kyura 2 (Conversion 0,7, ROI 0,3).

**Bisa ditampilkan sekarang** untuk Kyura: konversi dan ROI keduanya bersumber. Halaman Live dan Live Shift di Marketing Analytics sudah menggambar deretnya.

⛔ Metrik ROI Beauty Hacks dipetakan ke *"TIDAK ADA tracker pajak/audit internal/CAPA/izin BPOM"*, yang **tidak berhubungan sama sekali** dengan ROI live. Salah petak, sekelas dengan temuan di [[GA - Dashboard per Posisi]]. Perbaiki pemetaannya sebelum merancang kartunya.

### Customer Support

**Kyura bisa, Beauty Hacks belum.** Kyura metrik Perfoma (0,4, rating toko) bersumber `GET /integration/reviews/summary` dengan 6.314 ulasan. Beauty Hacks metrik terbesarnya Konversi (0,6) bersumber data GMV, tetapi Closing Rate (0,3) menunggu data percakapan CS yang tidak ada di sistem mana pun.

### Supervisor (BeautyHacks & Kyura)

Empat metrik, struktur sama di kedua brand: Revenue (0,6), Performance Monitoring Team (0,3), Inventory turnover (0,05), Customer Satisfaction (0,05).

**Bisa ditampilkan sekarang.** Dua metrik berbobot total 0,9, dan itu porsi tertinggi di seluruh dokumen ini.

- **Visual utama**: pencapaian revenue bulanan terhadap target (BH achievement 100%; Kyura profit 546 juta atau omzet 4,09 miliar).
- Sebaran skor KPI anggota departemen terhadap ambang 70.

⚠️ Metrik Customer Satisfaction bersandar `GET /task-management/report/csat` yang punya **17 tiket ter-rating seumur hidup**, dan seluruh rating Juli bernilai 5/5. Bobotnya memang cuma 0,05, tetapi **jangan digambar sebagai kartu ambang**: pil hijau dari 17 sampel akan dibaca sebagai fakta.

## Posisi yang TIDAK direkomendasikan dibuatkan dashboard

### Meta Advertiser (kedua brand)

⛔ **Nol dari empat metrik punya sumber**, dan sebabnya tunggal: **Meta/Facebook Ads tidak terintegrasi sama sekali.** Yang tersambung hanya TikTok Business/Shop, Shopee, Lazada, dan Accurate.

Ini bukan metrik yang belum dipetakan melainkan platform yang belum ada di sistem. Sampai integrasi Meta Ads berdiri, tak ada satu angka pun yang bisa digambar untuk posisi ini di kedua brand.

### Buzzer (kedua brand)

⛔ **Nol dari sembilan metrik punya sumber** (BH 4 + 1 template contoh, Kyura 5), semuanya karena satu hal: **akun buzzer memakai akun personal dan tidak ada integrasi API.**

Metriknya menuntut kecepatan boosting, kuantitas engagement, dan kualitas komentar, ketiganya hanya terbaca dari akun yang tidak dikendalikan perusahaan. Menyambungkannya bukan pekerjaan backend melainkan keputusan tentang bagaimana buzzer bekerja.

⚠️ Template `Buzzer` Beauty Hacks berisi **satu metrik bernama `contoh` berbobot 1,0**. Itu template yang belum diisi, bukan penilaian. Jangan merancang apa pun di atasnya, dan sebaiknya dibersihkan di master data.

### Video Editor (hanya Beauty Hacks)

⛔ **Nol dari tiga metrik punya sumber.** Ketiganya menunggu tracker garapan desain dan video (pengajuan, persetujuan, tenggat) yang tidak ada di sistem.

⚠️ Catatan penting untuk yang tergoda menambalnya: metrik posisi ini menilai **mutu dan ketepatan garapan**, bukan performa video di marketplace. Memakai `tt_shop_video_performances` yang tebal itu akan menghasilkan angka yang mulus dan menjawab pertanyaan yang sama sekali lain. Video Editor dinilai atas apakah garapannya selesai tepat waktu dan disetujui, bukan atas GMV yang dihasilkan videonya.

## Metrik sirkular: berlaku lintas posisi

⚠️ Metrik bernama **`Perfomance Monitoring`** di Affiliate Kyura (0,2), Host Live Beauty Hacks (0,1), dan Leader Kyura (0,2) **merujuk skor KPI final pemegangnya sendiri**, sehingga metrik itu ikut menentukan dirinya.

Ia tetap manual sampai maknanya diputuskan ulang, dan **tidak boleh digambar di dashboard dalam bentuk apa pun**. Kartu yang menampilkan skor sendiri sebagai komponen skor sendiri akan membingungkan pembacanya tanpa ada yang bisa menjelaskan angkanya.

## Kebutuhan backend, terurut

1. ~~**Isi dan verifikasi `icc_account_mappings`.**~~ **SELESAI 2026-09-04, dan ternyata bukan prasyarat.** Pemetaannya sehat (55 dari 55 baris aktif terisi, 32 orang, satu toko satu orang), dan atribusi video memang tidak lewat situ. Yang menggantikannya sebagai langkah pertama: **periksa cakupan `finance/incentive`** sebelum merancang layar ICC apa pun, karena metriknya sudah dihitung dan sudah dikonsumsi modul insentif.
2. **Tetapkan definisi "affiliator baru bergabung".** Keputusan pemilik KPI, bukan kode. Mengunci bobot 0,3 sampai 0,4 di dua posisi.
3. **Perbaiki pemetaan ROI Host Live Beauty Hacks** yang menunjuk tracker pajak/BPOM.
4. **Bersihkan template `Buzzer` Beauty Hacks** yang berisi metrik `contoh`.
5. **Isi `work_data.supervisor_id`** supaya cakupan tim Leader bisa dihitung.
6. **Integrasi Meta Ads.** Membuka 4 metrik di 2 posisi, tetapi pekerjaan terbesar di daftar ini.
7. **Data percakapan CS** untuk Closing Rate Customer Support Beauty Hacks.

⚠️ **Yang TIDAK masuk daftar**: tracker garapan video dan integrasi akun buzzer. Keduanya menuntut keputusan tentang cara kerja orangnya lebih dulu, bukan endpoint baru.

## Dokumen Terkait

- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — prinsip penurunannya
- [[REF - Layout Dashboard erp-frontend]] — cara menyusunnya di layar
- [[HRIS - Matriks KPI per Departemen]] — sumber angka di dokumen ini
- [[Sales - ICC Account Manager Mapping]] — jembatan atribusi ke `employee_id`
- [[Sales - ICC Affiliate Mapping]] — atribusi sisi afiliasi
- [[Sales - Marketing Dashboard (Index)]] — layar yang sudah ada, per topik
- [[Sales - Marketing Analytics (Audit Ketersediaan Data)]] — audit sumber angka divisi ini
- [[Microservices - Marketing Analytics Service]] — pemilik `mart_profit_attribution`
- [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] — kepemilikan toko dan tim
