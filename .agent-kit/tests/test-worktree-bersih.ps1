# test-worktree-bersih.ps1 - worktree-bersih.ps1 (kit 1.36.0) di repo sekali-pakai dengan origin lokal.
# Kontrol negatif utama (insiden 2026-10-05): worktree BARU tanpa commit ber-HEAD = origin/main
# WAJIB dilewati; dulu terbaca "merged" dan dibuang saat agen sedang menyuntingnya.
# Dipanggil test-init.ps1.
$ErrorActionPreference = 'Continue'
$kitRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$skrip = Join-Path $kitRoot 'hooks/worktree-bersih.ps1'
$tmp = Join-Path $env:TEMP ('agentkit-wtb-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$fail = 0
function Check($cond, $name) { if ($cond) { Write-Host "PASS $name" } else { Write-Host "FAIL $name"; $script:fail++ } }
function G { param([string]$d) git -C $d -c core.fsmonitor=false -c user.name=uji -c user.email=uji@x -c commit.gpgsign=false @args 2>&1 | Out-Null }

$origin = Join-Path $tmp 'origin.git'; $repo = Join-Path $tmp 'repo'
git init --bare -b main $origin 2>&1 | Out-Null
git clone $origin $repo 2>&1 | Out-Null
G $repo checkout -b main
Set-Content (Join-Path $repo 'a.txt') 'a'
G $repo add a.txt; G $repo commit -m awal; G $repo push origin main

function Wt([string]$nama) { $p = Join-Path $tmp $nama; G $repo worktree add -b "fix/$nama" $p origin/main; $p }
function Tua([string]$p) {
  # mundurkan semua mtime (berkas kerja + index/HEAD) supaya lolos jam senyap
  $t = (Get-Date).AddHours(-5)
  Get-ChildItem $p -Recurse -Force -File | ForEach-Object { $_.LastWriteTime = $t }
  $gd = git -C $p rev-parse --absolute-git-dir
  foreach ($f in 'index', 'HEAD') { $fp = Join-Path $gd $f; if (Test-Path $fp) { (Get-Item $fp -Force).LastWriteTime = $t } }
}

$baru = Wt 'baru'                       # tanpa commit, HEAD == origin/main
$merged = Wt 'merged'                   # commit sendiri, di-merge ke main
Set-Content (Join-Path $merged 'b.txt') 'b'; G $merged add b.txt; G $merged commit -m fitur
G $repo merge --ff-only fix/merged; G $repo push origin main
$untracked = Wt 'untracked'             # merged, tapi ada berkas untracked
Set-Content (Join-Path $untracked 'c.txt') 'c'; G $untracked add c.txt; G $untracked commit -m fitur2
G $repo merge --ff-only fix/untracked; G $repo push origin main
$dalam = Wt 'dalam'                     # merged, bersih, berkas DALAM baru disunting
New-Item -ItemType Directory -Force (Join-Path $dalam 'src/app') | Out-Null
Set-Content (Join-Path $dalam 'src/app/x.txt') 'x'; G $dalam add src; G $dalam commit -m fitur3
G $repo merge --ff-only fix/dalam; G $repo push origin main
$belum = Wt 'belum'                     # commit sendiri belum merged
Set-Content (Join-Path $belum 'd.txt') 'd'; G $belum add d.txt; G $belum commit -m wip

foreach ($p in $baru, $merged, $untracked, $dalam, $belum) { Tua $p }
Set-Content (Join-Path $untracked 'baru-untracked.txt') 'u'
(Get-Item (Join-Path $untracked 'baru-untracked.txt')).LastWriteTime = (Get-Date).AddHours(-5)
# sunting berkas dalam: mtime folder akar TIDAK ikut berubah
Set-Content (Join-Path $dalam 'src/app/x.txt') 'x'   # isi sama -> status bersih, mtime baru
(Get-Item (Join-Path $dalam 'src')).LastWriteTime = (Get-Date).AddHours(-5)

$out = & powershell -NoProfile -ExecutionPolicy Bypass -File $skrip -Repo $repo -TanpaGh 2>&1 | Out-String
function Baris([string]$b) { ($out -split "`n" | Where-Object { $_ -match [regex]::Escape("fix/$b ") }) -join '' }
Check ((Baris 'baru') -match '^\s*LEWATI' -and (Baris 'baru') -match 'tanpa commit sendiri') 'worktree baru tanpa commit -> LEWATI'
Check ((Baris 'merged') -match '^\s*HAPUS') 'branch dengan commit sendiri merged + bersih + senyap -> HAPUS'
Check ((Baris 'untracked') -match '^\s*LEWATI' -and (Baris 'untracked') -match 'untracked') 'berkas untracked -> LEWATI'
Check ((Baris 'dalam') -match '^\s*LEWATI' -and (Baris 'dalam') -match 'disentuh') 'sunting berkas dalam (bukan akar) -> LEWATI'
Check ((Baris 'belum') -match '^\s*LEWATI' -and (Baris 'belum') -match 'BELUM merged') 'commit belum merged -> LEWATI'
Check (Test-Path $merged) 'tanpa -Jalankan tak ada yang dihapus'

# .git rusak: status gagal tak boleh terbaca bersih
$rusak = Wt 'rusak'
Set-Content (Join-Path $rusak 'e.txt') 'e'; G $rusak add e.txt; G $rusak commit -m fitur4
G $repo merge --ff-only fix/rusak; G $repo push origin main
Tua $rusak; Remove-Item (Join-Path $rusak '.git') -Force

& powershell -NoProfile -ExecutionPolicy Bypass -File $skrip -Repo $repo -TanpaGh -Jalankan 2>&1 | Out-Null
Check (-not (Test-Path $merged)) '-Jalankan membuang worktree merged'
Check ((Test-Path $baru) -and (Test-Path (Join-Path $baru '.git'))) '-Jalankan TIDAK menyentuh worktree baru'
Check (Test-Path (Join-Path $untracked 'baru-untracked.txt')) '-Jalankan TIDAK menyentuh worktree ber-untracked'
Check (Test-Path $dalam) '-Jalankan TIDAK menyentuh worktree yang baru disunting'
Check (Test-Path (Join-Path $rusak 'e.txt')) '-Jalankan TIDAK membuang isi worktree ber-.git rusak'

foreach ($p in $baru, $untracked, $dalam, $belum) { G $repo worktree remove --force $p }
cmd /c ('rmdir /s /q "' + $tmp + '"') 2>&1 | Out-Null
if ($fail -gt 0) { Write-Host "$fail FAIL"; exit 1 }
Write-Host 'Semua lulus'; exit 0
