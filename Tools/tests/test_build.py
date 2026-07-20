import json
from pathlib import Path

import pytest

from vault_index.build import (
    VERSI_SKEMA, scan_vault, muat_index,
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
