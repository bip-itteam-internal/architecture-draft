# test-init.ps1 — integrasi: jalankan init di sandbox, assert artefak generate + hook nyata
$ErrorActionPreference = 'Stop'

# ⛔ BERHENTI bila lingkungan git hook masih terwarisi. Test ini membuat repo sandbox di %TEMP%
# lalu menjalankan puluhan perintah git atasnya; `GIT_DIR` MENANG atas penemuan repo, jadi
# `git -C <sandbox>` akan mendarat di repo yang sedang di-push. Terukur 2026-09-21: dua commit
# kosong bertambah di atas branch kerja repo nyata, branch `feat/uji` lahir di sana, HEAD
# berpindah, dan user.email uji tertulis ke config. Yang membersihkan lingkungannya adalah
# hooks/gerbang-kit.py; penjaga ini ada supaya test yang dijalankan tangan dari konteks hook
# berhenti alih-alih mengubah repo orang.
# Yang diperiksa hanya variabel yang MENGALIHKAN repo, index, atau objek. `GIT_EDITOR`,
# `GIT_ASKPASS`, dan kawannya tidak berbahaya dan memang sering terpasang di sesi biasa;
# memblokirnya membuat test menolak jalan di mesin yang sehat. gerbang-kit.py tetap membuang
# SELURUH `GIT_*` sebelum memanggil test, karena di sana tak satu pun dibutuhkan.
$gitBerbahaya = @('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR',
  'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_QUARANTINE_PATH',
  'GIT_PREFIX', 'GIT_NAMESPACE')
$gitWarisan = @($gitBerbahaya | Where-Object { Test-Path ('Env:' + $_) })
if ($gitWarisan.Count -gt 0) {
  Write-Host ("FAIL lingkungan git hook terwarisi (" + ($gitWarisan -join ', ') + "): test-init MENOLAK jalan supaya perintah gitnya tidak mengenai repo nyata.")
  exit 1
}

$kitRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)  # .agent-kit
$tmp = Join-Path $env:TEMP ("agentkit-test-" + [guid]::NewGuid().ToString('N').Substring(0,8))
$fail = 0
function Check($cond, $name) { if ($cond) { Write-Host "PASS $name" } else { Write-Host "FAIL $name"; $script:fail++ } }

# Jalankan skrip hook dengan stdin JSON persis seperti Claude Code, kembalikan exit code.
# stderr ditangkap ke berkas supaya pesan penolakan bisa diperiksa isinya.
function Read-Json([string]$path) {
  if (-not (Test-Path $path)) { return $null }
  try { return (Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json) } catch { return $null }
}
# Start-Process, bukan pipeline/`&`: PS 5.1 membungkus stderr anak jadi ErrorRecord dan dengan
# $ErrorActionPreference='Stop' pesan PENOLAKAN yang benar justru menghentikan test.
function Invoke-Ps([string]$script, [string[]]$argsSkrip, [string]$stdinFile, [string]$errFile) {
  # parameter TIDAK boleh bernama $args: itu variabel otomatis PowerShell, dan menamai parameter
  # begitu membuat daftar argumen kosong tanpa galat (skrip lalu gagal di parameter wajib, exit 1)
  $outFile = [IO.Path]::GetTempFileName()
  if (-not $errFile) { $errFile = [IO.Path]::GetTempFileName() }
  $argList = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $script + '"')) + @($argsSkrip | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } })
  $sp = @{ FilePath = 'powershell'; ArgumentList = $argList; RedirectStandardOutput = $outFile; RedirectStandardError = $errFile; Wait = $true; PassThru = $true; NoNewWindow = $true }
  if ($stdinFile) { $sp['RedirectStandardInput'] = $stdinFile }
  $p = Start-Process @sp
  Remove-Item $outFile -Force -ErrorAction SilentlyContinue
  return $p.ExitCode
}
function Invoke-Hook([string]$script, [hashtable]$stdin, [string]$errFile) {
  $inFile = [IO.Path]::GetTempFileName()
  [IO.File]::WriteAllText($inFile, ($stdin | ConvertTo-Json -Compress -Depth 6))
  $rc = Invoke-Ps $script @() $inFile $errFile
  Remove-Item $inFile -Force -ErrorAction SilentlyContinue
  return $rc
}

