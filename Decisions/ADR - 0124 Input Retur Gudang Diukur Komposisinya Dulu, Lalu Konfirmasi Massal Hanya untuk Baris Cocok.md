# ADR - 0124 Input Retur Gudang Diukur Komposisinya Dulu, Lalu Konfirmasi Massal Hanya untuk Baris Cocok

> **Status**: 🟡 **Diusulkan**, 2026-09-24, kode belum ada. Berdiri di atas pengukuran langsung produksi 2026-09-24 dan pembacaan `origin/main`.

%% Status ditulis DI SINI sebagai blockquote, bukan sebagai bullet di ## Deskripsi seperti
kebanyakan ADR, dan itu bukan gaya bebas: `## Untuk Manajemen` mendorong bagian Deskripsi
melewati baris ke-15, dan di bawah baris itu status tak terbaca VAULT-INDEX.json sehingga dok
muncul tanpa status di /ask (rulebook vault §5). Pola yang sama dipakai ADR 0120. Satu tempat
saja — jangan tambahkan bullet Status di ## Deskripsi. %%

## Untuk Manajemen

**Apa yang berubah di layar.** Untuk sekarang tidak ada. Keputusan ini memasang satu pengukuran
murah lebih dulu. Bila pengukurannya lolos, yang berubah kemudian: petugas gudang dapat
membereskan beberapa paket retur sekaligus dari satu daftar, alih-alih membuka dan menutup satu
formulir untuk tiap paket.

**Siapa yang terdampak.** Sembilan orang yang mencatat retur di Gudang Barang Jadi (terukur
2026-09-24). Tidak menyentuh departemen lain. Finance tetap menerima sinyal barang rusak
seperti sekarang.

**Apa yang TIDAK dijanjikan.** Tidak ada penilaian kondisi barang secara otomatis, dan tidak ada
AI. Sistem tidak pernah menebak berapa barang yang rusak; pemeriksaan fisik tetap dikerjakan
orang. Itu keputusan lama yang sengaja tidak dibuka kembali di sini. Juga tidak dijanjikan
pengurangan ketikan, karena formulirnya memang sudah nyaris tidak perlu diketik.

**Perkiraan besaran kerja.** Satu pengukuran kecil lebih dulu, lalu perubahan layar berukuran
sedang yang **hanya dikerjakan bila angkanya membenarkan**. Pengukurannya boleh menyimpulkan
bahwa perubahan layarnya tidak layak, dan itu hasil yang sah.

## Deskripsi

*Beban ketikan manusia terbesar yang terukur di ERP ada pada pencatatan kondisi barang retur di
gudang, tetapi formulirnya ternyata sudah berbasis pengecualian sehingga yang mahal bukan isinya
melainkan siklus buka-simpan-tutup per paket. Keputusan ini menolak membangun sebelum komposisi
siklus itu diukur, lalu mengarahkan perbaikannya ke konfirmasi massal yang dibatasi hanya pada
baris yang qty-nya sudah cocok dengan klaim marketplace.*

- **Path di repo**: `erp-frontend/src/features/manufacture/components/GudangBarangJadiView.tsx` · `erp-frontend/src/i18n/locales/id.ts` + `en.ts` · `bip-erp/services/manufacture/` (hanya bila T2 menyimpulkan endpoint massal diperlukan, **baru**)
- **Tanggal**: 2026-09-24

## Context

### Kebutuhannya datang sebagai solusi, dan pengukurannya membantahnya

Kalimat pembukanya "bantu pekerjaan manusia yang bisa dikerjakan AI". Screening ke seluruh 19
database produksi pada 2026-09-24 (baca-saja) menyimpulkan sebaliknya untuk alur ini, dan juga
untuk dua kandidat lain yang ikut diperiksa. Daftar tasknya ada di `Workspace/ANALISA - Kurangi Siklus Input Retur Gudang` (sengaja disebut sebagai path, bukan wikilink: dok published tak boleh menaut ke `Workspace/`).

### Beban manusia di ERP terpusat di satu tempat

Diukur per koleksi: total dokumen, laju 30 hari terakhir, dan **berapa orang berbeda**
menulisinya. Kolom terakhir itu yang memisahkan ketikan manusia dari sinkron mesin.

