> **Status**: 🟡 **Belum di kode**: PR terbuka, belum merged (bip-erp#2837 untuk keputusan ini; diukur 2026-10-08, ukur ulang sebelum dipakai). 🟢 Diterima, 2026-10-08, oleh irfanarfianto: Pemutus memerintahkan pengerjaannya di sesi analisa hari itu, dan baris ini ditulis agent atas perintah tersebut. Papan kerja: `ANALISA - Shop Quality Membaca Ulasan Toko Pegangan CS` di Workspace.

## Untuk Manajemen

**Apa yang berubah di layar.** Halaman Ulasan di ERP sudah menampilkan ulasan pembeli dari seluruh toko Shopee dalam satu daftar: nama toko, tanggal ulasan, jumlah bintang, isi ulasan, dan penanda ulasan yang belum dibalas. Staf Shop Quality selama ini tidak bisa memakainya, karena halaman itu hanya menampilkan toko yang dipegang seseorang sebagai pemegang akun toko, sedangkan Shop Quality tercatat sebagai CS toko. Sesudah keputusan ini, Shop Quality membuka halaman yang sama dan melihat ulasan toko yang ia layani sebagai CS, tanpa membuka toko satu per satu.

**Siapa yang terdampak.** Tiga orang berjabatan Shop Quality (satu di Kyura, dua di Beauty Hacks). Pemegang akun toko, leader marketing, dan tim Integration tidak berubah apa pun.

**Yang tidak dijanjikan.**

- **Ulasan TikTok per pembeli tidak ada.** TikTok tidak memberikan isi ulasan lewat jalur yang dipakai ERP, hanya sebaran bintang per produk. Untuk toko TikTok, ulasan tetap dibaca di Seller Center.
- **Ulasan Lazada belum ada sama sekali** di ERP.
- **Membalas ulasan dari ERP belum dibangun.** Balasan tetap dilakukan di Seller Center. Itu keputusan terpisah yang menunggu kepastian izin dari marketplace.
- **Mengajukan komplain dari ulasan tetap hak pemegang akun toko.** Shop Quality membaca ulasan, tetapi tidak mengajukan komplain dan tidak melihat penanda ulasan mana yang sudah dikomplainkan.
- **Data diperbarui sekali sehari, pagi hari.** Ulasan yang masuk siang ini terlihat besok pagi.

**Besaran kerja.** Kecil: satu perubahan di sisi server, tanpa perubahan tampilan, lalu satu langkah pemasangan hak akses ke tiga akun.

## Deskripsi

*Cakupan baca ulasan marketplace diperluas dari toko yang dipegang sebagai pemegang akun menjadi gabungan dengan toko yang dipegang sebagai CS, dan menu Ulasan dibuka untuk Shop Quality lewat paket izin yang sudah ada. Lahir dari permintaan Shop Quality yang membayangkan fitur baru, padahal fiturnya sudah ada dan yang hilang hanya aksesnya.*

- **Status**: lihat baris pertama dok ini (satu tempat, supaya tidak menyimpang saat disetujui).
- **Path di repo**: `bip-erp/services/integration/internal/interface/http/review_scope.go` · `bip-erp/services/integration/internal/interface/http/review_scope_test.go` · `bip-erp/services/integration/main.go` (pendaftaran grup `/reviews`) · komentar di `bip-erp/shared-library/common/catalog_akuntoko.go` dan `bip-erp/services/assistant/internal/alat/lintas_ulasan_produk.go`
- **Tanggal**: 2026-10-08

## Context

Permintaannya berbunyi: "saya harus membuka toko satu per satu untuk melihat ada ulasan atau tidak", dengan usulan fitur ulasan dan komplain yang memuat nama toko, tanggal, dan bintang, serta bila bisa membalas ulasan dari ERP. Pemohonnya staf berjabatan Shop Quality.

Diperiksa ke `origin/main` kedua repo dan diukur di prod pada 2026-10-08:

1. **Fiturnya sudah ada.** Tab Ulasan di `/integration/reviews` menampilkan daftar gabungan lintas toko dengan nama toko, tanggal, bintang, isi, dan filter "Belum dibalas" (`erp-frontend` `src/features/integration/reviews/components/review-card.tsx`, `daftar-ulasan.tsx`). Datanya 23.649 ulasan Shopee dari 15 toko, terbaru pagi itu.
2. **Sinkronnya sehat.** Job `sync-reviews` jalan tiap 06:45 WIB, 40 run terakhir sukses, sekitar 13 menit per run, 15 toko Shopee tanpa galat.
3. **Pemohon tidak bisa melihatnya.** Kelima rute `/reviews/*` dibatasi `MiddlewareCakupanUlasan` ke toko di `icc_account_mappings` milik pemanggil, dan yang tidak memegang toko mendapat nol baris (`review_scope.go`). Akun pemohon memegang nol baris di koleksi itu. Paket izin yang membuka menu Ulasan (`marketing_akuntoko_pemegang`) juga tidak terpasang padanya.
4. **Pemohon justru tercatat sebagai CS toko.** `cs_shop_mappings` berisi 21 baris aktif, seluruhnya atas nama pemohon: 17 toko TikTok dan 4 toko Shopee. Ketiga pemegang jabatan Shop Quality ber-`position_key` `customer_support`.
5. **Pekerjaannya nyata.** Di empat toko Shopee itu ada 3.627 ulasan dalam 30 hari terakhir, 3.599 di antaranya belum dibalas dan 67 berbintang 1 sampai 3.

Dok [[Microservices - Integration Service]] sudah meramalkan titik ini: kepemilikan CS "sengaja belum ikut" di cakupan ulasan karena CS tak punya menu Ulasan, dan "wajib ikut" begitu ada kebutuhannya. Kebutuhan itu datang lebih awal daripada fitur balas ulasan yang semula jadi pemicunya.

Batas yang tidak bisa dilewati keputusan ini: teks ulasan per pembeli hanya ada untuk Shopee. TikTok hanya memberi sebaran bintang kumulatif per produk, dan Lazada belum disinkronkan. Jadi untuk 17 dari 21 toko pemohon, ERP tidak menghapus kebutuhan membuka Seller Center. Volume ulasan TikTok di toko-toko itu tidak diketahui, sehingga seberapa besar keputusan ini meringankan pekerjaannya belum terukur.

Keputusan terdahulu yang disentuh:

- [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]] menurunkan hak **baca dan mengajukan** dari `icc_account_mappings`. Keputusan ini melebarkan hak **baca** saja.
- [[ADR - 0107 Alat Kerja Pemegang Akun Toko lewat Izin Posisi akuntoko]] butir 6 masih menulis "Ulasan tetap menampilkan semua toko". Kalimat itu sudah tidak benar sejak cakupan dipasang 2026-09-23.
- [[ADR - 0145 Agen Pengelola Toko Tumbuh dari Mesin Keputusan yang Ada, Dampak Diukur Sebelum Eksekusi]] mensyaratkan ADR sendiri dan izin scope marketplace untuk tiap aksi tulis ke marketplace, termasuk balas ulasan.

