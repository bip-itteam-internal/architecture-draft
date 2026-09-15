#!/usr/bin/env python3
"""kantor-agent.py: SATU-SATUNYA penulis data Kantor Agent (/kantor-agent). UI-nya satu tempat:
kantor-agent.template.html. Launcher: kantor-agent.ps1 (Windows) / kantor-agent.sh (mac/linux).

Membaca EKOR transkrip sesi Claude Code yang hidup, menurunkan area, keadaan, dan peran tiap sesi
dan subagent, lalu menulis <keluaran>/kantor-agent-data.js secara atomik.

Kenapa transkrip dan bukan status di .task-plans/sesi: diukur 2026-09-15, 72 dari 99 berkas sesi
berstatus "aktif" padahal hanya 7 transkripnya ditulis dalam 10 menit terakhir (SessionEnd sering
tak menyala). Berkas sesi kit hanya pelengkap: tahap, task, dan SessionEnd.

Berkas, bukan layanan (ADR 0077 §5): halaman membaca berkas ini lewat <script> yang disuntik ulang
(terbukti membaca isi terbaru di file://, spike CDP 2026-09-15). Penulis yang mati terlihat sebagai
data basi. Tanpa hook baru, hanya pustaka standar Python.

Format transkrip dinyatakan INTERNAL oleh dok resmi Claude Code dan bisa patah di rilis mana pun.
Kegagalan mengurai dilaporkan lewat skema.dikenali=false, bukan kantor kosong yang terbaca seolah
tak ada yang bekerja.

Desain: architecture-draft/.agent-kit/docs/2026-09-15-kantor-agent-design.md

pakai: kantor-agent.py --workspace WS [--proyek-dir DIR] (--sekali | --loop DETIK) [--sepi-menit 60] [--keluaran DIR]
"""
import argparse
import json
import os
import re
import sys
import time
from collections import OrderedDict, deque
from datetime import datetime, timezone

VERSI_DATA = 1
HIDUP_UTAMA_DETIK = 30 * 60
HIDUP_SUB_DETIK = 10 * 60
DIAM_MENIT = 10
# Ekor pertama sengaja pendek dan diperluas bila tak memuat user/assistant (baca_ekor). Diukur 2026-09-15
# atas 7 transkrip hidup: ekor 256 KB median 320 ms per tick, 64 KB sekitar 200 ms, sebelum cache per berkas.
EKOR_UTAMA = 64 * 1024
EKOR_SUB = 32 * 1024
EKOR_MAKS = 2 * 1024 * 1024
# prasaring daftar direktori, sengaja longgar (lihat _daftar_jsonl)
PRASARING_UTAMA_DETIK = 6 * 3600
PRASARING_SUB_DETIK = 30 * 60
_CACHE = {}  # path -> ((ukuran, mtime_ns), (hasil urai, baris_diurai, baris_rusak))
# transkrip sependek ini tanpa user/assistant = sesi yang baru lahir, bukan tanda format berubah
MIN_BARIS_TANPA_PERCAKAPAN = 20
GAGAL_TULIS_MAKS = 5
NAMA_DATA = "kantor-agent-data.js"
NAMA_PID = "kantor-agent.pid"

AREA_ALAT = {
    "Read": "perpustakaan", "Grep": "perpustakaan", "Glob": "perpustakaan", "WebFetch": "perpustakaan",
    "WebSearch": "perpustakaan", "Skill": "perpustakaan", "ToolSearch": "perpustakaan",
    "Edit": "meja", "Write": "meja", "NotebookEdit": "meja",
    "PowerShell": "server", "Bash": "server", "Monitor": "server", "TaskOutput": "server", "TaskStop": "server",
    "Agent": "rapat", "Workflow": "rapat", "SendMessage": "rapat",
    "AskUserQuestion": "lounge", "ExitPlanMode": "lounge",
}
PERAN = {
    "general-purpose": "Generalis", "Explore": "Peneliti", "Plan": "Arsitek", "loop-fix": "Engineer",
    "loop-test": "QA", "loop-refactor": "Refactor", "loop-judge": "Juri", "loop-docs": "Penulis",
    "claude-code-guide": "Pemandu",
}


def area_alat(nama):
    # tool MCP dan tool yang tak dikenal: ruang server dengan nama aslinya, TIDAK ditebak dari namanya
    return AREA_ALAT.get(str(nama or ""), "server")


def peran(jenis):
    if not jenis:
        return "subagent"
    return PERAN.get(jenis, jenis)


def _potong(s, n=56):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[: n - 1] + "\u2026"


