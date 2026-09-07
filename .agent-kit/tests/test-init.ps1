# test-init.ps1 — integrasi: jalankan init di sandbox, assert artefak generate + hook nyata
$ErrorActionPreference = 'Stop'
$kitRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)  # .agent-kit
$tmp = Join-Path $env:TEMP ("agentkit-test-" + [guid]::NewGuid().ToString('N').Substring(0,8))
$fail = 0
function Check($cond, $name) { if ($cond) { Write-Host "PASS $name" } else { Write-Host "FAIL $name"; $script:fail++ } }

# Jalankan skrip hook dengan stdin JSON persis seperti Claude Code, kembalikan exit code.
# stderr ditangkap ke berkas supaya pesan penolakan bisa diperiksa isinya.
function Read-Json([string]$path) {
  if (-not (Test-Path $path)) { return $null }
  try { return (Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json) } catch { return $null }
}
# Start-Process, bukan pipeline/`&`: PS 5.1 membungkus stderr anak jadi ErrorRecord dan dengan
# $ErrorActionPreference='Stop' pesan PENOLAKAN yang benar justru menghentikan test.
function Invoke-Ps([string]$script, [string[]]$argsSkrip, [string]$stdinFile, [string]$errFile) {
  # parameter TIDAK boleh bernama $args: itu variabel otomatis PowerShell, dan menamai parameter
  # begitu membuat daftar argumen kosong tanpa galat (skrip lalu gagal di parameter wajib, exit 1)
  $outFile = [IO.Path]::GetTempFileName()
  if (-not $errFile) { $errFile = [IO.Path]::GetTempFileName() }
  $argList = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $script + '"')) + @($argsSkrip | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } })
  $sp = @{ FilePath = 'powershell'; ArgumentList = $argList; RedirectStandardOutput = $outFile; RedirectStandardError = $errFile; Wait = $true; PassThru = $true; NoNewWindow = $true }
  if ($stdinFile) { $sp['RedirectStandardInput'] = $stdinFile }
  $p = Start-Process @sp
  Remove-Item $outFile -Force -ErrorAction SilentlyContinue
  return $p.ExitCode
}
function Invoke-Hook([string]$script, [hashtable]$stdin, [string]$errFile) {
  $inFile = [IO.Path]::GetTempFileName()
  [IO.File]::WriteAllText($inFile, ($stdin | ConvertTo-Json -Compress -Depth 6))
  $rc = Invoke-Ps $script @() $inFile $errFile
  Remove-Item $inFile -Force -ErrorAction SilentlyContinue
  return $rc
}

