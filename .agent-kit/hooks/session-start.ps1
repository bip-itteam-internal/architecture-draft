# session-start.ps1 — info flow + cek versi kit + cek staleness vault + daftarkan sesi ke papan
$ErrorActionPreference = 'SilentlyContinue'
. (Join-Path $PSScriptRoot 'sesi-lib.ps1')

$in = Get-HookInput
$ws = Get-WorkspaceRoot $in
$vault = Join-Path $ws 'architecture-draft'
$kitVerFile = Join-Path $vault '.agent-kit/VERSION'
$instFile   = Join-Path $ws '.claude/.kit-version'

$lines = @(
  'Flow wajib: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap',
  'Opsional sebelum flow: /analisa-kebutuhan <kebutuhan manajemen> (mentah -> ADR + dok + daftar task)',
  'Loop otonom: /brief <masalah> -> /kerjakan <brief> (judge otomatis, berhenti di PR). Sesi lain: /papan-sesi. Skill: /ekstrak-skill, /supervise'
)

if (Test-Path $kitVerFile) {
  $kitVer = (Get-Content $kitVerFile -Raw).Trim()
  $instVer = if (Test-Path $instFile) { (Get-Content $instFile -Raw).Trim() } else { 'unknown' }
  if ($kitVer -ne $instVer) {
    $lines += "Update agent-kit tersedia (terpasang: $instVer, terbaru: $kitVer). Jalankan ulang architecture-draft/.agent-kit/init.ps1 lalu restart sesi."
  } else {
    $lines += "Agent-kit v$instVer (terkini)."
  }
}

git -C $vault fetch --quiet 2>$null
$localRev  = (git -C $vault rev-parse '@' 2>$null)
$remoteRev = (git -C $vault rev-parse '@{u}' 2>$null)
$baseRev   = (git -C $vault merge-base '@' '@{u}' 2>$null)
# "ketinggalan" hanya bila local = merge-base & beda dari remote (remote di depan);
# kalau local ahead/diverged jangan suruh pull
if ($localRev -and $remoteRev -and $baseRev -and ($localRev -ne $remoteRev) -and ($localRev -eq $baseRev)) {
  $lines += 'architecture-draft ketinggalan dari remote. Jalankan: git -C architecture-draft pull'
}

# Daftarkan sesi ke papan. Sesi yang di-resume mempertahankan `mulai`-nya.
if ($in -and $in.session_id) {
  $id = [string]$in.session_id
  $p = Get-SesiPath $ws $id
  $s = Read-Sesi $p
  if ($null -eq $s) { $s = New-Sesi $id $ws }
  else {
    Set-SesiField $s 'terakhir' (Get-WaktuUtc)
    Set-SesiField $s 'status' 'aktif'
    Set-SesiField $s 'selesai' $null
  }
  Send-SesiLoop $PSScriptRoot 'sesi.mulai' $s
  Write-Sesi $p $s
  # /kerjakan dan /ekstrak-skill membaca id sesi dari baris ini; hook input tidak terlihat model
  $lines += "Sesi ini: $id (papan: .task-plans/sesi/$id.json)"
  # Kegagalan kirim ke papan tim tidak boleh senyap: sesudah 3 kali beruntun, katakan di sini.
  $gagalFile = Join-Path $env:USERPROFILE '.agent-kit\loop-ingest.gagal'
  if (Test-Path $gagalFile) {
    try { $g = Get-Content $gagalFile -Raw | ConvertFrom-Json; if ($g.beruntun -ge 3) { $lines += "loop-ingest: $($g.beruntun) kegagalan beruntun mengirim ke papan tim (kode $($g.kode)); sesi ini TIDAK tampil di papan. Periksa ~/.agent-kit/loop-ingest.json" } } catch {}
  }
}

$ctx = ($lines -join "`n")
@{ hookSpecificOutput = @{ hookEventName = 'SessionStart'; additionalContext = $ctx } } |
  ConvertTo-Json -Compress -Depth 5
exit 0
