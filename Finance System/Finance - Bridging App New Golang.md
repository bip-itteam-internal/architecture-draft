# Finance - Bridging App (Golang Rewrite)

⚠️ **Implemented (ada catatan)** — Fitur utama berjalan; beberapa endpoint direct-push Accurate masih di-comment dan digantikan alur summary-report.

## Deskripsi

*Fitur **Integration Accurate** adalah bagian dari [[Microservices - Integration Service]] yang berfungsi sebagai jembatan finansial antara marketplace (TikTok Shop & Shopee) dengan **Accurate Online**. Pengguna Finance dapat membuat ringkasan transaksi harian (Sales, Income, Return) per toko dan mengirimkannya ke Accurate sebagai Sales Invoice atau Sales Return. Ini adalah penulisan ulang (Golang rewrite) dari sistem Finance berbasis Java/ReactJS sebelumnya — lihat [[Finance - Bridging App]].*

- **Stack**: Go + Fiber v2 + MongoDB + Redis (backend) · Next.js 14 + TypeScript (frontend)
- **Path backend**: `services/integration` (bip-erp)
- **Path frontend**: `src/app/(main)/integration-accurate/` · `src/features/integration/accurate/` (erp-frontend)
- **Status backend**: ✅ Implemented — handler lengkap, route summary-report aktif; route direct-push di-comment
- **Status frontend**: ✅ Implemented — 6 halaman aktif (Sales, Income, Return × Shopee, TikTok)

---

## Endpoint / Fitur (Sudah Diimplementasikan)

### Frontend — Halaman & Route

| Route | Judul Halaman | Tipe Laporan | Channel |
|---|---|---|---|
| `/integration-accurate/sales/tiktok-shop` | Summary Sales TikTok Shop | SALES_INVOICE | TIKTOK |
| `/integration-accurate/sales/shopee` | Summary Sales Shopee | SALES_INVOICE | SHOPEE |
| `/integration-accurate/income/tiktok` | Summary Income TikTok Shop | INCOME | TIKTOK |
| `/integration-accurate/income/shopee` | Summary Income Shopee | INCOME | SHOPEE |
| `/integration-accurate/return/tiktok` | Summary Return TikTok Shop | SALES_RETURN | TIKTOK |
| `/integration-accurate/return/shopee` | Summary Return Shopee | SALES_RETURN | SHOPEE |

Setiap halaman list memiliki sub-route:
- `[id]` — halaman detail ringkasan (komponen `SummaryReportItemsDetailPage`)
- `[id]/items` — tabel baris item individual (komponen `IncomeDetailTableSection`)
- `[id]/invoices` — daftar invoice yang tergabung dalam ringkasan

#### Kolom Tabel Utama (List Ringkasan)

| Kolom | Keterangan |
|---|---|
| Order Date | Rentang tanggal transaksi (start / end) |
| Transaction Date | Tanggal transaksi yang dikirim ke Accurate |
| ID Number | Nomor invoice/return/income — ditampilkan sebagai collapsible cell |
| Shop Name | Nama toko marketplace |
| Status | Badge status API + nama service yang memproses (mis. `ACCURATE`) |

#### Kolom Tabel Detail Items

| Kolom | Keterangan |
|---|---|
| Order ID | Identifer order individual |
| Order Date | Tanggal order (formatted) |
| Item Name | Nama produk |
| SKU | SKU produk (badge) |
| Qty | Jumlah unit |
| Total Amount | Nilai dalam Rupiah |
| Status | Status pemrosesan item |

#### Filter & Pencarian

| Tipe Laporan | Filter Tersedia |
|---|---|
| Sales (SALES_INVOICE) | Shop ID, Sales Invoice Number, Date Range |
| Income (INCOME) | Shop ID, Sales Invoice Number, Income Number, Date Range |
| Return (SALES_RETURN) | Shop ID, Sales Invoice Number, Return Number, Date Range |

