# linear-verifikasi.ps1 - cocokkan status issue Linear (tim BHA) dengan PR GitHub yang tertaut.
#
# Dipasang init dari architecture-draft/.agent-kit/hooks (kit 1.32.0); dipanggil /linear-cek.
# Dasar aturan: agent-kit rules/team-memory.md bagian "Linear: status issue mengikuti keadaan ERP".
# Sumber bukti: attachment GitHub di tiap issue (diisi integrasi GitHub Linear; memuat status PR,
# mergedAt). PR yang tak menyebut bha-<n> tak pernah tertaut, jadi "tanpa PR" berarti "tak ada
# bukti", bukan "tak ada kode": sebelum menutup/membuka ulang, ukur ke kode + data prod.
#
# Pakai:
#   .\linear-verifikasi.ps1                 # laporan saja (default, tak menulis apa pun ke Linear)
#   .\linear-verifikasi.ps1 -Terapkan       # pindahkan status HANYA untuk aturan R1 dan R2
#   .\linear-verifikasi.ps1 -HariMacet 21   # ambang aturan R4
#
# Aturan:
#   R1  Backlog/Todo tetapi ada PR terbuka            -> usul In Review (bukti pasti)
#   R2  In Progress/In Review, semua PR merged        -> usul Menunggu Adopsi (bukti pasti)
#   R3  Done tanpa satu pun PR tertaut                -> tandai "Done tanpa bukti kode" (lapor saja)
#   R4  In Progress tanpa PR, tak disentuh > N hari   -> tandai macet (lapor saja)
#   R5  Menunggu Adopsi > 30 hari sejak merge         -> tanya pemilik proses (lapor saja)
#   R6  Lewat tenggat                                 -> daftar (lapor saja)
param(
  [switch]$Terapkan,
  [int]$HariMacet = 14,
  [int]$HariAdopsi = 30,
  [string]$KunciTim = 'BHA',
  [string]$Keluar
)
$ErrorActionPreference = 'Stop'
if (-not $Keluar) {
  # Terpasang di <erp>/.claude/hooks (hasil init) -> akar workspace = dua tingkat di atas.
  # Dijalankan dari sumber kit <erp>/architecture-draft/.agent-kit/hooks -> tiga tingkat.
  $induk = Split-Path -Parent $PSScriptRoot
  $akar = if ((Split-Path -Leaf $induk) -eq '.agent-kit') { Split-Path -Parent (Split-Path -Parent $induk) } else { Split-Path -Parent $induk }
  $Keluar = Join-Path $akar ('.task-plans\linear\verifikasi-' + (Get-Date -Format 'yyyy-MM-dd') + '.md')
}$kunci = $env:LINEAR_API_KEY
if (-not $kunci) { $kunci = [Environment]::GetEnvironmentVariable('LINEAR_API_KEY', 'User') }
if (-not $kunci) { [Console]::Error.WriteLine('LINEAR_API_KEY tidak ada (env proses maupun User).'); exit 2 }

function Kirim([string]$query, $vars) {
  $body = @{ query = $query; variables = $vars } | ConvertTo-Json -Depth 10 -Compress
  $r = Invoke-RestMethod -Uri 'https://api.linear.app/graphql' -Method Post -Headers @{ Authorization = $kunci; 'Content-Type' = 'application/json; charset=utf-8' } -Body ([Text.Encoding]::UTF8.GetBytes($body))
  if ($r.errors) { throw ('GraphQL: ' + ($r.errors | ConvertTo-Json -Depth 5 -Compress)) }
  $r.data
}

$timObj = (Kirim 'query($k:String!){ team(id:$k){ id states { nodes { id name type } } } }' @{ k = $KunciTim }).team
$state = @{}; foreach ($s in $timObj.states.nodes) { $state[$s.name] = $s }
foreach ($wajib in 'In Review', 'Menunggu Adopsi') { if (-not $state.ContainsKey($wajib)) { [Console]::Error.WriteLine("State '$wajib' tidak ada di tim $KunciTim."); exit 2 } }

$q = @'
query($t:ID!, $after:String) {
  issues(first: 100, after: $after, filter: { team: { id: { eq: $t } } }) {
    pageInfo { hasNextPage endCursor }
    nodes { id identifier title dueDate updatedAt state { name type }
      attachments { nodes { sourceType metadata } } }
  }
}
'@
$semua = @(); $after = $null
do {
  $d = Kirim $q @{ t = $timObj.id; after = $after }
  $semua += $d.issues.nodes; $after = $d.issues.pageInfo.endCursor
} while ($d.issues.pageInfo.hasNextPage)

