> **Status**: 🟡 Diusulkan. Keputusannya diambil 2026-09-16; kodenya belum ada.

## Untuk Manajemen

Pemegang toko akan diberi tahu saat ada ulasan pembeli berbintang rendah, dan dari baris ulasan itu ia bisa langsung meneruskannya ke unit yang benar-benar bisa memperbaikinya, misalnya gudang untuk salah kirim atau QC untuk dugaan produk tidak asli. Unit penerima mendapat kotak masuk sendiri, menuliskan tindakan yang diambil, lalu menutupnya, dan pemegang toko dikabari hasilnya. Hari ini tidak ada satu pun dari rangkaian itu: tidak ada pemberitahuan ulasan sama sekali, dan satu-satunya jalur komplain yang tersedia hanya bermuara ke QC.

Yang terdampak: tiga orang Account Specialist yang memegang sembilan toko Shopee, staf gudang di Manufaktur, staf QC, serta supervisor Kyura dan Beauty Hacks. Tugas CS tidak berubah, ia tetap yang membalas pembeli di Seller Center.

Yang **tidak** dijanjikan, dan sebaiknya tidak diharapkan:

- Tidak melayani TikTok. TikTok tidak menyediakan teks ulasan per pembeli sama sekali, jadi fitur ini hanya untuk Shopee.
- Tidak membalas pembeli. Seluruh alur ini internal; pembeli tetap dibalas CS.
- Tidak mengklasifikasi ulasan secara otomatis. Kategorinya dipilih orang.
- Tidak memasang tenggat penyelesaian.
- Tidak menjawab kewajiban regulatif BPOM atas keluhan efek samping. Itu menunggu jawaban tim QA/RA.

Perkiraan besaran kerja: sedang, dan sebagian besarnya sudah berdiri. Register komplain, layar pengajuan, layar validasi, notifikasi dua arah, serta data ulasan harian semuanya sudah hidup. Yang benar-benar baru hanya satu daftar kategori, satu penanda tujuan, satu pemicu pemberitahuan, dan satu kotak masuk per departemen.

## Deskripsi

*Komplain yang lahir dari ulasan marketplace dirutekan ke departemen yang tepat dengan memperluas register komplain yang sudah ada, bukan dengan membangun modul tiket baru. Kategori keluhan menentukan tujuannya, dan pemetaan itu hidup sebagai master data, bukan sebagai konstanta di kode.*

- **Path di repo**:
  - `bip-erp/shared-library/models/employee/models.go` (`QualityComplaint`, field tujuan dan salinan ulasan)
  - `bip-erp/shared-library/models/employee/master_data.go` (master kategori komplain, **baru**)
  - `bip-erp/services/employee/quality_complaint.go` (gerbang validasi per tujuan)
  - `bip-erp/services/employee/quality_complaint_notify.go` (kategori inbox per departemen)
  - `bip-erp/services/integration/internal/interface/http/review_handler.go` (tidak berubah, dibaca saja)
  - `erp-frontend/src/app/(main)/integration/reviews/` (tombol ajukan dari baris ulasan, **baru**)
  - `erp-frontend/src/features/quality/complaint/` (kotak masuk per departemen, **baru**)
- **Tanggal**: 2026-09-16

## Context

Kebutuhan datang sebagai solusi: "klasifikasikan ulasan per toko supaya pemegang toko bisa mengajukan komplain ke pihak terkait, tidak harus ke QC saja". Pengukuran ke produksi pada 2026-09-16 mengubah bentuk jawabannya.

**Datanya ada, dan hanya untuk Shopee.** `integration_db.marketplace_reviews` memuat 17.970 ulasan, seluruhnya SHOPEE dan nol TikTok, membentang 2025-03-05 sampai hari pengukuran. Teks ulasannya tersimpan, begitu pula foto, `order_sn`, dan balasan CS. TikTok tidak menyediakan daftar ulasan individual sama sekali, sehingga komplain TikTok di ERP diturunkan dari delta snapshot bintang produk. Lihat [[Microservices - Integration Service]].

**Volumenya kecil, dan ini yang paling membelokkan rancangan.** Sebaran bintang: 81 bintang satu, 51 bintang dua, 343 bintang tiga, 1.230 bintang empat, 16.265 bintang lima. Yang berbintang tiga ke bawah **dan** berteks hanya sekitar 65 sepanjang 18 bulan, yaitu 3 sampai 4 per bulan untuk seluruh sembilan toko. Pada volume itu, klasifikasi otomatis tidak terbayar, dan satu pilihan yang ditekan manusia lebih murah sekaligus tidak bisa salah diam-diam.

