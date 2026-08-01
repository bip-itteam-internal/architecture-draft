## Deskripsi

*Isi lengkap `kpi_template` di **production**: seluruh label metrik, bobot, dan targetnya, dikelompokkan per departemen. Dokumen kerja untuk dev departemen yang akan mengotomatiskan metriknya. Cara mengerjakannya ada di [[RUN - Menambah Metrik KPI Otomatis]]; latar belakang dan analisis kelayakannya di [[HRIS - Otomasi Skor KPI]].*

- **Status**: ✅ Salinan setia data production per **2026-08-01**. Bukan rancangan dan bukan usulan; ini yang benar-benar dipakai menilai orang hari ini.
- **Sumber**: koleksi `kpi_template` di `employee_db` ([[Microservices - Employee Service]]).

## Cara membaca

**Label ditulis persis seperti tersimpan**, termasuk typo (`Perfomance Monitoring`), spasi di ujung (`Monitoring Team `), dan penomoran yang tidak deskriptif (`Performa 1`, `Administrasi 3`). Itu bukan kelalaian penyalinan: **label adalah kunci identitas metrik di kode**, sehingga menuliskannya "yang benar" di sini justru membuat dokumen tidak cocok dengan sistem.

Kolom **Target / keterangan** adalah isi `description` apa adanya. Di situlah target sebenarnya tersimpan, karena `kpi_template` **tidak punya field target yang dapat dibaca mesin** (diverifikasi: nol template memilikinya). Konsekuensinya sebagian deskripsi memuat lebih dari satu angka, dan itu harus diselesaikan dengan pemilik metriknya sebelum diotomatiskan.

Kolom **Klasifikasi otomasi** per departemen memakai empat kategori dari [[HRIS - Otomasi Skor KPI]]: sumber ada dan terisi / sumber ada tapi butuh definisi / modul ada tapi datanya kosong / tidak ada sumber sama sekali. Itu penilaian tingkat departemen. **Verdict per metrik tetap tugas dev departemen**, memakai langkah 1 di [[RUN - Menambah Metrik KPI Otomatis]], karena "endpointnya ada" tidak sama dengan "datanya cukup terisi".

## Ringkasan

| Departemen | Template | Metrik | Otomatis | Semi | Terblokir data | Manual |
|---|---:|---:|---:|---:|---:|---:|
| Beauty Hacks | 11 | 30 | 14 | 2 | 0 | 14 |
| Finance | 11 | 61 | 13 | 17 | 0 | 31 |
| General Affair | 5 | 24 | 1 | 5 | 1 | 17 |
| Human Resource | 5 | 31 | 7 | 5 | 10 | 9 |
| Kesekretariatan | 7 | 28 | 0 | 0 | 0 | 28 |
| Kyura | 9 | 27 | 16 | 1 | 0 | 10 |
| Manufaktur | 9 | 52 | 3 | 16 | 16 | 17 |
| Procurement | 2 | 10 | 4 | 2 | 0 | 4 |
| Quality | 4 | 18 | 1 | 2 | 8 | 7 |
| Tech Development | 7 | 30 | 14 | 9 | 0 | 7 |
| **Total** | **70** | **311** | **73** | **59** | **35** | **144** |

Dua departemen di `work_data` **tidak muncul di sini karena belum punya template sama sekali**: Percetakan (13 karyawan) dan Marketing Offline Distribution (1 karyawan).

## Cacat yang sudah diketahui

Beberapa baris di bawah memang cacat di datanya, dan sengaja disalin apa adanya supaya terlihat:

- **Template uji ikut produksi.** `Beauty Hacks / Buzzer / Buzzer` berisi satu metrik berlabel `contoh` berbobot 1.0, sehingga posisi Buzzer punya dua template.
- **Metrik duplikat.** `Manufaktur / Warehouse Leader` memuat `Mencegah over-dispensing ...` dan `... 2` dengan deskripsi identik, total bobot 0,30 untuk hal yang sama.
- **Label memakai target korporat, bukan metrik personal.** `Revenue 240M`, `Net Income 20%`, `Penurunan HPP 5%` muncul sebagai label di posisi Staff Inventory, Tax Staff, dan QA RND. Metrik sebenarnya ada di deskripsinya.
- **Template menilai produk departemen lain.** `Kyura / Kyura Supervisor` memuat `Customer Satisfactions untuk Produk Beautyhacks 4,5 dari 5`.
- **Satu deskripsi memuat tiga angka.** `Kyura Supervisor / Revenue 240M` berbobot 0,6: label menyebut 240M, deskripsinya menyebut profit 546 juta dan omzet 4.090.000.000.

## Cara memperbarui dokumen ini

Angka di sini akan bergeser begitu template disunting. Untuk menyegarkan, baca ulang `kpi_template` di `employee_db` (urutkan `department`, `position`, `name`), lalu tulis ulang bab per departemen di bawah. Jangan menyunting sebagian, karena bobot antar-metrik saling terkait dan wajib berjumlah 1.0 per template.

## Beauty Hacks

11 template, 30 metrik. Klasifikasi otomasi: **14 / 2 / 0 / 14**.

### Affiliate

Template `AFFILIATE`, 2 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Jumlah Affiliate Aktif` | Jumlah Affiliator Baru yang bergabung dalam sebulan berdasarkan ketentuan perusahaan |
| 0.7 | `Conversion` | Jumlah Konversi Iklan dalam Sebulan |

### BeautyHacks Supervisor

Template `BEAUTYHACKS SUPERVISOR`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.6 | `Revenue 240M` | Achievement 100% / Bulan |
| 0.05 | `Inventory turn over 90 days` | Akurasi forecast minimal 85–90%. |
| 0.05 | `Customer Satisfactions untuk Produk Beautyhacks 4,5 dari 5` | Rating Toko > 4.5 |
| 0.3 | `Performance Monitoring Team` | TARGET SKOR >70 |

### Buzzer

Template `BUZZER BHS`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Peforma 1` | Early Engagement Speed : Kecepatan boosting (like, comment, share, save) dalam waktu yang ditentukan setelah video tayang. |
| 0.45 | `Performa 2` | Engagement Quantity : Jumlah like, comment, share, save sesuai target atau request tim ICC. |
| 0.2 | `Performa 3` | Reporting & Account Readiness : Kelengkapan laporan harian dan kesiapan akun buzzer (akun aktif & organik). |
| 0.05 | `Performa 4` | Kaizen : Jumlah inisiatif perbaikan yang diterapkan. |

### Buzzer

Template `Buzzer`, 1 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 1 | `contoh` | contoh |

