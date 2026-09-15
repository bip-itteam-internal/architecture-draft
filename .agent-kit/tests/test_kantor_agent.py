"""Test penulis data Kantor Agent (`hooks/kantor-agent.py`).

Skenario disusun dari templat baris transkrip NYATA di `fixtures/kantor-agent/baris-nyata.json`
(lihat README di sana). Hanya field yang diuji yang diubah, supaya parser diuji terhadap bentuk
asli Claude Code, bukan terhadap bentuk yang kita bayangkan.

Jalankan (Windows, dari akar workspace; tanpa cache supaya vault tidak kotor):
  $env:PYTHONDONTWRITEBYTECODE=1
  architecture-draft/Tools/.venv/Scripts/python.exe -m pytest -p no:cacheprovider -q architecture-draft/.agent-kit/tests/test_kantor_agent.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "kantor-agent"
SEKARANG = datetime(2026, 9, 15, 7, 0, 0, tzinfo=timezone.utc)
WS = "C:/uji/ws"  # hanya untuk fungsi murni; tidak menyentuh disk


def _muat_modul():
    # KANTOR_AGENT_MODUL menunjuk salinan yang sengaja dimutasi, untuk membuktikan test tidak vakum
    # tanpa menyunting berkas aslinya.
    sumber = os.environ.get("KANTOR_AGENT_MODUL") or (HERE.parent / "hooks" / "kantor-agent.py")
    spec = importlib.util.spec_from_file_location("kantor_agent", sumber)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


ka = _muat_modul()
TEMPLAT = json.loads((FIXTURE / "baris-nyata.json").read_text(encoding="utf-8"))
META = json.loads((FIXTURE / "meta-subagent.json").read_text(encoding="utf-8"))


# ---------- perakit skenario dari templat nyata ----------

def _ts(detik, dasar=SEKARANG):
    return (dasar + timedelta(seconds=detik)).isoformat().replace("+00:00", "Z")


def _epoch(detik, dasar=SEKARANG):
    return (dasar + timedelta(seconds=detik)).timestamp()


def baris(jenis, ws, detik=-60, dasar=SEKARANG):
    teks = json.dumps(TEMPLAT[jenis]).replace("{WORKSPACE}", json.dumps(str(ws))[1:-1])
    o = json.loads(teks)
    if "timestamp" in o:
        o["timestamp"] = _ts(detik, dasar)
    return o


def tool_use(ws, nama, id_, masukan=None, detik=-30, subagent=False, dasar=SEKARANG):
    o = baris("subagent_assistant_tool_use" if subagent else "assistant_tool_use", ws, detik, dasar)
    blok = o["message"]["content"][0]
    blok["name"], blok["id"] = nama, id_
    blok["input"] = masukan if masukan is not None else {"description": "uji"}
    return o


def tool_result(ws, id_, detik=-20, dasar=SEKARANG):
    o = baris("user_tool_result", ws, detik, dasar)
    o["message"]["content"][0]["tool_use_id"] = id_
    return o


def end_turn(ws, detik=-10, subagent=False, dasar=SEKARANG):
    return baris("subagent_assistant_end_turn" if subagent else "assistant_end_turn", ws, detik, dasar)


def prompt(ws, detik=-5, dasar=SEKARANG):
    return baris("user_prompt", ws, detik, dasar)


def meta_user(ws, detik=-5, dasar=SEKARANG):
    return baris("user_meta", ws, detik, dasar)


def keadaan_dari(kejadian, ada_subagent=False):
    return ka.turunkan_keadaan(ka.urai(kejadian), ada_subagent, SEKARANG)


def tulis_jsonl(path, kejadian, mtime):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(o) + "\n" for o in kejadian), encoding="utf-8")
    os.utime(path, (mtime, mtime))
    return path


def baca_data(ws):
    teks = (ws / ".task-plans" / "kantor-agent-data.js").read_text(encoding="utf-8")
    awalan = "window.__KANTOR__ = "
    assert teks.startswith(awalan)
    return json.loads(teks[len(awalan):].rstrip().rstrip(";"))


@pytest.fixture
def lingkungan(tmp_path):
    ws = tmp_path / "ws"
    (ws / ".task-plans" / "sesi").mkdir(parents=True)
    proyek = tmp_path / "proyek"
    (proyek / "slug-uji").mkdir(parents=True)
    return ws, proyek


def kumpulkan(ws, proyek):
    return ka.kumpulkan(str(proyek), str(ws), SEKARANG)


# ---------- peta ----------

@pytest.mark.parametrize("nama, area", [
    ("Read", "perpustakaan"), ("Grep", "perpustakaan"), ("Glob", "perpustakaan"), ("WebFetch", "perpustakaan"),
    ("WebSearch", "perpustakaan"), ("Skill", "perpustakaan"), ("ToolSearch", "perpustakaan"),
    ("Edit", "meja"), ("Write", "meja"), ("NotebookEdit", "meja"),
    ("PowerShell", "server"), ("Bash", "server"), ("Monitor", "server"), ("TaskOutput", "server"), ("TaskStop", "server"),
    ("Agent", "rapat"), ("Workflow", "rapat"), ("SendMessage", "rapat"),
    ("AskUserQuestion", "lounge"), ("ExitPlanMode", "lounge"),
    ("mcp__vault__read_note", "server"), ("AlatBaruEntahApa", "server"),
])
def test_peta_area_alat(nama, area):
    assert ka.area_alat(nama) == area


@pytest.mark.parametrize("jenis, hasil", [
    ("general-purpose", "Generalis"), ("Explore", "Peneliti"), ("Plan", "Arsitek"), ("loop-fix", "Engineer"),
    ("loop-test", "QA"), ("loop-refactor", "Refactor"), ("loop-judge", "Juri"), ("loop-docs", "Penulis"),
    ("claude-code-guide", "Pemandu"), ("agen-baru-tim", "agen-baru-tim"), (None, "subagent"),
])
def test_peran_dari_agent_type(jenis, hasil):
    assert ka.peran(jenis) == hasil


# ---------- penurunan keadaan (fungsi murni) ----------

def test_tool_tertunda_menentukan_area_detail_dan_durasi():
    k = keadaan_dari([prompt(WS, -60), baris("assistant_thinking", WS, -45),
                      tool_use(WS, "PowerShell", "toolu_a", {"command": "pnpm test", "description": "jalankan uji"}, -30)])
    assert (k["area"], k["keadaan"], k["alat"], k["detail"]) == ("server", "alat", "PowerShell", "jalankan uji")
    assert k["durasi_detik"] == 30


def test_hasil_tool_membuat_berpikir_di_meja():
    k = keadaan_dari([tool_use(WS, "Read", "toolu_a", {"file_path": "x/y.go"}, -30), tool_result(WS, "toolu_a", -20)])
    assert (k["area"], k["keadaan"], k["alat"]) == ("meja", "berpikir", "")


def test_beberapa_tool_paralel_yang_masih_tertunda_menentukan():
    k = keadaan_dari([tool_use(WS, "Read", "toolu_a", None, -30), tool_use(WS, "PowerShell", "toolu_b", None, -29),
                      tool_result(WS, "toolu_b", -20)])
    assert (k["area"], k["alat"]) == ("perpustakaan", "Read")


def test_batch_tool_lambat_dulu_hasil_read_tertahan_tetap_di_ruang_server():
    # transkrip nyata: [PowerShell, Read] satu pesan, hasil Read baru tertulis setelah PowerShell selesai
    k = keadaan_dari([tool_use(WS, "PowerShell", "toolu_a", {"description": "verifikasi"}, -100),
                      tool_use(WS, "Read", "toolu_b", {"file_path": "x/indeks.md"}, -99)])
    assert (k["area"], k["alat"], k["detail"]) == ("server", "PowerShell", "verifikasi")
    assert k["durasi_detik"] == 100


def test_batch_tool_cepat_dulu_hasil_tertahan_tetap_di_ruang_alat_lambat():
    k = keadaan_dari([tool_use(WS, "Grep", "toolu_a", None, -100), tool_use(WS, "Agent", "toolu_b", None, -99)])
    assert (k["area"], k["alat"]) == ("rapat", "Agent")


def test_batch_tool_lambat_semua_yang_paling_awal_menentukan():
    k = keadaan_dari([tool_use(WS, "Agent", "toolu_a", None, -100), tool_use(WS, "PowerShell", "toolu_b", None, -99)])
    assert (k["area"], k["alat"]) == ("rapat", "Agent")


def test_batch_tool_singkat_semua_yang_paling_awal_menentukan():
    k = keadaan_dari([tool_use(WS, "Edit", "toolu_a", None, -30), tool_use(WS, "Read", "toolu_b", None, -29)])
    assert (k["area"], k["alat"]) == ("meja", "Edit")


def test_detail_read_hanya_nama_berkas_bukan_path():
    k = keadaan_dari([tool_use(WS, "Read", "toolu_a", {"file_path": "C:/dalam/sekali/handler_kpi.go"}, -3)])
    assert k["detail"] == "handler_kpi.go"


def test_tanya_pengguna_menunggu_di_lounge_dengan_header():
    k = keadaan_dari([tool_use(WS, "AskUserQuestion", "toolu_a", {"questions": [{"header": "Gaya", "question": "Pilih?"}]}, -8)])
    assert (k["area"], k["keadaan"], k["alat"], k["detail"]) == ("lounge", "menunggu_anda", "AskUserQuestion", "Gaya")


def test_end_turn_tanpa_subagent_menunggu_anda_di_lounge():
    k = keadaan_dari([tool_use(WS, "Read", "toolu_a", None, -30), tool_result(WS, "toolu_a", -20), end_turn(WS, -10)])
    assert (k["area"], k["keadaan"], k["alat"]) == ("lounge", "menunggu_anda", "")
    assert k["diam_detik"] == 10


def test_end_turn_dengan_subagent_hidup_menunggu_di_rapat():
    k = keadaan_dari([end_turn(WS, -10)], ada_subagent=True)
    assert (k["area"], k["keadaan"]) == ("rapat", "menunggu_subagent")


def test_end_turn_menghapus_tool_tertunda_yang_tak_pernah_berhasil():
    k = keadaan_dari([tool_use(WS, "PowerShell", "toolu_a", None, -30), end_turn(WS, -10)])
    assert (k["area"], k["keadaan"]) == ("lounge", "menunggu_anda")


def test_prompt_baru_membatalkan_tool_tertunda():
    k = keadaan_dari([tool_use(WS, "Edit", "toolu_a", None, -30), prompt(WS, -5)])
    assert (k["area"], k["keadaan"], k["alat"]) == ("meja", "berpikir", "")


def test_pesan_meta_tidak_membatalkan_tool_tertunda():
    k = keadaan_dari([tool_use(WS, "PowerShell", "toolu_a", None, -30), meta_user(WS, -5)])
    assert (k["area"], k["alat"]) == ("server", "PowerShell")


def test_kejadian_non_percakapan_diabaikan_judul_dan_pr_terbaca():
    judul = baris("ai-title", WS)
    judul["aiTitle"] = "Judul uji"
    pr = baris("pr-link", WS, -1)
    pr["prNumber"] = 42
    u = ka.urai([judul, tool_use(WS, "Grep", "toolu_a", {"pattern": "cari"}, -30), baris("attachment", WS, -25),
                 baris("queue-operation", WS, -24), pr])
    k = ka.turunkan_keadaan(u, False, SEKARANG)
    assert (k["area"], k["alat"], k["detail"]) == ("perpustakaan", "Grep", "cari")
    assert (u["judul"], u["pr"], u["dikenal"]) == ("Judul uji", "#42", 1)


def test_tool_tak_dikenal_tampil_dengan_nama_aslinya():
    k = keadaan_dari([tool_use(WS, "mcp__vault__read_note", "toolu_a", {"path": "a"}, -4)])
    assert (k["area"], k["alat"]) == ("server", "mcp__vault__read_note")


def test_di_dalam_workspace(tmp_path):
    ws = tmp_path / "ws"
    (ws / "sub").mkdir(parents=True)
    assert ka.di_dalam_workspace(str(ws), str(ws))
    assert ka.di_dalam_workspace(str(ws / "sub"), str(ws))
    assert not ka.di_dalam_workspace(str(tmp_path / "ws-lain"), str(ws))  # awalan string sama bukan berarti di dalam
    assert not ka.di_dalam_workspace("", str(ws))


@pytest.mark.skipif(os.name != "nt", reason="huruf besar-kecil path hanya setara di Windows")
def test_di_dalam_workspace_beda_huruf_di_windows(tmp_path):
    ws = str(tmp_path / "ws")
    assert ka.di_dalam_workspace(ws.upper(), ws.lower())


def test_waktu_tujuh_digit_pecahan_dari_powershell():
    # berkas sesi kit ditulis PowerShell ToString('o'): 7 digit; Python <= 3.10 hanya menerima 3 atau 6
    assert ka._waktu("2026-09-08T01:15:11.0245893Z") == datetime(2026, 9, 8, 1, 15, 11, 24589, tzinfo=timezone.utc)
    assert ka._waktu("2026-09-15T06:34:00.123Z") == datetime(2026, 9, 15, 6, 34, 0, 123000, tzinfo=timezone.utc)
    assert ka._waktu("bukan waktu") is None and ka._waktu(None) is None


# ---------- pengumpulan dari disk ----------

def test_kumpulkan_lead_dengan_subagent_hidup(lingkungan):
    ws, proyek = lingkungan
    folder = proyek / "slug-uji"
    tulis_jsonl(folder / "sesi-a.jsonl", [prompt(ws, -90), end_turn(ws, -60)], _epoch(-60))
    sub = folder / "sesi-a" / "subagents"
    tulis_jsonl(sub / "agent-abc123.jsonl", [tool_use(ws, "PowerShell", "toolu_s", {"description": "hitung"}, -5, subagent=True)], _epoch(-5))
    (sub / "agent-abc123.meta.json").write_text(json.dumps(dict(META, agentType="Explore", description="cari pola")), encoding="utf-8")
    data = kumpulkan(ws, proyek)
    assert [s["id"] for s in data["sesi"]] == ["sesi-a"]
    s = data["sesi"][0]
    assert (s["area"], s["keadaan"]) == ("rapat", "menunggu_subagent")
    assert [(a["id"], a["jenis"], a["peran"], a["deskripsi"], a["area"], a["alat"], a["detail"]) for a in s["subagent"]] == [
        ("abc123", "Explore", "Peneliti", "cari pola", "server", "PowerShell", "hitung")]
    assert data["skema"]["dikenali"] is True


def test_subagent_yang_sudah_end_turn_pulang(lingkungan):
    ws, proyek = lingkungan
    folder = proyek / "slug-uji"
    tulis_jsonl(folder / "sesi-a.jsonl", [end_turn(ws, -60)], _epoch(-60))
    tulis_jsonl(folder / "sesi-a" / "subagents" / "agent-x1.jsonl", [end_turn(ws, -5, subagent=True)], _epoch(-5))
    s = kumpulkan(ws, proyek)["sesi"][0]
    assert s["subagent"] == []
    assert (s["area"], s["keadaan"]) == ("lounge", "menunggu_anda")


def test_subagent_diam_lebih_10_menit_pulang(lingkungan):
    ws, proyek = lingkungan
    folder = proyek / "slug-uji"
    tulis_jsonl(folder / "sesi-a.jsonl", [end_turn(ws, -60)], _epoch(-60))
    tulis_jsonl(folder / "sesi-a" / "subagents" / "agent-x1.jsonl", [tool_use(ws, "Read", "toolu_s", None, -700, subagent=True)], _epoch(-700))
    assert kumpulkan(ws, proyek)["sesi"][0]["subagent"] == []


def test_subagent_tanpa_meta_tetap_tampil(lingkungan):
    ws, proyek = lingkungan
    folder = proyek / "slug-uji"
    tulis_jsonl(folder / "sesi-a.jsonl", [end_turn(ws, -60)], _epoch(-60))
    tulis_jsonl(folder / "sesi-a" / "subagents" / "agent-x1.jsonl", [tool_use(ws, "Grep", "toolu_s", None, -5, subagent=True)], _epoch(-5))
    a = kumpulkan(ws, proyek)["sesi"][0]["subagent"][0]
    assert (a["jenis"], a["peran"], a["area"]) == ("subagent", "subagent", "perpustakaan")


def test_transkrip_lebih_30_menit_bukan_sesi_hidup(lingkungan):
    ws, proyek = lingkungan
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [end_turn(ws, -1900)], _epoch(-1900))
    assert kumpulkan(ws, proyek)["sesi"] == []


def test_session_end_kit_memulangkan_sesi_kecuali_dilanjutkan(lingkungan):
    ws, proyek = lingkungan
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [end_turn(ws, -60)], _epoch(-60))
    kit = ws / ".task-plans" / "sesi" / "sesi-a.json"
    selesai_ps = (SEKARANG + timedelta(seconds=-30)).strftime("%Y-%m-%dT%H:%M:%S") + ".1234567Z"  # bentuk ToString('o') PowerShell
    kit.write_text(json.dumps({"session_id": "sesi-a", "status": "selesai", "selesai": selesai_ps, "tahap": "wrap"}), encoding="utf-8")
    assert kumpulkan(ws, proyek)["sesi"] == []
    # SessionEnd yang LEBIH LAMA dari kejadian terakhir = sesi dilanjutkan (--resume): tetap hidup.
    # Berkas ditulis ber-BOM karena PowerShell di sebagian mesin menulisnya begitu.
    kit.write_text(json.dumps({"session_id": "sesi-a", "status": "selesai", "selesai": _ts(-120), "tahap": "wrap"}), encoding="utf-8-sig")
    sesi = kumpulkan(ws, proyek)["sesi"]
    assert [(s["id"], s["tahap"]) for s in sesi] == [("sesi-a", "wrap")]


def test_judul_dari_ai_title_lalu_task_kit(lingkungan):
    ws, proyek = lingkungan
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [end_turn(ws, -60)], _epoch(-60))
    (ws / ".task-plans" / "sesi" / "sesi-a.json").write_text(json.dumps({"session_id": "sesi-a", "status": "aktif", "task": "Tugas dari kit"}), encoding="utf-8")
    assert kumpulkan(ws, proyek)["sesi"][0]["judul"] == "Tugas dari kit"
    judul = baris("ai-title", ws)
    judul["aiTitle"] = "Judul dari Claude Code"
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [judul, end_turn(ws, -60)], _epoch(-60))
    assert kumpulkan(ws, proyek)["sesi"][0]["judul"] == "Judul dari Claude Code"


def test_cwd_di_luar_workspace_dilewati_dan_dihitung(lingkungan, tmp_path):
    ws, proyek = lingkungan
    lain = tmp_path / "proyek-lain"
    lain.mkdir()
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [end_turn(lain, -60)], _epoch(-60))
    data = kumpulkan(ws, proyek)
    assert data["sesi"] == []
    assert data["skema"]["dilewati_luar_workspace"] == 1


def test_baris_rusak_lebih_separuh_membuat_format_tidak_dikenali(lingkungan):
    ws, proyek = lingkungan
    f = proyek / "slug-uji" / "sesi-a.jsonl"
    f.write_text(json.dumps(end_turn(ws, -60)) + "\n" + "{rusak\n" * 3, encoding="utf-8")
    e = _epoch(-5)
    os.utime(f, (e, e))
    assert kumpulkan(ws, proyek)["skema"]["dikenali"] is False


def test_transkrip_panjang_tanpa_percakapan_membuat_format_tidak_dikenali(lingkungan):
    ws, proyek = lingkungan
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [baris("attachment", ws, -30)] * 25, _epoch(-5))
    assert kumpulkan(ws, proyek)["skema"]["dikenali"] is False


def test_transkrip_baru_yang_pendek_tanpa_percakapan_tetap_dikenali(lingkungan):
    ws, proyek = lingkungan
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [baris("attachment", ws, -30)] * 3, _epoch(-5))
    assert kumpulkan(ws, proyek)["skema"]["dikenali"] is True


def test_satu_hasil_tool_raksasa_membuat_ekor_diperluas(lingkungan):
    ws, proyek = lingkungan
    besar = tool_result(ws, "toolu_a", -20)
    besar["message"]["content"][0]["content"] = "z" * (300 * 1024)
    f = tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [prompt(ws, -60), tool_use(ws, "Read", "toolu_a", None, -30), besar], _epoch(-5))
    kejadian, diurai, rusak = ka.baca_ekor(str(f))
    assert rusak == 0 and diurai >= 2 and any(o.get("type") == "user" for o in kejadian)
    data = kumpulkan(ws, proyek)
    assert data["skema"]["dikenali"] is True
    assert (data["sesi"][0]["area"], data["sesi"][0]["keadaan"]) == ("meja", "berpikir")


def test_cache_tidak_basi_setelah_transkrip_bertambah(lingkungan):
    ws, proyek = lingkungan
    f = tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [tool_use(ws, "PowerShell", "toolu_a", None, -30)], _epoch(-30))
    assert kumpulkan(ws, proyek)["sesi"][0]["area"] == "server"
    with f.open("a", encoding="utf-8") as h:
        h.write(json.dumps(tool_result(ws, "toolu_a", -5)) + "\n")
    e = _epoch(-5)
    os.utime(f, (e, e))
    s = kumpulkan(ws, proyek)["sesi"][0]
    assert (s["area"], s["keadaan"]) == ("meja", "berpikir")


def test_judul_bertahan_walau_ai_title_keluar_dari_ekor(lingkungan):
    ws, proyek = lingkungan
    judul = baris("ai-title", ws)
    judul["aiTitle"] = "Judul lama"
    f = tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [judul, end_turn(ws, -60)], _epoch(-60))
    assert kumpulkan(ws, proyek)["sesi"][0]["judul"] == "Judul lama"
    panjang = end_turn(ws, -5)
    panjang["message"]["content"][0]["text"] = "y" * 3000
    with f.open("a", encoding="utf-8") as h:
        for _ in range(40):  # lebih dari 64 KB baris baru tanpa ai-title
            h.write(json.dumps(panjang) + "\n")
    e = _epoch(-5)
    os.utime(f, (e, e))
    assert kumpulkan(ws, proyek)["sesi"][0]["judul"] == "Judul lama"


# ---------- keluaran ----------

def test_render_js_dapat_diurai_kembali():
    data = {"versi": 1, "sesi": [{"judul": "a </script> b \u2028 c"}]}
    teks = ka.render_js(data)
    awalan = "window.__KANTOR__ = "
    assert teks.startswith(awalan) and teks.rstrip().endswith(";")
    assert json.loads(teks[len(awalan):].rstrip().rstrip(";")) == data


def test_tulis_atomik_tanpa_sisa_berkas_sementara(tmp_path):
    tujuan = tmp_path / "data.js"
    ka.tulis_atomik(str(tujuan), "a")
    ka.tulis_atomik(str(tujuan), "b")
    assert tujuan.read_text(encoding="utf-8") == "b"
    assert [p.name for p in tmp_path.iterdir()] == ["data.js"]


def test_tulis_atomik_gagal_ganti_nama_tidak_meninggalkan_berkas_sementara(tmp_path, monkeypatch):
    # antivirus/pengindeks mengunci tujuan: tiap tick yang gagal tak boleh menumpuk .tmp di .task-plans
    def dikunci(sumber, tujuan):
        raise PermissionError("dikunci pengindeks")

    monkeypatch.setattr(ka.os, "replace", dikunci)
    with pytest.raises(PermissionError):
        ka.tulis_atomik(str(tmp_path / "data.js"), "a")
    assert list(tmp_path.iterdir()) == []


def test_sekali_menulis_data_js(lingkungan):
    ws, proyek = lingkungan
    kini = datetime.now(timezone.utc)
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [tool_use(ws, "Edit", "toolu_a", {"file_path": "a/b.py"}, -2, dasar=kini)], time.time())
    assert ka.main(["--workspace", str(ws), "--proyek-dir", str(proyek), "--sekali",
                    "--registri-dir", str(ws / "tanpa-registri")]) == 0
    data = baca_data(ws)
    assert data["versi"] == 1
    assert [(s["id"], s["area"], s["alat"], s["detail"]) for s in data["sesi"]] == [("sesi-a", "meja", "Edit", "b.py")]
    assert data["penulis"]["berhenti"] is None
    assert not (ws / ".task-plans" / "kantor-agent.pid").exists()


def test_loop_berhenti_saat_sepi_dan_menandainya(lingkungan):
    ws, proyek = lingkungan
    log = ws / "penulis.log"
    assert ka.main(["--workspace", str(ws), "--proyek-dir", str(proyek), "--loop", "0.01", "--sepi-menit", "0.001",
                    "--log", str(log), "--registri-dir", str(ws / "tanpa-registri"), "--cek-silang-detik", "0"]) == 0
    data = baca_data(ws)
    assert data["penulis"]["berhenti"] == "sepi"
    assert "tak ada sesi hidup" in log.read_text(encoding="utf-8")
    assert not (ws / ".task-plans" / "kantor-agent.pid").exists()


def test_loop_keluar_3_setelah_lima_kali_berturut_gagal_menulis(lingkungan, monkeypatch):
    ws, proyek = lingkungan
    panggilan = []

    def gagal(path, teks):
        panggilan.append(path)
        raise PermissionError("dikunci pengindeks")

    monkeypatch.setattr(ka, "tulis_atomik", gagal)
    assert ka.main(["--workspace", str(ws), "--proyek-dir", str(proyek), "--loop", "0.01", "--sepi-menit", "10",
                    "--registri-dir", str(ws / "tanpa-registri"), "--cek-silang-detik", "0"]) == 3
    assert len(panggilan) == 5


# ---------- v2: registri sesi ~/.claude/sessions/<pid>.json ----------
# Bentuk berkas diamati 2026-09-15 (Claude Code 2.1.269, 6 sesi hidup): kunci di bawah, berkas sesi yang
# ditutup terhapus, dan procStart = FILETIME GetProcessTimes proses itu (6 dari 6 cocok).

def _ms(detik, dasar=SEKARANG):
    return int((dasar + timedelta(seconds=detik)).timestamp() * 1000)


def tulis_registri(folder, pid, sid, cwd, status="busy", diperbarui=-30, **ekstra):
    folder.mkdir(parents=True, exist_ok=True)
    isi = {"pid": pid, "sessionId": sid, "cwd": str(cwd), "kind": "interactive", "entrypoint": "claude-vscode",
           "name": "erp-8f", "status": status, "statusUpdatedAt": _ms(diperbarui), "updatedAt": _ms(diperbarui),
           "startedAt": _ms(-7200), "procStart": "134339285124572081", "version": "2.1.269",
           "messagingSocketPath": "x", "peerFeatures": "notify_idle", "peerProtocol": 1, "pidDomain": "win32:x"}
    isi.update(ekstra)
    p = folder / ("%d.json" % pid)
    p.write_text(json.dumps(isi), encoding="utf-8")
    return p


def selalu_hidup(pid, proc_start):
    return True


@pytest.fixture
def lingkungan2(lingkungan, tmp_path):
    ws, proyek = lingkungan
    return ws, proyek, tmp_path / "sessions"


def kumpulkan2(ws, proyek, reg, hidup=selalu_hidup):
    return ka.kumpulkan(str(proyek), str(ws), SEKARANG, registri_dir=str(reg), hidup=hidup)


def test_registri_berkas_sah_dibaca_kunci_tak_dikenal_diabaikan(tmp_path):
    reg = tmp_path / "sessions"
    tulis_registri(reg, 101, "sesi-a", tmp_path / "ws", status="idle", diperbarui=-90, kunciBaru={"x": 1})
    sesi, info = ka.baca_registri(str(reg), str(tmp_path / "ws"), selalu_hidup)
    assert (info["terbaca"], info["berkas"], info["rusak"], info["luar"]) == (True, 1, 0, 0)
    e = sesi["sesi-a"]
    assert (e["pid"], e["status"], e["asal"], e["nama"]) == (101, "idle", "claude-vscode", "erp-8f")
    assert e["status_sejak"] == SEKARANG + timedelta(seconds=-90)


def test_registri_json_rusak_dan_tanpa_kunci_wajib_dihitung_rusak(tmp_path):
    reg = tmp_path / "sessions"
    reg.mkdir()
    (reg / "1.json").write_text("{rusak", encoding="utf-8")
    (reg / "2.json").write_text(json.dumps({"pid": 2, "cwd": str(tmp_path)}), encoding="utf-8")  # tanpa sessionId
    sesi, info = ka.baca_registri(str(reg), str(tmp_path), selalu_hidup)
    assert sesi == {} and (info["terbaca"], info["berkas"], info["rusak"]) == (True, 2, 2)


def test_registri_pid_mati_atau_didaur_ulang_dilewati_dan_procstart_diteruskan(tmp_path):
    ws, reg = tmp_path / "ws", tmp_path / "sessions"
    tulis_registri(reg, 101, "hidup", ws)
    tulis_registri(reg, 202, "mati", ws)
    diperiksa = []

    def hidup(pid, proc_start):
        diperiksa.append((pid, proc_start))
        return pid == 101

    sesi, _ = ka.baca_registri(str(reg), str(ws), hidup)
    assert list(sesi) == ["hidup"]
    assert (202, "134339285124572081") in diperiksa


def test_registri_cwd_di_luar_workspace_dilewati_dan_dihitung(tmp_path):
    reg = tmp_path / "sessions"
    tulis_registri(reg, 101, "luar", tmp_path / "lain")
    sesi, info = ka.baca_registri(str(reg), str(tmp_path / "ws"), selalu_hidup)
    assert sesi == {} and (info["rusak"], info["luar"]) == (0, 1)


def test_registri_folder_tak_ada_tidak_terbaca(tmp_path):
    sesi, info = ka.baca_registri(str(tmp_path / "tidak-ada"), str(tmp_path), selalu_hidup)
    assert sesi == {} and info["terbaca"] is False


@pytest.mark.skipif(os.name != "nt", reason="pemeriksa hidup lewat ctypes hanya di Windows")
def test_proses_hidup_windows_tanpa_os_kill_dan_mencocokkan_procstart(monkeypatch):
    def jangan(*a, **k):
        raise AssertionError("os.kill di Windows = TerminateProcess: membunuh sesi yang diperiksa")

    monkeypatch.setattr(ka.os, "kill", jangan)
    sendiri = os.getpid()
    mulai = ka.waktu_buat_proses(sendiri)
    assert isinstance(mulai, int) and mulai > 0
    assert ka.proses_hidup(sendiri, str(mulai)) is True
    assert ka.proses_hidup(sendiri, str(mulai + 1)) is False  # PID sama, proses lain: didaur ulang
    assert ka.proses_hidup(sendiri, None) is True
    anak = subprocess.Popen([sys.executable, "-c", "pass"])
    anak.wait()
    assert ka.proses_hidup(anak.pid, None) is False


def test_sesi_registri_diam_lama_tetap_tampil_walau_transkrip_tua(lingkungan2):
    ws, proyek, reg = lingkungan2
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [prompt(ws, -30060), end_turn(ws, -30000)], _epoch(-30000))
    tulis_registri(reg, 101, "sesi-a", ws, status="idle", diperbarui=-30000)
    data = kumpulkan2(ws, proyek, reg)
    s = data["sesi"][0]
    assert (s["id"], s["area"], s["keadaan"], s["diam_detik"]) == ("sesi-a", "lounge", "menunggu_anda", 30000)
    assert (s["asal"], s["nama"], s["pid"], s["status_proses"]) == ("claude-vscode", "erp-8f", 101, "idle")
    assert data["skema"]["sumber_hidup"] == "registri"


def test_transkrip_hidup_tanpa_entri_registri_sudah_pulang(lingkungan2):
    ws, proyek, reg = lingkungan2
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [tool_use(ws, "Read", "toolu_a", None, -5)], _epoch(-5))
    tulis_registri(reg, 101, "sesi-lain", ws, status="idle")
    assert [s["id"] for s in kumpulkan2(ws, proyek, reg)["sesi"]] == ["sesi-lain"]


def test_sesi_registri_tanpa_transkrip_tampil_dari_status_proses(lingkungan2):
    ws, proyek, reg = lingkungan2
    tulis_registri(reg, 101, "baru-busy", ws, status="busy", diperbarui=-3)
    tulis_registri(reg, 102, "baru-idle", ws, status="idle", diperbarui=-40)
    sesi = {s["id"]: s for s in kumpulkan2(ws, proyek, reg)["sesi"]}
    assert (sesi["baru-busy"]["area"], sesi["baru-busy"]["keadaan"]) == ("meja", "berpikir")
    assert (sesi["baru-idle"]["area"], sesi["baru-idle"]["keadaan"], sesi["baru-idle"]["diam_detik"]) == (
        "lounge", "menunggu_anda", 40)


def test_registri_busy_sesudah_end_turn_berarti_berpikir(lingkungan2):
    # prompt baru sudah dikirim tetapi barisnya belum tertulis: registri lebih dulu tahu
    ws, proyek, reg = lingkungan2
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [end_turn(ws, -60)], _epoch(-60))
    tulis_registri(reg, 101, "sesi-a", ws, status="busy", diperbarui=-2)
    s = kumpulkan2(ws, proyek, reg)["sesi"][0]
    assert (s["area"], s["keadaan"]) == ("meja", "berpikir")


def test_registri_idle_tanpa_end_turn_berarti_menunggu_anda(lingkungan2):
    # giliran dihentikan (Esc) tanpa end_turn: mode transkrip terbaca berpikir selamanya
    ws, proyek, reg = lingkungan2
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [prompt(ws, -60), baris("assistant_thinking", ws, -50)], _epoch(-50))
    tulis_registri(reg, 101, "sesi-a", ws, status="idle", diperbarui=-45)
    s = kumpulkan2(ws, proyek, reg)["sesi"][0]
    assert (s["area"], s["keadaan"]) == ("lounge", "menunggu_anda")


def test_tool_tertunda_tetap_menentukan_area_saat_registri_busy(lingkungan2):
    ws, proyek, reg = lingkungan2
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [tool_use(ws, "PowerShell", "toolu_a", {"description": "uji"}, -12)], _epoch(-12))
    tulis_registri(reg, 101, "sesi-a", ws, status="busy")
    s = kumpulkan2(ws, proyek, reg)["sesi"][0]
    assert (s["area"], s["keadaan"], s["alat"]) == ("server", "alat", "PowerShell")


def hasil_latar(ws, tool_id, task_id, detik):
    # bentuk nyata: toolUseResult.backgroundTaskId + teks "Command running in background with ID: ..."
    o = tool_result(ws, tool_id, detik)
    o["message"]["content"][0]["content"] = "Command running in background with ID: %s. Output is being written to: x" % task_id
    o["toolUseResult"] = {"backgroundTaskId": task_id, "stdout": "", "stderr": "", "interrupted": False}
    return o


def notifikasi_latar(ws, task_id, detik, status="completed"):
    # bentuk nyata: queue-operation enqueue berisi <task-notification> dengan <task-id> dan <status>
    o = baris("queue-operation", ws, detik)
    o["operation"] = "enqueue"
    o["content"] = ("<task-notification>\n<task-id>%s</task-id>\n<tool-use-id>toolu_x</tool-use-id>\n"
                    "<status>%s</status>\n<summary>x</summary>\n</task-notification>" % (task_id, status))
    return o


def test_urai_melacak_tugas_latar_sampai_notifikasinya():
    mulai = [tool_use(WS, "PowerShell", "toolu_a", {"description": "uji panjang", "run_in_background": True}, -60),
             hasil_latar(WS, "toolu_a", "b1", -59), end_turn(WS, -50)]
    u = ka.urai(mulai)
    assert list(u["latar"]) == ["b1"] and u["latar"]["b1"][0] == "PowerShell"
    assert dict(ka.urai(mulai + [notifikasi_latar(WS, "b1", -10)])["latar"]) == {}


def test_registri_idle_dengan_tugas_latar_menunggu_di_ruang_server(lingkungan2):
    ws, proyek, reg = lingkungan2
    kejadian = [tool_use(ws, "PowerShell", "toolu_a", {"description": "uji panjang", "run_in_background": True}, -60),
                hasil_latar(ws, "toolu_a", "b1", -59), end_turn(ws, -50)]
    f = tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", kejadian, _epoch(-50))
    tulis_registri(reg, 101, "sesi-a", ws, status="idle", diperbarui=-50)
    s = kumpulkan2(ws, proyek, reg)["sesi"][0]
    assert (s["area"], s["keadaan"], s["alat"], s["detail"]) == ("server", "menunggu_latar", "PowerShell", "uji panjang")
    tulis_jsonl(f, kejadian + [notifikasi_latar(ws, "b1", -5)], _epoch(-5))
    s = kumpulkan2(ws, proyek, reg)["sesi"][0]
    assert (s["area"], s["keadaan"]) == ("lounge", "menunggu_anda")


def test_registri_idle_dengan_subagent_hidup_menunggu_di_rapat(lingkungan2):
    ws, proyek, reg = lingkungan2
    folder = proyek / "slug-uji"
    tulis_jsonl(folder / "sesi-a.jsonl", [end_turn(ws, -60)], _epoch(-60))
    tulis_jsonl(folder / "sesi-a" / "subagents" / "agent-x1.jsonl", [tool_use(ws, "Grep", "toolu_s", None, -5, subagent=True)], _epoch(-5))
    tulis_registri(reg, 101, "sesi-a", ws, status="idle", diperbarui=-60)
    s = kumpulkan2(ws, proyek, reg)["sesi"][0]
    assert (s["area"], s["keadaan"], len(s["subagent"])) == ("rapat", "menunggu_subagent", 1)


def test_registri_tak_terbaca_turun_ke_mode_transkrip(lingkungan2):
    ws, proyek, reg = lingkungan2  # folder registri sengaja tidak dibuat
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [tool_use(ws, "Edit", "toolu_a", None, -5)], _epoch(-5))
    data = kumpulkan2(ws, proyek, reg)
    assert [s["id"] for s in data["sesi"]] == ["sesi-a"]
    assert data["skema"]["sumber_hidup"] == "transkrip"


def test_tanpa_registri_dir_mode_transkrip(lingkungan):
    ws, proyek = lingkungan
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [end_turn(ws, -60)], _epoch(-60))
    assert kumpulkan(ws, proyek)["skema"]["sumber_hidup"] == "transkrip"


# ---------- v2: cek silang `claude agents --json` ----------

def _cek_sampai_selesai(cek, sid_registri, batas=20):
    t0 = time.monotonic()
    cek.tick(sid_registri)
    while time.monotonic() - t0 < batas:
        if not cek.berjalan():
            return cek.status()
        time.sleep(0.05)
        cek.tick(sid_registri)
    raise AssertionError("cek silang tak selesai dalam %s detik" % batas)


def _perintah_cetak(daftar):
    return [sys.executable, "-c", "import json, sys; sys.stdout.write(json.dumps(%r))" % (daftar,)]


def test_cek_silang_cocok_dengan_registri_workspace(tmp_path):
    ws = str(tmp_path / "ws")
    agents = [{"pid": 1, "cwd": ws, "kind": "interactive", "sessionId": "sesi-a", "status": "busy"},
              {"pid": 2, "cwd": str(tmp_path / "lain"), "kind": "interactive", "sessionId": "luar", "status": "idle"}]
    cek = ka.CekSilang(_perintah_cetak(agents), ws, interval_detik=0, batas_detik=20)
    st = _cek_sampai_selesai(cek, {"sesi-a"})
    assert (st["dicek"], st["cocok"]) == (True, True)


def test_cek_silang_tak_cocok_baru_ditandai_setelah_dua_kali_berturut(tmp_path):
    ws = str(tmp_path / "ws")
    agents = [{"pid": 1, "cwd": ws, "sessionId": "sesi-a"}, {"pid": 2, "cwd": ws, "sessionId": "sesi-b"}]
    cek = ka.CekSilang(_perintah_cetak(agents), ws, interval_detik=0, batas_detik=20)
    assert _cek_sampai_selesai(cek, {"sesi-a"})["cocok"] is True  # sekali tak cocok bisa sekadar jeda waktu
    assert _cek_sampai_selesai(cek, {"sesi-a"})["cocok"] is False
    assert _cek_sampai_selesai(cek, {"sesi-a", "sesi-b"})["cocok"] is True


def test_cek_silang_menggantung_dihentikan_dan_tick_tidak_menunggu(tmp_path):
    cek = ka.CekSilang([sys.executable, "-c", "import time; time.sleep(60)"], str(tmp_path), interval_detik=0, batas_detik=1)
    t0 = time.monotonic()
    cek.tick(set())
    assert time.monotonic() - t0 < 5  # memulai subprocess tidak menunggu hasilnya (anaknya tidur 60 detik)
    st = _cek_sampai_selesai(cek, set())
    assert st["dicek"] is False and "batas" in st["catatan"]


def test_cek_silang_perintah_tak_ada(tmp_path):
    cek = ka.CekSilang([str(tmp_path / "tidak-ada.exe"), "agents", "--json"], str(tmp_path), interval_detik=0)
    cek.tick(set())
    st = cek.status()
    assert st["dicek"] is False and st["catatan"] and cek.berjalan() is False


def test_cek_silang_keluaran_bukan_json_tidak_dianggap_cocok(tmp_path):
    cek = ka.CekSilang([sys.executable, "-c", "print('bukan json')"], str(tmp_path), interval_detik=0, batas_detik=20)
    st = _cek_sampai_selesai(cek, set())
    assert st["dicek"] is False and st["cocok"] is None


# ---------- v2: satu penulis per workspace ----------

def test_kunci_penulis_eksklusif_dan_lepas_setelah_ditutup(tmp_path):
    path = str(tmp_path / "kantor-agent.lock")
    pertama = ka.kunci_penulis(path)
    assert pertama is not None
    assert ka.kunci_penulis(path) is None
    pertama.close()
    kedua = ka.kunci_penulis(path)
    assert kedua is not None
    kedua.close()


def test_loop_keluar_4_bila_penulis_lain_memegang_kunci(lingkungan):
    ws, proyek = lingkungan
    kunci = ka.kunci_penulis(str(ws / ".task-plans" / "kantor-agent.lock"))
    try:
        t0 = time.monotonic()
        # sepi sekejap: kode yang benar keluar 4 sebelum loop, mutan tanpa kunci keluar 0 cepat (bukan menggantung)
        assert ka.main(["--workspace", str(ws), "--proyek-dir", str(proyek), "--loop", "0.01", "--sepi-menit", "0.001",
                        "--registri-dir", str(ws / "tanpa-registri"), "--cek-silang-detik", "0"]) == 4
        assert time.monotonic() - t0 < 5
        assert not (ws / ".task-plans" / "kantor-agent-data.js").exists()
    finally:
        kunci.close()
