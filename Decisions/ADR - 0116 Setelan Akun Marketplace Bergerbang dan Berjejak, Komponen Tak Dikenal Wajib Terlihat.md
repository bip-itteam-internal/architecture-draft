# ADR - 0116 Setelan Akun Marketplace Bergerbang dan Berjejak, Komponen Tak Dikenal Wajib Terlihat

## Untuk Manajemen

Finance berulang kali melaporkan biaya marketplace tercatat di akun yang salah, dan tiap laporan diperbaiki satu per satu lewat tiket ke IT. Pemeriksaan menemukan bahwa penyebabnya bukan pemetaan yang salah, melainkan dua hal yang tidak terlihat oleh siapa pun.

Pertama, komponen biaya yang belum dikenal sistem tidak hilang dan tidak berbunyi, melainkan masuk ke satu keranjang sisa. Keranjang sisa itu kebetulan memakai akun yang sama dengan Biaya Admin, sehingga biaya apa pun yang belum punya tempat akan muncul sebagai Biaya Admin. Itulah yang selama ini dibaca sebagai "ongkir masuk ke biaya admin". Kedua, tidak ada yang bisa melihat pemetaan yang sedang berlaku beserta artinya, sehingga dua akun yang namanya mirip berulang kali disimpulkan tertukar padahal keduanya memang berbeda peruntukan.

**Yang berubah di layar.** Halaman setelan akun akan menampilkan daftar komponen biaya yang muncul di data tetapi belum punya akun, lengkap dengan berapa kali muncul dan berapa nilainya per marketplace. Perubahan akun tidak lagi langsung tersimpan, melainkan diusulkan oleh staf dan disetujui atasan, dengan catatan alasan yang tersimpan. Setiap perubahan mencatat siapa yang mengubah dan kapan. Sebelum perubahan diterapkan, sistem menampilkan transaksi mana saja yang tercatat dengan akun lama.

**Siapa yang terdampak.** Staf Finance dan Accounting yang mengisi setelan akun, atasan yang menyetujui, dan AR yang menelusuri selisih. Tidak ada perubahan bagi pengguna di luar Finance.

**Yang tidak dijanjikan.** Sistem tidak akan memperbaiki sendiri transaksi yang sudah terlanjur tercatat di Accurate, dan tidak akan mengirim jurnal koreksi. Ia hanya menunjukkan mana yang terdampak; koreksinya tetap dikerjakan Accounting di Accurate. Sistem juga tidak menebak akun yang benar untuk komponen baru, ia hanya memastikan komponen itu terlihat sebelum menjadi selisih. Pemetaan yang berbeda per marketplace belum dibangun pada keputusan ini.

**Perkiraan besaran kerja.** Sedang. Seluruhnya di satu service dan satu halaman yang sudah ada, tanpa modul baru dan tanpa perubahan pada cara data dikirim ke Accurate.

## Deskripsi

*Setelan akun marketplace tetap tinggal di tempatnya sekarang, tetapi dikuatkan dengan gerbang peran, jejak perubahan, dan alur usul lalu setujui. Bersamaan dengan itu, komponen biaya yang belum punya akun diangkat jadi daftar yang terlihat, dan keranjang sisa dilarang berbagi akun dengan kategori bernama, karena di situlah kesalahan yang dikeluhkan Finance sebenarnya lahir.*

- **Status**: 🟡 **Diusulkan**, kode belum ada. Pemutus: SPV FAT (akun untuk keranjang sisa) dan IT (gerbang peran).
- **Path di repo**: `bip-erp/services/integration/main.go` (gerbang peran pada rute kv-config) · `bip-erp/services/integration/internal/domain/entity/accurate.go` (jejak pada `AccurateKVConfig`) · `bip-erp/services/integration/internal/infrastructure/repository/accurate_kv_riwayat.go` (baru) · `bip-erp/services/integration/internal/usecase/komponen_belum_berakun.go` (baru) · `bip-erp/services/integration/internal/interface/http/accurate_handler.go` · `erp-frontend/src/features/integration/config-accurate/` · `erp-frontend/src/i18n/locales/id.ts` dan `en.ts`
- **Tanggal**: 2026-09-22