---

### Frontend — Hook & State Management

File hooks berada di `src/features/integration/accurate/hooks/`.

| Hook | File | Fungsi |
|---|---|---|
| `useTiktokPage` | `use-tiktok-page.ts` | State halaman Sales TikTok |
| `useShopeePage` | `use-shopee-page.ts` | State halaman Sales Shopee |
| `useIncomeTiktok` | `income/hooks/use-income-tiktok-page.ts` | State halaman Income TikTok |
| `useIncomeShopee` | `income/hooks/use-income-shopee-page.ts` | State halaman Income Shopee |
| `useReturnTiktok` | `return/hooks/use-return-tiktok-page.ts` | State halaman Return TikTok |
| `useReturnShopee` | `return/hooks/use-return-shopee-page.ts` | State halaman Return Shopee |
| `useFetchTransactionsSummary` | `use-fetch-transactions-summary.ts` | Fetch daftar ringkasan (shared) |
| `useCreateSummaryReport` | `use-create-summary-report.ts` | POST buat ringkasan baru |
| `useCreateSummaryModal` | `use-create-summary-modal.ts` | State modal form buat ringkasan |

State pagination & filter dikelola **in-memory** (`useState`) per halaman — **tidak** dipersist ke localStorage (tidak ada `PageStateContext`).

---

### Backend — API Transactions Summary Reports

Base path: `/transactions/summary/reports`

| Method | Path | Fungsi |
|---|---|---|
| `POST` | `/transactions/summary/reports` | Buat ringkasan baru — validasi + push task ke queue (record ditulis worker) |
| `GET` | `/transactions/summary/reports` | List ringkasan dengan filter & paginasi |
| `GET` | `/transactions/summary/reports/:id` | Detail satu ringkasan |
| `GET` | `/transactions/summary/reports/:id/items` | Baris item dalam ringkasan |
| `GET` | `/transactions/summary/reports/:id/invoices` | Daftar invoice dalam ringkasan |
| `POST` | `/transactions/summary/reports/:id/retry` | Retry ringkasan yang gagal |
| `POST` | `/transactions/summary/reports/:id/send/:service` | Kirim ke service eksternal (mis. `ACCURATE`) |
| `DELETE` | `/transactions/summary/reports/:id` | Hapus ringkasan |

#### Query Parameter GET List

| Parameter | Tipe | Keterangan |
|---|---|---|
| `page` | int | Nomor halaman (default: 1) |
| `page_size` | int | Jumlah per halaman |
| `report_type` | string | `SALES_INVOICE` / `SALES_RETURN` / `INCOME` |
| `channel` | string | `SHOPEE` / `TIKTOK` |
| `shop_id` | string | Filter berdasarkan ID toko |
| `sales_invoice_no` | string | Filter nomor invoice |
| `sales_return_no` | string | Filter nomor return |
| `income_no` | string | Filter nomor income |
| `time_from` | timestamp | Batas awal rentang waktu |
| `time_to` | timestamp | Batas akhir rentang waktu |
| `status` | string | Filter status |

#### Request Body POST Create Summary

```json
{
  "shop_id": "123456",
  "start_time": 1708032000,
  "end_time": 1708118400,
  "transaction_date": "2024-02-15",
  "channel": "SHOPEE",
  "report_type": "SALES_INVOICE"
}
```

#### Response Data Summary

```json
{
  "id": "report-uuid",
  "channel": "SHOPEE",
  "shop_id": "123456",
  "shop_name": "Nama Toko Shopee",
  "transaction_date": "2024-02-15",
  "report_type": "SALES_INVOICE",
  "invoice_no": "INV-001, INV-002",
  "status": "CREATED",
  "services": [
    {
      "service_name": "ACCURATE",
      "status": "SUCCESS",
      "identity_number": "ACC-12345",
      "sent_at": "2024-02-15T10:30:00Z"
    }
  ]
}
```

