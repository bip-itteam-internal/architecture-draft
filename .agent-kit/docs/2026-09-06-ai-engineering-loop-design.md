# Desain: AI Engineering Loop di agent-kit (v1.15.0)

- **Status**: 🟡 Diusulkan, keputusan pemilik 2026-09-06, kode ditulis pada tanggal yang sama
- **Tanggal**: 2026-09-06
- **Versi kit target**: 1.15.0 (dari 1.14.0)
- **Keputusan arsitektur**: `Decisions/ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak` (bagian Revisi 2026-09-06)
- **Cara kerja untuk pembaca non-kit**: `IT/IT - Gerbang Repo dan Papan Sesi Agent`

## Konteks

Pemilik proses menyerahkan dokumen arsitektur *AI Engineering Loop System* (tiga lapis: eksekusi,
Judges, Supervisor; orkestrasi; skill extraction; dashboard) dan, setelah analisis menolaknya dan
keberatannya disampaikan, **menegaskan ulang** agar dibangun sesuai dokumen. Yang diukur hari itu
menentukan bentuknya: nol gerbang otomatis di repo kode, hook pre-commit bermatcher `Bash`
sehingga mati di mesin PowerShell, 35 worktree terdaftar dengan 31 sudah merged tanpa ada yang
tahu, `test-init.ps1` pernah merah beberapa rilis tanpa terdeteksi.

## Substitusi yang diputuskan (dan kenapa)

| Dokumen | Di kit ini | Alasan |
|---|---|---|
| Trigger.dev (orkestrasi, observability) | Agen kustom `.claude/agents/`, Agent tool, papan sesi berkas | layanan berbayar ditolak pemilik; masalahnya 4+ sesi di satu mesin, bukan penjadwalan lintas mesin |
| Fable/Claude/DeepSeek/Kimi/GLM | `sonnet` eksekutor, `opus` judge, `fable` supervisor + ekstraktor | tidak ada API key vendor lain; tingkatan Claude memenuhi fungsi yang sama |
| Judges sebagai agen | **dua lapis**: gerbang deterministik (`gerbang.ps1`) DAN agen `loop-judge` read-only; lolos hanya bila keduanya lolos | agen tidak berwenang membatalkan mesin; ini yang mencegah "mengakali satu metrik" |
| Triangulated metrics (test pass rate) | test **vs baseline bertanggal** (`baseline/<repo>.json`) | `pnpm test` main tidak pernah hijau penuh; angka mentah tak bisa dipakai |
| Supervisor memperbarui skill otomatis | `loop-supervisor` menulis **draft** ke `skills/_draft/` + laporan; `/supervise --terapkan` dijalankan manusia | tidak ada metrik kualitas skill; skill yang salah menyebar ke seluruh tim lewat `init` |
| Skill extraction dari ekspor sesi | `transkrip-ringkas` (deterministik, menolak bila skema tak terurai) → `loop-ekstrak-skill` → draft | skema JSONL dinyatakan internal oleh dok resmi; ringkasan kosong yang "berhasil" adalah kelas 200-berisi-nol |
| Dashboard World Monitor | `papan-sesi.ps1` → tabel + HTML statis | separuh panel rujukan tak punya sumber data di sini (dok domain § TBD) |
| Deploy/commit otomatis | agent berhenti di **PR** | ADR 0077 §1; `main` pernah mendarat di produksi lewat jalur tak terverifikasi |

## Bentuk

```
/brief <masalah>  ->  .task-plans/briefs/<tgl>-<slug>.md   (Quick Brief Spec, templates/brief.md)
/kerjakan <brief>
   routing deterministik (kata kunci) -> LLM hanya bila ambigu
   worktree-baru.ps1  -> ~/wt/<fe|be>-<slug>, branch <domain>/<slug>, pnpm install
   Agent loop-<domain> (sonnet)  ------------------------------+
   /judge:  gerbang.ps1 (tsc/lint/build | go build, test vs baseline)  |  loop perbaikan
            Agent loop-judge (opus, Read/Grep/Glob)  ->  <<VERDICT>> JSON  |  maks 2x
   lolos?  ne -> ulang dgn temuan ------------------------------+
           ya -> commit conventional -> push (pre-push hook) -> gh pr create -> BERHENTI
/papan-sesi      papan-sesi.ps1 atas .task-plans/sesi/*.json (ditulis hook SessionStart/UserPromptSubmit/SessionEnd)
/ekstrak-skill   transkrip-ringkas.ps1 -> Agent loop-ekstrak-skill (fable) -> skills/_draft/
/supervise       Agent loop-supervisor (fable) -> docs/supervise-<tgl>.md + skills/_draft/
```

Gerbang lokal yang benar-benar menolak:

- `hooks/pre-commit-gate.ps1|.sh` — `PreToolUse` matcher `Bash|PowerShell`; **exit 2** bila `git
  commit` di branch default repo kode (dari `origin/HEAD`, fallback `main|master`); vault
  dikecualikan. Exit 2 dipilih karena memblokir apa pun isi stdout, jadi JSON salah bentuk tidak
  bisa membuat gerbang gagal-terbuka.
- `hooks/githooks/pre-push` — dipasang `init` lewat `core.hooksPath` absolut per repo kode; Node:
  `pnpm tsc`, `lint`, `build` (`AGENTKIT_SKIP_BUILD=1` melewati build dan mencetaknya); Go: `go
  build ./...` per `services/<x>` tersentuh, semua bila `shared-library` tersentuh.

## Keputusan kecil yang punya alasan

- **Path worktree pendek, bukan `isolation: worktree` bawaan**: worktree di path panjang membuat
  `pnpm install` "sukses" tanpa rollup dan vitest mati (team-memory).
- **`-ceq`, bukan `-eq`, di tokenizer gate**: `-eq` PowerShell menyamakan `-C` dan `-c`; `-c
  core.fsmonitor=false` yang dipakai seluruh tim pernah menimpa path repo sehingga gerbang
  gagal-terbuka. Tertangkap kontrol positif `test-init.ps1`.
- **Satu lib untuk bentuk berkas sesi (`sesi-lib.ps1|.sh`) dan satu untuk pengurai test
  (`gerbang-lib.ps1|.py`)**: baseline yang ditulis satu OS harus terbaca OS lain; dua salinan
  pengurai berarti gerbang bisa menolak yang benar.
- **Harness test memakai `Start-Process`, bukan pipeline**: PS 5.1 membungkus stderr anak jadi
  ErrorRecord, dan dengan `$ErrorActionPreference='Stop'` pesan PENOLAKAN yang benar justru
  menghentikan test.
- **`add -N` sebelum diff untuk judge**: berkas baru ikut tampil; aman karena worktree terisolasi.
- **Baseline menolak menulis bila keluaran test tak terurai**: "0 gagal" dari pengurai yang mati
  terlihat sama dengan hijau.

## Yang sengaja tidak dibangun

Trigger.dev; vendor model lain; agent merge; supervisor auto-apply; dashboard web live; CI
GitHub/branch protection (paket akun + keputusan biaya); suite E2E baru (hanya baseline yang ada).

## Verifikasi

`tests/test-init.ps1`: init di sandbox, agents/githooks tersalin, `core.hooksPath` terpasang,
hook sesi menulis/menyentuh/menutup berkas sesi, **kontrol positif** gate exit 2 di `main`,
**kontrol negatif** exit 0 di branch fitur dan di vault, `transkrip-ringkas` menolak sampah,
matcher memuat `PowerShell`. Bukti akhir: satu `/kerjakan` sungguhan sampai PR.
