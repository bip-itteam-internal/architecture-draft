import json
import sys
from pathlib import Path

import pytest

import vault_index.build as build
from vault_index.build import (
    VERSI_SKEMA, NAMA_INDEX, NAMA_TUGAS, NAMA_HASIL, scan_vault, muat_index,
    pilih_yang_perlu_diringkas, rakit_index,
    _peringatan_status, _peringatan_folder_tak_dikenal,
)
from vault_index.summarize import ringkas_stub


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


# --- main(): tiga mode CLI (tanpa flag / --daftar-tugas / --serap), offline,
# tanpa jaringan sungguhan -- ringkasan dibuat Claude Code, bukan modul ini.


@pytest.fixture
def vault_ringkasan(tmp_path: Path) -> Path:
    """Vault kecil untuk mode --daftar-tugas / --serap: dua dokumen normal,
    satu dokumen besar (>8192 byte, membuktikan `isi` dipotong), satu dokumen
    🔴 Stub (harus DIKECUALIKAN dari daftar tugas, ditangani lokal)."""
    (tmp_path / "Sales").mkdir()
    (tmp_path / "Sales" / "Sales - A.md").write_text(
        "- **Status**: ✅ Implemented\n\nIsi A singkat.\n", encoding="utf-8",
    )
    (tmp_path / "Sales" / "Sales - C.md").write_text(
        "- **Status**: ✅ Implemented\n\nIsi C singkat.\n", encoding="utf-8",
    )
    besar = (
        "- **Status**: ✅ Implemented\n\n## Bagian Panjang\n\n"
        + ("Kalimat isi berulang. " * 1000)
    )
    (tmp_path / "Sales" / "Sales - Besar.md").write_text(besar, encoding="utf-8")
    (tmp_path / "Sales" / "Sales - Stub.md").write_text(
        "- **Status**: 🔴 Stub\n", encoding="utf-8",
    )
    return tmp_path


# --- --daftar-tugas ------------------------------------------------------


def test_daftar_tugas_tulis_dokumen_yang_perlu_diringkas(vault_ringkasan):
    kode = build.main(["--root", str(vault_ringkasan), "--daftar-tugas"])
    assert kode == 0
    tugas = json.loads((vault_ringkasan / NAMA_TUGAS).read_text(encoding="utf-8"))
    paths = {t["path"] for t in tugas["tugas"]}
    assert paths == {
        "Sales/Sales - A.md", "Sales/Sales - C.md", "Sales/Sales - Besar.md",
    }
    assert tugas["jumlah"] == 3


def test_daftar_tugas_kecualikan_stub(vault_ringkasan):
    build.main(["--root", str(vault_ringkasan), "--daftar-tugas"])
    tugas = json.loads((vault_ringkasan / NAMA_TUGAS).read_text(encoding="utf-8"))
    paths = {t["path"] for t in tugas["tugas"]}
    assert "Sales/Sales - Stub.md" not in paths


def test_daftar_tugas_field_lengkap_dan_isi_dipotong(vault_ringkasan):
    build.main(["--root", str(vault_ringkasan), "--daftar-tugas"])
    tugas = json.loads((vault_ringkasan / NAMA_TUGAS).read_text(encoding="utf-8"))
    by_path = {t["path"]: t for t in tugas["tugas"]}

    a = by_path["Sales/Sales - A.md"]
    assert {"path", "judul", "jenis", "hash", "isi"} <= set(a.keys())
    assert a["judul"] == "Sales - A"
    assert a["jenis"] == "domain"
    assert len(a["hash"]) == 64
    assert a["isi"] == "- **Status**: ✅ Implemented\n\nIsi A singkat.\n"

    besar_asli = (vault_ringkasan / "Sales" / "Sales - Besar.md").read_text(encoding="utf-8")
    besar = by_path["Sales/Sales - Besar.md"]
    assert "[...dipotong...]" in besar["isi"]
    assert len(besar["isi"].encode("utf-8")) < len(besar_asli.encode("utf-8"))


def test_daftar_tugas_panduan_non_kosong(vault_ringkasan):
    build.main(["--root", str(vault_ringkasan), "--daftar-tugas"])
    tugas = json.loads((vault_ringkasan / NAMA_TUGAS).read_text(encoding="utf-8"))
    assert tugas["panduan"].strip() != ""
    assert "ringkasan" in tugas["panduan"]
    assert "ISI DOKUMEN" not in tugas["panduan"]


# --- I2: panduan harus menjelaskan kontrak keluaran, bukan cuma gaya --------


