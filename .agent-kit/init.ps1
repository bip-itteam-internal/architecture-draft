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

# 4. salin commands/hooks/skills -> erp/.claude
# (team-memory TIDAK disalin: di-import langsung dari vault oleh CLAUDE.md, lihat template)
$claude = Join-Path $ws '.claude'
New-Item -ItemType Directory -Force -Path $claude | Out-Null
foreach ($d in 'commands','hooks','skills') {
  $src = Join-Path $kitRoot $d
  $dst = Join-Path $claude $d
  if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }   # prune file lama yg dihapus di kit baru
  if (Test-Path $src) {
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    Copy-Item -Path (Join-Path $src '*') -Destination $dst -Recurse -Force
  }
}

# 5. settings.json (programatik -> JSON-escape path benar)
$ssCmd = 'powershell -NoProfile -ExecutionPolicy Bypass -File "{0}"' -f (Join-Path $claude 'hooks\session-start.ps1')
$pcCmd = 'powershell -NoProfile -ExecutionPolicy Bypass -File "{0}"' -f (Join-Path $claude 'hooks\pre-commit-reminder.ps1')
$hooks = @{ SessionStart = @(@{ hooks = @(@{ type='command'; command=$ssCmd }) }) }
if (-not $NoPreCommitHook) {
  $hooks['PreToolUse'] = @(@{ matcher='Bash'; hooks=@(@{ type='command'; command=$pcCmd }) })
}
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Join-Path $claude 'settings.json'), (@{ hooks = $hooks } | ConvertTo-Json -Depth 8), $utf8NoBom)

# 6. generate erp/CLAUDE.md dari template
$kitVer = (Get-Content (Join-Path $kitRoot 'VERSION') -Raw).Trim()
$cm = Get-Content (Join-Path $kitRoot 'templates\workspace-CLAUDE.md') -Raw -Encoding UTF8
$cm = $cm.Replace('__KIT_VERSION__', $kitVer).Replace('__ACTIVE_PROJECT__', $active)
[System.IO.File]::WriteAllText((Join-Path $claude 'CLAUDE.md'), $cm, $utf8NoBom)

# 7. .kit-version
[System.IO.File]::WriteAllText((Join-Path $claude '.kit-version'), $kitVer, $utf8NoBom)

# 8. ringkasan
Write-Host ""
Write-Host "OK. Agent-kit v$kitVer terpasang ke $claude"
Write-Host "Project aktif: $active"
Write-Host "Flow: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap"
if ($NoPreCommitHook) { Write-Host "(pre-commit reminder: NONAKTIF)" } else { Write-Host "(pre-commit reminder: aktif)" }
