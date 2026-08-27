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

## Permintaan Barang ERP — create + persetujuan (✅ Diimplementasikan 2026-08-06)

Entitas **milik ERP** (bukan cermin Accurate), koleksi `permintaan_erp`. Arah data sama dengan Pemasok/Barang: dibuat di ERP. Prefix rute `/permintaan-erp` menandai bedanya dari cermin `GET /permintaan`.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/permintaan-erp` | Daftar berpaginasi. Query: `status`, `tipe`, `sudah_dicetak` (`true`/`false`/kosong=semua), `cari` (number+keterangan), `dari`/`sampai` (rentang `trans_date_ts`), `page`, `limit`. Role `akses`. |
| POST | `/permintaan-erp` | Buat permintaan. Body: `tipe_permintaan`, `keterangan?`, `number?` (kosong=auto), `trans_date?` (dd/MM/yyyy), `rincian[]` (`nama_barang`, `kuantitas`, `satuan` wajib; `kode_barang`/`tgl_diminta`/`departemen`/`proyek`/`keterangan`/`harga_estimasi` opsional). Server menetapkan status/persetujuan awal, peminta (dari header identitas + `BIP-Department`), total, nomor. Role `tulisPO`. `409` bila nomor bentrok. |
| GET | `/permintaan-erp/:id` | Detail satu permintaan. Role `akses`. |
| GET | `/permintaan-erp/usul-nomor` | Usulan nomor berikut `PR.<YYYY>.<MM>.<NNNNN>` (reset per bulan). Role `akses`. |
| GET | `/permintaan-erp/opsi-barang` | Daftar barang untuk pemilih form: `kode`, `nama`, `satuan`, `harga_beli` (tak dipaginasi). Role `akses`. |
| GET | `/permintaan-erp/persetujuan?tampilan=` | Antrean yang jadi tanggung jawab atasan pemanggil, disaring server ke `peminta_departemen ∈ BIP-Supervised-Departments`. **Tanpa gerbang izin procurement** (atasan bisa lain modul); auth diperiksa di handler. Cakupan kosong → daftar kosong (bukan 403). **`tampilan=riwayat`** (2026-08-10) membalik sumbu status ke yang SUDAH diputus (`$ne menunggu`); nilai lain — termasuk kosong & salah ketik — jatuh ke **menunggu**, jadi pemanggil lama tak berubah perilakunya. Penyaring cakupan supervisi TIDAK ikut longgar. |
| POST | `/permintaan-erp/:id/setujui` | Menyetujui. Wewenang: `peminta_departemen` harus dalam cakupan supervisi pemanggil. `403` bila bukan atasan departemen itu; `409` bila sudah diputuskan. Tanpa gerbang izin procurement. |
| POST | `/permintaan-erp/:id/tolak` | Menolak. Body `{"alasan": "..."}` **wajib** (`400` bila kosong). Wewenang & aturan status sama dengan setujui. |

> **Routing persetujuan = atasan langsung departemen peminta.** `BolehSetujuiPermintaan(peminta_departemen, supervised)` mencocokkan (case-insensitive) departemen peminta terhadap `BIP-Supervised-Departments` (diisi gateway dari klaim JWT) — tidak memanggil employee-service. Departemen peminta kosong → tak seorang pun berhak.

## Pesanan Pembelian ERP — create + Ambil Permintaan + persetujuan (✅ Diimplementasikan 2026-08-06)

Entitas **milik ERP** (koleksi `pesanan_erp`), TERPISAH dari cermin `pesanan_pembelian` dan dari `purchase_order` (push Accurate). Prefix `/pesanan-erp`.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/pesanan-erp` | Daftar berpaginasi. Query: `status`, `vendor_no`, `cari` (number+keterangan), `dari`/`sampai`, `page`, `limit`. Role `akses`. |
| POST | `/pesanan-erp` | Buat PO. Body: `vendor_no` (wajib), `rincian[]` (`nama_barang`/`kuantitas`/`satuan` wajib; `harga` boleh 0; `diskon_persen`/`pajak`/`gudang`/`departemen`/`proyek`/`keterangan`/`no_permintaan` opsional), Info lainnya header, `diskon_header_persen`, `number?`. Server hitung total & status awal **`diajukan`**. Role `tulisPO`. `409` nomor bentrok. |
| GET | `/pesanan-erp/:id` | Detail. Role `akses`. |
| GET | `/pesanan-erp/usul-nomor` | Usulan `PO.<YYYY>.<MM>.<NNNNN>` (reset per bulan). Role `akses`. |
| GET | `/pesanan-erp/permintaan-disetujui` | Permintaan yang SUDAH disetujui (untuk "Ambil → Permintaan"). Role `akses`. |
| GET | `/pesanan-erp/persetujuan?tampilan=` | Antrean PO, HANYA untuk pemegang jabatan setingkat Direktur (`BolehSetujuiPesanan` → `common.SetaraDirektur`). Jabatan lain → daftar kosong. Tanpa gerbang izin procurement. **`tampilan=riwayat`** (2026-08-10) sama seperti Permintaan Barang; gerbang jabatan tetap diperiksa LEBIH DULU, jadi yang bukan penyetuju menerima daftar kosong di kedua sumbu. Diverifikasi: Finance Supervisor → 0 pada `menunggu` maupun `riwayat`. |
| POST | `/pesanan-erp/:id/setujui` | Setujui → status `diajukan`→`menunggu_diproses`. `403` bila bukan jabatan approver; `409` bila sudah diputuskan. |
| POST | `/pesanan-erp/:id/tolak` | Tolak. Body `{"alasan": "..."}` wajib. Wewenang & aturan status sama. |