## Decision

### 1. Cakupan baca ulasan = gabungan toko pegangan akun dan toko pegangan CS

Toko yang boleh dibaca seseorang di kelima rute `/reviews/*` adalah gabungan:

- toko di `icc_account_mappings` miliknya yang `is_active`, dan
- toko di `cs_shop_mappings` miliknya yang `is_active`.

Yang tidak berubah: leader dan SPV marketing serta tim Integration tetap membaca seluruh toko; yang tidak memegang toko di kedua koleksi tetap mendapat **nol baris**, bukan semua; cakupan tetap dipasang paling akhir dan menimpa `shop_id` dari query; gagal membaca **salah satu** pemetaan tetap 500, bukan daftar kosong.

Kedua koleksi tetap terpisah. Entity `CsShopMapping` sudah melarang penggabungannya dengan `IccAccountMapping`, dan keputusan ini tidak mengubah itu: yang digabung adalah hasil bacanya di satu fungsi cakupan, bukan penyimpanannya.

### 2. Hak mengajukan komplain tidak ikut melebar

Tombol "Ajukan komplain" dan gerbang tulis kedua register komplain tetap diturunkan dari `icc_account_mappings` saja, sesuai ADR Komplain dari Ulasan Marketplace. Pemegang CS membaca ulasan tanpa tombol mengajukan dan tanpa lencana "Sudah dikomplain": frontend hanya meminta riwayat komplain bagi pemegang akun toko (pembaca lain ditolak 403), dan itu tidak diubah. Alasannya: mengajukan komplain menggerakkan KPI gudang dan antrean QC, dan belum ada yang meminta CS menjadi pengaju.

