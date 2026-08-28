# Rencana Implementasi: Command `/analisa-kebutuhan`

> **Untuk agentic worker:** REQUIRED SUB-SKILL: pakai `superpowers:subagent-driven-development`
> (disarankan) atau `superpowers:executing-plans` untuk mengeksekusi rencana ini task per task.
> Langkah memakai sintaks checkbox (`- [ ]`) untuk pelacakan.

**Goal:** Menambah command `/analisa-kebutuhan` ke agent-kit, yang menerjemahkan kebutuhan
manajemen mentah menjadi keputusan arsitektur tercatat (ADR + dok domain + daftar task) di vault,
dan berhenti sebelum kode.

**Architecture:** Slash command di `.agent-kit/commands/`, bukan subagent, karena perannya
menuntut tanya jawab dengan user dan subagent tidak bisa bertanya balik. Pembacaan lebar ke vault
dan tiga repo kode didelegasikan ke `Explore` paralel dari dalam command. Prosedur pencarian vault
yang kini tersalin di dua command diangkat ke `rules/vault-retrieval.md` karena command ini
menjadi pemakai ketiga.

**Tech Stack:** Markdown (prompt command), PowerShell (`init.ps1`, `tests/test-init.ps1`), Bash
(`init.sh`), git (vault `architecture-draft`).

**Spec:** [`.agent-kit/docs/2026-08-28-analisa-kebutuhan-command-design.md`](2026-08-28-analisa-kebutuhan-command-design.md)

## Global Constraints

- **Repo yang disunting hanya vault `architecture-draft`.** Tidak ada satu pun berkas di
  `bip-erp`, `erp-frontend`, atau `mybharata-app` yang diubah oleh rencana ini.
- **Vault push LANGSUNG ke `main`, tanpa PR.** Stage **per nama berkas**, jangan `git add -A`.
- **Git di workspace ini wajib `-c core.fsmonitor=false`**, karena path ber-spasi
  (`c:\Data utama\...`) membuat git menggantung tanpa flag itu.
- **Bash tool menggantung di sesi ini**; jalankan git dan skrip lewat PowerShell.
- **Bahasa artefak: Indonesia**, istilah teknis lazim English biarkan English.
- **Tanpa trailer `Co-Authored-By`** di pesan commit.
- **Versi kit naik `1.13.0` → `1.14.0`**, ditulis di `.agent-kit/VERSION` (satu baris, tanpa
  awalan `v`).
- **Perintah verifikasi tunggal untuk seluruh rencana:**
  `& "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\tests\test-init.ps1"`
- **Baseline sebelum rencana ini: MERAH**, 1 gagal, exit 1, pada assertion
  `jumlah command = 7 (6 flow + /ask)`. Task 1 memperbaikinya. Setelah Task 1 setiap task wajib
  berakhir hijau (`Semua lulus`, exit 0).

---

### Task 1: Perbaiki test kit yang sudah merah, dapatkan baseline hijau

Tidak ada yang bisa diverifikasi di atas test merah. `commands/` berisi 9 berkas
(`ask`, `implement`, `index-vault`, `plan`, `review`, `skills`, `start-task`, `sync-docs`,
`wrap`), sementara test mematok 7. Angka itu rot karena jumlah command adalah fakta yang hidup
di dua tempat: isi folder, dan literal di test. Perbaikannya bukan mengganti 7 jadi 9, melainkan
**menurunkan angkanya dari sumber**, supaya penambahan command berikutnya tidak mengulang ini.

**Files:**
- Modify: `.agent-kit/tests/test-init.ps1:26-28`

**Interfaces:**
- Consumes: tidak ada
- Produces: baseline hijau (`Semua lulus`, exit 0) yang dipakai semua task berikutnya

- [ ] **Step 1: Jalankan test untuk memastikan ia memang merah**

```powershell
& "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\tests\test-init.ps1"
"EXIT=$LASTEXITCODE"
```

Expected: `FAIL jumlah command = 7 (6 flow + /ask)`, lalu `1 gagal`, `EXIT=1`.

- [ ] **Step 2: Ganti assertion angka-mati jadi assertion turunan**

Di `.agent-kit/tests/test-init.ps1`, ganti dua baris ini:

```powershell
  $cmdCount = (Get-ChildItem (Join-Path $claude 'commands') -Filter *.md).Count
  Check ($cmdCount -eq 7) 'jumlah command = 7 (6 flow + /ask)'
```

menjadi:

```powershell
  # Jumlah command diturunkan dari kit, JANGAN dipatok angka: assertion angka-mati
  # sudah pernah rot diam-diam saat index-vault.md dan skills.md ditambahkan (2026-08-28).
  $srcCmd = (Get-ChildItem (Join-Path $kitRoot 'commands') -Filter *.md).Count
  $cmdCount = (Get-ChildItem (Join-Path $claude 'commands') -Filter *.md).Count
  Check ($cmdCount -eq $srcCmd) "semua command kit tersalin ($srcCmd berkas)"
```