def _nama_berkas(p):
    return str(p or "").replace("\\", "/").rsplit("/", 1)[-1]


def detail_alat(nama, masukan):
    m = masukan if isinstance(masukan, dict) else {}
    if nama in ("PowerShell", "Bash", "Monitor"):
        return _potong(m.get("description") or m.get("command"))
    if nama in ("Read", "Edit", "Write", "NotebookEdit"):
        return _potong(_nama_berkas(m.get("file_path") or m.get("notebook_path")))  # nama berkas, bukan path
    if nama in ("Grep", "Glob"):
        return _potong(m.get("pattern"), 40)
    if nama == "Agent":
        return _potong(m.get("description"))
    if nama == "WebSearch":
        return _potong(m.get("query"))
    if nama == "WebFetch":
        return _potong(m.get("url"), 48)
    if nama == "Skill":
        return _potong(m.get("skill"))
    if nama == "AskUserQuestion":
        qs = m.get("questions")
        q = qs[0] if isinstance(qs, list) and qs and isinstance(qs[0], dict) else {}
        return _potong(q.get("header") or q.get("question"))
    return ""


def urai(kejadian):
    """Satu lintasan atas kejadian berurutan.

    `tertunda` = tool_use yang belum punya tool_result. Dihapus oleh tool_result-nya, oleh
    end_turn, dan oleh prompt baru dari user (kejadian user tanpa tool_result dan bukan isMeta).
    Tipe selain user/assistant (attachment, queue-operation, ...) tidak mengubah keadaan; ai-title
    dan pr-link hanya dibaca sebagai label."""
    judul = pr = cwd = None
    tertunda = OrderedDict()
    akhir = None
    dikenal = 0
    for o in kejadian:
        if not isinstance(o, dict):
            continue
        t = o.get("type")
        if o.get("cwd"):
            cwd = o["cwd"]
        if t == "ai-title":
            judul = o.get("aiTitle") or judul
        elif t == "pr-link":
            if o.get("prNumber") is not None:
                pr = "#%s" % o["prNumber"]
        elif t == "assistant":
            dikenal += 1
            pesan = o.get("message") or {}
            for b in pesan.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    tertunda[b.get("id")] = (b.get("name"), b.get("input"), o.get("timestamp"))
            if pesan.get("stop_reason") == "end_turn":
                tertunda.clear()
            akhir = o
        elif t == "user":
            dikenal += 1
            if o.get("isMeta"):
                continue
            isi = (o.get("message") or {}).get("content")
            ada_hasil = False
            if isinstance(isi, list):
                for b in isi:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        tertunda.pop(b.get("tool_use_id"), None)
                        ada_hasil = True
            if not ada_hasil:
                tertunda.clear()  # prompt baru dari user
            akhir = o
    return {"judul": judul, "pr": pr, "cwd": cwd, "tertunda": tertunda, "akhir": akhir, "dikenal": dikenal}


_PECAHAN_LEBIH = re.compile(r"(\.\d{6})\d+")


def _waktu(ts):
    if not ts:
        return None
    # berkas sesi kit ditulis PowerShell ToString('o') dengan 7 digit pecahan; Python <= 3.10 hanya menerima 6
    teks = _PECAHAN_LEBIH.sub(r"\1", str(ts).replace("Z", "+00:00"))
    try:
        d = datetime.fromisoformat(teks)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _detik_sejak(ts, sekarang):
    d = _waktu(ts)
    return None if d is None else max(0, int((sekarang - d).total_seconds()))


def selesai_giliran(u):
    a = u["akhir"]
    return (a is not None and not u["tertunda"] and a.get("type") == "assistant"
            and (a.get("message") or {}).get("stop_reason") == "end_turn")


