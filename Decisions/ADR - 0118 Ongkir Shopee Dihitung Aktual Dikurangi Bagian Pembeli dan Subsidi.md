## Untuk Manajemen

Pada sebagian pesanan Shopee, biaya ongkir yang tercatat di pembukuan **lebih besar** daripada yang ditampilkan Shopee, dan kelebihannya mendarat di akun **Beban Admin E-Commerce**. Contoh yang finance laporkan: Shopee menampilkan Subtotal Ongkos Kirim **Rp0**, sistem mencatat **Rp112.000**. Terukur di produksi 22 September 2026: **3.870 pesanan, Rp96.826.227**, dan masih bertambah sekitar **Rp16 juta per bulan**. Uang yang diterima **tidak berubah sepeser pun** — yang salah pembagiannya antar dua akun, sehingga totalnya selalu tetap seimbang dan tak pernah memunculkan pesan galat.

**Terdampak**: tim FAT/AR yang mencocokkan akun ongkir dan admin ke Accurate, serta kolom ongkir di Rekap Pencairan. **Yang TIDAK dijanjikan**: membetulkan dokumen yang sudah terbit (berlaku maju saja, sesuai arahan finance "sekarang dan ke depan"), mengubah nilai uang masuk, dan menyentuh TikTok/Lazada. **Besaran kerja**: kecil sampai sedang; perubahan hitungannya satu tempat, ongkos sebenarnya ada di penerapan bertanggal dan pembuktiannya.

## Deskripsi

*Beban ongkir Shopee dihitung dari **ongkir aktual dikurangi bagian yang dibayar pembeli**, ditambah biaya proteksi kirim dan ongkir pengembalian barang — menggantikan rumus lama yang memasangkan `final_shipping_fee` dengan `buyer_paid_shipping_fee` DAN `actual_shipping_fee` sekaligus. Subsidi Shopee (`shopee_shipping_rebate`) SENGAJA TIDAK ikut dikurangkan di rumus ini — ia tetap tinggal di `TotalOtherIncome`/`TotalShippingRebate` seperti sekarang, karena mekanisme "Potongan Ongkos Kirim dari Shopee" yang sudah berjalan menanganinya di lapisan penerimaan.*

- **Status**: 🟡 **Diusulkan, kode ditulis** — branch `fix/ongkir-shopee-rumus-resmi` (bip-erp), belum merge, belum deploy. Keputusan finance atas gejalanya ada di tiket "Revisi Sistem Income"; rumus dan dampaknya diukur ke prod 22 September 2026.
- **Path di repo**: `bip-erp/services/integration/internal/domain/entity/shopee.go` (`OpsiTransformShopee`, `TransformToOrderIncomeDenganOpsi`) · `internal/usecase/shopee_new_usecase.go` (`rumusOngkirBaruBerlaku`, `transformShopeeIncome`) · `internal/domain/entity/income_identity_test.go` (fixture diperbaiki) · `internal/domain/entity/shopee_ongkir_test.go` **(baru)** · `internal/usecase/shopee_new_usecase_ongkir_test.go` **(baru)**
- **Tanggal**: 2026-09-22

## Context

### Gejala yang dilaporkan, dan sebab yang ditulis di tiket ternyata keliru

Tiket finance melaporkan: saat muncul baris "Potongan Ongkos Kirim dari Shopee", sistem berhenti menjumlahkan "Ongkir Dibayar Pembeli". Contohnya pesanan dengan Ongkir Dibayar Pembeli Rp112.000, Ongkos Kirim ke Jasa Kirim −Rp127.000, Potongan dari Shopee Rp15.000 — Subtotal Ongkos Kirim menurut Shopee **Rp0**, terbaca sistem **−Rp112.000**.

Gejalanya nyata, tapi **sebabnya tidak mungkin seperti yang ditulis**: rumus ongkir di kode tidak punya percabangan sama sekali terhadap ada-tidaknya baris potongan. Menerima sebab itu apa adanya akan menghasilkan perbaikan yang menambal percabangan yang tak pernah ada.