- [ ] **Step 3: Jalankan test, pastikan hijau**

```powershell
& "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\tests\test-init.ps1"
"EXIT=$LASTEXITCODE"
```

Expected: `PASS semua command kit tersalin (9 berkas)`, lalu `Semua lulus`, `EXIT=0`.

- [ ] **Step 4: Kontrol negatif, buktikan assertion barunya benar-benar bisa merah**

Assertion yang tak pernah dilihat merah tidak membuktikan apa pun. Sisipkan berkas palsu ke
`.claude/commands` sandbox tidak mungkin (sandbox dihapus di `finally`), jadi buktikan dari sisi
sumber: tambah berkas sementara ke `commands/`, jalankan test, pastikan MERAH pada assertion itu,
lalu hapus.

```powershell
$c = "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\commands"
Set-Content -Path (Join-Path $c "__probe__.md") -Value "probe" -Encoding UTF8
& "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\tests\test-init.ps1"
"EXIT=$LASTEXITCODE"
```

Expected: tetap `Semua lulus`, `EXIT=0`, karena berkas probe ikut tersalin sehingga kedua sisi
tetap sama. **Ini justru membuktikan assertion barunya mengukur "semua tersalin", bukan
"jumlahnya 9".** Itu perilaku yang diinginkan. Hapus probe:

```powershell
Remove-Item (Join-Path $c "__probe__.md")
```

- [ ] **Step 5: Commit**

```powershell
$v = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git -C $v -c core.fsmonitor=false add ".agent-kit/tests/test-init.ps1"
git -C $v -c core.fsmonitor=false commit -m "fix(agent-kit): turunkan jumlah command di test dari kit, bukan angka mati

Assertion mematok 7 sementara commands/ berisi 9; test gagal diam-diam sejak
index-vault.md dan skills.md ditambahkan."
```

---

### Task 2: Ekstraksi prosedur pencarian vault ke `rules/vault-retrieval.md`

Prosedur pencarian vault tersalin utuh di `ask.md` dan `start-task.md`. Command baru akan jadi
salinan ketiga, dan team-memory menetapkan sendiri bahwa pemakai ketiga adalah saatnya mengangkat
abstraksi.

⚠️ **Perilakunya harus IDENTIK, bukan disempurnakan sekalian.** Penyempurnaan prosedur adalah
task terpisah. Ekstraksi yang mengubah perilaku adalah regresi.

**Files:**
- Create: `.agent-kit/rules/vault-retrieval.md`
- Modify: `.agent-kit/commands/ask.md` (langkah 1 sampai 2)
- Modify: `.agent-kit/commands/start-task.md` (langkah 2 sampai 3)

**Interfaces:**
- Consumes: baseline hijau dari Task 1
- Produces: berkas `rules/vault-retrieval.md` yang dirujuk Task 3 dengan kalimat rujukan persis
  `Ikuti `architecture-draft/.agent-kit/rules/vault-retrieval.md`.`

- [ ] **Step 1: Rekam perilaku sekarang sebagai kontrol**

Sebelum menyunting apa pun, jalankan `/ask` dengan satu pertanyaan yang jawabannya diketahui, dan
**catat daftar dokumen yang dipilihnya**. Ini pembanding satu-satunya untuk membuktikan ekstraksi
tidak mengubah perilaku.

```
/ask apa aturan penomoran ADR di vault
```

Catat: judul dokumen yang dibaca, dan status yang dilaporkan. Simpan di catatan task, bukan di
berkas.

- [ ] **Step 2: Tulis `rules/vault-retrieval.md`**

Isinya adalah gabungan prosedur yang kini ada di `ask.md` langkah 1 sampai 2 dan `start-task.md`
langkah 2 sampai 3, tanpa penambahan aturan baru:

```markdown
# Prosedur Pencarian Vault (dipakai bersama)

> Dirujuk oleh `/ask`, `/start-task`, dan `/analisa-kebutuhan`. **Satu tempat**: sebelum berkas
> ini ada, prosedur yang sama tersalin di dua command dan sempat menyimpang. Jangan menyalinnya
> lagi ke command baru, rujuk saja.

## 1. Pilih dokumen dari dua arah

a. `architecture-draft/CLAUDE.md` §7 memetakan **repo kode → dokumen**. Dipakai bila titik
   berangkatnya kode.
b. `architecture-draft/VAULT-INDEX.json` memetakan **pertanyaan → dokumen**. Cocokkan teks ke
   `ringkasan` dan `kata_kunci`, ambil **3 sampai 5** kandidat.

Sumbunya berbeda dan keduanya berguna; gabungkan hasilnya.

Bila indeks tidak ada, rusak, atau `versi_skema` tak dikenal, pakai (a) saja, **beri tahu user**
bahwa indeks tidak tersedia, dan sarankan `/index-vault`.

## 2. Baca dokumen terpilih SECARA UTUH

Jangan menyimpulkan dari ringkasan indeks.

## 3. Perhatikan status

Perhatikan `status_emoji` + `status_teks` di entri indeks dan marker di dokumennya:

| Marker | Arti |
|---|---|
| ✅ Implemented | ada di kode |
| ⚠️ | ada catatan penting |
| 🟡 Konsep | rencana, belum ada kodenya |
| 🔴 Stub | kerangka saja |
| 🔜 Direncanakan | belum dikerjakan |
| ⛔ Superseded | sudah digantikan, jangan dipakai |

Sekitar sepertiga dokumen **tidak punya status**: seluruh dok meta root dan seluruh `API - *`.
Itu normal, bukan gap.

## 4. Cocok topik bukan berarti menjawab

Indeks selalu mengembalikan dokumen terdekat, bahkan ketika jawabannya belum pernah ditulis.
Setelah membaca, tanya diri sendiri apakah pertanyaannya benar-benar terjawab atau dokumen itu
cuma sebidang topik. Bila cuma sebidang, katakan begitu dan sebut apa yang belum ada. Diuji
2026-07-20: "berapa lama masa percobaan karyawan" dan "kenapa gaji telat cair" mengembalikan
dokumen recruitment dan payroll yang relevan topiknya tapi tidak memuat jawabannya.
```

- [ ] **Step 3: Ganti salinan di `ask.md` jadi rujukan**

Ganti seluruh blok langkah 1 dan 2 di `.agent-kit/commands/ask.md` (dari `1. Baca
`architecture-draft/VAULT-INDEX.json`` sampai sebelum `3. Bila vault mencakup pertanyaan`)
menjadi:

```markdown
1. Pilih dan baca dokumen vault. Ikuti `architecture-draft/.agent-kit/rules/vault-retrieval.md`.
2. Bila pertanyaannya berangkat dari kode, §7 tetap dipakai berdampingan dengan indeks
   (prosedurnya sudah menjelaskan kapan masing-masing dipakai).
```

Paragraf penutup `ask.md` tentang "Cocok topik ≠ menjawab pertanyaan" **dihapus dari sini**
karena sudah pindah ke §4 rulebook. Jangan disimpan di dua tempat.

- [ ] **Step 4: Ganti salinan di `start-task.md` jadi rujukan**

Ganti blok langkah 2 dan 3 di `.agent-kit/commands/start-task.md` menjadi:

```markdown
2. Pilih dan baca dokumen arsitektur yang relevan dengan task ini. Ikuti
   `architecture-draft/.agent-kit/rules/vault-retrieval.md`.
```

Lalu renumber langkah sesudahnya (`4. Baca kode terkait` jadi `3.`, dan seterusnya sampai
`6. BERHENTI` jadi `5.`).

- [ ] **Step 5: Jalankan test kit**

```powershell
& "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\tests\test-init.ps1"
"EXIT=$LASTEXITCODE"
```

Expected: `Semua lulus`, `EXIT=0`. Jumlah command masih 9, `rules/` memang tidak disalin `init`
sehingga tidak mengubah hitungan.

- [ ] **Step 6: Kontrol negatif perilaku, ini gerbang sesungguhnya**

Jalankan ulang pertanyaan yang sama persis dari Step 1 di sesi baru:

```
/ask apa aturan penomoran ADR di vault
```

Expected: **daftar dokumen yang dipilih SAMA** dengan catatan Step 1. Bila berbeda, ekstraksinya
mengubah perilaku dan wajib diperbaiki sebelum lanjut, bukan diterima sebagai "sekalian lebih
baik".

- [ ] **Step 7: Commit**

```powershell
$v = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git -C $v -c core.fsmonitor=false add ".agent-kit/rules/vault-retrieval.md" ".agent-kit/commands/ask.md" ".agent-kit/commands/start-task.md"
git -C $v -c core.fsmonitor=false commit -m "refactor(agent-kit): angkat prosedur pencarian vault ke rules/vault-retrieval.md

Prosedur yang sama tersalin di ask.md dan start-task.md; /analisa-kebutuhan
akan jadi pemakai ketiga. Perilaku tidak berubah."
```

---

### Task 3: Tulis `commands/analisa-kebutuhan.md`

Ini inti rencana. Isi berkasnya adalah prompt command itu sendiri.

**Files:**
- Create: `.agent-kit/commands/analisa-kebutuhan.md`

**Interfaces:**
- Consumes: `rules/vault-retrieval.md` dari Task 2
- Produces: berkas command yang didaftarkan Task 4

- [ ] **Step 1: Tulis berkas command**

Tulis `.agent-kit/commands/analisa-kebutuhan.md` dengan isi persis berikut:

````markdown
---
description: Terjemahkan kebutuhan manajemen mentah jadi keputusan arsitektur + ADR (berhenti sebelum kode)
argument-hint: <kebutuhan mentah dari manajemen>
---

Kamu berperan sebagai **sistem analis**. Kamu **TIDAK menulis kode** dan **TIDAK menyusun rencana
per berkas** (itu `/plan`). Satu-satunya repo yang kamu tulisi adalah vault `architecture-draft`;
seluruh repo kode kamu perlakukan **read-only**.