## Context

Empat permintaan sejenis masuk ke space System Finance dalam lima minggu (18 Agustus sampai 20 September 2026): salah kode akun beban ongkir sampel, kompensasi Shopee belum tercatat, harga dibaca bukan dari hasil pemetaan, dan biaya ongkir masuk ke biaya admin. Perbaikan atas keluhan ketiga tidak menghentikan keluhan keempat sebelas hari kemudian. Pembanding yang relevan ada di space yang sama: 26 permintaan "Bantuan Data" (IT mengoreksi data Finance langsung di basis data) berhenti total setelah alat hapus mandiri berizin dan berlog merge pada 8 Juli 2026, dari 8 permintaan di Mei, 11 di Juni, dan 7 di Juli menjadi nol sesudahnya.

Dugaan awal saat analisa dimulai adalah tidak adanya master pemetaan yang bisa disunting Finance. Pemeriksaan membantahnya.

### Masternya sudah ada, dan sudah bisa diubah tanpa deploy

Sebelas laci akun hidup di koleksi `accurate_kv_configs` sebagai katalog resmi di `entity/accurate.go`, dengan layar hidup di tab Setelan Akun pada Config Accurate. Katalog lacinya disajikan backend dan frontend merendernya apa adanya, sehingga laci baru muncul tanpa mengubah frontend. Nomor akun tidak lagi ditulis di kode, dengan satu pengecualian sadar: bawaan `611704` untuk ongkir sampel, karena baris diskon di dokumen Penerimaan wajib berakun dan mengirimnya kosong membuat penerimaan gagal.

Membangun master kedua karena itu akan melahirkan sumber kebenaran kedua atas fakta yang sama.

### Yang sebenarnya keliru, dan tidak terlihat siapa pun

**Keranjang sisa memakai akun yang sama dengan kategori bernama.** Komponen yang tidak dikenali sengaja jatuh ke residual `TotalAdjustment`, yang dibukukan ke laci `settlement-adjustment`. Terukur di produksi 2026-08-30 dan dikonfirmasi ulang 2026-09-22: laci `settlement-adjustment` dan `service-fee` sama-sama menunjuk akun **6112**. Accurate menjumlahkan keduanya jadi satu saldo akun, sehingga biaya apa pun yang belum punya tempat mendarat di Biaya Admin. Tidak ada kode yang salah memetakan, dan tidak ada galat yang muncul. Inilah bentuk teknis dari keluhan "biaya ongkir masuk ke biaya admin".

Dua komponen sudah pernah diselamatkan dari keranjang ini satu per satu, dan keduanya membuktikan polanya: biaya proteksi pengiriman Shopee (nilainya selalu Rp350, terukur 5.147 order pada Agustus 2026 senilai Rp1.801.450) dan PPh 22 TikTok yang tidak pernah mengisi field pajaknya sendiri. Keduanya ditemukan karena ada yang kebetulan menelusuri, bukan karena sistem memberi tahu.

**Berapa banyak yang berpotensi jatuh ke sana belum pernah diukur sampai analisa ini.** Diukur di produksi 2026-09-22: mutasi dompet Shopee memuat **14 jenis** transaksi, baris keuangan Lazada **19 jenis** nama fee, dan penyesuaian laporan TikTok **4 jenis**, melawan **11 laci akun** yang tersedia. Angka ini tidak berarti 26 komponen salah pos, karena sebagian memang bukan biaya dan sebagian sudah tertangani ember generik. Yang ditunjukkannya adalah tidak ada satu pun tempat yang bisa menjawab pertanyaan "komponen apa saja yang beredar tapi belum punya akun".

