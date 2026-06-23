# ERP Agent Kit — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bangun "agent-kit" di `architecture-draft/.agent-kit/` berisi 6 slash command flow, hooks, template, dan script init, sehingga semua dev punya gaya kerja koding ber-AI yang seragam dan grounded ke arsitektur draf.

**Architecture:** Kit hidup di dot-folder dalam Obsidian vault (Obsidian abaikan dot-folder, git lacak). Script `init` menyalin commands/skills/hooks ke `erp/.claude/` (project-level) dan generate `erp/CLAUDE.md` + `settings.json`. Update standar menyebar lewat `git pull` + re-init.

**Tech Stack:** Markdown (slash commands), PowerShell 5.1 (Windows, utama) + Bash (mac/linux) untuk init & hooks, JSON (settings.json). Tidak ada dependency baru.

**Spec:** `architecture-draft/.agent-kit/docs/2026-06-23-erp-agent-kit-design.md`

## Global Constraints

- Semua file kit hidup di `architecture-draft/.agent-kit/` (dot-folder; Obsidian mengabaikannya).
- Bahasa dokumen & pesan: **Bahasa Indonesia**, istilah teknis tetap English.
- Commit ke vault: **stage per-file** (`git add -- "path"`), **JANGAN `git add -A`**; pesan commit `docs: ...` atau `feat(agent-kit): ...`; **jangan push** kecuali user minta.
- Target install init = **project-level** `erp/.claude/` (bukan `~/.claude/`).
- `erp/.claude/` adalah artefak generate — **tidak** di-commit ke repo manapun.
- TDD di `/implement` = **default-adaptif** (test-first bila ada test infra; jangan paksa berhenti bila belum ada).
- Pre-commit hook = **reminder non-blocking**, bisa dimatikan (`-NoPreCommitHook`).
- JS/TS: **pnpm**, bukan npm/yarn.
- `skills/` dikosongkan di rilis-1 (init menyalinnya hanya bila ada).

---

### Task 1: Skeleton kit (VERSION + README onboarding)

**Files:**
- Create: `architecture-draft/.agent-kit/VERSION`
- Create: `architecture-draft/.agent-kit/README.md`

**Interfaces:**
- Produces: `VERSION` berisi semver `1.0.0` (dibaca init & session-start hook). `README.md` = onboarding 3 langkah.

- [ ] **Step 1: Buat VERSION**

```
1.0.0
```

- [ ] **Step 2: Buat README.md**

```markdown
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

- `commands/` — 6 slash command flow.
- `hooks/` — session-start (info flow + cek versi/staleness) & pre-commit-reminder.
- `templates/` — `workspace-CLAUDE.md` (jadi `erp/CLAUDE.md`).
- `init.ps1` / `init.sh` — pemasang.
- `VERSION` — versi kit.
- `docs/` — design & plan.
```

- [ ] **Step 3: Commit**

```powershell
cd "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git add -- ".agent-kit/VERSION" ".agent-kit/README.md"
git commit -m "feat(agent-kit): skeleton kit (VERSION + README onboarding)"
```

---

### Task 2: Enam slash command flow

**Files:**
- Create: `architecture-draft/.agent-kit/commands/start-task.md`
- Create: `architecture-draft/.agent-kit/commands/plan.md`
- Create: `architecture-draft/.agent-kit/commands/implement.md`
- Create: `architecture-draft/.agent-kit/commands/review.md`
- Create: `architecture-draft/.agent-kit/commands/sync-docs.md`
- Create: `architecture-draft/.agent-kit/commands/wrap.md`

**Interfaces:**
- Produces: 6 file slash command. Konsumen = Claude Code setelah init menyalinnya ke `erp/.claude/commands/`. Dipakai berurutan sebagai flow.

- [ ] **Step 1: Buat commands/start-task.md**

