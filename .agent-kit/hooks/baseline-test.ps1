# baseline-test.ps1 — ukur test yang MEMANG merah di sebuah repo, simpan bertanggal + ber-commit
# ke <kit>/baseline/<repo>.json. Dipakai gerbang.ps1 untuk membedakan kegagalan BARU dari yang lama.
#
# Kenapa ada: `pnpm test` erp-frontend tidak pernah hijau penuh di main, jadi tanpa baseline test
# tidak bisa masuk gerbang mana pun (ANALISA T13). Ukur di checkout origin/main yang BERSIH
# (mis. worktree ~/wt/fe-baseline), bukan di branch fitur, supaya baseline-nya milik main.
# Angka nol kegagalan diperlakukan sebagai PERTANYAAN: skrip menolak menulis baseline bila
# keluaran test tidak terurai, karena "0 gagal" dari pengurai yang mati terlihat sama dengan hijau.
param(
  [Parameter(Mandatory = $true)][string]$Path,
  [string]$KitRoot,
  [string[]]$Services
)
$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot 'gerbang-lib.ps1')
if (-not $KitRoot) { $KitRoot = Get-KitRoot $PSScriptRoot }

$top = Get-RepoTop $Path
if (-not $top) { [Console]::Error.WriteLine("Bukan repo git: $Path"); exit 2 }
$nama = Get-NamaRepo $top
$jenis = Get-JenisRepo $top
$commit = git -C $top -c core.fsmonitor=false rev-parse --short HEAD 2>$null
$sw = [Diagnostics.Stopwatch]::StartNew()
$gagal = @(); $jumlah = 0; $terurai = $false; $catatan = @()

if ($jenis -eq 'node') {
  $t = Invoke-VitestJson $top
  $gagal = $t.gagal; $jumlah = $t.jumlah; $terurai = $t.terurai
}
elseif ($jenis -eq 'go') {
  $svcs = if ($Services) { $Services } else { Get-SemuaService $top }
  foreach ($s in $svcs) {
    Write-Host ("  go test services/{0} ..." -f $s)
    $t = Invoke-GoTestJson $top $s
    if ($t.terurai) { $terurai = $true }
    $gagal += $t.gagal; $jumlah += $t.jumlah
    if (-not $t.terurai) { $catatan += ("services/{0}: keluaran go test tidak terurai (mungkin gagal build seluruhnya)" -f $s) }
  }
}
else { [Console]::Error.WriteLine("Jenis repo 'lain', tidak ada suite test: $top"); exit 2 }
$sw.Stop()

if (-not $terurai) {
  [Console]::Error.WriteLine('Keluaran test tidak terurai sama sekali. Baseline TIDAK ditulis: "0 gagal" dari pengurai yang mati bukan baseline.')
  exit 3
}
$baseline = [pscustomobject]@{
  repo = $nama; jenis = $jenis; tanggal = (Get-Date).ToUniversalTime().ToString('o'); commit = $commit
  path_ukur = $top; jumlah_test = $jumlah; jumlah_gagal = $gagal.Count
  gagal = @($gagal | Sort-Object -Unique); durasi_detik = [math]::Round($sw.Elapsed.TotalSeconds, 1)
  catatan = $catatan
  cara_ukur_ulang = ('baseline-test.ps1 -Path <checkout origin/main bersih> ; jangan di branch fitur')
}
$out = Join-Path $KitRoot ('baseline\' + $nama + '.json')
Write-JsonUtf8 $out $baseline
Write-Host ("Baseline {0} @ {1}: {2} test, {3} gagal, {4} detik -> {5}" -f $nama, $commit, $jumlah, $gagal.Count, $baseline.durasi_detik, $out)
if ($gagal.Count -eq 0) { Write-Host 'PERHATIAN: nol kegagalan. Pastikan suite benar-benar berjalan (jumlah_test masuk akal?) sebelum mempercayainya.' }
exit 0
