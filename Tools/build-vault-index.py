#!/usr/bin/env python3
"""Entry point: bangun VAULT-INDEX.json.

Ringkasan dokumen dibuat Claude Code sendiri (bukan panggilan API dari
skrip ini), lewat alur tiga langkah. Dijalankan dari `erp/` (folder induk
yang jadi cwd Claude Code), jadi `--root architecture-draft` wajib:

    1. python architecture-draft/Tools/build-vault-index.py --daftar-tugas --root architecture-draft
       -> tulis VAULT-INDEX.tugas.json (dokumen yang perlu diringkas)
    2. Claude Code membaca berkas itu, menulis VAULT-INDEX.hasil.json
    3. python architecture-draft/Tools/build-vault-index.py --serap --root architecture-draft
       -> baca hasil, tulis VAULT-INDEX.json

Mode lain:

    python architecture-draft/Tools/build-vault-index.py --root architecture-draft
        Tanpa flag: rakit ulang manifest hanya dari ringkasan yang SUDAH ada
        (carry-forward via hash + stub lokal). TIDAK PERNAH menghasilkan
        ringkasan baru -- dokumen yang belum diringkas tetap null dan
        exit 1. Bukan mode "incremental" dalam arti auto-generate.

    python architecture-draft/Tools/build-vault-index.py --full --root architecture-draft
        Sama seperti di atas, tapi abaikan carry-forward (paksa semua
        dokumen dianggap perlu ringkasan baru saat dipakai bersama
        --daftar-tugas).

    python architecture-draft/Tools/build-vault-index.py --check --root architecture-draft
        Exit 1 bila VAULT-INDEX.json basi (ada dokumen baru/berubah belum
        terwakili). Tidak menulis apa pun -- aman dijalankan di vault nyata,
        cocok untuk CI/pre-commit.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vault_index.build import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
