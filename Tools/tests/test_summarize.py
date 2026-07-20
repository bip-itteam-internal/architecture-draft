import json
from types import SimpleNamespace

import vault_index.summarize as summarize
from vault_index.summarize import (
    MODEL, bangun_prompt, SKEMA_RINGKASAN, ringkas_stub, _parse_isi_pesan,
    submit_batch, ambil_hasil,
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


# --- submit_batch: konstruksi request, tanpa panggilan API sungguhan ---

class _FakeBatches:
    """Stub permukaan client.messages.batches yang dipakai submit_batch/ambil_hasil."""

    def __init__(self, batch_id="batch_abc123", retrieve_statuses=None, results=None):
        self.batch_id = batch_id
        self.create_calls: list = []
        self._retrieve_statuses = list(retrieve_statuses or ["ended"])
        self.retrieve_calls = 0
        self._results = results or []

    def create(self, requests):
        self.create_calls.append(requests)
        return SimpleNamespace(id=self.batch_id)

    def retrieve(self, batch_id):
        self.retrieve_calls += 1
        status = self._retrieve_statuses.pop(0) if self._retrieve_statuses else "ended"
        return SimpleNamespace(id=batch_id, processing_status=status)

    def results(self, batch_id):
        return iter(self._results)


class _FakeClient:
    def __init__(self, batches: _FakeBatches):
        self.messages = SimpleNamespace(batches=batches)


def _tugas_contoh() -> list[dict]:
    return [
        {"custom_id": "doc-1", "judul": "HRIS - Overtime", "jenis": "domain", "isi": "isi 1"},
        {"custom_id": "doc-2", "judul": "IT - Network", "jenis": "domain", "isi": "isi 2"},
    ]


def test_submit_batch_mengembalikan_batch_id_dari_client():
    batches = _FakeBatches(batch_id="batch_xyz")
    client = _FakeClient(batches)
    assert submit_batch(client, _tugas_contoh()) == "batch_xyz"


def test_submit_batch_jumlah_request_sesuai_jumlah_tugas():
    batches = _FakeBatches()
    client = _FakeClient(batches)
    submit_batch(client, _tugas_contoh())
    assert len(batches.create_calls) == 1
    requests = list(batches.create_calls[0])
    assert len(requests) == 2


def test_submit_batch_tiap_request_custom_id_model_dan_output_config_benar():
    tugas = _tugas_contoh()
    batches = _FakeBatches()
    client = _FakeClient(batches)
    submit_batch(client, tugas)
    requests = list(batches.create_calls[0])
    for t, req in zip(tugas, requests):
        assert req["custom_id"] == t["custom_id"]
        assert req["params"]["model"] == "claude-opus-4-8"
        assert req["params"]["output_config"] == {
            "format": {"type": "json_schema", "schema": SKEMA_RINGKASAN}
        }


def test_submit_batch_prompt_memuat_judul_dokumen_bersangkutan():
    tugas = _tugas_contoh()
    batches = _FakeBatches()
    client = _FakeClient(batches)
    submit_batch(client, tugas)
    requests = list(batches.create_calls[0])
    for t, req in zip(tugas, requests):
        konten = req["params"]["messages"][0]["content"]
        assert t["judul"] in konten


# --- ambil_hasil: polling + pemetaan hasil, tanpa panggilan API sungguhan dan
# tanpa tidur sungguhan ---

def _baris_sukses(custom_id: str, ringkasan: str, kata_kunci: list[str]) -> SimpleNamespace:
    teks = json.dumps({"ringkasan": ringkasan, "kata_kunci": kata_kunci})
    return SimpleNamespace(
        custom_id=custom_id,
        result=SimpleNamespace(
            type="succeeded",
            message=SimpleNamespace(content=[SimpleNamespace(type="text", text=teks)]),
        ),
    )


def _baris_gagal(custom_id: str, tipe: str) -> SimpleNamespace:
    return SimpleNamespace(custom_id=custom_id, result=SimpleNamespace(type=tipe))


def test_ambil_hasil_sukses_memetakan_custom_id_ke_ringkasan_dan_kata_kunci():
    baris = _baris_sukses("doc-1", "Menjawab X.", ["a", "b"])
    batches = _FakeBatches(results=[baris])
    client = _FakeClient(batches)
    hasil = ambil_hasil(client, "batch_1", interval=0)
    assert hasil == {"doc-1": {"ringkasan": "Menjawab X.", "kata_kunci": ["a", "b"]}}


def test_ambil_hasil_result_type_errored_kembalikan_none():
    baris = _baris_gagal("doc-1", "errored")
    batches = _FakeBatches(results=[baris])
    client = _FakeClient(batches)
    hasil = ambil_hasil(client, "batch_1", interval=0)
    assert hasil == {"doc-1": None}


def test_ambil_hasil_result_type_canceled_dan_expired_kembalikan_none():
    baris = [_baris_gagal("doc-1", "canceled"), _baris_gagal("doc-2", "expired")]
    batches = _FakeBatches(results=baris)
    client = _FakeClient(batches)
    hasil = ambil_hasil(client, "batch_1", interval=0)
    assert hasil == {"doc-1": None, "doc-2": None}


def test_ambil_hasil_teks_bukan_json_valid_kembalikan_none():
    baris = SimpleNamespace(
        custom_id="doc-1",
        result=SimpleNamespace(
            type="succeeded",
            message=SimpleNamespace(
                content=[SimpleNamespace(type="text", text="bukan json")]
            ),
        ),
    )
    batches = _FakeBatches(results=[baris])
    client = _FakeClient(batches)
    hasil = ambil_hasil(client, "batch_1", interval=0)
    assert hasil == {"doc-1": None}


def test_ambil_hasil_polling_menunggu_sampai_status_ended(monkeypatch):
    """retrieve mengembalikan status non-ended dua kali lalu ended: fungsi harus
    menunggu (bukan berhenti lebih awal) lalu lanjut ambil hasil. time.sleep
    ditambal supaya tes ini tidak benar-benar tidur."""
    tidur: list[float] = []
    monkeypatch.setattr(summarize.time, "sleep", lambda s: tidur.append(s))

    baris = _baris_sukses("doc-1", "Menjawab X.", [])
    batches = _FakeBatches(
        retrieve_statuses=["in_progress", "in_progress", "ended"],
        results=[baris],
    )
    client = _FakeClient(batches)

    hasil = ambil_hasil(client, "batch_1", interval=0)

    assert hasil == {"doc-1": {"ringkasan": "Menjawab X.", "kata_kunci": []}}
    assert batches.retrieve_calls == 3
    assert len(tidur) == 2
