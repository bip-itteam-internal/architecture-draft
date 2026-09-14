## Deskripsi

*Endpoint **inventory-service** (aset/inventaris GA: item, master data, repair history). Gateway: `/api/inventory/*`. Grounded ke `services/inventory`.*

- **Implementasi**: [[Microservices - Inventory Service]] · **Status**: ✅
- **Indeks**: [[API - Index]] · RBAC: `RequireGeneralAffair` (sebagian rute master/data-type & health bersifat publik di service). Booking Ruang (`/peminjaman*`) dan feed kalender punya lapisan gerbang sendiri, lihat bagiannya di bawah.

## Master & data-type
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/master-items` | List master item | publik |
| GET | `/data-type/category` · `/electronics` · `/item-status` · `/repair` · `/service` · `/repair-status` · `/component-action` | Enum | publik |
| GET | `/categories` | Daftar kategori (registry, saran) | publik |
| POST | `/categories` | Daftar kategori baru (bebas-ketik, disimpan apa adanya) | GeneralAffair |
| GET | `/category-mapping` | Pemetaan kategori-ERP → golongan-Accurate (ADR-0037, dipakai FE Tab B/C) | publik |
| POST | `/category-mapping` | Upsert pemetaan (dedup `category_key`) | GeneralAffair |
| DELETE | `/category-mapping/:id` | Hapus pemetaan | GeneralAffair |
| GET | `/summary` | Ringkasan (jumlah + biaya) | publik |
| GET | `/health` | Health check | publik |

## Inventory items
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/item` | Buat item inventaris | GeneralAffair |
| GET | `/items` | List item | publik |
| GET/PATCH/DELETE | `/item/:id` | Detail/update/hapus item (PATCH juga = serahkan/ubah pemegang **& ceklis rekonsiliasi** via `accurate_asset_no`) | GeneralAffair |
| PATCH | `/item/:id/approve-handover` | SPV menyetujui serah-terima | **SPV penaung** (gate `SupervisedDepartments`, bukan GeneralAffair) |
| GET | `/item/master/:master_id/spec-template` | Template spesifikasi | GeneralAffair |
| POST/GET | `/item/upload/presigned-url` · `/item/upload/presigned-get` | Presigned upload/download dokumen (`purchase` · `arrived` · `handover`) | GeneralAffair |

## Repair history
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| POST | `/item/repair/:item_id` | Buat record perbaikan | GeneralAffair |
| GET | `/item/repair/:item_id/all` · `/item/repair/:repair_id` | List/detail perbaikan | GeneralAffair |
| PATCH | `/item/repair/:repair_id` | Edit record perbaikan | GeneralAffair |

## Opname perlengkapan (ADR-0067)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/perlengkapan-opname[?periode=YYYY-MM]` | List record opname per `(item_no, periode)`; **default bulan berjalan**, `?periode=` untuk riwayat | GeneralAffair (`PermGaWork`) |
| POST | `/perlengkapan-opname` | Simpan hitung fisik (upsert per `(item_no, periode bulan berjalan)`) | GeneralAffair (`PermGaWork`) |

- Koleksi `ga_opname`. Staff GA meng-input **hitung fisik**; qty Accurate live diambil FE dari [[API - Integration Service]] (`/accurate/stocks/list?category=Perlengkapan`). Selisih & akurasi dihitung **di FE** (pola FASS), BE cuma MENYIMPAN.
- POST body `{item_no, nama?, qty_fisik, qty_accurate_snapshot}`; `item_no`+`qty_fisik` wajib (`qty_fisik ≥ 0`). `qty_accurate_snapshot` = qty Accurate yang **dilihat operator** saat menghitung — dipatok agar selisih tak bergeser oleh sync. `selisih = qty_fisik − qty_accurate_snapshot` dihitung & disimpan BE; `oleh` dari header `EmployeeID`. **`periode` di-set SERVER = bulan berjalan WIB** (`Asia/Jakarta`, `periodeDari`), input client diabaikan → tak bisa menulis ke bulan lampau/depan.
- **Unique index `uniq_item_periode` = `(item_no, periode)`** (dibuat saat boot, non-fatal, penjaga `DB==nil`): satu record per barang per bulan; opname ulang bulan sama menimpa, bulan baru = record baru. Menuntaskan risiko dup upsert. Record lama pra-periode di-backfill dari `at` (WIB).

