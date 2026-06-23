## Deskripsi

*Single Sign-On (SSO) ekosistem bip-erp memungkinkan karyawan login sekali di portal ERP, lalu berpindah ke aplikasi internal lain (mis. Task Manager) tanpa login ulang. Mekanismenya adalah **one-time-code handoff** lewat [[CORE - API Master Gateway]] — **bukan** Identity Provider eksternal (OAuth/SAML pihak ketiga). Dokumen ini merangkai alurnya end-to-end; detail per komponen ada di dokumen masing-masing.*

- **Tipe**: one-time-code handoff internal (kode hex sekali-pakai → ditukar jadi ERP JWT)
- **Token**: ERP JWT (HS256, secret `JWT_SECRET`, TTL 72 jam) yang diterbitkan gateway
- **Status**: ✅ Implemented (dipakai produksi; Task Manager sudah cut-over penuh ke gateway)

## Komponen & Peran

| Komponen | Peran dalam SSO | Dokumen |
|---|---|---|
| Web ERP (`hris-dashboard`) | **Identity Provider** — tempat login utama & pemicu handoff | [[APP - Web Application]] |
| API Master Gateway | Menerbitkan JWT, menyimpan one-time code, endpoint `ticket`/`redeem` | [[CORE - API Master Gateway]] |
| Employee Service | **Sumber kredensial** — validasi login, balikin `PayloadJWT` | [[Microservices - Employee Service]] |
| Task Manager (FE) | **Konsumen SSO** — redeem code jadi sesi | [[APP - Dynamic Task Tracker]] |

## Alur SSO End-to-End

**Skenario utama (outbound launch):** karyawan sudah login di Web ERP, lalu membuka Task Manager.

```mermaid
sequenceDiagram
    actor U as Karyawan
    participant W as Web ERP (IdP)
    participant G as API Master Gateway
    participant E as Employee Service
    participant T as Task Manager FE
    U->>W: Login (employee_id + password)
    W->>G: POST /auth/login
    G->>E: validasi kredensial
    E-->>G: PayloadJWT
    G-->>W: ERP JWT (TTL 72 jam)
    U->>W: Klik menu "Task Management"
    W->>G: POST /auth/sso/ticket (Bearer JWT)
    G-->>W: { code } hex sekali-pakai (TTL 30 detik)
    W->>T: redirect ke /auth/callback?code=...
    T->>G: POST /auth/sso/redeem { code }
    G-->>T: { token } = ERP JWT
    T->>G: GET /api/task-management/me (Bearer)
    G-->>T: identitas + role
```

**Skenario alternatif (inbound handoff):** karyawan membuka Task Manager dulu dalam keadaan belum login.
1. Task Manager mendeteksi belum ada token → redirect ke login Web ERP dengan query `?redirect_url=<task-manager>/auth/callback`.
2. Karyawan login di Web ERP; setelah sukses, Web ERP mint `code` via `/auth/sso/ticket` lalu redirect balik ke `redirect_url?code=...`.
3. Lanjut sama seperti skenario utama mulai dari `/auth/sso/redeem`.

## Endpoint SSO (di Gateway)

| Endpoint | Auth | Fungsi |
|---|---|---|
| `POST /auth/login` | publik | Login; gateway delegasi ke employee-service, lalu mint ERP JWT |
| `POST /auth/sso/ticket` | Bearer JWT valid | Menerbitkan one-time code (hex), disimpan di `ssoStore` in-memory, TTL 30 detik |
| `POST /auth/sso/redeem` | publik (rate-limited) | Menukar one-time code menjadi ERP JWT |

## Token & Sesi

- **ERP JWT**: HS256, secret `JWT_SECRET`, TTL **72 jam**, divalidasi di gateway via shared-library/auth.
- Web ERP menyimpan token sebagai cookie + auto-refresh (`/auth/refresh`) menjelang expiry.
- Task Manager menyimpan token di `localStorage` (`erp_token`), dikirim sebagai `Authorization: Bearer` dan sebagai `?token=` pada koneksi WebSocket. **Tanpa refresh token** — 401 memaksa SSO ulang.
- Untuk call internal antar-service, gateway menambahkan header `INTERNAL_GATEWAY_KEY` (bukan JWT user).

## Implementasi Login Redirect (panduan developer)

*Cara membuat login Web ERP mendukung redirect SSO, dan langkah menambah aplikasi konsumen baru. Backend gateway **sudah generic** (`ticket`/`redeem` agnostik aplikasi) → menambah konsumen baru **tidak butuh perubahan backend**, hanya sisi FE + app konsumen + env.*