```markdown
---
description: Mulai task baru — muat konteks arsitektur + kode relevan sebelum menulis kode
argument-hint: <deskripsi task>
---

Kamu memulai task baru di workspace ERP. WAJIB arch-first: JANGAN menulis kode apa pun
sampai konteks dipahami dan user mengonfirmasi.

Task dari user: $ARGUMENTS

Langkah:
1. Baca `.claude/CLAUDE.md`, ambil baris "Project aktif".
2. Buka `architecture-draft/CLAUDE.md` §7 (pemetaan repo→dokumen) → tentukan dokumen
   arsitektur yang relevan dengan project & task ini.
3. Baca dokumen arsitektur terkait di `architecture-draft/`. Perhatikan status marker
   (✅ Implemented / ⚠️ ada catatan / 🟡 Konsep / 🔴 Stub) untuk menilai mana yang nyata.
4. Baca kode terkait di project aktif (modul/handler/service yang tersentuh).
5. Ringkas:
   - **Task**: <ringkasan>
   - **Landasan arsitektur**: dok yang dibaca + poin penting + status marker
   - **Kode relevan**: file/fungsi + perannya
   - **Gap/risiko**: di mana rencana arsitektur ≠ implementasi saat ini
   - **Pertanyaan terbuka**: yang perlu diklarifikasi sebelum lanjut
6. BERHENTI. Tunggu konfirmasi user sebelum `/plan`. Jangan menulis kode di tahap ini.
```

- [ ] **Step 2: Buat commands/plan.md**

```markdown
---
description: Susun rencana implementasi grounded ke arsitektur
---

Lanjutan dari /start-task. Susun rencana implementasi yang grounded ke arsitektur.

Langkah:
1. Pastikan ada konteks dari /start-task. Bila belum, minta user jalankan /start-task dulu.
2. Susun rencana bertahap:
   - Perubahan per file (path eksak) + alasan.
   - Langkah-langkah kecil yang masing-masing bisa diuji.
   - Test yang akan ditulis (lihat TDD adaptif di /implement).
   - Risiko & dependensi antar-service (rujuk dok arsitektur).
3. Tandai EKSPLISIT bila rencana menyimpang dari arsitektur draf (sebut dok mana & gap-nya).
4. Sajikan rencana, minta persetujuan user sebelum /implement.
```

- [ ] **Step 3: Buat commands/implement.md**

```markdown
---
description: Eksekusi rencana — TDD default-adaptif
---

Eksekusi rencana dari /plan.

Aturan TDD (default-adaptif):
- Jika project punya test infra (mis. *_test.go untuk Go, atau test runner di
  package.json untuk JS): tulis test dulu (gagal) → implement minimal → test hijau → ulang.
- Jika project BELUM punya test infra sama sekali: jangan berhenti; implement sesuai
  rencana, lalu sarankan menambah test untuk unit baru.

Langkah:
1. Untuk JS/TS pakai **pnpm**, BUKAN npm/yarn (lihat .claude/CLAUDE.md).
2. Kerjakan per langkah kecil dari rencana; commit sering (per langkah logis).
3. Jaga perubahan dalam lingkup rencana. Temuan di luar lingkup → catat untuk /review,
   jangan langsung dikerjakan.
```

- [ ] **Step 4: Buat commands/review.md**

```markdown
---
description: Review diff — bug + konsistensi vs arsitektur
---

Review pekerjaan sebelum /sync-docs & /wrap.

Langkah:
1. Lihat diff project aktif (perubahan sesi ini, belum/baru di-commit).
2. Cek dua dimensi:
   a. **Korrektness/bug**: error handling, edge case, regresi.
   b. **Konsistensi arsitektur**: apakah implementasi menyimpang dari dok di
      `architecture-draft/`? Endpoint/kontrak/ownership data sesuai? (rujuk dok dari /start-task)
3. Sajikan temuan: severity + lokasi (file:line) + saran fix.
4. Bila ada temuan kritis, sarankan kembali ke /implement; bila bersih, lanjut /sync-docs.
```

- [ ] **Step 5: Buat commands/sync-docs.md**

```markdown
---
description: Sinkronkan architecture-draft dengan kode (delegasi ke rulebook vault)
---

Sinkronkan dokumentasi `architecture-draft` dengan perubahan kode.

PENTING: Aturan dokumentasi LENGKAP ada di `architecture-draft/CLAUDE.md`. Command ini
hanya orkestrasi — IKUTI rulebook itu, JANGAN buat aturan dokumentasi sendiri.

Langkah:
1. Baca `architecture-draft/CLAUDE.md` (grounded-in-code §1, konvensi nama §3, wikilink §4,
   status marker §5, template §6, repo→doc §7, alur sync §8, aturan git §9).
2. `git -C architecture-draft pull` (vault dikerjakan paralel banyak orang).
3. Tentukan dok terdampak dari diff kode (pakai §7).
4. Update/buat dok sesuai template & konvensi; perbarui status marker.
5. Verifikasi 0 broken wikilink (§4).
6. Commit per-file (`git add -- "Folder/Nama.md"`, JANGAN `git add -A`), pesan `docs: ...`.
   Jangan push otomatis kecuali user minta.
```