## Perlengkapan campur + padanan Accurate (ADR-0069)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/perlengkapan-units/count` | `{data:{<item_no>: jumlah_barang_terpadan}}` — prefill Hitung Fisik opname | GeneralAffair (`PermGaWork`) |
| GET | `/perlengkapan-units[?item_no=]` | Daftar barang perlengkapan (ber-`accurate_item_no`; editor padanan) | GeneralAffair (`PermGaWork`) |

- Barang perlengkapan = `InventoryItem` yang **dipadankan** ke item perlengkapan Accurate → **`accurate_item_no`** (`item_no`; **TERPISAH** dari `accurate_asset_no` aset tetap). **Diinput lewat `POST /item` biasa** (seperti aset tetap, tanpa field khusus — CAMPUR di `/items` & summary), lalu dipadankan/lepas lewat **`PATCH /item/:id`** (`accurate_item_no`; kosong = lepas). Keberadaan `accurate_item_no` = penanda perlengkapan.
- ⛔ **Satu-satunya perlakuan khusus: `GetPenyusutan` mengecualikan item ber-`accurate_item_no`** (akun 1606 tak disusutkan → tak masuk opex). Kelola Aset (`/items`) & summary sengaja campur. Many-to-one: Accurate qty>1 → N barang per `item_no`. ⚠️ KPI `akurasi_aset_ga` (Fase 2) wajib mengecualikan `accurate_item_no`.

## Booking Ruang GA (ADR 0094)

Grounded ke `services/inventory/peminjaman_*.go`. Keputusan desain: [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]]. Konsep domain: [[GA - Asset Loan & Room Booking]]. Path di bawah adalah path service; gateway membuang prefix `/api/inventory`.

**Lapisan gerbang** (`daftarkanRutePeminjaman`):
- **Identitas**: SEMUA rute `/peminjaman*` menolak pemanggil tanpa `BIP-Employee-ID` dengan **401** (`gateIdentitasPeminjaman`).
- **`ga.view` / `ga.work`**: `gateGa(...)`, jatuh ke `RequireGeneralAffair` bila kill-switch `GA_PERMISSION_ENFORCEMENT=off`. Ditolak **403**.
- **`RequireHRISOrITSupervisor`**: `system_roles.hris` atau `system_roles.it` bernilai supervisor/admin.
- **Penunjukan HR**: wewenang menyetujui dan menolak diputus fungsi murni (`TentukanSetujui`, `TentukanTolak`) terhadap daftar penyetuju perusahaan, bukan izin modul.
- **Mengajukan** cukup identitas, tanpa izin modul.

