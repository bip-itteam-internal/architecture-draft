## Deskripsi

*Endpoint **procurement-service** (master Pemasok + master Barang & Jasa: CRUD, penomoran, katalog, import awal, worker sync ke Accurate; cermin baca-saja Pembelian: Pesanan/Penerimaan/Permintaan Barang; Tagihan Pemasok + Pembayaran Vendor + Aging Utang; Pengajuan Barang lima tipe dengan alur berjenjang; dan modul Kas Kecil + Pengajuan Budget yang menumpang service ini). Gateway: `/api/procurement/*`. Grounded ke `services/procurement/` (snapshot origin/main 2026-09-12 pagi).*

- **Implementasi**: [[Microservices - Procurement Service]] · **Status**: ⚠️ Implemented (ada catatan). Baris status sebelumnya di dok ini menyatakan service **belum di-deploy** dan import awal **belum dijalankan**, itu **usang**: [[Microservices - Procurement Service]] mencatat koreksi 2026-08-04, sudah deploy dan terisi di produksi (sensus `procurement_db` 4 Agustus 2026). Detail sensus per koleksi tidak diulang di sini, lihat dok itu. Modul Pembelian (PR #810) ✅ terverifikasi terhadap Accurate produksi read-only.
- **Indeks**: [[API - Index]] · Auth: gateway key `BIP-Gateway-ID` untuk semua route, plus **permission-set** (ADR 0030) lewat header `BIP-System-Roles`/klaim JWT, **bukan lagi** guard tier `system_roles["procurement"]` yang tercatat di versi lama dok ini. Akun yang belum ditugaskan paket izin tetap dilayani **fallback tier** (`common.ProcurementTierDefault`) supaya akses lama tidak putus (`main.go:575-588`, diverifikasi). Modul Kas Kecil murni (bukan Pengajuan Budget) **tidak punya fallback tier**, lihat [[Finance - Kas Kecil dan Pengajuan Budget]] §Izin.

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

## Pengajuan Barang (lima tipe, menggantikan Pengajuan Pembelian) (✅ Diimplementasikan)

**Modul lama dihapus dari kode, diverifikasi 2026-09-12.** Prefix `/pengajuan-pembelian` beserta seluruh sub-rute yang sebelumnya didokumentasikan di bagian ini (`/saya`, `/perlu-aksi`, `/penyetuju*`, `/beli`, `/bayar`, `/terima`, `/stok/coba-lagi`, `PATCH /alokasi`, izin `budget.pengajuan.software`) **tidak ada lagi** di `services/procurement/`. Komentar `main.go:1105-1115` menyebutnya diganti "pengajuan barang lima tipe", sekaligus melebur alur permintaan barang gudang GA yang sebelumnya berada di inventory-service. Koleksi `PenunjukanPembelian` (penunjukan penyetuju per tahap ala [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]]) tidak lagi punya satu pun rute HTTP; index Mongo-nya masih dipasang (`main.go:291-309`). `GET /internal/permission-holders` milik employee-service TETAP dipanggil service ini, kini untuk mencari penerima notifikasi tahap (`pengajuan_barang_notify_kirim.go:373`), bukan lagi lewat rute proksi kandidat penyetuju.

Koleksi baru `pengajuan_barang`, prefix rute `/pengajuan-barang` (`pengajuan_barang_handler.go:34-77`). Lima tipe (`pengajuan_barang_jenjang.go:11-22`): `UMUM`, `RAWMATERIAL`, `IKLAN`, `DANA`, `KONSUMSI`. KONSUMSI sengaja berbagi izin dengan DANA (keputusan bisnis eksplisit, bukan default tersembunyi). Status dokumen: `DRAFT`, `BERJALAN`, `SELESAI`, `DITOLAK`, `REVISI`, `DIBATALKAN`.

⛔ **Gerbang per tahap berada DI DALAM handler (`BolehMenindakTahap`, `pengajuan_barang_gate.go:210-241`), bukan middleware rute.** `DaftarkanRutePengajuanBarang(internal)` dipasang tanpa satu izin pun di gerbang rute karena wewenangnya berbeda tiap tahap, dan sebagian ditentukan hubungan organisasi, bukan izin (lihat kolom Wewenang di tabel bawah).