### Customer Support

Template `CUSTOMER SERVICE`, 3 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Perfomance 1` | Closing Rate |
| 0.6 | `Perfomance 2` | Konversi |
| 0.1 | `Kaizen` | Jumlah inisiatif perbaikan yang diterapkan. |

### Host Live

Template `HOST LIVE`, 3 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.6 | `Conversion` | Jumlah konversi live dalam sebulan |
| 0.3 | `ROI` | Skor final KPI tercapai sesuai target |
| 0.1 | `Perfomance Monitoring` | Skor final KPI tercapai sesuai target |

### ICC

Template `INTERNAL CONTENT CREATOR`, 3 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.4 | `Jumlah Video` | 125 video/bulan |
| 0.2 | `Video Memenuhi Standar Struktur Indikator VSA` | ≥ 70% atau min. 87 video |
| 0.4 | `Video Memenuhi Standar Struktur Indikator GMV MAX` | ≥ 30% atau min. 37 video |

### Leader

Template `LEADER`, 3 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.2 | `Perfomance Monitoring` | Persentase Team ICC Mencapai target KPI |
| 0.4 | `Conversion` | 120,000 |
| 0.4 | `ROI` | > 3.2 |

### Marketplace Advertiser

Template `ADV MARKETPLACE`, 2 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.7 | `Conversion` | Jumlah konversi iklan dalam sebulan |
| 0.3 | `CPA` | Rata-rata biaya iklan yang dikeluarkan per konversi |

### Meta Advertiser

Template `ADV META`, 2 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.5 | `Conversion` | Jumlah konversi iklan dalam sebulan |
| 0.5 | `CPA` | Rata-rata biaya iklan yang dikeluarkan per konversi |

### Video Editor

Template `VIDEO EDITOR`, 3 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.35 | `Lead Time` | Persentase pengambilan dan edit Video Content berdasarkan transisi, editing, dan hasil akhir selesai tepat waktu untuk pemenuhan tim marketing. |
| 0.25 | `Pengelolaan Alat dan Kelengkapan` | Persentase alat yang berfungsi baik, jumlah alat yang rusak, dan kerapihan penyimpanan & Kondisi kebersihan alat. |
| 0.4 | `Kualitas Konten` | Persentase pengambilan & edit video content disetujui kualitasnya. |

## Finance

11 template, 61 metrik. Klasifikasi otomasi: **13 / 17 / 0 / 31**.

### AR Leader

Template `KPI AR Leader`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Mengurangi piutang aging > 60 hari sampai < 5% dari total AR` | Rekonsiliasi AR Harian |
| 0.3 | `Pengawasan 100% AR aging ≤ 14 hari` | Follow-up pembayaran & rekonsiliasi kas - 90% pembayaran diterima sesuai aging ≤ 14 hari |
| 0.2 | `Monitoring Team` | Checker inputan team/Rekonsiliasi dengan selesai pengimputan data max tgl 3 bulan berikutnya |
| 0.1 | `Minimal 6 ide inovasi baru dari 5 TOTAL tim pada tiap kuartal` | Mengidentifikasi peluang inovasi di proses AR Finance |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV / Leader |

### AR Staff

Template `KPI AR Piutang`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.25 | `Penagihan > 60 hari sampai < 5% dari total AR` | Proses AR & Cash Collection Harian |
| 0.4 | `Pencatatan Piutang` | Input data piutang (Uang masuk) max laporan inputan piutang bulanan selesai tanggal 3 bulan berikutnya |
| 0.25 | `Penagihan piutang > 14 hari sampai < 5% dari total AR` | Proses AR & Cash Collection Harian dengan Max 5% piutang belum tertagih lebih dari 14 hari |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses AR dengan minimal 2 ide terdaftar perbulan |

### AR Staff

