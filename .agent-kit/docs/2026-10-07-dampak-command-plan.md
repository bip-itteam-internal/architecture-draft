# `/dampak` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Command `/dampak` yang, sebelum fakta di vault diubah, mendaftar dok vault dan berkas kode yang ikut terdampak, lalu menerapkan suntingan dok yang disetujui user.

**Architecture:** Skrip deterministik read-only `Tools/dampak.py` menghitung kandidat dari graf wikilink (`scan_vault`), fakta literal di vault, dan `git grep` atas ref remote tiga repo kode; keluarannya JSON. Command `commands/dampak.md` menyuruh agent menilai kandidat, menyajikan laporan, berhenti, lalu menerapkan suntingan yang disetujui. `/analisa-kebutuhan` dan `/sync-docs` memanggilnya dengan satu langkah masing-masing.

**Tech Stack:** Python 3 (venv `architecture-draft/Tools/.venv`), pytest, git CLI, Markdown command agent-kit, PowerShell (`tests/test-init.ps1`).

**Spec:** `architecture-draft/.agent-kit/docs/2026-10-07-dampak-command-design.md`

## Global Constraints

- Skrip **read-only**: tak menulis berkas apa pun, tak menjalankan git yang mengubah keadaan.
- `AMBANG_TERLALU_UMUM = 40` (berkas), konstanta bernama, satu tempat.
- Ref kode: `bip-erp` → `origin/main`, `erp-frontend` → `origin/main`, `mybharata-app` → `origin/dev`.
- Kode dicari dengan `git grep` atas **ref**, bukan working tree, dengan `-a` (berkas ber-byte NUL tetap terbaca) dan `-c core.fsmonitor=false`.
- Semua `GIT_*` dibuang dari env anak proses (skrip bisa terpanggil dari dalam hook git; lihat `hooks/gerbang-kit.py` `env_bersih`).
- Jenis dok yang tak pernah jadi kandidat: `workspace`, `log`, `template`.
- Tak ada yang dibuang diam-diam: fakta/repo yang dilewati masuk `dilewati` beserta alasannya.
- Index basi → `index_segar: false`, exit 0.
- Commit vault: stage **per nama berkas**, pesan `docs(kit): ...` / `feat(kit): ...`, **tanpa** trailer `Co-Authored-By`.
- Run test dari `architecture-draft/Tools` dengan `.venv\Scripts\python.exe -m pytest ...` lewat **PowerShell** (tool Bash tidak dipakai di mesin ini).
- Kit naik ke `1.36.0`.

## Review Focus

1. **Sumber disebut dengan berbagai bentuk** (judul, path relatif, dengan/tanpa `.md`, backslash Windows) → semuanya teresolusi ke dok yang sama; yang tak ada → exit 2 dengan pesan jelas. Test di Task 5.
2. **Angka di dalam angka lain** (`80` vs `8080`, `800`, `80.5`) → tidak cocok, baik di vault maupun di kode. Test di Task 3 dan Task 4.
3. **Teks perubahan tanpa satu pun fakta** → `fakta: []`, kandidat graf tetap keluar, exit 0. Test di Task 5.
4. **Pohon vault dipakai bersama sesi lain**: `--diff PATH` hanya membaca dok yang disebut, dok tak-ter-commit milik sesi lain tidak ikut. Test di Task 5.
5. **Keluaran non-ASCII di Windows** (emoji status, nama berkas berspasi) → JSON valid UTF-8 di stdout. Test di Task 5.

---

### Task 1: Ekstraksi fakta

**Files:**
- Create: `architecture-draft/Tools/dampak.py`
- Test: `architecture-draft/Tools/tests/test_dampak.py`

**Interfaces:**
- Produces: `ekstrak_fakta(teks: str) -> tuple[list[str], list[dict]]` (fakta berurutan unik; `dilewati` berisi `{"jenis","nilai","alasan"}`), `adalah_angka(fakta: str) -> bool`, konstanta `AMBANG_TERLALU_UMUM`, `JENIS_BUKAN_KANDIDAT`, `REPO_REF`.

- [ ] **Step 1: Tulis test yang gagal**

