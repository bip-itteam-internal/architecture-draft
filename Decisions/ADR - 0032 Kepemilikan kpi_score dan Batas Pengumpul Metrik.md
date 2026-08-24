**Status**: ⚠️ Diputuskan 2026-07-31; keputusan pokoknya **tetap berlaku**, tetapi catatan status lamanya sudah basi. Fondasinya **sudah merge dan sudah deploy** ke produksi 1 Agustus 2026 (PR #843/#857/#866), dan **tiga metrik Tech Development benar-benar terisi otomatis di produksi sejak 6 Agustus 2026** — kalimat lama "branch `feat/kpi-auto-value` belum merge, belum deploy" dan "tidak ada satu pun metrik KPI yang terisi otomatis" **sudah tidak berlaku**. Sejak itu otomasi berkembang jauh melampaui Fase 1 yang dibayangkan ADR ini; ringkasannya di bab **Perkembangan sesudah keputusan** di bawah. Analisis yang mendasarinya ada di [[HRIS - Otomasi Skor KPI]].

> **Penyempitan yang disepakati saat implementasi Fase 1**: butir 4 di bawah menyebut pintu masuk berupa **endpoint tulis**. Fase 1 justru **menghitung di sisi baca** (`GET /kpi/auto-values`, plus stempel saat submit `POST /kpi`), dan itu disengaja. Alasannya ada di kode yang sudah berjalan: `ApplyKPIValues` menolak submit yang tak memuat SELURUH label, dan `POST /kpi` menimpa dokumen skor dengan `ReplaceOne`, sehingga nilai yang dititipkan terpisah pasti tersapu pada submit berikutnya. Endpoint tulis tetap berlaku untuk Fase 2, saat collector eksternal benar-benar ada. Keputusan pokoknya (kepemilikan data, satu pintu bergerbang, DRAFT) tidak berubah.

## Perkembangan sesudah keputusan

Ditambahkan 2026-08-11, grounded ke `origin/main` bip-erp. Bab ini **tidak mengubah keputusannya**; ia mencatat bahwa dua premis angka di dalamnya sudah lewat.

**Pemicu ekstraksi collector di butir 6 SUDAH TERLAMPAUI, dan pemisahannya tetap tidak dikerjakan.** Butir 6 menetapkan tiga konektor keluar sebagai salah satu pemicunya. Konektor keluar employee-service yang benar-benar terdaftar di `main` kini **empat**, seluruhnya lewat `os.Getenv` ke modul lain, bukan lewat `InternalURL`:

| Sumber | Berkas | Menarik dari |
|---|---|---|
| `uptime_sistem` (metrik `uptime`, `downtime`) | `kpi_sumber_uptime.go` | `MONITORING_MODULE_URL` — [[Microservices - Monitoring Service]] |
| `kaizen_ide_diajukan`, `kaizen_ide_diterapkan` | `kpi_sumber_kaizen.go` | `FORM_BUILDER_MODULE_URL` — [[Microservices - Form Builder Service]] |
| `kinerja_toko` (7 metrik) | `kpi_sumber_kinerja_toko.go` | `MARKETING_ANALYTICS_MODULE_URL` — [[Microservices - Marketing Analytics Service]] |
| `kinerja_tiket` (3 metrik) | `kpi_sumber_tiket.go` | `TASK_MANAGEMENT_MODULE_URL` — [[Microservices - Task Management Service]] |
| `kedisiplinan_absensi` (2 metrik) | `kpi_sumber_kedisiplinan.go` | `ATTENDANCE_MODULE_URL` + `ATTENDANCE_SERVICE_KEY` — [[Microservices - Attendance Service]] |

Ditambah `skor_tim` yang membaca `kpi_score` employee-service sendiri (bukan konektor keluar), dan `akurasi_aset_ga` (`kpi_sumber_aset.go`) yang menarik dari **dua** modul sekaligus (inventory dan integration) — jadi begitu ia masuk, hitungannya menjadi enam.

**Per 22 Agustus 2026 hitungannya bertambah lagi**, dan justru ke arah yang membuat pertanyaan di bawah makin tajam. PR [#1379](https://github.com/bip-itteam-internal/bip-erp/pull/1379) menambah tiga sumber sekaligus: `kedisiplinan_absensi` (konektor keluar, sudah masuk tabel), plus `turnover_karyawan` (`kpi_sumber_turnover.go`) dan `kontrak_karyawan` (`kpi_sumber_kontrak.go`) yang **membaca `employee_db` sendiri** sehingga bukan konektor keluar. Total sumber terdaftar kini **18**, diverifikasi lewat `GET /kpi/sumber-katalog` di produksi.

Yang menarik dari ketiganya: dua di antaranya tidak menambah beban lintas-service sama sekali, dan yang satu memakai ulang pipeline HTTP yang polanya sudah ada. Ongkos yang dikhawatirkan ADR ini tetap tidak muncul.

**Yang belum diputuskan: apakah angka tiga masih pemicu yang bermakna.** Dua pemicu lainnya belum terpenuhi — tak ada penjadwalan di luar siklus HR (perhitungan tetap on-read, tak ada cron KPI), dan employee-service belum menyimpan kredensial non-HR (yang dipegangnya hanya kunci layanan per-service, bukan token iklan atau kredensial Accurate). Ongkos yang dikhawatirkan ADR ini ternyata tidak muncul: tiap konektor adalah satu berkas `kpi_sumber_*.go` yang tak menyentuh berkas milik orang lain, dan registry `DaftarkanSumber` memang dirancang supaya begitu. **TBD**: apakah pemicu konektor dicabut dan diganti pemicu yang benar-benar mengukur beban (mis. lama respons `GET /kpi/auto-values`, atau jumlah panggilan HTTP serial per permintaan), atau pemisahan memang dijalankan sekarang.

**Butir 3 dan 5 sudah dijalankan; butir 4 masih berbeda dari kenyataan.** Endpoint tulis bergerbang di butir 4 tetap tidak ada — perhitungan tetap di sisi baca, sesuai penyempitan yang dicatat di blockquote atas. `auto_value` terpisah dari `value` sudah berjalan (butir 3), dan supervisor tetap memverifikasi sebelum menyimpan (butir 5). **Jejak alasan saat supervisor menimpa angka sistem masih belum ada**; penimpaan hanya terdeteksi dari `value != auto_value`.

**Konfigurasi otomatis kini punya jejak perubahannya sendiri** (`kpi_template_audits`, PR [#1053](https://github.com/bip-itteam-internal/bip-erp/pull/1053)) — koleksi terpisah di `employee_db`, jadi kepemilikan datanya tak berubah. Rincian dan batasnya di [[HRIS - Otomasi Skor KPI]].

## Context

Penilaian KPI per karyawan sudah berjalan di produksi lewat [[Microservices - Employee Service]]: 70 template, 311 metrik, 11 departemen, 406 skor tersimpan sejak Maret 2026. **Seluruh nilainya diketik manusia.** `ApplyKPIValues` hanya menerima map `label -> 0..100` dari body request; tidak ada jalur pengisian otomatis (`shared-library/models/employee/models.go:411`).

Audit 2026-07-31 terhadap 311 metrik menemukan **132 metrik (42,5%) sumber datanya sudah ada di ERP dan terisi di produksi**. Masalahnya, sumber itu tersebar di banyak service: integration (laporan iklan TikTok, retur, ulasan), [[Microservices - Marketing Analytics Service]] (laba dan ROAS), [[Microservices - Attendance Service]] (kehadiran dan keterlambatan), [[Microservices - Task Management Service]] (SLA dan CSAT), [[IT - Monitoring System]] (uptime), procurement (lead time PO), dan [[External - Accurate]] (laporan keuangan). Dari situ muncul pertanyaan yang memicu ADR ini: **apakah otomasi KPI perlu service sendiri?**

Fakta yang membatasi jawabannya:

- **Datanya sudah punya pemilik.** `kpi_template` dan `kpi_score` berada di `employee_db`, satu database dengan `work_data` yang menyediakan posisi, departemen, dan `supervisor_id`. Model dan aturan bobotnya di `shared-library/models/employee/models.go:351-408`.
- **employee-service sudah yang terbesar**: 139 rute terdaftar dan `main.go` sepanjang 5.916 baris.
- **Tapi employee-service memang sudah memanggil service lain.** `InternalURL` sudah terpasang dan dipakai ke attendance (`services/employee/main.go:81`, `:88`, `:3348`) dan file-service (`:3392`). Menambah satu panggilan bukan kapabilitas baru.
- **Dua aksi otomasi paling bernilai nyaris tanpa dependensi keluar.** Metrik "Performance Monitoring Team" muncul di 13 posisi supervisor dan leader, dan menghitungnya hanya perlu mengagregasi `kpi_score` terhadap `work_data.supervisor_id`, keduanya di `employee_db`. Metrik kedisiplinan hanya butuh satu panggilan ke attendance yang jalurnya sudah ada.
- **Sudah ada engine yang menghitung skor tapi menulis ke tempat lain.** [[Microservices - Insentive Service]] menarik TikTok GMV-Max dan Shopee GMS lewat cron harian lalu menghitung `(realisasi / target) x bobot`, tetapi hasilnya masuk `incentive_results`, bukan `kpi_score`. Akibatnya angka yang sudah dihitung mesin tetap diketik ulang di modul HRIS. Pemakaiannya di produksi juga masih minim: `incentive_results` 6 dokumen, `master_kpis` 1, `employee_performance_mappings` 3.
- **Ongkos memisah service sudah terukur di repo ini.** [[Microservices - Marketing Analytics Service]] dibuat persis untuk bentuk masalah yang sama (agregasi lintas sumber, baca-saja database service lain, mart pre-agregasi, job dipicu). Biayanya nyata: 80+ berkas, replica set sendiri, migrasi index unik yang harus dijalankan manual saat deploy, dan sampai hari ini **belum punya scheduler sendiri** serta lock job yang **hanya berlaku dalam satu proses** sehingga belum aman di-scale horizontal.
- **`hris-orchestrator` bukan tempatnya.** Isinya `employee_route.go`, `attendance_route.go`, `employee_multicollection_route.go`, `transactions.go`: lapisan komposisi request untuk frontend, bukan wadah job periodik.

## Decision

**`employee_db` tetap satu-satunya pemilik `kpi_template` dan `kpi_score`. Otomasi dikerjakan di dalam employee-service dulu; pemisahan service ditunda sampai pemicu yang tertulis di bawah terpenuhi.**

1. **Tidak ada service lain yang menulis ke `employee_db`.** Konsisten dengan [[ADR - 0002 Database-per-Service]]. Ini berlaku juga untuk insentive-service: hasil hitungnya masuk lewat HTTP, bukan tulis langsung.
2. **Fase 1 dikerjakan di employee-service, tanpa service baru.** Cakupannya metrik yang sumbernya `employee_db` sendiri (agregasi skor tim) dan satu konektor yang jalurnya sudah ada (attendance).
3. **Kontrak nilai otomatis dipasang lebih dulu, sebelum konektor apa pun.** `KPIMetric` mendapat penanda sumber dan `auto_value` yang **terpisah** dari `value`. Nilai sistem tidak pernah menimpa nilai manusia diam-diam, dan override supervisor wajib berjejak alasan, meniru pola `PATCH /results/:id/override` yang sudah ada di insentive-service. Kontrak inilah yang membuat keputusan batas service dapat ditunda tanpa rework.
4. **Nilai otomatis masuk lewat satu pintu bergerbang**, yaitu satu endpoint internal di employee-service, bukan penulisan langsung ke koleksi dari mana pun. Sesuai [[ADR - 0031 Prefix internal Bukan Batas Keamanan]], endpoint itu **wajib menggerbangi dirinya sendiri**; prefix `/internal/` tidak memberi jaminan apa pun.
5. **Nilai otomatis berstatus DRAFT, bukan final.** Supervisor tetap memverifikasi sebelum skor periode ditutup, sama seperti alur DRAFT lalu approve di insentive-service.
6. **Pemicu ekstraksi `kpi-collector` sebagai service terpisah**, dipenuhi salah satu saja sudah cukup:
    - konektor keluar dari employee-service mencapai **tiga**, atau
    - dibutuhkan **penjadwalan yang bukan milik siklus HR** (mis. tarikan harian mengikuti jam sync marketplace, bukan tanggal 1 bulan berjalan), atau
    - employee-service mulai perlu **menyimpan kredensial atau akses sistem non-HR** (token iklan, kredensial Accurate).
   Saat dipisah, collector membaca sumber lalu **menyetor** nilai lewat endpoint di butir 4. Kepemilikan `kpi_score` tidak ikut pindah.

**Yang ditolak beserta alasannya:**

- **Membuat service KPI sekarang.** Akan memaksa salah satu dari dua hal: menulis lintas database (melanggar [[ADR - 0002 Database-per-Service]]) atau memigrasi `kpi_template` dan `kpi_score` yang sudah dipakai empat periode berjalan. Keduanya membayar ongkos marketing-analytics tanpa mendapat manfaatnya, karena dua aksi Fase 1 justru tidak punya dependensi keluar.
- **Menaruh job otomasi di `hris-orchestrator`.** Mencampur lapisan komposisi request dengan pekerjaan periodik.
- **Menjadikan insentive-service pemilik KPI.** Domainnya sendiri (insentif 9 role marketing) dan hanya menutup sekitar 30 dari 311 metrik.

## Consequences

**Konsekuensi yang diterima:**

- **employee-service bertambah besar dulu sebelum mengecil.** Ini disengaja: menunda pemisahan sampai bentuk konektornya diketahui lebih murah daripada menebak batas service di awal, lalu salah.
- **`auto_value` terpisah dari `value` berarti dua field yang harus dibedakan frontend.** Menggabungkannya akan menghapus kemampuan menjawab "angka ini dari mesin atau dari atasan", yang justru alasan utama otomasi ini dilakukan.
- **Template di-snapshot ke `kpi_score` saat submit**, sehingga skor lampau beku. Nilai otomatis yang dihitung ulang belakangan **tidak retroaktif**, dan itu perilaku yang memang diinginkan.
- **Nilai otomatis tetap perlu verifikasi manusia**, jadi otomasi ini mengurangi pengetikan dan salah ketik, bukan menghapus peran supervisor.

**Yang belum dikerjakan:**

- ⚠️ **Sudah basi**: kalimat lama "seluruh Fase 1 sampai Fase 4 masih rencana". Fase 1 butir 2 **selesai dan deploy**; enam sumber terdaftar, tiga metrik menyala di produksi. Yang masih rencana: penyambungan insentive-service ke `kpi_score` (Fase 1 butir 1), auto-fill ICC (butir 3), auto-fill kedisiplinan (butir 4), dan seluruh Fase 2 sampai 4. Status per fase yang mutakhir dipelihara di [[HRIS - Otomasi Skor KPI]], bukan di sini.
- **Pemetaan karyawan ke toko atau advertiser belum memadai.** Metrik marketing bersifat per toko, per kampanye, atau per video, sedangkan KPI dinilai per orang. Satu-satunya pemetaan yang ada, `employee_performance_mappings` di insentive-service, berisi **3 dokumen** di produksi. Tanpa membereskan ini, metrik iklan tidak dapat dibebankan ke orang yang tepat walaupun angkanya sudah tersedia.
- **Label metrik belum layak dijadikan kunci otomasi.** Label adalah identitas unik metrik di kode, tetapi produksi memuat label seperti `Performa 1/2/3`, `Administrasi 1/2/3/4`, dan `Revenue 240M` yang maknanya hanya ada di kolom deskripsi. Ada pula satu template uji (`Beauty Hacks / Buzzer / "Buzzer"` berisi metrik `contoh` bobot 1.0) dan satu metrik duplikat (`Warehouse Leader`, over-dispensing tercatat dua kali). Pembersihan ini prasyarat, bukan pekerjaan kosmetik.
- **Insentive-service belum menyetor hasilnya ke `kpi_score`**, sehingga duplikasi pengetikan untuk tim marketing masih berlangsung.

**Yang belum diputuskan (TBD):**

- Nama dan cakupan pasti `kpi-collector` bila pemicunya terpenuhi, termasuk apakah ia juga mengambil alih cron insentive-service atau berdampingan.
- Apakah metrik "SLA Pengumpulan KPI tepat waktu" pada posisi Training & Performance Officer masih bermakna setelah sebagian pengisian menjadi otomatis.
- Bagaimana menandai periode yang skornya **sebagian** otomatis dan sebagian manual, agar perbandingan antar periode tidak menyesatkan.
- Apakah nilai otomatis boleh mengisi ulang periode yang sudah lewat saat konektor baru dipasang, atau hanya berlaku maju.

## Terkait

- [[HRIS - Otomasi Skor KPI]] (analisis 311 metrik ke sumber datanya, dasar keputusan ini)
- [[HRIS - Key Performance Index]] (mekanisme scoring, RBAC per departemen, cakupan tim Leader) · [[HRIS - Work Review]]
- [[Microservices - Employee Service]] (pemilik `kpi_template` dan `kpi_score`)
- [[Microservices - Insentive Service]] (engine skor yang sudah ada, menulis ke `incentive_results`)
- [[Microservices - Marketing Analytics Service]] (preseden ongkos memisah service agregasi)
- [[Microservices - Attendance Service]] · [[Microservices - Task Management Service]] · [[IT - Monitoring System]] · [[External - Accurate]] (calon sumber)
- [[CORE - HRIS Orchestrator]] (lapisan komposisi, sengaja tidak dipakai untuk job)
- [[ADR - 0002 Database-per-Service]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
- [[IT - Background Jobs & Schedulers]] · [[DB - Overview and Notes]] · [[APP - Web ERP]]
