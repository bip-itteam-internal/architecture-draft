"""Test gerbang deterministik (`hooks/gerbang-lib.py`) dan gerbang kit (`hooks/gerbang-kit.py`).

Yang dijaga di sini adalah dua aturan yang gagalnya SENYAP:

1. **Nol gerbang bukan lulus.** Sampai 1.24.0, repo yang tak dikenali jenisnya menghasilkan daftar
   gerbang KOSONG, dan "tak ada gerbang yang gagal" dihitung sebagai lolos. Empat repo lewat begitu
   saja (mybharata-app, guestbook-system, consolidated-accounting-app, architecture-draft) tanpa satu
   pun tanda di keluaran `/judge`.
2. **Pelaksana Node dibaca dari lockfile, bukan ditebak.** `erp-frontend` memegang `pnpm-lock.yaml`
   DAN `package-lock.json` sekaligus, jadi urutan prioritasnya menentukan resolver mana yang dipakai.

Jalankan (Windows, dari akar workspace; tanpa cache supaya vault tidak kotor):
  $env:PYTHONDONTWRITEBYTECODE=1
  architecture-draft/Tools/.venv/Scripts/python.exe -m pytest -p no:cacheprovider -q architecture-draft/.agent-kit/tests/test_gerbang.py
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
HOOKS = HERE.parent / "hooks"


def _muat(nama_berkas, nama_modul):
    # GERBANG_LIB_MODUL / GERBANG_KIT_MODUL menunjuk salinan yang sengaja dimutasi, untuk
    # membuktikan test tidak vakum tanpa menyunting berkas aslinya.
    env = os.environ.get(nama_modul.upper() + "_MODUL")
    sumber = env or (HOOKS / nama_berkas)
    spec = importlib.util.spec_from_file_location(nama_modul, sumber)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


gl = _muat("gerbang-lib.py", "gerbang_lib")
gk = _muat("gerbang-kit.py", "gerbang_kit")


def buat(tmp_path, *berkas):
    """Bikin folder repo tiruan berisi berkas penanda (isi tak dibaca jenis_repo)."""
    for b in berkas:
        p = tmp_path / b
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{}\n", encoding="utf-8")
    return str(tmp_path)


# ---------------------------------------------------------------- jenis repo

@pytest.mark.parametrize("berkas,harapan", [
    (["pubspec.yaml"], "flutter"),
    (["package.json", "pnpm-lock.yaml"], "node"),
    (["package.json", "package-lock.json"], "node"),
    (["package.json", "yarn.lock"], "node"),
    (["package.json", "bun.lockb"], "node"),
    (["package.json", "bun.lock"], "node"),
    (["services/a/go.mod"], "go"),
    (["README.md"], "lain"),
])
def test_jenis_repo(tmp_path, berkas, harapan):
    assert gl.jenis_repo(buat(tmp_path, *berkas)) == harapan


def test_package_json_tanpa_lockfile_bukan_node(tmp_path):
    # Pelaksananya dibaca dari lockfile; tanpa lockfile tak ada yang bisa dibaca, dan MENEBAK npm
    # di repo pnpm memakai resolver yang salah. Jatuh ke 'lain' berarti tertolak dengan pesan,
    # bukan lolos diam-diam.
    assert gl.jenis_repo(buat(tmp_path, "package.json")) == "lain"


def test_flutter_menang_atas_package_json_tanpa_lockfile(tmp_path):
    assert gl.jenis_repo(buat(tmp_path, "pubspec.yaml", "package.json")) == "flutter"


# ---------------------------------------------------------------- pelaksana node

@pytest.mark.parametrize("berkas,nama", [
    (["pnpm-lock.yaml"], "pnpm"),
    (["package-lock.json"], "npm"),
    (["yarn.lock"], "yarn"),
    (["bun.lockb"], "bun"),
    (["bun.lock"], "bun"),
])
def test_pm_node(tmp_path, berkas, nama):
    pm = gl.pm_node(buat(tmp_path, "package.json", *berkas))
    assert pm is not None and pm["nama"] == nama


def test_pm_node_pnpm_menang_saat_dua_lockfile(tmp_path):
    # erp-frontend NYATA memegang keduanya (diukur 2026-09-21). Tanpa urutan ini gerbangnya
    # menjalankan npm di repo yang dependensinya diselesaikan pnpm.
    pm = gl.pm_node(buat(tmp_path, "package.json", "pnpm-lock.yaml", "package-lock.json"))
    assert pm["nama"] == "pnpm"


def test_pm_node_tanpa_lockfile_none(tmp_path):
    assert gl.pm_node(buat(tmp_path, "package.json")) is None


def test_pm_node_menjalankan_skrip_lewat_run_untuk_npm(tmp_path):
    # `npm tsc` bukan perintah; `npm run tsc` yang menjalankan skrip package.json.
    pm = gl.pm_node(buat(tmp_path, "package.json", "package-lock.json"))
    assert pm["jalan"] == "npm run"


# ---------------------------------------------------------------- nol gerbang bukan lulus

def test_jenis_tak_dikenali_gagal():
    lolos, catatan = gl.putuskan_lolos([], "guestbook-system", "lain")
    assert lolos is False
    assert catatan


def test_nol_gerbang_catatan_menyebut_dua_jalan_keluar():
    # Pesan yang cuma bilang "gagal" membuat orang menyangka gerbangnya rusak. Ia wajib menyebut
    # kedua jalan keluar yang sah: tambah cabang jenis, atau tambah ke daftar-izin.
    _, catatan = gl.putuskan_lolos([], "repo-baru", "lain")
    assert "cabang" in catatan.lower()
    assert "daftar-izin" in catatan.lower()


def test_nol_gerbang_lolos_untuk_repo_di_daftar_izin():
    lolos, catatan = gl.putuskan_lolos([], "architecture-draft", "lain")
    assert lolos is True
    assert "daftar-izin" in catatan.lower()


def test_daftar_izin_hanya_berlaku_saat_jenis_lain():
    # Vault yang PUNYA gerbang dan gerbangnya gagal tetap gagal; daftar-izin bukan kekebalan.
    lolos, _ = gl.putuskan_lolos([{"nama": "x", "lolos": False}], "architecture-draft", "lain")
    assert lolos is False


@pytest.mark.parametrize("jenis", ["go", "node", "flutter"])
def test_jenis_dikenali_tanpa_yang_tersentuh_tetap_lolos(jenis):
    # Nol gerbang punya DUA arti yang berlawanan. Repo Go yang branch-nya cuma menyentuh README
    # memang tidak punya yang perlu diperiksa; menolaknya membuat gerbang berbunyi untuk pekerjaan
    # yang benar, dan gerbang yang begitu dimatikan orang dalam sepekan.
    lolos, catatan = gl.putuskan_lolos([], "bip-erp", jenis)
    assert lolos is True
    assert "tidak membuktikan apa pun" in catatan.lower()


def test_gerbang_ada_dan_semua_lolos():
    lolos, catatan = gl.putuskan_lolos([{"nama": "a", "lolos": True}], "bip-erp", "go")
    assert lolos is True and catatan is None


def test_satu_gerbang_gagal_menggagalkan_semua():
    lolos, _ = gl.putuskan_lolos([{"nama": "a", "lolos": True}, {"nama": "b", "lolos": False}], "bip-erp", "go")
    assert lolos is False


def test_daftar_izin_tidak_memuat_repo_kode():
    # Daftar-izin adalah lubang yang disengaja; ia hanya boleh memuat repo TANPA suite mesin.
    for r in ("bip-erp", "erp-frontend", "mybharata-app", "guestbook-system"):
        assert r not in gl.REPO_TANPA_GERBANG


# ---------------------------------------------------------------- alat hilang = gagal

def test_alat_hilang_menghasilkan_gerbang_gagal(monkeypatch):
    # Kebalikan dari bug aslinya: alat yang tidak terpasang TIDAK boleh membuat gerbangnya lenyap.
    monkeypatch.setattr(gl.shutil, "which", lambda n: None)
    g = gl.gerbang_alat(["dart", "flutter"])
    assert g is not None and g["lolos"] is False
    assert "dart" in g["ekor"][0] or "flutter" in g["ekor"][0]


def test_alat_ada_tidak_menghasilkan_gerbang(monkeypatch):
    monkeypatch.setattr(gl.shutil, "which", lambda n: "/usr/bin/" + n)
    assert gl.gerbang_alat(["dart", "flutter"]) is None


# ---------------------------------------------------------------- gerbang kit (vault)

@pytest.mark.parametrize("berkas,harapan", [
    ([".agent-kit/hooks/gerbang.ps1"], True),
    (["Tools/build-vault-index.py"], True),
    (["IT/IT - Gerbang Repo dan Papan Sesi Agent.md"], False),
    (["Decisions/ADR - 0077 x.md", "VAULT-INDEX.json"], False),
    ([], False),
    (["HRIS/x.md", ".agent-kit/VERSION"], True),
])
def test_perlu_gerbang_kit(berkas, harapan):
    assert gk.perlu_gerbang(berkas) is harapan


def test_perlu_gerbang_kit_tidak_tertipu_prefiks_mirip():
    # 'Toolsmith/' bukan 'Tools/'; pencocokan prefiks telanjang akan menyalakan gerbang untuk dok.
    assert gk.perlu_gerbang(["Toolsmith/catatan.md", ".agent-kit-lama/x"]) is False


def test_gerbang_kit_hanya_putuskan_tidak_menjalankan_apa_pun(tmp_path):
    # Gerbang yang MENJALANKAN test-init dari dalam test-init akan berputar tanpa henti.
    # Mode putuskan-saja memisahkan keputusan (yang diuji) dari eksekusi (yang tidak).
    rc = subprocess.run(
        [sys.executable, str(HOOKS / "gerbang-kit.py"), "--hanya-putuskan",
         "--berkas", "HRIS/x.md"],
        capture_output=True, text=True)
    assert rc.returncode == 0
    assert "dilewati" in rc.stdout.lower()


def test_gerbang_kit_hanya_putuskan_menyala_untuk_kit():
    rc = subprocess.run(
        [sys.executable, str(HOOKS / "gerbang-kit.py"), "--hanya-putuskan",
         "--berkas", ".agent-kit/hooks/gerbang.ps1"],
        capture_output=True, text=True)
    assert rc.returncode == 0
    assert "menyala" in rc.stdout.lower()


def test_gerbang_kit_menolak_rekursi():
    # Bila gerbangnya dipicu dari dalam test kit yang sedang berjalan, ia berhenti, bukan berputar.
    env = dict(os.environ, AGENTKIT_KIT_TESTS_RUNNING="1")
    rc = subprocess.run(
        [sys.executable, str(HOOKS / "gerbang-kit.py"), "--berkas", ".agent-kit/VERSION"],
        capture_output=True, text=True, env=env)
    assert rc.returncode == 0
    assert "rekursi" in (rc.stdout + rc.stderr).lower()


# ---------------------------------------------------------------- paritas dua implementasi

@pytest.mark.skipif(shutil.which("powershell") is None, reason="butuh PowerShell")
@pytest.mark.parametrize("berkas,harapan", [
    (["pubspec.yaml"], "flutter"),
    (["package.json", "package-lock.json"], "node"),
    (["package.json", "pnpm-lock.yaml"], "node"),
    (["package.json"], "lain"),
    (["services/a/go.mod"], "go"),
    (["README.md"], "lain"),
])
def test_paritas_jenis_repo_ps_vs_py(tmp_path, berkas, harapan):
    """Logika gerbang punya DUA implementasi; yang menyimpang diam-diam adalah jalur mac/linux.

    Tanpa test ini, cabang baru yang cuma mendarat di satu sisi tidak berbunyi apa pun sampai
    seseorang menjalankan gerbang di OS yang lain.
    """
    top = buat(tmp_path, *berkas)
    lib = (HOOKS / "gerbang-lib.ps1").as_posix()
    cmd = ". '%s'; Get-JenisRepo '%s'" % (lib, top.replace("\\", "/"))
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                       capture_output=True, text=True)
    assert r.stdout.strip() == harapan == gl.jenis_repo(top)
