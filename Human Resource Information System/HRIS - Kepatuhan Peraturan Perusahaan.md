# HRIS - Kepatuhan Peraturan Perusahaan

## Deskripsi

*Peta selisih antara Peraturan Perusahaan PT Bharata Internasional Pharmaceutical 2026-2028 dan apa yang benar-benar dijalankan sistem. Untuk tiap aturan: apa yang diatur, apa yang berjalan, di mana nilainya tinggal, berapa nilainya di produksi, dan apakah keduanya cocok. Dokumen ini BUKAN sumber kebenaran aturan; sumbernya `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`, dan bila keduanya bertentangan, dokumen itu yang menang.*

- **Status**: ⚠️ **Peta terisi untuk potongan kehadiran, keterlambatan, dan sanksi; cuti dan lembur baru sebagian.** Diukur ke kode dan ke produksi 2026-09-01. Bukan hasil pembacaan menyeluruh atas seluruh pasal.
- **Keputusan**: [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]]
- **Implementasi**: [[Microservices - Payroll Service]] · [[Microservices - Attendance Service]] · [[Microservices - Employee Service]]

## Latar Belakang

Aturan yang menentukan gaji dan sanksi tidak tinggal di vault. Ia tinggal di repo mobile sebagai `BUSINESS_LOGIC_IMPLEMENTATION.md`, berukuran 6,4 KB, terakhir disunting 2026-05-26, dan tidak akan ditemukan oleh orang yang mengerjakan payroll di `bip-erp` kecuali ia mencarinya. Sebagian aturan sudah menetes ke vault tetapi tersebar di enam dokumen teknis, sehingga tidak ada satu tempat pun yang bisa menjawab pertanyaan "sistem patuh atau tidak".

Akibat nyatanya sudah terjadi dua kali. Potongan mangkir pernah dirancang dan diimplementasikan sebesar 1x, setengah dari yang diatur Pasal 20, lolos `/plan` dan `/implement`. Dan penyimpangan pengali di produksi ditemukan 2026-08-26, ditulis lengkap beserta dampak rupiahnya, lalu tidak ditindaklanjuti siapa pun.

## Ruang Lingkup

Yang dipetakan: aturan yang menentukan **uang, sanksi, jatah, dan ambang disiplin**. Yang tidak dipetakan di sini: jadwal shift per kategori, ketentuan biometrik, dan pasal-pasal yang tidak diterjemahkan jadi perilaku sistem.

**Cara membaca kolom "Nilai tinggal di"**, karena ini yang paling sering disalahpahami:

- **Konstanta Go** berarti mengubahnya menuntut deploy, dan nilainya terlihat dari kode
- **Config** berarti HR menyuntingnya dari layar tanpa deploy, dan ⛔ **nilainya TIDAK terlihat di kode mana pun**; satu-satunya cara mengetahuinya adalah membaca produksi
- **Master data** berarti tersimpan per perusahaan atau per karyawan, dan bisa berbeda antar orang

Baris bertanda ° belum saya buka sendiri dan berasal dari penelusuran; ia perlu diverifikasi ulang sebelum dipakai sebagai dasar keputusan.

## Peta Kepatuhan

### Potongan kehadiran (Pasal 20)

