# Microservices - Inventory Service

## Deskripsi

_Inventory Service adalah microservice untuk manajemen **aset/inventaris General Affairs (GA)** — mengelola item peralatan beserta spesifikasi, pemegang (heldBy), dokumen pembelian/kedatangan, serta riwayat perbaikan/maintenance. Fokusnya adalah pelacakan **aset** (asset tracking), bukan stok-kuantitas gudang._

- **Stack:** Go + Fiber v2 + MongoDB + MinIO
- **Path:** `services/inventory`
- **Status**: ✅ Implemented penuh

## Endpoint / Fitur (Sudah Diimplementasikan)

- **Health check:** `GET /health`
- **Data-type / enum master:** `GET /master-items`, `GET /data-type/category`, `GET /data-type/electronics`, `GET /data-type/item-status`, `GET /data-type/repair`, `GET /data-type/service`, `GET /data-type/repair-status`, `GET /data-type/component-action`
- **Kategori (registry `category`):** `GET /categories` (daftar untuk saran), `POST /categories` (daftar kategori baru — gate `RequireGeneralAffair`). Kategori bersifat **bebas-ketik**; disimpan apa adanya, dedup case-insensitive (`name_key`). Di-seed saat startup (`seedCategories`, unique index `name_key`). Lihat Catatan.
- **Group `/item`** (dulu di-gate `RequireGeneralAffair`; sejak branch `feat/ga-permission-set` — ⚠️ belum merge — berlantai izin `ga.view`, dengan `RequireGeneralAffair` jadi fallback kill-switch. Rute tulis di dalamnya menuntut `ga.work` di atasnya; lihat [[CORE - RBAC dan Permission Set]]):
  - `GET /item/master/:master_id/spec-template` — ambil template spesifikasi per master
  - `POST /item/` — create item; auto-create/reuse `DataMaster`, generate ID pola **`INV-BIP-DDMMYY-NAMA-n`** (DDMMYY dari `purchase_date` dibaca **WIB**; `NAMA` = `item_name` di-UPPERCASE tanpa spasi, maks 20 char; `n` = increment). Validasi spec; **pemegang (`held_by`) OPSIONAL** (aset boleh lahir "Tersedia di GA", diserahkan belakangan); simpan `location` & `useful_life_years` (opsional); verifikasi dokumen ada di MinIO sebelum simpan
  - `POST /item/upload/presigned-url` + `GET /item/upload/presigned-get` — MinIO presigned URL (upload/get); document yang diizinkan: `purchase` · `arrived` · **`handover`** · **`repair`** (bukti nota perbaikan, ditambah 2026-08-22); allowlist di `UploadRules["inventory"]` (`validation.go`) — kirim `document` di luar daftar dibalas **400** "invalid service or document"; nama objek dibersihkan (`sanitizeObjectName`)
  - `GET /item/:id` — detail item (termasuk `location`, `useful_life_years`, jejak serah-terima, dokumen, `accurate_asset_no`/`reconciled_at`)
  - `PATCH /item/:id` — partial update (juga jalur **serahkan/ubah pemegang**: kirim `held_by`; **dan ceklis rekonsiliasi**: kirim `accurate_asset_no` — non-kosong → stempel `reconciled_at`, kosong → lepas pasangan)
  - `DELETE /item/:id` — hapus item
