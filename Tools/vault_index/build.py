"""Orkestrasi: scan vault, diff incremental, rakit dan tulis VAULT-INDEX.json.

Ringkasan LLM dibuat oleh Claude Code sendiri, lewat tiga langkah CLI (bukan
panggilan API dari modul ini -- modul ini tidak pernah menyentuh jaringan):

    1. --daftar-tugas   tulis VAULT-INDEX.tugas.json (dokumen yang perlu diringkas)
    2. (Claude Code membaca berkas itu, menulis VAULT-INDEX.hasil.json)
    3. --serap          baca hasil, tulis VAULT-INDEX.json

Tanpa flag: rakit manifest hanya dari ringkasan yang sudah ada (plus stub).
"""

import argparse
import json
from datetime import date
from pathlib import Path

from .parsing import ekstrak_status, ekstrak_wikilink, hitung_hash, potong_untuk_llm
from .paths import klasifikasi_path
from .summarize import _TEMPLATE, _parse_isi_pesan, ringkas_stub

VERSI_SKEMA = 1
NAMA_INDEX = "VAULT-INDEX.json"
NAMA_TUGAS = "VAULT-INDEX.tugas.json"
NAMA_HASIL = "VAULT-INDEX.hasil.json"


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
    """Pilih dokumen yang perlu ringkasan baru.

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


def _panduan_untuk_agent() -> str:
    """Instruksi ringkasan untuk agent: `_TEMPLATE` tanpa bagian isi dokumen.

    Sumber tunggal kebenaran gaya ringkasan tetap `_TEMPLATE` (summarize.py).
    Ini cuma memotong bagian yang spesifik per-dokumen (isi mentah, yang di
    berkas daftar tugas sudah ada per-entri lewat field `isi`), supaya
    berkas `--daftar-tugas` menjelaskan dirinya sendiri ke agent yang
    membacanya, tanpa instruksi terpisah.
    """
    return _TEMPLATE.split("--- ISI DOKUMEN ---")[0].rstrip() + "\n"


def _tandai_perlu_dan_stub(entri: list[dict], lama: dict | None) -> set[str]:
    """Set ringkasan baseline untuk seluruh entri: carry-forward dokumen yang
    tidak perlu diringkas ulang, null untuk yang perlu, lalu terapkan
    `ringkas_stub` untuk dokumen 🔴 Stub (menimpa null ATAU carry-forward --
    stub tidak pernah butuh LLM, di jalur apa pun).

    Mengembalikan path dokumen yang perlu diringkas ulang (`perlu`), supaya
    pemanggil bisa membedakan mana yang masih genuinely butuh ringkasan baru.
    """
    perlu_paths = {e["path"] for e in pilih_yang_perlu_diringkas(entri, lama)}
    sebelumnya = {d["path"]: d for d in (lama or {}).get("dokumen", [])}

    for e in entri:
        if e["path"] in perlu_paths:
            e["ringkasan"] = None
            e["kata_kunci"] = []
        else:
            d = sebelumnya.get(e["path"], {})
            e["ringkasan"] = d.get("ringkasan")
            e["kata_kunci"] = d.get("kata_kunci", [])
        if e["status_emoji"] == "🔴":
            e.update(ringkas_stub(e["judul"]))

    return perlu_paths


def _tulis_index(entri: list[dict], root: Path) -> dict:
    index = rakit_index(entri)
    path_index = root / NAMA_INDEX
    path_index.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Ditulis: {path_index} ({index['jumlah_dokumen']} dokumen)")

    for p in _peringatan_status(entri):
        print(f"  PERINGATAN status hilang: {p}")
    for p in _peringatan_folder_tak_dikenal(entri):
        print(f"  PERINGATAN folder tak dikenal (publik=False): {p}")

    return index


def _mode_daftar_tugas(entri: list[dict], lama: dict | None, path_tugas: Path,
                        full: bool) -> int:
    perlu = pilih_yang_perlu_diringkas(entri, lama, full=full)
    tugas = [
        {
            "path": e["path"],
            "judul": e["judul"],
            "jenis": e["jenis"],
            "hash": e["hash"],
            "isi": potong_untuk_llm(e["_isi"]),
        }
        for e in perlu
        if e["status_emoji"] != "🔴"  # stub ditangani lokal oleh ringkas_stub
    ]
    data = {
        "versi_skema": VERSI_SKEMA,
        "jumlah": len(tugas),
        "panduan": _panduan_untuk_agent(),
        "tugas": tugas,
    }
    path_tugas.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if tugas:
        print(f"{len(tugas)} dokumen perlu diringkas. Ditulis: {path_tugas}")
    else:
        print(f"Tidak ada dokumen yang perlu diringkas. Ditulis: {path_tugas} (tugas: [])")
    return 0


def _mode_serap(entri: list[dict], lama: dict | None, path_hasil: Path, root: Path) -> int:
    if not path_hasil.exists():
        print(
            f"GAGAL: berkas hasil {path_hasil} tidak ditemukan. Jalankan "
            f"--daftar-tugas, buat ringkasannya, baru --serap."
        )
        return 1
    try:
        data = json.loads(path_hasil.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"GAGAL: berkas hasil {path_hasil} tidak bisa dibaca/diparse: {exc}")
        return 1

    hasil = data.get("hasil") if isinstance(data, dict) else None
    if not isinstance(hasil, dict):
        hasil = {}

    _tandai_perlu_dan_stub(entri, lama)
    entri_by_path = {e["path"]: e for e in entri}

    diterima = ditolak = basi = tak_ditemukan = 0
    peringatan_tanpa_hash_dicetak = False

    for path, entri_hasil in hasil.items():
        e = entri_by_path.get(path)
        if e is None:
            print(f"  PERINGATAN: path di hasil tidak ada di vault, dilewati: {path}")
            tak_ditemukan += 1
            continue

        parsed = _parse_isi_pesan(json.dumps(entri_hasil))
        if parsed is None:
            print(f"  DITOLAK (ringkasan/kata_kunci tidak valid): {path}")
            ditolak += 1
            continue

        hash_hasil = entri_hasil.get("hash")
        if hash_hasil is not None:
            if hash_hasil != e["hash"]:
                print(f"  BASI (hash tidak cocok dengan dokumen saat ini, dilewati): {path}")
                basi += 1
                continue
        elif not peringatan_tanpa_hash_dicetak:
            print(
                "  PERINGATAN: entri hasil tanpa 'hash' -- diterima tanpa "
                "verifikasi kebasian."
            )
            peringatan_tanpa_hash_dicetak = True

        e["ringkasan"] = parsed["ringkasan"]
        e["kata_kunci"] = parsed["kata_kunci"]
        diterima += 1

    index = _tulis_index(entri, root)

    print(
        f"Diserap: {diterima}, ditolak: {ditolak}, basi: {basi}, "
        f"tak ditemukan di vault: {tak_ditemukan}, masih gagal: {len(index['gagal'])}"
    )

    # artefak sementara -- hapus begitu manifest berhasil ditulis di atas
    for p in {path_hasil, root / NAMA_TUGAS, root / NAMA_HASIL}:
        if p.exists():
            p.unlink()
            print(f"Dihapus: {p}")

    if index["gagal"]:
        print(f"\n{len(index['gagal'])} dokumen masih belum punya ringkasan:")
        for p in index["gagal"]:
            print(f"  - {p}")
        return 1
    return 0


def _mode_default(entri: list[dict], lama: dict | None, root: Path) -> int:
    _tandai_perlu_dan_stub(entri, lama)
    index = _tulis_index(entri, root)

    if index["gagal"]:
        print(f"\n{len(index['gagal'])} dokumen belum punya ringkasan:")
        for p in index["gagal"]:
            print(f"  - {p}")
        print(
            "\nLangkah berikutnya: python Tools/build-vault-index.py --daftar-tugas"
        )
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bangun VAULT-INDEX.json")
    ap.add_argument("--full", action="store_true", help="regen semua, abaikan hash")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 bila index basi, tanpa menulis")
    ap.add_argument("--root", default=".", help="akar vault")
    ap.add_argument(
        "--daftar-tugas", nargs="?", const="", default=None, metavar="PATH",
        help=f"tulis dokumen yang perlu diringkas ke PATH (default {NAMA_TUGAS} di akar vault)",
    )
    ap.add_argument(
        "--serap", nargs="?", const="", default=None, metavar="PATH",
        help=f"serap ringkasan dari PATH (default {NAMA_HASIL} di akar vault), tulis {NAMA_INDEX}",
    )
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    path_index = root / NAMA_INDEX

    entri = scan_vault(root)
    lama = muat_index(path_index)

    if args.check:
        perlu = pilih_yang_perlu_diringkas(entri, lama, full=args.full)
        if perlu:
            print(f"BASI: {len(perlu)} dokumen belum terwakili di {NAMA_INDEX}")
            for e in perlu[:10]:
                print(f"  - {e['path']}")
            return 1
        print(f"SEGAR: {NAMA_INDEX} sinkron dengan {len(entri)} dokumen")
        return 0

    if args.daftar_tugas is not None:
        path_tugas = Path(args.daftar_tugas) if args.daftar_tugas else root / NAMA_TUGAS
        return _mode_daftar_tugas(entri, lama, path_tugas, full=args.full)

    if args.serap is not None:
        path_hasil = Path(args.serap) if args.serap else root / NAMA_HASIL
        return _mode_serap(entri, lama, path_hasil, root)

    return _mode_default(entri, lama, root)
