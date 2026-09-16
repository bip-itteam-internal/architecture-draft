---
description: Kantor Agent, denah kantor isometrik sesi Claude Code yang terbuka (robot per sesi dan subagent, pindah area sesuai tool yang sedang dipakai, gelembung "!" saat minta izin), HTML file:// yang memperbarui diri tiap 2 detik
---

Tampilkan **Kantor Agent**: tiap sesi Claude Code yang terbuka di workspace ini tampil sebagai robot Lead
di denah kantor isometrik, tiap subagent sebagai robot kecil sesuai perannya, dan robot berpindah ke
area sesuai alat yang sedang dipakai: **Perpustakaan** (baca, cari), **Meja** (edit, berpikir),
**Ruang server** (perintah, test, build, git, menunggu tugas shell latar), **Ruang rapat** (menunggu subagent),
**Lounge** (menunggu Anda). Sesi yang menunggu izin Anda bersinar dengan gelembung **!**.

Menjawab pertanyaan yang tak terjawab `/papan-sesi`: sesi mana **sedang melakukan apa sekarang**. Papan
sesi hanya tahu tahap flow, yang berubah lewat slash command, dan status `aktif`, yang tak bisa dipercaya
(diukur 2026-09-15: 72 dari 99 berkas aktif padahal hanya 7 transkripnya ditulis dalam 10 menit terakhir).

Dua sumber (kit 1.21.0). **Registri sesi Claude Code** (`~/.claude/sessions/<pid>.json`) menentukan sesi mana
yang terbuka dan apakah ia sibuk, diam, atau menunggu Anda; **ekor transkrip** menentukan tool dan areanya.
Registri itu format internal, jadi penulis mencocokkannya dengan `claude agents --json` (terdokumentasi)
tiap 60 detik. Bila registri tak terbaca, penulis kembali ke cara 1.20.0: sesi = transkrip yang ditulis
dalam 30 menit terakhir.

Berkas, bukan layanan (ADR 0077 §5): penulis Python menulis `.task-plans/kantor-agent-data.js`, dan
halaman `.task-plans/kantor-agent.html` membacanya lewat `file://`. Tanpa server, tanpa hook.

Argumen: `[--berhenti]` (hentikan penulis latar), `[--sekali]` (tulis data satu kali tanpa penulis latar).

## Langkah

1. Jalankan (Windows):
   ```
   powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/kantor-agent.ps1 -Workspace "<ws>" [-Berhenti] [-Sekali]
   ```
   (mac/linux: `.claude/hooks/kantor-agent.sh --workspace <ws> [--berhenti] [--sekali]`.)
   Tanpa argumen: menyalakan penulis latar bila belum ada yang hidup (menulis tiap 2 detik, berhenti
   sendiri setelah 60 menit tanpa sesi hidup), lalu membuka halaman. Penulis kedua tidak pernah menyala,
   termasuk bila dua launcher dijalankan bersamaan.
2. Tampilkan keluarannya apa adanya: PID penulis, path HTML, dan cara menghentikannya.
3. Bila exit 2 "butuh Python 3.8+": sebutkan tiga lokasi yang dicari (venv vault `Tools/.venv`, `py -3`,
   `python3`). Jangan menyarankan `python` global: di banyak mesin tim ia menunjuk ke venv proyek lain.
4. Bila exit 3 "penulis tidak menyala": tampilkan isi `.task-plans/kantor-agent.log`.

## Membaca halaman

- Gelembung **!** dan chip **! izin**: sesi itu berhenti menunggu jawaban Anda atas prompt izin. Buka sesinya.
- Tombol **salin id** di kartu menyalin id sesi lengkap. Kartu juga menyebut asal sesi (VS Code atau terminal),
  nama, dan pid untuk menemukan jendelanya; halaman tidak bisa memfokuskan jendela itu sendiri.
- Banner **versi data tidak cocok**: penulis yang jalan berasal dari kit lain, biasanya penulis lama yang masih
  hidup sesudah upgrade kit. Jalankan `/kantor-agent --berhenti`, lalu `/kantor-agent`.
- Banner **registri tak terbaca**: mode transkrip. Sesi yang lama diam tidak tampil, dan tanda **?** pada tool
  yang berjalan lebih dari 60 detik hanya tebakan bahwa tool itu menunggu persetujuan.
- Banner **registri tidak cocok dengan claude agents**: kedua sumber berbeda di dua pengecekan berturut-turut,
  jadi jumlah robot bisa keliru. Format registri mungkin berubah; perbarui kit.
- Banner **data basi**: penulis mati atau dihentikan. Jalankan `/kantor-agent` lagi.
- Banner **snapshot sekali**: halaman dibuka dengan `--sekali`, datanya memang tidak diperbarui.
- Banner **penulis berhenti**: tak ada sesi hidup cukup lama, penulis keluar sendiri.
- Banner **format transkrip tidak dikenali**: rilis Claude Code mengubah format transkrip, yang oleh dok
  resmi dinyatakan internal. Perbarui kit; jangan menyimpulkan apa pun dari robot yang tampil.

## Batas yang disadari

- Satu mesin, dan hanya sesi yang `cwd`-nya di dalam workspace ini.
- Registri sesi dan kuncinya (`status`, `waitingFor`) format internal Claude Code, diamati di 2.1.269.
- Tool yang baru mulai baru terlihat setelah pesan asisten yang memanggilnya selesai ditulis ke transkrip.
- Tugas shell latar dilacak dari 8 MB transkrip terakhir saat penulis pertama melihat sesinya, lalu dari tulisan
  barunya. Tugas yang dimulai sebelum jendela itu tak terlihat, jadi sesi yang hanya menunggunya tampil menunggu Anda.

Desain dan alasannya: `architecture-draft/.agent-kit/docs/2026-09-15-kantor-agent-design.md`.
