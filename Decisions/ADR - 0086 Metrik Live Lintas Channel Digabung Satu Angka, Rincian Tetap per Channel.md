## Untuk Manajemen

**Apa yang berubah di layar.** Belum ada yang berubah sekarang. Keputusan ini menetapkan **cara menghitung** metrik KPI Host Live bila kelak ada channel selain TikTok (Shopee atau Lazada). Bentuknya: satu angka gabungan untuk seluruh channel, misal satu "Add to cart rate" yang menghitung TikTok dan Shopee sekaligus, bukan dua metrik terpisah. Di panel detail metrik, pembacanya tetap melihat rincian **per channel** beserta angka gabungannya, sehingga bisa menelusuri dari mana angka itu datang.

**Siapa yang terdampak.** Host live dan atasannya (skor mereka akan dihitung dari seluruh channel, bukan TikTok saja). HR dan pengisi template KPI (target harus diturunkan ulang saat channel kedua bergabung). Manajemen yang membaca tren KPI bulanan (bulan peralihan akan menunjukkan loncatan yang bukan perubahan kinerja).

**Yang tidak dijanjikan.** Data live Shopee **belum bisa diambil sama sekali**, dan penyebabnya bukan pekerjaan kode: API-nya menuntut otorisasi tingkat akun streamer, sementara seluruh kredensial kita tingkat toko. Lazada tidak menyediakan data live sama sekali. Jadi keputusan ini tidak menghadirkan angka Shopee; ia menetapkan apa yang terjadi bila otorisasi itu kelak diberikan. Host yang hanya live di Shopee **hari ini tidak punya sumber KPI otomatis**, dan itu harus disadari saat menyusun template supaya tidak muncul sebagai skor nol yang terbaca sebagai kinerja buruk. Riwayat KPI sebelum dan sesudah penggabungan tidak akan sebanding, dan tidak ada rencana menghitung ulang bulan yang sudah dibekukan.

**Perkiraan besaran kerja.** Kecil sampai sedang, dan seluruhnya menunggu keputusan bisnis di sisi Shopee. Yang bisa dikerjakan lebih dulu tanpa menunggu apa pun: menambah penanda channel pada catatan shift host. Itu satu field, satu migrasi ringan, dan satu penjaga.

## Deskripsi

*Metrik KPI Host Live yang berbentuk rasio dihitung sebagai satu angka gabungan lintas channel, dengan menjumlahkan pembilang dan penyebut seluruh channel lalu membaginya sekali, bukan merata-ratakan rasio per channel. Bahan mentahnya tetap tersimpan per channel dan peleburannya terjadi saat baca, sehingga panel detail metrik dapat menampilkan rincian per channel berdampingan dengan angka gabungannya. Penggabungan hanya sah untuk channel yang semantik field-nya sudah diperiksa, dan channel yang belum diperiksa digalatkan alih-alih dilewati diam-diam.*

