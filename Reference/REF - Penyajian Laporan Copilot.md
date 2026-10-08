## Deskripsi

*Panduan cara Copilot menyajikan jawaban berangka sebagai laporan: angka utama, grafik berjudul kesimpulan, satu paragraf penjelasan per grafik, tabel lengkap, dan unduhan PDF/Excel. Ditulis supaya alat Copilot berikutnya (HR, keuangan, gudang) tampil dengan gaya yang sama tanpa membangun tampilan sendiri. Tiap aturan di sini menunjuk berkas kode yang menegakkannya; bila dokumen ini dan kode berbeda, kode yang menang.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Diukur 2026-10-08 ke `origin/main` bip-erp `ff3ea482` dan erp-frontend `a4151449c`. **Laporan penuh baru berlaku untuk dua alat**, `laba_produk` dan `laba_toko`; alat lain memakai jalur umum (§ Cakupan hari ini). Belum ada pengukuran PROD maupun uji end-to-end lewat gateway atas gelombang ini: yang terbukti kode dan test di repo.
- **Ruang lingkup**: tampilan jawaban Copilot di layar `/copilot` (`erp-frontend/src/features/copilot/`), blok yang dibangun `bip-erp/services/assistant/internal/alat/`, dan unduhan PDF/Excel-nya. Tata letak halaman dashboard lain diatur [[REF - Layout Dashboard erp-frontend]]; warna dan keputusan Recharts tetap di `.agent-kit/rules/team-memory.md` § Bagan/chart.
- **Dasar keputusan**: keputusan pemilik produk 2026-10-08 ("jangan semua dalam bentuk kalimat"; "harus bisa buat analisa data buat memudahkan pengambilan keputusan manajemen"; "menampilkan datanya jangan setengah setengah"), dikutip di kepala `bentuk_bawaan.go`, `temuan.go`, `laporan_laba.go`, dan `lib/laporan-visual.ts`.
- ⚠️ **Satu keputusan 2026-10-08 malam baru separuh sampai ke `origin/main`**: teks tak boleh dipotong dengan elipsis (§5). Bagian backend-nya (butir dan paragraf AI) merged lewat bip-erp #2829 dan diukur ulang ke `origin/main` `500ed91e`; bagian layar (nama kategori di sumbu grafik) belum. Lihat § Belum berlaku.
- **PR**: bip-erp #2789, #2822, #2827; erp-frontend #2195, #2204, #2205, #2208 (semuanya merged 2026-10-08).

## Kenapa dokumen ini ada

Diukur di PROD 2026-10-08 atas 81 giliran (kepala `bentuk_bawaan.go`): 61% blok berupa tabel dan 9 jawaban berdata keluar tanpa blok sama sekali, karena **model** yang memilih bentuk dan ia hampir selalu memilih tabel atau teks. Jawabannya benar, tetapi pembacanya masih harus menyimpulkan sendiri.

Perbaikannya bukan gaya per alat, melainkan satu jalur yang dilewati **setiap** alat (`jawab.go` memanggil `alat.PutuskanBentuk` sebelum dan `Selesaikan` sesudah tiap alat). Karena itu alat baru tidak boleh merakit tampilannya sendiri: yang ia sediakan adalah data yang berbentuk benar, sisanya dikerjakan jalur itu.

## Cakupan hari ini

| Yang didapat | `laba_produk`, `laba_toko` (laporan penuh) | Alat lain (jalur umum) |
|---|---|---|
| Bentuk dipilih sistem | ya, selalu laporan berblok | ya (`PutuskanBentuk`, `Selesaikan`) |
| Kartu angka utama + perubahan periode | ya (`blokAngkaUtama`) | hanya alat yang memang membangun blok kartu sendiri; tanpa pembanding dari jalur umum |
| Temuan | dihitung alat dari data lengkap, dibagi per bagian (`alatBertemuanSendiri`) | `konsentrasi`, `negatif`, `di_bawah_target` pada blok utama saja (`temuanUmumBlok`) |
| Pembanding periode | ya (`periodePembanding`) | tidak ada |
| Grafik urai, selisih, sebaran | ya, bersyarat | tidak ada |
| Batang gabungan "N lainnya" | ya (`lainnyaBatang`) | hanya bila sisanya bisa dijumlah tanpa menebak (`isiLainnyaUmum`) |
| Tabel lengkap + baris total | ya (`RincianBlok.Jumlah`) | tabel lengkap ya (`denganRincian`), baris total **tidak** |
| Sorotan batang dan garis target | ya | ya (`isiSorot`) |
| Paragraf penjelasan per grafik | ya | ya, untuk setiap blok grafik (`alamat_blok.go`) |
| Dugaan & saran AI | ya | ya |
| PDF dan Excel | ya | ya |

