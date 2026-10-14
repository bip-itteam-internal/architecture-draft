
# Bharata Boost — QA Device Lab

## Deskripsi

**Bharata Boost** adalah alat QA internal untuk menguji aplikasi Android secara massal pada banyak HP yang terhubung melalui USB ke satu PC. Aplikasi menyediakan mirroring, kontrol serentak, aksi massal, otomasi skenario, pengukuran performa, dan fondasi agen AI yang menjalankan pengujian berdasarkan satu perintah.

Aplikasi dikembangkan sebagai alternatif internal terhadap software group control Panda, dengan fokus pada pengujian aplikasi yang dapat diulang, terukur, dan menghasilkan bukti per perangkat.

- **Nama tampilan**: Bharata Boost (ikon petir), sejak PR #18.
- **Identitas teknis**: nama repo, `appId`, dan folder data `Documents\QA Device Lab` dipertahankan agar data dan pembaruan versi lama tidak terputus.
- **Status**: ⚠️ Implemented (ada catatan). Mode manual desktop Electron telah digabungkan melalui PR #2 tahap 1, PR #4 tahap 1b, PR #6 tahap 1c, PR #7 pemilih aplikasi, PR #8 panel Common, PR #9 stabilitas ADB, dan PR #10 pemilih elemen. Fitur tambahan dan mode agen AI memerlukan validasi atau implementasi lanjutan.
- **Platform**: Windows, dengan perangkat Android yang terhubung melalui USB.
- **Pengguna utama**: QA tester dan tim pengembangan aplikasi internal.
- **Prinsip**: pengujian terukur, hasil yang dapat direproduksi, kontrol perangkat yang eksplisit, serta pencatatan aktivitas.
- **Batas penggunaan**: aplikasi target harus merupakan aplikasi milik perusahaan atau aplikasi yang pengujiannya telah memperoleh izin pemiliknya.

## Latar Belakang

Tim menggunakan Panda 9.13.219 (`panda_android_setup_9.13.219.exe`, penerbit "xiaowei technoligy Ltd.") untuk mengontrol banyak HP Android dari PC.

Analisis statis pada 2026-10-13 dilakukan dengan mengekstrak installer, melakukan dekompilasi APK, dan membaca string aplikasi PC tanpa menjalankan aplikasi tersebut. Kesimpulannya:

- Tidak ditemukan indikasi kuat bahwa Panda merupakan malware yang telah dikenal. VirusTotal menunjukkan 1/65 deteksi, berupa deteksi machine learning berskor rendah.
- Namun, terdapat risiko untuk perangkat kantor:
  - Aplikasi PC terhubung terus-menerus ke server pembuat dan memiliki modul akses jarak jauh P2P.
  - Aplikasi pendamping HP dapat diperintah oleh aplikasi lain pada perangkat yang sama, termasuk menjalankan skrip otomasi dan membaca clipboard.
  - UI aplikasi PC memiliki izin menjalankan perintah shell.
  - Lisensi diikat ke sidik jari hardware.
  - Installer tidak memiliki tanda tangan digital.
  - Paket membawa Magisk (root) dan pemasang driver USB.

Rekomendasi awal adalah tidak memasang Panda pada PC kantor atau HP kerja.

Inti fungsi mirroring Panda menggunakan teknologi open-source seperti scrcpy. Karena itu, Bharata Boost dibangun ulang dari komponen open-source tanpa menyalin kode Panda.

Laporan teknis lengkap analisis Panda bersifat privat dan tidak disimpan di vault publik.

## Stack Teknologi

- **Desktop**: Electron 44.
- **Runtime**: Node.js 24.
- **Bahasa**: TypeScript.
- **Server lokal**: Fastify di proses utama.
- **Dashboard**: React, Vite, Tailwind CSS, shadcn/ui.
- **Mirroring dan kontrol**: scrcpy-server 3.1 dan Tango (`@yume-chan/*`, MIT).
- **ADB**: Android SDK Platform-Tools.
- **Otomasi UI**: Maestro.
- **Pengujian kode**: Vitest.
- **Package manager**: pnpm.
- **Installer**: electron-builder dengan NSIS.

### Struktur repository

- Repo privat: `bip-itteam-internal/qa-device-lab`.
- Lokasi workspace: sibling di workspace `erp/`.
- Server: `server/`.
- Proses utama Electron: `electron/`.
- Dashboard: `web/`.
- Spesifikasi desain: `docs/superpowers/specs/2026-10-13-qa-device-lab-design.md`, terutama §14 untuk Electron.
- Folder data aplikasi terpasang: `Documents\QA Device Lab`.

Branch protection belum tersedia pada repo privat GitHub Free yang digunakan.

## Ruang Lingkup / Cakupan (business view)

### 1. Mode manual

Mode manual merupakan mode utama yang telah diimplementasikan. Antarmuka dirancang untuk pengguna yang tidak harus memahami skrip atau perintah ADB.

