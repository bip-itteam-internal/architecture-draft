## ADR 0007 — Migrasi cloud bertahap untuk service kritis (ketahanan mati listrik / kegagalan server kantor)

- **Status**: 🟡 Proposed (rekomendasi system analyst; menunggu persetujuan manajemen/IT)
- **Tanggal**: 2026-06-29
- **Konteks dok**: [[IT - Server, VMs and Databases]] · [[IT - Backup & DR]] · [[CORE - API Master Gateway]] · [[DB - Overview and Notes]]

## Context

Seluruh sistem ERP bip-erp saat ini berjalan **on-premise** di server kantor: Windows Server (HyperV/RAID5, `10.10.10.15`) plus VM di subnet `10.10.10.x` (ERP Production `10.10.10.120`, Finance Production `10.10.10.38`, dst), dan **semua MongoDB per-service ada di VM ERP Production `10.10.10.120`** (lihat [[IT - Server, VMs and Databases]]). Konsekuensinya: **satu kali mati listrik atau kegagalan server kantor akan menjatuhkan seluruh service secara serentak** — termasuk jalur yang dipicu pihak luar (webhook marketplace) dan autentikasi yang dipakai semua aplikasi.

Dua kelas service paling tidak boleh ikut mati:

1. **Internet-facing / dipicu pihak luar** — event tetap dikirim eksternal walau kantor gelap; bila tak ada yang menerima, data **hilang permanen** (mis. webhook order/escrow/iklan marketplace ke [[Microservices - Integration Service]]).
2. **Tulang punggung** — bila ia mati, seluruh sistem tak bisa dipakai (gateway tunggal + sumber auth/SSO).

Kondisi pendukung yang relevan untuk keputusan ini:
- **Backup/DR masih parsial** ([[IT - Backup & DR]]): backup MongoDB & MinIO berjalan (cron mingguan, Minggu 04:15), tetapi **RPO/RTO, prosedur restore formal, retensi/offsite, dan uji-restore masih TBD**.
- Pola **database-per-service** ([[ADR - 0002 Database-per-Service]]): tiap service memiliki Mongo-nya sendiri; infra bersama hanya **Redis** (cache + queue + distributed lock) & **MinIO** (object storage, dipisah prefix per domain).

## Decision

Lakukan **migrasi cloud bertahap (phased), provider-agnostic**. ADR ini **hanya menetapkan service mana yang dipindah dan urutan prioritasnya**; pemilihan provider (AWS/GCP/Azure/lainnya) dan model migrasi (lift-and-shift Docker vs managed services) **di luar lingkup** dan akan dicatat sebagai ADR terpisah.

### Tier 1 — Wajib migrasi duluan (internet-facing + tulang punggung)

| Service | Alasan |
|---|---|
| [[CORE - API Master Gateway]] | Satu-satunya pintu menghadap internet untuk seluruh ekosistem (login, webhook `/ext/webhook/*`, apply publik, mobile). Mati = tak ada yang bisa masuk. |
| [[Microservices - Integration Service]] | Menerima webhook Shopee/TikTok/Desty terus-menerus. Mati = order/escrow/laporan iklan **hilang** + bridging finansial ke Accurate tertunda. Webhook-consumer jalan tiap 5 detik; sudah ber-Redis-lock + circuit breaker → paling siap di-HA-kan. |
| [[Microservices - TikTok Shop Service]] | Landing OAuth callback + webhook TikTok. Ringan, tetapi event yang masuk saat mati akan **hilang**. Pindah berbarengan dengan Integration. |
| [[Microservices - Employee Service]] | Sumber kebenaran auth + SSO + onboarding. Mati = **tidak ada aplikasi** (MyBharata, Web ERP, Task Manager) bisa login. Sudah berjalan sebagai replica set → relatif HA-ready. |
| [[Microservices - Attendance Service]] | Clock-in/out mobile bersifat time-sensitive (cron pra-alokasi entry tiap 30 menit, flip pending→alpha saat shift mulai). Karyawan remote/GPS harus tetap bisa absen walau kantor mati; clock-in yang hilang = masalah data payroll. |

### Tier 2 — Prioritas berikutnya (kontinuitas operasional & dependency)

