# papan-sesi.ps1 — papan sesi: tabel ke stdout + HTML statis ke .task-plans/papan-sesi.html.
# Berkas, bukan layanan: papan yang menuntut layanan hidup ikut mati saat keadaan kacau (ADR 0077 §5).
# BUKAN pengganti Papan Aktivitas Developer (peristiwa GitHub); ini mencatat pekerjaan yang
# sedang berjalan dan belum menghasilkan peristiwa apa pun.
param(
  [string]$Workspace = (Get-Location).Path,
  [int]$JamBasi = 24,
  [switch]$TanpaHtml,
  [switch]$Bersihkan7Hari
)
$ErrorActionPreference = 'SilentlyContinue'
. (Join-Path $PSScriptRoot 'sesi-lib.ps1')

$ws = (Resolve-Path $Workspace).Path
$now = (Get-Date).ToUniversalTime()
try { $tzWib = [TimeZoneInfo]::FindSystemTimeZoneById('SE Asia Standard Time') } catch { $tzWib = [TimeZoneInfo]::Utc }
function Wib([string]$iso) { if (-not $iso) { return '' }; try { $d = [DateTime]::Parse($iso, $null, [Globalization.DateTimeStyles]::RoundtripKind).ToUniversalTime(); return [TimeZoneInfo]::ConvertTimeFromUtc($d, $tzWib).ToString('dd MMM HH:mm') } catch { return $iso } }
function Umur([string]$iso) { if (-not $iso) { return '' }; try { $d = [DateTime]::Parse($iso, $null, [Globalization.DateTimeStyles]::RoundtripKind).ToUniversalTime(); $ts = $now - $d; if ($ts.TotalMinutes -lt 60) { return ('{0}m' -f [int]$ts.TotalMinutes) } elseif ($ts.TotalHours -lt 48) { return ('{0}j' -f [int]$ts.TotalHours) } else { return ('{0}h' -f [int]$ts.TotalDays) } } catch { return '' } }

if ($Bersihkan7Hari) {
  $n = 0
  foreach ($f in Get-ChildItem (Get-SesiDir $ws) -Filter *.json -File) {
    $s = Read-Sesi $f.FullName
    if ($s -and $s.status -eq 'selesai' -and $s.terakhir) {
      $d = [DateTime]::Parse([string]$s.terakhir, $null, [Globalization.DateTimeStyles]::RoundtripKind).ToUniversalTime()
      if (($now - $d).TotalDays -gt 7) { Remove-Item $f.FullName -Force; $n++ }
    }
  }
  Write-Host "Dibersihkan: $n berkas sesi selesai > 7 hari"
}

$sesi = @(Get-SemuaSesi $ws)
$baris = @()
foreach ($s in $sesi) {
  $status = [string]$s.status
  $basi = $false
  if ($status -eq 'aktif' -and $s.terakhir) {
    try { $d = [DateTime]::Parse([string]$s.terakhir, $null, [Globalization.DateTimeStyles]::RoundtripKind).ToUniversalTime(); $basi = (($now - $d).TotalHours -gt $JamBasi) } catch {}
  }
  $baris += [pscustomobject]@{
    keadaan = if ($basi) { 'BASI' } elseif ($status -eq 'aktif') { 'AKTIF' } else { 'selesai' }
    sesi = ([string]$s.session_id).Substring(0, [math]::Min(8, ([string]$s.session_id).Length))
    tahap = [string]$s.tahap; task = [string]$s.task
    worktree = [string]$s.worktree; branch = [string]$s.branch
    mulai = Wib $s.mulai; terakhir = Wib $s.terakhir; senyap = Umur $s.terakhir
    _urut = if ($basi) { 1 } elseif ($status -eq 'aktif') { 0 } else { 2 }
    _terakhir = [string]$s.terakhir
  }
}
$baris = @($baris | Sort-Object _urut, @{ Expression = '_terakhir'; Descending = $true })

# brief & judge untuk ubin ringkas
$briefs = @(Get-ChildItem (Join-Path $ws '.task-plans\briefs') -Filter *.md -File)
$judge = @(Get-ChildItem (Join-Path $ws '.task-plans\judge') -Filter *.json -File | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) })
$jLolos = 0; $jGagal = 0
foreach ($j in $judge) { $o = Read-Sesi $j.FullName; if ($o) { if ($o.lolos -eq $true) { $jLolos++ } else { $jGagal++ } } }
$nAktif = @($baris | Where-Object { $_.keadaan -eq 'AKTIF' }).Count
$nBasi = @($baris | Where-Object { $_.keadaan -eq 'BASI' }).Count
$nSelesai24 = @($baris | Where-Object { $_.keadaan -eq 'selesai' -and $_.senyap -match '^\d+[mj]$' }).Count

