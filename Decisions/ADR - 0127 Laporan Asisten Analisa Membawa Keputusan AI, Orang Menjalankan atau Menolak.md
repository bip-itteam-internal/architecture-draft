# ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak

> **Status**: ⚠️ **Implemented (ada catatan)** — diukur 2026-09-28 (versi sebelumnya 2026-09-27). Kode backend **merged** ke `origin/main` bip-erp lewat dua belas PR (§ Realisasi di bawah), **BELUM deploy prod**. Layar keputusan di erp-frontend (`/marketing-analytics/keputusan`, penanda di beranda modul, field "Penerima uji keputusan" pada form Jadwal setara `penerima_bayangan` BE) **MERGED** (erp-frontend [#1763](https://github.com/bip-itteam-internal/erp-frontend/pull/1763), [#1767](https://github.com/bip-itteam-internal/erp-frontend/pull/1767), [#1774](https://github.com/bip-itteam-internal/erp-frontend/pull/1774) — § Realisasi butir l/m; catatan "sedang dinilai review, PR menyusul" di versi sebelumnya sudah tidak berlaku). Tab Hasil analisa jadi satu laporan + unduh PDF (§ Realisasi butir n) **belum ada PR**, dikerjakan di branch lokal. Menggantikan [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]] §5 dan §7, serta [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] §5 **khusus untuk laporan Asisten Analisa Marketing**.

%% Status ditulis di blockquote atas, bukan bullet di ## Deskripsi, dengan alasan yang sama
seperti ADR 0120: ## Untuk Manajemen mendorong Deskripsi melewati baris ke-15 sehingga status
tak terbaca VAULT-INDEX.json. %%

## Untuk Manajemen

**Apa yang berubah di layar.** Laporan terjadwal Marketing tidak lagi berhenti di angka dan
kalimat "perlu ditinjau". Di bagian atasnya muncul daftar keputusan yang sudah diurutkan, misalnya
"Hentikan iklan video C", "Kurangi belanja toko A", "Naikkan belanja produk B", "Lengkapi
harga pokok produk E", atau "Perbaiki kecepatan balas chat toko F". Tiap keputusan menyebut alasannya dan seberapa kuat dasarnya. Penerima cukup
menandai tiap keputusan **dijalankan** atau **ditolak**.

**Siapa yang terdampak.** Penerima laporan terjadwal yang sudah ada: pemegang toko, supervisor
tim marketing, leader iklan, dan Direktur. Tidak ada penerima baru.

**Apa yang TIDAK dijanjikan.**
- Sistem **tidak menjalankan** keputusannya sendiri. Ia tidak menyentuh akun iklan di TikTok
  maupun Shopee. Orang tetap yang menekan tombol di sana.
- Keputusan menyebut **arah** (hentikan, kurangi, naikkan), **bukan besaran rupiah**. Data
  delapan bulan terakhir menunjukkan belanja iklan hanya menjelaskan sekitar seperempat dari
  naik-turunnya laba, jadi angka "naikkan Rp X" tidak punya dasar yang bisa dipertahankan.
  Keputusan "naikkan belanja" selalu ditandai **dasar terbatas**.
- Laba yang belum matang **tidak pernah** menjadi dasar keputusan apa pun. Laporan 25 September
  mencetak laba minus Rp212 juta untuk dua hari, padahal uang yang sudah cair saat itu **nol
  persen**: itu belum matang, bukan rugi. Karena itu keputusan soal laba selalu memakai periode
  yang uangnya sudah cair, bukan beberapa hari terakhir.
- Keputusan "kurangi" dan "naikkan" belanja **belum bisa terbit** sampai manajemen menegaskan
  **satu** angka target ROAS. Sistem menyimpan 4,5; KPI Leader memakai 3,2.
- Tidak ada keputusan soal harga, diskon, atau pelanggan berulang (datanya kosong), dan tidak ada
  keputusan iklan untuk Lazada (tidak ada data iklannya).
- Tidak ada kotak tanya bebas. Itu tetap tahap berikutnya.

**Satu laporan untuk semua.** Direktur dan semua supervisor menerima laporan yang sama. Paling
atas: status keputusan pekan lalu per tim (dijalankan, ditolak, belum dijawab). Lalu paling banyak
lima keputusan terbesar. Lalu keputusan per tim. Tiap keputusan menyebut siapa pelaksananya.
Dikirim mingguan di awal pekan.

**Masa uji.** Satu sampai dua pekan pertama, keputusan hanya dikirim ke pemilik produk untuk
dinilai. Penerima lain baru menerimanya setelah pemilik produk menyatakan keputusannya layak.

**Perkiraan besaran kerja.** Sekitar dua sampai tiga pekan kerja satu orang backend, ditambah
satu layar kecil di web untuk tombol jalankan/tolak. Ongkos AI per laporan belum pernah diukur
dan akan diukur pada pekan pertama berjalan.

## Deskripsi

*Direktur memutuskan bahwa laporan Asisten Analisa Marketing harus membawa keputusan tindakan,
bukan sekadar urutan perhatian, sehingga penerimanya tidak perlu menafsirkan angka sendiri. ADR
ini mencatat keputusan itu sebagai penyimpangan sadar dari ADR 0120 §5 dan §7 serta ADR 0058 §5,
lalu memagarinya: tindakan dipilih dari katalog tertutup, kelayakan tiap tindakan dihitung
backend dari data, model memilih dan mengurutkan serta menjelaskan, dan jawaban orang (jalankan
atau tolak) dicatat sebagai ukuran pengganti kondisi berhenti.*

- **Path di repo**: `bip-erp/services/marketing-analytics/` (`keputusan_ai*.go` **(baru)**, `hasil_analisa.go`, `penjalan_jadwal.go`), `bip-erp/docker-compose.yml` + `docker-compose.dev.yml` (env `AI_*` untuk blok marketing-analytics), `erp-frontend/src/features/marketing-analytics/` (tombol jalankan/tolak **(baru)**)
- **Tanggal**: 2026-09-25

## Context

**Keputusan sebelumnya sengaja melarang ini.** ADR 0058 §5: *"Keluaran model adalah urutan
perhatian, bukan tindakan. Pemotongan anggaran, penghentian iklan, dan keputusan produksi tetap
dijalankan orang."* ADR 0120 §5 menegaskannya ulang dan menolak rekomendasi anggaran, karena
hubungan belanja iklan ke laba lemah (R² 0,258) dibanding ke revenue (0,714); simulasi alokasi
dimatikan sejak 2026-08-15 karena itu. ADR 0120 §7 menunda irisan 2 sampai 30 hari pemakaian
irisan 1 terbukti.

**Keinginan pemakainya berbeda.** 2026-09-25 pemilik produk menyampaikan bahwa rancangan awal
tidak sesuai keinginan Direktur: penerima laporan tidak boleh lagi dibebani menafsirkan angka;
AI membaca data yang ada, menyimpulkan "lakukan X", dan manusia cukup menjalankan atau
menolaknya. Direktur juga memutuskan tidak menunggu 30 hari §7. Layar FE irisan 1 baru mendarat
2026-09-25, jadi jam §7 belum sempat berjalan sehari pun.

**Yang sudah ada, diukur ke `origin/main` bip-erp 2026-09-25:**

- Klien AI `shared-library/ai` (`GenerateJSON`, `client.go:90`) mengembalikan pemakaian token
  dan model yang benar-benar menjawab, tanpa retry, kuota, maupun cache. Pemakainya hanya
  recruitment (draf lowongan, screening CV). Env `AI_*` hanya dideklarasikan di blok
  recruitment (`docker-compose.yml:794-799`, `.env.example:682-687`); ADR 0082 mencatat klien ini
  belum pernah di-deploy.
- Recruitment sudah punya pola **pilihan tertutup yang disaring ulang**: enum
  `RekomendasiScreening` (`lanjut`/`pertimbangkan`/`tidak_lanjut`) yang ditolak bila di luar daftar
  atau tanpa butir berbukti (`models_cv_screening.go:20`, `cv_screening.go:45-77`). Itu bentuk
  yang dipakai ulang di sini.
- Penyimpanan narasi sudah berdiri (`hasil_analisa.go`: `Narasi`, `NarasiStatus`, `NarasiJejak`
  append-only, `sidikPrompt`), tetapi **tak satu baris kode pun menulis `siap` atau `gagal`**:
  kelima perakit selalu menulis `menunggu` (`penjalan_jadwal.go:346, 457, 729, 958, 1287`).
- Aturan yang **sudah** memilah sasaran jadi ember tindakan, semuanya berbasis kode:
  `susunKeputusan` (vonis laba + ROAS vs ambang, `blok_keputusan.go`), `pilihPenggerus` dan
  `pilihPeluang` (`beranda_vonis.go`), `klasifikasiVideoBoros` (terbukti berbelanja tanpa hasil
  vs belum diketahui), dan pengelompokan Account Specialist "Perlu dibantu" / "Belanjanya layak
  ditambah" (`penjalan_jadwal.go:1193, 1218`).
- **Tidak ada katalog tindakan tertutup** di marketing-analytics, **tidak ada** fungsi yang membaca
  hasil lama per jadwal (`hasil_analisa_store.go` hanya `SimpanHasil` dan `DaftarHasil` tanpa
  filter), dan **tidak ada** field umur data di hasil.

**Apa yang AI tambahkan di atas aturan itu, dinyatakan jujur.** Ember kelayakan sudah dihitung
aturan. Yang belum ada adalah (1) **satu daftar keputusan lintas analisa**, karena kelima analisa
hari ini dikirim sebagai blok terpisah dan pembaca sendiri yang menyatukannya; (2) **pengurutan**
antar sasaran dari ember yang berbeda; dan (3) **kalimat perintah** yang menyebut sasaran dan
alasannya. Kelayakan sebuah tindakan **tidak** termasuk yang ditambahkan AI, dan sengaja tidak.

**Empat jebakan angka dari ADR 0120 §Context tetap berlaku** dan justru makin mahal di sini,
karena keluarannya kini perintah, bukan urutan: laba periode pendek tampak rugi; `revenue` level
video hanya terisi 8,9%; level iklan revenue nol secara struktural; retur sudah terpotong di
settlement (pernah membuat laba TikTok Rp 669.007.085 lebih kecil sebulan).

**Isi `marketing_analytics_db` PRODUKSI, diukur 2026-09-25** (baca-saja, skrip di
`.task-plans/cek-db-marketing-prod.js` dan `cek-db-marketing-cakupan-prod.js`). Kekayaannya nyata
tetapi tidak merata, dan ketidakmerataan itu yang membentuk katalog §3:

| Sumber | Terukur | Arti untuk keputusan |
|---|---|---|
| `mart_profit_attribution` level shop/product/campaign, TikTok + Shopee | Sejak 2026-04-05; revenue > 0 di 75–95% baris | Dasar kuat untuk keputusan iklan per toko, produk, kampanye |
| level `video`, TikTok | 867.183 baris; revenue > 0 hanya **94.218 (10,9%)**, ads_cost > 0 di 94% | Hentikan iklan video hanya dari yang revenue-nya tercatat; sisanya "periksa" |
| level `ad`, TikTok | revenue > 0 di **0 dari 29.644** baris | Nol struktural (jebakan ke-3 ADR 0120), tak pernah jadi dasar |
| Lazada | ads_cost > 0 di **0** baris seluruh level | Tak ada keputusan iklan Lazada |
| `sync_state` catatan profit | 6–8 SKU per hari tanpa HPP berlaku ("laba LEBIH BESAR dari sebenarnya"); mapping penanggung jawab mencakup 64 toko | Keputusan kebersihan data: benar hampir pasti, dan memperbaiki angka laba itu sendiri |
| `mart_cs_sla_daily` | Shopee saja, 9 toko, sejak 2026-09-09; membawa `target_rate` | Keputusan layanan chat, terhadap target yang sudah tertulis |
| `mart_komplain_bulanan` | 2025-05 .. 2026-09, per bulan | Hanya layak di kiriman bulanan |
| `mart_live_sessions` | 7.375 sesi sejak 2026-07-03; GMV > 0 hanya **854 (11,6%)**, penonton > 0 hanya 406 | Terlalu tipis untuk keputusan jam tayang; **tidak** masuk katalog |
| `mart_buyer_cohort`, `mart_price_floor` | **0 baris** | Tak ada keputusan harga, diskon, maupun pelanggan |
| `mart_ambang` | Satu dokumen `global`, `roas_min` 4,5, berlaku 2026-08-01 | Ambang yang dipakai sistem; 3,2 hanya hidup di KPI Leader |

⛔ **Laporan produksi yang sudah terkirim membuktikan jebakan pertama masih lolos.** Kiriman
mingguan 2026-09-25 09:10 WIB mencetak `Laba kotor: -Rp212.372.304` untuk periode **2 hari**
(23–24 Sep) dengan settlement cair **0%** di 52 variasi order. Kiriman itu juga hanya menyimpan
analisa `ringkasan_laba` padahal jadwalnya memuat lima, periodenya 2 hari padahal kekerapannya
mingguan, dan ringkasannya tanpa baris "Keputusan:" dari bip-erp #2075 — tanda kuat build prod
tertinggal dari `origin/main` (belum dicocokkan ke umur image).

**Yang belum terukur, dan dinyatakan sebagai asumsi:**
- Ongkos per laporan. Yang diketahui hanya overhead tetap ~2.030 token system prompt per
  panggilan akibat prefiks `cc/` (ADR 0082). Belum ada harga rupiah untuk endpoint internal.
- Endpoint `code.bharatainternasional.com` adalah relay ke penyedia luar, jadi angka hasil hitung
  laba keluar dari perusahaan. Diasumsikan diterima karena jalur yang sama sudah dipakai untuk CV
  pelamar, yang lebih sensitif; belum pernah diputuskan eksplisit (lihat [[CORE - OCR Document Service]]).

## Decision

### §1 Laporan membawa keputusan tindakan; orang menjalankan atau menolak

Keputusan Direktur. Tiap kiriman laporan Asisten Analisa memuat daftar keputusan berurutan
berbentuk "lakukan X terhadap Y". Penerima menandai tiap keputusan **dijalankan** atau
**ditolak**. Ini menggantikan ADR 0120 §5 dan ADR 0058 §5 untuk laporan ini saja; kapabilitas
AI lain (termasuk peringatan dini iklan video di ADR 0058 §6) tetap terikat ADR 0058 §5.

### §2 Sistem tidak mengeksekusi

Tidak ada panggilan ke platform iklan, tidak ada perubahan anggaran otomatis. "Manusia cukup
menjalankan" berarti manusia yang menekan tombol di TikTok atau Shopee. Batas ini tetap dari
ADR 0058 §5 dan tidak ikut digantikan.

### §3 Tindakan dipilih dari katalog tertutup

Katalognya tertutup tetapi **boleh tumbuh**: menambah tindakan cukup satu baris katalog + satu
aturan kelayakan + uji negatifnya, dengan syarat datanya terukur cukup (tabel §Context). Isi awal
sepuluh tindakan:

| Tindakan | Syarat kelayakan (dihitung backend, bukan model) | Keyakinan |
|---|---|---|
| `hentikan_iklan` | Video **terbukti** berbelanja tanpa hasil (revenue > 0 dan laba < 0), atau kampanye/produk penggerus dengan laba **matang** negatif. TikTok dan Shopee saja | tinggi |
| `kurangi_belanja` | Toko/produk/kampanye dengan ROAS di bawah ambang, laba matang | tinggi |
| `naikkan_belanja` | Vonis sehat, ROAS di atas ambang, laba matang (ember "layak ditambah" / peluang yang sudah ada) | **terbatas**, selalu |
| `lengkapi_hpp` | SKU tanpa HPP berlaku pada periode itu (sudah dicatat sync profit; laba terhitung lebih besar dari sebenarnya) | tinggi |
| `tetapkan_penanggung_jawab` | Toko beraktivitas yang tidak tercakup mapping penanggung jawab | tinggi |
| `perbaiki_layanan_chat` | Toko Shopee dengan `response_rate` di bawah `target_rate`-nya sendiri pada periode itu | sedang |
| `tangani_komplain` | Toko dengan komplain belum selesai tinggi di bulan terakhir; **hanya di kiriman bulanan** | sedang |
| `periksa` | Data tak lengkap: video "belum diketahui", catatan perkiraan, status tak dikenal | — |
| `tunda_penilaian` | Laba belum matang | — |
| `pertahankan` | Sehat, tanpa sinyal lain | — |

**Sengaja TIDAK di katalog, dengan ukurannya:** jam tayang live (hanya 11,6% sesi ber-GMV),
harga dan diskon (`mart_price_floor` 0 baris), pelanggan berulang (`mart_buyer_cohort` 0 baris),
keputusan iklan Lazada (ads_cost nol di seluruh level), dan apa pun di level `ad` TikTok
(revenue nol struktural). Masing-masing boleh masuk kelak bila ukurannya berubah.

Sasaran keputusan wajib **entitas yang ada di hasil hitung** (toko, produk, kampanye, video,
orang), dirujuk dengan id-nya. Model yang menyebut sasaran di luar himpunan itu, atau tindakan
yang tidak layak untuk sasarannya, **ditolak validator**. Bentuknya meniru `RekomendasiScreening`
recruitment: skema `strict` mengunci pilihan, lalu disaring ulang di kode, karena ADR 0082
mencatat `maxLength` dan sejenisnya tidak ditegakkan keras oleh endpoint.

⛔ **`hentikan_iklan` tidak pernah layak dari ember "belum diketahui" maupun dari laba belum
matang.** Keduanya jebakan §Context yang paling mungkin menerbitkan perintah salah yang
terdengar yakin.

### §3a Keputusan soal laba memakai jendela yang sudah matang

Jendela laporan hari ini berakhir **kemarin** (2, 7, atau 30 hari), sehingga sebagian besar
settlement di dalamnya belum cair; kiriman 2026-09-25 membuktikannya dengan 0% cair. Keputusan
yang bergantung pada laba (`hentikan_iklan` dari laba, `kurangi_belanja`, `naikkan_belanja`) karena
itu dihitung atas **jendela terpisah yang bergeser mundur** sampai porsi settlement cairnya
memadai, bukan atas jendela laporan. Tanpa ini, setiap keputusan laba jatuh ke
`tunda_penilaian` dan fiturnya tampak hidup tanpa pernah memutuskan apa pun. Panjang mundur dan
ambang "memadai" ditetapkan dari data saat perencanaan (lihat task T8 di ANALISA), **bukan**
ditulis tangan di sini, sesuai ADR 0058 §4. Tindakan kebersihan data dan layanan tidak butuh
jendela ini.

### §4 Pembagian kerja: aturan menentukan kelayakan, model memilih, mengurutkan, menjelaskan

Model tidak memutuskan apakah sebuah tindakan **boleh**; ia hanya memilih di antara yang sudah
layak, mengurutkannya lintas analisa, dan menulis alasannya. Keyakinan dipasang backend per
tindakan (tabel §3), **bukan** dinilai model sendiri.

### §5 Model tetap tidak menerima angka mentah

ADR 0120 §4 **tidak** digantikan. Masukannya hasil hitung backend beserta penandanya: status
matang/belum matang, `roas` null berarti tak terhitung, catatan perkiraan, ambang yang berlaku.
Satu panggilan per **kiriman**, bukan per analisa: menyatukan analisa adalah separuh nilai
tambahnya, dan overhead ~2.030 token dibayar sekali.

### §6 Tiap keputusan membawa alasan yang merujuk bukti

Minimal: tindakan, sasaran (id), alasan yang merujuk field hasil hitung, dan keyakinan dari §3.
Keputusan tanpa rujukan bukti ditolak, pola yang sama dengan screening CV yang menolak hasil
tanpa butir kecocokan berbukti.

### §7 Gagal menurunkan mutu, tidak menahan kiriman

Keputusan dirakit **sebelum** notifikasi dikirim, dengan batas waktu per kiriman, karena
keputusan harus sampai di notifikasi yang sama; notifikasi susulan berarti dua pesan untuk satu
laporan. Bila model gagal, habis waktu, atau seluruh keluarannya ditolak validator, laporan
**tetap terkirim** dengan `Ringkasan` yang ditulis kode, bagian keputusannya menyatakan terang
bahwa keputusan AI tidak tersedia kali ini, `narasi_status` = `gagal`, dan percobaannya masuk
`NarasiJejak`. Tanpa retry di dalam tik yang sama.

### §8 Jawaban orang dicatat per keputusan

Dijalankan atau ditolak, oleh siapa, kapan, dan alasan tolak opsional. Tanpa catatan ini
keputusan AI tidak bisa dinilai sama sekali, dan fitur yang tak bisa dinilai hidup selamanya.

### §8b Satu laporan gabungan untuk semua penerima

Keputusan pemilik produk 2026-09-25: **tidak dipisah per pembaca**. Semua penerima menerima
laporan yang sama dan melihat seluruh isinya, supaya Direktur dan tiap SPV membaca gambaran yang
sama dan tahu apa yang diminta dari tim lain. Karena satu laporan melayani dua jenis pembaca,
urutannya yang membedakan, bukan isinya:

1. **Status keputusan periode sebelumnya, per tim**: dijalankan, ditolak, belum dijawab. Bagian
   yang paling dibutuhkan Direktur, jadi paling atas.
2. **Keputusan utama**: paling banyak lima keputusan dengan dampak rupiah terbesar lintas tim,
   ditambah keputusan yang hanya dapat diambil Direktur (misalnya penegasan target ROAS).
3. **Keputusan per tim**: seluruh keputusan layak lainnya, dikelompokkan per tim lalu per
   penanggung jawab, supaya tiap SPV langsung menemukan bagian timnya.

Kekerapan kiriman gabungan **mingguan** di awal pekan (bulanan tetap boleh); **bukan** dua
harian, karena jendela pendek selalu tampak rugi (ADR 0120 §Realisasi).
Empat syarat berlaku untuk seluruh isi:

1. **Pelaksana disebut.** Tiap keputusan membawa penanggung jawab sasarannya dari mapping
   penanggung jawab. Sasaran tanpa penanggung jawab menerbitkan `tetapkan_penanggung_jawab`
   lebih dulu, bukan keputusan yang tak punya pelaksana.
2. **Dampak berupa fakta yang sudah terjadi, bukan ramalan.** Belanja dan laba matang sasaran
   pada jendela §3a boleh dikutip; proyeksi hasil tindakan tidak boleh (ADR 0120 §5, R² 0,258).
3. **Tindak lanjut periode sebelumnya** (bagian 1 di atas) dihitung dari keputusan kiriman
   sebelumnya pada jadwal yang sama. Ini menuntut pembacaan hasil lama per `jadwal_id`, yang **belum ada**
   (`hasil_analisa_store.go` hanya `DaftarHasil` tanpa filter, `jadwal_id` tak pernah di-query).
4. **Bahasa bisnis, angka sama dengan layar.** Istilah teknis diterjemahkan ("uang belum cair",
   bukan `belum_matang`), dan tautan tiap keputusan membuka layar pada periode yang sama dengan
   angka yang dibekukan.

Konsekuensi yang diterima sadar: tiap SPV melihat angka dan keputusan tim lain. Ini sejalan
dengan keadaan hari ini, karena endpoint angka laba memang terbuka untuk siapa pun yang login
(ADR 0120 §Realisasi, issue bip-erp #2008); bila kelak #2008 memutuskan menutupnya, bentuk
gabungan ini wajib ditinjau ulang.

### §8a Mode bayangan sebelum sampai ke semua penerima

Selama **1-2 pekan pertama** di produksi, bagian keputusan hanya dikirim ke **pemilik produk**;
penerima lain tetap menerima laporan seperti sekarang (`Ringkasan`). Pemilik produk menjawab tiap
keputusan jalankan/tolak dengan alasan, sehingga keputusan yang keliru ditemukan oleh orang yang
bisa memperbaikinya, bukan pertama kali terbaca oleh Direktur. Keputusan dibuka ke semua penerima
hanya bila pemilik produk menyatakannya layak berdasarkan jawaban-jawaban itu; bila tidak,
katalog §3 atau jendela §3a diperbaiki dulu dan mode bayangan diulang. Penerima bayangan adalah
daftar eksplisit pada kiriman (ADR 0120 §6), bukan diturunkan dari peran.

### §9 Kondisi berhenti pengganti ADR 0120 §7

Dinilai 30 hari sejak keputusan pertama dibuka ke **semua** penerima (sesudah §8a):
- **Nol keputusan dijawab** → keputusan AI dimatikan, laporan kembali ke `Ringkasan` saja.
- **Lebih dari separuh keputusan yang dijawab ditolak** → katalog §3 dan syarat kelayakannya
  ditinjau sebelum berjalan lagi.

### §10 Prasyarat keputusan manajemen: satu target ROAS

`kurangi_belanja` dan `naikkan_belanja` bergantung pada ambang ROAS. Sistem hanya menyimpan
satu (`mart_ambang` `global`, `roas_min` 4,5, terukur prod 2026-09-25), tetapi KPI Leader memakai
3,2. Yang dibutuhkan karena itu bukan menetapkan angka dari nol, melainkan **penegasan
manajemen** bahwa 4,5 yang berlaku untuk keputusan (gerbang G2 di
[[ANALISA - Asisten Analisa Marketing]]). Sampai ditegaskan, kedua tindakan itu **tidak
diterbitkan**. Tindakan lain di §3 tidak bergantung pada ambang ROAS dan boleh berjalan lebih
dulu.

## Consequences

**Risiko yang diterima sadar.** `naikkan_belanja` berdiri di atas hubungan belanja ke laba yang
lemah (R² 0,258). Pagarnya: tanpa besaran rupiah, keyakinan selalu "terbatas", dan tingkat
tolaknya diukur §9. Bila tingkat tolak tindakan ini jauh di atas yang lain, itu tanda katalognya
yang salah, bukan pembacanya.

**Env baru di marketing-analytics.** `AI_BASE_URL`, `AI_API_KEY`, `AI_MODEL`, `AI_TIMEOUT` wajib
dideklarasikan di blok marketing-analytics compose prod dan dev. Env dibaca saat container
**dibuat**, jadi deploy menuntut `--force-recreate`, bukan `restart`. Ini juga deploy pertama
klien AI di mana pun (ADR 0082), jadi satu kiriman sungguhan wajib dipicu sebagai bukti, dan
model yang tercatat di `NarasiJejak` dibaca dari balasan, bukan dari konfigurasi.

**Perubahan kontrak `hasil_analisa`.** Field keputusan baru berarti **BE sebelum FE**; layar yang
ada tetap aman karena `narasiTampil` jatuh ke `ringkasan` saat status bukan `siap`. Dua PR
erp-frontend sedang menyentuh `src/features/marketing-analytics/`; tombol jalankan/tolak wajib
dikoordinasikan dengan keduanya.

**Pemakai ketiga klien AI.** ADR 0082 menahan kuota dan cache sampai pemakai ketiga, dan ini
pemakai ketiganya. Cache tidak berguna di sini (tiap kiriman unik); kuota cukup berbentuk satu
panggilan per kiriman per jatuh tempo tanpa retry. Abstraksi kuota lintas service tetap tidak
dibangun sampai ada kebutuhan yang terukur.

**Ongkos wajib diukur pekan pertama** dari `NarasiJejak` (`prompt_tokens`, `completion_tokens`,
`latency_ms`) dikali jumlah kiriman per pekan, lalu dicatat di dok service.

## Realisasi (2026-09-27, susulan diukur 2026-09-28)

Dua belas PR bip-erp (enam PR awal 2026-09-25 + enam PR susulan 2026-09-27/28), seluruhnya merged ke `main` (commit terakhir `cc460f15`, diukur 2026-09-28), **belum di-deploy**. Mekanisme lengkap: [[Microservices - Marketing Analytics Service]] § Asisten Analisa.

| Task | PR | Isi |
|---|---|---|
| T8 | [#2085](https://github.com/bip-itteam-internal/bip-erp/pull/2085) | Katalog sepuluh tindakan + kelayakannya, tanpa AI |
| T9 | [#2087](https://github.com/bip-itteam-internal/bip-erp/pull/2087) | Skema, penyusun masukan, validator keputusan AI |
| T10a | [#2093](https://github.com/bip-itteam-internal/bip-erp/pull/2093) | Keputusan berbasis aturan dihitung & disimpan per kiriman, tanpa AI |
| T10b | [#2101](https://github.com/bip-itteam-internal/bip-erp/pull/2101) | Panggilan model per kiriman, saklar bawaan mati |
| T12a | [#2104](https://github.com/bip-itteam-internal/bip-erp/pull/2104) | Mode bayangan §8a: pesan ke penerima bayangan |
| T11-BE | [#2109](https://github.com/bip-itteam-internal/bip-erp/pull/2109) | `GET`/`POST /keputusan-kiriman` (baca + jawab jalankan/tolak), status kiriman sebelumnya |
| — | [#2114](https://github.com/bip-itteam-internal/bip-erp/pull/2114) | CS SLA & komplain tersambung ke perakitan keputusan (menutup butir h) |
| — | [#2118](https://github.com/bip-itteam-internal/bip-erp/pull/2118) | Status kiriman sebelumnya dirinci per tim (menutup butir g) |
| — | [#2119](https://github.com/bip-itteam-internal/bip-erp/pull/2119) | Loop belajar langkah 1: riwayat jawaban per jenis tindakan |
| — | [#2125](https://github.com/bip-itteam-internal/bip-erp/pull/2125) | `kekerapan_tersedia` berhenti menawarkan `dua_harian` |
| — | [#2126](https://github.com/bip-itteam-internal/bip-erp/pull/2126) | Gerbang ROAS dibuka + `pertahankan` diterbitkan (menutup butir a & "belum bergerak") |
| — | [#2128](https://github.com/bip-itteam-internal/bip-erp/pull/2128) | `GET /keputusan-kiriman` membawa `label_tindakan` & `status_keputusan` |

FE erp-frontend: layar keputusan [#1763](https://github.com/bip-itteam-internal/erp-frontend/pull/1763), pesan galat i18n [#1767](https://github.com/bip-itteam-internal/erp-frontend/pull/1767), kartu radio kekerapan [#1774](https://github.com/bip-itteam-internal/erp-frontend/pull/1774), tab Hasil analisa satu laporan [#1776](https://github.com/bip-itteam-internal/erp-frontend/pull/1776), unduh PDF [#1778](https://github.com/bip-itteam-internal/erp-frontend/pull/1778): seluruhnya **merged**.

**Tempat keputusan bergeser dari ADR ini saat implementasi** — keputusan pemilik brief selama loop, bukan penyimpangan diam-diam:

a. **Katalog sepuluh tindakan diturunkan penuh (`keputusan_katalog.go`), dan `pertahankan` KINI diterbitkan (PR [#2126](https://github.com/bip-itteam-internal/bip-erp/pull/2126), merged 2026-09-27).** Butir a versi sebelumnya ("tetapi `pertahankan` belum diterbitkan") **sudah tidak berlaku**. `kelayakanPertahankanKiriman` (`keputusan_kelayakan.go:897`) dipanggil **paling akhir** di orkestrator (`HimpunanKeputusanKiriman`, `keputusan_orkestrator.go:198`), sesudah SELURUH ember lain mengisi hasil — syarat "tanpa sinyal lain" diperiksa atas `ShopID` seluruh keputusan yang sudah terkumpul sejauh itu (parameter `out`); memanggilnya lebih awal akan membuat toko yang belakangan ternyata bermasalah sudah kadung ditandai `pertahankan`. Hanya toko berstatus **SEHAT** (`statusVonis`, fungsi yang sama dengan Beranda) tanpa keputusan lain di kiriman itu yang menerbitkannya, dan **hanya level toko** (dikunci `keputusan_kelayakan_test.go:776`). `pertahankan` **tak pernah** menempati lima keputusan utama: `posisiUtamaKeputusan` (`keputusan_kirim_bayangan.go:900`) mengecualikan `TindakanPertahankan` secara struktural dari hitungan "utama" — fungsi yang sama dipakai pesan bayangan (`bagiUtamaSisanya`) **dan** field `utama` di `GET /keputusan-kiriman` (`keputusan_kiriman_handler.go:131`), sehingga kedua konsumen tak bisa berbeda pendapat.
b. **Jendela matang §3a memakai lag TERUKUR per channel, bukan satu angka ditulis tangan**: diukur dari kurva cair `mart_profit_attribution` produksi 75 hari — Shopee 10 hari, TikTok 35 hari (`LagMatangHari`, `keputusan_jendela_matang.go`), batas mundur pencarian 42 hari (35 + buffer 7 hari bolong sync). Sebabnya: `settlement_belum_matang` **tidak pernah** `true` di level campaign (TikTok 0/6.987, Shopee 0/620) maupun video (0/393.686) — flag itu tak bisa dipakai menilai kematangan di level itu, jadi dipakai UMUR baris (Date + Channel) sebagai gantinya.
c. **Keputusan disimpan di koleksi BARU `keputusan_kiriman`**, bukan menambah field ke `hasil_analisa` — satu dokumen per kiriman, index `{jadwal_id:1, dibuat_pada:-1}` (`index.go`).
d. **Identitas sasaran (nama, toko, bukti, keyakinan) dipasang KODE dari himpunan T8/T9**; model (T10b) hanya memilih, mengurutkan, dan menulis kalimat alasan — persis ADR §4, tidak melebar.
e. **Pelaksana dicari lewat `k.ShopID`** (bukan `EntityID`, yang untuk product/campaign/video bukan id toko) terhadap indeks penanggung jawab, dengan **empat label jujur** (`keputusan_kirim_bayangan.go`): "belum ditetapkan" (toko ada, mapping tak menemukan pemegang), "sasaran bukan satu toko" (portofolio/agregat lintas toko), "data penanggung jawab tidak terbaca" (indeks gagal dimuat), "perlu ditentukan pemilik laporan" (sasaran `periksa` atas seorang Account Specialist — bukan orang itu sendiri yang jadi pelaksana).
f. **Agregasi status kiriman sebelumnya (§8b butir 1) memakai aturan "TOLAK MENANG"**: begitu ADA satu penerima bayangan yang jawaban terakhirnya "tolak" untuk sebuah keputusan, statusnya "ditolak" — tak peduli berapa banyak atau siapa yang menjawab "jalankan", dan tak peduli urutan waktu (`statusKeputusanTerakhir`, `keputusan_kirim_bayangan.go`). Ini koreksi dari percobaan pertama ("jawaban paling baru menang"), yang bisa membalik status jadi "dijalankan" semata karena urutan mengetik.
g. **Status kiriman sebelumnya KINI dirinci PER TIM (PR [#2118](https://github.com/bip-itteam-internal/bip-erp/pull/2118), merged 2026-09-27), menutup §8b butir 1.** Butir g versi sebelumnya ("masih satu baris total") **sudah tidak berlaku**. `statusKirimanSebelumnyaPerTim` (`keputusan_kirim_bayangan.go:565`) membalik `IndeksDivisi` (tim→toko, sumber yang sudah ada — bukan mapping baru) jadi peta toko→tim lewat `petaTokoTim` (`:471`), lalu `timUntukKeputusan` (`:508`) mengelompokkan tiap keputusan ke timnya. Dua label tampung, keduanya di akhir urutan: `NamaDivisiBelumDipetakan` = "Belum dipetakan ke divisi" (toko ada, tak terpetakan ke divisi mana pun) dan `namaLintasTim` = "Lintas tim" (`:451`; keputusan tanpa satu toko tunggal, atau toko yang dipetakan ke lebih dari satu divisi sekaligus). Satu tim saja, atau indeks divisi gagal dimuat, tetap jatuh ke satu baris agregat seperti sebelumnya (`statusKirimanSebelumnya` lama tidak dihapus, dipakai sebagai fallback). Aturan TOLAK MENANG (`statusKeputusanTerakhir`) tetap SATU tempat untuk agregasi total maupun per tim.
h. **CS SLA dan komplain KINI tersambung ke perakitan keputusan (PR [#2114](https://github.com/bip-itteam-internal/bip-erp/pull/2114), merged 2026-09-27).** Butir h versi sebelumnya ("belum tersambung") **sudah tidak berlaku**. `keputusan_kiriman_rakit.go` memanggil `ambilSLAChatCSTokoKaryawan`/`ambilKomplainTokoKaryawan` lewat seam `bacaSLAChatCSUntukKeputusan`/`bacaKomplainUntukKeputusan`, dengan **toko dari baris toko yang sudah tersaring lingkup kiriman** (`tokoAktif`) — bukan query baru. Komplain HANYA dibaca untuk kiriman **bulanan** (`j.Kekerapan == KekerapanBulanan`), atas **bulan kalender lengkap terakhir WIB** yang berakhir pada/sebelum `sampai` (`bulanKomplainTerakhirLengkap`); kiriman mingguan (atau `dua_harian` lama) tidak menyentuh `mart_komplain_bulanan` sama sekali — dicek di titik pembacaan, bukan hanya diserahkan ke `kelayakanTanganiKomplain`, supaya mart tak dibaca sia-sia. Galat salah satu pembaca **tidak** menggagalkan seluruh perhitungan: dicatat ke `StatusGalat`, tindakan yang bergantung padanya (`perbaiki_layanan_chat`, `tangani_komplain`) sekadar tak terbit dari kiriman itu. ⚠️ **Catatan terbuka dari PR ini, belum diputuskan pemilik produk**: pelaksana kedua tindakan CS ini diresolusi lewat `pelaksanaKeputusan` yang SAMA dengan seluruh tindakan lain — indeks penanggung jawab **ICC** (`bacaIndeksICCGabungan`/`IndeksPenanggungJawab`, dipakai bersama `rakitKeputusanKiriman`) — **bukan** lewat `cs_shop_mappings` (pemetaan CS↔toko yang justru pemilik pekerjaan CS-nya). Pelaksana yang tercantum untuk "perbaiki layanan chat"/"tangani komplain" karena itu adalah Account Specialist pemegang toko, bukan CS yang menangani toko itu; bila pelaksananya seharusnya CS, itu brief terpisah.
i. **Penerima bayangan (§8a) disimpan per jadwal** lewat field `penerima_bayangan` (`JadwalLaporan.PenerimaBayangan`, daftar eksplisit — bukan diturunkan dari peran, sesuai §8a). Pesan bayangan memakai kategori inbox yang **sudah ada** (`kategoriInboxLaporanTerjadwal`), bukan kategori baru, sehingga T12a tidak butuh deploy dua container sekaligus (beda dari gotcha kategori inbox baru di team-memory).
j. **Loop belajar langkah 1: riwayat jawaban per jenis tindakan (PR [#2119](https://github.com/bip-itteam-internal/bip-erp/pull/2119), merged 2026-09-27).** `bacaRiwayatTindakan90Hari` (`keputusan_riwayat.go`) membaca kiriman **lintas seluruh jadwal** dalam jendela **90 hari** (`jendelaRiwayatTindakan`), selain kiriman yang sedang diproses, lalu `hitungRiwayatTindakan` menjumlah `RiwayatTindakan{Dijawab, Dijalankan}` per jenis `Tindakan` lewat `statusKeputusanTerakhir` (TOLAK MENANG, satu aturan satu tempat). Riwayat baru ditampilkan bila `Dijawab >= ambangTampilRiwayatTindakan` (= **3**) — di bawah itu ditandai eksplisit `belum_cukup_riwayat`, bukan dibiarkan terbaca sebagai nol jawaban. Dipakai DUA konsumen lewat fungsi kelayakan-tampil yang sama (`riwayatTindakanCukup`): masuk payload model (hitungan saja — tanpa employee id, nama, atau teks alasan) dan **satu baris tambahan** di pesan bayangan ("Riwayat: keputusan sejenis ditolak X dari Y kali.") hanya untuk keputusan utama yang jenisnya melewati ambang. **Tidak mengubah kelayakan, keyakinan, katalog, jendela matang, maupun saklar ROAS** — ini "langkah 1"; penyesuaian otomatis dari riwayat adalah langkah 2, belum dikerjakan. Kontrak `GET /keputusan-kiriman` tidak berubah oleh PR ini.
k. **`GET /keputusan-kiriman` kini membawa `label_tindakan` dan `status_keputusan` (PR [#2128](https://github.com/bip-itteam-internal/bip-erp/pull/2128), merged 2026-09-28), field lama tidak berubah.** `label_tindakan` = label bahasa-bisnis dari `labelTindakan` (`keputusan_kirim_bayangan.go`), **satu sumber** dengan pesan bayangan/`kalimatPerintah`; tindakan katalog yang belum punya entri label jatuh ke kalimat jujur (`labelTindakanTanpaEntri`), bukan token mentah, di API maupun pesan bayangan. `status_keputusan` = status GABUNGAN satu keputusan atas SELURUH penerima bayangan (bukan jawaban satu orang — beda dari `jawaban_saya`/`ringkasan_jawaban` yang sudah ada), tiga nilai tetap: `"dijalankan"` / `"ditolak"` / `"belum_dijawab"`, hanya MENAMAI `statusKeputusanTerakhir` (aturan TOLAK MENANG yang sama dipakai status kiriman sebelumnya di butir g), bukan salinan aturan.

**FE erp-frontend, seluruhnya konsumen kontrak di atas:**

l. **Pesan galat layar Keputusan lewat i18n, bukan kalimat axios mentah (PR [#1767](https://github.com/bip-itteam-internal/erp-frontend/pull/1767), merged 2026-09-27).** `/marketing-analytics/keputusan` sebelumnya menampilkan "Network Error"/"Request failed with status code 500" apa adanya saat backend tak mengirim `response.data.error`; sekarang jatuh ke `t("marketing.keputusan.galatMuat")`. Berlaku juga untuk toast galat saat menjawab (POST).
m. **Kekerapan jadwal jadi kartu radio Mingguan/Bulanan (bip-erp PR [#2125](https://github.com/bip-itteam-internal/bip-erp/pull/2125) + erp-frontend PR [#1774](https://github.com/bip-itteam-internal/erp-frontend/pull/1774), merged 2026-09-27/28).** `kekerapan_tersedia` di `GET /jadwal-laporan` kini persis **`["mingguan", "bulanan"]`** — "Tiap 2 hari" dicabut dari daftar tawaran, TAPI `KekerapanDuaHarian` tetap dikenali `kekerapanDikenal`, penjalan, dan `hitungJatuhTempo`, supaya jadwal LAMA berkekerapan itu tidak patah diam-diam (prod 2026-09-28: nol jadwal `dua_harian`, menurut catatan PR #2125). Sheet Jadwal Laporan merender kartu radio dari `kekerapan_tersedia` milik backend (bukan daftar tulis tangan); jadwal warisan ber-`dua_harian` tetap tampil terpilih (nonaktif) dan tetap bisa disimpan tanpa mengganti kekerapannya, tetapi jadwal BARU wajib memilih dari daftar.
n. **Tab Hasil analisa jadi satu laporan per kiriman (angka, diagram, keputusan AI) + unduh PDF A4 berkop (erp-frontend PR [#1776](https://github.com/bip-itteam-internal/erp-frontend/pull/1776) dan [#1778](https://github.com/bip-itteam-internal/erp-frontend/pull/1778), merged 2026-09-28).** Langkah berikutnya, bentuk sajian yang dipilih AI (blok teks/angka/tabel/bar/line atas dataset backend): [[ADR - 0132 Sajian Laporan Asisten Analisa Berupa Blok Terstruktur, AI Memilih Bentuk, Angka dari Backend]]. Tab kini satu kartu per laporan (dikelompokkan `jadwal_id` + periode): kepala laporan, angka utama, tiga diagram (laba harian, tren bulanan, komposisi keputusan — memakai `label_tindakan`/`status_keputusan` dari butir k), keputusan AI kiriman yang sama (utama dulu sesuai urutan backend, lalu per pelaksana), dan rincian per analisa. Tombol Jalankan/Tolak hanya untuk penerima bayangan jadwal itu; pembaca lain melihat keputusan dan statusnya hanya-baca. Unduh PDF membuka dokumen cetak A4 (`window.print`, `@page A4`, tanpa pustaka PDF baru) berkop resmi: identitas laporan, ringkasan eksekutif, keputusan utama bernomor, diagram bernomor, rincian per analisa, lampiran keputusan lainnya, dan kaki halaman — datanya dari fungsi `lib/` yang SAMA dengan layar. Layar Keputusan mandiri (`/marketing-analytics/keputusan`, butir l di atas) tidak berubah.

**Yang sudah bergerak sejak 2026-09-27, menutup "Yang belum bergerak dari ADR" versi sebelumnya**: gerbang ROAS KINI dibuka (PR [#2126](https://github.com/bip-itteam-internal/bip-erp/pull/2126)). Direktur menegaskan target ROAS **TUNGGAL 4,5**, disampaikan pemilik produk **2026-09-27**, jadi `GerbangROASDitegaskan = true` (`keputusan_katalog.go:140`) dan `kurangi_belanja`/`naikkan_belanja` kini bisa terbit. Angka ambangnya sendiri **tidak ditulis di kode ini** — tetap dibaca dari `mart_ambang` (dokumen `global`, field `roas_min`) lewat layar Ambang yang sudah ada (§10 tidak digantikan, hanya ditutup); mengubah target ROAS di kemudian hari cukup menyunting `mart_ambang` lewat layar itu, tanpa menyentuh `keputusan_katalog.go` maupun deploy ulang.

**Status prod (2026-09-28, bertanggal — ukur ulang sebelum dipakai; bukan diverifikasi lewat `git grep`, melainkan dilaporkan pemilik brief).** Saklar `MARKETING_ANALYTICS_AI_KEPUTUSAN_ENABLED=true` di PROD; penerima bayangan jadwal BH dan KY-GB adalah **Irfan Arfianto** dan **Kukuh Adafi Septya Rizki**. Seluruh PR yang merged 2026-09-28 (butir k, sebagian m) **belum ter-deploy** saat sync ini ditulis, konsisten dengan seluruh PR bip-erp lain di atas.

## Terkait

- [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]]
- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]]
- [[ADR - 0082 Integrasi AI lewat Klien Tipis di Shared-Library]]
- [[Microservices - Marketing Analytics Service]]
- [[ANALISA - Asisten Analisa Marketing]]
- [[ADR - 0132 Sajian Laporan Asisten Analisa Berupa Blok Terstruktur, AI Memilih Bentuk, Angka dari Backend]]