```python
"""Test dampak.py. Spec: .agent-kit/docs/2026-10-07-dampak-command-design.md"""
import json
import os
import subprocess
from pathlib import Path

import pytest

import dampak
from dampak import adalah_angka, ekstrak_fakta


def test_ekstrak_empat_bentuk_fakta():
    fakta, dilewati = ekstrak_fakta(
        "ambang `target_profit` dari 80 jadi 75 di /kpi/template, batas 5 hari, field ads_cost"
    )
    assert set(fakta) == {"target_profit", "/kpi/template", "80", "75", "ads_cost"}
    assert {"jenis": "fakta", "nilai": "5", "alasan": "angka satu digit"} in dilewati


def test_ekstrak_url_bukan_rute():
    fakta, _ = ekstrak_fakta("lihat https://github.com/org/repo")
    assert not any(f.startswith("/") for f in fakta)


def test_ekstrak_tanpa_fakta():
    assert ekstrak_fakta("ubah kalimat pembuka saja") == ([], [])


def test_ekstrak_unik_dan_tanpa_tanda_baca_ekor():
    fakta, _ = ekstrak_fakta("80, lalu 80. Rute /a/b.")
    assert fakta == ["/a/b", "80"]


def test_adalah_angka():
    assert adalah_angka("80") and adalah_angka("1,5") and adalah_angka("12.5")
    assert not adalah_angka("target_profit") and not adalah_angka("/kpi")
```

- [ ] **Step 2: Jalankan, pastikan gagal**

Run (PowerShell, dari `architecture-draft\Tools`): `.\.venv\Scripts\python.exe -m pytest tests/test_dampak.py -q`
Expected: FAIL `ModuleNotFoundError: No module named 'dampak'`

- [ ] **Step 3: Implementasi minimal**

`Tools/dampak.py`:

```python
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
```

- [ ] **Step 4: Jalankan, pastikan lolos**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_dampak.py -q`
Expected: 5 passed. (Catatan: di `test_ekstrak_unik_dan_tanpa_tanda_baca_ekor` urutannya rute dulu baru angka, karena ekstraksi berjalan per bentuk.)

- [ ] **Step 5: Commit**

```powershell
git -c core.fsmonitor=false -C architecture-draft add -- "Tools/dampak.py" "Tools/tests/test_dampak.py"
git -c core.fsmonitor=false -C architecture-draft commit -m "feat(kit): dampak.py ekstraksi fakta"
```

---

### Task 2: Kandidat graf

**Files:**
- Modify: `architecture-draft/Tools/dampak.py`
- Test: `architecture-draft/Tools/tests/test_dampak.py`

**Interfaces:**
- Consumes: `scan_vault(root: Path) -> list[dict]` dari `vault_index.build` (entri ber-field `path`, `judul`, `jenis`, `status_emoji`, `tautan`, `_isi`); `JENIS_BUKAN_KANDIDAT`.
- Produces: `kandidat_graf(sumber_paths: list[str], entri: list[dict]) -> dict[str, list[str]]` (path → daftar alasan dari `"tautan"`, `"backlink"`, `"adr-2hop"`), dan fixture `vault_mini`.

- [ ] **Step 1: Tulis test yang gagal** (tambahkan ke `test_dampak.py`)

```python
from vault_index.build import scan_vault

ADR = "Decisions/ADR - 0079 Target Profit.md"
INSENTIF = "Finance System/Finance - Insentif.md"
KPI = "Human Resource Information System/HRIS - KPI.md"
CUTI = "Human Resource Information System/HRIS - Cuti.md"
ANALISA = "Workspace/ANALISA - Target.md"
RUN = "Runbooks/RUN - Lain.md"


@pytest.fixture
def vault_mini(tmp_path: Path) -> Path:
    v = tmp_path / "architecture-draft"
    isi = {
        ADR: "- **Status**: ✅ Diterima\n\nAmbang `target_profit` 80. Lihat [[Finance - Insentif]].\n",
        INSENTIF: "- **Status**: ✅ Implemented\n\nTarget 80 dari [[ADR - 0079 Target Profit]]. "
                  "Lihat [[HRIS - KPI]].\n",
        KPI: "- **Status**: ⚠️ Implemented\n\nAmbang KPI 80. [[Finance - Insentif]]\n",
        CUTI: "- **Status**: ✅ Implemented\n\nTidak terkait, port 8080, batas 800, rasio 80.5.\n",
        ANALISA: "[[ADR - 0079 Target Profit]] 80\n",
        RUN: "> **Status**: ✅\n\n[[HRIS - KPI]]\n",
    }
    for rel, teks in isi.items():
        p = v / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(teks, encoding="utf-8")
    return v


