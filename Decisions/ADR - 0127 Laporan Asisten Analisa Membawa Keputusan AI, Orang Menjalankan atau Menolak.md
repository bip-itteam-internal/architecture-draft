# ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak

> **Status**: 🟡 **Diusulkan** — diputuskan 2026-09-25, kode belum ada. Menggantikan [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]] §5 dan §7, serta [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] §5 **khusus untuk laporan Asisten Analisa Marketing**.

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

### §9 Kondisi berhenti pengganti ADR 0120 §7

Dinilai 30 hari sejak laporan berkeputusan pertama terkirim di produksi:
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

## Terkait

- [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]]
- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]]
- [[ADR - 0082 Integrasi AI lewat Klien Tipis di Shared-Library]]
- [[Microservices - Marketing Analytics Service]]
- [[ANALISA - Asisten Analisa Marketing]]