> **Approval PO = jabatan**, bukan izin modul (beda dari Permintaan yang per-departemen supervisi). `PosisiApproverPO` = "Direktur" ("Pak Widi"), dicocokkan case-insensitive dengan `BIP-Position`. Ubah bersama padanan FE `POSISI_APPROVER_PO`.

## Penerimaan Barang ERP — create + Ambil Pesanan (✅ Diimplementasikan 2026-08-06)

Entitas **milik ERP** (koleksi `penerimaan_erp`), melengkapi rantai PR→PO→RI. TERPISAH dari cermin `penerimaan`. Prefix `/penerimaan-erp`. **Tanpa persetujuan.**

| Method | Path | Fungsi |
|---|---|---|
| GET | `/penerimaan-erp` | Daftar berpaginasi. Query: `status`, `vendor_no`, `cari` (number+no_terima+keterangan), `dari`/`sampai`, `page`, `limit`. Role `akses`. |
| POST | `/penerimaan-erp` | Buat penerimaan. Body: `vendor_no` (wajib), `no_terima` (wajib), `trans_date` (kedatangan), `rincian[]` (`nama_barang`/`kuantitas`/`satuan`/`gudang` wajib; `departemen`/`proyek`/`keterangan`/`no_permintaan`/`no_pesanan` opsional), Info lainnya header, `number?`. Server set status `diterima`. Role `tulisPO`. `409` No Form bentrok. |
| GET | `/penerimaan-erp/:id` | Detail. Role `akses`. |
| GET | `/penerimaan-erp/usul-nomor` | Usulan No Form `RI.<YYYY>.<MM>.<NNNNN>` (reset per bulan). Role `akses`. |
| GET | `/penerimaan-erp/pesanan-disetujui` | Pesanan pembelian yang SUDAH disetujui (untuk "Ambil → Pesanan"). Role `akses`. |

> **No Terima ≠ No Form.** No Form (`number`) di-generate sistem & unik; No Terima (`no_terima`) nomor surat jalan pemasok yang **diketik manual** gudang/QC, wajib tapi tak dijamin unik. Gudang **wajib** per baris.

## Pengajuan Pembelian — rantai delapan tahap (✅ Diimplementasikan)

Modul [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]], koleksi `pengajuan_pembelian`. Prefix `/pengajuan-pembelian`, **bukan** `/pembelian`: prefiks yang terakhir sudah dipakai cermin Accurate di atas, dan rute `:nomor` di sini akan menelannya.

