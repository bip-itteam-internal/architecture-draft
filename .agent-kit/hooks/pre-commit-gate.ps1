# pre-commit-gate.ps1 — PreToolUse(Bash|PowerShell): GERBANG commit, bukan pengingat.
#
# MENOLAK `git commit` di branch default (main/master/origin HEAD) sebuah repo KODE.
# Vault architecture-draft dikecualikan: konvensinya memang push langsung ke main.
#
# Menolak lewat EXIT 2, bukan JSON: exit 2 memblokir tool call apa pun isi stdout-nya, jadi
# JSON yang salah bentuk tidak bisa membuat gerbang ini gagal-terbuka (kelas kegagalan yang
# sama dengan matcher `Bash` yang membuat versi lama tak pernah menyala di mesin PowerShell).
# Selain kasus tolak: exit 0 + pengingat, persis perilaku lama.
#
# Yang TIDAK ditangkap, dan disadari: `--no-verify` bukan urusan hook ini (itu hook git);
# commit lewat GUI/terminal di luar Claude Code; path repo yang datang dari variabel yang
# di-assign di perintah LAIN (hanya assignment di perintah yang sama yang dibaca).
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

# `$v="..."; git -C $v commit` — baca assignment di perintah yang sama
$vars = @{}
foreach ($m in [regex]::Matches($cmd, '\$(\w+)\s*=\s*(?:"([^"]*)"|''([^'']*)'')')) {
  $vars[$m.Groups[1].Value] = if ($m.Groups[2].Success) { $m.Groups[2].Value } else { $m.Groups[3].Value }
}

# Periksa SETIAP segmen (`;`, `&&`, `||`, baris baru): `git add .; git commit` tetap kena.
$segments = $cmd -split '(?:;|&&|\|\||\r?\n)'
$repoDir = $null; $isCommit = $false
foreach ($seg in $segments) {
  $tokens = @(Get-Tokens $seg)
  $gi = -1
  for ($i = 0; $i -lt $tokens.Count; $i++) {
    if ($tokens[$i] -match '(^|[\\/])git(\.exe)?$') { $gi = $i; break }
  }
  if ($gi -lt 0) { continue }
  $dir = $null; $sub = $null
  for ($i = $gi + 1; $i -lt $tokens.Count; $i++) {
    $t = $tokens[$i]
    # -ceq (peka huruf): `-eq` PowerShell menyamakan -C dan -c, sehingga `-c core.fsmonitor=false`
    # pernah menimpa path repo dan gerbang ini gagal-terbuka persis di perintah git yang tim pakai
    if ($t -ceq '-C' -and ($i + 1) -lt $tokens.Count) { $dir = $tokens[$i + 1]; $i++; continue }
    if ($t -ceq '-c' -and ($i + 1) -lt $tokens.Count) { $i++; continue }
    if ($t -like '-*') { continue }
    $sub = $t; break   # token non-opsi pertama sesudah git = subperintah
  }
  if ($sub -eq 'commit') { $isCommit = $true; if ($dir) { $repoDir = $dir }; break }
}
if (-not $isCommit) { exit 0 }

if ($repoDir -and $repoDir.StartsWith('$')) {
  $n = $repoDir.TrimStart('$').Trim('{', '}')
  if ($vars.ContainsKey($n)) { $repoDir = $vars[$n] }
}
if (-not $repoDir -or -not (Test-Path $repoDir)) { $repoDir = $cwd }
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
