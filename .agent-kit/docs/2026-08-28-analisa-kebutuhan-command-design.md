# Desain: Command `/analisa-kebutuhan` (peran sistem analis)

- **Status**: 🟡 Diusulkan, desain disetujui 2026-08-28, kode belum ada
- **Tanggal**: 2026-08-28
- **Versi kit target**: 1.14.0 (dari 1.13.0)
- **Rencana implementasi**: `.agent-kit/docs/2026-08-28-analisa-kebutuhan-command-plan.md` (belum ditulis)

## Konteks

Seluruh flow wajib kit ini berangkat dari **task teknis yang sudah jelas**. `/start-task`
menerima `<deskripsi task>`, `/plan` menyusun rencana per berkas, `/implement` menulis kode.
Tidak ada satu pun langkah yang menerima **kebutuhan manajemen mentah** lalu menerjemahkannya
jadi proses bisnis, dampak ke modul mana, opsi arsitektur, dan keputusan.

Akibatnya penerjemahan itu terjadi di kepala orang, tidak tercatat, dan tidak tergerbang.
Kelas kegagalannya sudah terbukti di sini: fitur potongan kehadiran dirancang dengan mangkir
dipotong 1x padahal Pasal 20 Peraturan Perusahaan mengatur 1,5x sehari dan 2x bila dua hari
atau lebih. Angka yang salah itu **lolos brainstorming, `/plan`, dan `/implement`**, dan baru
tertangkap di `/review`, itu pun karena kebetulan menelusuri konsumen MyBharata. Tidak ada
gerbang yang dirancang untuk menangkapnya, karena semua gerbang yang ada bertanya apakah
**kodenya** benar, bukan apakah **kebutuhannya** dipahami.

Command ini mengisi langkah yang hilang itu.

## Keputusan bentuk: command, bukan subagent

Permintaan awal berbunyi "agent". Di Claude Code istilah itu berarti subagent, dan subagent
adalah bentuk yang **salah** di sini: ia berjalan otonom di konteks terisolasi dan tidak punya
jalur bertanya balik ke user di tengah kerja. Peran analis justru berdiri di atas kemampuan
menggali kebutuhan lewat tanya jawab.

Bentuk yang benar adalah **slash command** seperti `/start-task` dan `/plan`, dengan subagent
dipakai **di dalamnya** untuk pembacaan lebar (lihat §3).

Konsekuensi menguntungkan: `init` sudah menyalin `commands/` ke `.claude/`
([init.ps1:40](../init.ps1)), sedangkan `agents/` tidak. Memilih command berarti **nol
perubahan pada `init.ps1` dan `init.sh`**.

## Cakupan

**Masuk cakupan.** Menerima kebutuhan manajemen mentah, menggali lewat wawancara, grounding ke
vault dan kode, menyajikan opsi arsitektur, dan menulis artefak keputusan ke vault.

**Di luar cakupan.** Menulis kode, menyusun rencana per berkas (itu `/plan`), dan menyentuh
repo kode mana pun. Command ini **read-only terhadap seluruh repo kode**; satu-satunya repo
yang ditulisinya adalah vault `architecture-draft`.

## 1. Tahap wawancara

### Aturan keras

Kalimat pembuka user diperlakukan sebagai **solusi yang diusulkan, bukan kebutuhan**, sampai
terbukti sebaliknya. Manajemen hampir tidak pernah menyampaikan kebutuhan, mereka menyampaikan
solusi. "Manajemen mau dashboard performa cabang" adalah solusi; kebutuhannya mungkin "kami
baru tahu cabang mana yang rugi setelah tutup buku". Analis yang menerima solusi sebagai
kebutuhan menghasilkan ADR yang benar secara teknis untuk masalah yang salah, dan tidak ada
gerbang di flow ini yang bisa menangkapnya kemudian.

### Lima pertanyaan yang mengubah arsitektur

Bukan checklist kebutuhan generik. Hanya yang jawabannya membelokkan desain:

1. **Keputusan apa yang diambil dari ini, oleh siapa?** Memisahkan kebutuhan dari solusi. Bila
   tidak ada keputusan yang berubah, yang diminta adalah laporan hiasan, dan itu layak
   dikatakan.
2. **Sekarang orangnya bagaimana?** Selalu sudah ada cara manual. Ini menunjukkan data sumbernya
   hidup di mana, dan sering mengungkap modul yang sudah menyelesaikan separuh masalahnya.
3. **Sesering apa dilihat, seberapa segar datanya harus?** Pembelok arsitektur paling keras:
   query langsung, mart terjadwal, atau cron. Ketiganya berbeda ongkos dan berbeda mode gagal.
