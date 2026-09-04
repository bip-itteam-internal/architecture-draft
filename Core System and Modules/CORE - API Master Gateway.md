## Deskripsi

*API Master Gateway adalah satu-satunya pintu masuk yang menghadap ke internet untuk seluruh ekosistem bip-erp. Gateway ini menangani validasi JWT, CORS, rate limiting, dan response caching opsional via Redis, lalu melakukan reverse-proxy ke service internal lewat Docker network menggunakan internal gateway key header. Dengan pendekatan terpusat ini, pengelolaan authentication dan routing menjadi konsisten dan mudah dipelihara.*

- **Stack:** Go + Fiber v2, Redis (caching opsional)
- **Path:** `api-gateway/`
- **Port:** 6969 (prod: `api.bharatainternasional.com`)
- **Status**: ✅ Implemented (matang, production)

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
- **Header identitas dari klaim JWT** (`Reroute` membuang header `BIP-*` kiriman klien lalu meng-inject ulang dari klaim): `BIP-Employee-Id`, `BIP-System-Roles`, dan **`BIP-Company-ID`** (perusahaan/tenant; fallback `"BIP"`) — dikirim ke **semua** module secara seragam, dan diteruskan antar-service via `InternalRequest`. Inilah fondasi multi-perusahaan: [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]].

> ⛔ **Konsekuensi yang mengikat SETIAP service di belakang gateway: `ReadBufferSize` wajib ≥ 32 KB** (default fasthttp cuma 4 KB). Injeksi di atas membuat permintaan ke hulu **selalu lebih besar** daripada yang dikirim browser — `Reroute` menyalin seluruh header masuk lalu menambahkan `BIP-Permissions`, `BIP-System-Roles`, dan `BIP-Supervised-Departments` — dan ukurannya **tumbuh mengikuti jumlah permission-set** yang dipegang akun pemanggil ([[CORE - RBAC dan Permission Set]]).
>
> Di bawah 32 KB fasthttp menolak di lapisan HTTP **sebelum satu handler pun jalan**, membalas `431 Request Header Fields Too Large`. Karena gateway meneruskan status upstream apa adanya (`c.Status(resp.StatusCode)`), **431 milik service tampil di browser seolah berasal dari gateway** — jadi jangan mulai menyelidiki dari gateway.
>
> Dua sifat membuatnya sulit dikenali. **Per-akun**: akun berizin sedikit tetap lancar, sehingga gejalanya terlihat seperti masalah satu orang. **Per-rute**: hanya modul yang belum dinaikkan yang gagal, sehingga sisanya yang normal terbaca sebagai bukti gateway sehat. Pembeda tercepat: kirim satu header probe besar (mis. `X-Probe` 6 KB) ke rute yang dicurigai **dan** ke rute modul lain; kalau yang kedua 200, yang salah modulnya, bukan gateway.
>
> Diukur 2026-09-04: dari 25 proses Fiber di repo, 22 sudah 32 KB sejak `e84b93c4` (2026-08-18). Commit itu menyapu `api-gateway` + `services/*` dan **melewatkan `orchestrator/*`**, yang secara folder bukan `services/*` — lihat [[CORE - HRIS Orchestrator]] dan [[CORE - IT Orchestrator]].

**Routing service via `/api/:module/*`**
- Module: employee, attendance, notification, file, insentive, integration, tiktok-shop, inventory, task-management, recruitment, hris (orchestrator), it (orchestrator), **learning** (✅ live dev + prod 2026-08-06, port 6987 — [[Microservices - Learning Service]]), form-builder (⚠️ merged 2026-08-01, **belum live di dev** — `/health?check=form-builder` masih balas `400 unknown service`)
- Contoh port internal: employee-service:6970, attendance-service:6971, notification-service:6972, file-service:6973, hris-orchestrator:7000, it-orchestrator:7001
- **Open routes:** module `notification` & `file` boleh skip JWT bila ada query `?key=`
- ⚠️ **Catch-all, bukan allowlist.** `api.All("/:module/*")` meneruskan **seluruh** sub-path apa adanya; gateway tidak punya daftar rute yang diizinkan dan tidak menyaring path. Digabung dengan `Reroute` yang **mengisi sendiri** `BIP-Gateway-ID` (sehingga `ValidateGateway` di service selalu lolos), akibatnya **prefix `/internal/...` di service ikut terbuka ke internet**: syaratnya hanya token login valid, peran apa pun. Jadi `/internal/` **bukan** batas keamanan, dan setiap rute wajib menggerbangi dirinya sendiri. Latar, bukti di produksi, dan aturannya: [[ADR - 0031 Prefix internal Bukan Batas Keamanan]].
- Konsekuensi lain dari catch-all yang sama: rute yang punya limiter khusus di level gateway bisa **dilewati** lewat jalur `/api/<module>/*`. Contoh nyata: `strictLimiter` menempel di `/auth/login`, tapi employee-service juga melayani `/auth/login` sehingga `/api/employee/auth/login` mencapainya tanpa limiter (belum ditambal, tercatat di ADR 0031).