Langkah pengujian ditampilkan dalam bahasa biasa. Aplikasi dipilih berdasarkan nama yang ditampilkan, bukan mengharuskan pengguna mengetahui `appId`. Fitur teknis disimpan di menu Lainnya.

#### Grid video langsung

- Menampilkan video langsung dari seluruh HP yang terhubung.
- Menggunakan scrcpy untuk pengambilan layar dan WebCodecs untuk dekode video.
- Kualitas video dan frame rate dapat diatur melalui panel serta disimpan sebagai preferensi PC.
- Klik ubin untuk memperbesar tampilan HP ke layar besar.
- Layar besar menyediakan navigasi ▢ ○ ◁ dan kolom Fungsi.
- Ubin HP yang sedang diperbesar menampilkan status "Sedang dikontrol".
- Video per perangkat dapat diaktifkan atau dinonaktifkan.

#### Kontrol serentak

- Sentuhan dan tombol pada satu HP dapat diteruskan ke seluruh HP yang dipilih.
- Tombol Alt membatasi aksi ke HP yang sedang dikontrol.
- Pengiriman teks mendukung karakter non-ASCII melalui clipboard.
- Pengujian dapat dibatasi ke grup atau perangkat yang dipilih secara eksplisit.

#### Panel Common

Panel kanan mengikuti pola panel Common Panda dengan grid tiga kolom:

- Lainnya · Tampilan · Perangkat.
- Putar · Besar tetap · Kontrol kecil.
- Tombol yang disematkan, dengan bawaan Geser otomatis, Rekam aksi, Teks, Aplikasi, Skenario, dan Layar gelap.

Menu Lainnya mengatur tombol yang ditampilkan. Konsol, Restart ADB, dan API lokal disembunyikan di sana secara bawaan.

Panel juga menyediakan:

- Slider ukuran layar besar dan kecil.
- Pengaturan kualitas video.
- Pengaturan frame rate.
- Chip nomor HP per grup.

#### Tampilan

- Penanda ubin berupa nomor, nama, model, dan IP WiFi HP.
- Penanda dapat ditampilkan saat kursor berada di atas ubin atau selalu.
- Warna nomor, latar gelap, dan jarak antar-ubin dapat diatur.

#### Perangkat

Tabel perangkat menampilkan:

- Nomor.
- Nama.
- Model.
- Versi Android.
- Baterai.
- IP WiFi.
- Status koneksi.

Tindakan per perangkat mencakup:

- Mengaktifkan atau menonaktifkan video.
- Sambung ulang.
- Restart ADB.

Restart ADB ditolak saat pengujian atau Geser otomatis sedang berjalan.

#### Putar, Layar gelap, dan Besar tetap

- **Putar**: memutar orientasi layar HP yang dipilih.
- **Layar gelap**: meminta layar fisik HP dimatikan sementara aliran video tetap berjalan.
- **Besar tetap**: mempertahankan layar besar agar tetap terbuka.

Perilaku Layar gelap pada perangkat fisik masih perlu divalidasi langsung karena Android tetap melaporkan status layar `ON` pada pengujian awal.

#### Geser otomatis

Geser otomatis digunakan untuk pengujian scroll, ketahanan, dan performa aplikasi.

- Arah geser ditentukan.
- Jumlah pengulangan 1–5.000 kali.
- Jeda tetap 1–60 detik.
- Tersedia tombol Stop.
- HP ditandai sibuk selama pengujian.

Jika aplikasi yang diukur dipilih, setiap HP diukur saat mulai, setiap 30 detik, dan pada akhir pengujian. Metrik meliputi:

- RAM aplikasi berdasarkan PSS.
- Suhu perangkat.
- Level baterai.
- Status pengisian daya.
- Persentase frame patah atau jank berdasarkan statistik `gfxinfo`.

Statistik jank dikosongkan saat pengukuran dimulai. Ringkasan nilai awal, akhir, dan puncak ditampilkan di panel. Deret data lengkap disimpan di:

`runs/geser-<id>/<serial>/ukuran.csv`

Nilai yang tidak dapat dibaca dibiarkan kosong, bukan diisi nol. Perangkat yang dicas melalui USB diberi penanda karena hasil baterainya tidak mewakili pemakaian normal.

Geser otomatis dapat diawali dengan skenario Maestro. Hanya HP yang skenarionya lulus yang memulai pengukuran; perangkat yang dilewati dicatat. Menekan Stop juga menghentikan skenario terkait.

#### Aktivitas berjalan

Skenario, Geser otomatis, dan Uji acak yang sedang berjalan ditampilkan di sidebar dan pada ubin HP.

Informasi mencakup:

- Jenis aktivitas.
- HP sasaran.
- Progres.
- Tombol Stop dengan konfirmasi.

Status tetap terlihat meskipun dialog ditutup, melalui `GET /api/aktivitas`.

