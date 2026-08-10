# ERP Agent Kit

Gaya kerja koding ber-AI yang seragam untuk tim ERP Bharata. Landasannya arsitektur
draf (`architecture-draft`). Semua dev pakai Claude Code dengan flow & tooling yang sama.

## Onboarding (3 langkah)

1. Clone `architecture-draft` + project yang digarap sebagai **sibling** di dalam folder `erp/`:
   ```
   erp/
   ├── architecture-draft/   (vault ini)
   └── <project>/            (mis. bip-erp)
   ```
2. Buka folder `erp/` di Claude Code, jalankan init sekali:
   - Windows:  `powershell -ExecutionPolicy Bypass -File architecture-draft\.agent-kit\init.ps1`
   - mac/linux: `bash architecture-draft/.agent-kit/init.sh`
3. Mulai task: `/start-task <deskripsi>`.

## Flow wajib (per task)

`/start-task` → `/plan` → `/implement` → `/review` → `/sync-docs` → `/wrap`

## Update standar

`git -C architecture-draft pull` lalu jalankan ulang init. Session-start hook akan
mengingatkan bila versi kit terpasang ≠ versi terbaru.

## Isi kit

- `commands/` — 6 slash command flow + `/ask` (recall read-only, sebut sumber) + `/skills` (cek/install skill plugin rekomendasi tim).
- `hooks/` — session-start (info flow + cek versi/staleness) & pre-commit-reminder.
- `skills/` — skill tim (disalin `init` → `.claude/skills/`). Kini: `migrasi-tabel-hris`, `audit-keamanan`.
- `rules/` — `team-memory.md` (ingatan tim bersama; **di-import langsung** oleh CLAUDE.md dari vault via `@../architecture-draft/.agent-kit/rules/team-memory.md` — update cukup `git pull`, tak perlu re-init) plus tiga berkas prosedur yang **tidak** di-import dan dibaca on-demand supaya tak membakar konteks tiap sesi: `plan-checklist.md` (`/plan`), `review-checklist.md` (`/review`), dan `wrap-completion-gate.md` (`/wrap`).
- `templates/` — `workspace-CLAUDE.md` (jadi `erp/CLAUDE.md`).
- `init.ps1` / `init.sh` — pemasang.
- `VERSION` — versi kit.
- `docs/` — design & plan.

## Changelog