| Method | Path | Fungsi | Auth | Respons sukses |
|---|---|---|---|---|
| GET | `/peminjaman/ruang[?semua=true]` | Master ruang perusahaan pemanggil, urut nama. Ruang nonaktif hanya ikut bila `semua=true` **dan** pemanggil memegang `ga.work` | identitas | `{data: [Ruang], ada_penyetuju: bool}` |
| POST | `/peminjaman/ruang` | Tambah ruang (aktif kecuali disebut lain) | identitas + `ga.work` | 201 `{data: Ruang}` |
| PATCH | `/peminjaman/ruang/:id` | Ubah sebagian; menonaktifkan lewat `aktif: false` (tak ada DELETE) | identitas + `ga.work` | `{data: Ruang}` |
| GET | `/peminjaman/slot?ruang_id=&tanggal=YYYY-MM-DD` | Slot 30 menit dalam jam operasional ruang pada tanggal WIB itu | identitas | `{data: [{mulai_at, selesai_at, terpakai}]}` |
| GET | `/peminjaman/saya[?status=]` | Booking milik pemanggil, tanpa saringan perusahaan, maks 200 | identitas | `{data: [Peminjaman]}` |
| GET | `/peminjaman/perlu-aksi` | Antrean `DIAJUKAN` perusahaan pemanggil yang `selesai_at`-nya belum lewat, tanpa booking milik pemanggil, maks 200 | identitas + ditunjuk HR (bukan: 403) | `{data: [Peminjaman]}` |
| GET | `/peminjaman/penyetuju/saya` | Apakah pemanggil ditunjuk sebagai penyetuju | identitas | `{data: {penyetuju: bool}}` |
| GET | `/peminjaman/penyetuju[?company=]` | Daftar penyetuju satu perusahaan | identitas + `RequireHRISOrITSupervisor` | `{data: PenyetujuPeminjaman}` |
| PUT | `/peminjaman/penyetuju[?company=]` | Menimpa seluruh daftar penyetuju | identitas + `RequireHRISOrITSupervisor` | `{data: PenyetujuPeminjaman}` |
| GET | `/peminjaman[?status=&ruang_id=&dari=&sampai=]` | Jadwal seluruh booking perusahaan pemanggil, `mulai_at` terbaru dulu, maks 200 | identitas + `ga.view` | `{data: [Peminjaman], batas: 200, terpotong: bool}` |
| POST | `/peminjaman` | Ajukan booking | identitas | 201 `{data: Peminjaman}` |
| POST | `/peminjaman/:nomor/setujui` | Setujui | identitas + ditunjuk HR | `{data: Peminjaman, ditolak_otomatis: [nomor]}` |
| POST | `/peminjaman/:nomor/tolak` | Tolak, badan `{alasan}` wajib | identitas + ditunjuk HR | `{data: Peminjaman}` |
| POST | `/peminjaman/:nomor/batal` | Batal oleh pemohon, badan `{alasan}` opsional (badan kosong sah) | identitas + pemohon | `{data: Peminjaman}` |
| GET | `/peminjaman/:nomor` | Detail booking | identitas + berhak melihat (bukan: 404) | `{data: Peminjaman}` |
| PATCH | `/peminjaman/:nomor` | Ubah sebagian oleh pemohon | identitas + pemohon | `{data: Peminjaman}` |

- Rute literal didaftarkan SEBELUM saudara ber-`:nomor`, dikunci `TestRutePeminjamanLiteralTakTertelanNomor`.
- `?company=` pada rute penyetuju hanya dihormati bagi admin pusat (`common.EffectiveCompanyID`); pemakai lain selalu terkunci ke perusahaannya sendiri.

### Bentuk data
- **`Ruang`**: `id`, `company_id`, `nama`, `lokasi`, `kapasitas`, `fasilitas[]`, `jam_buka`, `jam_tutup` (`"HH:MM"` dibaca WIB), `aktif`, `metadata`. `nama_key` dan kunci sewa persetujuan (`kunci_token`, `kunci_sampai`) tak pernah dikirim ke klien.
- **`Peminjaman`**: `nomor` (`PJR-YYYYMMDD-nnn`), `company_id`, `jenis` (hari ini selalu `ruang`), `sumber_id` (id ruang), `sumber_nama`, `pemohon_id`, `pemohon_nama`, `divisi`, `posisi`, `no_wa`, `keperluan`, `keterangan`, `mulai_at`, `selesai_at`, `status` (`DIAJUKAN` · `DISETUJUI` · `DITOLAK` · `DIBATALKAN`), `asal{modul, id}` (opsional; belum diisi jalur mana pun), `riwayat[{aksi, oleh, nama, posisi, alasan, waktu}]`, `metadata`. Nama ruang, identitas pemohon, serta nama dan posisi di riwayat **dibekukan** saat tindakan.
- **`riwayat.aksi`**: `ajukan`, `setujui`, `tolak`, `batal`, `ubah`, `tolak_otomatis`, `batal_setujui_bentrok`, `batal_setujui_tak_terperiksa`. Tiga terakhir ber-`oleh: "sistem"`.
- **`PenyetujuPeminjaman`**: `company_id`, `penyetuju[{employee_id, nama, posisi}]`, `diubah_oleh`, `diubah_at`. Perusahaan yang belum pernah menunjuk dibalas daftar kosong, bukan galat.

