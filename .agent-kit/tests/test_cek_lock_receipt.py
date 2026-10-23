"""Test keputusan status lock receipt-sync (`hooks/cek-lock-receipt.py`).

Yang dijaga di sini gagalnya SENYAP dan mahal: baris "aman deploy" yang keliru membuat orang
membuat ulang container integration-service di tengah putaran receipt-sync, dan putaran yang
terpotong tidak meninggalkan jejak (IT - Background Jobs & Schedulers, catatan operasional).
Karena itu setiap keadaan yang tak bisa dipastikan harus jatuh ke "tidak bisa dicek" atau "TIDAK
aman", tidak pernah ke "aman".

Jalankan (Windows, dari akar workspace; tanpa cache supaya vault tidak kotor):
  $env:PYTHONDONTWRITEBYTECODE=1
  architecture-draft/Tools/.venv/Scripts/python.exe -m pytest -p no:cacheprovider -q architecture-draft/.agent-kit/tests/test_cek_lock_receipt.py
"""
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
HOOK = HERE.parent / "hooks" / "cek-lock-receipt.py"
spec = importlib.util.spec_from_file_location("cek_lock_receipt", HOOK)
cek = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cek)

WIB = timezone(timedelta(hours=7))
CID = "ab471965afe7"
JADWAL = "0 30 8,11,14,17,20 * * *"
KONFIG = {"jadwal": JADWAL, "timeout_ms": 90 * 60 * 1000, "aktif": True}


def ms(tahun, bulan, hari, jam, menit=0):
    return int(datetime(tahun, bulan, hari, jam, menit, tzinfo=WIB).timestamp() * 1000)


def fakta(sekarang, lock=None, konfig=KONFIG, putaran=(), container=CID):
    return {"sekarang_ms": sekarang, "container_id": container, "lock": lock,
            "konfig": konfig, "putaran": list(putaran)}


def test_lock_dipegang_container_hidup_tidak_aman():
    # kasus nyata 2026-10-23 12:27 WIB: putaran 11:30 berjalan, lock kedaluwarsa 13:00
    f = fakta(ms(2026, 10, 23, 12, 27),
              lock={"owner": CID + "-1", "kedaluwarsa_ms": ms(2026, 10, 23, 13, 0)},
              putaran=[{"mulai_ms": ms(2026, 10, 23, 8, 30), "selesai_ms": ms(2026, 10, 23, 9, 30)}])
    assert cek.putuskan(f) == ("Receipt lock TIDAK aman: receipt-sync sedang berjalan sejak 11:30 "
                               "(lock kedaluwarsa 13:00), aman deploy setelah selesai sampai 14:30")


def test_kosong_dan_jauh_dari_slot_berikutnya_aman():
    f = fakta(ms(2026, 10, 23, 9, 45),
              putaran=[{"mulai_ms": ms(2026, 10, 23, 8, 30), "selesai_ms": ms(2026, 10, 23, 9, 30)}])
    assert cek.putuskan(f) == "Receipt lock kosong dari 09:30 sampai 11:30, aman deploy sekarang"


def test_kosong_tapi_slot_berikutnya_sebentar_lagi_tidak_aman():
    f = fakta(ms(2026, 10, 23, 11, 25),
              putaran=[{"mulai_ms": ms(2026, 10, 23, 8, 30), "selesai_ms": ms(2026, 10, 23, 9, 30)}])
    teks = cek.putuskan(f)
    assert teks.startswith("Receipt lock TIDAK aman: kosong tapi receipt-sync mulai 11:30 (5 menit lagi)")


def test_ambang_tepat_sepuluh_menit_masih_tidak_aman_dan_sebelas_menit_aman():
    selesai = [{"mulai_ms": ms(2026, 10, 23, 8, 30), "selesai_ms": ms(2026, 10, 23, 9, 30)}]
    assert "TIDAK aman" in cek.putuskan(fakta(ms(2026, 10, 23, 11, 20), putaran=selesai))
    assert "aman deploy sekarang" in cek.putuskan(fakta(ms(2026, 10, 23, 11, 19), putaran=selesai))


def test_setelah_slot_terakhir_hari_ini_slot_berikutnya_besok_pagi():
    f = fakta(ms(2026, 10, 23, 22, 0),
              putaran=[{"mulai_ms": ms(2026, 10, 23, 20, 30), "selesai_ms": ms(2026, 10, 23, 21, 31)}])
    assert cek.putuskan(f) == "Receipt lock kosong dari 21:31 sampai besok 08:30, aman deploy sekarang"


def test_lock_yatim_pemilik_bukan_container_hidup_dilaporkan_apa_adanya():
    f = fakta(ms(2026, 10, 23, 9, 45),
              lock={"owner": "container-lama-1", "kedaluwarsa_ms": ms(2026, 10, 23, 10, 0)},
              putaran=[{"mulai_ms": ms(2026, 10, 23, 8, 30), "selesai_ms": ms(2026, 10, 23, 9, 30)}])
    teks = cek.putuskan(f)
    assert "aman deploy sekarang" in teks and "lock yatim" in teks and "10:00" in teks


