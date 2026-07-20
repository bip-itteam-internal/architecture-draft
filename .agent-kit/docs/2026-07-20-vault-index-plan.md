# Vault Index Fase 1 — Rencana Implementasi

> **Untuk agentic worker:** REQUIRED SUB-SKILL: pakai `superpowers:subagent-driven-development` (disarankan) atau `superpowers:executing-plans` untuk mengeksekusi rencana ini per-task. Langkah memakai checkbox (`- [ ]`) untuk pelacakan.

**Goal:** Membangun `VAULT-INDEX.json` (manifest 217 dokumen vault) plus generator Python-nya, lalu mengubah `/ask` dan `/start-task` agar memilih dokumen lewat manifest, bukan lewat tebakan keyword.

**Architecture:** Generator Python membaca vault, mengekstrak metadata secara deterministik (regex, aturan folder, SHA-256) dan meminta LLM hanya untuk ringkasan plus kata kunci. Hasilnya satu berkas JSON ter-commit di akar vault. Command agent-kit membacanya untuk memilih 3 sampai 5 dokumen, lalu membaca dokumen itu utuh. Tidak ada embedding, vector store, atau chunking.

**Tech Stack:** Python 3.14, pytest, `anthropic` SDK (Batches API), PyYAML. Model `claude-opus-4-8`.

**Spec:** `.agent-kit/docs/2026-07-20-vault-index-rag-design.md`

## Global Constraints

- **Repo kerja**: `architecture-draft/` (satu-satunya repo yang disentuh). Root `erp/` bukan git repo.
- **Git**: `git -c core.fsmonitor=false ...` selalu (path ber-spasi bikin git menggantung). **Stage per-nama berkas**, JANGAN `git add -A`. Pesan commit berformat `docs: ...` atau `feat: ...`. **Tanpa** trailer `Co-Authored-By`.
- **Venv terpisah**: `Tools/.venv`. JANGAN memakai `python` global — di mesin ini ia menunjuk ke `erp/scraping/.venv` (venv proyek lain, `anthropic` 0.42.0). Semua perintah memakai path venv eksplisit.
- **Bahasa**: kode dan komentar boleh English; string user-facing, ringkasan, dan dokumen Bahasa Indonesia. Istilah teknis lazim English dibiarkan English.
- **Model**: `claude-opus-4-8` persis. Jangan menurunkan tier.
- **Fail-closed**: dokumen di folder yang tidak dikenal WAJIB `publik: false`.
- **Encoding**: semua baca/tulis berkas `encoding="utf-8"` eksplisit (vault penuh emoji; default Windows cp1252 akan crash).
- **JANGAN mengubah isi dokumen vault mana pun.** Hanya menambah berkas baru di `Tools/`, `VAULT-INDEX.json`, dan mengubah 2 berkas di `.agent-kit/commands/`.

## Struktur Berkas

| Berkas | Tanggung jawab |
|---|---|
| `Tools/vault_index/paths.py` | Klasifikasi path: `jenis`, `area`, `publik`, dan apakah berkas diikutkan sama sekali |
| `Tools/vault_index/parsing.py` | Ekstraksi dari isi dokumen: status, wikilink, heading, hash |
| `Tools/vault_index/summarize.py` | Panggilan LLM: bangun prompt, submit batch, ambil hasil |
| `Tools/vault_index/build.py` | Orkestrasi: scan, incremental diff, rakit JSON, tulis, laporkan |
| `Tools/build-vault-index.py` | Entry point CLI (`--full`, `--check`) |
| `Tools/tests/*` | pytest |
| `Tools/requirements.txt` | Dependensi |
| `VAULT-INDEX.json` | Artefak |
| `Tools/eval-questions.yaml` | Eval set |

Dipecah per tanggung jawab, bukan per lapisan teknis. `paths.py` dan `parsing.py` murni (tanpa I/O jaringan) sehingga bisa dites cepat dan menyeluruh; `summarize.py` mengisolasi satu-satunya bagian non-deterministik.

---

### Task 1: Scaffolding, venv, dan klasifikasi path

**Files:**
- Create: `Tools/requirements.txt`
- Create: `Tools/vault_index/__init__.py`
- Create: `Tools/vault_index/paths.py`
- Create: `Tools/tests/__init__.py`
- Test: `Tools/tests/test_paths.py`
- Modify: `.gitignore` (tambah `Tools/.venv/`, `__pycache__/`, `.pytest_cache/`)

**Interfaces:**
- Produces:
  - `KLASIFIKASI: dict[str, tuple[str, bool]]` — nama folder tingkat-1 → `(jenis, publik)`
  - `klasifikasi_path(rel_path: str) -> dict | None` — kembalikan `{"area": str, "jenis": str, "publik": bool}`, atau `None` bila berkas harus dilewati seluruhnya (Shopee cache, Additional documents, non-`.md`)

- [ ] **Step 1: Buat venv dan pasang dependensi**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
py -3 -m venv Tools/.venv
Tools/.venv/Scripts/python.exe -m pip install --upgrade pip
```

Buat `Tools/requirements.txt`:

```
anthropic>=0.40
PyYAML>=6.0
pytest>=8.0
```

```bash
Tools/.venv/Scripts/python.exe -m pip install -r Tools/requirements.txt
Tools/.venv/Scripts/python.exe -m pip freeze > Tools/requirements.lock.txt
```

- [ ] **Step 2: Tambah entri `.gitignore`**

Tambahkan di akhir `architecture-draft/.gitignore`:

```
# Vault index tooling
Tools/.venv/
__pycache__/
.pytest_cache/
```

- [ ] **Step 3: Tulis tes yang gagal**

Buat `Tools/vault_index/__init__.py` dan `Tools/tests/__init__.py` sebagai berkas kosong.

Buat `Tools/tests/test_paths.py`:

```python
import pytest
from vault_index.paths import klasifikasi_path


@pytest.mark.parametrize("rel_path,area,jenis,publik", [
    ("Human Resource Information System/HRIS - Overtime.md",
     "Human Resource Information System", "domain", True),
    ("Decisions/ADR - 0006 Swap Jadwal Same-Department.md",
     "Decisions", "adr", True),
    ("Runbooks/RUN - Onboarding Developer Baru.md", "Runbooks", "runbook", True),
    ("Reference/REF - Glossary.md", "Reference", "reference", True),
    ("API Reference/API - Employee Service.md", "API Reference", "api", True),
    ("HOMEPAGE.md", "root", "meta", True),
    ("Sales/Sales - HPP Master (Plan).md", "Sales", "domain", True),
])
def test_folder_dikenal(rel_path, area, jenis, publik):
    hasil = klasifikasi_path(rel_path)
    assert hasil == {"area": area, "jenis": jenis, "publik": publik}


@pytest.mark.parametrize("rel_path,jenis", [
    ("IT/IT - Server, VMs and Databases.md", "domain"),
    ("Workspace/Inbox/2026-06-25.md", "workspace"),
    ("Workspace/Meetings/MTG - 2026-06-25 Contoh Notulen.md", "workspace"),
    ("Logs/LOG - Shopee API Rate Limit Request.md", "log"),
    ("Templates/Template - Daily Note.md", "template"),
])
def test_folder_tertutup_untuk_manusia(rel_path, jenis):
    """Ter-index untuk agent, tapi publik=False."""
    hasil = klasifikasi_path(rel_path)
    assert hasil is not None
    assert hasil["jenis"] == jenis
    assert hasil["publik"] is False


@pytest.mark.parametrize("rel_path", [
    "API Reference/Shopee Open API v2/Index.md",
    "API Reference/Shopee Open API v2/order.get_order_list.md",
    "API Reference/Shopee Open API v2/Tools/refresh.py",
    "Additional documents/Excalidraw/Recruitment Pipeline.excalidraw.md",
    "Tools/build-vault-index.py",
    "gambar.png",
])
def test_dilewati_seluruhnya(rel_path):
    assert klasifikasi_path(rel_path) is None


def test_folder_tak_dikenal_default_tertutup():
    """FAIL-CLOSED: folder baru yang belum diklasifikasi tidak boleh bocor ke publik."""
    hasil = klasifikasi_path("Folder Baru Yang Belum Ada/Sesuatu.md")
    assert hasil is not None, "dokumen tetap ter-index untuk agent"
    assert hasil["publik"] is False, "tapi WAJIB tertutup untuk kanal manusia"
    assert hasil["jenis"] is None
