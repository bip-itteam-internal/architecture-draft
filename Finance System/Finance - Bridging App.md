# Finance System – Bridging Accurate & Marketplace

⚠️ **Implemented (ada catatan)** — sistem Finance **lama** (Java/PostgreSQL/ReactJS), masih berjalan; sedang dimigrasi ke Golang. Lihat [[Finance - Bridging App New Golang]].

## Deskripsi

*Sistem Finance berfungsi sebagai **penghubung (bridging)** antara **Accurate** dan berbagai marketplace (**TikTok, Shopee, Lazada, Tokopedia, KiriminAja**). Fokus utamanya: **import data penjualan**, **sinkronisasi ke Accurate**, dan **pengelolaan keuangan operasional harian**.*

---

## Fitur Utama

### 1. Platform Integration
Import & olah file Excel dari berbagai platform:

| Platform     | Channel         |
| ------------ | --------------- |
| TikTok Shop  | Marketplace     |
| Shopee       | Marketplace     |
| Lazada       | Marketplace     |
| Tokopedia    | Marketplace     |
| KiriminAja   | Non-Marketplace |
| Order Online | Non-Marketplace |

---

### 2. Accurate Synchronization
- Transaksi dapat **disinkronkan ke Accurate**

### 3. Rekonsiliasi
* Rekonsiliasi untuk validasi data
* Rekonsiliasi terkait sales, return dan income

---

## Repositori

| Bagian   | Repo Git |
|---------|----------|
| Backend | https://github.com/bip-itteam-internal/finance-backend |
| Frontend| https://github.com/bip-itteam-internal/finance-frontend |

---

## Fitur Aplikasi

### 1. Master Data
Master digunakan sebagai komponen dasar referensi transaksi.

| Master             | Penjelasan                                                           |
| ------------------ | -------------------------------------------------------------------- |
| **Team**           | Grup penjualan — contoh: _Tiktok Beautyhacks, Tokopedia Beautyhacks_ |
| **Department**     | Unit kerja — contoh: _LEARNING CENTER, MARKETING - KYURA_            |
| **Project**        | Pemetaan budget/tim — contoh: _BIP CRM, BIP Kyura_                   |
| **Platform**       | Marketplace/Channel — _Shopee, Lazada, KiriminAja, Order Online_     |
| **Product**        | Daftar produk Bharata                                                |
| **Courier**        | Ekspedisi — _J&T Reguler, JNE Reguler, SiCepat, dll_                 |
| **Payment Method** | Transfer / COD / PayLater                                            |
| **Status**         | Status alur sistem                                                   |

---

### 2. Marketplace Upload
Menu untuk upload file excel per platform berbasis Team.

- TikTok Shop

| Order ID | Order Status | Order Substatus | Cancelation/Return Type | Normal or Pre-order | Shipping Fee After Discount | Original Shipping Fee | Shipping Fee Seller Discount | Shipping Fee Platform Discount | Payment platform discount | Taxes | Order Amount | Order Refund Amount | Created Time | Paid Time | RTS Time | Shipped Time | Delivered Time | Cancelled Time | Cancel By | Cancel Reason | Fulfillment Type | Warehouse Name | Tracking ID | Delivery Option | Shipping Provider Name | Buyer Message | Buyer Username | Recipient | Phone # | Zipcode | Country | Province | Regency and City | Districts | Villages | Detail Address | Additional address information | Payment Method | Product Category | Package ID | Seller Note | Checked Status | Checked Marked by | SKU ID | Seller SKU | Product Name | Variation | Quantity | Sku Quantity of return | SKU Unit Original Price | SKU Subtotal Before Discount | SKU Platform Discount | SKU Seller Discount | SKU Subtotal After Discount | Buyer Service Fee | Weight(kg) | Dynamic Commission |
|----------|--------------|-----------------|--------------------------|----------------------|------------------------------|------------------------|-------------------------------|--------------------------------|----------------------------|-------|--------------|----------------------|--------------|-----------|----------|---------------|-----------------|----------------|-----------|----------------|------------------|----------------|-------------|----------------|--------------------------|----------------|----------------|-----------|----------|---------|---------|----------|-------------------|-----------|----------|----------------|------------------------------|----------------|------------------|------------|-------------|----------------|---------------------|--------|------------|--------------|-----------|----------|------------------------|----------------------------|------------------------------|----------------------------|---------------------------|-------------------------------|------------------|-------------|--------------------|
- Tokopedia

