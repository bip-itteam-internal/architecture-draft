# Finance - Pemetaan Komponen Marketplace ke Akun Accurate

## Deskripsi

*Bagaimana komponen biaya dan pendapatan dari Shopee, TikTok, dan Lazada diterjemahkan jadi baris berakun di dokumen Accurate: di mana pemetaannya hidup, siapa yang boleh mengubahnya, komponen mana yang sengaja tidak dipetakan, dan kolom mana yang TIDAK boleh dijumlahkan karena sudah terkandung di kolom lain. Dokumen ini ada karena aturan-aturan itu sebelumnya hanya hidup sebagai komentar di kode Go, sehingga siapa pun yang merancang layar atau laporan dari dokumentasi tidak punya cara mengetahuinya.*

- **Status**: ⚠️ Implemented (ada catatan)
- **Implementasi**: [[Microservices - Integration Service]]
- **Keputusan**: [[ADR - 0116 Setelan Akun Marketplace Bergerbang dan Berjejak, Komponen Tak Dikenal Wajib Terlihat]] (🟡 Diusulkan) · [[ADR - 0001 Akuntansi via Accurate]] (pagar) · [[ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance]]

## Latar Belakang

Penjualan, potongan platform, dan uang masuk dari marketplace dikirim otomatis ke Accurate sebagai faktur, retur, dan penerimaan. Tiap komponen biaya pada penerimaan menjadi satu baris berakun. Akun tujuannya tidak ditulis di kode melainkan diambil dari laci setelan, supaya Finance bisa mengubahnya tanpa menunggu deploy.

Yang belum tertulis di mana pun sebelum dokumen ini: daftar lacinya, arti tiap laci, komponen yang sengaja dilewati, dan aturan penjumlahan antar kolom. Akibatnya keluhan salah pos berulang empat kali dalam lima minggu (18 Agustus sampai 20 September 2026) dan tiap kali diperbaiki satu per satu lewat tiket.

## Ruang Lingkup

Berlaku untuk jalur penerimaan (uang masuk) ketiga marketplace, yang memakai satu jalur kode yang sama. Tidak mencakup buku besar CV ([[Finance - Buku Besar CV]]) dan tidak mencakup pembelian atau kas kecil.

## Laci akun yang tersedia

Sebelas laci, tersimpan di koleksi `accurate_kv_configs` (satu baris per laci, nilainya nomor akun Accurate). **Global lintas marketplace**: tidak ada dimensi channel maupun toko.

| Laci | Arti | Isi dari |
|---|---|---|
| `service-fee` | Biaya Layanan | biaya layanan + komisi platform + biaya transaksi |
| `discount` | Diskon dan Promo | penyeimbang, dihitung, bukan data mentah |
| `affiliate-commision` | Komisi Affiliate | komisi afiliasi |
| `shipping-cost` | Ongkir | beban ongkir |
| `advertising-cost` | Iklan | beban iklan |
| `settlement-adjustment` | Penyesuaian Settlement | **residual**, lihat bagian di bawah |
| `other-income` | Pendapatan Lain-lain | ganti rugi paket hilang dan sejenisnya |
| `tax-pph` | Beban PPh 22 | pajak, reklas dari residual |
| `insurance-fee` | Beban Asuransi | asuransi, reklas dari residual, di-clamp |
| `sample-adjustment-account` | Beban Sampel, nilai **BARANG** | dokumen Penyesuaian Persediaan |
| `sample-shipping-account` | Beban Sampel, **ONGKIR** | baris diskon di dokumen Penerimaan |

Laci kosong berarti barisnya **tidak dikirim**, kecuali `sample-shipping-account` yang jatuh ke bawaan `611704`. Pengecualian itu disengaja: baris diskon di Penerimaan wajib berakun, dan mengirimnya kosong membuat penerimaan gagal.

⚠️ **`sample-adjustment-account` dan `sample-shipping-account` bukan pengganti satu sama lain.** Keduanya bersaudara di induk 6117 (611701 Afiliasi, 611702 KOL, 611703 Footage, 611704 Ongkir). Satu order sampel menimbulkan dua beban di dua dokumen berbeda: nilai barang yang keluar stok, dan ongkir kirimnya. Kemiripan angkanya sudah berkali-kali dibaca sebagai "setelannya tertukar", padahal tidak. Ini pembacaan keliru yang paling sering terjadi di area ini.

## ⛔ Aturan kolom: mana yang boleh dijumlahkan

