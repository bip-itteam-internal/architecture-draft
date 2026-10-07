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


def test_adalah_angka():
    assert adalah_angka("80") and adalah_angka("1,5") and adalah_angka("12.5")
    assert not adalah_angka("target_profit") and not adalah_angka("/kpi")
