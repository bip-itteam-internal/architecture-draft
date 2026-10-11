"""Isi VAULT-INDEX.hasil.001.json untuk dok SOP per posisi.

Ringkasan disusun dari isi dok itu sendiri (posisi, unit, daftar judul SOP di tabel "Daftar SOP"),
bukan ditebak dari judul berkas. Hash disalin dari berkas tugas.
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tulis_vault import POSISI, PETA  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
akar = sys.argv[1]
tugas = json.load(open(os.path.join(akar, "VAULT-INDEX.tugas.001.json"), encoding="utf-8"))
per_dok = {"%s/%s - SOP Posisi %s.md" % (f, p, n): (n, u) for _, f, p, n, u in POSISI}

HENTI = set("sop dan atau di ke dari yang untuk pada dengan proses saat atas per oleh secara dalam kepada serta the of".split())
PADANAN = {
    "Finance": ["finance", "keuangan"], "HRIS": ["HR", "SDM"], "GA": ["general affair", "GA"],
    "Marketing": ["marketing", "pemasaran"], "Manufacture": ["manufacture", "produksi"], "WH": ["warehouse", "gudang"],
    "QA": ["quality", "mutu"], "IT": ["IT", "tech development"], "Unlisted": ["kesekretariatan"],
}


def judul_sop(isi):
    """Judul dari tabel Daftar SOP di dok."""
    hasil = []
    m = re.search(r"## Daftar SOP\n\n\|[^\n]*\n\|[-|]+\n((?:\|[^\n]*\n)+)", isi)
    if not m:
        return hasil
    for baris in m.group(1).strip().split("\n"):
        sel = [s.strip() for s in re.split(r"(?<!\\)\|", baris)[1:-1]]
        if len(sel) >= 2:
            j = sel[1].replace("\\|", "|").replace("\\", "")
            j = re.sub(r"^\s*\d+(?:\.\d+)?\.?\s*", "", j)
            j = re.sub(r"^(SOP|PROTAP)\s+", "", j, flags=re.I)
            hasil.append(j.strip())
    return hasil


hasil = {}
for t in tugas["tugas"]:
    path, isi = t["path"], t["isi"]
    if path == "Reference/%s.md" % PETA:
        hasil[path] = {
            "ringkasan": (
                "Menjawab: posisi mana saja yang punya SOP resmi di kumpulan SOP BHARATA 2026, dok vault mana yang memuat "
                "salinannya, berapa dokumen per posisi, dan siapa (jabatan) penyusunnya. Menjelaskan juga apa yang sengaja "
                "tidak disalin (kontrak kerja per karyawan, templat slip gaji, gambar flowchart) dan memuat Form Inspeksi "
                "Implementasi SOP lintas departemen. Pintu masuk sebelum merancang fitur ERP yang menyentuh pekerjaan suatu posisi."
            ),
            "kata_kunci": ["SOP", "standar operasional prosedur", "SOP per posisi", "peta SOP", "SOP BHARATA 2026",
                           "inspeksi implementasi SOP", "jobdesk", "prosedur kerja", "posisi", "jabatan"],
            "hash": t["hash"],
        }
        continue
    if path not in per_dok:
        raise SystemExit("tugas di luar dok SOP sesi ini: " + path)
    nama, unit = per_dok[path]
    judul = judul_sop(isi)
    if not judul:
        raise SystemExit("tabel Daftar SOP tak terbaca: " + path)
    prefix = os.path.basename(path).split(" - ")[0]
    daftar = "; ".join(judul)
    ringkasan = (
        "Menjawab: apa saja SOP resmi posisi %s (unit %s) dan bagaimana langkah kerjanya menurut dokumen SOP BHARATA 2026. "
        "Memuat salinan apa adanya %d dokumen: %s. Tiap SOP berisi tujuan, ruang lingkup, penanggung jawab, rincian prosedur, "
        "dokumen pendukung, dan distribusinya; berguna untuk mengecek alur kerja posisi ini sebelum merancang fitur ERP yang menyentuhnya."
        % (nama, unit, len(judul), daftar)
    )
    hitung = collections.Counter()
    for j in judul:
        for k in set(re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}", j)):
            if k.lower() not in HENTI:
                hitung[k.lower()] += 1
    kunci = ["SOP", "SOP " + nama, nama, "prosedur kerja"]
    for k in PADANAN.get(prefix, []):
        if k.lower() not in [x.lower() for x in kunci]:
            kunci.append(k)
    for k, _ in sorted(hitung.items(), key=lambda x: (-x[1], x[0])):
        if len(kunci) >= 10:
            break
        if k not in [x.lower() for x in kunci] and k not in nama.lower().split():
            kunci.append(k)
    hasil[path] = {"ringkasan": ringkasan, "kata_kunci": kunci, "hash": t["hash"]}

if len(hasil) != len(tugas["tugas"]):
    raise SystemExit("jumlah hasil tak sama dengan tugas")
keluar = os.path.join(akar, tugas["berkas_keluaran"])
with open(keluar, "w", encoding="utf-8") as f:
    json.dump({"hasil": hasil}, f, ensure_ascii=False, indent=1)
print("ditulis", keluar, len(hasil), "entri")
for p in ("Finance System/Finance - SOP Posisi AR Staf.md", "Warehouse/WH - SOP Posisi Helper Packing.md"):
    print(json.dumps(hasil[p], ensure_ascii=False, indent=1))
