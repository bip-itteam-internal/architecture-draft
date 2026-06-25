## Deskripsi

*Endpoint **API Gateway** sendiri (bukan proxy). Gateway = entry point: auth/JWT, SSO, onboarding, public/ext, lalu proxy `/api/:module/*` ke service. Grounded ke `api-gateway/main.go`.*

- **Implementasi**: [[CORE - API Master Gateway]] · **Status**: ✅
- **Indeks**: [[API - Index]]

## Auth & SSO (`/auth`)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/auth/login` | Login username/password (`?device_id=`) | publik, rate-limit |
| POST | `/auth/login/pin` | Login PIN | publik |
| POST | `/auth/login/biometrics` | Login biometrik | JWT |
| POST | `/auth/verify/pin` | Verifikasi PIN (aksi sensitif) | JWT |
| GET | `/auth/verify/jwt` | Validasi JWT | JWT |
| GET | `/auth/refresh` | Refresh JWT + data employee | JWT |
| POST | `/auth/logout` | Logout + revoke token (`?employee_id=&device_id=`) | — |
| POST | `/auth/sso/ticket` | Mint one-time SSO code | JWT |
| POST | `/auth/sso/redeem` | Tukar code → token ERP | publik, rate-limit |

## Onboarding (`/onboarding`)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/onboarding/check-unique/:field/:value` | Cek keunikan field | publik |
| POST | `/onboarding/register` | Registrasi karyawan baru | publik |
| GET | `/onboarding/profile` | Profil user terautentikasi | JWT |

## Public (`/public`)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/public/feedback` | Kirim feedback ke grup WA (`?group=`) | publik |
| POST | `/public/guestbook` | Entri guestbook (`?validate=token`) | publik |
| GET | `/public/app/mybharata/version` | Versi app (Android/iOS) | publik |

## Extension (`/ext`)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/ext/fingerprint/health` · `/status` · `/export` | Status/ekspor device fingerprint (`?sn=`) | publik |
| POST | `/ext/fingerprint/event` · `/export` | Event & metadata ekspor fingerprint | publik (validated) |
| GET | `/ext/tiktok-shop/callback` | Callback TikTok Shop | publik |
| POST | `/ext/tiktok-shop/webhook` | Webhook TikTok Shop (TikTok-Signature) | publik |
| POST | `/ext/webhook/:service` | Webhook integrasi generik | publik (forward header) |

## Proxy & sistem
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| ALL | `/api/:module/*` | Proxy ke service internal (+ cache Redis) | JWT (open route: `?key=` utk notification/file) |
| GET | `/` · `/health` | Health gateway (`?check=<service>`) | — |
| GET | `/debug/*` | get-jwt / revoke-jwt / print-jwt / header-local | dev only |
| GET | `/dev/*` | trigger sync TikTok (dev) | dev only |

## Dokumen Terkait
- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]] · [[API - Index]]
