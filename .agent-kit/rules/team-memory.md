# Ingatan Tim — Shared Memory (bip-erp)

> Indeks memori **BERSAMA** antar-agent/dev, di-load tiap sesi via `@rules/team-memory.md` di `CLAUDE.md`.
> **Sumber** = kit (`architecture-draft/.agent-kit/rules/`) → disalin ke `.claude/rules/` saat `init` (dikelola kit; **jangan edit** file di `.claude/`, edit sumbernya lalu re-run init).
> Beda dari **auto-memory** `~/.claude/.../memory/` yang **privat per-mesin**. Fakta durable & layak-bagi → taruh di sini atau promosikan ke vault.

## Konvensi build & tooling
- **JS/TS pakai `pnpm`** (bukan npm/yarn) — berlaku semua repo JS (erp-frontend, mybharata, website-bharata, dll).

## Gotchas lingkungan (dev Windows)
- **Git hang**: `core.fsmonitor` bikin git menggantung di path ber-spasi (`c:\Data utama\...`). Selalu jalankan `git -c core.fsmonitor=false ...` (atau sekali: `git config --global core.fsmonitor false`). Perintah yang men-scan worktree (`status`/`diff`) tetap lambat karena `node_modules` → pakai perintah ref-only (`rev-parse`, `log`, `diff <a>..<b>`) bila bisa.
- **`.claude/` BUKAN git repo** (root `erp/` bukan repo). Isinya di-generate `init` dari agent-kit. Ubah standar/hook/command/**rules** → edit **`architecture-draft/.agent-kit/`** lalu re-run `init`; JANGAN edit file di `.claude/` (akan ketimpa saat init).
- **bip-erp auto-push**: commit lokal otomatis ter-push ke origin → perlakukan **commit = published**. Repo lain — `erp-frontend`, `mybharata` — **TIDAK** auto-push (push manual / izin eksplisit user).

## Konvensi git & rilis
- Branch **per service** dari `main` (mis. `feat/<service>`); jangan commit langsung di `main`.
- **Tanpa** trailer `Co-Authored-By` di pesan commit.
- **Deploy BE sebelum FE** untuk perubahan kontrak (FE fallback aman bila field baru belum ada).

## Konvensi FE / UI (erp-frontend · mybharata)
- Loading konten/field pakai **ShimmerBox**, bukan `CircularProgressIndicator`/spinner.
- Saat menyamakan UI → **reuse komponen shared** (pakai adapter), jangan bikin tiruan look-alike.
- **i18n dua bahasa** (id+en via react-i18next), default Indonesia; istilah teknis lazim English biarkan English. Detail: **ADR 0010** di vault.

## Gotchas repo & RBAC
- **Repo mybharata di-rename** `hris_bharata` → **`my-bharata`** (`github.com/bip-itteam-internal/my-bharata`). Remote `origin` lokal lama masih menunjuk nama lama tapi push/`gh` jalan via redirect; rapikan: `git remote set-url origin https://github.com/bip-itteam-internal/my-bharata.git`.
- **RBAC `system_roles`**: key = **kode MODUL** (`it`,`hris`,`finance`,`ga`,…), **BUKAN** nama departemen (pemetaan modul→nama dept di `shared-library/common/roles.go` `deptKeyToNames`; `space.division` simpan nama dept). `system_roles` = hak akses **modul/menu**, **bukan hierarki org** — **atasan/supervisor departemen ada di `work_data`** (`is_supervisor:true` + `department`), bukan di `system_roles`.

## Memori & sumber kebenaran
- **Vault `architecture-draft`** = shared knowledge base — baca dok terkait **DULU**. Fakta arsitektur/status proyek → dok domain / ADR / RUN di vault.
- **Plaintext credentials di IT docs vault** (`IT - Server, VMs and Databases`, `IT - Monitoring System`) **DISENGAJA** (referensi akses internal tim IT) — **jangan** diflag sebagai isu keamanan / jangan usulkan rotasi/scrub.
- **Auto-memory lokal** (`~/.claude/.../memory/`) = scratch **privat** per-mesin; tidak ter-share.
- **Naik kelas**: fakta lokal yang berguna untuk tim → promosikan ke vault (grounded) atau ke file ini.

## Bahasa
- Balasan AI ke user & dokumentasi: **Bahasa Indonesia**; istilah teknis lazim English biarkan English.
