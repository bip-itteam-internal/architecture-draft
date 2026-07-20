#!/usr/bin/env python3
"""Entry point: bangun VAULT-INDEX.json.

    python Tools/build-vault-index.py            # incremental
    python Tools/build-vault-index.py --full     # regen semua
    python Tools/build-vault-index.py --check    # exit 1 bila basi
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vault_index.build import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
