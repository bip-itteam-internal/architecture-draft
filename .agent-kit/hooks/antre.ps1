# antre.ps1 - jalankan satu perintah berat SESUDAH dapat giliran di antrean mesin ini (kit 1.30.0).
#
#   & "<ws>\.claude\hooks\antre.ps1" -- pnpm test
#   powershell -NoProfile -File "<ws>\.claude\hooks\antre.ps1" -- go test ./...
#   & "<ws>\.claude\hooks\antre.ps1" -- "pnpm lint && pnpm build"     (SATU string = lewat cmd /c)
#
# Keluaran perintah diteruskan apa adanya; status antrean ke STDERR supaya tak mencampuri keluaran
# yang diurai (vitest JSON, go test -json). Exit code = exit code perintah.
# Dari agent: jalankan dengan run_in_background: true, karena menunggu giliran bisa melampaui batas
# 10 menit tool. Aturan dan alasannya di antre-lib.ps1.
#
# Sengaja TANPA param(): parameter bernama akan menelan flag milik perintah anak (`-NoProfile`,
# `-C`), jadi seluruh argumen dibaca dari $args.
$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot 'antre-lib.ps1')
$perintah = @($args | ForEach-Object { [string]$_ })
if ($perintah.Count -gt 0 -and $perintah[0] -eq '--') { $perintah = @($perintah | Select-Object -Skip 1) }
if ($perintah.Count -eq 0) {
  [Console]::Error.WriteLine('pakai: antre.ps1 -- <perintah> [argumen...]')
  exit 2
}

$h = Enter-Antre ($perintah -join ' ')
$rc = 1
try {
  if ($perintah.Count -eq 1) {
    & $env:ComSpec /d /s /c $perintah[0]
    $rc = $LASTEXITCODE
  } else {
    # Application saja: pnpm.ps1 menerima array sebagai SATU argumen (vitest lalu cocok nol berkas
    # dan exit 0), jadi pnpm.cmd yang dipakai bila ada.
    $app = Get-Command $perintah[0] -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    $exe = if ($app) { $app.Source } else { $perintah[0] }
    $sisa = @($perintah | Select-Object -Skip 1)
    & $exe @sisa
    $rc = $LASTEXITCODE
  }
} finally { Exit-Antre $h }
if ($null -eq $rc) { $rc = 0 }
exit $rc
