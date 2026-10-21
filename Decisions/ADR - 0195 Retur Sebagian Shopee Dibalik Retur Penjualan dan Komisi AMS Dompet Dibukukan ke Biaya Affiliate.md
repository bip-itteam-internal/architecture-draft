> **Status**: 🟢 **Diterima, 2026-10-21, oleh bagusizzanm** (Pemutus; instruksi "lanjut kerjakan perbaikan yang finance butuhkan" sesudah ADR disajikan lengkap). **Belum ada kode** (issue bip-erp#3397 dan #3398). Bagian retur sebagian berdiri di atas butir 🟡 keputusan pemilik 2026-08-05 di ADR 0024, yang belum pernah masuk kode.

## Untuk Manajemen

**Apa yang berubah.** Dua hal di penerimaan marketplace Shopee, keduanya berlaku mulai penerimaan 1 Oktober 2026.

1. **Retur sebagian.** Pembeli membeli 2 pcs, 1 pcs diretur dan uangnya tetap cair. Hari ini penerimaan tetap mencatat 2 pcs senilai Rp184.000, dan nilai refund menumpuk di Biaya Admin (contoh `INC/2026/10/17/008-BH`: Biaya Admin Rp128.652, padahal fee aslinya sekitar Rp16 ribu). Sesudah perubahan, faktur tetap, dibuat dokumen **Retur Penjualan** untuk pcs yang diretur (Rp92.000), dan penerimaan hanya melunasi pcs yang tersisa (Rp92.000). Biaya Admin kembali berisi fee yang sebenarnya.
2. **Komisi AMS yang dipotong Shopee dari dompet.** Potongan ini sekarang tidak masuk ERP sama sekali, sehingga kas toko di ERP lebih besar dari Saldo Penjual Shopee (99 potongan, Rp1.136.138 pada 12–13 Oktober). Sesudah perubahan, potongan itu dibukukan sebagai **Biaya Affiliate** di penerimaan hari dipotongnya, satu baris per toko per hari, dengan rincian per pesanan di ekspor.

**Siapa yang terdampak.** Tim AR/finance yang merekonsiliasi penerimaan dengan mutasi Shopee, dan accounting yang membaca laporan penjualan dan retur (retur sebagian kini muncul sebagai dokumen retur).

**Yang tidak dijanjikan.**
- **Periode yang sudah tutup buku tidak disentuh.** September (14 order retur sebagian, refund Rp1,2 juta) dan sebelumnya tetap seperti sekarang.
- Retur TikTok dan Lazada tidak berubah.
- Retur yang sudah diterima tetapi belum dikurangkan di escrow Shopee (6 order terukur) memakai jalur yang berbeda dan tidak ikut diubah di sini.
- Penerimaan sebelum 1 Oktober tidak ditulis ulang otomatis.

**Besaran kerja.** Sedang: dua perubahan di satu service (`bip-erp` integration-service), dua isian tanggal baru di layar Config Accurate, tanpa perubahan layar. Retur sebagian wajib berubah serentak di dua sisi dalam satu deploy.

## Deskripsi

*Retur sebagian Shopee yang uangnya tetap cair (payout > 0) dibalik lewat dokumen Retur Penjualan per qty yang diretur, dan penerimaan hanya melunasi qty sisa. Komisi AMS yang dipotong dari dompet Shopee (`AMS_COMMISSION_FEE_DEDUCT`) dibukukan ke akun Biaya Affiliate. Keduanya digerbangi kv tanggal per hari penerimaan.*

- **Status**: lihat blockquote di baris pertama dokumen ini. Bagian retur sebagian berdiri di atas butir 🟡 "nilai barang selalu via retur" di [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] (keputusan pemilik 2026-08-05, belum pernah masuk kode), dan ADR ini yang menjadikannya terimplementasi untuk Shopee retur sebagian.
- **Path di repo** (yang akan disentuh): `bip-erp/services/integration/internal/domain/entity/shopee.go` (`refundShopee`, `normalizeShopeeIncomeIdentity`) · `internal/usecase/accurate_rts_usecase.go` (`returnPayoutGate`) · `internal/usecase/accurate_receipt_export_detail.go` (`receiptOrderPorsi`) · `internal/usecase/accurate_receipt_export_rekap.go` (`klasifikasiJenisOrder`) · `internal/usecase/accurate_receipt_usecase.go` (`buildReceiptPayload`) · `internal/usecase/accurate_receipt_wallet_adjustment.go` (`splitWalletAdjustments`, `applyWalletAdjustments`) · `internal/usecase/receipt_export_penyesuaian.go` · `internal/domain/entity/accurate.go` (dua kv tanggal baru, `shopee-retur-sebagian-cutover-date` dan `shopee-ams-wallet-cutover-date`) **(baru)**
- **Tanggal**: 2026-10-21
- **Permintaan**: sheet "CEK REKON" tab CEK (finance AR, 2026-10-21); butir 1 retur sebagian, butir 2 biaya affiliate yang hanya ada di mutasi.

## Context

### Retur sebagian

Order `261010944296TR` (Bumble beauty): 2 pcs PJB-006 @Rp92.000, 1 pcs diretur refund-only (solution 1), dicairkan 17 Oktober 2026 (`INC/2026/10/17/008-BH`). Escrow Shopee mengirim `order_original_price` 184.000, `order_discounted_price` 91.999, `seller_return_refund` −92.001, `drc_adjustable_refund` +71.385, `voucher_from_shopee` 20.614, dan `escrow_amount` 75.504 (= 91.999 − komisi 7.590 − biaya pemrosesan 625 − layanan 7.820 − PPh 460).

Penyebab, tiga lapis (terukur prod dan dibaca dari `origin/main`, 2026-10-21):

1. **Refund yang terbaca salah.** ERP menjumlahkan `seller_return_refund` dan `drc_adjustable_refund`, hasilnya −20.616, padahal escrow hanya memakai yang pertama. Dengan refund = −`seller_return_refund` (sebagai beban positif 92.001), identitas `184.000 − (16.495 + 92.001) − 75.504` tepat 0. Dengan angka sekarang, selisih Rp112.617 jatuh ke residual (`total_adjustment`) dan dibukukan ke akun `settlement-adjustment` = Biaya Admin 6112: 7.820 + 8.215 + 112.617 = **128.652**, persis angka di sheet.
2. **Retur dilewati.** Penerimaan hanya memakai harga faktur penuh (184.000) tanpa mengurangi qty retur, dan dokumen Retur Penjualan di-SKIP oleh gerbang payout ("payout 75504>0, refund ditangani Auto Sync Income") karena `TotalRefund` ≠ 0. Gerbang itu tidak membaca `Partial`, `Solution`, maupun `ReturnedQuantity`, padahal ketiganya sudah tersimpan.
3. **Ekspor rekap** menampilkan Harga (Accurate) = harga faktur penuh dengan sengaja ("tidak dikurangi retur: pembalikan dicatat di dokumen Retur Penjualan tersendiri"), jadi begitu retur tidak dibukukan, angka itu terbaca salah.

**Luasnya.** Sejak 1 September ada 22 order Shopee berstatus retur diterima dengan payout positif (14 pada September, 8 pada Oktober). Dari 22 itu, 15 memakai pola di atas (refund di escrow, residual besar); setelah rumus refund dibetulkan, residual 15 order itu tinggal ≤ Rp2.750 (biaya lain yang memang tak dipetakan: Rp350 dan Rp2.750). Sekitar Rp1,39 juta refund sejak 1 September terbukukan sebagai residual Biaya Admin. Tujuh order lain tidak punya refund di escrow dan lewat jalur berbeda.

**Jebakan kolom (wajib tertulis).** Untuk Shopee, `SubtotalAfterSellerDiscount` = `order_discounted_price`, yaitu nilai **sesudah** retur (91.999), sedangkan klasifikasi jenis order memakainya seperti subtotal sebelum retur (gaya TikTok). Bila refund diubah ke −92.001 tanpa membetulkan klasifikasi, order terbaca "Retur Penuh", base-nya jadi nol, dan penerimaan gagal balance. Tiga kolom lain: `TotalRefund` komponen identitas; `TotalAdjustment` residual identitas (bukan komponen mandiri); `TotalOrderAdjustment` sudah terkandung di settlement.

**Yang sudah ada.** Pola retur penuh (refund dikeluarkan dari identitas, base dinolkan), data retur per qty, Retur Penjualan per `ReturnedQuantity × harga faktur` dan mode NOT_RETURNED/RETURNED, opsi transform income bergerbang kv tanggal, dan keputusan finance 2026-08-31 bahwa penerimaan mengurus kas dan alokasi piutang sedangkan pendapatan dan stok dibalik Retur Penjualan.

### Komisi AMS

Mutasi dompet `AMS_COMMISSION_FEE_DEDUCT` ("Pemotongan biaya komisi AMS untuk Pesanan …") tidak punya aturan pembukuan: ia jatuh ke "tipe tak dikenal", hanya dilaporkan lewat notifikasi, dan tidak dibukukan. Sensus prod: **99 mutasi, −Rp1.136.138, seluruhnya 12–13 Oktober** (59 di Beautyhack's Original Shop = −Rp908.333, persis sheet; sisa 40 = −Rp227.805 di empat toko lain yang belum ada di sheet). Shopee memotongnya sekitar dua minggu setelah uang cair (order 24–29 September). **99 dari 99 order tidak punya komisi AMS di escrow maupun income**, jadi mutasi ini bukan duplikat komisi yang sudah dibukukan lewat escrow. Pengembalian komisi AMS yang positif (`ADJUSTMENT_CENTER_ADD`) sudah dibukukan lewat jalur kompensasi, sehingga yang negatif tidak simetris. Akun Biaya Affiliate sudah ada (kv `affiliate-commision`) dan dipakai komisi AMS dari escrow.

Vault tidak punya keputusan finance sebelumnya untuk tipe ini; jenis dompet tak dikenal sengaja tidak ditebak akunnya. Permintaan finance (biaya affiliate yang hanya ada di mutasi) dan keputusan Pemutus 2026-10-21 memilih akun Biaya Affiliate.

### Tutup buku

Bulan M ditutup tanggal 3 bulan M+1, 23:59 WIB ([[ADR - 0152 FO yang Dilaporkan Sesudah Uang Cair Mengecilkan atau Menghapus INC, FO Tidak Masuk Penjualan]], [[ADR - 0174 Keputusan Beda dengan Accurate Dibuat di Penyesuaian, Isi Accurate Diterima untuk Periode Tutup Buku]]). Penerimaan dalam jendela pindai 45 hari ditulis ulang otomatis begitu isi barisnya berubah, termasuk yang sudah SENT. Karena itu kedua perubahan digerbangi tanggal, mengikuti pola `tiktok-kompensasi-cutover-date` ([[ADR - 0119 Kompensasi TikTok Dipisah Menurut Sudah atau Belum Ada Uang Masuk]]).

## Decision

1. **Retur sebagian Shopee yang uangnya tetap cair dibalik dengan Retur Penjualan.** Syarat: order Shopee, retur diterima, payout > 0, dan sebagian (`order_discounted_price` > 0 dengan `seller_return_refund` ≠ 0). Retur Penjualan dibukukan per qty diretur × harga faktur, mode NOT_RETURNED untuk refund-only dan RETURNED untuk barang balik (barang balik tetap menunggu scan gudang, [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]).
2. **Penerimaan hanya melunasi qty sisa.** Base per order = harga faktur × (qty − qty diretur). Refund tidak lagi jatuh ke akun Potongan Penjualan 4003. Di identitas income, refund retur sebagian dihitung dari `seller_return_refund` (nilai retur yang sebenarnya), `drc_adjustable_refund` tidak ikut. Residual setelah itu hanya sisa biaya lain.
3. **Klasifikasi jenis order dibetulkan serentak** supaya `SubtotalAfterSellerDiscount` Shopee (nilai sesudah retur) tidak lagi membuat retur sebagian terbaca "Retur Penuh". Nilai dan tanda `TotalRefund` yang tersimpan tidak diubah tanpa itu.
4. **Dua sisi berubah dalam satu perubahan dan satu deploy** (gerbang retur dan sisi penerimaan). Salah satu saja berarti pembalikan ganda (Retur 92.000 ditambah penerimaan yang masih membayar 184.000) atau penjualan yang tak pernah terbalik, dua-duanya senyap.
5. **Digerbangi kv `shopee-retur-sebagian-cutover-date`** (format `YYYY-MM-DD`, hari penerimaan WIB pertama). Kosong atau format salah: perilaku lama persis. Nilainya **tidak boleh mundur sebelum 2026-10-01**. Retur yang tanggal dokumennya (tanggal refund diminta) sebelum batas tidak dibukukan otomatis; barisnya tetap SKIPPED sebagai jejak. Terdaftar di katalog kv tanggal, jadi diisi dari layar Config Accurate.
6. **Komisi AMS dompet dibukukan ke Biaya Affiliate.** Tipe `AMS_COMMISSION_FEE_DEDUCT` menjadi kategori sendiri: satu baris per toko per hari ke akun kv `affiliate-commision`, mengikuti pola premi asuransi dan tagihan SBS (tidak per order di payload), dengan rincian per pesanan di ekspor sehingga jumlah baris sama dengan perubahan cheque. Hari yang hanya berisi potongan AMS (tanpa escrow) tetap diproses. Pengembalian AMS positif tetap lewat jalur kompensasi.
7. **Digerbangi kv `shopee-ams-wallet-cutover-date`**, aturan sama seperti butir 5, juga tidak mundur sebelum 2026-10-01. Tanpa kv baru, semua hari sejak kv penyesuaian dompet (2026-07-01) dalam jendela 45 hari akan ikut tertulis ulang.
8. **Basis nilai retur** adalah harga faktur (bukan angka dompet atau escrow); selisih Rp1 seperti 92.001 lawan 92.000 diserap residual.
9. **Lingkup Shopee saja.** TikTok dan Lazada tidak berubah; retur sebagian TikTok sudah diserap Potongan Penjualan dengan identitas yang benar, dan keputusan menyeragamkannya ditinjau terpisah.

## Consequences

- **Test yang mengunci perilaku lama akan merah** sampai diubah sadar, antara lain test identitas retur sebagian (residual 60.000), test refund ganda (−23.349), test settle-minus bentuk lama, test gerbang retur Shopee (`TotalRefund −14352` ⇒ SKIP), test klasifikasi rekap, dan test katalog kv (jumlah katalog tanggal dan himpunan kunci yang boleh ditulis).
- **Penerimaan Oktober yang sudah SENT ditulis ulang otomatis** (komposisi baris berubah) begitu kv diisi; finance perlu diberi tahu dan dokumen baru Retur Penjualan akan muncul untuk order Oktober (8 order, refund Rp628.576 sejak 1 Oktober). Bukan perubahan nilai kas: cheque tidak bergeser, hanya klasifikasinya.
- **Pembalikan ganda** adalah risiko utama bila gerbang retur dan sisi penerimaan tidak berubah bersama; test harus mengunci keduanya terhadap pembeda yang sama.
- **Deploy**: satu service (integration), tanpa env baru, tanpa perubahan kontrak ke frontend, tanpa kategori inbox baru. Dua kv diisi lewat layar Config Accurate. `integration-service` hanya di-recreate saat `worker_locks` kosong (jangan memotong putaran sinkron penerimaan). Prod dijalankan manusia.
- **Verifikasi sesudah deploy** bukan "kode sudah naik" melainkan hasil akhirnya: `INC/2026/10/17/008-BH` memuat Bayar faktur Rp92.000, Biaya Admin sekitar Rp16.035, dan ada Retur Penjualan Rp92.000 NOT_RETURNED; mutasi AMS 12–13 Oktober (99, −Rp1.136.138) tampil di Biaya Affiliate, dengan jumlah per toko cocok sheet (Beautyhack's Original Shop −Rp908.333).
- **Tidak menyelesaikan**: tutup buku faktur ([[Microservices - Integration Service]] § Faktur harian tanpa gerbang tutup buku), tujuh order retur-diterima yang escrow-nya belum mengurangi refund, dan penerimaan FAILED yang macet.

## Dokumen Terkait

- [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] · [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]] · [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] · [[ADR - 0040 Retur Paket Utuh via Baris Induk Faktur]] · [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]
- [[ADR - 0119 Kompensasi TikTok Dipisah Menurut Sudah atau Belum Ada Uang Masuk]] · [[ADR - 0152 FO yang Dilaporkan Sesudah Uang Cair Mengecilkan atau Menghapus INC, FO Tidak Masuk Penjualan]] · [[ADR - 0174 Keputusan Beda dengan Accurate Dibuat di Penyesuaian, Isi Accurate Diterima untuk Periode Tutup Buku]]
- [[Microservices - Integration Service]] · [[Finance - Pemetaan Komponen Marketplace ke Akun Accurate]] · [[Finance - Proses Retur dan Piutang Marketplace]] · [[Finance - Proses Penjualan Marketplace dan Uang Masuk]]