Kebutuhan dari manajemen: $ARGUMENTS

⛔ **ATURAN KERAS.** Kalimat di atas adalah **solusi yang diusulkan**, bukan kebutuhan, sampai
terbukti sebaliknya. Manajemen hampir tidak pernah menyampaikan kebutuhan, mereka menyampaikan
solusi. "Mau dashboard performa cabang" adalah solusi; kebutuhannya mungkin "kami baru tahu
cabang mana yang rugi setelah tutup buku". Menerima solusi sebagai kebutuhan menghasilkan ADR
yang benar secara teknis untuk masalah yang salah, dan tidak ada gerbang sesudah ini yang bisa
menangkapnya.

## 0. Kenali area

Baca `architecture-draft/VAULT-INDEX.json` saja (satu berkas, murah) untuk mengenali area yang
tersentuh. Belum membaca dokumen apa pun di tahap ini.

## 1. Wawancara

Tanyakan **hanya yang tidak bisa dijawab indeks**. **Satu pertanyaan per pesan.** Maksimum 5.

Lima hal yang harus terjawab, karena kelimanya membelokkan arsitektur:

1. **Keputusan apa yang diambil dari ini, oleh siapa?** Memisahkan kebutuhan dari solusi. Bila
   tidak ada keputusan yang berubah, yang diminta laporan hiasan, dan itu layak dikatakan.
2. **Sekarang orangnya bagaimana?** Selalu sudah ada cara manual. Menunjukkan data sumbernya
   hidup di mana, dan sering mengungkap modul yang sudah menyelesaikan separuh masalahnya.
3. **Sesering apa dilihat, seberapa segar datanya harus?** Pembelok paling keras: query langsung
   vs mart terjadwal vs cron. Berbeda ongkos dan berbeda mode gagal.
4. **Siapa yang boleh melihat?** Menentukan keterlibatan RBAC, jebakan HRGA, prinsip tiga lapis
   kalender, dan data pribadi orang lain.
5. **Apa akibatnya bila angkanya salah?** Angka untuk menggaji orang menuntut gerbang yang sama
   sekali berbeda dari angka untuk rapat mingguan.

**Berhenti** begitu kelimanya terjawab dari sumber mana pun. Jangan menuntaskan daftar demi
lengkap. Jawaban "tidak tahu" dicatat sebagai **asumsi eksplisit**, jangan mandek menunggu.

## 2. Grounding

Dispatch `Explore` **paralel**, satu per sumber yang relevan. Tidak selalu empat; minimum dua
(vault + backend).

| Subagent | Sumber | Yang dikembalikan |
|---|---|---|
| vault | `architecture-draft` | dok terkait, status marker tiap dok, ADR yang mengikat |
| backend | `bip-erp` | service/handler tersentuh, koleksi + field, aturan pemakaian kolom |
| frontend | `erp-frontend` | halaman/menu tersentuh, komponen shared yang sudah ada |
| mobile | `mybharata-app` | konsumen yang ikut patah, aturan bisnis |

Untuk bagian vault, ikuti `architecture-draft/.agent-kit/rules/vault-retrieval.md`.

Tiap subagent wajib mengembalikan `file:line` untuk **setiap** klaim, dan satu bagian bernama
**"yang sudah ada"**: kode atau master data yang sudah menyelesaikan sebagian masalah ini.

### Lima gerbang, semuanya sudah pernah menggigit

1. ⛔ **Aturan bisnis.** Bila kebutuhan menyentuh **uang, sanksi, jatah, atau ambang disiplin**,
   buka `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` **LEBIH DULU**, sebelum
   opsi apa pun disusun. Perhatikan nama foldernya `mybharata-app`, bukan `mybharata`. Dokumen
   itu menang atas perilaku sistem. Ia tinggal di repo mobile sehingga tidak akan ditemukan
   kecuali dicari. Potongan mangkir pernah dirancang 1x padahal Pasal 20 mengatur 1,5x sehari
   dan 2x bila dua hari atau lebih, dan itu lolos `/plan` maupun `/implement`.
2. ⛔ **Klaim negatif.** "X belum ada" **tidak boleh** berdiri di atas `Grep` saja. Satu byte NUL
   membuat berkas hilang total dari ripgrep tanpa satu pun tanda. Konfirmasi dengan `git grep`,
   yang tidak melewati berkas biner. Ini gerbang terpenting di sini, karena seluruh keputusan
   "bangun baru" berdiri di atas klaim negatif.
3. ⛔ **Data nyata.** Sebelum merancang apa pun yang membaca data yang sudah ada, **ukur isinya
   di prod**. Sudah berkali-kali terjadi: nol slip payroll terbit padahal kodenya live, nol
   dokumen `web_browser` padahal push notification live. Angka nol yang mencurigakan adalah
   pertanyaan, bukan kabar baik. **Baca prod boleh, tulis TIDAK.**
