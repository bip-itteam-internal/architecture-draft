#!/usr/bin/env python3
"""Gerbang nomor ADR ganda (kit 1.35.0), dipanggil pre-push vault bila push menyentuh Decisions/ADR.

Nomor ADR "diklaim saat push": dua sesi yang menulis ADR berbarengan sama-sama mengambil nomor
bebas berikutnya, dan tak ada yang menolaknya. Diukur 2026-09-29: 10 nomor dipakai dua ADR
sekaligus (0058, 0061, 0065, 0066, 0077, 0078, 0088, 0090, 0097, 0117). Kutipan "ADR 0077" di
kode, PR, issue, dan aturan tim lalu ambigu tanpa satu pun galat.

Keputusan user 2026-09-29: pasangan LAMA tidak dinomori ulang (kutipannya sudah tersebar), cukup
ditandai; yang dicegah adalah pasangan BARU. Maka:
  - pasangan di IZIN (persis dua nama berkas itu) lolos;
  - nomor lain yang dipakai lebih dari satu berkas, atau berkas ketiga pada nomor berizin, DITOLAK.

Yang diperiksa adalah POHON COMMIT yang di-push (`git ls-tree <rev> Decisions/`), bukan working
tree: pohon vault dipakai bersama sesi lain, dan ADR mereka yang belum di-commit tak boleh
menggagalkan push orang lain.

Pemakaian: gerbang-adr.py --vault <akar vault> [--rev HEAD]
Keluar 0 = lolos, 1 = ada nomor ganda baru, 2 = galat pemakaian/git.
"""
import argparse
import re
import subprocess
import sys

POLA = re.compile(r"^ADR - (\d{4}) .+\.md$")

# Satu-satunya daftar pasangan ganda yang diterima. Mengganti JUDUL salah satu berkas ini wajib
# menyunting daftar ini juga (gerbang akan menyebut namanya), karena izin dipatok per nama berkas.
IZIN = {
    "0058": ("ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi.md",
             "ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri.md"),
    "0061": ("ADR - 0061 Jatah Cuti Tahunan Terbit Otomatis di Ulang Tahun Kontrak.md",
             "ADR - 0061 Kaizen Ada di Sistem tapi Tidak Dipakai untuk Otomasi KPI.md"),
    "0065": ("ADR - 0065 Payout yang Sudah Dibukukan Dokumen Lain Ditutup, Bukan Dibuat Ulang.md",
             "ADR - 0065 Template Form Generik untuk Realisasi Program (Culture).md"),
    "0066": ("ADR - 0066 Modul Kelola Program Culture.md",
             "ADR - 0066 Salinan Dokumen Retur Accurate + Pemindai Drift.md"),
    "0077": ("ADR - 0077 Koreksi Faktur via Impor Rekap Lengkap Mengalir ke Master-Data, Bukan Override per Baris.md",
             "ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak.md"),
    "0078": ("ADR - 0078 Fase Satu WMS Menggabungkan Matriks dan Paket Hak, Bukan Menggantikannya.md",
             "ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance.md"),
    "0088": ("ADR - 0088 Ambil Alih Sesi Live oleh Host Terjadwal dan Tutup Otomatis Akhir Shift.md",
             "ADR - 0088 Auto-Migrasi Padanan Perlengkapan Lewat ID Internal Accurate, Bukan Konfirmasi Manusia.md"),
    "0090": ("ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir.md",
             "ADR - 0090 KONSUMSI Eskalasi ke Direktur di Ambang Berbagi, Bukan Kebal.md"),
    "0097": ("ADR - 0097 Anggaran Iklan Dashboard Marketing Dibaca dari Master Anggaran Finance.md",
             "ADR - 0097 Kompensasi Shopee Susulan Ditahan dan Dicatat AR lewat Koreksi Manual ERP.md"),
    "0117": ("ADR - 0117 Realisasi Engagement Dilaporkan Pengerja per URL per Jenis Pekerjaan sampai Akhir Bulan KPI.md",
             "ADR - 0117 Riwayat Komplain Produk Terpusat di Satu Tabel, Register Tetap Dua.md"),
}


def daftar_adr(vault, rev):
    r = subprocess.run(["git", "-c", "core.fsmonitor=false", "-c", "core.quotepath=false", "ls-tree",
                        "--name-only", rev, "Decisions/"], cwd=vault, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "replace").strip() or "git ls-tree gagal")
    nama = [b.split("/", 1)[1] for b in r.stdout.decode("utf-8").splitlines() if "/" in b]
    return [n for n in nama if POLA.match(n)]


def periksa(berkas):
    """Kembalikan (daftar pelanggaran, nomor bebas berikutnya). Fungsi murni."""
    per_nomor = {}
    for b in berkas:
        per_nomor.setdefault(POLA.match(b).group(1), []).append(b)
    salah = []
    for nomor, isi in sorted(per_nomor.items()):
        if len(isi) < 2:
            continue
        if nomor in IZIN and sorted(isi) == sorted(IZIN[nomor]):
            continue
        salah.append((nomor, sorted(isi)))
    bebas = max((int(n) for n in per_nomor), default=0) + 1
    return salah, bebas


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", required=True)
    ap.add_argument("--rev", default="HEAD")
    a = ap.parse_args(argv)
    try:
        berkas = daftar_adr(a.vault, a.rev)
    except (RuntimeError, OSError) as e:
        print(f"[gerbang-adr] galat membaca pohon {a.rev}: {e}")
        return 2
    salah, bebas = periksa(berkas)
    if not salah:
        print(f"[gerbang-adr] lolos: {len(berkas)} ADR, nomor ganda hanya pasangan lama yang berizin")
        return 0
    for nomor, isi in salah:
        print(f"[gerbang-adr] GAGAL: nomor ADR {nomor} dipakai {len(isi)} berkas:")
        for b in isi:
            print(f"    Decisions/{b}")
        if nomor in IZIN:
            print("    Nomor ini pasangan lama berizin, tapi isinya kini berbeda (berkas ketiga, atau judul diganti).")
            print("    Judul diganti sengaja? sunting IZIN di .agent-kit/hooks/githooks/gerbang-adr.py.")
    print(f"[gerbang-adr] Beri ADR yang BARU nomor bebas berikutnya: {bebas:04d} (ganti nama berkas + judul"
          " di baris pertama + wikilink yang merujuknya), lalu push ulang.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