| Yang diatur | Yang dijalankan | Nilai tinggal di | Nilai prod (2026-09-01) | Status |
|---|---|---|---|---|
| Mangkir 1 hari potong **1,5x** tunjangan kehadiran | pengali dibaca dari config | Config `payroll_config.attendance_deduction.alpha_multiplier_one_day`. Default kode **1,5** (`services/payroll/models_config.go:264`, berkomentar "Peraturan Perusahaan Pasal 20") | **2** | ⛔ **MENYIMPANG** |
| Mangkir ≥2 hari potong **2x per hari** | sama, dikali jumlah hari | Config `alpha_multiplier_multi_day` | **2** | ✅ cocok |
| Izin jam kerja memotong tunjangan kehadiran dan uang makan, **tanpa ambang** | uang makan hangus hanya bila tak hadir > 4 jam | Config `meal_threshold_hours` | **4** | ⛔ **MENYIMPANG SADAR**, keputusan pemilik produk 2026-08-20, belum ber-ADR |
| tidak diatur di PP | potongan telat = tunjangan kehadiran / 173 per jam | Config `hour_divisor` | **173** | kebijakan perusahaan, di luar PP |
| tidak diatur di PP | potongan izin = tunjangan kehadiran / 26 per hari | Config `day_divisor` | **26** | kebijakan perusahaan, di luar PP |
| tidak diatur di PP | potongan uang makan Rp 10.000 per hari | Config `meal_deduction` | **10000** | kebijakan perusahaan, di luar PP |

⛔ **Dampak penyimpangan pengali sudah terukur, dan jendela perbaikannya masih terbuka.** Dua `payroll_run` di produksi keduanya berstatus `draft` (periode `2026-06` dan `2026-07`), jadi belum ada rupiah yang sampai ke karyawan. Delapan baris ber-mangkir tepat satu hari dipotong Rp 565.065; pada 1,5x seharusnya Rp 423.799, jadi **kelebihan potong Rp 141.266**. Begitu satu run di-`approve` lalu `published`, slip men-snapshot angkanya dan koreksi menuntut pembatalan run, bukan sekadar mengubah config.

### Keterlambatan dan pengunduran diri (Pasal 19)

| Yang diatur | Yang dijalankan | Nilai tinggal di | Nilai prod | Status |
|---|---|---|---|---|
| Terlambat **3x per bulan** otomatis memicu SP1 | sistem **mengusulkan**, HR yang menerbitkan | Konstanta Go `ambangTelatSP1 = 3` (`services/employee/warning_suggest.go:34`) | 3 | ⚠️ **MENYIMPANG SADAR** pada kata "otomatis"; alasan ditulis di `warning_suggest.go:22-31`, belum ber-ADR |
| Terlambat **5x per bulan** tanpa keterangan dikualifikasikan mengundurkan diri | tidak ditemukan implementasinya | tidak ada | tidak ada | ⛔ **BELUM ADA** |
| Mangkir **6 hari berturut-turut** dikualifikasikan mengundurkan diri | tidak ditemukan implementasinya | tidak ada | tidak ada | ⛔ **BELUM ADA** |
| tidak diatur di PP | toleransi tepat waktu, bawaan 1 menit ° | Config per perusahaan `company_attendance_setting` | ° | kebijakan, belum ber-ADR |
| tidak diatur di PP | ambang mulai memotong jam, bawaan 11 menit ° | Config per perusahaan | ° | kebijakan, belum ber-ADR |

⚠️ "Per bulan" di sini berarti **periode payroll tanggal 26 sampai 25**, bukan bulan kalender.

### Sanksi (Pasal 53 sampai 56)

| Yang diatur | Yang dijalankan | Nilai tinggal di | Nilai prod | Status |
|---|---|---|---|---|
| SP II memotong **25% gaji pokok** selama masa aktifnya | **tidak ada.** Payroll tidak pernah membaca catatan SP | tidak ada | `employee_warning` = **0 dokumen** | ⛔ **BELUM ADA** |
| Masa aktif SP **6 bulan** sejak terbit | dihitung dalam bulan kalender | Konstanta Go `WarningValidityMonths = 6` (`shared-library/models/employee/warning.go:121`) | 6 | ✅ cocok |
| SP III memberi hak PHK sepihak, dengan masa perbaikan 1 bulan | tidak ada eskalasi otomatis SP1 ke SP2 ke SP3 | tidak ada | tidak ada | ⛔ **BELUM ADA** |
| Skorsing maksimal 3 bulan, akses dicabut otomatis, upah tetap dibayar | tidak ditemukan implementasinya | tidak ada | tidak ada | ⛔ **BELUM ADA** |
| Denda pelanggaran informasi rahasia **Rp 2.000.000.000** | tidak ditemukan implementasinya | tidak ada | tidak ada | ⛔ **BELUM ADA** |
| Denda penyalahgunaan wewenang **Rp 5.000.000.000** | tidak ditemukan implementasinya | tidak ada | tidak ada | ⛔ **BELUM ADA** |