def test_lock_sudah_kedaluwarsa_dianggap_kosong():
    f = fakta(ms(2026, 10, 23, 13, 30),
              lock={"owner": CID + "-1", "kedaluwarsa_ms": ms(2026, 10, 23, 13, 0)},
              putaran=[{"mulai_ms": ms(2026, 10, 23, 11, 30), "selesai_ms": ms(2026, 10, 23, 12, 40)}])
    assert cek.putuskan(f) == "Receipt lock kosong dari 12:40 sampai 14:30, aman deploy sekarang"


def test_id_container_tak_terbaca_dengan_lock_ada_jatuh_ke_tidak_bisa_dicek_bukan_aman():
    f = fakta(ms(2026, 10, 23, 12, 27),
              lock={"owner": CID + "-1", "kedaluwarsa_ms": ms(2026, 10, 23, 13, 0)}, container="")
    teks = cek.putuskan(f)
    assert "tidak bisa dicek" in teks and "aman deploy sekarang" not in teks


def test_receipt_sync_nonaktif_aman_dengan_catatan():
    f = fakta(ms(2026, 10, 23, 9, 45), konfig=dict(KONFIG, aktif=False))
    assert cek.putuskan(f) == "Receipt lock kosong, receipt-sync nonaktif, aman deploy sekarang"


def test_belum_ada_catatan_putaran_tetap_menyebut_hal_itu():
    assert cek.putuskan(fakta(ms(2026, 10, 23, 9, 45))) == \
        "Receipt lock kosong (belum ada catatan putaran) sampai 11:30, aman deploy sekarang"


def test_jadwal_dibaca_dari_konfig_bukan_dikodekan_keras():
    # jadwal aktual bisa beda dari seed (worker_configs): hanya 09:15 dan 15:15
    konfig = dict(KONFIG, jadwal="0 15 9,15 * * *")
    f = fakta(ms(2026, 10, 23, 10, 0), konfig=konfig,
              putaran=[{"mulai_ms": ms(2026, 10, 23, 9, 15), "selesai_ms": ms(2026, 10, 23, 9, 55)}])
    assert cek.putuskan(f) == "Receipt lock kosong dari 09:55 sampai 15:15, aman deploy sekarang"


def test_jadwal_tak_dikenali_jatuh_ke_jadwal_seed_bukan_error():
    konfig = dict(KONFIG, jadwal="0 */15 * * * *")
    assert "sampai 11:30" in cek.putuskan(fakta(ms(2026, 10, 23, 9, 45), konfig=konfig))


def test_konfig_kosong_memakai_bawaan_dan_timeout_bawaan_90_menit():
    f = fakta(ms(2026, 10, 23, 12, 27),
              lock={"owner": CID + "-1", "kedaluwarsa_ms": ms(2026, 10, 23, 13, 0)}, konfig=None)
    assert "sejak 11:30" in cek.putuskan(f)


def test_waktu_server_hilang_tidak_pernah_menghasilkan_aman():
    teks = cek.putuskan({"container_id": CID})
    assert "tidak bisa dicek" in teks and "aman deploy sekarang" not in teks


def test_cli_membaca_baris_json_terakhir_walau_ada_peringatan_di_atasnya(tmp_path):
    f = fakta(ms(2026, 10, 23, 9, 45),
              putaran=[{"mulai_ms": ms(2026, 10, 23, 8, 30), "selesai_ms": ms(2026, 10, 23, 9, 30)}])
    masuk = "peringatan mongosh bukan json\n" + json.dumps(f) + "\n"
    r = subprocess.run([sys.executable, str(HOOK)], input=masuk, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0
    assert r.stdout.strip() == "Receipt lock kosong dari 09:30 sampai 11:30, aman deploy sekarang"


def test_cli_menerima_bom_di_awal_pipa_seperti_dari_powershell_51():
    f = fakta(ms(2026, 10, 23, 9, 45),
              putaran=[{"mulai_ms": ms(2026, 10, 23, 8, 30), "selesai_ms": ms(2026, 10, 23, 9, 30)}])
    masuk = b"\xef\xbb\xbf" + json.dumps(f).encode("utf-8") + b"\r\n"
    r = subprocess.run([sys.executable, str(HOOK)], input=masuk, capture_output=True)
    assert r.returncode == 0
    assert r.stdout.decode("utf-8").strip() == "Receipt lock kosong dari 09:30 sampai 11:30, aman deploy sekarang"


@pytest.mark.parametrize("masuk", ["", "bukan json", "[]", "{rusak"])
def test_cli_jawaban_server_tak_terbaca_menghasilkan_tidak_bisa_dicek(masuk):
    r = subprocess.run([sys.executable, str(HOOK)], input=masuk, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0
    assert "tidak bisa dicek" in r.stdout and "aman deploy sekarang" not in r.stdout
