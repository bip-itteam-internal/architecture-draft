# antre-lib.ps1 - antrean kerja berat lintas sesi Claude di SATU mesin (kit 1.30.0). Satu-satunya
# tempat untuk dua fakta: perintah mana yang dihitung "run penuh", dan cara mengantre.
#
# Kenapa ada: 2026-09-25 CPU 83-88% dan RAM 26/32 GB karena tsc + next build + vitest dari beberapa
# sesi berjalan bersamaan; gerbang be-jadwal-marketing-offline makan 2 jam. Prosa "dua eksekutor
# wajar" di commands/kerjakan.md tidak menegakkan apa pun (ADR 0077: yang bukan exit code atau
# penolakan hook bukan gerbang).
#
# Kunci = named MUTEX per slot ("Local\<nama>-slot-<i>"), BUKAN Semaphore: hitungan Semaphore BOCOR
# saat pemegangnya mati, sedangkan Mutex yang pemiliknya mati menjadi *abandoned* dan langsung bisa
# diambil penunggu berikutnya. `Local\` karena semua sesi Claude hidup di satu logon; `Global\`
# menuntut hak yang belum tentu ada.
#
# Bersarang: pemegang memasang env AGENTKIT_ANTRE_PEGANG=<PID>, dan proses anaknya (pnpm yang
# memanggil skrip yang memanggil antre lagi, atau gerbang yang dijalankan lewat antre.ps1) melihatnya
# lalu TIDAK mengambil kunci lagi. Tanpa ini satu slot berarti deadlock.
#
# Mac/linux: TIDAK diimplementasikan (keputusan 2026-09-25); antre.sh cuma exec, init.sh tidak
# memasang hook. Env untuk test/penyetelan: AGENTKIT_ANTRE_SLOT (default 1), AGENTKIT_ANTRE_NAMA,
# AGENTKIT_ANTRE_DIR, AGENTKIT_ANTRE_INTERVAL (detik antar cetak status, default 60).
$script:AntreLibDir = $PSScriptRoot

# ---------- klasifikasi: 'penuh' | 'tertarget' | 'bukan' ----------
# Hanya run PENUH yang mengantre (keputusan 2026-09-25): test satu berkas saat TDD yang harus
# menunggu suite 40 menit mematikan siklusnya. Meleset ke 'bukan' hanya mengembalikan keadaan
# sebelum kit ini (tanpa antre), jadi ragu = tidak dihitung penuh, KECUALI build/tsc yang
# memang selalu seluruh proyek.
$script:AntreFlagBernilai = @{
  pm      = @('-C', '--dir', '--filter', '-F', '--prefix', '--workspace')
  vitest  = @('--reporter', '--outputFile', '--config', '-c', '--project', '--maxWorkers', '--minWorkers', '--pool', '-t', '--testNamePattern', '--root', '-r', '--dir', '--environment', '--shard', '--mode')
  go      = @('-run', '-timeout', '-tags', '-o', '-p', '-count', '-skip', '-bench', '-coverprofile')
  flutter = @('--name', '--plain-name', '-j', '--concurrency', '--reporter', '-r', '--tags', '-t', '--exclude-tags', '-x')
}

function Get-AntreNamaAlat([string]$tok) {
  $n = ($tok -split '[\\/]')[-1].ToLowerInvariant()
  return ($n -replace '\.(exe|cmd|ps1|bat)$', '')
}

function Get-AntrePosisional([string[]]$t, [string[]]$bernilai, [string[]]$abaikan) {
  # token posisional (bukan flag, bukan nilai flag, bukan kata kunci yang diabaikan)
  $hasil = @()
  for ($i = 0; $i -lt $t.Count; $i++) {
    $x = $t[$i]
    if ($x -eq '--') { continue }
    if ($x -like '-*') {
      if ($x -notmatch '=' -and $bernilai -ccontains $x) { $i++ }
      continue
    }
    if ($abaikan -contains $x.ToLowerInvariant()) { continue }
    $hasil += $x
  }
  return , $hasil
}

