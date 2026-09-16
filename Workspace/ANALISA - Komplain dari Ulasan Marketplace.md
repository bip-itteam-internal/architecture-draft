# ANALISA - Komplain dari Ulasan Marketplace

Daftar task hasil `/analisa-kebutuhan` 2026-09-16. Keputusannya di [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]].

Papan kerja, bukan arsitektur. Tiap item cukup jelas untuk langsung dilempar ke `/start-task`.

## Menunggu keputusan orang, bukan kode

- [ ] **K1. Penindak internal untuk keluhan pengiriman lama.** Tidak ada departemen ekspedisi di sistem, dan kurirnya didominasi SPX milik Shopee. Pilihannya: diarahkan ke CS yang mengajukan klaim ke marketplace, ke Manufaktur sebagai pengirim, atau diakui di luar kendali dan tidak dibuatkan tiket. Memblokir seeding kategori `pengiriman_lama` saja, bukan seluruh pekerjaan.
- [ ] **K2. Kewajiban regulatif untuk keluhan dugaan efek tidak diinginkan.** Vault tidak punya dasarnya dan melarang mengarangnya. Pertanyaan untuk QA/RA: apakah keluhan semacam itu wajib masuk jalur CAPA atau pelaporan BPOM. Memblokir kategori itu saja.
- [ ] **K3. Lima toko Beauty Hacks tanpa CS.** Terukur 2026-09-16. Apakah memang belum ditugaskan atau pemetaannya tertinggal. Berdiri sendiri, tidak memblokir pekerjaan ini, tetapi memengaruhi KPI penyelesaian komplain yang sudah berjalan.

## Backend, berurutan

- [ ] **T1. Master kategori komplain.** Koleksi baru di employee-service mengikuti pola master yang sudah ada: `key`, `label`, `order`, `active`, `metadata`, ditambah penindak internal dan pihak luar. CRUD digerbang satu departemen. Seed kategori awal kecuali yang diblokir K1 dan K2.
- [ ] **T2. Tujuan dan salinan ulasan di register komplain.** Bergantung T1. Tambah field tujuan departemen, kategori, sumber, dan blok salinan ulasan. Gerbang validasi berubah dari khusus Quality menjadi per tujuan. Vonis jadi tiga nilai termasuk pengalihan, plus kolom tindakan dan tanggal. **Sekaligus tutup dua utang**: `company_id` yang belum ada, dan race `ReplaceOne` berfilter `_id` saja.
- [ ] **T3. Kategori inbox dan notifikasi per departemen.** Bergantung T2. Pola dua kategori: satu ke penerima saat diajukan, satu ke pengaju saat diputuskan. ⚠️ employee-service dan notification-service wajib naik bersama, notification-service lebih dulu.
- [ ] **T4. Pemicu notifikasi ulasan bintang rendah ke pemegang toko.** Dapat berdiri paralel dengan T2. Penerimanya diturunkan dari `department_shops`. Service mana yang memicunya diputuskan di `/plan`, sebab ulasan dimiliki integration-service sementara notifikasi bertetangga dengan employee-service.
- [ ] **T5. Pengisian otomatis kurir dan produk dari order.** Bergantung T2. Sumbernya `shopee_order_details.shipping_carrier`, dijodohkan lewat `order_sn` milik ulasan.

## Frontend

- [ ] **T6. Tombol ajukan komplain dari baris ulasan.** Bergantung T2. Di halaman Ulasan yang sudah ada, membawa serta `order_sn`, produk, bintang, teks, dan foto. Menampilkan penanda bila ulasan itu sudah pernah dikomplainkan, tanpa melarang pengajuan kedua.
- [ ] **T7. Kotak masuk komplain per departemen dan layar tindakan.** Bergantung T2 dan T3. Keterlihatannya menyalin pola [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]]. Wajib memuat tiga vonis dan kolom tindakan.
- [ ] **T8. Penanda "hanya Shopee" di layar.** Kecil, tetapi wajib, supaya ketiadaan TikTok tidak terbaca sebagai kelalaian.

## Sesudah data terkumpul

- [ ] **T9. Rekap pola per toko dan per kategori.** Baru berguna setelah beberapa bulan terkumpul. Ini juga yang kelak menjadi dasar menentukan tenggat, menggantikan angka tebakan.

## Di luar lingkup

- Klasifikasi otomatis atau LLM. Volumenya 3 sampai 4 per bulan.
- Membalas pembeli. Tetap milik CS di Seller Center.
- TikTok. Tidak ada teks ulasan per pembeli sama sekali.
- Tenggat dan SLA. Lihat keputusan 11 di ADR.
