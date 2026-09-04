# ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul

## Untuk Manajemen

- **Yang berubah di layar**: pada pengujian audit yang pembandingnya dokumen fisik — rekening koran, SPT, berita acara, bukti terima gudang — auditor kini punya tempat untuk **melampirkan dokumennya dan mengetikkan angka yang ia baca dari sana**. Sesudah itu sistem yang membandingkan dengan pembukuan, bukan orang. Hari ini tempat itu tidak ada sama sekali; yang bisa ditulis auditor cuma satu kalimat bebas.
- **Siapa terdampak**: auditor internal sebagai satu-satunya yang melampirkan dan mencatat. Direksi dan pembaca melihat hasilnya beserta dokumen sumbernya. Divisi yang diperiksa tidak mendapat akses.
- **Tidak dijanjikan**: keputusan ini **tidak** membuat sistem membaca rekening koran sendiri. Angka tetap diketik orang. Ia juga **tidak** menghidupkan dua belas pengujian sekaligus — sebelas di antaranya belum punya mesin pembandingnya, dan lampiran saja tidak membuatnya berjalan; yang benar-benar terbuka hari pertama **satu** pengujian. Pembacaan otomatis oleh AI dicatat sebagai tahap terpisah dan **belum diputuskan**, sebab ia menuntut rekening koran dikirim ke layanan di luar perusahaan.
- **Besaran kerja**: kecil untuk apa yang dibuka. Cara mengunggah dokumen **sudah ada dan sudah dipakai** modul arsip pajak di service yang sama, jadi yang dikerjakan sebagian besar menirukan yang sudah jalan, ditambah satu tempat baru untuk mencatat angkanya.

## Deskripsi

*Dua belas pengujian audit membandingkan pembukuan dengan dokumen fisik yang tak ada di sistem mana pun. Bukti itu **dilampirkan** ke barisnya dan angkanya **dicatat manusia**, lalu perbandingannya dikerjakan mesin secara deterministik. Pembacaan otomatis (pengurai CSV, lalu model penglihatan untuk pindaian) dipisah sebagai tahap tersendiri yang berprasyarat persetujuan Direksi, dan keluarannya tidak pernah boleh langsung dipakai.*