## Aturan penyajian

### 1. Halaman dibuka angka utama dengan perubahannya

Pembaca menangkap besarannya dulu, baru rinciannya. Laporan laba dibuka blok `kartu` berbagian `angka_utama`: omzet, laba kotor, margin, unit terjual, dihitung dari **seluruh** baris sumber (`laporan_laba.go` `blokAngkaUtama`).

- **Perubahan dibandingkan dengan periode yang setara** (`temuan.go` `periodePembanding`): bulan yang sudah lewat lawan bulan sebelumnya utuh; **bulan berjalan lawan tanggal yang sama bulan lalu** (tanggal 1 sampai kemarin lawan tanggal 1 sampai tanggal itu bulan lalu, dipotong akhir bulan); rentang `dari..sampai` lawan rentang sama panjang tepat sebelumnya; tanpa rentang memakai jendela bawaan sumber (30 hari) lawan jendela sebelumnya. Alasannya tertulis di kode: separuh bulan lawan sebulan penuh selalu terbaca "turun".
- **Margin berubah dalam poin, bukan persen** (`KartuAngka.PerubahanPoin`; layar `lib/laporan-visual.ts` `perubahanKartu`). Margin 21,1% dari 29,8% ditulis "-8,7 poin": persen dari persen menyesatkan.
- **Tak ada pembanding yang jujur = tak ada panah.** Tanggal 1 bulan berjalan, bulan depan, daftar yang mentok limit sumber, cakupan channel yang berbeda antar-periode, atau panggilan pembanding yang gagal membuat angka pembanding **tidak dikirim** (`pembandingSah`); laporannya tetap jadi.
- Persen perubahan `null` bila basisnya nol atau negatif (`perubahanPersen`).
- ⚠️ Pada bulan berjalan angka kartu sudah memuat hari ini, sedangkan persen perubahannya membandingkan tanggal 1 sampai kemarin; rentang yang dibandingkan ada di `Blok.Pembanding` (komentar `blokAngkaUtama`).
- Penanda "Perlu diperiksa" pindah ke bawah kartu angka utama bila jawabannya dibuka kartu itu (`adaAngkaUtama`).

### 2. Judul grafik adalah kesimpulan

Judul "Laba kotor per produk" menyuruh pembaca mencari sendiri isinya; judul "2 produk teratas menyumbang 32,8% laba kotor" sudah menyampaikannya. Judul bagian diambil dari **temuan pertama** blok itu yang bisa dirakit (`lib/laporan-visual.ts` `judulKesimpulan`, kalimatnya di `lib/temuan.ts` `judulTemuan`), dan di bawahnya satu baris keterangan kecil menyebut apa yang digambar dan satuannya (`keteranganBlok`).

- Blok tanpa temuan yang bisa dirakit memakai judul lama (`copilot.tampilan.bagian.<bagian>` atau `copilot.tampilan.judul.<alat>`), tanpa baris keterangan.
- Temuan yang sudah menjadi judul dan paragraf grafik **tidak diulang** di daftar "Temuan utama" (`lib/susunan-blok.ts` `temuanTanpaGrafik`); daftar itu tinggal untuk temuan blok kartu atau tabel.
- Kalimat temuan milik layar (`copilot.temuan.<kode>`, [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]); server hanya mengirim kode dan angka. Kode yang belum dikenal layar dilewati, tidak ditampilkan mentah (`KODE_TEMUAN`).

### 3. Bentuk grafik mengikuti jenis temuannya, dan SISTEM yang memilih

Bentuk yang salah membuat temuan yang benar tak terbaca, dan model terbukti tidak memilihnya dengan baik. Semua aturan bentuk ada di satu berkas, `bentuk_bawaan.go`:

1. Model meminta bentuk grafik yang sah untuk alat itu: dihormati.
2. Model mengisi `teks`, `tabel`, atau mengosongkan: sistem mengganti argumennya dengan bentuk bawaan alat (`aturanBentukAlat`; alat lain: tabel).
3. Tabel tak pernah hilang: blok grafik membawa tabel lengkapnya di `Blok.Rincian` bila barisnya bukan seluruh tabel.
4. Sesudah alat berjalan: batang pilihan sistem dengan kurang dari 2 batang turun jadi tabel; tabel alat tanpa aturan khusus naik jadi batang **hanya** bila bentuknya tak menyisakan tebakan (`grafikDariTabel`: tabel utuh, 2 sampai 15 baris, tepat satu kolom angka yang kuncinya sebuah ukuran, satu kolom teks unik); blok tabel satu baris yang tak diminta model dibuang karena hanya mengulang kalimat.