def test_daftar_tugas_panduan_menjelaskan_kontrak_keluaran(vault_ringkasan):
    build.main(["--root", str(vault_ringkasan), "--daftar-tugas"])
    tugas = json.loads((vault_ringkasan / NAMA_TUGAS).read_text(encoding="utf-8"))
    panduan = tugas["panduan"]
    assert NAMA_HASIL in panduan  # nama berkas keluaran
    assert "hasil" in panduan
    assert "hash" in panduan


def test_daftar_tugas_panduan_tanpa_placeholder_mentah(vault_ringkasan):
    build.main(["--root", str(vault_ringkasan), "--daftar-tugas"])
    tugas = json.loads((vault_ringkasan / NAMA_TUGAS).read_text(encoding="utf-8"))
    panduan = tugas["panduan"]
    assert "{judul}" not in panduan
    assert "{jenis}" not in panduan


def test_daftar_tugas_kosong_kalau_semua_sudah_diringkas(vault_ringkasan):
    entri = scan_vault(vault_ringkasan)
    lengkap = []
    for e in entri:
        if e["status_emoji"] == "🔴":
            lengkap.append({**e, **ringkas_stub(e["judul"])})
        else:
            lengkap.append({**e, "ringkasan": "sudah ada", "kata_kunci": []})
    lama = rakit_index(lengkap)
    (vault_ringkasan / NAMA_INDEX).write_text(json.dumps(lama), encoding="utf-8")

    kode = build.main(["--root", str(vault_ringkasan), "--daftar-tugas"])

    assert kode == 0
    tugas = json.loads((vault_ringkasan / NAMA_TUGAS).read_text(encoding="utf-8"))
    assert tugas["tugas"] == []


def test_daftar_tugas_full_masukkan_semua_non_stub_walau_sudah_lengkap(vault_ringkasan):
    entri = scan_vault(vault_ringkasan)
    lengkap = []
    for e in entri:
        if e["status_emoji"] == "🔴":
            lengkap.append({**e, **ringkas_stub(e["judul"])})
        else:
            lengkap.append({**e, "ringkasan": "sudah ada", "kata_kunci": []})
    lama = rakit_index(lengkap)
    (vault_ringkasan / NAMA_INDEX).write_text(json.dumps(lama), encoding="utf-8")

    kode = build.main(["--root", str(vault_ringkasan), "--daftar-tugas", "--full"])

    assert kode == 0
    tugas = json.loads((vault_ringkasan / NAMA_TUGAS).read_text(encoding="utf-8"))
    paths = {t["path"] for t in tugas["tugas"]}
    assert paths == {
        "Sales/Sales - A.md", "Sales/Sales - C.md", "Sales/Sales - Besar.md",
    }


def test_daftar_tugas_path_custom_dihormati(vault_ringkasan, tmp_path):
    custom = tmp_path / "custom-tugas.json"
    kode = build.main(["--root", str(vault_ringkasan), "--daftar-tugas", str(custom)])
    assert kode == 0
    assert custom.exists()
    assert not (vault_ringkasan / NAMA_TUGAS).exists()


# --- --serap ---------------------------------------------------------------


def test_serap_menyerap_valid_dan_tulis_manifest(vault_ringkasan):
    entri = {e["path"]: e for e in scan_vault(vault_ringkasan)}
    hasil = {
        "hasil": {
            "Sales/Sales - A.md": {
                "ringkasan": "Menjawab: apa isi A.", "kata_kunci": ["a"],
                "hash": entri["Sales/Sales - A.md"]["hash"],
            },
            "Sales/Sales - Besar.md": {
                "ringkasan": "Menjawab: apa isi Besar.", "kata_kunci": ["besar"],
                "hash": entri["Sales/Sales - Besar.md"]["hash"],
            },
        }
    }
    (vault_ringkasan / NAMA_HASIL).write_text(json.dumps(hasil), encoding="utf-8")

    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    assert kode != 0  # Sales - C.md tidak ada di hasil -> masih gagal
    index = json.loads((vault_ringkasan / NAMA_INDEX).read_text(encoding="utf-8"))
    ringkasan = {d["path"]: d["ringkasan"] for d in index["dokumen"]}
    assert ringkasan["Sales/Sales - A.md"] == "Menjawab: apa isi A."
    assert ringkasan["Sales/Sales - Besar.md"] == "Menjawab: apa isi Besar."
    assert ringkasan["Sales/Sales - Stub.md"] is not None
    assert index["gagal"] == ["Sales/Sales - C.md"]


