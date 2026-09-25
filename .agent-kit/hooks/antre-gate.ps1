# antre-gate.ps1 - PreToolUse(Bash|PowerShell): MENOLAK run penuh (test/build/tsc/lint) yang tidak
# lewat antre.ps1 (kit 1.30.0). Klasifikasinya satu tempat, Get-KelasPerintah di antre-lib.ps1.
#
# Dipasang init.ps1 di belakang filter `if` per pola, jadi proses ini hanya di-spawn untuk
# perintah yang memuat nama alat berat. Menambah alat yang dikenali Get-KelasPerintah wajib diikuti
# memperluas pola `if` di init.ps1 (fakta yang sama di dua tempat, ditandai di keduanya).
#
# Menolak lewat exit 2 (pola yang sama dengan pre-commit-gate.ps1). Jalan keluar sadar yang
# meninggalkan jejak di transkrip: `$env:AGENTKIT_ANTRE_LEWATI=1;` di perintah yang sama.
$ErrorActionPreference = 'SilentlyContinue'
if (-not [Console]::IsInputRedirected) { exit 0 }
$raw = [Console]::In.ReadToEnd()
try { $data = $raw | ConvertFrom-Json } catch { exit 0 }
$cmd = [string]$data.tool_input.command
if (-not $cmd) { exit 0 }
# Perintah yang SUDAH lewat antre.ps1 tidak dikecualikan lewat pencocokan teks (itu meloloskan
# `Get-Content antre.ps1; pnpm build`): segmennya berawal `&`/`powershell` + path antre, dan
# Get-KelasPerintah membacanya sebagai 'bukan' karena alat berat tak berada di posisi perintah.
if ($cmd -match 'AGENTKIT_ANTRE_LEWATI\s*=\s*1') { exit 0 }
. (Join-Path $PSScriptRoot 'antre-lib.ps1')
if ((Get-KelasPerintah $cmd) -ne 'penuh') { exit 0 }

$antre = Join-Path $PSScriptRoot 'antre.ps1'
$ringkas = if ($cmd.Length -gt 120) { $cmd.Substring(0, 120) + '...' } else { $cmd }
$msg = "DITOLAK antrean agent-kit: perintah ini run PENUH (test/build/tsc/lint) dan berebut CPU dengan sesi lain bila dijalankan langsung: $ringkas`n" +
       "Jalankan lewat antrean, WAJIB dengan run_in_background: true (menunggu giliran bisa melampaui batas 10 menit tool):`n" +
       "  PowerShell: & `"$antre`" -- <perintah yang sama>`n" +
       "  Bash:       powershell -NoProfile -File `"$antre`" -- <perintah yang sama>`n" +
       "Test tertarget (satu berkas/paket) tidak perlu antre. Lewati sadar (tercatat di transkrip): awali dengan `$env:AGENTKIT_ANTRE_LEWATI=1;"
[Console]::Error.WriteLine($msg)
exit 2