| Service | Alasan |
|---|---|
| [[Microservices - Notification Service]] | FCM/WhatsApp/email + email kandidat recruitment. Saat insiden justru notifikasi/alert harus tetap terkirim. |
| [[Microservices - Recruitment Service]] | Endpoint publik `/public/recruitment/apply` (pelamar daftar tanpa login) + email kandidat → menghadap luar, tetapi kekritisan bisnis di bawah order/auth. |
| [[Microservices - File Service]] | Bukan internet-facing, tetapi **dependency** banyak service Tier 1–2 (upload dokumen, foto, offer letter via MinIO). Harus ikut agar tier di atas utuh. |

### Tier 3 — Tetap on-prem / migrasi belakangan (internal, batch, toleran downtime)

- [[Microservices - Insentive Service]] — cron harian 00:00, hasil `DRAFT` dan bisa dihitung ulang; cukup rerun setelah listrik kembali.
- [[Microservices - Inventory Service]] — asset tracking GA, internal, frekuensi rendah, tidak memanggil service lain.
- [[Microservices - Task Management Service]] — produktivitas internal (diakses via SSO).
- [[Microservices - Manufacture Service]] — WMS internal; master sudah dari Google Sheets (sudah cloud).
- [[CORE - OCR Document Service]] — masih 🟡 konsep, belum ada di kode.

### Infra bersama ikut service-nya

- **MongoDB per-service** mengikuti service yang dipindah (database-per-service, [[ADR - 0002 Database-per-Service]]).
- **Redis** (queue webhook + distributed lock) wajib ikut [[Microservices - Integration Service]].
- **MinIO** ikut [[Microservices - File Service]].

## Consequences

- ➕ Jalur internet-facing (webhook marketplace) & auth tetap hidup saat kantor mati listrik / server bermasalah → tidak ada kehilangan event dan karyawan tetap bisa login/absen.
- ➕ Migrasi sekalian menjadi momentum menutup gap DR ([[IT - Backup & DR]]): tetapkan RPO/RTO, prosedur restore, dan backup offsite.
- ➖ Biaya berulang (cloud) + kompleksitas operasional baru (jaringan hybrid on-prem ↔ cloud, secret management, observability lintas-lokasi).
- ⚠️ **Blocker pra-migrasi — `ssoStore` in-memory** ([[CORE - SSO Flow]], `api-gateway/sso.go`): one-time-code SSO disimpan di memori satu instance → **tidak aman multi-instance**. Harus dipindah ke Mongo TTL **sebelum** gateway dijalankan HA/multi-replica di cloud.
- ⚠️ **Blocker pra-migrasi — cron tanpa distributed lock** ([[IT - Background Jobs & Schedulers]]): job di employee/attendance/notification/task-management aman **hanya selama single instance**; bila di-scale horizontal, job bisa dobel. Perlu distributed lock dulu. (Integration sudah Redis-lock; Insentive pakai Mongo `cron_locks`.)
- ⚠️ **Constraint DB** ([[DB - Overview and Notes]] / [[ADR - 0002 Database-per-Service]]): "cluster primary tidak boleh diubah sembarangan (belum ada dynamic cluster picker)"; semua waktu disimpan **UTC** → perhatikan saat memindah/replikasi Mongo.
- ⚠️ Migrasi bertahap menciptakan periode **hybrid** (sebagian service di cloud, sebagian on-prem) → komunikasi service-to-service via gateway harus tetap berfungsi lintas-lokasi (latency + konektivitas jadi pertimbangan).
- 🔗 Pemilihan provider & model migrasi (lift-and-shift vs managed Mongo/Redis/object-store) **belum diputuskan** — direncanakan sebagai ADR terpisah.
- 🔗 Bergantung pada kesehatan gateway sebagai komponen kritis tunggal ([[ADR - 0003 SSO-only Gateway]] · [[IT - Monitoring System]]).

## Dokumen Terkait

- [[IT - Server, VMs and Databases]] · [[IT - Backup & DR]] · [[IT - Background Jobs & Schedulers]] · [[IT - Monitoring System]]
- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]] · [[DB - Overview and Notes]]
- [[ADR - 0002 Database-per-Service]] · [[ADR - 0003 SSO-only Gateway]]
- [[Microservices - Integration Service]] · [[Microservices - TikTok Shop Service]] · [[Microservices - Employee Service]] · [[Microservices - Attendance Service]] · [[Microservices - Notification Service]] · [[Microservices - Recruitment Service]] · [[Microservices - File Service]]
