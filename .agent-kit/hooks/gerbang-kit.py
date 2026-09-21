#!/usr/bin/env python3
"""gerbang-kit.py — gerbang lokal vault `architecture-draft` atas TEST MILIK KIT SENDIRI.

ADR 0077 par 4 menuntut `tests/test-init.ps1` dan pytest `Tools/` ikut digerbang, tetapi sampai
1.24.0 tak ada satu pun hook yang menjalankannya: `init.ps1` sengaja mengecualikan vault saat
memasang `core.hooksPath`, jadi yang menjalankan test kit cuma ingatan orang.

Dipanggil `githooks/pre-push`. SATU implementasi untuk semua OS (bukan pasangan .ps1/.py), karena
python sudah jadi syarat pytest-nya sendiri.

Tiga hal yang membuatnya tidak mengganggu pekerjaan dokumentasi:

- **Saringan path.** Push yang tidak menyentuh `.agent-kit/` maupun `Tools/` keluar seketika.
  Vault ini dipakai menulis dokumentasi setiap hari; gerbang yang menyala di tiap push akan
  dimatikan orang dalam sepekan, dan gerbang yang dimatikan tidak menjaga apa pun.
- **Penjaga rekursi.** `test-init.ps1` menjalankan `init`, dan `init` memasang hook ini. Tanpa
  AGENTKIT_KIT_TESTS_RUNNING, sebuah push dari dalam test bisa memanggil test lagi.
- **Jalan keluar sadar** AGENTKIT_SKIP_KIT_TESTS=1, yang DICETAK supaya tidak senyap.

Alat yang tidak terpasang membuat gerbang GAGAL, bukan lolos: itu justru lubang yang sedang
ditutup di sini (lihat `gerbang-lib.py` putuskan_lolos).
"""
import os
import shutil
import subprocess
import sys

# Prefiks folder yang membuat gerbang menyala. Dicocokkan sebagai SEGMEN path, bukan awalan
# telanjang: 'Toolsmith/catatan.md' bukan perubahan kit.
FOLDER_KIT = (".agent-kit", "Tools")
BATAS_PYTEST = 900
BATAS_TEST_INIT = 1800


def perlu_gerbang(berkas):
    """True bila ada berkas tersentuh di dalam salah satu folder kit."""
    for b in berkas:
        segmen = b.replace("\\", "/").split("/")
        if segmen and segmen[0] in FOLDER_KIT and len(segmen) > 1:
            return True
    return False


def env_bersih(**tambahan):
    """⛔ Buang SELURUH `GIT_*` sebelum memanggil anak.

    Git mewariskan `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, dan `GIT_QUARANTINE_PATH` ke
    hook-nya, dan variabel itu MENANG atas penemuan repo biasa: `git -C <folder lain> <perintah>`
    tetap mengenai repo yang sedang di-push. Terukur 2026-09-21 pada push pertama yang memicu
    gerbang ini: `test-init.ps1` membuat repo sandbox di `%TEMP%`, lalu seluruh perintah gitnya
    mendarat di worktree vault yang sedang di-push — dua commit kosong bertambah di atas branch
    kerja, branch `feat/uji` lahir di repo nyata, HEAD berpindah ke `main`, dan
    `user.email=test@example.invalid` tertulis ke config repo. Tak satu pun terbaca sebagai galat;
    yang terlihat cuma test-init merah yang hijau bila dijalankan langsung.

    Dibuang semuanya, bukan daftar tertentu: yang diwariskan git bertambah antar versi, dan test
    kit tidak membutuhkan satu pun di antaranya (termasuk `GIT_EXEC_PATH`, yang ditemukan sendiri
    oleh git).
    """
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(tambahan)
    return env


def akar_utama(vault):
    """Worktree tertaut tidak punya Tools/.venv; venv-nya ada di worktree UTAMA repo itu."""
    r = subprocess.run(["git", "-C", vault, "-c", "core.fsmonitor=false", "rev-parse",
                        "--path-format=absolute", "--git-common-dir"],
                       capture_output=True, text=True, env=env_bersih())
    if r.returncode != 0 or not r.stdout.strip():
        return vault
    return os.path.dirname(r.stdout.strip().rstrip("/\\"))


def cari_python(kandidat_akar):
    """Python yang BENAR-BENAR punya pytest. Yang tidak punya pytest bukan kandidat."""
    kandidat = []
    for akar in kandidat_akar:
        for rel in ("Tools/.venv/Scripts/python.exe", "Tools/.venv/bin/python"):
            p = os.path.join(akar, rel.replace("/", os.sep))
            if os.path.exists(p):
                kandidat.append(p)
    for n in ("python3", "python"):
        p = shutil.which(n)
        if p:
            kandidat.append(p)
    for p in kandidat:
        r = subprocess.run([p, "-c", "import pytest"], capture_output=True, text=True, env=env_bersih())
        if r.returncode == 0:
            return p
    return None