def turunkan_keadaan(u, ada_subagent, sekarang):
    """Keadaan robot dari hasil `urai`.

     [berpikir @meja] ──tool_use tertunda──> [alat @area tool] ──AskUserQuestion──> [menunggu_anda @lounge]
            ^            <─tool_result/prompt──┘
            │ end_turn ─┬─ subagent hidup ≥1 ─> [menunggu_subagent @rapat]
            │           └─ subagent hidup 0 ──> [menunggu_anda @lounge]
            └──────────── prompt baru ──────────────────┘
    """
    akhir = u["akhir"]
    diam = _detik_sejak(akhir.get("timestamp"), sekarang) if akhir else None
    if u["tertunda"]:
        # batch paralel: hasil tool singkat sering baru tertulis setelah tool lambat di batch yang sama selesai,
        # jadi yang menentukan tool paling awal di luar perpustakaan/meja, bukan yang terakhir
        semua = list(u["tertunda"].values())
        nama, masukan, ts = next((t for t in semua if area_alat(t[0]) not in ("perpustakaan", "meja")), semua[0])
        area = area_alat(nama)
        return {"area": area, "keadaan": "menunggu_anda" if area == "lounge" else "alat", "alat": nama or "",
                "detail": detail_alat(nama, masukan), "sejak": ts, "durasi_detik": _detik_sejak(ts, sekarang),
                "diam_detik": diam}
    sejak = akhir.get("timestamp") if akhir else None
    if selesai_giliran(u):
        area, keadaan = ("rapat", "menunggu_subagent") if ada_subagent else ("lounge", "menunggu_anda")
    else:
        area, keadaan = "meja", "berpikir"
    return {"area": area, "keadaan": keadaan, "alat": "", "detail": "", "sejak": sejak, "durasi_detik": None,
            "diam_detik": diam}


def di_dalam_workspace(cwd, workspace):
    if not cwd or not workspace:
        return False
    try:
        c = os.path.normcase(os.path.normpath(os.path.abspath(cwd)))
        w = os.path.normcase(os.path.normpath(os.path.abspath(workspace)))
    except (TypeError, ValueError):
        return False
    return c == w or c.startswith(w.rstrip("\\/") + os.sep)


def _urai_ekor(path, ukuran, n):
    with open(path, "rb") as f:
        if ukuran > n:
            f.seek(ukuran - n)
            f.readline()  # buang baris pertama yang terpotong
        data = f.read()
    if data and not data.endswith(b"\n"):
        data = data.rsplit(b"\n", 1)[0] if b"\n" in data else b""  # baris terakhir sedang ditulis
    kejadian, rusak = [], 0
    for baris in data.split(b"\n"):
        if not baris.strip():
            continue
        try:
            o = json.loads(baris)
        except ValueError:
            rusak += 1
            continue
        if isinstance(o, dict):
            kejadian.append(o)
        else:
            rusak += 1
    return kejadian, rusak


def baca_ekor(path, awal=EKOR_UTAMA, maks=EKOR_MAKS):
    """(kejadian, baris_diurai, baris_rusak) dari ekor berkas.

    Bila ekor tak memuat satu pun kejadian user/assistant padahal berkasnya lebih besar, ekor
    diperluas sampai `maks`: satu hasil tool bisa lebih besar dari ekornya, dan ekor yang cuma berisi
    potongannya tak boleh terbaca sebagai format berubah."""
    ukuran = os.path.getsize(path)
    n = awal
    while True:
        kejadian, rusak = _urai_ekor(path, ukuran, n)
        percakapan = any(o.get("type") in ("user", "assistant") for o in kejadian)
        if percakapan or n >= ukuran or n >= maks:
            return kejadian, len(kejadian) + rusak, rusak
        n = min(n * 4, maks)


def _baca_json(path):
    try:
        with open(path, encoding="utf-8-sig") as f:  # PowerShell di sebagian mesin menulis ber-BOM
            o = json.load(f)
    except (OSError, ValueError):
        return {}
    return o if isinstance(o, dict) else {}


def _daftar_jsonl(folder, epoch, prasaring, awalan=""):
    """[(path, os.stat)] berkas .jsonl di `folder` yang mungkin hidup.

    os.stat per berkas di Windows membuka handle: terukur 77 ms untuk 167 transkrip per tick (2026-09-15).
    Data daftar direktori (DirEntry.stat) jauh lebih murah tapi bisa tertinggal untuk berkas yang sedang
    terbuka, jadi hanya dipakai sebagai prasaring longgar; kandidatnya lalu di-stat tepat."""
    hasil = []
    try:
        entri = os.scandir(folder)
    except OSError:
        return hasil
    with entri:
        for e in entri:
            if not (e.name.endswith(".jsonl") and e.name.startswith(awalan)):
                continue
            try:
                if not e.is_file() or epoch - e.stat().st_mtime > prasaring:
                    continue
                hasil.append((e.path, os.stat(e.path)))
            except OSError:
                continue  # terhapus di tengah tick
    hasil.sort(key=lambda x: x[0])
    return hasil


