## Deskripsi

*Service pembaca status infrastruktur. Ia TIDAK memantau apa pun sendiri: seluruh datanya berasal dari `kuma.db` milik [Uptime Kuma](https://github.com/louislam/uptime-kuma) yang berjalan native (pm2) di host produksi, dibuka read-only. Perannya menerjemahkan basis data itu menjadi endpoint yang dapat dipakai dashboard IT di web ERP dan, sejak Agustus 2026, menjadi sumber metrik KPI otomatis.*

- **Stack**: Go + Fiber v2, SQLite read-only via `modernc.org/sqlite` (driver murni Go, tanpa cgo)
- **Path di repo**: `bip-erp/services/monitoring/`
- **Port**: `6984` (`MONITORING_SERVICE_PORT`)
- **Status**: ⚠️ Implemented (ada catatan) — jalan di produksi. Endpoint periode (`/uptime`, `/kpi/uptime`) merge lewat PR #866 dan **sudah deploy ke produksi 1 Agustus 2026**, terverifikasi terhadap `kuma.db` sungguhan.

### Kenapa hanya jalan di produksi

`kuma.db` di-mount dari `/home/bharata/apps/uptime-kuma/data` pada VPS Biznet. Uptime Kuma tidak berjalan sebagai container, sehingga path itu hanya ada di host produksi. Di server dev, `/health` melaporkan `kuma.db` tidak terbaca dan seluruh endpoint membalas 503 — **itu perilaku yang benar**, bukan kerusakan. Kegagalan membuka basis data sengaja TIDAK mematikan service saat boot, supaya penyebabnya terbaca lewat `/health` alih-alih hilang di dalam restart-loop container.

## Endpoint (Sudah Diimplementasikan)

Gateway memanggil lewat `/api/monitoring/*` dan **melucuti** prefix itu, sehingga service menerima path tanpa nama modul.

### Dashboard (gerbang `monitoring.view`)

| Endpoint | Keterangan |
|---|---|
| `GET /monitors` | Daftar monitor aktif + uptime 24 jam / 7 hari / 30 hari, beserta `data_since` |
| `GET /monitors/:id/heartbeats?hours=24` | Riwayat cek satu monitor (1 sampai 168 jam) |
| `GET /incidents?limit=50` | Gangguan terakhir |
| `GET /summary` | Ringkasan status seluruh monitor |
| `GET /uptime?periode=YYYY-MM` | **Baru.** Uptime satu periode kalender, lengkap dengan rincian per monitor |

### Ekspor (gerbang `monitoring.export`)

| Endpoint | Keterangan |
|---|---|
| `GET /export/monitors.csv` | Ekspor daftar monitor |
| `GET /export/incidents.csv` | Ekspor daftar gangguan |

### Pengumpul KPI (gerbang kunci layanan)

| Endpoint | Keterangan |
|---|---|
| `GET /kpi/uptime?periode=YYYY-MM&key=...` | **Baru.** Uptime agregat satu periode, tanpa daftar monitor |

`GET /health` didaftarkan **sebelum** gerbang gateway supaya healthcheck Docker dapat memanggilnya dari dalam container. Ia melaporkan sehat HANYA bila `kuma.db` benar-benar terbaca; melaporkan "ok" saat sumber data tak terjangkau membuat dashboard tampak kosong tanpa sebab dan Autoheal tidak bertindak.

## Uptime per periode kalender

Endpoint `/monitors` menyajikan **jendela berjalan** (24 jam, 7 hari, 30 hari). Penilaian KPI memakai **periode kalender**, dan keduanya tidak saling menggantikan: "30 hari terakhir" yang diminta pada 5 Agustus memuat sebagian Juli, dan itu bukan nilai bulan mana pun.

Empat keputusan yang menentukan angkanya:

- **Batas periode dihitung di WIB, lalu dikonversi ke UTC.** `heartbeat.time` menyimpan UTC sebagai TEKS dan dibandingkan leksikografis oleh SQLite. Selisih tujuh jam memindahkan heartbeat 1 Agustus dini hari WIB ke bulan Juli. Ujung periode bersifat eksklusif (1 Agustus 00:00, bukan 31 Juli 23:59).
- **Rata-rata TERTIMBANG jumlah heartbeat**, bukan rata-rata dari rata-rata. Monitor yang baru dipasang pertengahan bulan punya jauh lebih sedikit cek; menyamakan bobotnya membuat satu monitor baru menjatuhkan angka seluruh tim. Monitor tanpa heartbeat tetap ditampilkan tetapi tidak ikut menimbang.
- **`uptime` bertipe nullable.** Bulan tanpa heartbeat membalas `null`, bukan `0`. Nol persen terbaca sebagai seluruh sistem mati sebulan penuh, tuduhan yang jauh lebih berat daripada "datanya memang belum ada".
- **Cakupan hari ikut dilaporkan** (`hari_diminta`, `hari_berdata`, `cakupan_persen`). Heartbeat produksi baru ada sejak **9 Juli 2026**, sehingga uptime Juli berdiri di atas 23 dari 31 hari. Angkanya tetap dapat dihitung, tetapi menyajikannya tanpa keterangan membuat pembaca mengira itu sebulan penuh.

Status 2 (pending) dikecualikan dari pembilang DAN penyebut, mengikuti perlakuan Kuma sendiri.

### Cache

Dipisah menurut apakah periodenya sudah tutup:

| Keadaan | Umur | Alasan |
|---|---|---|
| Periode berjalan | 20 detik | KPI dilihat langsung; angkanya masih bergerak |
| Periode tutup | 12 jam | Jawabannya tak mungkin berubah lagi |

Query ini memindai heartbeat sebulan penuh (produksi 1,24 juta baris, bertambah sekitar 57 ribu per hari), jadi menghitung ulang periode lampau tiap 20 detik hanya membakar CPU untuk jawaban yang sama persis. Jumlah entri dibatasi 36 (tiga tahun penilaian): tanpa batas, `YYYY-MM` yang sah membentang sampai tahun 9999 dan satu perulangan permintaan bisa membuat container kehabisan memori.

#### Single-flight dan penyajian entri basi (2026-08-30)

⛔ **Cache yang cuma "cek lalu hitung" TIDAK cukup, dan kegagalannya muncul sebagai skor KPI yang salah, bukan sebagai halaman lambat.** Sampai 30 Agustus 2026, tiap pemanggil yang menemukan entri kedaluwarsa menjalankan querynya sendiri. Karena TTL periode berjalan cuma 20 detik sementara querynya makan sekitar 3,5 detik saat cache dingin, permintaan yang datang bersamaan saling memperlambat sampai menembus batas waktu.

Terukur di produksi hari itu: **40 dari 104 permintaan `GET /kpi/uptime` berakhir `504`**, dan 504-nya **selalu datang berpasangan** — satu untuk karyawan yang metriknya memakai uptime, satu lagi untuk rantai `skor_tim` atasannya. Berpasangan itulah petunjuk yang membedakannya dari "monitoring lambat": probe satu per satu selalu membalas 70 sampai 90 ms dan tampak sehat sepenuhnya.

Yang dipasang (bip-erp PR [#1534](https://github.com/bip-itteam-internal/bip-erp/pull/1534)):

| Mekanisme | Perilaku |
|---|---|
| **Single-flight** per periode | Penyegaran kedua ikut menunggu hasil yang pertama, tidak menambah beban ke query yang sedang berjalan |
| **Entri basi tetap disajikan** | Bila penyegaran gagal, hasil lama dipakai alih-alih membalas 504 |
| **Batas umur basi 24 jam** | Lewat itu, gagal jujur — tanpa batas ini monitoring yang mati berhari-hari akan menyamar jadi angka yang masih berlaku |
| **Kegagalan tidak menimpa entri lama** | Entri itulah yang menyelamatkan permintaan berikutnya |

Batas waktu query periode juga **dipisah** dari batas dashboard: `batasWaktuQueryPeriode` 9 detik vs `batasWaktuQuery` 5 detik. Angkanya sengaja di **bawah** timeout klien employee-service (10 detik, `kpi_sumber_uptime.go`); rantai timeout yang terbalik membuat pelonggaran di sini tampak tidak bekerja sama sekali.

⚠️ **Yang belum ditangani**: kegagalan tidak di-cache, jadi saat monitoring benar-benar sakit setiap permintaan tetap memicu satu query berat (kini beruntun, bukan paralel). Dan `ctx` pemanggil pertama menentukan nasib seluruh penunggu — bila klien pertama memutus koneksi, querynya batal dan penunggu lain ikut gagal, tertolong penyajian entri basi bila ada.

Dampak hilirnya ada di [[HRIS - Otomasi Skor KPI]] bab **Sumber yang gagal bukan data yang belum ada**.

## Gerbang dan RBAC

Dua gerbang berbeda, karena pemanggilnya berbeda jenis.

**Dashboard dan ekspor** memakai izin RBAC (`monitoring.view`, `monitoring.export`) dengan fallback peran tier lama (`isITStaff`, `isITSupervisor`) sebagai kill-switch lewat `MONITORING_PERMISSION_ENFORCEMENT=off`. Fallback ekspor sengaja memakai `isITSupervisor`, bukan `isITStaff`: kill-switch harus mengembalikan perilaku, bukan melonggarkannya.

**Rute KPI** dipanggil MESIN (employee-service), yang tidak membawa identitas pemakai sehingga tak punya izin apa pun. Gerbangnya `MONITORING_SERVICE_KEY` — **terpisah dari `INTERNAL_GATEWAY_KEY`**. Alasannya penting: gateway memasang header `BIP-Gateway-ID` untuk SETIAP permintaan yang lolos JWT, jadi rute yang hanya bersandar padanya terbuka bagi semua karyawan yang sudah login lewat `/api/monitoring/kpi/uptime` (lihat [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Kunci yang belum dikonfigurasi **menutup** rute, bukan membukanya.

Muatan KPI sengaja agregat saja, tanpa daftar monitor: nama monitor memaparkan topologi infrastruktur, sedangkan penilaian hanya butuh satu angka.

### Hasil verifikasi produksi (1 Agustus 2026)

Dipanggil langsung di dalam container prod terhadap `kuma.db` sungguhan:

| Periode | `uptime` | `hari_berdata` / `hari_diminta` | `cakupan_persen` |
|---|---:|---:|---:|
| 2026-06 | `null` | 0 / 30 | 0 |
| 2026-07 | 99,813 | 23 / 31 | 74,19 |
| 2026-08 | 99,721 | 1 / 31 | 3,23 |

Angka 23 hari untuk Juli mengonfirmasi heartbeat terawal 9 Juli 2026 secara empiris. Gerbangnya juga terbukti: tanpa kunci layanan membalas 401, periode cacat membalas 400.

**Selama bulan berjalan, cakupan selalu jauh di bawah 100%** dan metriknya dilaporkan `semi`, bukan `otomatis`. Itu disengaja: uptime satu hari bukan uptime sebulan. Ia baru penuh setelah bulannya tutup, dan di situlah penilaian KPI dilakukan.

## Belum Diimplementasikan / Catatan

- **"System uptime" dan "Server uptime" belum dapat dibedakan.** Seluruh monitor di Kuma bertipe `docker` (33) dan `http` (1) per 1 Agustus 2026, jadi keduanya membaca angka yang sama. Memisahkannya butuh monitor tingkat host di Kuma — pekerjaan tim IT, bukan kode.
- **Juni 2026 dan sebelumnya tidak punya data.** Heartbeat terawal 9 Juli 2026; retensi Kuma `keepDataPeriodDays = 180`. Juli tercakup 23 dari 31 hari; Agustus dan seterusnya penuh.
- **Uptime bersifat lintas-tenant.** Infrastruktur yang dipantau melayani BIP dan ELT sekaligus, sehingga angkanya sama untuk kedua perusahaan. Ini benar secara fakta, bukan kebocoran scoping tenant ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]).
- **Belum ada konsumen yang benar-benar memakainya.** Endpoint sudah hidup dan terverifikasi, tetapi belum satu pun `kpi_template` diisi konfigurasi `auto` bersumber `uptime_sistem`, dan dashboard IT belum memanggil `/uptime`.
- `MONITORING_SERVICE_KEY` sudah terpasang di `.env` produksi (1 Agustus 2026). Nilainya berbeda dari `.env` pengembangan, dan itu memang seharusnya.

## Dependensi & Integrasi

- **Sumber data**: `kuma.db` milik [[IT - Monitoring System|Uptime Kuma]] (read-only, `mode=ro` di DSN + `:ro` pada mount Docker)
- **Konsumen**: [[APP - Web ERP]] (dashboard status IT), [[Microservices - Employee Service]] (sumber KPI `uptime_sistem`)
- **Gerbang**: [[CORE - API Master Gateway]] meneruskan `/api/monitoring/*` (butuh JWT)
- **RBAC**: [[CORE - RBAC dan Permission Set]] — modul `monitoring`

## Dokumen Terkait

- [[IT - Monitoring System]] — daftar monitoring tools yang dipakai perusahaan
- [[HRIS - Otomasi Skor KPI]] — analisis kelayakan otomasi skor KPI
- [[RUN - Menambah Metrik KPI Otomatis]] — cara menambah sumber metrik baru
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] — batas service pengumpul
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] — kenapa rute KPI butuh kunci sendiri
- [[IT - Server, VMs and Databases]] — VPS produksi tempat Uptime Kuma berjalan
