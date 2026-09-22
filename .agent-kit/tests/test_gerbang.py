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


def test_folder_dart_menandai_saat_terpotong():
    # Pemotongan diam-diam = sebagian perubahan tak dianalisis sementara gerbangnya hijau.
    banyak = ["f%02d/x.dart" % i for i in range(gl.BATAS_FOLDER_DART + 3)]
    folder, terpotong = gl.folder_dart(banyak)
    assert terpotong is True and len(folder) == gl.BATAS_FOLDER_DART
    folder, terpotong = gl.folder_dart(["lib/a/x.dart", "lib/b/y.dart", "README.md"])
    assert terpotong is False and folder == ["lib/a", "lib/b"]


def test_folder_dart_membuang_yang_sudah_tercakup_induknya():
    # `dart analyze lib lib/src/core/api` menganalisis subpohon yang sama dua kali. Diukur di
    # mybharata-app: 21 folder menyusut jadi 1, dan pemotongan 20-folder pun jadi tak terpicu.
    folder, terpotong = gl.folder_dart([
        "lib/app_root.dart", "lib/src/core/api/api.dart", "lib/l10n/app_localizations.dart",
        "test/unit/x.dart",
    ])
    assert folder == ["lib", "test/unit"]
    assert terpotong is False


def test_folder_dart_meruntuhkan_ke_akar_alih_alih_memotong():
    # Kasus nyata mybharata-app: 20+ folder daun di bawah `test/` yang tidak bersarang satu sama
    # lain. Memotongnya membuang pemeriksaan diam-diam; meruntuhkannya ke `test` justru MENAMBAH
    # cakupan karena dart analyze bekerja rekursif.
    banyak = ["test/features/f%02d/x.dart" % i for i in range(30)] + ["lib/a.dart"]
    folder, terpotong = gl.folder_dart(banyak)
    assert folder == ["lib", "test"]
    assert terpotong is False


def test_folder_dart_tidak_tertipu_prefiks_mirip():
    # 'libx' bukan anak 'lib'; pencocokan prefiks telanjang akan membuangnya tanpa dianalisis.
    folder, _ = gl.folder_dart(["lib/a.dart", "libx/b.dart"])
    assert folder == ["lib", "libx"]


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


def test_env_bersih_membuang_seluruh_git(monkeypatch):
    # Git mewariskan GIT_DIR dan kawannya ke hook-nya, dan variabel itu MENANG atas penemuan repo:
    # `git -C <folder lain>` tetap mengenai repo yang sedang di-push. Terukur 2026-09-21, test kit
    # yang berjalan di bawah hook menulis dua commit kosong dan sebuah branch ke repo NYATA.
    for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_QUARANTINE_PATH", "GIT_EXEC_PATH"):
        monkeypatch.setenv(k, "x")
    monkeypatch.setenv("PENANDA_UJI", "tetap")
    env = gk.env_bersih(AGENTKIT_KIT_TESTS_RUNNING="1")
    assert not [k for k in env if k.startswith("GIT_")]
    assert env["PENANDA_UJI"] == "tetap"
    assert env["AGENTKIT_KIT_TESTS_RUNNING"] == "1"


def test_env_bersih_tidak_mengubah_environ_proses(monkeypatch):
    monkeypatch.setenv("GIT_DIR", "x")
    gk.env_bersih()
    assert os.environ.get("GIT_DIR") == "x"


@pytest.mark.skipif(shutil.which("powershell") is None, reason="butuh PowerShell")
def test_test_init_menolak_jalan_saat_git_dir_terwarisi(tmp_path):
    # Penjaga lapis kedua, dijalankan sungguhan: test-init membuat repo sandbox, jadi ia tidak
    # boleh jalan sama sekali bila lingkungan hook masih menempel.
    env = dict(os.environ, GIT_DIR=str(tmp_path))
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-File", str(HERE / "test-init.ps1")],
                       capture_output=True, text=True, env=env, timeout=180)
    assert r.returncode == 1
    assert "MENOLAK jalan" in r.stdout


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


def test_gerbang_kit_paksa_menyala_walau_berkas_tak_relevan():
    # Daftar berkas yang tak bisa ditentukan harus MENYALAKAN gerbang, bukan mematikannya.
    # Terukur 2026-09-21: `$rsha` di pre-push bisa menunjuk commit yang belum ada di sini, lalu
    # `git diff` gagal diam-diam dan push ber-perubahan .agent-kit/ dilaporkan "DILEWATI".
    rc = subprocess.run(
        [sys.executable, str(HOOKS / "gerbang-kit.py"), "--hanya-putuskan", "--paksa",
         "--berkas", "HRIS/x.md"],
        capture_output=True, text=True)
    assert rc.returncode == 0
    assert "dinyalakan" in rc.stdout.lower()


def test_pre_push_memeriksa_basis_diff_ada_sebelum_memakainya():
    # Dijaga di sumber karena pre-push adalah skrip sh yang tak punya harness test sendiri di
    # sini; yang dikunci adalah keberadaan pemeriksaan objek dan penerusan --paksa.
    teks = (HOOKS / "githooks" / "pre-push").read_text(encoding="utf-8")
    assert "git cat-file -e" in teks
    assert "tak_tentu=1" in teks
    assert "--paksa" in teks
    # Go: daftar yang tak bisa ditentukan harus membangun SEMUA service, bukan melewatinya
    assert '[ "$tak_tentu" -eq 1 ] || printf' in teks


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


@pytest.mark.skipif(shutil.which("powershell") is None, reason="butuh PowerShell")
def test_paritas_konstanta_ps_vs_py():
    """Batas waktu, peta lockfile, dan daftar-izin hidup di DUA berkas.

    `jenis_repo` saja tidak cukup: nilai yang cuma diubah di satu sisi (mis. `BATAS_ANALYZE`
    dinaikkan di Python tapi tidak di PowerShell, atau lockfile baru ditambahkan di satu peta)
    menyimpang tanpa satu pun test merah, dan yang memakainya di OS lain tidak akan tahu.
    """
    lib = (HOOKS / "gerbang-lib.ps1").as_posix()
    cmd = (". '%s'; @{ batas_analyze = $script:BatasAnalyze; batas_test_flutter = "
           "$script:BatasTestFlutter; batas_folder_dart = $script:BatasFolderDart; "
           "repo_tanpa_gerbang = @($script:RepoTanpaGerbang); pm_node = @($script:PmNode | "
           "ForEach-Object { ,@($_.berkas, $_.nama, $_.jalan, $_.exec) }) } | "
           "ConvertTo-Json -Depth 5 -Compress") % lib
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    ps = json.loads(r.stdout)

    rp = subprocess.run([sys.executable, str(HOOKS / "gerbang-lib.py"), "konstanta"],
                        capture_output=True, text=True)
    assert rp.returncode == 0, rp.stderr
    py = json.loads(rp.stdout)

    assert ps["batas_analyze"] == py["batas_analyze"]
    assert ps["batas_test_flutter"] == py["batas_test_flutter"]
    assert ps["batas_folder_dart"] == py["batas_folder_dart"]
    assert list(ps["repo_tanpa_gerbang"]) == list(py["repo_tanpa_gerbang"])
    # urutan ikut dibandingkan: itulah yang menentukan pnpm menang atas npm di erp-frontend
    assert [list(x) for x in ps["pm_node"]] == [list(x) for x in py["pm_node"]]
