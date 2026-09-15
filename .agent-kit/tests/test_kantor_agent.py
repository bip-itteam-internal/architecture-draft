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


def test_sekali_menulis_data_js(lingkungan):
    ws, proyek = lingkungan
    kini = datetime.now(timezone.utc)
    tulis_jsonl(proyek / "slug-uji" / "sesi-a.jsonl", [tool_use(ws, "Edit", "toolu_a", {"file_path": "a/b.py"}, -2, dasar=kini)], time.time())
    assert ka.main(["--workspace", str(ws), "--proyek-dir", str(proyek), "--sekali"]) == 0
    data = baca_data(ws)
    assert data["versi"] == 1
    assert [(s["id"], s["area"], s["alat"], s["detail"]) for s in data["sesi"]] == [("sesi-a", "meja", "Edit", "b.py")]
    assert data["penulis"]["berhenti"] is None
    assert not (ws / ".task-plans" / "kantor-agent.pid").exists()


def test_loop_berhenti_saat_sepi_dan_menandainya(lingkungan):
    ws, proyek = lingkungan
    log = ws / "penulis.log"
    assert ka.main(["--workspace", str(ws), "--proyek-dir", str(proyek), "--loop", "0.01", "--sepi-menit", "0.001",
                    "--log", str(log)]) == 0
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
    assert ka.main(["--workspace", str(ws), "--proyek-dir", str(proyek), "--loop", "0.01", "--sepi-menit", "10"]) == 3
    assert len(panggilan) == 5
