# ADR - 0136 Pemilik Master Barang dan Master Gudang

> **Status**: 🟡 **Diusulkan**, 2026-09-29, BELUM diputuskan dan nol kode. Pengambil keputusan: **TBD** (tim IT bersama manajemen; lihat §Pertanyaan yang harus dijawab manusia, butir 1). Dok ini memetakan masalah, opsi, dan usulan penulis; ia tidak menetapkan apa pun sampai bagian §Decision diisi orang yang berwenang.
>
> **Issue GitHub**: [bip-erp#2357](https://github.com/bip-itteam-internal/bip-erp/issues/2357) (Project #15, dibuat 2026-09-29 dari verifikasi kode + data prod).

%% Status di blockquote atas supaya terbaca VAULT-INDEX.json (15 baris pertama), pola sama dengan ADR 0132/0135. %%

## Untuk Manajemen

**Masalahnya dalam satu kalimat.** Daftar barang (produk jadi, SKU marketplace, bahan baku, barang GA) disimpan di sembilan tempat di ERP dan daftar gudang di sedikitnya lima tempat sebagai ketikan bebas, tanpa satu pun yang ditetapkan sebagai "yang benar". Akibatnya angka yang bergantung pada barang (HPP, stok, laba, insentif) bisa salah tanpa ada yang berbunyi.

**Yang perlu diputuskan.** Siapa pemilik daftar barang dan daftar gudang: Accurate saja, satu modul ERP, atau dibagi per jenis barang dengan satu kode bersama. Juga siapa **orang atau bagian** di perusahaan yang bertanggung jawab menambah dan mengubah barang.

**Yang tidak dijanjikan.** ADR ini belum memindahkan data apa pun dan belum mengubah layar apa pun. Setelah diputuskan, pekerjaan migrasinya besar (menyentuh lima service dan beberapa layar) dan harus dipecah bertahap.

## Deskripsi

*Usulan untuk menetapkan SATU pemilik identitas barang (kode, nama, satuan, jenis) dan SATU pemilik daftar gudang di ERP Bharata, beserta aturan salinan satu arah berpenjaga untuk semua tempat lain yang sekarang menyimpan barang atau gudang sendiri. Tiga opsi dibandingkan; usulan penulis ditandai jelas sebagai usulan.*

- **Path di repo (yang terdampak, bukan yang diubah)**: `bip-erp/services/integration/internal/domain/entity/item.go`, `entity/profit.go`, `entity/incentive_profit.go` · `bip-erp/services/manufacture/master.go`, `master_product.go`, `sync_hpp.go`, `lokasi_gudang.go`, `accurate_push.go` · `bip-erp/services/procurement/barang.go`, `accurate_item.go`, `sync.go`, `pengajuan_barang.go`, `pesanan_erp.go`, `penerimaan_erp.go` · `bip-erp/services/warehouse/models.go`, `main.go` · `bip-erp/shared-library/models/manufacture/models.go` · `erp-frontend/src/features/pengajuan-barang/hooks/use-isi-harga.ts`
- **Tanggal**: 2026-09-29
- **Diukur ke**: bip-erp `origin/main` `89296af7`, erp-frontend `origin/main` `44c780311` (baris FE yang dikutip sama dengan pengukuran bahan di `1b9821715`)

## Context

### Barang: sembilan tempat, empat di antaranya bisa ditulis tangan

Dipetakan di [[REF - Kepemilikan Data]] §Duplikasi (baris Produk/SKU/bahan baku). Ringkasnya:

| Tempat | Service | Cara terisi | Bukti |
|---|---|---|---|
| `items` (BASE, VARIATION, SUB_VARIATION, BUNDLE, `bundle_contents`, `additional_skus`) | integration | CRUD dari layar | `services/integration/internal/domain/entity/item.go:8-43` |
| `product_costs` (HPP per produk, `master_sku` boleh `""` untuk baris lama berbasis nama) | integration | unggah xlsx / input manual / Accurate | `entity/profit.go:21-34` |
| `product_sku_mappings` (listing penjual ke `master_sku`, `qty_per_unit` untuk bundle) | integration | seed + CRUD manual | `entity/profit.go:37-67` |
| `manufacture_master_bahan` | manufacture | tarik dari `accurate_stocks` lewat integration **dan** `CreateMaster` manual bersumber `"manual"` yang "kebal stale-marking saat sync" | `services/manufacture/master.go:14-44`, `sync_hpp.go:179-301` |
| `manufacture_master_product` | manufacture | tarik dari HPP integration (`/profit/wms/finished-products`) + Accurate, **dan** create manual | `sync_hpp.go:566-643`, `master_product.go:123-160` (`CreateMasterProduct`, bersumber `"manual"`) |
| `barang` | procurement | CRUD dari layar, lalu **didorong ke Accurate** lewat `item/save.do` (menyimpan `accurate_id`, `sync_status`, retry) | `services/procurement/barang.go:53-93`, `accurate_item.go:101-104`, `sync.go:33` |
| `warehouse_products` (`sku`, `barcode`, `nama`, `lokasi_rak`) | warehouse | CRUD + impor manual | `services/warehouse/models.go:110-118`, `main.go:178-182` |
| `accurate_products`, `accurate_stocks` | integration | salinan Accurate, refresh harian | [[REF - Kepemilikan Data]] §Salinan |

Diverifikasi ulang 2026-09-29: **procurement adalah satu-satunya service yang menulis item ke Accurate** (`git grep item/save.do` hanya mengenai `services/procurement`). Integration `items` tidak punya field rujukan ke item Accurate sama sekali; `product_costs.external_id` disiapkan untuk itu tetapi berkomentar "fase berikut" (`profit.go:30`).

### Bundle didefinisikan dua kali, dan salinannya tak pernah menghapus

- `items.bundle_contents` (`item.go:38-39`) dan `product_sku_mappings` ber-`master_sku` beda dengan `qty_per_unit` (`profit.go:37-53`, butir (c) di komentarnya) sama-sama menyatakan isi bundle.
- manufacture menyalin mapping ke `manufacture_sku_mapping` lewat upsert `$set` per listing (`services/manufacture/sync_hpp.go:605-619`). `git grep` atas `Collections.SkuMapping` di `services/manufacture` hanya menemukan pembaca (`bundle.go:20`, `:69`) dan upsert itu; **tak ada penghapusan**. Listing yang dibuang di integration tetap hidup di manufacture selamanya.

### Akibat nyata yang sudah terjadi

- **HPP insentif meledak** (dicatat di ingatan tim, butir "kunci join KOSONG"): penjualan ber-`sku==""` jatuh ke satu bucket berisi semua baris penyelamat `product_sku_mappings` ber-`sku==""`, lalu HPP-nya dijumlah seolah satu bundle. HPP satu toko menjadi Rp1,45 M atas nilai jual Rp7,9 jt dan realisasi satu Account Specialist menjadi minus Rp1,16 M, tanpa satu pun galat. Perbaikan di jalur hitung (`HitungHPPInsentif`, `services/integration/internal/domain/entity/incentive_profit.go:337-422`, cocok lewat nama, tak cocok masuk `nilaiTanpaHPP`) lewat bip-erp PR [#1769](https://github.com/bip-itteam-internal/bip-erp/pull/1769). Akarnya belum tersentuh: kunci barang boleh kosong karena tak ada pemilik yang mewajibkannya.
- **Gudang faktur tertinggal**: gudang per toko hidup di `accurate_shops.warehouse_name` (`entity/accurate.go:201`) dan hanya dipakai saat menulis dokumen. Saat 17 toko dipindah ke Gudang Sadewa, 241 faktur lama tetap tercatat di Gudang Sidareja dan harus dipindah dengan alat khusus (`services/integration/cmd/gudangfix/main.go:1-9`).

### Gudang/lokasi: ada SATU master, tapi tak dirujuk siapa pun di luar manufacture

Koreksi atas peta sebelumnya ("tak ada master gudang"): manufacture **punya** master lokasi `manufacture_lokasi_gudang` (`LokasiGudang`: `kode`, `nama`, `tipe` `GUDANG`/`TOKO`, `konsinyasi`, `aktif`; `shared-library/models/manufacture/models.go:65`, `:874-883`), CRUD digerbang tab `master_lokasi` (`services/manufacture/main.go:127-131`), dan penghapusan ditolak bila lokasi dipakai dokumen mutasi (`lokasi_gudang.go:120-131`). Tetapi tempat lain menulis gudang sebagai **teks bebas** tanpa merujuknya:

- `MasterBahan.Lokasi` string (`shared-library/models/manufacture/models.go:98`), di model yang sama dengan master lokasi itu
- `warehouse_products.lokasi_rak` (`services/warehouse/models.go:114`)
- procurement: `penerimaan_erp.gudang` (`penerimaan_erp.go:44`), `pesanan_erp.gudang` (`pesanan_erp.go:70`), `pengajuan_barang.gudang_tujuan` (`pengajuan_barang.go:369`)
- integration: `accurate_shops.warehouse_name` (`entity/accurate.go:201`), `departments.warehouse` (`entity/department.go:8`)
- frontend: konstanta `GUDANG_GA = "GA"`, `GUDANG_RM = "RM"` yang "dibaca backend apa adanya" (`erp-frontend/src/features/pengajuan-barang/hooks/use-isi-harga.ts:16-18`)

⚠️ **Dua pernyataan di kode tentang gudang Accurate saling bertentangan.** `services/manufacture/accurate_push.go:38-39` menyatakan transfer antar gudang tak didorong karena "Accurate kita tidak berdimensi gudang", sementara integration menulis gudang per baris faktur dan retur, dan `gudangfix` menyebut bahwa memindah faktur tanpa retur membuat "stok kedua gudang permanen tak seimbang" (`cmd/gudangfix/main.go:10-12`). Jadi Accurate **mencatat** gudang di dokumen penjualan, tetapi pergerakan internal WMS tidak ikut. Mana yang benar untuk stok legal harus dijawab Finance (§Pertanyaan, butir 4).

### Kenapa belum pernah diputuskan

1. **Tiap salinan lahir dari kebutuhan sah satu modul**: profit marketplace butuh listing dan bundle, produksi butuh bahan bergram dan lokasi rak, pengadaan butuh pemasok dan PPN, gudang butuh barcode. Tak satu pun salah sendirian; yang hilang adalah aturan siapa yang memegang identitasnya.
2. **Accurate adalah pemilik legal** item persediaan dan buku besar PT ([[ADR - 0001 Akuntansi via Accurate]]), tetapi Accurate tak mengenal listing marketplace, varian toko, atau HPP per listing. Jadi "Accurate saja" tidak otomatis menjawab.
3. **Keputusannya lintas departemen** (Finance, PPIC/Produksi, Procurement, Gudang, Marketing, GA), dan belum ada satu pun bagian yang ditunjuk sebagai pemilik proses master data barang.
4. Aturan [[ADR - 0002 Database-per-Service]] menjaga agar tiap service punya koleksinya, tetapi tidak menjawab koleksi **mana** yang boleh menjadi sumber bila dua service menyimpan fakta yang sama. Pola jawaban untuk kasus serupa sudah ada: [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] (satu fakta satu pintu) dan [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]] §8 (teks bebas lokasi diganti rujukan ke satu master).

## Opsi

Semua opsi memakai definisi yang sama: **identitas barang** = kode, nama, satuan dasar, jenis (persediaan, non-persediaan, jasa), status aktif. Atribut khusus modul (listing marketplace, resep, lokasi rak, pemasok utama, HPP berlaku) bukan identitas dan boleh tetap di modulnya asal merujuk kode barang, bukan menyalin nama.

### Opsi 1: Accurate satu-satunya master barang dan gudang; ERP hanya cermin satu arah berpenjaga

Barang dan gudang dibuat dan diubah **di Accurate saja**. ERP menarik keduanya ke satu cermin (`accurate_products`/`accurate_stocks` yang sudah ada, plus daftar gudang Accurate yang belum ditarik), dan semua modul merujuk kode item Accurate.

- **Konsekuensi**: identitas barang dan gudang sama persis dengan buku besar; tak mungkin ada barang ERP yang tak punya padanan akuntansi. Layar `barang` procurement berubah jadi pembaca; `CreateMaster` manual manufacture dan CRUD `warehouse_products` dicabut. Listing marketplace, bundle, dan HPP per listing **tidak** bisa hidup di Accurate, jadi tetap perlu tabel pendamping di ERP yang merujuk kode Accurate (tetap satu tabel, bukan dua definisi bundle).
- **Ongkos migrasi**: sedang. Cermin sudah ada; yang baru adalah penarikan daftar gudang, pemetaan kode lama ke kode Accurate untuk `manufacture_master_*`, `warehouse_products`, `product_costs` ber-`master_sku` kosong, dan pencabutan jalur tulis di tiga service. Alat penyelaras kode sudah ada di manufacture (`align_bahan.go`, `align_product.go`).
- **Risiko**: barang baru bergantung pada orang yang punya akses Accurate, sehingga Gudang/PPIC bisa macet menunggu Finance; kegagalan token Accurate ([[ADR - 0014 Accurate Token DB-backed via OAuth]]) menghentikan penambahan barang di ERP. Barang non-persediaan GA dan barang yang sengaja tak dibukukan (sampel, bahan uji) harus dibuat di Accurate atau dikecualikan dengan aturan tertulis. Pengetahuan "Accurate tidak berdimensi gudang" untuk transfer internal (§Context) berarti daftar gudang Accurate mungkin tak cukup rinci untuk rak/lokasi fisik WMS.

### Opsi 2: satu service ERP jadi pemilik; modul lain membaca lewat API; pemilik menyinkron ke Accurate

Kandidat paling masuk akal dari kode adalah **procurement `barang`**: ia satu-satunya yang sudah menulis ke Accurate (`item/save.do`), menyimpan `accurate_id`, status sinkron, dan antrean ulang (`barang.go:86-91`), serta memvalidasi field wajib Accurate sebelum mengirim (`barang.go:99`). Kandidat kedua **integration `items`** punya struktur varian dan bundle, tetapi tanpa rujukan ke Accurate dan tanpa satuan; kandidat ketiga **manufacture** punya alat penyelaras dan jejak audit (`writeAudit`), tetapi berorientasi bahan dan barang jadi pabrik. Untuk gudang, pemiliknya **`manufacture_lokasi_gudang`** (satu-satunya master gudang berkode yang sudah ada).

- **Konsekuensi**: satu layar untuk menambah barang di seluruh ERP; Accurate tetap mendapat item lewat satu pintu. Modul lain membaca lewat HTTP (bukan membaca DB langsung, yang sekarang sudah dilakukan procurement ke `integration_db`, dicatat sebagai utang di [[REF - Kepemilikan Data]] §Pengecualian).
- **Ongkos migrasi**: besar. `barang` harus ditambah jenis, varian/bundle atau rujukannya, barcode; seluruh pembaca di integration, manufacture, dan warehouse dialihkan; data lama di sembilan tempat dicocokkan satu per satu ke satu kode. Procurement menjadi service kritis bagi profit marketplace, produksi, dan gudang, padahal hari ini pengadaan harian masih berjalan di Accurate (koleksi `barang` belum terbukti dipakai luas; ukur dulu).
- **Risiko**: ERP menjadi sumber kedua bagi fakta yang secara legal milik Accurate; bila seseorang tetap membuat item langsung di Accurate (dan hari ini itu yang terjadi), ERP tertinggal dan butuh arah tarik balik, sehingga sinkron menjadi dua arah, persis bentuk yang paling sering menyimpang. Satu service memegang kebutuhan lima departemen dengan ritme rilis yang berbeda.

### Opsi 3: pemilik per jenis barang, dengan satu kunci bersama

Identitas dibagi menurut jenis, semuanya berkunci sama (kode item Accurate):

| Jenis | Pemilik atribut | Alasan dari kode |
|---|---|---|
| Bahan baku dan kemas | manufacture `manufacture_master_bahan` | sudah menarik dari Accurate, punya faktor satuan (`sync_hpp.go:93-111`) dan penyelaras kode |
| Barang jadi, SKU marketplace, listing, bundle | integration (`product_sku_mappings` sebagai **satu-satunya** definisi bundle; `items.bundle_contents` dipensiunkan atau diturunkan) | profit, faktur harian, dan HPP insentif sudah membaca dari sini |
| Barang GA (aset, perlengkapan) | inventory, lewat `accurate_item_no` / `accurate_asset_no` yang sudah ada | padanan via id internal Accurate sudah berjalan ([[ADR - 0088 Auto-Migrasi Padanan Perlengkapan Lewat ID Internal Accurate, Bukan Konfirmasi Manusia]]) |
| Gudang | satu master (`manufacture_lokasi_gudang` atau daftar gudang Accurate, lihat §Pertanyaan butir 4); rak/lokasi fisik tetap milik WMS sebagai **sub-lokasi** yang merujuk kode gudang | |

- **Konsekuensi**: tiap departemen tetap memegang layarnya, tetapi tak ada lagi yang mengetik nama barang atau nama gudang yang dimiliki modul lain. `warehouse_products` menjadi atribut WMS (barcode, rak) atas kode barang milik pihak lain, bukan master ketiga.
- **Ongkos migrasi**: sedang sampai besar, tetapi bisa bertahap per jenis. Titik paling mahal adalah definisi bundle (menyatukan dua definisi dan memperbaiki salinan manufacture yang tak pernah menghapus) dan baris `master_sku` kosong.
- **Risiko**: "per jenis" butuh aturan siapa yang memutus bila satu barang berganti jenis (bahan yang juga dijual, sampel produk jadi untuk GA); tanpa kunci bersama yang **wajib dan tak boleh kosong**, opsi ini hanya memberi nama resmi pada duplikasi yang ada sekarang. Barang yang belum ada di Accurate (produk baru sebelum dibukukan) butuh status sementara yang jelas.

### Opsi 0 (pembanding): tidak memutuskan

Biaya nyatanya sudah terukur di §Context: angka salah tanpa galat, alat perbaikan satu-kali per insiden, dan penjaga yang ditambal di jalur hitung, bukan di sumber. Tiap modul baru yang butuh barang (Pengajuan Barang [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]], komplain produk, QC) akan memilih salinan sendiri lagi.

