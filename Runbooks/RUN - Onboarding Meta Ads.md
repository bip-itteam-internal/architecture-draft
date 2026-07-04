> **Status:** 🟡 Draft — disusun dari dokumentasi publik Meta for Developers (`developers.facebook.com`) per Juli 2026. **Belum pernah dieksekusi dengan akun Bharata asli** — belum ada implementasi client Meta Ads di [[Microservices - Integration Service]] (§Meta Ads, konsep). Jangan anggap langkah di bawah final; verifikasi ulang tiap field/permission saat implementasi nyata dimulai, dan naikkan status ke ✅ setelah terverifikasi jalan.

## Tujuan

Membuat app Meta for Developers, menghubungkannya ke Business Manager Bharata, dan mendapatkan token akses (System User) untuk menarik data performa iklan (spend, conversions, CPA) dari Meta Marketing API — menggantikan pembacaan manual dari dashboard akun pengiklan yang berjalan saat ini.

## Kapan dipakai

Saat memulai implementasi client Meta Ads di `services/integration` (lihat rencana teknis di [[Microservices - Integration Service]] §Meta Ads) — untuk kebutuhan data konversi/CPA skema insentif "ADV Meta" (lihat [[Finance - Incentive]]).

## Prasyarat

- Akun Facebook developer + akses ke **Business Manager** Bharata (business.facebook.com) yang menaungi ad account yang mau ditarik datanya.
- Peran **Admin** di Business Manager (untuk membuat System User & assign ad account).
- Ad Account ID Bharata yang sudah aktif berjalan (`act_{ad_account_id}`).

## Langkah

1. **Buat App** — di `developers.facebook.com` → *My Apps* → *Create App* → pilih tipe **"Business"** (ini yang membuka produk **Marketing API**, bukan tipe app consumer/lainnya).
2. **Hubungkan ke Business Manager** — saat setup app, connect ke Business Manager Bharata yang sudah ada (bukan bikin baru, kecuali belum ada sama sekali).
3. **Buat System User** — di Business Manager → *Business Settings* → *Users* → *System Users* → buat System User baru (mis. `bip-meta-ads-integration`), peran **Admin** atau **Employee** sesuai kebutuhan scope.
4. **Assign ad account & permission** — di System User, assign akses ke ad account Bharata yang relevan, lalu generate token dengan permission minimal: `ads_read` (baca performa/laporan — cukup untuk kebutuhan insentif ADV Meta), tambah `ads_management` hanya bila nanti perlu tulis/kelola campaign, `business_management` untuk kelola aset bisnis.
5. **Generate token System User** — token System User **tidak expired** (beda dari token user biasa yang cuma 60 hari) — ini yang dipakai untuk automasi/cron, bukan token login personal.
6. **App Review — cek dulu apakah perlu**: App Review **HANYA** wajib bila app perlu akses ad account **di luar** Business Manager Bharata sendiri (mis. jadi provider untuk klien lain). Untuk kebutuhan BIP saat ini (cuma ad account internal Bharata), **App Review TIDAK diperlukan** — langsung pakai System User token di atas.
7. **Simpan kredensial ke sistem** — setelah client Meta Ads ada di kode, simpan token mengikuti pola entity `PlatformToken`/`Credential` yang sudah ada (lihat [[Microservices - Integration Service]] §Meta Ads) — bukan mekanisme penyimpanan baru.

## Verifikasi

- Panggil `GET /act_{ad_account_id}/insights?level=campaign&date_preset=last_30d&fields=campaign_name,impressions,clicks,spend,actions,cost_per_action_type` dengan token System User → dapat response 200 berisi data campaign nyata, bukan error permission.
- Cek header response `X-FB-Ads-Insights-Throttle` untuk memastikan pemakaian rate-limit masih di bawah ambang tier akses.
- Token & App Secret tersimpan sebagai env var (bukan hardcoded), sejalan pola `SHOPEE_PARTNER_ID`/`TIKTOK_SHOP_APP_ID` yang sudah ada.

## Bila gagal / Rollback

- **Permission error / ad account tidak kebaca** — pastikan System User memang di-assign ke ad account yang benar di Business Manager (punya token saja tidak otomatis kasih akses ke ad account — harus di-assign eksplisit).
- **Token ditolak** — pastikan pakai token System User (tanpa expiry), bukan token user personal 60 hari yang sudah kedaluwarsa.
- **Kena rate limit** — Meta rate-limit berbasis tier (bukan window fixed seperti Lazada/Shopee); pacing ulang call & baca header `X-FB-Ads-Insights-Throttle` sebelum retry masif. Evaluasi pola circuit-breaker seperti Shopee (lihat §Observability & Ketahanan Shopee di [[Microservices - Integration Service]]) bila makin banyak ad account ditambahkan.
- **Token bocor** — token System User dengan scope `ads_management` bisa dipakai buat belanja iklan; segera revoke dari Business Manager bila diduga bocor, jangan hanya rotate di kode.

## Referensi Eksternal

- [Authorization - Marketing API - Meta for Developers](https://developers.facebook.com/docs/marketing-api/get-started/authorization)
- [Access Tokens for Meta Technologies](https://developers.facebook.com/documentation/facebook-login/guides/access-tokens)
- [Long-Lived Access Tokens - Meta for Developers](https://developers.facebook.com/documentation/facebook-login/guides/access-tokens/get-long-lived)
- [Insights API - Marketing API - Meta for Developers](https://developers.facebook.com/docs/marketing-api/insights/)
- [Rate Limiting - Marketing API - Meta for Developers](https://developers.facebook.com/docs/marketing-api/overview/rate-limiting/)
- [Update to Ads Management Standard Access — Meta for Developers blog](https://developers.meta.com/blog/updates-to-ads-management-standard-access-feature/)

## Dokumen Terkait

- [[Microservices - Integration Service]] — rencana teknis §Meta Ads, pola TikTok Business/Ads sebagai acuan
- [[Sales - Marketplace Integration]] — dokumen konsolidasi (Meta Ads dicatat di sini atas keputusan tim, meski bukan channel order/marketplace)
- [[Finance - Incentive]] — skema insentif "ADV Meta" yang jadi konsumen data konversi/CPA ini
- [[LOG - Shopee API Rate Limit Request]] — preseden mitigasi rate-limit vendor ads/marketplace
