# Desain — `/analisa-kebutuhan`: wawancara pilihan ganda + blueprint issue Siap Agent

- Tanggal: 2026-10-07
- Status: DRAFT, menunggu review
- Menyentuh: `commands/analisa-kebutuhan.md` (§1, §3, §4, §5c, §5d baru, §8), `tests/test-init.ps1`,
  `rules/team-memory.md` (satu butir), `VERSION`, `README.md` kit (changelog)
- Tidak menyentuh: `hooks/buat-sub-issue.ps1` (dipakai apa adanya), template issue di repo kode,
  ADR 0151 / Definition of Ready, judge, `/brief`, `/kerjakan`
- Asal: sub-proyek 2 dan 3 dari breakdown speckit.tech (sub-proyek 1 = `/dampak`, kit 1.37.0)

## 1. Masalah

Dua mekanisme SpecKit yang belum kita punya:

1. **Wawancara pilihan ganda adaptif.** `/analisa-kebutuhan` §1 bertanya terbuka, satu per pesan,
   **sebelum** grounding (§2). Pertanyaan bentuk (kesegaran data, siapa boleh melihat, akibat bila
   salah) karena itu dijawab manajemen tanpa tahu apa yang sudah ada di kode, dan jawabannya
   harus diterjemahkan ulang agent.
