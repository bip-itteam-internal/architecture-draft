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
- `skills/` — skill tim (disalin `init` → `.claude/skills/`). Kini: `migrasi-tabel-hris`.
- `rules/` — `team-memory.md` (ingatan tim bersama; **di-import langsung** oleh CLAUDE.md dari vault via `@../architecture-draft/.agent-kit/rules/team-memory.md` — update cukup `git pull`, tak perlu re-init).
- `templates/` — `workspace-CLAUDE.md` (jadi `erp/CLAUDE.md`).
- `init.ps1` / `init.sh` — pemasang.
- `VERSION` — versi kit.
- `docs/` — design & plan.

## Changelog

- **1.6.0** — skill tim pertama: **`/migrasi-tabel-hris`** (folder `skills/` baru, disalin `init` → `.claude/skills/`). Prosedur memindahkan halaman daftar ke struktur tabel HRIS beserta jebakan yang sudah terbukti menggigit dan gerbang verifikasi. **Butuh re-init** untuk dapat skill-nya. `rules/team-memory.md` ikut diperbarui (jebakan tabel/filter + peringatan gerbang CI erp-frontend mati) — bagian itu menyebar cukup dengan `git pull`, tanpa re-init.
- **1.4.0** — command **`/skills`**: cek skill/plugin Claude Code rekomendasi tim (superpowers, code-review, dataviz, frontend-design, deep-research) vs terpasang; tawarkan install yang kurang (user konfirmasi, agent yang install). Butuh re-init untuk dapat command-nya.
- **1.3.0** — team-memory kini **di-import langsung dari vault** (`@../architecture-draft/.agent-kit/rules/team-memory.md`) alih-alih disalin ke `.claude/rules/`; `init` tak lagi menyalin `rules/`. Efek: update ingatan tim cukup `git pull architecture-draft` — **tanpa re-run init**. (Re-init sekali untuk adopsi mekanisme baru; `.claude/rules/` lama bisa dihapus, tak dipakai.)
- **1.2.1** — `rules/team-memory.md`: tambah konvensi `pnpm`, gotchas (vault creds intentional, repo mybharata rename, RBAC `system_roles`=modul & atasan di `work_data`), perjelas auto-push (FE/mybharata tak auto-push).
- **1.2.0** — tambah `rules/team-memory.md` (ingatan tim bersama: gotchas, konvensi, sumber-kebenaran); `init` menyalin `rules/` → `.claude/rules/`; `workspace-CLAUDE.md` meng-`@import` file itu supaya ter-load tiap sesi.
- **1.1.0** — tambah `/ask`: tanya-jawab read-only grounded ke vault + kode, sebut sumber & status, sarankan `/sync-docs` bila ada gap dok.
- **1.0.1** — session-start tak lagi salah lapor "ketinggalan dari remote" saat local justru _ahead_ (kini bandingkan ke merge-base); re-run init mem-_prune_ file `commands/`/`hooks/` yang sudah dihapus di kit baru (bukan cuma menimpa).
- **1.0.0** — rilis awal: 6 command flow arch-first, hooks, init lintas-OS.