⛔ **Klaim "payroll tidak membaca SP" diverifikasi dengan `git grep`, bukan `Grep`, beserta kontrol positif.** Pola `EmployeeWarning|employee_warning` mengembalikan **nol** kecocokan di `services/payroll/` sementara pola yang sama menemukan 6 berkas di repo, jadi polanya memang bekerja. Delapan kemunculan kata "peringatan" di `services/payroll` seluruhnya merujuk **peringatan validasi baris impor**, bukan Surat Peringatan. Pemeriksaan ini dilakukan karena penelusuran pertama melaporkan hasil kosong dengan pola yang berbeda, dan hasil kosong tidak pernah cukup untuk menegakkan klaim negatif.

### Cuti dan izin (Pasal 15 sampai 18)

| Yang diatur | Yang dijalankan | Nilai tinggal di | Nilai prod | Status |
|---|---|---|---|---|
| Jatah **12 hari kerja** setelah 12 bulan bekerja | kuota diisi **manual per karyawan** oleh HR; tidak ada aturan penerbitan ° | Master data `work_data.vacation.quota` | 123 dari 180 karyawan berkuota **5** ° | ⛔ **BELUM ADA** aturannya di sistem |
| Tambahan **2 hari** untuk masa kerja ≥ 5 tahun | tidak ditemukan implementasinya ° | tidak ada | tidak ada | ⛔ **BELUM ADA** |
| Cuti hangus akhir tahun berikutnya | cron 1 Januari me-reset pemakaian, sisa hangus lebih cepat ° | Konstanta Go, jadwal cron ° | ° | ⛔ **MENYIMPANG** |
| Durasi izin dibayar: nikah 5, nikah anak 3, istri melahirkan 3, kematian keluarga 5, kematian saudara 1, wisuda 1, sunat/baptis 2, bencana 1 | katalog durasi maksimum per subtipe ° | Konstanta Go `LeaveSubtypeDetails` ° | ° | ⚠️ sebagian cocok, perlu pembandingan baris per baris |
| Melahirkan 1,5 bulan sebelum + 1,5 bulan sesudah | katalog mencatat 90 hari ° | Konstanta Go ° | ° | ⚠️ perlu dipastikan apakah 90 hari sama dengan 3 bulan kalender |
| Ibadah haji pertama maksimal 50 hari | tidak ditemukan di katalog ° | ° | ° | ⚠️ perlu diperiksa |

⚠️ `vacation.quota` **bukan** jatah tahunan melainkan sisa setelah Cuti Bersama dipotong HR di luar sistem, sehingga angka 5 bukan bukti penyimpangan dari 12. Ini justru contoh kenapa peta ini perlu kolom "yang dijalankan": angka yang sama bisa berarti dua hal.

### Lembur (Pasal 25)

| Yang diatur | Yang dijalankan | Nilai tinggal di | Nilai prod | Status |
|---|---|---|---|---|
| Lembur sah hanya dengan **SPKL** tertulis dari atasan | tidak ada validasi SPKL sebelum perhitungan upah | tidak ada | tidak ada | ⛔ **BELUM ADA** |
| Hanya **tim produksi** berhak upah lembur | tidak ada pembedaan produksi dan non-produksi | tidak ada | tidak ada | ⛔ **BELUM ADA** |
| Tarif lembur mengikuti ketentuan | `jam × (gaji pokok / 173)`, pengali DJTK 1,5x dan 2x masih TBD | **Konstanta Go hardcode** `services/payroll/payroll_calc.go:327` | 173 | ⛔ **BELUM SESUAI** |

