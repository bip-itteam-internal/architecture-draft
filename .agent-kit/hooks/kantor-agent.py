#!/usr/bin/env python3
"""kantor-agent.py: SATU-SATUNYA penulis data Kantor Agent (/kantor-agent). UI-nya satu tempat:
kantor-agent.template.html. Launcher: kantor-agent.ps1 (Windows) / kantor-agent.sh (mac/linux).

Sumber per tick:
- registri sesi Claude Code (~/.claude/sessions/<pid>.json): sesi mana yang TERBUKA dan apakah prosesnya
  sedang bekerja (status busy/idle). Diamati 2026-09-15: `claude agents --json` mencatat 7 sesi terbuka,
  sementara tebakan dari mtime transkrip hanya menemukan 6, karena sesi yang lama diam tak menulis transkrip.
- ekor transkrip sesi: tool yang sedang dipakai, tugas shell latar, judul, PR, subagent.
- berkas sesi kit (.task-plans/sesi): tahap dan task.

Kenapa bukan status di .task-plans/sesi: diukur 2026-09-15, 72 dari 99 berkas sesi berstatus "aktif"
padahal hanya 7 transkripnya ditulis dalam 10 menit terakhir (SessionEnd sering tak menyala).

Registri dan transkrip sama-sama format INTERNAL Claude Code dan bisa patah di rilis mana pun. Penjaganya:
registri dicocokkan dengan `claude agents --json` (terdokumentasi) tiap 60 detik; registri yang tak terbaca
turun ke mode transkrip; transkrip yang gagal diurai dilaporkan lewat skema.dikenali=false. Semuanya tampil
sebagai banner, bukan kantor kosong yang terbaca seolah tak ada yang bekerja.

Berkas, bukan layanan (ADR 0077 §5): halaman membaca berkas ini lewat <script> yang disuntik ulang
(terbukti membaca isi terbaru di file://, spike CDP 2026-09-15). Penulis yang mati terlihat sebagai
data basi. Tanpa hook per tool call, hanya pustaka standar Python.

Desain: architecture-draft/.agent-kit/docs/2026-09-15-kantor-agent-design.md

pakai: kantor-agent.py --workspace WS [--proyek-dir DIR] [--registri-dir DIR] (--sekali | --loop DETIK)
       [--sepi-menit 60] [--cek-silang-detik 60] [--keluaran DIR] [--log BERKAS]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
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
_LOKASI = {}  # sessionId -> path transkrip terakhir ditemukan, supaya tak mencari ulang di tiap folder proyek
# transkrip sependek ini tanpa user/assistant = sesi yang baru lahir, bukan tanda format berubah
MIN_BARIS_TANPA_PERCAKAPAN = 20
GAGAL_TULIS_MAKS = 5
NAMA_DATA = "kantor-agent-data.js"
NAMA_PID = "kantor-agent.pid"
NAMA_KUNCI = "kantor-agent.lock"
REGISTRI_DIR = os.path.join(os.path.expanduser("~"), ".claude", "sessions")
# `claude agents --json` terukur 6,7 sampai 8,6 detik per panggilan (2026-09-15): cek silang, bukan sumber per tick
CEK_SILANG_DETIK = 60
CEK_SILANG_BATAS_DETIK = 30
TIDAK_COCOK_MAKS = 2

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


# Tugas shell latar (run_in_background), bentuk diamati di 12 transkrip 2026-09-15: hasil tool membawa
# toolUseResult.backgroundTaskId dan teks "Command running in background with ID: <id>"; selesainya masuk
# sebagai queue-operation (atau pesan user) berisi <task-notification><task-id><id></task-id>...
_ID_LATAR = re.compile(r"background with ID: ([A-Za-z0-9_-]+)")
_ID_NOTIFIKASI = re.compile(r"<task-id>\s*([^<\s]+)\s*</task-id>")


def _teks_blok(isi):
    if isinstance(isi, str):
        return isi
    if isinstance(isi, list):
        return " ".join(b["text"] for b in isi if isinstance(b, dict) and isinstance(b.get("text"), str))
    return ""


def _id_tugas_latar(kejadian, blok):
    r = kejadian.get("toolUseResult")
    if isinstance(r, dict) and r.get("backgroundTaskId"):
        return str(r["backgroundTaskId"])
    m = _ID_LATAR.search(_teks_blok(blok.get("content")))
    return m.group(1) if m else None


def _tutup_latar(latar, teks):
    if isinstance(teks, str) and "<task-notification>" in teks:
        for m in _ID_NOTIFIKASI.finditer(teks):
            latar.pop(m.group(1), None)


def urai(kejadian):
    """Satu lintasan atas kejadian berurutan.

    `tertunda` = tool_use yang belum punya tool_result. Dihapus oleh tool_result-nya, oleh
    end_turn, dan oleh prompt baru dari user (kejadian user tanpa tool_result dan bukan isMeta).
    `latar` = tugas shell latar yang sudah dimulai dan belum diberi <task-notification>; tidak dihapus
    end_turn maupun prompt baru, karena tugasnya memang tetap berjalan.
    Tipe selain user/assistant/queue-operation (attachment, ...) tidak mengubah keadaan; ai-title
    dan pr-link hanya dibaca sebagai label."""
    judul = pr = cwd = None
    tertunda = OrderedDict()
    latar = OrderedDict()
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
                        asal = tertunda.pop(b.get("tool_use_id"), None)
                        ada_hasil = True
                        if asal and isinstance(asal[1], dict) and asal[1].get("run_in_background") is True:
                            tid = _id_tugas_latar(o, b)
                            if tid:
                                latar[tid] = asal
            _tutup_latar(latar, _teks_blok(isi))
            if not ada_hasil:
                tertunda.clear()  # prompt baru dari user
            akhir = o
        elif t == "queue-operation":
            _tutup_latar(latar, o.get("content"))
    return {"judul": judul, "pr": pr, "cwd": cwd, "tertunda": tertunda, "latar": latar, "akhir": akhir,
            "dikenal": dikenal}


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


def _iso(d):
    return d.isoformat().replace("+00:00", "Z") if d else None


def _dari_ms(ms):
    try:
        return datetime.fromtimestamp(float(ms) / 1000.0, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def _detik_sejak(ts, sekarang):
    d = _waktu(ts)
    return None if d is None else max(0, int((sekarang - d).total_seconds()))


def selesai_giliran(u):
    a = u["akhir"]
    return (a is not None and not u["tertunda"] and a.get("type") == "assistant"
            and (a.get("message") or {}).get("stop_reason") == "end_turn")


def _tool_penentu(tertunda):
    """(nama, input, timestamp) tool tertunda yang menentukan area, atau None.

    Batch paralel: hasil tool singkat sering baru tertulis setelah tool lambat di batch yang sama selesai,
    jadi yang menentukan tool paling awal di luar perpustakaan/meja, bukan yang terakhir."""
    semua = list(tertunda.values())
    if not semua:
        return None
    return next((t for t in semua if area_alat(t[0]) not in ("perpustakaan", "meja")), semua[0])


def turunkan_keadaan(u, ada_subagent, sekarang, registri=None):
    """Keadaan robot dari hasil `urai`, dan dari entri registri sesi bila ada.

     [berpikir @meja] ──tool_use tertunda──> [alat @area tool] ──AskUserQuestion──> [menunggu_anda @lounge]
            ^            <─tool_result/prompt──┘
            │ giliran selesai (end_turn, atau registri tidak busy)
            │     ├─ tugas shell latar belum selesai ─> [menunggu_latar @server]
            │     ├─ subagent hidup ≥1 ──────────────> [menunggu_subagent @rapat]
            │     └─ selain itu ─────────────────────> [menunggu_anda @lounge]
            └──────────── prompt baru / registri busy ───┘
     registri waiting (dialog terbuka) ─┬─ waitingFor "permission prompt" ─> [menunggu_izin @area tool, atau lounge]
                                        └─ alasan lain ────────────────────> [menunggu_anda @lounge]

    Registri menang atas transkrip untuk "prosesnya sedang bekerja atau tidak": status proses berubah
    seketika, sedangkan baris transkrip bisa baru tertulis belakangan. Tool tertunda tetap menentukan area.
    S0 2026-09-15: dialog AskUserQuestion membuat registri "waiting" + waitingFor "input needed" di detik yang
    sama dengan dialognya, 8 detik lebih cepat dari hook Notification permission_prompt."""
    akhir = u["akhir"]
    t_status = registri.get("status_sejak") if registri else None
    t_akhir = _waktu(akhir.get("timestamp")) if akhir else None
    t_diam = max([t for t in (t_akhir, t_status) if t is not None], default=None)
    diam = None if t_diam is None else max(0, int((sekarang - t_diam).total_seconds()))
    status = registri.get("status") if registri else None
    menunggu = registri.get("menunggu") if registri else None
    tunda = _tool_penentu(u["tertunda"])
    if status == "waiting" or menunggu:
        izin = "permission" in str(menunggu or "").lower()
        keadaan = "menunggu_izin" if izin else "menunggu_anda"
        if tunda:
            nama, masukan, ts = tunda
            return {"area": area_alat(nama) if izin else "lounge", "keadaan": keadaan, "alat": nama or "",
                    "detail": detail_alat(nama, masukan), "sejak": ts, "durasi_detik": _detik_sejak(ts, sekarang),
                    "diam_detik": diam}
        return {"area": "lounge", "keadaan": keadaan, "alat": "", "detail": "" if izin else str(menunggu or ""),
                "sejak": _iso(t_status), "durasi_detik": None, "diam_detik": diam}
    if tunda:
        nama, masukan, ts = tunda
        area = area_alat(nama)
        return {"area": area, "keadaan": "menunggu_anda" if area == "lounge" else "alat", "alat": nama or "",
                "detail": detail_alat(nama, masukan), "sejak": ts, "durasi_detik": _detik_sejak(ts, sekarang),
                "diam_detik": diam}
    sejak = akhir.get("timestamp") if akhir else _iso(t_status)
    selesai = selesai_giliran(u) if registri is None else status != "busy"
    if selesai and u["latar"]:
        nama, masukan, ts = next(iter(u["latar"].values()))  # tugas latar paling awal yang belum selesai
        return {"area": "server", "keadaan": "menunggu_latar", "alat": nama or "", "detail": detail_alat(nama, masukan),
                "sejak": ts, "durasi_detik": _detik_sejak(ts, sekarang), "diam_detik": diam}
    if selesai:
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


_KERNEL32 = None


def _periksa_windows(pid):
    """(masih_berjalan, waktu_buat FILETIME) lewat OpenProcess; (False, None) bila proses tak bisa dibuka."""
    global _KERNEL32
    import ctypes
    from ctypes import wintypes
    if _KERNEL32 is None:
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k.OpenProcess.restype = wintypes.HANDLE
        k.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        k.GetExitCodeProcess.restype = wintypes.BOOL
        k.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
        k.GetProcessTimes.restype = wintypes.BOOL
        k.CloseHandle.argtypes = [wintypes.HANDLE]
        _KERNEL32 = k
    h = _KERNEL32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return False, None
    try:
        kode = wintypes.DWORD()
        berjalan = bool(_KERNEL32.GetExitCodeProcess(h, ctypes.byref(kode))) and kode.value == 259  # STILL_ACTIVE
        ft = [wintypes.FILETIME() for _ in range(4)]
        ok = _KERNEL32.GetProcessTimes(h, *[ctypes.byref(x) for x in ft])
        return berjalan, (((ft[0].dwHighDateTime << 32) | ft[0].dwLowDateTime) if ok else None)
    finally:
        _KERNEL32.CloseHandle(h)


def waktu_buat_proses(pid):
    """Waktu pembuatan proses (FILETIME, 100 ns sejak 1601) di Windows; None di OS lain atau bila tak terbaca."""
    if os.name != "nt":
        return None
    try:
        return _periksa_windows(int(pid))[1]
    except (OSError, ValueError, TypeError, AttributeError):
        return None


def proses_hidup(pid, proc_start=None):
    """True bila proses `pid` masih berjalan dan, bila `proc_start` ada (Windows), waktu pembuatannya sama.

    JANGAN os.kill(pid, 0) di Windows: di sana os.kill memanggil TerminateProcess dan MEMBUNUH sesi yang
    diperiksa. procStart di registri = FILETIME GetProcessTimes (6 dari 6 sesi cocok, 2026-09-15), jadi PID
    yang sudah didaur ulang proses lain tidak terbaca sebagai sesi hidup."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            berjalan, buat = _periksa_windows(pid)
        except (OSError, AttributeError):
            return False
        return berjalan and (proc_start in (None, "") or str(buat) == str(proc_start))
    try:
        os.kill(pid, 0)  # posix: sinyal 0 hanya memeriksa keberadaan; procStart posix belum diukur bentuknya
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def baca_registri(folder, workspace, hidup):
    """({sessionId: entri}, info) dari registri sesi Claude Code (~/.claude/sessions/<pid>.json).

    Format INTERNAL, diamati 2026-09-15 di Claude Code 2.1.269: berkas sesi yang ditutup terhapus, dan
    statusnya busy/idle. Berpenjaga cek silang `claude agents --json`; folder yang tak terbaca membuat
    pemanggil turun ke mode transkrip."""
    info = {"terbaca": False, "berkas": 0, "rusak": 0, "luar": 0}
    sesi = {}
    try:
        with os.scandir(folder) as it:
            entri = [e.path for e in it if e.name.endswith(".json")]
    except OSError:
        return sesi, info
    info["terbaca"] = True
    for p in sorted(entri):
        info["berkas"] += 1
        j = _baca_json(p)
        sid, cwd, pid = j.get("sessionId"), j.get("cwd"), j.get("pid")
        if not (isinstance(sid, str) and sid and isinstance(cwd, str) and isinstance(pid, int)):
            info["rusak"] += 1
            continue
        mulai = j.get("procStart")
        if not hidup(pid, None if mulai is None else str(mulai)):
            continue
        if not di_dalam_workspace(cwd, workspace):
            info["luar"] += 1
            continue
        lama = sesi.get(sid)
        if lama and (lama["_diperbarui"] or 0) >= (j.get("updatedAt") or 0):
            continue  # satu sesi, dua proses (mis. dilanjutkan): yang terakhir diperbarui menang
        sesi[sid] = {"pid": pid, "cwd": cwd, "status": j.get("status"), "status_sejak": _dari_ms(j.get("statusUpdatedAt")),
                     "asal": j.get("entrypoint"), "nama": j.get("name"), "mulai": _dari_ms(j.get("startedAt")),
                     "menunggu": j.get("waitingFor"), "_diperbarui": j.get("updatedAt")}
    return sesi, info


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


