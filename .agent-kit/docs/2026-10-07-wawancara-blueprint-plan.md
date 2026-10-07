# `/analisa-kebutuhan` wawancara pilihan ganda + blueprint issue — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/analisa-kebutuhan` bertanya bentuk lewat pilihan ganda bersumber kode, dan keluarannya jadi draf issue Siap Agent berukuran Kecil/Sedang/Besar yang dibuat di GitHub setelah disetujui.

**Architecture:** Hanya berkas Markdown command (`commands/analisa-kebutuhan.md`) yang berubah; perilakunya dijaga pemeriksaan teks di `tests/test-init.ps1`, dibuktikan merah lebih dulu terhadap berkas lama. Pembuatan issue memakai `gh` + `hooks/buat-sub-issue.ps1` yang sudah ada.

**Tech Stack:** Markdown command agent-kit, PowerShell 5.1 (`test-init.ps1`), `gh` CLI.

**Spec:** `architecture-draft/.agent-kit/docs/2026-10-07-wawancara-blueprint-design.md`

## Global Constraints

- Total pertanyaan kebutuhan ≤ 7 (Q1-Q5 + ≤ 2 lanjutan); pertanyaan Pemutus tidak dihitung.
- Q1-Q2 terbuka, satu per pesan; Q3-Q5 `AskUserQuestion` ≤ 3 dalam satu panggilan.
- Tiap opsi menyebut sumbernya; selalu ada opsi "Belum tahu" → asumsi eksplisit.
- Issue dibuat **TANPA label `Siap Agent`** dan tanpa assignee; label dipasang manusia (ADR 0151).
- Keputusan di issue menunjuk ADR **dengan judul**, tidak menyalin isi.
- Vault: commit di `main`, stage per nama berkas, tanpa trailer `Co-Authored-By`; push lewat worktree sementara bila pohon bersama kotor milik sesi lain.
- Versi kit: satu minor di atas `VERSION` di `origin/main`, dicek **saat bump dan sebelum push**.
- Tool `Bash` tidak dipakai (hang di mesin ini): PowerShell.

## Review Focus

1. **Grounding tak menemukan apa pun untuk Q3-Q5** → pertanyaan tetap diajukan dengan opsi "bangun baru" berlabel + "Belum tahu", bukan dilewati. Teks di Task 1 §1b butir 4.
2. **Kebutuhan disimpulkan "tidak perlu dibangun"** → §5d tak berjalan, tak ada issue. Teks di Task 2 §5d kalimat penutup; pemeriksaan di Task 2.
3. **`gh` tanpa scope `project`** → issue tetap dibuat, item-add gagal tercatat + perintah refresh. Teks di Task 2 §5d butir 6.
4. **§5d dijalankan ulang sesudah gagal sebagian** → tak ada issue ganda (pencarian judul + skrip idempoten). Teks di Task 2 §5d butir 1, 5.
5. **Repo mobile bernama `my-bharata` di GitHub, folder lokal `mybharata-app`** → `buat-sub-issue.ps1 -Repo my-bharata`. Teks di Task 2 tabel ukuran / §5d butir 2.

---

### Task 1: Wawancara pilihan ganda (§1a, §1b, §3)

**Files:**
- Modify: `architecture-draft/.agent-kit/commands/analisa-kebutuhan.md` (§1 seluruhnya; sisipan sesudah akhir §2; §3)
- Modify: `architecture-draft/.agent-kit/tests/test-init.ps1` (sesudah baris `Check ($akMd -match '/dampak') ...`)
- Create (scratch, tidak di-commit): `<scratchpad>/cek-analisa.ps1`

**Interfaces:**
- Produces: penanda blok test-init `# analisa-kebutuhan wawancara+blueprint` … `# akhir analisa-kebutuhan wawancara+blueprint` (Task 2 menambah pemeriksaan di dalam blok ini); heading `## 1a. Wawancara niat`, `## 1b. Wawancara bentuk`.