- **List item:** `GET /items` — list `$lookup` ke master + filter `?status`. Respons memuat `held_by` (+ jejak serah-terima), `purchase_price`, `location`, `useful_life_years`, `accurate_asset_no`/`reconciled_at` (dipakai kolom, **export Excel**, & ceklis rekonsiliasi di FE)
- **Pemetaan kategori → golongan Accurate** (ADR-0037): `GET /category-mapping` (publik, dipakai FE Tab B/C), `POST /category-mapping` (upsert, dedup `category_key`), `DELETE /category-mapping/:id` — dua terakhir gate `RequireGeneralAffair`. Unique index `category_key` (`ensureCategoryMappingIndex`). ⚠️ **Sejak [[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]] (2026-08-22) editor UI-nya DIGANTI** padanan langsung barang→aset berbasis nama; koleksi + rute ini **tetap ada & masih dibaca tab Cocokkan** untuk pengelompokan saran (data lama), tetapi **tak ada lagi UI menambah** pemetaan baru
- **Serah-terima aset:** `PATCH /item/:id/approve-handover` — **persetujuan SPV** atas penyerahan. Gate manual di handler: departemen penyerah (`held_by.handover_dept`) harus ada di cakupan supervisi pemanggil (`common.SupervisedDepartments`, header `BIP-Supervised-Departments`). Set `handover_status=disetujui` + rekam SPV penyetuju
	- ⚠️ **KOREKSI 2026-08-11: dok ini sebelumnya menyatakan rutenya "di luar grup `/item`" dan "bukan di-gate `RequireGeneralAffair`". Keduanya KELIRU**, dan dibuktikan dengan uji Fiber, bukan dibaca dari kode sekilas. Middleware grup Fiber berlaku **per-PREFIX, bukan per-variabel**: setiap rute berawalan `/item` yang didaftarkan setelah `app.Group("/item", ...)` ikut melewatinya, tak peduli dipasang lewat `inv` atau `app`.
	- **Akibatnya SPV departemen penyerah yang bukan orang GA tak pernah bisa menyetujui** — kebalikan dari maksud desainnya, dan tak bergejala: tombolnya ada, balasannya 403. Gate manual di handler tak pernah sempat dinilai karena permintaannya sudah ditolak lebih dulu.
	- Perilaku ini sudah begitu **sebelum** modul `ga` dikatalogkan (lantainya dulu `RequireGeneralAffair`, kini `ga.view` yang setara selama fase satu), jadi penggerbangan izin tidak memperburuknya. Memindahkan rutenya keluar dari prefix adalah perbaikan tersendiri: ia **melebarkan** akses, jadi menuntut keputusan dan pengukuran. Kenyataannya dipatok uji `TestRuteBerprefixItemIkutMelewatiGerbangGrup` supaya perbaikan kelak terlihat sebagai perubahan yang disengaja.
- **Repair history** (`/item/repair`):
  - `POST /item/repair/:item_id` — tambah riwayat perbaikan; sinkron status ke item induk
  - `GET /item/repair/:item_id/all` — semua riwayat perbaikan untuk satu item
  - `GET /item/repair/:repair_id` — detail satu record perbaikan
  - `PATCH /item/repair/:repair_id` — edit satu record perbaikan (`UpdateRepairHistory`)
  - **Bukti nota (✅ 2026-08-22)**: `CreateRepairHistory`/`UpdateRepairHistory` menerima & menyimpan `documents` (`[]common.MinIOFile`, **opsional, boleh >1**) — lampiran nota perbaikan. Di-upload lewat presigned `document:"repair"` lalu **diverifikasi ada di MinIO** (`ValidateDocumentsExists`, anti `NoSuchKey`; samakan pola `CreateInventory`). FE menampilkannya di kartu riwayat (`InfoDocument`)
- **Summary / reporting:** `GET /summary` — agregasi `$facet` per category/status/department + new-arrivals 30 hari terakhir + **agregasi biaya** (`total_purchase_cost` dari `purchase_price`, `total_repair_cost` dari `repair_history`)

## Belum Diimplementasikan / Catatan

