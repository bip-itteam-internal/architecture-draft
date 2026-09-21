## Deskripsi

*Sistem ronda (patroli) berjadwal untuk posisi Security: petugas mengirim satu putaran ronda per jendela waktu lewat [[APP - MyBharata]], lengkap dengan koordinat, jam, area yang dicek, dan foto temuan. Temuan naik jadi tiket ke Building Maintenance yang sudah berjalan. Angka KPI ketepatan ronda lahir sebagai produk sampingan dari pekerjaan yang tercatat, bukan sebagai tujuan pertamanya.*

- **Status**: 🟡 Konsep / Direncanakan. Belum ada kode. Rancangan disetujui 2026-09-21, implementasi belum dimulai.
- **Path di repo**: TBD (rencananya `bip-erp/services/attendance`, lihat [[ADR - 0112 Ronda Security di Attendance Service, GPS Membuktikan Lokasi Bukan Titik]])
- **Pemilik**: GA Security. Atasan penilai: SPV HRGA.

## Latar Belakang

Template KPI `Security Team` punya empat metrik. Sampai 2026-09-21, **dua di antaranya belum punya sumber sama sekali** dan satu menunggu modul yang belum ada, sehingga [[GA - Dashboard per Posisi]] menyimpulkan posisi ini ⛔ tidak layak dibuatkan dashboard menurut [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]].

Sumbu kedua ADR itu (antrean, tenggat, persetujuan) juga kosong: Security tidak punya satu pun pekerjaan yang menunggu di sistem mana pun. Itulah yang dijawab dokumen ini. **Membangun alat kerjanya lebih dulu adalah yang mengisi sumbu kedua**, dan angka KPI menyusul sesudahnya. Urutan sebaliknya menghasilkan layar yang lahir cuma untuk mengisi angka, lalu tidak dipakai siapa pun.

## Keadaan Terukur per 2026-09-21

Diukur ke `origin/main` `bip-erp` commit `6ef719e3`. **Sebagian dokumentasi lama tentang posisi ini sudah usang**, dan perbedaannya besar, jadi jangan berangkat dari ingatan.

| Metrik | Bobot | Keadaan sebenarnya |
|---|---:|---|
| Rating pelayanan dan keamanan | 0,3 | ❌ belum dipetakan, butuh keputusan pemilik KPI |
| Kepatuhan patroli tiap 3 jam | 0,3 | 🟡 dokumen ini. Kata `patroli` nol hasil di seluruh `origin/main` |
| Kepatuhan SOP security | 0,2 | ❌ belum dipetakan. Berpeluang menumpang `ceklis_kpi`, lihat di bawah |
| Kerapihan dan kebersihan pos jaga | 0,2 | ✅ **sudah punya sumber**: `nilai_inspeksi_satgas` |

