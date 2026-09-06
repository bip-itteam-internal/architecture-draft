---
name: ubah-hook-agent-kit
description: Gunakan saat menambah atau mengubah hook Claude Code, skrip pendukung (.ps1/.sh), agen kustom, atau init di architecture-draft/.agent-kit, lalu harus membuktikan perubahannya benar-benar hidup di mesin PowerShell. Memuat urutan kerja TDD atas tests/test-init.ps1, kontrol positif langsung yang menangkap apa yang test-init lewatkan, jebakan PowerShell 5.1 dan siklus-hidup Claude Code yang sudah terbukti menggigit, serta gerbang verifikasi sebelum bump VERSION.
---

# Mengubah hook dan skrip di agent-kit

> **DRAFT** hasil `/ekstrak-skill` atas sesi `ba147e5f` (2026-09-06, kit 1.14.0 → 1.15.0).
> Belum ditinjau manusia. Bagian bertanda **TBD** belum punya jejak di transkrip.

Kit ini tidak punya CI. `tests/test-init.ps1` pernah **merah beberapa rilis tanpa ada yang
tahu** (README §Changelog 1.14.0), dan hook `pre-commit` versi lama **tidak pernah menyala di
mesin PowerShell** selama entah berapa lama karena matcher-nya `Bash` saja. Keduanya kelas yang
sama: perubahan kit yang "jadi" tapi tidak pernah dibuktikan hidup. Skill ini adalah urutan
yang di sesi 2026-09-06 menangkap **enam** cacat sebelum kit-nya menyebar ke tim lewat `init`.

Desain loop-nya sendiri ada di `docs/2026-09-06-ai-engineering-loop-design.md`; skill ini
tidak mengulanginya. Yang ada di sini hanya **cara mengerjakan dan membuktikan** perubahan kit.

---

## Kapan dipakai

- Menambah atau mengubah berkas di `hooks/` (hook Claude Code maupun skrip pendukung).
- Menambah agen kustom di `agents/`.
- Mengubah `init.ps1` / `init.sh` (folder yang disalin, isi `settings.json`, hooksPath).
- Menambah assertion di `tests/test-init.ps1`.

**Tidak** untuk perubahan `rules/*.md` saja: itu menyebar lewat `git pull` tanpa bump
`VERSION` (README, entri "rules-only 2026-08-25").

---

## Prosedur

### 0. Sunting di kit, bukan di `.claude/`

`erp/.claude/` adalah salinan hasil `init` dan tertimpa tiap re-init (team-memory § Gotchas
lingkungan). Semua suntingan ke `architecture-draft/.agent-kit/`. Vault push langsung ke
`main`, tanpa PR (team-memory § Gotchas lingkungan, butir vault).

### 1. Baca keadaan kit sebelum menulis apa pun

Yang dibaca sesi itu sebelum baris pertama ditulis [16:05:36, 16:05:41, 16:21:03]:

- `VERSION`, `init.ps1` **utuh**, `init.sh` **utuh** (keduanya harus tetap cermin).
- Seluruh `hooks/*.ps1` yang ada, terutama yang akan diganti.
- `tests/test-init.ps1` utuh: bentuk sandbox-nya, helper `Check`, cara ia memanggil hook.
- `README.md` §Changelog untuk format entri, `templates/workspace-CLAUDE.md` bila flow di
  `CLAUDE.md` workspace ikut berubah.

### 2. Kontrak Claude Code jangan ditebak

Sesi itu mendelegasikan empat kontrak ke agen `claude-code-guide` sebelum menulis hook
[16:06:03]: bentuk stdin JSON hook, arti exit code, frontmatter agen kustom, dan bentuk
matcher. Yang kemudian dipakai di kode dan terbukti:

- stdin hook adalah JSON dengan `session_id`, `cwd`, `hook_event_name`, `tool_name`,
  `tool_input.command` (PreToolUse), `prompt` (UserPromptSubmit). Bentuk persis ini yang
  ditiru `Invoke-Hook` di `test-init.ps1`.
- **Exit 2 memblokir tool call apa pun isi stdout-nya.** Itu sebabnya gerbang menolak lewat
  exit code, bukan lewat JSON `decision`: JSON yang salah bentuk tidak bisa membuat gerbang
  gagal-terbuka (`hooks/pre-commit-gate.ps1:6-8`).
