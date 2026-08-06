"""Orkestrasi: scan vault, diff incremental, rakit dan tulis VAULT-INDEX.json.

Ringkasan LLM dibuat oleh Claude Code sendiri, lewat tiga langkah CLI (bukan
panggilan API dari modul ini -- modul ini tidak pernah menyentuh jaringan):

    1. --daftar-tugas   tulis VAULT-INDEX.tugas.json (dokumen yang perlu diringkas)
       (atau, dengan --pecah N, beberapa VAULT-INDEX.tugas.NNN.json berdiri
       sendiri, untuk difan-out ke banyak subagent paralel)
    2. (Claude Code membaca berkas itu, menulis VAULT-INDEX.hasil.json,
       atau satu VAULT-INDEX.hasil.NNN.json per subagent bila dipecah)
    3. --serap          baca hasil (satu berkas atau gabungan banyak berkas
       bernomor), tulis VAULT-INDEX.json

Tanpa flag: rakit manifest hanya dari ringkasan yang sudah ada (plus stub).
"""

import argparse
import json
from datetime import date
from pathlib import Path

from .parsing import ekstrak_status, ekstrak_wikilink, hitung_hash, potong_untuk_llm
from .paths import klasifikasi_path
from .summarize import PANDUAN_AGENT, _parse_isi_pesan, ringkas_stub

VERSI_SKEMA = 1
NAMA_INDEX = "VAULT-INDEX.json"
NAMA_TUGAS = "VAULT-INDEX.tugas.json"
NAMA_HASIL = "VAULT-INDEX.hasil.json"

# Pola glob untuk berkas potongan bernomor (VAULT-INDEX.tugas.NNN.json /
# VAULT-INDEX.hasil.NNN.json). Diturunkan dari NAMA_TUGAS/NAMA_HASIL supaya
# tidak ada dua sumber kebenaran untuk nama dasarnya. `*` glob TIDAK cocok
# dengan berkas tunggal tanpa nomor (mis. "VAULT-INDEX.tugas.json") --
# butuh minimal satu karakter di antara "tugas." dan ".json" -- jadi pola
# ini murni menyasar potongan, dan berkas tunggal ditangani terpisah di
# tiap tempat yang butuh (lihat _temukan_berkas_hasil).
POLA_TUGAS_POTONGAN = Path(NAMA_TUGAS).stem + ".*.json"
POLA_HASIL_POTONGAN = Path(NAMA_HASIL).stem + ".*.json"


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
    """Status absen normal untuk meta/api; janggal untuk domain/adr/runbook.

    `runbook` ikut diperiksa karena `CLAUDE.md` §2 menegaskan Runbooks TIDAK
    dikecualikan dari status marker — beda dari `log`, `template`, dan
    `workspace` yang memang dikecualikan. Sebelumnya jenis ini tak diperiksa
    sama sekali, sehingga 12 runbook yang statusnya salah terbaca (ditulis
    blockquote, sementara parser hanya mengenal bullet) lolos tanpa satu pun
    peringatan selama berbulan-bulan. Bugnya di parser, tapi yang membuatnya
    tak terlihat adalah tak adanya yang memeriksa.
    """
    return [
        e["path"]
        for e in entri
        if e["jenis"] in ("domain", "adr", "runbook")
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
    """Instruksi lengkap untuk agent yang membaca `--daftar-tugas` (mode satu
    berkas, tanpa --pecah).

    Sumber tunggal kebenaran: `PANDUAN_AGENT` (summarize.py) -- konstanta
    berdiri sendiri yang menjelaskan gaya ringkasan DAN kontrak keluaran
    (nama berkas, bentuk JSON, kewajiban menyalin `hash`). Lihat docstring
    `PANDUAN_AGENT` untuk alasan kenapa ini bukan turunan `_TEMPLATE`.
    """
    return PANDUAN_AGENT


def _panduan_untuk_potongan(nomor: int, total: int, berkas_keluaran: str) -> str:
    """Panduan berdiri sendiri untuk SATU potongan (`--pecah`).

    Subagent yang menangani potongan ini hanya membaca berkas potongan itu
    sendiri -- tidak ada konteks lain -- jadi catatan posisi + override nama
    berkas keluaran ditaruh di ATAS panduan gaya umum (`PANDUAN_AGENT`).

    SENGAJA bukan substring-replace ke teks `PANDUAN_AGENT` (mis. mengganti
    kemunculan `NAMA_HASIL` di sana): itu rapuh terhadap perubahan wording di
    masa depan pada `summarize.py` -- kalau substring-nya tidak lagi cocok
    persis, `.replace()` diam-diam tidak melakukan apa-apa, dan panduan yang
    dibaca agent tetap menyebut nama berkas default yang SALAH. Menambahkan
    catatan override di depan tidak punya mode gagal senyap seperti itu.
    """
    return (
        f"## Kamu mengerjakan potongan {nomor} dari {total}\n\n"
        "Daftar tugas ini dipecah supaya beberapa agent bisa mengerjakannya "
        "paralel. Potongan lain ditangani agent lain -- JANGAN membaca atau "
        "menunggu berkas potongan lain, cukup kerjakan `tugas` di bawah ini.\n\n"
        f"**Berkas keluaran WAJIB untuk potongan ini: `{berkas_keluaran}`** "
        f"(BUKAN `{NAMA_HASIL}` yang disebut di panduan gaya di bawah -- itu "
        "nama default untuk mode tanpa pemecahan. Subagent lain menulis ke "
        "berkas hasil masing-masing dengan nama berbeda supaya tidak saling "
        "menimpa; `--serap` nanti menggabungkan seluruhnya).\n\n"
        "---\n\n"
        f"{PANDUAN_AGENT}"
    )


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


# --- Perubahan A: --pecah N pada --daftar-tugas -----------------------------


def _tipe_pecah(nilai: str) -> int:
    """Validator argparse untuk --pecah: integer >= 1."""
    try:
        n = int(nilai)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"--pecah harus berupa integer, dapat: {nilai!r}"
        )
    if n < 1:
        raise argparse.ArgumentTypeError("--pecah harus >= 1")
    return n


