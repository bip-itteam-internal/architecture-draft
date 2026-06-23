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

- `commands/` — 6 slash command flow + `/ask` (recall read-only, sebut sumber).
- `hooks/` — session-start (info flow + cek versi/staleness) & pre-commit-reminder.
- `templates/` — `workspace-CLAUDE.md` (jadi `erp/CLAUDE.md`).
- `init.ps1` / `init.sh` — pemasang.
- `VERSION` — versi kit.
- `docs/` — design & plan.

## Changelog

- **1.1.0** — tambah `/ask`: tanya-jawab read-only grounded ke vault + kode, sebut sumber & status, sarankan `/sync-docs` bila ada gap dok.
- **1.0.1** — session-start tak lagi salah lapor "ketinggalan dari remote" saat local justru _ahead_ (kini bandingkan ke merge-base); re-run init mem-_prune_ file `commands/`/`hooks/` yang sudah dihapus di kit baru (bukan cuma menimpa).
- **1.0.0** — rilis awal: 6 command flow arch-first, hooks, init lintas-OS.
