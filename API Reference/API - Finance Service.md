## Deskripsi

*Endpoint **finance-service** (master data divisi FAT: Cost Control, Tax, Biaya Variabel Produksi, dan Audit Internal). Gateway: `/api/finance/*`. Grounded ke `services/finance/routes.go`, `pajak_handler.go`, `biaya_variabel_handler.go`, `audit_handler.go`.*

- **Implementasi**: [[Finance - Rancangan Finance Service]] · **Status**: ⚠️ Implemented (ada catatan), Fase 0 + Cost Control Fase 1a + **modul Tax (kewajiban per masa) ada di kode**, tetapi datanya di prod masih kosong (master jenis pajak 0, kewajiban 0; seed master belum pernah dijalankan) + Biaya Variabel Produksi + Audit Internal ([[Finance - Audit Internal]]); register pelaporan SPT/temuan/klasifikasi akun masih deklarasi koleksi tanpa pemanggil (diukur 2026-09-12)
- **Indeks**: [[API - Index]] · **RBAC**: gerbang kunci gateway di seluruh rute (`ValidateGateway`), plus izin per-modul (`finance.pajak.*`, `audit.*`) dan pemeriksaan identitas per-handler pada rute `/internal/` (lihat catatan di bawah). ⚠️ **Rute `/biaya-variabel*` TIDAK bergerbang izin maupun `company_id` sama sekali**, lihat bagian Biaya Variabel Produksi.

> ⚠️ **Rute ditulis TANPA mengulang nama modul.** Gateway membuang prefix `/api/finance` sebelum meneruskan (`routes.Reroute` → `strings.TrimPrefix`), jadi `/api/finance/cost-control/rekomendasi` tiba di service sebagai `/cost-control/rekomendasi`. Mendaftarkannya sebagai `/finance/cost-control/...` membuat SELURUH permintaan lewat jalur normal membalas 404 sementara unit test tetap hijau. Dikunci `routes_test.go` dan `rekomendasi_handler_test.go`.

## Identitas & Health

| Method | Path | Fungsi |
|---|---|---|
| GET | `/` | Identitas service (`{"service":"finance","modul":["pajak","cost-control"]}`). Ada sejak Fase 0 justru untuk membuktikan kontrak pemotongan prefix di atas benar-benar dipenuhi |
| GET | `/health` | Healthcheck container. Didaftarkan **SEBELUM** gerbang gateway — healthcheck memasang kuncinya sendiri, dan menaruhnya di belakang gerbang membuat container tak pernah dinyatakan sehat |

## Cost Control — Rekomendasi Efisiensi

Memasok metrik KPI Cost Control **"minimal 3 rekomendasi efisiensi cost driver setiap bulan"** (bobot 20%). Yang dinilai adalah **cacahnya**, bukan besaran penghematannya.

| Method | Path | Fungsi |
|---|---|---|
| POST | `/cost-control/rekomendasi` | Catat satu rekomendasi. Body: `periode` (opsional, kosong = bulan berjalan), `isi` (wajib), `akun_no`/`akun_nama`/`taksiran_hemat` (opsional). ⚠️ **`employee_id` TIDAK diterima dari body** — pemiliknya diambil dari identitas pemanggil, sebab metrik ini menghitung capaian per orang dan menerima pemilik dari body berarti siapa pun dapat menulis capaian atas nama orang lain |
| GET | `/cost-control/rekomendasi?periode=YYYY-MM&employee_id=` | Daftar satu periode. `periode` **wajib** dan bentuk di luar `YYYY-MM` ditolak 400, bukan ditebak: `2026-8` ambigu dan `08-2026` terbalik. Balasannya selalu array — tak pernah `null` |
| DELETE | `/cost-control/rekomendasi/:id` | Hapus milik sendiri. Pemilik ikut jadi filter, bukan hanya id, sebab gateway tidak memeriksa kepemilikan baris. "Tidak ada" dan "bukan milikmu" **sengaja tak dibedakan** — membedakannya memberi tahu penanya bahwa sebuah id memang ada |
| GET | `/internal/kpi/cost-control?periode=YYYY-MM&employee_id=` | Agregat untuk sumber KPI `kinerja_cost_control` di [[Microservices - Employee Service]]. Membalas `{"rekomendasi_efisiensi": n}` |

### Penjaga rute `/internal/` — bentuknya TIDAK seperti feed kalender

