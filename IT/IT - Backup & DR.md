## Deskripsi

*Backup data & Disaster Recovery (DR) untuk sistem ERP — pencadangan database & object storage, retensi, serta pemulihan saat terjadi kegagalan. Sebagian sudah berjalan (script + cron); prosedur DR formal masih TBD.*

- **Status**: ⚠️ Sebagian terimplementasi (backup berjalan; DR/restore formal belum)

## Yang Sudah Ada (di kode/infra)

- **Backup MongoDB** — `scripts/mongo-backup.sh` (jalan via Makefile `make mongo-backup`); folder `mongo-backup` di-mount ke container Mongo (`./mongo-backup:/mongo-backup`, "MongoDB automated backups")
- **Cron backup DB (server lama .120)** — terjadwal **mingguan, Minggu 04:15** (di cron attendance, dijadwalkan agar tak bentrok job lain)
- **Backup MinIO (object storage)** — `scripts/minio-backup.sh`: mirror `app-bucket` → zip ke `.minio-backup`
- **Cron backup DB (VPS Biznet, 2026-07-09)** — `/usr/local/bin/erp-backup.sh` (cron root **harian 02:00 WIB**): `mongodump --archive | gzip` untuk **11 Mongo** (semua service; Employee-Secondary di-skip = replika) + zip mirror MinIO, output ke **`/backup`** (additional disk sdb 100G, terpisah dari disk data sda). **Retensi 14 hari** (`-mtime +14`). Backup pertama ~888M (Integration 355M + MinIO 522M terbesar). Log `/backup/backup.log` (logrotate bulanan). ⚠️ **Beda-disk, BUKAN offsite** — VPS/sdb hancur → backup ikut hilang.
- **Log rotation** — shared-library logger menyimpan `MaxBackups` 5–7 berkas; mongod pakai Docker `json-file` driver (max 50m × 3)
- **Checklist deploy** — "backup system creating backups", "old backups being cleaned up" (DEPLOYMENT_CHECKLIST)

## Disaster Recovery (Konsep / TBD)

- **Prosedur restore** (mongorestore + restore MinIO) terdokumentasi sebagai runbook
- **Retensi & offsite** — retensi VPS Biznet = 14 hari (sudah). **Offsite** masih TBD: backup bip-vps saat ini ke additional disk sdb (beda-disk, tapi masih 1 VPS). Target lanjut = Biznet Object Storage (S3, offsite sejati) — belum diimplementasi.
- **RPO/RTO** — target seberapa banyak data boleh hilang & seberapa cepat pulih
- **Uji restore berkala** (verifikasi backup benar-benar bisa dipulihkan)
- **Enkripsi backup** & **monitoring keberhasilan** backup (alert bila gagal)

## Dependensi / Dokumen Terkait

- [[IT - Big Pictures]]
- [[IT - Server, VMs and Databases]] · [[DB - Overview and Notes]] (DB yang di-backup)
- [[IT - CI-CD]] (checklist deploy) · [[Microservices - Attendance Service]] (cron backup mingguan) · [[Microservices - File Service]] (MinIO)
