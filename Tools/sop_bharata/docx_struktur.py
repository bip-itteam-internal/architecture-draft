"""Baca struktur .docx (paragraf + level daftar + tabel + kotak flowchart) tanpa pustaka luar.

Dipakai dua cara:
  python -I docx_struktur.py --dump <berkas.docx>      -> cetak struktur untuk diperiksa mata
  from docx_struktur import baca                       -> dipakai tulis_vault.py
"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"

# Elemen yang isinya bukan teks badan paragraf (gambar, kotak teks, objek).
LEWATI = {W + "drawing", W + "pict", W + "object", MC + "AlternateContent"}


def _rapikan(teks):
    return re.sub(r"\s+", " ", teks).strip()


def _teks_run(el):
    """Teks sebuah elemen, tanpa turun ke gambar/kotak teks."""
    potong = []

    def jalan(e):
        for anak in e:
            if anak.tag in LEWATI:
                continue
            if anak.tag == W + "t":
                potong.append(anak.text or "")
            elif anak.tag in (W + "tab", W + "br", W + "cr"):
                potong.append(" ")
            elif anak.tag == W + "noBreakHyphen":
                potong.append("-")
            else:
                jalan(anak)

    jalan(el)
    return "".join(potong)


def _kotak_teks(p):
    """Teks kotak flowchart di dalam paragraf, tanpa salinan mc:Fallback."""
    hasil = []

    def jalan(e, di_fallback):
        for anak in e:
            fb = di_fallback or anak.tag == MC + "Fallback"
            if anak.tag == W + "txbxContent":
                if not fb:
                    baris = [_rapikan(_teks_run(q)) for q in anak.iter(W + "p")]
                    teks = _rapikan(" ".join(b for b in baris if b))
                    if teks:
                        hasil.append(teks)
                continue
            jalan(anak, fb)

    jalan(p, False)
    return hasil


def _tebal_semua(p):
    run = [r for r in p.iter(W + "r") if _rapikan(_teks_run(r))]
    if not run:
        return False
    for r in run:
        rpr = r.find(W + "rPr")
        b = rpr.find(W + "b") if rpr is not None else None
        if b is None or b.get(W + "val") in ("0", "false"):
            return False
    return True


def _inden(ppr):
    """Inden kiri (twips) dari sebuah w:pPr, atau None."""
    if ppr is None:
        return None
    ind = ppr.find(W + "ind")
    if ind is None:
        return None
    v = ind.get(W + "left") or ind.get(W + "start")
    try:
        return int(v) if v is not None else None
    except ValueError:
        return None


def _muat_penomoran(z):
    """numId -> {ilvl: (numFmt, inden kiri)}."""
    peta = {}
    try:
        akar = ET.fromstring(z.read("word/numbering.xml"))
    except KeyError:
        return peta
    abstrak = {}
    for a in akar.findall(W + "abstractNum"):
        lv = {}
        for l in a.findall(W + "lvl"):
            f = l.find(W + "numFmt")
            lv[int(l.get(W + "ilvl", "0"))] = (
                f.get(W + "val") if f is not None else "decimal",
                _inden(l.find(W + "pPr")),
            )
        abstrak[a.get(W + "abstractNumId")] = lv
    for n in akar.findall(W + "num"):
        ref = n.find(W + "abstractNumId")
        if ref is not None:
            peta[n.get(W + "numId")] = abstrak.get(ref.get(W + "val"), {})
    return peta


def _muat_gaya(z):
    """styleId -> (numId, ilvl) bila gaya paragraf membawa penomoran."""
    peta = {}
    try:
        akar = ET.fromstring(z.read("word/styles.xml"))
    except KeyError:
        return peta
    for s in akar.findall(W + "style"):
        ppr = s.find(W + "pPr")
        if ppr is None:
            continue
        num = ppr.find(W + "numPr")
        if num is None:
            continue
        nid = num.find(W + "numId")
        lvl = num.find(W + "ilvl")
        peta[s.get(W + "styleId")] = (
            nid.get(W + "val") if nid is not None else None,
            int(lvl.get(W + "val")) if lvl is not None else 0,
        )
    return peta


def _paragraf(p, penomoran, gaya):
    ppr = p.find(W + "pPr")
    num_id, ilvl, sid = None, None, None
    if ppr is not None:
        ps = ppr.find(W + "pStyle")
        if ps is not None:
            sid = ps.get(W + "val")
            if sid in gaya:
                num_id, ilvl = gaya[sid]
        num = ppr.find(W + "numPr")
        if num is not None:
            nid = num.find(W + "numId")
            lvl = num.find(W + "ilvl")
            if nid is not None:
                num_id = nid.get(W + "val")
            ilvl = int(lvl.get(W + "val")) if lvl is not None else (ilvl or 0)
    if num_id in (None, "0"):
        num_id, ilvl = None, None
    fmt = None
    ind = _inden(ppr)
    if num_id is not None:
        fmt, ind_lvl = penomoran.get(num_id, {}).get(ilvl, ("decimal", None))
        if ind is None:
            ind = ind_lvl
    return {
        "jenis": "p",
        "teks": _rapikan(_teks_run(p)),
        "ilvl": ilvl,
        "num": num_id,
        "fmt": fmt,
        "ind": ind,
        "gaya": sid,
        "tebal": _tebal_semua(p),
        "kotak": _kotak_teks(p),
    }


def _tabel(t, penomoran, gaya):
    baris = []
    kotak = []
    for tr in t.findall(W + "tr"):
        sel = []
        for tc in tr.findall(W + "tc"):
            isi = []
            for p in tc.iter(W + "p"):
                d = _paragraf(p, penomoran, gaya)
                kotak.extend(d["kotak"])
                if d["teks"]:
                    isi.append(d["teks"])
            sel.append(isi)
        baris.append(sel)
    return {"jenis": "tbl", "baris": baris, "kotak": kotak}


def baca_header(jalur):
    """Daftar header dokumen; tiap header = daftar baris teksnya."""
    hasil = []
    with zipfile.ZipFile(jalur) as z:
        for nama in sorted(z.namelist()):
            if not re.match(r"word/header\d*\.xml$", nama):
                continue
            akar = ET.fromstring(z.read(nama))
            baris = [_rapikan(_teks_run(p)) for p in akar.iter(W + "p")]
            baris = [b for b in baris if b]
            if baris:
                hasil.append(baris)
    return hasil


def baca(jalur):
    """Daftar blok badan dokumen, berurutan: paragraf dan tabel."""
    with zipfile.ZipFile(jalur) as z:
        penomoran = _muat_penomoran(z)
        gaya = _muat_gaya(z)
        akar = ET.fromstring(z.read("word/document.xml"))
    badan = akar.find(W + "body")
    blok = []

    def jalan(e):
        for anak in e:
            if anak.tag == W + "p":
                blok.append(_paragraf(anak, penomoran, gaya))
            elif anak.tag == W + "tbl":
                blok.append(_tabel(anak, penomoran, gaya))
            elif anak.tag == W + "sdt":
                isi = anak.find(W + "sdtContent")
                if isi is not None:
                    jalan(isi)

    jalan(badan)
    return blok


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) == 3 and sys.argv[1] == "--dump":
        for b in baca(sys.argv[2]):
            if b["jenis"] == "tbl":
                print("[TBL %d baris]" % len(b["baris"]))
                for r in b["baris"][:6]:
                    print("    | " + " | ".join(" / ".join(s) for s in r))
                for k in b["kotak"]:
                    print("    [kotak] " + k)
                continue
            if not b["teks"] and not b["kotak"]:
                continue
            tanda = "L%s/%s/%s/%s" % (b["ilvl"], b["num"], b["fmt"], b["ind"]) if b["num"] else "- /%s" % b["ind"]
            print("%-22s %s%s %s" % (tanda, "B " if b["tebal"] else "  ", b["gaya"] or "", b["teks"][:110]))
            for k in b["kotak"]:
                print("    [kotak] " + k)
    else:
        print(__doc__)
