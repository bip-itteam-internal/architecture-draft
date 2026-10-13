# ADR - 0176 Ulasan Shopee Dibalas dari ERP oleh Pemegang Toko, Otomatisasi Menyusul

> **Status**: 🟡 **Diusulkan**, 2026-10-13. Kode: BE bip-erp#3054 dan FE erp-frontend#2393 merged 2026-10-13 atas perintah langsung Pemutus, halaman Rating erp-frontend#2416 belum merged, deploy prod belum diverifikasi (per 2026-10-14). Disetujui pemohon lewat `/analisa-kebutuhan` (opsi A dari tiga). Pemutus: irfanarfianto. Berdiri di atas grounding vault + kode `origin/main` + pengukuran prod read-only 2026-10-13. Papan kerja: [[ANALISA - Balas Ulasan Shopee dari ERP]].

## Untuk Manajemen

**Apa yang berubah di layar.** Di halaman Ulasan dan Komplain Belum Dibalas, ulasan Shopee yang belum dibalas mendapat kotak balasan dan tombol Kirim. Balasan langsung tampil di Shopee dan di ERP, tanpa membuka Seller Center. Ulasan yang sudah dibalas menampilkan balasannya seperti sekarang.

**Siapa yang terdampak.** CS yang memegang toko dan Account Specialist pemegang akun toko: mereka bisa membalas ulasan toko yang mereka pegang. Leader, SPV, dan tim Integration tetap bisa membaca semua toko, tetapi tidak membalas dari ERP.

**Apa yang TIDAK dijanjikan.**
- **Belum ada balasan otomatis, template tersimpan, atau kirim massal.** Satu ulasan dibalas satu kali tekan. Otomatisasi adalah langkah berikutnya dengan keputusan sendiri.
- **Tidak ada teks buatan AI.** Teks balasan ditulis orang.
- **Ulasan TikTok tetap dibalas di Seller Center TikTok**, karena TikTok tidak memberikan isi ulasan ke ERP.
- **Balasan yang sudah terkirim tidak bisa diubah atau dihapus dari ERP.** Shopee hanya mengizinkan satu balasan per ulasan.
- Ulasan baru tetap masuk ERP sekali sehari, pagi hari.

**Perkiraan besaran kerja.** Satu PR backend dan satu PR frontend, masing-masing beberapa hari kerja. Tidak ada pengaturan baru di server dan tidak ada paket izin baru.

## Deskripsi

*Ulasan Shopee dibalas dari ERP oleh orang yang memegang tokonya, satu ulasan per tekan Kirim, dikirim saat itu juga memakai token toko dan dicatat atas nama pengirim. Menggantikan kalimat "balasan tetap di Seller Center" di [[ADR - 0160 Cakupan Baca Ulasan Mencakup Toko Pegangan CS, Menu Dibuka lewat Paket Izin yang Ada]] untuk Shopee. Balasan otomatis, template, dan kirim massal sengaja ditunda ke keputusan berikutnya.*

- **Path di repo**: `bip-erp/services/integration/internal/infrastructure/clients/shopee_client_new.go` (fungsi `reply_comment`) · `bip-erp/services/integration/internal/usecase/review_reply_usecase.go` (baru) · `bip-erp/services/integration/internal/domain/entity/review_reply_log.go` (baru) · `bip-erp/services/integration/internal/interface/http/review_handler.go` + `review_scope.go` · `erp-frontend/src/features/integration/reviews/components/` (kotak balasan, baru) · `erp-frontend/src/features/marketing/layanan/components/halaman-komplain-terbuka.tsx`
- **Tanggal**: 2026-10-13

## Context

**Pekerjaannya tidak terkejar.** Diukur prod 2026-10-13 atas `integration_db.marketplace_reviews`, ulasan Shopee 90 hari terakhir:

| Ukuran | Nilai |
|---|---|
| Ulasan | 22.429 (sekitar 250 per hari) |
| Dibalas | 8.345 (37%) |
| Jeda balas | median 45 jam, p90 112 jam |
| Bintang 5 / bintang 1-2 | 20.566 / 167 |
| Berteks | 1.749 (7,8%) |
| Empat toko Kyura (`department_shops`) | 9.609 ulasan, 58 dibalas (0,6%) |
| Toko Beautyhacks | 50% sampai 75% dibalas |

Hari ini CS membalas satu per satu di Seller Center Shopee. ERP sudah menampilkan ulasan beserta penyaring "Belum dibalas" ([[Microservices - Integration Service]] § Ulasan Marketplace), jadi orangnya membaca di satu aplikasi lalu membalas di aplikasi lain.