### Validasi & aturan
- **`POST /peminjaman`** badan `{ruang_id, mulai_at, selesai_at, keperluan, no_wa, keterangan}` (waktu RFC3339). Urutan pemeriksaan (`handleAjukanPeminjaman` + `RakitPengajuan`):
  1. Ruang: id tak sah **400**, tak ada di perusahaan pemanggil **404**.
  2. Isian **400**: `keperluan` wajib, maks 500 karakter; `no_wa` hanya angka dan pemisah lazim (spasi `-` `+` `(` `)` `.`), 8 sampai 15 angka, disimpan tanpa pemisah dan prefiks tak diubah; `keterangan` maks 500.
  3. Jadwal **400** (`ValidasiJadwal`): ruang nonaktif; `selesai_at` sesudah `mulai_at`; `mulai_at` belum lewat; menit kelipatan 30; mulai dan selesai di tanggal WIB yang sama; di dalam `jam_buka`-`jam_tutup`.
  4. HR belum menunjuk penyetuju **422**.
  5. Bertumpuk dengan booking `DISETUJUI` di ruang yang sama **409** (pesan menyebut jam yang terpakai).
- Yang **sengaja tidak** diperiksa: durasi maksimum, jarak pemesanan ke depan, kapasitas.
- **Bentrok**: rentang setengah-terbuka `[mulai, selesai)`, jadi 10:00-11:00 dan 11:00-12:00 tidak bentrok. Hanya `DISETUJUI` yang memegang slot; `DIAJUKAN` lain boleh antre di slot yang sama.
- **Master ruang** (`ValidasiRuang`, atas hasil gabungan PATCH): `nama` wajib maks 100 karakter; `jam_buka`/`jam_tutup` `HH:MM` bermenit 00 atau 30 dan buka sebelum tutup; `kapasitas` tak negatif → **400**. Nama ganda per perusahaan (tanpa beda huruf besar/kecil, unique index `company_id + nama_key`) → **409**. Ruang tak ditemukan → **404**.
- **`GET /peminjaman/slot`**: `tanggal` bukan `YYYY-MM-DD` **400**; ruang nonaktif **400**. Slot tak memuat identitas pemakai, nomor, maupun keperluan (dipatok `TestSlotRuangTanpaIdentitas`).
- **Saringan daftar**: `status` hanya `DIAJUKAN|DISETUJUI|DITOLAK|DIBATALKAN` (tak peka huruf besar/kecil), nilai lain **400**. `dari`/`sampai` `YYYY-MM-DD` WIB, `sampai` inklusif, memilih booking yang **beririsan** dengan rentang; akhir mendahului awal **400**.
- **`PUT /peminjaman/penyetuju`** badan `{employee_ids: [string]}`: kosong dan ganda dibuang, maks 20 orang (**400**). Daftar tak kosong divalidasi ke employee-service `GET /list?type=employee` dengan header `BIP-Gateway-ID` dan identitas pemanggil diteruskan. Gagal-tertutup: daftar karyawan tak terbaca **503** (tak disimpan); id yang bukan karyawan aktif perusahaan itu **422**, pesannya menyebut id-nya. Daftar kosong disimpan tanpa pemeriksaan.
- Galat umum: DB belum tersambung **503**; galat lain **500** berpesan umum, teks galat driver hanya dicatat log (`balasGalatPeminjaman`).