- [ ] **Step 1: Tulis pemeriksaan yang gagal** — sisipkan di `test-init.ps1` sesudah baris `Check ($akMd -match '/dampak') '/analisa-kebutuhan memanggil /dampak'`:

```powershell
  # analisa-kebutuhan wawancara+blueprint (spec 2026-10-07-wawancara-blueprint-design)
  $ak = Get-Content (Join-Path $claude 'commands/analisa-kebutuhan.md') -Raw -Encoding UTF8
  $i1a = $ak.IndexOf('## 1a. Wawancara niat'); $i2 = $ak.IndexOf('## 2. Grounding'); $i1b = $ak.IndexOf('## 1b. Wawancara bentuk')
  Check ($i1a -ge 0 -and $i2 -gt $i1a -and $i1b -gt $i2) '/analisa-kebutuhan: urutan niat -> grounding -> bentuk'
  Check ($ak -match 'AskUserQuestion' -and $ak -match 'menyebut sumbernya' -and $ak -match 'Belum tahu') '/analisa-kebutuhan: pilihan ganda bersumber + Belum tahu'
  # akhir analisa-kebutuhan wawancara+blueprint
```

Lalu tulis `<scratchpad>/cek-analisa.ps1` (menjalankan blok itu atas berkas kit, tanpa init penuh):

```powershell
param([string]$Kit = 'c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit')
$t = Get-Content (Join-Path $Kit 'tests/test-init.ps1') -Raw -Encoding UTF8
$i = $t.IndexOf('  # analisa-kebutuhan wawancara+blueprint'); $j = $t.IndexOf('# akhir analisa-kebutuhan wawancara+blueprint')
if ($i -lt 0 -or $j -lt 0) { Write-Host 'blok tak ditemukan'; exit 2 }
$claude = Join-Path $env:TEMP 'cek-analisa'; Remove-Item $claude -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force (Join-Path $claude 'commands') | Out-Null
Copy-Item (Join-Path $Kit 'commands/analisa-kebutuhan.md') (Join-Path $claude 'commands')
$script:fail = 0
function Check($cond, $name) { if ($cond) { Write-Host "PASS $name" } else { Write-Host "FAIL $name"; $script:fail++ } }
Invoke-Expression $t.Substring($i, $j - $i)
Remove-Item $claude -Recurse -Force
Write-Host "gagal: $script:fail"; exit $script:fail
```

- [ ] **Step 2: Jalankan, pastikan gagal**

Run: `& "<scratchpad>\cek-analisa.ps1"`
Expected: `FAIL ... urutan niat -> grounding -> bentuk`, `FAIL ... pilihan ganda bersumber + Belum tahu`, `gagal: 2`.

- [ ] **Step 3: Ganti §1 seluruhnya** (dari `## 1. Wawancara` sampai sebelum `## 2. Grounding`) dengan:

```markdown
## 1a. Wawancara niat

Dua pertanyaan **terbuka**, satu per pesan, **sebelum** grounding. Jawabannya tidak ada di kode,
dan keduanya mempertajam apa yang dicari subagent di §2:

1. **Keputusan apa yang diambil dari ini, oleh siapa?** Memisahkan kebutuhan dari solusi. Bila
   tidak ada keputusan yang berubah, yang diminta laporan hiasan, dan itu layak dikatakan.
2. **Sekarang orangnya bagaimana?** Selalu sudah ada cara manual. Menunjukkan data sumbernya
   hidup di mana, dan sering mengungkap modul yang sudah menyelesaikan separuh masalahnya.

Lewati yang sudah dijawab kalimat pembuka user atau indeks. Jawaban "tidak tahu" dicatat sebagai
**asumsi eksplisit**, jangan mandek menunggu.

```

- [ ] **Step 4: Sisipkan §1b** tepat sebelum `## 3. Pertanyaan lanjutan` (sesudah paragraf "**Subagent tidak dipercaya buta.**" di akhir §2):