function Get-KelasAlat([string[]]$t) {
  if ($t.Count -eq 0) { return 'bukan' }
  $w = Get-AntreNamaAlat $t[0]
  $r = @(if ($t.Count -gt 1) { $t[1..($t.Count - 1)] })
  switch ($w) {
    'vitest' {
      $pos = Get-AntrePosisional $r $script:AntreFlagBernilai.vitest @('run', 'watch')
      if ($pos.Count -gt 0) { return 'tertarget' } else { return 'penuh' }
    }
    { $_ -in @('tsc', 'vue-tsc') } { return 'penuh' }
    'next' { if ($r.Count -gt 0 -and $r[0] -eq 'build') { return 'penuh' } else { return 'bukan' } }
    'eslint' {
      $pos = Get-AntrePosisional $r @('-c', '--config', '--ext', '-f', '--format', '-o', '--output-file') @()
      if (@($pos | Where-Object { $_ -match '\.[cm]?[jt]sx?$' }).Count -gt 0) { return 'tertarget' } else { return 'penuh' }
    }
    'go' {
      $pos = Get-AntrePosisional $r $script:AntreFlagBernilai.go @()
      if ($pos.Count -eq 0 -or $pos[0] -notin @('build', 'test')) { return 'bukan' }
      $pkg = @($pos | Select-Object -Skip 1)
      if (@($pkg | Where-Object { $_ -match '\.\.\.$' }).Count -gt 0) { return 'penuh' } else { return 'tertarget' }
    }
    'flutter' {
      $pos = Get-AntrePosisional $r $script:AntreFlagBernilai.flutter @()
      if ($pos.Count -eq 0) { return 'bukan' }
      if ($pos[0] -eq 'build') { return 'penuh' }
      if ($pos[0] -ne 'test') { return 'bukan' }
      if ($pos.Count -gt 1) { return 'tertarget' } else { return 'penuh' }
    }
    default { return 'bukan' }
  }
}

function Get-KelasPm([string[]]$r) {
  # pnpm/npm/yarn/bun: cari subperintah sesudah flag global
  $i = 0
  while ($i -lt $r.Count -and $r[$i] -like '-*') { if ($r[$i] -notmatch '=' -and $script:AntreFlagBernilai.pm -ccontains $r[$i]) { $i += 2 } else { $i++ } }
  if ($i -ge $r.Count) { return 'bukan' }
  $sub = $r[$i].ToLowerInvariant(); $i++
  if ($sub -in @('run', 'run-script')) {
    while ($i -lt $r.Count -and $r[$i] -like '-*') { $i++ }
    if ($i -ge $r.Count) { return 'bukan' }
    $sub = $r[$i].ToLowerInvariant(); $i++
  }
  $sisa = @(if ($i -lt $r.Count) { $r[$i..($r.Count - 1)] })
  if ($sub -in @('exec', 'dlx', 'x')) {
    $j = 0; while ($j -lt $sisa.Count -and $sisa[$j] -like '-*') { $j++ }
    if ($j -ge $sisa.Count) { return 'bukan' }
    return (Get-KelasAlat @($sisa[$j..($sisa.Count - 1)]))
  }
  if ($sub -in @('build', 'tsc', 'typecheck', 'type-check')) { return 'penuh' }
  if ($sub -in @('test', 'lint')) {
    $pos = Get-AntrePosisional $sisa @() @()
    if ($pos.Count -gt 0) { return 'tertarget' } else { return 'penuh' }
  }
  if ($sub -in @('vitest', 'eslint', 'tsc', 'next')) { return (Get-KelasAlat (@($sub) + $sisa)) }
  return 'bukan'
}