4. ⛔ **Kolom.** Untuk tiap kolom angka yang masuk rancangan, jawab eksplisit: komponen sejajar,
   atau himpunan bagian dari kolom lain? `iklan_sia_sia` adalah porsi `ads_cost` yang **sudah**
   terpotong dari laba; `orders_dikirim` himpunan bagian dari `orders`. Menjumlahkannya
   menghasilkan angka salah yang masuk akal, tanpa error dan tanpa test merah. Aturannya hampir
   selalu cuma hidup sebagai komentar Go, jadi baca kodenya. Kolom yang butuh kalimat "jangan
   dijumlahkan ke X" wajib ikut naik ke dok vault.
5. ⛔ **Status.** ADR yang berdiri di atas dok 🟡 Konsep berarti berdiri di atas rencana, bukan
   kenyataan, dan itu wajib dinyatakan terang di `## Context`.

**Subagent tidak dipercaya buta.** Ringkasan yang keliru tidak terlihat sebagai galat. Setiap
klaim yang jadi **dasar keputusan** diverifikasi ulang sendiri, minimal dengan membuka
`file:line` yang disebutnya.

## 3. Pertanyaan lanjutan

Maksimum 2, dan hanya yang **baru bisa muncul setelah baca kode**, misalnya "ternyata sudah ada X
yang menyelesaikan 70% ini, dipakai ulang atau dipisah?". Total pertanyaan sepanjang command ini
tidak pernah lebih dari 7. Sisanya jadi asumsi tertulis.

## 4. Sajikan, lalu BERHENTI

Sajikan di chat:

- **Kebutuhan sebenarnya**, dinyatakan terpisah dari solusi yang diminta
- **Yang sudah ada**, dan sejauh mana ia sudah menjawab
- **2 sampai 3 opsi arsitektur** dengan trade-off, dan rekomendasimu beserta alasannya
- **Asumsi eksplisit** dari pertanyaan yang tidak terjawab
- **Konsekuensi deploy** bila ada: env baru butuh `--force-recreate`, kategori inbox baru butuh
  dua container naik bersama, perubahan kontrak berarti BE sebelum FE

⛔ **BERHENTI. Tunggu persetujuan user. JANGAN menulis berkas apa pun sebelum disetujui.**

### Kamu BOLEH menyimpulkan "tidak perlu dibangun"

Ini yang membedakan analis dari juru tulis ADR. Bila grounding menemukan kebutuhannya sudah
dijawab modul yang ada, atau keputusannya sudah dikunci ADR sebelumnya, atau datanya tidak pernah
terisi sehingga fiturnya mustahil, maka **jangan tulis ADR**. Sajikan temuan itu sebagai hasil,
dan selesai. Analis yang selalu menghasilkan ADR adalah analis yang selalu bilang ya.

## 5. Tulis artefak (hanya setelah disetujui)

Tiga berkas, semuanya di `architecture-draft`.

**a. ADR di `Decisions/`.** Hitung nomor tertinggi saat ini dan tambah satu; **jangan pakai nomor
hafalan**, orang lain bisa menambah lebih dulu dan seluruh wikilink memakai judul lengkap. Bentuk
mengikuti `Decisions/ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap.md`:

```
## Untuk Manajemen
## Deskripsi            (miring, satu paragraf)
- Status / Path di repo / Tanggal
## Context
## Decision
## Consequences
```

- **Status** awal selalu 🟡 **Diusulkan**, kodenya memang belum ada.
- **Path di repo** diisi berkas yang **akan** disentuh, beri penanda `(baru)`.
- **`## Untuk Manajemen`** ditulis **tanpa satu pun nama fungsi atau path berkas**, berisi empat
  hal: apa yang berubah di layar, siapa yang terdampak, **apa yang tidak dijanjikan**, dan
  perkiraan besaran kerja. Ia sengaja **bagian di dalam ADR**, bukan berkas terpisah, supaya
  tidak bisa menyimpang saat keputusannya direvisi. Salin isinya ke chat siap kirim.

**b. Dok domain di folder area.** Modul yang **sudah ada** memperbarui dok yang ada; modul atau
service **baru** membuat dok baru dari `Templates/Template - Konsep Domain.md`. ADR dan dok
domain **saling menaut** dengan wikilink: ADR menyimpan kenapa dan keputusannya, dok domain
menyimpan cara kerjanya.

**c. Daftar task di `Workspace/ANALISA - <judul>.md`.** Pecahan kerja berurutan dengan
dependensinya, tiap item cukup jelas untuk langsung dilempar ke `/start-task`. **Bukan** rencana
per berkas. Sengaja tidak di dalam ADR: ADR adalah keputusan, bukan papan kerja.

## 6. Regenerasi indeks. WAJIB.