- Hook harus bisa berjalan tanpa stdin: `if (-not [Console]::IsInputRedirected) { exit 0 }`.

**TBD**: isi lengkap jawaban `claude-code-guide` (5.642 karakter) tidak terlihat di ringkasan;
yang tercatat di atas hanya yang berbekas di kode.

### 3. Test dulu, lihat merah, baru hook

Kit punya infra test, jadi TDD berlaku [16:15:28]. Untuk tiap hook baru tulis **dua** macam
assertion di `tests/test-init.ps1` sebelum hook-nya ada:

- **Kontrol positif**: hook harus **menolak** (exit 2) pada keadaan yang dilarang.
- **Kontrol negatif**: hook harus **lolos** (exit 0) pada keadaan yang sah, termasuk yang
  mirip tapi bukan (contoh nyata: `git log --grep commit` bukan `git commit`,
  `test-init.ps1:143-145`; vault di `main` tetap lolos, `:135-139`).

Jalankan dan pastikan merahnya **karena assertion**, bukan karena harness mati [16:16:35].
Yang menolong saat itu: berkas yang belum ada harus jadi `FAIL`, bukan abort. Helper
`Read-Json` mengembalikan `$null` alih-alih melempar [16:28:11], dan `Check` menghitung
`$script:fail` tanpa menghentikan skrip.

Jangan mematok angka mati (jumlah command, jumlah agen); turunkan dari isi kit
(`test-init.ps1:55-59, 76-78`). Angka mati sudah pernah rot diam-diam.

### 4. Tulis hook `.ps1`, lalu cerminnya `.sh`

Urutan di sesi itu [16:19:31 sampai 16:24:20]: lib bersama dulu (`sesi-lib.ps1` untuk
bentuk berkas sesi, `gerbang-lib.ps1` untuk pengurai hasil test), lalu hook yang memakainya,
lalu cermin `.sh`. Alasan desain **ditulis sekali di `.ps1`**; berkas `.sh` cukup berkata
"alasan desain ada di sana" (`pre-commit-gate.sh`, `transkrip-ringkas.sh`). Dua salinan
alasan = satu yang menyimpang.

Hook yang tidak boleh memblokir (`sesi-sentuh`, `sesi-selesai`) dinyatakan begitu di baris
pertama dan `$ErrorActionPreference = 'SilentlyContinue'`; gagal menulis papan bukan alasan
menahan prompt orang.

### 5. `init.ps1` dan `init.sh` bersamaan

Bila ada folder baru yang harus disalin (`agents/` di 1.15.0), daftar folder di `init.ps1:42`
dan padanannya di `init.sh` diubah **dalam giliran yang berdekatan** [16:22:53, 16:23:14].
`settings.json` ditulis **programatik** lewat hashtable → `ConvertTo-Json` → `WriteAllText`
UTF-8 tanpa BOM (`init.ps1:52-74`), jangan template string: path Windows berisi backslash
yang harus di-escape JSON.

Hook lama yang digantikan dihapus lewat `git rm` di vault, bukan `Remove-Item`, supaya
penghapusannya ikut ter-stage [16:26:44].

### 6. Jalankan `test-init.ps1` sampai "Semua lulus"

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<kit>\tests\test-init.ps1" 2>&1 |
  Select-String -Pattern "FAIL|gagal|lulus"
