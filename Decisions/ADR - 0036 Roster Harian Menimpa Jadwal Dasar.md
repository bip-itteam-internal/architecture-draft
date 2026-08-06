**Status**: ✅ Diputuskan 2026-08-05, **live di produksi 2026-08-06** dan sudah dipakai — Host Live Kyura sudah dinyalakan `roster_enabled`-nya. bip-erp PR #1012 (`79e95038`) + #1014, erp-frontend PR #805 (`5e1e61ae`) + #808 + #809. Backend prod di `92b2b914`, frontend prod di `6da8443c` (deploy manual; merge ke main hanya menurunkan ke DEV). Tombol Panduan in-app menyusul di erp-frontend #811.

## Context

Resolusi jadwal di [[Microservices - Attendance Service]] mengenal dua bentuk saja: `static` (satu dokumen `company_work_schedule`, jam per hari dalam seminggu) dan `pattern` (grup memutar daftar shift tiap X hari lewat `company_group_rotation`). Keduanya mengasumsikan hal yang sama, bahwa jadwal seseorang **punya pola**.

Posisi **Host Live** di departemen Kyura tidak punya pola itu. Jam siarnya mengikuti campaign, bukan rotasi. Selama ini konsekuensinya ditanggung dengan cara yang makin mahal:

- Delapan konstanta grup `HOSTLIVE-0226-*` ditulis sebagai konstanta Go di `shared-library/models/attendance/models.go`, dan jamnya di-seed di `services/attendance/setup.go`. Setiap kali HR mengubah polanya, itu berarti ubah kode lalu deploy.
- Penyimpangan sekali pakai ditambal hardcode. Aturan Ramadhan 2026 ditulis dengan tanggal literal di `services/attendance/func.go`, memetakan shift ke varian `-RAMADHAN-` selama sebulan.
- Komentar di kodenya sendiri sudah mencatat ini sebagai utang: *"This is so bad, we will refuse to support this kind of bullshit"*.

Berapa pun banyaknya template shift yang dibuat, kenyataannya tetap tidak muat, karena yang salah bukan jumlah templatenya melainkan asumsi bahwa polanya ada.

## Decision

**Jadwal boleh ditentukan per orang per tanggal, dan penentuan itu menimpa jadwal dasar hanya untuk tanggal yang benar-benar diisi.**

Aturan turunannya:

1. **Roster menumpuk di atas jadwal dasar, bukan menggantikannya.** `schedule_type` tetap `static` atau `pattern`, dan `schedule_id`/`group_id` tetap wajib terisi. Sengaja **bukan** nilai ketiga untuk `schedule_type`: nilai ketiga akan menghapus tempat jatuh, padahal justru tanggal yang tidak diisi harus tetap punya jawaban.

2. **Tanggal yang tidak diisi berperilaku persis seperti sebelum fitur ini ada.** Ini janji yang menentukan bentuk seluruh implementasinya, dan yang diuji paling keras. Lupa mengisi berarti perilaku lama, bukan presensi yang rusak.

3. **Urutan menang hidup di satu tempat.** Dari paling kuat: event perusahaan, roster, libur nasional/cuti bersama, jadwal dasar. Satu-satunya penulisnya `resolveEmployeeScheduleWithRoster`; cron dan jalur pemulihan menggerbang pada **vonis** resolver, bukan menyalin urutannya. Dua salinan urutan menang adalah kelas bug yang fitur ini justru ingin dihindari.

4. **Roster mengalahkan hari libur, tapi tidak mengalahkan event perusahaan.** Mengisi sel di tanggal merah adalah keputusan sadar bahwa live tetap jalan; event perusahaan berarti semua divisi ikut acara sehingga presensi memang tidak relevan bagi siapa pun.

5. **Roster menentukan jadwal dan jam, bukan status kehadiran.** Cuti dan perjalanan dinas yang disetujui tetap menang, dan entri yang sudah membawa keputusan dari jalur itu tidak boleh ditimpa maupun dihapus lewat roster.

