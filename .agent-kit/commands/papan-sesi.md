---
description: Papan sesi — sesi Claude Code mana yang sedang mengerjakan apa (tahap, task, worktree, terakhir disentuh), tabel + HTML statis
---

Tampilkan **papan sesi**: seluruh sesi yang terdaftar di `.task-plans/sesi/*.json` (ditulis hook
SessionStart, disegarkan tiap prompt, ditutup saat SessionEnd). Menjawab satu pertanyaan yang
sebelumnya tak terjawab: **dari sekian sesi paralel, mana yang masih hidup dan sedang di tahap
apa.** Terukur 2026-09-06 sebelum papan ini ada: 35 worktree terdaftar, 31 sudah merged, tak
seorang pun tahu.

Ini BUKAN pengganti Papan Aktivitas Developer (peristiwa GitHub yang sudah terjadi); ini pekerjaan
yang sedang berjalan dan belum menghasilkan peristiwa apa pun.

Argumen: `[--basi N]` jam (bawaan 24), `[--bersihkan]` (hapus berkas sesi **selesai** > 7 hari).

## Langkah

1. Jalankan:
   ```
   powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/papan-sesi.ps1 -Workspace "<ws>" [-JamBasi N] [-Bersihkan7Hari]
   ```
   (mac/linux: `papan-sesi.sh`, tabel saja tanpa HTML.)
2. Tampilkan keluarannya apa adanya (baris ringkas + tabel) dan path HTML
   `.task-plans/dashboard.html` (dibangkitkan `dashboard.ps1` dari cache PR; `/dashboard` untuk
   menarik data gh terbaru dan panel lengkap).
3. Untuk tiap sesi **BASI** (aktif tapi tak disentuh > N jam): sebutkan worktree/branch-nya bila
   ada, dan sarankan **satu** dari: lanjutkan di sesi itu, atau tutup sesinya (SessionEnd akan
   menandainya selesai). Jangan menghapus berkas sesi aktif; yang boleh dibersihkan hanya yang
   selesai > 7 hari lewat `--bersihkan`.
4. Bila "Belum ada sesi terdaftar": kit belum di-init ke 1.15.0 atau sesi belum di-restart.
   Katakan itu, jangan menyimpulkan tidak ada yang bekerja.

## Batas yang disadari

- Satu mesin. Sesi di mesin lain tidak muncul; itu keputusan sadar (dok domain § TBD).
- Papan tahu **tahap** dan **task**, tidak tahu isi obrolan. Untuk isi, buka sesinya.
