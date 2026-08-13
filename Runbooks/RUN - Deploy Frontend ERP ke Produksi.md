> **Status**: ✅ Implemented — prosedur manual, terverifikasi langsung 2026-08-13 (deploy PR #1030 ke produksi).

## Deskripsi

*Cara men-deploy `erp-frontend` ke produksi. **Manual sepenuhnya** — kedua workflow GitHub
Actions repo itu dimatikan 2026-08-14, dan tak ada jalur otomatis yang menggantikannya.*

- **Host**: VPS Biznet Gio `116.206.196.31` (Ubuntu 22.04)
- **URL publik**: `erp.bharatainternasional.com`
- **Dokumen terkait**: [[RUN - Deploy Microservices bip-erp]] (backend, prosedurnya
  berbeda) · [[APP - Web ERP]]

---

## Prosedur

```bash
ssh -i ~/.ssh/irfan-biznet bharata@116.206.196.31
cd ~/apps/erp-frontend
git fetch origin main && git reset --hard origin/main
docker compose build --no-cache && docker compose up -d
```

| | |
|---|---|
| App dir | `/home/bharata/apps/erp-frontend` |
| Container | `frontend-hris-dashboard` |
| Image | `erp-frontend-frontend-hris` |
| Port | `9696` |

**User SSH `bharata`, BUKAN `erp`.** `erp@` ditolak `Permission denied (publickey)`.

**Sepuluh aplikasi lain hidup di `~/apps/` pada host yang sama** (bip-erp, career-bharata,
guestbook-system, dan seterusnya), jadi jangan menjalankan perintah `docker compose` tanpa
`cd` ke direktori aplikasinya lebih dulu.

---

## Gerbang verifikasi

`docker ps` sehat **bukan bukti**. Yang membuktikan, berurutan:

**1. Biner memuat kode baru.** Cari string unik dari perubahanmu di dalam bundle yang
sedang jalan, dan sertakan **kontrol negatif** — string LAMA yang seharusnya sudah hilang:

```bash
docker exec frontend-hris-dashboard grep -rl "<string baru>" /app/.next | wc -l   # > 0
docker exec frontend-hris-dashboard grep -rl "<string lama>" /app/.next | wc -l   # harus 0
```

Kontrol negatifnya yang paling menentukan. Tanpa itu, container yang masih memegang image
lama tetap lolos: string barunya kebetulan juga ada di build sebelumnya, atau grep-nya
salah sasaran.

**2. Aplikasi merespons**, dari dalam maupun dari luar:

```bash
curl -sS -o /dev/null -D - http://localhost:9696/       # 307 -> /login
curl -sS -o /dev/null -w "%{http_code}\n" http://localhost:9696/login   # 200
curl -sS -o /dev/null -w "%{http_code}\n" -L https://erp.bharatainternasional.com/login
```

**3. Buka layarnya dan login.** Untuk perubahan yang menyentuh menu atau navigasi, ini
satu-satunya yang membuktikan fiturnya bisa dipakai — dan mode gagalnya senyap: orang
kehilangan menu tanpa satu pun galat.

---

## Rollback

```bash
cd ~/apps/erp-frontend
git reset --hard <commit-sebelumnya>
docker compose build --no-cache && docker compose up -d
```

Catat commit sebelumnya **sebelum** deploy (`git log --oneline -1`); mencarinya sesudah
sesuatu rusak selalu lebih lambat.

---

## Jebakan yang sudah terbukti

- **`.github/workflows/deploy-prod.yml` menarget `10.10.10.120`**, VM yang sudah pensiun
  sebagai produksi sejak ≤18 Juli 2026. Workflow-nya kini **dimatikan**, tetapi berkasnya
  masih ada di repo dengan nilai yang salah. Jangan menghidupkannya kembali tanpa
  membetulkan targetnya lebih dulu.
- **`runs-on: self-hosted`, dan tak ada runner-nya.** Diperiksa langsung di Biznet
  2026-08-14: nol proses `Runner.Listener`, nol direktori `actions-runner`, nol service.
  Karena itu memicunya tidak menghasilkan galat melainkan run yang **menggantung di
  antrean** — run 2026-07-05 mengantre 24 jam sebelum dibatalkan. Gejala itu mudah
  disangka "sedang berjalan".
- **Merged bukan berarti ter-deploy.** Produksi tidak pernah ikut otomatis; selalu jalankan
  prosedur di atas.