**Izin API sudah ada.** Dokumentasi resmi `v2.product.reply_comment` menyebut tipe app yang boleh memanggilnya: ERP System, Seller In House System, Product Management, Swam ERP. Sync ulasan memakai kredensial ERP_SYSTEM (`SHOPEE_ERP_SYSTEM_PARTNER_*`), yaitu app "One Bharata" berkategori ERP System, Live Partner_id 2032314, dicek di Shopee Open Platform Console 2026-10-13. `reply_comment` satu modul (Product) dengan `get_comment` yang sudah jalan tiap hari. Batasan dari dokumentasinya: 1 sampai 100 komentar per panggilan, 1 sampai 500 karakter, satu ulasan hanya bisa dibalas sekali (`product.duplicate_request`), dan `product.error_permission` berarti token toko perlu diotorisasi ulang.

**Yang mengikat dari keputusan lain.**
- [[ADR - 0160 Cakupan Baca Ulasan Mencakup Toko Pegangan CS, Menu Dibuka lewat Paket Izin yang Ada]] §5: balas ulasan menunggu cek izin API, lalu ADR tersendiri. Ini ADR tersendiri itu.
- [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]]: "pembeli tetap dibalas CS". Tetap benar: yang membalas tetap orang, hanya tempatnya pindah.
- [[ADR - 0145 Agen Pengelola Toko Tumbuh dari Mesin Keputusan yang Ada, Dampak Diukur Sebelum Eksekusi]] (🟡 Diusulkan) §6 menggariskan arah aksi tulis ke marketplace: dijalankan saat orang menekan, memakai identitas orang yang menekan, dimulai dari balas ulasan. Keputusan ini mengikuti bentuk itu, tetapi **bukan** eksekusi keputusan agent: tidak ada usulan sistem yang disetujui, yang ada orang menulis balasannya sendiri. Karena itu ia tidak menunggu gerbang dampak ADR 0145 §5, dan butir T11 di [[ANALISA - Agen Pengelola Toko]] tetap terbuka untuk balasan yang diusulkan agent.
- [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]] §2 (larangan memanggil platform dari laporan Asisten, sebagian sudah dicabut [[ADR - 0169 Asisten Analisa Marketing Dihapus, Copilot Jadi Pintu Tunggal, Mesin Keputusan Dipertahankan]]) tidak tersentuh: Asisten dan Copilot tetap tanpa aksi tulis.

**Dua sifat kode yang memaksa bentuk penyimpanan.** Sync menimpa SELURUH dokumen ulasan (`ReplaceOne` di `review_repo.go` `BulkUpsertReviews`), sehingga field tambahan apa pun di dokumen itu terhapus tiap pagi. Dan sync berhenti begitu satu halaman seluruhnya sudah tersimpan (`review_sync_usecase.go`), sehingga balasan untuk ulasan lama bisa tidak pernah terambil ulang.

**Yang tidak diukur.** Masalah yang dijawab (beban CS dan cakupan balasan) adalah asumsi analis dari data di atas; permintaannya datang dari Tech Development, bukan dari pemilik proses CS atau manajemen marketing.

## Decision

### 1. Ulasan Shopee dibalas dari ERP, satu ulasan per tekan Kirim

Kirim memanggil `POST /api/v2/product/reply_comment` saat itu juga, dengan token ERP_SYSTEM toko pemilik ulasan, berisi satu komentar. Tidak ada antrean, tidak ada pengiriman tertunda, tidak ada pengiriman tanpa orang. TikTok tidak berubah.

### 2. Yang boleh mengirim: pemegang toko, bukan pembaca semua toko

Boleh membalas ulasan toko X = pemanggil punya baris **aktif** untuk X di `icc_account_mappings` **atau** di `cs_shop_mappings`. Pembaca tanpa batas di `cakupanTokoUlasan` (Marketing Leader, staf Integration, pemegang `marketing.komplain-terbuka.view` cakupan semua) **tidak** otomatis boleh membalas: balasan tampil publik atas nama toko, jadi dikirim orang yang memegang toko itu. Tidak ada izin atau paket izin baru; wewenangnya mengikuti pemetaan toko.

Aturan itu hidup di **satu fungsi backend** yang dipakai dua kali: oleh rute kirim (menolak 403) dan oleh `GET /reviews/comments`, yang menambahkan penanda `boleh_balas` per baris. Frontend hanya membaca penanda itu dan tidak menyalin aturannya.

### 3. Isi balasan ditulis orang

Teks 1 sampai 500 karakter setelah dipangkas spasi, diperiksa di backend sebelum memanggil Shopee. Tanpa draf AI. Karena balasan tidak bisa diubah atau ditarik, layar meminta konfirmasi satu langkah sebelum mengirim.

