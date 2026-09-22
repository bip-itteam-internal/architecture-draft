## Untuk Manajemen

Pada sebagian pesanan Shopee, biaya ongkir yang tercatat di pembukuan **lebih besar** daripada yang ditampilkan Shopee, dan kelebihannya mendarat di akun **Beban Admin E-Commerce**. Contoh yang finance laporkan: Shopee menampilkan Subtotal Ongkos Kirim **Rp0**, sistem mencatat **Rp112.000**. Terukur di produksi 22 September 2026: **3.865 pesanan, Rp98.260.427**, dan masih bertambah sekitar **Rp16 juta per bulan**. Uang yang diterima **tidak berubah sepeser pun** — yang salah pembagiannya antar dua akun, sehingga totalnya selalu tetap seimbang dan tak pernah memunculkan pesan galat.

**Terdampak**: tim FAT/AR yang mencocokkan akun ongkir dan admin ke Accurate, serta kolom ongkir di Rekap Pencairan. **Yang TIDAK dijanjikan**: membetulkan dokumen yang sudah terbit (berlaku maju saja, sesuai arahan finance "sekarang dan ke depan"), mengubah nilai uang masuk, menyentuh TikTok/Lazada, dan menyelesaikan 96 pesanan menyimpang yang belum terjelaskan. **Besaran kerja**: kecil sampai sedang; perubahan hitungannya satu tempat, ongkos sebenarnya ada di penerapan bertanggal dan pembuktiannya.

## Deskripsi

*Beban ongkir Shopee dihitung dari **ongkir aktual dikurangi bagian yang dibayar pembeli dan subsidi Shopee** — mengikuti definisi resmi Shopee — menggantikan rumus lama yang memasangkan `final_shipping_fee` dengan `buyer_paid_shipping_fee`. Keduanya bukan komponen sejajar: di data produksi `final_shipping_fee` bernilai tepat negatif dari bagian pembeli, sehingga memasangkannya membuat bagian pembeli hilang dari perhitungan.*

- **Status**: 🟡 **Diusulkan** — belum ada di kode. Keputusan finance atas gejalanya sudah ada (tiket "Revisi Sistem Income"); rumus penggantinya diukur ke prod 2026-09-22 dan belum diimplementasi.
- **Path di repo**: `bip-erp/services/integration/internal/domain/entity/shopee.go` (`TransformToOrderIncomeWithAdjustment`) · `internal/usecase/receipt_rebate_ongkir.go` (saklar tanggal) · `internal/domain/entity/income_identity_test.go` (fixture diperbaiki) · `internal/domain/entity/shopee_ongkir_test.go` **(baru)**
- **Tanggal**: 2026-09-22

## Context

### Gejala yang dilaporkan, dan sebab yang ditulis di tiket ternyata keliru

Tiket finance melaporkan: saat muncul baris "Potongan Ongkos Kirim dari Shopee", sistem berhenti menjumlahkan "Ongkir Dibayar Pembeli". Contohnya pesanan dengan Ongkir Dibayar Pembeli Rp112.000, Ongkos Kirim ke Jasa Kirim −Rp127.000, Potongan dari Shopee Rp15.000 — Subtotal Ongkos Kirim menurut Shopee **Rp0**, terbaca sistem **−Rp112.000**.

Gejalanya nyata, tapi **sebabnya tidak mungkin seperti yang ditulis**: rumus ongkir di kode tidak punya percabangan sama sekali terhadap ada-tidaknya baris potongan. Menerima sebab itu apa adanya akan menghasilkan perbaikan yang menambal percabangan yang tak pernah ada.

### Sebab sebenarnya, diukur ke produksi

Rumus sekarang: `−(final_shipping_fee + buyer_paid_shipping_fee) + actual_shipping_fee + proteksi`.

Diukur atas seluruh 90.139 dokumen escrow di prod (22 September 2026):

| Keadaan | Jumlah | Σ \|final\| |
|---|---|---|
| `actual` terisi, `final` = 0 | 86.147 | 0 — rumus sekarang **benar** |
| `actual` terisi, `final` terisi | **3.865** | **Rp98.260.427** — kelas yang salah |
| keduanya 0 | 130 | 0 |

