# gerbang-lib.ps1 — dipakai (dot-source) oleh gerbang.ps1 dan baseline-test.ps1.
# SATU tempat untuk: deteksi jenis repo, nama repo, berkas tersentuh, dan PENGURAI hasil test
# (vitest --reporter=json, go test -json). Bentuk nama test yang disimpan di baseline dan yang
# dibandingkan gerbang HARUS keluar dari fungsi yang sama; dua salinan berarti baseline dan
# gerbang bisa menyimpang diam-diam dan gerbang menolak yang benar.

function Get-KitRoot([string]$scriptRoot) {
  # dipanggil dari .agent-kit/hooks (sumber) atau .claude/hooks (salinan init)
  $p = Split-Path -Parent $scriptRoot
  if ((Split-Path $p -Leaf) -eq '.agent-kit') { return $p }
  $ws = Split-Path -Parent $p            # .claude -> ws
  return (Join-Path $ws 'architecture-draft\.agent-kit')
}

function Get-RepoTop([string]$path) { return (git -C $path -c core.fsmonitor=false rev-parse --show-toplevel 2>$null) }

function Get-NamaRepo([string]$path) {
  # worktree tertaut pun terbaca milik repo mana: dari common dir, bukan dari nama folder
  $common = git -C $path -c core.fsmonitor=false rev-parse --path-format=absolute --git-common-dir 2>$null
  if (-not $common) { return $null }
  return (Split-Path (Split-Path $common -Parent) -Leaf)
}

function Get-JenisRepo([string]$top) {
  if ((Test-Path (Join-Path $top 'package.json')) -and (Test-Path (Join-Path $top 'pnpm-lock.yaml'))) { return 'node' }
  $svc = Join-Path $top 'services'
  if (Test-Path $svc) {
    $ada = Get-ChildItem $svc -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'go.mod') }
    if ($ada) { return 'go' }
  }
  return 'lain'
}

function Get-BerkasTersentuh([string]$top, [string]$base) {
  # working tree vs merge-base: mencakup yang belum di-commit (eksekutor tidak commit)
  $a = @()
  $mb = git -C $top -c core.fsmonitor=false merge-base $base HEAD 2>$null
  if ($mb) { $a += @(git -C $top -c core.fsmonitor=false diff --name-only $mb 2>$null) }
  $a += @(git -C $top -c core.fsmonitor=false ls-files --others --exclude-standard 2>$null)
  return @($a | Where-Object { $_ } | Sort-Object -Unique)
}

function Get-SemuaService([string]$top) {
  return @(Get-ChildItem (Join-Path $top 'services') -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'go.mod') } | Select-Object -ExpandProperty Name)
}

