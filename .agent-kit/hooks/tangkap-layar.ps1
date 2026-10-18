# tangkap-layar.ps1 - nyalakan build worktree erp-frontend, tangkap layar manifest, matikan lagi.
#
#   tangkap-layar.ps1 -Path <wt> -Manifest <json> -Keluaran <dir> [-Chrome <exe>]
#                     [-BatasServerDetik 60] [-BatasRuteDetik 90]
#
# Build-nya milik gerbang deterministik /judge (langkah 1); skrip ini TIDAK membangun. Ia memakai
# `pnpm start -p <port>`, bukan `pnpm dev`: membunuh `next dev` pernah merusak `.next/dev/types`.
#
# Kontrak keluar: exit 0 SELALU bila <Keluaran>\ringkasan.json tertulis, galatnya di dalam berkas
# (`galat` global atau per rute). Tangkapan gagal tidak boleh memblokir loop, jadi pemanggil
# membaca isinya, bukan exit code. Exit 1 hanya bila tak ada yang bisa ditulis sama sekali.
param(
  [Parameter(Mandatory = $true)][string]$Path,
  [Parameter(Mandatory = $true)][string]$Manifest,
  [Parameter(Mandatory = $true)][string]$Keluaran,
  [string]$Chrome = '',
  [int]$BatasServerDetik = 60,
  [int]$BatasRuteDetik = 90
)
$ErrorActionPreference = 'Continue'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$mjs = Join-Path $PSScriptRoot 'tangkap-layar.mjs'

try { New-Item -ItemType Directory -Force -Path $Keluaran -ErrorAction Stop | Out-Null }
catch { [Console]::Error.WriteLine("tangkap-layar: folder keluaran tak bisa dibuat: $Keluaran"); exit 1 }
$ringkasan = Join-Path $Keluaran 'ringkasan.json'
if (Test-Path -LiteralPath $ringkasan) { Remove-Item -LiteralPath $ringkasan -Force -ErrorAction SilentlyContinue }

function Tulis-Galat([string]$pesan, [string]$url) {
  # ConvertTo-Json PS 5.1 menulis larik kosong sebagai `{}` bila lewat pipeline; dirakit tangan.
  $isi = '{"url_dasar":' + (ConvertTo-Json $url -Compress) + ',"rute":[],"galat":' + (ConvertTo-Json $pesan -Compress) + '}'
  try { [IO.File]::WriteAllText($ringkasan, $isi, $utf8) } catch { [Console]::Error.WriteLine("tangkap-layar: ringkasan tak tertulis: $_"); exit 1 }
  [Console]::Error.WriteLine("tangkap-layar: $pesan")
}

function Ekor([string]$p) {
  if (Test-Path -LiteralPath $p) { return ((Get-Content -LiteralPath $p -Tail 5 -ErrorAction SilentlyContinue) -join ' | ') }
  return ''
}

# Pemilik port Listen, atau @() bila tak ada.
function Pemilik-Port([int]$port) {
  @(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | ForEach-Object { [int]$_.OwningProcess } | Where-Object { $_ -gt 0 } | Select-Object -Unique)
}

# Apakah $pid keturunan $akar? Port yang listen tapi milik proses lain = server sesi lain, dan
# menangkapnya berarti menilai layar orang lain.
function Keturunan([int]$procId, [int]$akar) {
  $semua = @{}
  Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | ForEach-Object { $semua[[int]$_.ProcessId] = [int]$_.ParentProcessId }
  $p = $procId
  for ($i = 0; $i -lt 15 -and $p -gt 0; $i++) {
    if ($p -eq $akar) { return $true }
    if (-not $semua.ContainsKey($p)) { return $false }
    $p = $semua[$p]
  }
  return $false
}

function Pilih-Port {
  for ($i = 0; $i -lt 20; $i++) {
    $l = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, 0)
    $l.Start(); $p = ([System.Net.IPEndPoint]$l.LocalEndpoint).Port; $l.Stop()
    # 3000 lazim dipakai `pnpm dev` sesi lain; TcpListener di loopback juga tak melihat yang
    # listen di alamat lain, jadi diperiksa ulang lewat tabel TCP.
    if ($p -ne 3000 -and (Pemilik-Port $p).Count -eq 0) { return $p }
  }
  return 0
}

if (-not (Test-Path -LiteralPath (Join-Path $Path '.next\BUILD_ID'))) { Tulis-Galat "build tidak ada: $(Join-Path $Path '.next\BUILD_ID') (jalankan gerbang build dulu)" ''; exit 0 }
if (-not (Test-Path -LiteralPath $Manifest)) { Tulis-Galat "manifest tidak ada: $Manifest" ''; exit 0 }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Tulis-Galat 'node tidak ada di PATH' ''; exit 0 }
if (-not (Test-Path -LiteralPath $mjs)) { Tulis-Galat "tangkap-layar.mjs tidak ada: $mjs" ''; exit 0 }

$port = Pilih-Port
if ($port -eq 0) { Tulis-Galat 'tak menemukan port bebas' ''; exit 0 }
$url = "http://localhost:$port"
$logOut = Join-Path $Keluaran 'server.log'
$logErr = Join-Path $Keluaran 'server.err.log'