**Pemetaan yang berlaku tidak bisa dilihat, sehingga disimpulkan keliru.** Akun `611701` dan `611704` bersaudara di induk 6117 dan bukan pengganti satu sama lain: `611701` untuk nilai barang sampel yang keluar stok, `611704` untuk ongkir kirimnya. `611701` bahkan tidak ada sama sekali di kode produksi, hanya muncul di berkas uji. Kemiripan keduanya sudah tercatat sebagai sumber kebingungan berulang di [[Microservices - Integration Service]], dan keluhan Agustus 2026 adalah kejadian kesekian dari pola yang sama.

### Perubahan pemetaan hari ini tanpa gerbang dan tanpa jejak

Keenam rute kv-config (`catalog`, `date-catalog`, `list`, `POST`, `PUT`, `DELETE`) terdaftar **tanpa middleware peran sama sekali**. Satu-satunya penjaga adalah pemeriksaan bahwa permintaan datang lewat api-gateway, yang menjawab "lewat pintu yang benar", bukan "penggunanya berhak". `RequireIntegrationAdmin` sudah tersedia dan dipakai rute lain di berkas yang sama, jadi yang kurang bukan mekanismenya.

Koleksinya hanya punya `key`, `value`, `description`, `type`, `created_at`, `updated_at`. **Tidak ada `updated_by` dan tidak ada koleksi riwayat.** Pertanyaan "siapa mengganti laci ini dan atas persetujuan siapa" tidak bisa dijawab dari ERP. Nilainya juga tidak divalidasi sebagai akun yang benar-benar ada di Accurate, hanya dibatasi panjang seratus karakter.

Field `type` tidak bisa dipakai membedakan jenis kunci: dari 26 baris di produksi, 17 bertipe `string`, 2 bertipe `system`, 4 bertipe kosong, dan 3 tidak punya field itu sama sekali. Satu laci akun bertipe kosong sementara laci akun lain bertipe `string` yang sama dengan sebuah tanggal cutover.

Frekuensinya justru rendah: enam laci akun inti dibuat 14 Juli 2026 dan **tidak pernah diubah sekali pun** sampai pengukuran 2026-09-22. Yang sering bergerak adalah tanggal cutover dan saklar. Itu sebabnya memperketat penyuntingan saja tidak akan menghentikan keluhan.

### Wewenang menetapkan pemetaan

Dinyatakan pemilik proses (2026-09-22): staf mengusulkan, SPV FAT menyetujui. Fakta "pemetaan komponen biaya ke akun" hari ini belum punya pemilik di [[REF - Kepemilikan Data]], padahal ditulis di tiga tempat: sheet COA milik Finance (hanya untuk Lazada), laci kv di ERP (Shopee dan TikTok), dan aturan klasifikasi di kode. Aturan dokumen itu sendiri mewajibkan dua penulis atas satu fakta tercatat sebagai ADR.

### Yang mengikat dan tidak boleh dilanggar

[[ADR - 0001 Akuntansi via Accurate]] (✅) menegaskan bagan akun, jurnal, dan buku besar adalah domain Accurate, ERP hanya menjembatani, dan integrasinya tidak boleh menulis balik sembarangan. Keputusan ini tunduk penuh padanya.

[[ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance]] (⚠️, belum deploy) menyatakan eksplisit bahwa Shopee dan TikTok **tidak** boleh dianggap mengikuti aturan COA Lazada, karena sheet finance hanya ada untuk Lazada. Itulah alasan dimensi per channel tidak dibangun sekarang.

[[ADR - 0097 Kompensasi Shopee Susulan Ditahan dan Dicatat AR lewat Koreksi Manual ERP]] (⚠️) sudah menutup kelas kompensasi Shopee secara terpisah, sehingga tidak diulang di sini.

## Decision

### 1. Setelan akun tetap di tempatnya, dikuatkan, bukan dipindah

Laci akun tetap hidup di `accurate_kv_configs` dan tetap disunting lewat tab Setelan Akun. Tidak ada entitas master baru dan tidak ada migrasi data. Alasannya lurus dari temuan: masternya bukan yang hilang.