Skenario dapat dihentikan menggunakan `AbortSignal` untuk menghentikan proses Maestro dan mencegah sisa antrean dijalankan.

#### Uji acak

Uji acak menggunakan Android `monkey` untuk mencari crash dan ANR pada satu aplikasi target.

- Urutan ketukan, geseran, dan ketikan dihasilkan secara acak tetapi ditentukan oleh seed.
- Seed dicatat agar pengujian dapat diulang.
- Seed yang sama digunakan pada seluruh HP dalam satu run jika konfigurasi pengujian sama.
- Jumlah aksi 1–100.000.
- Jeda tetap 100–2.000 ms.
- Tombol sistem seperti Home, Back, volume, dan telepon dinonaktifkan sesuai konfigurasi.
- Hasil per HP mencakup lulus, crash, ANR, atau gagal.
- Log disimpan di `runs/<id>/<serial>/monkey.log`.

Sebelum pengujian, pengguna diberi peringatan bahwa monkey dapat menarik panel notifikasi atau mengubah pengaturan cepat.

Uji acak berjalan di luar antrean `MAKS_ADB` karena satu sesi dapat berlangsung lama. Tombol Stop menjalankan `pkill` pada HP untuk menghentikan proses monkey yang telah berjalan; menghentikan `adb.exe` di PC tidak cukup.

Fitur ini merupakan pengujian robustness yang dapat direproduksi, bukan sarana untuk meniru perilaku manusia.

#### Dialog

Semua dialog menggunakan tiga bagian:

1. Header tetap.
2. Badan yang dapat digulir.
3. Footer tetap yang menampilkan jumlah HP sasaran atau peringatan jika belum ada HP dipilih.

#### Teks dan berkas

- Mengirim teks yang sama ke banyak HP.
- Mengirim teks berbeda untuk masing-masing HP.
- Menyimpan pintasan teks.
- Mengirim dan menarik berkas.
- Mengirim berkas ke folder Download atau Galeri.
- Menyalin clipboard dua arah, termasuk menyalin ke HP tanpa langsung menempelkan teks.

#### Aksi massal

Aksi yang tersedia:

- Install APK.
- Daftar aplikasi terpasang menggunakan nama aslinya.
- Uninstall aplikasi.
- Membuka dan menutup aplikasi.
- Menghapus data aplikasi.
- Mengganti keyboard aktif.
- Mengirim berkas.
- Mengambil screenshot.
- Menekan Home.
- Membuka halaman Settings.
- Menggeser ke atas, bawah, kiri, atau kanan melalui layar besar.

Daftar aplikasi diambil menggunakan `scrcpy --list-apps`, dengan fallback ke `pm list packages` jika gagal.

#### Konfirmasi dan panduan

Konfirmasi diwajibkan untuk aksi yang menghapus data, mengubah kondisi perangkat, atau menghentikan proses, termasuk:

- Hapus data.
- Uninstall.
- Tutup paksa.
- Tombol daya.
- Hapus atau keluarkan grup.
- Hapus jadwal.
- Jalankan konsol.
- Hapus pintasan.
- Timpa skenario.
- Menutup aplikasi saat pengujian berjalan.

Aplikasi menyediakan panduan bertahap untuk pengguna baru.

#### Manajemen HP dan grup

- Nama HP dapat diubah.
- Nomor urut HP dapat ditetapkan.
- HP dapat dikelompokkan berdasarkan label.
- HP tanpa nomor ditempatkan setelah nomor terbesar.
- Grup dapat diganti nama atau dihapus tanpa menghapus HP.
- Pengguna dapat memasukkan atau mengeluarkan HP terpilih dari grup.

#### Rekaman sesi dan log

- Merekam video sesi.
- Merekam logcat.
- Mendeteksi crash dan ANR.
- Menyimpan hasil per perangkat.
- Menyediakan bukti untuk reproduksi masalah.

#### Skenario Maestro

Editor skenario menggunakan YAML dengan format Maestro.

- Menjalankan skenario secara paralel pada beberapa HP.
- Menyimpan hasil per HP di `runs/`.
- Mendukung Data uji per skenario.
- Menggunakan CSV dengan pemisah koma atau titik koma ala Excel Indonesia.
- Menampilkan pratinjau pembagian data ke HP sebelum run.
- Mendukung variabel dari judul kolom, dengan sintaks `${KOLOM}`.
- Membatasi jumlah data hingga 200 baris.
- Menyamarkan kolom yang bernama sandi, PIN, OTP, token, atau secret pada pratinjau, pembacaan skenario, dan status run.

Data asli tetap tersimpan di folder `data/` dan `hasil.json` lokal. Folder tersebut harus diperlakukan sebagai data sensitif dan tidak boleh dimasukkan ke log publik atau commit repository.

#### Rekam aksi

Fitur Rekam aksi menyediakan layar HP langsung di samping daftar langkah berbahasa biasa, seperti "Ketuk layar", "Geser ke atas", dan "Ketik ...".

