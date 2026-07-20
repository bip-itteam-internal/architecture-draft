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
