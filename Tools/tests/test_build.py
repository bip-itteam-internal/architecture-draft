import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import vault_index.build as build
from vault_index.build import (
    VERSI_SKEMA, NAMA_INDEX, NAMA_SIDECAR, scan_vault, muat_index,
    pilih_yang_perlu_diringkas, rakit_index,
    _peringatan_status, _peringatan_folder_tak_dikenal,
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


def test_rakit_index_buang_field_internal(vault_mini):
    """Field berawalan _ (mis. _isi) tidak boleh bocor ke JSON."""
    entri = [{**e, "ringkasan": "r", "kata_kunci": []} for e in scan_vault(vault_mini)]
    idx = rakit_index(entri)
    for d in idx["dokumen"]:
        assert not any(k.startswith("_") for k in d)


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


def test_peringatan_status_menandai_domain_tanpa_status():
    entri = [
        {"path": "a.md", "jenis": "domain", "status_emoji": None, "status_teks": None},
        {"path": "b.md", "jenis": "adr", "status_emoji": None, "status_teks": None},
        {"path": "c.md", "jenis": "domain", "status_emoji": "✅", "status_teks": None},
        {"path": "d.md", "jenis": "meta", "status_emoji": None, "status_teks": None},
        {"path": "e.md", "jenis": "domain", "status_emoji": None, "status_teks": "prosa"},
    ]
    assert _peringatan_status(entri) == ["a.md", "b.md"]


def test_peringatan_folder_tak_dikenal_menandai_jenis_none():
    entri = [
        {"path": "a.md", "jenis": None},
        {"path": "b.md", "jenis": "domain"},
        {"path": "c.md", "jenis": None},
    ]
    assert _peringatan_folder_tak_dikenal(entri) == ["a.md", "c.md"]


# --- main(): sidecar batch_id, offline, tanpa jaringan sungguhan --------------
#
# Objek palsu bergaya SimpleNamespace yang sama dipakai di test_summarize.py,
# tapi didefinisikan lokal di sini (bukan diimpor) karena main() menyuntikkan
# client lewat `vault_index.build.anthropic.Anthropic()`, bukan lewat
# `client.messages.batches` langsung seperti submit_batch/ambil_hasil.


class _FakeBatches:
    """Stub permukaan client.messages.batches. `retrieve_raises` dipakai untuk
    membuktikan sidecar sudah tertulis SEBELUM polling pertama dilakukan."""

    def __init__(self, batch_id="batch_abc123", retrieve_statuses=None,
                 results=None, retrieve_raises=None):
        self.batch_id = batch_id
        self.create_calls: list = []
        self._retrieve_statuses = list(retrieve_statuses or ["ended"])
        self.retrieve_calls = 0
        self._results = results or []
        self._retrieve_raises = retrieve_raises

    def create(self, requests):
        self.create_calls.append(list(requests))
        return SimpleNamespace(id=self.batch_id)

    def retrieve(self, batch_id):
        self.retrieve_calls += 1
        if self._retrieve_raises is not None and self.retrieve_calls == 1:
            raise self._retrieve_raises
        status = self._retrieve_statuses.pop(0) if self._retrieve_statuses else "ended"
        return SimpleNamespace(id=batch_id, processing_status=status)

    def results(self, batch_id):
        return iter(self._results)


class _FakeClient:
    def __init__(self, batches: _FakeBatches):
        self.messages = SimpleNamespace(batches=batches)


class _FakeAnthropicModule:
    """Menggantikan `vault_index.build.anthropic` -- main() memanggil
    `anthropic.Anthropic()` untuk membuat client."""

    def __init__(self, client: _FakeClient):
        self._client = client

    def Anthropic(self):
        return self._client


def _baris_sukses(custom_id: str, ringkasan: str) -> SimpleNamespace:
    teks = json.dumps({"ringkasan": ringkasan, "kata_kunci": []})
    return SimpleNamespace(
        custom_id=custom_id,
        result=SimpleNamespace(
            type="succeeded",
            message=SimpleNamespace(content=[SimpleNamespace(type="text", text=teks)]),
        ),
    )


@pytest.fixture
def vault_batch(tmp_path: Path) -> Path:
    """Vault kecil dengan dua dokumen non-stub -> keduanya perlu LLM (tanpa
    index lama), cukup untuk memicu jalur submit batch."""
    (tmp_path / "Sales").mkdir()
    (tmp_path / "Sales" / "Sales - A.md").write_text(
        "- **Status**: ✅ Implemented\n\nIsi A.\n", encoding="utf-8",
    )
    (tmp_path / "Sales" / "Sales - B.md").write_text(
        "- **Status**: ✅ Implemented\n\nIsi B.\n", encoding="utf-8",
    )
    return tmp_path


def _tulis_sidecar_mentah(root: Path, batch_id: str, tugas: list[dict]) -> Path:
    p = root / NAMA_SIDECAR
    p.write_text(json.dumps({
        "batch_id": batch_id,
        "disubmit_pada": "2026-01-01T00:00:00+00:00",
        "tugas": tugas,
    }), encoding="utf-8")
    return p


def test_sidecar_ditulis_sebelum_polling_dimulai(vault_batch, monkeypatch):
    """Bukti inti perbaikan B1: kalau proses mati PERSIS saat polling pertama
    (retrieve melempar exception), batch_id sudah aman di disk, bukan cuma di
    memori/stdout."""
    batches = _FakeBatches(batch_id="batch_xyz", retrieve_raises=RuntimeError("mati"))
    client = _FakeClient(batches)
    monkeypatch.setattr(build, "anthropic", _FakeAnthropicModule(client))
    monkeypatch.setattr(build.time, "sleep", lambda s: None)

    with pytest.raises(RuntimeError):
        build.main(["--root", str(vault_batch)])

    assert (vault_batch / NAMA_SIDECAR).exists()
    assert not (vault_batch / NAMA_INDEX).exists()


def test_sidecar_memuat_batch_id_dan_peta_custom_id_path(vault_batch, monkeypatch):
    batches = _FakeBatches(batch_id="batch_xyz", retrieve_raises=RuntimeError("mati"))
    client = _FakeClient(batches)
    monkeypatch.setattr(build, "anthropic", _FakeAnthropicModule(client))
    monkeypatch.setattr(build.time, "sleep", lambda s: None)

    with pytest.raises(RuntimeError):
        build.main(["--root", str(vault_batch)])

    sidecar = json.loads((vault_batch / NAMA_SIDECAR).read_text(encoding="utf-8"))
    assert sidecar["batch_id"] == "batch_xyz"
    peta = {t["custom_id"]: t["path"] for t in sidecar["tugas"]}
    assert peta == {
        "doc-0": "Sales/Sales - A.md",
        "doc-1": "Sales/Sales - B.md",
    }


def test_sidecar_tertinggal_blok_submit_baru(vault_batch, monkeypatch, capsys):
    """Jaring pengaman utama: sidecar tertinggal -> JANGAN submit batch baru."""
    _tulis_sidecar_mentah(vault_batch, "batch_lama", [
        {"custom_id": "doc-0", "path": "Sales/Sales - A.md"},
        {"custom_id": "doc-1", "path": "Sales/Sales - B.md"},
    ])
    batches = _FakeBatches()
    client = _FakeClient(batches)
    monkeypatch.setattr(build, "anthropic", _FakeAnthropicModule(client))
    monkeypatch.setattr(build.time, "sleep", lambda s: None)

    kode = build.main(["--root", str(vault_batch)])

    assert kode != 0
    assert batches.create_calls == []
    assert not (vault_batch / NAMA_INDEX).exists()
    assert "batch_lama" in capsys.readouterr().out


def test_abaikan_batch_tertinggal_lanjut_submit(vault_batch, monkeypatch):
    _tulis_sidecar_mentah(vault_batch, "batch_lama", [
        {"custom_id": "doc-0", "path": "Sales/Sales - A.md"},
    ])
    hasil_baris = [_baris_sukses("doc-0", "R0"), _baris_sukses("doc-1", "R1")]
    batches = _FakeBatches(batch_id="batch_baru", results=hasil_baris)
    client = _FakeClient(batches)
    monkeypatch.setattr(build, "anthropic", _FakeAnthropicModule(client))
    monkeypatch.setattr(build.time, "sleep", lambda s: None)

    kode = build.main(["--root", str(vault_batch), "--abaikan-batch-tertinggal"])

    assert kode == 0
    assert len(batches.create_calls) == 1


def test_batch_id_melewati_submit_dan_tulis_manifest(vault_batch, monkeypatch):
    _tulis_sidecar_mentah(vault_batch, "batch_resume", [
        {"custom_id": "doc-0", "path": "Sales/Sales - A.md"},
        {"custom_id": "doc-1", "path": "Sales/Sales - B.md"},
    ])
    hasil_baris = [_baris_sukses("doc-0", "Ringkasan A"), _baris_sukses("doc-1", "Ringkasan B")]
    batches = _FakeBatches(results=hasil_baris)
    client = _FakeClient(batches)
    monkeypatch.setattr(build, "anthropic", _FakeAnthropicModule(client))
    monkeypatch.setattr(build.time, "sleep", lambda s: None)

    kode = build.main(["--root", str(vault_batch), "--batch-id", "batch_resume"])

    assert kode == 0
    assert batches.create_calls == []
    index = json.loads((vault_batch / NAMA_INDEX).read_text(encoding="utf-8"))
    ringkasan = {d["path"]: d["ringkasan"] for d in index["dokumen"]}
    assert ringkasan["Sales/Sales - A.md"] == "Ringkasan A"
    assert ringkasan["Sales/Sales - B.md"] == "Ringkasan B"


def test_sidecar_terhapus_setelah_manifest_berhasil_ditulis(vault_batch, monkeypatch):
    _tulis_sidecar_mentah(vault_batch, "batch_resume", [
        {"custom_id": "doc-0", "path": "Sales/Sales - A.md"},
        {"custom_id": "doc-1", "path": "Sales/Sales - B.md"},
    ])
    hasil_baris = [_baris_sukses("doc-0", "Ringkasan A"), _baris_sukses("doc-1", "Ringkasan B")]
    batches = _FakeBatches(results=hasil_baris)
    client = _FakeClient(batches)
    monkeypatch.setattr(build, "anthropic", _FakeAnthropicModule(client))
    monkeypatch.setattr(build.time, "sleep", lambda s: None)

    kode = build.main(["--root", str(vault_batch), "--batch-id", "batch_resume"])

    assert kode == 0
    assert not (vault_batch / NAMA_SIDECAR).exists()


def test_batch_id_sidecar_tidak_ada_berhenti(vault_batch, monkeypatch, capsys):
    batches = _FakeBatches()
    client = _FakeClient(batches)
    monkeypatch.setattr(build, "anthropic", _FakeAnthropicModule(client))

    kode = build.main(["--root", str(vault_batch), "--batch-id", "batch_hantu"])

    assert kode != 0
    assert batches.create_calls == []
    assert not (vault_batch / NAMA_INDEX).exists()


def test_batch_id_sidecar_tidak_cocok_berhenti(vault_batch, monkeypatch, capsys):
    _tulis_sidecar_mentah(vault_batch, "batch_A", [
        {"custom_id": "doc-0", "path": "Sales/Sales - A.md"},
        {"custom_id": "doc-1", "path": "Sales/Sales - B.md"},
    ])
    batches = _FakeBatches()
    client = _FakeClient(batches)
    monkeypatch.setattr(build, "anthropic", _FakeAnthropicModule(client))

    kode = build.main(["--root", str(vault_batch), "--batch-id", "batch_B"])

    assert kode != 0
    assert batches.create_calls == []
    assert not (vault_batch / NAMA_INDEX).exists()
    # sidecar tetap ada -- salah tebak tidak boleh menghapus jejak batch_A
    assert (vault_batch / NAMA_SIDECAR).exists()


def test_deadline_terlampaui_sidecar_tetap_ada(vault_batch, monkeypatch, capsys):
    batches = _FakeBatches(retrieve_statuses=["in_progress"] * 5)
    client = _FakeClient(batches)
    monkeypatch.setattr(build, "anthropic", _FakeAnthropicModule(client))
    monkeypatch.setattr(build.time, "sleep", lambda s: None)

    kode = build.main(["--root", str(vault_batch), "--batas-tunggu-menit", "0"])

    assert kode != 0
    assert not (vault_batch / NAMA_INDEX).exists()
    sidecar_path = vault_batch / NAMA_SIDECAR
    assert sidecar_path.exists()
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    keluaran = capsys.readouterr().out
    assert sidecar["batch_id"] in keluaran
    assert "--batch-id" in keluaran