```

Bentuk yang lebih informatif saat sudah hampir hijau [16:42:27]: kumpulkan seluruh baris,
cetak jumlah `PASS`, lalu tampilkan **hanya baris non-PASS**. Test ini membuat sandbox di
`$env:TEMP\agentkit-test-*`, menyalin kit nyata ke vault tiruan, menjalankan `init`
sungguhan, lalu memanggil hook dengan stdin JSON persis seperti Claude Code. Durasi di sesi
itu belasan detik sampai ~1 menit; beri `timeout` 240000.

### 7. Kontrol positif LANGSUNG di sesi hidup (bukan cuma test-init)

Ini langkah yang **menangkap cacat yang test-init lewatkan** [16:49:16 → 16:52:48]. Untuk
gerbang `PreToolUse`, setelah `init` menulis ulang `settings.json` (hook terbaca live, tanpa
restart), buat repo sementara di `main` lalu jalankan perintah yang seharusnya ditolak
**lewat tool PowerShell sesi ini sendiri**:

```powershell
$t = Join-Path $env:TEMP ("gate-live-" + [guid]::NewGuid().ToString('N').Substring(0,6))
New-Item -ItemType Directory -Force -Path $t | Out-Null
git -C $t init -q; git -C $t config user.email t@x.invalid; git -C $t config user.name t
git -C $t checkout -q -b main; git -C $t commit -q --allow-empty -m init
# --- perintah yang HARUS ditolak, dijalankan sebagai tool call terpisah: ---
git -C "<path literal $t>" commit --allow-empty -m "uji gerbang: harus DITOLAK"
"EXIT=$LASTEXITCODE (kalau baris ini tercetak, gerbang TIDAK menolak)"
```

Idiomnya: baris terakhir **tidak boleh pernah tercetak**. Kalau tercetak, gerbangnya
gagal-terbuka, dan itu persis yang terjadi pada bentuk `git -C $t commit` dengan `$t` dari
`Join-Path` [16:52:48]. Ulangi dengan **setiap bentuk perintah git yang benar-benar dipakai
tim** (`-C "<path>" -c core.fsmonitor=false`, `cd <repo>; git commit`, `$v="<path>"; git -C $v`).
Setiap bentuk yang lolos padahal seharusnya ditolak **naik jadi kasus di `test-init.ps1`**
di giliran yang sama [16:51:21], supaya tidak diulang.

Kontrol negatifnya: perintah yang sama di branch fitur harus mencetak `EXIT=0`.

### 8. Hook git (`githooks/pre-push`) dibuktikan lewat `--dry-run`

Dari worktree bersih yang sama dengan `origin/main` [16:46:43]:

```powershell
git -C <worktree> -c core.fsmonitor=false push --dry-run origin HEAD:refs/heads/tmp-agentkit-probe
```

Hook harus terlihat berjalan di keluaran. Sesudahnya **pastikan branch probe tidak pernah
sampai ke remote** [17:00:07]:

```powershell
git -C <repo> -c core.fsmonitor=false ls-remote --heads origin tmp-agentkit-probe   # harus kosong
```

### 9. Pasang ke workspace nyata, lalu jalankan satu skrip sungguhan

Re-init penuh [16:46:06]:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<kit>\init.ps1" -Workspace "<ws>" -ActiveProject bip-erp
```

Keluarannya harus menyebut versi baru dan, bila hooksPath dipasang, `(pre-push terpasang: ...)`.
Jalur cepat saat hanya **satu** hook yang baru diperbaiki dan `settings.json` tidak berubah
[16:48:45, 16:51:52]:

```powershell
Copy-Item "<kit>\hooks\<x>.ps1" "<ws>\.claude\hooks\<x>.ps1" -Force
```

Lalu jalankan skrip barunya **atas workspace nyata**, bukan sandbox (`papan-sesi.ps1` atas
`<ws>` [16:47:34]; `worktree-baru.ps1` atas repo nyata [16:47:58]). Langkah inilah yang
menemukan `$ErrorActionPreference='Stop'` mematikan `worktree-baru.ps1` di tengah jalan
(§ Jebakan, butir 4); sandbox test-init tidak pernah memanggil git yang menulis ke stderr
saat sukses.

### 10. Agen kustom baru menuntut **restart sesi**

Setelah `init` menyalin `agents/*.md`, tool `Agent` di sesi berjalan tetap membalas
`Agent type 'loop-fix' not found`, baik dengan nama frontmatter maupun path berkas
[16:51:28, 16:51:47]. Hook dan command terbaca live; agen **tidak**. Jalan darurat satu kali
yang dipakai [16:53:10]: dispatch `general-purpose` dengan isi berkas agen disisipkan sebagai
pembuka prompt, dan catat di log bahwa model serta batas tools-nya berbeda. Sudah tertulis di
`commands/kerjakan.md:52-56`.

### 11. Bump versi dan dokumen

Hanya bila `commands/`, `hooks/`, `skills/`, atau `agents/` berubah (hook session-start
membandingkan versi, jadi bump palsu menyuruh seluruh tim re-init tanpa alasan):

