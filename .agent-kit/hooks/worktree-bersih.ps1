# worktree-bersih.ps1 — daftar dan (dengan -Jalankan) buang worktree yang SUDAH SELESAI:
# pekerjaan branch-nya terbukti masuk origin/main, working tree bersih (termasuk untracked), dan
# tidak disentuh dalam -JamSenyap jam.
#
# Terukur 2026-09-06: 35 worktree terdaftar, 31 sudah merged dan tak ada yang tahu.
# Aturan yang dipatuhi (dari memori tim, semuanya pernah menggigit):
#   - "Merged" BUKAN `merge-base --is-ancestor branch origin/main`. Worktree yang baru dibuat
#     `worktree-baru.ps1` dan belum punya commit sendiri ber-HEAD tepat di (atau leluhur) origin/main,
#     jadi uji itu menyatakannya merged dan worktree yang SEDANG DIKERJAKAN agen dibuang (2026-10-05,
#     fe-2020-page-header & fe-2021-stat-summary). Bukti selesai yang diterima hanya dua:
#       (a) PR ber-head branch ini MERGED dan headRefOid == ujung branch (menutup squash merge), atau
#       (b) ada commit SENDIRI branch ini (entri reflog `commit...`) yang reachable dari origin/main.
#     Tanpa bukti = LEWATI. Reflog tak terbaca dan gh tak ada = LEWATI (fail-closed).
#   - Kotor dihitung TERMASUK untracked; `git status` yang gagal (mis. berkas .git hilang) = LEWATI,
#     bukan "bersih".
#   - Jam senyap memakai waktu sentuh berkas TERBARU di seluruh pohon (rekursif, tanpa node_modules/
#     .next/.git, tanpa mengikuti junction) + index/HEAD worktree. Mtime folder akar tidak berubah
#     saat src/app/x.tsx disunting, jadi memeriksa entri akar saja meloloskan worktree yang aktif.
#   - Semua pemeriksaan DIULANG tepat sebelum menghapus (agen bisa mulai menyunting di antaranya).
#   - `git worktree remove --force`, BUKAN Remove-Item: Remove-Item mengikuti junction pnpm dan
#     menghapus content-store bersama sehingga checkout lain ikut rusak.
#   - Bila `worktree remove` GAGAL dan folder masih ada, folder DIBIARKAN dan dilaporkan. Dulu sisa
#     folder dibuang `cmd /c rmdir /s /q`: rmdir menghapus `.git` (urut abjad pertama) lalu berhenti di
#     berkas yang dikunci proses lain, meninggalkan worktree tanpa .git yang masih dipakai agen.
#   - Detached, tanpa branch: DILEWATI. Branch lokal TIDAK dihapus (dilaporkan).
param(
  [Parameter(Mandatory = $true)][string]$Repo,
  [string]$Base = 'origin/main',
  [int]$JamSenyap = 2,
  [switch]$TanpaGh,
  [switch]$Jalankan
)
$ErrorActionPreference = 'Continue'
$top = git -C $Repo -c core.fsmonitor=false rev-parse --show-toplevel 2>$null
if (-not $top) { [Console]::Error.WriteLine("Bukan repo git: $Repo"); exit 2 }
git -C $top -c core.fsmonitor=false fetch origin --quiet 2>$null
$adaGh = (-not $TanpaGh) -and [bool](Get-Command gh -ErrorAction SilentlyContinue)

function Get-SentuhTerakhir([string]$p) {
  # Rekursif manual: Get-ChildItem -Recurse turun ke node_modules (ribuan junction pnpm).
  $lewati = @('node_modules', '.next', '.git', '.turbo', 'dist', 'build', 'coverage')
  $maks = [datetime]::MinValue; $nama = $null
  $antre = New-Object System.Collections.Generic.Stack[System.IO.DirectoryInfo]
  $antre.Push([System.IO.DirectoryInfo]$p)
  while ($antre.Count -gt 0) {
    $d = $antre.Pop()
    try { $isi = $d.GetFileSystemInfos() } catch { continue }
    foreach ($e in $isi) {
      if ($e -is [System.IO.DirectoryInfo]) {
        if ($lewati -contains $e.Name) { continue }
        if ($e.Attributes -band [System.IO.FileAttributes]::ReparsePoint) { continue }
        $antre.Push($e)
      }
      elseif ($e.LastWriteTime -gt $maks) { $maks = $e.LastWriteTime; $nama = $e.FullName }
    }
  }
  # index & HEAD worktree: berubah saat stage/commit/checkout walau berkas kerja tak berubah
  $gd = git -C $p -c core.fsmonitor=false rev-parse --absolute-git-dir 2>$null
  if ($gd) {
    foreach ($f in @('index', 'HEAD')) {
      $fp = Join-Path $gd $f
      if (Test-Path $fp) { $t = (Get-Item $fp -Force).LastWriteTime; if ($t -gt $maks) { $maks = $t; $nama = $fp } }
    }
  }
  [pscustomobject]@{ waktu = $maks; berkas = $nama }
}

