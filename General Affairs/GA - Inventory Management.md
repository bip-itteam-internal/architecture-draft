## Deskripsi

*Sistem inventory General Affairs — pencatatan & kontrol aset/barang perusahaan. **Catatan penting:** nama "Inventory Management" agak menyesatkan; saat ini cakupannya **bukan** mengelola Internal & external inventory sepenuhnya sekaligus, melainkan inventory yang digunakan dari purchase/procurement untuk produksi & penjualan produk tersebut. Arah jangka panjang: GA sebagai pengelola inventory perusahaan (lihat Pertimbangan).*

- **Status**: 🟡 Konsep / Draft
- **Penomoran aset (tag)**: implementasi saat ini `INV-BIP-DDMMYY-NAMA-n` (tanggal dari `purchase_date` WIB, `NAMA` = nama barang uppercase tanpa spasi, `n` = increment) — sudah menyertakan item, sejalan dengan arah yang diinginkan. Kategori & nama barang kini **bebas-ketik** (bukan lagi enum terbatas). Detail grounded: [[Microservices - Inventory Service]] · [[API - Inventory Service]].
- Terkait erat dengan [[GA - Procurement System]] (sumber masuknya barang) & [[WH - Management System]] (master data).

## Latar Belakang

GA ingin punya dashboard untuk mengelola aset perusahaan (alat & bahan, ATK, dokumen legal) dalam program paperless yang terintegrasi antar divisi (lihat [[GA - Big Pictures]]).

**GA sebagai "Pengelola" Inventory Perusahaan** — setiap item/objek inventory secara native dimiliki oleh GA; GA dapat menurunkan sebagian item ke departemen lain di mana departemen tersebut akan memelihara item itu sesuai kebutuhan. Modelnya semacam hierarki: GA di puncak, lainnya di bawah.

![[inventory-propergation.png]]

Artinya ada **1 master data** yang disirkulasikan dari GA ke departemen lain sesuai kebutuhan; sebagian departemen (mis. manufaktur) mungkin punya fitur unik terkait cara mereka melihat inventory mereka, dan seterusnya.

## Ruang Lingkup / Fitur

**Scope**
* Pencatatan aset menjadi jelas
* Controlling & monitoring aset
* lokasi barang
* Pencatatan vendor
* Ada informasi SOP pengajuan aset
* Reservasi ruang meeting & peminjaman aset (lihat [[GA - Asset Loan & Room Booking]])

**Breakdown fitur**
- **Dashboard** — ikhtisar yang baik untuk pelaporan ke stakeholder; ringkasan detail purchases, sales, stok, dan profit; volume aktivitas / perubahan stok
- **Purchases** *(mengapa fitur ini ada di sini?)* — purchase/procurement normal untuk produk, dengan detail vendor/supplier. GA punya dana **petty cash** untuk pengeluaran yang dikonsumsi dalam satu bulan (mis. perlengkapan kantor, peralatan kebersihan, atau request barang ≤ Rp2 juta/bulan). Bila demikian, **Finance tetap satu-satunya pemilik sistem purchasing**; GA dapat melakukan request dan melihat entri procurement mereka yang disetujui.
- **Sales** *(mengapa fitur ini ada di sini?)* — sales normal untuk produk, tetapi tanpa info ke mana produk dijual. Disepakati lebih baik **dipindah ke modulnya sendiri** (mis. ke Finance System).
- **[[CORE - OCR Document Service|OCR Document]]** (shared service) — dokumen fisik di-scan jadi gambar lalu di-upload; OCR membaca dokumen untuk kebutuhan lain (mis. pencarian judul dokumen, isi dokumen, nomor tertentu di dalam dokumen).

