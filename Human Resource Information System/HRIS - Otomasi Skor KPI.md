## Deskripsi

*Analisis kelayakan **mengisi skor KPI secara otomatis** dari data yang sudah dimiliki ERP, bukan diketik manual oleh supervisor. Menjawab: dari 311 metrik yang benar-benar terpasang di production, mana yang sumber datanya sudah ada, mana yang modulnya ada tapi belum dipakai, dan mana yang memang tidak punya sumber sama sekali. Melengkapi [[HRIS - Key Performance Index]] yang menjelaskan mekanisme scoring-nya.*

- **Status**: ⚠️ Mesin dan sumber pertamanya **sudah jalan di produksi** (PR #843 kontrak sumber nilai, #857 mesin reduksi + arah target + registry sumber, #866 sumber `uptime_sistem`; deploy 1 Agustus 2026 dan terverifikasi terhadap `kuma.db` sungguhan). **Tetapi belum ada satu pun metrik yang terisi otomatis**, karena belum satu pun `kpi_template` diisi konfigurasi `auto`-nya — itu pekerjaan data, bukan kode. Departemen pertama yang dikerjakan: **Tech Development**. **Inventaris sumber datanya ✅ grounded** ke kode `origin/main` bip-erp commit `23c6bdc8` dan sensus dokumen 15 database production per **2026-07-31**.
- **Ruang lingkup**: `kpi_template` / `kpi_score` di [[Microservices - Employee Service]]. **Bukan** engine insentif marketing di [[Microservices - Insentive Service]], walau bab 6 mengusulkan menyambungkan keduanya.

## Kondisi Saat Ini

Seluruh 311 metrik diisi manusia. Tidak ada jalur auto-fill di kode.

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
| Uptime server dan sistem | IT Infrastructure, IT Support, Tech Leader/SPV | Sumber `uptime_sistem` memanggil `GET /monitoring/kpi/uptime?periode=YYYY-MM` ([[Microservices - Monitoring Service]]). Jendela berjalan `GET /monitors` TIDAK dipakai untuk KPI: "30 hari terakhir" bukan nilai bulan mana pun | 34 monitor; heartbeat baru sejak 9 Juli 2026 |
| SLA e-ticket | IT Support, Backend/Frontend Developer | `GET /task-management/report/sla`, field `on_time_rate` untuk response dan resolution (`services/task-management/sla.go:112-159`) ([[IT - Helpdesk]]) | 293 task |
| CSAT layanan IT | IT Support, Fullstack, Tech Leader | `GET /report/csat`, `GET /report/manpower-performance` (`avg_csat` per orang, `services/task-management/report_handlers.go:160-232`) | tersedia |
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

> **Tech Development dikerjakan lebih dulu, tetapi bukan karena persentasenya tertinggi.** Persentase di tabel Rekap menghitung "sumber datanya ada", bukan "sumbernya cukup terisi. Pemeriksaan kepadatan 2026-08-01 menunjukkan bedanya: CSAT hanya **8 tiket ter-rating seumur hidup**, dan SLA resolusi **0 dokumen** memenuhi syarat hitung (`due_date` dan `completedAt` tak pernah terisi bersamaan dari 293 task). Yang benar-benar tegak di sana **7 dari 30 metrik**: lima uptime dan dua skor tim.
>
> Alasannya dikerjakan duluan: ketujuhnya tidak menunggu siapa pun mengisi data. Uptime sudah terekam sendiri oleh Uptime Kuma, dan skor tim sudah ada di `kpi_score`. Bandingkan dengan ICC yang butuh tabel pemetaan diisi manual lebih dulu. Yang tersisa di Tech Development justru butuh orang mengubah kebiasaan — mengisi due date dan meminta rating tiap hari — dan itu bukan pekerjaan kode.
>
> **Tetapi hanya lima dari tujuh yang menyentuh orang.** Sensus 1 Agustus 2026: posisi `IT Infrastructure` **tidak punya karyawan sama sekali**, sehingga `System` 0,1 dan `Server` 0,1 menempel di template yang tak dipegang siapa pun. Yang tersisa mengenai **4 orang**: `IT Support` (2), `Tech Development Leader ` (1), `Tech Development Supervisor` (1). Sementara **7 developer** (2 Backend, 1 Frontend, 4 Fullstack) tidak tersentuh sama sekali. Rinciannya di [[HRIS - Matriks KPI per Departemen]].
>
> Temuan ikutan yang perlu ditangani tim IT terpisah dari KPI: **SLA resolusi tiket saat ini tidak terukur sama sekali.**

**Fase 2, perlu development ringan**
6. ~~Tambahkan penanda sumber pada `KPIMetric`~~ **sudah dikerjakan di Fase 1** (`auto_value` terpisah dari `value`, sumber diturunkan `SumberMetrik`). **Sisanya**: jejak **alasan** saat supervisor menimpa angka sistem, meniru `PATCH /results/:id/override` di insentive. Saat ini penimpaan hanya terdeteksi dari `value != auto_value`, tanpa alasan.
7. Normalkan label metrik. Kunci stabil sudah ada, jadi label kini **aman diganti** tanpa memutus konfigurasi otomatis.
8. Auto-fill Finance dari Accurate live proxy (13 metrik) dan Procurement (4 metrik).
9. Simpan budget/anggaran di ERP, karena saat ini tidak ada di mana pun.

**Fase 3, adopsi operasional bukan development**
10. Wajibkan pemakaian Production Log dan Batch Record (16 metrik), modul Training (6), modul Recruitment (6).

**Fase 4, fitur baru menurut frekuensi kemunculan**
11. Modul Kaizen / Ide Inovasi (16 metrik lintas departemen, kandidat implementasi paling hemat: space khusus di [[Microservices - Task Management Service]] yang sudah ada).
12. Log 1-on-1 (9 metrik), sejalan dengan konsep [[HRIS - Work Review]].
13. Field skor dan survei kepuasan pada modul Training (4 metrik).
14. Checklist operasional berjadwal untuk patroli, 5R, GMP, dan preventive maintenance. Satu modul menutup General Affair, Quality, dan Warehouse sekaligus (kurang lebih 20 metrik). Lihat [[GA - Checklist Management]].

**Yang sebaiknya tetap manual**: kurang lebih 36 metrik memang subjektif. Untuk kelompok ini yang perlu diperbaiki adalah rubrik penilaian, bukan otomasi; fitur lampiran bukti `/kpi/evidence` sudah tepat sasaran.

## Catatan Akurasi

Field `attribution_note` pada `mart_profit_attribution` di production menyatakan retur **tidak dapat diatribusikan ke level iklan** (laporan iklan tidak membawanya dan order tidak menyimpan campaign/ad/video id), dan dasar laba memakai gross revenue laporan iklan, bukan settlement bersih. Konsekuensinya ROI/ROAS otomatis di level iklan akan lebih optimis dari kenyataan. Bila angka ini dipakai untuk KPI yang berdampak ke insentif, pakai level toko atau produk, atau tampilkan disclaimer di UI.

## Belum Diimplementasikan / Catatan

- Tidak ada satu pun metrik yang terisi otomatis hari ini. Mesin dan endpointnya sudah hidup di produksi; yang kurang adalah konfigurasi `auto` pada `kpi_template`, diisi lewat `POST /kpi/templates` tanpa perlu deploy.
- **Uptime bulan Juni 2026 dan sebelumnya tidak dapat dihitung.** Diverifikasi di produksi 1 Agustus 2026: Juni membalas `null` dengan 0 dari 30 hari, Juli 99,81% dengan 23 dari 31 hari (membenarkan heartbeat terawal 9 Juli). Agustus adalah periode penuh pertama.
- **Selama bulan berjalan, metrik uptime akan dilaporkan `semi`, bukan `otomatis`.** Cakupannya memang belum penuh, dan uptime satu hari bukan uptime sebulan. Ia menjadi `otomatis` setelah bulannya tutup, yaitu saat penilaian dilakukan.
- **`System uptime` dan `Server uptime` belum dapat dibedakan.** Seluruh monitor bertipe `docker` (33) dan `http` (1); memisahkannya butuh monitor tingkat host di Kuma, pekerjaan tim IT.
- Sumber ROI/ROAS otomatis berasal dari [[Microservices - Marketing Analytics Service]] (didokumentasikan 2026-07-31, sebelumnya service ini berjalan di production tanpa dok). Perlu diperhatikan: `/lives`, `/cohort`, dan `/price-floor` masih membalas kosong karena koleksinya belum terisi, dan `/matrix/sku-shop` masih stub. Konteks bisnisnya di [[Sales - Marketing Dashboard (Master Roadmap)]].
- Angka sensus adalah snapshot 2026-07-31 dan akan bergeser. Cara memperbarui daftar template per posisi tanpa menebak: baca koleksi `kpi_template` pada database `employee_db`, urutkan berdasarkan `department` lalu `position`. Kredensial Mongo diambil dari environment container, jangan ditulis di dokumen.

## Dependensi & Integrasi

- **Sumber skor manual**: [[Microservices - Employee Service]] (`/kpi/*`), FE di [[APP - Web ERP]]
- **Sumber otomatis yang sudah terpasang**: [[Microservices - Monitoring Service]] (`uptime_sistem`) · [[Microservices - Employee Service]] sendiri (`skor_tim`)
- **Kandidat sumber otomatis**: [[Microservices - Insentive Service]] · [[Microservices - Integration Service]] · [[Microservices - Attendance Service]] · [[Microservices - Task Management Service]] · [[Microservices - Procurement Service]] · [[Microservices - Warehouse Service]] · [[Microservices - Inventory Service]] · [[External - Accurate]] · [[IT - Monitoring System]]
- **Terblokir adopsi**: [[Microservices - Manufacture Service]] · [[Microservices - Recruitment Service]] · [[HRIS - Training Program]]
- **Penjadwalan**: [[IT - Background Jobs & Schedulers]]
- **Struktur atasan-bawahan** untuk agregasi skor tim: [[HRIS - Organization Structure]]
- **Koleksi**: [[DB - Overview and Notes]]

## Dokumen Terkait

- [[HRIS - Alur KPI Otomatis.excalidraw]] (diagram Excalidraw, penjelasan untuk non-teknis: rangkaiannya dan tiga syarat yang sering terlupa)
- [[HRIS - Key Performance Index]] (mekanisme scoring, RBAC, cakupan tim Leader)
- [[HRIS - Work Review]] (rencana menyatukan KPI kuantitatif dengan review kualitatif)
- [[HRIS - Career & Promotion]] · [[HRIS - Personalia]] · [[HRIS - Attendance System]]
- [[HRIS - Analysis]] · [[HRIS - Big Pictures]] · [[HRIS - Interrelationship Matrices]] · [[HRIS - Roadmap]]
- [[Finance - Incentive]] · [[Sales - Incentive]]
- [[REF - Glossary]]
