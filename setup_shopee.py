#!/usr/bin/env python3
"""
setup_shopee.py — bikin struktur konteks Shopee Open API v2 di architecture-draft.

Sekali jalan, tanpa dependency eksternal (stdlib saja), tanpa git.
Sumber data: SDK Go `QuoVadis86/shopee-sdk` via raw.githubusercontent.com.

Pakai:
    python setup_shopee.py                 # jalankan dari root repo
    python setup_shopee.py --wikilink      # penamaan "Order - Get Order List.md"
    python setup_shopee.py --refresh       # regenerate Index.md saja, sisanya aman
    python setup_shopee.py --root D:\\repo\\architecture-draft

Idempoten: aman dijalankan berulang. File cache di Endpoints/ tidak pernah ditimpa.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

REPO = "QuoVadis86/shopee-sdk"
BRANCH = "main"
RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/"
API = f"https://api.github.com/repos/{REPO}/contents/?ref={BRANCH}"
DEST = Path("API Reference") / "Shopee Open API v2"
MARK_A = "<!-- shopee-context:start -->"
MARK_B = "<!-- shopee-context:end -->"
TODAY = date.today().isoformat()

CONST_RE = re.compile(r'(Path\w+)\s*=\s*APIPath\("([a-z0-9_]+)",\s*"([a-z0-9_/]+)"\)')
FUNC_RE = re.compile(r"func \(s \*\w+\) (\w+)\(")
USE_RE = re.compile(r"\b(DoGet|DoPost|DoUpload|Do)\(.*?(Path\w+)")
VERB = {"DoGet": "GET", "DoPost": "POST", "DoUpload": "POST", "Do": "GET"}


def get(url, as_json=False):
    req = urllib.request.Request(url, headers={"User-Agent": "shopee-ctx-setup"})
    with urllib.request.urlopen(req, timeout=45) as r:
        raw = r.read().decode("utf-8", "replace")
    return json.loads(raw) if as_json else raw


# File .go yang tidak sama persis dengan nama modul di region.go
EXTRA_FILES = ["whs.go", "live.go", "client.go", "shopee.go", "media_space.go"]


def fetch_sdk():
    print("  region.go ...", end=" ", flush=True)
    region = get(RAW + "region.go")
    print(f"{len(region)//1024} KB")

    # Nama file diturunkan dari nama modul di region.go, bukan dari
    # contents API — API itu kena rate limit kalau tanpa token.
    mods = sorted({m for _, m, _ in CONST_RE.findall(region)})
    names = [f"{m}.go" for m in mods] + EXTRA_FILES

    # Lengkapi dengan contents API kalau kebetulan bisa (bonus, bukan syarat).
    try:
        names += [
            f["name"] for f in get(API, as_json=True)
            if f["name"].endswith(".go") and not f["name"].endswith("_test.go")
        ]
    except Exception:
        pass

    seen, modules, miss = set(), {}, 0
    names = [n for n in names if not (n in seen or seen.add(n))]
    for n in names:
        try:
            modules[n] = get(RAW + n)
        except urllib.error.HTTPError:
            miss += 1
        except Exception:
            miss += 1
    print(f"  {len(modules)} file modul terambil, {miss} tidak ada (wajar)")
    return region, modules


def parse(region, modules):
    consts = {}
    for name, mod, ep in CONST_RE.findall(region):
        consts[name] = {
            "module": mod, "endpoint": ep,
            "path": f"/api/v2/{mod}/{ep}", "method": None,
        }
    for text in modules.values():
        cur = None
        for line in text.splitlines():
            f = FUNC_RE.match(line)
            if f:
                cur = f.group(1)
            u = USE_RE.search(line)
            if u and u.group(2) in consts:
                c = consts[u.group(2)]
                c["method"] = c["method"] or VERB[u.group(1)]
    return consts


def build_index(consts):
    by_mod = defaultdict(list)
    for c in consts.values():
        by_mod[c["module"]].append(c)

    doc = "https://open.shopee.com/documents/v2/{m}.{e}?module=&type=1"
    out = [
        "# Shopee Open API v2 — Endpoint Index", "",
        f"Total **{len(consts)} endpoint** / {len(by_mod)} modul. "
        f"Digenerate {TODAY} dari `{REPO}`.", "",
        "> Index saja. Parameter request/response TIDAK ada di sini —",
        "> lihat `Endpoints/` atau ambil detailnya sesuai alur di README.",
        "> Kolom `method` diturunkan dari SDK, sifatnya indikatif.", "",
        "## Modul", "",
        " · ".join(f"`{m}` ({len(v)})" for m, v in sorted(by_mod.items())), "",
    ]
    for m in sorted(by_mod):
        out += [f"## {m}", "", "| method | path | doc |", "|---|---|---|"]
        for c in sorted(by_mod[m], key=lambda x: x["endpoint"]):
            out.append(
                f"| {c['method'] or '?'} | `{c['path']}` | "
                f"{doc.format(m=c['module'], e=c['endpoint'])} |"
            )
        out.append("")
    return "\n".join(out), by_mod


def readme(by_mod, total, wikilink):
    naming = ("`Order - Get Order List.md`" if wikilink
              else "`order.get_order_list.md`")
    return f"""# Shopee Open API v2