| Pekerjaan | per 30 hari | orang | per orang |
|---|---|---|---|
| **Input kondisi retur gudang** | 7.685 | **9** | **854** |
| Log engagement | 1.436 | 15 | 96 |
| Absen harian | 4.677 | 190 | 25 |
| Isi form | 1.867 | 181 | 10 |
| Pengajuan cuti | 275 | 124 | 2,2 |

Jaraknya **8,9x** ke kandidat berikutnya. Volume absolut terbesar di produksi seluruhnya mesin
(webhook 503.455, webhook TikTok 371.555, performa video 318.577) dan bukan kerja manusia sama
sekali; screening yang berhenti di "koleksi mana yang paling besar" akan salah sasaran.

### Formulirnya SUDAH berbasis pengecualian, jadi obat yang paling wajar sudah terpasang

Diverifikasi di `origin/main` erp-frontend:

- Baris diprefill dari feed marketplace: `reuse` diisi qty retur marketplace, `rework` dan
  `reject` kosong (`expandReturnLines`, `GudangBarangJadiView.tsx:671-704`).
- Bundle dipecah otomatis jadi baris komponen (`:676-687`).
- Tanggal default hari ini WIB saat form dibuka dari feed (`:940`) atau dari scan (`:995`);
  Nama Market prefill dari channel (`:932`); Resi prefill dari `reverse_tracking_no` (`:937`);
  PIC auto-isi dari JWT hanya bila kosong (`:430`).
- **Kasus normal karena itu 0 sentuhan per baris.** Kasus menyimpang 4 sentuhan (kurangi reuse,
  isi rework, pilih alasan), alasan wajib bila qty terisi.

90,2% baris memang tidak butuh catatan sama sekali (`qtyReject`=0 dan `qtyRework`=0, diukur
2026-09-14), jadi mayoritas mutlak paket sudah bisa disimpan tanpa menyentuh satu kolom pun.

**Konsekuensinya keras untuk keputusan ini**: "tambahkan nilai bawaan" bukan pekerjaan yang
tersisa. Ia sudah ada. Yang tersisa adalah **siklusnya** — satu modal dibuka, disimpan, ditutup,
untuk tiap paket.

### Yang tidak ada sama sekali

Tidak ada impor CSV atau XLSX, tidak ada paste, tidak ada "terapkan ke semua baris", tidak ada
pilih-banyak-baris. Satu-satunya akselerator adalah kolom scan resi di halaman daftar yang
membuka form otomatis ber-`autoFocus` supaya pemindai langsung bisa menembak paket berikutnya
(`:2675-2699`). `MainTable` sendiri **tidak punya seleksi baris**; satu-satunya tabel di repo
yang punya adalah `IntegrationTable`, dan ia bergaya visual modul Integration.

### Pembagian Reuse/Rework/Reject TIDAK menentukan pembukuan, dan itu sering disalahpahami