- [ ] **Step 6: Buat commands/wrap.md**

```markdown
---
description: Tutup task — checklist akhir + commit project
---

Tutup task.

Checklist (konfirmasi tiap poin ke user):
- [ ] Test hijau (atau dicatat kenapa belum ada test).
- [ ] /review sudah dijalankan; temuan kritis ditangani.
- [ ] /sync-docs sudah dijalankan; dok architecture-draft sinkron, 0 broken wikilink.
- [ ] Perubahan sesuai lingkup task.

Langkah:
1. Tampilkan ringkasan perubahan project (diff terkompres).
2. Commit project sesuai konvensi repo tsb (ikuti gaya pesan commit yang sudah ada).
   Stage file relevan saja. Jangan push kecuali user minta.
3. Ringkas: apa yang berubah di kode + apa yang berubah di dok.
```

- [ ] **Step 7: Verifikasi 6 file ada**

Run:
```powershell
Get-ChildItem "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\commands" -Name
```
Expected: `implement.md plan.md review.md start-task.md sync-docs.md wrap.md`

- [ ] **Step 8: Commit**

```powershell
cd "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git add -- ".agent-kit/commands/start-task.md" ".agent-kit/commands/plan.md" ".agent-kit/commands/implement.md" ".agent-kit/commands/review.md" ".agent-kit/commands/sync-docs.md" ".agent-kit/commands/wrap.md"
git commit -m "feat(agent-kit): 6 slash command flow (arch-first)"
```

---

### Task 3: Template workspace-CLAUDE.md

**Files:**
- Create: `architecture-draft/.agent-kit/templates/workspace-CLAUDE.md`

**Interfaces:**
- Produces: template dengan placeholder `__KIT_VERSION__` & `__ACTIVE_PROJECT__` yang diisi `init` saat generate `erp/CLAUDE.md`.

- [ ] **Step 1: Buat templates/workspace-CLAUDE.md**

```markdown
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
```

- [ ] **Step 2: Commit**

```powershell
cd "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git add -- ".agent-kit/templates/workspace-CLAUDE.md"
git commit -m "feat(agent-kit): template workspace CLAUDE.md"
```

---

### Task 4: Hook scripts (session-start + pre-commit-reminder)

**Files:**
- Create: `architecture-draft/.agent-kit/hooks/session-start.ps1`
- Create: `architecture-draft/.agent-kit/hooks/session-start.sh`
- Create: `architecture-draft/.agent-kit/hooks/pre-commit-reminder.ps1`
- Create: `architecture-draft/.agent-kit/hooks/pre-commit-reminder.sh`

**Interfaces:**
- Produces: hook scripts. `init` mendaftarkannya di `erp/.claude/settings.json`. session-start: SessionStart event → cetak `additionalContext`. pre-commit-reminder: PreToolUse(Bash) → bila command mengandung `git commit`, cetak reminder (non-blocking).
- CWD saat hook jalan = workspace `erp/`. Maka vault = `./architecture-draft`, versi terpasang = `./.claude/.kit-version`.

- [ ] **Step 1: Buat hooks/session-start.ps1**

```powershell
# session-start.ps1 — info flow + cek versi kit + cek staleness vault
$ErrorActionPreference = 'SilentlyContinue'
$vault = Join-Path $PWD 'architecture-draft'
$kitVerFile = Join-Path $vault '.agent-kit/VERSION'
$instFile   = Join-Path $PWD '.claude/.kit-version'

$lines = @('Flow wajib: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap')

if (Test-Path $kitVerFile) {
  $kitVer = (Get-Content $kitVerFile -Raw).Trim()
  $instVer = if (Test-Path $instFile) { (Get-Content $instFile -Raw).Trim() } else { 'unknown' }
  if ($kitVer -ne $instVer) {
    $lines += "Update agent-kit tersedia (terpasang: $instVer, terbaru: $kitVer). Jalankan ulang architecture-draft/.agent-kit/init.ps1."
  } else {
    $lines += "Agent-kit v$instVer (terkini)."
  }
}

git -C $vault fetch --quiet 2>$null
$localRev  = (git -C $vault rev-parse '@' 2>$null)
$remoteRev = (git -C $vault rev-parse '@{u}' 2>$null)
if ($localRev -and $remoteRev -and ($localRev -ne $remoteRev)) {
  $lines += 'architecture-draft ketinggalan dari remote. Jalankan: git -C architecture-draft pull'
}

$ctx = ($lines -join "`n")
@{ hookSpecificOutput = @{ hookEventName = 'SessionStart'; additionalContext = $ctx } } |
  ConvertTo-Json -Compress -Depth 5