Konteks integrasi Shopee. Digenerate {TODAY}, {total} endpoint / {len(by_mod)} modul.

## Isi folder

| File | Isi |
|---|---|
| `Index.md` | daftar {total} endpoint: method, path, doc URL |
| `Endpoints/` | cache detail parameter per endpoint, diisi bertahap |
| `Tools/refresh.py` | regenerate `Index.md` dari SDK upstream |

Penamaan file di `Endpoints/`: {naming}

## Alur saat butuh endpoint baru

1. Cek `Endpoints/` dulu. Kalau sudah ada, pakai — jangan fetch ulang.
2. Cari endpoint yang cocok di `Index.md`. Baca selektif (grep), file ini besar.
3. Ambil detail parameter, urut prioritas:
   - WebFetch ke doc URL di `Index.md`. **Sering gagal** — open.shopee.com
     merender pakai JS dan memblokir bot (403). Jangan retry berkali-kali.
   - SDK upstream (reliable, ini sumber Index.md):
     `raw.githubusercontent.com/{REPO}/{BRANCH}/<modul>.go` — struct request
     dan response lengkap dengan tag `json:"..."`.
     Alternatif TypeScript: `congminh1254/shopee-sdk`, folder `src/schemas/`.
   - Minta user paste dokumentasi dari browser (dia sudah login, tidak kena blokir).
4. Tulis hasilnya ke `Endpoints/` pakai template di bawah.
5. Baru tulis kode.

Kalau ketiga sumber gagal, bilang parameter belum terverifikasi.
**Jangan mengarang nama field.**

## Template file Endpoints/

