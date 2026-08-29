## Deskripsi

*Indeks **API Reference** bip-erp — daftar endpoint lengkap per service, grounded ke kode. Satu file per service di folder ini. Untuk konsep/arsitektur tiap service lihat dok `Microservices - *` / `CORE - *` terkait.*

- **Status**: ✅ Grounded ke kode (disegarkan 2026-08-26: Payroll ditambahkan, tiga service tanpa berkas `API -` didaftar eksplisit)
- **Sumber kebenaran**: kode service; bila berubah, sinkronkan via `/sync-docs`.

## Cara routing (penting)

- Semua request masuk lewat **[[CORE - API Master Gateway]]**. Service domain diakses sebagai **`/api/<module>/<path>`** → gateway memproxy ke service (path internal tanpa `/api/<module>`).
- **Auth**: gateway memvalidasi **JWT** lalu meneruskan identitas via header **`BIP-*`** (`BIP-Employee-ID`, `BIP-System-Roles`, dll). Service membaca header itu + RBAC ringan. Lihat [[CORE - SSO Flow]].
- **Open routes** (mis. sebagian notification/file): boleh tanpa JWT bila membawa **service key** `?key=...`.
- **Public/ext** (webhook, callback, fingerprint): lewat `/ext/*` & `/public/*` di gateway, tanpa JWT.
- Tiap service juga punya `GET /health` (di belakang gateway key).

> ⛔ **Satu service sengaja TIDAK lewat gateway, dan itu bukan kelalaian.** [[Microservices - Vault MCP Service]] dipaparkan langsung sebagai `mcp.bharatainternasional.com` lewat Nginx Proxy Manager, karena Claude menyambung dari infrastruktur cloud Anthropic dan gateway menuntut ERP JWT di `/api/*` sementara token yang dipegang Claude bukan itu. Gerbangnya OAuth 2.1, bukan `INTERNAL_GATEWAY_KEY`. Endpoint-nya tercatat di dok arsitekturnya, bukan di folder ini, karena ia tak punya prefix gateway untuk didaftarkan. Jangan "membetulkannya" dengan menambahkan baris ke tabel di bawah.

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
| Finance | `/api/finance/*` | [[API - Finance Service]] | [[Finance - Rancangan Finance Service]] |
| Inventory | `/api/inventory/*` | [[API - Inventory Service]] | [[Microservices - Inventory Service]] |
| TikTok Shop | `/api/tiktok-shop/*` | [[API - TikTok Shop Service]] | [[Microservices - TikTok Shop Service]] |
| Task Management | `/api/task-management/*` | [[API - Task Management Service]] | [[Microservices - Task Management Service]] |
| Manufacture | `/api/manufacture/*` | [[API - Manufacture Service]] | [[Microservices - Manufacture Service]] |
| Warehouse | `/api/warehouse/*` | [[API - Warehouse Service]] | [[Microservices - Warehouse Service]] |
| Recruitment | `/api/recruitment/*` | [[API - Recruitment Service]] | [[Microservices - Recruitment Service]] |
| Procurement | `/api/procurement/*` | [[API - Procurement Service]] | [[Microservices - Procurement Service]] |
| Form Builder ⚠️ | `/api/form-builder/*` | [[API - Form Builder Service]] | [[Microservices - Form Builder Service]] |
| Marketing Analytics | `/api/marketing-analytics/*` | [[API - Marketing Analytics Service]] | [[Microservices - Marketing Analytics Service]] |
| Learning | `/api/learning/*` | [[API - Learning Service]] | [[Microservices - Learning Service]] |
| Payroll | `/api/payroll/*` | [[API - Payroll Service]] | [[Microservices - Payroll Service]] |

> ⚠️ Form Builder sudah merged ke `main` (2026-08-01, PR #849) tapi **belum live di dev** — gateway dev masih membalas `400 unknown service`.

> **Finance sengaja memetakan ke dok domain, bukan `Microservices -`.** Arsitektur finance-service hidup di [[Finance - Rancangan Finance Service]] (folder Finance System), tidak di Core System and Modules seperti service lain. Itu keputusan yang berlaku, bukan berkas yang hilang — jangan membuat `Microservices - Finance Service` sebagai "pelengkap", karena yang lahir adalah sumber kebenaran kedua yang pasti menyimpang.

### Service tanpa berkas `API -` (per audit 2026-08-26)

Empat service terdaftar di gateway tetapi belum punya daftar endpoint di folder ini. **Payroll sudah ditutup** pada audit itu; tiga sisanya belum, dan didaftar di sini supaya ketiadaannya terlihat alih-alih terbaca sebagai "service-nya memang tak punya endpoint".

| Service | Dok arsitektur | Keadaan |
|---|---|---|
| Calendar | [[Microservices - Calendar Service]] | Rute per-endpoint tercatat di dok arsitekturnya, belum dipisah jadi berkas `API -` |
| HRD Document | [[Microservices - HRD Document Service]] | idem |
| Monitoring | [[Microservices - Monitoring Service]] | idem |

⚠️ **Tabel di atas dihitung dari `bip-erp/services/*` terhadap `origin/main`, bukan dari ingatan.** Cara mengauditnya ulang: bandingkan daftar folder service dengan daftar berkas `API - *.md` di sini. Cacah tangan sudah terbukti meleset berulang kali di [[API - Marketing Analytics Service]].

## Dokumen Terkait

- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]] · [[DB - Overview and Notes]] · [[HOMEPAGE]]
