# gerbang.ps1 — gerbang DETERMINISTIK untuk /judge. Lapisan pertama Judges; agen judge lapisan kedua.
#
# Node   : <pm> tsc, <pm> lint, <pm> build (-TanpaBuild melewatinya, dan itu dicatat di keluaran),
#          test vs baseline (kegagalan BARU terhadap baseline/<repo>.json = gagal). Pelaksana <pm>
#          dibaca dari LOCKFILE (pnpm/npm/yarn/bun), tidak ditebak.
# Go     : go build ./... per services/<x> yang tersentuh (semua bila shared-library tersentuh),
#          go test -json per service tersentuh vs baseline
# Flutter: dart analyze atas folder .dart yang tersentuh (BERBATAS WAKTU, terpisah dari test),
#          lalu flutter test --machine vs baseline
# lain   : TIDAK ADA GERBANG = GAGAL, kecuali repo ada di daftar-izin RepoTanpaGerbang.
#
# Keluaran: JSON ke stdout (+ ke -Keluaran bila diberi). Exit 0 bila seluruh gerbang lolos, 1 bila
# ada yang gagal, 2 bila argumen salah. Baseline yang TIDAK ADA tidak menggagalkan, tetapi dicatat
# keras di keluaran supaya judge dan manusia tahu test tidak dibandingkan dengan apa pun.
#
# ⛔ NOL GERBANG BUKAN LULUS (1.25.0). Sebelumnya `lolos` dihitung sebagai "tak ada gerbang yang
# gagal", dan daftar KOSONG memenuhi syarat itu, sehingga repo yang jenisnya tak dikenali lolos
# tanpa satu pemeriksaan pun. Aturannya kini di Get-PutusanLolos (gerbang-lib.ps1), dan cerminnya
# di gerbang-lib.py; mengubah salah satunya saja membuat jalur mac/linux menyimpang diam-diam.
param(
  [Parameter(Mandatory = $true)][string]$Path,
  [string]$Base = 'origin/main',
  [string]$KitRoot,
  [switch]$TanpaBuild,
  [switch]$TanpaTest,
  [string]$Keluaran
)
$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot 'gerbang-lib.ps1')
if (-not $KitRoot) { $KitRoot = Get-KitRoot $PSScriptRoot }

$top = Get-RepoTop $Path
if (-not $top) { [Console]::Error.WriteLine("Bukan repo git: $Path"); exit 2 }
$nama = Get-NamaRepo $top
$jenis = Get-JenisRepo $top
$commit = git -C $top -c core.fsmonitor=false rev-parse --short HEAD 2>$null
$branch = git -C $top -c core.fsmonitor=false symbolic-ref --short HEAD 2>$null
git -C $top -c core.fsmonitor=false fetch origin --quiet 2>$null
$berkas = Get-BerkasTersentuh $top $Base

