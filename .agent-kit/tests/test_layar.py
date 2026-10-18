"""Test keputusan deterministik judge desain (`hooks/layar-lib.py`).

Yang dijaga di sini adalah kegagalan yang SENYAP:

1. **Tangkapan gagal bukan "layar bersih".** Ringkasan tanpa satu pun rute yang berhasil ditangkap
   tidak boleh dibaca sebagai layar yang dinilai bersih; itu `layar_dinilai: false`.
2. **Mendarat di /login atau 404 bukan galat kode.** Itu masalah tangkapan (sesi/manifest), dan
   menuduh eksekutor atas hal itu membuat loop berputar tanpa sebab.
3. **Error boundary selalu galat kode** (kecuali `galat` alat atau /login, yang menang lebih dulu).
4. **Bantahan atas temuan yang tak ada dihitung nol**, bukan salah tuduh.

Jalankan (Windows, dari akar workspace; tanpa cache supaya vault tidak kotor):
  $env:PYTHONDONTWRITEBYTECODE=1
  architecture-draft/Tools/.venv/Scripts/python.exe -m pytest -p no:cacheprovider -q architecture-draft/.agent-kit/tests/test_layar.py
"""
import copy
import importlib.util
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
HOOKS = HERE.parent / "hooks"


def _muat():
    # LAYAR_LIB_MODUL menunjuk salinan yang sengaja dimutasi (kontrol negatif).
    sumber = os.environ.get("LAYAR_LIB_MODUL") or (HOOKS / "layar-lib.py")
    spec = importlib.util.spec_from_file_location("layar_lib", sumber)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


L = _muat()

MANIFEST = {
    "rute": [{"path": "/hris/kpi", "keadaan": ["berisi", "kosong"]}],
    "cookie": {"system_roles": {"hris": "supervisor"}, "position": "Staff", "department": "IT", "lang": "id"},
    "stub": {
        "berisi": [{"pola": "/kpi", "status": 200, "body": {"data": [1]}}],
        "kosong": [{"pola": "/kpi", "status": 200, "body": {"data": []}}],
    },
}


def _manifest(**ubah):
    m = copy.deepcopy(MANIFEST)
    m.update(ubah)
    return m


def _hasil(**kw):
    h = {"rute_akhir": "/hris/kpi", "status_http": 200, "error_boundary": False, "konsol": [], "galat": None}
    h.update(kw)
    return h


# --- pemilihan berkas layar ---

def test_berkas_layar_memilih_tsx_ui():
    masuk = ["src/app/hris/page.tsx", "src/lib/axios.ts", "src/features/kpi/components/x.tsx",
             "src/features/kpi/x.test.tsx", "src/i18n/locales/id.ts"]
    assert L.berkas_layar(masuk) == ["src/app/hris/page.tsx", "src/features/kpi/components/x.tsx"]


def test_berkas_layar_menerima_backslash_dan_spec():
    assert L.berkas_layar(["src\\components\\a.tsx", "src/components/a.spec.tsx"]) == ["src/components/a.tsx"]


def test_locale_dan_test_bukan_layar():
    assert L.perlu_judge_desain("erp-frontend", ["src/i18n/locales/en.ts", "src/features/a/__tests__/b.tsx"]) is False


def test_repo_lain_tidak_menyala():
    assert L.perlu_judge_desain("my-bharata", ["src/app/x.tsx"]) is False


def test_repo_frontend_dengan_layar_menyala():
    assert L.perlu_judge_desain("erp-frontend", ["src/app/x.tsx"]) is True


# --- manifest ---

def test_manifest_sah():
    assert L.validasi_manifest(MANIFEST) == []


def test_manifest_roles_array_ditolak():
    m = _manifest(cookie={"system_roles": {"hris": ["supervisor"]}})
    galat = L.validasi_manifest(m)
    assert len(galat) == 1 and "system_roles" in galat[0]


def test_manifest_stub_401_ditolak():
    m = _manifest(stub={"berisi": [{"pola": "/x", "status": 401, "body": {}}],
                        "kosong": MANIFEST["stub"]["kosong"]})
    galat = L.validasi_manifest(m)
    assert any("401" in g for g in galat)


