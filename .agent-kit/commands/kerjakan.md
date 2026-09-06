---
description: Jalankan satu brief sampai PR — worktree, agen domain, judge otomatis, loop perbaikan maks 2×, lalu PR. Merge tetap manusia.
---

Jalankan **AI Engineering Loop** untuk satu brief: routing → worktree terisolasi → eksekutor
domain → `/judge` → perbaikan bila gagal (maksimum 2 pengulangan, 3 percobaan total) → commit →
push → PR. **Berhenti di PR.** Agent tidak merge (ADR 0077 §1): `main` pernah terbukti mendarat
di produksi lewat jalur yang belum terverifikasi.

Argumen: path brief (`.task-plans/briefs/...md`), atau teks bebas (→ jalankan prosedur `/brief`
dulu, lalu lanjut dengan brief yang dihasilkan).

Skrip pendukung ada di `.claude/hooks/` (Windows: `.ps1` lewat tool PowerShell; mac/linux:
`.sh`). Di mesin dev Windows tool Bash tidak berfungsi, jangan dipakai.

## 0. Baca brief, tentukan repo dan domain

Baca brief utuh. `Repo` → path `<workspace>/<repo>`. `Domain` → agen `loop-<domain>`
(`loop-fix`, `loop-refactor`, `loop-test`, `loop-docs`). Slug = nama berkas brief tanpa tanggal.
Id sesi ini ada di konteks SessionStart (`Sesi ini: <id>`); kalau ada, catat `worktree` dan
`branch` ke `.task-plans/sesi/<id>.json` begitu worktree jadi (sunting dua field itu saja).

## 1. Worktree terisolasi di path pendek

Untuk repo kode:

```
powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/worktree-baru.ps1 -Repo "<path repo>" -Slug <slug> -Domain <domain>
```

Keluarannya JSON: `path`, `branch`, `install`. Bila `install.lolos` false → **berhenti**, laporkan
ekor keluarannya; eksekutor tanpa `node_modules` akan menghasilkan kegagalan yang menyesatkan.
Path sengaja pendek (`~/wt/fe-<slug>`) dan bukan `isolation: worktree` bawaan: worktree di path
panjang membuat vitest mati diam-diam (team-memory).

Untuk `architecture-draft` (domain docs): **tanpa worktree**, kerja langsung di vault di `main`
(konvensi vault: push langsung, tanpa PR).

## 2. Eksekutor

Dispatch `Agent` dengan `subagent_type: loop-<domain>`, `run_in_background: false`. Prompt wajib
memuat, dalam bentuk path absolut:

```
Brief: <path brief>
Worktree: <path worktree>   (atau: vault architecture-draft, branch main)
Repo: <nama repo>  Branch: <branch>
Skill yang relevan untuk dibaca dulu: <daftar .claude/skills/<x>/SKILL.md yang cocok, boleh kosong>
Percobaan: 1 dari 3
```

**Bila `Agent` menjawab "Agent type 'loop-<domain>' not found"**: daftar agen kustom dibaca saat sesi
mulai, jadi sesi ini lahir sebelum kit 1.15.0 di-init. Jalan yang benar: **restart sesi**. Jalan
darurat satu kali: dispatch `general-purpose` dengan seluruh isi `.claude/agents/loop-<domain>.md`
(tanpa frontmatter) sebagai pembuka prompt, lalu catat `agen` di log judge sebagai
`general-purpose(loop-<domain>)`; jangan jadikan ini kebiasaan, model dan batas tools-nya berbeda.

Pilih skill relevan dari `.claude/skills/`: `migrasi-tabel-hris` untuk halaman daftar erp-frontend,
`deploy-bip-erp` tidak relevan untuk eksekutor (jangan disertakan), `audit-keamanan` bila brief
menyebut auth/RBAC/izin. Catat daftar itu; ia masuk log judge sebagai `skills_dibaca`.

## 3. Judge

Jalankan prosedur `/judge` (baca `.claude/commands/judge.md` dan lakukan) atas worktree itu dengan
brief yang sama. Hasilnya `lolos` (gerbang deterministik **dan** agen judge sama-sama lolos) dan
daftar `temuan`, `gagal_baru`.

Tulis log `.task-plans/judge/<slug>-<n>.json`:

```json
{ "brief": "<path>", "worktree": "<path>", "branch": "...", "percobaan": n, "waktu": "<UTC ISO>",
  "gerbang": <hasil gerbang.ps1>, "verdict": <JSON judge>, "lolos": true|false,
  "skills_dibaca": ["..."], "agen": "loop-<domain>" }
```

## 4. Loop perbaikan

Bila **gagal** dan percobaan < 3: dispatch ulang `loop-<domain>` dengan prompt yang sama plus
bagian **"Yang harus diperbaiki (dari judge)"** berisi temuan `kritis`, kriteria yang tidak
terpenuhi, dan `gagal_baru` gerbang, apa adanya. Lalu kembali ke §3 dengan `percobaan+1`.

Bila **gagal 3 kali**: berhenti. Worktree **dibiarkan utuh** supaya manusia melanjutkan di tempat
yang sama. Laporkan:

```
GAGAL setelah 3 percobaan.
Worktree: <path>   Branch: <branch>
Temuan terakhir: <ringkas, file:line>
Lanjutkan sendiri:  code <path>   atau   /judge <path> --brief <brief>
Log: .task-plans/judge/<slug>-{1,2,3}.json
```

Tambahkan bagian `## Hasil` di brief dengan status GAGAL dan path log. Selesai.

## 5. Commit, push, PR (hanya bila lolos)

Repo kode, di dalam worktree:

1. `git -C "<wt>" -c core.fsmonitor=false add -A` (worktree ini terisolasi, jadi `-A` aman di sini;
   di checkout bersama tetap dilarang).
2. Commit dengan judul conventional dari brief: `<tipe>(<area>): <judul brief>` dengan tipe =
   domain (`fix`, `refactor`, `test`, `docs`), area = modul/folder utama yang disentuh. Badan:
   Tujuan brief (satu paragraf), lalu `Judge: lolos, <n> kriteria, percobaan <k>/3`. **Tanpa**
   trailer `Co-Authored-By`. ⚠️ **Tulis pesannya ke berkas lalu `git commit -F <berkas>`**, jangan
   `-m` inline: PowerShell 5.1 memecah argumen native pada tanda kutip ganda di dalam pesan, git
   lalu membaca sisa pesan sebagai pathspec dan commit gagal, sementara push berikutnya tetap
   jalan dan mendorong branch **tanpa commit**. Terjadi 2026-09-06 pada PR pertama loop ini.
3. `git -C "<wt>" -c core.fsmonitor=false push -u origin <branch>`. Hook `pre-push` akan
   menjalankan tsc/lint/build atau go build. Bila **ditolak**: JANGAN `--no-verify`. Perlakukan
   sebagai kegagalan judge (kembali ke §4 dengan keluaran hook sebagai temuan).
4. `gh pr create --repo bip-itteam-internal/<repo> --head <branch> --title "<judul commit>" --body-file <berkas>` dengan badan:
   - Tujuan (dari brief)
   - Kriteria lolos + bukti (dari verdict)
   - Ringkasan judge + gerbang yang dijalankan (nama, durasi, lolos)
   - `Brief: <path>` · `Log: .task-plans/judge/<slug>-<n>.json`
   - Baris penutup: *Dibuat oleh AI Engineering Loop (agent-kit). Merge tetap keputusan manusia (ADR 0077 §1).*
5. Cetak URL PR. Tambahkan `## Hasil` di brief: percobaan, verdict, URL PR.

Vault (domain docs): stage **per nama berkas**, commit, `build-vault-index.py --check` (regenerasi
lewat `/index-vault` bila basi), `git merge origin/main` bila remote maju, push `main`. Tanpa PR.

## 6. Tutup

Perbarui `.task-plans/sesi/<id>.json`: `tahap` = `kerjakan`, `task` = judul brief. Cetak ringkas:
brief, percobaan, gerbang, PR. Worktree **tidak dihapus** oleh command ini; setelah PR merged,
`worktree-bersih.ps1` yang membuangnya.

## Jangan

- Jangan merge, jangan `--no-verify`, jangan menyentuh checkout utama repo.
- Jangan menulis kode sendiri di sini; kalau eksekutor gagal, yang diperbaiki adalah prompt
  perbaikannya (temuan judge), bukan kodenya olehmu. Kalau kamu mulai menyunting kode, loop-nya
  sudah bocor.
- Jangan mengulang lebih dari 3 percobaan "sedikit lagi". Tiga adalah batasnya; sisanya manusia.
