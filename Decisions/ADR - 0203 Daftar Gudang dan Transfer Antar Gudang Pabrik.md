> **Status**: 🟡 **Diusulkan**, 2026-10-23. Lembar keputusan K-7 bagian **gudang** di [[ANALISA - Fondasi Manufaktur]], dipecah dari [[ADR - 0136 Pemilik Master Barang dan Master Gudang]]; bagian barang tetap di ADR itu. Pemutus: **Achmad Fauzi** (Warehouse Leader, Manufaktur; dikenal Oji/Ozi), ditunjuk lewat IT 2026-10-23. Pertanyaan 4 juga butuh persetujuan Finance (Senior Accounting), karena menyangkut pembukuan Accurate.

## Untuk Manajemen

**Apa yang perlu diputuskan.** Bagaimana pindahan barang antar gudang dicatat di ERP: gudang mana saja yang ada di daftar, apakah ERP perlu menghitung stok per gudang, siapa yang mencatat dan menerima, dan apakah pindahan itu otomatis masuk Accurate.

**Usulan singkat.**
1. Daftar gudang di ERP **memakai nama gudang yang sama dengan Accurate**, cukup gudang yang benar-benar dipakai tim gudang.
2. Stok pabrik di ERP tetap **satu angka per barang**, yaitu isi Gudang Utama (sesuai [[ADR - 0186 Stok Pabrik di ERP Jadi Stok Operasional, Accurate Menerima Penyesuaian Persediaan]]). Barang yang dipindah ke gudang lain tercatat **keluar** dari stok pabrik; barang yang dipindah masuk tercatat **masuk**. ERP tidak dipecah per gudang.
3. Pindahan dicatat **dua langkah**: gudang asal mencatat kirim, gudang tujuan mencatat terima. Pengirim dan penerima orang yang berbeda.
4. Pindahan **otomatis dikirim ke Accurate** sebagai Pemindahan Barang, sama dengan cara Finance mencatatnya hari ini. Sesudah itu Finance berhenti mengetik pindahan yang sama secara manual.
5. Jumlah diterima yang berbeda dari jumlah dikirim menjadi **usulan penyesuaian** di jalur penyesuaian stok tunggal (M-12), sama seperti Bukti Selisih RM.

**Siapa yang terdampak.** Tim gudang (pencatat kirim dan terima), Finance (Pemindahan Barang di Accurate), PPIC (angka stok pabrik).