def jalankan(judul, cmd, cwd, batas):
    print("[agent-kit gerbang-kit] %s ..." % judul, flush=True)
    env = env_bersih(AGENTKIT_KIT_TESTS_RUNNING="1", PYTHONDONTWRITEBYTECODE="1")
    try:
        r = subprocess.run(cmd, cwd=cwd, env=env, timeout=batas)
        rc = r.returncode
    except subprocess.TimeoutExpired:
        print("[agent-kit gerbang-kit] LEWAT BATAS %s detik: %s" % (batas, judul))
        rc = 124
    if rc != 0:
        print("[agent-kit gerbang-kit] GAGAL: %s (exit %s)" % (judul, rc))
    return rc == 0


def main(argv):
    vault, berkas, hanya_putuskan = None, [], False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--vault": vault = argv[i + 1]; i += 2
        elif a == "--berkas": berkas.append(argv[i + 1]); i += 2
        elif a == "--berkas-file":
            # nama berkas dok vault berisi spasi; daftar lewat berkas, bukan argumen yang terpecah
            with open(argv[i + 1], encoding="utf-8", errors="replace") as f:
                berkas += [b.strip() for b in f if b.strip()]
            i += 2
        elif a == "--hanya-putuskan": hanya_putuskan = True; i += 1
        else: i += 1
    vault = vault or os.getcwd()

    if not perlu_gerbang(berkas):
        print("[agent-kit gerbang-kit] tidak ada perubahan di %s: gerbang test kit DILEWATI"
              % " / ".join(f + "/" for f in FOLDER_KIT))
        return 0
    if hanya_putuskan:
        print("[agent-kit gerbang-kit] perubahan kit terdeteksi: gerbang test kit MENYALA")
        return 0
    if os.environ.get("AGENTKIT_KIT_TESTS_RUNNING") == "1":
        print("[agent-kit gerbang-kit] sudah berjalan di dalam test kit: dilewati untuk mencegah rekursi")
        return 0
    if os.environ.get("AGENTKIT_SKIP_KIT_TESTS") == "1":
        print("[agent-kit gerbang-kit] DILEWATI SADAR (AGENTKIT_SKIP_KIT_TESTS=1). "
              "Anda mendorong perubahan kit tanpa menjalankan test kit.")
        return 0

    kit = os.path.join(vault, ".agent-kit")
    utama = akar_utama(vault)
    py = cari_python([vault, utama])
    if not py:
        print("[agent-kit gerbang-kit] TIDAK ADA python ber-pytest. Gerbang GAGAL, bukan dilewati.")
        print("  Buat venv vault:  python -m venv Tools/.venv ; Tools/.venv/Scripts/pip install -r Tools/requirements.txt")
        print("  Lewati sadar   :  AGENTKIT_SKIP_KIT_TESTS=1 git push")
        return 1

    ok = True
    target = [os.path.join(utama, "Tools", "tests"), os.path.join(kit, "tests", "test_kantor_agent.py"),
              os.path.join(kit, "tests", "test_gerbang.py")]
    ok = jalankan("pytest", [py, "-m", "pytest", "-p", "no:cacheprovider", "-q"] + [t for t in target if os.path.exists(t)],
                  utama, BATAS_PYTEST) and ok

    # test-init.ps1 hanya ada dalam bentuk PowerShell. Mesin tanpa PowerShell tetap digerbang oleh
    # pytest di atas; yang dilewati DICETAK, supaya "lolos" tidak berarti "tidak diperiksa".
    psh = shutil.which("pwsh") or shutil.which("powershell")
    init_ps1 = os.path.join(kit, "tests", "test-init.ps1")
    if not psh:
        print("[agent-kit gerbang-kit] PowerShell tidak ada: test-init.ps1 DILEWATI (pytest tetap dijalankan)")
    elif not os.path.exists(init_ps1):
        print("[agent-kit gerbang-kit] tests/test-init.ps1 tidak ditemukan di %s" % kit)
        ok = False
    else:
        ok = jalankan("test-init.ps1", [psh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", init_ps1],
                      kit, BATAS_TEST_INIT) and ok

    if not ok:
        print("[agent-kit gerbang-kit] PUSH DITOLAK: test milik kit merah (ADR 0077 par 4).")
        print("  Lewati sadar: AGENTKIT_SKIP_KIT_TESTS=1 git push")
        return 1
    print("[agent-kit gerbang-kit] test kit lolos")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
