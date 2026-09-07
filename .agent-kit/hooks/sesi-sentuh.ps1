# sesi-sentuh.ps1 — UserPromptSubmit: perbarui `terakhir`, tahap (dari slash command), task.
# TIDAK PERNAH memblokir: selalu exit 0. Gagal menulis hanya berarti papan kurang segar.
$ErrorActionPreference = 'SilentlyContinue'
. (Join-Path $PSScriptRoot 'sesi-lib.ps1')

$in = Get-HookInput
if (-not $in -or -not $in.session_id) { exit 0 }
$ws = Get-WorkspaceRoot $in
$id = [string]$in.session_id
$p = Get-SesiPath $ws $id
$s = Read-Sesi $p
if ($null -eq $s) { $s = New-Sesi $id $ws }   # sesi lahir sebelum kit ini terpasang

$tahapLama = [string]$s.tahap
Set-SesiField $s 'terakhir' (Get-WaktuUtc)
Set-SesiField $s 'status' 'aktif'

$prompt = [string]$in.prompt
# Tahap hanya berubah bila prompt diawali slash command yang dikenal. Prompt biasa tidak
# mengubah tahap: yang dicatat adalah tahap terakhir yang dimasuki, bukan isi obrolan.
$dikenal = 'start-task|plan|implement|review|sync-docs|wrap|analisa-kebutuhan|brief|kerjakan|judge|supervise|ekstrak-skill|papan-sesi'
if ($prompt -match ('^\s*/(' + $dikenal + ')\b\s*(.*)$')) {
  $tahap = $Matches[1]; $arg = $Matches[2]
  Set-SesiField $s 'tahap' $tahap
  if (($tahap -in @('start-task','kerjakan','brief','analisa-kebutuhan')) -and $arg) {
    $arg = ($arg -replace '\s+', ' ').Trim()
    if ($arg.Length -gt 80) { $arg = $arg.Substring(0, 80) }
    Set-SesiField $s 'task' $arg
  }
}
# Kirim ke papan tim hanya bila tahap berubah atau sudah 5 menit sejak kiriman terakhir:
# hook ini berjalan tiap prompt, dan jaringan yang mati tidak boleh membuat tiap prompt menunggu.
$kirim = ([string]$s.tahap -ne $tahapLama) -or (-not $s.terkirim)
if (-not $kirim) {
  try { $t = [DateTime]::Parse([string]$s.terkirim, $null, [Globalization.DateTimeStyles]::RoundtripKind).ToUniversalTime(); $kirim = (((Get-Date).ToUniversalTime() - $t).TotalMinutes -ge 5) } catch { $kirim = $true }
}
if ($kirim) { Send-SesiLoop $PSScriptRoot 'sesi.sentuh' $s }
Write-Sesi $p $s
exit 0
