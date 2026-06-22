## Deskripsi

*IT Helpdesk / ticketing — desk dimiliki & ditangani **divisi IT**, sementara **karyawan semua divisi dapat membuat tiket** untuk meminta bantuan/penyelesaian. Konsep sisi IT; implementasinya sudah ada di backend [[Microservices - Task Management Service]] + FE [[APP - Dynamic Task Tracker]].*

- **Status**: ✅ Implemented (backend + FE)
- **Auth**: SSO via gateway (lihat [[CORE - SSO Flow]])

## Cara Kerja

- Karyawan (semua divisi) **buat tiket** → tim IT mentriase lewat **Kanban**: `Request → Todo → On Going → Testing → Done` (+ jalur `Ditolak`)
- **Approval** (Request→Todo wajib start/due date + prioritas) + **SLA 2-dimensi** (response + resolution) dengan **scheduler eskalasi** otomatis
- Comment, checklist, attachment (MinIO), audit trail
- **Notifikasi**: realtime WebSocket + FCM + inbox (via notification-service)
- **Laporan**: stats, report SLA (on-time response/penyelesaian per divisi), manpower performance, timeline

## Peran

- **Requestor** — karyawan dari semua divisi (pembuat tiket)
- **IT staff / supervisor** — menangani & menyelesaikan tiket
- **Admin** (sekretaris lintas-divisi) — pengelolaan lintas divisi

## Catatan Positioning

Kode saat ini masih mendukung **multi-divisi** (Space + supervisor per divisi). Sesuai positioning sebagai **IT Helpdesk**, penanganan difokuskan ke divisi IT dengan semua divisi sebagai requestor — pembatasan scope perlu dipertimbangkan di implementasi (lihat catatan di [[Microservices - Task Management Service]] & [[APP - Dynamic Task Tracker]]).

## Implementasi & Dokumen Terkait

- [[Microservices - Task Management Service]] (backend) · [[APP - Dynamic Task Tracker]] (FE)
- [[CORE - SSO Flow]]
- [[IT - Employee System]] · [[IT - Big Pictures]]