def test_manifest_tanpa_keadaan_kosong_ditolak():
    m = _manifest(stub={"berisi": MANIFEST["stub"]["berisi"]})
    galat = L.validasi_manifest(m)
    assert any("kosong" in g for g in galat)


def test_manifest_keadaan_tak_dikenal_ditolak():
    m = _manifest(rute=[{"path": "/a", "keadaan": ["error"]}])
    galat = L.validasi_manifest(m)
    assert any("error" in g for g in galat)


def test_manifest_rute_kosong_dan_path_tanpa_slash_ditolak():
    assert any("rute" in g for g in L.validasi_manifest(_manifest(rute=[])))
    assert any("path" in g for g in L.validasi_manifest(_manifest(rute=[{"path": "hris", "keadaan": []}])))


def test_manifest_bukan_dict_ditolak():
    assert L.validasi_manifest([]) != []


# --- klasifikasi ---

def test_klasifikasi_ok():
    assert L.klasifikasi_rute(_hasil(), []) == "ok"


def test_klasifikasi_login_tangkapan_gagal():
    assert L.klasifikasi_rute(_hasil(rute_akhir="/login"), []) == "tangkapan_gagal"


def test_klasifikasi_404_tangkapan_gagal():
    assert L.klasifikasi_rute(_hasil(status_http=404), []) == "tangkapan_gagal"


def test_klasifikasi_galat_tangkapan_gagal():
    assert L.klasifikasi_rute(_hasil(galat="timeout"), []) == "tangkapan_gagal"


def test_error_boundary_menunjuk_diff_galat_kode():
    h = _hasil(error_boundary=True, konsol=["TypeError ... at src/features/kpi/components/x.tsx:12"])
    assert L.klasifikasi_rute(h, ["src/features/kpi/components/x.tsx"]) == "galat_kode"


def test_error_boundary_bukan_diff_galat_kode():
    # Diubah 2026-10-18: build produksi tanpa source map, stack konsol menunjuk chunk, jadi syarat
    # "konsol menunjuk berkas diff" tak pernah terpenuhi. Boundary = kode aplikasi atau stub
    # eksekutor, keduanya tanggungan eksekutor.
    h = _hasil(error_boundary=True, konsol=["TypeError at src/components/table/index.tsx:3"])
    assert L.klasifikasi_rute(h, ["src/features/kpi/components/x.tsx"]) == "galat_kode"


def test_error_boundary_konsol_chunk_kosong_galat_kode():
    h = _hasil(error_boundary=True, konsol=["TypeError at http://localhost:4000/_next/static/chunks/a1b2.js:1:99"])
    assert L.klasifikasi_rute(h, []) == "galat_kode"
    assert L.klasifikasi_rute(_hasil(error_boundary=True, status_http=500), []) == "galat_kode"


def test_error_boundary_kalah_dari_galat_dan_login():
    assert L.klasifikasi_rute(_hasil(error_boundary=True, galat="timeout"), []) == "tangkapan_gagal"
    assert L.klasifikasi_rute(_hasil(error_boundary=True, rute_akhir="/login"), []) == "tangkapan_gagal"


def test_error_boundary_konsol_backslash_cocok():
    h = _hasil(error_boundary=True, konsol=["at src\\features\\kpi\\x.tsx:1"])
    assert L.klasifikasi_rute(h, ["src/features/kpi/x.tsx"]) == "galat_kode"


# --- ringkasan ---

def test_ringkasan_tanpa_tangkapan_tidak_dinilai():
    assert L.layar_dinilai({"rute": []}) is False
    assert L.layar_dinilai({"rute": [_hasil(rute_akhir="/login"), _hasil(status_http=404)]}) is False


def test_ringkasan_dengan_ok_atau_galat_kode_dinilai():
    assert L.layar_dinilai({"rute": [_hasil(rute_akhir="/login"), _hasil()]}) is True
    boundary = _hasil(error_boundary=True, konsol=["at src/app/a.tsx:1"])
    assert L.layar_dinilai({"rute": [boundary]}, ["src/app/a.tsx"]) is True


