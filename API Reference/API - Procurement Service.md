## Deskripsi

*Endpoint **procurement-service** (master Pemasok + master Barang & Jasa: CRUD, penomoran, katalog, import awal, worker sync ke Accurate; plus cermin baca-saja Pembelian: Pesanan/Penerimaan/Permintaan Barang). Gateway: `/api/procurement/*`. Grounded ke `services/procurement/`.*

- **Implementasi**: [[Microservices - Procurement Service]] · **Status**: ⚠️ Implemented (ada catatan) — backend Pemasok/Barang lengkap & terverifikasi berjalan lokal (119 test PASS); belum di-deploy, import awal (pemasok maupun barang) belum dijalankan di produksi. Modul Pembelian (PR #810) ✅ terverifikasi terhadap Accurate produksi read-only.
- **Indeks**: [[API - Index]] · Auth: gateway key `BIP-Gateway-ID` untuk semua route, plus role guard via `BIP-System-Roles` header (`system_roles["procurement"]`). Role yang diterima: `staff`, `spv`, `admin`; route import khusus `admin`.

## Master Pemasok (✅ Diimplementasikan)

| Method | Path | Fungsi |
|---|---|---|
| GET | `/pemasok` | Daftar pemasok. Query: `cari` (nama/nomor, regex case-insensitive), `kategori`, `sync_status`, `akun_utang_kosong=true` (daftar pantauan finance). |
| GET | `/pemasok/usul-nomor?kategori=` | Usulan nomor berikut per kategori. `400` bila kategori tidak dikenal. |
| POST | `/pemasok` | Buat pemasok. `201` + data (termasuk `id` hasil insert). `400` validasi gagal, `409` nomor sudah dipakai. |
| PUT | `/pemasok/:id` | Sunting pemasok. `400` id/body/validasi gagal, `404` tidak ditemukan, `409` nomor dipakai pemasok lain. |
| GET | `/katalog/syarat-pembayaran` | Opsi syarat pembayaran dari Accurate. `502` bila Accurate tidak dapat dihubungi. |
| GET | `/katalog/akun-utang` | Akun bertipe `ACCOUNT_PAYABLE` dari bagan akun Accurate (akun nonaktif dibuang). Mengisi dropdown Akun Utang agar staf memilih akun yang benar-benar ada. `502` bila Accurate tidak dapat dihubungi. |
| POST | `/import` | Import awal seluruh pemasok dari Accurate (role `admin`). Idempoten. `502` bila Accurate gagal. |
| GET | `/health` | Health check (tanpa auth). |

**Request body** `POST /pemasok` & `PUT /pemasok/:id`:
```json
{
  "nama":              "string (wajib)",
  "vendor_no":         "string (wajib) — format <PREFIX>-<angka>, prefix harus cocok kategori",
  "kategori":          "string (wajib) — Pemasok Bahan Baku / Pemasok Bahan Kemas / Umum",
  "no_wa":             "string — WhatsApp; Accurate menyimpannya di bbmPin",
  "no_hp":             "string — Handphone; Accurate mobilePhone",
  "telp_bisnis":       "string — Accurate workPhone",
  "faksimili":         "string — Accurate fax",
  "website":           "string",
  "mata_uang":         "string — Accurate currencyCode, mis. IDR",
  "email":             "string",
  "alamat":            { "jalan": "string", "kota": "string", "provinsi": "string", "kode_pos": "string" },
  "syarat_pembayaran": "string — nama term PERSIS seperti di Accurate (bisa terpotong 20 karakter)",
  "akun_utang":        "string — disimpan di ERP, TIDAK dikirim ke Accurate",
  "jenis_pajak":       "string — CTAS_KEPADA_SELAIN_PEMUNGUT_PPN (default) / PRLHNDLMNEGERI_BKN_PPN",
  "nama_wajib_pajak":  "string — kosongkan bila sama dengan nama; tidak diturunkan otomatis",
  "negara":            "string"
}
```

**Response** (bentuk `Pemasok`):
```json
{
  "data": {
    "id": "6a68a8f454ac69964f06f7ea",
    "nama": "CV Contoh Jaya",
    "vendor_no": "PBB-061",
    "kategori": "Pemasok Bahan Baku",
    "no_wa": "0812xxxxxxx",
    "no_hp": "0813xxxxxxx",
    "telp_bisnis": "0274-xxxxxx",
    "faksimili": "",
    "website": "",
    "mata_uang": "IDR",
    "email": "kontak@contoh.co.id",
    "alamat": { "jalan": "...", "kota": "...", "provinsi": "...", "kode_pos": "..." },
    "syarat_pembayaran": "C.B.D",
    "akun_utang": "2101",
    "jenis_pajak": "CTAS_KEPADA_SELAIN_PEMUNGUT_PPN",
    "nama_wajib_pajak": "",
    "negara": "Indonesia",
    "accurate_id": 0,
    "sync_status": "PENDING",
    "sync_error": "",
    "sync_attempts": 0,
    "last_synced_at": null,
    "next_retry_at": null,
    "metadata": { "created_at": "...", "created_by": "E1" }
  }
}
```

`sync_status`: `PENDING` (menunggu antrian) · `SYNCED` (sudah di Accurate, `accurate_id` terisi) · `FAILED` (`sync_error` memuat pesan asli dari Accurate).

## Master Barang & Jasa (✅ Diimplementasikan)

| Method | Path | Fungsi |
|---|---|---|
| GET | `/barang` | Daftar barang. Query: `cari` (nama/kode, regex case-insensitive), `kategori`, `jenis_barang`, `sync_status`. |
| GET | `/barang/usul-kode?kategori=` | Usulan kode berikut, format `BRG-{angka}` dari kode tertinggi **di seluruh koleksi** (parameter `kategori` diterima tapi diabaikan — beda dari `/pemasok/usul-nomor` yang per-kategori). |
| POST | `/barang` | Buat barang. `201` + data. `400` bila `nama`/`kategori`/`jenis_barang`/`satuan` kosong atau `jenis_barang`/`tipe_nomor_seri` di luar enum, `409` kode sudah dipakai. |
| PUT | `/barang/:id` | Sunting barang. `400` id/body/validasi gagal, `404` tidak ditemukan, `409` kode dipakai barang lain. |
| GET | `/katalog/kategori-barang` | Opsi Kategori Barang dari Accurate (`item-category/list.do`). `502` bila Accurate tidak dapat dihubungi. |
| GET | `/katalog/satuan` | Opsi Satuan dari Accurate (`unit/list.do`). `502` bila Accurate tidak dapat dihubungi. |
| GET | `/katalog/pajak` | Opsi Pajak/PPN dari Accurate (`tax/list.do`). `502` bila Accurate tidak dapat dihubungi. |
| POST | `/barang/import` | Import awal seluruh barang dari Accurate (role `admin`). Idempoten (kunci `accurate_id`). `502` bila Accurate gagal. |

**Request body** `POST /barang` & `PUT /barang/:id`:
```json
{
  "nama":                "string (wajib)",
  "kategori":            "string (wajib) — nama PERSIS seperti katalog kategori-barang Accurate",
  "jenis_barang":        "string (wajib) — INVENTORY / NON_INVENTORY / SERVICE / GROUP / PRODUCTION_COST",
  "kode":                "string — format BRG-{angka}, boleh disunting manual",
  "satuan":              "string (wajib) — nama PERSIS seperti katalog satuan Accurate",
  "upc":                 "string",
  "pakai_ppn":           "bool",
  "ppn":                 "string — nama PERSIS seperti katalog pajak Accurate, relevan hanya bila pakai_ppn true",
  "kelola_nomor_seri":   "bool",
  "tipe_nomor_seri":     "string — UNIQUE / BATCH, relevan hanya bila kelola_nomor_seri true",
  "pakai_kadaluarsa":    "bool — relevan hanya bila kelola_nomor_seri true",
  "pemasok_utama":       "string",
  "satuan_beli":         "string",
  "harga_beli":          "number",
  "minimum_beli":        "number",
  "batas_minimum_stok":  "number",
  "catatan":             "string",
  "berat":               "number"
}
```

**Response** (bentuk `Barang`):
```json
{
  "data": {
    "id": "6a68a8f454ac69964f06f7ea",
    "nama": "Botol Kaca 100ml",
    "kode": "BRG-112",
    "kategori": "Bahan Kemas",
    "jenis_barang": "INVENTORY",
    "satuan": "Pcs",
    "upc": "",
    "ppn": "PPN 11%",
    "pakai_ppn": true,
    "kelola_nomor_seri": false,
    "tipe_nomor_seri": "",
    "pakai_kadaluarsa": false,
    "pemasok_utama": "CV Contoh Jaya",
    "satuan_beli": "Pcs",
    "harga_beli": 2500,
    "minimum_beli": 100,
    "batas_minimum_stok": 500,
    "catatan": "",
    "berat": 15,
    "merek": "",
    "tipe_persediaan": "",
    "accurate_id": 0,
    "sync_status": "PENDING",
    "sync_error": "",
    "sync_attempts": 0,
    "last_synced_at": null,
    "next_retry_at": null,
    "metadata": { "created_at": "...", "created_by": "E1" }
  }
}
```

`merek` dan `tipe_persediaan` **baca-saja** — kosong sampai barang diimpor dari Accurate (`detail.do`); tidak ada di 58 parameter `item/save.do` sehingga mengirim nilai lewat POST/PUT diabaikan diam-diam oleh Accurate.

**Response** `GET /barang/usul-kode`:
```json
{ "data": { "kode": "BRG-112" } }
```

**Response** `GET /katalog/kategori-barang` (bentuk sama untuk `/katalog/satuan` dan `/katalog/pajak`):
```json
{ "data": [ { "nama": "Bahan Kemas", "tampilan": "Bahan Kemas" } ] }
```

> `nama` = nilai yang **dikirim** ke Accurate; `tampilan` = teks yang **dibaca user**. Frontend wajib menampilkan `tampilan` dan mengirim `nama` — sama aturannya dengan katalog syarat pembayaran pemasok.

**Response** `POST /barang/import`:
```json
{ "data": { "terimpor": 0 } }
```
> Bentuk mengikuti pola `POST /import` pemasok; belum pernah dijalankan terhadap data Accurate produksi (lihat catatan di [[Microservices - Procurement Service]]).

**Response** `GET /pemasok/usul-nomor`:
```json
{ "data": { "vendor_no": "PBB-061" } }
```

**Response** `GET /katalog/syarat-pembayaran`:
```json
{ "data": [ { "nama": "DP 50%, Pelunasan Se", "tampilan": "DP 50%, Pelunasan Setelah 30 Hari Barang Diterima" } ] }
```

> `nama` = nilai yang **dikirim** ke Accurate (dipotong 20 karakter oleh Accurate); `tampilan` = teks yang **dibaca user** (dari `memo`, jatuh ke `nama` bila memo kosong). Frontend wajib menampilkan `tampilan` dan mengirim `nama`.

**Response** `GET /katalog/akun-utang`:
```json
{ "data": [ { "nama": "2101", "tampilan": "2101 — Utang Usaha Supplier - IDR" } ] }
```

> Hanya akun bertipe `ACCOUNT_PAYABLE` yang ditawarkan. Akun Uang Muka Pembelian
> (1504/1507) bertipe `ACCOUNT_RECEIVABLE` sehingga bukan kandidat akun utang
> pemasok. `nama` berisi **nomor** akun — itu bentuk yang dipakai seluruh data
> pemasok produksi. Nilainya disimpan di ERP saja; lihat catatan di bawah.

**Response** `POST /import`:
```json
{ "data": { "terimpor": 139 } }
```

## Pembelian — cermin Accurate BACA-SAJA (✅ Diimplementasikan)

Arah data kebalikan dari Pemasok/Barang: dicatat finance **langsung di Accurate**, ditarik ke ERP otomatis (06:00 & 18:00 WIB) atau manual. Seluruh rute daftar membaca Mongo saja — **tidak pernah** memanggil Accurate saat layar dibuka.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/pesanan` | Daftar pesanan pembelian, cermin `purchase-order/list.do`. Query: `vendor_no`, `status` (cocok `status_name`). |
| GET | `/penerimaan` | Daftar penerimaan, cermin `receive-item/list.do` + baris turunan `pesanan_nomor`/`selisih_hari`/`punya_selisih`/`terlambat` (dihitung saat dibaca). Query: `status`. |
| GET | `/permintaan` | Daftar permintaan barang, cermin `purchase-requisition/list.do`. Query: `status`. Hanya `number`/`trans_date`/`status_name` — `requisitionType` tidak ada di list.do Accurate. |
| GET | `/pembelian/status` | Kemajuan impor per modul: `berhasil_pada`, `jumlah_terakhir`, `gagal_pada`, `gagal_pesan`, `detail_terambil`. |
| POST | `/pembelian/impor` | Penyegaran manual ketiga modul. Role `imporMassal` (bukan `akses` biasa). 200 bila ada yang berhasil; 502 hanya bila ketiganya gagal. Timeout 30 menit (impor pertama menarik detail ~belasan menit). |
| POST | `/penerimaan/:id/tandai-tidak-sesuai` | Menandai satu penerimaan sebagai barang tidak sesuai (rusak/kurang/salah kirim). Body `{"keterangan": "..."}`, **wajib diisi** — `400` bila kosong/hanya-spasi, `404` bila id tidak ditemukan. Role `tulisPO` (bukan permission baru). Catatan milik ERP murni — Accurate tidak pernah ditulis. |
| POST | `/penerimaan/:id/batal-tandai-tidak-sesuai` | Membatalkan penandaan. Tanpa body. Keterangan/penanda/waktu dikosongkan. Role `tulisPO`. `404` bila id tidak ditemukan. |

**Response** `GET /pesanan`:
```json
{
  "data": [
    {
      "id": "6a68a8f454ac69964f06f7ea",
      "accurate_id": 123456,
      "number": "PO.2026.07.0099",
      "trans_date": "05/07/2026",
      "ship_date": "12/07/2026",
      "status": "OPEN",
      "status_name": "Terbuka",
      "approval_status": "Approved",
      "percent_shipped": 40,
      "total_amount": 15000000,
      "vendor_no": "PBB-061",
      "vendor_nama": "CV Contoh Jaya",
      "catatan_erp": ""
    }
  ]
}
```
> `vendor_no`/`vendor_nama` diratakan backend dari objek `vendor` **bersarang** Accurate — `vendorId`/`vendorName` tidak ada langsung di `purchase-order/list.do`.

**Response** `GET /penerimaan`:
```json
{
  "data": [
    {
      "penerimaan": {
        "id": "6a68a8f454ac69964f06f7ea",
        "accurate_id": 654321,
        "number": "RI.2026.07.0050",
        "trans_date": "10/07/2026",
        "ship_date": "",
        "status_name": "Difaktur",
        "pesanan_accurate_id": 123456,
        "pesanan_nomor": "PO.2026.07.0099",
        "detail_terambil": true,
        "catatan_erp": "",
        "tidak_sesuai": false,
        "keterangan_tidak_sesuai": "",
        "tidak_sesuai_oleh": "",
        "tidak_sesuai_pada": null
      },
      "pesanan_nomor": "PO.2026.07.0099",
      "selisih_hari": 3,
      "punya_selisih": true,
      "terlambat": true,
      "detail_terambil": true
    }
  ],
  "detail_dari": "10/02/2026",
  "detail_sampai": "31/07/2026"
}
```
> `detail_dari`/`detail_sampai` (format `dd/MM/yyyy`) adalah jendela 6 bulan **yang benar-benar dipakai** backend saat itu — wajib ditampilkan FE agar cakupan periode tidak dibaca sebagai sepanjang masa. `punya_selisih=false` **tidak pernah** disertai angka hari yang berarti (`selisih_hari` tetap 0 tapi tidak dipakai) — `terlambat` juga selalu `false` dalam keadaan ini.
>
> Empat field `tidak_sesuai*` adalah catatan **milik ERP** (lihat bagian Penandaan di bawah) — muncul di **setiap** baris `penerimaan` karena dokumennya dibaca penuh (bukan lewat proyeksi terpisah), bukan hanya pada baris yang tertandai.

**Query** `GET /penerimaan?hanya_tidak_sesuai=true`: menyaring HANYA baris yang sudah ditandai — menggerakkan daftar kerja "Barang Tidak Sesuai" lewat rute yang sama. Nilai apa pun selain `"true"` (termasuk tidak dikirim) berarti false: seluruh baris ditampilkan.

**Request/Response** `POST /penerimaan/:id/tandai-tidak-sesuai`:
```json
// Request
{ "keterangan": "dus penyok, 3 unit pecah" }

// Response 200
{
  "data": {
    "id": "6a68a8f454ac69964f06f7ea",
    "accurate_id": 654321,
    "number": "RI.2026.07.0050",
    "tidak_sesuai": true,
    "keterangan_tidak_sesuai": "dus penyok, 3 unit pecah",
    "tidak_sesuai_oleh": "E1",
    "tidak_sesuai_pada": "2026-07-31T09:00:00+07:00"
  }
}
```
> `400` bila `keterangan` kosong/hanya-spasi: `{"error": "keterangan wajib diisi — jelaskan apa yang tidak sesuai (rusak/kurang/salah kirim)"}`. `tidak_sesuai_oleh` diambil dari header `BIP-Employee-ID`, bukan dari body.

**Response** `POST /penerimaan/:id/batal-tandai-tidak-sesuai`:
```json
{
  "data": {
    "id": "6a68a8f454ac69964f06f7ea",
    "tidak_sesuai": false,
    "keterangan_tidak_sesuai": "",
    "tidak_sesuai_oleh": "",
    "tidak_sesuai_pada": null
  }
}
```

**Response** `GET /pembelian/status`:
```json
{
  "data": [
    {
      "modul": "pesanan",
      "berhasil_pada": "2026-07-31T06:00:12+07:00",
      "jumlah_terakhir": 1036,
      "gagal_pada": null,
      "gagal_pesan": "",
      "detail_terambil": 0
    }
  ]
}
```
> `berhasil_pada: null` = modul ini **belum pernah** berhasil disegarkan. `gagal_pada` terisi hanya bila percobaan **terakhir** gagal — ditampilkan berdampingan dengan `berhasil_pada` supaya data lama yang masih tampil tidak dikira data terkini.

## Belum Diimplementasikan / Catatan

- Tidak ada endpoint **hapus pemasok** maupun **hapus barang** — penghapusan master dilakukan finance/procurement di Accurate.
- Tidak ada endpoint **pemicu sync manual**; worker berjalan otomatis tiap 30 detik atas baris `PENDING`/`FAILED` (pemasok maupun barang).
- **Toggle boolean pada `PUT /barang/:id`** (`pakai_ppn`, `kelola_nomor_seri`, `pakai_kadaluarsa`) hanya bisa **diaktifkan**, tidak bisa dinonaktifkan oleh payload yang tidak mengirim field itu — batasan `bool` biasa (tidak bisa membedakan "false" dari "tidak dikirim"). Tidak terasa di FE ERP karena form selalu mengirim seluruh field toggle.
- Dua field **dapat dibaca tetapi tidak dapat ditulis** lewat API: Tipe Pemasok
  (`vendorType`) dan Jenis Dokumen (`documentCode`). ERP menampilkannya hasil import;
  pengisiannya dilakukan finance di Accurate — lihat [[Microservices - Procurement Service]].
  Akun Utang & Akun Uang Muka **dikirim** ke Accurate (koreksi 2026-07-28).
- WhatsApp (`no_wa`) hanya tersimpan di ERP — `vendor/save.do` tidak menyediakan
  field WhatsApp untuk pemasok.
- Pengosongan nilai belum tersinkron (`omitempty`) — TBD, lihat dok implementasi.
- **Pembelian tidak punya endpoint tulis ke Accurate** — tak ada `POST`/`PUT`/`DELETE` yang mengirim pesanan/penerimaan/permintaan ke Accurate; seluruhnya dicatat finance di Accurate, ERP hanya mencerminkan. Pengecualian: `POST /penerimaan/:id/tandai-tidak-sesuai` dan `.../batal-tandai-tidak-sesuai` **menulis ke Mongo ERP saja** (catatan gudang internal) — Accurate tetap tidak pernah disentuh, penerimaan tetap cermin murni.
- **Permintaan barang hanya tiga field tampil** (`number`/`trans_date`/`status_name`) — `requisitionType` tidak dikembalikan `purchase-requisition/list.do`, bukan bug pengambilan data.
- **`purchaseOrderId` di penerimaan hanya terisi dalam jendela 6 bulan** — di luar jendela itu, `pesanan_nomor` kosong bukan karena pembelian langsung, melainkan detailnya belum pernah ditarik (`detail_terambil=false`).

## Dependensi & Integrasi

- Accurate Online (`vendor/save.do`, `vendor/list.do`, `vendor/detail.do`, `payment-term/list.do`) — [[ADR - 0001 Akuntansi via Accurate]].
- [[CORE - API Master Gateway]] (`PROCUREMENT_MODULE_URL`).

## Dokumen Terkait

- [[Microservices - Procurement Service]]
- [[API - Index]]