4. **Siapa yang boleh melihat?** Menentukan keterlibatan RBAC, dan di ERP ini menentukan apakah
   kena jebakan HRGA, prinsip tiga lapis kalender, atau data pribadi orang lain.
5. **Apa akibatnya bila angkanya salah?** Angka untuk menggaji orang menuntut gerbang yang sama
   sekali berbeda dari angka untuk rapat mingguan.

### Urutan

Sebagian jawaban ada di vault dan kode, dan menanyakannya membuang waktu user.

- **Langkah 0**: baca `VAULT-INDEX.json` saja (satu berkas, murah) untuk mengenali area yang
  tersentuh.
- **Langkah 1**: tanyakan hanya yang **tidak bisa** dijawab indeks. Satu pertanyaan per pesan.
- **Langkah 2**: fan-out grounding (§3).
- **Langkah 3**: satu putaran pertanyaan lanjutan yang **baru bisa muncul setelah baca kode**,
  nol sampai dua. Bentuknya seperti "ternyata sudah ada X yang menyelesaikan 70% ini, dipakai
  ulang atau dipisah?".

### Gerbang berhenti

Berhenti begitu lima hal di atas terjawab, dari sumber mana pun. Jangan menuntaskan daftar demi
lengkap. Jawaban "tidak tahu" dicatat sebagai **asumsi eksplisit** di artefak dan analisis
lanjut, bukan mandek menunggu.

Anggaran pertanyaan seluruhnya: **maksimum 5 di langkah 1, ditambah maksimum 2 di langkah 3**,
jadi tidak pernah lebih dari 7. Bila setelah anggaran itu masih ada yang gelap, yang gelap
dicatat sebagai asumsi, bukan ditanyakan lagi.

## 2. Tahap grounding

### Fan-out

Setelah wawancara ringan, dispatch `Explore` paralel, satu per sumber relevan. Tidak selalu
empat; yang dijalankan ditentukan area yang tersentuh, minimum dua (vault + backend).

| Subagent | Sumber | Yang dikembalikan |
|---|---|---|
| vault | `architecture-draft` | dok terkait, **status marker** tiap dok, ADR yang mengikat keputusan ini |
| backend | `bip-erp` | service/handler tersentuh, koleksi + field, aturan pemakaian kolom |
| frontend | `erp-frontend` | halaman/menu tersentuh, komponen shared yang sudah ada |
| mobile | `mybharata-app` | konsumen yang ikut patah, aturan bisnis di `BUSINESS_LOGIC_IMPLEMENTATION.md` |

Tiap subagent wajib mengembalikan `file:line` untuk **setiap** klaim, dan satu bagian bernama
**"yang sudah ada"**, yaitu kode atau master data yang sudah menyelesaikan sebagian masalah ini.
Bagian itu paling sering menentukan apakah kebutuhannya butuh barang baru sama sekali.

### Lima gerbang

Kelimanya sudah pernah menggigit dan tercatat di `rules/team-memory.md`.

1. **Gerbang aturan bisnis.** Bila kebutuhan menyentuh uang, sanksi, jatah, atau ambang
   disiplin, maka `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` dibuka
   **lebih dulu**, sebelum opsi apa pun disusun. Dokumen itu menang atas perilaku sistem, dan
   ia tinggal di repo mobile sehingga tidak akan ditemukan kecuali dicari.

2. **Gerbang klaim negatif.** Kalimat "X belum ada" tidak boleh berdiri di atas hasil `Grep`
   saja. Satu byte NUL membuat berkas hilang total dari ripgrep tanpa satu pun tanda;
   `templates-table.tsx` pernah menyembunyikan definisi `kunciPosisi`-nya sendiri. Klaim negatif
   wajib dikonfirmasi `git grep`, yang tidak melewati berkas biner. Ini gerbang terpenting untuk
   peran analis, karena seluruh keputusan "bangun baru" berdiri di atas klaim negatif.

3. **Gerbang data nyata.** Sebelum merancang apa pun yang membaca data yang sudah ada, **ukur
   isinya di prod**, jangan berasumsi terisi. Sudah terjadi berkali-kali: nol slip payroll
   terbit padahal kode Fase 1 sampai 5 live, nol dokumen `web_browser` padahal push notification
   live, `FORM_BUILDER_MODULE_URL` tidak pernah ada di employee-service sehingga metrik Kaizen
   mustahil otomatis. Angka nol yang mencurigakan adalah pertanyaan, bukan kabar baik. **Baca
   prod boleh, tulis tidak** (§ Konvensi git & rilis di team-memory).