Pada **3.769 dari 3.865** (97,5%) kelas bermasalah, `final_shipping_fee` bernilai **tepat negatif dari `buyer_paid_shipping_fee`**. Karena itu suku `−(final + buyer)` saling meniadakan jadi nol, dan akun ongkir menerima `aktual − subsidi` alih-alih `aktual − bagian pembeli − subsidi`. Selisihnya secara aljabar **tepat sebesar `final`**, yaitu sebesar bagian yang dibayar pembeli.

Contoh nyata dari prod: `260611SESSAEPU` (pembeli 23.300 · final −23.300 · aktual 38.300 · subsidi 15.000) dan `260612T9TYCNTA` (pembeli 1.000 · final −1.000 · aktual 61.000 · subsidi 60.000).

### Rumus resmi Shopee, diuji ke populasi yang sama

Dokumentasi `payment.get_escrow_detail` menyatakan (pada keterangan `shipping_fee_sst`): *Seller Paid Shipping Fee = Actual Shipping Fee − (Shipping Fee Paid by Buyer + Shipping Rebate From Shopee)*.

Diuji: rumus itu menghasilkan **tepat nol pada 3.769 pesanan** yang sama — yaitu persis angka "Subtotal Ongkos Kirim" yang finance tunjukkan di layar Shopee. Rumus lama hanya benar bila `final` kebetulan nol.

### Kenapa bertahun-tahun tak berbunyi

Dua lapis yang saling menutupi:

1. **Identitas selalu ditutup sendiri.** Komponen yang tak terpetakan ditambahkan ke residual penyesuaian sehingga dokumen selalu balance. Kesalahannya tak pernah berbentuk galat, hanya angka yang masuk akal.
2. **Residual dan biaya admin memakai akun yang sama** (kunci `settlement-adjustment` dan `service-fee` sama-sama menunjuk akun admin), jadi selisihnya mendarat di beban admin tanpa kolom bernama.

### Penjaganya sendiri dibangun di atas fixture yang kehilangan field penentu

`TestShopeeTransformIncomeIdentity_RealSample` menyebut dirinya "sample REAL Shopee (angka live escrow)" dan mengunci beban ongkir = 0. Ditelusuri ke prod, fixture itu adalah pesanan **`260612TSWHH5PW`** — enam angkanya identik (original 99.000 · commission 7.755 · service 7.990 · buyer_tx 1.000 · voucher 5.000 · escrow 71.006). Tetapi fixture **tidak menyertakan `actual_shipping_fee`**, padahal pesanan aslinya bernilai **107.400**. Dengan field itu absen, rumus yang salah menghasilkan 0 dan test-nya hijau.

Ini bukan test yang lemah, melainkan test yang **fixture-nya kehilangan justru field yang membedakan benar dan salah** — kelas yang sama dengan "fixture yang menyamakan `_id` dan `shop_id`".

### Komponen lain yang ikut terperiksa

- **`reverse_shipping_fee`** (Ongkos Kirim Pengembalian Barang): **77 dokumen, Rp1.574.800**, tidak pernah masuk rumus ongkir mana pun — ikut mendarat di residual.
- **`shipping_fee_discount_from_3pl`** (Potongan Ongkos Kirim dari Jasa Kirim): **nol kejadian** di seluruh 90.139 dokumen. Sengaja **tidak** dimasukkan; menambah komponen yang tak pernah terisi hanya menambah permukaan tanpa manfaat.

## Decision

### 1. Beban ongkir mengikuti definisi resmi Shopee

Beban ongkir seller = **ongkir aktual − (bagian yang dibayar pembeli + subsidi Shopee)**, ditambah **biaya proteksi pengiriman** dan **ongkir pengembalian barang**.

`final_shipping_fee` **tidak dipakai sama sekali**. Ia bukan komponen sejajar melainkan cerminan bagian pembeli; memasangkannya dengan `buyer_paid_shipping_fee` adalah bentuk hitung-ganda yang saling meniadakan.

### 2. Berlaku maju lewat saklar tanggal, dokumen terbit tidak disentuh

