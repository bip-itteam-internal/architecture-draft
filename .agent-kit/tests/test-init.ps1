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
  $cm = Get-Content (Join-Path $claude 'CLAUDE.md') -Raw -Encoding UTF8
  Check ($cm -match 'demo-proj') 'CLAUDE.md memuat project aktif'
  Check ($cm -notmatch '__ACTIVE_PROJECT__') 'placeholder project terisi'
  Check ($cm -notmatch '__KIT_VERSION__') 'placeholder versi terisi'
  $arrow = [char]0x2192
  Check ($cm.Contains($arrow)) 'CLAUDE.md panah utuh (UTF-8 tidak korup)'
  $st = Get-Content (Join-Path $claude 'settings.json') -Raw | ConvertFrom-Json
  Check ($null -ne $st.hooks.SessionStart) 'settings punya SessionStart'
  Check ($null -eq $st.hooks.PreToolUse) 'NoPreCommitHook menghapus PreToolUse'
  $kv = (Get-Content (Join-Path $claude '.kit-version') -Raw).Trim()
  $ver = (Get-Content (Join-Path $kitRoot 'VERSION') -Raw).Trim()
  Check ($kv -eq $ver) '.kit-version sama dgn VERSION'

  # v1.0.1: re-init harus prune file lama yg sudah tak ada di kit, tapi tetap salin yg nyata
  $stale = Join-Path $claude 'commands/__stale-test__.md'
  Set-Content -Path $stale -Value 'stale' -Encoding UTF8
  & (Join-Path $svVault '.agent-kit/init.ps1') -Workspace $tmp -ActiveProject 'demo-proj' -NoPreCommitHook | Out-Null
  Check (-not (Test-Path $stale)) 're-init prune file command lama'
  Check (Test-Path (Join-Path $claude 'commands/start-task.md')) 're-init tetap salin command nyata'
}
finally {
  if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
}
if ($fail -gt 0) { Write-Host "$fail gagal"; exit 1 } else { Write-Host 'Semua lulus'; exit 0 }