6. **Saklar `roster_enabled` per karyawan, bukan per departemen atau per posisi.** Saklar itu menentukan siapa yang muncul di halaman roster, siapa yang Tukar Shift-nya ditutup, dan menjadi pengaman ketika seseorang berpindah posisi. Nilai bawaannya `false`, sehingga hari rilis tidak mengubah apa pun bagi siapa pun.

7. **Sentinel `ROSTER` sengaja tidak punya dokumen `company_work_schedule`.** Jam roster berbeda tiap orang tiap hari, jadi tidak ada satu dokumen yang bisa mewakilinya. Konsekuensinya jamnya **dibawa bersama** hasil resolusi, dan entri presensi menjadi sumber kebenaran jam bagi jalur tap.

8. **Tanggal lampau read-only.** Membetulkan masa lalu sudah punya jalurnya sendiri, yaitu [[HRIS - Attendance Correction]], lengkap dengan persetujuan dan jejak audit. Roster tidak menjadi jalur kedua yang mengubah data historis.

9. **Tukar Shift ditutup untuk karyawan ber-roster,** di sisi pemohon maupun sisi rekan. Jadwal yang sudah bebas diatur leader membuat tukar shift mubazir, dan dua jalur yang mengubah tanggal yang sama menghasilkan urutan menang yang tidak bisa dijelaskan ke pemakainya.

## Consequences

**Konsekuensi yang diterima:**