Template `KPI AR Retur`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Penanganan retur di platform atau Expedisi` | Proses foll up retur lebih dari 14 hari dengan maksimal 5% retur |
| 0.5 | `Pencatatan retur penjualan` | Input data retur dengan max laporan inputan retur bulanan selesai tanggal 3 bulan berikutnya |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses AR minimal 2 ide terdaftar perbulan |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV / Leader |

### AR Staff

Template `KPI Sales Admin`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.5 | `Pencatatan Penjualan` | Input data penjualan dengan max laporan inputan penjualan bulanan selesai tanggal 3 bulan berikutnya |
| 0.3 | `Rekonsiliasi stok penjualan` | Rekonsiliasi data stok terjual dengan data pengiriman gudang dengan Max laporan rekonsiliasi stok selesai tanggal 3 bulan berikutnya |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses AR Minimal 2 ide inovasi terdaftar perbulan |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV / Leader |

### Account Payable

Template `KPI Finance Staff Account Payable`, 6 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.25 | `Cashflow terpantau 100% setiap minggu, operating cashflow ≥ 100%` | Mengecek expense dari cost control sesuai anggaran |
| 0.2 | `100% pembayaran dan pengeluaran sesuai rencana cashflow` | Memvalidasi dan mencatat pengeluaran operasional sebelum dibayarkan |
| 0.2 | `Perhitungan harga pokok produksi (HPP)` | Costing HPP 95% valid dengan realisasi costing max 1 hari setelah permintaan |
| 0.15 | `Minimal ide inovasi baru dari tim pada setiap quartal` | Mengidentifikasi peluang inovasi di proses finance minimal 1 ide inovasi terdaftar per bulan |
| 0.1 | `Laporan credit team dibuat 100% tepat waktu dan terdokumentasi` | Menyusun laporan credit term berdasarkan data valid selesai tepat waktu setiap bulan |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV |

### Cost Control

Template `KPI Cost Control`, 7 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.2 | `Varians antara budget vs realisasi OPEX ≤ ±5%` | Review Cash Outflow Mingguan - Realisasi OPEX dalam batas ±5% dari budget |
| 0.1 | `Penurunan biaya admin/non operasional minimal 2% YoY` | Analisis biaya berulang dan rekomendasi perbaikan |
| 0.2 | `Penurunan OPEX 3–5% dalam 6 bulan` | Melakukan Analisis Varians OPEX dengan minimal 3 rekomendasi efisiensi cost driver setiap bulan |
| 0.15 | `Forecast cashflow mingguan dengan akurasi ≥ 95%.` | Analisis Deviasi Forecast vs Aktual |
| 0.2 | `Pengelolaan Kas Iklan` | Akurasi Distribusi kas iklan dan pencatatan |
| 0.1 | `Minimal 5 ide inovasi baru dari tim` | Mengidentifikasi peluang inovasi di proses cost control |
| 0.05 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV |

### Finance Supervisor

Template `KPI Supervisor Finance`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.25 | `Revenue 240M` | Monitoring AR & Collection untuk Menjaga Cashflow Penjualan dengan mengurangi piutang aging > 60 hari sampai < 5% dari total AR. |
| 0.25 | `Rasio EBITDA 45%` | Kontrol OPEX dengan Budget Compliance 95% (Varians antara budget vs realisasi OPEX ≤ ±5%) |
| 0.2 | `Net income 20%` | Kontrol Beban Non-Operasional ≤ 2% |
| 0.1 | `Return on Operation = 2,75` | Cashflow Forecasting mingguan dengan akurasi ≥ 95%. |
| 0.2 | `Performance Monitoring Team` | KPI Tim minimal skor 70 |

### Junior Accountant

Template `KPI Accounting CV`, 6 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Laporan keuangan` | Menyusun laporan keuangan dengan persentase laporan keuangan secara akurat dan tepat waktu max tgl 4 bulan berikutnya |
| 0.25 | `Pengelolaan kas` | Melakukan rekonsiliasi bank dan pencatatan kas laporan keuangan dengan Presentase selisih antara laporan keuangan perusahaan dengan rekening koran setiap bulan (Target 0% selisih) |
| 0.15 | `Pengelolaan asset/perlengkapan` | Pengecekan dan depresiasi asset dengan Presentase aset dan perlengkapan tercatat secara akurat dan tepat waktu max tgl 4 bulan berikutnya |
| 0.1 | `Pajak` | Pajak terbayar tepat waktu dengan persentase pajak perusahaan dan karyawan terbayar tepat waktu (max 1 hari sebelum jatuh tempo) |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses accounting dengan Minimal 2 ide inovasi terdaftar perbulan di tiap kuartal |
| 0.1 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi.` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV |

### Junior Accountant

Template `KPI Accounting PT`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.35 | `Transaksi Keuangan` | Akurasi & ketepatan waktu pencatatan transaksi keuangan |
| 0.35 | `Transaksi Non-keuangan` | Akurasi & ketepatan waktu pencatatan transaksi non-keuangan |
| 0.15 | `Minimal 5 ide inovasi baru dari tim pada Q1` | Mengidentifikasi peluang inovasi di proses accounting |
| 0.15 | `Pertemuan 1-on-1 minimal 1 per bulan per staf, 100% terdokumentasi` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV |

### Senior Accountant

Template `KPI Senior Accounting Bharata`, 8 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.2 | `Laporan Keuangan 1` | Menyusun laporan keuangan secara akurat dengan persentase laporan keuangan secara akurat dan tepat waktu maks. tgl 7 bulan berikutnya |
| 0.15 | `Laporan Keuangan` | Melakukan analisa laporan keuangan min. 2 rekomendasi perbaikan kinerja perusahaan di setiap bulan |
| 0.15 | `Pengelolaan Aset Tetap` | Pengecekan dan depresiasi aset - Persentase aset dan perlengkapan tercatat secara akurat dan tepat waktu maks. tgl 7 |
| 0.15 | `Rekonsiliasi bank, penjualan, dan persediaan` | Melakukan rekonsiliasi bank, penjualan, dan persediaan - Persentase laporan rekonsiliasi bank, penjualan, persediaan secara akurat dan tepat waktu |
| 0.05 | `Audit Internal` | Menyusun data dan dokumentasi pendukung untuk audit internal 100% tersedia tepat waktu. |
| 0.1 | `Monitoring Team` | Checker pencatatan/inputan team dengan minimal target KPI Staff 80 dan maks. pengumpulan tgl 3 |
| 0.1 | `Minimal ide inovasi baru dari tim pada tiap kuartal` | Mengidentifikasi peluang inovasi di proses accounting minimal 2 ide inovasi terdaftar per bulan di kuartal 1 |
| 0.1 | `Pertemuan 1-on-1 min. 1 per bulan per staf, 100% terdokumentasi` | Aktif memberikan update progres pekerjaan saat 1-on-1 dengan SPV |

### Tax Staff

Template `KPI Tax Officer`, 8 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.15 | `Varians antara budget vs realisasi OPEX ≤ ±5%` | Memastikan perlakuan PPh dan PPN tepat (deductible vs non deductible) - Potensi untuk menekan biaya non-deuctible 10% |
| 0.15 | `Kepatuhan pajak 100% setiap bulan 1` | Rekonsiliasi pajak bulanan dengan Selisih (discrepancy) rekonsiliasi = 0% setiap bulan |
| 0.1 | `Kepatuhan pajak 100% setiap bulan 2` | Menyusun dan melakukan penyampaian SPT Masa tepat waktu minimal H-1 dari batas waktu |
| 0.15 | `Kepatuhan pajak 100% setiap bulan 3` | Melakukan monitoring kepatuhan dan melaporkan temuan pajak dengan 100% temuan ditindaklanjuti dalam ≤ 10 hari kerja |
| 0.15 | `100% laporan pajak & regulatory filing diperiksa sebelum dikirim` | Menyiapkan laporan tepat waktu, valid, dan sesuai regulasi |
| 0.1 | `Minimal 2 audit internal per tahun, rate non-compliance ≤ 5%` | Menyediakan data pajak dan laporan government filing untuk audit internal |
| 0.1 | `Laporan keuangan` | Menyusun laporan keuangan dengan persentasi laporan keuangan secara akurat dan tepat waktu maks. tgl 5 |
| 0.1 | `Minimal 5 ide inovasi baru dari tim pada setiap kuartal` | Mengidentifikasi peluang inovasi di proses tax dengan minimal 2 ide inovasi terdaftar per bulan |

## General Affair

5 template, 24 metrik. Klasifikasi otomasi: **1 / 5 / 1 / 17**.

### Admin

Template `Admin General Service`, 7 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.2 | `Pengelolaan Keuangan GA 1` | Persentase realisasi anggaran belanja sesuai rencana tanpa over budget. Terpakai di 30% dari Total Anggaran / Bulan |
| 0.2 | `Pengelolaan Keuangan GA 2` | Akurasi pencatatan data kas kecil secara tepat waktu. |
| 0.1 | `Administrasi & Pengadaan 1` | Persentase ketepatan rekap pengajuan dana kebutuhan GA |
| 0.15 | `Administrasi & Pengadaan 2` | Administrasi Dokumen GA ( Kelengkapan & kerapihan dokumen secara Real Time ) |
| 0.15 | `Administrasi & Pengadaan 3` | Ketepatan Pengadaan Barang ATK & GA ( Tepat Waktu ) |
| 0.1 | `Pengelolaan Vendor` | Skor Pelayanan & Harga(tidak Over Budget) vendor |
| 0.1 | `Aset Support Operational` | Akurasi Pengelolaan ATK & Inventory |

### GA Staff

Template `Building & Maintenance`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Pengelolaan Aset Building dan Fasilitas 1` | Realisasi Preventif Maintenance Building & Fasilitas |
| 0.3 | `Pengelolaan Aset Building dan Fasilitas 2` | Menyelesaikan kerusakan secara cepat dan tepat (Jumlah Perbaikan Berhasil : Total Perbaikan) |
| 0.25 | `Efisiensi Biaya Maintenance / Project` | Mengontrol biaya tanpa menurunkan kualitas (Realisasi/Budget) x 100% All Project Perbaikan |
| 0.15 | `Daily Report` | Checklist Harian & Bulanan |

