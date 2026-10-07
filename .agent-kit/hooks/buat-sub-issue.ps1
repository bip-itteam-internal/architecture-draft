# buat-sub-issue.ps1 - pecah issue induk jadi sub-issue per repo (BE / FE / Mobile) di Project #15.
# Dipasang init dari architecture-draft/.agent-kit/hooks (kit 1.34.0); dipanggil /brief langkah 2c.
# Aturan: agent-kit rules/team-memory.md bagian "Backlog: GitHub Project" butir sub-issue.
#
#   & '.claude/hooks/buat-sub-issue.ps1' -Induk bip-erp#2162 -Repo erp-frontend -Judul 'Layar anonim' [-Badan <berkas.md>]
#
# Hasil (stdout, satu baris): <repo>#<nomor> <url>
# Idempoten: bila induk SUDAH punya sub-issue di repo itu dengan awalan yang sama ([BE]/[FE]/[Mobile]),
# yang lama dipakai, tidak dibuat ganda. Sub-issue dimasukkan ke Project #15 dengan Status Backlog,
# Area dan Prioritas disalin dari induk. Satu tingkat saja: induk yang sendirinya sub-issue ditolak.
param(
  [Parameter(Mandatory = $true)][string]$Induk,
  [Parameter(Mandatory = $true)][ValidateSet('bip-erp', 'erp-frontend', 'my-bharata')][string]$Repo,
  [Parameter(Mandatory = $true)][string]$Judul,
  [string]$Badan
)
$ErrorActionPreference = 'Stop'
$ORG = 'bip-itteam-internal'
$NOMOR_PROJECT = 15
$utf8 = New-Object Text.UTF8Encoding $false
$AWALAN = @{ 'bip-erp' = '[BE]'; 'erp-frontend' = '[FE]'; 'my-bharata' = '[Mobile]' }

# PS 5.1: payload lewat BERKAS --input (kutip di argumen dirusak), stderr gh tak boleh jadi galat
# terminasi sebelum kode keluar dibaca.
function GhApi([string[]]$argumen, $obj) {
  $f = $null
  if ($null -ne $obj) {
    $f = Join-Path $env:TEMP ('subisu-' + [guid]::NewGuid().ToString('N') + '.json')
    [IO.File]::WriteAllText($f, ($obj | ConvertTo-Json -Depth 10 -Compress), $utf8)
    $argumen = $argumen + @('--input', $f)
  }
  $ErrorActionPreference = 'Continue'
  $out = & gh @argumen 2>&1; $kode = $LASTEXITCODE
  if ($f) { Remove-Item $f -ErrorAction SilentlyContinue }
  if ($kode -ne 0) { throw "gh $($argumen -join ' ') gagal: $out" }
  $teks = (($out | Where-Object { $_ -is [string] }) -join "`n")
  if ($teks) { $teks | ConvertFrom-Json }
}
function Gql([string]$q, [hashtable]$v) {
  $r = GhApi @('api', 'graphql') @{ query = $q; variables = $v }
  if ($r.errors) { throw ($r.errors | ConvertTo-Json -Depth 5 -Compress) }
  $r.data
}

if ($Induk -notmatch '^([A-Za-z0-9_.-]+)#(\d+)$') { throw "Format -Induk harus <repo>#<nomor>, bukan '$Induk'" }
$repoInduk = $Matches[1]; $noInduk = [int]$Matches[2]
$induk = GhApi @('api', "repos/$ORG/$repoInduk/issues/$noInduk") $null
if ($induk.pull_request) { throw "$Induk adalah PR, bukan issue" }
$indukDariInduk = Gql 'query($o:String!,$r:String!,$n:Int!){ repository(owner:$o,name:$r){ issue(number:$n){ parent { number repository { name } } } } }' @{ o = $ORG; r = $repoInduk; n = $noInduk }
if ($indukDariInduk.repository.issue.parent) { throw "$Induk sendiri sudah sub-issue dari $($indukDariInduk.repository.issue.parent.repository.name)#$($indukDariInduk.repository.issue.parent.number); sub-issue hanya satu tingkat" }