try {
  # sandbox: vault tiruan berisi kit nyata (copy) + project tiruan
  $svVault = Join-Path $tmp 'architecture-draft'
  New-Item -ItemType Directory -Force -Path $svVault | Out-Null
  Copy-Item -Path $kitRoot -Destination (Join-Path $svVault '.agent-kit') -Recurse -Force
  Set-Content -Path (Join-Path $svVault 'CLAUDE.md') -Value '# stub vault rulebook' -Encoding UTF8
  git -C $svVault init -q
  $proj = Join-Path $tmp 'demo-proj'; New-Item -ItemType Directory -Force -Path $proj | Out-Null
  git -C $proj init -q
  git -C $proj config user.email 'test@example.invalid'
  git -C $proj config user.name 'test'
  git -C $proj checkout -q -b main
  git -C $proj commit -q --allow-empty -m init

  & (Join-Path $svVault '.agent-kit/init.ps1') -Workspace $tmp -ActiveProject 'demo-proj' -NoPreCommitHook | Out-Null

  $claude = Join-Path $tmp '.claude'
  Check (Test-Path (Join-Path $claude 'commands/start-task.md')) 'commands tersalin'
  Check (Test-Path (Join-Path $claude 'commands/analisa-kebutuhan.md')) 'command /analisa-kebutuhan tersalin'
  # Jumlah command diturunkan dari kit, JANGAN dipatok angka: assertion angka-mati
  # sudah pernah rot diam-diam saat index-vault.md dan skills.md ditambahkan (2026-08-28).
  $srcCmd = (Get-ChildItem (Join-Path $kitRoot 'commands') -Filter *.md).Count
  $cmdCount = (Get-ChildItem (Join-Path $claude 'commands') -Filter *.md).Count
  Check ($cmdCount -eq $srcCmd) "semua command kit tersalin ($cmdCount/$srcCmd berkas)"
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

  # ---- v1.15.0: agents, githooks, hooksPath, folder sesi, hook sesi ----
  $srcAg = (Get-ChildItem (Join-Path $kitRoot 'agents') -Filter *.md -ErrorAction SilentlyContinue).Count
  $agCount = (Get-ChildItem (Join-Path $claude 'agents') -Filter *.md -ErrorAction SilentlyContinue).Count
  Check ($srcAg -gt 0 -and $agCount -eq $srcAg) "semua agen kit tersalin ($agCount/$srcAg berkas)"
  Check (Test-Path (Join-Path $claude 'hooks/githooks/pre-push')) 'githooks/pre-push tersalin'
  $hpExpected = (Join-Path $claude 'hooks\githooks')
  $hp = (git -C $proj config --get core.hooksPath)
  Check ($hp -eq $hpExpected) "core.hooksPath demo-proj = githooks kit"
  Check (Test-Path (Join-Path $tmp '.task-plans/sesi')) '.task-plans/sesi dibuat init'
  Check (Test-Path (Join-Path $tmp '.task-plans/briefs')) '.task-plans/briefs dibuat init'
  Check ($null -ne $st.hooks.UserPromptSubmit) 'settings punya UserPromptSubmit (walau NoPreCommitHook)'
  Check ($null -ne $st.hooks.SessionEnd) 'settings punya SessionEnd (walau NoPreCommitHook)'

  # session-start.ps1 harus mengeluarkan JSON sah di stdout DAN menulis berkas sesi.
  # $PWD diset ke $tmp supaya hook menemukan 'architecture-draft' untuk cek staleness.
  $errf = Join-Path $tmp 'hook.err'
  $hookJson = $null
  try {
    Push-Location $tmp
    try {
      $hookOut = (@{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='SessionStart' } | ConvertTo-Json -Compress) |
        powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $claude 'hooks/session-start.ps1') 2>$null
    } finally { Pop-Location }
    $hookJson = ($hookOut -join '') | ConvertFrom-Json
  } catch {}
  Check ($null -ne $hookJson -and $null -ne $hookJson.hookSpecificOutput.additionalContext) 'session-start.ps1 mengeluarkan JSON sah'
  $sesiFile = Join-Path $tmp '.task-plans/sesi/sesi-uji.json'
  Check (Test-Path $sesiFile) 'session-start.ps1 menulis berkas sesi'
  $sesi = $null; try { $sesi = Read-Json $sesiFile } catch {}
  Check ($null -ne $sesi -and $sesi.status -eq 'aktif' -and $sesi.session_id -eq 'sesi-uji') 'berkas sesi: status aktif + session_id'

  # sesi-sentuh.ps1 (UserPromptSubmit): tahap dari slash command, task dari argumennya
  $rc = Invoke-Hook (Join-Path $claude 'hooks/sesi-sentuh.ps1') @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='UserPromptSubmit'; prompt='/kerjakan .task-plans/briefs/2026-09-06-contoh.md' } $errf
  $sesi = Read-Json $sesiFile
  Check ($rc -eq 0 -and $sesi.tahap -eq 'kerjakan' -and $sesi.task -like '*contoh.md*') "sesi-sentuh: tahap=kerjakan, task terisi (exit $rc)"
  $rc = Invoke-Hook (Join-Path $claude 'hooks/sesi-sentuh.ps1') @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='UserPromptSubmit'; prompt='lanjut saja' } $errf
  $sesi2 = Read-Json $sesiFile
  Check ($rc -eq 0 -and $sesi2.tahap -eq 'kerjakan') 'sesi-sentuh: prompt biasa tidak mengubah tahap'
  # sesi-selesai.ps1 (SessionEnd)
  $rc = Invoke-Hook (Join-Path $claude 'hooks/sesi-selesai.ps1') @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='SessionEnd' } $errf
  $sesi3 = Read-Json $sesiFile
  Check ($rc -eq 0 -and $sesi3.status -eq 'selesai') 'sesi-selesai: status selesai'

  # ---- dashboard.ps1 -TanpaGh: HTML dari template + JSON tertanam memuat sesi uji ----
  $rc = Invoke-Ps (Join-Path $claude 'hooks/dashboard.ps1') @('-Workspace', $tmp, '-TanpaGh') $null $errf
  $dash = Join-Path $tmp '.task-plans/dashboard.html'
  $dashTxt = if (Test-Path $dash) { Get-Content $dash -Raw -Encoding UTF8 } else { '' }
  Check ($rc -eq 0 -and $dashTxt -match 'id="data"' -and $dashTxt -match 'sesi-uji' -and $dashTxt -notmatch '__DASHBOARD_DATA__') "dashboard.ps1 -TanpaGh: HTML + JSON tertanam memuat sesi uji (exit $rc)"
  $dashJson = $null; try { if ($dashTxt -match '(?s)<script id="data" type="application/json">(.*?)</script>') { $dashJson = ($Matches[1] -replace '<\\/', '</') | ConvertFrom-Json } } catch {}
  Check ($null -ne $dashJson -and $dashJson.versi -eq 1 -and $dashJson.gh.ok -eq $false) 'JSON tertanam sah, versi 1, gh ditandai tidak tersedia (bukan nol senyap)'

  # ---- pre-commit-gate: KONTROL POSITIF (harus menolak) dan NEGATIF (harus lolos) ----
  $gate = Join-Path $claude 'hooks/pre-commit-gate.ps1'
  Check (Test-Path $gate) 'pre-commit-gate.ps1 tersalin'
  $cmdMain = 'git -C "' + $proj + '" -c core.fsmonitor=false commit -m "x"'
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=$cmdMain } } $errf
  $errTxt = if (Test-Path $errf) { Get-Content $errf -Raw } else { '' }
  Check ($rc -eq 2) "KONTROL POSITIF: commit di main repo kode DITOLAK (exit $rc)"
  Check ($errTxt -match 'main') 'pesan penolakan menyebut branch-nya'
  git -C $proj checkout -q -b feat/uji
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=$cmdMain } } $errf
  Check ($rc -eq 0) "KONTROL NEGATIF: commit di branch fitur LOLOS (exit $rc)"
  # cwd = repo (tanpa -C), masih di feat/uji -> lolos; lalu kembali ke main -> ditolak
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$proj; hook_event_name='PreToolUse'; tool_name='Bash'; tool_input=@{ command='git commit -m "y"' } } $errf
  Check ($rc -eq 0) "repo dari cwd, branch fitur, matcher Bash: lolos (exit $rc)"
  git -C $proj checkout -q main
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$proj; hook_event_name='PreToolUse'; tool_name='Bash'; tool_input=@{ command='git commit -m "y"' } } $errf
  Check ($rc -eq 2) "repo dari cwd, branch main: ditolak (exit $rc)"
  # vault dikecualikan walau di main
  git -C $svVault checkout -q -b main 2>$null
  $cmdVault = 'git -C "' + $svVault + '" -c core.fsmonitor=false commit -m "dok"'
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=$cmdVault } } $errf
  Check ($rc -eq 0) "vault architecture-draft dikecualikan (exit $rc)"
  # perintah git non-commit di main: lolos
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$proj; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command='git status' } } $errf
  Check ($rc -eq 0) "git status di main: lolos (exit $rc)"
  # 'commit' sebagai kata di pesan, bukan subperintah: lolos
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$proj; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command='git log --grep commit' } } $errf
  Check ($rc -eq 0) "git log --grep commit: lolos (exit $rc)"
  # GAGAL-TERTUTUP: -C dari ekspresi yang tak bisa diurai -> DITOLAK, pesan menyarankan path literal.
  # Kontrol positif langsung 2026-09-06 membuktikan versi gagal-terbuka meloloskan commit di main lewat bentuk ini.
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command='$t = Join-Path $env:TEMP "x"; git -C $t commit -m "z"' } } $errf
  $errTxt = if (Test-Path $errf) { Get-Content $errf -Raw } else { '' }
  Check ($rc -eq 2 -and $errTxt -match 'LITERAL') "path repo dari ekspresi: DITOLAK gagal-tertutup, pesan menyebut path literal (exit $rc)"
  # $env:TEMP di dalam string di-expand -> repo dikenali; proj di main -> ditolak KARENA main (bukan karena tak terurai)
  $relProj = $proj.Substring($env:TEMP.Length)
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=('git -C "$env:TEMP' + $relProj + '" commit -m "e"') } } $errf
  $errTxt = if (Test-Path $errf) { Get-Content $errf -Raw } else { '' }
  Check ($rc -eq 2 -and $errTxt -match "branch 'main'" -and $errTxt -notmatch 'LITERAL') "`$env: di-expand: ditolak karena main, bukan karena tak terurai (exit $rc)"
  # `$v="literal"; git -C $v commit` tetap dikenali; proj di main -> ditolak karena main
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=('$v="' + $proj + '"; git -C $v -c core.fsmonitor=false commit -m "f"') } } $errf
  $errTxt = if (Test-Path $errf) { Get-Content $errf -Raw } else { '' }
  Check ($rc -eq 2 -and $errTxt -match "branch 'main'") "`$v=literal lalu -C `$v: ditolak karena main (exit $rc)"
  # `cd <repo>; git commit` dikenali lewat cd
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=('cd "' + $proj + '"; git commit -m "g"') } } $errf
  $errTxt = if (Test-Path $errf) { Get-Content $errf -Raw } else { '' }
  Check ($rc -eq 2 -and $errTxt -match "branch 'main'") "cd <repo>; git commit: ditolak karena main (exit $rc)"

  # ---- transkrip-ringkas: JSONL sah -> markdown; sampah -> tolak ----
  $tr = Join-Path $claude 'hooks/transkrip-ringkas.ps1'
  $jl = Join-Path $tmp 'sesi.jsonl'
  @(
    '{"type":"user","timestamp":"2026-09-06T01:00:00Z","message":{"role":"user","content":"tolong perbaiki paginasi retur"}}',
    '{"type":"assistant","timestamp":"2026-09-06T01:00:05Z","message":{"role":"assistant","content":[{"type":"text","text":"Saya cek dulu."},{"type":"tool_use","name":"Grep","input":{"pattern":"paginasi"}}]}}',
    '{"type":"queue-operation","operation":"enqueue"}'
  ) | Set-Content -Path $jl -Encoding UTF8
  $md = Join-Path $tmp 'sesi.md'
  $rc = Invoke-Ps $tr @('-Transkrip', $jl, '-Keluaran', $md) $null $errf
  $mdTxt = if (Test-Path $md) { Get-Content $md -Raw -Encoding UTF8 } else { '' }
  Check ($rc -eq 0 -and $mdTxt -match 'paginasi retur' -and $mdTxt -match 'Grep') "transkrip-ringkas: prompt + nama tool terambil (exit $rc)"
  $junk = Join-Path $tmp 'junk.jsonl'
  @('bukan json', '{"type":"tak-dikenal"}', 'x') | Set-Content -Path $junk -Encoding UTF8
  $rc = Invoke-Ps $tr @('-Transkrip', $junk, '-Keluaran', (Join-Path $tmp 'junk.md')) $null $errf
  Check ($rc -ne 0) "transkrip-ringkas: <50% terurai DITOLAK, bukan ringkasan kosong (exit $rc)"

  # ---- init tanpa -NoPreCommitHook: matcher wajib mencakup PowerShell ----
  & (Join-Path $svVault '.agent-kit/init.ps1') -Workspace $tmp -ActiveProject 'demo-proj' | Out-Null
  $st2 = Get-Content (Join-Path $claude 'settings.json') -Raw | ConvertFrom-Json
  $m = $st2.hooks.PreToolUse[0].matcher
  Check ($m -match 'PowerShell' -and $m -match 'Bash') "matcher pre-commit = Bash|PowerShell ($m)"
  Check (($st2.hooks.PreToolUse[0].hooks[0].command) -match 'pre-commit-gate') 'PreToolUse memanggil pre-commit-gate, bukan reminder'

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