def test_graf_adr_dua_lompatan(vault_mini):
    hasil = dampak.kandidat_graf([ADR], scan_vault(vault_mini))
    assert set(hasil[INSENTIF]) == {"tautan", "backlink"}
    assert "adr-2hop" in hasil[KPI]
    assert ANALISA not in hasil          # Workspace tak pernah kandidat
    assert ADR not in hasil              # sumber bukan kandidat
    assert RUN not in hasil              # tiga lompatan


def test_graf_non_adr_satu_lompatan(vault_mini):
    hasil = dampak.kandidat_graf([INSENTIF], scan_vault(vault_mini))
    assert set(hasil) == {ADR, KPI}
    assert RUN not in hasil


def test_graf_dok_yatim(vault_mini):
    assert dampak.kandidat_graf([CUTI], scan_vault(vault_mini)) == {}
```

- [ ] **Step 2: Jalankan, pastikan gagal**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_dampak.py -q`
Expected: 3 FAIL `AttributeError: module 'dampak' has no attribute 'kandidat_graf'`

- [ ] **Step 3: Implementasi**

Tambahkan ke `dampak.py` (impor di atas, fungsi di bawah `ekstrak_fakta`):

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vault_index.build import NAMA_INDEX, muat_index, pilih_yang_perlu_diringkas, scan_vault  # noqa: E402
```

```python
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
```

- [ ] **Step 4: Jalankan, pastikan lolos**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_dampak.py -q`
Expected: 8 passed

- [ ] **Step 5: Commit**

```powershell
git -c core.fsmonitor=false -C architecture-draft add -- "Tools/dampak.py" "Tools/tests/test_dampak.py"
git -c core.fsmonitor=false -C architecture-draft commit -m "feat(kit): dampak.py kandidat graf wikilink"
```

---

### Task 3: Fakta di vault

**Files:**
- Modify: `architecture-draft/Tools/dampak.py`
- Test: `architecture-draft/Tools/tests/test_dampak.py`

**Interfaces:**
- Consumes: `_catat`, `adalah_angka`, `AMBANG_TERLALU_UMUM`, fixture `vault_mini`.
- Produces: `kandidat_fakta_vault(fakta: list[str], entri: list[dict], sumber_paths: list[str]) -> tuple[dict[str, list[str]], list[dict]]` (alasan berbentuk `"fakta:<f>"`).

- [ ] **Step 1: Tulis test yang gagal**

```python
def test_fakta_vault_angka_utuh(vault_mini):
    alasan, dilewati = dampak.kandidat_fakta_vault(["80"], scan_vault(vault_mini), [ADR])
    assert set(alasan) == {INSENTIF, KPI}       # CUTI punya 8080/800/80.5: bukan 80
    assert alasan[KPI] == ["fakta:80"]
    assert dilewati == []


def test_fakta_vault_terlalu_umum(vault_mini, monkeypatch):
    monkeypatch.setattr(dampak, "AMBANG_TERLALU_UMUM", 1)
    alasan, dilewati = dampak.kandidat_fakta_vault(["80"], scan_vault(vault_mini), [ADR])
    assert alasan == {}
    assert dilewati[0]["nilai"] == "80" and dilewati[0]["alasan"].startswith("terlalu umum")
```

- [ ] **Step 2: Jalankan, pastikan gagal**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_dampak.py -q`
Expected: 2 FAIL `AttributeError: ... 'kandidat_fakta_vault'`

- [ ] **Step 3: Implementasi**

```python
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
```

- [ ] **Step 4: Jalankan, pastikan lolos**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_dampak.py -q`
Expected: 10 passed

- [ ] **Step 5: Commit**

```powershell
git -c core.fsmonitor=false -C architecture-draft add -- "Tools/dampak.py" "Tools/tests/test_dampak.py"
git -c core.fsmonitor=false -C architecture-draft commit -m "feat(kit): dampak.py fakta literal di vault"
```

---

### Task 4: Fakta di kode lewat `git grep` ref remote

**Files:**
- Modify: `architecture-draft/Tools/dampak.py`
- Test: `architecture-draft/Tools/tests/test_dampak.py`

**Interfaces:**
- Consumes: `REPO_REF`, `AMBANG_TERLALU_UMUM`, `adalah_angka`.
- Produces: `cari_kode(fakta: list[str], akar_repo: Path, repo_ref=REPO_REF) -> tuple[list[dict], list[dict]]` (kandidat `{"repo","ref","berkas","baris","fakta"}`), `_git(repo: Path, *args) -> subprocess.CompletedProcess`, fixture `repos`.

- [ ] **Step 1: Tulis test yang gagal**

