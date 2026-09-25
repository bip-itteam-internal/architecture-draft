# gerbang-lib.ps1 — dipakai (dot-source) oleh gerbang.ps1 dan baseline-test.ps1.
# SATU tempat untuk: deteksi jenis repo, nama repo, berkas tersentuh, dan PENGURAI hasil test
# (vitest --reporter=json, go test -json). Bentuk nama test yang disimpan di baseline dan yang
# dibandingkan gerbang HARUS keluar dari fungsi yang sama; dua salinan berarti baseline dan
# gerbang bisa menyimpang diam-diam dan gerbang menolak yang benar.
#
# Tiap langkah (Invoke-Gerbang / Invoke-GerbangBatas) mengantre di antre-lib.ps1 (kit 1.30.0):
# kunci PER LANGKAH, bukan sepanjang gerbang, supaya sesi lain bisa menyelip di antara tsc dan
# build alih-alih menunggu seluruh gerbang 2 jam. Waktu antre TIDAK masuk durasi_detik maupun batas.
. (Join-Path $PSScriptRoot 'antre-lib.ps1')

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

# Batas waktu (detik). `dart analyze` atas SELURUH repo sudah terbukti menggantung di mesin tim,
# jadi ia dijalankan atas folder tersentuh saja DAN berbatas waktu, terpisah dari `flutter test`.
# Angkanya menjaga GANTUNG, bukan lambat: diukur 2026-09-21 di mybharata-app, `dart analyze lib
# test` selesai 37,2 detik saat sepi. Batas 300 detik sempat KENA sekali ketika mesin sibuk
# menjalankan suite lain, dan gerbang yang kadang merah karena beban akan dimatikan orang.
$script:BatasAnalyze = 600
$script:BatasTestFlutter = 1200

# Lockfile -> pelaksana. URUTAN PENTING: erp-frontend memegang `pnpm-lock.yaml` DAN
# `package-lock.json` sekaligus (diukur 2026-09-21), jadi menebak dari keberadaan salah satunya
# memakai resolver yang salah. Gagalnya bukan "perintah tidak ada", melainkan dependensi berversi
# lain yang tetap jalan. Cermin PM_NODE di gerbang-lib.py; keduanya WAJIB sepakat.
$script:PmNode = @(
  @{ berkas = 'pnpm-lock.yaml';    nama = 'pnpm'; jalan = 'pnpm';     exec = 'pnpm exec' },
  @{ berkas = 'package-lock.json'; nama = 'npm';  jalan = 'npm run';  exec = 'npx --no-install' },
  @{ berkas = 'yarn.lock';         nama = 'yarn'; jalan = 'yarn';     exec = 'yarn' },
  @{ berkas = 'bun.lockb';         nama = 'bun';  jalan = 'bun run';  exec = 'bunx' },
  @{ berkas = 'bun.lock';          nama = 'bun';  jalan = 'bun run';  exec = 'bunx' }
)

# Repo yang memang TIDAK punya suite mesin. Lubang yang disengaja dan diberi nama, supaya ia
# terbaca sebagai keputusan alih-alih kelalaian. Repo KODE tidak boleh masuk sini.
$script:RepoTanpaGerbang = @('architecture-draft')

function Get-PmNode([string]$top) {
  # Pelaksana Node dibaca dari LOCKFILE, tidak pernah ditebak. $null = tak ada lockfile dikenali.
  foreach ($pm in $script:PmNode) { if (Test-Path (Join-Path $top $pm.berkas)) { return $pm } }
  return $null
}

function Get-JenisRepo([string]$top) {
  if (Test-Path (Join-Path $top 'pubspec.yaml')) { return 'flutter' }
  if ((Test-Path (Join-Path $top 'package.json')) -and (Get-PmNode $top)) { return 'node' }
  $svc = Join-Path $top 'services'
  if (Test-Path $svc) {
    $ada = Get-ChildItem $svc -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'go.mod') }
    if ($ada) { return 'go' }
  }
  return 'lain'
}