Prompt aturan 7 (`tanya.go`) menyuruh model mengosongkan argumen `tampilan` kecuali penanya meminta bentuk tertentu.

**Pertanyaan atau temuan menentukan jenis blok:**

| Pertanyaan yang dijawab | Kode temuan | Jenis blok | Bagian laporan laba |
|---|---|---|---|
| Berapa totalnya, berubah berapa | `perubahan` (menempel di kartu bila selisihnya tak bisa diurai) | `kartu` | `angka_utama` |
| Siapa terbesar, seberapa terkonsentrasi, adakah yang rugi | `konsentrasi`, `negatif` | `grafik` (batang peringkat + "N lainnya") | `peringkat` |
| Kenapa totalnya berubah | `perubahan`, `urai_perubahan` | `urai` (efek omzet dan efek margin pada satu skala) | `urai_selisih` |
| Siapa yang menyebabkan perubahan | `penyumbang_turun`, `penyumbang_naik` | `selisih` (batang dua arah dari garis nol) | `penyumbang` |
| Siapa yang besar tetapi rasionya ganjil | `rasio_terendah`, `rasio_tertinggi` | `sebaran` (ukuran lawan rasio, garis rasio gabungan) | `omzet_margin` |
| Berapa yang di bawah target | `di_bawah_target` | `grafik` batang dengan garis target | jalur umum (mis. `iklan`) |

**Bentuk data menentukan jenis blok lain** (pembangunnya di `grafik_jenis.go` dan `tren.go`; data yang tak memenuhi syarat menghasilkan `nil` dan alat jatuh ke bentuk sebelumnya, terakhir tabel):

| Jenis | Syarat data | Pemakai di kode |
|---|---|---|
| `tren` | deret per `YYYY-MM`, kurang dari 36 bulan; proyeksi berupa estimasi | `turnover_karyawan`, `kpi_ringkasan_departemen` |
| `area` | deret volume harian atau bulanan, 1 sampai 2 seri, nilai tak negatif, maks 92 hari atau 36 bulan | `live` |
| `donat` | komposisi utuh, 2 sampai 6 bagian, nilai tak negatif | `ringkasan_marketing`, `komposisi_karyawan` |
| `komposisi` | porsi bagian terhadap keseluruhan; bentuk jatuhan donat | sama |
| `radar` | 3 sampai 8 metrik berskala sama, 1 sampai 3 subjek | `kpi_rincian_karyawan` |
| `radial` | 1 sampai 4 angka terhadap target **kiriman sumber** | `anggaran_mingguan` |
| `tabel` | selain itu | semua alat berdata baris |

Alat yang punya bentuk bawaan selain tabel hari ini (`aturanBentukAlat`): `laba_toko`, `laba_produk`, `iklan`, `rekap_telat_tim`, `retur`, `ringkasan_marketing`, `kpi_ringkasan_departemen`, `affiliate_video` (batang) dan `live` (area). Garis tren berproyeksi sengaja **tidak** dijadikan bawaan: perkiraan hanya tampil bila diminta.

- Jenis blok baru hanya boleh lahir lewat pembangunnya (`blokArea`, `blokDonat`, `blokRadar`, `blokRadial`, `blokTren`, `blokUraiSelisih`, `blokPenyumbang`, `blokSebaranOmzetMargin`); alat tidak merakitnya sendiri.
- Target dan ambang hanya dari sumber (`Blok.Target`), tak pernah dikarang. Satu pengecualian yang dinyatakan lewat labelnya: `margin_gabungan` di blok sebaran, rasio yang dihitung ulang dari total baris alat itu sendiri.
- **TBD**: kapan persisnya `radar`, `radial`, `donat`, dan `tren` muncul untuk tiap alat di luar `aturanBentukAlat` (bawaan atau hanya saat model memintanya) tidak diperiksa satu per satu oleh dokumen ini.

### 4. Tiap grafik diikuti SATU paragraf teks polos selebar grafiknya

Grafik menunjukkan bentuk, paragraf mengatakan artinya bagi keputusan. Satu paragraf, tanpa kotak dan tanpa label, selebar grafik di atasnya (grafik selebar halaman: paragraf selebar halaman; dua grafik berdampingan: masing-masing selebar kolomnya), di layar dan di PDF.

