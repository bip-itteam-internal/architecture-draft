"""Ekstraksi deterministik dari isi dokumen markdown."""

import hashlib
import re

# Enam emoji yang benar-benar dipakai di vault (terukur 2026-07-20):
# 🟡 58 · ✅ 43 · ⚠️ 34 · 🔴 7 · 🔜 1 · ⛔ 1
EMOJI_STATUS: frozenset[str] = frozenset({"✅", "⚠️", "🟡", "🔴", "🔜", "⛔"})

BARIS_KEPALA = 15

# Prefix `>` diizinkan karena vault memakai DUA format status yang sama-sama sah,
# ditetapkan oleh templatenya masing-masing: `Template - Implementasi Service`
# memakai bullet di dalam `## Deskripsi`, sedangkan `Template - Runbook` memakai
# blockquote di baris pertama. Tanpa cabang ini seluruh 12 runbook (plus 3 ADR,
# 2 dok Application, dan 1 Sales) terbaca tanpa status — dan `_peringatan_status`
# dulu tak memeriksa runbook, jadi salah bacanya tak pernah bersuara.
# `*` bukan `?`: blockquote bersarang (`> >`) ikut terbaca.
# Urutan `>` sebelum `-` mengikuti markdown: `> - **Status**` sah, kebalikannya tidak.
_RE_STATUS = re.compile(
    r"^\s*(?:>\s*)*(?:-\s*)?(?:\*\*)?Status(?:\*\*)?\s*:\s*(\S+)[ \t]*(.*)$",
    re.MULTILINE,
)
_RE_WIKILINK = re.compile(r"(?<!!)\[\[([^\]|#]+)")
_RE_HEADING_LINE = re.compile(r"^#{1,6} .+$")
_RE_FENCE = re.compile(r"^(`{3,}|~{3,})")


def ekstrak_status(teks: str) -> tuple[str | None, str | None]:
    """Ambil (status_emoji, status_teks) mentah dari kepala dokumen.

    Status TIDAK dinormalisasi: kosakata ADR (Accepted/Proposed/Superseded)
    berbeda dari kosakata domain (Implemented/Konsep/Stub).

    Absennya status adalah kondisi normal — sekitar sepertiga korpus
    (seluruh dok meta root dan seluruh `API - *`).
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
    """Baris heading (# .. ######), melewati isi fenced code block.

    Pembatas ``` maupun ~~~ dikenali, termasuk fence dengan info string
    (```python) dan fence >3 karakter (```` menutup literal ``` di
    dalamnya). Fence hanya ditutup oleh pembatas jenis sama dengan
    panjang >= pembukanya dan tanpa isi lain di baris penutup. Fence
    yang tak pernah ditutup membuat sisa dokumen dianggap kode.
    """
    hasil: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in teks.splitlines():
        m = _RE_FENCE.match(line.lstrip())
        if m:
            marker = m.group(1)
            if not in_fence:
                in_fence = True
                fence_char = marker[0]
                fence_len = len(marker)
            elif (
                marker[0] == fence_char
                and len(marker) >= fence_len
                and line.lstrip()[len(marker):].strip() == ""
            ):
                in_fence = False
                fence_char = ""
                fence_len = 0
            continue

        if in_fence:
            continue

        if _RE_HEADING_LINE.match(line):
            hasil.append(line)

    return hasil


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
