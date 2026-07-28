## Deskripsi

*Endpoint **procurement-service** (master Pemasok: CRUD, penomoran, katalog, import awal, worker sync ke Accurate). Gateway: `/api/procurement/*`. Grounded ke `services/procurement/`.*

- **Implementasi**: [[Microservices - Procurement Service]] · **Status**: ⚠️ Implemented (ada catatan) — backend lengkap & terverifikasi berjalan lokal; belum di-deploy, import 139 pemasok belum dijalankan.
- **Indeks**: [[API - Index]] · Auth: gateway key `BIP-Gateway-ID` untuk semua route, plus role guard via `BIP-System-Roles` header (`system_roles["procurement"]`). Role yang diterima: `staff`, `spv`, `admin`; route import khusus `admin`.

## Master Pemasok (✅ Diimplementasikan)

| Method | Path | Fungsi |
|---|---|---|
| GET | `/pemasok` | Daftar pemasok. Query: `cari` (nama/nomor, regex case-insensitive), `kategori`, `sync_status`, `akun_utang_kosong=true` (daftar pantauan finance). |
| GET | `/pemasok/usul-nomor?kategori=` | Usulan nomor berikut per kategori. `400` bila kategori tidak dikenal. |
| POST | `/pemasok` | Buat pemasok. `201` + data (termasuk `id` hasil insert). `400` validasi gagal, `409` nomor sudah dipakai. |
| PUT | `/pemasok/:id` | Sunting pemasok. `400` id/body/validasi gagal, `404` tidak ditemukan, `409` nomor dipakai pemasok lain. |
| GET | `/katalog/syarat-pembayaran` | Opsi syarat pembayaran dari Accurate. `502` bila Accurate tidak dapat dihubungi. |
| POST | `/import` | Import awal seluruh pemasok dari Accurate (role `admin`). Idempoten. `502` bila Accurate gagal. |
| GET | `/health` | Health check (tanpa auth). |

**Request body** `POST /pemasok` & `PUT /pemasok/:id`:
```json
{
  "nama":              "string (wajib)",
  "vendor_no":         "string (wajib) — format <PREFIX>-<angka>, prefix harus cocok kategori",
  "kategori":          "string (wajib) — Pemasok Bahan Baku / Pemasok Bahan Kemas / Umum",
  "no_wa":             "string",
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

**Response** `GET /pemasok/usul-nomor`:
```json
{ "data": { "vendor_no": "PBB-061" } }
```

**Response** `GET /katalog/syarat-pembayaran`:
```json
{ "data": [ { "nama": "DP 50%, Pelunasan Se", "tampilan": "DP 50%, Pelunasan Setelah 30 Hari Barang Diterima" } ] }
```

> `nama` = nilai yang **dikirim** ke Accurate (dipotong 20 karakter oleh Accurate); `tampilan` = teks yang **dibaca user** (dari `memo`, jatuh ke `nama` bila memo kosong). Frontend wajib menampilkan `tampilan` dan mengirim `nama`.

**Response** `POST /import`:
```json
{ "data": { "terimpor": 139 } }
```

## Belum Diimplementasikan / Catatan

- Tidak ada endpoint **hapus pemasok** — penghapusan master pemasok dilakukan finance di Accurate.
- Tidak ada endpoint **pemicu sync manual**; worker berjalan otomatis tiap 30 detik atas baris `PENDING`/`FAILED`.
- Empat field **tidak dapat disinkronkan** ke Accurate (Akun Utang, Akun Uang Muka, Tipe Pemasok, Jenis Dokumen) — lihat [[Microservices - Procurement Service]].
- Pengosongan nilai belum tersinkron (`omitempty`) — TBD, lihat dok implementasi.

## Dependensi & Integrasi

- Accurate Online (`vendor/save.do`, `vendor/list.do`, `vendor/detail.do`, `payment-term/list.do`) — [[ADR - 0001 Akuntansi via Accurate]].
- [[CORE - API Master Gateway]] (`PROCUREMENT_MODULE_URL`).

## Dokumen Terkait

- [[Microservices - Procurement Service]]
- [[API - Index]]
