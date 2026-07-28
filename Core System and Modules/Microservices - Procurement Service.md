## Deskripsi

*Microservice **procurement-service** — master Pemasok yang diinput di BIP-ERP lalu disinkronkan otomatis ke Accurate Online. Tujuannya agar staf procurement tidak perlu lagi membuka Accurate untuk pendaftaran pemasok harian.*

- **Stack**: Go + Fiber v2 + MongoDB (driver resmi) + shared-library; di belakang [[CORE - API Master Gateway]] (`/api/procurement/*`), seluruh route internal dilindungi `BIP-Gateway-ID` + role guard `system_roles["procurement"]`.
- **Path di repo**: `bip-erp/services/procurement/` · flat package `main` · `models.go` (entity + peta prefix→kategori) · `accurate_client.go` (transport) · `accurate_vendor.go` (payload + method vendor) · `nomor.go` (usul nomor) · `sync.go` (worker antrian) · `pemasok.go` (handler CRUD) · `import.go` (import awal).
- **Port**: `6983` (default). **Database**: `procurement_db` (MongoDB per-service, host port `32794`). **Env kunci**: `MONGO_URI`, `MONGO_DB`, `INTERNAL_GATEWAY_KEY`, `ACCURATE_ACCOUNT_URL`, `ACCURATE_SECRET_KEY`, `ACCURATE_BEARER_TOKEN`.
- **Status**: ⚠️ Implemented (ada catatan) — backend lengkap & terverifikasi berjalan lokal (boot, index, guard, CRUD, penomoran) ✅; **belum di-deploy** dan **import 139 pemasok belum dijalankan** (butuh kredensial Accurate); frontend terpisah.
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

Pemisahan ini mencegah import ulang menghapus isian user di ERP — khususnya Akun Utang, yang tidak dapat disinkronkan lewat API sehingga ERP menjadi satu-satunya tempat nilainya hidup.

## Belum Diimplementasikan / Catatan

- **Belum di-deploy.** Backend terverifikasi berjalan di lingkungan lokal (Docker), belum pernah dijalankan di server.
- **Import 139 pemasok belum dijalankan.** Kredensial Accurate hanya tersedia di server produksi, tidak ada di lingkungan lokal.
- **Belum pernah menulis ke Accurate.** Seluruh perilaku payload bersumber dari OpenAPI resmi Accurate v1.4467.1872 dan pengamatan 139 pemasok produksi (read-only). Verifikasi nyata terjadi saat pemasok asli pertama dibuat.
- **Empat field dapat DIBACA tetapi tidak dapat DITULIS** lewat API: **Akun Utang**
  (`vendorPayableAccountList`), Akun Uang Muka (`vendorDownPaymentAccountList`),
  **Tipe Pemasok** (`vendorType`), dan Jenis Dokumen (`documentCode`, terisi
  `DIGUNGGUNG` pada 139/139 pemasok produksi).

  Keempatnya dikembalikan `detail.do` dengan nilai lengkap — probe read-only
  menunjukkan `detail.do` mengembalikan **87 field** sedangkan `save.do` hanya
  menerima **36**, jadi ada 51 field yang terbaca tetapi tak tertulis. Contoh
  nyata: `PBK-018 → vendorType=COMPANY, utang=2101, uang muka=1504`.

  Konsekuensinya ERP dapat **menampilkan** keempatnya (hasil import) tetapi
  pengisiannya dilakukan finance langsung di Accurate. Bila field akun tetap
  dikirim, Accurate mengabaikannya diam-diam sehingga request tampak sukses
  padahal akun tetap kosong.

  Sebagai pembanding, `customer/save.do` **punya** `customerReceivableAccountListNo`
  — Accurate menyediakannya untuk pelanggan tetapi tidak untuk pemasok.

  **Peringatan pembacaan:** kesimpulan "tidak dapat ditulis" bersumber dari
  spesifikasi OpenAPI yang **terakhir diperbarui 16 Agustus 2024**, sedangkan
  nilai `CTAS_KEPADA_SELAIN_PEMUNGUT_PPN` yang dipakai 53 pemasok produksi
  **tidak ada** di enum spec itu. Spec karena itu terbukti tertinggal dari
  server, dan kemungkinan server menerima field yang tak terdaftar belum dapat
  disingkirkan tanpa uji tulis.
