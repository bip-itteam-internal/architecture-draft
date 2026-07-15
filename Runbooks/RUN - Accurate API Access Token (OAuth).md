> **Status:** ✅ Terverifikasi end-to-end (akun trial, 2026-07-14) — code ditukar jadi access token, `db-list.do`/`open-db.do` jalan, dan `GetItemStock` lewat **client asli** mengembalikan stok nyata. Semua endpoint (`oauth/token`, `db-list.do`, `open-db.do`, data `/accurate/api/...`) teruji; cocokkan hanya daftar **scope** ke app-mu.
>
> **Penting — model token:** access_token OAuth Accurate berformat **UUID** (mis. `9748cd77-…`), **BUKAN** `aat.…`. Token OAuth **butuh session** (`open-db.do` → header `X-Session-ID`); client kita menanganinya **otomatis** bila `ACCURATE_DB_ID` diisi (lihat *§Mode token*). Token **API Token `aat.…`** (DB-bound) bebas-session → kosongkan `ACCURATE_DB_ID`.

> **Jalur UTAMA (2026-07-14): Connect via UI.** Untuk operasi rutin gunakan tombol **Connect** di [[APP - Web ERP]] tab `integration/oauth` (token disimpan di DB + auto-refresh; lihat [[ADR - 0014 Accurate Token DB-backed via OAuth]]). Prosedur `curl` manual di bawah = **fallback/darurat** & untuk memahami mekaniknya (tetap dipakai bila UI belum tersedia / redirect_uri belum didaftarkan).

## Tujuan

Mendapatkan **access token** Accurate (via OAuth 2.0 Authorization Code) dan mengisinya ke `.env` `services/integration`, supaya auto-sync Sales Invoice / Sales Return ([[Microservices - Integration Service]]) bisa memanggil API Accurate. Token ditempel **manual** ke env sekali (tak ada callback OAuth Accurate di kode, beda dari TikTok/Shopee yang punya `auth/callback`), lalu di-refresh saat kedaluwarsa; **session** ditangani **otomatis** oleh client bila `ACCURATE_DB_ID` diisi.

## Kapan dipakai

- Setup awal integrasi Accurate untuk lingkungan baru (dev/trial/prod).
- Token lama kedaluwarsa/dicabut → ambil ulang (atau pakai refresh token, lihat *§Refresh*).

## Prasyarat

Dari registrasi aplikasi di Accurate (`account.accurate.id`), siapkan nilai berikut — **3 masuk `.env`**:

| Nilai | Fungsi | Masuk `.env`? |
|---|---|---|
| **Signature Secret** | tanda-tangan HMAC tiap request | ✅ `ACCURATE_SECRET_KEY` |
| **access token** (UUID dari OAuth, atau `aat.…` API Token) | Bearer auth tiap request | ✅ `ACCURATE_BEARER_TOKEN` |
| **Host+base path data** (dari `open-db.do`) | base URL API — **WAJIB berakhiran `/accurate`** | ✅ `ACCURATE_ACCOUNT_URL` (mis. `https://zeus.accurate.id/accurate`) |
| **DB id** (dari `db-list.do`) | pilih database utk session (mode OAuth) | ✅ `ACCURATE_DB_ID` (kosong = mode API Token `aat.…`) |
| **Client ID** + **Client Secret** | identitas app **saat menukar code → token** | ❌ (hanya transit; jangan simpan di env service) |

- **Redirect URI** yang didaftarkan di app **harus sama persis** di semua langkah. Untuk BIP dev: `https://api-dev.bharatainternasional.com`.
- Scope yang dicentang di app mencakup kebutuhan fitur: minimal `item_view`, `sales_invoice_view`, `sales_invoice_save`, `item_adjustment_save` (tambah `sales_invoice_delete`/lainnya bila perlu). Sales Return memakai scope faktur/retur sesuai daftar scope app-mu.

> Cara kode meng-auth (grounded, `accurate_client.go`): tiap request mengirim `Authorization: Bearer <ACCURATE_BEARER_TOKEN>`, `X-Api-Timestamp: <unix detik>`, dan `X-Api-Signature: hex(HMAC-SHA256(timestamp, ACCURATE_SECRET_KEY))`. Rate limit dijaga 6 rps / 6 paralel.

> **Mode token** (`accurate_client.go`, `WithDatabaseSession`): bila `ACCURATE_DB_ID` diisi → client memanggil `open-db.do` (ambil `session`, di-cache) lalu mengirim `X-Session-ID` tiap call data; session kadaluarsa (`"Parameter session harus diisi"`) → buka ulang & retry sekali. Kosong → mode API Token (`aat.…`, tanpa session) = perilaku prod. `ACCURATE_ACCOUNT_URL` **wajib** berakhiran `/accurate` (client menyusun `<url>/api/...`; tanpa `/accurate` → server balas HTML → error unmarshal).

## Langkah

### 1. Dapatkan authorization `code` (butuh browser)

Buka URL ini di browser (isi `CLIENT_ID` + scope sesuai app), login akun Accurate trial, lalu **Setujui**:

```
https://account.accurate.id/oauth/authorize?client_id=357d8129-bf6e-4827-9e2b-9d914060ea53&response_type=code&redirect_uri=https://api-dev.bharatainternasional.com&scope=item_view%20sales_invoice_view%20sales_invoice_save%20item_adjustment_save
```

Setelah setuju, browser diarahkan ke `https://api-dev.bharatainternasional.com/?code=XXXXXXXX...`. **Salin nilai `code`** dari address bar.