### Sebab sebenarnya: `final_shipping_fee` murni cerminan aktual dan subsidi

Rumus lama: `−(final_shipping_fee + buyer_paid_shipping_fee) + actual_shipping_fee + proteksi`.

Diuji ke **seluruh 90.194 dokumen** escrow prod (22 September 2026), bukan sampel:

> `final_shipping_fee` == `−(actual_shipping_fee − shopee_shipping_rebate)` pada **90.194 dari 90.194 dokumen — 100%, nol pengecualian.**

`final_shipping_fee` bukan komponen independen — ia **Shopee sendiri yang menghitungnya** dari aktual dan subsidi. Rumus lama menjumlahkan `−final` (yang sudah memuat `aktual − subsidi` di dalamnya) **DAN** `actual_shipping_fee` mentah sekaligus, sehingga ongkir aktual terhitung **dua kali** untuk setiap pesanan yang final-nya bukan nol.

Kenapa mayoritas pesanan (86.324 dari 90.194) tak pernah kelihatan salah: pada pesanan itu `final_shipping_fee = 0` (subsidi menutup penuh ongkir aktual, pembeli tak menanggung apa pun), sehingga suku `−(final+buyer)` lenyap dan kebetulan menyisakan angka yang sama dengan rumus yang benar. Begitu `final` bukan nol, kebetulan itu berhenti berlaku.

### Rumus resmi Shopee, diuji ke populasi yang sama

Dokumentasi `payment.get_escrow_detail` menyatakan (pada keterangan `shipping_fee_sst`): *Seller Paid Shipping Fee = Actual Shipping Fee − (Shipping Fee Paid by Buyer + Shipping Rebate From Shopee)*.

Pengujian awal memakai rumus itu **apa adanya** (termasuk mengurangkan subsidi) sempat dianggap benar. **Dikoreksi saat implementasi (22 September 2026, hari yang sama):** test yang sedang HIJAU, `TestTransformToOrderIncome_TanpaProteksiKirimTakBerubah` (`actual_shipping_fee=3500`, `shopee_shipping_rebate=3500`, `buyer_paid=0`, mengunci `TotalShippingCost=3500`, komentar *"tak boleh berubah sedikit pun"*), akan **merah** bila subsidi ikut dikurangkan (hasilnya jadi 0, bukan 3500). Itu sinyal rumusnya salah arah, bukan test-nya yang perlu diubah — lihat § berikut.

### Kenapa subsidi TIDAK ikut dikurangkan di rumus ini

Subsidi Shopee (`shopee_shipping_rebate`) sudah punya rumah: ia ada di `TotalOtherIncome`, dan mekanisme **"Potongan Ongkos Kirim dari Shopee"** yang sudah berjalan (`accurate_receipt_usecase.go`, gerbang `RebateKeOngkir`, kv `shopee-shipping-rebate-cutover-date`) MENGURANGKAN `TotalShippingRebate` dari `TotalShippingCost` **di lapisan penerimaan**, per hari, dengan asumsi `TotalShippingCost` belum menghitungnya.

Menarik subsidi ke dalam rumus entity akan membuatnya terhitung **dua kali** begitu kedua mekanisme berjalan bersamaan, dan dua arah kegagalannya berbeda tapi sama-sama nyata:

- Hari yang sudah lewat cutover (`RebateKeOngkir=true`): subsidi dikurangkan **dua kali** dari ongkir — beban ongkir **kurang catat** sebesar subsidi.
- Hari sebelum cutover (`RebateKeOngkir=false`): subsidi tampil **dua kali** di dokumen — sekali sebagai ongkir yang sudah lebih kecil, sekali lagi sebagai baris Pendapatan Lain-lain terpisah — dokumen yang terposting lebih besar dari yang sebenarnya.

