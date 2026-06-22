## Catatan

*Nama sistem ini menyesatkan karena ini tidak mengelola sepenuhnya untuk Internal Inventory dan external inventory sekaligus. Ini hanya mengelola inventory yang digunakan dari purchase/procurement untuk produksi dan penjualan produk tersebut*

## Pertimbangan

Bisakah ini digabungkan dengan internal inventory? Karena keduanya kemungkinan akan memiliki banyak fitur yang sama, kita bisa menaruhnya di sini dan menambahkan tag tambahan untuk item yang digunakan secara internal.

Mungkin kurang diinginkan jika internal inventory tidak dikelola secara native oleh GA

### General Affairs sebagai "Pengelola" Inventory Perusahaan

Ini berarti setiap item dan objek inventory secara native dimiliki oleh GA, pada sistem ini GA dapat menurunkan sebagian item ke departemen lain di mana departemen tersebut akan dapat memelihara item tersebut sesuai kebutuhan.

Sistem ini akan merepresentasikan semacam hierarki dengan GA di puncak, dan lainnya di bawahnya

![[inventory-propergation.png]]

Ini berarti kita akan memiliki 1 master data yang disirkulasikan dari GA ke departemen lain sesuai kebutuhan, beberapa departemen seperti manufaktur mungkin memiliki fitur unik terkait bagaimana mereka melihat inventory mereka, dan seterusnya...

Tetapi di sini kita perlu tahu jenis inventory apa dan detail apa yang kita inginkan untuk dimilikinya? misalnya; bahan baku untuk produksi tidak akan memiliki banyak informasi pada mereka sementara komputer akan memiliki banyak termasuk SN dan detail lainnya

Dan bagaimana mereka menyimpan inventory mereka? apakah berbasis barcode dengan SKU pada lokasi keberadaannya? dan bagaimana hal itu diturunkan ke departemen dan sebagainya.

## Informasi gabungan dari Warehouse Master Data

### Deskripsi

*Master data ini mengelola hal-hal apa yang disimpan di warehouse saat ini, dengan Stock Keeping Unit dan barcode untuk menciptakan alur sistem yang lebih baik*

## Informasi gabungan dari Internal Inventory

### Catatan

*Ini belum ada atau belum disebutkan per 10/7/25 pada [berkas dokumen Bharata di google drive*](https://drive.google.com/drive/folders/1gKly790zuff8roX3kLQq1TVE02jT7drK)*

### Deskripsi

*Sistem ini akan melacak semua aset perusahaan dan akan menjadi dependency untuk sistem mendatang seperti perbaikan atau lainnya*

*Ini bisa menjadi child dari GA - Inventory Management yang berada untuk semua barang yang ditandai sebagai internal, dan ini ke depannya bisa diturunkan ke setiap sistem misalnya IT, HR untuk mengelola internal inventory mereka sendiri secara tepat*

### Fitur

- Dashboard
- Pembuatan dan penandaan untuk aset individual (ini sangat menyerupai salah satu fitur WH - Management System)
- Penugasan aset ke karyawan

### Detail yang Tertunda

- [ ] Database ini sepertinya bisa digabungkan dengan Warehouse Master Data dengan flag eksplisit untuk barang internal inventory

## Deskripsi

Jadi kita telah menyimpulkan bahwa pertimbangan di atas valid, dan dapat digunakan pada situasi saat ini karena diturunkan/dinaikkan dengan rapi berdasarkan tingkat kepentingan dan level saat ini

Saat ini tag unik inventory terlihat seperti: **INV.Year.Category.No** yang masih kurang diinginkan karena kita perlu tahu objeknya, sesuatu seperti **INV.Year.Category.Item.No** di mana itu memberi kita basis yang baik dan informasi spesifik sekaligus

Tetapi meskipun demikian pengembangan dapat dilanjutkan, kategori saat ini terbatas pada elektronik. Akan diisi nanti setelah pengembangan berlangsung

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
## Fitur

#### Scope
* Pencatatan aset menjadi jelas
* Controlling & monitoring aset
* lokasi barang
* Pencatatan vendor
* Ada informasi SOP pengajuan aset
* Reservasi ruang meeting

#### Breakdown
- Dashboard
	- Ikhtisar semuanya yang sangat baik untuk pelaporan ke stakeholder
	- Ringkasan secara detail: purchases, sales, stok, dan profit
	- Volume aktivitas atau perubahan stok
- Purchases (Mengapa fitur ini ada di sini?)
	- Purchase/procurement normal untuk produk, dengan detail vendor/supplier
	- Karena GA (General Affairs) memiliki dana petty cash yang digunakan untuk pengeluaran yang dikonsumsi dalam satu bulan — misalnya, membeli perlengkapan kantor, peralatan kebersihan, atau mengajukan permintaan untuk barang yang tidak melebihi 2 juta rupiah per bulan.
	- Jika demikian maka Finance tetap menjadi satu-satunya pemilik sistem purchasing, dan GA dapat melakukan request dan melihat entri procurement mereka yang disetujui
- Sales (Mengapa fitur ini ada di sini?)
	- Sales normal untuk produk, tetapi tidak ada informasi ke mana produk dijual
	- Saya setuju, lebih baik memindahkan fitur ini ke modulnya sendiri (mis: pindah ke Finance System)
* [[CORE - OCR Document Service|OCR Document]] (shared service)
	* dokumen fisik yang ada bisa di scan berbentuk gambar yang nantinya diupload ke sistem 
	* OCR akan membaca dokumen tersebut dan bisa dimanfaatkan untuk kebutuhan lain
	* misal: pencarian title dokumen, isi dokumen, nomor tertentu di dalam dokumen

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

## Masalah yang mungkin muncul dari departemen lain

- Finance
	- Purchase/procurement order diperlukan untuk memvalidasi entri
	- Sales order diperlukan untuk memvalidasi entri
- Warehouse
	- Dokumen tambahan untuk memvalidasi bahwa produk tersebut dipindahkan masuk/keluar dari warehouse

## Kebutuhan

- [ ] Warehouse master data (lihat referensi)
- [ ] Data purchase dari finance
- [ ] Data sales dari finance

### Referensi Sistem yang sudah ada
1. Inventa

## Dependencies

- [ ] [[WH - Management System]]