| Method | Path | Fungsi | Wewenang |
|---|---|---|---|
| POST | `/pengajuan-barang/lampiran` | Unggah bukti SEBELUM dokumen dibuat, dipakai tipe DANA yang mensyaratkan bukti sudah ditalangi. Rute literal, wajib terdaftar sebelum `/:id`. | Terautentikasi (identitas dari header) |
| POST | `/pengajuan-barang` | Buat pengajuan, lahir `DRAFT`. Body: `tipe`, `departemen?` (jatuh ke header bila kosong), `items[]`, `lampiran[]`, `tautan?`, `sudah_ditalangi`, `sumber_dana?`, `proyek_pembebanan?`. | Izin sesuai tipe (`IzinAjukanUntukTipe`): `budget.pengajuan.umum` / `.rawmaterial` / `.iklan` / `.dana` (DANA dan KONSUMSI sama-sama `.dana`) |
| GET | `/pengajuan-barang` | Daftar dalam cakupan pemanggil. Query: `tipe`, `status`, `pengaju_id`, `perlu_perhatian` (dibandingkan string `"true"` persis). | Terautentikasi |
| GET | `/pengajuan-barang/milik-saya` | Pengajuan milik pemanggil sendiri. | Terautentikasi |
| GET | `/pengajuan-barang/antrean` | "Perlu aksi saya", tahap yang boleh ditindak pemanggil, disaring `TahapYangBolehDitindak` (memanggil `BolehMenindakTahap` yang sama, dikunci test `TestTahapYangBolehDitindak_SepakatDenganGerbang`). | Terautentikasi |
| GET | `/pengajuan-barang/pembukuan` | Daftar keadaan pembukuan (jurnal ke Accurate) atas pengajuan uang, bawaan hanya yang GAGAL; `semua=true` untuk rekonsiliasi. | `budget.jurnal.view`, BUKAN `budget.view` yang dipegang setiap pemohon |
| GET | `/pengajuan-barang/:id` | Detail. | Terautentikasi |
| POST | `/pengajuan-barang/:id/setujui` | Menyetujui tahap berjalan. Tahap `pb_ap_transfer` menerima isian transfer (sumber dana + akun beban, divalidasi ke katalog Accurate bila terjangkau); ekor stok/bayar/jurnal dijalankan sesudah tahap maju. | `BolehMenindakTahap` per tahap, lihat peta di bawah |
| POST | `/pengajuan-barang/:id/tolak` | Menolak, `alasan` wajib. | `BolehMenindakTahap` |
| POST | `/pengajuan-barang/:id/revisi` | Mengembalikan untuk revisi, `alasan` wajib. | `BolehMenindakTahap` |
| POST | `/pengajuan-barang/:id/ajukan-ulang` | Pengaju mengajukan ulang dokumen berstatus REVISI, boleh sekalian menyunting isi (`SuntinganPengajuan`) sebelum diajukan. | Hanya `Pengaju.ID`, bukan `BolehMenindakTahap` (dokumen REVISI tidak punya tahap berjalan) |
| POST | `/pengajuan-barang/:id/cek-stok` | Menjawab cukup/tidaknya stok gudang; jawaban ini membekukan sisa jenjang. | `BolehMenindakTahap` (tahap `pb_cek_stok_ga`) |
| POST | `/pengajuan-barang/:id/qc` | Mencatat hasil QC per baris barang (qty lulus/reject/karantina, batch, expired). Menggantikan makna lama `qc-gagal`; dokumen maju hanya bila karantina nol. | `BolehMenindakTahap` (tahap `pb_qc` / `pb_qc_ga`) |
| POST | `/pengajuan-barang/:id/qc-gagal` | Rute LAMA, sengaja dipertahankan untuk kasus seluruh kiriman ditolak (tak ada angka per-baris yang perlu dicatat). Mengembalikan dokumen ke tahap procurement, bukan menolak. | `BolehMenindakTahap` |
| POST | `/pengajuan-barang/:id/kembali-qc` | Memulangkan dokumen dari tahap penerimaan ke QC untuk cacat yang baru ketahuan saat barang dibuka. | `BolehMenindakTahap` |
| POST | `/pengajuan-barang/:id/harga` | Procurement mengisi harga per baris, menaut ke master barang, memilih gudang tujuan; sisa jenjang dibekukan di sini. Tipe RAWMATERIAL divalidasi ke katalog bahan baku bila terjangkau. | `BolehMenindakTahap` (tahap `pb_procurement_beli`) |
| POST | `/pengajuan-barang/:id/klaim-selesai` | Menutup klaim ke pemasok (barang diganti atau uang kembali). Dokumen sering sudah SELESAI (tahap kosong) sehingga tidak bisa digerbang `BolehMenindakTahap`. | Izin langsung `budget.approve.procurement` |
| POST | `/pengajuan-barang/:id/ulangi-stok` | Mengulang HANYA penulisan stok yang gagal, kunci idempoten sama. Dokumen sering sudah maju/SELESAI sehingga tidak bisa digerbang tahap. | Izin langsung `budget.terima.ga` atau `budget.terima.rm` |
| POST | `/pengajuan-barang/:id/terbitkan-faktur` | AP menerbitkan faktur pembelian dari hasil QC, memicu antrean sync ke Accurate (tidak menulis langsung). Idempoten lewat `bill_number` deterministik (`PB-<nomor pengajuan>`); qty yang berubah antar-sesi QC bertahap ditangani `PutuskanFakturAda`, bukan sekadar dibalas dari cache. | `BolehMenerbitkanFaktur`: izin `budget.ap.bayar` DAN status dokumen `BERJALAN` atau `SELESAI`, bukan gerbang tahap (`pengajuan_barang_gate.go:349-387`) |
| POST | `/pengajuan-barang/:id/lampiran` | Unggah lampiran ke dokumen yang sudah ada. Hanya foto (jpg/jpeg/png/webp) dan PDF, maksimum 5 berkas per dokumen, 4 MB per berkas (beda dari lampiran Pengajuan Budget yang juga menerima office). | Terautentikasi, gerbang tahap tidak berlaku untuk lampiran |
| DELETE | `/pengajuan-barang/:id/lampiran` | Hapus lampiran. | Terautentikasi |
| GET | `/pengajuan-barang/:id/lampiran/pratinjau` | Pratinjau berkas lampiran. | Terautentikasi |
| GET | `/pengajuan-barang/:nomor/pembayaran` | Menemukan dokumen pembayaran dari nomor pengajuan (AP bekerja dari nomor pengajuan, unggah bukti transfer beralamat id pembayaran, lihat bagian Bukti Transfer di bawah). | `budget.view` (`main.go:1143-1144`) |