- **1.9.0** — **`/plan` dapat checklist, dan skill `audit-keamanan` lahir.** `rules/plan-checklist.md` (on-demand) menambah tiga bagian yang paling sering hilang dari rencana: **Apa yang Sudah Ada** (kode/komponen/master data/resolver yang sudah menyelesaikan sebagian masalah, dipakai ulang atau dibangun tandingannya dengan alasan), **Mode Kegagalan** (tiap jalur kode baru dijawab tiga pertanyaan — ada test? ada penanganan galat? senyap atau terlihat? — dan tidak-tidak-senyap ditandai celah kritis), serta matriks memilih jenis test (unit vs test handler lewat Fiber vs panggilan manual lewat gateway) dengan aturan regresi yang mutlak. Artefak `/plan` ikut bertambah dua bagian itu. Skill baru `audit-keamanan` diadaptasi dari `/cso` gstack: gerbang keyakinan 8/10 mode harian, verifikasi aktif lewat penelusuran kode (dilarang menyerang sistem hidup), sembilan fase yang disetel untuk Go/Fiber/MongoDB plus OWASP Top 10 dan STRIDE, dan **pengecualian keras** yang mendahului segalanya — plaintext credentials di dok IT vault DISENGAJA dan tidak boleh diflag. Laporannya wajib menyebut berapa kandidat yang dibuang, supaya auditnya bisa dipercaya. **Butuh re-init**; berkas checklist-nya sendiri menyebar cukup dengan `git pull`.
- **1.8.0** — **`/wrap` dapat gerbang kelengkapan, dan `/plan` mulai menulis artefak.** Prosedurnya di `rules/wrap-completion-gate.md` (on-demand): temukan artefak rencana, ekstrak itemnya, tentukan mode verifikasi (DIFF · LINTAS-REPO · KEADAAN-LUAR), klasifikasi SELESAI/SEBAGIAN/BELUM/BERUBAH/TAK TERVERIFIKASI, lalu gerbang yang **memblokir penutupan** saat ada item BELUM dan menuntut konfirmasi **per item** (bukan borongan) untuk yang tak terverifikasi. Tiga pemeriksaan khusus bip-erp berlaku selalu: fitur backend baru wajib sekali dipanggil lewat gateway (bukan cuma unit test), angka nol yang mencurigakan diperlakukan sebagai pertanyaan, dan konsekuensi deploy dua-container ikut tercatat. `/plan` kini menulis `.task-plans/<tanggal>-<slug>.md` setelah rencana disetujui, dengan bagian **Cara Verifikasi** dan **Di Luar Lingkup** yang wajib diisi. Tanpa artefak itu gerbangnya tak punya pembanding, dan `/wrap` akan bilang begitu terang-terangan alih-alih lolos diam-diam. Dipanen dari `ship/sections/plan-completion.md` gstack (MIT); mekanisme subagent, PR body, dan `/qa-only`-nya dibuang, mode lintas-repo diperkuat karena di sini menyentuh dua repo itu keadaan normal. **Butuh re-init**; berkas gerbangnya sendiri menyebar cukup dengan `git pull`.
- **1.7.0** — **`/review` naik kelas dari 5 baris jadi prosedur berjenjang.** Checklist barunya `rules/review-checklist.md` (dibaca on-demand, bukan di-import): dua pass (kritis/informasional), **gerbang verifikasi anti false-positive** (klaim "tidak ada" wajib dibuktikan Grep, klaim "consumer tak menangani" wajib dibuktikan dengan membaca berkasnya), heuristik fix-first, dan daftar yang JANGAN dilaporkan (creds vault disengaja, merah CI erp-frontend = startup failure, `pnpm test` main tak pernah hijau). Kategorinya dipanen dari checklist review [gstack](https://github.com/garrytan/gstack) (MIT) lalu diganti padanan Go/Fiber/MongoDB/Next.js, plus gotcha bip-erp yang sudah terbukti menggigit (rute akar vs prefix gateway, `c.JSON()` sebagai nilai galat, struct request tak ikut diperbarui, kategori inbox, `PATCH` menimpa penuh, i18n dua locale, `FilterTable` draft disemai sekali). **Butuh re-init** untuk `commands/review.md`; checklist-nya sendiri menyebar cukup dengan `git pull`.
- **1.6.0** — skill tim pertama: **`/migrasi-tabel-hris`** (folder `skills/` baru, disalin `init` → `.claude/skills/`). Prosedur memindahkan halaman daftar ke struktur tabel HRIS beserta jebakan yang sudah terbukti menggigit dan gerbang verifikasi. **Butuh re-init** untuk dapat skill-nya. `rules/team-memory.md` ikut diperbarui (jebakan tabel/filter + peringatan gerbang CI erp-frontend mati) — bagian itu menyebar cukup dengan `git pull`, tanpa re-init.
- **1.4.0** — command **`/skills`**: cek skill/plugin Claude Code rekomendasi tim (superpowers, code-review, dataviz, frontend-design, deep-research) vs terpasang; tawarkan install yang kurang (user konfirmasi, agent yang install). Butuh re-init untuk dapat command-nya.
- **1.3.0** — team-memory kini **di-import langsung dari vault** (`@../architecture-draft/.agent-kit/rules/team-memory.md`) alih-alih disalin ke `.claude/rules/`; `init` tak lagi menyalin `rules/`. Efek: update ingatan tim cukup `git pull architecture-draft` — **tanpa re-run init**. (Re-init sekali untuk adopsi mekanisme baru; `.claude/rules/` lama bisa dihapus, tak dipakai.)
- **1.2.1** — `rules/team-memory.md`: tambah konvensi `pnpm`, gotchas (vault creds intentional, repo mybharata rename, RBAC `system_roles`=modul & atasan di `work_data`), perjelas auto-push (FE/mybharata tak auto-push).
- **1.2.0** — tambah `rules/team-memory.md` (ingatan tim bersama: gotchas, konvensi, sumber-kebenaran); `init` menyalin `rules/` → `.claude/rules/`; `workspace-CLAUDE.md` meng-`@import` file itu supaya ter-load tiap sesi.
- **1.1.0** — tambah `/ask`: tanya-jawab read-only grounded ke vault + kode, sebut sumber & status, sarankan `/sync-docs` bila ada gap dok.
- **1.0.1** — session-start tak lagi salah lapor "ketinggalan dari remote" saat local justru _ahead_ (kini bandingkan ke merge-base); re-run init mem-_prune_ file `commands/`/`hooks/` yang sudah dihapus di kit baru (bukan cuma menimpa).
- **1.0.0** — rilis awal: 6 command flow arch-first, hooks, init lintas-OS.