- Membatalkan langkah terakhir.
- Menyimpan dan membuka rekaman dari berkas.
- Mengonversi rekaman menjadi skenario.
- Dapat dimulai dari kolom Fungsi pada layar besar.

Ketukan direkam sebagai pemilih elemen Maestro dengan prioritas:

1. `id` unik.
2. Teks atau `content-desc` unik.
3. Teks beserta `index`.

Teks di-escape karena digunakan sebagai regex. Struktur layar diperoleh melalui `uiautomator dump` setelah aksi. Jika layar belum dapat dibaca, langkah menggunakan koordinat persentase dan ditandai "· koordinat", bukan menebak elemen.

#### Jadwal pengujian

- Interval tetap 15 menit hingga 1 hari.
- Jadwal terlewat dijalankan sekali, bukan mengejar seluruh jadwal yang tertinggal.
- HP yang sibuk dilewati dan dicatat.
- Jadwal hanya berjalan selama aplikasi desktop terbuka.

#### Konsol ADB terbatas

- Hanya menjalankan `adb shell` pada HP terpilih.
- Tidak mendukung perintah shell bebas di PC, forward/reverse, atau root.
- Satu baris perintah.
- Batas waktu maksimal 30 detik.
- Selalu meminta konfirmasi.
- Aktivitas dicatat di `runs/konsol-*.log`.

#### API lokal

API lokal menyediakan akses bagi skrip otomasi.

- Hanya bind ke `127.0.0.1`.
- Wajib menggunakan token acak yang berubah setiap aplikasi dibuka.
- Token disimpan di `api-token.txt` dalam folder data.
- Panduan dan contoh PowerShell/Python tersedia di dalam aplikasi.

#### Dashboard browser

Dashboard yang sama dapat dibuka dalam mode pengembangan melalui `pnpm start`. Jika video langsung tidak tersedia, grid screenshot dapat digunakan sebagai fallback.

### 2. Fitur Tambahan untuk Kebutuhan QA

Fitur berikut dimasukkan ke roadmap untuk memperluas kemampuan pengujian. Fitur ini **belum boleh dianggap sudah diimplementasikan** sampai kode, pengujian, dan dokumentasi penerimaannya selesai.

#### Profil perangkat dan identitas uji

- Membuat profil konfigurasi pengujian per perangkat.
- Mencatat model, versi Android, resolusi, kepadatan layar, dan karakteristik jaringan.
- Mendukung profil perangkat virtual atau emulator untuk pengujian kompatibilitas.
- Memungkinkan pengujian terhadap identitas perangkat sintetis di lingkungan emulator atau harness khusus yang dikendalikan QA.
- Menyimpan konfigurasi awal dan akhir agar perubahan lingkungan dapat ditelusuri.

Identitas perangkat fisik tidak diubah diam-diam. Pengujian yang memerlukan simulasi identitas harus berjalan pada lingkungan yang mendukung simulasi secara eksplisit dan tidak digunakan untuk menghindari pemeriksaan keamanan layanan produksi.

#### Profil jaringan dan proxy pengujian

- Mengelola profil jaringan untuk pengujian konektivitas.
- Mengatur endpoint proxy pengujian yang telah disetujui.
- Menguji timeout, latency, kehilangan paket, kegagalan DNS, serta pemulihan koneksi melalui lingkungan jaringan uji.
- Mengaktifkan dan menonaktifkan profil jaringan berdasarkan skenario.
- Mencatat perubahan endpoint, waktu perubahan, dan perangkat sasaran.
- Memulihkan konfigurasi awal setelah pengujian selesai.

Profil jaringan hanya berlaku untuk lingkungan yang diizinkan. Pengujian rotasi endpoint ditujukan untuk memvalidasi ketahanan aplikasi terhadap perubahan koneksi, bukan untuk menyamarkan asal trafik atau menghindari pembatasan layanan.

#### Variasi waktu aksi

Untuk menguji sensitivitas aplikasi terhadap timing dan kondisi balapan, sistem dapat menyediakan:

- Jeda tetap.
- Jeda acak dalam rentang minimum dan maksimum.
- Offset awal per perangkat.
- Offset antarperangkat.
- Jeda sebelum dan sesudah langkah tertentu.
- Seed untuk mereproduksi urutan variasi acak.
- Batas waktu total.
- Penghentian otomatis.

Seluruh nilai harus tercatat dalam konfigurasi run. Variasi timing dipakai untuk mengeksplorasi kondisi pengujian, bukan sebagai mekanisme penyamaran otomasi.

#### Geser otomatis lanjutan

