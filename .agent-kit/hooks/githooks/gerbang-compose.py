#!/usr/bin/env python3
"""gerbang-compose.py — gerbang kunci ganda pada berkas Docker Compose.

YAML menolak kunci ganda dalam SATU mapping, dan `docker compose` lalu GAGAL PARSE SELURUH
BERKAS begitu itu terjadi -- bukan cuma blok yang bersangkutan. Kejadian nyata di bip-erp:
`INTEGRATION_MODULE_URL` masuk dua kali di blok `employee-service` docker-compose.yml
(2026-09-23 16:07, empat menit sesudah container terakhir dibangun). Seluruh service tetap
hidup dan `healthy`; nol pemeriksaan menangkapnya -- bukan lint, bukan test, bukan CI, bukan
pre-push -- sampai orang pertama mencoba deploy berikutnya, berjam-jam kemudian, dan gagal
(bip-erp #2038).

Dipanggil dari `githooks/pre-push`, HANYA atas berkas compose yang diberikan lewat
`--berkas-file` (satu path per baris) atau argv biasa -- bukan validasi YAML umum, dan bukan
pemindaian seluruh repo (lihat brief `2026-09-24-gerbang-kunci-ganda-compose.md` § Batas).

Deteksi: override `construct_mapping` bawaan `yaml.SafeLoader` sehingga tiap kali sebuah node
mapping dibangun, kunci yang SUDAH MUNCUL di mapping yang SAMA dicatat sebagai duplikat lengkap
DUA nomor barisnya (1-indexed) -- persis informasi yang biasa diberikan `docker compose` sendiri
saat menolak parse, tanpa perlu menjalankan `docker compose` (yang menarik `.env` dan bisa
menyentuh jaringan -- lihat brief § Batas).

⛔ Kunci `<<: *anchor` (YAML merge key, fitur Compose baku untuk extension fields/fragments --
bip-erp sudah memakai keluarga idiom yang sama lewat `x-mongo-logging: &mongolog`) SENGAJA
DILEWATI di loop, bukan diselesaikan lewat `flatten_mapping` bawaan `SafeConstructor`.
`flatten_mapping` menyisipkan pasangan hasil merge DI DEPAN `node.value`, jadi kunci lokal yang
memang sengaja menimpa kunci warisan (mis. `restart` di-override per service) akan muncul dua
kali dalam iterasi -- itu sendiri POSITIF PALSU baru, ditemukan judge percobaan 1. Kita tidak
peduli isi merge-nya (tak pernah membaca dokumen tergabungnya), cuma kunci ganda LITERAL di
blok itu; anchor-nya sendiri (`x-mongo-logging: &foo`) tetap diperiksa lewat jalur biasa karena
di TEMPAT DEFINISInya ia cuma kunci mapping biasa.

Alat yang tidak terpasang (python tanpa PyYAML) membuat gerbang GAGAL, bukan lolos diam-diam --
lihat pemanggilnya di `pre-push` untuk pencarian interpreter yang benar-benar punya PyYAML.
"""
import os
import sys


def muat_yaml():
    try:
        import yaml
    except ImportError:
        return None
    return yaml


def periksa_berkas(path, yaml_mod):
    """Kembalikan (duplikat, galat_lain).

    duplikat: list [(kunci, baris_pertama, baris_kedua), ...] -- SEMUA duplikat di seluruh
    dokumen (di sembarang kedalaman mapping: services, environment, dst), bukan cuma yang
    pertama ditemukan.
    galat_lain: pesan str satu baris bila dokumennya gagal di-parse karena sebab LAIN (bukan
    kunci ganda), atau None.
    """
    duplikat = []

    class _Loader(yaml_mod.SafeLoader):
        pass

    def _construct_mapping(loader, node, deep=False):
        pertama = {}
        mapping = {}
        for key_node, value_node in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                # `<<: *anchor` -- lihat catatan di docstring modul ini. Dilewati UTUH: key_node
                # dan value_node-nya TIDAK di-construct_object, dan kuncinya TIDAK dicatat --
                # bukan diselesaikan (flatten_mapping), supaya kunci lokal yang sengaja menimpa
                # warisannya tidak terbaca sebagai duplikat.
                continue
            kunci = loader.construct_object(key_node, deep=deep)
            baris = key_node.start_mark.line + 1
            nilai = loader.construct_object(value_node, deep=deep)
            if kunci in pertama:
                duplikat.append((kunci, pertama[kunci], baris))
            else:
                pertama[kunci] = baris
            mapping[kunci] = nilai
        return mapping

    _Loader.add_constructor(yaml_mod.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        teks = f.read()
    try:
        yaml_mod.load(teks, Loader=_Loader)
    except yaml_mod.YAMLError as e:
        return duplikat, " ".join(str(e).split())
    return duplikat, None


def main(argv):
    yaml_mod = muat_yaml()
    if yaml_mod is None:
        print("[gerbang-compose] modul python 'yaml' (PyYAML) tidak ditemukan. Gerbang GAGAL, bukan dilewati.")
        print("  Pasang: pip install pyyaml")
        return 1

    berkas = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--berkas-file":
            with open(argv[i + 1], encoding="utf-8", errors="replace") as f:
                berkas += [b.strip() for b in f if b.strip()]
            i += 2
        else:
            berkas.append(a)
            i += 1

    if not berkas:
        return 0

    gagal = False
    for path in berkas:
        if not os.path.exists(path):
            # Berkas terhapus/dipindah di commit yang sama -- tak ada isi untuk diperiksa.
            continue
        try:
            duplikat, galat_lain = periksa_berkas(path, yaml_mod)
        except Exception as e:  # bug di detektor sendiri: GAGAL, bukan lolos diam-diam
            print("[gerbang-compose] GAGAL memeriksa %s: %s" % (path, e))
            gagal = True
            continue
        for kunci, b1, b2 in duplikat:
            print("[gerbang-compose] %s: kunci '%s' muncul dua kali (baris %d dan baris %d)"
                  % (path, kunci, b1, b2))
            gagal = True
        if galat_lain is not None and not duplikat:
            print("[gerbang-compose] %s: gagal di-parse sebagai YAML (%s)" % (path, galat_lain))
            gagal = True

    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