def _bersihkan_potongan_tugas(root: Path) -> int:
    """Hapus VAULT-INDEX.tugas.NNN.json lama sebelum menulis yang baru.

    Run sebelumnya bisa saja menghasilkan lebih banyak potongan daripada run
    sekarang (mis. 10 lalu 3) -- sisa potongan basi HARUS dihapus, bukan
    dibiarkan tersebar dan diserap belakangan sebagai hasil yang sudah tidak
    relevan. Hanya menyasar potongan BERNOMOR -- BUKAN VAULT-INDEX.tugas.json
    tunggal (mode tanpa --pecah), yang siklus hidupnya diatur --serap.
    """
    lama = sorted(root.glob(POLA_TUGAS_POTONGAN))
    for p in lama:
        try:
            p.unlink()
        except OSError as exc:
            print(f"PERINGATAN: gagal menghapus potongan lama {p}: {exc}")
    return len(lama)


def _tulis_tugas_terpecah(tugas: list[dict], pecah: int, root: Path) -> int:
    """Tulis --pecah N potongan berdiri sendiri di akar vault.

    Selalu ditulis ke `root` dengan nama default bernomor -- BUKAN mengikuti
    PATH custom yang mungkin diberikan ke --daftar-tugas -- karena --serap
    (tanpa PATH) menemukan berkas hasil lewat pola nama tetap yang berpadanan
    (lihat _temukan_berkas_hasil); PATH custom akan memutus pemadanan itu.
    """
    dihapus = _bersihkan_potongan_tugas(root)
    if dihapus:
        print(f"Dihapus {dihapus} potongan tugas lama.")
    else:
        print("Tidak ada potongan tugas lama untuk dihapus.")

    if not tugas:
        print("Tidak ada dokumen yang perlu diringkas. Tidak ada potongan ditulis.")
        return 0

    kelompok = [tugas[i:i + pecah] for i in range(0, len(tugas), pecah)]
    total = len(kelompok)
    root.mkdir(parents=True, exist_ok=True)

    for idx, chunk in enumerate(kelompok, start=1):
        nomor = f"{idx:03d}"
        berkas_keluaran = f"{Path(NAMA_HASIL).stem}.{nomor}.json"
        data = {
            "versi_skema": VERSI_SKEMA,
            "jumlah": len(chunk),
            "potongan": idx,
            "total_potongan": total,
            "berkas_keluaran": berkas_keluaran,
            "panduan": _panduan_untuk_potongan(idx, total, berkas_keluaran),
            "tugas": chunk,
        }
        p = root / f"{Path(NAMA_TUGAS).stem}.{nomor}.json"
        p.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"Ditulis: {p} ({len(chunk)} dokumen, potongan {idx}/{total})")

    print(f"{len(tugas)} dokumen dipecah jadi {total} potongan di {root}.")
    return 0


def _mode_daftar_tugas(
    entri: list[dict], lama: dict | None, path_tugas: Path, root: Path,
    full: bool, pecah: int | None,
) -> int:
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

    if pecah is not None:
        return _tulis_tugas_terpecah(tugas, pecah, root)

    data = {
        "versi_skema": VERSI_SKEMA,
        "jumlah": len(tugas),
        "panduan": _panduan_untuk_agent(),
        "tugas": tugas,
    }
    path_tugas.parent.mkdir(parents=True, exist_ok=True)
    path_tugas.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if tugas:
        print(f"{len(tugas)} dokumen perlu diringkas. Ditulis: {path_tugas}")
    else:
        print(f"Tidak ada dokumen yang perlu diringkas. Ditulis: {path_tugas} (tugas: [])")
    return 0