### Kode status aksi booking (`/peminjaman/:nomor*`)
- Nomor tak cocok `^PJR-\d{8}-\d{3,}$` → **400** sebelum menyentuh DB.
- Booking tak ada, **atau pemanggil tak berhak melihatnya** → **404**, bukan 403. Berhak melihat (`bolehLihatPeminjaman`): pemohon (tanpa syarat perusahaan, karena `employee_id` bertahan saat mutasi, [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]); penyetuju yang ditunjuk atau pemegang `ga.view` hanya bila perusahaan booking sama dengan perusahaan pemanggil.
- **setujui** (urut): status bukan `DIAJUKAN` **409** · bukan penyetuju **403** · booking milik sendiri **403** · `selesai_at` sudah lewat **409** · ruang kini nonaktif, atau jadwalnya di luar jam operasional yang berlaku sekarang **409** (dibaca ulang sebelum kunci) · kunci ruang sedang dipegang penyetuju lain **409** · sudah ada `DISETUJUI` yang bertumpuk **409** · status atau jadwal booking berubah sejak dibaca **409** · cek ulang sesudah tulis menemukan tumpukan: dikembalikan ke `DIAJUKAN` (riwayat `batal_setujui_bentrok`) **409** · cek ulang tak terbaca: dikembalikan ke `DIAJUKAN` (riwayat `batal_setujui_tak_terperiksa`) **503**. Sukses: pengajuan `DIAJUKAN` lain yang bertumpuk di ruang itu ditolak otomatis dan nomornya dikirim di `ditolak_otomatis`; tolak otomatis yang gagal hanya dicatat log, tidak membatalkan persetujuan.
- **tolak**: status bukan `DIAJUKAN` **409** · bukan penyetuju atau booking milik sendiri **403** · `alasan` kosong atau lebih dari 500 karakter **400** · kalah balapan **409**.
- **batal**: bukan pemohon **403** · `DISETUJUI` yang sudah mulai **409** · status final **409** · `alasan` lebih dari 500 karakter **400** · kalah balapan **409**. Tidak ada syarat perusahaan: pemohon yang sudah pindah tenant tetap bisa membatalkan.
- **ubah (PATCH)**: badan pointer `{ruang_id, mulai_at, selesai_at, keperluan, no_wa, keterangan}`, field yang tak disebut tak berubah. Bukan pemohon **403** · perusahaan booking beda dari perusahaan pemanggil sekarang **403** · `DISETUJUI` yang sudah mulai **409** · status final **409**.
  - Ruang atau jam berubah: hasil gabungan divalidasi utuh seperti pengajuan baru (400/404/422/409; booking itu sendiri tak dihitung bentrok). Booking `DISETUJUI` kembali `DIAJUKAN` (slot lama dilepas), riwayat `ubah` beralasan `Jadwal sebelumnya: ...`, dan penyetuju dikabari lagi.
  - Hanya isian berubah: hanya isian yang divalidasi, status dipertahankan.
  - Tak ada yang berubah **400** · kalah balapan **409**.
- **Penjaga balapan**: setiap penulisan status memakai filter `{nomor, status diharapkan, sumber_id, mulai_at, selesai_at}` (`filterPenjagaPeminjaman`); tak cocok dibalas 409. Isian tidak ikut dijaga, jadi dua perubahan isian bersamaan saling timpa.

### Notifikasi
- Dikirim di goroutine (`jalankanNotifikasiPeminjaman`), tidak ditunggu respons, best-effort (galat hanya dicatat log). Endpoint notification-service: `POST /inbox/send?key=` dengan header `BIP-Gateway-ID` (`kirimInbox`). Tanpa header itu notification-service membalas 401 dan kabarnya hilang senyap, dan itulah yang terjadi sampai 2026-09-14.
- `peminjaman-ga-perlu-aksi` → seluruh penyetuju kecuali pemohon: saat diajukan, dan saat booking yang `DISETUJUI` diubah ruang atau jamnya.
- `peminjaman-ga-diperbarui` → pemohon: disetujui, ditolak (dengan alasan), ditolak otomatis (judul berbeda: slot sudah dipakai booking lain). Batal tidak mengirim kabar.
- `app_route` `/ga/peminjaman/<nomor>`; notification-service memetakannya ke `/ga/peminjaman?nomor=<nomor>` untuk push web (`services/notification/webpush.go`). Lihat [[Microservices - Notification Service]].

