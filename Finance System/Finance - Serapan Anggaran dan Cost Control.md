## Deskripsi

*Layar **Anggaran & Cost Control** (`/finance/anggaran`) menunjukkan per pos biaya berapa Anggaran, berapa Terpakai, dan berapa Sisa, ditambah dana yang terserap lewat Pengajuan Barang/Dana. Dok ini adalah **satu-satunya tempat** aturan membaca angka di layar itu: kolom mana bagian dari kolom mana, dan apa yang sengaja tidak dijumlahkan. Keputusan produknya ada di [[ADR - 0159 Serapan Anggaran Dibaca dari Pengajuan sebagai Bagian dari Terpakai, Rute Tulis Anggaran Digerbang Izin Sendiri]].*

- **Status**: ⚠️ Implemented (ada catatan), **kode merged ke `main` 2026-10-08, deploy prod TBD**. Catatan: belum ada layar yang dilihat di browser dan belum ada endpoint yang dicoba lewat gateway (catatan penutup bip-erp#2779, 2026-10-08); keputusan terbuka dilacak di bip-erp#2814.
- **Implementasi**: [[API - Procurement Service]] (`/pengajuan-barang/serapan-anggaran*`) · [[API - Integration Service]] (`/accounting/anggaran*`) · [[Microservices - Procurement Service]] · [[APP - Web ERP]] (layar) · izin: [[CORE - RBAC dan Permission Set]]
- **Path di repo**: `bip-erp/services/procurement/pengajuan_barang_serapan.go` · `bip-erp/services/integration/internal/domain/entity/anggaran.go` · `erp-frontend/src/features/finance/anggaran/` · `erp-frontend/src/features/pengajuan-barang/` (kotak sisa pos, kartu Anggaran) · forecast mingguan: `bip-erp/services/integration/internal/usecase/laporan_mingguan.go` + `minggu_periode.go` + `proyeksi_mingguan.go`, `internal/interface/http/anggaran_mingguan_handler.go` + `anggaran_proyeksi_handler.go` · cashflow tujuh komponen: `usecase/komponen_kas.go`, `realisasi_aset.go`, `realisasi_pajak.go`, `realisasi_material.go`, `kunci_isian.go`, `interface/http/anggaran_komponen_handler.go`, `worker/tasks/realisasi_material_refresh.go`, `bip-erp/services/finance/forecast_kas_internal.go`, `erp-frontend/src/features/finance/anggaran/lib/komponen-forecast.ts` + `isian-komponen.ts`

## Latar Belakang

- Master anggaran OPEX per **akun Accurate × departemen Accurate × bulan** sudah ada ([[Finance - Rancangan Finance Service]], pemilik data: [[REF - Kepemilikan Data]]), tetapi layarnya tidak memperlihatkan dana yang terserap lewat pengajuan, dan layar isian terkubur di dasar tab Master di bawah tiga panel laporan.
- Pengajuan Barang/Dana ([[Finance - Proses Pengajuan Pengeluaran dan Persetujuan]]) baru menjadi beban di Accurate setelah Accounting mencatatnya (jurnal terbit), jadi ada jeda antara "pengajuan lolos" dan "angka Terpakai naik".

## Ruang Lingkup (business view)

Tab di `/finance/anggaran`, urutan di layar (`tab-anggaran.ts`, array `TAB_ANGGARAN`):

| Tab | Isi |
|---|---|
| **Serapan** (bawaan) | Kartu Anggaran · Terpakai · Sisa dan kartu Menunggu dicatat; peringatan pos lewat anggaran dengan tautan **Buat rekomendasi** per pos; tabel serapan per pos (saringan Departemen dan Akun beban); tabel **Menunggu dicatat Accounting** per departemen pengaju; tombol **Rincian** per pos membuka sheet (terpakai per departemen Accurate, pengajuan pembentuknya, Jurnal lain); panel Admin & Non-Ops |
| Opex Marketing | Panel OPEX Marketing yang sudah ada; **tidak** disatukan ke Serapan |
| Rekomendasi | Pencatatan rekomendasi efisiensi (bekas `/finance/cost-control`); periodenya mengikuti Tahun/Bulan halaman, akun dari katalog |
| **Anggaran Bulanan** | Isian anggaran: unduh template, unggah Excel, tambah baris, koreksi, hapus (hapus meminta konfirmasi). `?tab=master` lama dipetakan **eksplisit** ke tab ini |
| **Forecast Mingguan** | Sejak 2026-10-19 (merged, deploy prod TBD): 4 minggu, tujuh komponen uang keluar yang bisa dibuka sampai tingkat akun, badge Akrual/Kas, kartu pembanding uang keluar riil, anggaran aset tahunan beserta sisanya, dan form isian proyeksi komponen (lihat §Cashflow Tujuh Komponen). Backend lama jatuh ke tampilan rincian per akun. Sebelumnya: ringkasan per minggu dan rincian per akun per minggu. Sejak 2026-10-09 (merged, deploy prod TBD): minggu **Berjalan** dan **Belum mulai** berpenanda, akurasi hanya dihitung atas minggu yang sudah selesai, dan baris total ringkasan berbunyi "Total minggu selesai (n dari m)" (lihat §Minggu yang Belum Selesai Tidak Dihitung); pemegang izin kelola bisa **Atur proyeksi** dan semua pembaca melihat **Riwayat perubahan** (lihat §Proyeksi Mingguan Diatur per Minggu) |

### Minggu yang Belum Selesai Tidak Dihitung (⚠️ merged 2026-10-09, deploy prod TBD)

Asal: bip-erp#2865 dan erp-frontend#2230 (PR bip-erp #2872, erp-frontend #2237).

- Sebuah minggu **selesai** begitu hari terakhirnya lewat menurut WIB. Minggu yang sedang berjalan dan yang belum mulai **tidak** punya akurasi (tampil "—", bukan 0%) dan **tidak masuk** total yang dipakai akurasi bulan maupun bahan KPI Cost Control #4.
- Baris total tabel **ringkasan** hanya menjumlahkan minggu selesai. Baris dan kolom total tabel **rincian per akun** tetap menjumlahkan semua minggu dan berlabel "(sebulan penuh)". **Kedua total itu sengaja berbeda cakupan; jangan dibandingkan atau dijumlahkan.**
- Realisasi minggu berjalan tetap tampil; realisasi minggu yang belum mulai (jurnal bertanggal maju di Accurate) tidak ditampilkan di ringkasan.
- Periode yang sudah lewat seluruhnya tidak berubah angkanya.

### Proyeksi Mingguan Diatur per Minggu (⚠️ merged 2026-10-09, deploy prod TBD)

Keputusan: [[ADR - 0161 Proyeksi Forecast Kas Mingguan Diatur Porsinya per Minggu oleh Cost Control, Jumlah Sebulan Tetap RAPB]]. Kode: PR bip-erp #2882 dan erp-frontend #2238. ⚠️ Per 2026-10-09 penyimpanannya belum diuji terhadap Mongo hidup, layarnya belum dilihat di browser, dan belum ada endpoint yang dicoba lewat gateway.

Cara kerja:

- Cost Control (pemegang `finance.anggaran.kelola`) mengetik **total rupiah per minggu**. Jumlah seluruh minggu harus sama dengan anggaran RAPB kas-keluar bulan itu, kalau tidak simpan ditolak.
- Sistem menyimpan **porsi** tiap minggu (sebagai bobot: rupiah yang diketik saat simpan, dibagi jumlahnya), bukan nominal yang dibekukan. Proyeksi tiap akun pada sebuah minggu = anggaran akun × porsi minggu itu, jadi tabel rincian per akun mengikuti tabel ringkasan. Semua akun memakai porsi yang sama.
- Minggu terkunci sejak hari pertamanya (WIB). Pergeseran hanya antar-minggu yang belum mulai.
- Tiap minggu paling banyak 2 kali diubah per periode; sekali simpan menghitung tiap minggu yang angkanya berubah.
- Riwayat perubahan (siapa, kapan, sebelum → sesudah per minggu) tampil di bawah tabel. Form isian berupa Sheet; penolakan backend (jumlah tidak sama, minggu terkunci, batas ubah) ditampilkan apa adanya. Layar tidak menghitung kunci maupun batas ubah sendiri.
- Periode tanpa isian tetap memakai pembagian menurut jumlah hari.
- Bila RAPB diunggah ulang, porsi yang tersimpan diterapkan ke anggaran baru untuk semua minggu, termasuk yang sudah terkunci. Bulan mendatang boleh diatur sebelum bulannya mulai. Tidak ada tombol kembalikan ke bawaan.

⚠️ **Jangan dibaca sebagai cara menaikkan KPI.** Akurasi bulan dan KPI Cost Control #4 dihitung dari **total** sebulan, dan total itu tidak berubah saat porsi digeser antar-minggu. Yang berubah hanya akurasi **per minggu**, dan akurasi **bulan berjalan** (karena hanya minggu selesai yang dihitung, porsi minggu-minggu awal ikut menentukan angka tengah bulan). Angka akhir bulan tidak terpengaruh.

### Cashflow Tujuh Komponen (⚠️ merged ke `main` 2026-10-19, deploy prod TBD)

Keputusan: [[ADR - 0184 Forecast Kas Mingguan Mencakup Tujuh Komponen Uang Keluar, Dibagi Empat Minggu, Realisasi Bertahap]]. ADR ini mengamandemen ADR 0161 pada tiga hal: cakupan, jumlah sebulan, dan pembagian minggu.

Kode:
- BE: bip-erp #3234 (C1); #3275, pemulihan C2–C3c karena PR bertumpuk #3236/#3258/#3260/#3262 semula merged ke branch induk, bukan `main`; #3276 (`dapat_diisi`).
- FE: erp-frontend #2570 (C4a); #2583, pemulihan C4b/#2572; #2584 (`dapat_diisi`).

Status verifikasi:
- Layar belum dilihat di browser.
- Endpoint belum dicoba lewat gateway.
- Penyegar Material belum dijalankan terhadap Accurate sungguhan.
- Verifikasi yang dijanjikan: realisasi Material September 2026 = **Rp 385.370.294** (penerimaan barang 1601 Rp 82.853.623 + 1602 Rp 302.516.671), dan layar dicocokkan dengan Excel cashflow Finance September.

Cara kerja:

- **Cakupan.** Forecast mencakup tujuh komponen uang keluar:
  - Pembelian material
  - BOP produksi (akun 5201, 5102, seluruh 53xx, dan perlengkapan produksi)
  - Beban marketing (61xx)
  - Beban gaji
  - Beban ops adum (62xx, 73xx)
  - Pajak
  - Pembelian aset

  Akun penyusutan dikecualikan. Pemetaan akun ke komponen ditulis di satu tempat di integration-service. Layar menerima komponen dari respons dan tidak memetakan sendiri.
- **Proyeksi.** ~~Operasional (marketing, gaji, adum) diambil dari RAPB tanpa penyusutan. Material, BOP, Pajak, dan Aset berasal dari isian Cost Control per komponen per bulan.~~ **Sejak 2026-10-22** (ADR 0184 Decision 2, amandemen): keenam komponen menerima isian Cost Control per bulan, dan isian **menggantikan** RAPB untuk komponen itu, termasuk BOP. RAPB menjadi bawaan bila isian kosong. Jumlah sebulan = Σ proyeksi komponen, bukan lagi = RAPB. Rincian di §Isian di bawah.
- **Aset.** Anggaran aset bersifat tahunan. Layar menampilkan sisa anggaran tahun berjalan, sedangkan total bulanan hanya memuat proyeksi aset bulan itu.
- **Minggu.** Satu bulan selalu dibagi 4 minggu. Minggu 1–3 masing-masing 7 hari dari tanggal 1, dan minggu 4 mencakup tanggal 22 sampai akhir bulan. Porsi bawaan rata ¼. Atur proyeksi tetap berlaku.
- **Realisasi bertahap.**
  - Tahap 1: Operasional dan BOP memakai mutasi akun (akrual), Pajak memakai setoran nyata, dan Aset memakai salinan aset tetap.
  - Tiap komponen ditandai `akrual` atau `kas`.
  - Tahap 2 mengganti sumber per komponen ke basis kas setelah Finance menjelaskan sumber yang mereka pakai secara manual.
- **Pembanding.** Total uang keluar riil dari seluruh rekening bank (salinan ADR 0163) tampil di samping total realisasi. ⚠️ Angka ini **tidak dipakai KPI**, dan **jangan dijumlahkan** dengan realisasi komponen karena keduanya mengukur uang yang sama dari dua sisi.
- **KPI #4.** Cost Control #4 dan SPV Finance F4 ikut definisi baru dengan rumus yang sama. Skor periode yang sudah beku tidak dihitung ulang tanpa keputusan HRD.

#### Yang benar-benar ada di kode (diukur 2026-10-19 di `origin/main`)

**Pemetaan akun ke komponen.** Pemetaannya ditulis sekali di `services/integration/internal/usecase/komponen_kas.go` (`DaftarKomponenKas`, `cocokKomponen`), berbasis nomor akun:

| Komponen | Akun | Sumber proyeksi | Sumber realisasi tahap 1 |
|---|---|---|---|
| Material | 1601 Bahan Baku, 1602 Bahan Kemas, 1603 Bahan Penolong | isian | buku besar akun persediaan, **hanya** jenis "Penerimaan Barang" dan "Faktur Pembelian"; "Retur Pembelian" mengurangi (`usecase/realisasi_material.go`, penyegar harian 03:50, koleksi `realisasi_material_mingguan`) · akrual |
| BOP | 5201, 5102, 53xx | isian, atau RAPB 5xxx bila isian kosong (sejak 2026-10-22; dulu isian + RAPB) | mutasi akun · akrual |
| Marketing | 61xx bukan gaji | isian, atau RAPB bila kosong (sejak 2026-10-22) | mutasi akun · akrual |
| Gaji | 61xx/62xx yang namanya memuat "gaji" | isian, atau RAPB bila kosong (sejak 2026-10-22) | mutasi akun · akrual |
| Ops adum | 62xx/73xx bukan gaji | isian, atau RAPB bila kosong (sejak 2026-10-22) | mutasi akun · akrual |
| Pajak | — | isian | setoran nyata PT Bharata dari finance-service (`GET /internal/forecast-kas/pajak`) · kas |
| Aset | — | isian | salinan aset tetap `accurate_fixed_assets` (biaya perolehan per tanggal transaksi, draft dibuang) · akrual |

Aturan pengecualian:
- Penyusutan dikecualikan. Penandanya dua: nomor 71xx, atau nama yang memuat "penyusutan".
- Akun beban pajak (`DaftarBebanPajak`) dikeluarkan dari semua komponen.

**Isian.** Isian per komponen per bulan disimpan di koleksi `anggaran_proyeksi_komponen`. Anggaran aset per tahun disimpan di `anggaran_aset_tahunan`. Pengisinya Cost Control, dengan gerbang `finance.anggaran.kelola`.
- Laporan mengirim `komponen[].dapat_diisi` dan `ditambah_rapb`. Layar membaca kedua penanda ini dan tidak menyalin daftarnya; salinan lama di `isian-komponen.ts` hanya tinggal sebagai fallback untuk backend lama.
- Isian sebuah komponen yang sudah masuk basis akurasi tunduk pada kunci minggu dan batas ubah ADR 0161. Pada bulan berjalan, isian itu praktis terkunci sejak minggu 1 mulai (422 `minggu_terkunci`).
- ✅ **Isian untuk semua komponen, menggantikan RAPB** (bip-erp#3466 dalam PR #3465, merged 2026-10-22; Integration-Service prod dibangun 2026-10-22 19:12 WIB dan memuatnya):
  - `DariIsian` dan `IsianMasukBasis` bernilai true untuk keenam komponen.
  - Satu fungsi `gabungIsian` (`usecase/proyeksi_mingguan.go`) membuang akun RAPB milik komponen yang punya isian. Isian 0 juga menggantikan. Fungsi ini dipakai laporan, proyeksi minggu, dan Atur proyeksi.
  - Baris akun RAPB yang diganti dikirim dengan `proyeksi: 0` dan `proyeksi_diganti_isian: true`, supaya tidak terhitung ganda.
  - `ditambah_rapb` bernilai false untuk semua komponen.
  - ⚠️ Bulan yang sudah punya isian BOP berubah angkanya, karena RAPB 5xxx tidak lagi ditambahkan.
- ✅ **Kelonggaran masa transisi** (bip-erp#3464 dalam PR #3465, ter-deploy pada image yang sama):
  - Hingga 31 Des 2026 23:59:59 WIB (`usecase.AkhirMasaTransisiIsian`, satu tempat), isian boleh menggeser minggu yang sudah mulai, termasuk bulan lalu.
  - Batasnya 2 susulan per komponen per bulan (`BatasUbahProyeksiMingguan`). Susulan ke-3 dibalas 422 `batas_ubah`.
  - Setiap PUT/DELETE isian tercatat hanya-tambah di `anggaran_proyeksi_komponen_riwayat`. Bila riwayat gagal dicatat, perubahan isian ikut gagal (500).
  - Penanda di laporan `komponen[].isian_susulan`. GET komponen memuat `susulan_kali`, `kunci_longgar_sampai`, dan `batas_susulan`. Ada rute baru `GET /accounting/anggaran/mingguan/komponen/riwayat`.
  - Atur proyeksi porsi tetap terkunci.
  - Celah yang disadari: dua simpan susulan yang berbarengan bisa meloloskan susulan ke-3.
- ⚠️ **Layar** (erp-frontend#2752): penanda "Diisi susulan", info masa transisi di dialog, dan label "Diganti isian" pada baris akun. Sudah **merged 2026-10-22 17:07 WIB, tetapi belum ada di prod**: bundel frontend prod dibangun 13:57 WIB dan belum memuat teksnya (diukur 2026-10-23). Tombol Isi proyeksi untuk Marketing, Gaji, dan Ops adum sudah tampil di prod karena dibaca dari `dapat_diisi`.

**Uang keluar riil.** Nilainya adalah Σ `keluar` rekening milik PT Bharata dari salinan arus kas-bank finance-service (`GET /internal/forecast-kas/arus-keluar`). Pemilik rekening ditentukan oleh `PemilikDariFakta` yang sama dengan layar arus kas-bank.

#### Aturan membaca angka forecast (⛔ wajib sebelum memakai respons `/accounting/anggaran/mingguan`)

| Angka | Artinya | Aturan |
|---|---|---|
| `minggu[].total_proyeksi`, `total`, akurasi, `/mingguan/kpi` | **Basis akurasi**: RAPB, ditambah isian **hanya** untuk komponen yang realisasinya sudah terukur | Satu objek selalu satu populasi. Jangan dicampur dengan `proyeksi_rencana` |
| `minggu[].proyeksi_rencana`, `total_anggaran_bulan` | Proyeksi **lengkap** termasuk semua isian | Dipakai Atur proyeksi dan ringkasan bulan. ⛔ Bukan penyebut akurasi |
| `komponen[].isian_masuk_basis` | Isian komponen ini sudah ikut basis akurasi | Bernilai false untuk Material/Pajak/Aset bila sumbernya belum terukur |
| `realisasi_pajak` / `realisasi_material` / `realisasi_aset` | Keadaan sumber realisasi komponen | `tersedia: false` atau `disinkron_pada: null` berarti **belum terukur**, bukan Rp 0. Layar menampilkan `sebab` |
| `uang_keluar_riil.keluar` | Pembanding dari sisi rekening bank | ⛔ Tidak masuk total, akurasi, maupun KPI, dan **jangan dijumlahkan** dengan realisasi komponen. `null` berarti salinan belum ada |
| Realisasi Material | **Pembelian**, bukan mutasi bersih persediaan | Mutasi bersih = pembelian − pemakaian − penyesuaian, dan bisa negatif. Contoh 1601 September 2026: mutasi bersih −Rp 65,6 jt, pembelian Rp 82,9 jt |
| `aset_tahunan.sisa` | Anggaran tahun − Σ realisasi aset 1 Jan s.d. akhir bulan laporan | `null` bila anggaran belum diisi atau aset belum disinkron. Boleh negatif. `BiayaPerolehan` adalah nilai current (sesudah pelepasan), bukan harga beli awal |
| Beban pajak 72xx (7201–7212) (tahap 1) | **Tidak masuk komponen mana pun** | Komponen Pajak hanya diisi setoran, yaitu delapan akun `akunPajakSetoran` milik finance: PPN, PPh 21/23/25/4(2)/Final UMKM/Badan, PBB. Akibatnya PKB (7206), BBNKB (7208), dan PPN Kurang Bayar (7212) belum terhitung sama sekali (§Belum Diputuskan) |

#### Tahap 2: realisasi berbasis kas (⚠️ BE merged 2026-10-21, FE PR terbuka, deploy prod TBD)

Keputusan: ADR 0184 Decision 5, bagian "Tahap 2 ditetapkan 2026-10-21" dan "Penerapan C6b". Acuannya laporan Accurate **Arus Kas (Langsung)**, yang hanya bisa ditarik per bulan. Karena itu integration menyusunnya ulang per minggu dari buku besar.

**Data mentah (C6a, bip-erp#3376, PR #3386):**
- Penyegar harian **01:30 WIB** menarik bulan berjalan dan bulan lalu. Hasilnya disimpan di koleksi `arus_kas_langsung_bulanan`, satu dokumen per bulan.
- Populasi kas = semua akun daun `CASH_BANK` dari bagan `glaccount/list.do` saat penyegaran (`ListGLAccountBagan`), bukan daftar nomor di kode. Laporan saldo hanya dipakai sebagai penanda induk cadangan, karena laporan saldo bisa melewatkan akun bersaldo nol.
- Transaksi dikunci jenis + nomor lintas akun kas. Jenis **"Penerimaan Penjualan" dikecualikan**, dan transfer antar-akun kas netonya nol.
  - ⚠️ **Cacat terukur 2026-10-22.** Accurate memberi semua jurnal penutupan bulan nomor yang sama (`"September 2026"`), sehingga jurnal-jurnal itu terlebur menjadi satu transaksi. Akibatnya penyusutan dan selisih biaya produksi ikut terhitung. Contoh September: 5104 −168,6 jt masuk "tak terpetakan", dan 6222 kelebihan 729.167.
  - Laporan Accurate yang dicetak ulang 22 Okt cocok persis untuk 62 akun.
  - ✅ Perbaikannya ada di PR bip-erp#3442 (issue #3440), merged 2026-10-22 dan ada di Integration-Service prod per 2026-10-23. Kunci menjadi `transId` dari `glaccount/history.do` lewat satu fungsi `KunciTransaksi`, yang juga dipakai netting realisasi aset.
  - Sesudah deploy, bulan berjalan dan bulan lalu ditulis ulang. Bulan yang lebih lama tetap memakai kunci lama sampai ditarik ulang.
- Gagal satu akun berarti bulan itu tidak ditulis ulang: angka lama utuh dan penanda gagal dicatat. Bulan yang belum pernah berhasil punya `disinkron_pada: null`, artinya belum ditarik, bukan nol.
- Rute baca untuk verifikasi: `GET /accounting/anggaran/arus-kas` ([[API - Integration Service]]).

**Pemetaan dan realisasi (C6b, bip-erp#3393, PR #3394):**
- Pemetaan akun lawan → komponen ditulis sekali di `PetaAkunArusKas` (`usecase/komponen_arus_kas.go`), mengikuti tabel ADR. Tiap akun masuk tepat satu kelompok: salah satu komponen, "tidak dihitung", CapEx, atau "tak terpetakan". Nomor CapEx dibaca dari `AkunAset()` dan beban pajak dari `akunBebanPajak`.
- Hanya **sel akun × minggu yang netonya minus** yang dihitung. Sel plus diabaikan dan tidak mengurangi.
- **Bulan tersinkron:** keenam komponen `sifat_realisasi = kas`, dan sumber tahap 1 tidak dicampur. **Bulan belum tersinkron** (mis. Juli–Agustus) tetap tahap 1 dan angkanya identik, jadi skor beku tidak bergeser.
- Pada bulan kas, `baris[]` tetap menjadi rincian proyeksi. Realisasinya 0 dengan `status_realisasi = diganti_kas`, supaya angka akrual tidak terjumlah bersama kas. Rincian realisasi ada di `komponen[].akun_arus_kas[]`.
- Bentuk agregat KPI (`/mingguan/kpi`) tidak berubah. Pada bulan kas, `baris_belum_tersinkron` = 0 karena ketersediaan diukur per bulan.

**Layar (C6b FE, erp-frontend#2691, PR #2697 terbuka):** pada bulan kas, keenam komponen bertanda "Kas". Tiap komponen menampilkan rincian per akun Arus Kas, sel akun anggaran berbunyi "Dipantau di Serapan", dan kotak kontrol "tak terpetakan"/"tidak dihitung" tampil.

| Angka (tahap 2) | Aturan |
|---|---|
| `realisasi_arus_kas.dipakai` | true = realisasi komponen bulan ini berbasis kas. Bila false, baca `sebab` dan perlakukan bulan itu sebagai tahap 1 |
| `realisasi_arus_kas.tak_terpetakan` | Uang keluar ke akun lawan yang belum dipetakan Finance. Bila bukan nol, itu pertanyaan pemetaan, bukan galat |
| `realisasi_arus_kas.dikecualikan` | Akumulasi penyusutan, 6113 Potongan Afiliasi, 6114 Ongkir E-Commerce, dan CapEx: tercatat, sengaja tidak dihitung |
| `GET /anggaran/arus-kas` `akun[]` | ⛔ Memuat arus masuk **dan** keluar, sedangkan `kas_keluar_total` dan `tidak_terpetakan` hanya memuat transaksi netto keluar. **Jangan menjumlahkan `akun[]` ke `kas_keluar_total`** |

### KPI Penurunan Biaya OPEX + Non Ops YoY (🟡 Direncanakan, ADR Diterima 2026-10-20, kode belum ada: bip-erp#3336, #3337)

KPI Cost Control #2 mengukur **perubahan total biaya OPEX + Non Ops dibanding bulan yang sama tahun lalu** ([[ADR - 0191 KPI Penurunan Biaya Cost Control Mencakup OPEX dan Non Ops, Baseline Accurate Tahun Lalu]]). Rencana cara kerjanya:

- **Populasi** = `DaftarKomponenOpex` ∪ `DaftarAkunAdminNonOps`. Keduanya daftar yang sudah ada, dan test menjaga agar tidak beririsan. Tidak ada daftar ketiga.
- **Nama diresolusi ke kode akun** dari katalog akun beban saat ini. Kedua periode lalu dicocokkan per **kode**, sehingga rename akun antartahun tidak memutus pasangan.
- **Kedua sisi dibaca lewat panggilan Accurate yang sama** dan disimpan sebagai cuplikan bulanan oleh penyegar harian. Periode yang ditarik: bulan berjalan, bulan lalu, dan pembanding tahun lalu keduanya.
  - `realisasi_opex` **tidak** dipakai, karena tidak punya bulan tahun lalu dan populasinya lebih luas.
- **Rumus** = (Realisasi − Baseline) ÷ Baseline × 100. Negatif berarti turun, dan targetnya ≤ −2. Tidak ada ×1,25.

| Kolom/keadaan | Artinya | Aturan pemakaian |
|---|---|---|
| Total realisasi / total baseline | Σ akun populasi pada bulan penilaian / bulan yang sama tahun lalu | ⛔ **Jangan dijumlahkan** dengan total laporan Non Ops atau varians OPEX: populasinya beririsan dengan keduanya |
| Persen tak terdefinisi | Salah satu sisi belum ditarik, Accurate belum punya data tahun lalu, atau baseline = 0 | Sumber KPI menggalatkannya dengan sebab yang dibedakan, bukan 0% |
| `tak_ada` / `ambigu` | Nama di daftar yang tidak ketemu di katalog Accurate, atau dipakai lebih dari satu akun | Tidak ikut dihitung dan dilaporkan sebagai baris pengecualian |
| `akun_satu_sisi` | Akun yang bersaldo hanya di salah satu periode | Tetap dihitung apa adanya, tetapi dicacah supaya baseline yang mengecil karena akun tutup terlihat |

**Hubungan dengan metrik lain:**
- **Laporan Non Ops** (baseline isian, ADR 0180) dan KPI Finance Supervisor F3 (`rasio_beban_non_ops_persen`) **tidak berubah**.
- **Varians OPEX** (#3, terhadap anggaran) memuat populasi OPEX yang sama, tetapi menjawab pertanyaan yang berbeda. Jangan baca keduanya sebagai bukti independen.

Tambahan di luar halaman ini: kotak **sisa pos** di bawah tiap baris form pencatatan Accounting, dan kartu **Anggaran** baca-saja di tahap Cost Control pada detail pengajuan (pos yang sudah lewat anggaran bulan ini, maksimal 5, sisanya diringkas, plus tautan ke tab Serapan). Kartu itu tidak memperkirakan pos pengajuan, karena pos baru ditetapkan Accounting.

## Aturan Membaca Angka

⛔ **Wajib dibaca sebelum merancang layar atau laporan yang memakai kolom-kolom ini.** Kegagalannya bukan galat, melainkan rupiah yang sama terhitung dua kali atau pos tanpa anggaran yang terbaca Rp 0. Aturan ini semula hanya hidup sebagai komentar kode.

🟢 **Akan berubah, diterima [[ADR - 0178 Serapan Anggaran per Departemen Jurnal, Seluruh Perusahaan Dihapus, Pagu Gabungan per Departemen]]** (diterima 2026-10-15 oleh Azzerith, kode belum ada). Tabel di bawah tetap menggambarkan kode yang berlaku sampai ADR itu dikerjakan. Yang direncanakan berubah:
- Baris `departemen` kosong ("Seluruh perusahaan") tidak lagi menjadi pos, tidak ditampilkan, dan tidak ikut total maupun KPI. Departemen wajib saat input anggaran.
- Pagu gabungan beberapa akun per departemen per bulan ditambahkan.
- Layar Serapan menampilkan **Varians = Terpakai − Anggaran** (minus = masih tersisa) dan **% Varians**. Field `varians` backend **tetap** Anggaran − Terpakai.

⚠️ **Risiko hitung dobel yang berlaku hari ini.** `RingkasVarians` (`anggaran.go:338-360`) menjumlah semua baris terdefinisi tanpa membedakan baris `departemen` kosong dari baris per departemen, padahal realisasi baris kosong = jumlah semua departemen akun itu (`agregasi_riwayat_akun.go:144-152`). Kalau satu akun dianggarkan di keduanya, realisasinya terhitung **dua kali** di total kartu dan di KPI `varians_anggaran`.
- Diukur di prod Oktober 2026: 38 dari 38 baris beranggaran ada di departemen kosong, jadi hitung dobel belum terjadi.
- Hitung dobel langsung terjadi bila RAPB per departemen diunggah **tanpa** menghapus baris kosong.

| Kolom / angka | Artinya | Aturan pemakaian |
|---|---|---|
| **Anggaran** | Nominal master anggaran pos (akun, departemen, bulan). Baris `departemen` kosong = seluruh perusahaan | Hanya baris yang anggarannya **terdefinisi** yang membawa angka |
| **Terpakai** | **Realisasi Accurate** pos itu, dari salinan lokal yang disegarkan harian dan lewat tombol Segarkan | Satu-satunya angka "terpakai"; **tidak pernah bertambah** karena angka dari pengajuan |
| **Sisa** | **Anggaran − Terpakai** (`HitungVarians`, `entity/anggaran.go:299`); bisa negatif | Bukan "anggaran − dari pengajuan" |
| **Lewat anggaran** | Terpakai **lebih besar** dari Anggaran (`anggaran.go:300`), yaitu di atas 100% | Satu-satunya ambang; "mendekati" belum ada. Hanya **peringatan**: tombol "Catat & kirim ke Accurate" tidak pernah dinonaktifkan oleh kondisi anggaran (`form-isian-accounting.tsx:309`). Persentase `null` bila Anggaran 0 (`anggaran.go:301-304`) |
| **Dari pengajuan** | **BAGIAN dari Terpakai**, keterangan atas pengajuan yang sudah berjurnal pada pos itu | ⛔ **Tidak dijumlahkan** ke Terpakai maupun Sisa (`gabungSerapan`, `serapan.ts:129-143`, realisasi baris tidak disentuh). Baris pos "seluruh perusahaan" menjumlah semua departemen akun itu. Total kartu hanya menghitung entri yang jatuh ke baris varians **terdefinisi** (`totalDariPengajuan`, `serapan.ts:150-165`) |
| **Jurnal lain** (sheet rincian) | Terpakai − dari pengajuan | Tidak pernah tampil negatif (menurut deskripsi PR erp-frontend#2188; tidak dibaca ulang barisnya di kode) |
| **Menunggu dicatat** | Pengajuan yang sudah lolos Cost Control tetapi belum berjurnal: antrean **per departemen pengaju** (departemen organisasi, **bukan** departemen Accurate) dan per tipe | ⛔ **Tidak dipetakan ke pos** (K5) dan **tidak ikut** Terpakai/Sisa. Tidak dibatasi periode: ini antrean berjalan (`pengajuan_barang_serapan.go:102-109`). Kalimat "bila dicatat ke akun X, Terpakai naik menjadi …" sengaja tidak dirender |
| **Total Anggaran / Terpakai / Sisa** (kartu ringkas) | Jumlah baris **terdefinisi** saja (`RingkasVarians`, `anggaran.go:338-364`) | Baris yang anggarannya belum diisi, realisasinya belum tersinkron, atau departemennya tak dikenal **tidak ikut** dan dicacah terpisah (`ada_baris_tak_terdefinisi`); layar wajib mengakuinya, bukan menampilkan Rp 0 |
| **Pos tanpa anggaran** | Tidak ada baris anggaran sama sekali | ⛔ Tampil "tidak punya anggaran", **bukan Rp 0**: Sisa Rp 0 berarti anggaran ada dan habis tepat. Baris yang hanya ada karena realisasinya (anggaran `belum_diisi`) **tidak** dihitung sebagai pos (`cariPos`, `serapan.ts:47-61`) |
| **Sisa sesudah dicatat** (form Accounting) | Sisa varians − nominal baris yang sedang diisi (`sisa-pos-anggaran.ts:97-108`); nominal minus (potongan) menambah sisa | Dihitung **per baris**: dua baris ber-akun dan departemen sama tidak saling menjumlah, jadi sisa bisa tampak lebih besar dan peringatan bisa tidak muncul (keputusan terbuka, §Belum Diputuskan). Periode kotak = bulan WIB berjalan |

### Dari mana angka "dari pengajuan" dan "menunggu dicatat"

- **`tercatat` bukan realisasi Accurate.** Ia dibangun dari baris Accounting dokumen pengajuan yang **sudah berjurnal** (`jurnal_nomor` terisi), per (akun COA, departemen Accurate) (`pengajuan_barang_serapan.go:24-28`). Realisasi baru menyusul pada sinkron berikutnya; antara pencatatan dan sinkron itu keduanya boleh berbeda. Bila dari pengajuan lebih besar dari Terpakai, layar menampilkannya **apa adanya** dengan keterangan "menunggu sinkron", tidak dipotong dan tidak ditambahkan (`serapan.ts:104-108`). Keterangan itu hanya muncul bila realisasinya **tersedia** (`status_realisasi === "ada"`). Selama realisasi belum ada, sel Terpakai berisi penanda kosong dan keterangan ini tidak tampil, karena sebabnya memang realisasi yang belum ada, bukan pengajuan yang mendahului Accurate. Syarat ini ditentukan di **satu** tempat, `gabungSerapan` (`serapan.ts:142`), dan dipakai bersama oleh tabel Serapan dan sheet rincian (erp-frontend #2358, merged 2026-10-12).
- **Periode `tercatat`** = bulan **WIB** dari **tanggal jurnal di Accurate**, bukan tanggal Accounting menekan tombol. Tanggal jurnal = tanggal transfer, dengan waktu pencatatan sebagai cadangan (`tanggalJurnalPengajuan`, `pengajuan_barang_jurnal_kirim.go:23-28`), fungsi yang **sama** dengan pembangun jurnal. Dua salinan aturan tanggal berarti serapan Oktober bisa memuat jurnal yang di Accurate jatuh di September.
- **Penanda pencatatan** di riwayat pengajuan berbunyi `dicatat`, **bukan** `disetujui` (`waktuDicatatPengajuan`, `pengajuan_barang_serapan.go:149-157`). Pembaca yang mencari `disetujui` di tahap itu mendapat serapan kosong yang terbaca "belum ada yang tercatat".
- **Syarat masuk antrean Menunggu dicatat** (`menungguDicatat`, `pengajuan_barang_serapan.go:262-278`): tipe berjurnal dan bukan dokumen pembelian, status berjalan, pernah dituntaskan tahap Finance setujui-bayar, `jurnal_nomor` kosong, belum pernah dicatat, jurnal tidak gagal terbit.
- ⚠️ **Dokumen yang tidak masuk daftar mana pun** (disengaja dan dilaporkan di komentar kode, belum diukur jumlahnya): pengajuan yang jurnalnya **gagal terbit**; yang sudah dicatat **tanpa nomor jurnal** (mis. kill switch jurnal mati); dan dokumen berjurnal **tanpa riwayat pencatatan** (jurnal terbit sebelum tahap pencatatan Accounting ada). Uangnya tidak muncul di `tercatat` maupun Menunggu dicatat. Keputusannya terbuka (§Belum Diputuskan).

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Cost Control | Finance; memegang anggaran dan rekomendasi efisiensi | Paket `finance_anggaran` (membaca laporan akuntansi + mengelola anggaran) | Web ERP |
| Supervisor Finance | Finance | Tier supervisor/admin finance memuat izin kelola anggaran | Web ERP |
| Accounting | Finance; mencatat pengajuan | Tahap pencatatan pengajuan (`budget.accounting.pencatatan`); membaca varians untuk kotak sisa pos | Web ERP |
| Staf finance lain | Finance | Boleh membaca laporan; **tidak** melihat tombol tulis anggaran | Web ERP |

Gerbang rute dan rincian izin hidup di [[API - Procurement Service]], [[API - Integration Service]], dan [[CORE - RBAC dan Permission Set]], bukan di sini.

- **Tujuan**: tahu pos mana yang hampir atau sudah lewat anggaran sebelum akhir bulan, dan seberapa besar dana yang masih antre dicatat.
- **Pain point**: dana yang terserap lewat pengajuan tidak terlihat, dan isian anggaran sulit ditemukan.
- **Aksi utama**: lihat Serapan, buka Rincian pos, buat rekomendasi untuk pos yang lewat, unggah RAPB di Anggaran Bulanan.

## Alur Pengguna

1. **Cost Control, awal bulan**: unduh template di tab Anggaran Bulanan, isi, unggah RAPB (`GET /accounting/anggaran/template?tahun=` lalu `POST /accounting/anggaran/upload`).
2. **Cost Control, harian**: buka Serapan, Rincian pos, dan untuk pos lewat anggaran klik **Buat rekomendasi** (akun terbawa ke form Rekomendasi). Di tahap Cost Control sebuah pengajuan, kartu Anggaran baca-saja menyebut pos yang sudah lewat.
3. **Accounting**: buka pengajuan tahap pencatatan (COA, project, departemen terisi seperti sebelumnya), lihat kotak sisa pos per baris, lalu **Catat & kirim**. Sesudah realisasi tersinkron, pengajuan berpindah dari Menunggu dicatat ke "dari pengajuan" pada posnya.

## Urutan Deploy (dijalankan MANUSIA)

Prod: **TBD (belum deploy per 2026-10-08)**. Urutan menurut bip-erp#2811 dan bip-erp#2779: employee-service naik, **pasang paket `finance_anggaran` ke posisi Cost Control** (layar Hak per Posisi) dan pastikan SPV Finance memegang tier supervisor, lalu integration-service naik, lalu **login ulang** pemegang paket (izin dibawa klaim token), baru FE. BE (procurement, integration, employee) sebelum FE. Bila paket terlewat, Cost Control mendapat 403 saat mengunggah RAPB; saat employee-service start cek log `[Migrate]` untuk memastikan paket tersisip. Bukti yang diminta: akun Cost Control mengunduh template, mengisi satu angka, mengunggah tanpa baris ditolak; akun staf finance mendapat 403 di unggah. Prosedur umumnya: [[RUN - Deploy Microservices bip-erp]].

## Belum Diputuskan (TBD)

Dilacak di bip-erp#2814 (Pemutus: wirkancil):

- **Sheet rincian pos**: tiga bagian mockup belum dirender (kalimat antrean IKLAN per akun, tautan "Lihat di buku besar", paragraf "Per orang (marketing)"); butuh penanda akun iklan dari backend dan rute buku besar per akun beban.
- **Dokumen di luar kedua daftar** (lihat §Aturan Membaca Angka): dibiarkan, atau ditambah daftar ketiga / periode dari tanggal transfer. Jumlahnya di prod belum diukur.
- **Gerbang endpoint serapan lebih sempit dari gerbang layar**: tanpa cadangan tier finance. Menyamakannya menuntut aturan cadangan dipindah ke `shared-library`.
- **Sisa sesudah dicatat**: dijumlahkan per pos, atau cukup diberi keterangan.
- **Template unggah bergantung pada Accurate**: daftar akun OPEX diambil langsung dari Accurate, jadi Accurate mati → 502.
- **Konfirmasi paket izin** `finance_anggaran` oleh Pemutus (K9).
- Sisa teknis dari issue yang sama sudah dipecah per issue dan dikerjakan 2026-10-12:
  - **Merged**:
    - bip-erp #2992: rute ganda `/katalog/departemen` dan `/katalog/satuan` dihapus, dijaga `TestRuteTidakTerdaftarGanda`.
    - bip-erp #2996: penjaga tabrakan judul template RAPB, `daftarkanJudulKanonik`.
    - erp-frontend #2338: aturan tier izin kelola kini satu tempat, `tierKelolaAnggaran` di `anggaran/lib/izin.ts`.
    - erp-frontend #2343: test pesan galat unduh template berbadan Blob.
    - erp-frontend #2352: keterangan "Terisi dari" di form Rekomendasi hilang begitu akun diganti.
    - erp-frontend #2355: sheet rincian tidak lagi terbuka sendiri saat posnya muncul lagi.
    - erp-frontend #2358: menunggu sinkron (lihat §Aturan Membaca Angka).
    - erp-frontend #2350: `sebabTakTerdefinisi` yang tak terpakai dihapus, sehingga urutan sebab hanya tersisa di `sebabBaris` (merged 2026-10-12).

  Deploy prod untuk semuanya TBD.
- **Verifikasi**: belum ada layar yang dilihat di browser dan belum ada endpoint yang dicoba lewat gateway.

Untuk cashflow tujuh komponen (ADR 0184), per 2026-10-19:

- ~~**Sumber realisasi berbasis kas (A1, tahap 2).**~~ Diputuskan 2026-10-21 (ADR 0184 tahap 2) dan diterapkan di C6a/C6b, lihat §Tahap 2 di atas. Yang masih perlu ditanyakan ke Finance:
  - **5201**, yang di tahap 1 dihitung BOP, tidak ada di tabel tahap 2 sehingga masuk "tak terpetakan".
  - Akun **72xx** yang namanya tidak memuat PPh/PPN dan tidak ada di `DaftarBebanPajak` juga masuk "tak terpetakan".
  - **6101 Gaji Sales** masuk Marketing menurut tabel. Komponen Gaji tahap 2 hanya berisi Utang Gaji dan Utang Asuransi.
  - Apakah `glaccount/list.do` benar-benar mengirim `isParent`. Cek sekali di dev sebelum prod.
- **Usulan keputusan yang belum disetujui Pemutus.** Semuanya bisa diputuskan dari data prod tanpa bertanya ke Finance:
  - keluarkan 7303/7304 (laba/rugi aset) dari ops adum dan 5313 (selisih persediaan) dari BOP, karena bukan uang keluar;
  - masukkan 7206 PKB dan 7208 BBNKB ke komponen Pajak, karena dibayar langsung dan tidak lewat setoran;
  - 7212 PPN Kurang Bayar tidak dimasukkan, karena dibayar lewat setoran PPN sehingga akan terhitung ganda;
  - 1606 Perlengkapan tidak dihitung saat dibeli, karena bebannya masuk komponen ops saat dipakai.
- **Populasi PT Bharata saja.** Ini asumsi, dengan alasan proyeksinya RAPB milik PT. Belum dikonfirmasi Finance.
- **Skor KPI #4/F4 Juli–September.** Keputusan HRD untuk menghitung ulang belum ada.
- **Nama jenis "Retur Pembelian".** Belum pernah terlihat di data prod. Perlu diukur saat retur pertama terjadi.

Untuk proyeksi mingguan yang diatur (ADR 0161, Diterima 2026-10-09): yang tersisa hanya asal nama pengubah di riwayat (diserahkan ke pelaksana). Sudah diputuskan di ADR-nya: unggah ulang RAPB menerapkan porsi ke anggaran baru untuk semua minggu, bulan mendatang boleh diatur, dan tidak ada tombol kembalikan ke bawaan.

## Dokumen Terkait

- [[ADR - 0159 Serapan Anggaran Dibaca dari Pengajuan sebagai Bagian dari Terpakai, Rute Tulis Anggaran Digerbang Izin Sendiri]]
- [[ADR - 0161 Proyeksi Forecast Kas Mingguan Diatur Porsinya per Minggu oleh Cost Control, Jumlah Sebulan Tetap RAPB]]
- [[ADR - 0184 Forecast Kas Mingguan Mencakup Tujuh Komponen Uang Keluar, Dibagi Empat Minggu, Realisasi Bertahap]] · [[ADR - 0163 Salinan Saldo dan Arus Kas-Bank per Rekening Dimiliki Finance Service, Ditarik lewat Integration Service]] · [[API - Finance Service]]
- [[ADR - 0178 Serapan Anggaran per Departemen Jurnal, Seluruh Perusahaan Dihapus, Pagu Gabungan per Departemen]] (🟢 Diterima)
- [[Finance - Rancangan Finance Service]] · [[Finance - Proses Pengajuan Pengeluaran dan Persetujuan]] · [[Finance - FAT Persona]]
- [[API - Procurement Service]] · [[API - Integration Service]] · [[Microservices - Procurement Service]]
- [[CORE - RBAC dan Permission Set]] · [[APP - Web ERP]] · [[REF - Kepemilikan Data]]
- [[ADR - 0130 Dashboard FAT Diringkas, Isi Posisi Pindah ke Modul Kerjanya]]
- [[ADR - 0180 Akun Anggaran Seluruh Perusahaan Diatur Finance, Non Ops Dua Akun dengan Baseline Isian]] · [[ADR - 0191 KPI Penurunan Biaya Cost Control Mencakup OPEX dan Non Ops, Baseline Accurate Tahun Lalu]] (🟢 Diterima)
