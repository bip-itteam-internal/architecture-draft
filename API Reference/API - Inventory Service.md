## Deskripsi

*Endpoint **inventory-service** (aset/inventaris GA: item, master data, repair history). Gateway: `/api/inventory/*`. Grounded ke `services/inventory`.*

- **Implementasi**: [[Microservices - Inventory Service]] · **Status**: ✅
- **Indeks**: [[API - Index]] · RBAC: `RequireGeneralAffair` (sebagian rute master/data-type & health bersifat publik di service).

## Master & data-type
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/master-items` | List master item | publik |
| GET | `/data-type/category` · `/electronics` · `/item-status` · `/repair` · `/service` · `/repair-status` · `/component-action` | Enum | publik |
| GET | `/categories` | Daftar kategori (registry, saran) | publik |
| POST | `/categories` | Daftar kategori baru (bebas-ketik, disimpan apa adanya) | GeneralAffair |
| GET | `/category-mapping` | Pemetaan kategori-ERP → golongan-Accurate (ADR-0037, dipakai FE Tab B/C) | publik |
| POST | `/category-mapping` | Upsert pemetaan (dedup `category_key`) | GeneralAffair |
| DELETE | `/category-mapping/:id` | Hapus pemetaan | GeneralAffair |
| GET | `/summary` | Ringkasan (jumlah + biaya) | publik |
| GET | `/health` | Health check | publik |

## Inventory items
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/item` | Buat item inventaris | GeneralAffair |
| GET | `/items` | List item | publik |
| GET/PATCH/DELETE | `/item/:id` | Detail/update/hapus item (PATCH juga = serahkan/ubah pemegang **& ceklis rekonsiliasi** via `accurate_asset_no`) | GeneralAffair |
| PATCH | `/item/:id/approve-handover` | SPV menyetujui serah-terima | **SPV penaung** (gate `SupervisedDepartments`, bukan GeneralAffair) |
| GET | `/item/master/:master_id/spec-template` | Template spesifikasi | GeneralAffair |
| POST/GET | `/item/upload/presigned-url` · `/item/upload/presigned-get` | Presigned upload/download dokumen (`purchase` · `arrived` · `handover`) | GeneralAffair |

## Repair history
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/item/repair/:item_id` | Buat record perbaikan | GeneralAffair |
| GET | `/item/repair/:item_id/all` · `/item/repair/:repair_id` | List/detail perbaikan | GeneralAffair |
| PATCH | `/item/repair/:repair_id` | Edit record perbaikan | GeneralAffair |

## Opname perlengkapan (ADR-0067)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/perlengkapan-opname` | List record opname (satu per `item_no`, opname terakhir) | GeneralAffair (`PermGaWork`) |
| POST | `/perlengkapan-opname` | Simpan hitung fisik satu barang (upsert per `item_no`) | GeneralAffair (`PermGaWork`) |

- Koleksi `ga_opname`. Staff GA meng-input **hitung fisik**; qty Accurate live diambil FE dari [[API - Integration Service]] (`/accurate/stocks/list?category=Perlengkapan`). Selisih & akurasi dihitung **di FE** (pola FASS), BE cuma MENYIMPAN.
- POST body `{item_no, nama?, qty_fisik, qty_accurate_snapshot, periode?}`; `item_no`+`qty_fisik` wajib (`qty_fisik ≥ 0`). `qty_accurate_snapshot` = qty Accurate yang **dilihat operator** saat menghitung — dipatok agar selisih tak bergeser oleh sync. `selisih = qty_fisik − qty_accurate_snapshot` dihitung & disimpan BE; `oleh` dari header `EmployeeID`.
- ⚠️ Upsert per `item_no` **tanpa unique index** (dua save konkuren item sama bisa duplikat; risiko rendah — alat single-user). Kunci unik ditunda sampai keputusan **periode** (`{item_no}` vs `{item_no, periode}`).

## Kontrak request & validasi (grounded)

Detail berikut grounded ke `services/inventory` (`controller.go`, `validation.go`).

### `POST /item` — buat item
- **Wajib**: `specs` (min 1, `key` & `value` non-kosong); `purchase_date`; `purchase_document`. Master item via `master_id` (pakai master lama) **atau** `item_name` + `item_category` (buat master baru — keduanya **bebas-ketik**, disimpan apa adanya; `item_category` juga didaftarkan ke registry `category`).
- **Pemegang OPSIONAL**: `held_by` boleh kosong → aset lahir "Tersedia di GA". Bila `held_by.department` diisi, `held_by.full_name` **wajib** (tolak `400 "fullname required"`).
- **Opsional**: `location`, `useful_life_years`, `arrived_date`, `arrived_document`, `purchase_price`, `notes`, `held_by.hold_period.assigned_at`/`revoked_at`.
- **ID ter-generate**: `INV-BIP-DDMMYY-NAMA-n` (tanggal dari `purchase_date` dibaca WIB).
- Dokumen (`purchase_document`/`arrived_document`) diverifikasi **ada di MinIO** sebelum simpan → tolak `400` bila objek tidak ditemukan.
- Grounded: `CreateInventory` (held_by opsional, `resolveCategory`, `ValidateDocumentsExists`) + `ValidateSpecs` + `generateUniqueID`.

