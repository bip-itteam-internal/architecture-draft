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

Saring `architecture-draft/VAULT-INDEX.json` untuk mengenali area yang tersentuh. **Jangan
dibaca utuh** — indeksnya ratusan dokumen dan pembacaan penuh akan terpotong diam-diam;
cocokkan `area` + `kata_kunci` saja. Belum membaca dokumen apa pun di tahap ini.

## 1a. Wawancara niat

Dua pertanyaan **terbuka**, satu per pesan, **sebelum** grounding. Jawabannya tidak ada di kode,
dan keduanya mempertajam apa yang dicari subagent di §2:

1. **Keputusan apa yang diambil dari ini, oleh siapa?** Memisahkan kebutuhan dari solusi. Bila
   tidak ada keputusan yang berubah, yang diminta laporan hiasan, dan itu layak dikatakan.
2. **Sekarang orangnya bagaimana?** Selalu sudah ada cara manual. Menunjukkan data sumbernya
   hidup di mana, dan sering mengungkap modul yang sudah menyelesaikan separuh masalahnya.

Lewati yang sudah dijawab kalimat pembuka user atau indeks. Jawaban "tidak tahu" dicatat sebagai
**asumsi eksplisit**, jangan mandek menunggu. Tiga pertanyaan bentuk menyusul di §1b, sesudah grounding.

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
   kecuali dicari. Potongan mangkir pernah dirancang **setengah** dari yang diatur Pasal 20,
   dan itu lolos `/plan` maupun `/implement`. Angkanya baca di dokumen itu, jangan dari sini.
2. ⛔ **Klaim negatif.** "X belum ada" **tidak boleh** berdiri di atas `Grep` saja. Satu byte NUL
   membuat berkas hilang total dari ripgrep tanpa satu pun tanda. Konfirmasi dengan `git grep`,
   yang tidak melewati berkas biner. Ini gerbang terpenting di sini, karena seluruh keputusan
   "bangun baru" berdiri di atas klaim negatif.
3. ⛔ **Data nyata.** Sebelum merancang apa pun yang membaca data yang sudah ada, **ukur isinya
   di prod**. Sudah berkali-kali terjadi: nol slip payroll terbit padahal kodenya live, nol
   dokumen `web_browser` padahal push notification live. Angka nol yang mencurigakan adalah
   pertanyaan, bukan kabar baik. **Baca prod boleh, tulis TIDAK** (batasnya per perintah: skill
   `deploy-bip-erp` §0). Alamat dan cara aksesnya ada di vault `IT - Server, VMs and Databases`
   § **MongoDB ERP Production**; coba itu dulu, jangan langsung menyerah. Bila tetap tak terjangkau
   dari mesin ini, catat sebagai **asumsi eksplisit**, tandai sebagai risiko di ADR, dan **tulis
   kuerinya** supaya manusia bisa menjalankannya (jadi "Perlu ukur prod:" di §5c); jangan menebak isinya.
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
4. Pertanyaan yang **sudah terjawab grounding atau jawaban §1a tidak ditanyakan**; jawabannya
   disajikan sebagai temuan di §4. Bila grounding tak menemukan apa pun yang relevan, pertanyaannya
   **tetap diajukan** dengan opsi "bangun baru" berlabel + "Belum tahu", bukan dilewati.
5. `AskUserQuestion` menampung **paling banyak 4 opsi** per pertanyaan, dan "Belum tahu" memakan satu:
   pilih tiga alternatif terkuat, sisanya sebut di teks §4.

Contoh Q3: "pakai mart `<nama>` yang sudah ada, segar H-1 (`<berkas>:<baris>`)" ·
"query langsung ke `<koleksi>` (bangun baru; jalur daftar berpaginasi, risiko compute-on-read)" · "Belum tahu".

## 3. Pertanyaan lanjutan

Maksimum 2, dan hanya yang **baru bisa muncul setelah baca kode**, misalnya "ternyata sudah ada X
yang menyelesaikan 70% ini, dipakai ulang atau dipisah?". Ajukan lewat `AskUserQuestion` dengan
aturan opsi §1b. Total pertanyaan kebutuhan sepanjang command ini tidak pernah lebih dari 7.
Sisanya jadi asumsi tertulis.

