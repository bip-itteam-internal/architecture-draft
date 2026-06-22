## Deskripsi

*Pengelolaan jaringan kantor & perangkat terhubung — LAN lokal, WiFi, perangkat on-network, dan jaringan multi-lokasi. Saat ini sebagian sudah terkelola (allowlist WiFi + inventaris VM); topologi/dokumentasi formal masih TBD.*

- **Status**: ⚠️ Sebagian terdokumentasi (allowlist WiFi & inventaris VM ada; topologi formal belum)

## Jaringan Lokal (LAN)

- Subnet lokal **`10.10.10.0/24`** — server, VM, dan perangkat kantor (detail di [[IT - Server, VMs and Databases]])
- Perangkat on-network: server & VM (ERP dev/prod/testing, DevOps, CI/CD runner, dll), **mesin fingerprint** (X105 `:4370`, X609 `:4371` — lihat [[APP (Extension) - Fingerprint Listener (Complete)]])

## WiFi Kantor

- Sekitar **±50 access point** kantor; **MAC di-allowlist** (collection `company_wifi`) dan dipakai sebagai **validasi geofencing** untuk clock-in via [[APP - Mobile Application]]
- **Pengelolaan allowlist oleh IT** (tambah/hapus AP) lewat endpoint network attendance — lihat [[IT - Employee System]] & [[Microservices - Attendance Service]]

## Monitoring Jaringan

- **VM Network Monitor** (`10.10.10.3`) untuk pemantauan jaringan — lihat [[IT - Monitoring System]]

## Jaringan Multi-Lokasi

- **Kantor utama** + **warehouse Cipari** (rencana extend LAN/WiFi ke gedung warehouse) — lihat [[WH - Infra Warehouse Cipari]]

## Belum Diputuskan (TBD)

- Topologi/diagram jaringan formal, segmentasi **VLAN**
- **Firewall** & kebijakan akses jaringan
- Redundansi internet / failover
- Standarisasi penamaan & dokumentasi perangkat jaringan (switch/router/AP)

## Dokumen Terkait

- [[IT - Big Pictures]]
- [[IT - Server, VMs and Databases]] · [[IT - Employee System]] · [[IT - Monitoring System]]
- [[Microservices - Attendance Service]] (WiFi geofencing) · [[WH - Infra Warehouse Cipari]]
