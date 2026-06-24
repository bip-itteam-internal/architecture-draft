## Deskripsi

*Kumpulan **runbook** operasional bip-erp — langkah konkret untuk tugas berulang. Grounded dari [[HOMEPAGE]], [[IT - CI-CD]], [[IT - Backup & DR]] + pola kode. Langkah yang belum terdokumentasi penuh ditandai (TBD).*

- **Status**: ⚠️ Deploy & backup grounded; restore/DR & rotasi secret = sebagian TBD

## Runbook 1 — Tambah microservice baru

Pola dari [[HOMEPAGE]] + [[ADR - 0002 Database-per-Service]]:
1. `bip-erp/services/<svc>/` → `go mod init '<svc>'`.
2. Link shared-library: `go mod edit -replace github.com/bharata/shared-library=../../shared-library` → `go get github.com/bharata/shared-library@v0.0.0`.
3. Salin `services/.template` (atau service mirip) → `main.go` + `Dockerfile`; daftarkan rute via `RegisterRoutes(app)`; akses Mongo via `mongodb.GetCollection(...)`.
4. Tambah service + Mongo container + volume di `docker-compose.yml`.
5. Tambah `<SVC>_MODULE_URL` ke `api-gateway/main.go` hashmap `InternalURL` + env gateway di compose.
6. Tambah variabel ke `.env` / `.env.example` (`<SVC>_SERVICE_PORT`, `MONGO_<SVC>_DB`) — lihat alokasi port di [[IT - Environment Inventory]].
7. Identitas user dari header `BIP-*` di belakang [[CORE - API Master Gateway]]; RBAC via `system_roles`.

> Contoh penerapan lengkap (path eksak): [[ERPGo - Form Builder]] §Rencana Implementasi.

## Runbook 2 — Deploy / rilis (grounded dari [[IT - CI-CD]])

**Infra**: self-hosted runner VM `10.10.10.8` (user `cicd`) menjalankan GitHub Actions → SSH ke VM target (**dev `10.10.10.121`**, **prod `10.10.10.120`**, user `erp`). Auth SSH password via GitHub Secret `VM_PASSWORD` (`sshpass`).

- **bip-erp (backend)** — trigger **push ke `main`** (+ `workflow_dispatch`). Alur: `detect` (git pull + deteksi service berubah) → `notify-start` → `deploy-*` (build → down → up per service, **paralel**) → `deployment-summary` (cleanup image, simpan 10 terakhir). **Selective**: hanya service berubah; bila file **shared** berubah (`shared-library/`, `.env*`, `docker-compose.yml`) → **semua 11 service** redeploy. App dir VM: `/home/erp/apps/bip-erp`.
- **erp-frontend (web)** — push `main` → SSH → `git reset --hard origin/main` → **PM2** `ecosystem.config.cjs` (app `web-erp`: `pnpm install && build && prod`) → verify `pm2 info`. App dir: `/home/erp/apps/frontend-hris-dashboard`. Lihat [[APP - Web ERP]].
- **mybharata-app (mobile)** — **Codemagic**: branch `development` → APK/IPA → Firebase App Distribution; `release/*`/`main` → AAB/IPA → Play Store/App Store. Lihat [[APP - MyBharata]].
- **Notifikasi**: WhatsApp grup "BIP Notification Center" (`scripts/notify.sh`) untuk backend/web; Slack `#hris-mobile-alerts` untuk mobile.

## Runbook 2b — Rollback

- **bip-erp**: `workflow_dispatch` → job `emergency-rollback` = `git reset --hard HEAD~1` + rebuild semua service.
- **erp-frontend**: `workflow_dispatch` (rollback) via GitHub Actions.
- (Catatan: belum ada health-check/automated test **sebelum** deploy — lihat roadmap di [[IT - CI-CD]].)

## Runbook 3 — Backup & restore (grounded dari [[IT - Backup & DR]])

- **Backup MongoDB**: `scripts/mongo-backup.sh` (`make mongo-backup`); folder `mongo-backup` di-mount ke container Mongo. **Cron mingguan: Minggu 04:15** (dijadwalkan di cron [[Microservices - Attendance Service]]).
- **Backup MinIO**: `scripts/minio-backup.sh` — mirror `app-bucket` → zip ke `.minio-backup`.
- **Restore** (mongorestore + restore MinIO): **TBD** — prosedur DR formal belum ada (lihat [[IT - Backup & DR]] §DR).
- **Belum ada**: retensi/offsite, RPO/RTO, uji restore berkala, enkripsi backup, alert kegagalan backup (semua TBD).

## Runbook 4 — Rotasi secret / incident response (TBD)

- Secret di `.env`: `INTERNAL_GATEWAY_KEY`, `JWT_SECRET`, kredensial Mongo/MinIO, token marketplace. Deploy SSH pakai `VM_PASSWORD` (GitHub Secret). Prosedur rotasi step-by-step = **TBD** — koordinasi [[IT - Security]].
- Incident response + jalur eskalasi = **TBD** → [[IT - Monitoring System]], [[REF - Ownership & RACI]].

## Dokumen Terkait

- [[HOMEPAGE]] · [[IT - CI-CD]] · [[IT - Backup & DR]] · [[IT - Server, VMs and Databases]] · [[IT - Security]] · [[IT - Monitoring System]]
- [[ADR - 0002 Database-per-Service]] · [[CORE - API Master Gateway]] · [[IT - Environment Inventory]] · [[APP - Web ERP]] · [[APP - MyBharata]] · [[Microservices - Attendance Service]]