function Get-PutusanLolos($gerbang, [string]$nama, [string]$jenis) {
  # Nol gerbang BUKAN lulus. Sampai 1.24.0 `lolos` dihitung sebagai "tak ada gerbang yang gagal",
  # dan daftar KOSONG memenuhi syarat itu, sehingga repo yang jenisnya tak dikenali dinyatakan
  # lolos tanpa satu pemeriksaan pun lalu /judge mengalikannya dengan verdict agen seolah lapis
  # mesin sudah bekerja. Diukur 2026-09-21: empat repo lewat begitu.
  #
  # Yang menentukan adalah JENIS repo, bukan jumlah gerbang. Keduanya sama-sama berakhir "nol
  # gerbang", tetapi artinya berlawanan: jenis 'lain' berarti kita TIDAK TAHU cara memeriksanya,
  # sedangkan repo Go yang branch-nya cuma menyentuh README berarti memang tidak ada yang perlu
  # diperiksa. Menolak yang kedua membuat gerbangnya berbunyi untuk pekerjaan yang benar.
  # Gerbang yang BENAR-BENAR berjalan selalu menang. Daftar-izin di bawah hanya menjawab
  # pertanyaan "tidak ada yang berjalan, lalu apa"; ia bukan kekebalan terhadap gerbang merah.
  $g = @($gerbang)
  if ($g.Count -gt 0) {
    return @{ lolos = (@($g | Where-Object { -not $_.lolos }).Count -eq 0); catatan = $null }
  }
  if ($jenis -eq 'lain') {
    if ($script:RepoTanpaGerbang -contains $nama) {
      return @{ lolos = $true; catatan = ("repo '{0}' ada di daftar-izin RepoTanpaGerbang: nol gerbang diterima SADAR karena repo ini tidak punya suite mesin" -f $nama) }
    }
    return @{ lolos = $false; catatan = ("JENIS REPO TIDAK DIKENALI untuk '{0}', jadi tidak ada satu pun gerbang yang bisa dijalankan: itu dihitung GAGAL, bukan lolos. Dua jalan keluar yang sah: tambah cabang jenis repo di gerbang-lib (.ps1 DAN .py), atau masukkan repo ini ke daftar-izin RepoTanpaGerbang dengan alasan tertulis." -f $nama) }
  }
  return @{ lolos = $true; catatan = ("jenis repo '{0}' dikenali, tetapi tidak ada satu pun pemeriksaan yang perlu dijalankan (tidak ada yang tersentuh, atau dilewati lewat flag). Lolos ini TIDAK membuktikan apa pun tentang kode." -f $jenis) }
}

function Get-GerbangAlat([string[]]$alat) {
  # Alat yang tidak terpasang menghasilkan gerbang GAGAL, bukan gerbang yang lenyap.
  $hilang = @($alat | Where-Object { -not (Get-Command $_ -ErrorAction SilentlyContinue) })
  if ($hilang.Count -eq 0) { return $null }
  return [pscustomobject]@{
    nama = 'alat'; lolos = $false; exit = 127; durasi_detik = 0.0
    ekor = @(("alat tidak ada di PATH: {0}. Gerbang GAGAL, bukan dilewati: alat yang tak terpasang tidak boleh membuat pemeriksaannya ikut hilang." -f ($hilang -join ', ')))
    semua = @()
  }
}

$script:BatasFolderDart = 20