- Tidak ada stub — CRUD lengkap, workflow repair, dan reporting sudah komplet.
- `InternalURL` kosong; service ini **tidak memanggil service lain**.
- **Kategori & nama barang bebas-ketik**: frontend kini memakai input teks manual (dropdown/saran dihapus). Backend tetap mendaftarkan kategori ke koleksi `category` via `resolveCategory` saat create, sehingga koleksi & endpoint `/categories` kini **vestigial** untuk UI (masih terisi, tidak lagi dibaca dropdown). Nama & kategori disimpan **apa adanya** (trim + rapikan spasi), dedup master **case-insensitive**; hanya **ID** yang di-UPPERCASE.
- **Integritas dokumen (anti `NoSuchKey`)**: `CreateInventory`/`UpdateInventory` memanggil `ValidateDocumentsExists` (MinIO `StatObject`) → tolak `400` bila objek tidak ada, mencegah referensi menggantung. `GeneratePresignedURL` membersihkan nama objek (`sanitizeObjectName`). Catatan operasional: presigned di-sign untuk `MINIO_PUBLIC_BASE_URL`; jika app HTTPS sementara nilai ini HTTP → upload diblokir *mixed-content* (perbaiki di infra, bukan kode).
- **ID pakai WIB**: komponen tanggal ID dibaca `time.FixedZone("WIB", +7)` agar tidak mundur 1 hari dari tanggal yang tampil (frontend kirim ISO UTC).
- **Serah-terima aset (`HeldBy`)**: alur = **Serahkan/Ubah Pemegang** (GA, via `PATCH /item/:id`) → `handover_status=menunggu_spv`, rekam penyerah (`handover_by`) & departemen penyerah (`handover_dept`) → **SPV penaung menyetujui** (`PATCH /item/:id/approve-handover`) → rekam `known_by_spv` + `handover_status=disetujui`. **Tarik/Kembalikan** = kosongkan pemegang + set `revoked_at` → "Tersedia di GA". Catatan pengganti tanda tangan surat serah terima = **`handover_document`** (upload, menggantikan catatan teks lama `handover_notes` yang kini deprecated).
- **Lokasi & penyusutan**: `InventoryItem` + `location` (string) & `useful_life_years` (opsional). **Nilai buku & penyusutan/tahun TIDAK disimpan** — dihitung di **frontend** (garis lurus, residu 0) sebagai *estimasi operasional GA*, bukan angka pembukuan (akuntansi via Accurate, lihat [[ADR - 0001 Akuntansi via Accurate]]).
- **Export**: daftar aset diekspor ke Excel **client-side** (frontend, `lib/export.ts`/exceljs) dari data `GET /items` yang terfilter — tak ada endpoint export di service.
- **Rekonsiliasi aset ↔ Accurate (ADR-0037; §pencocokan & skor sejak 2026-08-22 di-supersede [[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]])**: `InventoryItem` + `accurate_asset_no` & `reconciled_at`. **Komputasi 100% di frontend** — service ini **tetap tak memanggil siapa pun**: FE mengomposisi `GET /items` (inventory) + `GET /accounting/fixed-assets` ([[Microservices - Integration Service]]), memasangkan barang ERP ↔ aset Accurate **berbasis NAMA** (nama Accurate kini dari field `description`, [[Microservices - Integration Service]]) & menyimpan pasangan lewat `PATCH /item/:id` (`accurate_asset_no`). Padanan dilakukan di **dua layar yang menulis kunci sama**: **Pengaturan Aset** (editor padanan langsung barang→aset, pengganti editor kategori→golongan) dan tab **Cocokkan** (saran by nama + tandai ⚠ padanan lama yang salah + tombol Ganti). Skor akurasi/cakupan (ERP-only=100%) kini menilai **kesamaan DATA: harga + tanggal, TANPA golongan** (ADR-0049 §4). Koleksi `asset_category_mapping` jadi vestigial (lihat baris **Pemetaan kategori → golongan** di atas). **Feed KPI (Fase 2) belum** — dan saat rilis wajib membuang golongan sesuai ADR-0049.

## Dependencies & Integrasi

- **MongoDB** — collection: `inventory`, `data_master`, `repair_history`, `category`, `asset_category_mapping`.
- **MinIO** — diakses langsung untuk presigned URL serta upload image/PDF (limit 4MB); objek diverifikasi ada sebelum referensinya disimpan. Lihat [[Microservices - File Service]].
- Diekspos via gateway — lihat [[CORE - API Master Gateway]].
- Skema database — lihat [[DB - Overview and Notes]].

## Dokumen Terkait

- [[GA - Inventory Management]] · [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] · [[Microservices - Integration Service]] · [[External - Accurate]]
