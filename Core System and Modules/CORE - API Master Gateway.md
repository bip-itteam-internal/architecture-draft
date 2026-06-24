## Deskripsi

*API Master Gateway adalah satu-satunya pintu masuk yang menghadap ke internet untuk seluruh ekosistem bip-erp. Gateway ini menangani validasi JWT, CORS, rate limiting, dan response caching opsional via Redis, lalu melakukan reverse-proxy ke service internal lewat Docker network menggunakan internal gateway key header. Dengan pendekatan terpusat ini, pengelolaan authentication dan routing menjadi konsisten dan mudah dipelihara.*

- **Stack:** Go + Fiber v2, Redis (caching opsional)
- **Path:** `api-gateway/`
- **Port:** 6969 (prod: `api.bharatainternasional.com`)
- **Status:** ✅ Implemented (matang, production)

## Endpoint / Fitur (Sudah Diimplementasikan)

**Authentication (JWT Bearer)**
- JWT Bearer via shared-library/auth (HS256), secret dari env `JWT_SECRET`, TTL 72 jam
- Login didelegasikan ke employee-service, lalu gateway yang mint JWT:
	- `/auth/login`, `/auth/login/pin`, `/auth/login/biometrics` — employee-service balikin `PayloadJWT`, gateway menerbitkan JWT
	- Query `device_id` untuk enforcement satu device per akun
- `/auth/refresh` — refresh token
- `/auth/verify/jwt`, `/auth/verify/pin` — verifikasi kredensial
- `/auth/logout` — revoke token + opsional deactivate device

**SSO (one-time-code handoff, bukan IdP eksternal)** — alur lengkap end-to-end di [[CORE - SSO Flow]]
- `POST /auth/sso/ticket` (butuh JWT valid) — menghasilkan kode hex sekali-pakai, disimpan di `ssoStore` in-memory, TTL 30 detik
- `POST /auth/sso/redeem` (publik, rate-limited) — tukar kode menjadi ERP JWT
- Dipakai oleh FE Task Manager untuk handoff sesi

**Internal Service Auth**
- Gateway memasang header `GatewayID = INTERNAL_GATEWAY_KEY` di semua call yang diteruskan ke service internal
- Gateway panic saat startup bila key kosong (fail-fast)

**Routing service via `/api/:module/*`**
- Module: employee, attendance, notification, file, insentive, integration, tiktok-shop, inventory, task-management, hris (orchestrator), it (orchestrator)
- Contoh port internal: employee-service:6970, attendance-service:6971, notification-service:6972, file-service:6973, hris-orchestrator:7000, it-orchestrator:7001
- **Open routes:** module `notification` & `file` boleh skip JWT bila ada query `?key=`

**Routing non-`/api` (proxy khusus)**
- `/auth/*` & `/onboarding/*` → employee-service
- `/public/feedback` → notification-service
- `/public/guestbook` → attendance-service
- `/ext/fingerprint/*` → mesin fingerprint eksternal (X105:4370, X609:4371, dipilih dari serial) + attendance-service
- `/ext/tiktok-shop/callback` & `/ext/tiktok-shop/webhook` → tiktok-shop service
- `/ext/webhook/:service` → integration-service
- `/dev/*` & `/debug/*` (mint admin token) — khusus dev

**Response Caching (Redis)**
- Cache response GET, TTL 3 menit, hanya untuk JSON dengan status 200
- Cache key: `cache:{module}:{employeeID}:{url}`
- Module dikecualikan dari cache: file, hris, integration, inventory

**Lain-lain**
- CORS dan rate limiting di level gateway

## Belum Diimplementasikan / Catatan

- **SSO store in-memory** tidak aman untuk deployment multi-instance (sudah ditandai di kode) — kode SSO yang disimpan di satu instance tidak terlihat oleh instance lain.
- **Revoke token pada refresh/biometrics** masih placeholder kosong — JWT lama tidak benar-benar di-revoke saat refresh atau login biometrics.
- **Route `/dev/*` & `/debug/get-jwt`** sengaja dibuat insecure (mint admin token tanpa proteksi) dan **harus dihapus di production**.

## Dependencies & Integrasi

Gateway meneruskan request ke seluruh service internal berikut:

- [[Microservices - Employee Service]] — auth/login, onboarding, dan delegasi penerbitan JWT
- [[Microservices - Attendance Service]] — presensi, guestbook publik, integrasi fingerprint
- [[Microservices - Notification Service]] — notifikasi, feedback publik (open-route via `?key=`)
- [[Microservices - File Service]] — manajemen file (open-route via `?key=`)
- [[Microservices - Insentive Service]] — insentif
- [[Microservices - Integration Service]] — webhook eksternal (`/ext/webhook/:service`)
- [[Microservices - TikTok Shop Service]] — callback & webhook TikTok Shop
- [[Microservices - Inventory Service]] — inventory (dikecualikan dari cache)
- [[Microservices - Task Management Service]] — task management (klien FE Task Manager via SSO)
- [[CORE - HRIS Orchestrator]] — orchestrator domain HRIS
- [[CORE - IT Orchestrator]] — orchestrator domain IT

Klien utama gateway adalah [[APP - MyBharata]]. Penyimpanan terkait dijelaskan di [[DB - Overview and Notes]].

## Dokumen Terkait

- [[CORE - HRIS Orchestrator]]
- [[CORE - IT Orchestrator]]
- [[Microservices - Employee Service]]
- [[Microservices - Attendance Service]]
- [[Microservices - Notification Service]]
- [[Microservices - File Service]]
- [[DB - Overview and Notes]]
- [[APP - MyBharata]]
