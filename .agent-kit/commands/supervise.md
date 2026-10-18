---
description: Supervisor loop — evaluasi skill, temuan judge berulang, brief gagal, sesi macet; hasilnya laporan + DRAFT skill (tidak auto-apply). --terapkan <nama> memindahkan draft ke skills/
---

Lapisan **Supervisi** AI Engineering Loop. Mengevaluasi performa loop secara keseluruhan dan
mengusulkan perbaikan skill library. **Tidak auto-apply**: supervisor menulis draft, manusia yang
memutuskan. Alasannya tercatat di ADR 0077 §6: belum ada metrik kualitas skill yang bisa
dipercaya mesin, dan skill yang salah menyebar ke seluruh tim lewat `init`.

Argumen: `[--hari N]` (bawaan 14), atau `--terapkan <nama-draft>`.

## Mode evaluasi (bawaan)

0. **Centang salah tuduh di PR** (judge desain). Supervisor tak punya shell, jadi bahan dari
   GitHub dikumpulkan di sini. Untuk tiap brief dalam rentang yang log judge-nya
   (`.task-plans/judge/<slug>-<n>.json`) punya `verdict_desain` bukan `null`, ambil URL PR dari
   `## Hasil` brief-nya, lalu:
   ```
   gh pr view <url PR> --json number,url,state,body
   ```
   Kumpulkan hasilnya jadi satu array JSON (tambah field `slug`) di
   `.task-plans/supervise/<YYYY-MM-DD>-pr-desain.json`. Brief tanpa PR (gagal 3 kali) atau `gh`
   yang gagal: masukkan `{"slug": ..., "galat": "<alasan>"}`, jangan dilewati diam-diam; centang
   yang tak terbaca bukan berarti nol centang. Yang dihitung supervisor dari `body` adalah baris
   `- [x] salah tuduh:` (dicentang manusia) di antara baris `- [ ] salah tuduh:` yang ditulis
   `/kerjakan` §5. Field log yang dipakainya: `verdict_desain`, `layar`, `salah_tuduh`.
1. Dispatch `Agent` `subagent_type: loop-supervisor`, `run_in_background: false`, prompt: path
   akar workspace, path kit (`<ws>/architecture-draft/.agent-kit`), rentang hari, dan path berkas
   PR dari langkah 0.
2. Tampilkan: path laporan `docs/supervise-<tanggal>.md`, ringkasan temuan (maks 5 baris), daftar
   draft di `skills/_draft/`.
3. Tutup dengan:
   ```
   Baca laporannya. Draft yang layak: /supervise --terapkan <nama>
   Usulan untuk team-memory.md ada di laporan; sunting sendiri, jangan disalin mentah.
   ```

Bila log judge/brief masih sedikit (sebutkan angkanya), katakan bahwa laporan berdiri di atas data
tipis dan jangan memaksakan rekomendasi. Data log baru ada sejak kit 1.15.0.

**Judge desain** ditampilkan sebagai bagian sendiri: run yang menyalakannya, temuan kritis desain,
salah tuduh (bantahan diterima dari log `salah_tuduh` + centang `salah tuduh:` di PR), dan run
dengan `layar_dinilai: false` beserta alasannya. Angka itu dasar keputusan manusia untuk
mempertahankan pemblokiran, melonggarkan, atau mencabutnya. Di bawah **10 run** yang
menyalakannya, tampilkan angkanya saja dengan label data tipis dan **jangan** merekomendasikan
apa pun tentang pemblokirannya.

## Mode `--terapkan <nama>`

1. Pastikan `architecture-draft/.agent-kit/skills/_draft/<nama>/SKILL.md` ada dan `skills/<nama>/`
   belum ada (kalau sudah ada, ini **tambahan**: tampilkan diff-nya dan berhenti; penggabungan
   dilakukan manusia).
2. Pindahkan folder draft ke `skills/<nama>/`. Tampilkan isi frontmatter-nya.
3. Cetak langkah yang tersisa untuk manusia, jangan dikerjakan otomatis:
   ```
   Skill <nama> dipindah ke skills/. Sisa:
   1. bump architecture-draft/.agent-kit/VERSION + entri changelog README.md
   2. commit vault (stage per nama), push main
   3. tim: git pull + init + restart sesi
   ```

## Jangan

- Jangan menyunting `skills/<nama>/` yang sudah hidup, `rules/`, `commands/`, atau `agents/` dari
  command ini. Perubahan di situ lewat flow biasa (`/start-task`) supaya terreview.
- Jangan menghapus draft yang ditolak; biarkan, supaya supervisor berikutnya tahu itu sudah
  pernah diusulkan dan ditolak.
