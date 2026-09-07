# worktree-bersih.ps1 — daftar dan (dengan -Jalankan) buang worktree yang SUDAH SELESAI:
# branch-nya merged ke origin/main, working tree bersih, dan tidak disentuh dalam -JamSenyap jam.
#
# Terukur 2026-09-06: 35 worktree terdaftar, 31 sudah merged dan tak ada yang tahu.
# Aturan yang dipatuhi (dari memori tim, semuanya pernah menggigit):
#   - `git worktree remove --force`, BUKAN Remove-Item: Remove-Item mengikuti junction pnpm dan
#     menghapus content-store bersama sehingga checkout lain ikut rusak.
#   - Kegagalan `worktree remove` bisa SEBAGIAN (registrasi hilang, folder utuh): registrasi dan
#     folder diperiksa terpisah; sisa folder dibuang dengan `cmd /c rmdir /s /q` (junction-safe).
#   - Detached, belum merged, atau baru disentuh: DILEWATI. Branch lokal TIDAK dihapus (dilaporkan).
param(
  [Parameter(Mandatory = $true)][string]$Repo,
  [string]$Base = 'origin/main',
  [int]$JamSenyap = 2,
  [switch]$Jalankan
)
$ErrorActionPreference = 'Continue'
$top = git -C $Repo -c core.fsmonitor=false rev-parse --show-toplevel 2>$null
if (-not $top) { [Console]::Error.WriteLine("Bukan repo git: $Repo"); exit 2 }
git -C $top -c core.fsmonitor=false fetch origin --quiet 2>$null

$lines = git -C $top -c core.fsmonitor=false worktree list --porcelain
$items = @(); $cur = $null
foreach ($l in $lines) {
  if ($l -like 'worktree *') { $cur = [pscustomobject]@{ path = $l.Substring(9); branch = $null; detached = $false } ; $items += $cur }
  elseif ($l -like 'branch *' -and $cur) { $cur.branch = $l.Substring(18) }
  elseif ($l -eq 'detached' -and $cur) { $cur.detached = $true }
}
$utama = $items[0].path
$batas = (Get-Date).AddHours(-$JamSenyap)
$rencana = @()
foreach ($it in $items) {
  if ($it.path -eq $utama) { continue }
  $ada = Test-Path $it.path
  $alasan = $null; $aksi = 'LEWATI'
  if ($it.detached) { $alasan = 'detached HEAD' }
  elseif (-not $it.branch) { $alasan = 'tanpa branch' }
  else {
    git -C $top -c core.fsmonitor=false merge-base --is-ancestor $it.branch $Base 2>$null
    $merged = ($LASTEXITCODE -eq 0)
    if (-not $merged) { $alasan = 'BELUM merged ke ' + $Base }
    elseif ($ada) {
      $dirty = @(git -C $it.path -c core.fsmonitor=false status --porcelain --untracked-files=no 2>$null)
      if ($dirty.Count -gt 0) { $alasan = ('ada {0} perubahan belum di-commit' -f $dirty.Count) }
      else {
        $baru = Get-ChildItem $it.path -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -notin @('node_modules', '.git', '.next') -and $_.LastWriteTime -gt $batas }
        if ($baru) { $alasan = ('disentuh < {0} jam lalu ({1})' -f $JamSenyap, ($baru | Select-Object -First 1).Name) }
        else { $aksi = 'HAPUS'; $alasan = 'merged, bersih, senyap' }
      }
    }
    else { $aksi = 'PRUNE'; $alasan = 'folder sudah hilang, registrasi basi' }
  }
  $rencana += [pscustomobject]@{ path = $it.path; branch = $it.branch; folder_ada = $ada; aksi = $aksi; alasan = $alasan }
}

$rencana | Format-Table -AutoSize aksi, branch, alasan, path | Out-String -Width 220 | Write-Host
$hapus = @($rencana | Where-Object { $_.aksi -eq 'HAPUS' })
Write-Host ("Ringkas: {0} worktree non-utama; HAPUS {1}, PRUNE {2}, LEWATI {3}" -f $rencana.Count, $hapus.Count, @($rencana | Where-Object { $_.aksi -eq 'PRUNE' }).Count, @($rencana | Where-Object { $_.aksi -eq 'LEWATI' }).Count)
if (-not $Jalankan) { Write-Host 'Belum ada yang dihapus. Ulangi dengan -Jalankan untuk mengeksekusi baris HAPUS.'; exit 0 }

$sukses = 0; $gagal = @()
foreach ($r in $hapus) {
  git -C $top -c core.fsmonitor=false worktree remove --force $r.path 2>&1 | Out-Null
  $masihFolder = Test-Path $r.path
  if ($masihFolder) { cmd /c ('rmdir /s /q "' + $r.path + '"') 2>&1 | Out-Null; $masihFolder = Test-Path $r.path }
  $masihTerdaftar = ((git -C $top -c core.fsmonitor=false worktree list --porcelain) -contains ('worktree ' + $r.path))
  if (-not $masihFolder -and -not $masihTerdaftar) { $sukses++ }
  else { $gagal += ('{0} (folder ada: {1}, terdaftar: {2})' -f $r.path, $masihFolder, $masihTerdaftar) }
}
git -C $top -c core.fsmonitor=false worktree prune 2>$null
Write-Host ("Dihapus: {0}/{1}. Sisa terdaftar: {2}" -f $sukses, $hapus.Count, (@(git -C $top -c core.fsmonitor=false worktree list).Count))
if ($gagal.Count -gt 0) { Write-Host 'GAGAL SEBAGIAN (periksa dua hal terpisah: registrasi dan folder):'; $gagal | ForEach-Object { Write-Host ('  ' + $_) } }
$branchMerged = @($hapus | Select-Object -ExpandProperty branch)
if ($branchMerged.Count -gt 0) { Write-Host ('Branch lokal merged yang TIDAK dihapus (hapus sendiri bila mau): ' + ($branchMerged -join ', ')) }
exit 0
