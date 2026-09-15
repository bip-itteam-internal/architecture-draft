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
# - kit 1.21.0: gelembung "!" menunggu izin yang tak diredupkan, tanda ? hanya di mode transkrip, menunggu tugas
#   latar, label asal sesi, tombol salin id yang BENAR-BENAR mengisi clipboard (dibaca balik lewat CDP) beserta
#   kedua cadangannya, banner registri tak terbaca, registri tak cocok, dan versi data tak cocok;
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

function Tulis-Data($sesi, [bool]$Dikenali = $true, $Berhenti = $null, [int]$UmurDetik = 0, [int]$HidupMenit = 30, [int]$DiamMenit = 10, [int]$Interval = 2,
    [int]$Versi = 2, [string]$Sumber = 'registri', $RegistriCocok = $null) {
  $data = [ordered]@{
    versi = $Versi
    dibuat = (Get-Date).ToUniversalTime().AddSeconds(-$UmurDetik).ToString('yyyy-MM-ddTHH:mm:ss.fffZ', $inv)
    ambang = [ordered]@{ hidup_menit = $HidupMenit; diam_menit = $DiamMenit }
    skema = [ordered]@{ baris_diurai = 100; baris_rusak = $(if ($Dikenali) { 0 } else { 80 }); dikenali = $Dikenali; dilewati_luar_workspace = 0; sumber_hidup = $Sumber
      registri_dicek = ($null -ne $RegistriCocok); registri_cocok = $RegistriCocok
      registri_catatan = $(if ($null -ne $RegistriCocok) { '3 sesi menurut claude agents' } else { 'tidak dijalankan' }) }
    penulis = [ordered]@{ pid = 1; interval_detik = $Interval; berhenti = $Berhenti; tick_ms = $null }
    sesi = @($sesi)
  }
  $tmp = $dataJs + '.tmp'
  [IO.File]::WriteAllText($tmp, ('window.__KANTOR__ = ' + ($data | ConvertTo-Json -Depth 8 -Compress) + ";`n"), $utf8)
  Move-Item -LiteralPath $tmp -Destination $dataJs -Force
}
function Sesi($id, $judul, $area, $keadaan, $alat = '', $detail = '', $sub = @()) {
  [ordered]@{ id = $id; judul = $judul; tahap = 'implement'; pr = $null; area = $area; keadaan = $keadaan; alat = $alat; detail = $detail
    sejak = $null; durasi_detik = $(if ($alat) { 12 } else { $null }); diam_detik = 5; subagent = @($sub)
    asal = 'claude-vscode'; nama = ('uji-' + $id.Substring(0, 2)); pid = 4242; status_proses = 'busy'; menunggu = $null }
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

  function Teks-Gelembung { @((Eval 'Array.prototype.map.call(document.querySelectorAll("#label .gelembung"), function (g) { return g.textContent; })') | ForEach-Object { $_ }) }

  # 3c. menunggu izin (registri): gelembung "!" di ruang tool, tak diredupkan walau lama; tanpa tanda ? tebakan
  $izin = Sesi 'aaaaaaaa-1111' 'Lead di server' 'server' 'menunggu_izin' 'PowerShell' 'pnpm test'
  $izin.menunggu = 'permission prompt'; $izin.status_proses = 'waiting'; $izin.diam_detik = 900
  $lama = Sesi 'bbbbbbbb-2222' 'Lead di meja' 'server' 'alat' 'PowerShell' 'go build'
  $lama.durasi_detik = 120
  Tulis-Data @($izin, $lama)
  $ok = Tunggu { $aa = Robot | Where-Object { $_.key -eq 'aaaaaaaa-1111' }; $aa -and $aa.izin -and $aa.area -eq 'server' -and -not $aa.jalan } 8
  $gIzin = Eval '(function () { var g = document.querySelector("#label .gelembung.izin"); return g ? g.textContent : null; })()'
  $redup = Eval '!!document.querySelector(".robot.izin.redup, #label .gelembung.izin.redup")'
  $chip = Eval '!!document.querySelector("#k-aaaaaaaa-1111 .chip.izin")'
  Check ($ok -and $gIzin -like '! izin: PowerShell*' -and -not $redup -and $chip) "3c izin: robot bersinar di ruang server, gelembung '$gIzin', chip ! izin, tak diredupkan walau diam 15 menit"
  $semua = Teks-Gelembung
  $tanya = Eval 'document.querySelectorAll(".chip.peringatan").length'
  Check ((@($semua | Where-Object { $_.Contains('?') }).Count -eq 0) -and $tanya -eq 0) "3c registri: tool 2 menit tanpa tanda ? tebakan izin ($($semua -join ' | '))"
  Foto '3c-izin'

  # 3d. menunggu tugas shell latar: tetap di ruang server, bukan lounge "menunggu Anda"
  $latar = Sesi 'aaaaaaaa-1111' 'Lead di server' 'server' 'menunggu_latar' 'PowerShell' 'pnpm build'
  $latar.status_proses = 'idle'
  Tulis-Data @($latar, (Sesi 'bbbbbbbb-2222' 'Lead di meja' 'meja' 'berpikir'))
  $ok = Tunggu { $aa = Robot | Where-Object { $_.key -eq 'aaaaaaaa-1111' }; $aa -and $aa.keadaan -eq 'menunggu_latar' -and -not $aa.izin -and $aa.area -eq 'server' -and -not $aa.jalan } 8
  $gLatar = Teks-Gelembung
  $kiniA = Eval 'document.querySelector("#k-aaaaaaaa-1111 .kini").textContent'
  Check ($ok -and ($gLatar -contains 'tugas latar: pnpm build') -and $kiniA -like '*menunggu tugas latar: pnpm build*') "3d latar: robot tetap di ruang server, gelembung dan kartu menyebut tugas latar ($kiniA)"

  # 3e. asal sesi + tombol salin id. Clipboard DIBACA BALIK; teks tombol saja bisa berbunyi tersalin untuk salinan yang gagal.
  # Tool A 2 menit membuat kartunya berubah tiap detik, jadi umpan balik salin diuji melewati render ulang.
  $vs = Sesi 'aaaaaaaa-1111' 'Lead di server' 'server' 'alat' 'PowerShell' 'pnpm test'
  $vs.durasi_detik = 120
  $term = Sesi 'bbbbbbbb-2222' 'Lead di meja' 'meja' 'berpikir'
  $term.asal = 'cli'
  Tulis-Data @($vs, $term)
  $ok = Tunggu { (Eval '(function () { var c = document.querySelector("#k-bbbbbbbb-2222 .chip.asal"); return c ? c.textContent : null; })()') -eq 'terminal' } 6
  $asalA = Eval '(function () { var c = document.querySelector("#k-aaaaaaaa-1111 .chip.asal"); return c ? c.textContent : null; })()'
  $arahB = Eval '(function () { var p = document.querySelector("#k-bbbbbbbb-2222 .petunjuk"); return p ? p.textContent : null; })()'
  Check ($ok -and $asalA -eq 'VS Code' -and $arahB -like '*terminal*' -and $arahB -like '*pid 4242*') "3e asal: kartu berlabel VS Code dan terminal, petunjuk '$arahB'"

  function CdpBrowser([string]$method, $params) {
    # izin clipboard milik browser, bukan halaman: dikirim lewat soket browser dari /json/version
    $wb = New-Object System.Net.WebSockets.ClientWebSocket
    try {
      $wb.ConnectAsync([Uri](Invoke-RestMethod -Uri "http://127.0.0.1:$Port/json/version" -TimeoutSec 5).webSocketDebuggerUrl, $ct).Wait()
      $b = [Text.Encoding]::UTF8.GetBytes((@{ id = 1; method = $method; params = $params } | ConvertTo-Json -Compress -Depth 6))
      $wb.SendAsync([ArraySegment[byte]]::new($b), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()
      $buf = New-Object byte[] 65536
      $mem = New-Object IO.MemoryStream
      do { $r = $wb.ReceiveAsync([ArraySegment[byte]]::new($buf), $ct).Result; $mem.Write($buf, 0, $r.Count) } until ($r.EndOfMessage)
      return ([Text.Encoding]::UTF8.GetString($mem.ToArray()) | ConvertFrom-Json)
    } finally { $wb.Dispose() }
  }
  function Klik([string]$sel) { $null = Cdp 'Runtime.evaluate' @{ expression = "document.querySelector('$sel').click()"; userGesture = $true } }
  function Isi-Clipboard {
    # navigator.clipboard.readText ditolak di file:// walau Browser.grantPermissions berhasil (terukur 2026-09-15), jadi
    # clipboard dibaca dengan MENEMPEL: perintah edit "paste" lewat Input.dispatchKeyEvent ke textarea uji
    $null = Cdp 'Runtime.evaluate' @{ expression = '(function () { var t = document.getElementById("uji-tempel"); if (!t) { t = document.createElement("textarea"); t.id = "uji-tempel"; document.body.appendChild(t); } t.value = ""; t.focus(); })()' }
    $null = Cdp 'Input.dispatchKeyEvent' @{ type = 'keyDown'; modifiers = 2; key = 'v'; code = 'KeyV'; windowsVirtualKeyCode = 86; commands = @('paste') }
    $null = Cdp 'Input.dispatchKeyEvent' @{ type = 'keyUp'; modifiers = 2; key = 'v'; code = 'KeyV'; windowsVirtualKeyCode = 86 }
    return (Eval '(function () { var t = document.getElementById("uji-tempel"), v = t.value; t.remove(); return v; })()')
  }
  function Timpa-Clipboard { $null = Cdp 'Runtime.evaluate' @{ expression = 'navigator.clipboard.writeText("-")'; awaitPromise = $true; userGesture = $true } }
  function Teks-Tombol([string]$id) { Eval ('document.querySelector("#k-' + $id + ' .salin").textContent') }

  $izinClip = CdpBrowser 'Browser.grantPermissions' @{ permissions = @('clipboardReadWrite', 'clipboardSanitizedWrite') }
  Check ($null -eq $izinClip.error) "3e uji: izin clipboard diberikan lewat CDP browser $(if ($izinClip.error) { $izinClip.error.message })"
  $null = Cdp 'Page.bringToFront' @{}
  $null = Cdp 'Emulation.setFocusEmulationEnabled' @{ enabled = $true }

  Timpa-Clipboard
  Klik '#k-aaaaaaaa-1111 .salin'
  $ok = Tunggu { (Teks-Tombol 'aaaaaaaa-1111') -eq 'tersalin' } 5
  $isi = Isi-Clipboard
  Check ($ok -and $isi -eq 'aaaaaaaa-1111') "3e salin: tombol berbunyi tersalin dan clipboard berisi id sesi lengkap ('$isi')"

  Timpa-Clipboard
  $null = Cdp 'Runtime.evaluate' @{ expression = 'navigator.clipboard.writeText = function () { return Promise.reject(new Error("uji: clipboard ditolak")); }' }
  Klik '#k-bbbbbbbb-2222 .salin'
  $ok = Tunggu { (Teks-Tombol 'bbbbbbbb-2222') -eq 'tersalin' } 5
  $null = Cdp 'Runtime.evaluate' @{ expression = 'delete navigator.clipboard.writeText' }
  $isi = Isi-Clipboard
  Check ($ok -and $isi -eq 'bbbbbbbb-2222') "3e salin cadangan: clipboard API ditolak, execCommand tetap mengisi clipboard ('$isi')"

  $null = Cdp 'Runtime.evaluate' @{ expression = 'navigator.clipboard.writeText = function () { return Promise.reject(new Error("uji")); }; document.execCommand = function () { return false; }' }
  Klik '#k-aaaaaaaa-1111 .salin'
  $ok = Tunggu { (Eval '(function () { var m = document.querySelector("#k-aaaaaaaa-1111 .id-manual"); return !!m && m.value === "aaaaaaaa-1111" && document.activeElement === m && m.selectionEnd - m.selectionStart === m.value.length; })()') -eq $true } 5
  $tombol = Teks-Tombol 'aaaaaaaa-1111'
  Start-Sleep -Seconds 3
  $tetap = Eval '(function () { var m = document.activeElement; return !!m && m.classList.contains("id-manual") && m.selectionEnd - m.selectionStart === m.value.length; })()'
  $null = Cdp 'Runtime.evaluate' @{ expression = 'delete navigator.clipboard.writeText; delete document.execCommand' }
  Check ($ok -and $tombol -eq 'salin manual' -and $tetap) "3e salin manual: kedua jalan gagal -> kolom id terpilih, tetap terpilih melewati render tiap detik (tombol '$tombol')"
  Foto '3e-salin-manual'

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

  # 5b. registri tak terbaca -> mode transkrip: banner, dan tanda ? tebakan izin kembali (kontrol positif untuk 3c)
  $trans = Sesi 'cccccccc-0001' 'Lead ramai 1' 'server' 'alat' 'PowerShell' 'pnpm test'
  $trans.durasi_detik = 120; $trans.asal = $null; $trans.nama = $null; $trans.pid = $null; $trans.status_proses = $null
  Tulis-Data @($trans) -Sumber 'transkrip'
  $ok = Tunggu { $l = Layar; $l.banner -match 'Registri sesi Claude Code' -and $l.banner -notmatch 'Format transkrip' } 6
  $tanya = Tunggu { (Eval 'document.querySelectorAll(".chip.peringatan").length') -ge 1 } 4
  Check ($ok -and $tanya) '5b mode transkrip: banner registri tak terbaca, tanda ? izin muncul untuk tool 2 menit'
  Foto '5b-mode-transkrip'

  # 5c. registri tak cocok dengan claude agents -> banner; cocok lagi -> banner hilang (kontrol negatif)
  Tulis-Data @((Sesi 'cccccccc-0001' 'Lead ramai 1' 'server' 'alat' 'PowerShell' 'pnpm test')) -RegistriCocok $false
  $ok = Tunggu { $l = Layar; $l.banner -match 'tidak cocok dengan claude agents' } 6
  Foto '5c-registri-tak-cocok'
  Tulis-Data @((Sesi 'cccccccc-0001' 'Lead ramai 1' 'server' 'alat' 'PowerShell' 'pnpm test')) -RegistriCocok $true
  $hilang = Tunggu { $l = Layar; $l.banner -eq '' } 6
  Check ($ok -and $hilang) '5c registri tak cocok: banner menyebut claude agents, lalu hilang saat cocok'

  # 5d. data versi lain (penulis dari kit lama masih jalan): tidak ditafsirkan, robot pulang, banner menyebut jalan keluarnya
  Tulis-Data @((Sesi 'cccccccc-0001' 'Lead ramai 1' 'server' 'alat' 'PowerShell' 'pnpm test')) -Versi 1
  $ok = Tunggu { $l = Layar; $l.banner -match 'versi 1' -and $l.banner -match '--berhenti' -and $l.kosong -match 'Versi data' } 6
  $pulang = Tunggu { (Robot).Count -eq 0 } 20
  Check ($ok -and $pulang) '5d versi: data versi 1 tidak ditafsirkan, banner menyuruh --berhenti lalu /kantor-agent, robot pulang'
  Foto '5d-versi'

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

  # 7b. --sekali (interval 0): snapshot yang disengaja tidak boleh berbunyi "penulis mati"
  Tulis-Data @((Sesi 'dddddddd-0001' 'Lead basi' 'lounge' 'menunggu_anda')) -UmurDetik 30 -Interval 0
  $ok = Tunggu { $l = Layar; $l.basi -and $l.banner -match 'Snapshot sekali' -and $l.banner -notmatch 'mati' } 8
  Check $ok '7b sekali: banner snapshot sekali, bukan penulis mati'

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