- **Status**: ⚠️ **Sebagian terimplementasi** (2026-09-10). **§3 (prasyarat `live_shifts.channel`) SUDAH MERGED, TERVERIFIKASI DI DEV DAN DI PROD**: bip-erp [#1827](https://github.com/bip-itteam-internal/bip-erp/pull/1827) (merged 2026-09-10 15:17 WIB, `131ce13c`; field `Channel`, `channelNormal` dua sisi, `channelPerToko`, channel masuk predikat `jodohkanSesiDenganPorsi`, derivasi dari `department_shops` dengan 400 toko tak terpetakan vs 503 master data tak terbaca, resep `dropIndex` di `index.go`; `go build` dan `go test ./services/marketing-analytics` exit 0 di atas `main` terbaru, kontrol negatif dijalankan) dan erp-frontend [#1521](https://github.com/bip-itteam-internal/erp-frontend/pull/1521) (merged 2026-09-10 15:23 WIB, `72194d4a`; dialog Mulai menampilkan pesan server untuk 400/503 lewat daftar-izin, key `sebagianGagalSebab` di dua locale; hook pre-push `tsc`/`lint`/`build` lolos setelah merge `main`, `dialog-mulai.test.tsx` 27/27). ⚠️ Kedua merge dilakukan asisten atas penegasan ulang user, **menyimpang sadar dari [[ADR - 0077 Otonomi Merge Agent Digerbang Mekanisme yang Bisa Menolak]] §1**. **Dev, diukur 2026-09-10**: pipeline membangun ulang `marketing-analytics` 38 detik setelah merge dan frontend sekitar 4 menit sesudahnya; biner dev memuat string pesan barunya dan bundle dev memuat `sebagianGagalSebab` di 6 berkas; `POST /api/marketing-analytics/live-shifts` **lewat gateway dev** dengan JWT akun uji membalas **400** berbadan kalimat ICC Management, kontrol `GET /live-shifts/berjalan` 200, dan tak satu pun dokumen tertulis. **Yang TIDAK bisa dibuktikan di dev**: jalur 201 (channel tersimpan) dan penjodohan yang tetap berjalan, karena dev punya **0** baris `department_shops`, 0 `live_shifts`, dan 0 `mart_live_sessions`. Akibatnya sejak deploy ini **setiap** `POST /live-shifts` di dev dibalas 400, dan alur Mulai di layar dev tak bisa ditempuh karena dropdown tokonya kosong. **Prod, di-deploy manusia dan diukur 2026-09-11**: image backend dibangun 05:17 WIB dan biner prod memuat `channelPerToko` 1, `bacaTokoDepartemenBergalat` 3, `channelNormal` 1 (kontrol positif `jodohkanSesiDenganPorsi` 1); image frontend 07:55 WIB dan bundle prod memuat `sebagianGagalSebab` di 6 berkas. Tiga sesi host sungguhan yang dimulai 07:00 WIB tersimpan dengan `channel: "TIKTOK"`, jadi jalur 201 terbukti. Dua shift lama 9 September yang tak punya field `channel` **tetap terjodoh** di bawah biner baru (`GET /live-shifts` dari dalam container: `ada_data` true, GMV Rp3.353.938 dan Rp1.329.545), membuktikan normalisasi kosong = TIKTOK pada data prod. Satu-satunya yang tak teramati di mana pun: toast 400 di layar, karena 21 dari 21 toko prod terpetakan sehingga 400 tak pernah muncul, sementara dropdown toko dev kosong. **§1, §2, §4 sampai §11 masih 🟡 konsep** dan sebagian prasyaratnya di luar kendali kita (otorisasi streamer Shopee). Diukur di prod 2026-09-10: `mart_live_sessions` berisi **6.363 dokumen, seluruhnya `channel: "TIKTOK"`**, jadi belum ada satu pun sesi non-TikTok yang perlu digabungkan. Sementara itu `department_shops` **sudah** memuat 9 baris SHOPEE dan 3 baris LAZADA di samping 49 TIKTOK, jadi dimensi channel sudah nyata di master data dan hanya sesi live-nya yang belum ada. Prasyarat yang **bisa** dikerjakan sekarang tanpa menunggu Shopee: field `channel` pada `live_shifts`, yang per 2026-09-10 **tidak dimiliki satu pun dari 29 dokumen** shift September 2026. Keputusan ini lahir dari penelusuran metrik `add_to_cart_rate` Host Live 2026-09-10 (lihat §Context).
- **Path di repo**: `bip-erp/services/marketing-analytics/kpi_live.go` (`RasioAddToCart`, `bahanTraffic.tambah`, `tokoTikTokDepartemen`) · `bip-erp/services/marketing-analytics/kpi_live_individu.go` (jalur per host, prorata porsi waktu) · `bip-erp/services/marketing-analytics/live_shift_penjualan.go` (`jodohkanSesiDenganPorsi`, `batasSesiMenggantung`) · `bip-erp/services/marketing-analytics/live_shift_entity.go` (`LiveShift`, tempat field `channel` akan ditambahkan) · `bip-erp/services/marketing-analytics/entity.go` (`MartLiveSession`, sudah punya `channel`) · `bip-erp/services/marketing-analytics/envelope.go` (`ReasonShopeeLiveUserAuth`, `ReasonLazadaNoLive`) · `bip-erp/services/employee/kpi_sumber_live.go` (`minKlikRasioIndividu`, `bahanMetrikLive`, `rincianLive`) · `bip-erp/shared-library/models/employee/kpi_reduksi.go` (`RincianBaris`) · `erp-frontend/src/features/hris/kpi/lib/rincian-baris.ts` (`klasifikasiRincian`)
- **Tanggal**: 2026-09-10

## Context

**Penggabungan lintas channel sudah jadi perilaku bawaan kode, tanpa seorang pun memutuskannya.** `bahanTraffic.tambah(sesi, porsi)` menjumlahkan seluruh sesi yang terjodohkan ke sebuah shift **tanpa memeriksa `channel` sama sekali**, lalu `RasioAddToCart` membagi jumlah pembilang dengan jumlah penyebut. Artinya begitu sesi Shopee tersimpan di `mart_live_sessions`, ia langsung ikut terjumlah dan angkanya langsung jadi gabungan. Keputusan ini karena itu bukan mengubah rumus, melainkan **menjadikan yang sudah terjadi itu eksplisit dan berpenjaga**. Tanpa ADR ini, penggabungan tetap terjadi, hanya saja tanpa penjaga semantik, tanpa pelaporan cakupan, dan tanpa seorang pun tahu kapan mulainya.

**Penyebut rasio adalah klik produk, dan itu bagian dari definisi metriknya.** `RasioAddToCart` = `add_to_cart ÷ product_clicks × 100`, dengan komentar yang menyatakan penyebut klik itu keputusan pemilik metrik dan bukan detail perhitungan yang bebas diubah. Penelusuran 2026-09-10 menemukan alasan yang lebih kuat daripada yang tertulis di sana: `add_to_cart` dan `product_clicks` keduanya **cacahan peristiwa**, sementara `viewers` adalah cacahan yang ter-dedup. Terukur pada 351 sesi prod yang punya kedua field, `viewers` **tak pernah sekali pun** melebihi `views` dan rasio `views ÷ viewers` rata-rata 1,25 (maksimum 1,75), konsisten dengan `viewers` sebagai hitungan orang. Tetapi **9 sesi punya `product_clicks` lebih banyak daripada `viewers`**, yang mustahil bila klik dihitung per orang. Rasio dengan penyebut penonton karena itu mencampur peristiwa dibagi orang, tidak punya batas atas 100%, dan tidak boleh dibaca sebagai "berapa persen penonton". Penyebut klik tidak punya masalah itu.

**Rasio antar periode sudah dilarang dijumlahkan, dan alasannya berlaku antar channel.** `DaftarkanFormulaSumber` mendaftarkan `add_to_cart_rate` dengan reduksi `RataRata`, bukan `JumlahNilai`, dengan komentar bahwa menjumlah persentase memberi "7% + 8% = 15%, bukan capaian apa pun". Alasan yang sama melarang merata-ratakan rasio per channel: merata-ratakan memberi bobot sama kepada channel bervolume 10 klik dan channel bervolume 5.000 klik. Yang benar tetap jumlah pembilang dibagi jumlah penyebut.

**Shopee terhalang otorisasi, bukan ketiadaan API, dan bedanya sudah dicatat sengaja.** `ReasonShopeeLiveUserAuth` menyatakan seluruh API livestream Shopee ber-`api_type: "User"` (user_id ikut dalam tanda tangan) sementara seluruh 24 kredensial Shopee kita shop-level dengan `user_id_list` kosong; panggilan nyata `get_session_detail` membalas `error_param "There is no user_id in query"`, terverifikasi 2026-08-02. Lazada dinyatakan terpisah lewat `ReasonLazadaNoLive` karena Open Platform-nya tidak menyediakan analytics sesi live sama sekali. `tokoTikTokDepartemen` menyaring `channel: ChannelTikTok` dengan komentar yang menyebut host Shopee "TIDAK punya sumber otomatis, dinyatakan di sini supaya tidak terbaca sebagai kelalaian". Ketersediaan per metrik dipetakan di [[Sales - Marketing Analytics (Audit Ketersediaan Data)]] §6.

**`live_shifts` tidak punya channel, dan itu lubang yang menganga sebelum channel kedua masuk.** Penjodohan shift ke sesi hanya membandingkan `shop_id`, `username` terhadap `akun_live`, dan irisan waktu. Tidak ada channel di mana pun dalam predikat itu, dan `LiveShift` tidak punya fieldnya. Diukur prod 2026-09-10: **0 dari 29** dokumen shift September 2026 memuat `channel`. Konsekuensinya satu shift bisa menjodoh ke sesi dua platform sekaligus, dan gagalnya **senyap**: tidak ada galat, angkanya hanya menjadi lebih besar dan tetap masuk akal. Ini kelas kegagalan yang sudah berulang di repo ini (200 berisi baris kurang atau lebih tanpa satu pun galat).

**Satu sesi dibawakan banyak host, sehingga cacahan penonton tidak bisa dimiliki per orang.** Diukur prod September 2026: **29 shift dari 9 host terjodohkan ke hanya 5 sesi TikTok yang berbeda**, karena tiap akun menyiarkan satu siaran panjang yang host-nya bergantian masuk. Menjumlahkan penonton sesi ke setiap host memberi 13.110 sementara penonton dari 5 sesi distinct hanya 4.757, penggandaan **2,76 kali**. Prorata porsi waktu menghapus penggandaan itu, tetapi hasilnya bukan cacahan orang lagi. Yang tidak bisa dihilangkan: dedup TikTok berlaku di dalam satu sesi saja, jadi tidak ada angka "penonton unik sebulan" di data mana pun yang kita punya, dan tiga host satu sesi menerima rasio yang **identik** karena prorata mengalikan pembilang dan penyebut dengan faktor yang sama. Batas ini sudah tertulis di komentar `kpi_live_individu.go` dan diterima sebagai konsekuensi [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]].