def _urai_berkas(path, st, awal, terlihat):
    """urai() atas ekor berkas, di-cache per (ukuran, mtime): hanya transkrip yang berubah yang diurai ulang."""
    terlihat.add(path)
    kunci = (st.st_size, st.st_mtime_ns)
    lama = _CACHE.get(path)
    if lama and lama[0] == kunci:
        return lama[1]
    kejadian, d, r = baca_ekor(path, awal)
    u = urai(kejadian)
    if lama:  # judul dan PR bisa jatuh di luar ekor yang pendek: pertahankan yang terakhir terlihat
        if u["judul"] is None:
            u["judul"] = lama[1][0]["judul"]
        if u["pr"] is None:
            u["pr"] = lama[1][0]["pr"]
    _CACHE[path] = (kunci, (u, d, r))
    return u, d, r


def _kumpulkan_subagent(folder_sesi, sekarang, terlihat):
    hasil, diurai, rusak = [], 0, 0
    epoch = sekarang.timestamp()
    prasaring = HIDUP_SUB_DETIK + PRASARING_SUB_DETIK
    for sp, st in _daftar_jsonl(os.path.join(folder_sesi, "subagents"), epoch, prasaring, "agent-"):
        if epoch - st.st_mtime > HIDUP_SUB_DETIK:
            continue
        try:
            u, d, r = _urai_berkas(sp, st, EKOR_SUB, terlihat)
        except OSError:
            continue  # terkunci atau terhapus di tengah tick: coba lagi tick berikutnya
        diurai += d
        rusak += r
        if u["akhir"] is None or selesai_giliran(u):
            continue  # subagent yang end_turn sudah pulang
        meta = _baca_json(sp[: -len(".jsonl")] + ".meta.json")
        hasil.append(dict(id=os.path.basename(sp)[len("agent-"): -len(".jsonl")],
                          jenis=meta.get("agentType") or "subagent", peran=peran(meta.get("agentType")),
                          deskripsi=_potong(meta.get("description"), 60), **turunkan_keadaan(u, False, sekarang)))
    return hasil, diurai, rusak


