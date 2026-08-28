## Deskripsi

*Peta seluruh kapabilitas AI di ERP Bharata dalam satu tempat, beserta gerbang yang menentukan kapan pekerjaan AI baru boleh dimulai, dan rancangan kapabilitas prediktif pertama. Dibuat karena AI sudah berjalan di empat tempat yang tidak saling menaut, sehingga tidak ada yang dapat menjawab apa yang kita punya dan mana yang benar-benar hidup.*

- **Status**: ⚠️ **Sebagian Implemented** — dua kapabilitas generatif hidup di produksi, satu WIP, dua masih konsep tanpa kode. Kapabilitas prediktif belum berkode sama sekali.
- **Keputusan yang mengikat**: [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]]
- **Implementasi prediktif (rencana)**: [[Microservices - Marketing Analytics Service]]

## Latar Belakang

AI di ERP Bharata tumbuh dari kesempatan, bukan dari rencana. Video iklan lewat Veo muncul karena kebutuhan konten, analisis sentimen muncul karena kebutuhan riset produk, dan OCR muncul sebagai gagasan lintas modul. Tiga-tiganya berdiri sendiri, di tiga folder berbeda, dan tidak satu pun menaut ke yang lain.

Selama pertanyaannya "bagaimana fitur ini bekerja", keadaan itu tidak menyusahkan. Ia mulai menyusahkan begitu pertanyaannya berubah menjadi "AI apa yang kita punya" dan "boleh tidak kita bangun yang ini", karena tidak ada satu pun tempat yang menjawabnya. Dokumen ini tempat itu.

## Peta Kapabilitas

Dua sifat yang sangat berbeda hidup berdampingan di sini, dan membedakannya penting: kapabilitas **generatif** membuat sesuatu yang baru (video, ringkasan, jawaban), sedangkan kapabilitas **prediktif** menaksir sesuatu yang belum terjadi dari data yang sudah ada. Gerbang kelayakan data pada ADR 0058 mengikat keras yang prediktif, karena hanya yang prediktif menuntut label historis.

| Kapabilitas | Sifat | Engine | Status | Dokumen |
|---|---|---|---|---|
| Video iklan dari foto produk | Generatif | Veo 3.1 / Gemini | ✅ matang | [[APP - Ideamills]] · [[Sales - Veo (Gemini) Implementation]] |
| Otomasi tren ke video siap kirim | Generatif | LangGraph, human-in-the-loop | ⚠️ WIP | [[Sales - Veo (Gemini) Automation Layer]] |
| Analisis sentimen komentar TikTok | Generatif | Claude | ✅ jalan tiap awal pekan | [[APP - Tiktok Insight Analyzer]] · [[Sales - TikTok Sentiment Pipeline]] |
| OCR dan document intelligence | Generatif | rencana OCR + RAG lokal | 🟡 konsep, **0 kode** | [[CORE - OCR Document Service]] |
| Peringatan dini belanja iklan | **Prediktif** | belum ditentukan | 🟡 konsep, **0 kode** | dokumen ini |

Akses Claude ke vault lewat [[Microservices - Vault MCP Service]] sengaja **tidak** dimasukkan sebagai kapabilitas AI produk. Ia jalur baca dokumentasi untuk manusia, bukan fitur yang dipakai pengguna ERP.

Klaim "0 kode" pada dua baris di atas diverifikasi dengan `git grep` berbatas kata memakai kontrol positif dan negatif, bukan dengan pencarian teks biasa. Rincian dan alasannya di [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]].

## Ruang Lingkup / Cakupan (business view)

- **Menjadi satu-satunya tempat** yang menjawab AI apa saja yang ada, mana yang hidup, dan apa sifatnya.
- **Menjaga gerbang kelayakan data** tetap dapat dibaca oleh siapa pun yang mengusulkan pekerjaan AI baru.
- **Menyimpan rancangan kapabilitas prediktif**, karena belum ada dok domain yang memilikinya.
- **Di luar lingkup**: cara kerja rinci tiap kapabilitas generatif. Itu tetap milik dokumennya masing-masing, dan menyalinnya ke sini akan melahirkan sumber kebenaran kedua yang menyimpang diam-diam.

## Kapabilitas Prediktif Pertama: Peringatan Dini Belanja Iklan Video

### Masalah yang dipecahkan

Belanja iklan setara 61% laba kotor, sementara siklus koreksinya bulanan karena pagu belanja disimpan per bulan. Salah alokasi karena itu baru terlihat setelah bulannya lewat, dan belanjanya tidak dapat ditarik kembali. Pada tingkat video, Rp 1,15 miliar dari Rp 5,42 miliar belanja yang dapat ditelusuri jatuh pada video-hari yang pendapatannya nol.

Yang dibutuhkan bukan ramalan yang lebih tepat, melainkan **jarak yang lebih pendek antara uang keluar dan orang yang berwenang menghentikannya**.

### Bentuk keluarannya

Daftar berurutan berisi video yang belanjanya berjalan tanpa penjualan, ditujukan ke penanggung jawab tokonya, dengan tautan langsung ke tempat tindakannya diambil. **Bukan** pemotongan anggaran otomatis, sesuai ADR 0058 §5.

### Urutan kerja yang mengikat

Aturan sederhana diukur lebih dulu sebagai pembanding: dari video yang pada hari pertama belanjanya di atas ambang tertentu dan konversinya nol, berapa persen yang tetap nol sampai hari ketujuh. Bila angkanya tinggi, aturan sederhana sudah memberi sebagian besar manfaatnya dan model hanya menajamkan. Model dibangun hanya bila terbukti mengalahkan pembanding itu pada data yang sama.

### Aturan pemakaian kolom, dan ini bagian yang paling mudah salah

