import pytest
from vault_index.paths import klasifikasi_path


@pytest.mark.parametrize("rel_path,area,jenis,publik", [
    ("Human Resource Information System/HRIS - Overtime.md",
     "Human Resource Information System", "domain", True),
    ("Decisions/ADR - 0006 Swap Jadwal Same-Department.md",
     "Decisions", "adr", True),
    ("Runbooks/RUN - Onboarding Developer Baru.md", "Runbooks", "runbook", True),
    ("Reference/REF - Glossary.md", "Reference", "reference", True),
    ("API Reference/API - Employee Service.md", "API Reference", "api", True),
    ("HOMEPAGE.md", "root", "meta", True),
    ("Sales/Sales - HPP Master (Plan).md", "Sales", "domain", True),
])
def test_folder_dikenal(rel_path, area, jenis, publik):
    hasil = klasifikasi_path(rel_path)
    assert hasil == {"area": area, "jenis": jenis, "publik": publik}


@pytest.mark.parametrize("rel_path,jenis", [
    ("IT/IT - Server, VMs and Databases.md", "domain"),
    ("Workspace/Inbox/2026-06-25.md", "workspace"),
    ("Workspace/Meetings/MTG - 2026-06-25 Contoh Notulen.md", "workspace"),
    ("Logs/LOG - Shopee API Rate Limit Request.md", "log"),
    ("Templates/Template - Daily Note.md", "template"),
])
def test_folder_tertutup_untuk_manusia(rel_path, jenis):
    """Ter-index untuk agent, tapi publik=False."""
    hasil = klasifikasi_path(rel_path)
    assert hasil is not None
    assert hasil["jenis"] == jenis
    assert hasil["publik"] is False


@pytest.mark.parametrize("rel_path", [
    "API Reference/Shopee Open API v2/Index.md",
    "API Reference/Shopee Open API v2/order.get_order_list.md",
    "API Reference/Shopee Open API v2/Tools/refresh.py",
    "Additional documents/Excalidraw/Recruitment Pipeline.excalidraw.md",
    "Tools/build-vault-index.py",
    "gambar.png",
])
def test_dilewati_seluruhnya(rel_path):
    assert klasifikasi_path(rel_path) is None


def test_folder_tak_dikenal_default_tertutup():
    """FAIL-CLOSED: folder baru yang belum diklasifikasi tidak boleh bocor ke publik."""
    hasil = klasifikasi_path("Folder Baru Yang Belum Ada/Sesuatu.md")
    assert hasil is not None, "dokumen tetap ter-index untuk agent"
    assert hasil["publik"] is False, "tapi WAJIB tertutup untuk kanal manusia"
    assert hasil["jenis"] is None