[[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] Decision #8 menyatakan **ketiga
kondisi sama-sama menambah stok**; kondisinya adalah label informasi, dan barang rusak
disesuaikan finance secara manual (keputusan 21 Juli 2026). Catatan temuan
`Workspace/Inbox/2026-07-17 Temuan - Reject retur menambah stok FG` berstatus ⛔ **DITUTUP dan
arahnya DIBALIK**, dengan kalimat penutup *"Jangan 'memperbaiki' ini balik ke scrap — itu
keputusan sadar, bukan bug."*

⚠️ [[Microservices - Manufacture Service]] masih menuliskannya sebagai gap yang belum diperbaiki.
Dokumentasinya basi di titik itu, bukan kodenya. Dikoreksi bersama ADR ini.

### Yang dijaga gerbang ADR 0025 adalah hal LAIN, dan gerbang itu tidak disentuh di sini

Decision #8 yang sama melarang membukukan retur sebelum gudang mengonfirmasi barangnya benar
datang, karena itu berarti *"menebak qty yang belum dilihat siapa pun"*. Larangan itu tentang
**keberadaan fisik barang**, bukan tentang pembagian tiga kondisinya. Keputusan ini tidak
mengubah gerbang tersebut: konfirmasi tetap dilakukan orang yang memegang paketnya.

Yang tetap mengikat dan dikutip apa adanya: *"pembagian Reuse/Rework/Reject tetap penilaian
pengecek"* ([[APP - Web ERP]]).

### Preseden yang membolehkan, dan preseden yang memperingatkan

**Membolehkan.** [[ADR - 0100 Penerimaan Beda dengan Accurate Diputus di Halaman Penerimaan]]
Decision #1: "selaras = tak ada keputusan yang perlu diambil", terukur **18 dari 30 dokumen
tertutup sendiri**. [[ADR - 0069 Perlengkapan Per-Unit Opsional di inventory dengan Guard Anti-Kontaminasi]]
Decision #5 memprefill hitung fisik dan menyebutnya *"prefill cuma memudahkan"*, berdampingan
dengan opname manual.

**Memperingatkan, dan preseden ini yang menentukan bentuk keputusan di bawah.** ADR 0025
mencatat sweep pemulihan konfirmasi otomatis yang **dibangun sebelum komposisi kegagalannya
diukur**; hasilnya menolong **0 dari 5** dan ditandai *"JANGAN dinyalakan"*. Jalur retur ini juga
sudah melahirkan penanda "wired tapi inert": badge SEBAGIAN yang **tak pernah menyala sekali pun**
sejak fitur ada, sambil menandai setiap order "✅ Sudah discan" secara salah.

### Gerbang yang sudah ditutup

- **Aturan bisnis**: `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` diperiksa
  2026-09-24 dan hanya memuat absensi, cuti, lembur, payroll, dan sanksi (Pasal 13-56). **Nol**
  penyebutan retur, stok, gudang, kas kecil, maupun pengadaan. Alur ini tidak menyentuh
  Peraturan Perusahaan.
- **Kelayakan AI**: [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]]
  §3 menuntut aturan sederhana diuji lebih dulu. Di sini bahkan tidak sampai ke sana: tidak ada
  model yang diusulkan, karena tidak ada yang perlu diramalkan.

### Status dokumen yang jadi pijakan