function Test-Selesai([string]$branch) {
  # Mengembalikan alasan bila selesai, $null bila tak ada bukti.
  $ujung = git -C $top -c core.fsmonitor=false rev-parse --verify --quiet ("refs/heads/$branch") 2>$null
  if (-not $ujung) { return $null }
  if ($adaGh) {
    Push-Location $top
    try { $j = gh pr list --head $branch --state merged --json number,headRefOid 2>$null } finally { Pop-Location }
    if ($LASTEXITCODE -eq 0 -and $j) {
      foreach ($pr in @($j | ConvertFrom-Json | ForEach-Object { $_ })) {
        if ($pr.headRefOid -eq $ujung) { return ('PR #{0} merged, ujung branch = head PR' -f $pr.number) }
      }
    }
  }
  $log = @(git -C $top -c core.fsmonitor=false reflog show --format='%H %gs' ("refs/heads/$branch") 2>$null)
  $milik = @($log | Where-Object { $_ -match '^[0-9a-f]{40} commit' } | ForEach-Object { $_.Substring(0, 40) } | Select-Object -Unique)
  foreach ($c in $milik) {
    git -C $top -c core.fsmonitor=false merge-base --is-ancestor $c $Base 2>$null
    if ($LASTEXITCODE -eq 0) { return ('commit sendiri {0} ada di {1}' -f $c.Substring(0, 9), $Base) }
  }
  return $null
}

function Get-Penghalang([pscustomobject]$it, [datetime]$batas) {
  # Pemeriksaan worktree yang dipakai SAAT MENDAFTAR dan DIULANG SAAT MENGHAPUS.
  # Waktu sentuh diukur DULU, dan status memakai --no-optional-locks: `git status` biasa menulis
  # ulang index (refresh stat) sehingga pemeriksaan ini sendiri membuat worktree tampak baru disentuh.
  $s = Get-SentuhTerakhir $it.path
  $st = @(git --no-optional-locks -C $it.path -c core.fsmonitor=false status --porcelain --untracked-files=normal 2>$null)
  if ($LASTEXITCODE -ne 0) { return 'git status GAGAL (berkas .git rusak/hilang?): tak bisa membuktikan bersih' }
  if ($st.Count -gt 0) { return ('ada {0} perubahan belum di-commit (termasuk untracked)' -f $st.Count) }
  if ($s.waktu -gt $batas) { return ('disentuh < {0} jam lalu ({1:yyyy-MM-dd HH:mm}, {2})' -f $JamSenyap, $s.waktu, $s.berkas) }
  return $null
}

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
    $bukti = Test-Selesai $it.branch
    if (-not $bukti) {
      $maju = git -C $top -c core.fsmonitor=false rev-list --count ("$Base..refs/heads/" + $it.branch) 2>$null
      $alasan = if ($maju -eq '0') { 'tanpa commit sendiri yang masuk ' + $Base + ' (worktree baru/aktif?)' } else { 'BELUM merged ke ' + $Base }
    }
    elseif ($ada) {
      $h = Get-Penghalang $it $batas
      if ($h) { $alasan = $h } else { $aksi = 'HAPUS'; $alasan = $bukti + '; bersih, senyap' }
    }
    else { $aksi = 'PRUNE'; $alasan = 'folder sudah hilang, registrasi basi' }
  }
  $rencana += [pscustomobject]@{ path = $it.path; branch = $it.branch; folder_ada = $ada; aksi = $aksi; alasan = $alasan; obj = $it }
}

$rencana | Format-Table -AutoSize aksi, branch, alasan, path | Out-String -Width 260 | Write-Host
$hapus = @($rencana | Where-Object { $_.aksi -eq 'HAPUS' })
Write-Host ("Ringkas: {0} worktree non-utama; HAPUS {1}, PRUNE {2}, LEWATI {3}" -f $rencana.Count, $hapus.Count, @($rencana | Where-Object { $_.aksi -eq 'PRUNE' }).Count, @($rencana | Where-Object { $_.aksi -eq 'LEWATI' }).Count)
if (-not $adaGh) { Write-Host 'Catatan: gh tak dipakai; branch yang di-squash-merge tak terbukti selesai dan dilewati.' }
if (-not $Jalankan) { Write-Host 'Belum ada yang dihapus. Ulangi dengan -Jalankan untuk mengeksekusi baris HAPUS.'; exit 0 }

$sukses = 0; $gagal = @(); $batal = @(); $dibuang = @()
foreach ($r in $hapus) {
  # Ulangi pemeriksaan tepat sebelum menghapus: jeda sejak daftar dibuat bisa menit.
  $h = Get-Penghalang $r.obj (Get-Date).AddHours(-$JamSenyap)
  if ($h) { $batal += ('{0}: {1}' -f $r.path, $h); continue }
  git -C $top -c core.fsmonitor=false worktree remove --force $r.path 2>&1 | Out-Null
  $masihFolder = Test-Path $r.path
  $masihTerdaftar = ((git -C $top -c core.fsmonitor=false worktree list --porcelain) -contains ('worktree ' + $r.path))
  if (-not $masihFolder -and -not $masihTerdaftar) { $sukses++; $dibuang += $r.branch }
  else { $gagal += ('{0} (folder ada: {1}, terdaftar: {2})' -f $r.path, $masihFolder, $masihTerdaftar) }
}
git -C $top -c core.fsmonitor=false worktree prune 2>$null
Write-Host ("Dihapus: {0}/{1}. Sisa terdaftar: {2}" -f $sukses, $hapus.Count, (@(git -C $top -c core.fsmonitor=false worktree list).Count))
if ($batal.Count -gt 0) { Write-Host 'DIBATALKAN (berubah sejak didaftar):'; $batal | ForEach-Object { Write-Host ('  ' + $_) } }
if ($gagal.Count -gt 0) { Write-Host 'GAGAL (folder sengaja DIBIARKAN; tutup proses yang memegangnya lalu ulangi):'; $gagal | ForEach-Object { Write-Host ('  ' + $_) } }
if ($dibuang.Count -gt 0) { Write-Host ('Branch lokal merged yang TIDAK dihapus (hapus sendiri bila mau): ' + ($dibuang -join ', ')) }
exit 0