| Nomor | Nomor Invoice | Tanggal Pembayaran | Status Terakhir | Tanggal Pesanan Selesai | Waktu Pesanan Selesai | Tanggal Pesanan Dibatalkan | Waktu Pesanan Dibatalkan | Nama Produk | Tipe Produk | Nomor SKU | Catatan Produk Pembeli | Catatan Produk Penjual | Jumlah Produk Dibeli | Harga Awal (IDR) | Harga Satuan Bundling (IDR) | Diskon Produk (IDR) | Harga Jual (IDR) | Jumlah Subsidi Tokopedia (IDR) | Nilai Kupon Toko Terpakai (IDR) | Jenis Kupon Toko Terpakai | Kode Kupon Toko Yang Digunakan | Biaya Pengiriman Tunai (IDR) | Biaya Asuransi Pengiriman (IDR) | Total Biaya Pengiriman (IDR) | Total Penjualan (IDR) | Nama Pembeli | No Telp Pembeli | Nama Penerima | No Telp Penerima | Alamat Pengiriman | Kota | Provinsi | Nama Kurir | Tipe Pengiriman (regular, same day, etc) | No Resi / Kode Booking | Tanggal Pengiriman Barang | Waktu Pengiriman Barang | Gudang Pengiriman | Nama Campaign | Nama Bundling | Tipe Bebas Ongkir (Bebas Ongkir, Bebas Ongkir DT) | COD | Jumlah Produk Yang Dikurangkan | Total Pengurangan (IDR) | Nama Penawaran Terpakai | Tingkatan Promosi Terpakai | Diskon Penawaran Terpakai (IDR) |
|-------|----------------|--------------------|------------------|---------------------------|-------------------------|-------------------------------|-----------------------------|--------------|-------------|-----------|--------------------------|---------------------------|------------------------|-------------------|-----------------------------|------------------------|-------------------|----------------------------------|----------------------------------|-------------------------------|-------------------------------|----------------------------------|-----------------------------------|--------------------------------|-----------------------|---------------|--------------------|------------------|-------------------|--------------------|--------------------|-------|----------|------------------------------------|----------------------------|-----------------------------|----------------------------|-----------------------|----------------|--------------|-------------------------------------------|------|------------------------------|------------------------|---------------------------|------------------------------|-------------------------------|
- Lazada

| orderItemId | orderType | Guarantee | deliveryType | lazadaId | sellerSku | lazadaSku | wareHouse | createTime | updateTime | rtsSla | ttsSla | orderNumber | invoiceRequired | invoiceNumber | deliveredDate | customerName | customerEmail | nationalRegistrationNumber | shippingName | shippingAddress | shippingAddress2 | shippingAddress3 | shippingAddress4 | shippingAddress5 | shippingPhone | shippingPhone2 | shippingCity | shippingPostCode | shippingCountry | shippingRegion | billingName | billingAddr | billingAddr2 | billingAddr3 | billingAddr4 | billingAddr5 | billingPhone | billingPhone2 | billingCity | billingPostCode | billingCountry | taxCode | branchNumber | taxInvoiceRequested | payMethod | paidPrice | unitPrice | QTY | sellerDiscountTotal | shippingFee | walletCredit | PRODUCT NAME | itemName | variation | cdShippingProvider | shippingProvider | shipmentTypeName | shippingProviderType | cdTrackingCode | trackingCode | trackingUrl | shippingProviderFM | trackingCodeFM | trackingUrlFM | promisedShippingTime | premium | status | buyerFailedDeliveryReturnInitiator | buyerFailedDeliveryReason | buyerFailedDeliveryDetail | buyerFailedDeliveryUserName | bundleId | semiManaged | flexibleDeliveryTime | bundleDiscount | refundAmount | sellerNote |
|--------------|-----------|-----------|---------------|----------|-----------|-----------|-----------|-------------|-------------|--------|--------|--------------|------------------|----------------|----------------|----------------|----------------|-----------------------------|--------------|------------------|-------------------|-------------------|-------------------|-------------------|----------------|----------------|----------------|-------------------|------------------|----------------|--------------|---------------|----------------|----------------|----------------|----------------|---------------|----------------|---------------|------------------|-----------------|---------|--------------|--------------------|-----------|-----------|-----------|-----|----------------------|-------------|--------------|----------------|----------|-----------|---------------------|------------------|-------------------|----------------------|------------------|--------------|------------|---------------------|----------------|--------------|----------------------|---------|--------|-------------------------------------|-----------------------------|------------------------------|------------------------------|----------|-------------|-----------------------|----------------|-------------|------------|

- Shopee