**Ambang sampel dikalibrasi untuk satu channel.** `minKlikRasioIndividu = 100` menolak rasio per orang yang penyebutnya terlalu kecil. Terukur September 2026, ambang itu membuang **5 dari 9 host**, dan pembuangannya tepat: dua host dengan 6,4 dan 4,2 klik prorata menghasilkan rasio 13,52% dan 13,76%, yang terhadap target 7 berarti skor 193 dan 197. Dengan penyebut gabungan, ambang yang sama menjadi lebih permisif dengan sendirinya: 60 klik TikTok ditambah 50 klik Shopee lolos, padahal tak satu pun channel punya sampel bermakna.

**Rincian metrik punya tiga jenis baris dan penandanya teks.** `RincianBaris` di shared-library hanya `{label, nilai}`. Frontend memisahkan komponen, hasil, dan pengecualian di `rincian-baris.ts` dengan membaca awalan `"= "` dan frasa `"(tak ikut dihitung)"`, dan berkas itu sendiri menyatakan penandanya heuristik dan bukan kontrak. Model tiga-jenis itu tidak punya ember yang benar untuk baris **sub-total**: sebagai komponen ia mengundang dijumlahkan (dan rasio tidak boleh dijumlah), sebagai `"= "` ia bersaing dengan baris hasil yang sebenarnya.