**Temanya nyata dan memang milik unit yang berbeda.** Dari 40 ulasan bintang tiga ke bawah terbaru: pesanan tidak sesuai atau salah kirim 7, kemasan dan segel 6, dugaan produk tidak asli 5, klaim iklan tidak sesuai 3, pengiriman lama 2, mendekati kedaluwarsa 1, ditambah beberapa dugaan efek tidak diinginkan. Sisanya, 14 sampai 16 baris, adalah "produknya tidak mempan buat saya", yang berharga sebagai masukan produk tetapi bukan sesuatu yang dapat ditindak gudang atau QC.

**Kepemilikannya lengkap.** Kesembilan toko Shopee yang punya ulasan seluruhnya punya pemilik aktif, dipegang hanya tiga orang berposisi Account Specialist, jabatan yang sebelumnya bernama ICC. Sementara pemetaan CS justru timpang: hanya empat dari sembilan toko punya CS aktif dan semuanya satu orang. Kedua pemetaan itu sengaja terpisah dan menjawab pertanyaan berbeda, lihat [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]].

**Tidak ada yang diberi tahu.** Job sync ulasan tidak mengirim notifikasi kepada siapa pun; satu-satunya notifikasi di sana adalah Telegram ketika job-nya gagal. Jadi bahkan jalur komplain ke QC yang sudah ada pun tidak pernah terpicu oleh sebuah ulasan, karena tak ada pemicunya.

**Register komplain yang ada terkunci ke QC secara struktural.** Modelnya tidak punya satu pun field tujuan, rute validasinya digerbang staf Quality, dan kata "Valid" di sana berarti "memang kesalahan QC". Dok [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] sudah mencatat sendiri celahnya, bahwa komplain dan rating produk dari ulasan marketplace "tetap belum", dan bahwa register itu khusus komplain internal marketing ke QC, bukan ulasan pembeli.

**Tidak ada ADR yang mengatur komplain lintas departemen.** Penelusuran atas seluruh folder keputusan tidak menemukan satu pun. Jadi keputusan ini mengisi ruang kosong, bukan menabrak keputusan sebelumnya. Presedennya ada di [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] yang memberi kriteria kapan sebuah alur pantas punya koleksi sendiri, dan di [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]] yang sudah live sebagai contoh tiket menyeberang departemen.

⚠️ Dasar regulatif untuk keluhan efek samping **tidak ada di vault**. Dok CPOB dan [[QA - Deviation & CAPA]] keduanya masih berstatus stub, enum sumber CAPA tidak memuat keluhan pelanggan, dan rulebook vault melarang mengarang konten regulatif. Keputusan ini berdiri di atas kekosongan itu dan menanganinya dengan menahan satu kategori, bukan dengan menebak.

## Decision

1. **Perluas register komplain yang ada; jangan buat koleksi tiket baru.** Kriteria [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] tidak terpenuhi di sini: tidak ada penjaga struktural yang menghalangi, kosakata statusnya sama persis (diajukan lalu divalidasi), dan yang berbeda hanya siapa validatornya, yang merupakan satu field gerbang. ADR yang sama menutup dengan peringatan bahwa dua definisi "tiket" dalam satu service sudah terbukti berbahaya, dan membuat definisi ketiga akan mengulanginya.

2. **Kategori keluhan jadi master data, bukan konstanta.** Bentuknya mengikuti master `ComplianceViolationType` yang sudah ada: `key`, `label`, `order`, `active`, `metadata`, dengan normalisasi key. Tiap baris membawa **penindak internalnya** dan **pihak luar** yang terkait. Pemetaan kategori ke tujuan hidup **hanya di sini**; menyalinnya ke frontend akan menyimpang diam-diam dan gagalnya berupa tiket yang mendarat di departemen yang salah.

3. **Departemen penerima diturunkan dari `department_shops`**, yaitu satu toko satu departemen, bukan dari pemetaan orang ke akun. Keduanya menjawab pertanyaan berbeda, dan menukarnya menilai orang dengan angka yang bukan tanggung jawabnya.

4. **Isi ulasan DISALIN ke dalam komplain, bukan ditautkan lewat id saja.** Ulasan tinggal di `integration_db` dan komplain di `employee_db`, dan aturan database-per-service melarang service komplain membaca database tetangganya. Salinan bertanggal juga yang benar secara makna: ia bukti, bukan data hidup, dan ulasan yang kelak disembunyikan atau disunting tidak boleh mengubah dasar sebuah komplain yang sudah diajukan.

5. **Kategori dipilih manusia.** Tidak ada klasifikasi otomatis, tidak ada LLM. Volumenya 3 sampai 4 per bulan. Saran kata kunci boleh ditampilkan sebagai bantuan, tetapi yang tersimpan adalah pilihan orang.

