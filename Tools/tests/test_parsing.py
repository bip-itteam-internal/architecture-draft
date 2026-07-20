import re
from pathlib import Path

from vault_index.parsing import (
    ekstrak_status, ekstrak_wikilink, ekstrak_heading,
    hitung_hash, potong_untuk_llm,
)

VAULT_ROOT = Path(__file__).resolve().parents[2]


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


def test_ekstrak_heading_lewati_pagar_backtick():
    """'#' di dalam blok ``` bukan heading, mis. komentar shell."""
    teks = (
        "# Judul\n\n"
        "```\n"
        "# ini komentar shell di dalam kode, bukan heading\n"
        "```\n"
    )
    assert ekstrak_heading(teks) == ["# Judul"]


def test_ekstrak_heading_lewati_pagar_tilde():
    """Pembatas ~~~ juga harus dikenali, bukan cuma ```."""
    teks = (
        "# Judul\n\n"
        "~~~\n"
        "# ini juga bukan heading\n"
        "~~~\n"
    )
    assert ekstrak_heading(teks) == ["# Judul"]


def test_ekstrak_heading_pagar_dengan_info_string():
    """Fence dengan info string (```python) tetap dikenali sebagai pagar."""
    teks = (
        "# Judul\n\n"
        "```python\n"
        "# komentar python, bukan heading\n"
        "```\n"
        "## Bagian Setelah\n"
    )
    assert ekstrak_heading(teks) == ["# Judul", "## Bagian Setelah"]


def test_ekstrak_heading_pagar_lebih_dari_tiga_karakter():
    """Fence 4 backtick memuat literal ``` di isinya (nested, tak menutup)."""
    teks = (
        "# Judul\n\n"
        "````\n"
        "```\n"
        "# masih di dalam kode, fence 3 backtick tak cukup menutup fence 4\n"
        "```\n"
        "````\n"
        "## Setelah\n"
    )
    assert ekstrak_heading(teks) == ["# Judul", "## Setelah"]


def test_ekstrak_heading_setelah_blok_ditutup_tertangkap_lagi():
    teks = (
        "# Judul\n\n"
        "```\n"
        "# bukan heading\n"
        "```\n\n"
        "## Bagian Kedua\n"
    )
    assert ekstrak_heading(teks) == ["# Judul", "## Bagian Kedua"]


def test_ekstrak_heading_pagar_tak_tertutup_sisa_dokumen_dianggap_kode():
    """Fence yang tak pernah ditutup: sisa dokumen dianggap masih kode."""
    teks = (
        "# Judul\n\n"
        "```\n"
        "# bukan heading\n"
        "## juga bukan heading, fence tak pernah ditutup\n"
    )
    assert ekstrak_heading(teks) == ["# Judul"]


def test_ekstrak_heading_dokumen_vault_nyata_run_deploy_task_management():
    """Regresi nyata: RUN - Deploy Task Management Service.md punya dua
    komentar shell ('# (di host ...) dump ...' dan '# restore ke container
    prod ...') di dalam blok ```bash yang sebelum perbaikan tertangkap
    sebagai heading palsu (lihat inspect_headings pra-fix: 16 heading,
    2 di antaranya adalah komentar shell ini)."""
    path = VAULT_ROOT / "Runbooks" / "RUN - Deploy Task Management Service.md"
    teks = path.read_text(encoding="utf-8")
    heading = ekstrak_heading(teks)

    komentar_shell_1 = (
        "# (di host yg menjangkau mongo lama) dump — pakai --user "
        "agar izin volume host tak menolak"
    )
    komentar_shell_2 = "# restore ke container prod, rename db → task_management_db"
    assert komentar_shell_1 not in heading
    assert komentar_shell_2 not in heading

    # heading asli tetap tertangkap, termasuk yang persis sebelum/sesudah
    # blok kode yang mengandung komentar shell tadi
    assert "## 3. Database (task_management_db)" in heading
    assert "## 4. WebSocket ingress (untuk realtime FE)" in heading


# --- hash ---

def test_hash_stabil_dan_idempoten():
    assert hitung_hash("isi") == hitung_hash("isi")


def test_hash_berbeda_untuk_isi_berbeda():
    assert hitung_hash("isi a") != hitung_hash("isi b")


def test_hash_panjang_64_karakter_heksadesimal():
    h = hitung_hash("isi apa saja")
    assert len(h) == 64
    assert re.fullmatch(r"[0-9a-f]{64}", h)


def test_hash_cocok_vektor_sha256_dikenal():
    """Vektor dihitung via hashlib.sha256(...).hexdigest() di shell,
    bukan dari ingatan. Mengunci hitung_hash memang SHA-256, bukan
    fungsi deterministik lain (mis. identitas atau len(teks))."""
    assert hitung_hash("abc") == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )
    assert hitung_hash("") == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_hash_meng_hash_bytes_utf8_bukan_representasi_lain():
    """Vault penuh emoji: hitung_hash harus meng-hash bytes UTF-8 dari
    teks, bukan repr()/str lain yang kebetulan juga deterministik."""
    teks = "Status: ✅ selesai 😀 café — naïve résumé"
    assert hitung_hash(teks) == (
        "1bcd1471745209ef31f3b9ecd52e49e5bbb75d8c2ebbcd9eabae8923d0888389"
    )


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