Bagian ini yang paling mahal bila dilewatkan. Kolom yang namanya terdengar berdiri sendiri sering merupakan **bagian dari kolom lain**, dan menjumlahkannya menghitung rupiah yang sama dua kali. Gagalnya bukan galat, melainkan angka masuk akal yang salah.

**Komponen sejajar, aman dijumlahkan** sebagai beban: Biaya Layanan, Ongkir, Afiliasi, Iklan, Penyesuaian, Pajak, Asuransi (setelah clamp), dan Pendapatan Lain-lain (bertanda negatif).

**Himpunan bagian, JANGAN dijumlahkan ke induknya:**

| Kolom | Bagian dari | Akibat bila dijumlahkan |
|---|---|---|
| Potongan ongkir Shopee | Pendapatan Lain-lain | dihitung dua kali; ia dipindah ke ongkir, bukan ditambahkan |
| Penyesuaian order Shopee | Nilai settlement | sudah terkandung di nilai settlement yang dipakai |
| `order_seller_discount` | `seller_discount` | duplikat agregat, terbukti di data escrow produksi |
| `seller_shipping_discount` | ongkir neto | subsidi seller sudah terpotong di ongkir neto |
| Komisi afiliasi TikTok sebelum PIT | komisi afiliasi + pajak kreator | informasional, bukan komponen |

**Bukan komponen sama sekali:**

- **Diskon adalah penyeimbang, bukan data.** Ia dihitung mundur agar dokumen balance, dan **bisa bernilai positif**. Bila kolom ini terlihat aneh, yang salah biasanya kolom lain.
- **Asuransi hanya wadah**, tidak terbukti mengurangi uang cair. Ia direklas dari residual dan dibatasi sebesar residual yang benar-benar ada, supaya tidak memfabrikasi beban.
- **Pajak direklas dari residual**, bukan tambahan. Laci pajak kosong mengembalikannya ke residual.

⚠️ **Kolom Biaya Ongkir tidak setara antar marketplace.** Di TikTok isinya ongkir yang ditanggung penjual; di Shopee sudah neto terhadap ongkir yang dibayar pembeli, sementara rebate ongkirnya berdiri sendiri. Membandingkan dua kanal lewat kolom ini akan keliru.

## Residual, dan kenapa ia jadi sumber keluhan berulang

Komponen yang tidak dikenali **sengaja** jatuh ke residual, bukan diabaikan, supaya identitas settlement tidak bocor diam-diam saat marketplace menambah jenis biaya tanpa pemberitahuan. Keputusan itu benar.

Masalahnya bukan di situ, melainkan di akunnya. Terukur produksi 2026-08-30 dan dikonfirmasi ulang 2026-09-22: laci `settlement-adjustment` dan `service-fee` **sama-sama menunjuk akun 6112**. Accurate menjumlahkan keduanya jadi satu saldo, sehingga biaya apa pun yang belum punya tempat muncul sebagai Biaya Admin. Tidak ada kode yang salah memetakan, dan tidak ada galat.

Dua komponen sudah diselamatkan dari residual ini satu per satu: biaya proteksi pengiriman Shopee (selalu Rp350, terukur 5.147 order pada Agustus 2026 senilai Rp1.801.450) dan PPh 22 TikTok yang tidak pernah mengisi field pajaknya sendiri. Keduanya ditemukan karena ada yang kebetulan menelusuri.

[[ADR - 0116 Setelan Akun Marketplace Bergerbang dan Berjejak, Komponen Tak Dikenal Wajib Terlihat]] memutuskan residual dilarang berbagi akun dengan kategori bernama, dan komponen yang belum berakun wajib tampil sebagai daftar.

## Berapa jenis komponen yang beredar

Diukur produksi 2026-09-22. **Ukur ulang sebelum dipakai**, jumlah jenis bertambah saat marketplace menambah skema.

| Sumber | Baris tersimpan | Jenis komponen |
|---|---|---|
| Mutasi dompet Shopee | 115.007 | 14 |
| Baris keuangan Lazada | 4.076 | 19 |
| Penyesuaian laporan TikTok | 432 | 4 |

Melawan 11 laci akun. Angka ini **bukan** berarti 26 komponen salah pos: sebagian bukan biaya (penarikan ke bank, pencairan escrow), dan sebagian tertangani ember generik. Yang ditunjukkannya adalah tidak ada tempat yang bisa menjawab "komponen apa yang beredar tapi belum punya akun".

## Yang sengaja TIDAK dipetakan