### GA Staff

Template `General Asset Staff`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Aset dan Insidental 1` | Persentase Realisasi Rencana Kerja VS Realisasi |
| 0.25 | `Aset dan Insidental 2` | Persentase SLA Preventife Maintenance Alat Operational Tepat Waktu |
| 0.2 | `Aset dan Insidental 3` | Persentase Pemeliharaan Aset Dengan Tepat |
| 0.15 | `Aset dan Insidental 4` | Akurasi Ketepatan Stok Opname Aset |
| 0.1 | `Penglolaan Aset` | Labeling & Tagging Asset |

### Office Boy

Template `Office Boy Team`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Pelayanan Kebersihan` | Rating Pelayanan dan Kebersihan (1-10) |
| 0.3 | `Kebersihan 1` | Kondisi kebersihan area yang ditugaskan (halaman, loby, ruang QA/QC, produksi, direktur, dll). |
| 0.25 | `Kebersihan 2` | Kondisi perawatan barang/perabotan, tanaman asli/hias di area yang ditugaskan. |
| 0.15 | `Kebersihan 3` | Pelaksanaan 5R di Area Pantry dan Area Tanggung Jawab Kebersihan |

### Security

Template `Security Team`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Pelayanan Security` | Rating Pelayanan dan Keamanan (1-10) |
| 0.3 | `Kualitas Keamanan` | Kepatuhan Melakukan Patroli Setiap 3 Jam ( Aspek Keamanan, Kerapian & Kondisi Area ) |
| 0.2 | `Dokumentasi` | Kepatuhan SOP Security |
| 0.2 | `Kerapihan dan kebersihan Pos` | Persentase kerapihan dan kebersihan pos jaga ( Konsep 5R ) |

## Human Resource

5 template, 31 metrik. Klasifikasi otomasi: **7 / 5 / 10 / 9**.

### Culture & Industrial

Template `Organizational Development`, 6 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.2 | `Culture 1` | Penyusunan program culture |
| 0.2 | `Culture 2` | Persentase terlaksananya program culture yang sesuai jadwal |
| 0.2 | `Culture 3` | Prosentase Keaktifan Peserta Training >= 100% dari jumlah Peserta |
| 0.2 | `KPI` | Skor Penilaian Training All Karyawan > 70 |
| 0.1 | `SOP` | Tingkat Kedisipilnan Karyawan ( Attandance & Intergritas ) |
| 0.1 | `Kaizen` | Jumlah Inovasi All Divisi ( 7 / Bulan ) |

### HRD Supervisor

Template `KPI Supervisor HRGA`, 10 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.15 | `Revenue 240 Miliar` | Menjamin ketersediaan tenaga kerja dengan rata-rata time recruitment <30 hari untuk posisi kritikal |
| 0.05 | `Net Income 20%` | Efisiensi biaya operasional GA min. 5% dari bulanan |
| 0.05 | `Return On Operation Asset` | Monitoring aset 100% terdata secara realtime |
| 0.2 | `Performance Monitoring 100% Terimplementasi di Q4` | Memastikan seluruh tim/karyawan di setiap departemen memiliki skor KPI Min. 70 |
| 0.1 | `Turn Over Rate Target 5% per Tahun` | Peningkatan Kualitas Rekruitment |
| 0.1 | `Implementasi Training` | Memenuhi kebutuhan pelatihan untuk talent dan seluruh karyawan 100% terpenuhi tiap bulan dan terjadi peningkatan performa. |
| 0.2 | `Performance Monitoring Team HRGA` | Rata-rata KPI Team HRGA min. 70 |
| 0.05 | `Employee Productivity sebesar 120 Juta per Employee ( DIv. Marketing )` | Memberikan Training, Coaching, atau Tools untuk meningkatkan Produktivitas. |
| 0.05 | `Succession Planing Terimplementasi` | Menyusun Kaderisasi & Talent Pool - 100% Calon Successor memiliki Development Plan dan Siap apabila diperlukan |
| 0.05 | `Employee Satisfaction` | Tingkat kepuasan pelayanan Team General Service minimal 90% memberikan penilaian 5 dari all karyawan |

### Personalia

Template `Personalia Team`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.25 | `Administrasi 1` | Terselesaikannya administrasi payroll dan absensi karyawan sesuai dengan ketentuan perusahaan secara akurat |
| 0.2 | `Administrasi 2` | Terselesaikannya administrasi BPJS rekening dan surat-surat karyawan sesuai dengan ketentuan perusahaan |
| 0.2 | `Administrasi 3` | Terselesaikannya administrasi kontrak karyawan baru dan perpanjang kontrak dengan tepat |
| 0.25 | `Administrasi 4` | Pengkinian Data Karyawan terupdate secara akurat di drive utama |
| 0.1 | `Kedisiplinan` | Kehadiran dan Ketepatan Waktu |

### Recruitment & Onboarding

Template `Recruitment Team`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.25 | `Rekrutmen Seleksi dan penempatan` | Time to Fulfilment Rate ( < 30 Hari ) All Vacant |
| 0.2 | `Rekrutmen Seleksi dan penempatan` | Membuat rencana jadwal dan pelaksanaan onboarding karyawan Masa Percobaan. |
| 0.2 | `Rekrutmen Seleksi dan Penempatan` | Presentase Data Base Buffer Kebutuan MPP |
| 0.25 | `Job Description` | Skor Kompetensi New Hire Fase On Boarding >80 |
| 0.1 | `Kaizen` | Jumlah inisiatif perbaikan yang diterapkan |

### Training & Perfomance Officer

Template `People Development`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.35 | `Training & Development` | Terlaksananya kegiatan training & performance officer sesuai dengan rencana. |
| 0.25 | `Training & Development 2` | Training Attendance Rate |
| 0.2 | `Peningkatan Performance` | Skor Penilaian Training All Karyawan > 70 |
| 0.1 | `KPI` | SLA Pengumpulan KPI tepat waktu dan ter-update |
| 0.1 | `Pelayanan` | Training Satisfaction Score |

## Kesekretariatan

7 template, 28 metrik. Klasifikasi otomasi: **0 / 0 / 0 / 28**.

### Company Branding

Template `COMPANY BRANDING`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Perfomance & Engagement 1` | Persentase kenaikan engagement rate (ER) instagram dalam sebulan (min. Rata-rata 3%) |
| 0.25 | `Perfomance & Engagement 2` | Persentase kenaikan engagement rate (ER) TikTok dalam sebulan (min. Rata-rata 5%). |
| 0.3 | `Perfomance & Engagement 3` | Jumlah konten yang disetujui unggah sosial media (Tiktok dan Instagram) dalam sehari. |
| 0.15 | `Manajemen Waktu` | Membuat konten planner dan melaksanakan sesuai jadwal. |

