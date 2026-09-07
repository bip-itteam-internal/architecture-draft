---
description: Nilai sebuah worktree terhadap brief — gerbang deterministik (tsc/lint/build/go build, test vs baseline) DAN agen judge read-only; lolos hanya bila keduanya lolos
---

Lapisan **Judges** AI Engineering Loop, dua lapis yang **keduanya** harus lolos:

1. **Gerbang deterministik** (`gerbang.ps1`): tsc, lint, build, test dibanding baseline untuk repo
   Node; `go build ./...` dan `go test` per service tersentuh untuk bip-erp. Mesin, bukan opini.
2. **Agen judge** (`loop-judge`, read-only): kepatuhan brief per kriteria, prinsip arsitektur
   (`review-checklist.md` Pass 1), dan solusi nakal (test di-skip, `eslint-disable` baru, `any`,
   kondisi khusus yang cuma memuaskan brief).

Agen **tidak berwenang** membatalkan gerbang: gerbang gagal = verdict gagal. Triangulasi ini yang
mencegah "mengakali satu metrik dengan mengorbankan yang lain".

Argumen: `<path worktree>` (bawaan: repo di cwd), `--brief <path>` (bawaan: brief terbaru di
`.task-plans/briefs/` yang slug-nya cocok dengan nama branch), `--tanpa-build`, `--tanpa-test`
(hanya untuk iterasi cepat; verdict-nya dicatat sebagai **tidak lengkap**).

## Langkah

1. **Gerbang deterministik**

   ```
   powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/gerbang.ps1 -Path "<wt>" -Keluaran ".task-plans/judge/<slug>-gerbang.json"
   ```
   (mac/linux: `gerbang.sh`). Exit 0 = semua lolos. Tampilkan tabel: nama gerbang, lolos, durasi,
   `gagal_baru` untuk test. Perhatikan `catatan`: **"TIDAK ADA BASELINE"** berarti test tidak
   dibandingkan dengan apa pun; sebutkan itu terang di verdict, jangan diam.

2. **Diff untuk judge**

   ```
   git -C "<wt>" -c core.fsmonitor=false add -N .
   git -C "<wt>" -c core.fsmonitor=false diff $(git -C "<wt>" -c core.fsmonitor=false merge-base origin/main HEAD)
   ```
   `add -N` (intent-to-add) supaya berkas baru ikut tampil di diff; aman karena worktree ini
   terisolasi. Simpan ke `.task-plans/judge/<slug>-diff.patch`. Diff kosong → berhenti: tidak ada
   yang dinilai, katakan begitu.

3. **Agen judge**

   Dispatch `Agent` `subagent_type: loop-judge`, `run_in_background: false`, prompt berisi path
   absolut: brief, diff, hasil gerbang JSON, worktree, dan
   `architecture-draft/.agent-kit/rules/review-checklist.md`. Ambil JSON di antara `<<VERDICT>>`
   dan `<<END>>`. JSON tidak sah atau penanda tidak ada → `lolos: false`, `catatan: "verdict tidak
   terurai"`; jangan menebak isinya.

4. **Triangulasi dan laporan**

   `lolos = gerbang.lolos AND verdict.lolos`. Cetak:

   ```
   JUDGE <slug> — LOLOS | GAGAL
   Gerbang: tsc ✓ 12s · lint ✓ 20s · build ✓ 95s · test ✓ (0 baru, 14 di baseline) 
   Brief: 3/3 kriteria terpenuhi
   Temuan kritis: <n>   informasional: <m>
   <daftar temuan file:line — alasan — saran>
   Catatan: <pertanyaan judge, peringatan baseline>
   ```

   Bila dipanggil langsung oleh manusia (bukan dari `/kerjakan`), tutup dengan langkah berikutnya:
   lolos → "lanjut commit/PR lewat `/kerjakan`" ; gagal → daftar yang harus diperbaiki.

## Jangan

- Jangan memperbaiki kode di sini. Judge menilai; `/kerjakan` yang mengulang eksekutor.
- Jangan menurunkan `kritis` jadi `informasional` supaya lolos. Kalau judge salah, perbaiki
  `review-checklist.md` atau agen `loop-judge`, bukan verdict-nya.
- Jangan menyimpulkan apa pun dari CI GitHub; verifikasi di sini lokal.