Verifikasi ke prod: order `260907CHCFD1D5` (pola Contoh B tiket — pembeli 112.000, aktual 127.000, subsidi 15.000) menghasilkan `TotalShippingCost = 15.000` (aktual − pembeli, TANPA subsidi) di rumus ini. Angka **Rp0** yang ditunjukkan Shopee baru tercapai **setelah** mekanisme rebate-ke-ongkir yang sudah ada mengurangkan subsidi di lapisan penerimaan — bukan di sini. Ini bukan kekurangan, melainkan pembagian tanggung jawab yang disengaja: satu fakta (subsidi), satu tempat (mekanisme yang sudah ada dan sudah disetujui finance 2026-09-14).

### Kenapa bertahun-tahun tak berbunyi

Dua lapis yang saling menutupi:

1. **Identitas selalu ditutup sendiri.** Komponen yang tak terpetakan ditambahkan ke residual penyesuaian sehingga dokumen selalu balance. Kesalahannya tak pernah berbentuk galat, hanya angka yang masuk akal.
2. **Residual dan biaya admin memakai akun yang sama** (kunci `settlement-adjustment` dan `service-fee` sama-sama menunjuk akun admin), jadi selisihnya mendarat di beban admin tanpa kolom bernama.

### Penjaganya sendiri dibangun di atas fixture yang kehilangan field penentu

`TestShopeeTransformIncomeIdentity_RealSample` menyebut dirinya "sample REAL Shopee (angka live escrow)" dan mengunci beban ongkir = 0. Ditelusuri ke prod, fixture itu adalah pesanan **`260612TSWHH5PW`** — enam angkanya identik (original 99.000 · commission 7.755 · service 7.990 · buyer_tx 1.000 · voucher 5.000 · escrow 71.006). Tetapi fixture **tidak menyertakan `actual_shipping_fee`**, padahal pesanan aslinya bernilai **107.400**. Dengan field itu absen, rumus yang salah menghasilkan 0 dan test-nya hijau.

Ini bukan test yang lemah, melainkan test yang **fixture-nya kehilangan justru field yang membedakan benar dan salah** — kelas yang sama dengan "fixture yang menyamakan `_id` dan `shop_id`".

### Komponen lain yang ikut terperiksa

- **`reverse_shipping_fee`** (Ongkos Kirim Pengembalian Barang): **77 dokumen, Rp1.574.800, seluruhnya bertanda POSITIF** (diverifikasi, bukan diasumsikan) — tidak pernah masuk rumus ongkir mana pun sebelumnya, ikut mendarat di residual. Diberi rumah di rumus baru sebagai penambah beban.
- **`shipping_fee_discount_from_3pl`** (Potongan Ongkos Kirim dari Jasa Kirim): **nol kejadian** di seluruh 90.194 dokumen. Sengaja **tidak** dimasukkan; menambah komponen yang tak pernah terisi hanya menambah permukaan tanpa manfaat.

## Decision

### 1. Beban ongkir = aktual − bagian pembeli, ditambah proteksi dan ongkir pengembalian

Beban ongkir seller = **ongkir aktual − bagian yang dibayar pembeli**, ditambah **biaya proteksi pengiriman** dan **ongkir pengembalian barang**. Subsidi Shopee **TIDAK** ikut — lihat § "Kenapa subsidi TIDAK ikut dikurangkan" di atas.

`final_shipping_fee` **tidak dipakai sama sekali**. Ia bukan komponen independen melainkan cerminan Shopee sendiri atas aktual dan subsidi (terbukti 100%, nol pengecualian); memasangkannya dengan `actual_shipping_fee` adalah bentuk hitung-ganda.

Diimplementasikan lewat `entity.OpsiTransformShopee{RumusOngkirBaru: bool}` — opsi baru, bukan mengubah tanda tangan fungsi yang sudah ada. `TransformToOrderIncomeWithAdjustment`/`TransformToOrderIncome` jadi pembungkus tipis (`RumusOngkirBaru` selalu `false`) — perilaku lama byte-identik, ~20 titik panggil test lama tak berubah.

### 2. Berlaku maju lewat gerbang PER-ORDER, bukan kv tanggal

