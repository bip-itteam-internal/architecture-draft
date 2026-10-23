#!/usr/bin/env python3
"""Status lock receipt-sync: aman deploy integration-service sekarang atau tidak.

Membuat SATU baris Bahasa Indonesia dari FAKTA yang dikumpulkan `cek-lock-receipt.remote.sh` di
server (JSON satu baris di stdin). Keputusannya SATU tempat di sini (`putuskan`), supaya wrapper
PowerShell dan shell tak punya salinan aturan sendiri dan bisa diuji tanpa prod.

Kenapa ada: membuat ulang container integration-service saat `receipt-sync` berjalan memotong
putaran income dan TIDAK meninggalkan jejak (IT - Background Jobs & Schedulers, catatan operasional).
Putaran 60 sampai 90 menit pada 08:30, 11:30, 14:30, 17:30, 20:30 WIB, dan yang terpotong hanya
tampak sebagai baris yang tidak ada.

Aturan keputusan:
- Lock `lock:receipt-sync` ada, belum kedaluwarsa, dan pemiliknya container yang hidup  -> TIDAK aman.
- Lock ada tapi pemiliknya BUKAN container yang hidup (proses mati, lock yatim)           -> aman,
  disebut apa adanya (lock yatim menahan putaran berikutnya sampai kedaluwarsa, bukan deploy).
- Lock kosong tetapi putaran berikutnya mulai dalam AMBANG_MULAI_MENIT menit              -> TIDAK aman.
- Selain itu                                                                              -> aman.

Format fakta (JSON satu baris, waktu epoch milidetik):
  {"sekarang_ms": 0, "container_id": "ab471965afe7",
   "lock": {"owner": "ab471965afe7-1", "kedaluwarsa_ms": 0} | null,
   "konfig": {"jadwal": "0 30 8,11,14,17,20 * * *", "timeout_ms": 5400000, "aktif": true} | null,
   "putaran": [{"mulai_ms": 0, "selesai_ms": 0}, ...]}      # urutan bebas

Tak ada fakta yang bisa dipercaya -> baris "tidak bisa dicek", tidak pernah menebak aman.
"""
import json
import re
import sys
from datetime import datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))
JAM_BAWAAN = (8, 11, 14, 17, 20)
MENIT_BAWAAN = 30
TIMEOUT_BAWAAN_MS = 90 * 60 * 1000
# Deploy integration-service butuh beberapa menit (build + naik). Putaran yang mulai di tengahnya
# terpotong, jadi sisa waktu sebelum slot berikutnya harus cukup lega.
AMBANG_MULAI_MENIT = 10


def _jadwal(konfig):
    """(jam-jam, menit) dari cron enam kolom `detik menit jam hari bulan hari-minggu` milik worker.

    Hanya bentuk sederhana yang dikenali (angka atau daftar dipisah koma). Bentuk lain jatuh ke
    jadwal bawaan: lebih baik memakai jadwal seed yang diketahui daripada menebak ekspresi rumit.
    """
    jadwal = (konfig or {}).get("jadwal") or ""
    kolom = jadwal.split()
    if len(kolom) >= 3 and re.fullmatch(r"\d{1,2}", kolom[1]) and re.fullmatch(r"\d{1,2}(,\d{1,2})*", kolom[2]):
        jam = tuple(sorted({int(x) for x in kolom[2].split(",")}))
        menit = int(kolom[1])
        if all(0 <= j <= 23 for j in jam) and 0 <= menit <= 59:
            return jam, menit
    return JAM_BAWAAN, MENIT_BAWAAN


def _dt(ms):
    return datetime.fromtimestamp(ms / 1000, tz=WIB)


def _slot_berikutnya(sekarang, jam, menit):
    """Mulai putaran terjadwal PERTAMA yang tepat sesudah `sekarang` (datetime WIB)."""
    for hari in (0, 1):
        for j in jam:
            kandidat = (sekarang + timedelta(days=hari)).replace(hour=j, minute=menit, second=0, microsecond=0)
            if kandidat > sekarang:
                return kandidat
    raise ValueError("jadwal kosong")  # tak terjangkau: jam selalu tak kosong


