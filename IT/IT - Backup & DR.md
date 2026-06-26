## Deskripsi

*Backup data & Disaster Recovery (DR) untuk sistem ERP — pencadangan database & object storage, retensi, serta pemulihan saat terjadi kegagalan. Sebagian sudah berjalan (script + cron); prosedur DR formal masih TBD.*

- **Status**: ⚠️ Sebagian terimplementasi (backup berjalan; DR/restore formal belum)

## Yang Sudah Ada (di kode/infra)

- **Backup MongoDB** — `scripts/mongo-backup.sh` (jalan via Makefile `make mongo-backup`); folder `mongo-backup` di-mount ke container Mongo (`./mongo-backup:/mongo-backup`, "MongoDB automated backups")
- **Cron backup DB** — terjadwal **mingguan, Minggu 04:15** (di cron attendance, dijadwalkan agar tak bentrok job lain)
- **Backup MinIO (object storage)** — `scripts/minio-backup.sh`: mirror `app-bucket` → zip ke `.minio-backup`
- **Log rotation** — shared-library logger menyimpan `MaxBackups` 5–7 berkas
- **Checklist deploy** — "backup system creating backups", "old backups being cleaned up" (DEPLOYMENT_CHECKLIST)

## Disaster Recovery (Konsep / TBD)

- **Prosedur restore** (mongorestore + restore MinIO) terdokumentasi sebagai runbook
- **Retensi & offsite** — berapa lama backup disimpan + salinan di luar server utama
- **RPO/RTO** — target seberapa banyak data boleh hilang & seberapa cepat pulih
- **Uji restore berkala** (verifikasi backup benar-benar bisa dipulihkan)
- **Enkripsi backup** & **monitoring keberhasilan** backup (alert bila gagal)

## Dependensi / Dokumen Terkait

- [[IT - Big Pictures]]
- [[IT - Server, VMs and Databases]] · [[DB - Overview and Notes]] (DB yang di-backup)
- [[IT - CI-CD]] (checklist deploy) · [[Microservices - Attendance Service]] (cron backup mingguan) · [[Microservices - File Service]] (MinIO)
