# cek-lock-receipt.ps1 - status lock receipt-sync: aman deploy integration-service sekarang atau tidak.
#
# Mencetak SATU baris, dipakai agent di akhir tiap jawaban dan sesudah tugas perubahan kode
# (aturan di CLAUDE.md "Aturan turunan"). Keputusannya ada di cek-lock-receipt.py (satu tempat);
# pengumpul faktanya cek-lock-receipt.remote.sh, dijalankan DI SERVER lewat ssh, BACA-SAJA.
#
# Akses prod itu per orang, jadi host dan kunci TIDAK ada di kit. Opt-in per mesin, seperti
# loop-ingest.json: ~/.agent-kit/prod-ssh.json
#   { "host": "<user>@<alamat server prod>", "key": "C:\\Users\\<anda>\\.ssh\\<kunci pribadi>" }
# Tanpa berkas itu (atau ssh/python gagal) hasilnya "tidak bisa dicek" - TIDAK PERNAH menebak aman,
# dan exit selalu 0 supaya tidak memutus alur agent.
param([string]$Konfig = (Join-Path $env:USERPROFILE '.agent-kit\prod-ssh.json'))
$ErrorActionPreference = 'Continue'
$utf8 = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8

function Selesai([string]$teks) { Write-Output $teks; exit 0 }

if (-not (Test-Path $Konfig)) {
  Selesai ('Receipt lock tidak bisa dicek (belum ada {0}), jangan diasumsikan aman' -f $Konfig)
}
try { $k = Get-Content $Konfig -Raw | ConvertFrom-Json } catch { Selesai 'Receipt lock tidak bisa dicek (prod-ssh.json tidak terbaca), jangan diasumsikan aman' }
if (-not $k.host -or -not $k.key) { Selesai 'Receipt lock tidak bisa dicek (prod-ssh.json tanpa host/key), jangan diasumsikan aman' }

$py = $null
foreach ($c in @('python', 'py', 'python3')) { if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break } }
if (-not $py) {
  $venv = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'architecture-draft\Tools\.venv\Scripts\python.exe'
  if (Test-Path $venv) { $py = $venv }
}
if (-not $py) { Selesai 'Receipt lock tidak bisa dicek (python tidak ditemukan), jangan diasumsikan aman' }

# BOM dari stdin PowerShell 5.1 merusak baris pertama bash; skrip jarak jauh dibaca sebagai UTF-8
# tanpa BOM dan dikirim lewat stdin supaya tak ada berkas yang ditulis di server.
$skrip = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'cek-lock-receipt.remote.sh')) -replace "`r", ''
# ": " menelan BOM; "exit 0" menutup supaya CRLF yang ditambahkan PowerShell di ujung stdin tidak
# terbaca bash sebagai perintah terakhir (exit 127). Keberhasilan dinilai dari ADA tidaknya fakta
# (JSON satu baris), bukan dari exit code ssh.
$skrip = ": `n" + $skrip.TrimEnd() + "`nexit 0`n"
$fakta = $skrip | ssh -o BatchMode=yes -o ConnectTimeout=15 -i $k.key $k.host 'bash -s' 2>$null | Where-Object { $_ -match '^\{' } | Select-Object -Last 1
if (-not $fakta) { Selesai 'Receipt lock tidak bisa dicek (ssh ke server prod gagal), jangan diasumsikan aman' }

$hasil = ($fakta | & $py (Join-Path $PSScriptRoot 'cek-lock-receipt.py') 2>$null)
if (-not $hasil) { Selesai 'Receipt lock tidak bisa dicek (keputusan gagal dihitung), jangan diasumsikan aman' }
Write-Output ($hasil | Select-Object -Last 1)
exit 0
