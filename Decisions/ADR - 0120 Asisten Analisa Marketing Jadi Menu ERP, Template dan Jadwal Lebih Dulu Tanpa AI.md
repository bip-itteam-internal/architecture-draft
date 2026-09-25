# ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI

> **Status**: ⚠️ **Implemented (ada catatan)** — irisan 1 **hidup di PRODUKSI** sejak 2026-09-23, backend saja; layar FE belum ada. Irisan 2 dan 3 belum. Rinciannya di § Realisasi. **§5 dan §7 digantikan** [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]] (2026-09-25).

%% Status ditulis DI SINI, bukan sebagai bullet di ## Deskripsi seperti ADR lain, dan itu
bukan gaya bebas: `## Untuk Manajemen` mendorong bagian Deskripsi melewati baris ke-15, dan
di bawah baris itu status tak terbaca VAULT-INDEX.json sehingga dok muncul tanpa status di
/ask (rulebook vault §5). Terbukti: serap 2026-09-23 memperingatkan "status hilang" untuk
dok ini. Satu tempat saja — jangan tambahkan bullet Status di ## Deskripsi. %%

## Untuk Manajemen

**Apa yang berubah di layar.** Muncul satu menu baru di Marketing: daftar analisa siap pakai
yang bisa dipilih, dijadwalkan sendiri kapan dikirim dan ke siapa, tanpa meminta bantuan tim
IT tiap kali. Laporannya datang ke Inbox ERP dan MyBharata, membawa tautan langsung ke layar
yang menampilkan angkanya.

**Siapa yang terdampak.** Terukur 2026-09-22: 32 pemegang toko, 2 supervisor tim marketing,
2 leader iklan, dan 1 Direktur. Enam dari 32 pemegang toko menguasai 60% belanja iklan, jadi
laporan pertama diarahkan ke lingkaran kecil itu, bukan ke semua orang sekaligus.

**Apa yang TIDAK dijanjikan.** Sistem tidak memutuskan apa pun sendiri: ia mengurutkan dan
menyampaikan, orang yang menghentikan atau menaikkan belanja iklan. Tidak ada rekomendasi
anggaran, karena hubungan antara belanja iklan dan laba terlalu lemah untuk dijadikan dasar.
Tidak ada analisa untuk Harga & Diskon maupun Pelanggan & Cohort selama sumber datanya masih
kosong. Metrik iklan TikTok yang rinci juga tidak dijanjikan karena cakupan datanya di bawah
satu persen; untuk Shopee justru lengkap.

**Perkiraan besaran kerja.** Tiga irisan berurutan, dan tiap irisan berdiri sendiri sehingga
boleh dihentikan tanpa membuang yang sudah jadi. Irisan pertama, yang memberi nilai terbesar,
tidak melibatkan AI sama sekali.

## Deskripsi

*Analisa otomatis yang diminta manajemen sebagian besar sudah ada dan berbasis aturan; yang
kurang adalah pengantarannya. Keputusan ini menempatkan asisten analisa sebagai menu di dalam
ERP, bukan di harness luar, dan menunda lapisan AI sampai template dan penjadwalan tanpa AI
terbukti dipakai.*

- **Path di repo**: `bip-erp/services/marketing-analytics/` (`template_analisa*.go`, `jadwal_laporan*.go`, `jadwal_jatuh_tempo.go`, `penjalan_jadwal.go`, `hasil_analisa*.go`, `lingkup_hasil.go`), `bip-erp/shared-library/common/roles.go` (`RequireMarketingReportAdmin`), `bip-erp/shared-library/models/notification/models.go` (kategori `marketing-laporan-terjadwal`), `bip-erp/services/notification/webpush.go` (`aturanRuteWeb`); `erp-frontend/src/features/marketing-analytics/` **belum ada**
- **Tanggal**: 2026-09-22 (diputuskan) · 2026-09-23 (irisan 1 mendarat)

## Context

