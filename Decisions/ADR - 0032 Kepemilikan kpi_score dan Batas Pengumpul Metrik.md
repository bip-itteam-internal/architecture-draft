**Status**: 🟡 Diputuskan 2026-07-31, **belum diimplementasikan**. Tidak ada satu pun metrik KPI yang terisi otomatis hari ini. Analisis yang mendasarinya ada di [[HRIS - Otomasi Skor KPI]].

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

- Seluruh Fase 1 sampai Fase 4 di [[HRIS - Otomasi Skor KPI]] masih rencana.
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