Prefix `/internal/` **bukan** batas keamanan: gateway tetap meneruskannya dari internet ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Tetapi penjaganya di sini **tidak bisa** sekadar "wajib ada identitas" seperti feed kalender, karena pemanggil sahnya justru sumber KPI di employee-service yang memakai `routes.InternalRequest(nil, …)` — panggilan itu hanya membawa kunci gateway, **tanpa header identitas sama sekali**. Menuntut identitas akan memblokir pemanggil yang benar sambil tetap meloloskan orang lewat gateway.

Karena gateway **membuang seluruh header `BIP-*` kiriman klien lalu mengisinya ulang dari klaim JWT**, ada-tidaknya identitas justru membedakan kedua pemanggil itu dengan andal:

| Identitas pemanggil | Artinya | Perlakuan |
|---|---|---|
| **ADA** | orang lewat gateway | dikunci ke dirinya sendiri; `employee_id` di query **diabaikan** |
| **TIADA** | service pemegang kunci gateway | `employee_id` di query **dihormati** |

Dikunci `TestEmployeeIDEfektifMenguncKeIdentitasPemanggil` dengan keempat kombinasinya.

## Pajak (Tax): Kewajiban per Masa

Mengisi metrik KPI Tax Officer: pelaporan tepat waktu (bobot 65) dan arsip lengkap (bobot 35, BPE + bukti bayar). Kewajiban **dibangkitkan sistem** dari master jenis pajak per masa, bukan dibuat manual, lihat [[Finance - Rancangan Finance Service]] §Alur Modul Tax. FE: `/finance/pajak`.

| Method | Path | Izin | Fungsi |
|---|---|---|---|
| GET | `/pajak/ringkasan?periode=YYYY-MM` | `finance.pajak.view` | Daftar kewajiban satu periode + cuplikan KPI + `masa_terakhir_terbit` (menjawab apakah cron penerbitan masih hidup) |
| GET | `/pajak/master` | `finance.pajak.view` | Daftar jenis kewajiban (master) |
| POST | `/pajak/master/seed` | `finance.pajak.tenggat` | Menyemai jenis bawaan (idempoten via index unique `company_id`+`kode`) untuk `company_id` pemanggil |
| PATCH | `/pajak/master/:id` | `finance.pajak.tenggat` | Mengubah master; TIDAK menyentuh kewajiban yang sudah lahir |
| POST | `/pajak/terbitkan` | `finance.pajak.tenggat` | Pemicu manual penerbitan masa berjalan (memulihkan cron yang terlewat; fungsi yang SAMA dengan cron) |
| GET | `/pajak/:id` | `finance.pajak.view` | Detail satu kewajiban |
| PATCH | `/pajak/:id` | `finance.pajak.kelola` | Mengisi nilai/tanggal lapor/nomor BPE/taut pengajuan dana (PATCH sebagian); status diturunkan dari kelengkapan, tidak bisa dikirim klien |
| PATCH | `/pajak/:id/tenggat` | `finance.pajak.tenggat` | Menggeser tenggat (menulis `tenggat_override`, alasan wajib); ditolak bila kewajiban sudah berstatus `dilaporkan` |
| POST | `/pajak/:id/bukti/:jenis` | `finance.pajak.kelola` | Unggah bukti (`bpe` atau `bayar`, maks 4 MB, PDF/JPG/PNG) ke file-service |
| GET | `/internal/kpi/tax?periode=&company_id=` | *(tanpa izin, identitas menentukan cakupan)* | Cuplikan KPI Tax Officer untuk sumber `kinerja_tax` di [[Microservices - Employee Service]] |
| GET | `/internal/calendar-feed?from=&to=` | *(wajib identitas; RFC3339, rentang maks 400 hari)* | Feed `tax_due` untuk [[Microservices - Calendar Service]], lihat catatan cakupan di bawah |

(`services/finance/routes.go:86-109`, `pajak_handler.go`, `pajak_arsip.go`, `pajak_master_seed.go`)

### Tiga izin, sengaja bukan satu gerbang "kelola"