```python
def _git_uji(repo: Path, *args: str) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=uji", "-c", "user.email=uji@example.invalid",
                    "-c", "core.autocrlf=false", *args], check=True, capture_output=True, env=env)


@pytest.fixture
def repos(tmp_path: Path) -> Path:
    """Akar berisi bip-erp saja; origin/main = commit pertama."""
    akar = tmp_path / "repos"
    be = akar / "bip-erp"
    be.mkdir(parents=True)
    _git_uji(be, "init", "-q")
    (be / "a.go").write_text("x := target_profit\nambang := 80\n", encoding="utf-8")
    (be / "nul.go").write_bytes(b"\x00\x01\nvar y = target_profit\n")
    (be / "port.go").write_text("port := 8080\n", encoding="utf-8")
    (be / "wt.go").write_text("kosong\n", encoding="utf-8")
    _git_uji(be, "add", "-A")
    _git_uji(be, "commit", "-q", "-m", "awal")
    _git_uji(be, "update-ref", "refs/remotes/origin/main", "HEAD")
    # perubahan yang hanya ada di working tree: TIDAK boleh terbaca
    (be / "wt.go").write_text("z := target_profit\n", encoding="utf-8")
    return akar


def test_kode_membaca_ref_bukan_working_tree(repos):
    kandidat, _ = dampak.cari_kode(["target_profit"], repos)
    berkas = {k["berkas"] for k in kandidat}
    assert berkas == {"a.go", "nul.go"}
    assert all(k["ref"] == "origin/main" and k["repo"] == "bip-erp" for k in kandidat)


def test_kode_berkas_nul_tetap_ditemukan(repos):
    kandidat, _ = dampak.cari_kode(["target_profit"], repos)
    nul = [k for k in kandidat if k["berkas"] == "nul.go"]
    assert nul and nul[0]["baris"] == 2


def test_kode_angka_utuh(repos):
    kandidat, _ = dampak.cari_kode(["80"], repos)
    assert {k["berkas"] for k in kandidat} == {"a.go"}


def test_kode_repo_atau_ref_tak_ada(repos):
    _, dilewati = dampak.cari_kode(["target_profit"], repos)
    nilai = {d["nilai"]: d["alasan"] for d in dilewati if d["jenis"] == "repo"}
    assert set(nilai) == {"erp-frontend", "mybharata-app"}
    _, dilewati2 = dampak.cari_kode(["target_profit"], repos, (("bip-erp", "origin/dev"),))
    assert dilewati2 == [{"jenis": "repo", "nilai": "bip-erp", "alasan": "ref origin/dev tidak ada"}]


def test_kode_terlalu_umum(repos, monkeypatch):
    monkeypatch.setattr(dampak, "AMBANG_TERLALU_UMUM", 1)
    kandidat, dilewati = dampak.cari_kode(["target_profit"], repos)
    assert kandidat == []
    assert any(d["nilai"] == "target_profit" and d["alasan"].startswith("terlalu umum") for d in dilewati)
```

- [ ] **Step 2: Jalankan, pastikan gagal**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_dampak.py -q`
Expected: 5 FAIL `AttributeError: ... 'cari_kode'`

- [ ] **Step 3: Implementasi**

```python
import os
import subprocess


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
```

- [ ] **Step 4: Jalankan, pastikan lolos**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_dampak.py -q`
Expected: 15 passed

- [ ] **Step 5: Kontrol negatif** (jangan di-commit; kembalikan dengan menyunting ulang, BUKAN `git checkout --` yang membuang kerja belum ter-commit)

1. Ganti `ref, "--"]` jadi `"--"]` (grep working tree). Run test → `test_kode_membaca_ref_bukan_working_tree` **merah** (`wt.go` muncul). Kembalikan.
2. Hapus `"-a", ` dari `args`. Run test → `test_kode_berkas_nul_tetap_ditemukan` **merah**. Kembalikan.
3. Run test lagi → 15 passed. Catat hasil kedua kontrol di pesan commit.

- [ ] **Step 6: Commit**

```powershell
git -c core.fsmonitor=false -C architecture-draft add -- "Tools/dampak.py" "Tools/tests/test_dampak.py"
git -c core.fsmonitor=false -C architecture-draft commit -m "feat(kit): dampak.py fakta di kode via git grep ref remote" -m "Kontrol negatif: grep working tree -> test ref merah; tanpa -a -> test NUL merah."
```

---

### Task 5: CLI, mode `--diff`, kesegaran index, keluaran JSON