6. **Ekspedisi dan marketplace disatukan sebagai satu pihak luar.** Kurir pada ulasan didominasi SPX, yang merupakan layanan Shopee sendiri, jadi memisahkan keduanya memaksa pengaju menebak perbedaan yang tidak ada di lapangan.

7. **Nama kurir diisi otomatis dari `shopee_order_details.shipping_carrier`**, bukan dari `transaction_orders`. Yang pertama terisi 104.385 dari 109.520 baris; yang kedua tidak memiliki field itu sama sekali dan memakai `shipping_provider` yang lebih jarang terisi. Seluruh ulasan membawa `order_sn`, dan penjodohan ke order berhasil pada 116 dari 120 sampel.

8. **Kata "Valid" diganti.** Begitu tujuannya lebih dari satu, "Valid" menjadi ambigu karena tidak menyebut valid menurut siapa. Vonis penerima menjadi tiga: diakui, bukan dari kami, dan **dialihkan**. Pilihan ketiga itu wajib ada karena pengaju menebak tujuan dari kalimat pembeli, sementara pembeli tidak tahu apakah masalahnya gudang atau QC; tanpa pengalihan, tiket salah alamat mati sebagai penolakan dan masalah aslinya tidak pernah sampai ke siapa pun.

9. **Penerima wajib menuliskan tindakan dan tanggalnya sebelum menutup.** Tanpa itu, "diakui" hanyalah pengakuan salah yang tidak mengubah apa pun, dan itu keadaan yang berlaku hari ini.

10. **Notifikasi mengikuti pola dua kategori yang sudah dipakai**, yaitu satu ke penerima saat diajukan dan satu ke pengaju saat diputuskan, disalurkan lewat fan-out terpusat sesuai [[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]]. Ditambah satu pemicu baru: ulasan berbintang rendah memberi tahu pemegang tokonya.

11. **Tanpa tenggat dan tanpa SLA untuk sekarang.** SLA yang sudah ada di sistem berasal dari marketplace dan punya penegak di luar; alur internal ini tidak punya. Angka tenggat yang ditebak dari 3 tiket sebulan akan meleset di kedua arah. Yang dicatat cukup kapan tiket masuk dan kapan ditutup, sehingga tenggatnya kelak dapat diturunkan dari data sendiri.

12. **Hanya Shopee.** Dinyatakan terang di layar, bukan dibiarkan terlihat seperti kelalaian.

13. **Dua utang ditutup sebagai bagian pekerjaan ini, bukan diwariskan**: `QualityComplaint` yang tidak menyimpan `company_id`, dan race `ReplaceOne` berfilter `_id` saja yang dapat mengembalikan status ke "menunggu" tanpa pesan. Memperluas register ke banyak departemen memperbesar keduanya.

14. **Kategori dugaan efek tidak diinginkan DITAHAN** sampai tim QA/RA menyatakan apakah keluhan semacam itu wajib masuk jalur CAPA atau pelaporan BPOM. Kategori lain boleh jalan lebih dulu.

## Consequences

**Yang membaik.** Keluhan operasional sampai ke unit yang bisa memperbaikinya, dan untuk pertama kalinya ada jejak bahwa kesalahan yang sama berulang. Pemegang toko tidak lagi bergantung pada kebiasaan membuka Seller Center. Sebagian besar pekerjaan memakai ulang yang sudah berdiri, sehingga permukaan barunya kecil.

**Yang memburuk, dan diterima sadar.** Koleksi yang namanya menyebut mutu akan memuat komplain gudang. Ini harga dari tidak membuat definisi tiket ketiga, dan ia dibayar dengan penamaan field serta label layar yang jujur, bukan dengan mengganti nama koleksi yang sudah dipakai produksi.

**Yang tetap terbuka.** Siapa penindak internal untuk keluhan pengiriman lama belum diputuskan, sebab tidak ada departemen ekspedisi di sistem. Lima toko Beauty Hacks tidak punya CS sama sekali, dan itu temuan operasional yang berdiri sendiri. Kewajiban regulatif atas keluhan efek samping menunggu QA/RA.

**Konsekuensi deploy.** Kategori inbox baru menuntut employee-service dan notification-service naik bersama, dengan notification-service lebih dulu, karena keduanya memegang salinan daftar-izin kategori dan kategori yang tak dikenal ditolak tanpa suara. Tidak ada env baru. Bentuk respons komplain berubah, jadi backend naik sebelum frontend.

**Dokumen terkait**: [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]] · [[Microservices - Integration Service]] · [[Microservices - Notification Service]] · [[Microservices - Employee Service]] · [[APP - Web ERP]] · [[Sales - ICC Account Manager Mapping]] · [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] · [[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]] · [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]] · [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]]
