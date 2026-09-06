# sesi-selesai.ps1 — SessionEnd: tandai sesi selesai di papan. Selalu exit 0.
$ErrorActionPreference = 'SilentlyContinue'
. (Join-Path $PSScriptRoot 'sesi-lib.ps1')

$in = Get-HookInput
if (-not $in -or -not $in.session_id) { exit 0 }
$ws = Get-WorkspaceRoot $in
$p = Get-SesiPath $ws ([string]$in.session_id)
$s = Read-Sesi $p
if ($null -eq $s) { exit 0 }   # tak pernah terdaftar; tak ada yang perlu ditutup
$now = Get-WaktuUtc
Set-SesiField $s 'terakhir' $now
Set-SesiField $s 'selesai' $now
Set-SesiField $s 'status' 'selesai'
Write-Sesi $p $s
exit 0