def test_serap_tolak_entri_tipe_salah(vault_ringkasan, capsys):
    hasil = {
        "hasil": {
            "Sales/Sales - A.md": {"ringkasan": 123, "kata_kunci": []},
            "Sales/Sales - C.md": {"ringkasan": "", "kata_kunci": ["ok"]},
            "Sales/Sales - Besar.md": {"ringkasan": "x", "kata_kunci": [1, 2]},
        }
    }
    (vault_ringkasan / NAMA_HASIL).write_text(json.dumps(hasil), encoding="utf-8")

    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    assert kode != 0
    index = json.loads((vault_ringkasan / NAMA_INDEX).read_text(encoding="utf-8"))
    assert set(index["gagal"]) == {
        "Sales/Sales - A.md", "Sales/Sales - C.md", "Sales/Sales - Besar.md",
    }
    assert "DITOLAK" in capsys.readouterr().out


def test_serap_tolak_hash_tidak_cocok_laporkan_basi(vault_ringkasan, capsys):
    hasil = {
        "hasil": {
            "Sales/Sales - A.md": {
                "ringkasan": "Ringkasan A.", "kata_kunci": ["a"], "hash": "hash-salah",
            },
        }
    }
    (vault_ringkasan / NAMA_HASIL).write_text(json.dumps(hasil), encoding="utf-8")

    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    assert kode != 0
    index = json.loads((vault_ringkasan / NAMA_INDEX).read_text(encoding="utf-8"))
    assert "Sales/Sales - A.md" in index["gagal"]
    assert "basi" in capsys.readouterr().out.lower()


def test_serap_terima_tanpa_hash_dengan_peringatan(vault_ringkasan, capsys):
    hasil = {
        "hasil": {
            "Sales/Sales - A.md": {"ringkasan": "Ringkasan A.", "kata_kunci": ["a"]},
        }
    }
    (vault_ringkasan / NAMA_HASIL).write_text(json.dumps(hasil), encoding="utf-8")

    build.main(["--root", str(vault_ringkasan), "--serap"])

    index = json.loads((vault_ringkasan / NAMA_INDEX).read_text(encoding="utf-8"))
    ringkasan = {d["path"]: d["ringkasan"] for d in index["dokumen"]}
    assert ringkasan["Sales/Sales - A.md"] == "Ringkasan A."
    assert "tanpa" in capsys.readouterr().out.lower()


def test_serap_laporkan_path_tidak_ada_di_vault_tanpa_crash(vault_ringkasan, capsys):
    hasil = {
        "hasil": {
            "Sales/Sales - Tidak Ada.md": {"ringkasan": "x", "kata_kunci": []},
        }
    }
    (vault_ringkasan / NAMA_HASIL).write_text(json.dumps(hasil), encoding="utf-8")

    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    keluaran = capsys.readouterr().out
    assert "Sales/Sales - Tidak Ada.md" in keluaran
    assert kode != 0
    assert (vault_ringkasan / NAMA_INDEX).exists()  # tidak crash, manifest tetap ditulis


def test_serap_terapkan_stub(vault_ringkasan):
    (vault_ringkasan / NAMA_HASIL).write_text(json.dumps({"hasil": {}}), encoding="utf-8")

    build.main(["--root", str(vault_ringkasan), "--serap"])

    index = json.loads((vault_ringkasan / NAMA_INDEX).read_text(encoding="utf-8"))
    dok = {d["path"]: d for d in index["dokumen"]}
    assert dok["Sales/Sales - Stub.md"]["ringkasan"] is not None
    assert "Sales/Sales - Stub.md" not in index["gagal"]


def test_serap_hapus_berkas_tugas_dan_hasil_setelah_manifest_ditulis(vault_ringkasan):
    (vault_ringkasan / NAMA_TUGAS).write_text("{}", encoding="utf-8")
    (vault_ringkasan / NAMA_HASIL).write_text(json.dumps({"hasil": {}}), encoding="utf-8")

    build.main(["--root", str(vault_ringkasan), "--serap"])

    assert not (vault_ringkasan / NAMA_TUGAS).exists()
    assert not (vault_ringkasan / NAMA_HASIL).exists()


def test_serap_berkas_hasil_tidak_ada_berhenti_tanpa_crash(vault_ringkasan, capsys):
    """DISESUAIKAN untuk Perubahan B: --serap tanpa PATH sekarang mencari
    SEMUA pola berkas hasil (tunggal + bernomor), bukan cuma satu nama
    tetap -- jadi pesan kegagalan sekarang menjelaskan langkah 2 belum
    dikerjakan (lihat test_serap_tanpa_satupun_berkas_hasil_pesan_langkah_2)
    alih-alih menyebut satu path tetap yang tidak lagi merepresentasikan
    seluruh pencarian."""
    kode = build.main(["--root", str(vault_ringkasan), "--serap"])
    assert kode != 0
    assert not (vault_ringkasan / NAMA_INDEX).exists()
    assert "langkah 2" in capsys.readouterr().out.lower()


