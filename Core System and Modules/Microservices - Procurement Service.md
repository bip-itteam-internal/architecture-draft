## Deskripsi

*Microservice **procurement-service** — master Pemasok, master Barang & Jasa, Tagihan Pemasok, dan cermin baca-saja Pembelian (Pesanan/Penerimaan/Permintaan Barang) dari Accurate Online. Master data diinput di BIP-ERP lalu disinkronkan otomatis ke Accurate; Pembelian arahnya kebalikannya — dicatat finance langsung di Accurate lalu ditarik otomatis ke ERP untuk dipantau.*

- **Stack**: Go + Fiber v2 + MongoDB (driver resmi) + shared-library; di belakang [[CORE - API Master Gateway]] (`/api/procurement/*`), seluruh route internal dilindungi `BIP-Gateway-ID` + role guard `system_roles["procurement"]`.
- **Path di repo**: `bip-erp/services/procurement/` · flat package `main` · `models.go` (entity + peta prefix→kategori pemasok) · `accurate_client.go` (transport) · `accurate_vendor.go` (payload + method vendor) · `accurate_item.go` (payload + method barang) · `nomor.go` (usul nomor pemasok) · `sync.go` (worker antrian, kedua entity) · `pemasok.go` (handler CRUD pemasok) · `barang.go` (handler CRUD barang, termasuk usul kode) · `import.go` / `import_barang.go` (import awal) · `pesanan.go` / `penerimaan.go` / `permintaan.go` (entity cermin Pembelian, termasuk field penandaan "barang tidak sesuai" milik ERP di `penerimaan.go`) · `pembelian_handler.go` (handler daftar + baris turunan penerimaan + handler tandai/batal-tandai tidak sesuai) · `sync_pembelian.go` (worker impor terjadwal).
- **Port**: `6983` (default). **Database**: `procurement_db` (MongoDB per-service, host port `32794`). **Env kunci**: `MONGO_URI`, `MONGO_DB`, `INTERNAL_GATEWAY_KEY`, `ACCURATE_ACCOUNT_URL`, `ACCURATE_SECRET_KEY`, `ACCURATE_BEARER_TOKEN`.
- **Status**: ⚠️ Implemented (ada catatan) — backend Pemasok + Barang & Jasa lengkap & terverifikasi lokal (boot, index, guard, CRUD, penomoran; 139 test PASS) ✅; **belum di-deploy** dan **import awal (pemasok maupun barang) belum dijalankan** di produksi (butuh kredensial Accurate). Modul **Pembelian** (PR #810, merged) ✅ terverifikasi lokal — 1.036 Pesanan, 1.835 Penerimaan, 234 Permintaan tertarik dari Accurate produksi (read-only, tanpa menulis). Frontend Master Pemasok, Barang & Jasa, **dan** ketiga tab Pembelian sudah ada di `erp-frontend` (`src/features/procurement/`) — lihat [[APP - Web ERP]].
- **API**: [[API - Procurement Service]].

## Endpoint / Fitur (Sudah Diimplementasikan)

Daftar rute lengkap di [[API - Procurement Service]]. Ringkas:

### Master Pemasok (`pemasok.go`)

- **`GET /pemasok`** — daftar pemasok; filter `cari` (nama/nomor), `kategori`, `sync_status`, dan `akun_utang_kosong=true` (daftar pantauan finance).
- **`GET /pemasok/usul-nomor?kategori=`** — usulan nomor berikut per kategori.
- **`POST /pemasok`** — buat pemasok. Menolak nomor bentrok dengan **409**. Status awal `PENDING` (masuk antrian sync), jenis pajak default CTAS. Id hasil insert dikembalikan ke client supaya pemasok baru dapat langsung disunting.
- **`PUT /pemasok/:id`** — sunting pemasok. `accurate_id` selalu diambil dari data lama, **tidak pernah** dari kiriman client — nilai karangan bisa menimpa pemasok lain di Accurate. Setiap suntingan mengantre ulang (`PENDING`) dengan `sync_attempts` direset.
- **`GET /katalog/syarat-pembayaran`** — opsi syarat pembayaran dari Accurate.
- **`POST /import`** — import awal seluruh pemasok dari Accurate (role `admin`).

### Master Barang & Jasa (`barang.go`)

- **`GET /barang`** — daftar barang; filter `cari` (nama/kode), `kategori`, `jenis_barang`, `sync_status`.
- **`GET /barang/usul-kode`** — usulan kode berikut, format **`BRG-{angka}`**, dari kode **tertinggi di seluruh koleksi** (bukan per-kategori — beda dari `usul-nomor` pemasok, karena kategori barang berasal dari katalog Accurate yang terbuka, tidak ada skema prefix tetap). Parameter `kategori` diterima untuk konsistensi bentuk endpoint dengan pemasok tapi **tidak memengaruhi hasil**.
- **`POST /barang`** — buat barang. Empat field wajib (selaras `item/save.do`): `nama`, `kategori`, `jenis_barang` (enum `INVENTORY`/`NON_INVENTORY`/`SERVICE`/`GROUP`/`PRODUCTION_COST`), `satuan`. Menolak kode bentrok dengan **409**. Status awal `PENDING`.
- **`PUT /barang/:id`** — sunting barang. `accurate_id` selalu dari data lama. Toggle boolean (`pakai_ppn`, `kelola_nomor_seri`, `pakai_kadaluarsa`) pada edit parsial **hanya bisa diaktifkan, tidak bisa dinonaktifkan** oleh request yang tidak mengirim field itu — plain `bool` tidak bisa membedakan "false dikirim" dari "field tak dikirim". Tidak terasa di FE ERP karena form selalu mengirim seluruh field toggle; ini murni pengaman terhadap client yang mengirim payload parsial.
- **`GET /katalog/kategori-barang`**, **`GET /katalog/satuan`**, **`GET /katalog/pajak`** — opsi dari Accurate (`item-category/list.do`, `unit/list.do`, `tax/list.do`), bentuk `{nama, tampilan}` sama seperti katalog pemasok.
- **`POST /barang/import`** — import awal seluruh barang dari Accurate (role `admin`), idempoten dengan kunci `accurate_id`.

Nomor seri: `kelola_nomor_seri` (manageSN) mengaktifkan pilihan `tipe_nomor_seri` (`UNIQUE`/`BATCH`, enum `SerialNumberType`) dan `pakai_kadaluarsa` (manageExpired) — keduanya hanya dikirim ke Accurate bila nomor seri aktif; mengirim tipe nomor seri tanpa mengaktifkan nomor seri tidak masuk akal secara bisnis.

**Dua field baca-saja** (sama polanya dengan Tipe Pemasok): **Merek Barang** (`itemBrand`) dan **Tipe Persediaan** (`materialProduced`/`itemProduced`) tidak ada di antara 58 parameter `item/save.do` — Accurate mengabaikannya diam-diam bila dikirim. Struct `ItemPayload` sengaja tidak mendeklarasikan keduanya sama sekali; nilainya hanya terisi lewat import (`detail.do`).

`materialProduced`/`itemProduced` di respons `detail.do` adalah **boolean** (bukan string) — terbukti di server testing dengan Accurate sungguhan: mendeklarasikannya sebagai `string` membuat unmarshal gagal pada **setiap** barang, sehingga `POST /barang/import` mengembalikan `terimpor:0` walau ratusan barang tersedia. Diperbaiki: `ItemDetail.MaterialProduced`/`ItemProduced` sekarang `bool`, diterjemahkan ke `Barang.TipePersediaan` (string tampilan: "Bahan Baku", "Diproduksi", atau "Bahan Baku, Diproduksi" bila keduanya aktif) lewat `tipePersediaanDari()` di `import_barang.go`. Perbaikan terverifikasi di level test (139 PASS); **belum diverifikasi ulang di server testing produksi** (butuh re-run import barang).

### Pembelian — cermin Accurate BACA-SAJA (`pesanan.go`, `penerimaan.go`, `permintaan.go`, `pembelian_handler.go`)

Arah data **kebalikan** dari Pemasok/Barang: pesanan, penerimaan, dan permintaan barang dicatat finance **langsung di Accurate** (bukan di ERP), lalu ditarik ke sini agar terlihat tanpa membuka Accurate. Rute-nya berdiri **terpisah** dari `/po` lama — `/po` adalah pesanan yang *dibuat* lewat ERP (koleksi `purchase_order`, 0 dokumen di produksi, form-nya disembunyikan dari tab), sedangkan `/pesanan` mencerminkan 1.036 pesanan nyata dari Accurate. Menyatukan keduanya akan membuat antrean sync PO menjaring dokumen cermin dan mengirimkannya balik ke Accurate sebagai pesanan baru.

Seluruh rute daftar (`GET /pesanan`, `/penerimaan`, `/permintaan`) membaca Mongo **saja** — tidak satu pun memanggil Accurate saat layar dibuka; kata pengguna sendiri: *"jangan menampilkan langsung call yah boros api"*.

- **`GET /pesanan?vendor_no=&status=`** — daftar pesanan, cermin `purchase-order/list.do`. Nama/nomor pemasok datang dari objek `vendor` **bersarang** Accurate (`vendorId`/`vendorName` hilang dari list.do) — backend meratakannya ke `vendor_no`/`vendor_nama`. Disaring atas `status_name` (teks yang terlihat staf di Accurate), bukan `status`.
- **`GET /penerimaan?status=`** — daftar penerimaan, cermin `receive-item/list.do`, **plus** baris turunan `pesanan_nomor`/`selisih_hari`/`punya_selisih`/`terlambat` yang dihitung **saat dibaca** (bukan disimpan) dengan memasangkan `pesanan_accurate_id` ke koleksi pesanan. Field `status` **hilang** dari `receive-item/list.do` — status yang tampil selalu dari `statusName` ("Difaktur").
  - **Ketepatan waktu kirim dibatasi 6 bulan.** `purchaseOrderId` (kunci pemasangan ke pesanan) **hilang** dari `receive-item/list.do` dan hanya tersedia lewat `receive-item/detail.do` — memanggil detail untuk *seluruh* penerimaan tidak murah, sehingga hanya jendela 6 bulan terakhir yang ditarik detailnya. Respons membawa `detail_dari`/`detail_sampai` (format Accurate `dd/MM/yyyy`) supaya layar **wajib** menyebut periodenya — tanpanya, cakupan 6 bulan terbaca sebagai klaim sepanjang masa.
  - **Tiga keadaan dibedakan secara eksplisit** (`BarisPenerimaanTampil`), karena tindakannya beda: (1) `punya_selisih=true` → tertaut pesanan berjanji kirim, `selisih_hari` berarti; (2) `punya_selisih=false, detail_terambil=true` → memang pembelian langsung tanpa pesanan, tidak perlu ditindaklanjuti; (3) `punya_selisih=false, detail_terambil=false` → detailnya belum ditarik (di luar jendela 6 bulan atau menunggu penyegaran berikutnya). `terlambat` **selalu false** bila `punya_selisih=false` — menyatakan keterlambatan atas janji kirim yang tak diketahui adalah tuduhan tanpa dasar terhadap pemasok.
- **`GET /permintaan?status=`** — daftar permintaan barang, cermin `purchase-requisition/list.do`. Hanya `id`, `number`, `transDate`, `status`, `statusName` — `requisitionType` **hilang** dari list.do, sehingga hanya tiga kolom yang ditampilkan (bukan kekurangan yang perlu ditutupi).
- **`GET /penerimaan?hanya_tidak_sesuai=true`** — menyaring daftar penerimaan yang sudah **ditandai barang tidak sesuai**, lewat rute `GET /penerimaan` yang sama (bukan endpoint terpisah). `hanyaTidakSesuai=false` (bawaan) **tidak menyentuh filter sama sekali** — daftar Penerimaan biasa tetap menampilkan seluruh baris, tertandai maupun tidak, karena penandaan **tidak memindahkan/menyembunyikan** baris dari Penerimaan.
- **`POST /penerimaan/:id/tandai-tidak-sesuai`** — menandai satu penerimaan sebagai barang tidak sesuai (rusak/kurang/salah kirim). Body `{"keterangan": "..."}`, keterangan **wajib diisi** (`ValidasiTandaiTidakSesuai`, 400 bila kosong/hanya-spasi). **Catatan milik ERP murni — Accurate tidak pernah disentuh**, supaya penerimaan tetap cermin Accurate yang utuh. Digerbang `tulisPO` (bukan permission baru): satu alur kerja dengan penerimaan barang, dan permission baru akan tertanam di token saat login sehingga memaksa seluruh pengguna logout-login ulang — biaya yang tidak sepadan untuk fitur sekecil ini.
- **`POST /penerimaan/:id/batal-tandai-tidak-sesuai`** — membatalkan penandaan. Keterangan/penanda/waktu **dikosongkan**, bukan dibiarkan, supaya tak ada jejak menggantung yang menyesatkan setelah dicabut. Digerbang `tulisPO` sama seperti menandai.
  - Empat field penandaan (`tidak_sesuai`, `keterangan_tidak_sesuai`, `tidak_sesuai_oleh`, `tidak_sesuai_pada`) lahir **hanya** lewat `$setOnInsert` pada baris baru — **tidak pernah** lewat `$set` lapis impor (ringkas maupun detail). Worker sinkron berjalan 2x sehari; bila field ini bocor ke `$set`, penandaan gudang akan terhapus setiap putaran impor tanpa ada yang sadar. Dikunci test mutasi eksplisit (lihat `penerimaan_test.go`).
- **`GET /pembelian/status`** — kemajuan impor per modul (`pesanan`/`penerimaan`/`permintaan`): kapan **terakhir berhasil**, jumlah baris terakhir, DAN apakah percobaan **terakhir gagal** (`gagal_pada`/`gagal_pesan`) — keduanya wajib tampil bersama supaya kegagalan tidak berubah menjadi deretan nol yang terbaca "tidak ada data" padahal cuma data lama yang basi.
- **`POST /pembelian/impor`** — penyegaran manual ketiga modul sekaligus, role terpisah (`imporMassal`, bukan `akses` biasa — satu klik menembak Accurate puluhan hingga ratusan kali). Balas 200 selama **ada** yang berhasil (rincian per-modul di badan); 502 hanya bila **ketiganya** gagal — "penerimaan gagal, pesanan berhasil" adalah keberhasilan sebagian yang sah, bukan kegagalan total yang membuang hasil yang sudah tersimpan.

**Penyegaran otomatis dua kali sehari** (`sync_pembelian.go`, `JamImporWIB = [6, 18]` WIB) — keputusan pengguna: 06:00 mendahului jam kerja supaya layar sudah segar saat dibuka, 18:00 menangkap dokumen yang dicatat finance sepanjang hari. `PerluImporTerjadwal` membandingkan **keberhasilan terakhir** terhadap slot jadwal terakhir yang sudah terlewati (bukan "tepat pukul 06:00") — service yang baru hidup pukul 09:00 langsung mengejar slot 06:00 yang terlewat, dan koleksi yang belum pernah berhasil sama sekali (`terakhir == nil`) selalu memicu impor segera. Impor manual (`POST /pembelian/impor`) tetap tersedia sebagai lantai tambahan, bukan pengganti jadwal.

### Penomoran (`nomor.go`)

Nomor diketik manual oleh user; ERP hanya **mengusulkan** nomor berikut berdasarkan yang tertinggi per kategori (`PBB-060` → usul `PBB-061`). Prefix memetakan 1:1 ke kategori dan konsisten pada seluruh 139 pemasok produksi: `PBB` → Pemasok Bahan Baku, `PBK` → Pemasok Bahan Kemas, `PU` → Umum.

Lubang penomoran **tidak didaur ulang**: `PU-025` kosong di produksi (pemasok pernah dihapus), tetapi usulan tetap melanjutkan dari tertinggi (`PU-036`) karena nomor bekas berisiko masih dirujuk dokumen lama di Accurate.

### Worker Sync (`sync.go`)

Handler HTTP hanya menulis ke Mongo lalu langsung membalas; pengiriman ke Accurate dikerjakan worker terpisah. Ketikan user karena itu tidak tersandera ketersediaan Accurate.

Worker berjalan tiap 30 detik dan **hanya** menyentuh baris berstatus `PENDING`/`FAILED` yang `next_retry_at`-nya sudah lewat — nol perubahan berarti nol panggilan Accurate, tidak ada polling seluruh daftar pemasok. Kegagalan menyimpan pesan aslinya di `sync_error` (kegagalan tidak pernah senyap) dan dijadwalkan ulang dengan jeda menaik 1→2→4→8→16→32 menit, dibatasi 1 jam.

### Import Awal (`import.go`)

Menarik seluruh pemasok dari Accurate lalu upsert dengan kunci `accurate_id`, sehingga idempoten (dijalankan berulang tetap menghasilkan jumlah baris yang sama). Baris hasil import ditandai `SYNCED` — menandainya `PENDING` akan membuat worker mengirim ulang seluruh pemasok dan berpotensi menggandakan data di Accurate.

Import memisahkan dua kelompok field:

- **Milik Accurate** (selalu diperbarui): identitas, kategori, kontak, alamat, syarat pembayaran, status sync.
- **Hanya saat baris baru** (`$setOnInsert`): `akun_utang`, `jenis_pajak`, `nama_wajib_pajak`, `negara`.

Pemisahan ini mencegah import ulang menghapus isian user di ERP. Akun Utang dan
Akun Uang Muka kini termasuk **milik Accurate** (ikut diperbarui saat import),
karena keduanya benar-benar dikirim dan Accurate menjadi sumbernya.

## Belum Diimplementasikan / Catatan

- **Belum di-deploy.** Backend terverifikasi berjalan di lingkungan lokal (Docker), belum pernah dijalankan di server.
- **Import 139 pemasok belum dijalankan.** Kredensial Accurate hanya tersedia di server produksi, tidak ada di lingkungan lokal.
- **Import awal barang juga belum dijalankan di produksi**, alasan sama (kredensial Accurate). `ImportBarangDenganKlien` idempoten (kunci `accurate_id`) dan terverifikasi lewat test, tapi belum pernah menyentuh data Accurate sungguhan.
- **Barang tidak punya field milik-ERP-murni** seperti `jenis_pajak`/`negara` pada pemasok — seluruh data barang bersumber dari Accurate, jadi `FieldBarangSaatBaru` (bagian `$setOnInsert` import) hanya menyetel `sync_attempts`.
- **Belum pernah menulis ke Accurate.** Seluruh perilaku payload bersumber dari
  dokumentasi API **resmi** Accurate (`docs/accurate-api/accurate-api-resmi.json`,
  versi 1.0.1#4611) dan pengamatan 139 pemasok produksi (read-only). Verifikasi
  nyata terjadi saat pemasok asli pertama dibuat.
- **Dua field tidak dapat DITULIS** lewat API — hanya terbaca dari `detail.do`:
  **Tipe Pemasok** (`vendorType`) dan **Jenis Dokumen** (`documentCode`, terisi
  `DIGUNGGUNG` pada 139/139 pemasok produksi). Keduanya tidak ada di antara 41
  parameter `vendor/save.do`. ERP menampilkannya sebagai nilai baca-saja hasil
  import; pengisiannya dilakukan finance di Accurate.

  > **Koreksi 2026-07-28.** Sebelumnya dokumen ini menyatakan **empat** field
  > tidak dapat ditulis — Akun Utang dan Akun Uang Muka ikut disebut. Itu
  > **KELIRU**. Kesimpulan tersebut berasal dari spec SwaggerHub yang terakhir
  > diperbarui 16 Agustus 2024. Dokumentasi resmi menyediakan
  > `vendorPayableAccountListNo` ("Kode Akun Hutang") dan
  > `vendorDownPaymentAccountListNo` ("Kode Akun Uang Muka") — keduanya kini
  > **benar-benar dikirim**. Lihat `docs/accurate-api/README.md`.
- **WhatsApp tidak tersinkron.** `vendor/save.do` tidak punya field WhatsApp
  (`bbmPin` milik `EmployeeParam`, bukan `VendorParam`), sehingga `no_wa` hanya
  tersimpan di ERP. Mengirimkannya membuat Accurate mengabaikannya diam-diam.
- **Pengosongan nilai belum tersinkron (TBD).** Field opsional memakai `omitempty`, sehingga menghapus nilai yang sebelumnya terisi tidak sampai ke Accurate — Accurate mempertahankan nilai lama. Benar untuk pembuatan pemasok baru, tetapi bug diam untuk suntingan. Belum diperbaiki karena bergantung pada perilaku Accurate yang belum diverifikasi (apakah `save.do` menerima string kosong sebagai perintah mengosongkan). Wajib diuji saat pemasok asli pertama disunting.
- **Default jenis pajak CTAS menunggu konfirmasi finance.** Datanya kuat (16 pemasok terbaru 100% CTAS; `PRLHNDLMNEGERI_BKN_PPN` dilabeli Accurate sendiri sebagai *legacy*), tetapi penentuan perlakuan pajak adalah ranah finance.

## Jebakan Integrasi Accurate (grounded, terverifikasi)

Tiga hal yang paling mudah salah dan sudah dikunci test:

1. **Referensi memakai NAMA, bukan id.** `vendor/save.do` menerima `categoryName` dan `termName`, sedangkan `detail.do` mengembalikan `categoryId`/`defaultTermId`. Mengirim id akan ditolak.
2. **Field yang tidak ada di `vendor/save.do` jangan dikirim.** Accurate
   mengabaikannya diam-diam sehingga request tampak sukses padahal nilainya tidak
   tersimpan — sukses palsu yang tidak terdeteksi di produksi. Yang terbukti
   tidak ada: `vendorType`, `documentCode`, `bbmPin` (WhatsApp). Sebaliknya
   `vendorPayableAccountListNo` dan `vendorDownPaymentAccountListNo` **ada** dan
   wajib dikirim.
3. **Nama syarat pembayaran dipotong 20 karakter oleh Accurate.** Term id 300 bernama `"DP 50%, Pelunasan Se"` (tepat 20 karakter) sementara teks lengkapnya hanya ada di `memo`. Yang dikirim ke API harus bentuk terpotong; `memo` hanya untuk tampilan.

Selain itu: **`transDate` wajib** (format `dd/MM/yyyy`) meskipun pemasok bukan transaksi, dan **dihitung dalam WIB** — antara 00:00–07:00 WIB, UTC masih berada di tanggal sebelumnya sehingga tanggal pengakuan bisa mundur satu hari dan masuk periode pembukuan yang keliru. Zona waktu dikunci di kode, tidak bergantung pada variabel `TZ` lingkungan.

## Model Data

Koleksi `pemasok` di `procurement_db`. Index:

| Index | Sifat | Alasan |
|---|---|---|
| `vendor_no` | unique | Nomor diketik manual; database menjadi penjaga terakhir bila dua orang menyimpan nomor sama nyaris bersamaan. |
| `accurate_id` | unique + partial (`$gt: 0`) | Sparse tidak cukup — `accurate_id` bertipe `int64` sehingga pemasok baru bisa bernilai 0. Partial filter membatasi keunikan pada baris yang benar-benar sudah tersinkron. |
| `sync_status` + `next_retry_at` | biasa | Dipakai worker mengambil antrian. |

Koleksi `barang` di `procurement_db` — indeks berpola identik:

| Index | Sifat | Alasan |
|---|---|---|
| `kode` | unique (`kode_unique`) | Penomoran otomatis (`UsulKodeBarangBerikut`) hanya usulan; database tetap penjaga terakhir. |
| `accurate_id` | unique + partial `$gt: 0` (`accurate_id_unique`) | Sama alasannya dengan pemasok — barang baru bernilai `accurate_id: 0`. |
| `sync_status` + `next_retry_at` | biasa (`antrian_sync_barang`) | Dipakai worker mengambil antrian, baris pemasok maupun barang diproses worker yang sama. |

Koleksi `pesanan`, `penerimaan`, `permintaan` di `procurement_db` (cermin Pembelian) — indeks berpola sama untuk ketiganya:

| Index | Sifat | Alasan |
|---|---|---|
| `accurate_id` | unique (`pesanan_accurate_id_unique` / `penerimaan_accurate_id_unique` / `permintaan_accurate_id_unique`) | Kunci upsert impor — dijalankan berulang tetap idempoten, tidak menggandakan dokumen. |

Ditambah koleksi `impor_kemajuan` (index `modul` unique, `impor_kemajuan_modul_unique`) — satu baris per modul (`pesanan`/`penerimaan`/`permintaan`) menyimpan `berhasil_pada`/`gagal_pada`/`gagal_pesan`, sumber `GET /pembelian/status`.

## Dependensi & Integrasi

- **Accurate Online** — [[ADR - 0001 Akuntansi via Accurate]]. Endpoint yang dipakai: `vendor/save.do`, `vendor/list.do`, `vendor/detail.do`, `payment-term/list.do`, dan untuk Pembelian: `purchase-order/list.do`, `receive-item/list.do` + `receive-item/detail.do` (jendela 6 bulan), `purchase-requisition/list.do`. Klien Accurate **disalin** ke service ini (bukan diimpor dari integration) mengikuti pola [[Microservices - Manufacture Service]] yang juga berbicara langsung ke Accurate; endpoint vendor sama sekali tidak dipakai integration sehingga tidak ada logika terduplikasi.
- **Kredensial Accurate dibagi** dengan [[Microservices - Integration Service]] — satu database Accurate yang sama.
- **Gateway**: [[CORE - API Master Gateway]] (`PROCUREMENT_MODULE_URL`).

## Dokumen Terkait

- [[API - Procurement Service]]
- [[ADR - 0001 Akuntansi via Accurate]]
- [[Microservices - Integration Service]]
- [[Microservices - Manufacture Service]]