Finance menyatakan "sekarang dan ke depan". **Bukan kv tanggal** seperti pola potongan ongkir (§Consequences ADR ini menyimpang sengaja dari pola itu) — income Shopee **ditulis ulang dari escrow setiap kali order di-sync** (`shopee_new_usecase.go`, tiga titik: `SyncOrderDetailSNs` ×2, `RefetchOrderEscrow`), jadi perubahan rumus di lapisan transform bersifat retroaktif kalau digerbang per-tanggal saja: sync ulang order lama akan menimpa nilai yang sudah benar.

Gerbangnya `rumusOngkirBaruBerlaku(shopID, paidAt, tepercayaPaidAt)`: order yang **hari cairnya sudah dibukukan ke Accurate** (`ShopeeHariSudahDibukukan` — mekanisme yang sama dipakai `bolehBukukanPenyesuaian`) tetap dapat rumus lama; selebihnya (termasuk order yang belum pernah cair) dapat rumus baru. Predikatnya **terbalik** dari `bolehBukukanPenyesuaian`: order yang belum pernah cair (`paidAt` nil) pasti belum mungkin dibukukan, jadi justru harus dapat rumus **baru** — bukan ditolak. Galat baca / repo nil → rumus lama (konservatif).

⛔ **Justru karena predikatnya terbalik, `paidAt` nil saja TIDAK cukup sebagai masukan** (temuan review 2026-09-22, ditutup commit `2d269894`). `paidAtTersimpan` semula mengembalikan nil untuk **tiga** keadaan berbeda — order belum cair, query gagal, order tak ketemu — dan dua gerbang membacanya ke arah keamanan yang **berlawanan**: `bolehBukukanPenyesuaian` menolak saat nil (fail-closed, aman), `rumusOngkirBaruBerlaku` justru menerimanya. Galat baca yang menyamar jadi nil karena itu meloloskan rumus baru ke order yang harinya barangkali **sudah** dibukukan, lalu cron jendela 45 hari membangun ulang penerimaannya dan dokumen terposting berubah — persis yang arahan "sekarang dan ke depan" larang. Karena itu keterpercayaan bacaan **dioper terpisah**, bukan disimpulkan dari nilainya; `tepercaya=false` hanya saat query gagal, sedangkan order/income yang memang tak ada tetap jawaban sah "belum cair". Kelas umumnya: [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] § "sudah diserap di tempat lain" — sebuah nilai kosong bukan satu pernyataan, melainkan pertanyaan *kenapa* ia kosong.

Ketiga titik tulis dikonsolidasi lewat satu fungsi `transformShopeeIncome` supaya gerbang ini (dan `bolehBukukanPenyesuaian`) tak mungkin lupa dipasang di titik baru. `RefetchOrderEscrow` yang semula menyalin query `paid_at`-nya sendiri kini ikut memakai `paidAtTersimpan`, supaya aturan "galat baca ≠ belum cair" tidak hidup di dua tempat.

### 3. Residual Shopee diberi penjaga bernilai

Bila residual identitas Shopee melewati ambang (Rp500) sesudah transform, dicatat WARN beserta `order_sn` dan nominalnya — tidak diam. Tanpa ini, kelas "komponen ongkir yang kehilangan nama" akan terulang dan kembali hanya ketahuan dari layar finance berbulan-bulan kemudian — persis riwayat biaya proteksi pengiriman dan ongkir pengembalian sebelum keduanya dipetakan.

### 4. Fixture diperbaiki, dan perbaikannya dikunci kontrol negatif

`actual_shipping_fee` yang sebenarnya dikembalikan ke fixture `RealSample`, dan panggilannya diarahkan ke rumus baru (nilainya tetap 0 — buyer menanggung penuh, sekarang untuk alasan yang benar, bukan kebetulan field kosong). Ditambahkan kasus baru dari data prod: kelas rusak (`260907CHCFD1D5`), kelas retur (`26061309NVHYNA`), kombinasi retur+proteksi (`260607EHDM3DY6`), dan kelas sehat yang **wajib** menghasilkan angka sama persis di rumus lama maupun baru.