def _cari_transkrip(folder_proyek, sid):
    """(path, os.stat) transkrip sesi `sid`, tanpa batas umur: sesi terbuka yang lama diam tetap ditemukan."""
    lama = _LOKASI.get(sid)
    kandidat = [os.path.join(f, sid + ".jsonl") for f in folder_proyek]
    if lama and os.path.dirname(lama) in folder_proyek:
        kandidat.insert(0, lama)
    for p in kandidat:
        try:
            st = os.stat(p)
        except OSError:
            continue
        _LOKASI[sid] = p
        return p, st
    _LOKASI.pop(sid, None)
    return None, None


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


def kumpulkan(proyek_dir, workspace, sekarang, registri_dir=None, hidup=None):
    """Data lengkap untuk halaman, tanpa blok `penulis` (diisi pemanggil).

    Dengan `registri_dir` yang terbaca: sesi = entri registri yang prosesnya hidup dan cwd-nya di dalam
    workspace; transkrip hanya menambahkan tool, judul, PR, tugas latar, dan subagent. Tanpa itu (atau
    folder registri tak terbaca): mode transkrip, sesi = transkrip yang ditulis <= 30 menit."""
    epoch = sekarang.timestamp()
    sesi, diurai, rusak, luar, tanpa_percakapan = [], 0, 0, 0, 0
    terlihat = set()
    try:
        with os.scandir(proyek_dir) as entri:
            folder_proyek = sorted(e.path for e in entri if e.is_dir())
    except OSError:
        folder_proyek = []
    reg, info = baca_registri(registri_dir, workspace, hidup or proses_hidup) if registri_dir else ({}, {"terbaca": False})
    if info["terbaca"]:
        kandidat = [(sid, e) + _cari_transkrip(folder_proyek, sid) for sid, e in sorted(reg.items())]
        for sid in [s for s in _LOKASI if s not in reg]:
            del _LOKASI[sid]
        luar = info["luar"]
    else:
        kandidat = [(None, None, path, st) for f in folder_proyek for path, st in _daftar_jsonl(f, epoch, PRASARING_UTAMA_DETIK)
                    if epoch - st.st_mtime <= HIDUP_UTAMA_DETIK]
    for sid, e, path, st in kandidat:
        u = None
        if path:
            try:
                u, d, r = _urai_berkas(path, st, EKOR_UTAMA, terlihat)
            except OSError:
                u = None
            else:
                diurai += d
                rusak += r
                if u["dikenal"] == 0 and d >= MIN_BARIS_TANPA_PERCAKAPAN:
                    tanpa_percakapan += 1
        if e is None:  # mode transkrip
            if u is None:
                continue
            if not di_dalam_workspace(u["cwd"], workspace):
                if u["cwd"]:
                    luar += 1
                continue
            sid = os.path.basename(path)[: -len(".jsonl")]
        kit = _baca_json(os.path.join(workspace, ".task-plans", "sesi", sid + ".json"))
        if e is None:
            t_akhir = _waktu(u["akhir"].get("timestamp")) if u["akhir"] else None
            t_selesai = _waktu(kit.get("selesai")) if kit.get("status") == "selesai" else None
            if t_selesai and (t_akhir is None or t_selesai >= t_akhir):
                continue  # SessionEnd lebih baru dari kejadian terakhir: sudah pulang (yang lebih lama = --resume)
        if u is None:
            u = urai([])  # sesi terbuka tanpa transkrip (baru dibuka, belum ada prompt)
        anak, d2, r2 = _kumpulkan_subagent(path[: -len(".jsonl")], sekarang, terlihat) if path else ([], 0, 0)
        diurai += d2
        rusak += r2
        mulai = kit.get("mulai") or (_iso(e.get("mulai")) if e else None) or "~"
        sesi.append(dict(id=sid, judul=_potong(u["judul"] or kit.get("task") or "", 90), tahap=kit.get("tahap") or "",
                         pr=u["pr"], asal=e.get("asal") if e else None, nama=e.get("nama") if e else None,
                         pid=e.get("pid") if e else None, status_proses=e.get("status") if e else None,
                         menunggu=e.get("menunggu") if e else None,
                         _mulai=mulai, **turunkan_keadaan(u, bool(anak), sekarang, e), subagent=anak))
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
                  "dilewati_luar_workspace": luar, "sumber_hidup": "registri" if info["terbaca"] else "transkrip"},
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