- **Sumbernya** (`lib/laporan-visual.ts` `paragrafBlok`): `Blok.Penjelasan` bila ada, yaitu paragraf yang **ditulis model**; kalau kosong, kalimat temuan blok itu dirangkai jadi satu paragraf; kalau temuan pun kosong, tanpa paragraf.
- **Cara model menulisnya** (`penjelasan.go`, prompt aturan 14): tanpa putaran tambahan, model menutup jawaban dengan baris `PENJELASAN <alamat>: <paragraf>`; server mencabut baris itu dari jawaban dan menempelkannya ke blok beralamat itu. Alamatnya `<alat>.<bagian>` (blok tanpa bagian: `<alat>`), **disalin model dari hasil alat** (`tampilan.penjelasan_untuk`), tak pernah dikarang; satu-satunya tempat bentuknya diputuskan `alamat_blok.go`. Hanya blok grafik yang beralamat: tabel, kartu, dan radial tidak.
- **Batas**: paling banyak 6 paragraf per jawaban; prompt meminta 2 sampai 4 kalimat, paling panjang 400 karakter per paragraf (`maksBarisPenjelasan`, prompt aturan 14); alamat tak dikenal atau ambigu dibuang, tak pernah ditebak (`CocokkanAlamat`). Paragraf yang melampaui batas pengaman 700 karakter dipotong di akhir kalimat atau dibuang, tak pernah di tengah kalimat (§5).
- **Penjaga angka**: penjaga jawaban (angka rupiah terhadap hasil alat, token samaran yang disingkat, klaim akses) berjalan atas teks lengkap lebih dulu dengan satu jatah koreksi bersama, lalu **tiap paragraf diperiksa sendiri**; yang melanggar dibuang itu saja dan layar jatuh ke kalimat temuan (`jawab.go`, `pasangPenjelasan`).
- **Keterangan "ditulis AI"**: bila ada minimal satu paragraf AI yang tampil, kaki jawaban memuat satu kalimat `copilot.laporan.catatanAi` ("Paragraf penjelasan ditulis AI dari angka di laporan ini.") di bawah daftar sumber (`adaParagrafAi`, `panel-tanya.tsx`); PDF menulisnya di baris sumber.

### 5. Data tidak dipotong

Prinsip induknya, dalam kata pemilik produk: **"menampilkan datanya jangan setengah setengah"**. Yang dilarang adalah menampilkan sebagian lalu menyuruh pembaca mencari sisanya di tempat lain. Empat aturan turunannya, masing-masing dengan status penerapannya:

- ✅ **Tabel memuat semua baris.** Bagian "Rincian" laporan menampilkan seluruh baris yang dikirim server, dengan baris total di dasarnya, tanpa "tampilkan semua" dan tanpa tinggi maksimum (`blok-tampilan.tsx` `RincianLengkap`, isi dari `tabelRincian`). Ia tertutup saat pertama tampil; saat dibuka semua baris ada. Di PDF selalu dicetak penuh. Baris total hanya memuat kolom yang sah dijumlah ditambah rasio yang dihitung ulang dari total (`RincianBlok.Jumlah`); kolom yang memuat nilai tak diketahui bertotal `null` dan tampil sebagai tanda strip, bukan 0.
- ✅ **Grafik peringkat menggambar batang teratas dan menggabungkan sisanya jadi satu batang "N lainnya"** (`Blok.Lainnya`; label `copilot.laporan.lainnya`, mis. "27 produk lainnya"), supaya porsinya tetap berjumlah 100%. Batang gabungan sah karena grafik itu ringkasan dan rincian lengkapnya ada di halaman yang sama (tabel "Rincian" di bawahnya). Batang teratas: 10 di laporan laba (`BatasPeringkat`), 15 di jalur umum (`BatasGrafik`). Nilai gabungan = total seluruh baris dikurangi batang yang digambar, boleh negatif (`lainnyaBatang`); bila ada satu saja nilai tak diketahui, nilainya `null` dan batangnya **tidak digambar**, dan layar mengatakannya terus terang (`lainnyaTakDiketahui`), tidak menggantinya nol. Keputusan ini sempat dibatalkan lalu ditegaskan kembali pemilik produk pada 2026-10-08 malam: yang dikeluhkan ternyata bagian ringkasannya saja.
- ✅ **Kalimat "Menampilkan X dari Y, lengkapnya di Excel" dilarang** untuk grafik laporan: keterangan sebagian hanya ditulis bila sisanya benar-benar tak tampil di mana pun (`perluCatatanSebagian`). Di jalur umum kalimat itu masih bisa muncul (§ Belum berlaku).
- 🟡 **Teks tidak dipotong dengan elipsis.** Keputusan yang sama: nama kategori di grafik dibungkus ke baris berikutnya, dan butir atau paragraf AI yang kelewat panjang dipotong di **akhir kalimat** (tak pernah di tengah kalimat) atau dibuang. **Bagian backend sudah di `origin/main`** (bip-erp #2829, merged 2026-10-08, diukur ke `500ed91e`): prompt tetap meminta butir 200 dan paragraf 400 karakter, dan server hanya memasang batas pengaman butir 400 dan paragraf 700 karakter (`maksRuneButirAnalisa`, `maksRunePenjelasan`); yang melampauinya dipotong di akhir kalimat terakhir yang masih muat, tanpa elipsis, dan bila tak ada kalimat utuh yang muat butir atau paragraf itu dibuang (`potongDiKalimat` di `analisa_ai.go`). Berlaku sesudah `assistant-service` di-deploy. **Bagian layar belum di `origin/main`**: label kategori di sumbu grafik masih dipotong elipsis selebar sumbunya (`grafik-jenis.tsx`); pembungkusannya sedang dikerjakan.

**Batas yang benar-benar ada di kode `origin/main`**, disebut apa adanya:

| Batas | Nilai | Berkas | Yang terjadi saat terlampaui |
|---|---|---|---|
| Batang peringkat laporan laba | 10 | `laporan_laba.go` `BatasPeringkat` | sisanya jadi "N lainnya"; tabel rinciannya tetap lengkap |
| Batang grafik jalur umum | 15 | `tampilan.go` `BatasGrafik` | "N lainnya" bila kolomnya aditif, tabel lengkapnya utuh, dan tak ada `null`; selain itu grafik dipotong dan keterangan sebagian **masih ditulis** |
| Baris tabel rincian ke layar | 500 | `laporan_laba.go` `BatasRincianLaporan` | `total` tetap menyebut jumlah asli, sumber ditandai sebagian, PDF dan Excel menulis catatan terpotong |
| Limit endpoint sumber laba | 5.000 baris bulanan | `mkt_labaproduk.go`, `mkt_labatoko.go` | daftar dianggap tak lengkap: tanpa pembanding, tanpa temuan atas seluruh populasi, model diberi peringatan, sumber ditandai sebagian |
| Baris yang dikirim ke model | 20 | `labaProdukBatasModel`, `labaTokoBatasModel` | hanya untuk model; blok penanya tetap seluruh baris, dan total seluruh baris dikirim ke model di kunci `angka_utama` supaya ia tak menjumlah sendiri |
| Titik sebaran | 60 (omzet terbesar), minimal 6 | `laporan_laba.go` | `total` menyebut seluruh titik; kurang dari 6 = blok tak dikirim |
| Baris blok penyumbang | 5 perubahan terbesar | `laporan_laba.go` | `total` = seluruh baris yang berubah; tabel lengkapnya di rincian peringkat |
| Temuan per blok | 4 | `temuan.go` `maksTemuan` | dibuang dari belakang urutan prioritas |
| Tabel biasa di layar | diringkas 10 baris | `blok-tampilan.tsx` `BATAS_BARIS_RINGKAS` | tombol "Tampilkan semua"; ini lipatan, bukan pemotongan |

Blok bersyarat yang syaratnya tak terpenuhi **tidak dikirim** (tak ada blok kosong), dan deret kosong tidak digambar.

### 6. Disiplin warna: satu aksen, netral, merah hanya untuk yang buruk

Sepuluh batang hijau sama-sama berteriak; satu aksen menunjuk tepat ke yang dimaksud judulnya. Aturannya (`lib/laporan-visual.ts` `nadaPeringkat`, `lib/sorot-blok.ts` `nadaBatang`, `grafik-laporan.tsx`):

- Yang ditonjolkan (baris bersorot server, ditambah n batang teratas temuan `konsentrasi`) berwarna aksen; sisanya netral; **merah hanya untuk yang rugi atau buruk**, hijau untuk yang baik. Baris yang sama ditebalkan di tabel rincian (`indeksDisorot`).
- Penilaian menang atas aksen: batang tertinggi yang masih di bawah target tetap ditandai buruk.
- Identitas dan arah **tak pernah warna saja**: arah ditulis dengan kata ("Karena omzet turun"), tanda di angka ("−121 jt"), baris keterangan dan legend berteks, dan temuan memakai bentuk ikon berbeda per arah (`temuan-analisa.tsx`).
- ⛔ **Tidak ada komponen atau warna khusus Copilot.** Semua grafik memakai `ChartContainer` (`components/ui/chart.tsx`) dan token yang sudah ada: `WARNA_BAGAN` dan `WARNA_AMBANG` (`features/hris/dashboard/kartu/bagan/warna.ts`), `--fb-seri-*` lewat `warnaTim()`, serta token teks tema. Warna ditulis `theme: {light, dark}` supaya ikut mode gelap. Alasan dan larangannya di `.agent-kit/rules/team-memory.md` § Bagan/chart dan `.agent-kit/rules/ui-checklist.md`.
- Semua keputusan (judul, paragraf, skala sumbu, letak label, warna) ada di fungsi murni `lib/*.ts`, bukan di komponen: recharts dipalsukan di uji repo ini, jadi uji render tak membuktikan apa pun.

### 7. Tiga lapis kebenaran

Pembaca harus bisa membedakan yang dihitung dari yang ditulis. Tiga lapis, tak pernah dicampur:

| Lapis | Siapa yang membuat | Tampil sebagai | Penjaganya |
|---|---|---|---|
| Angka, tabel, grafik | sistem, dari balasan endpoint | blok | aturan kolom di tiap alat; `null` = tidak diketahui, tak pernah 0 |
| **Temuan** | sistem, fungsi murni di `temuan.go` | judul kesimpulan, kalimat temuan, daftar "Temuan utama" | hanya dari nilai yang sudah ada; angka baru terbatas pada jumlah, porsi, selisih, median; populasi terpotong = tanpa temuan |
| **Paragraf penjelasan** dan **Dugaan & saran AI** | model | paragraf di bawah grafik (dengan keterangan "ditulis AI" di kaki); kotak berbingkai putus-putus berlabel "Dibuat AI, bukan fakta. Periksa sebelum dipakai." | penjaga jawaban yang sama (`penjaga.go`); paragraf yang melanggar dibuang sendiri, butir analisa yang melanggar membuang seluruh `analisa_ai`; jawabannya tetap |

- Model menerima temuan di hasil alat (kunci `temuan`) dan dilarang bertentangan dengannya atau menambah perbandingan periode yang tak ada di temuan (prompt aturan 7).
- Dugaan & saran (`analisa_ai.go`, prompt aturan 13): paling banyak 2 dugaan dan 2 saran, prompt meminta paling panjang 200 karakter per butir (batas pengaman server 400, dipotong di akhir kalimat atau dibuang, §5), hanya untuk pertanyaan analitis atau bila ada temuan `perubahan` atau `negatif`. Dugaan harus bisa diperiksa dan menyebut angka dari alat; sebab yang tak ada datanya (kompetitor, musim, cuaca) hanya boleh ditulis sebagai hal yang perlu dicek.
- ⛔ **Saran tidak pernah menyangkut tindakan terhadap orang**: tak ada saran sanksi, penilaian kinerja, atau tindakan terhadap karyawan tertentu, juga di paragraf penjelasan (prompt aturan 13 dan 14). Copilot bukan alat penilaian kinerja.
- Paragraf dan butir analisa ikut ditutup bagi peninjau rekap umpan bila jawabannya tertutup (`umpan_rekap_rute.go`), dan versi samarannya disimpan untuk dikirim ulang ke model saat percakapan dilanjutkan.

### 8. PDF

PDF adalah laporan perusahaan, bukan tangkapan layar obrolan (`lib/laporan-pdf.ts`):

- **Kop resmi selebar bidang isi** di tiap halaman, dari **satu sumber**: `src/lib/kop-bharata.ts` (`KOP_BHARATA_SRC`, `NAMA_PERUSAHAAN_BHARATA`), yang juga dipakai `KopSurat` dokumen cetak lain. Kop yang lebih sempit dari isinya terbaca seperti stempel di pojok. Mengganti kop cukup mengganti gambar itu.
- **Judul = pertanyaan penanya** (diringkas), juga nama berkasnya. **Kalimat jawaban model tidak dicetak** sama sekali; begitu pula nama pencetak dan penanda `penilaian` (kalimat bebas model).
- Urutan cetak: judul dan periode, penanda data yang perlu diperiksa, angka utama, temuan utama, grafik berikut legend dan paragrafnya, tabel rinci, Dugaan & saran AI (berbingkai, berlabel bukan fakta), lalu sumber data.
- **Grafik vektor**: SVG layar disalin dengan gaya terhitungnya lalu digambar lewat `svg2pdf.js` (`lib/tangkap-grafik.ts`), selalu tema terang. Grafik selebar wadah dirender ulang di luar layar selebar kertas supaya hurufnya tidak mengecil (`components/grafik-cetak.tsx`, `lib/mode-cetak.ts`). Grafik yang gagal ditangkap dilewati; tabel angkanya tetap tercetak.
- **Tabel penuh berkepala ulang**: semua baris dicetak, kepala tabel diulang di tiap halaman, satu baris tak pernah terbelah; kolom rupiah ditulis dalam juta bila semua nilainya minimal sejuta (kepala kolom berakhiran "(jt)", `kolomJuta`); baris total dan baris bersorot tebal.
- Satu bagian (judul, grafik, legend, paragraf) pindah halaman utuh, tak pernah terbelah; penguraian selisih dan penyumbangnya dicetak berdampingan seperti di layar lebar.
- Aturan layar dipakai apa adanya, tidak disalin: susunan dari `lib/susunan-blok.ts`, warna dan sorotan dari `lib/sorot-blok.ts`, format angka dari `lib/format-blok.ts`. PDF karena itu tak bisa mencetak angka yang berbeda dari layar.

### 9. Excel

Excel adalah berkas data (`lib/laporan-excel.ts`): sel angka ditulis sebagai angka penuh (bukan juta, bukan teks), sel `null` tetap kosong, temuan utama mendapat sheet sendiri dengan kalimat yang sama, dan teks model (jawaban, Dugaan & saran AI) tidak ditulis. Yang belum ada dicatat di § Belum berlaku.

## Daftar periksa: menambah alat baru ke Copilot

**Didapat otomatis lewat jalur umum**, asal alat memakai argumen `tampilan` berenum (`skemaTampilan`) dan mengembalikan `*Blok` dari data sumbernya:

- bentuk dipilih sistem, sorotan batang, dan garis target bila sumber mengirim target;
- tabel lengkap di balik "Lihat data" (`Blok.Rincian`), batang "N lainnya" bila sisanya bisa dijumlah;
- temuan `konsentrasi`, `negatif`, `di_bawah_target` pada blok utama, berikut judul kesimpulannya;
- alamat penjelasan untuk tiap blok grafik, jadi paragraf AI dan penjaganya;
- Dugaan & saran AI, keterangan sumber, samaran identitas, unduhan PDF dan Excel.

**Yang harus disediakan alat supaya mendapat lebih dari itu:**

1. **Kunci kolom yang bisa dibaca jalur umum.** Jalur umum memutuskan dari nama kunci: kolom ukuran berawalan `jumlah`, `total`, `nilai`, `skor`, `omzet`, `laba`, `biaya`, dan seterusnya (`awalanUkuran`); kolom yang sah dijumlah memakai daftar-izin `awalanAditif`, dan kunci yang memuat `persen`, `rata`, `roas`, `rasio`, `margin`, `skor` tidak pernah dijumlah. Kolom rasio jangan diberi awalan aditif.
2. **Tabel lengkap, bukan potongan.** Bangun grafik lewat `denganRincian(grafik, tabel)`; alat yang masuk `aturanBentukAlat` wajib lolos `TestBentukBawaan_AlatBeraturanMembawaSeluruhBaris`.
3. **`null` untuk yang tidak diketahui**, bukan 0, sampai ke total.
4. **Target hanya dari sumber**, dengan `TargetKolom` dan `TargetLabel` (kunci label, bukan teks).
5. **Label layar di dua bahasa** (`id.ts` dan `en.ts`): `copilot.tampilan.judul.<alat>`, `copilot.tampilan.bagian.<bagian>`, `copilot.tampilan.kolom.<kunci>`, `copilot.panel.namaSumber.<alat>`. Kolom rupiah baru didaftarkan di `KOLOM_RUPIAH` (`lib/temuan.ts`), kalau tidak ia tampil tanpa "Rp" dan tanpa diringkas.
6. **Untuk temuan dengan pembanding periode**: alat mendaftar di `alatBertemuanSendiri`, menghitung dari data lengkapnya, dan mengambil pembanding lewat panggilan kedua ke endpoint yang sama dengan JWT penanya (hak akses tetap diputuskan sumber); kegagalan pembanding tidak boleh menggagalkan jawaban.
7. **Kode temuan baru** menuntut tiga tempat sekaligus: `temuan.go`, `KODE_TEMUAN` di `lib/temuan.ts`, dan kalimat serta judulnya di kedua locale. Tanpa yang kedua dan ketiga, butirnya dilewati layar tanpa galat.
8. **Jenis blok baru** lahir lewat satu pembangun di backend dan satu komponen di `features/copilot/components/` yang dirakit dari `ChartContainer` dan token yang ada, dengan keputusannya di fungsi murni `lib/`.
9. **Data per orang**: nama lewat samaran, tak ada saran atas orang, dan alat berisi uang perusahaan atau data pribadi masuk `alatJawabanTertutup` (`umpan_rekap_rute.go`).

⚠️ **Laporan berblok penuh belum punya perakit umum.** `susunLaporanLaba` dan `uraiTemuanLaba` berbicara dalam kolom laba (`omzet`, `laba_kotor`, `margin_persen`, `unit_terjual`), jadi alat HR, keuangan, atau gudang belum bisa mendapat angka utama, urai, penyumbang, dan sebaran hanya dengan mendaftar. Mengangkatnya jadi perakit umum adalah keputusan tersendiri (**TBD**), sejalan dengan prinsip tim menunggu pemakai ketiga sebelum mengangkat abstraksi.

## Belum berlaku / Catatan

- 🟡 **Nama kategori di sumbu grafik masih dipotong elipsis** di `origin/main` erp-frontend (pembungkusan ke baris berikutnya sedang dikerjakan): keputusan 2026-10-08 malam, rinciannya di §5. Bagian backend keputusan yang sama (butir dan paragraf AI) sudah merged lewat bip-erp #2829 dan menunggu deploy `assistant-service`.
- **Excel belum memuat paragraf penjelasan dan baris total.** `laporan-excel.ts` tidak membaca `Blok.penjelasan` maupun `rincian.jumlah` (`git grep` atas `origin/main` 2026-10-08: nol hasil untuk keduanya di berkas itu); sheet rincian memuat semua baris tanpa baris total.
- **Kalimat "menampilkan N dari M" masih bisa muncul di jalur umum**: grafik batang yang dipotong 15 dan sisanya tak bisa dijumlah (kolom rasio, ada `null`, atau tabel lengkapnya sendiri terpotong), blok komposisi yang dipotong, dan tabel yang dipotong server.
- **Ambang jumlah titik sebaran ada di dua tempat dengan nilai berbeda**: backend mengirim blok bila minimal 6 titik (`minTitikSebaran`), layar menggambar bila minimal 3 (`MIN_TITIK_SEBARAN`). Tidak bertabrakan hari ini karena yang lebih ketat ada di hulu, tetapi itu dua angka untuk satu fakta.
- **Aturan Jadwal Tugas, jempol, dan riwayat** tidak diatur di sini; lihat [[Microservices - Assistant Service]].
- **TBD**: pengukuran PROD sesudah gelombang ini (porsi blok tabel lawan grafik, seberapa sering paragraf AI dibuang penjaga) belum ada; angka 61% di atas adalah keadaan **sebelum** perubahan.
- **TBD**: perilaku tampilan di layar sempit (ponsel) tidak diukur dokumen ini; yang terbaca dari kode hanya bahwa pasangan urai dan selisih menumpuk di layar sempit.

## Penjaga di kode

| Yang dijaga | Test |
|---|---|
| Alat berbentuk bawaan membawa seluruh baris | `bentuk_bawaan_test.go` `TestBentukBawaan_AlatBeraturanMembawaSeluruhBaris` |
| Urutan blok laporan, angka utama, peringkat dan "lainnya", urai, penyumbang, sebaran | `laporan_laba_test.go` `TestLaporanLaba_*`, `TestLainnyaBatang`, `TestIsiLainnyaUmum` |
| Urutan dan batas empat temuan | `temuan_test.go` `TestBatasiTemuan_UrutanDanEmpatButir` |
| Paragraf menempel di blok yang benar, paragraf salah dibuang, ikut ditutup di rekap | `penjelasan_test.go` |
| Judul kesimpulan, paragraf, batang gabungan, skala, letak label (fungsi murni layar) | `lib/laporan-visual.test.ts` |
| Swatch legend setara token warna di kedua tema | `blok-tampilan.test.tsx` |

## Dokumen Terkait

- [[Microservices - Assistant Service]], kontrak blok, alat, penjaga, dan Jadwal Tugas
- [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]], §4 (tak pernah menghitung dari data mentah) dan §7 (keluaran terstruktur dari komponen yang sudah ada)
- [[REF - Layout Dashboard erp-frontend]], komposisi halaman berangka di luar Copilot
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]], kalimat dan label milik layar
- [[Microservices - Marketing Analytics Service]], sumber angka dan aturan pemakaian kolom laba
- [[APP - Web ERP]], tempat layar Copilot berdiri
- `.agent-kit/rules/ui-checklist.md` dan `.agent-kit/rules/team-memory.md` § Bagan/chart, aturan komponen dan warna yang dipakai di sini