### 3. Menu dibuka lewat paket izin yang sudah ada, tanpa izin baru

Paket `marketing_akuntoko_pemegang` dipasang ke akun pemegang jabatan Shop Quality. Tidak dibuat izin atau paket baru untuk tiga orang.

Konsekuensi yang diterima sadar: paket itu juga memunculkan menu Komplain ke Gudang dan Komplain ke QC, yang bagi pemegang CS akan berisi daftar kosong karena kedua register tetap dibatasi ke toko pegangan akun. Bila itu terbukti membingungkan, pemisahan izin baca ulasan dari izin komplain menjadi keputusan lanjutan, tidak dikerjakan sekarang.

⚠️ **Asumsi yang wajib dibuktikan di DEV sebelum prod**: bahwa memasang paket itu saja cukup memunculkan kategori Marketing dan menu Ulasan bagi akun yang tidak punya peran marketing. Bila tidak, yang kurang ada di frontend dan keputusan ini bertambah satu pekerjaan.

### 4. Kesegaran tetap harian

Tidak ada perubahan jadwal dan tidak ada tombol sinkron manual. Ulasan kemarin terlihat pagi ini.

### 5. Balas ulasan tidak diputuskan di sini

Tetap di Seller Center. Jalur menuju balas ulasan Shopee tetap seperti yang ditulis ADR Agen Pengelola Toko: cek izin scope API lebih dulu, lalu ADR tersendiri.

### 6. Urutan pemasangan

Backend naik lebih dulu, baru paket izin dipasang. Bila terbalik, menu Ulasan muncul dengan daftar kosong dan terbaca sebagai "toko saya belum punya ulasan".

## Consequences

**Yang didapat.** Pemegang CS melihat ulasan Shopee toko yang dilayaninya dalam satu daftar, dengan filter "Belum dibalas" dan "Semua bintang" yang sudah ada. Tidak ada layar baru dan tidak ada salinan aturan cakupan baru.

**Yang tidak didapat.** Toko TikTok dan Lazada tetap tidak punya ulasan per pembeli di ERP. Pemohon tetap membalas di Seller Center; supaya langkah itu tidak buntu, kartu ulasan diberi nomor pesanan yang bisa disalin dan tautan ke Seller Center Shopee (pekerjaan frontend terpisah, erp-frontend#2207, tidak mengubah keputusan ini).

**Risiko.**

- Tab Ulasan bawaannya menyaring bintang 1 sampai 3, pilihan yang dibuat untuk alur komplain. Pemegang CS yang ingin melihat semua ulasan harus menekan "Semua". Dibiarkan sampai ada keluhan nyata.
- Aturan cakupan ulasan saat ini dinyatakan ulang di dua komentar kode di luar `review_scope.go`, dan salah satunya sudah menyimpang (masih berbunyi ulasan tidak membatasi baris). Pekerjaan backend keputusan ini wajib merapikan keduanya supaya menunjuk ke satu tempat.
- Baris status sinkron di halaman Ulasan saat ini memperingatkan "toko gagal sinkron" untuk toko TikTok yang sudah dinonaktifkan sejak Agustus 2026. Pemegang CS baru akan membacanya sebagai kerusakan. Perbaikannya pekerjaan terpisah, tidak bergantung keputusan ini.

**Dok yang ikut berubah saat kodenya mendarat**: [[Microservices - Integration Service]] (paragraf cakupan toko), [[CORE - RBAC dan Permission Set]] (pemegang paket `akuntoko`).