Kontrol negatif dijalankan manual dua kali selama implementasi: (a) rumus sempat ditulis dengan subsidi ikut dikurangkan — 3 dari 6 test baru merah pada nilai `TotalShippingCost` yang salah, dikoreksi sebelum commit; (b) rumus lama sengaja dikembalikan sementara — hasil yang sama, test merah pada sebab yang tepat, bukan sebab lain.

## Consequences

- **Kas tidak berubah sepeser pun.** Yang berpindah hanya komposisi baris antara akun ongkir dan akun admin; nilai penerimaan, alokasi ke faktur, dan uang diterima tetap.
- **Beban admin akan turun dan beban ongkir naik** pada pesanan terdampak — dan itu memang arah yang benar. Finance perlu diberi tahu supaya perubahan tren tidak terbaca sebagai anomali baru.
- **Tidak menggeser insentif.** Profit insentif hanya bersandar pada net settlement (`entity/incentive_profit.go`: `ProfitSebelumOperasi = NetSettlement − HPP − IklanTiktok − IklanShopee`); beban ongkir masuk sebagai kolom informasi (`feeShipping`, PERAN "informasi"). Diperiksa langsung ke rumusnya dan ke seluruh pemanggilnya (`git grep TransformToOrderIncome` di `internal/usecase`), bukan disimpulkan.
- **Gerbangnya per-order, bukan kv tanggal** — pilihan yang menyimpang sengaja dari pola perpindahan potongan ongkir (PR #1883). Alasannya di Decision §2: field yang berubah di sini ditulis ulang setiap sync, kv tanggal akan retroaktif.
- **Penerapannya menuntut urutan operasi, bukan sekadar deploy**: deploy → ukur order yang sudah dapat rumus baru pasca-deploy → buktikan satu penerimaan di Accurate cocok dengan Subtotal Ongkos Kirim Shopee → beri tahu finance. Eksekusi prod dijalankan manusia.
- ⚠️ **Jebakan yang sudah terbukti dan belum diperbaiki di jalur LAIN**: mengulang kirim dokumen penerimaan yang **pernah** terkirim tetapi statusnya kini bukan terkirim dapat menarik keluar pelunasannya sendiri. Keputusan ini **tidak menyentuh** jalur itu (berlaku maju, gerbang per-order mencegah dokumen lama tersentuh oleh sync ulang) — dicatat di sini supaya siapa pun yang menguji dengan Retry manual tahu risikonya bukan dari perubahan ini.
- **Yang tetap terbuka**: dokumen yang terlanjur terbit dengan pembagian akun lama (dibiarkan, sesuai arahan finance); kunci `settlement-adjustment` yang masih berbagi akun dengan biaya admin sehingga residual selain ongkir tetap tak bernama.
- **96 "pesanan menyimpang" dari analisis awal TIDAK ADA** — itu artefak dari hipotesis awal yang belum tepat (`final = −buyer`, cocok 97,5%). Hipotesis yang benar (`final = −(actual−rebate)`) cocok 100%, nol pengecualian, dan rumus final (Decision §1) tidak lagi bergantung pada `final_shipping_fee` sama sekali — pertanyaan itu gugur dengan sendirinya, bukan dijawab.

## Dokumen Terkait

- [[Microservices - Integration Service]] — Auto Sync Income, potongan ongkir Shopee, dan urutan operasi yang jadi preseden
- [[Finance - Proses Penjualan Marketplace dan Uang Masuk]] — proses bisnis yang menaungi angka ini
- [[ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance]] — arti akun admin vs ongkir, dan kenapa fee tak dikenal jatuh ke admin
- [[ADR - 0001 Akuntansi via Accurate]] — alasan pembukuan tidak dilakukan sendiri
- [[APP - Web ERP]] — layar Auto Sync Penerimaan dan Rekap Pencairan tempat hasilnya terlihat