**Master data terkait**
- **Warehouse Master Data** — mengelola hal-hal apa yang disimpan di warehouse saat ini, dengan Stock Keeping Unit (SKU) dan barcode untuk menciptakan alur sistem yang lebih baik.
- **Internal Inventory** *(belum ada / belum disebutkan per 10/7/25 pada [berkas dokumen Bharata di Google Drive](https://drive.google.com/drive/folders/1gKly790zuff8roX3kLQq1TVE02jT7drK))* — akan melacak semua aset perusahaan & menjadi dependency untuk sistem mendatang (mis. perbaikan). Bisa menjadi **child** dari GA - Inventory Management untuk semua barang ber-tag internal, lalu ke depannya diturunkan ke tiap sistem (mis. IT, HR) untuk mengelola internal inventory mereka sendiri. Fitur: Dashboard; pembuatan & penandaan aset individual (sangat menyerupai salah satu fitur [[WH - Management System]]); penugasan aset ke karyawan.

## Alur

berikut alur sebuah barang menjadi aset perusahaan dari awal hingga akhir.
1. User mengajukan barang dengan mengisi form disertai tanda tangan SPV departement ybs. ([[Form Permintaan Barang GA.pdf]])
2. Form ini diserahkan ke GA dan dilakukan nego dengan mencarikan alternatif lain. minimal 3 pilihan barang yang sama dengan harga yang berbeda
3. GA dan user memilih barang sesuai dengan vendor yang dipilih
4. GA melakukan approval yang diwakili oleh Spv dan meneruskan proses
5. GA menentukan pembayaran dengan ketentuan
	* apabila harga barang kurang dari Rp. 3.000.000, maka tidak memerlukan tanda tangan Direktur
	* apabila harga barang lebih dari Rp. 3.000.000, maka memerlukan persetujuan Direktur melalui sekretariat
6. apabila sudah dilakukan approval di step 5 diatas, maka GA melanjutkan proses dengan melakukan PO
7. Barang akan dikirim
8. Setelah barang sampai, GA melakukan pencatatan dan melakukan penomoran (Jenis-Ruangan-Bulan-Tahun) dan menyerahkan barang ke User.
9. Form penerimaan barang diisi sebagai bentuk pencatatan.

## Hasil Observasi

Tanggal 13 Januari 2026
#### kendala yang dialami tim GA:
1. Ruangan aset yang belum ada. ruangan atau gudang aset & barang tidak terpakai belum ada. sehingga sementara ini barang-barang tersebut diletakan seadanya
2. Barang material diletakan dilokasi yang seadanya (khusus jika ada pembangunan)
3. Pencatatan barang yang rusak

#### Kategori barang
1. Barang Office
2. Produksi & warehouse
3. Aset building

#### Sifat barang
1. Konsumsi (Kopi, gula) (fixed cost)
2. Aset (Sesuai kebutuhan)

## Pertimbangan & Belum Diputuskan (TBD)

- **Gabung dengan internal inventory?** Keduanya kemungkinan punya banyak fitur sama, jadi bisa ditaruh di sini + tag tambahan untuk item yang dipakai internal. Mungkin kurang diinginkan jika internal inventory tidak dikelola secara native oleh GA. → **Disimpulkan pertimbangan ini valid** & dapat dipakai pada situasi saat ini karena diturunkan/dinaikkan rapi berdasarkan tingkat kepentingan & level saat ini; pengembangan dapat dilanjutkan.
- Jenis inventory & detail apa yang diinginkan? (mis. bahan baku produksi minim info; komputer banyak info termasuk SN). Bagaimana cara menyimpannya — berbasis barcode dengan SKU pada lokasi keberadaannya? Bagaimana diturunkan ke departemen?
- [ ] (Detail tertunda) Database Internal Inventory sepertinya bisa digabung dengan Warehouse Master Data dengan flag eksplisit untuk barang internal inventory.
- **Masalah yang mungkin muncul dari departemen lain:**
	- **Finance** — Purchase/procurement order diperlukan untuk memvalidasi entri; Sales order diperlukan untuk memvalidasi entri.
	- **Warehouse** — Dokumen tambahan untuk memvalidasi bahwa produk dipindahkan masuk/keluar dari warehouse.

## Kebutuhan

- [ ] Warehouse master data (lihat referensi)
- [ ] Data purchase dari finance
- [ ] Data sales dari finance

## Referensi

Sistem yang sudah ada:
1. Inventa

## Dependensi / Dokumen Terkait

- [[WH - Management System]]
- [[GA - Procurement System]] · [[CORE - OCR Document Service]]
- [[GA - Asset Loan & Room Booking]] — alur pinjam ruang/aset
- [[GA - Big Pictures]]
