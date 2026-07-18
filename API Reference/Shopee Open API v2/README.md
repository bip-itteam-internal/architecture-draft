# Shopee Open API v2

Konteks integrasi Shopee. Digenerate 2026-07-18, 367 endpoint / 15 modul.

## Isi folder

| File | Isi |
|---|---|
| `Index.md` | daftar 367 endpoint: method, path, doc URL |
| `Endpoints/` | cache detail parameter per endpoint, diisi bertahap |
| `Tools/refresh.py` | regenerate `Index.md` dari SDK upstream |
| `Tools/fetch_endpoints.py` | tarik detail endpoint dari **backend doc resmi Shopee** → tulis `Endpoints/*.md` (`verified-docs`) |

Penamaan file di `Endpoints/`: `order.get_order_list.md`

## Alur saat butuh endpoint baru

1. Cek `Endpoints/` dulu. Kalau sudah ada, pakai — jangan fetch ulang.
2. Cari endpoint yang cocok di `Index.md`. Baca selektif (grep), file ini besar.
3. Ambil detail parameter, urut prioritas:
   - **Backend doc resmi Shopee (PRIMARY, `verified-docs`).** URL halaman
     `open.shopee.com/documents/v2/...` itu SPA Nuxt — WebFetch/curl HTML-nya cuma
     dapat layar loading. Tapi datanya tersedia lewat JSON backend (lihat bagian
     **Backend doc API** di bawah). Jalankan `Tools/fetch_endpoints.py` untuk 1 modul
     atau `--all`. Ini yang mengisi mayoritas `Endpoints/` saat ini.
   - SDK upstream (fallback, sumber `Index.md`):
     `raw.githubusercontent.com/QuoVadis86/shopee-sdk/main/<modul>.go` — struct request
     dan response lengkap dengan tag `json:"..."`.
     Alternatif TypeScript: `congminh1254/shopee-sdk`, folder `src/schemas/`.
   - Minta user paste dokumentasi dari browser (dia sudah login).
4. Tulis hasilnya ke `Endpoints/` pakai template di bawah (atau biarkan
   `fetch_endpoints.py` yang menulis).
5. Baru tulis kode.

Kalau semua sumber gagal, bilang parameter belum terverifikasi.
**Jangan mengarang nama field.**

### Backend doc API (sumber `verified-docs`)

Base: `https://open.shopee.com/opservice/api/v1` — tanpa auth, tanpa login.

| Endpoint | Fungsi |
|---|---|
| `GET /doc/version_flag` | versi aktif (`show_version`, saat ini 2) |
| `GET /doc/module/?version=2` | daftar module + item (`name` = api_name, `type=1` = API) |
| `GET /doc/api/?version=2&api_name=<name>` | detail 1 API (JSON lengkap) |

Gotcha yang bikin gagal:
- `api_name` **wajib** ber-prefix versi: `v2.order.get_order_list`, bukan
  `order.get_order_list`. Kalau tidak → `{"error":"error_not_exists"}`.
- Sebagian `name` di module list punya spasi di depan/belakang — `.strip()` dulu.
- HTTP method ada di field **`method`: 2 = GET, 1 = POST** (bukan `is_get_method`,
  itu selalu 0). `define` kadang teks HTML, kadang JSON `{"content": "<html>"}`.

## Template file Endpoints/

```markdown
# {module}.{endpoint}

- Path: `/api/v2/{module}/{endpoint}`
- Method: GET|POST
- Auth: shop | merchant | public
- Sumber: <URL> — <tanggal>
- Confidence: verified-docs | from-sdk | unverified

## Request
| field | tipe | wajib | keterangan |

## Response
| field | tipe | keterangan |

## Catatan
Rate limit, batas rentang waktu, pagination, gotcha.
```

`Confidence` wajib diisi. Cari yang perlu diverifikasi ulang:
`grep -l "from-sdk" Endpoints/`

## Regenerate index

Kalau ada endpoint yang tidak ketemu di `Index.md`:

```
python "API Reference/Shopee Open API v2/Tools/refresh.py"
```

---

## Core context

### Host per region

| Region | Base URL |
|---|---|
| Global (ID/SG/MY/TH/VN/PH/TW) | `https://partner.shopeemobile.com` |
| China | `https://openplatform.shopee.cn` |
| Brazil | `https://openplatform.shopee.com.br` |
| Sandbox global | `https://openplatform.sandbox.test-stable.shopee.sg` |
| Sandbox CN | `https://openplatform.sandbox.test-stable.shopee.cn` |

Indonesia pakai Global.

### Signing (HMAC-SHA256, hex lowercase)

Query wajib: `partner_id`, `timestamp`, `sign`.
Shop API tambah `access_token` + `shop_id`.
Merchant API tambah `access_token` + `merchant_id`.

```
Public   : partner_id + api_path + timestamp
Shop     : partner_id + api_path + timestamp + access_token + shop_id
Merchant : partner_id + api_path + timestamp + access_token + merchant_id
```

`api_path` = path saja, mis. `/api/v2/order/get_order_list`. Tanpa host,
tanpa query string.

```python
import hmac, hashlib, time

def sign(partner_id, partner_key, path, access_token="", shop_id=""):
    ts = int(time.time())
    base = f"{partner_id}{path}{ts}{access_token}{shop_id}".encode()
    return ts, hmac.new(partner_key.encode(), base, hashlib.sha256).hexdigest()
```

### Endpoint auth

Terverifikasi dari dua SDK independen.

| Fungsi | Path |
|---|---|
| Authorization link | `/api/v2/shop/auth_partner` |
| Tukar code → token | `/api/v2/auth/token/get` |
| Refresh access token | `/api/v2/auth/access_token/get` |
| Token via resend code | `/api/v2/auth/get_token_by_resend_code` |

### Gotcha

- `timestamp` dalam **detik**, bukan milidetik. Toleransi drift ±5 menit.
- `access_token` expired **4 jam** (`expire_in: 14400`).
- `refresh_token` expired **30 hari**. Tiap refresh menghasilkan refresh_token
  baru yang harus menimpa yang lama — kalau tidak, otorisasi mati diam-diam.
- Response sukses tetap HTTP 200. Cek field `error` (kosong = sukses),
  jangan cuma status code.
- Rate limit per shop, umumnya ~10 req/detik.
- Endpoint list sering membatasi rentang waktu per request (umumnya 15 hari).
  Query 30 hari harus di-chunk. Verifikasi batas persisnya per endpoint.
- Pagination bisa `cursor` atau `offset`, tergantung endpoint. Jangan diasumsikan.
- URL gambar CDN Shopee kedaluwarsa. Simpan `image_id`, bukan URL.
- Sandbox tidak mendukung semua fitur; banyak yang hanya jalan di production.

### Catatan sumber

`Index.md` diturunkan dari SDK komunitas, bukan dokumentasi resmi Shopee.
Nama endpoint akurat (dipakai di produksi), tapi bisa tertinggal dari
perubahan Shopee. Nama modul mengikuti penamaan SDK dan bisa berbeda dengan
label di portal — kalau doc URL 404, coba variasi nama modul.