```markdown
# {{module}}.{{endpoint}}

- Path: `/api/v2/{{module}}/{{endpoint}}`
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
    base = f"{{partner_id}}{{path}}{{ts}}{{access_token}}{{shop_id}}".encode()
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
"""


SEED = """# order.get_order_list

- Path: `/api/v2/order/get_order_list`
- Method: GET
- Auth: shop
- Sumber: github.com/QuoVadis86/shopee-sdk `order.go` — {today}
- Confidence: from-sdk

## Request

| field | tipe | wajib | keterangan |
|---|---|---|---|
| `time_range_field` | string | ya | `create_time` atau `update_time` |
| `time_from` | int64 | ya | unix detik |
| `time_to` | int64 | ya | unix detik. Rentang dibatasi — chunk kalau lebih |
| `page_size` | int | ya | entri per halaman |
| `cursor` | string | tidak | kosongkan di request pertama |
| `order_status` | string | tidak | filter status |

## Response

| field | tipe | keterangan |
|---|---|---|
| `response.order_list[].order_sn` | string | nomor pesanan |
| `response.order_list[].order_status` | string | status |
| `response.more` | bool | masih ada halaman berikutnya |
| `response.next_cursor` | string | jadi `cursor` request berikutnya |
| `error` | string | kosong = sukses |
| `message` | string | pesan error |
| `request_id` | string | untuk debugging ke Shopee |

## Catatan

- Hanya mengembalikan `order_sn` + status. Detail lengkap lewat
  `order.get_order_detail` dengan `order_sn_list` (comma-separated) dan
  `response_optional_fields`.
- Pagination pakai `cursor`, bukan offset. Loop selama `more == true`.
- Batas persis rentang waktu dan `page_size` maksimum belum diverifikasi
  dari dokumentasi resmi. Konfirmasi sebelum dipakai di produksi.
""".format(today=TODAY)


POINTER = f"""{MARK_A}
## Integrasi eksternal

Konteks integrasi disimpan per folder dan dibaca **hanya saat relevan**.
Jangan load isinya kalau task tidak menyentuh integrasi tersebut.

| Integrasi | Folder | Baca kapan |
|---|---|---|
| Shopee Open API v2 | `API Reference/Shopee Open API v2/` | task menyentuh Shopee: order, produk, stok, logistik, iklan |

Saat relevan, baca `README.md` di folder tersebut lebih dulu — di situ ada
alur wajib, termasuk cara memperbarui dokumentasinya sendiri.
{MARK_B}"""


REFRESH = '''#!/usr/bin/env python3
"""Regenerate Index.md dari SDK upstream. Tidak menyentuh Endpoints/."""
import subprocess, sys
from pathlib import Path

setup = Path(__file__).resolve().parents[3] / "setup_shopee.py"
if not setup.exists():
    sys.exit(f"setup_shopee.py tidak ditemukan di {setup}")
sys.exit(subprocess.call([sys.executable, str(setup), "--refresh"],
                         cwd=str(setup.parent)))
'''


def write(path, text, force=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        print(f"  = {path}  (sudah ada, dilewati)")
        return False
    path.write_text(text, encoding="utf-8")
    print(f"  {'~' if force else '+'} {path}")
    return True


def patch_claude_md(root):
    f = root / "CLAUDE.md"
    if not f.exists():
        write(f, "# CLAUDE.md\n\n" + POINTER + "\n")
        return
    text = f.read_text(encoding="utf-8")
    if MARK_A in text:
        new = re.sub(re.escape(MARK_A) + r".*?" + re.escape(MARK_B),
                     POINTER, text, flags=re.S)
        if new != text:
            f.write_text(new, encoding="utf-8")
            print("  ~ CLAUDE.md  (section diperbarui)")
        else:
            print("  = CLAUDE.md  (section sudah sesuai)")
        return
    sep = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
    f.write_text(text + sep + POINTER + "\n", encoding="utf-8")
    print("  + CLAUDE.md  (section ditambahkan di akhir)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--wikilink", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    if not root.is_dir():
        sys.exit(f"Folder tidak ada: {root}")
    base = root / DEST

    print(f"Target: {base}\n")
    print("Ambil SDK dari GitHub:")
    try:
        region, modules = fetch_sdk()
    except urllib.error.URLError as e:
        sys.exit(f"\nGagal akses GitHub: {e}\nCek koneksi / proxy / firewall.")

    consts = parse(region, modules)
    if not consts:
        sys.exit("Tidak ada endpoint terparsing. Struktur SDK mungkin berubah.")
    index, by_mod = build_index(consts)
    known = sum(1 for c in consts.values() if c["method"])
    print(f"\n{len(consts)} endpoint, {len(by_mod)} modul, "
          f"method terdeteksi {known}/{len(consts)}\n")

    print("Tulis file:")
    write(base / "Index.md", index, force=True)

    if a.refresh:
        print("\nMode --refresh: hanya Index.md yang diperbarui.")
        return

    write(base / "README.md", readme(by_mod, len(consts), a.wikilink))
    seed = ("Order - Get Order List.md" if a.wikilink
            else "order.get_order_list.md")
    write(base / "Endpoints" / seed, SEED)
    write(base / "Tools" / "refresh.py", REFRESH, force=True)
    patch_claude_md(root)

    print(f"\nSelesai. Cek: {base}")
    print("Endpoints/ tidak pernah ditimpa saat script dijalankan ulang.")


if __name__ == "__main__":
    main()