$gerbang = @(); $catatan = @()
if ($jenis -eq 'node') {
  $pm = Get-PmNode $top
  $catatan += ("pelaksana Node dari lockfile: {0}" -f $pm.nama)
  $pkg = Get-Content (Join-Path $top 'package.json') -Raw -Encoding UTF8 | ConvertFrom-Json
  foreach ($s in 'tsc', 'lint') {
    if ($pkg.scripts.PSObject.Properties[$s]) { $gerbang += (Invoke-Gerbang $s $top ($pm.jalan + ' ' + $s)) }
    else { $catatan += "skrip '$s' tidak ada di package.json" }
  }
  if ($pkg.scripts.PSObject.Properties['build']) {
    if ($TanpaBuild) { $catatan += 'BUILD DILEWATI atas permintaan (-TanpaBuild); jalankan sebelum merge' }
    else { $gerbang += (Invoke-Gerbang 'build' $top ($pm.jalan + ' build')) }
  }
  if (-not $TanpaTest) {
    $t = Invoke-VitestJson $top $pm
    $bl = Read-Baseline $KitRoot $nama
    $baru = @(); $blGagal = @()
    if ($null -ne $bl) { $blGagal = @($bl.gagal); $baru = @($t.gagal | Where-Object { $blGagal -notcontains $_ }) }
    else { $catatan += ("TIDAK ADA BASELINE untuk '{0}' di {1}\baseline; kegagalan test TIDAK dibandingkan dengan apa pun. Buat dengan baseline-test.ps1." -f $nama, $KitRoot) }
    $lolosTest = if ($null -ne $bl) { ($t.terurai -and $baru.Count -eq 0) } else { $t.terurai }
    $gerbang += [pscustomobject]@{
      nama = 'test'; lolos = $lolosTest; exit = $t.gerbang.exit; durasi_detik = $t.gerbang.durasi_detik
      jumlah_test = $t.jumlah; gagal_total = $t.gagal.Count; gagal_di_baseline = @($t.gagal | Where-Object { $blGagal -contains $_ }).Count
      gagal_baru = $baru; terurai = $t.terurai
      baseline = if ($null -ne $bl) { ('{0} @ {1}' -f $bl.tanggal, $bl.commit) } else { $null }
      ekor = $t.gerbang.ekor
    }
    if (-not $t.terurai) { $catatan += 'keluaran vitest JSON tidak terurai; gerbang test dianggap GAGAL' }
  }
}
elseif ($jenis -eq 'go') {
  $svcs = Get-ServicesTersentuh $top $berkas
  if ($svcs.Count -eq 0) { $catatan += 'tidak ada services/<x> tersentuh: go build/test dilewati' }
  $bl = Read-Baseline $KitRoot $nama
  if ($null -eq $bl -and $svcs.Count -gt 0 -and -not $TanpaTest) { $catatan += ("TIDAK ADA BASELINE untuk '{0}'; kegagalan test TIDAK dibandingkan dengan apa pun." -f $nama) }
  foreach ($s in $svcs) {
    $gerbang += (Invoke-Gerbang ('build:' + $s) (Join-Path $top ('services\' + $s)) 'go build ./...')
    if (-not $TanpaTest) {
      $t = Invoke-GoTestJson $top $s
      $blGagal = if ($null -ne $bl) { @($bl.gagal) } else { @() }
      $baru = if ($null -ne $bl) { @($t.gagal | Where-Object { $blGagal -notcontains $_ }) } else { @() }
      $lolosTest = if ($null -ne $bl) { ($t.terurai -and $baru.Count -eq 0) } else { $t.terurai }
      $gerbang += [pscustomobject]@{
        nama = ('test:' + $s); lolos = $lolosTest; exit = $t.gerbang.exit; durasi_detik = $t.gerbang.durasi_detik
        jumlah_test = $t.jumlah; gagal_total = $t.gagal.Count; gagal_di_baseline = @($t.gagal | Where-Object { $blGagal -contains $_ }).Count
        gagal_baru = $baru; terurai = $t.terurai
        baseline = if ($null -ne $bl) { ('{0} @ {1}' -f $bl.tanggal, $bl.commit) } else { $null }
        ekor = $t.gerbang.ekor
      }
    }
  }
}
elseif ($jenis -eq 'flutter') {
  $alat = Get-GerbangAlat @('dart', 'flutter')
  if ($alat) { $gerbang += $alat }
  else {
    $folder = Get-FolderDart $berkas
    if ($folder.Count -gt 0) { $gerbang += (Invoke-GerbangBatas 'analyze' $top ('dart analyze ' + ($folder -join ' ')) $script:BatasAnalyze) }
    else { $catatan += 'tidak ada berkas .dart tersentuh: dart analyze dilewati' }
    if (-not $TanpaTest) {
      $bl = Read-Baseline $KitRoot $nama
      if ($null -eq $bl) { $catatan += ("TIDAK ADA BASELINE untuk '{0}'; kegagalan test TIDAK dibandingkan dengan apa pun." -f $nama) }
      $t = Invoke-FlutterTestJson $top
      $blGagal = if ($null -ne $bl) { @($bl.gagal) } else { @() }
      $baru = if ($null -ne $bl) { @($t.gagal | Where-Object { $blGagal -notcontains $_ }) } else { @() }
      $lolosTest = if ($null -ne $bl) { ($t.terurai -and $baru.Count -eq 0) } else { $t.terurai }
      $gerbang += [pscustomobject]@{
        nama = 'test'; lolos = $lolosTest; exit = $t.gerbang.exit; durasi_detik = $t.gerbang.durasi_detik
        jumlah_test = $t.jumlah; gagal_total = $t.gagal.Count; gagal_di_baseline = @($t.gagal | Where-Object { $blGagal -contains $_ }).Count
        gagal_baru = $baru; terurai = $t.terurai
        baseline = if ($null -ne $bl) { ('{0} @ {1}' -f $bl.tanggal, $bl.commit) } else { $null }
        ekor = $t.gerbang.ekor
      }
      if (-not $t.terurai) { $catatan += 'keluaran flutter test --machine tidak terurai; gerbang test dianggap GAGAL' }
    }
  }
}
else {
  if (Test-Path (Join-Path $top 'package.json')) {
    $catatan += 'package.json ada tetapi tidak ada lockfile yang dikenali (pnpm/npm/yarn/bun): pelaksana tidak bisa dibaca, dan menebaknya memakai resolver yang salah'
  }
  $catatan += "jenis repo 'lain': tidak ada gerbang deterministik"
}

# buang `semua` (besar) dari keluaran; ekor cukup untuk manusia
$gerbangKeluar = @($gerbang | ForEach-Object { $o = $_ | Select-Object * -ExcludeProperty semua; $o })
$putusan = Get-PutusanLolos $gerbangKeluar $nama $jenis
$lolos = $putusan.lolos
if ($putusan.catatan) { $catatan += $putusan.catatan }
$hasil = [pscustomobject]@{
  repo = $nama; jenis = $jenis; path = $top; branch = $branch; commit = $commit; base = $Base
  waktu = (Get-Date).ToUniversalTime().ToString('o')
  berkas_tersentuh = $berkas
  gerbang = $gerbangKeluar
  catatan = $catatan
  lolos = $lolos
}
$json = $hasil | ConvertTo-Json -Depth 8
if ($Keluaran) { Write-JsonUtf8 $Keluaran $hasil }
Write-Output $json
if ($lolos) { exit 0 } else { exit 1 }
