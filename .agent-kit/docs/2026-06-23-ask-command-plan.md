# `/ask` Command Implementation Plan (agent-kit v1.1.0)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tambah slash command `/ask` ke agent-kit — tanya-jawab read-only yang grounded ke vault + kode, selalu menyebut sumber.

**Architecture:** Satu file instruksi markdown `commands/ask.md` (seperti 6 command lain). Bump kit ke v1.1.0, perbarui README + changelog, tambah assertion jumlah command di test integrasi, lalu re-install ke `erp/`.

**Tech Stack:** Markdown (slash command), PowerShell (test/init). Tidak ada dependency baru.

**Spec:** `architecture-draft/.agent-kit/docs/2026-06-23-ask-command-design.md`

## Global Constraints

- File kit di `architecture-draft/.agent-kit/` (dot-folder).
- Bahasa Indonesia, istilah teknis English.
- `/ask` **READ-ONLY**: tidak pernah menulis/ubah dok atau kode; saran `/sync-docs` hanya teks, tidak dijalankan.
- Grounded-in-code: bila sumber tak ada → "tidak ditemukan", jangan mengarang.
- Commit stage **per-file** (`git add -- <path>`), JANGAN `git add -A`; jangan push (push di langkah finishing).
- Versi kit → `1.1.0`.

---

### Task 1: Tambah `/ask` command + bump versi + docs + test

**Files:**
- Create: `.agent-kit/commands/ask.md`
- Modify: `.agent-kit/VERSION` (→ `1.1.0`)
- Modify: `.agent-kit/README.md` (daftar isi kit + changelog)
- Modify: `.agent-kit/tests/test-init.ps1` (assertion jumlah command = 7)

**Interfaces:**
- Produces: command `/ask` terpasang ke `erp/.claude/commands/ask.md` saat init. Test menjamin jumlah `commands/*.md` = 7.

- [ ] **Step 1: Tambah assertion jumlah command ke test (RED dulu)**

Di `.agent-kit/tests/test-init.ps1`, sisipkan setelah baris `Check (Test-Path (Join-Path $claude 'commands/start-task.md')) 'commands tersalin'`:

```powershell
  $cmdCount = (Get-ChildItem (Join-Path $claude 'commands') -Filter *.md).Count
  Check ($cmdCount -eq 7) 'jumlah command = 7 (6 flow + /ask)'
```

- [ ] **Step 2: Jalankan test — verifikasi GAGAL (baru ada 6 command)**

Run:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\tests\test-init.ps1"
```
Expected: `FAIL jumlah command = 7 (6 flow + /ask)`, akhir `1 gagal`, exit 1. (RED — ask.md belum ada.)

- [ ] **Step 3: Buat `.agent-kit/commands/ask.md` (verbatim)**

```markdown
---
description: Tanya-jawab grounded atas vault + kode (read-only, sebut sumber)
argument-hint: <pertanyaan>
---

Jawab pertanyaan user secara grounded. READ-ONLY: JANGAN menulis/ubah dok atau kode apa
pun — tugasmu hanya menjawab + menyebut sumber.

Pertanyaan: $ARGUMENTS

Langkah:
1. Tentukan area pertanyaan. Buka `architecture-draft/CLAUDE.md` §7 (pemetaan repo→dokumen)
   untuk menemukan dok arsitektur relevan.
2. Baca dok vault terkait di `architecture-draft/`. Perhatikan status marker
   (§5: ✅ Implemented / ⚠️ ada catatan / 🟡 Konsep / 🔴 Stub).
3. Bila vault mencakup pertanyaan & konsisten dengan kode → jawab dari vault.
4. Bila vault diam ATAU terlihat usang vs kode → baca kode terkait di project aktif
   (lihat .claude/CLAUDE.md baris "Project aktif") untuk tetap menjawab.
