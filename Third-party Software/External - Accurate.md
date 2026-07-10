## Catatan

*[Accurate](https://accurate.id/) (Accurate Online) adalah software akuntansi third-party — **sumber kebenaran pembukuan** Bharata (lihat [[ADR - 0001 Akuntansi via Accurate]]). ERP tidak membangun general ledger sendiri; data penjualan dijembatani ke Accurate.*

- **Status**: ✅ Implemented — dipakai [[Microservices - Integration Service]] (auto-sync RTS + manual send) dan sistem Finance lama ([[Finance - Bridging App]])
- **Endpoint prod**: langsung `zeus.accurate.id` (mode **API Token**: `Authorization: Bearer` + HMAC-SHA256 `X-Api-Timestamp`/`X-Api-Signature` dari secret key; tanpa sesi open-db). Env service integration: `ACCURATE_ACCOUNT_URL`, `ACCURATE_SECRET_KEY`, `ACCURATE_BEARER_TOKEN`.
- **Schema resmi**: OpenAPI `account.accurate.id/open-api/json.do` (diverifikasi 2026-07-10 untuk desain auto-sync).

## Fakta API yang dipakai integrasi (verified dari schema resmi)

- `POST /api/sales-invoice/save.do` — body JSON; required `customerNo` + `detailItem[]`; per baris required `itemNo` + `unitPrice`. **`itemNo` boleh duplikat antar baris** (dasar split baris per harga).
- **Edit dokumen** = header `id` (int internal Accurate) + per-baris `id`/`_status: delete`. Kirim ulang `number` sama **tidak terdokumentasi** sebagai upsert — jangan diandalkan.
- `GET /api/sales-invoice/detail.do` — menerima `id` **atau** `number`; sumber `id` internal + daftar `detailItem[].id` untuk protokol edit.
- `POST /api/sales-invoice/delete.do` — ada di client tapi **tidak dipakai** (kebijakan: faktur tak pernah dihapus; koreksi via edit/retur).
- `POST /api/sales-return/save.do` — retur; `InvoiceNumber` menunjuk faktur, `Number` dikosongkan (auto-nomor Accurate).
- **Bundle/paket**: tidak ada field bundle di invoice — bundle harus terdaftar sebagai **item paket di master Accurate**; ERP mem-mapping SKU marketplace → kode item via koleksi `accurate_products`.

## Konsumen di ERP

- [[Microservices - Integration Service]] — **auto-sync RTS** (Sales Invoice otomatis saat order pickup kurir, 1 faktur/toko/hari WIB) + manual send summary report (Sales Invoice/Return/Income) + master mapping shop/product/bank/kv.
- [[APP - Web ERP]] — menu `integration-accurate` (tab Auto-Sync monitoring + Panduan finance + summary report manual).

## Dokumen Terkait

- [[Microservices - Integration Service]] — bridging Sales Invoice/Return ke Accurate
- [[API - Integration Service]] — daftar endpoint (termasuk `/accurate/daily-invoices`)
- [[ADR - 0001 Akuntansi via Accurate]]
- [[Finance - Bridging App]] · [[Finance - Big Pictures]] — konsumen akuntansi (sistem lama)
- [[Microservices - Insentive Service]] · [[Sales - Marketplace Integration]]