> **Lampiran punya endpoint unggah, bertentangan dengan catatan lama di dok ini.** Versi sebelumnya bagian "Belum Diimplementasikan" menyatakan lampiran pengajuan pembelian tidak punya endpoint unggah, itu berlaku untuk modul lama yang sudah dihapus. Modul Pengajuan Barang punya jalur unggah sebelum dan sesudah dokumen dibuat (`pengajuan_barang_lampiran.go`).

**Peta tahap ke izin** (`izinPerTahap`, `pengajuan_barang_gate.go:41-55`, sumber tunggal, jangan disalin ke dok lain):

| Tahap | Izin / dasar wewenang |
|---|---|
| `pb_spv_divisi` | Hubungan organisasi: atasan menaungi `Pengaju.Departemen` (bukan izin) |
| `pb_spv_manufactur` | Hubungan organisasi: atasan menaungi departemen Manufaktur (nama diambil dari `common.DepartmentNameFromKey`, bukan literal) |
| `pb_cek_stok_ga` | `budget.cek.stok` |
| `pb_serah_ga` | `budget.terima.ga` |
| `pb_spv_finance` | `budget.approve.finance` |
| `pb_direktur` | `budget.approve.direksi` |
| `pb_procurement_beli` | `budget.approve.procurement` |
| `pb_finance_setujui_bayar` | `budget.approve.pembayaran` |
| `pb_ap_transfer` | `budget.ap.bayar` |
| `pb_qc` | `budget.qc.periksa` |
| `pb_qc_ga` | `budget.terima.ga` (gudang GA yang memegang barangnya, bukan QC produksi) |
| `pb_terima_ga` | `budget.terima.ga` |
| `pb_terima_rm` | `budget.terima.rm` |

