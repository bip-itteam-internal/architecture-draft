## Untuk Manajemen

Kompensasi TikTok atas pesanan yang uangnya **sudah pernah cair** tidak lagi menambah nilai bayar faktur — fakturnya sudah lunas, jadi menambahnya berarti membayar dua kali. Mulai perubahan ini, kompensasi semacam itu dicatat sebagai **Pendapatan Lain-lain tanpa mengisi nilai bayar**, dan **dokumen retur pesanan itu tetap dibukukan** karena sekarang dialah satu-satunya yang membalik penjualan dan mengembalikan stok. Untuk pesanan yang **belum pernah menerima uang** (pesanan batal, paket hilang di logistik), perlakuannya **tidak berubah**: kompensasi tetap yang melunasi fakturnya.

Terukur di produksi 22 September 2026: **14 pesanan senilai Rp1.610.697** yang perlu dibetulkan, berhadapan dengan **360 pesanan senilai Rp34.872.894** yang sudah benar dan tidak disentuh. **Terdampak**: tim AR/finance yang menelusuri piutang minus dan kompensasi TikTok. **Yang TIDAK dijanjikan**: membetulkan dokumen yang sudah terbit (berlaku maju saja), membereskan retur lama yang menggantung menunggu scan gudang, mengubah aturan kanal Shopee, dan menyediakan tuas koreksi untuk pemindahan pelunasan yang hari ini masih ditolak sistem. **Besaran kerja**: sedang — kecil di nominal, tetapi dua tempat harus berubah bersamaan.

## Deskripsi

*Penyesuaian statement TikTok dipisah oleh **satu pembeda**: pesanannya sudah pernah menerima uang atau belum. Belum pernah → kompensasi melunasi faktur (perilaku sekarang, dari [[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]]). Sudah pernah → kompensasi jadi baris Pendapatan Lain-lain tanpa menyentuh bayar faktur, dan gerbang retur ikut memakai pembeda yang sama sehingga returnya kembali dibukukan.*

- **Status**: 🟡 **Diusulkan** — belum ada di kode. Aturannya sudah diputuskan finance (tiket "Revisi Sistem Income" + penegasan staf finance 2026-09-22); populasinya diukur ke prod 2026-09-22.
- **Path di repo**: `bip-erp/services/integration/internal/infrastructure/repository/transaction_repo.go` (`ListOrdersByTiktokStatement`) · `internal/usecase/accurate_receipt_usecase.go` · `internal/usecase/accurate_rts_usecase.go` (`returnPayoutGate`, `diserapPenyesuaianStatement`) · `internal/usecase/accurate_receipt_kompensasi_tiktok_test.go` **(baru)**
- **Tanggal**: 2026-09-22

## Context

### Aturan yang finance tetapkan

Ditanyakan langsung dan dijawab 22 September 2026, dengan pembeda yang sangat sederhana:

> Kalau pesanannya **belum pernah ada uang masuk** → kompensasi dicatat seperti income biasa. Kalau **sudah pernah ada uang masuk** → dicatat sebagai **Pendapatan Lain-lain**, dan **tidak mengisi nilai bayar**.

Ditambah tiga penegasan: **dokumen retur tetap dicatat**; berlaku **sekarang dan ke depan** (bukan mundur); dan aturan ini **untuk TikTok saja**.

### Kenapa ini bukan pembatalan ADR-0056, melainkan penyempitannya

[[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]] memutuskan kompensasi **melipat ke payout pesanan**, dan secara eksplisit **menolak** alternatif "Pendapatan Lain-lain terpisah". Penolakan itu berdasar: populasinya pesanan **batal** yang fakturnya tak pernah dibayar pembeli, sehingga kompensasi itulah satu-satunya yang melunasinya, dan hasilnya sudah dicocokkan ke hitungan manual finance.

Populasi tiket ini **berbeda**: pesanan cair normal lebih dulu, kompensasi datang belakangan. Diukur di prod atas seluruh 428 pesanan berkompensasi:

| Populasi | Pesanan | Nilai | Keadaan |
|---|---|---|---|
| **Sudah** ada uang masuk | **14** | **Rp1.610.697** | populasi tiket — salah hari ini |
| **Belum** ada uang masuk | 360 | Rp34.872.894 | populasi ADR-0056 — sudah benar |
| tak ada padanan pesanan | 54 | — | di luar lingkup, dicatat di bawah |

Contoh populasi tiket: `585616915329615127` berstatus COMPLETED dengan payout Rp74.679 lalu menerima kompensasi Rp94.500.

Menerapkan aturan baru menyeluruh **akan merusak 360 pesanan yang sudah benar** — faktur mereka tak punya pelunas lain. Karena itu yang berubah bukan keputusannya, melainkan batas populasinya.

### Aturan ini sudah berjalan di kanal Shopee

Jalur kompensasi Shopee sudah menerapkan pembeda yang sama: alokasi ke faktur **hanya** bila pesanan belum menerima uang; selebihnya satu baris ke akun pendapatan lain **tanpa menyentuh bayar faktur**, dengan alasan tertulis "mustahil dobel bayar karena tidak menyentuh Bayar faktur". TikTok tidak melewati jalur itu.

Jadi yang dikerjakan adalah **memindahkan aturan yang sudah teruji ke kanal kedua**, bukan merancang yang baru.

### Dua sisi, bukan satu — dan ini yang paling mudah terlewat

Gerbang retur hari ini men-**skip** pembukuan Retur Penjualan bila payout ditambah kompensasi melewati ambang, dengan alasan "penerimaan yang melunasi faktur". Gerbang itu **tidak membedakan** kedua populasi di atas.