⚠️ **Baris terakhir itu koreksi.** `kpi_sumber_inspeksi_satgas.go` komentarnya menyebut eksplisit bahwa ia menjawab metrik Security "Kerapihan dan kebersihan Pos" ([[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] §8). Merged, live di dev, **prod belum**. Dokumentasi yang menyatakan metrik ini terkunci menunggu modul checklist sudah tidak berlaku.

⚠️ **Mekanisme checklist generik sudah ada, namanya `ceklis_kpi`** (`services/employee/kpi_sumber_ceklis.go`). Ia menautkan satu metrik KPI ke **satu butir pertanyaan** form-builder lewat UID butir, bukan lewat judul form atau urutan pertanyaan. Metrik yang dinilai "sudah atau belum" oleh seorang penilai tidak perlu modul baru sama sekali. Kandidat terkuat: kepatuhan SOP security.

⛔ **Yang benar-benar tidak bisa menumpang apa pun adalah ronda tiap 3 jam.** Recurrence form-builder hanya mengenal `monthly` dan `weekly` (`services/form-builder/models_period.go:13-14`), tidak ada harian apalagi per-tiga-jam. Menambahkan satuan sub-harian ke sana berarti mengubah model periode yang dipakai bersama Kaizen, Satgas, dan `ceklis_kpi`, yaitu mengubah satu fakta yang dipegang banyak konsumen demi satu pemakai baru.

## Apa yang GPS Boleh dan Tidak Boleh Klaim

**Bagian terpenting dokumen ini.** Bukti lokasi di sini sengaja dibatasi, dan batas itu wajib ikut ke layar.

Geofence yang sudah ada memakai radius bawaan **800 meter**, dengan minimum yang boleh disetel **50 meter** (`services/attendance/attendance_setting.go:53-55`). Komentarnya menjelaskan kenapa longgar: lokasi kerap resolve ratusan meter dari titik sebenarnya, dan menolak orang yang benar-benar hadir jauh lebih merugikan daripada menerima yang di seberang jalan.

Konsekuensinya tegas:

- ✅ **Boleh diklaim**: petugas berada di area lokasi saat mengirim, dan rondanya terkirim di dalam jendela waktunya.
- ⛔ **TIDAK boleh diklaim**: petugas benar-benar mendatangi satu titik tertentu. Titik ronda di dalam satu lokasi umumnya berjarak jauh di bawah 50 meter, jadi GPS tidak bisa membedakan gerbang depan dari pagar belakang.

Karena itu area yang dicek **dinyatakan sendiri oleh petugas** dan disimpan apa adanya sebagai pernyataan, bukan sebagai verifikasi. Layar dilarang menampilkan bentuk seperti "6/6 titik terverifikasi", karena itu menjanjikan sesuatu yang datanya tidak sanggup dukung. Kelas kegagalannya sudah berulang di ERP ini: angka yang mulus, masuk akal, dan keliru, yang tak satu pun test menangkapnya dan keluhannya datang berhari-hari kemudian.

Bila kelak dibutuhkan bukti per-titik, mekanismenya bukan memperketat radius melainkan menambah penanda fisik di titiknya (QR atau NFC). Itu keputusan terpisah dan belum diambil.

## Bentuk yang Dipilih

Tiga bentuk dipertimbangkan 2026-09-21: ronda terjadwal plus temuan, buku jaga digital, dan memperluas [[GA - Guestbook System (Complete)]]. **Yang dipilih ronda terjadwal plus temuan.** Buku jaga ditolak untuk irisan pertama karena catatan bebas sulit diangkakan sehingga menunda manfaat KPI-nya. Memperluas Guestbook ditolak karena Guestbook adalah funnel publik tanpa login yang digerbang token per-kunjungan, sedangkan ronda menuntut identitas petugas, dan menyatukan keduanya mencampur permukaan publik dengan permukaan ber-identitas.

### Tempat tinggal

Modul tinggal di `attendance-service`, **bukan service baru**. Alasannya di [[ADR - 0112 Ronda Security di Attendance Service, GPS Membuktikan Lokasi Bukan Titik]]; ringkasnya, resolusi shift di sini berlapis tiga dan wajib dipanggil bukan disalin.

### Model data

Dua koleksi baru di `attendance_db`, sengaja hanya dua:

**`security_patrol_round`** (satu dokumen per ronda terkirim): `employee_id`, `company_id`, `submitted_at`, `window_start`, `coordinate` (`common.GPSCoordinate`), `within_site` (hasil pemeriksaan jarak, **disimpan sebagai hasil** supaya penilaian lama tidak berubah ketika titik atau radius lokasi disetel ulang), `areas[]`, `note`.

**`security_patrol_finding`** (satu dokumen per temuan): `round_id`, `area`, `description`, `photo_file_id`, `ticket_id`, `status`.

### Ronda yang diharapkan diturunkan, tidak disimpan

Daftar ronda yang seharusnya ada **dihitung saat baca** dari shift petugas dan satu setelan interval, bukan diarsipkan sebagai dokumen.

Ini keputusan sadar. Bila diarsipkan, ia langsung jadi fakta kedua yang menyimpang begitu shift seseorang diubah atau ditukar, dan gejalanya berupa ronda "terlewat" atas jam yang orangnya memang sudah tidak bertugas. Pembekuan penilaian tetap terjadi, tetapi di tempat yang memang sudah membekukannya, yaitu skor KPI periode tertutup.

### Interval jadi setelan, bukan konstanta

Angka "tiap 3 jam" menempel di setelan per perusahaan bersama titik dan radius lokasi yang sudah ada. Menuliskannya sebagai konstanta di backend dan sekali lagi di frontend adalah bentuk paling umum dari satu fakta di dua tempat, dan di sini ongkosnya jatuh langsung ke penilaian orang.

## Bagian yang Dipakai Ulang

Hampir seluruh bahannya sudah ada. Tabel ini yang membuat irisan pertamanya kecil.

| Kebutuhan | Sudah ada di | Catatan |
|---|---|---|
| Hitung jarak dua titik | `checkDistanceGPS` (Haversine), `services/attendance/main.go:4162` | panggil, jangan tulis ulang |
| Titik dan radius lokasi | `resolveOfficeGeofence`, `services/attendance/attendance_setting.go:74` | sudah punya validasi lat/long |
| Siapa sedang bertugas | `RosterEntry`, `shared-library/models/attendance/models.go:801` | resolusi berlapis tiga, wajib lewat resolver aslinya |
| Tipe koordinat bersama | `common.GPSCoordinate` | shared-library |
| Unggah foto | file-service | pola `file_fields` yang dipakai Satgas |
| Menyalurkan ke KPI | `kpi_sumber_*.go` + `/internal/*/metrics` | batasnya di [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] |
| Tiket temuan | [[Microservices - Task Management Service]] | space `Building Maintenance` sudah berjalan |

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Petugas Security | pelaksana ronda, GA Security | karyawan biasa, hanya ronda miliknya | MyBharata (Android) |
| SPV HRGA | penilai, melihat ronda terlewat | modul `ga` / `hris` | Web ERP |
| GA Staff Building | penerima temuan jadi tiket | space Building Maintenance | Web ERP |

- **Tujuan** petugas: menyelesaikan shift tanpa tuduhan lalai, dan punya tempat melaporkan temuan yang benar-benar ditindaklanjuti.
- **Pain point** hari ini: pekerjaannya tak terekam di mana pun, sehingga penilaiannya sepenuhnya kesan atasan. Guestbook yang jelas-jelas kerja nyata mereka **tidak muncul di satu pun metrik KPI-nya**.
- **Aksi utama**: kirim ronda, lampirkan temuan, lihat ronda berikutnya kapan.

## Belum Diputuskan (TBD)

- **Rating pelayanan dan keamanan (bobot 0,3)** diukur dari apa. Belum dipetakan, dan ini keputusan pemilik KPI, bukan tebakan yang boleh diambil dari dokumen ini.
- **Kepatuhan SOP security (bobot 0,2)**: apakah cukup lewat `ceklis_kpi` dengan penilai SPV, atau menuntut bentuk lain.
- **Apakah Guestbook layak masuk KPI Security.** Ia pekerjaan nyata yang sudah tercatat rapi, tetapi ketidakhadirannya di KPI adalah pertanyaan untuk HR, bukan celah yang boleh ditambal frontend.
- **Ronda di luar shift reguler** (lembur, hari libur, shift malam yang melewati tengah malam) belum dirancang penanganannya.
- **Serah terima shift dan pencatatan insiden** sengaja di luar irisan pertama. Keduanya bisa menyusul tanpa membongkar model di atas.
- **Bukti per-titik** (QR atau NFC di titik ronda) bila kelak dituntut. Bukan dengan memperketat radius.

## Dependensi & Integrasi

- [[Microservices - Attendance Service]] (tempat tinggal, roster, geofence)
- [[Microservices - Task Management Service]] (temuan jadi tiket Building Maintenance)
- [[Microservices - Employee Service]] (sumber KPI, lewat `/internal/*/metrics`)
- [[APP - MyBharata]] (layar petugas) · [[APP - Web ERP]] (layar atasan)

## Dokumen Terkait

- [[ADR - 0112 Ronda Security di Attendance Service, GPS Membuktikan Lokasi Bukan Titik]] — keputusan yang mengikat rancangan ini
- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — kenapa alat kerja dibangun lebih dulu
- [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] — yang sudah menjawab metrik pos jaga
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] — batas pengumpul metrik
- [[GA - Dashboard per Posisi]] · [[GA - Big Pictures]] · [[GA - Checklist Management]]
- [[GA - Guestbook System (Complete)]] — modul operasional Security yang sudah berjalan
- [[GA - Building Maintenance]] — tujuan eskalasi temuan
- [[HRIS - Matriks KPI per Departemen]] — sumber angka bobot metrik
- [[REF - Kepemilikan Data]] — sebelum menambah penyimpanan fakta baru