Pijakan utamanya dua dok ✅ Implemented ([[Microservices - Manufacture Service]],
[[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]) plus pembacaan `origin/main`
erp-frontend langsung. [[Manufacture - Stock & Material Management]] berstatus ⚠️ Sebagian
Implemented dan **tidak dijadikan pijakan**: ia tidak menyinggung form retur maupun
Reuse/Rework/Reject sama sekali.

## Decision

### 1. Komposisi siklus diukur lebih dulu, dan pengukurannya boleh membatalkan sisanya

Satu angka menentukan apakah pekerjaan ini layak sama sekali: **berapa paket per hari, bukan
berapa baris.** Angka 854 per orang per bulan diturunkan dari kesamaan total
`manufacture_audit_log` (17.755) dan `manufacture_transaksi` (17.715), dan itu **inferensi, bukan
ukuran**. Bila satu paket ternyata memuat banyak baris, jumlah siklusnya jauh lebih kecil dan
seluruh keputusan ini gugur.

Yang wajib terukur sebelum satu baris kode ditulis: jumlah submit per hari per orang, berapa
persen paket yang seluruh barisnya berbadge **cocok**, dan sebaran jumlah baris per paket.

Ini mengikuti preseden sweep 0-dari-5 di ADR 0025 secara langsung, bukan sebagai kehati-hatian
umum.

### 2. Bila lolos, bentuknya konfirmasi massal yang DIBATASI baris cocok

Hanya paket yang **seluruh** barisnya berbadge "cocok" terhadap klaim marketplace yang boleh
dipilih banyak lalu disimpan sekaligus. Badge itu sudah ada dan sudah dihitung
(`GudangBarangJadiView.tsx:2351-2368`).

Yang berbadge "kurang" atau "lebih" **tetap satu per satu lewat form**. Gerbangnya sengaja
sempit: yang dikonfirmasi massal adalah paket yang tidak memuat keputusan apa pun, persis
definisi "selaras" di ADR 0100.

### 3. Tabel antrean yang bisa disunting penuh DITOLAK untuk sekarang

Opsi mengganti modal dengan tabel yang barisnya disunting langsung memang menyerang biaya yang
sama, tetapi menuntut membongkar `GudangBarangJadiView.tsx` yang **3.476 baris, tanpa satu pun
impor `@/components/table`, dan praktis tanpa i18n** (hanya 2 kunci; komentar di `:160-162`
mengakuinya sebagai layar warisan). Ongkos itu tidak sebanding sebelum §1 membuktikan siklusnya
memang mahal.

Ditolak **untuk sekarang**, bukan selamanya. Bila §1 menghasilkan angka yang jauh lebih besar
dari dugaan, opsi ini ditinjau ulang lewat ADR baru.

### 4. Sinyal kerusakan tidak boleh hilang, dan itu diperiksa dengan angka

Konfirmasi massal hanya sah bila proporsi rework dan reject **tidak turun** sesudahnya. Terukur
2026-09-14: 8,8% rework dan 1,1% reject. Angka itu dipakai finance menyesuaikan Accurate secara
manual, jadi menghilangkannya berarti memindahkan kesalahan ke pembukuan tanpa satu pun galat.

Proporsi pra dan pasca perubahan wajib dibandingkan sebagai gerbang penerimaan, bukan sebagai
pemantauan sesudahnya.

### 5. Tidak ada jalur yang menambah stok dua kali

Form sekarang **selalu membuat transaksi baru dan tidak punya jalur edit**, sehingga simpan kedua
menambah stok dua kali. Konfirmasi massal menambah permukaan baru untuk kesalahan yang sama,
lebih-lebih karena satu aksi kini menyentuh banyak paket. Idempotensi per paket wajib dijamin
sebelum tombolnya ada, bukan sesudah.

### 6. Tidak ada AI, dan itu keputusan yang dicatat supaya tidak diusulkan ulang

Pencatatan kondisi retur tidak memuat satu pun kandidat AI. Tidak ada yang perlu diramalkan,
tidak ada teks untuk dipahami, dan penilaian fisiknya sudah dinyatakan milik orang oleh ADR 0025.
Usulan AI di alur ini ditolak tanpa perlu menyentuh gerbang [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] §1.

## Consequences

**Yang didapat**

- Kandidat termahal di ERP diperiksa dengan angka, dan yang tersisa dipersempit dari "kurangi
  ketikan" (sudah beres) jadi "kurangi siklus" (belum disentuh).
- Bentuk perbaikannya sempit dan bergerbang, jadi ongkos salahnya kecil.

**Yang dibayar**

- ⚠️ **Seluruh teks baru wajib lewat `react-i18next` dengan kunci di `id.ts` DAN `en.ts`**
  ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]). Layar ini warisan tanpa i18n, jadi tiap
  teks yang tersentuh menambah pekerjaan yang tidak terlihat dari besarnya perubahan. Kedua
  berkas locale itu yang paling sering disunting paralel; merge lokal plus `pnpm tsc` dan
  `pnpm build` wajib sebelum merge.
- **Seleksi baris harus dibangun**, karena `MainTable` tidak memilikinya dan `IntegrationTable`
  bergaya modul lain. Ini menambah kerja yang tidak terlihat dari deskripsi fiturnya.
- Menumpang layar warisan 3.476 baris berarti tiap perubahan memikul risiko regresinya.

**Batas yang sengaja tidak dilewati**

Mengubah gerbang konfirmasi gudang ADR 0025, mengubah arti tiga kondisi, menilai kondisi barang
otomatis, dan membongkar layar warisan jadi struktur tabel HRIS. Tiga yang pertama adalah
keputusan yang sudah diambil; yang keempat menunggu §1.

**Konsekuensi deploy**

Tidak ada. Perubahannya frontend saja, tanpa env baru, tanpa kategori inbox baru, dan tanpa
perubahan kontrak API, jadi tidak ada urutan backend-sebelum-frontend yang perlu diikuti. Bila
§1 ternyata menuntut endpoint massal di manufacture-service, urutan itu baru berlaku dan
dicatat sebagai perubahan atas keputusan ini.

## Dokumen Terkait

- [[Microservices - Manufacture Service]] — pemilik alur dan koleksinya
- [[APP - Web ERP]] — layar Gudang Barang Jadi
- [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] — gerbang konfirmasi gudang, arti tiga kondisi, preseden sweep 0-dari-5
- [[ADR - 0100 Penerimaan Beda dengan Accurate Diputus di Halaman Penerimaan]] — preseden "selaras = tak ada keputusan"
- [[ADR - 0069 Perlengkapan Per-Unit Opsional di inventory dengan Guard Anti-Kontaminasi]] — preseden prefill pada pemeriksaan fisik
- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] — gerbang usulan AI
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]] — kewajiban dua locale
