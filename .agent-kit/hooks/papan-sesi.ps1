# papan-sesi.ps1 — papan sesi: tabel ke stdout; HTML-nya dibangkitkan dashboard.ps1 (satu penulis UI).
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

$briefs = @(Get-ChildItem (Join-Path $ws '.task-plans\briefs') -Filter *.md -File)
$judge = @(Get-ChildItem (Join-Path $ws '.task-plans\judge') -Filter *.json -File | Where-Object { $_.Name -match '-\d+\.json$' -and $_.LastWriteTime -gt (Get-Date).AddDays(-7) })
$jLolos = 0; $jGagal = 0
foreach ($j in $judge) { $o = Read-Sesi $j.FullName; if ($o) { if ($o.lolos -eq $true) { $jLolos++ } else { $jGagal++ } } }
$nAktif = @($baris | Where-Object { $_.keadaan -eq 'AKTIF' }).Count
$nBasi = @($baris | Where-Object { $_.keadaan -eq 'BASI' }).Count
$nSelesai24 = @($baris | Where-Object { $_.keadaan -eq 'selesai' -and $_.senyap -match '^\d+[mj]$' }).Count

Write-Host ("PAPAN SESI  {0} WIB   aktif {1} | basi(>{2}j) {3} | selesai 24j {4} | brief {5} | judge 7h lolos {6} / gagal {7}" -f (Wib $now.ToString('o')), $nAktif, $JamBasi, $nBasi, $nSelesai24, $briefs.Count, $jLolos, $jGagal)
if ($baris.Count -eq 0) { Write-Host 'Belum ada sesi terdaftar. Hook SessionStart menulisnya; pastikan kit >= 1.15.0 sudah di-init dan sesi di-restart.' }
else { $baris | Select-Object keadaan, sesi, tahap, task, branch, worktree, terakhir, senyap | Format-Table -AutoSize | Out-String -Width 200 | Write-Host }

if ($TanpaHtml) { exit 0 }
# HTML: satu penulis UI (dashboard.template.html lewat dashboard.ps1); di sini pakai cache PR supaya cepat
& (Join-Path $PSScriptRoot 'dashboard.ps1') -Workspace $ws -TanpaGh | Out-Null
Write-Host ("HTML: {0}  (PR dari cache; /dashboard untuk menarik gh terbaru)" -f (Join-Path $ws '.task-plans\dashboard.html'))
exit 0
