"""Orkestrasi: scan vault, diff incremental, rakit dan tulis VAULT-INDEX.json."""

import argparse
import json
import os
import time
from datetime import date, datetime, timezone
from pathlib import Path

import anthropic

from .parsing import ekstrak_status, ekstrak_wikilink, hitung_hash
from .paths import klasifikasi_path
from .summarize import MODEL, ambil_hasil, ringkas_stub, submit_batch

VERSI_SKEMA = 1
NAMA_INDEX = "VAULT-INDEX.json"

# Sidecar sementara: batch_id + peta custom_id->path. Ditulis DUA TAHAP:
#   1. "submitting" (batch_id null) -- SEBELUM submit_batch dipanggil sama
#      sekali, supaya peta custom_id->path sudah aman di disk sebelum ada
#      kemungkinan uang terpakai (create() bisa sukses di server tapi
#      exception terjadi sebelum nilainya kembali ke kita -- timeout baca
#      respons, KeyboardInterrupt, retry SDK tanpa idempotency key).
#   2. "submitted" (batch_id terisi) -- SEGERA setelah submit_batch kembali,
#      sebelum polling yang bisa berjalan sampai 24 jam dimulai.
# Kalau proses mati di tengah polling, sidecar ini satu-satunya cara
# melanjutkan tanpa mensubmit (dan membayar) batch baru. Bukan isi vault ->
# masuk .gitignore.
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


class SidecarRusak(Exception):
    """Sidecar ADA tapi tidak bisa dipakai (JSON tak valid atau key wajib
    hilang) -- beda dari 'tidak ada'.

    Menyamakan keduanya (dua-duanya jadi None) adalah bug: gerbang deteksi
    batch tertinggal hanya menyala bila hasil `_muat_sidecar` bukan None,
    jadi sidecar rusak akan LOLOS gerbang itu dan proses mensubmit batch
    baru padahal batch lama (yang sudah dibayar) belum tentu sudah diambil.
    Dengan exception ini, pemanggil WAJIB menangani kasus rusak secara
    eksplisit dan berbeda dari kasus tidak-ada.
    """

    def __init__(self, path: Path, mentah: str):
        self.path = path
        self.mentah = mentah
        super().__init__(f"sidecar rusak: {path}")