### 2. Rute yang mengubah pemetaan wajib bergerbang peran

`POST`, `PUT`, dan `DELETE` kv-config memasang gerbang peran, bukan hanya pemeriksaan gateway. Rute baca boleh tetap terbuka bagi pemegang akses modul integration agar layar telaah tidak ikut mati.

⚠️ Memasang gerbang mencabut akses yang hari ini terbuka bagi siapa pun yang bisa memanggil gateway. Sebelum dipasang, siapa yang selama ini benar-benar memakai layar itu **wajib diukur lebih dulu**, dan hasilnya dicatat. Gerbang yang dipasang tanpa pengukuran akan menghentikan pekerjaan orang yang tidak pernah diberi tahu.

### 3. Perubahan pemetaan berjalan lewat usul lalu setujui, dengan jejak

Perubahan laci akun tidak langsung berlaku. Staf mengusulkan dengan alasan tertulis, SPV FAT menyetujui atau menolak, dan keputusannya tersimpan bersama pengusul, penyetuju, waktu, nilai lama, dan nilai baru. Riwayat itu **tidak boleh hanya berupa `updated_by` pada barisnya**, sebab nilai lama akan hilang tertimpa.

Polanya **tidak dibangun dari nol**: alur draft lalu adopsi atau tolak sudah hidup di modul yang sama (Kotak Adopsi, dengan catatan wajib, panel sebelum dan sesudah, rincian selisih, deteksi draf basi, serta jejak penyelesai). Di produksi 2026-09-22 ia memuat 525 draft (66 baru, 422 ditolak, 29 diadopsi, 8 basi). Yang dikerjakan adalah memasang pola itu untuk laci akun, bukan menciptakan mesin persetujuan kedua.

Perubahan tanggal cutover dan saklar sistem **tidak** ikut alur ini. Keduanya operasional, bukan keputusan akuntansi, dan menyeretnya ke persetujuan akan membuat alurnya diabaikan.

### 4. Nilai laci divalidasi terhadap akun yang benar-benar ada

Nilai yang disimpan diperiksa terhadap katalog akun Accurate yang sudah ditarik layar setelan, bukan sekadar dibatasi panjangnya.

### 5. Keranjang sisa dilarang berbagi akun dengan kategori bernama

Laci `settlement-adjustment` tidak boleh menunjuk akun yang sama dengan laci bernama mana pun. Simpanan yang melanggarnya ditolak, kecuali ditandai sengaja beserta alasannya, dan tandanya ikut tampil di layar.

Ini menuntut satu keputusan akuntansi dari SPV FAT: akun tersendiri untuk penyesuaian settlement. Selama keputusan itu belum diambil, keadaan sekarang tetap berjalan dan layar menampilkan peringatan bahwa dua laci berbagi akun, sehingga keadaannya terlihat alih-alih diam.

### 6. Komponen yang belum punya akun wajib terlihat

Sistem menyajikan daftar jenis komponen yang muncul di data tetapi belum punya laci akun, per marketplace, dengan jumlah kejadian, nilai, dan kapan pertama kali terlihat. Sumbernya data yang sudah tersimpan, bukan penarikan baru.

Saat sebuah jenis muncul **pertama kali**, dikirim satu pemberitahuan. Pemberitahuan berulang untuk jenis yang sudah diketahui tidak dikirim, karena notifikasi harian yang tidak bisa ditindaklanjuti akan diabaikan lalu mematikan seluruh mekanismenya.

Sistem **tidak menebak** akun yang benar. Ia hanya memastikan komponen itu terlihat sebelum menjadi selisih di rekap.

### 7. Perubahan pemetaan menampilkan transaksi terdampak, dan berhenti di situ

Sebelum perubahan disetujui, sistem menampilkan transaksi mana saja yang tercatat dengan akun lama beserta nilainya. ERP **tidak** mengirim koreksi ke Accurate dan **tidak** mengubah dokumen yang sudah terkirim, tunduk pada [[ADR - 0001 Akuntansi via Accurate]]. Koreksinya dikerjakan Accounting di Accurate.