exit 0
```

- [ ] **Step 2: Buat hooks/session-start.sh**

```bash
#!/usr/bin/env bash
# session-start.sh — info flow + cek versi kit + cek staleness vault
vault="$PWD/architecture-draft"
kit_ver_file="$vault/.agent-kit/VERSION"
inst_file="$PWD/.claude/.kit-version"

ctx="Flow wajib: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap"

if [ -f "$kit_ver_file" ]; then
  kit_ver="$(tr -d '[:space:]' < "$kit_ver_file")"
  inst_ver="unknown"; [ -f "$inst_file" ] && inst_ver="$(tr -d '[:space:]' < "$inst_file")"
  if [ "$kit_ver" != "$inst_ver" ]; then
    ctx="$ctx | Update agent-kit tersedia (terpasang: $inst_ver, terbaru: $kit_ver). Jalankan ulang .agent-kit/init.sh."
  else
    ctx="$ctx | Agent-kit v$inst_ver (terkini)."
  fi
fi

git -C "$vault" fetch --quiet >/dev/null 2>&1 || true
local_rev="$(git -C "$vault" rev-parse @ 2>/dev/null || true)"
remote_rev="$(git -C "$vault" rev-parse '@{u}' 2>/dev/null || true)"
if [ -n "$local_rev" ] && [ -n "$remote_rev" ] && [ "$local_rev" != "$remote_rev" ]; then
  ctx="$ctx | architecture-draft ketinggalan dari remote. Jalankan: git -C architecture-draft pull"
fi

# ctx tidak mengandung tanda kutip ganda → aman ditempel ke JSON string
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$ctx"
exit 0
```

- [ ] **Step 3: Buat hooks/pre-commit-reminder.ps1**

```powershell
# pre-commit-reminder.ps1 — PreToolUse(Bash) reminder non-blocking sebelum git commit
$ErrorActionPreference = 'SilentlyContinue'
$raw = [Console]::In.ReadToEnd()
try { $data = $raw | ConvertFrom-Json } catch { exit 0 }
$cmd = $data.tool_input.command
if ($cmd -and ($cmd -match 'git\s+commit')) {
  $msg = 'Reminder sebelum commit: sudah /sync-docs? wikilink resolve (0 broken)? test hijau?'
  @{ hookSpecificOutput = @{ hookEventName = 'PreToolUse'; additionalContext = $msg } } |
    ConvertTo-Json -Compress -Depth 5
}
exit 0
```

- [ ] **Step 4: Buat hooks/pre-commit-reminder.sh**

```bash
#!/usr/bin/env bash
# pre-commit-reminder.sh — PreToolUse(Bash) reminder non-blocking sebelum git commit
raw="$(cat)"
case "$raw" in
  *"git commit"*)
    msg='Reminder sebelum commit: sudah /sync-docs? wikilink resolve (0 broken)? test hijau?'
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"%s"}}\n' "$msg"
    ;;
