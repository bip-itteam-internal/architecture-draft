> Papan kerja hasil `/analisa-kebutuhan` 2026-08-28. Keputusannya di [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]], cara kerjanya di [[CORE - Kapabilitas AI dan Machine Learning]]. Berkas ini berubah tiap item selesai; keduanya di atas tidak.

# Daftar Task

Empat task pertama adalah **gerbang**. Ketiganya murah, tidak menyentuh kode produksi, dan hasilnya menentukan apakah task 5 dan seterusnya layak dikerjakan sama sekali. Mengerjakan task 5 sebelum gerbangnya lulus berarti membangun di atas angka yang belum tentu berarti seperti yang kita kira.

---

## Gerbang

### T1. Konfirmasi arti pendapatan nol pada tingkat video

**Blocking untuk T5.** Rp 1,15 miliar belanja pada video-hari berpendapatan nol adalah dasar seluruh kapabilitas pertama. Pendapatan tingkat video berasal dari laporan marketplace, bukan atribusi pesanan kita sendiri, karena nol dari 433.641 pesanan menyimpan penanda campaign, ad, maupun video. Perlu dipastikan ke pemilik jalur atribusi apakah nol berarti benar-benar tidak ada penjualan, atau penjualannya tercatat di tempat lain.

⛔ **Bobot task ini naik setelah temuan 2026-08-28.** Job `sync-video-performance` mencatat sendiri *"14487 video ber-spend tanpa baris organik (metrik nol = tak ada data)"*. Jadi nol pada kolom itu memuat dua makna yang tak dapat dibedakan dari kolomnya saja. Task ini karena itu bukan formalitas: ia dapat memangkas angka Rp 1,15 miliar secara berarti, dan angkanya sudah terlanjur dibawa ke manajemen sebagai batas atas.

Keluaran: satu kalimat putusan yang masuk ke [[CORE - Kapabilitas AI dan Machine Learning]], plus pemisahan "tidak ada penjualan" dari "tidak ada data" beserta angka masing-masing.

Dependensi: tidak ada.

### T2. Pastikan penurunan Maret 2026

**Blocking untuk T5 dan T8.** Pesanan Maret 2026 tercatat 17.764, jauh di bawah Februari 31.786 dan April 47.608. Perlu dipastikan kenyataan bisnis atau lubang sinkronisasi. Bila lubang data, seluruh model tersandung di titik yang sama dan Maret wajib dikecualikan.

Keluaran: putusan tertulis, dan bila lubang, catatan di dok domain tentang rentang yang tidak boleh dipakai.

Dependensi: tidak ada.

### T3. Buka isi `accurate_daily_returns`

7.779 baris, belum pernah dibuka. Berpotensi menjadi sumber label retur yang jauh lebih baik daripada 412 yang ditemukan di `transaction_orders`. Bila ternyata memadai, kandidat retur yang ditolak ADR 0058 §7 wajib ditinjau ulang lewat ADR baru, bukan lewat pengecualian diam-diam.

Keluaran: jumlah label yang benar-benar tersedia beserta rentang tanggalnya.

Dependensi: tidak ada. Boleh paralel dengan T1 dan T2.

### T4. Ukur pembanding aturan sederhana

**Blocking untuk T5**, dan ini gerbang yang paling menentukan. Dari video yang pada hari pertama belanjanya di atas ambang tertentu dan konversinya nol, berapa persen yang tetap nol sampai hari ketujuh. Ambangnya dipasang dari sebaran nyata, bukan ditulis tangan.

Bila angkanya tinggi, aturan sederhana sudah memberi sebagian besar manfaatnya dan T5 mengecil drastis menjadi sekadar menampilkannya. Bila rendah, barulah model punya alasan untuk ada.

Keluaran: angka persistensi, sebaran ambang, dan rekomendasi aturan versus model.

Dependensi: tidak ada.

---

## Prasyarat pipeline

Ditemukan 2026-08-28 saat mengaudit kelengkapan rancangan. Bukan gerbang untuk memulai, tetapi mengikat apa yang boleh dijanjikan dan harus beres sebelum fiturnya dinyatakan siap.

### T4b. Pulihkan job sync yang gagal berhari-hari

`sync-shop-performance` terakhir sukses **2026-08-20**, `sync-live-sessions` **2026-08-19**. Sebabnya sebagian toko dinonaktifkan (`code=36009006`) dan sebagian kredensialnya kedaluwarsa (`code=105002`), 11 dan 13 toko. Kegagalannya tidak berbunyi di layar mana pun.

Fitur peringatan yang dibangun di atas pipeline ini akan mewarisi kebutaannya: daftarnya tetap terisi dan tampak wajar sambil diam-diam tidak mencakup toko yang datanya tidak masuk.

Keluaran: job kembali hijau, atau keputusan sadar bahwa toko tertentu memang tidak lagi disinkronkan beserta cara menampilkannya.

Dependensi: tidak ada. Boleh paralel dengan gerbang.

### T4c. Putuskan kesegaran yang dibutuhkan versus interval 48 jam

`intervalPenjadwalBawaan = 48 * time.Hour` adalah konstanta di `penjadwal.go` dan tidak dapat diubah lewat env. Artinya peringatan tidak dapat harian, apalagi per jam.

Perlu diputuskan: menerima dua harian, atau mempercepat interval dengan ongkos kuota API yang harus dinilai lebih dulu. Jangan mengubah intervalnya diam-diam, karena jendela resync wajib tetap lebih lebar dari interval dan ada validasi yang menolak bila tidak.

Keluaran: putusan tertulis di dok domain, dan koreksi janji kecepatan di materi manajemen bila perlu.

Dependensi: tidak ada.

---

## Pelaksanaan

### T5. Lapisan peringatan dini belanja iklan video

