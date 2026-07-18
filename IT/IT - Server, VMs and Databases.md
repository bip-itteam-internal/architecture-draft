
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

**VPS - ERP Cloud (Biznet Gio, ⚠️ migrasi)**
- Public IP: 116.206.196.31 (Ubuntu 22.04)
- Username: bharata (SSH key `~/.ssh/biznet-key`, alias `ssh bip-vps`)
- Additional disk 100G → mount `/backup` (backup DB harian). App dir: `/home/bharata/apps/bip-erp`.
- Target migrasi prod dari `10.10.10.120`. Per 2026-07-10 masih **dobel deployment** (belum cutover). CI via Harness (delegate di VPS) + host **self-hosted GitHub Actions runner** (pindahan dari VM `10.10.10.8` yang sudah decommissioned). Ingress: nginx-proxy-manager (`~/npm`, network `BIP-ERP-Bridge`). Detail: [[IT - CI-CD]] · [[IT - Network Management]].
- **Akses MongoDB (dev)**: dari IP kantor statik (cloud firewall Biznet allow), Compass/mongosh `mongodb://erp-mongo:<pwd>@116.206.196.31:<port>/?authSource=admin` — port per service (Integration 32789, Employee-Primary 32783, dst).

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