def _tulis_sidecar(
    path_sidecar: Path,
    batch_id: str | None,
    tugas: list[dict],
    status: str = "submitted",
) -> None:
    """Simpan status + batch_id (boleh None) + peta custom_id->path.

    Dipanggil dua kali per submit baru (lihat komentar `NAMA_SIDECAR`):
    sekali dengan `status="submitting"` dan `batch_id=None` SEBELUM
    `submit_batch` dipanggil, sekali lagi dengan `status="submitted"` dan
    `batch_id` terisi SEGERA setelah `submit_batch` kembali. Jalur
    `--batch-id` yang menerima sidecar `submitting` juga memanggil ini untuk
    merekam batch_id yang dimasukkan manual.

    Peta custom_id->path wajib ada di sini SEJAK panggilan pertama: peta itu
    dibangun di memori saat submit dan akan hilang total kalau proses mati.
    Tanpanya, hasil batch yang masih ada di server Anthropic (sampai 29
    hari) tidak bisa dipetakan balik ke dokumen mana pun -- batch_id saja
    tidak cukup.

    Ditulis ATOMIC: tulis ke berkas sementara di direktori yang SAMA, flush +
    fsync supaya isinya benar-benar di disk, baru `os.replace` (atomic di
    POSIX maupun Windows) ke nama akhir. Ini membuat sidecar rusak-separuh
    mustahil terjadi -- proses yang mati kapan pun sebelum `os.replace` cuma
    meninggalkan berkas `.tmp-*`, bukan `NAMA_SIDECAR` yang setengah tertulis
    (yang justru melumpuhkan gerbangnya sendiri lewat `SidecarRusak`).
    """
    data = {
        "status": status,
        "batch_id": batch_id,
        "disubmit_pada": datetime.now(timezone.utc).isoformat(),
        "tugas": [{"custom_id": t["custom_id"], "path": t["path"]} for t in tugas],
    }
    isi = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    tmp = path_sidecar.with_name(f"{path_sidecar.name}.tmp-{os.getpid()}")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(isi)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path_sidecar)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def _cetak_pemulihan_sidecar_gagal(
    exc: BaseException,
    path_sidecar: Path,
    root: Path,
    batch_id: str | None,
    tugas: list[dict],
    tahap: str,
) -> None:
    """Cetak blok pemulihan saat `_tulis_sidecar` gagal dengan exception
    APA PUN (Perbaikan 2 -- bukan cuma `OSError`: `KeyboardInterrupt` dan
    `TypeError` dibuktikan lolos lewat `except OSError` yang lama).

    Dipanggil di KEDUA titik penulisan sidecar. `batch_id=None` berarti ini
    terjadi SEBELUM `submit_batch` dipanggil -- belum ada uang terpakai,
    aman untuk memperbaiki lalu mengulang. `batch_id` terisi berarti
    `submit_batch` SUDAH sukses -- uang SUDAH terpakai, satu-satunya jalan
    pulih adalah menyalin blok JSON di stdout ini jadi `NAMA_SIDECAR` manual
    lalu melanjutkan dengan `--batch-id`.

    Pemanggil WAJIB `raise` (bukan menelan) setelah memanggil ini --
    `KeyboardInterrupt`/`SystemExit` harus tetap menghentikan proses.
    """
    peta = [{"custom_id": t["custom_id"], "path": t["path"]} for t in tugas]
    if batch_id is None:
        print(
            f"GAGAL menulis sidecar intent {path_sidecar} {tahap}: {exc}\n"
            f"Belum ada batch yang tersubmit di titik ini -- aman untuk "
            f"memperbaiki masalah penulisan berkas ini lalu menjalankan "
            f"ulang.\n"
            f"Peta custom_id->path yang seharusnya tercatat (referensi bila "
            f"submit tetap sempat terjadi di server sebelum proses ini "
            f"berhenti):\n"
            f"{json.dumps(peta, ensure_ascii=False, indent=2)}"
        )
        return
    pemulihan = {
        "status": "submitted",
        "batch_id": batch_id,
        "disubmit_pada": datetime.now(timezone.utc).isoformat(),
        "tugas": peta,
    }
    print(
        f"GAGAL menulis sidecar {path_sidecar} {tahap}: {exc}\n"
        f"PENTING: batch {batch_id} SUDAH tersubmit dan SUDAH dibayar -- "
        f"jangan submit ulang. Salin blok JSON di bawah ini persis apa "
        f"adanya, simpan sebagai {NAMA_SIDECAR} di {root}, lalu lanjutkan "
        f"dengan:\n"
        f"  python Tools/build-vault-index.py --batch-id {batch_id}\n"
        f"--- SALIN DARI BARIS DI BAWAH INI ---\n"
        f"{json.dumps(pemulihan, ensure_ascii=False, indent=2)}\n"
        f"--- SAMPAI BARIS DI ATAS INI ---"
    )