`finance.pajak.tenggat` **dipisah** dari `finance.pajak.kelola`: tenggat adalah instrumen penilaian KPI, dan menyatukannya membuat yang dinilai bisa menggeser sendiri batas yang menilainya (`shared-library/common/catalog_finance.go:36-41`). Tier `supervisor` memegang ketiganya (view, kelola, tenggat); tier `staff` finance **tidak memegang satu pun** izin pajak (`catalog_finance.go:69-85`). Paket siap-pakai `finance_pajak` = view+kelola **tanpa** tenggat (`catalog_finance.go:140-149`), dirancang untuk Tax Officer, orang yang dinilai oleh tenggat itu sendiri; menggeser tenggat tetap kewenangan SPV FAT (tier supervisor). Diukur prod 2026-09-12: posisi Tax Staff belum memegang paket itu maupun tier finance apa pun, lihat [[Finance - FAT Persona]].

### Status TERSIMPAN hanya tiga, bukan empat

`pajak_kewajiban.go:14-24`: status yang tersimpan cuma `terjadwal` / `disiapkan` / `dilaporkan`. `terlambat` dan `dilaporkan_terlambat` adalah status TURUNAN (`StatusTampil`), dihitung ulang tiap kali dibaca, tidak pernah ditulis ke Mongo, sehingga cron yang mati tidak lagi berarti status yang basi. Lihat catatan gap dengan rancangan awal (status "Disetor") di [[Finance - Rancangan Finance Service]].

### Master bawaan: enam jenis

`MasterBawaan` (`pajak_master_seed.go:24-60`) menyemai PPN Masa, PPh 21, PPh 23, PPh 25, PPh 4 ayat 2, **dan PPh Badan tahunan** (`PPH_BADAN`, tenggat tanggal 30 + offset 4 bulan, masa direpresentasikan bulan terakhir tahunnya). Angka tenggatnya data yang dapat diubah SPV FAT lewat `PATCH /pajak/master/:id`, bukan konstanta kode: bila salah, yang membetulkan adalah orang yang tahu aturannya, tanpa menunggu rilis.

### Penjadwal: dua ritme berbeda

- **Penerbitan masa**: tik tiap 10 menit, menerbitkan hanya pada jendela tanggal 1 pukul 00:30 WIB (`pajak_jadwal.go:9-46`). Idempoten lewat index unique, bukan ketepatan jam.
- **Pengingat H-7/H-3**: diperiksa tiap tik, terkirim sekali per hari pada jendela jam 08:00 WIB (`pajak_jadwal.go:92-130`, dipanggil dari `main.go`), ke seluruh pemegang `finance.pajak.kelola` di perusahaan yang sama lewat `GET /internal/permission-holders` di employee-service (`pajak_notify.go:284`). ⚠️ Tanpa pemegang izin, kewajiban yang jatuh tempo hanya di-log, **tidak ada yang diberi tahu** (`pajak_notify.go:287-294`). ⚠️ Kategori inbox `tax-due-warning` membawa `deep_link` (`rutePajakDiAplikasi = "/finance/pajak"`), tetapi **belum ada konsumen yang menavigasi darinya**: `notification_route_mapper.dart` MyBharata belum punya aturan untuk kategori ini (`pajak_notify.go:46-57`).

### Feed kalender: terdaftar, belum tentu tersambung

`GET /internal/calendar-feed` sudah ada dan hanya mensyaratkan identitas pemanggil, bukan izin (`pajak_calendar_feed.go:157-163`), sejalan dengan prinsip "agenda perusahaan" [[Microservices - Calendar Service]]. **TBD**: blok `calendar-service` di `docker-compose.yml` (baris ~1590-1617) belum memuat `FINANCE_MODULE_URL` di antara provider feed-nya (baru `ATTENDANCE_MODULE_URL`, `EMPLOYEE_MODULE_URL`, `TASK_MANAGEMENT_MODULE_URL`, `FORM_BUILDER_MODULE_URL`), jadi feed `tax_due` kemungkinan **belum ditarik** calendar-service, bahkan di dev. `services/calendar/providers.go` tidak dapat diperiksa dari snapshot ini untuk memastikan; verifikasi ulang sebelum mengklaim live.

## Biaya Variabel Produksi

Bahan KPI SPV Manufacture F3 "Kontrol ketat biaya produksi variabel" (bobot 10), dicatat di sisi Finance atas permintaan HR. Yang dinilai perbandingan dengan bulan yang SAMA tahun lalu, bukan bulan sebelumnya (produksi bermusim). FE: `/finance/biaya-variabel`.