## Decision

### 1. Metrik rasio Host Live adalah SATU angka gabungan lintas channel

Berlaku untuk `conversion_rate`, `add_to_cart_rate`, dan `avg_viewing_duration`, serta metrik rasio Host Live yang lahir kemudian. Rumusnya jumlah pembilang seluruh channel dibagi jumlah penyebut seluruh channel, dikali 100 untuk yang berbentuk persen:

```
add_to_cart_rate = Σ add_to_cart (semua channel) ÷ Σ product_clicks (semua channel) × 100
```

**Bukan** rata-rata dari rasio per channel, dengan alasan yang sama yang melarangnya antar periode. Template KPI memuat satu metrik dengan satu bobot dan satu target, bukan satu metrik per channel.

### 2. Penyebutnya tetap klik produk, bukan penonton atau impresi

Ditetapkan di sini supaya tidak diusulkan ulang. Pembilang dan penyebut wajib satuan yang sama, dan `add_to_cart` bersama `product_clicks` keduanya cacahan peristiwa. Penyebut penonton menghasilkan angka yang tidak berbatas 100% dan tidak dapat dibaca sebagai persentase orang (bukti di §Context). Bila kelak diinginkan metrik berbasis orang, yang dibutuhkan **pembilang** ter-dedup (jumlah penonton yang memasukkan ke keranjang), bukan penyebut yang diganti, dan field itu tidak ada di endpoint mana pun yang kita panggil.

