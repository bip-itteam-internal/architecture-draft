## Notes

*This system name is misleading as this didn't manage fully for Internal Inventory and external inventory altogether. This only manage inventory used form purchase/procurement for production and sales of said products*

## Consideration

Can this be merged with internal inventory? As both will probably have a lot of feature the same, we could put it in here and add additional tags for items that is being used internally. 

Might be undesiredable if internal inventory aren't natively managed by GA

### General Affairs as the "Manager" of the Company Inventory

This means every inventory items and object are natively owned by GA, on this system GA can propagate down some of the items into other department where the department will be able to maintain the items accordingly.

This system will somewhat represent a hierarcy with GA at the top, and others below it

![[inventory-propergation.png]]

This means we would have 1 master data that is being circulated from GA to other department accordingly, some department like manufactur might have unique feature regarding how they see their inventory, and so on...

But in here we need to know what type of inventory and what details do we want it to have? for example; base material for production will not have that much information on them while computer would have plenty including SN and other details

And how does they keep their inventory? is it barcode based with SKU on where the location are? and how does that transfer down to department and such.

## Merged information from Warehouse Master Data

### Description

*This master data manage on what things are kept/stored in the warehouse at current time, with Stock Keeping Unit and barcode to create a better flow of the system*

## Merged information from Internal Inventory

### Notes

*This doesn't exist or yet mentioned as per 10/7/25 under [Bharata's document files google drive*](https://drive.google.com/drive/folders/1gKly790zuff8roX3kLQq1TVE02jT7drK)*

### Description

*This system would track all company's assets and would be dependency for upcoming system as repairs or something else*

*This could be a child of GA - Inventory Management that reside for all goods that tagged as internal, and this could future be propagated to each system for example IT, HR to manage their own internal inventory approriately*

### Features

- Dashboard
- Creation and tagging for individual assets (this is closely resemble one of WH - Management System features)
- Asset assignment to employees

### Pending Details

- [ ] This database seems can be merged with Warehouse Master Data with explicit flags for internal inventory goods

## Description

So we have concluded that te consideration above are valid, and can be used on the current situation since it is nicely propagated down/up based on the current importance and levels

Currently the inventory unique tags looks like: **INV.Year.Category.No** which is still underdesired since we need to know the object, something like **INV.Year.Category.Item.No** where that give us nice base and specific information altogether

But never the less the development can be continued, current category are limited to electronics. Will fill this later once the development taken place

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
## Features

#### Scope
* Pencatatan aset menjadi jelas
* Controlling & monitoring aset
* lokasi barang
* Pencatatan vendor
* Ada informasi SOP pengajuan aset
* Reservasi ruang meeting

#### Breakdown
- Dashboard
	- Overview of everything excellent for reporting to stakeholders
	- Summary in details: purchases, sales, stocks and profits
	- Volume activity or stock changes
- Purchases (Why this feature in here?)
	- Normal purchase/procurement for product, with vendor/supplier details
	- Because GA (General Affairs) has a petty cash fund used for expenses that are consumed within one month — for example, purchasing office supplies, cleaning equipment, or submitting requests for items not exceeding 2 million rupiah per month.
	- If so then Finance are still the sole owner of purchasing system, and GA are able request and see their accepted procurement entries
- Sales (Why this feature in here?)
	- Normal sales for product, but no information on where the product being sold to
	- I agree, better to move this feature to it's own module (eg: move to Finance System)
* OCR Document
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

## Issues that might come from other departments

- Finance
	- Purchase/procurement order is required to validate the entry
	- Sales order is required to validate the entry
- Warehouse
	- Additional document to validate said product is being moved around inbound/outbound of the warehouse

## Requirements

- [ ] Warehouse master data (look up reference)
- [ ] Purchase data from finance
- [ ] Sales data from finance

### Referensi Sistem yang sudah ada
1. Inventa

## Dependencies

- [ ] [[WH - Management System]]