**Files:**
- Modify: `architecture-draft/Tools/dampak.py`
- Test: `architecture-draft/Tools/tests/test_dampak.py`

**Interfaces:**
- Consumes: semua fungsi Task 1-4; `muat_index`, `pilih_yang_perlu_diringkas`, `NAMA_INDEX`.
- Produces: `resolusi_sumber(nilai: str, entri: list[dict]) -> str | None`, `dari_diff(vault: Path, paths: list[str]) -> tuple[list[str], str]`, `index_segar(root: Path, entri: list[dict]) -> bool`, `analisa(root, akar_repo, sumber_paths, teks, entri) -> dict`, `main(argv: list[str] | None = None) -> int`. Bentuk JSON persis spec §3 Output.

- [ ] **Step 1: Tulis test yang gagal**

```python
@pytest.mark.parametrize("nilai", [
    "ADR - 0079 Target Profit",
    "Decisions/ADR - 0079 Target Profit.md",
    "Decisions/ADR - 0079 Target Profit",
    "Decisions\\ADR - 0079 Target Profit.md",
])
def test_resolusi_sumber(vault_mini, nilai):
    assert dampak.resolusi_sumber(nilai, scan_vault(vault_mini)) == ADR


def test_resolusi_sumber_tak_ada(vault_mini):
    assert dampak.resolusi_sumber("ADR - 9999 Hantu", scan_vault(vault_mini)) is None


def _jalankan(capsys, argv):
    kode = dampak.main(argv)
    keluar = capsys.readouterr().out
    return kode, (json.loads(keluar) if kode == 0 else keluar)


def test_main_sumber_utuh(vault_mini, repos, capsys):
    kode, hasil = _jalankan(capsys, ["--root", str(vault_mini), "--repo-root", str(repos),
                                     "--sumber", "ADR - 0079 Target Profit",
                                     "--teks", "ambang `target_profit` dari 80 jadi 75"])
    assert kode == 0
    assert hasil["sumber"] == [ADR]
    assert {"target_profit", "80", "75"} <= set(hasil["fakta"])
    dok = {d["path"]: d for d in hasil["kandidat_dok"]}
    assert "tautan" in dok[INSENTIF]["alasan"] and "fakta:80" in dok[INSENTIF]["alasan"]
    # ekstrak_status bisa menyertakan variation selector; cukup pastikan emoji non-ASCII selamat lewat JSON
    assert dok[KPI]["status_emoji"] and dok[KPI]["status_emoji"].startswith("⚠")
    assert {k["berkas"] for k in hasil["kandidat_kode"]} >= {"a.go", "nul.go"}
    assert hasil["index_segar"] is False         # fixture tak punya VAULT-INDEX.json
    assert set(hasil) == {"sumber", "fakta", "kandidat_dok", "kandidat_kode", "dilewati", "index_segar"}


def test_main_tanpa_fakta(vault_mini, repos, capsys):
    kode, hasil = _jalankan(capsys, ["--root", str(vault_mini), "--repo-root", str(repos),
                                     "--sumber", "Finance - Insentif", "--teks", "rapikan kalimat"])
    assert kode == 0 and hasil["fakta"] == [] and hasil["kandidat_kode"] == []
    assert {d["path"] for d in hasil["kandidat_dok"]} == {ADR, KPI}


def test_main_sumber_tak_ada(vault_mini, repos, capsys):
    assert dampak.main(["--root", str(vault_mini), "--repo-root", str(repos),
                        "--sumber", "Hantu", "--teks", "80"]) == 2


@pytest.fixture
def vault_git(vault_mini) -> Path:
    _git_uji(vault_mini, "init", "-q")
    _git_uji(vault_mini, "add", "-A")
    _git_uji(vault_mini, "commit", "-q", "-m", "awal")
    return vault_mini


def test_main_diff_dibatasi_path(vault_git, repos, capsys):
    (vault_git / KPI).write_text("- **Status**: ⚠️ Implemented\n\nAmbang KPI 75. [[Finance - Insentif]]\n",
                                 encoding="utf-8")
    # dok milik "sesi lain" yang belum di-commit: tak boleh ikut bila PATH disebut
    (vault_git / CUTI).write_text("- **Status**: ✅ Implemented\n\nbatas 99\n", encoding="utf-8")
    kode, hasil = _jalankan(capsys, ["--root", str(vault_git), "--repo-root", str(repos), "--diff", KPI])
    assert kode == 0
    assert hasil["sumber"] == [KPI]
    assert "75" in hasil["fakta"] and "80" in hasil["fakta"] and "99" not in hasil["fakta"]


def test_main_diff_tanpa_perubahan(vault_git, repos, capsys):
    assert dampak.main(["--root", str(vault_git), "--repo-root", str(repos), "--diff"]) == 2
```