Begitu kompensasi tak lagi melunasi faktur untuk populasi tiket, alasan skip itu **hilang** — tetapi returnya tetap ter-skip. Akibatnya penjualan **tidak terbalik sama sekali**: kebalikan dari dobel yang tiket ini hendak perbaiki, dan sama senyapnya. [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] sudah menuliskan peringatan bentuk ini ("dua tempat WAJIB berubah bersamaan"); ini kejadian yang sama dengan arah berlawanan.

### Cicilan kompensasi: diukur, bukan diasumsikan

Shopee menangani kompensasi bertahap lewat penahanan dan pencatatan manual AR ([[ADR - 0097 Kompensasi Shopee Susulan Ditahan dan Dicatat AR lewat Koreksi Manual ERP]]). Apakah TikTok perlu hal yang sama? Diukur: dari **428** pesanan berkompensasi, hanya **1** yang punya lebih dari satu baris penyesuaian. Membangun mekanisme penahanan untuk satu kejadian adalah permukaan yang tak sebanding.

## Decision

### 1. Satu pembeda: payout pesanan itu sendiri, sebelum kompensasi

- **Payout ≈ 0** (belum pernah ada uang masuk) → kompensasi **melipat ke payout** dan melunasi faktur. **Tidak berubah** dari sekarang.
- **Payout > 0** (sudah pernah ada uang masuk) → kompensasi jadi **baris Pendapatan Lain-lain**, **nilai bayar tidak diisi**.

Yang dinilai adalah payout pesanan itu sendiri, **bukan** payout ditambah kompensasinya — gerbang sekarang menjumlahkan keduanya, dan penjumlahan itulah yang membuat kedua populasi jatuh ke keputusan yang sama.

### 2. Gerbang retur memakai pembeda yang SAMA

- **Payout ≈ 0** → retur tetap **di-skip**; kompensasi yang melunasi faktur, membukukan retur berarti pembalikan dobel.
- **Payout > 0** → retur **tetap dibukukan**; sekarang dialah satu-satunya yang membalik penjualan dan stok.

### 3. Kedua sisi berubah dalam satu perubahan, tidak boleh dipisah

Menerapkan sisi penerimaan saja menghasilkan penjualan yang tak pernah terbalik; menerapkan sisi retur saja menghasilkan pembalikan dobel. Keduanya salah dan keduanya senyap. Satu PR, satu deploy, dan test yang mengunci **kedua** sisi terhadap pembeda yang sama.

### 4. Tidak dibuat penahanan cicilan seperti Shopee

Satu kejadian dari 428 tidak cukup untuk melahirkan antrean, laman, dan aturan akun tersendiri. Bila kelak jumlahnya tumbuh, keputusannya ditinjau ulang dengan angka baru — bukan diantisipasi sekarang.

### 5. Berlaku maju, dokumen terbit tidak disentuh

Sesuai arahan finance. Konsekuensinya diterima sadar: 14 pesanan yang sudah terlanjur tercatat keliru **tetap keliru** sampai ada keputusan terpisah untuk membetulkannya.

### 6. Hanya TikTok; aturan Shopee tidak ikut berubah

Finance menyatakannya eksplisit. Perbedaan yang tersisa dengan Shopee — kompensasi bertahap Shopee memilih akun menurut bulan, TikTok selalu Pendapatan Lain-lain — **dipertahankan sadar dan dicatat di sini**, supaya tidak terbaca sebagai ketidaksengajaan oleh yang membacanya nanti.

## Consequences

- **Nominalnya kecil, kelas kesalahannya tidak.** Rp1,6 juta di 14 pesanan, tetapi bentuknya piutang minus dan uang yang tak terbukukan — dua hal yang mahal ditelusuri AR dan tidak pernah muncul sebagai galat.
- **Sebagian retur yang kembali dibukukan akan tertahan menunggu scan gudang.** Itu benar dan memang dikehendaki per [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]], bukan kemunduran.
- **Tidak menyelesaikan tuas koreksi pemindahan pelunasan ke akun GL.** Kasus prod yang tertolak karena penerjemah koreksi hanya mengenal geser-antar-faktur dan tambah-uang tetap terbuka; lihat [[ADR - 0100 Penerimaan Beda dengan Accurate Diputus di Halaman Penerimaan]]. Task terpisah.
- **Yang tetap terbuka**: retur lama yang menggantung menunggu barang yang takkan datang; **54** penyesuaian tanpa pesanan padanan (naik dari 7 yang tercatat saat ADR-0056 ditulis — kenaikannya belum ditelusuri); dan 14 pesanan yang sudah terlanjur salah.
- **Deploy**: satu service (integration), tanpa env baru, tanpa perubahan kontrak ke frontend. Eksekusi prod dijalankan manusia.

## Dokumen Terkait

- [[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]] — keputusan yang dipersempit di sini, bukan dibatalkan
- [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] — gerbang retur yang ikut berubah
- [[ADR - 0097 Kompensasi Shopee Susulan Ditahan dan Dicatat AR lewat Koreksi Manual ERP]] — aturan kanal sebelah yang sengaja TIDAK disamakan
- [[ADR - 0100 Penerimaan Beda dengan Accurate Diputus di Halaman Penerimaan]] — tuas koreksi yang belum ada
- [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] — gerbang gudang untuk retur barang-balik
- [[Microservices - Integration Service]] — Auto Sync Income & Auto-Sync Retur
- [[Finance - Proses Retur dan Piutang Marketplace]] — proses bisnis yang menaungi
