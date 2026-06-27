## Deskripsi

*`hris-dashboard` ("One Bharata") adalah portal web internal ERP/HRIS terpadu Bharata Group — dashboard berbasis role untuk mengelola HR, attendance, finance/insentif, integrasi marketplace, IT, dan GA. Selain itu, web ini juga berperan sebagai **SSO Identity Provider** untuk aplikasi lain (mis. Task Manager).*

- **Stack**: Next.js 16 (App Router) + React 19 + TypeScript; shadcn/ui + Radix + Tailwind v4; TanStack Query + axios; react-hook-form + zod; recharts (grafik); leaflet (peta lokasi absensi); `@uiw/react-md-editor` (article)
- **Path**: `erp-frontend` (repo `erp-frontend`), branch `feature/sso-task-manager-menu`
- **Status**: ✅ Implemented (aktif dikembangkan)

## Autentikasi & Role

- Login `employee_id` + password → `POST /auth/login` (gateway); `token`, `system_roles`, dll disimpan sebagai cookie. Bearer token auto-attach; proactive refresh via `/auth/refresh` (<60 detik sebelum expiry); interceptor 401 retry sekali lalu redirect `/login`.
- **SSO Identity Provider** (mint one-time code via `POST /auth/sso/ticket`):
	- *Inbound handoff*: jika login dengan query `?redirect_url=...`, setelah login di-redirect balik ke app tujuan dengan `?code=...`
	- *Outbound launch*: tombol/menu "Task Management" memanggil `/auth/sso/ticket` lalu menuju `${TASK_MANAGER_APP_URL}/auth/callback?code=...`
- Role dari cookie `system_roles` (map `module → role | role[]`). Module: `erp, finance, insentive, hris, kpi, it, ga, secretary, beauty_hacks, kyura, manufacture, quality, procurement, integration`. Role: `admin, supervisor, security`, dan khusus insentif `adv_leader, adv_marketplace, adv_meta`.
- **Role gating**: sidebar menampilkan module sesuai key `system_roles` (`erp` publik); menu KPI butuh `supervisor`; Guestbook butuh `ga:security`; create Article + seluruh card Splash butuh `admin`; sub-item Incentive di-gate per role.
- **Akun "integration-only" (allowlist env)**: username yang terdaftar di `NEXT_PUBLIC_INTEGRATION_ONLY_USERS` (comma-separated) dibatasi **hanya** melihat section Integration di sidebar — modul publik (`erp`/`hris`/`manufacture`) maupun section turunan Integration (INTEGRATION ACCURATE & INSIGHT) ikut disembunyikan — dan setelah login langsung diarahkan ke `/integration/ads-analytics`. Helper `isIntegrationOnlyUser` (`src/utils/access.ts`) dipakai di `components/layout/sidebar.tsx` & `app/login/page.tsx`. Tujuan: akun review/test marketplace (mis. Shopee).

## Modul / Fitur (Sudah Diimplementasikan)

**ERP (publik)**
- Dashboard: ringkasan kehadiran pribadi (clock in/out, overtime/telat/cuti), ringkasan karyawan, jadwal shift, widget helpdesk (`POST /feedback`)
- Article + Splash (admin): kelola artikel (md-editor) & gambar splash
- Guestbook view (role security), Task Management (tombol SSO ke app eksternal)

**HRIS** (module paling lengkap)
- Employee: CRUD penuh, filter/search, summary, export Excel, status registrasi myBharata, halaman detail
- Attendance: tabel clock in/out + ikon metode + preview geolokasi (Leaflet), update manual, summary
- Contract, Schedule (kalender + holiday CRUD), Vacation (kuota/terpakai/sisa), Report (bulanan + export Excel), Fingerprint (device management), Dashboard analitik, KPI

**KPI (shared)** — scoring per departemen + template CRUD + filter periode/status; HR lihat semua, supervisor hanya divisinya

**Finance**
- Piutang (TikTok/Shopee): tabel accounts-receivable + filter overdue/in-transit
- Incentive: Dashboard (stats/tren + bulk approve), detail, My Incentive, Master KPI CRUD, Master Integration (mapping employee ↔ platform/campaign)

**IT** — Employee (aktivasi akun, reset password), Network (WiFi SSID/MAC CRUD)
**GA** — Inventory (QR, repair history, assignment)
**Integration (marketplace ↔ Accurate)** — Ads Analytics (Shopee/TikTok), Ads Management, Auto-Approve log, Marketplace log, Transactions + Accurate sync, Master Data (Product, Config Accurate), Shipment Setting, OAuth; `integration-accurate`: Sales / Income / Return Shopee & TikTok-Shop
**Lain** — Secretary / Manufacture / Quality / Procurement (KPI saja), Beauty_hacks / Kyura (link eksternal Ideamiils + KPI)

## Belum Diimplementasikan / Catatan

- **`/integration/inventories` = STUB** (data `MOCK_INVENTORIES` hardcoded; inventory asli ada di module GA)
- **`/integration/shipment-setting`** create modal — `// TODO: wire up mutation` (tabel tampil, create belum di-wire)
- **Accurate transaction detail** — panel "Summary Coming Soon"
- **User dropdown**: item Account, Notifications, Settings *disabled*; belum ada route Settings
- **Payroll Calculator**: route ada tapi dihapus dari menu
- **Firebase/FCM push**: kode di-comment, env Firebase masih placeholder
- **Login**: "Forgot your password?" / "Contact admin" link mati; belum ada flow reset password / registrasi
- **Integration-only allowlist = UI-gating saja**: route `/integration/*` & `/dashboard` tetap bisa diakses via URL langsung (tidak dijaga middleware `proxy.ts`); akun tetap butuh role `integration` di `system_roles` agar API tidak 403. Env `NEXT_PUBLIC_*` di-inline saat build → ubah allowlist butuh rebuild/restart. Belum ada hardening middleware untuk akun ini.

## Dependencies & Integrasi

- **API Gateway bip-erp** (`NEXT_PUBLIC_BASE_URL`; dev `http://localhost:6969`) — semua request lewat sini → [[CORE - API Master Gateway]]
- Konsumsi module via gateway: [[Microservices - Employee Service]], [[Microservices - Attendance Service]], [[Microservices - Notification Service]], [[Microservices - Insentive Service]], [[Microservices - Integration Service]], [[Microservices - Inventory Service]], serta operasi IT via [[CORE - IT Orchestrator]] & HR via [[CORE - HRIS Orchestrator]]
- SSO target: app Task Manager (`tasks.bharatainternasional.com`) → memicu sesi ke [[Microservices - Task Management Service]]
- CDN dokumen (`NEXT_PUBLIC_DOC_URL`), MinIO read-key per domain (employee/attendance/task/notification)

## Dokumen Terkait

- [[BASE - Enterance Point]]
- [[APP - MyBharata]]
- [[HRIS - Key Performance Index]]
- [[Finance - Incentive]]
- [[Finance - Bridging App]]
- [[GA - Inventory Management]]