$judulPenuh = "$($AWALAN[$Repo]) $Judul"
# ConvertFrom-Json PS 5.1 mengembalikan array JSON sebagai SATU objek array; diratakan dulu supaya
# Where-Object menyaring per issue, bukan sekaligus (tanpa ini pencocokan mengembalikan semua anak).
$anak = @(GhApi @('api', "repos/$ORG/$repoInduk/issues/$noInduk/sub_issues?per_page=100") $null | ForEach-Object { $_ })
# Cocokkan JUDUL PENUH, bukan cuma awalan: sub saudara "bagian 2/2" di repo yang sama dulu dianggap
# sudah ada (awalan [BE] sama) dan nomor bagian 1/2 dikembalikan diam-diam (review 2026-10-07).
$ada = $anak | Where-Object { $_.repository_url -match "/$Repo$" -and $_.title -eq $judulPenuh } | Select-Object -First 1
if ($ada) { "$Repo#$($ada.number) $($ada.html_url)"; return }

$isiBadan = "Sub-issue dari $ORG/$repoInduk#$noInduk ($($induk.title)).`n`n"
if ($Badan) { $isiBadan += [IO.File]::ReadAllText($Badan, [Text.Encoding]::UTF8) }
$baru = GhApi @('api', "repos/$ORG/$Repo/issues", '--method', 'POST') @{ title = $judulPenuh; body = $isiBadan }
GhApi @('api', "repos/$ORG/$repoInduk/issues/$noInduk/sub_issues", '--method', 'POST') @{ sub_issue_id = [long]$baru.id } | Out-Null

# Project #15: tambah item, Status Backlog, salin Area + Prioritas dari item induk
$proj = (Gql 'query($o:String!,$n:Int!){ organization(login:$o){ projectV2(number:$n){ id fields(first:50){ nodes { ... on ProjectV2SingleSelectField { id name options { id name } } } } } } }' @{ o = $ORG; n = $NOMOR_PROJECT }).organization.projectV2
$item = (Gql 'mutation($p:ID!,$c:ID!){ addProjectV2ItemById(input:{projectId:$p,contentId:$c}){ item { id } } }' @{ p = $proj.id; c = $baru.node_id }).addProjectV2ItemById.item.id
$nilaiInduk = @{}
$itemInduk = Gql 'query($o:String!,$r:String!,$n:Int!){ repository(owner:$o,name:$r){ issue(number:$n){ projectItems(first:10){ nodes { project { id } fieldValues(first:30){ nodes { ... on ProjectV2ItemFieldSingleSelectValue { name field { ... on ProjectV2FieldCommon { name } } } } } } } } } }' @{ o = $ORG; r = $repoInduk; n = $noInduk }
$pi = $itemInduk.repository.issue.projectItems.nodes | Where-Object { $_.project.id -eq $proj.id } | Select-Object -First 1
if ($pi) { foreach ($v in $pi.fieldValues.nodes) { if ($v.field.name) { $nilaiInduk[$v.field.name] = $v.name } } }
foreach ($nama in @('Status', 'Area', 'Prioritas')) {
  $fld = $proj.fields.nodes | Where-Object name -eq $nama | Select-Object -First 1
  $nilai = if ($nama -eq 'Status') { 'Backlog' } else { $nilaiInduk[$nama] }
  if (-not $fld -or -not $nilai) { continue }
  $opsi = ($fld.options | Where-Object name -eq $nilai).id
  if (-not $opsi) { continue }
  Gql 'mutation($p:ID!,$i:ID!,$f:ID!,$o:String!){ updateProjectV2ItemFieldValue(input:{projectId:$p,itemId:$i,fieldId:$f,value:{singleSelectOptionId:$o}}){ projectV2Item { id } } }' @{ p = $proj.id; i = $item; f = $fld.id; o = $opsi } | Out-Null
}
"$Repo#$($baru.number) $($baru.html_url)"
