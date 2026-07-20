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