# Panggilan server-side Next (SSR, route handler) tak lewat Chrome sehingga tak tercegat stub. Proxy
# mati membuatnya gagal cepat alih-alih mengenai backend sungguhan (.env worktree bisa menunjuk PROD).
$envLama = @{}
$envUji = @{ NODE_USE_ENV_PROXY = '1'; HTTP_PROXY = 'http://127.0.0.1:9'; HTTPS_PROXY = 'http://127.0.0.1:9'; NO_PROXY = 'localhost,127.0.0.1,::1' }
foreach ($k in $envUji.Keys) { $envLama[$k] = [Environment]::GetEnvironmentVariable($k, 'Process'); [Environment]::SetEnvironmentVariable($k, $envUji[$k], 'Process') }

$server = $null
try {
  try {
    $server = Start-Process -FilePath $env:ComSpec -ArgumentList "/d /c pnpm start -p $port" -WorkingDirectory $Path `
      -RedirectStandardOutput $logOut -RedirectStandardError $logErr -WindowStyle Hidden -PassThru -ErrorAction Stop
  } catch { Tulis-Galat "pnpm start gagal dijalankan: $_" $url; exit 0 }

  $batas = (Get-Date).AddSeconds($BatasServerDetik)
  $siap = $false; $pesan = ''
  while ((Get-Date) -lt $batas) {
    $milik = Pemilik-Port $port
    if ($milik.Count -gt 0) {
      if (@($milik | Where-Object { Keturunan $_ $server.Id }).Count -gt 0) { $siap = $true; break }
      $pesan = "port $port dipakai proses lain (pid $($milik -join ','))"; break
    }
    if ($server.HasExited) { $pesan = "server berhenti sebelum listen (exit $($server.ExitCode)): $(Ekor $logErr) $(Ekor $logOut)"; break }
    Start-Sleep -Milliseconds 500
  }
  if (-not $siap) {
    if (-not $pesan) { $pesan = "server tidak listen di port $port dalam $BatasServerDetik dtk: $(Ekor $logErr) $(Ekor $logOut)" }
    Tulis-Galat $pesan $url
    exit 0
  }

  $argNode = @($mjs, '--url-dasar', $url, '--manifest', $Manifest, '--keluaran', $Keluaran, '--batas-rute-detik', "$BatasRuteDetik")
  if ($Chrome) { $argNode += @('--chrome', $Chrome) }
  & node @argNode
  $rcNode = $LASTEXITCODE
  if (-not (Test-Path -LiteralPath $ringkasan)) { Tulis-Galat "tangkap-layar.mjs berhenti tanpa ringkasan (exit $rcNode)" $url }
  elseif ($rcNode -ne 0) {
    # Node mati di tengah jalan: ringkasan sebagian tak boleh terbaca sebagai tangkapan utuh.
    try {
      $obj = [IO.File]::ReadAllText($ringkasan, $utf8).TrimStart([char]0xFEFF) | ConvertFrom-Json
      $pesanCrash = "tangkap-layar.mjs berhenti (exit $rcNode), ringkasan sebagian"
      if ($obj.PSObject.Properties.Name -contains 'galat') { $obj.galat = $pesanCrash } else { $obj | Add-Member -NotePropertyName galat -NotePropertyValue $pesanCrash }
      # Larik kosong lewat pipeline menjadi `{}` di PS 5.1: -InputObject + depth cukup menjaga rute.
      $tmpR = $ringkasan + '.tmp'
      [IO.File]::WriteAllText($tmpR, (ConvertTo-Json -InputObject $obj -Depth 30), $utf8)
      Move-Item -LiteralPath $tmpR -Destination $ringkasan -Force
      [Console]::Error.WriteLine("tangkap-layar: $pesanCrash")
    } catch { [Console]::Error.WriteLine("tangkap-layar: galat crash tak tertulis: $_") }
  }
}
finally {
  # Hentikan HANYA pohon proses milik run ini: cmd -> pnpm -> next, lalu pemilik port bila ada
  # yang tercerai dari induknya. Proses node/chrome lain di mesin ini tak disentuh.
  # Pemilik port dicatat SEBELUM induknya dibunuh: sesudahnya rantai ParentProcessId putus dan
  # keturunan tak lagi bisa dibuktikan.
  $milikKita = @()
  if ($server) { $milikKita = @(Pemilik-Port $port | Where-Object { Keturunan $_ $server.Id }) }
  if ($server -and -not $server.HasExited) { & taskkill.exe /T /F /PID $server.Id 2>&1 | Out-Null }
  foreach ($p in $milikKita) { & taskkill.exe /T /F /PID $p 2>&1 | Out-Null }
  for ($i = 0; $i -lt 10 -and $port -gt 0 -and (Pemilik-Port $port).Count -gt 0; $i++) { Start-Sleep -Milliseconds 500 }
  foreach ($k in $envUji.Keys) { [Environment]::SetEnvironmentVariable($k, $envLama[$k], 'Process') }
}
if (Test-Path -LiteralPath $ringkasan) { exit 0 } else { exit 1 }