5. Sajikan jawaban dengan format:
   - **Jawaban**: ringkas dan langsung.
   - **Sumber**: wikilink dok yang dibaca + `file:line` kode yang dipakai.
   - **Status**: ✅ terdokumentasi & cocok kode / ⚠️ dok ada tapi usang (sebut gap-nya) /
     🟡 hanya konsep/TBD / 🔴 tak terdokumentasi (dijawab dari kode).
   - **Saran**: bila ada gap dok, sarankan "jalankan /sync-docs untuk update dok <X>".
     JANGAN jalankan /sync-docs otomatis.
6. Bila tak ada di vault maupun kode → katakan jujur "tidak ditemukan", JANGAN mengarang
   (grounded-in-code §1).
```

- [ ] **Step 4: Bump VERSION → 1.1.0**

Isi `.agent-kit/VERSION` jadi (satu baris, tanpa newline akhir bila bisa):
```
1.1.0
```

- [ ] **Step 5: Update README.md**

Di `.agent-kit/README.md`, ganti baris daftar isi command:
```
- `commands/` — 6 slash command flow.
```
jadi:
```
- `commands/` — 6 slash command flow + `/ask` (recall read-only, sebut sumber).
```
lalu tambah entri changelog paling atas (di atas baris `- **1.0.1** …`):
```
- **1.1.0** — tambah `/ask`: tanya-jawab read-only grounded ke vault + kode, sebut sumber & status, sarankan `/sync-docs` bila ada gap dok.
```

- [ ] **Step 6: Jalankan test — verifikasi LULUS**

Run:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\tests\test-init.ps1"
```
Expected: semua `PASS ...` termasuk `PASS jumlah command = 7 (6 flow + /ask)`, akhir `Semua lulus`, exit 0. (GREEN.)

- [ ] **Step 7: Commit**

```powershell
cd "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git add -- ".agent-kit/commands/ask.md" ".agent-kit/VERSION" ".agent-kit/README.md" ".agent-kit/tests/test-init.ps1"
git commit -m "feat(agent-kit): /ask command (recall grounded, read-only) + v1.1.0"
```

---

### Task 2: Re-install ke `erp/` + verifikasi

**Files:**
- Generate (tidak di-commit): `erp/.claude/*`

**Interfaces:**
- Consumes: kit v1.1.0. Produces: instalasi terbarui di `erp/.claude` dengan 7 command.

- [ ] **Step 1: Jalankan init nyata**

Run:
```powershell
cd "c:\Data utama\Aplikasi\Office\erp"
powershell -NoProfile -ExecutionPolicy Bypass -File "architecture-draft\.agent-kit\init.ps1" -ActiveProject "bip-erp"
```
Expected: ringkasan "Agent-kit v1.1.0 terpasang".

- [ ] **Step 2: Verifikasi**

Run:
```powershell
$claude = "c:\Data utama\Aplikasi\Office\erp\.claude"
"ask.md ada     : " + (Test-Path "$claude\commands\ask.md")
"jumlah command : " + (Get-ChildItem "$claude\commands" -Filter *.md).Count
"kit-version    : " + (Get-Content "$claude\.kit-version")
```
Expected: `ask.md ada : True`, `jumlah command : 7`, `kit-version : 1.1.0`.

- [ ] **Step 3: Tidak ada commit** (erp/.claude artefak generate). Catat hasil di ringkasan.

---

## Self-Review

**Spec coverage:**
- `/ask` read-only grounded + format jawaban → Task 1 Step 3. ✅
- Vault-first + verifikasi kode + lapor gap + saran /sync-docs (tak auto) → ask.md langkah 3-5. ✅
- Tidak menulis dok/kode → ditegaskan di header ask.md + Global Constraints. ✅
- VERSION → 1.1.0 → Task 1 Step 4. ✅
- README + changelog → Task 1 Step 5. ✅
- Test assertion command count → Task 1 Step 1/6. ✅
- Re-install ke erp/ → Task 2. ✅

**Placeholder scan:** Tidak ada TODO/TBD eksekusi; semua langkah berisi konten nyata.

**Type/nama konsistensi:** `ask.md`, `$cmdCount`, jumlah `7`, `1.1.0` dipakai konsisten lintas Task 1/2.