## Feed kalender (Booking Ruang)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/internal/calendar-feed?from=&to=` | Booking milik pemanggil untuk calendar-service (provider `inventory`) | identitas; tanpa `BIP-Employee-ID` **403** (kontrak seragam feed kalender, bukan 401) |

- `from` dan `to` wajib RFC3339, `to` tak boleh mendahului `from`, rentang maks 400 hari → **400**. DB belum siap **503**, galat lain **500**.
- Respons `{items: [...]}`, tak pernah `null`. Tiap item: `id` `inventory:room_booking:<nomor>`, `source` `inventory`, `kind` `room_booking`, `title` `Booking <nama ruang>: <keperluan diringkas>`, `start_at`, `end_at`, `all_day: false`, `scope` `personal`, `owner{employee_id, full_name}`, `company_id` (perusahaan pembaca), `status` (`DIAJUKAN` → `tentative`, `DISETUJUI` → `confirmed`, selainnya `cancelled`), `deep_link` `/ga/peminjaman?nomor=<nomor>`, `meta{nomor, ruang}`.
- Yang dipancarkan hanya booking ber-`pemohon_id` pemanggil, ber-`company_id` perusahaan pemanggil, tanpa `asal`, dan beririsan dengan rentang (`filterFeedPeminjaman` + `saringFeedPeminjaman`). Jadwal ruang orang lain tidak masuk kalender siapa pun.
- Prefix `/internal/` tidak membuat rute ini privat: penyaringan hak akses dikerjakan handler. Lihat [[Microservices - Calendar Service]].

## Kontrak request & validasi (grounded)

Detail berikut grounded ke `services/inventory` (`controller.go`, `validation.go`).

### `POST /item` — buat item
- **Wajib**: `specs` (min 1, `key` & `value` non-kosong); `purchase_date`; `purchase_document`. Master item via `master_id` (pakai master lama) **atau** `item_name` + `item_category` (buat master baru — keduanya **bebas-ketik**, disimpan apa adanya; `item_category` juga didaftarkan ke registry `category`).
- **Pemegang OPSIONAL**: `held_by` boleh kosong → aset lahir "Tersedia di GA". Bila `held_by.department` diisi, `held_by.full_name` **wajib** (tolak `400 "fullname required"`).
- **Opsional**: `location`, `useful_life_years`, `arrived_date`, `arrived_document`, `purchase_price`, `notes`, `held_by.hold_period.assigned_at`/`revoked_at`.
- **ID ter-generate**: `INV-BIP-DDMMYY-NAMA-n` (tanggal dari `purchase_date` dibaca WIB).
- Dokumen (`purchase_document`/`arrived_document`) diverifikasi **ada di MinIO** sebelum simpan → tolak `400` bila objek tidak ditemukan.
- Grounded: `CreateInventory` (held_by opsional, `resolveCategory`, `ValidateDocumentsExists`) + `ValidateSpecs` + `generateUniqueID`.

### `PATCH /item/:id/approve-handover` — SPV menyetujui serah-terima
- **Otorisasi non-standar**: di **luar** grup `/item` (tak di-gate `RequireGeneralAffair`). Handler menolak `403` bila `held_by.handover_dept` **tidak** ada di `common.SupervisedDepartments(c)` (klaim `supervised_departments` / header `BIP-Supervised-Departments`). Tolak `400` bila status ≠ `menunggu_spv`.
- **Efek**: `held_by.known_by_spv` = nama SPV (dari body), `known_by_spv_id` dari header, `handover_status=disetujui`.
- Grounded: `ApproveHandover` + `common.SupervisedDepartments`.