Jalankan `/index-vault`. Retrieval vault berjalan lewat `VAULT-INDEX.json`, bukan RAG, jadi dok
yang belum terindeks **tidak terlihat sama sekali**, baik oleh `/ask` dan `/start-task` maupun
oleh manajemen lewat MCP. Ini sengaja berbeda dari `/ask` yang hanya menyarankan `/sync-docs`:
di sini dok barunya tidak berguna sampai terindeks.

## 7. Commit dan push

Vault push **langsung ke `main`, tanpa PR**. Stage **per nama berkas**, jangan `git add -A`.
Pakai `git -C <vault> -c core.fsmonitor=false`.

## 8. Serahkan

Tutup dengan kalimat konkret: task pertama apa, dan perintahnya, misalnya
`jalankan /start-task <deskripsi task pertama>`.
````

- [ ] **Step 2: Jalankan test kit**

```powershell
& "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\tests\test-init.ps1"
"EXIT=$LASTEXITCODE"
```

Expected: `PASS semua command kit tersalin (10 berkas)`, lalu `Semua lulus`, `EXIT=0`. Angka naik
sendiri dari 9 ke 10 karena Task 1 menurunkannya dari sumber.

- [ ] **Step 3: Commit**

```powershell
$v = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git -C $v -c core.fsmonitor=false add ".agent-kit/commands/analisa-kebutuhan.md"
git -C $v -c core.fsmonitor=false commit -m "feat(agent-kit): command /analisa-kebutuhan, peran sistem analis

Menerjemahkan kebutuhan manajemen mentah jadi ADR + dok domain + daftar task.
Berhenti sebelum kode; repo kode diperlakukan read-only."
```

---

### Task 4: Daftarkan command baru supaya sampai ke tim

Berkas command yang tidak disebut di mana pun akan tersalin tapi tidak diketahui orang. Task ini
membuat ia terlihat.

**Files:**
- Modify: `.agent-kit/tests/test-init.ps1` (tambah assertion berkas spesifik)
- Modify: `.agent-kit/hooks/session-start.ps1`
- Modify: `.agent-kit/hooks/session-start.sh`
- Modify: `.agent-kit/templates/workspace-CLAUDE.md`
- Modify: `.agent-kit/README.md`
- Modify: `.agent-kit/VERSION`

**Interfaces:**
- Consumes: `commands/analisa-kebutuhan.md` dari Task 3
- Produces: kit versi `1.14.0` yang siap di-`init` tim

- [ ] **Step 1: Tambah assertion berkas spesifik ke test**

Assertion jumlah dari Task 1 membuktikan "semua tersalin", tapi tidak membuktikan command **ini**
ada. Tambahkan setelah baris `Check (Test-Path (Join-Path $claude 'commands/start-task.md')) 'commands tersalin'`:

```powershell
  Check (Test-Path (Join-Path $claude 'commands/analisa-kebutuhan.md')) 'command /analisa-kebutuhan tersalin'
```

- [ ] **Step 2: Jalankan test, pastikan assertion baru PASS**

```powershell
& "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\tests\test-init.ps1"
"EXIT=$LASTEXITCODE"
```

Expected: `PASS command /analisa-kebutuhan tersalin`, `Semua lulus`, `EXIT=0`.

- [ ] **Step 3: Kontrol negatif, buktikan assertion itu bisa merah**

Assertion yang tak pernah dilihat merah tidak membuktikan apa pun.

```powershell
$c = "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\commands\analisa-kebutuhan.md"
Rename-Item $c "analisa-kebutuhan.md.bak"
& "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\tests\test-init.ps1"
"EXIT=$LASTEXITCODE"
```

Expected: `FAIL command /analisa-kebutuhan tersalin`, `EXIT=1`. Pastikan yang merah **assertion
itu**, bukan assertion jumlah saja. Lalu kembalikan:

```powershell
Rename-Item "$c.bak" "analisa-kebutuhan.md"
```

- [ ] **Step 4: Sebut command di kedua hook**

Jangan mengubah baris flow wajib itu sendiri; command ini opsional dan bukan bagian flow wajib.

Di `.agent-kit/hooks/session-start.ps1`, ganti:

```powershell
$lines = @('Flow wajib: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap')
```

menjadi:

```powershell
$lines = @(
  'Flow wajib: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap',
  'Opsional sebelum flow: /analisa-kebutuhan <kebutuhan manajemen> (mentah -> ADR + dok + daftar task)'
)
```

Di `.agent-kit/hooks/session-start.sh`, ganti:

```bash
ctx="Flow wajib: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap"
```

menjadi:

```bash
ctx="Flow wajib: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap"
ctx="$ctx | Opsional sebelum flow: /analisa-kebutuhan <kebutuhan manajemen> (mentah -> ADR + dok + daftar task)"
```

⚠️ Berkas `.sh` menempelkan `$ctx` mentah ke string JSON dan mengandalkan komentar di kakinya:
"ctx tidak mengandung tanda kutip ganda -> aman ditempel ke JSON string". Baris tambahan di atas
sengaja **tanpa tanda kutip ganda**. Jangan menambahkan tanda kutip ganda ke `$ctx`, itu akan
menghasilkan JSON rusak dan hook-nya gagal senyap.

