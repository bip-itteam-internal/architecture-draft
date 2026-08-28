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