### 3. `live_shifts.channel` adalah prasyarat, dan dikerjakan sebelum sesi non-TikTok pertama tersimpan

Field `Channel` ditambahkan ke `LiveShift` dan ikut ke dalam predikat penjodohan, sehingga sebuah shift hanya menjodoh ke sesi ber-channel sama. Dokumen shift lama tanpa field itu diperlakukan `TIKTOK`, karena terukur seluruh 6.363 sesi mart memang TikTok, dan asumsi itu **kedaluwarsa** begitu channel kedua masuk. Karena itu urutannya mengikat: field lebih dulu, sesi non-TikTok kemudian. Terbalik berarti ada periode yang angkanya sudah tercampur dan tidak bisa dipisah lagi.

Field ini juga yang membedakan "host tidak pernah live di channel itu" dari "live tapi datanya belum turun", pembedaan yang dibutuhkan §5 dan §6.

### 4. Channel hanya ikut digabung setelah semantik field-nya diperiksa, dan yang belum diperiksa DIGALATKAN

Daftar-izin channel yang boleh masuk penjumlahan hidup **di kode**, bukan di komentar, dan diuji. Sebuah channel masuk daftar hanya setelah dibuktikan bahwa `add_to_cart` dan `product_clicks` versinya adalah cacahan peristiwa pada langkah funnel yang sama seperti TikTok. Sesi ber-channel di luar daftar membuat metrik **galat** ("channel X belum diverifikasi semantiknya"), bukan dilewati diam-diam: melewatinya membuat angkanya tetap wajar sementara sebagian bisnisnya tak terhitung, dan itu tepat kelas kegagalan yang paling sulit disadari.

Pemeriksaan semantik ini bukan formalitas. Bila Shopee ternyata mengirim "pengguna unik yang menambahkan ke keranjang", penjumlahannya mencampur satuan dan hasilnya salah tanpa satu pun galat.

### 5. Cakupan dilaporkan sadar channel

`CakupanPersen` (yang menentukan sebuah metrik dilaporkan `otomatis` atau `semi`, dan yang tampil sebagai "Kelengkapan data" di layar) wajib turun bila ada channel yang host-nya benar-benar live di sana tetapi datanya belum turun. Tanpa ini, channel yang belum sync jatuh keluar dari pembilang **dan** penyebut sekaligus, sehingga angkanya tetap wajar dan tetap berlabel lengkap. Risikonya sudah nyata pada satu channel: dari 5 sesi September, satu sesi `carevolution.hub` tidak punya `viewers` sama sekali (null, bukan nol).

### 6. Rincian metrik menampilkan bahan per channel berdampingan dengan hasil gabungannya

Panel detail metrik memuat bahan mentah tiap channel sebagai baris komponen, lalu satu baris hasil berawalan `"= "` untuk angka gabungannya:

```
DARI DATA SUMBER
  Masuk keranjang (TikTok)          39
  Klik produk (TikTok)              712
  Masuk keranjang (Shopee)          12
  Klik produk (Shopee)              180
PERHITUNGAN
  = Add to cart rate gabungan       5,72%
```

Channel yang host-nya pakai tetapi datanya belum turun **tetap muncul** dengan nilai "belum ada data", bukan dihilangkan, mengikuti preseden `rincianSkorTim` yang menampilkan anggota belum berskor sebagai "Belum dinilai" justru supaya cakupan tak terbaca lebih lengkap dari kenyataannya. Channel yang host-nya tidak pernah pakai tidak dimunculkan, karena itu kebisingan.

Bentuk ini bekerja pada frontend yang ada sekarang tanpa perubahan, karena awalan `"= "` sudah menempatkan baris gabungan di blok terpisah.

