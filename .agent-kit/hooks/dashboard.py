#!/usr/bin/env python3
"""dashboard.py — cermin dashboard.ps1 untuk mac/linux; UI tetap SATU tempat: dashboard.template.html.
Bentuk JSON yang ditanam HARUS sama dengan versi .ps1 (versi 1). Dipanggil oleh dashboard.sh.
pakai: dashboard.py [--workspace WS] [--hari 30] [--repos a,b] [--org ORG] [--tanpa-gh] [--loop DETIK] [--keluaran F]
"""
import datetime
import glob
import json
import os
import re
import subprocess
import sys
import time

RE_PREFIX = re.compile(r"^(feat|fix|docs|test|chore|refactor|perf|style|build|ci)(\(([^)]+)\))?!?:")


def kit_root(script_dir):
    p = os.path.dirname(os.path.abspath(script_dir))
    if os.path.basename(p) == ".agent-kit":
        return p
    return os.path.join(os.path.dirname(p), "architecture-draft", ".agent-kit")


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def ambil_pr(repos, org, hari):
    hasil, terpotong, ok, pesan = {}, [], True, ""
    rc, _, err = run(["gh", "auth", "status"])
    if rc != 0:
        return {"ok": False, "pesan": "gh belum login: " + (err.strip().splitlines() or [""])[0], "pr": [], "terpotong": []}
    akhir = datetime.date.today()
    for repo in repos:
        i = 0
        while i * 7 < hari:
            sampai = akhir - datetime.timedelta(days=7 * i)
            dari = akhir - datetime.timedelta(days=7 * (i + 1) - 1)
            rentang = "%s..%s" % (dari.isoformat(), sampai.isoformat())
            for mode in ("created", "merged"):
                state = "merged" if mode == "merged" else "all"
                rc, out, err = run(["gh", "pr", "list", "--repo", "%s/%s" % (org, repo), "--state", state, "--limit", "500",
                                    "--search", "%s:%s" % (mode, rentang), "--json", "number,title,createdAt,mergedAt,state,headRefName,author,url"])
                if rc != 0:
                    ok, pesan = False, (err.strip().splitlines() or [""])[0]
                    continue
                try:
                    arr = json.loads(out)
                except Exception:
                    arr = []
                if len(arr) >= 500:
                    terpotong.append("%s %s %s" % (repo, mode, rentang))
                for p in arr:
                    key = "%s#%s" % (repo, p["number"])
                    if key in hasil:
                        continue
                    m = RE_PREFIX.match(p.get("title", ""))
                    hasil[key] = {"repo": repo, "number": p["number"], "title": p.get("title"), "createdAt": p.get("createdAt"),
                                  "mergedAt": p.get("mergedAt"), "state": p.get("state"), "branch": p.get("headRefName"),
                                  "author": (p.get("author") or {}).get("login", ""), "url": p.get("url"),
                                  "prefix": m.group(1).lower() if m else None, "scope": m.group(3).lower() if (m and m.group(3)) else None}
            i += 1
    pr = sorted(hasil.values(), key=lambda x: x["createdAt"] or "", reverse=True)
    return {"ok": ok, "pesan": pesan, "pr": pr, "terpotong": terpotong}


def ambil_brief(ws):
    out = []
    for f in sorted(glob.glob(os.path.join(ws, ".task-plans", "briefs", "*.md"))):
        txt = open(f, encoding="utf-8").read()
        g = lambda rx, d="": (re.search(rx, txt, re.M).group(1).strip() if re.search(rx, txt, re.M) else d)
        hasil = re.search(r"## Hasil\s*(.*)$", txt, re.S)
        hasil = hasil.group(1) if hasil else ""
        pr = re.search(r"(https://github\.com/[^\s)*]+/pull/\d+)", hasil)
        status = "pr" if pr else ("gagal" if "GAGAL" in hasil else "belum")
        perc = re.search(r"Percobaan:\s*(\d)", hasil)
        wt = re.search(r"Worktree:\s*`?([^`\s·]+)", hasil)
        base = os.path.splitext(os.path.basename(f))[0]
        out.append({"berkas": ".task-plans/briefs/" + os.path.basename(f), "slug": re.sub(r"^\d{4}-\d{2}-\d{2}-", "", base),
                    "judul": g(r"^# Brief:\s*(.+)$", base), "repo": g(r"^- Repo:\s*(\S+)"), "domain": g(r"^- Domain:\s*(\S+)"),
                    "tanggal": g(r"^- Tanggal:\s*(\S+)"), "status": status, "pr_url": pr.group(1) if pr else None,
                    "percobaan": int(perc.group(1)) if perc else None, "worktree": wt.group(1) if wt else ""})
    return out


