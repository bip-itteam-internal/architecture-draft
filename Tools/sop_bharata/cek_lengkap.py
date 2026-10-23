"""Bukti kelengkapan: setiap paragraf dan sel tabel dari tiap .docx harus muncul di dok posisinya."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_struktur import baca  # noqa: E402
from tulis_vault import POSISI, PETA  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sumber, keluar = sys.argv[1], sys.argv[2]


def inti(s):
    return re.sub(r"[^0-9a-z]+", "", s.lower())


BUANG = re.compile(r"^(Nama\s*:.*|Jabatan\s*:.*|(Disusun|Disetujui|Diperiksa|Dibuat)\s+oleh\s*:?|↓|→|\|)$", re.I)
total = hilang = 0
berkas = 0
for rel, folder, prefix, nama, unit in POSISI:
    with open(os.path.join(keluar, folder, "%s - SOP Posisi %s.md" % (prefix, nama)), encoding="utf-8") as f:
        dok = inti(f.read())
    d = os.path.join(sumber, rel)
    for fn in sorted(os.listdir(d)):
        if not fn.lower().endswith(".docx"):
            continue
        berkas += 1
        potong = []
        for b in baca(os.path.join(d, fn)):
            if b["jenis"] == "p":
                potong.append(b["teks"])
                potong.extend(b["kotak"])
            else:
                for r in b["baris"]:
                    for c in r:
                        potong.extend(c)
                potong.extend(b["kotak"])
        for t in potong:
            if not t or BUANG.match(t) or not inti(t):
                continue
            total += 1
            tanpa_nomor = re.sub(r"^\s*(?:[0-9]{1,2}|[IVX]{1,5})[.)]\s*", "", t).rstrip(": ")
            if inti(t) not in dok and not (len(t) <= 70 and inti(tanpa_nomor) and inti(tanpa_nomor) in dok):
                hilang += 1
                if hilang <= 15:
                    print("HILANG  %s\\%s :: %s" % (rel, fn, t[:120]))
with open(os.path.join(keluar, "Reference", PETA + ".md"), encoding="utf-8") as f:
    peta = inti(f.read())
form = [b for b in baca(os.path.join(sumber, "Form Inspeksi Implementasi SOP.docx"))]
tf = hf = 0
for b in form:
    isi = [b["teks"]] if b["jenis"] == "p" else [x for r in b["baris"] for c in r for x in c]
    for t in isi:
        if t and inti(t) and not BUANG.match(t):
            tf += 1
            if inti(t) not in peta:
                hf += 1
                print("HILANG  Form Inspeksi :: " + t[:120])
print("berkas=%d potongan teks=%d hilang=%d | form inspeksi: %d potongan, hilang=%d" % (berkas, total, hilang, tf, hf))
