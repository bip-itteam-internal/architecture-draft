## Deskripsi

*Inventaris **environment & endpoint** bip-erp. Nilai di bawah **grounded** dari komentar CORS di `api-gateway/main.go` + [[HOMEPAGE]]/[[README]]. Pemetaan port→service spesifik & detail VM = (TBD) — lengkapi dari `.env` & [[IT - Server, VMs and Databases]]. **Tidak memuat secret** (password/kunci ada di `.env`, lihat [[IT - Security]]).*

- **Status**: ⚠️ Sebagian — host/URL/port teramati; pemetaan port→service TBD

## Environment

| Env | Host (grounded) | Catatan |
|---|---|---|
| **Production** | **VPS Biznet `116.206.196.31`** (sejak ≤18 Juli 2026; `10.10.10.120` pensiun — konfirmasi user) | URL publik: `erp.bharatainternasional.com`, `tamu.bharatainternasional.com`, `tasks.bharatainternasional.com`. ⚠️ Workflow "Deploy to Prod" masih menarget `.120` — belum dipindah ke VPS |
| **Staging** | `erp-dev.bharatainternasional.com` | host internal = TBD |
| **Development** | `10.10.10.121` | port mirror production |
| **Wiki dok** | `architecture.bharatainternasional.com` | export vault (lihat [[README]]) |

## Port backend (internal, di belakang gateway) — grounded dari `.env.example`

| Port | Komponen |
|---|---|
| `6969` | API Gateway |
| `6970` | employee-service |
| `6971` | attendance-service |
| `6972` | notification-service |
| `6973` | file-service |
| `6974` | insentive-service |
| `6839` | integration-service |
| `6975` | tiktok-shop-service |
| `6976` | inventory-service |
| `6977` | task-management-service |
| `6978` | manufacture-service |
| `6979` | recruitment-service |
| `6980` | payroll-service |
| `7000` | HRIS orchestrator |
| `7001` | IT orchestrator |
| `9000` / `9001` | MinIO API / console |

> Tiap service juga punya Mongo container sendiri ([[DB - Overview and Notes]]). DB name: `employee_db`, `attendance_db`, `notification_db`, `insentive_db`, `integration_db`, `tiktok_shop_db`, `inventory_db`, `task_management_db`.

## Port frontend/app — grounded dari CORS origin gateway

| Port | Peran | Status |
|---|---|---|
| `3000` / `3001` | erp-frontend (Next.js) | grounded |
| `9696` | app/web tambahan | TBD peran pasti |
| `4321` | Astro (guestbook) | grounded (default Astro) |
| `2700` | Task Manager FE (`tasks.*`) | grounded |
| `4370` / `4371` | Hardware fingerprint extension (localhost) | grounded |

## Belum Diputuskan / Dilengkapi (TBD)

- Peran pasti port `9696` (frontend/app) + host staging.
- Spesifikasi VM/host (CPU/RAM/disk) → [[IT - Server, VMs and Databases]].
- Daftar domain + sertifikat + siapa pengelola DNS.

## Dokumen Terkait

- [[IT - Server, VMs and Databases]] · [[IT - Network Management]] · [[IT - Security]] · [[CORE - API Master Gateway]]
- [[IT - Runbooks]] · [[DB - Overview and Notes]] · [[README]]
