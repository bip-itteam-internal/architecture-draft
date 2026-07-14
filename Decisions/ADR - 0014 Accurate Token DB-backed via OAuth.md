# ADR - 0014 Accurate Token DB-backed via OAuth + WithTokenSource

Status: ⚠️ Implemented (ada catatan) — kode + tes selesai 2026-07-14; belum di-commit & alur connect UI belum di-smoke-test end-to-end (butuh redirect_uri FE didaftarkan).

## Context

Token Accurate sebelumnya **hanya dari env** (`ACCURATE_BEARER_TOKEN`), ditempel manual (lihat [[RUN - Accurate API Access Token (OAuth)]]). Access_token OAuth Accurate berformat UUID & **kedaluwarsa ±15 hari** (punya refresh_token) → menempel/refresh manual tiap 15 hari tak berkelanjutan untuk operasi rutin. Pola OAuth marketplace ([[Microservices - Integration Service]]: Shopee/TikTok) sudah menyimpan kredensial di DB + refresh on-demand — Accurate belum.

## Decision

Bangun fitur **connect Accurate via UI** (setara marketplace), token dikelola di DB & dipakai service otomatis:

- **Storage**: koleksi `accurate_credentials` (single doc `_id="default"` — satu perusahaan Accurate; token **AES-encrypted** via `internal/crypto`) + `accurate_oauth_states` (nonce CSRF sekali-pakai, TTL index).
- **Endpoint** grup `/accurate` (admin-only `RequireIntegrationAdmin`): `GET /auth` (authorize URL + state), `POST /auth/callback` (tukar `code`→token **server-side**, `client_secret` env; `db-list.do`/`open-db.do` pilih database → simpan), `GET /connection` (status ter-mask), `POST /disconnect`.
- **Client wiring**: `AccurateClient.WithTokenSource(fn)` — tiap request resolusi `(token, dbID)` dari usecase: kredensial DB → **refresh** near-expiry (mutex, buffer 5 mnt) → **fallback env** (`ACCURATE_BEARER_TOKEN`+`ACCURATE_DB_ID`) bila belum connect **atau** DB error transient. Mode statis `WithDatabaseSession` (API Token aat) tetap ada untuk tes/kompat.
- **FE**: tab "Accurate" di `integration/oauth` (kartu status tunggal Connect/Reconnect/Disconnect), redirect ke FE (mirror marketplace) → relay `code`+`state` ke callback.

## Consequences

- ✅ Token Accurate **self-service dari UI + auto-refresh** — tak perlu redeploy / tempel `.env` tiap 15 hari.
- ✅ **Prod aman**: fallback env → perilaku lama sampai admin klik Connect; blip DB → fallback (bukan menghentikan sync Accurate).
- ✅ Rahasia (`client_secret`, Signature Secret) **tetap server-side**; token **encrypted** at rest; **admin-only** + `state` CSRF; `/connection` tak balikin token mentah.
- ⚠️ **Ops**: `ACCURATE_REDIRECT_URI` (app Accurate) harus = URL FE `…/integration/oauth` (kini terdaftar root `api-dev.bharatainternasional.com`).
- ⚠️ **Single-host**: `baseURL` data tetap dari `ACCURATE_ACCOUNT_URL` (bukan host koneksi) — asumsi satu database Accurate. Multi-DB = di luar scope.
- ⚠️ Refresh token dicabut/gagal → perlu **Reconnect** via UI.
- Menggantikan jalur manual di [[RUN - Accurate API Access Token (OAuth)]] untuk operasi rutin (manual = fallback/darurat).

## Dokumen Terkait

- [[Microservices - Integration Service]]
- [[ADR - 0001 Akuntansi via Accurate]]
- [[RUN - Accurate API Access Token (OAuth)]]
