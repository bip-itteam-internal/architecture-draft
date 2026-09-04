# ANALISA - Dashboard per Posisi

Papan kerja untuk keluarga dok rancangan dashboard per posisi. Berubah tiap item selesai; yang arsitektural tetap di [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] dan dok divisi masing-masing. Indeks cakupan: [[REF - Dashboard per Posisi (Indeks Cakupan)]].

Disusun 2026-09-04. Angka cakupan bersandar salinan produksi 2026-08-28; **ukur ulang sebelum memutuskan**.

## Cara membaca

Urutannya disusun dari **daya ungkit dibagi ongkos**, bukan dari besar-kecilnya divisi. Tiga dari empat penghambat terbesar ternyata **tidak menuntut satu baris kode**, jadi gelombang 1 dan 3 dikerjakan orang di luar tim IT dan bisa berjalan paralel dengan gelombang 2.

Kolom **Siapa** menentukan apakah item ini tiket developer atau permintaan ke tim lain. Salah menaruhnya membuat pekerjaan non-kode menunggu rilis yang tak pernah relevan.

---

## Gelombang 1 — keputusan, nol kode

Berjalan paralel dengan gelombang 2. Tidak menahan siapa pun, tetapi nomor 1.1 **wajib mendahului** pembangunan layar untuk posisi yang terdampak.

- [ ] **1.1 Perbaiki 12 metrik salah petak** · 9 posisi, 7 divisi · *pemilik KPI*
      Daftar lengkap di [[REF - Dashboard per Posisi (Indeks Cakupan)]] § Salah petak yang tercatat.
      Yang paling mendesak, karena sumbernya berisi ratusan ribu baris sehingga angkanya akan mulus dan meyakinkan:
      - ketersediaan bahan baku & on time delivery (Staff Inventory) menunjuk **data iklan TikTok**
      - OTIF finished good (PPIC) menunjuk **data iklan TikTok**
      - rebate kontrak vendor (Procurement Leader) menunjuk **kontrak karyawan**
      - kelengkapan laporan audit (Internal Audit) menunjuk **data absensi**
      **Selesai bila**: tiap metrik punya sumber yang menjawab pertanyaannya, atau dinyatakan manual secara sadar.

- [ ] **1.2 Verifikasi isi `icc_account_mappings`** · menggerbang 11 posisi Sales · *IT + ICC*
      Tanpa atribusi `employee_id` ke akun, seluruh rancangan Sales menampilkan angka orang lain **tanpa satu pun galat**.
      **Selesai bila**: cakupan pemetaan terukur (berapa akun aktif punya `employee_id`), bukan sekadar tabelnya ada.

- [ ] **1.3 Petakan 47 metrik "belum dipetakan"** · 28 posisi, 8 divisi · *pemilik KPI*
      Bucket terbesar di seluruh analisis. Dahulukan divisi yang masuk gelombang 2.
      Prosedurnya di [[RUN - Menambah Metrik KPI Otomatis]] langkah 1: **cek jumlah dokumen sumbernya di prod, bukan keberadaan koleksinya**.

- [ ] **1.4 Bersihkan template `Buzzer` Beauty Hacks** yang berisi satu metrik bernama `contoh` berbobot 1,0 · *pemilik KPI*

---

## Gelombang 2 — bangun yang datanya sudah ada