Finance menyatakan "sekarang dan ke depan". Karena perubahan ini menggeser komposisi baris, dokumen penerimaan berstatus terkirim di dalam jendela pindai akan **diedit sendiri oleh penjadwal** bila tidak digerbang. Karena itu saklar tanggal **wajib**, mengikuti pola yang sudah terbukti pada perpindahan potongan ongkir ke akun ongkir: kosong berarti perilaku lama persis, dan satu penentu akun-per-hari dipasang di **seluruh** jalur (kirim, pratinjau, ekspor) supaya layar dan dokumen mustahil berselisih.

### 3. Residual Shopee diberi penjaga bernilai

Residual penyesuaian untuk pesanan Shopee yang melewati ambang dicatat sebagai peringatan **beserta nominalnya**, tidak diam. Tanpa ini, kelas "komponen ongkir yang kehilangan nama" akan terulang dan kembali hanya ketahuan dari layar finance berbulan-bulan kemudian — persis riwayat biaya proteksi pengiriman dan ongkir pengembalian.

### 4. Fixture diperbaiki, dan perbaikannya dikunci kontrol negatif

`actual_shipping_fee` yang sebenarnya dikembalikan ke fixture, dan ditambahkan kasus dari kelas bermasalah (pembeli 112.000 · aktual 127.000 · subsidi 15.000 → nol). Kontrol negatifnya: mengembalikan rumus lama harus membuat test itu **merah pada nilai ongkirnya**, bukan merah karena sebab lain.

### 5. 96 pesanan menyimpang tidak ikut diputuskan di sini

Sisa 3.865 − 3.769 = **96 pesanan** tidak mengikuti pola `final = −pembeli` dan belum terjelaskan. Rumus baru tetap berlaku seragam untuk mereka, tetapi **jumlah dan sebarannya wajib diukur sebelum saklar dinyalakan**. Menyatakan mereka "pasti ikut benar" tanpa melihat datanya adalah bentuk klaim yang berulang kali salah di layanan ini.

## Consequences

- **Kas tidak berubah sepeser pun.** Yang berpindah hanya komposisi baris antara akun ongkir dan akun admin; nilai penerimaan, alokasi ke faktur, dan uang diterima tetap.
- **Beban admin akan turun dan beban ongkir naik** pada pesanan terdampak — dan itu memang arah yang benar. Finance perlu diberi tahu supaya perubahan tren tidak terbaca sebagai anomali baru.
- **Tidak menggeser insentif.** Profit insentif hanya bersandar pada net settlement; beban ongkir masuk sebagai kolom informasi. Diperiksa langsung ke rumusnya, bukan disimpulkan.
- **Penerapannya menuntut urutan operasi, bukan sekadar deploy**: deploy dengan saklar kosong → ukur → nyalakan saklar per tanggal → beri tahu finance. Eksekusi prod dijalankan manusia.
- ⚠️ **Jebakan yang sudah terbukti dan belum diperbaiki**: mengulang kirim dokumen penerimaan yang **pernah** terkirim tetapi statusnya kini bukan terkirim dapat menarik keluar pelunasannya sendiri. Karena keputusan ini berlaku maju dan tidak menyentuh dokumen lama, jalur itu **tidak boleh** dipanggil sebagai bagian penerapan.
- **Yang tetap terbuka**: 96 pesanan menyimpang; dokumen yang terlanjur terbit dengan pembagian akun lama; dan kunci `settlement-adjustment` yang masih berbagi akun dengan biaya admin sehingga residual tetap tak bernama.

## Dokumen Terkait

- [[Microservices - Integration Service]] — Auto Sync Income, potongan ongkir Shopee, dan urutan operasi yang jadi preseden
- [[Finance - Proses Penjualan Marketplace dan Uang Masuk]] — proses bisnis yang menaungi angka ini
- [[ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance]] — arti akun admin vs ongkir, dan kenapa fee tak dikenal jatuh ke admin
- [[ADR - 0001 Akuntansi via Accurate]] — alasan pembukuan tidak dilakukan sendiri
- [[APP - Web ERP]] — layar Auto Sync Penerimaan dan Rekap Pencairan tempat hasilnya terlihat
