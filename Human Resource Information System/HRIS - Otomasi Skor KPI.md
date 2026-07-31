## Deskripsi

*Analisis kelayakan **mengisi skor KPI secara otomatis** dari data yang sudah dimiliki ERP, bukan diketik manual oleh supervisor. Menjawab: dari 311 metrik yang benar-benar terpasang di production, mana yang sumber datanya sudah ada, mana yang modulnya ada tapi belum dipakai, dan mana yang memang tidak punya sumber sama sekali. Melengkapi [[HRIS - Key Performance Index]] yang menjelaskan mekanisme scoring-nya.*

- **Status**: 🟡 Konsep otomasi (belum ada satu pun metrik yang terisi otomatis). **Inventaris sumber datanya ✅ grounded** ke kode `origin/main` bip-erp commit `23c6bdc8` dan sensus dokumen 15 database production per **2026-07-31**.
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
| **Skor KPI tim** | 13 posisi SPV dan Leader | `employee_db.kpi_score` sendiri, diagregasi lewat `work_data.supervisor_id` atau department ([[HRIS - Organization Structure]]) | 406 |
| Uptime server dan sistem | IT Infrastructure, IT Support, Tech Leader/SPV | `monitoring-service` membaca `kuma.db` Uptime Kuma read-only: `GET /monitors` (`uptime_24h/7d/30d`), `GET /incidents` (`downtime_seconds`) ([[IT - Monitoring System]]) | 35 monitor |
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

## Rencana Bertahap (TBD, belum ada di kode)

Seluruh bab ini **rencana**, belum satu pun dikerjakan.

**Fase 1, tanpa modul baru**
1. Sambungkan [[Microservices - Insentive Service]] ke `kpi_score` sebagai nilai berstatus DRAFT (kurang lebih 30 metrik Kyura dan Beauty Hacks).
2. Auto-fill metrik "Performance Monitoring Team" dari agregasi `kpi_score` bawahan (13 posisi). Datanya berada di `employee_db` sendiri sehingga tidak perlu memanggil service lain.
3. Auto-fill metrik kedisiplinan dari `GET /attendance/report`.
4. Auto-fill KPI Tech Development dari `task-management` dan `monitoring` (14 metrik). Departemen paling siap sekaligus dikerjakan tim sendiri, cocok sebagai pilot.
5. Bersihkan data master sesuai bab Temuan Data Master.

**Fase 2, perlu development ringan**
6. Tambahkan penanda sumber pada `KPIMetric` (mis. `source` dan `auto_value` terpisah dari `value`) supaya nilai sistem dapat ditimpa supervisor **dengan jejak alasan**, meniru pola `PATCH /results/:id/override` yang sudah ada di insentive.
7. Normalkan label metrik.
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

- Tidak ada satu pun metrik yang terisi otomatis hari ini. Seluruh bab Rencana Bertahap berstatus TBD.
- **`marketing-analytics-service` belum terdokumentasi di vault.** Service ini berjalan di production (container `marketing-analytics-service`, database `marketing_analytics_db`, koleksi `mart_profit_attribution` 405.543 dokumen, `mart_video_performance` 87.813, `mart_ad_creative_link` 7.814) dan menyediakan `GET /profit/{shops,products,campaigns,ads}`, `/videos`, `/lives`, `/affiliate`, `/cohort`, `/audience`, `/returns/breakdown`, `/matrix/sku-shop`, `/price-floor`. Perlu dok `Microservices - Marketing Analytics Service` tersendiri. Konteks bisnisnya ada di [[Sales - Marketing Dashboard (Master Roadmap)]].
- Angka sensus adalah snapshot 2026-07-31 dan akan bergeser. Cara memperbarui daftar template per posisi tanpa menebak: baca koleksi `kpi_template` pada database `employee_db`, urutkan berdasarkan `department` lalu `position`. Kredensial Mongo diambil dari environment container, jangan ditulis di dokumen.

## Dependensi & Integrasi

- **Sumber skor manual**: [[Microservices - Employee Service]] (`/kpi/*`), FE di [[APP - Web ERP]]
- **Kandidat sumber otomatis**: [[Microservices - Insentive Service]] · [[Microservices - Integration Service]] · [[Microservices - Attendance Service]] · [[Microservices - Task Management Service]] · [[Microservices - Procurement Service]] · [[Microservices - Warehouse Service]] · [[Microservices - Inventory Service]] · [[External - Accurate]] · [[IT - Monitoring System]]
- **Terblokir adopsi**: [[Microservices - Manufacture Service]] · [[Microservices - Recruitment Service]] · [[HRIS - Training Program]]
- **Penjadwalan**: [[IT - Background Jobs & Schedulers]]
- **Struktur atasan-bawahan** untuk agregasi skor tim: [[HRIS - Organization Structure]]
- **Koleksi**: [[DB - Overview and Notes]]

## Dokumen Terkait

- [[HRIS - Key Performance Index]] (mekanisme scoring, RBAC, cakupan tim Leader)
- [[HRIS - Work Review]] (rencana menyatukan KPI kuantitatif dengan review kualitatif)
- [[HRIS - Career & Promotion]] · [[HRIS - Personalia]] · [[HRIS - Attendance System]]
- [[HRIS - Analysis]] · [[HRIS - Big Pictures]] · [[HRIS - Interrelationship Matrices]] · [[HRIS - Roadmap]]
- [[Finance - Incentive]] · [[Sales - Incentive]]
- [[REF - Glossary]]