Daftar ini penting supaya ketiadaannya tidak dibaca sebagai kelalaian:

- Seluruh kompensasi dompet Shopee selama laci tanggal cutover-nya kosong.
- Kompensasi cicilan kedua dan seterusnya, ditahan untuk dicatat AR ([[ADR - 0097 Kompensasi Shopee Susulan Ditahan dan Dicatat AR lewat Koreksi Manual ERP]]).
- Kompensasi untuk order yang tidak dibukukan sebagai penjualan.
- Beberapa field escrow Shopee: voucher dari Shopee, proteksi produk final (wadah saja), promosi kartu kredit, biaya transaksi pembeli.
- Jenis mutasi dompet yang benar-benar tak dikenal: tidak ditebak akunnya, hanya dilaporkan.
- Order fiktif (FO): tidak dibukukan ke Accurate sama sekali.

## Klasifikasi per marketplace

**Shopee dan TikTok** memakai pembagian ember generik: komponen dipetakan ke tujuh ember, lalu tiap ember mengambil akun dari lacinya.

**Lazada** berbeda dan sengaja menyimpang: klasifikasinya bersandar langsung pada sheet COA milik Finance lewat satu fungsi klasifikasi, dengan nama fee tak dikenal jatuh ke Beban Admin. Keputusannya [[ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance]], yang menyatakan eksplisit bahwa **kanal lain tidak boleh dianggap mengikuti aturan ini** karena sheet finance hanya ada untuk Lazada.

## Persona

| Persona | Peran dan Divisi | Akses | Device |
|---|---|---|---|
| Staf Accounting | menyusun rekap, menemukan selisih | modul integration | Web ERP |
| Admin AR | menelusuri kompensasi dan retur | modul integration | Web ERP |
| SPV FAT | menyetujui pemetaan akun | modul finance, tingkat supervisor | Web ERP |

- **Tujuan**: pembukuan marketplace di Accurate cocok dengan yang sebenarnya terjadi, tanpa rekap manual.
- **Pain point**: biaya muncul di akun yang tidak diharapkan, dan tidak ada cara melihat pemetaan yang berlaku.
- **Aksi utama**: memeriksa rekap, mengubah laci akun, menelusuri selisih ke transaksi.

## Konsumen Data

- [[Finance - Proses Penjualan Marketplace dan Uang Masuk]], alur uang masuk per toko
- [[Finance - Proses Pencatatan dan Buku Besar]], pemeriksaan harian hasil sinkron
- [[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]], yang **mengasumsikan** komponen e-commerce sudah terpotong di uang cair dan karena itu mengecualikannya dari perhitungan insentif

## Kendala

- Pemetaan global, tidak per marketplace maupun per toko.
- Sheet COA Finance (Lazada) adalah sumber di luar ERP dan tidak berversi; bila berubah, tidak ada yang memberi tahu.
- Nilai laci tidak divalidasi terhadap akun yang benar-benar ada di Accurate.
- Perubahan laci tidak berjejak: tidak ada penulis, tidak ada riwayat, nilai lama hilang tertimpa.
- Rute yang mengubah laci belum bergerbang peran (diperbaiki oleh [[ADR - 0116 Setelan Akun Marketplace Bergerbang dan Berjejak, Komponen Tak Dikenal Wajib Terlihat]]).

## Belum Diputuskan (TBD)

- Akun tersendiri untuk `settlement-adjustment`, agar residual berhenti menyamar sebagai Biaya Admin. Pemutus SPV FAT.
- Peran mana persisnya yang dipakai sebagai penyetuju, dan siapa yang hari ini memakai layar setelan. **Wajib diukur sebelum gerbang dipasang.**
- Apakah laci akun perlu dimensi per marketplace. Ditinjau setelah [[ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance]] ter-deploy dan sheet COA untuk Shopee serta TikTok tersedia.
- Backfill data lama Lazada setelah klasifikasi barunya berlaku.

## Dokumen Terkait

- [[Microservices - Integration Service]], implementasinya
- [[ADR - 0116 Setelan Akun Marketplace Bergerbang dan Berjejak, Komponen Tak Dikenal Wajib Terlihat]]
- [[ADR - 0001 Akuntansi via Accurate]]
- [[ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance]]
- [[ADR - 0097 Kompensasi Shopee Susulan Ditahan dan Dicatat AR lewat Koreksi Manual ERP]]
- [[REF - Kepemilikan Data]]
- [[ANALISA - Setelan Akun Marketplace dan Komponen Tak Dikenal]], pecahan tugasnya