- [ ] **Step 2: Jalankan, pastikan gagal**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_dampak.py -q`
Expected: FAIL `AttributeError: ... 'resolusi_sumber'` / `'main'`

- [ ] **Step 3: Implementasi**

```python
import argparse
import json


def resolusi_sumber(nilai: str, entri: list[dict]) -> str | None:
    """Judul, path relatif, dengan/tanpa .md, garis miring apa pun."""
    n = nilai.replace("\\", "/").strip()
    if n.endswith(".md"):
        n = n[:-3]
    for e in entri:
        if e["path"][:-3] == n or e["judul"] == n:
            return e["path"]
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
        berkas, teks = dari_diff(root, [p.replace("\\", "/") for p in a.diff])
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
```

- [ ] **Step 4: Jalankan, pastikan lolos**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_dampak.py -q`
Expected: semua passed (25)

- [ ] **Step 5: Asap di vault sungguhan** (read-only)

Run dari `erp\`:
`architecture-draft\Tools\.venv\Scripts\python.exe architecture-draft\Tools\dampak.py --root architecture-draft --sumber "ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya" --teks "target profit diketik di insentif"`
Expected: exit 0, JSON valid, `kandidat_dok` tak kosong. Bila ref repo lokal belum di-fetch, repo itu muncul di `dilewati`, bukan crash.

- [ ] **Step 6: Commit**

```powershell
git -c core.fsmonitor=false -C architecture-draft add -- "Tools/dampak.py" "Tools/tests/test_dampak.py"
git -c core.fsmonitor=false -C architecture-draft commit -m "feat(kit): dampak.py CLI, mode --diff, kesegaran index"
```

---

### Task 6: Command `/dampak`, integrasi, rilis kit 1.36.0

**Files:**
- Create: `architecture-draft/.agent-kit/commands/dampak.md`
- Modify: `architecture-draft/.agent-kit/commands/analisa-kebutuhan.md` (§4 akhir, §5 awal)
- Modify: `architecture-draft/.agent-kit/commands/sync-docs.md` (antara langkah 4 dan 5)
- Modify: `architecture-draft/.agent-kit/rules/team-memory.md` (§ Skill & tooling, sesudah butir "Prosedur pencarian vault kini SATU tempat")
- Modify: `architecture-draft/.agent-kit/tests/test-init.ps1` (sesudah baris 75)
- Modify: `architecture-draft/.agent-kit/VERSION`, `architecture-draft/.agent-kit/README.md` (§ Changelog, paling atas)

**Interfaces:**
- Consumes: CLI `dampak.py` Task 5 (`--root`, `--repo-root`, `--sumber`/`--teks`, `--diff [PATH ...]`), bentuk JSON spec §3.

- [ ] **Step 1: Tulis test init yang gagal** — sisipkan sesudah baris 75 `test-init.ps1`:

```powershell
Check (Test-Path (Join-Path $claude 'commands/dampak.md')) 'command /dampak tersalin'
$dpMd = Get-Content (Join-Path $claude 'commands/dampak.md') -Raw -Encoding UTF8
Check ($dpMd -match 'dampak\.py' -and $dpMd -match 'BERHENTI' -and $dpMd -match 'AskUserQuestion') '/dampak: skrip, berhenti, persetujuan per dok'
$akMd = Get-Content (Join-Path $claude 'commands/analisa-kebutuhan.md') -Raw -Encoding UTF8
Check ($akMd -match '/dampak') '/analisa-kebutuhan memanggil /dampak'
$sdMd = Get-Content (Join-Path $claude 'commands/sync-docs.md') -Raw -Encoding UTF8
Check ($sdMd -match 'dampak\.py --root architecture-draft --diff') '/sync-docs memanggil dampak.py --diff'
```

- [ ] **Step 2: Jalankan, pastikan gagal**

Run (background, lewat antrean): `& "<erp>\.claude\hooks\antre.ps1" -- powershell -NoProfile -ExecutionPolicy Bypass -File architecture-draft\.agent-kit\tests\test-init.ps1`
Expected: FAIL pada `command /dampak tersalin`

- [ ] **Step 3: Tulis `commands/dampak.md`**

````markdown
---
description: Impact analysis sebelum mengubah fakta di vault — dok + kode terdampak, usul suntingan, terapkan setelah disetujui
---

Sebelum sebuah fakta di vault (ambang, rumus, daftar-izin, nama rute, field) diubah, temukan di mana
lagi fakta itu ditulis. Kelas bug termahal di sini adalah satu fakta di dua tempat yang menyimpang
diam-diam (`rules/team-memory.md` § SATU FAKTA SATU TEMPAT). Spec:
`.agent-kit/docs/2026-10-07-dampak-command-design.md`.

Pemakaian:
- `/dampak <judul-atau-path dok> "<perubahan yang dimaksud>"`
- `/dampak --diff [PATH ...]` — dok yang sudah disunting tapi belum di-commit. **Sebut PATH-nya**:
  pohon vault dipakai bersama sesi lain, tanpa PATH dok tak-ter-commit milik orang lain ikut terbaca.

Batas tegas: **tidak menyunting kode**, **tidak menyunting dok sumber** (itu tugas pemanggil),
**tidak membuat ADR**.

## 1. Siapkan

1. `git -c core.fsmonitor=false -C architecture-draft pull --ff-only`. Gagal → lanjut, tulis
   "⚠️ salinan vault lokal basi: <alasan>" di kepala laporan.
2. Dari akar `erp/`, jalankan dan simpan keluarannya ke scratchpad:
   `architecture-draft/Tools/.venv/Scripts/python.exe architecture-draft/Tools/dampak.py --root architecture-draft --sumber "<dok>" --teks "<perubahan>"`
   (atau `--diff <PATH ...>`). Exit 2 = sumber tak ditemukan / tak ada perubahan: laporkan, berhenti.
3. `index_segar: false` → catat di kepala laporan; jangan berhenti.

## 2. Nilai kandidat dok

Buka **setiap** `kandidat_dok` dengan `Read` (bukan ringkasan index). Beri satu vonis + satu kalimat alasan:

| Vonis | Artinya |
|---|---|
| **Terdampak** | menyatakan fakta yang sama, atau bergantung pada keputusan yang berubah. **Wajib kutipan baris.** |
| **Hanya menyebut** | menautkan, tak memuat fakta yang berubah |
| **Tidak terkait** | kecocokan kebetulan (mis. `80` sebagai port) |

## 3. Nilai kandidat kode

Kelompokkan `kandidat_kode` per repo, buka `berkas:baris`-nya. **Tidak disunting.** Fakta yang sama di
≥ 2 berkas kode → tandai ⛔ **duplikasi fakta**, sebagai kandidat task/brief.

## 4. Sajikan laporan, lalu BERHENTI

```
Perubahan ini menyentuh N dok + M berkas kode.   [peringatan basi bila ada]