Kolom di bawah pernah, atau berpotensi, dijumlahkan secara keliru sehingga menghasilkan angka yang salah namun masuk akal. Kegagalannya bukan galat dan tidak ada test yang menangkapnya. Aturan ini sebelumnya hanya hidup sebagai komentar Go, sehingga siapa pun yang merancang layar dari dokumentasi tidak punya cara mengetahuinya.

| Kolom | Sifat | Aturan |
|---|---|---|
| `ads_cost` | Komponen sejajar | **Sudah** dikurangkan seluruhnya dari `gross_profit`. Jangan dikurangkan lagi. |
| `iklan_sia_sia` | **Himpunan bagian** dari `ads_cost` | Porsi belanja yang sudah terbayar dan ternyata sia-sia, **bukan** uang baru yang hilang. Jangan dijumlahkan ke laba, jangan dijumlahkan dengan beban packing (itu uang fisik tambahan, ini bukan), dan **jangan di-rename** menjadi kerugian iklan. Namanya adalah pengamannya. |
| `revenue` tingkat video | Bukan hasil atribusi sendiri | Berasal dari laporan marketplace, karena nol dari 433.641 pesanan menyimpan penanda campaign, ad, maupun video. **Pendapatan nol tidak sama dengan pemborosan terbukti**; bisa berarti penjualannya tercatat di tempat lain. |
| `retur` | Komponen sejajar | `ads_cost` tidak pernah dialokasikan ulang saat retur terjadi, jadi ia sudah menanggung retur sejak awal. |
| `gross_profit` | Hasil | Sudah bersih dari HPP, fee marketplace, dan seluruh `ads_cost`. |

Konsekuensi langsungnya untuk kapabilitas ini: angka Rp 1,15 miliar adalah **ukuran ruang keputusan**, bukan kerugian yang sudah pasti, dan wajib dikonfirmasi ke pemilik jalur atribusi sebelum dipakai memindahkan anggaran.

### Apa yang tidak dijanjikan

Tidak ada ramalan lintas musim. Riwayat pesanan yang efektif hanya Januari sampai Agustus 2026 dan baru padat sejak Mei, sehingga tidak ada satu pun siklus tahunan yang pernah terlihat data ini.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| ICC pemegang toko | Tim ICC, Marketing | Digerbang penanggung jawab toko; kunci RBAC persisnya **TBD**, belum diverifikasi ke kode | Web ERP |
| Atasan marketing | Supervisor Marketing | Lingkup divisi atau tim | Web ERP |

- **Tujuan**: menghentikan belanja yang tidak menghasilkan selagi belanjanya masih berjalan.
- **Pain point**: salah alokasi baru terlihat setelah bulannya lewat, dan uangnya tidak dapat ditarik kembali.
- **Aksi utama**: membuka daftar peringatan, memeriksa videonya, lalu menurunkan atau menghentikan anggarannya sendiri.

Kepemilikan toko dibaca dari pemetaan ICC yang sudah ada, bukan ditebak dari nama toko. Dua kenyataan yang membentuknya: **satu toko dapat dipegang lebih dari satu orang** (terukur di produksi 2026-07-31), dan **cakupannya tidak pernah penuh** (terukur 1 sampai 12 Agustus 2026, 37 dari 38 toko punya penanggung jawab). Keadaan belum termapping karena itu wajib punya tampilannya sendiri yang tidak dapat disalahbaca, bukan didiamkan.

## Konsumen Data

- [[Microservices - Marketing Analytics Service]] — pemilik mart yang dibaca, dan tempat kapabilitas prediktif akan tinggal
- [[API - Marketing Analytics Service]] — endpoint yang akan bertambah bila rancangannya matang
- [[Sales - Profit Engine (Design)]] — sumber definisi laba yang dipakai sebagai dasar perhitungan

## Kendala

- **Riwayat data pendek.** Delapan bulan, padat sejak Mei 2026, tanpa siklus tahunan.
- **Katalog kecil.** 86 master SKU, 34 di antaranya punya riwayat memadai. Menguntungkan untuk model statistik per SKU, sekaligus menutup pintu bagi pendekatan yang menuntut data besar.
- **Atribusi tingkat video bukan milik kita.** Bergantung laporan marketplace, sehingga perubahan cara marketplace melaporkannya berpindah langsung ke keluaran model tanpa perantara.
- **Menumpang service yang sudah ada berarti ikut memikul jadwal deploy-nya**, dan cakupan test harus menjaga dua hal sekaligus.

## Belum Diputuskan (TBD)

- **Kunci RBAC** yang menggerbangi daftar peringatan. Belum diverifikasi ke kode.
- **Jalur pemberitahuan**: lewat inbox atau cukup tampil di layar. Bila lewat inbox, kategori barunya menuntut marketing-analytics dan notification-service naik bersama, dan kategori yang salah gagal senyap.
- **Frekuensi**: harian diasumsikan, per jam belum dinilai.
- **Ambang belanja hari pertama** yang memicu peringatan. Wajib dipasang dari sebaran nyata, tidak boleh ditulis tangan.
- **Isi `accurate_daily_returns`** (7.779 baris) belum dibuka, dan dapat mengubah putusan pada kandidat retur.
- **Penurunan tajam Maret 2026** belum dipastikan kenyataan bisnis atau lubang sinkronisasi. Bila lubang data, setiap model akan tersandung di titik yang sama.

## Dokumen Terkait

- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]]
- [[Microservices - Marketing Analytics Service]]
- [[APP - Ideamills]]
- [[APP - Tiktok Insight Analyzer]]
- [[CORE - OCR Document Service]]
- [[Sales - Marketing Analytics (Audit Ketersediaan Data)]]
- [[ADR - 0008 Profit Engine Join via item_group_id]]