| No. Pesanan | Status Pesanan | Alasan Pembatalan | Status Pembatalan Pengembalian | No. Resi | Opsi Pengiriman | Antar ke counter/ pick-up | Pesanan Harus Dikirimkan Sebelum | Waktu Pengiriman Diatur | Waktu Pesanan Dibuat | Waktu Pembayaran Dilakukan | Metode Pembayaran | SKU Induk | Nama Produk | Nomor Referensi SKU | Nama Variasi | Harga Awal | Harga Setelah Diskon | Jumlah | Returned quantity | Total Harga Produk | Total Diskon | Diskon Dari Penjual | Diskon Dari Shopee | Berat Produk | Jumlah Produk di Pesan | Total Berat | Voucher Ditanggung Penjual | Cashback Koin | Voucher Ditanggung Shopee | Paket Diskon | Paket Diskon (Diskon dari Shopee) | Paket Diskon (Diskon dari Penjual) | Potongan Koin Shopee | Diskon Kartu Kredit | Ongkos Kirim Dibayar oleh Pembeli | Estimasi Potongan Biaya Pengiriman | Ongkos Kirim Pengembalian Barang | Total Pembayaran | Perkiraan Ongkos Kirim | Catatan dari Pembeli | Catatan | Username (Pembeli) | Nama Penerima | No. Telepon | Alamat Pengiriman | Kota/Kabupaten | Provinsi | Waktu Pesanan Selesai |
|-------------|----------------|-------------------|--------------------------------|----------|-----------------|---------------------------|----------------------------------|-------------------------|----------------------|----------------------------|-------------------|-----------|-------------|---------------------|--------------|------------|----------------------|--------|-------------------|--------------------|--------------|--------------------|-------------------|--------------|------------------------|-------------|----------------------------|---------------|---------------------------|--------------|----------------------------------|-----------------------------------|----------------------|---------------------|----------------------------------|-------------------------------------|----------------------------------|------------------|------------------------|----------------------|---------|--------------------|--------------|--------------|--------------------|----------------|----------|----------------------|
- KiriminAja

| No | ID | Pengirim | Penerima | No. HP | Alamat Pengirim | Kecamatan Pengirim | Kabupaten Pengirim | Provinsi Pengirim | Alamat Penerima | Kecamatan Penerima | Kabupaten Penerima | Provinsi Penerima | Isi Paket | Catatan | Nilai Barang | QTY | Jenis Barang | Expedisi | Service | AWB | Type | COD | Biaya COD | Pencairan COD | Ongkir | Rts Fee | Diskon Ongkir | Asuransi | Admin | Total Ongkir | Status | Dibuat oleh | Tgl. Dibuat | Tgl. Dikirim | Tgl. Diterima/Selesai | Tgl. Retur Selesai | TLC |
|----|----|-----------|-----------|--------|------------------|----------------------|------------------------|---------------------|------------------|----------------------|-----------------------|---------------------|-----------|----------|----------------|-----|--------------|----------|---------|------|------|-----|------------|----------------|---------|---------|----------------|----------|--------|---------------|--------|-------------|--------------|--------------|------------------------|----------------------|-----|

---

### 3. Transaction

| Menu           | Deskripsi                                                             |
|---------------|------------------------------------------------------------------------|
| **Sales Invoice** | Catatan invoice penjualan resmi                                     |
| **Sample Sales**  | Transaksi sample sales **+ sync Accurate**                       |
| **Daily Sales**   | Rekap penjualan harian **+ sync Accurate + notif**         |

---

### 4. Income
Menu pendapatan berdasarkan marketplace & harian.

- TikTok Shop

| Order/adjustment ID | Type | Order created time | Order settled time | Currency | Total settlement amount | Total revenue | Subtotal after seller discounts | Subtotal before discounts | Seller discounts | Refund subtotal after seller discounts | Refund subtotal before seller discounts | Refund of seller discounts | Total fees | Platform commission fee | Flat fee | Sales fee | Pre-Order Service Fee | Mall service fee | Payment fee | Shipping cost | Shipping costs passed on to the logistics provider | Replacement shipping fee (passed on to the customer) | Exchange shipping fee (passed on to the customer) | Shipping cost borne by the platform | Shipping cost paid by the customer | Refunded shipping cost paid by the customer | Return shipping costs (passed on to the customer) | Shipping cost subsidy | Affiliate commission | Affiliate partner commission | Affiliate Shop Ads commission | SFP service fee | LIVE Specials Service Fee | Voucher Xtra Service Fee | Order processing fee | Installation service fee | EAMS Program service fee | Fix Infrastructure Fee | Brand Crazy Deals/Flash Sale service fee | Bonus cashback service fee | DT Handling Fee | PayLater Handling Fee | Adjustment amount | Related order ID | Customer payment | Customer refund | Seller co-funded voucher discount | Refund of seller co-funded voucher discount | Platform discounts | Refund of platform discounts | Platform co-funded voucher discounts | Refund of platform co-funded voucher discounts | Seller shipping cost discount | Estimated package weight (g) | Actual package weight (g) | Shopping center items | Order Source | Dynamic Commission |
|---------------------|------|---------------------|---------------------|----------|---------------------------|--------------|----------------------------------|-----------------------------|-------------------|------------------------------------------|-------------------------------------------|-----------------------------|------------|---------------------------|----------|-----------|--------------------------|------------------|-------------|---------------|------------------------------------------------------|------------------------------------------------------|---------------------------------------------------|-------------------------------------------|----------------------------------|------------------------------------------|-------------------------------------------|-----------------------|--------------------|------------------------------|------------------------------|------------------|------------------------------|------------------------|--------------------|--------------------------|------------------------------|---------------------------|------------------------------|------------------|------------------|--------------------|------------------|--------------------|-----------------------------|-----------------|---------------------------|--------------------------|------------------------------|------------------------------------------|---------------------------------------------|------------------------------------------|---------------------------|-------------------------------|------------------------------|--------------------------|--------------|-------------------|
- Tokopedia