# --- C1: pembungkus "hasil" salah bentuk -- harus fail-closed, bukan senyap
# jadi {} yang menghapus seluruh sesi ringkasan tanpa jejak. ------------------


def test_serap_tanpa_pembungkus_hasil_gagal_tanpa_menulis_atau_menghapus(
    vault_ringkasan, capsys
):
    """Agent menulis peta path->ringkasan langsung di level atas, tanpa
    pembungkus `"hasil"`. Ini reproduksi persis skenario C1: dulu diam-diam
    diperlakukan sebagai {} (nol diserap) dan berkas hasil tetap dihapus."""
    entri = {e["path"]: e for e in scan_vault(vault_ringkasan)}
    salah_bentuk = {
        "Sales/Sales - A.md": {
            "ringkasan": "Ringkasan A.", "kata_kunci": ["a"],
            "hash": entri["Sales/Sales - A.md"]["hash"],
        },
    }
    (vault_ringkasan / NAMA_HASIL).write_text(json.dumps(salah_bentuk), encoding="utf-8")

    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    assert kode != 0
    assert not (vault_ringkasan / NAMA_INDEX).exists()
    assert (vault_ringkasan / NAMA_HASIL).exists()  # TIDAK dihapus
    keluaran = capsys.readouterr().out
    assert "GAGAL" in keluaran
    assert "hasil" in keluaran


@pytest.mark.parametrize("hasil_salah", [[], "sebuah string", None, "123"])
def test_serap_hasil_bukan_dict_gagal_tanpa_menulis_atau_menghapus(
    vault_ringkasan, capsys, hasil_salah
):
    (vault_ringkasan / NAMA_HASIL).write_text(
        json.dumps({"hasil": hasil_salah}), encoding="utf-8",
    )

    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    assert kode != 0
    assert not (vault_ringkasan / NAMA_INDEX).exists()
    assert (vault_ringkasan / NAMA_HASIL).exists()
    assert "GAGAL" in capsys.readouterr().out


# --- I1/I4: hapus artefak hanya bila serap bersih total ----------------------


def test_serap_sebagian_ditolak_artefak_dipertahankan(vault_ringkasan, capsys):
    (vault_ringkasan / NAMA_TUGAS).write_text("{}", encoding="utf-8")
    hasil = {
        "hasil": {
            "Sales/Sales - A.md": {"ringkasan": 123, "kata_kunci": []},  # ditolak
        }
    }
    (vault_ringkasan / NAMA_HASIL).write_text(json.dumps(hasil), encoding="utf-8")

    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    assert kode != 0
    assert (vault_ringkasan / NAMA_HASIL).exists()
    assert (vault_ringkasan / NAMA_TUGAS).exists()
    assert "dipertahankan" in capsys.readouterr().out.lower()


def test_serap_hash_basi_artefak_dipertahankan(vault_ringkasan, capsys):
    hasil = {
        "hasil": {
            "Sales/Sales - A.md": {
                "ringkasan": "x", "kata_kunci": [], "hash": "hash-salah",
            },
        }
    }
    (vault_ringkasan / NAMA_HASIL).write_text(json.dumps(hasil), encoding="utf-8")

    build.main(["--root", str(vault_ringkasan), "--serap"])

    assert (vault_ringkasan / NAMA_HASIL).exists()
    assert "dipertahankan" in capsys.readouterr().out.lower()


def test_serap_path_tak_ditemukan_artefak_dipertahankan(vault_ringkasan, capsys):
    hasil = {"hasil": {"Sales/Sales - Tidak Ada.md": {"ringkasan": "x", "kata_kunci": []}}}
    (vault_ringkasan / NAMA_HASIL).write_text(json.dumps(hasil), encoding="utf-8")

    build.main(["--root", str(vault_ringkasan), "--serap"])

    assert (vault_ringkasan / NAMA_HASIL).exists()
    assert "dipertahankan" in capsys.readouterr().out.lower()