> ⚠️ `code` **sekali-pakai & berumur pendek** (± beberapa menit). Segera lanjut ke langkah 2. Kalau telat → ulangi langkah 1 (dapat `code` baru).

### 2. Tukar `code` → access token

```bash
curl -s -X POST "https://account.accurate.id/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "<CLIENT_ID>:<CLIENT_SECRET>" \
  -d "grant_type=authorization_code" \
  -d "code=<CODE_DARI_LANGKAH_1>" \
  -d "redirect_uri=https://api-dev.bharatainternasional.com"
```

Respons (JSON):
```json
{ "access_token": "aat.xxxxxxxx...", "token_type": "bearer",
  "expires_in": 86400, "refresh_token": "atr.yyyy...", "scope": "item_view ..." }
```
Simpan **`access_token`** (UUID) dan **`refresh_token`** (untuk perpanjang nanti). Jangan commit ke git.

### 3. Temukan `id` + host database (`db-list.do` → `open-db.do`)

Panggil `db-list.do` (butuh signature HMAC) untuk dapat **`id`** database:

```bash
TS=$(date +%s)
SIG=$(printf "%s" "$TS" | openssl dgst -sha256 -hmac "<SIGNATURE_SECRET>" | awk '{print $NF}')
curl -s "https://account.accurate.id/api/db-list.do" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" -H "X-Api-Timestamp: $TS" -H "X-Api-Signature: $SIG"
# → {"s":true,"d":[{"alias":"PT BIP Trial 21","id":2757525,...}]}
```

Lalu `open-db.do?id=<id>` untuk konfirmasi **`host`** (dan bukti session model):

```bash
TS=$(date +%s); SIG=$(printf "%s" "$TS" | openssl dgst -sha256 -hmac "<SIGNATURE_SECRET>" | awk '{print $NF}')
curl -s "https://account.accurate.id/api/open-db.do?id=2757525" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" -H "X-Api-Timestamp: $TS" -H "X-Api-Signature: $SIG"
# → {"s":true,"session":"...","host":"https://zeus.accurate.id",...}
```
Trial BIP: `id=2757525`, `host=https://zeus.accurate.id`. **`ACCURATE_ACCOUNT_URL` = host + `/accurate`** (client menyusun `<url>/api/...`; tanpa `/accurate` server balas HTML → error unmarshal). `id` → `ACCURATE_DB_ID`.

### 4. Isi `.env` `services/integration`

```
ACCURATE_ACCOUNT_URL=https://zeus.accurate.id/accurate
ACCURATE_SECRET_KEY=<SIGNATURE_SECRET>
ACCURATE_BEARER_TOKEN=<ACCESS_TOKEN UUID>
ACCURATE_DB_ID=2757525
```
`.env` **gitignored** — jangan pindah nilai asli ke `.env.example` (itu placeholder committed). `ACCURATE_DB_ID` diisi → client otomatis `open-db.do` + kirim `X-Session-ID` (mode OAuth). Untuk prod pakai token `aat.…`: **kosongkan** `ACCURATE_DB_ID`.

## Verifikasi

- **Terbukti 2026-07-14** (trial): `GetItemStock` lewat `AccurateClient` (mode session, dari env) → `Found=true Stock=9.6435` utk item `BBK-110`. Auth + session + base path `/accurate` benar.
- Cek cepat manual: `db-list.do` (langkah 3) → **HTTP 200** & database muncul = Bearer + signature benar; call data (`item/list.do`/`get-stock.do`) tanpa `X-Session-ID` → `401 "Parameter session harus diisi"`, dengan session → 200.
- Pastikan tak ada secret ter-hardcode; semua dari env (sejalan pola `SHOPEE_PARTNER_ID`/`TIKTOK_SHOP_APP_ID`).

## Refresh (saat token kedaluwarsa)

```bash
curl -s -X POST "https://account.accurate.id/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "<CLIENT_ID>:<CLIENT_SECRET>" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=<REFRESH_TOKEN>"
```
Ganti `ACCURATE_BEARER_TOKEN` dengan `access_token` baru.

## Bila gagal / Rollback

- **`invalid_grant` saat tukar token** — `code` sudah dipakai/kedaluwarsa **atau** `redirect_uri` tak sama persis dengan langkah 1 & registrasi app. Ambil `code` baru + samakan redirect URI (harus `https://api-dev.bharatainternasional.com`, tanpa trailing slash beda).
- **`invalid_client`** — Client ID/Secret salah atau cara auth (Basic `-u` vs form) tak sesuai app. Cek dokumen Accurate untuk metode auth klien.
- **`401` di call API (bukan token)** — signature salah: `ACCURATE_SECRET_KEY` ≠ Signature Secret app, atau jam server jauh melenceng (timestamp). Sinkronkan waktu; pastikan secret benar.
- **200 tapi database salah / kosong** — `ACCURATE_ACCOUNT_URL` bukan host DB trial. Set dari `db-list.do` (langkah 3).
- **Token bocor** — cabut/rotate dari `account.accurate.id`, ganti env; jangan hanya hapus di kode.

## Referensi Eksternal

- Portal aplikasi & OAuth Accurate: `https://account.accurate.id`
- Schema OpenAPI Accurate: `https://account.accurate.id/open-api/json.do` (lihat [[External - Accurate]])

## Dokumen Terkait

- [[Microservices - Integration Service]] — konsumen token (Auto-Sync Faktur & Retur)
- [[External - Accurate]] — kontrak API, host, signing
- [[ADR - 0001 Akuntansi via Accurate]] — keputusan integrasi Accurate
- [[ADR - 0013 Retur via Sales Return per Mode + Keep Invoice Line]] — fitur retur yang butuh token ini