- `VERSION` [16:39:23], entri baru di `README.md` §Changelog yang menyebut **kenapa**, bukan
  cuma apa, dan ditutup "Butuh re-init" atau "Butuh re-init + restart sesi" bila ada agen
  [16:39:13]. Bagian "Isi kit" ikut diperbarui bila ada folder baru.
- `docs/<tanggal>-<slug>-design.md` untuk keputusan yang punya alasan [16:39:02].
- Dok vault yang menyebut `init` atau flow: `DEVELOPER GUIDE.md`, `Runbooks/RUN - Onboarding
  Developer Baru.md`, `templates/workspace-CLAUDE.md` [16:35:18, 16:43:51 sampai 16:44:23].
  Perhatikan kalimat lama yang sudah salah (contoh yang ditemukan: "push ke `main` → deploy
  otomatis", diganti karena pipeline `disabled_manually`).
- Regenerasi `VAULT-INDEX.json` (skill `/index-vault`), stage **per nama berkas**, commit,
  merge `origin/main`, push [16:47:32, 17:00:40, 17:02:23].

---

## Jebakan yang sudah terbukti (2026-09-06, semua di sesi yang sama)

Keenamnya sekelas: **gagalnya tidak terbaca sebagai gagal**. Tiga di antaranya membuat
gerbang gagal-terbuka, yaitu kegagalan terburuk untuk sebuah gerbang.

1. **Harness test memanggil hook lewat pipeline, dan pesan penolakan yang BENAR
   menghentikan test.** [16:31:00 → 16:32:55 → 16:41:36] `$json | powershell -File hook.ps1
   2>$err` di bawah `$ErrorActionPreference='Stop'`: PS 5.1 membungkus stderr proses anak
   jadi `ErrorRecord`, jadi gerbang yang menulis "DITOLAK" ke stderr justru mematikan
   harness-nya. Bentuk `& powershell ...` sama saja. Yang bekerja: `Start-Process` dengan
   `RedirectStandardInput/Output/Error` ke berkas, `-Wait -PassThru`, lalu baca `.ExitCode`
   (`test-init.ps1:14-27`).

2. **`-eq` PowerShell tidak peka huruf, jadi `-c core.fsmonitor=false` menimpa path dari
   `-C`.** [16:38:19] Tokenizer gerbang memakai `-eq '-C'`, dan `-c` cocok juga. Perintah git
   yang **seluruh tim** pakai (`git -C <repo> -c core.fsmonitor=false commit`) membuat path
   repo berganti jadi `core.fsmonitor=false`, repo tak dikenali, gerbang lolos. Pakai `-ceq`
   (`pre-commit-gate.ps1:75-78`). Tertangkap kontrol positif test-init, bukan oleh membaca kode.

3. **Parameter fungsi bernama `$args` diam-diam kosong.** [16:46:01] `$args` adalah variabel
   otomatis PowerShell; menamai parameter begitu membuat daftar argumen kosong **tanpa galat**,
   skrip yang dipanggil lalu gagal di parameter wajib dan exit 1, dan gejalanya terbaca seperti
   skrip yang dites yang salah. Ganti nama (`$argsSkrip`, `test-init.ps1:16-18`).

4. **`$ErrorActionPreference='Stop'` di skrip yang memanggil git mematikannya saat git
   SUKSES.** [16:48:12 → 16:48:39 → 16:48:45] `git worktree add` menulis "Preparing worktree
   ..." ke stderr pada jalur sukses; di bawah `Stop`, PS 5.1 mengubahnya jadi galat
   terminating. `worktree-baru.ps1` mati dengan exit 1 **sesudah** worktree setengah jadi,
   dan `/kerjakan` membaca `install.lolos` false. Pakai `'Continue'` dan periksa
   `$LASTEXITCODE` sendiri (`worktree-baru.ps1:16-19`). Sisa worktree parsial harus dibersihkan
   sebelum mencoba lagi (folder ada, tapi belum terdaftar di `git worktree list`).

5. **Gerbang gagal-terbuka pada path dari ekspresi, dan test-init hijau.** [16:49:16,
   16:52:48 → 16:51:02, 16:51:06, 16:51:21] `git -C $t commit` dengan `$t = Join-Path ...`
   di baris sebelumnya: gerbang tak bisa mengurai `$t`, jatuh ke `cwd`, `cwd` bukan repo,
   lolos. Yang menangkapnya kontrol positif **langsung** (§ Prosedur 7), bukan test-init,
   karena test-init saat itu hanya memuat bentuk literal. Perbaikannya **gagal-tertutup**:
   `commit` ada tapi repo tak terurai → tolak dengan pesan yang menyarankan path literal
   (`pre-commit-gate.ps1:10-15, 89-95`). Setiap gerbang harus dijawab: "bila saya tidak bisa
   menentukan keadaannya, saya menolak atau meloloskan?" Untuk gerbang, jawabannya menolak.

6. **`git commit -m` dengan tanda kutip ganda di dalam pesan.** [16:57:45 → 16:58:44] PS 5.1
   memecah argumen native pada kutip ganda; git membaca sisa pesan sebagai pathspec, commit
   gagal, dan **push berikutnya tetap jalan mendorong branch tanpa commit**. Tulis pesan ke
   berkas lewat `[IO.File]::WriteAllText(<path>, <pesan>, (New-Object Text.UTF8Encoding $false))`
   lalu `git commit -F <path>` (`commands/kerjakan.md:104-107`). Sekelas dengan memori privat
   `powershell-commit-message-file`; here-string `@'...'@` **tidak** cukup.

Yang **tidak** diulang di sini karena sudah ada di team-memory dan hanya ditegaskan ulang
oleh sesi ini: tool `Bash` praktis mati di mesin Windows (semua perintah di atas lewat tool
PowerShell), dan worktree di path panjang mematikan vitest (alasan `worktree-baru.ps1`
menolak path > 60 karakter, `:33`).

---

## Gerbang verifikasi

Perubahan kit belum selesai sampai **semua** ini terpenuhi, dan tiap butir punya bukti yang
bisa ditempel, bukan kalimat "sudah dites":

1. `test-init.ps1` mencetak `Semua lulus` dan **nol** baris non-PASS. Jumlah PASS disebut.
2. Untuk hook yang menolak: kontrol positif langsung (§7) **tidak** mencetak baris `EXIT=`,
   dan kontrol negatif di branch fitur mencetak `EXIT=0`. Dijalankan untuk tiap bentuk
   perintah yang tim pakai, bukan satu bentuk.
3. Untuk `githooks/*`: `push --dry-run` menunjukkan hook berjalan, dan `ls-remote` branch
   probe kosong.
4. Re-init di workspace nyata: keluaran menyebut versi baru, `.claude/.kit-version` sama
   dengan `VERSION`, jumlah berkas `.claude/commands|agents` sama dengan kit.
5. Satu skrip baru dijalankan **atas data nyata** (workspace, repo, transkrip sesi nyata),
   bukan hanya sandbox.
6. Bila menambah agen: sesudah restart sesi, `Agent` dengan `subagent_type: <nama>` resolve.
   **TBD**: di sesi 2026-09-06 restart belum dilakukan; bukti ini belum pernah diambil.
7. `README.md` §Changelog punya entri versi baru yang menyebut "Butuh re-init".

Bukti akhir yang dipakai sesi itu untuk seluruh loop: satu `/kerjakan` sungguhan sampai PR
terbuka (bip-erp #1739, `gh pr view` membalas `OPEN` [17:00:48]). Untuk perubahan hook
tunggal, gerbang 1 sampai 5 cukup.

---

## Yang tidak dicakup

- **Merancang apa yang hook-nya lakukan.** Itu `/plan` dan, bila menyentuh wewenang agent,
  ADR (contoh: ADR 0077 untuk gerbang commit).
- **Cermin `.sh` untuk mac/linux.** **TBD**: tidak satu pun `.sh` dijalankan di sesi
  2026-09-06 (tool Bash mati di mesin ini), dan `test-init.ps1` hanya menguji `.ps1`. Belum
  ada bukti cermin `.sh` benar; siapa pun di mac/linux yang pertama memakainya adalah
  penguji pertamanya.
- **CI untuk `test-init.ps1`.** Tidak ada, dan keputusan biaya GitHub Actions ditolak pemilik
  (ADR 0077). Satu-satunya penjaga adalah orang yang menjalankan langkah 6 sebelum push.
- **Isi `settings.json` di luar yang ditulis `init`** (permission, env). Skill `update-config`
  untuk itu.