```

- [ ] **Step 4: Jalankan tes, pastikan gagal**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft/Tools"
.venv/Scripts/python.exe -m pytest tests/test_paths.py -v
```

Expected: FAIL dengan `ModuleNotFoundError: No module named 'vault_index'`

- [ ] **Step 5: Implementasi minimal**

Buat `Tools/pytest.ini` supaya `vault_index` bisa di-import:

```ini
[pytest]
pythonpath = .
testpaths = tests
```

Buat `Tools/vault_index/paths.py`:

```python
"""Klasifikasi path berkas vault menjadi (area, jenis, publik)."""

from pathlib import PurePosixPath

# folder tingkat-1 -> (jenis, publik)
KLASIFIKASI: dict[str, tuple[str, bool]] = {
    "Application": ("domain", True),
    "Core System and Modules": ("domain", True),
    "Finance System": ("domain", True),
    "General Affairs": ("domain", True),
    "Human Resource Information System": ("domain", True),
    "Manufacture": ("domain", True),
    "Quality & Regulatory": ("domain", True),
    "Sales": ("domain", True),
    "Third-party Software": ("domain", True),
    "Unknown or not listed": ("domain", True),
    "Warehouse": ("domain", True),
    "Decisions": ("adr", True),
    "Runbooks": ("runbook", True),
    "Reference": ("reference", True),
    "API Reference": ("api", True),
    # ter-index untuk agent, TERTUTUP untuk kanal manusia
    "IT": ("domain", False),
    "Workspace": ("workspace", False),
    "Logs": ("log", False),
    "Templates": ("template", False),
}

# dilewati seluruhnya: tidak ter-index untuk siapa pun
DILEWATI: frozenset[str] = frozenset({
    "Additional documents",  # aset Excalidraw
    "Tools",                 # tooling ini sendiri
})

# subpohon vendor cache yang di-generate skrip
PREFIX_DILEWATI: tuple[str, ...] = (
    "API Reference/Shopee Open API v2/",
)


def klasifikasi_path(rel_path: str) -> dict | None:
    """Klasifikasikan path relatif-vault.

    Kembalikan {"area", "jenis", "publik"}, atau None bila berkas
    harus dilewati seluruhnya.

    Folder yang tidak dikenal tetap ter-index untuk agent tapi
    SELALU publik=False (fail-closed).
    """
    p = PurePosixPath(rel_path.replace("\\", "/"))

    if p.suffix.lower() != ".md":
        return None

    posix = p.as_posix()
    if any(posix.startswith(prefix) for prefix in PREFIX_DILEWATI):
        return None

    if len(p.parts) == 1:
        return {"area": "root", "jenis": "meta", "publik": True}

    top = p.parts[0]
    if top in DILEWATI or top.startswith("."):
        return None

    if top in KLASIFIKASI:
        jenis, publik = KLASIFIKASI[top]
        return {"area": top, "jenis": jenis, "publik": publik}

    # fail-closed
    return {"area": top, "jenis": None, "publik": False}
```

- [ ] **Step 6: Jalankan tes, pastikan lulus**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft/Tools"
.venv/Scripts/python.exe -m pytest tests/test_paths.py -v
```

Expected: PASS, 19 passed

- [ ] **Step 7: Commit**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
git -c core.fsmonitor=false add -- .gitignore Tools/requirements.txt Tools/requirements.lock.txt Tools/pytest.ini Tools/vault_index/__init__.py Tools/vault_index/paths.py Tools/tests/__init__.py Tools/tests/test_paths.py
git -c core.fsmonitor=false commit -m "feat(tools): klasifikasi path vault untuk index (fail-closed)"
```

---

### Task 2: Parsing isi dokumen

**Files:**
- Create: `Tools/vault_index/parsing.py`
- Test: `Tools/tests/test_parsing.py`

**Interfaces:**
- Consumes: tidak ada (modul murni)
- Produces:
  - `EMOJI_STATUS: frozenset[str]` — enam emoji yang dikenal
  - `ekstrak_status(teks: str) -> tuple[str | None, str | None]` — `(status_emoji, status_teks)`
  - `ekstrak_wikilink(teks: str) -> list[str]` — basename unik, urut kemunculan, embed `![[...]]` dikecualikan
  - `ekstrak_heading(teks: str) -> list[str]` — semua baris heading markdown apa adanya
  - `hitung_hash(teks: str) -> str` — SHA-256 hex
  - `potong_untuk_llm(teks: str, batas_byte: int = 8192) -> str` — dokumen besar jadi kepala + daftar heading

- [ ] **Step 1: Tulis tes yang gagal**

Buat `Tools/tests/test_parsing.py`:

```python
from vault_index.parsing import (
    ekstrak_status, ekstrak_wikilink, ekstrak_heading,
    hitung_hash, potong_untuk_llm,
)


# --- status: tiga format yang benar-benar ada di vault ---

def test_status_format_bullet_bold():
    teks = "## Deskripsi\n\n- **Status**: ✅ Accepted (mencerminkan kondisi kode)\n"
    assert ekstrak_status(teks) == ("✅", "Accepted (mencerminkan kondisi kode)")


def test_status_format_polos_tanpa_bullet_bold():
    """ADR - 0014 memakai format ini."""
    teks = "Status: ⚠️ Implemented (ada catatan) — kode selesai 2026-07-14.\n"
    emoji, txt = ekstrak_status(teks)
    assert emoji == "⚠️"
    assert txt.startswith("Implemented (ada catatan)")


def test_status_emoji_superseded():
    teks = "- **Status**: ⛔ Superseded — digantikan [[ADR - 0022]]\n"
    emoji, _ = ekstrak_status(teks)
    assert emoji == "⛔"


def test_status_emoji_segera():
    teks = "- **Status**: 🔜 Direncanakan Q3\n"
    assert ekstrak_status(teks) == ("🔜", "Direncanakan Q3")


def test_status_berupa_prosa_bukan_emoji():
    """4 dokumen menulis status sebagai prosa. Emoji None, teks utuh."""
    teks = "- **Status**: desain masih dibahas bersama HRD\n"
    emoji, txt = ekstrak_status(teks)
    assert emoji is None
    assert txt == "desain masih dibahas bersama HRD"


def test_status_absen_adalah_kondisi_normal():
    """69 dari 217 dokumen memang tidak punya status. Bukan error."""
    teks = "## Deskripsi\n\nDokumen tanpa baris status sama sekali.\n"
    assert ekstrak_status(teks) == (None, None)


def test_status_hanya_dicari_di_kepala_dokumen():
    """'Status' di tengah dokumen (mis. '## Status Rollout') tidak boleh tertangkap."""
    teks = "## Deskripsi\n" + ("isi\n" * 40) + "- **Status**: ✅ Accepted\n"
    assert ekstrak_status(teks) == (None, None)


# --- wikilink ---

def test_wikilink_dasar():
    teks = "Lihat [[HRIS - Overtime]] dan [[APP - MyBharata]]."
    assert ekstrak_wikilink(teks) == ["HRIS - Overtime", "APP - MyBharata"]


def test_wikilink_embed_gambar_dikecualikan():
    """![[...]] adalah embed aset, bukan tautan dokumen."""
    teks = "![[erp-request-nutshell.png]] lalu [[CORE - SSO Flow]]"
    assert ekstrak_wikilink(teks) == ["CORE - SSO Flow"]


def test_wikilink_alias_diambil_basename_saja():
    teks = "[[HRIS - Overtime|lembur]]"
    assert ekstrak_wikilink(teks) == ["HRIS - Overtime"]


def test_wikilink_duplikat_dibuang_urutan_dijaga():
    teks = "[[B]] [[A]] [[B]]"
    assert ekstrak_wikilink(teks) == ["B", "A"]


def test_wikilink_kosong():
    assert ekstrak_wikilink("tanpa tautan apa pun") == []


# --- heading ---

def test_ekstrak_heading():
    teks = "# Judul\n\nisi\n\n## Bagian A\n\nisi\n\n### Sub\n"
    assert ekstrak_heading(teks) == ["# Judul", "## Bagian A", "### Sub"]


# --- hash ---

def test_hash_stabil_dan_idempoten():
    assert hitung_hash("isi") == hitung_hash("isi")


def test_hash_berbeda_untuk_isi_berbeda():
    assert hitung_hash("isi a") != hitung_hash("isi b")


# --- pemotongan ---

def test_dokumen_kecil_tidak_dipotong():
    teks = "# Judul\n\nisi pendek\n"
    assert potong_untuk_llm(teks) == teks


def test_dokumen_besar_dipotong_dan_heading_dipertahankan():
    teks = "# Judul\n\n" + ("x" * 20000) + "\n\n## Bagian Akhir\n"
    hasil = potong_untuk_llm(teks, batas_byte=1000)
    assert len(hasil.encode("utf-8")) < len(teks.encode("utf-8"))
    assert "# Judul" in hasil
    assert "## Bagian Akhir" in hasil, "heading di luar potongan tetap harus terdaftar"
```