**Permintaan aslinya tidak menyebut AI.** Checklist manajemen nomor 133 berbunyi *"Semua
halaman Marketing punya analisa otomatis"*. Kata "AI" masuk belakangan lewat percakapan.
[[LOG - 2026-09-17 Audit Checklist Marketing dan Integration]] mencatat pertanyaan yang sudah
dikembalikan ke manajemen dan belum dijawab: apakah yang dimaksud berbasis aturan (sudah ada)
atau narasi AI (pekerjaan baru).

**Sebagian besar sudah ada.** Diukur ke `origin/main` 2026-09-22: **14 dari 18** halaman
analitik sudah punya blok "Perlu tindakan" berbasis aturan, lengkap dengan kalimat sebab dan
langkah. Yang belum: Harga & Diskon (halaman unggah harga minimal, sumbernya nol baris),
Pelanggan & Cohort (bloknya ada, sumbernya nol baris), dan tab Video selain GMV Max (belanja
0,26% dari total, isinya tumpang tindih dengan tab sebelah). Checklist menandainya
"Belum Mulai" karena kolomnya diisi dari melihat menu, bukan memeriksa kode.

**Datanya sehat.** Seluruh job sinkron berhasil 2026-09-22 pukul 03:03 WIB, dengan 1.024.260
baris laba yang terentang 5 April sampai hari itu. Mart disegarkan tiap 48 jam, dan intervalnya
terkunci di kode, bukan env.

**Yang benar-benar kurang adalah pengantaran.** Tidak ada satu pun jalur yang memberi tahu
orang bahwa ada sesuatu yang perlu ditindak; semuanya menunggu orang membuka layar. Pemilik
permintaan sendiri menyatakan belum pernah melihat blok yang sudah tayang.

**Ada harness agent di jaringan internal, tetapi milik pribadi.** VM netmon menjalankan Hermes
Agent dengan gateway hidup dan model `claude-opus-5` (lihat dok domain). Ia dipakai untuk
membuktikan rantai ERP dapat dipanggil dan bentuk laporannya masuk akal. Tetapi daftar izin
Telegram-nya berisi satu id, botnya bernama pribadi, dan percobaan menambah penerima kedua
ditolak sistemnya sendiri. netmon juga VM monitoring di kantor, bukan bagian stack ERP produksi.

**Empat jebakan angka yang sudah terbukti**, dan semuanya menentukan bentuk keputusan ini:

1. Laba periode pendek SELALU tampak rugi besar. Terukur: satu tim tampak rugi Rp 230 juta
   dalam 7 hari sementara laba yang benar-benar cair minus Rp 95 ribu. Penilaian wajib memakai
   laba matang.
2. `revenue` di level video hanya terisi **8,9%**; nol di sana berarti tidak diketahui, bukan
   tidak laku.
3. Level iklan menyimpan revenue nol secara struktural, sehingga labanya negatif sebesar biaya
   iklan dan itu bukan kerugian.
