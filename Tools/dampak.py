#!/usr/bin/env python3
"""dampak.py -- kandidat dok vault dan berkas kode yang terdampak sebuah perubahan fakta.

Deterministik dan read-only. Skrip ini TIDAK memutuskan relevansi; itu tugas agent di
`/dampak`. Yang dijamin skrip: daftar kandidat sama setiap kali dijalankan atas keadaan
yang sama, dan tak ada yang dibuang diam-diam (semuanya tercatat di `dilewati`).

Spec: .agent-kit/docs/2026-10-07-dampak-command-design.md
"""
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vault_index.build import NAMA_INDEX, muat_index, pilih_yang_perlu_diringkas, scan_vault  # noqa: E402,F401

# Fakta yang cocok di lebih dari sekian berkas (vault, atau per repo kode) tak menunjuk
# apa pun dan hanya membanjiri laporan.
AMBANG_TERLALU_UMUM = 40

# Bukan dokumentasi arsitektur (rulebook vault §2), jadi tak pernah disunting /dampak.
JENIS_BUKAN_KANDIDAT = frozenset({"workspace", "log", "template"})

# mybharata-app dirilis dari `dev`, bukan `main`.
REPO_REF = (
    ("bip-erp", "origin/main"),
    ("erp-frontend", "origin/main"),
    ("mybharata-app", "origin/dev"),
)

_RE_BACKTICK = re.compile(r"`([^`\n]+)`")
# Garis miring pertama tak boleh didahului huruf/angka/titik/titik dua/garis miring:
# itu membuang URL (`https://...`) dan pecahan path di tengah kata.
_RE_RUTE = re.compile(r"(?<![\w.:/])/[A-Za-z0-9_\-:{}]+(?:/[A-Za-z0-9_\-:{}]+)*")
_RE_SNAKE = re.compile(r"\b[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+\b")
_RE_ANGKA = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)?(?![\w]|[.,]\d)")
_RE_ANGKA_PENUH = re.compile(r"\d+(?:[.,]\d+)?")


def adalah_angka(fakta: str) -> bool:
    return _RE_ANGKA_PENUH.fullmatch(fakta) is not None


def ekstrak_fakta(teks: str) -> tuple[list[str], list[dict]]:
    """Fakta literal dari teks perubahan: backtick, rute, snake_case, angka >= 2 digit."""
    fakta: list[str] = []
    dilewati: list[dict] = []

    def tambah(f: str) -> None:
        f = f.strip().rstrip(".,;:)")
        if f and f not in fakta:
            fakta.append(f)

    for m in _RE_BACKTICK.finditer(teks):
        tambah(m.group(1))
    sisa = _RE_BACKTICK.sub(" ", teks)
    for m in _RE_RUTE.finditer(sisa):
        tambah(m.group(0))
    for m in _RE_SNAKE.finditer(sisa):
        tambah(m.group(0))
    for m in _RE_ANGKA.finditer(sisa):
        angka = m.group(0)
        if sum(c.isdigit() for c in angka) >= 2:
            tambah(angka)
        else:
            catatan = {"jenis": "fakta", "nilai": angka, "alasan": "angka satu digit"}
            if catatan not in dilewati:
                dilewati.append(catatan)
    return fakta, dilewati


def _catat(alasan: dict[str, list[str]], path: str, sebab: str, per_path: dict,
           sumber_paths: list[str]) -> None:
    if path in sumber_paths or per_path[path]["jenis"] in JENIS_BUKAN_KANDIDAT:
        return
    daftar = alasan.setdefault(path, [])
    if sebab not in daftar:
        daftar.append(sebab)


def _tetangga(e: dict, entri: list[dict], per_judul: dict) -> tuple[set[str], set[str]]:
    keluar = {per_judul[t]["path"] for t in e["tautan"] if t in per_judul}
    masuk = {x["path"] for x in entri if e["judul"] in x["tautan"]}
    return keluar, masuk