# --- Perubahan B: --serap menggabungkan banyak berkas hasil -----------------


def _artefak_potongan_tersisa(root: Path) -> list[Path]:
    """Seluruh berkas potongan bernomor (tugas + hasil) yang masih ada."""
    return sorted(root.glob(POLA_TUGAS_POTONGAN)) + sorted(root.glob(POLA_HASIL_POTONGAN))


def _temukan_berkas_hasil(root: Path) -> list[Path]:
    """Temukan berkas hasil untuk --serap TANPA PATH eksplisit.

    Seluruh VAULT-INDEX.hasil.NNN.json (urut nama, hasil fan-out --pecah),
    PLUS VAULT-INDEX.hasil.json tunggal bila ada (mode lama / tanpa pemecahan).
    """
    berkas = sorted(root.glob(POLA_HASIL_POTONGAN))
    tunggal = root / NAMA_HASIL
    if tunggal.exists():
        berkas.append(tunggal)
    return berkas


def _muat_berkas_hasil(p: Path) -> tuple[dict | None, str | None]:
    """Muat + validasi bentuk SATU berkas hasil.

    (peta_hasil, None) sukses -- (None, pesan) gagal, pesan sudah termasuk
    detail supaya operator tahu berkas mana yang salah dan kenapa. Rusak
    bukan berarti kosong: pemanggil TIDAK boleh memperlakukan None sebagai
    {} (nol diserap) -- itu persis skenario yang dulu membuang 210 ringkasan.
    """
    try:
        mentah = p.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"tidak bisa dibaca: {exc}"
    try:
        data = json.loads(mentah)
    except json.JSONDecodeError as exc:
        return None, f"tidak bisa diparse sebagai JSON: {exc}"

    if not isinstance(data, dict) or not isinstance(data.get("hasil"), dict):
        return None, (
            'bentuknya salah. Diharapkan objek JSON level atas dengan key '
            '"hasil" berisi peta path -> {"ringkasan": ..., "kata_kunci": '
            '[...], "hash": ...}. Contoh:\n'
            '  {"hasil": {"Sales/Sales - A.md": {"ringkasan": "...", '
            '"kata_kunci": ["..."], "hash": "..."}}}'
        )
    return data["hasil"], None


def _gabung_berkas_hasil(berkas_list: list[Path]) -> tuple[dict | None, int]:
    """Muat + gabungkan banyak berkas hasil.

    Dua aturan fail-closed, keduanya menolak SELURUH operasi (bukan
    melewati/memakai sebagian):

    1. Bentuk salah pada SATU berkas -> tolak seluruhnya. "Rusak bukan
       berarti kosong" -- satu berkas rusak di antara sepuluh tidak boleh
       diam-diam diperlakukan seolah berkas itu {} (nol entri).
    2. Path dokumen yang sama muncul di lebih dari satu berkas -> konflik ->
       tolak seluruhnya. Diam-diam memakai yang terakhir akan menyembunyikan
       bug di sisi pemecahan (dua subagent kebetulan meringkas dokumen sama).
    """
    per_berkas: list[tuple[Path, dict]] = []
    for p in berkas_list:
        hasil, pesan_error = _muat_berkas_hasil(p)
        if hasil is None:
            print(f"GAGAL: berkas hasil {p} {pesan_error}")
            print(
                "Manifest TIDAK ditulis, tidak ada berkas yang dihapus. "
                "Perbaiki bentuk berkas hasil lalu jalankan --serap lagi."
            )
            return None, 1
        per_berkas.append((p, hasil))

    sumber: dict[str, list[str]] = {}
    for p, hasil in per_berkas:
        for path_dok in hasil:
            sumber.setdefault(path_dok, []).append(p.name)

    konflik = {k: v for k, v in sumber.items() if len(v) > 1}
    if konflik:
        print(
            f"GAGAL: {len(konflik)} path dokumen konflik -- muncul di lebih dari "
            "satu berkas hasil (kemungkinan dua subagent kebetulan meringkas "
            "dokumen yang sama):"
        )
        for path_dok, files in konflik.items():
            print(f"  - {path_dok}: {', '.join(files)}")
        print("Manifest TIDAK ditulis, tidak ada berkas yang dihapus.")
        return None, 1

    gabungan: dict = {}
    for _, hasil in per_berkas:
        gabungan.update(hasil)
    return gabungan, 0


