## Deskripsi

*Titik-masuk **"cara kerja"** tunggal untuk semua developer ERP Bharata — manusia **dan** AI agent — supaya satu visi. Dok ini **ringkas + menaut** ke dok detail (bukan menyalin), agar tidak jadi sumber-kebenaran ganda. Mulai onboarding dari sini, lalu ikuti link.*

> Dok meta root (tanpa prefix), sejajar [[README]] · [[HOMEPAGE]] · [[CLAUDE]] · [[SCRUM SPECS]] · [[ROADMAP]].

## 1. Prinsip (satu visi)

- **Arch-first**: baca dok arsitektur terkait di `architecture-draft/` **sebelum** menulis kode.
- **Grounded-in-code**: tulis/dokumentasikan hanya yang benar-benar ada; yang belum ada → **TBD**. Jangan mengarang.
- **Vault = sumber kebenaran arsitektur**; kode = sumber kebenaran implementasi. Keduanya dijaga selaras via `/sync-docs`.

## 2. Prasyarat workspace (PENTING)

Clone vault + repo kode sebagai **folder bersebelahan (sibling)** di bawah satu folder induk, lalu buka folder induk:

```
erp/                      ← working directory
├── architecture-draft/   ← vault dokumentasi (Obsidian)
├── bip-erp/              ← backend Go microservices
├── erp-frontend/         ← web (Next.js)
├── mybharata-app/        ← mobile (Flutter)
└── task-management/ · ideamiils/ · scraping/ · guestbook-system/
```

Tidak wajib semua repo — cukup vault + repo yang sedang digarap. Detail: [[CLAUDE]] §0 (vault) & struktur repo di [[HOMEPAGE]].

## 3. Tools

- **JS/TS**: **pnpm** (BUKAN npm/yarn).
- **Vault**: Obsidian (Open existing vault → folder `architecture-draft/`).
- **Backend**: Go + Fiber v2; jalan via **Docker Compose** (`bip-erp/docker-compose.yml` = entry point), MongoDB per-service + Redis + MinIO ([[DB - Overview and Notes]]).
- **Mobile**: Flutter.

## 4. Alur kerja per task (agent-kit)

Flow wajib tiap task: **`/start-task` → `/plan` → `/implement` → `/review` → `/sync-docs` → `/wrap`**

- Didefinisikan di `architecture-draft/.agent-kit/` (di-init ke `erp/.claude/`).
- `/start-task` memuat konteks arsitektur + kode relevan **sebelum** menulis kode (arch-first).
- `/sync-docs` menyinkronkan dok dengan perubahan kode (delegasi ke rulebook vault).

**Loop otonom untuk task kecil** (kit ≥ 1.15.0): `/brief <masalah>` → `/kerjakan <path brief>`. Agent membuat worktree di path pendek, mengerjakan lewat agen domain, dinilai `/judge` (gerbang mesin **dan** penilai, keduanya harus lolos), mengulang maksimum dua kali, lalu membuka **PR**. **Merge tetap manusia.** Pendukung: `/papan-sesi` (sesi mana mengerjakan apa), `/ekstrak-skill` (sesi → draft skill), `/supervise` (evaluasi loop → draft). Gerbang lokal: commit di branch utama repo kode **ditolak**; push menjalankan tsc/lint/build atau go build. Cara kerja dan batasnya: [[IT - Gerbang Repo dan Papan Sesi Agent]]; keputusannya: [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]].

## 5. Konvensi

- **Kode**: ikuti pola service yang ada (lihat runbook "tambah service baru" di [[IT - Runbooks]]); database-per-service + di belakang SSO/gateway ([[CORE - API Master Gateway]], [[CORE - SSO Flow]]).
- **Dokumentasi vault**: format `Prefix - Nama.md`, status marker (✅/⚠️/🟡/🔴), wikilink 0-broken, Bahasa Indonesia (istilah teknis English). Aturan lengkap: [[CLAUDE]] (rulebook) + prosedur [[IT - SOP Dokumentasi Vault]].
- **Glosarium istilah**: [[REF - Glossary]].

## 6. Git & rilis

- **Alur branch kode**: `feature → PR → main`. **Semua repo kode wajib PR**, nama branch utama apa pun (`main` maupun `master`). ⚠️ Kalimat lama "push ke `main` → deploy otomatis" **sudah tidak berlaku**: per 2026-09-06 seluruh workflow GitHub Actions di `bip-erp` dan `erp-frontend` berstatus `disabled_manually`, dan jalur deploy produksi belum terverifikasi mekanismenya; yang berlaku ada di [[IT - CI-CD]]. Deploy: [[RUN - Deploy Microservices bip-erp]] · [[RUN - Deploy Frontend ERP ke Produksi]] · mobile lewat Codemagic. Detail proses: [[SCRUM SPECS]] · [[IT - Runbooks]].
- **Vault (dok)**: selalu `git pull` sebelum push; **stage per-file** (`git add -- "Folder/Nama.md"`, JANGAN `git add -A`); pesan `docs: ...`; jangan commit `.obsidian/*`. ([[CLAUDE]] §8–§9)

## 7. Akses arsitektur

- **Utama (sekarang)**: vault lokal sebagai sibling (§2) dibuka di **Obsidian**; tersedia juga **wiki publish** di `architecture.bharatainternasional.com` (lihat [[README]]).
- **Mulai baca dari**: [[HOMEPAGE]] (peta) → dok domain terkait.
- **Akses via MCP** (untuk manajemen dan Claude di luar workspace): **sudah dibangun dan hidup di prod** sebagai [[Microservices - Vault MCP Service]] (baca dan tulis). Cara menyambungkan: [[RUN - Menyambungkan Claude ke Vault MCP]]. Kalimat lama "belum dibangun" di sini usang sejak 2026-08-27.

## 8. Onboarding hari-1 (checklist)

- [ ] Clone vault + repo yang akan digarap sebagai **sibling** (§2).
- [ ] Pasang tools (§3): pnpm, Obsidian, Go, Docker.
- [ ] **Pasang agent-kit**: dari folder `erp/`, jalankan init **sekali** — Windows `powershell -ExecutionPolicy Bypass -File architecture-draft\.agent-kit\init.ps1`; mac/linux `bash architecture-draft/.agent-kit/init.sh`. Lalu **restart sesi Claude Code** (hook dibaca saat sesi mulai). Tanpa ini, `/start-task … /sync-docs … /wrap` tak muncul di Claude Code, dan gerbang commit/push tidak terpasang. Detail + multi-project: [[RUN - Onboarding Developer Baru]].
- [ ] Buka vault di Obsidian → baca [[HOMEPAGE]] + [[CLAUDE]] (rulebook).
- [ ] Pahami alur kerja per task (§4) + konvensi (§5).
- [ ] Jalankan stack lokal bila perlu (`bip-erp/docker-compose.yml`; port di [[IT - Environment Inventory]]).
- [ ] Ambil task → mulai dengan `/start-task` (arch-first).

## Dokumen Terkait

- [[HOMEPAGE]] · [[CLAUDE]] · [[README]] · [[SCRUM SPECS]] · [[ROADMAP]]
- [[IT - SOP Dokumentasi Vault]] · [[IT - CI-CD]] · [[IT - Runbooks]] · [[IT - Environment Inventory]]
- [[DB - Overview and Notes]] · [[CORE - API Master Gateway]] · [[CORE - SSO Flow]] · [[REF - Glossary]]
