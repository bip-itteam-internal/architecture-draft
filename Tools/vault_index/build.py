"""Orkestrasi: scan vault, diff incremental, rakit dan tulis VAULT-INDEX.json."""

import argparse
import json
import time
from datetime import date, datetime, timezone
from pathlib import Path

import anthropic

from .parsing import ekstrak_status, ekstrak_wikilink, hitung_hash
from .paths import klasifikasi_path
from .summarize import MODEL, ambil_hasil, ringkas_stub, submit_batch

VERSI_SKEMA = 1
NAMA_INDEX = "VAULT-INDEX.json"

# Sidecar sementara: batch_id + peta custom_id->path, ditulis SEGERA setelah
# submit (sebelum polling yang bisa berjalan sampai 24 jam). Kalau proses mati
# di tengah polling, sidecar ini satu-satunya cara melanjutkan tanpa
# mensubmit (dan membayar) batch baru. Bukan isi vault -> masuk .gitignore.
NAMA_SIDECAR = "VAULT-INDEX.batch.json"


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


def _tulis_sidecar(path_sidecar: Path, batch_id: str, tugas: list[dict]) -> None:
    """Simpan batch_id + peta custom_id->path SEGERA setelah submit, sebelum
    polling dimulai.

    Peta custom_id->path wajib ada di sini: peta itu dibangun di memori saat
    submit dan akan hilang total kalau proses mati saat polling. Tanpanya,
    hasil batch yang masih ada di server Anthropic (sampai 29 hari) tidak
    bisa dipetakan balik ke dokumen mana pun -- batch_id saja tidak cukup.
    """
    data = {
        "batch_id": batch_id,
        "disubmit_pada": datetime.now(timezone.utc).isoformat(),
        "tugas": [{"custom_id": t["custom_id"], "path": t["path"]} for t in tugas],
    }
    path_sidecar.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _muat_sidecar(path_sidecar: Path) -> dict | None:
    """Muat sidecar. Hilang, rusak, atau bentuknya tak dikenal -> None.

    Jangan pernah menebak isi sidecar yang rusak; pemanggil harus berhenti
    dengan pesan jelas, bukan melanjutkan dengan asumsi.
    """
    if not path_sidecar.exists():
        return None
    try:
        data = json.loads(path_sidecar.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict) or "batch_id" not in data or "tugas" not in data:
        return None
    return data


def _tunggu_batch_dengan_deadline(
    client, batch_id: str, batas_tunggu_menit: int, interval: int = 30
) -> bool:
    """Poll status batch dengan batas waktu, TANPA pernah membuang batch_id.

    Beda dari `summarize.ambil_hasil` (menunggu tanpa batas): fungsi ini
    hanya mengecek `processing_status` dan berhenti begitu 'ended' (True)
    atau begitu batas waktu terlampaui (False). Baik hasil True maupun
    False, batch_id tidak hilang -- sidecar sudah ditulis oleh pemanggil
    sebelum fungsi ini dipanggil, jadi keduanya sama-sama pulih via
    `--batch-id`.

    Batas waktu dihitung dari akumulasi `interval` yang "ditidurkan", bukan
    jam dinding. Ini sengaja: cukup untuk deadline praktis, dan bisa diuji
    hanya dengan menambal `time.sleep` -- konsisten dengan gaya
    `ambil_hasil` di summarize.py -- tanpa perlu menambal jam sistem juga.
    """
    batas_detik = batas_tunggu_menit * 60
    terlewat = 0
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            return True
        if terlewat >= batas_detik:
            return False
        time.sleep(interval)
        terlewat += interval