def kandidat_graf(sumber_paths: list[str], entri: list[dict]) -> dict[str, list[str]]:
    """Tetangga wikilink satu lompatan; sumber ADR ditambah lompatan kedua."""
    per_path = {e["path"]: e for e in entri}
    per_judul = {e["judul"]: e for e in entri}
    alasan: dict[str, list[str]] = {}
    for sp in sumber_paths:
        e = per_path[sp]
        keluar, masuk = _tetangga(e, entri, per_judul)
        for p in sorted(keluar):
            _catat(alasan, p, "tautan", per_path, sumber_paths)
        for p in sorted(masuk):
            _catat(alasan, p, "backlink", per_path, sumber_paths)
        if e["jenis"] == "adr":
            for p1 in sorted(keluar | masuk):
                k2, m2 = _tetangga(per_path[p1], entri, per_judul)
                for p in sorted((k2 | m2) - keluar - masuk):
                    _catat(alasan, p, "adr-2hop", per_path, sumber_paths)
    return alasan


def _cocok_isi(fakta: str, isi: str) -> bool:
    if adalah_angka(fakta):
        pola = r"(?<![\d.,])" + re.escape(fakta) + r"(?![\d]|[.,]\d)"
        return re.search(pola, isi) is not None
    return fakta in isi


def kandidat_fakta_vault(fakta: list[str], entri: list[dict],
                         sumber_paths: list[str]) -> tuple[dict[str, list[str]], list[dict]]:
    """Dok vault lain yang menyatakan fakta literal yang sama."""
    per_path = {e["path"]: e for e in entri}
    alasan: dict[str, list[str]] = {}
    dilewati: list[dict] = []
    for f in fakta:
        cocok = [e["path"] for e in entri if _cocok_isi(f, e["_isi"])]
        if len(cocok) > AMBANG_TERLALU_UMUM:
            dilewati.append({"jenis": "fakta", "nilai": f,
                             "alasan": f"terlalu umum: {len(cocok)} dok vault"})
            continue
        for p in cocok:
            _catat(alasan, p, f"fakta:{f}", per_path, sumber_paths)
    return alasan, dilewati


def _env_bersih() -> dict[str, str]:
    """Buang seluruh GIT_*: dipanggil dari dalam hook git, variabel itu membelokkan `git -C`."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "core.fsmonitor=false", "-c", "core.quotePath=false", *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=_env_bersih(),
    )


def cari_kode(fakta: list[str], akar_repo: Path, repo_ref=REPO_REF) -> tuple[list[dict], list[dict]]:
    """Berkas kode yang memuat fakta, dibaca dari REF remote (bukan working tree, bukan ripgrep)."""
    kandidat: list[dict] = []
    dilewati: list[dict] = []
    for nama, ref in repo_ref:
        repo = akar_repo / nama
        if not (repo / ".git").exists():
            dilewati.append({"jenis": "repo", "nilai": nama, "alasan": "folder tidak ada atau bukan repo git"})
            continue
        if _git(repo, "rev-parse", "--verify", "--quiet", ref).returncode != 0:
            dilewati.append({"jenis": "repo", "nilai": nama, "alasan": f"ref {ref} tidak ada"})
            continue
        for f in fakta:
            # -a: berkas ber-byte NUL tetap dibaca sebagai teks (ripgrep melewatinya senyap).
            args = ["grep", "-n", "-a", "-F"] + (["-w"] if adalah_angka(f) else []) + ["-e", f, ref, "--"]
            r = _git(repo, *args)
            if r.returncode not in (0, 1):
                dilewati.append({"jenis": "kode", "nilai": f"{nama}:{f}",
                                 "alasan": "git grep gagal: " + r.stderr.strip()[:200]})
                continue
            per_berkas: dict[str, int] = {}
            awalan = ref + ":"
            for baris in r.stdout.splitlines():
                if not baris.startswith(awalan):
                    continue
                berkas, nomor, _ = baris[len(awalan):].split(":", 2)
                per_berkas.setdefault(berkas, int(nomor))
            if len(per_berkas) > AMBANG_TERLALU_UMUM:
                dilewati.append({"jenis": "fakta", "nilai": f,
                                 "alasan": f"terlalu umum: {len(per_berkas)} berkas di {nama}"})
                continue
            for berkas, nomor in sorted(per_berkas.items()):
                kandidat.append({"repo": nama, "ref": ref, "berkas": berkas, "baris": nomor, "fakta": f})
    return kandidat, dilewati