## Pertanyaan yang harus dijawab manusia

1. **Siapa pemilik proses master data barang di bisnis?** Bagian mana yang berhak menambah, mengganti nama, dan menonaktifkan barang (Finance/Akuntansi, PPIC, Procurement, atau fungsi Master Data tersendiri), dan siapa yang menyetujuinya? Tanpa jawaban ini, opsi apa pun hanya memindahkan kekacauan ke satu layar.
2. **Apakah barang non-persediaan GA (ATK, perlengkapan, aset) termasuk master yang sama**, atau tetap master terpisah di inventory yang hanya berpadanan ke Accurate?
3. **Apakah bundle marketplace adalah item Accurate** (item grup/paket) atau murni konsep penjualan ERP? Kode tidak menjawab ini (TBD); jawabannya menentukan apakah Opsi 1 bisa memegang bundle.
4. **Apakah Accurate memegang stok per gudang untuk buku besar PT?** Kode menyatakan dua hal berbeda (§Context). Bila ya, daftar gudang Accurate adalah pemilik dan `manufacture_lokasi_gudang` merujuknya; bila tidak, master lokasi ERP yang menjadi pemilik dan Accurate hanya menerima gudang di dokumen penjualan.
5. **Apakah toko konsinyasi adalah gudang** (seperti `LokasiGudang` bertipe `TOKO` sekarang) **atau pelanggan Accurate**? Ini bersinggungan dengan baris Pelanggan/toko di [[REF - Kepemilikan Data]] §Duplikasi.
6. **Barang untuk 40 CV grup**: apakah master barang berlaku lintas badan usaha atau per PT saja (Accurate yang dipakai integrasi adalah pembukuan PT)?
7. **Dua WMS**: `warehouse_products` (warehouse-service) dan master manufacture sama-sama menyimpan barang gudang. Apakah keduanya melayani gudang berbeda (Sadewa vs pabrik) atau salah satunya dipensiunkan?
8. **Baris HPP lama berbasis nama** (`product_costs.master_sku == ""`): dipetakan ke kode, atau dibekukan sebagai riwayat dan dilarang untuk baris baru?

