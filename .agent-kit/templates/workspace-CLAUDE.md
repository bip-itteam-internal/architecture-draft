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
- **i18n dua bahasa (`erp-frontend`)**: SEMUA teks user-facing **baru** WAJIB lewat `react-i18next` — `t("domain.key")`, key ditaruh di **dua** file `src/i18n/locales/id.ts` **dan** `en.ts`. **JANGAN hardcode** string yang tampil ke user. Default **Indonesia**; **istilah teknis lazim English biarkan English** di kedua locale (Dashboard, Export, KPI, Score, dll) — jangan dipaksa Indonesia. Tanggal/bulan/angka pakai `toLocaleDateString(intlLocale(lang))`, bukan hardcode `"id-ID"`. Aturan lengkap: **ADR 0010** di vault (`Decisions/ADR - 0010 Internasionalisasi (i18n) Dua Bahasa.md`).

## Ingatan tim (shared memory)
Indeks memori bersama antar-agent/dev (gotchas, konvensi, sumber-kebenaran) — di-import LANGSUNG dari vault; update cukup `git pull architecture-draft` (tanpa re-run init):
@../architecture-draft/.agent-kit/rules/team-memory.md