4. **Gerbang kolom.** Untuk tiap kolom angka yang akan masuk rancangan, jawab eksplisit: ini
   komponen sejajar, atau himpunan bagian dari kolom lain? `iklan_sia_sia` adalah porsi
   `ads_cost` yang **sudah** terpotong dari laba; `orders_dikirim` himpunan bagian dari `orders`.
   Menjumlahkannya menghasilkan angka salah yang masuk akal, tanpa error dan tanpa test merah.
   Aturan ini hampir selalu hanya hidup sebagai komentar Go, jadi wajib dibaca dari kode, bukan
   dari dok. Bila ditemukan kolom yang butuh kalimat "jangan dijumlahkan ke X", kalimat itu ikut
   naik ke dok vault sebagai bagian dari artefak.

5. **Gerbang status.** Dok vault punya status (✅ Implemented, ⚠️, 🟡 Konsep, 🔴 Stub, 🔜
   Direncanakan, ⛔ Superseded). ADR yang berdiri di atas dok 🟡 berarti berdiri di atas rencana,
   bukan kenyataan, dan itu wajib dinyatakan terang di bagian `## Context`. Berlaku juga
   peringatan `/ask`: cocok topik bukan berarti menjawab.

### Subagent tidak dipercaya buta

Ringkasan keliru dari subagent tidak terlihat sebagai galat. Karena itu setiap klaim yang jadi
**dasar keputusan** di ADR diverifikasi ulang di konteks utama, minimal dengan membuka
`file:line` yang disebutnya. Klaim yang tidak jadi dasar keputusan boleh lewat.

## 3. Artefak

Tiga berkas di vault, semuanya di repo `architecture-draft`.

### 3.1 ADR di `Decisions/`

Nomor **dihitung ulang saat menulis**, tidak dipatok di command. Tertinggi saat desain ini
ditulis adalah 0057, tapi orang lain bisa menambah lebih dulu, dan tabrakan nomor menyakitkan
karena seluruh wikilink memakai judul lengkap.

Bentuk mengikuti `ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap.md` apa adanya:

```
## Untuk Manajemen        <- bagian baru, lihat 3.2
## Deskripsi              <- miring, satu paragraf
- Status / Path di repo / Tanggal
## Context
## Decision
## Consequences
```

- **Status** awal selalu 🟡 **Diusulkan**, karena kodenya memang belum ada.
- **Path di repo** diisi berkas yang **akan** disentuh dengan penanda `(baru)`, persis seperti
  ADR 0057 menuliskannya sebelum kodenya ada.

### 3.2 Ringkasan manajemen: bagian di dalam ADR, bukan berkas terpisah

Ringkasan manajemen sebagai berkas sendiri adalah satu fakta di dua tempat, dan bentuk yang
paling pasti menyimpang: ADR direvisi saat keputusannya berubah, ringkasannya tidak, lalu
manajemen memegang versi yang sudah dibatalkan.

Jadi ia menjadi bagian `## Untuk Manajemen` di **kepala** ADR, ditulis tanpa satu pun nama
fungsi atau path berkas, berisi empat hal: apa yang berubah di layar, siapa yang terdampak,
**apa yang tidak dijanjikan**, dan perkiraan besaran kerja. Command menyalinnya ke chat siap
kirim. Satu sumber, dua penyajian.

Menaruhnya di kepala juga tepat untuk jalur MCP: manajemen membuka ADR lewat Claude Desktop dan
hal pertama yang terbaca adalah bagiannya sendiri.

### 3.3 Dok domain di folder area

- Kebutuhan yang menambah cara kerja ke modul yang **sudah ada** memperbarui dok yang ada.
- Kebutuhan yang melahirkan modul atau service **baru** membuat dok baru dari
  `Templates/Template - Konsep Domain.md`.

ADR dan dok domain **saling menaut** dengan wikilink: ADR menyimpan kenapa dan keputusannya,
dok domain menyimpan cara kerjanya.

### 3.4 Daftar task di `Workspace/ANALISA - <judul>.md`

Masuk vault supaya orang lain bisa mengambil tasknya. Folder `Workspace/` sudah menampung
`Inbox` dan `Meetings`, jadi papan kerja memang tempatnya di situ, bukan di folder area domain.
Prefix `ANALISA - ` mengikuti konvensi vault yang ada (`ADR - `, `LOG - `, `RUN - `, `REF - `).

Isinya pecahan kerja berurutan dengan dependensinya, tiap item cukup jelas untuk langsung
dilempar ke `/start-task`. **Bukan** rencana per berkas; itu tetap tugas `/plan`.

