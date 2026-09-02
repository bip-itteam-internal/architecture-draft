## Deskripsi

*Endpoint **finance-service** (master data divisi FAT: Cost Control, dan menyusul Tax). Gateway: `/api/finance/*`. Grounded ke `services/finance/routes.go` dan `rekomendasi_handler.go`.*

- **Implementasi**: [[Finance - Rancangan Finance Service]] · **Status**: ⚠️ Implemented (Fase 0 + Cost Control Fase 1a; modul Tax belum ada)
- **Indeks**: [[API - Index]] · **RBAC**: gerbang kunci gateway di seluruh rute (`ValidateGateway`), plus pemeriksaan identitas per-handler pada rute `/internal/` — lihat catatan di bawah.

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

## Catatan Kontrak

- **`rekomendasi_efisiensi` adalah kontrak lintas modul Go.** finance-service dan employee-service berada di modul berbeda sehingga kompilator tidak menghubungkan keduanya: mengganti nama field itu membuat pembacanya diam-diam terisi nol, metrik melaporkan "0 rekomendasi", dan tak satu pun galat muncul. Dikunci dari sisi pembaca oleh `TestKontrakJSONAgregatCostControl`; bila test itu merah, **kedua service wajib naik bersama**.
- **Periode memakai zona `Asia/Jakarta`, bukan UTC.** Rekomendasi yang dibuat 1 Agustus 00:30 WIB masih 31 Juli di UTC; mengambilnya dari UTC membuat cacah bulan berjalan kurang satu tanpa satu pun galat, dan metrik ini dinilai per bulan dengan target 3 sehingga selisih satu langsung mengubah skor orang. Frontend memakai patokan yang sama.
- **Nol rekomendasi adalah NILAI, bukan galat.** Bulan yang belum diisi memang bernilai nol; menggagalkannya membuat metrik hilang dari layar KPI sehingga penilai menyangka sistemnya rusak padahal orangnya yang belum mencatat.
- **Target metrik TIDAK ada di service ini.** Ia dimiliki `kpi_template` di employee-service ([[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]) dan dapat berbeda per posisi, per periode, maupun per karyawan. Menaruhnya di sini akan melahirkan sumber kebenaran kedua yang menyimpang diam-diam.

## Belum Ada

- **Modul Tax** — menunggu keputusan pemilik metrik; lihat [[Finance - Rancangan Finance Service]].
- ~~**Forecast kas mingguan** (Fase 1b, metrik bobot 15%) — koleksi `cost_forecast_kas` sudah dinamai sejak Fase 0, rutenya belum ada.~~ **Koreksi 2026-09-02: baris ini sudah usang dan menyesatkan.** Fase 1b memang dibangun (14 Agustus 2026), tetapi **bukan di service ini dan bukan sebagai modul forecast** — ia menjadi pemecahan mingguan atas laporan anggaran vs realisasi yang sudah hidup di [[Microservices - Integration Service]] (`GET /accounting/anggaran/mingguan` dan `/mingguan/kpi`), memasok sumber KPI `forecast_kas` di [[Microservices - Employee Service]]. Koleksi `cost_forecast_kas` **tidak jadi dipakai**, dan finance-service tidak disentuh sama sekali. Membiarkan baris ini di daftar "Belum Ada" membuat pembaca mencari rute yang memang tidak akan pernah ada di sini, lalu menyimpulkan metrik berbobot besar belum tergarap padahal ia satu-satunya metrik Cost Control yang rantainya sudah utuh. Alasan rancangannya di [[Finance - Rancangan Finance Service]], bab "Modul Cost Control Fase 1b". Bobot metriknya sendiri kini **35**, bukan 15 — lihat bab "Sheet KPI revisi September 2026" di berkas yang sama.
- **Master anggaran OPEX** — sengaja **tidak** dimigrasi ke sini; ia tetap milik [[Microservices - Integration Service]] karena hidupnya dari katalog akun dan realisasi Accurate.

## Dokumen Terkait

- [[Finance - Rancangan Finance Service]] — rancangan & status modul
- [[Microservices - Employee Service]] — pemilik `kpi_template`, tempat sumber `kinerja_cost_control` terdaftar
- [[Microservices - Integration Service]] — pemilik `anggaran_opex` & varians
- [[CORE - API Master Gateway]] — pemotongan prefix `/api/<module>`
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]
- [[RUN - Menambah Metrik KPI Otomatis]] · [[API - Index]]
