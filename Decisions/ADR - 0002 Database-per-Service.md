## ADR 0002 — Database-per-Service (Mongo terpisah per microservice)

- **Status**: ✅ Accepted (mencerminkan kondisi kode)
- **Tanggal**: TBD (keputusan historis; dikodifikasi 2026-06-24)
- **Konteks dok**: [[DB - Overview and Notes]] · [[CORE - API Master Gateway]]

## Context

bip-erp adalah mono-repo microservices Go. Tiap service (employee, attendance, notification, file, insentive, integration, inventory, tiktok-shop, task-management) butuh kepemilikan data yang jelas & pengembangan terisolasi. Lihat [[DB - Overview and Notes]].

## Decision

Setiap microservice **memiliki MongoDB-nya sendiri** (container terpisah) dan menjadi pemilik penuh datanya. **Tidak ada akses langsung lintas-database** antar service; komunikasi via HTTP internal melalui [[CORE - API Master Gateway]]. Infra data bersama hanya **Redis** (cache/queue) & **MinIO** (object storage, dipisah prefix per domain). Khusus employee-service berjalan sebagai **replica set** agar bisa diekspos read-only.

## Consequences

- ➕ Service mudah dikembangkan & dideploy terisolasi; blast-radius perubahan kecil.
- ➕ Ownership data tegas → konsisten dengan keputusan lain (mis. service baru = DB baru).
- ➖ Butuh komunikasi service-to-service / orchestrator untuk data lintas-domain; bila alur rumit, pindahkan ke orchestrator ([[CORE - HRIS Orchestrator]] / [[CORE - IT Orchestrator]]).
- ⚠️ Cluster primary tidak boleh diubah sembarangan (belum ada dynamic cluster picker). Semua waktu UTC.
- ⚠️ Fitur/modul baru wajib mengikuti pola ini (mis. rencana [[IT - Form Builder]] = service + Mongo sendiri).

## Dokumen Terkait

- [[DB - Overview and Notes]] · [[CORE - API Master Gateway]] · [[CORE - HRIS Orchestrator]] · [[CORE - IT Orchestrator]]
