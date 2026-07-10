## Deskripsi

*Pengelolaan jaringan kantor & perangkat terhubung — LAN lokal, WiFi, perangkat on-network, dan jaringan multi-lokasi. Saat ini sebagian sudah terkelola (allowlist WiFi + inventaris VM); topologi/dokumentasi formal masih TBD.*

- **Status**: ⚠️ Sebagian terdokumentasi (allowlist WiFi & inventaris VM ada; topologi formal belum)

## Jaringan Lokal (LAN)

- Subnet lokal **`10.10.10.0/24`** — server, VM, dan perangkat kantor (detail di [[IT - Server, VMs and Databases]])
- Perangkat on-network: server & VM (ERP dev/prod/testing, DevOps, CI/CD runner, dll), **mesin fingerprint** (X105 `:4370`, X609 `:4371` — lihat [[APP (Extension) - Fingerprint Listener (Complete)]])

## WiFi Kantor

- Sekitar **±50 access point** kantor; **MAC di-allowlist** (collection `company_wifi`) dan dipakai sebagai **validasi geofencing** untuk clock-in via [[APP - MyBharata]]
- **Pengelolaan allowlist oleh IT** (tambah/hapus AP) lewat endpoint network attendance — lihat [[IT - Employee System]] & [[Microservices - Attendance Service]]

## Monitoring Jaringan

- **VM Network Monitor** (`10.10.10.3`) untuk pemantauan jaringan — lihat [[IT - Monitoring System]]

## Jaringan Multi-Lokasi

- **Kantor utama** + **warehouse Cipari** (rencana extend LAN/WiFi ke gedung warehouse) — lihat [[WH - Infra Warehouse Cipari]]

## Ingress & Firewall VPS Biznet (migrasi cloud, ⚠️)

Migrasi ERP dari server LAN lama (`10.10.10.120`) ke **VPS Biznet Gio** (`116.206.196.31`) — lihat [[IT - Server, VMs and Databases]] & [[IT - CI-CD]].

- **Reverse proxy**: `nginx-proxy-manager` (container `npm-npm-1`) di VPS = ingress ke stack ERP (port 80/443). npm HARUS ikut Docker network `BIP-ERP-Bridge` agar bisa forward ke `API-Gateway:6969` — kalau beda network → **502 Bad Gateway** saat login. Config di-version-control di `bip-erp/infra/npm/`.
- **Cloud firewall Biznet** (panel Inbound Rules, bukan ufw OS — ufw inactive): port aplikasi publik dibatasi per-rule. Port **MongoDB (32740, 32783–32792)** hanya di-allow dari **IP kantor statik** (`121.101.132.82`, `103.247.15.156` — Terabit) via Source `/32`; sisanya di-drop. Mongo listen `0.0.0.0` sehingga cloud firewall = satu-satunya pembatas eksternal — akses dev pakai Compass/mongosh dari IP kantor (user `erp-mongo`, authSource=admin).
- **Migrasi domain**: `api.bharatainternasional.com` DNS sudah dialihkan ke VPS Biznet (`116.206.196.31`, cert wildcard Sectigo valid, TLS 1.3). Server lama (`103.247.15.156`, ISP Terabit) masih melayani selama TTL cache (3600s) belum habis — belum dimatikan.

## Belum Diputuskan (TBD)

- Topologi/diagram jaringan formal, segmentasi **VLAN**
- Kebijakan firewall LAN internal (cloud firewall Biznet sudah ada untuk VPS)
- Redundansi internet / failover
- Standarisasi penamaan & dokumentasi perangkat jaringan (switch/router/AP)
- Hardening: Mongo bind `0.0.0.0` → idealnya `127.0.0.1`/internal-only (defense-in-depth, tak hanya andalkan cloud firewall)

## Dokumen Terkait

- [[IT - Big Pictures]]
- [[IT - Server, VMs and Databases]] · [[IT - Employee System]] · [[IT - Monitoring System]]
- [[Microservices - Attendance Service]] (WiFi geofencing) · [[WH - Infra Warehouse Cipari]]
