---
description: Supervisor loop — evaluasi skill, temuan judge berulang, brief gagal, sesi macet; hasilnya laporan + DRAFT skill (tidak auto-apply). --terapkan <nama> memindahkan draft ke skills/
---

Lapisan **Supervisi** AI Engineering Loop. Mengevaluasi performa loop secara keseluruhan dan
mengusulkan perbaikan skill library. **Tidak auto-apply**: supervisor menulis draft, manusia yang
memutuskan. Alasannya tercatat di ADR 0077 §6: belum ada metrik kualitas skill yang bisa
dipercaya mesin, dan skill yang salah menyebar ke seluruh tim lewat `init`.

Argumen: `[--hari N]` (bawaan 14), atau `--terapkan <nama-draft>`.

## Mode evaluasi (bawaan)

1. Dispatch `Agent` `subagent_type: loop-supervisor`, `run_in_background: false`, prompt: path
   akar workspace, path kit (`<ws>/architecture-draft/.agent-kit`), rentang hari.
2. Tampilkan: path laporan `docs/supervise-<tanggal>.md`, ringkasan temuan (maks 5 baris), daftar
   draft di `skills/_draft/`.
3. Tutup dengan:
   ```
   Baca laporannya. Draft yang layak: /supervise --terapkan <nama>
   Usulan untuk team-memory.md ada di laporan; sunting sendiri, jangan disalin mentah.
   ```

Bila log judge/brief masih sedikit (sebutkan angkanya), katakan bahwa laporan berdiri di atas data
tipis dan jangan memaksakan rekomendasi. Data log baru ada sejak kit 1.15.0.

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