### Corporate Secretary

Template `CORPORATE SECRETARY`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.2 | `Manajemen Jadwal Direktur` | Persentase agenda berjalan tanpa bentrok dan sesuai jadwal. |
| 0.25 | `Kualitas & Ketepatan Dokumen Direktur` | Tingkat kesalahan dalam surat, laporan, dan bahan presentasi sesuai standar. |
| 0.3 | `Supporting Agenda Direktur` | Penyelesaian Instruksi Direktur |
| 0.25 | `Penyediaan Laporan dan Data Direktur` | Akurasi Laporan ke Direktur |

### Graphic Design

Template `GRAPHIC DESIGNER`, 3 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.35 | `Graphic Content untuk produk kemasan` | Persentase design yang disetujui oleh pengaju dan diserahkan 1 hari setelah form pengajuan ditandatangani. |
| 0.35 | `Product Design untuk kebutuhan perusahaan` | Persentase design disetujui perusahaan dan diserahkan 1 hari setelah form pengajuan ditandatangani. |
| 0.3 | `Graphic Content untuk marketing` | Persentase design yang disetujui oleh marketing officer dan diserahkan 1 hari setelah form pengajuan ditandatangani. |

### Internal Audit

Template `INTERNAL AUDIT`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.15 | `Kepatuhan Implementasi Kebijakan` | Persentase kebijakan dan arahan Direktur yang dijalankan sesuai standar. |
| 0.2 | `Akurasi dan Validitas Data Laporan` | Tingkat kesalahan data dalam laporan lintas divisi Error ≤ 2% |
| 0.25 | `Ketepatan Monitoring dan Follow Up` | Persentase Penyelesaian Temuan (Closing Finding Rate) |
| 0.15 | `Efektivitas Kontrol dan Deteksi Issue` | Jumlah issue/kendala yang teridentifikasi sebelum berdampak besar. |
| 0.25 | `Kedisiplinan Sistem & Koordinasi Divisi` | Kelengkapan laporan, & Kejelasan rekomendasi ( Target 100 % ) Sesuai |

### Personal Assistant

Template `PERSONAL ASSISTANT`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Ketepatan Manajemen Jadwal Direktur` | Persentase agenda berjalan tanpa bentrok/terlewat |
| 0.25 | `Ketepatan & Kecepatan Penyelesaian Tugas` | Persentase tugas Direktur selesai tepat waktu & sesuai instruksi |
| 0.3 | `Kelancaran Perjalanan & Agenda Khusus` | Tingkat kesiapan & kelancaran perjalanan dinas tanpa kendala |
| 0.15 | `Responsivitas & Kerahasiaan` | Kecepatan respon & keamanan informasi Direktur |

### QA RND

Template `R&D REGULATORY`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.1 | `Zero major finding saat external audit dengan BPOM` | memastikan seluruh aktivitas sesuai regulasi (BPOM, GMP, HACCP, dll) |
| 0.4 | `Net income 20%` | Product Development Support |
| 0.25 | `Inovation & Improvement` | Meningkatkan Inovasi & Efisiensi Produk |
| 0.25 | `New Product Readiness (Permit & Licence from BPOM) di Q1` | Penyelesaian izin BPOM & Halal sebelum deadline launching |

### Video Editor

Template `VIDEOGRAPHER & EDITOR COMPANY`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.35 | `Lead Time` | Persentase pengambilan dan edit Video Content berdasarkan transisi, editing, dan hasil akhir selesai tepat waktu untuk pemenuhan perusahaan. |
| 0.15 | `Pengelolaan & Kelengkapan Alat` | Persentase alat yang berfungsi baik, jumlah alat yang rusak, dan kerapihan penyimpanan. |
| 0.1 | `Kebersihan Alat` | Kondisi kebersihan alat. |
| 0.4 | `Kualitas Konten` | Persentase pengambilan & edit video content disetujui kualitasnya. |

## Kyura

9 template, 27 metrik. Klasifikasi otomasi: **16 / 1 / 0 / 10**.

### Affiliate

Template `AFFILIATE ACQUSITION`, 3 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.4 | `Jumlah Affiliate Aktif` | Jumlah Affiliator Baru yang bergabung dalam sebulan berdasarkan ketentuan perusahaan |
| 0.4 | `Conversion` | Jumlah Konversi Iklan dalam Sebulan |
| 0.2 | `Perfomance Monitoring` | Skor final KPI tercapai sesuai target |

### Buzzer

Template `BUZZER`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Early Engagement Speed` | Kecepatan boosting (like, comment, share, save) dalam waktu yang ditentukan setelah video tayang.≥ 95% video diboost ≤ 5 menit |
| 0.25 | `Engagement Quantity` | Jumlah like, comment, share, save sesuai target atau request tim ICC. |
| 0.2 | `Engagement Quality` | Kualitas komentar (natural, variatif, relevan, tidak template & aman) sehingga meningkatkan engagement.≥ 90% komentar lolos review |
| 0.2 | `Reporting & Account Readiness` | Kelengkapan laporan harian dan kesiapan akun buzzer (akun aktif & organik). |
| 0.05 | `Kaizen` | Jumlah inisiatif perbaikan yang diterapkan. |

### Customer Support

Template `Customer service`, 3 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.4 | `Perfoma` | Rating toko |
| 0.4 | `Kinerja` | Rate kecepatan respon chat toko |
| 0.2 | `Kaizen` | Jumlah inisiatif perbaikan yang diterapkan. |