# --- salah tuduh ---

TEMUAN = [{"file": "a.tsx", "line": 3, "alasan": "kontras"}, {"file": "b.tsx", "line": 9, "alasan": "tap target"}]


def _bantah(t):
    return {"temuan": t, "alasan": "keliru", "bukti": "offsetWidth 44"}


def _putus(t, putusan):
    return {"temuan": t, "putusan": putusan, "alasan": "dinilai ulang"}


def test_bantahan_diterima_dihitung():
    berikut = {"temuan": [], "bantahan": [_putus(TEMUAN[0], "diterima")]}
    assert L.hitung_salah_tuduh(berikut, [_bantah(TEMUAN[0])], TEMUAN) == {"diterima": 1, "ditolak": 0, "diabaikan": 0}


def test_bantahan_ditolak_dihitung():
    berikut = {"temuan": list(TEMUAN), "bantahan": [_putus(TEMUAN[0], "ditolak")]}
    assert L.hitung_salah_tuduh(berikut, [_bantah(TEMUAN[0])], TEMUAN) == {"diterima": 0, "ditolak": 1, "diabaikan": 0}


def test_bantahan_tanpa_temuan_diabaikan():
    z = {"file": "z.tsx", "line": 1, "alasan": "tak ada"}
    berikut = {"temuan": list(TEMUAN), "bantahan": [_putus(z, "diterima")]}
    assert L.hitung_salah_tuduh(berikut, [_bantah(z)], TEMUAN) == {"diterima": 0, "ditolak": 0, "diabaikan": 1}


def test_bantahan_tanpa_putusan_ditolak():
    # temuan hilang dari verdict tapi judge tak memutus: tidak disimpulkan diterima
    assert L.hitung_salah_tuduh({"temuan": []}, [_bantah(TEMUAN[0])], TEMUAN) == {"diterima": 0, "ditolak": 1, "diabaikan": 0}


def test_boundary_500_menunjuk_diff_galat_kode():
    h = _hasil(status_http=500, error_boundary=True, konsol=["Error at src/features/kpi/x.tsx:5"])
    assert L.klasifikasi_rute(h, ["src/features/kpi/x.tsx"]) == "galat_kode"


# --- CLI (subprocess, input ber-BOM seperti keluaran PowerShell 5.1) ---

def _jalan(*args):
    import json as _j
    import subprocess
    p = subprocess.run([sys.executable, str(HOOKS / "layar-lib.py"), *map(str, args)],
                       capture_output=True, text=True)
    return p.returncode, _j.loads(p.stdout)


def _tulis(path, teks, bom=True):
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + teks.encode("utf-8"))
    return path


def test_cli_perlu_dengan_bom(tmp_path):
    f = _tulis(tmp_path / "b.txt", "src/app/x.tsx\n")
    kode, out = _jalan("perlu", "--repo", "erp-frontend", "--berkas-dari", f)
    assert kode == 0 and out == {"perlu": True, "berkas_layar": ["src/app/x.tsx"]}


def test_cli_validasi_sah_dan_gagal(tmp_path):
    import json as _j
    sah = _tulis(tmp_path / "m.json", _j.dumps(MANIFEST))
    assert _jalan("validasi", sah) == (0, {"galat": []})
    buruk = _tulis(tmp_path / "n.json", _j.dumps(_manifest(rute=[])))
    kode, out = _jalan("validasi", buruk)
    assert kode == 1 and out["galat"]


def test_cli_ringkas_dengan_bom(tmp_path):
    import json as _j
    r = _tulis(tmp_path / "r.json", _j.dumps({"rute": [_hasil(rute_akhir="/login"), _hasil()]}))
    d = _tulis(tmp_path / "d.txt", "src/app/x.tsx\n")
    kode, out = _jalan("ringkas", r, "--berkas-dari", d)
    assert kode == 0 and out["layar_dinilai"] is True
    assert [x["klasifikasi"] for x in out["rute"]] == ["tangkapan_gagal", "ok"]
