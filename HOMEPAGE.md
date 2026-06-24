## Pemberitahuan

*Semua yang ada di sini hanyalah ikhtisar singkat dan gambaran kasar tentang bagaimana sistem terlihat serta bagaimana setiap bagian berinteraksi satu sama lain, hal ini memerlukan diskusi terbuka lebih lanjut bersama-sama. Halaman ini juga berfungsi sebagai **landing page / peta dokumentasi** — lihat indeks di bawah.*

## Seperti apa sistem ERP itu?

**Backend** ERP (`bip-erp`) berupa **mono-repo microservices Go** (di belakang satu API Gateway). **Frontend & aplikasi** berada di **repo terpisah**: web ([[APP - Web ERP]]), mobile ([[APP - MyBharata]]), Task Manager ([[APP - Dynamic Task Tracker]]), generator konten (Ideamills → [[Sales - Veo (Gemini) Implementation]]), dan beberapa tool lain.

Interaksi antar service dapat diinterpretasikan seperti gambar di bawah ini
![[erp-request-nutshell.png]]

### Apa yang dilakukan API Gateway?

Ini adalah entry point untuk request, yang juga menangani JWT authentication, **SSO** (one-time-code handoff antar aplikasi internal — lihat [[CORE - SSO Flow]]), dan pengecekan propagasi routes untuk open/restricted routes. Detail: [[CORE - API Master Gateway]].

### Penjelasan tentang struktur routes API Gateway

Secara default API Gateway tidak memiliki routes-nya sendiri, dan hanya meneruskan request ke internal services sesuai kebutuhan *(dengan pengecualian authentication karena akan diproses lebih lanjut oleh API Gateway itu sendiri untuk pembuatan JWT)*

![[api-gateway-routes.png]]

Daftar struktur routes (detail lengkap):
- **/public** - public routes, dapat diakses bebas oleh siapa saja
- **/health** - heartbeat check untuk services, selalu di-resolve ke `/api/:service/`
- **/api** - panggilan api normal ke internal services dengan syarat JWT dan/atau `access-key` unik (untuk open route services)
- **/auth** - authentication: selalu memanggil `/api/employee` di balik layar, mengambil data employee, lalu menandatanganinya dengan JWT. Termasuk **SSO** (`/auth/sso/ticket` & `/auth/sso/redeem`)
- **/ext** - extension/external routes, akses langsung (tanpa JWT) ke services atau webhooks *(mis. integrasi fingerprint, callback marketplace)*
- **/onboarding** - akses publik (minimal) untuk fungsi helper onboarding via aplikasi mobile
- **/debug** dan **/dev** - debug & development routes, hanya di environment dev/staging

### Apa yang dilakukan Orchestrator?

Orchestrator adalah wrapper untuk aksi berbasis event/lintas-service — satu request yang perlu memanggil beberapa service sekaligus. Saat ini: **HRIS** ([[CORE - HRIS Orchestrator]]) dan **IT** ([[CORE - IT Orchestrator]]).

### Apa yang dilakukan Service?

Service adalah end-point yang berinteraksi dengan database-nya masing-masing (database-per-service), sehingga pengembangan tiap service mudah & terisolasi. Dua tipe:
- **Open route services** - request dari luar boleh, perlu access/service keys; fallback ke JWT bila keys tak ada
- **Restricted services** - wajib JWT authentication

## Tipe Request

1. **Direct request ke services** — contoh `/api/employee/status`, `/api/file/preview`
2. **Request ke orchestrator** — aksi bisnis lintas-service, contoh `/api/hris/employees/multi` (buat employee + upload dokumen + notifikasi)
3. **Direct request ke services yang bergantung pada service lain** — panggilan internal service-to-service. **Bila alurnya membingungkan, pindahkan ke orchestrator.**

## Struktur Repository (bip-erp)

