> Detail ingatan tim, dibaca **ON-DEMAND** dari indeks `../team-memory.md`. Jangan di-import ke `CLAUDE.md`; update cukup `git pull architecture-draft`.

## Backlog: GitHub Project #15 "Semangatt guyss !!! 👏" (2026-09-29, menggantikan Linear)

Backlog tim pindah dari Linear ke **GitHub Project #15** org `bip-itteam-internal` (judulnya bisa
diganti; rujuk project lewat **nomor 15**, jangan lewat judul)
(https://github.com/orgs/bip-itteam-internal/projects/15, privat). Alasannya terukur: paket Free
Linear berhenti di **250 issue** (terisi 245), dan hanya 3 dari 10 anggota org yang ada di Linear
sehingga PIC terpaksa ditulis sebagai teks. Keputusannya [[ADR - 0143 Backlog Pindah dari Linear ke GitHub Project]].
**Linear `BHA` dibekukan jadi arsip baca**: jangan membuat atau memperbarui issue di sana. Tiap issue
lama punya padanan di GitHub: judulnya berakhiran `[BHA-<n>]` dan field **Linear ID** berisi `BHA-<n>`,
jadi rujukan `BHA-<n>` di vault, ADR, dan brief tetap bisa dilacak (`gh search issues "BHA-<n>" --owner bip-itteam-internal`).

| Status | Artinya | Yang memindahkan |
|---|---|---|
| Backlog / Todo | belum ada branch | manusia |
| In Progress | branch sudah ada | pembuat branch (manusia atau agent) |
| In Review | PR terbuka | pembuat PR (manusia atau agent) |
| **Menunggu Adopsi** | kode merged; sisa deploy prod (manusia) dan fitur benar-benar dipakai | otomatis: PR merged menutup issue, workflow *Item closed* memindahkannya |
| Done | terbukti dipakai (**Bukti Adopsi** diisi orang), **atau** sudah 7 hari di Menunggu Adopsi (Bukti Adopsi berawalan `otomatis:`) | manusia dengan bukti; atau otomasi harian sesudah 7 hari |
| Canceled | tidak dikerjakan / duplikat | manusia |

Aturan (berlaku untuk developer DAN agent):

- ⛔ **Yang menentukan selesai adalah field Status, BUKAN issue open/closed.** Issue tertutup berarti
  kodenya merged, belum berarti dipakai. View dan laporan menyaring Status, jangan `is:open`.
- ⛔ **PR wajib memuat `Closes bip-itteam-internal/<repo>#<n>` di badannya.** Hanya tautan resmi
  (kata kunci penutup, atau branch dari `gh issue develop`) yang menggerakkan otomasi; `Refs #<n>`
  tidak menyambungkan apa pun, dan issue-nya diam di In Review selamanya. Bentuk lengkap
  `<org>/<repo>#<n>` wajib saat PR dan issue beda repo (PR erp-frontend untuk issue bip-erp).
- ⛔ **MyBharata: `Closes` TIDAK menutup issue, karena PR di-merge ke `dev` sedangkan branch default
  repo `main`.** GitHub hanya menutup issue untuk PR yang masuk ke branch default, jadi issue
  `my-bharata` tak pernah closed, workflow *Item closed* tak pernah terpicu, dan kartunya diam di
  In Review. Kueri "issue terbuka dengan PR merged" pun **buta** terhadapnya: PR ke `dev` tidak
  tercatat sebagai penutup (`closedByPullRequestsReferences` kosong). Terjadi pada my-bharata#175
  (PR #176 merged 2026-10-04, ketahuan 2026-10-07 hanya dengan mencocokkan teks PR). **Sesudah PR
  `my-bharata` merged ke `dev`, yang me-merge menutup issue-nya manual** (`gh issue close <n> -R
  bip-itteam-internal/my-bharata --reason completed`) lalu memastikan kartunya di Menunggu Adopsi.
  Issue yang tak ditutup juga **dilewati** otomasi 7-hari-ke-Done.
- ⛔ **Item yang dimasukkan ke board WAJIB langsung diberi Status** (`gh project item-edit`), jangan
  dibiarkan "No Status". Workflow bawaan project (*Item added*, *Item closed*) bisa MATI tanpa ada
  yang berbunyi: diukur 2026-10-07, lima dari enam workflow Project #15 mati sejak 2026-09-29, dan
  43 kartu merged diam di In Review plus 7 kartu tanpa Status sebelum ada yang bertanya. Otomasi
  board itu bantuan, bukan jaminan.
- ⛔ **Merge BUKAN Done.** Pelajaran audit Linear 2026-09-29 tetap berlaku: status meleset ke dua arah
  (BHA-249 Done tanpa satu baris kode, BHA-250 "Belum Mulai" padahal 127 sesi live sudah memakainya,
  BHA-22 kodenya lengkap di prod dengan 0 snapshot), dan 82 dari 105 issue Done tak punya PR tertaut.
  "Kode selesai" dan "dipakai" pemiliknya berbeda; satu status untuk keduanya menyembunyikan siapa
  yang ditunggu. **Agent tidak pernah memindahkan issue ke Done secara manual.**
- **Menunggu Adopsi 7 hari → Done otomatis** (keputusan 2026-10-08,
  [[ADR - 0156 Backlog Menunggu Adopsi Tujuh Hari Otomatis Done]]). Diukur hari itu: 230 dari 578
  kartu menumpuk di Menunggu Adopsi dan **0** berisi Bukti Adopsi. Otomasi harian (`bip-erp`
  `scripts/board/adopsi_otomatis.py`, GitHub Actions) memindahkan kartu yang field Status-nya sudah
  7 hari di Menunggu Adopsi dan issue-nya **tertutup**, lalu mengisi Bukti Adopsi
  `otomatis: 7 hari di Menunggu Adopsi (<tanggal>)`. Dilewati: issue terbuka, *not planned*, bukan
  issue. ⚠️ Akibatnya **Done tidak lagi selalu berarti terbukti dipakai**, dan kartu yang merged
  tetapi belum di-deploy prod ikut jadi Done: laporan adopsi wajib menyaring Bukti Adopsi yang
  **tidak** berawalan `otomatis:`. ⚠️ Ukur dulu apakah otomasinya benar-benar jalan (run Actions
  terakhir, secret `PROJECT_TOKEN`) sebelum mengandalkannya; token kedaluwarsa membuat kartu
  menumpuk lagi tanpa galat di board.
- ⛔ **Jangan membuat issue di repo vault `architecture-draft`: repo itu PUBLIK.** Issue bertanda
  keamanan hanya di repo kode (privat), dan rincian celah yang belum ditambal tidak ditulis ke vault.
- **Satu issue tinggal di satu repo.** Taruh di repo kode yang paling banyak disentuh.
- ⭐ **Perubahan yang menyentuh lebih dari satu repo (BE `bip-erp`, FE `erp-frontend`, Mobile
  `my-bharata`) WAJIB dipecah jadi issue induk + SATU sub-issue per repo.** Induk = fiturnya (tinggal
  di repo tempat kontraknya lahir, biasanya `bip-erp`), tanpa PR sendiri; tiap sub-issue berjudul
  `[BE]` / `[FE]` / `[Mobile]`, tinggal di repo-nya, punya brief dan PR-nya sendiri, dan PR itulah
  yang menutupnya (`Closes <org>/<repo>#<sub>`). Hasilnya progress bar "2/3" di kartu induk, jadi
  semua orang melihat bagian mana yang tertinggal tanpa membuka issue. Buat lewat
  `& '.claude/hooks/buat-sub-issue.ps1' -Induk <repo>#<n> -Repo <bip-erp|erp-frontend|my-bharata> -Judul '<judul>'`
  (idempoten, memasukkan ke Project #15, menyalin Area + Prioritas induk); jangan merakit `gh api`
  sendiri, karena PS 5.1 merusak array dan kutip tanpa galat. Aturan turunannya:
  - **Satu tingkat saja.** Sub-issue tidak dipecah lagi; butir rinci masuk checklist rencana, bukan sub-issue.
  - **Satu repo cukup satu issue**, tanpa sub-issue. Memecah pekerjaan satu repo jadi sub-issue per berkas
    membuat board tak terbaca.
  - **Status induk mengikuti anak-anaknya**: In Progress begitu satu anak mulai; **Menunggu Adopsi**
    hanya bila SEMUA anak sudah merged (induk ditutup manual saat itu); Done mengikuti aturan Menunggu Adopsi di atas.
  - **Urutan deploy BE sebelum FE/Mobile** ditulis di badan sub-issue FE/Mobile ("deploy sesudah
    `bip-erp#<sub BE>`"); merged duluan boleh, deploy duluan tidak.
- ⛔ **Masuk Todo = WAJIB ber-assignee** (keputusan user 2026-10-07, menggantikan aturan 2026-09-29
  yang membiarkan Todo tanpa assignee). Todo berarti "sudah dijatahkan, siap dikerjakan", jadi kartu
  Todo tanpa nama tak punya pemilik dan tak ada yang merasa ditunggu. **Backlog** tetap boleh tanpa
  assignee (belum dijatahkan); PIC rencana di Backlog cukup ditulis di badan (`**PIC:** <login>`).
  Yang memindahkan kartu ke Todo memasang assignee-nya saat itu juga; tak tahu siapa = kartunya tetap
  Backlog. Saat mulai (In Progress), assignee diganti/ditambah akun yang benar-benar mengerjakan;
  agent yang mulai mengerjakan issue meng-assign akun yang menjalankannya. Pengawas ditulis di badan
  issue sebagai `**Pengawas:** <login>`.
- **Nama branch `<domain>/<n>-<slug>`**, `<n>` = nomor issue GitHub. Bukan syarat otomasi (yang
  menyambungkan adalah `Closes` di PR), tetapi membuat branch terbaca dan dipakai pre-push untuk
  mengingatkan. Branch lama `bha-<n>-` tetap diterima.
- **Membatalkan**: tutup issue sebagai *not planned* lalu set Status **Canceled** sendiri; workflow
  *Item closed* tidak membedakan alasan penutupan dan akan menaruhnya di Menunggu Adopsi.
- ⚠️ **Deskripsi hasil audit bisa basi dan audit bisa salah baca.** "Rute tak ditemukan" di banyak
  issue lama lahir dari lupa bahwa gateway membuang prefix `/api/<module>`; MyBharata dibaca dari
  `main` padahal rilis store dari `dev`. Sebelum memindahkan status, ukur ke `origin/main`
  (MyBharata: `origin/dev`) dan data prod, lalu tulis komentar `Verifikasi <tanggal>` di issue.

### ⛔ Definition of Ready: issue baru boleh dikerjakan agent bila berlabel `Siap Agent`

Diukur 2026-10-02: dari 52 issue yang disentuh runner backlog, **4 jadi PR dan 46 berhenti di
Butuh Info**, karena issue berisi masalah tanpa keputusan. Keputusannya
[[ADR - 0151 Issue Siap Dikerjakan Agent Bila Keputusannya Bisa Ditunjuk, Ditandai Manusia]].
**Checklist ini satu-satunya sumber**; template issue di `bip-erp`/`erp-frontend` hanya memuat
judul bagiannya. Label `Siap Agent` dipasang **manusia** (pembuat issue atau Pemutus) bila SEMUA terpenuhi:

1. **Keputusan bisa ditunjuk**: tautan ADR berstatus **Diterima** (bukan Diusulkan), `ANALISA - *.md` yang ADR-nya sudah Diterima,
   atau bagian `## Keputusan` di badan issue yang menjawab "bentuknya apa" (penerima, ambang, kanal,
   satuan, siapa boleh apa). Kalimat "pertimbangkan", "perlu disepakati", atau "dsb" = belum siap.
2. **Satu repo, satu PR.** Lebih dari itu dipecah dulu. PR agent wajib `Closes` issue-nya, jadi issue
   yang memuat T1-T7 sekaligus tak bisa dikerjakan sebagian. Cara memecah, supaya tidak melanggar
   "Satu tingkat saja" di atas:
   - issue **tingkat atas** satu repo: pecah jadi beberapa issue **sejajar** (bukan sub-issue), masing-masing
     satu PR, saling merujuk di badan ("bagian 1/3, sesudah #<n>");
   - issue yang sudah **sub-issue** (`[BE]`/`[FE]`): **ganti** dengan beberapa sub-issue **saudara** di bawah
     induk yang sama (`buat-sub-issue.ps1 -Induk <induk>`), lalu tutup yang lama *not planned* + Status
     Canceled dengan komentar "dipecah jadi #a, #b". Jangan membuat sub-issue di bawah sub-issue.
   Pecah **sesudah** keputusannya ada (ADR Diterima), bukan sebelumnya: pecahan dari issue yang belum
   diputuskan hanya memperbanyak kartu Butuh Info.
3. **`## Yang harus benar`** berisi kriteria yang bisa diperiksa (perilaku, angka, layar), bukan
   "dashboard + analisa otomatis".
4. **Data produksi yang dibutuhkan sudah ditempel** di issue. Runner dilarang membaca prod.
5. **Prasyarat sudah merged** (issue lain, atau ADR yang disebut).
6. **`**Pemutus:** <login>`** di badan: orang yang berwenang memutuskan bentuk solusinya (boleh beda
   dari PIC). Pertanyaan agent ditujukan ke dia.

Aturan turunan:
- ⛔ **Persetujuan ADR ditulis di baris status ADR-nya**: `🟢 Diterima, <tanggal>, oleh <login/jabatan>`.
  Disetujui lisan tapi baris status tetap "Diusulkan" = bagi agent belum disetujui.
- **Menjawab Butuh Info**: jawab di issue, lalu **lepas label `Butuh Info`** (dan pasang `Siap Agent`
  bila checklist terpenuhi). Komentar yang hanya menambah data tanpa melepas label tidak mengantre ulang.
- ⚠️ **Status penerapan**: skrip runner (hanya di PC IT, lihat [[RUN - Agent Backlog Otonom]]) baru
  memakai gerbang ini setelah diperbarui di sana. Ukur runbook-nya sebelum mengklaim runner sudah mematuhinya.

Cara agent mengaksesnya:

- Lewat `gh`, butuh scope **`project`** di mesin itu (`gh auth refresh -h github.com -s project`,
  sekali per mesin; tanpa itu perintah project gagal dengan pesan scope, bukan diam).
- Tambah issue ke project: `gh project item-add 15 --owner bip-itteam-internal --url <url issue>`.
  Ubah field: `gh project item-edit` (butuh id item, id field, id opsi; `gh project field-list 15
  --owner bip-itteam-internal --format json`). Pada PowerShell 5.1, kirim payload GraphQL lewat
  berkas `--input`, bukan argumen: kutip ganda di argumen `-f query=` dirusak.
- ⚠️ **PowerShell: `$L` dan `$l`, `$F` dan `$f`, `$ORG` dan `$org` adalah variabel yang SAMA.**
  Skrip migrasi menggigit tiga kali dalam satu jam: `foreach ($l in $L)` menimpa daftar label
  sehingga hanya label terakhir yang terkirim, tanpa galat. Juga: `@($x.nodes.name)` atas daftar
  kosong menghasilkan `@($null)` (satu elemen null), bukan array kosong.
- `/linear-cek` dan `linear-verifikasi.ps1` **usang** sejak Linear dibekukan; penggantinya (laporan
  mingguan dari Project #15) **belum ada** (TBD).