> Pengaju TIDAK boleh menindak tahap keputusan atas dokumennya sendiri. `tahapKeputusanPengaju` lebih luas dari tahap persetujuan saja, ikut mencakup `pb_cek_stok_ga` dan `pb_procurement_beli` karena keduanya menentukan uang meski bukan tahap "approval" secara nama.

> **Jejak langkah membawa pelakunya.** Tiap baris `riwayat` menyimpan `oleh` (employee_id) plus `nama` dan `posisi` yang **dibekukan saat tindakan terjadi**, diambil dari header `BIP-Fullname`/`BIP-Position`. Pola ini diwarisi dari modul lama.

> **Pengabaran.** Tiap perpindahan tahap mengirim inbox berkategori `pengajuan-barang-*` (konstanta di `pengajuan_barang_notify.go:15` dan seterusnya, mis. `pengajuan-barang-perlu-persetujuan`, `pengajuan-barang-perlu-cek-stok`); penerimanya dicari lewat `GET /internal/permission-holders` milik employee-service (`pengajuan_barang_notify_kirim.go:373`). Kategori `pembelian-perlu-aksi`/`pembelian-diperbarui` yang tercatat di versi lama dok ini milik modul yang sudah dihapus. Bukti transfer punya dua kategori sendiri, `pengajuan-barang-bukti-perlu-review` dan `pengajuan-barang-bukti-disetujui` (`bukti_transfer_handler.go:47-48`); penolakan bukti sengaja dikirim ke AP dengan kategori perlu-review (`:476-480`).

## Tagihan Pemasok, Pembayaran & Aging Utang (✅ Diimplementasikan)

Koleksi `faktur_pembelian` (Accounts Payable). Berbeda dari Pembelian cermin Accurate di atas: tagihan **dibuat di ERP** lalu disinkronkan ke Accurate lewat antrean worker yang sama dengan master Pemasok/Barang, bukan sekadar ditarik baca-saja.

| Method | Path | Fungsi | Izin |
|---|---|---|---|
| GET | `/tagihan` | Daftar tagihan pemasok. | `procurement.view` |
| POST | `/tagihan` | Buat tagihan. | `procurement.tagihan.save` |
| POST | `/tagihan/import` | Import tagihan dari Accurate (finance sudah mencatat langsung di sana sebelum modul ini ada). Rute LITERAL, wajib sebelum `/tagihan/:id/...` (dikunci `TestRuteImportFakturTidakTertangkapSebagaiID`). | `procurement.import` |
| GET | `/tagihan/aging` | Sebaran nominal utang menurut jatuh tempo (dashboard AP), diagregasi backend agar zona waktu peramban tidak menggeser embernya. Rute literal, wajib sebelum `/tagihan/:id` (`TestRuteAgingTidakTertangkapSebagaiID`). | `procurement.view` |
| GET | `/tagihan/per-pemasok` | Sisa utang dikelompokkan per pemasok (panel bar dashboard AP). Rute literal, wajib sebelum `/tagihan/:id` (`TestRutePerPemasokTidakTertangkapSebagaiID`). | `procurement.view` |
| GET | `/tagihan/:id` | Detail tagihan, termasuk `total_down_payment` (uang muka yang sudah dialokasikan ke tagihan ini) dan `prime_owing` (sisa utang). | `procurement.view` |
| GET | `/tagihan/:id/pembayaran` | Riwayat pembayaran atas satu tagihan. | `procurement.view` |
| POST | `/tagihan/:id/kirim` | Melepas faktur berstatus DITAHAN ke antrean sync (DITAHAN ke PENDING). Faktur dari Pengajuan Barang sengaja tidak terkirim otomatis, layak ditinjau dulu sebelum masuk pembukuan sungguhan; worker yang benar-benar mengirim. | `procurement.tagihan.save` |
| POST | `/tagihan/:id/tahan` | Menahan faktur yang gagal sync supaya berhenti dicoba ulang (lawan dari `/kirim`). Tanpa ini, faktur yang gagal karena datanya sendiri salah dicoba ulang tanpa batas. | `procurement.tagihan.save` |
| POST | `/tagihan/:id/pembayaran` | Mencatat pembayaran baru atas satu tagihan (menentukan nominal & akun dari body). | `procurement.bayar.save` |
| POST | `/pembayaran/:id/kirim` | Mengirim baris pembayaran yang **sudah tercatat** ke Accurate (`purchase-payment/save.do`). **Sengaja dipicu manusia, bukan worker**: rute ini menarik sisa utang terkini dari Accurate sebelum menembak sebagai penjaga kelebihan bayar, dan worker otomatis akan melewatkan pemeriksaan itu (`pembayaran_kirim.go:12-35`). Menutup celah lama: pembayaran hasil `SusunPembayaranDariPengajuan` sempat lahir PENDING tanpa satu pun worker yang memprosesnya. Menolak bila status bukan PENDING, bila bukti transfer belum diunggah atau ditolak pemeriksa, atau bila faktur belum tersinkron ke Accurate. | `procurement.bayar.save` |