| Dok | Vonis | Kutipan | Usulan suntingan (diff singkat) |
Dibuang: vonis "hanya menyebut"/"tidak terkait" + seluruh `dilewati` beserta alasannya
Kode (tidak disunting): repo · berkas:baris · fakta · ⛔ bila duplikasi
```

Bila perubahannya **menyimpang dari ADR yang berlaku** (bukan sekadar menyelaraskan dok dengan ADR),
tulis **"butuh ADR"** dan berhenti di sini tanpa langkah 5-6.

## 5. Persetujuan per dok

`AskUserQuestion` multiSelect, satu opsi per dok berverdikt **Terdampak**. Yang tidak dipilih tidak disentuh.

## 6. Terapkan yang disetujui

1. Sunting dok terpilih; perbarui status marker bila berubah (rulebook vault §5).
2. Verifikasi 0 wikilink rusak (rulebook §4).
3. `--check` index (`/sync-docs` langkah 6); basi → `/index-vault`.
4. Commit **per nama berkas**: `docs: selaraskan <fakta> (dampak dari <sumber>)`. Lalu merge
   `origin/main`, push `main` (konvensi vault: tanpa PR).
````

- [ ] **Step 4: Integrasi**

`commands/analisa-kebutuhan.md`, akhir §4 (sebelum `### Kamu BOLEH menyimpulkan "tidak perlu dibangun"`), tambahkan:

```markdown
**Fakta yang berubah.** Bila keputusannya **mengubah** fakta yang sudah tertulis di dok lain (ambang,
rumus, daftar-izin, rute), jalankan `/dampak` langkah 1-4 atas draf keputusan ini **sebelum
menyajikan**, dan sajikan laporannya di sini. Satu gerbang persetujuan untuk keduanya. Keputusan yang
murni menambah hal baru boleh lewat.
```

