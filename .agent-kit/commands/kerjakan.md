---
description: Jalankan satu brief sampai PR — worktree, agen domain, judge otomatis, loop perbaikan maks 2×, lalu PR. Merge tetap manusia.
---

Jalankan **AI Engineering Loop** untuk satu brief: routing → worktree terisolasi → eksekutor
domain → `/judge` → perbaikan bila gagal (maksimum 2 pengulangan, 3 percobaan total) → commit →
push → PR. **Berhenti di PR.** Agent tidak merge (ADR 0077 §1): `main` pernah terbukti mendarat
di produksi lewat jalur yang belum terverifikasi.

Argumen: path brief (`.task-plans/briefs/...md`), atau teks bebas (→ jalankan prosedur `/brief`
dulu, lalu lanjut dengan brief yang dihasilkan). ⛔ **Kecuali brief itu `ragu`** — field `Sumber`
kosong atau `tidak ada`, atau repo/domain bertanda `(ditebak)`. brief `ragu` berhenti di sini:
tampilkan briefnya, tunggu persetujuan user, baru §1. Itu satu-satunya titik manusia di jalur ini,
dan melewatinya membuat brief berpremis karangan berjalan sampai PR tanpa seorang pun melihatnya.

Skrip pendukung ada di `.claude/hooks/` (Windows: `.ps1` lewat tool PowerShell; mac/linux:
`.sh`). Di mesin dev Windows tool Bash tidak berfungsi, jangan dipakai.

## 0. Baca brief, tentukan repo, domain, dan PERAN

Baca brief utuh. `Repo` → path `<workspace>/<repo>`. Slug = nama berkas brief tanpa tanggal.
Eksekutornya dipilih dari **dua sumbu**, domain DAN repo, bukan domain saja:

| Domain | Repo | Eksekutor |
|---|---|---|
| `docs` | `architecture-draft` | `loop-docs` (Penulis) |
| `test` | mana pun | `loop-test` (QA) |
| `fix`, `refactor` | `erp-frontend` | `loop-fe` |
| `fix`, `refactor` | `bip-erp` | `loop-be` |
| `fix`, `refactor` | `mybharata-app` | `loop-mobile` |
| `fix`, `refactor` | brief menyentuh CI, compose, env, atau urutan deploy | `loop-devops` |
| `fix`, `refactor` | repo lain | `loop-fix` / `loop-refactor` (cadangan) |

`test` dan `docs` sengaja tetap lintas lapisan: QA menguji lapisan mana pun, dan dok tinggal di
vault. `loop-devops` menang atas lapisan bila briefnya memang soal jalur rilis, bukan soal layar
atau handler; ia **tidak punya shell** dan hanya menyiapkan perintah untuk manusia.
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

Dua brief berarti **dua worktree**, satu per repo, dibuat lebih dulu sebelum §2. Keduanya berdiri
sendiri, jadi tak ada berkas yang diperebutkan dan tak ada stash yang perlu dipakai bersama.

## 2. Eksekutor

Dispatch `Agent` dengan `subagent_type` = peran hasil §0, `run_in_background: false`. Prompt wajib
memuat, dalam bentuk path absolut:

```
Brief: <path brief>
Worktree: <path worktree>   (atau: vault architecture-draft, branch main)
Repo: <nama repo>  Branch: <branch>
Skill yang relevan untuk dibaca dulu: <daftar .claude/skills/<x>/SKILL.md yang cocok, boleh kosong>
Titik mulai (file:line yang sudah diketahui dari bagian Konteks brief, boleh kosong bila brief tak punya satu pun): <salin anchor file:line dari `## Konteks yang diketahui` brief>
Percobaan: 1 dari 3
```

**Anchor `file:line` itu titik mulai, bukan pagar.** Eksekutor tetap boleh membaca berkas utuh
atau rentang lain bila perlu; jangan pernah menulis larangan "hanya baca rentang ini" ke prompt
eksekutor, satu perbaikan yang salah karena konteks kurang jauh lebih mahal daripada token yang
dihemat. Orkestrator sudah mengukur anchor itu sendiri saat menulis brief (bagian `## Konteks
yang diketahui`); meneruskannya cuma memberi eksekutor tempat berpijak, bukan mekanisme baru.

**Bila `Agent` menjawab "Agent type '<peran>' not found"**: sesi ini lahir sebelum kit yang
memperkenalkan peran itu di-init (peran per lapisan masuk di 1.24.0, agen loop pertama di 1.15.0).
⚠️ **Coba sekali lagi di giliran berikutnya sebelum memutuskan restart.** Diukur 2026-09-21:
sesudah `init` dijalankan di tengah sesi, `loop-fe` ditolak "not found" pada giliran yang sama,
lalu **terbaca sendiri pada giliran berikutnya tanpa restart apa pun**. Bila giliran berikutnya
masih menolak, barulah **restart sesi**. Jalan darurat
satu kali: dispatch `general-purpose` dengan seluruh isi `.claude/agents/<peran>.md` (tanpa
frontmatter) sebagai pembuka prompt, lalu catat `agen` di log judge sebagai
`general-purpose(<peran>)`; jangan jadikan ini kebiasaan, model dan batas tools-nya berbeda.
⚠️ Untuk `loop-devops` jalan darurat ini **tidak sah**: `general-purpose` punya shell, sementara
seluruh gerbang peran itu justru terletak pada ketiadaan shell. Restart sesi, atau kerjakan manual.

Pilih skill relevan dari `.claude/skills/`: `migrasi-tabel-hris` untuk halaman daftar erp-frontend,
`deploy-bip-erp` hanya untuk `loop-devops`, `audit-keamanan` bila brief menyebut auth/RBAC/izin.
Catat daftar itu; ia masuk log judge sebagai `skills_dibaca`.

**Jangan menyuruh eksekutor membaca `rules/team-memory.md`.** Isinya sudah ada di konteks tiap
subagent lewat `CLAUDE.md` (diukur 2026-09-21); menyuruhnya membaca ulang hanya membakar satu
panggilan tool untuk isi yang sudah dipegangnya.

### Dua brief sekaligus (paralel)

`/kerjakan <a.md> <b.md>` menjalankan keduanya bersamaan. Periksa **tiga syarat** sebelum dispatch,
dan bila satu saja tidak terpenuhi, jalankan berurutan sesuai urutan yang ditulis `/brief`:

1. **Repo-nya berbeda.** Dua brief di repo yang sama selalu satu per satu.
2. **Tiap brief menulis `Paralel: aman`.** Ragu berarti `tidak`, dan `tidak` berarti berurutan.
   Brief lama yang ditulis sebelum kit 1.24.0 **tidak punya field ini sama sekali**; itu dibaca
   sebagai `tidak`, bukan sebagai izin. Jangan menambahkan fieldnya sendiri demi meloloskan.
3. **Bila keduanya menyentuh satu endpoint yang sama**, kedua brief memuat blok `## Kontrak`
   dengan isi identik. Tanpa blok itu, pasangan BE dan FE dijalankan berurutan, BE dulu.

Caranya: dispatch kedua `Agent` **dalam satu pesan** (dua tool call sekaligus), bukan
`run_in_background`. Keduanya selesai lebih dulu, baru §3 dijalankan **per brief**.

Batasnya satu mesin: dua eksekutor wajar, lebih dari itu mereka berebut CPU dan ada yang gagal
karena timeout, bukan karena kodenya salah. **Jangan menjalankan lebih dari dua brief sekaligus.**

Paralel di sini soal waktu MENGETIK, bukan waktu deploy. Untuk perubahan kontrak, BE tetap
di-deploy sebelum FE, dan itu ditulis di badan PR (§5).

## 3. Judge

**Bila dua brief dijalankan paralel, §3 sampai §6 dikerjakan PER BRIEF**, berurutan dan terpisah:
satu judge, satu loop perbaikan, satu commit, dan satu PR untuk masing-masing. Yang paralel hanya
eksekutornya di §2. Brief yang gagal tidak menahan pasangannya yang lolos.

Jalankan prosedur `/judge` (baca `.claude/commands/judge.md` dan lakukan) atas worktree itu dengan
brief yang sama. Hasilnya `lolos` (gerbang deterministik **dan** agen judge sama-sama lolos) dan
daftar `temuan`, `gagal_baru`.

Kirim verdict ke papan tim (best-effort; no-op bila mesin ini tidak menyalakan ingest):
```
& '.claude/hooks/loop-kirim.ps1' -Jenis judge.verdict -BriefSlug <slug> -Data '{"percobaan":<n>,"lolos":<true|false>,"temuan_kritis":<k>,"durasi_gerbang":<detik>}'
```
(in-process dengan `&`, bukan `powershell -File`; alasannya di komentar skrip)

Tulis log `.task-plans/judge/<slug>-<n>.json`:

```json
{ "brief": "<path>", "worktree": "<path>", "branch": "...", "percobaan": n, "waktu": "<UTC ISO>",
  "gerbang": <hasil gerbang.ps1>, "verdict": <JSON judge>, "lolos": true|false,
  "skills_dibaca": ["..."], "agen": "<peran hasil §0, mis. loop-fe>",
  "keputusan_lanjut": "ulangi" | "berhenti_lolos" | "berhenti_gagal",
  "titik_mulai": "<anchor file:line dari §2, apa adanya>" | "kosong" }
```

