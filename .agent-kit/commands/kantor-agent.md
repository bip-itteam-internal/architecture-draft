---
description: Kantor Agent, denah kantor isometrik sesi Claude Code yang hidup (robot per sesi dan subagent, pindah area sesuai tool yang sedang dipakai), HTML file:// yang memperbarui diri tiap 2 detik
---

Tampilkan **Kantor Agent**: tiap sesi Claude Code yang hidup di workspace ini tampil sebagai robot Lead
di denah kantor isometrik, tiap subagent sebagai robot kecil sesuai perannya, dan robot berpindah ke
area sesuai alat yang sedang dipakai: **Perpustakaan** (baca, cari), **Meja** (edit, berpikir),
**Ruang server** (perintah, test, build, git), **Ruang rapat** (menunggu subagent), **Lounge** (menunggu Anda).

Menjawab pertanyaan yang tak terjawab `/papan-sesi`: sesi mana **sedang melakukan apa sekarang**. Papan
sesi hanya tahu tahap flow, yang berubah lewat slash command, dan status `aktif`, yang tak bisa dipercaya
(diukur 2026-09-15: 72 dari 99 berkas aktif padahal hanya 7 transkripnya ditulis dalam 10 menit terakhir).
Kantor Agent membaca ekor transkrip sesi, jadi robotnya ikut bergerak selagi agent bekerja.

Berkas, bukan layanan (ADR 0077 §5): penulis Python menulis `.task-plans/kantor-agent-data.js`, dan
halaman `.task-plans/kantor-agent.html` membacanya lewat `file://`. Tanpa server, tanpa hook baru.

Argumen: `[--berhenti]` (hentikan penulis latar), `[--sekali]` (tulis data satu kali tanpa penulis latar).

## Langkah

1. Jalankan (Windows):
   ```
   powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/kantor-agent.ps1 -Workspace "<ws>" [-Berhenti] [-Sekali]
   ```
   (mac/linux: `.claude/hooks/kantor-agent.sh --workspace <ws> [--berhenti] [--sekali]`.)
   Tanpa argumen: menyalakan penulis latar bila belum ada yang hidup (menulis tiap 2 detik, berhenti
   sendiri setelah 60 menit tanpa sesi hidup), lalu membuka halaman. Penulis kedua tidak pernah dinyalakan.
2. Tampilkan keluarannya apa adanya: PID penulis, path HTML, dan cara menghentikannya.
3. Bila exit 2 "butuh Python 3.8+": sebutkan tiga lokasi yang dicari (venv vault `Tools/.venv`, `py -3`,
   `python3`). Jangan menyarankan `python` global: di banyak mesin tim ia menunjuk ke venv proyek lain.
4. Bila exit 3 "penulis tidak menyala": tampilkan isi `.task-plans/kantor-agent.log`.

## Membaca halaman

- Banner **data basi**: penulis mati atau dihentikan. Jalankan `/kantor-agent` lagi.
- Banner **penulis berhenti**: tak ada sesi hidup cukup lama, penulis keluar sendiri.
- Banner **format transkrip tidak dikenali**: rilis Claude Code mengubah format transkrip, yang oleh dok
  resmi dinyatakan internal. Perbarui kit; jangan menyimpulkan apa pun dari robot yang tampil.
- Tanda **?** pada tool yang berjalan lebih dari 60 detik: prompt izin tidak tercatat di transkrip, jadi
  tool itu mungkin sedang menunggu persetujuan di sesinya.

## Batas yang disadari

- Satu mesin, dan hanya sesi yang `cwd`-nya di dalam workspace ini.
- Menunggu tugas shell latar (`run_in_background`) tampil sebagai "menunggu Anda".
- Halaman read-only. Untuk mengerjakan sebuah sesi, buka sesinya (8 karakter id di kartu, id penuh di tooltip).

Desain dan alasannya: `architecture-draft/.agent-kit/docs/2026-09-15-kantor-agent-design.md`.