- Mendukung profil pengulangan yang dapat disimpan.
- Mendukung variasi arah geser.
- Menetapkan jumlah aksi dan durasi maksimum.
- Menjalankan skenario persiapan sebelum pengukuran.
- Mengumpulkan RAM, suhu, baterai, jank, crash, dan ANR.
- Menghasilkan perbandingan antarsesi.
- Menghentikan seluruh proses yang terkait ketika Stop ditekan.
- Menyediakan pemulihan ke layar atau kondisi awal bila memungkinkan.

#### Uji beban interaksi massal

- Menjalankan aksi UI yang ditentukan QA pada banyak perangkat.
- Mendukung pola aksi seragam dan variasi data uji per perangkat.
- Membatasi jumlah perangkat dan aksi per run.
- Menyediakan pembatas laju dan batas durasi.
- Merekam keberhasilan, kegagalan, waktu respons, dan bukti per perangkat.
- Menandai perangkat yang kehilangan koneksi atau gagal menjalankan aksi.
- Mendukung penghentian global dan penghentian per perangkat.

Aksi yang memengaruhi sistem eksternal harus menggunakan lingkungan staging, akun uji, atau data sintetis yang disetujui. Interaksi yang dapat menghasilkan transaksi atau efek nyata tidak dijalankan tanpa persetujuan khusus.

#### Pengelolaan akun dan data QA

- Mengimpor data uji dari CSV.
- Membagikan baris data secara deterministik ke perangkat.
- Mendukung akun khusus QA dan data sintetis.
- Menyamarkan informasi rahasia di antarmuka.
- Menyediakan validasi sebelum run.
- Menghapus data uji sementara setelah selesai berdasarkan kebijakan retensi.
- Mencegah data akun atau token masuk ke log yang tidak terlindungi.

Fitur ini tidak dimaksudkan untuk mengumpulkan atau mengimpor akun pihak ketiga secara massal.

#### Pengujian integrasi dan regresi

- Menjalankan skenario yang sama pada beberapa versi aplikasi.
- Membandingkan hasil antarversi Android dan model perangkat.
- Mengumpulkan screenshot ketika pemeriksaan gagal.
- Menyimpan logcat dan metrik performa.
- Menghasilkan laporan regresi per perangkat dan per versi.
- Menyediakan format laporan yang dapat dikonsumsi pipeline CI/CD.

#### Integrasi pipeline QA

- Menjalankan pengujian dari pipeline internal.
- Membuat run ID untuk setiap eksekusi.
- Mengambil hasil dan artefak melalui API lokal yang terautentikasi.
- Mengatur batas waktu dan pembatalan.
- Menyimpan riwayat hasil.
- Menghasilkan laporan lulus/gagal dan ringkasan anomali.

Integrasi harus tetap menggunakan izin eksplisit, pembatasan target, dan audit log. API tidak dibuka langsung ke internet.

#### Kriteria penerimaan fitur tambahan

1. Semua fitur baru dapat diaktifkan dan dinonaktifkan secara eksplisit.
2. Setiap run memiliki ID, daftar perangkat, aplikasi target, parameter, waktu, dan hasil.
3. Pengujian yang menggunakan randomness mencatat seed dan parameter yang dibutuhkan untuk reproduksi.
4. Penghentian run menghentikan proses yang dimiliki run tersebut dan mencatat status akhirnya.
5. Perubahan konfigurasi jaringan dapat dipulihkan atau dilaporkan jika pemulihan gagal.
6. Data rahasia disamarkan pada tampilan dan tidak masuk ke log yang tidak terlindungi.
7. Pengujian massal dibatasi pada perangkat, aplikasi, dan lingkungan yang disetujui.
8. Tidak ada fitur yang sengaja dibuat untuk memalsukan aktivitas manusia, memanipulasi engagement, atau menghindari mekanisme anti-penyalahgunaan layanan.

### 3. Mode agen AI — Tahap 2

Mode agen AI belum diimplementasikan.

Pola desain mengikuti Microservices - Assistant Service.

#### Alur agen

1. QA memberikan satu perintah menggunakan bahasa alami.
2. Agen mengusulkan aplikasi target dan pemeriksaan yang akan dilakukan.
3. QA meninjau dan menyetujui rencana.
4. Pemeriksaan yang disetujui dikunci.
5. Agen membaca struktur layar dan menyusun skenario.
6. Agen mencoba skenario pada satu HP.
7. Agen memperbaiki skenario jika gagal, maksimal tiga putaran.
8. Agen menjalankan skenario pada perangkat lain dengan data uji yang sesuai.
9. Agen mengumpulkan hasil dan melaporkan temuan.

#### Batas agen

- Agen tidak boleh melemahkan pemeriksaan yang telah dikunci.
- Kegagalan pemeriksaan setelah navigasi berjalan benar dilaporkan sebagai kemungkinan bug aplikasi.
- Perubahan pada data, jaringan, atau kondisi perangkat harus sesuai izin dan rencana pengujian.
- Agen tidak boleh menjalankan aksi eksternal yang tidak termasuk dalam rencana yang disetujui.
- Operasi destruktif memerlukan konfirmasi tambahan.
- Hasil agen harus menyertakan bukti dan langkah reproduksi.