**Kenapa perlu ditulis sekarang.** Butir M-18 (transfer stok antar gudang, erp-frontend#1869) tidak bisa dikerjakan tanpa jawaban ini. Hari ini pindahan antar gudang hanya tercatat di Accurate, diketik tangan oleh Finance.

**Apa yang tidak dijanjikan.** Master barang: siapa yang menambah dan mengubah barang, bundle marketplace, dan HPP tetap di [[ADR - 0136 Pemilik Master Barang dan Master Gudang]]. Stok gudang online/marketing (Sadewa, Shopee, dan lain-lain) di ERP juga tidak termasuk.

**Perkiraan besaran kerja.** Sedang (estimasi). ERP sudah punya dokumen Mutasi Gudang dua langkah yang tinggal disambungkan ke stok, persetujuan, dan Accurate (lihat Context).

## Pertanyaan untuk Pemutus

Rekomendasi disertakan; Pemutus boleh memilih lain.

| # | Pertanyaan | Pilihan | Rekomendasi |
|---|---|---|---|
| 1 | Daftar gudang di ERP | (a) memakai nama gudang Accurate, hanya yang dipakai tim gudang; (b) daftar sendiri di ERP, dipetakan ke Accurate | **(a)**. Nama yang sama membuat pindahan bisa dikirim ke Accurate tanpa tabel padanan. Sebutkan gudang mana saja dari 8 gudang Accurate (lihat Context) yang dipegang tim gudang |
| 2 | Perlu stok per gudang di ERP? | (a) tidak: stok pabrik = isi Gudang Utama, pindahan keluar/masuk Gudang Utama mengurangi/menambah stok pabrik; (b) ya: semua stok di ERP dipecah per gudang | **(a)**. (b) menuntut setiap transaksi gudang menyebut gudangnya, dan itu perubahan besar di seluruh layar gudang dan produksi |
| 3 | Siapa mencatat dan siapa menyetujui pindahan | (a) admin gudang mencatat kirim, penerima di gudang tujuan mencatat terima, tanpa persetujuan tambahan; (b) seperti (a), ditambah persetujuan Warehouse Leader sebelum dikirim; (c) seperti (a), ditambah persetujuan SPV Manufaktur | **(a)**. Dua orang berbeda di kirim dan terima sudah menjadi pengendali, dan pindahan tidak mengubah total persediaan perusahaan |
| 4 | Dikirim ke Accurate? *(perlu persetujuan Finance juga)* | (a) ya, otomatis sebagai Pemindahan Barang dua langkah (keluar saat dikirim, masuk saat diterima), lalu Finance berhenti mencatat manual untuk pindahan yang sama; (b) tidak, Finance tetap mencatat manual | **(a)**. Mengikuti praktik Finance hari ini. Bila ERP dan Finance sama-sama mencatat, pindahan tercatat dua kali |
| 5 | Jumlah diterima berbeda dari jumlah dikirim | (a) penerima mencatat jumlah nyata, selisihnya menjadi usulan penyesuaian di jalur M-12 (disetujui SPV Manufaktur, divalidasi Senior Accounting); (b) penerima wajib menerima sejumlah yang dikirim, selisih dicatat di luar sistem | **(a)**. Sama dengan keputusan Bukti Selisih RM ([[ADR - 0201 Selisih RM Dicatat Dua Sisi lalu Masuk Satu Jalur Penyesuaian Stok]]), sehingga satu stok punya satu cara dibetulkan |

*Dicocokkan ke kode `origin/main` dan data prod (baca saja) 2026-10-23 sebelum dikirim, supaya Pemutus tak ditanya hal yang sudah tertulis.*

## Deskripsi

*Pindahan antar gudang dicatat dua langkah (kirim, terima) memakai daftar gudang bernama sama dengan Accurate; stok pabrik ERP tetap satu angka per barang (isi Gudang Utama) yang berkurang/bertambah saat barang keluar/masuk Gudang Utama; pindahan dikirim ke Accurate sebagai Pemindahan Barang; selisih terima masuk jalur penyesuaian M-12.*

- **Status**: lihat blockquote di baris pertama dokumen ini
- **Keputusan papan**: K-7 bagian gudang; membuka M-18 di [[ANALISA - Fondasi Manufaktur]]
- **Issue**: bip-itteam-internal/erp-frontend#1869 (transfer antar gudang); keputusan induk bip-itteam-internal/bip-erp#2189
- **Dipecah dari**: [[ADR - 0136 Pemilik Master Barang dan Master Gudang]] (§Pertanyaan butir 4, dan bagian gudang dari Rekomendasi butir 5)
- **Tanggal**: 2026-10-23

## Context

Diukur di kode `bip-erp` `origin/main` (f241829be) dan data prod (baca saja) 2026-10-23.

**Gudang di Accurate.** Ada 8 gudang: Gudang Utama, Sadewa, Shopee, Gentara, Iis, Sidareja, Rework, dan GA. Bahan baku dan bahan kemas pabrik yang diperiksa (kode BBK, BKK, BKO) seluruhnya bersaldo di Gudang Utama. Accurate menyediakan stok per gudang (`item/list-stock.do?warehouseName=`; Gudang Utama berisi 922 barang).

**Pindahan di Accurate hari ini.** Ada 1.285 dokumen Pemindahan Barang, terbaru 19 Oktober 2026. Dari 12 dokumen terbaru, semuanya berpasangan TRANSFER_OUT dan TRANSFER_IN (dua langkah), dengan rute Gudang Rework ↔ Sadewa, Gudang Utama → Sidareja, dan Sidareja → Sadewa. Siapa yang mengetiknya belum diukur. API-nya `item-transfer/save.do` (wajib: `detailItem`, `itemTransferType`, `transDate`; gudang lewat `warehouseName` dan `referenceWarehouseName`).

**Yang sudah ada di ERP** (manufacture-service):
- **Master lokasi** `manufacture_lokasi_gudang` (kode, nama, tipe GUDANG/TOKO, konsinyasi, aktif), digerbang tab `master_lokasi`. Isinya di prod **kosong**.
- **Mutasi Gudang** (`services/manufacture/mutasi_gudang.go`, rute `main.go:139-142`): dokumen dua langkah DRAFT → DIKIRIM → DITERIMA antar lokasi di master itu, dengan PIC kirim dan PIC terima. Menurut komentar modelnya, ia **tidak menyentuh stok global** (lapisan pelacakan); saldo per lokasi hanya diturunkan dari dokumen mutasi, bukan stok absolut. Tidak ada persetujuan dan tidak dikirim ke Accurate. Di prod **belum pernah dipakai** (koleksinya belum ada).
- **Stok pabrik** `manufacture_stok` berkunci kode barang saja, tanpa dimensi gudang.
- Komentar `services/manufacture/accurate_push.go:38-39` menyebut transfer antar gudang tidak didorong karena "Accurate kita tidak berdimensi gudang". **Itu tidak sesuai data di atas**; Accurate mencatat stok dan pindahan per gudang.

**Gudang online.** warehouse-service (Gudang Sadewa) hanya punya master produk tanpa saldo, dan sengaja tidak memegang buku stok kedua (`services/warehouse/models.go:125-129`).

## Decision

**TBD.** Diisi setelah Pemutus menjawab §Pertanyaan. Pertanyaan 4 juga membutuhkan persetujuan Finance (Senior Accounting).

## Consequences

*Bila usulan diterima:*

**Yang didapat.** Pindahan yang hari ini diketik dua kali (di kertas atau chat, lalu di Accurate oleh Finance) cukup dicatat sekali oleh gudang. Stok pabrik di ERP ikut bergerak saat barang keluar atau masuk Gudang Utama. Selisih di perjalanan terlihat dan punya jalan resmi untuk dibetulkan.

**Yang harus diterima.**
- ERP tidak tahu isi gudang lain (Sidareja, Sadewa, dan seterusnya); angka itu tetap dibaca dari Accurate.
- Finance harus berhenti mengetik pindahan yang sudah dikirim ERP. Masa peralihannya perlu diumumkan, supaya tidak ada pindahan yang tercatat dua kali.
- Pindahan antar dua gudang yang sama-sama bukan Gudang Utama (mis. Rework → Sadewa) tidak mengubah stok pabrik ERP. Bila tim gudang tetap mencatatnya di ERP, pindahan itu hanya diteruskan ke Accurate.

## Alternatif yang ditolak

- **Stok ERP dipecah per gudang untuk semua gudang.** Menuntut setiap transaksi gudang dan produksi menyebut gudangnya, dan menjadikan ERP buku kedua untuk gudang online yang hari ini sengaja tidak memegang saldo.
- **Membiarkan pindahan hanya di Accurate.** Stok pabrik ERP tidak tahu barang sudah keluar ke gudang lain, sehingga ERP menyimpang dari fisik begitu tarikan Accurate dihentikan (ADR 0186).
