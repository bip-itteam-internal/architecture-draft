# sesi-lib.ps1 — dipakai (dot-source) oleh hook sesi dan papan-sesi.
# SATU tempat untuk bentuk berkas sesi `.task-plans/sesi/<session_id>.json`; jangan disalin.
#
# Bentuk:
#   session_id, mulai, terakhir, selesai (null bila aktif), status (aktif|selesai),
#   cwd, tahap (mulai|start-task|plan|implement|review|sync-docs|wrap|brief|kerjakan|judge|...),
#   task (80 char pertama argumen /start-task, /kerjakan, /brief), worktree, branch
# Semua waktu UTC ISO-8601 (round-trip 'o'). Papan yang menampilkan mengonversi ke WIB.

function Get-HookInput {
  # Claude Code selalu memberi stdin JSON. Bila dijalankan manusia tanpa stdin, jangan
  # memblokir menunggu EOF: kembalikan $null.
  if (-not [Console]::IsInputRedirected) { return $null }
  $raw = [Console]::In.ReadToEnd()
  if (-not $raw) { return $null }
  try { return ($raw | ConvertFrom-Json) } catch { return $null }
}

function Get-WorkspaceRoot($hookInput) {
  if ($hookInput -and $hookInput.cwd) { return [string]$hookInput.cwd }
  return $PWD.Path
}

function Get-SesiDir([string]$ws) { return (Join-Path $ws '.task-plans\sesi') }
function Get-SesiPath([string]$ws, [string]$id) { return (Join-Path (Get-SesiDir $ws) ($id + '.json')) }

function Get-WaktuUtc { return (Get-Date).ToUniversalTime().ToString('o') }

function Read-Sesi([string]$path) {
  if (-not (Test-Path $path)) { return $null }
  try { return (Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json) } catch { return $null }
}

function New-Sesi([string]$id, [string]$ws) {
  $now = Get-WaktuUtc
  return [pscustomobject]@{
    session_id = $id; mulai = $now; terakhir = $now; selesai = $null; status = 'aktif'
    cwd = $ws; tahap = 'mulai'; task = ''; worktree = ''; branch = ''
    # waktu terakhir sesi ini dikirim ke papan tim (loop-kirim); dipakai sesi-sentuh untuk throttle
    terkirim = $null
  }
}

# Kirim peristiwa sesi ke papan tim (best-effort, opt-in per mesin). Judul/teks task TIDAK ikut.
function Send-SesiLoop([string]$hookDir, [string]$jenis, $sesi) {
  try {
    $data = [ordered]@{
      id = [string]$sesi.session_id; tahap = [string]$sesi.tahap; status = [string]$sesi.status
      mulai = $sesi.mulai; terakhir = $sesi.terakhir; selesai = $sesi.selesai
    } | ConvertTo-Json -Compress
    & (Join-Path $hookDir 'loop-kirim.ps1') -Jenis $jenis -Data $data | Out-Null
    Set-SesiField $sesi 'terkirim' (Get-WaktuUtc)
  } catch {}
}

function Set-SesiField($sesi, [string]$name, $value) {
  if ($sesi.PSObject.Properties[$name]) { $sesi.$name = $value }
  else { $sesi | Add-Member -NotePropertyName $name -NotePropertyValue $value }
}

function Write-Sesi([string]$path, $sesi) {
  $dir = Split-Path $path -Parent
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  $utf8 = New-Object System.Text.UTF8Encoding($false)
  [IO.File]::WriteAllText($path, ($sesi | ConvertTo-Json -Depth 4), $utf8)
}

function Get-SemuaSesi([string]$ws) {
  $dir = Get-SesiDir $ws
  if (-not (Test-Path $dir)) { return @() }
  $hasil = @()
  foreach ($f in Get-ChildItem $dir -Filter *.json -File) {
    $s = Read-Sesi $f.FullName
    if ($null -ne $s) { $hasil += $s }
  }
  return $hasil
}
