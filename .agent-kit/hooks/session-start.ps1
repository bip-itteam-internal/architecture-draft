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