Field `agen` ditulis apa adanya karena ia yang membuat angka pengulangan bisa dibandingkan
antar-peran nanti: apakah spesialis lapisan benar-benar lebih jarang ditolak judge daripada
eksekutor domain generik. Tanpa field itu, klaim "peran spesialis mempercepat" tak bisa diukur.

`keputusan_lanjut` ditulis **saat log ini dibuat**, bukan di akhir run, dan itu seluruh gunanya.
Status akhir memang sudah dicatat di `## Hasil` milik brief (§4 dan §5), tetapi catatan itu ditulis
di ujung, jadi run yang terputus di tengah tak meninggalkan apa pun. Diperiksa 2026-09-23 atas tiga
brief yang berhenti: dua menuliskannya dengan benar, satu masih memuat placeholder template.
Dengan field ini, log percobaan-1 berbunyi `ulangi` yang tidak punya pasangan log percobaan-2
**membuktikan** run-nya terputus — satu-satunya cara membedakan "sudah diulang dan tetap gagal"
dari "tak pernah sempat diulang". Tanpa pembedaan itu mutu pemulihan kesalahan tak bisa
dievaluasi sama sekali.

Pemetaannya ditetapkan, jangan ditebak: `berhenti_lolos` bila §3 menghasilkan lolos; `ulangi` bila
gagal dan percobaan < 3; `berhenti_gagal` bila gagal pada percobaan ke-3. Nilai yang tidak jujur
membatalkan seluruh gunanya — `ulangi` yang ditulis pada percobaan terakhir membuat run yang
selesai wajar terbaca sebagai run yang terputus.

`titik_mulai` mencatat anchor `file:line` yang benar-benar dikirim ke prompt eksekutor di §2, apa
adanya, atau literal `"kosong"` bila brief itu sendiri tak punya satu pun di bagian Konteks. Field
ini **deskriptif, bukan gerbang**: log `kosong` bukan kegagalan dan tidak menahan apa pun — brief
tanpa `file:line` di Konteksnya itu sah (`brief.md:51`, "Konteks kosong lebih jujur daripada
Konteks karangan"), dan memaksanya terisi hanya akan mengundang karangan yang lebih buruk daripada
kosong. Gunanya murni supaya token antar-run bisa dibandingkan tahu run mana yang benar-benar
membawa anchor dan run mana yang fieldnya kosong, bukan menuntut brief selalu punya satu.

## 4. Loop perbaikan

Bila **gagal** dan percobaan < 3: dispatch ulang **peran yang sama** dengan prompt yang sama plus
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
   - **Urutan deploy**, wajib ditulis bila brief ini separuh dari pasangan yang berbagi blok
     `## Kontrak`: sebut PR pasangannya dan tegaskan **BE di-deploy sebelum FE**. Paralel di §2
     hanya soal waktu mengetik; yang menentukan aman atau tidaknya di produksi adalah urutan ini,
     dan ia harus terbaca oleh yang menekan tombol merge.
   - `Dasar keputusan: <isi field Sumber brief>` — ADR/dok yang memutuskan, atau `tidak ada`.
     Ia yang membuat gerbang merge berhenti jadi klik buta: yang menekan merge bisa membantah
     premisnya di titik terakhir. Terukur 2026-09-23, nol `reviewDecision` tercatat pada 634 PR
     dalam 30 hari.
   - Baris penutup: *Dibuat oleh AI Engineering Loop (agent-kit). Merge tetap keputusan manusia (ADR 0077 §1).*
5. Cetak URL PR. Tambahkan `## Hasil` di brief: percobaan, verdict, URL PR. Kirim ke papan tim:
   ```
   & '.claude/hooks/loop-kirim.ps1' -Jenis loop.pr -BriefSlug <slug> -Data '{"repo":"<repo>","number":<nomor PR>}'
   ```

Vault (domain docs): stage **per nama berkas**, commit, `build-vault-index.py --check` (regenerasi
lewat `/index-vault` bila basi), `git merge origin/main` bila remote maju, push `main`. Tanpa PR.

⛔ **Jalur vault TIDAK berhenti di PR**, jadi ia tak punya tombol merge tempat seorang manusia bisa
membantah premisnya, dan gerbang deterministiknya lolos lewat daftar-izin `RepoTanpaGerbang`.
Karena itu badan commit vault **wajib** memuat `Dasar keputusan: <isi field Sumber brief>` — di
jalur ini itu satu-satunya tempat premisnya tercatat. Brief vault ber-`Sumber: tidak ada` adalah
`ragu`, dan `ragu` sudah berhenti menunggu persetujuan di §0.

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
