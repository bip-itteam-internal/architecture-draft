## Deskripsi

*Aturan penamaan untuk dua hal yang muncul berdampingan di layar KPI: **sumber/metrik katalog** (dibuat dev, tampil di dropdown "Sumber data") dan **metrik template** (dibuat HR, tampil sebagai baris penilaian). Keduanya sering ditulis panjang, tanpa keterangan, atau bernama tak deskriptif, dan akibatnya jatuh ke orang yang mengisi KPI, bukan ke yang menamainya.*

- **Status**: ✅ Berlaku sejak 2026-08-25, dan **seluruh sumber produksi sudah memenuhinya** (lihat "Keadaan terukur"). Dijaga test, bukan oleh dokumen ini. Aturannya diturunkan dari label yang benar-benar terpasang, bukan dari selera.
- **Ruang lingkup**: kamus label di `erp-frontend/src/features/hris/kpi/lib/label-otomatis.ts` + `src/i18n/locales/{id,en}.ts`, dan field `label`/`description` pada `kpi_template` ([[Microservices - Employee Service]]).

## Dua hal yang dinamai, dan siapa pemiliknya

| Yang dinamai | Siapa menamai | Tampil di mana | Kalau buruk |
|---|---|---|---|
| **Sumber & metrik katalog** (`kinerja_toko`, `retur_persen`) | dev, saat mendaftarkan sumber | dropdown "Sumber data" | pengisi tak tahu sumber mana yang benar, lalu memilih yang salah tanpa ada yang berbunyi |
| **Metrik template** (`Performance Monitoring Team`) | HR, saat menyusun template | baris penilaian per karyawan | yang dinilai tak tahu apa yang diukur darinya |

Aturannya sama untuk keduanya. Yang berbeda hanya siapa yang menanggung akibatnya.

## Aturan label

**1. Label menyebut YANG DIUKUR, bukan targetnya.** Angka target berubah tiap periode; label tidak boleh ikut basi.

| ⛔ | ✅ |
|---|---|
| `Revenue 240M` | `Revenue` (target 240 juta ditaruh di target, bukan di nama) |
| `Turn Over Rate Target 5% per Tahun` | `Turnover karyawan` |
| `Mengurangi piutang aging > 60 hari sampai < 5% dari total AR` | `Piutang lewat 60 hari` |

**2. Label tidak bernomor tanpa makna.** `Performa 1`, `Administrasi 3`, `Perfomance 2` tidak memberi tahu apa pun kepada yang dinilai, dan tak bisa dibedakan satu sama lain di daftar.

**3. Ringkas secukupnya agar tidak terpotong.** Batasnya bukan angka keramat melainkan **lebar kontrol yang benar-benar dipakai**: pemilih sumber selebar `w-60`, dan label di atas ±28 karakter terpotong di sana. Bila lebar kontrolnya berubah, angkanya ikut berubah; yang tetap adalah kewajiban memeriksanya di layar, bukan di editor.

**4. Yang tidak muat pindah ke keterangan, bukan dipendekkan sampai kabur.** `Penjualan tercatat sebelum cutoff (persen)` lebih baik jadi label `Penjualan tepat waktu` dengan keterangan yang menjelaskan cutoff-nya.

**5. Jangan mengandalkan perapian token.** Sumber tanpa entri kamus tampil sebagai hasil `rapikanToken` (`kinerja_po_marketing` → "Kinerja po marketing"): kapitalisasi acak, singkatan tak terbuka, dan **tanpa keterangan sama sekali**. Itu jaring pengaman supaya sumber baru tak hilang, bukan penamaan.

## Aturan keterangan

**1. Keterangan WAJIB, dan menjawab dua hal**: apa yang dihitung, dan **dari menu mana angkanya bisa dilihat sendiri**. Yang kedua yang membuat angkanya bisa ditelusuri alih-alih dipercaya begitu saja.

