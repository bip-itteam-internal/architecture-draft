## Deskripsi

*Kalender terpusat lintas modul. Service ini **tidak punya agenda sendiri**: ia menarik agenda dari service lain lewat satu kontrak feed yang seragam, menormalkannya jadi satu bentuk, lalu menyajikannya sebagai satu daftar. Tujuannya agar karyawan punya satu tempat untuk semua yang menyangkut dirinya, dan agar setiap modul baru yang punya tanggal cukup **mendaftarkan feed**, bukan membangun kalender sendiri-sendiri.*

- **Status**: ⚠️ Implemented (ada catatan) — irisan 1 **live di DEV** dan terverifikasi lewat gateway (PR [#1040](https://github.com/bip-itteam-internal/bip-erp/pull/1040), [#1041](https://github.com/bip-itteam-internal/bip-erp/pull/1041), erp-frontend [#823](https://github.com/bip-itteam-internal/erp-frontend/pull/823), 2026-08-06). **PROD belum di-deploy.** Irisan 2 dan 3 belum ada kode.
- **Stack**: Go + Fiber. **Tanpa MongoDB** di irisan 1 (agregator murni; database menyusul di irisan 2 bersama koleksi `calendar_events`).
- **Path di repo**: `bip-erp/services/calendar/` · FE: `erp-frontend/src/features/calendar/` + `src/app/(main)/calendar/`
- **Rute gateway**: `/api/calendar/*` (entri `"calendar"` di map `InternalURL` [[CORE - API Master Gateway]]; masuk `noCacheRoutes`).

## Aturan Integrasi (WAJIB dibaca sebelum menambah fitur bertanggal)

> **Aturan pokok**: fitur apa pun yang punya **tanggal, jadwal, atau tenggat** yang perlu dilihat orang **WAJIB mendaftarkan feed** ke service ini, dan **DILARANG** membangun halaman kalender sendiri.

Alasannya bukan kerapian: tiap kalender tambahan membawa salinan aturan visibilitasnya sendiri, dan salinan itu yang menyimpang diam-diam sampai ada yang melihat agenda yang seharusnya tidak boleh dilihatnya.

### Cara mendaftarkan feed

1. **Kalau service Anda belum punya feed**: tambah `GET /internal/calendar-feed?from=<RFC3339>&to=<RFC3339>` yang membalas `{"items": [...]}`.
2. **Kalau sudah punya**: cukup tambah `kind` baru di endpoint feed yang sudah ada. Tidak ada perubahan di frontend.
3. Tambah satu baris di `providerRegistry` (`services/calendar/providers.go`) bila service Anda belum terdaftar, plus env `<SERVICE>_MODULE_URL` di blok `calendar-service` pada `docker-compose.yml`.

### Bentuk item (wajib diikuti)

| Field | Aturan |
|---|---|
| `id` | Berprefiks sumber: `<source>:<kind>:<id-asli>`. ObjectId antar-service bisa bertabrakan dan React butuh key yang benar-benar unik |
| `kind` | Slug jenis agenda. Jenis yang belum dikenal FE tetap tampil dengan gaya netral, jadi aman menambah duluan |
| `start_at` / `end_at` | RFC3339 |
| `all_day` | Dipisah dari waktu. Cuti, libur, dan ulang tahun berlangsung seharian; interview dan rapat berjam. Tanpa penanda ini tampilan bulanan salah merender keduanya |
| `scope` | `personal` \| `department` \| `company` |
| `deep_link` | **Wajib**. Kalender adalah **pintu, bukan tujuan**: mengkliknya berarti lompat ke halaman modul asalnya. Karena itu feed tak perlu menyalin detail agenda |
| `status` | `confirmed` \| `tentative` \| `cancelled` |

### Aturan yang tidak boleh dilanggar

- **Penyaringan hak akses dikerjakan DI SERVICE SUMBER**, bukan di kalender. Kalender sengaja tidak punya aturan visibilitas sendiri.
- **Prefix `/internal/` TIDAK membuat rute privat.** Gateway tetap meneruskan permintaan dari internet, jadi tiap endpoint feed wajib memeriksa identitas pemanggil sendiri. Lihat [[Microservices - Employee Service]] yang sudah mencatat pola ini di rute `/internal/check`.
- **Jangan masukkan URL provider ke map yang divalidasi `ValidateInternalURL`.** Penjaga itu memanggil panic untuk URL kosong, dan di sini URL kosong adalah keadaan sah: service sumber yang belum ter-deploy cukup dilewati. Melanggar ini memadamkan seluruh kalender hanya karena satu service belum di-deploy.
- **Jangan menulis ulang resolusi milik modul lain.** Feed shift memanggil resolver jadwal yang sama dengan halaman Jadwal, karena urutan menangnya berlapis (roster menimpa jadwal dasar, lalu Tukar Shift menimpa keduanya). Menyalin urutan itu melahirkan sumber kebenaran kedua yang pasti menyimpang.
- **Jangan menambah endpoint kalender sendiri.** Rencana `GET /bookings/calendar` di [[GA - Asset Loan & Room Booking]] harus menjadi `/internal/calendar-feed` di [[Microservices - Inventory Service]] saat dikerjakan, bukan kalender kedua.
- **Feed yang gagal tidak boleh menjatuhkan kalender.** Kegagalan apa pun (termasuk 404 karena endpoint belum ada) turun kelas jadi penanda `degraded`, dan frontend memberi tahu pengguna. Kalender bolong tanpa pemberitahuan lebih berbahaya daripada kalender yang mengaku sedang pincang.

### Checklist untuk AI agent

Saat merencanakan fitur yang menyentuh tanggal, jawab dulu:

1. Apakah fitur ini menghasilkan sesuatu yang orang perlu lihat di kalender? Kalau ya, feed-nya masuk lingkup pekerjaan, bukan follow-up.
2. Siapa yang boleh melihat item ini, dan apakah penyaringnya sudah ada di service sumber?
3. Apakah item ini seharian atau berjam?
4. `deep_link`-nya ke halaman mana?
5. Apakah jenis ini bertabrakan dengan feed yang sudah ada (mis. hari libur yang sudah dipancarkan attendance)?

## Endpoint / Fitur (Sudah Diimplementasikan)

**Publik (lewat gateway):**
- `GET /api/calendar?from&to&scope&kinds` → `{ items[], degraded[] }`. `from`/`to` wajib RFC3339, `to >= from`, rentang maksimal 400 hari. `scope` opsional (`personal`/`department`/`company`), `kinds` opsional (dipisah koma).

**Feed yang sudah terdaftar (irisan 1):**

| Service | `kind` | Catatan |
|---|---|---|
| [[Microservices - Attendance Service]] | `holiday` | Hari libur perusahaan, seharian, lingkup `company` |
| [[Microservices - Attendance Service]] | `leave` | Cuti/izin/sakit **berstatus disetujui saja**. Izin berjam tidak dijadikan seharian |
| [[Microservices - Attendance Service]] | `shift` | Jadwal kerja pemanggil sendiri, lewat resolver yang sama dengan halaman Jadwal |
| [[Microservices - Employee Service]] | `contract_end` | Kontrak berakhir. PKWTT dibuang karena `end_date`-nya kosong |

## Belum Diimplementasikan / Catatan

- **Irisan 2 (belum ada kode)**: koleksi `calendar_events` untuk event mandiri beserta peserta, plus feed berikutnya. Urutan yang disepakati: **Perjalanan Dinas** (`business_trip_request` di [[Microservices - Attendance Service]]) dan **pelatihan** ([[Microservices - Learning Service]]) lebih dulu karena keduanya paling murah dan paling cepat terasa, lalu **jadwal interview** ([[Microservices - Recruitment Service]]), lalu due date [[Microservices - Task Management Service]] dan periode form berulang [[Microservices - Form Builder Service]].
- **Ulang tahun karyawan sengaja TIDAK masuk kalender** (keputusan pemilik produk, 2026-08-06). Endpointnya ada dan murah, tapi itu bukan alasan memasukkannya kembali. Ia tetap tampil di widget Agenda Mendatang pada dashboard HRIS.
- **Tukar Shift yang disetujui TIDAK dibuat feed sendiri**: hasilnya sudah tercermin di feed `shift`, karena resolver yang dipanggil sudah menerapkannya. Menambahkannya membuat satu hari tampil dua kali.
- **Irisan 3 (belum ada kode)**: mesin kewajiban berulang (one-on-one bulanan, pelatihan wajib) beserta papan kepatuhan. Polanya menyalin `FormPeriod` di [[Microservices - Form Builder Service]] yang sudah terbukti di produksi. Sejak 2026-08-06 irisan ini **termasuk terima/tolak peserta**: yang wajib memilih sendiri lawan sesinya dari kandidat yang lolos aturan per-template, dan agenda baru jadi pasti setelah pihak itu menyetujui. Ajakan yang belum dijawab tetap tampil di kedua kalender dengan tampilan berbeda, karena menyembunyikannya membuat pengusul kehilangan jejak dan tenggat lewat tanpa disadari. Persetujuan **tidak** langsung memenuhi kewajiban; pertemuannya tetap harus ditandai selesai, supaya angka kepatuhan mengukur kenyataan, bukan niat.
- **Belum ada**: booking ruang meeting, pengingat lewat [[Microservices - Notification Service]], kalender di [[APP - MyBharata]].
- **Hasil verifikasi di DEV (2026-08-06)**, lewat gateway dengan akun nyata: hari libur muncul dengan `all_day` dan lingkup `company`; **79 dari 79 shift cocok jam-per-jam dengan halaman Jadwal, 0 berbeda, 0 hari kerja hilang** (risiko ADR 0036 tertutup, karena feed memanggil resolver yang sama); cuti muncul lengkap dengan subtipe dan membedakan izin berjam dari seharian; `degraded` selalu kosong. Gerbang teruji **dua arah**: karyawan biasa hanya melihat miliknya sendiri, supervisor melihat cuti anak buahnya, supervisor departemen lain tidak melihatnya.
- **GOTCHA yang menggigit saat rilis**: gateway MEMBUANG prefix `/api/<module>` (`routes.Reroute` memanggil `strings.TrimPrefix`), jadi `/api/calendar` tiba di service sebagai `/`. Rute agregat sempat didaftarkan di `/calendar` sehingga seluruh permintaan lewat jalur normal membalas 404 `Cannot GET /`, padahal 33 test hijau karena semuanya memanggil path lokal langsung ke Fiber. Diperbaiki di #1041 beserta test yang mereproduksi pemotongan prefix itu. **Berlaku untuk service mana pun**: rute akar modul didaftarkan di `/`, bukan `/<module>`.
- **Batas rentang shift melebar ke satu hari WIB penuh**, sehingga `to=2026-09-30T23:59:59Z` ikut memunculkan shift 1 Oktober. Tidak berbahaya untuk frontend (grid-nya memang mencakup hari luapan), tapi secara kontrak memasukkan item di luar rentang yang diminta. Belum dirapikan.
- **Widget Agenda Mendatang** di dashboard HRIS masih menggabungkan hari libur dan ulang tahun sendiri. Setelah `/api/calendar` hidup, widget itu sebaiknya diarahkan ke sana supaya normalisasinya satu, bukan dua.

## Dependensi & Integrasi

- [[CORE - API Master Gateway]] — rute `/api/calendar/*`, identitas pemanggil, dan `noCacheRoutes`.
- [[Microservices - Attendance Service]] · [[Microservices - Employee Service]] — penyedia feed irisan 1. **Keduanya opsional**: URL kosong berarti feed-nya dilewati.
- [[CORE - RBAC dan Permission Set]] — penyaringan tetap milik service sumber; kalender tidak menambah lapis izin sendiri.

## Dokumen Terkait

- [[APP - Web ERP]] — halaman `/calendar`.
- [[GA - Asset Loan & Room Booking]] — rencana booking ruang yang harus masuk sebagai feed, bukan kalender kedua.
- [[Microservices - Form Builder Service]] — asal pola periode dan papan kepatuhan untuk irisan 3.
