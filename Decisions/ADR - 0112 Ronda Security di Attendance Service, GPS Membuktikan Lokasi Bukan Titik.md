**Status**: 🟡 Diputuskan 2026-09-21, **belum ada kode**. Rancangan lengkapnya di [[GA - Ronda Security]]. Diukur ke `origin/main` `bip-erp` commit `6ef719e3`; kata `patroli` nol hasil di seluruh repo pada saat keputusan ini diambil.

## Konteks

Posisi Security dinilai lewat template `Security Team` berisi empat metrik, dan sampai 2026-09-21 hanya satu yang punya sumber. Salah satu yang kosong, **kepatuhan patroli tiap 3 jam** (bobot 0,3), tidak bisa menumpang mekanisme mana pun yang sudah ada: recurrence form-builder hanya mengenal `monthly` dan `weekly` (`services/form-builder/models_period.go:13-14`).

Dua pertanyaan muncul bersamaan saat merancangnya, dan keduanya mahal kalau dijawab diam-diam nanti.

**Pertama, modulnya tinggal di mana.** Ronda butuh tahu siapa yang sedang bertugas pada jam tertentu. Resolusi jadwal kerja di sini **berlapis tiga**: `RosterEntry` (manual per tanggal) menang atas `WorkScheduleAssignment`, yang menang atas dokumen dasar `work_schedule` (`shared-library/models/attendance/models.go:801` dan sesudahnya). Urutan menang seperti ini adalah persis jenis aturan yang, bila disalin ke service lain, melahirkan sumber kebenaran kedua yang menyimpang tanpa satu pun galat.

**Kedua, GPS sebenarnya membuktikan apa.** Geofence yang sudah ada memakai radius bawaan **800 meter**, minimum yang boleh disetel **50 meter** (`services/attendance/attendance_setting.go:53-55`). Komentarnya menyatakan kelonggaran itu disengaja karena lokasi kerap resolve ratusan meter dari titik sebenarnya, dan menolak orang yang benar-benar hadir lebih merugikan daripada menerima yang di seberang jalan. Titik ronda di dalam satu lokasi umumnya berjarak jauh di bawah 50 meter.

## Keputusan

1. **Modul ronda tinggal di `attendance-service`**, bukan service baru dan bukan menumpang form-builder. Resolusi shift dipanggil lewat resolver aslinya, tidak disalin. Ia juga sudah memuat `checkDistanceGPS` (`services/attendance/main.go:4162`), `resolveOfficeGeofence`, dan [[GA - Guestbook System (Complete)]], satu-satunya modul operasional Security hari ini.

2. **GPS dipakai membuktikan KEHADIRAN DI LOKASI, bukan kedatangan di satu titik.** Yang boleh diklaim sistem hanya dua hal: petugas berada di area lokasi saat mengirim, dan rondanya terkirim di dalam jendela waktunya.

3. **Area yang dicek adalah PERNYATAAN petugas, disimpan apa adanya.** Layar dilarang menampilkannya sebagai verifikasi, termasuk bentuk seperti "6/6 titik terverifikasi".

4. **Ronda yang diharapkan diturunkan saat baca**, tidak diarsipkan sebagai dokumen. Pembekuan penilaian tetap terjadi di skor KPI periode tertutup, yang memang sudah membekukannya.

5. **Interval ronda adalah setelan**, menempel di setelan per perusahaan bersama titik dan radius lokasi. Bukan konstanta di backend, dan tidak disalin ke frontend.

6. **Bukti per-titik, bila kelak dituntut, ditambahkan sebagai penanda fisik di titiknya** (QR atau NFC), **bukan dengan memperketat radius**. Itu keputusan terpisah yang belum diambil.

## Konsekuensi

**Yang diterima sadar.** Sistem ini tidak bisa membuktikan petugas benar-benar berkeliling. Ia membuktikan petugas ada di lokasi dan mengirim rondanya tepat waktu, lalu merekam pernyataannya tentang apa yang dilihat. Bagi penilaian KPI itu cukup, karena yang dinilai metriknya adalah **kepatuhan jadwal**, bukan cakupan geografis. Bagi investigasi insiden itu tidak cukup, dan siapa pun yang memakainya untuk itu harus tahu batasnya.

**Yang dicegah.** Memperketat radius sampai bisa membedakan titik akan menolak ronda yang sah setiap kali sinyal meleset, dan penolakan itu jatuh ke orang yang benar-benar bekerja. Menampilkan "titik terverifikasi" dari data yang tidak mendukungnya menghasilkan angka mulus yang keliru, kelas kegagalan yang sudah berulang di ERP ini dan tidak pernah tertangkap test.

**Ongkos yang ditanggung `attendance-service`.** Service ini sudah luas (presensi, cuti, izin, lembur, tukar shift, koreksi, guestbook). Ronda menambah dua koleksi dan satu endpoint internal. Bila kelak buku jaga, insiden, dan serah terima ikut masuk, **pemisahan jadi modul GA tersendiri layak ditinjau ulang**, dan pemicunya adalah saat ronda mulai butuh fakta yang bukan milik attendance.

**Kalau keputusan 1 dibalik nanti**, yang wajib ikut dipindahkan adalah pemanggilan resolver shift, bukan salinannya. Menyalin urutan menang berlapis tiga itu membuat ronda menilai orang atas jadwal yang berbeda dari yang dipakai presensi, dan selisihnya tidak akan terlihat sampai ada yang membandingkan dua layar berdampingan.

## Dokumen Terkait

- [[GA - Ronda Security]] — rancangan yang diikat keputusan ini
- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — kenapa alat kerja dibangun sebelum dashboard
- [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] — yang sudah menjawab metrik pos jaga
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] — batas pengumpul metrik
- [[Microservices - Attendance Service]] · [[GA - Dashboard per Posisi]] · [[REF - Kepemilikan Data]]