#### Integrasi AI

Router AI menggunakan konfigurasi internal yang sama dengan Copilot:

- `AI_BASE_URL`
- `AI_API_KEY`
- `AI_MODEL`

Kunci API tidak boleh ditulis ke log atau dimasukkan ke artefak hasil pengujian.

## Stabilitas Banyak HP

Seluruh pemanggilan ADB melalui satu antrean berbatas dengan 12 pekerjaan serentak. Konfigurasi awal berada di `MAKS_ADB` pada `server/mulai.ts`; kapasitas tersebut belum diukur melalui uji multi-HP.

Pemanggilan `adb -s <serial> shell ...` dikirim melalui socket ke ADB server menggunakan Tango dan protokol shell v2, tanpa selalu membuat proses `adb.exe`. Jika metode tersebut gagal, aplikasi kembali menggunakan `adb.exe`.

Pada A50s, keluaran kedua metode identik. Pengukuran awal menunjukkan 30 perintah membutuhkan 346 ms melalui socket dibandingkan 934 ms melalui `adb.exe`.

Tombol Segarkan hanya menjalankan `adb devices -l`. Informasi baterai, versi Android, dan IP diambil dari cache latar belakang:

- Satu shell gabungan per HP.
- Maksimal empat HP per dua detik.
- Umur informasi cache 30 detik.

Maestro tidak menggunakan antrean ADB yang sama karena satu skenario dapat berlangsung puluhan menit. Uji paralel Maestro ke HP berbeda masih memerlukan validasi. Jika terjadi konflik, `PARALEL = false` dapat digunakan di `server/orkestrator.ts` sampai masalah terselesaikan.

### Rencana pengujian kapasitas

- Uji 1, 2, 5, 10, dan 20 HP.
- Ukur penggunaan CPU, RAM PC, throughput ADB, frame rate video, latensi kontrol, dan kestabilan koneksi.
- Uji satu perangkat terputus saat perangkat lain sedang berjalan.
- Uji penghentian global ketika sebagian perangkat gagal.
- Uji pengulangan skenario dengan data berbeda.
- Uji pemulihan setelah ADB server direstart.
- Tentukan kapasitas perangkat yang didukung berdasarkan hasil pengukuran, bukan asumsi.

## Pengaman Utama

- Server hanya bind ke `127.0.0.1`.
- Program eksternal dijalankan melalui satu pintu dengan daftar izin dan argumen array, tanpa shell bebas.
- Serial HP divalidasi.
- Akses berkas dibatasi pada folder proyek yang diizinkan.
- Tidak ada aplikasi pendamping yang perlu dipasang pada HP.
- Jendela Electron menggunakan `contextIsolation` dan `sandbox`.
- IPC hanya menerima pesan dari dashboard lokal dan memvalidasi masukan di proses utama.
- Dalam aplikasi desktop, setiap permintaan `/api` membutuhkan token.
- Token dashboard disuntikkan oleh proses utama.
- Tautan hasil uji dibuka pada jendela aplikasi sendiri karena browser biasa tidak membawa token.
- Jendela turunan dibatasi ke dashboard lokal.
- Mode pengembangan melalui `pnpm start` berjalan tanpa token dan hanya boleh digunakan dalam lingkungan pengembangan yang sesuai.

### Autentikasi akun ERP

- Aplikasi hanya bisa dipakai setelah masuk dengan akun ERP. Hak masuknya lewat izin `booster.use` (modul `booster`, paket bawaan "Bharata Boost: Pengguna"), dipasang di ERP → IT → Hak Akses. Pemegang paket Semua Izin otomatis ikut mendapatkannya ([[ADR - 0172 Token Login Keluar dari Cookie dan Paket Semua Izin Dimekarkan saat Token Terbit]]).
- ⚠️ **Menyimpang dari [[ADR - 0003 SSO-only Gateway]]** (keputusan user 2026-10-14). Aplikasi memanggil `POST /auth/login` milik gateway langsung, seperti MyBharata, bukan lewat SSO ticket/redeem. Alasannya: ini aplikasi desktop internal untuk pengguna non-teknis, dan login langsung lebih sederhana daripada berpindah ke peramban. Akunnya tetap akun ERP yang sama, bukan akun terpisah. Password tidak disimpan; yang disimpan hanya JWT, terenkripsi per akun Windows. `device_id` sengaja tidak dikirim supaya tidak bentrok dengan device binding MyBharata.
- Gerbangnya di server lokal: seluruh `/api` (termasuk skrip yang memakai `api-token.txt`) hanya melayani selama ada pengguna berizin yang masuk. Token dari disk dikonfirmasi ulang lewat `/auth/refresh` setiap aplikasi dibuka, sehingga izin yang dicabut langsung berlaku.
- Setiap uji, geser otomatis, uji acak, dan jadwal mencatat siapa pemulainya. Uji dari jadwal tercatat atas nama pembuat jadwal.

