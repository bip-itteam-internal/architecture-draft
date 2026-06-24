## Deskripsi

*Inventaris **environment & endpoint** bip-erp. Nilai di bawah **grounded** dari komentar CORS di `api-gateway/main.go` + [[HOMEPAGE]]/[[README]]. Pemetaan port→service spesifik & detail VM = (TBD) — lengkapi dari `.env` & [[IT - Server, VMs and Databases]]. **Tidak memuat secret** (password/kunci ada di `.env`, lihat [[IT - Security]]).*

- **Status**: ⚠️ Sebagian — host/URL/port teramati; pemetaan port→service TBD

## Environment

| Env | Host (grounded) | Catatan |
|---|---|---|
| **Production** | `10.10.10.120` | URL publik: `erp.bharatainternasional.com`, `tamu.bharatainternasional.com`, `tasks.bharatainternasional.com` |
| **Staging** | `erp-dev.bharatainternasional.com` | host internal = TBD |
| **Development** | `10.10.10.121` | port mirror production |
| **Wiki dok** | `architecture.bharatainternasional.com` | export vault (lihat [[README]]) |

## Port teramati (dari CORS gateway)

| Port | Dugaan peran | Status |
|---|---|---|
| `6969` | API Gateway / web utama | TBD konfirmasi |
| `3000` / `3001` | Frontend (Next.js) | TBD |
| `9696` | (service/app) | TBD |
| `4321` | Astro (guestbook?) | TBD |
| `2700` | Task Manager FE (`tasks.*`) | TBD |
| `6977` | task-management-service (dari `docker-compose.yml`) | grounded |
| `4370` / `4371` | Hardware fingerprint extension (localhost) | grounded |

> Port→service final ditetapkan dari `.env` (`*_SERVICE_PORT`). Tiap service juga punya Mongo container sendiri ([[DB - Overview and Notes]]).

## Belum Diputuskan / Dilengkapi (TBD)

- Pemetaan pasti tiap port ke service/app.
- Spesifikasi VM/host (CPU/RAM/disk) → [[IT - Server, VMs and Databases]].
- Daftar domain + sertifikat + siapa pengelola DNS.

## Dokumen Terkait

- [[IT - Server, VMs and Databases]] · [[IT - Network Management]] · [[IT - Security]] · [[CORE - API Master Gateway]]
- [[IT - Runbooks]] · [[DB - Overview and Notes]] · [[README]]
