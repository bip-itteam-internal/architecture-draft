"""Orkestrasi: scan vault, diff incremental, rakit dan tulis VAULT-INDEX.json."""

import argparse
import json
from datetime import date
from pathlib import Path

from .parsing import ekstrak_status, ekstrak_wikilink, hitung_hash
from .paths import klasifikasi_path
from .summarize import MODEL, ambil_hasil, ringkas_stub, submit_batch

VERSI_SKEMA = 1
NAMA_INDEX = "VAULT-INDEX.json"


def scan_vault(root: Path) -> list[dict]:
    """Kumpulkan entri beserta seluruh field deterministik (tanpa ringkasan)."""
    entri: list[dict] = []
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root).as_posix()
        if any(bagian.startswith(".") for bagian in Path(rel).parts):
            continue
        klas = klasifikasi_path(rel)
        if klas is None:
            continue

        isi = p.read_text(encoding="utf-8")
        emoji, teks_status = ekstrak_status(isi)
        entri.append({
            "path": rel,
            "judul": p.stem,
            "area": klas["area"],
            "jenis": klas["jenis"],
            "status_emoji": emoji,
            "status_teks": teks_status,
            "publik": klas["publik"],
            "tautan": ekstrak_wikilink(isi),
            "hash": hitung_hash(isi),
            "ukuran_kb": round(p.stat().st_size / 1024, 1),
            "_isi": isi,
        })
    return entri


def muat_index(path: Path) -> dict | None:
    """Muat index lama. Hilang, rusak, atau beda versi skema -> None."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict) or data.get("versi_skema") != VERSI_SKEMA:
        return None
    return data


def pilih_yang_perlu_diringkas(
    entri: list[dict], lama: dict | None, full: bool = False
) -> list[dict]:
    """Pilih dokumen yang perlu panggilan LLM.

    Dipilih bila: --full, atau belum ada di index lama, atau hash berubah,
    atau ringkasan sebelumnya null (percobaan sebelumnya gagal).
    """
    if full or lama is None:
        return list(entri)

    sebelumnya = {d["path"]: d for d in lama.get("dokumen", [])}
    perlu = []
    for e in entri:
        d = sebelumnya.get(e["path"])
        if d is None or d.get("hash") != e["hash"] or d.get("ringkasan") is None:
            perlu.append(e)
    return perlu


def rakit_index(entri: list[dict]) -> dict:
    dokumen = []
    gagal = []
    for e in entri:
        d = {k: v for k, v in e.items() if not k.startswith("_")}
        if d.get("ringkasan") is None:
            gagal.append(d["path"])
        dokumen.append(d)
    return {
        "versi_skema": VERSI_SKEMA,
        "digenerate": date.today().isoformat(),
        "jumlah_dokumen": len(dokumen),
        "dokumen": dokumen,
        "gagal": gagal,
    }


def _peringatan_status(entri: list[dict]) -> list[str]:
    """Status absen normal untuk meta/api; janggal untuk domain/adr."""
    return [
        e["path"]
        for e in entri
        if e["jenis"] in ("domain", "adr")
        and e["status_emoji"] is None
        and e["status_teks"] is None
    ]


def _peringatan_folder_tak_dikenal(entri: list[dict]) -> list[str]:
    """Folder belum terdaftar di KLASIFIKASI: aman (publik=False) tapi harus terlihat.

    Kalau dibiarkan senyap, folder domain baru akan tertutup selamanya dari
    kanal manusia tanpa ada yang sadar.
    """
    return [e["path"] for e in entri if e["jenis"] is None]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bangun VAULT-INDEX.json")
    ap.add_argument("--full", action="store_true", help="regen semua, abaikan hash")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 bila index basi, tanpa menulis")
    ap.add_argument("--root", default=".", help="akar vault")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    path_index = root / NAMA_INDEX

    entri = scan_vault(root)
    lama = muat_index(path_index)
    perlu = pilih_yang_perlu_diringkas(entri, lama, full=args.full)

    if args.check:
        if perlu:
            print(f"BASI: {len(perlu)} dokumen belum terwakili di {NAMA_INDEX}")
            for e in perlu[:10]:
                print(f"  - {e['path']}")
            return 1
        print(f"SEGAR: {NAMA_INDEX} sinkron dengan {len(entri)} dokumen")
        return 0

    print(f"{len(entri)} dokumen di-scan, {len(perlu)} perlu diringkas")

    # bawa ringkasan lama untuk dokumen yang tidak berubah
    sebelumnya = {d["path"]: d for d in (lama or {}).get("dokumen", [])}
    for e in entri:
        d = sebelumnya.get(e["path"], {})
        e["ringkasan"] = d.get("ringkasan")
        e["kata_kunci"] = d.get("kata_kunci", [])

    # 🔴 Stub tidak perlu LLM
    perlu_llm = []
    for e in perlu:
        if e["status_emoji"] == "🔴":
            e.update(ringkas_stub(e["judul"]))
        else:
            perlu_llm.append(e)

    if perlu_llm:
        import anthropic
        client = anthropic.Anthropic()
        tugas = [
            {"custom_id": f"doc-{i}", "judul": e["judul"],
             "jenis": e["jenis"], "isi": e["_isi"]}
            for i, e in enumerate(perlu_llm)
        ]
        print(f"Submit batch {len(tugas)} dokumen ke {MODEL} ...")
        batch_id = submit_batch(client, tugas)
        print(f"Batch id: {batch_id}")
        hasil = ambil_hasil(client, batch_id)
        for i, e in enumerate(perlu_llm):
            r = hasil.get(f"doc-{i}")
            e["ringkasan"] = r["ringkasan"] if r else None
            e["kata_kunci"] = r["kata_kunci"] if r else []

    index = rakit_index(entri)
    path_index.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Ditulis: {path_index} ({index['jumlah_dokumen']} dokumen)")

    for p in _peringatan_status(entri):
        print(f"  PERINGATAN status hilang: {p}")
    for p in _peringatan_folder_tak_dikenal(entri):
        print(f"  PERINGATAN folder tak dikenal (publik=False): {p}")

    if index["gagal"]:
        print(f"\nGAGAL diringkas ({len(index['gagal'])}):")
        for p in index["gagal"]:
            print(f"  - {p}")
        return 1
    return 0
