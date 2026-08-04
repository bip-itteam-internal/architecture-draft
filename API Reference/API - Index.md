## Deskripsi

*Indeks **API Reference** bip-erp — daftar endpoint lengkap per service, grounded ke kode. Satu file per service di folder ini. Untuk konsep/arsitektur tiap service lihat dok `Microservices - *` / `CORE - *` terkait.*

- **Status**: ✅ Grounded ke kode (2026-06-24)
- **Sumber kebenaran**: kode service; bila berubah, sinkronkan via `/sync-docs`.

## Cara routing (penting)

- Semua request masuk lewat **[[CORE - API Master Gateway]]**. Service domain diakses sebagai **`/api/<module>/<path>`** → gateway memproxy ke service (path internal tanpa `/api/<module>`).
- **Auth**: gateway memvalidasi **JWT** lalu meneruskan identitas via header **`BIP-*`** (`BIP-Employee-ID`, `BIP-System-Roles`, dll). Service membaca header itu + RBAC ringan. Lihat [[CORE - SSO Flow]].
- **Open routes** (mis. sebagian notification/file): boleh tanpa JWT bila membawa **service key** `?key=...`.
- **Public/ext** (webhook, callback, fingerprint): lewat `/ext/*` & `/public/*` di gateway, tanpa JWT.
- Tiap service juga punya `GET /health` (di belakang gateway key).

## Daftar service

| Service | Prefix gateway | File | Implementasi |
|---|---|---|---|
| API Gateway | (root) | [[API - API Gateway]] | [[CORE - API Master Gateway]] |
| HRIS Orchestrator | `/api/hris/*` | [[API - HRIS Orchestrator]] | [[CORE - HRIS Orchestrator]] |
| IT Orchestrator | `/api/it/*` | [[API - IT Orchestrator]] | [[CORE - IT Orchestrator]] |
| Employee | `/api/employee/*` | [[API - Employee Service]] | [[Microservices - Employee Service]] |
| Attendance | `/api/attendance/*` | [[API - Attendance Service]] | [[Microservices - Attendance Service]] |
| Notification | `/api/notification/*` | [[API - Notification Service]] | [[Microservices - Notification Service]] |
| File | `/api/file/*` | [[API - File Service]] | [[Microservices - File Service]] |
| Insentive | `/api/insentive/*` | [[API - Insentive Service]] | [[Microservices - Insentive Service]] |
| Integration | `/api/integration/*` | [[API - Integration Service]] | [[Microservices - Integration Service]] |
| Inventory | `/api/inventory/*` | [[API - Inventory Service]] | [[Microservices - Inventory Service]] |
| TikTok Shop | `/api/tiktok-shop/*` | [[API - TikTok Shop Service]] | [[Microservices - TikTok Shop Service]] |
| Task Management | `/api/task-management/*` | [[API - Task Management Service]] | [[Microservices - Task Management Service]] |
| Manufacture | `/api/manufacture/*` | [[API - Manufacture Service]] | [[Microservices - Manufacture Service]] |
| Warehouse | `/api/warehouse/*` | [[API - Warehouse Service]] | [[Microservices - Warehouse Service]] |
| Recruitment | `/api/recruitment/*` | [[API - Recruitment Service]] | [[Microservices - Recruitment Service]] |
| Procurement | `/api/procurement/*` | [[API - Procurement Service]] | [[Microservices - Procurement Service]] |
| Form Builder ⚠️ | `/api/form-builder/*` | [[API - Form Builder Service]] | [[Microservices - Form Builder Service]] |
| Marketing Analytics | `/api/marketing-analytics/*` | [[API - Marketing Analytics Service]] | [[Microservices - Marketing Analytics Service]] |

> ⚠️ Form Builder sudah merged ke `main` (2026-08-01, PR #849) tapi **belum live di dev** — gateway dev masih membalas `400 unknown service`.

## Dokumen Terkait

- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]] · [[DB - Overview and Notes]] · [[HOMEPAGE]]