> ✅ `Persentase retur terhadap revenue per toko. Menu Marketing (Laba per Level).`

**2. Satu keterangan tidak boleh dipakai dua label.** `kaizen_ide_diajukan` dan `kaizen_ide_diterapkan` berbagi satu kalimat "ide yang diajukan/diterapkan", sehingga justru pada titik pengisi perlu membedakannya, keterangannya diam. Dua metrik berbeda menuntut dua kalimat berbeda.

**3. Keterangan bukan pengulangan label.** "Kinerja tiket: kinerja tiket" tidak menambah apa pun; lebih baik menyebut sumber datanya.

**4. Untuk metrik template, `description` adalah tempat TARGET yang sebenarnya.** `kpi_template` tak punya field target yang dapat dibaca mesin untuk metrik manual, jadi angkanya hidup di sana. Satu deskripsi memuat lebih dari satu angka membuat metriknya mustahil diotomatiskan tanpa bertanya ke pemiliknya lebih dulu (lihat [[HRIS - Matriks KPI per Departemen]]).

## Keadaan terukur

Diukur langsung ke kamus label dan katalog produksi, bukan diperkirakan.

| Yang diukur | Saat aturan ditulis | Sesudah dibereskan |
|---|---:|---:|
| Sumber terdaftar di backend | 20 | 20 |
| Punya entri label **dan** keterangan | **10** | **20** |
| Tampil sebagai token dirapikan, tanpa keterangan | **10** | **0** |
| Label melewati ±28 karakter (terpotong di `w-60`) | **4** | **0** |
| Keterangan dipakai lebih dari satu label | **1** (Kaizen) | **0** |

Keempat label yang dulu terpotong, beserta penggantinya. Detail yang hilang dari label **pindah ke keterangan**, tidak dibuang:

| Sebelum | Panjang | Sesudah |
|---|---:|---|
| `Penjualan tercatat sebelum cutoff (persen)` | 42 | `Penjualan tepat waktu` |
| `Retur tuntas sebelum cutoff (persen)` | 36 | `Retur tuntas tepat waktu` |
| `Kinerja affiliate (per tim channel)` | 35 | `Affiliate per tim` |
| `Pembayaran tepat waktu (persen)` | 31 | `Pembayaran tepat waktu` |

⚠️ **Angka di kolom kanan tidak dijaga oleh dokumen ini, melainkan oleh test.** `label-otomatis.aturan.test.ts` di erp-frontend memeriksa tiap sumber produksi punya label dan keterangan di dua locale, panjangnya tak melewati batas, keterangannya tak dipakai bersama, dan tak sekadar mengulang labelnya. Dokumen yang menyimpan angka tanpa penjaga akan usang dalam hitungan minggu; yang menjaganya di sini adalah suite, dan tabel ini hanya menerangkan kenapa penjaga itu ada.

⛔ **Penjaga itu menutupi SUMBER, tidak METRIK, dan keduanya daftar yang berbeda.** `SUMBER_PRODUKSI` memuat 20 dari 20 sumber produksi, sehingga sumber baru yang tak berlabel pasti memerahkan suite. `METRIK_DIKENAL` berdiri sendiri dan per 2026-08-26 memuat **14 dari 37** entri kamus metrik. Konsekuensinya tajam: metrik yang tak punya entri kamus **dan** tak didaftarkan di situ tidak terlihat oleh siapa pun, sementara tabel di atas tetap sah berbunyi "20 dari 20".

Itu bukan kemungkinan teoretis. `piutang_lewat_14_persen` dan `piutang_lewat_60_persen` sudah terdaftar di backend dan yang kedua sudah dipakai template produksi `AR STAFF PIUTANG`, tetapi keduanya tak punya entri kamus sama sekali sampai 2026-08-26 dan tampil sebagai token dirapikan tanpa keterangan. Sumbernya, `kinerja_ar`, berlabel lengkap sepanjang waktu itu.

