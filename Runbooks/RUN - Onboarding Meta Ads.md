> **Status:** 🟡 Draft — disusun dari dokumentasi publik Lazada Open Platform (`open.lazada.com`) per Juli 2026. **Belum pernah dieksekusi dengan akun Bharata asli** — belum ada implementasi client Lazada di [[Microservices - Integration Service]] (§Lazada, konsep). Jangan anggap langkah di bawah final; verifikasi ulang tiap field/URL saat implementasi nyata dimulai, dan naikkan status ke ✅ setelah terverifikasi jalan.

## Tujuan

Membuat akun developer + app di Lazada Open Platform dan mendapatkan kredensial (App Key/App Secret) serta otorisasi seller, sebagai prasyarat integrasi API Lazada langsung (setara pola Shopee/TikTok Shop yang sudah ada).

## Kapan dipakai

Saat memulai implementasi client Lazada di `services/integration` (lihat rencana teknis di [[Microservices - Integration Service]] §Lazada) — baik untuk environment test/sandbox maupun produksi.

## Prasyarat

- Akun email untuk daftar di `open.lazada.com`.
- Akun Seller Center Lazada Bharata yang sudah aktif (butuh **Seller ID** — dilihat dari profil Seller Center) untuk langkah otorisasi.
- Redirect/callback URL yang bisa diakses publik (mengarah ke handler `AuthCallback` di `services/integration`, mirror pola `shopeeRoute.Get("/auth/callback", ...)` / `tpRoute.Get("/auth/callback", ...)`).

## Langkah

1. **Daftar/masuk** ke `open.lazada.com` (sign in atau sign up akun developer).
2. **Buat App** — buka menu *App Console* → *create* → pilih tipe app **"Seller In-house APP"** (app pemakaian sendiri, bukan app publik untuk banyak seller pihak ketiga — sejalan dengan pola Shopee `ERP_SYSTEM`/`ADS_SERVICE` di BIP yang juga app privat, bukan app marketplace publik). Isi App Name & Callback URL.
3. **Ambil kredensial** — buka *Manage* pada app yang baru dibuat → bagian **"Advance information"** di App Overview → catat **App Key** dan **App Secret**. Simpan sebagai secret (env var), jangan commit ke repo.
4. **Otorisasi seller** — buka menu *Auth Management* → masukkan **Seller ID** (dari profil Seller Center), **country**, serta email/password seller → proses otorisasi mengikuti standar OAuth2.0 ("Code for token"):
   - Authorization URL: `https://auth.lazada.com/oauth/authorize?response_type=code&force_auth=true&redirect_uri={callback_url}&client_id={app_key}`
   - Setelah user approve, Lazada redirect ke `{callback_url}?code=...`
5. **Tukar `code` jadi access token** — panggil `/auth/token/create` dengan parameter wajib: `app_key`, `timestamp`, `sign_method`, `code`, `sign`. `sign` dihitung HMAC-SHA256 atas string parameter (App Secret sebagai key), hasil di-hex lalu di-uppercase — pola sign umum Lazada Open Platform (dipakai juga di endpoint API lain, bukan cuma token exchange). Response berisi `access_token`, `refresh_token`, `country`, `account_id`, `expires_in`, `refresh_expires_in`.
6. **Mode test vs produksi** — app baru default di mode **test** (kuota/rate-limit terbatas). Untuk menaikkan durasi token & call-limit, ajukan **"Apply Online"** di App Console (proses approval dari pihak Lazada, bukan otomatis) — mirip proses request kenaikan limit yang sudah pernah dilakukan untuk Shopee, lihat [[LOG - Shopee API Rate Limit Request]] sebagai preseden.
7. **Simpan kredensial ke sistem** — setelah client Lazada ada di kode, simpan `access_token`/`refresh_token` mengikuti pola entity `PlatformToken`/`Credential` yang sudah ada (lihat [[Microservices - Integration Service]] §Lazada) — bukan mekanisme penyimpanan baru.

## Verifikasi

- Panggil salah satu endpoint ringan (mis. daftar order/`GetOrders` dengan filter kecil) menggunakan `access_token` hasil langkah 5 → dapat response 200 dengan payload valid, bukan error signature/otorisasi.
- App Key/App Secret tersimpan sebagai env var di konfigurasi service (bukan hardcoded), sejalan pola `SHOPEE_PARTNER_ID`/`TIKTOK_SHOP_APP_ID` yang sudah ada.

## Bila gagal / Rollback

- **Sign tidak valid** — cek ulang urutan parameter sebelum di-HMAC (Lazada mengharuskan parameter terurut alfabetis sebelum digabung jadi base string) dan pastikan App Secret yang dipakai benar (tiap app punya secret sendiri, jangan tertukar dengan app Shopee/TikTok).
- **`code` sudah kedaluwarsa** — authorization code Lazada berumur pendek; ulangi langkah 4 (otorisasi ulang) bila token exchange gagal.
- **Rate limit / app diblokir sementara** — tunggu sesuai jendela reset Lazada, lalu evaluasi apakah perlu pola circuit-breaker seperti Shopee (lihat §Observability & Ketahanan Shopee di [[Microservices - Integration Service]]) sebelum retry masif.
- **Jangan** merujuk dokumentasi API Seller Center lama (`lazada-sellercenter.readme.io`) — platform itu **sudah di-decommission sejak 2018**; satu-satunya sumber resmi aktif adalah `open.lazada.com`.

## Referensi Eksternal

- [Lazada Open Platform](https://open.lazada.com/) — portal utama, App Console
- [Seller authorization introduction](https://open.lazada.com/apps/doc/doc?nodeId=10777&docId=108260)
- [Configure seller authorization](https://open.lazada.com/apps/doc/doc?nodeId=10434&docId=108056)
- [Getting Started - Lazada Open Platform](https://open.lazada.com/doc/doc.htm)
- [Webhook API Trade Order Notifications](https://open.lazada.com/apps/doc/doc?nodeId=29538&docId=120196)
- [Getting started with Lazada Push Mechanism](https://open.lazada.com/apps/doc/doc?nodeId=29526&docId=120168)
- [Decommission of API documentation - Announcement](https://lazada-sellercenter.readme.io/docs/announcement) — konfirmasi Seller Center API lama sudah mati sejak 2018

## Dokumen Terkait

- [[Microservices - Integration Service]] — rencana teknis §Lazada, implementasi Shopee/TikTok Shop sebagai pola acuan
- [[Sales - Marketplace Integration]] — sisi konsep/bisnis
- [[External - Desty]] — jalur Lazada generik yang sudah berjalan saat ini
- [[LOG - Shopee API Rate Limit Request]] — preseden insiden rate-limit & proses request kenaikan limit ke vendor
