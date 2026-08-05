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
| GET | `/summary` | Ringkasan (jumlah + biaya) | publik |
| GET | `/health` | Health check | publik |

## Inventory items
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/item` | Buat item inventaris | GeneralAffair |
| GET | `/items` | List item | publik |
| GET/PATCH/DELETE | `/item/:id` | Detail/update/hapus item (PATCH juga = serahkan/ubah pemegang) | GeneralAffair |
| PATCH | `/item/:id/approve-handover` | SPV menyetujui serah-terima | **SPV penaung** (gate `SupervisedDepartments`, bukan GeneralAffair) |
| GET | `/item/master/:master_id/spec-template` | Template spesifikasi | GeneralAffair |
| POST/GET | `/item/upload/presigned-url` · `/item/upload/presigned-get` | Presigned upload/download dokumen (`purchase` · `arrived` · `handover`) | GeneralAffair |

## Repair history
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/item/repair/:item_id` | Buat record perbaikan | GeneralAffair |
| GET | `/item/repair/:item_id/all` · `/item/repair/:repair_id` | List/detail perbaikan | GeneralAffair |
| PATCH | `/item/repair/:repair_id` | Edit record perbaikan | GeneralAffair |

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
- Grounded: `UpdateInventory` + `buildUpdateBson`.

### `GET /items` — list
- Mengembalikan **seluruh** item (⚠️ **tanpa pagination/search**). Hanya query `?status=` yang dihormati untuk filter server-side; `page` / `limit` / `search` **diabaikan**. Pencarian, filter, **dan paginasi** dilakukan **client-side** di frontend (list page: 10/hal). Respons menyertakan `held_by` (+ jejak serah-terima `handover_status`/`handover_by`/`known_by_spv`; ditampilkan kolom "Karyawan Pemegang", kosong → "Tersedia di GA"), serta `purchase_price`, `location`, `useful_life_years` — dipakai kolom & **export Excel** (FE, `lib/export.ts`). Nilai buku/penyusutan dihitung FE (estimasi garis lurus).
- Grounded: `ListInventory` + `InventoryListResponse`.

### `GET /summary` — ringkasan (jumlah + biaya)
- Respons: `{ data: { overview: [{ total_assets, new_arrivals, total_purchase_cost }], by_category: [{ category, total }], by_status: [{ status, total }], by_department: [{ department, total }], total_repair_cost } }`. `new_arrivals` = item dengan `arrived_date` ≤ 30 hari terakhir. `total_purchase_cost` = Σ `purchase_price`; `total_repair_cost` = Σ biaya dari `repair_history`.
- Grounded: `GetSummary`.

### Upload dokumen (`POST /item/upload/presigned-url`)
- **Tipe diizinkan**: `image/*` dan `application/pdf`; **maks 4 MB**. Document valid: `purchase` (nota), `arrived` (foto barang), **`handover`** (dokumen serah terima — menggantikan catatan teks). Tolak `400 "file type not allowed"` / `"invalid service or document"` bila melanggar. Nama objek dibersihkan (`sanitizeObjectName`).
- **Integritas**: saat item disimpan, `ValidateDocumentsExists` memverifikasi objek benar-benar ada di MinIO (cegah `NoSuchKey`/referensi menggantung). Presigned di-sign untuk `MINIO_PUBLIC_BASE_URL` — pastikan skema/host cocok dengan yang diakses browser (isu *mixed-content* bila app HTTPS & MinIO HTTP).
- Grounded: `UploadRules` + `ValidateFileMeta` + `ValidateDocumentsExists`.

## Dokumen Terkait
- [[Microservices - Inventory Service]] · [[GA - Asset Loan & Room Booking]] · [[API - Index]]