def test_serap_sukses_penuh_artefak_tetap_terhapus(vault_ringkasan):
    """Kontrol positif: serap bersih (semua entri diterima) tetap membersihkan
    artefak sementara seperti sebelumnya -- I1 hanya menambah pengecualian."""
    entri = {e["path"]: e for e in scan_vault(vault_ringkasan)}
    hasil = {
        "hasil": {
            "Sales/Sales - A.md": {
                "ringkasan": "a", "kata_kunci": [],
                "hash": entri["Sales/Sales - A.md"]["hash"],
            },
            "Sales/Sales - C.md": {
                "ringkasan": "c", "kata_kunci": [],
                "hash": entri["Sales/Sales - C.md"]["hash"],
            },
            "Sales/Sales - Besar.md": {
                "ringkasan": "b", "kata_kunci": [],
                "hash": entri["Sales/Sales - Besar.md"]["hash"],
            },
        }
    }
    (vault_ringkasan / NAMA_HASIL).write_text(json.dumps(hasil), encoding="utf-8")

    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    assert kode == 0
    assert not (vault_ringkasan / NAMA_HASIL).exists()


def test_serap_gagal_unlink_cetak_peringatan_bukan_crash(vault_ringkasan, monkeypatch, capsys):
    """Berkas terkunci proses lain (Obsidian, antivirus) saat unlink tidak
    boleh melempar traceback -- manifest yang sudah benar tetap harus
    dilaporkan lengkap."""
    (vault_ringkasan / NAMA_HASIL).write_text(json.dumps({"hasil": {}}), encoding="utf-8")

    asli_unlink = Path.unlink

    def unlink_gagal(self, *a, **k):
        if self.name == NAMA_HASIL:
            raise OSError("berkas terkunci")
        return asli_unlink(self, *a, **k)

    monkeypatch.setattr(Path, "unlink", unlink_gagal)

    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    assert kode != 0  # mencerminkan hasil serap (dokumen lain masih gagal), bukan crash
    assert (vault_ringkasan / NAMA_INDEX).exists()
    keluaran = capsys.readouterr().out
    assert "PERINGATAN" in keluaran
    assert "gagal menghapus" in keluaran.lower()


# --- mode tanpa flag ---------------------------------------------------------


def test_mode_tanpa_flag_ringkasan_null_untuk_yang_belum_ada_dan_exit_nonzero(
    vault_ringkasan, capsys
):
    kode = build.main(["--root", str(vault_ringkasan)])

    assert kode != 0
    index = json.loads((vault_ringkasan / NAMA_INDEX).read_text(encoding="utf-8"))
    dok = {d["path"]: d for d in index["dokumen"]}
    assert dok["Sales/Sales - A.md"]["ringkasan"] is None
    assert dok["Sales/Sales - Stub.md"]["ringkasan"] is not None
    assert "Sales/Sales - A.md" in index["gagal"]
    assert "--daftar-tugas" in capsys.readouterr().out


def test_mode_tanpa_flag_tidak_panggil_parse_isi_pesan(vault_ringkasan, monkeypatch):
    def _gagal(*a, **k):
        raise AssertionError("_parse_isi_pesan tidak boleh dipanggil di mode tanpa flag")

    monkeypatch.setattr(build, "_parse_isi_pesan", _gagal)

    build.main(["--root", str(vault_ringkasan)])  # tidak boleh raise


def test_mode_tanpa_flag_carry_forward_ringkasan_yang_hash_nya_sama(vault_ringkasan):
    entri = scan_vault(vault_ringkasan)
    lengkap = [{**e, "ringkasan": "sudah ada", "kata_kunci": ["x"]} for e in entri]
    lama = rakit_index(lengkap)
    (vault_ringkasan / NAMA_INDEX).write_text(json.dumps(lama), encoding="utf-8")

    kode = build.main(["--root", str(vault_ringkasan)])

    assert kode == 0
    index = json.loads((vault_ringkasan / NAMA_INDEX).read_text(encoding="utf-8"))
    dok = {d["path"]: d for d in index["dokumen"]}
    assert dok["Sales/Sales - A.md"]["ringkasan"] == "sudah ada"


# --- minor: mode CLI harus saling eksklusif, bukan diselesaikan senyap by
# precedence (--check / --daftar-tugas / --serap). ---------------------------


@pytest.mark.parametrize(
    "argv",
    [
        ["--check", "--serap"],
        ["--check", "--daftar-tugas"],
        ["--daftar-tugas", "--serap"],
    ],
)
def test_dua_flag_mode_sekaligus_ditolak_argparse(vault_ringkasan, argv):
    with pytest.raises(SystemExit):
        build.main(["--root", str(vault_ringkasan), *argv])


# --- Task 11 -- Perubahan A: --pecah N pada --daftar-tugas ------------------


