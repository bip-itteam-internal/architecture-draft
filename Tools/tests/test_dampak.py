"""Test dampak.py. Spec: .agent-kit/docs/2026-10-07-dampak-command-design.md"""
import json
import os
import subprocess
from pathlib import Path

import pytest

import dampak
from dampak import adalah_angka, ekstrak_fakta


def test_ekstrak_empat_bentuk_fakta():
    fakta, dilewati = ekstrak_fakta(
        "ambang `target_profit` dari 80 jadi 75 di /kpi/template, batas 5 hari, field ads_cost"
    )
    assert set(fakta) == {"target_profit", "/kpi/template", "80", "75", "ads_cost"}
    assert {"jenis": "fakta", "nilai": "5", "alasan": "angka satu digit"} in dilewati


def test_ekstrak_url_bukan_rute():
    fakta, _ = ekstrak_fakta("lihat https://github.com/org/repo")
    assert not any(f.startswith("/") for f in fakta)


def test_ekstrak_tanpa_fakta():
    assert ekstrak_fakta("ubah kalimat pembuka saja") == ([], [])


def test_ekstrak_unik_dan_tanpa_tanda_baca_ekor():
    fakta, _ = ekstrak_fakta("80, lalu 80. Rute /a/b.")
    assert fakta == ["/a/b", "80"]


from vault_index.build import scan_vault  # noqa: E402

ADR = "Decisions/ADR - 0079 Target Profit.md"
INSENTIF = "Finance System/Finance - Insentif.md"
KPI = "Human Resource Information System/HRIS - KPI.md"
CUTI = "Human Resource Information System/HRIS - Cuti.md"
ANALISA = "Workspace/ANALISA - Target.md"
RUN = "Runbooks/RUN - Lain.md"


@pytest.fixture
def vault_mini(tmp_path: Path) -> Path:
    v = tmp_path / "architecture-draft"
    isi = {
        ADR: "- **Status**: ✅ Diterima\n\nAmbang `target_profit` 80. Lihat [[Finance - Insentif]].\n",
        INSENTIF: "- **Status**: ✅ Implemented\n\nTarget 80 dari [[ADR - 0079 Target Profit]]. "
                  "Lihat [[HRIS - KPI]].\n",
        KPI: "- **Status**: ⚠️ Implemented\n\nAmbang KPI 80. [[Finance - Insentif]]\n",
        CUTI: "- **Status**: ✅ Implemented\n\nTidak terkait, port 8080, batas 800, rasio 80.5.\n",
        ANALISA: "[[ADR - 0079 Target Profit]] 80\n",
        RUN: "> **Status**: ✅\n\n[[HRIS - KPI]]\n",
    }
    for rel, teks in isi.items():
        p = v / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(teks, encoding="utf-8")
    return v


def test_graf_adr_dua_lompatan(vault_mini):
    hasil = dampak.kandidat_graf([ADR], scan_vault(vault_mini))
    assert set(hasil[INSENTIF]) == {"tautan", "backlink"}
    assert "adr-2hop" in hasil[KPI]
    assert ANALISA not in hasil          # Workspace tak pernah kandidat
    assert ADR not in hasil              # sumber bukan kandidat
    assert RUN not in hasil              # tiga lompatan


def test_graf_non_adr_satu_lompatan(vault_mini):
    hasil = dampak.kandidat_graf([INSENTIF], scan_vault(vault_mini))
    assert set(hasil) == {ADR, KPI}
    assert RUN not in hasil


def test_graf_dok_yatim(vault_mini):
    assert dampak.kandidat_graf([CUTI], scan_vault(vault_mini)) == {}


def test_fakta_vault_angka_utuh(vault_mini):
    alasan, dilewati = dampak.kandidat_fakta_vault(["80"], scan_vault(vault_mini), [ADR])
    assert set(alasan) == {INSENTIF, KPI}       # CUTI punya 8080/800/80.5: bukan 80
    assert alasan[KPI] == ["fakta:80"]
    assert dilewati == []