- [ ] **Step 2: Jalankan tes, pastikan gagal**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft/Tools"
.venv/Scripts/python.exe -m pytest tests/test_parsing.py -v
```

Expected: FAIL dengan `ModuleNotFoundError: No module named 'vault_index.parsing'`

- [ ] **Step 3: Implementasi minimal**

Buat `Tools/vault_index/parsing.py`:

```python
"""Ekstraksi deterministik dari isi dokumen markdown."""

import hashlib
import re

# Enam emoji yang benar-benar dipakai di vault (terukur 2026-07-20):
# 🟡 58 · ✅ 43 · ⚠️ 34 · 🔴 7 · 🔜 1 · ⛔ 1
EMOJI_STATUS: frozenset[str] = frozenset({"✅", "⚠️", "🟡", "🔴", "🔜", "⛔"})

BARIS_KEPALA = 15

_RE_STATUS = re.compile(
    r"^\s*(?:-\s*)?(?:\*\*)?Status(?:\*\*)?\s*:\s*(\S+)[ \t]*(.*)$",
    re.MULTILINE,
)
_RE_WIKILINK = re.compile(r"(?<!!)\[\[([^\]|#]+)")
_RE_HEADING = re.compile(r"^#{1,6} .+$", re.MULTILINE)


def ekstrak_status(teks: str) -> tuple[str | None, str | None]:
    """Ambil (status_emoji, status_teks) mentah dari kepala dokumen.

    Status TIDAK dinormalisasi: kosakata ADR (Accepted/Proposed/Superseded)
    berbeda dari kosakata domain (Implemented/Konsep/Stub).

    Absennya status adalah kondisi normal (69 dari 217 dokumen).
    """
    kepala = "\n".join(teks.splitlines()[:BARIS_KEPALA])
    m = _RE_STATUS.search(kepala)
    if not m:
        return (None, None)

    token, sisa = m.group(1), m.group(2).strip()
    if token in EMOJI_STATUS:
        return (token, sisa or None)
    # status berupa prosa: tidak ada emoji, seluruh baris jadi teks
    gabung = f"{token} {sisa}".strip()
    return (None, gabung or None)


def ekstrak_wikilink(teks: str) -> list[str]:
    """Basename wikilink unik, urut kemunculan. Embed ![[...]] dikecualikan."""
    hasil: list[str] = []
    for m in _RE_WIKILINK.finditer(teks):
        nama = m.group(1).strip()
        if nama and nama not in hasil:
            hasil.append(nama)
    return hasil


def ekstrak_heading(teks: str) -> list[str]:
    return _RE_HEADING.findall(teks)


def hitung_hash(teks: str) -> str:
    return hashlib.sha256(teks.encode("utf-8")).hexdigest()


def potong_untuk_llm(teks: str, batas_byte: int = 8192) -> str:
    """Dokumen besar jadi kepala + daftar seluruh heading.

    Ringkasan tingkat-dokumen tidak butuh isi lengkap, dan berkas
    terbesar di vault 139 KB.
    """
    raw = teks.encode("utf-8")
    if len(raw) <= batas_byte:
        return teks

    kepala = raw[:batas_byte].decode("utf-8", errors="ignore")
    heading = ekstrak_heading(teks)
    return (
        kepala
        + "\n\n[...dipotong...]\n\n## Seluruh heading dokumen ini:\n"
        + "\n".join(heading)
    )
```

- [ ] **Step 4: Jalankan tes, pastikan lulus**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft/Tools"
.venv/Scripts/python.exe -m pytest tests/test_parsing.py -v
```

Expected: PASS, 18 passed

- [ ] **Step 5: Verifikasi regex terhadap vault nyata**

Skrip sekali pakai untuk memastikan parser cocok dengan angka terukur (148 punya status, 69 tidak):

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
Tools/.venv/Scripts/python.exe -c "
import sys; sys.path.insert(0, 'Tools')
from pathlib import Path
from vault_index.paths import klasifikasi_path
from vault_index.parsing import ekstrak_status
root = Path('.')
ada = tidak = 0
for p in root.rglob('*.md'):
    rel = p.relative_to(root).as_posix()
    if rel.startswith('.') or klasifikasi_path(rel) is None:
        continue
    e, t = ekstrak_status(p.read_text(encoding='utf-8'))
    if e or t: ada += 1
    else: tidak += 1
print('punya status:', ada, '| tanpa status:', tidak, '| total:', ada + tidak)
"
```

Expected: `punya status: 148 | tanpa status: 69 | total: 217`

Kalau angkanya meleset, regex atau klasifikasi salah. **Perbaiki sebelum lanjut** — task berikutnya bergantung pada total 217.

- [ ] **Step 6: Commit**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
git -c core.fsmonitor=false add -- Tools/vault_index/parsing.py Tools/tests/test_parsing.py
git -c core.fsmonitor=false commit -m "feat(tools): parsing status/wikilink/heading/hash dokumen vault"
```

---

### Task 3: Ringkasan LLM via Batches API

**Files:**
- Create: `Tools/vault_index/summarize.py`
- Test: `Tools/tests/test_summarize.py`

**Interfaces:**
- Consumes: `potong_untuk_llm` dari `vault_index.parsing`
- Produces:
  - `MODEL = "claude-opus-4-8"`
  - `bangun_prompt(judul: str, jenis: str | None, isi: str) -> str`
  - `SKEMA_RINGKASAN: dict` — JSON schema untuk `output_config.format`
  - `submit_batch(client, tugas: list[dict]) -> str` — `tugas` berisi `{"custom_id", "judul", "jenis", "isi"}`, kembalikan `batch_id`
  - `ambil_hasil(client, batch_id: str) -> dict[str, dict | None]` — `custom_id` → `{"ringkasan", "kata_kunci"}` atau `None` bila gagal
  - `ringkas_stub(judul: str) -> dict` — ringkasan dokumen 🔴 Stub tanpa panggil LLM

- [ ] **Step 1: Tulis tes yang gagal**

Buat `Tools/tests/test_summarize.py`:

```python
import json
from vault_index.summarize import (
    MODEL, bangun_prompt, SKEMA_RINGKASAN, ringkas_stub, _parse_isi_pesan,
)


def test_model_adalah_opus_4_8():
    """Jangan menurunkan tier: kualitas ringkasan menentukan kualitas retrieval."""
    assert MODEL == "claude-opus-4-8"


def test_prompt_memuat_judul_dan_isi():
    p = bangun_prompt("HRIS - Overtime", "domain", "isi dokumen di sini")
    assert "HRIS - Overtime" in p
    assert "isi dokumen di sini" in p


def test_prompt_meminta_orientasi_pertanyaan():
    """Ringkasan harus menjawab 'dokumen ini menjawab pertanyaan apa',
    bukan memadatkan isi."""
    p = bangun_prompt("X", "domain", "isi")
    assert "pertanyaan" in p.lower()


def test_prompt_menetapkan_bahasa_indonesia():
    p = bangun_prompt("X", "domain", "isi")
    assert "Indonesia" in p


def test_skema_mewajibkan_kedua_field():
    assert SKEMA_RINGKASAN["required"] == ["ringkasan", "kata_kunci"]
    assert SKEMA_RINGKASAN["additionalProperties"] is False
    assert SKEMA_RINGKASAN["properties"]["kata_kunci"]["type"] == "array"


def test_ringkas_stub_tidak_panggil_llm():
    hasil = ringkas_stub("IT - Network Management")
    assert "IT - Network Management" in hasil["ringkasan"]
    assert hasil["kata_kunci"] == []


def test_parse_isi_pesan_valid():
    isi = json.dumps({"ringkasan": "Menjawab: bagaimana X.", "kata_kunci": ["a", "b"]})
    assert _parse_isi_pesan(isi) == {
        "ringkasan": "Menjawab: bagaimana X.", "kata_kunci": ["a", "b"]
    }


def test_parse_isi_pesan_rusak_kembalikan_none():
    """JSON rusak jadi None, bukan exception. Kegagalan dilaporkan, bukan meledak."""
    assert _parse_isi_pesan("bukan json") is None
    assert _parse_isi_pesan('{"ringkasan": "ada"}') is None  # kata_kunci hilang
```