Polanya sudah ada dan dipakai ulang: modal "Faktur terdampak" pada riwayat harga jual berjalan tiga langkah (pilih beserta alasan, konfirmasi, hasil per baris).

### 8. Dimensi per marketplace belum dibangun

Laci akun tetap global lintas Shopee, TikTok, dan Lazada. Menambah dimensi channel sebelum Finance punya sheet COA untuk Shopee dan TikTok berarti membuat kolom kosong yang tidak ada isinya. Keputusan ini ditinjau ulang setelah [[ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance]] ter-deploy dan sheet untuk kanal lain tersedia.

### 9. Pemiliknya dicatat

Fakta "pemetaan komponen biaya marketplace ke akun" masuk ke peta [[REF - Kepemilikan Data]] dengan pemilik Finance, penulis lewat usul dan persetujuan di ERP, dan salinan sah di sheet COA Finance untuk Lazada selama [[ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance]] belum diperluas.

## Consequences

**Yang membaik.** Komponen baru dari marketplace terlihat sebelum menjadi selisih, bukan sesudah. Keluhan "biaya X masuk ke akun Y" berhenti berulang karena penyebab strukturalnya, yaitu keranjang sisa yang menyamar sebagai Biaya Admin, dihilangkan. Pertanyaan "siapa mengubah laci ini" bisa dijawab. Pembacaan keliru atas akun bersaudara berkurang karena pemetaan yang berlaku bisa dilihat beserta artinya.

**Yang menjadi lebih lambat.** Mengubah akun tidak lagi satu klik. Mengingat enam laci inti tidak pernah diubah dalam lebih dari dua bulan, ongkos ini kecil, tetapi nyata bagi yang sedang memperbaiki keadaan mendesak. Jalan daruratnya adalah persetujuan SPV FAT yang sama, bukan pintu belakang.

**Yang tidak diselesaikan.** Pemetaan berbeda per marketplace (§8). Transaksi yang sudah terlanjur salah pos di Accurate, yang tetap dikoreksi manual. Sheet COA Finance yang masih menjadi sumber tidak berversi di luar ERP, tercatat sebagai utang di [[ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance]].

**Risiko yang diterima sadar.** Gerbang peran bisa mencabut akses orang yang hari ini bekerja lewat layar itu; diredam dengan pengukuran pemakaian sebelum pemasangan (§2). Daftar komponen belum berakun bisa panjang di awal dan terbaca seperti kerusakan massal, padahal sebagian memang bukan biaya; diredam dengan mengurutkan berdasarkan nilai dan menandai jenis yang sudah sengaja tidak dipetakan.

**Deploy.** Backend sebelum frontend. Tidak ada env baru, jadi `--force-recreate` tidak diperlukan. Bila pemberitahuan komponen baru memakai kategori inbox baru, `integration-service` dan `notification-service` wajib naik bersama karena daftar-izin kategori hidup di `shared-library`, lalu satu pemberitahuan sungguhan dipicu sebagai bukti.

⚠️ **Layar Config Accurate belum memakai i18n sama sekali** (nol pemakaian `useTranslation`, diperiksa 2026-09-22). Menyentuhnya mengaktifkan [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]: seluruh teks baru wajib lewat `react-i18next` dan masuk ke dua berkas locale. Ini kerja tambahan yang mudah terlewat saat memperkirakan.

## Dokumen Terkait

- [[Finance - Pemetaan Komponen Marketplace ke Akun Accurate]], cara kerjanya dan daftar lacinya
- [[ADR - 0001 Akuntansi via Accurate]], pagar yang mengikat
- [[ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance]]
- [[ADR - 0097 Kompensasi Shopee Susulan Ditahan dan Dicatat AR lewat Koreksi Manual ERP]]
- [[Microservices - Integration Service]], implementasinya
- [[REF - Kepemilikan Data]]
- [[Finance - Proses Penjualan Marketplace dan Uang Masuk]]
