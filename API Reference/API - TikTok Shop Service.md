## Deskripsi

*Endpoint **tiktok-shop-service** (landing callback & webhook TikTok Shop; menyimpan event + forward ke integration). Gateway: `/api/tiktok-shop/*`; publik via `/ext/tiktok-shop/*`. Grounded ke `services/tiktok-shop-service/main.go`.*

- **Implementasi**: [[Microservices - TikTok Shop Service]] · **Status**: ✅
- **Indeks**: [[API - Index]]

## Endpoint
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/health` | Health check | publik (sebelum middleware) |
| GET | `/callback` | OAuth callback otorisasi TikTok Shop | publik |
| POST | `/webhook` | Webhook TikTok Shop — simpan event, forward ke integration | publik; HMAC-SHA256 `TikTok-Signature` bila `TIKTOK_SHOP_APP_SECRET` di-set |

> Juga tersedia publik via gateway: `/ext/tiktok-shop/callback` & `/ext/tiktok-shop/webhook`.

## Dokumen Terkait
- [[Microservices - TikTok Shop Service]] · [[Microservices - Integration Service]] · [[Sales - Marketplace Integration]] · [[API - Index]]
