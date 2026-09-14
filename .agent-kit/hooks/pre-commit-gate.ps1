# pre-commit-gate.ps1 — PreToolUse(Bash|PowerShell): GERBANG commit, bukan pengingat.
#
# MENOLAK `git commit` di branch default (main/master/origin HEAD) sebuah repo KODE.
# Vault architecture-draft dikecualikan: konvensinya memang push langsung ke main.
#
# Menolak lewat EXIT 2, bukan JSON: exit 2 memblokir tool call apa pun isi stdout-nya, jadi
# JSON yang salah bentuk tidak bisa membuat gerbang ini gagal-terbuka (kelas kegagalan yang
# sama dengan matcher `Bash` yang membuat versi lama tak pernah menyala di mesin PowerShell).
#
# GAGAL-TERTUTUP: bila ada `commit` tetapi repo-nya tidak bisa ditentukan (path dari ekspresi
# seperti `-C $t` dengan `$t = Join-Path ...`), gerbang MENOLAK dan menyuruh memakai path
# literal. Terbukti 2026-09-06: versi gagal-terbuka meloloskan commit di `main` persis lewat
# bentuk perintah yang biasa ditulis agent. Yang masih dikenali: `-C "literal"`, `-C $v` dengan
# `$v="literal"` di perintah yang sama, `$env:NAMA` di dalam string, dan `cd <path>; git commit`.
# Selain kasus tolak: exit 0 + pengingat, persis perilaku lama.
#
# CATATAN (brief pre-commit-gate-overhead, 2026-09-12): init.ps1/init.sh memasang skrip ini
# di belakang filter 'if' (pola *commit* pada isi command) sehingga proses ini TIDAK di-spawn
# sama sekali kalau isi command tak cocok pola itu. Menambah bentuk commit baru yang dikenali
# DI SINI wajib diikuti memperluas pola 'if' di init.ps1 DAN init.sh -- kalau tidak, bentuk
# barunya tidak akan pernah sampai kesini untuk diperiksa. Detail dan hasil verifikasi ada di
# komentar blok PreToolUse pada init.ps1, jangan diduplikasi di sini.
$ErrorActionPreference = 'SilentlyContinue'
if (-not [Console]::IsInputRedirected) { exit 0 }
$raw = [Console]::In.ReadToEnd()
try { $data = $raw | ConvertFrom-Json } catch { exit 0 }
$cmd = [string]$data.tool_input.command
if (-not $cmd) { exit 0 }
$cwd = [string]$data.cwd

function Get-Tokens([string]$s) {
  # token ber-kutip dipertahankan utuh (path ber-spasi), kutipnya dibuang
  $ms = [regex]::Matches($s, '"([^"]*)"|''([^'']*)''|(\S+)')
  foreach ($m in $ms) {
    if ($m.Groups[1].Success) { $m.Groups[1].Value }
    elseif ($m.Groups[2].Success) { $m.Groups[2].Value }
    else { $m.Groups[3].Value }
  }
}

# `$v="..."; git -C $v commit` — baca assignment LITERAL di perintah yang sama
$vars = @{}
foreach ($m in [regex]::Matches($cmd, '\$(\w+)\s*=\s*(?:"([^"]*)"|''([^'']*)'')')) {
  $vars[$m.Groups[1].Value] = if ($m.Groups[2].Success) { $m.Groups[2].Value } else { $m.Groups[3].Value }
}

$TAK = '<<tak-terurai>>'
function Resolve-Dir([string]$rawDir) {
  if (-not $rawDir) { return $null }
  $d = $rawDir
  # $env:NAMA di dalam string -> nilai env
  $d = [regex]::Replace($d, '\$env:(\w+)', { param($m) [string][Environment]::GetEnvironmentVariable($m.Groups[1].Value) })
  if ($d -match '^\$\{?(\w+)\}?$') {
    $n = $Matches[1]
    if ($vars.ContainsKey($n)) { $d = $vars[$n] } else { return $TAK }
  }
  if ($d -match '\$' -or $d -match '`') { return $TAK }   # masih ada ekspresi
  if (Test-Path $d) { return (Resolve-Path $d).Path }
  return $TAK
}

