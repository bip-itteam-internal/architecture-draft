"""Salin SOP BHARATA 2026 (.docx) menjadi dok vault, satu dok per posisi + satu dok peta.

  python -I tulis_vault.py <folder SOP> <folder keluaran> [--vault <akar vault>]

Tanpa --vault: tulis ke <folder keluaran> dengan struktur folder vault (untuk diperiksa).
Dengan --vault: dipakai hanya untuk memeriksa tabrakan nama dan dok terkait yang sudah ada.
Isi SOP disalin apa adanya. Yang sengaja dibuang: nama orang di blok tanda tangan, dan
folder KONTRAK KERJA (data pribadi, bukan SOP).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_struktur import baca, baca_header  # noqa: E402

TANGGAL_EKSPOR = "2026-10-10"
PETA = "REF - SOP Bharata 2026 per Posisi"

# (folder sumber, folder vault, prefix, nama posisi, unit)
POSISI = [
    (r"BEAUTYHACKS\SUPERVISOR BEAUTYHACKS", "Marketing", "Marketing", "Supervisor Beautyhacks", "Marketing Beautyhacks"),
    (r"BEAUTYHACKS\LEADER BEAUTYHACKS", "Marketing", "Marketing", "Leader Beautyhacks", "Marketing Beautyhacks"),
    (r"BEAUTYHACKS\ADVERTISER META BEAUTYHACKS", "Marketing", "Marketing", "Advertiser Meta Beautyhacks", "Marketing Beautyhacks"),
    (r"BEAUTYHACKS\MARKETPLACE BEAUTYHACKS", "Marketing", "Marketing", "Marketplace Beautyhacks", "Marketing Beautyhacks"),
    (r"BEAUTYHACKS\SHOPEE", "Marketing", "Marketing", "Shopee Beautyhacks", "Marketing Beautyhacks"),
    (r"BEAUTYHACKS\AFFILIATE BEAUTYHACKS", "Marketing", "Marketing", "Affiliate Beautyhacks", "Marketing Beautyhacks"),
    (r"BEAUTYHACKS\BUZZER BEAUTYHACKS", "Marketing", "Marketing", "Buzzer Beautyhacks", "Marketing Beautyhacks"),
    (r"BEAUTYHACKS\CS MARKETPLACE SUPPORT", "Marketing", "Marketing", "CS Marketplace Support Beautyhacks", "Marketing Beautyhacks"),
    (r"BEAUTYHACKS\CS META BEAUTYHACKS", "Marketing", "Marketing", "CS Meta Beautyhacks", "Marketing Beautyhacks"),
    (r"BEAUTYHACKS\HOSTLIVE BEAUTYHACKS", "Marketing", "Marketing", "Host Live Beautyhacks", "Marketing Beautyhacks"),
    (r"BEAUTYHACKS\INTERNAL CONTENT CREATOR", "Marketing", "Marketing", "Internal Content Creator Beautyhacks", "Marketing Beautyhacks"),
    (r"KYURA\SUPERVISOR KYURA", "Marketing", "Marketing", "Supervisor Kyura", "Marketing Kyura"),
    (r"KYURA\LEADER ADV TIKTOK KYURA", "Marketing", "Marketing", "Leader Advertiser TikTok Kyura", "Marketing Kyura"),
    (r"KYURA\ADVERTISER META KYURA", "Marketing", "Marketing", "Advertiser Meta Kyura", "Marketing Kyura"),
    (r"KYURA\ADVERTISER SHOPEE KYURA", "Marketing", "Marketing", "Advertiser Shopee Kyura", "Marketing Kyura"),
    (r"KYURA\BUZZER KYURA", "Marketing", "Marketing", "Buzzer Kyura", "Marketing Kyura"),
    (r"KYURA\CS MARKETPLACE KYURA", "Marketing", "Marketing", "CS Marketplace Kyura", "Marketing Kyura"),
    (r"KYURA\HOSTLIVE KYURA", "Marketing", "Marketing", "Host Live Kyura", "Marketing Kyura"),
    (r"KYURA\HOSTLIVE GLOWBOOSTER", "Marketing", "Marketing", "Host Live Glowbooster", "Marketing Kyura"),
    (r"KYURA\INTERNAL CONTENT CREATOR", "Marketing", "Marketing", "Internal Content Creator Kyura", "Marketing Kyura"),
    (r"CRM", "Marketing", "Marketing", "CRM", "CRM"),
    (r"FINANCE\SUPERVISOR FAT", "Finance System", "Finance", "Supervisor FAT", "Finance"),
    (r"FINANCE\SENIOR ACCOUNTING", "Finance System", "Finance", "Senior Accounting", "Finance"),
    (r"FINANCE\JUNIOR ACCOUNTING", "Finance System", "Finance", "Junior Accounting", "Finance"),
    (r"FINANCE\ACCOUNTING STAF", "Finance System", "Finance", "Accounting Staf", "Finance"),
    (r"FINANCE\FINANCE-AP", "Finance System", "Finance", "Finance AP", "Finance"),
    (r"FINANCE\AR LEADER", "Finance System", "Finance", "AR Leader", "Finance"),
    (r"FINANCE\AR STAF", "Finance System", "Finance", "AR Staf", "Finance"),
    (r"FINANCE\ADMIN SALES", "Finance System", "Finance", "Admin Sales", "Finance"),
    (r"FINANCE\COST CONTROL", "Finance System", "Finance", "Cost Control", "Finance"),
    (r"FINANCE\TAX OFFICER", "Finance System", "Finance", "Tax Officer", "Finance"),
    (r"HRGA\SUPERVISOR HRGA", "Human Resource Information System", "HRIS", "Supervisor HRGA", "HRGA"),
    (r"HRGA\HRD\RECRUITMENT", "Human Resource Information System", "HRIS", "Recruitment", "HRGA, HRD"),
    (r"HRGA\HRD\PERSONALIA", "Human Resource Information System", "HRIS", "Personalia", "HRGA, HRD"),
    (r"HRGA\HRD\TRAINING DEVELOPMENT", "Human Resource Information System", "HRIS", "Training Development", "HRGA, HRD"),
    (r"HRGA\HRD\ORGANIZATIONAL DEVELOPMENT", "Human Resource Information System", "HRIS", "Organizational Development", "HRGA, HRD"),
    (r"HRGA\GA\GENERAL AFFAIR", "General Affairs", "GA", "General Affair", "HRGA, GA"),
    (r"HRGA\GA\ADMIN GENERAL SERVICE", "General Affairs", "GA", "Admin General Service", "HRGA, GA"),
    (r"HRGA\GA\BUILDING & MAINTENANCE", "General Affairs", "GA", "Building & Maintenance", "HRGA, GA"),
    (r"HRGA\GA\SECURITY", "General Affairs", "GA", "Security", "HRGA, GA"),
    (r"HRGA\GA\OB-OG", "General Affairs", "GA", "OB-OG", "HRGA, GA"),
    (r"PROCUREMENT", "General Affairs", "GA", "Procurement", "Procurement"),
    (r"KESEKRETARIATAN\ASISTEN EKSEKUTIF\ASISTEN EKSEKUTIF INTERNAL", "Unknown or not listed", "Unlisted", "Asisten Eksekutif Internal", "Kesekretariatan"),
    (r"KESEKRETARIATAN\INTERNAL CONTROL", "Unknown or not listed", "Unlisted", "Internal Control", "Kesekretariatan"),
    (r"KESEKRETARIATAN\LEGAL", "Unknown or not listed", "Unlisted", "Legal", "Kesekretariatan"),
    (r"KESEKRETARIATAN\COMPANY BRANDING", "Unknown or not listed", "Unlisted", "Company Branding", "Kesekretariatan"),
    (r"KESEKRETARIATAN\GRAPHIC DESIGNER", "Unknown or not listed", "Unlisted", "Graphic Designer", "Kesekretariatan"),
    (r"KESEKRETARIATAN\VIDEO EDITOR", "Unknown or not listed", "Unlisted", "Video Editor", "Kesekretariatan"),
    (r"KESEKRETARIATAN\VIDEOGRAPHER", "Unknown or not listed", "Unlisted", "Videographer", "Kesekretariatan"),
    (r"KESEKRETARIATAN\R&D-APOTEKER", "Quality & Regulatory", "QA", "R&D Apoteker", "Kesekretariatan"),
    (r"QUALITY\SUPERVISOR QUALITY", "Quality & Regulatory", "QA", "Supervisor Quality", "Quality"),
    (r"QUALITY\QUALITY CONTROL", "Quality & Regulatory", "QA", "Quality Control", "Quality"),
    (r"QUALITY\QUALITY TEKNOLOGI PANGAN", "Quality & Regulatory", "QA", "Quality Teknologi Pangan", "Quality"),
    (r"MANUFACTURE\PPIC", "Manufacture", "Manufacture", "PPIC", "Manufacture"),
    (r"MANUFACTURE\PRODUKSI\LEADER PRODUKSI", "Manufacture", "Manufacture", "Leader Produksi", "Manufacture, Produksi"),
    (r"MANUFACTURE\PRODUKSI\ADMIN PRODUKSI", "Manufacture", "Manufacture", "Admin Produksi", "Manufacture, Produksi"),
    (r"MANUFACTURE\PRODUKSI\OPERATOR PRODUKSI", "Manufacture", "Manufacture", "Operator Produksi", "Manufacture, Produksi"),
    (r"MANUFACTURE\WAREHOUSE\LEADER WAREHOUSE", "Warehouse", "WH", "Leader Warehouse", "Manufacture, Warehouse"),
    (r"MANUFACTURE\WAREHOUSE\ADMIN WAREHOUSE", "Warehouse", "WH", "Admin Warehouse", "Manufacture, Warehouse"),
    (r"MANUFACTURE\WAREHOUSE\STAF WAREHOUSE", "Warehouse", "WH", "Staf Warehouse", "Manufacture, Warehouse"),
    (r"MANUFACTURE\WAREHOUSE PACKING\LEADER WAREHOUSE PACKING", "Warehouse", "WH", "Leader Warehouse Packing", "Manufacture, Warehouse Packing"),
    (r"MANUFACTURE\WAREHOUSE PACKING\ADMIN WAREHOUSE PACKING", "Warehouse", "WH", "Admin Warehouse Packing", "Manufacture, Warehouse Packing"),
    (r"MANUFACTURE\WAREHOUSE PACKING\HELPER PACKING", "Warehouse", "WH", "Helper Packing", "Manufacture, Warehouse Packing"),
    (r"TECH DEVELOPMENT", "IT", "IT", "Tech Development", "Tech Development"),
]

# Berkas non-docx di folder posisi: dicatat, tidak disalin.
CATATAN_BERKAS_LAIN = {
    r"HRGA\HRD\PERSONALIA": [
        "`Template SLIP GAJI PT.Bharata.xlsx`: templat slip gaji (spreadsheet), tidak disalin.",
        "`CEKLIS AUDIT HRD PERSONALIA-*.zip`: arsip ceklis audit HRD Personalia, tidak dibuka dan tidak disalin.",
        "Subfolder `KONTRAK KERJA`: kontrak kerja per karyawan (PDF). Itu data pribadi, bukan SOP, dan repo vault ini publik, jadi **sengaja tidak disalin** dan tidak didaftar di sini.",
    ],
    r"QUALITY\QUALITY TEKNOLOGI PANGAN": [
        "`1. INSPEKSI DIRI.pdf` berbentuk PDF: teksnya diambil lewat `pdftotext`, lalu butir bernomor dipecah per baris. Dua tabel penutupnya (riwayat perubahan, distribusi) disusun ulang dari teks hasil ekstraksi karena kolomnya tercampur.",
    ],
}

DOK_TERKAIT = {
    "GA - SOP Posisi Procurement": ["GA - SOP Procurement"],
}

KEPALA = {
    "tujuan": "Tujuan",
    "ruang lingkup": "Ruang Lingkup",
    "penanggung jawab": "Penanggung Jawab",
    "tanggung jawab": "Tanggung Jawab",
    "definisi": "Definisi",
    "referensi": "Referensi",
    "rincian prosedur": "Rincian Prosedur",
    "prosedur": "Prosedur",
    "sla/target waktu": "SLA/Target Waktu",
    "sla / target waktu": "SLA/Target Waktu",
    "dokumen pendukung atau lampiran": "Dokumen Pendukung atau Lampiran",
    "dokumen pendukung atau lampiran (optional)": "Dokumen Pendukung atau Lampiran (Optional)",
    "dokumen pendukung dan formulir": "Dokumen Pendukung dan Formulir",
    "dokumen pendukung": "Dokumen Pendukung",
    "dokumen lampiran": "Dokumen Lampiran",
    "alat/dokumen/formulir pendukung": "Alat/Dokumen/Formulir Pendukung",
    "catatan perubahan": "Catatan Perubahan",
    "riwayat perubahan": "Riwayat Perubahan",
    "distribusi dokumen": "Distribusi Dokumen",
    "pihak terkait": "Pihak Terkait",
    "dokumen terkait": "Dokumen Terkait (SOP)",
}
AWALAN_NOMOR = re.compile(r"^\s*(?:[0-9]{1,2}|[IVX]{1,5})[.)]\s*")
FLOWCHART = re.compile(r"^(flow\s*chart|diagram alir|bagan alir)\b", re.I)
TERURUT = {"decimal", "lowerLetter", "upperLetter", "lowerRoman", "upperRoman", "decimalZero"}


def aman(teks, baris=False):
    """Lindungi teks sumber dari tafsir Markdown/Obsidian tanpa mengubah isinya."""
    teks = teks.replace("\\", "\\\\")
    teks = re.sub(r"<(?=[A-Za-z/!])", r"\\<", teks)
    teks = re.sub(r"(^|\s)#(?=[A-Za-z])", r"\1\\#", teks)
    teks = teks.replace("[[", "\\[\\[").replace("%%", "\\%\\%")
    teks = re.sub(r"(?<!\\)\*", r"\\*", teks)
    teks = re.sub(r"(?<![\\\w])_|_(?!\w)", r"\\_", teks)
    teks = teks.replace("`", "'")
    if not baris:
        return teks
    if re.match(r"^(\d+)([.)])\s", teks):  # "6.1 Invoice" aman; "6. Invoice" akan dinomori ulang
        teks = re.sub(r"^(\d+)([.)])", r"\1\\\2", teks)
    if re.match(r"^[-+>]\s", teks):
        teks = "\\" + teks
    return teks


def kepala_bagian(b):
    """Nama bagian kanonik bila paragraf ini kepala bagian, selain itu None."""
    t = b["teks"]
    if not t or len(t) > 70:
        return None
    bernomor = bool(AWALAN_NOMOR.match(t))
    inti = AWALAN_NOMOR.sub("", t).strip().rstrip(":").strip()
    kunci = re.sub(r"\s+", " ", inti.lower())
    penanda = (
        (b["num"] and b["ilvl"] == 0 and b["fmt"] in TERURUT)
        or b["tebal"]
        or bernomor
        or (inti.isupper() and len(inti) > 3)
    )
    if not penanda:
        return None
    if kunci in KEPALA:
        return KEPALA[kunci]
    if FLOWCHART.match(inti):
        return inti
    if bernomor and inti.isupper() and len(inti) > 3 and re.match(r"^\s*[IVX]{1,5}\.", t):
        return t.strip()  # apa adanya: "I." bisa angka romawi, bisa juga huruf urut (A..I)
    return None


def tabel_md(baris):
    lebar = max((len(r) for r in baris), default=0)
    if lebar == 0:
        return []
    keluar = []
    for i, r in enumerate(baris):
        sel = []
        for c in r + [[]] * (lebar - len(r)):
            isi = "<br>".join(aman(x).replace("|", "\\|") for x in c if not re.match(r"^Nama\s*:", x))
            sel.append(isi if isi else " ")
        keluar.append("| " + " | ".join(sel) + " |")
        if i == 0:
            keluar.append("|" + "---|" * lebar)
    return keluar


def tanda_tangan(tbl):
    """Tabel tanda tangan -> {'Disusun oleh': 'Jabatan', ...} atau None."""
    rata = [" ".join(c) for r in tbl["baris"] for c in r]
    if not any(re.search(r"\b(disusun|dibuat)\s+oleh\b", x, re.I) for x in rata):
        return None
    baris_sel = [x for r in tbl["baris"] for c in r for x in c]
    if len(tbl["baris"]) > 4 or not any(re.match(r"^(Nama|Jabatan)\s*:", x) for x in baris_sel):
        return None  # tabel formulir biasa yang kebetulan memuat "dibuat oleh"
    hasil = {}
    label = None
    for r in tbl["baris"]:
        teks_baris = [" ".join(c).strip() for c in r]
        if any(re.search(r"\boleh\b", x, re.I) for x in teks_baris) and not any("Jabatan" in x for x in teks_baris):
            label = [x.rstrip(" :") for x in teks_baris]
            continue
        if label is None:
            continue
        for i, c in enumerate(r):
            for x in c:
                m = re.match(r"^Jabatan\s*:\s*(.+)$", x)
                if m and i < len(label) and label[i]:
                    hasil.setdefault(label[i], m.group(1).strip())
    return hasil


class Daftar:
    """Susun paragraf bertingkat jadi daftar Markdown (lihat catatan tumpukan di bawah)."""

    def __init__(self):
        self.baris = []
        self.tumpuk = []  # ("n", numId, ilvl, fmt, inden) atau ("p",)
        self.hitung = {}  # kedalaman -> nomor terakhir
        self.geser = 0  # sesudah tabel, daftar dilanjutkan rata kiri supaya tidak terbaca blok kode
        self.baru_tabel = False

    def sesudah_tabel(self):
        self.baru_tabel = True

    def _tulis(self, dalam, penanda, teks, tebal):
        if self.baru_tabel:
            self.geser = dalam
            self.baru_tabel = False
        elif dalam < self.geser:
            self.geser = dalam
        dalam -= self.geser
        isi = aman(teks, baris=True)
        if tebal and len(teks) <= 90:
            isi = "**" + isi + "**"
        self.baris.append("    " * dalam + penanda + " " + isi)

    def paragraf(self, b):
        t = b["teks"]
        if t in ("↓", "→", "|"):
            return
        if b["num"]:
            kunci = ("n", b["num"], b["ilvl"], b["fmt"], b["ind"])
            pos = None
            for i in range(len(self.tumpuk) - 1, -1, -1):
                e = self.tumpuk[i]
                if e[0] == "n" and (e[1:3] == kunci[1:3] or e[2:] == kunci[2:]):
                    pos = i
                    break
            hitung = 0
            if pos is not None:
                hitung = self.hitung.get(pos, 0)
                del self.tumpuk[pos:]
            else:
                for i, e in enumerate(self.tumpuk):
                    if e[0] == "n" and e[1] == kunci[1] and e[2] > kunci[2]:
                        del self.tumpuk[i:]
                        break
            self.tumpuk.append(kunci)
            dalam = len(self.tumpuk) - 1
            for k in [k for k in self.hitung if k > dalam]:
                del self.hitung[k]
            self.hitung[dalam] = hitung + 1
            penanda = ("%d." % self.hitung[dalam]) if b["fmt"] in TERURUT else "-"
            self._tulis(dalam, penanda, t, b["tebal"])
            return
        for i in range(len(self.tumpuk) - 1, -1, -1):
            if self.tumpuk[i][0] == "p":
                del self.tumpuk[i:]
                break
        dalam = len(self.tumpuk)
        for k in [k for k in self.hitung if k >= dalam]:
            del self.hitung[k]
        label = t.endswith(":") or (b["tebal"] and len(t) <= 90)
        self._tulis(dalam, "-", t, b["tebal"])
        if label:
            self.tumpuk.append(("p",))

    def putus(self):
        self.tumpuk = []
        self.hitung = {}


def susun_badan(blok):
    """Blok satu bagian -> baris Markdown."""
    ada_daftar = any(b["jenis"] == "p" and b["num"] for b in blok)
    ada_tabel = any(b["jenis"] == "tbl" for b in blok)
    ada_label = any(b["jenis"] == "p" and b["teks"].endswith(":") for b in blok)
    keluar = []
    if not ada_daftar and not ada_tabel and not ada_label:
        semua_kotak = []
        for b in blok:
            if b["teks"] and b["teks"] not in ("↓", "→"):
                isi = aman(b["teks"], baris=True)
                keluar.append(("**%s**" % isi) if b["tebal"] and len(b["teks"]) <= 90 else isi)
                keluar.append("")
            semua_kotak.extend(b["kotak"])
        if semua_kotak:
            keluar.extend("%d. %s" % (i + 1, aman(k)) for i, k in enumerate(semua_kotak))
            keluar.append("")
        return keluar
    d = Daftar()
    kotak = []

    def buang():
        if d.baris:
            keluar.extend(d.baris)
            keluar.append("")
            d.baris = []

    for b in blok:
        if b["jenis"] == "tbl" and len(b["baris"]) == 1 and len(b["baris"][0]) == 1:
            # Tabel satu sel = kotak (mis. langkah flowchart yang digambar pakai tabel).
            isi = " ".join(x for x in b["baris"][0][0] if not re.match(r"^Nama\s*:", x))
            if isi:
                d.paragraf({"teks": isi, "num": None, "tebal": False})
            kotak.extend(b["kotak"])
            continue
        if b["jenis"] == "tbl":
            buang()
            d.sesudah_tabel()
            keluar.extend(tabel_md(b["baris"]))
            keluar.append("")
            kotak.extend(b["kotak"])
            continue
        if b["teks"]:
            d.paragraf(b)
        kotak.extend(b["kotak"])
    buang()
    if kotak:
        keluar.extend("%d. %s" % (i + 1, aman(k)) for i, k in enumerate(kotak))
        keluar.append("")
    return keluar


def info_header(jalur, judul_berkas):
    """No.Doc dan Tanggal dari header yang judulnya paling cocok dengan nama berkas."""
    kata = set(re.findall(r"[a-z]{3,}", judul_berkas.lower()))
    terbaik, skor_terbaik = None, 0
    for baris in baca_header(jalur):
        potong = []
        for i, x in enumerate(baris):
            if re.match(r"^STANDAR OPERASIONAL PROSEDUR$", x.strip(), re.I) and i > 0:
                potong.append(i)
        blok = [baris]
        if potong:
            tepi = [0] + potong + [len(baris)]
            blok = [baris[tepi[k]:tepi[k + 1]] for k in range(len(tepi) - 1)]
        for bl in blok:
            gabung = " ".join(bl).lower()
            skor = len(kata & set(re.findall(r"[a-z]{3,}", gabung)))
            if skor > skor_terbaik:
                terbaik, skor_terbaik = bl, skor
    info = {}
    if terbaik and skor_terbaik >= 2:
        for x in terbaik:
            m = re.match(r"^No\.?\s*Doc\w*\s*:\s*(.*)$", x, re.I)
            if m and m.group(1).strip():
                info["nodoc"] = m.group(1).strip()
            m = re.match(r"^Tanggal\s*:\s*(.*)$", x, re.I)
            if m and m.group(1).strip():
                info["tanggal"] = m.group(1).strip()
            m = re.match(r"^Revisi\s*:\s*(\d+)$", x, re.I)
            if m:
                info["revisi"] = m.group(1)
    return info


def urut_berkas(nama):
    m = re.match(r"^\s*(\d+)(?:\.(\d+))?", nama)
    return (0, int(m.group(1)), int(m.group(2) or 0), nama.lower()) if m else (1, 0, 0, nama.lower())


def judul_dari_berkas(nama):
    return re.sub(r"\s+", " ", os.path.splitext(nama)[0].replace("_", " ")).strip()


def salin_sop(jalur):
    """Satu .docx -> dict(judul, info, ttd, baris, statistik)."""
    nama = os.path.basename(jalur)
    judul = judul_dari_berkas(nama)
    blok = baca(jalur)
    ttd = {}
    label_ttd = None
    bagian = [(None, [])]
    for b in blok:
        if b["jenis"] == "tbl":
            t = tanda_tangan(b)
            if t is not None:
                ttd.update(t)
                continue
            bagian[-1][1].append(b)
            continue
        if re.match(r"^Nama\s*:", b["teks"]):
            continue
        m = re.match(r"^Jabatan\s*:\s*(.+)$", b["teks"])
        if m:
            if label_ttd:
                ttd.setdefault(label_ttd, m.group(1).strip())
            continue
        if re.match(r"^(Disusun|Disetujui|Diperiksa|Dibuat)\s+oleh\s*:?$", b["teks"], re.I):
            label_ttd = b["teks"].rstrip(" :")
            continue
        k = kepala_bagian(b)
        if k:
            bagian.append((k, []))
            if b["kotak"]:
                bagian[-1][1].append(dict(b, teks=""))
            continue
        if b["teks"] or b["kotak"]:
            bagian[-1][1].append(b)
    baris = []
    n_bagian = 0
    for nama_bagian, isi in bagian:
        badan = susun_badan(isi)
        if nama_bagian is None:
            if badan:
                baris.extend(badan)
            continue
        n_bagian += 1
        baris.append("### " + aman(nama_bagian))
        baris.append("")
        if FLOWCHART.match(nama_bagian) and any(b.get("kotak") for b in isi):
            baris.append("*Teks kotak flowchart, menurut urutan tersimpan di dokumen. Panah dan percabangan tidak ikut tersalin.*")
            baris.append("")
        if badan:
            baris.extend(badan)
        else:
            baris.append("*(Kosong di dokumen sumber, atau isinya berupa gambar.)*")
            baris.append("")
    n_teks = sum(len(b.get("teks", "")) for b in blok if b["jenis"] == "p")
    return {
        "berkas": nama,
        "judul": judul,
        "info": info_header(jalur, judul),
        "ttd": ttd,
        "baris": baris,
        "n_bagian": n_bagian,
        "n_teks": n_teks,
        "n_tabel": sum(1 for b in blok if b["jenis"] == "tbl"),
    }


PDF_INSPEKSI = {"jalur": None}
REL_PDF_INSPEKSI = r"QUALITY\QUALITY TEKNOLOGI PANGAN"
BUANG_PDF = re.compile(
    r"^(STANDARD OPERATIONAL PROCEDURES|INSPEKSI DIRI|No\. Doc\s*:.*|Revisi\s*:.*|Tanggal\s*:.*|Halaman\s*:.*|"
    r"Disusun oleh|Approved by|Nama\s*:.*|Jabatan\s*:.*)$"
)


def salin_pdf_inspeksi(jalur_txt):
    """SOP Inspeksi Diri (PDF, sudah lewat pdftotext) -> bentuk yang sama dengan salin_sop."""
    with open(jalur_txt, encoding="utf-8") as f:
        mentah = [re.sub(r"\s+", " ", x).strip() for x in f.read().replace("\f", "\n").split("\n")]
    info = {}
    for x in mentah:
        m = re.match(r"^No\. Doc\s*:\s*(.+)$", x)
        if m:
            info.setdefault("nodoc", m.group(1))
        m = re.match(r"^Tanggal\s*:\s*(.+)$", x)
        if m:
            info.setdefault("tanggal", m.group(1))
        m = re.match(r"^Revisi\s*:\s*(\d+)$", x)
        if m:
            info.setdefault("revisi", m.group(1))
    baris = []
    n_bagian = 0
    for x in mentah:
        if not x or BUANG_PDF.match(x):
            continue
        m = re.match(r"^(\d)\. ([A-Z][A-Z ]+?)(?: (?=\d\.\d)(.*))?$", x)
        if not m:
            continue  # sisa tabel penutup, disusun ulang di bawah
        nomor, judul, sisa = m.group(1), m.group(2).strip(), m.group(3) or ""
        if nomor in ("8", "9"):
            continue
        n_bagian += 1
        baris.append("### " + KEPALA.get(judul.lower(), judul.title()))
        baris.append("")
        for butir in re.split(r"(?<![\d.])(?=\d\.\d{1,2}\.(?:\d{1,2}\.)? )", sisa):
            butir = butir.strip()
            if not butir:
                continue
            tingkat = len(re.match(r"^((?:\d{1,2}\.)+)", butir).group(1).strip(".").split(".")) - 2
            baris.append("    " * max(0, tingkat) + "- " + aman(butir))
        baris.append("")
    baris += [
        "### Riwayat Perubahan", "",
        "| Revisi | No. Dokumen | Tanggal | Alasan |", "|---|---|---|---|",
        "| 00 | PM/SOP/007/00 | 25 Agustus 2025 | Baru |", "",
        "### Catatan Distribusi Dokumen", "",
        "| No | Penerima | Copy |", "|---|---|---|",
        "| 01 | Bagian Penanggung Jawab Teknis/QA | 1 |",
        "| 02 | Bagian Pengawasan Mutu | 1 |",
        "| 03 | Pimpinan Perusahaan | 1 |",
        "| 04 | Tim Inspeksi Diri | 1 |",
        "| 05 | Bagian Produksi | 1 |", "",
    ]
    gabung = " ".join(mentah)
    for wajib in ("8. RIWAYAT PERUBAHAN", "00 PM/SOP/007/00 25 Agustus 2025", "Baru", "9. CATATAN DISTRIBUSI DOKUMEN",
                  "01 Bagian Penanggung Jawab Teknis/QA", "02 Bagian Pengawasan Mutu", "03 Pimpinan Perusahaan",
                  "04 Tim Inspeksi Diri", "05 Bagian Produksi", "Copy 1 1 1 1 1"):
        if wajib not in gabung:
            raise SystemExit("PDF Inspeksi Diri berubah, tabel penutup tak cocok lagi: " + wajib)
    return {
        "berkas": "1. INSPEKSI DIRI.pdf", "judul": "1. INSPEKSI DIRI", "info": info,
        "ttd": {"Disusun oleh": "Penanggung Jawab Teknis", "Disetujui oleh": "Direktur"},
        "baris": baris, "n_bagian": n_bagian + 2, "n_teks": len(gabung), "n_tabel": 2,
    }


def tulis_posisi(sumber, rel, folder, prefix, nama, unit, akar_keluar, akar_vault):
    d = os.path.join(sumber, rel)
    berkas = sorted((f for f in os.listdir(d) if f.lower().endswith(".docx")), key=urut_berkas)
    sop = [salin_sop(os.path.join(d, f)) for f in berkas]
    if rel == REL_PDF_INSPEKSI and PDF_INSPEKSI["jalur"]:
        sop.insert(0, salin_pdf_inspeksi(PDF_INSPEKSI["jalur"]))
    judul_dok = "%s - SOP Posisi %s" % (prefix, nama)
    penyusun = []
    penyetuju = []
    for s in sop:
        for k, v in s["ttd"].items():
            sasaran = penyusun if re.search(r"disusun|dibuat", k, re.I) else penyetuju if re.search(r"disetujui", k, re.I) else None
            v = re.sub(r"\s+", " ", v).strip()
            if sasaran is not None and v and v.lower() not in [x.lower() for x in sasaran]:
                sasaran.append(v)
    rel_tampil = "SOP BHARATA 2026/" + rel.replace("\\", "/")
    L = []
    L.append("## Deskripsi")
    L.append("")
    L.append(
        "*Salinan **%d dokumen SOP** posisi **%s** (unit %s) PT Bharata Internasional Pharmaceutical, "
        "diambil dari kumpulan \"SOP BHARATA 2026\". Isinya proses kerja yang dijalankan orang, disalin apa adanya "
        "dari dokumen sumber, bukan gambaran perilaku sistem ERP.*" % (len(sop), aman(nama), aman(unit))
    )
    L.append("")
    L.append("- **Status**: 🟡 **Rekaman SOP (proses bisnis, non-kode).** Kepatuhan sistem ERP terhadap SOP ini belum dipetakan (TBD).")
    L.append("- **Sumber**: `%s` (ekspor Google Drive %s, di luar repo). Dokumen sumber yang menang bila salinan ini berbeda." % (rel_tampil, TANGGAL_EKSPOR))
    if penyusun:
        L.append("- **Disusun oleh (jabatan)**: %s" % ", ".join(aman(x) for x in penyusun))
    if penyetuju:
        L.append("- **Disetujui oleh (jabatan)**: %s" % ", ".join(aman(x) for x in penyetuju))
    L.append("- **Peta seluruh posisi**: [[%s]]" % PETA)
    L.append("")
    L.append("## Daftar SOP")
    L.append("")
    L.append("| No | Dokumen | No. dokumen | Tanggal |")
    L.append("|---|---|---|---|")
    for i, s in enumerate(sop, 1):
        L.append("| %d | %s | %s | %s |" % (
            i, aman(s["judul"]).replace("|", "\\|"),
            aman(s["info"].get("nodoc", "")).replace("|", "\\|") or " ",
            aman(s["info"].get("tanggal", "")) or " ",
        ))
    L.append("")
    L.append("## Catatan Penyalinan")
    L.append("")
    L.append("- Teks, urutan langkah, dan tabel disalin apa adanya, termasuk salah ketik di dokumen sumber. Tidak ada yang dirangkum atau ditambah.")
    L.append("- Nama orang di blok tanda tangan sengaja tidak disalin; yang dicatat hanya jabatannya.")
    L.append("- Flowchart berupa gambar: yang tersalin hanya teks kotaknya. Bentuk alur yang sah tetap di dokumen sumber.")
    L.append("- Kolom \"No. dokumen\" dan \"Tanggal\" diambil dari kop dokumen; kosong berarti kopnya tidak memuat nilai itu.")
    for c in CATATAN_BERKAS_LAIN.get(rel, []):
        L.append("- " + c)
    L.append("")
    for s in sop:
        L.append("## " + aman(s["judul"]))
        L.append("")
        meta = ["**Berkas sumber**: `%s`" % s["berkas"].replace("`", "'")]
        if s["info"].get("nodoc"):
            meta.append("**No. dokumen**: %s" % aman(s["info"]["nodoc"]))
        if s["info"].get("revisi"):
            meta.append("**Revisi**: %s" % s["info"]["revisi"])
        if s["info"].get("tanggal"):
            meta.append("**Tanggal**: %s" % aman(s["info"]["tanggal"]))
        for k, v in s["ttd"].items():
            meta.append("**%s**: %s" % (aman(k), aman(v)))
        L.append(" · ".join(meta))
        L.append("")
        if s["baris"]:
            L.extend(s["baris"])
        else:
            L.append("*(Dokumen sumber tidak memuat teks yang bisa disalin.)*")
            L.append("")
    L.append("## Dokumen Terkait")
    L.append("")
    L.append("- [[%s]]" % PETA)
    for t in DOK_TERKAIT.get(judul_dok, []):
        L.append("- [[%s]]" % t)
    L.append("")
    teks = re.sub(r"\n{3,}", "\n\n", "\n".join(L)).rstrip() + "\n"
    tujuan = os.path.join(akar_keluar, folder, judul_dok + ".md")
    if akar_vault:
        ada = os.path.join(akar_vault, folder, judul_dok + ".md")
        if os.path.exists(ada):
            with open(ada, encoding="utf-8") as f:
                if "SOP BHARATA 2026" not in f.read(4000):
                    raise SystemExit("TABRAKAN: %s sudah ada dan bukan hasil skrip ini" % ada)
    os.makedirs(os.path.dirname(tujuan), exist_ok=True)
    with open(tujuan, "w", encoding="utf-8", newline="\n") as f:
        f.write(teks)
    return {"dok": judul_dok, "folder": folder, "nama": nama, "unit": unit, "rel": rel, "sop": sop,
            "penyusun": penyusun, "penyetuju": penyetuju, "ukuran": len(teks)}


def tulis_peta(sumber, hasil, akar_keluar, akar_vault):
    n_sop = sum(len(h["sop"]) for h in hasil)
    L = []
    L.append("## Deskripsi")
    L.append("")
    L.append(
        "*Peta salinan **SOP BHARATA 2026** PT Bharata Internasional Pharmaceutical: **%d dokumen** untuk **%d posisi**, "
        "tiap posisi satu dok. Dipakai untuk menjawab \"posisi ini kerjanya menurut SOP bagaimana\" sebelum merancang "
        "fitur yang menyentuh pekerjaan posisi itu.*" % (n_sop, len(hasil))
    )
    L.append("")
    L.append("- **Status**: 🟡 **Rekaman SOP (proses bisnis, non-kode).** Kepatuhan sistem ERP terhadap tiap SOP belum dipetakan (TBD), kecuali Procurement di [[GA - SOP Procurement]].")
    L.append("- **Sumber**: folder Google Drive \"SOP BHARATA 2026\", diekspor %s (di luar repo). Dokumen sumber yang menang bila salinan berbeda." % TANGGAL_EKSPOR)
    L.append("- **Cara salin**: skrip `Tools/sop_bharata/` (cara pakai di README-nya), bukan ringkasan. Teks dan urutan langkah apa adanya; nama orang di blok tanda tangan dibuang.")
    L.append("")
    L.append("## Peta Posisi")
    L.append("")
    unit_urut = []
    for h in hasil:
        if h["unit"] not in unit_urut:
            unit_urut.append(h["unit"])
    for u in unit_urut:
        L.append("### " + aman(u))
        L.append("")
        L.append("| Posisi | Dok | Jumlah dokumen | Disusun oleh (jabatan) |")
        L.append("|---|---|---|---|")
        for h in hasil:
            if h["unit"] != u:
                continue
            L.append("| %s | [[%s]] | %d | %s |" % (aman(h["nama"]), h["dok"], len(h["sop"]), ", ".join(aman(x) for x in h["penyusun"]) or " "))
        L.append("")
    L.append("## Yang Tidak Disalin")
    L.append("")
    L.append("- **Kontrak kerja per karyawan** (subfolder `HRGA/HRD/PERSONALIA/KONTRAK KERJA`, ratusan PDF): data pribadi, bukan SOP, dan repo vault ini publik. Sengaja dilewati seluruhnya.")
    L.append("- `Template SLIP GAJI PT.Bharata.xlsx` dan arsip `CEKLIS AUDIT HRD PERSONALIA-*.zip` di folder Personalia: bukan dokumen SOP.")
    L.append("- `Bukti Inspeksi Implementasi SOP Admin Warehouse.docx`: berisi foto bukti inspeksi tanpa teks.")
    L.append("- Gambar di dalam dokumen (flowchart, foto, logo): hanya teks kotak flowchart yang tersalin.")
    L.append("")
    L.append("## Yang Belum Dikerjakan (TBD)")
    L.append("")
    L.append("- Peta kepatuhan sistem ERP terhadap tiap SOP (yang sudah ada baru Procurement).")
    L.append("- Beberapa posisi berbagi SOP yang hampir sama antar-brand (Beautyhacks dan Kyura). Salinan ini mengikuti dokumen sumber apa adanya, jadi kemiripan itu ikut tersalin dan belum disatukan.")
    L.append("- Kop sebagian dokumen memuat nomor dokumen yang tidak lengkap atau kolom revisi yang belum diisi angka; itu keadaan dokumen sumber.")
    L.append("")
    form = os.path.join(sumber, "Form Inspeksi Implementasi SOP.docx")
    if os.path.exists(form):
        s = salin_sop(form)
        L.append("## Form Inspeksi Implementasi SOP")
        L.append("")
        L.append("**Berkas sumber**: `%s` (di akar folder, berlaku lintas departemen)" % s["berkas"])
        L.append("")
        for x in s["baris"]:
            L.append(("#" + x) if x.startswith("### ") else x)
        L.append("")
    L.append("## Dokumen Terkait")
    L.append("")
    for t in ("GA - SOP Procurement", "HRIS - Kepatuhan Peraturan Perusahaan", "REF - PRD ERP", "REF - Kepemilikan Data"):
        if not akar_vault or any(os.path.exists(os.path.join(akar_vault, f, t + ".md")) for f in os.listdir(akar_vault) if os.path.isdir(os.path.join(akar_vault, f))):
            L.append("- [[%s]]" % t)
    L.append("")
    teks = re.sub(r"\n{3,}", "\n\n", "\n".join(L)).rstrip() + "\n"
    tujuan = os.path.join(akar_keluar, "Reference", PETA + ".md")
    os.makedirs(os.path.dirname(tujuan), exist_ok=True)
    with open(tujuan, "w", encoding="utf-8", newline="\n") as f:
        f.write(teks)
    return len(teks)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sumber, keluar = sys.argv[1], sys.argv[2]
    vault = sys.argv[sys.argv.index("--vault") + 1] if "--vault" in sys.argv else None
    if "--pdf-inspeksi" in sys.argv:
        PDF_INSPEKSI["jalur"] = sys.argv[sys.argv.index("--pdf-inspeksi") + 1]
    terpakai = set()
    hasil = []
    for rel, folder, prefix, nama, unit in POSISI:
        h = tulis_posisi(sumber, rel, folder, prefix, nama, unit, keluar, vault)
        hasil.append(h)
        terpakai.update(os.path.join(rel, s["berkas"]).lower() for s in h["sop"])
    # Kelengkapan: setiap .docx di luar KONTRAK KERJA harus tersalin atau tercatat.
    lolos = []
    for d, _, fs in os.walk(sumber):
        if "KONTRAK KERJA" in d:
            continue
        for f in fs:
            if f.lower().endswith(".docx"):
                r = os.path.relpath(os.path.join(d, f), sumber)
                if r.lower() not in terpakai:
                    lolos.append(r)
    n_peta = tulis_peta(sumber, hasil, keluar, vault)
    print("posisi=%d dokumen=%d peta=%d karakter" % (len(hasil), sum(len(h["sop"]) for h in hasil), n_peta))
    print("docx tak masuk posisi mana pun:", lolos)
    print("--- per dok (karakter, dokumen, tanpa bagian)")
    for h in hasil:
        kosong = [s["berkas"] for s in h["sop"] if s["n_bagian"] == 0]
        print("%7d %3d  %s/%s%s" % (h["ukuran"], len(h["sop"]), h["folder"], h["dok"], ("   TANPA-BAGIAN: %s" % kosong) if kosong else ""))


if __name__ == "__main__":
    main()