### Host Live

Template `HOST LIVE KYURA`, 2 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.7 | `Conversion` | Jumlah konversi live dalam sebulan 2500 |
| 0.3 | `ROI` | Jumlah Roi 4 |

### ICC

Template `INTERNAL CONTENT CREATOR`, 3 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.4 | `Kuantitas Video Konten` | 125 video/bulan |
| 0.2 | `Video Memenuhi Standar Struktur Indikator 10.000/video` | ≥ 70% atau min. 87 video |
| 0.4 | `Video Memenuhi Standar Struktur Indikator 150.000/video` | ≥ 30% atau min. 37 video |

### Kyura Supervisor

Template `KPI Kyura Supervisor`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.6 | `Revenue 240M` | Target Profit 546 jt yang ditentukan Oleh Finance/ Omset 4.090.000.000 |
| 0.05 | `Inventory turn over 90 days` | Demand forecasting lebih akurat dengan target minimal 85–90%. |
| 0.05 | `Customer Satisfactions untuk Produk Beautyhacks 4,5 dari 5` | Target Kepuasan Customer dengan target Rating Toko > 4.5 |
| 0.3 | `Performance Monitoring Team` | KPI Team Kyura denan target skor minimal 70 |

### Leader

Template `LEADER TIKTOK KYURA`, 3 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.4 | `ROI` | Rata-rata biaya iklan yang dikeluarkan per konversi 3.2 |
| 0.4 | `Conversion / OMZET` | Jumlah konversi yang tertera pada dashboard akun pengiklan 54000 |
| 0.2 | `Perfomance Monitoring` | Skor final KPI tercapai sesuai target |

### Marketplace Advertiser

Template `ADV MARKETPLACE`, 2 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.5 | `Conversion` | Jumlah konversi iklan dalam sebulan |
| 0.5 | `ROI` | Rata-rata biaya iklan yang dikeluarkan per konversi |

### Meta Advertiser

Template `ADV META`, 2 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.5 | `Conversion` | Jumlah konversi iklan dalam sebulan |
| 0.5 | `ROI` | Rata-rata biaya iklan yang dikeluarkan per konversi |

## Manufaktur

9 template, 52 metrik. Klasifikasi otomasi: **3 / 16 / 16 / 17**.

### Admin Production

Template `ADMIN PRODUKSI`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Dokumen Produksi` | Persentase kelengkapan dan keabsahan dokumen produksi yang diajukan maksimal 1 hari setelah produksi selesai 100% |
| 0.3 | `Perlengkapan Produksi` | Persentase stok perlengkapan produksi yang tidak ada keluhan berupa kekurangan atau kelebihan |
| 0.2 | `Sumber data terverifikasi dan tervalidasi di setiap bulan` | Melakukan input data produksi (output, downtime, defect) ke template dashboard |
| 0.2 | `Dokumen pendukung produksi diserahkan ke QA/R&D paling lambat Minggu ke-2 Januari` | Menyusun dokumen teknis produksi untuk BPOM (flow proses, parameter kritis, kapasitas mesin, draft batch record) |

### Admin Warehouse

Template `ADMIN WAREHOUSE 2`, 6 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.25 | `Arus Stok Bahan` | Persentase input data gudang tepat waktu. |
| 0.2 | `100% sumber data terverifikasi dan tervalidasi di akhir bulan` | Rekonsiliasi stok fisik vs sistem untuk validasi data dashboard |
| 0.2 | `100% material high-risk & finished goods mengikuti FIFO/FEFO setiap batch` | Melaksanakan proses penerimaan & penyimpanan barang sesuai urutan FIFO/FEFO |
| 0.15 | `Akurasi stok fisik vs sistem ≥ 100% setiap stock opname bulanan` | Update kartu stok & dashboard FIFO/FEFO |
| 0.1 | `Barang Reject/Retur` | Persentasi penanganan tindak lanjut barang reject/retur |
| 0.1 | `100% monitoring mingguan dengan temuan dikoreksi dalam ≤3 hari` | Pencatatan kuantitas limbah |

### Admin Warehouse

Template `ADMIN WAREHOUSE TINGGARJAYA`, 6 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.2 | `Proses Inbound dan Outbound` | Akurasi controlling stok gudang (fisik) |
| 0.2 | `Stock Opname` | Selisih hasil stock opname fisik dengan data sistem. |
| 0.15 | `Administrasi Gudang 1` | Kelengkapan dan kerapian dokumen gudang (surat jalan, retur) |
| 0.15 | `Administrasi Gudang 2` | Pembagian dan pemetaan produk sebelum dikirim ke ekspedisi (100% resi yang diserahkan ke packing - ekspedisi). |
| 0.2 | `Akurasi Pengiriman Produk` | Jumlah komplain customer yang masuk (salah produk & produk reject) |
| 0.1 | `Kas Gudang` | Report update kas kecil secara realtime |

### Leader Production

Template `LEADER PRODUKSI`, 7 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.15 | `Proses Produksi 1` | Produksi 95% tanpa hambatan teknis, 5% Untuk Perbaikan 95% |
| 0.15 | `Proses Produksi 2` | Menurunkan waste pengolahan dan pengemasan. 1,5% |
| 0.15 | `Proses Produksi 3` | Menjaga pemenuhan target kuantiti produk yang diluluskan ≥ 98% |
| 0.15 | `Perfomance Monitoring` | Persentase operator produksi mencapai target KPI (Min. 70). |
| 0.1 | `Kaizen 1` | Mengurangi Jumlah CAPA produksi yang ditemukan. |
| 0.15 | `Kaizen 2` | Menjaga Kualitas Produk Target 98% ( Sesuai SOP QC ) |
| 0.15 | `Realisasi Produksi` | Meningkatkan pelaksanaan rencana produksi sesuai dengan realisasi produksi ≥ 98% |

### Manufacturing Supervisor

Template `SPV MANUFAKTUR`, 7 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.2 | `Jumlah Produksi` | Target Produksi 322.000 pcs / Bulan, 12.800 / Hari |
| 0.1 | `Mengurangi rework & scrap` | Reject & scrap turun ≥ 20%. |
| 0.1 | `Kontrol ketat biaya produksi variabel` | variable dimaintain sama dengan tahun 2025 |
| 0.1 | `Menurunkan material loss` | Material loss mixing turun ≤ 1,5%. |
| 0.1 | `Penguatan implementasi GMP di area produksi & warehouse` | 100% area produksi & gudang memenuhi checklist GMP internal setiap bulan |
| 0.1 | `Penguatan SOP K3 dan Standard Safety Equipment di area produksi & warehouse` | 100% pekerja menggunakan APD sesuai SOP setiap hari, Zero accident |
| 0.3 | `Performance Monitoring Team` | TARGET SKOR >70 |

### Operator Production

Template `OPERATOR PRODUKSI`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.2 | `Keluhan` | 0% |
| 0.25 | `Pengolahan` | ≥ 98% |
| 0.25 | `Waste (pembelian material tambahan akibat kesalahan internal selama 1 bulan produksi)` | MAXIMAL 1,5 % |
| 0.15 | `Kesesuaian stock opname` | 100% |
| 0.15 | `Penurunan biaya utilitas (listrik, air, gas) minimal 5% dalam 3 bulan` | 0% |

### PPIC

Template `STAFF PPIC`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.2 | `REVENUE 240M: OTIF (On Time In Full) / Fill Rate` | Finished good yang dikirim ke WH FG tepat waktu dan dalam jumlah lengkap sesuai yang planning produksi |
| 0.2 | `Inventory Turnover Ratio (ITO) / Perputaran Persediaan` | ITO tinggi menandakan perputaran barang cepat dan manajemen stok efisien. ITO rendah bisa berarti overstock atau barang lambat laku. |
| 0.25 | `Stock Accuracy (Akurasi Stok)` | Memastikan integritas data. PPIC sangat bergantung pada data stok; jika data salah, perencanaan produksi dan pembelian akan kacau. Target umum adalah 98-100%. |
| 0.2 | `Stockout Rate (Tingkat Kekurangan Stok)` | Menghindari terhentinya lini produksi atau hilangnya penjualan karena barang tidak ada. |
| 0.15 | `Factory Utilization (Utilisasi Pabrik)` | Aset pabrik (mesin dan manusia) digunakan secara optimal. Terlalu rendah berarti idle capacity (boros), terlalu tinggi (di atas 90%) bisa berisiko jika ada lonjakan permintaan darurat. |

### Warehouse Leader

Template `LEADER WAREHOUSE`, 8 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.2 | `Melakukan cycle count secara rutin dan terjadwal ( Secara Mingguan )` | Cycle count Bulanan selesai sesuai jadwal dengan akurasi 100% |
| 0.15 | `Menjalankan sistem FIFO/FEFO secara konsisten` | Kepatuhan FIFO/FEFO ≥ 98%. |
| 0.15 | `Mencegah over-dispensing (bahan diberi lebih banyak dari yang dibutuhkan)` | Selisih antara bahan di-issue dan bahan dipakai ≤ 0,5%.( Khusus Serbuk & Cair) |
| 0.15 | `Mengurangi kerusakan material selama penyimpanan` | Kerusakan bahan baku turun dari baseline ≥5% |
| 0.1 | `Penerapan GMP di warehouse (kebersihan, pest control, zoning area, suhu & humidity)` | 100% warehouse comply dengan checklist GMP bulanan |
| 0.05 | `Memastikan Update kartu stok & dashboard FIFO/FEFO` | Memastikan 100% kartu stok ter-update ≤ H+1 setelah stock check |
| 0.05 | `Memberikan update progres pekerjaan & aspirasi saat 1-on-1 (menjaga stabilitas mood, memberikan solusi, mengajukan bahan diskusi ke atasan)` | 100% mengikuti 1-on-1 bulanan |
| 0.15 | `Mencegah over-dispensing (bahan diberi lebih banyak dari yang dibutuhkan) 2` | Selisih antara bahan di-issue dan bahan dipakai ≤ 0,5%.( Khusus Serbuk & Cair) |

### Warehouse Staff

Template `STAFF WAREHOUSE`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Zero miss-pick stock 1` | Melakukan stock check berkala untuk mencegah kesalahan picking yang menyebabkan complain |
| 0.3 | `Zero miss-pick stock 2` | Ketepatan Picking (Kesesuaian item, batch, dan quantity) |
| 0.2 | `Kerapihan dan Kebersihan Area` | Penerapan GMP di warehouse (kebersihan, pest control, zoning area, suhu & humidity) |
| 0.2 | `Ketepatan Loading dan Unloading` | Barang tidak rusak dan sesuai dokumen |

