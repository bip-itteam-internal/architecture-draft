## Deskripsi

*Backup data & Disaster Recovery (DR) untuk sistem ERP — pencadangan database & object storage, retensi, serta pemulihan saat terjadi kegagalan. Sebagian sudah berjalan (script + cron); prosedur DR formal masih TBD.*

- **Status**: ⚠️ Sebagian terimplementasi (backup berjalan; DR/restore formal belum)

## Yang Sudah Ada (di kode/infra)

- **Backup MongoDB** — `scripts/mongo-backup.sh` (jalan via Makefile `make mongo-backup`); folder `mongo-backup` di-mount ke container Mongo (`./mongo-backup:/mongo-backup`, "MongoDB automated backups")
- **Cron backup DB (server lama .120)** — terjadwal **mingguan, Minggu 04:15** (di cron attendance, dijadwalkan agar tak bentrok job lain)
- **Backup MinIO (object storage)** — `scripts/minio-backup.sh`: mirror `app-bucket` → zip ke `.minio-backup`
- **Cron backup DB (VPS Biznet, 2026-07-09)** — `/usr/local/bin/erp-backup.sh` (cron root **harian 02:00 WIB**): `mongodump --archive | gzip` + zip mirror MinIO, output ke **`/backup`** (additional disk sdb 100G, terpisah dari disk data sda). **Retensi 14 hari** (`-mtime +14`). Log `/backup/backup.log` (logrotate bulanan). Per 2026-08-09: 19 container Mongo, `/backup/mongo` 11G + `/backup/minio` 11G. ⚠️ **Beda-disk, BUKAN offsite** — VPS/sdb hancur → backup ikut hilang.
- **Daftar container auto-discovery (2026-08-09)** — script mendeteksi container Mongo lewat `docker ps`, bukan daftar tetap. Sebelumnya daftar 11 nama ditulis manual dan tak pernah diperbarui saat service baru lahir, sehingga **8 database tak pernah ter-backup sekali pun**: Marketing-Analytics (481 MB), Warehouse, Procurement, Calendar, Form-Builder, Learning, HRD-Document, log-direktur. Script tetap melaporkan sukses tiap malam karena 11 yang terdaftar memang berhasil — tak ada sinyal apa pun bahwa ada yang terlewat. Sumber script kini di repo (`bip-erp/scripts/erp-backup.sh`, PR [#1093](https://github.com/bip-itteam-internal/bip-erp/pull/1093)); sebelumnya hidup hanya di server, di luar version control. ⚠️ Deploy **belum otomatis**: setelah merge, file masih perlu disalin manual ke `/usr/local/bin/erp-backup.sh`.
- **Kredensial per container + verifikasi dump** — kredensial diambil dari env container dulu, baru `.env` global, dengan fallback tanpa-auth (`log-direktur-mongo-1` jalan tanpa auth, menolak kredensial global). Dump berukuran ≤1 KB dihitung **GAGAL**: `mongodump` bisa keluar dengan status sukses sambil menulis nol byte. Log ditutup ringkasan `OK/total` + daftar yang gagal.
- **Log rotation** — shared-library logger menyimpan `MaxBackups` 5–7 berkas; mongod pakai Docker `json-file` driver (max 50m × 3)
- **Checklist deploy** — "backup system creating backups", "old backups being cleaned up" (DEPLOYMENT_CHECKLIST)

## Disaster Recovery (Konsep / TBD)

- **Prosedur restore** (mongorestore + restore MinIO) terdokumentasi sebagai runbook
- **Retensi & offsite** — retensi VPS Biznet = 14 hari (sudah). **Offsite** masih TBD: backup bip-vps saat ini ke additional disk sdb (beda-disk, tapi masih 1 VPS). Target lanjut = Biznet Object Storage (S3, offsite sejati) — belum diimplementasi.
- **RPO/RTO** — target seberapa banyak data boleh hilang & seberapa cepat pulih
- **Uji restore berkala** — belum terjadwal. Pernah dilakukan **sekali, manual** (2026-08-09): kedelapan database yang sebelumnya tak punya salinan diuji `mongorestore --archive --dryRun`, semuanya bisa dipulihkan. Uji berkala otomatis masih TBD.
- **Enkripsi backup** & **monitoring keberhasilan** backup (alert bila gagal) — ringkasan `OK/total` sudah masuk `/backup/backup.log`, tapi **belum ada alert**: kegagalan hanya terlihat bila ada yang membuka log.

## Dependensi / Dokumen Terkait

- [[IT - Big Pictures]]
- [[IT - Server, VMs and Databases]] · [[DB - Overview and Notes]] (DB yang di-backup)
- [[IT - CI-CD]] (checklist deploy) · [[Microservices - Attendance Service]] (cron backup mingguan) · [[Microservices - File Service]] (MinIO)