### Pengamanan tambahan untuk fitur QA

- Batasi jumlah perangkat, durasi run, dan jumlah aksi.
- Sediakan tombol Stop yang terlihat dan dapat diakses saat pengujian berjalan.
- Gunakan akun dan data sintetis untuk skenario berisiko.
- Catat perubahan konfigurasi perangkat dan jaringan.
- Pisahkan hasil pengujian dari data rahasia.
- Jangan menulis token atau sandi ke log.
- Validasi seluruh parameter yang diterima API.
- Batasi operasi destruktif dengan konfirmasi.
- Sediakan mekanisme pemulihan setelah pengujian.
- Jangan mengekspos endpoint kontrol melalui jaringan kantor atau internet.
- Lakukan pengujian keamanan sebelum fitur tambahan digunakan pada perangkat kerja.

## Persona / Pengguna

| Persona   | Peran & Divisi                                           | Akses/RBAC                                                  | Perangkat                             |
| --------- | -------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------- |
| QA tester | TBD; belum ada posisi QA aplikasi di struktur organisasi | Lokal di PC QA, tanpa login aplikasi                        | PC Windows dan rak HP Android via USB |
| Developer | Tim pengembangan aplikasi                                | Penggunaan sesuai akses PC dan lingkungan uji               | PC pengembangan dan HP uji            |
| QA lead   | TBD                                                      | Meninjau rencana, hasil, dan persetujuan pengujian berisiko | PC QA                                 |

### Tujuan

- Menjalankan pengujian yang sama pada banyak HP sekaligus.
- Mendapatkan hasil terpisah untuk setiap perangkat.
- Mengidentifikasi regresi, crash, ANR, dan masalah performa.
- Mengurangi pekerjaan manual berulang.
- Menghasilkan hasil pengujian yang dapat direproduksi.

### Pain point

- Risiko keamanan Panda pada perangkat kantor.
- Pengujian manual per HP memakan waktu.
- Hasil antarperangkat sulit dibandingkan.
- Reproduksi bug membutuhkan langkah dan konfigurasi yang konsisten.
- Belum tersedia alur agen AI untuk menyusun dan menjalankan skenario.

### Aksi utama

- Kontrol serentak.
- Menjalankan skenario.
- Mengelola data uji.
- Mengukur performa.
- Menghentikan run.
- Membaca laporan dan bukti kegagalan.
- Menyetujui rencana agen AI.

## Belum Diimplementasikan / Catatan

### Pengujian perangkat

- Baru diuji dengan satu HP: Samsung A50s, Android 11.
- Video grid, layar besar, dan kontrol telah terbukti pada perangkat tersebut.
- Belum dilakukan validasi multi-HP.
- Batas HP per PC, dengan asumsi awal 20 perangkat, belum diukur.

### Fitur yang telah diuji di A50s

- Konsol (`getprop`).
- Daftar aplikasi dengan nama asli, sekitar 1,6 detik.
- Daftar keyboard.
- Putar dan Layar gelap diterima perangkat.
- Geser otomatis 2/2.
- IP WiFi terbaca.
- Token API: permintaan eksternal tanpa token menghasilkan 401 dan dashboard menghasilkan 200.
- Dialog tiga bagian.

### Fitur yang belum dicoba pada perangkat

- Rekam aksi sampai disimpan lalu diputar ulang.
- Jadwal yang benar-benar berjalan.
- Manajemen grup.
- Uninstall.
- Slider kualitas dan frame rate.
- Perilaku fisik layar saat Layar gelap aktif.

### Rekam aksi dan pemilih elemen

PR #10 baru diuji pada layar kunci A50s dengan dua elemen yang teridentifikasi benar.

Belum diuji pada layar aplikasi yang ramai dan belum diputar ulang dengan Maestro di HP kedua.

Pembacaan layar membutuhkan sekitar 3,7 detik pada A50s. Pengguna harus menunggu indikator selesai sebelum melakukan ketukan berikutnya. Geseran masih direkam menggunakan koordinat persentase.

### Test suite

- Satu pengujian waktu di `test/orkestrator.test.ts` sesekali gagal ketika suite penuh berjalan paralel pada mesin sibuk, tetapi lulus ketika diulang.
- Test waktu proses pada `test/proses.test.ts` dan `test/orkestrator.test.ts` masih sensitif terhadap beban mesin.
- Batas waktu perlu ditinjau atau pengujian waktu dipisahkan dari suite utama.

### Spike yang tersisa

- Validasi Maestro paralel pada HP berbeda dengan data berbeda.
- Pembacaan hierarki layar menggunakan `maestro hierarchy` untuk Tahap 2.
- Uji ketahanan koneksi dan pemulihan saat beberapa HP terputus.
- Validasi penggunaan memori dan CPU ketika banyak stream video berjalan.
- Validasi pemulihan konfigurasi jaringan setelah run.

