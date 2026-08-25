## Deskripsi

*Analisis kelayakan **mengisi skor KPI secara otomatis** dari data yang sudah dimiliki ERP, bukan diketik manual oleh supervisor. Menjawab: dari 311 metrik yang benar-benar terpasang di production, mana yang sumber datanya sudah ada, mana yang modulnya ada tapi belum dipakai, dan mana yang memang tidak punya sumber sama sekali. Melengkapi [[HRIS - Key Performance Index]] yang menjelaskan mekanisme scoring-nya.*

- **Status**: ⚠️ **24 metrik ber-`auto` di produksi per 2026-08-20**, tersebar di 11 template. Angka "tiga metrik Tech Development" di bawah adalah keadaan **6 Agustus 2026** dan sudah lama terlampaui; bab **Metrik otomatis yang sudah menyala** belum disegarkan mengikutinya. Sensus 2026-08-20 langsung ke `employee_db` prod: 24 dari 362 metrik di 83 template, menyentuh **38 dari 183 karyawan aktif**, dan **30 di antaranya berada di posisi yang otomasinya PENUH** (bobot 1,00) yaitu ICC Beauty Hacks 19 orang dan ICC Kyura 11 orang. Ketiga puluh orang itu kini dibekukan sistem, lihat [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]. Catatan lama "belum ada satu pun metrik yang terisi otomatis" **sudah tidak berlaku**. Mesinnya sendiri jalan sejak PR #843 (kontrak sumber nilai), #857 (mesin reduksi + arah target + registry), dan #866 (sumber `uptime_sistem`), deploy 1 Agustus 2026. **Inventaris sumber datanya ✅ grounded** ke kode `origin/main` bip-erp commit `23c6bdc8` dan sensus dokumen 15 database production per **2026-07-31**.
	- ✅ **Penilai kini bisa melihatnya.** Frontend produksi di-deploy ulang **6 Agustus 19:02 WIB** (container `frontend-hris-dashboard`), sesudah PR erp-frontend #831 dan #834 merged, jadi modal Score KPI di produksi sudah memuat pengambilan `auto-values`. Catatan lama "penilai belum melihatnya, otomasi hidup di API saja" sudah tidak berlaku. Perlu diketahui: nilainya muncul sebagai **usulan yang harus ditekan** lewat tombol "Pakai usulan" (#831 sengaja tidak mengisi kolom otomatis), jadi supervisor yang tidak menekannya tetap melihat kolom kosong — itu perilaku yang dirancang, bukan kegagalan pengambilan data.
	- ⚠️ **Batch besar berikutnya merged tetapi BELUM di-deploy** (bip-erp #1049/#1051/#1053, erp-frontend #831/#832, seluruhnya 6 Agustus 2026): katalog sumber, pratinjau konfigurasi sebelum simpan, jejak perubahan, target berbeda per karyawan, dan metrik `jumlah_video`. HR karenanya **belum** benar-benar dapat mengisi konfigurasi sendiri di produksi. Rincian, gap yang tersisa, dan satu PR yang **tidak sampai ke `main`** ada di bab **HR mengisi konfigurasinya sendiri** di bawah.
	- ✅ **Layar yang menjawab "metrik mana yang macet" sudah ada di produksi.** Modal Score KPI menjawab satu orang satu periode; untuk melihat seluruh metrik satu departemen sekaligus beserta sebab yang gagal, ada halaman **Otomasi KPI** (bip-erp PR [#1066](https://github.com/bip-itteam-internal/bip-erp/pull/1066) + erp-frontend PR [#843](https://github.com/bip-itteam-internal/erp-frontend/pull/843), keduanya merged 6 Agustus 2026; `Employee-Service`, `API-Gateway`, dan `frontend-hris-dashboard` prod di-recreate 7 Agustus 2026 pagi). Rinciannya di bab **Layar diagnostik** di bawah.
	- ✅ **Kebuntuan HRGA dibuka 22 Agustus 2026.** Lima metrik HRGA berlabel "bisa otomatis sekarang" selama berbulan-bulan ternyata **tak punya konektor**, sehingga tak ada apa pun untuk dipilih HR di `/hris/kpi/otomasi`. PR [#1379](https://github.com/bip-itteam-internal/bip-erp/pull/1379) menambah `kedisiplinan_absensi`, `turnover_karyawan`, dan `kontrak_karyawan` (total sumber terdaftar **15 → 18**) plus cakupan **`perusahaan`**, dan sudah naik di prod maupun dev hari itu juga. ⚠️ **Yang bertambah baru KEMAMPUANNYA**: konfigurasi `auto` kelima metrik itu belum diisi, jadi jumlah metrik ber-`auto` di produksi **belum berubah**. Rincian per metrik beserta cakupan yang harus dipilih ada di [[HRIS - Matriks KPI per Departemen]].
- **Ruang lingkup**: `kpi_template` / `kpi_score` di [[Microservices - Employee Service]]. **Bukan** engine insentif marketing di [[Microservices - Insentive Service]], walau bab 6 mengusulkan menyambungkan keduanya.

## Metrik otomatis yang sudah menyala

Dinyalakan di produksi **2026-08-06** dengan menulis blok `auto` pada tiga metrik `kpi_template`. Tidak menyentuh `kpi_score` sama sekali, jadi seluruh penilaian yang sudah tersimpan tetap beku.

| Posisi | Metrik | Bobot | Sumber | Formula | Scope | Target |
|---|---|---:|---|---|---|---:|
| Tech Development Leader | `Performance Monitoring Team` | 0,4 | `skor_tim` | `rata_rata` | `team` | 70 |
| Tech Development Supervisor | `Performance Monitoring Team` | 0,3 | `skor_tim` | `rata_rata` | `department` | 70 |
| IT Support | `Network ` | 0,4 | `uptime_sistem` metrik `downtime` | `rata_rata` | `department` | 0,5 **arah turun** |

> Baris ketiga diubah 7 Agustus 2026 dari `uptime` target 90 menjadi `downtime` target 0,5 arah turun. Alasannya di bab **Kenapa tiga ini yang didahulukan** di bawah: target 90 atas uptime memberi 100 setiap bulan, dan metrik yang selalu penuh tidak mengukur apa pun.

**Hasil nyata, diverifikasi lewat `GET /kpi/auto-values` untuk orang sungguhan pada hari yang sama:**

| Siapa | Periode | `auto_value` | Cakupan | Sumber | `auto_basis` |
|---|---|---:|---:|---|---|
| Tech Dev Leader | 2026-07 | **100** | 100% | `otomatis` | rata-rata 86.00 dari 5 pengukuran (populasi 5); target naik 70.00 |
| IT Support | 2026-07 | **100** | 74,19% | `semi` | rata-rata 99.81 dari 1 pengukuran; 23 dari 31 hari berdata; target naik 90.00 |
| Tech Dev Leader | 2026-08 | — | — | `manual` | belum dapat dihitung: belum ada satu pun pengukuran pada periode ini |

Tiga hal yang dibuktikan baris-baris itu, dan ketiganya inti rancangannya:

1. **Cakupan penuh menghasilkan `otomatis`, cakupan parsial menghasilkan `semi`.** Uptime Juli melampaui targetnya, tetapi heartbeat baru ada 23 dari 31 hari, jadi angkanya dipakai sambil menyatakan ia berdiri di atas data parsial.
2. **Bulan berjalan tidak dikarang.** Agustus belum punya penilaian, dan sistem menjawab "belum dapat dihitung" beserta alasannya, bukan nol.
3. **Nilai dibatasi 100.** Realisasi Leader 86 atas target 70 sebenarnya 122,8.

**Dampak ke skor yang sudah ada: nol.** Juli sudah dinilai manual dengan angka yang kebetulan sama persis (100 pada kedua metrik), dan snapshot `kpi_score` beku sehingga tak tersentuh. Angka otomatis baru terpakai pada penilaian **Agustus**, yang dikerjakan awal September.

### Dua hal yang menentukan apakah otomasi Agustus benar-benar terpakai

Diperiksa langsung ke database produksi 2026-08-07.

**1. `skor_tim` menuntut urutan penilaian, dan salah urutan tak bisa diperbaiki.** Metrik `Performance Monitoring Team` membaca `kpi_score` **periode yang sama**. Per 7 Agustus, `kpi_score` periode `2026-08` masih **nol dokumen** (periode terakhir yang terisi 2026-07 dengan 150 dokumen), jadi kedua metrik itu wajar berstatus `manual` di layar Otomasi KPI sekarang — sistem menjawab "belum ada satu pun pengukuran pada periode ini", bukan mengarang nol.

Konsekuensinya di awal September: **anggota tim harus dinilai lebih dulu, baru Leader dan Supervisor.** Kalau Leader dinilai duluan, `auto_value`-nya kosong, penilai mengisi manual, lalu `POST /kpi` membekukan snapshot itu — dan angka otomatis untuk bulan itu tak pernah terpakai meski datanya muncul beberapa jam kemudian. Snapshot beku adalah inti desain penilaian, jadi ini tidak bisa dibatalkan dengan menilai ulang tanpa menimpa penilaian yang sudah tersimpan.

**2. Cakupan tim Leader sudah penuh; yang kosong justru posisi Supervisor.** Tech Development punya 11 baris `work_data`, tetapi **hanya 6 yang akunnya aktif** — lima non-aktif (dua Backend Developer, satu Frontend Developer, satu IT Support, dan **Supervisor `BIP-0135-03-25` sendiri**). Keaktifan ditentukan `system_authentication.is_active`, kriteria yang sama dipakai `akunAktif()` di `services/employee/subordinate.go:60`, jadi yang non-aktif memang tak pernah masuk perhitungan KPI.

Dari enam yang aktif, **lima sudah punya `supervisor_id` dan semuanya menunjuk Leader** (`BIP-0221-10-25`). Satu-satunya orang aktif tanpa atasan adalah Leader itu sendiri, dan itu memang disengaja. Jadi `scope: team` miliknya mencakup **seluruh bawahan aktifnya, bukan sebagian** — konsisten dengan cakupan **100%** yang tercatat pada baris hasil Juli di atas. Rata-rata 86,00 berasal dari kelima bawahan itu (91,6 · 91,6 · 83,575 · 81,6 · 81,6) dan cocok persis dengan yang dilaporkan `GET /kpi/auto-values`.

> Catatan koreksi: dokumen ini sempat menyatakan sebaliknya — bahwa metrik Leader "hanya mencakup separuh departemen" karena 5 dari 11 orang punya `supervisor_id`. Itu **salah**: 11 adalah jumlah baris `work_data`, bukan jumlah karyawan aktif, dan bukti pembantahnya sudah ada di dokumen ini sendiri berupa cakupan 100% pada hasil Juli. Angka mentah dari `work_data` tidak boleh dibaca sebagai jumlah orang tanpa menyaring keaktifan lebih dulu.

**Yang benar-benar perlu ditindaklanjuti adalah posisi Supervisor yang kosong.** Template `Tech Development Supervisor` punya konfigurasi `auto` (`skor_tim`, `scope: department`, target 70), tetapi tak seorang pun aktif memegang posisi itu. Di layar Otomasi KPI posisi itu muncul berstatus **`tanpa_karyawan`** — contoh nyata pertama status tersebut, dan alasan status itu dibuat: konfigurasi yang benar tetapi tak menghasilkan apa pun karena tak ada yang dinilai. Selama posisi itu kosong, konfigurasinya tidak berpengaruh pada siapa pun. Konteks hierarki: [[HRIS - Key Performance Index]].

Metrik ketiga, `Network` milik IT Support, tidak bergantung pada penilaian siapa pun: `Monitoring-Service` hidup di produksi dan `MONITORING_SERVICE_KEY` terpasang 32 karakter di employee-service, jadi ia menghasilkan angka dari heartbeat harian sejak hari pertama bulan berjalan — dengan cakupan parsial selama bulannya belum habis, dan itulah sebabnya statusnya `semi`.

Heartbeatnya diperiksa 7 Agustus 2026 lewat endpoint yang sama dengan yang dipakai KPI: **7 dari 7 hari yang sudah berjalan terisi, tanpa satu pun hari bolong** (uptime 99,93%). Angka 23 dari 31 pada Juli juga bukan kerusakan — heartbeat produksi baru dinyalakan 9 Juli, dan 9 sampai 31 tepat 23 hari. Jadi pada 1 September cakupannya akan penuh dan statusnya naik dari `semi` ke `otomatis`.

**Tetapi bentuk metriknya salah, dan itu ditemukan justru karena angkanya terlalu bagus.** Uptime 99,9% terhadap target 90 menghasilkan 111%, dibatasi 100 — dan akan 100 setiap bulan selama sistem tidak mati lebih dari tiga hari berturut-turut. Metrik berbobot 0,4 yang selalu penuh tidak mengukur apa pun. Menaikkan target tidak menolong: pada target 99,5 pun Juli tetap 100, dan pada 99,9 masih 99,9, sebab uptime memang menempel di ujung skala.

Penawarnya membalik besarannya: metrik **`downtime`** dengan `arah: turun` dan target berupa **anggaran downtime bulanan**. Dengan SLA 99,5% yang disepakati (anggaran 0,5%), Juli yang 0,19% tetap dinilai 100, sedangkan bulan dengan downtime 1% jatuh ke 50 dan 2% ke 25. Kemampuannya ditambahkan di bip-erp PR [#1069](https://github.com/bip-itteam-internal/bip-erp/pull/1069) sebagai metrik kedua pada sumber `uptime_sistem`.

✅ **Sudah berlaku di produksi 7 Agustus 2026.** employee-service di-deploy lebih dulu, baru konfigurasinya diubah — urutan itu wajib, sebab sebelum binary mengenal `downtime` metriknya akan jatuh ke `manual`. Konfigurasi metrik `Network` (template IT Support, `6a02a536551518dc794afc1a`, bobot 0,4):

| | sebelum | sesudah |
|---|---|---|
| `metrik` | — (berarti `uptime`) | `downtime` |
| `target` | 90 | 0.5 |
| `arah` | `naik` | `turun` |

Sisanya tidak disentuh (`sumber: uptime_sistem`, `formula: rata_rata`, `scope: department`), dan `kpi_score` tidak disentuh sama sekali sehingga penilaian yang sudah tersimpan tetap beku.

**Perubahan ini tidak menurunkan skor siapa pun sekarang.** Uptime Agustus 99,93% berarti downtime 0,07%, jauh di dalam anggaran, jadi nilainya tetap 100 — sama seperti sebelumnya. Yang berubah adalah metriknya kini **bisa** turun: dampaknya baru terasa pada bulan yang benar-benar buruk, dan itulah gunanya.

**Kenapa tiga ini yang didahulukan**: sumbernya sudah ada di produksi dan tak menunggu siapa pun mengisi data. `skor_tim` membaca `kpi_score` sendiri, `uptime_sistem` membaca heartbeat yang tercatat otomatis. Metrik IT lain (SLA tiket, CSAT) semula menunggu produksi ditarik ke `main` terbaru agar sumber `kinerja_tiket` ikut; **penantian itu selesai** — `Employee-Service` dan `Task-Management-Service` produksi di-recreate 6 Agustus 2026 sekitar pukul 19:00 WIB, jadi sumber `kinerja_tiket` sudah ada di prod. Yang menahannya sekarang bukan lagi kode melainkan **kesepakatan target**: tingkat ketepatan waktu Juli berkisar 8,7%–56,3% tergantung ambang yang dipakai, dan menyalakan metrik dengan target yang belum disepakati berarti menerbitkan angka merah yang tak seorang pun setujui dasarnya.

**Yang sengaja dilewati**: `Revenue 240M` pada Leader dan Supervisor. Deskripsinya di sistem berbunyi "Menjamin operasional IT tanpa gangguan" sementara dokumen KPI menyebut targetnya persentase tiket support yang selesai; dua sumber berbeda untuk satu label, dan itu keputusan pemilik metrik, bukan keputusan teknis.

## Layar diagnostik: Otomasi KPI

> **Status**: ✅ **live di dev dan produksi** — bip-erp PR [#1066](https://github.com/bip-itteam-internal/bip-erp/pull/1066) (endpoint) + erp-frontend PR [#843](https://github.com/bip-itteam-internal/erp-frontend/pull/843) (layar), merged 6 Agustus 2026; prod di-deploy 7 Agustus 2026 pagi (`Employee-Service`, `API-Gateway`, `frontend-hris-dashboard`).
>
> **Sudah diuji lewat gateway dev** dengan hasil: ketiga invarian ringkasan cocok, sepuluh tab departemen terisi, dan permintaan **tanpa parameter `department` dipilihkan backend** (jatuh ke "Beauty Hacks") alih-alih 400 atau 403. Pembebasan cache dibuktikan **dengan kontrol negatif**: `/kpi/auto-overview` tak pernah menjawab `X-Cache: HIT` pada panggilan kedua, sementara `/api/employee/birthdays` yang diperlakukan sama menjawab `HIT` — jadi Redis memang hidup dan rute ini memang dikecualikan, bukan sekadar cache yang mati.
>
> ⚠️ **Dua jalur belum tersentuh uji lapangan.** Dev tak punya satu pun konfigurasi `auto` (27 metrik, semuanya `belum`), sehingga status `otomatis`/`semi`/`manual` di sana tak pernah terbentuk dari data nyata — yang menjaganya masih unit test. Jalur **403 beserta `departemen_tersedia` di badannya** juga belum terbukti: akun uji yang tersedia ternyata berhak atas semua departemen, dan nama departemen karangan dijawab 200 kosong (itu perilaku `RequireKPIDepartmentRBAC` yang sudah ada, bukan sesuatu yang PR ini ubah). Keduanya baru bisa dibuktikan di produksi, tempat tiga metrik Tech Development menyala.

Tiga metrik menyala di antara 311, dan tak ada satu pun tempat untuk melihat itu. Sampai layar ini ada, pertanyaan "metrik mana yang sudah otomatis" hanya bisa dijawab dengan membuka modal penilaian satu orang satu periode, atau membaca `kpi_template` langsung di Mongo. Pertanyaan yang lebih penting, "kenapa metrik ini tidak menghasilkan angka", tak punya jawaban sama sekali di antarmuka.

**HRIS › Otomasi KPI** (`/hris/kpi/otomasi`) menampilkan satu departemen satu periode sekaligus: tiap metrik tiap posisi, statusnya, dan bila macet, alasannya apa adanya dari backend.

| Status | Artinya | Warna |
|---|---|---|
| `otomatis` | semua yang dinilai menghasilkan angka, cakupan penuh | hijau |
| `semi` | menghasilkan angka, cakupan datanya parsial | biru |
| `manual` | ada yang gagal dihitung; sebabnya ada di `alasan_gagal` | kuning |
| `belum` | metrik belum punya blok `auto` sama sekali | netral |
| `tanpa_karyawan` | sudah dikonfigurasi, tetapi posisinya tak dipegang siapa pun | kuning |

Tiga status pertama memakai nama yang sama persis dengan `KPISources` di `shared-library`, bukan istilah tandingan. Dua terakhir khusus layar ini karena keduanya keadaan yang tak pernah dialami satu metrik satu orang: sebuah metrik hanya bisa "belum dikonfigurasi" pada tingkat template, dan hanya bisa "tak ada yang memegang posisinya" pada tingkat departemen.

`semi` dihitung sebagai **menghasilkan**, karena angkanya nyata dan dipakai penilai; yang parsial adalah cakupan datanya. `tanpa_karyawan` masuk **perlu perhatian** bersama `manual`, karena keduanya menuntut tindakan manusia, sementara `belum` tidak.

**Keputusan rancangan yang perlu diketahui sebelum menirunya:**

- **Perhitungannya memanggil `terapkanOtomatis` yang sudah dipakai `/kpi/auto-values`**, bukan menyalin rumusnya. Kalau aturan reduksi, cakupan, atau pembatasan 100 berubah, kedua layar ikut berubah bersama. Layar diagnostik yang menghitung dengan rumusnya sendiri akan berbohong justru saat perbedaannya paling penting.
- **Evaluasi dibatasi 10 orang per metrik.** Sebagian sumber memanggil service lain lewat HTTP secara berurutan; satu posisi berisi 15 orang berarti 15 panggilan serial, dan timeout-nya menumpuk persis saat service sumbernya mati — yaitu saat layar ini justru dibuka. Batasnya meniru `maksPratinjauKaryawan` yang sudah dipakai endpoint pratinjau untuk alasan yang sama.
- **Rutenya dikeluarkan dari cache Redis gateway.** `GET /api/employee/*` dicache tiga menit; pada layar yang gunanya melihat apakah metrik yang baru dibetulkan sudah menghasilkan angka, tombol Segarkan akan berbohong selama tiga menit.
- **Frontend tidak memegang default departemen.** Backend yang memilih departemen pertama yang berhak dilihat pemanggil, dan badan 403 ikut membawa daftar departemen yang berhak, supaya pengguna bisa pindah tab alih-alih terdampar.

Kontrak lengkapnya di [[API - Employee Service]]; cara menambah metrik otomatis baru dan memverifikasinya lewat layar ini di [[RUN - Menambah Metrik KPI Otomatis]].

### Skor total per orang: kolom Otomasi dan kartu skor total harus satu rumus

`GET /kpi/auto-scores` menghitung **satu skor per karyawan** untuk kolom Otomasi di daftar Scoring dan badge skor di dropdown `/portal/kpi`; kartu skor total per-orang (tab Ringkasan → Per Karyawan) menghitung ulang dari `GET /kpi/auto-values` di frontend. Keduanya WAJIB memakai rumus yang sama: **rata-rata berbobot** `Σ(bobot × usulan) / Σ(bobot)` atas metrik yang berhasil dihitung — identik dengan skor final `ApplyKPIValues`, yang Σbobot-nya selalu 1,0 (dijaga `ValidateKPIMetrics`).

Sempat menyimpang 2026-08-25: `hitungSkorOtomatis` (`services/employee/kpi_auto_scores.go`) menjumlah `Σ(bobot × usulan)` **tanpa** membaginya dengan Σbobot. Selama data belum lengkap (Σbobot metrik terhitung < 1) jumlah itu keluar LEBIH RENDAH dari rata-rata, sehingga badge menampilkan angka berbeda dari kartu skor total untuk **orang yang sama** — dilaporkan 12 (jumlah) vs 15 (rata-rata) untuk SPV Kyura yang cakupannya 3 dari 4 metrik. Diperbaiki dengan menormalisasi `auto_score` di backend; cakupannya tetap terbaca lewat `terhitung`/`total_otomatis`, jadi normalisasi tidak menyembunyikan bahwa skornya berdiri di atas sebagian metrik. Pada cakupan penuh (Σbobot = 1) rata-rata sama dengan jumlah, jadi posisi ber-otomasi penuh tak berubah angkanya. Ini persis kelas "layar yang menghitung dengan rumusnya sendiri akan berbohong" di atas — kali ini dua layar berbeda rumus, bukan satu layar yang menyalin.

## HR mengisi konfigurasinya sendiri

> **Status**: ⚠️ **merged, BELUM di-deploy** per 2026-08-11. bip-erp PR [#1049](https://github.com/bip-itteam-internal/bip-erp/pull/1049) · [#1051](https://github.com/bip-itteam-internal/bip-erp/pull/1051) · [#1053](https://github.com/bip-itteam-internal/bip-erp/pull/1053) dan erp-frontend PR [#831](https://github.com/bip-itteam-internal/erp-frontend/pull/831) · [#832](https://github.com/bip-itteam-internal/erp-frontend/pull/832), seluruhnya merged 6 Agustus 2026. **Belum satu pun terbukti jalan lewat gateway produksi**, jadi seluruh bab ini menggambarkan kode yang ada di `main`, bukan perilaku yang sudah disaksikan.

Sampai batch ini, menyalakan satu metrik otomatis menuntut seseorang membedah `kpi_template` langsung di Mongo dengan `arrayFilters` — prosedur yang tertulis di [[RUN - Menambah Metrik KPI Otomatis]] dan memang dipakai untuk tiga metrik pertama. Batch ini memindahkan pekerjaan itu ke layar, sehingga HR tak lagi menunggu dev untuk tiap metrik.

**Tiga kemampuan baru di backend:**

| Apa | Rute / kontrak | Kenapa ada |
|---|---|---|
| **Katalog pilihan** | `GET /kpi/sumber-katalog?department=` | Daftar sumber, sub-metrik, formula, arah, dan scope selama ini hanya hidup di kode Go. Frontend yang menuliskan daftarnya sendiri membuat tiap sumber baru menuntut perubahan di dua tempat. Formula/arah/scope dibaca **lewat refleksi** atas struct di `shared-library`, bukan disalin — literal berarti pilihan baru tak pernah muncul dan gejalanya cuma dropdown yang kurang |

> [!important] Katalog kini menjawab cakupan dan rumus PER SUMBER
> ⚠️ Branch `feat/kpi-katalog-scope-sumber`, **belum merge, belum deploy** (2026-08-25).
>
> Sampai perubahan ini, katalog mengirim `scope` dan `formula` sebagai **daftar global**
> saja. Frontend karena itu tak punya dasar mengisi keduanya, lalu mengirim blok `auto`
> ber-`scope` kosong yang ditolak `ValidateKPIAutoConfig` dengan 400. Tiap entri sumber kini
> membawa empat field baru:
>
> | Field | Arti |
> |---|---|
> | `scope_didukung` | cakupan yang benar-benar dibaca sumber ini. **Kosong = cakupan tak berpengaruh**, form boleh menyembunyikan pemilihnya |
> | `scope_baku` | selalu terisi nilai yang lolos validator, termasuk bagi sumber yang mengabaikan cakupan |
> | `formula_baku` | rumus kanonik sumber yang tak bersub-metrik (mis. `skor_tim`) |
> | `formula_metrik` | rumus kanonik per sub-metrik; satu sumber bisa berbeda per metrik |
>
> **Hanya 5 dari 18 sumber yang benar-benar membaca `KPIAutoConfig.Scope`**: `skor_tim`,
> `kinerja_toko`, `kedisiplinan_absensi`, `kontrak_karyawan`, dan `turnover_karyawan`. Dua
> yang terakhir **menolak** cakupan selain `perusahaan` di dalam kodenya sendiri, jadi
> katalog menyatakannya lebih dulu supaya salah pilih ketahuan saat memilih, bukan saat
> skornya gagal dihitung berminggu kemudian. Bagi 13 sisanya cakupan adalah isian wajib
> yang diabaikan — validator masih menuntutnya, dan itu sengaja **tidak** diputuskan di
> [[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]].
>
> **Nilai rumusnya grounded ke pemakaian nyata**, dari sensus `kpi_template` produksi
> 2026-08-25 atas **34 metrik ber-`auto`** (naik dari 24 pada sensus 2026-08-20). Pasangan
> yang terbukti dipakai:
>
> | Sumber · metrik | Formula | Cakupan yang dipakai |
> |---|---|---|
> | `skor_tim` (tanpa sub-metrik) | `rata_rata` (6×) | department, team |
> | `kinerja_toko` · `gross_profit`, `profit_bersih` | `jumlah_nilai` | department, individu, team |
> | `kinerja_toko` · `roas`, `retur_persen` | `rata_rata` | department, individu, team |
> | `kinerja_ar` · empat metrik `*_persen` | `rata_rata` | department |
> | `kinerja_sales_admin` · `penjualan_tuntas_cutoff_persen` | `rata_rata` | department |
> | `kinerja_affiliate_tim` · `affiliate_aktif`, `conversion` | `jumlah_nilai` | individu |
> | `forecast_kas` · `akurasi_forecast_kas` | `jumlah_nilai` | individu |
> | `uptime_sistem` · `downtime` | `rata_rata` | department |
> | `varians_anggaran` · `varians_persen` | `rata_rata` | department |
>
> Sumber yang **belum punya bukti pemakaian sengaja dibiarkan kosong**, dan frontend
> meminta pengisi memilih. Menebak rumus lebih berbahaya daripada mengakui belum tahu:
> rumus yang salah tidak menimbulkan galat, hanya angka salah yang tampak wajar. Formula
> di luar `KPIReduksi` jadi **panic saat boot**, bukan koreksi senyap.
| **Pratinjau sebelum simpan** | `POST /kpi/auto-values/pratinjau`, maks **10** `employee_ids` | Salah konfigurasi **tidak menimbulkan galat**, hanya angka salah yang tampak wajar. Sebaran beberapa orang pada periode lampau menunjukkannya langsung: semua 100 berarti target terlalu rendah, semua 0 berarti terlalu tinggi atau arahnya terbalik |
| **Jejak perubahan** | koleksi `kpi_template_audits` | Konfigurasi kini disunting orang yang bukan penulisnya, dan blok `auto` yang berubah diam-diam mengubah nilai semua orang di posisi itu |

**Target berbeda per karyawan** (`TargetPerKaryawan`, berkunci `employee_id`) adalah perubahan yang paling menentukan hasilnya. `TargetPeriode` diganti `TargetBerlaku(cfg, periode, employeeID)` dengan urutan **per karyawan → per periode → umum**. Alasannya ada di datanya sendiri: profit nominal antar toko ICC Juli 2026 timpang **570×** — dari Rp342.585.503 sampai minus Rp3.471.743. Satu garis target meloloskan pemegang toko besar dan menggagalkan sisanya tanpa ada kaitannya dengan kinerja. Frontend #832 menyediakan tabel pengisian massalnya.

**`kinerja_toko` bertambah `jumlah_video`**, menjadi tujuh metrik (`revenue`, `ads_cost`, `gross_profit`, `jumlah_video`, `roi`, `roi_bersih`, `retur_persen`). Berbeda dari metrik rasio di sebelahnya, **nol video BUKAN galat**: seorang ICC memang dapat tidak menerbitkan video sebulan penuh, dan itu justru keadaan yang hendak diukur — menggalatkannya menyembunyikan kinerja terburuk sebagai "gagal hitung".

> Daftar metrik di atas **sudah bergeser** sejak Agustus 2026: `roi`/`roi_bersih` dinamai ulang `roas`/`roas_bersih`, dan metrik kedelapan `profit_bersih` ditambahkan. Rinciannya di bab **Perubahan Agustus 2026: ROAS, profit bersih, dan opex per ICC** di bawah.

**Penyempurnaan pengisian angka** (branch `feature/workspace-position`, **belum di-push** per 2026-08-12). Field target, ambang, `nilai_minimum`, dan target per-bulan/per-karyawan kini menampilkan **pemisah ribuan langsung saat mengetik** (netral-satuan, sadar-locale id/en, desimal dipertahankan), sementara yang dikirim ke backend tetap `number` mentah — komponen `InputAngka` + helper `formatKetik`/`parseAngka` di `src/features/hris/kpi/lib/angka.ts`. Di samping field target muncul **petunjuk satuan berbasis FORMULA** (`jumlah_nilai`→nominal, `jumlah_unit`→jumlah, `rasio_ambang`→persen, `rata_rata`→nilai) sebagai pill berikon, ditambah baris "Tersimpan ke sistem" yang memperlihatkan angka mentah. Satuan sengaja diturunkan dari formula, bukan nama sumber, agar sumber baru tak menuntut rilis FE — konsekuensi diterima: metrik uptime/downtime (juga `rata_rata`) berlabel "nilai (0–100)", bukan "persen". Tabel target massal tetap integer-only (`bacaAngka`) dan hanya menampilkan grouping saat blur.

### Yang harus diketahui sebelum angkanya dipercaya

Lima hal ini tidak terlihat dari layar mana pun, dan tiap satunya cukup untuk membuat skor terbaca sebagai kinerja buruk padahal bukan.

1. 🔴 **`shopee_shop_id` KOSONG di seluruh 12 baris `icc_account_mappings`** (diperiksa langsung ke produksi 2026-08-06; 12 baris aktif). `tokoMilikKaryawan` mengambil `tiktok_shop_id` dan `shopee_shop_id` dan melewati yang kosong, jadi hari ini profit dan revenue KPI **hanya terhitung dari toko TikTok**. Revenue Juli 2026 per channel: TIKTOK **Rp7.741.562.100** (20 toko) · SHOPEE **Rp1.951.681.920** (8 toko) · LAZADA Rp7.193.788 (2 toko) — jadi yang terhitung sekitar 80% omzet dan sisanya luput tanpa satu pun pesan. **Ini pekerjaan data tim marketing, bukan pekerjaan kode.** Pemetaan TikTok pun belum penuh: 21 toko terotorisasi, **11 dipetakan**.
2. 🔴 **Tiga toko berprofit NEGATIF sepanjang Juli penuh**: Kyura Beauty Skincare −3.471.743, Glowbooster Glowfast −718.501, Glowbooster.Store −604.194. Dengan arah `naik`, pemegangnya bernilai **0 berapa pun targetnya** — termasuk target per-karyawan. Angka negatif bukan kegagalan hitung, jadi tak ada yang jatuh ke `manual`; skor 0-nya akan terlihat sah. Keputusan pemilik metrik dibutuhkan sebelum penilaian Agustus, bukan sesudah.
3. ⚠️ **SPV departemen belum dapat menemukan halaman konfigurasinya.** Backend mengizinkan — `RequireKPIDepartmentRBAC` meloloskan penyunting template satu departemen, dan itu sebabnya `GET /kpi/sumber-katalog` menerima `?department=`. Tetapi menu **KPI Templates** (`/hris/kpi/templates`) terdaftar di kategori sidebar **`hris`** dengan `perm: "kpi.view"`, dan kategori yang bukan modul si pembaca hanya menampilkan item bertanda `public` — yang tidak dipasang di sini. Praktis **hanya pemilik `system_roles.hris` yang dapat mengisi konfigurasi**. **Gap ini belum diperbaiki (TBD)**: entah menandai menunya `public`, memindahkannya ke kategori `kpi`, atau memang menerima bahwa pengisian tetap milik HR.
4. ⚠️ **Jejak `kpi_template_audits` ditulis tetapi tak terbaca.** Belum ada endpoint maupun layar untuk membacanya — satu-satunya jalan adalah akses Mongo langsung. Belum pula ada index `{template_id, diubah_at:-1}`, sehingga penelusuran per template memindai seluruh koleksi. Riwayat yang hanya bisa dibuka lewat Mongo tidak menjawab pertanyaan yang membuatnya dibangun ("siapa yang mengubah target ini").
5. ⚠️ **Seluruh batch ini belum di-deploy.** Merged bukan bukti jalan; ingatan tim ini sudah mencatat fitur yang merged, deployed, dan tetap mustahil dipakai selama tiga hari karena satu lapisan pengikatan request tak ikut diperbarui. Sebelum diklaim selesai, tiap rute baru wajib dijalankan **sekali lewat gateway** sungguhan.

### KPI ICC versi Juli 2026

Sumbernya `REKOMENDASI KPI ICC UPDATE JULI 2026.xlsx` (dokumen HR, bukan kode). **Berlaku mulai penilaian Agustus 2026**; KPI Juli sudah ditutup dan snapshot `kpi_score`-nya beku.

| Posisi | Bobot dan metrik |
|---|---|
| ICC | 0,30 kuantitas video · 0,30 ROI · 0,40 Revenue |
| Leader ICC | 0,15 kuantitas video team · 0,15 ROI team · 0,50 Revenue team · 0,20 KPI Team (Average 70; **<70 = 0**) |
| SPV Marketing | 0,60 Revenue · 0,10 inventory turnover · 0,10 retur (maks 7%) · 0,20 Performance Monitoring (**<70 = 0**) |

- **Ambang GMV per video (10.000 / 150.000) DIHAPUS** dari versi ini. Metrik yang tercatat di bab Matriks di atas beserta pembuktian ambangnya karena itu **tidak lagi dipakai** untuk ICC mulai Agustus; yang tersisa dari sisi video hanya cacahannya. Itu pula sebabnya `/kpi/kinerja-toko` membawa `jumlah_video` telanjang tanpa GMV tiap video — membawanya hanya menambah muatan tanpa dipakai siapa pun.
- **Aturan "<70 = 0" dinyatakan lewat `NilaiMinimum`**, field pointer baru di `KPIAutoConfig`. Pointer, bukan nilai biasa, supaya "tidak memakai minimum" terbedakan dari "minimum nol" — dan minimum nol adalah aturan yang sah. Tanpa field ini aturan tebing itu mustahil dinyatakan lewat konfigurasi: realisasi 65 atas target 70 bernilai 92,86.
- 🔴 **`inventory turnover` pada SPV Marketing tidak punya sumber** — tidak ada modul demand planning di ERP mana pun. Metrik itu **tetap manual**, dan bobot 0,10-nya tak dapat diotomatiskan oleh batch ini maupun batch berikutnya.
- ⚠️ **Metrik ber-scope "team" pada Leader ICC belum punya cakupan yang benar.** Kedua Leader ICC punya **NOL bawahan** di `work_data.supervisor_id` (`icc_leaders`: Kyura → BIP-0024-01-23 Ridho, Beauty Hacks → BIP-0013-03-22 Satrio), sedangkan **23 dari 39 ICC** justru menunjuk BeautyHacks Supervisor. Dengan `scope: team`, keempat metrik team Leader menghasilkan populasi nol dan jatuh ke `manual`. Upaya menjawabnya lewat cakupan `tim_icc` **tidak sampai ke `main`** — lihat bab di bawah.

### Cakupan `tim_icc`: merged ke branch yang salah, tidak ada di `main`

> **Status**: 🔴 **TIDAK ADA di `main`** per 2026-08-11, meskipun PR-nya bertanda MERGED.

bip-erp PR [#1058](https://github.com/bip-itteam-internal/bip-erp/pull/1058) ("cakupan tim ICC untuk metrik KPI Leader") menambahkan `GET /kpi/anggota-tim-icc`, scope baru `KPIAutoScopes.TimICC`, dan sumber pembacanya. GitHub mencatatnya **merged 6 Agustus 2026 11:30:34 UTC** — tetapi `baseRef`-nya bukan `main`, melainkan branch `feat/kpi-katalog-pratinjau-audit` milik PR #1053. Branch itu **sudah lebih dulu di-merge ke `main` 39 detik sebelumnya** (11:29:55 UTC). Akibatnya isi #1058 mendarat di branch yang sudah tak dibaca siapa pun: merge commit-nya bukan leluhur `origin/main`, dan berkas `services/marketing-analytics/kpi_tim_icc.go` serta `services/employee/kpi_sumber_tim_icc.go` **tidak ada di `main`**. `KPIAutoScopes` di `main` masih berisi `department`, `team`, `individu` saja.

**Jadi masalah yang hendak dijawabnya masih terbuka**: kedua Leader ICC tetap tak punya bawahan di `supervisor_id`, dan metrik team mereka tetap tak dapat dihitung. Pekerjaan kodenya sudah ada dan teruji di branch `feat/kpi-cakupan-tim-icc`; yang dibutuhkan hanya PR baru yang menargetkan `main`.

**Pelajaran yang layak diingat**: PR bertumpuk (`base` menunjuk branch fitur lain, bukan `main`) kehilangan seluruh isinya bila branch dasarnya di-merge lebih dulu. Tanda MERGED di GitHub **tidak berarti kodenya ada di `main`** — yang membuktikannya hanya `git merge-base --is-ancestor <merge-commit> origin/main`, atau lebih sederhana, mencari berkasnya di `origin/main`.

### Perubahan Agustus 2026: ROAS, profit bersih, dan opex per ICC

> **Status**: ⚠️ **selesai & terverifikasi di dev, BELUM di prod** per 2026-08-19. Branch `feature/workspace-position` (bip-erp, sudah di-push), commit `619eeafd` (ROAS), `a51c5216` (kerangka profit bersih), `68adb0d2` (opex pakai `bersih`). Berlaku di prod setelah `marketing-analytics-service` + `employee-service` di-deploy, lalu migrasi template prod `roi`→`roas`.

Tiga perubahan lahir dari masukan manajemen atas metrik marketing ICC/SPV.

**1. `roi` → `roas`** (dan `roi_bersih` → `roas_bersih`). Rumus `revenue / ads_cost` di katalog `kinerja_toko` sejak awal memang **ROAS** (Return on Ad Spend, pembilang revenue KOTOR), bukan ROI — ROI membagi untung bersih terhadap biaya. Target 4,5 pun hanya masuk akal sebagai ROAS (revenue 4,5× belanja iklan), bukan ROI (450% untung). Nama lama tetap diterima lewat `aliasMetrikUsang` di `services/employee/kpi_sumber_kinerja_toko.go` supaya template yang belum dimigrasi tak gagal hitung saat biner baru naik lebih dulu dari config-nya; picker hanya menampilkan nama baru. **Menggantikan** daftar metrik `roi`/`roi_bersih` di bab "HR mengisi konfigurasinya sendiri" di atas. Diverifikasi di dev: metrik Kualitas Iklan ICC Kyura tetap menghasilkan angka identik (ROAS 3,97 atas target 4,5 → 88,3), murni ganti nama. Ruang lingkup "ROAS tingkat toko" (revenue toko ÷ belanja iklan) disepakati cukup — bukan ROAS per-kampanye dari laporan platform ads.

**2. Metrik baru `profit_bersih`** = `net_settlement − hpp − ads_cost − retur − opex`, per rumus atasan. Berbeda dari `gross_profit` yang bertumpu pada revenue: basisnya **net_settlement** (uang yang benar-benar diterima setelah potongan marketplace), lalu dikurangi seluruh biaya termasuk opex. **Boleh negatif** — ICC yang belanja iklannya melampaui hasil bersihnya memang rugi, dan menjepitnya ke nol menyembunyikan keadaan yang justru hendak diukur. `net_settlement` dan `hpp` ditambahkan ke `$group` agregasi `mart_profit_attribution` (sudah ada per baris); `opex` dari sumber di poin 3. Diverifikasi end-to-end di dev untuk BIP-0028-05-23 (Juli 2026): `4.918.124 − 1.577.794 − 3.117.799 − 0 − 0 = ` **222.531** — opex `bersih`-nya Juli = 0 (lihat poin 3), jadi hasilnya kebetulan sama dengan gross_profit bulan itu.

**3. Opex per ICC dari Accurate — `integration_db.incentive_opex_accurate`** (salinan lokal yang disinkron integration-service dari akun induk **`6000` "Beban Operasional"** Accurate, per proyek). Berkunci `proyek_no` (= `employee_id`; satu proyek Accurate = satu ICC) + `periode`. Field: `induk` (total 6000 mentah), `dikecualikan` (Σ 14 akun yang SUDAH terhitung di tempat lain), `bersih` = `induk − dikecualikan`, dan `rincian[]` (daftar akun yang **dikecualikan** itu, bukan yang dibebankan).

Rumus memakai field **`bersih`**, BUKAN `induk` mentah maupun `Σrincian`/`dikecualikan`. Ini menentukan benar-salahnya angka, dan integration-service sudah memutuskannya untuk rumus profit insentif yang bentuknya SAMA:
- `induk` **salah** — 88,5% opex Juli 2026 (Rp4,47 M dari Rp5,05 M) sudah dikurangkan di tempat lain; mengambilnya mentah menghitung dobel.
- `Σrincian`/`dikecualikan` **salah** — justru akun-akun yang sudah terhitung di tempat lain: fee e-commerce yang sudah terpotong di **net_settlement** (Admin E-Commerce 6112, Afiliasi 6113, Ongkir 6114, dst.), **iklan** (6107/6108), dan **gaji** (payroll). Mengurangkannya = dobel.
- `bersih` = opex yang **BELUM** terhitung di tempat lain — satu-satunya yang sah dikurangkan dari rumus yang net_settle/hpp/iklan/retur-nya sudah dihitung terpisah. Definisi milik integration-service (`AkunDikecualikan` di `incentive_opex_accurate.go`), dipakai ulang alih-alih melahirkan versi kedua. Hanya baris status `ada` yang dipakai.

[[Microservices - Marketing Analytics Service]] yang membacanya (satu-satunya dengan koneksi baca ke `integration_db`) lalu menempelkannya ke `/kpi/kinerja-toko` lewat `services/marketing-analytics/kpi_opex_icc.go`; opex gagal-baca tak menggagalkan metrik toko lain. (Iterasi awal keliru memakai `Σrincian`; dikoreksi ke `bersih`, commit `68adb0d2`.)

**Sumber `kinerja_affiliate_tim` — KPI Affiliate Acquisition PER-TIM-CHANNEL** (🟡 branch `feature/workspace-position`, **belum merge/prod**, terverifikasi DEV 2026-08-25). Keputusan pemilik metrik: KPI staf Affiliate dinilai **per-tim-channel (TikTok/Shopee)**, bukan per-akun/per-individu — realisasi = **TOTAL channel** pada periode, jadi semua staf di channel yang sama berbagi angka yang sama. Alur: endpoint `GET /kpi/kinerja-affiliate-tim` di [[Microservices - Marketing Analytics Service]] (`kpi_affiliate_tim.go`) menentukan channel staf dari koleksi **`affiliate_channel_team`** (integration_db) lalu menghitung total; sumber `kpi_sumber_affiliate_tim.go` di employee-service memilih metrik & merakit target.
- **Mapping staf→channel** dikelola dari **menu Affiliate** (dialog "Tim Channel"): CRUD `affiliate_channel_team` di [[Microservices - Integration Service]] (`/affiliate/channel-team`, gate `RequireMarketingLeader`, unik satu channel aktif per karyawan). 7 staf ter-seed: Nur Istiqomah & Ahmad Rifki Kurniawan → **Shopee**; Maulana/Fajar/Gumilang/Annisa/Ida → **TikTok**.
- **`Conversion`** = total order channel **AFFILIATOR EKSTERNAL saja** — akun **internal** (`icc_affiliate_accounts`, milik perusahaan/dijalankan ICC) **dikecualikan** (`creator_username`/`affiliate_username` `$nin` daftar internal), karena di luar kendali staf Affiliate Acquisition. **TikTok** distinct `order_id` di `affiliate_orders`; **Shopee** Σ`orders` di `shopee_affiliate_performance`. Target per-channel: TikTok **31.000**, Shopee **11.000** (lewat `target_per_karyawan` tiap staf sesuai channel-nya). Terverifikasi DEV Jul-2026 (data penuh 212.543 order, 9.223 kreator): TikTok **25.014** eksternal (dari 31.966 total − 6.952 internal), Shopee **8.533** (≈11k; tak ada akun internal Shopee).
- **`affiliate_aktif` (Jumlah Affiliate Aktif)** = affiliator external yang **dapat ≥1 order** pada bulan itu (revisi **2026-08-25**; sebelumnya "upload ≥1 video/konten"). **TikTok**: distinct `creator_username` ber-order di `affiliate_orders`. **Shopee**: distinct `affiliate_username` dengan `orders>0` di `shopee_affiliate_performance` (sumber & saringan tanggal SAMA dengan Conversion). Definisi order-based menghapus ketergantungan data upload konten yang dulu bikin undercount. Target per-channel: TikTok **7.500**, Shopee **4.500**. DEV Jul (verified lewat endpoint): Shopee **1.693** (dari 101 definisi lama), TikTok **2.323** — masih di bawah target.
- **`kinerja_affiliate` (per-holder)** lama tetap ada (untuk atribusi ICC pemegang akun via `icc_affiliate_accounts`), tetapi template Affiliate kini memakai `kinerja_affiliate_tim`.

> **Koreksi bab-bab di bawah**: baris "Varians budget vs realisasi OPEX — Budget/anggaran tidak tersimpan di ERP mana pun" (Semi-otomatis) **sudah tidak akurat**. `integration_db` memuat `anggaran_opex` (229 dok), `realisasi_opex` (112), `realisasi_opex_mingguan` (60) — level akun+bulan+departemen — dan `incentive_opex_accurate` (17) yang **per-ICC**.

**Yang masih menahannya (bukan kode):**
- **Cakupan opex tipis & `bersih` Juli = 0**: `incentive_opex_accurate` baru terisi **17 ICC, periode 2026-07** — terikat sinkron fitur incentive, bukan feed bulanan umum. Dan di data itu `bersih` = 0 untuk **semuanya** (seluruh opex mereka jatuh ke akun yang sudah terpotong di net_settlement/iklan), jadi profit bersih untuk sekarang praktis **= gross**. ICC/periode yang belum tersinkron juga mengembalikan 0 secara SAH. Butuh dipastikan Accurate mengisi semua ICC tiap bulan, dan bila `bersih` tetap 0 terus, perlu konfirmasi finance apakah pengecualiannya memang benar.
- **Target `profit_bersih` belum disepakati**: net profit jauh lebih kecil dari gross (88rb vs gross 222rb untuk contoh di atas), jadi target lama (mis. 50 jt untuk gross) tak cocok. Keputusan pemilik metrik.
- **Ganti atau tambah**: apakah metrik "Profit" ICC yang ada beralih ke `profit_bersih`, atau net profit jadi metrik terpisah di samping gross — TBD.

Konteks sumber: [[Microservices - Marketing Analytics Service]] (agregasi mart + join opex), [[Microservices - Employee Service]] (katalog metrik), [[External - Accurate]] (opex).

## Progres bulan berjalan di MyBharata

> **Status**: ⚠️ **endpoint live di `main`, layar ada di `dev` tetapi BELUM rilis** per 2026-08-25. Endpoint `pratinjauKPISaya` ada di `origin/main` bip-erp dan sudah dua iterasi lebih maju daripada versi awalnya (commit `45bdfd8b` menambah `template_id` dan pemilihan template beraturan bersama; `cakupan` dan `rincian` per metrik ikut dikirim). Layarnya mendarat di `dev` my-bharata (commit `42fe0528`). ⛔ **Yang terpasang di HP orang belum memuatnya**: rilis `origin/main` my-bharata masih `1.14.5+135`, sementara `dev` sudah `1.14.14+149`. Catatan lama "belum merge" sudah tidak berlaku.

Metrik otomatis hidup di produksi sejak 6 Agustus, tetapi **orang yang dinilai tak pernah melihatnya**. `GET /me/kpi-score` membaca dokumen `kpi_score` tersimpan dan membalas 404 bila belum ada, sedangkan layar KPI MyBharata mematok batas tombol maju di **bulan kemarin** — jadi bulan berjalan tak punya isi sekaligus tak bisa dibuka. Yang bisa melihat angka otomatis hanya penilai, lewat modal Score KPI dan halaman Otomasi KPI.

`?preview=true` pada periode yang belum dinilai kini membalas 200 dengan progres berjalan: metrik yang sudah punya angka beserta basisnya, ditambah **cacahan** metrik yang masih menunggu atasan.

**Tidak ada skor total di RESPONS, dan itu keputusan utamanya.** Metrik otomatis baru menutupi sebagian bobot template — untuk IT Support baru satu metrik berbobot 0,4 dari empat. Total apa pun yang dihitung dari sebagian itu menyesatkan: menganggap sisanya nol memberi 40, menormalisasi ke yang ada memberi 100, dan keduanya terlihat meyakinkan padahal keduanya salah. Angka besar di layar selalu terbaca sebagai kesimpulan, bukan perkiraan.

> ⚠️ **Koreksi 2026-08-25 atas kalimat di atas.** Versi lama berbunyi "tidak ada skor total di respons **maupun di layar**". Bagian "maupun di layar" **tidak pernah benar untuk web** dan **sudah tidak benar untuk mobile**. Rinciannya di bab berikut. Yang tetap berlaku: **responsnya sendiri memang tak membawa total** — kedua klien menghitungnya sendiri.

Keputusan lain yang perlu diketahui sebelum menirunya:

- **Metrik yang GAGAL dihitung diperlakukan sama dengan metrik manual**, tidak dikirim beserta alasannya. Kalimat seperti "belum ada tiket bertenggat" ditulis untuk penilai yang bisa menindaklanjuti, bukan untuk karyawan yang cuma akan membacanya sebagai tuduhan. Bagi yang dinilai, keduanya sama-sama menunggu atasan.
- **`preview` opt-in, bukan perilaku baru yang dipaksakan.** Aplikasi yang telanjur terpasang di ponsel tetap menerima 404 yang sama. Tanpa itu, bentuk respons yang berbeda membuat parser lamanya pecah pada field `template` yang tak ada — `KpiModel.fromJson` melakukan `json['template'] as Map<String, dynamic>` tanpa penjagaan.
- **`dinilai: false` adalah inti kontraknya.** Tanpa penanda itu aplikasi akan menampilkan angka berjalan dengan gaya yang sama seperti skor final.
- **Basis ditampilkan apa adanya** (`uptime 99.93%; 7 dari 31 hari berdata`) supaya angkanya bisa ditelusuri tanpa bertanya. Metrik bersumber `semi` diberi keterangan bahwa datanya belum lengkap — pada bulan berjalan itu keadaan normal, dan tanpa keterangan akan terbaca sebagai cacat.
- **Perhitungannya memanggil `terapkanOtomatis`**, bukan menyalin rumusnya: karyawan dan penilai harus melihat angka yang sama.

### Bulan berjalan jadi default, dan skor totalnya ikut tampil

> **Status**: 🟡 branch `feat/kpi-bulan-berjalan` (my-bharata, dari `dev`), **belum PR** per 2026-08-25. Rencana: `.task-plans/2026-08-25-kpi-mobile-bulan-berjalan.md`.

Irisan pertama menyediakan datanya tetapi tak mengubah pintunya: layar tetap **membuka bulan kemarin**, sehingga progres berjalan ada, bisa dibuka, dan tetap tak terlihat kecuali orangnya menekan panah kanan. Irisan ini memindahkan default ke **bulan berjalan**.

**Skor totalnya kini ditampilkan, dan itu membalik keputusan di bab atas.** Yang membalikkannya bukan argumen baru melainkan keadaan yang sudah berjalan: web `/hris/kpi` **sudah** menampilkan total dari otomasi di produksi (`kpi-scorecard.tsx`, lencana "dari Otomasi"), dihitung sebagai `Σ(bobot × nilai) / Σbobot` **atas metrik yang punya angka saja**. Menahannya di mobile berarti karyawan dan penilainya melihat angka berbeda untuk orang dan bulan yang sama — persis yang hendak dicegah prinsip "karyawan dan penilai harus melihat angka yang sama" di daftar atas.

Kekhawatiran lamanya tetap sah dan dijawab **di layar**, bukan dengan menyembunyikan angkanya:

- **Judulnya "Skor Sementara", tak pernah "Skor Akhir"**, dan kartunya berbeda dari kartu skor final.
- **Cakupan bobot disebut angka demi angka** ("Dihitung dari 40% bobot yang sudah terisi otomatis"). Bisa dibaca langsung sebagai persen karena `ValidateKPIMetrics` menjamin bobot satu template berjumlah tepat 1,0; nilainya tetap di-clamp karena template yang disunting langsung di Mongo tak melewati validasi itu, dan jalur itulah yang dipakai menyalakan metrik otomatis pertama.
- **Rumusnya ditiru persis dari web**, bukan disusun ulang. Konsekuensi yang diterima sadar: rumusnya kini hidup di dua tempat (TypeScript dan Dart) dan bisa menyimpang. Memindahkannya ke backend supaya kedua klien berbagi satu sumber adalah pekerjaan yang belum dikerjakan.

**Konsekuensi yang paling menentukan justru bukan soal angka.** Sensus 2026-08-20 mencatat metrik ber-`auto` baru menyentuh **38 dari 183 karyawan aktif**, jadi sesudah perubahan ini mayoritas orang mendarat di layar tanpa angka — padahal sebelumnya mereka langsung melihat skor final bulan lalu. Karena itu **kedua keadaan kosong diberi tombol "Lihat penilaian bulan lalu"**: kartu kosong progres (200 dengan `metrik` kosong) dan cabang **404** (posisi tanpa template KPI). Cabang 404 mudah terlewat dan justru yang paling berbahaya: ia juga menyambut **semua orang** bila employee-service yang terpasang belum mengenal `?preview=true`, dengan pesan "KPI tidak ditemukan" yang menunjuk ke sebab yang salah.

⛔ **Gerbang rilis: pastikan employee-service PROD sudah mengenal `?preview=true` sebelum versi mobile ini naik.** Bila belum, seluruh pemakai membuka KPI dan melihat keadaan kosong. Urutannya BE dulu, baru FE.

## Kondisi Saat Ini

> Bab ini menggambarkan keadaan **sebelum** otomasi menyala, dan sengaja dipertahankan sebagai titik banding. Per 2026-08-06 tiga metrik sudah otomatis (bab di atas); sisanya, 308 dari 311, masih diisi manusia.

Semula seluruh 311 metrik diisi manusia dan tidak ada jalur auto-fill di kode.

| Aspek | Kondisi (grounded) |
|---|---|
| Model | `KPITemplate{position, department, name, metrics[]}`, `KPIMetric{label, description, weight, value}`, `KPIScore{employee_id, period, template (snapshot), score}` di `shared-library/models/employee/models.go:351-377` |
| Aturan bobot | `ValidateKPIMetrics` mewajibkan label unik, bobot 0..1, total tepat 1.0 (`models.go:384-408`) |
| Pengisian nilai | `ApplyKPIValues` menerima map `label -> 0..100` dari body request. **Tidak ada sumber selain input manusia** (`models.go:411`) |
| Lampiran bukti | `POST/GET/DELETE /kpi/evidence` + `GET /kpi/evidence/:id/file` (`services/employee/kpi_evidence.go:217-224`); retensi dibersihkan cron harian 03:30 WIB (`services/employee/cron.go:40`) |
| Pengingat siklus | Cron `employee` tanggal 1 pukul 08:45 broadcast FCM + inbox (`services/employee/cron.go:34`) |
| Label = identitas | Label metrik adalah kunci unik template dan kunci map nilai. **Setiap rencana auto-fill harus mengikat ke label**, sehingga penamaan label yang buruk langsung menghambat otomasi |

**Snapshot production 2026-07-31**: 70 template, 311 metrik, 11 departemen, 204 karyawan aktif, 406 `kpi_score` (2026-03: 1, 04: 107, 05: 152, 06: 146). Periode 2026-07 belum diisi; polanya bulan berjalan diisi awal bulan berikutnya.

## Klasifikasi 311 Metrik

| Status | Jumlah | % | Arti |
|---|---:|---:|---|
| 🟢 Otomatis penuh | 73 | 23,5% | Sumber data ada di ERP **dan** terisi di production |
| 🟡 Semi-otomatis | 59 | 19,0% | Sumber ada, tapi butuh definisi, target, atau mapping tambahan |
| 🟠 Terblokir data | 35 | 11,3% | Modul sudah jalan di production tapi **koleksinya nol dokumen** |
| 🔴 Manual | 144 | 46,3% | Tidak ada sumber data, perlu fitur baru atau memang subjektif |

**42,5% metrik dapat diotomatiskan tanpa modul baru.** Bila modul yang sudah dibangun tapi menganggur ikut dipakai, naik ke 53,7%.

## Rekap per Departemen

| Departemen | Template | Metrik | 🟢 | 🟡 | 🟠 | 🔴 | % otomatis |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tech Development | 7 | 30 | 14 | 9 | 0 | 7 | 76,7% |
| Kyura | 9 | 27 | 16 | 1 | 0 | 10 | 63,0% |
| Procurement | 2 | 10 | 4 | 2 | 0 | 4 | 60,0% |
| Beauty Hacks | 11 | 30 | 14 | 2 | 0 | 14 | 53,3% |
| Finance | 11 | 61 | 13 | 17 | 0 | 31 | 49,2% |
| Human Resource | 5 | 31 | 7 | 5 | 10 | 9 | 38,7% |
| Manufaktur | 9 | 52 | 3 | 16 | 16 | 17 | 36,5% |
| General Affair | 5 | 24 | 1 | 5 | 1 | 17 | 25,0% |
| Quality | 4 | 18 | 1 | 2 | 8 | 7 | 16,7% |
| Kesekretariatan | 7 | 28 | 0 | 0 | 0 | 28 | 0% |
| **Total** | **70** | **311** | **73** | **59** | **35** | **144** | **42,5%** |

Departemen **Percetakan** (13 karyawan) dan **Marketing Offline Distribution** (1 karyawan) ada di `work_data` tetapi belum punya template KPI sama sekali.

## Peta Metrik ke Sumber Data (🟢 siap otomatis)

| Klaster metrik | Posisi terdampak | Sumber data | Volume prod 2026-07-31 |
|---|---|---|---|
| Konversi iklan TikTok | ADV Marketplace, Leader, Host Live, Affiliate (BHS + Kyura) | `integration_db.tt_business_gmv_max_performance_reports`, disegarkan cron harian 01:00 + intraday 4x sehari ([[IT - Background Jobs & Schedulers]]) | 712.855 |
| ROI/ROAS dan CPA | Host Live, Leader, ADV Marketplace | `marketing_analytics_db.mart_profit_attribution` (level `ad`/`campaign`/`video`/`shop`/`product`) | 405.543 |
| Kuantitas dan mutu video ICC | ICC (BHS + Kyura) | `tt_shop_video_performances`, `mart_video_performance`, `GET /insight/icc-video-metrics` ([[Microservices - Integration Service]]) | 84.134 / 87.813 |
| Omzet / Revenue | SPV BHS, SPV Kyura, SPV Finance, Leader | `integration_db.transaction_orders` + Accurate `GET /accounting/profit-loss` | 413.220 |
| Rating toko | SPV BHS, SPV Kyura, CS Kyura | `GET /integration/reviews/summary` (ringkasan **per toko**), koleksi `marketplace_reviews` + `product_rating_snapshots`, cron `sync-reviews` harian 06:45 | 6.314 / 10.933 |
| Retur penjualan | AR Staff (Retur) | `accurate_daily_returns`, `shopee_returns`, `GET /daily-returns/stats` | 3.351 / 271 |
| Piutang / AR aging | AR Leader, AR Staff (Piutang) | Accurate live proxy `GET /accounting/receivables`, `GET /orders/piutang/summary` ([[External - Accurate]]) | live |
| EBITDA, net income, cashflow, OPEX YoY | SPV Finance, Account Payable, Cost Control | Accurate live proxy `/accounting/profit-loss`, `/balance-sheet`, `/profit/cash-flow` | live |
| **Skor KPI tim** | 15 posisi SPV dan Leader (16 baris metrik), rinciannya di bawah | `employee_db.kpi_score` sendiri, diagregasi lewat department atau `work_data.supervisor_id` ([[HRIS - Organization Structure]]) | 406 |

> ⚠️ **Koreksi 2026-08-12, khusus baris "EBITDA, net income, cashflow, OPEX YoY" untuk Account Payable.** Ketiga metrik template `KPI Finance Staff Account Payable` yang tadinya diasumsikan masuk klaster ini ternyata **tidak sesederhana itu** saat ditelusuri satu-per-satu (Langkah 1 runbook):
> - **"100% pembayaran sesuai rencana kas"** — Accurate live proxy P&L/cashflow **tidak memuat tanggal pembayaran per faktur**. Yang ternyata dibutuhkan (dan baru ditemukan lewat probe live `purchase-invoice/list.do`) adalah field `lastPaymentDate` di level faktur — bukan di klaster ini sama sekali. Diselesaikan lewat sumber baru `kinerja_ap` di [[Microservices - Procurement Service]], bukan Accurate live proxy P&L. Lihat [[Microservices - Employee Service]] (registry sumber) untuk detail & status PR.
> - **"Perhitungan HPP"** — `/profit/costing-ratio` menjawab, tapi **selalu 100%** (486/486 SKU produksi punya HPP) dan **tak ber-periode** — nilainya sama tiap bulan. Metrik berbobot besar yang tak pernah bergerak tidak mengukur apa pun, pola sama dengan `uptime` sebelum dibalik jadi `downtime`. **Tetap divonis perlu definisi ulang**, bukan siap otomatis.
> - **"Laporan credit term"** — datanya (`term_name`, `due_date`) lengkap 2.055/2.055 di `procurement_db.faktur_pembelian`, tapi KPI-nya mengukur **penyerahan laporan**, bukan data itu sendiri — tak ada jejak kapan laporan diserahkan. **Tetap divonis perlu definisi ulang.**
>
> Pelajarannya: baris tabel klaster di atas menunjukkan sumbernya *ada*, bukan bahwa metriknya otomatis dijamin benar — dua dari tiga metrik Account Payable di klaster ini tetap manual setelah ditelusuri.
| Uptime server dan sistem | IT Infrastructure, IT Support, Tech Leader/SPV | Sumber `uptime_sistem` memanggil `GET /monitoring/kpi/uptime?periode=YYYY-MM` ([[Microservices - Monitoring Service]]). Jendela berjalan `GET /monitors` TIDAK dipakai untuk KPI: "30 hari terakhir" bukan nilai bulan mana pun | 34 monitor; heartbeat baru sejak 9 Juli 2026 |
| SLA e-ticket | IT Support, Backend/Frontend Developer | `GET /task-management/report/sla`, field `on_time_rate` untuk response dan resolution (`services/task-management/sla.go:112-159`) ([[IT - Helpdesk]]) | 307 task; 214 terukur resolusi, 63 response (prod 2026-08-06) |
| CSAT layanan IT | IT Support, Fullstack, Tech Leader | `GET /report/csat`, `GET /report/manpower-performance` (`avg_csat` per orang, `services/task-management/report_handlers.go:160-232`) | 17 tiket ter-rating (prod 2026-08-06) |
| Kedisiplinan dan kehadiran | Personalia, Culture & Industrial | `GET /attendance/report?date=YYYY-MM`, entri harian membawa `status` (Hadir/Terlambat/Tanpa Keterangan) dan `late_hour`; periode sudah tanggal 26 ke 26 mengikuti siklus payroll (`services/attendance/main.go:716`) ([[HRIS - Attendance System]]) | 24.163 entri |
| Administrasi kontrak | Personalia | `work_data.contract_ending` dan `join_date` ([[HRIS - Personalia]]) | 204 karyawan |
| SLA pengumpulan KPI | Training & Performance Officer | `kpi_score.metadata.created_at` dibandingkan `period` | 406 |
| On Time Delivery supplier | Staff Inventory, Admin GA | `GET /procurement/po/lead-time` + koleksi `penerimaan` ([[Microservices - Procurement Service]]) | PO 1.036, penerimaan 1.835 |
| Efisiensi harga beli dan credit term | Staff Inventory, Leader Procurement | `GET /harga/banding`, `GET /pemasok/:vendorNo/harga/riwayat`, `faktur_pembelian` | 2.055 faktur |
| Resi ke ekspedisi | Admin Warehouse | `manufacture_resi` + `warehouse_db.fulfillment_orders` ([[Microservices - Warehouse Service]]) | 328.272 / 38.949 |

### Semi-otomatis (🟡): apa yang masih kurang

| Klaster | Sudah ada | Yang kurang |
|---|---|---|
| Jumlah affiliate aktif/baru | `affiliate_orders`, `shopee_affiliate_performance` | Definisi "affiliator baru bergabung" dan master affiliate per brand |
| Ketepatan input transaksi (max tgl 3/4/5/7) | `accurate_daily_invoices`, `accurate_daily_returns` beserta timestamp sinkron | Tidak ada penanda periode closing resmi di ERP; deadline hanya tertulis di dokumen KPI |
| Varians budget vs realisasi OPEX | Realisasi dari Accurate | **Budget/anggaran tidak tersimpan di ERP mana pun** |
| Akurasi stok fisik vs sistem | `manufacture_stok`, `manufacture_saldo_awal_bulanan`, `POST /stok/reconcile`, `GET /selisih` | Siklus stock opname terjadwal belum tercatat ([[Manufacture - Stock & Material Management]]) |
| ITO, stockout, stock accuracy (PPIC) | Stok dan penjualan tersedia | Tidak ada modul demand planning, sehingga "akurasi forecast" tidak terukur |
| Ketepatan picking gudang | `fulfillment_orders` beserta event pick/pack/handover | Belum ada penanda miss-pick; hanya bisa diproksi lewat retur bermotif salah produk |
| Aset GA terdata dan labeling | `inventory_db.inventory` beserta handover per karyawan ([[Microservices - Inventory Service]], [[GA - Inventory Management]]) | Belum ada stock opname aset dan target cakupan |
| Delivery dan Quality developer | `task-management` (`due_date`, `reopen_count`) + `monitoring` | Perlu board development yang dipakai disiplin |

## Modul Ada tapi Data Kosong (🟠, 35 metrik)

Temuan paling penting. Kode berjalan di production, tetapi koleksinya **nol dokumen**, sehingga metriknya tidak bisa dihitung hari ini walau tidak butuh development.

| Modul | Koleksi | Isi | Metrik yang tergantung |
|---|---|---:|---:|
| Production Log dan Batch Record ([[Microservices - Manufacture Service]], [[Manufacture - Dokumen Produksi Batch]], [[QA - Batch Record & Traceability]]) | `manufacture_production_log`, `batch_record`, `selisih_rm` | 0 | 16 (QA release time, waste pengolahan 1,5%, material loss mixing, kuantiti diluluskan ≥98%, realisasi produksi ≥98%, defect rate) |
| Training ([[HRIS - Training Program]]) | `training`, `training_participant` | 0 (`training_type` hanya 1) | 6 (Training Attendance Rate, keaktifan peserta, implementasi training) |
| Recruitment ([[Microservices - Recruitment Service]], [[HRIS - Recruitment]]) | `candidate`, `offer`, `onboarding_*` | 0 (`job_requisition` 2, `job_posting` 1) | 6 (Time to Fulfilment <30 hari, skor kompetensi new hire) |
| Repair history aset GA | `repair_history` | 0 | 1 |

> `BatchRecord` sudah membawa `TglSelesaiOlah`, `DiajukanAt`, `DisetujuiAt`, dan `Rekonsiliasi` (`shared-library/models/manufacture/models.go:398-470`). Begitu modul ini dipakai, **QA release time dan waste langsung terhitung tanpa menulis kode pengumpul data baru**.

## Tidak Ada Sumber Data (🔴, 144 metrik)

| Penyebab | Contoh metrik | Perkiraan |
|---|---|---:|
| **Tidak ada modul Kaizen / ide inovasi.** Diverifikasi: pencarian `kaizen` dan `inovasi` di seluruh `services/` dan `shared-library/` nol hasil | "Minimal 5 ide inovasi baru per kuartal" | 16 |
| Tidak ada log 1-on-1 | "Pertemuan 1-on-1 min. 1 per bulan per staf, 100% terdokumentasi" | 9 |
| **Meta/Facebook Ads tidak terintegrasi.** Integrasi iklan yang ada hanya TikTok Business/Shop, Shopee, Lazada, dan Accurate | ADV Meta: Conversion, CPA, ROI | 4 |
| Instagram dan TikTok organik akun company tidak terintegrasi | Company Branding: kenaikan engagement rate IG dan TikTok | 4 |
| Akun Buzzer memakai akun personal tanpa API | Early Engagement Speed, Engagement Quantity/Quality | 9 |
| Tidak ada data percakapan CS atau chat marketplace | Closing Rate, rate kecepatan respon chat toko | 4 |
| Tidak ada tracker pajak, SPT, audit internal, CAPA, atau izin BPOM ([[QA - Deviation & CAPA]], [[QA - BPOM & Izin Edar (NIE)]] masih konsep) | Kepatuhan pajak, SPT Masa H-1, Zero major finding BPOM, Closing Finding Rate | 18 |
| Tidak ada modul maintenance gedung, 5R, patroli security, kebersihan. `guestbook_entries` adalah buku tamu, **bukan** log patroli ([[GA - Building Maintenance]], [[GA - Checklist Management]] masih konsep) | Building & Maintenance, Office Boy Team, Security Team seluruhnya | 12 |
| Tidak ada skor maupun survei kepuasan training. `TrainingParticipant` hanya punya `Attended bool`, `Training` tidak punya field skor (`shared-library/models/employee/training.go:58-84`) | Skor Penilaian Training >70, Training Satisfaction Score, Employee Satisfaction | 4 |
| Tidak ada budget, forecast, MRP, atau succession plan ([[HRIS - Career & Promotion]] masih konsep) | Forecast cashflow ≥95%, MRP ≥95%, Factory Utilization, Succession Planning | 10 |
| Subjektif menurut sifatnya | kualitas konten, kerapihan dokumen, multitasking, responsivitas | 36 |

## Temuan Data Master

Perlu dibereskan sebelum otomasi apa pun, karena semuanya menyentuh label yang jadi kunci identitas metrik.

1. **Template uji ikut production**: `Beauty Hacks / Buzzer / "Buzzer"` berisi satu metrik berlabel `contoh`, deskripsi `contoh`, bobot 1.0. Akibatnya posisi Buzzer punya dua template dan dropdown scoring jadi ambigu.
2. **Metrik duplikat**: `Manufaktur / Warehouse Leader` memuat `Mencegah over-dispensing ...` dan `Mencegah over-dispensing ... 2` dengan deskripsi identik, total bobot 0,30 untuk hal yang sama.
3. **Label tidak deskriptif**: banyak template memakai `Performa 1/2/3/4`, `Administrasi 1/2/3/4`, `Aset dan Insidental 1..4`, `Kebersihan 1/2/3`. Makna sebenarnya hanya ada di kolom `description`.
4. **Label memakai target korporat, bukan metrik personal**: `Revenue 240M`, `Net Income 20%`, `Penurunan HPP 5%` dipakai sebagai label di posisi Staff Inventory, Tax Staff, dan QA RND.
5. **Dua departemen tanpa template**: Percetakan dan Marketing Offline Distribution.
6. **Engine otomasi yang sudah ada tidak tersambung ke HRIS**: [[Microservices - Insentive Service]] sudah menarik TikTok GMV-Max dan Shopee GMS lewat cron harian lalu menghitung `(realisasi / target) x bobot`, tetapi hasilnya masuk `incentive_results`, bukan `kpi_score`. Marketing mengetik ulang angka yang sudah dihitung mesin. Pemakaiannya di production juga masih minim (`incentive_results` 6, `master_kpis` 1, `employee_performance_mappings` 3).

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Supervisor / Leader | Penilai bawahan, semua departemen | `RequireKPIDepartmentRBAC`, atau `scope=team` bila punya bawahan langsung | Web |
| Staf HR (Training & Performance Officer) | Penjaga siklus bulanan dan rekap | Role `hris`, lolos untuk departemen mana pun | Web |
| Karyawan dinilai | Objek penilaian, pengunggah bukti | Baca skor sendiri di Portal Saya | Web, Mobile |
| Direktur / Stakeholder | Konsumen dashboard dan rekap lintas departemen | Lewat dashboard KPI | Web |

- **Tujuan**: supervisor ingin menilai cepat dan adil; HR ingin siklus tepat waktu dan angka dapat dipertanggungjawabkan.
- **Pain point**: metrik yang datanya sudah ada di ERP tetap diketik manual, sehingga rawan salah ketik dan sulit diaudit.
- **Aksi utama**: isi nilai 0..100 per metrik, unggah bukti, kirim per periode `YYYY-MM`.

## Metrik "skor tim" bukan satu kelompok

Enam belas baris metrik bertema monitoring tim tersebar di 15 posisi, tetapi **deskripsinya menyimpan lima maksud berbeda**. Menganggapnya satu kelompok adalah cara termudah salah mengotomatiskannya.

| Kelompok | Baris | Contoh posisi | Bisa diotomatiskan |
|---|---:|---|---|
| Supervisor cakupan departemen | 7 | Finance SPV, Quality SPV, Kyura SPV, Tech Dev SPV, BeautyHacks SPV, Manufacturing SPV, HRD SPV (kelompok HRGA) | ✅ jalur pertama |
| Supervisor lintas seluruh departemen | 1 | HRD SPV, "Performance Monitoring 100% Terimplementasi di Q4" | rumus berbeda, belum |
| Cakupan Leader (`work_data.supervisor_id`) | 3 | Leader Beauty Hacks, Leader Production, Tech Dev Leader | ✅ tanpa kode tambahan; bergantung pengisian `supervisor_id` yang sedang berjalan (2026-08-01: **54 dari 204**, Beauty Hacks 45, Tech Development 5, Human Resource 4) sehingga Leader Beauty Hacks sudah bisa terlayani sementara Leader Production belum ([[HRIS - Organization Structure]]) |
| Merujuk skor pemegangnya sendiri | 3 | Host Live BHS, Affiliate Kyura, Leader Kyura ("Skor final KPI tercapai sesuai target") | ❌ sirkular, tetap manual |
| Bukan skor tim | 2 | AR Leader & Senior Accountant, "Monitoring Team" = checker inputan + ketepatan tanggal | ❌ tetap manual |

Label keenam belas baris itu juga punya **enam varian penulisan**, termasuk satu berspasi di ujung (`Monitoring Team `) dan satu typo (`Perfomance Monitoring`). Karena label adalah kunci identitas metrik di kode, inilah alasan konkret kunci stabil dibutuhkan (lihat Fase 1 nomor 2).

## Matriks metrik per posisi (kandidat otomasi)

Label ditulis **persis** seperti tersimpan di `kpi_template` produksi, termasuk typo dan spasi, karena label adalah kunci identitas metrik di kode. Bobot dan target disalin apa adanya dari `weight` dan `description`. Daftar lengkap 311 metrik tidak disalin ke sini karena akan cepat basi; ia dibaca dari koleksi `kpi_template` (urutkan `department`, `position`).

### ICC (36 orang aktif, kandidat pertama)

Posisi terbesar yang dikaji: **Beauty Hacks 24 aktif dari 26, Kyura 12 aktif dari 15**. Dua departemen memakai template berbeda meski posisinya sama.

**Kyura, template `INTERNAL CONTENT CREATOR `**

| Bobot | Label | Target (dari deskripsi) | Sumber | Status |
|---:|---|---|---|---|
| 0,4 | `Kuantitas Video Konten` | 125 video/bulan | `tt_shop_video_performances.published_at` | ✅ |
| 0,2 | `Video Memenuhi Standar Struktur Indikator 10.000/video` | ≥ 70% atau min. 87 video | `gmv` per video ≥ 10.000 | ✅ |
| 0,4 | `Video Memenuhi Standar Struktur Indikator 150.000/video` | ≥ 30% atau min. 37 video | `gmv` per video ≥ 150.000 | ✅ |

**Beauty Hacks, template `INTERNAL CONTENT CREATOR`**

| Bobot | Label | Target | Sumber | Status |
|---:|---|---|---|---|
| 0,4 | `Jumlah Video` | 125 video/bulan | sama dengan Kyura | ✅ |
| 0,2 | `Video Memenuhi Standar Struktur Indikator VSA` | ≥ 70% atau min. 87 video | `mart_video_performance.sumber` = `vsa` | ⚠️ sumber berbeda |
| 0,4 | `Video Memenuhi Standar Struktur Indikator GMV MAX` | ≥ 30% atau min. 37 video | `mart_video_performance.sumber` = `gmv_max` | ⚠️ sumber berbeda |

Perhatikan bahwa angka `10.000` dan `150.000` pada Kyura adalah **ambang GMV**, sedangkan `VSA` dan `GMV MAX` pada Beauty Hacks adalah **jenis iklan**. Bobotnya kebetulan sama (0,2 dan 0,4) sehingga mudah dikira metrik yang sama; keduanya butuh sumber data yang berbeda.

**Ambangnya dibuktikan dari data, bukan ditafsirkan.** Untuk 10 toko Kyura sepanjang Juli 2026 (3.419 video):

| Tafsir | Hasil | Target | Layak? |
|---|---:|---:|---|
| `gmv` ≥ 10.000 | 37% | 70% | ✅ menantang tapi tercapai |
| `gmv` ≥ 150.000 | 20% | 30% | ✅ |
| `views` ≥ 10.000 | 3% | 70% | ❌ semua orang gagal selamanya |
| `views` ≥ 150.000 | 0% | 30% | ❌ |

**Atribusi**: lewat `icc_account_mappings.employee_id` → `tiktok_shop_id` → video toko itu. Berlaku karena satu orang memegang satu toko dan tokonya berbeda-beda. Jangan lewat kolom `team` di koleksi yang sama: kolom itu menulis `"Tech Development"` untuk sepuluh orang yang `work_data`-nya berkata `Kyura`.

Keadaan pemetaan per 2026-08-01: **Kyura 10 dari 12 aktif** (kurang Annisa Nurul Fadhilah `BIP-0086-09-24` dan Priyastama Wahyu Romadhoni `BIP-0169-06-25`); **Beauty Hacks praktis nol** (satu-satunya barisnya milik Aan Budiyanto dan sudah nonaktif).

**Skor manual saat ini meleset ke dua arah.** Perbandingan Juni 2026, skor tersimpan di `kpi_score` vs hasil hitung dari data video:

| Orang | Video Juni | Manual | Hitungan data | Selisih |
|---|---:|---:|---:|---:|
| Dika | 308 | 54,0 | 76,0 | +22,0 |
| Firdaus | 465 | 42,2 | 61,2 | +19,0 |
| Ryfanda | 147 | 45,4 | 63,4 | +18,0 |
| Ardiyansah | 155 | 40,0 | 52,0 | +12,0 |
| Fitriyah | 262 | 52,8 | 63,2 | +10,4 |
| Wiky | 684 | 44,3 | 54,2 | +9,9 |
| Burhanuddin | 178 | 41,1 | 50,2 | +9,1 |
| Putri | 319 | 45,4 | 43,4 | -2,0 |
| Silvia | 735 | 75,6 | 63,0 | -12,6 |
| Dzimar | **31** | 42,2 | **12,8** | **-29,4** |

Dua pola yang menjelaskannya, dan keduanya bukan kesalahan orang per orang:

- **Metrik `...10.000/video` diisi 0 untuk SEMUA orang, tiap bulan**, padahal 8% sampai 32% video tiap toko melewati ambang itu. Pola "semua nol, selalu" adalah ciri metrik yang tak seorang pun tahu cara menghitungnya.
- **Kuantitas video diisi 100 walau realisasinya jauh di bawah target**: Dzimar menerbitkan 31 dari 125 video (25%) tetapi dinilai penuh.

⚠️ **Belum diputuskan**: deskripsi berbunyi "≥ 70% **atau min. 87 video**". Perbandingan di atas hanya memakai sisi persentase. Bila cabang jumlah absolut ikut dihitung (ambil yang lebih menguntungkan), skor pemilik volume tinggi seperti Wiky (684 video) dan Silvia (735) naik lebih jauh.

### Kyura, posisi selain ICC

| Posisi | Bobot | Label | Status |
|---|---:|---|---|
| Kyura Supervisor | 0,6 | `Revenue 240M` | 🟡 deskripsi memuat **tiga** angka: label 240M, "Target Profit 546 jt", "Omset 4.090.000.000" |
| Kyura Supervisor | 0,05 | `Inventory turn over 90 days` | 🔴 tidak ada modul forecast |
| Kyura Supervisor | 0,05 | `Customer Satisfactions untuk Produk Beautyhacks 4,5 dari 5` | 🟡 rating toko tersedia, tapi **labelnya menyebut produk Beautyhacks di template Kyura** |
| Kyura Supervisor | 0,3 | `Performance Monitoring Team` | ✅ agregasi `kpi_score` departemen |
| Host Live | 0,7 · 0,3 | `Conversion` · `ROI` | ✅ GMV-Max dan `mart_profit_attribution` |
| Leader | 0,4 · 0,4 · 0,2 | `ROI` · `Conversion / OMZET` · `Perfomance Monitoring` | ✅ · ✅ · ❌ sirkular |
| Marketplace Advertiser | 0,5 · 0,5 | `Conversion` · `ROI` | ✅ |
| Affiliate | 0,4 · 0,4 · 0,2 | `Jumlah Affiliate Aktif` · `Conversion` · `Perfomance Monitoring` | 🟡 · ✅ · ❌ sirkular |
| Meta Advertiser | 0,5 · 0,5 | `Conversion` · `ROI` | ❌ Meta Ads tidak terintegrasi |
| Customer Support | 0,4 · 0,4 · 0,2 | `Perfoma` (rating toko) · `Kinerja` (respon chat) · `Kaizen` | ✅ · ❌ · ❌ |
| Buzzer | 5 metrik | `Early Engagement Speed` dst. | ❌ akun personal, tanpa API |

## Rencana Bertahap

Batas service dan kepemilikan datanya diputuskan di [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]: otomasi dikerjakan di dalam employee-service dulu, `kpi_score` tetap milik employee-service, dan pemisahan `kpi-collector` ditunda sampai pemicu yang tertulis di ADR terpenuhi.

**Fase 1, tanpa modul baru**
1. Sambungkan [[Microservices - Insentive Service]] ke `kpi_score` sebagai nilai berstatus DRAFT (kurang lebih 30 metrik Kyura dan Beauty Hacks). **Belum dikerjakan.**
2. **⚠️ Fondasinya sudah merge ke `main`, belum deploy** (PR #843 lalu PR #857): kontrak sumber nilai pada `KPIMetric`, kunci metrik stabil beserta migrasinya, `GET /kpi/auto-values`, stempel `auto_*` saat submit, mesin reduksi empat rumus, arah target naik/turun, dan registry sumber yang membuat kerja per departemen bisa paralel. Detail di [[Microservices - Employee Service]] dan cara memakainya di [[RUN - Menambah Metrik KPI Otomatis]].
	- Cakupan yang benar-benar tersentuh: **7 baris** supervisor level departemen, bukan 13 seperti tertulis di versi awal dokumen ini.
	- Belum menghasilkan apa pun sampai HR mengisi konfigurasi `auto` pada ketujuh metrik lewat `POST /kpi/templates`. Ini disengaja: tidak ada nama posisi yang di-hardcode, sehingga departemen atau perusahaan baru tidak menuntut ubah kode.
	- Frontend belum ada, jadi usulan sistem belum tampil di modal Score KPI.
3. **Auto-fill ICC (36 orang aktif) — posisi yang dipilih dikerjakan lebih dulu.** Belum dikerjakan. Rincian label, ambang, atribusi, dan perbandingan skor manual vs data ada di bab Matriks di atas. Dipotong dua: **Kyura 12 orang** (10 sudah terpetakan, satu sumber data) lalu **Beauty Hacks 24 orang** (butuh 24 pemetaan diisi dan sumber kedua `mart_video_performance.sumber` disambungkan).
4. Auto-fill metrik kedisiplinan dari `GET /attendance/report`. **Belum dikerjakan.**
5. Bersihkan data master sesuai bab Temuan Data Master.

> **Tech Development dikerjakan lebih dulu, tetapi bukan karena persentasenya tertinggi.** Persentase di tabel Rekap menghitung "sumber datanya ada", bukan "sumbernya cukup terisi".
>
> ⚠️ **Koreksi 2026-08-06.** Pemeriksaan kepadatan 2026-08-01 menyimpulkan SLA resolusi **0 dokumen** memenuhi syarat hitung. **Kesimpulan itu keliru**: sensusnya memakai nama field `completedAt` padahal BSON yang sebenarnya `completed_at`. Pembacaan ulang langsung ke `task_management_db` prod hari ini menemukan `completedAt` ada di **0 dokumen** dan `completed_at` di **220**, sehingga dari 307 tiket ada **271 ber-`due_date`** dan **214 terukur SLA resolusinya**. CSAT juga bertambah dari 8 menjadi **17**. Artinya yang tegak di Tech Development bukan 7 dari 30 metrik melainkan lebih banyak, dan alasan mendahulukannya tetap sah walau premis angkanya berubah.
>
> Alasannya dikerjakan duluan: ketujuhnya tidak menunggu siapa pun mengisi data. Uptime sudah terekam sendiri oleh Uptime Kuma, dan skor tim sudah ada di `kpi_score`. Bandingkan dengan ICC yang butuh tabel pemetaan diisi manual lebih dulu. Yang tersisa di Tech Development justru butuh orang mengubah kebiasaan — mengisi due date dan meminta rating tiap hari — dan itu bukan pekerjaan kode.
>
> **Tetapi hanya lima dari tujuh yang menyentuh orang.** Sensus 1 Agustus 2026: posisi `IT Infrastructure` **tidak punya karyawan sama sekali**, sehingga `System` 0,1 dan `Server` 0,1 menempel di template yang tak dipegang siapa pun. Yang tersisa mengenai **4 orang**: `IT Support` (2), `Tech Development Leader ` (1), `Tech Development Supervisor` (1). Sementara **7 developer** (2 Backend, 1 Frontend, 4 Fullstack) tidak tersentuh sama sekali. Rinciannya di [[HRIS - Matriks KPI per Departemen]].
>
> Temuan ikutan yang perlu ditangani tim IT terpisah dari KPI: **SLA resolusi tiket ternyata terukur, dan hasilnya buruk.** On-time rate Juli 2026 per space: System Finance 8,7% (2 dari 23), IT Support 30% (3 dari 10), MyBharata/HRIS 56,3% (9 dari 16), System Marketing 0% (0 dari 4). Ini angka yang perlu dibicarakan sebelum dipakai menilai orang, bukan sesudah.
>
> **Penghalang yang tersisa soal bentuk laporannya, bukan soal datanya**: rute `/report/*` di [[Microservices - Task Management Service]] hanya menerima `start_date` dan `end_date`, **tanpa penyaring per space**. Padahal KPI Leader IT memisahkan "E-Ticket Infra & IT Support" dari "E-Ticket Software Dev" sebagai dua metrik berbeda berbobot 20 masing-masing, dan space-nya di produksi memang sudah terpisah rapi (`IT Support` vs `MyBharata / HRIS`, `System Finance`, `System Marketing`, dan seterusnya). Datanya bisa dipisah lewat kueri; yang tak bisa adalah membacanya dari layar, karena rincian per space yang tersedia (`summary-by-department`) cuma total/open/done tanpa SLA maupun CSAT. Ditambah **skala CSAT 1–5 sedangkan ketiga KPI menargetkan skor 1–10**, sehingga konversinya perlu disepakati sebelum metrik apa pun disambungkan.

**Fase 2, perlu development ringan**
6. ~~Tambahkan penanda sumber pada `KPIMetric`~~ **sudah dikerjakan di Fase 1** (`auto_value` terpisah dari `value`, sumber diturunkan `SumberMetrik`). **Sisanya**: jejak **alasan** saat supervisor menimpa angka sistem, meniru `PATCH /results/:id/override` di insentive. Saat ini penimpaan hanya terdeteksi dari `value != auto_value`, tanpa alasan.
7. Normalkan label metrik. Kunci stabil sudah ada, jadi label kini **aman diganti** tanpa memutus konfigurasi otomatis.
8. Auto-fill Finance dari Accurate live proxy (13 metrik) dan Procurement (4 metrik). ⚠️ **Dimulai 2026-08-12, sebagian**: rumpun AR (`kinerja_ar`, piutang — sudah di `main`) dan **1 dari 3 metrik Account Payable** (`kinerja_ap`, "pembayaran tepat waktu" — PR [#1178](https://github.com/bip-itteam-internal/bip-erp/pull/1178) belum merge). Dua metrik AP lainnya (HPP, credit term) **tetap manual** setelah ditelusuri — lihat koreksi di atas. Belum ada konfigurasi `auto` yang diisi ke `kpi_template` untuk keduanya; kapasitasnya baru dibangun, belum menyala. Ditambah **dua metrik retur** pada sumber `kinerja_ar`, keduanya ✅ **live di produksi**: `retur_lewat_14_persen` (12 Agustus, "Penanganan retur di platform atau Expedisi") dan `retur_tuntas_cutoff_persen` (14 Agustus, "Pencatatan retur penjualan").

> ⚠️ **Pelajaran dari metrik retur: memilih jam mulai yang salah menghasilkan metrik yang tidak mengukur apa pun.**
>
> Rancangan pertama memakai **konfirmasi gudang** sebagai jam mulai, dengan alasan keadilan — orang finance tak boleh dinilai atas barang yang masih di jalan. Diuji ke data produksi, jeda scan-gudang→pembukuan ternyata rata-rata **9,6 jam** dengan maksimum **5,4 hari**, sementara ambang metriknya 14 hari. Maksimum yang pernah terjadi tak sampai separuh ambang, sehingga Juli **dan** Agustus 2026 sama-sama bernilai **100**. Yang terukur ternyata **worker otomatis**, bukan pekerjaan orang.
>
> Ini pola yang sama persis dengan metrik `uptime` yang dulu diganti `downtime`: realisasi wajar yang selalu jauh dari target berarti **metriknya salah bentuk, bukan salah angka**.
>
> Setelah jam mulai dipindah ke **tanggal retur** dan "selesai" didefinisikan sebagai terbukukan-atau-diterima-gudang, angkanya bergerak: Juli **27,6%** (nilai 18,1), Agustus **33,1%** (nilai 15,1). Yang sebelumnya terbuang dari perhitungan — retur yang **tak kunjung** selesai — justru yang dimaksud KPI-nya ("proses follow up retur lebih dari 14 hari"), dan datanya membenarkan: retur yang memang sampai tiba rata-rata **0,4 hari**, jadi yang menggantung 14 hari bukan sedang di perjalanan melainkan macet.
>
> Keadilan tetap dijaga, tetapi lewat **batas tenggat**: retur yang belum selesai dan usianya belum 14 hari menurunkan cakupan (`semi`), bukan dihitung telat.
>
> ✅ **Babak berikutnya (17 Agustus 2026, bip-erp PR [#1252](https://github.com/bip-itteam-internal/bip-erp/pull/1252) + erp-frontend PR [#1066](https://github.com/bip-itteam-internal/erp-frontend/pull/1066)): gerbang penolakan bulan-berjalan DIHAPUS, bukan digeser.** Dokumen ini sempat menyisakan pertanyaan terbuka — geser gerbangnya jadi "14 hari setelah periode tutup", atau sepakati jadwal penilaian tetap. Jawabannya ternyata bukan keduanya: instabilitas angka (selisih 25 poin Juli dibaca 1 vs 15 Agustus) **tidak hilang** dengan menahannya sampai tanggal tertentu, cuma memindahkan masalah. Bulan berjalan sekarang **diterima realtime**, dan keadilannya sepenuhnya dipikul cakupan `semi` yang sudah ada. Metrik `retur_tuntas_cutoff_persen` (Pencatatan) yang tak mengenal cakupan-per-retur mendapat mekanisme sendiri: cakupan **proporsional** ke seberapa jauh jendela `[awal periode, batas_cutoff]` sudah terlewati, selama tenggatnya sendiri belum lewat — supaya bulan berjalan tak terlihat 100% meyakinkan padahal belum pernah diuji tenggat sungguhannya.
>
> Ditambah **`Rincian`**: breakdown terstruktur `[]{label,nilai}` (Total retur, Sudah dapat dinilai/Terbukukan, Telat/Belum, dst., diformat pemisah ribuan) di balik kalimat `basis` yang sudah ada, dibuka lewat tombol "Lihat rincian" di modal Score KPI dan laman KPI Saya. Mekanismenya generik (`Cuplikan.Rincian` di `shared-library`, bukan khusus retur), jadi sumber KPI lain tinggal mengisinya untuk ikut dapat popup yang sama. Perbaikan hasil `/review` di PR yang sama: `Cuplikan.PopulasiNyata` mencegah metrik `skor_tim` yang kebetulan beranggota 1 orang kehilangan peringatan "(populasi 1)" — sebelumnya cuma metrik company-wide (retur, uptime) yang dimaksud disembunyikan jargonnya, tapi kondisinya (`Populasi<=1`) tak sengaja juga mencakup tim sungguhan beranggota satu.
9. Simpan budget/anggaran di ERP, karena saat ini tidak ada di mana pun.

**Fase 3, adopsi operasional bukan development**
10. Wajibkan pemakaian Production Log dan Batch Record (16 metrik), modul Training (6), modul Recruitment (6).

**Fase 4, fitur baru menurut frekuensi kemunculan**
11. Modul Kaizen / Ide Inovasi (16 metrik lintas departemen). **Sudah dirancang, lihat [[HRIS - Kaizen (Ide Perbaikan)]].** Kandidat lama "space khusus di [[Microservices - Task Management Service]]" **gugur** setelah diperiksa ke kode: jawaban pertanyaan per tipe di sana tidak disimpan sebagai data melainkan dirangkai jadi markdown di `description`, sehingga tidak bisa difilter atau dilaporkan per pertanyaan, padahal laporan per kategori dan hitungan kuota per periode justru inti fitur ini. Rumah yang dipilih: [[Microservices - Form Builder Service]] sebagai `form_type` kelima. Catatan penting soal metrik: sebagian metrik bernama Kaizen di matriks sebenarnya **bukan hitungan ide** (mis. "mengurangi jumlah CAPA produksi", "menjaga kualitas produk 98%"), jadi modul ini tidak menutup seluruh 16 metrik itu.
12. Log 1-on-1 (9 metrik), sejalan dengan konsep [[HRIS - Work Review]]. **Rumahnya sudah ditentukan**: mesin kewajiban berulang di **irisan 3** [[Microservices - Calendar Service]] (belum ada kode), yang menyalin pola `FormPeriod` [[Microservices - Form Builder Service]]. Metrik Fullstack "Monitoring Kegiatan Sinkronisasi/Review dengan Requester" (bobot 0,2) menunggu irisan yang sama.
13. Field skor dan survei kepuasan pada modul Training (4 metrik).
14. Checklist operasional berjadwal untuk patroli, 5R, GMP, dan preventive maintenance. Satu modul menutup General Affair, Quality, dan Warehouse sekaligus (kurang lebih 20 metrik). Lihat [[GA - Checklist Management]].

**Yang sebaiknya tetap manual**: kurang lebih 36 metrik memang subjektif. Untuk kelompok ini yang perlu diperbaiki adalah rubrik penilaian, bukan otomasi; fitur lampiran bukti `/kpi/evidence` sudah tepat sasaran.

## Catatan Akurasi

Field `attribution_note` pada `mart_profit_attribution` di production menyatakan retur **tidak dapat diatribusikan ke level iklan** (laporan iklan tidak membawanya dan order tidak menyimpan campaign/ad/video id), dan dasar laba memakai gross revenue laporan iklan, bukan settlement bersih. Konsekuensinya ROI/ROAS otomatis di level iklan akan lebih optimis dari kenyataan. Bila angka ini dipakai untuk KPI yang berdampak ke insentif, pakai level toko atau produk, atau tampilkan disclaimer di UI.

## Belum Diimplementasikan / Catatan

- **308 dari 311 metrik masih diisi manusia.** Tiga yang otomatis sejak 2026-08-06 ada di bab **Metrik otomatis yang sudah menyala**. Sisanya menunggu konfigurasi `auto` pada `kpi_template`, yang diisi lewat `POST /kpi/templates` tanpa perlu deploy.
- ⚠️ **Sudah basi**: catatan lama "frontend produksi belum menampilkan usulan sistem". FE prod di-deploy ulang **6 Agustus 19:02 WIB** sesudah #831 merged, jadi modal Score KPI produksi sudah memuat `auto-values` (lihat bab Deskripsi). Yang **belum** di produksi adalah form konfigurasi otomasi #832 beserta backend pendukungnya — bab **HR mengisi konfigurasinya sendiri**.
- 🔴 **`shopee_shop_id` kosong di seluruh 12 baris `icc_account_mappings`**, sehingga metrik bersumber `kinerja_toko` hanya terhitung dari toko TikTok (± 80% omzet). Pekerjaan data tim marketing; tanpa catatan ini angka KPI ICC akan terbaca sebagai kinerja buruk. Rinciannya beserta angka per channel di bab **Yang harus diketahui sebelum angkanya dipercaya**.
- 🔴 **bip-erp PR #1058 (`tim_icc`) bertanda MERGED tetapi isinya tidak ada di `main`** — ter-merge ke branch PR #1053 yang sudah lebih dulu masuk `main` 39 detik sebelumnya. Metrik team Leader ICC karena itu masih tak dapat dihitung. Detail di bab **Cakupan `tim_icc`**.
- ⚠️ ~~**Di DEV, `MONITORING_SERVICE_KEY` dan `MARKETING_ANALYTICS_SERVICE_KEY` kosong** (diperiksa 2026-08-06)~~ **Koreksi 2026-08-22: `MARKETING_ANALYTICS_SERVICE_KEY` kini TERISI di dev (32 karakter).** Diverifikasi langsung: `/kpi/kinerja-toko` dan `/kpi/kinerja-affiliate` menghasilkan angka nyata di dev (mis. tim ICC Kyura, dan conversion affiliate per-individu). Jadi uji end-to-end otomasi KPI di dev **sudah bisa** — catatan lama "mustahil menghasilkan angka di dev" tak lagi berlaku untuk marketing-analytics. (Status `MONITORING_SERVICE_KEY` di dev tak diperiksa ulang.)
- **Uptime bulan Juni 2026 dan sebelumnya tidak dapat dihitung.** Diverifikasi di produksi 1 Agustus 2026: Juni membalas `null` dengan 0 dari 30 hari, Juli 99,81% dengan 23 dari 31 hari (membenarkan heartbeat terawal 9 Juli). Agustus adalah periode penuh pertama.
- **Selama bulan berjalan, metrik uptime akan dilaporkan `semi`, bukan `otomatis`.** Cakupannya memang belum penuh, dan uptime satu hari bukan uptime sebulan. Ia menjadi `otomatis` setelah bulannya tutup, yaitu saat penilaian dilakukan.
- **`System uptime` dan `Server uptime` belum dapat dibedakan.** Seluruh monitor bertipe `docker` (33) dan `http` (1); memisahkannya butuh monitor tingkat host di Kuma, pekerjaan tim IT.
- Sumber ROI/ROAS otomatis berasal dari [[Microservices - Marketing Analytics Service]] (didokumentasikan 2026-07-31, sebelumnya service ini berjalan di production tanpa dok). Perlu diperhatikan: `/lives`, `/cohort`, dan `/price-floor` masih membalas kosong karena koleksinya belum terisi, dan `/matrix/sku-shop` masih stub. Konteks bisnisnya di [[Sales - Marketing Dashboard (Master Roadmap)]].
- Angka sensus adalah snapshot 2026-07-31 dan akan bergeser. Cara memperbarui daftar template per posisi tanpa menebak: baca koleksi `kpi_template` pada database `employee_db`, urutkan berdasarkan `department` lalu `position`. Kredensial Mongo diambil dari environment container, jangan ditulis di dokumen.

## Dependensi & Integrasi

- **Sumber skor manual**: [[Microservices - Employee Service]] (`/kpi/*`), FE di [[APP - Web ERP]]
- **Sumber otomatis yang sudah terpasang**: [[Microservices - Monitoring Service]] (`uptime_sistem`) · [[Microservices - Employee Service]] sendiri (`skor_tim`) · [[Microservices - Form Builder Service]] (`kaizen`) · [[Microservices - Marketing Analytics Service]] (`kinerja_toko`, PR #1042) · [[Microservices - Integration Service]] (`kinerja_ar` — piutang rumpun AR Finance di `main` sejak 11 Agustus 2026; metrik retur `retur_lewat_14_persen` (12 Agustus) dan `retur_tuntas_cutoff_persen` (14 Agustus) keduanya ✅ live, realtime bulan-berjalan + popup Rincian sejak PR [#1252](https://github.com/bip-itteam-internal/bip-erp/pull/1252) 17 Agustus 2026).
  - [[Microservices - Task Management Service]] (`kinerja_tiket`, PR #1055 merged & di-deploy 6 Agustus 2026 — bukan lagi "sedang dikerjakan"). Tiga metrik dari satu agregat: `ontime` (ketepatan waktu penyelesaian, dipasangkan `rasio_ambang` ambang 0), `csat` (kepuasan pemohon skala 1..5, dinyatakan sebagai target 5 sehingga **tidak perlu konversi skala** walau KPI menulis "rating 10 dari 1-10"), dan `selesai_persen`. Rincian keputusan penyebutnya di [[API - Task Management Service]]
- **Sumber yang sedang dikerjakan** 🟡: [[Microservices - Procurement Service]] (`kinerja_ap`, tren pembayaran Account Payable, PR [#1178](https://github.com/bip-itteam-internal/bip-erp/pull/1178) belum merge). Satu metrik: `pembayaran_tepat_waktu_persen` — lihat koreksi di bab "Peta Metrik" di atas untuk kenapa cuma satu dari tiga metrik Account Payable yang tergarap.
- 🟡 [[Microservices - Integration Service]] (`kinerja_sales_admin`, PR [#1254](https://github.com/bip-itteam-internal/bip-erp/pull/1254) belum merge). Satu metrik: `penjualan_tuntas_cutoff_persen` untuk "Pencatatan Penjualan" (KPI Sales Admin, bobot 0,5) — ketuntasan pembukuan faktur harian pada tenggat tutup buku, sepasang dengan `retur_tuntas_cutoff_persen` tapi sumber TERPISAH: AR Staf sesungguhnya memegang tiga template KPI berbeda (Piutang, Retur, Sales Admin), bukan satu posisi satu template. "Rekonsiliasi stok penjualan" (bobot 0,3) tetap manual, menunggu kesepakatan definisi selisih dan batas waktunya.
- **Kandidat sumber otomatis**: [[Microservices - Insentive Service]] · [[Microservices - Integration Service]] · [[Microservices - Attendance Service]] · [[Microservices - Task Management Service]] · [[Microservices - Procurement Service]] · [[Microservices - Warehouse Service]] · [[Microservices - Inventory Service]] · [[External - Accurate]] · [[IT - Monitoring System]]
- **Terblokir adopsi**: [[Microservices - Manufacture Service]] · [[Microservices - Recruitment Service]] · [[HRIS - Training Program]]
- **Penjadwalan**: [[IT - Background Jobs & Schedulers]]
- **Struktur atasan-bawahan** untuk agregasi skor tim: [[HRIS - Organization Structure]]
- **Koleksi**: [[DB - Overview and Notes]]

## Dokumen Terkait

- [[HRIS - Alur KPI Otomatis.excalidraw]] (diagram Excalidraw, penjelasan untuk non-teknis: rangkaiannya dan tiga syarat yang sering terlupa)
- [[HRIS - Pengumpulan Data KPI Otomatis.excalidraw]] (diagram Excalidraw untuk dev: di mana data ditampung sepanjang bulan, kapan dihitung, kapan angkanya beku, dan kapan snapshot harian memang perlu)
- [[HRIS - Key Performance Index]] (mekanisme scoring, RBAC, cakupan tim Leader)
- [[HRIS - Work Review]] (rencana menyatukan KPI kuantitatif dengan review kualitatif)
- [[HRIS - Career & Promotion]] · [[HRIS - Personalia]] · [[HRIS - Attendance System]]
- [[HRIS - Analysis]] · [[HRIS - Big Pictures]] · [[HRIS - Interrelationship Matrices]] · [[HRIS - Roadmap]]
- [[Finance - Incentive]] · [[Sales - Incentive]]
- [[REF - Glossary]]
