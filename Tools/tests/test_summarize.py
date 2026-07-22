import json
import sys

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


# --- validasi tipe: manifest hilir berasumsi ringkasan=str, kata_kunci=list[str] ---
# Makin penting sekarang: input datang dari berkas JSON yang ditulis agent
# (--serap), bukan lagi dari structured output API yang dibatasi skema.

def test_parse_isi_pesan_ringkasan_bukan_string_ditolak():
    """ringkasan angka lolos cek keberadaan key tapi salah tipe untuk manifest."""
    isi = json.dumps({"ringkasan": 5, "kata_kunci": []})
    assert _parse_isi_pesan(isi) is None


def test_parse_isi_pesan_kata_kunci_elemen_bukan_string_ditolak():
    isi = json.dumps({"ringkasan": "x", "kata_kunci": [1, 2, 3]})
    assert _parse_isi_pesan(isi) is None


def test_parse_isi_pesan_kata_kunci_elemen_objek_ditolak():
    isi = json.dumps({"ringkasan": "x", "kata_kunci": [{"a": 1}]})
    assert _parse_isi_pesan(isi) is None


def test_parse_isi_pesan_valid_dengan_kata_kunci_string_lolos():
    isi = json.dumps({"ringkasan": "Menjawab: bagaimana X.", "kata_kunci": ["a", "b"]})
    assert _parse_isi_pesan(isi) == {
        "ringkasan": "Menjawab: bagaimana X.", "kata_kunci": ["a", "b"]
    }


def test_parse_isi_pesan_ringkasan_kosong_ditolak():
    """String kosong (atau whitespace saja) bukan ringkasan yang berguna untuk
    retrieval; manifest yang memuat entri semacam ini gagal jauh dari sumbernya.
    Ditolak di titik ini, bukan diteruskan sebagai `str` kosong yang lolos tipe."""
    assert _parse_isi_pesan(json.dumps({"ringkasan": "", "kata_kunci": []})) is None
    assert _parse_isi_pesan(json.dumps({"ringkasan": "   ", "kata_kunci": []})) is None


# --- anti-regresi: jalur berbayar (Batches API) benar-benar hilang, bukan cuma
# tak terpakai. Task 10 menghapus seluruh mesin API -- modul ini tidak boleh
# lagi bisa menyentuh jaringan sama sekali. ---

def test_summarize_tidak_mengimpor_anthropic():
    assert "anthropic" not in sys.modules
    import vault_index.summarize as summarize
    assert "anthropic" not in sys.modules
    assert not hasattr(summarize, "anthropic")


def test_submit_batch_dan_ambil_hasil_tidak_ada_lagi():
    import vault_index.summarize as summarize
    assert not hasattr(summarize, "submit_batch")
    assert not hasattr(summarize, "ambil_hasil")
    assert not hasattr(summarize, "MAX_TOKENS")
