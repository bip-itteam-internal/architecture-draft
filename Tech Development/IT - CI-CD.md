## Deskripsi

*Ringkasan pipeline CI/CD ERP Bharata. Backend & web di-deploy otomatis lewat **GitHub Actions** dengan **self-hosted runner** ke VM internal; aplikasi **mobile** di-build & didistribusikan lewat **Codemagic**. Infrastruktur VM-nya tercatat di [[IT - Server, VMs and Databases]].*

## Infrastruktur CI/CD

- **Self-hosted runner**: VM `10.10.10.8` (user `cicd`) — menjalankan workflow GitHub Actions, lalu SSH ke VM target
- **Deployment VM (dev)**: `10.10.10.121` (user `erp`) — host container/app (dev). Prod di `10.10.10.120`
- Auth deploy: **SSH password** via GitHub Secret `VM_PASSWORD` (`sshpass`); StrictHostKeyChecking dimatikan untuk automation
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
- SSH deploy pakai password dari GitHub Secret (`VM_PASSWORD`), tidak disimpan di runner; tanpa akses root langsung (`cicd` di runner, `erp` di VM target)
- Git di VM pakai SSH deploy key tanpa passphrase (read-only)
- Secret mobile (Firebase/keystore) tidak masuk repo — Base64 di Codemagic env

## Catatan / Roadmap
- Belum ada health-check & automated test **sebelum** deploy (rencana di dok bip-erp); deploy-approval workflow & registry image (GHCR) masih ide

## Dokumen Terkait

- [[IT - Server, VMs and Databases]]
- [[IT - Big Pictures]]
- [[IT - Monitoring System]]
- [[CORE - API Master Gateway]]
