"""Test gerbang nomor ADR ganda (`hooks/githooks/gerbang-adr.py`, kit 1.35.0).

Yang dijaga:
1. Pasangan lama berizin LOLOS (keputusan user 2026-09-29: tidak dinomori ulang).
2. Nomor ganda BARU ditolak, begitu juga berkas ketiga pada nomor berizin.
3. Yang dibaca POHON COMMIT, bukan working tree: ADR sesi lain yang belum di-commit tak
   boleh menggagalkan push (kontrol untuk pohon vault yang dipakai bersama).
4. Pesan menyebut nomor bebas berikutnya.

Jalankan:
  architecture-draft/Tools/.venv/Scripts/python.exe -m pytest -p no:cacheprovider -q architecture-draft/.agent-kit/tests/test_gerbang_adr.py
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

sys.dont_write_bytecode = True
SKRIP = Path(__file__).resolve().parent.parent / "hooks" / "githooks" / "gerbang-adr.py"
spec = importlib.util.spec_from_file_location("gerbang_adr", SKRIP)
ga = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ga)


def _git(repo, *a):
    subprocess.run(["git", "-c", "core.fsmonitor=false", *a], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def vault(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@t")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "Decisions").mkdir()
    return tmp_path


def _tulis(vault, *nama, commit=True):
    for n in nama:
        (vault / "Decisions" / n).write_text("# x\n", encoding="utf-8")
    if commit:
        _git(vault, "add", "-A")
        _git(vault, "commit", "-q", "-m", "x")


def _jalan(vault, capsys):
    kode = ga.main(["--vault", str(vault), "--rev", "HEAD"])
    return kode, capsys.readouterr().out


def test_bersih_lolos(vault, capsys):
    _tulis(vault, "ADR - 0001 A.md", "ADR - 0002 B.md")
    kode, out = _jalan(vault, capsys)
    assert kode == 0 and "lolos" in out


def test_pasangan_lama_berizin_lolos(vault, capsys):
    _tulis(vault, *ga.IZIN["0077"], "ADR - 0078 Lain.md")
    kode, _ = _jalan(vault, capsys)
    assert kode == 0


def test_ganda_baru_ditolak_dengan_nomor_bebas(vault, capsys):
    _tulis(vault, "ADR - 0143 Backlog.md", "ADR - 0144 Satu.md", "ADR - 0144 Dua.md")
    kode, out = _jalan(vault, capsys)
    assert kode == 1
    assert "nomor ADR 0144 dipakai 2 berkas" in out
    assert "0145" in out


def test_berkas_ketiga_pada_nomor_berizin_ditolak(vault, capsys):
    _tulis(vault, *ga.IZIN["0058"], "ADR - 0058 Ketiga.md")
    kode, out = _jalan(vault, capsys)
    assert kode == 1 and "pasangan lama berizin" in out


def test_judul_berizin_diganti_ditolak(vault, capsys):
    a, _ = ga.IZIN["0061"]
    _tulis(vault, a, "ADR - 0061 Judul Diganti.md")
    kode, _ = _jalan(vault, capsys)
    assert kode == 1


def test_working_tree_sesi_lain_diabaikan(vault, capsys):
    # kontrol pohon bersama: berkas ganda yang BELUM di-commit tidak ikut dihitung
    _tulis(vault, "ADR - 0010 Ada.md")
    _tulis(vault, "ADR - 0010 Belum Commit Sesi Lain.md", commit=False)
    kode, _ = _jalan(vault, capsys)
    assert kode == 0
    # kontrol negatif: begitu di-commit, ia tertangkap
    _git(vault, "add", "-A")
    _git(vault, "commit", "-q", "-m", "y")
    kode, _ = _jalan(vault, capsys)
    assert kode == 1


def test_izin_persis_sepuluh_pasangan():
    assert len(ga.IZIN) == 10
    for nomor, (a, b) in ga.IZIN.items():
        assert a.startswith(f"ADR - {nomor} ") and b.startswith(f"ADR - {nomor} ") and a != b


def test_vault_sungguhan_lolos():
    vault = Path(__file__).resolve().parents[2]
    if not (vault / "Decisions").is_dir():
        pytest.skip("bukan di dalam vault")
    salah, _ = ga.periksa(ga.daftar_adr(str(vault), "HEAD"))
    assert salah == [], salah
