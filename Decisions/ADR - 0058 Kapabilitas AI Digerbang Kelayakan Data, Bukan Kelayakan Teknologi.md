## Untuk Manajemen

- **Yang berubah di layar**: belum ada, sekarang juga. Keputusan ini menetapkan gerbang dan urutannya. Yang direncanakan sesudahnya: satu daftar peringatan dini yang menandai iklan video yang belanjanya berjalan tanpa menghasilkan penjualan, beserta pemberitahuan ke penanggung jawab tokonya.
- **Siapa terdampak**: tim ICC pemegang toko dan atasan marketing. Tidak menyentuh HR, keuangan, maupun karyawan umum.
- **Tidak dijanjikan**: tidak ada ramalan setahun ke depan (riwayat data baru delapan bulan), tidak ada pengurangan retur, tidak ada prediksi karyawan mengundurkan diri maupun penilaian pelamar, dan sistem tidak memotong anggaran sendiri.
- **Besaran kerja**: satu pengukuran murah lebih dulu untuk menguji apakah aturan sederhana sudah cukup, baru dinilai apakah model perlu dibangun sama sekali.

## Deskripsi

*Kelayakan pekerjaan AI di bip-erp ditentukan oleh kelayakan DATA-nya, bukan oleh ketersediaan teknologinya. Tiga syarat dijadikan gerbang, model menumpang service yang sudah memegang datanya alih-alih berdiri sebagai service AI terpisah, dan kapabilitas prediktif pertama diarahkan ke belanja iklan karena di situ syaratnya terpenuhi sekaligus uangnya terbesar.*

- **Status**: 🟡 **Diusulkan**, 2026-08-28, kode belum ada. Berdiri di atas pengukuran langsung database produksi pada 2026-08-28.
- **Path di repo**: `bip-erp/services/marketing-analytics/` (baru, lapisan peringatan dini). Tidak ada service baru dan tidak ada perubahan gateway.
- **Tanggal**: 2026-08-28

## Context

### AI sudah dikerjakan di empat tempat, tanpa satu pun keputusan yang mengaturnya

Vault ini memuat 57 ADR sebelum keputusan ini, dan **tidak satu pun mengatur kapan AI layak dipakai**. [[ADR - 0028 Code Index bip-erp]] menyinggung LLM hanya untuk menyatakan bahwa Code Index sengaja TIDAK memakainya.

Sementara itu kapabilitas AI sudah berjalan di empat tempat yang tidak saling menaut sebagai satu kapabilitas: [[APP - Ideamills]] dan [[Sales - Veo (Gemini) Implementation]] (video iklan lewat Veo/Gemini, matang), [[Sales - Veo (Gemini) Automation Layer]] (LangGraph dengan human-in-the-loop, WIP), [[APP - Tiktok Insight Analyzer]] dan [[Sales - TikTok Sentiment Pipeline]] (analisis sentimen lewat Claude, berjalan tiap awal pekan), serta [[CORE - OCR Document Service]] (OCR dan RAG, masih konsep).

Empat-empatnya lahir dari kesempatan, bukan dari saringan. Akibatnya usulan AI berikutnya tidak punya dasar untuk ditolak selain selera, dan itu berbahaya di modul yang menggerakkan uang.

### Peta kapabilitas dan gerbangnya sengaja dipisah

Keputusan ini menyimpan **kenapa dan aturannya**. Peta lengkap kelima kapabilitas beserta statusnya, aturan pemakaian kolomnya, dan rancangan kapabilitas prediktifnya tinggal di [[CORE - Kapabilitas AI dan Machine Learning]]. Pemisahan ini mengikuti pembagian yang sama dengan ADR lain di vault: ADR memegang keputusan, dok domain memegang cara kerjanya.

### Yang diukur, bukan diperkirakan

Seluruh angka di bawah diukur langsung dari database produksi pada 2026-08-28 lewat kueri baca. Rentang finansialnya 146 hari, 5 April sampai 28 Agustus 2026, diambil pada tingkat toko sehingga tidak ada penjumlahan ganda antar level.

| Pos | 146 hari |
|---|---|
| Pendapatan | Rp 40,44 miliar |
| Belanja iklan | Rp 7,14 miliar |
| Laba kotor | Rp 11,66 miliar |
| HPP | Rp 4,29 miliar |
| Fee marketplace | Rp 5,78 miliar |
| Retur | Rp 285 juta |

