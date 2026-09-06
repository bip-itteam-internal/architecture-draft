# worktree-baru.ps1 — buat worktree TERISOLASI di path PENDEK untuk satu brief, dari origin/main.
#
# Kenapa path pendek dan bukan `isolation: worktree` bawaan: worktree erp-frontend di path
# panjang (scratchpad sesi, ~150 char) membuat `pnpm install` "sukses" tanpa rollup dan vitest
# mati (team-memory). Pola yang sudah terbukti dipakai tim: ~/fe-<slug>, ~/be-<slug>.
# Kenapa worktree dan bukan checkout utama: beberapa sesi berbagi satu working tree = commit
# nyasar ke branch orang lain (memori two-claude-sessions-one-worktree).
param(
  [Parameter(Mandatory = $true)][string]$Repo,      # path repo utama, mis. ...\erp\erp-frontend
  [Parameter(Mandatory = $true)][string]$Slug,
  [string]$Domain = 'fix',
  [string]$Base = 'origin/main',
  [string]$Akar = (Join-Path $env:USERPROFILE 'wt'),
  [switch]$TanpaInstall
)
# 'Continue', BUKAN 'Stop': git menulis "Preparing worktree ..." ke stderr saat SUKSES, dan PS 5.1
# di bawah 'Stop' mengubah baris stderr native jadi galat terminating (skrip mati dengan exit 1
# padahal worktree-nya jadi). Keberhasilan diperiksa lewat $LASTEXITCODE.
$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot 'gerbang-lib.ps1')

$top = Get-RepoTop $Repo
if (-not $top) { [Console]::Error.WriteLine("Bukan repo git: $Repo"); exit 2 }
$nama = Get-NamaRepo $top
$prefix = switch ($nama) { 'erp-frontend' { 'fe' } 'bip-erp' { 'be' } 'mybharata-app' { 'mb' } 'architecture-draft' { 'ad' } default { ($nama -replace '[^a-z0-9]', '').Substring(0, [math]::Min(3, ($nama -replace '[^a-z0-9]', '').Length)) } }
$slug = ($Slug.ToLowerInvariant() -replace '[^a-z0-9]+', '-').Trim('-')
if ($slug.Length -gt 30) { $slug = $slug.Substring(0, 30).Trim('-') }
if (-not $slug) { [Console]::Error.WriteLine('Slug kosong setelah dibersihkan'); exit 2 }
$domain = ($Domain.ToLowerInvariant() -replace '[^a-z]', '')
if ($domain -notin @('fix', 'refactor', 'test', 'docs', 'feat', 'chore')) { $domain = 'fix' }

$path = Join-Path $Akar ($prefix + '-' + $slug)
if ($path.Length -gt 60) { [Console]::Error.WriteLine("Path worktree terlalu panjang ($($path.Length) > 60): $path. pnpm/vitest akan mati diam-diam."); exit 2 }
if ($path -match '\s') { [Console]::Error.WriteLine("Path worktree mengandung spasi: $path"); exit 2 }
if (Test-Path $path) { [Console]::Error.WriteLine("Sudah ada: $path. Pakai slug lain atau bersihkan dulu."); exit 2 }
$branch = "$domain/$slug"

New-Item -ItemType Directory -Force -Path $Akar | Out-Null
git -C $top -c core.fsmonitor=false fetch origin --quiet 2>$null
$adaBranch = git -C $top -c core.fsmonitor=false rev-parse --verify --quiet ('refs/heads/' + $branch) 2>$null
if ($adaBranch) { [Console]::Error.WriteLine("Branch sudah ada: $branch. Pakai slug lain."); exit 2 }
$out = git -C $top -c core.fsmonitor=false worktree add -b $branch $path $Base 2>&1
if ($LASTEXITCODE -ne 0) { [Console]::Error.WriteLine(("git worktree add gagal: {0}" -f ($out -join ' '))); exit 1 }

$jenis = Get-JenisRepo $path
$install = $null
if ($jenis -eq 'node' -and -not $TanpaInstall) {
  $sw = [Diagnostics.Stopwatch]::StartNew()
  Push-Location $path
  try { $io = @(pnpm install --prefer-offline --frozen-lockfile 2>&1 | ForEach-Object { [string]$_ }); $irc = $LASTEXITCODE } finally { Pop-Location }
  $sw.Stop()
  $install = [pscustomobject]@{ lolos = ($irc -eq 0); durasi_detik = [math]::Round($sw.Elapsed.TotalSeconds, 1); ekor = @($io | Select-Object -Last 5) }
  if ($irc -ne 0) { [Console]::Error.WriteLine('pnpm install GAGAL di worktree; eksekutor akan bekerja tanpa node_modules. Periksa ekor keluaran.') }
}
$hasil = [pscustomobject]@{ repo = $nama; jenis = $jenis; path = $path; branch = $branch; base = $Base; install = $install }
$hasil | ConvertTo-Json -Depth 4
exit 0
