#!/usr/bin/env python3
"""layar-lib.py — keputusan DETERMINISTIK judge desain (gerbang tinjau layar erp-frontend).

Semua keputusan yang tidak butuh penilaian ada di sini, bukan di prompt agen: agen yang diminta
"tentukan sendiri apakah tangkapan ini gagal" akan menjawab berbeda tiap run. Yang dijaga adalah
kegagalan yang SENYAP:

- **Tangkapan gagal bukan layar bersih.** Ringkasan tanpa satu pun rute yang berhasil ditangkap
  (semua `/login`, 404, atau galat alat) harus terbaca `layar_dinilai: false`. Kalau dibaca "tidak
  ada temuan", gerbang lolos tanpa melihat satu layar pun.
- **Mendarat di /login atau 404 adalah masalah tangkapan, bukan galat kode.** Menuduh eksekutor atas
  sesi palsu atau rute manifest yang keliru membuat loop berputar tanpa sebab.
- **Error boundary selalu galat kode** (diubah 2026-10-18), kecuali `galat` alat atau /login yang
  menang lebih dulu. Syarat lama "konsol menunjuk berkas diff" tak pernah terpenuhi atas build
  produksi tanpa source map. Parameter `berkas_diff` dipertahankan demi kompatibilitas tanda
  tangan (`klasifikasi_rute`, `layar_dinilai`, CLI `ringkas`) tetapi tidak lagi memutus apa pun.
- **Bantahan atas temuan yang tak pernah ada tidak dihitung salah tuduh.** Ia diabaikan dan dicatat.

Manifest layar (skema di spec 2026-10-18-judge-desain-design.md) wajib sah sebelum skrip tangkapan
berjalan: peran dalam cookie bernilai string per modul, stub tak pernah 401 (401 melempar tangkapan
ke /login), dan keadaan `berisi` + `kosong` selalu ada.

CLI:
  python layar-lib.py perlu --repo <r> --berkas-dari <txt>
  python layar-lib.py validasi <manifest.json>        (exit 0 sah, 1 ada galat)
  python layar-lib.py ringkas <ringkasan.json> --berkas-dari <txt>   -> {rute, layar_dinilai, galat}
  python layar-lib.py salah-tuduh --sebelum <verdict desain n-1> --berikut <verdict desain n> --bantahan <json>
"""
import argparse
import json
import re
import sys

sys.dont_write_bytecode = True

REPO_FRONTEND = "erp-frontend"
FOLDER_LAYAR = ("src/app/", "src/features/", "src/components/")
KEADAAN_WAJIB = ("berisi", "kosong")


def _norm(p):
    return str(p).replace("\\", "/")


def berkas_layar(berkas):
    """Berkas `.tsx` UI di bawah src/app, src/features, src/components; tanpa test."""
    hasil = []
    for b in berkas:
        p = _norm(b)
        if not p.endswith(".tsx"):
            continue
        if p.endswith(".test.tsx") or p.endswith(".spec.tsx") or "/__tests__/" in "/" + p:
            continue
        if not p.startswith(FOLDER_LAYAR):
            continue
        hasil.append(p)
    return hasil


def perlu_judge_desain(repo, berkas):
    return repo == REPO_FRONTEND and bool(berkas_layar(berkas))


def validasi_manifest(obj):
    """Daftar galat manifest; kosong = sah."""
    if not isinstance(obj, dict):
        return ["manifest bukan objek JSON"]
    galat = []
    rute = obj.get("rute")
    stub = obj.get("stub")
    if not isinstance(stub, dict):
        stub = {}
        galat.append("stub tidak ada atau bukan objek")
    if not isinstance(rute, list) or not rute:
        galat.append("rute kosong atau tidak ada")
        rute = []
    for i, r in enumerate(rute):
        path = r.get("path") if isinstance(r, dict) else None
        if not isinstance(path, str) or not path.startswith("/"):
            galat.append("rute[%d].path harus diawali '/'" % i)
        for k in (r.get("keadaan") or []) if isinstance(r, dict) else []:
            if k not in stub:
                galat.append("rute[%d] merujuk keadaan '%s' yang tidak ada di stub" % (i, k))
    cookie = obj.get("cookie") or {}
    roles = cookie.get("system_roles", {}) if isinstance(cookie, dict) else {}
    if not isinstance(roles, dict):
        galat.append("cookie.system_roles harus objek modul -> string")
    else:
        for modul, nilai in roles.items():
            if not isinstance(nilai, str):
                galat.append("cookie.system_roles['%s'] harus string, bukan %s" % (modul, type(nilai).__name__))
    for wajib in KEADAAN_WAJIB:
        if wajib not in stub:
            galat.append("stub tidak punya keadaan '%s'" % wajib)
    for nama, daftar in stub.items():
        for j, s in enumerate(daftar if isinstance(daftar, list) else []):
            if isinstance(s, dict) and s.get("status") == 401:
                galat.append("stub['%s'][%d] berstatus 401 (melempar sesi ke /login)" % (nama, j))
    return galat