### `PATCH /item/:id/approve-handover` — SPV menyetujui serah-terima
- **Otorisasi non-standar**: di **luar** grup `/item` (tak di-gate `RequireGeneralAffair`). Handler menolak `403` bila `held_by.handover_dept` **tidak** ada di `common.SupervisedDepartments(c)` (klaim `supervised_departments` / header `BIP-Supervised-Departments`). Tolak `400` bila status ≠ `menunggu_spv`.
- **Efek**: `held_by.known_by_spv` = nama SPV (dari body), `known_by_spv_id` dari header, `handover_status=disetujui`.
- Grounded: `ApproveHandover` + `common.SupervisedDepartments`.

### `PATCH /item/:id` — update (partial)
- **Partial update**: hanya field yang dikirim yang di-`$set` (`buildUpdateBson`); semua field opsional. `held_by` di-set hanya bila dikirim (tanpa validasi wajib, beda dari create). Balas `400 "No update fields"` bila tidak ada field.
- **Ceklis rekonsiliasi (ADR-0037)**: kirim `accurate_asset_no` untuk mengonfirmasi/lepas pasangan aset ke Aktiva Tetap Accurate. Non-kosong → `$set accurate_asset_no` + stempel `reconciled_at`; string kosong → `$unset` keduanya (lepas pasangan). `updated_at` tetap distempel walau perubahan hanya `$unset`.
- Grounded: `UpdateInventory` + `buildUpdateBson`.

### `GET /items` — list
- Mengembalikan **seluruh** item (⚠️ **tanpa pagination/search**). Hanya query `?status=` yang dihormati untuk filter server-side; `page` / `limit` / `search` **diabaikan**. Pencarian, filter, **dan paginasi** dilakukan **client-side** di frontend (list page: 10/hal). Respons menyertakan `held_by` (+ jejak serah-terima `handover_status`/`handover_by`/`known_by_spv`; ditampilkan kolom "Karyawan Pemegang", kosong → "Tersedia di GA"), serta `purchase_price`, `location`, `useful_life_years`, `accurate_asset_no`/`reconciled_at` — dipakai kolom, **export Excel** (FE, `lib/export.ts`), & **ceklis rekonsiliasi** (Tab Cocokkan). Nilai buku/penyusutan dihitung FE (estimasi garis lurus).
- Grounded: `ListInventory` + `InventoryListResponse`.

### `/category-mapping` — pemetaan kategori-ERP → golongan-Accurate (ADR-0037)
- `GET` (publik) balas seluruh pemetaan; `POST` (GA) upsert by `category_key` (kategori dinormalisasi `NormalizeCategoryKey` = lowercase + rapikan spasi) — kategori yang sama **menimpa**, bukan menggandakan; `DELETE /:id` (GA) hapus satu. Unique index `category_key`.
- Dipakai FE Tab B (editor) & Tab C (mengelompokkan aset per golongan untuk saran pasangan + matrix). Golongan Accurate diambil live dari `GET /accounting/fixed-assets` ([[API - Integration Service]]).
- Grounded: `ListCategoryMapping` · `UpsertCategoryMapping` · `DeleteCategoryMapping` (`mapping.go`).

### `GET /summary` — ringkasan (jumlah + biaya)
- Respons: `{ data: { overview: [{ total_assets, new_arrivals, total_purchase_cost }], by_category: [{ category, total }], by_status: [{ status, total }], by_department: [{ department, total }], total_repair_cost } }`. `new_arrivals` = item dengan `arrived_date` ≤ 30 hari terakhir. `total_purchase_cost` = Σ `purchase_price`; `total_repair_cost` = Σ biaya dari `repair_history`.
- Grounded: `GetSummary`.

### Upload dokumen (`POST /item/upload/presigned-url`)
- **Tipe diizinkan**: `image/*` dan `application/pdf`; **maks 4 MB**. Document valid: `purchase` (nota), `arrived` (foto barang), **`handover`** (dokumen serah terima — menggantikan catatan teks). Tolak `400 "file type not allowed"` / `"invalid service or document"` bila melanggar. Nama objek dibersihkan (`sanitizeObjectName`).
- **Integritas**: saat item disimpan, `ValidateDocumentsExists` memverifikasi objek benar-benar ada di MinIO (cegah `NoSuchKey`/referensi menggantung). Presigned di-sign untuk `MINIO_PUBLIC_BASE_URL` — pastikan skema/host cocok dengan yang diakses browser (isu *mixed-content* bila app HTTPS & MinIO HTTP).
- Grounded: `UploadRules` + `ValidateFileMeta` + `ValidateDocumentsExists`.

## Dokumen Terkait
- [[Microservices - Inventory Service]] · [[GA - Asset Loan & Room Booking]] · [[API - Index]] · [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] · [[API - Integration Service]]