function Get-KelasSegmen([string[]]$t) {
  $i = 0
  while ($i -lt $t.Count -and $t[$i] -in @('&', '.')) { $i++ }
  if ($i -ge $t.Count) { return 'bukan' }
  $w = Get-AntreNamaAlat $t[$i]
  $r = @(if ($i + 1 -lt $t.Count) { $t[($i + 1)..($t.Count - 1)] })
  if ($w -in @('pnpm', 'npm', 'yarn', 'bun')) { return (Get-KelasPm $r) }
  if ($w -in @('npx', 'pnpx', 'bunx')) {
    $j = 0; while ($j -lt $r.Count -and $r[$j] -like '-*') { $j++ }
    if ($j -ge $r.Count) { return 'bukan' }
    return (Get-KelasAlat @($r[$j..($r.Count - 1)]))
  }
  return (Get-KelasAlat @($t[$i..($t.Count - 1)]))
}

function Get-KelasPerintah([string]$cmd) {
  if ([string]::IsNullOrWhiteSpace($cmd)) { return 'bukan' }
  # teks berkutip dibuang lebih dulu: "pnpm test" di pesan commit atau pola grep BUKAN perintah.
  # Diganti satu token 'Q' tanpa spasi, supaya `--outputFile="..."` tetap satu token flag dan
  # `vitest run "src/x"` tetap punya argumen path.
  $s = [regex]::Replace($cmd, "(?s)@'.*?'@|@`".*?`"@", 'Q')
  $s = [regex]::Replace($s, '"[^"]*"|''[^'']*''', 'Q')
  $hasil = 'bukan'
  foreach ($seg in ($s -split '&&|\|\||[;|\r\n]')) {
    $raw = @($seg.Trim() -split '\s+' | Where-Object { $_ })
    $t = @()
    for ($i = 0; $i -lt $raw.Count; $i++) {
      $x = $raw[$i]
      if ($x -match '^[\d*]?>>?$') { $i++; continue }       # `> out.txt`: buang operator + targetnya
      if ($x -match '^[\d*]?>>?') { continue }              # `2>&1`, `>out.txt`
      $t += $x
    }
    if ($t.Count -eq 0) { continue }
    $k = Get-KelasSegmen $t
    if ($k -eq 'penuh') { return 'penuh' }
    if ($k -eq 'tertarget') { $hasil = 'tertarget' }
  }
  return $hasil
}

# ---------- antrean ----------
function Get-AntreDir {
  if ($env:AGENTKIT_ANTRE_DIR) { return $env:AGENTKIT_ANTRE_DIR }
  # terpasang di <ws>\.claude\hooks -> <ws>\.task-plans\antre (dibaca papan-sesi)
  $claude = Split-Path -Parent $script:AntreLibDir
  if ((Split-Path -Leaf $claude) -eq '.claude') { return (Join-Path (Split-Path -Parent $claude) '.task-plans\antre') }
  return (Join-Path $env:TEMP 'agentkit-antre')
}
function Get-AntreSlot {
  $n = 1
  if ($env:AGENTKIT_ANTRE_SLOT -match '^\d+$' -and [int]$env:AGENTKIT_ANTRE_SLOT -ge 1) { $n = [int]$env:AGENTKIT_ANTRE_SLOT }
  return [math]::Min($n, 32)
}
function Test-AntrePidHidup($id) { try { return [bool](Get-Process -Id ([int]$id) -ErrorAction Stop) } catch { return $false } }

function Get-AntreStatus {
  # berkas status yang pemiliknya sudah mati dibuang (best-effort), tak pernah dilaporkan
  $dir = Get-AntreDir
  if (-not (Test-Path $dir)) { return }
  foreach ($f in @(Get-ChildItem -Path $dir -Filter '*.json' -ErrorAction SilentlyContinue)) {
    $o = $null
    try { $o = Get-Content $f.FullName -Raw -Encoding UTF8 | ConvertFrom-Json } catch {}
    if (-not $o -or -not (Test-AntrePidHidup $o.pid)) { Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue; continue }
    $o
  }
}

function Write-AntreStatus([string]$berkas, $obj) {
  try {
    $dir = Split-Path -Parent $berkas
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    [IO.File]::WriteAllText($berkas, ($obj | ConvertTo-Json -Compress), (New-Object Text.UTF8Encoding($false)))
  } catch {}
}

function Enter-Antre([string]$label, [string]$cwd = (Get-Location).Path) {
  $p = $env:AGENTKIT_ANTRE_PEGANG
  if ($p -match '^\d+$' -and (Test-AntrePidHidup $p)) { return [pscustomobject]@{ bersarang = $true } }
  $nama = if ($env:AGENTKIT_ANTRE_NAMA) { $env:AGENTKIT_ANTRE_NAMA } else { 'agentkit-antre' }
  $n = Get-AntreSlot
  $interval = 60
  if ($env:AGENTKIT_ANTRE_INTERVAL -match '^\d+$' -and [int]$env:AGENTKIT_ANTRE_INTERVAL -ge 1) { $interval = [int]$env:AGENTKIT_ANTRE_INTERVAL }
  $mutex = @(0..($n - 1) | ForEach-Object { New-Object Threading.Mutex($false, ('Local\{0}-slot-{1}' -f $nama, $_)) })
  $berkas = Join-Path (Get-AntreDir) ([string]$PID + '.json')
  $mulai = (Get-Date).ToUniversalTime()
  $st = [ordered]@{ pid = $PID; keadaan = 'menunggu'; perintah = $label; cwd = $cwd; mulai = $mulai.ToString('o'); pegang_sejak = $null; slot = $null }
  Write-AntreStatus $berkas $st
  $idx = -1
  while ($idx -lt 0) {
    try {
      $r = [Threading.WaitHandle]::WaitAny([Threading.WaitHandle[]]$mutex, $interval * 1000)
      if ($r -ne [Threading.WaitHandle]::WaitTimeout) { $idx = $r }
    } catch {
      # pemegang mati tanpa melepas: kepemilikan TETAP berpindah ke kita. PowerShell membungkus
      # galat .NET dalam MethodInvocationException, jadi dicari di rantai InnerException.
      $e = $_.Exception
      while ($e -and -not ($e -is [Threading.AbandonedMutexException])) { $e = $e.InnerException }
      if (-not $e) { throw }
      $idx = $e.MutexIndex
      [Console]::Error.WriteLine('[antre] pemegang sebelumnya mati tanpa melepas slot; slot diambil alih')
    }
    if ($idx -lt 0) {
      $pg = @(Get-AntreStatus | Where-Object { $_.keadaan -eq 'pegang' -and $_.pid -ne $PID })
      $siapa = if ($pg.Count -gt 0) { ($pg | ForEach-Object { 'PID {0} "{1}" di {2}' -f $_.pid, $_.perintah, $_.cwd }) -join '; ' } else { 'pemegang tak tercatat' }
      [Console]::Error.WriteLine(('[antre] menunggu slot kerja berat ({0} slot) sudah {1:N0} dtk; dipegang: {2}' -f $n, ((Get-Date).ToUniversalTime() - $mulai).TotalSeconds, $siapa))
    }
  }
  for ($i = 0; $i -lt $mutex.Count; $i++) { if ($i -ne $idx) { $mutex[$i].Dispose() } }
  $env:AGENTKIT_ANTRE_PEGANG = [string]$PID
  $tunggu = ((Get-Date).ToUniversalTime() - $mulai).TotalSeconds
  $st.keadaan = 'pegang'; $st.pegang_sejak = (Get-Date).ToUniversalTime().ToString('o'); $st.slot = $idx
  Write-AntreStatus $berkas $st
  if ($tunggu -ge 1) { [Console]::Error.WriteLine(('[antre] dapat slot {0} sesudah menunggu {1:N0} dtk' -f $idx, $tunggu)) }
  return [pscustomobject]@{ bersarang = $false; mutex = $mutex[$idx]; berkas = $berkas; slot = $idx; tunggu_detik = $tunggu }
}

function Exit-Antre($h) {
  if (-not $h -or $h.bersarang) { return }
  try { $h.mutex.ReleaseMutex() } catch {}
  try { $h.mutex.Dispose() } catch {}
  Remove-Item Env:AGENTKIT_ANTRE_PEGANG -ErrorAction SilentlyContinue
  Remove-Item $h.berkas -Force -ErrorAction SilentlyContinue
}