### Installer

Installer `QA Device Lab Setup 0.1.0.exe` berukuran sekitar 120 MB dan belum memiliki tanda tangan digital. Windows SmartScreen memberi peringatan saat pemasangan pertama.

### Agen AI

Mode agen AI Tahap 2 belum dibuat.

### Kepemilikan

Pemilik produk, penanggung jawab QA, dan pengguna tetap alat masih TBD.

## Rencana Pengembangan

### Prioritas 1 — Validasi dan stabilisasi

- Jalankan uji multi-HP bertahap.
- Perbaiki test suite yang sensitif terhadap beban mesin.
- Uji rekaman aksi sampai replay pada HP kedua.
- Uji jadwal, manajemen grup, dan kontrol video.
- Validasi installer dan pembaruan aplikasi.
- Tentukan batas kapasitas perangkat berdasarkan data.

### Prioritas 2 — Pengujian QA lanjutan

- Profil konfigurasi perangkat.
- Variasi timing yang dapat direproduksi.
- Pengujian jaringan pada lingkungan staging.
- Uji beban interaksi dengan pembatas laju.
- Pengelolaan data sintetis.
- Perbandingan hasil antarversi aplikasi.

### Prioritas 3 — Pelaporan

- Ringkasan run lintas perangkat.
- Perbandingan metrik performa.
- Pengumpulan bukti crash dan ANR.
- Ekspor laporan QA.
- Retensi dan pembersihan artefak.

### Prioritas 4 — Agen AI

- Integrasi router AI.
- Pembacaan hierarki layar.
- Penyusunan skenario dari bahasa alami.
- Persetujuan dan penguncian pemeriksaan.
- Maksimal tiga putaran perbaikan.
- Eksekusi lintas perangkat dan pelaporan hasil.

Urutan prioritas dapat berubah setelah hasil validasi multi-HP diketahui.

## Kriteria Kesiapan Rilis

Sebelum dipakai secara luas oleh tim QA, hal berikut harus dipenuhi:

- [ ] Uji pada lebih dari satu model dan versi Android.
- [ ] Uji multi-HP dengan kapasitas bertahap.
- [ ] Validasi kontrol serentak dan isolasi aksi menggunakan Alt.
- [ ] Validasi Stop dan pemulihan ketika perangkat terputus.
- [ ] Validasi Rekam aksi dan replay.
- [ ] Validasi jadwal.
- [ ] Validasi installer dan proses pembaruan.
- [ ] Audit pengamanan API, IPC, dan eksekusi program eksternal.
- [ ] Validasi penanganan data sensitif.
- [ ] Penetapan pemilik produk dan penanggung jawab QA.
- [ ] Dokumentasi prosedur pemulihan.
- [ ] Penetapan daftar aplikasi dan lingkungan pengujian yang diizinkan.

## Sumber Daya

### Komponen dan alat

- [scrcpy](https://github.com/Genymobile/scrcpy) — mirroring dan kontrol HP.
- [Tango / ya-webadb](https://github.com/yume-chan/ya-webadb) — pustaka TypeScript untuk ADB dan klien scrcpy.
- [shadcn/ui](https://ui.shadcn.com) — komponen antarmuka.
- [getdesign](https://getdesign.md) — referensi gaya dashboard dan `DESIGN.md`.
- [Maestro](https://maestro.mobile.dev) — framework pengujian UI mobile berbasis YAML.
- [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools) — ADB.
- [Google USB Driver](https://developer.android.com/studio/run/win-usb) — driver USB resmi untuk Windows.

### Analisis Panda

- [Manual resmi Panda](https://doc.some3c.com/panda-manual/quickstart) — referensi fitur.
- [Hasil VirusTotal installer Panda](https://www.virustotal.com/gui/file/3d857a283f97dee627082e57789832700def545be1cda3e767be9c3b4ae1d037) — SHA256 `3D857A28…4AE1D037`, hasil 1/65.
- [innoextract](https://constexpr.org/innoextract/) — mengekstrak installer Inno Setup tanpa menjalankannya.
- [JADX](https://github.com/skylot/jadx) — decompiler APK.
- [REA: Reverse Engineer Anything](https://github.com/morluto/rea) — opsi analisis berikutnya; tidak digunakan dalam analisis awal karena persyaratan Node dan Ghidra.

Laporan Analisis Keamanan Aplikasi Panda tersedia melalui Claude Docs privat; akses perlu diminta kepada tim IT.

## Dokumen Terkait

- [[IT - Development Apps and Tools]] — tools internal tim.
- [[IT - Security]] — kebijakan keamanan IT.
- [[Microservices - Assistant Service]] — pola loop agen dan router AI.
- [[CORE - Kapabilitas AI dan Machine Learning]] — kapabilitas AI di ERP.
- [[IT - Big Pictures]] — peta domain IT.