Belanja iklan setara **61% laba kotor**, sementara retur hanya 2,4%. Pada tingkat video, dari Rp 5,42 miliar belanja yang dapat ditelusuri per video per hari, **Rp 1,15 miliar jatuh pada 581.677 video-hari yang pendapatannya nol**.

### Ketersediaan label, yang ternyata menggugurkan sebagian besar kandidat

| Kandidat | Contoh tersedia | Riwayat |
|---|---|---|
| Iklan video tidak konversi | 581.677 negatif, ~71.204 positif | 146 hari |
| Permintaan per SKU | 86 SKU, 34 dengan riwayat memadai | 8 bulan |
| Pembatalan pesanan | 81.696, tetapi 39.520 diinisiasi sistem | 8 bulan |
| Keluhan produk dari ulasan | 342 ulasan bintang 3 ke bawah | 18 bulan |
| Retur | 412 | 8 bulan |
| Karyawan mengundurkan diri | 0 kejadian | 7 bulan, 208 orang |
| Penilaian pelamar | koleksi kosong | tidak ada |

Yang gugur, gugur karena kekurangan contoh untuk dipelajari, bukan karena kekurangan teknologi. Perbedaan ini menentukan sikap: menambah data akan mengubah putusannya, sedangkan mengganti algoritma tidak.

### Riwayat data jauh lebih pendek daripada yang terlihat

`transaction_orders` memuat tanggal sejak 2023, dan itu menyesatkan. Sebarannya: 2023 satu baris, 2024 tiga baris, 2025 sebanyak 2.352, dan **2026 sebanyak 487.932**. Riwayat efektifnya Januari sampai Agustus 2026, dan baru padat sejak Mei. Konsekuensinya keras: **tidak ada satu pun siklus tahunan yang pernah terlihat data ini**, sehingga model apa pun yang dijanjikan mengantisipasi Ramadan, Lebaran, atau Harbolnas sedang menebak.

### Pipeline yang menyuplainya menyegarkan diri tiap 48 jam, dan sebagian jobnya sedang gagal

Dua kenyataan yang membatasi apa yang boleh dijanjikan, keduanya terkonfirmasi di produksi 2026-08-28:

1. **Interval penjadwal 48 jam dan terkunci di kode**, bukan konfigurasi. Karena itu peringatan apa pun yang dibangun di atasnya tidak dapat datang harian, apalagi per jam. Yang dapat dijanjikan adalah dari bulanan menjadi paling cepat dua harian.
2. **Job `sync-shop-performance` terakhir sukses 2026-08-20 dan `sync-live-sessions` 2026-08-19**, karena sebagian toko dinonaktifkan dan sebagian kredensialnya kedaluwarsa. Kegagalannya tidak berbunyi di layar mana pun.

Keduanya tidak membatalkan keputusan ini, tetapi mengikat janji yang boleh dibuat atas namanya, dan itulah alasan keduanya dicatat di sini alih-alih ditemukan belakangan oleh orang yang mengimplementasikan.

### Nol pada metrik video bisa berarti tidak ada datanya

Job `sync-video-performance` mencatat sendiri pada 2026-08-28: *"14487 video ber-spend tanpa baris organik (metrik nol = tak ada data)"*. Jadi nol pada kolom itu memuat dua makna yang tidak dapat dibedakan dari kolomnya saja, yaitu tidak ada penjualan dan tidak ada datanya. Angka Rp 1,15 miliar di atas karena itu adalah batas atas, dan memisahkan kedua makna itu menjadi prasyarat, bukan penyempurnaan.

### Modul ini sudah pernah memindahkan uang atas dasar angka karangan

`services/marketing-analytics/kurva_alokasi.go` mencatat bahwa layar simulasi alokasi belanja pernah memakai kurva dengan parameter yang ditulis tangan agar grafiknya berbentuk bagus, lengkap dengan keterangan bahwa kurvanya dipasang dari 12 bulan realisasi, padahal tidak satu pun parameternya ada di data mana pun. Tombol optimalkan otomatis di sebelahnya memindahkan anggaran puluhan juta rupiah. Pola yang sama terjadi pada ambang 18% yang dibantah sebaran nyata 4,5% sampai 38,8%, dan ambang ROAS 3,2 yang beredar sebagai bawaan kode.