function Get-FolderDart([string[]]$berkas, [int]$batas = 0) {
  # `dart analyze` seluruh repo menggantung; yang dianalisis cuma folder yang tersentuh.
  # `terpotong` WAJIB diteruskan sebagai catatan: pemotongan diam-diam berarti sebagian
  # perubahan tak dianalisis sementara gerbangnya tetap hijau, persis kelas kegagalan yang
  # sedang ditutup rilis ini.
  # Folder yang sudah TERCAKUP induknya dibuang: `dart analyze` menganalisis satu folder secara
  # rekursif, jadi mengirim `lib` bersama `lib/src/core/api` menganalisis subpohon yang sama
  # berkali-kali tanpa menambah satu pun pemeriksaan. Diukur di mybharata-app: 21 folder jadi 1.
  if ($batas -le 0) { $batas = $script:BatasFolderDart }
  $d = @($berkas | Where-Object { $_ -like '*.dart' } | ForEach-Object {
    $p = Split-Path $_ -Parent
    if ($p) { $p -replace '\\', '/' } else { '.' }
  } | Sort-Object -Unique)
  $akar = @()
  foreach ($x in $d) {
    $tercakup = $false
    foreach ($a in $akar) { if ($x -eq $a -or $x.StartsWith($a + '/')) { $tercakup = $true; break } }
    if (-not $tercakup) { $akar += $x }
  }
  if ($akar.Count -gt $batas) {
    # Terlalu banyak folder daun yang tidak bersarang (mis. 20+ folder di bawah `test/`).
    # Diruntuhkan ke segmen pertama, bukan dipotong: `dart analyze test` mencakup SELURUH
    # anaknya, jadi ini menambah cakupan sekaligus memendekkan baris perintah.
    $akar = @($akar | ForEach-Object { ($_ -split '/')[0] } | Sort-Object -Unique)
  }
  return @{ folder = @($akar | Select-Object -First $batas); terpotong = ($akar.Count -gt $batas) }
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
  $kunci = Enter-Antre ('gerbang ' + $nama + ': ' + $cmd) $dir
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $out = @(); $rc = 1
  try {
    Push-Location $dir
    try { $out = @(Invoke-Expression ($cmd + ' 2>&1') | ForEach-Object { [string]$_ }); $rc = $LASTEXITCODE }
    finally { Pop-Location }
  } catch { $out += [string]$_; $rc = 1 }
  finally { Exit-Antre $kunci }
  $sw.Stop()
  if ($null -eq $rc) { $rc = 0 }
  return [pscustomobject]@{
    nama = $nama; lolos = ($rc -eq 0); exit = $rc
    durasi_detik = [math]::Round($sw.Elapsed.TotalSeconds, 1)
    ekor = @($out | Select-Object -Last 25); semua = $out
  }
}

