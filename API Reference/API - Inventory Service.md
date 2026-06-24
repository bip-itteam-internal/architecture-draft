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

## Dokumen Terkait
- [[Microservices - Inventory Service]] · [[GA - Asset Loan & Room Booking]] · [[API - Index]]