def klasifikasi_rute(hasil, berkas_diff):
    """'ok' | 'tangkapan_gagal' | 'galat_kode' untuk satu entri rute dari ringkasan.json.

    Urutan menang: galat alat, lalu /login, lalu error boundary (galat_kode), lalu status >= 400.
    `berkas_diff` dipertahankan demi kompatibilitas tanda tangan; tidak memutus keputusan apa pun.
    """
    if hasil.get("galat"):
        return "tangkapan_gagal"
    akhir = hasil.get("rute_akhir") or ""
    if re.match(r"^/login(?:[/?#]|$)", akhir):
        return "tangkapan_gagal"
    # Boundary = galat kode APA PUN isi konsol dan status dokumennya (diubah 2026-10-18). Build
    # produksi tak menerbitkan source map browser, jadi stack konsol menunjuk chunk
    # `/_next/static/...`, bukan berkas sumber: syarat lama "konsol menunjuk berkas diff" tak pernah
    # terpenuhi dan crash sungguhan lolos sebagai tangkapan gagal. Boundary hanya lahir dari kode
    # aplikasi atau stub manifest, dan keduanya tanggungan eksekutor. Konsol tetap direkam sebagai
    # bukti untuk judge. `berkas_diff` tidak lagi ikut memutus di sini.
    if hasil.get("error_boundary"):
        return "galat_kode"
    status = hasil.get("status_http")
    if isinstance(status, int) and status >= 400:
        return "tangkapan_gagal"
    return "ok"


def layar_dinilai(ringkasan, berkas_diff=None):
    """True bila minimal satu rute 'ok' atau 'galat_kode'."""
    diff = berkas_diff or []
    return any(klasifikasi_rute(r, diff) in ("ok", "galat_kode") for r in ringkasan.get("rute") or [])


def _kunci(t):
    return (t.get("file"), t.get("line"), t.get("alasan"))


def hitung_salah_tuduh(verdict_desain_berikut, bantahan, temuan_sebelum):
    """Bantahan eksekutor vs putusan judge. Kunci temuan = (file, line, alasan).

    bantahan: {"temuan": {file,line,alasan}, "alasan", "bukti"}.
    Putusan dibaca dari verdict_desain_berikut["bantahan"]: {"temuan", "putusan", "alasan"};
    TIDAK disimpulkan dari hilangnya temuan (temuan bisa hilang karena kode diubah).
    diabaikan: temuan tak ada di temuan_sebelum. Sah tanpa putusan = ditolak.
    """
    sebelum = {_kunci(t) for t in temuan_sebelum}
    putusan = {}
    for p in verdict_desain_berikut.get("bantahan") or []:
        putusan[_kunci(p.get("temuan") or {})] = p.get("putusan")
    hasil = {"diterima": 0, "ditolak": 0, "diabaikan": 0}
    for b in bantahan:
        k = _kunci(b.get("temuan") or {})
        if k not in sebelum:
            hasil["diabaikan"] += 1
        elif putusan.get(k) == "diterima":
            hasil["diterima"] += 1
        else:
            hasil["ditolak"] += 1
    return hasil


def _baca_berkas_diff(path):
    with open(path, encoding="utf-8-sig") as f:  # PowerShell 5.1 menulis BOM
        return [baris.strip() for baris in f if baris.strip()]


def _baca_json(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Keputusan deterministik judge desain")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("perlu")
    p.add_argument("--repo", required=True)
    p.add_argument("--berkas-dari", required=True)
    v = sub.add_parser("validasi")
    v.add_argument("manifest")
    r = sub.add_parser("ringkas")
    r.add_argument("ringkasan")
    r.add_argument("--berkas-dari", required=True)
    s = sub.add_parser("salah-tuduh")
    s.add_argument("--sebelum", required=True)
    s.add_argument("--berikut", required=True)
    s.add_argument("--bantahan", required=True)
    a = ap.parse_args(argv)

    if a.cmd == "perlu":
        berkas = _baca_berkas_diff(a.berkas_dari)
        print(json.dumps({"perlu": perlu_judge_desain(a.repo, berkas), "berkas_layar": berkas_layar(berkas)}, indent=1))
        return 0
    if a.cmd == "validasi":
        try:
            with open(a.manifest, encoding="utf-8-sig") as f:
                galat = validasi_manifest(json.load(f))
        except (OSError, ValueError) as e:
            galat = ["manifest tidak terbaca: %s" % e]
        print(json.dumps({"galat": galat}, indent=1))
        return 1 if galat else 0
    if a.cmd == "salah-tuduh":
        sebelum, berikut, bantahan = (_baca_json(x) for x in (a.sebelum, a.berikut, a.bantahan))
        print(json.dumps(hitung_salah_tuduh(berikut, bantahan or [], sebelum.get("temuan") or []), indent=1))
        return 0
    with open(a.ringkasan, encoding="utf-8-sig") as f:
        ringkasan = json.load(f)
    diff = _baca_berkas_diff(a.berkas_dari)
    rute = [dict(r, klasifikasi=klasifikasi_rute(r, diff)) for r in ringkasan.get("rute") or []]
    # `galat` tingkat atas (build tak ada, port dipakai, server tak listen, node tak ada) diteruskan:
    # tanpa itu ringkasan ber-`rute: []` cuma terbaca "tidak dinilai" tanpa alasan di verdict/PR.
    galat = ringkasan.get("galat") or None
    # indent=1: Read memotong baris panjang, dan keluaran satu baris >80 KB terbaca sebagian oleh judge.
    print(json.dumps({"rute": rute, "layar_dinilai": layar_dinilai(ringkasan, diff), "galat": galat}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
