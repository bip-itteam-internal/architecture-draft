# dashboard.ps1 — pengumpul data dashboard AI Engineering Loop; UI-nya SATU tempat: dashboard.template.html.
#
# Mengumpulkan: PR (gh, per irisan mingguan supaya tidak terpotong batas 500), brief, log judge,
# sesi, baseline, jumlah worktree; menanamkan JSON ke template; menulis .task-plans/dashboard.html.
# Berkas, bukan layanan (ADR 0077 §5). -Loop <detik> menulis ulang berkala; halaman me-refresh
# diri tiap 60 detik. -TanpaGh memakai cache .task-plans/dashboard-data.json (cepat, offline).
#
# Panel tanpa sumber data (biaya per PR, klasifikasi risiko) sengaja tidak dihitung; ditulis di
# kaki halaman supaya tidak ada nol palsu.
param(
  [string]$Workspace = (Get-Location).Path,
  [int]$Hari = 30,
  [string[]]$Repos = @('bip-erp', 'erp-frontend'),
  [string]$Org = 'bip-itteam-internal',
  [switch]$TanpaGh,
  [int]$Loop = 0,
  [string]$Keluaran
)
$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot 'sesi-lib.ps1')
. (Join-Path $PSScriptRoot 'gerbang-lib.ps1')

$ws = (Resolve-Path $Workspace).Path
$kit = Get-KitRoot $PSScriptRoot
$template = Join-Path $PSScriptRoot 'dashboard.template.html'
if (-not $Keluaran) { $Keluaran = Join-Path $ws '.task-plans\dashboard.html' }
$cachePath = Join-Path $ws '.task-plans\dashboard-data.json'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$RE_PREFIX = '^(feat|fix|docs|test|chore|refactor|perf|style|build|ci)(\(([^)]+)\))?!?:'

function Ambil-PR {
  # union per (repo, number) dari irisan mingguan `created:` dan `merged:`; catat irisan yang penuh
  $hasil = @{}; $terpotong = @(); $ok = $true; $pesan = ''
  $cek = gh auth status 2>&1
  if ($LASTEXITCODE -ne 0) { return [pscustomobject]@{ ok = $false; pesan = ('gh belum login: ' + (($cek | Out-String).Trim() -split "`n")[0]); pr = @(); terpotong = @() } }
  $akhir = (Get-Date).Date
  foreach ($repo in $Repos) {
    $i = 0
    while ($i * 7 -lt $Hari) {
      $sampai = $akhir.AddDays(-7 * $i); $dari = $akhir.AddDays(-7 * ($i + 1) + 1)
      $rentang = $dari.ToString('yyyy-MM-dd') + '..' + $sampai.ToString('yyyy-MM-dd')
      foreach ($mode in 'created', 'merged') {
        $stateArg = if ($mode -eq 'merged') { 'merged' } else { 'all' }
        $raw = gh pr list --repo "$Org/$repo" --state $stateArg --limit 500 --search "$mode`:$rentang" --json number,title,createdAt,mergedAt,state,headRefName,author,url 2>$null
        if ($LASTEXITCODE -ne 0) { $ok = $false; $pesan = "gh pr list gagal untuk $repo $mode $rentang (exit $LASTEXITCODE)"; continue }
        # PS 5.1: ConvertFrom-Json atas ARRAY JSON memancarkan array itu sebagai SATU objek; tanpa
        # ForEach-Object, foreach di bawah berputar sekali dengan $p = seluruh array (terjadi 2026-09-07:
        # "20 PR" = 20 irisan, dan $p.title berupa array sehingga $Matches kosong).
        try { $arr = @((($raw -join '') | ConvertFrom-Json) | ForEach-Object { $_ }) } catch { $arr = @() }
        if ($arr.Count -ge 500) { $terpotong += ("{0} {1} {2}" -f $repo, $mode, $rentang) }
        foreach ($p in $arr) {
          $key = $repo + '#' + $p.number
          if ($hasil.ContainsKey($key)) { continue }
          $prefix = $null; $scope = $null
          $judul = [string]$p.title
          if ($judul -match $RE_PREFIX) { $prefix = $Matches[1].ToLower(); if ($Matches[3]) { $scope = $Matches[3].ToLower() } }
          $hasil[$key] = [pscustomobject]@{
            repo = $repo; number = $p.number; title = $judul; createdAt = $p.createdAt; mergedAt = $p.mergedAt
            state = $p.state; branch = $p.headRefName; author = [string]$p.author.login; url = $p.url; prefix = $prefix; scope = $scope
          }
        }
      }
      $i++
    }
  }
  return [pscustomobject]@{ ok = $ok; pesan = $pesan; pr = @($hasil.Values | Sort-Object createdAt -Descending); terpotong = $terpotong }
}

