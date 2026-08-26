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

## Mengganti label yang sudah dipakai

**Metrik template aman diganti namanya** sejak tiap metrik punya `key` yang stabil: `IsiKunciMetrik` mempertahankan kunci yang sudah ada, jadi konfigurasi otomatis tidak lepas saat label dibetulkan. Sebelum ada `key`, backend memasangkan konfigurasi lewat label, dan memperbaiki typo berarti menghapus konfigurasinya tanpa pesan.

⚠️ **Yang TIDAK aman adalah mengganti token sumber/metrik katalog** (`kinerja_toko`, `retur_persen`). Token itu tersimpan di `auto.sumber`/`auto.metrik` tiap template, dan menggantinya membuat metrik yang sudah dikonfigurasi gagal hitung dengan pesan "sumber tidak terdaftar". Yang boleh diganti adalah LABELNYA, bukan tokennya.

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
