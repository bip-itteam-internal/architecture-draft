"""Klasifikasi path berkas vault menjadi (area, jenis, publik)."""

from pathlib import PurePosixPath

# folder tingkat-1 -> (jenis, publik)
KLASIFIKASI: dict[str, tuple[str, bool]] = {
    "Application": ("domain", True),
    "Core System and Modules": ("domain", True),
    "Finance System": ("domain", True),
    "General Affairs": ("domain", True),
    "Human Resource Information System": ("domain", True),
    "Manufacture": ("domain", True),
    "Quality & Regulatory": ("domain", True),
    "Sales": ("domain", True),
    "Third-party Software": ("domain", True),
    "Unknown or not listed": ("domain", True),
    "Warehouse": ("domain", True),
    "Decisions": ("adr", True),
    "Runbooks": ("runbook", True),
    "Reference": ("reference", True),
    "API Reference": ("api", True),
    # ter-index untuk agent, TERTUTUP untuk kanal manusia
    "IT": ("domain", False),
    "Workspace": ("workspace", False),
    "Logs": ("log", False),
    "Templates": ("template", False),
}

# dilewati seluruhnya: tidak ter-index untuk siapa pun
DILEWATI: frozenset[str] = frozenset({
    "Additional documents",  # aset Excalidraw
    "Tools",                 # tooling ini sendiri
})

# subpohon vendor cache yang di-generate skrip
PREFIX_DILEWATI: tuple[str, ...] = (
    "API Reference/Shopee Open API v2/",
)

# dok meta akar yang memang ada dan memang layak publik (persis, case-sensitive,
# dicocokkan ke basename tanpa ekstensi). Berkas akar lain -> fail-closed.
META_ROOT: frozenset[str] = frozenset({
    "README", "HOMEPAGE", "CLAUDE", "SCRUM SPECS", "ROADMAP", "DEVELOPER GUIDE",
})


def klasifikasi_path(rel_path: str) -> dict | None:
    """Klasifikasikan path relatif-vault.

    Kembalikan {"area", "jenis", "publik"}, atau None bila berkas
    harus dilewati seluruhnya.

    Folder yang tidak dikenal tetap ter-index untuk agent tapi
    SELALU publik=False (fail-closed).
    """
    p = PurePosixPath(rel_path.replace("\\", "/"))

    if p.suffix.lower() != ".md":
        return None

    posix = p.as_posix()
    if any(posix.startswith(prefix) for prefix in PREFIX_DILEWATI):
        return None

    if len(p.parts) == 1:
        if p.stem in META_ROOT:
            return {"area": "root", "jenis": "meta", "publik": True}
        # fail-closed: berkas akar baru yang tak dikenal tidak boleh otomatis publik
        return {"area": "root", "jenis": None, "publik": False}

    top = p.parts[0]
    if top in DILEWATI or top.startswith("."):
        return None

    if top in KLASIFIKASI:
        jenis, publik = KLASIFIKASI[top]
        return {"area": top, "jenis": jenis, "publik": publik}

    # fail-closed
    return {"area": top, "jenis": None, "publik": False}
