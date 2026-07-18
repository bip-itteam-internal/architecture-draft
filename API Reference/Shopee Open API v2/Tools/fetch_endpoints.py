#!/usr/bin/env python3
"""Fetch Shopee Open API v2 endpoint details from the OFFICIAL docs backend and
write one Markdown file per endpoint into ../Endpoints/.

Sumber data: backend yang dipakai portal open.shopee.com (SPA Nuxt). Halaman HTML-nya
dirender via JS sehingga WebFetch/curl atas URL dokumen hanya dapat layar loading —
tapi datanya tersedia lewat JSON endpoint di bawah ini. Ini lebih otoritatif daripada
community SDK => Confidence: verified-docs.

    GET {BASE}/doc/version_flag                      -> versi aktif
    GET {BASE}/doc/module/?version=2                 -> daftar module + item (nama API)
    GET {BASE}/doc/api/?version=2&api_name=<name>    -> detail 1 API (JSON)

`api_name` = nama item apa adanya dari module list, mis. `v2.order.get_order_list`
(prefix `v2.` PENTING — tanpa itu backend balas "Api does not exist").

Pemakaian:
    python fetch_endpoints.py                     # module default (Order, Logistics, Product, Payment)
    python fetch_endpoints.py Order Returns       # module tertentu (nama sesuai module list)
    python fetch_endpoints.py --all               # semua module type=1
    python fetch_endpoints.py --limit 2 Order     # uji: 2 endpoint pertama saja
"""
import sys, os, re, json, html, time, datetime
from urllib.request import urlopen, Request
from urllib.parse import quote

BASE = "https://open.shopee.com/opservice/api/v1"
VERSION = 2
DEFAULT_MODULES = ["Order", "Logistics", "Product", "Payment"]
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "Endpoints")
TODAY = datetime.date.today().isoformat()
UA = {"User-Agent": "Mozilla/5.0 (docs-sync)"}


def get(url):
    req = Request(url, headers=UA)
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def clean(text):
    """HTML -> teks polos satu baris, aman untuk sel tabel Markdown."""
    if text is None:
        return ""
    s = str(text)
    s = s.replace("<br />", " ").replace("<br/>", " ").replace("<br>", " ")
    s = re.sub(r"<a [^>]*href=\s*([^ >]+)[^>]*>(.*?)</a>", r"\2 (\1)", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = s.replace("|", r"\|").replace("\r", " ").replace("\n", " ").replace("\t", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def http_method(detail):
    """Field `method` di backend: 2 = GET, 1 = POST (terverifikasi lintas endpoint).
    `is_get_method` selalu 0 dan tidak dipakai."""
    return {1: "POST", 2: "GET", 3: "PUT", 4: "DELETE"}.get(detail.get("method"), "GET")


def rich_text(value):
    """`define` kadang teks HTML biasa, kadang JSON rich-text {"content": "<html>", ...}.
    Kembalikan teks polos satu baris."""
    if not value:
        return ""
    v = str(value).strip()
    if v.startswith("{") or v.startswith("["):
        try:
            obj = json.loads(v)
            if isinstance(obj, dict) and "content" in obj:
                return clean(obj["content"])
        except Exception:
            pass
    return clean(v)


AUTH_MAP = {"shop": "shop", "merchant": "merchant", "public": "public"}


def auth_of(detail):
    return AUTH_MAP.get(str(detail.get("api_type", "")).strip().lower(), str(detail.get("api_type", "")).lower() or "shop")


def flatten(params, prefix=""):
    """response_params bertingkat -> baris (path, tipe, keterangan)."""
    rows = []
    for p in params:
        name = p.get("name", "")
        typ = p.get("type", "")
        path = f"{prefix}{name}"
        rows.append((path, typ, clean(p.get("description", ""))))
        if p.get("children"):
            child_prefix = f"{path}[]." if typ.endswith("[]") else f"{path}."
            rows.extend(flatten(p["children"], child_prefix))
    return rows


def render(detail):
    api_name = detail["api_name"].strip()          # v2.order.get_order_list (kadang ada spasi/prefix ganda)
    short = re.sub(r"^(v\d+\.)+", "", api_name)     # order.get_order_list
    path = detail.get("path") or ""
    method = http_method(detail)
    auth = auth_of(detail)
    define = rich_text(detail.get("define", ""))
    try:
        params = json.loads(detail.get("params") or "{}")
    except Exception:
        params = {}
    req = params.get("request_params", []) or []
    resp = params.get("response_params", []) or []

    L = []
    L.append(f"# {short}")
    L.append("")
    L.append(f"- Path: `{path}`")
    L.append(f"- Method: {method}")
    L.append(f"- Auth: {auth}")
    if define:
        L.append(f"- Deskripsi: {define}")
    rl = detail.get("rate_limit")
    L.append(f"- Sumber: open.shopee.com/documents/v2/{short}?type=1 (backend doc/api) — {TODAY}")
    L.append("- Confidence: verified-docs")
    L.append("")
    L.append("## Request")
    L.append("")
    if req:
        L.append("| field | tipe | wajib | keterangan |")
        L.append("|---|---|---|---|")
        for p in req:
            wajib = "ya" if str(p.get("required", "")).lower() in ("true", "1", "yes") else "tidak"
            ket = clean(p.get("description", ""))
            sample = clean(p.get("sample", ""))
            if sample:
                ket = (ket + f" Contoh: `{sample}`").strip()
            L.append(f"| `{p.get('name','')}` | {p.get('type','')} | {wajib} | {ket} |")
    else:
        L.append("_Tidak ada parameter request selain common params._")
    L.append("")
    L.append("## Response")
    L.append("")
    if resp:
        L.append("| field | tipe | keterangan |")
        L.append("|---|---|---|")
        for pth, typ, ket in flatten(resp):
            L.append(f"| `{pth}` | {typ} | {ket} |")
    else:
        L.append("_TBD._")
    L.append("")
    L.append("## Catatan")
    L.append("")
    notes = []
    if rl and rl not in ("[0, 0, 0]", "[0,0,0]", None):
        notes.append(f"- Rate limit (doc): `{rl}`.")
    notes.append("- Common params (`partner_id`, `timestamp`, `access_token`, `shop_id`/`merchant_id`, `sign`) wajib — lihat `../README.md`.")
    notes.append("- Response sukses tetap HTTP 200; cek field `error` (kosong = sukses).")
    L.extend(notes)
    L.append("")
    return short, "\n".join(L)


def write_one(name):
    """Fetch 1 endpoint by api_name (prefix `v2.` opsional), render, tulis file.
    Return (short, None) sukses; (None, pesan_error) kalau tidak ada."""
    name = name.strip()
    if not re.match(r"^v\d+\.", name):
        name = f"v{VERSION}.{name}"
    d = get(f"{BASE}/doc/api/?version={VERSION}&api_name={quote(name)}")
    if d.get("error") or "api_name" not in d:
        return None, d.get("error") or d.get("msg") or "unknown"
    short, md = render(d)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"{short}.md"), "w", encoding="utf-8") as f:
        f.write(md)
    return short, None