def _jam(dt, sekarang):
    """HH:mm bila hari ini; `besok HH:mm`; selain itu `dd/MM HH:mm`."""
    selisih = (dt.date() - sekarang.date()).days
    if selisih == 0:
        return dt.strftime("%H:%M")
    if selisih == 1:
        return "besok " + dt.strftime("%H:%M")
    return dt.strftime("%d/%m %H:%M")


def putuskan(fakta, ambang_menit=AMBANG_MULAI_MENIT):
    """Satu baris status dari fakta; tak melempar untuk fakta tak lengkap."""
    try:
        sekarang = _dt(int(fakta["sekarang_ms"]))
    except (KeyError, TypeError, ValueError):
        return "Receipt lock tidak bisa dicek (waktu server tidak terbaca), jangan diasumsikan aman"

    konfig = fakta.get("konfig") or None
    jam, menit = _jadwal(konfig)
    berikut = _slot_berikutnya(sekarang, jam, menit)
    aktif = True if konfig is None else bool(konfig.get("aktif", True))
    timeout_ms = int((konfig or {}).get("timeout_ms") or TIMEOUT_BAWAAN_MS)

    lock = fakta.get("lock") or None
    kontainer = (fakta.get("container_id") or "").strip()
    if lock and int(lock.get("kedaluwarsa_ms") or 0) > int(fakta["sekarang_ms"]):
        kedaluwarsa = _dt(int(lock["kedaluwarsa_ms"]))
        hidup = bool(kontainer) and str(lock.get("owner") or "").startswith(kontainer)
        if hidup:
            mulai = kedaluwarsa - timedelta(milliseconds=timeout_ms)
            return ("Receipt lock TIDAK aman: receipt-sync sedang berjalan sejak %s "
                    "(lock kedaluwarsa %s), aman deploy setelah selesai sampai %s"
                    % (_jam(mulai, sekarang), _jam(kedaluwarsa, sekarang), _jam(berikut, sekarang)))
        if not kontainer:
            return "Receipt lock tidak bisa dicek (id container integration-service tidak terbaca), jangan diasumsikan aman"
        yatim = " (ada sisa lock yatim milik proses yang sudah mati, kedaluwarsa %s)" % _jam(kedaluwarsa, sekarang)
    else:
        yatim = ""

    selesai = [int(p["selesai_ms"]) for p in (fakta.get("putaran") or [])
               if p.get("selesai_ms") and int(p["selesai_ms"]) <= int(fakta["sekarang_ms"])]
    dari = _jam(_dt(max(selesai)), sekarang) if selesai else None

    if not aktif:
        return "Receipt lock kosong%s, receipt-sync nonaktif, aman deploy sekarang" % yatim

    sisa = int((berikut - sekarang).total_seconds() // 60)
    if sisa <= ambang_menit:
        return ("Receipt lock TIDAK aman: kosong tapi receipt-sync mulai %s (%d menit lagi), "
                "deploy setelah putaran itu selesai" % (_jam(berikut, sekarang), max(sisa, 0)))

    asal = (" dari %s" % dari) if dari else " (belum ada catatan putaran)"
    return "Receipt lock kosong%s%s sampai %s, aman deploy sekarang" % (yatim, asal, _jam(berikut, sekarang))


def main():
    # stdin dibaca sebagai bytes: PowerShell 5.1 menyisipkan BOM di awal pipa ke proses native, dan
    # pembacaan teks bawaan Windows (cp1252) akan mengubah BOM itu jadi tiga karakter aneh.
    mentah = sys.stdin.buffer.read().decode("utf-8-sig", errors="replace").strip()
    try:
        # fakta adalah baris JSON TERAKHIR (mongosh bisa mencetak peringatan di atasnya)
        baris = [b for b in mentah.splitlines() if b.strip().startswith("{")]
        fakta = json.loads(baris[-1])
    except (IndexError, ValueError):
        print("Receipt lock tidak bisa dicek (jawaban server tak terbaca), jangan diasumsikan aman")
        return 0
    print(putuskan(fakta))
    return 0


if __name__ == "__main__":
    sys.exit(main())