esac
exit 0
```

- [ ] **Step 5: Smoke-test session-start.ps1 di workspace nyata**

Run (dari `erp/`):
```powershell
cd "c:\Data utama\Aplikasi\Office\erp"
powershell -NoProfile -ExecutionPolicy Bypass -File "architecture-draft\.agent-kit\hooks\session-start.ps1"
```
Expected: satu baris JSON valid berisi `"hookEventName":"SessionStart"` dan `additionalContext` yang memuat teks "Flow wajib:". (Versi/staleness boleh apa adanya.)

- [ ] **Step 6: Smoke-test pre-commit-reminder.ps1**

Run:
```powershell
'{"tool_name":"Bash","tool_input":{"command":"git commit -m x"}}' | powershell -NoProfile -ExecutionPolicy Bypass -File "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\hooks\pre-commit-reminder.ps1"
```
Expected: satu baris JSON berisi "Reminder sebelum commit". Lalu tes negatif:
```powershell
'{"tool_name":"Bash","tool_input":{"command":"ls"}}' | powershell -NoProfile -ExecutionPolicy Bypass -File "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\hooks\pre-commit-reminder.ps1"
```
Expected: tidak ada output (exit 0).

- [ ] **Step 7: Commit**

```powershell
cd "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git add -- ".agent-kit/hooks/session-start.ps1" ".agent-kit/hooks/session-start.sh" ".agent-kit/hooks/pre-commit-reminder.ps1" ".agent-kit/hooks/pre-commit-reminder.sh"
git commit -m "feat(agent-kit): hooks session-start + pre-commit-reminder (ps1 & sh)"
```

---

### Task 5: init.ps1 (Windows) + test integrasi

**Files:**
- Create: `architecture-draft/.agent-kit/init.ps1`
- Create: `architecture-draft/.agent-kit/tests/test-init.ps1`

**Interfaces:**
- Consumes: `VERSION`, `commands/`, `hooks/`, (opsional) `skills/`, `templates/workspace-CLAUDE.md` dari kit.
- Produces: `erp/.claude/{commands,hooks,skills?}/`, `erp/.claude/settings.json`, `erp/.claude/CLAUDE.md`, `erp/.claude/.kit-version`.
- Param: `-Workspace <path>` (default CWD), `-ActiveProject <nama>` (lewati prompt; dipakai test), `-NoPreCommitHook` (matikan reminder hook).
- `settings.json` digenerate **programatik** via ConvertTo-Json (bukan string-replace) agar path Windows ter-escape benar di JSON — deviasi kecil dari spec yang menyebut "template", hasil akhirnya sama.

- [ ] **Step 1: Tulis test integrasi dulu (gagal) — tests/test-init.ps1**

```powershell
# test-init.ps1 — integrasi: jalankan init di sandbox, assert artefak generate
$ErrorActionPreference = 'Stop'
$kitRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)  # .agent-kit
$tmp = Join-Path $env:TEMP ("agentkit-test-" + [guid]::NewGuid().ToString('N').Substring(0,8))
$fail = 0
function Check($cond, $name) { if ($cond) { Write-Host "PASS $name" } else { Write-Host "FAIL $name"; $script:fail++ } }
try {
  # sandbox: vault tiruan berisi kit nyata (copy) + project tiruan
  $svVault = Join-Path $tmp 'architecture-draft'
  New-Item -ItemType Directory -Force -Path $svVault | Out-Null
  Copy-Item -Path $kitRoot -Destination (Join-Path $svVault '.agent-kit') -Recurse -Force
  Set-Content -Path (Join-Path $svVault 'CLAUDE.md') -Value '# stub vault rulebook' -Encoding UTF8
  git -C $svVault init -q
  $proj = Join-Path $tmp 'demo-proj'; New-Item -ItemType Directory -Force -Path $proj | Out-Null
  git -C $proj init -q

  & (Join-Path $svVault '.agent-kit/init.ps1') -Workspace $tmp -ActiveProject 'demo-proj' -NoPreCommitHook | Out-Null

  $claude = Join-Path $tmp '.claude'
  Check (Test-Path (Join-Path $claude 'commands/start-task.md')) 'commands tersalin'
  Check (Test-Path (Join-Path $claude 'hooks/session-start.ps1')) 'hooks tersalin'
  Check (Test-Path (Join-Path $claude 'settings.json')) 'settings.json ada'
  $cm = Get-Content (Join-Path $claude 'CLAUDE.md') -Raw
  Check ($cm -match 'demo-proj') 'CLAUDE.md memuat project aktif'
  Check ($cm -notmatch '__ACTIVE_PROJECT__') 'placeholder project terisi'
  Check ($cm -notmatch '__KIT_VERSION__') 'placeholder versi terisi'
  $st = Get-Content (Join-Path $claude 'settings.json') -Raw | ConvertFrom-Json
  Check ($null -ne $st.hooks.SessionStart) 'settings punya SessionStart'
  Check ($null -eq $st.hooks.PreToolUse) 'NoPreCommitHook menghapus PreToolUse'
  $kv = (Get-Content (Join-Path $claude '.kit-version') -Raw).Trim()
  $ver = (Get-Content (Join-Path $kitRoot 'VERSION') -Raw).Trim()
  Check ($kv -eq $ver) '.kit-version sama dgn VERSION'
}
finally {
  if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
}
if ($fail -gt 0) { Write-Host "$fail gagal"; exit 1 } else { Write-Host 'Semua lulus'; exit 0 }
```

- [ ] **Step 2: Jalankan test — verifikasi GAGAL (init.ps1 belum ada)**

Run:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\tests\test-init.ps1"
```
Expected: error karena `init.ps1` belum ada (file not found) → exit ≠ 0.