## Procurement

2 template, 10 metrik. Klasifikasi otomasi: **4 / 2 / 0 / 4**.

### Leader

Template `KPI Leader Procurement`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.4 | `Revenue 240M` | Menjamin Produksi Berjalan Tanpa Shortage dengan target zero production stop karena kekurangan material dan pembuatan SLA untuk semua pembelian R/P materials 100% |
| 0.2 | `Net Income 20%` | Optimasi Inventory & Cashflow dengan target perencanaan kebutuhan (MRP) akurasi ≥ 95% |
| 0.1 | `Penurunan HPP 5%` | Mengembangkan Skema Kontrak Jangka Panjang (volume-based, price lock, rebate) dengan Mendapatkan rebate/bonus minimal 3-5% dari nilai pembelian tahunan. |
| 0.2 | `Credit Terms dari Vendor Rata-Rata N+60 hari` | Negosiasi Ulang Dengan Vendor Untuk Memperpanjang Credit Term Menjadi Rata-Rata 60 hari dengan target Minimal 80% dari total vendor strategis memiliki credit term N+60 hari pada akhir Q2 |
| 0.1 | `Perfoirmance TIM` | Perfomance TIM dengan target KPI minimal 70 |

### Staff Inventory

Template `KPI Staff Inventory`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.4 | `Revenue 240M` | Availability material produksi dengan target ketersediaan stock bahan baku 100 % sesuai planning PPIC dan tidak ada stop produksi karena kekurangan material |
| 0.2 | `Revenue 240 M` | Material yang dipesan datang sesuai dengan waktu yang sudah dijanjikan (ETA) dengan target On Time Delivery Supplier (≥ 95%) |
| 0.2 | `Penurunan HPP 5%` | Efisiensi Harga Pembelian dengan target Selisih harga vs last price / standard cost ( saving ≥5% ) YOY |
| 0.1 | `Penurunan HPP 5% - 2` | Evaluasi Vendor dengan target melakukan evaluasi pelayanan vendor ( Maks 70 % dari jumlah Vendor ) |
| 0.1 | `Penurunan HPP 5% - 3` | Compliance GMP & QA material dengan target material sesuai standar QC ( Target 100 % sesuai ) |

## Quality

4 template, 18 metrik. Klasifikasi otomasi: **1 / 2 / 8 / 7**.

### QA Leader