def _mode_serap(
    entri: list[dict], lama: dict | None, root: Path, path_eksplisit: Path | None,
) -> int:
    if path_eksplisit is not None:
        if not path_eksplisit.exists():
            print(
                f"GAGAL: berkas hasil {path_eksplisit} tidak ditemukan. Jalankan "
                f"--daftar-tugas, buat ringkasannya, baru --serap."
            )
            return 1
        berkas_list = [path_eksplisit]
    else:
        berkas_list = _temukan_berkas_hasil(root)
        if not berkas_list:
            print(
                f"GAGAL: tidak ada berkas hasil ditemukan di {root} (pola "
                f"{NAMA_HASIL} atau {POLA_HASIL_POTONGAN}). Langkah 2 (Claude "
                "Code meringkas, menulis berkas hasil) belum dikerjakan -- "
                "jalankan --daftar-tugas dulu, buat ringkasannya, baru --serap."
            )
            return 1

    hasil, kode_gagal = _gabung_berkas_hasil(berkas_list)
    if hasil is None:
        return kode_gagal

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

    # artefak sementara -- hapus HANYA bila serap bersih total (tanpa entri
    # ditolak/basi/tak-ditemukan). Sebagian gagal berarti operator masih
    # perlu memperbaiki hasil.json dan menjalankan ulang --serap; menghapus
    # artefak di titik itu membuang bukti dan memaksa mengulang seluruh sesi
    # ringkasan dari nol. Cakupan pembersihan MENCAKUP seluruh berkas
    # potongan tugas dan hasil (bukan cuma dua nama tetap) -- run --pecah
    # sebelumnya bisa saja meninggalkan potongan yang tidak lagi relevan
    # begitu manifest gabungan berhasil ditulis.
    if ditolak or basi or tak_ditemukan:
        nama_berkas = ", ".join(str(p) for p in berkas_list)
        print(
            f"Artefak dipertahankan ({nama_berkas}) -- ada entri "
            f"ditolak/basi/tak ditemukan. Perbaiki lalu jalankan --serap lagi."
        )
    else:
        artefak = set(berkas_list)
        artefak.add(root / NAMA_TUGAS)
        artefak.add(root / NAMA_HASIL)
        artefak.update(root.glob(POLA_TUGAS_POTONGAN))
        artefak.update(root.glob(POLA_HASIL_POTONGAN))
        for p in sorted(artefak):
            if p.exists():
                try:
                    p.unlink()
                    print(f"Dihapus: {p}")
                except OSError as exc:
                    print(f"PERINGATAN: gagal menghapus {p}: {exc}")

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
    ap.add_argument("--root", default=".", help="akar vault")
    ap.add_argument(
        "--pecah", type=_tipe_pecah, default=None, metavar="N",
        help=(
            "pakai bersama --daftar-tugas: pecah jadi berkas bernomor "
            f"{Path(NAMA_TUGAS).stem}.NNN.json, N dokumen per potongan, "
            "untuk difan-out ke banyak subagent"
        ),
    )

    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                       help="exit 1 bila index basi, tanpa menulis")
    mode.add_argument(
        "--daftar-tugas", nargs="?", const="", default=None, metavar="PATH",
        help=f"tulis dokumen yang perlu diringkas ke PATH (default {NAMA_TUGAS} di akar vault)",
    )
    mode.add_argument(
        "--serap", nargs="?", const="", default=None, metavar="PATH",
        help=(
            f"serap ringkasan dari PATH, atau (tanpa PATH) gabungkan seluruh "
            f"{NAMA_HASIL} dan {POLA_HASIL_POTONGAN} yang ditemukan di akar "
            f"vault, tulis {NAMA_INDEX}"
        ),
    )
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    path_index = root / NAMA_INDEX

    entri = scan_vault(root)
    lama = muat_index(path_index)

    if args.check:
        perlu = pilih_yang_perlu_diringkas(entri, lama, full=args.full)
        tersisa = _artefak_potongan_tersisa(root)
        if tersisa:
            print(f"PERINGATAN: {len(tersisa)} artefak potongan tugas/hasil tertinggal:")
            for p in tersisa:
                print(f"  - {p.name}")
        if perlu:
            print(f"BASI: {len(perlu)} dokumen belum terwakili di {NAMA_INDEX}")
            for e in perlu[:10]:
                print(f"  - {e['path']}")
            return 1
        print(f"SEGAR: {NAMA_INDEX} sinkron dengan {len(entri)} dokumen")
        return 0

    if args.daftar_tugas is not None:
        path_tugas = Path(args.daftar_tugas) if args.daftar_tugas else root / NAMA_TUGAS
        return _mode_daftar_tugas(
            entri, lama, path_tugas, root, full=args.full, pecah=args.pecah
        )

    if args.serap is not None:
        path_eksplisit = Path(args.serap) if args.serap else None
        return _mode_serap(entri, lama, root, path_eksplisit)

    return _mode_default(entri, lama, root)
