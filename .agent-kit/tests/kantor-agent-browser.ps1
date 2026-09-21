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
# TANPA --hide-scrollbars: flag itu membuat lebar bilah gulir terukur 0px, sehingga uji ketebalan bilah
# di 3h akan lolos untuk aturan CSS apa pun. Bilah yang ikut terpotret di screenshot adalah harga yang murah.
$proses = Start-Process -FilePath $Chrome -ArgumentList @('--headless=new', '--disable-gpu', "--user-data-dir=$ud", "--remote-debugging-port=$Port", '--window-size=1600,1150', $url) -PassThru -WindowStyle Hidden
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
  # pengguna selesai menyalin: fokus keluar dari kolom, supaya panel tak tertahan 15 detik di langkah berikutnya
  $null = Cdp 'Runtime.evaluate' @{ expression = 'delete navigator.clipboard.writeText; delete document.execCommand; document.activeElement && document.activeElement.blur()' }
  Check ($ok -and $tombol -eq 'salin manual' -and $tetap) "3e salin manual: kedua jalan gagal -> kolom id terpilih, tetap terpilih melewati render tiap detik (tombol '$tombol')"
  Foto '3e-salin-manual'

  # 3f. arah hadap: duduk mengikuti perabot, berjalan mengikuti jalur. Wajah hanya tergambar saat hadap selatan
  # atau timur, karena proyeksi ini tak pernah memperlihatkan sisi utara dan barat.
  function Arah([string]$key) { $r = Robot | Where-Object { $_.key -eq $key }; if ($r) { return $r.arah }; return $null }
  # keadaan 'alat' dipakai, bukan 'berpikir': histeresis berpikir menahan robot di ruang sebelumnya 20 detik
  # dua subagent supaya KEDUA bangku pod terisi: yang di barat meja menghadap timur, yang di timur menghadap barat
  Tulis-Data @((Sesi 'aaaaaaaa-1111' 'Lead di meja' 'meja' 'alat' 'Edit' 'x.py' @((Sub 'sub1' 'Peneliti' 'meja' 'alat' 'Edit'), (Sub 'sub2' 'Peneliti' 'meja' 'alat' 'Edit'))),
    (Sesi 'bbbbbbbb-2222' 'Lead di server' 'server' 'alat' 'PowerShell' 'pnpm test'),
    (Sesi 'cccccccc-3333' 'Lead di rapat' 'rapat' 'menunggu_subagent'),
    (Sesi 'cccccccc-3334' 'Lead di rapat 2' 'rapat' 'menunggu_subagent'),
    (Sesi 'cccccccc-3335' 'Lead di rapat 3' 'rapat' 'menunggu_subagent'),
    (Sesi 'cccccccc-3336' 'Lead di rapat 4' 'rapat' 'menunggu_subagent'),
    (Sesi 'dddddddd-4444' 'Lead di lounge' 'lounge' 'menunggu_anda'),
    (Sesi 'eeeeeeee-5555' 'Lead di perpustakaan' 'perpustakaan' 'alat' 'Grep' 'pola'))
  $ok = Tunggu { @(Robot | Where-Object { -not $_.pergi -and -not $_.jalan }).Count -eq 10 } 40
  $rA = Robot | Where-Object { $_.key -eq 'aaaaaaaa-1111' }
  Check ($ok -and (Arah 'aaaaaaaa-1111') -eq 'selatan') "3f arah: Lead di pod menghadap mejanya, selatan (dapat '$(Arah 'aaaaaaaa-1111')')"
  $barat = Robot | Where-Object { $_.key -like 'aaaaaaaa-1111:*' -and $_.x -lt $rA.x }
  $timur = Robot | Where-Object { $_.key -like 'aaaaaaaa-1111:*' -and $_.x -gt $rA.x }
  Check ($barat -and $timur -and $barat.arah -eq 'timur' -and $timur.arah -eq 'barat') "3f arah: bangku pod sisi barat menghadap timur dan sisi timur menghadap barat (dapat '$($barat.arah)' dan '$($timur.arah)')"
  Check ((Arah 'bbbbbbbb-2222') -eq 'utara') "3f arah: robot ruang server menghadap rak, utara (dapat '$(Arah 'bbbbbbbb-2222')')"
  Check ((Arah 'eeeeeeee-5555') -eq 'utara') "3f arah: robot perpustakaan menghadap rak buku, utara (dapat '$(Arah 'eeeeeeee-5555')')"
  Check ((Arah 'dddddddd-4444') -eq 'selatan') "3f arah: robot lounge menghadap penonton, selatan (dapat '$(Arah 'dddddddd-4444')')"
  # empat kursi terisi supaya KEDUA sumbu pembulatan teruji: satu kursi saja bisa kebetulan timur/barat
  # sehingga cabang utara/selatan lolos tanpa penjaga
  $rapatSemua = @(Robot | Where-Object { $_.area -eq 'rapat' -and -not $_.pergi })
  $salah = @()
  foreach ($r in $rapatSemua) {
    $dx = 22 - $r.x; $dy = 11.5 - $r.y
    $h = if ([Math]::Abs($dx) -ge [Math]::Abs($dy)) { if ($dx -ge 0) { 'timur' } else { 'barat' } } else { if ($dy -ge 0) { 'selatan' } else { 'utara' } }
    if ($r.arah -ne $h) { $salah += ("{0} di ({1};{2}) menghadap {3}, seharusnya {4}" -f $r.key.Substring(0, 8), $r.x, $r.y, $r.arah, $h) }
  }
  $sumbuX = @($rapatSemua | Where-Object { $_.arah -eq 'timur' -or $_.arah -eq 'barat' }).Count
  $sumbuY = @($rapatSemua | Where-Object { $_.arah -eq 'utara' -or $_.arah -eq 'selatan' }).Count
  Check ($rapatSemua.Count -ge 4 -and $salah.Count -eq 0 -and $sumbuX -ge 1 -and $sumbuY -ge 1) "3f arah: $($rapatSemua.Count) kursi ruang rapat menghadap pusat meja, dibulatkan empat arah, kedua sumbu terwakili ($sumbuX timur/barat, $sumbuY utara/selatan; salah: $($salah -join '; '))"
  # Mata dihitung lewat KELAS, bukan lewat warnanya: sejak robot modern (1.26.0) warna mata =
  # warna sesi, jadi mematok '88ffff' akan hijau untuk implementasi apa pun dan check-nya vakum.
  # Kontrol positifnya wajib ada di baris yang sama: 0 mata tanpa pembanding tak membuktikan
  # bahwa yang menghadap kamera MEMANG bermata.
  $mataUtara = Eval '(function () { var g = document.querySelector("[data-lead=eeeeeeee-5555] .badan"); return g ? g.querySelectorAll(".mata").length : -1; })()'
  $mataDepan = Eval '(function () { var g = document.querySelector("[data-lead=dddddddd-4444] .badan"); return g ? g.querySelectorAll(".mata").length : -1; })()'
  $senyumDepan = Eval '(function () { var g = document.querySelector("[data-lead=dddddddd-4444] .badan"); return g ? g.querySelectorAll(".senyum").length : -1; })()'
  Check ($mataUtara -eq 0 -and $mataDepan -eq 2 -and $senyumDepan -eq 1) "3f arah: yang menghadap utara digambar dari punggung tanpa mata ($mataUtara), yang menghadap selatan bermata dua dan bersenyum ($mataDepan mata, $senyumDepan senyum)"
  # Identitas sesi pindah ke cahaya visor, jadi warna mata WAJIB ikut warna sesi, bukan tetap cyan
  $warnaMata = Eval '(function () { var g = document.querySelector("[data-lead=dddddddd-4444] .badan .mata"); return g ? g.getAttribute("fill") : ""; })()'
  Check ($warnaMata -and $warnaMata -ne '#88ffff' -and $warnaMata -match '^#') "3f identitas: mata memakai warna sesi, bukan cyan tetap (dapat '$warnaMata')"
  $ledOk = Eval '(function () { var e = document.getElementById("led-pod-0"); return !!e && !!e.getAttribute("fill"); })()'
  Check ($ledOk -eq $true) '3f pod: penanda warna Lead tetap ada sesudah layar monitor diputar menghadap robot'
  Foto '3f-arah'

  # 3g. arah saat berjalan mengikuti jalur, lalu kembali ke arah kursinya setibanya
  Tulis-Data @((Sesi 'eeeeeeee-5555' 'Lead di perpustakaan' 'server' 'alat' 'PowerShell' 'jalan jauh'))
  Check (Tunggu { $r = Robot | Where-Object { $_.key -eq 'eeeeeeee-5555' }; $r -and $r.jalan -and $r.arah -eq 'timur' } 12) '3g arah: robot yang berjalan ke ruang server menghadap timur selagi berjalan'
  Check (Tunggu { $r = Robot | Where-Object { $_.key -eq 'eeeeeeee-5555' }; $r -and -not $r.jalan -and $r.arah -eq 'utara' } 20) '3g arah: setibanya di ruang server, arahnya kembali mengikuti kursinya (utara)'
  # BADAN-nya, bukan cuma keadaan arah: titik berdiri ruang server tak mengubah dudukZ, jadi bila kunci cache
  # gambarBadan tak memuat arah, badan hasil jalan ke timur (bermata) tetap terpasang dan mata masih terhitung
  $mataTiba = Eval '(function () { var g = document.querySelector("[data-lead=eeeeeeee-5555] .badan"); return g ? (g.innerHTML.match(/88ffff/g) || []).length : -1; })()'
  Check ($mataTiba -eq 0) "3g arah: badan digambar ulang saat berputar, bukan cuma keadaannya ($mataTiba mata sesudah menghadap utara)"

  # 3h. panel samping bisa disembunyikan, dan bilah gulirnya lebih tipis dari bawaan peramban.
  # Lebar bilah WAJIB diukur di peramban dengan elemen KONTROL pembanding: membacanya dari aturan CSS
  # menyesatkan, karena scrollbar-width dan ::-webkit-scrollbar tidak sama-sama berlaku di tiap peramban.
  $bilah = Eval '(function () {
    var a = document.getElementById("sisi");
    var k = document.createElement("div");
    k.style.cssText = "position:absolute;left:-9999px;top:0;width:200px;height:100px;overflow-y:scroll";
    k.innerHTML = "<div style=\"height:400px\"></div>";
    document.body.appendChild(k);
    var kontrol = k.offsetWidth - k.clientWidth;
    var sisiAsli = a.style.overflowY;
    a.style.overflowY = "scroll";
    var cs = getComputedStyle(a);
    var tepi = parseFloat(cs.borderLeftWidth) + parseFloat(cs.borderRightWidth);
    var panel = a.offsetWidth - a.clientWidth - tepi;
    a.style.overflowY = sisiAsli;
    k.parentNode.removeChild(k);
    return { panel: panel, kontrol: kontrol };
  })()'
  Check ($bilah.panel -gt 0 -and $bilah.panel -le 6 -and $bilah.panel -lt $bilah.kontrol) "3h panel: bilah gulir panel $($bilah.panel)px, lebih tipis dari bilah bawaan $($bilah.kontrol)px"
  $sebelum = Eval '(function () { return document.getElementById("panggung").getBoundingClientRect().width; })()'
  Eval '(function () { document.getElementById("saklar-panel").click(); return 1; })()' | Out-Null
  $sesudah = Eval '(function () {
    var a = document.getElementById("sisi"), s = document.getElementById("saklar-panel");
    return { sembunyi: a.hidden, satuKolom: document.querySelector("main").classList.contains("tanpa-panel"),
      teks: s.textContent.trim(), aria: s.getAttribute("aria-expanded"),
      panggung: document.getElementById("panggung").getBoundingClientRect().width };
  })()'
  Check ($sesudah.sembunyi -eq $true -and $sesudah.satuKolom -eq $true -and $sesudah.teks -eq 'tampilkan panel' -and $sesudah.aria -eq 'false' -and $sesudah.panggung -gt $sebelum) "3h panel: saklar menyembunyikan panel dan denah melebar ($([int]$sebelum)px -> $([int]$sesudah.panggung)px)"
  Eval '(function () { document.getElementById("saklar-panel").click(); return 1; })()' | Out-Null
  $kembali = Eval '(function () {
    var a = document.getElementById("sisi"), s = document.getElementById("saklar-panel");
    return { tampil: !a.hidden, teks: s.textContent.trim(), aria: s.getAttribute("aria-expanded"),
      kartu: document.querySelectorAll("#panel .kartu").length };
  })()'
  Check ($kembali.tampil -eq $true -and $kembali.teks -eq 'sembunyikan panel' -and $kembali.aria -eq 'true' -and $kembali.kartu -gt 0) "3h panel: saklar mengembalikannya lengkap dengan kartunya ($($kembali.kartu) kartu)"
  Foto '3h-panel'

  # 3i. menyorot sebuah sesi memperbesar denah ke robotnya, dan kameranya mengikutinya berjalan.
  # Yang diukur viewBox SUNGGUHAN, bukan sekadar kelas .sorot: kelas bisa terpasang sementara
  # kameranya tak bergerak sama sekali, dan check yang cuma melihat kelas akan hijau untuk itu.
  function ViewBox { $v = Eval '(function () { return document.getElementById("denah").getAttribute("viewBox"); })()'; return @($v -split '\s+' | ForEach-Object { [double]$_ }) }
  $vAwal = ViewBox
  # id sesi yang hidup berganti antar langkah, jadi yang diklik robot mana pun yang sedang ada;
  # mematok id membuat check-nya gagal bukan karena kameranya, melainkan karena robotnya tak ada
  $adaRobot = Eval '(function () { var g = document.querySelector("#dunia .robot[data-lead]"); if (!g) return 0; g.dispatchEvent(new MouseEvent("click", { bubbles: true })); return 1; })()'
  $okZoom = Tunggu { $v = ViewBox; $v[2] -lt ($vAwal[2] * 0.6) } 8
  $vZoom = ViewBox
  Check ($adaRobot -eq 1 -and $okZoom -and $vZoom[2] -lt $vAwal[2]) "3i kamera: menyorot sesi memperbesar denah (lebar viewBox $([int]$vAwal[2]) -> $([int]$vZoom[2]))"
  # pusat kamera benar-benar mendarat di robotnya, bukan sekadar mengecil di tempat
  $dekat = Eval '(function () {
    var v = document.getElementById("denah").getAttribute("viewBox").trim().split(/\s+/).map(Number);
    var g = document.querySelector("#dunia .robot.sorot");
    if (!g) return -1;
    var m = /translate\(([-0-9.]+),([-0-9.]+)\)/.exec(g.getAttribute("transform") || "");
    if (!m) return -1;
    return Math.abs((v[0] + v[2] / 2) - parseFloat(m[1]));
  })()'
  Check ($dekat -ge 0 -and $dekat -lt 40) "3i kamera: pusatnya mendarat di robot yang disorot (selisih $([int]$dekat)px)"
  $chipZoom = Eval '(function () { var e = document.getElementById("lepas-sorot"); return !!e && !e.hidden; })()'
  Check ($chipZoom -eq $true) '3i kamera: petunjuk cara keluar tampil selagi kamera mengikuti'
  Foto '3i-kamera'
  Eval '(function () { document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true })); return 1; })()' | Out-Null
  $okLepas = Tunggu { $v = ViewBox; [Math]::Abs($v[2] - $vAwal[2]) -lt 1 } 8
  $chipLepas = Eval '(function () { var e = document.getElementById("lepas-sorot"); return !!e && e.hidden; })()'
  $vAkhir = ViewBox
  Check ($okLepas -and $chipLepas -eq $true) "3i kamera: Esc melepas sorotan dan kamera kembali ke denah penuh (lebar $([int]$vAkhir[2]))"

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