$kini = Get-Date
$temuan = New-Object System.Collections.Generic.List[object]
foreach ($i in $semua) {
  $pr = @($i.attachments.nodes | Where-Object { $_.sourceType -eq 'github' -and $_.metadata.number })
  $terbuka = @($pr | Where-Object { $_.metadata.status -in @('open', 'draft', 'inReview', 'approved') -or (-not $_.metadata.mergedAt -and -not $_.metadata.closedAt) })
  $merged = @($pr | Where-Object { $_.metadata.mergedAt })
  $st = $i.state.name; $tipe = $i.state.type
  $daftarPR = ($pr | ForEach-Object { '{0}#{1}({2})' -f $_.metadata.repoName, $_.metadata.number, $_.metadata.status }) -join ', '
  $tambah = { param($aturan, $usul, $ket) $temuan.Add([pscustomobject]@{ Aturan = $aturan; ID = $i.identifier; Uuid = $i.id; Status = $st; Usul = $usul; Ket = $ket; PR = $daftarPR; Judul = $i.title }) }

  if ($tipe -in @('backlog', 'unstarted') -and $terbuka.Count -gt 0) { & $tambah 'R1' 'In Review' "$($terbuka.Count) PR terbuka" }
  if ($st -in @('In Progress', 'In Review') -and $pr.Count -gt 0 -and $merged.Count -eq $pr.Count) {
    $akhir = ($merged | ForEach-Object { [datetime]$_.metadata.mergedAt } | Sort-Object | Select-Object -Last 1)
    & $tambah 'R2' 'Menunggu Adopsi' ('semua PR merged, terakhir ' + $akhir.ToString('yyyy-MM-dd'))
  }
  if ($tipe -eq 'completed' -and $pr.Count -eq 0) { & $tambah 'R3' '' 'Done tanpa PR tertaut; ukur ke kode sebelum percaya' }
  if ($st -eq 'In Progress' -and $pr.Count -eq 0 -and ($kini - [datetime]$i.updatedAt).TotalDays -gt $HariMacet) { & $tambah 'R4' '' ('tanpa PR, tak disentuh ' + [int]($kini - [datetime]$i.updatedAt).TotalDays + ' hari') }
  if ($st -eq 'Menunggu Adopsi' -and $merged.Count -gt 0) {
    $akhir = ($merged | ForEach-Object { [datetime]$_.metadata.mergedAt } | Sort-Object | Select-Object -Last 1)
    if (($kini - $akhir).TotalDays -gt $HariAdopsi) { & $tambah 'R5' '' ('merged ' + [int]($kini - $akhir).TotalDays + ' hari lalu, belum Done') }
  }
  if ($tipe -notin @('completed', 'canceled', 'duplicate') -and $i.dueDate -and ([datetime]$i.dueDate) -lt $kini.Date) { & $tambah 'R6' '' ('tenggat ' + $i.dueDate) }
}

$ket = @{ R1 = 'Backlog/Todo tapi PR terbuka'; R2 = 'Semua PR merged, masih In Progress/Review'; R3 = 'Done tanpa PR tertaut'; R4 = "In Progress tanpa PR > $HariMacet hari"; R5 = "Menunggu Adopsi > $HariAdopsi hari"; R6 = 'Lewat tenggat' }
$md = New-Object System.Text.StringBuilder
[void]$md.AppendLine("# Verifikasi Linear $KunciTim $(Get-Date -Format 'yyyy-MM-dd HH:mm')")
[void]$md.AppendLine('')
[void]$md.AppendLine("Issue diperiksa: $($semua.Count). Mode: $(if ($Terapkan) { 'TERAPKAN (R1, R2)' } else { 'laporan saja' }).")
[void]$md.AppendLine('Bukti hanya PR yang tertaut ke issue lewat bha-<n>; "tanpa PR" bukan bukti tak ada kode.')
foreach ($a in 'R1', 'R2', 'R3', 'R4', 'R5', 'R6') {
  $g = @($temuan | Where-Object Aturan -eq $a)
  [void]$md.AppendLine(''); [void]$md.AppendLine("## $a $($ket[$a]) ($($g.Count))"); [void]$md.AppendLine('')
  if (-not $g.Count) { [void]$md.AppendLine('(tidak ada)'); continue }
  [void]$md.AppendLine('| Issue | Status | Usul | Keterangan | PR | Judul |'); [void]$md.AppendLine('|---|---|---|---|---|---|')
  foreach ($t in ($g | Sort-Object ID)) { [void]$md.AppendLine("| $($t.ID) | $($t.Status) | $($t.Usul) | $($t.Ket) | $($t.PR) | $(($t.Judul -replace '\|', '/')) |") }
}

if ($Terapkan) {
  [void]$md.AppendLine(''); [void]$md.AppendLine('## Diterapkan'); [void]$md.AppendLine('')
  $m = 'mutation($id:String!,$s:String!){ issueUpdate(id:$id, input:{ stateId:$s }){ success } }'
  foreach ($t in @($temuan | Where-Object { $_.Aturan -in @('R1', 'R2') })) {
    $ok = (Kirim $m @{ id = $t.Uuid; s = $state[$t.Usul].id }).issueUpdate.success
    [void]$md.AppendLine("- $($t.ID): $($t.Status) -> $($t.Usul) ($(if ($ok) { 'ok' } else { 'GAGAL' }))")
  }
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Keluar) | Out-Null
[IO.File]::WriteAllText($Keluar, $md.ToString(), (New-Object Text.UTF8Encoding $false))
foreach ($a in 'R1', 'R2', 'R3', 'R4', 'R5', 'R6') { '{0} {1}: {2}' -f $a, $ket[$a], @($temuan | Where-Object Aturan -eq $a).Count }
"Laporan: $Keluar"
