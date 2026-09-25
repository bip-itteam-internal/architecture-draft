# test-antre.ps1 - antrean kerja berat lintas sesi (kit 1.30.0): klasifikasi perintah, hook penolak,
# Mutex per slot dengan PROSES NYATA, dan kunci per langkah di gerbang-lib. Dipanggil test-init.ps1.
#
# Nama Mutex dan folder status dibuat UNIK per run (AGENTKIT_ANTRE_NAMA / AGENTKIT_ANTRE_DIR), supaya
# test ini tidak mengantre di belakang gerbang sesi Claude sungguhan yang sedang berjalan di mesin
# yang sama, dan sebaliknya tidak menahan mereka.
$ErrorActionPreference = 'Stop'
$kitRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$hooks = Join-Path $kitRoot 'hooks'
$tmp = Join-Path $env:TEMP ('agentkit-antre-test-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:AGENTKIT_ANTRE_NAMA = 'agentkit-antre-uji-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
$env:AGENTKIT_ANTRE_DIR = Join-Path $tmp 'antre'
$env:AGENTKIT_ANTRE_INTERVAL = '1'
Remove-Item Env:AGENTKIT_ANTRE_PEGANG -ErrorAction SilentlyContinue
Remove-Item Env:AGENTKIT_ANTRE_SLOT -ErrorAction SilentlyContinue
$fail = 0
function Check($cond, $name) { if ($cond) { Write-Host "PASS $name" } else { Write-Host "FAIL $name"; $script:fail++ } }

$antre = Join-Path $hooks 'antre.ps1'
$gate = Join-Path $hooks 'antre-gate.ps1'

function Start-Pemegang([int]$detik) {
  # pemegang = antre.ps1 yang menjalankan tidur; keluarannya ke berkas supaya tak menggantung pipe
  $o = Join-Path $tmp ('pemegang-' + [guid]::NewGuid().ToString('N') + '.txt')
  $p = Start-Process -FilePath 'powershell' -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $antre + '"'), '--', 'powershell', '-NoProfile', '-Command', ('Start-Sleep ' + $detik)) `
    -RedirectStandardOutput $o -RedirectStandardError ($o + '.err') -NoNewWindow -PassThru
  # tunggu sampai ia benar-benar MEMEGANG (berkas status berkeadaan pegang), bukan sekadar hidup
  $sw = [Diagnostics.Stopwatch]::StartNew()
  while ($sw.Elapsed.TotalSeconds -lt 20) {
    $f = Join-Path $env:AGENTKIT_ANTRE_DIR ([string]$p.Id + '.json')
    if (Test-Path $f) { try { if ((Get-Content $f -Raw | ConvertFrom-Json).keadaan -eq 'pegang') { return $p } } catch {} }
    Start-Sleep -Milliseconds 100
  }
  throw 'pemegang tidak pernah memegang slot dalam 20 detik'
}
function Invoke-Antre([string[]]$argsAntre, [int]$batasDetik = 60) {
  $o = Join-Path $tmp ('antre-' + [guid]::NewGuid().ToString('N') + '.txt')
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $p = Start-Process -FilePath 'powershell' -ArgumentList (@('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $antre + '"'), '--') + $argsAntre) `
    -RedirectStandardOutput $o -RedirectStandardError ($o + '.err') -NoNewWindow -PassThru
  $null = $p.Handle   # PS 5.1: tanpa handle dipegang, ExitCode terbaca null
  $selesai = $p.WaitForExit($batasDetik * 1000)
  if (-not $selesai) { & taskkill /T /F /PID $p.Id 2>&1 | Out-Null }
  $sw.Stop()
  $p.WaitForExit()
  $err = if (Test-Path ($o + '.err')) { Get-Content ($o + '.err') -Raw } else { '' }
  return [pscustomobject]@{ selesai = $selesai; exit = $p.ExitCode; detik = $sw.Elapsed.TotalSeconds; err = [string]$err }
}
function Stop-Pohon($p) { if ($p -and -not $p.HasExited) { & taskkill /T /F /PID $p.Id 2>&1 | Out-Null } }

