# kantor-agent.ps1 — launcher Windows untuk /kantor-agent.
#
# Logika data SATU tempat: kantor-agent.py (penulis). UI SATU tempat: kantor-agent.template.html.
# Skrip ini hanya mencari Python, menjaga penulis tidak ganda, menyalin template ke .task-plans,
# menjalankan penulis terlepas, dan membuka halaman. Berkas, bukan layanan (ADR 0077 §5): halaman
# membaca .task-plans/kantor-agent-data.js, dan penulis yang mati terlihat sebagai data basi.
#
# Kenapa penulisnya Python, bukan PowerShell: ConvertFrom-Json PS 5.1 atas ekor transkrip terukur tak
# selesai dalam 180 detik untuk profil yang diselesaikan Python dalam 0,045 detik (2026-09-15).
# Urutan interpreter mengikuti commands/index-vault.md: venv vault dulu, karena `python` global di
# banyak mesin tim menunjuk ke venv proyek lain (sengaja tidak dipakai).
#
# Satu penulis per workspace dijaga DUA lapis: launcher memeriksa PID + command line, dan penulis sendiri
# memegang kunci berkas (kantor-agent.lock). Dua launcher pada detik yang sama sama-sama lolos cek PID;
# yang kalah rebutan kunci keluar 4, dan launcher-nya menunggu PID pemenangnya tercatat.
#
# pakai: kantor-agent.ps1 [-Workspace WS] [-ProyekDir DIR] [-RegistriDir DIR] [-Sekali] [-Interval 2] [-SepiMenit 60]
#        [-CekSilangDetik 60] [-TanpaBuka] [-Berhenti] [-Python EXE]
param(
  [string]$Workspace = (Get-Location).Path,
  [string]$ProyekDir = (Join-Path $env:USERPROFILE '.claude\projects'),
  [string]$RegistriDir,
  [double]$CekSilangDetik = 60,
  [switch]$Sekali,
  [double]$Interval = 2,
  [double]$SepiMenit = 60,
  [switch]$TanpaBuka,
  [switch]$Berhenti,
  [string]$Python
)
# 'Continue', BUKAN 'Stop': di PS 5.1 baris stderr native command pada jalur SUKSES berubah jadi galat
# terminating di bawah 'Stop' (terbukti mematikan worktree-baru.ps1). Keberhasilan dicek lewat exit code.
$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot 'gerbang-lib.ps1')

$inv = [Globalization.CultureInfo]::InvariantCulture   # kultur id-ID menulis 2,5; Python butuh 2.5
$ws = (Resolve-Path -LiteralPath $Workspace).Path
$keluaran = Join-Path $ws '.task-plans'
$pidFile = Join-Path $keluaran 'kantor-agent.pid'
$html = Join-Path $keluaran 'kantor-agent.html'
$log = Join-Path $keluaran 'kantor-agent.log'
$penulis = Join-Path $PSScriptRoot 'kantor-agent.py'
$template = Join-Path $PSScriptRoot 'kantor-agent.template.html'
$venv = Join-Path (Split-Path -Parent (Get-KitRoot $PSScriptRoot)) 'Tools\.venv\Scripts\python.exe'

function Get-PenulisHidup {
  # PID di berkas bisa basi dan sudah dipakai proses lain: sah hanya bila command line-nya memang kantor-agent.py
  if (-not (Test-Path -LiteralPath $pidFile)) { return $null }
  $id = 0
  if (-not [int]::TryParse(([IO.File]::ReadAllText($pidFile)).Trim(), [ref]$id)) { return $null }
  $p = Get-CimInstance Win32_Process -Filter "ProcessId=$id" -ErrorAction SilentlyContinue
  if ($p -and $p.CommandLine -like '*kantor-agent.py*') { return $p }
  return $null
}

if ($Berhenti) {
  $p = Get-PenulisHidup
  if ($p) {
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Host ("Penulis Kantor Agent (pid {0}) dihentikan." -f $p.ProcessId)
  } else {
    Write-Host 'Tidak ada penulis Kantor Agent yang hidup.'
  }
  if (Test-Path -LiteralPath $pidFile) { [IO.File]::Delete($pidFile) }   # penulis yang dibunuh tak sempat menghapusnya
  exit 0
}