Awal §5, sesudah kalimat "Tiga berkas, semuanya di `architecture-draft`.", tambahkan:

```markdown
Suntingan dok terdampak hasil `/dampak` yang disetujui di §4 diterapkan bersama artefak ini, mengikuti
`/dampak` langkah 6.
```

`commands/sync-docs.md`, sisipkan sesudah langkah 4 (nomor langkah berikutnya digeser +1):

```markdown
5. Cari dok **lain** yang masih menyatakan fakta lama:
   `architecture-draft/Tools/.venv/Scripts/python.exe architecture-draft/Tools/dampak.py --root architecture-draft --diff <dok yang kamu sunting>`
   lalu ikuti `/dampak` langkah 2-6. §7 hanya memetakan repo → dok, jadi tanpa langkah ini salinan
   fakta di dok lain tertinggal tanpa satu pun tanda.
```

`rules/team-memory.md`, sesudah butir "Prosedur pencarian vault kini SATU tempat":

```markdown
- **`/dampak` (kit ≥ 1.36.0) sebelum mengubah FAKTA di vault** (ambang, rumus, daftar-izin, rute, field).
  Ia mendaftar dok lain dan berkas kode yang menyatakan fakta yang sama (`git grep` atas ref remote,
  bukan ripgrep), lalu menyunting dok hanya yang disetujui; kode tak pernah disentuh. Dipanggil sendiri
  oleh `/analisa-kebutuhan` §4 dan `/sync-docs`.
```

`VERSION`: `1.36.0`.

`README.md` § Changelog, paling atas:

```markdown
- **1.36.0**: **`/dampak`, impact analysis sebelum mengubah fakta di vault** (ditiru dari *Impact Analysis* speckit.tech). `/sync-docs` cuma bekerja kode → dok, jadi dok LAIN yang menyatakan fakta lama tertinggal tanpa tanda; kelas bug "satu fakta di dua tempat" di `team-memory.md`. `Tools/dampak.py` (deterministik, read-only, JSON) mendaftar kandidat dari graf wikilink (`scan_vault`, satu lompatan, ADR dua), fakta literal di vault, dan `git grep -a` atas `origin/main`/`origin/dev` tiga repo kode; agent menilai, menyajikan, BERHENTI, lalu menyunting dok yang disetujui per dok. Kode tak disunting. Dipanggil `/analisa-kebutuhan` §4-§5 dan `/sync-docs`. Test: `Tools/tests/test_dampak.py` (kontrol negatif: grep working tree dan tanpa `-a` sama-sama merah), 5 pemeriksaan baru di `tests/test-init.ps1`. Spec + plan: `docs/2026-10-07-dampak-command-*`. **Butuh re-init.**
```

- [ ] **Step 5: Jalankan test init + pytest penuh, pastikan lolos**

Run (background, antrean): `test-init.ps1` seperti Step 2, lalu `.\.venv\Scripts\python.exe -m pytest tests -q` dari `Tools`.
Expected: test-init tanpa FAIL; pytest seluruh `Tools/tests` hijau.

- [ ] **Step 6: Re-init dan cek salinan**

Run: `& architecture-draft\.agent-kit\init.ps1` (dari `erp\`), lalu `Test-Path .claude\commands\dampak.md` → `True`.

- [ ] **Step 7: Commit**

```powershell
$f = ".agent-kit/commands/dampak.md", ".agent-kit/commands/analisa-kebutuhan.md", ".agent-kit/commands/sync-docs.md",
     ".agent-kit/rules/team-memory.md", ".agent-kit/tests/test-init.ps1", ".agent-kit/VERSION", ".agent-kit/README.md"
git -c core.fsmonitor=false -C architecture-draft add -- $f
git -c core.fsmonitor=false -C architecture-draft commit -m "feat(kit): command /dampak + integrasi, kit 1.36.0"
```

- [ ] **Step 8: Push vault** (hanya bila `git pull --ff-only` sudah bersih; perubahan lokal sesi lain di `.agent-kit/baseline/erp-frontend.json` **jangan** disentuh)

`git -C architecture-draft pull --ff-only` → bila konflik `VAULT-INDEX.json`, ikuti team-memory § vault (ambil satu sisi, regenerasi sekali). Lalu `git push origin main` **di background** (pre-push menjalankan `gerbang-kit.py`).