- [ ] **Step 2: Jalankan tes, pastikan gagal**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft/Tools"
.venv/Scripts/python.exe -m pytest tests/test_summarize.py -v
```

Expected: FAIL dengan `ModuleNotFoundError: No module named 'vault_index.summarize'`

- [ ] **Step 3: Implementasi minimal**

Buat `Tools/vault_index/summarize.py`:

```python
"""Ringkasan dokumen via Claude Batches API.

Ini satu-satunya bagian non-deterministik dari generator. Kualitasnya
diukur lewat eval set (Task 6), bukan lewat assertion.
"""

import json
import time

from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

from .parsing import potong_untuk_llm

MODEL = "claude-opus-4-8"
MAX_TOKENS = 1024

SKEMA_RINGKASAN: dict = {
    "type": "object",
    "properties": {
        "ringkasan": {
            "type": "string",
            "description": "2-3 kalimat, Bahasa Indonesia, berorientasi pertanyaan",
        },
        "kata_kunci": {
            "type": "array",
            "items": {"type": "string"},
            "description": "5-10 kata kunci, campur Indonesia dan English",
        },
    },
    "required": ["ringkasan", "kata_kunci"],
    "additionalProperties": False,
}

_TEMPLATE = """Kamu meringkas satu dokumen dari vault arsitektur ERP Bharata \
untuk dipakai sebagai index pencarian.

Judul dokumen: {judul}
Jenis dokumen: {jenis}

Tulis dalam Bahasa Indonesia. Istilah teknis yang lazim English biarkan English \
(endpoint, request, service, payroll, approval, dst).

`ringkasan`: 2 sampai 3 kalimat yang menjawab "dokumen ini bisa menjawab \
pertanyaan apa saja", BUKAN sekadar memadatkan isinya.
Buruk : "Berisi endpoint dan alur lembur."
Baik  : "Menjawab: bagaimana cara mengajukan lembur, siapa yang menyetujui, \
dan bagaimana upah lembur dihitung."

`kata_kunci`: 5 sampai 10 istilah yang mungkin dipakai orang saat mencari \
dokumen ini. Sertakan padanan dua bahasa bila ada (mis. "lembur" dan \
"overtime"), termasuk singkatan yang dipakai internal.

JANGAN menyimpulkan status implementasi. Itu diambil terpisah dari marker \
dokumen.

--- ISI DOKUMEN ---
{isi}
"""


def bangun_prompt(judul: str, jenis: str | None, isi: str) -> str:
    return _TEMPLATE.format(
        judul=judul,
        jenis=jenis or "tidak diketahui",
        isi=potong_untuk_llm(isi),
    )


def ringkas_stub(judul: str) -> dict:
    """Dokumen 🔴 Stub: satu baris, tanpa panggil LLM. Hemat dan jujur."""
    return {
        "ringkasan": f"Stub kosong untuk {judul}. Belum ada isi.",
        "kata_kunci": [],
    }


def _parse_isi_pesan(isi: str) -> dict | None:
    """Parse JSON balasan model. Rusak -> None, bukan exception."""
    try:
        data = json.loads(isi)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    if "ringkasan" not in data or "kata_kunci" not in data:
        return None
    if not isinstance(data["kata_kunci"], list):
        return None
    return {"ringkasan": data["ringkasan"], "kata_kunci": data["kata_kunci"]}


def submit_batch(client, tugas: list[dict]) -> str:
    """Submit batch ringkasan. Batches API memberi diskon 50 persen."""
    requests = [
        Request(
            custom_id=t["custom_id"],
            params=MessageCreateParamsNonStreaming(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                output_config={
                    "format": {"type": "json_schema", "schema": SKEMA_RINGKASAN}
                },
                messages=[{
                    "role": "user",
                    "content": bangun_prompt(t["judul"], t["jenis"], t["isi"]),
                }],
            ),
        )
        for t in tugas
    ]
    batch = client.messages.batches.create(requests=requests)
    return batch.id


def ambil_hasil(client, batch_id: str, interval: int = 30) -> dict[str, dict | None]:
    """Tunggu batch selesai, kembalikan custom_id -> hasil (None bila gagal)."""
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            break
        print(f"  batch {batch_id}: {batch.processing_status} ...")
        time.sleep(interval)

    hasil: dict[str, dict | None] = {}
    for baris in client.messages.batches.results(batch_id):
        if baris.result.type != "succeeded":
            hasil[baris.custom_id] = None
            continue
        teks = next(
            (b.text for b in baris.result.message.content if b.type == "text"), ""
        )
        hasil[baris.custom_id] = _parse_isi_pesan(teks)
    return hasil
```

- [ ] **Step 4: Jalankan tes, pastikan lulus**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft/Tools"
.venv/Scripts/python.exe -m pytest tests/test_summarize.py -v
```

Expected: PASS, 8 passed

- [ ] **Step 5: Commit**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
git -c core.fsmonitor=false add -- Tools/vault_index/summarize.py Tools/tests/test_summarize.py
git -c core.fsmonitor=false commit -m "feat(tools): ringkasan dokumen via Claude Batches API"
```

---

### Task 4: Orkestrasi build, mode incremental, dan CLI

**Files:**
- Create: `Tools/vault_index/build.py`
- Create: `Tools/build-vault-index.py`
- Test: `Tools/tests/test_build.py`

**Interfaces:**
- Consumes: `klasifikasi_path`; `ekstrak_status`, `ekstrak_wikilink`, `hitung_hash`; `ringkas_stub`, `submit_batch`, `ambil_hasil`
- Produces:
  - `VERSI_SKEMA = 1`
  - `scan_vault(root: Path) -> list[dict]` — entri tanpa ringkasan, sudah ber-`hash`
  - `muat_index(path: Path) -> dict | None`
  - `pilih_yang_perlu_diringkas(entri, lama, full=False) -> list[dict]`
  - `rakit_index(entri: list[dict]) -> dict`
  - `main(argv) -> int` — exit code

- [ ] **Step 1: Tulis tes yang gagal**

Buat `Tools/tests/test_build.py`:

```python
import json
from pathlib import Path

import pytest

from vault_index.build import (
    VERSI_SKEMA, scan_vault, muat_index,
    pilih_yang_perlu_diringkas, rakit_index,
)


@pytest.fixture
def vault_mini(tmp_path: Path) -> Path:
    """Vault kecil yang meniru struktur asli, termasuk yang harus dilewati."""
    (tmp_path / "Human Resource Information System").mkdir(parents=True)
    (tmp_path / "Human Resource Information System" / "HRIS - Overtime.md").write_text(
        "## Deskripsi\n\n- **Status**: ⚠️ Sebagian terimplementasi\n\n"
        "Lihat [[APP - MyBharata]].\n",
        encoding="utf-8",
    )
    (tmp_path / "Decisions").mkdir()
    (tmp_path / "Decisions" / "ADR - 0006 Swap.md").write_text(
        "- **Status**: ✅ Accepted\n", encoding="utf-8"
    )
    (tmp_path / "IT").mkdir()
    (tmp_path / "IT" / "IT - Security.md").write_text(
        "- **Status**: 🟡 Konsep\n", encoding="utf-8"
    )
    (tmp_path / "HOMEPAGE.md").write_text("# Peta\n\nTanpa status.\n", encoding="utf-8")
    # harus dilewati seluruhnya
    shopee = tmp_path / "API Reference" / "Shopee Open API v2"
    shopee.mkdir(parents=True)
    (shopee / "order.get_order_list.md").write_text("cache\n", encoding="utf-8")
    return tmp_path


