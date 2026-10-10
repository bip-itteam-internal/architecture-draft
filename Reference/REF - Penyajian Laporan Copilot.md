## Deskripsi

*Panduan cara Copilot menyajikan jawaban berangka sebagai laporan: angka utama, grafik berjudul kesimpulan, satu paragraf penjelasan per grafik, tabel lengkap, dan unduhan PDF/Excel. Ditulis supaya alat Copilot berikutnya (HR, keuangan, gudang) tampil dengan gaya yang sama tanpa membangun tampilan sendiri. Tiap aturan di sini menunjuk berkas kode yang menegakkannya; bila dokumen ini dan kode berbeda, kode yang menang.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Diukur 2026-10-08 ke `origin/main` bip-erp `ff3ea482` dan erp-frontend `a4151449c`. **Laporan penuh baru berlaku untuk dua alat**, `laba_produk` dan `laba_toko`; alat lain memakai jalur umum (§ Cakupan hari ini). Belum ada pengukuran PROD maupun uji end-to-end lewat gateway atas gelombang ini: yang terbukti kode dan test di repo.
- **Ruang lingkup**: tampilan jawaban Copilot di layar `/copilot` (`erp-frontend/src/features/copilot/`), blok yang dibangun `bip-erp/services/assistant/internal/alat/`, dan unduhan PDF/Excel-nya. Tata letak halaman dashboard lain diatur [[REF - Layout Dashboard erp-frontend]]; warna dan keputusan Recharts tetap di `.agent-kit/rules/team-memory.md` § Bagan/chart.
- **Dasar keputusan**: keputusan pemilik produk 2026-10-08 ("jangan semua dalam bentuk kalimat"; "harus bisa buat analisa data buat memudahkan pengambilan keputusan manajemen"; "menampilkan datanya jangan setengah setengah"), dikutip di kepala `bentuk_bawaan.go`, `temuan.go`, `laporan_laba.go`, dan `lib/laporan-visual.ts`.
- **Sinkron 2026-10-09** (diukur ke `origin/main` bip-erp `8a1f9905` dan erp-frontend `0c96129b0`): keputusan "teks tak boleh dipotong dengan elipsis" kini di `main` untuk backend (bip-erp #2829) dan untuk label grafik batang (erp-frontend #2210); sisanya di §5. Ditambah satu aturan baru (§10 model tidak menyaring, menghitung, atau mengetik tabel), bagian § Jalur tanpa mengetik, dan pengecualian latar di §6. Bagian lain dokumen ini tetap hasil ukur 2026-10-08 dan tidak dibaca ulang seluruhnya.
- **Sinkron 2026-10-10** (diukur ke `origin/main` bip-erp `9dcd3d4a` dan erp-frontend `e4d020d5a`): urutan baca 3-30-3 dengan pita "belum final" dan kolom andal (§11), kepala kelompok bila alat yang sama dipanggil lebih dari sekali (§12), tautan halaman dengan hak klik (§13), label jujur untuk cek silang (§14), dan jebakan tata letak area gulir (§15). Kontrak sisi backend ada di [[Microservices - Assistant Service]] § Gelombang 2026-10-10. Bagian lain dokumen ini tetap hasil ukur 2026-10-08 dan 2026-10-09. ⚠️ Belum ada pengukuran PROD atas gelombang ini.
- **PR**: bip-erp #2789, #2822, #2827, #2829, #2863, #2870; erp-frontend #2195, #2204, #2205, #2208, #2210, #2213, #2227, #2228, #2229, #2236 (merged 2026-10-08 dan 2026-10-09). Gelombang 2026-10-10: bip-erp #2906, #2907, #2910, #2913, #2914, #2916, #2917, #2918, #2919, #2922, #2928, #2929; erp-frontend #2267, #2268, #2271, #2272, #2273, #2274, #2275, #2276, #2277, #2280, #2282, #2284.

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
- ⚠️ **Teks tidak dipotong dengan elipsis.** Keputusan yang sama: nama kategori di grafik dibungkus ke baris berikutnya, dan butir atau paragraf AI yang kelewat panjang dipotong di **akhir kalimat** (tak pernah di tengah kalimat) atau dibuang. **Bagian backend sudah di `origin/main`** (bip-erp #2829, merged 2026-10-08, diukur ke `500ed91e`): prompt tetap meminta butir 200 dan paragraf 400 karakter, dan server hanya memasang batas pengaman butir 400 dan paragraf 700 karakter (`maksRuneButirAnalisa`, `maksRunePenjelasan`); yang melampauinya dipotong di akhir kalimat terakhir yang masih muat, tanpa elipsis, dan bila tak ada kalimat utuh yang muat butir atau paragraf itu dibuang (`potongDiKalimat` di `analisa_ai.go`). Berlaku sesudah `assistant-service` di-deploy. **Bagian layar sudah di `origin/main` untuk grafik batang** (erp-frontend #2210, diukur ke `0c96129b0`): nama kategori dibungkus ke baris berikutnya selebar kolomnya, dipecah di spasi (kata tunggal yang lebih lebar dari kolom dipecah per huruf), tanpa membuang satu huruf pun (`bungkusLabel` di `lib/visual-blok.ts`); lebar kolom dan tinggi baris menyesuaikan (`lebarKolomLabel`, `tinggiBarisLabel`), dan kalimat komponen di grafik urai ikut dibungkus di wadah sempit (`tataUrai`). **Yang masih memakai pemotong lama** (dibaca di `grafik-jenis.tsx`): legend donat (kelas `truncate`, nama lengkap di `title`) dan label nama metrik di sumbu radar (elipsis selebar ruang label, nama lengkap di `<title>`). Di luar grafik, usulan nama jadwal dari pertanyaan masih dipotong di batas kata dengan elipsis (`namaDariPertanyaan` di `lib/jadwal.ts`; hanya usulan yang bisa disunting di form).

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

- Yang ditonjolkan berwarna aksen; sisanya netral; **merah hanya untuk yang rugi atau buruk**, hijau untuk yang baik. Di grafik peringkat yang punya temuan `konsentrasi`, yang ditonjolkan adalah **n batang teratas temuan itu, dan hanya itu** (erp-frontend #2210): grafik berjudul "4 produk teratas ..." punya empat batang beraksen, dan sorot `tertinggi` dari server tidak ikut karena judulnya berbunyi "n teratas", bukan "tertinggi". Tanpa temuan itu, sorot dari server yang dipakai. Satu aturan (`indeksDisorot`) dipakai warna batang, baris keterangan ("4 produk teratas", `keteranganPeringkat`), dan baris tebal tabel rincian, supaya ketiganya menonjolkan baris yang sama dengan judulnya.
- Tick sumbu dibuat bulat dan serapat mungkin membungkus datanya (`sumbuBagus`, `sumbuSelisih`): satu pencilan tidak melebarkan sumbu ke kelipatan besar berikutnya, dan tak ada titik yang dibuang.
- Penilaian menang atas aksen: batang tertinggi yang masih di bawah target tetap ditandai buruk.
- Identitas dan arah **tak pernah warna saja**: arah ditulis dengan kata ("Karena omzet turun"), tanda di angka ("−121 jt"), baris keterangan dan legend berteks, dan temuan memakai bentuk ikon berbeda per arah (`temuan-analisa.tsx`).
- ⛔ **Tidak ada komponen atau warna khusus Copilot.** Semua grafik memakai `ChartContainer` (`components/ui/chart.tsx`) dan token yang sudah ada: `WARNA_BAGAN` dan `WARNA_AMBANG` (`features/hris/dashboard/kartu/bagan/warna.ts`), `--fb-seri-*` lewat `warnaTim()`, serta token teks tema. Warna ditulis `theme: {light, dark}` supaya ikut mode gelap. Alasan dan larangannya di `.agent-kit/rules/team-memory.md` § Bagan/chart dan `.agent-kit/rules/ui-checklist.md`.
- Semua keputusan (judul, paragraf, skala sumbu, letak label, warna) ada di fungsi murni `lib/*.ts`, bukan di komponen: recharts dipalsukan di uji repo ini, jadi uji render tak membuktikan apa pun.
- ⚠️ **Satu pengecualian yang diminta pemilik produk: latar animasi DarkVeil** (2026-10-09, erp-frontend #2236). Ia komponen baru dengan dependensi baru (`ogl`), jadi menyimpang dari butir "tidak ada komponen khusus Copilot" di atas. Batasnya ditulis di kode supaya pengecualian ini tidak melebar:
  - **Lokal di fitur Copilot**, bukan komponen shared (`components/latar-dark-veil.tsx`, dipakai hanya lewat `latar-copilot.tsx`), dengan alasan tertulis di kepala berkasnya; dimuat malas tanpa SSR sehingga `ogl` tidak masuk bundel awal.
  - **Hanya di keadaan awal** halaman (katalog, sebelum ada giliran). Begitu ada pertanyaan ia **tidak dirender sama sekali** (`lib/latar.ts` `keadaanLatar`): tabel dan grafik tidak boleh bersaing dengan latar yang bergerak. Animasinya berhenti saat `prefers-reduced-motion`, tab tersembunyi, atau wadah di luar layar; tanpa WebGL halaman tetap berfungsi tanpa latar.
  - **Peredam dari hasil ukur kontras, bukan selera**: di atas kanvas ada lapisan `bg-background` 70% di mode gelap dan 96% di mode terang, dipilih supaya teks redup terkecil tetap minimal 4,5:1 di titik latar yang paling merugikan (diukur 2026-10-09 dari tangkapan layar; komentar `latar-copilot.tsx`). Akibatnya di mode terang latar hanya rona tipis. Persennya tidak boleh diturunkan tanpa mengukur ulang di kedua tema.
  - Ini dekorasi halaman awal, **bukan** preseden untuk warna atau komponen grafik: blok jawaban tetap tunduk pada butir-butir di atas.

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

### 10. Model tidak menyaring, menghitung, atau mengetik tabel

Angka yang dihitung model berubah dari jawaban ke jawaban dan tidak bisa ditelusuri, sedangkan angka dari alat sama setiap kali dan tampil di tabel yang bisa diperiksa. Aturan ini diputuskan 2026-10-09 dari satu kejadian PROD hari itu: penanya meminta izin bersubtipe "tidak masuk kerja" saja untuk satu periode gaji; alatnya mengembalikan 235 catatan campuran karena belum punya saringan jenis; model menyaring barisnya sendiri, mengetik tabelnya sebagai teks, dan menghitungnya **50 di satu jawaban lalu 60 di jawaban berikutnya untuk data yang sama**. Untuk persentase izin terhadap hari kerja ia menjumlah dan membagi sendiri angka alat lain, dengan pembilang yang salah (komentar `cuti_tim.go`, `tanya.go`, `penjaga_tabel.go`).

- **Menyaring adalah tugas alat.** Bila sebagian data wajar diminta (jenis, subtipe, orang, rentang), alatnya menyediakan argumen saringan dan menerapkannya atas seluruh baris sumber sebelum tabel dan hitungan dibuat; nilai saringan yang tak dikenal **ditolak**, tidak diabaikan diam-diam. Saringan yang dipakai dicatat di `Sumber.saringan` dan tampil sebagai "disaring: ..." di keterangan sumber (`cuti_tim.go`, `lib/keterangan-sumber.ts`).
- **Menghitung adalah tugas alat atau sumbernya.** Jumlah baris, jumlah hari, dan rincian per kelompok dihitung alat dari baris yang sama dengan tabelnya dan dikirim ke model sebagai ringkasan untuk **disebut ulang** (`hitungRingkasanCuti`: `jumlah_catatan` selalu sama dengan jumlah baris tabel).
- **Angka turunan diambil dari sumber bila sumber sudah menghitungnya.** Persentase, rasio, dan total yang sudah dihitung modul pemiliknya diteruskan apa adanya beserta artinya; alat tidak menghitung ulang, dan model apalagi. Contohnya `ringkasan_kehadiran`: persen kehadiran dan persen izin tidak masuk kerja datang dari attendance, lengkap dengan penyebutnya, dan satu-satunya hitungan di alat itu (selisih poin persen izin) dinyatakan terbuka di kodenya (`ringkasan_kehadiran.go`).
- **Arti angka ikut dikirim.** Angka turunan tanpa definisi akan ditafsir ulang: catatan alat menyebut satuan (hari-orang, hari kalender), apa yang masuk penyebut, dan apa yang tidak (`catatanRingkasanKehadiranID`, `catatanRingkasanCutiID`).
- **Tabel selalu dibangun sistem**, walaupun penanya meminta "buatkan tabel". Model menulis satu sampai tiga kalimat inti dan merujuk tampilan di bawahnya.
- **Bila alat tak punya saringan atau angkanya, model mengatakannya terus terang** ("belum tersedia sebagai hitungan sistem"), menyebut angka mentah yang memang ada, dan tidak menggantinya dengan hitungan sendiri.

Yang menegakkannya: prompt aturan 15 (`tanya.go`, larangan per perbuatan), penjaga `tabel_diketik` (`penjaga_tabel.go`: tabel bergaris minimal 2 baris, atau daftar minimal 6 butir saat blok sudah tampil), deskripsi alat yang mengarahkan pertanyaan persen ke alat yang menghitungnya, dan uji pertanyaan tetap bersyarat `saringan_wajib` (`cmd/ujitetap/uji.go`). ⚠️ **Yang tidak dijaga penjaga mana pun**: hitungan dan persentase di dalam kalimat biasa, angka tanpa awalan `Rp`, dan saringan yang dilakukan model diam-diam. Untuk itu satu-satunya penahan adalah aturan prompt dan ketersediaan alat yang menghitung; rinciannya di [[Microservices - Assistant Service]] § Penjaga jawaban sisi server.

### 11. Urutan baca 3-30-3, pita belum final, dan kolom andal

Rumusnya: **3 detik** pertama menjawab angkanya, **30 detik** menjawab artinya, **3 menit** menjawab rinciannya (`panel-tanya.tsx` `BadanJawaban`, erp-frontend #2272, #2273).

- **Jawaban yang dibuka kartu angka** (`kartuPembuka`, `lib/susunan-blok.ts`): kartu itu dulu, lalu kalimat jawaban, lalu "Perlu diperiksa", baru grafik beserta paragrafnya dan tabel. Jawaban lain memakai urutan lama; kalimat jawaban dirender tepat sekali di kedua cabang.
- **Rekomendasi bernomor** (`temuan-analisa.tsx`): `saran` tampil lebih dulu sebagai daftar bernomor berjudul "Rekomendasi" (server mengurutkannya dari dampak terbesar, jadi nomor berarti prioritas), baru `dugaan` berjudul "Yang perlu dicek". Kotak ini berlabel "bukan fakta" karena butirnya ditulis model.
- **Pita "Angka sementara, belum final"** selalu paling atas bila ada blok `keadaan: "belum_final"`. Isinya judul, keterangan, kalimat tentang apa yang aman dipakai, dan tombol "periode sebelumnya" (hanya di giliran terakhir, dinonaktifkan selagi jawaban lain diproses). Ia ikut tercetak di PDF.
- **Angka sementara tampil tanpa penilaian**: kartu tanpa panah dan tanpa warna baik/buruk (`belumFinal`, `lib/sorot-blok.ts`). Hijau penilaian memakai teks `emerald-700` supaya terbaca di mode terang (#2268).
- **Kolom andal** (`kolom_andal`, #2273): blok belum final yang membawa daftar kunci kolom yang tidak menunggu settlement digambar dan dijelaskan seperti biasa pada kolom itu (`nilaiSementara`), sedangkan kolom lain bertanda "(sementara)" di kepalanya (`kepalaKolom`, juga di PDF). Kalimat pita menyebut apa yang sudah bisa dipakai (omzet, unit terjual, biaya iklan, ROAS), dan hanya bila kuncinya punya label. Tanpa `kolom_andal` (backend lama) seluruh blok diredam. Daftar kolom andal milik backend; layar tidak memutuskannya.

### 12. Kepala kelompok bila alat yang sama dipanggil lebih dari sekali

Satu jawaban bisa memuat dua panggilan alat yang sama (dua divisi, dua periode). Tanpa pemisah, blok berjudul sama terbaca tanpa pemilik. `kepalaKelompok` (`lib/susunan-blok.ts`, #2273) membuka tiap kelompok dengan garis pemisah dan judul yang menyebut apa yang **membedakan** panggilan itu:

- saringan yang nilainya berbeda antar panggilan ("Divisi Kyura"); panggilan yang tak membawa saringan itu berjudul "Semua divisi";
- periode blok akarnya bila berbeda; keduanya berbeda = digabung;
- tak ada yang berbeda = tanpa judul.

Asalnya `Blok.saringan` di blok **akar** panggilan (selalu hadir walau `[]`, hanya di blok akar; jawaban lama tanpa kunci ini tampil seperti sebelumnya). Label kunci dan nilai memakai `butirSaringan`, sama dengan keterangan sumber. Kelompok alat lain sesudah kelompok berjudul mendapat garis pemisah tanpa judul. PDF mencetak per kelompok bila ada kepala kelompok.

### 13. Tautan halaman dan hak klik

Kalimat Copilot boleh menyuruh penanya membuka halaman, dan tautannya hanya bisa diklik oleh yang berhak (#2276, #2282, #2284). Model tidak menulis nama halaman; ia menulis token `[[buka:<nama_alat>]]` dan server membuang nama yang bukan alat yang ditawarkan ([[Microservices - Assistant Service]] § Gelombang 2026-10-10). Semua sisi layar ada di satu berkas, `lib/tautan-halaman.ts`:

- **Peta nama alat ke rute** (`PETA_HALAMAN_ALAT`): hanya alat yang halamannya ada **dan** jelas memuat data alat itu. Alat yang tak dipetakan tampil sebagai nama sumbernya, teks biasa. Menebak rute membuat tautan mendarat di halaman yang salah tanpa galat. Dua uji menjaga peta: tiap rute punya `page.tsx`, dan terdaftar sebagai menu sidebar di kategori yang didukung.
- **Label tautan = label menu sidebar rute itu** (`keySidebar`), supaya teks tautan dan nama menu tak pernah berbeda. Satu pengecualian bernama (`LABEL_DARI_SUMBER`): `ringkasan_marketing` memakai nama sumbernya, karena "Ringkasan" di tengah kalimat tak menunjuk apa pun.
- **Boleh-tidaknya diklik memakai fungsi sidebar** (`bolehBukaHalaman`: `kunciModulAktif` + `bolehItemSidebar`), bukan aturan RBAC baru. Tiga hasil: **tautan** (berhak), **terkunci** (terpetakan tetapi tak berhak: label redup, bukan tautan), **label** (tak terpetakan). Ini keputusan **menu**, bukan keamanan: datanya tetap dijaga halaman dan backend tujuan.
- **Kategori yang didukung** (`KATEGORI_DIDUKUNG`) hanya yang gerbangnya "kategori aktif + izin item". Portal Saya, manufacture, warehouse, dan integration tidak, karena gerbangnya hidup di komponen sidebar dan menirunya melahirkan aturan akses kedua. Alat yang halamannya terbelah di dua halaman atau tak terdaftar di sidebar kategori itu sengaja tak dipetakan (daftarnya di komentar berkas).
- **Teks polos untuk PDF dan judul percakapan** (`teksTanpaTautan`): token jadi label halamannya, token tak dikenal dibuang rapi.
- Tombol unduh PDF memakai ikon unduh (label lewat tooltip).

### 14. Label cek silang: jujur terhadap tiga keadaan

Cek silang ([[ADR - 0165 Copilot Tidak Menyimpulkan Ketiadaan atau Sebab dari Satu Sumber, Cek Silang Dikerjakan Sistem dengan Tiga Keadaan]]) menghasilkan tiga status dan label layar wajib mempertahankan bedanya:

| Status backend | Label bermakna | Yang DILARANG |
|---|---|---|
| `libur_tercatat`, `ada_shift_tercatat`, `ada_penanggung_jawab` | ada, dengan jenis libur bila ada | menyatakannya pasti lengkap |
| `tanpa_libur_tercatat`, `tanpa_shift_tercatat`, `tanpa_penanggung_jawab` | "tanpa X **tercatat**" | "tidak ada X" |
| `tidak_diperiksa` | "tidak diperiksa" (sebab bila ada) | "tidak ada", atau angka nol |

Kolom cek di tabel (mis. status libur per tanggal, host yang mencatat shift) memakai label yang sama; contoh bentuk datanya di `lib/cek-libur.contoh.ts` dan `lib/live.contoh.ts`. Hari berjalan dan hari yang belum tersinkron tidak ikut deret harian `live`; layar menyebutnya sebagai hari yang tak ikut.

Rekap payroll per departemen menampilkan keterangan asal departemennya (sal_departemen: saat gaji dihitung, saat ini, atau campuran) dan baris departemen kecil yang digabung; kartu, templat, dan saran beralat payroll hanya ditawarkan bila oleh_payroll benar (lib/akses-payroll.ts), sedangkan penegakannya di backend ([[ADR - 0164 Data Upah di Copilot Hanya untuk Direktur, Supervisor HRD, dan IT, Tanpa Daftar Gaji per Orang]]).

### 15. Jebakan tata letak: area gulir yang tak berposisi

Kepala (judul + Percakapan baru, Jadwal Tugas, Riwayat) dan kaki (pilih pertanyaan + kotak tulis) halaman Copilot **mengambang** di atas area gulir; isi memudar di belakangnya dan diberi ruang setinggi tepi itu, yang **diukur** (`ResizeObserver`), bukan ditulis mati (`lib/tepi-melayang.ts`, #2267, #2274). Aturan yang berlaku:

- **Area gulir wajib `relative`** (`AREA_GULIR` = `relative min-h-0 flex-1 overflow-y-auto overscroll-contain`, #2280). Elemen `position: absolute` di dalam area gulir yang tak berposisi (mis. `sr-only`) berinduk ke leluhur di **luar** area itu: ia tak ikut tergulir, tak terpotong, dan menambah tinggi **dokumen** sebesar letaknya di dalam isi. Diukur 2026-10-10 di Chrome (1907x870, dua jawaban): dokumen 2476 px untuk jendela 870 px, hanya karena dua `sr-only` di tautan terkunci; roda tetikus di dasar percakapan lalu menggulir dokumen dan panel terdorong keluar layar. jsdom tidak menangkapnya (tak ada mesin layout), jadi penjaganya mengunci kelas, bukan hasil (`lib/area-gulir.test.ts`).
- **`overscroll-contain`** menahan gulir yang mentok agar tak berantai ke leluhur.
- **Jangan `scrollIntoView`** di dalam area ini: ia menggulir semua leluhur termasuk dokumen. Pakai `gulirkanKeDalam`, yang hanya mengubah `scrollTop` wadah bertanda `data-area-gulir`.
- Kepala diredam hanya saat isi sudah digulir (`sudahTergulir`), supaya latar animasi terlihat utuh di posisi paling atas.
- Subjudul halaman "ERP AI Assistant" (#2271). Katalog pertanyaan 18 dari 21 kartunya kini berbentuk pertanyaan keputusan; statusnya **draf** sampai wawancara manajemen.
## Jalur tanpa mengetik

Kalimat bebas adalah tempat pertanyaan meleset dari kemampuan alat: periode yang tak diterima, saringan yang tak ada, janji yang tak bisa dipenuhi. Karena itu sejak 2026-10-09 pintu utama halaman Copilot adalah **katalog pertanyaan per departemen** (erp-frontend #2213, #2228, #2229; `lib/katalog-pertanyaan.ts`), dan kotak tulis bebas tetap ada tetapi bukan hal pertama.

- **Katalog sebagai pintu utama.** Tampilan awal berisi tab departemen (marketing, HR & GA, keuangan, gudang; departemen pemakai lebih dulu), kartu pertanyaan, isian berupa **pilihan** (bulan, periode gaji, divisi, channel, waktu), kalimat yang akan dikirim, dan apa yang didapat. Selama percakapan berjalan katalog tetap satu klik lewat "Pilih pertanyaan". Satu sumber data dipakai kartu halaman awal, dialog itu, dan saran di sheet Jadwal Tugas.
- **Kartu harus cocok dengan argumen alatnya.** `PERIODE_ALAT` adalah satu-satunya tempat di frontend untuk fakta "alat ini menerima periode apa", dan `katalog-pertanyaan.test.ts` mengunci tiap kartu dan templat terhadapnya: tak ada kartu yang menanyakan periode dalam bentuk yang tak diterima alatnya, tak ada baris yatim, dan tak ada janji di luar isi alat (test menyebut contohnya: stok di bawah minimum, kontrak berakhir "dalam N hari", cakupan departemen). `tanpa` periode hanya didaftarkan bila jawabannya jujur: alat marketing tanpa periode diam-diam menjadi 30 hari terakhir dan antrean gudang menjadi seluruh riwayat, jadi keduanya tidak boleh berkartu tanpa periode.
- **Periode khas departemen disediakan sebagai pilihan**, bukan dijelaskan: isian "periode gaji" menghitung rentang 26 sampai 25 (`periodeGaji`, WIB) untuk alat presensi, isian "bulan" untuk alat berbulan kalender.
- **Kalimat untuk Tanyakan menyebut periode eksplisit; kalimat jadwal memakai frasa relatif.** Yang ditanyakan sekarang menyebut nama bulan atau tanggal periodenya ("periode gaji 26 Agustus sampai 25 September 2026"), supaya alat ber-`YYYY-MM` dan alat berentang tanggal sama-sama bisa memakainya. Yang dijadwalkan selalu relatif ("bulan lalu", "periode gaji lalu"), karena nama bulan di jadwal berulang akan menanyakan bulan yang sama selamanya (`PilihanIsian.frasa` lawan `frasaJadwal`). Berlaku untuk isian bulan dan periode gaji; isian waktu cuti dan waktu antrean memakai frasa relatif di kedua mode.
- **Divisi marketing mengikuti pemakainya.** Isian Divisi berbawaan divisi pemakai (Kyura atau Beauty Hacks), selain itu "Semua divisi"; nilai rusak jatuh ke semua divisi, bukan diam-diam menyempitkan data. Kartu perbandingan meminta tiap divisi diambil terpisah karena backend menolak dua divisi dalam satu panggilan.
- **Jadwal tetap pengingat.** "Jadwalkan" dan bagian "Disarankan" membuka form jadwal yang **sudah terisi** untuk diperiksa lalu disimpan; yang tersimpan tetap pengingat bertautan, bukan laporan yang berjalan sendiri ([[ADR - 0135 Jadwal Tugas Copilot Mengirim Pengingat, Bukan Menjalankan Tanpa Kehadiran Pemakai]]). Kalimat di form menyebut kapan pengingat datang dan tidak pernah menjanjikan laporan terkirim (`kalimatPengingat`).
- **Hak akses tidak diputuskan katalog.** Katalog hanya diurutkan, tidak disaring: boleh-tidaknya sebuah alat tetap diputuskan modul sumbernya saat ditanya. Daftar toko dan produk sengaja tidak dijadikan isian karena daftarnya digerbang modul marketing.

⚠️ `PERIODE_ALAT` adalah **cermin** definisi alat di backend (komentarnya menyebut berkas dan baris yang disalin). Test menjaga kartu terhadap tabel itu, bukan tabel itu terhadap backend; alat yang argumen periodenya berubah wajib disunting di kedua repo.

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
10. **Saringan yang wajar diminta.** Daftar dulu sebagian data apa yang akan diminta orang dari alat ini (jenis, status, departemen, orang, rentang), lalu sediakan argumennya dengan nilai sah dari katalog sumbernya, bukan daftar kedua. Kolom yang dikirim sumber tetapi tak bisa disaring alat akan disaring model (§10). Catat saringan yang diterapkan di `Sumber.saringan`.
11. **Hitungan yang wajar diminta.** Daftar dulu angka apa yang akan ditanyakan (jumlah, total, persentase, perbandingan periode). Bila sumber sudah menghitungnya, teruskan angkanya beserta artinya; bila belum, alat menghitung dari baris yang sama dengan tabelnya dan mengirimnya sebagai ringkasan. Yang tidak bisa dihitung dengan jujur (mis. hari kerja yang tak dikirim sumber) dinyatakan tak tersedia, bukan didekati.
12. **Periode khas departemennya.** Tulis di deskripsi argumen apa arti periode kosong, dan pilih bentuk yang dipakai orangnya (bulan kalender, periode gaji 26-25, rentang, atau tanpa periode). Arti "bulan ini" hari ini berbeda antar alat ([[Microservices - Assistant Service]] § Kekurangan yang diketahui), jadi jangan mengandalkan periode kosong untuk pertanyaan yang menyebut bulan.
13. **Kartu katalognya.** Tambahkan alat ke `PERIODE_ALAT` dan buat kartunya di `KATALOG` (`lib/katalog-pertanyaan.ts`) dengan isian yang cocok dengan argumennya, teks di `copilot.katalog.*` kedua locale, dan templat jadwal bila wajar diulang; test katalog akan menunjuk yang tak cocok.

⚠️ **Laporan berblok penuh belum punya perakit umum.** `susunLaporanLaba` dan `uraiTemuanLaba` berbicara dalam kolom laba (`omzet`, `laba_kotor`, `margin_persen`, `unit_terjual`), jadi alat HR, keuangan, atau gudang belum bisa mendapat angka utama, urai, penyumbang, dan sebaran hanya dengan mendaftar. Mengangkatnya jadi perakit umum adalah keputusan tersendiri (**TBD**), sejalan dengan prinsip tim menunggu pemakai ketiga sebelum mengangkat abstraksi.

## Belum berlaku / Catatan

- ⚠️ **Dua tempat di grafik masih memotong teks dengan elipsis**: legend donat dan label metrik sumbu radar (`grafik-jenis.tsx`, dibaca di `origin/main` erp-frontend `0c96129b0`); rinciannya di §5. Label grafik batang (erp-frontend #2210) dan butir serta paragraf AI (bip-erp #2829) sudah di `main`; yang backend berlaku sesudah `assistant-service` di-deploy.
- 🟡 **Aturan §10 baru punya alat penghitung untuk dua hal**: saringan dan ringkasan `cuti_tim`, dan persen kehadiran lewat `ringkasan_kehadiran`. Alat lain tidak diperiksa satu per satu apakah saringan dan hitungan yang wajar diminta sudah tersedia (**TBD**); sampai itu ada, aturan prompt 15 membuat model menjawab "belum tersedia sebagai hitungan sistem".
- 🟡 **Katalog baru memuat empat departemen dan 19 alat** (isi `PERIODE_ALAT`), dari lebih dari seratus alat yang ditawarkan ke model; alat di luar katalog hanya terjangkau lewat kotak tulis.
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
| Saringan dan ringkasan `cuti_tim`; angka `ringkasan_kehadiran` diteruskan apa adanya | `cuti_tim_saringan_test.go`, `ringkasan_kehadiran_test.go` |
| Tabel atau daftar baris yang diketik model | `penjaga_tabel_test.go` |
| Kartu dan templat katalog cocok dengan periode alatnya; kalimat tanya eksplisit, kalimat jadwal relatif | `lib/katalog-pertanyaan.test.ts` |
| Kapan latar tampil dan beranimasi | `lib/latar.test.ts`, `components/latar-copilot.test.tsx` |

## Dokumen Terkait

- [[Microservices - Assistant Service]], kontrak blok, alat, penjaga, dan Jadwal Tugas
- [[ADR - 0132 Asisten AI Tanya-Jawab Lintas Modul, Lapisan Data Bisnis per Service Bukan Terpusat]], §4 (tak pernah menghitung dari data mentah) dan §7 (keluaran terstruktur dari komponen yang sudah ada)
- [[REF - Layout Dashboard erp-frontend]], komposisi halaman berangka di luar Copilot
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]], kalimat dan label milik layar
- [[ADR - 0164 Data Upah di Copilot Hanya untuk Direktur, Supervisor HRD, dan IT, Tanpa Daftar Gaji per Orang]] · [[ADR - 0165 Copilot Tidak Menyimpulkan Ketiadaan atau Sebab dari Satu Sumber, Cek Silang Dikerjakan Sistem dengan Tiga Keadaan]]
- [[Microservices - Marketing Analytics Service]], sumber angka dan aturan pemakaian kolom laba
- [[APP - Web ERP]], tempat layar Copilot berdiri
- `.agent-kit/rules/ui-checklist.md` dan `.agent-kit/rules/team-memory.md` § Bagan/chart, aturan komponen dan warna yang dipakai di sini