def ambil_judge(ws):
    out = []
    for f in sorted(glob.glob(os.path.join(ws, ".task-plans", "judge", "*.json"))):
        if not re.search(r"-\d+\.json$", f):
            continue
        try:
            j = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        dur = sum(float(g.get("durasi_detik") or 0) for g in ((j.get("gerbang") or {}).get("gerbang") or []))
        kritis = len([t for t in ((j.get("verdict") or {}).get("temuan") or []) if t.get("kelas") == "kritis"])
        base = os.path.splitext(os.path.basename(f))[0]
        out.append({"berkas": os.path.basename(f), "slug": re.sub(r"-\d+$", "", base), "percobaan": j.get("percobaan"),
                    "lolos": bool(j.get("lolos")), "waktu": j.get("waktu"), "durasi_gerbang": round(dur, 1), "temuan_kritis": kritis, "agen": j.get("agen")})
    return out


def ambil_json_dir(d):
    out = []
    for f in sorted(glob.glob(os.path.join(d, "*.json"))):
        try:
            out.append(json.load(open(f, encoding="utf-8")))
        except Exception:
            pass
    return out


def main(argv):
    ws, hari, repos, org, tanpa_gh, loop, keluaran = os.getcwd(), 30, ["bip-erp", "erp-frontend"], "bip-itteam-internal", False, 0, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--workspace": ws = argv[i + 1]; i += 2
        elif a == "--hari": hari = int(argv[i + 1]); i += 2
        elif a == "--repos": repos = argv[i + 1].split(","); i += 2
        elif a == "--org": org = argv[i + 1]; i += 2
        elif a == "--tanpa-gh": tanpa_gh = True; i += 1
        elif a == "--loop": loop = int(argv[i + 1]); i += 2
        elif a == "--keluaran": keluaran = argv[i + 1]; i += 2
        else: i += 1
    ws = os.path.abspath(ws)
    here = os.path.dirname(os.path.abspath(__file__))
    kit = kit_root(here)
    template = os.path.join(here, "dashboard.template.html")
    if not os.path.exists(template):
        print("Template tidak ada: " + template, file=sys.stderr); return 2
    keluaran = keluaran or os.path.join(ws, ".task-plans", "dashboard.html")
    cache = os.path.join(ws, ".task-plans", "dashboard-data.json")

    def bangun():
        if tanpa_gh:
            gh, pr = {"ok": False, "pesan": "tanpa gh dan tidak ada cache", "terpotong": [], "dari_cache": None}, []
            if os.path.exists(cache):
                try:
                    c = json.load(open(cache, encoding="utf-8")); pr = c.get("pr", [])
                    gh = {"ok": bool(c["gh"].get("ok")), "pesan": c["gh"].get("pesan"), "terpotong": c["gh"].get("terpotong", []), "dari_cache": c.get("dibuat")}
                except Exception:
                    pass
        else:
            r = ambil_pr(repos, org, hari); pr = r["pr"]
            gh = {"ok": r["ok"], "pesan": r["pesan"], "terpotong": r["terpotong"], "dari_cache": None}
        sesi = [s for s in ambil_json_dir(os.path.join(ws, ".task-plans", "sesi")) if s.get("session_id")]
        baseline = [{"repo": b.get("repo"), "tanggal": b.get("tanggal"), "commit": b.get("commit"), "jumlah_test": b.get("jumlah_test"), "jumlah_gagal": b.get("jumlah_gagal")}
                    for b in ambil_json_dir(os.path.join(kit, "baseline"))]
        wt = []
        for r_ in repos:
            p = os.path.join(ws, r_)
            if os.path.isdir(p):
                rc, out, _ = run(["git", "-C", p, "-c", "core.fsmonitor=false", "worktree", "list"])
                wt.append({"repo": r_, "jumlah": len(out.strip().splitlines()) if rc == 0 else 0})
        data = {"versi": 1, "dibuat": datetime.datetime.now().astimezone().isoformat(), "workspace": ws, "hari": hari, "repos": repos,
                "gh": gh, "pr": pr, "briefs": ambil_brief(ws), "judge": ambil_judge(ws), "sesi": sesi, "baseline": baseline, "worktree": wt,
                "tanpa_sumber": ["biaya per PR / token (tidak ada pelacakan biaya)", "klasifikasi risiko dan patch/architectural (klasifikasi otomatis tampil pasti padahal tebakan)"]}
        js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        if not tanpa_gh:
            open(cache, "w", encoding="utf-8").write(js)
        html = open(template, encoding="utf-8").read().replace("__DASHBOARD_DATA__", js.replace("</", "<\\/"))
        os.makedirs(os.path.dirname(keluaran), exist_ok=True)
        open(keluaran, "w", encoding="utf-8").write(html)
        print("Dashboard: %s  (PR %d, brief %d, judge %d, sesi %d%s)" % (keluaran, len(pr), len(data["briefs"]), len(data["judge"]), len(sesi), "" if gh["ok"] else ", GH TIDAK: " + str(gh["pesan"])))
        if gh["terpotong"]:
            print("PERINGATAN irisan penuh (angka kurang dari kenyataan): " + "; ".join(gh["terpotong"]))

    if loop > 0:
        print("Mode loop: menulis ulang tiap %d detik." % loop)
        while True:
            bangun(); time.sleep(loop)
    else:
        bangun()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