| Commission Name | Product ID | Product Name | Invoice No | Total Product Amount | Promo | Promo Rate | Promo Code | Finish Date | Service Fee Rate | Service Fee Gross | Service Fee Net | PPN | PPH |
|-----------------|------------|--------------|------------|-----------------------|-------|------------|------------|--------------|-------------------|--------------------|------------------|------|------|
- Lazada

| Periode Laporan | Nomor Laporan | Tanggal Transaksi | Nama Biaya | Jumlah (Termasuk Pajak) | VAT Amount | Status Pelepasan Dana | Tanggal Dilepas | Komentar | Tanggal Pesanan Dibuat | Nomor Pesanan | ID Pesanan | SKU Penjual | Lazada SKU | WHT Amount | WHT termasuk dalam jumlah | Status Pesanan | Nama Produk |
|-----------------|---------------|-------------------|------------|--------------------------|------------|------------------------|------------------|----------|-------------------------|----------------|------------|-------------|-------------|------------|----------------------------|----------------|-------------|
- Shopee

| No. Pesanan | No. Pengajuan | Username (Pembeli) | Waktu Pesanan Dibuat | Metode Pembayaran | Tanggal Dana Dilepaskan | Harga Asli Produk | Total Diskon Produk | Refund ke Pembeli | Diskon Shopee | Voucher Penjual | Diskon Voucher Penjual | Cashback Penjual | Ongkir Dibayar Pembeli | Diskon Ongkir Kurir | Gratis Ongkir Shopee | Ongkir Diteruskan ke Kurir | Ongkir Retur | Pengembalian Biaya Kirim | Kembali ke Biaya Pengiriman Pengirim | Biaya Komisi AMS | Biaya Administrasi | Biaya Layanan | Biaya Proses Pesanan | Premi | Biaya Program | Biaya Kartu Kredit | Biaya Kampanye | Bea Masuk/PPN/PPh | Total Penghasilan | Kode Voucher | Kompensasi | Promo Gratis Ongkir Penjual | Jasa Kirim | Nama Kurir |
|-------------|---------------|---------------------|-----------------------|--------------------|--------------------------|--------------------|----------------------|-------------------|----------------|------------------|-------------------------|--------------------|---------------------------|----------------------|-----------------------|------------------------------|--------------|---------------------------|-----------------------------------------|-------------------|---------------------|----------------|-------------------------|--------|---------------|---------------------|----------------|-------------------------|-------------------|--------------|-------------|------------------------------|--------------|-------------|
- KiriminAja

| Tanggal | Keterangan | Kategori | Nominal Masuk | Nominal Keluar | Saldo |
|---------|------------|----------|----------------|-----------------|--------|

- **Daily Income** → Pendapatan harian

---

### 5. Retur
Pengelolaan barang kembali/retur.

- TikTok Shop
- Tokopedia
- Lazada
- Shopee
- KiriminAja
- **Daily Retur** → Rekap retur harian

---

## Tech Stack

### 🔧 Backend
- Language   : **Java**
- Database   : **PostgreSQL**
- API Docs   : **Swagger**
- Auth       : **JWT Authentication**

### 🎨 Frontend
- Language   : **JavaScript**
- Runtime    : **NodeJS**
- Framework  : **ReactJS**

## Dokumen Terkait

- [[Finance - Bridging App New Golang]] — penulisan ulang (Golang) sistem ini
- [[Finance]] — overview domain Finance System
- [[External - Accurate]] — target sinkronisasi akuntansi
- [[Finance - Incentive]] — sistem insentif terkait