try {
  . (Join-Path $hooks 'antre-lib.ps1')

  # ---- 1. klasifikasi (fungsi murni) ----
  $kasus = @(
    @('pnpm test', 'penuh'), @('pnpm run test', 'penuh'), @('pnpm build', 'penuh'), @('pnpm tsc', 'penuh'),
    @('pnpm typecheck', 'penuh'), @('pnpm lint', 'penuh'), @('pnpm lint --fix', 'penuh'),
    @('pnpm -C "C:\x y\fe" build', 'penuh'), @('pnpm exec tsc --noEmit', 'penuh'), @('npx vitest run', 'penuh'),
    @('pnpm vitest run', 'penuh'), @('pnpm exec vitest run --reporter=json --outputFile="C:\t\a.json"', 'penuh'),
    @('pnpm exec vitest run --reporter json', 'penuh'), @('next build', 'penuh'), @('tsc --noEmit', 'penuh'),
    @('eslint ./src', 'penuh'), @('go test ./... -json -count=1', 'penuh'), @('go build ./...', 'penuh'),
    @('flutter test', 'penuh'), @('flutter test --machine', 'penuh'),
    @('cd "C:\wt\fe"; pnpm build', 'penuh'), @('Set-Location x && pnpm test 2>&1 | Select-Object -Last 20', 'penuh'),
    @('pnpm test > out.txt', 'penuh'),
    @('pnpm vitest run src/a.test.tsx', 'tertarget'), @('pnpm vitest run "src/app/(main)/x.test.tsx"', 'tertarget'),
    @('pnpm test -- src/a.test.tsx', 'tertarget'), @('pnpm exec eslint src/a.tsx', 'tertarget'),
    @('go test ./internal/kpi', 'tertarget'), @('go build .', 'tertarget'), @('flutter test test/a_test.dart', 'tertarget'),
    @('git commit -m "jalankan pnpm test dulu"', 'bukan'), @("Select-String -Pattern 'go test' -Path x", 'bukan'),
    @('pnpm install', 'bukan'), @('pnpm dev', 'bukan'), @('git status', 'bukan'), @('', 'bukan'),
    @("git commit -m @'`npnpm build gagal`n'@", 'bukan'), @('echo pnpm build', 'bukan')
  )
  foreach ($k in $kasus) {
    $h = Get-KelasPerintah $k[0]
    Check ($h -eq $k[1]) ("kelas [{0}] = {1} (dapat {2})" -f ($k[0] -replace "`n", '\n'), $k[1], $h)
  }

  # ---- 2. hook penolak ----
  function Invoke-Gate([string]$cmd, [string]$tool = 'PowerShell') {
    $in = Join-Path $tmp ('in-' + [guid]::NewGuid().ToString('N') + '.json')
    $er = $in + '.err'
    [IO.File]::WriteAllText($in, (@{ tool_name = $tool; tool_input = @{ command = $cmd }; cwd = $tmp } | ConvertTo-Json -Compress))
    $p = Start-Process -FilePath 'powershell' -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $gate + '"')) `
      -RedirectStandardInput $in -RedirectStandardOutput ($in + '.out') -RedirectStandardError $er -NoNewWindow -Wait -PassThru
    return [pscustomobject]@{ exit = $p.ExitCode; err = [string](Get-Content $er -Raw -ErrorAction SilentlyContinue) }
  }
  $g = Invoke-Gate 'pnpm test'
  Check ($g.exit -eq 2) "hook: run penuh polos DITOLAK exit 2 (dapat $($g.exit))"
  Check ($g.err -like ('*' + $antre + '*')) 'hook: pesan memuat path ABSOLUT antre.ps1'
  Check ($g.err -match 'run_in_background') 'hook: pesan menyuruh run_in_background'
  Check ($g.err -match 'AGENTKIT_ANTRE_LEWATI') 'hook: pesan menyebut jalan keluar sadar'
  Check ((Invoke-Gate ('& "' + $antre + '" -- pnpm test')).exit -eq 0) 'hook: yang sudah lewat antre.ps1 lolos'
  Check ((Invoke-Gate ('& ' + ($antre -replace ' ', '` ') + ' -- pnpm test')).exit -eq 0) 'hook: antre.ps1 tanpa kutip juga lolos'
  Check ((Invoke-Gate ('powershell -NoProfile -File "' + $antre + '" -- go test ./...') 'Bash').exit -eq 0) 'hook: bentuk Bash lewat powershell -File antre.ps1 lolos'
  Check ((Invoke-Gate 'Get-Content .claude\hooks\antre.ps1; pnpm build').exit -eq 2) 'hook: menyebut antre.ps1 TIDAK meloloskan run penuh di segmen lain'
  Check ((Invoke-Gate 'pnpm vitest run src/a.test.tsx').exit -eq 0) 'hook: test tertarget lolos'
  Check ((Invoke-Gate '$env:AGENTKIT_ANTRE_LEWATI=1; pnpm build').exit -eq 0) 'hook: AGENTKIT_ANTRE_LEWATI=1 lolos'
  Check ((Invoke-Gate 'git commit -m "pnpm test hijau"').exit -eq 0) 'hook: teks di pesan commit TIDAK ditolak'
  Check ((Invoke-Gate 'go test ./...' 'Bash').exit -eq 2) 'hook: tool Bash ikut ditolak'

  # ---- 3. Mutex dengan proses nyata ----
  $r = Invoke-Antre @('cmd', '/d', '/c', 'exit 3')
  Check ($r.selesai -and $r.exit -eq 3) "antre: exit code anak diteruskan (dapat $($r.exit))"

  $a = Start-Pemegang 5
  try {
    $r = Invoke-Antre @('cmd', '/d', '/c', 'exit 0')
    Check ($r.selesai -and $r.exit -eq 0) 'antre: penunggu akhirnya jalan'
    Check ($r.detik -ge 2.5) ("antre: penunggu MENUNGGU pemegang ({0:N1} dtk)" -f $r.detik)
    Check ($r.err -match 'menunggu') 'antre: penunggu mencetak status menunggu'
    Check ($r.err -match [string]$a.Id) 'antre: status menunggu menyebut PID pemegang'
  } finally { Stop-Pohon $a }

  $a = Start-Pemegang 120
  $sw = [Diagnostics.Stopwatch]::StartNew()
  Start-Sleep -Milliseconds 500
  Stop-Process -Id $a.Id -Force   # pemegang mati TANPA melepas: Mutex jadi abandoned
  $r = Invoke-Antre @('cmd', '/d', '/c', 'exit 0') 30
  Check ($r.selesai -and $r.exit -eq 0 -and $r.detik -lt 15) ("antre: slot pemegang yang di-kill diambil alih ({0:N1} dtk)" -f $r.detik)
  Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -like '*Start-Sleep 120*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

  $r = Invoke-Antre @('powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $antre + '"'), '--', 'cmd', '/d', '/c', 'exit 0') 30
  Check ($r.selesai -and $r.exit -eq 0) 'antre: antre bersarang tidak deadlock'

  $env:AGENTKIT_ANTRE_SLOT = '2'
  $a = Start-Pemegang 8
  try {
    $r = Invoke-Antre @('cmd', '/d', '/c', 'exit 0')
    Check ($r.selesai -and $r.detik -lt 5) ("antre: 2 slot, penunggu kedua langsung jalan ({0:N1} dtk)" -f $r.detik)
  } finally { Stop-Pohon $a; $env:AGENTKIT_ANTRE_SLOT = '1' }

  # papan-sesi menampilkan pemegang yang HIDUP (dan tidak menampilkan bagian antrean saat kosong)
  $papan = Join-Path $hooks 'papan-sesi.ps1'
  $a = Start-Pemegang 20
  try {
    $o = Join-Path $tmp 'papan.txt'
    Start-Process -FilePath 'powershell' -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $papan + '"'), '-Workspace', ('"' + $tmp + '"'), '-TanpaHtml') `
      -RedirectStandardOutput $o -RedirectStandardError ($o + '.err') -NoNewWindow -Wait | Out-Null
    $txt = Get-Content $o -Raw
    Check ($txt -match 'ANTREAN KERJA BERAT' -and $txt -match 'PEGANG' -and $txt -match [string]$a.Id) 'papan-sesi: pemegang hidup tampil di bagian antrean'
  } finally { Stop-Pohon $a }
  Start-Sleep -Milliseconds 500
  Start-Process -FilePath 'powershell' -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $papan + '"'), '-Workspace', ('"' + $tmp + '"'), '-TanpaHtml') `
    -RedirectStandardOutput $o -RedirectStandardError ($o + '.err') -NoNewWindow -Wait | Out-Null
  Check ((Get-Content $o -Raw) -notmatch 'ANTREAN KERJA BERAT') 'papan-sesi: pemegang yang di-kill tidak tampil lagi'

  # berkas status milik PID mati tidak terbaca sebagai pemegang/penunggu
  New-Item -ItemType Directory -Force -Path $env:AGENTKIT_ANTRE_DIR | Out-Null
  [IO.File]::WriteAllText((Join-Path $env:AGENTKIT_ANTRE_DIR '999999.json'), '{"pid":999999,"keadaan":"pegang","perintah":"hantu"}')
  Check (@(Get-AntreStatus | Where-Object { $_.pid -eq 999999 }).Count -eq 0) 'status: PID mati dibuang'

  # ---- 4. kunci per langkah di gerbang-lib ----
  . (Join-Path $hooks 'gerbang-lib.ps1')
  $a = Start-Pemegang 4
  try {
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $g = Invoke-Gerbang 'uji' $tmp 'cmd /d /c exit 0'
    $sw.Stop()
    Check ($sw.Elapsed.TotalSeconds -ge 2) ("Invoke-Gerbang menunggu slot ({0:N1} dtk)" -f $sw.Elapsed.TotalSeconds)
    Check ($g.lolos) 'Invoke-Gerbang tetap lolos sesudah menunggu'
    Check ($g.durasi_detik -lt 2) ("Invoke-Gerbang: durasi_detik tidak memuat waktu antre ({0})" -f $g.durasi_detik)
  } finally { Stop-Pohon $a }
  $a = Start-Pemegang 5
  try {
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $g = Invoke-GerbangBatas 'uji' $tmp 'ping -n 2 127.0.0.1 >nul' 3
    $sw.Stop()
    Check ($sw.Elapsed.TotalSeconds -ge 2.5) ("Invoke-GerbangBatas menunggu slot ({0:N1} dtk)" -f $sw.Elapsed.TotalSeconds)
    Check ($g.lolos) "Invoke-GerbangBatas: waktu antre TIDAK dihitung ke batas 3 dtk (exit $($g.exit))"
  } finally { Stop-Pohon $a }
  Check (-not $env:AGENTKIT_ANTRE_PEGANG) 'gerbang-lib: env pemegang dibersihkan sesudah langkah'

  # ---- 5. pre-push: pnpm tsc/lint/build lewat antre (push SUNGGUHAN ke remote bare sandbox) ----
  # pnpm palsu mencatat AGENTKIT_ANTRE_PEGANG: env itu hanya dipasang pemegang slot, jadi isinya
  # PID membuktikan perintahnya dijalankan di dalam antrean, bukan sekadar lolos.
  $bin = Join-Path $tmp 'bin'; New-Item -ItemType Directory -Force -Path $bin | Out-Null
  $tanda = Join-Path $tmp 'tanda-pnpm.txt'
  [IO.File]::WriteAllText((Join-Path $bin 'pnpm.cmd'), "@echo %1 pegang=%AGENTKIT_ANTRE_PEGANG%>> `"$tanda`"`r`n@exit /b 0`r`n")
  # kembaran untuk sh: tanpa ini kontrol negatif (pre-push tanpa antre) memanggil pnpm ASLI dan
  # merah karena sebab lain, bukan pada assertion "di dalam antrean" (terukur saat menulis test ini)
  $tandaSh = $tanda -replace '\\', '/'   # sh Git for Windows menerima C:/...
  [IO.File]::WriteAllText((Join-Path $bin 'pnpm'), "#!/bin/sh`necho `"`$1 pegang=`$AGENTKIT_ANTRE_PEGANG`" >> `"$tandaSh`"`nexit 0`n")
  # stderr git (peringatan CRLF) jadi ErrorRecord di PS 5.1 dan menghentikan test ber-Stop
  function G { $ErrorActionPreference = 'Continue'; & git @args 2>&1 | Out-Null }
  $bare = Join-Path $tmp 'remote.git'; $kerja = Join-Path $tmp 'kerja'
  G init -q --bare $bare
  G init -q -b main $kerja
  [IO.File]::WriteAllText((Join-Path $kerja 'package.json'), '{"scripts":{"tsc":"tsc","lint":"eslint","build":"next build"}}')
  [IO.File]::WriteAllText((Join-Path $kerja 'pnpm-lock.yaml'), "lockfileVersion: '9.0'`n")
  G -C $kerja -c core.fsmonitor=false add -A
  G -C $kerja -c core.fsmonitor=false -c user.email=uji@contoh -c user.name=uji commit -q -m awal
  G -C $kerja remote add origin $bare
  G -C $kerja config core.hooksPath ((Join-Path $hooks 'githooks') -replace '\\', '/')
  $pathLama = $env:PATH
  try {
    $env:PATH = $bin + ';' + $env:PATH
    $pushOut = Join-Path $tmp 'push.txt'
    $pp = Start-Process -FilePath 'git' -ArgumentList @('-C', ('"' + $kerja + '"'), '-c', 'core.fsmonitor=false', 'push', '-q', 'origin', 'main') `
      -RedirectStandardOutput $pushOut -RedirectStandardError ($pushOut + '.err') -NoNewWindow -PassThru
    $null = $pp.Handle
    $pp.WaitForExit(120000) | Out-Null
  } finally { $env:PATH = $pathLama }
  $baris = @(if (Test-Path $tanda) { Get-Content $tanda })
  Check ($pp.ExitCode -eq 0) ("pre-push: push sandbox lolos (exit {0}) {1}" -f $pp.ExitCode, (Get-Content ($pushOut + '.err') -Raw -ErrorAction SilentlyContinue))
  Check ($baris.Count -eq 3) ("pre-push: pnpm palsu dipanggil 3x (tsc, lint, build), dapat {0}" -f $baris.Count)
  Check (@($baris | Where-Object { $_ -match 'pegang=\d+\s*$' }).Count -eq 3) ("pre-push: SETIAP pnpm berjalan di dalam antrean: {0}" -f ($baris -join ' | '))
}
finally {
  if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue }
}
if ($fail -gt 0) { Write-Host "$fail gagal"; exit 1 } else { Write-Host 'Semua lulus'; exit 0 }