def test_scan_melewati_shopee_cache(vault_mini):
    paths = {e["path"] for e in scan_vault(vault_mini)}
    assert not any("Shopee" in p for p in paths)
    assert len(paths) == 4


def test_scan_isi_field_deterministik(vault_mini):
    entri = {e["path"]: e for e in scan_vault(vault_mini)}
    hris = entri["Human Resource Information System/HRIS - Overtime.md"]
    assert hris["judul"] == "HRIS - Overtime"
    assert hris["area"] == "Human Resource Information System"
    assert hris["jenis"] == "domain"
    assert hris["publik"] is True
    assert hris["status_emoji"] == "⚠️"
    assert hris["tautan"] == ["APP - MyBharata"]
    assert len(hris["hash"]) == 64


def test_scan_it_tertutup_untuk_publik(vault_mini):
    entri = {e["path"]: e for e in scan_vault(vault_mini)}
    assert entri["IT/IT - Security.md"]["publik"] is False


def test_scan_homepage_tanpa_status_bukan_error(vault_mini):
    entri = {e["path"]: e for e in scan_vault(vault_mini)}
    home = entri["HOMEPAGE.md"]
    assert home["status_emoji"] is None
    assert home["jenis"] == "meta"


def test_incremental_lewati_hash_yang_sama(vault_mini):
    entri = scan_vault(vault_mini)
    lama = rakit_index([{**e, "ringkasan": "sudah ada", "kata_kunci": []} for e in entri])
    assert pilih_yang_perlu_diringkas(entri, lama) == []


def test_incremental_pilih_yang_berubah(vault_mini):
    entri = scan_vault(vault_mini)
    lama = rakit_index([{**e, "ringkasan": "sudah ada", "kata_kunci": []} for e in entri])
    lama["dokumen"][0]["hash"] = "hash-lama-yang-berbeda"
    terpilih = pilih_yang_perlu_diringkas(entri, lama)
    assert len(terpilih) == 1
    assert terpilih[0]["path"] == lama["dokumen"][0]["path"]


def test_incremental_pilih_yang_ringkasannya_null(vault_mini):
    """Dokumen yang gagal diringkas sebelumnya harus dicoba lagi."""
    entri = scan_vault(vault_mini)
    lama = rakit_index([{**e, "ringkasan": "ada", "kata_kunci": []} for e in entri])
    lama["dokumen"][0]["ringkasan"] = None
    terpilih = pilih_yang_perlu_diringkas(entri, lama)
    assert len(terpilih) == 1


def test_full_pilih_semua(vault_mini):
    entri = scan_vault(vault_mini)
    lama = rakit_index([{**e, "ringkasan": "ada", "kata_kunci": []} for e in entri])
    assert len(pilih_yang_perlu_diringkas(entri, lama, full=True)) == 4


def test_rakit_index_bentuk_benar(vault_mini):
    entri = [{**e, "ringkasan": "r", "kata_kunci": []} for e in scan_vault(vault_mini)]
    idx = rakit_index(entri)
    assert idx["versi_skema"] == VERSI_SKEMA
    assert idx["jumlah_dokumen"] == 4
    assert idx["gagal"] == []


def test_rakit_index_catat_yang_gagal(vault_mini):
    entri = [{**e, "ringkasan": None, "kata_kunci": []} for e in scan_vault(vault_mini)]
    idx = rakit_index(entri)
    assert len(idx["gagal"]) == 4


def test_muat_index_tidak_ada(tmp_path):
    assert muat_index(tmp_path / "tidak-ada.json") is None


def test_muat_index_rusak_kembalikan_none(tmp_path):
    p = tmp_path / "rusak.json"
    p.write_text("{ bukan json", encoding="utf-8")
    assert muat_index(p) is None


def test_muat_index_versi_skema_beda_kembalikan_none(tmp_path):
    p = tmp_path / "lama.json"
    p.write_text(json.dumps({"versi_skema": 99, "dokumen": []}), encoding="utf-8")
    assert muat_index(p) is None
```

- [ ] **Step 2: Jalankan tes, pastikan gagal**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft/Tools"
.venv/Scripts/python.exe -m pytest tests/test_build.py -v
```

Expected: FAIL dengan `ModuleNotFoundError: No module named 'vault_index.build'`

- [ ] **Step 3: Implementasi minimal**

Buat `Tools/vault_index/build.py`:

```python
"""Orkestrasi: scan vault, diff incremental, rakit dan tulis VAULT-INDEX.json."""

import argparse
import json
from datetime import date
from pathlib import Path

from .parsing import ekstrak_status, ekstrak_wikilink, hitung_hash
from .paths import klasifikasi_path
from .summarize import MODEL, ambil_hasil, ringkas_stub, submit_batch

VERSI_SKEMA = 1
NAMA_INDEX = "VAULT-INDEX.json"


def scan_vault(root: Path) -> list[dict]:
    """Kumpulkan entri beserta seluruh field deterministik (tanpa ringkasan)."""
    entri: list[dict] = []
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root).as_posix()
        if any(bagian.startswith(".") for bagian in Path(rel).parts):
            continue
        klas = klasifikasi_path(rel)
        if klas is None:
            continue

        isi = p.read_text(encoding="utf-8")
        emoji, teks_status = ekstrak_status(isi)
        entri.append({
            "path": rel,
            "judul": p.stem,
            "area": klas["area"],
            "jenis": klas["jenis"],
            "status_emoji": emoji,
            "status_teks": teks_status,
            "publik": klas["publik"],
            "tautan": ekstrak_wikilink(isi),
            "hash": hitung_hash(isi),
            "ukuran_kb": round(p.stat().st_size / 1024, 1),
            "_isi": isi,
        })
    return entri


def muat_index(path: Path) -> dict | None:
    """Muat index lama. Hilang, rusak, atau beda versi skema -> None."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict) or data.get("versi_skema") != VERSI_SKEMA:
        return None
    return data


def pilih_yang_perlu_diringkas(
    entri: list[dict], lama: dict | None, full: bool = False
) -> list[dict]:
    """Pilih dokumen yang perlu panggilan LLM.

    Dipilih bila: --full, atau belum ada di index lama, atau hash berubah,
    atau ringkasan sebelumnya null (percobaan sebelumnya gagal).
    """
    if full or lama is None:
        return list(entri)

    sebelumnya = {d["path"]: d for d in lama.get("dokumen", [])}
    perlu = []
    for e in entri:
        d = sebelumnya.get(e["path"])
        if d is None or d.get("hash") != e["hash"] or d.get("ringkasan") is None:
            perlu.append(e)
    return perlu


def rakit_index(entri: list[dict]) -> dict:
    dokumen = []
    gagal = []
    for e in entri:
        d = {k: v for k, v in e.items() if not k.startswith("_")}
        if d.get("ringkasan") is None:
            gagal.append(d["path"])
        dokumen.append(d)
    return {
        "versi_skema": VERSI_SKEMA,
        "digenerate": date.today().isoformat(),
        "jumlah_dokumen": len(dokumen),
        "dokumen": dokumen,
        "gagal": gagal,
    }


def _peringatan_status(entri: list[dict]) -> list[str]:
    """Status absen normal untuk meta/api; janggal untuk domain/adr."""
    return [
        e["path"]
        for e in entri
        if e["jenis"] in ("domain", "adr")
        and e["status_emoji"] is None
        and e["status_teks"] is None
    ]


def _peringatan_folder_tak_dikenal(entri: list[dict]) -> list[str]:
    """Folder belum terdaftar di KLASIFIKASI: aman (publik=False) tapi harus terlihat.

    Kalau dibiarkan senyap, folder domain baru akan tertutup selamanya dari
    kanal manusia tanpa ada yang sadar.
    """
    return [e["path"] for e in entri if e["jenis"] is None]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bangun VAULT-INDEX.json")
    ap.add_argument("--full", action="store_true", help="regen semua, abaikan hash")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 bila index basi, tanpa menulis")
    ap.add_argument("--root", default=".", help="akar vault")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    path_index = root / NAMA_INDEX

    entri = scan_vault(root)
    lama = muat_index(path_index)
    perlu = pilih_yang_perlu_diringkas(entri, lama, full=args.full)

    if args.check:
        if perlu:
            print(f"BASI: {len(perlu)} dokumen belum terwakili di {NAMA_INDEX}")
            for e in perlu[:10]:
                print(f"  - {e['path']}")
            return 1
        print(f"SEGAR: {NAMA_INDEX} sinkron dengan {len(entri)} dokumen")
        return 0

    print(f"{len(entri)} dokumen di-scan, {len(perlu)} perlu diringkas")

    # bawa ringkasan lama untuk dokumen yang tidak berubah
    sebelumnya = {d["path"]: d for d in (lama or {}).get("dokumen", [])}
    for e in entri:
        d = sebelumnya.get(e["path"], {})
        e["ringkasan"] = d.get("ringkasan")
        e["kata_kunci"] = d.get("kata_kunci", [])

    # 🔴 Stub tidak perlu LLM
    perlu_llm = []
    for e in perlu:
        if e["status_emoji"] == "🔴":
            e.update(ringkas_stub(e["judul"]))
        else:
            perlu_llm.append(e)

    if perlu_llm:
        import anthropic
        client = anthropic.Anthropic()
        tugas = [
            {"custom_id": f"doc-{i}", "judul": e["judul"],
             "jenis": e["jenis"], "isi": e["_isi"]}
            for i, e in enumerate(perlu_llm)
        ]
        print(f"Submit batch {len(tugas)} dokumen ke {MODEL} ...")
        batch_id = submit_batch(client, tugas)
        print(f"Batch id: {batch_id}")
        hasil = ambil_hasil(client, batch_id)
        for i, e in enumerate(perlu_llm):
            r = hasil.get(f"doc-{i}")
            e["ringkasan"] = r["ringkasan"] if r else None
            e["kata_kunci"] = r["kata_kunci"] if r else []

    index = rakit_index(entri)
    path_index.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Ditulis: {path_index} ({index['jumlah_dokumen']} dokumen)")

    for p in _peringatan_status(entri):
        print(f"  PERINGATAN status hilang: {p}")
    for p in _peringatan_folder_tak_dikenal(entri):
        print(f"  PERINGATAN folder tak dikenal (publik=False): {p}")

    if index["gagal"]:
        print(f"\nGAGAL diringkas ({len(index['gagal'])}):")
        for p in index["gagal"]:
            print(f"  - {p}")
        return 1
    return 0
```

