## Deskripsi

*Cara dev departemen menambahkan satu metrik KPI yang terisi otomatis, tanpa menyentuh aturan penilaian dan tanpa bertabrakan dengan dev departemen lain. Latar belakang dan peta metriknya ada di [[HRIS - Otomasi Skor KPI]]; keputusan batas servicenya di [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]].*

- **Status**: ✅ Mesinnya **deploy ke produksi 1 Agustus 2026** (PR #843 kontrak sumber, #857 mesin reduksi dan registry, #866 sumber `uptime_sistem`), dan **metrik otomatis pertama menyala 6 Agustus 2026**: tiga metrik Tech Development kini benar-benar menghasilkan angka di produksi. Prosedur di bawah final terhadap kode itu dan sudah pernah dijalankan sampai tuntas. Rinciannya di [[HRIS - Otomasi Skor KPI]].
	- ⚠️ **Prosedur di bawah berubah pada dua titik oleh batch 6 Agustus 2026 yang MERGED tetapi BELUM di-deploy** (bip-erp PR [#1049](https://github.com/bip-itteam-internal/bip-erp/pull/1049)/[#1051](https://github.com/bip-itteam-internal/bip-erp/pull/1051)/[#1053](https://github.com/bip-itteam-internal/bip-erp/pull/1053)): sumber bermetrik kini didaftarkan lewat **`DaftarkanSumberBermetrik`** agar ikut masuk katalog, dan **`TargetPeriode` sudah tidak ada** — penggantinya `TargetBerlaku`. Bab **Langkah 2** dan **Target yang berubah tiap bulan** sudah menyesuaikan. Sampai batch itu di-deploy, `GET /kpi/sumber-katalog` dan `POST /kpi/auto-values/pratinjau` belum dapat dipakai di produksi.
	- Catatan lama "frontend produksi belum menampilkan `auto_value`" **sudah tidak berlaku**: FE prod di-deploy ulang 6 Agustus 19:02 WIB sesudah PR erp-frontend #831 merged.
	- ⚠️ **Di DEV, `MONITORING_SERVICE_KEY` dan `MARKETING_ANALYTICS_SERVICE_KEY` kosong** (prod terisi). Gerbang kunci layanan fail-closed, jadi sumber yang menariknya **mustahil menghasilkan angka di dev**. Kalau metrikmu memakai salah satunya, jangan buang waktu menguji di dev sebelum kuncinya diisi.
	- ✅ **`ATTENDANCE_SERVICE_KEY` terisi di DEV maupun PROD** sejak 22 Agustus 2026, jadi `kedisiplinan_absensi` bisa diuji di dev. ⚠️ Tapi datanya tidak mewakili: hampir seluruh entri absensi dev berstatus `Tanpa Keterangan` (4.301 dari ~4.334 pada periode 2026-07), sebab tak ada yang benar-benar absen di sana. Angka `ketepatan_waktu` dev karenanya mendekati nol dan itu **benar** menurut datanya; jangan dibaca sebagai konektornya rusak.

Sumber yang sudah ada dan bisa dipakai sebagai contoh:

| Nama sumber | Datanya dari | Contoh yang mewakili |
|---|---|---|
| `skor_tim` | Koleksi `kpi_score` di employee-service sendiri | Sumber yang membaca data lokal, disempitkan ke tim atau departemen |
| `uptime_sistem` | monitoring-service lewat HTTP | Sumber yang menarik dari service lain, dan cakupannya bersifat WAKTU sehingga `CakupanPersen` ditimpa |
| `kaizen` | form-builder lewat HTTP | Sumber yang mencacah kiriman per periode |
| `kinerja_toko` | marketing-analytics lewat HTTP | **Satu sumber melayani banyak metrik** lewat `KPIAutoConfig.Metrik` — kini **delapan**: `revenue`, `ads_cost`, `gross_profit`, `jumlah_video`, `roas`, `roas_bersih`, `retur_persen`, `profit_bersih`; tiap entri katalog menghasilkan SATU angka. (`roas`/`roas_bersih` dulu bernama `roi`/`roi_bersih` — alias lama tetap jalan. `profit_bersih` = net_settle − hpp − iklan − retur − opex, boleh negatif. Detail: [[HRIS - Otomasi Skor KPI]]) |
| `kinerja_tiket` ✅ | task-management lewat HTTP | Pola yang sama, tetapi tiap entri katalog menghasilkan **Cuplikan utuh** karena bentuk cakupan tiap metriknya berbeda. (Penanda "belum merge" di sini sudah usang: PR [#1055](https://github.com/bip-itteam-internal/bip-erp/pull/1055) merged dan hidup di prod sejak 6 Agustus 2026.) |
| `kinerja_tiket_divisi` ⏳ | task-management lewat HTTP | Satu-satunya contoh sumber yang **cakupannya BUKAN orang**. Ia menilai tiket satu kelompok space, dan ruang lingkupnya ditentukan data di service seberang (`space.division` + `space.kpi_group`), bukan `KPIAutoConfig.Scope`. Juga contoh sumber yang **memakai ulang katalog penghitung sumber lain** alih-alih menyalinnya, dan yang **meneruskan badan galat** service seberang apa adanya ke `auto_basis`. Merged 2026-08-25, belum di prod |
| `kedisiplinan_absensi` ✅ | attendance lewat HTTP | Sumber yang cakupannya bisa **ratusan orang**, sehingga daftar `employee_id` dipecah 100 per panggilan. Contoh pemakaian cakupan **`perusahaan`**, dan contoh sumber yang memakai ulang definisi penyebut milik service seberang alih-alih menulis tandingannya |
| `turnover_karyawan` · `kontrak_karyawan` ✅ | `employee_db` sendiri | Sumber **lokal** yang tak memanggil HTTP sama sekali. `turnover_karyawan` juga contoh sumber yang **MENOLAK cakupan** yang tak sah baginya, alih-alih menerimanya lalu menghasilkan angka yang menjawab pertanyaan lain |

**Kalau sumbermu menyediakan lebih dari satu angka, jangan bikin sumber baru per metrik.** Pakai `KPIAutoConfig.Metrik` sebagai pemilihnya, seperti `kinerja_toko` dan `kinerja_tiket`. Dengan begitu mengganti metrik sebuah baris KPI cukup mengubah konfigurasi, tanpa sumber baru dan tanpa deploy.

Bentuk katalognya ikuti kebutuhan, bukan contoh terdekat. `kinerja_toko` memakai `map[string]func(M) (float64, error)` karena semua metriknya satu angka dengan cakupan yang sama. `kinerja_tiket` memakai `map[string]func(M) (employee.Cuplikan, error)` karena cakupan tiap metriknya memang tidak sama: dua metriknya membawa banyak pengukuran dengan penyebut berbeda, satu lagi cuma satu angka. Memaksakan bentuk satu-angka di situ akan menyembunyikan perbedaan itu, dan **cakupan yang salah membuat metrik setengah-terisi dilaporkan seolah lengkap**.

## Model mental: dari orang bekerja sampai angka di layar

> Versi gambarnya: [[HRIS - Pengumpulan Data KPI Otomatis.excalidraw]]. Bab ini dan diagram itu menjelaskan hal yang sama; pakai yang mana pun lebih cepat kamu pahami.

Pertanyaan pertama yang selalu muncul, dan sudah ditanyakan berkali-kali: *"datanya ditampung dulu di mana? apa perlu dihitung tiap hari?"*

**Tidak ada tabel penampung KPI, dan itu disengaja.** Yang menampung adalah database service tempat orang bekerja, dan ia terisi sendiri setiap hari karena orang memang bekerja di sana. Polanya sama dengan absensi: tap masuk dan keluar tercatat harian di `attendance`, tetapi tidak ada tabel "rekap absensi harian" yang ditulis tiap malam; laporan bulanan dihitung dari entri harian saat dibuka.

```
Sepanjang bulan   orang bekerja  -> data mentah tersimpan di service asalnya
                                    (tiket, video, heartbeat, order)
                                    TIDAK ADA pekerjaan tambahan, tidak ada cron KPI

Kapan saja        layar dibuka   -> GET /kpi/auto-values menghitung SAAT ITU dari data mentah
                                    cakupan < 100% -> dilabeli `semi` (bulan belum habis)
                                    tidak menyimpan apa pun

Saat menilai      POST /kpi      -> dihitung ULANG, hasilnya distempel jadi auto_value
                                    penilai boleh menerima atau menimpa

Setelah simpan    kpi_score      -> snapshot template + nilai DIBEKUKAN
                                    data mentah boleh berubah, skor tidak ikut
```

Angka hanya hidup di dua tempat, dan keduanya punya pemilik yang jelas:

| Tempat | Isinya | Boleh berubah? |
|---|---|---|
| Database service sumber | data mentah bertanggal (tiket, video, heartbeat) | Ya, terus-menerus |
| `kpi_score.template` | snapshot penilaian satu orang satu periode | **Tidak**, kecuali periode itu dinilai ulang |
| `kpi_template` | **konfigurasi saja, bukan angka** | Ya, dan tidak menyeret skor lampau |

Baris ketiga dijaga kode, bukan sekadar kesepakatan: `BersihkanNilaiOtomatis` membuang setiap hasil pengukuran per orang yang coba dititipkan ke master template. Tanpa itu, pemanggil bisa menitipkan `auto_value` karangan yang ikut tersalin ke tiap snapshot.

### Kenapa dihitung ulang, bukan diakumulasi harian

Tiga alasan, dan ketiganya sudah terbukti di sini:

1. **Data mentahnya sudah bertanggal.** Tiket punya `createdAt` dan `completed_at`, video punya `published_at`. Menghitung ulang satu bulan itu murah dan selalu benar. Penampung harian adalah salinan kedua, dan salinan kedua selalu berakhir menyimpang.
2. **Masa lalu berubah, dan itu normal.** Tiket di-reopen dan `due_date`-nya di-reset, CSAT dikirim terlambat dan boleh ditimpa, supervisor membetulkan tenggat. Angka harian yang terlanjur ditulis tidak ikut terkoreksi; hitung ulang benar dengan sendirinya.
3. **Pembekuannya sudah ada di tempat yang tepat.** Yang memang harus beku adalah angka saat dinilai, dan `kpi_score` sudah mengerjakannya. Menambah penampung harian berarti tiga lapis untuk pekerjaan satu lapis.

### Satu-satunya kasus yang memang butuh snapshot harian

Ketika **sumbernya tidak bisa ditanya soal masa lalu**. Contoh nyata sudah ada: `GET /monitors` di Uptime Kuma hanya membalas "30 hari terakhir", dan itu bukan nilai bulan mana pun, sehingga sengaja TIDAK dipakai untuk KPI; yang dipakai `GET /monitoring/kpi/uptime?periode=` yang membaca heartbeat sungguhan. Kalau retensi sumbermu pendek atau API pihak ketiga hanya memberi jendela berjalan, snapshot harian memang wajib.

Bila itu terjadi, **snapshot adalah tanggung jawab service sumber**, bukan modul KPI. Metrik tetap tidak menyimpan apa pun, dan sumbermu tetap menjawab pertanyaan "berapa untuk periode YYYY-MM ini".

### Yang menentukan sebuah metrik layak diotomatiskan

Bukan "apakah datanya ada", melainkan **siapa yang mengisi data penentunya**. Metrik yang datanya diisi oleh orang yang dinilai itu sendiri menaruh sebagian kemudi di tangan yang dinilai. Contoh nyata di modul tiket: CSAT diisi requester sehingga aman, tetapi `completed_at` distempel saat status menjadi Done, dan yang menandai Done adalah penangan tiket itu sendiri. Itu bukan alasan membatalkan metriknya, tetapi wajib disadari saat menyepakati bobot, dan itulah gunanya `auto_basis` beserta pembedaan `value != auto_value`: keduanya membuat "angka ini dari mesin atau dari atasan" tetap terjawab dari datanya sendiri.

## Yang perlu dipahami lebih dulu

Perhitungan dipecah tiga lapis, dan **kamu hanya menyentuh lapis pertama**:

```
Sumber      (kamu)          -> Cuplikan{Nilai[], Populasi}
Reduksi     (satu pemilik)  -> realisasi
Arah+Target (satu pemilik)  -> nilai 0..100
```

Sumber **tidak mengenal target dan tidak menghitung nilai**. Ia hanya melapor apa yang terukur dan berapa yang seharusnya terukur. Pemisahan itu disengaja: kalau sumber boleh menghitung nilai sendiri, sepuluh departemen akan melahirkan sepuluh semantik penilaian, dan skor KPI dibandingkan lintas departemen ("KPI Team minimal 70") sehingga perbedaan itu merusak perbandingannya secara diam-diam.

## Langkah 1: pastikan metriknya memang bisa

Tanyakan tiga hal ini sebelum menulis kode. Ketiganya sudah pernah menjatuhkan pekerjaan di sini.

1. **Datanya ada dan cukup terisi, dan nama field yang Anda hitung itu benar?** "Endpoint-nya ada" tidak sama dengan "datanya ada", tetapi ada jebakan yang lebih halus: **nol palsu karena salah nama field**. Contoh nyata yang sudah menjatuhkan pekerjaan di sini: sensus 2026-08-01 menyimpulkan SLA resolusi tiket punya **0 dari 293 task** yang memenuhi syarat hitung, dan atas dasar itu metriknya dicoret dari rencana. Pembacaan ulang 2026-08-06 menemukan **214 dari 307** justru terukur; sensusnya menghitung `completedAt` padahal BSON yang sebenarnya `completed_at`, dan field camelCase itu ada di **nol** dokumen. Karena itu: ambil nama field dari **tag `bson:` di struct Go**, bukan dari nama JSON di respons API, lalu buktikan dengan `countDocuments({<field>: {$exists: true}})` sebelum menyimpulkan apa pun. Nol yang rapi adalah alasan memeriksa ulang, bukan temuan.
2. **Bisa diatribusikan ke satu orang?** Metrik iklan bersifat per toko atau per kampanye, sedangkan KPI dinilai per orang. Kalau pemetaannya belum ada, itu pekerjaan data lebih dulu, bukan pekerjaan kode.
3. **Deskripsi metriknya tunggal maknanya?** Contoh yang tidak: `Revenue 240M` pada Kyura Supervisor, deskripsinya memuat "Target Profit 546 jt" **dan** "Omset 4.090.000.000". Dua angka, dua sumber berbeda. Selesaikan dengan pemilik metriknya dulu.

## Langkah 2: daftarkan sumber

Satu berkas baru di `services/employee/`, tidak menyentuh berkas milik orang lain.

```go
const SumberVideoToko = "video_toko"

func init() {
    DaftarkanSumber(SumberVideoToko, func(k KonteksSumber) (employee.Cuplikan, error) {
        // k.Karyawan, k.CompanyID, k.Periode, k.Cfg tersedia.
        // Kembalikan pengukuran per unit + berapa unit yang SEHARUSNYA terukur.
        return employee.Cuplikan{
            Nilai:    gmvTiapVideo,        // satu angka per video
            Populasi: jumlahVideoSeharusnya,
            Catatan:  "3 dari 20 toko belum dipetakan", // opsional, ikut ke basis
        }, nil
    })
}
```

**Kalau sumbermu menyediakan beberapa metrik, daftarkan dengan `DaftarkanSumberBermetrik`, bukan `DaftarkanSumber`:**

```go
DaftarkanSumberBermetrik(SumberVideoToko, []string{"jumlah_video", "gmv_per_video"}, fn)
```

Daftar metrik itu yang **masuk katalog** `GET /kpi/sumber-katalog` dan menjadi isi dropdown form konfigurasi. Menuliskannya di sini berarti tak ada daftar kedua di frontend yang bisa ketinggalan saat kamu menambah metrik. `DaftarkanSumber` tetap ada dan tetap benar untuk sumber satu-angka — ia hanya memanggil `DaftarkanSumberBermetrik` dengan daftar `nil`. **Daftar KOSONG (`[]string{}`) berbeda maknanya dari `nil`**: ia menyatakan sumber itu memang hanya menyediakan satu angka, sehingga form tidak menampilkan pilihan metrik — bukan menampilkannya kosong dan membuat pengisi mencari isian yang tak ada.

Aturan yang mengikat:

- **Nama sumber unik.** Nama ganda membuat `panic` saat boot, bukan penimpaan diam-diam, karena dua sumber bernama sama berarti separuh metrik mengambil data dari tempat yang salah dan gejalanya cuma angka keliru.
- **`Populasi` bukan `len(Nilai)`.** Bedanya yang membuat cakupan bermakna: 8 dari 12 anggota dinilai menghasilkan cakupan 67%, dan metriknya dilaporkan `semi`, bukan `otomatis`.
- **Kembalikan error, jangan Cuplikan kosong.** Cuplikan kosong dan kegagalan baca ditangani berbeda; menelan error jadi kosong membuat "tidak tahu" terbaca sebagai "hasilnya nol".

### Bila cakupanmu bukan "berapa unit dari berapa unit"

`Cakupan()` bawaan menghitung `len(Nilai) / Populasi`. Itu benar untuk metrik yang mencacah unit (anggota tim dinilai, video terpasang), tetapi salah untuk sumber yang hanya membawa **satu angka realisasi**. Contohnya cakupan **waktu**: uptime Juli 2026 berdiri di atas 23 dari 31 hari, tetapi `Nilai` hanya berisi satu angka, sehingga rasio bawaannya 1/1 dan melapor 100% lengkap. Cakupan **nilai** punya masalah yang sama: 18,7% omzet Kyura belum terpetakan pemiliknya, dan itu tak terwakili oleh cacahan unit.

Isi `CakupanPersen` untuk menimpanya:

```go
cakupan := float64(hariBerdata) / float64(hariDiminta) * 100
return employee.Cuplikan{
    Nilai:         []float64{uptime},
    Populasi:      1,
    CakupanPersen: &cakupan, // pointer: nil = pakai rasio unit, 0 tetap berarti nol
    Catatan:       fmt.Sprintf("%d dari %d hari berdata", hariBerdata, hariDiminta),
}, nil
```

Pointer, bukan `float64` biasa, supaya "belum diisi" terbedakan dari "nol persen" — dan nol persen adalah jawaban yang sah.

### Bila datanya ada di service lain

Boleh ditarik lewat HTTP; [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] mengizinkannya selama employee-service tetap jadi pemilik tunggal `kpi_score`. Tiga hal yang wajib diikuti, semuanya dipetik dari `kpi_sumber_uptime.go`:

- **Rute di service tujuan menggerbangi dirinya sendiri dengan kunci layanan sendiri**, bukan bersandar pada `INTERNAL_GATEWAY_KEY`. Gateway memasang header itu untuk setiap permintaan yang lolos JWT, jadi rute yang bersandar padanya terbuka bagi semua karyawan yang sudah login ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Kunci yang belum dikonfigurasi harus **menutup** rute, bukan membukanya.
- **Jangan masukkan URL-nya ke `InternalURL`.** Peta itu divalidasi saat boot dengan `panic`, sehingga satu env yang belum dipasang saat deploy akan mematikan seluruh employee-service demi satu metrik KPI. Baca env-nya langsung.
- **Beri batas waktu klien HTTP-nya.** Tanpa itu, satu service yang tersendat menahan `GET /kpi` sampai frontend menyerah.

#### Cetak biru rute di service sumber

Bagian ini yang paling sering terlewat: **service sumber perlu rute baru**, karena rute laporan yang sudah ada hampir selalu tidak cocok. Rute laporan digerbang RBAC **pemanggil** dan cakupannya mengikuti siapa yang memanggil, sedangkan ini panggilan **mesin** yang menanyakan **orang lain**. Contohnya `/report/sla` di task-management: ada, tetapi menjawab "apa yang boleh dilihat pemanggil", bukan "berapa angka si A pada Juli".

Salin pola `services/monitoring/kpi_uptime.go`:

```go
// Kunci layanan TERPISAH dari INTERNAL_GATEWAY_KEY. Gateway memasang header itu
// pada SETIAP permintaan yang lolos JWT, jadi rute yang bersandar padanya
// terbuka bagi seluruh karyawan yang sudah login (ADR 0031).
var kunciLayananKPI = os.Getenv(common.Env.<Service>ServiceKey)

func gerbangKunciLayanan(c *fiber.Ctx) error {
    // Kunci yang belum dikonfigurasi MENUTUP rute, bukan membukanya.
    if kunciLayananKPI == "" || c.Query("key") != kunciLayananKPI {
        return c.Status(fiber.StatusUnauthorized).JSON(common.ErrorMessage.InvalidGatewayKey)
    }
    return c.Next()
}
```

Tiga hal yang membuat muatannya benar:

- **Sempitkan muatannya.** `KPIUptime` sengaja tanpa daftar monitor: nama monitor memaparkan topologi infrastruktur, sementara penilaian hanya butuh angka. Kalau kunci layanan bocor, yang terpapar sebatas itu. Terapkan hal sama pada rutemu: kirim angka dan cacahan, jangan judul tiket, nama toko, atau nama orang.
- **Bawa cakupannya, dan itu bukan hiasan.** Yang menilai orang berhak tahu bahwa angkanya berdiri di atas 23 dari 31 hari, atau 13 dari 51 tiket.
- **Bedakan "tidak ada data" dari "nol".** `Uptime *float64` memakai pointer supaya `null` berarti tidak ada heartbeat, bukan sistem mati sebulan penuh. Sumber lalu mengembalikan **error**, dan metriknya jatuh ke `manual` dengan alasan tertulis, bukan bernilai 0.

**Wajib ada test yang melewati Fiber**, bukan hanya test fungsi murni: `app.Test(httptest.NewRequest(...))` untuk tanpa `key`, `key` salah, dan env kosong. Alasannya tercatat sebagai kejadian nyata di ingatan tim: satu service pernah punya 183 test hijau sementara seluruh jalur galatnya membalas 502, karena tak satu pun test melewati Fiber.

Terakhir, env barunya dipasang di **dua** blok `docker-compose.yml`: service sumber (yang memeriksa kunci) dan employee-service (yang mengirimnya). Lupa salah satu membuat metrik diam-diam jatuh ke `manual`, dan gejalanya hanya kalimat di `auto_basis` yang tak dibaca siapa pun sampai ada yang bertanya.

## Langkah 3: isi konfigurasi metrik

Lewat `POST /kpi/templates` yang sudah ada. Tidak perlu deploy untuk mengubahnya.

⚠️ **Sesudah batch 6 Agustus 2026 di-deploy, langkah ini tidak lagi harus dikerjakan dev.** Form konfigurasi otomasi (erp-frontend PR [#832](https://github.com/bip-itteam-internal/erp-frontend/pull/832)) mengisi dropdown-nya dari `GET /kpi/sumber-katalog`, jadi sumber yang kamu daftarkan di Langkah 2 **langsung muncul di layar HR tanpa perubahan frontend apa pun**. Tugasmu berhenti setelah sumbernya terdaftar dan terbukti menghasilkan angka; yang menyalakan metriknya adalah pemilik metrik. Bedah Mongo di bawah tetap dipakai untuk template yang sudah ada, atau selama batch itu belum di-deploy. **Catatan gap**: menu **KPI Templates** hari ini hanya terlihat oleh pemilik `system_roles.hris`, jadi SPV departemen belum benar-benar dapat mengisinya sendiri walau backend mengizinkan — lihat [[HRIS - Otomasi Skor KPI]].

### Contoh yang benar-benar terpasang di produksi

Ketiganya dinyalakan 2026-08-06 dan sudah diverifikasi menghasilkan angka:

```jsonc
// Tech Development Leader / "Performance Monitoring Team" (bobot 0,4)
{ "sumber": "skor_tim", "formula": "rata_rata", "target": 70, "arah": "naik", "scope": "team" }

// Tech Development Supervisor / "Performance Monitoring Team" (bobot 0,3)
{ "sumber": "skor_tim", "formula": "rata_rata", "target": 70, "arah": "naik", "scope": "department" }

// IT Support / "Network " (bobot 0,4)   <- perhatikan spasi di ujung labelnya
{ "sumber": "uptime_sistem", "formula": "rata_rata", "target": 90, "arah": "naik", "scope": "department" }
```

**Pilihan `scope` harus berdasar data, bukan selera.** Untuk Leader dipilih `team` karena `work_data.supervisor_id` memang menunjuk 5 bawahan langsung yang semuanya aktif; kalau kolom itu kosong, `team` menghasilkan populasi nol dan metriknya gagal hitung. Periksa dulu: `db.work_data.countDocuments({ supervisor_id: "<employee_id atasan>" })`.

**Uptime tidak peduli `scope`**, tetapi fieldnya tetap wajib berisi nilai yang dikenal (`department` atau `team`), karena `ValidateKPIAutoConfig` menolak yang lain.

### ⚠️ Cara menerapkannya menentukan seberapa besar risikonya

`POST /kpi/templates` melakukan **`ReplaceOne`**: ia mengganti seluruh dokumen template. Payload yang kurang satu field berarti field itu **terhapus diam-diam**, dan template KPI memuat label, deskripsi, bobot, serta kunci metrik yang semuanya harus utuh.

Untuk menyalakan satu-dua metrik pada template yang sudah ada, bedah per-metrik jauh lebih sempit:

```js
db.kpi_template.updateOne(
  { _id: ObjectId("...") },
  { $set: { "metrics.$[m].auto": { sumber: "skor_tim", formula: "rata_rata",
                                   target: 70, arah: "naik", scope: "team" } } },
  { arrayFilters: [{ "m.key": "performance-monitoring-team" }] }
)
```

Menyaring lewat **`m.key`**, bukan `m.label`: label produksi memuat spasi di ujung dan typo, sedangkan `key` memang identitas stabilnya.

Konsekuensinya jalur ini **melewati `ValidateKPIAutoConfig`**, jadi konfigurasinya harus dicocokkan sendiri: formula dan scope termasuk kosakata yang dikenal, `arah` diisi sadar, dan `target > 0` untuk arah `naik`.

Apa pun jalurnya, **cetak konfigurasi sebelum dan sesudah**, lalu periksa dua penjaga: jumlah template ber-`auto` bertambah persis sebanyak yang diniatkan, dan `kpi_score` ber-`auto_value` **tidak berubah** (menyalakan konfigurasi tak boleh menyentuh penilaian yang sudah tersimpan).

```json
{
  "sumber":  "video_toko",
  "formula": "rasio_ambang",
  "ambang":  10000,
  "target":  70,
  "arah":    "naik",
  "scope":   "department"
}
```

### Katalog reduksi

| `formula` | Realisasi yang dihasilkan | Contoh metrik nyata |
|---|---|---|
| `rata_rata` | rata-rata `Nilai` | skor tim SPV, rating toko |
| `jumlah_unit` | banyaknya `Nilai` | `Kuantitas Video Konten`, target 125 |
| `jumlah_nilai` | jumlah isi `Nilai` | omzet departemen |
| `rasio_ambang` | persen `Nilai` ≥ `ambang`, terhadap `Populasi` | `Video ... Indikator 10.000/video`, ambang 10.000 target 70 |

Metrik yang sumbernya sudah berupa persentase (uptime, konversi) memakai `rata_rata` atas satu `Nilai`: realisasinya dipakai apa adanya, lalu dibandingkan dengan target seperti metrik lain.

**Persentase yang menempel di ujung skala tidak bisa diukur dengan rasio.** Uptime produksi bergerak di 99,8–99,9%, dan `realisasi/target` dibatasi 100, jadi metriknya bernilai 100 setiap bulan berapa pun targetnya dinaikkan — target 99,5 pun masih memberi 100, dan target 99,9 memberi 99,9. Metrik berbobot besar yang selalu penuh tidak membedakan bulan baik dari bulan buruk.

Penawarnya bukan menaikkan target, melainkan **membalik besarannya**: ukur yang tersisa (downtime, cacat, keterlambatan) dengan `arah: turun`, dan jadikan targetnya **anggaran** — berapa banyak yang masih dapat diterima. Downtime bergerak dari 0,07% sampai berkali lipat, sehingga dengan anggaran 0,5% (SLA 99,5%) bulan normal tetap 100 sementara downtime 1% jatuh ke 50 dan 2% ke 25. Sumber `uptime_sistem` karena itu menyediakan dua metrik: `uptime` dan `downtime`. Aturan umumnya: **kalau realisasi wajar selalu melampaui target, metriknya salah bentuk, bukan salah angka.**

**`ambang` dan `target` adalah dua hal berbeda.** `ambang` dipakai mencacah, `target` dipakai membandingkan. Metrik ICC membutuhkan keduanya sekaligus: ambang GMV 10.000 per video, target 70% video yang melewatinya.

### Arah target: bagian yang paling mudah salah

| `arah` | Artinya | Contoh |
|---|---|---|
| `naik` (bawaan) | makin besar makin baik | omzet, konversi, jumlah video |
| `turun` | makin kecil makin baik | waste, retur, CPA, selisih, temuan audit |

**Salah arah tidak menghasilkan error, hanya angka yang salah dan tampak wajar.** `Waste maksimal 1,5%` dengan realisasi 0,8% akan bernilai **53 dari 100** bila arahnya lupa diisi, padahal seharusnya penuh. Tidak ada yang akan curiga pada angka 53.

Dari 311 metrik produksi, **43 berarah turun** dan menumpuk di Finance, Manufaktur, Quality, dan General Affair. Kalau departemenmu salah satunya, anggap `arah: "turun"` sebagai bawaan sampai terbukti sebaliknya.

Untuk arah `turun`, **`target: 0` sah dan bermakna**: "zero accident", "zero major finding", "selisih 0%". Realisasi 0 bernilai penuh; sekali melanggar langsung jatuh ke 0, karena tidak ada yang namanya sedikit zero accident.

### Target berlapis tiga: per karyawan, per periode, umum

```json
{
  "target": 4090000000,
  "target_per_periode":  { "2026-08": 4500000000 },
  "target_per_karyawan": { "BIP-0086-09-24": 250000000 }
}
```

Yang menentukan target berlaku adalah **`TargetBerlaku(cfg, periode, employeeID)`**. ⚠️ **`TargetPeriode(cfg, periode)` sudah TIDAK ADA** — diganti fungsi itu di PR [#1051](https://github.com/bip-itteam-internal/bip-erp/pull/1051); kode yang masih memanggilnya tidak akan kompilasi.

Urutan menangnya dari yang paling khusus:

1. **`target_per_karyawan[employee_id]`** — menang atas semuanya
2. **`target_per_periode[periode]`**
3. **`target`** — lapis paling umum

Yang tak terdaftar jatuh ke lapis berikutnya, **bukan nol**. Pemeriksaannya memakai bentuk dua-nilai (`t, ada :=`), bukan membandingkan hasil dengan nol, sebab **target 0 sah** untuk arah `turun` dan memperlakukannya sebagai "tak diisi" akan diam-diam mengembalikan target umum yang bukan maksudmu.

**Pakai `target_per_karyawan` untuk metrik NOMINAL, bukan untuk rasio.** Alasannya bukan kelenturan melainkan ketimpangan yang terukur: profit antar toko ICC Juli 2026 berentang **570×**, dari Rp342.585.503 sampai minus Rp3.471.743. Satu garis target di situ meloloskan pemegang toko besar dan menggagalkan sisanya tanpa ada kaitannya dengan kinerja. Metrik rasio (ROAS, persentase retur) sudah ternormalisasi, jadi target seragam justru yang benar di sana.

⚠️ **Target per karyawan menggeser bebannya, bukan menghapusnya.** Sekali dipakai, target tiap orang jadi keputusan yang harus dipertanggungjawabkan tiap periode dan tak lagi terbaca dari satu angka di template. Isi lewat tabel massal di form konfigurasi (erp-frontend PR [#832](https://github.com/bip-itteam-internal/erp-frontend/pull/832)), dan **pratinjau dulu sebarannya** sebelum menyimpan.

### Pratinjau sebelum menyimpan

⚠️ Tersedia sejak PR [#1053](https://github.com/bip-itteam-internal/bip-erp/pull/1053) (**merged, belum di-deploy**).

`POST /kpi/auto-values/pratinjau` menghitung konfigurasi yang **belum tersimpan** untuk sampai **10** karyawan sekaligus, memakai jalur hitung yang sama dengan `/kpi/auto-values`. Gunanya satu: salah konfigurasi tidak menimbulkan galat, hanya angka salah yang tampak wajar. Yang dibaca dari sebarannya:

| Yang terlihat | Kemungkinan besar artinya |
|---|---|
| Semua 100 | Target terlalu rendah — metriknya tak membedakan apa pun |
| Semua 0 | Target terlalu tinggi, **atau arahnya terbalik** |
| Sebagian besar gagal hitung | Sumbernya belum siap, atau atribusinya belum lengkap |

Batas 10 orang bukan angka arbitrer: tiap orang adalah panggilan sumber tersendiri, dan sebagian sumber memanggil service lain lewat HTTP **berurutan**. Konfigurasi yang tak lolos `ValidateKPIAutoConfig` dibalas **400 berisi pesan yang dapat dibaca HR**, bukan 500 — yang salah adalah isian formnya.

## Dua bentuk yang jadi tugas sumber, bukan reduksi baru

Jangan menunggu reduksi baru untuk keduanya, karena tidak akan datang.

**Perbandingan antar-periode** ("turun ≥20% dari baseline", "2% YoY", "penurunan OPEX 3-5% dalam 6 bulan"). Sumber yang membaca dua periode dan melaporkan **deltanya** sebagai `Nilai`. Reduksinya cukup `jumlah_nilai` atau `rata_rata`.

**Ketepatan waktu** ("maks tgl 3 bulan berikutnya", "≤24 jam", "SLA"). Sumber mengubah tanggal jadi angka, mis. selisih jam terhadap tenggat, lalu `rasio_ambang` mencacah berapa yang lolos. Ada 59 metrik berbentuk ini.

## Aturan yang tidak boleh dilanggar

- **Jangan pernah mengarang angka saat data belum ada.** Metrik yang gagal dihitung dibiarkan kosong dengan alasannya di `auto_basis`, dan sumbernya otomatis jatuh ke `manual`. Mengisinya 0 akan menekan skor orang tanpa dasar dan tak terbedakan dari hasil yang memang nol.
- **Jangan memakai `label` sebagai kunci.** Label metrik di produksi memuat typo (`Perfomance Monitoring`) dan spasi di ujung (`Monitoring Team `). Kunci identitasnya `key`, diturunkan sekali lalu dipertahankan, pola sama dengan `position_items[].key` di [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].
- **Jangan mencocokkan entitas lewat nama.** Nama toko di produksi ada yang berspasi di ujung (`Kyura Beauty Official Store `). Pakai id.
- **Jangan membuat kosakata baru** untuk hal yang sudah punya nama. Sumber angka memakai `otomatis`/`semi`/`manual` (`KPISources` di `shared-library/models/employee/kpi_source.go`), dan `SumberMetrik` yang menentukannya, bukan pemanggil: konfigurasi saja tidak membuat metrik otomatis, dan cakupan di bawah 100% selalu `semi`.
	- ⚠️ **Koreksi 2026-08-06**: dua rujukan lama ke frontend keliru dan akan menyesatkan siapa pun yang mencarinya. Komentar `SumberMetrik` menyebut *"meniru `tampilanSumberKpi()` di frontend"*, padahal fungsi itu **tidak ada** di `erp-frontend` `origin/main`. Versi lama runbook ini menyebut kosakatanya sama dengan `finance/posisi/lib/status-sumber.ts`, padahal berkas itu memakai `ada`/`sebagian`/`belum` untuk keperluan yang berbeda (audit ketersediaan sumber di dashboard FAT). Jadi **kosakata tampilan `otomatis`/`semi`/`manual` di frontend belum ada dan memang perlu dibuat** saat layar Score KPI dikerjakan; itu bukan pelanggaran aturan ini.
- **Hormati batas perusahaan.** Data disempitkan memakai perusahaan **karyawan yang dinilai**, bukan pemanggil ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]). Produksi berisi lebih dari satu perusahaan.
- **Rute baru menggerbangi dirinya sendiri** ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]).

## Kesalahan yang sudah pernah terjadi di sini

Empat contoh nyata, semuanya bertipe sama: salah yang tidak menimbulkan error.

| Kejadian | Akibat |
|---|---|
| Enam toko Kyura tak pernah ditugaskan ke siapa pun | Rp 715,7 juta dari Rp 3,82 miliar (18,7%) luput dari hitungan omzet |
| Kolom `team` di `icc_account_mappings` menulis `Tech Development` untuk sepuluh orang Kyura | Atribusi ke departemen yang salah bila dijoin lewat kolom itu, bukan lewat `work_data` |
| Metrik `...10.000/video` diisi 0 untuk semua ICC tiap bulan | Semua ICC kehilangan poin yang sebenarnya mereka dapat |
| Template Kyura Supervisor menilai `Produk Beautyhacks` | Supervisor Kyura dinilai dari rating toko departemen lain |

## Checklist sebelum PR

- [ ] Jumlah dokumen sumber di produksi dicek, bukan cuma keberadaan koleksinya
- [ ] Atribusi ke orang terbukti, termasuk berapa persen yang belum terpetakan
- [ ] `arah` diisi sadar, terutama bila deskripsinya memuat "turun", "maksimal", "≤", atau "zero"
- [ ] `ambang` dan `target` dibedakan bila memakai `rasio_ambang`
- [ ] Sumber diuji dengan data palsu, tanpa Mongo
- [ ] Hasil hitung dibandingkan dengan skor manual periode terakhir, dan selisihnya dijelaskan
- [ ] Metrik yang gagal dihitung terbukti tetap kosong, bukan bernilai 0
- [ ] Bila menarik dari service lain: rute sumber punya test yang **melewati Fiber** untuk tanpa kunci, kunci salah, dan env kosong
- [ ] Env kunci layanan terpasang di **dua** blok compose (service sumber dan employee-service)
- [ ] Sumber bermetrik didaftarkan lewat **`DaftarkanSumberBermetrik`** dan metriknya benar-benar muncul di `GET /kpi/sumber-katalog`
- [ ] Sebarannya **dipratinjau** (`POST /kpi/auto-values/pratinjau`) untuk beberapa orang pada periode lampau — bukan semua 100, bukan semua 0
- [ ] Sudah dijalankan **sekali lewat gateway** sungguhan, bukan hanya lokal
- [ ] Merge-nya terbukti sampai `main`: `git merge-base --is-ancestor <merge-commit> origin/main`, atau berkasnya benar-benar ada di `origin/main`. Tanda **MERGED** di GitHub tidak cukup — PR yang `base`-nya menunjuk branch fitur lain kehilangan seluruh isinya bila branch dasarnya di-merge lebih dulu (terjadi nyata pada PR #1058, lihat [[HRIS - Otomasi Skor KPI]])
- [ ] Metriknya dibuka di layar **Otomasi KPI** (`/hris/kpi/otomasi`) dan berstatus `otomatis` atau `semi` — bukan `manual`
- [ ] **Label dan keterangannya diisi di kamus, di DUA locale** ([[REF - Penamaan Metrik & Sumber KPI]]). Sumber tanpa entri tidak hilang — ia jatuh ke perapian token (`kinerja_po_marketing` → "Kinerja po marketing") **tanpa keterangan sama sekali**, dan pengisi tak punya cara tahu sumbermu menghitung apa. Per 2026-08-25 separuh katalog (10 dari 20 sumber) berada dalam keadaan itu; jangan menambah yang kesebelas
- [ ] Labelnya **dilihat di layar**, bukan di editor: pemilih Sumber data selebar `w-60`, dan label di atas ±28 karakter terpotong di sana

Butir terakhir adalah cara termurah membuktikan metrikmu benar-benar hidup untuk **semua** orang di posisi itu, bukan cuma untuk satu karyawan yang kebetulan kamu uji. Statusnya `semi` bukan kegagalan — itu berarti angkanya nyata tetapi cakupan datanya parsial, dan layar itu menyebutkan berapa persen. Yang harus membuat berhenti adalah `manual`: berarti hitungannya gagal, dan sebabnya sudah tertulis di kolom keterangan.

Butir kedua dari terakhir bukan formalitas. Perbandingan itulah yang menemukan bahwa skor ICC manual meleset ke dua arah, dan tanpa itu otomasi akan diam-diam menggantikan satu kesalahan dengan kesalahan lain.

## Dokumen Terkait

- [[HRIS - Pengumpulan Data KPI Otomatis.excalidraw]] (diagram: di mana data ditampung, kapan dihitung, kapan beku)
- [[HRIS - Alur KPI Otomatis Rinci.excalidraw]] (diagram: jalur request employee-service, langkah demi langkah)
- [[HRIS - Otomasi Skor KPI]] (peta metrik, matriks label per posisi, temuan data)
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] (batas service, pemicu ekstraksi collector)
- [[HRIS - Key Performance Index]] (mekanisme scoring, RBAC, cakupan tim Leader)
- [[Microservices - Employee Service]] (pemilik `kpi_template` dan `kpi_score`)
- [[Microservices - Integration Service]] · [[Microservices - Marketing Analytics Service]] (calon sumber data marketing)
- [[HRIS - Organization Structure]] (cakupan departemen dan atasan langsung)
- [[REF - Penamaan Metrik & Sumber KPI]] (aturan label & keterangan; bagian dari checklist di atas)
