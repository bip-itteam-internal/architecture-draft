
## Deskripsi

*Akses ke server on-site dan VM tercantum di bawah ini, semua password root sama dengan user, namun harap JANGAN menggunakan root sebagai default*

- **Status**: ✅ Aktif — inventaris server/VM/DB yang berjalan (referensi akses IT).

## Server

**Server - Windows Server (RAID5/HyperV)**
- Local IP: 10.10.10.15
- Username: administrator, devops
- Password: Hijau+99!

## VM (Virtual Machine dan VPS)

**VM - DevOps Ubuntu**
- Local IP: 10.10.10.37
- Username: devops_ubuntu
- Password: Hijau+99

**VM - ERP Development**
- Local IP: 10.10.10.121
- Username: erp
- Password: Hijau+99

**VM - ERP Production**
- Local IP: 10.10.10.120
- Username: erp
- Password: Hijau+99
- ⛔ **Masih menyala tetapi TIDAK DIPAKAI** (dikonfirmasi pemilik 2026-09-22). Produksi kini berjalan di **VPS Biznet** di bawah. Port Mongo-nya masih menerima koneksi, jadi mudah tersangka sebagai sumber yang sah — **jangan** dijadikan sumber pengukuran maupun pembanding.

**VPS - ERP Cloud (Biznet Gio, ⚠️ migrasi)**
- Public IP: 116.206.196.31 (Ubuntu 22.04)
- Username: bharata (SSH key `~/.ssh/biznet-key`, alias `ssh bip-vps`)
- Additional disk 100G → mount `/backup` (backup DB harian). App dir: `/home/bharata/apps/bip-erp`.
- ✅ **INI SERVER PRODUKSI yang berjalan** (dikonfirmasi pemilik 2026-09-22; `10.10.10.120` menyala tapi tidak dipakai). ⚠️ Catatan lama *"target migrasi prod, per 2026-07-10 masih dobel deployment (belum cutover)"* **sudah basi** — sempat membuat hasil pengukuran prod diragukan keabsahannya. Dibuktikan dengan mencocokkan ke angka yang tim sendiri catat: potongan ongkir Shopee Agustus terukur **Rp231.316.465** (dok Integration Service menulis "±Rp231 jt") dan proteksi kirim Agustus meleset **tepat 18 × Rp350** dari angka 2026-09-08 — selisih yang justru membuktikan data yang sama, dua minggu lebih matang. Pengukuran read-only dijalankan lewat `docker exec <container> mongosh` di server ini, kredensial dibaca dari `.env` setempat. CI via Harness (delegate di VPS) + host **self-hosted GitHub Actions runner** (pindahan dari VM `10.10.10.8` yang sudah decommissioned). Ingress: nginx-proxy-manager (`~/npm`, network `BIP-ERP-Bridge`). Detail: [[IT - CI-CD]] · [[IT - Network Management]].
- **Akses MongoDB** (label "(dev)" dicabut 2026-09-22 — ini Mongo produksi) — ⚠️ **berubah 2026-08-09**: port Mongo kini diikat **`127.0.0.1`**, tidak lagi `0.0.0.0`, jadi koneksi langsung dari IP kantor **tidak lagi bisa**. Pakai **SSH tunnel** lebih dulu (mis. `ssh -L 32789:127.0.0.1:32789 bip-vps`), lalu Compass/mongosh ke `mongodb://erp-mongo:<pwd>@127.0.0.1:<port>/?authSource=admin` — port per service tetap sama (Integration 32789, Employee-Primary 32783, dst). **Alasan**: 16 port Mongo sebelumnya mendengarkan di seluruh antarmuka termasuk IP publik; UFW `inactive` dan rantai `DOCKER-USER` kosong, sehingga satu-satunya yang menutupnya adalah cloud firewall Biznet — perlindungan **di luar kendali repo**, yang hilang begitu IP berubah atau provider berganti. Diverifikasi aman sebelum diubah: nol koneksi established dari alamat non-Docker, dan seluruh trafik 24 jam berasal dari `172.22` (jaringan Docker) + `127.0` (sesi lokal). Komunikasi antar-container tak lewat port publikasi (pakai nama service), jadi tak terpengaruh. Grounded: `bip-erp/docker-compose.yml`, PR [#1104](https://github.com/bip-itteam-internal/bip-erp/pull/1104).

**VM - ERP Testing
- Local IP: 10.10.10.122
- Username: erp
- Password: Hijau+99

**VM - Finance Production**
- Local IP: 10.10.10.38
- Username: financeprodapi
- Password: Hijau+99

**VM - Network Monitor**
- Local IP: 10.10.10.3
- Username: netmon
- Password: Hijau@99!

## Isi tiap mesin (diukur 2026-10-16)

> ⚠️ **Potret bertanggal, bukan fakta tetap.** Container naik-turun tiap deploy; ukur ulang sebelum dipakai untuk keputusan (`docker ps`, `docker compose ls`, `ss -tln`). Diukur read-only dari jaringan kantor `10.10.21.x` (SSH `plink`/`ssh`, tanpa mengubah apa pun).

| Mesin | Terjangkau? | OS · RAM · disk `/` | Isinya |
|---|---|---|---|
| `10.10.10.3` Network Monitor | ✅ SSH | Ubuntu 22.04 · 11 Gi · 145G (51%) | lihat rincian di bawah: **9router** (`code.bharatainternasional.com`), n8n, uptime-kuma, beszel server, Zabbix server, GLPI, Ideamills, TikTok Insight Analyzer, Frappe, 8 container `hermes-coding` |
| `10.10.10.15` | ⚠️ hanya port 80 | — | Port 80 membalas halaman login **`doc/page/login.asp`**, pola web Hikvision (CCTV/NVR), **bukan** Windows Server seperti blok di atas. RDP 3389 dan SSH tertutup. Pemetaan IP-nya belum dikonfirmasi pemilik (TBD) |
| `10.10.10.37` DevOps Ubuntu | ❌ ping & port 22/80/443 diam | — | tak terukur; kemungkinan mati |
| `10.10.10.38` Finance Production | ❌ ping & port diam | — | tak terukur; kemungkinan mati |
| `10.10.10.120` ERP Production (lama) | ✅ SSH (sering putus `connection abort`) | Arch Linux · 7,7 Gi · 189G (65%) | compose `bip-erp` 30 container (service ERP + MongoDB, termasuk `Employee-MongoDB-Secondary`), `beszel-agent`. Masih menyala walau tak dipakai |
| `10.10.10.121` ERP Development | ✅ SSH | Arch Linux · 11 Gi · 139G (**86%**) | compose `bip-erp` 50 container (seluruh service + MongoDB per service, Redis, MinIO, Autoheal, Harness delegate `bip-erp-delegate`, `hoppscotch`), `frontend-hris-dashboard`, `beszel-agent`. Saat diukur `Vault-MCP` **restart berulang** |
| `10.10.10.122` ERP Testing | ❌ ping & port diam | — | tak terukur; kemungkinan mati |
| VPS Biznet `116.206.196.31` (prod) | ✅ SSH kunci | Ubuntu 22.04 · 15 Gi · 88G (81%) | lihat rincian di bawah |

**VM `10.10.10.3` (netmon)**, rincian:
- **9router** (`9router.service`, `node /usr/bin/9router`, port **20128**): relay AI OpenAI-compatible yang dikenal sebagai `https://code.bharatainternasional.com/v1` (lihat [[ADR - 0082 Integrasi AI lewat Klien Tipis di Shared-Library]]). DB-nya `/home/netmon/.9router/db/data.sqlite`.
	- ⚠️ **TLS untuk domain itu TIDAK diterminasi di VM ini.** nginx `.3` tak punya vhost `code.bharatainternasional.com`, dan port 443 tidak listen. DNS-nya mengarah ke IP kantor `103.247.15.156` (Terabit), jadi ada reverse proxy ber-TLS di mesin/router lain yang meneruskan ke `.3:20128`. **Mesin proxy itu belum diketahui (TBD)**, cek tabel port forward router kantor.
	- 2026-10-16: 9router sendiri hidup (`127.0.0.1:20128/v1/models` membalas 200), tetapi dari luar TCP 443 tersambung lalu TLS handshake gagal (`ERR_CONNECTION_ABORTED`), dan tak ada koneksi masuk ke 20128. Jadi yang rusak ada di proxy depannya, bukan di 9router. Dugaan `10.10.10.37` sebagai proxy itu (karena VM tersebut mati) **belum diverifikasi**. **Pulih sendiri di hari yang sama** (sekitar 12.17 WIB): dari luar membalas 401 (normal tanpa kunci), dan `.3` tidak di-reboot (uptime berlanjut). Jadi gangguannya sementara dan ada di jalur depan; penyebabnya tidak tercatat.
- Docker compose: `n8n` (5678), `uptime-kuma` (3001), `beszel-server` + `beszel-agent` (8090), `ideamiils` (5 container: app, ws-server, worker, scraper, mongo), `tiktok-insight-analyzer` (frontend, backend, mongo; nginx vhost `glowgap.bharatainternasional.com` → `127.0.0.1:3000` dan `:8000/api/`), `frappe_docker` (MariaDB).
- Container lepas: 8× `hermes-coding:latest` (Hermes Agent, lihat [[IT - Monitoring System]]).
- systemd: `nginx`, `apache2`, `mysql`, `postgresql@14-main`, `zabbix-server` + `zabbix-agent` (10050/10051), `pm2-netmon`, `tailscaled` (`100.68.91.104`). Folder `glpi-11.0.5` di home.

**VPS Biznet (prod)**, compose project per `docker compose ls`:
- `bip-erp` (50): seluruh service ERP + MongoDB per service, Redis, MinIO, Autoheal, Vault-MCP · `erp-frontend` (`frontend-hris-dashboard`)
- `bip-distribusi` (14): Sistem Distribusi Offline (`distribusi-*`: frontend, api-gateway, warehouse, canvas, master, selling, finance, report, redis + mongo canvas/finance/warehouse/selling/master)
- `audit-bharata` (`Audit-App`) · `career-bharata` · `form-survey` (app, server, PostGIS) · `log-direktur` (app + mongo)
- `npm` (nginx-proxy-manager, ingress 80/81/443) · `beszel` + `beszel-agent` · `hoppscotch` (+ postgres)

## MongoDB ERP Production

- **Employee (Primary Replication):** 
	- mongodb://erp-mongo:{password}@10.10.10.120:32783/employee_db?authSource=admin&directConnection=true

- **Attendance:** 
	- mongodb://erp-mongo:{password}@10.10.10.120:32785/attendance_db?authSource=admin

- **Notification:** 
	- mongodb://erp-mongo:{password}@10.10.10.120:32786/notification_db?authSource=admin

- **Insentive:** 
	- mongodb://erp-mongo:{password}@10.10.10.120:32787/insentive_db?authSource=admin

- **Integration:** 
	- mongodb://erp-mongo:{password}@10.10.10.120:32789/integration_db?authSource=admin

## Dokumen Terkait

- [[IT - Big Pictures]] — peta domain IT
- [[IT - Network Management]] (subnet & perangkat) · [[IT - CI-CD]] (runner & deploy) · [[IT - Monitoring System]] (VM netmon) · [[IT - Backup & DR]]
- [[DB - Overview and Notes]] — database per service