#### Status Ringkasan

| Status | Keterangan |
|---|---|
| `PENDING` | Antri di queue Redis (di-set saat create & retry) |
| `CREATING` | Worker mulai membuat record ringkasan |
| `PROCESSING` | Worker sedang memproses |
| `CREATED` | Berhasil dibuat |
| `FAILED` | Gagal — dapat di-retry |

---

### Backend — Accurate Settings API

Base path: `/accurate`

#### Shop Settings

| Method | Path | Fungsi |
|---|---|---|
| `GET` | `/accurate/settings/shops` | List konfigurasi toko |
| `POST` | `/accurate/settings/shops` | Tambah konfigurasi toko |
| `PUT` | `/accurate/settings/shops/:id` | Update konfigurasi toko |
| `DELETE` | `/accurate/settings/shops/:id` | Hapus konfigurasi toko |

**Entity Shop:**

| Field | Keterangan |
|---|---|
| `shop_id` | ID toko di marketplace |
| `shop_name` | Nama toko |
| `shop_code` | Kode internal toko |
| `invoice_code` | Prefix kode invoice Accurate |
| `channel` | `SHOPEE` / `TIKTOK` |
| `accurate_customer_id` | ID customer di Accurate untuk toko ini |
| `warehouse_name` | Nama gudang di Accurate |

Filter query yang tersedia: `id`, `shop_id`, `channel`, `shop_code`, `invoice_code`, `accurate_cust_id`, `warehouse_name`.

#### Product Mapping

| Method | Path | Fungsi |
|---|---|---|
| `GET` | `/accurate/products/list` | List mapping produk |
| `POST` | `/accurate/products` | Tambah mapping produk |
| `GET` | `/accurate/products/:id` | Detail mapping produk |
| `PUT` | `/accurate/products/:id` | Update mapping produk |
| `DELETE` | `/accurate/products/:id` | Hapus mapping produk |

Validasi saat create: item harus berupa **leaf SKU yang valid** dengan **harga aktif**. Field: `item_id`, `product_code`, `item_name`, `item_sku`, `item_base_price`, `item_type`.

#### Bank Account Mapping

| Method | Path | Fungsi |
|---|---|---|
| `GET` | `/accurate/bank-accounts/list` | List mapping rekening |
| `POST` | `/accurate/bank-accounts` | Tambah mapping rekening |
| `GET` | `/accurate/bank-accounts/:id` | Detail mapping rekening |
| `PUT` | `/accurate/bank-accounts/:id` | Update mapping rekening |
| `DELETE` | `/accurate/bank-accounts/:id` | Hapus mapping rekening |

Validasi: kode mata uang harus ISO 4217. Field: `bank_name`, `bank_code`, `branch_name`, `branch_code`, `account_name`, `account_number`, `account_currency`, `accurate_id`.

#### KV Configuration

| Method | Path | Fungsi |
|---|---|---|
| `GET` | `/accurate/settings/kv-configs/list` | List konfigurasi key-value |
| `POST` | `/accurate/settings/kv-configs` | Tambah konfigurasi |
| `GET` | `/accurate/settings/kv-configs/:id` | Detail konfigurasi |
| `PUT` | `/accurate/settings/kv-configs/:id` | Update konfigurasi |
| `DELETE` | `/accurate/settings/kv-configs/:id` | Hapus konfigurasi |

**Key yang diizinkan** (nilai string tersimpan = lowercase-hyphenated): `service-fee`, `discount`, `affiliate-commision` (sic — typo di kode, satu `m`), `shipping-cost`, `advertising-cost`.

---

### Accurate Client Library

File: `shared-library/accurate/accurate.go`

Autentikasi menggunakan **HMAC-SHA256** dengan header `X-API-Timestamp` dan `X-API-Signature`, serta Bearer token.

