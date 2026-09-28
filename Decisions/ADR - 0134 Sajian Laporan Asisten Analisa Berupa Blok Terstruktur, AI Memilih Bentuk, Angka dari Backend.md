---
tags: [adr, marketing-analytics, ai, frontend]
status: Accepted
tanggal: 2026-09-28
---

# ADR - 0134 Sajian Laporan Asisten Analisa Berupa Blok Terstruktur, AI Memilih Bentuk, Angka dari Backend

> **Status**: ⚠️ **Implemented (ada catatan)** — diukur 2026-09-28. §1 (katalog dataset beku per kiriman) dan §2 (model memilih jenis+urutan blok) **merged** ke `origin/main` bip-erp lewat dua PR (§ Realisasi di bawah), **BELUM deploy prod** — saklar dan status deploy sama dengan [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]] (satu mekanisme, satu panggilan model, satu saklar `MARKETING_ANALYTICS_AI_KEPUTUSAN_ENABLED`). §3 (perender FE: blok di tab Hasil analisa dan dokumen PDF) **MERGED** erp-frontend [#1784](https://github.com/bip-itteam-internal/erp-frontend/pull/1784). Melengkapi [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]] §5 dan [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]] §4; tidak menggantikan keduanya.

## Context

Laporan Asisten Analisa hari ini menyajikan keputusan AI sebagai kalimat, sementara angka dan diagram di tab Hasil analisa disusun tetap oleh FE. Pemilik produk meminta laporan yang **memutuskan bentuk penyajian yang paling cocok**: angka tunggal cukup teks, daftar atau perbandingan jadi tabel, tren atau perbandingan antar kategori jadi chart (bar/line), dengan output berupa **data terstruktur** yang FE render sesuai jenisnya, dan chart WAJIB memakai komponen yang sudah ada di erp-frontend (ChartContainer + Recharts beserta aturan bakunya), bukan sistem chart baru.

Tiga bagian contoh tampilan yang disetujui pemilik produk belum bisa ditampilkan karena datanya tidak dikirim backend: tindak lanjut kiriman sebelumnya per tim (hanya ada di pesan bayangan), revenue dan belanja iklan per toko (hasil_analisa hanya menyimpan total), dan pembanding periode sebelumnya.

Batas yang tetap berlaku: model **tidak menerima dan tidak menulis angka mentah** (ADR 0120 §4, ADR 0127 §5), rules menentukan kelayakan (ADR 0127 §4), dan angka yang dibekukan saat kiriman tidak berubah arti belakangan.

## Decision

### §1 Satu kiriman membawa `sajian`: daftar blok + katalog dataset

Tiap dokumen `keputusan_kiriman` membawa `sajian`, dibekukan saat kiriman dibuat (angka tidak dihitung ulang saat dibaca):

- **`dataset`**: peta `id → dataset` yang **dihitung backend**. Tiap dataset memuat judul (bahasa bisnis), satuan (`rupiah` | `rasio` | `persen` | `jumlah` | `skor`), `bentuk_diizinkan` (subset `angka` | `tabel` | `bar` | `line`), definisi kolom/seri berlabel, baris data, dan ambang bila ada (mis. target ROAS dari `mart_ambang`).
- **`blok`**: daftar berurutan `{jenis, judul, kalimat?, dataset_id?}` dengan `jenis` ∈ `teks` | `angka` | `tabel` | `bar` | `line`. Blok `teks` hanya membawa kalimat; blok lain WAJIB merujuk `dataset_id` yang ada dan `jenis`-nya harus termasuk `bentuk_diizinkan` dataset itu.
- **`sumber_susunan`**: `aturan` | `model`.

Katalog awal: angka utama laporan, laba harian, ROAS per pekan dengan garis target, revenue dan belanja iklan per toko, pembanding periode sebelumnya, keputusan per jenis tindakan, status keputusan, tindak lanjut kiriman sebelumnya per tim. Katalog boleh tumbuh: satu dataset = satu penghitung backend + uji.

### §2 AI memilih bentuk dan urutan; tidak pernah menulis angka

Model menerima **daftar dataset beserta metadatanya** (id, judul, satuan, bentuk_diizinkan, ringkasan hasil hitung yang sudah boleh ia terima menurut ADR 0127 §5), lalu mengembalikan urutan blok, jenis tiap blok, dan kalimat penjelas. Model **tidak** mengembalikan angka, baris, atau seri. Validator menolak blok yang merujuk dataset tak dikenal, jenis di luar `bentuk_diizinkan`, atau kalimat yang memuat angka yang tidak ada di ringkasan hasil hitung. Model gagal, habis waktu, atau seluruh bloknya ditolak → **susunan bawaan dari aturan** (`sumber_susunan: aturan`) yang selalu tersedia, sehingga laporan tidak pernah kosong.

Aturan pemilihan bentuk yang dipakai susunan bawaan dan dijadikan instruksi model: satu nilai → `angka`; daftar atau perbandingan beberapa atribut → `tabel`; tren waktu → `line`; perbandingan antar kategori → `bar`.

### §3 FE hanya perender, memakai komponen yang sudah ada

- `teks`/`angka`: komponen teks dan kartu angka yang ada; `tabel`: tabel yang ada; `bar`/`line`: `ChartContainer` (`components/ui/chart.tsx`) + Recharts dengan aturan baku tim (team-memory § Bagan/chart): warna `theme:{light,dark}` dari `--fb-seri-*`/`WARNA_BAGAN` (bukan `--chart-1..5`, bukan hex), `domain={[0,100]}` untuk satuan `skor`, `connectNulls={false}`, `type="monotone"`, deret kosong disembunyikan diganti satu kalimat, legend berlabel, garis ambang hanya bila dataset membawa ambang.
- Format angka di render dengan `intlLocale(lang)` sesuai `satuan`; label dari backend apa adanya.
- Dokumen PDF A4 memakai perender blok yang sama.
- Blok yang tak dapat dirender (jenis/dataset tak dikenal oleh FE lama) dilewati diam dan dicatat, bukan menjatuhkan halaman.

### §4 Satu fakta satu tempat

Rumus tiap dataset hidup di backend; FE tidak menghitung ulang total, rasio, atau status. Status keputusan tetap `statusKeputusanTerakhir` (TOLAK MENANG), label tindakan tetap `labelTindakan`.

## Consequences

- Kontrak `GET /keputusan-kiriman` bertambah field `sajian` (aditif). **BE sebelum FE**; FE tanpa `sajian` jatuh ke tampilan yang ada hari ini.
- Dokumen `keputusan_kiriman` membesar (dataset beku). Dataset dibatasi jumlah baris (mis. per toko teratas N) dan dicatat di dok service.
- Kiriman yang dibuat sebelum ADR ini tidak punya `sajian`; layar menampilkan tampilan lama untuknya.
- Pemanggilan model per kiriman tetap satu (ADR 0127 §5): pemilihan blok digabung ke panggilan keputusan yang sama, bukan panggilan kedua.

## Realisasi (2026-09-28)

Dua PR bip-erp, keduanya merged ke `origin/main` (diukur 2026-09-28), **belum deploy prod**. Satu PR erp-frontend, merged. Mekanisme lengkap (struct, validator, fungsi perakit): `services/marketing-analytics/sajian.go`, `keputusan_ai_sajian.go`, `keputusan_ai_skema.go`, `keputusan_ai_validator.go`, `keputusan_ai_panggil.go`.

| Task | PR | Isi |
|---|---|---|
| BE-1 | [#2140](https://github.com/bip-itteam-internal/bip-erp/pull/2140) | Katalog dataset beku per kiriman + susunan blok aturan (§1) |
| BE-2 | [#2144](https://github.com/bip-itteam-internal/bip-erp/pull/2144) | Model memilih jenis dan urutan blok, angka dan teks tetap dari backend (§2) |
| FE | erp-frontend [#1784](https://github.com/bip-itteam-internal/erp-frontend/pull/1784) | Perender blok di tab Hasil analisa dan PDF (§3) |

**BE-1 (`sajian.go`) — katalog dataset beku:**

a. **Delapan id dataset tetap** (`DatasetID*`): `angka_utama` (1 baris: laba kotor, revenue, belanja iklan, net settlement, ROAS, porsi cair; ambang target ROAS terlampir dari `mart_ambang` bila terbaca), `banding_periode_lalu` (revenue/belanja iklan/ROAS/laba kotor, periode ini vs periode sebelumnya), `laba_harian` (per tanggal, kolom `belum_cair` boolean), `roas_per_pekan` (SELALU 8 baris, Senin–Minggu WIB, ambang `roas_min`), `per_toko` (maks **15** baris, diurut revenue menurun), `keputusan_per_jenis` (per jenis tindakan: label bisnis + jumlah), `status_keputusan`, `tindak_lanjut_sebelumnya` (per tim, struktur sama dengan baris status per tim pesan bayangan ADR 0127 §8b). Susunan blok aturan (bila datanya ada): teks Ringkasan → angka `angka_utama` → tabel `banding_periode_lalu` → bar `laba_harian` → line `roas_per_pekan` → tabel `per_toko` → bar `keputusan_per_jenis`; `tindak_lanjut_sebelumnya` ditambahkan terpisah oleh penjalan (butuh dokumen kiriman sebelumnya, tak tersedia saat perakitan utama).
b. **Dua satuan kolom baru, di luar enam satuan lama.** `ikut_baris` (kolom yang satuannya ditentukan field `"satuan"` pada BARIS itu sendiri, bukan satu satuan tetap untuk seluruh kolom) — dipakai `banding_periode_lalu` karena satu tabel mencampur baris rupiah (revenue, belanja iklan, laba kotor) dan baris rasio (ROAS); tanpa ini kolomnya terpaksa `jumlah` dan FE tak tahu memformat "Rp" atau "x". `penanda` (boolean murni, bukan teks bebas) — dipakai `laba_harian.belum_cair`. Kolom ber-satuan ini tidak boleh dipakai sebagai `seri` atau `sumbu_x` (bar/line butuh satu skala tunggal), ditegakkan `validasiDatasetSajian`.
c. **`porsi_cair` memakai definisi jendela matang §3a (ADR 0127), bukan NetSettlement/Revenue.** Koreksi dari judge percobaan 1 (KRITIS): rumus awal (`porsiPersen(NetSettlement, Revenue)`) sebenarnya menghitung porsi fee marketplace yang terpotong (ongkir, komisi) — toko yang **sudah matang penuh** tetap ber-NetSettlement < Revenue karena potongan itu selalu ada, sehingga rumus lama melaporkan porsi cair ~39% untuk toko yang sebenarnya 100% matang. Yang benar: porsi **revenue** dari baris yang tidak bertanda `SettlementBelumMatang`, dihitung lewat fungsi jendela matang yang sudah ada (`ringkasLabaJendela`), bukan rumus kedua.
d. **Catatan dataset berbahasa bisnis, satu kalimat per jenis alasan, maks 4 kalimat.** Alasan mentah (`CatatanPerkiraan`) unik per toko-hari sehingga mendedup string persis bisa meledak jadi puluhan kalimat nyaris identik (preseden: kelas masalah yang sama melahirkan `catatan_perkiraan_ringkas.go` di badan kiriman). Sajian mengelompokkan alasan per jenis dan menerbitkan tepat satu kalimat per jenis (`susunCatatanBisnisPerkiraan`), dibatasi 4 kalimat (`batasKalimatCatatanPerkiraan`); sisanya diringkas satu kalimat penutup "Ada N alasan perkiraan lain."
e. **Dua dataset (`banding_periode_lalu`, `roas_per_pekan`) melakukan pembacaan Mongo baru** (rentang periode sebelumnya dan 8 pekan mundur), memakai reader yang sudah ada (`bacaProfitPenuh` + filter lingkup kiriman) dengan rentang berbeda — bukan loader baru. Masing-masing dibungkus **anggaran waktu sendiri 5 detik** (`anggaranPembacaanSajianBaru`), terpisah dari anggaran 60 detik keseluruhan perakitan kiriman: tanpa ini satu sumber lambat pada salah satu pembacaan bisa menghabiskan anggaran 60 detik itu sendirian dan menggagalkan seluruh kiriman, termasuk keputusan yang sama sekali tak bergantung padanya. Galat pada satu dataset (dua pembacaan baru ini) tidak menggagalkan sajian maupun dataset lain — dataset dan bloknya dibuang, galatnya masuk `StatusGalat` kiriman.
f. **`status_keputusan` dan `keputusan_per_jenis` DIHITUNG ULANG tiap `GET /keputusan-kiriman`, tidak dibekukan** — satu-satunya dua dataset yang begitu; dataset lain (angka_utama, laba_harian, dst.) tetap beku persis seperti saat kiriman dibuat. Alasannya kelas yang sama dengan "status yang bergerak jangan disimpan sebagai fakta": TOLAK MENANG (ADR 0127 §8b butir f) bisa berubah begitu seseorang menjawab sesudah kiriman terbit, dan angka yang dibekukan saat dibuat akan berbunyi "belum dijawab" selamanya walau sudah dijawab. `keputusan_per_jenis` dihitung ulang atas **daftar keputusan yang SAMA dengan yang tampil di baris `keputusan` respons yang sama** (`susunDaftarKeputusanBayangan`) — termasuk `KeputusanModel` (subset pilihan model, bukan seluruh keputusan aturan) saat `StatusModel == siap`; tanpa penyamaan ini bagan "keputusan per jenis" bisa menghitung keputusan yang tak tampil di daftar pada layar yang sama.

**BE-2 (`keputusan_ai_sajian.go`, `keputusan_ai_skema.go`) — model memilih jenis dan urutan:**

g. **Model hanya mengirim `{jenis, dataset_id}` per blok** — skema JSON strict TIDAK memuat properti `judul` atau `kalimat` sama sekali (dicoret, bukan sekadar opsional), dan tipe Go balasan model (`blokSajianAIItem`) tidak punya field itu sama sekali, sehingga kunci JSON tambahan yang mungkin tetap dikirim model otomatis dibuang `encoding/json` sebelum sampai ke memori. Judul dan kalimat blok akhir **selalu** berasal dari blok aturan untuk dataset itu (bila ada) atau metadata dataset (bila tidak ada blok aturan untuk dataset itu, kalimat dikosongkan, bukan dikarang).
h. **Jenis `teks` dikeluarkan dari enum yang ditawarkan ke model, dan blok teks dari model ditolak seluruhnya** — blok "Ringkasan" aturan selalu dipasang paling atas susunan akhir, satu-satunya teks yang mungkin tampil.
i. **Kelengkapan dataset**: dataset_id yang dirujuk blok ATURAN tapi tidak dipilih model ditambahkan di akhir susunan, blok aturan apa adanya, menjaga urutan blok model yang lolos tetap persis. Bila **tidak satu pun** blok model lolos validasi, hasilnya diperlakukan sama dengan model gagal total — sajian jatuh ke susunan aturan sepenuhnya (bukan "aturan dilabeli model").
j. **Sajian model hanya dievaluasi/diterapkan bila `StatusModel == siap`** (keputusan berhasil, minimal satu keputusan lolos validator) — ditegakkan pemanggil (`jalankanKeputusanAI`), bukan di dalam `SajianAkhirDariModel` sendiri. Saat keputusan gagal (konfigurasi AI kosong, jaringan gagal, atau seluruh keputusan model ditolak validator), sajian tetap dari aturan walau balasan JSON yang sama sempat membawa properti `sajian` yang tampak valid.
k. **Bagian `sajian` balasan model diurai TERPISAH dari bagian `keputusan`** (`hasil.Sajian` disimpan sebagai `json.RawMessage`, diurai belakangan lewat `uraiSajianAI`) — `sajian` yang bentuknya rusak (proxy AI tidak menegakkan skema dengan keras, ADR 0082) gagal urai secara diam-diam (kembali `nil`, jatuh ke aturan) TANPA menjatuhkan `json.Unmarshal` seluruh balasan, yang kalau digabung satu struct akan ikut menggagalkan keputusan yang sudah lolos.

**Penyimpangan dari teks awal ADR §2, wajib dicatat:** ADR ini semula menulis model mengembalikan "urutan blok, jenis tiap blok, **dan kalimat penjelas**". Realisasi (butir g–j di atas) **sengaja membuang judul/kalimat model sepenuhnya**, bukan cuma memvalidasinya lebih ketat. Sebabnya ditemukan lewat dua putaran judge: model hanya menerima **metadata** dataset (id, judul, satuan, bentuk_diizinkan, jumlah baris) sesuai §2, **tidak pernah baris datanya** — sehingga judul/kalimat bebas seperti "Sesuai target" atau "Lima toko teratas" adalah **penilaian tanpa dasar**, bukan sekadar risiko "angka karangan". Keputusan pemilik produk (2026-09-28): "jangan ada yang salah penyajian", opsi paling aman — model tidak lagi menulis satu karakter teks pun untuk blok non-teks. **Validator yang dicoba lebih dulu lalu dibuang**: sebelum keputusan di atas, tim sempat memasang validator berbasis pencocokan teks (`angkaKalimatDikenal`/`angkaFingerprint`) untuk menolak kalimat model yang memuat angka karangan; validator itu **bocor di banyak arah** (kalimat model bisa mengutip angka dari header riwayat yang sah, dan fingerprint-nya bisa menyamakan dua angka yang maknanya berbeda) sehingga diganti larangan-digit mutlak, yang pada gilirannya juga dibuang seluruhnya setelah keputusan final "model tak lagi mengirim teks apa pun" membuat validator teks apa pun jadi kode mati.

**§3 — erp-frontend #1784 (perender blok):**

l. **Satu komponen perender (`sajian/blok-sajian.tsx`) dipakai DUA konsumen**: tab Hasil analisa (`kartu-laporan.tsx`) dan dokumen cetak PDF (`laporan-pdf.tsx`) — satu fakta satu tempat untuk aturan render per jenis (teks/angka/tabel/bar/line). Blok bar/line dibungkus `ChartContainer` (bukan `ResponsiveContainer` telanjang) dan warnanya dari `WARNA_BAGAN`/`WARNA_AMBANG` lewat `lib/sajian-bagan.ts` (`--fb-seri-*`, mengikuti aturan tim § Bagan/chart di team-memory), bukan `--chart-1..5` maupun hex mentah.
m. **Target ROAS tampil di kartu angka utama** lewat `dataset.ambang` (kunci `roas`, label "Target ROAS" dari BE-1 butir a) — kartu kolom yang kuncinya sama dengan `ambang.kunci` menampilkan pembanding "di atas/di bawah target".
n. **Dokumen cetak memaksa bagan sajian ke varian warna terang**, walau mode gelap aplikasi sedang aktif — pola yang sama dengan bagan lama `laporan-pdf.tsx` (CSS memaksa tiap `--color-*` bagan ke token `WARNA_BAGAN`/`WARNA_AMBANG` terang lewat `!important`), diperluas ke tabel dataset sajian di dokumen yang sama (kelas CSS tabel diekstrak satu sumber, `cetak-gaya.ts`, dipakai tabel identitas/keputusan lama DAN tabel dataset sajian baru).
o. **Penomoran "Tabel N."/"Gambar N." dihitung saat render**, mengikuti bagian lain yang ada atau tidak di dokumen PDF yang sama (mis. `nomorBagianDiagram`/`nomorBagianRincian` bergeser tergantung apakah bagian diagram lama ditampilkan) — bukan nomor tertulis tangan yang bisa menyimpang dari susunan sesungguhnya.

**Catatan terbuka:**

- ⚠️ **Anggaran baca 5 detik (butir e) belum diukur di prod.** Kode menegakkannya sebagai batas waktu, tapi belum ada data latensi sungguhan atas dua pembacaan baru itu (rentang periode sebelumnya, rentang 8 pekan) di lingkungan produksi — ukur ulang sebelum mengandalkan angka itu sebagai margin aman.
- **Status prod (2026-09-28, bertanggal — ukur ulang sebelum dipakai)**: saklar `MARKETING_ANALYTICS_AI_KEPUTUSAN_ENABLED` menyala di PROD (fakta yang sama dengan [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]] § Realisasi, tidak diulang rinciannya di sini), tetapi PR sajian (BE-1 #2140, BE-2 #2144) **belum ter-deploy prod** saat dok ini ditulis — konsisten dengan seluruh PR bip-erp lain di ADR 0127 yang juga belum deploy.

## Terkait

- [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]]
- [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]]
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
- [[Microservices - Marketing Analytics Service]]
