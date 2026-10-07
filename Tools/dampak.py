#!/usr/bin/env python3
"""dampak.py -- kandidat dok vault dan berkas kode yang terdampak sebuah perubahan fakta.

Deterministik dan read-only. Skrip ini TIDAK memutuskan relevansi; itu tugas agent di
`/dampak`. Yang dijamin skrip: daftar kandidat sama setiap kali dijalankan atas keadaan
yang sama, dan tak ada yang dibuang diam-diam (semuanya tercatat di `dilewati`).

Spec: .agent-kit/docs/2026-10-07-dampak-command-design.md
"""
import re

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