def search_endpoints(keywords):
    """Cari endpoint di module list backend: cocok kalau SEMUA kata kunci muncul
    di `<module> <api_name>`. Return list (module, api_name)."""
    kws = [k.lower() for k in keywords]
    mods = get(f"{BASE}/doc/module/?version={VERSION}")["modules"]
    hits = []
    for m in mods:
        if m["type"] != 1:
            continue
        for it in m["items"]:
            if it["type"] != 1:
                continue
            hay = f"{m['module_name']} {it['name']}".lower()
            if all(k in hay for k in kws):
                hits.append((m["module_name"], it["name"].strip()))
    return hits


def main():
    argv = sys.argv[1:]

    # --search kw...  : hanya daftar endpoint yang cocok (tanpa fetch)
    if "--search" in argv:
        kws = argv[argv.index("--search") + 1:]
        hits = search_endpoints(kws)
        print(f"{len(hits)} endpoint cocok untuk {kws}:")
        for mod, name in hits:
            short = re.sub(r"^(v\d+\.)+", "", name)
            print(f"  {mod:<12} {short}")
        return

    # --api name[,name...] : tarik endpoint tertentu (bisa diulang / dipisah koma)
    if "--api" in argv:
        i = argv.index("--api")
        raw = argv[i + 1:]
        names = [n for chunk in raw for n in chunk.split(",") if n.strip()]
        for name in names:
            short, err = write_one(name)
            if err:
                print(f"  GAGAL {name}: {err}")
            else:
                print(f"  OK    {short}  -> Endpoints/{short}.md")
            time.sleep(0.25)
        return

    # mode module (default): --all, --limit N, atau daftar nama module
    limit = None
    if "--limit" in argv:
        i = argv.index("--limit")
        limit = int(argv[i + 1])
        del argv[i:i + 2]
    want_all = "--all" in argv
    argv = [a for a in argv if a != "--all"]
    wanted = argv or DEFAULT_MODULES

    os.makedirs(OUT_DIR, exist_ok=True)
    vf = get(f"{BASE}/doc/version_flag")
    print(f"version_flag: {vf}")
    mods = get(f"{BASE}/doc/module/?version={VERSION}")["modules"]

    targets = []
    for m in mods:
        if m["type"] != 1:
            continue
        if not want_all and m["module_name"] not in wanted:
            continue
        items = [it for it in m["items"] if it["type"] == 1]
        if limit:
            items = items[:limit]
        for it in items:
            targets.append((m["module_name"], it["name"]))

    print(f"Total endpoint: {len(targets)}")
    ok = fail = 0
    for idx, (mod, name) in enumerate(targets, 1):
        try:
            short, err = write_one(name)
            if err:
                print(f"  [{idx}/{len(targets)}] SKIP {name}: {err}")
                fail += 1
            else:
                ok += 1
                print(f"  [{idx}/{len(targets)}] {mod:<10} {short}")
        except Exception as e:
            print(f"  [{idx}/{len(targets)}] ERROR {name}: {e}")
            fail += 1
        time.sleep(0.25)
    print(f"\nSelesai. tulis={ok} gagal={fail} -> {os.path.abspath(OUT_DIR)}")


if __name__ == "__main__":
    main()