## Bukti Transfer (✅ Diimplementasikan)

Melayani KEDUA asal pembayaran (tagihan vendor maupun Pengajuan Barang), sebab yang dibuktikan sama-sama uang keluar dari bank. **Tiga gerbang berbeda dengan sengaja**: yang mengunggah bukti tidak boleh memeriksa buktinya sendiri (`main.go:1117-1150`).

| Method | Path | Fungsi | Izin |
|---|---|---|---|
| GET | `/pembayaran/antrean-bukti` | Antrean bukti yang menunggu diperiksa. Rute literal, wajib sebelum `/pembayaran/:id/...`. | `budget.bukti.review` |
| POST | `/pembayaran/:id/bukti-transfer/review` | Menyetujui atau menolak bukti transfer. | `budget.bukti.review` |
| GET | `/pembayaran/:id/bukti-transfer/file` | Mengunduh berkas bukti. | `budget.view` |
| POST | `/pembayaran/:id/bukti-transfer` | Mengunggah bukti transfer atas satu baris pembayaran. `409` bila bukti sudah disetujui, `403` bila bukan milik pengunggah. | `budget.ap.bayar` |

## KPI Account Payable (Internal, ✅ Diimplementasikan)

Dua endpoint dipanggil **employee-service** (mesin, bukan manusia) saat menghitung skor KPI, digerbang **dua lapis**: header gateway biasa (siapa pun karyawan yang login lewat `/api/procurement/...` lolos lapis ini) DAN `?key=` yang dicocokkan ke env `PROCUREMENT_SERVICE_KEY` lewat `gerbangKunciLayananKPI` (`kpi_pembayaran.go:39-54`, pola sama `services/monitoring/kpi_uptime.go`). Kunci yang belum dikonfigurasi MENUTUP rute, bukan membukanya.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/faktur/pembayaran-tren?bulan=YYYY-MM&key=...` | Tren ketepatan waktu pembayaran hutang per bulan: `tepat_waktu_persen` (nil bila tidak ada faktur yang bisa dinilai bulan itu, dibedakan sengaja dari 0% atau 100%), jumlah jatuh tempo/tepat waktu/terlambat/belum lunas/dikecualikan. Faktur lunas lewat alokasi uang muka (tanpa `lastPaymentDate` individual) dikecualikan dari penyebut, bukan dihukum maupun diluluskan. Menarik seluruh `purchase-invoice/list.do` dari Accurate, di-cache 1 jam in-memory. |
| GET | `/pengajuan/kpi-ap?key=...` | Realisasi pengajuan untuk KPI Account Payable: ketepatan waktu (ambang 30 menit) dan ketepatan nominal. Gerbang dua lapis sama seperti di atas. |

## Kas Kecil & Pengajuan Budget (ringkas, ✅ Diimplementasikan)

Modul ini menumpang procurement-service demi menghemat satu modul gateway; isinya BUKAN cermin Accurate seperti sisa service ini, justru berhenti SEBELUM Accurate. **Aturan bisnis, jenjang persetujuan per Tujuan, ambang plafon, dan tabel endpoint inti kas kecil sudah lengkap di [[Finance - Kas Kecil dan Pengajuan Budget]] (§Sudah Ada di Kode, §Endpoint) dan TIDAK diulang di sini** (satu fakta satu tempat). Tabel di bawah hanya melengkapi rute yang belum tercatat di dok itu.

| Method | Path | Fungsi | Izin |
|---|---|---|---|
| GET | `/kas/departemen` | Daftar departemen yang punya unit kas kecil, untuk dropdown plafon. | `kaskecil.view` |
| GET / POST | `/kas/plafon` | Lihat / tetapkan plafon kas kecil per departemen per periode. | `kaskecil.view` (baca) · `kaskecil.master.save` (tulis) |
| GET | `/kas/akun` · `/kas/cv` · `/kas/proyek` | Katalog Accurate untuk dropdown transaksi kas kecil: akun beban, CV (sumber dana), proyek karyawan. Ditarik hidup dari integration-service, bukan disalin jadi master ERP. | `kaskecil.view` |
| GET | `/katalog/akun-beban` · `/katalog/sumber-dana/pt` · `/katalog/sumber-dana/cv` · `/katalog/proyek` · `/katalog/bahan-baku` · `/katalog/satuan` | Alamat NETRAL (tanpa prefix `/kas/`) untuk katalog Accurate yang sama, dipakai bersama modul Pengajuan Barang supaya pengaju dari divisi lain (PPIC, GA, marketing) tidak tergerbang izin kas kecil. Handler dipakai ulang, bukan disalin. `/katalog/bahan-baku` diteruskan dari manufaktur (kode bahan baku sah untuk tipe RAWMATERIAL). | `budget.view` ATAU izin kas manapun (`katalogBaca`, OR eksplisit) |
| GET | `/katalog/gudang` | Daftar gudang Accurate untuk dropdown pengaturan. | `procurement.view` |
| GET | `/kas/saldo` | Plafon, terpakai, sisa satu unit kas. | `kaskecil.view` |
| POST | `/kas/putuskan-jalur` | Menjawab jalur mana yang berlaku (kas kecil vs pengajuan budget) untuk sebuah rencana transaksi, TANPA mencatat apa pun. | Baca kas |
| GET | `/kas/buku-besar` | Baris + saldo berjalan, bentuk yang dicocokkan pemegang kas dengan uang fisik di tangannya. | `kaskecil.view` |
| GET | `/kas/jurnal/pratinjau` · POST `/kas/jurnal/kirim` · POST `/kas/jurnal/:nomor/batal` | Jurnal harian ke Accurate. Urutan pendaftaran mengikat: pratinjau & kirim WAJIB sebelum `:nomor/batal`. | `kaskecil.approve.finance` |
| GET | `/kas/alokasi/pratinjau` · POST `/kas/alokasi/kirim` | Alokasi awal bulan: membongkar penampung akun 2205 jadi beban per CV, satu Journal Voucher per CV. | `kaskecil.approve.finance` |
| PATCH | `/kas/transaksi/:nomor/akun` | Penetapan akun beban oleh Finance, terpisah dari mencatat transaksi. | `kaskecil.approve.finance` |
| POST | `/kas/transaksi/:nomor/cek-cc` | Cek CC (kartu kredit korporat) oleh Finance. | `kaskecil.approve.finance` |
| GET / POST | `/budget/parameter` | Parameter berversi jalur PENGAJUAN BUDGET (ambang Direktur, dll), koleksi sama dengan `/kas/parameter` tapi lingkup kunci terpisah. | `kaskecil.view` (baca) · `kaskecil.master.save` (tulis, belum punya izin master sendiri) |
| GET | `/budget/pengajuan` | Daftar pengajuan budget (di luar antrean persetujuan yang sudah didokumentasikan di [[Finance - Kas Kecil dan Pengajuan Budget]]). | `gateBacaBudget` |
| GET | `/budget/pengajuan/:nomor` | Detail satu pengajuan budget. | `gateBacaBudget` |
| PATCH | `/budget/pengajuan/:nomor` | Pemohon menyunting pengajuan miliknya sendiri; handler yang memverifikasi kepemilikan. | `budget.pengajuan.save` |
| POST | `/budget/pengajuan/:nomor/batal` | Pembatalan oleh pemohon. | `budget.pengajuan.save` |
| PATCH | `/budget/pengajuan/:nomor/alokasi` | Alokasi akuntansi (akun beban/CV/proyek) oleh Finance, tahap terakhir sebelum Direktur atau tahap tunggal bila jenjang tidak sampai Direktur. | `budget.approve.finance` |
| POST | `/katalog/impor` | Penyegaran manual katalog Accurate (akun, cabang, departemen, kategori barang, satuan, pajak, dll), dipakai kas kecil DAN Pengajuan Barang. | `procurement.import` |

> **Gerbang rute persetujuan budget sengaja LONGGAR.** `POST /budget/pengajuan/:nomor/setujui|tolak|revisi` meloloskan siapa pun pemegang salah satu izin `budget.approve.{finance,direksi,aset,procurement}` di gerbang rute; yang memutuskan izin mana yang COCOK dengan tahap berjalan pada dokumen tertentu adalah handler. Lolos di gerbang rute TIDAK berarti berwenang menyetujui tahap ini.

## Belum Diimplementasikan / Catatan

- **Lampiran pengajuan pembelian tidak punya endpoint unggah** sudah **tidak berlaku**; itu klaim atas modul lama yang dihapus. Lihat catatan di bagian Pengajuan Barang di atas.
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
- **TBD, ditemukan saat audit 2026-09-12, belum diverifikasi mana yang menang**: `GET /katalog/satuan` didaftarkan DUA kali di `main.go` dengan handler dan gerbang berbeda (`main.go:705` `katalogBaca` + `ListKatalogSatuan`, memanggil integration-service; `main.go:1076` `akses` + `KatalogHandler(JenisSatuan)`, membaca cermin Mongo `katalog`). Kelas masalahnya sama dengan jebakan rute tertelan yang sudah tercatat di tim (urutan pendaftaran Fiber mengikat), tetapi di sini KEDUANYA path literal tanpa parameter, jadi belum jelas dari pembacaan main.go saja mana yang benar-benar dieksekusi saat runtime. `TestKatalogTidakMemanggilAccurate` (yang mewajibkan rute ini tidak memanggil Accurate langsung) tidak membedakan keduanya karena `ListKatalogSatuan` sendiri memanggil integration-service, bukan `client *AccurateClient` yang di-mock test itu. Perlu ditelusuri terpisah (baca tree routing Fiber v2 atau uji manual) sebelum dok ini menyatakan gerbang/perilaku `GET /katalog/satuan` secara pasti; tabel di atas mengikuti dokumentasi lama untuk baris ini dan TIDAK memasukkannya ke bagian Kas Kecil ringkas karena alasan ini.

## Dependensi & Integrasi

- Accurate Online (`vendor/save.do`, `vendor/list.do`, `vendor/detail.do`, `payment-term/list.do`) — [[ADR - 0001 Akuntansi via Accurate]].
- [[CORE - API Master Gateway]] (`PROCUREMENT_MODULE_URL`).

## Dokumen Terkait

- [[Microservices - Procurement Service]]
- [[Finance - Kas Kecil dan Pengajuan Budget]]
- [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]] (konteks historis, penunjukan per tahap sudah tidak berjalan lewat rute HTTP)
- [[API - Index]]