- **`roster_enabled` hidup di database employee dan mengalir SATU ARAH.** Koleksi `work_schedule` disinkronkan ke attendance-service lewat `SyncCollection`, yang melakukan `DeleteMany({})` lalu `InsertMany` seluruh koleksi tiap 30 menit. Menyetel saklar di database attendance akan terhapus pada tik berikutnya, tanpa galat apa pun. Ini menjebak, dan sudah menjebak sekali saat penulisan runbook penyalaannya.
- **Dokumen `work_schedule` di database employee tidak menyimpan `department` maupun `position`.** Keduanya di-*enrich* saat dibaca oleh `/sync/work-schedules`. Menyaring dengan keduanya untuk menyalakan saklar mencocokkan nol dokumen; turunkan `employee_id` dari `work_data` lebih dulu.
- **Field baru tidak otomatis sampai ke frontend.** Respons detail karyawan dibangun dari allowlist proyeksi di `services/employee/aggregate_projection.go`; field yang tidak disebut di sana hilang tanpa jejak dan responsnya tetap tampak wajar. `roster_enabled` sempat gagal total karena ini.
- **Grup `HOSTLIVE-0226-*` dan tambalan Ramadhan tetap hidup** sebagai jadwal dasar tempat jatuh. Fitur ini tidak menghapus utang lama, ia membuat utang itu berhenti bertambah.
- **Cron berjalan tiap 30 menit, sedangkan roster mengizinkan menit bebas.** Cabang roster karena itu memakai pemicu **jendela**, bukan kesetaraan menit; tanpa itu sel 09:15 tidak akan pernah menghasilkan entri dan orangnya tidak bisa tap masuk tanpa galat muncul di mana pun.
- **Batas 500 sel per permintaan** adalah penjaga yang disengaja. Klien memecah kirimannya sendiri, dan tiap batch adalah transaksi tersendiri di server.
- **Slice Go yang tak pernah terisi di-serialisasi sebagai `null`, bukan `[]`.** `GET /roster` sempat membalas `{"employees": null}` untuk departemen yang belum punya karyawan ber-roster — yaitu SETIAP departemen sebelum saklarnya dinyalakan pertama kali — dan halamannya jatuh ke error boundary begitu dibuka (diperbaiki PR #1014 di sisi server, #808 di sisi klien). Sekelas dengan jebakan allowlist proyeksi di [[Microservices - Employee Service]]: keduanya membuat respons tampak wajar sementara datanya tidak ada.
- **Tipe frontend yang ditulis dari asumsi menutupi ketiganya.** Tiga bug dalam fitur ini lolos suite hijau dengan pola identik: `date` dikira tanggal telanjang padahal RFC3339, `RosterResponse` menyatakan array non-nullable padahal Go mengirim `null`, dan `ScheduleFormData` mewajibkan `schedule_id` serta tak mengenal `group_id` padahal karyawan `pattern` justru kebalikannya. Fixture test dibuat mengikuti tipe, bukan mengikuti respons sungguhan, sehingga yang diuji adalah dunia yang diasumsikan. Ketiga tipe kini dibuat jujur agar kelalaian serupa jadi galat kompilasi.

**Yang tidak diantisipasi dan baru terlihat saat dipakai:**

- **Menyalakan saklar sempat menuntut jadwal dipilih ulang.** Form edit jadwal membaca `schedule_id` saja, sedangkan karyawan `pattern` menyimpannya di `group_id`, sehingga kotaknya kosong dan validasi menolak. Digabung dengan saklar yang dulu hanya tersimpan setelah form jadwal lolos validasi, HR yang cuma ingin menyalakan roster dipaksa memilih ulang jadwal — dan salah pilih berarti mengubah jadwal kerja orang itu, dengan delapan varian grup Host Live yang bernama mirip. Diperbaiki di erp-frontend #809: jadwal dibaca `schedule_id ?? group_id`, dan jadwal hanya ditulis bila pemakai benar-benar menyentuhnya.
- **Alur halaman tidak terbaca sendiri.** Pemakai harus memilih sel DULU sebelum tombol pengisian aktif, dan tombol itu bernama "Terapkan" walau fungsinya membuka editor. Ditambah bayangan jadwal dasar yang mencetak nama grup panjang di setiap kotak, grid terlihat seperti sudah terisi. Ditutup sementara lewat panduan in-app (#811); perbaikan tampilannya sendiri belum dikerjakan.

**Yang belum dikerjakan (menyusul):**

- **Bayangan jadwal dasar di sel kosong belum per tanggal.** Grid menampilkan satu nilai yang sama untuk seluruh bulan, bukan shift yang benar-benar berlaku pada tanggal itu. Untuk host berjadwal `pattern`, bayangan itu justru menyesatkan.
- **Seret-rentang dan shift-klik belum ada.** Seleksi baris dan kolom sudah menutup kasus terbanyak.
- **Notifikasi ke host saat rosternya berubah belum ada.** Sengaja di luar lingkup sejak awal.
- **Aplikasi [[APP - MyBharata]] tidak menyembunyikan tombol Tukar Shift** untuk host ber-roster; penolakannya murni di backend dengan pesan yang jelas.
- **Shift yang mulai 00:00/01:00 masih berselisih** antara jalur roster dan jalur penyemaian warisan, karena jendela pra-alokasinya jatuh pukul 22:00/23:00 sehingga aturan warisan menyala di jalur penyemaian itu sendiri.

**Yang belum diputuskan (TBD):**

- Apakah pengisian roster perlu jejak persetujuan, mengingat sekarang satu supervisor cukup untuk mengubah jadwal seluruh timnya.
- Apakah perlakuan payroll untuk hari libur yang di-roster jadi hari kerja sudah benar; ini perlu dikonfirmasi ke pemilik payroll sebelum periode gaji pertama.
- Apakah departemen selain Kyura akan memakai roster, dan apakah ambang 500 sel masih cukup bila dipakai lebih luas.

## Terkait

- [[Microservices - Attendance Service]] (koleksi, resolver, cron, rute) · [[API - Attendance Service]] (daftar endpoint)
- [[Microservices - Employee Service]] (saklar `roster_enabled`, proyeksi, sinkronisasi) · [[API - Employee Service]]
- [[HRIS - Attendance System]] (konsep presensi) · [[HRIS - Attendance Correction]] (jalur perbaikan masa lalu)
- [[HRIS - Tukar Jadwal Kerja]] (ditutup untuk karyawan roster) · [[ADR - 0006 Swap Jadwal Same-Department]]
- [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] (isolasi tenant) · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] (gerbang hak akses)
- [[APP - Web ERP]] (halaman HRIS → Personalia → Roster) · [[IT - Background Jobs & Schedulers]] (cron penyemaian)