def kumpulkan(proyek_dir, workspace, sekarang):
    """Data lengkap untuk halaman, tanpa blok `penulis` (diisi pemanggil)."""
    epoch = sekarang.timestamp()
    sesi, diurai, rusak, luar, tanpa_percakapan = [], 0, 0, 0, 0
    terlihat = set()
    try:
        with os.scandir(proyek_dir) as entri:
            folder_proyek = sorted(e.path for e in entri if e.is_dir())
    except OSError:
        folder_proyek = []
    for path, st in [x for f in folder_proyek for x in _daftar_jsonl(f, epoch, PRASARING_UTAMA_DETIK)]:
        if epoch - st.st_mtime > HIDUP_UTAMA_DETIK:
            continue
        try:
            u, d, r = _urai_berkas(path, st, EKOR_UTAMA, terlihat)
        except OSError:
            continue
        diurai += d
        rusak += r
        if u["dikenal"] == 0 and d >= MIN_BARIS_TANPA_PERCAKAPAN:
            tanpa_percakapan += 1
        if not di_dalam_workspace(u["cwd"], workspace):
            if u["cwd"]:
                luar += 1
            continue
        sid = os.path.basename(path)[: -len(".jsonl")]
        kit = _baca_json(os.path.join(workspace, ".task-plans", "sesi", sid + ".json"))
        t_akhir = _waktu(u["akhir"].get("timestamp")) if u["akhir"] else None
        t_selesai = _waktu(kit.get("selesai")) if kit.get("status") == "selesai" else None
        if t_selesai and (t_akhir is None or t_selesai >= t_akhir):
            continue  # SessionEnd lebih baru dari kejadian terakhir: sudah pulang (yang lebih lama = --resume)
        anak, d2, r2 = _kumpulkan_subagent(path[: -len(".jsonl")], sekarang, terlihat)
        diurai += d2
        rusak += r2
        sesi.append(dict(id=sid, judul=_potong(u["judul"] or kit.get("task") or "", 90), tahap=kit.get("tahap") or "",
                         pr=u["pr"], _mulai=kit.get("mulai") or "~", **turunkan_keadaan(u, bool(anak), sekarang),
                         subagent=anak))
    sesi.sort(key=lambda s: (s["_mulai"], s["id"]))
    for s in sesi:
        del s["_mulai"]
    dikenali = not (diurai and rusak * 2 > diurai) and tanpa_percakapan == 0
    for k in [k for k in _CACHE if k not in terlihat]:
        del _CACHE[k]  # transkrip yang tak lagi hidup tidak ditahan di memori
    return {
        "versi": VERSI_DATA,
        "dibuat": sekarang.isoformat().replace("+00:00", "Z"),
        "ambang": {"hidup_menit": HIDUP_UTAMA_DETIK // 60, "diam_menit": DIAM_MENIT},
        "skema": {"baris_diurai": diurai, "baris_rusak": rusak, "dikenali": dikenali,
                  "dilewati_luar_workspace": luar},
        "sesi": sesi,
    }


def render_js(data):
    teks = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # U+2028/2029 sah di JSON tapi memutus string literal di mesin JS lama; "</" dijaga seandainya disisipkan inline
    teks = teks.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029").replace("</", "<\\/")
    return "window.__KANTOR__ = " + teks + ";\n"


def tulis_atomik(path, teks):
    """Tulis ke berkas sementara lalu ganti nama: halaman tak pernah membaca berkas setengah jadi."""
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(teks)
    try:
        os.replace(tmp, path)
    except OSError:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def _hapus_pid(path):
    try:
        with open(path, encoding="utf-8") as f:
            if f.read().strip() != str(os.getpid()):
                return  # milik penulis lain
        os.remove(path)
    except OSError:
        pass


def _persentil(nilai, q):
    if not nilai:
        return None
    urut = sorted(nilai)
    return round(urut[min(len(urut) - 1, int(q * len(urut)))], 1)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Penulis data Kantor Agent")
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--proyek-dir", default=os.path.join(os.path.expanduser("~"), ".claude", "projects"))
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--sekali", action="store_true")
    mode.add_argument("--loop", type=float, metavar="DETIK")
    ap.add_argument("--sepi-menit", type=float, default=60.0)
    ap.add_argument("--keluaran")
    ap.add_argument("--log", help="catat ke berkas ini, bukan stdout/stderr (dipakai launcher)")
    a = ap.parse_args(argv)
    workspace = os.path.abspath(a.workspace)
    keluaran = a.keluaran or os.path.join(workspace, ".task-plans")
    os.makedirs(keluaran, exist_ok=True)
    path_data = os.path.join(keluaran, NAMA_DATA)
    path_pid = os.path.join(keluaran, NAMA_PID)
    penulis = {"pid": os.getpid(), "interval_detik": a.loop or 0, "berhenti": None, "tick_ms": None}
    durasi = deque(maxlen=120)
    # launcher memberi --log supaya proses lepas tak perlu mewarisi handle stdout/stderr siapa pun
    log = open(a.log, "a", encoding="utf-8") if a.log else None

    def catat(pesan, galat=False):
        tujuan = log or (sys.stderr if galat else sys.stdout)
        print("%s kantor-agent: %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pesan), file=tujuan, flush=True)

    def satu_tick():
        t0 = time.perf_counter()
        data = kumpulkan(a.proyek_dir, workspace, datetime.now(timezone.utc))
        durasi.append((time.perf_counter() - t0) * 1000)
        penulis["tick_ms"] = {"p50": _persentil(durasi, 0.5), "p95": _persentil(durasi, 0.95), "n": len(durasi)}
        data["penulis"] = dict(penulis)
        return data

    if a.sekali:
        try:
            tulis_atomik(path_data, render_js(satu_tick()))
        except OSError as e:
            catat("gagal menulis %s: %s" % (path_data, e), galat=True)
            return 3
        finally:
            if log:
                log.close()
        return 0

    with open(path_pid, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    catat("pid %d menulis %s tiap %s detik" % (os.getpid(), path_data, a.loop))
    gagal = 0
    sepi_sejak = None
    try:
        while True:
            data = satu_tick()
            if data["sesi"]:
                sepi_sejak = None
            elif sepi_sejak is None:
                sepi_sejak = time.monotonic()
            sepi = sepi_sejak is not None and time.monotonic() - sepi_sejak >= a.sepi_menit * 60
            if sepi:
                data["penulis"]["berhenti"] = "sepi"
            try:
                tulis_atomik(path_data, render_js(data))
                gagal = 0
            except OSError as e:
                gagal += 1
                catat("gagal menulis (%d/%d): %s" % (gagal, GAGAL_TULIS_MAKS, e), galat=True)
                if gagal >= GAGAL_TULIS_MAKS:
                    catat("berhenti, %d kali berturut-turut gagal menulis" % gagal, galat=True)
                    return 3
            if sepi:
                catat("tak ada sesi hidup selama %s menit, berhenti" % a.sepi_menit)
                return 0
            time.sleep(a.loop)
    except KeyboardInterrupt:
        return 0
    finally:
        _hapus_pid(path_pid)
        if log:
            log.close()


if __name__ == "__main__":
    sys.exit(main())