## Rekomendasi penulis (USULAN, bukan keputusan)

Penulis mengusulkan **Opsi 3 dengan identitas dari Accurate**, yaitu gabungan Opsi 1 dan 3:

1. **Kode item Accurate adalah satu-satunya kunci barang** di seluruh ERP, wajib dan tak boleh kosong untuk baris baru. Nama dan satuan dibaca dari cermin Accurate, tidak disalin ke koleksi modul.
2. **Satu pintu tulis ke Accurate** untuk item yang lahir dari ERP: jalur `barang` procurement yang sudah ada (bukan pintu baru). Item yang dibuat langsung di Accurate masuk lewat cermin. Arah tiap fakta tetap satu.
3. **Atribut per jenis tetap di modulnya** (tabel Opsi 3), merujuk kode, tanpa menyalin identitas.
4. **Bundle hanya di `product_sku_mappings`**; `items.bundle_contents` dipensiunkan atau dijadikan tampilan turunan, dan salinan `manufacture_sku_mapping` diganti menjadi salinan penuh yang juga menghapus.
5. **Gudang**: tunggu jawaban §Pertanyaan butir 4. Bila Accurate memegang stok per gudang, daftar gudang Accurate adalah pemilik dan `manufacture_lokasi_gudang` menyimpan kode rujukannya; bila tidak, `manufacture_lokasi_gudang` pemiliknya. Di kedua kasus, semua teks bebas gudang (§Context) diganti rujukan kode, dan rak WMS menjadi sub-lokasi.