@pytest.fixture
def vault_pecah(tmp_path: Path) -> Path:
    """5 dokumen non-stub -- cukup untuk --pecah 2 menghasilkan potongan 2/2/1."""
    (tmp_path / "Sales").mkdir()
    for huruf in "ABCDE":
        (tmp_path / "Sales" / f"Sales - {huruf}.md").write_text(
            f"- **Status**: ✅ Implemented\n\nIsi {huruf}.\n", encoding="utf-8",
        )
    return tmp_path


def test_pecah_menghasilkan_potongan_2_2_1(vault_pecah):
    kode = build.main(["--root", str(vault_pecah), "--daftar-tugas", "--pecah", "2"])
    assert kode == 0

    potongan = sorted(vault_pecah.glob("VAULT-INDEX.tugas.*.json"))
    assert [p.name for p in potongan] == [
        "VAULT-INDEX.tugas.001.json",
        "VAULT-INDEX.tugas.002.json",
        "VAULT-INDEX.tugas.003.json",
    ]
    jumlah = [len(json.loads(p.read_text(encoding="utf-8"))["tugas"]) for p in potongan]
    assert jumlah == [2, 2, 1]
    assert not (vault_pecah / NAMA_TUGAS).exists()  # bukan berkas tunggal lama


def test_pecah_tiap_potongan_berdiri_sendiri(vault_pecah):
    build.main(["--root", str(vault_pecah), "--daftar-tugas", "--pecah", "2"])

    for i, nomor in enumerate(["001", "002", "003"], start=1):
        data = json.loads(
            (vault_pecah / f"VAULT-INDEX.tugas.{nomor}.json").read_text(encoding="utf-8")
        )
        assert data["versi_skema"] == VERSI_SKEMA
        assert data["panduan"].strip() != ""
        assert data["potongan"] == i
        assert data["total_potongan"] == 3
        assert data["berkas_keluaran"] == f"VAULT-INDEX.hasil.{nomor}.json"
        assert data["jumlah"] == len(data["tugas"])


def test_pecah_berkas_keluaran_potongan_ketiga(vault_pecah):
    build.main(["--root", str(vault_pecah), "--daftar-tugas", "--pecah", "2"])
    data = json.loads(
        (vault_pecah / "VAULT-INDEX.tugas.003.json").read_text(encoding="utf-8")
    )
    assert data["berkas_keluaran"] == "VAULT-INDEX.hasil.003.json"


def test_pecah_tanpa_dokumen_perlu_diringkas_nol_potongan(vault_pecah):
    entri = scan_vault(vault_pecah)
    lengkap = [{**e, "ringkasan": "sudah ada", "kata_kunci": []} for e in entri]
    lama = rakit_index(lengkap)
    (vault_pecah / NAMA_INDEX).write_text(json.dumps(lama), encoding="utf-8")

    kode = build.main(["--root", str(vault_pecah), "--daftar-tugas", "--pecah", "2"])

    assert kode == 0
    assert sorted(vault_pecah.glob("VAULT-INDEX.tugas.*.json")) == []


def test_pecah_bersihkan_potongan_lama_sebelum_menulis_baru(vault_pecah, capsys):
    for n in range(1, 11):
        (vault_pecah / f"VAULT-INDEX.tugas.{n:03d}.json").write_text("{}", encoding="utf-8")

    kode = build.main(["--root", str(vault_pecah), "--daftar-tugas", "--pecah", "2"])

    assert kode == 0
    sisa = sorted(p.name for p in vault_pecah.glob("VAULT-INDEX.tugas.*.json"))
    assert sisa == [
        "VAULT-INDEX.tugas.001.json",
        "VAULT-INDEX.tugas.002.json",
        "VAULT-INDEX.tugas.003.json",
    ]
    assert "Dihapus 10" in capsys.readouterr().out


@pytest.mark.parametrize("nilai", ["0", "-1", "abc"])
def test_pecah_nilai_tidak_valid_ditolak_argparse(vault_pecah, nilai):
    with pytest.raises(SystemExit):
        build.main(["--root", str(vault_pecah), "--daftar-tugas", "--pecah", nilai])


# --- Task 11 -- Perubahan B: --serap menggabungkan banyak berkas hasil ------