# Periksa SETIAP segmen (`;`, `&&`, `||`, baris baru): `git add .; git commit` tetap kena.
# `cd`/Set-Location sebelum segmen commit ikut dicatat sebagai repo kandidat.
$segments = $cmd -split '(?:;|&&|\|\||\r?\n)'
$repoRaw = $null; $adaC = $false; $isCommit = $false; $cdRaw = $null
foreach ($seg in $segments) {
  $tokens = @(Get-Tokens $seg)
  if ($tokens.Count -eq 0) { continue }
  $t0 = $tokens[0]
  if ($t0 -in @('cd', 'chdir', 'sl', 'Set-Location', 'Push-Location', 'pushd') -and $tokens.Count -gt 1) {
    $cdRaw = ($tokens[1..($tokens.Count - 1)] | Where-Object { $_ -notlike '-*' } | Select-Object -First 1)
    continue
  }
  $gi = -1
  for ($i = 0; $i -lt $tokens.Count; $i++) {
    if ($tokens[$i] -match '(^|[\\/])git(\.exe)?$') { $gi = $i; break }
  }
  if ($gi -lt 0) { continue }
  $dir = $null; $sub = $null; $punyaC = $false
  for ($i = $gi + 1; $i -lt $tokens.Count; $i++) {
    $t = $tokens[$i]
    # -ceq (peka huruf): `-eq` PowerShell menyamakan -C dan -c, sehingga `-c core.fsmonitor=false`
    # pernah menimpa path repo dan gerbang ini gagal-terbuka persis di perintah git yang tim pakai
    if ($t -ceq '-C' -and ($i + 1) -lt $tokens.Count) { $dir = $tokens[$i + 1]; $punyaC = $true; $i++; continue }
    if ($t -ceq '-c' -and ($i + 1) -lt $tokens.Count) { $i++; continue }
    if ($t -like '-*') { continue }
    $sub = $t; break   # token non-opsi pertama sesudah git = subperintah
  }
  if ($sub -eq 'commit') { $isCommit = $true; $adaC = $punyaC; $repoRaw = $dir; break }
}
if (-not $isCommit) { exit 0 }

$repoDir = $null
if ($adaC) { $repoDir = Resolve-Dir $repoRaw }
elseif ($cdRaw) { $repoDir = Resolve-Dir $cdRaw }
if ($repoDir -eq $TAK) {
  $msg = "DITOLAK gerbang agent-kit: ada 'git commit' tetapi repo-nya tidak bisa ditentukan dari perintah " +
         "(path datang dari ekspresi/variabel: '$(if ($adaC) { $repoRaw } else { $cdRaw })'). " +
         "Tulis path LITERAL, mis. git -C `"C:\...\repo`" commit ..., atau `$v=`"C:\...\repo`" di perintah yang sama. Gerbang ini sengaja gagal-tertutup."
  [Console]::Error.WriteLine($msg)
  exit 2
}
if (-not $repoDir) { $repoDir = $cwd }
if (-not $repoDir -or -not (Test-Path $repoDir)) { exit 0 }

# --path-format=absolute supaya worktree tertaut pun terbaca milik repo mana
$common = git -C $repoDir rev-parse --path-format=absolute --git-common-dir 2>$null
if (-not $common) { exit 0 }   # bukan repo git: bukan urusan gerbang ini
if ($common -match 'architecture-draft') {
  @{ hookSpecificOutput = @{ hookEventName = 'PreToolUse'; additionalContext = 'Vault: stage per-nama berkas (jangan git add -A), wikilink 0 broken, regenerasi VAULT-INDEX bila dok berubah, tanpa trailer Co-Authored-By.' } } |
    ConvertTo-Json -Compress -Depth 5
  exit 0
}

$branch = git -C $repoDir symbolic-ref --short HEAD 2>$null
if (-not $branch) { exit 0 }   # detached HEAD: bukan branch default
$defaults = @('main', 'master')
$oh = git -C $repoDir symbolic-ref --short refs/remotes/origin/HEAD 2>$null
if ($oh) { $defaults += ($oh -replace '^origin/', '') }

if ($defaults -contains $branch) {
  $msg = "DITOLAK gerbang agent-kit: 'git commit' di branch '$branch' repo kode '$repoDir'. " +
         "Semua repo kode wajib lewat PR (team-memory, ADR 0077). Buat branch dulu: " +
         "git -C `"$repoDir`" checkout -b feat/<nama>  lalu commit di sana."
  [Console]::Error.WriteLine($msg)
  exit 2
}

@{ hookSpecificOutput = @{ hookEventName = 'PreToolUse'; additionalContext = 'Reminder sebelum commit: sudah /sync-docs? wikilink resolve (0 broken)? test hijau? Tanpa trailer Co-Authored-By.' } } |
  ConvertTo-Json -Compress -Depth 5
exit 0