function Get-ServicesTersentuh([string]$top, [string[]]$berkas) {
  if (@($berkas | Where-Object { $_ -like 'shared-library/*' }).Count -gt 0) { return (Get-SemuaService $top) }
  $svc = @($berkas | ForEach-Object { if ($_ -match '^services/([^/]+)/') { $Matches[1] } } | Sort-Object -Unique)
  return @($svc | Where-Object { Test-Path (Join-Path $top ("services\" + $_ + "\go.mod")) })
}

function Invoke-Gerbang([string]$nama, [string]$dir, [string]$cmd) {
  # jalankan satu perintah; simpan seluruh keluaran (untuk pengurai) dan ekornya (untuk manusia)
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $out = @(); $rc = 1
  try {
    Push-Location $dir
    try { $out = @(Invoke-Expression ($cmd + ' 2>&1') | ForEach-Object { [string]$_ }); $rc = $LASTEXITCODE }
    finally { Pop-Location }
  } catch { $out += [string]$_; $rc = 1 }
  $sw.Stop()
  if ($null -eq $rc) { $rc = 0 }
  return [pscustomobject]@{
    nama = $nama; lolos = ($rc -eq 0); exit = $rc
    durasi_detik = [math]::Round($sw.Elapsed.TotalSeconds, 1)
    ekor = @($out | Select-Object -Last 25); semua = $out
  }
}

function Invoke-VitestJson([string]$top) {
  # exit code vitest TIDAK dipakai sebagai lolos/gagal: yang menentukan adalah kegagalan BARU
  # terhadap baseline, karena `pnpm test` main tidak pernah hijau penuh di sini.
  $tmp = Join-Path $env:TEMP ('vitest-' + [guid]::NewGuid().ToString('N') + '.json')
  $g = Invoke-Gerbang 'test' $top ('pnpm exec vitest run --reporter=json --outputFile="' + $tmp + '"')
  $gagal = @(); $jumlah = 0; $terurai = $false
  if (Test-Path $tmp) {
    try {
      $j = Get-Content $tmp -Raw -Encoding UTF8 | ConvertFrom-Json
      $terurai = $true
      foreach ($f in @($j.testResults)) {
        $rel = ([string]$f.name)
        if ($rel.StartsWith($top)) { $rel = $rel.Substring($top.Length).TrimStart('\', '/') }
        $rel = $rel -replace '\\', '/'
        foreach ($t in @($f.assertionResults)) {
          $jumlah++
          if ($t.status -eq 'failed') { $gagal += ('{0} > {1}' -f $rel, [string]$t.fullName) }
        }
        # berkas yang gagal dimuat sama sekali (galat import) tidak punya assertionResults
        if ($f.status -eq 'failed' -and @($f.assertionResults).Count -eq 0) { $gagal += ('{0} > (gagal dimuat)' -f $rel) }
      }
    } catch {}
    Remove-Item $tmp -Force -ErrorAction SilentlyContinue
  }
  return [pscustomobject]@{ gerbang = $g; jumlah = $jumlah; gagal = @($gagal | Sort-Object -Unique); terurai = $terurai }
}

function Invoke-GoTestJson([string]$top, [string]$svc) {
  $dir = Join-Path $top ('services\' + $svc)
  $g = Invoke-Gerbang ('test:' + $svc) $dir 'go test ./... -json -count=1'
  $gagal = @(); $jumlah = 0; $terurai = $false
  foreach ($line in $g.semua) {
    if (-not $line.StartsWith('{')) { continue }
    try { $e = $line | ConvertFrom-Json } catch { continue }
    $terurai = $true
    if (-not $e.Test) { continue }
    if ($e.Action -eq 'pass' -or $e.Action -eq 'fail') { $jumlah++ }
    if ($e.Action -eq 'fail') { $gagal += ('services/{0}:{1}.{2}' -f $svc, [string]$e.Package, [string]$e.Test) }
  }
  # paket yang gagal BUILD tidak punya event Test; catat sebagai satu kegagalan bernama
  foreach ($line in $g.semua) {
    if ($line -match '^\{' ) { try { $e = $line | ConvertFrom-Json } catch { continue }; if ($e.Action -eq 'fail' -and -not $e.Test -and $e.Package) { $gagal += ('services/{0}:{1}.(paket gagal)' -f $svc, [string]$e.Package) } }
  }
  return [pscustomobject]@{ gerbang = $g; jumlah = $jumlah; gagal = @($gagal | Sort-Object -Unique); terurai = $terurai }
}

function Read-Baseline([string]$kitRoot, [string]$nama) {
  $p = Join-Path $kitRoot ('baseline\' + $nama + '.json')
  if (-not (Test-Path $p)) { return $null }
  try { return (Get-Content $p -Raw -Encoding UTF8 | ConvertFrom-Json) } catch { return $null }
}

function Write-JsonUtf8([string]$path, $obj) {
  $dir = Split-Path $path -Parent
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  $utf8 = New-Object System.Text.UTF8Encoding($false)
  [IO.File]::WriteAllText($path, ($obj | ConvertTo-Json -Depth 8), $utf8)
}