### 4. Setiap percobaan dicatat di koleksi terpisah

Koleksi baru di `integration_db` (nama final di `/plan`), append-only, tidak pernah diubah: `comment_id`, `shop_id`, teks, pengirim (`entity.Actor` dari header gateway), waktu, hasil (berhasil, atau kode galat Shopee beserta pesannya). Percobaan yang gagal ikut dicatat. Tidak disimpan di dokumen `marketplace_reviews`, karena sync menghapusnya.

### 5. Sesudah berhasil, data lokal diperbarui saat itu juga

`comment_reply` di dokumen ulasan di-`$set` (bukan diganti utuh) dengan teks dan waktu kirim, sehingga ulasan langsung keluar dari daftar "Belum dibalas". Sync berikutnya menimpanya dengan versi Shopee, yang isinya sama.

### 6. Galat Shopee dibaca, bukan diratakan

| Galat | Arti di layar |
|---|---|
| `product.duplicate_request` | Ulasan sudah dibalas (misalnya dari Seller Center); belum terlihat di ERP sampai sync berikutnya |
| `product.error_permission`, `error_auth` | Token toko perlu diotorisasi ulang; hubungi tim Integration |
| `product.comment_length_invalid` | Panjang teks di luar 1 sampai 500 |
| `product.error_not_exist` | Ulasan sudah tidak ada di Shopee |
| lainnya | Gagal mengirim, coba lagi |

Shopee membalas HTTP 200 untuk galat; hasilnya dibaca dari `error` dan `response.result_list[].fail_error`, bukan dari status HTTP.

### 7. Otomatisasi, template, dan kirim massal ditunda

Data 90 hari menunjukkan 98,5% balasan memakai empat teks template yang sama, jadi langkah berikutnya yang paling bernilai adalah template dan pengiriman massal atau otomatis. Itu butuh keputusan sendiri yang menjawab: bintang mana yang ikut, siapa mengelola template, dinyalakan per toko atau per brand, dan identitas siapa yang tercatat bila tak ada orang yang menekan (bersinggungan dengan [[ADR - 0135 Jadwal Tugas Copilot Mengirim Pengingat, Bukan Menjalankan Tanpa Kehadiran Pemakai]] §7). Jejak di §4 sudah membedakan pengirim, jadi keputusan itu tidak perlu mengubah bentuk penyimpanan.

## Consequences

- Kalimat "balasan tetap di Seller Center" berhenti berlaku untuk Shopee di [[ADR - 0160 Cakupan Baca Ulasan Mencakup Toko Pegangan CS, Menu Dibuka lewat Paket Izin yang Ada]], [[Microservices - Integration Service]], dan teks layar erp-frontend (`reviews.ulasan.balasSellerCenter`, keterangan sumber data halaman Ulasan, keterangan halaman Komplain Belum Dibalas). Komentar `url-ulasan.ts` yang menyebut API Shopee tak menyediakan balasan keliru dan ikut dibetulkan.
- Aksi tulis pertama ke marketplace selain pengiriman barang. Klien Shopee mendapat POST kedua di jalur yang sama dengan `ShipOrder`, dan ikut rate limiter `SHOPEE_RATE_LIMIT_QPS` yang sudah ada.
- **Deploy BE sebelum FE.** FE yang naik lebih dulu tidak menerima `boleh_balas`, dan wajib memperlakukan field yang hilang sebagai tidak boleh (tombol tak tampil), bukan galat.
- Tidak ada env baru, kategori inbox baru, atau paket izin baru.
- Risiko: satu ulasan bisa dibalas dari Seller Center dan ERP hampir bersamaan; yang kedua ditolak Shopee (`duplicate_request`) dan dibaca seperti §6. Orang yang hanya memegang toko lewat `cs_shop_mappings` baru bisa membuka menu Ulasan sesudah paket izin ADR 0160 terpasang padanya.
- Keputusan ini tidak mengubah hak mengajukan komplain (tetap `icc_account_mappings`, ADR 0160).

## Terkait

- [[ANALISA - Balas Ulasan Shopee dari ERP]] (papan kerja + issue)
- [[Microservices - Integration Service]] § Ulasan Marketplace · [[API - Integration Service]] § Reviews
- [[ADR - 0160 Cakupan Baca Ulasan Mencakup Toko Pegangan CS, Menu Dibuka lewat Paket Izin yang Ada]] · [[ADR - 0145 Agen Pengelola Toko Tumbuh dari Mesin Keputusan yang Ada, Dampak Diukur Sebelum Eksekusi]] · [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]]