- [ ] **Step 5: Sebut command di template dan README**

Di `.agent-kit/templates/workspace-CLAUDE.md`, di bawah bagian "Flow wajib (per task)",
tambahkan:

```markdown
## Sebelum flow (opsional)
`/analisa-kebutuhan <kebutuhan mentah dari manajemen>` — menerjemahkan kebutuhan manajemen jadi
ADR + dok domain + daftar task di vault. Berhenti sebelum kode. Dipakai saat kebutuhannya datang
mentah dari manajemen; task teknis biasa tetap langsung `/start-task`.
```

Di `.agent-kit/README.md` ada **dua** tempat yang harus disentuh.

Pertama, baris 30 yang mendaftar isi `commands/`. Ganti:

```markdown
- `commands/` — 6 slash command flow + `/ask` (recall read-only, sebut sumber) + `/skills` (cek/install skill plugin rekomendasi tim).
```

menjadi:

```markdown
- `commands/` — 6 slash command flow + `/ask` (recall read-only, sebut sumber) + `/skills` (cek/install skill plugin rekomendasi tim) + `/index-vault` (bangun VAULT-INDEX.json) + `/analisa-kebutuhan` (kebutuhan manajemen mentah → ADR + dok domain + daftar task; berhenti sebelum kode).
```

⚠️ Baris itu juga sudah lupa menyebut `/index-vault`, yang ditambahkan di versi sebelumnya.
Perbaiki sekalian karena sedang menyunting baris yang sama.

Kedua, tambahkan entri changelog paling atas di daftar versi:

```markdown
- **1.14.0** — command **`/analisa-kebutuhan`**, peran sistem analis yang berdiri **sebelum** `/start-task` dan sifatnya **opsional**. Menerima kebutuhan manajemen mentah, memperlakukannya sebagai **solusi yang diusulkan bukan kebutuhan**, menggali lewat maksimum 7 pertanyaan, grounding lewat `Explore` paralel ke vault + tiga repo dengan lima gerbang (aturan bisnis di `mybharata-app`, klaim negatif wajib `git grep`, ukur data prod, kolom sejajar vs himpunan bagian, status dok), lalu menulis ADR + dok domain + `Workspace/ANALISA - *.md`. Ia **boleh menyimpulkan "tidak perlu dibangun"**. Prosedur pencarian vault diangkat ke `rules/vault-retrieval.md` karena command ini pemakai ketiga; `/ask` dan `/start-task` kini merujuk ke sana, perilaku tidak berubah. Ikut memperbaiki `tests/test-init.ps1` yang **sudah merah sejak `index-vault.md` dan `skills.md` ditambahkan** (mematok 7 command padahal ada 9); jumlahnya kini diturunkan dari kit, bukan angka mati. **Butuh re-init.**
```

- [ ] **Step 6: Bump VERSION**

Isi `.agent-kit/VERSION` dengan satu baris:

```
1.14.0
```

- [ ] **Step 7: Jalankan test, pastikan hijau**

```powershell
& "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\tests\test-init.ps1"
"EXIT=$LASTEXITCODE"
```

Expected: `Semua lulus`, `EXIT=0`. Assertion `.kit-version sama dgn VERSION` ikut membuktikan bump
versinya konsisten.

- [ ] **Step 8: Commit**

```powershell
$v = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git -C $v -c core.fsmonitor=false add ".agent-kit/tests/test-init.ps1" ".agent-kit/hooks/session-start.ps1" ".agent-kit/hooks/session-start.sh" ".agent-kit/templates/workspace-CLAUDE.md" ".agent-kit/README.md" ".agent-kit/VERSION"
git -C $v -c core.fsmonitor=false commit -m "feat(agent-kit): daftarkan /analisa-kebutuhan, kit 1.14.0"
```

---

### Task 5: Catat di ingatan tim

`rules/team-memory.md` di-import langsung oleh `CLAUDE.md` tiap sesi, jadi ini yang membuat
seluruh tim tahu command ini ada tanpa re-run `init`.

**Files:**
- Modify: `.agent-kit/rules/team-memory.md` (bagian "Skill & tooling AI (Claude Code)")

**Interfaces:**
- Consumes: kit 1.14.0 dari Task 4
- Produces: tidak ada, ini artefak akhir

- [ ] **Step 1: Tambah satu butir ke bagian "Skill & tooling AI"**

Sisipkan setelah butir tentang `/plan` menulis artefak:

```markdown
- **`/analisa-kebutuhan` (kit ≥ 1.14.0) berdiri SEBELUM `/start-task`, dan sifatnya opsional.**
  Seluruh flow wajib berangkat dari task teknis yang sudah jelas, jadi penerjemahan kebutuhan
  manajemen jadi keputusan arsitektur selama ini terjadi di kepala orang, tidak tercatat, dan
  tidak tergerbang. Itu persis cara potongan mangkir dirancang 1x padahal Pasal 20 mengatur
  1,5x: lolos brainstorming, `/plan`, dan `/implement`, tertangkap di `/review` cuma karena
  kebetulan. Command ini memperlakukan kalimat pembuka user sebagai **solusi yang diusulkan**,
  bukan kebutuhan, lalu menulis ADR + dok domain + `Workspace/ANALISA - *.md`. Ia **boleh
  menyimpulkan "tidak perlu dibangun"**, dan itu bagian dari gunanya. Task teknis biasa tetap
  langsung `/start-task`; memaksa semua task lewat sini cuma menambah gesekan.
  Desain: `.agent-kit/docs/2026-08-28-analisa-kebutuhan-command-design.md`.
- **Prosedur pencarian vault kini SATU tempat**: `.agent-kit/rules/vault-retrieval.md`, dirujuk
  `/ask`, `/start-task`, dan `/analisa-kebutuhan`. Jangan menyalinnya lagi ke command baru.
```

- [ ] **Step 2: Commit dan push seluruh rangkaian**

```powershell
$v = "c:\Data utama\Aplikasi\Office\erp\architecture-draft"
git -C $v -c core.fsmonitor=false add ".agent-kit/rules/team-memory.md"
git -C $v -c core.fsmonitor=false commit -m "docs(agent-kit): catat /analisa-kebutuhan dan vault-retrieval di ingatan tim"
git -C $v -c core.fsmonitor=false fetch origin
git -C $v -c core.fsmonitor=false merge origin/main --no-edit
git -C $v -c core.fsmonitor=false push origin main
```

⚠️ Bila `VAULT-INDEX.json` konflik saat merge, **jangan menggabungkannya baris per baris**. Ambil
salah satu sisi, selesaikan konflik dokumennya dulu, lalu regenerasi indeks **sekali di akhir**.

---

### Task 6: Verifikasi hidup

Test hijau bukan bukti fitur bisa dipakai. Task ini yang membuktikannya, dan tanpa task ini
rencana ini belum selesai.

**Files:** tidak ada yang disunting.

**Interfaces:**
- Consumes: seluruh task sebelumnya
- Produces: bukti pakai

- [ ] **Step 1: Jalankan `init` sungguhan di workspace ini**

```powershell
& "c:\Data utama\Aplikasi\Office\erp\architecture-draft\.agent-kit\init.ps1"
Test-Path "c:\Data utama\Aplikasi\Office\erp\.claude\commands\analisa-kebutuhan.md"
Get-Content "c:\Data utama\Aplikasi\Office\erp\.claude\.kit-version"
```

Expected: `True`, dan `1.14.0`.

- [ ] **Step 2: Restart sesi Claude Code, pastikan command muncul**

Command baru tidak muncul di sesi yang sedang berjalan. Restart, lalu ketik `/` dan pastikan
`analisa-kebutuhan` ada di daftar.

- [ ] **Step 3: Satu perjalanan utuh sebagai orang**

Jalankan dengan satu kebutuhan manajemen **nyata**, bukan contoh karangan:

```
/analisa-kebutuhan <kebutuhan nyata dari manajemen>
```

Gerbang yang harus lulus, semuanya:

| Gerbang | Bukti |
|---|---|
| Wawancara berhenti di bawah anggaran | tidak lebih dari 5 pertanyaan di tahap 1 |
| Grounding benar-benar jalan | ada `file:line` nyata di ringkasannya, bukan nama berkas saja |
| Gerbang persetujuan dihormati | **tidak ada berkas terbentuk** sebelum kamu bilang setuju |
| Tiga artefak terbentuk | ADR di `Decisions/`, dok domain, `Workspace/ANALISA - *.md` |
| ADR punya `## Untuk Manajemen` | dan isinya **tanpa** nama fungsi atau path berkas |
| Nomor ADR benar | `0058` atau lebih, tidak menabrak yang ada |
| Indeks terbarui | dok barunya **ketemu** lewat `/ask`, ini yang membuktikan `/index-vault` jalan |

- [ ] **Step 4: Buktikan jalur "tidak perlu dibangun" hidup**

Tanpa uji ini jalur itu kemungkinan besar mati tanpa ketahuan, karena jalur bahagia tidak pernah
melewatinya.

```
/analisa-kebutuhan bikin halaman kalender sendiri untuk jadwal booking ruangan
```

Expected: command **menolak menulis ADR** dan menunjuk aturan kalender terpusat, yaitu fitur
bertanggal wajib mendaftarkan feed ke `calendar-service` dan dilarang membuat halaman kalender
sendiri. Bila ia tetap menulis ADR, gerbangnya belum bekerja dan Task 3 harus diperbaiki.

- [ ] **Step 5: Laporkan hasil apa adanya**

Bila ada gerbang yang gagal, sebutkan yang gagal beserta keluarannya. Jangan melaporkan selesai
dengan gerbang tertunda; itu persis pola yang membuat form-builder "live" tiga hari dalam keadaan
mustahil dipakai.