| Method | Fungsi |
|---|---|
| `GetDatabaseHost()` | Ambil host database Accurate spesifik akun via `POST /api/api-token.do` |
| `FetchListTotal(dbHost, endpoint, params, amountField)` | Pemanggil generik endpoint list Accurate |
| `GetMonthlySalesSummary(month, year)` | Total invoice, total return, dan net income bulan tertentu |
| `GetMonthlySalesInvoices(month, year)` | Total sales invoice periode tertentu |
| `GetMonthlyIncome(month, year)` | Kalkulasi net income periode tertentu |

Endpoint Accurate yang dipanggil:
- `POST {dbHost}/accurate/api/sales-invoice/list.do`
- `POST {dbHost}/accurate/api/sales-return/list.do`

---

## Alur Data (Data Flow)

### Alur Pembuatan Ringkasan Transaksi

```
1. Pengguna buka halaman (mis. /integration-accurate/sales/shopee)
2. Klik "Create New Summary"
3. Isi modal:
   - Pilih Shop (dropdown, filter by channel)
   - Pilih rentang tanggal (start_time, end_time)
   - Pilih transaction_date (tanggal di Accurate)
4. Frontend POST /api/integration/transactions/summary/reports
5. Backend buat record status PENDING di MongoDB
6. Redis queue menerima task TaskSummaryReport
7. Worker memproses: ambil data order dari Shopee/TikTok API
   sesuai rentang tanggal, normalisasi ke model terpadu
8. Record diupdate: CREATED (berhasil) atau FAILED (gagal)
9. Jika CREATED → pengguna dapat klik "Send to Accurate"
10. POST /transactions/summary/reports/:id/send/ACCURATE
11. Accurate client buat Sales Invoice / Sales Return di Accurate Online
12. Status services.ACCURATE diupdate: SUCCESS / FAILED
```

### Alur Retry

Jika status `FAILED`, pengguna dapat klik retry:
```
POST /transactions/summary/reports/:id/retry
→ Reset status ke PENDING → masuk queue ulang
```

---

## Konfigurasi & Konstanta

**File:** `src/features/integration/constants/accurate-integration.ts`

**Report Types:** `SALES_INVOICE`, `SALES_RETURN`, `INCOME`

**Channels:** `SHOPEE`, `TIKTOK`

**Daftar Toko Terdaftar:**
- Shopee: 8 toko terdaftar
- TikTok: 10 toko terdaftar

---

## Belum Diimplementasikan / Catatan

- **Route direct-push Accurate** (`/accurate/transactions/summary/create`, `.../send`, `.../status`) masih **di-comment** di `main.go`. Hanya handler **send** (`SendTransactionSummaryOrderToAccurate`) & **status** (`GetTransactionSummaryOrderStatus`) yang ada; handler **create** (`CreateTransactionSummaryOrder`) **belum ada** — route create menunjuk handler yang belum dibuat. Alur ini digantikan oleh `/transactions/summary/reports/:id/send/:service`.
- **Service selain Accurate** mengembalikan HTTP 501 "service integration not implemented yet" — enum `service` saat ini hanya mendukung `ACCURATE`.
- **Lazada, Tokopedia, KiriminAja** — tidak ada halaman integration-accurate untuk platform ini; hanya Shopee dan TikTok yang didukung pada Golang rewrite.
- **Tokopedia & KiriminAja** sudah ada di sistem Finance lama (Java) tapi **belum dimigrasi**.
- TODO kecil: indexing `time.Time` di MongoDB.
- **Auto-send ke Accurate** belum otomatis — pengguna harus trigger manual via tombol.
- **Endpoint belum didokumentasikan rinci**: `GET /transactions/summary/reports/group-by-status` & `GET /transactions/insight/demography` (terdaftar di `main.go`, belum dijabarkan di tabel atas).

---

### Gap dari Meeting 2026-06-26

> Sumber: [[MTG - 2026-06-26 Finance Service Modul]]

#### Produk & SKU