2. **Blueprint yang ukurannya mengikuti kerumitan.** Keluaran §5c hari ini daftar task bebas di
   `Workspace/ANALISA - *.md`. Diukur 2026-10-02 (ADR 0151 "Issue Siap Dikerjakan Agent Bila
   Keputusannya Bisa Ditunjuk, Ditandai Manusia"): dari 52 issue yang disentuh runner backlog,
   **46 berhenti di Butuh Info** karena issue berisi masalah tanpa keputusan. Hasil
   `/analisa-kebutuhan` justru berisi keputusan itu, tapi tidak pernah sampai ke issue dalam bentuk
   checklist Siap Agent.

## 2. Keputusan yang sudah diambil (brainstorming 2026-10-07)

| Pertanyaan | Keputusan |
|---|---|
| Pembaca blueprint | **Agent/runner**: blueprint = issue yang lolos checklist ADR 0151, bukan set dok gaya SpecKit (yang menduplikasi ADR + dok domain, melanggar SATU FAKTA SATU TEMPAT). |
| Sampai mana ke GitHub | **Buat issue setelah disetujui, TANPA label `Siap Agent`** (label tetap dipasang manusia, ADR 0151). |
| Wawancara | Grounding didahulukan untuk pertanyaan bentuk; opsi dari temuan kode. Pertanyaan niat tetap terbuka. |
| Blueprint | ANALISA berubah jadi kumpulan draf issue berformat template `tugas.md`, diukur Kecil/Sedang/Besar. |

## 3. Wawancara pilihan ganda

### Urutan baru (total pertanyaan tetap ≤ 7)

| Langkah | Isi | Bentuk |
|---|---|---|
| §0 Kenali area | tak berubah | — |
| **§1a Niat** | Q1 keputusan apa yang diambil, oleh siapa; Q2 sekarang orangnya bagaimana | terbuka, satu per pesan |
| §2 Grounding | tak berubah (subagent paralel + 5 gerbang) | — |
| **§1b Bentuk** | Q3 kesegaran; Q4 siapa boleh melihat; Q5 akibat bila salah | `AskUserQuestion`, ≤ 3 pertanyaan dalam **satu** panggilan |
| §3 Lanjutan | ≤ 2, hanya yang baru muncul setelah baca kode | `AskUserQuestion` |

Q1-Q2 tetap terbuka karena jawabannya tidak ada di kode, dan keduanya mempertajam sasaran grounding.

### Aturan opsi

1. **Tiap opsi menyebut sumbernya** di deskripsi: `file:line`, nama koleksi/mart, atau judul dok/ADR.
   Opsi tanpa sumber hanya boleh sebagai alternatif "bangun baru", dan dilabeli begitu.
2. `(Recommended)` hanya bila grounding mendukungnya, dengan alasan satu kalimat; opsi itu di urutan pertama.
3. Selalu ada opsi **"Belum tahu"** → dicatat sebagai **asumsi eksplisit** di ADR (aturan lama), tak mandek.
4. Pertanyaan yang **sudah terjawab grounding tidak ditanyakan**; jawabannya disajikan sebagai temuan di §4.

Contoh Q3: "pakai mart `<nama>` yang sudah ada, segar H-1 (`<berkas>:<baris>`)" ·
"query langsung ke `<koleksi>` (jalur daftar berpaginasi, risiko compute-on-read)" · "Belum tahu".

## 4. Blueprint: ANALISA = draf issue Siap Agent

### Bentuk `Workspace/ANALISA - <judul>.md`

1. **Kepala**: wikilink ADR + dok domain; **ukuran** + alasannya; Pemutus.
2. **Satu blok per issue**, bagian persis template `bip-erp/.github/ISSUE_TEMPLATE/tugas.md`:
   `**Pemutus:**` / `**PIC:**`, `## Masalah`, `## Keputusan`, `## Yang harus benar`,
   `## Di luar cakupan`, `## Data / bukti pendukung`, `## Prasyarat`; ditambah repo tujuan, urutan,
   dan (sesudah §5d) nomor + URL issue.

### Aturan ukuran

| Ukuran | Kapan | Bentuk |
|---|---|---|
| **Kecil** | 1 repo, 1 PR | 1 issue, tanpa induk |
| **Sedang** | > 1 repo | induk di repo tempat kontrak lahir (biasanya `bip-erp`, tanpa PR sendiri) + 1 sub-issue `[BE]`/`[FE]`/`[Mobile]` per repo |
| **Besar** | ada repo yang butuh > 1 PR | seperti Sedang, ditambah sub-issue **saudara** "bagian i/N" di bawah induk yang sama; tak pernah sub di bawah sub |

Diturunkan dari team-memory § Backlog (sub-issue satu tingkat; satu repo satu PR).

### Aturan isi

- **Keputusan** menunjuk ADR **dengan judul** (nomor ADR bukan kunci unik), tidak menyalin isinya.
  ADR baru berstatus 🟡 Diusulkan, jadi blok menulis terang: *layak `Siap Agent` sesudah ADR Diterima*.
- **Yang harus benar** diturunkan dari `## Decision` ADR jadi kriteria yang bisa diperiksa
  (perilaku, angka, layar). Kalimat "pertimbangkan"/"perlu disepakati"/"dsb" dilarang (ADR 0151).
- **Data** diisi hasil ukur prod dari gerbang 3 §2; tak tersedia → ditulis sebagai asumsi.
- **Prasyarat**: urutan deploy BE sebelum FE/Mobile ditulis di sub-issue FE/Mobile.

### Persetujuan (§4)

Daftar issue (judul, repo, ukuran) ikut disajikan bersama ADR/dok, ditambah satu pertanyaan
**Pemutus** (login GitHub, `AskUserQuestion`; tidak dihitung dalam batas 7 karena bukan pertanyaan
kebutuhan). Satu persetujuan mencakup semuanya.

### §5d Buat issue (baru, sesudah §5a-c, sebelum commit vault)

1. Induk / issue tunggal: cari dulu `gh issue list --repo bip-itteam-internal/<repo> --search "<judul> in:title"`;
   tak ada → `gh issue create --repo ... --title ... --body-file <berkas>` lalu
   `gh project item-add 15 --owner bip-itteam-internal --url <url>`.
2. Sub-issue: `& '.claude/hooks/buat-sub-issue.ps1' -Induk <repo>#<n> -Repo <repo> -Judul <judul> -Badan <badan>`
   (idempoten, memasukkan ke Project #15, menyalin Area + Prioritas).
3. **Tanpa** label `Siap Agent`, **tanpa** assignee (PIC di badan; assignee dipasang saat In Progress).
4. Nomor + URL ditulis balik ke ANALISA, sehingga vault di-commit/push **sekali** di §7.
5. **Gagal sebagian**: laporkan yang terbuat (URL) dan yang gagal (galat); jangan ulang buta.
   Mengulang §5d aman karena langkah 1-2 idempoten.
6. Bila `gh` tak punya scope `project` → pesan scope muncul; laporkan perintah
   `gh auth refresh -h github.com -s project`, lanjutkan tanpa item-add, tandai di laporan.

Kesimpulan **"tidak perlu dibangun"** → tak ada blueprint, tak ada issue (aturan lama berlaku).

### §8 Serahkan

Ganti "task pertama + `/start-task`" dengan: daftar URL issue, dan langkah berikutnya bagi manusia:
setujui ADR (`🟢 Diterima, <tanggal>, oleh <login>`) lalu pasang `Siap Agent` pada issue yang lolos checklist.

## 5. Pengujian

`tests/test-init.ps1` (berkas yang tersalin ke `.claude/commands/analisa-kebutuhan.md`):

- urutan heading `§1a` → `## 2.` → `§1b` (indeks kemunculan naik);
- memuat `AskUserQuestion`, aturan "opsi menyebut sumber", dan opsi "Belum tahu";
- memuat tabel ukuran (Kecil/Sedang/Besar) dan merujuk `tugas.md`;
- §5d memuat `buat-sub-issue.ps1`, `item-add 15`, dan larangan `Siap Agent`.

Tiap pemeriksaan dibuktikan **merah** dengan kontrol negatif (salinan dirusak), seperti `/dampak`.

**Uji kering manual** sekali sesudah implementasi: `/analisa-kebutuhan` atas kebutuhan contoh sampai
§4, berhenti sebelum persetujuan; periksa opsi Q3-Q5 menyebut sumber dan draf issue lolos checklist.
Tidak membuat issue sungguhan.

## 6. Rilis

Naik satu minor dari `VERSION` di `origin/main` **saat implementasi** (cek ulang sebelum bump dan
sebelum push: nomor diklaim saat push). Entri changelog `README.md`; butir team-memory § Skill & tooling.
**Butuh re-init.**

## 7. Di luar lingkup

- Memasang `Siap Agent` otomatis (butuh ADR baru yang menyimpang dari ADR 0151).
- Mengubah `/brief` / `/kerjakan` untuk membaca ANALISA langsung (issue adalah antarmukanya).
- Deteksi kerumitan otomatis berbasis skor; ukuran ditentukan agent dari temuan grounding, alasannya tertulis.