def _muat_sidecar(path_sidecar: Path) -> dict | None:
    """Muat sidecar. Tidak ada -> None. ADA tapi rusak (JSON tak valid atau
    key wajib hilang) -> raise `SidecarRusak`, BUKAN None.

    Jangan pernah menebak isi sidecar yang rusak; pemanggil harus berhenti
    dengan pesan jelas (memuat isi mentah supaya bisa diselamatkan manual),
    bukan melanjutkan dengan asumsi seolah sidecar tak pernah ada.
    """
    if not path_sidecar.exists():
        return None
    try:
        mentah = path_sidecar.read_text(encoding="utf-8")
    except OSError:
        return None
    try:
        data = json.loads(mentah)
    except json.JSONDecodeError as exc:
        raise SidecarRusak(path_sidecar, mentah) from exc
    if not isinstance(data, dict) or "batch_id" not in data or "tugas" not in data:
        raise SidecarRusak(path_sidecar, mentah)
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

    # 🔴 Stub tidak perlu LLM -- berlaku di KEDUA jalur (submit baru maupun
    # --batch-id). Vault nyata punya beberapa dokumen stub; kalau loop ini
    # cuma ada di satu cabang, jalur satunya selalu berakhir dengan stub
    # ber-ringkasan null (masuk daftar gagal, exit 1) walau tidak ada
    # yang benar-benar salah.
    perlu_llm = []
    for e in perlu:
        if e["status_emoji"] == "🔴":
            e.update(ringkas_stub(e["judul"]))
        else:
            perlu_llm.append(e)

    if args.batch_id:
        # --- B2: lanjutkan batch yang sudah tersubmit, tanpa submit ulang ---
        client = anthropic.Anthropic()

        try:
            sidecar = _muat_sidecar(path_sidecar)
        except SidecarRusak as exc:
            print(
                f"GAGAL: --batch-id {args.batch_id} diberikan tapi sidecar "
                f"{NAMA_SIDECAR} di {exc.path} RUSAK (tidak bisa diparse atau "
                f"bentuknya tak dikenal). Tidak menebak, berhenti.\n"
                f"Isi mentah sidecar (untuk penyelamatan manual):\n{exc.mentah}"
            )
            return 1
        if sidecar is None:
            print(
                f"GAGAL: --batch-id {args.batch_id} diberikan tapi sidecar "
                f"{NAMA_SIDECAR} tidak ditemukan di {root}. Tidak bisa "
                f"memetakan hasil batch ke dokumen tanpa itu. Tidak menebak, berhenti."
            )
            return 1
        status_sidecar = sidecar.get("status", "submitted")
        if status_sidecar == "submitting":
            # I1 (Perbaikan 1): sidecar intent (batch_id belum tercatat) --
            # ini JUSTRU skenario pemulihan utama: pengguna menemukan
            # batch_id secara manual (mis. dashboard/API Anthropic) dan
            # memasukkannya di sini. Peta custom_id->path di dalamnya sudah
            # utuh sejak ditulis SEBELUM submit_batch dipanggil -- terima
            # apa adanya, lalu SEGERA perbarui sidecar jadi status
            # 'submitted' dengan batch_id itu supaya jejak di disk tetap
            # konsisten kalau proses ini mati lagi di tengah polling.
            try:
                _tulis_sidecar(
                    path_sidecar, args.batch_id, sidecar["tugas"], status="submitted"
                )
            except BaseException as exc:
                _cetak_pemulihan_sidecar_gagal(
                    exc, path_sidecar, root, args.batch_id, sidecar["tugas"],
                    "saat memperbarui sidecar 'submitting' dengan --batch-id",
                )
                raise
            print(
                f"Sidecar {path_sidecar} diperbarui: status=submitted, "
                f"batch_id={args.batch_id}"
            )
        elif sidecar["batch_id"] != args.batch_id:
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
        try:
            sidecar_tertinggal = _muat_sidecar(path_sidecar)
        except SidecarRusak as exc:
            # Sidecar RUSAK tidak boleh diperlakukan sama dengan "tidak ada":
            # ini bisa berarti proses sebelumnya mati SETELAH submit_batch
            # sukses (uang sudah terpakai) tapi SEBELUM sidecar selesai
            # ditulis. Selalu blokir -- termasuk saat --abaikan-batch-tertinggal
            # dipakai, karena flag itu untuk mengabaikan sidecar VALID yang
            # sudah dibaca dan dipahami risikonya, bukan untuk melewati
            # sidecar yang bahkan belum bisa dibaca.
            print(
                f"GAGAL: sidecar {NAMA_SIDECAR} di {exc.path} ADA tapi RUSAK "
                f"(tidak bisa diparse atau bentuknya tak dikenal). Ini bisa "
                f"berarti sebuah batch SUDAH tersubmit (sudah dibayar) dan "
                f"proses mati sebelum sidecar-nya selesai ditulis. TIDAK "
                f"mensubmit batch baru sampai ini ditangani manual -- "
                f"perbaiki atau hapus {exc.path} setelah memastikan tidak "
                f"ada batch yang belum diambil hasilnya.\n"
                f"Isi mentah sidecar (untuk penyelamatan manual):\n{exc.mentah}"
            )
            return 1
        if sidecar_tertinggal is not None:
            status_tertinggal = sidecar_tertinggal.get("status", "submitted")
            if status_tertinggal == "submitting":
                # I1 (Perbaikan 1): batch_id BELUM tercatat -- proses
                # sebelumnya kemungkinan mati TEPAT di sekitar submit.
                # Beda dari sidecar 'submitted' biasa di bawah: di sini kita
                # bahkan tidak tahu apakah submit-nya sempat sukses di
                # server. SELALU blokir -- termasuk saat
                # --abaikan-batch-tertinggal dipakai, karena flag itu untuk
                # mengabaikan sidecar VALID yang risikonya sudah dipahami
                # (batch_id diketahui), bukan status "kita bahkan tidak
                # tahu" yang justru paling berisiko menyembunyikan batch
                # yatim yang sudah dibayar.
                print(
                    f"GAGAL: sidecar {NAMA_SIDECAR} di {path_sidecar} berstatus "
                    f"'submitting' -- batch_id BELUM tercatat. Proses sebelumnya "
                    f"kemungkinan mati TEPAT di sekitar submit: ADA kemungkinan "
                    f"sebuah batch SUDAH tersubmit dan SUDAH dibayar di server "
                    f"Anthropic, tapi batch_id-nya belum sempat tersimpan di "
                    f"sini -- batch itu bisa jadi YATIM (orphan) tanpa jejak "
                    f"lokal sama sekali. JANGAN submit batch baru sebelum "
                    f"memeriksa manual apakah ada batch semacam itu (mis. lewat "
                    f"dashboard/API Anthropic, cek sekitar waktu "
                    f"{sidecar_tertinggal.get('disubmit_pada')}).\n"
                    f"Peta custom_id->path (untuk pencocokan manual bila batch "
                    f"ketemu):\n"
                    f"{json.dumps(sidecar_tertinggal['tugas'], ensure_ascii=False, indent=2)}\n"
                    f"Kalau KETEMU batch_id-nya, lanjutkan dengan:\n"
                    f"  python Tools/build-vault-index.py --batch-id <BATCH_ID>\n"
                    f"Kalau YAKIN tidak ada batch yang tersubmit (mis. proses "
                    f"mati sebelum sempat menghubungi server), hapus "
                    f"{path_sidecar} lalu jalankan ulang."
                )
                return 1
            if not args.abaikan_batch_tertinggal:
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

        if perlu_llm:
            client = anthropic.Anthropic()
            tugas = [
                {"custom_id": f"doc-{i}", "judul": e["judul"],
                 "jenis": e["jenis"], "isi": e["_isi"], "path": e["path"]}
                for i, e in enumerate(perlu_llm)
            ]
            # I1 (Perbaikan 1): tulis sidecar INTENT (status='submitting',
            # batch_id null) SEBELUM submit_batch dipanggil sama sekali.
            # Menutup celah terakhir: kalau create() sukses di server tapi
            # exception terjadi SEBELUM nilainya kembali ke sini (timeout
            # baca respons, KeyboardInterrupt, retry SDK yang melahirkan
            # batch ganda -- anthropic 0.117.0 DEFAULT_MAX_RETRIES=2 tanpa
            # header idempotency), peta custom_id->path tetap ada di disk
            # walau batch_id belum diketahui. Tanpa ini, batch berbayar itu
            # jadi TANPA JEJAK sama sekali di sisi kita.
            try:
                _tulis_sidecar(path_sidecar, None, tugas, status="submitting")
            except BaseException as exc:
                # I2 (Perbaikan 2): tangkap APA PUN (bukan cuma OSError),
                # cetak info, lalu naikkan lagi -- KeyboardInterrupt/
                # SystemExit tetap harus menghentikan proses.
                _cetak_pemulihan_sidecar_gagal(
                    exc, path_sidecar, root, None, tugas,
                    "SEBELUM submit_batch dipanggil",
                )
                raise
            print(f"Sidecar intent ditulis (status=submitting): {path_sidecar}")

            print(f"Submit batch {len(tugas)} dokumen ke {MODEL} ...")
            batch_id = submit_batch(client, tugas)
            print(f"Batch id: {batch_id}")

            # I1: sidecar diperbarui jadi status='submitted' SEGERA setelah
            # submit_batch kembali, sebelum polling (yang bisa berjalan
            # sampai 24 jam) dimulai.
            try:
                _tulis_sidecar(path_sidecar, batch_id, tugas, status="submitted")
            except BaseException as exc:
                # I2: uang SUDAH terpakai (submit_batch sukses di atas) dan
                # sidecar GAGAL ditulis -- tanpa ini, batch_id hilang total
                # dari disk, dan --batch-id mewajibkan sidecar. Satu-satunya
                # jalan pulih: cetak semuanya ke stdout dalam bentuk yang
                # bisa disalin manusia jadi VAULT-INDEX.batch.json. Lalu
                # tetap naikkan exception -- jangan menelan.
                _cetak_pemulihan_sidecar_gagal(
                    exc, path_sidecar, root, batch_id, tugas,
                    "SETELAH submit_batch sukses",
                )
                raise
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