| Method | Path | Fungsi |
|---|---|---|
| POST | `/biaya-variabel` | Catat satu baris (`periode`, `kategori` wajib; `kode_produk` opsional, tempat penempelan ke produksi, belum dikerjakan di FE) |
| GET | `/biaya-variabel?periode=YYYY-MM` | Daftar + total + cacah satu periode |
| DELETE | `/biaya-variabel/:id` | Hapus milik pencatat sendiri |
| GET | `/biaya-variabel/komparasi?periode=` | Total periode berjalan berdampingan bulan yang sama tahun lalu (dua angka mentah, bukan rasio) |
| GET | `/internal/kpi/biaya-variabel?periode=` | Alias, HANDLER YANG SAMA dengan `/biaya-variabel/komparasi` di atas; dibaca sumber KPI `biaya_variabel_produksi` di employee-service (`services/employee/kpi_sumber_biaya_variabel.go:19`) |

(`services/finance/routes.go:61-69`, `biaya_variabel_handler.go`, `biaya_variabel.go`)

⛔ **Catatan keamanan (netral, belum diperbaiki)**: berbeda dari Cost Control dan Pajak di atas, **tak satu pun rute modul ini memanggil `common.HasPermission`**, nol gerbang izin (diverifikasi seluruh `biaya_variabel_handler.go`). `GET /biaya-variabel` dan `GET /internal/kpi/biaya-variabel` juga **tidak menyaring `company_id`**: struct `BiayaVariabelProduksi` (`biaya_variabel.go:34-53`) tidak punya field itu sama sekali, sehingga keduanya membalas data seluruh tenant yang mengisi periode yang sama. `POST`/`DELETE` tetap menuntut identitas pemanggil (bukan izin) untuk menentukan `dicatat_oleh`.

## Audit Internal

Modul terpisah, di-host di service ini (ADR 0073, diamandemen 2026-09-02); lihat [[Finance - Audit Internal]] untuk domain lengkap (36 uji, tiga kelompok, semantik kolom, aturan layar). Tabel di bawah hanya memetakan rute; **jangan salin logika audit ke sini**.

| Method | Path | Izin | Fungsi |
|---|---|---|---|
| GET | `/audit/uji` | `audit.view` | Daftar definisi uji |
| GET | `/audit/temuan` | `audit.view` | Daftar temuan |
| GET | `/audit/jejak?periode=&kunci=` | `audit.view` | Jejak perubahan (belum tercatat di dok API sebelumnya) |
| GET | `/audit/setelan-sampel` | `audit.view` | Setelan sampling |
| PUT | `/audit/setelan-sampel/:kode` | `audit.master.save`* | Ubah setelan sampling |
| GET | `/audit/bukti/:id/berkas` | `audit.view` | Unduh berkas bukti |
| DELETE | `/audit/bukti/:id` | `audit.tinjau`* | Hapus bukti |
| GET | `/audit/periode/:periode` | `audit.view` | Kertas kerja satu periode |
| POST | `/audit/periode/:periode/tarik` | `audit.tinjau`* | Tarik ulang periode |
| PATCH | `/audit/periode/:periode/baris/:kode/tinjau` | `audit.tinjau`* | Tinjau satu baris |
| POST | `/audit/periode/:periode/baris/:kode/temuan` | `audit.temuan.terbitkan`* | Terbitkan temuan dari baris |
| GET | `/audit/periode/:periode/baris/:kode/bukti` | `audit.view` | Daftar bukti baris (sengaja `view`, bukan `tinjau`: melihat bukti bagian dari membaca laporan) |
| POST | `/audit/periode/:periode/baris/:kode/bukti` | `audit.tinjau`* | Unggah bukti baris |

*Nama konstanta persis: `common.PermAuditView`, `common.PermAuditMasterSave`, `common.PermAuditTinjau`, `common.PermAuditTemuanTerbitkan` (`audit_handler.go:331-355`). Izin ber-prefiks `audit`, BUKAN `finance`: pemegang izin finance tidak otomatis membuka kertas kerja yang memeriksa pekerjaannya sendiri.

⚠️ **Status kertas kerja `terbit` (`KertasKerjaTerbit`, `audit_kertas_kerja.go:26`) dideklarasikan dan DIBACA (`:289`) tapi tak punya rute penulis.** Diverifikasi: `git grep` atas `KertasKerjaTerbit`/`TerbitPada`/`TerbitOleh` di seluruh `services/finance` hanya mengembalikan deklarasi struct + satu titik baca, nol penulis.

