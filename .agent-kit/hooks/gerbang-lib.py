#!/usr/bin/env python3
"""gerbang-lib.py — cermin gerbang-lib.ps1 + gerbang.ps1 + baseline-test.ps1 untuk mac/linux.

Dipanggil oleh gerbang.sh dan baseline-test.sh. Alasan desain ada di berkas .ps1-nya.
Bentuk nama test yang disimpan di baseline dan dibandingkan gerbang HARUS sama dengan versi .ps1:
  vitest : '<path relatif>/<file> > <fullName>'   dan '<file> > (gagal dimuat)'
  go     : 'services/<svc>:<Package>.<Test>'        dan 'services/<svc>:<Package>.(paket gagal)'
Baseline yang ditulis di Windows harus bisa dibaca di mac dan sebaliknya.
"""
import datetime
import glob
import json
import os
import subprocess
import sys
import tempfile
import time


def git(top, *args):
    r = subprocess.run(["git", "-C", top, "-c", "core.fsmonitor=false", *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def kit_root(script_dir):
    p = os.path.dirname(os.path.abspath(script_dir))
    if os.path.basename(p) == ".agent-kit":
        return p
    return os.path.join(os.path.dirname(p), "architecture-draft", ".agent-kit")


def repo_top(path):
    return git(path, "rev-parse", "--show-toplevel")


def nama_repo(path):
    c = git(path, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return os.path.basename(os.path.dirname(c)) if c else None


def jenis_repo(top):
    if os.path.exists(os.path.join(top, "package.json")) and os.path.exists(os.path.join(top, "pnpm-lock.yaml")):
        return "node"
    if glob.glob(os.path.join(top, "services", "*", "go.mod")):
        return "go"
    return "lain"


def berkas_tersentuh(top, base):
    a = []
    mb = git(top, "merge-base", base, "HEAD")
    if mb:
        a += git(top, "diff", "--name-only", mb).splitlines()
    a += git(top, "ls-files", "--others", "--exclude-standard").splitlines()
    return sorted(set(x for x in a if x))


def semua_service(top):
    return sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(top, "services", "*", "go.mod")))


def services_tersentuh(top, berkas):
    if any(b.startswith("shared-library/") for b in berkas):
        return semua_service(top)
    s = set()
    for b in berkas:
        parts = b.split("/")
        if parts[0] == "services" and len(parts) > 2 and os.path.exists(os.path.join(top, "services", parts[1], "go.mod")):
            s.add(parts[1])
    return sorted(s)


def jalankan(nama, cwd, cmd):
    t = time.time()
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    out = (r.stdout + r.stderr).splitlines()
    return {"nama": nama, "lolos": r.returncode == 0, "exit": r.returncode,
            "durasi_detik": round(time.time() - t, 1), "ekor": out[-25:], "semua": out}


def vitest_json(top):
    tmp = os.path.join(tempfile.gettempdir(), "vitest-%d.json" % os.getpid())
    g = jalankan("test", top, 'pnpm exec vitest run --reporter=json --outputFile="%s"' % tmp)
    gagal, jumlah, terurai = [], 0, False
    if os.path.exists(tmp):
        try:
            j = json.load(open(tmp, encoding="utf-8"))
            terurai = True
            for f in j.get("testResults", []):
                rel = f.get("name", "")
                if rel.startswith(top):
                    rel = rel[len(top):].lstrip("\\/")
                rel = rel.replace("\\", "/")
                ars = f.get("assertionResults", [])
                for tc in ars:
                    jumlah += 1
                    if tc.get("status") == "failed":
                        gagal.append("%s > %s" % (rel, tc.get("fullName", "")))
                if f.get("status") == "failed" and not ars:
                    gagal.append("%s > (gagal dimuat)" % rel)
        except Exception:
            pass
        os.remove(tmp)
    return {"gerbang": g, "jumlah": jumlah, "gagal": sorted(set(gagal)), "terurai": terurai}


def gotest_json(top, svc):
    d = os.path.join(top, "services", svc)
    g = jalankan("test:" + svc, d, "go test ./... -json -count=1")
    gagal, jumlah, terurai = [], 0, False
    for line in g["semua"]:
        if not line.startswith("{"):
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        terurai = True
        if e.get("Test"):
            if e.get("Action") in ("pass", "fail"):
                jumlah += 1
            if e.get("Action") == "fail":
                gagal.append("services/%s:%s.%s" % (svc, e.get("Package", ""), e.get("Test", "")))
        elif e.get("Action") == "fail" and e.get("Package"):
            gagal.append("services/%s:%s.(paket gagal)" % (svc, e.get("Package", "")))
    return {"gerbang": g, "jumlah": jumlah, "gagal": sorted(set(gagal)), "terurai": terurai}


def read_baseline(kit, nama):
    try:
        return json.load(open(os.path.join(kit, "baseline", nama + ".json"), encoding="utf-8"))
    except Exception:
        return None


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def tulis_json(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def tanpa_semua(g):
    return {k: v for k, v in g.items() if k != "semua"}


def gerbang_test(nama_gerbang, t, bl):
    bl_gagal = bl.get("gagal", []) if bl else []
    baru = [x for x in t["gagal"] if x not in bl_gagal] if bl else []
    lolos = (t["terurai"] and not baru) if bl else t["terurai"]
    return {"nama": nama_gerbang, "lolos": lolos, "exit": t["gerbang"]["exit"], "durasi_detik": t["gerbang"]["durasi_detik"],
            "jumlah_test": t["jumlah"], "gagal_total": len(t["gagal"]),
            "gagal_di_baseline": len([x for x in t["gagal"] if x in bl_gagal]), "gagal_baru": baru,
            "terurai": t["terurai"], "baseline": ("%s @ %s" % (bl.get("tanggal"), bl.get("commit"))) if bl else None,
            "ekor": t["gerbang"]["ekor"]}


def cmd_gerbang(argv):
    path, base, kit, tanpa_build, tanpa_test, keluaran = None, "origin/main", None, False, False, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--base": base = argv[i + 1]; i += 2
        elif a == "--kit": kit = argv[i + 1]; i += 2
        elif a == "--keluaran": keluaran = argv[i + 1]; i += 2
        elif a == "--tanpa-build": tanpa_build = True; i += 1
        elif a == "--tanpa-test": tanpa_test = True; i += 1
        else: path = a; i += 1
    if not path:
        print("pakai: gerbang.sh <path> [--base X] [--kit K] [--tanpa-build] [--tanpa-test] [--keluaran F]", file=sys.stderr); return 2
    kit = kit or kit_root(os.path.dirname(__file__))
    top = repo_top(path)
    if not top:
        print("Bukan repo git: %s" % path, file=sys.stderr); return 2
    nama, jenis = nama_repo(top), jenis_repo(top)
    git(top, "fetch", "origin", "--quiet")
    berkas = berkas_tersentuh(top, base)
    gerbang, catatan = [], []
    if jenis == "node":
        pkg = json.load(open(os.path.join(top, "package.json"), encoding="utf-8"))
        scripts = pkg.get("scripts", {})
        for s in ("tsc", "lint"):
            if s in scripts: gerbang.append(jalankan(s, top, "pnpm " + s))
            else: catatan.append("skrip '%s' tidak ada di package.json" % s)
        if "build" in scripts:
            if tanpa_build: catatan.append("BUILD DILEWATI atas permintaan (--tanpa-build); jalankan sebelum merge")
            else: gerbang.append(jalankan("build", top, "pnpm build"))
        if not tanpa_test:
            t = vitest_json(top); bl = read_baseline(kit, nama)
            if bl is None: catatan.append("TIDAK ADA BASELINE untuk '%s' di %s/baseline; kegagalan test TIDAK dibandingkan dengan apa pun. Buat dengan baseline-test.sh." % (nama, kit))
            gerbang.append(gerbang_test("test", t, bl))
            if not t["terurai"]: catatan.append("keluaran vitest JSON tidak terurai; gerbang test dianggap GAGAL")
    elif jenis == "go":
        svcs = services_tersentuh(top, berkas)
        if not svcs: catatan.append("tidak ada services/<x> tersentuh: go build/test dilewati")
        bl = read_baseline(kit, nama)
        if bl is None and svcs and not tanpa_test: catatan.append("TIDAK ADA BASELINE untuk '%s'; kegagalan test TIDAK dibandingkan dengan apa pun." % nama)
        for s in svcs:
            gerbang.append(jalankan("build:" + s, os.path.join(top, "services", s), "go build ./..."))
            if not tanpa_test: gerbang.append(gerbang_test("test:" + s, gotest_json(top, s), bl))
    else:
        catatan.append("jenis repo 'lain': tidak ada gerbang deterministik")
    keluar = [tanpa_semua(g) for g in gerbang]
    lolos = all(g["lolos"] for g in keluar)
    hasil = {"repo": nama, "jenis": jenis, "path": top, "branch": git(top, "symbolic-ref", "--short", "HEAD"),
             "commit": git(top, "rev-parse", "--short", "HEAD"), "base": base, "waktu": now_iso(),
             "berkas_tersentuh": berkas, "gerbang": keluar, "catatan": catatan, "lolos": lolos}
    if keluaran: tulis_json(keluaran, hasil)
    print(json.dumps(hasil, ensure_ascii=False, indent=2))
    return 0 if lolos else 1


def cmd_baseline(argv):
    path, kit, services = None, None, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--kit": kit = argv[i + 1]; i += 2
        elif a == "--services": services = argv[i + 1].split(","); i += 2
        else: path = a; i += 1
    if not path:
        print("pakai: baseline-test.sh <path> [--kit K] [--services a,b]", file=sys.stderr); return 2
    kit = kit or kit_root(os.path.dirname(__file__))
    top = repo_top(path)
    if not top:
        print("Bukan repo git: %s" % path, file=sys.stderr); return 2
    nama, jenis = nama_repo(top), jenis_repo(top)
    t0 = time.time(); gagal, jumlah, terurai, catatan = [], 0, False, []
    if jenis == "node":
        t = vitest_json(top); gagal, jumlah, terurai = t["gagal"], t["jumlah"], t["terurai"]
    elif jenis == "go":
        for s in (services or semua_service(top)):
            print("  go test services/%s ..." % s)
            t = gotest_json(top, s)
            terurai = terurai or t["terurai"]; gagal += t["gagal"]; jumlah += t["jumlah"]
            if not t["terurai"]: catatan.append("services/%s: keluaran go test tidak terurai (mungkin gagal build seluruhnya)" % s)
    else:
        print("Jenis repo 'lain', tidak ada suite test: %s" % top, file=sys.stderr); return 2
    if not terurai:
        print('Keluaran test tidak terurai sama sekali. Baseline TIDAK ditulis: "0 gagal" dari pengurai yang mati bukan baseline.', file=sys.stderr); return 3
    bl = {"repo": nama, "jenis": jenis, "tanggal": now_iso(), "commit": git(top, "rev-parse", "--short", "HEAD"),
          "path_ukur": top, "jumlah_test": jumlah, "jumlah_gagal": len(set(gagal)), "gagal": sorted(set(gagal)),
          "durasi_detik": round(time.time() - t0, 1), "catatan": catatan,
          "cara_ukur_ulang": "baseline-test.sh <checkout origin/main bersih> ; jangan di branch fitur"}
    out = os.path.join(kit, "baseline", nama + ".json")
    tulis_json(out, bl)
    print("Baseline %s @ %s: %d test, %d gagal, %s detik -> %s" % (nama, bl["commit"], jumlah, bl["jumlah_gagal"], bl["durasi_detik"], out))
    if bl["jumlah_gagal"] == 0: print("PERHATIAN: nol kegagalan. Pastikan suite benar-benar berjalan (jumlah_test masuk akal?) sebelum mempercayainya.")
    return 0


if __name__ == "__main__":
    sub = sys.argv[1] if len(sys.argv) > 1 else ""
    if sub == "gerbang": sys.exit(cmd_gerbang(sys.argv[2:]))
    if sub == "baseline": sys.exit(cmd_baseline(sys.argv[2:]))
    print("pakai: gerbang-lib.py gerbang|baseline ...", file=sys.stderr); sys.exit(2)