```markdown
## 1b. Wawancara bentuk

Tiga pertanyaan yang membelokkan arsitektur, diajukan **sesudah** grounding supaya opsinya
berdiri di atas kode yang sudah ada, bukan tebakan:

3. **Sesering apa dilihat, seberapa segar datanya harus?** Pembelok paling keras: query langsung
   vs mart terjadwal vs cron. Berbeda ongkos dan berbeda mode gagal.
4. **Siapa yang boleh melihat?** Menentukan keterlibatan RBAC, jebakan HRGA, prinsip tiga lapis
   kalender, dan data pribadi orang lain.
5. **Apa akibatnya bila angkanya salah?** Angka untuk menggaji orang menuntut gerbang yang sama
   sekali berbeda dari angka untuk rapat mingguan.

Ajukan lewat **`AskUserQuestion`**, paling banyak tiga pertanyaan dalam **satu** panggilan. Aturan opsi:

1. **Tiap opsi menyebut sumbernya** di deskripsi: `file:line`, nama koleksi/mart, atau judul dok/ADR
   dari hasil §2. Opsi tanpa sumber hanya boleh sebagai alternatif **"bangun baru"**, dan dilabeli begitu.
2. `(Recommended)` hanya bila grounding mendukungnya, dengan alasan satu kalimat; opsi itu di urutan pertama.
3. Selalu ada opsi **"Belum tahu"**: dicatat sebagai **asumsi eksplisit** di ADR, tak mandek.
4. Pertanyaan yang **sudah terjawab grounding tidak ditanyakan**; jawabannya disajikan sebagai temuan
   di §4. Bila grounding tak menemukan apa pun yang relevan, pertanyaannya **tetap diajukan** dengan
   opsi "bangun baru" berlabel + "Belum tahu", bukan dilewati.

Contoh Q3: "pakai mart `<nama>` yang sudah ada, segar H-1 (`<berkas>:<baris>`)" ·
"query langsung ke `<koleksi>` (bangun baru; jalur daftar berpaginasi, risiko compute-on-read)" · "Belum tahu".

```

- [ ] **Step 5: Ganti badan §3** (paragraf di bawah `## 3. Pertanyaan lanjutan`) dengan:

```markdown
Maksimum 2, dan hanya yang **baru bisa muncul setelah baca kode**, misalnya "ternyata sudah ada X
yang menyelesaikan 70% ini, dipakai ulang atau dipisah?". Ajukan lewat `AskUserQuestion` dengan
aturan opsi §1b. Total pertanyaan kebutuhan sepanjang command ini tidak pernah lebih dari 7.
Sisanya jadi asumsi tertulis.
```

- [ ] **Step 6: Jalankan, pastikan lolos**

Run: `& "<scratchpad>\cek-analisa.ps1"`
Expected: 2 × `PASS`, `gagal: 0`. Periksa juga tak ada lagi heading `## 1. Wawancara`:
`Select-String -LiteralPath architecture-draft\.agent-kit\commands\analisa-kebutuhan.md -Pattern '^## 1\. Wawancara'` → kosong.

- [ ] **Step 7: Commit**

```powershell
git -c core.fsmonitor=false -C architecture-draft add -- ".agent-kit/commands/analisa-kebutuhan.md" ".agent-kit/tests/test-init.ps1"
git -c core.fsmonitor=false -C architecture-draft commit -m "feat(kit): /analisa-kebutuhan wawancara pilihan ganda bersumber grounding"
```

---

### Task 2: Blueprint issue (§4, §5c, §5d, §8)

**Files:**
- Modify: `architecture-draft/.agent-kit/commands/analisa-kebutuhan.md` (§4 daftar sajian; §5 kalimat pembuka + butir c; butir d baru; §8)
- Modify: `architecture-draft/.agent-kit/tests/test-init.ps1` (di dalam blok Task 1)

**Interfaces:**
- Consumes: blok test-init + `cek-analisa.ps1` dari Task 1.
- Produces: penanda `**d. Buat issue` di §5.

