# ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI

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

- **Status**: 🟡 **Diusulkan** — kode belum ada. Berdiri di atas pengukuran produksi dan `origin/main` 2026-09-22.
- **Path di repo**: `bip-erp/services/marketing-analytics/` (baru), `erp-frontend/src/features/marketing-analytics/` (baru), `bip-erp/shared-library/notification/` (kategori inbox baru)
- **Tanggal**: 2026-09-22

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

## Terkait

- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]]
- [[ADR - 0082 Integrasi AI lewat Klien Tipis di Shared-Library]]
- [[Microservices - Assistant Service]]
- [[Microservices - Marketing Analytics Service]]
- [[LOG - 2026-09-17 Audit Checklist Marketing dan Integration]]
- [[IT - Server, VMs and Databases]]
- [[ANALISA - Asisten Analisa Marketing]]
