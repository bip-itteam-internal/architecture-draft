# loop-kirim.ps1 — kirim satu peristiwa AI Engineering Loop ke dev-activity-board, BEST-EFFORT.
#
# Opt-in per mesin: hanya bila ~/.agent-kit/loop-ingest.json ada. Tanpa berkas itu, no-op.
#   { "url": "https://dev-activity-board.<akun>.workers.dev/loop/ingest",
#     "secret": "<LOOP_INGEST_SECRET>", "mesin": "opsional, bawaan nama komputer" }
#
# Aturan yang tidak boleh dilanggar: skrip ini TIDAK PERNAH memperlambat atau menggagalkan
# pekerjaan. Timeout 3 detik, semua galat ditelan, selalu exit 0. Setelah 3 kegagalan
# beruntun ia berhenti mencoba selama 10 menit (dicatat di ~/.agent-kit/loop-ingest.gagal),
# supaya jaringan yang mati tidak membuat tiap prompt menunggu.
#
# Privasi (ADR 0034 §4): yang dikirim hanya id, tahap, status, repo, domain, nomor PR,
# dan identitas git. Judul brief, teks task, dan judul PR TIDAK PERNAH dikirim.
# Tanda tangan: HMAC-SHA256 atas badan mentah, header X-Loop-Signature-256: sha256=<hex>.
param(
  [Parameter(Mandatory = $true)][string]$Jenis,
  # JSON bagian (sesi/brief/judge/pr). Panggil skrip ini IN-PROCESS (`& path\loop-kirim.ps1 -Data '{...}'`),
  # bukan lewat `powershell -File`: pemanggilan proses baru membuat Windows melucuti tanda kutip di
  # dalam argumen sehingga JSON-nya rusak diam-diam. Untuk pemanggil lintas proses pakai -DataFile.
  [string]$Data = '{}',
  [string]$DataFile,
  # Slug brief; id-nya (12 hex SHA-256) dihitung DI SINI, satu-satunya tempat aturan itu hidup,
  # lalu disuntikkan ke brief.id / judge.brief_id / pr.brief_id. Slug sendiri tidak dikirim.
  [string]$BriefSlug,
  [string]$Konfig = (Join-Path $env:USERPROFILE '.agent-kit\loop-ingest.json'),
  [int]$TimeoutDetik = 3,
  # Hanya cetak id brief lalu keluar (dipakai /kerjakan untuk log lokal yang cocok dengan papan)
  [switch]$HanyaId
)
$ErrorActionPreference = 'SilentlyContinue'
function Get-BriefId([string]$slug) {
  $sha = [System.Security.Cryptography.SHA256]::Create()
  $h = $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($slug.Trim().ToLowerInvariant()))
  return ([BitConverter]::ToString($h)).Replace('-', '').ToLowerInvariant().Substring(0, 12)
}
if ($HanyaId) { if ($BriefSlug) { Write-Output (Get-BriefId $BriefSlug) }; exit 0 }
try {
  if (-not (Test-Path $Konfig)) { exit 0 }
  $k = Get-Content $Konfig -Raw -Encoding UTF8 | ConvertFrom-Json
  if (-not $k.url -or -not $k.secret) { exit 0 }

  # jeda setelah kegagalan beruntun
  $gagalFile = Join-Path (Split-Path $Konfig -Parent) 'loop-ingest.gagal'
  $gagal = $null
  if (Test-Path $gagalFile) { try { $gagal = Get-Content $gagalFile -Raw | ConvertFrom-Json } catch {} }
  if ($gagal -and $gagal.beruntun -ge 3) {
    $sejak = [DateTime]::Parse([string]$gagal.terakhir, $null, [Globalization.DateTimeStyles]::RoundtripKind)
    if (((Get-Date).ToUniversalTime() - $sejak.ToUniversalTime()).TotalMinutes -lt 10) { exit 0 }
  }

  $mesin = if ($k.mesin) { [string]$k.mesin } else { $env:COMPUTERNAME }
  $email = (git config --global user.email 2>$null)
  $nama = (git config --global user.name 2>$null)
  $loginFile = Join-Path (Split-Path $Konfig -Parent) 'gh-login.txt'
  $login = if (Test-Path $loginFile) { (Get-Content $loginFile -Raw).Trim() } else { $null }
  if (-not $login) {
    $login = (gh api user --jq .login 2>$null)
    if ($login) { [IO.File]::WriteAllText($loginFile, $login.Trim()) }
  }

  $bagian = $null
  if ($DataFile -and (Test-Path $DataFile)) { $Data = Get-Content $DataFile -Raw -Encoding UTF8 }
  try { $bagian = $Data | ConvertFrom-Json } catch { $bagian = $null }
  $kunciBagian = switch -Regex ($Jenis) { '^sesi\.' { 'sesi' } '^brief\.' { 'brief' } '^judge\.' { 'judge' } '^loop\.pr$' { 'pr' } default { $null } }
  if (-not $kunciBagian -or $null -eq $bagian) { exit 0 }
  if ($BriefSlug) {
    $idBrief = Get-BriefId $BriefSlug
    $namaField = if ($kunciBagian -eq 'brief') { 'id' } else { 'brief_id' }
    if ($bagian.PSObject.Properties[$namaField]) { $bagian.$namaField = $idBrief } else { $bagian | Add-Member -NotePropertyName $namaField -NotePropertyValue $idBrief }
  }

  $muatan = [ordered]@{
    versi = 1; jenis = $Jenis; waktu = (Get-Date).ToUniversalTime().ToString('o'); mesin = $mesin
    orang = [ordered]@{ login = $(if ($login) { [string]$login } else { $null }); email = $(if ($email) { [string]$email } else { $null }); name = $(if ($nama) { [string]$nama } else { $null }) }
  }
  $muatan[$kunciBagian] = $bagian
  $json = $muatan | ConvertTo-Json -Compress -Depth 6
  $bytes = [Text.Encoding]::UTF8.GetBytes($json)

  $hmac = New-Object System.Security.Cryptography.HMACSHA256
  $hmac.Key = [Text.Encoding]::UTF8.GetBytes(([string]$k.secret).Trim())
  $hex = ([BitConverter]::ToString($hmac.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()

  $res = Invoke-WebRequest -Uri ([string]$k.url) -Method Post -Body $bytes -ContentType 'application/json; charset=utf-8' `
    -Headers @{ 'X-Loop-Signature-256' = ('sha256=' + $hex) } -TimeoutSec $TimeoutDetik -UseBasicParsing
  $ok = ($null -ne $res -and $res.StatusCode -ge 200 -and $res.StatusCode -lt 300)
  if ($ok) { if (Test-Path $gagalFile) { Remove-Item $gagalFile -Force } }
  else {
    $n = if ($gagal) { [int]$gagal.beruntun + 1 } else { 1 }
    $kode = if ($res) { $res.StatusCode } else { 'tanpa respons' }
    [IO.File]::WriteAllText($gagalFile, (@{ beruntun = $n; terakhir = (Get-Date).ToUniversalTime().ToString('o'); kode = "$kode" } | ConvertTo-Json -Compress))
  }
} catch {
  try {
    $n = if ($gagal) { [int]$gagal.beruntun + 1 } else { 1 }
    [IO.File]::WriteAllText($gagalFile, (@{ beruntun = $n; terakhir = (Get-Date).ToUniversalTime().ToString('o'); kode = [string]$_.Exception.Message } | ConvertTo-Json -Compress))
  } catch {}
}
exit 0
