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


def test_adalah_angka():
    assert adalah_angka("80") and adalah_angka("1,5") and adalah_angka("12.5")
    assert not adalah_angka("target_profit") and not adalah_angka("/kpi")