```
├── docker-compose.yml      (entry point semua service)
├── Makefile
├── api-gateway             (auth + routing)
├── orchestrator/           (hris, it)
├── services/               (employee, attendance, notification, file,
│                            insentive, integration, inventory,
│                            task-management, tiktok-shop)
└── shared-library/         (auth, database, routes, common, models,
                             notification[WA/FCM], minio, accurate, logs, validation)
```
> Catatan: stok backup di `mongo-backup`/`minio-backup` (lihat [[IT - Backup & DR]]); deployment via GitHub Actions/Codemagic ([[IT - CI-CD]]).

## Peta Dokumentasi (Index)

**Core / Infra** → [[CORE - API Master Gateway]] · [[CORE - SSO Flow]] · [[CORE - HRIS Orchestrator]] · [[CORE - IT Orchestrator]] · [[DB - Overview and Notes]] · [[CORE - OCR Document Service]]

**Microservices** → [[Microservices - Employee Service]] · [[Microservices - Attendance Service]] · [[Microservices - Notification Service]] · [[Microservices - File Service]] · [[Microservices - Insentive Service]] · [[Microservices - Integration Service]] · [[Microservices - Inventory Service]] · [[Microservices - Task Management Service]] · [[Microservices - TikTok Shop Service]]

**Aplikasi** → [[BASE - Enterance Point]] · [[APP - Web ERP]] · [[APP - MyBharata]] · [[APP - Dynamic Task Tracker]] · [[APP - Ideamills]] · [[APP - Tiktok Insight Analyzer]] · [[APP (Extension) - Fingerprint Listener (Complete)]]

**Domain (Big Pictures)** → [[HRIS - Big Pictures]] · [[Sales - Big Pictures]] · [[GA - Big Pictures]] · [[IT - Big Pictures]] · [[WH - Management System]] · [[Finance]]

**Quality & Regulatory** → [[QA - Big Pictures]] (CPOB/GMP · BPOM/izin edar · batch & traceability · deviation/CAPA · ED & recall — farmasi)

**Reference** → [[REF - Glossary]] (glosarium istilah & singkatan Bharata)

**Benchmark** → [[ERPGo - Overview & Gap Matrix]] (riset fitur produk eksternal vs bip-erp)

**API Reference** → [[API - Index]] (daftar endpoint lengkap per service)

**Mulai di sini (dev)** → [[DEVELOPER GUIDE]] (onboarding · workspace sibling · flow agent-kit · konvensi · git)

**Roadmap & Keputusan** → [[ROADMAP]] · [[REF - Ownership & RACI]] · [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0002 Database-per-Service]] · [[ADR - 0003 SSO-only Gateway]] · [[ADR - 0004 ERPGo Out-of-Scope]]

**Tata Kelola** → [[IT - SOP Dokumentasi Vault]] (cara nulis dok konsisten + template)

## Dari mana saya mulai?

Biasakan diri dengan shared-library, api-gateway, lalu boilerplate services/orchestrator. Untuk membuat service baru:
1. Buat folder service → `go mod init '<service-name>'`
2. Tautkan shared-library: `go mod edit -replace github.com/bharata/shared-library=../../shared-library` lalu `go get github.com/bharata/shared-library@v0.0.0`
3. (Salin template dari service lain) buat `main.go` + `Dockerfile`
4. Edit `docker-compose.yml`
5. Tambah service-module-url ke `api-gateway/main.go` (hashmap `InternalURL`)
6. Tambah variabel baru ke `.env`

## TODO

1. ~~Pisahkan jadi repo terpisah~~ → FE/app sudah terpisah; backend masih mono-repo Go
2. shared-library sebagai repo standalone (agar mudah di-include tiap service)
3. Pisahkan docker-compose & env per service secara benar

## Menggunakan authentication ERP yang sudah ada untuk aplikasi eksternal

Bila tidak bisa membangun di atas ERP (atau punya prototype standalone) namun butuh authentication, gunakan authentication ERP yang ada via **SSO** ([[CORE - SSO Flow]]): panggil fungsinya, simpan JWT sebagai header, validasi tiap akses halaman.

![[erp-external-auth-use-case.svg]]