function Ambil-Brief {
  $dir = Join-Path $ws '.task-plans\briefs'
  if (-not (Test-Path $dir)) { return @() }
  $out = @()
  foreach ($f in Get-ChildItem $dir -Filter *.md -File) {
    $txt = Get-Content $f.FullName -Raw -Encoding UTF8
    $judul = if ($txt -match '(?m)^# Brief:\s*(.+)$') { $Matches[1].Trim() } else { $f.BaseName }
    $repo = if ($txt -match '(?m)^- Repo:\s*(\S+)') { $Matches[1] } else { '' }
    $domain = if ($txt -match '(?m)^- Domain:\s*(\S+)') { $Matches[1] } else { '' }
    $tanggal = if ($txt -match '(?m)^- Tanggal:\s*(\S+)') { $Matches[1] } else { '' }
    $hasil = if ($txt -match '(?s)## Hasil\s*(.*)$') { $Matches[1] } else { '' }
    $prUrl = if ($hasil -match '(https://github\.com/[^\s)*]+/pull/\d+)') { $Matches[1] } else { $null }
    $status = if ($prUrl) { 'pr' } elseif ($hasil -match 'GAGAL') { 'gagal' } else { 'belum' }
    $percobaan = if ($hasil -match 'Percobaan:\s*(\d)') { [int]$Matches[1] } else { $null }
    $worktree = if ($hasil -match 'Worktree:\s*`?([^`\s·]+)') { $Matches[1] } else { '' }
    $slug = $f.BaseName -replace '^\d{4}-\d{2}-\d{2}-', ''
    $out += [pscustomobject]@{ berkas = ('.task-plans/briefs/' + $f.Name); slug = $slug; judul = $judul; repo = $repo; domain = $domain; tanggal = $tanggal; status = $status; pr_url = $prUrl; percobaan = $percobaan; worktree = $worktree }
  }
  return $out
}

function Ambil-Judge {
  $dir = Join-Path $ws '.task-plans\judge'
  if (-not (Test-Path $dir)) { return @() }
  $out = @()
  foreach ($f in Get-ChildItem $dir -Filter *.json -File | Where-Object { $_.Name -match '-\d+\.json$' }) {
    try { $j = Get-Content $f.FullName -Raw -Encoding UTF8 | ConvertFrom-Json } catch { continue }
    $dur = 0; foreach ($g in @($j.gerbang.gerbang)) { if ($g.durasi_detik) { $dur += [double]$g.durasi_detik } }
    $kritis = @($j.verdict.temuan | Where-Object { $_.kelas -eq 'kritis' }).Count
    $out += [pscustomobject]@{ berkas = $f.Name; slug = ($f.BaseName -replace '-\d+$', ''); percobaan = $j.percobaan; lolos = [bool]$j.lolos; waktu = $j.waktu; durasi_gerbang = [math]::Round($dur, 1); temuan_kritis = $kritis; agen = $j.agen }
  }
  return $out
}