Penjadwal audit membuka periode (bulan sebelumnya, tutup buku) tiap tanggal 6 pukul 01:00 WIB (`audit_kertas_kerja.go:133-165`), sengaja terpisah dari penjadwal pajak (tanggal 1): jendelanya berbeda, dan menyatukan dua fakta yang kebetulan berbentuk sama akan mengunci keduanya bergerak bersama.

## Catatan Kontrak

- **`rekomendasi_efisiensi` adalah kontrak lintas modul Go.** finance-service dan employee-service berada di modul berbeda sehingga kompilator tidak menghubungkan keduanya: mengganti nama field itu membuat pembacanya diam-diam terisi nol, metrik melaporkan "0 rekomendasi", dan tak satu pun galat muncul. Dikunci dari sisi pembaca oleh `TestKontrakJSONAgregatCostControl`; bila test itu merah, **kedua service wajib naik bersama**.
- **Periode memakai zona `Asia/Jakarta`, bukan UTC.** Rekomendasi yang dibuat 1 Agustus 00:30 WIB masih 31 Juli di UTC; mengambilnya dari UTC membuat cacah bulan berjalan kurang satu tanpa satu pun galat, dan metrik ini dinilai per bulan dengan target 3 sehingga selisih satu langsung mengubah skor orang. Frontend memakai patokan yang sama.
- **Nol rekomendasi adalah NILAI, bukan galat.** Bulan yang belum diisi memang bernilai nol; menggagalkannya membuat metrik hilang dari layar KPI sehingga penilai menyangka sistemnya rusak padahal orangnya yang belum mencatat.
- **Target metrik TIDAK ada di service ini.** Ia dimiliki `kpi_template` di employee-service ([[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]) dan dapat berbeda per posisi, per periode, maupun per karyawan. Menaruhnya di sini akan melahirkan sumber kebenaran kedua yang menyimpang diam-diam.

## Belum Ada

- **Register pelaporan SPT, register temuan kepatuhan, klasifikasi akun deductible**: koleksi `pajak_spt`, `pajak_temuan`, `pajak_klasifikasi_akun` sudah dinamai (`db.go:22-28`) tapi **tak ada pemanggil sama sekali**. Satu masa punya tepat satu pelaporan, jadi tanggal lapor/BPE/bukti untuk sementara tinggal di dokumen kewajibannya sendiri. Lihat [[Finance - Rancangan Finance Service]].
- **Jembatan KPI terpadu `GET /internal/kpi/metrics` + sumber `kinerja_finance`**: rancangan awal, **TIDAK ada di kode**. Yang benar-benar berjalan hari ini adalah endpoint TERPISAH per sumber: `/internal/kpi/cost-control` (dibaca sumber `kinerja_cost_control`), `/internal/kpi/tax` (`kinerja_tax`), `/internal/kpi/biaya-variabel` (`biaya_variabel_produksi`); tiga berkas `kpi_sumber_*.go` berbeda di employee-service, bukan satu fasad.
- **Forecast kas mingguan** (Fase 1b, metrik bobot 15%) — koleksi `cost_forecast_kas` sudah dinamai sejak Fase 0, rutenya belum ada.
- **Master anggaran OPEX** — sengaja **tidak** dimigrasi ke sini; ia tetap milik [[Microservices - Integration Service]] karena hidupnya dari katalog akun dan realisasi Accurate.

## Dokumen Terkait

- [[Finance - Rancangan Finance Service]] — rancangan & status modul
- [[Finance - Audit Internal]]: domain lengkap modul Audit Internal (36 uji, semantik kolom)
- [[Finance - FAT Persona]]: persona per posisi FAT (Tax Officer, Cost Control, SPV FAT), grounded ke izin dan paket prod
- [[Microservices - Employee Service]] — pemilik `kpi_template`; tempat sumber `kinerja_cost_control`, `kinerja_tax`, `biaya_variabel_produksi` terdaftar
- [[Microservices - Integration Service]] — pemilik `anggaran_opex` & varians
- [[Microservices - Calendar Service]]: konsumen feed `tax_due`
- [[CORE - API Master Gateway]] — pemotongan prefix `/api/<module>`
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] · [[ADR - 0073 Modul Audit Internal di finance-service dan Kertas Kerja yang Dipegang Sendiri]]
- [[RUN - Menambah Metrik KPI Otomatis]] · [[API - Index]]