- [x] **2.1 IT** — SELESAI 2026-09-04, **tapi tidak seperti yang direncanakan.** erp-frontend [#1452](https://github.com/bip-itteam-internal/erp-frontend/pull/1452).
      Tiga lembar per posisi **dibatalkan**: `/portal/kpi` sudah melayani ketiga posisi lewat kaskade persona, dengan komponen yang lebih matang. Rinciannya di [[IT - Dashboard per Posisi]] § Kenapa lembar per posisi dibatalkan.
      Yang dibangun: blok **Uptime Bulan Penilaian** (endpoint `/uptime?periode=` yang sebelumnya nol konsumen) dan **tautan kartu KPI ke `/portal/kpi`**.
      ⚠️ **Pelajaran yang mengubah item 2.2 sampai 2.4 di bawah**: sebelum merancang lembar mana pun, periksa dulu apakah `/portal/kpi` sudah menjawabnya untuk posisi itu. Untuk posisi yang **bukan penilai**, kemungkinan besar sudah. Yang layak dibangun adalah yang TIDAK ada di scorecard KPI: angka operasional, antrean pekerjaan, dan ambang yang perlu ditindak.
      **Tersisa**: verifikasi manual di layar (blok uptime wajib menampilkan pesan bersebab saat monitoring 503 di dev), dan dua item review yang belum diputuskan (pesan khusus untuk 502/504, dan tautan kartu uptime ke `/it/status-infrastruktur`).

- [ ] **2.2 Manufaktur sisi gudang** · Warehouse Staff, Warehouse Leader, Admin Warehouse (2 lokasi)
      17 dari 24 metrik bersumber. Rancangan: [[Manufacture - Dashboard per Posisi]].
      ⚠️ Periksa dulu **dua metrik over-dispensing kembar** di Warehouse Leader: bila entri ganda, 0,3 nilai orangnya ditentukan satu pengukuran yang dihitung dua kali.

- [ ] **2.3 Finance AR** · AR Leader + 3 lembar AR Staff
      Layarnya sudah ada di `/finance`, tinggal diisi mengikuti ADR 0076. Rancangan: [[Finance - Dashboard per Posisi (FAT)]].

- [ ] **2.4 Sales, ICC dan Supervisor** · menunggu 1.2 tuntas
      Datanya paling tebal di perusahaan; yang kurang cuma atribusinya.

---

## Gelombang 3 — pemakaian modul yang sudah ada, nol kode

Koleksinya sudah ada di kode. Yang tidak ada isinya. **Ini permintaan ke tim yang memakai, bukan tiket developer.**

- [ ] **3.1 Isi Batch Record & Production Log** · membuka **16 metrik di 8 posisi**, Manufaktur + Quality · *tim produksi*
      Membuka sisi produksi Manufaktur dan hampir seluruh divisi Quality sekaligus. Daya ungkit tertinggi di seluruh papan ini.
      `batch_record` bahkan sudah punya `TglSelesaiOlah`, `DiajukanAt`, `DisetujuiAt`, persis tiga stempel waktu yang dibutuhkan.

- [ ] **3.2 Isi modul Training** · membuka **8 metrik di 3 posisi** HR · *tim people development*
      Mengunci bobot 0,9 di Training & Performance Officer, 0,4 di Culture & Industrial, 0,15 di HRD Supervisor.

- [ ] **3.3 Isi master anggaran per departemen** · 9 metrik, 8 posisi, 3 divisi · *finance*
      Dibutuhkan GA, Finance, dan IT untuk metrik varians dan efisiensi biaya masing-masing.
      ⚠️ Untuk IT ada syarat kedua: `/accounting/anggaran/varians` dipanggil **tanpa parameter departemen**, jadi mengisi master saja belum cukup.

---

## Gelombang 4 — bangun modul

- [ ] **4.1 Modul checklist berjadwal** · 14 metrik, 8 posisi, 3 divisi · [[GA - Checklist Management]]
      Satu-satunya yang membuat **Office Boy dan Security** layak punya layar sama sekali.

- [ ] **4.2 Tracker pajak / audit internal / CAPA / BPOM** · 13 metrik, 10 posisi, 5 divisi
      Sebagian sudah bergerak lewat pemisahan modul Audit Internal ([[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]]).

- [ ] **4.3 Tracker garapan desain & video** · 10 metrik, 3 posisi, 2 divisi
      Melayani Graphic Design dan Video Editor Kesekretariatan **plus** Video Editor Beauty Hacks sekaligus.
      ⚠️ Yang diukur mutu dan ketepatan garapan, **bukan** performa video di marketplace. Jangan ditambal dengan `tt_shop_video_performances`.

- [ ] **4.4 Fitur log 1-on-1** · 9 metrik, 7 posisi, 2 divisi
      Fitur kecil, jangkauan lebar: tujuh posisi Finance plus Warehouse Leader.

---

## Gelombang 5 — integrasi baru

- [ ] **5.1 Integrasi Meta Ads** · 7 metrik · membuka posisi Meta Advertiser di kedua brand
- [ ] **5.2 Modul demand planning / forecast** · 7 metrik, 7 posisi, 5 divisi
- [ ] **5.3 Data percakapan CS** · 3 metrik

---

## Sengaja TIDAK dikerjakan

- ⛔ **Kaizen, 19 metrik di 15 posisi lintas 8 divisi.** Manual **karena keputusan** ([[ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI]]), bukan karena sistemnya kurang. **Jangan digambar sebagai panel menunggu**: panel jujur yang terbukti berbohong di satu tempat membuat panel jujur di tempat lain ikut tak dipercaya.
  ⚠️ Beberapa metrik bernama `Kaizen` justru **bukan** Kaizen (review SOP di QA Leader, CAPA dan kualitas produk di Leader Production, `Inovation & Improvement` di QA RND). Ketiganya butuh sumber sendiri dan masuk item 1.3.
- ⛔ **Integrasi akun buzzer, 10 metrik.** Akun personal tanpa API. Menuntut keputusan tentang cara kerja buzzer lebih dulu, bukan endpoint baru.

## Utang yang dicatat, bukan penghambat

`position_key` belum mengalir ke frontend, sehingga pencocokan posisi masih memakai **nama** (`useAuth().position`). Ini utang [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]], **bukan gerbang**: 17 lembar HRGA dan FAT sudah berjalan begitu hari ini, dan seluruh gelombang 2 boleh memakai cara yang sama.

Konsekuensi yang diterima sadar: rename nama posisi di master data memutus pencocokannya secara senyap. Selama utang ini hidup, perubahan nama posisi wajib diperlakukan sebagai perubahan yang menyentuh frontend.

## Dokumen Terkait

- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]
- [[REF - Dashboard per Posisi (Indeks Cakupan)]]
- [[REF - Layout Dashboard erp-frontend]]
- [[HRIS - Matriks KPI per Departemen]]
- [[RUN - Menambah Metrik KPI Otomatis]]