function Find-Python {
  if ($Python) { if (Test-Path -LiteralPath $Python) { return , @($Python) } else { return $null } }
  if (Test-Path -LiteralPath $venv) { return , @($venv) }
  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) { return , @($py.Source, '-3') }
  $p3 = Get-Command python3 -ErrorAction SilentlyContinue
  if ($p3 -and $p3.Source -notmatch 'WindowsApps') { return , @($p3.Source) }   # stub Microsoft Store bukan Python
  return $null
}
$pyCmd = Find-Python
if (-not $pyCmd) {
  $dicari = if ($Python) { "-Python $Python (berkasnya tidak ada)" } else { "$venv, py -3, python3" }
  [Console]::Error.WriteLine("kantor-agent: butuh Python 3.8+. Dicari: $dicari")
  exit 2
}
$pyExe = $pyCmd[0]
$pyArgs = @($pyCmd | Select-Object -Skip 1)

if (-not (Test-Path -LiteralPath $template)) { [Console]::Error.WriteLine("kantor-agent: template tidak ada: $template"); exit 2 }
New-Item -ItemType Directory -Force -Path $keluaran | Out-Null
Copy-Item -LiteralPath $template -Destination $html -Force
$dasar = @($pyArgs) + @($penulis, '--workspace', $ws, '--proyek-dir', $ProyekDir)
if ($RegistriDir) { $dasar += @('--registri-dir', $RegistriDir) }   # kosong = registri bawaan ~/.claude/sessions

if ($Sekali) {
  & $pyExe @dasar --sekali
  $rc = $LASTEXITCODE
  if ($rc -ne 0) { [Console]::Error.WriteLine("kantor-agent: penulis gagal (exit $rc)"); exit $rc }
  Write-Host ("Kantor Agent: {0}" -f $html)
  if (-not $TanpaBuka) { Start-Process -FilePath $html }
  exit 0
}

$hidup = Get-PenulisHidup
if ($hidup) {
  Write-Host ("Penulis Kantor Agent sudah jalan (pid {0}); tidak menyalakan yang kedua." -f $hidup.ProcessId)
} else {
  # Start-Process menggabung argumen tanpa kutip: path berspasi (C:\Data utama\...) wajib dikutip sendiri
  $argLoop = @($dasar + @('--loop', $Interval.ToString($inv), '--sepi-menit', $SepiMenit.ToString($inv),
      '--cek-silang-detik', $CekSilangDetik.ToString($inv), '--log', $log)) |
    ForEach-Object { if ("$_" -match '\s') { '"' + $_ + '"' } else { "$_" } }
  # tanpa -RedirectStandard*: penulis mencatat sendiri ke --log, jadi tak ada handle yang diwariskan ke proses lepas
  $p = Start-Process -FilePath $pyExe -ArgumentList $argLoop -WindowStyle Hidden -PassThru
  $null = $p.Handle   # tanpa ini ExitCode bisa kosong sesudah proses selesai (PS 5.1)
  $sw = [Diagnostics.Stopwatch]::StartNew()
  while (-not (Get-PenulisHidup) -and -not $p.HasExited -and $sw.Elapsed.TotalSeconds -lt 30) { Start-Sleep -Milliseconds 300 }
  $hidup = Get-PenulisHidup
  if (-not $hidup -and $p.HasExited -and $p.ExitCode -eq 4) {
    # exit 4 = kunci dipegang penulis lain yang menyala di saat yang sama: tunggu PID pemenangnya tercatat
    while (-not ($hidup = Get-PenulisHidup) -and $sw.Elapsed.TotalSeconds -lt 30) { Start-Sleep -Milliseconds 300 }
    if ($hidup) { Write-Host ("Penulis Kantor Agent sudah jalan (pid {0}); tidak menyalakan yang kedua." -f $hidup.ProcessId) }
  } elseif ($hidup) {
    Write-Host ("Penulis Kantor Agent menyala (pid {0}), menulis tiap {1} detik, berhenti sendiri setelah {2} menit tanpa sesi hidup." -f $hidup.ProcessId, $Interval.ToString($inv), $SepiMenit.ToString($inv))
  }
  if (-not $hidup) { [Console]::Error.WriteLine("kantor-agent: penulis tidak menyala dalam 30 detik. Lihat $log"); exit 3 }
}
Write-Host ("Kantor Agent: {0}" -f $html)
Write-Host 'Hentikan: /kantor-agent --berhenti'
if (-not $TanpaBuka) { Start-Process -FilePath $html }
exit 0
