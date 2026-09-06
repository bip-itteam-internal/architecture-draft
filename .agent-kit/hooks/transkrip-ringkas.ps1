# transkrip-ringkas.ps1 — JSONL sesi Claude Code -> markdown ringkas untuk agen ekstraksi skill.
#
# Skema JSONL dinyatakan INTERNAL dan bisa berubah antar-versi (dok resmi Claude Code), jadi
# skrip ini defensif: hanya membaca `type: user|assistant`, mengabaikan yang lain, dan MENOLAK
# (exit 3) bila kurang dari separuh baris terurai atau tidak ada pasangan user+assistant.
# Ringkasan kosong yang "berhasil" adalah kelas kegagalan 200-berisi-nol; lebih baik gagal jelas.
param(
  [Parameter(Mandatory = $true)][string]$Transkrip,
  [Parameter(Mandatory = $true)][string]$Keluaran,
  [int]$MaksTeks = 1500,
  [int]$MaksInput = 200
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path $Transkrip)) { [Console]::Error.WriteLine("Transkrip tidak ada: $Transkrip"); exit 2 }

function Potong([string]$s, [int]$n) {
  if ($null -eq $s) { return '' }
  $s = ($s -replace '\s+', ' ').Trim()
  if ($s.Length -gt $n) { return ($s.Substring(0, $n) + ' […]') }
  return $s
}

function Ringkas-Content($content, [int]$maksTeks, [int]$maksInput) {
  # content bisa string (prompt ketikan) atau array blok {type: text|tool_use|tool_result}
  $baris = @()
  if ($content -is [string]) { $baris += (Potong $content $maksTeks); return $baris }
  foreach ($b in @($content)) {
    $t = [string]$b.type
    if ($t -eq 'text') { $baris += (Potong ([string]$b.text) $maksTeks) }
    elseif ($t -eq 'tool_use') {
      $arg = @()
      if ($b.input) {
        foreach ($p in $b.input.PSObject.Properties) {
          $v = $p.Value
          if ($v -is [string]) { $arg += ("{0}: {1}" -f $p.Name, (Potong $v $maksInput)) }
          elseif ($null -ne $v) { $arg += ("{0}: {1}" -f $p.Name, (Potong (($v | ConvertTo-Json -Compress -Depth 3)) $maksInput)) }
        }
      }
      $baris += ("- tool: **{0}** {{ {1} }}" -f [string]$b.name, ($arg -join '; '))
    }
    elseif ($t -eq 'tool_result') {
      $isi = $b.content
      $n = 0
      if ($isi -is [string]) { $n = $isi.Length }
      elseif ($isi) { foreach ($c in @($isi)) { if ($c.text) { $n += ([string]$c.text).Length } } }
      $baris += ("- hasil tool ({0} char)" -f $n)
    }
  }
  return $baris
}

$lines = Get-Content $Transkrip -Encoding UTF8
$total = 0; $sah = 0; $u = 0; $a = 0
$sb = New-Object System.Text.StringBuilder
foreach ($l in $lines) {
  if (-not $l.Trim()) { continue }
  $total++
  try { $o = $l | ConvertFrom-Json } catch { continue }
  $sah++
  if ($o.isSidechain -eq $true) { continue }   # subagent: bukan alur utama sesi
  $t = [string]$o.type
  if ($t -ne 'user' -and $t -ne 'assistant') { continue }
  $msg = $o.message
  if ($null -eq $msg) { continue }
  $blok = @(Ringkas-Content $msg.content $MaksTeks $MaksInput)
  if ($blok.Count -eq 0) { continue }
  $ts = [string]$o.timestamp
  if ($t -eq 'user') { $u++; [void]$sb.AppendLine(("### [{0}] USER" -f $ts)) }
  else { $a++; [void]$sb.AppendLine(("### [{0}] ASSISTANT" -f $ts)) }
  foreach ($b in $blok) { [void]$sb.AppendLine($b) }
  [void]$sb.AppendLine()
}

$ratio = if ($total -gt 0) { $sah / $total } else { 0 }
if ($ratio -lt 0.5 -or $u -eq 0 -or $a -eq 0) {
  [Console]::Error.WriteLine(("Transkrip tidak terurai: {0}/{1} baris JSON sah, user={2}, assistant={3}. Skema mungkin berubah. JANGAN memakai ringkasan kosong." -f $sah, $total, $u, $a))
  exit 3
}

$header = @(
  ("# Ringkasan transkrip: {0}" -f (Split-Path $Transkrip -Leaf)),
  ("- Baris: {0}, JSON sah: {1}, giliran user: {2}, giliran assistant: {3}" -f $total, $sah, $u, $a),
  ("- Dibuat: {0} UTC oleh transkrip-ringkas.ps1 (teks dipotong {1} char, argumen tool {2} char)" -f (Get-Date).ToUniversalTime().ToString('s'), $MaksTeks, $MaksInput),
  '',
  '## Alur',
  ''
) -join "`n"
$dir = Split-Path $Keluaran -Parent
if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
$utf8 = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($Keluaran, ($header + "`n" + $sb.ToString()), $utf8)
Write-Host ("OK: {0} giliran user, {1} giliran assistant -> {2}" -f $u, $a, $Keluaran)
exit 0