## 4. Sajikan, lalu BERHENTI

Sajikan di chat:

- **Kebutuhan sebenarnya**, dinyatakan terpisah dari solusi yang diminta
- **Yang sudah ada**, dan sejauh mana ia sudah menjawab
- **2 sampai 3 opsi arsitektur** dengan trade-off, dan rekomendasimu beserta alasannya
- **Asumsi eksplisit** dari pertanyaan yang tidak terjawab
- **Konsekuensi deploy** bila ada: env baru butuh `--force-recreate`, kategori inbox baru butuh
  dua container naik bersama, perubahan kontrak berarti BE sebelum FE
- **Dok terdampak** bila keputusannya **mengubah** fakta yang sudah tertulis di dok lain (ambang,
  rumus, daftar-izin, rute): jalankan `/dampak` langkah 1-4 atas draf keputusan ini **sebelum
  menyajikan**, dan sajikan laporannya di sini. Satu gerbang persetujuan untuk keduanya. Keputusan
  yang murni menambah hal baru boleh lewat.
- **Blueprint**: daftar issue yang akan dibuat (judul, repo, ukuran Kecil/Sedang/Besar, urutan),
  lihat §5c. Tanyakan **Pemutus** (login GitHub) lewat `AskUserQuestion`: kandidatnya dari jawaban
  Q1 ("oleh siapa") dan pemilik dok/ADR yang ditemukan grounding, plus "Belum tahu"; aturan opsi
  bersumber §1b tidak berlaku di sini. Pertanyaan ini tidak dihitung dalam batas 7. Satu persetujuan
  mencakup ADR, dok, dan pembuatan issue.

⛔ **BERHENTI. Tunggu persetujuan user. JANGAN menulis berkas apa pun sebelum disetujui.**

### Kamu BOLEH menyimpulkan "tidak perlu dibangun"

Ini yang membedakan analis dari juru tulis ADR. Bila grounding menemukan kebutuhannya sudah
dijawab modul yang ada, atau keputusannya sudah dikunci ADR sebelumnya, atau datanya tidak pernah
terisi sehingga fiturnya mustahil, maka **jangan tulis ADR**. Sajikan temuan itu sebagai hasil,
dan selesai. Analis yang selalu menghasilkan ADR adalah analis yang selalu bilang ya.

**Bila kesimpulannya ini, langkah 5 sampai 8 di bawah TIDAK dijalankan.**

## 5. Tulis artefak (hanya setelah disetujui)

Tiga berkas di `architecture-draft`, lalu issue di repo kode.

Suntingan dok terdampak hasil `/dampak` yang disetujui di §4 diterapkan bersama artefak ini, mengikuti
`/dampak` langkah 6 sebagai **pemanggil** (sunting + cek wikilink saja); index, commit, dan push ikut
§6-§7 di bawah, sekali untuk semuanya.

**a. ADR di `Decisions/`.** Hitung nomor tertinggi saat ini dan tambah satu; **jangan pakai nomor
hafalan**, orang lain bisa menambah lebih dulu dan seluruh wikilink memakai judul lengkap. Bentuk
mengikuti `Decisions/ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap.md`:

```
## Untuk Manajemen        (bagian BARU, belum ada di ADR 0057)
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

**c. Blueprint di `Workspace/ANALISA - <judul>.md`.** Kumpulan **draf issue** yang lolos checklist
Siap Agent (team-memory § Definition of Ready, ADR 0151 "Issue Siap Dikerjakan Agent Bila
Keputusannya Bisa Ditunjuk, Ditandai Manusia"). Sengaja tidak di dalam ADR: ADR adalah keputusan,
blueprint papan kerja.

Kepala: wikilink ADR + dok domain, **ukuran** + alasannya, Pemutus, dan baris status
**"Menunggu ADR <judul> Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk
`/brief`."** Blokernya berisi bagian Keputusan dan Yang harus benar, jadi tanpa baris ini triase
`/start-task` akan menerimanya sebagai sumber dan `/kerjakan` jalan atas ADR yang belum disetujui.

Ukuran ditentukan dari repo yang **harus berubah**, bukan repo yang sekadar memuat fitur terkait:
untuk tiap repo konsumen (FE, mobile), periksa dulu apakah ia sudah merender bentuk baru secara
generik sebelum menghitungnya. Alasan ukuran menyebut bukti itu (`file:line`).

| Ukuran | Kapan | Bentuk |
|---|---|---|
| **Kecil** | 1 repo | 1 issue tanpa induk. Butuh > 1 PR → issue **sejajar** "bagian i/N, sesudah #<n>", juga tanpa induk: team-memory "satu repo cukup satu issue", sub-issue tak dipakai di dalam satu repo |
| **Sedang** | > 1 repo, tiap repo 1 PR | induk di repo tempat kontrak lahir (biasanya `bip-erp`, tanpa PR sendiri) + 1 sub-issue `[BE]`/`[FE]`/`[Mobile]` per repo |
| **Besar** | > 1 repo, ada repo yang butuh > 1 PR | seperti Sedang + sub-issue **saudara** "bagian i/N" di bawah induk yang sama; tak pernah sub di bawah sub |

Tiap issue satu blok berbagian persis template `bip-erp/.github/ISSUE_TEMPLATE/tugas.md`:
`**Pemutus:**` / `**PIC:**`, `## Masalah`, `## Keputusan`, `## Yang harus benar`,
`## Di luar cakupan`, `## Data / bukti pendukung`, `## Prasyarat`; ditambah repo tujuan
(`bip-erp`, `erp-frontend`, `my-bharata`; folder lokal mobile `mybharata-app`) dan urutan.

- **Keputusan** menunjuk ADR **dengan judul** (nomor ADR bukan kunci unik) dan menulis terang:
  *layak `Siap Agent` sesudah ADR berstatus Diterima* (ADR baru masih 🟡 Diusulkan). Boleh
  ringkasan **bentuk** paling banyak tiga baris (ambang, satuan, penerima, siapa boleh apa) supaya
  issue terbaca sendiri; alasan dan alternatif tetap hanya di ADR.
- **Yang harus benar** diturunkan dari `## Decision` jadi kriteria yang bisa diperiksa (perilaku,
  angka, layar). "Pertimbangkan", "perlu disepakati", "dsb" dilarang.
- **Data** diisi hasil ukur prod gerbang 3 §2. Tak tersedia → tulis **"Perlu ukur prod:"** diikuti
  angka yang dibutuhkan dan kuerinya. Itu menahan issue dari `Siap Agent` (Definition of Ready #4:
  runner dilarang membaca prod), dan §8 menyebutnya sebagai langkah manusia.
- **Prasyarat**: urutan deploy BE sebelum FE/Mobile ditulis di sub-issue FE/Mobile.
- ⛔ **Issue bertopik keamanan** (celah, akses, kebocoran data): vault ini repo **PUBLIK**, jadi blok
  di ANALISA hanya memuat judul, repo, dan kalimat "rincian di issue privat". Masalah, bukti, dan cara
  reproduksi hanya ditulis di badan issue (repo kode privat). Rincian celah yang belum ditambal tak
  pernah ditulis ke vault (team-memory § Backlog).

**d. Buat issue.** Dijalankan **di dalam §7, sesudah merge `origin/main`**, bukan di sini: judul ADR
memuat nomornya, dan nomor itu baru pasti tak bertabrakan sesudah merge. Dari akar `erp/`, via PowerShell:

1. Induk / issue tunggal: cari dulu
   `gh issue list --repo bip-itteam-internal/<repo> --state all --search "<judul> in:title" --json number,title,url`
   dan anggap "sudah ada" hanya bila `title` **sama persis**; belum ada → tulis badan ke berkas
   scratchpad, `gh issue create --repo bip-itteam-internal/<repo> --title "<judul>" --body-file <berkas>`,
   lalu `gh project item-add 15 --owner bip-itteam-internal --url <url>`.
