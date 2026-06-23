# CLAUDE.md — Workspace ERP (di-generate oleh agent-kit; jangan edit manual)

> Di-generate oleh `architecture-draft/.agent-kit/init`. Untuk ubah standar: edit sumber
> di `.agent-kit/` lalu jalankan ulang init. Versi kit terpasang: __KIT_VERSION__

## Landasan
`architecture-draft/` adalah **sumber kebenaran arsitektur** (Obsidian vault). Baca dok
terkait DULU sebelum menulis kode. Aturan dokumentasi: `architecture-draft/CLAUDE.md`.

## Project aktif
__ACTIVE_PROJECT__

## Flow wajib (per task)
`/start-task` → `/plan` → `/implement` → `/review` → `/sync-docs` → `/wrap`

## Aturan turunan
- JS/TS: pakai **pnpm**, bukan npm/yarn.
- Grounded-in-code: jangan mengarang; yang belum ada tandai TBD.
- Dokumentasi disinkronkan via `/sync-docs` (delegasi ke rulebook vault).