Write-Host ("PAPAN SESI  {0} WIB   aktif {1} · basi(>{2}j) {3} · selesai 24j {4} · brief {5} · judge 7h lolos {6} / gagal {7}" -f (Wib $now.ToString('o')), $nAktif, $JamBasi, $nBasi, $nSelesai24, $briefs.Count, $jLolos, $jGagal)
if ($baris.Count -eq 0) { Write-Host 'Belum ada sesi terdaftar. Hook SessionStart menulisnya; pastikan kit >= 1.15.0 sudah di-init dan sesi di-restart.' }
else { $baris | Select-Object keadaan, sesi, tahap, task, branch, worktree, terakhir, senyap | Format-Table -AutoSize | Out-String -Width 200 | Write-Host }

if ($TanpaHtml) { exit 0 }
function H([string]$s) { if ($null -eq $s) { return '' }; return [System.Net.WebUtility]::HtmlEncode($s) }
$rows = ($baris | ForEach-Object {
  $cls = switch ($_.keadaan) { 'AKTIF' { 'aktif' } 'BASI' { 'basi' } default { 'selesai' } }
  ('<tr class="{0}"><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td><td>{8}</td></tr>' -f $cls, (H $_.keadaan), (H $_.sesi), (H $_.tahap), (H $_.task), (H $_.branch), (H $_.worktree), (H $_.terakhir), (H $_.senyap))
}) -join "`n"
$html = @"
<!doctype html><html lang="id"><head><meta charset="utf-8"><title>Papan Sesi</title>
<meta http-equiv="refresh" content="60">
<style>
body{background:#0b0f14;color:#c9d1d9;font:13px/1.5 ui-monospace,Consolas,monospace;margin:0;padding:20px}
h1{font-size:14px;letter-spacing:.12em;color:#8b949e;margin:0 0 14px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:18px}
.tile{border:1px solid #21262d;border-radius:6px;padding:10px 12px;background:#0d1117}
.tile b{display:block;font-size:22px;color:#e6edf3}.tile span{font-size:11px;color:#8b949e;letter-spacing:.08em}
.tile.aktif b{color:#3fb950}.tile.basi b{color:#f0883e}.tile.gagal b{color:#f85149}
table{width:100%;border-collapse:collapse}th{text-align:left;color:#8b949e;font-weight:normal;letter-spacing:.08em;font-size:11px;border-bottom:1px solid #21262d;padding:6px}
td{padding:6px;border-bottom:1px solid #161b22;vertical-align:top}tr.aktif td:first-child{color:#3fb950}tr.basi td:first-child{color:#f0883e;font-weight:bold}tr.selesai{color:#6e7681}
.kaki{margin-top:14px;color:#6e7681;font-size:11px}
</style></head><body>
<h1>PAPAN SESI &middot; $(H (Wib $now.ToString('o'))) WIB &middot; dibuat oleh papan-sesi.ps1</h1>
<div class="tiles">
<div class="tile aktif"><b>$nAktif</b><span>AKTIF</span></div>
<div class="tile basi"><b>$nBasi</b><span>BASI &gt; ${JamBasi}J</span></div>
<div class="tile"><b>$nSelesai24</b><span>SELESAI 24J</span></div>
<div class="tile"><b>$($briefs.Count)</b><span>BRIEF</span></div>
<div class="tile"><b>$jLolos</b><span>JUDGE LOLOS 7H</span></div>
<div class="tile gagal"><b>$jGagal</b><span>JUDGE GAGAL 7H</span></div>
</div>
<table><thead><tr><th>KEADAAN</th><th>SESI</th><th>TAHAP</th><th>TASK</th><th>BRANCH</th><th>WORKTREE</th><th>TERAKHIR</th><th>SENYAP</th></tr></thead>
<tbody>$rows</tbody></table>
<div class="kaki">Sesi yang berjalan dan belum menghasilkan PR. Peristiwa GitHub (commit, PR, review) ada di Papan Aktivitas Developer, bukan di sini. Berkas sumber: .task-plans/sesi/*.json. Sesi BASI = aktif tapi tak disentuh &gt; $JamBasi jam; bersihkan yang selesai &gt; 7 hari dengan -Bersihkan7Hari.</div>
</body></html>
"@
$out = Join-Path $ws '.task-plans\papan-sesi.html'
$utf8 = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($out, $html, $utf8)
Write-Host "HTML: $out"
exit 0
