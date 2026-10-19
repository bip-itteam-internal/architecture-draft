# test-tangkap-layar.ps1 - tangkap-layar.ps1 + tangkap-layar.mjs atas worktree PALSU sekali-pakai.
# Worktree palsu punya `.next/BUILD_ID` dan skrip `start` yang menyajikan fixtures/layar/ lewat
# server statis Node, jadi jalur PENUH (pilih port -> pnpm start -> tunggu listen -> Chrome CDP ->
# hentikan pohon proses) teruji tanpa build erp-frontend sungguhan.
# Dipanggil test-init.ps1; dilewati dengan pesan tercetak bila Chrome tidak ada.
$ErrorActionPreference = 'Continue'
$kitRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$ps1 = Join-Path $kitRoot 'hooks/tangkap-layar.ps1'
$mjs = Join-Path $kitRoot 'hooks/tangkap-layar.mjs'
$lib = Join-Path $kitRoot 'hooks/layar-lib.py'
$fixture = Join-Path $kitRoot 'tests/fixtures/layar'
$fail = 0
function Check($cond, $name) { if ($cond) { Write-Host "PASS $name" } else { Write-Host "FAIL $name"; $script:fail++ } }

$chromeExe = @('C:\Program Files\Google\Chrome\Application\chrome.exe', 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe') | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $chromeExe) { $chromeExe = 'C:\Program Files\Google\Chrome\Application\chrome.exe' }
if (-not (Test-Path -LiteralPath $chromeExe)) { Write-Host "LEWAT test-tangkap-layar: Chrome tidak ada di $chromeExe"; exit 0 }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Write-Host 'LEWAT test-tangkap-layar: node tidak ada di PATH'; exit 0 }
if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) { Write-Host 'LEWAT test-tangkap-layar: pnpm tidak ada di PATH'; exit 0 }

$id = [guid]::NewGuid().ToString('N').Substring(0, 8)
$tmp = Join-Path $env:TEMP ('agentkit-layar-' + $id)
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
# Profil Chrome ditaruh di bawah $tmp supaya pemeriksaan "tak ada Chrome tersisa" hanya melihat
# proses MILIK test ini, bukan browser user atau run tangkapan sesi lain.
$env:TANGKAP_LAYAR_PROFIL_DASAR = Join-Path $tmp 'profil'
# Nama skrip server unik: command line `node serve-<id>.mjs` tak memuat path $tmp, jadi pembersihan
# di finally mencocokkan nama ini.
$serve = "serve-$id.mjs"; $diam = "diam-$id.js"
$utf8 = New-Object System.Text.UTF8Encoding($false)
function Tulis([string]$p, [string]$isi) { [IO.File]::WriteAllText($p, $isi, $utf8) }
function Proses([string]$pola) {
  @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -and $_.CommandLine -like $pola })
}
function Jalankan([string[]]$argumen) {
  & powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File $ps1 @argumen | Out-Host
  return $LASTEXITCODE
}