- [ ] **Step 3: Tulis init.ps1**

```powershell
#requires -version 5
param(
  [string]$Workspace = (Get-Location).Path,
  [string]$ActiveProject,
  [switch]$NoPreCommitHook
)
$ErrorActionPreference = 'Stop'

$kitRoot = Split-Path -Parent $PSCommandPath          # ...\architecture-draft\.agent-kit
$ws = (Resolve-Path $Workspace).Path

# 1. validasi vault sibling
$vault = Join-Path $ws 'architecture-draft'
if (-not (Test-Path $vault)) {
  Write-Error "architecture-draft tidak ditemukan sebagai sibling di '$ws'. Clone dulu vault-nya."
  exit 1
}

# 2. info staleness (best-effort, tidak menggagalkan)
try { git -C $vault fetch --quiet 2>$null } catch {}

# 3. deteksi project sibling (folder ber-.git, selain architecture-draft)
$projects = @(Get-ChildItem -Path $ws -Directory -ErrorAction SilentlyContinue | Where-Object {
  (Test-Path (Join-Path $_.FullName '.git')) -and $_.Name -ne 'architecture-draft'
} | Select-Object -ExpandProperty Name)

$active = $ActiveProject
if (-not $active) {
  if ($projects.Count -eq 0) { Write-Error 'Tidak ada project sibling ber-.git. Clone project dulu.'; exit 1 }
  Write-Host 'Project terdeteksi:'
  for ($i=0; $i -lt $projects.Count; $i++) { Write-Host ("  [{0}] {1}" -f $i, $projects[$i]) }
  $sel = Read-Host 'Pilih nomor/nama project aktif'
  if ($sel -match '^\d+$' -and [int]$sel -lt $projects.Count) { $active = $projects[[int]$sel] } else { $active = $sel }
}

# 4. salin commands/hooks/skills → erp/.claude
$claude = Join-Path $ws '.claude'
New-Item -ItemType Directory -Force -Path $claude | Out-Null
foreach ($d in 'commands','hooks','skills') {
  $src = Join-Path $kitRoot $d
  if (Test-Path $src) {
    $dst = Join-Path $claude $d
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    Copy-Item -Path (Join-Path $src '*') -Destination $dst -Recurse -Force
  }
}

# 5. settings.json (programatik → JSON-escape path benar)
$ssCmd = 'powershell -NoProfile -ExecutionPolicy Bypass -File "{0}"' -f (Join-Path $claude 'hooks\session-start.ps1')
$pcCmd = 'powershell -NoProfile -ExecutionPolicy Bypass -File "{0}"' -f (Join-Path $claude 'hooks\pre-commit-reminder.ps1')
$hooks = @{ SessionStart = @(@{ hooks = @(@{ type='command'; command=$ssCmd }) }) }
if (-not $NoPreCommitHook) {
  $hooks['PreToolUse'] = @(@{ matcher='Bash'; hooks=@(@{ type='command'; command=$pcCmd }) })
}
(@{ hooks = $hooks } | ConvertTo-Json -Depth 8) | Set-Content -Path (Join-Path $claude 'settings.json') -Encoding UTF8

# 6. generate erp/CLAUDE.md dari template
$kitVer = (Get-Content (Join-Path $kitRoot 'VERSION') -Raw).Trim()
$cm = Get-Content (Join-Path $kitRoot 'templates\workspace-CLAUDE.md') -Raw
$cm = $cm.Replace('__KIT_VERSION__', $kitVer).Replace('__ACTIVE_PROJECT__', $active)
Set-Content -Path (Join-Path $claude 'CLAUDE.md') -Value $cm -Encoding UTF8

# 7. .kit-version
Set-Content -Path (Join-Path $claude '.kit-version') -Value $kitVer -Encoding UTF8

# 8. ringkasan
Write-Host ""
Write-Host "OK. Agent-kit v$kitVer terpasang ke $claude"
Write-Host "Project aktif: $active"
Write-Host "Flow: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap"
if ($NoPreCommitHook) { Write-Host "(pre-commit reminder: NONAKTIF)" } else { Write-Host "(pre-commit reminder: aktif)" }
```