**Yang sudah ada di kode** (referensi grounding):
- FE inbound redirect: `erp-frontend/src/app/login/page.tsx` — pada `onSuccess` login, baca query `redirect_url`, validasi allowlist, `POST /auth/sso/ticket`, lalu `window.location.href = redirect_url?code=...` (fallback `/dashboard` bila tak ada / gagal).
- FE outbound launch: `erp-frontend/src/features/erp/auth/hooks/use-task-manager-sso.ts` (`useTaskManagerSSO`).
- Gateway: `bip-erp/api-gateway/sso.go` (`ticketHandler`/`redeemHandler`, `ssoStore`, `ssoCodeTTL = 30s`) + `main.go` (`/sso/ticket` di-`ValidateJWT`, `/sso/redeem` + `strictLimiter`).

**Langkah menambah app konsumen SSO baru:**

1. **Sisi ERP (IdP) — allowlist redirect.** Saat ini gating hanya 1 app via `redirectUrl.startsWith(NEXT_PUBLIC_TASK_MANAGER_APP_URL)`. Untuk multi-app, ganti ke allowlist **per-origin** (env `NEXT_PUBLIC_SSO_ALLOWED_ORIGINS`, dipisah koma) — cocokkan `new URL(redirect_url).origin` dengan daftar yang diizinkan (jangan `startsWith` string; rawan open redirect). *Perubahan ini belum ada di kode (TBD).*
2. **Sisi app konsumen.** (a) Guard "belum login" → `redirect ke ${ERP_BASE_URL}/login?redirect_url=${encodeURIComponent(APP_URL + "/auth/callback")}`. (b) Halaman `/auth/callback`: ambil `?code=`, `POST /auth/sso/redeem { code }` → simpan `token` (pola Task Manager: `localStorage` `erp_token`), kirim `Authorization: Bearer` ke `/api/...`; 401 → ulang SSO (tanpa refresh token). Lihat [[APP - Dynamic Task Tracker]].
3. **Env & CORS.** ERP: tambah origin ke allowlist. App: set `GATEWAY_BASE_URL` (prod `https://api.bharatainternasional.com`, dev `http://localhost:6969`) & `ERP_BASE_URL`. Gateway: pastikan origin baru diizinkan **CORS** ([[CORE - API Master Gateway]]) — tanpa ubah kode.

**Verifikasi:** buka app tanpa sesi → ter-redirect ke `/login?redirect_url=...` → login → balik ke `<app>/auth/callback?code=...` (bukan `/dashboard`) → `redeem` balikin `token` → request Bearer 200. Origin di luar allowlist harus diabaikan; code kedaluwarsa (>30s) / dipakai 2× → `redeem` 401.

## Role & Otorisasi

- Role berasal dari `system_roles` (map `module → role | role[]`) di collection `system_authentication` ([[Microservices - Employee Service]]).
- Gateway menurunkan identitas + role lalu meneruskannya ke service via header; service membaca role dari header (mis. Task Manager: `system_roles["task-management"]` → admin / supervisor / staff).

## Aplikasi: Pakai SSO atau Tidak

| Aplikasi | SSO? | Keterangan |
|---|---|---|
| [[APP - Web Application]] (web ERP) | ✅ (IdP) | Tempat login utama + pemicu handoff |
| [[APP - Dynamic Task Tracker]] (Task Manager) | ✅ (konsumen) | Gateway-cutover selesai; tanpa login lokal |
| [[APP - Mobile Application]] (MyBharata) | ❌ | Login JWT **langsung** ke HRIS backend (`admin.hris-bharata.com`), ekosistem terpisah |
| [[GA - Guestbook System (Complete)]] | ❌ | Publik, akses via token kunjungan (bukan SSO) |

## Catatan & Keterbatasan

- **`ssoStore` in-memory** tidak aman untuk deployment multi-instance gateway (kode di satu instance tak terlihat instance lain) — sudah ditandai di kode, disarankan pindah ke Mongo TTL.
- **Revoke token saat refresh/biometrics** masih placeholder — JWT lama tidak benar-benar di-revoke.
- Route `/dev/*` & `/debug/get-jwt` (mint admin token) **insecure**, khusus dev, harus dihapus di production.
- **Allowlist redirect masih single-app** (`startsWith(NEXT_PUBLIC_TASK_MANAGER_APP_URL)`) — generalisasi multi-origin masih TBD; `startsWith` rawan **open redirect**, sebaiknya pindah ke pencocokan per-origin sebelum membuka untuk banyak app.
- **Re-login paksa**: login page meng-auto-logout saat mount (hapus cookie `token` dkk), sehingga user ERP yang sudah login lalu diarahkan ke `/login?redirect_url=...` tetap dipaksa login ulang. Perbaikan TBD: bila token masih valid + origin allowlist, langsung mint code tanpa minta password.
- **Silent fallback**: bila `/auth/sso/ticket` gagal, user diam-diam mendarat di `/dashboard` ERP tanpa pesan ke app asal.

## Dokumen Terkait

- [[CORE - API Master Gateway]]
- [[Microservices - Employee Service]]
- [[APP - Web Application]]
- [[APP - Dynamic Task Tracker]]
- [[Microservices - Task Management Service]]
- [[BASE - Enterance Point]]
