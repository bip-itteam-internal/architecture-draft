#!/usr/bin/env python3
"""dampak.py -- kandidat dok vault dan berkas kode yang terdampak sebuah perubahan fakta.

Deterministik dan read-only. Skrip ini TIDAK memutuskan relevansi; itu tugas agent di
`/dampak`. Yang dijamin skrip: daftar kandidat sama setiap kali dijalankan atas keadaan
yang sama, dan tak ada yang dibuang diam-diam (semuanya tercatat di `dilewati`).

Spec: .agent-kit/docs/2026-10-07-dampak-command-design.md
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vault_index.build import NAMA_INDEX, muat_index, pilih_yang_perlu_diringkas, scan_vault  # noqa: E402

# Fakta yang cocok di lebih dari sekian berkas (vault, atau per repo kode) tak menunjuk
# apa pun dan hanya membanjiri laporan.
AMBANG_TERLALU_UMUM = 40

# Fakta bukan angka yang lebih pendek dari ini dicatat `terlalu pendek`, tidak dicari.
PANJANG_MIN_FAKTA = 3

# Di atas sekian fakta, pencarian kode dilewati (tercatat). Diukur 2026-10-07: 33-67 fakta
# 26-27 dtk, tetapi 228 fakta 9 menit dan 344 fakta 57 menit. Diff sebesar itu dipersempit
# per dok (`--diff PATH`), bukan ditunggu.
BATAS_FAKTA_KODE = 60

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
# Angka berpemisah ganda (Rupiah 1.500.000, versi 1.36.0, tanggal 2026-09-07) adalah SATU fakta.
# Boleh didahului huruf (Rp1.500.000); diambil sebelum _RE_ANGKA supaya tak terpecah atau hilang.
_RE_ANGKA_MAJEMUK = re.compile(r"(?<![\d.,-])\d+(?:[.,-]\d+){2,}(?!\d|[.,-]\d)")
_RE_ANGKA = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)?(?![\w]|[.,]\d)")
_RE_ANGKA_PENUH = re.compile(r"\d+(?:[.,-]\d+)*")


def adalah_angka(fakta: str) -> bool:
    return _RE_ANGKA_PENUH.fullmatch(fakta) is not None


def ekstrak_fakta(teks: str) -> tuple[list[str], list[dict]]:
    """Fakta literal dari teks perubahan: backtick, rute, snake_case, angka >= 2 digit."""
    fakta: list[str] = []
    dilewati: list[dict] = []

    def tambah(f: str) -> None:
        f = f.strip().rstrip(".,;:)")
        if not f or f in fakta:
            return
        # Fakta bukan angka yang pendek atau tanpa huruf/angka (`/`, `_`, `id`) cocok di ratusan
        # ribu baris kode: diukur 2026-10-07, dua fakta begitu membuat satu grep bip-erp 385 dtk.
        if not adalah_angka(f) and (len(f) < PANJANG_MIN_FAKTA or not any(c.isalnum() for c in f)):
            catatan = {"jenis": "fakta", "nilai": f, "alasan": "terlalu pendek"}
            if catatan not in dilewati:
                dilewati.append(catatan)
            return
        fakta.append(f)

    for m in _RE_BACKTICK.finditer(teks):
        tambah(m.group(1))
    sisa = _RE_BACKTICK.sub(" ", teks)
    for m in _RE_RUTE.finditer(sisa):
        tambah(m.group(0))
    for m in _RE_SNAKE.finditer(sisa):
        tambah(m.group(0))
    for m in _RE_ANGKA_MAJEMUK.finditer(sisa):
        tambah(m.group(0))
    sisa = _RE_ANGKA_MAJEMUK.sub(" ", sisa)
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
    """Tetangga wikilink satu lompatan, untuk sumber jenis apa pun.

    Sengaja tanpa lompatan kedua: graf vault padat (median derajat 12, hub sampai 202), jadi dua
    lompatan dari satu ADR menyapu ratusan dok. Dok jauh yang benar-benar memuat fakta yang
    berubah ditangkap kandidat_fakta_vault, bukan graf.
    """
    per_path = {e["path"]: e for e in entri}
    per_judul = {e["judul"]: e for e in entri}
    alasan: dict[str, list[str]] = {}
    for sp in sumber_paths:
        keluar, masuk = _tetangga(per_path[sp], entri, per_judul)
        for p in sorted(keluar):
            _catat(alasan, p, "tautan", per_path, sumber_paths)
        for p in sorted(masuk):
            _catat(alasan, p, "backlink", per_path, sumber_paths)
    return alasan


def _cocok_isi(fakta: str, isi: str) -> bool:
    if adalah_angka(fakta):
        pola = r"(?<![\d.,-])" + re.escape(fakta) + r"(?!\d|[.,-]\d)"
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
    if len(fakta) > BATAS_FAKTA_KODE:
        dilewati.append({"jenis": "kode", "nilai": "semua repo",
                         "alasan": f"{len(fakta)} fakta melebihi batas {BATAS_FAKTA_KODE}: "
                                   "persempit dengan --diff PATH per dok"})
        return kandidat, dilewati
    for nama, ref in repo_ref:
        repo = akar_repo / nama
        if not (repo / ".git").exists():
            dilewati.append({"jenis": "repo", "nilai": nama, "alasan": "folder tidak ada atau bukan repo git"})
            continue
        if _git(repo, "rev-parse", "--verify", "--quiet", ref).returncode != 0:
            dilewati.append({"jenis": "repo", "nilai": nama, "alasan": f"ref {ref} tidak ada"})
            continue
        # fakta -> berkas -> baris pertama yang BENAR-BENAR cocok
        per_fakta: dict[str, dict[str, int]] = {f: {} for f in fakta}
        for kelompok, kata_utuh in (([f for f in fakta if adalah_angka(f)], True),
                                    ([f for f in fakta if not adalah_angka(f)], False)):
            if not kelompok:
                continue
            baris_cocok, galat = _grep_kelompok(repo, ref, kelompok, kata_utuh)
            if galat:
                dilewati.append({"jenis": "kode", "nilai": nama, "alasan": "git grep gagal: " + galat})
                continue
            for berkas, nomor, isi in baris_cocok:
                for f in kelompok:
                    # -w git grep menganggap "." batas kata (80 cocok di 80.5): saring ulang di sini.
                    if _cocok_isi(f, isi):
                        per_fakta[f].setdefault(berkas, nomor)
        for f in fakta:
            per_berkas = per_fakta[f]
            if len(per_berkas) > AMBANG_TERLALU_UMUM:
                dilewati.append({"jenis": "fakta", "nilai": f,
                                 "alasan": f"terlalu umum: {len(per_berkas)} berkas di {nama}"})
                continue
            for berkas, nomor in sorted(per_berkas.items()):
                kandidat.append({"repo": nama, "ref": ref, "berkas": berkas, "baris": nomor, "fakta": f})
    return kandidat, dilewati


def _grep_kelompok(repo: Path, ref: str, pola: list[str],
                   kata_utuh: bool) -> tuple[list[tuple[str, int, str]], str | None]:
    """SATU git grep untuk banyak pola (lewat berkas -f): satu grep per fakta terukur +-4 dtk
    per fakta di repo nyata, dan satu commit docs bisa membawa ratusan fakta."""
    # newline="\n": di Windows mode teks menulis CRLF, dan git membaca \r sebagai bagian polanya.
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", suffix=".pola", delete=False) as t:
        t.write("\n".join(pola) + "\n")
        berkas_pola = t.name
    try:
        # -a: berkas ber-byte NUL tetap dibaca sebagai teks (ripgrep melewatinya senyap).
        args = ["grep", "-n", "-a", "-F"] + (["-w"] if kata_utuh else []) + ["-f", berkas_pola, ref, "--"]
        r = _git(repo, *args)
    finally:
        os.unlink(berkas_pola)
    if r.returncode not in (0, 1):
        return [], r.stderr.strip()[:200]
    hasil: list[tuple[str, int, str]] = []
    awalan = ref + ":"
    for baris in r.stdout.splitlines():
        if not baris.startswith(awalan):
            continue
        berkas, nomor, isi = baris[len(awalan):].split(":", 2)
        hasil.append((berkas, int(nomor), isi))
    return hasil, None


def resolusi_sumber(nilai: str, entri: list[dict]) -> str | None:
    """Judul, path relatif, dengan/tanpa .md, garis miring apa pun."""
    n = nilai.replace("\\", "/").strip()
    if n.endswith(".md"):
        n = n[:-3]
    for e in entri:
        if e["path"][:-3] == n or e["judul"] == n:
            return e["path"]
    return None


def path_relatif_vault(nilai: str, root: Path) -> str | None:
    """PATH relatif-vault, relatif-CWD (mis. `architecture-draft/...` dari akar erp/), atau absolut.

    Relatif-CWD hanya dipakai bila berkasnya ADA: CWD bisa berada di dalam vault (mis. `Tools/`),
    dan tanpa syarat itu path relatif-vault terbaca sebagai `Tools/<path>`. Selain itu dibaca
    relatif-vault. Di luar vault -> None (galat bernama, bukan "tak ada perubahan").
    """
    p = Path(nilai)
    if p.is_absolute():
        calon = [p]
    else:
        dari_cwd = Path.cwd() / p
        calon = ([dari_cwd] if dari_cwd.exists() else []) + [root / p]
    for c in calon:
        try:
            return c.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
    return None


def dari_diff(vault: Path, paths: list[str]) -> tuple[list[str], str]:
    """Dok yang berubah di working tree vs HEAD (plus yang belum dilacak), dan baris +/- nya."""
    spec = paths or ["*.md"]
    r = _git(vault, "diff", "HEAD", "-U0", "--", *spec)
    berkas: list[str] = []
    baris: list[str] = []
    for b in r.stdout.splitlines():
        if b.startswith("+++ b/"):
            berkas.append(b[6:].rstrip("\t"))   # git bisa menambah TAB di header path berspasi
        elif b.startswith(("+++", "---")):
            continue
        elif b.startswith(("+", "-")):
            baris.append(b[1:])
    baru = _git(vault, "ls-files", "--others", "--exclude-standard", "--", *spec)
    for p in baru.stdout.splitlines():
        berkas.append(p)
        baris.append((vault / p).read_text(encoding="utf-8"))
    return berkas, "\n".join(baris)


def index_segar(root: Path, entri: list[dict]) -> bool:
    """Aturan yang sama dengan `build-vault-index.py --check`, dipakai ulang, bukan disalin."""
    return not pilih_yang_perlu_diringkas(entri, muat_index(root / NAMA_INDEX), full=False)


def analisa(root: Path, akar_repo: Path, sumber_paths: list[str], teks: str, entri: list[dict]) -> dict:
    per_path = {e["path"]: e for e in entri}
    fakta, dilewati = ekstrak_fakta(teks)
    alasan = kandidat_graf(sumber_paths, entri)
    alasan_fakta, dil_vault = kandidat_fakta_vault(fakta, entri, sumber_paths)
    for p, daftar in alasan_fakta.items():
        for a in daftar:
            if a not in alasan.setdefault(p, []):
                alasan[p].append(a)
    kode, dil_kode = cari_kode(fakta, akar_repo)
    return {
        "sumber": sumber_paths,
        "fakta": fakta,
        "kandidat_dok": [{"path": p, "alasan": alasan[p], "status_emoji": per_path[p]["status_emoji"]}
                         for p in sorted(alasan)],
        "kandidat_kode": kode,
        "dilewati": dilewati + dil_vault + dil_kode,
        "index_segar": index_segar(root, entri),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kandidat dok vault dan kode yang terdampak perubahan fakta.")
    ap.add_argument("--root", required=True, help="akar vault architecture-draft")
    ap.add_argument("--repo-root", help="folder berisi repo kode (default: induk --root)")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--sumber", help="judul atau path dok yang akan diubah")
    mode.add_argument("--diff", nargs="*", metavar="PATH",
                      help="dok yang berubah vs HEAD; PATH membatasi (pohon vault dipakai bersama)")
    ap.add_argument("--teks", help="perubahan yang dimaksud (wajib bersama --sumber)")
    a = ap.parse_args(argv)

    root = Path(a.root).resolve()
    akar_repo = Path(a.repo_root).resolve() if a.repo_root else root.parent
    entri = scan_vault(root)

    if a.sumber is not None:
        if not a.teks:
            ap.error("--sumber butuh --teks")
        sp = resolusi_sumber(a.sumber, entri)
        if sp is None:
            print(f"sumber tidak ditemukan di vault: {a.sumber}", file=sys.stderr)
            return 2
        sumber, teks = [sp], a.teks
    else:
        paths = []
        for p in a.diff:
            rel = path_relatif_vault(p, root)
            if rel is None:
                print(f"PATH di luar vault {root}: {p}", file=sys.stderr)
                return 2
            paths.append(rel)
        berkas, teks = dari_diff(root, paths)
        dikenal = {e["path"] for e in entri}
        sumber = [b for b in berkas if b in dikenal]
        if not sumber:
            print("tidak ada dok vault yang berubah", file=sys.stderr)
            return 2

    hasil = analisa(root, akar_repo, sumber, teks, entri)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(hasil, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