def test_serap_tanpa_path_gabung_beberapa_berkas_hasil_bernomor(vault_ringkasan):
    entri = {e["path"]: e for e in scan_vault(vault_ringkasan)}
    hasil_1 = {
        "hasil": {
            "Sales/Sales - A.md": {
                "ringkasan": "Ringkasan A.", "kata_kunci": ["a"],
                "hash": entri["Sales/Sales - A.md"]["hash"],
            },
            "Sales/Sales - C.md": {
                "ringkasan": "Ringkasan C.", "kata_kunci": ["c"],
                "hash": entri["Sales/Sales - C.md"]["hash"],
            },
        }
    }
    hasil_2 = {
        "hasil": {
            "Sales/Sales - Besar.md": {
                "ringkasan": "Ringkasan Besar.", "kata_kunci": ["besar"],
                "hash": entri["Sales/Sales - Besar.md"]["hash"],
            },
        }
    }
    (vault_ringkasan / "VAULT-INDEX.hasil.001.json").write_text(
        json.dumps(hasil_1), encoding="utf-8"
    )
    (vault_ringkasan / "VAULT-INDEX.hasil.002.json").write_text(
        json.dumps(hasil_2), encoding="utf-8"
    )

    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    assert kode == 0  # A, C, Besar semua diserap; Stub ditangani lokal
    index = json.loads((vault_ringkasan / NAMA_INDEX).read_text(encoding="utf-8"))
    ringkasan = {d["path"]: d["ringkasan"] for d in index["dokumen"]}
    assert ringkasan["Sales/Sales - A.md"] == "Ringkasan A."
    assert ringkasan["Sales/Sales - C.md"] == "Ringkasan C."
    assert ringkasan["Sales/Sales - Besar.md"] == "Ringkasan Besar."
    assert not (vault_ringkasan / "VAULT-INDEX.hasil.001.json").exists()
    assert not (vault_ringkasan / "VAULT-INDEX.hasil.002.json").exists()


def test_serap_satu_berkas_salah_bentuk_menolak_seluruh_operasi(vault_ringkasan, capsys):
    """C1 versi banyak-berkas: satu berkas hasil bentuknya salah harus
    menolak SELURUH gabungan walau berkas lain sah -- rusak bukan berarti
    kosong, dan bukan 'lewati yang rusak, pakai yang sah'."""
    entri = {e["path"]: e for e in scan_vault(vault_ringkasan)}
    hasil_sah = {
        "hasil": {
            "Sales/Sales - A.md": {
                "ringkasan": "Ringkasan A.", "kata_kunci": ["a"],
                "hash": entri["Sales/Sales - A.md"]["hash"],
            },
        }
    }
    (vault_ringkasan / "VAULT-INDEX.hasil.001.json").write_text(
        json.dumps(hasil_sah), encoding="utf-8"
    )
    # bentuk salah: tanpa pembungkus "hasil"
    (vault_ringkasan / "VAULT-INDEX.hasil.002.json").write_text(
        json.dumps({"Sales/Sales - C.md": {"ringkasan": "x", "kata_kunci": []}}),
        encoding="utf-8",
    )

    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    assert kode != 0
    assert not (vault_ringkasan / NAMA_INDEX).exists()  # manifest TIDAK ditulis
    assert (vault_ringkasan / "VAULT-INDEX.hasil.001.json").exists()  # tidak dihapus
    assert (vault_ringkasan / "VAULT-INDEX.hasil.002.json").exists()  # tidak dihapus
    keluaran = capsys.readouterr().out
    assert "GAGAL" in keluaran
    assert "VAULT-INDEX.hasil.002.json" in keluaran


def test_serap_path_konflik_lintas_berkas_menolak_seluruh_operasi(vault_ringkasan, capsys):
    entri = {e["path"]: e for e in scan_vault(vault_ringkasan)}
    hash_a = entri["Sales/Sales - A.md"]["hash"]
    hasil_1 = {
        "hasil": {
            "Sales/Sales - A.md": {"ringkasan": "Versi 1.", "kata_kunci": [], "hash": hash_a},
        }
    }
    hasil_2 = {
        "hasil": {
            "Sales/Sales - A.md": {"ringkasan": "Versi 2.", "kata_kunci": [], "hash": hash_a},
        }
    }
    (vault_ringkasan / "VAULT-INDEX.hasil.001.json").write_text(
        json.dumps(hasil_1), encoding="utf-8"
    )
    (vault_ringkasan / "VAULT-INDEX.hasil.002.json").write_text(
        json.dumps(hasil_2), encoding="utf-8"
    )

    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    assert kode != 0
    assert not (vault_ringkasan / NAMA_INDEX).exists()
    assert (vault_ringkasan / "VAULT-INDEX.hasil.001.json").exists()
    assert (vault_ringkasan / "VAULT-INDEX.hasil.002.json").exists()
    keluaran = capsys.readouterr().out
    assert "Sales/Sales - A.md" in keluaran
    assert "VAULT-INDEX.hasil.001.json" in keluaran
    assert "VAULT-INDEX.hasil.002.json" in keluaran