Sengaja **tidak** ditaruh di dalam ADR: ADR adalah keputusan, bukan papan kerja, dan
mencampurnya berarti ADR tersunting tiap satu item selesai.

### 3.5 Setelah menulis

1. **Regenerasi `VAULT-INDEX.json` lewat `/index-vault`. Ini wajib, bukan saran.** Retrieval
   vault berjalan lewat indeks, bukan RAG. Dok yang belum masuk indeks **tidak terlihat sama
   sekali**, baik oleh `/ask` dan `/start-task` maupun oleh manajemen lewat MCP. Ini menyimpang
   dari pola `/ask` yang menyarankan `/sync-docs` tanpa memicunya, dan penyimpangannya disengaja
   karena di sini dok barunya tidak berguna sampai terindeks.
2. **Commit dan push langsung ke `main` vault, tanpa PR.** Stage **per nama berkas**, jangan
   `git add -A`.

## 4. Alur utuh dan gerbang

```
/analisa-kebutuhan <kalimat mentah dari manajemen>

  0  Baca VAULT-INDEX.json, kenali area yang tersentuh
  1  Wawancara: maks 5 pertanyaan, satu per pesan, lewati yang terjawab indeks
  2  Fan-out Explore paralel, lalu 5 gerbang grounding
  3  Pertanyaan lanjutan yang baru muncul setelah baca kode (0 sampai 2)
  4  Sajikan: kebutuhan sebenarnya (bukan solusi yang diminta)
     + 2 sampai 3 opsi arsitektur + rekomendasi + asumsi eksplisit
 ⛔  BERHENTI. Tunggu persetujuan user. Tidak ada berkas ditulis sebelum ini.
  5  Tulis 3 berkas vault + salin `## Untuk Manajemen` ke chat
  6  Jalankan /index-vault
  7  Commit per nama berkas, push langsung ke main vault
  8  Serahkan: "task pertama siap, jalankan /start-task <...>"