class CekSilang:
    """Mencocokkan registri dengan `claude agents --json` (terdokumentasi) tiap `interval_detik`.

    Subprocess dijalankan tanpa ditunggu: tick penulis tetap 2 detik walau perintahnya terukur 6,7 sampai
    8,6 detik (2026-09-15). Keluarannya ditampung di berkas sementara, bukan pipe, supaya anak yang menulis
    banyak tidak tertahan buffer lalu terbaca "menggantung". Satu kali tak cocok bisa sekadar jeda antar-
    bacaan (sesi dibuka atau ditutup di tengahnya), jadi baru ditandai setelah TIDAK_COCOK_MAKS kali berturut."""

    def __init__(self, perintah, workspace, interval_detik=CEK_SILANG_DETIK, batas_detik=CEK_SILANG_BATAS_DETIK,
                 jam=time.monotonic):
        self.perintah, self.workspace = perintah, workspace
        self.interval, self.batas, self.jam = interval_detik, batas_detik, jam
        self._proses = self._keluaran = None
        self._mulai = self._berikutnya = 0.0
        self._tidak_cocok = 0
        self._status = {"dicek": False, "cocok": None, "catatan": "belum dijalankan"}

    def berjalan(self):
        return self._proses is not None

    def status(self):
        return dict(self._status)

    def _selesai(self, dicek, cocok, catatan):
        self._status = {"dicek": dicek, "cocok": cocok, "catatan": catatan}
        self._berikutnya = self.jam() + self.interval
        if self._keluaran is not None:
            try:
                self._keluaran.close()
            except OSError:
                pass
        self._proses = self._keluaran = None

    def hentikan(self):
        if self._proses is not None:
            try:
                self._proses.kill()
                self._proses.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                pass
            self._selesai(False, None, "dihentikan")

    def tick(self, sid_registri):
        kini = self.jam()
        if self._proses is None:
            if kini < self._berikutnya:
                return
            if not self.perintah:
                self._selesai(False, None, "claude CLI tidak ditemukan di PATH")
                return
            try:
                self._keluaran = tempfile.TemporaryFile()
                self._proses = subprocess.Popen(self.perintah, stdout=self._keluaran, stderr=subprocess.DEVNULL,
                                                stdin=subprocess.DEVNULL,
                                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                self._mulai = kini
            except (OSError, ValueError) as e:
                self._selesai(False, None, "gagal menjalankan: %s" % e)
            return
        if self._proses.poll() is None:
            if kini - self._mulai > self.batas:
                try:
                    self._proses.kill()
                    self._proses.wait(timeout=5)
                except (OSError, subprocess.TimeoutExpired):
                    pass
                self._selesai(False, None, "melewati batas %s detik, dihentikan" % self.batas)
            return
        try:
            self._keluaran.seek(0)
            daftar = json.loads(self._keluaran.read().decode("utf-8", "replace") or "null")
        except (OSError, ValueError):
            daftar = None
        if not isinstance(daftar, list):
            self._selesai(False, None, "keluaran bukan daftar JSON (exit %s)" % self._proses.returncode)
            return
        milik = {str(x["sessionId"]) for x in daftar
                 if isinstance(x, dict) and x.get("sessionId") and di_dalam_workspace(x.get("cwd"), self.workspace)}
        self._tidak_cocok = 0 if milik == set(sid_registri) else self._tidak_cocok + 1
        self._selesai(True, self._tidak_cocok < TIDAK_COCOK_MAKS, "%d sesi menurut claude agents" % len(milik))


def perintah_agents():
    """[exe, 'agents', '--json'] atau None. Di Windows lewat shim npm .cmd, bukan .ps1 (tanpa spawn PowerShell)."""
    for nama in (("claude.cmd", "claude.exe") if os.name == "nt" else ("claude",)):
        p = shutil.which(nama)
        if p:
            return [p, "agents", "--json"]
    return None


def kunci_penulis(path):
    """Kunci eksklusif satu penulis per workspace, dipegang selama proses hidup dan dilepas OS saat proses mati.

    Sebelumnya hanya launcher yang memeriksa PID, jadi dua launcher pada detik yang sama bisa sama-sama
    menyalakan penulis. Mengembalikan berkas yang tetap terbuka, atau None bila kunci dipegang penulis lain."""
    try:
        f = open(path, "a+")
    except OSError:
        return None
    try:
        if os.name == "nt":
            import msvcrt
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return None
    return f


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
    ap.add_argument("--registri-dir", default=REGISTRI_DIR,
                    help="registri sesi Claude Code; folder yang tak terbaca = mode transkrip")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--sekali", action="store_true")
    mode.add_argument("--loop", type=float, metavar="DETIK")
    ap.add_argument("--sepi-menit", type=float, default=60.0)
    ap.add_argument("--cek-silang-detik", type=float, default=CEK_SILANG_DETIK,
                    help="selang cek silang claude agents --json; 0 = tanpa cek silang")
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
    cek = None
    # launcher memberi --log supaya proses lepas tak perlu mewarisi handle stdout/stderr siapa pun
    log = open(a.log, "a", encoding="utf-8") if a.log else None

    def catat(pesan, galat=False):
        tujuan = log or (sys.stderr if galat else sys.stdout)
        print("%s kantor-agent: %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), pesan), file=tujuan, flush=True)

    def satu_tick():
        t0 = time.perf_counter()
        data = kumpulkan(a.proyek_dir, workspace, datetime.now(timezone.utc), registri_dir=a.registri_dir)
        skema = data["skema"]
        if cek is not None and skema["sumber_hidup"] == "registri":
            cek.tick({s["id"] for s in data["sesi"] if s.get("status_proses") is not None})
            st = cek.status()
        else:
            st = {"dicek": False, "cocok": None, "catatan": "tidak dijalankan"}
        skema.update(registri_dicek=st["dicek"], registri_cocok=st["cocok"], registri_catatan=st["catatan"])
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

    kunci = kunci_penulis(os.path.join(keluaran, NAMA_KUNCI))
    if kunci is None:
        catat("penulis lain memegang kunci %s; tidak menyalakan yang kedua" % NAMA_KUNCI)
        if log:
            log.close()
        return 4
    if a.cek_silang_detik > 0:
        cek = CekSilang(perintah_agents(), workspace, interval_detik=a.cek_silang_detik)
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
        if cek is not None:
            cek.hentikan()
        _hapus_pid(path_pid)
        kunci.close()
        if log:
            log.close()


if __name__ == "__main__":
    sys.exit(main())