### 7. Menampilkan RASIO per channel menuntut field `jenis` pada `RincianBaris` lebih dulu

Bila kelak diminta menampilkan rasio tiap channel (misal TikTok 5,48%, Shopee 6,67%, gabungan 5,72%), itu **tidak boleh** dikerjakan dengan penanda teks yang ada. Sebagai komponen, rasio duduk di blok yang mengundang penjumlahan; sebagai `"= "` ia bersaing dengan baris hasil sesungguhnya sehingga pembacanya tak tahu mana yang final; sebagai pengecualian ia salah arti, karena rasio per channel memang ikut membentuk angkanya, hanya tidak secara aditif.

Prasyaratnya field `jenis` pada `RincianBaris` di shared-library, menggantikan heuristik teks, dengan nilai untuk "sub-total, jangan dijumlah". Itu juga perbaikan yang sudah direkomendasikan sendiri oleh `rincian-baris.ts`.

### 8. Ambang sampel dihitung ulang atas penyebut gabungan

`minKlikRasioIndividu` tetap diterapkan pada penyebut yang dilaporkan, yaitu penyebut gabungan, karena rasio yang dilaporkan juga gabungan. Tetapi angkanya (100) diukur ulang saat channel kedua bergabung dan **tidak** dibawa apa adanya. Ukurannya sama seperti sebelumnya: penyebut terkecil yang membuat rasio per orang bermakna, dinilai dari sebaran nyata, bukan dari selera.

### 9. Penyimpanan tetap per channel, peleburan terjadi saat baca

Tidak ada perubahan penyimpanan yang diperlukan: `mart_live_sessions` sudah menyimpan `channel` per sesi. Bahan mentah tidak boleh dilebur saat menulis. Melebur saat menyimpan tidak bisa dibatalkan, melebur saat baca bisa kapan saja, dan §6 memang menuntut bahan per channel tetap tersedia untuk ditampilkan. Aturan ini sejalan dengan keputusan yang sudah berlaku untuk atribusi order.

### 10. Target diturunkan ulang saat channel bertambah, dan riwayat sebelum-sesudah dinyatakan tidak sebanding

Bergabungnya channel kedua menggeser angka gabungan **walau tidak ada satu orang pun yang berubah kinerjanya**, karena komposisi channel-nya berubah. Karena itu: target metrik wajib diturunkan ulang pada periode peralihan, komposisi channel per periode dicatat supaya loncatannya dapat dijelaskan, dan bulan peralihan ditandai pada bagan tren. Skor periode yang sudah dibekukan **tidak** dihitung ulang, sejalan dengan [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]].

### 11. Prorata porsi waktu berlaku apa adanya untuk channel apa pun

Aturan penjodohan berbasis irisan waktu, penolakan sesi menggantung yang nol order dan nol GMV, penanda `PerluKoreksi` untuk shift berdurasi lebih dari 12 jam, dan aturan pointer nil (null berarti belum dikirim platform, bukan nol) semuanya tidak bergantung platform dan tidak berubah. Termasuk batasnya yang sudah diterima: host yang bergantian dalam satu sesi menerima rasio yang identik.

## Consequences

### Yang membaik

- Penggabungan yang sudah terjadi secara bawaan menjadi keputusan yang tercatat, berpenjaga, dan punya tanggal mulai, alih-alih perilaku yang tidak pernah diputuskan siapa pun.
- Satu metrik dengan satu bobot dan satu target membuat template KPI tidak membengkak tiap kali ada channel baru, dan tidak menuntut pengisi template memahami channel mana yang aktif.
- Penyebut klik ditetapkan beserta alasan yang lebih kuat daripada yang tertulis di kode, sehingga usulan mengganti penyebut punya jawaban tanpa perlu mengukur ulang.
- `live_shifts.channel` menutup lubang penjodohan yang hari ini masih senyap, dan bisa dikerjakan sekarang tanpa menunggu keputusan Shopee.
- Rincian per channel membuat angka gabungan dapat ditelusuri pembacanya, sejalan dengan alasan yang sudah tertulis di sumber KPI bahwa yang melihat sebuah persen harus bisa menelusurinya ke dua angka pembentuknya.

