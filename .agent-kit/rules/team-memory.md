# Ingatan Tim — Shared Memory (bip-erp)

> Indeks memori **BERSAMA** antar-agent/dev, di-load tiap sesi via `@rules/team-memory.md` di `CLAUDE.md`.
> **Sumber** = kit (`architecture-draft/.agent-kit/rules/`) → disalin ke `.claude/rules/` saat `init` (dikelola kit; **jangan edit** file di `.claude/`, edit sumbernya lalu re-run init).
> Beda dari **auto-memory** `~/.claude/.../memory/` yang **privat per-mesin**. Fakta durable & layak-bagi → taruh di sini atau promosikan ke vault.

## Konvensi build & tooling
- **JS/TS pakai `pnpm`** (bukan npm/yarn) — berlaku semua repo JS (erp-frontend, mybharata, website-bharata, dll).

## Gotchas lingkungan (dev Windows)
- **Git hang**: `core.fsmonitor` bikin git menggantung di path ber-spasi (`c:\Data utama\...`). Selalu jalankan `git -c core.fsmonitor=false ...` (atau sekali: `git config --global core.fsmonitor false`). Perintah yang men-scan worktree (`status`/`diff`) tetap lambat karena `node_modules` → pakai perintah ref-only (`rev-parse`, `log`, `diff <a>..<b>`) bila bisa.
- **`.claude/` BUKAN git repo** (root `erp/` bukan repo). Isinya di-generate `init` dari agent-kit. Ubah standar/hook/command/**rules** → edit **`architecture-draft/.agent-kit/`** lalu re-run `init`; JANGAN edit file di `.claude/` (akan ketimpa saat init).
- **Semua repo wajib PR** — termasuk `bip-erp`. Jangan commit langsung ke `main`. Alur: buat branch `feat/<nama>` dari `origin/main` → commit → push branch → buat PR. Info lama "bip-erp auto-push" adalah **SALAH** dan sudah dihapus.

## Konvensi git & rilis
- Branch **per service** dari `main` (mis. `feat/<service>`); jangan commit langsung di `main`.
- **Tanpa** trailer `Co-Authored-By` di pesan commit.
- **Deploy BE sebelum FE** untuk perubahan kontrak (FE fallback aman bila field baru belum ada).

## Konvensi FE / UI (erp-frontend · mybharata)
- Loading konten/field pakai **ShimmerBox**, bukan `CircularProgressIndicator`/spinner.
- Saat menyamakan UI → **reuse komponen shared** (pakai adapter), jangan bikin tiruan look-alike.
- **i18n dua bahasa** (id+en via react-i18next), default Indonesia; istilah teknis lazim English biarkan English. Detail: **ADR 0010** di vault.

## Kalender terpusat (WAJIB untuk fitur bertanggal)
- **Fitur yang punya tanggal/jadwal/tenggat yang perlu dilihat orang WAJIB mendaftarkan feed ke `calendar-service`, DILARANG bikin halaman kalender sendiri.** Tiap kalender tambahan membawa salinan aturan visibilitasnya sendiri, dan salinan itu yang menyimpang diam-diam sampai ada yang melihat agenda yang tak boleh dilihatnya. Contoh yang harus diarahkan ke sini: rencana `GET /bookings/calendar` di [[GA - Asset Loan & Room Booking]].
- **Cara daftar**: tambah `GET /internal/calendar-feed?from&to` di service Anda (atau cuma tambah `kind` baru bila endpoint-nya sudah ada) → tambah satu baris di `providerRegistry` (`services/calendar/providers.go`) + env `<SERVICE>_MODULE_URL` di blok `calendar-service` compose. **Tanpa perubahan frontend.**
- **Penyaringan hak akses dikerjakan DI SERVICE SUMBER**, kalender sengaja tak punya aturan visibilitas sendiri. Ingat `/internal/` **bukan** privat: gateway tetap meneruskannya dari internet, jadi tiap feed wajib memeriksa identitas pemanggil sendiri.
- **URL provider JANGAN masuk map yang divalidasi `ValidateInternalURL`** (panic bila kosong = seluruh kalender padam hanya karena satu service belum di-deploy). URL kosong = provider dilewati diam-diam.
- **`deep_link` wajib** di tiap item: kalender itu **pintu, bukan tujuan**, jadi feed tak perlu menyalin detail agenda. **`all_day` dipisah dari waktu** (cuti/libur seharian vs interview berjam), dan **`id` berprefiks sumber** (`<source>:<kind>:<id>`) karena ObjectId antar-service bisa bertabrakan.
- **Jangan menulis ulang resolusi milik modul lain** untuk feed; panggil resolver aslinya. Feed shift memakai resolver yang sama dengan halaman Jadwal karena urutan menangnya berlapis (roster menimpa jadwal dasar, lalu Tukar Shift menimpa keduanya).
- **Gateway MEMBUANG prefix `/api/<module>`** sebelum meneruskan (`routes.Reroute` → `strings.TrimPrefix`). Jadi rute **akar modul** didaftarkan di `app.Get("/")`, BUKAN `app.Get("/<module>")`; `/api/calendar/events/:id` jadi `/events/:id`. Salah menaruhnya = 404 `Cannot GET /` untuk SEMUA permintaan lewat jalur normal, sementara unit test tetap hijau karena memanggil path lokal langsung ke Fiber. Terjadi nyata di calendar-service 2026-08-06 (lolos ke dev, diperbaiki PR [#1041](https://github.com/bip-itteam-internal/bip-erp/pull/1041)). Tulis test yang MEREPRODUKSI pemotongan itu, bukan sekadar menuliskan path yang benar.
- Detail lengkap + checklist perencanaan: **[[Microservices - Calendar Service]]** di vault. Status kini: irisan 1 **live di DEV** dan terverifikasi lewat gateway; PROD belum.

## Gotchas backend Go (berlaku SEMUA service bip-erp)
- **`c.JSON()` mengembalikan `nil` saat sukses**, jadi memakainya sebagai NILAI GALAT selalu rusak. `return nil, c.Status(400).JSON(x)` sebenarnya `return nil, nil`; penjaga `if err != nil` di pemanggil tak pernah menyala, eksekusi lanjut dengan pointer nil, lalu memanik. Service tidak mati (fasthttp memutus koneksi per-permintaan) tapi **gateway membalas 502**. Pola aman: kembalikan `(*T, bool)` dan pemanggil `return nil` saat `ok` false, karena responsnya sudah ditulis. Mengembalikan error non-nil juga salah: Fiber lalu menjalankan ErrorHandler dan menulis respons KEDUA. Ditemukan di prod-path form-builder 2026-08-06 (PR [#1018](https://github.com/bip-itteam-internal/bip-erp/pull/1018)); seluruh jalur galat `/forms/:id*` membalas 502 sejak entah kapan.
- **Fitur bisa MERGED, DEPLOYED, dan tetap mustahil dipakai** bila lapisan pengikatan request tak ikut diperbarui. Form berulang di form-builder lengkap sampai cron dan teruji, tapi `formRequest` tak punya field `recurrence` sehingga tak seorang pun bisa menyalakannya; diam selama 3 hari "live", ketahuan cuma karena uji end-to-end. **Tiap fitur wajib sekali dijalankan lewat gateway sebelum diklaim selesai**, dan angka nol yang mencurigakan (0 dokumen padahal fitur sudah live) diperlakukan sebagai pertanyaan, bukan kabar baik.
- **Test fungsi murni TIDAK menangkap cacat glue handler.** form-builder punya 183 test hijau saat bug di atas hidup, karena tak satu pun melewati Fiber. Tambahkan minimal satu test `app.Test(httptest.NewRequest(...))` untuk jalur galat tiap handler — tak butuh database bila kasusnya gagal di penguraian ID. Sekelas dengan gotcha `primitive.A` (fixture rakitan tangan tak pernah melewati decode BSON).

## Gotchas repo & RBAC
- **Repo mybharata di-rename** `hris_bharata` → **`my-bharata`** (`github.com/bip-itteam-internal/my-bharata`). Remote `origin` lokal lama masih menunjuk nama lama tapi push/`gh` jalan via redirect; rapikan: `git remote set-url origin https://github.com/bip-itteam-internal/my-bharata.git`.
- **RBAC `system_roles`**: key = **kode MODUL** (`it`,`hris`,`finance`,`ga`,…), **BUKAN** nama departemen (pemetaan modul→nama dept di `shared-library/common/roles.go` `deptKeyToNames`; `space.division` simpan nama dept). `system_roles` = hak akses **modul/menu**, **bukan hierarki org** — **atasan/supervisor departemen ada di `work_data`** (`is_supervisor:true` + `department`), bukan di `system_roles`.

## Memori & sumber kebenaran
- **Vault `architecture-draft`** = shared knowledge base — baca dok terkait **DULU**. Fakta arsitektur/status proyek → dok domain / ADR / RUN di vault.
- **Plaintext credentials di IT docs vault** (`IT - Server, VMs and Databases`, `IT - Monitoring System`) **DISENGAJA** (referensi akses internal tim IT) — **jangan** diflag sebagai isu keamanan / jangan usulkan rotasi/scrub.
- **Auto-memory lokal** (`~/.claude/.../memory/`) = scratch **privat** per-mesin; tidak ter-share.
- **Naik kelas**: fakta lokal yang berguna untuk tim → promosikan ke vault (grounded) atau ke file ini.

## Skill & tooling AI (Claude Code)
- **Command tim ERP** (`/start-task`→`/plan`→`/implement`→`/review`→`/sync-docs`→`/wrap` + `/ask`): dari **agent-kit**, BUKAN plugin. Onboarding: clone `architecture-draft` + project sibling → jalankan `init`. Sumber: `.agent-kit/commands/`.
- **Skill umum** (superpowers: brainstorming/TDD/systematic-debugging/writing-plans, dataviz, frontend-design, code-review, deep-research, dll.): **plugin per-mesin**, tak ikut repo. Marketplace resmi Anthropic (`claude-plugins-official`) **sudah pre-registered**. Install: `/plugin` (tab Discover) atau CLI `claude plugin install <nama>@claude-plugins-official` (mis. `superpowers`). Kelola: `/plugin list`, `claude plugin enable|disable|uninstall <nama>@<marketplace>`. (Cek nama marketplace asli plugin di `/plugin` → tab Marketplaces.)
- **Standarkan set plugin tim**: `enabledPlugins` di `.claude/settings.json` (project scope) auto-enable saat clone + trust. Tapi `.claude/settings.json` ERP **di-generate `init`** (bisa ketimpa) → standarisasi resmi tim idealnya lewat agent-kit (init menulis `enabledPlugins`) — **belum dilakukan (TBD)**.
- **Bikin skill custom tim** (shareable): taruh `SKILL.md` di `.agent-kit/skills/<nama>/` → `init` menyalin ke `.claude/skills/`; bump versi kit → tim `git pull` + re-init.
- **Update file ingatan-tim ini**: edit `.agent-kit/rules/team-memory.md` di vault → tim cukup `git pull architecture-draft` (di-import langsung sejak kit v1.3.0; **tanpa** re-init).

## Bahasa
- Balasan AI ke user & dokumentasi: **Bahasa Indonesia**; istilah teknis lazim English biarkan English.