Daftar berurutan berisi video yang belanjanya berjalan tanpa penjualan, ditujukan ke penanggung jawab tokonya, dengan tautan ke tempat tindakannya diambil. Tanpa pemotongan anggaran otomatis.

Bentuk pekerjaannya ditentukan hasil T4: aturan sederhana bila pembandingnya sudah cukup, model bila terbukti mengalahkannya.

Empat hal yang wajib diputuskan di dalam task ini, dan tidak satu pun sudah terjawab:

- **Bentuk penyimpanan dan kontrak API.** Dihitung saat dibaca atau disimpan sebagai koleksi sendiri, dan endpoint apa yang menyajikannya.
- **Batas hari WIB.** Definisi operasional "video-hari" harus dipatok eksplisit. Mart ini memakai konvensi hari WIB, dan mencampuradukkan tanggal dengan instant sudah pernah menggigit di modul yang sama.
- **Aturan berhenti memberi peringatan.** Video yang sama akan memenuhi syarat lagi pada siklus berikutnya. Perlu status sudah-ditindak, atau batas berapa kali sebuah video diperingatkan, kalau tidak daftarnya berubah jadi kebisingan yang diabaikan orang.
- **Tampilan untuk sumber basi.** Bila job sync-nya gagal (lihat T4b), layar wajib mengatakannya, bukan menampilkan daftar yang terlihat normal.
- **Perlakuan terhadap belanja `gmv_max`.** Belanja per video punya tiga sumber dengan kekuatan bukti berbeda: `vsa` aktual per iklan, `gmv_max` estimasi prorata per campaign. Menandai video boros atas dasar angka prorata berarti menuduh video tertentu atas taksiran tingkat campaign, dan salahnya berbentuk paling sulit disadari, yaitu iklan yang sebenarnya bekerja ikut ditutup.

Dependensi: **T1, T2, T4 lulus**. T4b sebaiknya sudah beres, kalau tidak hasilnya tidak dapat dipercaya.

### T6. Verifikasi kunci RBAC penggerbang

Kunci RBAC yang menggerbangi daftar peringatan masih TBD di dok domain. Perlu ditelusuri ke kode marketing-analytics, termasuk cara gerbang penanggung jawab toko yang sudah ada bekerja. Kepemilikan toko dibaca dari pemetaan ICC yang sudah ada, bukan ditebak dari nama toko, dan bentuknya daftar karena satu toko dapat dipegang lebih dari satu orang.

Perlu juga memutuskan tampilan untuk toko yang belum termapping, karena cakupannya tidak pernah penuh dan keadaan itu tidak boleh didiamkan.

Dependensi: dikerjakan bersama T5, hasilnya menutup TBD di dok domain.

### T7. Putuskan jalur pemberitahuan

Lewat inbox atau cukup tampil di layar. Bila lewat inbox, kategori barunya hidup di daftar-izin `shared-library`, sehingga **marketing-analytics dan notification-service wajib naik bersama** dan satu notifikasi sungguhan dipicu sebagai bukti. Kategori yang absen maupun yang salah gagal senyap: fiturnya tampak berjalan penuh, notifikasinya tidak pernah tiba.

Dependensi: T5 sudah berbentuk.

### T7b. Sisi frontend dan i18n

Belum disinggung sama sekali di rancangan, padahal fiturnya user-facing. Perlu diputuskan halaman mana yang menampungnya dan komponen apa yang dipakai.

⛔ **Seluruh teks baru yang tampil ke pengguna wajib lewat `react-i18next`**, dengan key ditaruh di **dua** berkas locale `id` dan `en` sekaligus. Berkas locale itu yang paling sering disunting paralel, jadi merge lokal plus `pnpm tsc` dan `pnpm build` wajib sebelum merge; auto-merge git pernah menelan kurung tutup sehingga seluruh build mati.

Halaman daftar mengikuti struktur tabel HRIS, bukan merakit tabel dan filter sendiri.

Dependensi: T5 sudah punya kontrak API.

---

## Bersyarat

### T8b. Putuskan runtime bila model terlatih ternyata diperlukan

**Hanya dikerjakan bila T4 menyimpulkan aturan sederhana kalah.** ADR 0058 §2 menetapkan model menumpang service pemilik data, dan itu memadai untuk aturan statistik di Go. Untuk model terlatih belum terjawab: marketing-analytics berbahasa Go dan tidak ada service Python di bip-erp.

Menjawabnya sekarang berarti menebak, karena kemungkinan besar T4 membuat task ini tidak pernah perlu dikerjakan.

Dependensi: **T4 menyimpulkan model diperlukan.**

---

## Kandidat kedua

### T8. Ramalan permintaan per SKU untuk perencanaan produksi

Menyentuh HPP sekitar Rp 882 juta per bulan. Katalognya 86 master SKU dengan 34 yang punya riwayat memadai, sehingga model statistik per SKU realistis dan mudah diperiksa manusia.

**Tidak dikerjakan paralel dengan T5.** Menjalankan dua kapabilitas prediktif sekaligus di atas riwayat delapan bulan berarti dua-duanya dikerjakan setengah matang.

Dependensi: T2 lulus, dan T5 sudah berjalan di produksi.

---

## Catatan

- Seluruh angka di papan ini berasal dari pengukuran produksi 2026-08-28. Ringkasannya untuk manajemen terbit sebagai halaman terpisah di luar vault.
- Task yang menyentuh uang, sanksi, jatah, atau ambang disiplin wajib membuka `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` lebih dulu. Tidak ada task di papan ini yang menyentuhnya, tetapi aturannya dicatat supaya tidak terlewat bila lingkupnya melebar.
- Tiap task dilempar ke `/start-task` satu per satu, bukan sekaligus.