- **Status**: ⚠️ **Implemented sebagian** — §1-§3 dan §5 **SUDAH DIKERJAKAN** 2026-09-03: prefix MinIO `audit/` (bip-erp [#1699](https://github.com/bip-itteam-internal/bip-erp/pull/1699)), koleksi `audit_bukti` + empat rute ([#1700](https://github.com/bip-itteam-internal/bip-erp/pull/1700)), keduanya merged. **§4 (pembacaan otomatis) belum dimulai** dan tetap berprasyarat persetujuan Direksi. ⛔ **Belum bisa dipakai siapa pun**: layarnya belum ada, dan `MINIO_AUDIT_KEY` belum diisi di `.env` mana pun
- **Path di repo**: `bip-erp/services/finance/audit_bukti.go` (baru) · `bip-erp/services/finance/audit_kertas_kerja.go` · `bip-erp/services/finance/audit_handler.go` · `bip-erp/services/file/main.go` · `bip-erp/docker-compose.yml` · `audit-bharata/src/features/audit/components/detail-uji-panel.tsx`
- **Tanggal**: 2026-09-03

## Context

### Kebutuhan yang diminta bukan kebutuhan yang terukur

Permintaannya berbunyi *"rekening koran perlu diunggah lalu dianalisa AI"*, dengan alasan dua belas pengujian mandek menunggu dokumen. Pengukuran ke registry membalikkan alasannya:

**Sebelas dari dua belas pengujian ber-`SumberUnggahan` belum punya penjalan sama sekali** (`services/finance/audit_registry.go`). Keduanya membalas `KeadaanBelumDiimplementasi`, bukan `KeadaanMenungguData`. Hanya `jurnal_manual_besar` yang punya penjalan. Diukur di prod 2026-09-03 lewat layar kertas kerja periode 2026-08: **32 baris `belum diimplementasi`, 4 `gagal ditarik`, 0 `menunggu data`.**

Artinya jalur unggah, dibangun sendirian, **membuka nol dari sebelas pengujian itu**. Klaim "dua belas mandek karena tak ada jalur unggah" salah, dan menerimanya akan menghasilkan fitur yang benar secara teknis untuk masalah yang tidak ada.

### Yang benar-benar tidak ada

`ujiJurnalManualBesar` (`audit_uji_aturan.go:273`) sudah menunjukkan bentuk yang dituju: ia menarik jurnal, mengurutkan menurut nilai, memilih sampel terarah, mengisi `HasilUji.Terpilih`, lalu berhenti di `KeadaanMenungguData` dengan kalimat *"Menunggu dokumen sumbernya ditunjukkan."*

Sistem sudah tahu apa yang ia tunggu dan dari item mana. **Yang tak ada adalah tempat menjawabnya.** `Tinjauan` (`audit_kertas_kerja.go:44`) hanya `{Oleh, Pada, Alasan}` — tiga field teks, tanpa slot lampiran dan tanpa slot angka. Sembilan rute audit yang terdaftar (`audit_handler.go:331-341`) tak satu pun menerima berkas.

### Yang sudah ada, dan menentukan besaran kerjanya

- **`services/file`** menyimpan ke MinIO dengan **peta akses per-prefix**: tiap modul punya kunci tulis dan kunci baca sendiri (`employee/`, `attendance/`, `kas-kecil/`, `pembayaran/`, `pajak/`, `form/`). Prefix bukan sekadar penamaan — ia yang membatasi siapa boleh membaca apa.
- ⭐ **`services/finance/pajak_arsip.go` sudah mengunggah bukti ke file-service dari service yang sama dengan audit.** Ia memuat seluruh keputusan yang berulang: batas 4 MB yang mencerminkan `services/file/main.go:252`, **daftar-izin** ekstensi (`.pdf .jpg .jpeg .png`) bukan daftar-tolak, hex acak pada nama objek supaya unggahan kedua tak menimpa yang pertama, dan catatan bahwa kunci salah dijawab `invalid access key` — galat yang tak menyebut sebabnya. Ada testnya (`pajak_arsip_test.go`).
- **`HasilUji.Terpilih []string`** (`audit_uji.go:82`) sudah menghasilkan daftar item yang menuntut bukti, dan **`KeadaanMenungguData`** sudah berarti persis keadaan ini.

Jadi ini bukan membangun sistem unggah. Ini menambah satu prefix MinIO dan meniru berkas yang sudah teruji di service yang sama.

### ⛔ Dua bentuk berbeda yang registry tidak membedakannya

| Bentuk | Uji | Yang dikerjakan manusia | Guna pembacaan otomatis |
|---|---|---|---|
| **A. Bukti per item terpilih** | jurnal manual besar, penyesuaian persediaan, kapitalisasi vs beban, retur penjualan, pisah batas penjualan, penjualan PT ke CV | melampirkan dokumen **per item** dan menilai apakah ia mendukung entrinya | **hampir nihil** — yang diminta penilaian, bukan ekstraksi |
| **B. Angka dari satu dokumen** | rekonsiliasi bank, rekonsiliasi pajak, kas rekening CV, piutang iklan ke CV | membaca saldo/mutasi dari satu dokumen | **di sinilah letaknya**, dan hanya di sini |

Empat dari dua belas. Merancang seluruh fitur di sekitar pembacaan otomatis berarti mengoptimalkan sepertiganya sambil membiarkan dua pertiga sisanya tanpa tempat menaruh bukti.

### ⛔ Taruhannya lebih besar dari yang terlihat

Peraturan Perusahaan Pasal 54 menetapkan denda **Rp 2.000.000.000** untuk pelanggaran informasi rahasia dan **Rp 5.000.000.000** untuk penyalahgunaan wewenang, dan menulis eksplisit bahwa sanksi itu *"harus tercatat dalam sistem audit"* (`mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md:87-89`). Temuan modul ini karena itu dapat menjadi dasar sanksi bernilai miliaran.

Konsekuensinya mengikat rancangan: **angka hasil pembacaan mesin yang tak pernah dikonfirmasi manusia tidak boleh menjadi dasar tunggal sebuah temuan.** Ini bukan kehati-hatian umum; ini kelas kegagalan yang sudah berulang di repo ini dalam bentuk lain — angka salah yang masuk akal, tanpa galat dan tanpa test merah.

### Status dokumen yang menopang

[[Finance - Audit Internal]] ✅ dan [[Microservices - File Service]] ✅ menggambarkan yang sudah ada. [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]] ⚠️ **implemented sebagian**: §1 (pemisahan service) belum dimulai, jadi keputusan ini ditulis untuk modul audit **yang masih di dalam finance-service**, dan ikut pindah bersamanya kelak.

## Decision

### 1. Bukti dilampirkan ke BARIS, angkanya dicatat TERPISAH dari alasannya

`Tinjauan` tidak diperluas. Bukti tinggal di strukturnya sendiri, karena keduanya menjawab pertanyaan yang berbeda: alasan adalah **kesimpulan**, bukti adalah **bahan**. Satu baris dapat memiliki banyak bukti dan satu kesimpulan.

Tiap bukti memuat: item terpilih yang dijawabnya (kosong untuk Bentuk B), objek MinIO, nama berkas asli, siapa dan kapan, serta **angka yang dibaca manusia beserta satuannya**.

⚠️ **Angka dicatat sebagai field tersendiri, bukan diselipkan di teks alasan.** Angka yang hanya hidup di kalimat tak bisa dibandingkan mesin, dan perbandingan itulah seluruh gunanya.

### 2. Prefix MinIO `audit/` sendiri, bukan menumpang `pajak/`

Peta akses file-service berbasis prefix, jadi menumpang prefix modul lain berarti siapa pun yang boleh membaca arsip pajak ikut boleh membaca rekening koran. Kunci tulis dan kunci baca dipisah, mengikuti pola yang sudah ada.

### 3. Perbandingannya deterministik, dan dikerjakan penjalan uji

Setelah angka tercatat, penjalan uji membandingkannya dengan sisi pembukuan seperti uji lain — `bersih` atau `berbunyi` menurut kondisi idealnya. **Tidak ada jalur di mana manusia menyatakan sendiri hasilnya bersih**; manusia menyediakan bahan, mesin yang menyimpulkan. Vonis manusia tetap ada, tetapi lewat `Tinjauan` yang sudah ada dan tetap menuntut alasan tertulis.

### 4. Pembacaan otomatis dipisah jadi tahap sendiri, dan keluarannya selalu DRAF

Tidak dikerjakan pada tahap ini. Ketika dikerjakan, urutannya wajib:

1. **Pengurai deterministik** untuk CSV/XLS dan PDF berteks. Bila bank memberi e-statement tabel, model tidak dipakai sama sekali — penguraian deterministik persis, gratis, berulang, dan bisa direview orang.
2. **Model penglihatan lewat API luar** hanya untuk dokumen tanpa teks terbaca mesin.

⛔ **Keluaran keduanya mengisi field angka sebagai draf yang WAJIB dikonfirmasi auditor sebelum dipakai.** Tidak ada jalur yang melewatkan konfirmasi itu, termasuk untuk pengurai deterministik: yang membedakan bukti dari tebakan adalah ada orang yang menyatakan angkanya benar.

⛔ **Prasyarat yang belum terpenuhi**: mengirim rekening koran ke API di luar perusahaan menuntut **persetujuan tertulis Direksi**. Pemilik pekerjaan menyatakan itu dapat diterima **dengan persetujuan Direksi** (2026-09-03); persetujuannya sendiri belum ada. Sampai ada, tahap ini tidak dimulai.

#### Endpoint AI internal: diukur 2026-09-03, dan hasilnya mengubah bentuk tahap ini

`https://code.bharatainternasional.com/v1` adalah **relay ke Anthropic, bukan model yang berjalan di infrastruktur sendiri.** Buktinya: model yang ditawarkan Claude dan MiniMax-M3 — Claude tak bisa di-self-host — dan id pesan berbentuk `msg_011Ceg…`, format asli Anthropic. Auth ditegakkan (401 tanpa kunci maupun dengan kunci ngawur).

**Artinya rekening koran tetap keluar dari gedung, dan prasyarat persetujuan Direksi di atas berlaku utuh.** Nama domain sendiri tidak mengubahnya.

⛔ **Risiko yang belum pernah tercatat: router boleh memilih penyedia sendiri.** Dari sembilan model, satu bernama `Claude` (`owned_by: combo`) dan satu `token-router/MiniMax-M3`. Memakai id `Claude` berarti **tidak mengendalikan penyedia mana yang melihat rekening koran** — ia bisa mendarat di MiniMax. **Aturannya: selalu patok id `cc/claude-*` eksplisit, jangan pernah `Claude` atau apa pun di bawah `token-router/`.**

⛔ **Relay itu MENELAN lampiran PDF, dan mode gagalnya berbeda per jalur.** Diuji dengan PDF sintetis berisi `SALDO AKHIR 87.654.321,09`:

| Jalur | Hasil |
|---|---|
| `/v1/messages` + blok `image` | ✅ `87654321.09` benar |
| `/v1/chat/completions` + `image_url` PNG | ✅ `87654321.09` benar |
| `/v1/messages` + blok `document` (PDF) | ⚠️ 200, model menjawab jujur *"tidak dapat membaca dokumen"* |
| `/v1/chat/completions` + blok `file` (PDF) | ⛔ 200, JSON sah, **`{"saldo_akhir":0}`** — angka karangan |

**Kontrol negatif yang membuktikannya**: pertanyaan yang sama **tanpa lampiran apa pun** menjawab `{"saldo_akhir": 1000000}` — juga karangan. PDF-nya tak menyumbang satu bit pun.

Baris terakhir tabel itu adalah kelas kegagalan yang seluruh ADR ini dibuat untuk mencegah, dan ia terbukti sendiri dalam satu percobaan: status 200, JSON sah, bentuk persis seperti diminta, **angka salah**, tanpa satu pun galat.

**Dua konsekuensi mengikat untuk §4:**

1. **PDF WAJIB dirender jadi gambar per halaman lebih dulu.** Mengirim PDF apa adanya tidak menghasilkan galat, ia menghasilkan angka karangan.
2. **Verifikasi ekstraksi WAJIB punya kontrol negatif**: kirim pertanyaan yang sama tanpa lampiran. Kalau jawabannya tetap keluar, ekstraksinya tidak terjadi — dan tanpa kontrol ini tak ada cara membedakan bacaan dari karangan.

⚠️ Gotcha integrasi: endpoint ini **default-nya SSE**. Tanpa `"stream": false` eksplisit ia membalas `data: {…}` beruntun, dan klien Go yang mengurai JSON biasa gagal dengan galat yang menunjuk ke bentuk respons, bukan ke sebabnya.

⚠️ Subdomain `code.` dan prefiks `cc/` mengesankan gateway ini diperuntukkan bagi Claude Code, bukan sebagai backend aplikasi. Memakainya di produksi berarti modul audit ikut mati bila gateway itu mati.

### 5. Berkas sumbernya disimpan selamanya, bukan cuma angkanya

Temuan yang angkanya tak dapat ditelusuri balik ke halaman dokumen asalnya bukan bukti. Berkas tidak dihapus saat baris ditinjau ulang atau periode ditutup.

## Consequences

**Yang menjadi mungkin.** `jurnal_manual_besar` selesai penuh sejak hari pertama — ia sudah memilih sampelnya dan hanya menunggu tempat menjawab. Sebelas uji Bentuk A dan B mendapat tempat yang sudah siap begitu penjalannya menyusul, jadi tiap penjalan baru tak perlu memikirkan lagi cara menyimpan buktinya.

**Yang tetap tidak mungkin.** Sebelas uji itu **tetap tidak berjalan** setelah keputusan ini; masing-masing masih menunggu penjalannya ditulis. Keputusan ini sengaja tidak menjanjikan sebaliknya.

⚠️ **Batas 4 MB belum diukur terhadap rekening koran pindaian sungguhan.** Ia batas file-service (`services/file/main.go:252`), bukan batas audit, jadi menaikkannya menyentuh seluruh modul yang memakainya. Bila ternyata kekecilan, itu keputusan tersendiri — jangan diam-diam dinaikkan di satu sisi saja.

⚠️ **Env baru `MINIO_AUDIT_KEY` menuntut `docker compose up -d --force-recreate` pada file-service DAN finance-service**, bukan `restart`. Env dibaca saat container dibuat. Kunci yang belum terpasang dijawab `invalid access key` — galat yang tak menyebut sebabnya, dan sudah pernah memakan waktu di jalur arsip pajak.

⛔ **TIDAK ADA `MINIO_AUDIT_READ_KEY`, dan itu koreksi terhadap rancangan awal ADR ini.** Versi pertama menyebut sepasang kunci. Yang membatalkannya: kunci baca hari ini sampai ke **peramban** lewat `NEXT_PUBLIC_MINIO_*_READ_KEY` (`erp-frontend/src/hooks/use-document.ts`), ditanam ke bundel klien saat build, dan satu kunci baca memberi akses ke **seluruh prefix**. Kunci baca `audit/` karena itu berarti tiap rekening koran terbaca siapa pun yang punya bundelnya — persis kebalikan dari yang dijanjikan [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]]. Pembacaan berkas lewat **proxy di sisi server** yang memakai kunci **tulis** dan memeriksa `audit.view` setiap kali. Penolakannya dikunci `TestPrefixAuditTakPunyaKunciBaca`; rinciannya di [[Microservices - File Service]].