- **Bundling produk belum masuk Accurate** — validasi saat ini hanya menerima *leaf SKU* tunggal. Perlu logic baru untuk menangani bundle (1 item bundle → beberapa SKU komponen). SKU aktif sejak 17 Juni 2026.
- **Kategori produk** belum dipetakan ke Accurate: Kyuragb → Skincare; Beautyhack → Perawatan dan Kecantikan.
- **Departemen** belum dikonfigurasi: Marketing Beautyhack · Marketing KY+GB.
- **Project** di Accurate belum disetup untuk kedua departemen di atas.
- **List account Accurate** belum didokumentasikan: Rahardian · Afiani · Utvi.

#### Summary — Constraint Status Order

Saat `create summary`, sistem harus memvalidasi bahwa order memiliki timestamp yang relevan sesuai tipe summary:

| Tipe Summary | Status Order | Field wajib ada |
|---|---|---|
| `summaryInvoice` | TO_SHIP, SHIPPED | `shipped_at` |
| `summaryIncome` | — | `shipped_at`, `completed_at` |
| `summaryReturn` | CANCELLED | `completed_at`, `returned_at` |
| `summaryReturn` | RETURNED | `completed_at`, `returned_at` |

Status yang sudah ter-cover di data order: COMPLETED → `completed_at`; SHIPPED → `shipped_at`; CANCELLED → `cancelled_at`; RETURNED → `returned_at`. Validasi constraint ini **belum diimplementasikan** di backend.

#### Summary Multi-Toko

- Fitur **centang multi toko** (pilih beberapa shop sekaligus untuk income/sales/return) belum ada — saat ini satu summary = satu `shop_id`.

#### Bank & List Data Bank

- **List data bank dari Accurate** belum ada endpoint fetch-nya — pengguna tidak dapat memilih bank dari dropdown yang bersumber Accurate.

#### Modul Baru (Belum Ada Implementasi)

- **Piutang** — modul baru total:
  - Kolom tanggal jatuh tempo di invoice
  - Notifikasi otomatis pada H+14 dan H+60 setelah jatuh tempo
  - Baca piutang non-marketplace (diinput langsung di Accurate)
  - Dok target: buat `Finance - Piutang.md` (🔴 Stub)

- **Transaksi Logistik** — uang masuk/keluar dari logistik yang belum teridentifikasi:
  - Mekanisme: `order_id` → `related_order_id` (dari data logistik)
  - Blueprint **TBD — menunggu dokumen dari Utvi**
  - Dok target: buat `Finance - Transaksi Logistik.md` setelah blueprint ada

- **Mutasi Toko** — toko memiliki mutasi seperti rekening bank; perlu fitur baca transaksi masuk/keluar non-sales:
  - Dok target: buat `Finance - Mutasi Toko.md` (🟡 Konsep)

---

## Dependensi & Integrasi

- [[CORE - API Master Gateway]] — entry point semua request dari frontend ke service
- [[Microservices - Integration Service]] — service ini adalah rumah semua handler di atas
- [[External - Accurate]] — target bridging finansial (Accurate Online, autentikasi HMAC-SHA256)
- [[DB - Overview and Notes]] — MongoDB (data ringkasan) + Redis (queue key `queue:integration_tasks`; prefix Redis `srv:integration`, lock `srv:integration:lock`)
- **TikTok Shop API** — sumber data order untuk channel TIKTOK
- **Shopee API** — sumber data order untuk channel SHOPEE

---

## Dokumen Terkait

- [[Finance - Bridging App]] — sistem Finance lama (Java/ReactJS) yang sedang dimigrasi
- [[Finance - Big Pictures]] — overview domain Finance System
- [[Microservices - Integration Service]] — dokumentasi lengkap service (129 endpoint, semua modul)
- [[External - Accurate]] — detail integrasi Accurate Online
- [[Sales - Marketplace Integration]] — konteks bisnis sisi marketing
