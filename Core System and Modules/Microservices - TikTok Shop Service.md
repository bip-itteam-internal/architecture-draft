# Microservices - TikTok Shop Service

## Deskripsi

_TikTok Shop Service adalah penerima minimal untuk **OAuth callback + webhook TikTok Shop**. Service ini hanya menangkap dan menyimpan event dari TikTok; **tidak ada business logic** di dalamnya._

- **Stack:** Go + Fiber v2 + MongoDB
- **Path:** `services/tiktok-shop-service`
- **Status:** 🔴 Stub / skeleton (paling belum berkembang)

## Endpoint / Fitur (Sudah Diimplementasikan)

- **Health check:** `GET /health`
- **OAuth callback:** `GET /callback` — membutuhkan query `?code`; menyimpan `{code, state, created_at}` ke collection `tiktok_shop_callbacks`
- **Webhook:** `POST /webhook` — verifikasi HMAC-SHA256 saat `TiktokShopAppSecret` di-set (format header `t=<ts>,s=<sig>`); menyimpan payload mentah ke collection `tiktok_shop_webhooks`

## Belum Diimplementasikan / Catatan

- Pada dasarnya hanya **skeleton ingestion**. TIDAK ada:
  - TikTok API client
  - Token exchange — `code` hanya disimpan, tidak ditukar menjadi access token
  - Sync order / produk
  - Pemrosesan (processing) event webhook
  - Endpoint baca / query
- `InternalURL` kosong.
- Verifikasi signature **dilewati** jika secret tidak di-set.
- **Logika marketplace yang sebenarnya berada di integration-service** — lihat [[Microservices - Integration Service]].

## Dependencies & Integrasi

- **MongoDB** — collection: `tiktok_shop_callbacks`, `tiktok_shop_webhooks`.
- **Inbound** dari TikTok Shop (callback + webhook); tidak ada outbound call ke service lain.
- Logika marketplace yang sesungguhnya — lihat [[Microservices - Integration Service]].
- Diekspos via gateway — lihat [[CORE - API Master Gateway]].
- Skema database — lihat [[DB - Overview and Notes]].

## Dokumen Terkait

- [[Sales - GMV Creative]]