**Routing non-`/api` (proxy khusus)**
- `/auth/*` & `/onboarding/*` → employee-service
- `/public/feedback` → notification-service
- `/public/guestbook` → attendance-service
- `/public/recruitment/apply` → recruitment-service (pelamar mendaftar sendiri tanpa JWT)
- `/public/recruitment/postings` & `/public/recruitment/postings/:id` → recruitment-service (portal karir: daftar & detail lowongan Open, tanpa JWT)
- `/public/recruitment/track/:token` → recruitment-service (kandidat cek status lamaran via tracking token, tanpa JWT)
- `/ext/fingerprint/*` → mesin fingerprint eksternal (X105:4370, X609:4371, dipilih dari serial) + attendance-service
- `/ext/tiktok-shop/callback` & `/ext/tiktok-shop/webhook` → tiktok-shop service
- `/ext/webhook/:service` → integration-service
- `/dev/*` & `/debug/*` (mint admin token) — khusus dev

**Response Caching (Redis)**
- Cache response GET, TTL 3 menit, hanya untuk JSON dengan status 200
- Cache key: `cache:{module}:{employeeID}:{url}`
- Module dikecualikan dari cache: file, hris, integration, inventory

> ⚠️ **Kunci cache tidak memuat hak apa pun — hanya employee & URL.** Dua token milik ORANG YANG SAMA dengan klaim berbeda karena itu berbagi satu entri. Balasan token lama (mis. terbit sebelum `supervised_departments` atau sebuah permission-set dipasang) tersaji ke token baru selama TTL 3 menit, dan sebaliknya. Gejalanya: daftar yang seharusnya terisi tetap **kosong tanpa galat** sesaat setelah hak berubah — persis seperti "jabatan ini tak berhak", padahal cuma cache.
>
> Terbukti di dev 2026-08-10: panel Permintaan Barang yang sudah terisi mendadak hilang setelah tab lama (token pra-perubahan) memuat halaman lebih dulu; `redis-cli FLUSHALL` memulihkannya seketika. Karena itu **setiap pengukuran RBAC harus didahului flush cache**, dan perubahan hak selalu menuntut login ulang PLUS menunggu TTL habis — lihat [[CORE - RBAC dan Permission Set]].

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
- [[Microservices - Recruitment Service]] — ATS; termasuk apply publik `/public/recruitment/apply` (tanpa JWT)
- [[Microservices - Form Builder Service]] — form dinamis IT/HRGA (⚠️ merged 2026-08-01, belum live di dev). ⚠️ **`FORM_BUILDER_MODULE_URL` masuk map `InternalURL` yang divalidasi**, jadi nilai kosong = gateway panic saat boot = seluruh ERP mati. `.env` **dev dan prod sudah diisi 2026-08-01** dan diverifikasi lewat `docker compose config`; yang tersisa: gateway harus dideploy dengan `docker-compose.yml` yang ikut ter-merge, bukan env lama. Rute `/internal/compliance`-nya adalah contoh penerapan [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]: karena catch-all di atas membuatnya terbuka ke internet, rute itu mengunci identitas ke header dan mengabaikan query param dari request pemakai.
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
- [[Microservices - Recruitment Service]]
- [[DB - Overview and Notes]]
- [[APP - MyBharata]]
