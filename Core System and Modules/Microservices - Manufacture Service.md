## Deskripsi

*Microservice **manufacture-service** — WMS manufaktur (warehouse/produksi): master bahan baku & produk, stok, transaksi in/out, formula/BOM, produksi, material order, PO marketing/procurement, proposal koreksi, dan audit log. Master di-sync dari **Google Sheets** (via service account); data operasional (transaksi, stok) **sumber kebenaran di MongoDB**. Implementasi nyata dari konsep [[Manufacture - Stock & Material Management]].*

- **Stack**: Go + Fiber v2 + MongoDB (driver resmi) + shared-library; di belakang [[CORE - API Master Gateway]] (`/api/manufacture/*`), auth via header gateway (lihat [[CORE - SSO Flow]]).
- **Path di repo**: `bip-erp/services/manufacture/` · models: `bip-erp/shared-library/models/manufacture/models.go` · FE modul: `erp-frontend/src/features/manufacture/`.
- **Port**: `6978` (`MANUFACTURE_SERVICE_PORT`). **Database**: `manufacture_db` (Mongo per-service, **replica set 1-node** `rs-manufacture` + keyfile auth).
- **Status**: ✅ Implemented (Fase 1 master/stok/transaksi/formula sync jalan; entitas produksi/PO/proposal ada di kode).
- **API**: [[API - Manufacture Service]].

## Endpoint / Fitur (Sudah Diimplementasikan)

Daftar rute lengkap di [[API - Manufacture Service]]. Ringkas:

- **Master bahan & produk** — list/detail + `POST /sync` (tarik dari Google Sheet) + `PATCH status` (active/discontinued, dengan audit). **Master bahan** kini juga punya **CRUD manual** (`POST`/`PUT`/`DELETE /master-bahan[/:kode]`): item buatan WMS ditandai `source:"manual"` dan **dikecualikan dari stale-marking** saat sync (tidak hilang saat sync berikutnya).
- **Stok** — snapshot per kode + `POST /stok/reconcile` (rekonsiliasi snapshot vs transaksi) + `GET /stok/sektor` (stok riil per gudang: utama/tinggar/sadewa, breakdown jenis barang → satuan; konsumen = card Status Sektor di Dashboard FE).
- **Saldo awal bulanan** — `manufacture_saldo_awal_bulanan`: snapshot stok tiap awal bulan (terpisah dari master barang), dibuat otomatis oleh goroutine ticker (saat boot + tiap 6 jam, idempoten per bulan — service mati saat tanggal 1 terbackfill saat nyala) atau manual via `POST /saldo-awal/snapshot`.
- **Transaksi** — INBOUND/OUTBOUND; mengubah stok **atomik** (Mongo transaction). Validasi kode menerima **master bahan baku ATAU produk jadi** (`master_product`) → transaksi barang jadi (FG in/out) tidak lagi ditolak. OUTBOUND dengan stok tidak cukup ditolak 422 (**stok tidak boleh minus**). `PATCH /transaksi/:id/status` mengubah `detail.status` (alur terima SJ Kirim Produk: IN TRANSIT → DELIVERED). Field UI tambahan (Qty QC, PIC, produk jadi, formula, dll) disimpan apa adanya di field fleksibel `detail`.
- **Formula/BOM** — CRUD + `POST /formula/sync` (tarik resep dari Sheet via service account).
- **Produksi** — order produksi (konsumsi stok) + production-log (catatan tanpa konsumsi).
- **PO & Proposal** — marketing-po, procurement-po (status workflow + audit), proposal approve/reject. Proposal dipakai untuk **deviasi pemakaian fisik vs teori BOM** pada keluar-produksi: FE membuat proposal `PENDING_PPIC` (transaksi belum ada), approval dua tahap PPIC → SPV; saat `APPLIED` backend insert transaksi + potong stok dengan filter kondisional `stok_sekarang >= qty` (ditolak 409 bila akan minus).
- **Audit log** — `GET /audit-log` (siapa mengubah apa, per aksi/target).

## Model Data (`manufacture_db`)

14 collection (prefix `manufacture_`), grounded ke `models.go`:

- `manufacture_master_bahan` — master bahan baku (`_id`=kode, nama, kategori, satuan, min_stok, stok_awal dari Sheet, status app-managed, `source` `sheet`/`manual`).
- `manufacture_master_product` — master produk/bahan kemas (kode, jenis_barang, kategori_produk, status).
- `manufacture_stok` — snapshot stok per kode.
- `manufacture_transaksi` — transaksi in/out (sumber kebenaran pergerakan stok) + `detail` (bson.M, field UI tambahan).
- `manufacture_formula` — resep/BOM (product_name + ingredients[kode_bahan, nama, qty_needed]). Catatan: `product_sku` kosong dari sync Sheet → pencocokan FE via **nama produk**.
- `manufacture_sync_log` — riwayat sync Sheet (tipe: master/product/formula).
- `manufacture_production_log` (+`detail`) · `manufacture_material_order` · `manufacture_marketing_po` · `manufacture_procurement_po` (+`detail`, menampung daftar `items` saat 1 permintaan berisi banyak bahan) · `manufacture_proposal`.
- `manufacture_saldo_awal_bulanan` — snapshot saldo awal per bulan (`_id` = `kode|YYYY-MM`, kode, nama, bulan, qty) — memisahkan saldo awal bulanan dari data master barang.
- `manufacture_audit_log` — jejak perubahan oleh user (dari header `BIP-Employee-ID`/`BIP-Username`).
- `manufacture_resi` — master resi retur ekspedisi (no resi, market, ekspedisi, items) — sumber scan form Return & Keluar FG.