⚠️ **Nilai `MINIO_AUDIT_KEY` wajib berbeda dari seluruh kunci lain.** `bangunAccessMap` menolak tabrakan dengan membuang **kedua** entri, jadi menyalin nilai `MINIO_PAJAK_KEY` ke sini tidak membuat keduanya jalan — ia mematikan keduanya.

**Kontrak berubah, jadi BE naik sebelum FE.** Aplikasi `audit-bharata` menampilkan bukti hanya bila field-nya ada; tanpa itu panel detail tetap berfungsi tanpa blok bukti.

**Ikut pindah bersama [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]] §1.** Bila audit menjadi service sendiri, prefix MinIO dan rute unggahnya pindah bersamanya. Prefix `audit/` justru mempermudah: pemisahannya tidak menyentuh berkas modul lain.

**Yang sengaja tidak diputuskan di sini.**

- **Apakah pembacaan otomatis jadi dikerjakan**, dan dengan model apa. Menunggu persetujuan Direksi.
- **Apakah kelompok tiga belas uji konsistensi internal dihidupkan kembali** — sudah berdiri sebagai TBD di [[Finance - Audit Internal]] dan tidak tersentuh keputusan ini.
- **Retensi berkas.** Disimpan selamanya untuk sekarang; kebijakan pemusnahan menuntut keputusan Finance.

## Dokumen Terkait

- [[Finance - Audit Internal]] · [[APP - Audit Internal]]
- [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]] · [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]]
- [[Microservices - File Service]] · [[API - File Service]]
- [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]]