```

**Satu gerbang saja, di langkah 4 ke 5.** Memakai pola yang sudah ada di `/start-task` langkah 6
dan `/plan` langkah 4, bukan mekanisme baru.

### Command ini boleh menyimpulkan "tidak perlu dibangun"

Ini yang membedakan analis dari juru tulis ADR. Bila grounding menemukan kebutuhannya sudah
dijawab modul yang ada, atau keputusan yang diminta sudah dikunci ADR sebelumnya, atau datanya
tidak pernah terisi sehingga fiturnya mustahil, maka **tidak ada ADR yang ditulis**. Yang keluar
adalah temuan itu sendiri. Analis yang selalu menghasilkan ADR adalah analis yang selalu
bilang ya.

### Posisi di flow: opsional

Flow wajib tetap `/start-task` → `/plan` → `/implement` → `/review` → `/sync-docs` → `/wrap`.
Command ini berdiri **sebelum** `/start-task` dan hanya dipakai saat kebutuhannya datang mentah
dari manajemen. Task teknis biasa tetap langsung `/start-task`; memaksa semua task lewat sini
hanya menambah gesekan.

## 5. Perbaikan bersasaran: ekstraksi prosedur pencarian vault

Prosedur "baca `VAULT-INDEX.json`, cocokkan ke `ringkasan` + `kata_kunci`, ambil 3 sampai 5
dokumen, perhatikan status marker, fallback ke `CLAUDE.md` §7 bila indeks rusak" saat ini
**disalin utuh** di dua tempat: [ask.md](../commands/ask.md) langkah 1 sampai 2 dan
[start-task.md](../commands/start-task.md) langkah 2 sampai 3.

`/analisa-kebutuhan` akan menjadi pemakai **ketiga**. Team-memory menetapkan sendiri ambangnya:
"Tunggu pemakai **ketiga** sebelum mengangkat abstraksi". Jadi sekarang waktunya, bukan
sebelumnya.

Prosedurnya diangkat ke `rules/vault-retrieval.md`, dan ketiga command merujuk ke sana alih-alih
menyalinnya. Berkas di `rules/` dibaca **langsung dari vault** dan tidak disalin `init`, jadi
perubahannya berlaku cukup dengan `git pull architecture-draft`.

⚠️ Ekstraksi ini menyunting dua command yang sudah dipakai sehari-hari. Perilakunya harus
**identik**, bukan "disempurnakan sekalian". Penyempurnaan prosedur adalah task terpisah.

## 6. Berkas yang tersentuh

| Berkas | Perubahan |
|---|---|
| `.agent-kit/commands/analisa-kebutuhan.md` | baru |
| `.agent-kit/rules/vault-retrieval.md` | baru, hasil ekstraksi §5 |
| `.agent-kit/commands/ask.md` | ganti salinan prosedur jadi rujukan |
| `.agent-kit/commands/start-task.md` | ganti salinan prosedur jadi rujukan |
| `.agent-kit/rules/team-memory.md` | catat command baru + posisinya di flow |
| `.agent-kit/templates/workspace-CLAUDE.md` | sebut command baru sebagai langkah opsional |
| `.agent-kit/hooks/session-start.ps1` · `.sh` | sebut command baru |
| `.agent-kit/README.md` | daftar command |
| `.agent-kit/tests/test-init.ps1` | uji `analisa-kebutuhan.md` ikut tersalin ke `.claude/commands/` |
| `.agent-kit/VERSION` | `1.13.0` → `1.14.0` |

**Nol perubahan** pada `init.ps1` dan `init.sh`: `commands/` sudah disalin.

## 7. Ketergantungan dan risiko

⛔ **Vault MCP belum berdiri di mana pun.** Jalur baca manajemen ke vault belum ada:
PR [#1489](https://github.com/bip-itteam-internal/bip-erp/pull/1489) yang menutup tiga celah
keamanan (open redirector, nol pembatasan laju, rotasi refresh token baca-lalu-tulis) masih
OPEN, `docker build` belum pernah berhasil dicoba, dan `mcp.bharatainternasional.com` belum ada
di DNS. Sampai itu beres, artefak tetap ditulis ke vault tapi **user yang meneruskan ringkasan
manajemen secara manual**. Command ini tidak boleh dirancang seolah jalur kirimnya sudah ada,
dan tidak bergantung padanya untuk berfungsi.

⚠️ **Audiens vault berubah, dan itu perlu keputusan terpisah.** Kredensial plaintext di dok IT
selama ini disengaja dengan alasan "referensi akses internal tim IT". Begitu pembacanya
manajemen lewat MCP, asumsi audiens itu berubah. Di luar cakupan desain ini, tapi layak
diputuskan sebelum MCP hidup.

⚠️ **Ringkasan subagent bisa keliru tanpa terlihat.** Dimitigasi oleh aturan verifikasi ulang
di §2, tapi mitigasinya bergantung pada disiplin, bukan mekanisme. Ini risiko yang diterima
sadar.

## 8. Yang sengaja tidak dikerjakan

- **Bukan subagent.** Sudah dijelaskan di §Keputusan bentuk.
- **Bukan dua command terpisah** (`/analisa` lalu `/tulis-adr`). Gerbang "BERHENTI, tunggu
  konfirmasi" sudah jadi pola yang dipakai `/start-task` dan `/plan`; membuat mekanisme kedua
  untuk gerbang yang sama adalah persis yang dilarang team-memory.
- **Tidak menyentuh `init.ps1`/`init.sh`** untuk menambah jenis artefak `agents/`. Tidak
  dibutuhkan, dan menambah jenis artefak demi satu pemakai adalah generalisasi dini.
- **Tidak menulis kode, tidak menyusun rencana per berkas.** Itu `/plan` dan `/implement`.
- **Tidak menjadikan command ini wajib** di flow.

## 9. Cara verifikasi

Test hijau bukan bukti fitur bisa dipakai. Yang membuktikan:

1. **`init` menyalin command baru.** Jalankan `init.ps1`, pastikan
   `.claude/commands/analisa-kebutuhan.md` ada. Dikunci `tests/test-init.ps1`.
2. **Kontrol negatif ekstraksi.** Setelah `ask.md` dan `start-task.md` diubah jadi merujuk
   `rules/vault-retrieval.md`, jalankan `/ask` dengan pertanyaan yang jawabannya diketahui dan
   pastikan dokumen yang terpilih **sama** dengan sebelum ekstraksi. Ekstraksi yang mengubah
   perilaku adalah regresi, bukan perbaikan.
3. **Satu perjalanan utuh sebagai orang.** Jalankan `/analisa-kebutuhan` dengan satu kebutuhan
   manajemen nyata sampai selesai: wawancara berhenti di bawah 5 pertanyaan, tiga berkas
   terbentuk, `/index-vault` dijalankan, dan dok barunya **benar-benar ketemu** lewat `/ask`.
   Langkah terakhir itu yang membuktikan indeksnya ikut terbarui.
4. **Gerbang "tidak perlu dibangun" benar-benar bisa menyala.** Uji dengan kebutuhan yang sudah
   dijawab modul yang ada, dan pastikan hasilnya **tidak ada ADR yang ditulis**. Tanpa uji ini,
   jalur itu kemungkinan besar mati tanpa ketahuan.
