#requires -version 5
param(
  [string]$Workspace = (Get-Location).Path,
  [string]$ActiveProject,
  [switch]$NoPreCommitHook,
  [switch]$NoGitHooks
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
try { git -C $vault -c core.fsmonitor=false fetch --quiet 2>$null } catch {}

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

# 4. salin commands/hooks/skills/agents -> erp/.claude
# (team-memory TIDAK disalin: di-import langsung dari vault oleh CLAUDE.md, lihat template)
# (hooks/githooks ikut tersalin sebagai subfolder hooks; dipakai lewat core.hooksPath di §7)
$claude = Join-Path $ws '.claude'
New-Item -ItemType Directory -Force -Path $claude | Out-Null
foreach ($d in 'commands','hooks','skills','agents') {
  $src = Join-Path $kitRoot $d
  $dst = Join-Path $claude $d
  if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }   # prune file lama yg dihapus di kit baru
  if (Test-Path $src) {
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    Copy-Item -Path (Join-Path $src '*') -Destination $dst -Recurse -Force
  }
}

# 5. settings.json (programatik -> JSON-escape path benar)
function HookCmd([string]$name) {
  return ('powershell -NoProfile -ExecutionPolicy Bypass -File "{0}"' -f (Join-Path $claude ('hooks\' + $name)))
}
$hooks = @{
  SessionStart     = @(@{ hooks = @(@{ type='command'; command=(HookCmd 'session-start.ps1') }) })
  UserPromptSubmit = @(@{ hooks = @(@{ type='command'; command=(HookCmd 'sesi-sentuh.ps1') }) })
  SessionEnd       = @(@{ hooks = @(@{ type='command'; command=(HookCmd 'sesi-selesai.ps1') }) })
}
if (-not $NoPreCommitHook) {
  # Matcher WAJIB mencakup PowerShell: di mesin dev Windows seluruh git dijalankan lewat tool
  # PowerShell, dan matcher `Bash` saja membuat gerbang ini tidak pernah menyala (ADR 0077).
  $hooks['PreToolUse'] = @(@{ matcher='Bash|PowerShell'; hooks=@(@{ type='command'; command=(HookCmd 'pre-commit-gate.ps1') }) })
}
# Plugin WAJIB tim, di-enable lewat settings SCOPE PROJECT supaya berlaku bagi siapa pun yang
# clone + trust workspace ini — tak perlu tiap orang ingat menyalakannya sendiri.
# Sengaja hanya yang WAJIB; rekomendasi lain tetap opsional lewat /skills.
$enabledPlugins = @{ 'superpowers@claude-plugins-official' = $true }
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText(
  (Join-Path $claude 'settings.json'),
  (@{ enabledPlugins = $enabledPlugins; hooks = $hooks } | ConvertTo-Json -Depth 8),
  $utf8NoBom)

# 6. generate erp/CLAUDE.md dari template
$kitVer = (Get-Content (Join-Path $kitRoot 'VERSION') -Raw).Trim()
$cm = Get-Content (Join-Path $kitRoot 'templates\workspace-CLAUDE.md') -Raw -Encoding UTF8
$cm = $cm.Replace('__KIT_VERSION__', $kitVer).Replace('__ACTIVE_PROJECT__', $active)
[System.IO.File]::WriteAllText((Join-Path $claude 'CLAUDE.md'), $cm, $utf8NoBom)

# 7. git hooks lokal (pre-push) lewat core.hooksPath ABSOLUT per repo kode.
# .git/hooks tidak ikut ter-clone, jadi tanpa langkah ini gerbangnya cuma hidup di mesin
# yang kebetulan memasangnya. Path absolut karena worktree tertaut punya root berbeda.
# Repo yang sudah punya hooksPath lain (mis. husky) DILEWATI, bukan ditimpa.
$githooks = Join-Path $claude 'hooks\githooks'
$hookDipasang = @(); $hookDilewati = @()
if (-not $NoGitHooks) {
  foreach ($p in $projects) {
    $dir = Join-Path $ws $p
    $existing = ''
    try { $existing = (git -C $dir -c core.fsmonitor=false config --get core.hooksPath 2>$null) } catch {}
    if ($existing -and ($existing -ne $githooks)) { $hookDilewati += ("{0} (sudah ada: {1})" -f $p, $existing); continue }
    try { git -C $dir -c core.fsmonitor=false config core.hooksPath $githooks 2>$null; $hookDipasang += $p } catch { $hookDilewati += ("{0} (gagal)" -f $p) }
  }
}

# 8. folder papan sesi, brief, dan log judge di akar workspace
foreach ($d in 'sesi','briefs','judge') {
  New-Item -ItemType Directory -Force -Path (Join-Path $ws ('.task-plans\' + $d)) | Out-Null
}

# 9. .kit-version
[System.IO.File]::WriteAllText((Join-Path $claude '.kit-version'), $kitVer, $utf8NoBom)

# 10. ringkasan
Write-Host ""
Write-Host "OK. Agent-kit v$kitVer terpasang ke $claude"
Write-Host "Project aktif: $active"
Write-Host "Flow: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap"
Write-Host "Loop: /brief -> /kerjakan (judge otomatis) -> PR | /papan-sesi | /supervise | /ekstrak-skill"
if ($NoPreCommitHook) { Write-Host "(gerbang pre-commit: NONAKTIF)" } else { Write-Host "(gerbang pre-commit: aktif, matcher Bash|PowerShell)" }
if ($hookDipasang.Count -gt 0) { Write-Host ("(pre-push terpasang: {0})" -f ($hookDipasang -join ', ')) }
if ($hookDilewati.Count -gt 0) { Write-Host ("(pre-push DILEWATI: {0})" -f ($hookDilewati -join ', ')) }
Write-Host "Restart sesi Claude Code supaya hook baru terbaca."