try {
  # sandbox: vault tiruan berisi kit nyata (copy) + project tiruan
  $svVault = Join-Path $tmp 'architecture-draft'
  New-Item -ItemType Directory -Force -Path $svVault | Out-Null
  Copy-Item -Path $kitRoot -Destination (Join-Path $svVault '.agent-kit') -Recurse -Force
  Set-Content -Path (Join-Path $svVault 'CLAUDE.md') -Value '# stub vault rulebook' -Encoding UTF8
  git -C $svVault init -q
  $proj = Join-Path $tmp 'demo-proj'; New-Item -ItemType Directory -Force -Path $proj | Out-Null
  git -C $proj init -q
  git -C $proj config user.email 'test@example.invalid'
  git -C $proj config user.name 'test'
  git -C $proj checkout -q -b main
  git -C $proj commit -q --allow-empty -m init

  & (Join-Path $svVault '.agent-kit/init.ps1') -Workspace $tmp -ActiveProject 'demo-proj' -NoPreCommitHook | Out-Null

  $claude = Join-Path $tmp '.claude'
  Check (Test-Path (Join-Path $claude 'commands/start-task.md')) 'commands tersalin'
  Check (Test-Path (Join-Path $claude 'commands/analisa-kebutuhan.md')) 'command /analisa-kebutuhan tersalin'
  # Jumlah command diturunkan dari kit, JANGAN dipatok angka: assertion angka-mati
  # sudah pernah rot diam-diam saat index-vault.md dan skills.md ditambahkan (2026-08-28).
  $srcCmd = (Get-ChildItem (Join-Path $kitRoot 'commands') -Filter *.md).Count
  $cmdCount = (Get-ChildItem (Join-Path $claude 'commands') -Filter *.md).Count
  Check ($cmdCount -eq $srcCmd) "semua command kit tersalin ($cmdCount/$srcCmd berkas)"

  # Triase (kit 1.28.0): aturan pemicu di team-memory.md. `rules/` TIDAK disalin init
  # (init.ps1 tak punya cabang rules), jadi assert dibaca dari SUMBER kit, bukan dari $claude.
  $tmPath = Join-Path $kitRoot 'rules/team-memory.md'
  $tmIsi = Get-Content $tmPath -Raw -Encoding UTF8
  $judulTriase = '## Triase task: keputusan dulu, atau langsung brief'
  Check ($tmIsi -like "*$judulTriase*") 'team-memory punya bagian triase'

  # Anggaran 8 baris tak-kosong. Bukan gaya: berkas ini auto-load tiap sesi, jadi blok yang
  # membengkak dibayar berulang oleh SETIAP sesi. Tanpa penjaga, ia pasti tumbuh.
  $barisTm = Get-Content $tmPath -Encoding UTF8
  $iAwal = [array]::IndexOf($barisTm, $judulTriase)
  $iAkhir = -1
  if ($iAwal -ge 0) {
    for ($i = $iAwal + 1; $i -lt $barisTm.Count; $i++) {
      if ($barisTm[$i] -like '## *') { $iAkhir = $i; break }
    }
    if ($iAkhir -lt 0) { $iAkhir = $barisTm.Count }
  }
  $isiTriase = if ($iAwal -ge 0) { @($barisTm[$iAwal..($iAkhir - 1)] | Where-Object { $_.Trim() -ne '' }) } else { @() }
  Check ($isiTriase.Count -ge 1 -and $isiTriase.Count -le 8) "blok triase $($isiTriase.Count) baris tak-kosong (batas 8)"

  # Langkah 0 triase harus ikut TERSALIN init, bukan cuma ada di sumber kit.
  # Nama $stTriase, BUKAN $st: $st sudah dipakai di bawah untuk isi settings.json. Sisipan ini
  # kebetulan berada di atasnya sehingga urutannya selamat, tapi itu bergantung pada posisi --
  # memindahkan blok ini ke bawah akan menimpa objek settings tanpa satu pun galat.
  $stTriase = Get-Content (Join-Path $claude 'commands/start-task.md') -Raw -Encoding UTF8
  Check ($stTriase -like '*## 0. Triase*') 'start-task punya langkah 0 triase'
  # .Contains, BUKAN -like: backtick adalah karakter ESCAPE di pola wildcard PowerShell, jadi
  # '*`yakin`*' terurai jadi "yakin" diikuti tanda bintang HARFIAH dan tak akan pernah cocok.
  Check ($stTriase.Contains('`yakin`') -and $stTriase.Contains('`ragu`')) 'start-task menyebut tingkat yakin dan ragu'

  # Field `Sumber` sudah ada di templates/brief.md sejak lama; yang dijaga di sini ARTINYA.
  # Frasa 'turun ke `ragu`' sengaja spesifik: assertion atas kata 'Sumber' saja akan hijau
  # untuk implementasi apa pun begitu kata itu muncul di kalimat lain, dan jadi vakum.
  $bfTriase = Get-Content (Join-Path $claude 'commands/brief.md') -Raw -Encoding UTF8
  Check ($bfTriase.Contains('`Sumber`') -and $bfTriase.Contains('turun ke `ragu`')) 'brief memberi arti Sumber dan aturan turun ke ragu'

  # Grounding graf kode (2026-09-23): langkah 4 brief.md dulu menyuruh "satu dua Grep" saja,
  # bertentangan dengan protokol SessionStart yang mewajibkan codebase-memory-mcp lebih dulu
  # untuk eksplorasi kode. .Contains, BUKAN -like (backtick = escape di wildcard, lihat catatan
  # di atas). Dua klaim wajib benar BERSAMA: alatnya (search_graph) DAN kewajiban menuliskan
  # kesegaran graf ke Konteks -- bukan gerbang wajib yang memblokir (lihat Batas brief tugas ini).
  Check ($bfTriase.Contains('search_graph') -and $bfTriase.Contains('kesegaran graf')) 'brief grounding menyebut search_graph dan kewajiban kesegaran graf'

  # Log .task-plans/judge/<slug>-<n>.json ditulis /kerjakan Sec.3, BUKAN /judge (yang hanya
  # menulis <slug>-gerbang.json dan <slug>-diff.patch). Menyunting judge.md tak berpengaruh apa pun.
  $kjTriase = Get-Content (Join-Path $claude 'commands/kerjakan.md') -Raw -Encoding UTF8
  Check ($kjTriase.Contains('keputusan_lanjut')) 'kerjakan mencatat keputusan_lanjut di log judge'
  Check ($kjTriase.Contains('Dasar keputusan')) 'badan PR menyebut dasar keputusan'

  # brief 2026-09-23 (ui-checklist-ke-judge): agen judge tak pernah diberi rules/ui-checklist.md,
  # jadi kriteria UX (lima keadaan layar, umpan balik aksi, satu aksi utama per area, token+gelap,
  # responsif, aksesibilitas) tak pernah dinilai -- hanya eksekutor (loop-fe.md) yang membacanya.
  # .Contains, BUKAN -like (backtick = escape di wildcard, lihat catatan di atas).
  $jdMd = Get-Content (Join-Path $claude 'commands/judge.md') -Raw -Encoding UTF8
  Check ($jdMd.Contains('ui-checklist.md')) 'judge.md merujuk ui-checklist.md di prompt agen judge'
  # Rujukannya wajib BERSYARAT (hanya saat diff menyentuh layar): mengirimnya tanpa syarat
  # membakar konteks brief backend/docs yang tak punya layar sama sekali (Batas brief).
  Check ($jdMd.Contains('menyentuh berkas layar')) 'rujukan ui-checklist.md bersyarat pada diff berlayar, bukan tanpa syarat'

  # brief 2026-09-23 (alur-pengguna-di-brief): /plan, /review, dan /wrap sudah menuntut dan
  # menggerbang '## Alur Pengguna', tapi /brief -- satu-satunya pintu ke loop OTONOM -- tak
  # pernah menuntutnya, jadi celah itu justru lebih lebar di loop daripada di jalur manual.
  # templates/ TIDAK disalin init (sama seperti rules/, lihat catatan team-memory di atas),
  # jadi dibaca dari SUMBER kit, bukan dari $claude.
  $tplBrief = Get-Content (Join-Path $kitRoot 'templates/brief.md') -Raw -Encoding UTF8
  Check ($tplBrief.Contains('## Alur Pengguna (WAJIB bila brief menyentuh layar') -and $tplBrief.Contains('hapus bagian ini bila brief tidak menyentuh layar')) 'templates/brief.md: bagian Alur Pengguna bersyarat, pola sama dengan Kontrak'

  # commands/brief.md wajib mendefinisikan KAPAN bagian itu wajib (brief menyentuh layar) DAN
  # apa ISINYA (langkah orang + titik putus), merujuk plan-checklist.md -- BUKAN menyalin tabel
  # tiga-bentuk-putusnya ke sini (Batas brief tugas ini). $bfTriase sudah dibaca di atas (baris
  # 'Field `Sumber`...'), dipakai ulang di sini.
  Check ($bfTriase.Contains('Alur Pengguna') -and $bfTriase.Contains('menyentuh layar')) 'brief.md: mendefinisikan KAPAN Alur Pengguna wajib (brief menyentuh layar)'
  Check ($bfTriase.Contains('langkah orang, bukan aliran data, dengan titik putusnya ditandai') -and $bfTriase.Contains('plan-checklist.md')) 'brief.md: mendefinisikan ISI Alur Pengguna (langkah orang + titik putus) dan merujuk plan-checklist.md, bukan menyalin'

  # --- Sambungan antar-berkas, temuan review akhir 1.28.0 ---
  # Kelas yang sama untuk kelimanya: tiap berkas benar sendiri-sendiri, yang salah sambungannya.

  # Baris 'Flow wajib' disuntikkan hook SessionStart ke SETIAP sesi sebagai baris PERTAMA, dan
  # kata 'wajib' membantah pemicu triase yang baru dipasang di team-memory.md. Paritas .ps1/.sh
  # dijaga: mengubah satu sisi saja membuat jalur mac/linux menyimpang diam-diam.
  $ssPs = Get-Content (Join-Path $claude 'hooks/session-start.ps1') -Raw -Encoding UTF8
  $ssSh = Get-Content (Join-Path $claude 'hooks/session-start.sh') -Raw -Encoding UTF8
  $cmGen = Get-Content (Join-Path $claude 'CLAUDE.md') -Raw -Encoding UTF8
  Check ($ssPs.Contains('triase')) 'session-start.ps1 mengkualifikasi flow wajib dengan triase'
  Check ($ssSh.Contains('triase')) 'session-start.sh mengkualifikasi flow wajib dengan triase (paritas)'
  Check ($cmGen.Contains('triase')) 'CLAUDE.md hasil generate menyebut triase'

  # /kerjakan <teks bebas> menjalankan prosedur /brief lalu LANJUT tanpa syarat, sehingga brief
  # ber-Sumber kosong melewati gerbang ragu yang baru dibuat brief.md.
  Check ($kjTriase.Contains('brief `ragu` berhenti')) 'kerjakan: teks bebas yang jadi brief ragu berhenti'

  # keputusan_lanjut tanpa aturan nilai cuma niat: buktinya ("ulangi tanpa pasangan log
  # percobaan berikutnya = run terputus") runtuh bila nilainya tidak dipetakan ke keadaan.
  Check ($kjTriase.Contains('`berhenti_lolos` bila')) 'kerjakan memetakan nilai keputusan_lanjut ke keadaan'

  # Jalur vault (domain docs) push langsung ke main TANPA PR, jadi 'Dasar keputusan' yang cuma
  # ada di badan gh pr create tak pernah terbit untuk brief docs.
  $nDasar = ([regex]::Matches($kjTriase, 'Dasar keputusan')).Count
  Check ($nDasar -ge 2) "kerjakan menulis Dasar keputusan di jalur PR DAN vault ($nDasar tempat)"

  # brief 2026-09-23 (prompt-eksekutor-file-line): eksekutor melaporkan membaca berkas UTUH
  # (mis. test-init.ps1 581 baris) padahal brief sudah memuat rentang file:line relevan di
  # bagian Konteks -- orkestrator yang mengukurnya sendiri sebelum menulis brief. §2 sekarang
  # wajib meneruskan titik mulai itu ke prompt eksekutor. Dua fakta terpisah, dua assertion:
  # (a) daftar isi prompt WAJIB punya satu baris anchor file:line dari Konteks brief,
  # (b) teksnya eksplisit bilang anchor itu titik mulai, bukan pagar (eksekutor tetap boleh
  # membaca lebih luas). $kjTriase sudah dibaca di atas (baris 'keputusan_lanjut'), dipakai ulang.
  Check ($kjTriase.Contains('Titik mulai (file:line yang sudah diketahui dari bagian Konteks brief')) 'kerjakan §2: daftar prompt WAJIB membawa titik mulai file:line dari Konteks brief'
  # Frasa 'titik mulai, bukan pagar' DAN 'tetap boleh membaca' wajib berdiri BERSAMA: menghapus
  # klausa "bukan pagar" saja (tanpa menyentuh baris anchor di atas) harus menjatuhkan assertion
  # ini sendirian, tanpa ikut menjatuhkan assertion anchor di atasnya -- itu bukti keduanya
  # tidak vakum satu sama lain (lihat laporan kontrol negatif eksekutor).
  Check ($kjTriase.Contains('titik mulai, bukan pagar') -and $kjTriase.Contains('tetap boleh membaca')) 'kerjakan §2: eksplisit anchor cuma titik mulai (bukan pagar), eksekutor tetap boleh membaca lebih luas'

  # brief 2026-09-23 (log-judge-catat-anchor): kriteria "(orang)" milik brief prompt-eksekutor
  # (41771a89) tak bisa ditafsirkan -- log judge mencatat skills_dibaca/agen/keputusan_lanjut tapi
  # TIDAK anchor yang benar-benar dikirim ke prompt §2, jadi token antar-run tak bisa dipisahkan
  # antara run yang membawa anchor nyata dan run yang fieldnya kosong. Dua fakta terpisah, dua
  # assertion: (a) skema §3 memuat field titik_mulai berisi anchor apa adanya atau literal
  # "kosong", (b) teksnya eksplisit field ini DESKRIPTIF bukan gerbang -- anchor kosong bukan
  # kegagalan dan tidak menahan apa pun, karena brief tanpa file:line di Konteksnya itu SAH
  # (brief.md:51, "Konteks kosong lebih jujur daripada Konteks karangan"). $kjTriase sudah dibaca
  # di atas (baris 'keputusan_lanjut'), dipakai ulang -- BUKAN variabel baru (lihat catatan nama
  # variabel di brief tugas ini).
  Check ($kjTriase.Contains('"titik_mulai"') -and $kjTriase.Contains('| "kosong" }')) 'kerjakan §3: skema log memuat titik_mulai (anchor apa adanya atau literal "kosong")'
  # Assertion terpisah dari yang di atas: field bisa ada TANPA teksnya bilang ia deskriptif,
  # bukan gerbang -- dua klausa itu wajib bisa gagal SENDIRI-SENDIRI (kontrol negatif di laporan).
  Check ($kjTriase.Contains('deskriptif, bukan gerbang') -and $kjTriase.Contains('bukan kegagalan')) 'kerjakan §3: titik_mulai eksplisit deskriptif bukan gerbang, kosong bukan kegagalan'

  # brief 2026-09-25 (loop-pakai-graf-kode): diukur nol panggilan codebase-memory-mcp di seluruh
  # transkrip sesi/subagent, padahal brief.md langkah 4 sudah lama mewajibkan search_graph/
  # trace_path untuk ORKESTRATOR yang menulis brief -- kewajiban itu tak pernah turun ke agen yang
  # benar-benar menyentuh kode saat /kerjakan berjalan. Dua fakta wajib naik BERSAMA ke tiap agen
  # eksekutor lapisan kode DAN ke kerjakan.md sendiri: (a) alatnya (search_graph/trace_path),
  # (b) kewajiban menuliskan KESEGARAN graf yang dipakai ke laporan. .Contains, BUKAN -like
  # (backtick = escape di wildcard, lihat catatan test lain di berkas ini). Bukan gerbang wajib
  # yang memblokir loop (Batas brief ini: MCP mati/basi turun ke git grep, bukan berhenti) --
  # itu diperiksa lewat prosa "bukan alasan berhenti" di §1b, bukan lewat assertion di sini.
  $agenEksekutorKode = @('loop-be', 'loop-fe', 'loop-mobile', 'loop-fix', 'loop-refactor', 'loop-test')
  foreach ($nmAg in $agenEksekutorKode) {
    $pAg = Join-Path $claude ('agents/' + $nmAg + '.md')
    $isiAg = Get-Content $pAg -Raw -Encoding UTF8
    Check ($isiAg.Contains('search_graph') -and $isiAg.Contains('kesegaran graf')) "agents/$nmAg.md menyebut search_graph dan kewajiban kesegaran graf"
  }
  # loop-judge (read-only, tanpa MCP) dan loop-docs/loop-devops (di luar lingkup brief ini)
  # SENGAJA tidak diperiksa -- lihat Batas brief 2026-09-25 dan §0 kerjakan.md (peta eksekutor).
  Check ($kjTriase.Contains('search_graph') -and $kjTriase.Contains('kesegaran graf')) 'kerjakan.md menyebut search_graph dan kewajiban kesegaran graf'
  # Kriteria lolos brief #2: TIDAK ADA jalur dispatch tanpa nama project ATAU catatan
  # ketidaktersediaan. Diperiksa lewat frasa eksplisit "tidak ada jalur" (bukan cuma dua fakta
  # berdiri sendiri-sendiri, yang bisa hijau untuk prosedur yang punya jalur ketiga tak tertulis).
  Check ($kjTriase.Contains('Tidak ada jalur ketiga') -and $kjTriase.Contains('tidak ada jalur di mana eksekutor')) 'kerjakan.md: §1b/§2 eksplisit tidak ada jalur dispatch tanpa graf ATAU catatan ketidaktersediaan'

  # Langkah 0 menuntut resolusi sumber 'dengan perintah' tapi prosedur pencariannya hanya
  # dirujuk di langkah 2, yang justru dilewati saat task dialihkan ke brief.
  $iLangkah = $stTriase.IndexOf('Langkah:')
  $iVaultRet = $stTriase.IndexOf('vault-retrieval')
  Check ($iVaultRet -ge 0 -and $iVaultRet -lt $iLangkah) 'start-task langkah 0 menunjuk vault-retrieval'

  # Assertion keberadaan saja tidak menjaga URUTAN: memindahkan blok triase ke bawah tetap
  # hijau sementara sifat "berhenti sebelum memuat arsitektur" hilang tanpa gejala.
  $iTriase = $stTriase.IndexOf('## 0. Triase')
  Check ($iTriase -ge 0 -and $iTriase -lt $iLangkah) 'langkah 0 triase berada SEBELUM daftar Langkah'
  Check (Test-Path (Join-Path $claude 'hooks/session-start.ps1')) 'hooks tersalin'
  Check (Test-Path (Join-Path $claude 'settings.json')) 'settings.json ada'
  $cm = Get-Content (Join-Path $claude 'CLAUDE.md') -Raw -Encoding UTF8
  Check ($cm -match 'demo-proj') 'CLAUDE.md memuat project aktif'
  Check ($cm -notmatch '__ACTIVE_PROJECT__') 'placeholder project terisi'
  Check ($cm -notmatch '__KIT_VERSION__') 'placeholder versi terisi'
  $arrow = [char]0x2192
  Check ($cm.Contains($arrow)) 'CLAUDE.md panah utuh (UTF-8 tidak korup)'
  $st = Get-Content (Join-Path $claude 'settings.json') -Raw | ConvertFrom-Json
  Check ($null -ne $st.hooks.SessionStart) 'settings punya SessionStart'
  # 1.30.0: -NoPreCommitHook hanya membuang gerbang COMMIT; gerbang antrean kerja berat tetap ada
  $ptuNo = @($st.hooks.PreToolUse)
  Check (@($ptuNo | Where-Object { @($_.hooks | Where-Object { $_.command -match 'pre-commit-gate' }).Count -gt 0 }).Count -eq 0) 'NoPreCommitHook menghapus gerbang commit dari PreToolUse'
  Check (@($ptuNo | Where-Object { @($_.hooks | Where-Object { $_.command -match 'antre-gate' }).Count -gt 0 }).Count -eq 2) 'NoPreCommitHook TIDAK membuang gerbang antrean (Bash + PowerShell)'
  $kv = (Get-Content (Join-Path $claude '.kit-version') -Raw).Trim()
  $ver = (Get-Content (Join-Path $kitRoot 'VERSION') -Raw).Trim()
  Check ($kv -eq $ver) '.kit-version sama dgn VERSION'

  # ---- v1.15.0: agents, githooks, hooksPath, folder sesi, hook sesi ----
  $srcAg = (Get-ChildItem (Join-Path $kitRoot 'agents') -Filter *.md -ErrorAction SilentlyContinue).Count
  $agCount = (Get-ChildItem (Join-Path $claude 'agents') -Filter *.md -ErrorAction SilentlyContinue).Count
  Check ($srcAg -gt 0 -and $agCount -eq $srcAg) "semua agen kit tersalin ($agCount/$srcAg berkas)"
  Check (Test-Path (Join-Path $claude 'hooks/githooks/pre-push')) 'githooks/pre-push tersalin'
  $hpExpected = (Join-Path $claude 'hooks\githooks')
  $hp = (git -C $proj config --get core.hooksPath)
  Check ($hp -eq $hpExpected) "core.hooksPath demo-proj = githooks kit"
  Check (Test-Path (Join-Path $tmp '.task-plans/sesi')) '.task-plans/sesi dibuat init'
  Check (Test-Path (Join-Path $tmp '.task-plans/briefs')) '.task-plans/briefs dibuat init'
  Check ($null -ne $st.hooks.UserPromptSubmit) 'settings punya UserPromptSubmit (walau NoPreCommitHook)'
  Check ($null -ne $st.hooks.SessionEnd) 'settings punya SessionEnd (walau NoPreCommitHook)'

  # ---- v1.24.0: peran per lapisan tim IT ----
  # Penjaga peta peran. Tiap agen kit WAJIB punya entri di PERAN (hooks/kantor-agent.py), kalau tidak
  # robotnya tampil di Kantor Agent sebagai nama mentah `loop-xxx`. Gagalnya senyap dan kosmetik,
  # jadi ia hanya tertangkap oleh penjaga seperti ini, bukan oleh mata.
  $peranPy = Get-Content (Join-Path $kitRoot 'hooks/kantor-agent.py') -Raw -Encoding UTF8
  $blokPeran = [regex]::Match($peranPy, '(?s)PERAN\s*=\s*\{(.*?)\}').Groups[1].Value
  $tanpaPeran = @(Get-ChildItem (Join-Path $kitRoot 'agents') -Filter *.md |
    Where-Object { $blokPeran -notmatch ('"' + [regex]::Escape($_.BaseName) + '"') } |
    ForEach-Object { $_.BaseName })
  Check ($blokPeran.Length -gt 0 -and $tanpaPeran.Count -eq 0) ("tiap agen kit punya entri PERAN (tanpa entri: " + (($tanpaPeran -join ', ')) + ")")

  # loop-devops adalah peran PENYIAP: ia menulis compose, workflow, skrip, dan urutan deploy, tetapi
  # tidak boleh memegang alat untuk menjalankannya. Dijaga di frontmatter `tools`, bukan di prosa,
  # karena kalimat "jangan eksekusi prod" di dalam berkas agen bukan gerbang (ADR 0077 par 3).
  $devopsMd = Join-Path $kitRoot 'agents/loop-devops.md'
  $devopsTools = ''
  if (Test-Path $devopsMd) {
    $barisTools = Select-String -LiteralPath $devopsMd -Pattern '^tools:' | Select-Object -First 1
    if ($barisTools) { $devopsTools = $barisTools.Line }
  }
  Check ((Test-Path $devopsMd) -and $devopsTools -and $devopsTools -notmatch 'PowerShell' -and $devopsTools -notmatch 'Bash') "loop-devops penyiap: tools tanpa shell ('$devopsTools')"

  # ---- v1.25.0: dua lubang gerbang ----
  $errf = Join-Path $tmp 'hook.err'
  # Lubang 1: kit tidak menundukkan dirinya pada disiplinnya sendiri. init SENGAJA mengecualikan
  # vault saat memasang core.hooksPath, jadi test milik kit tak pernah digerbang (ADR 0077 par 4).
  $hpVault = (git -C $svVault config --get core.hooksPath)
  Check ($hpVault -eq $hpExpected) "core.hooksPath architecture-draft = githooks kit (vault ikut digerbang)"
  $prePush = Get-Content (Join-Path $claude 'hooks/githooks/pre-push') -Raw -Encoding UTF8
  Check ($prePush -match 'gerbang-kit\.py') 'pre-push memanggil gerbang-kit.py untuk vault'
  Check ($prePush -match '--berkas-file') 'pre-push mengoper daftar berkas lewat BERKAS (nama dok vault berisi spasi)'
  Check (Test-Path (Join-Path $claude 'hooks/gerbang-kit.py')) 'gerbang-kit.py ikut tersalin init'

  # Lubang 2: nol gerbang dihitung LULUS. Diuji lewat gerbang.ps1 sungguhan, bukan lewat fungsinya
  # saja: yang rusak dulu adalah baris penghitung `$lolos` di gerbang.ps1, bukan pustakanya.
  . (Join-Path $kitRoot 'hooks/gerbang-lib.ps1')
  $fx = Join-Path $tmp 'fx'
  function New-Fx([string]$nama, [string[]]$berkas) {
    $d = Join-Path $fx $nama
    foreach ($b in $berkas) {
      $p = Join-Path $d $b
      New-Item -ItemType Directory -Force -Path (Split-Path $p -Parent) | Out-Null
      Set-Content -LiteralPath $p -Value '{}' -Encoding UTF8
    }
    return $d
  }
  Check ((Get-JenisRepo (New-Fx 'fl' @('pubspec.yaml'))) -eq 'flutter') 'Get-JenisRepo: pubspec.yaml = flutter'
  Check ((Get-JenisRepo (New-Fx 'npm' @('package.json', 'package-lock.json'))) -eq 'node') 'Get-JenisRepo: package-lock.json juga node (bukan pnpm saja)'
  Check ((Get-JenisRepo (New-Fx 'nolock' @('package.json'))) -eq 'lain') 'Get-JenisRepo: package.json tanpa lockfile BUKAN node (pelaksana tak bisa dibaca)'
  # erp-frontend NYATA memegang keduanya; urutannya menentukan resolver mana yang dipakai
  Check ((Get-PmNode (New-Fx 'dua' @('package.json', 'pnpm-lock.yaml', 'package-lock.json'))).nama -eq 'pnpm') 'Get-PmNode: pnpm menang saat dua lockfile hidup berdampingan'
  Check ((Get-PmNode (New-Fx 'npm2' @('package.json', 'package-lock.json'))).jalan -eq 'npm run') 'Get-PmNode: skrip npm dijalankan lewat `npm run`, bukan `npm`'

  $gerbangPs1 = Join-Path $kitRoot 'hooks/gerbang.ps1'
  $outJson = Join-Path $tmp 'gerbang-lain.json'
  $rc = Invoke-Ps $gerbangPs1 @('-Path', $proj, '-Keluaran', $outJson) $null $errf
  $gj = Read-Json $outJson
  Check ($rc -eq 1 -and $null -ne $gj -and $gj.lolos -eq $false) "nol gerbang = GAGAL, bukan lolos (exit $rc, lolos=$($gj.lolos))"
  Check ($null -ne $gj -and (($gj.catatan -join ' ') -match 'daftar-izin')) 'catatan nol gerbang menyebut jalan keluarnya, bukan cuma "gagal"'

  # Vault sengaja TIDAK punya suite mesin; lubangnya diberi nama supaya terbaca sebagai keputusan.
  $outVault = Join-Path $tmp 'gerbang-vault.json'
  $rcV = Invoke-Ps $gerbangPs1 @('-Path', $svVault, '-Keluaran', $outVault) $null $errf
  $gv = Read-Json $outVault
  Check ($rcV -eq 0 -and $null -ne $gv -and $gv.lolos -eq $true) "architecture-draft lolos lewat daftar-izin (exit $rcV)"
  Check ($null -ne $gv -and (($gv.catatan -join ' ') -match 'daftar-izin')) 'lolosnya vault DICATAT, tidak senyap'

  # Alat yang tidak terpasang tidak boleh membuat pemeriksaannya ikut hilang: itu persis lubang
  # yang sedang ditutup. PATH dipangkas ke yang dibutuhkan saja supaya dart/flutter PASTI tak ada
  # (menyaring nama folder tidak cukup, dan salah sedikit berarti `flutter test` sungguhan jalan).
  $fdir = New-Fx 'flutterproj' @('pubspec.yaml')
  git -C $fdir init -q; git -C $fdir config user.email 'test@example.invalid'; git -C $fdir config user.name 'test'
  git -C $fdir checkout -q -b main; git -C $fdir add -A 2>$null; git -C $fdir commit -q -m init 2>$null
  $pathAsli = $env:PATH
  try {
    $env:PATH = @(
      (Split-Path (Get-Command powershell).Source -Parent),
      (Split-Path (Get-Command git).Source -Parent),
      (Join-Path $env:SystemRoot 'System32')
    ) -join ';'
    $outFl = Join-Path $tmp 'gerbang-flutter.json'
    $rcF = Invoke-Ps $gerbangPs1 @('-Path', $fdir, '-Keluaran', $outFl) $null $errf
  } finally { $env:PATH = $pathAsli }
  $gf = Read-Json $outFl
  Check ($null -ne $gf -and $gf.jenis -eq 'flutter') "repo pubspec.yaml terbaca jenis flutter ($($gf.jenis))"
  Check ($rcF -eq 1 -and $null -ne $gf -and @($gf.gerbang | Where-Object { $_.nama -eq 'alat' }).Count -eq 1) "alat flutter hilang = gerbang GAGAL bernama 'alat' (exit $rcF)"

  # session-start.ps1 harus mengeluarkan JSON sah di stdout DAN menulis berkas sesi.
  # $PWD diset ke $tmp supaya hook menemukan 'architecture-draft' untuk cek staleness.
  $errf = Join-Path $tmp 'hook.err'
  $hookJson = $null
  try {
    Push-Location $tmp
    try {
      $hookOut = (@{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='SessionStart' } | ConvertTo-Json -Compress) |
        powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $claude 'hooks/session-start.ps1') 2>$null
    } finally { Pop-Location }
    $hookJson = ($hookOut -join '') | ConvertFrom-Json
  } catch {}
  Check ($null -ne $hookJson -and $null -ne $hookJson.hookSpecificOutput.additionalContext) 'session-start.ps1 mengeluarkan JSON sah'
  $sesiFile = Join-Path $tmp '.task-plans/sesi/sesi-uji.json'
  Check (Test-Path $sesiFile) 'session-start.ps1 menulis berkas sesi'
  $sesi = $null; try { $sesi = Read-Json $sesiFile } catch {}
  Check ($null -ne $sesi -and $sesi.status -eq 'aktif' -and $sesi.session_id -eq 'sesi-uji') 'berkas sesi: status aktif + session_id'

  # sesi-sentuh.ps1 (UserPromptSubmit): tahap dari slash command, task dari argumennya
  $rc = Invoke-Hook (Join-Path $claude 'hooks/sesi-sentuh.ps1') @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='UserPromptSubmit'; prompt='/kerjakan .task-plans/briefs/2026-09-06-contoh.md' } $errf
  $sesi = Read-Json $sesiFile
  Check ($rc -eq 0 -and $sesi.tahap -eq 'kerjakan' -and $sesi.task -like '*contoh.md*') "sesi-sentuh: tahap=kerjakan, task terisi (exit $rc)"
  $rc = Invoke-Hook (Join-Path $claude 'hooks/sesi-sentuh.ps1') @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='UserPromptSubmit'; prompt='lanjut saja' } $errf
  $sesi2 = Read-Json $sesiFile
  Check ($rc -eq 0 -and $sesi2.tahap -eq 'kerjakan') 'sesi-sentuh: prompt biasa tidak mengubah tahap'
  # sesi-selesai.ps1 (SessionEnd)
  $rc = Invoke-Hook (Join-Path $claude 'hooks/sesi-selesai.ps1') @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='SessionEnd' } $errf
  $sesi3 = Read-Json $sesiFile
  Check ($rc -eq 0 -and $sesi3.status -eq 'selesai') 'sesi-selesai: status selesai'

  # ---- dashboard.ps1 -TanpaGh: HTML dari template + JSON tertanam memuat sesi uji ----
  $rc = Invoke-Ps (Join-Path $claude 'hooks/dashboard.ps1') @('-Workspace', $tmp, '-TanpaGh') $null $errf
  $dash = Join-Path $tmp '.task-plans/dashboard.html'
  $dashTxt = if (Test-Path $dash) { Get-Content $dash -Raw -Encoding UTF8 } else { '' }
  Check ($rc -eq 0 -and $dashTxt -match 'id="data"' -and $dashTxt -match 'sesi-uji' -and $dashTxt -notmatch '__DASHBOARD_DATA__') "dashboard.ps1 -TanpaGh: HTML + JSON tertanam memuat sesi uji (exit $rc)"
  $dashJson = $null; try { if ($dashTxt -match '(?s)<script id="data" type="application/json">(.*?)</script>') { $dashJson = ($Matches[1] -replace '<\\/', '</') | ConvertFrom-Json } } catch {}
  Check ($null -ne $dashJson -and $dashJson.versi -eq 1 -and $dashJson.gh.ok -eq $false) 'JSON tertanam sah, versi 1, gh ditandai tidak tersedia (bukan nol senyap)'

  # ---- kantor-agent (kit 1.20.0): launcher + penulis Python atas folder proyek palsu ----
  # Transkrip disusun dari templat baris NYATA (tests/fixtures/kantor-agent), bukan rakitan tangan.
  # sesi-uji sudah 'selesai' (sesi-selesai di atas) tapi kejadiannya LEBIH BARU = kasus --resume: tetap hidup.
  $kaPs = Join-Path $claude 'hooks/kantor-agent.ps1'
  Check (Test-Path $kaPs) 'kantor-agent.ps1 tersalin'
  $kaTemplat = (Get-Content (Join-Path $kitRoot 'tests/fixtures/kantor-agent/baris-nyata.json') -Raw -Encoding UTF8) | ConvertFrom-Json
  $kaBaris = $kaTemplat.assistant_tool_use
  $kaBaris.cwd = $tmp
  $kaBaris.timestamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ', [Globalization.CultureInfo]::InvariantCulture)
  $kaBaris.message.content[0].name = 'Edit'
  $kaBaris.message.content[0].input = [pscustomobject]@{ file_path = 'uji/berkas_uji.py' }
  $kaUtf8 = New-Object System.Text.UTF8Encoding($false)
  $kaProyek = Join-Path $tmp 'proyek-palsu'
  New-Item -ItemType Directory -Force -Path (Join-Path $kaProyek 'slug-uji') | Out-Null
  [IO.File]::WriteAllText((Join-Path $kaProyek 'slug-uji/sesi-uji.jsonl'), (($kaBaris | ConvertTo-Json -Depth 20 -Compress) + "`n"), $kaUtf8)
  $kaData = Join-Path $tmp '.task-plans/kantor-agent-data.js'
  function Read-KantorData([string]$path) {
    if (-not (Test-Path $path)) { return $null }
    $t = [IO.File]::ReadAllText($path, [Text.Encoding]::UTF8)
    $awalan = 'window.__KANTOR__ = '
    if (-not $t.StartsWith($awalan)) { return $null }
    try { return ($t.Substring($awalan.Length).TrimEnd().TrimEnd(';') | ConvertFrom-Json) } catch { return $null }
  }
  function Invoke-PsLepas([string]$script, [string[]]$argsSkrip) {
    # BUKAN Invoke-Ps (Start-Process -Wait): launcher mode loop sengaja meninggalkan penulis yang hidup,
    # jadi yang ditunggu hanya proses launcher-nya sendiri lewat WaitForExit.
    $argList = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $script + '"')) + @($argsSkrip | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } })
    $p = Start-Process -FilePath 'powershell' -ArgumentList $argList -WindowStyle Hidden -PassThru
    $null = $p.Handle   # tanpa ini ExitCode bisa kosong sesudah proses selesai (PS 5.1)
    if (-not $p.WaitForExit(90000)) { try { $p.Kill() } catch {}; return -1 }
    return $p.ExitCode
  }
  function Get-PenulisUji { @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*kantor-agent.py*' -and $_.CommandLine -like ('*' + $tmp + '*') }) }

  # registri sesi palsu berbentuk ~/.claude/sessions/<pid>.json (kit 1.21.0). PID dipinjam dari proses yang
  # memang hidup (test ini dan induknya) dan tanpa procStart, supaya pemeriksa hidup lolos tanpa menebak FILETIME.
  $kaReg = Join-Path $tmp 'registri-palsu'
  New-Item -ItemType Directory -Force -Path $kaReg | Out-Null
  $kaMs = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
  $kaInduk = [int](Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
  [IO.File]::WriteAllText((Join-Path $kaReg "$PID.json"), (@{ pid = $PID; sessionId = 'sesi-uji'; cwd = $tmp; kind = 'interactive'; entrypoint = 'cli'; name = 'uji-01'; status = 'busy'; statusUpdatedAt = $kaMs; updatedAt = $kaMs; startedAt = $kaMs } | ConvertTo-Json -Compress), $kaUtf8)
  [IO.File]::WriteAllText((Join-Path $kaReg "$kaInduk.json"), (@{ pid = $kaInduk; sessionId = 'sesi-diam'; cwd = $tmp; kind = 'interactive'; entrypoint = 'claude-vscode'; name = 'uji-02'; status = 'idle'; statusUpdatedAt = ($kaMs - 7200000); updatedAt = ($kaMs - 7200000); startedAt = ($kaMs - 9000000) } | ConvertTo-Json -Compress), $kaUtf8)

  $rc = Invoke-Ps $kaPs @('-Workspace', $tmp, '-ProyekDir', $kaProyek, '-RegistriDir', $kaReg, '-Sekali', '-TanpaBuka') $null $errf
  $d = Read-KantorData $kaData
  $s0 = @($d.sesi) | Where-Object { $_.id -eq 'sesi-uji' } | Select-Object -First 1
  $sDiam = @($d.sesi) | Where-Object { $_.id -eq 'sesi-diam' } | Select-Object -First 1
  Check ($rc -eq 0 -and $null -ne $d -and $d.versi -eq 2) "kantor-agent -Sekali: data.js versi 2 tertulis (exit $rc)"
  Check ($null -ne $s0 -and $s0.id -eq 'sesi-uji' -and $s0.area -eq 'meja' -and $s0.alat -eq 'Edit' -and $s0.detail -eq 'berkas_uji.py') "kantor-agent: sesi-uji di meja, alat Edit, detail nama berkas ($($s0.area)/$($s0.alat)/$($s0.detail))"
  Check ($null -ne $d -and $d.skema.sumber_hidup -eq 'registri' -and $null -ne $sDiam -and $sDiam.area -eq 'lounge' -and $sDiam.diam_detik -ge 7000 -and $sDiam.asal -eq 'claude-vscode') "kantor-agent: registri -> sesi terbuka yang diam 2 jam tanpa transkrip tampil di lounge ($($d.skema.sumber_hidup)/$($sDiam.area)/$($sDiam.diam_detik))"
  Check ($null -ne $d -and $d.skema.dikenali -eq $true) 'kantor-agent: transkrip dari templat nyata dikenali'
  $kaHtml = Join-Path $tmp '.task-plans/kantor-agent.html'
  Check ((Test-Path $kaHtml) -and ((Get-Content $kaHtml -Raw -Encoding UTF8) -match 'kantor-agent-data\.js')) 'kantor-agent: HTML tersalin dari template dan memuat data.js'

  # format berubah: lebih dari separuh baris rusak -> dikenali=false, bukan kantor kosong yang senyap
  $kaRusak = Join-Path $tmp 'proyek-rusak'
  New-Item -ItemType Directory -Force -Path (Join-Path $kaRusak 'slug-uji') | Out-Null
  [IO.File]::WriteAllText((Join-Path $kaRusak 'slug-uji/sesi-rusak.jsonl'), (($kaBaris | ConvertTo-Json -Depth 20 -Compress) + "`n{rusak`n{rusak`n{rusak`n"), $kaUtf8)
  $rc = Invoke-Ps $kaPs @('-Workspace', $tmp, '-ProyekDir', $kaRusak, '-RegistriDir', (Join-Path $tmp 'tanpa-registri'), '-Sekali', '-TanpaBuka') $null $errf   # mode transkrip
  $d = Read-KantorData $kaData
  Check ($rc -eq 0 -and $null -ne $d -and $d.skema.dikenali -eq $false) "kantor-agent: >50% baris rusak -> dikenali=false (exit $rc)"

  # Python yang ditunjuk tak ada -> exit 2 dengan pesan, bukan diam
  $rc = Invoke-Ps $kaPs @('-Workspace', $tmp, '-ProyekDir', $kaProyek, '-Sekali', '-TanpaBuka', '-Python', (Join-Path $tmp 'tidak-ada\python.exe')) $null $errf
  $errTxt = if (Test-Path $errf) { Get-Content $errf -Raw } else { '' }
  Check ($rc -eq 2 -and $errTxt -match 'Python') "kantor-agent: -Python tak ada -> exit 2 + pesan (exit $rc)"

  # mode loop: launcher kedua TIDAK menyalakan penulis kedua; -Berhenti menghentikannya dan membuang pid
  $rc = Invoke-PsLepas $kaPs @('-Workspace', $tmp, '-ProyekDir', $kaProyek, '-RegistriDir', $kaReg, '-CekSilangDetik', '0', '-Interval', '1', '-TanpaBuka')
  $sw = [Diagnostics.Stopwatch]::StartNew()
  while (@(Get-PenulisUji).Count -lt 1 -and $sw.Elapsed.TotalSeconds -lt 30) { Start-Sleep -Milliseconds 500 }
  $n1 = @(Get-PenulisUji).Count
  $rc2 = Invoke-PsLepas $kaPs @('-Workspace', $tmp, '-ProyekDir', $kaProyek, '-RegistriDir', $kaReg, '-CekSilangDetik', '0', '-Interval', '1', '-TanpaBuka')
  Start-Sleep -Seconds 2
  $n2 = @(Get-PenulisUji).Count
  Check ($rc -eq 0 -and $rc2 -eq 0 -and $n1 -eq 1 -and $n2 -eq 1) "kantor-agent loop: launcher dua kali = satu penulis (exit $rc/$rc2, proses $n1 lalu $n2)"
  $rc = Invoke-PsLepas $kaPs @('-Workspace', $tmp, '-Berhenti')
  $sw = [Diagnostics.Stopwatch]::StartNew()
  while (@(Get-PenulisUji).Count -gt 0 -and $sw.Elapsed.TotalSeconds -lt 15) { Start-Sleep -Milliseconds 500 }
  Check ($rc -eq 0 -and @(Get-PenulisUji).Count -eq 0 -and -not (Test-Path (Join-Path $tmp '.task-plans/kantor-agent.pid'))) "kantor-agent -Berhenti: penulis mati, berkas pid terhapus (exit $rc)"

  # dua launcher SERENTAK: keduanya bisa lolos cek PID sebelum ada yang menulis pid; kunci penulis (kit 1.21.0)
  # membuat yang kalah keluar 4 dan launcher-nya melapor "sudah jalan", jadi tetap satu penulis
  $argSerentak = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $kaPs + '"'), '-Workspace', ('"' + $tmp + '"'), '-ProyekDir', ('"' + $kaProyek + '"'), '-RegistriDir', ('"' + $kaReg + '"'), '-CekSilangDetik', '0', '-Interval', '1', '-TanpaBuka')
  $l1 = Start-Process -FilePath 'powershell' -ArgumentList $argSerentak -WindowStyle Hidden -PassThru; $null = $l1.Handle
  $l2 = Start-Process -FilePath 'powershell' -ArgumentList $argSerentak -WindowStyle Hidden -PassThru; $null = $l2.Handle
  $null = $l1.WaitForExit(90000); $null = $l2.WaitForExit(90000)
  Start-Sleep -Seconds 3
  $nSerentak = @(Get-PenulisUji).Count
  Check ($l1.ExitCode -eq 0 -and $l2.ExitCode -eq 0 -and $nSerentak -eq 1) "kantor-agent: dua launcher serentak = satu penulis (exit $($l1.ExitCode)/$($l2.ExitCode), proses $nSerentak)"
  $null = Invoke-PsLepas $kaPs @('-Workspace', $tmp, '-Berhenti')

  # ---- pre-commit-gate: KONTROL POSITIF (harus menolak) dan NEGATIF (harus lolos) ----
  $gate = Join-Path $claude 'hooks/pre-commit-gate.ps1'
  Check (Test-Path $gate) 'pre-commit-gate.ps1 tersalin'
  $cmdMain = 'git -C "' + $proj + '" -c core.fsmonitor=false commit -m "x"'
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=$cmdMain } } $errf
  $errTxt = if (Test-Path $errf) { Get-Content $errf -Raw } else { '' }
  Check ($rc -eq 2) "KONTROL POSITIF: commit di main repo kode DITOLAK (exit $rc)"
  Check ($errTxt -match 'main') 'pesan penolakan menyebut branch-nya'
  git -C $proj checkout -q -b feat/uji
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=$cmdMain } } $errf
  Check ($rc -eq 0) "KONTROL NEGATIF: commit di branch fitur LOLOS (exit $rc)"
  # cwd = repo (tanpa -C), masih di feat/uji -> lolos; lalu kembali ke main -> ditolak
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$proj; hook_event_name='PreToolUse'; tool_name='Bash'; tool_input=@{ command='git commit -m "y"' } } $errf
  Check ($rc -eq 0) "repo dari cwd, branch fitur, matcher Bash: lolos (exit $rc)"
  git -C $proj checkout -q main
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$proj; hook_event_name='PreToolUse'; tool_name='Bash'; tool_input=@{ command='git commit -m "y"' } } $errf
  Check ($rc -eq 2) "repo dari cwd, branch main: ditolak (exit $rc)"
  # vault dikecualikan walau di main
  git -C $svVault checkout -q -b main 2>$null
  $cmdVault = 'git -C "' + $svVault + '" -c core.fsmonitor=false commit -m "dok"'
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=$cmdVault } } $errf
  Check ($rc -eq 0) "vault architecture-draft dikecualikan (exit $rc)"
  # perintah git non-commit di main: lolos
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$proj; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command='git status' } } $errf
  Check ($rc -eq 0) "git status di main: lolos (exit $rc)"
  # 'commit' sebagai kata di pesan, bukan subperintah: lolos
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$proj; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command='git log --grep commit' } } $errf
  Check ($rc -eq 0) "git log --grep commit: lolos (exit $rc)"
  # GAGAL-TERTUTUP: -C dari ekspresi yang tak bisa diurai -> DITOLAK, pesan menyarankan path literal.
  # Kontrol positif langsung 2026-09-06 membuktikan versi gagal-terbuka meloloskan commit di main lewat bentuk ini.
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command='$t = Join-Path $env:TEMP "x"; git -C $t commit -m "z"' } } $errf
  $errTxt = if (Test-Path $errf) { Get-Content $errf -Raw } else { '' }
  Check ($rc -eq 2 -and $errTxt -match 'LITERAL') "path repo dari ekspresi: DITOLAK gagal-tertutup, pesan menyebut path literal (exit $rc)"
  # $env:TEMP di dalam string di-expand -> repo dikenali; proj di main -> ditolak KARENA main (bukan karena tak terurai)
  $relProj = $proj.Substring($env:TEMP.Length)
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=('git -C "$env:TEMP' + $relProj + '" commit -m "e"') } } $errf
  $errTxt = if (Test-Path $errf) { Get-Content $errf -Raw } else { '' }
  Check ($rc -eq 2 -and $errTxt -match "branch 'main'" -and $errTxt -notmatch 'LITERAL') "`$env: di-expand: ditolak karena main, bukan karena tak terurai (exit $rc)"
  # `$v="literal"; git -C $v commit` tetap dikenali; proj di main -> ditolak karena main
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=('$v="' + $proj + '"; git -C $v -c core.fsmonitor=false commit -m "f"') } } $errf
  $errTxt = if (Test-Path $errf) { Get-Content $errf -Raw } else { '' }
  Check ($rc -eq 2 -and $errTxt -match "branch 'main'") "`$v=literal lalu -C `$v: ditolak karena main (exit $rc)"
  # `cd <repo>; git commit` dikenali lewat cd
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=('cd "' + $proj + '"; git commit -m "g"') } } $errf
  $errTxt = if (Test-Path $errf) { Get-Content $errf -Raw } else { '' }
  Check ($rc -eq 2 -and $errTxt -match "branch 'main'") "cd <repo>; git commit: ditolak karena main (exit $rc)"

  # ---- KONTROL POSITIF TAMBAHAN (brief pre-commit-gate-overhead 2026-09-12): bentuk commit
  # yang logikanya SUDAH menolak hari ini tapi belum pernah diuji eksplisit. $proj masih di
  # branch main sejak blok di atas. Dijalankan lewat $gate = skrip yang benar-benar dipasang
  # init (bukan path kit langsung), sama seperti kontrol di atas.
  $cmdCKecil = 'git -c core.fsmonitor=false -C "' + $proj + '" commit -m "x"'   # -c SEBELUM -C
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=$cmdCKecil } } $errf
  Check ($rc -eq 2) "KONTROL POSITIF: '-c' sebelum '-C', tetap DITOLAK (exit $rc)"

  $cmdKapital = 'git -C "' + $proj + '" Commit -m "x"'   # huruf kapital pada subperintah
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=$cmdKapital } } $errf
  Check ($rc -eq 2) "KONTROL POSITIF: 'Commit' huruf kapital, tetap DITOLAK (exit $rc)"

  $cmdGitExe = 'Git.exe -C "' + $proj + '" commit -m "x"'
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=$cmdGitExe } } $errf
  Check ($rc -eq 2) "KONTROL POSITIF: 'Git.exe' (bukan 'git' polos), tetap DITOLAK (exit $rc)"

  $gitExePath = (Get-Command git).Source   # path lengkap git.exe di mesin ini, bukan dikarang
  $cmdAmpersand = '& "' + $gitExePath + '" -C "' + $proj + '" commit -m "x"'
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$tmp; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=$cmdAmpersand } } $errf
  Check ($rc -eq 2) "KONTROL POSITIF: path lengkap git.exe lewat '&', tetap DITOLAK (exit $rc)"

  $cmdChain = 'git add .; git commit -m "x"'
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$proj; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=$cmdChain } } $errf
  Check ($rc -eq 2) "KONTROL POSITIF: 'git add .; git commit' dirangkai ';', tetap DITOLAK (exit $rc)"

  $cmdBaris = 'git status' + "`r`n" + 'git commit -m "x"'
  $rc = Invoke-Hook $gate @{ session_id='sesi-uji'; cwd=$proj; hook_event_name='PreToolUse'; tool_name='PowerShell'; tool_input=@{ command=$cmdBaris } } $errf
  Check ($rc -eq 2) "KONTROL POSITIF: 'git status' + 'git commit' baris baru, tetap DITOLAK (exit $rc)"

  # ---- loop-kirim: BEST-EFFORT, tidak pernah menahan ----
  # Ambangnya sengaja LONGGAR (20 dan 25 detik). Yang dijaga adalah "tidak menggantung", bukan
  # kecepatan spawn: terukur 5,07 dan 9 detik saat mesin sepi, 11,4 dan 16 detik saat sibuk, dan
  # sejak 1.25.0 test ini ikut jalan di pre-push (mesin justru sedang sibuk). Ambang ketat membuat
  # gerbangnya kadang merah tanpa sebab, dan gerbang yang begitu dimatikan orang dalam sepekan.
  $lk = Join-Path $claude 'hooks/loop-kirim.ps1'
  # JSON dilewatkan lewat berkas: argumen ber-kutip ke proses baru dilucuti Windows (lihat komentar di skrip)
  $dataFile = Join-Path $tmp 'loop-data.json'; [IO.File]::WriteAllText($dataFile, '{"id":"s"}')
  $konfigTidakAda = Join-Path $tmp 'tidak-ada\loop-ingest.json'
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $rc = Invoke-Ps $lk @('-Jenis', 'sesi.mulai', '-DataFile', $dataFile, '-Konfig', $konfigTidakAda) $null $errf
  Check ($rc -eq 0 -and $sw.Elapsed.TotalSeconds -lt 20) "loop-kirim tanpa konfigurasi: no-op, exit 0 ($([int]$sw.Elapsed.TotalMilliseconds) ms)"
  $konfigMati = Join-Path $tmp 'loop-ingest.json'
  [IO.File]::WriteAllText($konfigMati, '{"url":"http://127.0.0.1:9/loop/ingest","secret":"x","mesin":"UJI"}')
  [IO.File]::WriteAllText((Join-Path $tmp 'gh-login.txt'), 'uji')   # cegah panggilan gh sungguhan
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $rc = Invoke-Ps $lk @('-Jenis', 'sesi.mulai', '-DataFile', $dataFile, '-Konfig', $konfigMati) $null $errf
  $gagalFile = Join-Path $tmp 'loop-ingest.gagal'
  Check ($rc -eq 0 -and $sw.Elapsed.TotalSeconds -lt 25) "loop-kirim ke URL mati: tetap exit 0 dalam $([int]$sw.Elapsed.TotalSeconds) detik"
  Check (Test-Path $gagalFile) 'loop-kirim mencatat kegagalan ke loop-ingest.gagal (tidak senyap)'
  $idOut = [IO.Path]::GetTempFileName()
  $p = Start-Process powershell -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',('"' + $lk + '"'),'-Jenis','brief.dibuat','-BriefSlug','Hapus-PR-Notification','-HanyaId') -RedirectStandardOutput $idOut -Wait -PassThru -NoNewWindow
  $id1 = (Get-Content $idOut -Raw).Trim()
  $p = Start-Process powershell -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',('"' + $lk + '"'),'-Jenis','brief.dibuat','-BriefSlug','hapus-pr-notification','-HanyaId') -RedirectStandardOutput $idOut -Wait -PassThru -NoNewWindow
  $id2 = (Get-Content $idOut -Raw).Trim()
  Check ($id1 -match '^[0-9a-f]{12}$' -and $id1 -eq $id2) "id brief 12 hex, stabil terhadap huruf besar-kecil ($id1)"

  # ---- transkrip-ringkas: JSONL sah -> markdown; sampah -> tolak ----
  $tr = Join-Path $claude 'hooks/transkrip-ringkas.ps1'
  $jl = Join-Path $tmp 'sesi.jsonl'
  @(
    '{"type":"user","timestamp":"2026-09-06T01:00:00Z","message":{"role":"user","content":"tolong perbaiki paginasi retur"}}',
    '{"type":"assistant","timestamp":"2026-09-06T01:00:05Z","message":{"role":"assistant","content":[{"type":"text","text":"Saya cek dulu."},{"type":"tool_use","name":"Grep","input":{"pattern":"paginasi"}}]}}',
    '{"type":"queue-operation","operation":"enqueue"}'
  ) | Set-Content -Path $jl -Encoding UTF8
  $md = Join-Path $tmp 'sesi.md'
  $rc = Invoke-Ps $tr @('-Transkrip', $jl, '-Keluaran', $md) $null $errf
  $mdTxt = if (Test-Path $md) { Get-Content $md -Raw -Encoding UTF8 } else { '' }
  Check ($rc -eq 0 -and $mdTxt -match 'paginasi retur' -and $mdTxt -match 'Grep') "transkrip-ringkas: prompt + nama tool terambil (exit $rc)"
  $junk = Join-Path $tmp 'junk.jsonl'
  @('bukan json', '{"type":"tak-dikenal"}', 'x') | Set-Content -Path $junk -Encoding UTF8
  $rc = Invoke-Ps $tr @('-Transkrip', $junk, '-Keluaran', (Join-Path $tmp 'junk.md')) $null $errf
  Check ($rc -ne 0) "transkrip-ringkas: <50% terurai DITOLAK, bukan ringkasan kosong (exit $rc)"

  # ---- init tanpa -NoPreCommitHook: gerbang terpasang utk Bash DAN PowerShell, disaring 'if' ----
  # Sejak brief pre-commit-gate-overhead (2026-09-12): bukan lagi SATU entri matcher
  # "Bash|PowerShell" (yang men-spawn utk SETIAP panggilan), melainkan DUA entri terpisah,
  # masing-masing memakai field `if` supaya Claude Code menyaring ISI command sebelum spawn.
  # `if` sendiri TIDAK bisa diuji test-init (test ini memanggil skrip hook langsung, bukan lewat
  # mesin pencocokan `if` milik Claude Code) -- yang diperiksa di sini cuma BENTUK konfigurasi.
  & (Join-Path $svVault '.agent-kit/init.ps1') -Workspace $tmp -ActiveProject 'demo-proj' | Out-Null
  $st2 = Get-Content (Join-Path $claude 'settings.json') -Raw | ConvertFrom-Json
  # 1.30.0: entri gerbang antrean (antre-gate) hidup berdampingan; yang dipatok di sini entri COMMIT
  $ptuSemua = @($st2.hooks.PreToolUse)
  $ptu = @($ptuSemua | Where-Object { @($_.hooks | Where-Object { $_.command -match 'pre-commit-gate' }).Count -gt 0 })
  Check ($ptu.Count -eq 2) "PreToolUse punya 2 entri gerbang commit terpisah, Bash dan PowerShell ($($ptu.Count))"
  $antreE = @($ptuSemua | Where-Object { @($_.hooks | Where-Object { $_.command -match 'antre-gate' }).Count -gt 0 })
  Check ((($antreE.matcher | Sort-Object) -join ',') -eq 'Bash,PowerShell') "gerbang antrean terpasang untuk Bash DAN PowerShell ($($antreE.matcher -join ','))"
  $polaHarap = @('*pnpm *', '*vitest*', '*tsc*', '*eslint*', '*next build*', '*go test*', '*go build*', '*flutter test*', '*flutter build*')
  foreach ($e in $antreE) {
    $ifs = @($e.hooks | ForEach-Object { $_.'if' })
    $harap = @($polaHarap | ForEach-Object { '{0}({1})' -f $e.matcher, $_ })
    Check ((@($harap | Where-Object { $ifs -ccontains $_ }).Count -eq $harap.Count) -and $ifs.Count -eq $harap.Count) ("antre-gate {0}: pola 'if' PERSIS daftar alat berat ({1})" -f $e.matcher, ($ifs -join ' '))
  }
  # test perilaku antrean (klasifikasi, hook, Mutex proses nyata, gerbang-lib, pre-push) di berkasnya sendiri
  $antreTest = Join-Path $kitRoot 'tests/test-antre.ps1'
  $rcAntre = Invoke-Ps $antreTest @()
  Check ($rcAntre -eq 0) "tests/test-antre.ps1 lulus (exit $rcAntre; jalankan langsung untuk rinciannya)"
  $bashEntry = $ptu | Where-Object { $_.matcher -eq 'Bash' }
  $psEntry   = $ptu | Where-Object { $_.matcher -eq 'PowerShell' }
  Check ($null -ne $bashEntry -and $null -ne $psEntry) "gerbang terpasang untuk tool Bash DAN PowerShell (matcher: $($ptu.matcher -join ', '))"
  Check ($null -ne $bashEntry -and ($bashEntry.hooks[0].command -match 'pre-commit-gate')) 'entri Bash memanggil pre-commit-gate, bukan reminder'
  Check ($null -ne $psEntry -and ($psEntry.hooks[0].command -match 'pre-commit-gate')) 'entri PowerShell memanggil pre-commit-gate, bukan reminder'
  # Dipatok PERSIS lewat -ceq, BUKAN -match longgar: pola longgar ('(?i)commit') tetap PASS
  # walau polanya DIPERSEMPIT (mis. 'PowerShell(git commit*)'), padahal penyempitan semacam
  # itulah yang membuat bentuk '-C'/'Git.exe'/'&'/';' di kontrol positif atas gagal-terbuka
  # (proses hook tidak pernah di-spawn Claude Code untuk bentuk itu). Mengubah pola 'if' di
  # init.ps1/init.sh WAJIB mengulang kontrol positif langsung di sesi Claude Code hidup
  # (skill ubah-hook-agent-kit §7) -- test-init ini TIDAK bisa membuktikan perilaku `if`
  # sesungguhnya, cuma bentuk konfigurasinya.
  Check ($null -ne $bashEntry -and ($bashEntry.hooks[0].'if' -ceq 'Bash(*commit*)')) "entri Bash: filter 'if' PERSIS 'Bash(*commit*)' ($($bashEntry.hooks[0].'if'))"
  Check ($null -ne $psEntry -and ($psEntry.hooks[0].'if' -ceq 'PowerShell(*commit*)')) "entri PowerShell: filter 'if' PERSIS 'PowerShell(*commit*)' ($($psEntry.hooks[0].'if'))"

  # v1.0.1: re-init harus prune file lama yg sudah tak ada di kit, tapi tetap salin yg nyata
  $stale = Join-Path $claude 'commands/__stale-test__.md'
  Set-Content -Path $stale -Value 'stale' -Encoding UTF8
  & (Join-Path $svVault '.agent-kit/init.ps1') -Workspace $tmp -ActiveProject 'demo-proj' -NoPreCommitHook | Out-Null
  Check (-not (Test-Path $stale)) 're-init prune file command lama'
  Check (Test-Path (Join-Path $claude 'commands/start-task.md')) 're-init tetap salin command nyata'

  # ---- brief 2026-09-23 (init-project-aktif-kosong): cabang interaktif TANPA -ActiveProject,
  # jawaban kosong/spasi. Sebelum ini `$sel` yang kosong jatuh ke else `$active = $sel` tanpa
  # validasi, dan '__ACTIVE_PROJECT__' tetap tergantikan (oleh string kosong) -- test lama
  # (baris ~181-182) tak pernah menangkapnya karena SELALU memanggil dengan -ActiveProject.
  # Invoke-Ps -RedirectStandardInput menjalankan cabang interaktif tanpa menggantung.
  $initUji = Join-Path $svVault '.agent-kit/init.ps1'
  $cmSebelum = Get-Content (Join-Path $claude 'CLAUDE.md') -Raw -Encoding UTF8

  $stdinKosong = Join-Path $tmp 'stdin-kosong.txt'
  [IO.File]::WriteAllText($stdinKosong, "`r`n")
  $errfKosong = Join-Path $tmp 'hook-kosong.err'
  $rcKosong = Invoke-Ps $initUji @('-Workspace', $tmp, '-NoPreCommitHook') $stdinKosong $errfKosong
  $errKosongTxt = if (Test-Path $errfKosong) { Get-Content $errfKosong -Raw } else { '' }
  Check ($rcKosong -ne 0) "jawaban interaktif KOSONG: init.ps1 exit code bukan 0 (exit $rcKosong)"
  Check ($errKosongTxt -match '(?i)project aktif') "pesan penolakan (kosong) menyebut project aktif ($errKosongTxt)"
  $cmSesudahKosong = Get-Content (Join-Path $claude 'CLAUDE.md') -Raw -Encoding UTF8
  Check ($cmSesudahKosong -eq $cmSebelum) 'CLAUDE.md tidak tersentuh saat jawaban interaktif kosong (tidak dirusak)'

  $stdinSpasi = Join-Path $tmp 'stdin-spasi.txt'
  [IO.File]::WriteAllText($stdinSpasi, "   `r`n")
  $errfSpasi = Join-Path $tmp 'hook-spasi.err'
  $rcSpasi = Invoke-Ps $initUji @('-Workspace', $tmp, '-NoPreCommitHook') $stdinSpasi $errfSpasi
  $errSpasiTxt = if (Test-Path $errfSpasi) { Get-Content $errfSpasi -Raw } else { '' }
  Check ($rcSpasi -ne 0) "jawaban interaktif HANYA SPASI: init.ps1 exit code bukan 0 (exit $rcSpasi)"
  Check ($errSpasiTxt -match '(?i)project aktif') "pesan penolakan (spasi) menyebut project aktif ($errSpasiTxt)"
  $cmSesudahSpasi = Get-Content (Join-Path $claude 'CLAUDE.md') -Raw -Encoding UTF8
  Check ($cmSesudahSpasi -eq $cmSebelum) 'CLAUDE.md tidak tersentuh saat jawaban interaktif hanya spasi'
}
finally {
  # penulis kantor-agent yang tertinggal (test gagal di tengah) jangan sampai hidup terus
  Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*kantor-agent.py*' -and $_.CommandLine -like ('*' + $tmp + '*') } | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop } catch {} }
  if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
}
if ($fail -gt 0) { Write-Host "$fail gagal"; exit 1 } else { Write-Host 'Semua lulus'; exit 0 }
