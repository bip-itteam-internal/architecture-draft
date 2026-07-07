## Deskripsi

*Endpoint **inventory-service** (aset/inventaris GA: item, master data, repair history). Gateway: `/api/inventory/*`. Grounded ke `services/inventory`.*

- **Implementasi**: [[Microservices - Inventory Service]] · **Status**: ✅
- **Indeks**: [[API - Index]] · RBAC: `RequireGeneralAffair` (sebagian rute master/data-type & health bersifat publik di service).

## Master & data-type
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/master-items` | List master item | publik |
| GET | `/data-type/category` · `/electronics` · `/item-status` · `/repair` · `/service` · `/repair-status` · `/component-action` | Enum | publik |
| GET | `/summary` | Ringkasan (per category/status/department) | publik |
| GET | `/health` | Health check | publik |

## Inventory items
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/item` | Buat item inventaris | GeneralAffair |
| GET | `/items` | List item | publik |
| GET/PATCH/DELETE | `/item/:id` | Detail/update/hapus item | GeneralAffair |
| GET | `/item/master/:master_id/spec-template` | Template spesifikasi | GeneralAffair |
| POST/GET | `/item/upload/presigned-url` · `/item/upload/presigned-get` | Presigned upload/download dokumen | GeneralAffair |

## Repair history
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/item/repair/:item_id` | Buat record perbaikan | GeneralAffair |
| GET | `/item/repair/:item_id/all` · `/item/repair/:repair_id` | List/detail perbaikan | GeneralAffair |

## Kontrak request & validasi (grounded)

Detail berikut grounded ke `services/inventory` (`controller.go`, `validation.go`).

### `POST /item` — buat item
- **Wajib**: `held_by.department` **dan** `held_by.full_name` (tolak `400 "HeldBy data is required"` / `"fullname required"` bila kosong); `specs` (min 1, `key` & `value` non-kosong); `purchase_date`; `purchase_document`. Master item via `master_id` (pakai master lama) **atau** `item_name` + `item_category` (buat master baru).
- **Opsional**: `arrived_date`, `arrived_document`, `held_by.hold_period.assigned_at` / `revoked_at`, `purchase_price`, `notes`.
- Grounded: `CreateInventory` (cek held_by) + `ValidateSpecs`.

### `PATCH /item/:id` — update (partial)
- **Partial update**: hanya field yang dikirim yang di-`$set` (`buildUpdateBson`); semua field opsional. `held_by` di-set hanya bila dikirim (tanpa validasi wajib, beda dari create). Balas `400 "No update fields"` bila tidak ada field.
- Grounded: `UpdateInventory` + `buildUpdateBson`.

### `GET /items` — list
- Mengembalikan **seluruh** item (⚠️ **tanpa pagination/search**). Hanya query `?status=` yang dihormati untuk filter server-side; `page` / `limit` / `search` **diabaikan**. Pencarian & filter lain dilakukan **client-side** di frontend.
- Grounded: `ListInventory`.

### `GET /summary` — ringkasan (berbasis jumlah)
- Respons: `{ data: { overview: [{ total_assets, new_arrivals }], by_category: [{ category, total }], by_status: [{ status, total }], by_department: [{ department, total }] } }`. `new_arrivals` = item dengan `arrived_date` ≤ 30 hari terakhir. Tidak ada agregasi nilai/harga.
- Grounded: `GetSummary`.

### Upload dokumen (`POST /item/upload/presigned-url`)
- **Tipe diizinkan**: `image/*` dan `application/pdf`; **maks 4 MB** (berlaku untuk dokumen `purchase` & `arrived`). Tolak `400 "file type not allowed"` / `"file size exceeds limit"` bila melanggar.
- Grounded: `UploadRules` + `ValidateFileMeta`.

## Dokumen Terkait
- [[Microservices - Inventory Service]] · [[GA - Asset Loan & Room Booking]] · [[API - Index]]