⛔ **Asimetri yang layak diperhatikan**: pembagi jam untuk **potongan** adalah config yang bisa disunting HR (`hour_divisor`), sedangkan pembagi jam untuk **lembur** hardcode. Mengubah setelan itu di layar membuat satu jam bernilai berbeda saat menambah dan saat mengurangi, tanpa ada yang memberi tahu.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Manajemen | Direksi dan kepala departemen | pembaca vault, sebagian lewat [[Microservices - Vault MCP Service]] | Claude / Obsidian |
| HRD | Human Resource / Personalia | penyunting config potongan (`payroll.config`), penerbit SP | Web ERP |
| Developer | Tech Development | pembaca dan pengubah kode | Obsidian / editor |

- **Tujuan**: menjawab "sistem menjalankan aturan apa, dan di mana ia berbeda dari peraturan" tanpa membaca kode Go.
- **Pain point**: aturannya tersebar di dokumen repo mobile, enam dokumen vault, dan 638 komentar di 347 berkas Go; nilai yang menentukan rupiah bahkan tidak terlihat di kode mana pun.
- **Aksi utama**: membuka satu halaman, membaca baris berstatus ⛔, lalu memutuskan memperbaiki sistem atau menerbitkan ADR penyimpangan.

## Konsumen Data

- [[Microservices - Payroll Service]] — enam angka config yang jadi baris ⛔ pertama di peta ini
- [[HRIS - Disciplinary (Surat Peringatan)]] — aturan SP yang sebagian besar belum punya efek apa pun
- [[HRIS - Payroll]] — tabel tarif yang jadi bahan baris potongan kehadiran

## Kendala

- **Kolom nilai produksi basi sejak ditulis.** Ia config yang bisa disunting HR kapan saja tanpa deploy dan tanpa jejak di kode. Karena itu tanggal ukur wajib, dan nilai tanpa tanggal diperlakukan sebagai tidak diketahui.
- **Peta ini tidak memeriksa dirinya sendiri.** Tidak ada yang gagal bila ia menyimpang dari kode.
- **Repo vault publik.** Peta ini memuat aturan dan nilai konfigurasi, **tidak boleh memuat gaji atau data pribadi siapa pun**.

## Belum Diputuskan (TBD)

- **Berapa seharusnya `alpha_multiplier_one_day` di produksi.** Nilai 2 disetel sengaja oleh orang bernama pada 2026-08-21; bila itu memang dikehendaki HRD, ia wajib jadi ADR, dan bila tidak, config harus dikembalikan ke 1,5 sebelum run pertama di-`approve`.
- **Ambang 4 jam untuk uang makan**, menyimpang dari PP yang tidak menyebut ambang. Sudah dua kali diminta jadi ADR.
- **Kata "otomatis" pada pemicu SP1.** Sistem sengaja hanya mengusulkan; ini perlu ADR atau perlu diluruskan.
- **Perusahaan mana yang jadi acuan.** `payroll_config.company.name` di produksi berbunyi `CV Pure Glow Lux`, sementara peraturan yang dipetakan di sini milik PT Bharata Internasional Pharmaceutical, dan config itu `_id: singleton` untuk semua.
- Apakah sanksi yang belum ada (SP II potong 25%, skorsing, denda Pasal 54) memang **sengaja tidak dibangun**, atau tertunda.

## Dokumen Terkait

- [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]]
- [[HRIS - Payroll]] · [[Microservices - Payroll Service]] · [[HRIS - Disciplinary (Surat Peringatan)]]
- [[HRIS - Attendance System]] · [[Microservices - Attendance Service]] · [[HRIS - Overtime]]
- [[HRIS - Leave Request]] · [[HRIS - Compensation & Benefits]]
- [[ADR - 0061 Jatah Cuti Tahunan Terbit Otomatis di Ulang Tahun Kontrak]]