function Invoke-GerbangBatas([string]$nama, [string]$dir, [string]$cmd, [int]$batasDetik) {
  # Seperti Invoke-Gerbang, tetapi BERBATAS WAKTU. Invoke-Expression tidak bisa dihentikan dari
  # luar, jadi perintahnya dijalankan sebagai proses terpisah. Windows-only, sesuai jalur .ps1.
  # Exit code diminta dari cmd sendiri, BUKAN dari objek Process. Dua jebakan sekaligus, keduanya
  # terukur 2026-09-21 pada `dart analyze` mybharata-app: `$p.ExitCode` sesudah WaitForExit(ms)
  # terbaca $null sehingga analyze yang berbunyi "No issues found!" dinilai GAGAL; lalu
  # WaitForExit() tanpa argumen -- obat yang tampak benar -- menunggu pipe keluaran tertutup, dan
  # proses dart sisa menahannya sampai batas 300 detik habis. `/v:on` dipakai supaya !ERRORLEVEL!
  # diperluas SESUDAH perintahnya jalan (%ERRORLEVEL% diperluas saat baris diurai, jadi selalu
  # memberi nilai sebelum-jalan). Konsekuensinya perintah ber-`!` tidak boleh dilewatkan ke sini.
  # Kunci antre diambil SEBELUM stopwatch dan batas mulai: menunggu giliran bukan lewat batas.
  $kunci = Enter-Antre ('gerbang ' + $nama + ': ' + $cmd) $dir
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $outF = [IO.Path]::GetTempFileName(); $errF = [IO.Path]::GetTempFileName()
  $rc = 1; $lewat = $false
  try {
    $p = Start-Process -FilePath $env:ComSpec -ArgumentList @('/v:on', '/d', '/c', ($cmd + ' & echo __RC__!ERRORLEVEL!')) `
      -WorkingDirectory $dir -RedirectStandardOutput $outF -RedirectStandardError $errF -NoNewWindow -PassThru
    if (-not $p.WaitForExit($batasDetik * 1000)) {
      # membunuh cmd.exe saja meninggalkan dart/flutter hidup; /T membereskan seluruh pohonnya
      $lewat = $true; $rc = 124
      & taskkill /T /F /PID $p.Id 2>&1 | Out-Null
    }
  } catch { $rc = 1 }
  finally { Exit-Antre $kunci }
  # dibaca dengan FileShare ReadWrite: proses sisa bisa masih memegang handle berkasnya
  $out = @()
  foreach ($f in @($outF, $errF)) {
    if (Test-Path $f) {
      try {
        $fs = [IO.File]::Open($f, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
        $sr = New-Object IO.StreamReader($fs)
        $out += @($sr.ReadToEnd() -split "`r?`n")
        $sr.Close(); $fs.Close()
      } catch {}
    }
    Remove-Item $f -Force -ErrorAction SilentlyContinue
  }
  if (-not $lewat) {
    $penanda = @($out | Where-Object { $_ -match '^__RC__(\d+)\s*$' }) | Select-Object -Last 1
    if ($penanda -and $penanda -match '^__RC__(\d+)') { $rc = [int]$Matches[1] }
    else { $out += 'PENANDA EXIT CODE TIDAK DITEMUKAN di keluaran cmd; gerbang dianggap GAGAL.' }
  }
  $out = @($out | Where-Object { $_ -notmatch '^__RC__\d+\s*$' })
  if ($lewat) { $out += ("LEWAT BATAS WAKTU {0} detik: proses dihentikan, gerbang dianggap GAGAL." -f $batasDetik) }
  $sw.Stop()
  return [pscustomobject]@{
    nama = $nama; lolos = ($rc -eq 0); exit = $rc
    durasi_detik = [math]::Round($sw.Elapsed.TotalSeconds, 1)
    ekor = @($out | Select-Object -Last 25); semua = $out
  }
}

function Invoke-FlutterTestJson([string]$top) {
  # `flutter test --machine`: satu JSON per baris, dan nama test hanya ada di event testStart.
  $g = Invoke-GerbangBatas 'test' $top 'flutter test --machine' $script:BatasTestFlutter
  $namaTest = @{}; $gagal = @(); $jumlah = 0; $terurai = $false
  $tl = ($top -replace '\\', '/').TrimEnd('/')
  foreach ($line in $g.semua) {
    $l = ([string]$line).Trim()
    if (-not $l.StartsWith('{')) { continue }
    try { $e = $l | ConvertFrom-Json } catch { continue }
    $terurai = $true
    if ($e.type -eq 'testStart') {
      $t = $e.test
      $rel = [string]$t.url; if (-not $rel) { $rel = [string]$t.root_url }
      $rel = $rel -replace '\\', '/'
      if ($rel.StartsWith('file:///')) { $rel = $rel.Substring(8) }
      if ($rel.ToLower().StartsWith($tl.ToLower())) { $rel = $rel.Substring($tl.Length).TrimStart('/') }
      $namaTest[[string]$t.id] = ('{0} > {1}' -f $rel, [string]$t.name)
    }
    elseif ($e.type -eq 'testDone') {
      # `hidden` menandai test sintetis milik runner (memuat berkas), bukan test yang ditulis orang
      if ($e.hidden) { continue }
      $jumlah++
      if ($e.result -ne 'success') {
        $k = [string]$e.testID
        $gagal += $(if ($namaTest.ContainsKey($k)) { $namaTest[$k] } else { "(test $k)" })
      }
    }
  }
  return [pscustomobject]@{ gerbang = $g; jumlah = $jumlah; gagal = @($gagal | Sort-Object -Unique); terurai = $terurai }
}

function Invoke-VitestJson([string]$top, $pm) {
  # exit code vitest TIDAK dipakai sebagai lolos/gagal: yang menentukan adalah kegagalan BARU
  # terhadap baseline, karena `pnpm test` main tidak pernah hijau penuh di sini.
  $tmp = Join-Path $env:TEMP ('vitest-' + [guid]::NewGuid().ToString('N') + '.json')
  $g = Invoke-Gerbang 'test' $top ($pm.exec + ' vitest run --reporter=json --outputFile="' + $tmp + '"')
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