Buat `Tools/build-vault-index.py`:

```python
#!/usr/bin/env python3
"""Entry point: bangun VAULT-INDEX.json.

    python Tools/build-vault-index.py            # incremental
    python Tools/build-vault-index.py --full     # regen semua
    python Tools/build-vault-index.py --check    # exit 1 bila basi
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vault_index.build import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Jalankan tes, pastikan lulus**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft/Tools"
.venv/Scripts/python.exe -m pytest tests/ -v
```

Expected: PASS, 50 passed (19 + 18 + 8 + 13 - 8 param collapse; angka pastinya boleh berbeda, yang penting **0 failed**)

- [ ] **Step 5: Verifikasi `--check` pada vault nyata (belum ada index)**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
Tools/.venv/Scripts/python.exe Tools/build-vault-index.py --check
echo "exit code: $?"
```

Expected: `BASI: 217 dokumen belum terwakili di VAULT-INDEX.json`, exit code `1`

- [ ] **Step 6: Commit**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
git -c core.fsmonitor=false add -- Tools/vault_index/build.py Tools/build-vault-index.py Tools/tests/test_build.py
git -c core.fsmonitor=false commit -m "feat(tools): orkestrasi build + mode incremental + CLI"
```

---

### Task 5: Generate `VAULT-INDEX.json` sungguhan

**Files:**
- Create: `VAULT-INDEX.json` (di akar vault)

**Interfaces:**
- Consumes: CLI dari Task 4
- Produces: `VAULT-INDEX.json` yang dibaca Task 7

**Catatan biaya:** sekitar $1,41 sekali jalan (~400rb token input, ~33rb output, Opus 4.8 via Batches dengan diskon 50 persen). Batch bisa memakan waktu hingga satu jam.

- [ ] **Step 1: Pastikan kredensial tersedia**

```bash
ant auth status
```

Kalau belum ada profil aktif dan `ANTHROPIC_API_KEY` belum di-set, jalankan `ant auth login` dulu. **Jangan hardcode API key di berkas mana pun.**

- [ ] **Step 2: Uji coba kecil dulu (5 dokumen) sebelum membakar biaya penuh**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
mkdir -p /tmp/vault-mini/Decisions
cp Decisions/"ADR - 0001 Akuntansi via Accurate.md" /tmp/vault-mini/Decisions/
cp Decisions/"ADR - 0002 Database-per-Service.md" /tmp/vault-mini/Decisions/
cp Decisions/"ADR - 0006 Swap Jadwal Same-Department.md" /tmp/vault-mini/Decisions/
cp "Human Resource Information System/HRIS - Overtime.md" /tmp/vault-mini/
cp HOMEPAGE.md /tmp/vault-mini/
Tools/.venv/Scripts/python.exe Tools/build-vault-index.py --root /tmp/vault-mini
```

Expected: `Ditulis: /tmp/vault-mini/VAULT-INDEX.json (5 dokumen)`, exit code `0`

**Periksa manual kualitas ringkasannya.** Ringkasan harus berbentuk "Menjawab: ...", berbahasa Indonesia, dan `kata_kunci` memuat padanan dua bahasa. Kalau tidak, perbaiki `_TEMPLATE` di `summarize.py` dan ulangi langkah ini **sebelum** menjalankan yang penuh.

- [ ] **Step 3: Generate penuh**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
Tools/.venv/Scripts/python.exe Tools/build-vault-index.py --full
```

Expected: `217 dokumen di-scan, 217 perlu diringkas` lalu `Ditulis: ... (217 dokumen)`, exit code `0`.

Bila exit code `1`, baca daftar `GAGAL diringkas` dan jalankan ulang tanpa `--full` (mode incremental otomatis mencoba lagi hanya yang `ringkasan: null`).

- [ ] **Step 4: Verifikasi hasil**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
Tools/.venv/Scripts/python.exe -c "
import json
d = json.load(open('VAULT-INDEX.json', encoding='utf-8'))
print('dokumen      :', d['jumlah_dokumen'])
print('gagal        :', len(d['gagal']))
print('publik=True  :', sum(1 for x in d['dokumen'] if x['publik']))
print('publik=False :', sum(1 for x in d['dokumen'] if not x['publik']))
bocor = [x['path'] for x in d['dokumen'] if x['publik'] and x['path'].startswith(('IT/','Workspace/','Logs/','Templates/'))]
print('BOCOR        :', bocor)
print('ukuran KB    :', round(len(open('VAULT-INDEX.json',encoding='utf-8').read().encode())/1024,1))
"
```

Expected: `dokumen: 217`, `gagal: 0`, `BOCOR: []`.

**`BOCOR` harus kosong.** Kalau tidak, ada dokumen sensitif yang ditandai publik; hentikan dan perbaiki `paths.py` sebelum commit.

- [ ] **Step 5: Verifikasi `--check` sekarang bersih**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
Tools/.venv/Scripts/python.exe Tools/build-vault-index.py --check
echo "exit code: $?"
```

Expected: `SEGAR: VAULT-INDEX.json sinkron dengan 217 dokumen`, exit code `0`

- [ ] **Step 6: Commit**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
git -c core.fsmonitor=false add -- VAULT-INDEX.json
git -c core.fsmonitor=false commit -m "feat: VAULT-INDEX.json untuk 217 dokumen vault"
```

---

### Task 6: Eval set dan pengukuran recall@5

**Files:**
- Create: `Tools/eval-questions.yaml`
- Create: `Tools/eval_recall.py`
- Test: `Tools/tests/test_eval.py`

**Interfaces:**
- Consumes: `VAULT-INDEX.json`
- Produces:
  - `muat_pertanyaan(path: Path) -> list[dict]` — parse YAML, tiap item `{"tanya", "dok_benar"}`
  - `hitung_recall(hasil: list[tuple[list[str], list[str]]], k: int = 5) -> float`

**Nama berkas memakai underscore** (`eval_recall.py`, bukan `eval-recall.py`) karena harus bisa di-`import` oleh tes.

> **BLOKIR — butuh input user.** 20+ pertanyaan harus berasal dari tiket dan chat **nyata** yang pernah masuk ke tim IT. Pertanyaan karangan memakai kosakata dokumen dan menyembunyikan persis masalah retrieval yang paling nyata (staf menulis "gaji telat", dokumen menulis "payroll cutoff"). Minta user mengumpulkannya sebelum task ini dieksekusi.

- [ ] **Step 1: Tulis tes yang gagal**

Buat `Tools/tests/test_eval.py`:

```python
import pytest
import yaml
from pathlib import Path