def test_fakta_vault_terlalu_umum(vault_mini, monkeypatch):
    monkeypatch.setattr(dampak, "AMBANG_TERLALU_UMUM", 1)
    alasan, dilewati = dampak.kandidat_fakta_vault(["80"], scan_vault(vault_mini), [ADR])
    assert alasan == {}
    assert dilewati[0]["nilai"] == "80" and dilewati[0]["alasan"].startswith("terlalu umum")


def _git_uji(repo: Path, *args: str) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    r = subprocess.run(["git", "-C", str(repo), "-c", "user.name=uji", "-c", "user.email=uji@example.invalid",
                        "-c", "core.autocrlf=false", *args], capture_output=True, env=env)
    assert r.returncode == 0, f"git {args} gagal: {r.stderr.decode(errors='replace')}{r.stdout.decode(errors='replace')}"


@pytest.fixture
def repos(tmp_path: Path) -> Path:
    """Akar berisi bip-erp saja; origin/main = commit pertama."""
    akar = tmp_path / "repos"
    be = akar / "bip-erp"
    be.mkdir(parents=True)
    _git_uji(be, "init", "-q")
    (be / "a.go").write_text("x := target_profit\nambang := 80\n", encoding="utf-8")
    (be / "biner.go").write_bytes(b"\x00\x01\nvar y = target_profit\n")
    (be / "port.go").write_text("port := 8080\n", encoding="utf-8")
    (be / "wt.go").write_text("kosong\n", encoding="utf-8")
    _git_uji(be, "add", "-A")
    _git_uji(be, "commit", "-q", "-m", "awal")
    _git_uji(be, "update-ref", "refs/remotes/origin/main", "HEAD")
    # perubahan yang hanya ada di working tree: TIDAK boleh terbaca
    (be / "wt.go").write_text("z := target_profit\n", encoding="utf-8")
    return akar


def test_kode_membaca_ref_bukan_working_tree(repos):
    kandidat, _ = dampak.cari_kode(["target_profit"], repos)
    berkas = {k["berkas"] for k in kandidat}
    assert "wt.go" not in berkas
    assert berkas == {"a.go", "biner.go"}
    assert all(k["ref"] == "origin/main" and k["repo"] == "bip-erp" for k in kandidat)


def test_kode_berkas_nul_tetap_ditemukan(repos):
    kandidat, _ = dampak.cari_kode(["target_profit"], repos)
    biner = [k for k in kandidat if k["berkas"] == "biner.go"]
    assert biner and biner[0]["baris"] == 2


def test_kode_angka_utuh(repos):
    kandidat, _ = dampak.cari_kode(["80"], repos)
    assert {k["berkas"] for k in kandidat} == {"a.go"}


def test_kode_repo_atau_ref_tak_ada(repos):
    _, dilewati = dampak.cari_kode(["target_profit"], repos)
    nilai = {d["nilai"]: d["alasan"] for d in dilewati if d["jenis"] == "repo"}
    assert set(nilai) == {"erp-frontend", "mybharata-app"}
    _, dilewati2 = dampak.cari_kode(["target_profit"], repos, (("bip-erp", "origin/dev"),))
    assert dilewati2 == [{"jenis": "repo", "nilai": "bip-erp", "alasan": "ref origin/dev tidak ada"}]


def test_kode_terlalu_umum(repos, monkeypatch):
    monkeypatch.setattr(dampak, "AMBANG_TERLALU_UMUM", 1)
    kandidat, dilewati = dampak.cari_kode(["target_profit"], repos)
    assert kandidat == []
    assert any(d["nilai"] == "target_profit" and d["alasan"].startswith("terlalu umum") for d in dilewati)


def test_adalah_angka():
    assert adalah_angka("80") and adalah_angka("1,5") and adalah_angka("12.5")
    assert not adalah_angka("target_profit") and not adalah_angka("/kpi")
