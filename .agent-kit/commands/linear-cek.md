---
description: Cocokkan status issue Linear (tim BHA) dengan PR GitHub yang tertaut; laporan dulu, pindah status hanya dengan --terapkan
argument-hint: [--terapkan] [--hari-macet N]
---

Jalankan verifikasi status backlog Linear terhadap bukti PR, sesuai definisi status di
`team-memory.md` § Linear. Argumen: $ARGUMENTS

Butuh `LINEAR_API_KEY` (env proses atau env **User**; key pribadi dari Linear → Settings →
Security & access). Tanpa itu skrip keluar dengan pesan, jangan meminta user menempel key ke chat.

## Langkah

1. Jalankan (PowerShell, bukan Bash):
   ```
   & '.claude/hooks/linear-verifikasi.ps1'                  # laporan saja
   & '.claude/hooks/linear-verifikasi.ps1' -Terapkan        # bila argumen memuat --terapkan
   & '.claude/hooks/linear-verifikasi.ps1' -HariMacet <N>   # bila argumen memuat --hari-macet N
   ```
   Laporan ditulis ke `.task-plans/linear/verifikasi-<tanggal>.md`.

2. Baca laporannya, lalu sampaikan ke user per aturan:
   - **R1** Backlog/Todo tapi ada PR terbuka, **R2** semua PR merged tapi masih In Progress/In
     Review: buktinya pasti. Tawarkan `--terapkan` bila belum; `--terapkan` HANYA memindahkan dua
     aturan ini (R1 ke In Review, R2 ke Menunggu Adopsi), tak pernah ke Done.
   - **R3** Done tanpa PR tertaut: bukan bukti kodenya tak ada (PR tanpa `bha-<n>` tak pernah
     tertaut). Jangan membuka ulang issue dari daftar ini; sebelum itu ukur ke `origin/main`
     (MyBharata: `origin/dev`) dan data prod, lalu tulis bagian `### Verifikasi <tanggal>`.
   - **R4** In Progress tanpa PR dan lama tak disentuh, **R5** Menunggu Adopsi lama sejak merge,
     **R6** lewat tenggat: daftar untuk ditanyakan ke PIC atau pemilik proses.

## Jangan

- Jangan memindahkan issue ke **Done** dari command ini. Done berarti terbukti dipakai di prod,
  dan itu tak bisa dibuktikan dari PR.
- Jangan menulis ulang deskripsi issue secara massal dari laporan ini; deskripsi hanya ditambah
  bagian verifikasi setelah diukur per issue.