2. Sub-issue: `& '.claude/hooks/buat-sub-issue.ps1' -Induk <repo>#<n> -Repo <bip-erp|erp-frontend|my-bharata> -Judul '<judul>' -Badan <berkas-badan.md>`.
   `-Badan` adalah **path berkas** (skrip membacanya dengan `ReadAllText`), bukan teks. Skrip
   idempoten per judul penuh dan memasukkan issue ke Project #15.
3. **TANPA label `Siap Agent`**, tanpa assignee: label dipasang manusia (ADR 0151), assignee saat In Progress.
4. Pemutus "Belum tahu" di §4 → tulis `**Pemutus:** BELUM DITETAPKAN` di badan (DoR #6 menuntut login),
   dan §8 menyebutnya sebagai langkah manusia.
5. Tulis nomor + URL tiap issue balik ke blok-nya di ANALISA **sebelum** regenerasi indeks §6, supaya
   vault di-commit dan di-push sekali.
6. **Gagal sebagian**: laporkan yang terbuat (URL) dan yang gagal (galat); jangan ulang buta.
   Menjalankan ulang aman karena butir 1-2 idempoten; indeks pencarian GitHub bisa tertinggal
   beberapa detik, jadi tunggu sebentar sebelum mengulang butir 1.
7. `gh` tanpa scope `project` → issue tetap dibuat; catat item-add yang gagal dan perintah
   `gh auth refresh -h github.com -s project` di laporan.

Kesimpulan **"tidak perlu dibangun"** melewati seluruh §5-§8 (lihat §4): tak ada blueprint, tak ada issue.

## 6. Regenerasi indeks. WAJIB.

Retrieval vault berjalan lewat `VAULT-INDEX.json`, bukan RAG, jadi dok yang belum terindeks
**tidak terlihat sama sekali**, baik oleh `/ask` dan `/start-task` maupun oleh manajemen lewat
MCP. Ini sengaja berbeda dari `/ask` yang hanya menyarankan `/sync-docs`: di sini dok barunya
tidak berguna sampai terindeks.

⚠️ **Jalankan `/index-vault` SEKALI, pada urutannya di langkah 7** (sesudah merge, sebelum
push), bukan di sini. Merge bisa membawa dok orang lain, jadi indeks yang dibuat sebelum merge
sudah basi lagi begitu merge selesai.

## 7. Commit, merge, push

Vault push **langsung ke `main`, tanpa PR**. Stage **per nama berkas**, jangan `git add -A`.
Pakai `git -C <vault> -c core.fsmonitor=false`. Urutan: commit di `main` → merge
`origin/main` → periksa nomor ADR baru tak dipakai dok lain sesudah merge (bila dipakai: nomori
ulang, perbarui wikilink-nya) → **§5 butir d (buat issue)** → regenerasi indeks (langkah 6) →
commit → push. Bila push ditolak `gerbang-adr.py` karena nomor ganda sesudah issue terbuat, nomori
ulang ADR lalu sunting badan tiap issue yang mengutip judul lamanya
(`gh issue edit <n> --repo bip-itteam-internal/<repo> --body-file <berkas>`). Bila `VAULT-INDEX.json` konflik saat
merge, **jangan digabung baris per baris**: ambil salah satu sisi, selesaikan konflik
dokumennya dulu, lalu regenerasi indeks **sekali di akhir**.

## 8. Serahkan

Tutup dengan daftar URL issue yang dibuat (induk dulu), lalu langkah manusia berikutnya, konkret:
setujui ADR dengan menulis `🟢 Diterima, <tanggal>, oleh <login>` di baris statusnya (lalu hapus
baris "Menunggu ADR … Diterima" di kepala ANALISA); untuk issue yang memuat **"Perlu ukur prod:"**,
jalankan kuerinya (baca saja) dan tempel hasilnya; isi Pemutus yang masih **BELUM DITETAPKAN**; lalu pasang
label `Siap Agent` pada issue yang lolos checklist Definition of Ready. Sebelum langkah-langkah itu,
runner backlog tidak akan mengambil issue-nya.
