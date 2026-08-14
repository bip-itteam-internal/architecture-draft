**Status**: ⚠️ **Implemented (ada catatan)** — pipeline dev jalan lewat GitHub Actions, mobile lewat Codemagic. Catatan besar: **jalur deploy produksi ada di luar repo dan belum terverifikasi mekanismenya**, dan **seluruh workflow `erp-frontend` dimatikan 2026-08-14** sehingga deploy web produksi kini **manual** ([[RUN - Deploy Frontend ERP ke Produksi]]).

## Deskripsi

*Ringkasan pipeline CI/CD ERP Bharata. Backend & web di-deploy otomatis lewat **GitHub Actions** dengan **self-hosted runner** (di VPS Biznet Gio); aplikasi **mobile** di-build & didistribusikan lewat **Codemagic**. Infrastruktur VM-nya tercatat di [[IT - Server, VMs and Databases]].*

## Infrastruktur CI/CD

- **Self-hosted runner**: ⚠️ **lokasinya tidak diketahui.** Beberapa workflow memakai `runs-on: self-hosted` (`deploy.yml` bip-erp, `local-deploy.yml` task-management, `deploy-prod.yml` erp-frontend), tetapi **runner-nya tidak ada di VPS Biznet Gio** `116.206.196.31` — diperiksa menyeluruh 2026-08-14: nol proses `Runner.Listener`, nol unit systemd `actions.runner.*`, nol direktori `actions-runner`, nol container ber-nama runner/delegate. Enumerasi resmi lewat API GitHub **tidak bisa dilakukan** dengan hak yang ada (403 di level org, 404 di level repo), jadi *"tidak ada runner sama sekali"* **belum terbukti** — yang terbukti hanya *"tidak di Biznet"*. VM internal lama `10.10.10.8`/`cicd` sudah **decommissioned**. Gejala bila memang tak ada executor: run **menggantung di antrean** alih-alih gagal (run `deploy-prod.yml` 2026-07-05 mengantre 24 jam sebelum dibatalkan).
- **Deployment VM (dev)**: `10.10.10.121` (user `erp`) — host container/app (dev). ⚠️ Prod LIVE kini di **VPS Biznet `116.206.196.31`** (konfirmasi user 18 Juli 2026; `10.10.10.120` pensiun)
- 🔴 **PENTING — merge ke `main` MENDARAT DI PRODUKSI** (terverifikasi 2026-08-13). `finance-service` yang baru lahir hari itu **sudah menjawab di prod** lewat gateway (`GET /api/finance` → 200) padahal **dev masih 404** berjam-jam sesudahnya. Repo bip-erp hanya punya **dua** workflow — `deploy.yml` (judulnya "Deploy to **Dev**", `VM_IP: 10.10.10.121`) dan `pr-notification.yml`; **tidak ada** `deploy-prod.yml`. Jadi prod menerima deploy dari `main` lewat jalur **di luar GitHub Actions**; kandidat terkuat delegate **Harness** di VPS, tetapi pemicunya **belum terverifikasi** — jangan tulis mekanismenya sebagai fakta sebelum ada yang membuktikannya.
  **Konsekuensi praktis**: gerbang **sebelum** merge adalah satu-satunya gerbang. Perubahan yang bisa mematikan boot (mis. entri baru di `InternalURL` gateway tanpa `*_MODULE_URL` di compose → `ValidateInternalURL` memanik → restart-loop) akan menjatuhkan **seluruh ERP produksi**, bukan dev. Dan "uji di dev dulu" tidak berarti apa-apa bila dev tertinggal; per 2026-08-13 dev menjalankan biner gateway **8 jam lebih tua** dari `main` sampai di-deploy ulang manual.
- 🔴 **TETAPI JANGAN DIBALIK JADI "SEMUA SERVICE OTOMATIS NAIK"** — terbukti **tidak seragam** 2026-08-14. `integration-service` **tidak pernah dibangun ulang** setelah dua PR OPEX merge: image-nya bertanggal `2026-08-13 20:13` sementara PR-nya merge `23:50` dan `06:32` esoknya. Checkout `/home/bharata/apps/bip-erp` **sudah** memuat kedua commit — jadi *repo* di prod ter-update tapi *container*-nya tidak. Fitur tampak "sudah di prod" padahal biner lamanya yang melayani; gejalanya persis kelas "merged, deployed, tetap mustahil dipakai". Dibereskan manual dengan `docker compose up -d --build integration-service --no-deps` (lihat [[RUN - Deploy Microservices bip-erp]] §1).
  **Aturan yang berlaku**: setelah merge, **verifikasi per service** — `docker image inspect <image> --format '{{.Created}}'` harus lebih baru dari waktu merge-nya. `docker ps`, `/health`, dan "checkout-nya sudah benar" **semuanya tidak membuktikan apa pun** tentang biner yang sedang jalan.
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

### erp-frontend (web "hris-dashboard") — ⚠️ MANUAL, tanpa otomasi
- **Semua workflow dimatikan 2026-08-14** (`CI — Verify PR` dan `Deploy PROD ERP Frontend`, keduanya `disabled_manually`). Tak ada trigger otomatis apa pun ke dev maupun prod.
- **Deploy prod = manual lewat SSH**, prosedur + gerbang verifikasinya di [[RUN - Deploy Frontend ERP ke Produksi]].
- **Bukan PM2 lagi**, dan bukan lagi user `erp`: produksi jalan sebagai **container Docker** `frontend-hris-dashboard` (image `erp-frontend-frontend-hris`, port `9696`) di app dir **`/home/bharata/apps/erp-frontend`**. Diverifikasi langsung 2026-08-14 — `pm2 list` di VPS hanya memegang `uptime-kuma`, dan direktori lama `/home/*/apps/frontend-hris-dashboard` sudah tidak ada.
- **`.github/workflows/deploy-prod.yml` masih tersimpan di repo dengan isi yang salah** (`VM_IP` menunjuk `10.10.10.120` yang sudah pensiun, dan `runs-on: self-hosted`). Berkasnya terbaca seolah jalur ini hidup; ia tidak. Lihat [[APP - Web ERP]]

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