⚠️ **Kelalaian yang sama punya bentuk kedua yang lebih senyap**: `SATUAN_PER_METRIK` di `konfigurasi-otomatis-rules.ts`. Metrik yang absen di sana jatuh ke penurunan formula, dan `rata_rata` menghasilkan `nilai` yang dirender bersuffix **`x`** (satuan ROAS). Target 5 **persen** karena itu tampil sebagai "5 x": angkanya benar, satuannya menyesatkan, dan tak satu pun test menangkapnya. **Metrik baru wajib didaftarkan di EMPAT tempat**, bukan satu: kamus label, daftar penjaga `METRIK_DIKENAL`, `SATUAN_PER_METRIK`, dan `FORMULA_PER_METRIK`.

**Terjadi lagi 2026-08-27, dan kali ini pada EMPAT tempat.** Tiga metrik `kinerja_live` (`conversion_rate` · `add_to_cart_rate` · `avg_viewing_duration`) masuk tanpa entri di `SATUAN_PER_METRIK` **maupun** `FORMULA_PER_METRIK`, sehingga Tipe isian jatuh ke penurunan formula dan memberi `nilai (0 sampai 100)` untuk ketiganya. Bahayanya berbeda per metrik dan tak satu pun bergalat: target `60` **detik** dibaca sebagai skor 0–100, target `2` **persen** dibaca sebagai 2 unit. Ketahuannya bukan dari test melainkan dari layar — Tipe isian menampilkan "jumlah" yang **kebetulan benar** karena bawaan template lama, bukan hasil penurunan dari metriknya. Diperbaiki bersama penjaganya (erp-frontend [#1277](https://github.com/bip-itteam-internal/erp-frontend/pull/1277)); penjaga barunya juga menuntut **keterangan menyebut SATUAN targetnya**, karena "isi target" tanpa satuan menyisakan pertanyaan yang tak bisa dijawab pengisi dari layar.

⛔ **`conversion` membuktikan kamus metrik yang DATAR tidak cukup.** Nama itu kini dipakai **tiga** sumber dengan arti berbeda — order affiliate milik karyawan (`kinerja_affiliate`), total order channel tim (`kinerja_affiliate_tim`), dan pesanan dibayar dari siaran live (`kinerja_live`) — sehingga pengisi template Host Live membaca keterangan affiliate, kalimat yang salah total untuk metrik yang sedang ia pilih. Jalan keluarnya `METRIK_PER_SUMBER` berkunci `"<sumber>|<metrik>"` yang menang atas entri umum (erp-frontend [#1267](https://github.com/bip-itteam-internal/erp-frontend/pull/1267)). **Metrik bernama umum wajib memakai entri khusus-sumber sejak awal**, jangan menunggu tabrakannya terjadi.

### 🟡 `rasio_beban_non_ops_persen` — contoh kerja aturan ini (2026-08-31)

Metrik baru pada sumber **`admin_non_ops`** untuk KPI F3 SPV Finance (erp-frontend PR [#1332](https://github.com/bip-itteam-internal/erp-frontend/pull/1332), branch `feat/kpi-rasio-non-ops`, **sudah merge** ke `origin/main` 31 Agustus 2026, merge commit `de1f24ea`; backend bip-erp PR [#1548](https://github.com/bip-itteam-internal/bip-erp/pull/1548), merge commit `fea804a7`, juga sudah di `origin/main`). Dicatat di sini karena ia melewati checklist empat-tempat dengan hasil yang berbeda per tempat.

| Locale | Label | Keterangan |
|---|---|---|
| `id.ts` | `Rasio beban non-ops` (20 karakter) | "Beban admin & non-operasional (Iuran & Sumbangan, Bank, Entertainment Adum) dibagi pendapatan periode itu, dalam persen. Target maksimal 2%." |
| `en.ts` | `Non-ops expense ratio` | "Admin & non-operational expenses (Dues, Bank Fees, Entertainment) divided by that period's revenue, in percent. Target maximum 2%." |

Kunci i18n: `hris.kpi.mtkRasioNonOps` / `…Ket`.

Checklist **empat tempat**, apa adanya:

| Tempat | Status | Catatan |
|---|---|---|
| Kamus label (`label-otomatis.ts` `METRIK`) | ✅ | |
| `METRIK_DIKENAL` (`label-otomatis.aturan.test.ts`) | ✅ | metrik masuk penjaga dua-locale |
| `SATUAN_PER_METRIK` (`konfigurasi-otomatis-rules.ts`) | ✅ `persen` | **wajib**; tanpanya target `2` **persen** dirender "2 x" (satuan ROAS) |
| `FORMULA_PER_METRIK` | ⬜ tidak diisi | **bukan kelalaian** — lihat di bawah |

⚠️ **Kenapa `FORMULA_PER_METRIK` sengaja dilewati di sini**, dan kapan itu sah. `formulaKatalog` (`auto-block-rules.ts:92-103`) mengambil rumus dari **katalog backend** lebih dulu (`formula_metrik` → `formula_baku`), dan hanya jatuh ke `FORMULA_PER_METRIK` sebagai **jaring terakhir** untuk jendela antar-deploy. Diverifikasi 2026-08-31: **tak satu pun sumber grup Finance** (`kinerja_ar`, `varians_anggaran`, `forecast_kas`, `kinerja_cost_control`, `admin_non_ops`) memanggil `DaftarkanFormulaSumber`, jadi ketiganya sama-sama mengembalikan `undefined`. Akibatnya pengisi **diminta memilih rumus sendiri**, dan itu memang perilaku yang dikehendaki (komentar `formulaKatalog`: rumus yang salah tak menghasilkan galat, hanya angka salah yang tampak wajar — lebih baik meminta pengisi memilih daripada memilihkan).

⛔ **Bedanya tajam dengan `SATUAN_PER_METRIK`, dan itu yang membuat satuan wajib sementara formula tidak**: satuan yang absen **tidak** meminta apa pun kepada pengisi — ia diam-diam merender suffix yang salah. Formula yang absen berhenti dan bertanya. Aturannya karena itu: **satuan selalu wajib; formula wajib hanya bila sumbernya mendaftarkan formula ke katalog atau kamu ingin ada nilai awal.**

⚠️ Metrik ini **tidak** butuh `METRIK_PER_SUMBER`: namanya tidak dipakai sumber lain mana pun (per 2026-08-31). Bila kelak dipakai, entri per-pasangan wajib ikut.

### ✅ `piutang_lewat_90_persen` — metrik ketiga rumpun AR

Metrik baru pada sumber **`kinerja_ar`** yang sudah ada, untuk `Pengawasan 100% AR aging ≤ 90 hari.` (template `AR Staff 2026`, bobot **0,50**). **Live di dev & prod 31 Agustus 2026** (bip-erp [#1579](https://github.com/bip-itteam-internal/bip-erp/pull/1579), erp-frontend [#1351](https://github.com/bip-itteam-internal/erp-frontend/pull/1351)); konfigurasi templatenya belum dinyalakan HR. Dicatat di sini karena ia menempuh checklist empat-tempat dengan hasil yang sama dengan `rasio_beban_non_ops_persen`, dan karena penjaganya menyingkap pelanggaran pada dua metrik yang SUDAH lama hidup.

| Locale | Label | Keterangan |
|---|---|---|
| `id.ts` | `Piutang lewat 90 hari` (21 karakter) | "Porsi nominal piutang macet yang belum tertagih lebih dari 90 hari terhadap total piutang terbuka, dalam persen. Bagian tertua dari piutang lewat 60 hari, jadi keduanya tidak boleh dijumlahkan. Makin kecil makin baik: pilih arah Turun, dan isi target sebagai anggaran yang masih dapat diterima (anjuran 1). Menu Finance (Accounts Receivable)." |
| `en.ts` | `Receivables past 90 days` | "Share of bad-debt receivables uncollected for more than 90 days… Lower is better: pick the Down direction…" |

Kunci i18n: `hris.kpi.mtkPiutangLewat90` / `…Ket`.

| Tempat | Status | Catatan |
|---|---|---|
| Kamus label (`label-otomatis.ts` `METRIK`) | ✅ | |
| `METRIK_DIKENAL` | ✅ | |
| `SATUAN_PER_METRIK` | ✅ `persen` | **wajib**; tanpanya target `1` **persen** dirender "1 x" |
| `FORMULA_PER_METRIK` | ⬜ tidak diisi | sama alasannya dengan seluruh sumber grup Finance yang tak memanggil `DaftarkanFormulaSumber` |
| `METRIK_PER_SUMBER` | ⬜ tidak perlu | nama metriknya tak dipakai sumber lain mana pun (per 2026-08-31) |

⛔ **Keterangannya menyebut ARAH, dan itu bukan kelebihan melainkan keharusan di sini.** Metrik ini berbobot 0,50, jadi arah `naik` yang keliru memberi **skor penuh** tanpa satu pun galat, sementara kalimat penjelas di layar ikut membenarkannya. Terukur di prod: realisasi Juli 2026 **11,76%** bernilai 8,5 pada arah `turun` target 1, dan akan bernilai **100** bila arahnya terbalik. Layar Atur Target membuka dengan toggle "Makin besar makin baik", sehingga keterangan adalah satu-satunya tempat pengisi membaca arah yang benar pada saat ia memilih. Penjaganya `label-otomatis.aturan.test.ts` menuntut frasa arahnya ada di **kedua** locale.

⚠️ **Penjaga satuan yang ditulis bersamanya memerahkan DUA metrik yang sudah lama dipakai template produksi**: keterangan `piutang_lewat_14_persen` dan `piutang_lewat_60_persen` sama sekali tak menyebut satuan maupun arah. Keduanya ikut dibetulkan, satu frasa masing-masing. Polanya sama dengan temuan `kinerja_affiliate_tim` di bawah: **penjaga yang ditulis untuk entri baru hampir selalu menemukan entri lama yang melanggar aturan yang sama**, dan itu justru gunanya.

### 🟡 `program_culture` — sumber baru (branch `feature/workspace-position`)

Sumber KPI baru dari [[Microservices - Form Builder Service]] (`GET /internal/culture/metrics`), memasok metrik `culture` KPI Culture & Industrial. **Belum merge/prod.** Nilainya **skor komposit** program culture (blueprint 30/30/40), bukan % sesuai jadwal — lihat [[ADR - 0066 Modul Kelola Program Culture]]. Label ramah + keterangan ditaruh di kamus `label-otomatis.ts` dan dua locale `src/i18n/locales/{id,en}.ts`.

| Locale | Label sumber | Keterangan |
|---|---|---|
| `id.ts` | `Program Culture: skor komposit` | "Skor komposit program culture (partisipasi, antusiasme, implementasi) dari penilaian peserta, dirata-rata per periode. Untuk jabatan Culture & Industrial." |
| `en.ts` | `Culture Program: composite score` | "Composite culture-program score (participation, enthusiasm, implementation) from participant ratings, averaged per period. For the Culture & Industrial role." |

Kunci i18n: **`srcProgramCulture` / `srcProgramCultureKet`** (dengan awalan `src` karena ini penamaan **SUMBER**, bukan metrik template — bedakan dari `mtk*` untuk metrik). Sumber ini **tanpa sub-metrik**, jadi tak butuh entri `METRIK_PER_SUMBER`; nama metrik yang dilayaninya (`culture`) unik dan tak dipakai sumber lain (per 2026-08-30). `SATUAN_PER_METRIK`/`FORMULA_PER_METRIK`: formula bakunya `rata_rata` (nilai 0–100), jadi mengikuti aturan yang sama dengan sumber Finance — formula boleh dilewatkan bila pengisi diminta memilih; satuan tetap wajib bila targetnya bukan skala 0–100.

## ⛔ Nama metrik menyiratkan ARAH, dan salah membacanya tak menimbulkan galat

Aturan ini soal penamaan, tetapi ada satu akibat penamaan yang tidak berhenti di layar: **nama metrik menentukan `arah` mana yang benar bagi siapa pun yang mengonfigurasinya.**

| Nama metrik mengembalikan | `arah` yang benar | Contoh terdaftar |
|---|---|---|
| akurasi, persentase-tercapai, cakupan, ketepatan waktu, uptime | `naik` | `akurasi_forecast_kas`, `uptime` |
| pelanggaran, keterlambatan, selisih, sisa, rasio-beban, retur | `turun` | `piutang_lewat_60_persen`, `varians_absolut_persen`, `rasio_beban_non_ops_persen`, `downtime`, `retur_persen` |

⚠️ **Terjadi di produksi 2026-08-31.** `akurasi_forecast_kas` dikonfigurasi `arah: turun`, sehingga akurasi **38,03%** terhadap target 95 dinilai **100/100** — arah `naik` yang benar memberi 40. Tak ada galat, dan kalimat penjelas di layar ikut membenarkannya. Yang membuatnya mudah terjadi: metrik lain di template yang sama (`piutang_lewat_60_persen`) berarah `turun` dan **itu benar**, jadi penyeragaman tampak masuk akal.

**Konsekuensinya untuk penamaan**: metrik yang namanya tak menyatakan besaran yang diukur (`kinerja_x`, `performa_2`) memaksa pengisi menebak arahnya. **Nama yang menyebut besarannya — `akurasi_…`, `…_persen`, `…_lewat_…`, `keterlambatan_…` — adalah petunjuk arah yang gratis.** Aturan lengkap beserta cara mengujinya di [[RUN - Menambah Metrik KPI Otomatis]] §"Arah mengikuti BUNYI KPI-nya"; kejadiannya di [[HRIS - Otomasi Skor KPI]] §"Kesalahan arah F4".

## Mengganti label yang sudah dipakai

**Metrik template aman diganti namanya** sejak tiap metrik punya `key` yang stabil: `IsiKunciMetrik` mempertahankan kunci yang sudah ada, jadi konfigurasi otomatis tidak lepas saat label dibetulkan. Sebelum ada `key`, backend memasangkan konfigurasi lewat label, dan memperbaiki typo berarti menghapus konfigurasinya tanpa pesan.

⚠️ **Yang TIDAK aman adalah mengganti token sumber/metrik katalog** (`kinerja_toko`, `retur_persen`). Token itu tersimpan di `auto.sumber`/`auto.metrik` tiap template, dan menggantinya membuat metrik yang sudah dikonfigurasi gagal hitung dengan pesan "sumber tidak terdaftar". Yang boleh diganti adalah LABELNYA, bukan tokennya.

⚠️ **Satu nama metrik boleh hidup di DUA sumber, dan sejak 2026-08-27 memang begitu.** `retur_persen` ada di `kinerja_toko` (dari mart marketing-analytics) **dan** di `insentif_profit` (dari dokumen retur terbukukan). Nama yang sama disengaja: satuan "persen", formula `rata_rata`, dan target 7 di template berkunci **nama metrik**, sehingga memindahkan sumbernya cukup mengganti satu field tanpa menyentuh yang lain ([bip-erp#1462](https://github.com/bip-itteam-internal/bip-erp/pull/1462)).

Konsekuensinya di layar: kedua opsi akan tampil dengan label yang **sama persis** kalau labelnya hanya berkunci nama metrik. Karena itu ada `METRIK_PER_SUMBER` berkunci `${sumber}|${metrik}` yang menang lebih dulu, dan `infoMetrik(token, sumber?)` menerima sumber sebagai argumen opsional ([erp-frontend#1257](https://github.com/bip-itteam-internal/erp-frontend/pull/1257)). Pemanggil yang tak tahu sumbernya tetap mendapat label lama — tak ada yang mendadak kosong. **Saat menambah metrik yang namanya sudah dipakai sumber lain, entri per-pasangan itu wajib ikut**, kalau tidak pengisi template tak punya cara membedakan mana yang benar selain menebak.

### ⛔ Aturan di atas dilanggar lagi tiga hari kemudian — dan jalan keluarnya bukan aturan keempat

`roas` dan `roas_bersih` ditambahkan ke `insentif_profit` 2026-08-28 (bip-erp `71aa32a1`) **tanpa** entri `METRIK_PER_SUMBER`, sehingga pemilih menampilkan **empat** entri ROAS yang dua-dua berlabel dan berketerangan sama persis. Yang membuat kejadian ini layak dicatat: aturannya sudah tertulis **dua kali** — di dokumen ini (paragraf di atas) dan di [[RUN - Menambah Metrik KPI Otomatis]] baris tabel `insentif_profit` — dan tetap terlewat, karena yang menambah metrik di backend tak punya alasan membuka dokumen frontend. Ketahuannya dari layar, seperti dua kali sebelumnya.

Bedanya bukan kosmetik: sumbu periodenya berlainan (tanggal order tanpa cutoff vs hari-kirim + cutoff tgl 25), dan prod 2026-08-26 mencatat median ROAS **4,06 vs 3,17** untuk 15 Account Specialist yang sama — cukup untuk menggeser siapa yang lolos target 4,5.

**Karena itu aturannya kini punya penegak, bukan cuma kalimat** (erp-frontend `fix/kpi-label-roas-per-sumber`, 2026-08-31):

| Lapis | Apa yang dilakukan | Batasnya |
|---|---|---|
| `bedakanLabelKembar` (`use-opsi-sumber.ts`) | Label yang muncul di lebih dari satu sumber dibubuhi nama sumbernya, saat itu juga | **Menyingkap** bahwa dua pilihan berbeda; TIDAK menjelaskan bedanya |
| Penjaga `pasanganKhususSumber()` (`label-otomatis.aturan.test.ts`) | Tiap entri khusus-sumber wajib berlabel & berketerangan beda dari entri umumnya, ada di dua locale, `en` bukan salinan `id` | Hanya menjaga entri yang SUDAH ditulis |

Daftar pasangan yang ditulis tangan sengaja **tidak** dipakai sebagai penjaga: daftar semacam itu bolong persis pada pasangan yang belum terpikirkan, dan bolongnya senyap — `METRIK_DIKENAL` di berkas yang sama memuat 14 dari 37 entri (lihat catatan di atas). Jaring runtime tak punya mode kegagalan itu.

⚠️ **Jaring bukan pengganti kamus.** "Konversi (order) · Affiliate per tim" memberi tahu pengisi bahwa ada dua hal berbeda, tetapi keterangannya tetap keterangan yang salah sampai ada yang menulis entri kamusnya.

**Temuan sampingan yang dibuka jaring itu**: `kinerja_affiliate_tim` ternyata sudah lama memakai label DAN keterangan milik `kinerja_affiliate` untuk `conversion` dan `affiliate_aktif` — kalimat "lewat akun **karyawan**" dan "**milik** karyawan" untuk metrik yang menilai satu tim channel, tempat semua staf di channel yang sama bernilai sama. Perbaikan `conversion` di erp-frontend [#1267](https://github.com/bip-itteam-internal/erp-frontend/pull/1267) menambahkan entri untuk `kinerja_live` dan melewatkan sumber tim ini. Kini keduanya punya entri sendiri (`mtkConversionTim`, `mtkAffiliateAktifTim`). **Perbaikan yang menutup satu tabrakan tidak menutup saudaranya** — itu pola yang sama dengan `SupervisedDepartments` yang harus diperbaiki dua kali dalam sehari.

### ⛔ Bentuk KEEMPAT: kamusnya benar, PEMANGGILNYA yang tidak mengirim sumber

> Ditemukan 2026-09-01 di `blueprint/kpi-scorecard.tsx` (erp-frontend branch
> `feat/kpi-scorecard-asal-data-rincian`, **belum merge**). Sudah diperbaiki di branch itu.

Ketiga bentuk sebelumnya soal **isi kamus**: entri yang belum ditulis, atau entri yang
dipakai bersama. Bentuk ini berbeda dan lebih senyap, sebab kamusnya sudah benar sejak awal.
`infoMetrik(token, sumber?)` menerima sumber sebagai argumen **opsional**, dan panel detail
metrik di scorecard memanggilnya `infoMetrik(m.metrikNama)` tanpa sumber, padahal ia
memegang `m.sumberNama` di variabel sebelahnya.

Akibatnya entri `METRIK_PER_SUMBER` tak pernah dicari, dan **sembilan** pasangan jatuh ke
entri umum yang kalimatnya salah untuk metrik yang sedang dibaca:

`insentif_profit|retur_persen` · `insentif_profit|roas` · `insentif_profit|roas_bersih` ·
`kinerja_live|conversion` · `kinerja_live|conversion_rate` · `kinerja_live|add_to_cart_rate` ·
`kinerja_live|avg_viewing_duration` · `kinerja_affiliate_tim|conversion` ·
`kinerja_affiliate_tim|affiliate_aktif`

⚠️ **Kedua penegak yang ditulis 2026-08-31 tidak bisa menangkap ini**, dan itu bukan
kelalaian melainkan batas rancangannya: `bedakanLabelKembar` bekerja pada **daftar opsi
pemilih sumber** (layar Atur Target), sedangkan `pasanganKhususSumber()` memeriksa **isi
kamus**. Tidak ada di antara keduanya yang melihat **titik panggil** di layar lain. Penjaga
suite karena itu tetap hijau sementara layar menerangkan metrik yang salah, persis seperti
tiga kali sebelumnya, dan lagi-lagi ketahuan dari layar.

**Aturannya**: tiap pemanggil `infoMetrik` yang **tahu** sumbernya WAJIB mengirimkannya.
Argumen opsional itu ada untuk pemanggil yang benar-benar tak punya sumbernya, bukan sebagai
kemudahan. Bila sebuah layar memegang `auto_sumber` dan `auto_metrik` berdampingan, tidak
ada alasan sah untuk mengirim salah satunya saja.

## Cara memeriksa

1. **Di layar, bukan di editor.** Buka pemilih Sumber data dan pastikan tak ada label yang terpotong dan tak ada opsi tanpa baris kedua.
2. **Dua bahasa.** Label dan keterangan wajib ada di `id.ts` DAN `en.ts` ([[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]). Istilah teknis lazim English dibiarkan English di kedua locale.
3. **Sumber baru wajib punya entri kamus**, jangan diserahkan ke perapian token. Masuk checklist [[RUN - Menambah Metrik KPI Otomatis]].
4. **Jalankan `label-otomatis.aturan.test.ts`.** Ia menjaga aturannya, bukan daftar isinya: sumber baru yang tak berlabel akan memerahkannya begitu ditambahkan ke daftar sumber produksi di berkas test itu. Daftar itu sengaja ditulis tangan, sebab daftar yang ikut berubah sendiri tak akan pernah gagal.

## Dokumen Terkait

- [[RUN - Menambah Metrik KPI Otomatis]] — prosedur menambah sumber; penamaan ini bagian dari checklist PR-nya
- [[HRIS - Matriks KPI per Departemen]] — daftar label template yang benar-benar terpasang, termasuk yang melanggar aturan ini
- [[HRIS - Otomasi Skor KPI]] — katalog sumber dan konfigurasinya
- [[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]] — layar tempat label ini dibaca
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