### Yang memburuk atau tetap terbuka

- **Riwayat KPI terputus sebandingnya** pada bulan peralihan, dan bagan tren akan menggambarnya sebagai gerakan nyata. Mitigasinya penjelasan, bukan penghapusan gejala.
- **Host yang bergantian dalam satu sesi tetap menerima rasio identik.** Penggabungan lintas channel tidak memperbaikinya sama sekali; ia mewarisinya utuh. Terukur September 2026: tiga host satu siaran menerima 5,55% dan 4,06% yang sama persis.
- **Tidak ada angka penonton unik per orang, dan tidak akan ada** dari data yang kita punya. Dedup berlaku per sesi, jadi penjumlahan lintas sesi menghitung orang yang sama berkali-kali. Kolom cacahan penonton per host tidak boleh dijumlahkan ke tingkat tim (terukur menggandakan 2,76 kali).
- **Host Shopee tetap tanpa sumber otomatis** sampai otorisasi akun streamer diberikan, dan itu keputusan bisnis di luar kendali tim. Selama itu penilaiannya manual, dan template yang menugaskan metrik otomatis kepada mereka akan menghasilkan galat "belum dapat dihitung", bukan skor.
- **Field `jenis` pada `RincianBaris` belum ada**, sehingga §7 memblokir tampilan rasio per channel sampai dikerjakan. Sampai saat itu, pembaca yang ingin rasio per channel harus menghitungnya sendiri dari bahan yang ditampilkan §6.
- **Ambang sampel gabungan belum punya angka.** §8 menetapkan cara menurunkannya, bukan nilainya, karena sebaran channel kedua belum ada untuk diukur.

### Yang sengaja tidak dilakukan

- **Tidak** membuat metrik terpisah per channel dengan bobot masing-masing. Itu alternatif yang dipertimbangkan dan ditolak: template membengkak, bobotnya harus dihitung ulang tiap kali komposisi channel berubah, dan pembacanya menghadapi dua angka yang tidak bisa dibandingkan.
- **Tidak** merancang nama field yang netral lintas channel untuk bahan rasio. Semantik channel kedua belum diperiksa, dan field netral yang dibentuk dari data TikTok hampir pasti tidak muat lalu dibongkar. Ini konsisten dengan aturan yang sudah berlaku untuk atribusi afiliasi.
- **Tidak** menghitung ulang skor periode yang sudah dibekukan.
- **Tidak** menambah penyebut penonton sebagai metrik alternatif, dengan alasan satuan di §2.
- **Tidak** memakai ulang `auto_formula` untuk membawa aritmetika rumus. Field itu sudah berisi token reduksi (`rata_rata` dan seterusnya) yang di layar tampil sebagai "Rumus: Rata-rata"; menampilkan aritmetikanya menuntut field baru, dan memakai ulang yang lama menghapus keterangan reduksi yang sekarang benar tanpa satu pun galat.

## Dokumen Terkait

- [[Microservices - Marketing Analytics Service]] — service pemilik `mart_live_sessions` dan `live_shifts`
- [[API - Marketing Analytics Service]] — endpoint `/lives` beserta `unavailable_channels`
- [[Sales - Marketing Analytics (Audit Ketersediaan Data)]] — §6 ketersediaan metrik Live Shopping per platform
- [[HRIS - Otomasi Skor KPI]] — mesin skor yang mengonsumsi metrik ini
- [[REF - Penamaan Metrik & Sumber KPI]] — konvensi nama sumber dan metrik
- [[RUN - Menambah Metrik KPI Otomatis]] — prosedur menambah metrik baru
- [[HRIS - Matriks KPI per Departemen]] — posisi mana dinilai dari metrik apa
- [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]] — dasar penjodohan sesi dan prorata porsi waktu
- [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]] — siapa yang boleh mencatat shift live
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] — batas antara pengumpul metrik dan pemilik skor
- [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]] — kekebalan skor beku terhadap perubahan belakangan
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]] — label rincian per channel wajib lewat i18n
- [[REF - Kepemilikan Data]] — peta fakta bisnis dan service pemiliknya