### `PATCH /item/:id` — update (partial)
- **Partial update**: hanya field yang dikirim yang di-`$set` (`buildUpdateBson`); semua field opsional. `held_by` di-set hanya bila dikirim (tanpa validasi wajib, beda dari create). Balas `400 "No update fields"` bila tidak ada field.
- **Ceklis rekonsiliasi (ADR-0037)**: kirim `accurate_asset_no` untuk mengonfirmasi/lepas pasangan aset ke Aktiva Tetap Accurate. Non-kosong → `$set accurate_asset_no` + stempel `reconciled_at`; string kosong → `$unset` keduanya (lepas pasangan). `updated_at` tetap distempel walau perubahan hanya `$unset`.
- Grounded: `UpdateInventory` + `buildUpdateBson`.

### `GET /items` — list
- Mengembalikan **seluruh** item (⚠️ **tanpa pagination/search**). Hanya query `?status=` yang dihormati untuk filter server-side; `page` / `limit` / `search` **diabaikan**. Pencarian, filter, **dan paginasi** dilakukan **client-side** di frontend (list page: 10/hal). Respons menyertakan `held_by` (+ jejak serah-terima `handover_status`/`handover_by`/`known_by_spv`; ditampilkan kolom "Karyawan Pemegang", kosong → "Tersedia di GA"), serta `purchase_price`, `location`, `useful_life_years`, `accurate_asset_no`/`reconciled_at` — dipakai kolom, **export Excel** (FE, `lib/export.ts`), & **ceklis rekonsiliasi** (Tab Cocokkan). Nilai buku/penyusutan dihitung FE (estimasi garis lurus).
- Grounded: `ListInventory` + `InventoryListResponse`.

### `/category-mapping` — pemetaan kategori-ERP → golongan-Accurate (ADR-0037)
- `GET` (publik) balas seluruh pemetaan; `POST` (GA) upsert by `category_key` (kategori dinormalisasi `NormalizeCategoryKey` = lowercase + rapikan spasi) — kategori yang sama **menimpa**, bukan menggandakan; `DELETE /:id` (GA) hapus satu. Unique index `category_key`.
- Dipakai FE Tab B (editor) & Tab C (mengelompokkan aset per golongan untuk saran pasangan + matrix). Golongan Accurate diambil live dari `GET /accounting/fixed-assets` ([[API - Integration Service]]).
- Grounded: `ListCategoryMapping` · `UpsertCategoryMapping` · `DeleteCategoryMapping` (`mapping.go`).

### `GET /summary` — ringkasan (jumlah + biaya)
- Respons: `{ data: { overview: [{ total_assets, new_arrivals, total_purchase_cost }], by_category: [{ category, total }], by_status: [{ status, total }], by_department: [{ department, total }], total_repair_cost } }`. `new_arrivals` = item dengan `arrived_date` ≤ 30 hari terakhir. `total_purchase_cost` = Σ `purchase_price`; `total_repair_cost` = Σ biaya dari `repair_history`.
- Grounded: `GetSummary`.

### Upload dokumen (`POST /item/upload/presigned-url`)
- **Tipe diizinkan**: `image/*` dan `application/pdf`; **maks 4 MB**. Document valid: `purchase` (nota), `arrived` (foto barang), **`handover`** (dokumen serah terima — menggantikan catatan teks). Tolak `400 "file type not allowed"` / `"invalid service or document"` bila melanggar. Nama objek dibersihkan (`sanitizeObjectName`).
- **Integritas**: saat item disimpan, `ValidateDocumentsExists` memverifikasi objek benar-benar ada di MinIO (cegah `NoSuchKey`/referensi menggantung). Presigned di-sign untuk `MINIO_PUBLIC_BASE_URL` — pastikan skema/host cocok dengan yang diakses browser (isu *mixed-content* bila app HTTPS & MinIO HTTP).
- Grounded: `UploadRules` + `ValidateFileMeta` + `ValidateDocumentsExists`.

## Dokumen Terkait
- [[Microservices - Inventory Service]] · [[GA - Asset Loan & Room Booking]] · [[API - Index]] · [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] · [[API - Integration Service]]
- Booking Ruang: [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]] · [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]] · [[Microservices - Calendar Service]] · [[Microservices - Notification Service]]
