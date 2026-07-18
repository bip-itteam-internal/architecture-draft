#!/usr/bin/env python3
"""Regenerate Index.md dari SDK upstream. Tidak menyentuh Endpoints/."""
import subprocess, sys
from pathlib import Path

setup = Path(__file__).resolve().parents[3] / "setup_shopee.py"
if not setup.exists():
    sys.exit(f"setup_shopee.py tidak ditemukan di {setup}")
sys.exit(subprocess.call([sys.executable, str(setup), "--refresh"],
                         cwd=str(setup.parent)))