## Keputusan Teknis (grounded)

- **Stok = opening-balance-as-transaction + reconcile**: stok awal dari Sheet (STOK GUDANG) di-seed sebagai transaksi OPENING, bukan snapshot langsung → rekonsiliasi konsisten (snapshot = jumlah semua transaksi). Mutasi stok pakai **Mongo multi-document transaction** (butuh replica set; itu sebab `manufacture_db` dijadikan RS 1-node + keyfile).
- **Master dari Google Sheets (3 file terpisah)** via **service account** (`SHEETS_SA_KEY` base64, scope readonly): bahan baku, produk, formula. Tiap sync upsert ke koleksi + catat sync-log + audit. Service account lebih aman dari gviz publik (sheet tak perlu "anyone with link"). Sheet wajib di-share ke email SA (Viewer).
- **Tagged logging** `[Manufacture <Event>]` untuk identifikasi di monitoring Docker.
- **Audit log** merekam user login terakhir yang mengubah data di tab mana pun (header gateway).
- **Field `detail` (bson.M) sebagai blob fleksibel**: model Go inti (transaksi, production-log, procurement-po) minimal, sedangkan UI punya banyak field tambahan (QC, PIC, checklist, daftar bahan). Field tersebut disimpan apa adanya di `detail` agar log/ledger/arsip tetap utuh setelah reload — tanpa menambah kolom per-field di model.
- **Item master manual kebal sync**: master-bahan buatan WMS (`source:"manual"`) dikecualikan dari penandaan `stale` saat `SyncMaster`, jadi tidak terhapus oleh sync Google Sheet.
- **Mapping gudang = per-spreadsheet** (tidak ada kolom gudang per baris di Sheet): spreadsheet master bahan ("MUTASI GUDANG MANUFACTURE") = **Gudang Utama** (bahan baku+kemas); spreadsheet master barang ("GUDANG TINGGAR JAYA") = **Gudang Tinggar** (kemas+barang jadi); **Gudang Sadewa** (titipan) tidak punya sheet — dihitung dari net transaksi bergudang-simpan "sadewa". Kode yang terdaftar di dua master terhitung di dua gudang (aproksimasi; stok per-gudang sejati masih TBD).
- **Aturan stok & approval keluar-produksi**: stok **tidak boleh minus** (blokir di FE + validasi 422 backend + filter kondisional saat proposal APPLIED). Approval PPIC→SPV terpicu oleh **deviasi fisik pemakaian vs teori BOM** (bukan oleh kekurangan stok).
- **Rantai alur FE saling tereferensi & anti-duplikat**: keluar-produksi membuat `grupDokumen` (RM-OUT-BOM) → Laporan Hasil Produksi mengambil grup (menyimpan `grupDokumen`; grup terpakai disembunyikan) & Qty Masuk Gudang menciptakan stok FG (`PROD-<batch>`) → Kirim Produk mengambil laporan (menyimpan `refLaporanProduksi`; laporan terpakai disembunyikan; OUTBOUND, SJ IN TRANSIT) → Input Gudang FG menerima SJ (PATCH status DELIVERED; INBOUND + gudang simpan Utama/Tinggar/Sadewa) → Masuk Kembali mengembalikan sisa bahan per grup via checklist. 
- **Akses modul WMS**: halaman `/manufacture` dibatasi system role `manufacture` (guard FE `ManufactureGuard`), supervisor IT super-akses; tombol approve di menu Persetujuan & Akun mengikuti role `manufacture: ppic`/`supervisor` dari cookie `system_roles` (verifikasi role backend belum ada — lihat temuan audit).
- **FE**: modul `manufacture` di [[APP - Web ERP]] (Next.js, `erp-frontend/src/features/manufacture`), 10 view (gudang bahan baku/jadi, stok, produksi, PO, KPI, dll). Konversi field **dua arah**: tulis (legacy camelCase → Go snake_case + `_id`), baca (Go snake_case → legacy camelCase) lewat mapper di container — tanpa ini create gagal validasi (`id`/`product_sku` wajib) & arsip tampil kosong.

## Belum Diimplementasikan / Catatan (TBD)

- Perhitungan kebutuhan→kekurangan otomatis dari rencana produksi (Fase 2 di [[Manufacture - Stock & Material Management]]) — sebagian (formula ada, planning belum penuh).
- Multi-gudang/lokasi + karantina ED, stock opname digital, integrasi [[External - Accurate]] — masih konsep.
- Master `stok_awal` tersimpan 0 saat upsert master (kosmetik; snapshot stok benar ter-seed dari STOK GUDANG).
- **Temuan audit kode** (authz, race stok, mapper FE, seed atomik) terdaftar di [[Manufacture - Issue Code Audit 2026-06]] — perbaikan terjadwal.

## Dependensi & Integrasi

- [[CORE - API Master Gateway]] (routing + inject header identitas) · [[CORE - SSO Flow]] (auth).
- [[Microservices - Employee Service]] — sumber identitas/role (audit).
- [[GA - Procurement System]] — kekurangan → pengadaan (rencana).
- [[External - Accurate]] — tarik stok awal (rencana, hybrid bertahap).
- Google Sheets (master bahan/produk/formula) — sumber master via service account.

## Dokumen Terkait

- [[Manufacture - Stock & Material Management]] (konsep/desain) · [[API - Manufacture Service]] (endpoint)
- [[DB - Overview and Notes]] · [[APP - Web ERP]]