try {
  Check (Test-Path -LiteralPath $ps1) 'hooks/tangkap-layar.ps1 ada'
  Check (Test-Path -LiteralPath $mjs) 'hooks/tangkap-layar.mjs ada'

  # ---- worktree palsu: build "ada", start = server statis atas salinan fixture ----
  $wt = Join-Path $tmp 'wt'
  New-Item -ItemType Directory -Force -Path (Join-Path $wt '.next'), (Join-Path $wt 'situs') | Out-Null
  Tulis (Join-Path $wt '.next/BUILD_ID') 'uji'
  Copy-Item -Path (Join-Path $fixture '*') -Destination (Join-Path $wt 'situs') -Recurse
  Tulis (Join-Path $wt 'package.json') ('{"name":"wt-uji","private":true,"scripts":{"start":"node ' + $serve + '"}}')
  Tulis (Join-Path $wt $serve) @'
import http from "node:http"; import fs from "node:fs"; import path from "node:path";
const i = process.argv.indexOf("-p"); const port = Number(process.argv[i + 1]);
const akar = path.join(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")), "situs");
http.createServer((req, res) => {
  const p = path.join(akar, decodeURIComponent(new URL(req.url, "http://x").pathname));
  if (p.startsWith(akar) && fs.existsSync(p) && fs.statSync(p).isFile()) {
    res.writeHead(200, { "content-type": "text/html; charset=utf-8" }); res.end(fs.readFileSync(p));
  } else { res.writeHead(404, { "content-type": "text/plain" }); res.end("tidak ada"); }
}).listen(port);
'@

  $manifest = Join-Path $tmp 'manifest.json'
  Tulis $manifest @'
{
  "rute": [
    {"path": "/index.html", "keadaan": ["berisi", "kosong"], "aksi": [{"klik_teks": "Buka panel"}]},
    {"path": "/tidak-ada.html", "keadaan": ["berisi"]},
    {"path": "/galat.html", "keadaan": ["berisi"]}
  ],
  "cookie": {"system_roles": {"hris": "supervisor"}, "position": "Staff", "department": "Information Technology", "lang": "id"},
  "stub": {
    "berisi": [{"pola": "/api/x", "status": 200, "body": {"isi": "berisi-uji"}}],
    "kosong": [{"pola": "/api/x", "status": 200, "body": {"isi": []}}]
  }
}
'@
  if (Get-Command python -ErrorAction SilentlyContinue) {
    & python $lib validasi $manifest | Out-Null
    Check ($LASTEXITCODE -eq 0) 'manifest uji sah menurut layar-lib.py validasi'
  } else { Write-Host 'LEWAT validasi manifest uji: python tidak ada di PATH' }

  $out = Join-Path $tmp 'keluaran'
  $rc = Jalankan @('-Path', $wt, '-Manifest', $manifest, '-Keluaran', $out)
  $rj = Join-Path $out 'ringkasan.json'
  Check ($rc -eq 0) "tangkap-layar.ps1 exit 0 (exit $rc)"
  Check (Test-Path -LiteralPath $rj) 'ringkasan.json tertulis'
  $r = $null
  if (Test-Path -LiteralPath $rj) { $r = [IO.File]::ReadAllText($rj, $utf8) | ConvertFrom-Json }
  $rute = @(); if ($r) { $rute = @($r.rute) }
  Check ($r -and $null -eq $r.galat) "ringkasan tanpa galat global ($($r.galat))"
  Check ($r -and $r.url_dasar -match '^http://localhost:\d+$' -and $r.url_dasar -notmatch ':3000$') "url_dasar localhost, bukan port 3000 ($($r.url_dasar))"

  $idx = @($rute | Where-Object { $_.path -eq '/index.html' })
  $berisi = @($idx | Where-Object { $_.keadaan -eq 'berisi' })
  $kosong = @($idx | Where-Object { $_.keadaan -eq 'kosong' })
  $kombinasi = @($berisi | ForEach-Object { '{0}-{1}' -f $_.lebar, $_.tema } | Sort-Object)
  Check ($berisi.Count -eq 4 -and ($kombinasi -join ',') -eq '1366-dark,1366-light,390-dark,390-light') "index berisi: 4 entri 2 lebar x 2 tema ($($kombinasi -join ','))"
  Check ($kosong.Count -eq 1 -and $kosong[0].lebar -eq 1366 -and $kosong[0].tema -eq 'light') "index kosong: 1 entri desktop terang ($($kosong.Count))"
  Check (@($idx | Where-Object { $_.tema_terbukti -ne $_.tema }).Count -eq 0 -and $idx.Count -eq 5) "tema_terbukti = tema di semua entri index ($(@($idx | ForEach-Object { $_.tema + '/' + $_.tema_terbukti }) -join ' '))"
  Check ($idx.Count -eq 5 -and @($idx | Where-Object { $_.status_http -ne 200 -or $_.galat }).Count -eq 0) 'entri index: status 200 tanpa galat'
  Check ($idx.Count -eq 5 -and @($idx | Where-Object { -not $_.png -or -not (Test-Path -LiteralPath $_.png) }).Count -eq 0) 'tiap entri index punya PNG yang ada di disk'
  $png0 = @($berisi | Where-Object { $_.lebar -eq 390 -and $_.tema -eq 'dark' })
  Check ($png0.Count -eq 1 -and (Split-Path -Leaf $png0[0].png) -match '^\d+-berisi-390-dark\.png$') "nama PNG <i>-<keadaan>-<lebar>-<tema>.png ($(if ($png0.Count) { Split-Path -Leaf $png0[0].png }))"
  if ($png0.Count -eq 1 -and (Test-Path -LiteralPath $png0[0].png)) {
    Add-Type -AssemblyName System.Drawing
    $img = [System.Drawing.Image]::FromFile($png0[0].png)
    $lebarPng = $img.Width; $img.Dispose()
    Check ($lebarPng -eq 390) "PNG ponsel selebar viewport 390, bukan halaman penuh ($lebarPng)"
  }

  $d = @($berisi | Where-Object { $_.lebar -eq 1366 -and $_.tema -eq 'light' }) | Select-Object -First 1
  $p = @($berisi | Where-Object { $_.lebar -eq 390 -and $_.tema -eq 'light' }) | Select-Object -First 1
  $selD = @(); if ($d) { $selD = @($d.ukuran.luber_wadah | ForEach-Object { $_.selektor }) }
  Check (@($selD | Where-Object { $_ -like '*#wadah-luber*' }).Count -ge 1) "luber_wadah memuat #wadah-luber ($($selD -join ' | '))"
  Check ($d -and @($selD | Where-Object { $_ -like '*#wadah-rapi*' }).Count -eq 0) 'luber_wadah TIDAK memuat #wadah-rapi'
  Check (@($selD | Where-Object { $_ -like '*#wadah-panel*' }).Count -ge 1) 'aksi klik_teks "Buka panel" dijalankan (#wadah-panel terlihat dan meluber)'
  Check ($d -and $d.ukuran.luber_halaman -eq $false) 'desktop 1366: halaman tidak meluber'
  Check ($p -and $p.ukuran.luber_halaman -eq $true) 'ponsel 390: halaman meluber oleh elemen 600px (lebar benar-benar diemulasi)'
  $tump = @(); if ($d) { $tump = @($d.ukuran.tumpang | ForEach-Object { $_.a }) }
  Check (@($tump | Where-Object { $_ -like '*#tombol-tertutup*' }).Count -ge 1) "tumpang memuat #tombol-tertutup ($($tump -join ' | '))"
  Check ($d -and @($tump | Where-Object { $_ -like '*#tombol-utama*' }).Count -eq 0) 'overlay "Nanti saja" ditutup: #tombol-utama tidak tertimpa'
  $dis = @(); if ($d) { $dis = @($d.ukuran.disabled) }
  Check (@($dis | Where-Object { $_.teks -eq 'Kirim' -and $_.opacity -eq '0.5' }).Count -eq 1) "disabled memuat tombol Kirim ber-opacity 0.5 ($(@($dis | ForEach-Object { $_.teks + ':' + $_.opacity }) -join ' '))"

  $konD = @(); if ($d) { $konD = @($d.konsol) }
  $konK = @(); if ($kosong.Count) { $konK = @($kosong[0].konsol) }
  Check (@($konD | Where-Object { $_ -match 'uji-stub /api/x 200 \{"isi":"berisi-uji"\}' }).Count -ge 1) "/api/x menerima body stub keadaan berisi"
  Check (@($konK | Where-Object { $_ -match 'uji-stub /api/x 200 \{"isi":\[\]\}' }).Count -ge 1) "/api/x menerima body stub keadaan kosong"
  Check (@($konD | Where-Object { $_ -match 'uji-stub /api/tak-distub 500' }).Count -ge 1) '/api/tak-distub menerima 500'
  # pola = akhiran path, bukan potongan teks: stub '/api/x' tak boleh menjawab '/api/x/rinci'.
  Check (@($konD | Where-Object { $_ -match 'uji-stub /api/x/rinci 500' }).Count -ge 1) 'pola /api/x tidak menjawab /api/x/rinci (500)'
  Check ($d -and @($d.png_segmen).Count -ge 1 -and @($d.png_segmen | Where-Object { -not (Test-Path -LiteralPath $_) }).Count -eq 0) "halaman panjang: segmen gulir tertangkap ($(@($d.png_segmen).Count))"
  Check (@($konD | Where-Object { $_ -match 'uji-stub /api/employee/me 200' }).Count -ge 1) '/api/employee/me 200 walau tak distub'
  Check (@($konD | Where-Object { $_ -match 'galat-uji-sengaja' -and $_ -match 'index\.html' }).Count -ge 1) 'pengecualian tak tertangkap terekam beserta url berkasnya'
  Check ($d -and $d.error_boundary -eq $false -and $d.rute_akhir -eq '/index.html') "index: error_boundary false, rute_akhir /index.html ($($d.rute_akhir))"

  $tak = @($rute | Where-Object { $_.path -eq '/tidak-ada.html' })
  Check ($tak.Count -ge 1 -and @($tak | Where-Object { $_.status_http -ne 404 }).Count -eq 0) "/tidak-ada.html ber-status_http 404 ($(@($tak | ForEach-Object { $_.status_http }) -join ','))"
  $gal = @($rute | Where-Object { $_.path -eq '/galat.html' })
  Check ($gal.Count -ge 1 -and @($gal | Where-Object { $_.error_boundary -ne $true }).Count -eq 0) '/galat.html: error_boundary true (teks "Terjadi Kesalahan")'

  # Chrome yang sudah di-taskkill bisa tetap TERDAFTAR lama saat CPU penuh: penghentian proses di
  # Windows asinkron dan butuh CPU. Terukur 2026-10-18: tanpa beban hilang 0,47 dtk; semua inti
  # sibuk >75 dtk, lalu hilang 0,37 dtk sesudah beban berhenti. Pemeriksaan "tak terdaftar" polos
  # karena itu merah di gerbang pre-push (test-init penuh di mesin yang dipakai sesi lain) dan hijau
  # bila dijalankan sendiri. Yang dicari di sini KEBOCORAN sungguhan: tunggu sebentar, lalu sisa
  # dianggap bocor hanya bila port debug browsernya (dari command line) masih menjawab.
  $sisaChrome = @(); $batasSisa = (Get-Date).AddSeconds(20)
  do { $sisaChrome = @(Proses ('*' + $env:TANGKAP_LAYAR_PROFIL_DASAR + '*')); if ($sisaChrome.Count -eq 0) { break }; Start-Sleep -Milliseconds 500 } while ((Get-Date) -lt $batasSisa)
  $hidup = @()
  foreach ($x in $sisaChrome) {
    $mPort = [regex]::Match([string]$x.CommandLine, '--remote-debugging-port=(\d+)')
    if (-not $mPort.Success) { continue }
    try {
      $null = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 -Uri ("http://127.0.0.1:{0}/json/version" -f $mPort.Groups[1].Value)
      $hidup += $x
    } catch {}
  }
  foreach ($x in $sisaChrome) { Write-Host ("  catatan: pid {0} masih terdaftar, {1}" -f $x.ProcessId, $(if ($hidup -contains $x) { 'port debug MASIH MENJAWAB (bocor)' } else { 'port debug diam (sudah dihentikan, belum selesai berhenti)' })) }
  Check ($hidup.Count -eq 0) "tidak ada Chrome berprofil uji yang masih hidup (port debug menjawab: $($hidup.Count), sedang berhenti: $($sisaChrome.Count - $hidup.Count))"
  Check (@(Proses "*$serve*").Count -eq 0) 'server pnpm start dihentikan sesudah tangkapan'

  # ---- batas waktu server: `start` yang tak pernah listen tak boleh menggantung loop ----
  $wtDiam = Join-Path $tmp 'wt-diam'
  New-Item -ItemType Directory -Force -Path (Join-Path $wtDiam '.next') | Out-Null
  Tulis (Join-Path $wtDiam '.next/BUILD_ID') 'uji'
  Tulis (Join-Path $wtDiam 'package.json') ('{"name":"wt-diam","private":true,"scripts":{"start":"node ' + $diam + '"}}')
  Tulis (Join-Path $wtDiam $diam) 'setInterval(function () {}, 1000);'
  $outDiam = Join-Path $tmp 'keluaran-diam'
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $rc = Jalankan @('-Path', $wtDiam, '-Manifest', $manifest, '-Keluaran', $outDiam, '-BatasServerDetik', '5')
  $sw.Stop()
  $rDiam = $null; $rjD = Join-Path $outDiam 'ringkasan.json'
  if (Test-Path -LiteralPath $rjD) { $rDiam = [IO.File]::ReadAllText($rjD, $utf8) | ConvertFrom-Json }
  Check ($rc -eq 0) "batas waktu server: exit 0 (exit $rc)"
  Check ($rDiam -and $rDiam.galat -match 'listen' -and @($rDiam.rute).Count -eq 0) "batas waktu server: galat menyebut listen, rute kosong ($($rDiam.galat))"
  Check ($sw.Elapsed.TotalSeconds -lt 45) "batas waktu server: berhenti berbatas ($([int]$sw.Elapsed.TotalSeconds) dtk)"
  Check (@(Proses "*$diam*").Count -eq 0) 'batas waktu server: proses start yang diam dihentikan'

  # ---- node mati di tengah jalan: ringkasan sebagian wajib ber-galat ----
  # Shim node.cmd di depan PATH: hanya pemanggilan tangkap-layar.mjs yang "crash" (menulis ringkasan
  # sebagian lalu exit 3); `pnpm start` (serve-*.mjs) diteruskan ke node asli.
  $nodeAsli = (Get-Command node -CommandType Application | Select-Object -First 1).Source
  $shimDir = Join-Path $tmp 'shim'; New-Item -ItemType Directory -Force -Path $shimDir | Out-Null
  Tulis (Join-Path $shimDir 'sebagian.json') '{"url_dasar":"x","rute":[],"galat":null}'
  Tulis (Join-Path $shimDir 'node.cmd') ("@echo off`r`nif /i `"%~nx1`"==`"tangkap-layar.mjs`" (copy /y `"%~dp0sebagian.json`" `"%~7\ringkasan.json`" >nul & exit /b 3)`r`n`"$nodeAsli`" %*`r`nexit /b %errorlevel%`r`n")
  $pathLama = $env:PATH; $env:PATH = $shimDir + ';' + $pathLama
  $outC = Join-Path $tmp 'keluaran-crash'
  try { $rc = Jalankan @('-Path', $wt, '-Manifest', $manifest, '-Keluaran', $outC) } finally { $env:PATH = $pathLama }
  $rCrash = $null; $rjC = Join-Path $outC 'ringkasan.json'
  if (Test-Path -LiteralPath $rjC) { $rCrash = [IO.File]::ReadAllText($rjC, $utf8) | ConvertFrom-Json }
  Check ($rc -eq 0 -and $rCrash -and $rCrash.galat -match 'berhenti \(exit 3\), ringkasan sebagian') "node crash: exit 0, galat ringkasan sebagian (exit $rc; $($rCrash.galat))"

  # ---- tanpa build ----
  $wtKosong = Join-Path $tmp 'wt-tanpa-build'
  New-Item -ItemType Directory -Force -Path $wtKosong | Out-Null
  $outK = Join-Path $tmp 'keluaran-tanpa-build'
  $rc = Jalankan @('-Path', $wtKosong, '-Manifest', $manifest, '-Keluaran', $outK)
  $rK = $null; $rjK = Join-Path $outK 'ringkasan.json'
  if (Test-Path -LiteralPath $rjK) { $rK = [IO.File]::ReadAllText($rjK, $utf8) | ConvertFrom-Json }
  Check ($rc -eq 0 -and $rK -and $rK.galat -match 'build tidak ada') "tanpa .next: exit 0, galat 'build tidak ada' ($($rK.galat))"
}
finally {
  foreach ($pola in @('*' + $tmp + '*', "*$serve*", "*$diam*")) {
    Proses $pola | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop } catch {} }
  }
  Remove-Item Env:TANGKAP_LAYAR_PROFIL_DASAR -ErrorAction SilentlyContinue
  for ($i = 0; $i -lt 5 -and (Test-Path -LiteralPath $tmp); $i++) {
    try { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction Stop } catch { Start-Sleep -Milliseconds 500 }
  }
}
if ($fail -gt 0) { Write-Host "$fail gagal"; exit 1 } else { Write-Host 'Semua lulus'; exit 0 }