- **Pengosongan nilai belum tersinkron (TBD).** Field opsional memakai `omitempty`, sehingga menghapus nilai yang sebelumnya terisi tidak sampai ke Accurate — Accurate mempertahankan nilai lama. Benar untuk pembuatan pemasok baru, tetapi bug diam untuk suntingan. Belum diperbaiki karena bergantung pada perilaku Accurate yang belum diverifikasi (apakah `save.do` menerima string kosong sebagai perintah mengosongkan). Wajib diuji saat pemasok asli pertama disunting.
- **Default jenis pajak CTAS menunggu konfirmasi finance.** Datanya kuat (16 pemasok terbaru 100% CTAS; `PRLHNDLMNEGERI_BKN_PPN` dilabeli Accurate sendiri sebagai *legacy*), tetapi penentuan perlakuan pajak adalah ranah finance.

## Jebakan Integrasi Accurate (grounded, terverifikasi)

Tiga hal yang paling mudah salah dan sudah dikunci test:

1. **Referensi memakai NAMA, bukan id.** `vendor/save.do` menerima `categoryName` dan `termName`, sedangkan `detail.do` mengembalikan `categoryId`/`defaultTermId`. Mengirim id akan ditolak.
2. **Akun Utang tidak boleh masuk payload.** Lihat catatan di atas — kebocoran menghasilkan sukses palsu yang tidak terdeteksi di produksi.
3. **Nama syarat pembayaran dipotong 20 karakter oleh Accurate.** Term id 300 bernama `"DP 50%, Pelunasan Se"` (tepat 20 karakter) sementara teks lengkapnya hanya ada di `memo`. Yang dikirim ke API harus bentuk terpotong; `memo` hanya untuk tampilan.

Selain itu: **`transDate` wajib** (format `dd/MM/yyyy`) meskipun pemasok bukan transaksi, dan **dihitung dalam WIB** — antara 00:00–07:00 WIB, UTC masih berada di tanggal sebelumnya sehingga tanggal pengakuan bisa mundur satu hari dan masuk periode pembukuan yang keliru. Zona waktu dikunci di kode, tidak bergantung pada variabel `TZ` lingkungan.

## Model Data

Koleksi `pemasok` di `procurement_db`. Index:

| Index | Sifat | Alasan |
|---|---|---|
| `vendor_no` | unique | Nomor diketik manual; database menjadi penjaga terakhir bila dua orang menyimpan nomor sama nyaris bersamaan. |
| `accurate_id` | unique + partial (`$gt: 0`) | Sparse tidak cukup — `accurate_id` bertipe `int64` sehingga pemasok baru bisa bernilai 0. Partial filter membatasi keunikan pada baris yang benar-benar sudah tersinkron. |
| `sync_status` + `next_retry_at` | biasa | Dipakai worker mengambil antrian. |

## Dependensi & Integrasi

- **Accurate Online** — [[ADR - 0001 Akuntansi via Accurate]]. Endpoint yang dipakai: `vendor/save.do`, `vendor/list.do`, `vendor/detail.do`, `payment-term/list.do`. Klien Accurate **disalin** ke service ini (bukan diimpor dari integration) mengikuti pola [[Microservices - Manufacture Service]] yang juga berbicara langsung ke Accurate; endpoint vendor sama sekali tidak dipakai integration sehingga tidak ada logika terduplikasi.
- **Kredensial Accurate dibagi** dengan [[Microservices - Integration Service]] — satu database Accurate yang sama.
- **Gateway**: [[CORE - API Master Gateway]] (`PROCUREMENT_MODULE_URL`).

## Dokumen Terkait

- [[API - Procurement Service]]
- [[ADR - 0001 Akuntansi via Accurate]]
- [[Microservices - Integration Service]]
- [[Microservices - Manufacture Service]]