def _pesan_deadline_terlampaui(batch_id: str, path_sidecar: Path, menit: int) -> str:
    return (
        f"GAGAL: batch {batch_id} belum 'ended' setelah {menit} menit. "
        f"batch_id TIDAK hilang -- sidecar {path_sidecar} tetap ada. "
        f"Lanjutkan nanti dengan:\n"
        f"  python Tools/build-vault-index.py --batch-id {batch_id}"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bangun VAULT-INDEX.json")
    ap.add_argument("--full", action="store_true", help="regen semua, abaikan hash")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 bila index basi, tanpa menulis")
    ap.add_argument("--root", default=".", help="akar vault")
    ap.add_argument("--batch-id", default=None,
                     help="lanjutkan batch yang sudah tersubmit (lewati submit ulang)")
    ap.add_argument("--abaikan-batch-tertinggal", action="store_true",
                     help="submit batch baru walau ada sidecar batch tertinggal")
    ap.add_argument("--batas-tunggu-menit", type=int, default=90,
                     help="batas waktu polling batch dalam menit (default 90)")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    path_index = root / NAMA_INDEX
    path_sidecar = root / NAMA_SIDECAR

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
    entri_by_path = {e["path"]: e for e in entri}

    if args.batch_id:
        # --- B2: lanjutkan batch yang sudah tersubmit, tanpa submit ulang ---
        client = anthropic.Anthropic()

        sidecar = _muat_sidecar(path_sidecar)
        if sidecar is None:
            print(
                f"GAGAL: --batch-id {args.batch_id} diberikan tapi sidecar "
                f"{NAMA_SIDECAR} tidak ditemukan/rusak di {root}. Tidak bisa "
                f"memetakan hasil batch ke dokumen tanpa itu. Tidak menebak, berhenti."
            )
            return 1
        if sidecar["batch_id"] != args.batch_id:
            print(
                f"GAGAL: sidecar {NAMA_SIDECAR} menyebut batch_id "
                f"'{sidecar['batch_id']}', bukan '{args.batch_id}' yang diminta. "
                f"Tidak menebak, berhenti."
            )
            return 1

        selesai = _tunggu_batch_dengan_deadline(
            client, args.batch_id, args.batas_tunggu_menit
        )
        if not selesai:
            print(_pesan_deadline_terlampaui(
                args.batch_id, path_sidecar, args.batas_tunggu_menit
            ))
            return 1

        hasil = ambil_hasil(client, args.batch_id)
        for t in sidecar["tugas"]:
            e = entri_by_path.get(t["path"])
            if e is None:
                continue  # dokumen sudah tak ada lagi di vault sejak submit
            r = hasil.get(t["custom_id"])
            e["ringkasan"] = r["ringkasan"] if r else None
            e["kata_kunci"] = r["kata_kunci"] if r else []

    else:
        # --- B3: jaring pengaman -- sidecar tertinggal menghalangi submit baru ---
        sidecar_tertinggal = _muat_sidecar(path_sidecar)
        if sidecar_tertinggal is not None and not args.abaikan_batch_tertinggal:
            print(
                f"GAGAL: batch tertinggal ditemukan (batch_id="
                f"{sidecar_tertinggal['batch_id']}) di {path_sidecar}. Proses "
                f"sebelumnya kemungkinan mati sebelum hasilnya diambil. Mensubmit "
                f"batch baru sekarang berisiko membayar dua kali.\n"
                f"Lanjutkan batch itu dengan:\n"
                f"  python Tools/build-vault-index.py --batch-id "
                f"{sidecar_tertinggal['batch_id']}\n"
                f"Atau, bila memang ingin mengabaikannya dan submit baru:\n"
                f"  python Tools/build-vault-index.py --abaikan-batch-tertinggal"
            )
            return 1

        # 🔴 Stub tidak perlu LLM
        perlu_llm = []
        for e in perlu:
            if e["status_emoji"] == "🔴":
                e.update(ringkas_stub(e["judul"]))
            else:
                perlu_llm.append(e)

        if perlu_llm:
            client = anthropic.Anthropic()
            tugas = [
                {"custom_id": f"doc-{i}", "judul": e["judul"],
                 "jenis": e["jenis"], "isi": e["_isi"], "path": e["path"]}
                for i, e in enumerate(perlu_llm)
            ]
            print(f"Submit batch {len(tugas)} dokumen ke {MODEL} ...")
            batch_id = submit_batch(client, tugas)
            print(f"Batch id: {batch_id}")

            # B1: sidecar ditulis SEGERA, sebelum polling (yang bisa berjalan
            # sampai 24 jam) dimulai.
            _tulis_sidecar(path_sidecar, batch_id, tugas)
            print(f"Sidecar ditulis: {path_sidecar}")

            selesai = _tunggu_batch_dengan_deadline(
                client, batch_id, args.batas_tunggu_menit
            )
            if not selesai:
                print(_pesan_deadline_terlampaui(
                    batch_id, path_sidecar, args.batas_tunggu_menit
                ))
                return 1

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

    # B4: hapus sidecar HANYA setelah manifest berhasil ditulis di atas.
    if path_sidecar.exists():
        path_sidecar.unlink()
        print(f"Sidecar dihapus: {path_sidecar}")

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