Berkas itu kini memasang seluruh parameternya dari titik data dan **menolak kanal yang datanya tidak cukup** dengan sebab yang dapat dibaca manusia. Perilaku itulah yang dijadikan standar oleh keputusan ini, bukan diperlakukan sebagai kasus khusus satu berkas.

### Klaim negatif yang menjadi dasar keputusan ini, dan cara memverifikasinya

Klaim "belum ada kodenya" tidak boleh berdiri di atas pencarian teks biasa, karena satu byte NUL membuat sebuah berkas hilang total dari ripgrep tanpa satu pun tanda. Diverifikasi dengan `git grep` berbatas kata, memakai kontrol positif (`fiber` cocok di 723 berkas, membuktikan pencariannya bekerja) dan kontrol negatif (kata karangan, 0 berkas):

- `ocr` sebagai kata utuh: **0 berkas**
- `rag`, `faiss`, `ollama`, `embedding`: **0 berkas**
- Direktori `services/ocr`, `services/ai`, `services/ml`: **tidak ada**

Jadi [[CORE - OCR Document Service]] berstatus 🟡 secara jujur, dan seluruh pekerjaan prediktif di bawah ini memang belum berkode.

## Decision

### 1. Tiga syarat menjadi gerbang, dan ketiganya wajib terpenuhi

Sebuah pekerjaan AI atau ML boleh dimulai hanya bila ketiganya terjawab dengan angka, bukan dengan perkiraan:

1. **Ada label historisnya.** Berapa banyak kejadian yang pernah tercatat, diukur di produksi. Kandidat dengan contoh sedikit ditolak, sebanyak apa pun minat terhadapnya.
2. **Riwayatnya cukup untuk pertanyaan yang diajukan.** Pertanyaan bermusim menuntut riwayat lintas musim. Riwayat delapan bulan tidak boleh dipakai menjawab pertanyaan tahunan.
3. **Ada keputusan yang benar-benar berubah, dan ada orang yang mengambilnya.** Bila tidak ada yang akan bertindak berbeda karena hasilnya, yang diminta adalah laporan hiasan, dan itu layak dikatakan terus terang.

Angka pengukurannya wajib dicantumkan di usulan. Usulan tanpa angka ditolak tanpa dibahas isinya.

### 2. Model menumpang service pemilik data, tidak ada service AI terpisah

Kapabilitas prediktif tinggal di service yang sudah memegang datanya, dalam kasus pertama [[Microservices - Marketing Analytics Service]]. Service AI terpisah ditolak karena memisahkan model dari data yang dibacanya, sehingga melahirkan jalur baca lintas service untuk data yang sudah ada di tangan, dan menambah satu container yang harus ikut naik tiap kali salah satunya berubah.

Ini **tidak** berlaku untuk kapabilitas AI generatif yang sudah berdiri di aplikasinya sendiri ([[APP - Ideamills]], [[APP - Tiktok Insight Analyzer]]). Keduanya memang bukan pembaca data ERP.

### 3. Aturan sederhana diuji lebih dulu, model hanya bila aturan kalah

Sebelum model apa pun dibangun, aturan statistik sederhana diukur sebagai pembanding. Model hanya dibangun bila terbukti mengalahkannya pada data yang sama. Pada riwayat sependek delapan bulan, pembanding sederhana sering menang, dan mengetahui itu lebih awal jauh lebih murah daripada mengetahuinya setelah model jadi.

### 4. Parameter dipasang dari data, dan menolak diri sendiri saat datanya kurang

Tidak ada ambang, bobot, atau koefisien yang boleh ditulis tangan lalu dipakai memindahkan uang. Bila datanya tidak cukup untuk memasang parameternya, keluarannya adalah penolakan dengan sebab yang dapat dibaca manusia, bukan angka bawaan. "Hanya satu dari empat kanal dapat dipasang" adalah hasil yang sah dan lebih berguna daripada empat angka karangan.

### 5. Sistem mengurutkan, orang memutuskan

Keluaran model adalah urutan perhatian, bukan tindakan. Pemotongan anggaran, penghentian iklan, dan keputusan produksi tetap dijalankan orang. Alasannya bukan kehati-hatian umum melainkan sifat datanya: riwayat delapan bulan tanpa siklus tahunan tidak layak diberi kewenangan mengeksekusi sendiri.

### 6. Kapabilitas prediktif pertama adalah peringatan dini belanja iklan video