from eval_recall import hitung_recall, muat_pertanyaan

BERKAS = Path(__file__).parent.parent / "eval-questions.yaml"


def test_hitung_recall_semua_kena():
    hasil = [(["A"], ["A", "B"]), (["C"], ["C"])]
    assert hitung_recall(hasil) == 1.0


def test_hitung_recall_separuh():
    hasil = [(["A"], ["A", "B"]), (["Z"], ["C", "D"])]
    assert hitung_recall(hasil) == 0.5


def test_hitung_recall_hormati_k():
    """Dok benar di posisi 6 tidak dihitung untuk recall@5."""
    hasil = [(["F"], ["A", "B", "C", "D", "E", "F"])]
    assert hitung_recall(hasil, k=5) == 0.0


def test_hitung_recall_kosong():
    assert hitung_recall([]) == 0.0


def test_eval_set_punya_minimal_20_pertanyaan():
    data = muat_pertanyaan(BERKAS)
    assert len(data) >= 20, "spec mensyaratkan 20+ pertanyaan NYATA"


def test_setiap_pertanyaan_punya_dok_benar():
    for item in muat_pertanyaan(BERKAS):
        assert item["tanya"].strip()
        assert item["dok_benar"], f"'{item['tanya']}' tidak punya dok_benar"


def test_dok_benar_ada_di_index():
    """Judul di dok_benar harus benar-benar ada di VAULT-INDEX.json."""
    import json
    idx = json.loads(
        (BERKAS.parent.parent / "VAULT-INDEX.json").read_text(encoding="utf-8")
    )
    judul = {d["judul"] for d in idx["dokumen"]}
    for item in muat_pertanyaan(BERKAS):
        for d in item["dok_benar"]:
            assert d in judul, f"'{d}' tidak ada di index"
```

- [ ] **Step 2: Jalankan tes, pastikan gagal**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft/Tools"
.venv/Scripts/python.exe -m pytest tests/test_eval.py -v
```

Expected: FAIL dengan `ModuleNotFoundError: No module named 'eval_recall'`

- [ ] **Step 3: Implementasi**

Buat `Tools/eval-questions.yaml` — **isi dengan pertanyaan nyata dari user**, minimal 20. Format:

```yaml
- tanya: "Berapa lama masa evaluasi karyawan PKWT?"
  dok_benar: ["HRIS - Onboarding"]

- tanya: "Kenapa pengajuan tukar shift saya ditolak?"
  dok_benar: ["ADR - 0006 Swap Jadwal Same-Department"]

- tanya: "Gaji saya telat cair, kenapa?"
  dok_benar: ["HRIS - Payroll"]
```

Buat `Tools/eval_recall.py`:

```python
"""Ukur recall@5 pemilihan dokumen terhadap eval set."""

from pathlib import Path

import yaml


def muat_pertanyaan(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or []


def hitung_recall(hasil: list[tuple[list[str], list[str]]], k: int = 5) -> float:
    """hasil = [(dok_benar, dok_terpilih_terurut), ...]

    Satu pertanyaan dihitung 'kena' bila minimal satu dok_benar
    muncul di k teratas.
    """
    if not hasil:
        return 0.0
    kena = sum(
        1 for benar, terpilih in hasil
        if set(benar) & set(terpilih[:k])
    )
    return kena / len(hasil)
```

- [ ] **Step 4: Jalankan tes, pastikan lulus**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft/Tools"
.venv/Scripts/python.exe -m pytest tests/test_eval.py -v
```

Expected: PASS, 7 passed

- [ ] **Step 5: Ukur recall@5 secara manual**

Untuk setiap pertanyaan di `eval-questions.yaml`, jalankan sesi agent terpisah dengan prompt:

```
Baca architecture-draft/VAULT-INDEX.json. Untuk pertanyaan berikut, sebutkan
5 judul dokumen paling relevan, terurut dari paling relevan. Jawab HANYA
dengan daftar judul, tanpa penjelasan, tanpa membaca dokumennya.

Pertanyaan: <tanya>
```

Catat hasilnya, lalu hitung:

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft/Tools"
.venv/Scripts/python.exe -c "
from eval_recall import hitung_recall
hasil = [
    (['HRIS - Onboarding'], ['HRIS - Onboarding', '...']),
    # ...isi seluruh hasil pengukuran
]
print('recall@5 =', round(hitung_recall(hasil) * 100, 1), '%')
"
```

- [ ] **Step 6: Catat hasil dan ambil keputusan fase 3**

Tambahkan bagian berikut ke akhir spec (`.agent-kit/docs/2026-07-20-vault-index-rag-design.md`), isi angkanya:

```markdown
## Hasil Eval (diisi setelah Task 6)

- Tanggal ukur: <YYYY-MM-DD>
- Jumlah pertanyaan: <N>
- **recall@5: <X>%**
- **Keputusan fase 3**: <"Berhenti di fase 1" bila ≥85%, atau "Naik ke fase 3a (BM25)" bila <85%>
- Pertanyaan yang meleset dan dugaan sebabnya:
  - <daftar>
```

- [ ] **Step 7: Commit**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
git -c core.fsmonitor=false add -- Tools/eval-questions.yaml Tools/eval_recall.py Tools/tests/test_eval.py ".agent-kit/docs/2026-07-20-vault-index-rag-design.md"
git -c core.fsmonitor=false commit -m "feat(tools): eval set + pengukuran recall@5"
```

---

### Task 7: Ubah `/ask` dan `/start-task` di agent-kit

**Files:**
- Modify: `.agent-kit/commands/ask.md:11-18`
- Modify: `.agent-kit/commands/start-task.md:11-17`
- Modify: `.agent-kit/commands/sync-docs.md` (tambah gate `--check`)
- Modify: `.agent-kit/VERSION` (1.4.0 → 1.5.0)

**Interfaces:**
- Consumes: `VAULT-INDEX.json` dari Task 5

> **Ditulis di `.agent-kit/`, BUKAN di `erp/.claude/`.** Berkas di `.claude/` di-generate `init` dan akan tertimpa.

- [ ] **Step 1: Ubah `ask.md`**

Ganti langkah 1 dan 2 di `.agent-kit/commands/ask.md`. Dari:

```
1. Tentukan area pertanyaan. Buka `architecture-draft/CLAUDE.md` §7 (pemetaan repo→dokumen)
   untuk menemukan dok arsitektur relevan.
2. Baca dok vault terkait di `architecture-draft/`. Perhatikan status marker
   (§5: ✅ Implemented / ⚠️ ada catatan / 🟡 Konsep / 🔴 Stub).
```

Menjadi:

```
1. Baca `architecture-draft/VAULT-INDEX.json`. Pilih **3 sampai 5 dokumen** paling
   relevan berdasarkan `ringkasan` dan `kata_kunci`. Bila index tidak ada, rusak,
   atau `versi_skema` tidak dikenal → kembali ke cara lama (`architecture-draft/CLAUDE.md`
   §7 + grep) dan **beri tahu user** bahwa index tidak tersedia.
2. Baca dokumen terpilih **secara utuh** di `architecture-draft/`. Perhatikan
   `status_emoji` + `status_teks` pada entri index dan marker di dokumennya
   (✅ / ⚠️ / 🟡 / 🔴 / 🔜 / ⛔). Catatan: 69 dari 217 dokumen memang tidak punya
   status (seluruh dok meta root dan seluruh `API - *`); itu normal, bukan gap.
   Bila pertanyaannya menyangkut kode, `CLAUDE.md` §7 tetap dipakai untuk memetakan
   repo → dokumen — index memetakan pertanyaan → dokumen, keduanya berbeda sumbu.
```

- [ ] **Step 2: Ubah `start-task.md`**

Ganti langkah 2 dan 3. Dari:

```
2. Buka `architecture-draft/CLAUDE.md` §7 (pemetaan repo→dokumen) → tentukan dokumen
   arsitektur yang relevan dengan project & task ini.
