# TikTok Shop Partner API

Konteks integrasi TikTok Shop. Base: **`https://open-api.tiktokglobalshop.com`**.

> **Beda mendasar dari Shopee Open API v2** (`API Reference/Shopee Open API v2/`): Shopee punya backend doc JSON publik tanpa auth
> (`open.shopee.com/opservice/api/v1/doc/...`) yang bisa di-fetch skrip. **TikTok TIDAK.** Portal
> dok `partner.tiktokshop.com/docv2` adalah SPA — HTML-nya cuma shell (~1,2 MB), isi API dimuat via
> JS setelah load, jadi WebFetch/curl hanya dapat layar kosong. Konsekuensinya alur pakainya beda
> (lihat di bawah): tak ada auto-fetch, sumber utamanya **kode kita sendiri**.

## Isi folder

| File | Isi |
|---|---|
| `Index.md` | daftar endpoint yang RELEVAN untuk ERP, di-seed dari path yang benar-benar dipanggil kode `bip-erp/services/integration` (verified-by-usage) + struktur modul |
| `Endpoints/` | cache detail parameter per endpoint, diisi bertahap (`<module>.<endpoint>.md`) |

## Alur saat butuh endpoint (urut prioritas)

1. **Cek `Endpoints/` & `Index.md` dulu.** Kalau sudah ada, pakai.
2. **Grep kode integration** — sumber PALING grounded (path yang dipakai = verified-by-usage):
   ```
   grep -rhoE '/[a-z_]+/20[0-9]{4}/[a-zA-Z0-9/_%{}.+-]+' bip-erp/services/integration/internal/ --include=*.go | sort -u
   ```
   Struct request/response TikTok ada di `internal/infrastructure/clients/tiktok*.go` &
   `internal/domain/entity/tiktokshop.go` — nama field JSON di tag `json:"..."` (grounded).
3. **WebSearch** nama endpoint + "TikTok Shop API" → dok resmi / mirror pihak ketiga untuk
   field yang belum ada di kode. Halaman resmi SPA, tapi search engine sudah meng-crawl isinya
   dan banyak SDK pihak ketiga mendokumentasikannya.
4. **Minta user paste** dari browser (dia login ke Partner Center) — fallback terakhir.

**Jangan mengarang nama field.** Kalau tak terverifikasi dari kode/dok/paste, bilang jujur.

## Auth & sign (grounded — `internal/infrastructure/clients/tiktok_client.go`)

- **Query params wajib**: `app_key`, `timestamp` (unix detik), `shop_cipher` (per shop), `sign`.
- **Header**: `x-tts-access-token: <access_token>`, `Content-Type: application/json`.
- **Kredensial**: `app_key`/`app_secret` (env, per app), `access_token` + `shop_cipher` (per shop).
- **Algoritma `sign`** (`generateSign`, HMAC-SHA256):
  1. Ambil semua query param KECUALI `sign` & `access_token`.
  2. Urutkan key secara alfabet.
  3. Gabung `key+value` berurutan → `paramStr`.
  4. `msg = app_secret + path + paramStr + body + app_secret`.
  5. `sign = hex( HMAC_SHA256(key=app_secret, msg) )`.

> Versi path **tidak seragam** — tiap modul punya versi tanggalnya sendiri (`202309`, `202410`,
> `202509`, `202602`, `202605`). Jangan menebak versi; ambil dari kode. Contoh nyata: return
> search = `202602`, BUKAN `202309`.

## Dokumen Terkait

- [[Microservices - Integration Service]] — konsumen; jalur order/retur/fulfillment TikTok.
- [[API - Integration Service]] — endpoint internal yang membungkus panggilan ini.