- [ ] **Step 4: Jalankan test — verifikasi LULUS**

Run:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\tests\test-init.ps1"
```
Expected: semua baris `PASS ...`, akhir `Semua lulus`, exit 0.

- [ ] **Step 5: Commit**

```powershell
cd "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git add -- ".agent-kit/init.ps1" ".agent-kit/tests/test-init.ps1"
git commit -m "feat(agent-kit): init.ps1 (Windows) + test integrasi"
```

---

### Task 6: init.sh (mac/linux) — paritas

**Files:**
- Create: `architecture-draft/.agent-kit/init.sh`

**Interfaces:**
- Sama dengan init.ps1: argumen via flag `--workspace`, `--active-project`, `--no-precommit-hook`. Mendaftarkan hook varian `.sh`.

- [ ] **Step 1: Tulis init.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

ws="$PWD"; active=""; no_precommit=0
while [ $# -gt 0 ]; do
  case "$1" in
    --workspace) ws="$2"; shift 2;;
    --active-project) active="$2"; shift 2;;
    --no-precommit-hook) no_precommit=1; shift;;
    *) echo "arg tak dikenal: $1"; exit 1;;
  esac
done

kit_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # .agent-kit
vault="$ws/architecture-draft"
[ -d "$vault" ] || { echo "architecture-draft tidak ada sebagai sibling di '$ws'. Clone dulu."; exit 1; }

git -C "$vault" fetch --quiet >/dev/null 2>&1 || true

# deteksi project sibling ber-.git
mapfile -t projects < <(for d in "$ws"/*/; do
  name="$(basename "$d")"
  [ "$name" = "architecture-draft" ] && continue
  [ -d "$d/.git" ] && echo "$name"
done)

if [ -z "$active" ]; then
  [ "${#projects[@]}" -gt 0 ] || { echo "Tidak ada project sibling ber-.git."; exit 1; }
  echo "Project terdeteksi:"; i=0
  for p in "${projects[@]}"; do echo "  [$i] $p"; i=$((i+1)); done
  read -r -p "Pilih nomor/nama project aktif: " sel
  if [[ "$sel" =~ ^[0-9]+$ ]]; then active="${projects[$sel]}"; else active="$sel"; fi
fi

claude="$ws/.claude"; mkdir -p "$claude"
for d in commands hooks skills; do
  [ -d "$kit_root/$d" ] && { mkdir -p "$claude/$d"; cp -R "$kit_root/$d/." "$claude/$d/"; }
done

ss_cmd="bash \\\"$claude/hooks/session-start.sh\\\""
pc_cmd="bash \\\"$claude/hooks/pre-commit-reminder.sh\\\""
if [ "$no_precommit" -eq 1 ]; then
  cat > "$claude/settings.json" <<JSON
{ "hooks": { "SessionStart": [ { "hooks": [ { "type": "command", "command": "$ss_cmd" } ] } ] } }
JSON
else
  cat > "$claude/settings.json" <<JSON
{ "hooks": {
  "SessionStart": [ { "hooks": [ { "type": "command", "command": "$ss_cmd" } ] } ],
  "PreToolUse": [ { "matcher": "Bash", "hooks": [ { "type": "command", "command": "$pc_cmd" } ] } ]
} }
JSON
fi

kit_ver="$(tr -d '[:space:]' < "$kit_root/VERSION")"
sed -e "s/__KIT_VERSION__/$kit_ver/g" -e "s/__ACTIVE_PROJECT__/$active/g" \
  "$kit_root/templates/workspace-CLAUDE.md" > "$claude/CLAUDE.md"
printf '%s' "$kit_ver" > "$claude/.kit-version"

echo ""
echo "OK. Agent-kit v$kit_ver terpasang ke $claude"
echo "Project aktif: $active"
echo "Flow: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap"
[ "$no_precommit" -eq 1 ] && echo "(pre-commit reminder: NONAKTIF)" || echo "(pre-commit reminder: aktif)"
```