Dipilih karena ketiga syarat gerbang terpenuhi sekaligus dan uangnya terbesar. Rancangan rincinya di [[CORE - Kapabilitas AI dan Machine Learning]].

Kandidat kedua, ramalan permintaan per SKU untuk perencanaan produksi, disiapkan sesudahnya dan tidak dikerjakan paralel.

### 7. Yang ditolak sekarang, beserta angkanya

Ditolak agar tidak diusulkan berulang tanpa data baru: **prediksi retur** (412 label), **prediksi karyawan mengundurkan diri** (0 kejadian tercatat, 208 orang, riwayat 7 bulan), **penilaian pelamar otomatis** (koleksi rekrutmen kosong, ditambah risiko bias yang tidak sebanding), dan **prediksi pembatalan pesanan** (ditunda, bukan ditolak permanen, karena 39.520 dari 81.696 pembatalan diinisiasi sistem dan dari 30.458 pembatalan sesudah barang dikirim sebanyak 30.374 juga sistem sementara pembeli hanya 49, sehingga artinya perlu dipastikan lebih dulu).

**Analisis keluhan produk dari ulasan** dikerjakan dengan LLM, bukan model yang dilatih, karena 342 contoh negatif terlalu sedikit untuk melatih apa pun sementara teksnya sudah tersedia dan pipeline sejenis sudah berjalan di [[Sales - TikTok Sentiment Pipeline]].

## Consequences

- **Usulan AI berikutnya punya dasar penolakan yang tidak bergantung selera.** Ini manfaat utamanya, dan berlaku sejak keputusan ini diterima, sebelum satu baris kode ditulis.
- **Sebagian besar kandidat yang biasa diminta menjadi tertutup**, dan itu disengaja. Bila datanya bertambah, putusannya ditinjau ulang lewat ADR baru, bukan lewat pengecualian diam-diam.
- **Pemberitahuan menuntut dua container naik bersama.** Bila peringatan dini dikirim lewat inbox, kategori inbox barunya hidup di daftar-izin `shared-library`, dan service yang tidak ikut di-rebuild memegang salinan lama. Gagalnya senyap: fiturnya tampak berjalan penuh, notifikasinya tidak pernah tiba. Marketing-analytics dan notification-service karena itu selalu dinaikkan bersama, lalu satu notifikasi sungguhan dipicu sebagai bukti.
- **Menumpang service yang ada berarti ikut memikul jadwal deploy-nya.** Perubahan pada marketing-analytics kini berpotensi menyentuh dua hal sekaligus, sehingga cakupan test harus menjaga keduanya.
- **Tidak ada perubahan kontrak API sampai rancangannya matang**, jadi belum ada urutan deploy backend sebelum frontend yang perlu diikuti pada tahap ini.
- **Janji kecepatannya terbatas pada dua harian**, mengikuti interval penjadwal yang terkunci di kode. Menjanjikan harian atau per jam atas nama keputusan ini adalah salah, dan mempercepatnya adalah keputusan tersendiri dengan ongkos kuota API yang belum dinilai.
- **Keputusan §2 menetapkan TEMPAT model, bukan runtime-nya.** Untuk aturan statistik, service pemilik data yang berbahasa Go sudah memadai. Bila gerbang T4 nanti menyimpulkan model terlatih memang diperlukan, runtime-nya belum terjawab karena tidak ada service Python di bip-erp, dan itu akan menuntut keputusan tambahan. Dicatat terbuka di sini alih-alih dijawab sekarang, karena menjawabnya sebelum tahu modelnya perlu atau tidak berarti menebak.
- **Keputusan ini berdiri di atas pengukuran satu titik waktu.** Dua lubang diketahui dan sengaja dicatat: isi `accurate_daily_returns` sebanyak 7.779 baris belum dibuka dan dapat mengubah putusan pada kandidat retur, dan penurunan tajam Maret 2026 belum dipastikan kenyataan bisnis atau lubang sinkronisasi. Keduanya masuk daftar kerja sebagai gerbang, bukan sebagai catatan kaki.

## Dokumen Terkait

- [[CORE - Kapabilitas AI dan Machine Learning]]
- [[Microservices - Marketing Analytics Service]]
- [[API - Marketing Analytics Service]]
- [[ADR - 0028 Code Index bip-erp]]
- [[Sales - Marketing Analytics (Audit Ketersediaan Data)]]