function Ambil-Baseline {
  $dir = Join-Path $kit 'baseline'
  if (-not (Test-Path $dir)) { return @() }
  $out = @()
  foreach ($f in Get-ChildItem $dir -Filter *.json -File) {
    try { $b = Get-Content $f.FullName -Raw -Encoding UTF8 | ConvertFrom-Json } catch { continue }
    $out += [pscustomobject]@{ repo = $b.repo; tanggal = $b.tanggal; commit = $b.commit; jumlah_test = $b.jumlah_test; jumlah_gagal = $b.jumlah_gagal }
  }
  return $out
}

function Ambil-Worktree {
  $out = @()
  foreach ($r in $Repos) {
    $p = Join-Path $ws $r
    if (-not (Test-Path $p)) { continue }
    $n = @(git -C $p -c core.fsmonitor=false worktree list 2>$null).Count
    $out += [pscustomobject]@{ repo = $r; jumlah = $n }
  }
  return $out
}

function Bangun {
  $ghInfo = $null; $pr = @()
  if ($TanpaGh) {
    if (Test-Path $cachePath) {
      try { $c = Get-Content $cachePath -Raw -Encoding UTF8 | ConvertFrom-Json; $pr = @($c.pr); $ghInfo = [pscustomobject]@{ ok = [bool]$c.gh.ok; pesan = $c.gh.pesan; terpotong = @($c.gh.terpotong); dari_cache = $c.dibuat } } catch {}
    }
    if ($null -eq $ghInfo) { $ghInfo = [pscustomobject]@{ ok = $false; pesan = 'tanpa gh dan tidak ada cache'; terpotong = @(); dari_cache = $null } }
  } else {
    $r = Ambil-PR; $pr = @($r.pr)
    $ghInfo = [pscustomobject]@{ ok = $r.ok; pesan = $r.pesan; terpotong = @($r.terpotong); dari_cache = $null }
  }
  $data = [pscustomobject]@{
    versi = 1; dibuat = (Get-Date).ToString('o'); workspace = $ws; hari = $Hari; repos = $Repos
    gh = $ghInfo; pr = $pr
    briefs = @(Ambil-Brief); judge = @(Ambil-Judge); sesi = @(Get-SemuaSesi $ws)
    baseline = @(Ambil-Baseline); worktree = @(Ambil-Worktree)
    tanpa_sumber = @('biaya per PR / token (tidak ada pelacakan biaya)', 'klasifikasi risiko dan patch/architectural (klasifikasi otomatis tampil pasti padahal tebakan)')
  }
  $json = $data | ConvertTo-Json -Depth 8 -Compress
  if (-not $TanpaGh) { [IO.File]::WriteAllText($cachePath, $json, $utf8) }
  $html = Get-Content $template -Raw -Encoding UTF8
  $aman = $json -replace '</', '<\/'   # jangan menutup <script> dari dalam JSON
  $html = $html.Replace('__DASHBOARD_DATA__', $aman)
  $dir = Split-Path $Keluaran -Parent
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  [IO.File]::WriteAllText($Keluaran, $html, $utf8)
  Write-Host ("Dashboard: {0}  (PR {1}, brief {2}, judge {3}, sesi {4}{5})" -f $Keluaran, $pr.Count, $data.briefs.Count, $data.judge.Count, $data.sesi.Count, $(if ($ghInfo.ok) { '' } else { ', GH TIDAK: ' + $ghInfo.pesan }))
  if ($ghInfo.terpotong.Count -gt 0) { Write-Host ('PERINGATAN irisan penuh (angka kurang dari kenyataan): ' + ($ghInfo.terpotong -join '; ')) }
}

if (-not (Test-Path $template)) { [Console]::Error.WriteLine("Template tidak ada: $template"); exit 2 }
if ($Loop -gt 0) {
  Write-Host ("Mode loop: menulis ulang tiap {0} detik. Hentikan dengan Ctrl+C atau matikan prosesnya." -f $Loop)
  while ($true) { Bangun; Start-Sleep -Seconds $Loop }
} else { Bangun }
exit 0
