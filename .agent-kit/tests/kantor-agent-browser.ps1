# kantor-agent-browser.ps1 — verifikasi MANUAL halaman Kantor Agent di Chrome sungguhan lewat CDP.
#
# Bukan bagian test-init: butuh Chrome dan sekitar satu menit. Jalankan tiap kali
# hooks/kantor-agent.template.html berubah, lalu nilai screenshot-nya dengan mata.
#
# Yang dibuktikan di sini, dan TIDAK bisa dibuktikan jsdom maupun screenshot ber-virtual-time:
# - data.js yang disuntik ulang membaca isi terbaru di file:// tanpa reload;
# - robot benar-benar TIBA di area tujuannya dengan jam nyata (bukan cuma dibuat);
# - pod dan warna Lead stabil saat data berganti;
# - ruang berisi >= 4 robot tanpa gelembung alat (label ringkas);
# - keadaan layar memuat, normal, format berubah, kosong, basi, sepi;
# - nol galat JavaScript selama semua itu.
# Data ditulis tangan di sini supaya tiap keadaan bisa dipaksa; kebenaran data dari transkrip sudah
# diuji test_kantor_agent.py.
#
# pakai: kantor-agent-browser.ps1 [-Keluaran DIR] [-Chrome EXE] [-Port 9340]
param(
  [string]$Keluaran = (Join-Path $env:TEMP ('kantor-agent-browser-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))),
  [string]$Chrome = (Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'),
  [int]$Port = 9340
)
$ErrorActionPreference = 'Continue'
$script:fail = 0
function Check($cond, $name) { if ($cond) { Write-Host "PASS $name" } else { Write-Host "FAIL $name"; $script:fail++ } }
if (-not (Test-Path -LiteralPath $Chrome)) { [Console]::Error.WriteLine("Chrome tidak ada: $Chrome"); exit 2 }

New-Item -ItemType Directory -Force -Path $Keluaran | Out-Null
$halaman = Join-Path $Keluaran 'halaman'
New-Item -ItemType Directory -Force -Path $halaman | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '..\hooks\kantor-agent.template.html') -Destination (Join-Path $halaman 'kantor-agent.html') -Force
$dataJs = Join-Path $halaman 'kantor-agent-data.js'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$inv = [Globalization.CultureInfo]::InvariantCulture

function Tulis-Data($sesi, [bool]$Dikenali = $true, $Berhenti = $null, [int]$UmurDetik = 0, [int]$HidupMenit = 30, [int]$DiamMenit = 10) {
  $data = [ordered]@{
    versi = 1
    dibuat = (Get-Date).ToUniversalTime().AddSeconds(-$UmurDetik).ToString('yyyy-MM-ddTHH:mm:ss.fffZ', $inv)
    ambang = [ordered]@{ hidup_menit = $HidupMenit; diam_menit = $DiamMenit }
    skema = [ordered]@{ baris_diurai = 100; baris_rusak = $(if ($Dikenali) { 0 } else { 80 }); dikenali = $Dikenali; dilewati_luar_workspace = 0 }
    penulis = [ordered]@{ pid = 1; interval_detik = 2; berhenti = $Berhenti; tick_ms = $null }
    sesi = @($sesi)
  }
  $tmp = $dataJs + '.tmp'
  [IO.File]::WriteAllText($tmp, ('window.__KANTOR__ = ' + ($data | ConvertTo-Json -Depth 8 -Compress) + ";`n"), $utf8)
  Move-Item -LiteralPath $tmp -Destination $dataJs -Force
}
function Sesi($id, $judul, $area, $keadaan, $alat = '', $detail = '', $sub = @()) {
  [ordered]@{ id = $id; judul = $judul; tahap = 'implement'; pr = $null; area = $area; keadaan = $keadaan; alat = $alat; detail = $detail
    sejak = $null; durasi_detik = $(if ($alat) { 12 } else { $null }); diam_detik = 5; subagent = @($sub) }
}
function Sub($id, $peran, $area, $keadaan, $alat = '') {
  [ordered]@{ id = $id; jenis = 'Explore'; peran = $peran; deskripsi = 'uji'; area = $area; keadaan = $keadaan; alat = $alat; detail = ''
    sejak = $null; durasi_detik = $null; diam_detik = 3 }
}

$ud = Join-Path $Keluaran 'chrome-profil'
$url = ([Uri](Join-Path $halaman 'kantor-agent.html')).AbsoluteUri
$proses = Start-Process -FilePath $Chrome -ArgumentList @('--headless=new', '--disable-gpu', '--hide-scrollbars', "--user-data-dir=$ud", "--remote-debugging-port=$Port", '--window-size=1600,1150', $url) -PassThru -WindowStyle Hidden
$script:galatJs = New-Object System.Collections.ArrayList
$ws = $null
try {
  $target = $null
  $sw = [Diagnostics.Stopwatch]::StartNew()
  while (-not $target -and $sw.Elapsed.TotalSeconds -lt 120) {
    try { $target = @(Invoke-RestMethod -Uri "http://127.0.0.1:$Port/json/list" -TimeoutSec 3) | ForEach-Object { $_ } | Where-Object { $_.url -like '*kantor-agent.html*' } | Select-Object -First 1 } catch {}
    if (-not $target) { Start-Sleep -Milliseconds 500 }
  }
  if (-not $target) { throw "target CDP tidak ditemukan dalam 120 detik (port $Port)" }
  Write-Host ("Chrome siap sesudah {0} detik" -f [int]$sw.Elapsed.TotalSeconds)
  $ws = New-Object System.Net.WebSockets.ClientWebSocket
  $ct = [Threading.CancellationToken]::None
  $ws.ConnectAsync([Uri]$target.webSocketDebuggerUrl, $ct).Wait()
  $script:idCdp = 0
  function Cdp([string]$method, $params) {
    $script:idCdp++
    $msg = @{ id = $script:idCdp; method = $method; params = $params } | ConvertTo-Json -Compress -Depth 6
    $bytes = [Text.Encoding]::UTF8.GetBytes($msg)
    $ws.SendAsync([ArraySegment[byte]]::new($bytes), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()
    while ($true) {
      $buf = New-Object byte[] 1048576
      $mem = New-Object IO.MemoryStream
      do { $r = $ws.ReceiveAsync([ArraySegment[byte]]::new($buf), $ct).Result; $mem.Write($buf, 0, $r.Count) } until ($r.EndOfMessage)
      $o = [Text.Encoding]::UTF8.GetString($mem.ToArray()) | ConvertFrom-Json
      if ($o.method -eq 'Runtime.exceptionThrown') { [void]$script:galatJs.Add([string]$o.params.exceptionDetails.exception.description) }
      if ($o.id -eq $script:idCdp) { return $o }
    }
  }
  function Eval([string]$expr) {
    $o = Cdp 'Runtime.evaluate' @{ expression = "JSON.stringify($expr)"; returnByValue = $true }
    $v = $o.result.result.value
    if ($null -eq $v) { return $null }
    return ($v | ConvertFrom-Json)
  }
  function Robot { @((Eval 'window.__KANTOR_UJI__ ? window.__KANTOR_UJI__.robot() : []') | ForEach-Object { $_ }) }
  function Layar { Eval 'window.__KANTOR_UJI__ ? window.__KANTOR_UJI__.layar() : null' }
  function Tunggu([scriptblock]$syarat, [int]$detik) {
    $t = [Diagnostics.Stopwatch]::StartNew()
    while ($t.Elapsed.TotalSeconds -lt $detik) { if (& $syarat) { return $true }; Start-Sleep -Milliseconds 400 }
    return $false
  }
  function Foto([string]$nama) {
    $o = Cdp 'Page.captureScreenshot' @{ format = 'png' }
    $path = Join-Path $Keluaran ($nama + '.png')
    [IO.File]::WriteAllBytes($path, [Convert]::FromBase64String($o.result.data))
    Write-Host "  foto: $path"
  }
  $null = Cdp 'Runtime.enable' @{}

  # 1. memuat: belum ada data.js sama sekali
  $ok = Tunggu { $l = Layar; $l -and $l.kosong -match 'Belum ada data' } 15
  Check $ok '1 memuat: tanpa data.js halaman menyuruh menjalankan /kantor-agent, bukan kosong diam'
  Foto '1-memuat'

  # 2. normal: dua Lead dan satu subagent, semuanya harus TIBA
  Tulis-Data @((Sesi 'aaaaaaaa-1111' 'Lead di server' 'server' 'alat' 'PowerShell' 'pnpm test' @((Sub 'sub1' 'Peneliti' 'perpustakaan' 'alat' 'Grep'))), (Sesi 'bbbbbbbb-2222' 'Lead di meja' 'meja' 'berpikir'))
  $ok = Tunggu { $r = Robot; $r.Count -eq 3 -and -not ($r | Where-Object { $_.jalan }) } 20
  $r = Robot
  $a = $r | Where-Object { $_.key -eq 'aaaaaaaa-1111' }
  $b = $r | Where-Object { $_.key -eq 'bbbbbbbb-2222' }
  $s = $r | Where-Object { $_.key -eq 'aaaaaaaa-1111:sub1' }
  Check ($ok -and $a.area -eq 'server' -and $b.area -eq 'meja' -and $s.area -eq 'perpustakaan') '2 normal: data.js terbaca, 3 robot tiba di server/meja/perpustakaan dan tak ada yang masih berjalan'
  Check ($null -ne $a -and $a.x -ge 12 -and $a.x -le 26 -and $a.y -ge 0 -and $a.y -le 6) "2 posisi robot server benar-benar di dalam ruang server ($($a.x), $($a.y))"
  Check ($null -ne $s -and $s.x -ge 0 -and $s.x -le 12 -and $s.y -ge 0 -and $s.y -le 6) "2 posisi subagent benar-benar di dalam perpustakaan ($($s.x), $($s.y))"
  Foto '2-normal'

  # 3. data berganti tanpa reload; pod dan warna Lead tetap
  $podA = $a.pod; $warnaA = $a.warna; $podB = $b.pod; $warnaB = $b.warna
  Tulis-Data @((Sesi 'aaaaaaaa-1111' 'Lead di server' 'meja' 'alat' 'Edit' 'x.py' @((Sub 'sub1' 'Peneliti' 'perpustakaan' 'alat' 'Grep'))), (Sesi 'bbbbbbbb-2222' 'Lead di meja' 'server' 'alat' 'PowerShell' 'go build'))
  $ok = Tunggu { $bb = Robot | Where-Object { $_.key -eq 'bbbbbbbb-2222' }; $bb -and $bb.area -eq 'server' } 6
  Check $ok '3 data B terbaca dalam 6 detik tanpa reload (Lead meja pindah ke ruang server)'
  $r = Robot
  $a2 = $r | Where-Object { $_.key -eq 'aaaaaaaa-1111' }
  $b2 = $r | Where-Object { $_.key -eq 'bbbbbbbb-2222' }
  Check ($a2.pod -eq $podA -and $a2.warna -eq $warnaA -and $b2.pod -eq $podB -and $b2.warna -eq $warnaB) "3 pod dan warna Lead stabil antar-data (pod $podA/$podB, warna $warnaA/$warnaB)"

  # 3b. ambang diam dan hidup milik penulis (data.ambang), bukan angka yang ditulis mati di halaman
  $diam = Sesi 'aaaaaaaa-1111' 'Lead di server' 'meja' 'alat' 'Edit' 'x.py'
  $diam.diam_detik = 90
  Tulis-Data @($diam, (Sesi 'bbbbbbbb-2222' 'Lead di meja' 'server' 'alat' 'PowerShell' 'go build')) -HidupMenit 45 -DiamMenit 1
  $ok = Tunggu { Eval '!!document.querySelector(''.robot.redup'') && document.getElementById(''ambang-hidup'').textContent === ''45''' } 6
  Check $ok '3b ambang dari penulis: diam_menit 1 meredupkan Lead yang diam 90 detik, footer menyebut 45 menit'

  # 4. ramai: enam Lead di ruang server -> label ringkas
  Tulis-Data (1..6 | ForEach-Object { Sesi ('cccccccc-000' + $_) ('Lead ramai ' + $_) 'server' 'alat' 'PowerShell' 'pnpm test' })
  $ok = Tunggu { @(Robot | Where-Object { -not $_.pergi -and $_.area -eq 'server' -and -not $_.jalan }).Count -eq 6 } 25
  Check $ok '4 ramai: enam Lead tiba di ruang server'
  $habis = Tunggu { @(Robot).Count -eq 6 } 20
  $abu = @(Robot | Where-Object { $_.tipe -eq 'lead' -and $_.warna -eq '#8a8f98' }).Count
  Check ($habis -and $abu -eq 0) "4 ramai: enam Lead baru tak ada yang abu walau Lead lama masih berjalan pulang saat mereka datang ($abu abu)"
  $gelembung = Eval 'document.querySelectorAll("#label .gelembung").length'
  Check ($gelembung -eq 0) "4 ramai: ruang berisi >= 4 robot tanpa gelembung alat ($gelembung gelembung)"
  Foto '4-ramai'

  # 5. format transkrip berubah
  Tulis-Data @((Sesi 'cccccccc-0001' 'Lead ramai 1' 'server' 'alat' 'PowerShell' 'pnpm test')) -Dikenali $false
  $ok = Tunggu { $l = Layar; $l.banner -match 'Format transkrip' } 6
  Check $ok '5 format berubah: banner meminta memperbarui kit'
  Foto '5-format-berubah'

  # 6. kosong: tak ada sesi hidup, semua robot pulang lewat pintu
  Tulis-Data @()
  $ok = Tunggu { $l = Layar; $l.kosong -match 'Tak ada sesi' } 6
  $pulang = Tunggu { (Robot).Count -eq 0 } 20
  Check ($ok -and $pulang) '6 kosong: pesan tak ada sesi hidup, semua robot pulang dan hilang'
  Foto '6-kosong'

  # 7. basi: data 30 detik lalu
  Tulis-Data @((Sesi 'dddddddd-0001' 'Lead basi' 'lounge' 'menunggu_anda')) -UmurDetik 30
  $ok = Tunggu { $l = Layar; $l.basi -and $l.banner -match 'Data berhenti' } 8
  Check $ok '7 basi: banner data berhenti dan robot diredupkan'
  Foto '7-basi'

  # 8. penulis berhenti karena sepi
  Tulis-Data @() -Berhenti 'sepi' -UmurDetik 30
  $ok = Tunggu { $l = Layar; $l.banner -match 'Penulis berhenti' } 8
  Check $ok '8 sepi: banner penulis berhenti, bukan sekadar basi'
  Foto '8-sepi'

  Check ($script:galatJs.Count -eq 0) ("0 galat JavaScript selama uji" + $(if ($script:galatJs.Count) { ': ' + ($script:galatJs -join ' | ') } else { '' }))
}
catch {
  Write-Host "FAIL skrip berhenti: $($_.Exception.Message)"
  $script:fail++
}
finally {
  if ($ws) { try { $ws.Dispose() } catch {} }
  try { Stop-Process -Id $proses.Id -Force -ErrorAction Stop } catch {}
  $profil = [regex]::Escape($ud)
  Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match $profil } | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop } catch {} }
}
Write-Host "Screenshot di: $Keluaran"
if ($script:fail -gt 0) { Write-Host "$($script:fail) gagal"; exit 1 } else { Write-Host 'Semua lulus'; exit 0 }