4. Retur sudah terpotong di dalam settlement. Menguranginya dua kali pernah membuat laba
   TikTok tercatat Rp 669.007.085 lebih kecil dalam sebulan. Kamus Metrik di layar sempat
   mengajarkan kesalahan itu selama 53 hari (diperbaiki erp-frontend #1678).

## Decision

### §1 Asisten berdiri di dalam ERP, bukan di harness luar

Menu, penyimpanan jadwal, penjalan, dan pengantarannya milik ERP. Harness di netmon TIDAK
menjadi bagian produk.

Empat alasan, ketiga pertamanya terukur: kepemilikannya melekat pada akun pribadi dan
penambahan penerima kedua sudah ditolak; netmon bukan bagian stack produksi sehingga fitur ERP
akan bergantung pada VM kantor; dan identitasnya tunggal, sementara menu ERP menuntut hak akses
mengikuti orang yang membukanya. Keempat, di dalam repo ada code review, test, dan CI.

Ini **tidak** menuntut service baru. ERP sudah punya klien AI tipis di `shared-library/ai`
([[ADR - 0082 Integrasi AI lewat Klien Tipis di Shared-Library]]) yang sudah dipakai dua tempat
di recruitment.

### §2 Tiga irisan berurutan, dan yang pertama tanpa AI

1. **Template dan penjadwalan, tanpa AI.** Daftar analisa siap pilih, jadwal yang disetel
   pemakainya, dikirim lewat Inbox. Isinya angka yang sudah dihitung backend, apa adanya.
2. **AI merangkai** template itu jadi kalimat, dengan keluaran terkunci skema.
3. **Tanya-jawab bebas**, dan hanya bila pemakaian irisan 1 membuktikan orang bertanya di luar
   template.

Urutannya bukan kehati-hatian. Irisan 1 menghasilkan data yang dibutuhkan untuk merancang
irisan 3: template mana yang paling sering dipilih adalah petunjuk paling dapat dipercaya
tentang pertanyaan apa yang sebenarnya orang punya.

### §3 Template adalah pengaman, bukan pembatas

Banyak pertanyaan yang wajar diajukan justru tidak punya data: diskon mana yang menggerus laba
(kolomnya belum dipisah), konversi iklan TikTok (cakupan di bawah 1%), pola musiman (riwayat
efektif 8 bulan). Kotak tanya bebas akan menerima pertanyaan itu dan menjawabnya dengan
percaya diri.

Template menutup lubang itu di depan, dan ia dapat dibuat tanpa AI sama sekali.

### §4 Model tidak pernah menerima angka mentah

Yang diberikan ke model hanya hasil hitung backend beserta penanda ketidakpastiannya
(`attribution_kolom`, laba matang vs belum matang, umur data). Keluarannya dikunci skema, bukan
prosa bebas, sehingga dapat divalidasi sebelum sampai ke orang.

Alasannya bukan kehati-hatian umum, melainkan keempat jebakan di §Context: seluruhnya
menghasilkan angka masuk akal yang salah, tanpa galat dan tanpa test yang menangkapnya.

### §5 Sistem mengurutkan, orang memutuskan

> ⛔ **Digantikan 2026-09-25** oleh [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]]: Direktur memutuskan laporan membawa keputusan tindakan yang dijalankan atau ditolak orang. Yang tetap: sistem tidak mengeksekusi apa pun sendiri, dan tidak ada besaran rupiah anggaran. Teks di bawah dipertahankan sebagai jejak alasan semula.

Ditegaskan ulang dari [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]]
§5. Tidak ada penghentian atau penambahan belanja iklan otomatis. Rekomendasi anggaran juga
tidak dijanjikan: simulasi alokasi sengaja dimatikan sejak 2026-08-15 karena hubungan belanja
ke laba jauh lebih lemah (R² 0,258) daripada belanja ke revenue (0,714).

### §6 Daftar penerima ditulis eksplisit, tidak diturunkan dari peran

`RequireMarketingLeader` jauh lebih luas daripada namanya: selain supervisor Kyura dan Beauty
Hacks serta leader iklan, ia meloloskan 16 supervisor Integration dan 15 orang IT. Dipakai
sebagai daftar kirim, 31 orang non-marketing ikut menerima laba seluruh toko.

Gerbang akses **menu** tetap memakai peran; daftar **penerima laporan** ditulis sendiri.

### §7 Kondisi berhenti ditetapkan di muka

> ⛔ **Digantikan 2026-09-25** oleh [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]] §9: irisan 2 dikerjakan tanpa menunggu 30 hari pemakaian irisan 1 (keputusan Direktur), dan ukuran berhentinya kini jawaban jalankan/tolak atas keputusan AI. Semangatnya tetap: fitur ini punya kondisi berhenti tertulis.

Irisan 1 dinilai setelah 30 hari dengan satu ukuran: berapa laporan yang benar-benar dibuka,
dan berapa tindakan yang mengikutinya. Bila nol, fitur dihentikan dan irisan 2 tidak
dikerjakan. Fitur analitik hampir tidak pernah punya kondisi berhenti, dan itu sebabnya banyak
yang hidup bertahun-tahun tanpa dibaca.

## Consequences