Alasannya: Accurate sudah pemilik legal dan tak bisa ditawar untuk buku besar, sehingga menjadikan ERP pemilik identitas (Opsi 2) melahirkan sinkron dua arah; sedangkan Accurate saja (Opsi 1) tak mampu memegang listing dan bundle. Kelemahan usulan ini sama dengan Opsi 1: penambahan barang bergantung pada akses Accurate, dan itu harus dijawab lewat §Pertanyaan butir 1, bukan lewat kode.

## Decision

**TBD.** Diisi setelah §Pertanyaan yang harus dijawab manusia dijawab dan pengambil keputusan ditetapkan. Sampai saat itu, dok ini tidak boleh dikutip sebagai keputusan, dan kode baru yang menyimpan barang atau gudang **tidak** boleh menjadikannya alasan untuk salinan baru.

## Langkah sesudah diputuskan (daftar task kasar)

Urutan mengikuti usulan penulis; disesuaikan bila opsi lain dipilih.

1. **Ukur dulu** (baca saja, prod): jumlah dokumen dan jumlah kode yang tak berpadanan di tiap tempat dari tabel §Context, termasuk `product_costs`/`product_sku_mappings` ber-`master_sku` kosong dan `manufacture_sku_mapping` yang listingnya sudah tak ada di integration. Tanpa angka ini ongkos migrasi hanya tebakan.
2. Tetapkan pemilik gudang (§Pertanyaan butir 4); bila Accurate, tambahkan penarikan daftar gudang ke cermin integration.
3. Wajibkan kunci barang tak kosong untuk baris BARU di `product_sku_mappings`, `product_costs`, `warehouse_products` (baris lama dibiarkan, ditandai).
4. Satukan definisi bundle ke `product_sku_mappings`; ubah salinan `manufacture_sku_mapping` agar menghapus listing yang hilang di sumber.
5. Ganti teks bebas gudang di procurement (`gudang`, `gudang_tujuan`), `MasterBahan.Lokasi`, `departments.warehouse`, dan konstanta FE `GUDANG_GA`/`GUDANG_RM` dengan rujukan kode gudang yang dibaca dari pemiliknya.
6. Cabut jalur tulis identitas yang bukan pemilik (`CreateMaster` manual manufacture, create manual `master_product`, CRUD nama di `warehouse_products`), atau ubah menjadi "ajukan barang baru" ke pemilik.
7. Alihkan pembacaan procurement ke `integration_db` (`kamus.go`) menjadi HTTP ke pemiliknya.
8. Sinkronkan dok: [[REF - Kepemilikan Data]] (pindahkan baris dari §Duplikasi ke §Peta dan §Salinan), [[Microservices - Integration Service]], [[Microservices - Manufacture Service]], [[Microservices - Procurement Service]], [[Microservices - Warehouse Service]].