3. Baca dokumen arsitektur terkait di `architecture-draft/`. Perhatikan status marker
   (✅ Implemented / ⚠️ ada catatan / 🟡 Konsep / 🔴 Stub) untuk menilai mana yang nyata.
```

Menjadi:

```
2. Tentukan dokumen relevan dari **dua arah**:
   a. `architecture-draft/CLAUDE.md` §7 → pemetaan repo kode ke dokumen.
   b. `architecture-draft/VAULT-INDEX.json` → cocokkan deskripsi task dengan
      `ringkasan` dan `kata_kunci`, ambil 3 sampai 5 kandidat.
   Gabungkan keduanya. Bila index tidak tersedia, pakai (a) saja dan beri tahu user.
3. Baca dokumen terpilih secara utuh. Perhatikan status marker
   (✅ / ⚠️ / 🟡 / 🔴 / 🔜 / ⛔) untuk menilai mana yang nyata dan mana yang rencana.
   Dokumen tanpa status (dok meta root, `API - *`) itu normal.
```

- [ ] **Step 3: Tambah gate `--check` di `sync-docs.md`**

Tambahkan sebagai langkah terakhir sebelum commit:

```
- Setelah dokumen diperbarui, jalankan:
  `Tools/.venv/Scripts/python.exe Tools/build-vault-index.py`
  lalu `... --check` untuk memastikan `VAULT-INDEX.json` sinkron.
  Ikutkan `VAULT-INDEX.json` dalam commit. Index basi lebih berbahaya daripada
  tidak ada index, karena agent akan mempercayai ringkasan yang salah.
```

- [ ] **Step 4: Naikkan versi kit**

Isi `.agent-kit/VERSION` dengan `1.5.0`.

- [ ] **Step 5: Verifikasi manual**

```bash
cd "c:/Data utama/Aplikasi/Office/erp"
```

Jalankan `/ask Bagaimana alur pengajuan lembur?` di sesi Claude Code baru.

Expected: agent membaca `VAULT-INDEX.json` **lebih dulu**, menyebut dokumen yang dipilihnya, baru membaca dokumen itu. Jawaban tetap menyertakan **Sumber** dan **Status** seperti sebelumnya.

Lalu uji degradasi:

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
mv VAULT-INDEX.json VAULT-INDEX.json.bak
```

Jalankan `/ask` lagi. Expected: agent memberi tahu index tidak tersedia dan tetap menjawab lewat cara lama. Lalu:

```bash
mv VAULT-INDEX.json.bak VAULT-INDEX.json
```

- [ ] **Step 6: Commit**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
git -c core.fsmonitor=false add -- ".agent-kit/commands/ask.md" ".agent-kit/commands/start-task.md" ".agent-kit/commands/sync-docs.md" ".agent-kit/VERSION"
git -c core.fsmonitor=false commit -m "feat(kit): /ask dan /start-task pilih dokumen lewat VAULT-INDEX.json (v1.5.0)"
```

---

### Task 8: Dokumentasi dan penutup

**Files:**
- Create: `Tools/README.md`
- Modify: `architecture-draft/CLAUDE.md` (tambah bagian tentang index)

- [ ] **Step 1: Tulis `Tools/README.md`**

```markdown
# Tools — Vault Index

Generator `VAULT-INDEX.json`, manifest pencarian untuk seluruh vault.
Desain lengkap: `.agent-kit/docs/2026-07-20-vault-index-rag-design.md`

## Setup

```bash
py -3 -m venv Tools/.venv
Tools/.venv/Scripts/python.exe -m pip install -r Tools/requirements.txt
```

Kredensial Anthropic lewat `ant auth login` atau `ANTHROPIC_API_KEY`.
Jangan hardcode key.

## Pemakaian

| Perintah | Fungsi |
|---|---|
| `python Tools/build-vault-index.py` | Incremental: hanya dokumen yang hash-nya berubah |
| `python Tools/build-vault-index.py --full` | Regen semua (~$1,41 via Batches) |
| `python Tools/build-vault-index.py --check` | Exit 1 bila index basi, tanpa menulis |

Dipanggil otomatis di akhir `/sync-docs`.

## Tes

```bash
cd Tools && .venv/Scripts/python.exe -m pytest tests/ -v
```

## Yang perlu diingat

- **Fail-closed**: folder yang belum diklasifikasi di `vault_index/paths.py`
  otomatis `publik: false`. Menambah folder domain baru? Daftarkan di `KLASIFIKASI`.
- **Status disimpan mentah**, tidak dinormalisasi. Enam emoji dipakai di vault
  (✅ ⚠️ 🟡 🔴 🔜 ⛔) dan 69 dari 217 dokumen memang tidak punya status.
- **`IT/` tidak pernah `publik: true`** — memuat kredensial plaintext yang
  disengaja untuk tim IT, tapi tidak boleh masuk kanal chat tim non-IT.
```

- [ ] **Step 2: Tambah rujukan di `architecture-draft/CLAUDE.md`**

Sisipkan setelah bagian §7 (pemetaan repo → dokumen):

```markdown
## 7b. Index pencarian (`VAULT-INDEX.json`)

Manifest seluruh dokumen vault: judul, area, jenis, status, tautan, ringkasan,
dan kata kunci. Dipakai agent untuk memilih dokumen relevan dari sebuah
**pertanyaan** (§7 memetakan dari **repo kode**; keduanya berbeda sumbu dan
saling melengkapi).

Diregenerasi oleh `Tools/build-vault-index.py`, wajib ikut ter-commit tiap
`/sync-docs`. Jangan diedit tangan. Detail: `Tools/README.md`.
```

- [ ] **Step 3: Jalankan seluruh tes terakhir kali**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft/Tools"
.venv/Scripts/python.exe -m pytest tests/ -v
```

Expected: semua PASS, 0 failed

- [ ] **Step 4: Verifikasi wikilink vault tetap 0 broken**

Rulebook vault §4 mewajibkan seluruh wikilink resolve. Task ini menambah
heading baru di `CLAUDE.md` tanpa wikilink, jadi seharusnya aman, tapi verifikasi:

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
Tools/.venv/Scripts/python.exe -c "
import sys, json; sys.path.insert(0,'Tools')
from pathlib import Path
d = json.load(open('VAULT-INDEX.json', encoding='utf-8'))
judul = {x['judul'] for x in d['dokumen']}
rusak = [(x['path'], t) for x in d['dokumen'] for t in x['tautan'] if t not in judul]
print('wikilink rusak:', len(rusak))
for p, t in rusak[:20]: print(' ', p, '->', t)
"
```

Catatan: sebagian "rusak" akan menunjuk ke dokumen di `Additional documents/`
atau cache Shopee yang sengaja tidak ter-index. Periksa daftarnya; hanya
tautan ke dokumen yang benar-benar tidak ada yang perlu dilaporkan ke user.

- [ ] **Step 5: Commit**

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
git -c core.fsmonitor=false add -- Tools/README.md CLAUDE.md
git -c core.fsmonitor=false commit -m "docs: dokumentasi Tools/ dan rujukan VAULT-INDEX.json di rulebook"
```

- [ ] **Step 6: Lapor ke user, jangan push sendiri**

Ringkas ke user: jumlah commit, angka recall@5, keputusan fase 3, dan
sisa pekerjaan. **Tanyakan dulu sebelum `git push`** — vault dikerjakan
banyak orang dan `main` sudah dipakai bersama. Bila user setuju:

```bash
cd "c:/Data utama/Aplikasi/Office/erp/architecture-draft"
git -c core.fsmonitor=false pull --rebase
git -c core.fsmonitor=false push
```

---

## Urutan Eksekusi dan Ketergantungan

```
Task 1 (paths)  ──┐
Task 2 (parsing) ─┼──> Task 4 (build+CLI) ──> Task 5 (generate) ──┬──> Task 6 (eval) ──> Task 8 (dok)
Task 3 (LLM)    ──┘                                               └──> Task 7 (commands) ──┘
```

- Task 1, 2, 3 saling independen dan bisa dikerjakan paralel.
- Task 5 memerlukan kredensial API dan memakan biaya nyata; jangan dijalankan sebelum Task 4 hijau.
- **Task 6 diblokir input user** (20+ pertanyaan nyata). Task 7 boleh jalan lebih dulu bila pertanyaan belum siap.