Template `KPI QA Staff`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.4 | `Average QA relelase time sejak batch production selesai` | Melakukan percepatan pre-check batch record dengan target <20 jam batch record setelah dokumen diterima |
| 0.15 | `Testing cost per batch turun 15% dengan optimalisasi alat dan metode` | Testing alat ukur bulanan terselesaikan sesuai jadwal |
| 0.25 | `Zero major finding saat external audit (BPOM)` | Melakukan audit area QC, porduksi, penyimpanan, serta dokumen setiap 2x dalam sebulan |
| 0.2 | `Kaizen dan Growth` | Melakukan Review Kesesuaian SOP & WI di Area Produksi dengan target 5 produk/bulan |

### QC Assistant

Template `KPI QC Assistant`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Complain/Rejection` | Persentase bahan kemas yang diluluskan oleh QC Oleh Tim Produksi |
| 0.3 | `Raw Material Checking` | Persentase pengecekan bahan kemas selesai sebelum tenggat waktu retur yang diberikan supplier dengan maksimal 3 hari |
| 0.3 | `Zero major finding saat external audit (BPOM)` | Pelaksanaan pengendalian ruang penyimpanan bahan dan penyimpanan produk jadi |
| 0.1 | `Growth` | Kemampuan Multi-Tasking di Area Quality |

### QC Production

Template `KPI Quality Staff - Production`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.25 | `Revenue 240M` | Mempercepat penyelesaian dokumen catatan pengujian pengolahan dan pengemasan batch dengan target maksimal 12 Jam setelah penerimaan CPPB |
| 0.25 | `Complain/Rejection Maks.5%` | Melakukan In-Process Control Tiap Tahap Produksi dengan target 100% produksi berhasil |
| 0.15 | `Complain/Rejection Maksimal 5%` | Tidak ada complain kualitas produk dari Marketing dengan target jumlah komplain maksimal 12 produk tiap bulan |
| 0.15 | `Raw Material checking` | Meningkatkan incoming inspection untuk raw material dan packaging dengan target laporan maks. 3 hari kerja |
| 0.2 | `Zero major finding saat external audit (BPOM)` | Pelaksanaan pengendalian ruang produksi dan penyimpanan bahan baku dengan 100% area produksi, penyimpanan diaudit setiap minggu |

### Quality Supervisor

Template `KPI Quality Supervisor`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.15 | `Revenue 240M` | Mempercepat release produk agar tidak menunda shipment dengan Average QA Release Time ≤24 jam sejak batch production selesai |
| 0.25 | `Complain/Rejection Maks.5%` | Zero complain per bulan dengan persentase jumlah complain 15/bulan |
| 0.15 | `Defect rate maksimal 2% per satu bulan produksi` | Meningkatkan incoming inspection untuk raw material dan packaging dengan incoming inspection raw material dengan laporan maks. 3 hari kerja |
| 0.15 | `Zero major finding saat external audit (BPOM)` | Melaksanaan internal audit kualitas secara bulanan dengan target tidak ada temukan hal yang melanggar (unsur CAPA) |
| 0.3 | `Performance Monitoring Team` | KPI Team minimal target skor 70 |

## Tech Development

7 template, 30 metrik. Klasifikasi otomasi: **14 otomatis / 9 semi / 0 terblokir / 7 manual**.

### Backend Developer

Template `Backend Developer`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Delivery` | Kesesuaian dengan requirements dan timeline /Project |
| 0.35 | `Quality` | Kualitas dan performa sistem |
| 0.2 | `Support` | Support dan Troubleshooting |
| 0.15 | `Improvement` | Improvement dan otomasi |

### Frontend Developer

Template `Frontend Developer`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.3 | `Delivery` | Kesesuaian dengan requirements dan timeline /Project |
| 0.35 | `Quality` | Kualitas dan performa sistem |
| 0.2 | `Support` | Support dan Troubleshooting |
| 0.15 | `Improvement` | Improvement dan otomasi |

### Fullstack Developer

Template `Fullstack`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.5 | `System Development` | Penyelesaian Project Development Software & Uprgade Fitur Penunjang Operational |
| 0.2 | `Implementasi` | Monitoring Implementasi Sinkronisasi/Review dengan Requester |
| 0.2 | `Customer Satifaction` | Survey Penilaian Software yang sudah diimplementasikan |
| 0.1 | `Kaizen` | Ide Improvement |

### IT Infrastructure

Template `Infrastruktur`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.1 | `Infrastruktur` | Otomasi & Deployment |
| 0.1 | `Network` | Arsitektur jaringan sesuai requirements |
| 0.1 | `System` | System uptime 99% |
| 0.1 | `Server` | Server uptime 99% |
| 0.6 | `Support` | Support System |

### IT Support

Template `IT Support`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.4 | `Network` | Optimalisasi Uptime Server & Sistem |
| 0.15 | `Customer Satisfaction` | Kepuasan Pelayanan IT Support |
| 0.3 | `Problem Solving` | Penyelesaian E - Ticket sesuai dengan SLA ( Service Level Agreement ) |
| 0.15 | `Kaizen` | Improvement |

### Tech Development Leader

Template `Leader`, 5 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.2 | `Revenue 240M` | Menjamin operasional IT tanpa gangguan |
| 0.1 | `Net income 20%` | Pengendalian anggaran IT |
| 0.2 | `Integration System Development di Q4` | On-time project delivery rate (%) – proyek IT/development selesai sesuai timeline |
| 0.1 | `Customer Satifaction` | Average Tingkat Kepuasan User Terhadap Pelayanan Team IT ( Fullstack & Support ) |
| 0.4 | `Performance Monitoring Team` | KPI Team |

### Tech Development Supervisor

Template `Supervisor KPI`, 4 metrik.

| Bobot | Label | Target / keterangan |
|---:|---|---|
| 0.2 | `Revenue 240M` | Menjamin operasional IT tanpa gangguan |
| 0.1 | `Net income 20%` | Pengendalian anggaran IT |
| 0.4 | `Integration System Development di Q4` | Menyelesaikan Fitur Baru Sesuai Request SPV All Dept / Bulan |
| 0.3 | `Performance Monitoring Team` | KPI Team |

## Dokumen Terkait

- [[RUN - Menambah Metrik KPI Otomatis]] (cara mengerjakan otomasinya)
- [[HRIS - Otomasi Skor KPI]] (analisis kelayakan, peta sumber data, rencana bertahap)
- [[HRIS - Key Performance Index]] (mekanisme scoring, RBAC, cakupan tim Leader)
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] (batas service)
- [[Microservices - Employee Service]] (pemilik koleksi kpi_template dan kpi_score)