- [ ] **Step 1: Tulis pemeriksaan yang gagal** — sisipkan tepat sebelum baris `  # akhir analisa-kebutuhan wawancara+blueprint`:

```powershell
  # -cmatch atas penanda tebal: -match tak peka huruf, dan 'Besar' sudah cocok "besaran kerja" di §5a
  Check ($ak -cmatch '\*\*Kecil\*\*' -and $ak -cmatch '\*\*Sedang\*\*' -and $ak -cmatch '\*\*Besar\*\*' -and $ak -match 'tugas\.md') '/analisa-kebutuhan: blueprint berukuran, format tugas.md'
  $i5d = $ak.IndexOf('**d. Buat issue'); $s5d = if ($i5d -ge 0) { $ak.Substring($i5d, [Math]::Min(3500, $ak.Length - $i5d)) } else { '' }
  Check ($s5d -match 'buat-sub-issue\.ps1' -and $s5d -match 'item-add 15' -and $s5d -match 'TANPA label' -and $s5d -match 'tidak perlu dibangun') '/analisa-kebutuhan 5d: buat issue tanpa Siap Agent'
```

- [ ] **Step 2: Jalankan, pastikan gagal**

Run: `& "<scratchpad>\cek-analisa.ps1"`
Expected: 2 PASS (Task 1), 2 FAIL (blueprint, 5d), `gagal: 2`.

- [ ] **Step 3: §4** — di daftar "Sajikan di chat:", sesudah butir `- **Dok terdampak** ...` tambahkan:

```markdown
- **Blueprint**: daftar issue yang akan dibuat (judul, repo, ukuran Kecil/Sedang/Besar, urutan),
  lihat §5c. Tanyakan **Pemutus** (login GitHub) lewat `AskUserQuestion`; pertanyaan ini tidak
  dihitung dalam batas 7. Satu persetujuan mencakup ADR, dok, dan pembuatan issue.
```

- [ ] **Step 4: §5** — ganti `Tiga berkas, semuanya di `architecture-draft`.` dengan
`Tiga berkas di `architecture-draft`, lalu issue di repo kode.` Lalu ganti seluruh butir **c** dengan:

```markdown
**c. Blueprint di `Workspace/ANALISA - <judul>.md`.** Kumpulan **draf issue** yang lolos checklist
Siap Agent (team-memory § Definition of Ready, ADR 0151 "Issue Siap Dikerjakan Agent Bila
Keputusannya Bisa Ditunjuk, Ditandai Manusia"). Sengaja tidak di dalam ADR: ADR adalah keputusan,
blueprint papan kerja.

Kepala: wikilink ADR + dok domain, **ukuran** + alasannya, Pemutus. Ukuran ditentukan dari repo
yang ditemukan grounding:

| Ukuran | Kapan | Bentuk |
|---|---|---|
| **Kecil** | 1 repo, 1 PR | 1 issue, tanpa induk |
| **Sedang** | > 1 repo | induk di repo tempat kontrak lahir (biasanya `bip-erp`, tanpa PR sendiri) + 1 sub-issue `[BE]`/`[FE]`/`[Mobile]` per repo |
| **Besar** | ada repo yang butuh > 1 PR | seperti Sedang + sub-issue **saudara** "bagian i/N" di bawah induk yang sama; tak pernah sub di bawah sub |

Tiap issue satu blok berbagian persis template `bip-erp/.github/ISSUE_TEMPLATE/tugas.md`:
`**Pemutus:**` / `**PIC:**`, `## Masalah`, `## Keputusan`, `## Yang harus benar`,
`## Di luar cakupan`, `## Data / bukti pendukung`, `## Prasyarat`; ditambah repo tujuan
(`bip-erp`, `erp-frontend`, `my-bharata`; folder lokal mobile `mybharata-app`) dan urutan.

- **Keputusan** menunjuk ADR **dengan judul** (nomor ADR bukan kunci unik), tidak menyalin isinya,
  dan menulis terang: *layak `Siap Agent` sesudah ADR berstatus Diterima* (ADR baru masih 🟡 Diusulkan).