def test_serap_tanpa_satupun_berkas_hasil_pesan_langkah_2(vault_ringkasan, capsys):
    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    assert kode != 0
    assert not (vault_ringkasan / NAMA_INDEX).exists()
    assert "langkah 2" in capsys.readouterr().out.lower()


def test_serap_pembersihan_mencakup_seluruh_potongan_tugas_dan_hasil(vault_ringkasan):
    """Pembersihan artefak sukses harus mencakup seluruh berkas potongan
    tugas DAN hasil, bukan cuma dua nama tetap (VAULT-INDEX.tugas.json /
    VAULT-INDEX.hasil.json)."""
    entri = {e["path"]: e for e in scan_vault(vault_ringkasan)}
    pasangan = [
        ("001", "Sales/Sales - A.md"),
        ("002", "Sales/Sales - C.md"),
        ("003", "Sales/Sales - Besar.md"),
    ]
    for n, path_dok in pasangan:
        (vault_ringkasan / f"VAULT-INDEX.tugas.{n}.json").write_text("{}", encoding="utf-8")
        hasil = {
            "hasil": {
                path_dok: {
                    "ringkasan": f"Ringkasan {path_dok}.", "kata_kunci": [],
                    "hash": entri[path_dok]["hash"],
                }
            }
        }
        (vault_ringkasan / f"VAULT-INDEX.hasil.{n}.json").write_text(
            json.dumps(hasil), encoding="utf-8"
        )

    kode = build.main(["--root", str(vault_ringkasan), "--serap"])

    assert kode == 0
    for n, _ in pasangan:
        assert not (vault_ringkasan / f"VAULT-INDEX.tugas.{n}.json").exists()
        assert not (vault_ringkasan / f"VAULT-INDEX.hasil.{n}.json").exists()


# --- Task 11 -- Perubahan C: --check melaporkan sisa artefak ----------------


def _index_lengkap(vault: Path) -> dict:
    entri = scan_vault(vault)
    lengkap = []
    for e in entri:
        if e["status_emoji"] == "🔴":
            lengkap.append({**e, **ringkas_stub(e["judul"])})
        else:
            lengkap.append({**e, "ringkasan": "sudah ada", "kata_kunci": []})
    return rakit_index(lengkap)


def test_check_melaporkan_artefak_potongan_tersisa(vault_ringkasan, capsys):
    lama = _index_lengkap(vault_ringkasan)
    (vault_ringkasan / NAMA_INDEX).write_text(json.dumps(lama), encoding="utf-8")
    (vault_ringkasan / "VAULT-INDEX.tugas.001.json").write_text("{}", encoding="utf-8")
    (vault_ringkasan / "VAULT-INDEX.hasil.001.json").write_text("{}", encoding="utf-8")

    kode = build.main(["--root", str(vault_ringkasan), "--check"])

    assert kode == 0  # index tetap segar -- exit code TIDAK berubah oleh artefak
    keluaran = capsys.readouterr().out
    assert "PERINGATAN" in keluaran
    assert "VAULT-INDEX.tugas.001.json" in keluaran
    assert "VAULT-INDEX.hasil.001.json" in keluaran


def test_check_tanpa_artefak_tidak_ada_peringatan(vault_ringkasan, capsys):
    lama = _index_lengkap(vault_ringkasan)
    (vault_ringkasan / NAMA_INDEX).write_text(json.dumps(lama), encoding="utf-8")

    kode = build.main(["--root", str(vault_ringkasan), "--check"])

    assert kode == 0
    assert "PERINGATAN" not in capsys.readouterr().out


# --- anti-regresi: jalur berbayar (Batches API) benar-benar hilang ----------


def test_build_tidak_mengimpor_anthropic():
    assert "anthropic" not in sys.modules
    import vault_index.build as build_mod
    assert "anthropic" not in sys.modules
    assert not hasattr(build_mod, "anthropic")


def test_build_sidecar_dan_batch_flag_tidak_ada_lagi():
    assert not hasattr(build, "NAMA_SIDECAR")
    assert not hasattr(build, "_tulis_sidecar")
    assert not hasattr(build, "_muat_sidecar")
    assert not hasattr(build, "SidecarRusak")
    assert not hasattr(build, "_cetak_pemulihan_sidecar_gagal")
    assert not hasattr(build, "_tunggu_batch_dengan_deadline")

    with pytest.raises(SystemExit):
        build.main(["--batch-id", "batch_x"])