⛔ **Rute literal didaftarkan sebelum saudara ber-`:nomor`.** Fiber mencocokkan sesuai urutan pendaftaran, dan rute yang tertelan membalas 200 berisi bentuk yang masuk akal, bukan 404.

Gerbangnya berlapis: gerbang rute menyaring "punya urusan dengan modul ini", sedangkan yang memutuskan apakah izin pemanggil COCOK dengan TAHAP yang sedang berjalan adalah handler — gerbang rute tak dapat melihat dokumennya.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/pengajuan-pembelian` | Daftar dalam cakupan pemanggil. Query: `tipe`, `status`, `batas` (bawaan 100, maksimum 500). |
| GET | `/pengajuan-pembelian/saya` | Pengajuan milik pemanggil. Rute terpisah, bukan penyaring atas daftar umum: staf pengaju tak punya cakupan apa pun sehingga daftar umum kosong baginya. |
| GET | `/pengajuan-pembelian/perlu-aksi` | Antrean yang menunggu tindakan pemanggil. Tahap mana saja yang masuk ditentukan izin **dan** penunjukan per tahap ([[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]]); frontend tidak merakit daftarnya sendiri. |
| GET | `/pengajuan-pembelian/penyetuju` | Penunjukan seluruh tahap yang dapat ditetapkan, termasuk yang masih kosong (agar layar dapat membedakan "belum ditetapkan" dari "tahap tak ada"). Izin `budget.master.save`. |
| GET | `/pengajuan-pembelian/penyetuju/kandidat?tahap=` | Pemegang izin tahap itu, diproksi ke `GET /internal/permission-holders` milik employee-service. **Layar tak pernah menyebut nama izin**: peta tahap→izin tinggal di service ini. `400` tahap tak dikenal, `502` employee-service tak terjangkau. Izin `budget.master.save`. |
| PUT | `/pengajuan-pembelian/penyetuju/:tahap` | Menetapkan penyetuju satu tahap. Body `{"employee_ids": [...]}`; daftar kosong = kembalikan ke seluruh pemegang izin. `400` bila tahap tak dikenal, bila tahap `spv_divisi` (penyetujunya mengikuti departemen pengaju, diatur di HRIS), atau bila ada id yang **tidak memegang izin tahap itu**. `502` bila izin tak dapat diperiksa (gagal-tertutup). Izin `budget.master.save`. |
| POST | `/pengajuan-pembelian` | Buat pengajuan. Selalu lahir **DRAFT**; `jenjang_wajib` belum dibekukan. `nominal` dihitung server dari Σ subtotal item dan **ditolak 400 bila dikirim klien**. Digerbang per TIPE (`budget.pengajuan.{umum,rawmaterial,software,iklan}`) di dalam handler, sebab tipe dibaca dari body. |
| GET | `/pengajuan-pembelian/:nomor` | Detail. Pengaju selalu boleh melihat miliknya; selebihnya mengikuti cakupan departemen. |
| PATCH | `/pengajuan-pembelian/:nomor` | Sunting DRAFT/REVISI oleh pengajunya. Menerima `keperluan`, `kategori_kode`, `tautan`, `items`. **TIPE tidak dapat diubah**, bahkan saat draft. Nilai kosong berarti "jangan sentuh", sehingga `tautan` yang sudah terisi tidak dapat dikosongkan lewat rute ini. |
| POST | `/pengajuan-pembelian/:nomor/ajukan` | Membekukan `jenjang_wajib` dan ambang Direktur, lalu menjalankan dokumen. REVISI ikut boleh diajukan, dan jenjangnya **dihitung ulang**. |
| POST | `/pengajuan-pembelian/:nomor/batal` | Pembatalan oleh pengaju. Ditolak `409` bila `nomor_po` sudah terisi. |
| POST | `/pengajuan-pembelian/:nomor/setujui` · `/tolak` · `/revisi` | Gerbang persetujuan. Alasan **wajib** pada tolak dan revisi. `DITOLAK` hanya untuk penolakan saat belum ada uang keluar. |
| POST | `/pengajuan-pembelian/:nomor/beli` | Tahap Procurement (`budget.approve.procurement`). Mencatat `nomor_po`; putaran kedua tidak menerbitkan PO baru. |
| POST | `/pengajuan-pembelian/:nomor/bayar` | Tahap AP (`budget.ap.bayar`). Mencatat `id_pembayaran`. |
| POST | `/pengajuan-pembelian/:nomor/qc` | Pemeriksaan mutu raw material (`budget.qc.periksa`). TIDAK LOLOS mengembalikan dokumen ke Procurement dengan status tetap `BERJALAN`, bukan `DITOLAK`. |
| POST | `/pengajuan-pembelian/:nomor/terima` | Penerimaan gudang (`budget.terima.ga` / `budget.terima.rm`). Bertahap; `stok_ditulis: false` datang lewat jalur SUKSES dan wajib diperiksa pemanggil. |
| POST | `/pengajuan-pembelian/:nomor/stok/coba-lagi` | Mengulang HANYA penulisan stok yang gagal. Body kosong: angkanya diambil server dari catatan penerimaan terakhir. |
| PATCH | `/pengajuan-pembelian/:nomor/alokasi` | Alokasi akuntansi oleh Finance (`budget.approve.finance`). **Belum punya konsumen frontend.** |

> **Jejak langkah membawa pelakunya.** Tiap baris `riwayat` menyimpan `oleh` (employee_id) plus `nama` dan `posisi` yang **dibekukan saat tindakan terjadi**, diambil dari header `BIP-Fullname`/`BIP-Position` sehingga tak menuntut satu pun panggilan lintas service. Sengaja tidak diterjemahkan dari `oleh` saat dibaca: jabatan berubah, dan jejak yang menerjemahkannya belakangan akan menyatakan bahwa yang menyetujui setahun lalu adalah jabatannya yang sekarang. Keduanya `omitempty` — baris yang dibuat sebelum field ini ada tidak memilikinya, dan pembacanya **wajib jatuh ke `oleh`**, bukan menampilkan kosong.

> **Pengabaran.** Tiap perpindahan tahap mengirim inbox `pembelian-perlu-aksi` ke penindak berikutnya, dan `pembelian-diperbarui` ke pengaju saat ditolak, diminta revisi, atau selesai. Best-effort: kegagalannya di-log dan tidak membatalkan transisi. Tahap yang **belum ditetapkan penyetujunya** sengaja tidak dikabari (dicatat di log), sebab menebak nama departemen tiap tahap di kode menghasilkan filter yang tak cocok dengan siapa pun: nol notifikasi tanpa satu pun tanda.

## Belum Diimplementasikan / Catatan

- **Rute kas kecil, pengajuan budget lama, dan katalog Accurate belum didaftar di dokumen ini** (TBD). Yang sudah didaftar hanya master pemasok/barang, cermin Pembelian, rantai PR→PO→RI, dan Pengajuan Pembelian.
- **Lampiran pengajuan pembelian tidak punya endpoint unggah.** Field `lampiran` ada di model dan sengaja dinolkan saat pembuatan, tetapi tak ada rute yang mengisinya.
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
- **Cermin `GET /permintaan` hanya tiga field** (`number`/`trans_date`/`status_name`) — `requisitionType` tidak dikembalikan `purchase-requisition/list.do`, bukan bug pengambilan data. Berlaku HANYA untuk endpoint cermin; layar Permintaan Barang kini memakai entitas ERP-native `/permintaan-erp` (data lengkap, lihat bagian di atas).
- **`purchaseOrderId` di penerimaan hanya terisi dalam jendela 6 bulan** — di luar jendela itu, `pesanan_nomor` kosong bukan karena pembelian langsung, melainkan detailnya belum pernah ditarik (`detail_terambil=false`).

## Dependensi & Integrasi

- Accurate Online (`vendor/save.do`, `vendor/list.do`, `vendor/detail.do`, `payment-term/list.do`) — [[ADR - 0001 Akuntansi via Accurate]].
- [[CORE - API Master Gateway]] (`PROCUREMENT_MODULE_URL`).

## Dokumen Terkait

- [[Microservices - Procurement Service]]
- [[API - Index]]