- **Yang harus benar** diturunkan dari `## Decision` jadi kriteria yang bisa diperiksa (perilaku,
  angka, layar). "Pertimbangkan", "perlu disepakati", "dsb" dilarang.
- **Data** diisi hasil ukur prod gerbang 3 §2; tak tersedia → ditulis sebagai asumsi.
- **Prasyarat**: urutan deploy BE sebelum FE/Mobile ditulis di sub-issue FE/Mobile.
```

- [ ] **Step 5: Tambah butir d** sesudah butir c:

```markdown
**d. Buat issue** (sesudah a-c, **sebelum** commit vault), dari akar `erp/`, via PowerShell:

1. Induk / issue tunggal: cari dulu
   `gh issue list --repo bip-itteam-internal/<repo> --state all --search "<judul> in:title"`;
   belum ada → tulis badan ke berkas scratchpad, `gh issue create --repo bip-itteam-internal/<repo> --title "<judul>" --body-file <berkas>`,
   lalu `gh project item-add 15 --owner bip-itteam-internal --url <url>`.
2. Sub-issue: `& '.claude/hooks/buat-sub-issue.ps1' -Induk <repo>#<n> -Repo <bip-erp|erp-frontend|my-bharata> -Judul '<judul>' -Badan <badan>`
   (idempoten, memasukkan ke Project #15, menyalin Area + Prioritas induk).
3. **TANPA label `Siap Agent`**, tanpa assignee: label dipasang manusia (ADR 0151), assignee saat In Progress.
4. Tulis nomor + URL tiap issue balik ke blok-nya di ANALISA, supaya vault di-commit sekali di §7.
5. **Gagal sebagian**: laporkan yang terbuat (URL) dan yang gagal (galat); jangan ulang buta.
   Menjalankan ulang langkah ini aman karena butir 1-2 idempoten.
6. `gh` tanpa scope `project` → issue tetap dibuat; catat item-add yang gagal dan perintah
   `gh auth refresh -h github.com -s project` di laporan.

Bila kesimpulannya **"tidak perlu dibangun"**, butir c dan d tidak dijalankan: tak ada blueprint, tak ada issue.
```

- [ ] **Step 6: §8** — ganti badannya dengan:

```markdown
Tutup dengan daftar URL issue yang dibuat (induk dulu), lalu langkah manusia berikutnya, konkret:
setujui ADR dengan menulis `🟢 Diterima, <tanggal>, oleh <login>` di baris statusnya, lalu pasang
label `Siap Agent` pada issue yang lolos checklist Definition of Ready. Sebelum dua langkah itu,
runner backlog tidak akan mengambil issue-nya.
```

- [ ] **Step 7: Jalankan, pastikan lolos**

Run: `& "<scratchpad>\cek-analisa.ps1"`
Expected: 4 × `PASS`, `gagal: 0`.

- [ ] **Step 8: Commit**

```powershell
git -c core.fsmonitor=false -C architecture-draft add -- ".agent-kit/commands/analisa-kebutuhan.md" ".agent-kit/tests/test-init.ps1"
git -c core.fsmonitor=false -C architecture-draft commit -m "feat(kit): /analisa-kebutuhan blueprint issue Siap Agent berukuran + pembuatan issue"
```

---

### Task 3: Rilis kit, uji kering, push

**Files:**
- Modify: `architecture-draft/.agent-kit/rules/team-memory.md` (§ Skill & tooling, sesudah butir `/dampak`)
- Modify: `architecture-draft/.agent-kit/VERSION`, `architecture-draft/.agent-kit/README.md` (§ Changelog paling atas)

**Interfaces:**
- Consumes: Task 1-2.

- [ ] **Step 1: Tetapkan versi** — `git -C architecture-draft fetch -q origin`; `git -C architecture-draft show origin/main:.agent-kit/VERSION` → naikkan satu minor (mis. `1.37.0` → `1.38.0`). Tulis ke `VERSION` (7 byte, LF akhir, tanpa BOM).

- [ ] **Step 2: team-memory** — sesudah butir `- **`/dampak` (kit ≥ ...)`:

```markdown
- **`/analisa-kebutuhan` (kit ≥ <versi>) bertanya bentuk lewat pilihan ganda bersumber kode, dan
  keluarannya draf issue Siap Agent** (Kecil/Sedang/Besar) yang dibuat di GitHub setelah disetujui,
  **tanpa** label `Siap Agent`: label tetap dipasang manusia sesudah ADR-nya Diterima (ADR 0151).
```

- [ ] **Step 3: Changelog** — paling atas § Changelog `README.md`:

```markdown
- **<versi>**: **`/analisa-kebutuhan`: wawancara pilihan ganda + blueprint issue Siap Agent** (ditiru dari speckit.tech). Pertanyaan bentuk (kesegaran, siapa boleh melihat, akibat bila salah) kini diajukan **sesudah** grounding lewat `AskUserQuestion`, tiap opsi menyebut sumbernya di kode, selalu ada "Belum tahu" yang jadi asumsi; pertanyaan niat tetap terbuka. `ANALISA - *.md` jadi blueprint: draf issue berformat `tugas.md`, ukuran Kecil (1 issue) / Sedang (induk + sub per repo) / Besar (+ sub saudara bagian i/N); §5d membuat issue via `gh` + `buat-sub-issue.ps1` ke Project #15 **tanpa** label `Siap Agent`. Alasan: 46 dari 52 issue runner berhenti di Butuh Info (ADR 0151); hasil analisa berisi keputusan tapi tak pernah sampai ke issue. Test: 4 pemeriksaan di `tests/test-init.ps1` (dibuktikan merah atas berkas lama). Spec + plan: `docs/2026-10-07-wawancara-blueprint-*`. **Butuh re-init.**
```

- [ ] **Step 4: test-init penuh** (background, lewat antrean):
`& "<erp>\.claude\hooks\antre.ps1" -- powershell -NoProfile -ExecutionPolicy Bypass -File "<erp>\architecture-draft\.agent-kit\tests\test-init.ps1"`
Expected: `Semua lulus`, 0 baris `FAIL`.

- [ ] **Step 5: Commit**

```powershell
git -c core.fsmonitor=false -C architecture-draft add -- ".agent-kit/rules/team-memory.md" ".agent-kit/VERSION" ".agent-kit/README.md"
git -c core.fsmonitor=false -C architecture-draft commit -m "chore(kit): rilis <versi> wawancara + blueprint /analisa-kebutuhan"
```

- [ ] **Step 6: Uji kering** — subagent `general-purpose` membaca `analisa-kebutuhan.md` hasil commit dan menjalankannya atas kebutuhan contoh *"manajemen ingin tahu toko marketplace mana yang ROAS-nya turun minggu ini"* sampai §4, **berhenti sebelum persetujuan**, tanpa membuat issue dan tanpa menulis berkas vault. Periksa: opsi Q3-Q5 menyebut sumber (`file:line`/koleksi/dok), ada "Belum tahu", draf issue berbagian `tugas.md` dan berukuran. Temuan yang menunjukkan teks command ambigu → perbaiki teksnya (commit terpisah), ulangi Step 4.

- [ ] **Step 7: Push** — cek ulang `origin/main:.agent-kit/VERSION` (bump lagi bila sudah diklaim). Bila `git status` vault memuat perubahan sesi lain yang menghalangi merge: worktree sementara `C:\Users\irfan\wt\vault-<slug>` dari `main`, `git merge origin/main` di sana (konflik VERSION → versi kita; README → simpan dua entri), commit, `git push origin <branch>:main` **di background**, re-init dari worktree itu (supaya `.claude/` memuat kit hasil merge), verifikasi `merge-base --is-ancestor <branch> origin/main`, hapus worktree + branch.