## Penjaga yang dibutuhkan supaya salinan liar tak tumbuh lagi

- **Pemindai sumber berdaftar-izin** (pola `penjaga_perusahaan_test.go` recruitment dan penjaga `cakupanDepartemenKPI` employee): test yang menolak `InsertOne`/`UpdateOne`/`BulkWrite` ke koleksi identitas barang dan gudang dari berkas di luar service pemiliknya, dan menolak struct baru ber-field `Gudang string`/`Lokasi string` tanpa rujukan kode. ⚠️ Nama koleksi ditulis literal di argumen supaya pemindainya tak lulus tanpa memeriksa (ingatan tim, butir soft-delete).
- **Test kunci kosong dengan fixture yang membedakan**: baris ber-kode kosong ditolak di jalur tulis; fixture yang kodenya sama dengan nama tak menjaga apa pun.
- **Test salinan yang menghapus**: fixture sumber tanpa listing X harus menghasilkan salinan tanpa listing X (menutup kelas `sync_hpp.go:605-619`), dengan kontrol negatif mengembalikan upsert-tanpa-hapus.
- **Pemindai drift cermin Accurate** untuk item dan gudang, pola [[ADR - 0066 Salinan Dokumen Retur Accurate + Pemindai Drift]]: kode yang dirujuk modul tetapi hilang atau berganti nama di Accurate dilaporkan, perbaikan oleh manusia.
- **Test FE** yang menolak konstanta gudang tertulis mati di `src/features/**` (daftar gudang dibaca dari API).
- **Test kontrak** untuk endpoint baca pemilik (bentuk respons nyata, bukan tiruan struct), sesuai pelajaran "memanggil endpoint daftar service lain" di ingatan tim.

## Dokumen Terkait

- [[REF - Kepemilikan Data]] (§Duplikasi: Produk/SKU/bahan baku, Gudang/lokasi, Pelanggan/toko)
- [[REF - Rantai Pengajuan Lintas Modul]]
- [[ADR - 0001 Akuntansi via Accurate]] · [[ADR - 0002 Database-per-Service]]
- [[ADR - 0008 Profit Engine Join via item_group_id]] · [[ADR - 0077 Koreksi Faktur via Impor Rekap Lengkap Mengalir ke Master-Data, Bukan Override per Baris]]
- [[ADR - 0015 Push Pergerakan WMS ke Accurate]] · [[ADR - 0088 Auto-Migrasi Padanan Perlengkapan Lewat ID Internal Accurate, Bukan Konfirmasi Manusia]]
- [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]] · [[ADR - 0079 Target Profit Satu Pintu di Insentif, KPI Membacanya]] · [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]]
- [[Microservices - Integration Service]] · [[Microservices - Manufacture Service]] · [[Microservices - Procurement Service]] · [[Microservices - Warehouse Service]] · [[Microservices - Inventory Service]]
- [[GA - Inventory Management]] · [[WH - Warehouse Sadewa]]
