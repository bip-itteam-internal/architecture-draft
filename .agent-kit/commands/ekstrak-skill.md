---
description: Ekstrak pola kerja dari transkrip sesi Claude Code jadi DRAFT skill — sesi diringkas skrip deterministik dulu, agen fable menulis draftnya
---

**Tahap 1 AI Engineering Loop: Skill Extraction.** Sesi manual yang menyelesaikan tugas berulang
diubah jadi skill terstruktur. Dua langkah, sengaja dipisah (prinsip hybrid §5.1 dokumen
rujukan): **skrip deterministik** meringkas JSONL (skemanya internal dan tidak stabil menurut dok
resmi Claude Code, jadi skrip menolak bila tidak terurai), lalu **agen** menulis draft dari
ringkasan itu. Hasilnya `skills/_draft/`, bukan `skills/`; yang menaikkan tetap manusia.

Argumen: `latest` (transkrip terbaru selain sesi ini) · `ini` (sesi ini) · `<session-id>` ·
`<path .jsonl>`; opsional `--nama <kebab-case>`.

## Langkah

1. **Temukan transkrip.** Folder proyek Claude Code: `~/.claude/projects/<slug>/` dengan slug =
   path workspace yang karakter non-alfanumeriknya diganti `-` (contoh:
   `c--Data-utama-Aplikasi-Office-erp`). Id sesi ini ada di konteks SessionStart (`Sesi ini:`).
   - `latest`: `.jsonl` termuda yang bukan sesi ini
   - `ini`: `<id sesi ini>.jsonl`
   - id / path: pakai apa adanya
   Tampilkan berkas yang dipilih (nama, ukuran, waktu ubah) sebelum lanjut.

2. **Ringkas deterministik.**
   ```
   powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/transkrip-ringkas.ps1 -Transkrip "<jsonl>" -Keluaran ".task-plans/ekstrak/<id>.md"
   ```
   (mac/linux: `transkrip-ringkas.sh <jsonl> <md>`). Exit 3 = tidak terurai (skema berubah, atau
   sesi tanpa giliran user/assistant): **berhenti**, laporkan angkanya, jangan menyuruh agen
   membaca JSONL mentah. Exit 0: tampilkan baris ringkasan (giliran user/assistant).

3. **Agen ekstraktor.** Dispatch `Agent` `subagent_type: loop-ekstrak-skill`,
   `run_in_background: false`, prompt: path ringkasan (absolut), path kit
   (`<ws>/architecture-draft/.agent-kit`), dan `--nama` bila ada.

4. **Laporkan.** Path draft (atau kesimpulan "tidak ada pola yang layak" beserta alasannya),
   tumpang tindih dengan skill yang ada, TBD yang harus diisi manusia. Tutup dengan:
   ```
   Baca draftnya: architecture-draft/.agent-kit/skills/_draft/<nama>/SKILL.md
   Naikkan bila layak: /supervise --terapkan <nama>
   ```

## Catatan

- Ringkasan di `.task-plans/ekstrak/` boleh dihapus kapan saja; ia turunan.
- Transkrip memuat apa pun yang diketik di sesi itu. Draft skill yang dihasilkan **jangan** memuat
  kredensial, token, atau data karyawan yang kebetulan lewat; periksa sebelum menaikkan.
- Satu sesi yang tidak berulang bukan bahan skill. Agen boleh menjawab "tidak ada pola yang
  layak", dan itu jawaban yang benar, bukan kegagalan.
