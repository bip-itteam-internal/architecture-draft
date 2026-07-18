## Deskripsi

*Ringkasan pipeline CI/CD ERP Bharata. Backend & web di-deploy otomatis lewat **GitHub Actions** dengan **self-hosted runner** (di VPS Biznet Gio); aplikasi **mobile** di-build & didistribusikan lewat **Codemagic**. Infrastruktur VM-nya tercatat di [[IT - Server, VMs and Databases]].*

## Infrastruktur CI/CD

- **Self-hosted runner**: kini di **VPS Biznet Gio** `116.206.196.31` (VM internal lama `10.10.10.8`/`cicd` sudah **decommissioned**) — menjalankan workflow GitHub Actions (`runs-on: self-hosted` di `deploy.yml`), lalu SSH ke VM target
- **Deployment VM (dev)**: `10.10.10.121` (user `erp`) — host container/app (dev). ⚠️ Prod LIVE kini di **VPS Biznet `116.206.196.31`** (konfirmasi user 18 Juli 2026; `10.10.10.120` pensiun) — workflow deploy-prod masih menarget `.120` dan perlu dipindah
- Auth deploy: **SSH password** via GitHub Secret `VM_PASSWORD` (`sshpass`); StrictHostKeyChecking dimatikan untuk automation
- **VPS Biznet Gio (migrasi, ⚠️)**: `116.206.196.31` (user `bharata`, Ubuntu 22.04) — target migrasi prod baru. CI via **Harness** (`bip-erp-vm-delegate` container jalan di VPS; build di VM). Per 2026-07-09 masih **dobel deployment** dengan `.120` (integration-service + worker jalan di dua tempat, belum cutover). Storage: additional disk 100G di-mount `/backup`.
- Detail VM & kredensial: [[IT - Server, VMs and Databases]]

## Pipeline per Aplikasi

### bip-erp (backend microservices) — GitHub Actions
- **Trigger**: push ke `main` + `workflow_dispatch` (rollback / force_deploy)
- **Alur**: `detect` (git pull di VM + deteksi service berubah) → `notify-start` → `deploy-*` (build → down → up per service, **paralel**) → `deployment-summary` (cleanup image, simpan 10 terakhir)
- **Selective deploy**: hanya service yang berubah; jika file **shared** berubah (`shared-library/`, `.env*`, `docker-compose.yml`) → **semua 11 service** di-deploy
- **Rollback**: `emergency-rollback` (manual) → `git reset --hard HEAD~1` + rebuild semua
- App dir: `/home/erp/apps/bip-erp`. Detail: `CICD_WORKFLOW_DOCUMENTATION.md` di repo. Lihat [[CORE - API Master Gateway]]

### erp-frontend (web "hris-dashboard") — GitHub Actions + PM2
- **Trigger**: push ke `main` + `workflow_dispatch` (rollback)
- **Alur**: SSH ke VM → `git reset --hard origin/main` → **PM2** jalankan `ecosystem.config.cjs` (app `web-erp`, otomatis `pnpm install && build && prod`) → verify `pm2 info`
- App dir: `/home/erp/apps/frontend-hris-dashboard`. Lihat [[APP - Web ERP]]

### mybharata-app (mobile Flutter) — Codemagic
- **Trigger branch**: `development` → build staging (APK/IPA) → **Firebase App Distribution**; `release/*` atau `main` → build prod (AAB/IPA) → **Google Play Store & App Store Connect**
- Tahap: unit test → `build_runner` → build per flavor (`dev`/`prod`)
- **Secrets** disimpan sebagai Base64 di Codemagic env (FCM `google-services.json`, `GoogleService-Info.plist`, keystore `.jks`), direkonstruksi via pre-build script
- **Notifikasi**: Slack `#hris-mobile-alerts`. Lihat [[APP - MyBharata]]

### Lainnya
- **task-management** FE & BE — GitHub Actions `local-deploy.yml` (deploy via self-hosted runner). Lihat [[APP - Dynamic Task Tracker]]
- **scraping** (TikTok Sentiment) — GitHub Actions `auto-deploy.yml` + Docker (`Dockerfile.backend`, `docker-compose.yml`, `deploy.sh`); standalone lokal. Lihat [[Sales - TikTok Sentiment Pipeline]]
- **ideamiils** (Veo) — `docker-compose.yml` + `deploy.sh` (deploy manual/Docker). Lihat [[Sales - Veo (Gemini) Implementation]]

## Notifikasi
- **bip-erp & erp-frontend**: WhatsApp grup **"BIP Notification Center"** via Bharata API (`scripts/notify.sh`) — start / success / completed-with-errors / rollback
- **mybharata-app**: Slack `#hris-mobile-alerts` (Codemagic)

## Keamanan
- SSH deploy pakai password dari GitHub Secret (`VM_PASSWORD`), tidak disimpan di runner; tanpa akses root langsung (user runner terbatas di VPS, `erp` di VM target)
- Git di VM pakai SSH deploy key tanpa passphrase (read-only)
- Secret mobile (Firebase/keystore) tidak masuk repo — Base64 di Codemagic env

## Build & Runtime (Docker)
- **Multi-stage production build** (bip-erp, 2026-07): 15 service Go pindah dari dev/`air` hot-reload (image ~1GB, source ter-mount) ke multi-stage binary static (`CGO_ENABLED=0`, `alpine` runtime, image ~30-65MB). Hemat disk rootfs ~14G di VPS Biznet. Volume mount source dev dibuang (binary tak butuh source live). PR #299/#300.
- **Frontend** (erp-frontend, Next.js): sudah production-grade — multi-stage `node:22-alpine`, Next standalone output, non-root user.
- **mongod logging**: log ke `json-file` driver (max-size 50m × max-file 3), bukan `--logpath` ke volume data (dulu numpuk 67G). PR #285.
- **Auto-recovery**: `autoheal` container (`willfarrell/autoheal`, `LABEL=all`) monitor semua container ber-healthcheck via `docker.sock`, auto-restart yang `unhealthy` (hang). Melengkapi `restart: unless-stopped` (yang hanya tangani crash). PR #300.
- **Healthcheck coverage**: 15 service Go + Mongo punya healthcheck (`wget /health` / `mongosh ping`). PR #307.

## Catatan / Roadmap
- ✅ **Health-check per service sudah ada** (autoheal + healthcheck 15 service) — sebelumnya roadmap
- Automated test **sebelum** deploy, deploy-approval workflow & registry image (GHCR) masih ide. Build cache di VM dibersihkan via cron `docker-prune.sh` (build cache >48h + dangling).

## Dokumen Terkait

- [[IT - Server, VMs and Databases]]
- [[IT - Big Pictures]]
- [[IT - Monitoring System]]
- [[CORE - API Master Gateway]]