**Menyelesaikan ketegangan dengan ADR 0058 §2.** Aturan itu melarang service AI terpisah supaya
model tidak terpisah dari data. Keputusan ini mematuhinya dengan cara yang lebih kuat daripada
yang dibayangkan saat itu: tidak ada service baru sama sekali, dan pemanggilan model memakai
klien tipis dari service pemilik data. Rancangan di [[Microservices - Assistant Service]] yang
mengandaikan service tersendiri karena itu **digantikan** untuk irisan 1 dan 2; ia tetap
relevan sebagai bahan irisan 3, dan ketegangan yang dicatatnya sudah dijawab di sini.

**Kategori inbox baru menuntut dua container naik bersama.** `notification.InboxCategories` di
shared-library adalah daftar izin, dan service yang tidak di-rebuild memegang salinan lama.
Gagalnya senyap: fitur tampak jalan penuh, notifikasinya tidak pernah tiba. Sudah menggigit dua
kali. Marketing-analytics dan notification-service wajib naik bersamaan, lalu satu notifikasi
sungguhan dipicu sebagai bukti.

**Tujuan notifikasi wajib memakai rute aplikasi**, bukan URL eksternal, karena URL eksternal
tidak berfungsi di MyBharata.

**Asisten menyimpan datanya sendiri** (jadwal, penerima, riwayat kirim). Kepemilikan koleksinya
perlu diputuskan saat perencanaan irisan 1; menaruhnya di marketing-analytics membuat modul itu
tahu soal penjadwalan, yang bukan urusannya.

**Dua keputusan non-teknis memblokir kualitas, bukan kelayakan.** Target ROAS masih dua angka
(4,5 di dashboard, 3,2 di KPI Leader), sehingga vonis "boros" memakai ambang yang belum
disepakati. Dan daftar harga minimal belum pernah diunggah siapa pun, sehingga Harga & Diskon
tidak dapat dianalisa apa pun.

**Hermes tetap dipakai sebagai alat uji.** Ia sudah membayar dirinya: membuktikan rantai ERP
dapat dipanggil dan bentuk laporan masuk akal, tanpa satu baris kode ditulis di repo. Ia tidak
menjadi ketergantungan produk.

## Realisasi (2026-09-23)

