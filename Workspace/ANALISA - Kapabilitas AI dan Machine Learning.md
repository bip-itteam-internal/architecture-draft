> Papan kerja hasil `/analisa-kebutuhan` 2026-08-28. Keputusannya di [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]], cara kerjanya di [[CORE - Kapabilitas AI dan Machine Learning]]. Berkas ini berubah tiap item selesai; keduanya di atas tidak.

# Daftar Task

Empat task pertama adalah **gerbang**. Ketiganya murah, tidak menyentuh kode produksi, dan hasilnya menentukan apakah task 5 dan seterusnya layak dikerjakan sama sekali. Mengerjakan task 5 sebelum gerbangnya lulus berarti membangun di atas angka yang belum tentu berarti seperti yang kita kira.

---

## Gerbang

### T1. Konfirmasi arti pendapatan nol pada tingkat video

**Blocking untuk T5.** Rp 1,15 miliar belanja pada video-hari berpendapatan nol adalah dasar seluruh kapabilitas pertama. Pendapatan tingkat video berasal dari laporan marketplace, bukan atribusi pesanan kita sendiri, karena nol dari 433.641 pesanan menyimpan penanda campaign, ad, maupun video. Perlu dipastikan ke pemilik jalur atribusi apakah nol berarti benar-benar tidak ada penjualan, atau penjualannya tercatat di tempat lain.

Keluaran: satu kalimat putusan yang masuk ke [[CORE - Kapabilitas AI dan Machine Learning]], plus penyesuaian angka bila ternyata perlu.

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

## Pelaksanaan

### T5. Lapisan peringatan dini belanja iklan video

Daftar berurutan berisi video yang belanjanya berjalan tanpa penjualan, ditujukan ke penanggung jawab tokonya, dengan tautan ke tempat tindakannya diambil. Tanpa pemotongan anggaran otomatis.

Bentuk pekerjaannya ditentukan hasil T4: aturan sederhana bila pembandingnya sudah cukup, model bila terbukti mengalahkannya.

Dependensi: **T1, T2, T4 lulus**.

### T6. Verifikasi kunci RBAC penggerbang

Kunci RBAC yang menggerbangi daftar peringatan masih TBD di dok domain. Perlu ditelusuri ke kode marketing-analytics, termasuk cara gerbang penanggung jawab toko yang sudah ada bekerja. Kepemilikan toko dibaca dari pemetaan ICC yang sudah ada, bukan ditebak dari nama toko, dan bentuknya daftar karena satu toko dapat dipegang lebih dari satu orang.

Perlu juga memutuskan tampilan untuk toko yang belum termapping, karena cakupannya tidak pernah penuh dan keadaan itu tidak boleh didiamkan.

Dependensi: dikerjakan bersama T5, hasilnya menutup TBD di dok domain.

### T7. Putuskan jalur pemberitahuan

Lewat inbox atau cukup tampil di layar. Bila lewat inbox, kategori barunya hidup di daftar-izin `shared-library`, sehingga **marketing-analytics dan notification-service wajib naik bersama** dan satu notifikasi sungguhan dipicu sebagai bukti. Kategori yang absen maupun yang salah gagal senyap: fiturnya tampak berjalan penuh, notifikasinya tidak pernah tiba.

Dependensi: T5 sudah berbentuk.

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
