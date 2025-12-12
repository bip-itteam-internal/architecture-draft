# 🧾 Finance System – Bridging Accurate & Marketplace

Sistem Finance berfungsi sebagai **penghubung (bridging)** antara **Accurate** dan berbagai marketplace seperti **TikTok, Shopee, Lazada, Tokopedia, dan KiriminAja**.  
Fokus utamanya adalah **import data penjualan**, **sinkronisasi ke Accurate**, dan **pengelolaan keuangan operasional harian**.

---

## 🔥 Fitur Utama

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

#### Contoh Excel TikTok Shop
| Order ID | Order Status | Order Substatus | Cancelation/Return Type | Normal or Pre-order | Shipping Fee After Discount | Original Shipping Fee | Shipping Fee Seller Discount | Shipping Fee Platform Discount | Payment platform discount | Taxes | Order Amount | Order Refund Amount | Created Time | Paid Time | RTS Time | Shipped Time | Delivered Time | Cancelled Time | Cancel By | Cancel Reason | Fulfillment Type | Warehouse Name | Tracking ID | Delivery Option | Shipping Provider Name | Buyer Message | Buyer Username | Recipient | Phone # | Zipcode | Country | Province | Regency and City | Districts | Villages | Detail Address | Additional address information | Payment Method | Product Category | Package ID | Seller Note | Checked Status | Checked Marked by | SKU ID | Seller SKU | Product Name | Variation | Quantity | Sku Quantity of return | SKU Unit Original Price | SKU Subtotal Before Discount | SKU Platform Discount | SKU Seller Discount | SKU Subtotal After Discount | Buyer Service Fee | Weight(kg) | Dynamic Commission |
|----------|--------------|-----------------|--------------------------|----------------------|------------------------------|------------------------|-------------------------------|--------------------------------|----------------------------|-------|--------------|----------------------|--------------|-----------|----------|---------------|-----------------|----------------|-----------|----------------|------------------|----------------|-------------|----------------|--------------------------|----------------|----------------|-----------|----------|---------|---------|----------|-------------------|-----------|----------|----------------|------------------------------|----------------|------------------|------------|-------------|----------------|---------------------|--------|------------|--------------|-----------|----------|------------------------|----------------------------|------------------------------|----------------------------|---------------------------|-------------------------------|------------------|-------------|--------------------|


---

### 2. Accurate Synchronization
- Transaksi dapat **disinkronkan ke Accurate**

---

## 📂 Repositori

| Bagian   | Repo Git |
|---------|----------|
| Backend | https://github.com/bip-itteam-internal/finance-be |
| Frontend| https://github.com/bip-itteam-internal/finance-frontend |

---

## 🏗 Fitur Aplikasi

### 1. Master Data
Master digunakan sebagai komponen dasar referensi transaksi.

| Master            | Penjelasan                                                                               |
|------------------|-------------------------------------------------------------------------------------------|
| **Team**         | Grup penjualan — contoh: _Tiktok Beautyhacks, Tokopedia Beautyhacks_                      |
| **Department**   | Unit kerja — contoh: _LEARNING CENTER, MARKETING - KYURA_                                 |
| **Project**      | Pemetaan budget/tim — contoh: _BIP CRM, BIP Kyura_                                        |
| **Platform**     | Marketplace/Channel — _Shopee, Lazada, KiriminAja, Order Online_                          |
| **Product**      | Daftar produk Bharata                                                                     |
| **Courier**      | Ekspedisi — _J&T Reguler, JNE Reguler, SiCepat, dll_                                      |
| **Payment Method** | Transfer / COD / PayLater                                                                |
| **Status**       | Status alur sistem           |

---

### 2. Marketplace Upload
Menu untuk upload file excel per platform berbasis Team.

- TikTok Shop  
- Tokopedia  
- Lazada  
- Shopee  
- KiriminAja  

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
- Tokopedia  
- Lazada  
- Shopee  
- KiriminAja  
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

## ⚙️ Tech Stack

### 🔧 Backend
- Language   : **Java**
- Database   : **PostgreSQL**
- API Docs   : **Swagger**
- Auth       : **JWT Authentication**

### 🎨 Frontend
- Language   : **JavaScript**
- Runtime    : **NodeJS**
- Framework  : **ReactJS**

---