Irisan 1 mendarat di `main` lewat PR [#2003](https://github.com/bip-itteam-internal/bip-erp/pull/2003), [#2005](https://github.com/bip-itteam-internal/bip-erp/pull/2005), dan [#2013](https://github.com/bip-itteam-internal/bip-erp/pull/2013). Cara kerjanya diuraikan satu tempat saja, di [[Microservices - Marketing Analytics Service]] §Asisten Analisa; kontrak per-rute di [[API - Marketing Analytics Service]]. Yang dicatat di sini hanya **tempat keputusannya bergeser dari ADR ini**.

**Kepemilikan data diputuskan: `marketing_analytics_db`**, koleksi `jadwal_laporan` dan `hasil_analisa`. §Consequences menyebut ini perlu diputuskan saat perencanaan dan menandai konsekuensinya (modul ini jadi tahu soal penjadwalan); konsekuensi itu diterima, karena alternatifnya melahirkan pertanyaan service baru yang sudah dijawab §1.

**§6 dilampaui, bukan sekadar dipenuhi.** §6 menulis "gerbang akses **menu** tetap memakai peran; daftar **penerima** ditulis sendiri". Penerima memang ditulis eksplisit. Tetapi gerbang menunya ikut dipersempit jadi `RequireMarketingReportAdmin` (kyura SPV/admin, beauty_hacks SPV/admin, it admin), memakai alasan §6 sendiri: `RequireMarketingLeader` jauh lebih luas daripada namanya. Yang berhak MEMBACA angka marketing tidak dengan sendirinya berhak memutuskan angka itu dikirim ke siapa. Terukur kosong saat dipersempit, jadi tak mencabut apa pun dari siapa pun.

**Satu bentuk yang tidak ada di ADR ini: KIRIMAN.** Satu jadwal memegang beberapa analisa, satu lingkup, satu daftar penerima. ADR ini mengandaikan jadwal per template. Alasannya di dok service; ringkasnya, yang berbeda iramanya bukan tiap analisa melainkan tiap kebutuhan.

⛔ **Satu temuan yang mengubah arti §6, dan belum diputuskan.** Diukur di PROD 2026-09-23 dengan kontrol positif dan negatif: `/beranda`, `/summary`, dan `/returns/detail` membalas **200 berisi angka laba seluruh perusahaan** untuk pemanggil **tanpa peran modul apa pun**, sementara `/jadwal-laporan` membalas 403 untuk peran yang sama. Artinya lingkup pada kiriman adalah penyaring **tampilan**, bukan kontrol kerahasiaan, dan §6 melindungi daftar kirim tanpa melindungi angkanya. Menyusun aturan lingkup per orang di atas endpoint yang tak punya gerbang menciptakan kesan kerahasiaan yang tidak ada — lebih berbahaya daripada terbuka terang-terangan, karena orang lalu memasukkan hal sensitif ke dalamnya. Keputusannya (terima terbuka, atau gerbang jalur bacanya) menunggu di issue bip-erp [#2008](https://github.com/bip-itteam-internal/bip-erp/issues/2008).

**Yang belum**: narasi AI (irisan 2) belum dipasang sehingga seluruh baris berstatus `menunggu`; layar FE belum ada; dan §7 belum dapat ditegakkan karena pengukuran pemakaian (T6) menunggu layar itu. **Jam nol 30 hari §7 belum berjalan** — ia mulai saat orang benar-benar bisa membuka laporannya, bukan saat kodenya merged maupun ter-deploy.

### Terbukti jalan di PRODUKSI, 2026-09-23

⚠️ Keadaan bertanggal, **ukur ulang sebelum dipakai**. Prosedur dan gerbangnya di [[RUN - Deploy Microservices bip-erp]].

Satu kiriman sungguhan dijalankan ujung-ke-ujung di prod dengan lingkup `Kyura`: dibuat lewat `POST /jadwal-laporan` (201), penjalan merangkainya, dan notifikasinya **tiba di kotak masuk penerimanya**. Gerbang biner terbukti dari keluarannya sendiri — string `variasi angka berbeda` terukur **nol** di biner prod sebelum deploy dan muncul di badan notifikasi sesudahnya, sehingga yang melayani memang build baru.

**Badan kiriman 686 karakter, 11 baris.** Pembandingnya: kiriman pertama di DEV sebelum perbaikan berukuran **13.017 karakter, 43 baris**, yang 98%-nya satu kalimat catatan diulang. Perbaikannya di bip-erp [#2024](https://github.com/bip-itteam-internal/bip-erp/pull/2024); alasannya di [[Microservices - Marketing Analytics Service]] §Asisten Analisa.

⛔ **Dua hal di isi laporan produksi yang menuntut keputusan, bukan perbaikan kode.**

Pertama, laporannya mencetak `ROAS: 5.95 (ambang 4.5)`. Ambang 4,5 adalah angka dashboard, sementara KPI Leader memakai 3,2 — dan §Consequences ADR ini sendiri mencatat keduanya belum disatukan. Artinya vonis yang sekarang benar-benar sampai ke orang berdiri di atas ambang yang belum disepakati siapa pun. Selama dua angka beredar, kata "boros" dan "sehat" di laporan ini tak punya dasar yang bisa dipertahankan.

Kedua, laporannya mencetak `Laba kotor: -Rp112.322.242` dengan `Status: belum_matang` — persis **jebakan pertama** di §Context, dan kekerapan `dua_harian` berjalan lurus ke sana. Peredamnya bekerja: baris catatan menerangkan bahwa minus itu berarti belum matang, bukan rugi. Tetapi yang terbaca lebih dulu tetap angka minus ratusan juta di baris ketiga, dan pembaca yang berhenti di situ menyimpulkan kebalikan dari yang benar. **Untuk penerima tingkat direksi, kekerapan bawaan sebaiknya mingguan, bukan dua harian.**

## Terkait

- [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]]
- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]]
- [[ADR - 0082 Integrasi AI lewat Klien Tipis di Shared-Library]]
- [[Microservices - Assistant Service]]
- [[Microservices - Marketing Analytics Service]]
- [[LOG - 2026-09-17 Audit Checklist Marketing dan Integration]]
- [[IT - Server, VMs and Databases]]
- [[ANALISA - Asisten Analisa Marketing]]
