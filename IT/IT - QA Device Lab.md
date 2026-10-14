## Deskripsi

*Alat QA internal untuk menguji aplikasi Android secara massal di banyak HP yang tercolok USB ke satu PC: mirroring, kontrol serentak, aksi massal, dan agen AI yang menjalankan uji dari satu perintah. Dibangun sebagai pengganti aman untuk software "group control" Panda.*

- **Nama tampilan**: **Bharata Boost** (ikon petir) sejak PR #18; nama repo, `appId`, dan folder data `Documents\QA Device Lab` sengaja tetap supaya data dan pembaruan versi lama tidak terputus. Fiturnya tetap terbatas untuk QA dan tidak disambungkan ke tiket boosting modul Engagement (lihat Sengaja tidak dibuat).
- **Status**: ⚠️ Implemented (ada catatan) — mode manual sebagai aplikasi desktop Electron merged 2026-10-14 (PR #2 tahap 1, PR #4 tahap 1b, PR #6 tahap 1c, PR #7 pemilih aplikasi, PR #8 panel Common, PR #9 stabilitas adb, PR #10 pemilih elemen); diuji dengan 1 HP (Samsung A50s, Android 11), sebagian fitur belum dicoba ke HP (lihat Catatan); belum diuji banyak HP sekaligus; mode agen AI (Tahap 2) belum dibuat.
- **Stack**: Electron 44 + Node 24 + TypeScript; server Fastify di proses utama; dashboard React + Vite + Tailwind + shadcn/ui; video dan kontrol lewat scrcpy-server 3.1 + Tango (`@yume-chan/*`, MIT); vitest; pnpm; installer electron-builder (NSIS). Alat eksternal: `adb`, `scrcpy`, `maestro`.
- **Path di repo**: repo privat `bip-itteam-internal/qa-device-lab` (sibling di workspace `erp/`); server di `server/`, proses utama Electron di `electron/`, dashboard di `web/`, spec di `docs/superpowers/specs/2026-10-13-qa-device-lab-design.md` (§14 untuk Electron). Data kerja aplikasi terpasang di `Documents\QA Device Lab`. Branch protection tidak tersedia (GitHub Free, repo privat).

## Latar Belakang

Tim memakai Panda 9.13.219 (`panda_android_setup_9.13.219.exe`, penerbit "xiaowei technoligy Ltd.") untuk mengontrol banyak HP Android dari PC. Analisis statis 2026-10-13 (installer diekstrak, APK di-decompile, string aplikasi PC dibaca; aplikasi tidak dijalankan) menyimpulkan:

- **Bukan malware yang dikenal.** VirusTotal 1/65, satu-satunya deteksi berupa tebakan machine learning berskor rendah.
- **Tetapi berisiko untuk perangkat kantor**:
  - aplikasi PC terhubung terus-menerus ke server pembuat dan punya modul akses jarak jauh (P2P);
  - aplikasi pendamping di HP bisa diperintah aplikasi lain di HP yang sama, termasuk menjalankan skrip otomasi dan membaca clipboard;
  - UI aplikasi PC diberi izin menjalankan perintah shell;
  - lisensi diikat ke sidik jari hardware;
  - installer tanpa tanda tangan digital;
  - paket membawa Magisk (root) dan pemasang driver USB.

Rekomendasi: Panda **tidak dipasang di PC kantor atau HP kerja**. Rincian teknis temuan ada di laporan privat (lihat Sumber Daya); sengaja tidak ditulis di vault karena repo vault publik.

Inti Panda ternyata alat open-source (scrcpy untuk mirroring). Karena itu penggantinya dibangun ulang dari komponen open-source, **tanpa menyalin kode Panda**.

## Ruang Lingkup

**Mode manual** (setara Panda, tanpa AI), aplikasi desktop dengan tata letak meniru Panda, **dirancang untuk pengguna yang tidak paham skrip**: langkah tampil dalam bahasa biasa, aplikasi dipilih dari namanya (bukan appId), dan fitur teknis disimpan di menu Lainnya:
- grid **video langsung** semua HP (scrcpy, didekode WebCodecs; **kualitas** dan **frame rate** bisa diatur dari panel, tersimpan per PC); klik ubin memperbesar HP ke **layar besar** dengan navigasi ▢ ○ ◁ dan kolom Fungsi; ubin yang diperbesar menampilkan "Sedang dikontrol";
- kontrol serentak lewat socket kontrol scrcpy: sentuhan dan tombol di satu HP ikut ke semua HP terpilih (Alt = HP itu saja); teks termasuk non-ASCII lewat clipboard;
- panel kanan ala "Common" Panda, grid 3 kolom: Lainnya · Tampilan · Perangkat, lalu Putar · Besar tetap · Kontrol kecil, lalu tombol yang disematkan (bawaan: Geser otomatis, Rekam aksi, Teks, Aplikasi, Skenario, Layar gelap). **Lainnya** mengatur tombol mana yang tampil di panel; Konsol, Restart ADB, dan API lokal disembunyikan di sana secara bawaan. Di bawahnya slider ukuran layar besar/kecil, kualitas, frame rate, dan chip nomor HP per grup;
- **Tampilan**: penanda ubin (nomor, nama, model, IP WiFi HP) muncul saat kursor di atas ubin atau selalu; warna nomor, gelap latar, dan jarak antar-ubin bisa diatur;
- **Perangkat**: tabel HP (nomor, nama, model, Android, baterai, IP WiFi, status), sakelar video per HP, Sambung ulang, Restart ADB (ditolak selama uji atau geser otomatis berjalan);
- **Putar** layar dan **Layar gelap** (layar fisik HP dimatikan, video tetap mengalir) untuk HP terpilih; **Besar tetap** membuat layar besar selalu terbuka;
- **Geser otomatis** untuk uji scroll/daya tahan: arah tetap, 1-5000 kali (500 sebelumnya), jeda **tetap** 1-60 detik, tombol Stop; HP ditandai sibuk selama berjalan. Bila **aplikasi yang diukur** dipilih (PR #16), tiap HP diukur saat mulai, tiap 30 detik, dan di akhir: RAM aplikasi (PSS), suhu dan level baterai, status dicas, serta persen frame patah (jank, statistik `gfxinfo` dikosongkan saat mulai); ringkasan awal→akhir dan puncak di panel, deret lengkap di `runs/geser-<id>/<serial>/ukuran.csv`; nilai tak terbaca dibiarkan kosong, bukan nol. HP yang dicas lewat USB ditandai karena angka baterainya tidak mewakili pemakaian normal; Geser bisa **diawali skenario** (PR #16) yang membawa HP ke layar yang diuji; geser hanya dimulai di HP yang skenarionya lulus, sisanya dicatat dilewati, dan Stop ikut menghentikan skenarionya;
- **Sedang berjalan** (PR #16): skenario, geser otomatis, dan uji acak yang berjalan tampil di sidebar (jenis, HP, progres, Stop berkonfirmasi) dan sebagai label di ubin HP, tetap terlihat walau dialognya ditutup (`GET /api/aktivitas`). Skenario bisa dihentikan: proses Maestro dibunuh lewat `AbortSignal` dan sisa antrean tidak dijalankan;
- **Uji acak** (Android `monkey`, PR #13, di menu Lainnya secara bawaan) untuk mencari crash dan ANR di **satu aplikasi**: urutan ketukan/geseran/ketikan acak tetapi ditentukan **kode ulang** (seed) yang dicatat dan sama di semua HP, sehingga crash bisa diulang persis; jumlah aksi 1-100.000, jeda **tetap** 100-2000 ms, tombol sistem (Home, Back, volume, telepon) dimatikan; hasil per HP lulus/crash/ANR/gagal beserta cuplikan dan `runs/<id>/<serial>/monkey.log`; dikonfirmasi dengan peringatan bahwa monkey bisa menarik panel notifikasi dan mengubah pengaturan cepat. Berjalan di luar antrean `MAKS_ADB` (seperti Maestro) karena bisa berjam-jam. Tombol Stop menjalankan `pkill` di HP, karena membunuh `adb.exe` di PC **tidak** menghentikan monkey yang sudah berjalan (terukur di A50s). Ini **bukan** *Random Delay/Offset*: acaknya untuk mencari crash di aplikasi sendiri dan justru dibuat bisa diulang, bukan untuk meniru manusia;
- semua dialog berangka tiga: header tetap, badan menggulir, footer tetap berisi jumlah HP sasaran atau peringatan bila belum ada HP terpilih;
- kirim teks sama atau berbeda per HP, pintasan teks, kirim dan tarik berkas;
- aksi massal: install APK, daftar aplikasi terpasang dengan nama aslinya (dibaca lewat `scrcpy --list-apps`, kembali ke `pm list packages` bila gagal), uninstall, buka/tutup aplikasi, hapus data aplikasi, ganti keyboard aktif, kirim berkas ke Download atau Galeri, screenshot, Home, buka halaman Settings; geser atas/bawah/kiri/kanan dari layar besar;
- konfirmasi untuk setiap aksi yang menghapus atau menghentikan (hapus data, uninstall, tutup paksa, tombol daya, hapus/keluarkan grup, hapus jadwal, jalankan konsol, hapus pintasan, timpa skenario, menutup aplikasi saat uji berjalan) dan panduan bertahap untuk pengguna baru;
- nama, grup, dan nomor urut HP yang bisa diatur (HP tanpa nomor menyusul sesudah nomor terbesar); kelola grup sebagai label: ganti nama, hapus (HP tetap ada), masukkan/keluarkan HP terpilih;
- rekam video sesi, rekam logcat + deteksi crash/ANR, clipboard dua arah (termasuk salin ke HP tanpa menempel);
- editor skenario YAML (format Maestro) dan menjalankannya paralel di banyak HP, hasil per HP di `runs/`; **Data uji** per skenario (PR #16), mis. akun uji per HP: dimuat dari berkas CSV (koma atau titik koma ala Excel Indonesia) lewat panel, dengan pratinjau HP mana menjalankan baris mana (dihitung server dengan aturan pembagian yang sama dengan run), templat dari variabel skenario, dan hapus berkonfirmasi; judul kolom = variabel `${KOLOM}`, maks. 200 baris; kolom bernama sandi/PIN/OTP/token/secret disamarkan di layar (pratinjau, baca skenario, status run), sedangkan `data/` dan `hasil.json` lokal tetap berisi nilai asli; **Rekam aksi** (padanan Action Record): layar HP langsung di samping daftar langkah berbahasa biasa ("Ketuk layar", "Geser ke atas", "Ketik ..."), batalkan langkah terakhir, simpan/buka rekaman dari berkas, lalu disimpan sebagai skenario; bisa juga dimulai dari kolom Fungsi layar besar. Ketukan disimpan sebagai **pemilih elemen** Maestro (`id` unik, lalu teks/content-desc unik, lalu teks + `index`, teks di-escape karena berupa regex) dari struktur layar `uiautomator dump` yang dibaca sesudah tiap aksi; bila layar belum terbaca, langkah jatuh ke koordinat persen dan ditandai "· koordinat", tidak ditebak;
- **jadwal uji** berkala dengan interval tetap (15 menit sampai 1 hari); jadwal terlewat dijalankan sekali, HP sibuk dilewati dan dicatat; hanya berjalan selama aplikasi terbuka;
- **konsol ADB terbatas**: hanya `adb shell` di HP terpilih (bukan perintah di PC, bukan forward/reverse/root), satu baris, maks. 30 detik, selalu dikonfirmasi, dicatat ke `runs/konsol-*.log`;
- **API lokal** untuk skrip otomasi (padanan Panda API): hanya `127.0.0.1`, wajib token acak yang berganti tiap aplikasi dibuka (`api-token.txt` di folder data); panduan dan contoh PowerShell/Python di dalam aplikasi;
- dashboard yang sama tetap bisa dibuka di browser (`pnpm start`) dengan grid screenshot sebagai cadangan.

**Mode agen** (pola sama dengan [[Microservices - Assistant Service]]):
- satu perintah bahasa alami, lalu agen mengusulkan aplikasi target dan pengecekan hasil, disetujui QA, lalu dikunci;
- loop: baca struktur layar, susun skenario, coba di satu HP, perbaiki (maks. 3 putaran), sebar ke semua HP dengan data bervariasi, lapor;
- agen **tidak boleh melemahkan pengecekan terkunci**; pengecekan yang gagal setelah navigasi benar dilaporkan sebagai kemungkinan bug aplikasi;
- AI lewat router internal yang sama dengan Copilot (`AI_BASE_URL`, `AI_API_KEY`, `AI_MODEL`).

**Sengaja tidak dibuat** (tidak dibutuhkan QA, hanya berguna untuk menyamarkan otomasi sebagai banyak manusia):
- pemalsuan identitas perangkat, rotasi IP/proxy per HP, *Random Delay* / *Random Offset* / *Delay Sync* pada kontrol serentak;
- Auto Swipe versi Panda (loop tanpa batas, interval acak 1-10 detik), warm-up akun, like/komentar otomatis: pola untuk meniru penonton manusia di aplikasi media sosial, bukan untuk QA. Uji aplikasi pihak ketiga diarahkan ke pengukuran (jank, RAM, baterai/suhu, crash), yang justru butuh pola tetap supaya bisa dibandingkan;
- impor massal akun dan password, integrasi aplikasi chat multi-akun;
- sambungan ke tiket boosting modul Engagement ERP (Bank Komen, target URL, laporan realisasi): akan menjadikan alat ini eksekutor komentar/like/ulasan otomatis di media sosial dan marketplace, bukan alat QA (diputuskan 2026-10-14);
- shell bebas di PC (konsol yang ada hanya shell HP, lihat di atas), interval jadwal acak, akses lewat internet, HP virtual/cloud, root;
- WIFI Mode (`adb tcpip`): membuka port kontrol HP ke seluruh jaringan kantor; tetap lewat USB (diputuskan 2026-10-14);
- berbagi HP dan skrip lewat cloud Panda (Get/Manage Shared, Merge Auth). Safe Mode Panda belum jelas perilakunya (TBD).

**Stabilitas banyak HP**: semua pemanggilan adb lewat satu antrean berbatas (12 serentak, `MAKS_ADB` di `server/mulai.ts`; angka awal, belum diukur dengan banyak HP). `adb -s <serial> shell ...` dikirim lewat socket ke adb server (Tango, protokol shell v2) tanpa membuat proses `adb.exe`, dan kembali ke `adb.exe` bila gagal; di A50s keluarannya identik dan 30 perintah 346 ms vs 934 ms. Tombol Segarkan hanya menjalankan `adb devices -l`; baterai, versi, dan IP diambil dari cache yang diperbarui di latar (satu shell gabungan per HP, maks. 4 HP per 2 detik, umur info 30 detik). Maestro tidak ikut antrean karena satu uji bisa berjalan puluhan menit.

**Pengaman utama**: server hanya `127.0.0.1`; semua program eksternal lewat satu pintu (daftar-izin, argumen array, tanpa shell); serial HP divalidasi; berkas hanya dari folder proyek; tidak ada aplikasi pendamping di HP. Jendela Electron tanpa akses Node (`contextIsolation`, `sandbox`); IPC hanya diterima dari dashboard lokal dan setiap masukannya divalidasi di proses utama. Di aplikasi desktop setiap `/api` wajib token; dashboard mendapatkannya lewat header yang disuntik proses utama, sehingga tautan hasil uji dibuka di jendela aplikasi sendiri (browser bawaan tidak membawa token) dan semua jendela turunan dikunci ke dashboard lokal. Mode dev (`pnpm start`) berjalan tanpa token.

Target uji: aplikasi milik perusahaan (mis. [[APP - MyBharata]]) atau aplikasi pihak ketiga atas izin pemiliknya.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| QA tester | TBD (belum ada posisi QA aplikasi di struktur organisasi) | Lokal di PC QA, tanpa login | PC Windows + rak HP Android via USB |

- **Tujuan**: menjalankan uji yang sama di banyak HP sekaligus dan mendapat hasil per HP.
- **Pain point**: Panda berisiko untuk perangkat kantor; uji manual per HP lambat.
- **Aksi utama**: kontrol serentak, jalankan skenario, beri perintah ke agen, baca hasil.

## Belum Diimplementasikan / Catatan

- **Baru diuji dengan 1 HP.** Video grid, layar besar, dan kontrol terbukti di Samsung A50s (Android 11). Banyak HP sekaligus belum diuji, jadi batas HP per PC (asumsi 20) belum diukur.
- **Sudah terbukti di A50s**: konsol (`getprop`), daftar aplikasi dengan nama (1,6 detik), daftar keyboard, Putar dan Layar gelap diterima HP, Geser otomatis 2/2, IP WiFi terbaca, token API (luar tanpa token 401, dashboard 200), dialog tiga bagian. **Belum dicoba ke HP**: alur Rekam aksi sampai disimpan lalu diputar ulang, jadwal yang benar-benar jalan, kelola grup, uninstall, slider kualitas/frame rate, dan padamnya layar fisik saat Layar gelap (Android tetap melapor layar `ON`, jadi harus dilihat langsung).
- Satu test waktu di `test/orkestrator.test.ts` sesekali gagal saat suite penuh berjalan paralel di mesin sibuk; lulus bila diulang.
- Rekaman berbasis pemilih elemen (PR #10) baru diuji pada layar kunci A50s (2 elemen, keduanya benar); belum diuji di layar aplikasi yang ramai dan belum diputar ulang dengan Maestro di HP kedua. Membaca layar makan ±3,7 detik di A50s, jadi pengguna perlu menunggu tanda centang di antara ketukan. Geseran tetap koordinat persen.
- Test waktu proses (`test/proses.test.ts`, `test/orkestrator.test.ts`) goyah saat mesin sibuk; batas waktunya perlu dilonggarkan atau dipisah dari suite utama.
- Spike yang masih tersisa:
  - Maestro paralel ke HP berbeda dengan data berbeda (bila bentrok: `PARALEL = false` di `server/orkestrator.ts`);
  - pembacaan hierarki layar lewat `maestro hierarchy` (dibutuhkan Tahap 2).
- Installer (`QA Device Lab Setup 0.1.0.exe`, sekitar 120 MB) **belum bertanda tangan digital**; Windows SmartScreen memperingatkan saat pemasangan pertama.
- Mode agen AI (Tahap 2) belum dibuat.
- Siapa pemilik dan pengguna tetap alat ini (persona QA): TBD.

## Sumber Daya

**Komponen dan alat:**
- [scrcpy](https://github.com/Genymobile/scrcpy) — mirroring dan kontrol HP, inti teknis yang juga dipakai Panda.
- [Tango / ya-webadb](https://github.com/yume-chan/ya-webadb) — pustaka TypeScript (MIT) untuk adb dan klien scrcpy; dipakai untuk video langsung dan kontrol di aplikasi Electron.
- [shadcn/ui](https://ui.shadcn.com) dan `DESIGN.md` dari [getdesign](https://getdesign.md) (template mydealz) — komponen dan panduan gaya dashboard.
- [Maestro](https://maestro.mobile.dev) — framework uji UI mobile berbasis YAML, black-box lewat accessibility tree.
- [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools) — `adb`.
- [Google USB Driver](https://developer.android.com/studio/run/win-usb) — driver USB resmi untuk Windows, pengganti pemasang driver Panda.

**Analisis Panda:**
- [Manual resmi Panda](https://doc.some3c.com/panda-manual/quickstart) — daftar fitur yang dijadikan rujukan (dan yang sengaja tidak ditiru).
- [Hasil VirusTotal installer Panda](https://www.virustotal.com/gui/file/3d857a283f97dee627082e57789832700def545be1cda3e767be9c3b4ae1d037) — SHA256 `3D857A28…4AE1D037`, 1/65.
- [innoextract](https://constexpr.org/innoextract/) — mengekstrak installer Inno Setup tanpa menjalankannya.
- [JADX](https://github.com/skylot/jadx) — decompiler APK.
- [REA: Reverse Engineer Anything](https://github.com/morluto/rea) — MCP server reverse engineering. Tidak dipakai di analisis ini (butuh Node ≥ 24.11 dan Ghidra), dicatat sebagai opsi untuk analisis berikutnya.
- Laporan Analisis Keamanan Aplikasi Panda (Claude Docs, privat): minta akses ke tim IT.

## Dokumen Terkait

- [[IT - Development Apps and Tools]] — tools internal tim
- [[IT - Security]] — kebijakan keamanan IT
- [[Microservices - Assistant Service]] — Copilot ERP, pola loop agen dan router AI yang ditiru
- [[CORE - Kapabilitas AI dan Machine Learning]] — kapabilitas AI di ERP
- [[IT - Big Pictures]] — peta domain IT