- [ ] **Step 2: Cek sintaks bash**

Run (Git Bash):
```bash
bash -n "/c/Data utama/Aplikasi/Office/erp/architecture-draft/.agent-kit/init.sh" && echo "syntax OK"
```
Expected: `syntax OK`.

- [ ] **Step 3: Commit**

```powershell
cd "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git add -- ".agent-kit/init.sh"
git commit -m "feat(agent-kit): init.sh (mac/linux) paritas"
```

---

### Task 7: Pemasangan nyata di erp/ + verifikasi end-to-end

**Files:**
- Generate (tidak di-commit): `erp/.claude/*`

**Interfaces:**
- Consumes: seluruh kit. Produces: instalasi nyata di workspace `erp/`.

- [ ] **Step 1: Jalankan init nyata di erp/**

Run:
```powershell
cd "c:\Data utama\Aplikasi\Office\erp"
powershell -NoProfile -ExecutionPolicy Bypass -File "architecture-draft\.agent-kit\init.ps1" -ActiveProject "bip-erp"
```
Expected: ringkasan "Agent-kit v1.0.0 terpasang", project aktif bip-erp.

- [ ] **Step 2: Verifikasi artefak generate**

Run:
```powershell
Get-ChildItem "c:\Data utama\Aplikasi\Office\erp\.claude" -Recurse -Name
Get-Content "c:\Data utama\Aplikasi\Office\erp\.claude\CLAUDE.md" -Raw
Get-Content "c:\Data utama\Aplikasi\Office\erp\.claude\settings.json" -Raw | ConvertFrom-Json
```
Expected: ada `commands/` (6 file), `hooks/`, `settings.json`, `CLAUDE.md` (memuat "bip-erp", tanpa placeholder), `.kit-version` = 1.0.0; settings.json valid (SessionStart + PreToolUse).

- [ ] **Step 3: Verifikasi Obsidian mengabaikan kit**

Konfirmasi manual: buka vault `architecture-draft` di Obsidian → folder `.agent-kit` TIDAK muncul di file explorer Obsidian (dot-folder diabaikan). Dokumentasi vault tidak terpengaruh.

- [ ] **Step 4: Verifikasi slash command terbaca Claude Code**

Konfirmasi manual: buka folder `erp/` di Claude Code, ketik `/` → muncul `start-task, plan, implement, review, sync-docs, wrap`. Session-start hook menampilkan baris flow + status versi kit.

- [ ] **Step 5: Self-check final (tanpa commit — erp/.claude artefak generate)**

Tidak ada commit untuk task ini. Catat hasil verifikasi di ringkasan sesi. Bila semua hijau, kit siap dipakai semua dev.

---

## Self-Review

**Spec coverage:**
- Layout `.agent-kit/` + dot-folder → Task 1, 7(step 3). ✅
- 6 command flow arch-first → Task 2. ✅
- TDD default-adaptif di /implement → Task 2 step 3. ✅
- /sync-docs delegasi ke rulebook vault → Task 2 step 5. ✅
- Hooks SessionStart + pre-commit reminder non-blocking → Task 4. ✅
- init project-level ke erp/.claude → Task 5 (ps1) & 6 (sh). ✅
- Template workspace-CLAUDE.md + placeholder → Task 3, diisi di Task 5. ✅
- Versioning .kit-version + cek update → Task 4 (session-start) & 5. ✅
- Onboarding 3 langkah → Task 1 (README). ✅
- Risiko Obsidian-ignore → diverifikasi Task 7 step 3. ✅

**Catatan deviasi dari spec:** `settings.json` digenerate programatik (bukan string-replace `templates/settings.json`) demi JSON-escape path Windows yang benar; isi & maksud sama dengan spec. File `templates/settings.json` TIDAK dibuat.

**Placeholder scan:** Tidak ada TODO/TBD eksekusi; `__KIT_VERSION__`/`__ACTIVE_PROJECT__` adalah placeholder template yang sengaja diisi init (diverifikasi di test Task 5 step 1).

**Type/nama konsistensi:** Nama param init konsisten (`-ActiveProject`/`--active-project`, `-NoPreCommitHook`/`--no-precommit-hook`); file `.kit-version`, `VERSION`, placeholder dipakai konsisten lintas Task 3/4/5/6.
